"""F4b §1: director de intensidad (gfx_intensity) — validador literal, fallback, cache, léxico del cap, pico, propuestas."""
from __future__ import annotations

import json

from script_engine import gfx_intensity as gi
from script_engine import gfx_peak as gp

MOODS = {"agua": {"active": True, "layer": "agua", "triggers": {"agua": 1, "sumergidos": 3}},
         "oscuridad_encierro": {"active": True, "layer": "oscuridad", "triggers": {"encierro": 2}},
         "silencio": {"active": False, "layer": None, "triggers": {"silencio": 2}}}
SENTS = ["Las calles quedaron sumergidas bajo el agua.", "Nadie abrió las celdas.", "El silencio fue total."]


def W(text: str, step: float = 0.5) -> list[dict]:
    return [{"word": w, "start": round(k * step, 3), "end": round(k * step + 0.4, 3)} for k, w in enumerate(text.split())]


def raw(**kw):
    base = {"pico_sentence_idx": 1, "intensidad": [0.5, 0.9, 0.7],
            "cargas": [{"word": "celdas", "sentence_idx": 1, "categoria": "oscuridad_encierro", "peso": 3, "concreta": True},
                       {"word": "sumergidas", "sentence_idx": 0, "categoria": "agua", "peso": 2, "concreta": False},
                       {"word": "silencio", "sentence_idx": 2, "categoria": "silencio", "peso": 2, "concreta": False}]}
    base.update(kw)
    return base


def test_validador_literal_categoria_peso():
    res, why = gi.validate(raw(), SENTS, MOODS)
    assert [c["word"] for c in res["cargas"]] == ["celdas", "sumergidas", "silencio"] and not why
    bad = raw(cargas=[{"word": "celda", "sentence_idx": 1, "categoria": "oscuridad_encierro", "peso": 3, "concreta": True},   # otra flexión
                      {"word": "celdas", "sentence_idx": 1, "categoria": "fuego_x", "peso": 3, "concreta": True},           # categoría
                      {"word": "celdas", "sentence_idx": 1, "categoria": "oscuridad_encierro", "peso": 4, "concreta": True},  # peso
                      {"word": "agua", "sentence_idx": 0, "categoria": "agua", "peso": 1, "concreta": True}])
    res, why = gi.validate(bad, SENTS, MOODS)
    assert [c["word"] for c in res["cargas"]] == ["agua"] and len(why) == 3
    assert gi.validate(raw(intensidad=[0.5, 0.9]), SENTS, MOODS)[0] is None             # una cifra por frase


def test_fallback_tras_dos_fallos_y_cache(tmp_path):
    calls = []

    def bad(prompt, **kw):
        calls.append(prompt)
        return raw(intensidad=[1])
    assert gi.intensity_for(SENTS, cap="ch02", work_dir=tmp_path, moods_all=MOODS, call=bad) is None
    assert len(calls) == 2 and "NO sirvió" in calls[1]
    good = lambda p, **k: raw()  # noqa: E731
    r = gi.intensity_for(SENTS, cap="ch02", work_dir=tmp_path, moods_all=MOODS, call=good)
    assert r and (tmp_path / "gfx_intensity_ch02.json").exists()
    boom = lambda p, **k: (_ for _ in ()).throw(RuntimeError("no debería llamar"))  # noqa: E731
    assert gi.intensity_for(SENTS, cap="ch02", work_dir=tmp_path, moods_all=MOODS, call=boom) == r      # cache
    assert gi.intensity_for(SENTS[:2], cap="ch02", work_dir=tmp_path, moods_all=MOODS, call=lambda p, **k: raw(intensidad=[0.1, 0.2])) is not None  # otra narración → re-llama


def test_lexico_del_cap_y_pico():
    res, _ = gi.validate(raw(), SENTS, MOODS)
    act = {k: v for k, v in MOODS.items() if v["active"]}
    aug = gi.augmented_moods(act, res)
    assert aug["oscuridad_encierro"]["triggers"]["celdas"] == 3 and aug["agua"]["triggers"]["sumergidas"] == 2
    assert "silencio" not in aug and "celdas" not in MOODS["oscuridad_encierro"]["triggers"]          # sin mutar el perfil
    assert gi.peak_sentence(res) == 1
    tie = dict(res, intensidad=[0.9, 0.9, 0.7], cargas=res["cargas"] + [{"word": "sumergidas", "sentence_idx": 0,
                                                                        "categoria": "agua", "peso": 3, "concreta": False}])
    assert gi.peak_sentence(tie) == 0 and gi.peak_sentence(dict(res, intensidad=[0.9, 0.9, 0.7], cargas=[])) == 0
    words = W(" ".join(SENTS))
    pk = gp.peak_from_intensity(words, aug, res)
    assert pk["word"] == "celdas." .rstrip(".") and pk["sentence_idx"] == 1 and pk["intensity"] == 0.9


def test_pico_garantizado_prefiere_la_cifra_de_agua_cercana(tmp_path):
    words = W("Las calles quedaron sumergidas bajo 4.6 metros de agua. Nadie abrió las celdas. Fin del día.")
    ctx = {"facts": ["Algunas partes quedaron bajo 15 pies (4.6 metros) de agua."], "eligible": {}}
    res = {"intensidad": [0.85, 0.95, 0.2], "cargas": [{"word": "celdas", "sentence_idx": 1, "categoria": "oscuridad_encierro",
                                                       "peso": 3, "concreta": True}], "pico_llm": 1}
    aug = gi.augmented_moods({k: v for k, v in MOODS.items() if v["active"]}, res)
    aug["agua"]["triggers"]["sumergidas"] = 3
    plan = {"callouts": [], "emphasis": [], "punch_in": [], "archive_clippings": []}
    log: list[str] = []
    gp.plan_peak(plan, ctx=ctx, words=words, scenes=[], moods=aug, clip_dur=30.0, box_for=lambda si, w: None, log=log,
                 intensity=res)
    assert plan["pico"]["block"] == "water_level" and "por la cifra de agua" in log[0]
    res2 = dict(res, intensidad=[0.7, 0.95, 0.2])                                     # a más de 0.1 → gana la intensidad
    plan2 = {"callouts": [], "emphasis": [], "punch_in": [], "archive_clippings": []}
    gp.plan_peak(plan2, ctx=ctx, words=words, scenes=[], moods=aug, clip_dur=30.0, box_for=lambda si, w: None, intensity=res2)
    assert plan2["pico"]["word"] == "celdas" and plan2["pico"]["block"] is None


def test_propuestas_y_promocion_a_los_2_videos(tmp_path):
    prop, prof = tmp_path / "lexico_propuestas.json", tmp_path / "perfil.json"
    prof.write_text('{\n  "moods": {\n    "oscuridad_encierro": {"active": true, "triggers": {"encierro": 2}}\n  }\n}\n', encoding="utf-8")
    res, _ = gi.validate(raw(), SENTS, MOODS)
    assert gi.record_proposals(res, MOODS, video_id="v1", path=prop, profile_path=prof) == []
    data = json.loads(prop.read_text(encoding="utf-8"))
    assert set(data) == {"celdas", "sumergidas"} and data["celdas"]["videos"] == ["v1"]       # «silencio» ya está
    assert gi.record_proposals(res, MOODS, video_id="v1", path=prop, profile_path=prof) == []   # mismo video: no cuenta
    assert gi.record_proposals(res, MOODS, video_id="v2", path=prop, profile_path=prof) == ["celdas"]   # «agua» no está en el perfil de prueba
    txt = prof.read_text(encoding="utf-8")
    assert '"triggers": {"celdas": 3, "encierro": 2}' in txt and json.loads(txt)               # edición mínima
    assert json.loads(prop.read_text(encoding="utf-8"))["celdas"]["promovida"]
