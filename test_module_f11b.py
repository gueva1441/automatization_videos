"""
test_module_f11b.py — F11b (guion v4 con largo + modelos): la guardia de la regeneración (solo cifras, nombres y
citas), el modelo enchufable (con `post`/`call` falsos, sin red), los ids por beat y la línea de largo del prompt.
"""
from __future__ import annotations

import urllib.error

import pytest

import fase1_5 as f15
import gpt_helpers
from cost_tracker import cost_tracker
from script_engine import guion_v4 as g4
from script_engine import m01d_particion as md
from script_engine.m01c_editor import lexical_guard
from test_module_f11 import POOL, TOPIC, _esc, _parrafos

# ═══════════════════════════════════════════════════════════════
#  Guardia de la regeneración (§1.2)
# ═══════════════════════════════════════════════════════════════

ANTES = "El humo bajó del techo. La gente corrió hacia el portón."
CON_ADJ = "El humo negro y espeso bajó del techo. La gente, desesperada, corrió hacia el portón."


def test_guardia_por_defecto_igual_que_siempre():
    assert any(x.startswith("adjetivos nuevos") for x in lexical_guard(ANTES, CON_ADJ))
    assert lexical_guard(ANTES, CON_ADJ) == lexical_guard(ANTES, CON_ADJ, ("cifras", "nombres", "adjetivos", "citas"))


def test_guardia_v4_permite_adjetivos_y_frena_cifras_nombres_citas():
    assert lexical_guard(ANTES, CON_ADJ, g4.REGEN_GUARD) == []
    out = lexical_guard(ANTES, CON_ADJ + " Murieron 400 personas, dijo Pedro Gómez: «nadie nos abrió nunca».",
                        g4.REGEN_GUARD)
    assert [x.split()[0] for x in out] == ["cifras", "nombres", "citas"]


def _regen(guard, seen):
    esc = _esc()
    ps = _parrafos(esc)
    largo = " ".join(["El humo negro y espeso bajó del techo, oscuro, terrible."] * 6)

    def call(prompt, **kw):
        seen.append(prompt)
        return {"parrafos": [{"beat": 2, "texto": largo + " El portón 2 quedó cerrado."},
                             {"beat": 3, "texto": largo + " El portón 3 quedó cerrado."}]}
    kw = {"guard": guard} if guard is not None else {}
    return ps, md.regenerate_cap_v3(TOPIC, esc, ps, 2, POOL, notas=["cap 2 corto"], attempts=1, call=call, **kw)


def test_regenerar_cap_v3_por_defecto_rechaza_adjetivos_nuevos():
    seen: list[str] = []
    ps, out = _regen(None, seen)
    assert out == ps                                                    # el cap queda como estaba
    assert "nombres, adjetivos ni citas" in seen[0]                     # la línea de siempre (v3 / m01c)


def test_regenerar_cap_v4_acepta_prosa_nueva():
    seen: list[str] = []
    ps, out = _regen(g4.REGEN_GUARD, seen)
    assert out != ps and [p["beat"] for p in out if p["cap"] == 2] == [2, 3]
    assert "adjetivos" not in seen[0].split("REGLAS:")[1].split("\n")[0]


def test_reparar_pasa_la_guardia_v4_a_la_regeneracion(monkeypatch):
    got = {}

    def fake_regen(topic, esc, ps, cap, pool, **kw):
        got.setdefault("guard", kw.get("guard"))
        return ps
    monkeypatch.setattr(md, "regenerate_cap_v3", fake_regen)
    esc = _esc()
    ps = [p for p in _parrafos(esc) if p["cap"] != 3]                   # cap 3 vacío → (c) → regenerar
    g4.reparar(TOPIC, esc, ps, call=lambda p, **k: {"texto": "", "parrafos": []}, log=[])
    assert got["guard"] == g4.REGEN_GUARD == ("cifras", "nombres", "citas")


# ═══════════════════════════════════════════════════════════════
#  Modelo enchufable (§1.3) — sin red
# ═══════════════════════════════════════════════════════════════

def _fake_post(bodies, content='{"texto": "ok"}', model="gpt-6.1-sol-2026-09-01"):
    def post(body):
        bodies.append(body)
        return {"model": model, "choices": [{"message": {"content": content}, "finish_reason": "stop"}],
                "usage": {"prompt_tokens": 1_000_000, "completion_tokens": 100_000, "total_tokens": 1_100_000,
                          "completion_tokens_details": {"reasoning_tokens": 40_000}}}
    return post


def test_gpt_call_cuerpo_esfuerzo_esquema_y_costo():
    bodies: list[dict] = []
    call = gpt_helpers.make_call("gpt-6.1-sol", "high", post=_fake_post(bodies))
    cost_tracker.start_video("t-f11b")
    try:
        out = call("PROMPT", system_instruction="SIS", response_schema=g4.EDIT_SCHEMA, description="x")
    finally:
        rep = cost_tracker.end_video()
    b = bodies[0]
    assert out == {"texto": "ok"}
    assert b["model"] == "gpt-6.1-sol" and b["reasoning_effort"] == "high"
    assert b["messages"] == [{"role": "system", "content": "SIS"}, {"role": "user", "content": "PROMPT"}]
    assert b["response_format"]["json_schema"]["schema"]["type"] == "object"
    assert b["response_format"]["json_schema"]["schema"]["properties"]["texto"]["type"] == "string"
    e = rep.entries[0]
    assert e.total_cost == pytest.approx(1.0 * 2.0 + 0.1 * 10.0)         # US$ 2 / 10 por millón in / out
    assert (e.tokens_in, e.tokens_out, e.tokens_thinking) == (1_000_000, 60_000, 40_000)


def test_gpt_sin_esfuerzo_no_manda_el_parametro_y_sin_esquema_json_object():
    bodies: list[dict] = []
    gpt_helpers.make_call("gpt-6-astra", post=_fake_post(bodies, model="gpt-6-astra"))("P")
    assert "reasoning_effort" not in bodies[0] and bodies[0]["response_format"] == {"type": "json_object"}
    assert gpt_helpers.cost_of("gpt-6-astra", {"prompt_tokens": 1e6, "completion_tokens": 1e6}) == 60.0


def test_gpt_modelo_inexistente_se_reporta_y_no_se_reemplaza():
    import io

    def post(body):
        raise urllib.error.HTTPError("u", 404, "nf", {}, io.BytesIO(b'{"error": "model_not_found"}'))
    with pytest.raises(gpt_helpers.GPTError, match="404"):
        gpt_helpers.make_call("gpt-6-astra", post=post)("P")


def test_gpt_reintenta_5xx_y_json_roto(monkeypatch):
    import io
    monkeypatch.setattr(gpt_helpers.time, "sleep", lambda s: None)
    n = {"k": 0}
    ok = _fake_post([])

    def post(body):
        n["k"] += 1
        if n["k"] == 1:
            raise urllib.error.HTTPError("u", 503, "x", {}, io.BytesIO(b"busy"))
        if n["k"] == 2:
            return {**ok(body), "choices": [{"message": {"content": "{roto"}, "finish_reason": "length"}]}
        return ok(body)
    assert gpt_helpers.make_call("gpt-6.1-sol", post=post)("P") == {"texto": "ok"} and n["k"] == 3


def test_call_for_elige_modelo_y_esfuerzo(monkeypatch):
    import gemini_helpers
    assert g4.call_for("gemini-pro") is gemini_helpers.call_pro_json and g4.call_for(None).model == "gpt-6.1-sol"
    sol, astra = g4.call_for("gpt-6.1-sol"), g4.call_for("gpt-6-astra")
    assert (sol.model, sol.reasoning_effort) == ("gpt-6.1-sol", "high")
    assert (astra.model, astra.reasoning_effort) == ("gpt-6-astra", None)
    with pytest.raises(ValueError):
        g4.call_for("gpt-5")


def test_toda_la_cadena_v4_usa_el_call_del_modelo(monkeypatch):
    """guionista + regeneración + edición de oración + editor: todo pasa por el mismo `call` (ninguna llamada se
    escapa a Gemini)."""
    import gemini_helpers

    def boom(*a, **k):
        raise AssertionError("se llamó a Gemini")
    monkeypatch.setattr(gemini_helpers, "call_pro_json", boom)
    esc = _esc()
    descs: list[str] = []

    def call(prompt, **kw):
        descs.append(kw.get("description") or "")
        if kw.get("description") == "guion_v4 guionista":
            return {"parrafos": [{"beat": p["beat"], "texto": p["texto"]} for p in _parrafos(esc) if p["cap"] != 3]}
        return {"texto": "", "parrafos": []}
    g = g4.write(TOPIC, esc, call=call, log=[])
    g4.reparar(TOPIC, esc, g["parrafos"], call=call, log=[])
    assert descs[0] == "guion_v4 guionista" and "m01d regenerate_cap 3" in descs and "guion_v4 editor" in descs


def test_fase1_5_pasa_el_modelo(monkeypatch):
    got = []
    monkeypatch.setattr(f15, "_load_topic_by_id", lambda tid: {"id": tid, "evidence_pool": {"datos": []}})
    monkeypatch.setattr(f15, "_topic_v3", lambda tid: {"id": tid})
    out = {"particion": {"skeleton": {}, "narration": {}}}
    monkeypatch.setattr(f15, "run_guion_v4", lambda tid, modelo=None: got.append(modelo) or out)
    f15.process_topic("t", from_step="m01b", stop_after_step="m01b", v3=True, guion="v4", modelo="gpt-6-astra")
    f15.process_topic("t", from_step="m01b", stop_after_step="m01b", v3=True, guion="v4")
    assert got == ["gpt-6-astra", None]


# ═══════════════════════════════════════════════════════════════
#  Ids por beat (§1.4) y línea de largo (§1.1)
# ═══════════════════════════════════════════════════════════════

def test_ids_por_beat_descarta_lo_que_no_es_del_beat_ni_del_cap():
    esc = _esc()
    p = {"beat": 4, "cap": 3, "texto": "El portón 4 estaba cerrado y el portón 9 también. Hubo 327 muertos."}
    sin = g4.with_ids([p], POOL)[0]["ids_usados"]
    con = g4.with_ids([p], POOL, esc)[0]["ids_usados"]
    assert {"D4", "D9", "D50"} <= set(sin)
    assert con == [i for i in sin if i in g4.beat_ids(esc, 4)] and "D9" not in con and "D50" not in con
    assert "D4" in con and "D3" in g4.beat_ids(esc, 4)                  # D3 = lo asignado al cap 3


def test_ids_por_parrafo_antes_y_despues():
    esc = _esc()
    ps = [{"beat": 4, "cap": 3, "texto": "El portón 4 estaba cerrado y el portón 9 también.", "ids_usados": ["D4"]}]
    m = g4.ids_per_paragraph(ps, POOL, esc)
    assert m["antes"] > m["despues"] >= 1
    assert g4.ids_per_paragraph(ps, POOL, esc, declared=True)["antes"] == 1


def test_prompt_dice_el_largo():
    esc = _esc()
    p = g4.prompt(TOPIC, esc)
    assert "CAP 2 · ≈ 125 palabras" in p                                  # F11c: sin «──» (un solo delimitador)
    assert "es su largo, no un máximo); el video completo ≈ 735 palabras." in p
