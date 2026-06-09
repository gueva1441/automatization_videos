"""
subtopic_es_relevance.py — Fix saturación ES (Diseño B), Piezas 1 y 3.

El bug: medir saturación ES con el keyword EN + `title_contains_anchor` (substring del ancla
inglesa) falla para nombres transliterados (Chernobyl→"Chernóbil") → 0 competidores falsos →
VACIO falso → un tema saturadísimo entra como hueco. El fix NO relaja el regex; busca en español
y deja que un juez-LLM decida la relevancia semánticamente.

Dos llamadas Gemini Flash, ambas con `response_schema` (MODEL_PROMPTING_RULES §3 R4), una
destilación por llamada (R1), few-shot conceptual y no literal (AP3):

  translate_to_es(name)        -> {"es_query": str, "es_aliases": [str]}   # Pieza 1
  filter_relevant(entity, cands, aliases=...) -> list[dict]                # Pieza 3 (sub-lista relevante)

Tolerancia a fallo (las maneja el caller _measure_es): translate_to_es lanza si Gemini falla
(el caller cae a la grafía EN); filter_relevant lanza si Gemini falla (el caller emite ES_ERROR,
no fabrica dato).
"""
from __future__ import annotations

import json

from gemini_helpers import _client, _cfg, types, _with_retry

# ── Pieza 1: traducción de grafía EN→ES ──────────────────────────────────────────────────────

_TRANSLATE_SYSTEM = (
    "Convertís el NOMBRE de una entidad concreta (un lugar, un caso, un evento, una persona) a la "
    "grafía con la que el público hispanohablante la busca y titula videos en YouTube. "
    "Reglas:\n"
    "- Si el nombre se escribe IGUAL en español, devolvelo sin cambios.\n"
    "- Si tiene una grafía/transliteración española establecida distinta de la inglesa (por "
    "ejemplo topónimos que el español acentúa o adapta), devolvé la grafía española REAL y "
    "corriente, no una invención.\n"
    "- NO generalices a un tema más amplio ni cambies de entidad: es la MISMA entidad, solo su "
    "grafía española.\n"
    "- Devolvé además 'es_aliases': otras grafías con las que un video hispano podría titular la "
    "MISMA entidad, INCLUYENDO la grafía inglesa original si el español también la usa. Sirven "
    "como red de seguridad para la búsqueda; ante la duda, incluí más aliases razonables.\n"
    "No expliques nada; solo devolvé el JSON del schema."
)

_TRANSLATE_SCHEMA = types.Schema(
    type=types.Type.OBJECT,
    required=["es_query"],
    properties={
        "es_query": types.Schema(type=types.Type.STRING),
        "es_aliases": types.Schema(type=types.Type.ARRAY, items=types.Schema(type=types.Type.STRING)),
    },
)


def translate_to_es(name: str) -> dict:
    """Pieza 1. Devuelve {"es_query": str, "es_aliases": [str]}. Lanza si Gemini falla
    (el caller decide el fallback a la grafía EN)."""
    prompt = (f'ENTIDAD (en inglés): {name}\n\n'
              "Devolvé su grafía española de búsqueda (es_query) y aliases (es_aliases).")

    def _do():
        resp = _client.models.generate_content(
            model=_cfg.gemini_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=_TRANSLATE_SYSTEM,
                response_mime_type="application/json",
                response_schema=_TRANSLATE_SCHEMA,
                temperature=0.0,
            ),
        )
        return json.loads(resp.text)

    d = _with_retry(_do)
    es_query = (d.get("es_query") or "").strip() or name
    aliases = [a.strip() for a in (d.get("es_aliases") or []) if isinstance(a, str) and a.strip()]
    # garantizar que el nombre EN esté entre los aliases (red de seguridad para el juez)
    if name.strip() and name.strip().lower() not in {a.lower() for a in aliases} \
            and name.strip().lower() != es_query.lower():
        aliases.append(name.strip())
    return {"es_query": es_query, "es_aliases": aliases}


# ── Pieza 3: juez de relevancia sobre la lista cruda ─────────────────────────────────────────

_RELEVANCE_SYSTEM = (
    "Te doy una ENTIDAD concreta (un lugar/caso/evento) y una lista numerada de títulos de videos "
    "de YouTube en español. Para CADA título decidí si el video trata de ESA MISMA entidad.\n"
    "- Cuenta como relevante si el tema central del título es esa entidad (ese lugar/caso/evento), "
    "aunque use otra grafía, otro idioma de transliteración, o la nombre dentro de un título más "
    "largo.\n"
    "- NO cuenta si es de OTRO tema, una entidad HOMÓNIMA distinta (mismo nombre, otro lugar/cosa), "
    "una lista o recopilación genérica que solo la menciona de pasada, o contenido apenas "
    "relacionado.\n"
    "Ante la duda razonable de que sea la misma entidad, NO la incluyas (preferí precisión). "
    "Devolvé solo los índices (enteros) de los títulos relevantes."
)

_RELEVANCE_SCHEMA = types.Schema(
    type=types.Type.OBJECT,
    required=["relevantes"],
    properties={"relevantes": types.Schema(
        type=types.Type.ARRAY, items=types.Schema(type=types.Type.INTEGER))},
)

_MAX_TITLES = 60   # cota del batch (1 sola llamada; YT_LIMIT_ARCHAEOLOGY=50 × 2 pasadas, ya filtrado ES)


def filter_relevant(entity: str, candidates: list[dict], aliases: list[str] | None = None) -> list[dict]:
    """Pieza 3. Filtra `candidates` (cada uno {title, views, months, ...}) dejando solo los que
    el juez considera de la MISMA entidad. UNA llamada batch. Lanza si Gemini falla
    (el caller emite ES_ERROR). Si no hay candidatos, devuelve []."""
    if not candidates:
        return []
    batch = candidates[:_MAX_TITLES]
    alias_str = ""
    if aliases:
        alias_str = " (también conocida como: " + ", ".join(aliases) + ")"
    titles_block = "\n".join(f"{i}. {(c.get('title') or '')[:140]}" for i, c in enumerate(batch))
    prompt = (f"ENTIDAD: {entity}{alias_str}\n\n"
              f"TÍTULOS:\n{titles_block}\n\n"
              "Devolvé los índices de los títulos que tratan de ESA entidad.")

    def _do():
        resp = _client.models.generate_content(
            model=_cfg.gemini_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=_RELEVANCE_SYSTEM,
                response_mime_type="application/json",
                response_schema=_RELEVANCE_SCHEMA,
                temperature=0.0,
            ),
        )
        return json.loads(resp.text)

    d = _with_retry(_do)
    idxs = d.get("relevantes") or []
    out = []
    seen = set()
    for i in idxs:
        try:
            i = int(i)
        except (TypeError, ValueError):
            continue
        if 0 <= i < len(batch) and i not in seen:
            seen.add(i)
            out.append(batch[i])
    return out
