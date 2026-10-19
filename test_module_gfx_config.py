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
                 "count_up", "shot_transition", "punch_in", "grade",
                 "chapter_question", "source_tag"}                  # F2 §0d
    assert gc.VALID_BLOCKS == esperados
    # deterministas: el LLM no los elige
    assert "shot_transition" not in gc.LLM_BLOCKS and "grade" not in gc.LLM_BLOCKS
    assert "source_tag" not in gc.LLM_BLOCKS and "chapter_question" in gc.LLM_BLOCKS


def test_prompt_incluye_todos_los_bloques():
    txt = gc.render_inventory_for_prompt()
    for b in gc.GFX_INVENTORY:
        assert f"- {b.name} " in txt
    assert "NO lo elegís" in txt


def test_maximos_por_cap():
    assert gc.max_per_cap("data_callout") == 5             # F2 §1: techo 5/cap
    assert gc.max_per_cap("punch_in") == 2
    assert gc.max_per_cap("archive_clipping") == 2          # F2 §0b.6
    assert gc.clamp_count([1, 2, 3, 4, 5, 6], "data_callout") == [1, 2, 3, 4, 5]


def test_clamps():
    assert gc.clamp_callout_duration(99) == gc.gfx_rules.callout_dur_max
    assert gc.clamp_callout_duration(0.1) == gc.gfx_rules.callout_dur_min
    assert gc.clamp_box([1.4, -0.2, 0.9, 0.01]) == [0.75, 0.0, 0.25, 0.06]   # tope F1b 0.25
    assert gc.clamp_box(["x"]) is None
    assert gc.clamp_quality("looks") == "looks" and gc.clamp_quality("4k") == "looks"


def test_calibracion_f1b_vigente():
    r = gc.gfx_rules
    assert r.flash_peak == 0.3
    assert r.flash_max_per_cap == 2 and r.flash_min_gap_sec == 20.0
    assert r.callout_dur_min == 2.5 and r.archive_min_sec == 4.0 and r.count_hold_sec == 2.5
    assert r.zoom_box_max == 0.25 and r.zoom_label_margin_px >= 40
    assert {"A", "B", "C"} <= set(gc.GRADE_VARIANTS) and gc.GRADE_VARIANTS["C"]["intensity"] == 0.3   # recetas inactivas
    assert gc.GRADE_VARIANTS["B"]["opacity"]["gr-haze"] == 0.0
    assert gc.gfx_rules.css_grade_variant == gc.gfx_rules.grade_default    # alias F1b


def test_calibracion_f2_0b():
    r = gc.gfx_rules
    assert r.grade_default == "off"                                  # §0b.1
    off = gc.GRADE_VARIANTS["off"]["opacity"]
    assert off["gr-grain"] == 0.15 and off["gr-vignette"] == 0.20
    assert all(v == 0 for k, v in off.items() if k not in ("gr-grain", "gr-vignette"))
    assert r.title_dur == 3.0 and r.title_scale == 0.7 and r.title_fade_out == 0.4      # §0b.2
    assert r.punch_scale == 1.025 and r.punch_in_sec == 0.4 and r.punch_hold             # §0b.3
    assert r.transition_frames == {"R1": 3, "R2": 20, "R3": 30} and r.dip_frames == 10  # §0b.4
    assert r.zoom_hold_min_sec >= 1.0                                                   # §0b.5
    assert r.archive_dur == 6.0 and r.archive_max_per_cap == 2 and r.archive_scale == 0.68  # §0b.6 + ajuste
    assert r.callout_font == "Playfair Display SC" and r.callout_font_weight >= 700     # §0b.8
    assert r.accent_hex.startswith("#") and len(r.accent_hex) == 7                      # §0b.9


def test_acento_unico_en_css():
    from script_engine.gfx_project import render_css
    css = render_css(2560, 1440)
    assert "#c8102e" not in css.replace(gc.gfx_rules.accent_hex, "") or gc.gfx_rules.accent_hex == "#c8102e"
    assert css.count(gc.gfx_rules.accent_hex) >= 4


def test_ajustes_previos_al_ok_0b():
    """Ajustes de Omar antes del OK de §0b: looks por default, rampa del count_up, recorte ≤ 38 %."""
    import fase2b
    from script_engine.gfx_project import render_css
    assert gc.gfx_render.quality == "looks" and gc.gfx_render.debug_quality == "draft"
    assert fase2b._resolve_gfx_quality(None, False) == "looks"
    assert fase2b._resolve_gfx_quality(None, True) == "draft"
    assert fase2b._resolve_gfx_quality("looks", True) == "looks"       # la explícita manda
    assert gc.gfx_rules.count_dur == 1.2 and gc.gfx_rules.count_hold_sec == 2.5
    import re
    w = int(re.search(r"\.ar-paper \{[^}]*width: (\d+)px", render_css(2560, 1440)).group(1))
    assert w <= 0.30 * 2560 and gc.gfx_rules.archive_body_px == 40 and gc.gfx_rules.archive_body_lines == 2
    assert gc.gfx_rules.archive_head_max_words == 8 and not gc.gfx_rules.archive_body_default
    css = render_css(2560, 1440)
    assert "font-variant-ligatures: none" in css and "calc(2 * 1.3em)" in css


def test_default_off_y_cromo():
    assert gc.gfx_render.enable_gfx is False
    assert gc.chrome_strings(2) == frozenset({"CAPÍTULO 2", "DETALLE"})


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
