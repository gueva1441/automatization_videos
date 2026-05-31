"""test_chat33_pausas_conjy.py — valida OFFLINE que se quitaron las pausas '...'
de m01b y la regla conjunction_y de m02_5. NO llama a Flash. NO gasta."""
from script_engine.m01b_narrator import TONE_INSTRUCTIONS_BY_INTENT, PROSE_RULES
from script_engine.m02_5_normalizer_gate import _build_system_instruction


def test_tone_instructions_sin_pausas():
    for intent, txt in TONE_INSTRUCTIONS_BY_INTENT.items():
        assert "..." not in txt, f"{intent}: todavia tiene '...'"
        # OJO (chat33): se chequea el marcador de INSTRUCCION "PAUSAS:" (con dos
        # puntos), NO el substring "PAUSA" — porque "Pacing pausado" (tono legit
        # de resolution) contiene "PAUSA" en mayusculas y daba falso positivo.
        assert "PAUSAS:" not in txt, f"{intent}: todavia tiene instruccion PAUSAS:"


def test_tone_instructions_conservan_tono():
    # No deben quedar vacios: el tono se conserva.
    assert "Densidad alta" in TONE_INSTRUCTIONS_BY_INTENT["hook"]
    assert "Pacing calmo" in TONE_INSTRUCTIONS_BY_INTENT["setup"]
    assert "Foreshadowing" in TONE_INSTRUCTIONS_BY_INTENT["rising_tension"]
    # Los 7 intents siguen presentes.
    assert len(TONE_INSTRUCTIONS_BY_INTENT) == 7


def test_prose_rules_sin_regla_pausas():
    # OJO (chat33): NO se chequea `"..." not in PROSE_RULES` — la regla 5 tiene
    # ejemplos de aperturas prohibidas ("Hoy les voy a contar...") con "..."
    # literales que NO son instruccion de pausa. Se valida en cambio que la
    # regla 8 (PAUSAS DRAMATICAS / marca de pausa) ya no exista.
    assert "PAUSAS DRAMATICAS" not in PROSE_RULES.upper().replace("Á", "A")
    assert "marca de pausa" not in PROSE_RULES, "todavia esta la regla 8 de pausas"
    assert "\n8." not in PROSE_RULES, "PROSE_RULES todavia tiene una regla 8"
    # La regla 7 (tags [F##]) sigue ahi: no rompimos las otras reglas.
    assert "[F##]" in PROSE_RULES or "F\\d+" in PROSE_RULES


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
