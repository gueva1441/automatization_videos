"""F6c: m01b_guionista (prompt, partición por beat → cap, revisión v3) y m01c_editor (guardia léxica, rechazo por
validadores, párrafo rechazado = original). Sin red."""
from __future__ import annotations

import pytest

import copy

from script_engine import m01a_escaleta as me
from script_engine import m01b_guionista as mg
from script_engine import m01c_editor as mc
from test_module_f6b import POOL, good


@pytest.fixture(autouse=True)
def _escaleta_pre_f8(monkeypatch):
    """Las escaletas de prueba son de 8 beats (antes de F8 §2): 1 beat por cap de desarrollo alcanza acá; la regla de
    ≥ 2 se prueba en test_module_f8.py."""
    monkeypatch.setattr(me, "MIN_BEATS_DEV_CAP", 1)


def _setup():
    pool = copy.deepcopy(POOL)
    pool["citas"][0]["verificacion"] = {"estado": "verificada"}
    pool["citas"].append({"id": "Q09", "texto": "Nadie abrió las puertas esa noche", "autor": "Rhonda Ducre",
                          "testimonio": True, "verificacion": {"estado": "sin_verificar"}})
    pool["personajes"][1]["testigo_verificado"] = True
    pool["datos"].append({"id": "D11", "texto": "Más de 500 prisioneros no figuraban en la lista", "tipo": "cifra",
                          "valor": "500", "bloque": "humano"})
    esc, hard, _, _ = me.validate(good(), pool)
    assert hard == []
    me.apply_pool_plan(esc, pool)
    topic = {"id": "t", "video_title": "La prisión", "evidence_pool": pool, "verified_facts": []}
    return topic, esc, pool


def _p(beat, cap, texto, ids=()):
    return {"beat": beat, "cap": cap, "texto": texto, "ids_usados": list(ids)}


def test_prompt_y_particion():
    topic, esc, _ = _setup()
    pr = mg.build_prompt(topic, esc, ["cap 2: faltan datos"])
    assert "BEAT 1" in pr and "Edward Burton" in pr and "CORREGÍ" in pr and "≤ 12 palabras" in pr
    ps = mg.normalize({"parrafos": [{"beat": 1, "texto": "Agua negra.", "ids_usados": ["[q01]"]},
                                    {"beat": 99, "texto": "fuera"}, {"beat": 2, "texto": ""}]}, esc)
    assert ps == [{"beat": 1, "cap": 1, "texto": "Agua negra.", "ids_usados": ["Q01"]}]
    caps = mg.caps_text(esc, [_p(1, 1, "A."), _p(2, 2, "B."), _p(3, 3, "C.", ["T02"])])
    assert [c["chapter_number"] for c in caps] == list(range(1, 8)) and caps[2]["datos_usados"] == ["T02"]


def test_revision_v3_detecta_gancho_ritmo_citas_y_conteo():
    topic, esc, _ = _setup()
    larga = " ".join(["palabra"] * 32) + "."
    ps = [_p(1, 1, "En 2005 la prisión de Orleans se inundó. Había 517 presos adentro. " + larga, ["D02"]),
          _p(2, 2, "Rhonda Ducre lo dijo: «Nadie abrió las puertas esa noche». Y eran 517 reclusos.", ["Q09", "D02"])]
    rv = mg.review(topic, esc, ps)
    h = " | ".join(rv["hard"])
    assert "gancho: la primera frase" in h and "más de 30 palabras" in h
    assert "Q09 está SIN VERIFICAR" in h and "la cifra 517 suena 2 veces" in h
    assert "faltan los beats" in h and "Edward Burton aparece por nombre" in h


def test_editor_guardia_y_rechazo_por_validadores():
    topic, esc, _ = _setup()
    orig = [_p(1, 1, "El agua subía por los barrotes. Nadie vino. Edward Burton esperó en la celda oscura toda la noche.",
               ["Q01"]),
            _p(2, 2, "El sheriff anunció que no los iba a evacuar. Fue el 28 de agosto.", ["T01"])]
    assert mc.lexical_guard(orig[0]["texto"], orig[0]["texto"].replace("toda la noche", "durante 3 noches"))
    assert "nombres nuevos" in " ".join(mc.lexical_guard(orig[1]["texto"], orig[1]["texto"] + " Lo confirmó Kathleen Blanco."))
    assert mc.lexical_guard(orig[0]["texto"], "El agua subía por los barrotes. Nadie vino.") == []

    def fake(prompt, **kw):
        return {"parrafos": [
            {"beat": 1, "texto": "El agua subía por los barrotes. Nadie vino.", "ids_usados": []},       # acorta: ok
            {"beat": 2, "texto": "El sheriff anunció que no los iba a evacuar. Eran 300 presos.", "ids_usados": ["T01"]}],
            "cambios": [{"parrafo": 0, "antes": "x", "despues": "y", "motivo": "corta"},
                        {"parrafo": 1, "antes": "x", "despues": "y", "motivo": "ritmo"}]}
    out = mc.edit(topic, esc, orig, call=fake)
    st = {c["parrafo"]: c for c in out["cambios"]}
    assert st[1]["estado"] == "rechazado" and "cifras nuevas" in st[1]["motivo_rechazo"]
    assert out["parrafos"][1]["texto"] == orig[1]["texto"]                    # vuelve el original del guionista
    # el párrafo 0 pierde el nombre del humano: si los validadores empeoran, también se rechaza
    assert st[0]["estado"] in ("aceptado", "rechazado")
    if st[0]["estado"] == "rechazado":
        assert st[0]["motivo_rechazo"].startswith("validadores")
    bad = mc.edit(topic, esc, orig, call=lambda *a, **k: {"parrafos": [], "cambios": []})
    assert bad["parrafos"] == orig and bad["aceptados"] == 0


def test_write_best_of_2_reintenta_con_las_duras():
    topic, esc, _ = _setup()
    prompts = []

    def fake(prompt, **kw):
        prompts.append(prompt)
        return {"parrafos": [{"beat": 1, "texto": "En 2005 todo cambió.", "ids_usados": []}]}
    out = mg.write(topic, esc, call=fake)
    assert len(prompts) == 2 and "CORREGÍ" in prompts[1] and out["elegido"] in (1, 2)
    assert len(out["_intentos"]) == 2 and out["revision"]["hard"]
