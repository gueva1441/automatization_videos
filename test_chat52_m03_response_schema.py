"""
test_chat52_m03_response_schema.py — BLOQUE 1 del handoff m03 two-step: gemini_helpers gana
response_schema opcional (MODEL_PROMPTING_RULES R4).

OBJETIVO: call_flash_json / call_pro_json aceptan response_schema=None (default). Cuando se pasa,
va a config_kwargs (fuerza la estructura del output). Cuando NO se pasa, el field NO se incluye →
comportamiento IDÉNTICO al de hoy (las llamadas existentes no se rompen).

A) UNIT (sin red): mockea el SDK y captura el config para verificar el branching.
B) LIVE (red, guardado por SKIP_LIVE): un schema que fuerza una lista de strings devuelve eso.

Correr:  python -X utf8 test_chat52_m03_response_schema.py
         SKIP_LIVE=1 python -X utf8 test_chat52_m03_response_schema.py
"""
from __future__ import annotations

import os
import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import gemini_helpers as gh

_fails: list[str] = []


def check(cond: bool, msg: str):
    print(("  ✓ " if cond else "  ✗ ") + msg)
    if not cond:
        _fails.append(msg)


class _FakeConfig:
    """Captura los kwargs con que se construye GenerateContentConfig."""
    def __init__(self, **kwargs):
        self.kwargs = kwargs


class _FakeModels:
    def __init__(self, sink):
        self._sink = sink

    def generate_content(self, model, contents, config):
        self._sink["model"] = model
        self._sink["config"] = config
        class _R:
            text = '{"ok": 1}'
        return _R()


class _FakeClient:
    def __init__(self, sink):
        self.models = _FakeModels(sink)


def _capture(call, **call_kwargs):
    """Corre `call` con SDK mockeado; devuelve (config_kwargs, model)."""
    sink: dict = {}
    orig_client, orig_cfg = gh._client, gh.types.GenerateContentConfig
    gh._client = _FakeClient(sink)
    gh.types.GenerateContentConfig = _FakeConfig
    try:
        res = call(**call_kwargs)
    finally:
        gh._client, gh.types.GenerateContentConfig = orig_client, orig_cfg
    return sink["config"].kwargs, sink.get("model"), res


def test_sin_schema_identico():
    print("\n[B1] sin response_schema → config IDÉNTICO a hoy (no aparece el field)")
    cfg, model, res = _capture(gh.call_flash_json, prompt="p")
    check("response_schema" not in cfg, "NO incluye response_schema cuando no se pasa")
    check(cfg.get("response_mime_type") == "application/json", "mantiene response_mime_type=application/json")
    check("system_instruction" not in cfg, "sin system_instruction tampoco aparece (default)")
    check(res == {"ok": 1}, "parsea la respuesta como antes")


def test_con_schema_va_al_config():
    print("\n[B1] con response_schema → se agrega a config_kwargs")
    schema = {"type": "ARRAY", "items": {"type": "STRING"}}
    cfg, model, res = _capture(gh.call_flash_json, prompt="p",
                               system_instruction="SYS", response_schema=schema)
    check(cfg.get("response_schema") == schema, "response_schema pasa tal cual al config")
    check(cfg.get("system_instruction") == "SYS", "system_instruction sigue funcionando junto al schema")
    check(cfg.get("response_mime_type") == "application/json", "response_mime_type sigue presente")


def test_pro_simetrico():
    print("\n[B1] call_pro_json simétrico (mismo branching, modelo de research)")
    schema = {"type": "OBJECT"}
    cfg_none, model_none, _ = _capture(gh.call_pro_json, prompt="p")
    cfg_sch, model_sch, _ = _capture(gh.call_pro_json, prompt="p", response_schema=schema)
    check("response_schema" not in cfg_none, "pro: sin schema no aparece el field")
    check(cfg_sch.get("response_schema") == schema, "pro: con schema va al config")
    check(model_none == gh._cfg.gemini_model_research, "pro usa gemini_model_research")


def test_live_schema_fuerza_lista():
    print("\n[B1·LIVE] un schema 'lista de strings' fuerza esa estructura")
    schema = {"type": "ARRAY", "items": {"type": "STRING"}}
    try:
        out = gh.call_flash_json(
            "Devolvé una lista JSON con exactamente 3 colores primarios, en español.",
            response_schema=schema,
        )
    except Exception as e:
        print(f"  ⚠ SKIP live: {str(e)[:90]}")
        return
    # _safe_json_parse envuelve un array suelto como {"image_prompts": [...]}
    arr = out.get("image_prompts") if isinstance(out, dict) else out
    ok = isinstance(arr, list) and len(arr) >= 1 and all(isinstance(x, str) for x in arr)
    print(f"     output: {arr}")
    check(ok, f"el schema forzó una lista de strings (obtuvo {type(arr).__name__})")


if __name__ == "__main__":
    test_sin_schema_identico()
    test_con_schema_va_al_config()
    test_pro_simetrico()
    if os.environ.get("SKIP_LIVE"):
        print("\n[B1·LIVE] SKIPPED (SKIP_LIVE set)")
    else:
        test_live_schema_fuerza_lista()

    print("\n" + ("=" * 60))
    if _fails:
        print(f"FALLOS: {len(_fails)}")
        for f in _fails:
            print(f"  - {f}")
        sys.exit(1)
    print("TODO OK")
