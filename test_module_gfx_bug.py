"""F4b §0.3: marca del canal (gfx_bug) — solo desde el perfil, dónde se esconde, cosido FFmpeg con la marca y el cierre."""
from __future__ import annotations

import subprocess

import numpy as np


from script_engine import gfx_bug as gb

SVG = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" class="gfx-icon">'
       '<path class="ic-fill" fill="#e8e0cc" d="M40 20h120v170H40z"/><g id="flame" fill="#e8a84a"><path d="M90 90h20v20H90z"/></g></svg>')


def test_solo_desde_el_perfil(tmp_path, monkeypatch):
    assert gb.config({}) is None and gb.config({"channel_bug": {"enabled": False, "svg": "x.svg"}}) is None
    (tmp_path / "bug").mkdir()
    (tmp_path / "bug" / "b.svg").write_text(SVG, encoding="utf-8")
    monkeypatch.setattr(gb, "GFX_PROFILES_DIR", tmp_path)
    cfg = gb.config({"channel_bug": {"enabled": True, "svg": "bug/b.svg"}})
    assert cfg["opacity"] == 0.55 and cfg["height_frac"] == 0.04 and cfg["outro_sec"] == 2.5
    assert gb.config({"channel_bug": {"enabled": True, "svg": "bug/no.svg"}}) is None


def test_donde_se_esconde():
    plan = {"title_card": {"title": "x"}, "chapter_question": {"start": 90.0, "duration": 3.0},
            "black_hold": {"start": 93.0, "duration": 1.0}, "water_level": {"start": 30.0, "duration": 4.5},
            "callouts": [{"start": 50.0, "duration": 2.5, "side": "left"}, {"start": 60.0, "duration": 2.5, "side": "right"}],
            "archive_clippings": [], "emphasis": []}
    w = gb.hide_windows(plan, 94.0)
    assert (0.0, round(gb.gfx_rules.title_dur + 0.2, 3)) == w[0]
    assert (30.0, 34.5) in w and (50.0, 52.5) in w and all(not (a <= 61.0 <= b) for a, b in w)   # derecha: no se esconde
    assert (90.0, 94.0) in w                                                                       # pregunta + negro juntos
    ex = gb.visibility_expr([(10.0, 12.0)])
    v = lambda T: max(min(max((10.0 - T) / 0.3, 0), 1), min(max((T - 12.0) / 0.3, 0), 1))  # noqa: E731
    assert "clip((10.000-T)/0.3,0,1)" in ex and v(5) == 1 and v(11) == 0


def test_cosido_con_marca_y_cierre(tmp_path, monkeypatch):
    """Video negro de 4 s: la marca aparece arriba a la izquierda (sin bloques) y el cierre pone el encapuchado grande."""
    from script_engine import gfx_sparse as sp
    W, H, FPS = 640, 360, 30
    base = tmp_path / "base.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"color=c=0x202020:s={W}x{H}:r={FPS}:d=4",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", str(base)], check=True)
    (tmp_path / "bug").mkdir()
    (tmp_path / "bug" / "b.svg").write_text(SVG, encoding="utf-8")
    monkeypatch.setattr(gb, "GFX_PROFILES_DIR", tmp_path)
    cfg = gb.config({"channel_bug": {"enabled": True, "svg": "bug/b.svg", "height_frac": 0.2, "outro_sec": 1.5,
                                     "outro_black_sec": 0.5}})
    plan = {"callouts": [], "archive_clippings": [], "emphasis": [], "outro_bug": {"start": 2.0, "duration": 2.0}}
    bug = {"cfg": cfg, "plan": plan, "intro": False, "corner_pngs": gb.pngs(cfg, int(H * 0.2), tmp_path / "png"),
           "outro_t0": 2.0, "visible_until": 2.0, "outro_pngs": gb.pngs(cfg, int(H * 0.25), tmp_path / "png")}
    out = tmp_path / "out.mp4"
    sp.stitch(base, base, [(0.0, 0.0)], [], 4.0, out, width=W, height=H, fps=FPS, vignette=None, grain=None,
              grain_opacity=0.0, bug=bug)

    def fr(t):
        raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t), "-i", str(out), "-frames:v", "1", "-f", "rawvideo",
                              "-pix_fmt", "gray", "-"], capture_output=True, check=True).stdout
        return np.frombuffer(raw, np.uint8).reshape(H, W).astype(float)
    f1 = fr(1.0)
    x, y = int(W * 0.03), int(H * 0.035)
    assert f1[y:y + 60, x:x + 60].mean() > f1[200:260, 300:360].mean() + 5        # marca visible en la esquina
    f2 = fr(2.6)
    assert f2[:40, :].mean() < 5 and f2[H // 2 - 20:H // 2 + 20, W // 2 - 20:W // 2 + 20].mean() > 20   # cierre: negro + figura al centro
    assert fr(3.8).mean() < 3                                                     # negro final
