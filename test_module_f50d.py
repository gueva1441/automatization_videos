"""F50d — la época por tramo en el canon (A), la marca del canon (pedido + esquema) y el pedido de m03 con los tramos
(B). Offline, sin modelos."""
import json

from researcher_steps import step_4e_visual_canon as s4e
from script_engine import m03_expediente as mexp
from script_engine import m03_visual as m3

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


# ─────────────────────────── F50d B. época por tramo en el pedido ───────────────────────────

_ERA_VIEJA = {"primary_decade": "1950s", "spans": "1943-1966", "clothing": "khaki shorts",
              "technology": "valve radios", "vehicles_machinery": "Bedford trucks", "interiors": "fibro huts",
              "forbidden_anachronisms": "mobile phones"}
_PERIODS = [
    {"years": "1943-1957", "clothing": "c1", "technology": "t1", "vehicles_machinery": "v1", "interiors": "i1"},
    {"years": "1958-1966", "clothing": "c2", "technology": "t2", "vehicles_machinery": "v2", "interiors": "i2"},
    {"years": "1985-1995", "clothing": "c3", "technology": "t3", "vehicles_machinery": "v3", "interiors": "i3"},
]
_CABEZA = ("ERA (capa genérica de la época):\n"
           "  primary_decade        : 1950s\n"
           "  spans                 : 1943-1966\n")
_COLA = "  forbidden_anachronisms: mobile phones\n\nLUGAR PUNTUAL"


def _canon(era, anios=None):
    return m3._format_seedream_canon_block({"era_visual_canon": era, "documented_people": [],
                                            "documented_props": [], "anachronism_blocklist": []}, anios)


def _tanda(n, years):
    return (f"  period {years}:\n  clothing              : c{n}\n  technology            : t{n}\n"
            f"  vehicles_machinery    : v{n}\n  interiors             : i{n}\n")


def test_f50d_b_canon_sin_periods_igual_que_antes():
    esperado = (_CABEZA +
                "  clothing              : khaki shorts\n"
                "  technology            : valve radios\n"
                "  vehicles_machinery    : Bedford trucks\n"
                "  interiors             : fibro huts\n" + _COLA)
    for anios in (None, [], ["1962"], ["1990"]):          # sin periods los años no importan
        assert _canon(_ERA_VIEJA, anios).startswith(esperado)
    assert _canon(_ERA_VIEJA) == _canon({**_ERA_VIEJA, "periods": []}, ["1990"])   # periods vacío = topic viejo


def test_f50d_b_periods_que_se_cruzan():
    era = {**_ERA_VIEJA, "periods": _PERIODS}
    b = _canon(era, ["1962", "1990", None, ""])
    assert b.startswith(_CABEZA + _tanda(2, "1958-1966") + _tanda(3, "1985-1995") + _COLA)
    assert "period 1943-1957" not in b and "khaki shorts" not in b     # los campos únicos no salen con periods
    assert _canon(era, ["1957", "1958"]).startswith(_CABEZA + _tanda(1, "1943-1957") + _tanda(2, "1958-1966"))


def test_f50d_b_ningun_period_se_cruza_el_mas_cercano():
    era = {**_ERA_VIEJA, "periods": _PERIODS}
    assert _canon(era, ["1970"]).startswith(_CABEZA + _tanda(2, "1958-1966") + _COLA)       # 4 años vs 15
    assert _canon(era, ["2001"]).startswith(_CABEZA + _tanda(3, "1985-1995") + _COLA)
    assert _canon(era, ["1975"]).startswith(_CABEZA + _tanda(2, "1958-1966") + _COLA)       # 9 vs 10
    assert _canon(era, ["1976"]).startswith(_CABEZA + _tanda(3, "1985-1995") + _COLA)       # 10 vs 9
    tie = [{"years": "1960-1960", "clothing": "a"}, {"years": "1964-1964", "clothing": "b"}]
    b = _canon({**_ERA_VIEJA, "periods": tie}, ["1962"])                                     # 2 y 2 → los dos
    assert "  period 1960-1960:" in b and "  period 1964-1964:" in b


def test_f50d_b_tramo_entiende_los_formatos_de_flash():
    casos = {"1937-1957": (1937, 1957), "1958-1966": (1958, 1966), "1950s-1970s": (1950, 1979),
             "1937-1950s": (1937, 1959), "2000s-2026": (2000, 2026), "2000s-present": (2000, 2030),
             "1971-present": (1971, 2030), "1979-2000s": (1979, 2009), "1962": (1962, 1962),
             "1950s": (1950, 1959), "1960–1970": (1960, 1970)}
    for years, esperado in casos.items():
        assert m3._tramo(years, hoy=2030) == esperado, years
    for ilegible in ("c. 1960", "", None, "1966-1958", "late colonial"):
        assert m3._tramo(ilegible, hoy=2030) is None, ilegible


def test_f50d_b_canon_de_produccion_fotos_despues_de_1966():
    prod = [{"years": "1937-1957"}, {"years": "1958-1966"}]
    yrs = lambda anios: [pe["years"] for pe in m3._periods_del_cap(prod, anios)]
    assert yrs(["1985"]) == ["1958-1966"] and yrs(["2006"]) == ["1958-1966"]   # ninguno cruza → el más cercano
    assert yrs(["1962", "1990"]) == ["1958-1966"]
    assert yrs(["1940", "1990"]) == ["1937-1957", "1958-1966"]                  # foto por foto: 1940 cruza, 1990 → cercano
    assert yrs(["1957", "1958"]) == ["1937-1957", "1958-1966"]


def test_f50d_b_period_ilegible_no_cruza():
    pe = [{"years": "late colonial", "clothing": "x"}, {"years": "1958-1966", "clothing": "c2"}]
    assert [p["years"] for p in m3._periods_del_cap(pe, ["1962"])] == ["1958-1966"]
    assert m3._periods_del_cap([{"years": "?"}], ["1962"]) == []
    b = _canon({**_ERA_VIEJA, "periods": [{"years": "?", "clothing": "x"}]}, ["1962"])   # ninguno legible → únicos
    assert "  clothing              : khaki shorts\n" in b and "period" not in b


def test_f50d_b_sin_anios_en_el_cap_todos_los_periods():
    b = _canon({**_ERA_VIEJA, "periods": _PERIODS}, [None, ""])
    assert b.startswith(_CABEZA + _tanda(1, "1943-1957") + _tanda(2, "1958-1966") + _tanda(3, "1985-1995") + _COLA)


def test_f50d_b_anios_llegan_del_expediente_al_pedido(monkeypatch):
    vistos = {}
    def falso(topic, anios=None):
        vistos["a"] = anios
        return "CANON"
    monkeypatch.setattr(m3, "_format_seedream_canon_block", falso)
    p = m3._build_seedream_prompt_step2({}, {"chapter_number": 2}, "n", ["a"], "", ["1962", "1990"])
    assert "CANON" in p
    assert vistos["a"] == ["1962", "1990"]


def test_f50d_b_clothing_con_dos_tramos():
    g = {"id": "miners", "who": "w", "where_when": "ww", "appearance": "lean",
         "clothing_by_period": [{"years": "1958-1966", "clothing": "khaki shorts"},
                                {"years": "1985-1995", "clothing": "hi-vis vests"}]}
    b = mexp.bloque([], [g])
    assert b.endswith("  - miners: w · ww · APPEARANCE: lean · CLOTHING: 1958-1966: khaki shorts; "
                      "1985-1995: hi-vis vests\n")


def test_f50d_b_grupo_sin_clothing_by_period_y_clothing_viejo_ignorado():
    b = mexp.bloque([], [{"id": "g", "who": "w", "where_when": "ww", "clothing": "cotton dresses"}])
    assert b.endswith("  - g: w · ww · APPEARANCE: - · CLOTHING: -\n") and "cotton dresses" not in b
    assert mexp.bloque([], [{"id": "g", "who": "w", "where_when": "ww", "clothing_by_period": []}]).endswith(
        "CLOTHING: -\n")
