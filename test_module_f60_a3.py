# -*- coding: utf-8 -*-
"""F60 Etapa A3 — el canon de cada persona documentada separa aspecto fijo de estado.

- `_clean_person` devuelve `condition_by_period` (lista de {years, condition}), descarta entradas rotas, quita el nombre
  de `condition` por tokens y no aplica el strip C5 de era a `condition`; ausente → [].
- El bloque PERSONAS DOCUMENTADAS de m03 imprime `    condition {years}: {condition}` por entrada; con lista vacía queda
  idéntico al de hoy.
- `TEXTO_PERSONA` dice «at the age the canon describes» (sin «and condition»).
Sin red, US$ 0.
"""
from researcher_steps import step_4e_visual_canon as s4e
from script_engine import m03_visual as m3

PERSONA = {"name": "Daniel Écija", "role": "Spanish migrant miner", "era": "1962-1963", "age_at_event": None,
           "appearance_canon": "a young adult Spanish man of lean build"}


def test_condition_by_period_sobrevive_la_limpieza():
    out = s4e._clean_person({**PERSONA, "condition_by_period": [
        {"years": "1962-1963", "condition": "one foot bandaged after a mine injury"},
        {"years": "1991-1992", "condition": "gaunt and weakened by mesothelioma"}]})
    assert out["condition_by_period"] == [
        {"years": "1962-1963", "condition": "one foot bandaged after a mine injury"},
        {"years": "1991-1992", "condition": "gaunt and weakened by mesothelioma"}]
    assert out["appearance_canon"] == PERSONA["appearance_canon"]


def test_condition_by_period_descarta_entradas_rotas_y_es_opcional():
    out = s4e._clean_person({**PERSONA, "condition_by_period": [
        "texto suelto", None, 7, {"years": "", "condition": "x"}, {"years": "1962", "condition": "  "},
        {"years": 1962, "condition": "  one foot bandaged  "}, {"condition": "sin años"}]})
    assert out["condition_by_period"] == [{"years": "1962", "condition": "one foot bandaged"}]
    assert s4e._clean_person(PERSONA)["condition_by_period"] == []                      # ausente → []
    assert s4e._clean_person({**PERSONA, "condition_by_period": "no-lista"})["condition_by_period"] == []
    assert s4e._PERSON_REQUIRED_KEYS == ("name", "role", "era", "appearance_canon")   # el campo es opcional


def test_condition_sin_nombre_y_sin_strip_de_era():
    out = s4e._clean_person({**PERSONA, "condition_by_period": [
        {"years": "1962-1963", "condition": "Daniel Écija limps in 1960s work boots after the injury"}]})
    c = out["condition_by_period"][0]["condition"]
    assert "Daniel" not in c and "Écija" not in c
    assert "1960s work boots" in c                                                        # el strip C5 no se aplica
    # el mismo texto en appearance sí pierde la era (C5), como hoy
    assert "1960s" not in s4e._clean_person({**PERSONA, "appearance_canon": "a lean man in 1960s work boots"})["appearance_canon"]


def _topic(people):
    return {"era_visual_canon": {}, "documented_people": people, "anachronism_blocklist": [], "documented_props": []}


def test_bloque_personas_imprime_condition_y_vacio_queda_igual():
    sin = m3._format_seedream_canon_block(_topic([{**PERSONA, "condition_by_period": []}]))
    base = m3._format_seedream_canon_block(_topic([PERSONA]))
    assert sin == base and "condition " not in sin
    con = m3._format_seedream_canon_block(_topic([{**PERSONA, "condition_by_period": [
        {"years": "1962-1963", "condition": "one foot bandaged"}, {"years": "", "condition": "rota"}, "x"]}]))
    lines = con.splitlines()
    i = next(n for n, l in enumerate(lines) if l.startswith("    appearance_canon: "))
    assert lines[i + 1] == "    condition 1962-1963: one foot bandaged"
    assert con.count("    condition ") == 1                                               # la rota y el no-dict no se imprimen
    assert con.replace("    condition 1962-1963: one foot bandaged\n", "") == base


def test_texto_persona_sin_condition():
    assert "at the age the canon describes — the main one first" in m3.TEXTO_PERSONA
    assert "same age and condition" not in m3.TEXTO_PERSONA and "or if unsure" not in m3.TEXTO_PERSONA
    assert m3.TEXTO_PERSONA in m3.SYSTEM_INSTRUCTION_CASILLEROS


def test_pedido_del_canon_pide_condition_by_period():
    src = s4e._build_prompt({"seed_title": "t"}, {}, [{"fact": "f"}], None)
    assert "- condition_by_period: una entrada por cada tramo de años" in src
    assert "solo el aspecto físico fijo de la persona" in src
    assert "naval officer with focused" not in src and '"a mid-30s American man of medium build"' in src
    assert '"condition_by_period": []' in src
