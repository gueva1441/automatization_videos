"""
test_module_f30.py — F30: render rápido, el navegador solo pinta bloques (sin red; ffmpeg local con videos sintéticos
chicos). A: la escena safe no abre ventana y la cuece ffmpeg (cuadros exactos, el base conserva duración y fps).
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest
from PIL import Image

from gfx_config import gfx_rules
from script_engine import gfx_safe_bake as sb
from script_engine import gfx_sparse as sp
from script_engine.gfx_project import GfxScene

W, H, FPS = 160, 90, 30


def _png(path: Path) -> Path:
    im = Image.new("RGB", (W, H))
    for x in range(W):
        for y in range(H):
            im.putpixel((x, y), ((x * 7) % 256, (y * 11) % 256, ((x + y) * 5) % 256))
    im.save(path)
    return path


def _base(path: Path, dur: float) -> Path:
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"testsrc2=s={W}x{H}:r={FPS}:d={dur}",
                    "-c:v", "libx264", "-preset", "ultrafast", "-g", "30", "-pix_fmt", "yuv420p", str(path)], check=True)
    return path


def _probe(path: Path) -> tuple[int, str]:
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_frames", "-show_entries",
                        "stream=nb_read_frames,r_frame_rate", "-of", "json", str(path)], capture_output=True, text=True)
    st = json.loads(r.stdout)["streams"][0]
    return int(st["nb_read_frames"]), st["r_frame_rate"]


# ═══════════════ A ═══════════════

def test_escena_safe_no_abre_ventana():
    sc = [GfxScene(0, 0.0, 10.0, "R2", safe={"image": "x.png", "movement": "push"}),
          GfxScene(1, 10.0, 20.0, "R3", safe={"image": "y.png", "movement": "pan"})]
    plan = {"callouts": [{"text": "x", "start": 15.0, "duration": 2.5}], "transitions": {"1": {"kind": "cut", "frames": 0}}}
    w = sp.event_windows(plan, sc, FPS, 20.0)
    assert all(not (a <= 2.0 <= b) for a, b in w)                  # la escena 0 entera ya no es ventana
    assert sum(b - a for a, b in w) < 10.0
    viejo = sp.event_windows(plan, sc, FPS, 20.0, safe_windows=True)   # sin bake: el camino de F2 §4
    assert sum(b - a for a, b in viejo) == pytest.approx(20.0)


def test_bake_da_n_cuadros_exactos(tmp_path):
    img = _png(tmp_path / "s.png")
    for mov, n in (("push", 47), ("pan", 31), ("pull", 20), ("static", 12)):
        out = tmp_path / f"{mov}.mp4"
        sb.bake_scene(img, mov, [0.4, 0.6], n / FPS, n, out, width=W, height=H, fps=FPS)
        assert _probe(out) == (n, f"{FPS}/1")


def test_curva_del_push_igual_a_gsap():
    import math
    z, x0, y0 = sb.expresiones("push", 2.0, [0.45, 0.45], width=W, height=H, fps=FPS)
    env = {"math": math, "cos": math.cos, "PI": math.pi}
    for k in (0, 15, 60):
        zz = eval(z.replace("in", "k"), {**env, "k": k})
        assert zz == pytest.approx(1 + (gfx_rules.safe_push_scale - 1) * (0.5 - 0.5 * math.cos(math.pi * k / 60)))
        # la esquina visible deja fijo el origen (45 %, 45 %): ox·W = x0 + ox·W/z
        assert eval(x0.replace("in", "k"), {**env, "k": k}) + 0.45 * W / zz == pytest.approx(0.45 * W)
    assert sb.expresiones("pan", 2.0, [0.45, 0.45], width=W, height=H, fps=FPS)[1].startswith("(80.000000-")   # el
    # paneo y el alejar van centrados (como el templater): el origen solo cuenta en el push


def test_base_cocido_conserva_duracion_y_fps(tmp_path):
    base = _base(tmp_path / "base.mp4", 3.0)
    img = _png(tmp_path / "s.png")
    sc = [GfxScene(0, 0.0, 1.0, "R2"), GfxScene(1, 1.0, 2.2, "R3", safe={"image": str(img), "movement": "push"}),
          GfxScene(2, 2.2, 3.0, "R3", safe={"image": str(img), "movement": "static"})]
    rep = sb.bake(base, sc, tmp_path / "cocido.mp4", width=W, height=H, fps=FPS, workers=2)
    assert _probe(tmp_path / "cocido.mp4") == (90, f"{FPS}/1")
    assert rep["cuadros_cocidos"] == 36 + 24 and rep["cuadros_total"] == 90
    assert sb.bake(base, [GfxScene(0, 0.0, 3.0, "R2")], tmp_path / "nada.mp4", width=W, height=H, fps=FPS) is None
