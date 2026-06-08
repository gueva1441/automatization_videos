"""
subtopic_classifier.py — Stage 1 del fix spy-subtemas: clasificador BINARIO
ATÓMICO/CONTENEDOR de un video, leyendo su transcript (contrato cerrado, chat 49).

- BINARIO + test del video-standalone (Addendum 1 D3 / Addendum 3): "¿cada cosa se sostiene
  SOLA como video propio, o son facetas del MISMO asunto que solo importan juntas?".
- Gemini Flash + response_schema (MODEL_PROMPTING_RULES §3 R4), temperature=0.0.
- NO juzga producibilidad ni nicho — solo estructura (Addendum 3 D10).

Validado en lab: stage 1 binario 24/25 (con #3→CONTENEDOR en el key), casos-trampa 4/4.

API:
    classify(title: str, transcript: str) -> dict  # {"tipo": "ATOMICO|CONTENEDOR", "razon": str}
"""
from __future__ import annotations

import json

from gemini_helpers import _client, _cfg, types, _with_retry

SYSTEM_INSTRUCTION = (
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

_SCHEMA = types.Schema(
    type=types.Type.OBJECT,
    required=["tipo", "razon"],
    properties={
        "tipo": types.Schema(type=types.Type.STRING, enum=["ATOMICO", "CONTENEDOR"]),
        "razon": types.Schema(type=types.Type.STRING),
    },
)

TRANSCRIPT_CAP = 500_000


def classify(title: str, transcript: str) -> dict:
    """Clasifica ATOMICO vs CONTENEDOR. Devuelve {"tipo", "razon"}.
    tipo == "ERROR" si Gemini falla (el caller decide fallback)."""
    transcript = (transcript or "")[:TRANSCRIPT_CAP]
    prompt = (f"TÍTULO: {title}\n\nTRANSCRIPT (limpio):\n{transcript}\n\n"
              "Clasificá ATOMICO vs CONTENEDOR aplicando el TEST DECISIVO.")

    def _do():
        resp = _client.models.generate_content(
            model=_cfg.gemini_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                response_mime_type="application/json",
                response_schema=_SCHEMA,
                temperature=0.0,
            ),
        )
        return json.loads(resp.text)

    try:
        d = _with_retry(_do)
        return {"tipo": d.get("tipo", "ERROR"), "razon": (d.get("razon") or "").strip()}
    except Exception as e:
        return {"tipo": "ERROR", "razon": str(e)[:120]}
