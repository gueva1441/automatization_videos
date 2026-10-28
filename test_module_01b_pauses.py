"""test_module_01b_pauses.py — valida OFFLINE (sin Flash) que las pausas
quedaron cableadas en m01b + que el normalizer no las marcará. Chat 32 #228a."""
import re

# Imports ajustados al layout real (BLOQUE 0):
#   - m01b vive en script_engine/
#   - m02_5 vive en script_engine/   (no en raíz)
#   - tts_normalizer vive en raíz
from script_engine.m01b_narrator import _first_sentence   # F41: los prompts del narrador viejo se borraron
from script_engine.m02_5_normalizer_gate import _build_system_instruction
from tts_normalizer import normalize_for_tts


def test_first_sentence_ignora_pausa_inicial():
    assert _first_sentence("... 99 marinos. Sin SOS.") == "99 marinos."
    assert _first_sentence("Hola mundo. Otra frase.") == "Hola mundo."


def test_normalizer_no_marca_pausas():
    si = _build_system_instruction({}, set())
    assert "..." in si and "INTENCIONALES" in si, "falta excepcion de pausas"


def test_tts_normalizer_preserva_pausas():
    assert "..." in normalize_for_tts("El lago ... despertó de noche.")


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
