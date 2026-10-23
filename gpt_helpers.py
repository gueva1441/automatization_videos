# gpt_helpers.py — F11b (HANDOFF_F11b §1.3): OpenAI chat completions con salida JSON, para enchufar otro modelo en
# la cadena del guion v4. Misma firma que gemini_helpers.call_pro_json (prompt, system_instruction, response_schema,
# thinking_budget, description) → dict, así guion_v4 / m01d / m01c no se enteran del cambio.
#
# La llave se lee de OPENAI_API_KEY (entorno) o de `.env` en la raíz del repo. NUNCA se imprime ni se guarda: los
# errores muestran el código HTTP y el cuerpo de la respuesta, nunca el pedido ni los headers.
# Costo: usage × PRICES (US$ por millón de tokens de entrada / salida; el razonamiento factura como salida) →
# cost_tracker, como cualquier llamada de Gemini.

import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Callable

from cost_tracker import cost_tracker
from error_handler import PipelineStage

URL = "https://api.openai.com/v1/chat/completions"
# Fuente: HANDOFF_F11b §1.3 (precios que pasó el analista; Sol US$ 2 / 10, Astra US$ 10 / 50 por millón in / out).
PRICES = {"gpt-6.1-sol": (2.0, 10.0), "gpt-6-astra": (10.0, 50.0)}
MAX_ATTEMPTS = 3
TIMEOUT_S = 600
MAX_COMPLETION_TOKENS = 32000


class GPTError(RuntimeError):
    """El modelo no existe, la llave falta o la API falló después de los reintentos. Se reporta; no se cambia de
    modelo."""


def _api_key() -> str:
    key = os.environ.get("OPENAI_API_KEY")
    if key:
        return key
    env = Path(__file__).resolve().parent / ".env"
    if env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            k, sep, v = line.strip().partition("=")
            if sep and k.strip() == "OPENAI_API_KEY":
                return v.strip().strip('"').strip("'")
    raise GPTError("falta OPENAI_API_KEY (entorno o .env)")


def json_schema(s: Any) -> Any:
    """Esquema estilo Gemini (`"type": "OBJECT"`) → JSON Schema (`"type": "object"`)."""
    if isinstance(s, dict):
        return {k: (v.lower() if k == "type" and isinstance(v, str) else json_schema(v)) for k, v in s.items()}
    if isinstance(s, list):
        return [json_schema(x) for x in s]
    return s


def _post(body: dict) -> dict:
    req = urllib.request.Request(URL, data=json.dumps(body).encode("utf-8"),
                                 headers={"Authorization": "Bearer " + _api_key(),
                                          "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=TIMEOUT_S) as r:
        return json.load(r)


def cost_of(model: str, usage: dict) -> float:
    pin, pout = PRICES.get(model) or PRICES.get(_base(model)) or (0.0, 0.0)
    return (usage.get("prompt_tokens") or 0) / 1e6 * pin + (usage.get("completion_tokens") or 0) / 1e6 * pout


def _base(model: str) -> str:
    """«gpt-6.1-sol-2026-09-01» (lo que devuelve la API) → «gpt-6.1-sol»."""
    return next((m for m in PRICES if model.startswith(m)), model)


def _track(model: str, usage: dict, description: str) -> float:
    cost = cost_of(model, usage)
    reasoning = ((usage.get("completion_tokens_details") or {}).get("reasoning_tokens") or 0)
    cost_tracker._add_entry(stage=PipelineStage.SCRIPT.value, service=f"OpenAI {_base(model)}", description=description,
                            units=usage.get("total_tokens") or 0, unit_label="tokens", cost_per_unit=0.0,
                            total_cost=cost, tokens_in=usage.get("prompt_tokens") or 0,
                            tokens_out=(usage.get("completion_tokens") or 0) - reasoning, tokens_thinking=reasoning,
                            usage_ok=bool(usage))
    return cost


def call_json(prompt: str, *, model: str, system_instruction: str | None = None, response_schema: Any = None,
              reasoning_effort: str | None = None, description: str | None = None,
              post: Callable[[dict], dict] | None = None, max_completion_tokens: int | None = None) -> dict:
    """Una llamada a chat completions con salida JSON. `response_schema` (estilo Gemini) va como `json_schema` no
    estricto; sin esquema, `json_object`. Reintenta 429/5xx/timeout y JSON roto (generación fresca) hasta
    MAX_ATTEMPTS; 4xx (modelo inexistente, parámetro inválido) → GPTError en el acto. `max_completion_tokens` (F12):
    tope de salida + razonamiento de la llamada; None → MAX_COMPLETION_TOKENS."""
    post = post or _post
    msgs = ([{"role": "system", "content": system_instruction}] if system_instruction else []) + \
        [{"role": "user", "content": prompt}]
    body: dict[str, Any] = {"model": model, "messages": msgs, "max_completion_tokens": max_completion_tokens or MAX_COMPLETION_TOKENS,
                            "response_format": ({"type": "json_schema", "json_schema": {
                                "name": "salida", "schema": json_schema(response_schema), "strict": False}}
                                if response_schema is not None else {"type": "json_object"})}
    if reasoning_effort:
        body["reasoning_effort"] = reasoning_effort
    desc = description or "call_gpt_json"
    last = ""
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            r = post(body)
        except urllib.error.HTTPError as e:
            msg = e.read().decode("utf-8", "replace")[:300]
            if e.code == 429 or e.code >= 500:
                last = f"HTTP {e.code}: {msg}"
                time.sleep(2 ** attempt)
                continue
            raise GPTError(f"{model}: HTTP {e.code}: {msg}") from None
        except (urllib.error.URLError, TimeoutError) as e:
            last = f"{type(e).__name__}"
            time.sleep(2 ** attempt)
            continue
        _track(r.get("model") or model, r.get("usage") or {}, desc)
        ch = (r.get("choices") or [{}])[0]
        txt = (ch.get("message") or {}).get("content") or ""
        try:
            return json.loads(txt)
        except json.JSONDecodeError as e:
            last = f"JSON inválido ({e.msg}; finish_reason {ch.get('finish_reason')})"
            print(f"[gpt] {desc}: {last} (intento {attempt}/{MAX_ATTEMPTS}) — re-llamando")
    raise GPTError(f"{model}: {desc} falló después de {MAX_ATTEMPTS} intentos: {last}")


def make_call(model: str, reasoning_effort: str | None = None,
              post: Callable[[dict], dict] | None = None) -> Callable[..., dict]:
    """Un `call` con la firma de gemini_helpers.call_pro_json, atado a `model` y `reasoning_effort`.
    `thinking_budget` (de Gemini) se ignora."""
    def _call(prompt: str, system_instruction: str | None = None, response_schema: Any = None,
              thinking_budget: int | None = None, description: str | None = None) -> dict:
        return call_json(prompt, model=model, system_instruction=system_instruction, response_schema=response_schema,
                         reasoning_effort=reasoning_effort, description=description, post=post)
    _call.model = model                         # type: ignore[attr-defined]
    _call.reasoning_effort = reasoning_effort   # type: ignore[attr-defined]
    return _call
