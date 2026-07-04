# gemini_helpers.py

import json
import time
from google import genai
from google.genai import types
from google.genai import errors as genai_errors
from config import APIConfig
# HANDOFF_133: telemetría de costo por tokens en EL productor (una sola costura para
# todos los módulos que llaman via call_flash_json/call_pro_json). cost_tracker NO importa
# gemini_helpers → sin ciclo.
from cost_tracker import cost_tracker

_cfg = APIConfig()
_client = genai.Client(api_key=_cfg.gemini_api_key)


def _with_retry(fn, max_attempts: int = 3):
    """Reintenta fn() con backoff exponencial si Gemini devuelve 503."""
    for attempt in range(max_attempts):
        try:
            return fn()
        except genai_errors.ServerError:
            if attempt == max_attempts - 1:
                raise
            wait = 2 ** (attempt + 1)  # 2s, 4s, 8s
            print(f"[gemini] 503, reintentando en {wait}s ({attempt+1}/{max_attempts})")
            time.sleep(wait)


# HANDOFF 66b — LEVER A: resiliencia de parseo centralizada. Si el modelo devuelve JSON roto
# (ej. comillas dobles sin escapar dentro de un string), se RE-LLAMA (generación fresca) hasta
# PARSE_MAX_ATTEMPTS. Solo el fallo FINAL dumpea + propaga, con el MISMO mensaje de error que
# antes (hay UI/consola que lo lee). Protege a los 6 módulos de una, sin tocar su retry.
PARSE_MAX_ATTEMPTS = 3


class _JsonParseError(ValueError):
    """Parse falló (SIN dump). El loop decide re-llamar o dumpear+propagar.
    args[0] = (raw_text, text_post_clean, JSONDecodeError)."""


def _try_json_parse(raw_text: str) -> dict:
    """Igual que el viejo _safe_json_parse PERO sin dump: lanza _JsonParseError en falla.
    Tolera markdown fences / texto extra recortando al objeto/array más externo."""
    text = raw_text.strip()

    # Tolerar tanto objetos {...} como arrays [...] como output principal.
    # Gemini 3+ a veces devuelve array directo donde 2.5 devolvía wrapper.
    if not (text.startswith("{") or text.startswith("[")):
        # Si hay basura antes/después, recortar al objeto/array más externo.
        first_obj = text.find("{")
        first_arr = text.find("[")
        candidates = [c for c in (first_obj, first_arr) if c != -1]
        if candidates:
            start = min(candidates)
            end = max(text.rfind("}"), text.rfind("]"))
            if end > start:
                text = text[start:end + 1]

    try:
        result = json.loads(text)
        # Si el modelo devolvió array directo donde el caller esperaba dict
        # con wrapper, normalizar al shape esperado por m03. (PRESERVADO).
        if isinstance(result, list):
            result = {"image_prompts": result}
        return result
    except json.JSONDecodeError as e:
        raise _JsonParseError((raw_text, text, e))


def _dump_invalid_json(raw_text: str, text: str, e: "json.JSONDecodeError") -> str:
    """Escribe el dump a data/_debug/ y devuelve el sufijo ' | Dump completo: <path>'
    (cuerpo idéntico al except viejo — preserva el diagnóstico en disco)."""
    from datetime import datetime
    from config import DATA_DIR
    debug_dir = DATA_DIR / "_debug"
    debug_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
    dump_path = debug_dir / f"json_invalid_{timestamp}.txt"

    dump_content = (
        f"=== JSON INVALIDO ===\n"
        f"Timestamp: {datetime.now().isoformat()}\n"
        f"JSONDecodeError: {e}\n"
        f"Error pos: line {e.lineno} col {e.colno} (char {e.pos})\n"
        f"raw_text length: {len(raw_text)} chars\n"
        f"text post-clean length: {len(text)} chars\n"
        f"\n=== RAW_TEXT (input crudo de Gemini) ===\n{raw_text}\n"
        f"\n=== TEXT POST-CLEAN (lo que se intentó parsear) ===\n{text}\n"
    )
    try:
        dump_path.write_text(dump_content, encoding="utf-8")
        return f" | Dump completo: {dump_path}"
    except Exception:
        return " | (no se pudo escribir dump)"


def _parse_with_retry(get_text_fn) -> dict:
    """Llama get_text_fn() (que devuelve el .text del modelo, con su propio retry de 503) y
    parsea. Si el parseo falla, re-llama (generación fresca) hasta PARSE_MAX_ATTEMPTS. Solo el
    fallo FINAL dumpea + propaga, con el MISMO mensaje de error que hoy."""
    last = None
    for attempt in range(1, PARSE_MAX_ATTEMPTS + 1):
        raw = get_text_fn()
        try:
            return _try_json_parse(raw)
        except _JsonParseError as pe:
            last = pe.args[0]
            if attempt < PARSE_MAX_ATTEMPTS:
                _rt, _tx, _e = last
                print(f"[gemini] JSON inválido (intento {attempt}/{PARSE_MAX_ATTEMPTS}) "
                      f"char {_e.pos}: {_e.msg} — re-llamando")
    raw_text, text, e = last
    dump_msg = _dump_invalid_json(raw_text, text, e)
    raise ValueError(
        f"Gemini devolvió JSON inválido en char {e.pos} "
        f"(line {e.lineno} col {e.colno}): {e.msg}.{dump_msg}"
    )


def call_flash_json(prompt: str, system_instruction: str | None = None,
                    response_schema=None) -> dict:
    """Llama a Gemini Flash y devuelve la respuesta parseada como dict.

    Args:
        prompt: user prompt (contents).
        system_instruction: opcional. Si se pasa, se envía como system_instruction
            del config (separado del user prompt). Si es None, no se incluye el
            field — comportamiento idéntico al previo.
        response_schema: opcional (MODEL_PROMPTING_RULES R4). Si se pasa, se agrega
            a config_kwargs para forzar la estructura del output (los campos del
            schema pasan a ser obligatorios). Si es None, NO se incluye el field —
            comportamiento idéntico al previo (default).
    """
    def _get_text():
        config_kwargs = {"response_mime_type": "application/json"}
        if system_instruction is not None:
            config_kwargs["system_instruction"] = system_instruction
        if response_schema is not None:
            config_kwargs["response_schema"] = response_schema
        resp = _with_retry(lambda: _client.models.generate_content(
            model=_cfg.gemini_model,
            contents=prompt,
            config=types.GenerateContentConfig(**config_kwargs),
        ))
        # HANDOFF_133: trackear cada generación REAL (incluye re-llamadas por parseo).
        cost_tracker.track_gemini_response(resp, _cfg.gemini_model, "call_flash_json")
        return resp.text
    return _parse_with_retry(_get_text)


def call_pro_json(prompt: str, system_instruction: str | None = None,
                  response_schema=None) -> dict:
    """Llama a Gemini Pro y devuelve la respuesta parseada como dict.

    Args:
        prompt: user prompt (contents).
        system_instruction: opcional. Si se pasa, se envía como system_instruction
            del config (separado del user prompt). Si es None, no se incluye el
            field — comportamiento idéntico al previo.
        response_schema: opcional (MODEL_PROMPTING_RULES R4). Si se pasa, se agrega
            a config_kwargs. Si es None, NO se incluye — comportamiento idéntico
            al previo (default).
    """
    def _get_text():
        config_kwargs = {"response_mime_type": "application/json"}
        if system_instruction is not None:
            config_kwargs["system_instruction"] = system_instruction
        if response_schema is not None:
            config_kwargs["response_schema"] = response_schema
        resp = _with_retry(lambda: _client.models.generate_content(
            model=_cfg.gemini_model_research,
            contents=prompt,
            config=types.GenerateContentConfig(**config_kwargs),
        ))
        # HANDOFF_133: trackear cada generación REAL (incluye re-llamadas por parseo).
        cost_tracker.track_gemini_response(resp, _cfg.gemini_model_research, "call_pro_json")
        return resp.text
    return _parse_with_retry(_get_text)