"""test_module_01b_pauses.py — valida OFFLINE (sin Flash) que las pausas
quedaron cableadas en m01b + que el normalizer no las marcará. Chat 32 #228a."""
import re

# Imports ajustados al layout real (BLOQUE 0):
#   - m01b vive en script_engine/
#   - m02_5 vive en script_engine/   (no en raíz)
#   - tts_normalizer vive en raíz
from script_engine.m01b_narrator import (
    TONE_INSTRUCTIONS_BY_INTENT, PROSE_RULES, _first_sentence,
)
from script_engine.m02_5_normalizer_gate import _build_system_instruction
from tts_normalizer import normalize_for_tts


def test_tone_blocks_tienen_pausas():
    for intent, txt in TONE_INSTRUCTIONS_BY_INTENT.items():
        assert "PAUSAS" in txt, f"{intent}: falta guia de PAUSAS"
        assert "..." in txt, f"{intent}: no menciona el marcador '...'"


def test_hook_abre_con_pausa():
    h = TONE_INSTRUCTIONS_BY_INTENT["hook"]
    assert "..." in h and "ANTES" in h, "hook no instruye abrir con '...' ANTES"


def test_prose_rules_regla_pausas():
    assert "PAUSAS" in PROSE_RULES and "..." in PROSE_RULES


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
