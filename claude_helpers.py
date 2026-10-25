# claude_helpers.py — F22b: la Messages API de Anthropic con salida JSON, para enchufar Claude en la cadena del guion v4.
# Copia de gpt_helpers.py (misma firma que gemini_helpers.call_pro_json: prompt, system_instruction, response_schema,
# thinking_budget, description → dict), así guion_v4 / m01d / m01c no se enteran del cambio. HTTP directo como
# gpt_helpers (el SDK `anthropic` no está instalado en el venv); header `anthropic-version` 2026-10-21.
#
# La llave se lee de ANTHROPIC_API_KEY (entorno) o de `.env` en la raíz del repo. NUNCA se imprime ni se guarda: los
# errores muestran el código HTTP y el cuerpo de la respuesta, nunca el pedido ni los headers.
# Costo: usage × PRICES (US$ por millón de tokens de entrada / salida; el razonamiento factura como salida y ya viene
# dentro de `output_tokens`) → cost_tracker, como cualquier llamada de Gemini o GPT.
#
# F25a (regla de Omar, docs oficiales de thinking: los tokens de razonamiento cuentan dentro de `max_tokens`, tope
# 128k): toda llamada va con max_tokens 100 000 y en STREAMING (la API lo exige por encima de 21 333); effort `high`
# solo en el guion y `medium` en ficha y escaleta (ESFUERZO_POR_ETAPA, lo usa quien arma el `call`); sin esquema
# forzado cuando la salida pasa de ~20k tokens (SALIDA_GRANDE: JSON libre + el chequeo nuestro de cada paso).

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
TIMEOUT_S = 600                       # por lectura del stream (socket), no por la llamada entera
MAX_TOKENS = 100_000                  # F25a: razonamiento + salida; con streaming (> 21 333 lo exige la API)
ESFUERZO_POR_ETAPA = {"guion": "high", "ficha": "medium", "escaleta": "medium"}
# descripciones de llamadas cuya salida pasa de ~20k tokens: van sin `output_config.format` (la gramática del esquema
# de la ficha es demasiado grande para la API: «The compiled grammar is too large», HTTP 400)
SALIDA_GRANDE = ("ficha_caso",)


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


def leer_stream(lineas) -> dict:
    """F25a: los eventos SSE de una respuesta en streaming → el mismo dict que devuelve la API sin streaming
    (`model`, `content` con los bloques de texto, `stop_reason`, `stop_details`, `usage`). Un evento `error` →
    ClaudeError (los sobrecargados/limitados, como HTTP 529/429, para que `call_json` reintente)."""
    msg: dict[str, Any] = {"content": [], "usage": {}}
    bloques: dict[int, dict] = {}
    evento = None
    for raw in lineas:
        linea = raw.decode("utf-8") if isinstance(raw, bytes) else raw
        linea = linea.rstrip("\r\n")
        if linea.startswith("event:"):
            evento = linea[6:].strip()
            continue
        if not linea.startswith("data:"):
            continue
        d = json.loads(linea[5:].strip() or "{}")
        t = d.get("type") or evento
        if t == "message_start":
            m = d.get("message") or {}
            msg.update({k: v for k, v in m.items() if k not in ("content", "usage")})
            msg["usage"].update(m.get("usage") or {})
        elif t == "content_block_start":
            bloques[d["index"]] = dict(d.get("content_block") or {})
            if bloques[d["index"]].get("type") == "text":
                bloques[d["index"]].setdefault("text", "")
        elif t == "content_block_delta":
            delta, b = d.get("delta") or {}, bloques.setdefault(d["index"], {"type": "text", "text": ""})
            if delta.get("type") == "text_delta":
                b["text"] = (b.get("text") or "") + delta.get("text", "")
        elif t == "message_delta":
            delta = d.get("delta") or {}
            for k in ("stop_reason", "stop_sequence", "stop_details"):
                if k in delta:
                    msg[k] = delta[k]
            msg["usage"].update(d.get("usage") or {})
        elif t == "error":
            err = d.get("error") or {}
            raise _StreamError(err.get("type") or "error", str(err.get("message") or err)[:300])
        elif t == "message_stop":
            break
    msg["content"] = [bloques[i] for i in sorted(bloques)]
    return msg


class _StreamError(ClaudeError):
    def __init__(self, tipo: str, mensaje: str):
        super().__init__(f"stream {tipo}: {mensaje}")
        self.tipo = tipo


def _post(body: dict) -> dict:
    """F25a: siempre en streaming (max_tokens > 21 333 lo exige); devuelve el mensaje armado (`leer_stream`)."""
    req = urllib.request.Request(URL, data=json.dumps({**body, "stream": True}).encode("utf-8"),
                                 headers={"x-api-key": _api_key(), "anthropic-version": API_VERSION,
                                          "content-type": "application/json", "accept": "text/event-stream"})
    with urllib.request.urlopen(req, timeout=TIMEOUT_S) as r:
        return leer_stream(r)


def json_del_texto(txt: str) -> str:
    """F25a: sin esquema forzado, el modelo puede envolver el JSON en ```json … ``` o en una línea de texto: se toma del
    primer «{» al último «}» (si no hay, el texto tal cual, y `json.loads` dice por qué no es JSON)."""
    i, j = txt.find("{"), txt.rfind("}")
    return txt[i:j + 1] if 0 <= i < j else txt


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
    `output_config.format` (json_schema), salvo las descripciones de SALIDA_GRANDE (F25a); sin esquema no se agrega
    formato y se parsea el texto. `effort` va en `output_config.effort` (Opus 5.5 tiene por defecto `medium`). Thinking: el adaptativo por
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
    if response_schema is not None and (description or "") not in SALIDA_GRANDE:     # F25a: salida grande, sin esquema
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
        except _StreamError as e:                         # F25a: error a mitad del stream
            if e.tipo in ("overloaded_error", "rate_limit_error", "api_error"):
                last = str(e)
                time.sleep(2 ** attempt)
                continue
            raise ClaudeError(f"{model}: {e}") from None
        except (urllib.error.URLError, TimeoutError) as e:
            last = f"{type(e).__name__}"
            time.sleep(2 ** attempt)
            continue
        _track(r.get("model") or model, r.get("usage") or {}, desc)
        if r.get("stop_reason") == "refusal":
            raise ClaudeError(f"{model}: {desc}: el modelo se negó ({r.get('stop_details')})")
        txt = "".join(b.get("text") or "" for b in r.get("content") or [] if b.get("type") == "text")
        try:
            return json.loads(txt if oc.get("format") else json_del_texto(txt))
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
