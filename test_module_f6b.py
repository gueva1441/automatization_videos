"""F6b: m01a_escaleta — validador (curva, un id por beat, humano, gancho, rúbrica de preguntas), reparaciones,
pool plan heredado de m01a_skeleton, frozen y flag v3. Sin red."""
from __future__ import annotations

import copy
import json

import pytest

from script_engine import m01a_escaleta as me

POOL = {
    "datos": [{"id": f"D{k:02d}", "texto": t, "tipo": "cifra", "valor": v, "bloque": "tecnico"} for k, (t, v) in enumerate([
        ("El agua llegó al nivel del pecho en Templeman 1 y 2", None),
        ("517 reclusos no estaban contabilizados", "517"),
        ("Edward Burton vio a los guardias abandonar Templeman III", None),
        ("Había 6,375 reclusos en la prisión", "6,375"),
        ("Un jurado otorga $650,000 a dos turistas de Ohio", "650,000"),
        ("Edward Burton pasó días en una celda sin luz ni ventilación", None),
        ("Los presos rompieron ventanas para respirar", None),
        ("Reclusos vieron cadáveres flotando en el agua", None),
        ("El sheriff declaró que ningún preso murió", None),
        ("Catorce órdenes de arresto para fugitivos", None)], start=1)],
    "cronologia": [{"id": "T01", "fecha": "2005-08-28", "evento": "El sheriff anuncia que no evacuará la prisión."},
                   {"id": "T02", "fecha": "2005-08-29", "evento": "Se corta la luz y fallan los generadores."},
                   {"id": "T03", "fecha": "2005-09-01", "evento": "Termina la evacuación."}],
    "citas": [{"id": "Q01", "texto": "Nadie allí, nos dejaron por muertos", "autor": "Edward Burton", "testimonio": True},
              {"id": "Q02", "texto": "Están en la cárcel, hombre", "autor": "Sheriff Gusman", "testimonio": False}],
    "lugares": [{"id": "L01", "nombre": "Templeman III"}],
    "personajes": [{"id": "P01", "nombre": "Marlin N. Gusman", "rol": "sheriff", "antagonista": True},
                   {"id": "P08", "nombre": "Edward Burton", "rol": "preso", "testigo": True, "presente_en": ["T02"]}],
}


def _beat(n, cap, central, inten, q="", *, fn="escalada", hum=False, img="agua negra subiendo por la escalera de la celda",
          words=0):
    return {"n": n, "cap": cap, "funcion": fn, "emocion": "miedo", "intensidad": inten, "dato_central": central,
            "datos_apoyo": [], "humano_en_escena": hum, "imagen_sensorial": img, "pregunta_abierta": "¿y ahora?",
            "pregunta_pantalla": q, "cierre": "anticipa lo que sigue", "palabras_objetivo": words}


def good() -> dict:
    return {"humano": {"id": "P08", "nombre": "Edward Burton", "rol": "preso", "por_que": "estuvo ahí", "colectivo": False},
            "antagonista": {"id": "P01"}, "promesa_gancho": "Esa noche dejaron a miles encerrados con el agua subiendo.",
            "pico": {"beat": 6, "id": "D08", "por_que": "los cadáveres"}, "cierre_humano": "¿Cuántos siguen sin nombre?",
            "beats": [
                _beat(1, 1, "Q01", 2, "¿Quién dejó a Edward Burton ahí?", fn="gancho", hum=True, words=110),
                {**_beat(2, 2, "T01", 2, "¿Por qué el sheriff no los sacó?", hum=True, words=190), "datos_apoyo": ["D03"]},
                _beat(3, 3, "T02", 3, "¿Quién apagó las luces de la prisión?", words=190),
                {**_beat(4, 4, "D01", 4, "¿Por qué nadie abrió las celdas?", hum=True, words=190), "datos_apoyo": ["D06"]},
                _beat(5, 5, "D02", 4, words=100),
                _beat(6, 5, "D08", 5, "¿Dónde están los 517 reclusos?", fn="pico", words=90),
                _beat(7, 6, "D09", 1, "¿Por qué mintió el sheriff?", fn="respiro", words=190),
                _beat(8, 7, "D05", 2, "¿Cuántos siguen sin nombre en la prisión?", fn="cierre", words=110)]}


def test_escaleta_buena_pasa():
    esc, hard, rep, warn = me.validate(good(), POOL)
    assert hard == [] and rep == [] and all(b.get("pregunta_valida", True) for b in esc["beats"])


@pytest.mark.parametrize("mut, frag", [
    (lambda e: e["beats"][3].update(intensidad=2), "baja antes del pico"),
    (lambda e: e["beats"][6].update(intensidad=2), "respiro"),
    (lambda e: e["beats"][4].update(dato_central="Q01"), "un id, un solo beat"),
    (lambda e: e["beats"][4].update(dato_central="D99"), "no existe"),
    (lambda e: e.update(promesa_gancho="En 2005 todo se inundó."), "promesa del gancho"),
    (lambda e: e["beats"][0].update(imagen_sensorial="la desesperación y la injusticia del sistema"), "ver, oír"),
    (lambda e: [b.update(humano_en_escena=False) for b in e["beats"][1:]], "en escena"),
    (lambda e: e["beats"][6].update(humano_en_escena=True), "sin un dato suyo"),
    (lambda e: e["humano"].update(id="P99"), "no es una persona del pool"),
    (lambda e: e["beats"].pop(), "beats"),
    (lambda e: e["beats"][0].update(funcion="planteo"), "gancho"),
    (lambda e: e["pico"].update(beat=8), "último beat"),
])
def test_rechazos_duros(mut, frag):
    e = good()
    mut(e)
    _, hard, _, _ = me.validate(e, POOL)
    assert any(frag in h for h in hard), hard


def test_reparaciones_mecanicas():
    e = good()
    e["beats"][2]["palabras_objetivo"] = 400                       # cap 3 se pasa → se escala
    e["beats"][3]["datos_apoyo"] = ["D99", "Q01", "D06"]             # inexistente y repetido → fuera (D06 queda)
    e["pico"]["id"] = "D02"                                          # no es el central de su beat
    e["humano"]["nombre"] = "edward burton"
    esc, hard, rep, _ = me.validate(e, POOL)
    assert hard == [] and esc["beats"][2]["palabras_objetivo"] == 190 and esc["beats"][3]["datos_apoyo"] == ["D06"]
    assert esc["pico"]["id"] == "D08" and esc["humano"]["nombre"] == "Edward Burton" and len(rep) == 5


def test_rubrica_de_preguntas():
    known = "Edward Burton el sheriff las celdas de Templeman la prisión 517 reclusos"
    ok = me.question_problems("¿Por qué nadie abrió las celdas?", known, False, ["Edward Burton"])
    assert ok == []
    assert me.question_problems("¿Quién pagó la indemnización a los turistas?", known, False, [])
    assert any("palabras" in p for p in me.question_problems("¿Quién decidió que los presos de la cárcel se quedaran "
                                                             "encerrados sin luz?", known, False, []))
    assert any("nombre propio" in p for p in me.question_problems("¿Quién avisó a Kathleen Blanco?", known, False, []))
    assert any("culpa" in p for p in me.question_problems("¿Llovió mucho esa noche?", known, False, []))
    assert any("¿" in p for p in me.question_problems("Quién apagó las luces", known, False, []))


def test_pregunta_mala_en_el_ultimo_intento_queda_marcada():
    e = good()
    e["beats"][2]["pregunta_pantalla"] = "¿Qué pasó con los generadores?"
    _, hard, _, _ = me.validate(e, POOL)
    assert any("generadores" in h for h in hard)
    esc, hard, _, warn = me.validate(e, POOL, final=True)
    assert hard == [] and esc["beats"][2]["pregunta_valida"] is False and any("generadores" in w for w in warn)


def test_colectivo_sin_nombre_inventado():
    e = good()
    e["humano"] = {"id": "Q01", "nombre": "un preso de Templeman III, 19 años", "rol": "preso", "por_que": "x",
                   "colectivo": True, "fuente": "Q01"}
    assert me.validate(e, POOL)[1] == []
    e["humano"]["nombre"] = "Juan Pérez, preso de Templeman III"
    assert any("inventado" in h for h in me.validate(e, POOL)[1])


def test_generate_con_reintento_pool_plan_y_frozen(tmp_path, monkeypatch):
    monkeypatch.setattr(me, "STEPS_DIR", tmp_path)
    bad = good()
    bad["beats"][3]["intensidad"] = 1
    calls = []

    def fake(prompt, **kw):
        calls.append(prompt)
        return bad if len(calls) == 1 else good()
    topic = {"id": "t1", "evidence_pool": copy.deepcopy(POOL), "video_title": "X"}
    esc = me.generate_escaleta(topic, call=fake)
    assert len(calls) == 2 and "CORREGÍ" in calls[1] and "baja antes del pico" in calls[1]
    assert [c["chapter_number"] for c in esc["caps"]] == list(range(1, 8))
    assert esc["caps"][0]["evidence_ids"] == ["Q01"] and esc["caps"][0]["cliffhanger"] == "T01"
    assert all("pantalla_ids" in c for c in esc["caps"]) and esc["_pool_plan"] is not None
    saved = tmp_path / "t1" / "01a_escaleta.json"
    assert json.loads(saved.read_text(encoding="utf-8"))["humano"]["id"] == "P08"
    fz = me.generate_escaleta({**topic, "escaleta_frozen": {"escaleta": str(saved)}},
                              call=lambda *a, **k: pytest.fail("frozen no llama a Pro"))
    assert fz["beats"][0]["dato_central"] == "Q01" and fz["_frozen"]["problemas"] == []


def test_flag_v3_y_camino_v2(monkeypatch):
    monkeypatch.delenv("GUION_V3", raising=False)
    assert not me.is_v3({"evidence_pool": POOL}) and me.is_v3({"evidence_pool": POOL, "guion_version": 3})
    assert not me.is_v3({"guion_version": 3})                                   # sin pool: siempre v2
    monkeypatch.setenv("GUION_V3", "1")
    assert me.is_v3({"evidence_pool": POOL})
    with pytest.raises(ValueError):
        me.generate_escaleta({"id": "x"}, call=lambda *a, **k: {})
