"""
_lab_spy_subtemas_chat49.py — LAB read-only (chat 49). Puerta 1: extracción de subtemas.
NO toca prod. NO escribe seeds. Solo _lab_out/. Stage 1+2 (clasificar + extraer + verificar).

────────────────────────────────────────────────────────────────────────────
PROBLEMA: spy caza un viral EN que muchas veces es una COMPILACIÓN ("18 Terrifying
Ocean Mysteries"). Hoy se traduce el TÍTULO a algo genérico y se groundea eso →
medís la compilación, producís un tema genérico. El fix: leer el TRANSCRIPT, un LLM
clasifica atómico/contenedor/genérico, y de los contenedores extrae los subtemas reales.

HALLAZGOS FIRMES (reglas de diseño, NO re-testear):
  H1: el clasificador DEBE ser un LLM leyendo (no regex/NER de cues de enumeración).
  H2: el extractor necesita VERIFICAR nombres (ASR garabatea: "Wilhelm Gusoff"=Gustloff,
      "Aang Medan"=Ourang Medan, "High Brazil"=Hy-Brasil).
  Discriminador núcleo: ATÓMICO = todos los hechos convergen en UN sujeto;
      CONTENEDOR = recorre MUCHOS sujetos inconexos (cada uno podría ser su video).

CORPUS: _lab_out/transcripts_chat42.json (lista de 28; 1-indexed = answer-key).
Limpiar [Music]/[Applause] y marcadores de speaker ">>" antes de pasar al LLM.

LLAMADA: cliente Gemini directo con response_schema (§3 R4) — NO se modifica
call_flash_json. Few-shot CONCEPTUAL (AP3), sin texto copiable. Flakiness=estructura (§3.4).

Correr:  python -X utf8 _lab_spy_subtemas_chat49.py
Output:  _lab_out/spy_subtemas_stage1.json  +  _lab_out/spy_subtemas_stage2.json
"""
from __future__ import annotations

import json
import re
import sys
import time
from collections import defaultdict
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from gemini_helpers import _client, _cfg, types, _with_retry

LAB_OUT = Path("_lab_out")
CORPUS = LAB_OUT / "transcripts_chat42.json"
OUT_S1 = LAB_OUT / "spy_subtemas_stage1.json"
OUT_S2 = LAB_OUT / "spy_subtemas_stage2.json"

TRANSCRIPT_CAP = 500_000   # ningún transcript del corpus lo supera (max ~277k)
SLEEP = 0.3

# ── Answer-key (1-indexed) ──
ANSWER_KEY = {}
for n in (1, 4, 9, 10, 14, 15, 16, 17, 20, 21, 24, 27):
    ANSWER_KEY[n] = "CONTENEDOR"
for n in (3, 11, 12, 13, 25, 22):
    ANSWER_KEY[n] = "ATOMICO"
for n in (6, 7, 8, 18, 19, 23, 28):
    ANSWER_KEY[n] = "GENERICO"
for n in (2, 5, 26):
    ANSWER_KEY[n] = "DROP"

# casos-trampa que el clasificador DEBE acertar con transcript
TRAP_CASES = {10, 14, 17, 21}
# controles negativos para stage 2 (deben devolver 0 subtemas)
NEG_CONTROLS = {6, 23}
# objetivos conocidos para auditar stage 2
S2_KNOWN = {14, 15, 17, 20}


# ══════════════════════════════════════════════════════════════════════════════
#  Limpieza de transcript
# ══════════════════════════════════════════════════════════════════════════════
def clean_transcript(raw: str) -> str:
    if not raw:
        return ""
    t = raw
    t = re.sub(r"\[(Music|Applause|Laughter|Áudio|Audio|música|Music\?)\]", " ", t, flags=re.IGNORECASE)
    t = re.sub(r">>+", " ", t)            # marcadores de speaker
    t = re.sub(r"\s+", " ", t).strip()
    return t[:TRANSCRIPT_CAP]


# ══════════════════════════════════════════════════════════════════════════════
#  STAGE 1 — clasificador ATOMICO/CONTENEDOR/GENERICO
# ══════════════════════════════════════════════════════════════════════════════
S1_SYSTEM = (
    "Sos un clasificador de TIPO de video documental, leyendo su transcript completo. "
    "Tu única tarea es decidir la ESTRUCTURA del contenido, no si es popular ni si sería buen "
    "video; la demanda se mide en otro lado y no es tu problema.\n\n"
    "Clasificá en uno de tres tipos según cómo se distribuyen los SUJETOS del video:\n\n"
    "- ATOMICO: todos los hechos, nombres y datos del video CONVERGEN en UN solo sujeto "
    "(un evento, un lugar, una persona, una misión). Aunque mencione muchos nombres, todos "
    "pertenecen a esa misma historia única. Ejemplo abstracto: un video entero sobre una sola "
    "misión espacial fallida y la gente involucrada en ESA misión.\n\n"
    "- CONTENEDOR: el video RECORRE MÚLTIPLES sujetos INCONEXOS, uno tras otro, donde cada "
    "sujeto podría ser su propio video independiente (un caso, después otro caso sin relación, "
    "después otro). Es una compilación o recorrido, aunque el título no diga un número y aunque "
    "no haya señales de enumeración explícitas, y aunque los sujetos se narren sin nombrarlos "
    "en mayúscula (un faro, tres hombres, una fecha = un caso concreto igual). Lo que define "
    "CONTENEDOR es la DISPERSIÓN en varios sujetos producibles por separado.\n\n"
    "- GENERICO: el video trata un CONCEPTO, fenómeno o categoría general, sin sujetos concretos "
    "y producibles. No hay eventos/lugares/casos específicos nombrables: es divulgación abstracta "
    "(un concepto científico, un tipo de criatura en general, una categoría sin instancias "
    "puntuales). Si al terminar no podés nombrar NINGÚN caso/lugar/evento concreto, es GENERICO.\n\n"
    "Discriminador clave ATOMICO vs CONTENEDOR: NO es cuántos nombres hay, es si los nombres se "
    "agrupan en UN sujeto (ATOMICO) o se dispersan en MUCHOS sujetos sin relación (CONTENEDOR).\n"
    "Discriminador clave CONTENEDOR vs GENERICO: el CONTENEDOR tiene casos concretos (aunque "
    "narrados sin nombre propio); el GENERICO no tiene ningún caso concreto, solo el concepto."
)

S1_SCHEMA = types.Schema(
    type=types.Type.OBJECT,
    required=["tipo", "razon"],
    properties={
        "tipo": types.Schema(type=types.Type.STRING,
                             enum=["ATOMICO", "CONTENEDOR", "GENERICO"]),
        "razon": types.Schema(type=types.Type.STRING),
    },
)


def classify_one(title: str, transcript: str) -> dict:
    prompt = (f"TÍTULO: {title}\n\nTRANSCRIPT (limpio):\n{transcript}\n\n"
              "Clasificá el TIPO según su estructura de sujetos.")

    def _do():
        resp = _client.models.generate_content(
            model=_cfg.gemini_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=S1_SYSTEM,
                response_mime_type="application/json",
                response_schema=S1_SCHEMA,
                temperature=0.0,
            ),
        )
        return json.loads(resp.text)

    try:
        d = _with_retry(_do)
        return {"tipo": d.get("tipo", "ERROR"), "razon": (d.get("razon") or "").strip()}
    except Exception as e:
        return {"tipo": "ERROR", "razon": str(e)[:120]}


# ══════════════════════════════════════════════════════════════════════════════
#  STAGE 2 — extractor de subtemas + verificación de nombres
# ══════════════════════════════════════════════════════════════════════════════
S2_SYSTEM = (
    "Sos un extractor de SUBTEMAS de un video-compilación documental, leyendo su transcript. "
    "Tu tarea: listar las ENTIDADES NOMBRADAS y CONCRETAS que el video recorre como sujetos "
    "separados — eventos, lugares, naufragios, barcos, casos, personas, sitios. Cada subtema "
    "debe ser una unidad que PODRÍA ser su propio video.\n\n"
    "Reglas:\n"
    "- Extraé la ENTIDAD concreta, no la categoría. Si el video describe 'un faro del que "
    "desaparecieron tres fareros en 1900', la entidad es ese caso puntual (su nombre real), "
    "no 'misterios de faros'.\n"
    "- Si un sujeto se narra sin nombre propio pero es claramente un caso concreto y real, "
    "dale el nombre canónico que mejor lo identifique si lo reconocés; si no lo podés nombrar, "
    "no lo inventes.\n"
    "- NO inventes nombres. Si el video es un concepto general o un listicle de tipos sin casos "
    "concretos (p.ej. 'criaturas marinas aterradoras' en general), devolvé lista VACÍA.\n"
    "- es_compilacion_item = true si el subtema aparece como uno más de la lista del video.\n"
    "Devolvé solo entidades reales y distintas; sin duplicados."
)

S2_SCHEMA = types.Schema(
    type=types.Type.OBJECT,
    required=["subtemas"],
    properties={
        "subtemas": types.Schema(
            type=types.Type.ARRAY,
            items=types.Schema(
                type=types.Type.OBJECT,
                required=["nombre_en", "es_compilacion_item"],
                properties={
                    "nombre_en": types.Schema(type=types.Type.STRING),
                    "es_compilacion_item": types.Schema(type=types.Type.BOOLEAN),
                },
            ),
        )
    },
)


def extract_one(title: str, transcript: str) -> list[dict]:
    prompt = (f"TÍTULO: {title}\n\nTRANSCRIPT (limpio):\n{transcript}\n\n"
              "Extraé los SUBTEMAS (entidades concretas nombradas). Si no hay casos concretos, "
              "devolvé subtemas: [].")

    def _do():
        resp = _client.models.generate_content(
            model=_cfg.gemini_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=S2_SYSTEM,
                response_mime_type="application/json",
                response_schema=S2_SCHEMA,
                temperature=0.0,
            ),
        )
        return json.loads(resp.text)

    try:
        d = _with_retry(_do)
        out = []
        seen = set()
        for s in (d.get("subtemas") or []):
            name = (s.get("nombre_en") or "").strip()
            if name and name.lower() not in seen:
                seen.add(name.lower())
                out.append({"nombre_en": name,
                            "es_compilacion_item": bool(s.get("es_compilacion_item", True))})
        return out
    except Exception as e:
        return [{"nombre_en": f"__ERROR__ {str(e)[:80]}", "es_compilacion_item": False}]


# ── Verificación de nombres (HALLAZGO 2): batch Flash → grafía canónica o null ──
VERIFY_SYSTEM = (
    "Sos un verificador de nombres propios extraídos de transcripts con errores de "
    "reconocimiento de voz (ASR). Para cada nombre, decidí si corresponde a una ENTIDAD REAL "
    "conocida (un evento, lugar, barco, persona, naufragio real). Si sí, devolvé su grafía "
    "CANÓNICA correcta (corrigiendo el error de ASR). Si no corresponde a nada real conocido "
    "o es demasiado genérico para ser una entidad, devolvé canonical=null.\n"
    "Ejemplos del tipo de corrección (conceptual): un nombre mal transcripto de un barco "
    "histórico se corrige a su grafía oficial; un nombre que no mapea a nada real → null."
)
VERIFY_SCHEMA = types.Schema(
    type=types.Type.OBJECT,
    required=["items"],
    properties={"items": types.Schema(
        type=types.Type.ARRAY,
        items=types.Schema(
            type=types.Type.OBJECT,
            required=["id", "canonical", "is_real"],
            properties={
                "id": types.Schema(type=types.Type.INTEGER),
                "canonical": types.Schema(type=types.Type.STRING, nullable=True),
                "is_real": types.Schema(type=types.Type.BOOLEAN),
            },
        ),
    )},
)


def verify_names(names: list[str]) -> dict[str, dict]:
    """name (raw) -> {canonical, is_real}. Batch de 40."""
    result: dict[str, dict] = {}
    uniq = list(dict.fromkeys(names))
    for start in range(0, len(uniq), 40):
        chunk = uniq[start:start + 40]
        lines = [f"{i}. {n}" for i, n in enumerate(chunk)]
        prompt = "Verificá estos nombres (corregí ASR o devolvé null):\n" + "\n".join(lines)

        def _do():
            resp = _client.models.generate_content(
                model=_cfg.gemini_model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=VERIFY_SYSTEM,
                    response_mime_type="application/json",
                    response_schema=VERIFY_SCHEMA,
                    temperature=0.0,
                ),
            )
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
    print("LAB SPY SUBTEMAS — chat 49. read-only, NO escribe seeds. stage 1+2.")
    print(f"corpus: {len(videos)} videos · answer-key 1-indexed")

    # ── STAGE 1 ──
    print("\n" + "=" * 78)
    print("STAGE 1 — clasificador (1 llamada Flash/video, schema, temp 0.0)")
    print("=" * 78)
    s1_rows = []
    for i, v in enumerate(videos, 1):
        key = ANSWER_KEY.get(i, "?")
        raw = v.get("transcript") or ""
        clean = clean_transcript(raw)
        title = v.get("title", "")
        if not clean or len(clean) < 50:
            s1_rows.append({"n": i, "title": title, "key": key, "tipo": "DROP_NO_TRANSCRIPT",
                            "razon": "transcript ausente/vacío", "tlen": len(clean)})
            print(f"  #{i:>2} [key={key:<10}] -> DROP_NO_TRANSCRIPT (sin transcript)")
            continue
        res = classify_one(title, clean)
        s1_rows.append({"n": i, "title": title, "key": key, "tipo": res["tipo"],
                        "razon": res["razon"], "tlen": len(clean)})
        trap = " <TRAMPA>" if i in TRAP_CASES else ""
        mark = "" if key in ("DROP", "?") else ("✓" if res["tipo"] == key else "✗")
        print(f"  #{i:>2} [key={key:<10}] -> {res['tipo']:<11} {mark}{trap}  :: {res['razon'][:70]}")
        time.sleep(SLEEP)

    # ── Matriz de confusión (solo sobre key ∈ {ATOMICO,CONTENEDOR,GENERICO}) ──
    classes = ["ATOMICO", "CONTENEDOR", "GENERICO"]
    confusion = {k: {p: 0 for p in classes + ["OTHER"]} for k in classes}
    scored = [r for r in s1_rows if r["key"] in classes]
    correct = 0
    for r in scored:
        pred = r["tipo"] if r["tipo"] in classes else "OTHER"
        confusion[r["key"]][pred] += 1
        if r["tipo"] == r["key"]:
            correct += 1
    trap_detail = [{"n": r["n"], "key": r["key"], "tipo": r["tipo"],
                    "hit": r["tipo"] == r["key"], "title": r["title"]}
                   for r in s1_rows if r["n"] in TRAP_CASES]

    print("\n  -- MATRIZ DE CONFUSIÓN (filas=answer-key, cols=predicho) --")
    _hdr = "key/pred"
    print(f"  {_hdr:<12}" + "".join(f"{c[:9]:>11}" for c in classes + ["OTHER"]))
    for k in classes:
        print(f"  {k:<12}" + "".join(f"{confusion[k][p]:>11}" for p in classes + ["OTHER"]))
    print(f"  ACCURACY (sobre {len(scored)} keyed): {correct}/{len(scored)}")
    print("  -- casos-trampa --")
    for t in trap_detail:
        print(f"    #{t['n']} key={t['key']} pred={t['tipo']} {'✓' if t['hit'] else '✗ FAIL'}")

    OUT_S1.write_text(json.dumps({
        "confusion": confusion, "accuracy": f"{correct}/{len(scored)}",
        "trap_cases": trap_detail, "rows": s1_rows,
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n  guardado: {OUT_S1}")

    # ── STAGE 2 — extractor sobre CONTENEDOR (predicho) + controles negativos ──
    print("\n" + "=" * 78)
    print("STAGE 2 — extractor de subtemas (CONTENEDOR predicho + controles neg)")
    print("=" * 78)
    targets = set(r["n"] for r in s1_rows if r["tipo"] == "CONTENEDOR") | NEG_CONTROLS
    by_n = {r["n"]: r for r in s1_rows}
    vid_by_n = {i: v for i, v in enumerate(videos, 1)}

    s2_rows = []
    all_names = []
    for n in sorted(targets):
        v = vid_by_n[n]
        clean = clean_transcript(v.get("transcript") or "")
        subs = extract_one(v.get("title", ""), clean) if clean else []
        for s in subs:
            all_names.append(s["nombre_en"])
        s2_rows.append({"n": n, "key": ANSWER_KEY.get(n, "?"),
                        "pred_tipo": by_n[n]["tipo"], "title": v.get("title", ""),
                        "n_subtemas": len(subs), "subtemas": subs})
        tag = " (NEG-CONTROL→debe ser 0)" if n in NEG_CONTROLS else (" [conocido]" if n in S2_KNOWN else "")
        print(f"  #{n:>2} [{by_n[n]['tipo']}] {len(subs)} subtemas{tag}")
        time.sleep(SLEEP)

    # ── Verificación de nombres (HALLAZGO 2) ──
    print(f"\n  Verificando {len(set(n for n in all_names))} nombres únicos (batch Flash)...")
    verif = verify_names([n for n in all_names if not n.startswith("__ERROR__")])
    for row in s2_rows:
        for s in row["subtemas"]:
            v = verif.get(s["nombre_en"])
            if v:
                s["canonical"] = v["canonical"]
                s["is_real"] = v["is_real"]
                s["asr_corrected"] = bool(v["canonical"]) and v["canonical"].strip().lower() != s["nombre_en"].strip().lower()
            else:
                s["canonical"] = None
                s["is_real"] = None
                s["asr_corrected"] = False

    OUT_S2.write_text(json.dumps({"rows": s2_rows}, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  guardado: {OUT_S2}")

    # ── Resumen stage 2 a stdout ──
    print("\n  -- STAGE 2 muestra (conocidos + controles) --")
    for row in s2_rows:
        if row["n"] in S2_KNOWN | NEG_CONTROLS:
            print(f"\n  #{row['n']} {row['title'][:60]}  ({row['n_subtemas']} subtemas)")
            for s in row["subtemas"][:14]:
                can = s.get("canonical")
                flag = ""
                if can and s.get("asr_corrected"):
                    flag = f"  → CANÓNICO: {can}"
                elif s.get("is_real") is False:
                    flag = "  → no-real?"
                print(f"      • {s['nombre_en']}{flag}")

    # totales de verificación
    total_subs = sum(r["n_subtemas"] for r in s2_rows)
    corrected = sum(1 for r in s2_rows for s in r["subtemas"] if s.get("asr_corrected"))
    not_real = sum(1 for r in s2_rows for s in r["subtemas"] if s.get("is_real") is False)
    print(f"\n  TOTALES stage2: {total_subs} subtemas · {corrected} corregidos por ASR-verif · "
          f"{not_real} marcados no-real")
    print(f"\nGuardado:\n  {OUT_S1}\n  {OUT_S2}")


if __name__ == "__main__":
    main()
