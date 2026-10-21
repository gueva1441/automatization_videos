"""F4d (Omar 2026-10-20): pico con preferencia (agua > recorte con fuente > zoom humano), recortes por cláusula
completa con las 3 mejores para Flash, marca con +1 px y el \\b de los íconos Lucide."""
from __future__ import annotations

import gfx_config as gc
from script_engine import gfx_fragments as gf
from script_engine import gfx_intensity as gi
from script_engine import gfx_peak as gp
from script_engine.gfx_project import GfxScene

MOODS = {"agua": {"active": True, "layer": "agua", "triggers": {"agua": 1, "sumergidos": 3}},
         "veneno_enfermedad": {"active": True, "layer": "veneno", "triggers": {"putrefacta": 3}},
         "oscuridad_encierro": {"active": True, "layer": "oscuridad", "triggers": {"celdas": 3}}}
FACT_K = "El huracán Katrina tocó tierra el 29 de agosto de 2005."
FACT_S = ("Los prisioneros quedaron atrapados durante días en celdas inundadas con agua contaminada con aguas residuales, "
          "que en algunos casos les llegaba hasta el pecho.")
FACT_T = ("Reclusos de la sección 'Templeman III' informaron haber visto cadáveres flotando en las aguas de la inundación "
          "mientras eran evacuados el 1 de septiembre.")


def W(text: str, step: float = 0.5) -> list[dict]:
    return [{"word": w, "start": round(k * step, 3), "end": round(k * step + 0.4, 3)} for k, w in enumerate(text.split())]


def _plan():
    return {"callouts": [], "emphasis": [], "punch_in": [], "archive_clippings": []}


def test_pico_agua_salvo_que_otra_supere_por_mas_de_02():
    words = W("Calles sumergidos bajo 4.6 metros de agua putrefacta. Nadie abrió las celdas. Fin del día.")
    ctx = {"facts": ["Algunas partes quedaron bajo 15 pies (4.6 metros) de agua."], "eligible": {}}
    cg = [{"word": "celdas", "sentence_idx": 1, "categoria": "oscuridad_encierro", "peso": 3, "concreta": True}]
    for inten, block in (([0.85, 1.0, 0.2], "water_level"), ([0.8, 1.0, 0.2], "water_level"), ([0.75, 1.0, 0.2], None)):
        plan = _plan()
        gp.plan_peak(plan, ctx=ctx, words=words, scenes=[], moods=MOODS, clip_dur=30.0, box_for=lambda si, w: None,
                     intensity={"intensidad": inten, "cargas": cg})
        assert (plan["pico"]["block"] == "water_level") is (block == "water_level"), inten
    plan = _plan()                                   # con el agua, la palabra del pico es PUTREFACTA (no otra de agua)
    gp.plan_peak(plan, ctx=ctx, words=words, scenes=[], moods=MOODS, clip_dur=30.0, box_for=lambda si, w: None,
                 intensity={"intensidad": [0.85, 1.0, 0.2], "cargas": cg})
    assert plan["pico"]["palabra"] == "putrefacta"
    assert [e["word"] for e in plan["emphasis"] if e.get("peak_word")] == ["putrefacta"]


def test_pico_recorte_con_fuente_antes_que_zoom_humano():
    words = W("Vieron celdas cerradas. Fin.")
    scenes = [GfxScene(0, 0.0, 8.0)]
    res = {"intensidad": [0.9, 0.1], "cargas": [{"word": "celdas", "sentence_idx": 0, "categoria": "oscuridad_encierro",
                                                 "peso": 3, "concreta": True}]}
    box = lambda si, w: [0.4, 0.4, 0.2, 0.2]  # noqa: E731
    p1 = _plan()
    p1["archive_clippings"] = [{"headline": "x", "kicker": "2005", "start": 1.0, "duration": 6.0, "side": "left"}]
    gp.plan_peak(p1, ctx={"facts": []}, words=words, scenes=scenes, moods=MOODS, clip_dur=8.0, box_for=box,
                 intensity=res, human_box_for=box)
    assert p1["pico"]["block"] == "archive_clippings" and p1["archive_clippings"][0]["peak"]
    p2 = _plan()                                     # sin recorte → zoom, solo si el detalle es humano
    gp.plan_peak(p2, ctx={"facts": []}, words=words, scenes=scenes, moods=MOODS, clip_dur=8.0, box_for=box,
                 intensity=res, human_box_for=lambda si, w: None)
    assert p2["pico"]["block"] == "emphasis"


def test_recorte_clausulas_completas():
    k = gf.clause_options(FACT_K)
    assert "El huracán Katrina tocó tierra el 29 de agosto" in k and "el 29 de agosto" not in k   # sin sujeto, no
    assert all(len(o.split()) <= 10 for o in k)
    s = gf.clause_options(FACT_S)
    assert "celdas inundadas con agua contaminada con aguas residuales" in s
    assert not any(o.startswith(("quedaron", "inundadas", "que ", "durante")) for o in s)      # verbo/participio/función
    t = gf.clause_options(FACT_T)
    assert "cadáveres flotando en las aguas de la inundación" in t                                # «mientras» corta
    assert not any("visto" in o.split()[0] or o.startswith("III") for o in t)


def test_flash_elige_entre_las_3_que_mas_aportan(tmp_path):
    words = W("Los presos quedaron atrapados en celdas inundadas. Era 2005.")
    items = gf.build_items({"archive_clippings": [{"headline": "celdas inundadas", "fact_idx": 0, "scene_idx": 0,
                                                  "start": 1.0}]}, facts=[FACT_S], words=words,
                           scenes=[GfxScene(0, 0.0, 20.0)], time_offset=0.0, key_words=set(), documents=True)
    opts = items[0]["options"]
    assert len(opts) == 3 and all("residuales" in o for o in opts)


def test_marca_mas_fina_y_lucide_con_pathlength():
    assert gc.ACTIVE_PROFILE["channel_bug"]["corner_dilate_px"] == 1
    from script_engine.gfx_icons import lucide_restyled
    out = lucide_restyled('<svg viewBox="0 0 24 24"><path d="M1 1"/><circle r="2"/></svg>')
    assert out.count('pathLength="1"') == 2
    assert gi.MAX_CARGAS == 5                                                # sin cambios en R1


def test_cache_de_la_marca_distingue_el_engrosado(tmp_path, monkeypatch):
    from script_engine import gfx_bug as gb
    from test_module_gfx_bug import SVG
    (tmp_path / "bug").mkdir()
    (tmp_path / "bug" / "b.svg").write_text(SVG, encoding="utf-8")
    monkeypatch.setattr(gb, "GFX_PROFILES_DIR", tmp_path)
    c1 = gb.config({"channel_bug": {"enabled": True, "svg": "bug/b.svg", "corner_dilate_px": 1}})
    c2 = {**c1, "corner_dilate_px": 2}
    assert gb.pngs(c1, 86, tmp_path / "p", corner=True)[0] != gb.pngs(c2, 86, tmp_path / "p", corner=True)[0]
