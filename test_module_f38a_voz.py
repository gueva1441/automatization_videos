"""
test_module_f38a_voz.py — F38 §A.2 y §A.4 (HANDOFF_F38_reintento_tarjeta_juez): lo que sale de la voz sin modelo.
    §A.4  fracciones en letras en el parser de cifras (voz_utils): «un centímetro y medio» = 1,5, «medio centímetro» =
          0,5, «dos horas y media» = 2,5, «y cuarto» = +0,25, «un tercio» = 1/3 (contra «0,33» del archivo: redondeo a
          los decimales del archivo); lo de antes se sigue leyendo igual. D68 de Vajont («1,5 cm por día»; la voz de ch04
          dice «más de un centímetro y medio por día») deja de volver por error en la verificación «voz_lo_dice».
    §A.2  la tarjeta desde la voz (voz_datos.tarjeta_de_voz): Vajont → «9 OCT 1963 · 22:39» con la hora de T66 (T72
          22:43 no); sin fecha completa en el gancho → falta; sin hora en el beat pico → solo la fecha.
Los de Vajont se saltean si data/ (fuera de git) no está en disco.
"""
from __future__ import annotations

import copy
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from script_engine import evidence as ev  # noqa: E402
from script_engine import m01e_pantalla as mp  # noqa: E402
from script_engine import voz_datos as vd  # noqa: E402
from script_engine import voz_utils as vu  # noqa: E402

ROOT = Path(__file__).resolve().parent
VAJONT = "f8s3-vajont"
STEPS = ROOT / "data" / "scripts" / "_steps"
SEG = {"valor": 0.35, "oraciones": 1, "caps": 1, "voz": "test"}   # medido: SEG_POR_PALABRA_RESPALDO de m01e (Vajont ch04)
hay_vajont = pytest.mark.skipif(not (STEPS / VAJONT / "01a_escaleta.json").exists(), reason="sin Vajont en disco")


@pytest.fixture(scope="module")
def vajont() -> dict:
    carga = mp.cargar(VAJONT, STEPS)
    ent = mp.entrada(carga, vocabulario=[], seg=SEG)
    return {"ent": ent, "escaleta": carga["escaleta"], "pool": carga["pool"]}


def _valores(texto: str) -> list[float]:
    return [v for v, _, _ in vu._analiza(texto)[0]]


# ═══════════════════════ §A.4 fracciones en letras ═══════════════════════

@pytest.mark.parametrize("texto, valor, unidad", [
    ("más de un centímetro y medio por día", 1.5, "cm"),
    ("la ladera se movía medio centímetro por día", 0.5, "cm"),
    ("dos horas y media de viaje", 2.5, None),
    ("las diez y cuarto", 10.25, None),
    ("un año y medio.", 1.5, None),
    ("tres metros y medio", 3.5, "m"),
])
def test_a4_fracciones_en_letras(texto, valor, unidad):
    assert (valor, unidad) in [(v, u) for v, u, _ in vu._analiza(texto)[0]]


def test_a4_un_tercio_y_su_comparacion_con_el_archivo():
    assert _valores("un tercio de la población") == [pytest.approx(1 / 3)]
    assert vu.numero_en("0,33", "un tercio de la población")          # redondeado a los 2 decimales del archivo
    assert not vu.numero_en("0,34", "un tercio de la población")
    assert vu.misma_cifra("0,33", 1 / 3) and not vu.misma_cifra("0", 1 / 3)
    assert vu.numero_en("1,5", "más de un centímetro y medio por día")


def test_a4_lo_de_antes_se_sigue_leyendo_igual():
    assert vu.numeros("nueve de octubre de mil novecientos sesenta y tres") == ["9", "1963"]
    assert _valores("Son las diez y treinta y nueve.") == [10.0, 39.0]
    assert [(v, u) for v, u, _ in vu._analiza("270 millones de metros cúbicos")[0]] == [(2.7e8, "m3")]
    assert [(v, u) for v, u, _ in vu._analiza("1,5 cm por día")[0]] == [(1.5, "cm")]
    assert _valores("medio valle") == []                        # «medio» sin unidad no es una cifra
    assert _valores("un centímetro") == []                      # «un» sin fracción sigue siendo artículo
    assert _valores("dos casas y media docena") == [2.0]        # «media» va con «docena», no suma
    assert vu.numero_en("2", "dos horas y media")               # el entero se sigue listando


@hay_vajont
def test_a4_d68_deja_de_volver_por_error(vajont):
    """D68 «1,5 cm por día» lo cuenta el beat 7 (ch04); la voz de ch04 dice «más de un centímetro y medio por día»."""
    ent, pool = vajont["ent"], vajont["pool"]
    d68 = ev.items(pool)["D68"]
    assert "1,5 cm" in ev.text_of(d68)
    caps = {c["cap"]: c for c in ent["caps"]}
    voz = " ".join(s["texto"] for s in caps["ch04"]["oraciones"])
    assert "centímetro y medio" in voz
    assert mp.voz_no_lo_dice(d68, voz, ent["anios"]) is None
    r1 = {"beats": [], "descartados": [{"pool_id": "D68", "tipo": "voz_lo_dice", "motivo": "La voz ya lo dice."}]}
    v = mp.validar(r1, ent)
    assert not [x for x in v["vuelven"] if x["pool_id"] == "D68"]


# ═══════════════════════ §A.2 tarjeta desde la voz ═══════════════════════

def test_a2_horas_dichas_en_letras_y_digitos():
    assert vd.horas_dichas("Son las diez y treinta y nueve.") == [(10, 39)]
    assert vd.horas_dichas("Llegó a las seis de la tarde.") == [(18, 0)]
    assert vd.horas_dichas("A las 22:39 el Toc cae.") == [(22, 39)]
    assert vd.horas_dichas("Eran las once menos cuarto.") == [(10, 45)]
    assert vd.horas_dichas("Las tres casas quedaron en pie.") == []
    assert vd.horas_dichas("Murieron 1.910 personas.") == []


@hay_vajont
def test_a2_vajont_9_oct_1963_22_39_de_t66(vajont):
    t = vd.tarjeta_de_voz(vajont["ent"], vajont["escaleta"], vajont["pool"])
    assert t["texto"] == "9 OCT 1963 · 22:39"
    assert t["fecha"] == "1963-10-09" and t["hora"] == "22:39"
    assert t["hora_de"] == "T66"                                 # T72 (22:43) no: la voz dice «las diez y treinta y nueve»
    assert t["fecha_de"].startswith("ch01 [")
    assert "T66" in t["fuente"] and "T72" not in t["fuente"]


@hay_vajont
def test_a2_sin_fecha_en_el_gancho_falta(vajont):
    ent = copy.deepcopy(vajont["ent"])
    for s in ent["caps"][0]["oraciones"]:
        s["texto"] = s["texto"].replace("nueve de octubre de mil novecientos sesenta y tres", "aquella noche")
    t = vd.tarjeta_de_voz(ent, vajont["escaleta"], vajont["pool"])
    assert t.get("falta") is True and "gancho" in t["motivo"]


@hay_vajont
def test_a2_voz_sin_hora_solo_fecha(vajont):
    ent = copy.deepcopy(vajont["ent"])
    for c in ent["caps"]:
        for s in c["oraciones"]:
            s["texto"] = s["texto"].replace("Son las diez y treinta y nueve.", "Es de noche.")
    t = vd.tarjeta_de_voz(ent, vajont["escaleta"], vajont["pool"])
    assert t["texto"] == "9 OCT 1963" and t["hora"] is None and t["hora_de"] is None
    assert "sin hora" in t["fuente"]


def test_a2_sin_pool_ni_vajont_la_hora_sale_del_item_que_coincide():
    """Sin data/: un caso armado a mano (el beat pico no trae hora; el ítem de la fecha que coincide sí)."""
    ent = {"caps": [{"cap": "ch01", "n": 1, "oraciones": [
        {"idx": 0, "beat": 1, "texto": "Fue el tres de marzo de mil novecientos veinte."}]},
        {"cap": "ch02", "n": 2, "oraciones": [{"idx": 0, "beat": 2, "texto": "Eran las nueve y cuarto de la noche."}]}]}
    esc = {"pico": {"beat": 2, "id": "T01"}, "beats": [{"n": 2, "cap": 2, "dato_central": "T01", "datos_apoyo": []}]}
    pool = {"cronologia": [{"id": "T01", "fecha": "1920-03-03", "texto": "a"},
                           {"id": "T02", "fecha": "1920-03-03", "hora": "21:10", "texto": "b"},
                           {"id": "T03", "fecha": "1920-03-03", "hora": "21:15", "texto": "c"}]}
    t = vd.tarjeta_de_voz(ent, esc, pool)
    assert t["texto"] == "3 MAR 1920 · 21:15" and t["hora_de"] == "T03" and t["fecha_de"] == "ch01 [0]"
