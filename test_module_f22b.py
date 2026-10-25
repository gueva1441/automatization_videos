"""
test_module_f22b.py — F22b: (a) acepta las cifras de las líneas de datos que recibió el guionista (el «1982» de
Kyshtym F22, que venía en VERSIÓN DE) y no las de los ids ni las de estructura; `claude_helpers` (Messages API de
Anthropic, misma firma que gpt_helpers) y `--modelo claude-opus-5-5` en la cadena v4. Sin red.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

import claude_helpers as ch
from script_engine import guion_v4 as g4
from script_engine.m05_narrative import invented_numbers

ROOT = Path(__file__).resolve().parent
STEPS = ROOT / "data" / "scripts" / "_steps" / "f18-kyshtym-mayak"
F22 = ROOT / "lab" / "hyperframes" / "f22"


def _kyshtym():
    def f22(nombre: str, respaldo: str) -> Path:           # F23 rehízo pool y ficha: los de F22 quedaron como respaldo
        return STEPS / respaldo if (STEPS / respaldo).exists() else STEPS / nombre
    need = [f22("00_pool_v3.json", "00_pool_v3_f22.json"), f22("ficha_caso.json", "ficha_caso_f22.json"),
            STEPS / "01a_escaleta_f22.json", F22 / "guion_kyshtym_f22.json"]
    if not all(p.exists() for p in need):
        pytest.skip("sin los datos de Kyshtym F22")
    pool, ficha, esc, g = (json.loads(p.read_text(encoding="utf-8")) for p in need)
    return {"id": "f18-kyshtym-mayak", "evidence_pool": pool}, ficha, esc, g


# ═══════════════════════════════════════════════════════════════
#  1. Corrector: cifras de lo que recibió el guionista
# ═══════════════════════════════════════════════════════════════

def test_kyshtym_1982_ya_no_es_inventada():
    topic, ficha, esc, g = _kyshtym()
    assert [b["motivo"] for b in g["bloqueantes"]] == ["cifra que no está en el research: 1982"]   # lo de F22
    rec = g4.datos_recibidos(esc, topic["evidence_pool"], ficha)
    assert "VERSIÓN DE: An Analysis of the Alleged Kyshtym Disaster, 1982" in rec
    texto = next(p["texto"] for p in g["parrafos"] if p["beat"] == 13)
    assert "1982" in invented_numbers(texto, topic["evidence_pool"])                 # sin lo recibido, como antes
    assert "1982" not in invented_numbers(texto, topic["evidence_pool"], recibido=rec)
    assert g4.bloqueantes(topic, esc, g["parrafos"], ficha=ficha) == []


def test_ids_y_estructura_no_cuentan_como_cifras():
    esc = {"beats": [{"n": 1, "cap": 1, "funcion": "gancho", "emocion": "miedo", "intensidad": 4,
                      "imagen_sensorial": "x", "dato_central": "D96", "datos_apoyo": ["Q08"], "pregunta_abierta": "?"}],
           "caps": [{"chapter_number": 1}]}
    pool = {"datos": [{"id": "D96", "texto": "un dato sin cifras"}],
            "citas": [{"id": "Q08", "texto": "una cita", "autor": "Alguien"}]}
    rec = g4.datos_recibidos(esc, pool)
    assert "D96" not in rec and "Q08" not in rec and "BEAT" not in rec and "intensidad" not in rec
    assert invented_numbers("En 96 casos, 8 veces, el beat 1, intensidad 4.", pool, recibido=rec) == ["96", "8", "1", "4"]


def test_datos_recibidos_sigue_la_version_del_usuario():
    from test_module_f11 import POOL, _esc_ok
    esc = _esc_ok()
    def esperado(sec: str) -> str:
        return "\n".join(g4._ID_DATO.sub(" ", ln) for ln in sec.splitlines() if g4._ID_DATO.search(ln))
    v5 = g4.datos_recibidos(esc, POOL)
    f11c = g4.datos_recibidos(esc, POOL, version="f11c-1", largo="objetivo")
    assert v5 and v5 == esperado(g4.escaleta_section_v5(esc, POOL))
    assert f11c and f11c == esperado(g4.escaleta_section(esc, POOL, "objetivo"))


# ═══════════════════════════════════════════════════════════════
#  2. claude_helpers y --modelo claude-opus-5-5
# ═══════════════════════════════════════════════════════════════

def test_esquema_gemini_a_structured_outputs():
    s = ch.json_schema(g4.SCHEMA)
    assert s["type"] == "object" and s["additionalProperties"] is False
    item = s["properties"]["parrafos"]["items"]
    assert item["type"] == "object" and item["additionalProperties"] is False
    assert item["properties"]["beat"] == {"type": "integer"} and item["required"] == ["beat", "texto"]


def test_call_json_cuerpo_respuesta_y_costo(monkeypatch):
    seen = []

    def post(body):
        seen.append(body)
        return {"model": "claude-opus-5-5", "stop_reason": "end_turn",
                "content": [{"type": "thinking", "thinking": ""},
                            {"type": "text", "text": '{"parrafos": [{"beat": 1, "texto": "Hola."}]}'}],
                "usage": {"input_tokens": 1_000_000, "output_tokens": 100_000}}
    added = []
    monkeypatch.setattr(ch.cost_tracker, "_add_entry", lambda **k: added.append(k))
    out = ch.make_call("claude-opus-5-5", "high", post=post)("usuario", system_instruction="sistema",
                                                              response_schema=g4.SCHEMA, description="prueba")
    assert out == {"parrafos": [{"beat": 1, "texto": "Hola."}]}
    b = seen[0]
    assert b["model"] == "claude-opus-5-5" and b["system"] == "sistema" and b["max_tokens"] == ch.MAX_TOKENS
    assert b["messages"] == [{"role": "user", "content": "usuario"}] and "thinking" not in b
    assert b["output_config"]["effort"] == "high" and b["output_config"]["format"]["type"] == "json_schema"
    assert added[0]["total_cost"] == pytest.approx(4.0 + 2.0) and added[0]["service"] == "Anthropic claude-opus-5-5"
    assert ch.cost_of("claude-sonnet-5-5", {"input_tokens": 1_000_000, "output_tokens": 1_000_000}) == pytest.approx(12.0)


def test_negativa_y_json_roto(monkeypatch):
    monkeypatch.setattr(ch.cost_tracker, "_add_entry", lambda **k: None)
    monkeypatch.setattr(ch.time, "sleep", lambda s: None)
    with pytest.raises(ch.ClaudeError, match="se negó"):
        ch.call_json("x", model="claude-opus-5-5", post=lambda b: {"stop_reason": "refusal", "content": [],
                                                                    "usage": {}})
    n = {"k": 0}

    def roto(b):
        n["k"] += 1
        return {"stop_reason": "max_tokens", "content": [{"type": "text", "text": '{"parr'}], "usage": {}}
    with pytest.raises(ch.ClaudeError, match="JSON inválido"):
        ch.call_json("x", model="claude-opus-5-5", post=roto)
    assert n["k"] == ch.MAX_ATTEMPTS


def test_llave_de_env_sin_imprimirla(monkeypatch, tmp_path):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setattr(ch, "__file__", str(tmp_path / "claude_helpers.py"))
    (tmp_path / ".env").write_text("OTRA=1\nANTHROPIC_API_KEY=sk-prueba\n", encoding="utf-8")
    assert ch._api_key() == "sk-prueba"
    (tmp_path / ".env").write_text("OTRA=1\n", encoding="utf-8")
    with pytest.raises(ch.ClaudeError, match="falta ANTHROPIC_API_KEY") as e:
        ch._api_key()
    assert "sk-" not in str(e.value)


def test_modelo_claude_en_la_cadena_v4():
    c = g4.call_for("claude-opus-5-5")
    assert c.model == "claude-opus-5-5" and c.reasoning_effort == "high"
    assert "claude-opus-5-5" in g4.MODELOS and g4.call_for(None).model == "gpt-6.1-sol"
    assert '"claude-opus-5-5"' in (ROOT / "fase1_5.py").read_text(encoding="utf-8")
