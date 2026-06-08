"""
_lab_spy_subtemas_chat49_v2.py — LAB read-only (chat 49, addendum). Stage 1+2 CORREGIDO.
NO toca prod. NO escribe seeds. Solo _lab_out/. $0 (Flash centavos).

ADJUDICACIÓN aplicada (4 decisiones del addendum):
  D1. Clasificador BINARIO: ATOMICO vs CONTENEDOR. GENERICO eliminado. Answer-key binario
      (#6,7,8,18,19,23,28 → CONTENEDOR).
  D2. El filtro "genérico" se muda al EXTRACTOR como criterio de CONCRECIÓN (ontología
      objetiva, NO nicho): extrae PARTICULARES CONCRETOS, saltea UNIVERSALES ABSTRACTOS.
      El extractor etiqueta cada item CONCRETO/ABSTRACTO → keep solo concretos.
  D3. Test del VIDEO-STANDALONE en el clasificador: "¿cada nombre se sostiene SOLO como
      video propio, o son facetas de UN mismo misterio que solo importan juntas?".
      Reportar el split de #3, #11, #25.
  D4. Verificación ASR = REVIEW-FLAG, nunca kill-gate. (Se reporta, no se dropea.)

Correr:  python -X utf8 _lab_spy_subtemas_chat49_v2.py
Output:  _lab_out/spy_subtemas_stage1_v2.json  +  _lab_out/spy_subtemas_stage2_v2.json
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

LAB_OUT = Path("_lab_out")
CORPUS = LAB_OUT / "transcripts_chat42.json"
OUT_S1 = LAB_OUT / "spy_subtemas_stage1_v2.json"
OUT_S2 = LAB_OUT / "spy_subtemas_stage2_v2.json"

TRANSCRIPT_CAP = 500_000
SLEEP = 0.3

# ── Answer-key BINARIO (D1) ──
KEY_ATOMICO = {3, 11, 12, 13, 22, 25}
KEY_DROP = {2, 5, 26}
def key_of(n: int) -> str:
    if n in KEY_DROP: return "DROP"
    if n in KEY_ATOMICO: return "ATOMICO"
    return "CONTENEDOR"

TRAP_CASES = {10, 14, 17, 21}
ATOMIC_SPLIT_REPORT = {3, 11, 25}     # mostrar cómo los partiría el extractor (D3)
NEG_CONTROLS = {6, 23}                  # ~0 concretos esperado (D2)
KEEP_ROSTER = {15, 17, 20}             # roster limpio no debe romperse
MIXED = {9}                             # concreto+abstracto (Castle Bravo vs lithium problem)


def clean_transcript(raw: str) -> str:
    if not raw:
        return ""
    t = re.sub(r"\[(Music|Applause|Laughter|Audio|música)\]", " ", raw, flags=re.IGNORECASE)
    t = re.sub(r">>+", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t[:TRANSCRIPT_CAP]


# ══════════════════════════════════════════════════════════════════════════════
#  STAGE 1 — clasificador BINARIO + test video-standalone (D1 + D3)
# ══════════════════════════════════════════════════════════════════════════════
S1_SYSTEM = (
    "Sos un clasificador de ESTRUCTURA de un video documental, leyendo su transcript completo. "
    "Tu única tarea es decidir si el video trata UN solo asunto o MUCHOS asuntos independientes. "
    "NO juzgás si es popular, ni si sería buen video, ni si es producible para ningún canal: "
    "eso se decide en otro lado y no es tu problema. Solo estructura.\n\n"
    "Dos tipos:\n\n"
    "- ATOMICO: todo el video converge en UN solo asunto/misterio/sujeto. Aunque mencione "
    "muchos nombres, datos o personas, son FACETAS del mismo asunto, que solo cobran sentido "
    "JUNTAS dentro de esa única historia.\n\n"
    "- CONTENEDOR: el video recorre MÚLTIPLES asuntos, uno tras otro, donde cada asunto "
    "se sostendría SOLO como su propio video independiente. Es un recorrido/compilación, "
    "aunque el título no diga un número, aunque no haya señales de enumeración, y aunque los "
    "asuntos se narren sin nombrarlos en mayúscula (un faro del que desaparecieron tres "
    "fareros en una fecha = un caso concreto que se sostiene solo, igual).\n\n"
    "TEST DECISIVO (aplicalo siempre): para cada cosa que el video trata, preguntate "
    "'¿ESTO se sostiene SOLO como un video propio, o solo importa como una pieza/evidencia "
    "del MISMO misterio que el resto?'. "
    "Si las cosas se sostienen cada una sola y por separado → CONTENEDOR. "
    "Si solo importan juntas como facetas de un único asunto → ATOMICO.\n"
    "Ejemplo abstracto de ATOMICO: un video sobre una sola conspiración donde cada 'caso' "
    "alegado es evidencia de ESA conspiración y no tendría sentido como video aislado.\n"
    "Ejemplo abstracto de CONTENEDOR: un video que cuenta un naufragio, luego otro naufragio "
    "sin relación, luego otro — cada uno sería un video por su cuenta."
)
S1_SCHEMA = types.Schema(
    type=types.Type.OBJECT, required=["tipo", "razon"],
    properties={
        "tipo": types.Schema(type=types.Type.STRING, enum=["ATOMICO", "CONTENEDOR"]),
        "razon": types.Schema(type=types.Type.STRING),
    },
)


def classify_one(title: str, transcript: str) -> dict:
    prompt = (f"TÍTULO: {title}\n\nTRANSCRIPT (limpio):\n{transcript}\n\n"
              "Clasificá ATOMICO vs CONTENEDOR aplicando el TEST DECISIVO.")
    def _do():
        resp = _client.models.generate_content(
            model=_cfg.gemini_model, contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=S1_SYSTEM, response_mime_type="application/json",
                response_schema=S1_SCHEMA, temperature=0.0))
        return json.loads(resp.text)
    try:
        d = _with_retry(_do)
        return {"tipo": d.get("tipo", "ERROR"), "razon": (d.get("razon") or "").strip()}
    except Exception as e:
        return {"tipo": "ERROR", "razon": str(e)[:120]}


# ══════════════════════════════════════════════════════════════════════════════
#  STAGE 2 — extractor con criterio de CONCRECIÓN (D2)
# ══════════════════════════════════════════════════════════════════════════════
S2_SYSTEM = (
    "Sos un extractor de SUBTEMAS de un video documental, leyendo su transcript. Listás las "
    "entidades que el video recorre, clasificando cada una por su ONTOLOGÍA (criterio objetivo, "
    "NO depende de ningún canal ni de si es 'producible'):\n\n"
    "- CONCRETO = un PARTICULAR con referente real y definido: un evento puntual, un lugar "
    "nombrado, una persona, un objeto/barco/naufragio específico (p.ej. un naufragio con su "
    "nombre, un faro concreto, una prueba nuclear nombrada, una persona). Se puede señalar 'ESE'.\n"
    "- ABSTRACTO = un UNIVERSAL: un fenómeno, concepto científico, teoría, categoría o tipo "
    "general (p.ej. un problema teórico de física, una anomalía-tipo, 'criaturas marinas' como "
    "categoría, una clase de objeto). No es una instancia única señalable.\n\n"
    "Reglas:\n"
    "- Extraé TODAS las entidades que el video trata como sujeto, etiquetando cada una "
    "CONCRETO o ABSTRACTO. NO filtres vos: etiquetá y devolvé ambas (el filtrado se hace después).\n"
    "- Para los CONCRETO, dá el nombre canónico real que mejor identifique la entidad si lo "
    "reconocés. NO inventes nombres: si una cosa no tiene referente real identificable, no la "
    "incluyas.\n"
    "- es_compilacion_item = true si aparece como uno más del recorrido del video.\n"
    "Sin duplicados."
)
S2_SCHEMA = types.Schema(
    type=types.Type.OBJECT, required=["items"],
    properties={"items": types.Schema(
        type=types.Type.ARRAY, items=types.Schema(
            type=types.Type.OBJECT,
            required=["nombre_en", "clase", "es_compilacion_item"],
            properties={
                "nombre_en": types.Schema(type=types.Type.STRING),
                "clase": types.Schema(type=types.Type.STRING, enum=["CONCRETO", "ABSTRACTO"]),
                "es_compilacion_item": types.Schema(type=types.Type.BOOLEAN),
            }))})


def extract_one(title: str, transcript: str) -> list[dict]:
    prompt = (f"TÍTULO: {title}\n\nTRANSCRIPT (limpio):\n{transcript}\n\n"
              "Extraé las entidades etiquetando cada una CONCRETO o ABSTRACTO.")
    def _do():
        resp = _client.models.generate_content(
            model=_cfg.gemini_model, contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=S2_SYSTEM, response_mime_type="application/json",
                response_schema=S2_SCHEMA, temperature=0.0))
        return json.loads(resp.text)
    try:
        d = _with_retry(_do)
        out, seen = [], set()
        for s in (d.get("items") or []):
            name = (s.get("nombre_en") or "").strip()
            if name and name.lower() not in seen:
                seen.add(name.lower())
                out.append({"nombre_en": name,
                            "clase": s.get("clase", "ABSTRACTO"),
                            "es_compilacion_item": bool(s.get("es_compilacion_item", True))})
        return out
    except Exception as e:
        return [{"nombre_en": f"__ERROR__ {str(e)[:80]}", "clase": "ABSTRACTO",
                 "es_compilacion_item": False}]


# ── Verificación ASR = review-flag (D4) ──
VERIFY_SYSTEM = (
    "Verificás nombres propios extraídos de transcripts con errores de ASR. Para cada nombre, "
    "si corresponde a una ENTIDAD REAL conocida devolvé su grafía CANÓNICA (corrigiendo el "
    "ASR); si no corresponde a nada real, canonical=null e is_real=false. Esto es solo un FLAG "
    "de revisión, no decide nada."
)
VERIFY_SCHEMA = types.Schema(
    type=types.Type.OBJECT, required=["items"],
    properties={"items": types.Schema(type=types.Type.ARRAY, items=types.Schema(
        type=types.Type.OBJECT, required=["id", "canonical", "is_real"],
        properties={
            "id": types.Schema(type=types.Type.INTEGER),
            "canonical": types.Schema(type=types.Type.STRING, nullable=True),
            "is_real": types.Schema(type=types.Type.BOOLEAN),
        }))})


def verify_names(names: list[str]) -> dict[str, dict]:
    result: dict[str, dict] = {}
    uniq = list(dict.fromkeys(names))
    for start in range(0, len(uniq), 40):
        chunk = uniq[start:start + 40]
        prompt = "Verificá (corregí ASR o null):\n" + "\n".join(f"{i}. {n}" for i, n in enumerate(chunk))
        def _do():
            resp = _client.models.generate_content(
                model=_cfg.gemini_model, contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=VERIFY_SYSTEM, response_mime_type="application/json",
                    response_schema=VERIFY_SCHEMA, temperature=0.0))
            return json.loads(resp.text)
        try:
            d = _with_retry(_do)
            for it in (d.get("items") or []):
                try:
                    idx = int(it["id"])
                    if 0 <= idx < len(chunk):
                        result[chunk[idx]] = {"canonical": it.get("canonical"),
                                              "is_real": bool(it.get("is_real"))}
                except (KeyError, ValueError, TypeError):
                    continue
        except Exception:
            pass
        time.sleep(SLEEP)
    return result


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════════════════
def main():
    LAB_OUT.mkdir(parents=True, exist_ok=True)
    videos = json.loads(CORPUS.read_text(encoding="utf-8"))
    by_n = {i: v for i, v in enumerate(videos, 1)}
    print("LAB SPY SUBTEMAS v2 — chat 49 addendum. binario + concreción. read-only, no seeds.")

    # ── STAGE 1 (binario + standalone test) ──
    print("\n" + "=" * 78)
    print("STAGE 1 — clasificador BINARIO (ATOMICO/CONTENEDOR) + test standalone")
    print("=" * 78)
    s1 = []
    for i, v in enumerate(videos, 1):
        k = key_of(i)
        clean = clean_transcript(v.get("transcript") or "")
        if not clean or len(clean) < 50:
            s1.append({"n": i, "key": k, "tipo": "DROP_NO_TRANSCRIPT", "razon": "", "title": v.get("title", "")})
            print(f"  #{i:>2} [key={k:<10}] DROP_NO_TRANSCRIPT")
            continue
        r = classify_one(v.get("title", ""), clean)
        s1.append({"n": i, "key": k, "tipo": r["tipo"], "razon": r["razon"], "title": v.get("title", "")})
        mark = "" if k == "DROP" else ("✓" if r["tipo"] == k else "✗")
        trap = " <TRAMPA>" if i in TRAP_CASES else ""
        print(f"  #{i:>2} [key={k:<10}] -> {r['tipo']:<11} {mark}{trap} :: {r['razon'][:66]}")
        time.sleep(SLEEP)

    classes = ["ATOMICO", "CONTENEDOR"]
    conf = {a: {b: 0 for b in classes + ["OTHER"]} for a in classes}
    scored = [r for r in s1 if r["key"] in classes]
    correct = 0
    for r in scored:
        p = r["tipo"] if r["tipo"] in classes else "OTHER"
        conf[r["key"]][p] += 1
        correct += (r["tipo"] == r["key"])
    print("\n  -- MATRIZ BINARIA (filas=key, cols=pred) --")
    print(f"  {'key/pred':<12}" + "".join(f"{c:>12}" for c in classes + ["OTHER"]))
    for a in classes:
        print(f"  {a:<12}" + "".join(f"{conf[a][b]:>12}" for b in classes + ["OTHER"]))
    print(f"  ACCURACY (sobre {len(scored)} keyed): {correct}/{len(scored)}")
    traps = [r for r in s1 if r["n"] in TRAP_CASES]
    print("  -- casos-trampa --")
    for t in traps:
        print(f"    #{t['n']} key={t['key']} pred={t['tipo']} {'✓' if t['tipo']==t['key'] else '✗'}")
    atom_detail = [{"n": r["n"], "key": r["key"], "pred": r["tipo"],
                    "hit": r["tipo"] == r["key"], "razon": r["razon"]}
                   for r in s1 if r["key"] == "ATOMICO"]
    print("  -- ATÓMICOS (key) --")
    for a in atom_detail:
        print(f"    #{a['n']} pred={a['pred']} {'✓' if a['hit'] else '✗'} :: {a['razon'][:60]}")

    OUT_S1.write_text(json.dumps({"matriz": conf, "accuracy": f"{correct}/{len(scored)}",
                                  "traps": traps, "atomicos": atom_detail, "rows": s1},
                                 indent=2, ensure_ascii=False), encoding="utf-8")

    # ── STAGE 2 (concreción) ──
    print("\n" + "=" * 78)
    print("STAGE 2 — extractor CONCRECIÓN (CONCRETO keep / ABSTRACTO descarta)")
    print("=" * 78)
    pred_cont = {r["n"] for r in s1 if r["tipo"] == "CONTENEDOR"}
    targets = sorted(pred_cont | NEG_CONTROLS | KEEP_ROSTER | MIXED | ATOMIC_SPLIT_REPORT)
    s2 = []
    all_concrete_names = []
    for n in targets:
        v = by_n[n]
        clean = clean_transcript(v.get("transcript") or "")
        items = extract_one(v.get("title", ""), clean) if clean else []
        concretos = [x for x in items if x["clase"] == "CONCRETO"]
        abstractos = [x for x in items if x["clase"] == "ABSTRACTO"]
        for x in concretos:
            if not x["nombre_en"].startswith("__ERROR__"):
                all_concrete_names.append(x["nombre_en"])
        s2.append({"n": n, "key": key_of(n), "pred_tipo": next((r["tipo"] for r in s1 if r["n"]==n), "?"),
                   "title": v.get("title", ""), "n_concreto": len(concretos),
                   "n_abstracto": len(abstractos), "concretos": concretos, "abstractos": abstractos})
        tag = ""
        if n in NEG_CONTROLS: tag = " (NEG→~0 concretos)"
        elif n in KEEP_ROSTER: tag = " (roster)"
        elif n in MIXED: tag = " (mixto)"
        elif n in ATOMIC_SPLIT_REPORT: tag = " (split atómico)"
        print(f"  #{n:>2} concretos={len(concretos):>3} abstractos={len(abstractos):>3}{tag}")
        time.sleep(SLEEP)

    # verificación ASR (flag) sobre concretos
    print(f"\n  Verificando {len(set(all_concrete_names))} nombres concretos (review-flag)...")
    verif = verify_names(all_concrete_names)
    for row in s2:
        for x in row["concretos"]:
            vd = verif.get(x["nombre_en"])
            if vd:
                x["canonical"] = vd["canonical"]; x["is_real"] = vd["is_real"]
                x["asr_corrected"] = bool(vd["canonical"]) and vd["canonical"].strip().lower() != x["nombre_en"].strip().lower()
            else:
                x["canonical"] = None; x["is_real"] = None; x["asr_corrected"] = False

    OUT_S2.write_text(json.dumps({"rows": s2}, indent=2, ensure_ascii=False), encoding="utf-8")

    # ── REPORTE pedido por el addendum ──
    print("\n  -- D3: SPLIT de los 3 atómicos (qué entidades percibe el extractor) --")
    for n in sorted(ATOMIC_SPLIT_REPORT):
        row = next(r for r in s2 if r["n"] == n)
        s1r = next(r for r in s1 if r["n"] == n)
        print(f"\n  #{n} [stage1={s1r['tipo']} (key=ATOMICO)] concretos={row['n_concreto']}:")
        for x in row["concretos"][:16]:
            print(f"      • {x['nombre_en']}")

    print("\n  -- D2: concretos vs abstractos en controles/mixto --")
    for n in sorted(NEG_CONTROLS | MIXED):
        row = next(r for r in s2 if r["n"] == n)
        print(f"  #{n} {row['title'][:46]:<46} CONCRETO={row['n_concreto']:>3} ABSTRACTO={row['n_abstracto']:>3}")
        if row["abstractos"][:6]:
            print(f"       abstractos(muestra): " + " · ".join(x["nombre_en"][:28] for x in row["abstractos"][:6]))
        if row["concretos"][:6]:
            print(f"       concretos(muestra):  " + " · ".join(x["nombre_en"][:28] for x in row["concretos"][:6]))

    print("\n  -- roster limpio (#15/#17/#20) NO debe romperse --")
    for n in sorted(KEEP_ROSTER):
        row = next(r for r in s2 if r["n"] == n)
        print(f"\n  #{n} concretos={row['n_concreto']}:")
        for x in row["concretos"][:14]:
            can = f"  →{x['canonical']}" if x.get("asr_corrected") else ("  (no-real?)" if x.get("is_real") is False else "")
            print(f"      • {x['nombre_en']}{can}")

    tot_c = sum(r["n_concreto"] for r in s2)
    tot_a = sum(r["n_abstracto"] for r in s2)
    nf = sum(1 for r in s2 for x in r["concretos"] if x.get("is_real") is False)
    print(f"\n  TOTALES stage2: {tot_c} concretos · {tot_a} abstractos descartados · "
          f"{nf} concretos flageados no-real (review, NO drop)")
    print(f"\nGuardado:\n  {OUT_S1}\n  {OUT_S2}")


if __name__ == "__main__":
    main()
