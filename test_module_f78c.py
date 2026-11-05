# -*- coding: utf-8 -*-
"""F78c — el bloque PERSONAS DOCUMENTADAS de m03 describe a la persona con los rasgos de su foto madre (HANDOFF_F78c, adenda 2:
m03 SOLO lee rasgos.json si su md5_entrada coincide con `foto_madre.entrada_rasgos` del 03_visual.json en disco; nunca llama).

Sin red: rasgos, madres, estados y variantes simulados."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

import foto_madre as fm
from script_engine import m03_visual as m3

PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 16
CARMEN = {"name": "Carmen Cortés", "role": "adolescent victim", "era": "1981-2000", "age_at_event": 14,
          "appearance_canon": "a fourteen-year-old Spanish girl",
          "condition_by_period": [{"years": "1981-1982", "condition": "Visibly emaciated."}]}
SANCHO = {"name": "Jesús Sancho Rof", "role": "minister", "era": "1981", "age_at_event": None,
          "appearance_canon": "a middle-aged Spanish man", "condition_by_period": []}
MOSCOSO = {"name": "Javier Moscoso", "role": "attorney", "era": "1989", "age_at_event": None,
           "appearance_canon": "a middle-aged Spanish man", "condition_by_period": []}
VISUAL = {"chapters": [{"chapter_number": 3, "image_prompts": [
    {"prompt": "a", "persona": ["Carmen Cortés"], "anio": "1981", "people_group": ["kids"]},
    {"prompt": "b", "persona": ["Carmen Cortés"], "anio": "1981", "people_group": ["kids"]},
    {"prompt": "c", "persona": ["Jesús Sancho Rof"], "anio": "1981", "people_group": []},
    {"prompt": "d", "persona": ["Jesús Sancho Rof"], "anio": "1981", "people_group": []},
    {"prompt": "e", "persona": ["Javier Moscoso"], "anio": "1989", "people_group": []}]}]}
RASGOS = {"Carmen Cortés": "Oval face, long dark brown hair tied back in a single braid, slender build",
          "Jesús Sancho Rof": "Broad oval face, thick dark-rimmed glasses, stocky build"}


def _topic():
    return {"id": "t78c", "documented_people": [dict(CARMEN), dict(SANCHO), dict(MOSCOSO)],
            "people_groups": [{"id": "kids", "appearance": "Spanish children."}]}


@pytest.fixture
def disco(tmp_path, monkeypatch):
    """OUTPUT_DIR y STEPS_DIR de foto_madre en tmp, con el 03_visual.json del topic; las llamadas simuladas se cuentan."""
    monkeypatch.setattr(fm, "OUTPUT_DIR", tmp_path / "output")
    monkeypatch.setattr(fm, "STEPS_DIR", tmp_path / "_steps")
    (tmp_path / "_steps" / "t78c").mkdir(parents=True)
    (tmp_path / "_steps" / "t78c" / "03_visual.json").write_text(json.dumps(VISUAL), encoding="utf-8")
    monkeypatch.setattr(fm.api, "image_engine", "nb2_lite", raising=False)
    llamadas: list = []
    monkeypatch.setattr(fm, "_llamar_rasgos", lambda e: (llamadas.append("rasgos"), {x["name"]: RASGOS[x["name"]] for x in e})[1])
    monkeypatch.setattr(fm, "_llamar_estados", lambda f: (llamadas.append("estados"), {(x["name"], x["tramo"]): "thin arms" for x in f})[1])

    def madre(prompt, dest):
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(PNG)
        return {"endpoint": "seedream", "path": str(dest)}

    def variante(prompt, ref, dest):
        dest.write_bytes(PNG)
        return {"motor": "nb2_lite", "usd": 0}
    monkeypatch.setattr(fm, "_generate_madre_seedream", madre)
    monkeypatch.setattr(fm, "_generate_variante", variante)
    return tmp_path, llamadas


def _personas(bloque: str) -> str:
    i = bloque.index("PERSONAS DOCUMENTADAS")
    return bloque[i:bloque.find("\n\n", i)]


def test_con_rasgos_vigentes_la_linea_appearance_reemplaza_al_canon(disco, capsys):
    tmp, llamadas = disco
    topic = _topic()
    fm.generate_fotos_madre_personas(topic, "t78c")            # crea rasgos.json (1 llamada) como en producción
    assert llamadas.count("rasgos") == 1
    b = _personas(m3._format_seedream_canon_block(topic))
    assert f"    appearance: {RASGOS['Carmen Cortés']}" in b and f"    appearance: {RASGOS['Jesús Sancho Rof']}" in b
    assert "appearance_canon: a fourteen-year-old Spanish girl" not in b and "appearance_canon: a middle-aged Spanish man" in b  # Moscoso
    assert b.count("appearance_canon:") == 1                                                  # no se suman las dos líneas
    assert "    condition 1981-1982: Visibly emaciated." in b and "| age 14 |" in b                 # edad y condition no cambian
    assert b.startswith("PERSONAS DOCUMENTADAS (el nombre es solo para el casillero persona; en la prosa usar appearance "
                        "(o appearance_canon si no hay), NUNCA el nombre):")
    assert llamadas.count("rasgos") == 1 and "WARN" not in capsys.readouterr().out             # m03 no llamó


def test_sin_rasgos_json_linea_vieja_y_warn_sin_llamar(disco, capsys, monkeypatch):
    monkeypatch.setattr(fm, "_llamar_rasgos", lambda e: pytest.fail("m03 nunca llama a rasgos"))
    b = _personas(m3._format_seedream_canon_block(_topic()))
    assert b.count("appearance_canon:") == 3 and "    appearance: " not in b
    assert "WARN PERSONAS DOCUMENTADAS con appearance_canon: rasgos no vigentes (sin rasgos.json)" in capsys.readouterr().out


def test_md5_distinto_linea_vieja_y_warn(disco, capsys, monkeypatch):
    topic = _topic()
    fm.generate_fotos_madre_personas(topic, "t78c")
    topic["documented_people"][0]["role"] = "otra"             # la entrada cambia → el cache no vale
    monkeypatch.setattr(fm, "_llamar_rasgos", lambda e: pytest.fail("m03 nunca llama a rasgos"))
    b = _personas(m3._format_seedream_canon_block(topic))
    assert "    appearance: " not in b and "md5 de la entrada distinto" in capsys.readouterr().out


def test_sin_03_visual_o_sin_id(disco, capsys):
    assert fm.rasgos_vigentes({"documented_people": []}) == ({}, "topic sin id")
    assert fm.rasgos_vigentes({"id": "otro", "documented_people": []}) == ({}, "sin 03_visual.json")


def test_entrada_rasgos_misma_que_usa_foto_madre(disco):
    tmp, llamadas = disco
    topic = _topic()
    fm.generate_fotos_madre_personas(topic, "t78c")
    cache = json.loads((tmp / "output" / "t78c" / "foto_madre" / "rasgos.json").read_text(encoding="utf-8"))
    entrada = fm.entrada_rasgos(topic, VISUAL)
    assert fm._md5(entrada) == cache["md5_entrada"] and entrada == cache["entrada"]
    assert [e["name"] for e in entrada] == ["Carmen Cortés", "Jesús Sancho Rof"]                    # Moscoso: 1 foto → no
    assert entrada[0]["grupo_appearance"] == "Spanish children."
    fm.generate_fotos_madre_personas(topic, "t78c")              # segunda corrida: cache, sin llamada
    assert llamadas.count("rasgos") == 1


COLZA = "c4934b7d-3f54-448f-ba5f-539dc744f0d8"


@pytest.mark.skipif(not (fm.OUTPUT_DIR / COLZA / "foto_madre" / "rasgos.json").exists(), reason="sin el rasgos.json de Colza")
def test_colza_md5_desde_m03_igual_al_de_rasgos_json(monkeypatch):
    """Adenda 1.2: el md5 que arma m03 = el `md5_entrada` del rasgos.json real de Colza → 0 llamadas nuevas. Solo lectura."""
    db = json.loads((fm.DATA_DIR / "topics_db.json").read_text(encoding="utf-8"))
    topic = next(t for t in (db["topics"] if isinstance(db, dict) else db) if t.get("id") == COLZA)
    monkeypatch.setattr(fm, "_llamar_rasgos", lambda e: pytest.fail("no se llama"))
    rasgos, motivo = fm.rasgos_vigentes(topic)
    assert motivo == "ok" and len(rasgos) == 7
    visual = json.loads((fm.STEPS_DIR / COLZA / "03_visual.json").read_text(encoding="utf-8"))
    cache = json.loads((fm.OUTPUT_DIR / COLZA / "foto_madre" / "rasgos.json").read_text(encoding="utf-8"))
    assert fm._md5(fm.entrada_rasgos(topic, visual)) == cache["md5_entrada"]
