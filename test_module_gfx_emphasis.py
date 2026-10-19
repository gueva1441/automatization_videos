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
    assert set(moods) == {"veneno_enfermedad", "agua", "muerte", "oscuridad_encierro"}
    assert all(len(m["triggers"]) >= 25 and m["layer"] in gc.VALID_MOOD_LAYERS for m in moods.values())
    reserva = {k for k, v in gc.ACTIVE_PROFILE["moods"].items() if not v["active"]}
    assert reserva == {"fuego", "caos_gritos", "radiacion_quimico", "frio_abandono", "silencio"}


def test_perfil_rechaza_mood_activo_flaco(tmp_path, monkeypatch):
    import json
    prof = json.loads(gc.profile_path("misterio").read_text(encoding="utf-8"))
    prof["moods"]["fuego"]["active"] = True                  # sin capa y con 10 disparadores
    monkeypatch.setattr(gc, "GFX_PROFILES_DIR", tmp_path)
    (tmp_path / "x.json").write_text(json.dumps(prof, ensure_ascii=False), encoding="utf-8")
    with pytest.raises(ValueError, match="moods.fuego"):
        gc.load_profile("x")


def test_candidatos_frases_y_flexiones():
    w = _words("Quedaron atrapados sin luz entre cadáveres y agua contaminada.")
    c = gd.emphasis_candidates(w, gc.active_moods())
    assert [(i, n, cat) for i, n, cat in c] == [(1, 1, "oscuridad_encierro"), (2, 2, "oscuridad_encierro"),
                                                (5, 1, "muerte"), (7, 1, "agua"), (8, 1, "veneno_enfermedad")]


def test_maximo_uno_por_frase_y_las_mas_raras():
    # frase 1: agua + cadáveres → 1 sola (la más rara: cadáveres, el agua aparece 3 veces en la narración)
    text = "El agua subía y había cadáveres flotando. Agua y más agua. " + " ".join(["nada"] * 30) + " Todo quedó a oscuras."
    words = _words(text)
    out = {"emphasis": [], "callouts": [], "punch_in": []}
    gd.place_emphasis(out, [], words=words, scenes=[GfxScene(0, 0.0, 60.0)], ctx={**CTX, "narration_all": text},
                      time_offset=0.0, limit=5)
    got = [(e["word"], e["category"]) for e in out["emphasis"]]
    assert [e["word"] for e in out["emphasis"] if e["sid"] == 0] == ["cadáveres"]     # la rara gana en su frase
    assert len({e["sid"] for e in out["emphasis"]}) == len(out["emphasis"])          # máx 1 por frase
    assert ("a oscuras", "oscuridad_encierro") in got                                 # frase del léxico, literal


def test_misma_categoria_separada_20_s():
    text = "cadáveres. muertos. " + " ".join(["x."] * 30) + " murieron."
    words = _words(text)
    out = {"emphasis": [], "callouts": [], "punch_in": []}
    gd.place_emphasis(out, [], words=words, scenes=[GfxScene(0, 0.0, 60.0)], ctx={**CTX, "narration_all": text},
                      time_offset=0.0, limit=5)
    ts = sorted(e["start"] for e in out["emphasis"] if e["category"] == "muerte")
    assert all(b - a >= gc.gfx_rules.emphasis_same_cat_gap_sec for a, b in zip(ts, ts[1:])) and len(ts) == 2


def test_resolve_pone_enfasis_y_rellena_hueco_primero_con_enfasis():
    text = ("Los presos esperaban. " * 3 + "Afuera todo seguía. " * 4 + "Algunos murieron sin ayuda. " +
            "Nadie vino. " * 6 + "Las celdas quedaron atrapadas en el olvido.")
    words = _words(text, 1.4)
    log: list[str] = []
    res = gd.resolve_plan({"title_card": {"use": True}}, ctx={**CTX, "narration_all": text, "skeleton": {"title": "T"}},
                          words=words, scenes=[GfxScene(0, 0.0, words[-1]["end"] + 1)], log=log)
    cats = [e["category"] for e in res["emphasis"]]
    assert "muerte" in cats and "oscuridad_encierro" in cats
    assert all(gd._literal_in(e["word"], text) for e in res["emphasis"])          # literal por construcción


def test_lock_y_cues_y_templater(tmp_path):
    plan = {"chapter_number": 2, "title_card": None, "callouts": [], "count_up": None, "archive_clippings": [],
            "evidence_zoom": None, "punch_in": [],
            "emphasis": [{"word": "cadáveres", "category": "muerte", "layer": "muerte", "icon": None, "start": 2.0,
                          "duration": 2.5, "side": "left", "stamp": True, "sid": 0},
                         {"word": "inventada", "category": "agua", "layer": "agua", "icon": None, "start": 6.0,
                          "duration": 2.5, "side": "right", "stamp": True, "sid": 1}]}
    ok, rej = lock(plan, {"narration_ch02": "Vieron cadáveres en el agua."}, chapter_number=2)
    assert [e["word"] for e in ok["emphasis"]] == ["cadáveres"] and rej[0]["block"] == "keyword_emphasis"
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


def test_sfx_tic_sordo_en_el_enfasis():
    out = {"emphasis": [{"start": 5.0}], "callouts": []}
    ev = gd.sfx_events(out, [], 0.0, gc.sfx_for)
    assert ev and ev[0]["block"] == "keyword_emphasis" and ev[0]["file"].endswith("tic_sordo.wav")


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
