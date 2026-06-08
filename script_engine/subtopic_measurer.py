"""
subtopic_measurer.py — Stage 3 del fix spy-subtemas: medidor de demanda por subtema
(contrato cerrado, chat 49 Addendum 2/3).

Contrato del medidor (NO re-abrir):
  - compuerta ES-PRIMERO: score_spanish_saturation → si SATURADO, descarta (no paga EN).
    Solo VACIO/HUECO pagan la medición EN. (Addendum 2 D7; Doña Paz lo probó.)
  - vara LAXO: standalone EN con vistas medianas propias (top_views >= LAXO_FLOOR_VIEWS).
    La fórmula outlier (compute_outlier_filter) NO se usa para subtemas (Addendum 2 D5):
    mide anomalía-de-canal, señal equivocada para un subtema-entidad (mató Marine Sulphur
    Queen con 585k reales).
  - chequeo de RELEVANCIA título↔entidad (Addendum 3 D12): el top result debe tratar de la
    entidad medida, o no cuenta (mata la contaminación Azores→Antártida). Substring de anclas
    por defecto; deuda anotada: es coarse (mismo-lugar/otro-sujeto no lo caza).

Reusa prod SIN reescribir: score_spanish_saturation, search_viral_english, extract_anchors.
NO usa compute_outlier_filter.

API:
    measure(name) -> dict   # ver SHAPE abajo; measure(...)["passes"] = bool  (ES-primero + EN, JUNTOS)

    # T3 (chat 49): el fan-out usa las DOS fases por separado para no pagar el ES caro de los
    # sujetos que el cap K va a tirar. measure() queda como wrapper para quien quiera ambas.
    _measure_en_laxo(name) -> dict   # solo demanda EN (LAXO + relevancia). Barato. {top_rel_views, pasa_laxo, ...}
    _measure_es(name) -> dict        # solo saturación ES (score_spanish_saturation). Caro. {label, saturation, ...}
"""
from __future__ import annotations

import re

from script_engine.youtube_scanner import (
    score_spanish_saturation, search_viral_english, extract_anchors,
)

# Constantes (cabecera del módulo; LAXO_FLOOR_VIEWS = decisión abierta #2, lab=50k provisional)
LAXO_FLOOR_VIEWS = 50_000
EN_SEARCH_LIMIT = 15
ES_SATURATED_LABEL = "SATURADO"


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


def _measure_es(name: str) -> dict:
    try:
        sat = score_spanish_saturation(name, anchors=extract_anchors(name))
        return {"label": sat.get("label"), "saturation": sat.get("saturation"),
                "heaviest": sat.get("heaviest"), "ontopic_count": sat.get("ontopic_count"),
                "anchors_used": sat.get("anchors_used"), "source": sat.get("source")}
    except Exception as e:
        return {"label": "ERROR", "error": str(e)[:100]}


def _measure_en_laxo(name: str) -> dict:
    """LAXO + relevancia. top_views relevante >= piso. SIN outlier filter."""
    try:
        cands = search_viral_english(name, limit=EN_SEARCH_LIMIT)
    except Exception as e:
        return {"error": str(e)[:100], "top_views": 0, "pasa_laxo": False}
    cands_sorted = sorted(cands, key=lambda c: int(c.get("views") or 0), reverse=True)
    relevantes = [c for c in cands_sorted if is_relevant(name, c.get("title", ""))]
    top_rel = relevantes[0] if relevantes else None
    top_raw = cands_sorted[0] if cands_sorted else None
    top_rel_views = int((top_rel or {}).get("views") or 0) if top_rel else 0
    return {
        "n_cands": len(cands), "n_relevantes": len(relevantes),
        "top_raw_title": (top_raw or {}).get("title"),
        "top_raw_views": int((top_raw or {}).get("views") or 0) if top_raw else 0,
        "top_rel_title": (top_rel or {}).get("title"),
        "top_rel_video_id": (top_rel or {}).get("video_id"),
        "top_rel_views": top_rel_views,
        "pasa_laxo": top_rel_views >= LAXO_FLOOR_VIEWS,
    }


def measure(name: str) -> dict:
    """Mide un subtema con compuerta ES-primero + vara LAXO + relevancia EN.

    Returns:
        {
          "name": str,
          "es": {label, saturation, ...},
          "en": {top_rel_views, pasa_laxo, ...} | None (si gateado por ES),
          "passes": bool,          # ES no-saturado Y EN LAXO relevante pasa
          "gated_by_es": bool,     # True si se cortó por ES SATURADO (no pagó EN)
          "verdict": "PASA" | "CORTADO_ES" | "CORTA_LAXO" | "EN_ERROR" | "ES_ERROR"
        }
    """
    es = _measure_es(name)
    if es.get("label") == "ERROR":
        return {"name": name, "es": es, "en": None, "passes": False,
                "gated_by_es": False, "verdict": "ES_ERROR"}
    if es.get("label") == ES_SATURATED_LABEL:
        return {"name": name, "es": es, "en": None, "passes": False,
                "gated_by_es": True, "verdict": "CORTADO_ES"}
    en = _measure_en_laxo(name)
    if en.get("error"):
        return {"name": name, "es": es, "en": en, "passes": False,
                "gated_by_es": False, "verdict": "EN_ERROR"}
    passes = bool(en.get("pasa_laxo"))
    return {"name": name, "es": es, "en": en, "passes": passes,
            "gated_by_es": False, "verdict": "PASA" if passes else "CORTA_LAXO"}
