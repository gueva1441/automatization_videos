"""
test_judge_seeds_cache.py — Test SIN red del cache del juez de seeds (chat 56).

Bug: judge_seeds re-juzgaba seeds que ya tenían seed["judge"] persistido (60 llamadas LLM
repetidas por corrida). Fix: skip si seed["judge"] existe; --rejudge (force=True) fuerza.
Monkeypatch de _judge_once → cuenta invocaciones sin tocar el LLM.
"""
from __future__ import annotations

import sys

from script_engine import m_judge_seeds as mj


def _spy_seed(title, judged=True):
    s = {"discovery_mode": "spy_arbitrage", "seed_title": title}
    if judged:
        s["judge"] = {"verdict": "oro", "cohort": "3/3", "risk": "ninguno", "votes": ["oro", "oro", "oro"]}
    return s


def main() -> int:
    print("=" * 64 + "\n  TEST cache del juez de seeds (sin red)\n" + "=" * 64)
    calls = {"n": 0}
    orig = mj._judge_once
    mj._judge_once = lambda seed: (calls.__setitem__("n", calls["n"] + 1)
                                   or {"verdict": "oro", "risk": "ninguno", "reason": "fake"})
    ok = True
    try:
        # 1. seed con judge previo + force=False → NO re-juzga
        calls["n"] = 0
        mj.judge_seeds([_spy_seed("cacheado")], n_votes=3, force=False)
        if calls["n"] != 0:
            ok = False; print(f"  ✗ re-juzgó un seed cacheado ({calls['n']} llamadas)")
        else:
            print("  ✓ seed con judge previo NO dispara _judge_once (cacheado)")

        # 2. seed con judge previo + force=True → SÍ re-juzga (n_votes llamadas)
        calls["n"] = 0
        mj.judge_seeds([_spy_seed("forzado")], n_votes=3, force=True)
        if calls["n"] != 3:
            ok = False; print(f"  ✗ force=True no re-juzgó ({calls['n']} llamadas, esperaba 3)")
        else:
            print("  ✓ force=True (--rejudge) re-juzga: 3 votos")

        # 3. seed SIN judge → juzga normal y persiste seed["judge"]
        calls["n"] = 0
        fresh = _spy_seed("nuevo", judged=False)
        mj.judge_seeds([fresh], n_votes=3)
        if calls["n"] != 3 or "judge" not in fresh:
            ok = False; print(f"  ✗ seed nuevo: {calls['n']} llamadas, judge={'judge' in fresh}")
        else:
            print("  ✓ seed sin judge → 3 votos + seed['judge'] persistido")

        # 4. mezcla: 1 cacheado + 1 nuevo → solo el nuevo gasta llamadas
        calls["n"] = 0
        mj.judge_seeds([_spy_seed("cache"), _spy_seed("nuevo2", judged=False)], n_votes=3)
        if calls["n"] != 3:
            ok = False; print(f"  ✗ mezcla: {calls['n']} llamadas (esperaba 3, solo el nuevo)")
        else:
            print("  ✓ mezcla cacheado+nuevo → solo el nuevo gasta (3 llamadas)")
    finally:
        mj._judge_once = orig

    print("\n" + "=" * 64)
    print(f"  {'PASS ✅' if ok else 'FAIL ❌'}  cache del juez de seeds")
    print("=" * 64)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
