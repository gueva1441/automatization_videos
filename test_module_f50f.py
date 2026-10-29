"""F50f — el canon visual con Claude Opus 5.5 sin esquema (`step_4e`), la marca con el modelo, la Parada por canon
que no sale o con `years` ilegibles (`fase1_5.asegurar_canon`) y la línea de log de fotos sin period (m03). Offline:
la API de Claude es un `_post` falso."""
import json

import pytest

import claude_helpers
import fase1_5
from researcher_steps import step_4e_visual_canon as s4e
from script_engine import m03_visual as m3

FICHA = {"hechos": [{"texto": "La mina cerró en 1966."}], "cronologia": [], "escenas": []}
TOPIC = {"video_title": "W", "evidence_pool": {"personajes": [{"rol": "Minero.", "lugar": "W",
                                                                "fechas_presente": ["1962"]}]}}
CANON = {"era_visual_canon": {"primary_decade": "1960s", "periods": [{"years": "1937-1966", "clothing": "c"}]},
         "people_groups": [{"id": "g", "who": "w", "clothing_by_period": [{"years": "1937-1966", "clothing": "c"}]}]}


def _api(monkeypatch, respuesta: dict):
    """`claude_helpers._post` falso: guarda el cuerpo del pedido y contesta `respuesta` como texto (sin red)."""
    visto = {}

    def post(body):
        visto.update(body)
        return {"model": body["model"], "stop_reason": "end_turn", "usage": {},
                "content": [{"type": "text", "text": "```json\n" + json.dumps(respuesta) + "\n```"}]}
    monkeypatch.setattr(claude_helpers, "_post", post)
    return visto


def test_f50f_la_llamada_va_a_opus_con_effort_y_sin_esquema(monkeypatch):
    visto = _api(monkeypatch, CANON)
    c = s4e.canon_desde_ficha(TOPIC, FICHA)
    assert visto["model"] == s4e.MODELO_CANON == "claude-opus-5-5"
    assert visto["output_config"] == {"effort": s4e.ESFUERZO_CANON} and s4e.ESFUERZO_CANON == "high"
    assert "format" not in visto["output_config"]                       # sin response_schema
    assert visto["messages"][0]["content"] == s4e.pedido_canon(TOPIC, FICHA)
    assert c["era_visual_canon"]["periods"][0]["years"] == "1937-1966" and c["people_groups"][0]["id"] == "g"


@pytest.mark.parametrize("respuesta, falta", [
    ({"people_groups": CANON["people_groups"]}, "periods"),
    ({"era_visual_canon": {"periods": []}, "people_groups": CANON["people_groups"]}, "periods"),
    ({"era_visual_canon": CANON["era_visual_canon"], "people_groups": [{"who": "sin id"}]}, "people_groups"),
])
def test_f50f_canon_sin_periods_o_sin_grupos_es_error(monkeypatch, respuesta, falta):
    _api(monkeypatch, respuesta)
    with pytest.raises(s4e.CanonError, match=falta):
        s4e.canon_desde_ficha(TOPIC, FICHA)


def test_f50f_sin_hechos_o_api_que_falla_es_error(monkeypatch):
    with pytest.raises(s4e.CanonError, match="sin hechos"):
        s4e.canon_desde_ficha(TOPIC, {"hechos": []})

    def falla(body):
        raise claude_helpers.ClaudeError("HTTP 400")
    monkeypatch.setattr(claude_helpers, "_post", falla)
    with pytest.raises(s4e.CanonError, match="HTTP 400"):
        s4e.canon_desde_ficha(TOPIC, FICHA)


def test_f50f_lo_viejo_ya_no_esta():
    for x in ("_VISUAL_CANON_SCHEMA", "VISUAL_CANON_SCHEMA_FICHA", "_ERA_SCHEMA", "_GRUPO_SCHEMA", "_PERIODO_SCHEMA",
              "_ROPA_TRAMO_SCHEMA", "_STR", "call_flash_json", "_empty_canon", "genai_types"):
        assert not hasattr(s4e, x), x


def test_f50f_marca_cambia_con_el_modelo_y_con_una_letra(monkeypatch):
    b = json.dumps(FICHA).encode("utf-8")
    m0 = s4e.marca_canon(TOPIC, FICHA, b)
    monkeypatch.setattr(s4e, "MODELO_CANON", "claude-sonnet-5-5")
    m1 = s4e.marca_canon(TOPIC, FICHA, b)
    monkeypatch.setattr(s4e, "MODELO_CANON", "claude-opus-5-5")
    monkeypatch.setattr(s4e, "ESFUERZO_CANON", "medium")
    m2 = s4e.marca_canon(TOPIC, FICHA, b)
    monkeypatch.setattr(s4e, "ESFUERZO_CANON", "high")
    monkeypatch.setattr(s4e, "TEXTO_S5", s4e.TEXTO_S5.replace("Personajes", "Personajez"))
    m3_ = s4e.marca_canon(TOPIC, FICHA, b)
    assert len({m0, m1, m2, m3_}) == 4


@pytest.fixture
def entorno(tmp_path, monkeypatch):
    tid = "t-f50f"
    (tmp_path / tid).mkdir()
    (tmp_path / tid / "ficha_caso.json").write_text(json.dumps(FICHA), encoding="utf-8")
    db = {"topics": [{"id": tid, "video_title": "W"}]}
    monkeypatch.setattr(fase1_5, "STEPS_DIR", tmp_path)
    monkeypatch.setattr(fase1_5, "load_db", lambda: db)
    monkeypatch.setattr(fase1_5, "save_db", lambda d: None)
    monkeypatch.setattr(fase1_5, "_step_cost", lambda tid_, label, fn: fn())
    return {"tid": tid, "db": db}


def test_f50f_years_ilegible_es_parada(entorno, monkeypatch):
    malo = {**CANON, "era_visual_canon": {"periods": [{"years": "1937-1966"}, {"years": "late colonial"}]}}
    monkeypatch.setattr(s4e, "canon_desde_ficha", lambda topic, ficha: malo)
    with pytest.raises(fase1_5.Parada, match="late colonial"):
        fase1_5.asegurar_canon(entorno["tid"], dict(entorno["db"]["topics"][0]), [])


def test_f50f_canon_que_no_sale_es_parada(entorno, monkeypatch):
    def no_sale(topic, ficha):
        raise s4e.CanonError("claude-opus-5-5: la respuesta no trae era_visual_canon.periods")
    monkeypatch.setattr(s4e, "canon_desde_ficha", no_sale)
    with pytest.raises(fase1_5.Parada, match="no salió"):
        fase1_5.asegurar_canon(entorno["tid"], dict(entorno["db"]["topics"][0]), [])


def test_f50f_log_de_fotos_sin_period():
    t = {"era_visual_canon": {"periods": [{"years": "1937-1957"}, {"years": "1958-1966"}]}}
    assert m3._log_sin_period(t, ["1962", "1990", "2006", ""], 5) == \
        "cap 5: 2 de 4 fotos sin period → 1990: 1958-1966; 2006: 1958-1966"
    assert m3._log_sin_period(t, ["1940", "1962"], 2) == "cap 2: 0 de 2 fotos sin period"
    assert m3._log_sin_period({}, ["1962"], 1) == "cap 1: canon sin periods (época única)"
