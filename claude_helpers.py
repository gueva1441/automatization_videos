# claude_helpers.py — F22b: la Messages API de Anthropic con salida JSON, para enchufar Claude en la cadena del guion v4.
# Copia de gpt_helpers.py (misma firma que gemini_helpers.call_pro_json: prompt, system_instruction, response_schema,
# thinking_budget, description → dict), así guion_v4 / m01d / m01c no se enteran del cambio. HTTP directo como
# gpt_helpers (el SDK `anthropic` no está instalado en el venv); header `anthropic-version` 2026-10-21.
#
# La llave se lee de ANTHROPIC_API_KEY (entorno) o de `.env` en la raíz del repo. NUNCA se imprime ni se guarda: los
# errores muestran el código HTTP y el cuerpo de la respuesta, nunca el pedido ni los headers.
# Costo: usage × PRICES (US$ por millón de tokens de entrada / salida; el razonamiento factura como salida y ya viene
# dentro de `output_tokens`) → cost_tracker, como cualquier llamada de Gemini o GPT.

import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Callable

from cost_tracker import cost_tracker
from error_handler import PipelineStage

URL = "https://api.anthropic.com/v1/messages"
API_VERSION = "2026-10-21"
# Fuente: tabla pública de precios de Anthropic (US$ por millón in / out): Opus 5.5 4 / 20, Sonnet 5.5 2 / 10;
# F22d: Fable 5.1 10 / 50.
PRICES = {"claude-opus-5-5": (4.0, 20.0), "claude-sonnet-5-5": (2.0, 10.0), "claude-fable-5-1": (10.0, 50.0)}
MAX_ATTEMPTS = 3
TIMEOUT_S = 600
MAX_TOKENS = 32000


class ClaudeError(RuntimeError):
    """El modelo no existe, la llave falta, el modelo se negó o la API falló después de los reintentos. Se reporta; no
    se cambia de modelo."""


def _api_key() -> str:
    key = os.environ.get("ANTHROPIC_API_KEY")
    if key:
        return key
    env = Path(__file__).resolve().parent / ".env"
    if env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            k, sep, v = line.strip().partition("=")
            if sep and k.strip() == "ANTHROPIC_API_KEY":
                return v.strip().strip('"').strip("'")
    raise ClaudeError("falta ANTHROPIC_API_KEY (entorno o .env)")


def json_schema(s: Any) -> Any:
    """Esquema estilo Gemini (`"type": "OBJECT"`) → JSON Schema de structured outputs (`"type": "object"`, y cada
    objeto con `additionalProperties: false`, que la API exige)."""
    if isinstance(s, dict):
        out = {k: (v.lower() if k == "type" and isinstance(v, str) else json_schema(v)) for k, v in s.items()}
        if out.get("type") == "object":
            out["additionalProperties"] = False
        return out
    if isinstance(s, list):
        return [json_schema(x) for x in s]
    return s


def _post(body: dict) -> dict:
    req = urllib.request.Request(URL, data=json.dumps(body).encode("utf-8"),
                                 headers={"x-api-key": _api_key(), "anthropic-version": API_VERSION,
                                          "content-type": "application/json"})
    with urllib.request.urlopen(req, timeout=TIMEOUT_S) as r:
        return json.load(r)


def _base(model: str) -> str:
    return next((m for m in PRICES if model.startswith(m)), model)


def cost_of(model: str, usage: dict) -> float:
    pin, pout = PRICES.get(_base(model)) or (0.0, 0.0)
    tin = (usage.get("input_tokens") or 0) + (usage.get("cache_creation_input_tokens") or 0) * 1.25 \
        + (usage.get("cache_read_input_tokens") or 0) * 0.1
    return tin / 1e6 * pin + (usage.get("output_tokens") or 0) / 1e6 * pout


def _track(model: str, usage: dict, description: str) -> float:
    cost = cost_of(model, usage)
    tin, tout = usage.get("input_tokens") or 0, usage.get("output_tokens") or 0
    cost_tracker._add_entry(stage=PipelineStage.SCRIPT.value, service=f"Anthropic {_base(model)}",
                            description=description, units=tin + tout, unit_label="tokens", cost_per_unit=0.0,
                            total_cost=cost, tokens_in=tin, tokens_out=tout, tokens_thinking=0, usage_ok=bool(usage))
    return cost


def call_json(prompt: str, *, model: str, system_instruction: str | None = None, response_schema: Any = None,
              effort: str | None = None, description: str | None = None,
              post: Callable[[dict], dict] | None = None, max_tokens: int | None = None) -> dict:
    """Una llamada a la Messages API con salida JSON. `response_schema` (estilo Gemini) va como
    `output_config.format` (json_schema); sin esquema no se agrega formato y se parsea el texto. `effort` va en `output_config.effort` (Opus 5.5 tiene por defecto `medium`). Thinking: el adaptativo por
    defecto del modelo (no se manda `thinking`). Reintenta 429/5xx/529/timeout y JSON roto (generación fresca) hasta
    MAX_ATTEMPTS; otro 4xx o `stop_reason: refusal` → ClaudeError en el acto."""
    post = post or _post
    body: dict[str, Any] = {"model": model, "max_tokens": max_tokens or MAX_TOKENS,
                            "messages": [{"role": "user", "content": prompt}]}
    if system_instruction:
        body["system"] = system_instruction
    oc: dict[str, Any] = {}
    if effort:
        oc["effort"] = effort
    if response_schema is not None:
        oc["format"] = {"type": "json_schema", "schema": json_schema(response_schema)}
    if oc:
        body["output_config"] = oc
    desc = description or "call_claude_json"
    last = ""
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            r = post(body)
        except urllib.error.HTTPError as e:
            msg = e.read().decode("utf-8", "replace")[:300]
            if e.code in (408, 429, 529) or e.code >= 500:
                last = f"HTTP {e.code}: {msg}"
                time.sleep(2 ** attempt)
                continue
            raise ClaudeError(f"{model}: HTTP {e.code}: {msg}") from None
        except (urllib.error.URLError, TimeoutError) as e:
            last = f"{type(e).__name__}"
            time.sleep(2 ** attempt)
            continue
        _track(r.get("model") or model, r.get("usage") or {}, desc)
        if r.get("stop_reason") == "refusal":
            raise ClaudeError(f"{model}: {desc}: el modelo se negó ({r.get('stop_details')})")
        txt = "".join(b.get("text") or "" for b in r.get("content") or [] if b.get("type") == "text")
        try:
            return json.loads(txt)
        except json.JSONDecodeError as e:
            last = f"JSON inválido ({e.msg}; stop_reason {r.get('stop_reason')})"
            print(f"[claude] {desc}: {last} (intento {attempt}/{MAX_ATTEMPTS}) — re-llamando")
    raise ClaudeError(f"{model}: {desc} falló después de {MAX_ATTEMPTS} intentos: {last}")


def make_call(model: str, effort: str | None = None,
              post: Callable[[dict], dict] | None = None) -> Callable[..., dict]:
    """Un `call` con la firma de gemini_helpers.call_pro_json, atado a `model` y `effort`. `thinking_budget` (de
    Gemini) se ignora."""
    def _call(prompt: str, system_instruction: str | None = None, response_schema: Any = None,
              thinking_budget: int | None = None, description: str | None = None) -> dict:
        return call_json(prompt, model=model, system_instruction=system_instruction, response_schema=response_schema,
                         effort=effort, description=description, post=post)
    _call.model = model                         # type: ignore[attr-defined]
    _call.reasoning_effort = effort             # type: ignore[attr-defined]
    return _call
