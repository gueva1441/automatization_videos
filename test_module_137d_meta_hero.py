"""
test_module_137d_meta_hero.py — HANDOFF_137d (offline, lint + smoke de firmas, sin red).

Verifica el form de miniaturas 137d:
- _META_SYSTEM: 6 títulos/overlays anclados a VERIFIED FACTS, ≤70, REGLA DE ORO; sin la
  forma vieja "3 candidatos, ≤90".
- _HERO_SYSTEM: TRES CONCEPTOS.
- Schemas: titulos/overlays maxItems 6; hero concepts maxItems 3.
- Plumbing del tamaño: compose_thumbnail / compose_and_package aceptan size_factor.

USO:
    python test_module_137d_meta_hero.py
"""
import inspect
import sys

import script_engine.m09_packaging as pkg


def _check(cond: bool, msg: str, fails: list) -> None:
    if not cond:
        fails.append(msg)


def main() -> int:
    fails: list[str] = []
    ms = pkg._META_SYSTEM
    for tok in ["6 candidatos", "VERIFIED FACTS", "≤70", "REGLA DE ORO"]:
        _check(tok in ms, f"137d _META_SYSTEM falta {tok!r}", fails)
    _check("3 candidatos, ≤90" not in ms,
           "137d _META_SYSTEM TODAVÍA tiene la forma vieja '3 candidatos, ≤90'", fails)

    _check("TRES CONCEPTOS" in pkg._HERO_SYSTEM, "137d _HERO_SYSTEM falta 'TRES CONCEPTOS'", fails)

    # schemas
    props = pkg._META_SCHEMA["properties"]
    _check(props["titulos"]["maxItems"] == 6, "schema titulos maxItems != 6", fails)
    _check(props["overlays"]["maxItems"] == 6, "schema overlays maxItems != 6", fails)
    _check(pkg._HERO_SCHEMA["properties"]["concepts"]["maxItems"] == 3,
           "hero schema concepts maxItems != 3", fails)

    # plumbing del tamaño del overlay (§3.c)
    _check("size_factor" in inspect.signature(pkg.compose_thumbnail).parameters,
           "compose_thumbnail sin parámetro size_factor", fails)
    _check("size_factor" in inspect.signature(pkg.compose_and_package).parameters,
           "compose_and_package sin parámetro size_factor", fails)

    if fails:
        print(f"[FAIL] {len(fails)} assert(s):")
        for f in fails:
            print(f"   ✗ {f}")
        return 1
    print("[PASS] 137d: 6 títulos/overlays anclados + TRES CONCEPTOS + size_factor cableado")
    return 0


if __name__ == "__main__":
    sys.exit(main())
