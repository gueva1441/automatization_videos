"""
test_m03_guarda1_degrade.py — Tests SIN red del fix Guarda 1 (handoff chat 114).

B1 (productor): _enforce_measure_fit suelta medidas sobrantes (>1/imagen) antes de lockear.
A  (backstop):  _fluidify_item DEGRADA (acepta la mejor prosa + WARN) en vez de raise tras
                los 3 intentos; solo raise si NINGUNA prosa fue utilizable.
call_pro_json se fakea (cero red).
"""
from __future__ import annotations

import io
import sys
from contextlib import redirect_stdout

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import script_engine.m03_visual as m
from script_engine.m03_visual import VisualValidationError


def _section(t): print("\n" + "─" * 68 + f"\n{t}")


class _StubProfile:
    """Perfil mínimo para _build_fluidificador_user (formula + aspect_ratio_text)."""
    formula = ("subject", "action", "setting", "lighting", "mood")
    aspect_ratio_text = "16:9 horizontal."


_SLOTS = {"subject": "a cold empty stone corridor", "action": "standing silent",
          "setting": "an abandoned ward", "lighting": "muted blue light", "mood": "dread"}


def _const_pro(prose):
    """Fake de call_pro_json que siempre devuelve la misma prosa."""
    def f(user, system_instruction=None, response_schema=None):
        return {"prose": prose}
    return f


class _CountingPro:
    def __init__(self, prose): self.prose = prose; self.calls = 0
    def __call__(self, *a, **k): self.calls += 1; return {"prose": self.prose}


# ─────────────────────────────────────────────────────────────────────────
def test_b1_drops_extra_measure():
    _section("1· B1 _enforce_measure_fit: suelta la 2da medida, conserva la 1ra + el año")
    locked = [
        {"num": "33", "kind": "measure", "mtype": "area"},
        {"num": "1939", "kind": "year"},
        {"num": "8,400", "kind": "measure", "mtype": "length"},
    ]
    buf = io.StringIO()
    with redirect_stdout(buf):
        kept = m._enforce_measure_fit(locked, "cap 3 img #17")
    out = buf.getvalue()
    ok = True
    measures = [it for it in kept if it["kind"] == "measure"]
    years = [it for it in kept if it["kind"] == "year"]
    if len(measures) != 1 or measures[0]["num"] != "33":
        ok = False; print(f"  ✗ no conservó SOLO la 1ra medida: {measures}")
    else:
        print("  ✓ conserva la 1ra medida (33, area), suelta la sobrante")
    if len(years) != 1 or years[0]["num"] != "1939":
        ok = False; print(f"  ✗ el año no se preservó: {years}")
    else:
        print("  ✓ el año (1939) NO se toca")
    if len(locked) != 3:
        ok = False; print("  ✗ mutó la lista original")
    else:
        print("  ✓ no muta el locked original")
    if "FIT" not in out or "8,400" not in out:
        ok = False; print(f"  ✗ sin WARN ruidoso del drop: {out!r}")
    else:
        print("  ✓ WARN ruidoso nombra la cifra soltada (8,400)")
    return ok


def test_b1_single_measure_untouched():
    _section("2· B1: carga posible (1 medida) pasa intacta, sin WARN")
    locked = [{"num": "873", "kind": "measure", "mtype": "area"}, {"num": "1885", "kind": "year"}]
    buf = io.StringIO()
    with redirect_stdout(buf):
        kept = m._enforce_measure_fit(locked, "cap 2 img #3")
    ok = kept == locked and buf.getvalue().strip() == ""
    print(f"  {'✓' if ok else '✗'} 1 medida + 1 año pasan intactos sin WARN")
    return ok


def test_a_degrade_returns_best_no_raise():
    _section("3· A backstop: 2da medida imposible → DEGRADA (mejor prosa + WARN), NO raise")
    locked = [{"num": "33", "kind": "measure", "mtype": "area"}]
    prose_missing = "A wide cold shot of an empty stone corridor in muted blue light, 16:9 horizontal."
    orig = m.call_pro_json
    ok = True
    try:
        m.call_pro_json = _const_pro(prose_missing)
        buf = io.StringIO()
        with redirect_stdout(buf):
            out = m._fluidify_item(_SLOTS, locked, _StubProfile(), "cap 3 img #17")
        warn = buf.getvalue()
        if out != prose_missing:
            ok = False; print(f"  ✗ no devolvió la mejor prosa degradada: {out!r}")
        else:
            print("  ✓ devuelve la mejor prosa (run sigue, no raise)")
        if "DEGRADADA" not in warn or "33" not in warn:
            ok = False; print(f"  ✗ sin WARN ruidoso de degradación: {warn!r}")
        else:
            print("  ✓ WARN ruidoso nombra la cifra no embebida (33)")
    except VisualValidationError as e:
        ok = False; print(f"  ✗ rompió en vez de degradar: {e}")
    finally:
        m.call_pro_json = orig
    return ok


def test_a_empty_prose_still_raises():
    _section("4· A: si NINGÚN intento devuelve prosa utilizable → raise legítimo")
    locked = [{"num": "33", "kind": "measure", "mtype": "area"}]
    orig = m.call_pro_json
    ok = True
    try:
        m.call_pro_json = _const_pro("")   # siempre vacío → nada que degradar
        buf = io.StringIO()
        try:
            with redirect_stdout(buf):
                m._fluidify_item(_SLOTS, locked, _StubProfile(), "cap 3 img #17")
            ok = False; print("  ✗ no lanzó VisualValidationError con prosa vacía")
        except VisualValidationError as e:
            if "no devolvió prosa utilizable" not in str(e):
                ok = False; print(f"  ✗ mensaje inesperado: {e}")
            else:
                print("  ✓ prosa vacía en todos los intentos → raise legítimo")
    finally:
        m.call_pro_json = orig
    return ok


def test_a_success_no_regression():
    _section("5· A: carga posible (cifra entra) → retorna al 1er intento (sin regresión)")
    locked = [{"num": "873", "kind": "measure", "mtype": "area"}]
    prose_ok = "A wide shot revealing 873 acres of barren cold land under grey light, 16:9 horizontal."
    orig = m.call_pro_json
    ok = True
    try:
        fake = _CountingPro(prose_ok)
        m.call_pro_json = fake
        out = m._fluidify_item(_SLOTS, locked, _StubProfile(), "cap 2 img #1")
        if out != prose_ok:
            ok = False; print(f"  ✗ no devolvió la prosa válida: {out!r}")
        elif fake.calls != 1:
            ok = False; print(f"  ✗ no cortó al 1er intento (calls={fake.calls})")
        else:
            print("  ✓ cifra embebida → retorna al 1er intento, sin reintentos ni degradación")
    finally:
        m.call_pro_json = orig
    return ok


def main() -> int:
    print("=" * 68 + "\n  TESTS m03 Guarda 1 — B1 fit + A backstop (sin red)\n" + "=" * 68)
    results = {
        "b1_drops_extra_measure": test_b1_drops_extra_measure(),
        "b1_single_measure_untouched": test_b1_single_measure_untouched(),
        "a_degrade_returns_best": test_a_degrade_returns_best_no_raise(),
        "a_empty_prose_raises": test_a_empty_prose_still_raises(),
        "a_success_no_regression": test_a_success_no_regression(),
    }
    print("\n" + "=" * 68)
    for k, v in results.items():
        print(f"  {'PASS ✅' if v else 'FAIL ❌'}  {k}")
    print("=" * 68)
    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
