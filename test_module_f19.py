"""
test_module_f19.py — F19 (Kyshtym otra vez): cirílico en el perfil del seed y en `place_re` (un texto en ruso nombra
el evento; sin ninguna forma, no; Orleans e Ycuá dan el mismo `place_re` que antes); antagonista persona o institución
de la ficha (Gusman pasa; una institución en ≥ 2 hechos pasa; «la KGB» fuera de la ficha no; sin ficha, como siempre);
el rango de beats de la compuerta en el usuario de la escaleta (sin compuerta, el usuario de F16/F17 no cambia); citas
con traducción en la ficha (el chequeo compara `texto` con el pool; el guion usa la traducción). Sin red.
"""
from __future__ import annotations

import copy
import json
import re
from pathlib import Path

import pytest

from researcher_steps import ficha_caso as fc
from researcher_steps import research_v3 as r3
from script_engine import m01a_escaleta as me
from test_module_f6b import POOL, good
from test_module_f16 import FICHA as FICHA16
from test_module_f16 import TOPIC

ROOT = Path(__file__).resolve().parent
STEPS = ROOT / "data" / "scripts" / "_steps"
RU = ("В сентябре 1957 года на комбинате «Маяк» под городом Кыштым взорвалась ёмкость с радиоактивными отходами. "
      "Авария получила название Кыштымская авария.")


# ═══════════════════════════════════════════════════════════════
#  1.1 Cirílico en el perfil y en place_re
# ═══════════════════════════════════════════════════════════════

def _viejo(names: list[str], fallback: str) -> str:
    return "|".join(rf"\b{re.escape(n)}\b" for n in names) or re.escape(fallback)


def test_texto_ruso_nombra_el_evento_con_las_formas_locales():
    pr = r3.place_regex(["Kyshtym disaster", "Ozyorsk"], ["Кыштым", "Маяк", "Озёрск", "Кыштымская авария", "ВУРС"])
    assert r3.names_event(RU, pr)
    assert r3.names_event("", pr, "Кыштымская авария 1957 года")              # en el título
    assert not r3.names_event(RU, _viejo(["Kyshtym disaster", "Ozyorsk"], "x"))  # el place_re de F18: no lo ve
    assert not r3.names_event("В 1957 году на одном заводе взорвалась ёмкость.", pr)   # sin ninguna forma
    assert not r3.names_event("Кыштымовский район", r3.place_regex([], ["Кыштым"]))     # límite de letra


def test_sin_locales_el_place_re_de_siempre():
    for names in (["Orleans Parish Prison", "OPP", "Templeman"], ["Ycuá Bolaños", "Ycua Bolanos"], []):
        assert r3.place_regex(names, None, "fallback") == _viejo(names, "fallback")
        assert r3.place_regex(names, [], "fallback") == _viejo(names, "fallback")
    pr = r3.place_regex(["Mayak"], ["Mayak", "Маяк"])                             # una local igual a una latina no se repite
    assert pr.count("Mayak") == 1 and "Маяк" in pr


@pytest.mark.parametrize("tid", ["f8s1-ycua-bolanos", "f8s2-cromanon", "f8s3-vajont"])
def test_perfiles_guardados_dan_el_mismo_place_re(tid):
    f = STEPS / tid / "_perfil.json"
    if not f.exists():
        pytest.skip("sin el perfil guardado")
    prof = json.loads(f.read_text(encoding="utf-8"))
    assert r3.place_regex(prof["nombres_lugar"], prof.get("nombres_locales"), "x") == prof["place_re"]


def test_seed_profile_pide_y_guarda_las_formas_locales():
    seen = {}

    def call(prompt, response_schema=None, description=None):
        seen.update(p=prompt, s=response_schema)
        return {"anio_evento": 1957, "lugar_principal": "Mayak", "idioma_local": "ruso",
                "nombres_lugar": ["Kyshtym disaster", "Ozyorsk"], "nombres_locales": ["Кыштым", "Маяк", "ВУ"]}
    prof = r3.seed_profile({"seed_title": "Desastre nuclear Kyshtym Mayak"}, call=call)
    assert "nombres_locales" in seen["s"]["properties"] and "alfabeto del idioma local" in seen["p"]
    assert prof["nombres_locales"] == ["Кыштым", "Маяк"]                          # < 3 letras fuera, como los latinos
    assert prof["place_re"] == r3.place_regex(["Kyshtym disaster", "Ozyorsk"], ["Кыштым", "Маяк"])
    assert r3.names_event(RU, prof["place_re"])


# ═══════════════════════════════════════════════════════════════
#  1.2 Antagonista persona o institución
# ═══════════════════════════════════════════════════════════════

FICHA = copy.deepcopy(FICHA16)
FICHA["hechos"] += [
    {"texto": "El Ministerio de Construcción de Maquinaria Media ordenó guardar el secreto.", "nivel": 1, "ids": ["D02"]},
    {"texto": "Los informes iban al Ministerio de Construcción de Maquinaria Media.", "nivel": 2, "ids": ["D04"]},
    {"texto": "El comité regional pidió la evacuación.", "nivel": 2, "ids": ["D05"]}]


def _ant(ant: dict, ficha: dict | None = FICHA) -> list[str]:
    e = good()
    e["antagonista"] = ant
    return [b for b in me.bloqueantes(e, POOL, ficha)[1] if me.bloqueante_de(b) == "antagonista es persona de la ficha"]


def test_antagonista_persona_pasa():
    assert _ant({"tipo": "persona", "id": "P01", "nombre": "Marlin N. Gusman"}) == []
    assert _ant({"id": "P01"}) == []                                              # sin tipo: como siempre


def test_antagonista_institucion_en_dos_hechos_pasa():
    assert _ant({"tipo": "institucion", "id": "", "nombre": "el Ministerio de Construcción de Maquinaria Media"}) == []
    assert me.institucion_de_la_ficha("Ministerio de Construccion de Maquinaria Media", FICHA)


def test_antagonista_institucion_fuera_de_la_ficha_no_pasa():
    assert _ant({"tipo": "institucion", "id": "", "nombre": "la KGB"})
    assert _ant({"tipo": "institucion", "id": "", "nombre": "el comité regional"})   # en un solo hecho
    f = copy.deepcopy(FICHA)
    f["personas"].append({"nombre": "Comité Regional", "rol": "institución", "ids": ["D05"]})
    assert _ant({"tipo": "institucion", "id": "", "nombre": "Comité Regional"}, f) == []   # como persona de la ficha


def test_sin_ficha_el_antagonista_es_persona_como_siempre():
    e = good()
    e["antagonista"] = {"tipo": "institucion", "id": "", "nombre": "el Ministerio de Construcción de Maquinaria Media"}
    hard = me.validate(e, POOL)[1]
    assert any(h.startswith("antagonista ") and "no es una persona del pool" in h for h in hard)
    assert me.SCHEMA["properties"]["antagonista"]["properties"].keys() == {"id", "por_que"}       # el de sin ficha
    assert {"tipo", "nombre"} <= me.SCHEMA_FICHA["properties"]["antagonista"]["properties"].keys()


# ═══════════════════════════════════════════════════════════════
#  1.3 Rango de beats de la compuerta en el usuario
# ═══════════════════════════════════════════════════════════════

def test_linea_de_beats_antes_de_la_tarea():
    p = me.build_prompt_v2(TOPIC, POOL, FICHA16, beats=(7, 8))
    assert p.endswith("Esta escaleta lleva entre 7 y 8 beats\n\n" + me.TAREA_V2)
    p = me.build_prompt_v2(TOPIC, POOL, FICHA16, ["x"], beats=(7, 14))
    assert p.index("</rechazo>") < p.index("Esta escaleta lleva entre 7 y 14 beats") < p.index("<tarea>")
    assert me.build_prompt_v2(TOPIC, POOL, FICHA16) == me.build_prompt_v2(TOPIC, POOL, FICHA16, beats=None)


@pytest.mark.parametrize("amarillo, rango", [(True, "entre 7 y 8 beats"), (False, "entre 7 y 14 beats")])
def test_el_rango_sale_del_perfil_de_la_compuerta(monkeypatch, tmp_path, amarillo, rango):
    monkeypatch.setattr(me, "STEPS_DIR", tmp_path)

    def gate(topic, pool, **kw):
        if amarillo:
            topic["_largo"] = {"cap_words": me.CAP_WORDS, "max_beats": 8, "min_beats_dev_cap": 1}
        return {"color": "amarillo" if amarillo else "verde", "metricas": {}, "motivos": [], "target_words": 1200}
    monkeypatch.setattr(me, "pool_gate_profile", gate)
    prompts = []

    def call(prompt, **kw):
        prompts.append(prompt)
        return good()
    me.generate_escaleta(dict(TOPIC), call=call, persist=False, ficha=FICHA16)
    assert rango in prompts[0]


def test_sin_compuerta_no_hay_linea(monkeypatch, tmp_path):
    monkeypatch.setattr(me, "STEPS_DIR", tmp_path)
    monkeypatch.setattr(me, "pool_gate_profile", lambda *a, **k: None)
    prompts = []
    me.generate_escaleta(dict(TOPIC), call=lambda p, **k: prompts.append(p) or good(), persist=False, ficha=FICHA16)
    assert "Esta escaleta lleva" not in prompts[0]


# ═══════════════════════════════════════════════════════════════
#  Citas con traducción (§2)
# ═══════════════════════════════════════════════════════════════

def test_cita_en_su_idioma_con_traduccion():
    props = fc.SCHEMA["properties"]["citas"]["items"]["properties"]
    assert "traduccion" in props and "traduccion" not in fc.SCHEMA["properties"]["citas"]["items"]["required"]
    its = {"Q01": {"id": "Q01", "_kind": "citas", "texto": "Nadie vino por nosotros", "texto_original":
                   "Nobody came for us", "texto_es": "Nadie vino por nosotros", "autor": "Edward Burton"}}
    cita = {"autor": "Edward Burton", "rol": "preso", "verificacion": "verificada", "texto": "Nobody came for us",
            "original": "", "traduccion": "Nadie vino por nosotros", "ids": ["Q01"]}
    assert fc.problems("citas", cita, its) == []
    assert fc.problems("citas", {**cita, "texto": "Nobody ever came"}, its)      # el chequeo de siempre sobre `texto`
    tx = fc.id_texts({"citas": [cita]})
    assert tx["Q01"] == "«Nadie vino por nosotros» — Edward Burton"
    assert fc.id_texts({"citas": [{**cita, "traduccion": ""}]})["Q01"] == "«Nobody came for us» — Edward Burton"
    f = copy.deepcopy(FICHA16)
    f["citas"] = [{**cita, "texto": "Nadie allí, nos dejaron por muertos", "traduccion": ""}]
    assert "traducción" not in me.ficha_section_v2(f, POOL)
    f["citas"] = [{**cita, "texto": "Nobody there, they left us for dead", "traduccion": "Nadie allí"}]
    assert "(traducción: «Nadie allí»)" in me.ficha_section_v2(f, POOL)
