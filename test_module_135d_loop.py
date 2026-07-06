"""
test_module_135d_loop.py — HANDOFF_135d + HANDOFF_140a (offline, sin render real).

VELOCIDAD CONSTANTE (140a): para los movimientos que loopean (horizontal/vertical/orbital),
CUALQUIER duración → 1 ciclo dulce de 7.0s + stream_loop -t (cortado/extendido a la ventana).
El umbral de 9s murió. Casos:
  1. loop largo 17.3 → DepthFlow(7.0 a _cycle) + ffmpeg -stream_loop -1 -t 17.300.
  2. loop CORTO 6.0 → TAMBIÉN DepthFlow(7.0) + ffmpeg -t 6.000 (antes iba directo; ese acople murió).
  3. FLAG-1 zoom_in (6.0 y 12.0) → camino viejo INTACTO: DepthFlow directo, SIN stream_loop.
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


def _run(duration, out, movement="horizontal"):
    return pav.build_animated_clip(
        image_path=Path("fake.png"), output_path=out, duration=duration,
        flow_spec={"movement": movement, "intensity": 0.5, "steady": 0.5, "dof": False},
        width=2560, height=1440, fps=30,
    )


def main() -> int:
    fails: list[str] = []
    tmp = Path(tempfile.mkdtemp())
    calls, restore = _install_stubs()
    try:
        # ── (1) loop largo 17.3 → ciclo 7.0 + stream_loop -t 17.300 ──
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

        # ── (2) HANDOFF_140a: loop CORTO 6.0 → TAMBIÉN ciclo 7.0 + stream_loop -t 6.000 ──
        calls["df"].clear(); calls["ff"].clear()
        out2 = tmp / "short.mp4"
        _run(6.0, out2)
        _check(calls["df"] == [(7.0, out2.with_name("short_cycle.mp4"))],
               f"(2) loop corto no usó el ciclo dulce 7.0: {calls['df']}", fails)
        _check(len(calls["ff"]) == 1, "(2) loop corto NO llamó stream_loop (velocidad no constante)", fails)
        cmd2 = calls["ff"][0] if calls["ff"] else []
        _check("-t" in cmd2 and cmd2[cmd2.index("-t") + 1] == "6.000",
               f"(2) -t del corto no es 6.000: {cmd2[cmd2.index('-t')+1] if '-t' in cmd2 else 'n/a'}", fails)

        # ── (3) FLAG-1: zoom_in queda INTACTO (directo, sin stream_loop) a cualquier duración ──
        for dz in (6.0, 12.0):
            calls["df"].clear(); calls["ff"].clear()
            oz = tmp / f"zoom_{dz}.mp4"
            _run(dz, oz, movement="zoom_in")
            _check(calls["df"] == [(round(dz, 3), oz)],
                   f"(3) zoom {dz} no fue DepthFlow directo: {calls['df']}", fails)
            _check(len(calls["ff"]) == 0,
                   f"(3) zoom {dz} llamó stream_loop (FLAG-1: debía quedar intacto)", fails)
    finally:
        restore()

    if fails:
        print(f"[FAIL] {len(fails)} assert(s):")
        for f in fails:
            print(f"   ✗ {f}")
        return 1
    print("[PASS] 140a: loop (corto y largo) → ciclo 7s + stream_loop -t exacto; zoom_in intacto")
    return 0


if __name__ == "__main__":
    sys.exit(main())
