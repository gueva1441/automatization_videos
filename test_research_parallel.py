"""
test_research_parallel.py — HANDOFF_121: paralelización de los 4 ángulos de grounding (sin red).

Cubre las aceptaciones D (tiempo: paralelo ~1× no 4×) y E (backoff 429 reintenta), + los
invariantes ① (mismas keys/contenido), ② (todos fallan → dict vacío, el caller hace RuntimeError)
y ③ (un ángulo cae aislado, los otros sobreviven). Monkeypatchea _research_angle → cero red.
"""
from __future__ import annotations

import io
import sys
import time
from contextlib import redirect_stdout

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import topic_researcher as tr
import error_handler as eh_mod

# Backoff SIN esperas reales — shim SOLO del `time` que ve error_handler (no toca el time global,
# así el sleep real del fake de test 1 sigue midiendo concurrencia de verdad).
_real_time = time


class _ShimTime:
    def __getattr__(self, name):      # delega todo lo demás al time real
        return getattr(_real_time, name)

    def sleep(self, *a, **k):         # ...menos sleep, que es no-op (retries instantáneos)
        pass


eh_mod.time = _ShimTime()

SEED = {"seed_title": "K-19 (test)"}
ANGLE_KEYS = {a["key"] for a in tr.DEEP_RESEARCH_ANGLES}


def _section(t): print("\n" + "─" * 68 + f"\n{t}")


def _patch_angle(fake):
    orig = tr._research_angle
    tr._research_angle = fake
    return orig


def test_parallel_speed_and_content():
    _section("1· paralelo: 4 ángulos, wall-time ~1× (no 4×) + contenido idéntico al serial (D/①)")
    PER = 0.4
    def fake(seed, angle):
        time.sleep(PER)                         # sleep real → libera GIL → corre en paralelo
        return f"{angle['key']}-block"
    orig = _patch_angle(fake)
    ok = True
    try:
        with redirect_stdout(io.StringIO()):
            t0 = time.perf_counter()
            blocks = tr._gather_angle_blocks(SEED)
            elapsed = time.perf_counter() - t0
    finally:
        tr._research_angle = orig
    if set(blocks) != ANGLE_KEYS:
        ok = False; print(f"  ✗ keys != esperadas: {set(blocks)} vs {ANGLE_KEYS}")
    elif any(blocks[k] != f"{k}-block" for k in ANGLE_KEYS):
        ok = False; print("  ✗ contenido por-ángulo incorrecto")
    else:
        print(f"  ✓ {len(ANGLE_KEYS)} keys presentes + contenido correcto (idéntico al serial)")
    serial = PER * len(ANGLE_KEYS)
    if elapsed < PER * 2:
        print(f"  ✓ wall-time {elapsed:.2f}s << serial {serial:.2f}s → paralelo real")
    else:
        ok = False; print(f"  ✗ wall-time {elapsed:.2f}s no bajó (esperaba < {PER*2:.2f}s)")
    return ok


def test_backoff_429_recovers():
    _section("2· backoff: 429 en el 1er intento → reintenta y zafa (E)")
    state = {"n": 0}
    def fake(seed, angle):
        state["n"] += 1
        if state["n"] == 1:
            raise Exception("simulated 429 RESOURCE_EXHAUSTED rate limit")
        return "recovered"
    orig = _patch_angle(fake)
    ok = True
    out = None
    try:
        with redirect_stdout(io.StringIO()):
            out = tr._research_angle_with_backoff(SEED, tr.DEEP_RESEARCH_ANGLES[0])
    except Exception as e:
        ok = False; print(f"  ✗ no se recuperó del 429: {type(e).__name__}: {e}")
    finally:
        tr._research_angle = orig
    if ok and out == "recovered" and state["n"] == 2:
        print("  ✓ 429 → reintento → 'recovered' (2 llamadas)")
    elif ok:
        ok = False; print(f"  ✗ out={out!r} n={state['n']} (esperaba 'recovered' en 2 llamadas)")
    return ok


def test_one_angle_fails_isolated():
    _section("3· aislamiento: un ángulo revienta → block='' y los otros sobreviven (③)")
    victim = sorted(ANGLE_KEYS)[0]
    def fake(seed, angle):
        if angle["key"] == victim:
            raise ValueError("boom (agota reintentos y no tumba a los demás)")
        return f"{angle['key']}-ok"
    orig = _patch_angle(fake)
    try:
        with redirect_stdout(io.StringIO()):
            blocks = tr._gather_angle_blocks(SEED)
    finally:
        tr._research_angle = orig
    ok = True
    if victim in blocks:
        ok = False; print(f"  ✗ el ángulo caído '{victim}' quedó en blocks")
    elif set(blocks) != (ANGLE_KEYS - {victim}):
        ok = False; print(f"  ✗ sobrevivientes != esperados: {set(blocks)}")
    else:
        print(f"  ✓ '{victim}' cae aislado; sobreviven {sorted(blocks)}")
    return ok


def test_all_fail_empty_dict():
    _section("4· guard: todos vacíos → _gather devuelve {} (el caller hace RuntimeError) (②)")
    def fake(seed, angle):
        return ""                                # éxito-pero-vacío (no excepción) → no reintenta
    orig = _patch_angle(fake)
    try:
        with redirect_stdout(io.StringIO()):
            blocks = tr._gather_angle_blocks(SEED)
    finally:
        tr._research_angle = orig
    ok = blocks == {}
    print(f"  {'✓' if ok else '✗'} angle_blocks vacío = {blocks!r} (guard del caller preservado)")
    return ok


def main() -> int:
    print("=" * 68 + "\n  TESTS research paralelo (HANDOFF_121, sin red)\n" + "=" * 68)
    results = {
        "parallel_speed_and_content": test_parallel_speed_and_content(),
        "backoff_429_recovers": test_backoff_429_recovers(),
        "one_angle_fails_isolated": test_one_angle_fails_isolated(),
        "all_fail_empty_dict": test_all_fail_empty_dict(),
    }
    print("\n" + "=" * 68)
    for k, v in results.items():
        print(f"  {'PASS ✅' if v else 'FAIL ❌'}  {k}")
    print("=" * 68)
    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
