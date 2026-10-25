"""
test_module_f22d.py — F22d (decisión del analista): la escaleta va sin columna por defecto (`--columna` genera la
columna solo como página de lectura) y el guion v4 usa claude-opus-5-5 por defecto (max_tokens 32 000, esfuerzo high);
escaleta y columna siguen en Sol. Prompts sin cambios. Sin red.
"""
from __future__ import annotations

import hashlib

import claude_helpers as ch
from script_engine import guion_v4 as g4


def test_modelo_del_guion_por_defecto_es_opus():
    assert g4.DEFAULT_MODELO_GUION == "claude-opus-5-5" and g4.DEFAULT_MODELO == "gpt-6.1-sol"
    c = g4.call_for(g4.DEFAULT_MODELO_GUION)
    assert (c.model, c.reasoning_effort) == ("claude-opus-5-5", "high") and ch.MAX_TOKENS == 32000


def test_run_guion_v4_sin_modelo_usa_opus(monkeypatch):
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
    for modelo, esperado in ((None, "claude-opus-5-5"), ("gpt-6.1-sol", "gpt-6.1-sol")):
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
    assert [m(fc.system()), m(mc.SYSTEM), m(me.SYSTEM_V2), m(g4.system())] == [
        "7d3599dc6e4123a3bb883fc15a541e71", "f294cf6b1220983903ce339f5b21cb27", "7ea18a6aa1ca91c5ad0dfb7cc9b239a8",
        "743e4f0a7ff9e58d86762bbd43679952"]
