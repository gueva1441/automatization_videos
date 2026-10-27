"""test_module_gfx_emphasis.py — F2b §2: léxico de moods + énfasis de palabra (regex, sin LLM).
Correr: python -m pytest test_module_gfx_emphasis.py -q
"""
import sys

import pytest

import gfx_config as gc
import script_engine.gfx_director as gd
from script_engine.gfx_literal_lock import lock, plan_strings
from script_engine.gfx_project import GfxScene, cue_events, write_project


def _words(text: str, step: float = 1.0) -> list[dict]:
    return [{"word": w, "start": i * step, "end": i * step + .9 * step} for i, w in enumerate(text.split())]


CTX = {"chapter_number": 2, "facts": [], "skeleton": {}, "eligible": {}, "sources": {}}


def test_lexico_activo_tiene_4_categorias_con_25_disparadores():
    moods = gc.active_moods()
    propias = {k for k, m in moods.items() if m["layer"] != gc.MINIMAL_MOOD_LAYER}
    assert propias == {"veneno_enfermedad", "agua", "muerte", "oscuridad_encierro"}
    assert all(len(moods[k]["triggers"]) >= 25 and moods[k]["layer"] in gc.VALID_MOOD_LAYERS for k in propias)
    # F4c R5: las 5 de reserva pasan a activas con capa mínima (ya no hay reserva inactiva). F36 §D: sin su sfx propio
    minimas = set(moods) - propias
    assert minimas == {"fuego", "caos_gritos", "radiacion_quimico", "frio_abandono", "silencio"}
    assert not any("sfx" in moods[k] for k in moods)                           # huérfana del perfil, sacada al cargar
    assert not {k for k, v in gc.ACTIVE_PROFILE["moods"].items() if not v["active"]}


def test_perfil_rechaza_mood_activo_flaco(tmp_path, monkeypatch):
    import json
    prof = json.loads(gc.profile_path("misterio").read_text(encoding="utf-8"))
    prof["moods"]["fuego"].update(active=True, layer=None)  # sin capa (la mínima no exige 25 disparadores)
    prof["moods"]["agua"]["triggers"]["agua"] = 5            # peso fuera de 1–3
    monkeypatch.setattr(gc, "GFX_PROFILES_DIR", tmp_path)
    (tmp_path / "x.json").write_text(json.dumps(prof, ensure_ascii=False), encoding="utf-8")
    with pytest.raises(ValueError, match="moods.fuego") as e:
        gc.load_profile("x")
    assert "moods.agua.triggers" in str(e.value)


def test_lock_y_cues_y_templater(tmp_path):
    plan = {"chapter_number": 2, "title_card": None, "callouts": [], "count_up": None, "archive_clippings": [],
            "evidence_zoom": None, "punch_in": [],
            "emphasis": [{"word": "cadáveres", "category": "muerte", "layer": "muerte", "icon": None, "start": 2.0,
                          "duration": 2.5, "side": "left", "stamp": True, "sid": 0},
                         {"word": "inventada", "category": "agua", "layer": "agua", "icon": None, "start": 6.0,
                          "duration": 2.5, "side": "right", "stamp": True, "sid": 1}]}
    ok, rej = lock(plan, {"narration_ch02": "Vieron cadáveres en el agua."}, chapter_number=2)
    # F37 §B.4: el candado ya no mira los sellos (son de clima: no repiten la voz a propósito)
    assert [e["word"] for e in ok["emphasis"]] == ["cadáveres", "inventada"] and not rej
    ok["emphasis"] = ok["emphasis"][:1]
    assert "cadáveres" in plan_strings(ok)
    ev = cue_events(ok, [GfxScene(0, 0.0, 10.0)], 30)
    assert any(e["block"] == "keyword_emphasis:muerte" and e["text"] == "cadáveres" for e in ev)
    (tmp_path / "public").mkdir()
    (tmp_path / "public" / "base.mp4").write_bytes(b"x")
    for layer in sorted(gc.VALID_MOOD_LAYERS):
        ok["emphasis"][0]["layer"] = layer
        write_project(ok, [GfxScene(0, 0.0, 10.0)], tmp_path, duration=10.0, width=2560, height=1440, fps=30)
        html = (tmp_path / "index.html").read_text(encoding="utf-8")
        assert 'id="md0"' in html and 'id="em0"' in html and "cadáveres" in html
        if layer == "oscuridad":                                   # PARADA 1: sin parpadeos en misterio
            assert 'id="md0-beam"' in html and 'id="md0-fl"' not in html


def test_sparse_incluye_y_corre_el_enfasis():
    from script_engine import gfx_sparse as sp
    plan = {"title_card": None, "callouts": [], "count_up": None, "archive_clippings": [], "evidence_zoom": None,
            "punch_in": [], "chapter_question": None,
            "emphasis": [{"word": "agua", "category": "agua", "layer": "agua", "start": 20.0, "duration": 2.5}]}
    scenes = [GfxScene(0, 0.0, 40.0)]
    win = sp.event_windows(plan, scenes, 30, 40.0)
    assert any(a <= 20.0 and b >= 22.5 for a, b in win)
    p, _, _, _ = sp.compose_sparse(plan, scenes, win, 30)
    assert p["emphasis"][0]["start"] == pytest.approx(0.5)


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
