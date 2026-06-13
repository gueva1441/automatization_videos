"""
test_run_pipeline.py — Tests SIN red del orquestador secuenciador (chat 57).

Monkeypatchea subprocess.run (fakea returncode + crea el artefacto de cada fase) y
los helpers de path/status para no tocar disco real ni topics_db. Cubre: orden de
comandos + tid, frenado en exit≠0, frenado por artefacto faltante, y que el modo
asistido SÍ llega a fase3.
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import run_pipeline as rp


def _section(t): print("\n" + "─" * 68 + f"\n{t}")


class _FakeCompleted:
    def __init__(self, rc): self.returncode = rc


def _install(tmp: Path, tid: str, *, rc_overrides=None, skip_artifacts=None):
    """Instala fakes y devuelve (calls, status_holder, restore()).

    calls: lista de (script_name, cmd) en orden.
    rc_overrides: {script_name: returncode} (default 0).
    skip_artifacts: set de script_names que NO crean su artefacto (simula [R]/[E]).
    """
    rc_overrides = rc_overrides or {}
    skip = skip_artifacts or set()
    calls: list[tuple[str, list]] = []
    status = {"v": "assets_rendered"}

    script_p = tmp / "scripts" / f"{tid}.json"
    manifest_p = tmp / "out" / tid / "assets" / "assets_manifest.json"

    orig = (rp.subprocess.run, rp._script_path, rp._manifest_path, rp._video_status)

    def fake_run(cmd, *a, **k):
        # cmd = [PY, "<script>.py", ...]
        script = cmd[1]
        calls.append((script, cmd))
        if script not in skip:
            if script == "fase1_5.py":
                script_p.parent.mkdir(parents=True, exist_ok=True)
                script_p.write_text("{}", encoding="utf-8")
            elif script == "fase2a.py":
                manifest_p.parent.mkdir(parents=True, exist_ok=True)
                manifest_p.write_text("{}", encoding="utf-8")
            elif script == "fase2b.py":
                status["v"] = rp.VIDEO_DONE_STATUS
        return _FakeCompleted(rc_overrides.get(script, 0))

    rp.subprocess.run = fake_run
    rp._script_path = lambda t: script_p
    rp._manifest_path = lambda t: manifest_p
    rp._video_status = lambda t: status["v"]

    def restore():
        (rp.subprocess.run, rp._script_path, rp._manifest_path, rp._video_status) = orig

    return calls, status, restore


def test_order_and_tid():
    _section("1· orden correcto de comandos + tid en cada uno (asistido)")
    tid = "top_abc"
    tmp = Path(tempfile.mkdtemp())
    calls, _status, restore = _install(tmp, tid)
    ok = True
    try:
        rc = rp.sequence(tid, batch=False)
        scripts = [s for s, _ in calls]
        if scripts != ["fase1_5.py", "fase2a.py", "fase2b.py", "fase3.py"]:
            ok = False; print(f"  ✗ orden de fases: {scripts}")
        else:
            print(f"  ✓ orden: {scripts}")
        if not all(tid in cmd for _, cmd in calls):
            ok = False; print("  ✗ tid no presente en alguna fase")
        else:
            print("  ✓ tid threadeado a las 4 fases")
        # fase1_5/fase2a por --topic; fase2b/fase3 posicional
        f15 = next(cmd for s, cmd in calls if s == "fase1_5.py")
        if "--topic" not in f15:
            ok = False; print("  ✗ fase1_5 sin --topic")
        else:
            print("  ✓ fase1_5 con --topic")
        if rc != 0:
            ok = False; print(f"  ✗ rc={rc} (esperaba 0)")
        else:
            print("  ✓ cadena completa rc=0")
    finally:
        restore()
    return ok


def test_stop_on_nonzero():
    _section("2· exit≠0 en fase2a → frena, NO llama fase2b/fase3")
    tid = "top_x"
    tmp = Path(tempfile.mkdtemp())
    calls, _status, restore = _install(tmp, tid, rc_overrides={"fase2a.py": 2})
    ok = True
    try:
        rc = rp.sequence(tid, batch=False)
        scripts = [s for s, _ in calls]
        if scripts != ["fase1_5.py", "fase2a.py"]:
            ok = False; print(f"  ✗ siguió después del fallo: {scripts}")
        else:
            print("  ✓ frenó tras fase2a, no llamó fase2b/fase3")
        if rc != 1:
            ok = False; print(f"  ✗ rc={rc} (esperaba 1)")
        else:
            print("  ✓ rc=1")
    finally:
        restore()
    return ok


def test_stop_missing_script():
    _section("3· sin data/scripts/<id>.json tras fase1_5 → frena en GUION")
    tid = "top_y"
    tmp = Path(tempfile.mkdtemp())
    # fase1_5 devuelve 0 PERO no deja el script (m06 quedó en [R]/[E])
    calls, _status, restore = _install(tmp, tid, skip_artifacts={"fase1_5.py"})
    ok = True
    try:
        rc = rp.sequence(tid, batch=False)
        scripts = [s for s, _ in calls]
        if scripts != ["fase1_5.py"]:
            ok = False; print(f"  ✗ siguió sin script fresco: {scripts}")
        else:
            print("  ✓ frenó en GUION (exit 0 pero sin artefacto)")
        if rc != 1:
            ok = False; print(f"  ✗ rc={rc} (esperaba 1)")
        else:
            print("  ✓ rc=1")
    finally:
        restore()
    return ok


def test_assisted_calls_fase3():
    _section("4· asistido → SÍ llama fase3 (form)")
    tid = "top_z"
    tmp = Path(tempfile.mkdtemp())
    calls, _status, restore = _install(tmp, tid)
    ok = True
    try:
        rp.sequence(tid, batch=False)
        if "fase3.py" not in [s for s, _ in calls]:
            ok = False; print("  ✗ no llamó fase3")
        else:
            f3 = next(cmd for s, cmd in calls if s == "fase3.py")
            print(f"  ✓ fase3 llamado (posicional): …{f3[1:]}")
        if tid not in next(cmd for s, cmd in calls if s == "fase3.py"):
            ok = False; print("  ✗ fase3 sin tid")
        else:
            print("  ✓ fase3 con tid posicional")
    finally:
        restore()
    return ok


def test_batch_skips_fase3():
    _section("5· --batch → NO llama fase3; fase1_5 recibe --batch")
    tid = "top_b"
    tmp = Path(tempfile.mkdtemp())
    calls, _status, restore = _install(tmp, tid)
    ok = True
    try:
        rc = rp.sequence(tid, batch=True)
        scripts = [s for s, _ in calls]
        if "fase3.py" in scripts:
            ok = False; print(f"  ✗ batch llamó fase3: {scripts}")
        else:
            print(f"  ✓ batch NO llama fase3: {scripts}")
        f15 = next(cmd for s, cmd in calls if s == "fase1_5.py")
        if "--batch" not in f15:
            ok = False; print(f"  ✗ fase1_5 sin --batch: {f15}")
        else:
            print("  ✓ fase1_5 recibe --batch")
        if rc != 0:
            ok = False; print(f"  ✗ rc={rc} (esperaba 0)")
        else:
            print("  ✓ rc=0 (cadena batch completa hasta video)")
    finally:
        restore()
    return ok


def main() -> int:
    print("=" * 68 + "\n  TESTS run_pipeline (sin red)\n" + "=" * 68)
    results = {
        "order_and_tid": test_order_and_tid(),
        "stop_on_nonzero": test_stop_on_nonzero(),
        "stop_missing_script": test_stop_missing_script(),
        "assisted_calls_fase3": test_assisted_calls_fase3(),
        "batch_skips_fase3": test_batch_skips_fase3(),
    }
    print("\n" + "=" * 68)
    for k, v in results.items():
        print(f"  {'PASS ✅' if v else 'FAIL ❌'}  {k}")
    print("=" * 68)
    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
