"""test_chat33_pausas_conjy.py — valida OFFLINE que se quitaron las pausas '...'
de m01b y la regla conjunction_y de m02_5. NO llama a Flash. NO gasta."""
from script_engine.m02_5_normalizer_gate import _build_system_instruction


def test_normalizer_sin_conjunction_y():
    si = _build_system_instruction({}, set())
    assert "CONJUNCTION_Y" not in si, "todavia esta la regla CONJUNCTION_Y"
    assert "conjunction_y" not in si, "todavia esta la mencion conjunction_y"
    assert "reemplazar \"Y\" por \"I\"" not in si, "todavia esta la instruccion Y->I"


def test_normalizer_conserva_otras_reglas():
    # No rompimos las reglas vecinas.
    si = _build_system_instruction({}, set())
    assert "YEAR_FORMAT" in si, "se rompio la regla 7 year_format"
    assert "PUNCTUATION_ARTIFACT" in si, "se rompio la regla 6"
    # La excepcion de '...' en punctuation_artifact sigue (NO marcar '...').
    assert "INTENCIONALES" in si, "se borro la excepcion de '...' del normalizer"


if __name__ == "__main__":
    import sys
    fns = [v for k, v in sorted(globals().items())
           if k.startswith("test_") and callable(v)]
    fails = 0
    for fn in fns:
        try:
            fn()
            print(f"  OK  {fn.__name__}")
        except AssertionError as e:
            fails += 1
            print(f"  XX  {fn.__name__}: {e}")
    print(f"\n{'PASS' if not fails else 'FAIL'} - {len(fns)-fails}/{len(fns)}")
    sys.exit(1 if fails else 0)
