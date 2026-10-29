"""F50d — la época por tramo en el canon (A), la marca del canon (pedido + esquema) y el pedido de m03 con los tramos
(B). Offline, sin modelos."""
import json

from researcher_steps import step_4e_visual_canon as s4e

FICHA = {"hechos": [{"texto": "La mina cerró en 1966."}], "cronologia": [], "escenas": []}
TOPIC = {"video_title": "W", "evidence_pool": {"personajes": [{"rol": "Minero.", "lugar": "W",
                                                                "fechas_presente": ["1962"]}]}}


# ─────────────────────────── A. el canon por tramo ───────────────────────────
def test_f50d_a_las_tres_lineas_del_pedido():
    p = s4e.pedido_canon(TOPIC, FICHA)
    interiors = "- interiors: string EN, interiores característicos (oficinas, salas, casas).\n"
    assert interiors + ("- periods: una entrada por cada tramo del material en que cambian la ropa, la tecnología, los "
                        "vehículos o los interiores; years \"AAAA-AAAA\" y esos 4 campos para ese tramo (EN). Si el "
                        "tema es de una sola época, una sola entrada.\n") in p
    assert ("- where_when: dónde y en qué años aparecen, todos los años en que el material los muestra, también "
            "décadas después (EN, una frase)\n") in p
    assert ("- clothing_by_period: una entrada por cada tramo de años en que el material muestra a ese grupo; years "
            "\"AAAA-AAAA\" y clothing: ropa, peinado y accesorios de ESE grupo en ESE tramo, ese clima y esa clase "
            "social (EN, una frase)\n") in p
    assert "- clothing: ropa, peinado y accesorios de ESE grupo en ESOS años" not in p


def test_f50d_a_esquema_por_tramo_y_campos_unicos_que_se_quedan():
    era = s4e.VISUAL_CANON_SCHEMA_FICHA.properties["era_visual_canon"].properties
    assert set(era["periods"].items.properties) == set(s4e.PERIODO_CAMPOS)
    assert {"clothing", "technology", "vehicles_machinery", "interiors"} <= set(era)   # los leen m05, m06 y v3
    g = s4e.VISUAL_CANON_SCHEMA_FICHA.properties["people_groups"].items.properties
    assert "clothing" not in g and set(g["clothing_by_period"].items.properties) == {"years", "clothing"}
    assert "periods" not in s4e._VISUAL_CANON_SCHEMA.properties["era_visual_canon"].properties   # el viejo, intacto


def test_f50d_a_la_respuesta_guarda_periods_y_ropa_por_tramo(monkeypatch):
    resp = {"era_visual_canon": {"primary_decade": "1960s", "periods": [
        {"years": "1937-1966", "clothing": "work shirts", "technology": "valve radios"}, "basura"]},
        "people_groups": [{"id": "g", "clothing_by_period": [{"years": "1958-1966", "clothing": "cotton"}]}]}
    monkeypatch.setattr(s4e, "call_flash_json", lambda prompt, response_schema=None, **k: resp)
    c = s4e.canon_desde_ficha(TOPIC, FICHA)
    assert c["era_visual_canon"]["periods"] == [{"years": "1937-1966", "clothing": "work shirts",
                                                 "technology": "valve radios", "vehicles_machinery": "",
                                                 "interiors": ""}]
    assert c["people_groups"][0]["clothing_by_period"] == [{"years": "1958-1966", "clothing": "cotton"}]


def test_f50d_marca_cambia_con_una_letra_del_pedido_o_con_la_ficha(monkeypatch):
    b = json.dumps(FICHA).encode("utf-8")
    m0 = s4e.marca_canon(TOPIC, FICHA, b)
    assert m0 == s4e.marca_canon(TOPIC, FICHA, b)
    assert s4e.marca_canon(TOPIC, FICHA, b + b" ") != m0
    monkeypatch.setattr(s4e, "TEXTO_S5", s4e.TEXTO_S5.replace("Personajes", "Personajez"))
    assert s4e.marca_canon(TOPIC, FICHA, b) != m0
