"""
test_module_f17.py — F17 (la columna vertebral): el sistema y la tarea de la columna byte-idénticos al archivo del
analista (extraídos anclando en «## SISTEMA», en LF); el usuario con caso, ficha (la misma sección que la escaleta v2)
y tarea; el esquema y el chequeo determinista (7 caps, humano de la ficha, ids que existen, personas de la ficha); una
sola regeneración y después PARADA; la métrica de personas; la escaleta v2 con columna (columna antes de la ficha,
tarea literal de «CÓMO SE USA LA COLUMNA», f17-1, métricas nuevas, los mismos 13 bloqueantes); sin columna, la escaleta
byte-idéntica a F16 (md5); `--sin-columna` en fase1_5; el cost_tracker no escribe el historial bajo pytest. Sin red.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import pytest

from script_engine import m01a_columna as mc
from script_engine import m01a_escaleta as me
from test_module_f6b import POOL, good
from test_module_f16 import FICHA as FICHA16
from test_module_f16 import TOPIC

ROOT = Path(__file__).resolve().parent
F17 = ROOT / "lab" / "hyperframes" / "f17"

FICHA = copy.deepcopy(FICHA16)
FICHA["personas"].append({"nombre": "Marlin N. Gusman", "rol": "sheriff", "variantes": ["Sheriff Gusman"],
                          "ids": ["P01", "Q02"]})


def _md() -> str:
    return (F17 / "PROMPT_COLUMNA_v1.md").read_text(encoding="utf-8").replace("\r\n", "\n")


def _sistema_md() -> tuple[str, str, str]:
    md = _md()
    i0 = md.index("\n## SISTEMA\n\n") + len("\n## SISTEMA\n\n")
    u0 = md.index("\n## USUARIO")
    c0 = md.index("\n## CÓMO SE USA LA COLUMNA")
    t0 = md.index("su tarea cambia a: «", c0) + len("su tarea cambia a: «")
    return (md[i0:md.index("</errores>", i0) + len("</errores>")],
            md[md.index("<tarea>", u0):md.index("</tarea>", u0) + len("</tarea>")],
            md[t0:md.index("»\n", t0)])


def col_buena() -> dict:
    caps = [{"cap": k, "que_pasa": f"pasa {k}", "termina": f"termina {k}", "personas": ["Edward Burton"],
             "ids": [i]} for k, i in enumerate(["Q01", "T01", "T02", "D01", "D08", "D09", "D05"], 1)]
    caps[1]["personas"].append("Sheriff Gusman")
    # F22: la columna v1.1 trae QUIÉN DECIDE (antagonista); el sheriff de la ficha
    return {"humano": {"nombre": "Edward Burton", "por_que": "entra, sufre, sale", "ids": ["P08", "Q01"]},
            "antagonista": {"tipo": "persona", "nombre": "Marlin N. Gusman", "por_que": "decide", "ids": ["P01"]},
            "pico": {"cap": 5, "que": "los cadáveres", "ids": ["D08"]}, "caps": caps,
            "afuera": [{"que": "Catorce órdenes de arresto", "por_que": "no suma al hilo"}]}


# ═══════════════════════════════════════════════════════════════
#  Prompt de la columna (§1.1)
# ═══════════════════════════════════════════════════════════════

def test_sistema_columna_byte_identico_al_archivo():
    sis, tarea, _ = _sistema_md()
    # F22: la v1 de F17 queda con su versión, byte-idéntica (la v1.1 en test_module_f22)
    assert mc.SYSTEM_F17_1 == sis and mc.TAREA_F17_1 == tarea and mc.PROMPT_VERSION_F17 == "f17-1"
    assert sis.startswith("<rol>\nSos el guionista jefe") and sis.endswith("</errores>")
    assert "## SISTEMA" not in mc.SYSTEM_F17_1 and "Para CC" not in mc.SYSTEM_F17_1


def test_usuario_columna_caso_ficha_tarea():
    p = mc.build_prompt(TOPIC, POOL, FICHA)
    assert p.startswith("<caso>") and p.endswith(mc.TAREA)
    assert p.index("<caso>") < p.index("<ficha>") < p.index("</ficha>") < p.index("<tarea>")
    assert me.ficha_section_v2(FICHA, POOL) in p                       # la misma sección que la escaleta v2
    assert "<rechazo>" not in p and "Notas del editor" not in p
    p2 = mc.build_prompt(TOPIC, POOL, FICHA, ["x"], notas="más corto el cap 3")
    assert p2.index("<rechazo>") < p2.index("<tarea>") < p2.index("Notas del editor") < p2.index("</tarea>")
    assert "más corto el cap 3" in p2


# ═══════════════════════════════════════════════════════════════
#  Esquema y chequeo (§1.1)
# ═══════════════════════════════════════════════════════════════

def test_esquema_de_la_tarea():
    props = mc.SCHEMA["properties"]
    assert set(props) == {"humano", "antagonista", "pico", "caps", "afuera"}             # F22: + antagonista
    assert set(props["humano"]["properties"]) == {"nombre", "por_que", "ids"}
    assert set(props["pico"]["properties"]) == {"cap", "que", "ids"}
    assert set(props["caps"]["items"]["properties"]) == {"cap", "que_pasa", "termina", "personas", "ids"}
    assert set(props["afuera"]["items"]["properties"]) == {"que", "por_que"}


def test_columna_buena_pasa():
    assert mc.chequeo(col_buena(), POOL, FICHA) == []


@pytest.mark.parametrize("nombre, fn, frag", [
    ("6 caps", lambda c: c.update(caps=c["caps"][:6]), "caps 1 a 7"),
    ("caps fuera de orden", lambda c: c["caps"][2].update(cap=5), "caps 1 a 7"),
    ("humano fuera de la ficha", lambda c: c["humano"].update(nombre="Renard Reed"), "humano"),
    ("id que no existe", lambda c: c["caps"][3].update(ids=["D99"]), "D99"),
    ("id del pico", lambda c: c["pico"].update(ids=["Q77"]), "Q77"),
    ("persona fuera de la ficha", lambda c: c["caps"][4]["personas"].append("Renard Reed"), "Renard Reed"),
])
def test_chequeo_rechaza(nombre, fn, frag):
    c = col_buena()
    fn(c)
    prob = mc.chequeo(c, POOL, FICHA)
    assert prob and any(frag in p for p in prob), (nombre, prob)


def test_nombres_y_ids_con_explicacion():
    c = col_buena()
    c["caps"][0]["personas"] = ["Burton", "Gusman (sheriff)"]
    c["caps"][0]["ids"] = ["Q01: Burton bebe del inodoro", "T01, D03: dos cosas"]
    c = mc.leer_ids(c)
    assert c["caps"][0]["ids"] == ["Q01", "T01", "D03"] and mc.chequeo(c, POOL, FICHA) == []
    assert mc.personas_con_nombre(c, FICHA) == ["Edward Burton", "Marlin N. Gusman"]


# ═══════════════════════════════════════════════════════════════
#  Una sola regeneración, PARADA, Sol (§1.1)
# ═══════════════════════════════════════════════════════════════

def _gen(respuestas, tmp_path, monkeypatch, **kw):
    monkeypatch.setattr(mc, "STEPS_DIR", tmp_path)
    prompts = []

    def call(prompt, **k):
        prompts.append((prompt, k.get("system_instruction"), k.get("response_schema")))
        return copy.deepcopy(respuestas[len(prompts) - 1])
    return prompts, (lambda: mc.generate_columna(TOPIC, POOL, FICHA, call=call, **kw))


def test_una_regeneracion_y_parada(tmp_path, monkeypatch):
    mala = col_buena()
    mala["caps"] = mala["caps"][:6]
    prompts, go = _gen([mala, mala, col_buena()], tmp_path, monkeypatch)
    with pytest.raises(mc.ColumnaError, match="PARADA"):
        go()
    assert len(prompts) == 2 and "<rechazo>" not in prompts[0][0] and "<rechazo>" in prompts[1][0]
    assert all(s == mc.SYSTEM and sch is mc.SCHEMA for _, s, sch in prompts)
    assert (tmp_path / "t-f16" / "01a_columna_rechazada.json").exists()


def test_regeneracion_que_pasa_guarda_y_mide(tmp_path, monkeypatch):
    mala = col_buena()
    mala["humano"]["nombre"] = "Nadie"
    prompts, go = _gen([mala, col_buena()], tmp_path, monkeypatch)
    col = go()
    assert len(prompts) == 2 and col["prompt_version"] == mc.PROMPT_VERSION
    assert col["_metricas"] == {"personas_con_nombre": 2, "personas": ["Edward Burton", "Marlin N. Gusman"]}
    assert json.loads((tmp_path / "t-f16" / "01a_columna.json").read_text(encoding="utf-8"))["humano"]["nombre"] == \
        "Edward Burton"
    md = mc.to_markdown(col, "Orleans")
    assert "**HUMANO:** Edward Burton" in md and "**CAP 7 · QUÉ PASA:** pasa 7 **TERMINA:** termina 7" in md
    assert "**AFUERA:** Catorce órdenes de arresto (no suma al hilo)" in md


def test_columna_usa_sol_high(monkeypatch, tmp_path):
    import gpt_helpers
    seen = {}

    def fake_make_call(model, effort=None, post=None):
        seen["m"] = (model, effort)
        return lambda prompt, **kw: col_buena()
    monkeypatch.setattr(gpt_helpers, "make_call", fake_make_call)
    monkeypatch.setattr(mc, "STEPS_DIR", tmp_path)
    mc.generate_columna(TOPIC, POOL, FICHA, persist=False)
    assert seen["m"] == ("gpt-6.1-sol", "high")


# ═══════════════════════════════════════════════════════════════
#  Escaleta v2 con columna (§1.2) y sin columna (F16 byte-idéntica)
# ═══════════════════════════════════════════════════════════════

def test_tarea_columna_literal():
    assert me.TAREA_COLUMNA == "<tarea>\n" + _sistema_md()[2] + "\n</tarea>"
    assert me.PROMPT_VERSION_COLUMNA_F17 == "f17-1" and me.PROMPT_VERSION_COLUMNA == "f26-1"   # F22e; F24; F25c; F26


def test_escaleta_con_columna_antes_de_la_ficha():
    p = me.build_prompt_v2(TOPIC, POOL, FICHA, columna=col_buena())
    assert p.index("<caso>") < p.index("<columna>") < p.index("</columna>") < p.index("<ficha>") < p.index("<tarea>")
    assert p.endswith(me.TAREA_COLUMNA) and me.TAREA_V2 not in p
    assert mc.section(col_buena()) in p and "HUMANO: Edward Burton" in p and "CAP 7 · QUÉ PASA: pasa 7" in p


# md5 de la escaleta v2 de HEAD (fceeee3, F16) con los fixtures de test_module_f16 (sin y con feedback).
ESC_V2_MD5 = {"sin_fb": "5aea02448a1916912d53e9ab0e66db21", "fb": "560e94e3b7ea68bde810a8d48d1c617d"}
# md5 de los prompts reales de F16 (lab/hyperframes/f16/costos_f16.json, prompt_md5_intento1).
F16_REAL = {"sistema": "49ed74d941def064cdda077212629ff1",
            "ycua": ("f8s1-ycua-bolanos", "2d77969a706f3cdc1a2b71581ba044b2"),
            "orl": ("ba6c3cac-f7r3", "d748efd2f49d60319fce7ff67eeb06bb")}


def _md5(s: str) -> str:
    return hashlib.md5(s.encode("utf-8")).hexdigest()


def test_escaleta_sin_columna_byte_identica_a_f16():
    assert _md5(me.build_prompt_v2(TOPIC, POOL, FICHA16)) == ESC_V2_MD5["sin_fb"]
    assert _md5(me.build_prompt_v2(TOPIC, POOL, FICHA16, ["a"])) == ESC_V2_MD5["fb"]
    assert me.build_prompt_v2(TOPIC, POOL, FICHA16, columna=None) == me.build_prompt_v2(TOPIC, POOL, FICHA16)
    assert _md5(me.SYSTEM_V2_F16_1) == F16_REAL["sistema"]                 # F22: la v2 de F16, con su versión


@pytest.mark.parametrize("tema", ["ycua", "orl"])
def test_escaleta_sin_columna_md5_de_los_prompts_reales_de_f16(tema):
    from researcher_steps import ficha_caso as fc
    tid, md5 = F16_REAL[tema]
    ficha = fc.load(tid)
    if not ficha or not (me.STEPS_DIR / tid / "00_pool_v3.json").exists():
        pytest.skip("sin los datos de F16 en _steps")
    import fase1_5 as f15
    topic = dict(f15._load_topic_by_id(tid))
    assert _md5(me.build_prompt_v2(topic, topic["evidence_pool"], ficha)) == md5


def _esc(monkeypatch, tmp_path, respuestas, **kw):
    monkeypatch.setattr(me, "STEPS_DIR", tmp_path)
    monkeypatch.setattr(mc, "STEPS_DIR", tmp_path)
    monkeypatch.setattr(me, "pool_gate_profile", lambda *a, **k: None)
    prompts = []

    def call(prompt, **k):
        prompts.append((prompt, k.get("system_instruction"), k.get("description")))
        return copy.deepcopy(respuestas[len(prompts) - 1])
    return prompts, me.generate_escaleta(TOPIC, call=call, persist=False, ficha=FICHA, **kw)


def test_escaleta_con_columna_version_y_metricas(monkeypatch, tmp_path):
    prompts, esc = _esc(monkeypatch, tmp_path, [good()], columna=col_buena())
    assert len(prompts) == 1 and prompts[0][1] == me.SYSTEM_V2 and "<columna>" in prompts[0][0]
    assert esc["prompt_version"] == me.PROMPT_VERSION_COLUMNA and esc["columna"]["prompt_version"] is None
    m = esc["_metricas"]["columna"]
    assert m["humano_es_el_de_la_columna"] is True
    assert m["caps_con_personas_fuera"] == []                          # Gusman (Q02) no está en ningún beat
    assert set(m["cierres"]) == set(range(1, 8)) and m["cierres_iguales"] == 0
    e = good()
    e["beats"][7]["cierre"] = "termina 7"
    e["beats"][4]["datos_apoyo"] = ["Q02"]                             # Gusman en el cap 5: la columna no lo nombra
    m = _esc(monkeypatch, tmp_path, [e], columna=col_buena())[1]["_metricas"]["columna"]
    assert m["cierres"][7]["igual"] is True and m["personas_fuera_de_la_columna"] == {5: ["Marlin N. Gusman"]}


def test_escaleta_con_columna_mismos_bloqueantes(monkeypatch, tmp_path):
    mala = good()
    mala["pico"]["beat"] = 99
    with pytest.raises(me.EscaletaValidationError, match="PARADA"):
        _esc(monkeypatch, tmp_path, [mala, mala], columna=col_buena())


def test_generar_columna_y_despues_escaleta(monkeypatch, tmp_path):
    prompts, esc = _esc(monkeypatch, tmp_path, [col_buena(), good()], columna="generar")
    assert [p[1] for p in prompts] == [mc.SYSTEM, me.SYSTEM_V2]
    assert "<columna>" in prompts[1][0] and esc["prompt_version"] == me.PROMPT_VERSION_COLUMNA


def test_sin_columna_la_escaleta_es_f16(monkeypatch, tmp_path):
    prompts, esc = _esc(monkeypatch, tmp_path, [good()])
    assert len(prompts) == 1 and "<columna>" not in prompts[0][0] and esc["prompt_version"] == me.PROMPT_VERSION_V2
    assert "columna" not in esc and "columna" not in esc["_metricas"]


# ═══════════════════════════════════════════════════════════════
#  fase1_5 --sin-columna (§1.4) · cost_history (§3)
# ═══════════════════════════════════════════════════════════════

@pytest.mark.parametrize("columna", [False, True])
def test_fase1_5_sin_columna(monkeypatch, tmp_path, columna):
    # F22d (decisión del analista): la escaleta va siempre sin columna; `columna=True` genera la columna aparte, solo
    # como página de lectura
    import fase1_5 as f15
    seen = {}
    monkeypatch.setattr(f15, "_topic_v3", lambda tid: {"id": tid, "evidence_pool": POOL})
    monkeypatch.setattr(f15, "_step_cost", lambda tid, label, fn: fn())
    monkeypatch.setattr(f15, "STEPS_DIR", tmp_path)
    monkeypatch.setattr(me, "generate_escaleta", lambda topic, **kw: seen.update(kw) or {"ok": 1})
    monkeypatch.setattr("researcher_steps.ficha_caso.load", lambda tid, d=None: FICHA)
    monkeypatch.setattr(mc, "generate_columna", lambda *a, **k: seen.setdefault("col", col_buena()))
    (tmp_path / "t-f17").mkdir()
    f15.run_escaleta_v3("t-f17", columna=columna)
    assert seen["columna"] is None
    assert ("col" in seen) is columna and (tmp_path / "t-f17" / "COLUMNA_t-f17.md").exists() is columna


def test_fase1_5_flag_sin_columna():
    import inspect

    import fase1_5 as f15
    src = inspect.getsource(f15.main)
    assert '"--sin-columna"' in src and '"--columna"' in src and "columna=args.columna" in src   # F22d
    assert "columna" in inspect.signature(f15.process_topic).parameters


def test_cost_tracker_no_escribe_el_historial_bajo_pytest(tmp_path, monkeypatch):
    from cost_tracker import cost_tracker
    f = tmp_path / "cost_history.json"
    monkeypatch.setattr(type(cost_tracker), "HISTORY_FILE", f)
    cost_tracker.start_video("t-f17")
    cost_tracker.end_video()
    assert not f.exists()
