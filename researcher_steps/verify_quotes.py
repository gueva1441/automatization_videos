"""
researcher_steps/verify_quotes.py — F6b-3: verificación de las citas TESTIMONIO del evidence_pool.

Por cada cita con `testimonio: true`, una búsqueda (Gemini Flash + Google Search) de la cita TEXTUAL (el original
suele estar en inglés: el pool la tiene traducida). La cita queda:
    verificada     el modelo la encontró, atribuida a esa persona, y dio una URL cuyo dominio está entre las fuentes
                   REALES que devolvió la búsqueda (grounding_metadata): la URL no puede salir de la nada
    sin_verificar  todo lo demás (con el motivo)
En el pool: `cita["verificacion"] = {"estado", "url_fuente", "publicacion", "cita_original", "dominios_busqueda",
"motivo"}` y `personaje["testigo_verificado"]` (al menos una cita suya verificada). Regla aguas abajo (escaleta /
guionista): una cita sin_verificar no se usa CON NOMBRE en la narración.
Caché por cita (`cache`): no se vuelve a buscar lo ya buscado.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlparse

PROMPT_VERSION = "f6b3-1"


def build_prompt(q: dict[str, Any]) -> str:
    return f"""Buscá con Google la fuente ORIGINAL de esta cita textual. Está traducida al español; el original
probablemente está en inglés.

CITA: «{q['texto']}»
ATRIBUIDA A: {q.get('autor')}{' (' + q['rol'] + ')' if q.get('rol') else ''}
TEMA: la Prisión Parroquial de Orleans (Orleans Parish Prison) durante el huracán Katrina, 2005.

Respondé SOLO un JSON, sin markdown:
{{"encontrada": true/false, "cita_original": "el texto tal como aparece en la fuente (o vacío)",
  "autor_en_fuente": "a quién se la atribuye la fuente (o vacío)", "publicacion": "medio u organización, año",
  "url": "la URL de la página donde está la cita (o vacío)", "nota": "una línea"}}
encontrada=true SOLO si viste la cita (o una versión casi idéntica) atribuida a esa persona en una página concreta.
Nunca inventes una URL."""


def _domain(u: str) -> str:
    try:
        d = urlparse(u if "://" in u else "https://" + u).netloc.lower()
    except ValueError:
        return ""
    return d[4:] if d.startswith("www.") else d


def _grounding(resp: Any) -> list[dict[str, str]]:
    out = []
    try:
        gm = resp.candidates[0].grounding_metadata
        for ch in (getattr(gm, "grounding_chunks", None) or []):
            w = getattr(ch, "web", None)
            if w:
                out.append({"title": str(getattr(w, "title", "") or ""), "uri": str(getattr(w, "uri", "") or "")})
    except (AttributeError, IndexError, TypeError):
        pass
    return out


def _parse(text: str) -> dict[str, Any]:
    m = re.search(r"\{.*\}", text or "", re.S)
    if not m:
        return {}
    try:
        return json.loads(m.group(0))
    except ValueError:
        return {}


def judge(raw: dict[str, Any], chunks: list[dict[str, str]]) -> dict[str, Any]:
    """Veredicto determinista sobre la respuesta del modelo y las fuentes reales de la búsqueda."""
    doms = sorted({_domain(c["title"]) or c["title"].lower() for c in chunks if c.get("title")})
    url = str(raw.get("url") or "").strip()
    ud = _domain(url) if url else ""
    hit = next((c for c in chunks if url and c.get("uri") == url), None)
    if hit:                                     # el modelo copió el enlace de una fuente de la búsqueda (redirección)
        ud = _domain(hit["title"]) or hit["title"].lower()
    base = {"url_fuente": url or None, "publicacion": raw.get("publicacion") or None,
            "cita_original": raw.get("cita_original") or None, "autor_en_fuente": raw.get("autor_en_fuente") or None,
            "dominios_busqueda": doms}
    if not raw.get("encontrada"):
        return {"estado": "sin_verificar", "motivo": "la búsqueda no encontró la cita", **base}
    if not url:
        return {"estado": "sin_verificar", "motivo": "encontrada sin URL", **base}
    if not any(ud == d or ud.endswith("." + d) or d.endswith("." + ud) for d in doms):
        return {"estado": "sin_verificar", "motivo": f"la URL ({ud}) no está entre las fuentes de la búsqueda {doms}",
                **base}
    return {"estado": "verificada", "motivo": raw.get("nota") or "", **base}


def _named(autor: str) -> bool:
    """¿La cita tiene un autor con nombre propio («Vincent Norman»), no un anónimo («un preso de…»)?"""
    return bool(re.match(r"^[A-ZÁÉÍÓÚÑ][\wáéíóúñ“”\"'.]+\s+[A-ZÁÉÍÓÚÑ“\"]", autor.strip()))


def resolve_redirect(url: str, timeout: float = 10.0) -> str | None:
    """URL final de un enlace de redirección de la búsqueda (vertexaisearch…); None si no se puede."""
    import urllib.request
    try:
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.geturl()
    except Exception:  # noqa: BLE001
        return None


def _search(prompt: str, model: str | None = None) -> tuple[str, list[dict[str, str]]]:
    from google.genai import types

    from config import api, gemini_client
    from cost_tracker import cost_tracker
    model = model or api.gemini_model
    resp = gemini_client.models.generate_content(
        model=model, contents=prompt,
        config=types.GenerateContentConfig(tools=[types.Tool(google_search=types.GoogleSearch())], temperature=0.0))
    cost_tracker.track_gemini_response(resp, model, "verify_quote")
    text = ""
    try:
        text = "".join(p.text for p in resp.candidates[0].content.parts or [] if getattr(p, "text", None))
    except (AttributeError, IndexError, TypeError):
        pass
    return text, _grounding(resp)


def verify_testimonios(pool: dict[str, Any], *, cache: Path | None = None,
                       search: Callable[[str], tuple[str, list[dict[str, str]]]] | None = None,
                       log: list[str] | None = None,
                       resolve: Callable[[str], str | None] | None = resolve_redirect,
                       retry_model: str | None = None) -> dict[str, int]:
    """In place sobre el pool. Devuelve {"verificada": n, "sin_verificar": m}. `retry_model` (p. ej. Pro): segundo
    intento solo para las citas CON NOMBRE que quedaron sin verificar (las anónimas no se nombran igual)."""
    log = log if log is not None else []
    search = search or _search
    store = json.loads(cache.read_text(encoding="utf-8")) if cache and cache.exists() else {}
    count = {"verificada": 0, "sin_verificar": 0}
    for q in pool.get("citas") or []:
        if not q.get("testimonio"):
            continue
        key = f"{PROMPT_VERSION}|{q['texto']}|{q.get('autor')}"
        if key not in store:
            text, chunks = search(build_prompt(q))
            store[key] = {"text": text, "chunks": chunks}
            if cache:
                cache.parent.mkdir(parents=True, exist_ok=True)
                cache.write_text(json.dumps(store, ensure_ascii=False, indent=1), encoding="utf-8")
        v = judge(_parse(store[key]["text"]), store[key]["chunks"])
        named = _named(q.get("autor") or "")
        if v["estado"] != "verificada" and retry_model and named:
            k2 = f"{key}|{retry_model}"
            if k2 not in store:
                store[k2] = dict(zip(("text", "chunks"), search(build_prompt(q), retry_model)))
                if cache:
                    cache.write_text(json.dumps(store, ensure_ascii=False, indent=1), encoding="utf-8")
            v2 = judge(_parse(store[k2]["text"]), store[k2]["chunks"])
            v2["modelo"] = retry_model
            if v2["estado"] == "verificada":
                key, v = k2, v2
            else:
                v["motivo"] += f" · 2.º intento ({retry_model}): {v2['motivo']}"
        if v["estado"] == "verificada" and "vertexaisearch" in (v["url_fuente"] or ""):
            final = store[key].get("url_final")
            if final is None and resolve is not None:
                final = store[key]["url_final"] = resolve(v["url_fuente"]) or ""
                if cache:
                    cache.write_text(json.dumps(store, ensure_ascii=False, indent=1), encoding="utf-8")
            v["url_redireccion"], v["url_fuente"] = v["url_fuente"], final or v["url_fuente"]
        q["verificacion"] = v
        count[v["estado"]] += 1
        log.append(f"  [verificación] {q['id']} {q.get('autor')}: {v['estado']} — {v['motivo'][:90]}"
                   + (f" · {v['url_fuente']}" if v["estado"] == "verificada" else ""))
    from researcher_steps.evidence_pool import _person_key
    for p in pool.get("personajes") or []:
        sur = _person_key(p["nombre"])[1]
        p["testigo_verificado"] = any(
            (q.get("verificacion") or {}).get("estado") == "verificada" and _person_key(q.get("autor") or "")[1] == sur
            for q in pool.get("citas") or [])
    return count
