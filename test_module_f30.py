"""
test_module_f30.py — F30: render rápido, el navegador solo pinta bloques (sin red; ffmpeg local con videos sintéticos
chicos). A: la escena safe no abre ventana y la cuece ffmpeg (cuadros exactos, el base conserva duración y fps).
B: las transiciones no abren ventana y las hace el stitch (grafo esperado; la que cae en una ventana la dibuja HF y
no el stitch; sin aire para su fundido, entra a la ventana; duración exacta con cut_punch, dissolve, dip y flash).
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


# ═══════════════ B ═══════════════

def _cuatro():
    sc = [GfxScene(0, 0.0, 4.0, "R2"), GfxScene(1, 4.0, 8.0, "R3"), GfxScene(2, 8.0, 12.0, "R3"),
          GfxScene(3, 12.0, 16.0, "R3")]
    tr = {"1": {"kind": "cut", "frames": 0}, "2": {"kind": "dissolve", "frames": 20}, "3": {"kind": "dip", "frames": 10}}
    return sc, tr


def test_grafo_del_stitch_4_escenas_cut_dissolve_dip():
    sc, tr = _cuatro()
    plan = {"transitions": tr, "chapter_question": {"start": 15.0, "duration": 1.0}}
    w = sp.event_windows(plan, sc, FPS, 16.0)
    assert w == [(14.5, 16.0)]                                       # las transiciones ya no abren ventana
    trs = sp.stitch_transitions(plan, sc, w)
    assert [(c, t["kind"]) for c, t in trs] == [(4.0, "cut"), (8.0, "dissolve"), (12.0, "dip")]
    _, _, _, offs = sp.compose_sparse(plan, sc, w, FPS)
    graph, last = sp.stitch_graph(sp.stitch_segments(offs, 16.0, FPS, trs), FPS, 1280, 720)
    P = ",setpts=PTS-STARTPTS,fps=30,format=yuv420p,settb=AVTB"
    assert graph == [
        f"[0:v]trim=start_frame=0:end_frame=120{P}[s0]",                       # el corte seco: dos tramos
        f"[0:v]trim=start_frame=120:end_frame=240{P}[s1]",
        f"[0:v]trim=start_frame=239:end_frame=240{P},tpad=stop_mode=clone:stop=19[s2a]",   # último cuadro saliente
        f"[0:v]trim=start_frame=240:end_frame=260{P}[s2b]",
        "[s2a][s2b]xfade=transition=fade:duration=0.666667:offset=0[s2]",
        f"[0:v]trim=start_frame=260:end_frame=360{P}[s3]",
        f"[0:v]trim=start_frame=359:end_frame=360{P},tpad=stop_mode=clone:stop=4,fade=t=out:st=0:d=0.166667[s4]",
        f"[0:v]trim=start_frame=365:end_frame=370{P},fade=t=in:st=0:d=0.166667[s5]",
        f"[0:v]trim=start_frame=370:end_frame=435{P}[s6]",
        f"[0:v]trim=start_frame=435:end_frame=439{P}[s7a]",                     # unión base → HF (4 cuadros)
        f"[1:v]trim=start_frame=0:end_frame=4{P}[s7b]",
        "[s7a][s7b]xfade=transition=fade:duration=0.133333:offset=0[s7]",
        f"[1:v]trim=start_frame=4:end_frame=45{P}[s8]",
        "[s0][s1][s2][s3][s4][s5][s6][s7][s8]concat=n=9:v=1:a=0[cat]",
    ] and last == "cat"


def test_transicion_dentro_de_una_ventana_la_dibuja_hf_y_no_el_stitch():
    sc, tr = _cuatro()
    plan = {"transitions": tr, "callouts": [{"text": "x", "start": 7.0, "duration": 2.5}]}   # cruza el corte de 8.0
    w = sp.event_windows(plan, sc, FPS, 16.0)
    assert any(a <= 8.0 < b for a, b in w)
    kinds = [(c, t["kind"]) for c, t in sp.stitch_transitions(plan, sc, w)]
    assert (8.0, "dissolve") not in kinds and (4.0, "cut") in kinds and (12.0, "dip") in kinds
    _, _, tr_s, _ = sp.compose_sparse(plan, sc, w, FPS)              # HF la sigue dibujando en su ventana
    assert any(v["kind"] == "dissolve" for v in tr_s.values())


def test_transicion_sin_aire_entra_a_la_ventana():
    sc = [GfxScene(0, 0.0, 4.0, "R2"), GfxScene(1, 4.0, 4.4, "R3"), GfxScene(2, 4.4, 9.0, "R3")]
    plan = {"transitions": {"1": {"kind": "dissolve", "frames": 20}, "2": {"kind": "cut", "frames": 0}}}
    w = sp.event_windows(plan, sc, FPS, 9.0)
    assert any(a <= 4.0 < b for a, b in w)                           # el dissolve no entra en 0.4 s: lo hace HF


def test_stitch_duracion_exacta(tmp_path):
    base = _base(tmp_path / "base.mp4", 16.0)
    hf = _base(tmp_path / "hf.mp4", 2.0)
    sc, tr = _cuatro()
    tr["2"] = {"kind": "flash", "frames": 3}
    plan = {"transitions": {**tr, "1": {"kind": "cut_punch", "frames": 0}},
            "chapter_question": {"start": 15.0, "duration": 1.0}}
    w = sp.event_windows(plan, sc, FPS, 16.0)
    trs = sp.stitch_transitions(plan, sc, w)
    _, _, _, offs = sp.compose_sparse(plan, sc, w, FPS)
    out = tmp_path / "cap.mp4"
    sp.stitch(base, hf, w, offs, 16.0, out, width=W, height=H, fps=FPS, vignette=None, grain=None, grain_opacity=0.0,
              transitions=trs)
    n, r = _probe(out)
    assert abs(n - 16 * FPS) <= 1 and r == f"{FPS}/1"
