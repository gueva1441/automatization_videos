"""test_chat33_hhmm.py — valida OFFLINE que el normalizer ahora detecta HH:MM.
NO llama a Flash. NO gasta."""
from script_engine.m02_5_normalizer_gate import (
    _build_system_instruction, VALID_LLM_CATEGORIES, _CATEGORIES_NEVER_RECURRING,
)


def test_hhmm_ya_no_esta_en_maneja_bien():
    si = _build_system_instruction({}, set())
    # La afirmacion falsa "Horas HH:MM: 14:30" ya no debe estar en la lista
    # de cosas que ElevenLabs maneja bien.
    assert "Horas HH:MM" not in si, "todavia dice que HH:MM se maneja bien"
    assert "catorce treinta" not in si, "todavia esta el ejemplo enganoso 14:30"


def test_regla_time_format_hm_presente():
    si = _build_system_instruction({}, set())
    assert "TIME_FORMAT_HM" in si, "falta la regla nueva TIME_FORMAT_HM"
    assert "veintiunoceocero" in si, "falta la descripcion del sintoma real"
    assert "las veintiuna" in si, "falta el ejemplo de conversion"


def test_header_dice_8_casos():
    si = _build_system_instruction({}, set())
    assert "los 8 casos" in si, "el header no se actualizo a 8 casos"
    assert "los 7 casos" not in si, "el header todavia dice 7 casos"


def test_categoria_en_validas():
    assert "time_format_hm" in VALID_LLM_CATEGORIES


def test_categoria_es_never_recurring():
    assert "time_format_hm" in _CATEGORIES_NEVER_RECURRING


def test_conjunction_y_limpiada_de_categorias():
    # Aprovechamos para confirmar que la referencia muerta se fue.
    assert "conjunction_y" not in VALID_LLM_CATEGORIES


def test_no_rompimos_reglas_vecinas():
    si = _build_system_instruction({}, set())
    assert "YEAR_FORMAT" in si, "se rompio year_format"
    assert "PUNCTUATION_ARTIFACT" in si, "se rompio punctuation_artifact"
    assert "INTENCIONALES" in si, "se borro la excepcion de '...'"
    # El TIME_FORMAT viejo (HH:MM:SS con segundos) sigue presente y distinto.
    assert "HH:MM:SS" in si, "se rompio el time_format con segundos"


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
