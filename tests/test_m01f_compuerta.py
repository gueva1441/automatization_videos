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
    assert f15.papel_falta(TID) == "papel de otra narración: se re-escribe"
    f.write_text(json.dumps({"beats": []}), encoding="utf-8")
    assert f15.papel_falta(TID) == "papel de otra narración: se re-escribe"


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


# ═══════════════════════ C.2 y F67d: reconstruir y el borrador ═══════════════════════

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


def _editar(env, i: int, texto: str) -> str:
    """Una edición guardada en disco, sin pasar por la página (lo que queda después de un borrador aprobado)."""
    c = mf._carga(TID, env["sd"])
    c["parrafos"][i] = {**c["parrafos"][i], "texto": texto}
    return mf._aplicar(TID, c, env["sd"])


def _borr(env, decisiones=None, ediciones=None) -> dict:
    return mf.borrador(_n3(env)["parrafos"], mf.cargar_critica(TID, env["sd"]), decisiones, ediciones)


def _textos_cap(ps, n=2) -> list[str]:
    return [p["texto"] for p in ps if p["cap"] == n]


ACEPTAR = {"accion": "aceptar"}
RECHAZAR = {"accion": "rechazar"}


def test_editar_invalida_la_aprobacion(env):
    f15.aprobar_narracion(TID, "Omar 2026-10-31")
    assert f15.estado_narracion(TID)[0]
    r = mf.guardar_y_aprobar(TID, {}, [{"i": 0, "texto": "Ana Roldan volvió al valle."}], "Omar", env["sd"])
    n = _n3(env)
    assert n["parrafos"][0]["texto"] == "Ana Roldan volvió al valle." and r["cambio"] is True and n["aprobado"]["por"] == "Omar"
    assert "Ana Roldan volvió al valle." in (env["d"] / "01b_narration.json").read_text(encoding="utf-8")
    _editar(env, 0, "Otra vez.")
    assert "aprobado" not in _n3(env) and not f15.estado_narracion(TID)[0]


@pytest.mark.parametrize("ediciones", [[{"i": 99, "texto": "x"}], [{"i": 0, "texto": "  "}], [{"i": "0", "texto": "x"}]])
def test_ediciones_invalidas(env, ediciones):
    with pytest.raises(ValueError):
        _borr(env, None, ediciones)


def test_decisiones_invalidas(env):
    _generar(env, _deb(oraciones=(1, 2)))
    for mala in ({"1": {"accion": "borrar"}}, {"1": "aceptar"}, {"9": ACEPTAR}, {"1": {"accion": "editar", "texto": "  "}}):
        with pytest.raises(ValueError):
            _borr(env, mala)


def test_borrador_es_puro_y_llega_con_claves_de_json(env, monkeypatch):
    """Sin disco y sin juez: ni reconstruye ni escribe; las claves de `decisiones` llegan como texto."""
    _generar(env, _deb(oraciones=(1, 2), texto="Un texto nuevo."))

    def explota(*a, **k):
        raise AssertionError("el borrador no toca el disco")
    monkeypatch.setattr(mf, "_aplicar", explota)
    antes = _bytes(env)
    ps = _n3(env)["parrafos"]
    copia = json.loads(json.dumps(ps))
    b = mf.borrador(ps, mf.cargar_critica(TID, env["sd"]), {"1": ACEPTAR}, [])
    assert b["por_k"][1]["estado"] == "aplicado" and b["cambio"] is True and b["pendientes"] == []
    assert ps == copia and _bytes(env) == antes


def test_deberia_que_cruza_dos_parrafos(env):
    # ch02: [0] Ana llegó. [1] La casa… (párrafo A) · [2] El valle dormía. [3] Nadie hablaba. (párrafo B)
    _generar(env, _deb(oraciones=(1, 2), texto="[idx1] Un texto  nuevo.", ids=("D2", "NOPE")))
    b = _borr(env, {1: ACEPTAR})
    a, c = [p for p in b["parrafos"] if p["cap"] == 2]
    assert a["texto"] == "Ana Roldan llegó al cap 2. Un texto nuevo." and c["texto"] == "Nadie hablaba."
    assert "D2" in a["ids_usados"] and "NOPE" not in a["ids_usados"] and c["ids_usados"] == ["D8"]
    assert b["por_k"][1]["beats"] == [2] and b["por_k"][1]["beats_sin_texto"] == []


def test_deberia_de_tres_parrafos_elimina_el_del_medio_y_mantiene_el_i_del_disco(env):
    ps = sorted(_parrafos() + [{"cap": 2, "beat": 2, "texto": "Hubo un ruido. Cayó el techo.", "ids_usados": []}], key=lambda p: p["cap"])
    md.particionar({"id": TID}, env["esc"], ps, POOL, call_titles=lambda p, **k: {"titulos": []})
    _generar(env, _deb(oraciones=(1, 2, 3, 4), texto="Reemplazo."))     # de la última del 1.º a la primera del 3.º
    b = _borr(env, {1: ACEPTAR})
    assert _textos_cap(b["parrafos"]) == ["Ana Roldan llegó al cap 2. Reemplazo.", "Cayó el techo."]   # tag_cap correría los índices
    disco = [i for i, p in enumerate(_n3(env)["parrafos"]) if p["cap"] == 2]
    assert [i for i, p in zip(b["indices"], b["parrafos"]) if p["cap"] == 2] == [disco[0], disco[2]]    # nunca sobre la vista previa


def test_los_vacios_correrian_el_pico_de_tag_cap():
    """Por qué se eliminan: tag_cap saltea los párrafos vacíos, pero `pico_par` e `intensities` son índices sobre todos los párrafos."""
    from script_engine.tts_tags import tag_cap
    con_vacio, _ = tag_cap("Uno dos.\n\n\n\nTres cuatro.", intent="reveal", intensities=[0, 0, 0], pico_par=2)
    sin_vacio, _ = tag_cap("Uno dos.\n\nTres cuatro.", intent="reveal", intensities=[0, 0], pico_par=1)
    assert con_vacio != sin_vacio


def test_el_deberia_que_contiene_su_original_se_aplica_una_sola_vez(env):
    """El bug de ch03 de Wittenoom: el texto contiene el original y lo agrega después; aceptar otra vez no lo repite."""
    original = "La casa estaba a oscuras."
    _generar(env, _deb(oraciones=(1,), texto=f"{original} Y no fue la única."))
    b = _borr(env, {1: ACEPTAR})
    assert b["por_k"][1]["estado"] == "aplicado"
    assert _textos_cap(b["parrafos"])[0].count("Y no fue la única.") == 1
    r = mf.guardar_y_aprobar(TID, {"1": ACEPTAR}, [], "Omar", env["sd"])
    assert r["cambio"] is True
    md5 = _n3(env)["aprobado"]["md5"]
    b2 = _borr(env, {1: ACEPTAR})                                       # la original sigue ubicable: no se vuelve a aplicar
    assert b2["por_k"][1]["estado"] == "ya_aplicado" and b2["cambio"] is False
    r2 = mf.guardar_y_aprobar(TID, {"1": ACEPTAR}, [], "Omar", env["sd"])
    assert r2["cambio"] is False and _n3(env)["aprobado"]["md5"] == md5
    assert _textos_cap(_n3(env)["parrafos"])[0].count("Y no fue la única.") == 1


def test_parte_contenida_en_su_original_no_cuenta_como_ya_aplicada(env):
    """Acortar: la parte está en el texto porque está dentro del original, y hay que aplicarla."""
    _generar(env, _deb(oraciones=(1,), texto="La casa"))
    assert _borr(env, {1: ACEPTAR})["por_k"][1]["estado"] == "aplicado"


def test_partes_con_el_separador_por_tramos(env):
    # ch02: [0] [1] · [2] [3]: dos tramos separados
    _generar(env, _deb(oraciones=(0, 3), texto="[idx 0] Primero nuevo. […] [idx 3] Segundo nuevo."))
    b = _borr(env, {1: ACEPTAR})
    assert b["por_k"][1]["estado"] == "aplicado" and b["por_k"][1]["partes_ya_aplicadas"] == 0
    assert _textos_cap(b["parrafos"]) == ["Primero nuevo. La casa estaba a oscuras.", "El valle dormía. Segundo nuevo."]


def test_partes_distintas_de_tramos_no_se_adivina(env):
    """k=5 de Wittenoom: 2 tramos y 1 parte."""
    _generar(env, _deb(oraciones=(0, 3), texto="Un solo texto."))
    p = _borr(env)
    assert p["por_k"][1]["estado"] == "pendiente" and p["por_k"][1]["aplica"] == "no_aplica" and "editar a mano" in p["por_k"][1]["motivo"]
    b = _borr(env, {1: ACEPTAR})
    assert b["por_k"][1]["estado"] == "no_aplica" and b["pendientes"] == [1] and b["cambio"] is False


def test_no_aplica_se_decide_rechazando_o_editando(env):
    _generar(env, _deb(oraciones=(0, 3), texto="Un solo texto."))
    assert _borr(env, {1: RECHAZAR})["pendientes"] == []
    assert _borr(env, {1: {"accion": "editar"}})["por_k"][1]["estado"] == "editado_a_mano"   # lo resolvió en los párrafos
    assert _borr(env, {1: {"accion": "editar"}})["pendientes"] == []
    assert _borr(env, {1: {"accion": "editar", "texto": "Sigue siendo uno."}})["pendientes"] == [1]
    b = _borr(env, {1: {"accion": "editar", "texto": "Uno. […] Dos."}})
    assert b["por_k"][1]["estado"] == "aplicado" and b["pendientes"] == []


def test_una_parte_ya_aplicada_y_otra_no(env):
    _generar(env, _deb(oraciones=(0, 3), texto="El valle dormía. […] Segundo nuevo."))
    b = _borr(env, {1: ACEPTAR})
    assert b["por_k"][1]["estado"] == "aplicado" and b["por_k"][1]["partes_ya_aplicadas"] == 1
    assert _textos_cap(b["parrafos"]) == ["Ana Roldan llegó al cap 2. La casa estaba a oscuras.", "El valle dormía. Segundo nuevo."]


def test_la_edicion_va_primero_y_si_toca_el_tramo_lo_deja_no_aplica(env):
    _generar(env, _deb(oraciones=(1,), texto="Oscuro."), _deb(cap="ch03", oraciones=(0,), texto="Otro."))
    i = [j for j, p in enumerate(_n3(env)["parrafos"]) if p["cap"] == 2][0]
    b = _borr(env, {1: ACEPTAR, 2: ACEPTAR}, [{"i": i, "texto": "Ana Roldan cambió todo."}])
    assert b["por_k"][1] == {"estado": "no_aplica", "motivo": "editado a mano", "oraciones_actuales": []}
    assert b["por_k"][2]["estado"] == "aplicado" and b["pendientes"] == [1]
    assert _textos_cap(b["parrafos"])[0] == "Ana Roldan cambió todo."
    igual = _n3(env)["parrafos"][i]["texto"]
    assert _borr(env, {1: ACEPTAR}, [{"i": i, "texto": igual}])["por_k"][1]["estado"] == "aplicado"   # dejar el texto igual no es editar


def test_ya_no_aplica_si_cambio_el_texto(env):
    _generar(env, _deb(oraciones=(1, 2)))
    _editar(env, [i for i, p in enumerate(_n3(env)["parrafos"]) if p["cap"] == 2][0], "Ana Roldan cambió todo.")
    r = _borr(env, {1: ACEPTAR})["por_k"][1]
    assert r["estado"] == "no_aplica" and "ya no está" in r["motivo"]


def test_dos_deberia_del_mismo_cap_en_orden(env):
    """El segundo se ubica por texto: el `idx` ya se corrió."""
    _generar(env, _deb(oraciones=(0,), texto="Una. Dos. Tres."), _deb(oraciones=(3,), texto="Silencio.", ids=("D3",)))
    b = _borr(env, {1: ACEPTAR, 2: ACEPTAR})
    a, c = [p for p in b["parrafos"] if p["cap"] == 2]
    assert a["texto"] == "Una. Dos. Tres. La casa estaba a oscuras." and c["texto"] == "El valle dormía. Silencio."
    assert "D3" in c["ids_usados"] and b["por_k"][2]["beats"] == [2]


def test_aprobar_con_decisiones_pendientes_no_escribe(env):
    _generar(env, _deb(oraciones=(1,), texto="Uno."), _deb(cap="ch03", oraciones=(0,), texto="Dos."))
    antes = _bytes(env)
    with pytest.raises(ValueError, match=r"falta decidir DEBERÍA \[2\]"):
        mf.guardar_y_aprobar(TID, {"1": ACEPTAR}, [], "Omar", env["sd"])
    assert _bytes(env) == antes and "aprobado" not in _n3(env)
    with pytest.raises(ValueError, match="falta quién"):
        mf.guardar_y_aprobar(TID, {"1": ACEPTAR, "2": ACEPTAR}, [], " ", env["sd"])
    assert _bytes(env) == antes


def test_aprobar_aplica_todo_junto_con_una_sola_reconstruccion_y_un_juez(env, monkeypatch):
    from script_engine import m05_narrative as m5
    _generar(env, _deb(oraciones=(1,), texto="Uno."), _deb(cap="ch03", oraciones=(0,), texto="Dos."))
    cuenta = {"r": 0, "j": 0}
    rec, jue = md.reconstruir, m5.judge_narration

    def r(*a, **k):
        cuenta["r"] += 1
        return rec(*a, **k)

    def j(*a, **k):
        cuenta["j"] += 1
        return jue(*a, **k)
    monkeypatch.setattr(md, "reconstruir", r)
    monkeypatch.setattr(m5, "judge_narration", j)
    res = mf.guardar_y_aprobar(TID, {"1": ACEPTAR, "2": ACEPTAR}, [], "Omar", env["sd"])
    assert cuenta == {"r": 1, "j": 1} and res["aprobado"]["por"] == "Omar"
    n = _n3(env)
    assert f15.estado_narracion(TID)[0] and n["aprobado"]["md5"] == md.md5_narracion(n)
    assert json.loads((env["d"] / "06_judge_narrative.json").read_text(encoding="utf-8"))["retencion"]["total_palabras"] > 0


def test_rechazar_todo_no_reconstruye_y_el_md5_no_cambia(env, monkeypatch):
    _generar(env, _deb(oraciones=(1,), texto="Uno."))
    md5 = md.md5_narracion(_n3(env))

    def explota(*a, **k):
        raise AssertionError("sin cambios no se reconstruye")
    monkeypatch.setattr(mf, "_aplicar", explota)
    r = mf.guardar_y_aprobar(TID, {"1": RECHAZAR}, [], "Omar", env["sd"])
    assert r["cambio"] is False and _n3(env)["aprobado"]["md5"] == md5


def test_las_funciones_viejas_se_borraron():
    assert not any(hasattr(mf, x) for x in ("aceptar_deberia", "editar_parrafo", "aplica", "oraciones_actuales"))


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
    assert d["k"] == 1 and d["palabras_antes"] == 8 and d["cifras_sin_respaldo"] == [] and d["marcas"] == []
    assert c3["deberia"][0]["k"] == 2
    assert v["borrador"]["por_k"][1]["aplica"] == "aplica" and v["borrador"]["pendientes"] == [1, 2] and v["borrador"]["cambio"] is False
    _editar(env, 0, "Ana Roldan cambió.")
    assert qa.narracion_vista(st)["critico"]["vigente"] is False     # no se re-critica sola


def test_borrador_oraciones_actuales_tras_aceptar_otro(env, monkeypatch):
    """El `idx` del crítico se corre al aceptar otro DEBERÍA del cap: la pestaña resalta los de hoy."""
    qa, st = _qa(env, monkeypatch)
    _generar(env, _deb(oraciones=(0,), texto="Una. Dos. Tres."), _deb(oraciones=(3,), texto="Silencio."))
    b = qa.narracion_vista(st)["borrador"]
    assert [b["por_k"][k]["oraciones_actuales"] for k in (1, 2)] == [[0], [3]]
    b, s = qa.narracion_post(st, "/narracion/borrador", {"decisiones": {"1": ACEPTAR}})
    assert s == 200 and b["por_k"][1]["oraciones_actuales"] == [] and b["por_k"][2]["oraciones_actuales"] == [5]
    assert [o["texto"] for p in b["caps"][1]["parrafos"] for o in p["oraciones"]][:3] == ["Una.", "Dos.", "Tres."]


def test_papel_de_otra_narracion_no_pasa_aunque_este_aprobado(env, monkeypatch, capsys):
    monkeypatch.setattr(f15, "_load_topic_by_id", lambda tid: {"id": tid, "evidence_pool": {"datos": [], "_research_v3": True}})
    f15.aprobar_narracion(TID, "Omar 2026-10-31")
    (env["d"] / "01e_pantalla.json").write_text(json.dumps({"narracion_md5": "otra", "beats": []}), encoding="utf-8")
    f15.aprobar_papel(TID, "Omar 2026-10-31")
    assert f15.estado_papel(TID)[0]
    r = f15.process_topic(TID, from_step="normalizer_gate", gate_interactive=False, music_gate_interactive=False)
    assert r["status"] == "PARADA" and r["parada"] == "papel" and "otra narración" in r["motivo"]
    assert "--papel" in capsys.readouterr().out


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
    _editar(env, 0, "Otro.")
    assert qa.narracion_vista(st)["verificacion"]["vigente"] is False


def test_post_narracion(env, monkeypatch):
    qa, st = _qa(env, monkeypatch)
    _generar(env, _deb(oraciones=(1, 2)))
    assert qa.narracion_post(st, "/narracion/aprobar", {"decisiones": {"1": RECHAZAR}})[1] == 400         # falta quién
    assert qa.narracion_post(st, "/narracion/aprobar", {"por": "Omar"})[1] == 400                          # falta decidir
    assert "aprobado" not in _n3(env)
    assert qa.narracion_post(st, "/narracion/borrador", {"decisiones": {"9": ACEPTAR}})[1] == 400
    assert qa.narracion_post(st, "/narracion/borrador", {"ediciones": [{"i": 99, "texto": "x"}]})[1] == 400
    assert qa.narracion_post(st, "/narracion/otra", {})[1] == 404
    for vieja in ("/narracion/aceptar", "/narracion/editar"):                                              # se borraron
        assert qa.narracion_post(st, vieja, {"k": 1, "i": 0, "texto": "x"})[1] == 404
    antes = _bytes(env)
    b, s = qa.narracion_post(st, "/narracion/borrador", {"decisiones": {"1": ACEPTAR}})
    assert s == 200 and b["por_k"]["1" if "1" in b["por_k"] else 1]["estado"] == "aplicado" and _bytes(env) == antes   # no escribe
    r, s = qa.narracion_post(st, "/narracion/aprobar", {"por": "Omar", "decisiones": {"1": ACEPTAR}})
    assert s == 200 and r["aprobado"]["por"] == "Omar"
    assert f15.estado_narracion(TID, env["sd"])[0] and "Un texto nuevo de 1949." in json.dumps(_n3(env)["parrafos"], ensure_ascii=False)
    _editar(env, 0, "Nuevo.")
    assert not f15.estado_narracion(TID, env["sd"])[0]


def test_la_pagina_solo_manda_decisiones_y_el_boton_se_apaga():
    s = (ROOT / "qa_studio.html").read_text(encoding="utf-8")
    assert "/narracion/aceptar" not in s and "/narracion/editar" not in s
    assert "nnBusy||pend.length?'disabled':''" in s and "guardando…" in s and "/narracion/borrador" in s


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
    _editar(env, 0, "Otro.")                     # editar devuelve a la compuerta
    assert rp.etapa_de(TID)[0] == "narracion"


def test_etapa_de_sin_narracion_es_guion(env, rp_env):
    (env["d"] / "01b_narracion_v3.json").unlink()
    assert rp_env.etapa_de(TID)[0] == "guion"


def test_el_form_conoce_la_compuerta():
    import qa_studio_server as qa
    assert qa._FORM_PHASES[:4] == ["RESEARCH", "GUION", "NARRACION", "PAPEL"]
    assert "narracion_gate" in (ROOT / "qa_form.html").read_text(encoding="utf-8")
    s = (ROOT / "qa_studio.html").read_text(encoding="utf-8")
    assert s.index('id="narrBtn"') < s.index('id="papelBtn"') and all(f"/narracion/{x}" in s for x in ("borrador", "aprobar"))


# ═══════════════════════ F67b: cierre de la compuerta ═══════════════════════

def _generar_papel(env):
    return mp.generar(TID, env["sd"], pool=POOL, vocabulario=["CALMA"], post=lambda b: _msg(json.dumps({"beats": []})))


def test_f67b_papel_aprobado_sin_narracion_md5_es_papel_nuevo(env, rp_env):
    (env["d"] / "01b_verificacion.json").write_text("{}", encoding="utf-8")
    f15.aprobar_narracion(TID, "Omar 2026-10-31")
    _papel(env, beats=[], aprobado={"por": "Omar", "fecha": "x", "md5": "y"})
    assert f15.papel_falta(TID) == "papel de otra narración: se re-escribe"
    assert rp_env.etapa_de(TID)[0] == "papel_nuevo"
    _papel(env, narracion_md5="otra", aprobado={"por": "Omar", "fecha": "x", "md5": "y"})
    assert rp_env.etapa_de(TID)[0] == "papel_nuevo"


def test_f67b_papel_aprobado_desfasado_se_reescribe(env, monkeypatch, capsys):
    f15.aprobar_narracion(TID, "Omar 2026-10-31")
    _papel(env, beats=[], aprobado={"por": "Omar", "fecha": "x", "md5": "y"})
    corridas = []
    monkeypatch.setattr(f15, "run_pantalla", lambda tid, pool, log: corridas.append(tid))
    f15.run_papel_aprobado(TID)
    assert corridas == [TID] and "papel de otra narración: se re-escribe" in capsys.readouterr().out


def test_f67b_aprobar_papel_409(env, monkeypatch):
    qa, st = _qa(env, monkeypatch)
    _generar_papel(env)
    r, s = qa.papel_post(st, "/papel/aprobar", {"por": "Omar"})
    assert (s, r["error"]) == (409, "la narración no está aprobada")
    assert qa.papel_vista(st)["bloqueo_aprobar"] == "la narración no está aprobada"
    assert "aprobado" not in mp.cargar_papel(TID, env["sd"])
    f15.aprobar_narracion(TID, "Omar 2026-10-31")
    assert qa.papel_vista(st)["bloqueo_aprobar"] is None
    assert qa.papel_post(st, "/papel/aprobar", {"por": "Omar"})[1] == 200
    _editar(env, 0, "Otro.")                     # editar cae la aprobación de la narración
    f15.aprobar_narracion(TID, "Omar 2026-10-31")
    r, s = qa.papel_post(st, "/papel/aprobar", {"por": "Omar"})
    assert (s, r["error"]) == (409, "el papel es de otra narración")
    assert qa.papel_vista(st)["bloqueo_aprobar"] == "el papel es de otra narración"


def test_f67b_la_pestana_deshabilita_el_boton():
    s = (ROOT / "qa_studio.html").read_text(encoding="utf-8")
    assert "p.bloqueo_aprobar?'disabled':''" in s and 'id="ppBloqueo"' in s


def _normalizado(env, textos):
    (env["d"] / "01b_narration_normalized.json").write_text(json.dumps({"chapters": [
        {"chapter_number": n, "narration_original": t, "narration_normalized": t} for n, t in textos.items()]}, ensure_ascii=False), encoding="utf-8")


def _narr(env) -> dict:
    return {c["chapter_number"]: c["narration"] for c in json.loads((env["d"] / "01b_narration.json").read_text(encoding="utf-8"))["chapters"]}


def test_f67b_normalizado_desfasado_y_vigente(env, capsys):
    f = env["d"] / "01b_narration_normalized.json"
    assert f15.descartar_normalizado(TID) == []                       # no hay: nada
    _normalizado(env, _narr(env))
    assert f15.descartar_normalizado(TID) == [] and f.exists()        # vigente: se queda
    t = _narr(env)
    t[3] = "otro"
    del t[5]
    _normalizado(env, t)
    assert f15.descartar_normalizado(TID) == [3, 5] and not f.exists()
    assert "desfasado: 2 caps distintos, se borra" in capsys.readouterr().out
    f.write_text("{no es json", encoding="utf-8")
    assert len(f15.normalizado_desfasado(TID)) == 7


@pytest.mark.parametrize("desde,borra", [("normalizer_gate", True), ("audio", True), ("m03", False)])
def test_f67b_normalizado_se_borra_antes_de_la_voz(env, monkeypatch, desde, borra):
    monkeypatch.setattr(f15, "_load_topic_by_id", lambda tid: {"id": tid, "evidence_pool": {"datos": [], "_research_v3": True}})
    f15.aprobar_narracion(TID, "Omar 2026-10-31")
    _generar_papel(env)
    f15.aprobar_papel(TID, "Omar 2026-10-31")
    _normalizado(env, {n: "viejo" for n in range(1, 8)})

    class Corte(Exception):
        pass

    def corta(*a, **k):
        raise Corte
    monkeypatch.setattr(f15.m02_5_normalizer_gate, "gate_normalizer_for_topic", corta)
    monkeypatch.setattr(f15, "_build_audio_script", corta)
    monkeypatch.setattr(f15, "assign_visual_prompts", corta)
    monkeypatch.setattr(f15, "_load_skeleton", lambda t: {})
    monkeypatch.setattr(f15, "_load_narration", lambda t: {})
    f15.process_topic(TID, from_step=desde, gate_interactive=False, music_gate_interactive=False)
    assert (env["d"] / "01b_narration_normalized.json").exists() is not borra


def test_f67b_criticar_no_llama_al_verificador_ni_toca_la_narracion(env, monkeypatch, capsys):
    from script_engine import narracion_verificador as nv

    def explota(*a, **k):
        raise AssertionError("--criticar no llama al verificador")
    monkeypatch.setattr(nv, "verificar_caps", explota)
    monkeypatch.setattr(f15, "run_verificacion", explota)
    monkeypatch.setattr(f15, "run_pantalla", explota)
    monkeypatch.setattr(f15, "_step_cost", lambda tid, label, fn: fn())
    f15.aprobar_narracion(TID, "Omar 2026-10-31")
    antes = (env["d"] / "01b_narracion_v3.json").read_bytes()
    pedidos = []

    def post(body):
        pedidos.append(body)
        return _msg(json.dumps(_resp(_deb()), ensure_ascii=False))
    assert f15.criticar(TID, post=post) == 0
    assert len(pedidos) == 1 and pedidos[0]["system"] == mf.SYSTEM
    assert (env["d"] / "01b_narracion_v3.json").read_bytes() == antes and f15.estado_narracion(TID)[0]
    assert json.loads((env["d"] / "01f_critico.json").read_text(encoding="utf-8"))["n_deberia"] == 1
    assert (env["d"] / "06_judge_narrative.json").exists() and "narración aprobada" in capsys.readouterr().out


def test_f67b_criticar_usa_o_avisa_la_verificacion(env):
    assert "| ch01 | x | y | D1 | z |" in mf.entrada(TID, env["sd"], pool=POOL)["verificacion"]
    (env["d"] / "01b_verificacion.md").unlink()
    assert mf.entrada(TID, env["sd"], pool=POOL)["verificacion"] == "sin verificación en disco"


def test_f67b_criticar_sin_narracion_para(env):
    (env["d"] / "01b_narracion_v3.json").unlink()
    with pytest.raises(f15.Parada, match="no hay narración"):
        f15.criticar(TID)
