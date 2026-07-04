"""
test_module_135d_loop.py — HANDOFF_135d (offline, sin render real).

Ciclo DepthFlow fijo (7s) + stream_loop para ventanas largas:
  1. duration=17.3 → DepthFlow llamado con 7.0 (a un _cycle), ffmpeg con -stream_loop -1 y -t 17.300.
  2. duration=6.0 → camino viejo: DepthFlow con 6.0 al output directo, SIN ffmpeg stream_loop.
  3. umbral: 9.0 → viejo · 9.01 → loop.
  Ken Burns NO se llama (no hay fallo).

Mockea build_depthflow_clip y subprocess.run del módulo.

USO:
    python test_module_135d_loop.py
"""
import subprocess as _sp
import sys
import tempfile
from pathlib import Path

import script_engine.parallax_animator_v2 as pav


def _check(c, m, fails):
    if not c:
        fails.append(m)


def _install_stubs():
    """Devuelve (calls, restore). calls = {'df': [(duration, out)], 'ff': [cmd], 'kb': int}."""
    calls = {"df": [], "ff": [], "kb": 0}
    o_df, o_run, o_kb = pav.build_depthflow_clip, pav.subprocess.run, pav.build_kenburns_fallback

    def stub_df(*, image_path, output_path, duration, flow_spec, width=None, height=None,
                fps=None, tiling_mode=None, **kw):
        calls["df"].append((round(float(duration), 3), Path(output_path)))
        Path(output_path).write_bytes(b"x")   # simula el mp4 del ciclo/clip
        return Path(output_path)

    def stub_run(cmd, **kw):
        calls["ff"].append(list(cmd))
        Path(cmd[-1]).write_bytes(b"y")        # simula el output final del ffmpeg
        return _sp.CompletedProcess(cmd, 0, stdout="", stderr="")

    def stub_kb(**kw):
        calls["kb"] += 1
        Path(kw["output_path"]).write_bytes(b"z")

    pav.build_depthflow_clip = stub_df
    pav.subprocess.run = stub_run
    pav.build_kenburns_fallback = stub_kb

    def restore():
        pav.build_depthflow_clip, pav.subprocess.run, pav.build_kenburns_fallback = o_df, o_run, o_kb
    return calls, restore


def _run(duration, out):
    return pav.build_animated_clip(
        image_path=Path("fake.png"), output_path=out, duration=duration,
        flow_spec={"movement": "horizontal", "intensity": 0.5, "steady": 0.5, "dof": False},
        width=2560, height=1440, fps=30,
    )


def main() -> int:
    fails: list[str] = []
    tmp = Path(tempfile.mkdtemp())
    calls, restore = _install_stubs()
    try:
        # ── (1) ventana larga 17.3 → ciclo 7.0 + stream_loop -t 17.300 ──
        out = tmp / "long.mp4"
        r = _run(17.3, out)
        _check(r == "depthflow", f"(1) no devolvió depthflow: {r}", fails)
        _check(calls["df"] == [(7.0, out.with_name("long_cycle.mp4"))],
               f"(1) DepthFlow no se llamó con 7.0 a un _cycle: {calls['df']}", fails)
        _check(len(calls["ff"]) == 1, f"(1) ffmpeg no se llamó 1 vez: {len(calls['ff'])}", fails)
        cmd = calls["ff"][0] if calls["ff"] else []
        _check("-stream_loop" in cmd and cmd[cmd.index("-stream_loop") + 1] == "-1",
               "(1) falta -stream_loop -1", fails)
        _check("-t" in cmd and cmd[cmd.index("-t") + 1] == "17.300",
               f"(1) -t no es 17.300: {cmd[cmd.index('-t')+1] if '-t' in cmd else 'n/a'}", fails)
        _check(calls["kb"] == 0, "(1) Ken Burns se llamó sin fallo", fails)
        _check(not out.with_name("long_cycle.mp4").exists(), "(1) no limpió el _cycle temporal", fails)

        # ── (2) ventana corta 6.0 → camino viejo, sin stream_loop ──
        calls["df"].clear(); calls["ff"].clear()
        out2 = tmp / "short.mp4"
        _run(6.0, out2)
        _check(calls["df"] == [(6.0, out2)], f"(2) DepthFlow no fue directo con 6.0: {calls['df']}", fails)
        _check(len(calls["ff"]) == 0, "(2) camino corto igual llamó ffmpeg stream_loop", fails)

        # ── (3) umbral exacto: 9.0 viejo · 9.01 loop ──
        calls["df"].clear(); calls["ff"].clear()
        _run(9.0, tmp / "t90.mp4")
        _check(calls["df"] == [(9.0, tmp / "t90.mp4")] and not calls["ff"],
               f"(3) 9.0 debía ser camino viejo: df={calls['df']} ff={len(calls['ff'])}", fails)
        calls["df"].clear(); calls["ff"].clear()
        _run(9.01, tmp / "t901.mp4")
        _check(calls["df"] and calls["df"][0][0] == 7.0 and len(calls["ff"]) == 1,
               f"(3) 9.01 debía ser loop: df={calls['df']} ff={len(calls['ff'])}", fails)
    finally:
        restore()

    if fails:
        print(f"[FAIL] {len(fails)} assert(s):")
        for f in fails:
            print(f"   ✗ {f}")
        return 1
    print("[PASS] ventana larga → ciclo 7s + stream_loop -t exacto; corta → camino viejo; umbral 9.0/9.01")
    return 0


if __name__ == "__main__":
    sys.exit(main())
