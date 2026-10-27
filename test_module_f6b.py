"""F6b: m01a_escaleta — validador (curva, un id por beat, humano, gancho, rúbrica de preguntas), reparaciones,
pool plan heredado de m01a_skeleton, frozen y flag v3. Sin red."""
from __future__ import annotations

import copy
import json

import pytest

from script_engine import m01a_escaleta as me


@pytest.fixture(autouse=True)
def _escaleta_pre_f8(monkeypatch):
    """Las escaletas de prueba son de 8 beats (antes de F8 §2): 1 beat por cap de desarrollo alcanza acá; la regla de
    ≥ 2 se prueba en test_module_f8.py."""
    monkeypatch.setattr(me, "MIN_BEATS_DEV_CAP", 1)

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
                _beat(1, 1, "Q01", 2, "¿Quién dejó a Edward Burton ahí?", fn="gancho", hum=True, words=me.CAP_WORDS[1]),
                {**_beat(2, 2, "T01", 2, "¿Por qué el sheriff no los sacó?", hum=True, words=me.CAP_WORDS[2]), "datos_apoyo": ["D03"]},
                _beat(3, 3, "T02", 3, "¿Quién apagó las luces de la prisión?", words=me.CAP_WORDS[3]),
                {**_beat(4, 4, "D01", 4, "¿Por qué nadie abrió las celdas?", hum=True, words=me.CAP_WORDS[4]), "datos_apoyo": ["D06"]},
                _beat(5, 5, "D02", 4, words=me.CAP_WORDS[5] - me.CAP_WORDS[5] * 9 // 19),
                _beat(6, 5, "D08", 5, "¿Dónde están los 517 reclusos?", fn="pico", words=me.CAP_WORDS[5] * 9 // 19),
                _beat(7, 6, "D09", 1, "¿Por qué mintió el sheriff?", fn="respiro", words=me.CAP_WORDS[6]),
                {**_beat(8, 7, "D05", 2, "¿Cuántos siguen sin nombre en la prisión?", fn="cierre", words=me.CAP_WORDS[7]),
                 "cierre": "Edward Burton todavía espera que alguien diga cuántos eran."}]}


def test_escaleta_buena_pasa():
    esc, hard, rep, warn = me.validate(good(), POOL)
    assert hard == [] and rep == [] and all(b.get("pregunta_valida", True) for b in esc["beats"])


@pytest.mark.parametrize("mut, frag", [
    (lambda e: e["beats"][3].update(intensidad=2), "baja antes del pico"),
    (lambda e: e["beats"][6].update(intensidad=2), "respiro"),
    (lambda e: e["beats"][4].update(dato_central="Q01"), "un id, un solo beat"),
    (lambda e: e["beats"][4].update(dato_central="D99"), "no existe"),
    (lambda e: e.update(promesa_gancho="En 2005 todo se inundó."), "promesa del gancho"),
    (lambda e: e.update(promesa_gancho="Dejaron a más de seis mil personas encerradas."), "promesa del gancho"),
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
    assert hard == [] and esc["beats"][2]["palabras_objetivo"] == me.CAP_WORDS[3] and esc["beats"][3]["datos_apoyo"] == ["D06"]
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
    _, hard, _, warn = me.validate(e, POOL)
    assert not any("generadores" in h for h in hard) and any("generadores" in w for w in warn)   # F21: métrica
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
    # F39 §A.2: la escaleta sin ficha v2 se borró: va con una ficha v2 mínima (sintética) y el reintento es la
    # regeneración de la v2, con un bloqueante (un dato central que no existe)
    monkeypatch.setattr(me, "STEPS_DIR", tmp_path)
    ficha = {"prompt_version": "test", "historia": {"humanos_candidatos": [{"nombre": "Edward Burton", "ids": ["P08"]}]},
             "personas": [{"nombre": "Edward Burton", "rol": "preso", "ids": ["P08"]}]}
    bad = good()
    bad["beats"][3]["dato_central"] = "D99"
    calls = []

    def fake(prompt, **kw):
        calls.append(prompt)
        return bad if len(calls) == 1 else good()
    topic = {"id": "t1", "evidence_pool": copy.deepcopy(POOL), "video_title": "X"}
    esc = me.generate_escaleta(topic, call=fake, ficha=ficha)
    assert len(calls) == 2 and "<rechazo>" in calls[1] and "D99" in calls[1] and "no existe en el pool" in calls[1]
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


# ═══ F6b-3 ═══

def _pool3():
    pool = copy.deepcopy(POOL)
    pool["datos"].append({"id": "D11", "texto": "Más de 500 prisioneros no figuraban en la lista", "tipo": "cifra",
                          "valor": "500", "bloque": "humano"})
    pool["datos"].append({"id": "D12", "texto": "Edward Burton nadó hasta el segundo piso", "tipo": "cifra", "bloque": "x"})
    pool["citas"].append({"id": "Q03", "texto": "Todavía lo sueño", "autor": "Edward Burton", "testimonio": True,
                          "verificacion": {"estado": "sin_verificar"}})
    pool["citas"].append({"id": "Q04", "texto": "Somos ciudadanos de segunda", "autor": "Eric Balaban", "testimonio": False})
    pool["citas"][0]["verificacion"] = {"estado": "verificada", "url_fuente": "https://x.org/a"}
    pool["personajes"][1]["testigo_verificado"] = True
    return pool


def test_flash_forward_cuenta_la_curva_desde_el_beat_2():
    e = good()
    e["beats"][0].update(intensidad=4, flash_forward=True)
    e["beats"][1]["intensidad"] = 2
    assert me.validate(e, POOL)[1] == []
    e["beats"][2]["flash_forward"] = True
    assert any("solo el beat 1" in h for h in me.validate(e, POOL)[1])
    e = good()
    e["beats"][0].update(intensidad=4)                         # sin la marca, baja al beat 2: rechazo
    assert any("baja antes del pico" in h for h in me.validate(e, POOL)[1])


def test_a_pantalla_conteo_unico_y_cierre_con_testigo():
    pool = _pool3()
    e = good()
    e["a_pantalla"] = [{"id": "Q04", "cap": 7, "por_que": "abogado"}, {"id": "D99", "cap": 2}]
    esc, hard, rep, _ = me.validate(e, pool)
    assert hard == [] and [x["id"] for x in esc["a_pantalla"]] == ["Q04"] and any("D99" in r for r in rep)
    e["a_pantalla"] = [{"id": "Q01", "cap": 1}]                 # está en un beat
    assert any("también está en un beat" in h for h in me.validate(e, pool)[1])
    e = good()
    e["beats"][4]["datos_apoyo"] = ["D11"]                      # la aproximada del conteo 517
    esc, hard, rep, _ = me.validate(e, pool)
    assert esc["beats"][4]["datos_apoyo"] == [] and any("otra cifra del conteo 517" in r for r in rep)
    e["beats"][4]["dato_central"] = "D11"
    assert any("un hecho, una cifra" in h for h in me.validate(e, pool)[1])
    e = good()
    e["beats"][-1]["cierre"] = "Como dijo el abogado, somos ciudadanos de segunda."
    assert any("última frase" in h for h in me.validate(e, pool)[1])


def test_humano_solo_con_datos_verificados():
    pool = _pool3()
    e = good()
    e["beats"][2]["datos_apoyo"] = ["Q03"]                      # cita suya SIN verificar: no lo pone en escena
    e["beats"][2]["humano_en_escena"] = True
    assert any("sin un dato suyo verificado" in h for h in me.validate(e, pool)[1])
    e["beats"][2]["datos_apoyo"] = ["D12"]                      # un dato que lo nombra: vale
    assert me.validate(e, pool)[1] == []


def test_reservados_por_fecha_e_instrucciones(tmp_path, monkeypatch):
    pool = _pool3()
    pool["cronologia"].append({"id": "T04", "fecha": "2005-08-28", "evento": "Los reclusos reciben su última comida."})
    e, _, _, _ = me.validate(good(), pool)
    sk = me.caps_view(e)
    sk["chapters"][4]["pantalla_ids"] = ["T04"]                 # el reparto por palabras lo mandó al cap 5
    e["a_pantalla"] = [{"id": "Q04", "cap": 7}]
    me._screen_by_date(e, sk, pool)
    by = {c["chapter_number"]: c["pantalla_ids"] for c in sk["chapters"]}
    assert by[2] == ["T04"] and by[5] == [] and by[7] == ["Q04"] and "por fecha" in e["_pantalla_por_fecha"][0]
    e["beats"][3]["datos_apoyo"] = ["Q03"]
    ins = me.writer_instructions(e, pool)
    assert any("517" in x and "UNA sola vez" in x and "más de 500" in x for x in ins)
    assert any("Q03" in x and "SIN VERIFICAR" in x for x in ins) and any("Q04 va a pantalla" in x for x in ins)


def test_juez_de_verificacion():
    from researcher_steps import verify_quotes as vq
    chunks = [{"title": "thelensnola.org", "uri": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/abc"}]
    ok = vq.judge({"encontrada": True, "url": chunks[0]["uri"], "cita_original": "left for dead"}, chunks)
    assert ok["estado"] == "verificada"
    assert vq.judge({"encontrada": True, "url": "https://www.thelensnola.org/x"}, chunks)["estado"] == "verificada"
    assert vq.judge({"encontrada": True, "url": "https://aclu.org/x"}, [])["estado"] == "sin_verificar"
    assert vq.judge({"encontrada": False}, chunks)["estado"] == "sin_verificar"
    pool = {"citas": [{"id": "Q01", "texto": "x", "autor": "Edward Burton", "testimonio": True},
                      {"id": "Q02", "texto": "y", "autor": "un preso anónimo", "testimonio": True}],
            "personajes": [{"id": "P01", "nombre": "Edward Burton"}]}
    calls = []

    def fake(prompt, model=None):
        calls.append(model)
        return ('{"encontrada": true, "url": "https://thelensnola.org/a"}' if model else '{"encontrada": false}', chunks)
    n = vq.verify_testimonios(pool, search=fake, resolve=None, retry_model="pro")
    assert n == {"verificada": 1, "sin_verificar": 1} and calls == [None, "pro", None]   # el anónimo no se reintenta
    assert pool["personajes"][0]["testigo_verificado"] and pool["citas"][0]["verificacion"]["modelo"] == "pro"


def test_miles_no_es_cifra():
    assert not me.has_figure("Abandonaron a miles de personas en celdas inundadas.")
    assert me.has_figure("Quinientos presos desaparecieron") and me.has_figure("más de seis mil")


def test_reservados_por_fecha_no_van_a_un_cap_anterior():
    pool = _pool3()
    pool["cronologia"] += [{"id": "T08", "fecha": "2006-08-10", "evento": "La ACLU publica el informe sobre la prisión."},
                           {"id": "T09", "fecha": "2006-08-10", "evento": "La ACLU publica su informe sobre la prisión."},
                           {"id": "T10", "fecha": "2005-08-30", "evento": "Rescatan presos en botes."}]
    e, _, _, _ = me.validate(good(), pool)
    sk = me.caps_view(e)
    sk["chapters"][6]["pantalla_ids"] = ["T08", "T09"]           # posteriores a todo lo narrado: quedan; T09 = T08
    sk["chapters"][0]["pantalla_ids"] = ["T10"]                  # entre el cap 3 (29/8) y nada más: va al siguiente
    me._screen_by_date(e, sk, pool)
    by = {c["chapter_number"]: c["pantalla_ids"] for c in sk["chapters"]}
    assert by[7] == ["T08"] and any("T09 cuenta lo mismo que T08" in x for x in e["_pantalla_por_fecha"])
    assert "T10" not in by[1] and "T10" not in by[2]


def test_cita_con_otra_cifra_del_conteo_se_parafrasea():
    pool = _pool3()
    pool["citas"].append({"id": "Q05", "texto": "Éramos más de 500 mujeres en el puente", "autor": "una presa"})
    e, _, _, _ = me.validate(good(), pool)
    e["beats"][5]["datos_apoyo"] = ["Q05"]
    assert any("Q05 trae otra cifra del conteo 517" in x for x in me.writer_instructions(e, pool))


# ═══ F6b-4 ═══

def test_una_cifra_en_pantalla_una_vez_y_cap7_obligatoria():
    e = good()
    e["beats"][4]["contador"] = True                      # D02: 517 como contador
    e["beats"][5]["pregunta_pantalla"] = "¿Dónde están los 517 reclusos?"
    assert any("dos veces" in h for h in me.validate(e, POOL)[1])
    e["beats"][5]["pregunta_pantalla"] = "¿Dónde están esos reclusos?"
    assert me.validate(e, POOL)[1] == []
    e["beats"][-1]["pregunta_pantalla"] = ""
    _, hard, _, _ = me.validate(e, POOL, final=True)       # aun en el último intento: obligatoria
    assert any("cap 7" in h for h in hard)


def test_ultima_frase_sin_eco_de_cita():
    e = good()
    e["beats"][-1]["cierre"] = "Edward Burton lo dijo: nadie allí, nos dejaron por muertos."
    assert any("repite textual la cita Q01" in h for h in me.validate(e, POOL)[1])
    e["beats"][-1]["cierre"] = "Edward Burton sigue esperando que alguien vuelva a buscarlo."
    assert me.validate(e, POOL)[1] == []


def test_solo_apoyo_y_citas_sin_verificar_fuera_de_pantalla():
    e = good()
    assert any("solo como apoyo" in h for h in me.validate(e, POOL, solo_apoyo=("D05",))[1])
    pool = _pool3()
    e["a_pantalla"] = [{"id": "Q03", "cap": 6}]
    esc, hard, rep, _ = me.validate(e, pool)
    assert esc["a_pantalla"] == [] and any("sin verificar" in r for r in rep)
    sk = me.caps_view(esc)
    sk["chapters"][0]["pantalla_ids"] = ["Q03"]
    me._screen_by_date(esc, sk, pool)
    assert all("Q03" not in c["pantalla_ids"] for c in sk["chapters"])
