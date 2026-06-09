"""
subtopic_measurer.py — Stage 3 del fix spy-subtemas: medidor de demanda por subtema
(contrato cerrado, chat 49 Addendum 2/3).

Contrato del medidor (NO re-abrir):
  - compuerta ES-PRIMERO: se mide saturación ES → si SATURADO, descarta (no paga EN).
    Solo VACIO/HUECO pagan la medición EN. (Addendum 2 D7; Doña Paz lo probó.)
  - vara LAXO: standalone EN con vistas medianas propias (top_views >= LAXO_FLOOR_VIEWS).
    La fórmula outlier (compute_outlier_filter) NO se usa para subtemas (Addendum 2 D5):
    mide anomalía-de-canal, señal equivocada para un subtema-entidad (mató Marine Sulphur
    Queen con 585k reales).
  - chequeo de RELEVANCIA título↔entidad EN: el top result debe tratar de la entidad medida
    (mata la contaminación Azores→Antártida). En EN sigue por substring de anclas (is_relevant).

Saturación ES (fix Diseño B — reemplaza score_spanish_saturation SOLO acá): el substring de
ancla EN fallaba para nombres transliterados (Chernobyl→"Chernóbil" daba 0 competidores falsos).
Ahora _measure_es traduce la grafía ES (subtopic_es_relevance.translate_to_es) → trae la lista ES
CRUDA sin ancla (youtube_scanner.list_spanish_candidates) → un juez-LLM filtra relevancia
(filter_relevant) → label con la MISMA matemática/umbrales reusados (_es_age_decay,
_es_saturation_label). score_spanish_saturation queda intacto para topic_validator y Mode B.

Reusa prod SIN reescribir: list_spanish_candidates, search_viral_english, extract_anchors,
_es_age_decay, _es_saturation_label. NO usa compute_outlier_filter.

API:
    measure(name) -> dict   # ver SHAPE abajo; measure(...)["passes"] = bool  (ES-primero + EN, JUNTOS)

    # T3 (chat 49): el fan-out usa las DOS fases por separado para no pagar el ES caro de los
    # sujetos que el cap K va a tirar. measure() queda como wrapper para quien quiera ambas.
    _measure_en_laxo(search_query, entity=None) -> dict   # demanda EN: busca con search_query, relevancia vs entity
    _measure_es(search_query, entity=None) -> dict        # saturación ES: busca con search_query, relevancia vs entity

CHAT 51 — los medidores separan "con qué busco" (search_query angulado) de "contra qué mido
relevancia" (entity = nombre canónico). entity opcional → default search_query (compat 1-arg).
Safety net over-narrow: si la query angulada trae pocos/0 resultados, re-busca con la entidad
pelada y marca query_fallback=True (nunca matar demanda real por una query muy específica).
"""
from __future__ import annotations

import re

from script_engine.youtube_scanner import (
    search_viral_english, extract_anchors,
    list_spanish_candidates, _es_age_decay, _es_saturation_label,
)
from script_engine.subtopic_es_relevance import translate_to_es, filter_relevant

# Constantes (cabecera del módulo; LAXO_FLOOR_VIEWS = decisión abierta #2, lab=50k provisional)
LAXO_FLOOR_VIEWS = 50_000
EN_SEARCH_LIMIT = 15
ES_SATURATED_LABEL = "SATURADO"
# CHAT 51 — safety net over-narrow: si la query angulada trae < EN_MIN_CANDS, re-buscar con la
# entidad pelada (nunca matar demanda real por una query demasiado específica). query_fallback=True.
EN_MIN_CANDS = 5


def is_relevant(entity: str, title: str) -> bool:
    """Relevancia título↔entidad por substring de anclas (D12). Coarse (deuda anotada)."""
    if not title:
        return False
    tl = title.lower()
    anchors = [a.lower() for a in extract_anchors(entity) if len(a) >= 4]
    if anchors:
        return any(a in tl for a in anchors)
    words = [w for w in re.findall(r"\w+", entity.lower()) if len(w) >= 4]
    return any(w in tl for w in words)


def _measure_es(search_query: str, entity: str | None = None) -> dict:
    """Fix saturación ES (Diseño B): traducir grafía EN→ES → lista ES CRUDA (sin ancla substring,
    que era el bug Chernobyl→"Chernóbil") → juez-LLM de relevancia → label con la MISMA matemática
    y umbrales reusados (eff = views * _es_age_decay(months); saturación = max(eff);
    _es_saturation_label). Reemplaza score_spanish_saturation SOLO en este camino (fan-out).
    El shape de salida es el mismo de antes (+ es_query), para no romper al caller.

    CHAT 51 — separa "con qué busco" (search_query, angulado) de "contra qué mido relevancia"
    (entity, nombre canónico; el juez filter_relevant juzga contra entity). Safety net over-narrow:
    si la query angulada trae 0 candidatos ES, re-busca con la entidad pelada (query_fallback=True).
    entity opcional → default search_query (compat con callers viejos de 1 arg).

    Fallos: traducción que falla → grafía EN (no rompe). Scrape ES totalmente caído o juez de
    relevancia que falla → label="ERROR" (no fabrica dato; el measurer lo trata como ES_ERROR)."""
    entity = entity or search_query
    # Pieza 1 — traducir a grafía ES la QUERY angulada (fallback a EN si Gemini falla)
    try:
        tr = translate_to_es(search_query)
        es_query, aliases = tr["es_query"], tr.get("es_aliases") or []
    except Exception:
        es_query, aliases = search_query, []

    # Pieza 2 — lista ES cruda (sin ancla; tolera SSL: None = todas las pasadas cayeron)
    try:
        cands = list_spanish_candidates(es_query)
    except Exception as e:
        return {"label": "ERROR", "error": f"scrape ES: {str(e)[:90]}", "es_query": es_query}
    if cands is None:
        return {"label": "ERROR", "error": "scrape ES falló (todas las pasadas)", "es_query": es_query}

    # over-narrow ES: 0 candidatos con la query angulada → red de seguridad con la entidad pelada
    query_fallback = False
    if not cands and entity != search_query:
        try:
            tr2 = translate_to_es(entity)
            es_query_fb, aliases_fb = tr2["es_query"], tr2.get("es_aliases") or aliases
        except Exception:
            es_query_fb, aliases_fb = entity, aliases
        try:
            cands_fb = list_spanish_candidates(es_query_fb)
        except Exception:
            cands_fb = None
        if cands_fb:
            cands, es_query, aliases, query_fallback = cands_fb, es_query_fb, aliases_fb, True

    # Pieza 3 — juez de relevancia sobre la lista, juzgando contra ENTITY (0 videos = VACIO legítimo)
    if cands:
        try:
            relevant = filter_relevant(entity, cands, aliases=aliases)
        except Exception as e:
            return {"label": "ERROR", "error": f"juez relevancia: {str(e)[:80]}", "es_query": es_query}
    else:
        relevant = []

    # saturación = competidor relevante más pesado (misma fórmula y umbrales que score_spanish_saturation)
    best = None
    for c in relevant:
        months = c.get("months")
        decay = _es_age_decay(months)
        eff = (c.get("views") or 0) * decay
        if best is None or eff > best["eff"]:
            best = {"title": (c.get("title") or "")[:80], "views": c.get("views"),
                    "months": months, "decay": decay, "eff": eff}
    saturation = best["eff"] if best else 0.0
    return {
        "label": _es_saturation_label(saturation),
        "saturation": saturation,
        "heaviest": best,
        "ontopic_count": len(relevant),
        "anchors_used": [es_query],          # ahora = la query ES usada (ya no anclas substring EN)
        "source": "scrapetube+juez",
        "es_query": es_query,
        "query_fallback": query_fallback,
    }


def _measure_en_laxo(search_query: str, entity: str | None = None) -> dict:
    """LAXO + relevancia. top_views relevante >= piso. SIN outlier filter.

    CHAT 51 — separa "con qué busco" de "contra qué mido relevancia":
      - BUSCA con search_query (entidad + ángulo del segmento → YouTube devuelve on-topic).
      - RELEVANCIA con entity (nombre canónico; is_relevant(entity, title), igual que antes).
    Safety net over-narrow: si la query angulada trae < EN_MIN_CANDS, re-busca con la entidad
    pelada y marca query_fallback=True (nunca matar demanda real por una query muy específica).
    entity opcional → default search_query (compat con callers viejos de 1 arg)."""
    entity = entity or search_query
    try:
        cands = search_viral_english(search_query, limit=EN_SEARCH_LIMIT)
    except Exception as e:
        return {"error": str(e)[:100], "top_views": 0, "pasa_laxo": False}
    query_used, query_fallback = search_query, False
    # over-narrow: pocos resultados con la query angulada → red de seguridad con la entidad pelada
    if len(cands) < EN_MIN_CANDS and entity != search_query:
        try:
            cands_fb = search_viral_english(entity, limit=EN_SEARCH_LIMIT)
        except Exception:
            cands_fb = None
        if cands_fb and len(cands_fb) > len(cands):
            cands, query_used, query_fallback = cands_fb, entity, True
    cands_sorted = sorted(cands, key=lambda c: int(c.get("views") or 0), reverse=True)
    relevantes = [c for c in cands_sorted if is_relevant(entity, c.get("title", ""))]
    top_rel = relevantes[0] if relevantes else None
    top_raw = cands_sorted[0] if cands_sorted else None
    top_rel_views = int((top_rel or {}).get("views") or 0) if top_rel else 0
    return {
        "query_used": query_used, "query_fallback": query_fallback,
        "n_cands": len(cands), "n_relevantes": len(relevantes),
        "top_raw_title": (top_raw or {}).get("title"),
        "top_raw_views": int((top_raw or {}).get("views") or 0) if top_raw else 0,
        "top_rel_title": (top_rel or {}).get("title"),
        "top_rel_video_id": (top_rel or {}).get("video_id"),
        "top_rel_views": top_rel_views,
        # CHAT 50: el candidato EN ya trae channel_id + en_age_months precalculados
        # (youtube_scanner._scrape_viral_english). Propagarlos GRATIS ($0, sin fetch) para
        # que el fan-out pueda calcular outlier_ratio/channel_median sobre los survivors.
        "top_rel_channel_id": (top_rel or {}).get("channel_id"),
        "top_rel_age_months": (top_rel or {}).get("en_age_months"),
        "pasa_laxo": top_rel_views >= LAXO_FLOOR_VIEWS,
    }


def measure(search_query: str, entity: str | None = None) -> dict:
    """Mide un subtema con compuerta ES-primero + vara LAXO + relevancia EN.

    CHAT 51 — busca con search_query (angulado), mide relevancia contra entity. entity opcional
    → default search_query (compat con callers viejos de 1 arg).

    Returns:
        {
          "name": str,             # = entity (nombre canónico)
          "es": {label, saturation, ...},
          "en": {top_rel_views, pasa_laxo, ...} | None (si gateado por ES),
          "passes": bool,          # ES no-saturado Y EN LAXO relevante pasa
          "gated_by_es": bool,     # True si se cortó por ES SATURADO (no pagó EN)
          "verdict": "PASA" | "CORTADO_ES" | "CORTA_LAXO" | "EN_ERROR" | "ES_ERROR"
        }
    """
    entity = entity or search_query
    es = _measure_es(search_query, entity)
    if es.get("label") == "ERROR":
        return {"name": entity, "es": es, "en": None, "passes": False,
                "gated_by_es": False, "verdict": "ES_ERROR"}
    if es.get("label") == ES_SATURATED_LABEL:
        return {"name": entity, "es": es, "en": None, "passes": False,
                "gated_by_es": True, "verdict": "CORTADO_ES"}
    en = _measure_en_laxo(search_query, entity)
    if en.get("error"):
        return {"name": entity, "es": es, "en": en, "passes": False,
                "gated_by_es": False, "verdict": "EN_ERROR"}
    passes = bool(en.get("pasa_laxo"))
    return {"name": entity, "es": es, "en": en, "passes": passes,
            "gated_by_es": False, "verdict": "PASA" if passes else "CORTA_LAXO"}
