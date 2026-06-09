"""
test_chat52_decay_none.py — BLOQUE 1: months=None deja de desinflar 10× al competidor pesado.

BUG (auditoría Cowork): _es_age_decay(None) devolvía ES_DECAY_FLOOR=0.1 (trataba fecha desconocida
como >5 años). scrapetube falla la fecha JUSTO en los evergreen grandes → eff = views×0.1 / 10 →
como el gate solo descarta SATURADO, un SATURADO real se disfrazaba de DISPUTADO y sobrevivía
(Centralia 652k, Ashgabat 404k, Plymouth 308k).

FIX (surgical, solo la rama None): None → ES_DECAY_UNKNOWN=0.6 (decay neutro). El floor de >60m
NO se toca. Revierte la decisión T5 con evidencia.

Determinista, SIN red. Correr:  python -X utf8 test_chat52_decay_none.py
"""
from __future__ import annotations

import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from script_engine.youtube_scanner import (
    _es_age_decay, _es_saturation_label, ES_DECAY_UNKNOWN, ES_DECAY_FLOOR,
)

_fails: list[str] = []


def check(cond: bool, msg: str):
    print(("  ✓ " if cond else "  ✗ ") + msg)
    if not cond:
        _fails.append(msg)


def test_decay_table():
    print("\n[B1] _es_age_decay: None neutro, tiers y floor intactos")
    d_none = _es_age_decay(None)
    check(d_none == 0.6 and d_none == ES_DECAY_UNKNOWN,
          f"_es_age_decay(None) → 0.6 (ES_DECAY_UNKNOWN), no 0.1; obtuvo {d_none}")
    check(_es_age_decay(6) == 1.0, f"_es_age_decay(6) → 1.0 (≤12m intacto); obtuvo {_es_age_decay(6)}")
    check(_es_age_decay(24) == 0.6, f"_es_age_decay(24) → 0.6 (≤36m intacto); obtuvo {_es_age_decay(24)}")
    check(_es_age_decay(80) == 0.1 and _es_age_decay(80) == ES_DECAY_FLOOR,
          f"_es_age_decay(80) → 0.1 (floor de viejo INTACTO); obtuvo {_es_age_decay(80)}")


def test_label_flip():
    print("\n[B1] caso sintético: competidor pesado con fecha None ya NO se disfraza")
    views = 400_000
    # ANTES: eff = 400k × 0.1 = 40k → DISPUTADO (< 150k) → sobrevivía el gate.
    eff_old = views * 0.1
    # AHORA: eff = 400k × 0.6 = 240k → SATURADO (≥ 150k) → se descarta.
    eff_new = views * _es_age_decay(None)
    print(f"     400k views, months=None: eff_old={eff_old:,.0f} → {_es_saturation_label(eff_old)} | "
          f"eff_new={eff_new:,.0f} → {_es_saturation_label(eff_new)}")
    check(_es_saturation_label(eff_old) == "DISPUTADO",
          f"viejo: 400k×0.1=40k → DISPUTADO (disfrazado); obtuvo {_es_saturation_label(eff_old)}")
    check(_es_saturation_label(eff_new) == "SATURADO",
          f"nuevo: 400k×0.6=240k → SATURADO (descarta); obtuvo {_es_saturation_label(eff_new)}")


if __name__ == "__main__":
    test_decay_table()
    test_label_flip()

    print("\n" + ("=" * 60))
    if _fails:
        print(f"FALLOS: {len(_fails)}")
        for f in _fails:
            print(f"  - {f}")
        sys.exit(1)
    print("TODO OK")
