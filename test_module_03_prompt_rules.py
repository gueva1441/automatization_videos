"""test_module_03_prompt_rules.py — valida OFFLINE las reglas afiladas
(#232/#235 chat 32). NO llama Flash."""
from script_engine.m03_visual import SYSTEM_INSTRUCTION_VISUAL, _build_rules_block

SI = SYSTEM_INSTRUCTION_VISUAL
RB = _build_rules_block()


def test_regla5_calma_antes():
    assert "CALM BEFORE" in SI, "#232: falta pivote calma-antes en regla 5"
    assert "animals" in SI.lower() and "mass casualties" in SI.lower()


def test_regla7_pantallas():
    low = SI.lower()
    assert "data projection" in low or "data projections" in low
    assert "abstract glowing" in low, "#235: falta guia de pantallas abstractas"


def test_regla4_moderno_tangible():
    assert "holographic" in SI.lower(), "#235: falta prohibicion holograms"
    assert "2010s-2020s" in SI or "present-day" in SI.lower()


def test_rules_block_sin_negativo_instruido():
    # La REGLA DE ORO ya NO debe instruir "terminar con 'no readable text'"
    assert 'debe terminar con "no readable text"' not in RB, "regla 3 aun instruye el negativo"
    assert "Flux/Veo IGNORAN los negativos" in RB, "falta nota AP2"


def test_rules_block_docstring():
    assert "SOLO las inyecta" in _build_rules_block.__doc__ if _build_rules_block.__doc__ else False


if __name__ == "__main__":
    import sys
    fns = [v for k, v in sorted(globals().items())
           if k.startswith("test_") and callable(v)]
    fails = 0
    for fn in fns:
        try:
            fn(); print(f"  OK  {fn.__name__}")
        except AssertionError as e:
            fails += 1; print(f"  XX  {fn.__name__}: {e}")
    print(f"\n{'PASS' if not fails else 'FAIL'} - {len(fns)-fails}/{len(fns)}")
    sys.exit(1 if fails else 0)
