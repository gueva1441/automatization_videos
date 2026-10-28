"""
test_module_03_leakage_retry.py — HANDOFF_134 (offline, sin API).

Queda la yapa del rótulo FAIL honesto:
  5. _derive_failed_step('m01a', [...m07]) == 'm03' (no el mentiroso).
(1–4 —REGLA 3 con retry+feedback sobre el fluidificador y backstop scrub— se borraron en F50 con el
fluidificador; el backstop de texto legible ahora saca la frase en m03 sin re-tejido.)

USO:
    python test_module_03_leakage_retry.py
"""
import sys

import fase1_5


def main() -> int:
    fails: list[str] = []

    # ── (5) yapa: paso REAL, no from_step ──
    fs = fase1_5._derive_failed_step("m01a", ["m01a", "m01b", "normalizer_gate", "audio", "m07"])
    if fs != "m03":
        fails.append(f"(5) yapa: esperaba 'm03', dio {fs!r}")
    if fase1_5._derive_failed_step("m01a", ["m01a", "m01b", "normalizer_gate", "audio",
                                            "m07", "m03", "assemble"]) is not None:
        fails.append("(5) yapa: todo completo debería dar None (rótulo honesto)")

    if fails:
        print(f"[FAIL] {len(fails)} assert(s):")
        for f in fails:
            print(f"   ✗ {f}")
        return 1
    print("[PASS] yapa del rótulo honesto")
    return 0


if __name__ == "__main__":
    sys.exit(main())
