"""
test_chat51_outro_no_fatal.py — valida que un outro un toque largo NO mate el topic (CHAT 51),
SIN red ni Gemini (call_flash_json mockeado). Cubre §3 del handoff.

POR QUÉ: corrida real (Fordlandia) murió en m01b con cap 7 = 1111 chars (techo 1100, se pasó
por 11) → raise → topic ya investigado perdido. Fix de raíz: el outro (cierre, no cliffhanger)
se recorta en límite de oración a ≤hi en vez de explotar. SOLO outro + SOLO lado largo.

Cubre:
  - caso real: outro >1100 en el último intento → _trim_to_sentence_boundary → retorna
    (no raise), termina en .!?…, 400 ≤ len ≤ 1100.
  - outro de UNA sola oración gigante (>hi) → trimmed "" → raise.
  - recorte que dejaría <400 → no se acepta → raise.
  - hook largo → NO se recorta → raise (no entra al branch outro).
  - development largo → NO se recorta → raise.
  - outro corto (<400) → raise (no hay recorte para el corto).
  - 1.2: la instrucción de reintento del outro usa techo CON margen (hi-120); dev usa hi.
  - 1.3: el outro tiene 3 intentos (hook/dev siguen en 2).
  - _trim_to_sentence_boundary unit: respeta oraciones, no parte palabras, maneja '…'.

Correr:  python -X utf8 test_chat51_outro_no_fatal.py
"""
from __future__ import annotations

import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import script_engine.m01b_narrator as m
from script_engine.m01b_narrator import (
    _trim_to_sentence_boundary, _call_with_length_retry,
    NarrationValidationError, LEN_OUTRO, LEN_DEVELOPMENT, OUTRO_RETRY_MARGIN,
)

# Oración limpia (sin aperturas/cierres/conectores prohibidos), termina en punto.
SENT = "La estructura abandonada resistia el paso del tiempo en silencio."


def _text(n_sentences: int) -> str:
    return " ".join([SENT] * n_sentences)


class _MockFlash:
    """call_flash_json mockeado: devuelve narraciones en cola y registra los prompts."""
    def __init__(self, narrations):
        self.queue = list(narrations)
        self.prompts: list[str] = []
        self.calls = 0

    def __call__(self, prompt):
        self.prompts.append(prompt)
        self.calls += 1
        # si se agota la cola, repetir la última (mock estable)
        narr = self.queue.pop(0) if self.queue else (self.prompts and SENT)
        return {"narration": narr}


def run():
    failures = []

    def check(cond, msg):
        print(f"  [{'✓' if cond else '✗'}] {msg}")
        if not cond:
            failures.append(msg)

    orig_flash = m.call_flash_json
    lo, hi = LEN_OUTRO   # (400, 1100)

    # ── _trim_to_sentence_boundary unit ──
    print("unit — _trim_to_sentence_boundary\n")
    t = _trim_to_sentence_boundary("Uno. Dos. Tres.", 8)
    check(t == "Uno.", f"respeta límite de oración: {t!r} == 'Uno.'")
    t2 = _trim_to_sentence_boundary("Hola mundo entero. Segunda.", 10)
    check(t2 == "Hola mundo entero." or t2 == "",
          f"no parte palabras (oración 1 = 18 chars > 10 → ''): {t2!r}")
    t3 = _trim_to_sentence_boundary("Primera corta. Segunda.", 14)
    check(t3 == "Primera corta.", f"corta=14 entra justo: {t3!r}")
    te = _trim_to_sentence_boundary("Hola… Mundo final.", 6)
    check(te == "Hola…", f"maneja '…': {te!r}")
    tg = _trim_to_sentence_boundary("UnaSolaOracionGiganteSinPunto", 5)
    check(tg == "", f"oración única > max → '': {tg!r}")

    # ── caso real: outro 1111-ish en el último intento → recorta y retorna ──
    print("\ncaso real — outro largo en el último intento → recortado, NO raise\n")
    long_outro = _text(20)   # ~1300 chars, varias oraciones, todas terminan en '.'
    check(len(long_outro) > hi, f"setup: el outro mock mide {len(long_outro)} > {hi}")
    mock = _MockFlash([long_outro, long_outro, long_outro])  # 3 intentos, siempre largo
    m.call_flash_json = mock
    try:
        result = _call_with_length_retry("PROMPT", role="reveal_outro", cap_number=7, max_attempts=3)
        ok = True
    except NarrationValidationError:
        result = None
        ok = False
    finally:
        m.call_flash_json = orig_flash
    check(ok and result is not None, "outro largo → retorna (no raise)")
    check(result and len(result) <= hi, f"recortado a ≤{hi}: {len(result) if result else '—'}")
    check(result and len(result) >= lo, f"sigue ≥{lo}: {len(result) if result else '—'}")
    check(result and result[-1] in ".!?…", f"termina en oración completa: …{result[-6:]!r}" if result else "—")
    check(mock.calls == 3, f"1.3: el outro intentó 3 veces antes de recortar: {mock.calls}")

    # ── 1.2: la instrucción de reintento del outro usa techo CON margen ──
    print("\n1.2 — instrucción de reintento: outro con margen (hi-120), dev sin margen\n")
    mock2 = _MockFlash([long_outro, _text(11)])  # intento1 largo, intento2 válido (~720)
    m.call_flash_json = mock2
    try:
        _call_with_length_retry("PROMPT", role="reveal_outro", cap_number=7, max_attempts=3)
    finally:
        m.call_flash_json = orig_flash
    retry_prompt = mock2.prompts[1] if len(mock2.prompts) > 1 else ""
    check(f"MÁXIMO {hi - OUTRO_RETRY_MARGIN}" in retry_prompt,
          f"outro: instruye techo con margen 'MÁXIMO {hi - OUTRO_RETRY_MARGIN}'")
    check(f"MÁXIMO {hi} chars" not in retry_prompt,
          "outro: NO instruye el techo pelado (hi)")

    dlo, dhi = LEN_DEVELOPMENT
    long_dev = _text(40)   # > 2000
    mid_dev = _text(22)    # ~1430, dentro de [800,2000]
    check(len(long_dev) > dhi and dlo <= len(mid_dev) <= dhi, "setup dev ok")
    mock3 = _MockFlash([long_dev, mid_dev])
    m.call_flash_json = mock3
    try:
        _call_with_length_retry("PROMPT", role="development", cap_number=3, max_attempts=2)
    finally:
        m.call_flash_json = orig_flash
    dev_retry = mock3.prompts[1] if len(mock3.prompts) > 1 else ""
    check(f"MÁXIMO {dhi} chars" in dev_retry,
          f"development: instrucción intacta (techo = hi = {dhi}, sin margen)")

    # ── outro de UNA sola oración gigante → trimmed '' → raise ──
    print("\noutro oración única gigante → raise legítimo\n")
    giant = "A" * (hi + 200) + "."   # sin espacios internos = una sola oración
    mock4 = _MockFlash([giant, giant, giant])
    m.call_flash_json = mock4
    try:
        _call_with_length_retry("PROMPT", role="reveal_outro", cap_number=7, max_attempts=3)
        raised = False
    except NarrationValidationError:
        raised = True
    finally:
        m.call_flash_json = orig_flash
    check(raised, "oración única > hi (no recortable) → raise")

    # ── recorte dejaría < 400 → no se acepta → raise ──
    print("\nrecorte que dejaría <400 → raise\n")
    s1 = "X" * 378 + "."          # 379 chars, una oración < lo
    s2 = "Y" * 800 + "."          # oración enorme; s1+s2 > hi
    two = s1 + " " + s2
    check(len(two) > hi and 379 < lo, "setup: total > hi y la 1ra oración < 400")
    mock5 = _MockFlash([two, two, two])
    m.call_flash_json = mock5
    try:
        _call_with_length_retry("PROMPT", role="reveal_outro", cap_number=7, max_attempts=3)
        raised5 = False
    except NarrationValidationError:
        raised5 = True
    finally:
        m.call_flash_json = orig_flash
    check(raised5, "recorte cae < 400 → no se acepta → raise")

    # ── hook largo → NO se recorta → raise ──
    print("\nhook/development largos → NO se recortan\n")
    long_hook = _text(16)   # > 800 (LEN_HOOK hi)
    mock6 = _MockFlash([long_hook, long_hook])
    m.call_flash_json = mock6
    try:
        _call_with_length_retry("PROMPT", role="hook", cap_number=1, max_attempts=2)
        rh = False
    except NarrationValidationError:
        rh = True
    finally:
        m.call_flash_json = orig_flash
    check(rh, "hook largo → raise (no entra al branch outro)")

    mock7 = _MockFlash([long_dev, long_dev])
    m.call_flash_json = mock7
    try:
        _call_with_length_retry("PROMPT", role="development", cap_number=4, max_attempts=2)
        rd = False
    except NarrationValidationError:
        rd = True
    finally:
        m.call_flash_json = orig_flash
    check(rd, "development largo → raise (no se recorta)")

    # ── outro corto (<400) → raise (no hay recorte del lado corto) ──
    print("\noutro corto (<400) → raise (sin recorte del lado corto)\n")
    short = _text(3)   # ~195 chars < 400
    check(len(short) < lo, f"setup: outro corto {len(short)} < {lo}")
    mock8 = _MockFlash([short, short, short])
    m.call_flash_json = mock8
    try:
        _call_with_length_retry("PROMPT", role="reveal_outro", cap_number=7, max_attempts=3)
        rs = False
    except NarrationValidationError:
        rs = True
    finally:
        m.call_flash_json = orig_flash
    check(rs, "outro corto → raise (el corto no se puede fabricar)")

    print("\n" + ("✅ TODOS OK" if not failures else f"❌ {len(failures)} FALLO(S): " + "; ".join(failures)))
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(run())
