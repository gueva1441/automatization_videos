"""
test_fase3.py — Tests SIN red del runner fase3 (chat 56).

Cubre: resolución del video desde topics_db (DONE + path válido / sin DONE / path inexistente),
PACKAGED tras compose (callback), y el builder de argv headless. topics_db/m09 monkeypatcheados.
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import fase3
from script_engine import topics_db, m09_packaging as m09


def _section(t): print("\n" + "─" * 68 + f"\n{t}")


def test_resolve():
    _section("1· _resolve_video (DONE+path ok / sin DONE / path inexistente / no existe)")
    orig = topics_db.get_topic_by_id
    tmp = Path(tempfile.mkdtemp())
    mp4 = tmp / "v.mp4"; mp4.write_bytes(b"x")
    ok = True
    try:
        # válido
        topics_db.get_topic_by_id = lambda tid: {"id": tid, "status": "video_generated", "video_path": str(mp4)}
        t, vp = fase3._resolve_video("TID")
        if vp != str(mp4):
            ok = False; print(f"  ✗ path resuelto mal: {vp}")
        else:
            print("  ✓ DONE + path válido → resuelve")
        # sin DONE
        topics_db.get_topic_by_id = lambda tid: {"id": tid, "status": "validated", "video_path": str(mp4)}
        try:
            fase3._resolve_video("TID"); ok = False; print("  ✗ sin DONE no falló")
        except ValueError:
            print("  ✓ status != video_generated → error")
        # path inexistente
        topics_db.get_topic_by_id = lambda tid: {"id": tid, "status": "video_generated", "video_path": str(tmp / "no.mp4")}
        try:
            fase3._resolve_video("TID"); ok = False; print("  ✗ path inexistente no falló")
        except ValueError:
            print("  ✓ video_path inexistente → error")
        # topic None
        topics_db.get_topic_by_id = lambda tid: None
        try:
            fase3._resolve_video("TID"); ok = False; print("  ✗ topic None no falló")
        except ValueError:
            print("  ✓ topic inexistente → error")
        # sin video_path
        topics_db.get_topic_by_id = lambda tid: {"id": tid, "status": "video_generated"}
        try:
            fase3._resolve_video("TID"); ok = False; print("  ✗ sin video_path no falló")
        except ValueError:
            print("  ✓ DONE sin video_path → error")
    finally:
        topics_db.get_topic_by_id = orig
    return ok


def test_packaged_on_compose():
    _section("2· PACKAGED se setea tras COMPONER (callback de fase3.package)")
    orig = (m09.run_review, topics_db.mark_as_packaged, topics_db.get_topic_by_id)
    marked = {"ids": []}
    ok = True
    try:
        # run_review fake: invoca el on_compose como lo haría el form al componer
        m09.run_review = lambda tid, video_path=None, on_compose=None: on_compose and on_compose("thumb_final_01.png")
        topics_db.mark_as_packaged = lambda tid: marked["ids"].append(tid) or True
        topics_db.get_topic_by_id = lambda tid: {"id": tid, "packaged": None}
        fase3.package("TID", "/x/v.mp4")
        if marked["ids"] != ["TID"]:
            ok = False; print(f"  ✗ no marcó PACKAGED: {marked['ids']}")
        else:
            print("  ✓ COMPONER → mark_as_packaged('TID')")
    finally:
        m09.run_review, topics_db.mark_as_packaged, topics_db.get_topic_by_id = orig
    return ok


def test_headless_argv():
    _section("3· _build_m09_argv (passthrough headless correcto)")
    ok = True
    argv = fase3._build_m09_argv("TID", "/path/v3.mp4",
                                 ["--compose", "--base", "fresh_01.png", "--text", "HOLA", "--fill", "rojo"])
    exp = ["-m", "script_engine.m09_packaging", "TID", "--video-path", "/path/v3.mp4",
           "--compose", "--base", "fresh_01.png", "--text", "HOLA", "--fill", "rojo"]
    if argv != exp:
        ok = False; print(f"  ✗ argv:\n    {argv}\n  esperado:\n    {exp}")
    else:
        print("  ✓ argv incluye -m m09, topic, --video-path y el passthrough en orden")
    # candidates passthrough
    a2 = fase3._build_m09_argv("T", "/v.mp4", ["--candidates", "--only-fresh"])
    if a2[:5] != ["-m", "script_engine.m09_packaging", "T", "--video-path", "/v.mp4"] or a2[5:] != ["--candidates", "--only-fresh"]:
        ok = False; print(f"  ✗ candidates argv: {a2}")
    else:
        print("  ✓ --candidates --only-fresh pasan tal cual")
    return ok


def test_volatile_warning():
    _section("4· _volatile_warning (nombre volátil vs estable)")
    tmp = Path(tempfile.mkdtemp())
    (tmp / "abc_final.mp4").write_bytes(b"x")
    (tmp / "abc_final_v3_ZOOM.mp4").write_bytes(b"x")
    ok = True
    w = fase3._volatile_warning(str(tmp / "abc_final.mp4"))
    if not w or "VOLÁTIL" not in w:
        ok = False; print(f"  ✗ no avisó del nombre volátil: {w}")
    else:
        print("  ✓ avisa cuando el path es _final.mp4 y existe un _ZOOM estable")
    if fase3._volatile_warning(str(tmp / "abc_final_v3_ZOOM.mp4")) is not None:
        ok = False; print("  ✗ avisó sobre el estable")
    else:
        print("  ✓ no avisa sobre el nombre estable")
    return ok


def main() -> int:
    print("=" * 68 + "\n  TESTS fase3 (sin red)\n" + "=" * 68)
    results = {
        "resolve": test_resolve(),
        "packaged_on_compose": test_packaged_on_compose(),
        "headless_argv": test_headless_argv(),
        "volatile_warning": test_volatile_warning(),
    }
    print("\n" + "=" * 68)
    for k, v in results.items():
        print(f"  {'PASS ✅' if v else 'FAIL ❌'}  {k}")
    print("=" * 68)
    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
