# -*- coding: utf-8 -*-
"""F67 A: `m05_narrative.retencion`, con una narración sintética de 2 caps: racha conocida, pico en el último párrafo del cap 1,
promesa con 2 cifras (una dentro de la ventana del gancho y otra afuera) y los casos sin pico, sin personaje e institución."""
import json

import pytest

from script_engine import m05_narrative as m5

SEG = 0.5                                                     # ventana del gancho: round(30 / 0,5) = 60 palabras
PERSONA = {"id": "P1", "nombre": "Ana Pérez", "rol": "minera"}
POOL = {"personajes": [PERSONA, {"id": "P2", "nombre": "Luis Gómez"}]}
SK = {"chapters": [{"chapter_number": 1, "title": "Uno"}, {"chapter_number": 2, "title": "Dos"}], "personajes": [PERSONA]}
ESC = {"humano": {"id": "P1"}, "pico": {"beat": 2}, "promesa_gancho": "Murieron 40 mineros y quedaron 1.500 toneladas."}
RELLENO = " ".join(["palabra"] * 60)
PARS = [{"cap": 1, "beat": 1, "texto": f"En 1950 murieron 40 mineros. Ana Pérez llegó. {RELLENO}. Nadie habló.", "ids_usados": []},
        {"cap": 1, "beat": 2, "texto": "Quedaron 1.500 toneladas. Era 1960. Bernal calló.", "ids_usados": []},
        {"cap": 2, "beat": 3, "texto": "El polvo voló. Pasaron los años. Ana Pérez murió. Cerró la mina.", "ids_usados": []}]


def _r(pars=PARS, sk=SK, esc=ESC):
    return m5.retencion(pars, sk, esc, POOL, SEG)


def test_por_cap():
    r = _r()
    assert r["seg_por_palabra"] == SEG and [c["cap"] for c in r["caps"]] == ["ch01", "ch02"]
    a, b = r["caps"]
    assert (a["titulo"], a["oraciones"]) == ("Uno", 7) and b["oraciones"] == 4
    assert a["palabras"] == len(m5.words_of(PARS[0]["texto"] + " " + PARS[1]["texto"]))
    assert a["palabras"] + b["palabras"] == r["total_palabras"] and a["segundos"] == round(a["palabras"] * SEG)
    assert a["anios_distintos"] == 2 and a["anios_por_min"] == round(2 / (a["segundos"] / 60), 2)
    assert b["pct_acumulado"] == 100 and a["pct_acumulado"] == round(100 * a["palabras"] / r["total_palabras"])
    assert b["anios_distintos"] == 0 and b["anios_por_min"] == 0.0


def test_racha_conocida():
    a, b = _r()["caps"]
    # ch01: [0] sin, [1] Ana, [2] relleno, [3] sin, [4] sin, [5] sin, [6] sin → racha 5 de [2] a [6]
    assert a["oraciones_con_personaje"] == 1 and a["personaje_en_voz"] is True
    assert (a["racha_max_sin_personaje"], a["racha_desde_hasta"]) == (5, [2, 6])
    # ch02: [0] sin, [1] sin, [2] Ana, [3] sin → racha 2, la primera
    assert (b["racha_max_sin_personaje"], b["racha_desde_hasta"]) == (2, [0, 1])


def test_cap_mas_humano_y_cociente():
    r = _r()
    assert r["cap_mas_humano"] == "ch02"                  # menor racha
    assert r["anios_por_min_vs_mas_humano"] == {"ch01": None, "ch02": None}   # denominador 0 → null


def test_cap_mas_humano_empate_y_el_primero():
    pars = [{"cap": 1, "beat": 1, "texto": "Ana Pérez llegó. Nadie habló.", "ids_usados": []},
            {"cap": 2, "beat": 2, "texto": "Ana Pérez habló en 1950. Ana Pérez calló. Nadie vino.", "ids_usados": []},
            {"cap": 3, "beat": 3, "texto": "Ana Pérez sigue. Nadie volvió.", "ids_usados": []}]
    r = _r(pars)
    assert r["cap_mas_humano"] == "ch02"                  # empate de racha → mayor proporción
    pars[1]["texto"] = "Ana Pérez habló en 1950. Nadie vino."
    assert _r(pars)["cap_mas_humano"] == "ch01"           # empate persistente → el primero


def test_pico_en_el_ultimo_parrafo_del_cap_1():
    r = _r()
    p = r["pico"]
    assert (p["beat"], p["cap"], p["idx_ultima_oracion"]) == (2, "ch01", 6) and r["pico_motivo"] is None
    assert p["pct_acumulado"] == r["caps"][0]["pct_acumulado"]
    assert p["segundos_despues"] == round(r["caps"][1]["palabras"] * SEG)
    assert p["oraciones_siguientes"] == ["El polvo voló.", "Pasaron los años.", "Ana Pérez murió."] and p["n_siguientes"] == 3
    assert p["personaje_en_siguientes"] is True


def test_pico_sin_personaje_en_las_siguientes():
    pars = [dict(PARS[0]), dict(PARS[1]), {"cap": 2, "beat": 3, "texto": "El polvo voló. Pasaron los años. Nadie vino. Ana Pérez murió.",
                                           "ids_usados": []}]
    assert _r(pars)["pico"]["personaje_en_siguientes"] is False


def test_promesa_una_en_la_ventana_y_otra_afuera():
    pr = _r()["promesa"]
    assert pr["cifras"] == ["40", "1500"] and pr["cifras_en_gancho"] == ["40"] and pr["faltan"] == ["1500"] and pr["motivo"] is None


def test_promesa_sin_cifras_en_digitos_y_sin_promesa():
    pr = _r(esc={**ESC, "promesa_gancho": "Un minero vivió diez meses."})["promesa"]
    assert pr["cifras"] == [] and pr["faltan"] == [] and pr["motivo"] == "sin cifras en dígitos" and pr["texto"]
    pr = _r(esc={k: v for k, v in ESC.items() if k != "promesa_gancho"})["promesa"]
    assert pr["texto"] is None and pr["motivo"]


def test_sin_pico():
    r = _r(esc={k: v for k, v in ESC.items() if k != "pico"})
    assert r["pico"] is None and r["pico_motivo"]
    r = _r(esc={**ESC, "pico": {"beat": 99}})
    assert r["pico"] is None and "99" in r["pico_motivo"]


@pytest.mark.parametrize("sk,esc", [
    ({**SK, "personajes": []}, ESC),                                                          # no está en el skeleton
    ({**SK, "personajes": [{**PERSONA, "tipo": "institucion"}]}, ESC),                        # institución
    (SK, {k: v for k, v in ESC.items() if k != "humano"}),                                    # sin humano
])
def test_sin_personaje_o_institucion(sk, esc):
    r = _r(sk=sk, esc=esc)
    assert r["personaje"] is None and r["personaje_motivo"] and r["cap_mas_humano"] is None
    assert r["anios_por_min_vs_mas_humano"] is None and r["pico"]["personaje_en_siguientes"] is None
    c = r["caps"][0]
    assert c["personaje_en_voz"] is None and c["racha_max_sin_personaje"] is None and c["racha_desde_hasta"] is None
    assert c["palabras"] > 0                              # lo demás se mide igual


def test_personaje_terminos():
    assert _r()["personaje"] == {"id": "P1", "nombre": "Ana Pérez", "terminos": ["ana perez", "perez"]}


def test_judge_narration_lee_del_disco_y_guarda_retencion(tmp_path, monkeypatch):
    import script_engine.m01e_pantalla as mp
    monkeypatch.setattr(mp, "velocidad", lambda seg=None: {"valor": SEG})
    d = tmp_path / "t"
    d.mkdir()
    (d / "01b_narracion_v3.json").write_text(json.dumps({"parrafos": PARS}), encoding="utf-8")
    (d / "01a_escaleta.json").write_text(json.dumps(ESC), encoding="utf-8")
    nar = {"chapters": [{"chapter_number": 1, "narration": "En 1950 murieron."}]}
    rep = m5.judge_narration("t", steps_dir=tmp_path, pool=POOL, narration=nar, skeleton=SK)
    assert rep["retencion"]["total_palabras"] > 0 and rep["retencion"]["pico"]["beat"] == 2
    assert json.loads((d / "06_judge_narrative.json").read_text(encoding="utf-8"))["retencion"]["cap_mas_humano"] == "ch02"
    # por kwargs manda lo que se pasa, no el disco
    rep = m5.judge_narration("t", steps_dir=tmp_path, pool=POOL, narration=nar, skeleton=SK, parrafos=PARS[:1], escaleta={})
    assert rep["retencion"]["pico"] is None and [c["cap"] for c in rep["retencion"]["caps"]] == ["ch01"]


def test_judge_narration_sin_parrafos_retencion_none(tmp_path):
    nar = {"chapters": [{"chapter_number": 1, "narration": "En 1950 murieron."}]}
    assert m5.judge_narration("t", steps_dir=tmp_path, pool=POOL, narration=nar, skeleton={"chapters": []})["retencion"] is None
