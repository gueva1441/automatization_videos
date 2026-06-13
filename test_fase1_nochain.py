"""
test_fase1_nochain.py — Test SIN red del flag --no-chain de fase1 (chat 57).

run_latido_a(no_chain=True) NO debe auto-encadenar al guion (run_one_topic_from_menu);
no_chain=False (default) SÍ lo llama (comportamiento histórico chat 35 intacto).

Neutraliza los pasos pesados de Latido A (con skip flags + monkeypatch de los helpers)
para llegar al bloque final de encadenamiento sin tocar red ni APIs.
"""
from __future__ import annotations

import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import fase1
from fase1_5 import __name__ as _f15  # noqa: F401  (asegura que fase1_5 importa)
import fase1_5


def _section(t): print("\n" + "─" * 68 + f"\n{t}")


def _run_latido_a(no_chain: bool, counter: dict) -> None:
    """Corre run_latido_a con todos los pasos caros neutralizados; cuenta las
    llamadas a run_one_topic_from_menu."""
    # skip_niche/research/validate=True cortocircuita PASO 1-3; quedan PASO 4
    # (export) + el bloque de encadenamiento. video_type evita el prompt.
    orig = {
        "audit": fase1._audit_pending_promises,
        "seeds": fase1._load_seeds,
        "load_db": fase1.load_db,
        "export": getattr(fase1, "export_fase1_csv", None),
        "summary": getattr(fase1, "print_export_summary", None),
        "cost": fase1._close_cost_tracking,
        "menu": fase1_5.run_one_topic_from_menu,
    }
    try:
        fase1._audit_pending_promises = lambda: None
        fase1._load_seeds = lambda: [{"seed_title": "x"}]
        fase1.load_db = lambda: {"topics": [{"id": "t1"}]}
        fase1.export_fase1_csv = lambda: "fake.csv"
        fase1.print_export_summary = lambda p: None
        fase1._close_cost_tracking = lambda: None
        fase1_5.run_one_topic_from_menu = lambda *a, **k: counter.__setitem__("n", counter["n"] + 1)

        fase1.run_latido_a(
            video_type="long",
            skip_niche=True, skip_research=True, skip_validate=True,
            no_chain=no_chain,
        )
    finally:
        fase1._audit_pending_promises = orig["audit"]
        fase1._load_seeds = orig["seeds"]
        fase1.load_db = orig["load_db"]
        if orig["export"] is not None:
            fase1.export_fase1_csv = orig["export"]
        if orig["summary"] is not None:
            fase1.print_export_summary = orig["summary"]
        fase1._close_cost_tracking = orig["cost"]
        fase1_5.run_one_topic_from_menu = orig["menu"]


def test_no_chain_true_skips_menu():
    _section("1· no_chain=True → NO llama run_one_topic_from_menu")
    counter = {"n": 0}
    _run_latido_a(no_chain=True, counter=counter)
    ok = counter["n"] == 0
    print(f"  {'✓' if ok else '✗'} run_one_topic_from_menu llamado {counter['n']}× (esperaba 0)")
    return ok


def test_no_chain_false_calls_menu():
    _section("2· no_chain=False (default) → SÍ llama run_one_topic_from_menu")
    counter = {"n": 0}
    _run_latido_a(no_chain=False, counter=counter)
    ok = counter["n"] == 1
    print(f"  {'✓' if ok else '✗'} run_one_topic_from_menu llamado {counter['n']}× (esperaba 1)")
    return ok


def main() -> int:
    print("=" * 68 + "\n  TESTS fase1 --no-chain (sin red)\n" + "=" * 68)
    results = {
        "no_chain_true_skips_menu": test_no_chain_true_skips_menu(),
        "no_chain_false_calls_menu": test_no_chain_false_calls_menu(),
    }
    print("\n" + "=" * 68)
    for k, v in results.items():
        print(f"  {'PASS ✅' if v else 'FAIL ❌'}  {k}")
    print("=" * 68)
    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
