"""test_module_gfx_anim.py — F2 §2: animaciones firma por tipo de bloque.
Correr: python -m pytest test_module_gfx_anim.py -q
"""
import sys

import pytest

import script_engine.gfx_project as gp
from script_engine.gfx_project import GfxScene, callout_anim, chars_html, write_project


def test_mapa_bloque_animacion():
    assert callout_anim("name") == callout_anim("place") == "cascade"
    assert callout_anim("year") == "stamp"
    assert callout_anim("figure") == gp.gfx_rules.anim_figure == "stamp"            # F4: cifras con sello (lab)


def test_cascade_parte_en_palabras_y_letras():
    h = chars_html("Nueva Orleans")
    assert h.count('class="w"') == 2 and h.count('class="ch"') == 12 and "&" not in h


@pytest.fixture
def project(tmp_path):
    (tmp_path / "public").mkdir()
    (tmp_path / "public" / "base.mp4").write_bytes(b"x")
    return tmp_path


def test_index_usa_las_tres_animaciones(project):
    plan = {"chapter_number": 2, "title_card": None, "evidence_zoom": None, "punch_in": [],
            "callouts": [{"text": "Nueva Orleans", "start": 1.0, "kind": "place", "duration": 2.5, "side": "left"},
                         {"text": "2005", "start": 4.0, "kind": "year", "duration": 2.5, "side": "right"},
                         {"text": "4.6 metros", "start": 7.0, "kind": "figure", "duration": 2.5, "side": "left"}],
            "count_up": {"value_text": "6,500", "unit": "personas", "start": 10.0},
            "archive_clippings": [{"kicker": "OPP", "headline": "Más de 500", "body": "", "start": 2.0, "duration": 5.0,
                                   "side": "left", "era_decade": 2000}]}
    write_project(plan, [GfxScene(0, 0.0, 15.0, "R3", "")], project, duration=15.0, width=2560, height=1440, fps=30)
    html = (project / "index.html").read_text(encoding="utf-8")
    assert f"stagger: {gp.gfx_rules.cascade_stagger}" in html                       # cascade (callout + recorte)
    assert '"#ar0 .ar-head .ch"' in html
    assert 'class="co-text serif stamp"' in html and "rotation: -3.0" in html      # stamp
    if gp.gfx_rules.anim_figure == "number_pop":                                       # golpe del contador solo con number_pop
        assert f"scale: {gp.gfx_rules.pop_from_scale}" in html and '"#cu-num"' in html
    assert "letterSpacing" not in html and "letter-spacing:" not in html.split("<style>")[1].split("</style>")[1]


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
