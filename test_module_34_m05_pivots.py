"""
test_module_34_m05_pivots.py — Valida que m05_PROMPT_v1.txt incorpora las dos
reglas de patrones intencionales (P1 muerte->calma, P2 expected_era no
absoluta) sin romper el loader ni borrar contenido existente.

OFFLINE. NO llama a Flash. Cero gasto de API. Correr desde la raiz del proyecto.
"""
import sys


def _assert(cond, msg):
    status = "PASS" if cond else "FAIL"
    print(f"  [{status}] {msg}")
    if not cond:
        _assert.failed += 1
_assert.failed = 0


def main():
    # 1. El modulo importa y el loader corre sin RuntimeError
    from script_engine.m05_judge import SYSTEM_PROMPT_FIXED, VALID_CATEGORIES

    # 2. Loader intacto: arranca como siempre
    _assert(SYSTEM_PROMPT_FIXED.startswith("You are"),
            "SYSTEM_PROMPT_FIXED sigue arrancando con 'You are'")

    # 3. El bloque nuevo esta presente
    _assert("INTENTIONAL PATTERNS" in SYSTEM_PROMPT_FIXED,
            "bloque INTENTIONAL PATTERNS presente")

    # 4. P1 (muerte->calma) presente con su par acotado
    _assert("calm-before pivot" in SYSTEM_PROMPT_FIXED,
            "P1 muerte->calma presente")
    _assert("Do NOT flag anchor_mismatch when the calm image" in SYSTEM_PROMPT_FIXED,
            "P1 tiene la clausula 'Do NOT flag' acotada")
    _assert("DO still flag anchor_mismatch if the image shows an unrelated" in SYSTEM_PROMPT_FIXED,
            "P1 conserva el guardrail 'DO still flag' (no es escapatoria amplia)")

    # 5. P2 (expected_era) presente con su par acotado
    _assert("expected_era is dominant" in SYSTEM_PROMPT_FIXED,
            "P2 expected_era presente")
    _assert("Do NOT flag era_mismatch_anchor when the prompt's era matches" in SYSTEM_PROMPT_FIXED,
            "P2 tiene la clausula 'Do NOT flag' acotada")
    _assert("DO still flag era_mismatch_anchor if the prompt's era contradicts" in SYSTEM_PROMPT_FIXED,
            "P2 conserva el guardrail 'DO still flag'")

    # 6. NO se borro nada: las 8 categorias originales siguen
    for cat in ("name_leakage", "text_in_image", "era_mismatch_anchor",
                "era_textual_in_canon", "anchor_mismatch", "anachronism_visual",
                "narration_unvisualizable"):
        _assert(cat in SYSTEM_PROMPT_FIXED, f"categoria '{cat}' sigue en el prompt")
    _assert("NON-NEGOTIABLE RULES" in SYSTEM_PROMPT_FIXED,
            "seccion NON-NEGOTIABLE RULES sigue presente")
    _assert("OUTPUT SCHEMA" in SYSTEM_PROMPT_FIXED,
            "seccion OUTPUT SCHEMA sigue presente")

    # 7. El bloque nuevo esta ANTES de NON-NEGOTIABLE RULES (compuerta previa)
    _assert(SYSTEM_PROMPT_FIXED.index("INTENTIONAL PATTERNS")
            < SYSTEM_PROMPT_FIXED.index("NON-NEGOTIABLE RULES"),
            "bloque nuevo posicionado ANTES de NON-NEGOTIABLE RULES")

    # 8. NO se toco el enum de categorias
    _assert("acronym_leak" in VALID_CATEGORIES and "commercial_brand_leak" in VALID_CATEGORIES,
            "VALID_CATEGORIES intacto (no se agrego/quito categoria)")

    print()
    if _assert.failed == 0:
        print("RESULTADO: PASS (todos los asserts OK)")
        sys.exit(0)
    print(f"RESULTADO: FAIL ({_assert.failed} asserts fallaron)")
    sys.exit(1)


if __name__ == "__main__":
    main()
