"""
_lab_spy_stage3_chat49.py — LAB (chat 49 addendum) STAGE 3: vara de demanda EN por subtema.
read-only sobre prod (NO escribe seeds, NO toca data/). SÍ gasta scrape (YouTube/scrapetube
vía proxy) — limitado a ~5 subtemas LIMPIOS de #15/#17. Reporta costo aprox.

PREGUNTA ABIERTA (del handoff): ¿qué vara de demanda EN por subtema?
  ESTRICTO = el subtema tiene su PROPIO standalone viral EN (pasa compute_outlier_filter).
  LAXO     = aparece en la compilación + tiene algo MEDIANO propio (un standalone con vistas
             decentes aunque no sea outlier fuerte).
Correr ambas sobre los subtemas y ver cuál no deja pasar basura ni mata oro.

Compuerta barata primero: ES (score_spanish_saturation) es más barato que EN (outlier hace
get_channel por candidato con anti-ban 2s). Se mide ES primero y se reporta; en un pipeline
real un ES SATURADO gatearía-out antes de pagar EN. Acá medimos EN igual (es la pregunta).

Reusa prod sin reescribir: search_viral_english, compute_outlier_filter, extract_anchors,
score_spanish_saturation, count_competing_spanish, detect_language.

Correr:  python -X utf8 _lab_spy_stage3_chat49.py
Output:  _lab_out/spy_subtemas_stage3.json
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from script_engine.youtube_scanner import (
    search_viral_english, compute_outlier_filter, extract_anchors,
    score_spanish_saturation, count_competing_spanish,
)

LAB_OUT = Path("_lab_out")
OUT = LAB_OUT / "spy_subtemas_stage3.json"

# Subtemas limpios de #15/#17 (no dependen de ningún fix de stage 1/2)
SUBTEMAS = [
    "Mary Celeste",
    "USS Cyclops",
    "Wilhelm Gustloff",
    "Doña Paz",
    "Marine Sulphur Queen",
]

EN_SEARCH_LIMIT = 15        # acota get_channel del outlier (costo)
LAXO_FLOOR_VIEWS = 50_000   # "algo mediano propio" para LAXO (declarado, tunable)
SCRAPE_COUNT = {"en_search": 0, "en_outlier": 0, "es_sat": 0, "es_count": 0}


def measure_es(name: str) -> dict:
    """Lado barato: saturación ES + competidores. Compuerta previa."""
    anchors = extract_anchors(name)
    try:
        SCRAPE_COUNT["es_sat"] += 1
        sat = score_spanish_saturation(name, anchors=anchors)
    except Exception as e:
        sat = {"error": str(e)[:100]}
    try:
        SCRAPE_COUNT["es_count"] += 1
        comp = count_competing_spanish(name, anchors=anchors)
    except Exception as e:
        comp = {"error": str(e)[:100]}
    return {
        "anchors": anchors,
        "label": sat.get("label"),
        "saturation": sat.get("saturation"),
        "heaviest": sat.get("heaviest"),
        "competing_count": comp.get("count") if isinstance(comp, dict) else None,
        "raw_sat": sat, "raw_comp": comp,
    }


def measure_en(name: str) -> dict:
    """Lado caro: demanda EN. STRICTO = pasa outlier filter; LAXO = mediano standalone."""
    try:
        SCRAPE_COUNT["en_search"] += 1
        cands = search_viral_english(name, limit=EN_SEARCH_LIMIT)
    except Exception as e:
        return {"error_search": str(e)[:120]}
    try:
        SCRAPE_COUNT["en_outlier"] += len(cands)
        outliers = compute_outlier_filter(cands)
    except Exception as e:
        outliers = []
        outlier_err = str(e)[:120]
    else:
        outlier_err = None

    top = max(cands, key=lambda c: int(c.get("views") or 0), default=None)
    top_views = int(top.get("views") or 0) if top else 0
    best_outlier = max(outliers, key=lambda c: float(c.get("ratio") or 0), default=None) if outliers else None

    stricto = len(outliers) > 0
    laxo = top_views >= LAXO_FLOOR_VIEWS
    return {
        "n_cands": len(cands),
        "top_title": (top or {}).get("title"),
        "top_views": top_views,
        "n_outliers": len(outliers),
        "best_outlier_title": (best_outlier or {}).get("title") if best_outlier else None,
        "best_outlier_views": int((best_outlier or {}).get("views") or 0) if best_outlier else 0,
        "best_outlier_ratio": round(float((best_outlier or {}).get("ratio") or 0), 2) if best_outlier else 0,
        "best_outlier_median": int((best_outlier or {}).get("median") or 0) if best_outlier else 0,
        "passed_reason": (best_outlier or {}).get("passed_reason") if best_outlier else None,
        "VARA_ESTRICTO_pasa": stricto,
        "VARA_LAXO_pasa": laxo,
        "outlier_err": outlier_err,
    }


def main():
    LAB_OUT.mkdir(parents=True, exist_ok=True)
    print("LAB STAGE 3 — vara demanda EN por subtema. read-only, SÍ gasta scrape (proxy).")
    print(f"subtemas ({len(SUBTEMAS)}): {SUBTEMAS}")
    print(f"LAXO_FLOOR_VIEWS={LAXO_FLOOR_VIEWS:,} · EN_SEARCH_LIMIT={EN_SEARCH_LIMIT}")

    rows = []
    for i, name in enumerate(SUBTEMAS, 1):
        print(f"\n[{i}/{len(SUBTEMAS)}] {name}")
        print("  · ES (compuerta barata)...")
        es = measure_es(name)
        print(f"    ES label={es['label']} saturation={es['saturation']} competing={es['competing_count']}")
        print("  · EN (outlier — caro)...")
        en = measure_en(name)
        if "error_search" in en:
            print(f"    EN ERROR: {en['error_search']}")
        else:
            print(f"    EN cands={en['n_cands']} top_views={en['top_views']:,} "
                  f"('{(en['top_title'] or '')[:42]}')")
            print(f"    EN outliers={en['n_outliers']} "
                  f"best_ratio={en['best_outlier_ratio']} median={en['best_outlier_median']:,}")
            print(f"    → ESTRICTO={'PASA' if en['VARA_ESTRICTO_pasa'] else 'no'} "
                  f"· LAXO={'PASA' if en['VARA_LAXO_pasa'] else 'no'}")
        rows.append({"subtema": name, "es": es, "en": en})
        time.sleep(0.5)

    # ── resumen comparativo de varas ──
    print("\n" + "=" * 78)
    print("RESUMEN — comparación de varas EN (sobre subtemas YA limpios)")
    print("=" * 78)
    print(f"  {'SUBTEMA':<24} {'top_views':>10} {'outl':>5} {'ratio':>7}  {'ESTRICTO':<9} {'LAXO':<6} {'ES_label':<10}")
    for r in rows:
        en = r["en"]; es = r["es"]
        if "error_search" in en:
            print(f"  {r['subtema']:<24} {'ERROR':>10}")
            continue
        print(f"  {r['subtema']:<24} {en['top_views']:>10,} {en['n_outliers']:>5} "
              f"{en['best_outlier_ratio']:>7} "
              f"{'PASA' if en['VARA_ESTRICTO_pasa'] else 'no':<9} "
              f"{'PASA' if en['VARA_LAXO_pasa'] else 'no':<6} {str(es['label']):<10}")

    n_estricto = sum(1 for r in rows if r["en"].get("VARA_ESTRICTO_pasa"))
    n_laxo = sum(1 for r in rows if r["en"].get("VARA_LAXO_pasa"))
    print(f"\n  ESTRICTO deja pasar: {n_estricto}/{len(rows)}  ·  LAXO deja pasar: {n_laxo}/{len(rows)}")
    print(f"  COSTO scrape aprox: EN_search={SCRAPE_COUNT['en_search']} · "
          f"EN_outlier(get_channel)≈{SCRAPE_COUNT['en_outlier']} · "
          f"ES_sat={SCRAPE_COUNT['es_sat']} · ES_count={SCRAPE_COUNT['es_count']}")

    OUT.write_text(json.dumps({"config": {"LAXO_FLOOR_VIEWS": LAXO_FLOOR_VIEWS,
                                          "EN_SEARCH_LIMIT": EN_SEARCH_LIMIT},
                               "scrape_count": SCRAPE_COUNT, "rows": rows},
                              indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nGuardado: {OUT}")


if __name__ == "__main__":
    main()
