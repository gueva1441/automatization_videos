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
    assert res is None and len(why) == 5                                     # F4c R1: peso 1 tampoco es carga
    assert gi.validate(raw(intensidad=[0.5, 0.9]), SENTS, MOODS)[0] is None             # una cifra por frase


def test_top5_por_peso_no_por_orden():
    """F4c R1 (bug): ch02 perdía encierro/oscuridad/silencio (peso 3) porque se cortaba a las 5 primeras."""
    sents = ["La catástrofe y la furia del agua.", "El caos y la tragedia.", "Encierro, oscuridad y silencio total."]
    first = [("catástrofe", 0, 2), ("furia", 0, 2), ("agua", 0, 2), ("caos", 1, 2), ("tragedia", 1, 2)]
    last = [("encierro", 2, 3), ("oscuridad", 2, 3), ("silencio", 2, 3)]
    moods = {"m": {"triggers": {}}}
    r = {"pico_sentence_idx": 2, "intensidad": [0.5, 0.5, 0.9],
         "cargas": [{"word": w, "sentence_idx": i, "categoria": "m", "peso": p, "concreta": False} for w, i, p in first + last]}
    res, why = gi.validate(r, sents, moods, freq={"agua": 14, "caos": 1, "tragedia": 3, "furia": 2, "catástrofe": 1})
    assert [c["word"] for c in res["cargas"]] == ["encierro", "oscuridad", "silencio", "catástrofe", "caos"]
    assert any("tope" in w for w in why)


def test_prompt_sensorial_y_lexico_manda():
    p = gi.build_prompt(["Agua putrefacta."], [], [], {"m": {"triggers": {"x": 2}}}, [])
    assert "OLER" in p and "putrefacta" in p and "hasta 10" in p and "peso 1 NO es carga" in p
    aug = gi.augmented_moods({"agua": {"triggers": {"agua": 1}}}, {"cargas": [
        {"word": "agua", "categoria": "agua", "peso": 2}, {"word": "pútrida", "categoria": "agua", "peso": 3}]})
    assert aug["agua"]["triggers"] == {"agua": 1, "pútrida": 3}               # Flash no infla una palabra del léxico


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
