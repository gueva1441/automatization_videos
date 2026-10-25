"""
test_module_f25b.py — F25b: ficha_caso con --modelo. Un modelo de Claude va por claude_helpers (streaming, max_tokens
100 000, effort medium, sin esquema forzado, JSON sacado del texto) y la respuesta cruda se guarda; sin modelo, Sol
high como siempre. Sin red.
"""
from __future__ import annotations

import json

from researcher_steps import ficha_caso as fc
from test_module_f25a import _sse


def _stream_de(texto: str) -> dict:
    import claude_helpers as ch
    return ch.leer_stream(_sse(
        {"type": "message_start", "message": {"model": "claude-opus-5-5", "usage": {"input_tokens": 10}}},
        {"type": "content_block_start", "index": 0, "content_block": {"type": "text", "text": ""}},
        {"type": "content_block_delta", "index": 0, "delta": {"type": "text_delta", "text": texto}},
        {"type": "message_delta", "delta": {"stop_reason": "end_turn"}, "usage": {"output_tokens": 20}},
        {"type": "message_stop"}))


def test_claude_va_por_claude_helpers_sin_esquema_y_guarda_el_crudo(tmp_path):
    bodies = []

    def post(body):
        bodies.append(body)
        return _stream_de("```json\n{\"hechos\": []}\n```")
    call = fc.call_for("claude-opus-5-5", crudo=tmp_path / "crudo.json", post=post)
    assert (call.model, call.reasoning_effort) == ("claude-opus-5-5", "medium")
    assert fc.build({"datos": []}, "t", call=call) == {"hechos": []}
    b = bodies[0]
    assert b["max_tokens"] == 100_000 and "format" not in b["output_config"] and b["output_config"]["effort"] == "medium"
    assert json.loads((tmp_path / "crudo.json").read_text(encoding="utf-8"))["stop_reason"] == "end_turn"


def test_sin_modelo_sol_high(tmp_path):
    vistos = []

    def post(body):
        vistos.append(body)
        return {"model": "gpt-6.1-sol", "usage": {}, "choices": [{"message": {"content": "{\"hechos\": []}"},
                                                                   "finish_reason": "stop"}]}
    call = fc.call_for(None, crudo=tmp_path / "c.json", post=post)
    assert (call.model, call.reasoning_effort) == ("gpt-6.1-sol", "high") and fc.esfuerzo_de(None) == "high"
    assert fc.build({"datos": []}, "t", call=call) == {"hechos": []} and (tmp_path / "c.json").exists()
    assert vistos[0]["model"] == "gpt-6.1-sol"


def test_save_registra_el_modelo(tmp_path):
    raw_pool = json.dumps({"datos": [], "cronologia": [], "citas": [], "personajes": [], "lugares": []}).encode()
    res = fc.save("t", {}, raw_pool, steps_dir=tmp_path, title="x", tag="x", modelo="claude-opus-5-5")
    assert (res["meta"]["modelo"], res["meta"]["esfuerzo"]) == ("claude-opus-5-5", "medium")
    assert fc.save("t", {}, raw_pool, steps_dir=tmp_path, title="x", tag="x")["meta"]["modelo"] == "gpt-6.1-sol"
