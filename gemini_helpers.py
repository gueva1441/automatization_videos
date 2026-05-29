# gemini_helpers.py

import json
import time
from google import genai
from google.genai import types
from google.genai import errors as genai_errors
from config import APIConfig

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


def _safe_json_parse(raw_text: str) -> dict:
    """Parsea JSON tolerando markdown fences y texto extra.

    Cuando falla, dumpea raw_text COMPLETO + texto post-clean a un archivo
    en data/_debug/ y menciona el path en la excepción para diagnóstico.
    """
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
                text = text[start:end+1]

    try:
        result = json.loads(text)
        # Si el modelo devolvió array directo donde el caller esperaba dict
        # con wrapper, normalizar al shape esperado por m03.
        if isinstance(result, list):
            result = {"image_prompts": result}
        return result
    except json.JSONDecodeError as e:
        # Dump completo a disco para diagnosticar
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
            dump_msg = f" | Dump completo: {dump_path}"
        except Exception:
            dump_msg = " | (no se pudo escribir dump)"

        raise ValueError(
            f"Gemini devolvió JSON inválido en char {e.pos} "
            f"(line {e.lineno} col {e.colno}): {e.msg}.{dump_msg}"
        ) from e


def call_flash_json(prompt: str, system_instruction: str | None = None) -> dict:
    """Llama a Gemini Flash y devuelve la respuesta parseada como dict.

    Args:
        prompt: user prompt (contents).
        system_instruction: opcional. Si se pasa, se envía como system_instruction
            del config (separado del user prompt). Si es None, no se incluye el
            field — comportamiento idéntico al previo.
    """
    def _do():
        config_kwargs = {"response_mime_type": "application/json"}
        if system_instruction is not None:
            config_kwargs["system_instruction"] = system_instruction
        response = _client.models.generate_content(
            model=_cfg.gemini_model,
            contents=prompt,
            config=types.GenerateContentConfig(**config_kwargs),
        )
        return _safe_json_parse(response.text)
    return _with_retry(_do)


def call_pro_json(prompt: str, system_instruction: str | None = None) -> dict:
    """Llama a Gemini Pro y devuelve la respuesta parseada como dict.

    Args:
        prompt: user prompt (contents).
        system_instruction: opcional. Si se pasa, se envía como system_instruction
            del config (separado del user prompt). Si es None, no se incluye el
            field — comportamiento idéntico al previo.
    """
    def _do():
        config_kwargs = {"response_mime_type": "application/json"}
        if system_instruction is not None:
            config_kwargs["system_instruction"] = system_instruction
        response = _client.models.generate_content(
            model=_cfg.gemini_model_research,
            contents=prompt,
            config=types.GenerateContentConfig(**config_kwargs),
        )
        return _safe_json_parse(response.text)
    return _with_retry(_do)