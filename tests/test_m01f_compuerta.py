# -*- coding: utf-8 -*-
"""F67 B y C: el crítico de narración (m01f) y la compuerta NARRACIÓN. Sin API: `claude_helpers._post` explota; todo va con post falso."""
import hashlib
import json
import re
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
