"""
test_subtopic_measurer.py — C2: valida script_engine.subtopic_measurer sobre los subtemas
limpios de #15/#17, reproduciendo el cierre del lab:
  - Mary Celeste / USS Cyclops / Wilhelm Gustloff / Marine Sulphur Queen → PASA (LAXO, sin outlier).
  - Doña Paz → CORTADO_ES (gateado por ES SATURADO antes de pagar EN).
  - Azores Plateau Monolith → relevancia descarta el fantasma (Antártida) del top.
Gasta scrape mínimo (ES + EN search por subtema; sin get_channel).

Correr:  python -X utf8 test_subtopic_measurer.py
"""
from __future__ import annotations

import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from script_engine.subtopic_measurer import measure, LAXO_FLOOR_VIEWS

GOOD = ["Mary Celeste", "USS Cyclops", "Wilhelm Gustloff", "Marine Sulphur Queen"]
ES_GATED = "Doña Paz"
CONTAM = "Azores Plateau Monolith"


def main():
    print(f"C2 — subtopic_measurer (LAXO_FLOOR_VIEWS={LAXO_FLOOR_VIEWS:,})\n")
    results = {}
    for name in GOOD + [ES_GATED, CONTAM]:
        r = measure(name)
        results[name] = r
        en = r.get("en") or {}
        extra = ""
        if r["verdict"] == "CORTADO_ES":
            extra = f"ES sat={r['es'].get('saturation')}"
        elif en:
            extra = (f"top_rel={en.get('top_rel_views'):,} ('{(en.get('top_rel_title') or '')[:36]}') "
                     f"raw={en.get('top_raw_views'):,}")
        print(f"  {name:<24} {r['verdict']:<12} {extra}")

    # asserts estructurales
    good_pass = sum(1 for n in GOOD if results[n]["verdict"] == "PASA")
    dp = results[ES_GATED]["verdict"] == "CORTADO_ES"
    # relevancia: el top relevante de Azores NO es el de Antártida
    az = results[CONTAM].get("en") or {}
    az_rel_title = (az.get("top_rel_title") or "").lower()
    az_raw_title = (az.get("top_raw_title") or "").lower()
    relevance_worked = ("antarctic" not in az_rel_title) and (az.get("top_rel_views", 0) != az.get("top_raw_views", -1) or "antarctic" not in az_raw_title)

    print(f"\n  GOOD que pasan LAXO: {good_pass}/{len(GOOD)} (esperado {len(GOOD)})")
    print(f"  Doña Paz CORTADO_ES: {'sí' if dp else 'NO'}")
    print(f"  Relevancia mató el fantasma Antártida en Azores: {'sí' if relevance_worked else 'NO/revisar'}")
    ok = good_pass == len(GOOD) and dp and relevance_worked
    print(f"\nC2 measurer: {'PASS' if ok else 'REVISAR'}")


if __name__ == "__main__":
    main()
