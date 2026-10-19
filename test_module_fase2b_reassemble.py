"""test_module_fase2b_reassemble.py — F2 §3.4: huella de insumos por segmento (re-ensamble incremental).
Correr: python -m pytest test_module_fase2b_reassemble.py -q
"""
import sys
from types import SimpleNamespace

import pytest

import fase2b


@pytest.fixture
def cap(tmp_path):
    (tmp_path / "a.wav").write_bytes(b"a")
    (tmp_path / "t.json").write_text("[]", encoding="utf-8")
    (tmp_path / "ch04_flux_visual.mp4").write_bytes(b"v")
    (tmp_path / "gfx_plan_ch04.json").write_text('{"raw": {"callouts": []}}', encoding="utf-8")
    plan = SimpleNamespace(chapter_id="ch04", audio_path=tmp_path / "a.wav", timestamps_path=tmp_path / "t.json")
    return plan, tmp_path


FLAGS = {"gfx": True, "quality": "looks", "debug": False, "sfx": True, "sparse": True, "hook": None, "no_subs": False}


def test_huella_estable_sin_cambios(cap):
    plan, wd = cap
    assert fase2b._segment_hash(plan, wd, FLAGS) == fase2b._segment_hash(plan, wd, FLAGS)


def test_cambia_el_plan_gfx_del_cap(cap):
    plan, wd = cap
    h0 = fase2b._segment_hash(plan, wd, FLAGS)
    (wd / "gfx_plan_ch04.json").write_text('{"raw": {"callouts": [1]}}', encoding="utf-8")
    assert fase2b._segment_hash(plan, wd, FLAGS) != h0


def test_cambian_los_flags_o_el_visual(cap):
    plan, wd = cap
    h0 = fase2b._segment_hash(plan, wd, FLAGS)
    assert fase2b._segment_hash(plan, wd, {**FLAGS, "sparse": False}) != h0
    (wd / "ch04_flux_visual.mp4").write_bytes(b"vv")                  # cambia el tamaño del visual
    assert fase2b._segment_hash(plan, wd, FLAGS) != h0


def test_huella_post_build_coincide_con_la_del_reensamble(cap):
    """Regresión (revisor §3.4): el visual y el box del zoom nacen DURANTE el build; la huella del
    manifiesto se toma después, así el re-ensamble siguiente la encuentra igual."""
    plan, wd = cap
    (wd / "ch04_flux_visual.mp4").unlink()
    antes = fase2b._segment_hash(plan, wd, FLAGS)                      # pre-build: falta el visual
    (wd / "ch04_flux_visual.mp4").write_bytes(b"v")                    # el build lo crea
    (wd / "gfx_zoom_box_ch04.json").write_text("{}", encoding="utf-8")
    guardada = fase2b._segment_hash(plan, wd, FLAGS)                   # lo que se guarda (post-build)
    assert guardada != antes and fase2b._segment_hash(plan, wd, FLAGS) == guardada


def test_otro_cap_no_afecta(cap):
    plan, wd = cap
    h0 = fase2b._segment_hash(plan, wd, FLAGS)
    (wd / "gfx_plan_ch05.json").write_text('{"raw": {"x": 1}}', encoding="utf-8")
    assert fase2b._segment_hash(plan, wd, FLAGS) == h0


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
