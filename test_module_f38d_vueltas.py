"""
test_module_f38d_vueltas.py — F38d §A (HANDOFF_F38d_vueltas_y_caben), los tests del commit A:
    §A.1  vueltas de reintento parcial: lo nuevo que aparece después de una vuelta (una coincidencia `contradice`,
          `no_dicho`, `spoiler`) no corta: es una pregunta de la vuelta siguiente; hay otra vuelta mientras haya
          motivos, los motivos no sean iguales a los de la vuelta anterior («sin progreso») y la vuelta entre en el
          tope; al cerrar, la validación final de hoy (lo que sigue sin preguntar corta) y el .md dice por qué cerró;
    §A.2  «caben» igual en el prompt, en el motivo y en el código: la línea del prompt (m01e-5, literal) y el motivo
          con el desglose (etiqueta + dato + autor con comillas y raya; el máximo del beat).
Sin API: el autor va con POST falsos. La entrada de Fase 1 de Vajont y el papel de F38c se leen de sus copias
congeladas en lab/ (nunca data/).
"""
from __future__ import annotations

import difflib
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from script_engine import gfx_guion as gg  # noqa: E402
from script_engine import m01e_pantalla as mp  # noqa: E402

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
# la pregunta de D241 (la cota del proyecto, 723) que en F38c se cortó sin preguntar
PREGUNTA_D241 = ("D241 (ch04 beat 7, oración [13]) «COTA DEL PROYECTO · 723 metros»: la voz dice «715» para lo mismo, "
                 "en la oración ancla o en una vecina en ch04 [13] («La cota autorizada fue de setecientos quince.»); "
                 "¿es el mismo hecho? si no, mantenelo")
# §A.2.2 + test 4: el motivo de Q50 (la del reintento de F38c, 109 car.)
MOTIVO_Q50 = ("etiqueta 21 + dato 42 + autor 41 (con comillas y raya) = 109 caracteres y en la oración [3] caben 77; "
              "en este beat caben como máximo 90 (oración [0])")
PREGUNTAS = ("no_dicho", "spoiler", "contradice")
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


def _vuelta2_la_mantiene(r2: dict) -> dict:
    """La vuelta 2: el autor mantiene D241 (la misma ficha: «otro hecho») y recorta la cita Q50 como permite el prompt,
    en la oración [2] del beat (caben 90): «CARTA DE ERTO Y CASSO» 21 + «continua aprensión» 18 + 46 = 85."""
    q50 = dict(_cambio(r2, "ch05", 8)["ficha"])
    q50.update({"sentence_idx": 2, "palabra": "avisos", "texto": "continua aprensión"})
    return {"cambios": [{"cap": "ch04", "beat": 7, "ficha": _cambio(r2, "ch04", 7)["ficha"]},
                        {"cap": "ch05", "beat": 8, "ficha": q50}]}


def _tuplas(bs) -> list[tuple[str, int]]:
    return [(str(c), int(b)) for c, b in bs]


def _vueltas(res: dict) -> list[dict]:
    return res["reintento"]["vueltas"]


def _cortados(res: dict) -> list[str]:
    return [str(d.get("pool_id")) for d in res["reintento"]["cortados_al_cierre"]]


def _seccion_sin_pregunta(md: str) -> str:
    """Lo que el .md lista como cortado al cerrar sin pregunta (desde esa línea hasta la sección siguiente)."""
    lns = md.splitlines()
    i = next((k for k, ln in enumerate(lns) if "sin pregunt" in ln.lower() and "cortado" in ln.lower()), None)
    if i is None:
        return ""
    fin = next((k for k in range(i + 1, len(lns)) if lns[k].startswith("#")), len(lns))
    return "\n".join(lns[i:fin])


def _chequeo5(ent: dict, ficha: dict, cap: str, beat: int) -> dict:
    """El chequeo 5 de gfx_guion sobre el evento de la ficha (con su juicio, como lo lleva pantalla_colocar)."""
    c = next(c for c in ent["caps"] if c["cap"] == cap)
    ors = [s["texto"] for s in c["oraciones"]]
    si = ficha["sentence_idx"]
    voz_video = [s["texto"] for cc in ent["caps"] for s in cc["oraciones"]]
    e = {"t": 1.0, "t_mp4": 1.0, "cap": cap, "beat": beat, "funcion": "", "tipo": "ficha", "queda": True,
         "etiqueta": ficha["etiqueta"], "texto": ficha["texto"], "dur": 3.0, "lectura_min": None, "escena": None,
         "escena_t0": None, "escena_t1": None, "voz_prev": ors[si - 1], "voz_ancla": ors[si],
         "voz_next": ors[si + 1] if si + 1 < len(ors) else "", "pool_id": ficha["pool_id"],
         "juicio_autor": ficha.get("juicio_autor")}
    capd = {"cap": cap, "eventos": [e], "a_pantalla": [], "plan": {}, "resumen": [], "seg_dur": 10.0}
    out = gg.chequeos([capd], title_dur=3.0, fps=30, mezcla=None, voz_video=voz_video)
    return next(r for r in out if r["nombre"] == "cifra que contradice la voz")


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
def test_1_d241_se_pregunta_en_la_vuelta_2_y_el_autor_la_mantiene(ent, r1, r2, tmp_path):
    pedidos: list[dict] = []
    res = mp.llamar(ent, tmp_path, tope=100.0, post=_post_seq([r1, r2, _vuelta2_la_mantiene(r2)], pedidos))
    vs = _vueltas(res)
    assert len(vs) >= 2
    assert len(pedidos) == 1 + len(vs)                       # cada llamada: intento 1, vuelta 1, vuelta 2…
    assert [v["vuelta"] for v in vs] == list(range(1, len(vs) + 1))
    # vuelta 1 = el reintento de F38c: los motivos del intento 1, D241 entra en ch04 b7
    assert ("ch04", 7) in _tuplas(vs[0]["beats"]) and ("ch05", 8) in _tuplas(vs[0]["beats"])
    assert any(a["cap"] == "ch04" and a["beat"] == 7 for a in vs[0]["aplicados"])
    # la validación de la vuelta 1 pregunta por D241 (contradice) y NO la corta: la pregunta va en la vuelta 2
    assert PREGUNTA_D241 in vs[1]["motivos"]
    assert PREGUNTA_D241 in pedidos[2]["messages"][0]["content"]
    assert ("ch04", 7) in _tuplas(vs[1]["beats"])
    # lo que ya se preguntó en la vuelta 1 (T39 «50», D47 «2», D105 «1962») no se vuelve a preguntar
    assert not any(m.startswith(("T39 (", "D47 (", "D105 (")) and "¿es el mismo hecho?" in m for m in vs[1]["motivos"])
    # los confirmados se acumulan, nunca se pisan
    conf = res["confirmados"]
    assert conf["D105"] == {"no_dicho": ["1962"]} and conf["T39"] == {"spoiler": ["50"]}
    assert conf["D47"] == {"spoiler": ["2"]} and conf["D241"] == {"contradice": ["715"]}
    # vuelta 2: el autor la mantuvo → queda con su juicio; Q50 recortada entra; no quedan motivos
    fin = res["validacion"]
    s7 = next(b for b in fin["beats"] if b["cap"] == "ch04" and b["beat"] == 7)
    assert s7["ficha"]["pool_id"] == "D241"
    assert s7["ficha"]["juicio_autor"]["contradice"] == ["715"]
    assert not any(d.get("pool_id") == "D241" for d in fin["descartados"] if d.get("quien") == "validación")
    s8 = next(b for b in fin["beats"] if b["cap"] == "ch05" and b["beat"] == 8)
    assert s8["ficha"] and s8["ficha"]["pool_id"] == "Q50"
    assert len(vs) == 2 and res["reintento"]["cierre"] == "sin motivos"
    assert res["reintento"]["cortados_al_cierre"] == []
    # chequeo 5 de Fase 2: ✓ con el juicio del autor (sin juicio, ✗)
    assert _chequeo5(ent, s7["ficha"], "ch04", 7)["ok"] is True
    assert _chequeo5(ent, {**s7["ficha"], "juicio_autor": None}, "ch04", 7)["ok"] is False
    # el raw guarda las vueltas; el .md las muestra y dice por qué cerró
    raw = json.loads((tmp_path / f"{mp.ARCHIVO}.raw.json").read_text(encoding="utf-8"))
    assert [v["vuelta"] for v in raw["reintento"]["vueltas"]] == [1, 2]
    assert raw["reintento"]["cierre"] == "sin motivos"
    for v in raw["reintento"]["vueltas"]:
        assert {"vuelta", "beats", "motivos", "aplicados", "ignorados", "usd"} <= set(v)
    md = mp.a_markdown(mp.armar(ent, res)).lower()
    assert "vuelta 1" in md and "vuelta 2" in md and "sin motivos" in md


@hay_vajont
def test_2_sin_progreso_cierra(ent, r1, r2, tmp_path):
    # vuelta 1: solo la Q50 de 109 (sigue sin caber); vuelta 2: lo mismo → los motivos quedan iguales
    solo_q50 = {"cambios": [_copia(_cambio(r2, "ch05", 8))]}
    pedidos: list[dict] = []
    res = mp.llamar(ent, tmp_path, tope=100.0, post=_post_seq([r1, solo_q50, solo_q50], pedidos))
    rt = res["reintento"]
    assert rt["cierre"] == "sin progreso"
    vs = _vueltas(res)
    assert len(vs) == 2 and len(pedidos) == 3                 # no se manda una tercera vuelta
    assert vs[0]["motivos"] != vs[1]["motivos"]              # la vuelta 1 llevó los del intento 1 (con preguntas)
    fin = res["validacion"]
    assert fin["motivos"] == vs[1]["motivos"]                # después de la vuelta 2, los mismos: sin progreso
    assert any("Q50" in m and "109" in m for m in fin["motivos"])
    # la validación final de hoy: Q50 cae por caben; lo preguntado y mantenido (D105, T39, D47) queda con su juicio
    assert any(d.get("pool_id") == "Q50" and d["regla"] == "caben"
               for d in fin["descartados"] if d.get("quien") == "validación")
    for cap, beat, pid in (("ch04", 7, "D105"), ("ch04", 6, "T39"), ("ch02", 3, "D47")):
        s = next(b for b in fin["beats"] if b["cap"] == cap and b["beat"] == beat)
        assert s["ficha"] and s["ficha"]["pool_id"] == pid and s["ficha"].get("juicio_autor")
    # lo cortado sin pregunta: cada uno es un descarte de la validación final por una regla que pregunta y que el
    # autor nunca vio (con motivos iguales a la vuelta anterior no puede quedar una pregunta sin hacer: lista vacía)
    for d in rt["cortados_al_cierre"]:
        assert d["regla"] in PREGUNTAS and d.get("pool_id") not in res["confirmados"]
    assert rt["cortados_al_cierre"] == []
    md = mp.a_markdown(mp.armar(ent, res))
    assert "sin progreso" in md.lower()
    sec = _seccion_sin_pregunta(md)
    assert sec and not any(pid in sec for pid in ("Q50", "D105", "T39", "D47"))    # el .md dice qué cortó: nada


def _peor(body: dict, salida: int) -> float:
    import claude_helpers as hx
    pin, pout = hx.PRICES.get(hx._base(mp.MODELO), (0.0, 0.0))
    return mp._peor_usd(len(json.dumps(body, ensure_ascii=False)), salida, pin, pout)


def _usd(salida: int) -> float:
    import claude_helpers as hx
    return round(hx.cost_of(mp.MODELO, {"input_tokens": 1000, "output_tokens": salida}), 5)


@hay_vajont
def test_3_tope_cierra_antes_de_la_vuelta_que_no_entra(ent, r1, r2, tmp_path):
    seq, salidas = [r1, r2, _vuelta2_la_mantiene(r2)], [200, 20_000, 200]
    # corrida de medida (tope holgado): los pedidos de cada llamada
    pedidos: list[dict] = []
    mp.llamar(ent, tmp_path / "medida", tope=100.0, post=_post_seq(seq, pedidos, salidas))
    assert len(pedidos) >= 3
    peor0 = _peor(pedidos[0], mp.OUT_TOKENS_PEOR)
    peor1 = _peor(pedidos[1], mp.OUT_TOKENS_PEOR)
    peor2 = _peor(pedidos[2], max(mp.OUT_TOKENS_PEOR, salidas[1]))   # la salida peor: la mayor vista
    g1, g2 = _usd(salidas[0]), _usd(salidas[0]) + _usd(salidas[1])

    # (a) entra el intento 1 y no la vuelta 1: queda el intento 1, final, como hoy (lo que preguntaba, corta)
    tope_a = (peor0 + g1 + peor1) / 2
    assert peor0 <= tope_a < g1 + peor1
    ped_a: list[dict] = []
    res_a = mp.llamar(ent, tmp_path / "a", tope=tope_a, post=_post_seq(seq, ped_a, salidas))
    assert len(ped_a) == 1 and _vueltas(res_a) == [] and res_a["reintento"]["cierre"] == "tope"
    assert "tope" in (res_a.get("error") or "")
    assert res_a["validacion"]["motivos"] == mp.validar(r1, ent, {})["motivos"]
    assert {"D105", "T39", "D47"} <= set(_cortados(res_a))
    assert "tope" in mp.a_markdown(mp.armar(ent, res_a)).lower()

    # (b) entra la vuelta 1 y no la vuelta 2: la pregunta de D241 queda sin hacer → al cierre corta
    tope_b = g2 + peor2 - 1e-4
    assert g1 + peor1 <= tope_b, "la vuelta 2 no es más cara que la 1: el escenario (b) no se puede armar"
    ped_b: list[dict] = []
    res_b = mp.llamar(ent, tmp_path / "b", tope=tope_b, post=_post_seq(seq, ped_b, salidas))
    assert len(ped_b) == 2 and len(_vueltas(res_b)) == 1 and res_b["reintento"]["cierre"] == "tope"
    fin = res_b["validacion"]
    d = next(d for d in fin["descartados"] if d.get("pool_id") == "D241" and d.get("quien") == "validación")
    assert d["regla"] == "contradice"
    assert "D241" in _cortados(res_b)
    md = mp.a_markdown(mp.armar(ent, res_b))
    assert "tope" in md.lower()
    assert "D241" in _seccion_sin_pregunta(md), "el .md no dice que D241 se cortó sin pregunta"


# ═══════════════════════ §A.2 «caben» ═══════════════════════

@hay_vajont
def test_4_motivo_de_caben_de_q50(ent, r1, r2):
    v1 = mp.validar(r1, ent)
    fus, _, _ = mp.fusionar(r1, r2, mp.beats_con_motivo(v1["motivos_beat"]))
    for v in (mp.validar(fus, ent), mp.validar(fus, ent, mp._confirmar(v1["preguntas"]))):
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
    assert mp.PROMPT_VERSION == "m01e-6"
    hoy = mp.PANTALLA_SYSTEM
    assert VIEJA not in hoy and NUEVA not in hoy              # m01e-6 lo dice con sus palabras (las de la prueba 1)
    assert ("Etiqueta + dato —y en una cita, también el autor y 5 caracteres de comillas y raya— no pueden pasar de los "
            "caracteres que caben en la oración ancla (`caben`); si no caben, elegí otra oración o un dato más corto.") in hoy
    assert hoy.count("`caben`") == 1
    assert mp.prompt_md5() != MD5_M01E_4
    assert difflib is not None
