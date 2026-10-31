"""
test_module_f38d_vueltas.py — F38d §A (HANDOFF_F38d_vueltas_y_caben), los tests del commit A:
    §A.1  vueltas de reintento parcial: hay otra vuelta mientras haya motivos y las CLAVES de los motivos (F64 Etapa
          3: regla, pool_id, cap, beat, token; no el texto) no se repitan («sin progreso»); el .md dice por qué cerró.
          F64 Etapa 1: el tope se borró (DECISIONES 2026-10-31 13:07) y con él el test 3. F64 Etapa 3 (DECISIONES
          2026-10-31 14:20): una coincidencia `contradice`/`no_dicho`/`spoiler` ya no es pregunta al autor ni corta
          al cerrar: es una marca que juzga pantalla_verificador en una llamada; test_1 se reescribió (D241 llega como
          marca `contradice` y con un juez que la pasa queda con `juicio_verificador`; con uno que la corta cae con
          quien «verificador»); se borraron `confirmados`, `juicio_autor`, `cortados_al_cierre`, la «validación final»
          y el chequeo 5 con juicio (helpers _cortados, _seccion_sin_pregunta, _chequeo5, PREGUNTA_D241, PREGUNTAS);
    §A.2  «caben» igual en el prompt, en el motivo y en el código: la línea del prompt (m01e-5, literal) y el motivo
          con el desglose (etiqueta + dato + autor con comillas y raya; el máximo del beat).
Sin API: el autor va con POST falsos y el verificador es JUEZ_PASA. La entrada de Fase 1 de Vajont y el papel de F38c
se leen de sus copias congeladas en lab/ (nunca data/).
"""
from __future__ import annotations

import difflib
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from script_engine import m01e_pantalla as mp  # noqa: E402
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
FASE1 = ROOT / "lab" / "hyperframes" / "f38" / "b2" / "fase1"
RAW_F38C = ROOT / "lab" / "hyperframes" / "f38" / "b3" / "01e_pantalla.raw.json"
HANDOFF = ROOT / "lab" / "hyperframes" / "f38" / "HANDOFF_F38d_vueltas_y_caben.md"
CLIMA = ["PÁNICO", "CALMA", "AMENAZA", "AVISO", "ALARMA", "INMINENTE", "COLAPSO", "SILENCIO", "RABIA", "MEMORIA"]
SEG = {"valor": 0.3459, "oraciones": 200, "caps": 9, "voz": "prueba"}
# §A.2.1, literal: la oración de m01e-4 y la de m01e-5
VIEJA = ("Etiqueta + dato no pueden pasar de los caracteres que caben en la oración ancla (`caben`); si no caben, "
         "elegí otra oración o un dato más corto.")
NUEVA = ("Etiqueta + dato —y en una cita, también el autor tal como viene en el archivo y 5 caracteres de comillas y "
         "raya— no pueden pasar de los caracteres que caben en la oración ancla (`caben`); si no caben, elegí otra "
         "oración o un dato más corto.")
MD5_M01E_4 = "163e1fd195238696d9e66871983d5ac5"
# §A.2.2 + test 4: el motivo de Q50 (la del reintento de F38c, 109 car.)
MOTIVO_Q50 = ("etiqueta 21 + dato 42 + autor 41 (con comillas y raya) = 109 caracteres y en la oración [3] caben 77; "
              "en este beat caben como máximo 90 (oración [0])")
hay_vajont = pytest.mark.skipif(not RAW_F38C.exists() or not (FASE1 / VAJONT).exists(), reason="sin Vajont (F38c)")


@pytest.fixture(scope="module")
def ent() -> dict:
    carga = mp.cargar(VAJONT, FASE1)
    e = mp.entrada(carga, vocabulario=CLIMA, seg=SEG)
    e["_pool"] = carga["pool"]
    return e


@pytest.fixture(scope="module")
def raw38c() -> dict:
    return json.loads(RAW_F38C.read_text(encoding="utf-8"))


def _con_respaldo(resp: dict, ent: dict) -> dict:
    """F38e §C.3: el formato pide `respaldo` por ficha y las respuestas de F38c no lo traen: se completa con el texto
    entero del ítem (fragmento literal trivial), con lo que el candado contra el respaldo es el de antes."""
    arch = {x["id"]: x["texto"] for x in ent["archivo"]}
    out = json.loads(json.dumps(resp, ensure_ascii=False))
    for fila in list(out.get("beats") or []) + list(out.get("cambios") or []):
        fi = fila.get("ficha") if isinstance(fila, dict) else None
        if isinstance(fi, dict) and not fi.get("respaldo") and fi.get("pool_id") in arch:
            fi["respaldo"] = arch[fi["pool_id"]]
    return out


@pytest.fixture(scope="module")
def r1(raw38c, ent) -> dict:
    """El intento 1 de F38c: D105 en ch04 b7, Q50 de 118 car. en ch05 b8 (con `respaldo`, F38e)."""
    return _con_respaldo(raw38c["intentos"][0]["respuesta"], ent)


@pytest.fixture(scope="module")
def r2(raw38c, ent) -> dict:
    """El reintento de F38c (`cambios`): D241 en ch04 b7, Q50 de 109 car. (con `respaldo`, F38e)."""
    return _con_respaldo(raw38c["intentos"][1]["respuesta"], ent)


def _fila(resp: dict, cap: str, beat: int) -> dict:
    return next(b for b in resp["beats"] if b["cap"] == cap and b["beat"] == beat)


def _cambio(resp: dict, cap: str, beat: int) -> dict:
    return next(c for c in resp["cambios"] if c["cap"] == cap and c["beat"] == beat)


def _copia(x):
    return json.loads(json.dumps(x, ensure_ascii=False))


def _post_seq(resps: list[dict], pedidos: list[dict], salidas: list[int] | None = None):
    """POST falso: la llamada k devuelve resps[k] (la última se repite); `salidas` = los tokens de salida por llamada."""
    def post(body: dict) -> dict:
        pedidos.append(body)
        k = len(pedidos) - 1
        r = resps[min(k, len(resps) - 1)]
        out = (salidas[min(k, len(salidas) - 1)] if salidas else 200)
        return {"content": [{"type": "text", "text": json.dumps(r, ensure_ascii=False)}],
                "usage": {"input_tokens": 1000, "output_tokens": out}, "stop_reason": "end_turn"}
    return post


def _tuplas(bs) -> list[tuple[str, int]]:
    return [(str(c), int(b)) for c, b in bs]


def _vueltas(res: dict) -> list[dict]:
    return res["reintento"]["vueltas"]


# ═══════════════════════ los datos de F38c (lo que los tests dan por sentado) ═══════════════════════

@hay_vajont
def test_datos_f38c(r1, r2):
    assert _fila(r1, "ch04", 7)["ficha"]["pool_id"] == "D105"
    q = _fila(r1, "ch05", 8)["ficha"]
    assert q["pool_id"] == "Q50" and q["sentence_idx"] == 3
    assert _cambio(r2, "ch04", 7)["ficha"]["pool_id"] == "D241"
    q2 = _cambio(r2, "ch05", 8)["ficha"]
    assert (q2["pool_id"], q2["sentence_idx"], q2["etiqueta"]) == ("Q50", 3, "CARTA DE ERTO Y CASSO")


# ═══════════════════════ §A.1 vueltas ═══════════════════════

@hay_vajont
def test_1_d241_llega_como_marca_contradice_y_el_verificador_decide(ent, r1, r2):
    """F64 Etapa 3: D241 (la cota del proyecto, 723, en ch04 b7 [13] «La cota autorizada fue de setecientos quince»)
    ya no se pregunta ni se corta en el código: es una marca `contradice` («715») para el verificador; con un juez que la
    pasa queda con `juicio_verificador`; con uno que la corta cae con quien «verificador», su regla y su motivo."""
    fus, _, _ = mp.fusionar(r1, r2, [("ch04", 7), ("ch05", 8)])           # el reintento de F38c: D241 entra en ch04 b7
    assert _fila(fus, "ch04", 7)["ficha"]["pool_id"] == "D241"
    v = mp.validar(fus, ent)                                              # JUEZ_PASA
    ms = [m for m in v["marcas"] if m["pool_id"] == "D241"]
    assert [(m["regla"], m["cap"], m["beat"], m["coincidencia"]["token"]) for m in ms] == [("contradice", "ch04", 7, "715")]
    assert (ms[0]["coincidencia"]["cap"], ms[0]["coincidencia"]["idx"]) == ("ch04", 13)
    assert ms[0]["coincidencia"]["oracion"] == ms[0]["oracion_ancla"] == "La cota autorizada fue de setecientos quince."
    assert (ms[0]["etiqueta"], ms[0]["texto"]) == ("COTA DEL PROYECTO", "723 metros")
    s7 = next(b for b in v["beats"] if b["cap"] == "ch04" and b["beat"] == 7)
    assert s7["ficha"]["pool_id"] == "D241" and s7["ficha"]["juicio_verificador"]["tokens"] == {"contradice": ["715"]}
    assert not any("D241" in m for m in v["motivos"])
    # las otras marcas del papel (T39 «50», D47 «2») también pasan, sin motivo (D105 ya no está: D241 la reemplazó)
    assert {m["pool_id"] for m in v["marcas"]} == {"D241", "T39", "D47"}
    assert not [d for d in v["descartados"] if d.get("quien") == "verificador"]

    def corta(marcas, caps):
        return {"veredictos_fichas": [{"pool_id": "D241", "cap": "ch04", "beat": 7, "veredicto": "corta",
                                       "motivo": "la misma cota", "oracion": {"cap": "ch04", "idx": 13}}],
                "veredictos_descartes": []}
    vc = mp.validar(fus, ent, juez=corta)
    d = next(d for d in vc["descartados"] if d.get("pool_id") == "D241")
    assert d["quien"] == "verificador" and d["regla"] == "contradice" and d["tokens"] == {"contradice": ["715"]}
    assert d["motivo"] == "la misma cota (ch04 [13])"
    assert next(b for b in vc["beats"] if b["cap"] == "ch04" and b["beat"] == 7)["ficha"] is None
    assert "D241 (ch04 beat 7) «COTA DEL PROYECTO · 723 metros»: contradice: la misma cota (ch04 [13])" in vc["motivos"]
    assert ("contradice", "D241", "ch04", 7, "715") in vc["claves"]
    md = mp.a_markdown(mp.armar(ent, {"validacion": vc, "modelo": "m", "effort": "e", "intentos": []}))
    assert "## Lo que cayó" in md and any("D241" in ln and "(verificador" in ln for ln in md.splitlines())


@hay_vajont
def test_2_sin_progreso_cierra(ent, r1, r2, tmp_path):
    """F64 Etapa 3: el cierre es por CLAVES (regla, pool_id, cap, beat, token), no por el texto de los motivos: la
    vuelta 1 cambia la Q50 de 118 a 109 caracteres (sigue sin caber) → el texto del motivo cambia, la clave
    («caben», Q50, ch05, 8) no, y con ella el pico y el `a_pantalla` del beat 8 → cierra «sin progreso»."""
    solo_q50 = {"cambios": [_copia(_cambio(r2, "ch05", 8))]}
    pedidos: list[dict] = []
    res = mp.llamar(ent, tmp_path, post=_post_seq([r1, solo_q50, solo_q50], pedidos))
    rt = res["reintento"]
    assert rt["cierre"] == "sin progreso"
    vs = _vueltas(res)
    assert len(vs) == 1 and len(pedidos) == 2                 # no se manda una segunda vuelta
    assert _tuplas(vs[0]["beats"]) == [("ch05", 8)]           # las marcas de D47/T39/D105 no son motivo: solo el beat 8
    fin = res["validacion"]
    assert vs[0]["motivos"] != fin["motivos"]                 # el texto cambió (Q50 de 118 → 109 car.)…
    assert sorted(map(tuple, vs[0]["claves"])) == sorted(map(tuple, fin["claves"]))   # …las claves no
    assert {tuple(c) for c in fin["claves"]} == {("caben", "Q50", "ch05", 8, None), ("pico", "ch05", 8),
                                                 ("a_pantalla", "ch05", 8)}
    assert any("Q50" in m and "109" in m for m in fin["motivos"])
    assert any(d.get("pool_id") == "Q50" and d["regla"] == "caben"
               for d in fin["descartados"] if d.get("quien") == "validación")
    # las fichas marcadas (D105 «1962», T39 «50», D47 «2») quedan con el juicio del verificador (JUEZ_PASA)
    for cap, beat, pid in (("ch04", 7, "D105"), ("ch04", 6, "T39"), ("ch02", 3, "D47")):
        s = next(b for b in fin["beats"] if b["cap"] == cap and b["beat"] == beat)
        assert s["ficha"] and s["ficha"]["pool_id"] == pid and s["ficha"]["juicio_verificador"]["tokens"]
    assert not [d for d in fin["descartados"] if d.get("quien") == "verificador"]
    assert "cortados_al_cierre" not in rt and "confirmados" not in res
    md = mp.a_markdown(mp.armar(ent, res))
    assert "cerró por: **sin progreso**" in md and "## Cierre del reintento" in md


# ═══════════════════════ §A.2 «caben» ═══════════════════════

@hay_vajont
def test_4_motivo_de_caben_de_q50(ent, r1, r2):
    v1 = mp.validar(r1, ent)
    fus, _, _ = mp.fusionar(r1, r2, mp.beats_con_motivo(v1["motivos_beat"]))
    v = mp.validar(fus, ent)
    d = next(d for d in v["descartados"] if d.get("pool_id") == "Q50" and d.get("quien") == "validación")
    assert d["regla"] == "caben"
    assert d["motivo"] == MOTIVO_Q50
    assert any(m.startswith("Q50 (ch05 beat 8)") and m.endswith(MOTIVO_Q50) for m in v["motivos"])
    # los números del motivo son los de la entrada (data, no regla)
    c5 = next(c for c in ent["caps"] if c["cap"] == "ch05")
    b8 = [s for s in c5["oraciones"] if s["beat"] == 8]
    assert max(s["caben"] for s in b8) == 90 and next(s for s in b8 if s["caben"] == 90)["idx"] == 0
    assert next(s for s in b8 if s["idx"] == 3)["caben"] == 77


def test_5_el_prompt_dice_lo_que_mide_el_codigo_para_caben():
    """F38d §A.2.1 (m01e-5) cambió solo la línea de «caben» sobre m01e-4 (md5 163e1fd1…); F38e §C.1 reemplazó el SYSTEM
    entero por el de la prueba 1 (m01e-6), que conserva lo que §A.2.1 pedía: el autor de la cita y los 5 caracteres de
    comillas y raya cuentan en «caben». Lo que ya no se puede medir (el diff de una línea contra m01e-4) se saca."""
    h = HANDOFF.read_text(encoding="utf-8")
    assert VIEJA in h and NUEVA in h                          # literal del handoff de F38d
    assert mp.PROMPT_VERSION == "m01e-7"                     # F64 Etapa 0
    hoy = mp.PANTALLA_SYSTEM
    assert VIEJA not in hoy and NUEVA not in hoy              # m01e-6 lo dice con sus palabras (las de la prueba 1)
    assert ("Etiqueta + dato —y en una cita, también el autor y 5 caracteres de comillas y raya— no pueden pasar de los "
            "caracteres que caben en la oración ancla (`caben`); si no caben, elegí otra oración o un dato más corto.") in hoy
    assert hoy.count("`caben`") == 1
    assert mp.prompt_md5() != MD5_M01E_4
    assert difflib is not None
