"""test_module_gfx_config.py — F1 capa gráfica: inventario inmutable, prompt y clamps.
Correr: python -m pytest test_module_gfx_config.py -q   (o python test_module_gfx_config.py)
"""
import dataclasses
import sys

import pytest

import gfx_config as gc


def test_inventario_es_inmutable():
    assert isinstance(gc.GFX_INVENTORY, tuple)
    with pytest.raises(dataclasses.FrozenInstanceError):
        gc.GFX_INVENTORY[0].name = "otro"  # type: ignore[misc]
    with pytest.raises(dataclasses.FrozenInstanceError):
        gc.gfx_render.quality = "looks"  # type: ignore[misc]


def test_inventario_cubre_doc_maestro_v1():
    esperados = {"title_card", "data_callout", "archive_clipping", "evidence_zoom",
                 "count_up", "shot_transition", "punch_in", "grade"}
    assert gc.VALID_BLOCKS == esperados
    # deterministas: el LLM no los elige
    assert "shot_transition" not in gc.LLM_BLOCKS and "grade" not in gc.LLM_BLOCKS


def test_prompt_incluye_todos_los_bloques():
    txt = gc.render_inventory_for_prompt()
    for b in gc.GFX_INVENTORY:
        assert f"- {b.name} " in txt
    assert "NO lo elegís" in txt


def test_maximos_por_cap():
    assert gc.max_per_cap("data_callout") == 3
    assert gc.max_per_cap("punch_in") == 2
    assert gc.max_per_cap("archive_clipping") == 1
    assert gc.clamp_count([1, 2, 3, 4, 5, 6], "data_callout") == [1, 2, 3]


def test_clamps():
    assert gc.clamp_callout_duration(99) == gc.gfx_rules.callout_dur_max
    assert gc.clamp_callout_duration(0.1) == gc.gfx_rules.callout_dur_min
    assert gc.clamp_box([1.4, -0.2, 0.9, 0.01]) == [0.75, 0.0, 0.25, 0.06]   # tope F1b 0.25
    assert gc.clamp_box(["x"]) is None
    assert gc.clamp_quality("looks") == "looks" and gc.clamp_quality("4k") == "draft"


def test_calibracion_f1b():
    r = gc.gfx_rules
    assert r.transition_frames == {"R1": 3, "R2": 12, "R3": 20} and r.flash_peak == 0.3
    assert r.flash_max_per_cap == 2 and r.flash_min_gap_sec == 20.0
    assert r.callout_dur_min == 2.5 and r.archive_min_sec == 4.0 and r.count_hold_sec == 2.5
    assert r.zoom_box_max == 0.25 and r.zoom_label_margin_px >= 40
    assert set(gc.GRADE_VARIANTS) == {"A", "B", "C"} and gc.GRADE_VARIANTS["C"]["intensity"] == 0.3
    assert gc.GRADE_VARIANTS["B"]["opacity"]["gr-haze"] == 0.0
    assert gc.gfx_rules.css_grade_variant == "B"                 # elección de Omar (F1b §2.4)


def test_default_off_y_cromo():
    assert gc.gfx_render.enable_gfx is False
    assert gc.chrome_strings(2) == frozenset({"CAPÍTULO 2", "DETALLE"})


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
