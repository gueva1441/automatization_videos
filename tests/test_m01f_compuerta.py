# -*- coding: utf-8 -*-
"""F67 B y C: el crítico de narración (m01f) y la compuerta NARRACIÓN. Sin API: `claude_helpers._post` explota; todo va con post falso."""
import hashlib
import json
import re
import shutil
from pathlib import Path

import pytest

import fase1_5 as f15
from script_engine import m01d_particion as md
from script_engine import m01e_pantalla as mp
from script_engine import m01f_critico as mf

ROOT = Path(__file__).resolve().parent.parent
TID = "t"
PERSONA = {"id": "P01", "nombre": "Ana Roldan", "rol": "vecina"}
POOL = {"datos": [{"id": f"D{k}", "texto": f"dato numero {k}", "fuente": "F", "cita_literal": f"fuente {k}", "fecha": "1949" if k == 2 else ""}
                  for k in range(1, 9)], "cronologia": [], "citas": [], "lugares": [],
        "personajes": [PERSONA, {"id": "P02", "nombre": "Juan Paiva", "rol": "dueño"}]}


def _esc() -> dict:
    beats = [{"n": n, "cap": n, "funcion": "gancho" if n == 1 else "pico" if n == 3 else "escalada", "dato_central": f"D{n}", "datos_apoyo": [],
              "imagen_sensorial": f"imagen {n}", "cierre": "", "emocion": "miedo", "intensidad": 3, "humano_en_escena": n % 2 == 1}
             for n in range(1, 8)]
    caps = [{"chapter_number": n, "role": "hook" if n == 1 else "reveal_outro" if n == 7 else "development", "render_engine": "flux",
             "duration_seconds": 100, "narrative_intent": "setup", "evidence_ids": [f"D{n}"], "cliffhanger": "", "pantalla_ids": []}
            for n in range(1, 8)]
    return {"beats": beats, "caps": caps, "pico": {"beat": 3}, "humano": {"id": "P01"}, "antagonista": {"id": "P02"}, "a_pantalla": [],
            "_pool_plan": {"pantalla": {}}, "prompt_version": "x", "promesa_gancho": "Murieron 40.", "loops": [], "recuerda_loop": None,
            "cierre_humano": None}


def _parrafos() -> list[dict]:
    return [{"cap": n, "beat": n, "texto": f"Ana Roldan llegó al cap {n}. La casa estaba a oscuras.", "ids_usados": [f"D{n}"]}
            for n in range(1, 8)] + [{"cap": 2, "beat": 2, "texto": "El valle dormía. Nadie hablaba.", "ids_usados": ["D8"]}]


@pytest.fixture(autouse=True)
def _sin_api(monkeypatch):
    import claude_helpers as hx

    def explota(body):
        raise AssertionError(f"llamada real al modelo en un test: {body.get('model')}")
    monkeypatch.setattr(hx, "_post", explota)


@pytest.fixture
def env(tmp_path, monkeypatch):
    monkeypatch.setattr(f15, "STEPS_DIR", tmp_path)
    monkeypatch.setattr(md, "STEPS_DIR", tmp_path)
    monkeypatch.setattr(mp, "seg_por_palabra", lambda *a, **k: {"valor": 0.5, "oraciones": 10, "caps": 2, "voz": "x"})
    monkeypatch.setattr(f15, "_topic_v3", lambda tid: {"id": tid, "evidence_pool": POOL})
    esc = _esc()
    d = tmp_path / TID
    d.mkdir()
    (d / "01a_escaleta.json").write_text(json.dumps(esc, ensure_ascii=False), encoding="utf-8")
    md.particionar({"id": TID}, esc, sorted(_parrafos(), key=lambda p: p["cap"]), POOL, call_titles=lambda p, **k: {"titulos": []})
    (d / "01b_verificacion.md").write_text("# V\n\n| cap | oración | afirmación | ids | fragmento |\n|---|---|---|---|---|\n| ch01 | x | y | D1 | z |\n\n## Sin\n", encoding="utf-8")
    return {"d": d, "sd": tmp_path, "esc": esc}


def _msg(txt: str) -> dict:
    return {"content": [{"type": "text", "text": txt}], "usage": {"input_tokens": 100, "output_tokens": 10}, "stop_reason": "end_turn"}


def _deb(cap="ch02", oraciones=(1, 2), texto="Un texto nuevo de 1949.", ids=("D2",)) -> dict:
    return {"cap": cap, "oraciones": list(oraciones), "que_sale": "s", "por_que_se_van": "p", "deberia_texto": texto, "ids": list(ids)}


def _resp(*deberia) -> dict:
    return {"nota_total": 6.5, "resumen": ["r"], "gancho": {"promesa_cumplida": True, "comentario": "c"},
            "caps": [{"cap": f"ch{n:02d}", "nota": 7, "personaje_en_voz": True, "oraciones_seguidas_sin_personaje": 1, "fuerte": "f", "debil": "d",
                      "reengancho": "e"} for n in range(1, 8)], "loops": [{"pregunta": "p", "abre": "ch01:0", "paga": None, "se_recuerda": True}],
            "pico": {"cap": "ch03", "pct_acumulado": 50, "segundos_despues": 10, "comentario": "c"}, "cierre": "c", "deberia": list(deberia),
            "reglas_generales_candidatas": [{"regla": "r", "medible_como": "m", "por_que": "p"}], "riesgos": ["no tocar"]}


def _generar(env, *deberia, post=None):
    return mf.generar(TID, env["sd"], pool=POOL, post=post or (lambda b: _msg(json.dumps(_resp(*deberia), ensure_ascii=False))))


# ═══════════════════════ B: prompts ═══════════════════════

def _bloque(t: str, titulo: str) -> str:
    i = t.index("```\n", t.index(titulo)) + 4
    return t[i:t.index("\n```", i)]


def test_prompts_byte_a_byte_del_lab():
    h = (ROOT / "lab/hyperframes/f67/HANDOFF_F67a_critico_por_api.md").read_bytes().decode("utf-8").replace("\r\n", "\n")
    assert hashlib.md5(mf.SYSTEM.encode("utf-8")).hexdigest() == json.loads((ROOT / "lab/hyperframes/f67/a/md5.json").read_text())["system"]
    assert mf.SYSTEM == _bloque(h, "## 4. SYSTEM") and mf.FORMATO == _bloque(h, "## 5. FORMATO_SALIDA")
    assert mf.PROMPT_VERSION == "m01f-1" and (mf.MODELO, mf.EFFORT) == ("claude-opus-5-5", "medium")


def test_produccion_no_importa_el_lab():
    src = (ROOT / "script_engine/m01f_critico.py").read_text(encoding="utf-8")
    assert not re.search(r"^\s*(from|import)\s+.*(etapa_a_critico|lab\.)", src, re.M)


# ═══════════════════════ B: entrada ═══════════════════════

def test_entrada_mismo_payload_del_lab_con_metricas_del_juez(env):
    from script_engine.m05_narrative import judge_narration
    rep = judge_narration(TID, steps_dir=env["sd"], pool=POOL)
    ent = mf.entrada(TID, env["sd"], pool=POOL)
    assert ent["metricas"] == rep["retencion"]
    assert ent["verificacion"].startswith("| cap | oración") and "## Sin" not in ent["verificacion"]
    u = mf.armar_user(ent["e"], ent["metricas"], ent["verificacion"], mf.FORMATO)
    p = json.loads(u.split("\n\nFormato de salida (devolvé solo este JSON):\n")[0])
    assert u.endswith(mf.FORMATO) and list(p) == ["caps", "beats", "escaleta_video", "archivo", "disputas", "metricas", "verificacion"]
    assert "caben" not in json.dumps(p["caps"]) and "clima" not in p
    assert all("flash_forward" not in b for b in p["beats"])
    assert [b["humano_en_escena"] for b in p["beats"]] == [b["humano_en_escena"] for b in env["esc"]["beats"]]


def test_entrada_corre_el_juez_si_no_hay_retencion(env):
    assert not (env["d"] / "06_judge_narrative.json").exists()
    assert mf.entrada(TID, env["sd"], pool=POOL)["metricas"]["total_palabras"] > 0
    assert (env["d"] / "06_judge_narrative.json").exists()


def test_entrada_sin_humano_en_escena_aborta_con_el_nombre(env):
    esc = _esc()
    del esc["beats"][0]["humano_en_escena"]
    (env["d"] / "01a_escaleta.json").write_text(json.dumps(esc), encoding="utf-8")
    with pytest.raises(ValueError, match=r"entrada\.beats\[\*\]\.humano_en_escena"):
        mf.entrada(TID, env["sd"], pool=POOL)


# ═══════════════════════ B: llamada, validación, archivos ═══════════════════════

def test_generar_escribe_json_y_md(env):
    vistos = []

    def post(body):
        vistos.append(body)
        return _msg("```json\n" + json.dumps(_resp(_deb()), ensure_ascii=False) + "\n```")
    r = _generar(env, post=post)
    assert len(vistos) == 1 and vistos[0]["system"] == mf.SYSTEM and vistos[0]["output_config"] == {"effort": "medium"}
    assert vistos[0]["model"] == "claude-opus-5-5"
    j = json.loads((env["d"] / "01f_critico.json").read_text(encoding="utf-8"))
    for k in ("prompt_version", "modelo", "effort", "system_md5", "user_md5", "narracion_md5", "usd", "segundos", "respuesta", "validacion", "n_deberia"):
        assert k in j, k
    assert j["n_deberia"] == 1 and j["respuesta"]["nota_total"] == 6.5 == r["respuesta"]["nota_total"]
    n3 = json.loads((env["d"] / "01b_narracion_v3.json").read_text(encoding="utf-8"))
    assert j["narracion_md5"] == md.md5_narracion(n3)
    t = (env["d"] / "01f_critico.md").read_text(encoding="utf-8")
    assert "**Nota total:** 6.5" in t and "Personaje según la escaleta: P01 Ana Roldan" in t and "### 1. ch02" in t and "## Riesgos" in t


def test_sin_json_reintenta_una_vez_y_no_aborta(env):
    n = {"k": 0}

    def post(body):
        n["k"] += 1
        return _msg("esto no es json")
    r = _generar(env, post=post)
    assert n["k"] == 2 and r["respuesta"] is None and r["error"] and r["crudo"] == "esto no es json" and r["n_deberia"] == 0
    assert "sin JSON válido" in (env["d"] / "01f_critico.md").read_text(encoding="utf-8")
    assert "sin crítica" in f15.parada_de_narracion(TID)


def test_reintento_tras_sin_json_vale(env):
    rs = [_msg("nada"), _msg(json.dumps(_resp()))]
    assert _generar(env, post=lambda b: rs.pop(0))["respuesta"]["nota_total"] == 6.5 and not rs


def test_error_de_api_tambien_reintenta(env):
    def post(b):
        raise TimeoutError("caída")
    r = _generar(env, post=post)
    assert r["respuesta"] is None and r["intentos"] == 2 and "TimeoutError" in r["error"]


def test_validacion_ids_oraciones_cifras_marcas(env):
    d1 = _deb(oraciones=(1, 2, 99), texto="[idx1] En 7777 y en 1949 pasó. […] Fin.", ids=("D2", "NOPE"))
    d2 = _deb(cap="ch01", oraciones=(0,), texto="Nada.", ids=("D1",))
    r = _generar(env, d1, d2)
    v = r["validacion"]
    assert v["ids_invalidos"] == ["NOPE"] and v["oraciones_invalidas"] == ["ch02:99"]
    f1, f2 = v["deberia"]
    assert (f1["k"], f2["k"]) == (1, 2)
    assert f1["cifras_sin_respaldo"] == ["7777"]                 # 1949 viene de la `fecha` de D2; las marcas no cuentan
    assert f1["marcas"] == ["[idx1]", "[…]"] and f1["palabras_despues"] == len("En 7777 y en 1949 pasó. Fin.".split())
    assert f1["texto_original"] == ["La casa estaba a oscuras.", "El valle dormía."] and f1["ids_invalidos"] == ["NOPE"]
    assert f1["palabras_antes"] == 8 and f1["idx"] == [1, 2, 99]


def test_deberia_no_se_truncan(env):
    assert _generar(env, *[_deb() for _ in range(11)])["n_deberia"] == 11


def test_limpiar():
    assert mf.limpiar("[idx1] Hola  [x] mundo. […]") == "Hola mundo."


# ═══════════════════════ C.1: estado / aprobar / invalidar ═══════════════════════

def _n3(env) -> dict:
    return json.loads((env["d"] / "01b_narracion_v3.json").read_text(encoding="utf-8"))


def test_estado_aprobar_invalidar(env):
    ok, m = f15.estado_narracion(TID)
    assert not ok and m == "la narración no está aprobada"
    md5 = md.md5_narracion(_n3(env))
    ap = f15.aprobar_narracion(TID, "Omar 2026-10-31")
    assert ap == {"por": "Omar", "fecha": "2026-10-31", "md5": md5} and _n3(env)["aprobado"] == ap
    assert md.md5_narracion(_n3(env)) == md5                         # aprobar no cambia el md5
    ok, m = f15.estado_narracion(TID)
    assert ok and "aprobada por Omar (2026-10-31)" in m
    n = _n3(env)
    n["parrafos"][0]["texto"] = "Otro texto."
    (env["d"] / "01b_narracion_v3.json").write_text(json.dumps(n, ensure_ascii=False), encoding="utf-8")
    ok, m = f15.estado_narracion(TID)
    assert not ok and "cambió después de la aprobación de Omar" in m


def test_sin_narracion_no_hay_nada_que_aprobar(env):
    (env["d"] / "01b_narracion_v3.json").unlink()
    assert "no hay narración" in f15.estado_narracion(TID)[1]
    with pytest.raises(f15.Parada, match="no hay narración"):
        f15.aprobar_narracion(TID, "Omar")


def test_steps_dir_no_toca_el_topic_real(env, tmp_path):
    otra = tmp_path / "copia" / TID
    otra.parent.mkdir()
    shutil.copytree(env["d"], otra)
    antes = (env["d"] / "01b_narracion_v3.json").read_bytes()
    f15.aprobar_narracion(TID, "Omar 2026-10-31", otra.parent)
    assert f15.estado_narracion(TID, otra.parent)[0] and not f15.estado_narracion(TID)[0]
    assert (env["d"] / "01b_narracion_v3.json").read_bytes() == antes


def test_papel_falta(env):
    assert f15.papel_falta(TID) == "no hay papel"
    f15.aprobar_narracion(TID, "Omar 2026-10-31")
    md5 = _n3(env)["aprobado"]["md5"]
    f = env["d"] / "01e_pantalla.json"
    f.write_text(json.dumps({"narracion_md5": md5}), encoding="utf-8")
    assert f15.papel_falta(TID) is None
    f.write_text(json.dumps({"narracion_md5": "otro"}), encoding="utf-8")
    assert "otra narración" in f15.papel_falta(TID)
    f.write_text(json.dumps({"beats": []}), encoding="utf-8")
    assert "no dice" in f15.papel_falta(TID)                          # sin el campo y sin aprobar: se re-corre
    f.write_text(json.dumps({"aprobado": {"md5": "x"}}), encoding="utf-8")
    assert f15.papel_falta(TID) is None                               # uno aprobado sin el campo se respeta


def test_run_papel_aprobado_chequea_adentro_y_corre_una_vez(env, monkeypatch, capsys):
    corridas = []

    def falso(tid, pool, log):
        corridas.append(tid)
        (env["d"] / "01e_pantalla.json").write_text(json.dumps({"narracion_md5": _n3(env)["aprobado"]["md5"], "beats": []}), encoding="utf-8")
    monkeypatch.setattr(f15, "run_pantalla", falso)
    assert f15.run_papel_aprobado(TID) == 0 and corridas == []        # sin aprobar: no corre
    assert "PARADA de narración" in capsys.readouterr().out
    f15.aprobar_narracion(TID, "Omar 2026-10-31")
    assert f15.run_papel_aprobado(TID) == 0 and corridas == [TID]
    assert "PARADA del papel" in capsys.readouterr().out
    assert f15.run_papel_aprobado(TID) == 0 and corridas == [TID]     # vigente: no se re-paga


def test_el_papel_dice_de_que_narracion_salio(env):
    p = mp.generar(TID, env["sd"], pool=POOL, vocabulario=["CALMA"], post=lambda b: _msg(json.dumps({"beats": []})))
    assert p["narracion_md5"] == md.md5_narracion(_n3(env))


def test_process_topic_para_en_narracion_antes_del_papel_y_al_reanudar(env, monkeypatch, capsys):
    monkeypatch.setattr(f15, "_load_topic_by_id", lambda tid: {"id": tid, "evidence_pool": {"datos": [], "_research_v3": True}})
    guion = []
    monkeypatch.setattr(f15, "run_guion_v4", lambda *a, **k: guion.append(1))
    for desde in ("normalizer_gate", "audio", "m03"):
        r = f15.process_topic(TID, from_step=desde, gate_interactive=False, music_gate_interactive=False)
        assert r["status"] == "PARADA" and r["parada"] == "narracion"
    assert guion == []                                                # al retomar no se vuelve a pagar el guion
    f15.aprobar_narracion(TID, "Omar 2026-10-31")
    r = f15.process_topic(TID, from_step="audio", gate_interactive=False, music_gate_interactive=False)
    assert r["parada"] == "papel" and guion == []


# ═══════════════════════ C.2: reconstruir, editar, aceptar ═══════════════════════

ARCHIVOS = ("01a_skeleton.json", "01b_narration.json", "01b_narracion_v3.json")


def _bytes(env) -> dict:
    return {n: (env["d"] / n).read_bytes() for n in ARCHIVOS}


def test_reconstruir_sin_cambios_es_identico_y_no_llama_a_flash(env, monkeypatch):
    def explota(*a, **k):
        raise AssertionError("reconstruir no llama a Flash ni rebalancea")
    monkeypatch.setattr(md, "titles", explota)
    monkeypatch.setattr(md, "rebalance", explota)
    antes = _bytes(env)
    c = mf._carga(TID, env["sd"])
    (env["d"] / "01b_narration_normalized.json").write_text("{}", encoding="utf-8")
    md.reconstruir(c["topic"], c["esc"], c["parrafos"], c["pool"], c["titulos"], steps_dir=env["sd"])
    assert _bytes(env) == antes and not (env["d"] / "01b_narration_normalized.json").exists()


def test_reconstruir_cap_vacio_no_escribe(env):
    antes = _bytes(env)
    c = mf._carga(TID, env["sd"])
    with pytest.raises(md.ParticionError, match="caps sin narración"):
        md.reconstruir(c["topic"], c["esc"], [p for p in c["parrafos"] if p["cap"] != 3], c["pool"], c["titulos"], steps_dir=env["sd"])
    assert _bytes(env) == antes


def test_editar_parrafo_invalida_la_aprobacion(env):
    f15.aprobar_narracion(TID, "Omar 2026-10-31")
    assert f15.estado_narracion(TID)[0]
    r = mf.editar_parrafo(TID, 0, "Ana Roldan volvió al valle.", env["sd"])
    n = _n3(env)
    assert n["parrafos"][0]["texto"] == "Ana Roldan volvió al valle." and "aprobado" not in n and r["md5"] == md.md5_narracion(n)
    assert not f15.estado_narracion(TID)[0]
    assert "Ana Roldan volvió al valle." in (env["d"] / "01b_narration.json").read_text(encoding="utf-8")
    for malo, texto in ((99, "x"), (0, "  "), ("0", "x")):
        with pytest.raises(ValueError):
            mf.editar_parrafo(TID, malo, texto, env["sd"])


def test_aceptar_deberia_que_cruza_dos_parrafos(env):
    # ch02: [0] Ana llegó. [1] La casa… (párrafo A) · [2] El valle dormía. [3] Nadie hablaba. (párrafo B)
    _generar(env, _deb(oraciones=(1, 2), texto="[idx1] Un texto  nuevo. […]", ids=("D2", "NOPE")))
    f15.aprobar_narracion(TID, "Omar 2026-10-31")
    r = mf.aceptar_deberia(TID, 1, env["sd"])
    n = _n3(env)
    a, b = [p for p in n["parrafos"] if p["cap"] == 2]
    assert a["texto"] == "Ana Roldan llegó al cap 2. Un texto nuevo." and b["texto"] == "Nadie hablaba."
    assert "D2" in a["ids_usados"] and "NOPE" not in a["ids_usados"] and b["ids_usados"] == ["D8"]
    assert r["beats_cambiados"] == [2] and r["beats_sin_texto"] == [] and "aprobado" not in n
    assert json.loads((env["d"] / "06_judge_narrative.json").read_text(encoding="utf-8"))["retencion"]["total_palabras"] > 0


def test_aceptar_deberia_de_tres_parrafos_elimina_el_del_medio(env):
    ps = sorted(_parrafos() + [{"cap": 2, "beat": 2, "texto": "Hubo un ruido. Cayó el techo.", "ids_usados": []}], key=lambda p: p["cap"])
    md.particionar({"id": TID}, env["esc"], ps, POOL, call_titles=lambda p, **k: {"titulos": []})
    assert len([p for p in _n3(env)["parrafos"] if p["cap"] == 2]) == 3
    _generar(env, _deb(oraciones=(1, 2, 3, 4), texto="Reemplazo."))     # de la última del 1.º a la primera del 3.º
    mf.aceptar_deberia(TID, 1, env["sd"])
    q = [p["texto"] for p in _n3(env)["parrafos"] if p["cap"] == 2]
    assert q == ["Ana Roldan llegó al cap 2. Reemplazo.", "Cayó el techo."]   # el del medio se eliminó: tag_cap correría los índices


def test_los_vacios_correrian_el_pico_de_tag_cap():
    """Por qué se eliminan: tag_cap saltea los párrafos vacíos, pero `pico_par` e `intensities` son índices sobre todos los párrafos."""
    from script_engine.tts_tags import tag_cap
    con_vacio, _ = tag_cap("Uno dos.\n\n\n\nTres cuatro.", intent="reveal", intensities=[0, 0, 0], pico_par=2)
    sin_vacio, _ = tag_cap("Uno dos.\n\nTres cuatro.", intent="reveal", intensities=[0, 0], pico_par=1)
    assert con_vacio != sin_vacio


def test_ya_no_aplica(env):
    _generar(env, _deb(oraciones=(1, 2)))
    mf.editar_parrafo(TID, [i for i, p in enumerate(_n3(env)["parrafos"]) if p["cap"] == 2][0], "Ana Roldan cambió todo.", env["sd"])
    fila = mf.cargar_critica(TID, env["sd"])["validacion"]["deberia"][0]
    assert mf.aplica(fila, _n3(env)["parrafos"]) is False
    with pytest.raises(ValueError, match="ya no aplica"):
        mf.aceptar_deberia(TID, 1, env["sd"])
    with pytest.raises(ValueError, match="no hay DEBERÍA"):
        mf.aceptar_deberia(TID, 9, env["sd"])


def test_no_contigua_o_vacia_no_aplica(env):
    _generar(env, _deb(oraciones=(0, 3)), _deb(cap="ch03", oraciones=(1,)))
    filas = mf.cargar_critica(TID, env["sd"])["validacion"]["deberia"]
    n = _n3(env)["parrafos"]
    assert mf.aplica(filas[0], n) is False and mf.aplica(filas[1], n) is True
    assert mf.aplica({"cap": "ch03", "texto_original": []}, n) is False


def test_dos_deberia_del_mismo_cap_en_orden(env):
    """El segundo se ubica por texto: el `idx` ya se corrió."""
    _generar(env, _deb(oraciones=(0,), texto="Una. Dos. Tres."), _deb(oraciones=(3,), texto="Silencio.", ids=("D3",)))
    mf.aceptar_deberia(TID, 1, env["sd"])
    r = mf.aceptar_deberia(TID, 2, env["sd"])
    a, b = [p for p in _n3(env)["parrafos"] if p["cap"] == 2]
    assert a["texto"] == "Una. Dos. Tres. La casa estaba a oscuras." and b["texto"] == "El valle dormía. Silencio."
    assert "D3" in b["ids_usados"] and r["beats_cambiados"] == [2]


# ═══════════════════════ C.3: QA Studio y run_pipeline ═══════════════════════

def _qa(env, monkeypatch):
    import qa_studio_server as qa
    monkeypatch.setattr(qa, "_steps_dir", lambda state: env["sd"])

    class S:
        topic_id = TID
    return qa, S()


def test_get_narracion(env, monkeypatch):
    qa, st = _qa(env, monkeypatch)
    _generar(env, _deb(oraciones=(1, 2)), _deb(cap="ch03", oraciones=(0,)))
    v = qa.narracion_vista(st)
    assert v["estado"] == {"aprobado": False, "motivo": "la narración no está aprobada"} and not v["sin_critico"]
    assert v["critico"]["nota_total"] == 6.5 and v["critico"]["vigente"] is True and v["critico"]["n_deberia"] == 2
    assert all(k in v["critico"] for k in ("resumen", "gancho", "caps", "loops", "pico", "cierre", "deberia", "riesgos", "usd", "modelo", "prompt_version"))
    assert v["metricas"]["total_palabras"] > 0 and len(v["caps"]) == 7
    c2, c3 = v["caps"][1], v["caps"][2]
    assert [o["idx"] for p in c2["parrafos"] for o in p["oraciones"]] == [0, 1, 2, 3]
    assert c2["nota"] == 7 and c2["racha_max_sin_personaje"] is not None and c2["parrafos"][0]["i"] == 1
    d = c2["deberia"][0]
    assert d["k"] == 1 and d["aplica"] is True and d["palabras_antes"] == 8 and d["cifras_sin_respaldo"] == [] and d["marcas"] == []
    assert c3["deberia"][0]["k"] == 2 and c3["deberia"][0]["aplica"] is True
    mf.editar_parrafo(TID, 0, "Ana Roldan cambió.", env["sd"])
    assert qa.narracion_vista(st)["critico"]["vigente"] is False     # no se re-critica sola


def test_get_narracion_sin_critico_muestra_parrafos(env, monkeypatch):
    qa, st = _qa(env, monkeypatch)
    v = qa.narracion_vista(st)
    assert v["sin_critico"] is True and v["critico"] is None and v["caps"][0]["parrafos"] and v["caps"][0]["deberia"] == []


def test_verificacion_vigente_por_md5(env, monkeypatch):
    qa, st = _qa(env, monkeypatch)
    n = md.md5_narracion(_n3(env))
    (env["d"] / "01b_verificacion.json").write_text(json.dumps({"narracion_md5": n, "quedan": [{"cap": "ch01", "texto": "x"}]}), encoding="utf-8")
    v = qa.narracion_vista(st)["verificacion"]
    assert v["vigente"] is True and len(v["quedan"]) == 1
    f15.aprobar_narracion(TID, "Omar 2026-10-31")                     # aprobar no invalida: el md5 no mira `aprobado`
    assert qa.narracion_vista(st)["verificacion"]["vigente"] is True
    mf.editar_parrafo(TID, 0, "Otro.", env["sd"])
    assert qa.narracion_vista(st)["verificacion"]["vigente"] is False


def test_post_narracion(env, monkeypatch):
    qa, st = _qa(env, monkeypatch)
    _generar(env, _deb(oraciones=(1, 2)))
    assert qa.narracion_post(st, "/narracion/aprobar", {})[1] == 400
    assert qa.narracion_post(st, "/narracion/aceptar", {"k": "1"})[1] == 400
    assert qa.narracion_post(st, "/narracion/aceptar", {"k": 9})[1] == 400
    assert qa.narracion_post(st, "/narracion/editar", {"i": 99, "texto": "x"})[1] == 400
    assert qa.narracion_post(st, "/narracion/otra", {})[1] == 404
    r, s = qa.narracion_post(st, "/narracion/aceptar", {"k": 1})
    assert s == 200 and r["beats_cambiados"] == [2]
    assert qa.narracion_post(st, "/narracion/aceptar", {"k": 1})[1] == 400         # ya no aplica
    r, s = qa.narracion_post(st, "/narracion/aprobar", {"por": "Omar"})
    assert s == 200 and r["aprobado"]["por"] == "Omar"
    assert f15.estado_narracion(TID, env["sd"])[0]
    assert qa.narracion_post(st, "/narracion/editar", {"i": 0, "texto": "Nuevo."})[1] == 200
    assert not f15.estado_narracion(TID, env["sd"])[0]


@pytest.fixture
def rp_env(env, monkeypatch):
    import run_pipeline as rp
    monkeypatch.setattr(rp, "DATA_DIR", env["sd"].parent / "data")
    monkeypatch.setattr(rp, "OUTPUT_DIR", env["sd"].parent / "output")
    monkeypatch.setattr(rp, "_steps_path", lambda tid, n: env["d"] / n)
    monkeypatch.setattr(rp, "_papel_md_path", lambda tid: env["d"] / "01e_pantalla.md")
    monkeypatch.setattr(rp, "_video_hecho", lambda tid: False)
    monkeypatch.setattr(rp, "_packaged", lambda tid: False)
    return rp


def _papel(env, **kw):
    (env["d"] / "01e_pantalla.json").write_text(json.dumps(kw), encoding="utf-8")
    (env["d"] / "01e_pantalla.md").write_text("# papel", encoding="utf-8")


def test_etapa_de_guion_narracion_papel_nuevo_papel(env, rp_env):
    rp = rp_env
    assert rp.etapa_de(TID)[0] == "guion"                             # hay narración, falta la verificación
    (env["d"] / "01b_verificacion.json").write_text("{}", encoding="utf-8")
    assert rp.etapa_de(TID) == ("narracion", "la narración no está aprobada")
    _papel(env, beats=[])                                             # un papel viejo no saltea la compuerta
    assert rp.etapa_de(TID)[0] == "narracion"
    (env["d"] / "01e_pantalla.json").unlink()
    (env["d"] / "01e_pantalla.md").unlink()
    f15.aprobar_narracion(TID, "Omar 2026-10-31")
    assert rp.etapa_de(TID) == ("papel_nuevo", "no hay papel")
    _papel(env, narracion_md5="otro")
    assert rp.etapa_de(TID)[0] == "papel_nuevo"
    _papel(env, beats=[])
    assert rp.etapa_de(TID)[0] == "papel_nuevo"                       # sin el campo y sin aprobar
    _papel(env, narracion_md5=_n3(env)["aprobado"]["md5"])
    assert rp.etapa_de(TID)[0] == "papel"
    mf.editar_parrafo(TID, 0, "Otro.", env["sd"])                     # editar devuelve a la compuerta
    assert rp.etapa_de(TID)[0] == "narracion"


def test_etapa_de_sin_narracion_es_guion(env, rp_env):
    (env["d"] / "01b_narracion_v3.json").unlink()
    assert rp_env.etapa_de(TID)[0] == "guion"


def test_el_form_conoce_la_compuerta():
    import qa_studio_server as qa
    assert qa._FORM_PHASES[:4] == ["RESEARCH", "GUION", "NARRACION", "PAPEL"]
    assert "narracion_gate" in (ROOT / "qa_form.html").read_text(encoding="utf-8")
    s = (ROOT / "qa_studio.html").read_text(encoding="utf-8")
    assert s.index('id="narrBtn"') < s.index('id="papelBtn"') and all(f"/narracion/{x}" in s for x in ("aceptar", "editar", "aprobar"))
