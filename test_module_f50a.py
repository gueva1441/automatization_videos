"""F50 A — el canon visual sale de la ficha (`step_4e.canon_desde_ficha`) y lo asegura `fase1_5.asegurar_canon` antes
de m03, con la marca `canon_ficha_md5`. Offline: Flash y topics_db falsos."""
import json

import pytest

import fase1_5
from researcher_steps import step_4e_visual_canon as s4e

FICHA = {"hechos": [{"texto": "La mina cerró en 1966."}, {"texto": ""}],
         "cronologia": [{"fecha": "1943", "evento": "Abre la mina"}, {"fecha": "", "evento": ""}],
         "escenas": [{"donde": "Wittenoom", "quien": "mineros", "que_pasa": "cargan", "sentidos": "polvo azul"}]}


def test_adaptador_ficha_a_hechos():
    assert s4e.adaptador_facts(FICHA) == [{"fact": "La mina cerró en 1966."}, {"fact": "1943: Abre la mina"},
                                          {"fact": "Wittenoom — mineros — cargan — polvo azul"}]


def test_canon_desde_ficha_pide_grupos_y_los_devuelve(monkeypatch):
    pedido = {}

    def opus(prompt, **k):                                    # F50f: el canon va a Claude Opus, sin esquema
        pedido.update(prompt=prompt, **k)
        return {"era_visual_canon": {"periods": [{"years": "1937-1966"}]}, "documented_props": None,
                "people_groups": [{"id": "miners", "who": "w"}, {"who": "sin id"}]}
    monkeypatch.setattr(s4e.claude_helpers, "call_json", opus)
    topic = {"video_title": "Wittenoom", "evidence_pool": {"personajes": [
        {"rol": "Minero español.", "lugar": "Wittenoom", "fechas_presente": ["1962"]}]}}
    canon = s4e.canon_desde_ficha(topic, FICHA)
    assert canon["people_groups"] == [{"id": "miners", "who": "w"}] and canon["documented_props"] == []
    assert pedido["prompt"].endswith(s4e.TEXTO_S5 + "\n- Minero español · Wittenoom · 1962")
    assert s4e.TEXTO_1_PEOPLE_GROUPS in pedido["prompt"] and "response_schema" not in pedido


@pytest.fixture
def entorno(tmp_path, monkeypatch):
    tid = "t-f50"
    (tmp_path / tid).mkdir()
    (tmp_path / tid / "ficha_caso.json").write_text(json.dumps(FICHA), encoding="utf-8")
    db = {"topics": [{"id": tid, "video_title": "W"}]}
    llamadas = []
    monkeypatch.setattr(fase1_5, "STEPS_DIR", tmp_path)
    monkeypatch.setattr(fase1_5, "load_db", lambda: db)
    monkeypatch.setattr(fase1_5, "save_db", lambda d: None)
    monkeypatch.setattr(fase1_5, "_step_cost", lambda tid_, label, fn: fn())
    monkeypatch.setattr(s4e, "canon_desde_ficha", lambda topic, ficha: llamadas.append(1) or
                        {"era_visual_canon": {"spans": "1943-2024"}, "people_groups": [{"id": "g"}]})
    return {"tid": tid, "db": db, "llamadas": llamadas, "dir": tmp_path / tid}


def test_marca_md5_misma_ficha_no_llama_y_ficha_nueva_si(entorno):
    tid, db, llamadas = entorno["tid"], entorno["db"], entorno["llamadas"]
    t1 = fase1_5.asegurar_canon(tid, dict(db["topics"][0]), [])
    f = entorno["dir"] / "ficha_caso.json"                       # F50d: marca = ficha + pedido + esquema
    md5 = s4e.marca_canon(db["topics"][0], json.loads(f.read_text(encoding="utf-8")), f.read_bytes())
    assert llamadas == [1] and t1["canon_ficha_md5"] == md5 and db["topics"][0]["people_groups"] == [{"id": "g"}]
    assert (entorno["dir"] / "05_visual_canon.json").exists()
    fase1_5.asegurar_canon(tid, dict(db["topics"][0]), [])
    assert llamadas == [1]                                       # misma ficha → no se llama
    (entorno["dir"] / "ficha_caso.json").write_text(json.dumps({**FICHA, "hechos": []}), encoding="utf-8")
    fase1_5.asegurar_canon(tid, dict(db["topics"][0]), [])
    assert llamadas == [1, 1]                                    # ficha nueva → canon nuevo


def test_sin_people_groups_es_parada(entorno, monkeypatch):
    monkeypatch.setattr(s4e, "canon_desde_ficha", lambda topic, ficha: {"people_groups": []})
    with pytest.raises(fase1_5.Parada, match="people_groups"):
        fase1_5.asegurar_canon(entorno["tid"], {"id": entorno["tid"]}, [])


def test_el_research_ya_no_arma_canon():
    import topic_researcher as tr
    assert not hasattr(tr, "extract_visual_canon")
