"""test_module_gfx_router.py — F2 §4: router anti-deformación (riesgo + movimiento seguro HyperFrames).
Correr: python -m pytest test_module_gfx_router.py -q
"""
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

import fase2b
from script_engine import gfx_sparse as sp
from script_engine.depth_probe import deform_risk, route_images
from script_engine.gfx_project import GfxScene, write_project
from script_engine.parallax_animator_v2 import clamp_for_risk


def test_riesgo_por_veredicto():
    assert deform_risk({"center_minus_border": 0.3}, {"categoria": "cara_closeup"}) == "high"
    assert deform_risk({"center_minus_border": 0.3}, {"categoria": "sujeto_con_fondo"}) == "low"
    assert deform_risk(None, None) == "low"
    assert route_images(["a", "b"], {}, {"a": {"categoria": "cara_closeup"}}) == {"a": "high", "b": "low"}


def test_mid_atenua_depthflow():
    spec = {"movement": "orbital", "intensity": 1.2, "steady": 0.3, "dof": False}
    out = clamp_for_risk(spec, "mid")
    assert out["intensity"] == 0.85 and out["movement"] == "horizontal"
    assert clamp_for_risk(spec, "low") is spec


@pytest.fixture
def project(tmp_path):
    (tmp_path / "public").mkdir()
    (tmp_path / "public" / "base.mp4").write_bytes(b"x")
    img = tmp_path / "img.png"
    img.write_bytes(b"png")
    return tmp_path, img


@pytest.mark.parametrize("mv,needle", [("push", "scale: 1.08"), ("pan", "x: ")])
def test_escena_segura_tapa_el_clip_con_la_imagen(project, mv, needle):
    proj, img = project
    sc = [GfxScene(0, 0.0, 5.0, "R3", ""), GfxScene(1, 5.0, 10.0, "R2", "", "right",
                                                   {"image": str(img), "movement": mv, "risk": "high"})]
    plan = {"chapter_number": 2, "title_card": None, "callouts": [], "count_up": None, "archive_clippings": [],
            "evidence_zoom": None, "punch_in": []}
    write_project(plan, sc, proj, duration=10.0, width=2560, height=1440, fps=30)
    html = (proj / "compositions" / "scene_02.html").read_text(encoding="utf-8")
    assert 'id="sf02"' in html and needle in html and (proj / "public" / "safe" / "safe_02.png").exists()
    assert 'id="sf01"' not in (proj / "compositions" / "scene_01.html").read_text(encoding="utf-8")


def test_freeze_de_la_escena_siguiente_es_la_imagen_segura(project):
    """La disolvencia que SALE de una escena segura parte de su imagen fija en el estado final (no del DepthFlow)."""
    proj, img = project
    sc = [GfxScene(0, 0.0, 5.0, "R3", "", "right", {"image": str(img), "movement": "push", "risk": "high"}),
          GfxScene(1, 5.0, 10.0, "R3", "")]
    plan = {"chapter_number": 2, "title_card": None, "callouts": [], "count_up": None, "archive_clippings": [],
            "evidence_zoom": None, "punch_in": []}
    write_project(plan, sc, proj, duration=10.0, width=2560, height=1440, fps=30)
    html = (proj / "compositions" / "scene_02.html").read_text(encoding="utf-8")
    assert 'src="public/cuts/freeze_02.png"' in html and "scale(1.08)" in html


def test_disperso_incluye_la_escena_segura_entera():
    sc = [GfxScene(0, 0.0, 10.0), GfxScene(1, 10.0, 20.0, "R3", "", "right", {"image": "x", "movement": "push"}),
          GfxScene(2, 20.0, 40.0)]
    plan = {"title_card": None, "callouts": [], "count_up": None, "archive_clippings": [], "evidence_zoom": None,
            "punch_in": [], "chapter_question": None}
    w = sp.event_windows(plan, sc, 30, 40.0)
    assert any(a <= 10.0 and b >= 20.0 for a, b in w)
    _, scenes_s, _, _ = sp.compose_sparse(plan, sc, w, 30)
    assert sum(1 for s in scenes_s if s.safe) == 1


def test_route_safe_orleans_sin_llamadas_nuevas():
    """Orleans: solo hay veredictos de las candidatas del gate de zoom; ninguna es retrato → 0 high."""
    vid = "ba6c3cac-a091-41c0-8dad-afd2f4364747"
    assets = fase2b.OUTPUT_DIR / vid / "assets"
    if not (assets / "zoom_verdicts.json").exists():
        pytest.skip("sin assets de Orleans")
    imgs = sorted((assets / "ch02_flux").glob("*.png"))
    assert imgs
    plan = SimpleNamespace(engine="flux", chapter_id="ch02", asset_paths=imgs)
    safe, counts = fase2b._route_safe([plan], vid, {})
    assert counts["high"] == 0 and counts["low"] == len(imgs) and safe == {}


def test_kenburns_registrado_pasa_a_movimiento_seguro(tmp_path):
    base = tmp_path / "ch02_flux_visual.mp4"
    base.with_suffix(".kenburns.json").write_text("[1]", encoding="utf-8")
    plan = SimpleNamespace(engine="flux", asset_paths=[Path("a.png"), Path("b.png")])
    out = fase2b._safe_scenes_for(plan, base, {})
    assert out == {1: {"image": "b.png", "movement": "push", "risk": "kenburns"}}
    assert fase2b._safe_scenes_for(plan, base, None) is None          # --no-safe-router


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
