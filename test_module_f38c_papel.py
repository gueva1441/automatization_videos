"""
test_module_f38c_papel.py — F38c §A.1 y §A.2 (HANDOFF_F38c_marcas_contradice_decimales), la parte del papel:
    §A.1  dos marcas distintas: el `a_pantalla` de la escaleta va en un campo propio del ítem ({beat, por_que}) y no en
          `beats_que_lo_cuentan`; un beat sin ninguno de sus `a_pantalla` queda en `a_pantalla_vacios` (JSON y ⚠ en el
          .md); F65a Etapa A (DECISIONES 2026-10-31 15:49): ya NO es motivo del reintento ni clave (hasta F64 lo era);
          si lleva uno, los demás de ese beat no cuentan; un `a_pantalla` descartado «voz_lo_dice» se verifica contra
          todo el video;
    §A.2  la cifra que contradice la voz (regla `contradice`, token = la cifra de la voz): F64 Etapa 3, es una MARCA
          para el verificador (pantalla_verificador), no una pregunta al autor; con un juez que la pasa la ficha queda
          con `juicio_verificador`.
Borrado por F64 Etapa 3 (DECISIONES 2026-10-31 14:20): test_a2_d40_pregunta_literal (reescrito como
test_a2_d40_marca_contradice: la misma coincidencia, ahora marca), test_a2_confirmada_queda_juzgada_y_el_chequeo_5_no_la_marca
(`_confirmar`, `confirmados`, `juicio_autor` y el `juicio_autor` del chequeo 5 de gfx_guion no existen) y
test_a2_contradice_nueva_tras_el_reintento_corta (el código ya no corta por `contradice`: corta el verificador).
Borrado por F65a Etapa A: test_a1_papel_f38b_da_dos_motivos (el motivo «quedó sin ninguno de los datos que la escaleta
dejó para la pantalla» no existe más; lo que sigue vivo —`a_pantalla_vacios`— va en
test_a1_a_pantalla_vacios_sigue_en_la_salida_sin_ser_motivo); test_a1_d128_en_b11_no_da_motivo_por_d192 adaptado (sin
motivos de a_pantalla: D128 queda en b11, nada nombra a D192, `a_pantalla_vacios` solo ch07 b13). F65a Etapa B:
`pantalla_filtros._sin_juicio` existe otra vez (Fase 2 respeta el `juicio_verificador` del papel) y
test_a2_contradicciones_estructura_y_frases lo asevera al revés que en F64.
Sin API: el verificador es JUEZ_PASA. Las entradas de Fase 1 de Vajont y el papel de F38b se leen de sus copias
congeladas (lab/hyperframes/f38/b2).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from script_engine import m01e_pantalla as mp  # noqa: E402
from script_engine import pantalla_filtros as pf  # noqa: E402
from script_engine import pantalla_verificador as pv  # noqa: E402


def JUEZ_PASA(marcas: list[dict], caps: list[dict]) -> dict:
    """F64 Etapa 3: el verificador falso de los tests: «pasa» toda ficha marcada y «no_dicho» todo descarte dudoso."""
    return {"veredictos_fichas": [{"pool_id": m["pool_id"], "cap": m["cap"], "beat": m["beat"], "veredicto": "pasa",
                                   "motivo": "test", "oracion": None} for m in marcas if m.get("que") != "descarte"],
            "veredictos_descartes": [{"pool_id": m["pool_id"], "veredicto": "no_dicho", "motivo": "test", "oracion": None}
                                     for m in marcas if m.get("que") == "descarte"],
            "usage": None, "usd": 0.0, "segundos": 0.0, "pedido_md5": "test", "intentos": 0}


@pytest.fixture(scope="module", autouse=True)
def _sin_verificador_real():
    """F64 Etapa 3: ningún test de este archivo llama al verificador real (gasta API). `validar` sin `juez` toma
    `_juez_por_defecto` → JUEZ_PASA; `llamar` sin `juez` toma `pantalla_verificador.verificar` con el POST falso, que
    también se reemplaza por JUEZ_PASA para que la llamada del verificador no consuma las respuestas en orden del POST."""
    m = pytest.MonkeyPatch()
    m.setattr(mp, "_juez_por_defecto", lambda: JUEZ_PASA)
    m.setattr(pv, "verificar", lambda marcas, caps, **kw: JUEZ_PASA(marcas, caps))
    yield
    m.undo()


ROOT = Path(__file__).resolve().parent
VAJONT = "f8s3-vajont"
B2 = ROOT / "lab" / "hyperframes" / "f38" / "b2"
FASE1 = B2 / "fase1"
RAW_F38B = B2 / "01e_pantalla.raw.json"
CLIMA = ["PÁNICO", "CALMA", "AMENAZA", "AVISO", "ALARMA", "INMINENTE", "COLAPSO", "SILENCIO", "RABIA", "MEMORIA"]
SEG = {"valor": 0.3459, "oraciones": 200, "caps": 9, "voz": "prueba"}
hay_vajont = pytest.mark.skipif(not RAW_F38B.exists() or not (FASE1 / VAJONT).exists(), reason="sin Vajont (F38b)")


@pytest.fixture(scope="module")
def ent() -> dict:
    carga = mp.cargar(VAJONT, FASE1)
    e = mp.entrada(carga, CLIMA, SEG)
    e["_pool"] = carga["pool"]
    return e


def _con_respaldo(resp: dict, ent: dict) -> dict:
    """F38e §C.3: el formato pide `respaldo` por ficha y las respuestas de F38b no lo traen: se completa con el texto
    entero del ítem (fragmento literal trivial), con lo que el candado contra el respaldo es el de antes."""
    arch = {x["id"]: x["texto"] for x in ent["archivo"]}
    out = json.loads(json.dumps(resp, ensure_ascii=False))
    for fila in list(out.get("beats") or []) + list(out.get("cambios") or []):
        fi = fila.get("ficha") if isinstance(fila, dict) else None
        if isinstance(fi, dict) and not fi.get("respaldo") and fi.get("pool_id") in arch:
            fi["respaldo"] = arch[fi["pool_id"]]
    return out


@pytest.fixture(scope="module")
def papel(ent) -> dict:
    """La respuesta final del autor en F38b (12 fichas), con `respaldo` (F38e)."""
    return _con_respaldo(json.loads(RAW_F38B.read_text(encoding="utf-8"))["final"], ent)


@pytest.fixture(scope="module")
def val1(ent, papel) -> dict:
    return mp.validar(papel, ent)


def _x(ent: dict, pid: str) -> dict:
    return next(x for x in ent["archivo"] if x["id"] == pid)


def test_prompt_no_cambia():
    # F38c no cambió el prompt (163e1fd1…); F38d §A.2.1 cambió solo la línea de «caben» (m01e-5, 76f1de7a…); F38e §C.1
    # lo reemplazó por el de la prueba 1 (m01e-6) y sumó `respaldo` y `autor` a los formatos (3b98aef1…); F64 Etapa 0
    # reemplazó la oración 2 del SYSTEM por la de F63 A.2 (m01e-7, SYSTEM 85d094be…): este es el de hoy
    assert mp.prompt_md5() == "f2bfdf2044a4c77a59fc62ebe93966c2"


# ═══════════════════════ §A.1 ═══════════════════════

@hay_vajont
def test_a1_a_pantalla_en_campo_propio(ent):
    cuentan = {}
    for b in ent["beats"]:
        for i in [b["dato_central"]] + b["apoyo"]:
            if i:
                cuentan.setdefault(i, []).append(b["n"])
    for pid, beat in (("D128", 11), ("D192", 11), ("D245", 13)):
        x = _x(ent, pid)
        assert x["a_pantalla"]["beat"] == beat
        assert x["a_pantalla"]["por_que"] == ent["a_pantalla"][pid]
        assert beat not in x["beats_que_lo_cuentan"]
        assert x["beats_que_lo_cuentan"] == sorted(cuentan.get(pid) or [])     # solo dato central / apoyo
    para = {x["id"]: x for x in mp._para_modelo(ent)["archivo"]}
    assert para["D128"]["a_pantalla"] == {"beat": 11, "por_que": ent["a_pantalla"]["D128"]}   # el modelo lo ve


@hay_vajont
def test_a1_a_pantalla_vacios_sigue_en_la_salida_sin_ser_motivo(val1):
    """F65a Etapa A: los dos beats sin su `a_pantalla` del papel de F38b siguen en `a_pantalla_vacios` (con sus ids),
    pero ya no son motivo de vuelta ni clave."""
    assert [(a["cap"], a["beat"]) for a in val1["a_pantalla_vacios"]] == [("ch06", 11), ("ch07", 13)]
    assert [[i["id"] for i in a["ids"]] for a in val1["a_pantalla_vacios"]] == [["D128", "D192"], ["D245"]]
    assert not any("datos que la escaleta dejó para la pantalla" in m for m in val1["motivos"])
    assert not any(str(c[0]) == "a_pantalla" for c in val1["claves"])
    assert len(val1["motivos"]) == len(val1["motivos_beat"]) == len(val1["claves"])


@hay_vajont
def test_a1_md_marca_el_beat_sin_su_a_pantalla(ent, val1):
    p = mp.armar(ent, {"validacion": val1, "modelo": "m", "effort": "e", "intentos": []})
    md = mp.a_markdown(p)
    l11 = next(ln for ln in md.splitlines() if ln.startswith("- beat 11 "))
    assert "⚠ sin su a_pantalla: D128 (el autor no lo puso); D192 (el autor lo descartó [otro]: " in l11
    l13 = next(ln for ln in md.splitlines() if ln.startswith("- beat 13 "))
    assert "⚠ sin su a_pantalla: D245 (el autor no lo puso)" in l13
    assert "⚠ sin su a_pantalla" not in next(ln for ln in md.splitlines() if ln.startswith("- beat 2 "))


@hay_vajont
def test_a1_d128_en_b11_no_da_motivo_por_d192(ent, papel):
    resp = json.loads(json.dumps(papel, ensure_ascii=False))
    fila = next(b for b in resp["beats"] if b["cap"] == "ch06" and b["beat"] == 11)
    fila["ficha"] = {"pool_id": "D128", "sentence_idx": fila["ficha"]["sentence_idx"], "palabra": "",
                     "etiqueta": "MUERTOS", "texto": "1.910 personas", "aporta": "el recuento",
                     "respaldo": _x(ent, "D128")["texto"]}
    v = mp.validar(resp, ent)
    s11 = next(b for b in v["beats"] if b["cap"] == "ch06" and b["beat"] == 11)
    assert s11["ficha"] and s11["ficha"]["pool_id"] == "D128"
    # F65a Etapa A: con D128 puesto, el beat 11 sale de `a_pantalla_vacios` (queda solo ch07 b13); nada nombra a D192
    assert [(a["cap"], a["beat"]) for a in v["a_pantalla_vacios"]] == [("ch07", 13)]
    assert not any("D192" in m for m in v["motivos"])
    assert not any("datos que la escaleta dejó para la pantalla" in m for m in v["motivos"])


@hay_vajont
def test_a1_a_pantalla_descartado_voz_lo_dice_contra_todo_el_video(ent, papel):
    resp = json.loads(json.dumps(papel, ensure_ascii=False))
    resp["descartados"] = list(resp.get("descartados") or []) + [
        {"pool_id": "D128", "tipo": "voz_lo_dice", "motivo": "la voz ya cuenta los muertos"}]
    v = mp.validar(resp, ent)
    vu = next(x for x in v["vuelven"] if x["pool_id"] == "D128")
    assert vu["caps"] == ["todo el video"]                     # sin `beats_que_lo_cuentan`: todos los caps
    assert vu["falta"] == ["1.910"]


# ═══════════════════════ §A.2 ═══════════════════════

@hay_vajont
def test_a2_d40_marca_contradice(val1):
    """F64 Etapa 3: la única marca `contradice` de las 12 fichas es D40 «715» (ch04 [13]); no es motivo ni corta."""
    ms = [m for m in val1["marcas"] if m["regla"] == "contradice"]
    assert [(m["pool_id"], m["cap"], m["beat"], m["coincidencia"]["token"]) for m in ms] == [("D40", "ch04", 7, "715")]
    assert (ms[0]["coincidencia"]["cap"], ms[0]["coincidencia"]["idx"]) == ("ch04", 13)
    assert ms[0]["coincidencia"]["oracion"] == "La cota autorizada fue de setecientos quince."
    assert ms[0]["etiqueta"] == "COTA MÁXIMA" and ms[0]["texto"] == "722.50 metros"
    assert not any("D40" in m for m in val1["motivos"])
    assert not [d for d in val1["descartados"] if d.get("pool_id") == "D40"]
    s7 = next(b for b in val1["beats"] if b["cap"] == "ch04" and b["beat"] == 7)
    assert s7["ficha"]["pool_id"] == "D40" and s7["ficha"]["juicio_verificador"]["tokens"] == {"contradice": ["715"]}
    assert val1["verificador"]["veredictos_fichas"]                  # el juez (falso) se llamó una vez con las marcas


def test_a2_contradicciones_estructura_y_frases():
    voz = ["La cota autorizada fue de setecientos quince."]
    cs = pf.contradicciones_de("COTA MÁXIMA 720 m", voz, cerca=voz)
    assert [(c["bloque"], c["voz"], c["token"], c["oracion"]) for c in cs] == [(720, 715, "715", voz[0])]
    assert pf.contradicciones("COTA MÁXIMA 720 m", voz, cerca=voz) == [pf.frase_contradiccion(cs[0])]
    # F65a Etapa B: `_sin_juicio` volvió (F64 Etapa 3 lo había borrado); con el token juzgado «pasa» no hay contradicción
    assert hasattr(pf, "_sin_juicio")
    assert pf.contradicciones("COTA MÁXIMA 720 m", voz, cerca=voz, juicio={"contradice": ["715"]}) == []
    assert pf.contradicciones_de("COTA MÁXIMA 720 m", voz, cerca=voz, juicio={"no_dicho": ["715"]}) == cs   # otra regla no
