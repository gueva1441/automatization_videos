"""
test_module_f39_escaleta.py — F39 §A.2 (HANDOFF_F39_fase1_de_la_semilla): la escaleta sin ficha v2 es un error que
para. (a) sin ficha → `EscaletaSinFicha` con el mensaje, sin llamar a ningún modelo; (b) ficha sin `historia` (v1) →
igual; (c) con ficha v2 sintética y `call` falso, el camino v2 de siempre. Además: el camino `escaleta_frozen` no mira
la ficha. Fixtures sintéticos (test_module_f6b / test_module_f16), nada de data/. Sin red.
"""
from __future__ import annotations

import copy
import json

import pytest

from script_engine import m01a_escaleta as me
from test_module_f6b import POOL, good
from test_module_f16 import FICHA

TOPIC = {"id": "t-f39", "video_title": "X", "angle": "a", "mystery": "m", "reveal": "r", "evidence_pool": POOL}
MSG = "t-f39: sin ficha_caso.json con historia"


def _boom(*a, **k):
    raise AssertionError("sin ficha v2 no se llama a ningún modelo")


@pytest.fixture
def steps(tmp_path, monkeypatch):
    monkeypatch.setattr(me, "STEPS_DIR", tmp_path)
    monkeypatch.setattr(me, "call_escaleta", lambda *a, **k: _boom)      # el `call` por defecto también explota
    return tmp_path


def _sin_escaleta(steps) -> bool:
    d = steps / TOPIC["id"]
    return not (d / "01a_escaleta.json").exists() and not (d / "01a_escaleta_rechazada.json").exists()


# ═══════════════════════════════════════════════════════════════
#  (a) sin ficha
# ═══════════════════════════════════════════════════════════════

def test_sin_ficha_en_disco_para_sin_llamar(steps):
    with pytest.raises(me.EscaletaSinFicha) as e:
        me.generate_escaleta(dict(TOPIC), call=_boom)
    assert str(e.value) == MSG and _sin_escaleta(steps)
    with pytest.raises(me.EscaletaSinFicha, match=MSG):                  # sin `call`: el de por defecto no se arma
        me.generate_escaleta(dict(TOPIC))
    with pytest.raises(me.EscaletaSinFicha, match=MSG):                  # ficha=None explícito
        me.generate_escaleta(dict(TOPIC), call=_boom, ficha=None, persist=False)


def test_sin_ficha_tambien_con_columna_generar(steps, monkeypatch):
    from script_engine import m01a_columna as mc
    monkeypatch.setattr(mc, "generate_columna", _boom)
    with pytest.raises(me.EscaletaSinFicha, match=MSG):
        me.generate_escaleta(dict(TOPIC), call=_boom, columna="generar", persist=False)


def test_es_excepcion_publica_y_no_es_de_validacion():
    assert issubclass(me.EscaletaSinFicha, Exception)
    assert not issubclass(me.EscaletaSinFicha, me.EscaletaValidationError)


# ═══════════════════════════════════════════════════════════════
#  (b) ficha sin `historia` (v1)
# ═══════════════════════════════════════════════════════════════

FICHA_V1 = {k: v for k, v in FICHA.items() if k != "historia"}


def test_ficha_sin_historia_para_igual(steps):
    with pytest.raises(me.EscaletaSinFicha, match=MSG):
        me.generate_escaleta(dict(TOPIC), call=_boom, ficha=copy.deepcopy(FICHA_V1), persist=False)
    (steps / TOPIC["id"]).mkdir(parents=True, exist_ok=True)              # la misma, leída del disco («auto»)
    (steps / TOPIC["id"] / "ficha_caso.json").write_text(json.dumps(FICHA_V1), encoding="utf-8")
    with pytest.raises(me.EscaletaSinFicha, match=MSG):
        me.generate_escaleta(dict(TOPIC), call=_boom)
    assert _sin_escaleta(steps)


def test_topic_id_como_lo_usa_la_funcion(steps):
    t = {k: v for k, v in TOPIC.items() if k != "id"} | {"topic_id": "otro-id"}
    with pytest.raises(me.EscaletaSinFicha, match="^otro-id: sin ficha_caso.json con historia$"):
        me.generate_escaleta(t, call=_boom, persist=False)


# ═══════════════════════════════════════════════════════════════
#  (c) con ficha v2: el camino v2 de siempre
# ═══════════════════════════════════════════════════════════════

def test_con_ficha_v2_sigue_el_camino_v2(steps):
    seen = []

    def call(prompt, **kw):
        seen.append((prompt, kw.get("system_instruction"), kw.get("response_schema")))
        return good()
    (steps / TOPIC["id"]).mkdir(parents=True, exist_ok=True)
    (steps / TOPIC["id"] / "ficha_caso.json").write_text(json.dumps(FICHA), encoding="utf-8")
    esc = me.generate_escaleta(dict(TOPIC), call=call)
    assert len(seen) == 1
    p, s, sch = seen[0]
    assert s == me.SYSTEM_V2 and sch is me.SCHEMA_FICHA
    assert me.pool_gate_profile(dict(TOPIC), POOL, persist=False) is None   # pool sin compuerta: sin rango de beats
    assert p == me.build_prompt_v2(TOPIC, POOL, FICHA)
    assert esc["prompt_version"] == me.PROMPT_VERSION_V2 and esc["ficha"]["prompt_version"] == FICHA["prompt_version"]
    assert "_metricas" in esc and [c["chapter_number"] for c in esc["caps"]] == list(range(1, 8))
    assert (steps / TOPIC["id"] / "01a_escaleta.json").exists()


def test_con_ficha_v2_dict_sin_call_va_por_call_escaleta(steps, monkeypatch):
    pedidos = []

    def fake_call_escaleta(modelo=None):
        pedidos.append(modelo)
        return lambda *a, **k: good()
    monkeypatch.setattr(me, "call_escaleta", fake_call_escaleta)
    esc = me.generate_escaleta(dict(TOPIC), ficha=copy.deepcopy(FICHA), persist=False, modelo="m-x")
    assert pedidos == ["m-x"] and esc["prompt_version"] == me.PROMPT_VERSION_V2


# ═══════════════════════════════════════════════════════════════
#  escaleta_frozen: no se toca (no mira la ficha)
# ═══════════════════════════════════════════════════════════════

def test_frozen_no_mira_la_ficha(steps):
    (steps / "fz").mkdir()
    saved = steps / "fz" / "01a_escaleta.json"
    saved.write_text(json.dumps(good(), ensure_ascii=False), encoding="utf-8")
    fz = me.generate_escaleta({**TOPIC, "escaleta_frozen": {"escaleta": str(saved)}}, call=_boom)
    assert fz["beats"][0]["dato_central"] == good()["beats"][0]["dato_central"] and "_frozen" in fz
