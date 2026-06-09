"""
subtopic_extractor.py — Stage 2 del fix spy-subtemas: extractor de SUJETOS-DE-SEGMENTO
de un video CONTENEDOR (contrato cerrado, chat 49 Addendum 3 D9).

- Unidad = SUJETO-DE-SEGMENTO: los N casos a los que el video le dedica un TRAMO propio de
  narración. NO toda entidad nombrada (las menciones incidentales — lugares, fechas, personas
  dentro del segmento de otro caso — se excluyen). Validado: #15 168→17, #17→18, #20→30.
- SIN eje de producibilidad/nicho (D10). Eso lo filtran las puertas + el gate humano.
- verify_names() = review-flag de ASR (D4): grafía canónica o is_real=False. NUNCA dropea.

API:
    extract_segment_subjects(title, transcript) -> list[dict]   # {nombre_en, search_query_en, angle_en}
    verify_names(names) -> dict[str, {"canonical": str|None, "is_real": bool}]   # review-flag

CHAT 51 — cada sujeto ahora es un dict de 3 campos (antes un str pelado), cada uno a su destino:
  - nombre_en       : entidad canónica → relevancia + dedup + provenance.
  - search_query_en : entidad + 2-3 palabras del ángulo → con qué se BUSCA (EN/ES). Ni pelado
                      (trae genérico), ni oración (over-narrow → 0 resultados).
  - angle_en        : frase corta del ángulo del segmento → seed_title que groundea el research.
El transcript es SEÑAL (clasificar/extraer/ángulo), NUNCA base del guion (la narración la hace
el research independiente — copyright + reused-content).
"""
from __future__ import annotations

import json

from gemini_helpers import _client, _cfg, types, _with_retry

TRANSCRIPT_CAP = 500_000

SEGMENT_SYSTEM = (
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
    "NO juzgues si el tema es producible, popular ni de ningún nicho — solo su rol estructural.\n\n"
    "Para CADA sujeto-de-segmento devolvé TRES campos:\n"
    "1. nombre_en — el nombre canónico real de la entidad (lugar, caso, obra), pelado.\n"
    "2. angle_en — una frase CORTA y específica del ángulo que ESTE video le da a la entidad "
    "(el por-qué aparece: qué le pasó, qué la vuelve un caso). El calificador concreto del "
    "segmento, no una oración larga.\n"
    "3. search_query_en — con qué buscarías ESE segmento en YouTube: el nombre del lugar MÁS "
    "2-3 palabras del ángulo. El nombre pelado solo trae resultados genéricos de turismo o "
    "geografía que no son el tema; una oración entera no devuelve resultados. El punto medio: "
    "la entidad acompañada del calificador clave en pocas palabras.\n"
    "Patrón conceptual (no copies estas palabras literalmente): <nombre del lugar> + <2-3 "
    "palabras del por-qué del segmento>.\n"
    "Dá el nombre canónico real de cada sujeto. Sin duplicados."
)

_SEGMENT_SCHEMA = types.Schema(
    type=types.Type.OBJECT, required=["subtemas"],
    properties={"subtemas": types.Schema(
        type=types.Type.ARRAY, items=types.Schema(
            type=types.Type.OBJECT,
            required=["nombre_en", "search_query_en", "angle_en"],
            properties={
                "nombre_en": types.Schema(type=types.Type.STRING),
                "search_query_en": types.Schema(type=types.Type.STRING),
                "angle_en": types.Schema(type=types.Type.STRING),
            }))})


def extract_segment_subjects(title: str, transcript: str) -> list[dict]:
    """Devuelve la lista de sujetos-de-segmento como dicts {nombre_en, search_query_en,
    angle_en}. [] si falla. search_query_en/angle_en caen a nombre_en si el modelo los omite."""
    transcript = (transcript or "")[:TRANSCRIPT_CAP]
    prompt = (f"TÍTULO: {title}\n\nTRANSCRIPT (limpio):\n{transcript}\n\n"
              "Devolvé SOLO los sujetos-de-segmento (los N casos del recorrido). Excluí las "
              "menciones incidentales que viven dentro del segmento de otro caso.")

    def _do():
        resp = _client.models.generate_content(
            model=_cfg.gemini_model, contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SEGMENT_SYSTEM, response_mime_type="application/json",
                response_schema=_SEGMENT_SCHEMA, temperature=0.0))
        return json.loads(resp.text)

    try:
        d = _with_retry(_do)
        out, seen = [], set()
        for s in (d.get("subtemas") or []):
            nm = (s.get("nombre_en") or "").strip()
            if not nm or nm.lower() in seen:
                continue
            seen.add(nm.lower())
            sq = (s.get("search_query_en") or "").strip() or nm   # fallback al pelado si falta
            ang = (s.get("angle_en") or "").strip() or nm
            out.append({"nombre_en": nm, "search_query_en": sq, "angle_en": ang})
        return out
    except Exception:
        return []


# ── Verificación ASR (D4): REVIEW-FLAG, nunca kill-gate ──
_VERIFY_SYSTEM = (
    "Verificás nombres propios extraídos de transcripts con errores de ASR. Para cada nombre, "
    "si corresponde a una ENTIDAD REAL conocida devolvé su grafía CANÓNICA (corrigiendo el "
    "ASR); si no corresponde a nada real, canonical=null e is_real=false. Esto es solo un FLAG "
    "de revisión, no decide nada."
)
_VERIFY_SCHEMA = types.Schema(
    type=types.Type.OBJECT, required=["items"],
    properties={"items": types.Schema(type=types.Type.ARRAY, items=types.Schema(
        type=types.Type.OBJECT, required=["id", "canonical", "is_real"],
        properties={
            "id": types.Schema(type=types.Type.INTEGER),
            "canonical": types.Schema(type=types.Type.STRING, nullable=True),
            "is_real": types.Schema(type=types.Type.BOOLEAN),
        }))})


def verify_names(names: list[str], batch: int = 40) -> dict[str, dict]:
    """REVIEW-FLAG (no dropea). name -> {"canonical": str|None, "is_real": bool}."""
    result: dict[str, dict] = {}
    uniq = list(dict.fromkeys(n for n in names if n))
    for start in range(0, len(uniq), batch):
        chunk = uniq[start:start + batch]
        prompt = "Verificá (corregí ASR o null):\n" + "\n".join(
            f"{i}. {n}" for i, n in enumerate(chunk))

        def _do():
            resp = _client.models.generate_content(
                model=_cfg.gemini_model, contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=_VERIFY_SYSTEM, response_mime_type="application/json",
                    response_schema=_VERIFY_SCHEMA, temperature=0.0))
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
    return result
