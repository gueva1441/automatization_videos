# -*- coding: utf-8 -*-
"""F75 B1 (módulo 5 del handoff): la pestaña NARRACIÓN de QA Studio muestra `validacion.entre_promesas` junto a «loops» y dice
«Personaje según la narración» con sus oraciones. Sin API."""
import json
from pathlib import Path

from test_m01f_compuerta import _generar, _qa, _sin_api, env  # noqa: F401 — fixtures

ROOT = Path(__file__).resolve().parent.parent


def test_critico_lleva_entre_promesas(env, monkeypatch):  # noqa: F811
    qa, st = _qa(env, monkeypatch)
    _generar(env)
    c = qa.narracion_vista(st)["critico"]
    j = json.loads((env["d"] / "01f_critico.json").read_text(encoding="utf-8"))
    assert c["entre_promesas"] == j["validacion"]["entre_promesas"] and c["entre_promesas"]["tramos"][0]["desde"] == "ch01:0"


def test_critica_vieja_sin_entre_promesas_da_none(env, monkeypatch):  # noqa: F811
    qa, st = _qa(env, monkeypatch)
    _generar(env)
    f = env["d"] / "01f_critico.json"
    j = json.loads(f.read_text(encoding="utf-8"))
    del j["validacion"]["entre_promesas"]
    f.write_text(json.dumps(j, ensure_ascii=False), encoding="utf-8")
    assert qa.narracion_vista(st)["critico"]["entre_promesas"] is None


def test_la_pagina_dice_segun_la_narracion_y_muestra_entre_promesas():
    s = (ROOT / "qa_studio.html").read_text(encoding="utf-8")
    assert "Personaje según la escaleta" not in s and "Personaje según la narración" in s and "m.personaje.oraciones" in s
    i, j = s.index("nnPlegado(`loops ("), s.index('id="nnEntrePromesas"')
    assert 0 < j - i < 600 and "r.entre_promesas.tramos" in s and "max_segundos" in s
