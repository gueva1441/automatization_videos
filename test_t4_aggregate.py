"""
test_t4_aggregate.py — valida la LÓGICA de _aggregate_v2 (regla 2/3-genérico) OFFLINE,
sin Gemini. La tabla contra los 26 seeds la produce _lab_judge_2of3_chat49.py (live).

Casos clave del consenso:
  - 2/3 descartar+generico → descartar (caza el genérico que el flip-flop hoy salva).
  - 3/3 oro → oro (NO mata joyas).
  - 2/3 descartar+ratio_inflado (no generico) → NO aplica la regla → flip-flop→inestable/dudoso.
  - 1/3 descartar+generico → NO aplica (NO veto de 1) → flip-flop→dudoso.

Correr:  python -X utf8 test_t4_aggregate.py
"""
from __future__ import annotations

import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from _lab_judge_2of3_chat49 import _aggregate_v2
from script_engine.m_judge_seeds import _aggregate as _aggregate_old


def V(verdict, risk="ninguno"):
    return {"verdict": verdict, "risk": risk, "reason": f"{verdict}/{risk}"}


def run():
    failures = []

    def check(cond, msg):
        print(f"  [{'✓' if cond else '✗'}] {msg}")
        if not cond:
            failures.append(msg)

    print("T4 — _aggregate_v2 (2/3-genérico), comparado con el viejo\n")

    # 1. 2/3 descartar+generico + 1 oro → NUEVO descarta (viejo lo salvaba como dudoso/inestable)
    votes = [V("descartar", "generico"), V("descartar", "generico"), V("oro")]
    old, new = _aggregate_old(votes, 3), _aggregate_v2(votes, 3)
    check(old["verdict"] == "dudoso", f"viejo: flip-flop → dudoso (era {old['verdict']})")
    check(new["verdict"] == "descartar" and new["cohort"] == "2/3",
          f"NUEVO: 2/3 generico → descartar (2/3)  [caza el genérico]")

    # 2. 3/3 oro → oro (no mata joyas)
    votes = [V("oro"), V("oro"), V("oro")]
    new = _aggregate_v2(votes, 3)
    check(new["verdict"] == "oro", "3/3 oro → oro (JOYA preservada)")

    # 3. 2/3 descartar pero ratio_inflado (no generico) → regla NO aplica → flip-flop→dudoso
    votes = [V("descartar", "ratio_inflado"), V("descartar", "ratio_inflado"), V("oro")]
    new = _aggregate_v2(votes, 3)
    check(new["verdict"] == "dudoso" and new["risk"] == "inestable",
          "2/3 descartar+ratio_inflado → NO aplica regla → dudoso/inestable")

    # 4. 1/3 descartar+generico → NO veto de 1 → flip-flop→dudoso
    votes = [V("descartar", "generico"), V("oro"), V("oro")]
    new = _aggregate_v2(votes, 3)
    check(new["verdict"] != "descartar", f"1/3 generico NO descarta (sin veto de 1) → {new['verdict']}")

    # 5. 3/3 descartar+generico → descartar 3/3
    votes = [V("descartar", "generico")] * 3
    new = _aggregate_v2(votes, 3)
    check(new["verdict"] == "descartar" and new["cohort"] == "3/3", "3/3 generico → descartar 3/3")

    # 6. 2/3 descartar+generico SIN oro (1 dudoso) → descartar (también, no solo en flip-flop)
    votes = [V("descartar", "generico"), V("descartar", "generico"), V("dudoso")]
    old, new = _aggregate_old(votes, 3), _aggregate_v2(votes, 3)
    check(new["verdict"] == "descartar", "2/3 generico + 1 dudoso → descartar")
    check(old["verdict"] == "descartar", "(el viejo ya descartaba este caso: regla no regresiona)")

    # 7. mayoría no-descartar intacta
    votes = [V("dudoso"), V("dudoso"), V("oro")]
    new = _aggregate_v2(votes, 3)
    check(new["verdict"] == "dudoso", "2/3 dudoso → dudoso (mayoría simple intacta)")

    print("\n" + ("✅ TODOS OK" if not failures else f"❌ {len(failures)} FALLO(S): " + "; ".join(failures)))
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(run())
