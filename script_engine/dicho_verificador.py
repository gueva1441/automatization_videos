"""
script_engine/dicho_verificador.py — F55 A.2 (DECISIONES 2026-10-29 19:16): segunda opinión del detector con Sonnet 5.5,
solo sobre lo que el código marcó «no dicho» y solo para el `dato_central` que miran los bloqueantes (f) cierre y (h)
pago. `pedido(hecho, oraciones)` es puro; `verificar(hecho, oraciones, *, log, id, cap_md5)` llama al modelo y devuelve el
índice (desde 1) de la oración que dice el hecho, o None. Caché en memoria por (id, md5 del texto del cap) dentro de la
corrida; `estado()` = {"llamadas", "cache", "usd"} para las métricas. Modelo, cliente, effort y precios: los de
m01e_pantalla (claude_helpers).
"""
from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Callable

from script_engine import evidence as ev

MODELO = "claude-sonnet-5-5"        # el mismo de m01e_pantalla.MODELO (DECISIONES 2026-10-29 19:16: Sonnet 5.5)
EFFORT = "medium"                   # el EFFORT de m01e_pantalla
MAX_TOKENS = 2_000                  # salida chica: {"oracion": n, "fragmento": "…"}
REINTENTOS = 1                      # HANDOFF_F55 A.2: error de API, timeout o JSON inválido → None + log, 1 reintento
PREGUNTA = ("¿Alguna de estas oraciones dice este hecho, con las mismas palabras o con otras? Un hecho dicho como "
            "promesa, pregunta o adelanto también cuenta. Respondé con el número de la oración y copiá el fragmento "
            "que lo dice, o null.")
# esquema ya en JSON Schema (minúsculas: `claude_helpers.json_schema` solo baja los `type` que son str, no las listas)
SCHEMA = {"type": "object", "properties": {"oracion": {"type": ["integer", "null"]}, "fragmento": {"type": ["string", "null"]}},
          "required": ["oracion", "fragmento"]}

_cache: dict[tuple[str, str], int | None] = {}
_estado = {"llamadas": 0, "cache": 0, "usd": 0.0}


def pedido(hecho: str, oraciones: list[str]) -> str:
    """Solo el hecho, las oraciones numeradas desde 1 y la pregunta literal. Puro."""
    lineas = "\n".join(f"{k}. {s}" for k, s in enumerate(oraciones, start=1))
    return f"HECHO: {hecho}\n\nORACIONES:\n{lineas}\n\n{PREGUNTA}\nDevolvé JSON: {{\"oracion\": n | null, \"fragmento\": str | null}}"


def cap_md5(oraciones: list[str]) -> str:
    return hashlib.md5("\n".join(oraciones).encode("utf-8")).hexdigest()


def estado() -> dict[str, Any]:
    return {"llamadas": _estado["llamadas"], "cache": _estado["cache"], "usd": round(_estado["usd"], 4)}


def reset() -> None:
    _cache.clear()
    _estado.update(llamadas=0, cache=0, usd=0.0)


def _leer(resp: dict | None, oraciones: list[str]) -> int | None:
    """None si `oracion` está fuera de rango o si `fragmento` normalizado no es subcadena de esa oración."""
    if not isinstance(resp, dict):
        return None
    n, frag = resp.get("oracion"), resp.get("fragmento")
    try:
        n = int(n)
    except (TypeError, ValueError):
        return None
    if not 1 <= n <= len(oraciones) or not frag:
        return None
    return n if ev.norm(str(frag)).strip(" .,;:«»\"") in ev.norm(oraciones[n - 1]) else None


def _llamada(prompt: str, post: Callable[[dict], dict] | None) -> dict | None:
    import claude_helpers as hx
    body = {"model": MODELO, "max_tokens": MAX_TOKENS, "messages": [{"role": "user", "content": prompt}],
            "output_config": {"effort": EFFORT, "format": {"type": "json_schema", "schema": hx.json_schema(SCHEMA)}}}
    r = (post or hx._post)(body)
    u = r.get("usage") or {}
    _estado["usd"] += hx.cost_of(MODELO, u)
    if post is None:
        hx._track(r.get("model") or MODELO, u, "dicho_verificador")
    txt = "".join(c.get("text") or "" for c in r.get("content") or [] if c.get("type") == "text")
    m = re.search(r"\{.*\}", txt, re.S)
    return json.loads(m.group(0)) if m else None


def verificar(hecho: str, oraciones: list[str], *, log: list[str] | None = None, id: str = "", cap_md5_: str | None = None,
              post: Callable[[dict], dict] | None = None) -> int | None:
    """Índice desde 1 de la oración que dice el hecho, o None. Caché por (id, md5 del cap); 1 reintento ante error."""
    log = log if log is not None else []
    clave = (id, cap_md5_ or cap_md5(oraciones))
    if clave in _cache:
        _estado["cache"] += 1
        return _cache[clave]
    out: int | None = None
    for intento in range(REINTENTOS + 1):
        try:
            _estado["llamadas"] += 1
            out = _leer(_llamada(pedido(hecho, oraciones), post), oraciones)
            break
        except Exception as e:  # noqa: BLE001 — API, timeout, JSON roto: None + log, 1 reintento
            log.append(f"  [verificador] {id}: error ({type(e).__name__}: {str(e)[:80]}), intento {intento + 1}")
            out = None
    _cache[clave] = out
    log.append(f"  [verificador] {id}: {'oración ' + str(out) if out else 'no dicho'}")
    return out
