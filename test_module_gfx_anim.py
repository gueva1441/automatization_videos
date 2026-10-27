"""test_module_gfx_anim.py — F2 §2: animaciones firma por tipo de bloque.
Correr: python -m pytest test_module_gfx_anim.py -q
"""
import sys

import pytest

import script_engine.gfx_project as gp
from script_engine.gfx_project import GfxScene, chars_html, write_project


def test_cascade_parte_en_palabras_y_letras():
    h = chars_html("Nueva Orleans")
    assert h.count('class="w"') == 2 and h.count('class="ch"') == 12 and "&" not in h


@pytest.fixture
def project(tmp_path):
    (tmp_path / "public").mkdir()
    (tmp_path / "public" / "base.mp4").write_bytes(b"x")
    return tmp_path


def test_index_usa_la_cascada_del_recorte(project):
    plan = {"chapter_number": 2, "title_card": None, "evidence_zoom": None, "punch_in": [],
            "callouts": [],                                   # F36 §D: sin dato suelto ni contador
            "archive_clippings": [{"kicker": "OPP", "headline": "Más de 500", "body": "", "start": 2.0, "duration": 5.0,
                                   "side": "left", "era_decade": 2000}]}
    write_project(plan, [GfxScene(0, 0.0, 15.0, "R3", "")], project, duration=15.0, width=2560, height=1440, fps=30)
    html = (project / "index.html").read_text(encoding="utf-8")
    assert f"stagger: {gp.gfx_rules.cascade_stagger}" in html                       # cascade (recorte)
    assert '"#ar0 .ar-head .ch"' in html
    assert "letterSpacing" not in html and "letter-spacing:" not in html.split("<style>")[1].split("</style>")[1]


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
