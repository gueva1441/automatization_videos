"""test_module_gfx_sparse.py — F2 §3.1: render disperso (ventanas, timeline concatenado, cosido).
Correr: python -m pytest test_module_gfx_sparse.py -q
"""
import subprocess
import sys

import numpy as np
import pytest

from script_engine import gfx_sparse as sp
from script_engine.gfx_project import GfxScene

SCENES = [GfxScene(0, 0.0, 10.0, "R3"), GfxScene(1, 10.0, 20.0, "R2"), GfxScene(2, 20.0, 40.0, "R3")]
PLAN = {"title_card": {"kicker": "CAPÍTULO 2", "title": "x"}, "callouts": [{"text": "a", "start": 25.0, "kind": "figure", "duration": 2.5}],
        "count_up": None, "archive_clippings": [], "evidence_zoom": None, "punch_in": [33.0], "chapter_question": None}


def test_ventanas_cubren_eventos_cortes_y_punch_hasta_el_corte():
    w = sp.event_windows(PLAN, SCENES, 30, 40.0, transition_windows=True)   # F30 §B: el camino de antes (con el stitch, test_module_f30)
    inside = lambda t: any(a <= t < b for a, b in w)              # noqa: E731
    assert inside(0.0) and inside(2.9)                           # title card
    assert inside(9.95) and inside(10.5)                         # corte R2 (freeze del saliente + 20 f)
    assert inside(25.0) and inside(27.4)                         # callout
    assert inside(33.0) and inside(39.9)                         # punch se sostiene hasta el corte (fin de cap)
    assert not inside(15.0)                                      # tramo sin eventos → base
    assert all(abs(x * 30 - round(x * 30)) < 1e-3 for ab in w for x in ab)          # alineado a frame


def test_timeline_concatenado_y_cortes_en_las_uniones():
    w = sp.event_windows(PLAN, SCENES, 30, 40.0, transition_windows=True)   # F30 §B: el camino de antes (con el stitch, test_module_f30)
    p, sc, tr, offs = sp.compose_sparse(PLAN, SCENES, w, 30)
    a, b, o = next(x for x in offs if x[0] <= 25.0 < x[1])
    assert p["callouts"][0]["start"] == pytest.approx(o + 25.0 - a, abs=1e-3)
    assert all(abs(s.end - s.start) > 0 for s in sc)
    joins = [k for k, v in tr.items() if v.get("window_join")]
    assert joins and all(tr[k]["kind"] == "cut" for k in joins)   # nunca disolvencia entre ventanas
    real = [v for v in tr.values() if not v.get("window_join") and v["kind"] != "cut"]
    assert any(v["rank"] == "R2" for v in real)                   # el corte real conserva su transición


def test_cosido_sin_huecos_y_duracion_exacta(tmp_path):
    base, hf = tmp_path / "b.mp4", tmp_path / "h.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "color=c=gray:s=64x36:r=30:d=6",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", str(base)], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "color=c=white:s=64x36:r=30:d=2",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", str(hf)], check=True)
    windows = [(2.0, 4.0)]
    offsets = [(2.0, 4.0, 0.0)]
    out = tmp_path / "o.mp4"
    sp.stitch(base, hf, windows, offsets, 6.0, out, width=64, height=36, fps=30, vignette=None, grain=None, grain_opacity=0)
    d = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(out)],
                             capture_output=True, text=True).stdout)
    assert d == pytest.approx(6.0, abs=0.05)
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(out), "-f", "rawvideo", "-pix_fmt", "gray", "-"],
                         capture_output=True).stdout
    y = np.frombuffer(raw, np.uint8).reshape(-1, 36, 64).mean(axis=(1, 2))
    assert y[30] < 140 and y[90] > 230 and y[150] < 140           # base · ventana HF · base
    assert 140 <= y[61] <= 230                                    # fundido de 4 cuadros en la unión


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
