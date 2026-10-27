"""test_module_gfx_0d.py — F2 §0d: sfx, chapter_question y source_tag.
Correr: python -m pytest test_module_gfx_0d.py -q
"""
import sys

import pytest

import gfx_config as gc
from script_engine.gfx_project import GfxScene, write_project

WORDS = [{"word": w, "start": i * 0.5, "end": i * 0.5 + 0.4} for i, w in enumerate(
    "Ese día el huracán Katrina llegó a Nueva Orleans y el agua subió sin parar".split())]
NEXT = {"next.bullets[0]": "Generadores de respaldo fallan el 29 de agosto de 2005.",
        "next.bullets[1]": "Prisión sin luz ni ventilación.", "narration_ch03": "La prisión quedó a oscuras."}


def test_libreria_sfx_existe_y_perfil_la_referencia():
    wavs = {p.name for p in gc.SFX_DIR.glob("*.wav")}
    assert 8 <= len(wavs) <= 15                       # F4c R5: + 5 SFX propios de las categorías de reserva
    prof = gc.load_profile("misterio")
    assert {v["file"] for v in prof["sfx"].values()} <= wavs
    assert all(v["gain_db"] <= -18 for v in prof["sfx"].values())          # bajo la voz


def test_plantilla_question(tmp_path):
    (tmp_path / "public").mkdir()
    (tmp_path / "public" / "base.mp4").write_bytes(b"x")
    plan = {"chapter_number": 2, "title_card": None, "count_up": None, "archive_clippings": [], "evidence_zoom": None,
            "punch_in": [], "callouts": [],                  # F36 §D: sin source_tag ni dato suelto
            "chapter_question": {"text": "¿Por qué fallan los generadores?", "start": 7.5, "duration": 2.3,
                                 "keyword": "generadores"}}
    write_project(plan, [GfxScene(0, 0.0, 10.0, "R3", "")], tmp_path, duration=10.0, width=2560, height=1440, fps=30)
    html = (tmp_path / "index.html").read_text(encoding="utf-8")
    assert '<span class="kw">generadores</span>' in html and 'id="cq-dim"' in html


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
