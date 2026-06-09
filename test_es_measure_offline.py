"""
test_es_measure_offline.py — valida la LÓGICA del nuevo _measure_es SIN red ni Gemini
(mockea translate_to_es / list_spanish_candidates / filter_relevant). Cubre:
  - saturación = max(views * _es_age_decay(months)) sobre relevantes, label por umbrales reusados,
  - VACIO cuando no hay relevantes (y el juez NO se llama si la lista cruda viene vacía),
  - ERROR cuando el scrape cae del todo (None) o el juez de relevancia lanza,
  - fallback a la grafía EN cuando la traducción lanza.

La tabla de regresión con datos REALES la da test_es_saturation_judge.py (live).

Correr:  python -X utf8 test_es_measure_offline.py
"""
from __future__ import annotations

import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import script_engine.subtopic_measurer as m

CALLS = {"filter": 0}


def _patch(translate, listfn, filterfn):
    m.translate_to_es = translate
    m.list_spanish_candidates = listfn
    def _f(entity, cands, aliases=None):
        CALLS["filter"] += 1
        return filterfn(entity, cands, aliases=aliases)
    m.filter_relevant = _f


def run():
    failures = []

    def check(cond, msg):
        print(f"  [{'✓' if cond else '✗'}] {msg}")
        if not cond:
            failures.append(msg)

    print("Offline — lógica de _measure_es (Diseño B)\n")

    # 1. Chernobyl-shaped: traduce a Chernóbil, lista trae competidor 12M reciente, juez lo da relevante
    CALLS["filter"] = 0
    cands = [
        {"title": "¿QUIÉN fue el CULPABLE? | Chernóbil | Documental", "views": 12_457_285, "months": 6},
        {"title": "Receta de cocina rusa", "views": 9_000_000, "months": 3},   # ruido, el juez lo descarta
    ]
    _patch(lambda n: {"es_query": "Chernóbil", "es_aliases": ["Chernobyl"]},
           lambda q, limit=50: cands,
           lambda e, c, aliases=None: [c[0]])   # solo el relevante
    r = m._measure_es("Chernobyl")
    check(r["label"] == "SATURADO", f"Chernobyl → SATURADO (era VACIO bug) [{r['label']}]")
    check(r["es_query"] == "Chernóbil", "es_query traducido a 'Chernóbil'")
    check(r["saturation"] == 12_457_285, f"saturación = eff del relevante más pesado [{r['saturation']:,}]")
    check(r["ontopic_count"] == 1, "ontopic_count = relevantes (1, el ruido excluido)")
    check(r["source"] == "scrapetube+juez", "source marca el camino nuevo")

    # 2. lista cruda vacía → VACIO y el juez NO se llama
    CALLS["filter"] = 0
    _patch(lambda n: {"es_query": n, "es_aliases": []},
           lambda q, limit=50: [],
           lambda e, c, aliases=None: c)
    r = m._measure_es("Fukushima Daiichi")
    check(r["label"] == "VACIO" and r["saturation"] == 0, "lista cruda vacía → VACIO")
    check(CALLS["filter"] == 0, "juez NO se llama si no hay candidatos (no gasta Gemini)")

    # 3. scrape total caído (None) → ERROR
    _patch(lambda n: {"es_query": n, "es_aliases": []},
           lambda q, limit=50: None,
           lambda e, c, aliases=None: c)
    r = m._measure_es("X")
    check(r["label"] == "ERROR", "list_spanish_candidates None (scrape caído) → ERROR")

    # 4. juez de relevancia lanza → ERROR (no fabrica dato)
    def _boom(e, c, aliases=None): raise RuntimeError("gemini down")
    _patch(lambda n: {"es_query": n, "es_aliases": []},
           lambda q, limit=50: [{"title": "algo", "views": 100, "months": 1}],
           _boom)
    r = m._measure_es("Y")
    check(r["label"] == "ERROR", "juez relevancia lanza → ERROR")

    # 5. traducción lanza → fallback a grafía EN, flujo sigue
    def _t_boom(n): raise RuntimeError("translate down")
    _patch(_t_boom,
           lambda q, limit=50: [{"title": "Pripyat ghost town", "views": 5_000, "months": 6}],
           lambda e, c, aliases=None: c)
    r = m._measure_es("Pripyat")
    check(r["es_query"] == "Pripyat", "traducción falla → es_query = grafía EN (no rompe)")
    check(r["label"] == "HUECO", f"5k views, decay 1.0 → HUECO [{r['label']}]")

    # 6. matemática del decay: months=None → floor 0.1
    _patch(lambda n: {"es_query": n, "es_aliases": []},
           lambda q, limit=50: [{"title": "viejo sin fecha", "views": 1_000_000, "months": None}],
           lambda e, c, aliases=None: c)
    r = m._measure_es("Z")
    check(abs(r["saturation"] - 100_000.0) < 1, f"months=None → decay floor 0.1 → eff 100k [{r['saturation']:,}]")
    check(r["label"] == "DISPUTADO", f"eff 100k → DISPUTADO (<150k) [{r['label']}]")

    print("\n" + ("✅ TODOS OK" if not failures else f"❌ {len(failures)} FALLO(S): " + "; ".join(failures)))
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(run())
