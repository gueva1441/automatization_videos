"""
test_m01b_retry.py — Tests SIN red del retry de m01b (handoff chat 114).

Cubre que _call_with_length_retry reintenta también las violaciones de FRASE
(apertura/cierre/conector), no solo el largo, y que el salvataje de outro (chat 51)
y el retry de largo siguen intactos. call_flash_json se fakea (cero red).
"""
from __future__ import annotations

import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import script_engine.m01b_narrator as m
from script_engine.m01b_narrator import NarrationValidationError


def _section(t): print("\n" + "─" * 68 + f"\n{t}")


# Unidad de oración SIN frases prohibidas (apertura/cierre/conector). Termina en ". "
# para que _trim_to_sentence_boundary pueda cortar por oración.
UNIT = "El metal frío crujió en la penumbra y nadie respondió al llamado. "
CLEAN_DEV = (UNIT * 16).strip()                       # ~1050 chars ∈ [800, 2000]
PHRASE_DEV = (UNIT * 8 + "A continuación, todo cambió para siempre. "
              + UNIT * 8).strip()                     # contiene "a continuación", largo en rango
OPEN_BAD_DEV = ("En este video vas a entender por qué todo se vino abajo. "
                + UNIT * 15).strip()                  # apertura prohibida
CLOSE_BAD_DEV = (UNIT * 15 + "Si te gustó, dejá tu comentario abajo.").strip()  # cierre prohibido
TOO_LONG_DEV = (UNIT * 40).strip()                    # > 2000
TOO_SHORT_DEV = (UNIT * 5).strip()                    # < 800
OUTRO_LONG = (UNIT * 18).strip()                      # > 1100, recortable a ∈ [400, 1100]


class _FakeFlash:
    """Cola de respuestas para call_flash_json; registra los prompts recibidos."""
    def __init__(self, narrations):
        self.queue = list(narrations)
        self.prompts: list[str] = []

    def __call__(self, prompt, response_schema=None):
        self.prompts.append(prompt)
        narr = self.queue.pop(0)
        return {"narration": narr}


def _patch(narrations):
    fake = _FakeFlash(narrations)
    m.call_flash_json = fake
    return fake


def test_retry_phrase_connector():
    _section("1· RETRY de frase (conector 'a continuación') → reintenta y zafa")
    orig = m.call_flash_json
    ok = True
    try:
        fake = _patch([PHRASE_DEV, CLEAN_DEV])
        out = m._call_with_length_retry("PROMPT", role="development", cap_number=3)
        if out != CLEAN_DEV:
            ok = False; print("  ✗ no devolvió la narración limpia tras el reintento")
        else:
            print("  ✓ devuelve la narración limpia (no raise)")
        if len(fake.prompts) != 2:
            ok = False; print(f"  ✗ se esperaban 2 llamadas, hubo {len(fake.prompts)}")
        elif "FRASE PROHIBIDA" not in fake.prompts[1] or "a continuación" not in fake.prompts[1]:
            ok = False; print("  ✗ el 2do prompt no trae la dirección de frase con el detail")
        else:
            print("  ✓ 2do prompt = dirección de frase con detail \"a continuación\"")
    finally:
        m.call_flash_json = orig
    return ok


def test_retry_phrase_open_and_close():
    _section("2· apertura/cierre prohibidos → reintenta y zafa")
    orig = m.call_flash_json
    ok = True
    try:
        for label, bad in (("apertura", OPEN_BAD_DEV), ("cierre", CLOSE_BAD_DEV)):
            _patch([bad, CLEAN_DEV])
            out = m._call_with_length_retry("PROMPT", role="development", cap_number=4)
            if out != CLEAN_DEV:
                ok = False; print(f"  ✗ {label}: no zafó en el reintento")
            else:
                print(f"  ✓ {label} prohibido → reintenta y devuelve la limpia")
    finally:
        m.call_flash_json = orig
    return ok


def test_phrase_exhausted_raises():
    _section("3· EXHAUSTO: todos los intentos repiten la frase → raise (kind preservado)")
    orig = m.call_flash_json
    ok = True
    try:
        _patch([PHRASE_DEV, PHRASE_DEV])
        try:
            m._call_with_length_retry("PROMPT", role="development", cap_number=3)
            ok = False; print("  ✗ no lanzó NarrationValidationError")
        except NarrationValidationError as e:
            if e.kind != "phrase":
                ok = False; print(f"  ✗ kind no preservado: {e.kind!r}")
            elif e.detail != "a continuación":
                ok = False; print(f"  ✗ detail no preservado: {e.detail!r}")
            else:
                print("  ✓ raise en el último intento con kind='phrase', detail='a continuación'")
    finally:
        m.call_flash_json = orig
    return ok


def test_length_retry_regression():
    _section("4· REGRESIÓN largo: >hi reescribe, <lo reescribe")
    orig = m.call_flash_json
    ok = True
    try:
        fake = _patch([TOO_LONG_DEV, CLEAN_DEV])
        out = m._call_with_length_retry("PROMPT", role="development", cap_number=2)
        if out != CLEAN_DEV or "DEMASIADO LARGO" not in fake.prompts[1]:
            ok = False; print("  ✗ retry de largo (>hi) no funcionó")
        else:
            print("  ✓ >hi → 'DEMASIADO LARGO' y zafa")
        fake = _patch([TOO_SHORT_DEV, CLEAN_DEV])
        out = m._call_with_length_retry("PROMPT", role="development", cap_number=2)
        if out != CLEAN_DEV or "DEMASIADO CORTO" not in fake.prompts[1]:
            ok = False; print("  ✗ retry de largo (<lo) no funcionó")
        else:
            print("  ✓ <lo → 'DEMASIADO CORTO' y zafa")
    finally:
        m.call_flash_json = orig
    return ok


def test_outro_salvage_intact():
    _section("5· REGRESIÓN salvataje outro: outro >hi en el último intento → recorta y acepta")
    orig = m.call_flash_json
    ok = True
    try:
        # outro largo en TODOS los intentos (max_attempts=3) → en el último, salvataje.
        _patch([OUTRO_LONG, OUTRO_LONG, OUTRO_LONG])
        out = m._call_with_length_retry("PROMPT", role="reveal_outro", cap_number=7,
                                        max_attempts=3)
        lo, hi = m.LEN_OUTRO
        if not (lo <= len(out) <= hi):
            ok = False; print(f"  ✗ salvataje no dejó el outro en rango: {len(out)} ∉ [{lo},{hi}]")
        elif len(out) >= len(OUTRO_LONG):
            ok = False; print("  ✗ no recortó (devolvió el largo original)")
        elif not out.endswith((".", "!", "?", "…")):
            ok = False; print("  ✗ el recorte no terminó en límite de oración")
        else:
            print(f"  ✓ outro {len(OUTRO_LONG)}→{len(out)} chars recortado por oración y aceptado")
    finally:
        m.call_flash_json = orig
    return ok


def main() -> int:
    print("=" * 68 + "\n  TESTS m01b retry (sin red)\n" + "=" * 68)
    results = {
        "retry_phrase_connector": test_retry_phrase_connector(),
        "retry_phrase_open_close": test_retry_phrase_open_and_close(),
        "phrase_exhausted_raises": test_phrase_exhausted_raises(),
        "length_retry_regression": test_length_retry_regression(),
        "outro_salvage_intact": test_outro_salvage_intact(),
    }
    print("\n" + "=" * 68)
    for k, v in results.items():
        print(f"  {'PASS ✅' if v else 'FAIL ❌'}  {k}")
    print("=" * 68)
    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
