"""
test_module_f22d.py — F22d (decisión del analista): la escaleta va sin columna por defecto (`--columna` genera la
columna solo como página de lectura) y el guion v4 usa claude-opus-5-5 por defecto (max_tokens 32 000, esfuerzo high);
escaleta y columna siguen en Sol. Prompts sin cambios. Sin red.
"""
from __future__ import annotations

import hashlib

import claude_helpers as ch
from script_engine import guion_v4 as g4


def test_modelo_del_guion_por_defecto():
    # F22e: el modelo por defecto del guion pasa a Fable 5.1; Opus 5.5 y Sol siguen con --modelo
    assert g4.DEFAULT_MODELO_GUION == "claude-fable-5-1" and g4.DEFAULT_MODELO == "gpt-6.1-sol"
    c = g4.call_for(g4.DEFAULT_MODELO_GUION)
    assert (c.model, c.reasoning_effort) == ("claude-fable-5-1", "high") and ch.MAX_TOKENS == 100_000   # F25a: 100k
    assert g4.call_for("claude-opus-5-5").model == "claude-opus-5-5" and g4.call_for("gpt-6.1-sol").model == "gpt-6.1-sol"


def test_run_guion_v4_sin_modelo_usa_el_del_guion(monkeypatch):
    import fase1_5 as f15
    seen = {}

    class Corte(Exception):
        pass

    def fake_call_for(m):
        seen["m"] = m
        raise Corte
    monkeypatch.setattr(f15, "_topic_v3", lambda tid: {"id": tid, "evidence_pool": {}})
    monkeypatch.setattr(f15, "_load_step_output", lambda tid, name: {})
    monkeypatch.setattr(g4, "call_for", fake_call_for)
    for modelo, esperado in ((None, "claude-fable-5-1"), ("gpt-6.1-sol", "gpt-6.1-sol"),
                             ("claude-opus-5-5", "claude-opus-5-5")):
        try:
            f15.run_guion_v4("t", modelo=modelo)
        except Corte:
            pass
        assert seen["m"] == esperado


def test_prompts_sin_cambios():
    from researcher_steps import ficha_caso as fc
    from script_engine import m01a_columna as mc
    from script_engine import m01a_escaleta as me

    def m(s: str) -> str:
        return hashlib.md5(s.encode("utf-8")).hexdigest()
    # F23: ficha v2.2 y guion v5.3 en test_module_f23; acá, los de F22 con su versión
    # F24: la escaleta f22-2 con su versión (la de hoy, f24-1, en test_module_f24)
    assert [m(fc.system("f22-1")), m(mc.SYSTEM), m(g4.system("f22-1"))] == [
        "7d3599dc6e4123a3bb883fc15a541e71", "f294cf6b1220983903ce339f5b21cb27",
        "743e4f0a7ff9e58d86762bbd43679952"]                 # F55 C.0 (ii): la escaleta f22-2 ya no vive en el código
