"""
_dry_run_modeA_chat42.py — GATE 4 (chat 42). Corre el Mode A INTEGRADO en dry-run:
puertas fijas → search (sin filtro abs) → compute_outlier_filter → tabla. NO traduce
con Gemini, NO chequea competencia ES, NO escribe seeds/topics_db. Solo lectura+scraping.

USO:
    python -X utf8 _dry_run_modeA_chat42.py
"""
from __future__ import annotations

import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import niche_discoverer as n  # noqa: E402

if __name__ == "__main__":
    niches = sys.argv[1:] or ["espacio", "oceano"]
    print(f"DRY-RUN Mode A integrado — nichos: {niches}")
    passed = n._run_spy_arbitrage(niches, dry_run=True)
    print(f"\nFIN DRY-RUN: {len(passed)} candidatos pasaron el filtro EN "
          f"(NO se persistió nada, NO se llamó a Gemini, NO topics_db).")
