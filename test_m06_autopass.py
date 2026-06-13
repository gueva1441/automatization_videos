"""
test_m06_autopass.py — Tests SIN red del auto-pass de m06 (chat 57).

classify_and_decide(interactive=False, auto_pass=True) debe ENSAMBLAR el JSON final
(como [P]) en vez de cortar en NON_INTERACTIVE — si no, el batch rompe sin script.json.
interactive=False SIN auto_pass sigue siendo audit-only (final_path=None).

Monkeypatchea los helpers de disco/LLM de m06 para no tocar red ni filesystem.
"""
from __future__ import annotations

import sys
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from script_engine import m06_classifier as m


def _section(t): print("\n" + "─" * 68 + f"\n{t}")


def _install():
    """Fakea todo lo que classify_and_decide toca con issues relevantes. Devuelve
    (counters, restore())."""
    counters = {"assemble": 0, "fps": 0, "persisted": 0}
    orig = (m.assemble_final_script, m._approve_false_positives, m._load_step,
            m._load_topic_facts, m._load_known_fps, m.classify_one_issue,
            m._persist_issue_payload, m._print_summary)

    def _assemble(tid):
        counters["assemble"] += 1
        return Path("data") / "scripts" / f"{tid}.json"

    def _fps(payloads):
        counters["fps"] += 1
        return 2

    def _persist(tid, payload, n):
        counters["persisted"] += 1
        return Path("x")

    m.assemble_final_script = _assemble
    m._approve_false_positives = _fps
    m._load_step = lambda tid, name: {}
    m._load_topic_facts = lambda tid: {}
    m._load_known_fps = lambda: []
    m.classify_one_issue = lambda *a, **k: {"bucket": "grave", "chapter_id": "ch01"}
    m._persist_issue_payload = _persist
    m._print_summary = lambda tid, payloads: None

    def restore():
        (m.assemble_final_script, m._approve_false_positives, m._load_step,
         m._load_topic_facts, m._load_known_fps, m.classify_one_issue,
         m._persist_issue_payload, m._print_summary) = orig

    return counters, restore


# judge_result con issues relevantes (cohort>=2) que NO es PASS → llega al gate
_JUDGE = {
    "global_verdict": "REROLL",
    "all_issues": [
        {"cohort": 2, "chapter_id": "ch01", "image_index": 1},
        {"cohort": 3, "chapter_id": "ch02", "image_index": 2},
    ],
}


def test_auto_pass_assembles():
    _section("1· interactive=False + auto_pass=True → AUTO_PASS, final_path!=None")
    counters, restore = _install()
    ok = True
    try:
        res = m.classify_and_decide("TID", _JUDGE, interactive=False, auto_pass=True)
        if res["decision"] != "AUTO_PASS":
            ok = False; print(f"  ✗ decision={res['decision']!r} (esperaba AUTO_PASS)")
        else:
            print("  ✓ decision == AUTO_PASS")
        if not res["final_path"]:
            ok = False; print("  ✗ final_path es None/vacío (batch rompería)")
        else:
            print(f"  ✓ final_path ensamblado: {res['final_path']}")
        if counters["assemble"] != 1:
            ok = False; print(f"  ✗ assemble_final_script llamado {counters['assemble']}×")
        else:
            print("  ✓ assemble_final_script llamado 1×")
        if res["fps_added"] != 2:
            ok = False; print(f"  ✗ fps_added={res['fps_added']} (esperaba 2)")
        else:
            print("  ✓ fps_added propagado (2)")
        if counters["persisted"] != 2:
            ok = False; print(f"  ✗ issues persistidos={counters['persisted']} (esperaba 2)")
        else:
            print("  ✓ los 2 issues quedaron logueados (_persist_issue_payload)")
    finally:
        restore()
    return ok


def test_audit_only_unchanged():
    _section("2· interactive=False SIN auto_pass → NON_INTERACTIVE, final_path=None (intacto)")
    counters, restore = _install()
    ok = True
    try:
        res = m.classify_and_decide("TID", _JUDGE, interactive=False, auto_pass=False)
        if res["decision"] != "NON_INTERACTIVE":
            ok = False; print(f"  ✗ decision={res['decision']!r} (esperaba NON_INTERACTIVE)")
        else:
            print("  ✓ decision == NON_INTERACTIVE (audit-only)")
        if res["final_path"] is not None:
            ok = False; print(f"  ✗ final_path={res['final_path']!r} (esperaba None)")
        else:
            print("  ✓ final_path None (no ensambló)")
        if counters["assemble"] != 0:
            ok = False; print(f"  ✗ assemble_final_script llamado {counters['assemble']}× (no debía)")
        else:
            print("  ✓ NO ensambló (audit-only intacto)")
    finally:
        restore()
    return ok


def main() -> int:
    print("=" * 68 + "\n  TESTS m06 auto-pass (sin red)\n" + "=" * 68)
    results = {
        "auto_pass_assembles": test_auto_pass_assembles(),
        "audit_only_unchanged": test_audit_only_unchanged(),
    }
    print("\n" + "=" * 68)
    for k, v in results.items():
        print(f"  {'PASS ✅' if v else 'FAIL ❌'}  {k}")
    print("=" * 68)
    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
