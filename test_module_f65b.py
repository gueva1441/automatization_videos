"""
test_module_f65b.py — F65b (HANDOFF_F65b_qa_del_papel; DECISIONES 2026-10-31 16:13): el QA del papel.
    Etapa A  m01e_pantalla.sugerir (hasta n alternativas de UN beat, sin tocar el papel): el USER, el caché, los excluidos en
             código, candados por validar, UNA llamada al verificador solo con las marcas del beat, «corta»/«pasa», sin JSON,
             candado de la entrada; aplicar_veredicto compartido; md5 de los prompts sin cambios; editar conserva
             juicio_verificador.
    Etapa B  rutas del servidor (por HTTP, en un puerto local): GET /papel con descartes por beat, /revisar fuera del papel, /editar
             (null, alternativa con juicio_verificador, invalida la aprobación), /sugerir en un hilo con 409 y status, /aprobar
             (400 sin quién, md5 + fecha, nada más corre), preflight con solo el papel y visor con 0 caps.
Sin API: toda llamada va con `post`/`juez` falsos y `claude_helpers._post` explota si alguien lo alcanza (fixture autouse).
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import claude_helpers as hx  # noqa: E402
from script_engine import m01e_pantalla as mp  # noqa: E402
from script_engine import pantalla_verificador as pv  # noqa: E402

TID = "t-papel"
SEG = {"valor": 1.0, "oraciones": 10, "caps": 2, "voz": "x"}


@pytest.fixture(autouse=True)
def _sin_api(monkeypatch):
    def explota(body):
        raise AssertionError(f"llamada real al modelo en un test: {body.get('model')}")
    monkeypatch.setattr(hx, "_post", explota)
    monkeypatch.setattr(mp, "seg_por_palabra", lambda *a, **k: SEG)


POOL = {"datos": [{"id": "D1", "texto": "La presa mide 266 metros.", "fuente": "F", "fecha": "1960", "cita_literal": "266 m"},
                  {"id": "D3", "texto": "Cruzaron cerca de 8000 españoles.", "fuente": "F", "fecha": "1960"},
                  {"id": "D4", "texto": "El acuerdo se firmó en 1958.", "fuente": "F", "fecha": "1958"},
                  {"id": "D5", "texto": "El río arrastra el polvo hasta el mar.", "fuente": "F", "fecha": "1960"}],
        "cronologia": [], "personajes": [], "lugares": [],
        "citas": [{"id": "Q1", "texto": "Nadie nos avisó nunca de nada", "autor": "Una vecina", "rol": "vecina",
                   "fecha": None, "testimonio": True, "fuente": "F"}]}
ESC = {"pico": {"beat": 3}, "a_pantalla": [],
       "beats": [{"n": 1, "cap": 1, "funcion": "gancho", "dato_central": "", "datos_apoyo": [], "flash_forward": True},
                 {"n": 2, "cap": 2, "funcion": "planteo", "dato_central": "D4", "datos_apoyo": []},
                 {"n": 3, "cap": 2, "funcion": "pico", "dato_central": "", "datos_apoyo": []}]}
PARRAFOS = [{"cap": 1, "beat": 1, "texto": "Hoy, en 2024, el valle sigue vacío. Nadie volvió."},
            {"cap": 2, "beat": 2, "texto": "El baile fue en 1961. Se casaron en 1962. Cruzaron ocho mil españoles por un acuerdo. El acuerdo venía desde 1950."},
            {"cap": 2, "beat": 3, "texto": "Nadie nos avisó, dice ella. El valle quedó en silencio."}]


def _fi(pid: str, si: int, pal: str, et: str, txt: str, resp: str) -> dict:
    return {"pool_id": pid, "sentence_idx": si, "palabra": pal, "etiqueta": et, "texto": txt, "respaldo": resp, "autor": None, "aporta": "suma"}


F_D4 = _fi("D4", 0, "valle", "EL ACUERDO", "Firmado en 1958", "firmó en 1958")                       # gancho
F_D1 = _fi("D1", 2, "acuerdo", "LA PRESA", "Mide 266 metros", "mide 266 metros")                     # beat 2, limpia
F_Q1 = _fi("Q1", 4, "avisó", "UNA VECINA", "Nadie nos avisó nunca de nada", "Nadie nos avisó nunca de nada")   # pico
F_D3 = _fi("D3", 2, "españoles", "LOS QUE CRUZARON", "Cerca de 8000 españoles", "cerca de 8000 españoles")     # no_dicho «8000»
F_D5 = _fi("D5", 3, "acuerdo", "EL RÍO", "Lleva el polvo al mar", "arrastra el polvo hasta el mar")   # limpia, sin marcas
RESP = {"beats": [{"cap": "ch01", "beat": 1, "ficha": F_D4, "sello": None}, {"cap": "ch02", "beat": 2, "ficha": F_D1, "sello": None},
                  {"cap": "ch02", "beat": 3, "ficha": F_Q1, "sello": None}], "relojes": [], "descartados": []}


def _msg(obj, usage: dict | None = None) -> dict:
    txt = obj if isinstance(obj, str) else json.dumps(obj, ensure_ascii=False)
    return {"content": [{"type": "text", "text": txt}], "usage": usage or {"input_tokens": 1000, "output_tokens": 100}, "stop_reason": "end_turn"}


@pytest.fixture
def env(tmp_path):
    d = tmp_path / TID
    d.mkdir()
    for n, o in (("01a_escaleta.json", ESC), ("01b_narracion_v3.json", {"parrafos": PARRAFOS}), ("00_pool_v3.json", POOL),
                 ("01a_skeleton.json", {"chapters": [{"chapter_number": 1, "title": "Uno"}, {"chapter_number": 2, "title": "Dos"}]})):
        (d / n).write_text(json.dumps(o, ensure_ascii=False), encoding="utf-8")
    papel = mp.generar(TID, tmp_path, vocabulario=["CALMA"], post=lambda b: _msg(RESP), log=[])
    assert [b["ficha"]["pool_id"] for b in papel["beats"]] == ["D4", "D1", "Q1"]
    return {"dir": d, "steps": tmp_path, "papel": papel}


def _post_alts(alts, pedidos: list[dict] | None = None):
    def post(body):
        if pedidos is not None:
            pedidos.append(body)
        return _msg({"alternativas": alts})
    return post


def _juez(veredictos: dict[str, str], reg: list | None = None):
    def juez(marcas, caps):
        if reg is not None:
            reg.append(marcas)
        return {"veredictos_fichas": [{"pool_id": m["pool_id"], "cap": m["cap"], "beat": m["beat"], "veredicto": veredictos.get(m["pool_id"], "pasa"),
                                       "motivo": f"motivo de {m['pool_id']}", "oracion": {"cap": "ch02", "idx": 2}} for m in marcas],
                "veredictos_descartes": [], "usd": 0.07, "usage": {}, "segundos": 1.0, "pedido_md5": "x", "error": None}
    return juez


def test_a1_prompts_no_cambian_y_textos_fuera_del_md5():
    assert hashlib.md5(mp.PANTALLA_SYSTEM.encode("utf-8")).hexdigest() == "85d094bed6090b14d1802ca97433d982"
    assert hashlib.md5(pv.SYSTEM_V.encode("utf-8")).hexdigest() == "104b9ea817690c5b45afbe74f87a2111"
    assert mp.prompt_md5() == "f2bfdf2044a4c77a59fc62ebe93966c2" and mp.PROMPT_VERSION == "m01e-7"
    assert mp.SUGERIR_N == 3 and "Proponé hasta {n} fichas" in mp.SUGERIR_USER and mp.FORMATO_SUGERIR.startswith('{"alternativas": [{"pool_id": "D49"')


def test_a2_body_cacheado_y_prefijo_del_autor():
    b = hx.body_cacheado("S", "U", "m", "medium", resto="R")
    assert b["system"] == [{"type": "text", "text": "S", "cache_control": {"type": "ephemeral"}}]
    assert b["messages"][0]["content"] == [{"type": "text", "text": "U", "cache_control": {"type": "ephemeral"}}, {"type": "text", "text": "R"}]
    assert (b["model"], b["max_tokens"], b["output_config"]) == ("m", hx.MAX_TOKENS, {"effort": "medium"})
    assert len(hx.body_cacheado("S", "U", "m", "medium")["messages"][0]["content"]) == 1
    assert hx.tokens_entrada({"input_tokens": 1, "cache_creation_input_tokens": 2, "cache_read_input_tokens": 3}) == 6


def test_a3_el_autor_usa_el_cache_y_la_vuelta_comparte_el_prefijo(tmp_path):
    d = tmp_path / TID
    d.mkdir()
    for n, o in (("01a_escaleta.json", ESC), ("01b_narracion_v3.json", {"parrafos": PARRAFOS}), ("00_pool_v3.json", POOL),
                 ("01a_skeleton.json", {"chapters": [{"chapter_number": 1, "title": "Uno"}, {"chapter_number": 2, "title": "Dos"}]})):
        (d / n).write_text(json.dumps(o, ensure_ascii=False), encoding="utf-8")
    pedidos: list[dict] = []
    vacio = {"beats": [], "relojes": [], "descartados": []}

    def post(body):
        pedidos.append(body)
        return _msg(vacio)
    mp.generar(TID, tmp_path, vocabulario=["CALMA"], post=post, log=[])
    a, b = pedidos[0]["messages"][0]["content"], pedidos[1]["messages"][0]["content"]
    assert len(a) == 1 and len(b) == 2 and a[0] == b[0] and a[0]["cache_control"] == {"type": "ephemeral"}
    assert pedidos[0]["system"][0]["text"] == mp.PANTALLA_SYSTEM and "TU RESPUESTA ANTERIOR" in b[1]["text"]


def test_a4_el_user_y_el_caché_de_sugerir(env):
    pedidos: list[dict] = []
    r = mp.sugerir(TID, "ch02", 2, 3, steps_dir=env["steps"], post=_post_alts([], pedidos))
    assert r["alternativas"] == [] and r["descartadas"] == [] and "error" not in r
    c = pedidos[0]["messages"][0]["content"]
    raw = json.loads((env["dir"] / "01e_pantalla.raw.json").read_text(encoding="utf-8"))
    assert c[0]["text"] == mp.pedido(raw["entrada"]) and c[0]["cache_control"]
    assert hashlib.md5(c[0]["text"].encode("utf-8")).hexdigest() == env["papel"]["entrada_md5"]
    assert c[1]["text"].startswith("\n\nTU RESPUESTA ANTERIOR (el papel completo, como contexto):\n" + json.dumps(raw["final"], ensure_ascii=False))
    assert "OTRAS opciones para ch02 beat 2. Proponé hasta 3 fichas" in c[1]["text"]
    assert "ya están en pantalla en este video): D1, D4, Q1." in c[1]["text"]
    assert c[1]["text"].endswith("\n\nFormato de salida: " + mp.FORMATO_SUGERIR)
    assert (pedidos[0]["model"], pedidos[0]["output_config"]) == (mp.MODELO, {"effort": mp.EFFORT})
    assert pedidos[0]["system"][0]["text"] == mp.PANTALLA_SYSTEM


def test_a5_excluidos_en_codigo_antes_de_validar_y_el_gancho_no_se_come_otra_ficha(env):
    # en ch01 beat 1, una alternativa con el pool_id de una ficha de otro beat: se descarta en código
    otra = _fi("D1", 0, "valle", "LA PRESA", "Mide 266 metros", "mide 266 metros")
    r = mp.sugerir(TID, "ch01", 1, 3, steps_dir=env["steps"], post=_post_alts([otra, F_D5 | {"sentence_idx": 0, "palabra": "valle"}]), juez=_juez({}))
    assert [d["motivo"] for d in r["descartadas"]] == ["ya está en pantalla"] and r["descartadas"][0]["quien"] == "código"
    assert [a["pool_id"] for a in r["alternativas"]] == ["D5"]


def test_a6_candado_y_verificador_solo_con_las_marcas_del_beat(env):
    # D3: marca no_dicho «8000» (el verificador decide); D5: limpia; candado: cifra que no está en el respaldo
    mala = _fi("D5", 3, "acuerdo", "EL RÍO", "Lleva 999 toneladas", "arrastra el polvo hasta el mar")
    reg: list[list] = []
    r = mp.sugerir(TID, "ch02", 2, 3, steps_dir=env["steps"], post=_post_alts([F_D3, mala]), juez=_juez({}, reg))
    assert [a["pool_id"] for a in r["alternativas"]] == ["D3"]
    assert r["alternativas"][0]["juicio_verificador"] == {"regla": ["no_dicho"], "motivo": "motivo de D3", "tokens": {"no_dicho": ["8000"]}}
    assert r["descartadas"][0]["regla"] == "candado" and r["descartadas"][0]["quien"] == "validación" and "999" in r["descartadas"][0]["motivo"]
    assert len(reg) == 1 and {(m["pool_id"], m["cap"], m["beat"]) for m in reg[0]} == {("D3", "ch02", 2)}     # nada de otros beats
    for campo in ("caben", "caracteres", "estilo", "oracion", "respaldo", "aporta", "sentence_idx", "palabra_en_oracion"):
        assert campo in r["alternativas"][0]
    assert r["usd_verificador"] == 0.07 and r["usd"] == round(r["usd_autor"] + 0.07, 5)


def test_a7_el_verificador_corta_y_sin_marcas_no_se_llama(env):
    r = mp.sugerir(TID, "ch02", 2, 3, steps_dir=env["steps"], post=_post_alts([F_D3]), juez=_juez({"D3": "corta"}))
    assert r["alternativas"] == [] and r["descartadas"][0]["quien"] == "verificador" and "motivo de D3" in r["descartadas"][0]["motivo"]

    def prohibido(m, c):
        raise AssertionError("sin marcas no se llama")
    r2 = mp.sugerir(TID, "ch02", 2, 3, steps_dir=env["steps"], post=_post_alts([F_D5]), juez=prohibido)
    assert [a["pool_id"] for a in r2["alternativas"]] == ["D5"] and "juicio_verificador" not in r2["alternativas"][0]
    assert r2["usd_verificador"] == 0.0


def test_a8_una_cita_testimonio_no_cae_por_cita_sin_fecha_y_hasta_n(env):
    # Q1 (testimonio, sin fecha) en ch02 beat 2: con el pool real no cae; hasta n propuestas
    (env["dir"] / "01e_pantalla.json").write_text(json.dumps({**env["papel"], "beats": [
        {**b, "ficha": None} if b["beat"] == 3 else b for b in env["papel"]["beats"]]}, ensure_ascii=False), encoding="utf-8")
    q = _fi("Q1", 2, "acuerdo", "UNA VECINA", "Nadie nos avisó nunca de nada", "Nadie nos avisó nunca de nada")
    r = mp.sugerir(TID, "ch02", 2, 1, steps_dir=env["steps"], post=_post_alts([q, F_D5]), juez=_juez({}))
    assert [a["pool_id"] for a in r["alternativas"]] == ["Q1"] and r["alternativas"][0]["estilo"] == "cita"


def test_a9_sin_json_un_reintento_y_vuelve_vacio(env):
    pedidos: list[dict] = []

    def post(body):
        pedidos.append(body)
        return _msg("no hay json")
    r = mp.sugerir(TID, "ch02", 2, 3, steps_dir=env["steps"], post=post)
    assert len(pedidos) == 2 and r["alternativas"] == [] and r["error"] == "sin JSON" and r["usd"] > 0
    assert "TU RESPUESTA ANTERIOR TUVO ESTOS PROBLEMAS" in pedidos[1]["messages"][0]["content"][1]["text"]


def test_a10_candado_de_la_entrada_y_beat_inexistente(env):
    with pytest.raises(ValueError, match="no hay beat"):
        mp.sugerir(TID, "ch02", 99, 3, steps_dir=env["steps"], post=_post_alts([]))
    f = env["dir"] / "01e_pantalla.json"
    f.write_text(json.dumps({**env["papel"], "entrada_md5": "otro"}), encoding="utf-8")
    with pytest.raises(ValueError, match="el raw no es de este papel"):
        mp.sugerir(TID, "ch02", 2, 3, steps_dir=env["steps"], post=_post_alts([]))
    f.write_text(json.dumps(env["papel"]), encoding="utf-8")
    (env["dir"] / "01b_narracion_v3.json").write_text(json.dumps({"parrafos": PARRAFOS[:2]}), encoding="utf-8")
    with pytest.raises(ValueError, match="la entrada de hoy no es la del papel"):
        mp.sugerir(TID, "ch02", 2, 3, steps_dir=env["steps"], post=_post_alts([]))


def test_a11_no_toca_el_papel_y_deja_el_log(env):
    f = env["dir"] / "01e_pantalla.json"
    antes = f.read_bytes()
    mp.sugerir(TID, "ch02", 2, 3, steps_dir=env["steps"], post=_post_alts([F_D5]), juez=_juez({}))
    assert f.read_bytes() == antes
    fila = json.loads((env["dir"] / "01e_sugerir.log.jsonl").read_text(encoding="utf-8").splitlines()[-1])
    assert fila["cap"] == "ch02" and "OTRAS opciones" in fila["pedido"] and fila["respuesta_cruda"] and fila["resultado"]["alternativas"]


def test_a12_editar_conserva_juicio_verificador(env):
    r = mp.sugerir(TID, "ch02", 2, 3, steps_dir=env["steps"], post=_post_alts([F_D3]), juez=_juez({}))
    alt = r["alternativas"][0]
    mp.editar(TID, [{"cap": "ch02", "beat": 2, "ficha": alt}], env["steps"])
    b = next(x for x in mp.cargar_papel(TID, env["steps"])["beats"] if x["beat"] == 2)
    assert b["ficha"]["juicio_verificador"]["tokens"] == {"no_dicho": ["8000"]} and b["ficha"]["respaldo"] == alt["respaldo"]
    assert b["ficha"]["aporta"] == "suma" and b["ficha"]["editado"] is True


def test_a13_aplicar_veredicto():
    fi = {"pool_id": "D1", "etiqueta": "E", "texto": "T", "sentence_idx": 0}
    m = {"que": "ficha", "pool_id": "D1", "cap": "ch01", "beat": 1, "regla": "spoiler", "coincidencia": {"token": "2"}}
    assert mp.aplicar_veredicto(dict(fi), "ch01", 1, [], {}) is None
    f2 = dict(fi)
    assert mp.aplicar_veredicto(f2, "ch01", 1, [m], {}) is None and f2["juicio_verificador"]["motivo"] == "sin veredicto"
    d = mp.aplicar_veredicto(dict(fi), "ch01", 1, [m], {("D1", "ch01", 1): {"veredicto": "corta", "motivo": "x", "oracion": {"cap": "ch02", "idx": 3}}})
    assert (d["quien"], d["regla"], d["motivo"], d["tokens"]) == ("verificador", "spoiler", "x (ch02 [3])", {"spoiler": ["2"]})


# ═══════════════════════ Etapa B: rutas del servidor ═══════════════════════

@pytest.fixture
def srv(env, tmp_path, monkeypatch):
    """Un QA Studio de verdad en un puerto local, sobre el topic de `env` (base = tmp, steps en base/data/scripts/_steps)."""
    import shutil
    import threading
    from http.server import ThreadingHTTPServer

    import fase1_5 as f15
    import qa_studio_server as qa
    base = tmp_path / "base"
    sd = base / "data" / "scripts" / "_steps"
    sd.mkdir(parents=True)
    shutil.copytree(env["dir"], sd / TID)
    monkeypatch.setattr(f15, "STEPS_DIR", sd)
    f15.aprobar_narracion(TID, "Omar 2026-10-31")                       # F67b: sin eso, /papel/aprobar responde 409
    st = qa.QAState(TID, base)
    monkeypatch.setattr(qa, "STATE", st)
    monkeypatch.setattr(qa, "TOPIC_ID", TID)
    qa._SUG.update(running=False, result=None, error=None, cap=None, beat=None)
    http = ThreadingHTTPServer(("127.0.0.1", 0), qa.Handler)
    threading.Thread(target=http.serve_forever, daemon=True).start()
    yield {"url": f"http://127.0.0.1:{http.server_address[1]}", "sd": sd, "dir": sd / TID, "qa": qa, "f15": f15, "state": st}
    http.shutdown()


def _get(srv, ruta: str) -> tuple[int, dict]:
    import urllib.error
    import urllib.request
    try:
        with urllib.request.urlopen(srv["url"] + ruta) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())


def _post(srv, ruta: str, body: dict) -> tuple[int, dict]:
    import urllib.error
    import urllib.request
    req = urllib.request.Request(srv["url"] + ruta, data=json.dumps(body).encode("utf-8"), method="POST",
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())


def _papel(srv) -> dict:
    return json.loads((srv["dir"] / "01e_pantalla.json").read_text(encoding="utf-8"))


def test_b1_get_papel_con_descartes_por_beat(srv):
    f = srv["dir"] / "01e_pantalla.json"
    p = _papel(srv)
    p["descartados"] = [{"pool_id": "D4", "tipo": "voz_lo_dice", "motivo": "ya lo dice", "quien": "modelo"},       # beat 2 (dato central)
                        {"pool_id": "D3", "tipo": "otro", "motivo": "no suma", "quien": "modelo"},                  # sin beat
                        {"pool_id": "D5", "cap": "ch02", "beat": 3, "que": "ficha", "regla": "caben", "motivo": "x", "quien": "validación"}]
    f.write_text(json.dumps(p, ensure_ascii=False), encoding="utf-8")
    st, v = _get(srv, "/papel")
    assert st == 200 and v["estado"] == {"aprobado": False, "motivo": "el papel no está aprobado"}
    assert v["md5"] == srv["f15"].md5_papel(p) and v["fichas"] == 3 and v["revisadas"] == 0 and v["caps"][1]["titulo"] == "Dos"
    b1, b2, b3 = v["beats"]
    assert (b1["cap"], b1["beat"], b1["funcion"], b1["revisado"]) == ("ch01", 1, "gancho", False)
    assert b1["ficha"]["pool_id"] == "D4" and b1["ficha"]["oracion"].startswith("Hoy")
    assert [d["pool_id"] for d in b2["descartes"]] == ["D4"] and b2["descartes"][0]["texto"] == "El acuerdo se firmó en 1958."
    assert (b3["descartes"][0]["pool_id"], b3["descartes"][0]["tipo"], b3["descartes"][0]["quien"]) == ("D5", "caben", "validación")
    assert [d["pool_id"] for d in v["sin_beat"]] == ["D3"]


def test_b2_revisar_va_fuera_del_papel_y_no_invalida(srv):
    antes = (srv["dir"] / "01e_pantalla.json").read_bytes()
    st, r = _post(srv, "/papel/revisar", {"cap": "ch02", "beat": 2, "on": True})
    assert st == 200 and r["revisados"] == [["ch02", 2]]
    assert (srv["dir"] / "01e_pantalla.json").read_bytes() == antes
    assert json.loads((srv["dir"] / "01e_pantalla.revision.json").read_text(encoding="utf-8")) == {"revisados": [["ch02", 2]]}
    v = _get(srv, "/papel")[1]
    assert v["revisadas"] == 1 and v["beats"][1]["revisado"] is True
    assert _post(srv, "/papel/revisar", {"cap": "ch02", "beat": 2, "on": False})[1]["revisados"] == []
    assert _post(srv, "/papel/revisar", {"cap": "../x", "beat": 2, "on": True})[0] == 400
    assert _post(srv, "/papel/revisar", {"cap": "ch02", "beat": "2", "on": True})[0] == 400


def test_b3_editar_null_alternativa_y_la_aprobacion_se_invalida(srv):
    assert _post(srv, "/papel/aprobar", {"por": "Omar"})[0] == 200
    v = _get(srv, "/papel")[1]
    assert v["estado"]["aprobado"] is True and v["aprobado_por"]["por"] == "Omar"
    assert _post(srv, "/papel/revisar", {"cap": "ch02", "beat": 2, "on": True})[0] == 200
    assert _get(srv, "/papel")[1]["estado"]["aprobado"] is True                # el ✓ no invalida
    assert _post(srv, "/papel/editar", {"cap": "ch02", "beat": 2, "ficha": None})[0] == 200
    v = _get(srv, "/papel")[1]
    assert v["beats"][1]["ficha"] is None and v["estado"]["aprobado"] is False and "cambió después de la aprobación" in v["estado"]["motivo"]
    assert (srv["dir"] / "01e_pantalla.antes_de_edicion.json").exists() and "ediciones" in _papel(srv)
    # una alternativa de «sugerir» se guarda con su juicio y su aporta; la mano, con «(edición a mano)»
    alt = {**F_D3, "juicio_verificador": {"regla": ["no_dicho"], "motivo": "m", "tokens": {"no_dicho": ["8000"]}}}
    assert _post(srv, "/papel/editar", {"cap": "ch02", "beat": 2, "ficha": alt})[0] == 200
    f = _get(srv, "/papel")[1]["beats"][1]["ficha"]
    assert f["juicio_verificador"]["tokens"] == {"no_dicho": ["8000"]} and f["aporta"] == "suma" and f["caben"] and f["caracteres"]
    mano = {"pool_id": "D3", "sentence_idx": 2, "palabra": "españoles", "etiqueta": "OTRA", "texto": "Otro texto"}
    assert _post(srv, "/papel/editar", {"cap": "ch02", "beat": 2, "ficha": mano})[0] == 200
    f = _get(srv, "/papel")[1]["beats"][1]["ficha"]
    assert f["aporta"] == "(edición a mano)" and f["editado"] is True and f["texto"] == "Otro texto"
    assert _post(srv, "/papel/editar", {"cap": "ch02", "beat": 2})[0] == 400        # sin la clave ficha
    assert _post(srv, "/papel/editar", {"cap": "ch09", "beat": 2, "ficha": None})[0] == 400


def test_b4_sugerir_en_un_hilo_409_y_status(srv, monkeypatch):
    import threading
    import time as _t
    suelta = threading.Event()
    llamadas = []

    def falso(tid, cap, beat, n, *, steps_dir=None, **k):
        llamadas.append((tid, cap, beat, n, steps_dir))
        suelta.wait(10)
        return {"cap": cap, "beat": beat, "alternativas": [{"pool_id": "D3"}], "descartadas": [], "usd": 0.14}
    monkeypatch.setattr(mp, "sugerir", falso)
    assert _post(srv, "/papel/sugerir", {"cap": "ch02", "beat": 2}) == (200, {"started": True})
    assert _post(srv, "/papel/sugerir", {"cap": "ch02", "beat": 3})[0] == 409
    assert _get(srv, "/papel/sugerir_status")[1]["running"] is True
    suelta.set()
    for _ in range(100):
        s = _get(srv, "/papel/sugerir_status")[1]
        if not s["running"]:
            break
        _t.sleep(0.05)
    assert s["result"]["alternativas"] == [{"pool_id": "D3"}] and s["error"] is None and (s["cap"], s["beat"]) == ("ch02", 2)
    assert llamadas == [(TID, "ch02", 2, 3, srv["sd"])]
    monkeypatch.setattr(mp, "sugerir", lambda *a, **k: (_ for _ in ()).throw(ValueError("el raw no es de este papel")))
    assert _post(srv, "/papel/sugerir", {"cap": "ch02", "beat": 2})[0] == 200
    for _ in range(100):
        s = _get(srv, "/papel/sugerir_status")[1]
        if not s["running"]:
            break
        _t.sleep(0.05)
    assert "el raw no es de este papel" in s["error"] and s["result"] is None


def test_b5_aprobar_y_nada_mas_corre(srv, monkeypatch):
    def explota(*a, **k):
        raise AssertionError("aprobar no corre nada más")
    monkeypatch.setattr(srv["f15"], "process_topic", explota)
    assert _post(srv, "/papel/aprobar", {"por": "  "})[0] == 400
    assert _post(srv, "/papel/aprobar", {})[0] == 400
    assert "aprobado" not in _papel(srv)
    st, r = _post(srv, "/papel/aprobar", {"por": "Omar Guevara"})
    assert st == 200 and r["aprobado"]["por"] == "Omar Guevara" and "T" in r["aprobado"]["fecha"] and " " not in r["aprobado"]["fecha"]
    p = _papel(srv)
    assert p["aprobado"]["md5"] == srv["f15"].md5_papel(p) and srv["f15"].estado_papel(TID)[0] is True


def test_b6_preflight_con_solo_el_papel_y_visor_con_cero_caps(srv, tmp_path):
    qa = srv["qa"]
    assert qa._preflight(srv["state"]) == [] and srv["state"].caps() == []
    assert _get(srv, "/caps") == (200, [])
    assert _get(srv, "/topic")[0] == 200
    vacio = qa.QAState("otro", tmp_path / "vacia")
    assert any("no tiene assets, audio ni papel" in x for x in qa._preflight(vacio))


def test_b7_sin_papel_el_get_no_rompe(srv):
    (srv["dir"] / "01e_pantalla.json").unlink()
    st, v = _get(srv, "/papel")
    assert st == 200 and v["sin_papel"] is True and v["beats"] == []
    assert _post(srv, "/papel/aprobar", {"por": "Omar"})[0] == 400


def test_b8_el_servidor_no_escribe_el_json_del_papel():
    src = (Path(__file__).resolve().parent / "qa_studio_server.py").read_text(encoding="utf-8")
    zona = src[src.index("ZONA PAPEL"):src.index("class Handler(BaseHTTPRequestHandler)")]
    assert "_write_json" not in zona and "write_text" not in zona and "open(" not in zona


def test_b9_un_papel_nuevo_borra_la_revision_y_la_cache_no(env):
    mp.marcar_revisado(TID, "ch02", 2, True, env["steps"])
    assert mp.revisados(TID, env["steps"]) == [["ch02", 2]]
    mp.generar(TID, env["steps"], vocabulario=["CALMA"], post=lambda b: _msg(RESP), log=[])     # caché: misma clave
    assert mp.revisados(TID, env["steps"]) == [["ch02", 2]]
    (env["dir"] / "01e_pantalla.raw.json").unlink()
    mp.generar(TID, env["steps"], vocabulario=["CALMA"], post=lambda b: _msg(RESP), log=[])
    assert mp.revisados(TID, env["steps"]) == []
