"""
test_t5_sentinel.py — valida T5 (eliminar sentinel 999 de fechas) SIN red.

Verifica:
  1. _parse_date_scrapetube_months_ago devuelve None (no 999) cuando no parsea.
  2. _es_age_decay(None) == ES_DECAY_FLOOR  → la saturación ES NO cambia (equivale al viejo 999).
  3. el prompt del juez muestra "desconocida" + instrucción de NO penalizar cuando la edad es
     None/ausente, y "N meses" cuando es int. (Sin "None meses".)

Correr:  python -X utf8 test_t5_sentinel.py
"""
from __future__ import annotations

import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from script_engine.youtube_scanner import (
    _parse_date_scrapetube_months_ago as parse,
    _es_age_decay, ES_DECAY_FLOOR,
)
from script_engine.m_judge_seeds import _build_judge_prompt


def run():
    failures = []

    def check(cond, msg):
        print(f"  [{'✓' if cond else '✗'}] {msg}")
        if not cond:
            failures.append(msg)

    print("T5.1 — parser de fecha: válidos intactos, no-parseable → None\n")
    check(parse("hace 2 meses") == 2, "'hace 2 meses' → 2")
    check(parse("hace 1 año") == 12, "'hace 1 año' → 12")
    check(parse("hace 3 días") == 0, "'hace 3 días' → 0")
    check(parse("hace 5 horas") == 0, "'hace 5 horas' → 0")
    check(parse("") is None, "'' → None (antes 999)")
    check(parse("hace mucho tiempo") is None, "'hace mucho tiempo' (sin dígito) → None")
    check(parse("2024") is None, "'2024' (dígito sin unidad) → None")

    print("\nT5.2 — decay ES: None se comporta IGUAL que el viejo 999 (saturación intacta)\n")
    check(_es_age_decay(None) == ES_DECAY_FLOOR, f"_es_age_decay(None) == floor ({ES_DECAY_FLOOR})")
    check(_es_age_decay(5) == 1.0, "_es_age_decay(5) == 1.0 (≤12m)")
    check(_es_age_decay(50) == 0.3, "_es_age_decay(50) == 0.3 (≤60m)")
    check(_es_age_decay(100) == ES_DECAY_FLOOR, "_es_age_decay(100) == floor (>60m)")

    print("\nT5.3 — prompt del juez: 'desconocida' + no-penalizar cuando edad es None/ausente\n")

    seed_none = {"seed_title": "X", "evidence": {"en_viral": {"en_age_months": None}, "es_gap": {}}}
    p = _build_judge_prompt(seed_none)
    check("edad del viral: desconocida" in p, "en_age_months=None → 'edad del viral: desconocida'")
    check("None meses" not in p, "NO aparece 'None meses' (el bug que arregla T5)")
    check("NO la uses" in p, "instrucción explícita de NO penalizar por fecha desconocida")

    seed_fanout = {"seed_title": "Chernobyl", "evidence": {"en_viral": {}, "es_gap": {}}}  # sin la key
    p2 = _build_judge_prompt(seed_fanout)
    check("edad del viral: desconocida" in p2, "subtema fan-out (sin en_age_months) → 'desconocida'")

    seed_int = {"seed_title": "Y", "evidence": {"en_viral": {"en_age_months": 36}, "es_gap": {}}}
    p3 = _build_judge_prompt(seed_int)
    check("edad del viral: 36 meses" in p3, "en_age_months=36 → 'edad del viral: 36 meses'")

    print("\n" + ("✅ TODOS OK" if not failures else f"❌ {len(failures)} FALLO(S): " + "; ".join(failures)))
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(run())
