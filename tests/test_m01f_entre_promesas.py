# -*- coding: utf-8 -*-
"""F75 B1: segundos entre promesas nuevas (m01f `entre_promesas`), el .md re-renderizado desde el JSON sin API, y el personaje
«según la narración». Sin API: el `_sin_api` de test_m01f_compuerta explota si algo llama al modelo."""
import json

from script_engine import m01d_particion as md
from script_engine import m01f_critico as mf
from test_m01f_compuerta import POOL, TID, _generar, _msg, _resp, _sin_api, env  # noqa: F401 — fixtures

# ch01: 4 + 6 + 10 palabras · ch02: 5 + 15 palabras → total 40
CAPS = [{"cap": "ch01", "oraciones": [{"idx": 0, "texto": "uno dos tres cuatro."},
                                      {"idx": 1, "texto": "a b c d e f."},
                                      {"idx": 2, "texto": " ".join(["x"] * 10) + "."}]},
        {"cap": "ch02", "oraciones": [{"idx": 0, "texto": "p q r s t."},
                                      {"idx": 1, "texto": " ".join(["y"] * 15) + "."}]}]


def _loop(abre, pregunta="p"):
    return {"pregunta": pregunta, "abre": abre, "paga": None, "se_recuerda": True}


def test_cuenta_palabras_anteriores_por_seg_y_redondea_cada_tramo():
    # aperturas en las palabras 4 (ch01:1), 20 (ch02:0) y 25 (ch02:1); total 40; seg 0.33 → 5.28 / 1.65 / 4.95
    ep = mf.entre_promesas([_loop("ch02:1", "c"), _loop("ch01:1", "a"), _loop("ch02:0", "b")], CAPS, 0.33)
    assert [(t["desde"], t["hasta"], t["segundos"], t["pregunta_que_abre"]) for t in ep["tramos"]] == [
        ("ch01:1", "ch02:0", 5, "a"), ("ch02:0", "ch02:1", 2, "b"), ("ch02:1", "fin", 5, "c")]
    assert ep["max_segundos"] == 5 and ep["max_tramo"] == {"desde": "ch01:1", "hasta": "ch02:0"}    # empate → el primero
    assert ep["loops_invalidos"] == [] and ep["seg_por_palabra"] == 0.33


def test_dos_loops_en_la_misma_oracion_son_una_apertura():
    ep = mf.entre_promesas([_loop("ch01:0", "a"), _loop("ch01:2", "b"), _loop("ch01:2", "c")], CAPS, 1.0)
    assert [(t["desde"], t["hasta"], t["segundos"]) for t in ep["tramos"]] == [("ch01:0", "ch01:2", 10), ("ch01:2", "fin", 30)]
    assert ep["tramos"][1]["pregunta_que_abre"] == "b / c"


def test_abre_invalido_va_a_loops_invalidos_y_no_cuenta():
    ep = mf.entre_promesas([_loop("ch01:0"), _loop("ch09:3", "fuera"), _loop(None, "sin abre"), {"pregunta": "nada"}, "basura"], CAPS, 1.0)
    assert [t["desde"] for t in ep["tramos"]] == ["ch01:0"] and ep["tramos"][0]["segundos"] == 40
    assert ep["loops_invalidos"] == [{"abre": "ch09:3", "pregunta": "fuera"}, {"abre": None, "pregunta": "sin abre"},
                                     {"abre": None, "pregunta": "nada"}]


def test_sin_loops_no_hay_tramos():
    ep = mf.entre_promesas([], CAPS, 1.0)
    assert ep["tramos"] == [] and ep["max_segundos"] is None and ep["max_tramo"] is None


def _met(per=None, seg=0.5):
    return {"seg_por_palabra": seg, "caps": [], "personaje": per, "personaje_motivo": None if per else "nadie del pool se nombra en la voz"}


def _critica(md5_critico="aaa"):
    return {"prompt_version": "m01f-1", "modelo": "claude-opus-5-5", "effort": "medium", "usd": 0.69, "segundos": 1.0, "intentos": 1,
            "usage": {"input_tokens": 1, "output_tokens": 2}, "narracion_md5": md5_critico,
            "respuesta": {**_resp(), "loops": [_loop("ch01:1", "a"), _loop("ch02:0", "b"), _loop("ch07:0", "mala")]},
            "validacion": {"deberia": [], "ids_invalidos": [], "oraciones_invalidas": []}}


def test_rerender_desde_el_json_con_el_aviso_de_otra_narracion():
    c = _critica("aaa")
    copia = json.loads(json.dumps(c))
    val, t = mf.rerender(c, CAPS, _met(seg=0.5), "bbb")
    assert c == copia                                                       # no toca el JSON
    ep = val["entre_promesas"]
    assert (ep["narracion_md5"], ep["narracion_md5_critico"]) == ("bbb", "aaa")
    sec = t[t.index("## Promesas nuevas (código)"):t.index("## Pico")]
    assert mf.AVISO_OTRA_NARRACION in sec
    assert "| desde | hasta | s |\n|---|---|---|\n| ch01:1 | ch02:0 | 8 |\n| ch02:0 | fin | **10 (máx.)** |\n" in sec
    assert "ch07:0 «mala»" in sec
    assert t.index("## Loops") < t.index("## Promesas nuevas (código)") < t.index("## Pico")
    assert t.splitlines()[2] == mf.cabecera_de(c) and "`m01f-1`" in t.splitlines()[2]


def test_misma_narracion_no_lleva_aviso():
    _, t = mf.rerender(_critica("aaa"), CAPS, _met(), "aaa")
    assert "## Promesas nuevas (código)" in t and mf.AVISO_OTRA_NARRACION not in t


def test_critica_md_sin_entre_promesas_no_tiene_la_seccion():
    c = _critica()
    t = mf.critica_md(c["respuesta"], c["validacion"], _met(), "cab")
    assert "## Promesas nuevas" not in t and "## Loops" in t and "## Pico" in t


def test_personaje_segun_la_narracion_con_oraciones():
    c = _critica()
    t = mf.critica_md(c["respuesta"], c["validacion"], _met({"id": "P17", "nombre": "Daniel Écija (padre)", "oraciones": 16}), "cab")
    assert "Personaje según la narración: P17 Daniel Écija (padre) · 16 oraciones" in t and "según la escaleta" not in t
    t = mf.critica_md(c["respuesta"], c["validacion"], _met({"id": "P16", "nombre": "María Bernal"}), "cab")   # m05 viejo: sin `oraciones`
    assert "Personaje según la narración: P16 María Bernal\n" in t
    t = mf.critica_md(c["respuesta"], c["validacion"], _met(None), "cab")
    assert "Personaje según la narración: ninguno (nadie del pool se nombra en la voz)" in t


def test_generar_guarda_entre_promesas_en_json_y_md(env):  # noqa: F811
    r = _generar(env)                                                      # _resp: un loop que abre en ch01:0
    j = json.loads((env["d"] / "01f_critico.json").read_text(encoding="utf-8"))
    ep = j["validacion"]["entre_promesas"]
    assert ep == r["validacion"]["entre_promesas"]
    n3 = md.md5_narracion(json.loads((env["d"] / "01b_narracion_v3.json").read_text(encoding="utf-8")))
    assert ep["narracion_md5"] == ep["narracion_md5_critico"] == n3 == j["narracion_md5"]
    met = json.loads((env["d"] / "06_judge_narrative.json").read_text(encoding="utf-8"))["retencion"]
    assert ep["seg_por_palabra"] == met["seg_por_palabra"]
    assert [(t["desde"], t["hasta"], t["segundos"]) for t in ep["tramos"]] == [("ch01:0", "fin", round(met["total_palabras"] * met["seg_por_palabra"]))]
    t = (env["d"] / "01f_critico.md").read_text(encoding="utf-8")
    assert "## Promesas nuevas (código)" in t and mf.AVISO_OTRA_NARRACION not in t


def test_generar_sin_json_no_calcula(env):  # noqa: F811
    r = _generar(env, post=lambda b: _msg("no"))
    assert "entre_promesas" not in r["validacion"]


def test_entre_promesas_no_llama_a_velocidad(monkeypatch):
    from script_engine import m01e_pantalla as mp

    def explota(*a, **k):
        raise AssertionError("B usa metricas['seg_por_palabra'], nunca velocidad()")
    monkeypatch.setattr(mp, "velocidad", explota)
    mf.rerender(_critica(), CAPS, _met(), "x")
