"""
test_module_f55.py — F55 Parte A: `evidence.regla_dicho` (ancla / A1 / A2 / None) con los casos de la simulación §3 del
handoff sobre el pool y los guiones de Wittenoom; `dicho_verificador.pedido` puro y la lectura de la respuesta; (f)/(h)
con `verificar` simulado sí / no / None y las altas en `ids_usados`; `ids_usados` de los 7 caps viejos y nuevos: antes ⊆
después y la diferencia escrita. Un test con Sonnet real (D10, cap 6 nuevo) solo con F55_REAL=1. Sin red salvo ese.
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

import pytest

from script_engine import dicho_verificador as dv
from script_engine import evidence as ev
from script_engine import guion_v4 as g4
from script_engine.m05_narrative import used_items

ROOT = Path(__file__).resolve().parent
VIEJO = ROOT / "lab" / "hyperframes" / "f54" / "antes"
NUEVO = ROOT / "lab" / "hyperframes" / "f55" / "antes"
hay = pytest.mark.skipif(not (NUEVO / "01_facts_sources.json").exists() or not (VIEJO / "01b_narration.json").exists(),
                         reason="sin los snapshots de Wittenoom (lab/hyperframes/f54|f55/antes)")


def _pool() -> dict:
    p = json.loads((NUEVO / "01_facts_sources.json").read_text(encoding="utf-8"))
    return p.get("evidence_pool", p)


def _caps(d: Path) -> dict[int, str]:
    return {c["chapter_number"]: c["narration"]
            for c in json.loads((d / "01b_narration.json").read_text(encoding="utf-8"))["chapters"]}


# ═══════════════════════════════════════════════════════════════
#  A.1 regla_dicho: ancla / A1 / A2 / None (simulación §3 del handoff)
# ═══════════════════════════════════════════════════════════════

def test_constantes_a2():
    assert ev.UMBRAL_A2 == 0.5 and ev.A2_MIN_COINCIDENCIAS == 2


@hay
def test_a1_a2_sobre_el_guion_nuevo_como_la_simulacion():
    its, caps = ev.items(_pool()), _caps(NUEVO)
    sin_ancla = [i for i, it in its.items() if it["_kind"] == "datos" and not ev.anchors(it)]
    assert len(sin_ancla) == 68
    a1 = {i for i in sin_ancla if any(ev.regla_dicho(t, its[i]) == "A1" for t in caps.values())}
    assert a1 == {"D19", "D21", "D27", "D29", "D57", "D59", "D60", "D61", "D91", "D92", "D112", "D135", "D144"}
    a2 = {i for i in sin_ancla if any(ev.regla_dicho(t, its[i]) == "A2" for t in caps.values())}
    assert a2 == {"D42", "D71", "D85", "D150"}             # D19 y D92 también cumplen A2, pero A1 va primero
    assert ev.regla_dicho(caps[3], its["D21"]) == "A1" and ev.regla_dicho(caps[6], its["D10"]) is None
    assert ev.regla_dicho(caps[6], its["D42"]) == "A2" and ev.regla_dicho(caps[1], its["D85"]) == "A2"
    assert ev.regla_dicho(caps[1], its["D92"]) == "A1"        # promesa del gancho: cuenta (riesgo aceptado §3)
    assert ev.used_in(caps[3], its["D21"]) and not ev.used_in(caps[6], its["D10"])


@hay
def test_oracion_dicha_devuelve_la_oracion_que_acerto():
    its, caps = ev.items(_pool()), _caps(NUEVO)
    k = ev.oracion_dicha(caps[3], its["D21"])
    assert "la produccion aumento" in ev.norm(ev._sentences(caps[3])[k])
    k = ev.oracion_dicha(caps[6], its["D42"])
    assert "barricadas permanentes" in ev.norm(ev._sentences(caps[6])[k])
    assert ev.oracion_dicha(caps[6], its["D10"]) is None


def test_a1_no_cuenta_el_anio_en_letras_como_palabra_del_hecho():
    it = {"_kind": "datos", "tipo": "fecha", "fecha": "1948", "texto": "En 1948 el doctor advirtió por escrito.", "valor": None}
    assert ev.regla_dicho("Mil novecientos cuarenta y ocho. Llovió toda la tarde.", it) is None    # solo el año
    assert ev.regla_dicho("Mil novecientos cuarenta y ocho. El doctor escribe su advertencia.", it) is None   # otra oración
    assert ev.regla_dicho("En mil novecientos cuarenta y ocho, el doctor escribe su advertencia.", it) == "A1"
    assert ev.regla_dicho("En 1948 el doctor escribió.", it) == "A1"
    assert ev.regla_dicho("El doctor advirtió por escrito y nadie lo leyó.", it) == "A2"      # sin año: A2 (2 de 3)


def test_a2_exige_dos_coincidencias_y_la_mitad():
    it = {"_kind": "datos", "tipo": "lugar", "texto": "Barricadas permanentes en las entradas del pueblo.", "valor": None}
    assert ev.regla_dicho("Pusieron barricadas permanentes.", it) == "A2"           # 2 de 3 ≥ 0,5
    assert ev.regla_dicho("Las barricadas siguen.", it) is None                      # 1 coincidencia
    cita = {"_kind": "citas", "texto": "Nadie nos dijo nada del polvo", "autor": "x"}
    assert ev.regla_dicho("Nadie les dijo nada del polvo que respiraban.", cita) is None   # citas: solo ancla literal
    assert ev.regla_dicho("Lo dijo claro: «Nadie nos dijo nada del polvo».", cita) == "ancla"


def test_con_ancla_nada_cambia():
    it = {"_kind": "datos", "tipo": "cifra", "texto": "517 reclusos no estaban contabilizados", "valor": "517"}
    assert ev.regla_dicho("Quinientos diecisiete reclusos sin contar.", it) == "ancla"
    assert ev.regla_dicho("Los reclusos no estaban contabilizados.", it) is None      # con ancla, A2 no aplica


# ═══════════════════════════════════════════════════════════════
#  A.2 dicho_verificador: pedido puro y lectura de la respuesta
# ═══════════════════════════════════════════════════════════════

def test_pedido_puro_y_literal():
    p = dv.pedido("Hecho X.", ["Primera oración.", "Segunda oración."])
    assert p.startswith("HECHO: Hecho X.\n\nORACIONES:\n1. Primera oración.\n2. Segunda oración.\n\n")
    assert dv.PREGUNTA in p and dv.PREGUNTA.startswith("¿Alguna de estas oraciones dice este hecho, con las mismas palabras o con otras?")
    assert dv.MODELO == "claude-sonnet-5-5" and dv.EFFORT == "medium"


def test_leer_respuesta_rango_y_fragmento():
    ors = ["La producción aumentó en 1961.", "Nadie dijo nada."]
    assert dv._leer({"oracion": 1, "fragmento": "la producción aumentó"}, ors) == 1
    assert dv._leer({"oracion": 3, "fragmento": "x"}, ors) is None                     # fuera de rango
    assert dv._leer({"oracion": 2, "fragmento": "la producción"}, ors) is None          # el fragmento no está en la 2
    assert dv._leer({"oracion": None, "fragmento": None}, ors) is None
    assert dv._leer("basura", ors) is None


def test_verificar_con_post_simulado_cache_y_error():
    dv.reset()
    llamadas = []

    def post_ok(body):
        llamadas.append(body)
        return {"model": dv.MODELO, "usage": {"input_tokens": 100, "output_tokens": 10},
                "content": [{"type": "text", "text": '{"oracion": 2, "fragmento": "nadie dijo nada"}'}]}
    ors = ["La producción aumentó.", "Nadie dijo nada."]
    log: list[str] = []
    assert dv.verificar("Nadie dijo nada del polvo.", ors, log=log, id="D1", post=post_ok) == 2
    assert dv.verificar("Nadie dijo nada del polvo.", ors, log=log, id="D1", post=post_ok) == 2    # caché
    assert len(llamadas) == 1 and dv.estado()["llamadas"] == 1 and dv.estado()["cache"] == 1 and dv.estado()["usd"] > 0
    assert llamadas[0]["model"] == dv.MODELO and llamadas[0]["output_config"]["effort"] == dv.EFFORT

    def post_err(body):
        raise TimeoutError("lento")
    assert dv.verificar("Otro hecho.", ors, log=log, id="D2", post=post_err) is None
    assert sum("error" in x for x in log) == 2                                           # 1 reintento


# ═══════════════════════════════════════════════════════════════
#  A.3 (f)/(h) con verificar simulado; altas en ids_usados
# ═══════════════════════════════════════════════════════════════

def _fixture():
    import test_module_f11 as t11
    esc = t11._esc_ok()
    esc["beats"][-1]["funcion"] = "cierre"
    esc["beats"][-1]["dato_central"] = "D20"          # sin ancla
    esc["beats"][5]["paga"] = 2
    esc["beats"][5]["dato_central"] = "D21"            # sin ancla
    pool = json.loads(json.dumps(t11.POOL))
    pool["datos"] += [{"id": "D20", "texto": "Nadie volvió a abrir el portón del patio", "tipo": "lugar"},
                      {"id": "D21", "texto": "Los bomberos esperaron afuera sin entrar", "tipo": "lugar"}]
    topic = {**t11.TOPIC, "evidence_pool": pool}
    ps = t11._parrafos(esc)
    return topic, esc, ps


def test_sin_ancla_decide_sonnet_si_y_entra_a_ids_usados():
    topic, esc, ps = _fixture()
    vistos = []

    def si(hecho, oraciones, **k):
        vistos.append((k.get("id"), len(oraciones)))
        return 1
    bl = g4.bloqueantes(topic, esc, ps, verificar=si)
    assert not [x for x in bl if x["codigo"] in ("f", "h")]
    assert sorted(i for i, _ in vistos) == ["D20", "D21"]
    assert "D20" in ps[-1]["ids_usados"] and "D21" in ps[5]["ids_usados"]
    assert [a["id"] for a in g4.ULTIMAS_ALTAS] == ["D20", "D21"] and all(a["regla"] == "sonnet" for a in g4.ULTIMAS_ALTAS)
    m = g4.metricas(topic, esc, ps)
    assert [a["id"] for a in m["confirmados_sonnet"]] == ["D20", "D21"] and set(m["verificador"]) == {"llamadas", "cache", "usd"}


def test_sin_ancla_sonnet_no_o_none_frena():
    topic, esc, ps = _fixture()
    bl = g4.bloqueantes(topic, esc, ps, verificar=lambda h, o, **k: None)
    assert sorted(x["codigo"] for x in bl if x["codigo"] in "fh") == ["f", "h"] and g4.ULTIMAS_ALTAS == []
    assert "D20" not in ps[-1]["ids_usados"]


def test_sin_ancla_sonnet_decide_aunque_a2_diga_si():
    topic, esc, ps = _fixture()
    ps[-1]["texto"] += " Nadie volvió a abrir el portón del patio."          # A2 lo ve
    assert ev.regla_dicho(ps[-1]["texto"], ev.items(topic["evidence_pool"])["D20"]) == "A2"
    bl = g4.bloqueantes(topic, esc, ps, verificar=lambda h, o, **k: None)    # Sonnet dice no → frena igual
    assert any(x["codigo"] == "f" for x in bl)


def test_con_ancla_no_llama_al_verificador():
    import test_module_f11 as t11
    esc = t11._esc_ok()
    esc["beats"][-1]["funcion"] = "cierre"                 # D12, con ancla
    ps = t11._parrafos(esc)

    def nunca(*a, **k):
        raise AssertionError("no debía llamar")
    assert g4.bloqueantes(t11.TOPIC, esc, ps, verificar=nunca) == []


def test_f_y_h_devuelven_bloqueantes_y_altas():
    topic, esc, ps = _fixture()
    ps_ids = g4.with_ids(ps, topic["evidence_pool"], esc)
    bl, altas = g4.cierre_no_dicho(esc, ps_ids, topic["evidence_pool"], verificar=lambda h, o, **k: 2)
    assert bl == [] and altas == [{"id": "D20", "cap": 7, "parrafo": 11, "oracion": 2, "regla": "sonnet", "que": "cierre"}]
    bl, altas = g4.pago_no_dicho(esc, ps_ids, topic["evidence_pool"], verificar=lambda h, o, **k: None)
    assert [x["codigo"] for x in bl] == ["h"] and altas == []


# ═══════════════════════════════════════════════════════════════
#  ids_usados de los 7 caps, viejo y nuevo: antes ⊆ después, y la diferencia escrita
# ═══════════════════════════════════════════════════════════════

def _used_in_viejo(text: str, it: dict) -> bool:
    ancs = ev.anchors(it)
    dated = it.get("_kind") == "cronologia" or (it.get("_kind") == "datos" and it.get("tipo") == "fecha")
    if not dated:
        return any(ev.literal_in(a, text) for a in ancs)
    words = ev._content(ev.text_of(it)) - {w[:6] for a in ancs for w in re.findall(r"[a-zñ]{5,}", ev.norm(a))}
    return any(any(ev.literal_in(a, s) for a in ancs) and (not words or words & ev._content(s)) for s in ev._sentences(text))


@hay
@pytest.mark.parametrize("d, esperado", [
    (VIEJO, {1: [], 2: [], 3: ["D19", "D21"], 4: [], 5: ["D27"], 6: ["D36", "D54", "D59", "D61", "D93"], 7: ["D71"]}),
    (NUEVO, {1: ["D85"], 2: [], 3: ["D19", "D21", "D92"], 4: [], 5: ["D27"], 6: ["D42", "D59", "D150"], 7: ["D61"]}),
])
def test_ids_usados_antes_subconjunto_de_despues(d, esperado):
    pool, its = _pool(), ev.items(_pool())
    esc = json.loads((d / "01a_escaleta.json").read_text(encoding="utf-8"))
    for cap, txt in _caps(d).items():
        own = {i for b in esc["beats"] if b["cap"] == cap for i in [b["dato_central"], *(b.get("datos_apoyo") or [])]}
        antes = [i for i in its if its[i]["_kind"] in ("datos", "cronologia", "citas") and i in own and _used_in_viejo(txt, its[i])]
        despues = [i for i in used_items(txt, pool, hard=False) if i in own]
        assert set(antes) <= set(despues)
        assert [i for i in despues if i not in antes] == esperado[cap], cap


# ═══════════════════════════════════════════════════════════════
#  Sonnet real (fuera de la suite rápida; solo con F55_REAL=1)
# ═══════════════════════════════════════════════════════════════

@hay
@pytest.mark.skipif(os.environ.get("F55_REAL") != "1", reason="llamada real a Sonnet: F55_REAL=1")
def test_sonnet_real_d10_cap_6_nuevo():
    its, caps = ev.items(_pool()), _caps(NUEVO)
    dv.reset()
    ors = ev._sentences(caps[6])
    n = dv.verificar(its["D10"]["texto"], ors, id="D10")
    assert n is not None and "colonial" in ev.norm(ors[n - 1]) and dv.estado()["llamadas"] == 1


# ═══════════════════════════════════════════════════════════════
#  Parte B: dedupe de citas del pool (DECISIONES 2026-10-29 19:30: mismo autor + 0,7)
# ═══════════════════════════════════════════════════════════════

from researcher_steps import research_v3 as r3  # noqa: E402


def _pool_antes() -> dict:
    """El pool de Wittenoom ANTES del dedupe (f55/antes/01_facts_sources.json, copia de F54 B.5: 58 citas)."""
    p = json.loads((NUEVO / "01_facts_sources.json").read_text(encoding="utf-8"))
    return p.get("evidence_pool", p)


def test_umbral_dedupe():
    assert r3.UMBRAL_DEDUPE_CITAS == 0.7


@hay
def test_los_8_pares_de_wittenoom_con_la_funcion_de_produccion():
    pool = _pool_antes()
    its = ev.items(pool)
    esperado = {("Q20", "Q33"): 0.94, ("Q18", "Q30"): 0.92, ("Q15", "Q27"): 0.90, ("Q16", "Q28"): 0.89,
                ("Q14", "Q26"): 0.88, ("Q12", "Q25"): 0.88, ("Q17", "Q29"): 0.73, ("Q23", "Q35"): 0.71}
    for (a, b), s in esperado.items():
        assert round(r3._similitud_citas(its[a], its[b]), 2) == s, (a, b)
    assert r3._similitud_citas(its["Q30"], its["Q36"]) is None and r3._similitud_citas(its["Q18"], its["Q36"]) is None
    assert round(r3._similitud_citas(its["Q19"], its["Q32"]), 2) == 0.50          # mismo autor, no duplicado
    fuera = r3._dedupe_citas(pool)
    pares = {frozenset((d["id"], d["duplicado_de"])) for d in fuera}
    assert pares == {frozenset(p) for p in esperado} and len(pool["citas"]) == 50
    assert all(d["kind"] == "citas" and d["motivo"] == "cita duplicada" and d["similitud"] >= 0.7 for d in fuera)
    assert {d["id"] for d in fuera} & {q["id"] for q in pool["citas"]} == set()
    ids = [q["id"] for q in pool["citas"]]
    assert ids == sorted(ids, key=lambda x: int(x[1:])) and "Q25" in ids and "Q12" not in ids   # sin renumerar


def _cita(i, autor, texto, n=1, docs=None):
    return {"id": i, "autor": autor, "texto": texto, "n_fuentes": n, "docs": docs or [f"F{i[1:]}"]}


def test_queda_la_de_mas_fuentes_y_suma_docs():
    pool = {"citas": [_cita("Q1", "Ana López", "Nadie nos dijo nada del polvo que había en el pueblo", 1, ["F01"]),
                      _cita("Q2", "Ana Lopez", "Nadie nos dijo nada del polvo del pueblo", 2, ["F02", "F03"])],
            "_descartados": []}
    fuera = r3._dedupe_citas(pool)
    assert [d["id"] for d in fuera] == ["Q1"] and fuera[0]["duplicado_de"] == "Q2"      # más fuentes gana a más larga
    q2 = pool["citas"][0]
    assert q2["id"] == "Q2" and q2["docs"] == ["F02", "F03", "F01"] and q2["n_fuentes"] == 3
    assert pool["_descartados"][0]["kind"] == "citas" and pool["_descartados"][0]["similitud"] >= 0.7


def test_empate_en_fuentes_queda_la_mas_larga_y_no_compara_sin_autor():
    pool = {"citas": [_cita("Q1", "Ana López", "Nadie nos dijo nada del polvo"),
                      _cita("Q2", "Ana López", "Nadie nos dijo nada del polvo que había en el pueblo entero"),
                      _cita("Q3", None, "Nadie nos dijo nada del polvo que había en el pueblo entero"),
                      _cita("Q4", "Pedro Ruiz", "Nadie nos dijo nada del polvo que había en el pueblo entero")]}
    fuera = r3._dedupe_citas(pool)
    assert [(d["id"], d["duplicado_de"]) for d in fuera] == [("Q1", "Q2")]              # Q3 sin autor, Q4 otro autor
    assert [q["id"] for q in pool["citas"]] == ["Q2", "Q3", "Q4"]


def test_remapear_ids():
    pool = {"_descartados": [{"kind": "citas", "id": "Q12", "duplicado_de": "Q25"},
                             {"kind": "datos", "id": "D9", "texto": "x"}]}
    obj = {"beats": [{"dato_central": "Q12", "datos_apoyo": ["Q12", "Q25", "D3"], "cierre": "Q12 no es un id acá"}],
           "a_pantalla": [{"id": "Q12", "cap": 2}], "ids": ["D9", "Q12"]}
    out = r3.remapear_ids(obj, pool)
    assert out["beats"][0]["dato_central"] == "Q25" and out["beats"][0]["datos_apoyo"] == ["Q25", "D3"]
    assert out["a_pantalla"][0]["id"] == "Q25" and out["ids"] == ["D9", "Q25"]
    assert out["beats"][0]["cierre"] == "Q12 no es un id acá" and obj["beats"][0]["dato_central"] == "Q12"   # copia
    assert r3.remapear_ids(obj, {"_descartados": []}) == obj


# ═══════════════════════════════════════════════════════════════
#  Parte C: promesa de una oración (DECISIONES 2026-10-29 19:15) · C.0 (ii): fuera las versiones viejas
# ═══════════════════════════════════════════════════════════════

from script_engine import m01a_escaleta as me  # noqa: E402

F55 = ROOT / "lab" / "hyperframes" / "f55"


def _sistema(p: Path) -> str:
    md = p.read_text(encoding="utf-8").replace("\r\n", "\n")
    i = md.index("\n## SISTEMA\n\n") + len("\n## SISTEMA\n\n")
    return md[i:md.index("\n\n---\n", i)]


def test_escaleta_f55_1_literal_y_una_sola_linea():
    assert me.SYSTEM_V2 == _sistema(F55 / "PROMPT_ESCALETA_f55_1.md") and me.PROMPT_VERSION_V2 == "f55-1"
    assert me.PROMPT_VERSION_COLUMNA == "f55-1"
    f54_1 = _sistema(ROOT / "lab" / "hyperframes" / "f54" / "PROMPT_ESCALETA_f54_1.md")
    a, b = f54_1.split("\n"), me.SYSTEM_V2.split("\n")
    assert len(a) == len(b)
    dif = [(x, y) for x, y in zip(a, b) if x != y]
    assert dif == [("promesa_gancho: «Once personas esperaron veintitrés días un barco que no llegó. Esta es la historia "
                    "de quién decidió que no llegara.»",
                    "promesa_gancho: «Once personas esperaron veintitrés días un barco que alguien había decidido que no "
                    "llegara.»")]


def test_las_versiones_viejas_de_la_escaleta_se_borraron():
    for n in ("SYSTEM_V2_F26_1", "SYSTEM_V2_F25_1", "SYSTEM_V2_F24_1", "SYSTEM_V2_F22_2", "SYSTEM_V2_F22_1", "SYSTEM_V2_F16_1",
              "PROMPT_VERSION_V2_F26_1", "PROMPT_VERSION_V2_F25_1", "PROMPT_VERSION_V2_F24_1", "PROMPT_VERSION_V2_F22_2",
              "PROMPT_VERSION_V2_F22", "PROMPT_VERSION_V2_F16"):
        assert not hasattr(me, n), n
    assert me.SYSTEM_V2.count("<rol>") == 1


def test_esquema_promesa_con_descripcion():
    for s in (me.SCHEMA, me.SCHEMA_FICHA):
        assert s["properties"]["promesa_gancho"] == {"type": "STRING", "description": "Una sola oración: lo que está en juego."}


def test_promesa_de_dos_oraciones_se_repara_por_codigo():
    import test_module_f6b as t6
    e = t6.good()
    e["promesa_gancho"] = "Daniel vivió diez meses en Wittenoom. Murió de eso casi treinta años después."
    esc, hard, rep, _ = me.validate(e, t6.POOL)
    assert esc["promesa_gancho"] == "Daniel vivió diez meses en Wittenoom." and esc["_promesa_oraciones"] == 2
    assert any(r.startswith("promesa_gancho: 2 oraciones") for r in rep) and not any("promesa" in h for h in hard)
    e = t6.good()
    esc, hard, rep, _ = me.validate(e, t6.POOL)
    assert esc["_promesa_oraciones"] == 1 and not any("promesa" in r for r in rep)
    import test_module_f16 as t16
    assert me.metricas_escaleta(esc, t16.POOL, t16.FICHA, [])["promesa_oraciones"] == 1


# ═══════════════════════════════════════════════════════════════
#  D.0: remapear_ids con claves; ficha_caso.load remapea contra el pool del topic
# ═══════════════════════════════════════════════════════════════

def test_remapear_ids_tambien_claves_de_dict():
    pool = {"_descartados": [{"kind": "citas", "id": "Q12", "duplicado_de": "Q25"}]}
    out = r3.remapear_ids({"textos": {"Q12": "a", "D3": "b"}, "lista": ["Q12"]}, pool)
    assert out == {"textos": {"Q25": "a", "D3": "b"}, "lista": ["Q25"]}
    out = r3.remapear_ids({"textos": {"Q25": "la que queda", "Q12": "la duplicada"}}, pool)
    assert out == {"textos": {"Q25": "la que queda"}}                       # la clave nueva ya existía: queda la existente


def test_ficha_load_remapea_en_memoria(tmp_path):
    from researcher_steps import ficha_caso as fc
    d = tmp_path / "t1"
    d.mkdir()
    ficha = {"escenas": [{"ids": ["Q12", "D3"]}], "versiones": [{"versiones": [{"ids": ["Q23"]}]}], "personas": [{"ids": ["Q25"]}]}
    (d / "ficha_caso.json").write_text(json.dumps(ficha), encoding="utf-8")
    (d / "00_pool_v3.json").write_text(json.dumps({"citas": [], "_descartados": [
        {"kind": "citas", "id": "Q12", "duplicado_de": "Q25"}, {"kind": "citas", "id": "Q23", "duplicado_de": "Q35"},
        {"kind": "datos_r3", "id": "D99"}]}), encoding="utf-8")
    log: list[str] = []
    out = fc.load("t1", tmp_path, log=log)
    assert out["escenas"][0]["ids"] == ["Q25", "D3"] and out["versiones"][0]["versiones"][0]["ids"] == ["Q35"]
    assert log == ["  [ficha] 2 id(s) de citas duplicadas remapeados al cargar (el archivo no cambia)"]
    assert json.loads((d / "ficha_caso.json").read_text(encoding="utf-8")) == ficha        # el archivo no se reescribe
    # sin descartados: tal cual, sin log
    d2 = tmp_path / "t2"
    d2.mkdir()
    (d2 / "ficha_caso.json").write_text(json.dumps(ficha), encoding="utf-8")
    (d2 / "00_pool_v3.json").write_text(json.dumps({"citas": [], "_descartados": []}), encoding="utf-8")
    log2: list[str] = []
    assert fc.load("t2", tmp_path, log=log2) == ficha and log2 == []
    # sin pool: tal cual
    d3 = tmp_path / "t3"
    d3.mkdir()
    (d3 / "ficha_caso.json").write_text(json.dumps(ficha), encoding="utf-8")
    assert fc.load("t3", tmp_path) == ficha and fc.load("t4", tmp_path) is None


@hay
def test_ficha_de_wittenoom_cargada_sin_ids_descartados():
    from researcher_steps import ficha_caso as fc
    from script_engine.m01a_skeleton import STEPS_DIR
    tid = "123bbb64-9fca-4395-8bf4-57d60e219ef1"
    if not (STEPS_DIR / tid / "ficha_caso.json").exists():
        pytest.skip("sin la ficha de Wittenoom en _steps/")
    pool = json.loads((STEPS_DIR / tid / "00_pool_v3.json").read_text(encoding="utf-8"))
    gone = {d["id"] for d in pool.get("_descartados") or [] if d.get("kind") == "citas"}
    if not gone:
        pytest.skip("el pool de Wittenoom en _steps/ no tiene citas descartadas (dedupe_pool.py no corrió)")
    s = json.dumps(fc.load(tid), ensure_ascii=False)
    assert not re.findall(r'"(' + "|".join(sorted(gone)) + r')"', s)
