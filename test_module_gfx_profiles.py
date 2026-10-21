"""test_module_gfx_profiles.py — F2 §0c: motor (gfx_config) + perfil de canal (gfx_profiles/*.json).
Correr: python -m pytest test_module_gfx_profiles.py -q
"""
import json
import sys
from dataclasses import fields

import pytest

import gfx_config as gc


def test_carga_ambos_perfiles_sin_tocar_codigo():
    mis, fin = gc.load_profile("misterio"), gc.load_profile("finanzas")
    rm, rf = gc.rules_from_profile(mis), gc.rules_from_profile(fin)
    assert rm.accent_hex == "#c2302f" and rf.accent_hex != rm.accent_hex          # F4: acento de la identidad del lab
    inv_f = {b.name: b for b in gc.inventory_from_profile(fin)}
    assert not inv_f["archive_clipping"].enabled and inv_f["archive_clipping"].max_per_cap == 0
    assert rf.archive_max_per_cap == 0 and rf.grain_opacity == 0.0
    assert gc.grade_variants(rf)["off"]["opacity"]["gr-grain"] == 0.0


def test_misterio_reproduce_la_calibracion_0b():
    """El perfil misterio = defaults del motor salvo lo que F2b §1 cambió por perfil (densidad 18 s, grano 0, viñeta 0.15)."""
    rm = gc.rules_from_profile(gc.load_profile("misterio"))
    engine = gc.GfxRules()
    diffs = {f.name for f in fields(gc.GfxRules) if getattr(rm, f.name) != getattr(engine, f.name)}
    assert diffs == {"interrupt_min_sec", "interrupt_max_sec", "grain_opacity", "vignette_opacity",
                     "mood_dark_flicker",                                  # PARADA 1: oscuridad sin parpadeos
                     "question_auto", "question_dim", "icon_px",           # F3: pregunta generada (70 %) + ícono L
                     "black_hold_sec", "peak_blocks",                      # F3: corte a negro 1 s + pico del cap
                     "accent_hex", "punch_scale", "anim_figure", "emphasis_stamp_px",
                     "question_max_words_auto", "identity_rules", "ticker_min_times",
                     "intensity_director", "fragment_director", "photo_first_zoom", "auto_icons",
                     "peak_word", "doc_clippings", "callout_no_repeat", "question_rubric",   # F4c: doctrina
                     "visual_critic",                                                         # F4e: crítico visual
                     "icon_literal_only", "critic_snapshot", "stamp_nouns_only"}, diffs       # F5b S4 · G1 · F5e
    assert (rm.interrupt_max_sec, rm.grain_opacity, rm.vignette_opacity) == (18.0, 0.0, 0.15)
    assert (rm.question_auto, rm.question_dim, rm.icon_px, rm.question_pause_sec) == (True, 0.7, 360, 3.0)


def test_perfil_activo_por_nicho_y_por_env(monkeypatch):
    monkeypatch.delenv("GFX_PROFILE", raising=False)
    assert gc.active_profile_name() == "misterio"          # nicho dark_history → misterio
    monkeypatch.setenv("GFX_PROFILE", "finanzas")
    assert gc.active_profile_name() == "finanzas"


def test_clave_desconocida_falla(tmp_path, monkeypatch):
    bad = json.loads(gc.profile_path("misterio").read_text(encoding="utf-8"))
    bad["tokens"]["acent_hex"] = "#000000"                  # typo
    (tmp_path / "typo.json").write_text(json.dumps(bad), encoding="utf-8")
    monkeypatch.setattr(gc, "GFX_PROFILES_DIR", tmp_path)
    with pytest.raises(ValueError, match="acent_hex"):
        gc.load_profile("typo")


def test_fuente_sin_font_face_falla(tmp_path, monkeypatch):
    bad = json.loads(gc.profile_path("finanzas").read_text(encoding="utf-8"))
    bad["fonts"]["callout"] = "Comic Sans MS"
    (tmp_path / "f.json").write_text(json.dumps(bad), encoding="utf-8")
    monkeypatch.setattr(gc, "GFX_PROFILES_DIR", tmp_path)
    with pytest.raises(ValueError, match="Comic Sans"):
        gc.load_profile("f")


def test_bloque_apagado_no_llega_al_prompt(monkeypatch):
    fin = gc.load_profile("finanzas")
    monkeypatch.setattr(gc, "GFX_INVENTORY", gc.inventory_from_profile(fin))
    txt = gc.render_inventory_for_prompt()
    assert "archive_clipping" not in txt and "evidence_zoom" not in txt and "data_callout" in txt
    assert "máx 4 por cap" in txt                           # el máximo sale del perfil


def test_css_con_perfil_finanzas(monkeypatch):
    import script_engine.gfx_project as gp
    rf = gc.rules_from_profile(gc.load_profile("finanzas"))
    monkeypatch.setattr(gp, "gfx_rules", rf)
    css = gp.render_css(2560, 1440)
    assert rf.accent_hex in css and "#c8102e" not in css


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
