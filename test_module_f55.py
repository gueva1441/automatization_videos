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
