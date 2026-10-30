"""
test_module_f16.py — F16 (escaleta v2): el sistema v2 byte-idéntico al archivo del analista; el usuario con la forma
del archivo (caso, ficha con historia y escenas primero, tarea literal al final; sin reglas, sin FEWSHOT, sin notas);
(F39 §A.2: el camino sin ficha se borró, con sus tests; ver test_module_f39_escaleta); los 13 bloqueantes (un caso cada uno, sobre los fixtures de test_module_f6b); una sola
regeneración y después PARADA; las métricas no rechazan; sin `instrucciones_guionista` con ficha; Sol high por
defecto. Sin red.
"""
from __future__ import annotations

import copy
from pathlib import Path

import pytest

from script_engine import m01a_escaleta as me
from test_module_f6b import POOL, _pool3, good

F16 = Path(__file__).resolve().parent / "lab" / "hyperframes" / "f16"

FICHA = {"prompt_version": "f15-1",
         "historia": {"humanos_candidatos": [{"nombre": "Edward Burton", "rol": "preso", "arco": "entra, sufre, sale",
                                              "ids": ["P08", "Q01"], "citas_verificadas": 1}],
                      "giros": [{"orden": 1, "que_cambia": "el sheriff no evacúa", "ids": ["T01"]},
                                {"orden": 2, "que_cambia": "se corta la luz", "ids": ["T02"]},
                                {"orden": 3, "que_cambia": "algo que no entra", "ids": ["D10"]}],
                      "pico": {"que": "los cadáveres", "por_que": "todo lo prepara", "ids": ["D08"]},
                      "pregunta_final": {"pregunta": "¿Cuántos siguen sin nombre?", "ids": ["D02"]}},
         "escenas": [{"donde": "celda", "quien": "presos", "que_pasa": "sube el agua", "sentidos": "agua al pecho",
                      "ids": ["D01"]}],
         "personas": [{"nombre": "Edward Burton", "rol": "preso", "ids": ["P08"]}],
         "hechos": [{"texto": "El agua llegó al pecho.", "nivel": 1, "sirve_para": "escalada", "ids": ["D01"]},
                    {"texto": "Catorce órdenes de arresto.", "nivel": 2, "sirve_para": "contexto", "ids": ["D10"]}],
         "citas": [{"texto": "Nadie allí, nos dejaron por muertos", "autor": "Edward Burton", "rol": "preso",
                    "ids": ["Q01"]}],
         "versiones": [{"tema": "muertes", "versiones": [{"dice": "ningún preso murió", "doc_id": "F01", "ids": ["D09"]}]}]}
TOPIC = {"id": "t-f16", "video_title": "Orleans", "angle": "a", "mystery": "m", "reveal": "r", "evidence_pool": POOL}


def _sistema_md() -> tuple[str, str]:
    md = (F16 / "PROMPT_ESCALETA_v2.md").read_text(encoding="utf-8").replace("\r\n", "\n")
    i0 = md.index("\n## SISTEMA\n\n") + len("\n## SISTEMA\n\n")
    u0 = md.index("\n## USUARIO")
    return (md[i0:md.index("</errores>", i0) + len("</errores>")],
            md[md.index("<tarea>", u0):md.index("</tarea>", u0) + len("</tarea>")])


# ═══════════════════════════════════════════════════════════════
#  Prompt v2 (§1.1)
# ═══════════════════════════════════════════════════════════════

def test_sistema_v2_byte_identico_al_archivo():
    sis, tarea = _sistema_md()
    # F22: la v2 de F16 queda con su versión, byte-idéntica (la v2.1 en test_module_f22)
    assert me.TAREA_V2 == tarea                       # F55 C.0 (ii): la constante SYSTEM_V2_F16_1 se borró; el .md queda
    assert sis.startswith("<rol>\nSos el guionista jefe") and sis.endswith("</errores>")


def test_usuario_v2_con_la_forma_del_archivo():
    p = me.build_prompt_v2(TOPIC, POOL, FICHA)
    assert p.startswith("<caso>") and p.endswith(me.TAREA_V2)
    assert p.index("<caso>") < p.index("<ficha>") < p.index("</ficha>") < p.index("<tarea>")
    assert p.index("historia:") < p.index("escenas:") < p.index("personas:") < p.index("hechos nivel 1:") \
        < p.index("hechos nivel 2:") < p.index("citas:") < p.index("versiones en disputa:")
    for viejo in ("REGLAS DE LA ESCALETA", "CÓMO SE VE UNA BUENA ESCALETA", "INDICACIONES DEL EDITOR", "<rechazo>"):
        assert viejo not in p
    assert "E1. celda" in p and "· — ·" in p                                     # Q01 sin verificación en POOL
    assert "VERIFICADA" in me.build_prompt_v2(TOPIC, _pool3(), FICHA)           # en _pool3, Q01 está verificada


# ═══════════════════════════════════════════════════════════════
#  Los 13 bloqueantes (§1.3): un caso cada uno
# ═══════════════════════════════════════════════════════════════

def _bloq(e, pool=POOL):
    return me.bloqueantes(e, pool, FICHA)


def _mut(fn, pool=POOL):
    e = good()
    fn(e)
    return _bloq(e, pool)


def test_escaleta_buena_sin_bloqueantes():
    esc, bloq, rep, otros = _bloq(good())
    assert bloq == []


@pytest.mark.parametrize("nombre, fn", [
    ("beats entre 7 y 14", lambda e: e.update(beats=e["beats"][:6])),
    ("caps 1–7 en orden", lambda e: e["beats"][2].update(cap=5)),
    ("el beat 1 es el gancho", lambda e: e["beats"][0].update(funcion="planteo")),
    ("dato_central existe", lambda e: e["beats"][3].update(dato_central="D99")),
    ("un id en un solo beat", lambda e: e["beats"][3].update(dato_central="T01")),
    ("el pico es un beat", lambda e: e["pico"].update(beat=99)),
    ("el pico no es el último beat", lambda e: e["pico"].update(beat=8)),
    ("humano es persona de la ficha", lambda e: e["humano"].update(id="P99")),
    ("antagonista es persona de la ficha", lambda e: e["antagonista"].update(id="P99")),
    ("a_pantalla no repite un id de un beat", lambda e: e.update(a_pantalla=[{"id": "Q01", "cap": 1}])),
])
def test_bloqueante_rechaza(nombre, fn):
    bloq = _mut(fn)[1]
    assert bloq and all(me.bloqueante_de(b) for b in bloq), (nombre, bloq)


def test_otra_cifra_del_mismo_conteo():
    pool = _pool3()
    esc, bloq, rep, _ = _mut(lambda e: e["beats"][4].update(datos_apoyo=["D11"]), pool)   # apoyo → sale (reparación)
    assert bloq == [] and esc["beats"][4]["datos_apoyo"] == [] and any("otra cifra del conteo" in r for r in rep)
    bloq = _mut(lambda e: e["beats"][4].update(dato_central="D11"), pool)[1]                 # dato central → rechazo
    assert any(me.bloqueante_de(b) == "otra cifra del mismo conteo fuera" for b in bloq)


def test_reparaciones_que_no_rechazan():
    pool = _pool3()
    esc, bloq, rep, _ = _mut(lambda e: e["humano"].update(nombre="Edgar"), pool)             # nombre exacto
    assert bloq == [] and esc["humano"]["nombre"] == "Edward Burton"
    esc, bloq, rep, _ = _mut(lambda e: e.update(a_pantalla=[{"id": "Q03", "cap": 3}]), pool)  # cita sin verificar
    assert bloq == [] and esc["a_pantalla"] == [] and any("sin verificar" in r for r in rep)
    esc, bloq, rep, _ = _mut(lambda e: e["beats"][2].update(datos_apoyo=["T01"]), pool)       # apoyo repetido
    assert bloq == [] and esc["beats"][2]["datos_apoyo"] == []


def test_lo_demas_de_validate_no_rechaza():
    def peor(e):
        e["beats"][0].update(intensidad=4)                                     # baja antes del pico (sin flash-forward)
        e["beats"][2].update(imagen_sensorial="la desesperación")              # imagen abstracta / corta
        e["beats"][2].update(humano_en_escena=True)                            # humano en escena sin dato verificado
        e["beats"][1]["pregunta_pantalla"] = "Era cierto"                      # pregunta de pantalla mal formada
    esc, bloq, rep, otros = _mut(peor, _pool3())
    assert bloq == [] and len(otros) >= 4
    m = me.metricas_escaleta(esc, _pool3(), FICHA, otros)
    assert m["curva_problemas"] and m["imagenes_abstractas"]             # F54: la promesa con cifras ya no se mide


# ═══════════════════════════════════════════════════════════════
#  Una sola regeneración, PARADA, sin instrucciones, Sol (§1.2–1.4)
# ═══════════════════════════════════════════════════════════════

def _run(respuestas, monkeypatch, tmp_path):
    monkeypatch.setattr(me, "STEPS_DIR", tmp_path)
    monkeypatch.setattr(me, "pool_gate_profile", lambda *a, **k: None)
    prompts = []

    def call(prompt, **kw):
        prompts.append((prompt, kw.get("system_instruction"), kw.get("response_schema")))
        return copy.deepcopy(respuestas[len(prompts) - 1])
    return prompts, (lambda: me.generate_escaleta(TOPIC, call=call, persist=False, ficha=FICHA))


def test_una_sola_regeneracion_y_parada(monkeypatch, tmp_path):
    mala = good()
    mala["pico"]["beat"] = 99
    prompts, go = _run([mala, mala, good()], monkeypatch, tmp_path)
    with pytest.raises(me.EscaletaValidationError, match="PARADA"):
        go()
    assert len(prompts) == 2 and "<rechazo>" not in prompts[0][0] and "<rechazo>" in prompts[1][0]
    assert all(s == me.SYSTEM_V2 and sch is me.SCHEMA_FICHA for _, s, sch in prompts)


def test_regeneracion_que_pasa_y_sin_instrucciones(monkeypatch, tmp_path):
    mala = good()
    mala["antagonista"]["id"] = "P99"
    prompts, go = _run([mala, good()], monkeypatch, tmp_path)
    esc = go()
    assert len(prompts) == 2 and esc["prompt_version"] == me.PROMPT_VERSION_V2
    assert "instrucciones_guionista" not in esc and "caps" in esc and "_metricas" in esc
    m = esc["_metricas"]
    assert m["giros_total"] == 3 and m["giros_con_beat"] == 2 and m["humano_en_candidatos"] is True
    assert m["pico_es_el_de_la_ficha"] is True


def test_escaleta_v2_usa_sol_high(monkeypatch, tmp_path):
    import gpt_helpers
    seen = {}

    def fake_make_call(model, effort=None, post=None):
        seen["m"] = (model, effort)
        return lambda prompt, **kw: copy.deepcopy(good())
    monkeypatch.setattr(gpt_helpers, "make_call", fake_make_call)
    monkeypatch.setattr(me, "STEPS_DIR", tmp_path)
    monkeypatch.setattr(me, "pool_gate_profile", lambda *a, **k: None)
    # F25c: la escaleta v2 va con Fable por defecto (test_module_f25c); Sol sigue con modelo="gpt-6.1-sol"
    me.generate_escaleta(TOPIC, persist=False, ficha=FICHA, modelo="gpt-6.1-sol")
    assert seen["m"] == ("gpt-6.1-sol", "high")


def test_ids_v2_lee_el_id_del_texto():
    e = good()
    e["beats"][0]["dato_central"] = "Q01: Burton bebe del inodoro. Usar aquí ese recuerdo."
    e["beats"][1]["datos_apoyo"] = ["D03 (Burton ve a los guardias irse)", "T03, D10: dos cosas"]
    e["pico"]["id"] = "D08 — los cadáveres"
    e["humano"]["id"] = "P08 (Edward Burton)"
    out, rep = me.ids_v2(e)
    assert out["beats"][0]["dato_central"] == "Q01" and out["beats"][1]["datos_apoyo"] == ["D03", "T03", "D10"]
    assert out["pico"]["id"] == "D08" and out["humano"]["id"] == "P08" and len(rep) >= 4
    assert me.bloqueantes(out, POOL, FICHA)[1] == []
    sin_id = good()
    sin_id["beats"][3]["dato_central"] = "una explicación sin id"
    assert any(me.bloqueante_de(b) == "dato_central existe" for b in me.bloqueantes(me.ids_v2(sin_id)[0], POOL, FICHA)[1])
