"""test_module_gfx_cues.py — F1b: hoja de cues, overlay --gfx-debug, página de revisión, plan de transiciones.
Correr: python -m pytest test_module_gfx_cues.py -q
"""
import sys

import pytest

import script_engine.gfx_project as gp
from script_engine.gfx_project import GfxScene, cue_events, plan_transitions, write_project
from script_engine.gfx_review import write_cues, write_review

PLAN = {"chapter_number": 2, "title_card": {"kicker": "CAPÍTULO 2", "title": "La Tormenta Perfecta"},
        "callouts": [{"text": "4.6 metros", "start": 5.0, "kind": "figure"}], "count_up": None,
        "archive_clipping": None, "evidence_zoom": None, "punch_in": [5.0]}
ONE = [GfxScene(0, 0.0, 10.0, "R3", "")]


@pytest.fixture
def project(tmp_path):
    (tmp_path / "public").mkdir()
    (tmp_path / "public" / "base.mp4").write_bytes(b"x")
    return tmp_path


def test_debug_nunca_sin_flag(project):
    write_project(PLAN, ONE, project, duration=10.0, width=2560, height=1440, fps=30)
    assert 'id="dbg"' not in (project / "index.html").read_text(encoding="utf-8")


def test_debug_con_flag(project):
    write_project(PLAN, ONE, project, duration=10.0, width=2560, height=1440, fps=30, debug=True)
    html = (project / "index.html").read_text(encoding="utf-8")
    assert 'id="dbg"' in html and "dbg-tc" in html and "scene_01" in html and "data_callout" in html


def test_cue_events_ordenados_y_completos():
    ev = cue_events(PLAN, ONE, 30)
    assert [e["t"] for e in ev] == sorted(e["t"] for e in ev)
    blocks = {e["block"] for e in ev}
    assert {"title_card", "data_callout", "punch_in"} <= blocks


def test_plan_transiciones_r1_flash_con_tope(monkeypatch):
    scenes = [GfxScene(0, 0, 5), GfxScene(1, 5, 10, "R1"), GfxScene(2, 10, 30, "R1"),
              GfxScene(3, 30, 40, "R1"), GfxScene(4, 40, 50, "R2"), GfxScene(5, 50, 60, "R3")]
    monkeypatch.setattr(gp, "gfx_rules", gp.gfx_rules.__class__(flash_max_per_cap=2, flash_min_gap_sec=20.0))
    tr = plan_transitions(scenes)
    assert tr[1]["kind"] == "flash"
    assert tr[2]["kind"] == "cut_punch"          # a 5 s del flash anterior
    assert tr[3]["kind"] == "flash"              # a 25 s → segundo y último flash
    assert tr[4]["kind"] == tr[5]["kind"] == "dissolve"


def test_corte_seco_despues_del_zoom():
    scenes = [GfxScene(0, 0, 5, "R3"), GfxScene(1, 5, 10, "R2"), GfxScene(2, 10, 20, "R3")]
    tr = plan_transitions(scenes, zoom_scene_idx=0)
    assert tr[1]["kind"] == "cut" and tr[2]["kind"] in ("dissolve", "dip")


def test_write_cues_y_review(tmp_path):
    ev = cue_events(PLAN, ONE, 30)
    md = write_cues("ch02", ev, ["callout omitido (x)", "  plan: {...}"], [[0.0, 36.0]], 12.3, tmp_path)
    txt = md.read_text(encoding="utf-8")
    assert "| 00:05.0 | data_callout | «4.6 metros»" in txt
    assert "callout omitido" in txt and "plan:" not in txt and "00:36.0" in txt and "12.3 s" in txt
    page = write_review("ch02", tmp_path / "ch02_segment_only.mp4", tmp_path)
    html = page.read_text(encoding="utf-8")
    assert 'src="ch02_segment_only.mp4"' in html and "copiar nota" in html and "cdn" not in html.lower()


def test_freeze_es_el_plano_saliente(tmp_path):
    """Regresión F2 §0b.4: rojo 0–1 s, azul 1–2 s @30 fps → el freeze del corte en 1.0 s debe ser ROJO."""
    import subprocess
    import numpy as np
    vid = tmp_path / "rb.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "color=c=red:s=64x36:r=30:d=1",
                    "-f", "lavfi", "-i", "color=c=blue:s=64x36:r=30:d=1", "-filter_complex", "[0:v][1:v]concat=n=2:v=1",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", str(vid)], check=True)
    for cut in (1.0, 1.0 + 1 / 3000):              # incluso con un corte "sucio" de redondeo
        out = tmp_path / "fz.png"
        assert gp._extract_freeze(vid, cut - 1.5 / 30, out)
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(out), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                             capture_output=True).stdout
        r, g, b = np.frombuffer(raw, np.uint8).reshape(-1, 3).mean(axis=0)
        assert r > 150 and b < 100, (cut, r, g, b)


def test_review_sin_cues_no_rompe(tmp_path):
    assert write_review("ch09", tmp_path / "x.mp4", tmp_path) is None


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
