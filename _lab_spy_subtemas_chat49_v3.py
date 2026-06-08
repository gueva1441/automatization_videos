"""
_lab_spy_subtemas_chat49_v3.py — LAB CIERRE (chat 49 addendum 3). read-only, NO toca prod.
Solo _lab_out/. $0 (Flash) + scrape mínimo (4 search EN, sin outlier).

Cierra el lab afilado con 3 correcciones adjudicadas:
  D9  — extractor = SUJETO-DE-SEGMENTO (no "entidad concreta"): los N casos a los que el video
        le dedica un TRAMO propio, NO toda entidad nombrada. #15 debería bajar 168→~15-20.
  D11 — answer-key stage 1: #3 → CONTENEDOR (era key-error, no fallo del modelo). Re-score.
  D12 — medidor EN-LAXO gana chequeo de RELEVANCIA título↔entidad (substring de anclas):
        si el top result no trata de la entidad, NO cuenta (mata la contaminación Azores→Antarctic).

Contrato cerrado (no re-abrir): stage1 BINARIO + standalone · extractor=sujeto-de-segmento sin
eje de producibilidad (D10) · medidor vara LAXO, sin outlier, ES-primero, +relevancia EN ·
procedencia parent/origen (D8) · ASR=review-flag (D4).

Correr:  python -X utf8 _lab_spy_subtemas_chat49_v3.py
Output:  _lab_out/spy_subtemas_v3_cierre.json
"""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from gemini_helpers import _client, _cfg, types, _with_retry
from script_engine.youtube_scanner import search_viral_english, extract_anchors

LAB_OUT = Path("_lab_out")
CORPUS = LAB_OUT / "transcripts_chat42.json"
STAGE1_V2 = LAB_OUT / "spy_subtemas_stage1_v2.json"
OUT = LAB_OUT / "spy_subtemas_v3_cierre.json"

TRANSCRIPT_CAP = 500_000
LAXO_FLOOR_VIEWS = 50_000
EN_SEARCH_LIMIT = 15

# números v2 (concreción) para el antes/después
V2_CONCRETO = {15: 168, 17: 166, 20: 108, 6: 91, 23: 30}
EXTRACT_TARGETS = [15, 17, 20, 6, 23]
EN_RELEVANCE_SAMPLE = [
    ("Azores Plateau Monolith", "OSCURO/contaminado"),
    ("Mary Celeste", "BUENO"),
    ("USS Cyclops", "BUENO"),
    ("Wilhelm Gustloff", "BUENO"),
]


def clean_transcript(raw: str) -> str:
    if not raw:
        return ""
    t = re.sub(r"\[(Music|Applause|Laughter|Audio|música)\]", " ", raw, flags=re.IGNORECASE)
    t = re.sub(r">>+", " ", t)
    return re.sub(r"\s+", " ", t).strip()[:TRANSCRIPT_CAP]


# ── D9: extractor SUJETO-DE-SEGMENTO ──
SEG_SYSTEM = (
    "Sos un extractor de SUJETOS-DE-SEGMENTO de un video documental, leyendo su transcript. "
    "Estos videos RECORREN una serie de casos/temas, dedicándole a cada uno un TRAMO propio de "
    "narración. Tu tarea: devolver SOLO esos sujetos — los N casos que el video trata como tema "
    "PROPIO de un segmento del recorrido.\n\n"
    "La señal NO es si una entidad es 'concreta'. Es su ROL en la estructura del video. "
    "Para cada cosa nombrada preguntate: '¿el video le dedica su PROPIO segmento (es uno de los "
    "casos del recorrido), o solo se MENCIONA dentro del segmento de otro caso?'.\n"
    "- SÍ es sujeto-de-segmento → inclúyelo.\n"
    "- Solo se menciona dentro del tramo de otro (un lugar, una persona, una fecha, un barco, "
    "un dato de contexto que aparece adentro de la historia de OTRO caso) → NO lo incluyas.\n\n"
    "Ejemplo abstracto: si el video dedica un tramo a la desaparición de cierto barco, y dentro "
    "de ese tramo menciona el mar donde ocurrió y el puerto de origen, el SUJETO es el barco; "
    "el mar y el puerto son menciones incidentales, NO sujetos.\n"
    "NO juzgues si el tema es producible, popular ni de ningún nicho — solo su rol estructural. "
    "Dá el nombre canónico real de cada sujeto. Sin duplicados."
)
SEG_SCHEMA = types.Schema(
    type=types.Type.OBJECT, required=["subtemas"],
    properties={"subtemas": types.Schema(
        type=types.Type.ARRAY, items=types.Schema(
            type=types.Type.OBJECT, required=["nombre_en"],
            properties={"nombre_en": types.Schema(type=types.Type.STRING)}))})


def extract_segments(title: str, transcript: str) -> list[str]:
    prompt = (f"TÍTULO: {title}\n\nTRANSCRIPT (limpio):\n{transcript}\n\n"
              "Devolvé SOLO los sujetos-de-segmento (los N casos del recorrido). Excluí las "
              "menciones incidentales que viven dentro del segmento de otro caso.")
    def _do():
        resp = _client.models.generate_content(
            model=_cfg.gemini_model, contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SEG_SYSTEM, response_mime_type="application/json",
                response_schema=SEG_SCHEMA, temperature=0.0))
        return json.loads(resp.text)
    try:
        d = _with_retry(_do)
        out, seen = [], set()
        for s in (d.get("subtemas") or []):
            nm = (s.get("nombre_en") or "").strip()
            if nm and nm.lower() not in seen:
                seen.add(nm.lower()); out.append(nm)
        return out
    except Exception as e:
        return [f"__ERROR__ {str(e)[:80]}"]


# ── D12: relevancia título↔entidad (substring de anclas, $0) ──
def is_relevant(entity: str, title: str) -> bool:
    if not title:
        return False
    tl = title.lower()
    anchors = [a.lower() for a in extract_anchors(entity) if len(a) >= 4]
    if anchors:
        return any(a in tl for a in anchors)
    # sin anclas largas → fallback: alguna palabra del nombre (>=4) en el título
    words = [w for w in re.findall(r"\w+", entity.lower()) if len(w) >= 4]
    return any(w in tl for w in words)


def en_laxo_relevante(name: str) -> dict:
    try:
        cands = search_viral_english(name, limit=EN_SEARCH_LIMIT)
    except Exception as e:
        return {"error": str(e)[:100]}
    cands_sorted = sorted(cands, key=lambda c: int(c.get("views") or 0), reverse=True)
    top_raw = cands_sorted[0] if cands_sorted else None
    relevantes = [c for c in cands_sorted if is_relevant(name, c.get("title", ""))]
    top_rel = relevantes[0] if relevantes else None
    return {
        "top_raw_title": (top_raw or {}).get("title"),
        "top_raw_views": int((top_raw or {}).get("views") or 0) if top_raw else 0,
        "top_rel_title": (top_rel or {}).get("title"),
        "top_rel_views": int((top_rel or {}).get("views") or 0) if top_rel else 0,
        "n_cands": len(cands), "n_relevantes": len(relevantes),
        "pasa_laxo_RAW": (int((top_raw or {}).get("views") or 0) if top_raw else 0) >= LAXO_FLOOR_VIEWS,
        "pasa_laxo_RELEVANTE": (int((top_rel or {}).get("views") or 0) if top_rel else 0) >= LAXO_FLOOR_VIEWS,
    }


def main():
    LAB_OUT.mkdir(parents=True, exist_ok=True)
    videos = json.loads(CORPUS.read_text(encoding="utf-8"))
    by_n = {i: v for i, v in enumerate(videos, 1)}
    print("LAB CIERRE v3 — sujeto-de-segmento (D9) + relevancia EN (D12) + key #3 (D11)")

    # ── D9: extractor sujeto-de-segmento ──
    print("\n" + "=" * 78)
    print("D9 — EXTRACTOR SUJETO-DE-SEGMENTO (antes=concreción v2 / después=v3)")
    print("=" * 78)
    seg_rows = []
    for n in EXTRACT_TARGETS:
        v = by_n[n]
        subs = extract_segments(v.get("title", ""), clean_transcript(v.get("transcript") or ""))
        pvid, ptitle = v.get("video_id"), v.get("title")
        seg_rows.append({"n": n, "parent_video_id": pvid, "parent_title": ptitle,
                         "n_v2_concreto": V2_CONCRETO.get(n), "n_v3_segmento": len(subs),
                         "subtemas": [{"nombre_en": s, "parent_video_id": pvid,
                                       "parent_title": ptitle,
                                       "origen": f"#{n} \"{(ptitle or '')[:50]}\""} for s in subs]})
        print(f"  #{n:>2} {V2_CONCRETO.get(n,'?'):>4} → {len(subs):>3}   {(ptitle or '')[:52]}")
        time.sleep(0.3)

    print("\n  -- roster #15/#17/#20 (sujetos-de-segmento, deben ser casos, no menciones) --")
    for n in (15, 17, 20):
        row = next(r for r in seg_rows if r["n"] == n)
        print(f"\n  #{n} ({row['n_v3_segmento']} sujetos):")
        for s in row["subtemas"][:22]:
            print(f"      • {s['nombre_en']}")
    for n in (6, 23):
        row = next(r for r in seg_rows if r["n"] == n)
        print(f"\n  #{n} ({row['n_v3_segmento']} sujetos · NO se espera 0, filtro nicho NO es del extractor):")
        for s in row["subtemas"][:14]:
            print(f"      • {s['nombre_en']}")

    # ── D12: relevancia EN ──
    print("\n" + "=" * 78)
    print("D12 — RELEVANCIA EN (RAW vs RELEVANTE). Azores debe dejar de contar.")
    print("=" * 78)
    rel_rows = []
    for name, clase in EN_RELEVANCE_SAMPLE:
        r = en_laxo_relevante(name)
        rel_rows.append({"name": name, "clase": clase, **r})
        if "error" in r:
            print(f"  {name:<26} ERROR {r['error']}")
            continue
        print(f"  {name:<26} [{clase}]")
        print(f"     RAW       top={r['top_raw_views']:>10,}  '{(r['top_raw_title'] or '')[:44]}'  LAXO={'PASA' if r['pasa_laxo_RAW'] else 'no'}")
        print(f"     RELEVANTE top={r['top_rel_views']:>10,}  '{(r['top_rel_title'] or '')[:44]}'  LAXO={'PASA' if r['pasa_laxo_RELEVANTE'] else 'no'}  ({r['n_relevantes']}/{r['n_cands']} relevantes)")
        time.sleep(0.4)

    # ── D11: re-score stage 1 con key #3→CONTENEDOR ──
    print("\n" + "=" * 78)
    print("D11 — RE-SCORE stage 1 con answer-key corregido (#3 → CONTENEDOR)")
    print("=" * 78)
    s1 = json.loads(STAGE1_V2.read_text(encoding="utf-8"))
    rows = s1["rows"]
    KEY_ATOMICO = {11, 12, 13, 22, 25}   # #3 sacado de ATOMICO → ahora CONTENEDOR
    KEY_DROP = {2, 5, 26}
    def newkey(n):
        if n in KEY_DROP: return "DROP"
        return "ATOMICO" if n in KEY_ATOMICO else "CONTENEDOR"
    classes = ["ATOMICO", "CONTENEDOR"]
    conf = {a: {b: 0 for b in classes + ["OTHER"]} for a in classes}
    correct = scored = 0
    misses = []
    for r in rows:
        n = r["n"]; k = newkey(n)
        if k not in classes:  # DROP
            continue
        pred = r["tipo"] if r["tipo"] in classes else "OTHER"
        conf[k][pred] += 1; scored += 1
        if r["tipo"] == k: correct += 1
        else: misses.append((n, k, r["tipo"]))
    print(f"  key/pred      " + "".join(f"{c:>12}" for c in classes + ["OTHER"]))
    for a in classes:
        print(f"  {a:<12}" + "".join(f"{conf[a][b]:>12}" for b in classes + ["OTHER"]))
    print(f"  ACCURACY (key corregido): {correct}/{scored}   (v2 era 23/25)")
    print(f"  misses restantes: " + (", ".join(f"#{n}(key={k},pred={p})" for n,k,p in misses) or "ninguno"))

    OUT.write_text(json.dumps({
        "d9_segment_extractor": seg_rows,
        "d12_en_relevance": rel_rows,
        "d11_stage1_rescore": {"accuracy": f"{correct}/{scored}", "matriz": conf,
                               "misses": [{"n": n, "key": k, "pred": p} for n, k, p in misses]},
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nGuardado: {OUT}")


if __name__ == "__main__":
    main()
