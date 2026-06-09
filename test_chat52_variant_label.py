"""
test_chat52_variant_label.py — BLOQUE 4: en variantes (n>1), título y label del MISMO tema.

BUG: el gate agrupa variantes del mismo evento y decide sobre la MÁS saturada (worst), pero el seed
persistía el TÍTULO de la variante más vista (rep) con el es_gap de worst (OTRA variante). El humano
veía un label que no era de la query del título.

FIX (sin cambiar la decisión conservadora del gate):
  - _event_seed_inputs(variants) → (rep_item, rep_sat, worst_sat). rep = más views (titula → su
    es_gap se persiste); worst = más saturado (el gate decide sobre ESA).
  - _atomic_es_gap(rep_sat, worst_sat, n) → es_gap con campos PRINCIPALES del rep + worst_variant_*.

Determinista, SIN red. Correr:  python -X utf8 test_chat52_variant_label.py
"""
from __future__ import annotations

import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from niche_discoverer import _event_seed_inputs, _atomic_es_gap

_fails: list[str] = []


def check(cond: bool, msg: str):
    print(("  ✓ " if cond else "  ✗ ") + msg)
    if not cond:
        _fails.append(msg)


def _sat(label, saturation, ontopic=1):
    """Fabrica un dict-sat tipo _measure_es (los campos que el es_gap consume)."""
    return {"label": label, "saturation": saturation, "heaviest": {"title": label},
            "ontopic_count": ontopic, "anchors_used": [label], "source": "scrapetube+juez"}


def test_seleccion_rep_vs_worst():
    print("\n[B4] _event_seed_inputs: rep = más views, worst = más saturado (variantes distintas)")
    # variante A: MÁS VISTA pero HUECO (poca competencia ES). variante B: menos vista pero SATURADA.
    var_rep = ({"spanish_topic": "Tema A (titula)", "views": 900_000}, None, _sat("HUECO", 10_000))
    var_worst = ({"spanish_topic": "Tema B", "views": 100_000}, None, _sat("SATURADO", 300_000))
    variants = [var_rep, var_worst]

    rep_item, rep_sat, worst_sat = _event_seed_inputs(variants)
    check(rep_item["spanish_topic"] == "Tema A (titula)", "rep = la variante con MÁS views")
    check(rep_sat["label"] == "HUECO", "rep_sat = el es_gap del más-visto (HUECO)")
    check(worst_sat["label"] == "SATURADO", "worst_sat = la variante MÁS saturada (SATURADO)")


def test_es_gap_no_mezcla():
    print("\n[B4] _atomic_es_gap: principal = rep; worst_variant_* = worst (no se mezclan)")
    rep_sat = _sat("HUECO", 10_000, ontopic=2)
    worst_sat = _sat("SATURADO", 300_000)
    es_gap = _atomic_es_gap(rep_sat, worst_sat, n=2)
    check(es_gap["label"] == "HUECO", "es_gap.label = rep (el del título)")
    check(es_gap["saturation"] == 10_000, "es_gap.saturation = rep")
    check(es_gap["ontopic_count"] == 2, "es_gap.ontopic_count = rep")
    check(es_gap["worst_variant_label"] == "SATURADO", "worst_variant_label = worst (señal preservada)")
    check(es_gap["worst_variant_saturation"] == 300_000, "worst_variant_saturation = worst")
    check(es_gap["variants_grouped"] == 2, "variants_grouped = n")


def test_gate_sigue_conservador():
    print("\n[B4] el gate sigue decidiendo sobre worst (descarta si el PEOR es SATURADO)")
    # rep HUECO pero worst SATURADO → la condición del gate (worst_sat['label']=='SATURADO') es True.
    _, rep_sat, worst_sat = _event_seed_inputs([
        ({"spanish_topic": "rep", "views": 500_000}, None, _sat("HUECO", 5_000)),
        ({"spanish_topic": "worst", "views": 10_000}, None, _sat("SATURADO", 200_000)),
    ])
    check(worst_sat["label"] == "SATURADO", "el gate vería SATURADO (descarta) aunque el rep sea HUECO")
    check(rep_sat["label"] == "HUECO", "rep sigue siendo HUECO (no contamina la decisión)")


def test_n1_degenera():
    print("\n[B4] n==1: rep y worst son la misma variante (sin worst_variant divergente)")
    only = ({"spanish_topic": "solo", "views": 42}, None, _sat("DISPUTADO", 80_000))
    rep_item, rep_sat, worst_sat = _event_seed_inputs([only])
    check(rep_sat is worst_sat or rep_sat["label"] == worst_sat["label"], "rep == worst con 1 variante")
    es_gap = _atomic_es_gap(rep_sat, worst_sat, n=1)
    check(es_gap["label"] == es_gap["worst_variant_label"] == "DISPUTADO",
          "label principal == worst_variant_label con n==1")


if __name__ == "__main__":
    test_seleccion_rep_vs_worst()
    test_es_gap_no_mezcla()
    test_gate_sigue_conservador()
    test_n1_degenera()

    print("\n" + ("=" * 60))
    if _fails:
        print(f"FALLOS: {len(_fails)}")
        for f in _fails:
            print(f"  - {f}")
        sys.exit(1)
    print("TODO OK")
