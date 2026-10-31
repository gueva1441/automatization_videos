"""
test_module_f66.py — F66 (HANDOFF_F66_verificador_narracion): el verificador de la narración a producción.
    Etapa A  narracion_verificador: SYSTEM_B/FORMATO_B literales del lab (md5), user_b, parseo, 1 reintento (sin JSON o
             excepción de API), paralelismo con 7 caps, un cap que falla dos veces no frena.
    Etapa B  edit_sentences sin parámetros nuevos = la guardia de hoy; con guard/cifras_ok, sin adjetivos y con las cifras
             de los datos; particionar sin title_list = igual, con title_list no llama a titles; run_verificacion:
             contradice → edición aceptada → re-partición → re-verifica solo el cap cambiado; la guardia rechaza → aviso y
             la cadena sigue; sigue contradiciendo y nuevas; aviso en el papel y en la PARADA; --verificar-narracion no
             llama al guionista; orden de run_guion_v4.
Sin API: toda llamada va con `post` falso y `claude_helpers._post` explota si alguien lo alcanza (fixture autouse).
"""
from __future__ import annotations

import hashlib
import json
import sys
import threading
import time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import fase1_5 as f15  # noqa: E402
from script_engine import guion_v4 as g4  # noqa: E402
from script_engine import m01d_particion as md  # noqa: E402
from script_engine import m01e_pantalla as mp  # noqa: E402
from script_engine import narracion_verificador as nv  # noqa: E402

ROOT = Path(__file__).resolve().parent
MD5_SYSTEM_B = "ce31cc515a077d74da72479e9693296e"       # F63 B (candado)


def _cap(n: int, oraciones: list[str]) -> dict:
    return {"cap": f"ch{n:02d}", "n": n, "titulo": "", "oraciones": [{"idx": i, "beat": n, "texto": t, "caben": 50}
                                                                      for i, t in enumerate(oraciones)]}


ARCHIVO = [{"id": "D1", "texto": "El pie no cerraba.", "fecha": "1963", "fuente": "F", "contexto_fuente": "never healed"}]
DISPUTAS = {"versiones": [], "contradicciones": []}


def _msg(obj: dict | str, usage: dict | None = None) -> dict:
    txt = obj if isinstance(obj, str) else json.dumps(obj, ensure_ascii=False)
    return {"content": [{"type": "text", "text": txt}], "usage": usage or {"input_tokens": 100, "output_tokens": 10},
            "stop_reason": "end_turn"}


@pytest.fixture(autouse=True)
def _sin_api(monkeypatch):
    """Nada de este archivo llega a la API: el POST real explota."""
    import claude_helpers as hx

    def explota(body):
        raise AssertionError(f"llamada real al modelo en un test: {body.get('model')}")
    monkeypatch.setattr(hx, "_post", explota)


# ═══════════════════════ Etapa A ═══════════════════════

def test_a1_system_y_formato_literales_del_lab():
    assert hashlib.md5(nv.SYSTEM_B.encode("utf-8")).hexdigest() == MD5_SYSTEM_B
    lab = (ROOT / "lab" / "hyperframes" / "f63" / "etapa_b_verificador.py").read_text(encoding="utf-8").replace("\r\n", "\n")
    assert f'SYSTEM_B = """{nv.SYSTEM_B}"""' in lab
    assert nv.FORMATO_B.startswith('{"cap": "ch01", "afirmaciones": [{"oracion": 0, "afirmacion": "…", "estado": "respaldada"')
    assert (nv.MODELO, nv.EFFORT, nv.INTENTOS) == ("claude-opus-5-5", "medium", 2)


def test_a2_user_b_como_el_lab_y_archivo_b_reduce():
    cap = _cap(1, ["Uno.", "Dos."])
    u = nv.user_b(cap, ARCHIVO, DISPUTAS)
    assert u.endswith("\n\nFormato de salida: " + nv.FORMATO_B)
    cuerpo = json.loads(u.split("\n\nFormato de salida: ")[0])
    assert list(cuerpo) == ["cap", "oraciones", "archivo", "disputas"]
    assert cuerpo["oraciones"] == [{"idx": 0, "texto": "Uno."}, {"idx": 1, "texto": "Dos."}]    # sin beat ni caben
    ent = {"archivo": [{"id": "D1", "texto": "t", "fuente": "F", "fecha": "1", "beats_que_lo_cuentan": [1], "autor": "a",
                        "contexto_fuente": "c"}]}
    assert nv.archivo_b(ent) == [{"id": "D1", "texto": "t", "fecha": "1", "fuente": "F", "contexto_fuente": "c"}]


def test_a3_parseo_body_y_listas():
    pedidos: list[dict] = []
    resp = {"cap": "ch01", "afirmaciones": [
        {"oracion": 0, "afirmacion": "va a cerrar", "estado": "contradice", "ids": ["D1"], "fragmento": "no cerraba"},
        {"oracion": 1, "afirmacion": "dos", "estado": "sin_respaldo", "ids": [], "fragmento": None},
        {"oracion": 1, "afirmacion": "tres", "estado": "respaldada", "ids": ["D1"], "fragmento": None},
        {"oracion": 9, "afirmacion": "fuera", "estado": "contradice", "ids": ["D1"], "fragmento": "x"}]}

    def post(body):
        pedidos.append(body)
        return _msg(resp)
    log: list[str] = []
    r = nv.verificar_caps([_cap(1, ["Ese pie va a cerrar.", "Dos."])], ARCHIVO, DISPUTAS, post=post, log=log)
    b = pedidos[0]
    assert (b["model"], b["system"], b["output_config"]) == ("claude-opus-5-5", nv.SYSTEM_B, {"effort": "medium"})
    assert r["contradice"][0] == {"cap": "ch01", "oracion": 0, "texto": "Ese pie va a cerrar.", "beat": 1,
                                  "afirmacion": "va a cerrar", "ids": ["D1"], "fragmento": "no cerraba"}
    assert r["contradice"][1]["oracion"] == 9 and r["contradice"][1]["texto"] is None      # idx inexistente: anotado
    assert [x["afirmacion"] for x in r["sin_respaldo"]] == ["dos"]
    pc = r["por_cap"]["ch01"]
    assert len(pc["afirmaciones"]) == 4 and pc["error"] is None and pc["intentos"] == 1 and pc["usd"] > 0
    assert r["usd"] == pc["usd"] and log


def test_a4_un_reintento_sin_json_y_por_excepcion():
    n = {"k": 0}

    def post(body):
        n["k"] += 1
        return _msg("no hay json") if n["k"] == 1 else _msg({"afirmaciones": []})
    r = nv.verificar_caps([_cap(1, ["Uno."])], ARCHIVO, DISPUTAS, post=post)
    assert n["k"] == 2 and r["por_cap"]["ch01"]["intentos"] == 2 and r["por_cap"]["ch01"]["error"] is None
    m = {"k": 0}

    def post2(body):
        m["k"] += 1
        if m["k"] == 1:
            raise TimeoutError("api")
        return _msg({"afirmaciones": []})
    r2 = nv.verificar_caps([_cap(1, ["Uno."])], ARCHIVO, DISPUTAS, post=post2)
    assert m["k"] == 2 and r2["por_cap"]["ch01"]["error"] is None


def test_a5_un_cap_que_falla_dos_veces_no_frena_y_los_demas_siguen():
    def post(body):
        if json.loads(body["messages"][0]["content"].split("\n\nFormato")[0])["cap"] == "ch02":
            raise TimeoutError("api caída")
        return _msg({"afirmaciones": [{"oracion": 0, "afirmacion": "x", "estado": "contradice", "ids": [], "fragmento": "y"}]})
    r = nv.verificar_caps([_cap(1, ["Uno."]), _cap(2, ["Dos."])], ARCHIVO, DISPUTAS, post=post)
    assert "TimeoutError" in r["por_cap"]["ch02"]["error"] and r["por_cap"]["ch02"]["afirmaciones"] == []
    assert r["por_cap"]["ch02"]["intentos"] == 2 and [x["cap"] for x in r["contradice"]] == ["ch01"]


def test_a6_los_siete_caps_van_en_paralelo():
    barrera = threading.Barrier(7, timeout=20)                 # solo pasa si las 7 llamadas están a la vez adentro

    def post(body):
        barrera.wait()
        return _msg({"afirmaciones": []})
    t0 = time.time()
    r = nv.verificar_caps([_cap(n, ["Uno."]) for n in range(1, 8)], ARCHIVO, DISPUTAS, post=post)
    assert sorted(r["por_cap"]) == [f"ch{n:02d}" for n in range(1, 8)] and time.time() - t0 < 20
    assert all(v["error"] is None for v in r["por_cap"].values())


def test_a7_sin_caps_no_llama():
    def post(body):
        raise AssertionError("no debe llamar")
    assert nv.verificar_caps([], ARCHIVO, DISPUTAS, post=post)["usd"] == 0.0


# ═══════════════════════ Etapa B: edit_sentences y particionar ═══════════════════════

PARRAFO = {"cap": 4, "beat": 10, "texto": "Nadie miraba. En ese pueblo murió alguien. El polvo seguía."}
PROB = {"codigo": "v", "frase": "En ese pueblo murió alguien.", "ids": ["Q16"],
        "motivo": "el archivo dice otra cosa (Q16): «murieron varias personas»"}


def _edita(nuevo: str, **kw) -> tuple[str, str]:
    return g4.edit_sentences(PARRAFO, [PROB], call=lambda pr, **k: {"texto": nuevo}, **kw)


def test_b1_sin_parametros_la_guardia_es_la_de_hoy(monkeypatch):
    from script_engine import m05_narrative as m5
    from script_engine.m01c_editor import lexical_guard
    monkeypatch.setattr(m5, "adjectives", lambda t: ["terrible"] if "terrible" in t else [])
    casos = ["Nadie miraba. En 1999 en ese pueblo murieron varios. El polvo seguía.",
             "Nadie miraba. En ese pueblo terrible murieron varios. El polvo seguía.",
             "Nadie miraba. En ese pueblo Kuleshov murió. El polvo seguía.",
             "Nadie miraba. Dijo «algo que nadie dijo». El polvo seguía."]
    for nuevo in casos:
        lg = lexical_guard(PARRAFO["texto"], nuevo)
        assert lg, nuevo
        assert _edita(nuevo) == (PARRAFO["texto"], "guardia léxica: " + "; ".join(lg))
    ok = "Nadie miraba. En ese pueblo murieron varios. El polvo seguía."
    assert _edita(ok) == (ok, "")
    assert _edita(PARRAFO["texto"]) == (PARRAFO["texto"], "sin cambio")
    assert _edita("Otra cosa. En ese pueblo murieron varios.")[1] == "tocó otras frases del párrafo"
    pedidos: list[str] = []
    g4.edit_sentences(PARRAFO, [PROB], call=lambda pr, **k: pedidos.append(pr) or {"texto": ok})
    assert "Sacá esas frases o corregilas para que el\nproblema desaparezca" in pedidos[0]
    assert "«En ese pueblo murió alguien.» → el archivo dice otra cosa (Q16): «murieron varias personas»" in pedidos[0]
    assert g4.PEDIDO_E not in pedidos[0]


def test_b2_guard_sin_adjetivos_y_cifras_ok_de_los_datos(monkeypatch):
    from script_engine import m05_narrative as m5
    monkeypatch.setattr(m5, "adjectives", lambda t: ["varios"] if "varios" in t else [])
    conAdj = "Nadie miraba. En ese pueblo murieron varios. El polvo seguía."
    assert _edita(conAdj)[1].startswith("guardia léxica: adjetivos nuevos")     # la de hoy lo rechaza
    assert _edita(conAdj, guard=g4.REGEN_GUARD) == (conAdj, "")                 # F66: sin adjetivos pasa
    con2022 = "Nadie miraba. En 2022 en ese pueblo murió alguien. El polvo seguía."
    assert "cifras nuevas" in _edita(con2022, guard=g4.REGEN_GUARD)[1]
    assert _edita(con2022, guard=g4.REGEN_GUARD, cifras_ok="un fin a un período oscuro 2022") == (con2022, "")
    # otra cifra sigue cayendo y los nombres del texto de los datos NO se aceptan por cifras_ok
    assert "cifras nuevas ['1999']" in _edita("Nadie miraba. En 1999 murió alguien. El polvo seguía.", guard=g4.REGEN_GUARD,
                                              cifras_ok="2022")[1]
    assert "nombres nuevos" in _edita("Nadie miraba. Murió alguien en Roldán. El polvo seguía.", guard=g4.REGEN_GUARD,
                                      cifras_ok="Roldán 2022")[1]


def _esc() -> dict:
    beats = [{"n": n, "cap": n, "funcion": "gancho" if n == 1 else "pico" if n == 3 else "escalada", "dato_central": f"D{n}",
              "datos_apoyo": [], "imagen_sensorial": f"imagen {n}", "cierre": "", "emocion": "miedo", "intensidad": 3}
             for n in range(1, 8)]
    caps = [{"chapter_number": n, "role": "hook" if n == 1 else "reveal_outro" if n == 7 else "development",
             "render_engine": "flux", "duration_seconds": 100, "narrative_intent": "setup", "evidence_ids": [f"D{n}"],
             "cliffhanger": "", "pantalla_ids": []} for n in range(1, 8)]
    return {"beats": beats, "caps": caps, "pico": {"beat": 3}, "humano": {"id": "P01"}, "antagonista": {"id": "P02"},
            "a_pantalla": [], "_pool_plan": {"pantalla": {}}, "prompt_version": "x"}


POOL = {"datos": [{"id": f"D{k}", "texto": f"dato numero {k}", "fuente": "F", "fecha": "2022" if k == 2 else None,
                   "cita_literal": f"fuente {k}"} for k in range(1, 9)], "cronologia": [], "citas": [], "lugares": [],
        "personajes": [{"id": "P01", "nombre": "Ana Roldan", "rol": "vecina"}, {"id": "P02", "nombre": "Juan Paiva", "rol": "dueño"}]}
ORACION = "El pie va a cerrar."
TITULOS = [f"Titulo {n}" for n in range(1, 8)]


def _parrafos() -> list[dict]:
    return [{"cap": n, "beat": n, "texto": f"{ORACION if n == 2 else 'La casa estaba a oscuras.'} El valle del cap {n} dormía.",
             "ids_usados": []} for n in range(1, 8)]


@pytest.fixture
def env(tmp_path, monkeypatch):
    monkeypatch.setattr(f15, "STEPS_DIR", tmp_path)
    monkeypatch.setattr(md, "STEPS_DIR", tmp_path)
    monkeypatch.setattr(mp, "seg_por_palabra", lambda *a, **k: {"valor": 1.0, "oraciones": 10, "caps": 2, "voz": "x"})
    esc = _esc()
    d = tmp_path / "t"
    d.mkdir()
    (d / "01a_escaleta.json").write_text(json.dumps(esc, ensure_ascii=False), encoding="utf-8")
    topic = {"id": "t", "evidence_pool": POOL}
    md.particionar(topic, esc, _parrafos(), POOL, title_list=TITULOS)
    (d / "01b_guionista_v4.json").write_text(json.dumps({"reparacion": {"parrafos": _parrafos()}}), encoding="utf-8")
    return {"d": d, "esc": esc, "topic": topic}


def _post_verif(contradice: dict[str, list[dict]], pedidos: list[str] | None = None, despues: dict | None = None):
    """El verificador falso: la primera vez que ve un cap devuelve `contradice[cap]`; la segunda, `despues[cap]`."""
    vistos: dict[str, int] = {}
    lock = threading.Lock()

    def post(body):
        cap = json.loads(body["messages"][0]["content"].split("\n\nFormato de salida: ")[0])["cap"]
        with lock:
            vistos[cap] = vistos.get(cap, 0) + 1
            if pedidos is not None:
                pedidos.append(cap)
            k = vistos[cap]
        fuente = contradice if k == 1 else (despues or {})
        return _msg({"cap": cap, "afirmaciones": fuente.get(cap) or []})
    return post


AFIRMA = {"oracion": 0, "afirmacion": "la herida va a cerrar", "estado": "contradice", "ids": ["D2"], "fragmento": "no cerraba nunca"}


def _corre(env, post, call, log=None):
    log = log if log is not None else []
    return f15.run_verificacion("t", _parrafos(), env["topic"], env["esc"], POOL, call=call, log=log, post=post)


def test_b3_particionar_sin_title_list_igual_y_con_title_list_no_llama(tmp_path, monkeypatch):
    monkeypatch.setattr(md, "STEPS_DIR", tmp_path)
    esc = _esc()
    llamadas = []
    r = md.particionar({"id": "a"}, esc, _parrafos(), POOL, call_titles=lambda p, **k: llamadas.append(p) or {"titulos": []})
    assert llamadas and r["skeleton"]["_v3"]["particion"]["titulos"] == "respaldo"

    def no_llamar(p, **k):
        raise AssertionError("no debe pedir títulos")
    r2 = md.particionar({"id": "b"}, esc, _parrafos(), POOL, call_titles=no_llamar, title_list=TITULOS)
    assert [c["title"] for c in r2["skeleton"]["chapters"]] == TITULOS
    assert r2["skeleton"]["_v3"]["particion"]["titulos"] == "los de la partición anterior"
    assert r2["narration"] == md.particionar({"id": "b"}, esc, _parrafos(), POOL, call_titles=lambda p, **k: {"titulos": []})["narration"]


def test_b4_contradice_edicion_aceptada_reparticion_y_solo_el_cap_cambiado(env, monkeypatch):
    def no_llamar(*a, **k):
        raise AssertionError("no se piden títulos ni se acorta")
    monkeypatch.setattr(md, "titles", no_llamar)
    monkeypatch.setattr(md, "editor_shorten", no_llamar)
    pedidos: list[str] = []
    n3_antes = (env["d"] / "01b_narracion_v3.json").read_bytes()

    def call(pr, **k):
        assert "«El pie va a cerrar.» → el archivo dice otra cosa (D2): «no cerraba nunca»" in pr
        return {"texto": "El pie no cerraba. El valle del cap 2 dormía."}
    r = _corre(env, _post_verif({"ch02": [AFIRMA]}, pedidos), call)
    assert sorted(pedidos) == sorted([f"ch{n:02d}" for n in range(1, 8)] + ["ch02"])          # 7 + solo el cap cambiado
    assert r["caps_cambiados"] == ["ch02"] and r["quedan"] == [] and r["nuevas"] == []
    f = r["filas"][0]
    assert (f["hecho"], f["despues"], f["parrafo"]) == ("corregida ✔", "El pie no cerraba.", 1)
    assert r["particion"] is not None
    n3 = json.loads((env["d"] / "01b_narracion_v3.json").read_text(encoding="utf-8"))
    assert (env["d"] / "01b_narracion_v3.json").read_bytes() != n3_antes
    assert n3["parrafos"][1]["texto"].startswith("El pie no cerraba.")
    assert "va a cerrar" not in (env["d"] / "01b_narration.json").read_text(encoding="utf-8")
    sk = json.loads((env["d"] / "01a_skeleton.json").read_text(encoding="utf-8"))
    assert [c["title"] for c in sk["chapters"]] == TITULOS
    v = json.loads((env["d"] / "01b_verificacion.json").read_text(encoding="utf-8"))
    assert v["narracion_md5_antes"] != v["narracion_md5_despues"] and v["re_verificacion"]["por_cap"].keys() == {"ch02"}
    md_txt = (env["d"] / "01b_verificacion.md").read_text(encoding="utf-8")
    assert "corregida ✔" in md_txt and "| ch02 | [0] El pie va a cerrar." in md_txt and "El pie no cerraba." in md_txt
    g = json.loads((env["d"] / "01b_guionista_v4.json").read_text(encoding="utf-8"))
    assert g["verificacion"]["parrafos"][1]["texto"].startswith("El pie no cerraba.")
    assert g["reparacion"]["parrafos"][1]["texto"].startswith(ORACION)                       # lo de la reparación no se toca
    assert nv.leer_quedan(env["d"]) == []


def test_b5_el_parrafo_se_ubica_por_texto_y_el_beat_desempata():
    ps = [{"cap": 2, "beat": 2, "texto": "Uno. La frase."}, {"cap": 2, "beat": 3, "texto": "Dos. La frase."},
          {"cap": 3, "beat": 4, "texto": "Tres."}]
    assert f15._parrafo_de({"cap": "ch02", "texto": "La frase.", "beat": 3}, ps) == 1
    assert f15._parrafo_de({"cap": "ch02", "texto": "La frase.", "beat": 9}, ps) == 0
    assert f15._parrafo_de({"cap": "ch02", "texto": "Tres.", "beat": 4}, ps) is None        # otro cap
    assert f15._parrafo_de({"cap": "ch02", "texto": None, "beat": 2}, ps) is None


def test_b6_la_guardia_rechaza_queda_como_aviso_y_la_cadena_sigue(env, capsys):
    pedidos: list[str] = []
    r = _corre(env, _post_verif({"ch02": [AFIRMA]}, pedidos), lambda pr, **k: {"texto": "En 1999 no cerraba. El valle del cap 2 dormía."})
    assert len(pedidos) == 7 and r["particion"] is None and r["caps_cambiados"] == [] and r["re_verificacion"] is None
    assert "rechazada: guardia léxica: cifras nuevas ['1999'] ⚠" == r["filas"][0]["hecho"]
    assert len(r["quedan"]) == 1 and r["quedan"][0]["ids"] == ["D2"] and r["quedan"][0]["texto"] == ORACION
    assert r["narracion_md5_antes"] == r["narracion_md5_despues"]
    assert "⚠ la narración sigue contradiciendo el archivo en 1 punto(s)" in capsys.readouterr().out
    assert nv.leer_quedan(env["d"])[0]["cap"] == "ch02"
    assert "⚠ la narración sigue contradiciendo" in f15.parada_del_papel("t")


def test_b7_la_cifra_de_la_fecha_del_dato_se_acepta(env):
    r = _corre(env, _post_verif({"ch02": [AFIRMA]}), lambda pr, **k: {"texto": "En 2022 no cerraba. El valle del cap 2 dormía."})
    assert r["filas"][0]["hecho"] == "corregida ✔"                                             # D2 trae fecha 2022


def test_b8_error_de_la_edicion_es_aviso(env):
    def call(pr, **k):
        raise TimeoutError("api")
    r = _corre(env, _post_verif({"ch02": [AFIRMA]}), call)
    assert "TimeoutError" in r["filas"][0]["hecho"] and len(r["quedan"]) == 1


def test_b9_sigue_contradiciendo_y_nueva_quedan_como_aviso(env):
    segunda = {"ch02": [{**AFIRMA, "oracion": 0, "afirmacion": "todavía"},
                        {"oracion": 1, "afirmacion": "otra cosa", "estado": "contradice", "ids": ["D3"], "fragmento": "x"}]}
    r = _corre(env, _post_verif({"ch02": [AFIRMA]}, despues=segunda), lambda pr, **k: {"texto": "El pie no cerraba. El valle del cap 2 dormía."})
    assert r["filas"][0]["hecho"] == "sigue contradiciendo ⚠"
    assert [x["afirmacion"] for x in r["quedan"]] == ["todavía", "otra cosa"] and [x["ids"] for x in r["nuevas"]] == [["D3"]]
    assert "nueva en la re-verificación ⚠" in (env["d"] / "01b_verificacion.md").read_text(encoding="utf-8")


def test_b10_sin_contradice_no_edita_ni_reparte(env):
    def call(pr, **k):
        raise AssertionError("no hay nada que editar")
    pedidos: list[str] = []
    r = _corre(env, _post_verif({}, pedidos), call)
    assert len(pedidos) == 7 and r["particion"] is None and r["filas"] == [] and r["quedan"] == []
    assert "nada que corregir" in (env["d"] / "01b_verificacion.md").read_text(encoding="utf-8")


def test_b11_un_cap_sin_verificar_se_avisa_en_el_md(env):
    def post(body):
        raise TimeoutError("api caída")
    r = _corre(env, post, lambda pr, **k: {"texto": ""})
    assert r["filas"] == [] and all(v["error"] for v in r["primera"]["por_cap"].values())
    assert "⚠ caps sin verificar" in (env["d"] / "01b_verificacion.md").read_text(encoding="utf-8")


def _msg_papel(resp: dict) -> dict:
    return _msg(resp, {"input_tokens": 1000, "output_tokens": 200})


def test_b12_el_aviso_va_al_final_del_papel_y_a_la_parada(env):
    (env["d"] / "01b_verificacion.json").write_text(json.dumps({"quedan": [
        {"cap": "ch02", "oracion": 0, "texto": ORACION, "afirmacion": "va a cerrar", "ids": ["D2"], "fragmento": "no cerraba"}]},
        ensure_ascii=False), encoding="utf-8")
    p = mp.generar("t", env["d"].parent, pool=POOL, vocabulario=["CALMA"], post=lambda b: _msg_papel({"beats": []}))
    assert p["aviso_narracion"][0]["ids"] == ["D2"]
    md_txt = (env["d"] / "01e_pantalla.md").read_text(encoding="utf-8")
    assert md_txt.rindex("## ⚠ Aviso de la verificación de la narración") > md_txt.rindex("## Descartados por el modelo")
    assert "«El pie va a cerrar.»" in md_txt
    assert "⚠ la narración sigue contradiciendo el archivo en 1 punto(s)" in f15.parada_del_papel("t")
    (env["d"] / "01b_verificacion.json").write_text(json.dumps({"quedan": []}), encoding="utf-8")
    (env["d"] / "01e_pantalla.raw.json").unlink()
    p2 = mp.generar("t", env["d"].parent, pool=POOL, vocabulario=["CALMA"], post=lambda b: _msg_papel({"beats": []}))
    assert "aviso_narracion" not in p2 and "⚠ la narración" not in f15.parada_del_papel("t")


def test_b13_prompts_del_papel_no_cambian():
    assert mp.prompt_md5() == "f2bfdf2044a4c77a59fc62ebe93966c2" and mp.PROMPT_VERSION == "m01e-7"
    assert hashlib.md5(mp.PANTALLA_SYSTEM.encode("utf-8")).hexdigest() == "85d094bed6090b14d1802ca97433d982"


def test_b14_verificar_narracion_no_llama_al_guionista(env, monkeypatch, capsys):
    def explota(*a, **k):
        raise AssertionError("no se vuelve a llamar al guionista")
    monkeypatch.setattr(g4, "write", explota)
    monkeypatch.setattr(g4, "reparar", explota)
    monkeypatch.setattr(f15, "_topic_v3", lambda tid: env["topic"])
    monkeypatch.setattr(g4, "call_for", lambda m: (lambda pr, **k: {"texto": "El pie no cerraba. El valle del cap 2 dormía."}))
    monkeypatch.setattr(f15, "_step_cost", lambda tid, label, fn: pasos.append(label) or fn())
    pasos: list[str] = []
    orden: list[str] = []
    real = f15.run_verificacion
    monkeypatch.setattr(f15, "run_verificacion", lambda *a, **k: orden.append("verificacion") or real(*a, post=_post_verif({"ch02": [AFIRMA]}), **k))
    monkeypatch.setattr(f15, "run_pantalla", lambda tid, pool, log: orden.append("pantalla") or {})
    assert f15.verificar_narracion("t") == 0
    assert orden == ["verificacion", "pantalla"] and pasos == ["verificacion"]
    out = capsys.readouterr().out
    assert "PARADA del papel" in out and "Aprobar:" in out
    n3 = json.loads((env["d"] / "01b_narracion_v3.json").read_text(encoding="utf-8"))
    assert n3["parrafos"][1]["texto"].startswith("El pie no cerraba.")


def test_b15_verificar_narracion_sin_guion_para(env):
    (env["d"] / "01b_guionista_v4.json").unlink()
    with pytest.raises(f15.Parada, match="no hay guion"):
        f15.verificar_narracion("t")


def test_b16_orden_de_run_guion_v4_y_el_juez_recibe_la_particion_final(env, monkeypatch):
    from script_engine import m05_narrative as m5
    orden: list[str] = []
    monkeypatch.setattr(f15, "_topic_v3", lambda tid: env["topic"])
    monkeypatch.setattr(f15, "_load_step_output", lambda tid, name: env["esc"])
    monkeypatch.setattr(f15, "_step_cost", lambda tid, label, fn: fn())
    monkeypatch.setattr(g4, "call_for", lambda m: (lambda pr, **k: {}))
    monkeypatch.setattr(g4, "write", lambda *a, **k: orden.append("guionista") or {"parrafos": _parrafos()})
    monkeypatch.setattr(g4, "reparar", lambda *a, **k: orden.append("reparar") or {"parrafos": _parrafos(), "parada": False, "bloqueantes_despues": []})
    monkeypatch.setattr(g4, "metricas", lambda *a, **k: {})
    monkeypatch.setattr(g4, "nota_b", lambda: "")
    monkeypatch.setattr(md, "particionar", lambda *a, **k: orden.append("particionar") or {"narration": "vieja", "skeleton": "sk"})
    monkeypatch.setattr(f15, "run_verificacion", lambda *a, **k: orden.append("verificacion") or {"particion": {"narration": "final", "skeleton": "sk2"}})
    monkeypatch.setattr(f15, "run_pantalla", lambda *a, **k: orden.append("pantalla") or {})
    vio = {}
    monkeypatch.setattr(m5, "judge_narration", lambda tid, **k: orden.append("juez") or vio.update(k) or {})
    from researcher_steps import ficha_caso
    monkeypatch.setattr(ficha_caso, "load", lambda *a, **k: None)
    r = f15.run_guion_v4("t")
    assert orden == ["guionista", "reparar", "particionar", "verificacion", "pantalla", "juez"]
    assert vio["narration"] == "final" and r["particion"]["narration"] == "final"
    # sin correcciones: la partición de antes
    orden.clear()
    monkeypatch.setattr(f15, "run_verificacion", lambda *a, **k: {"particion": None})
    assert f15.run_guion_v4("t")["particion"]["narration"] == "vieja"
