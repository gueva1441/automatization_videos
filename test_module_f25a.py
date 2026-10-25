"""
test_module_f25a.py — F25a, regla de Omar para Claude: max_tokens 100 000 con streaming obligatorio (los eventos SSE se
arman en el mismo dict que la respuesta sin streaming), effort por etapa (high solo en el guion) y sin esquema forzado
en las salidas grandes (la ficha). Sin red.
"""
from __future__ import annotations

import io
import json

import pytest

import claude_helpers as ch


def _sse(*eventos: dict) -> list[bytes]:
    out = []
    for e in eventos:
        out += [f"event: {e['type']}\n".encode(), f"data: {json.dumps(e)}\n".encode(), b"\n"]
    return out


STREAM = _sse(
    {"type": "message_start", "message": {"id": "m1", "model": "claude-fable-5-1", "content": [],
                                          "usage": {"input_tokens": 1200, "output_tokens": 1}}},
    {"type": "content_block_start", "index": 0, "content_block": {"type": "thinking", "thinking": ""}},
    {"type": "content_block_delta", "index": 0, "delta": {"type": "thinking_delta", "thinking": "pienso"}},
    {"type": "content_block_stop", "index": 0},
    {"type": "content_block_start", "index": 1, "content_block": {"type": "text", "text": ""}},
    {"type": "ping"},
    {"type": "content_block_delta", "index": 1, "delta": {"type": "text_delta", "text": "{\"a\": "}},
    {"type": "content_block_delta", "index": 1, "delta": {"type": "text_delta", "text": "1}"}},
    {"type": "content_block_stop", "index": 1},
    {"type": "message_delta", "delta": {"stop_reason": "end_turn"}, "usage": {"output_tokens": 345}},
    {"type": "message_stop"})


def test_leer_stream_arma_el_mensaje():
    m = ch.leer_stream(STREAM)
    assert m["model"] == "claude-fable-5-1" and m["stop_reason"] == "end_turn"
    assert m["usage"] == {"input_tokens": 1200, "output_tokens": 345}
    txt = "".join(b.get("text") or "" for b in m["content"] if b.get("type") == "text")
    assert json.loads(txt) == {"a": 1} and m["content"][0]["type"] == "thinking"


def test_post_va_en_streaming_con_100k(monkeypatch):
    vistos = {}

    class Resp(io.BytesIO):
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    def urlopen(req, timeout):
        vistos["body"] = json.loads(req.data.decode("utf-8"))
        vistos["accept"] = req.get_header("Accept")
        return Resp(b"".join(STREAM))
    monkeypatch.setattr(ch, "_api_key", lambda: "x")
    monkeypatch.setattr(ch.urllib.request, "urlopen", urlopen)
    out = ch.call_json("p", model="claude-fable-5-1", description="t")
    assert out == {"a": 1} and vistos["body"]["stream"] is True and vistos["body"]["max_tokens"] == 100_000
    assert vistos["accept"] == "text/event-stream" and ch.MAX_TOKENS == 100_000


def test_error_en_el_stream_sobrecargado_reintenta(monkeypatch):
    n = {"k": 0}

    def post(body):
        n["k"] += 1
        if n["k"] == 1:
            return ch.leer_stream(_sse({"type": "error", "error": {"type": "overloaded_error", "message": "x"}}))
        return ch.leer_stream(STREAM)
    monkeypatch.setattr(ch.time, "sleep", lambda s: None)
    assert ch.call_json("p", model="claude-fable-5-1", post=post) == {"a": 1} and n["k"] == 2
    with pytest.raises(ch.ClaudeError, match="invalid_request_error"):
        ch.call_json("p", model="claude-fable-5-1", post=lambda b: ch.leer_stream(_sse(
            {"type": "error", "error": {"type": "invalid_request_error", "message": "mal"}})))


def test_sin_esquema_el_json_puede_venir_envuelto():
    envuelto = _sse(
        {"type": "message_start", "message": {"model": "claude-fable-5-1", "usage": {"input_tokens": 1}}},
        {"type": "content_block_start", "index": 0, "content_block": {"type": "text", "text": ""}},
        {"type": "content_block_delta", "index": 0, "delta": {"type": "text_delta",
                                                              "text": "Acá va la ficha:\n```json\n{\"a\": {\"b\": 2}}\n```"}},
        {"type": "message_delta", "delta": {"stop_reason": "end_turn"}, "usage": {"output_tokens": 9}},
        {"type": "message_stop"})
    assert ch.call_json("p", model="claude-fable-5-1", description="ficha_caso", response_schema={"type": "OBJECT"},
                        post=lambda b: ch.leer_stream(envuelto)) == {"a": {"b": 2}}
    assert ch.json_del_texto("sin json") == "sin json"


def test_salida_grande_va_sin_esquema_y_esfuerzo_por_etapa():
    bodies = []

    def post(body):
        bodies.append(body)
        return ch.leer_stream(STREAM)
    sch = {"type": "OBJECT", "properties": {"a": {"type": "INTEGER"}}}
    ch.call_json("p", model="claude-fable-5-1", response_schema=sch, description="ficha_caso", effort="medium", post=post)
    ch.call_json("p", model="claude-fable-5-1", response_schema=sch, description="m01a_escaleta v2 intento 1",
                 effort="medium", post=post)
    assert "format" not in bodies[0]["output_config"] and bodies[0]["output_config"]["effort"] == "medium"
    assert bodies[1]["output_config"]["format"]["type"] == "json_schema"
    assert ch.ESFUERZO_POR_ETAPA == {"guion": "high", "ficha": "medium", "escaleta": "medium"}
