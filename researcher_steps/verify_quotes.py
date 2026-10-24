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

F6c (validación del analista, regla nueva): `verify_literal` — se BAJA el documento fuente y se busca la cita LITERAL
(no alcanza el dominio). Un documento vale si su fecha es ≤ evento + 20 años y su texto nombra el lugar o el evento.
La cita se busca tal como está en el pool y, si existe, en su original (inglés) — sin mayúsculas ni tildes, y con
tolerancia al carácter de reemplazo (�) de las copias con la codificación rota. Estados:
    verificada              la cita literal en un documento válido, con el apellido del autor a ≤ 400 caracteres
    encontrada_sin_autor    la cita literal está, pero no junto a ese autor: se usa SIN nombre
    sin_verificar           no está literal en ningún documento válido
`verificacion` = {"estado", "metodo": "literal", "documento", "url_fuente", "fecha_documento", "contexto", "motivo"}.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlparse

PROMPT_VERSION = "f6b3-1"


def build_prompt(q: dict[str, Any], tema: str = "") -> str:
    return f"""Buscá con Google la fuente ORIGINAL de esta cita textual. Está traducida al español; el original
probablemente está en inglés.

CITA: «{q['texto']}»
ATRIBUIDA A: {q.get('autor')}{' (' + q['rol'] + ')' if q.get('rol') else ''}
TEMA: {tema or "(el del video)"}

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
    from script_engine import nombres
    return nombres.es_persona(autor)                                    # F21: alias


def resolve_redirect(url: str, timeout: float = 10.0) -> str | None:
    """URL final de un enlace de redirección de la búsqueda (vertexaisearch…); None si no se puede."""
    import urllib.request
    try:
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.geturl()
    except Exception:  # noqa: BLE001
        return None


# ═══════════════════════════════════════════════════════════════
#  F6c — verificación LITERAL contra el documento fuente
# ═══════════════════════════════════════════════════════════════

FFFD = "\ufffd"
AUTHOR_WINDOW = 400


def _nz(s: str) -> str:
    """Minúsculas, sin tildes (conserva el carácter de reemplazo), comillas/guiones/puntuación → espacio, espacios
    colapsados. Un � pegado a un espacio es puntuación rota (→ espacio); entre letras, una letra rota (queda)."""
    import unicodedata
    t = "".join(c for c in unicodedata.normalize("NFD", str(s or "")) if unicodedata.category(c) != "Mn").lower()
    t = re.sub(rf"[^\w{FFFD}]+", " ", t)
    t = re.sub(rf"(?<!\w){FFFD}+|{FFFD}+(?!\w)", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def _pattern(quote: str) -> re.Pattern | None:
    q = _nz(quote).replace(FFFD, "")
    if len(q.split()) < 3:
        return None
    parts = []
    for ch in q:
        parts.append(r"\s+" if ch == " " else f"(?:{re.escape(ch)}|{FFFD})")
    return re.compile("".join(parts))


def find_literal(quote: str, text: str) -> int | None:
    """Posición de la cita literal en el texto normalizado (None si no está)."""
    pat = _pattern(quote)
    if pat is None:
        return None
    m = pat.search(_nz(text))
    return m.start() if m else None


def doc_ok(doc: dict[str, Any], event_year: int, place_re: str) -> str | None:
    """Motivo por el que el documento NO vale (None si vale): fecha > evento + 20 años, o no nombra el lugar/evento."""
    y = int(str(doc.get("fecha") or "0")[:4] or 0)
    if not y or y > event_year + 20:
        return f"fecha del documento {doc.get('fecha')} > evento + 20 años ({event_year + 20})"
    if not re.search(place_re, doc.get("texto") or "", re.I):
        return "el documento no nombra el lugar ni el evento"
    return None


def verify_literal(pool: dict[str, Any], docs: list[dict[str, Any]], *, event_year: int, place_re: str,
                   ids: list[str] | None = None, log: list[str] | None = None) -> dict[str, int]:
    """In place: `verificacion` literal de las citas testimonio (o de `ids`, también datos). Devuelve el conteo."""
    from researcher_steps.evidence_pool import _person_key
    log = log if log is not None else []
    valid = []
    for d in docs:
        why = doc_ok(d, event_year, place_re)
        if why:
            log.append(f"  [literal] documento {d['id']} descartado: {why}")
        else:
            valid.append({**d, "_nz": _nz(d["texto"])})
    count = {"verificada": 0, "encontrada_sin_autor": 0, "sin_verificar": 0}
    items = [("citas", q) for q in pool.get("citas") or []] + [("datos", x) for x in pool.get("datos") or []]
    for kind, it in items:
        if ids is not None and it["id"] not in ids:
            continue
        if ids is None and not (kind == "citas" and it.get("testimonio")):
            continue
        text = it.get("texto") or ""
        cands = [text] + [x for x in [(it.get("verificacion") or {}).get("cita_original")] if x]
        sur = _person_key(it.get("autor") or "")[1] if kind == "citas" else ""
        best = None
        for d in valid:
            for c in cands:
                k = find_literal(c, d["texto"])
                if k is None:
                    continue
                near = d["_nz"][max(0, k - AUTHOR_WINDOW):k + len(_nz(c)) + AUTHOR_WINDOW]
                ok_author = not sur or re.search(rf"\b{re.escape(sur)}\b", near) is not None
                cand = {"documento": d["id"], "url_fuente": d.get("url"), "fecha_documento": d.get("fecha"),
                        "contexto": d["_nz"][max(0, k - 150):k + len(_nz(c)) + 150], "cita_buscada": c,
                        "autor_cerca": ok_author}
                if best is None or (ok_author and not best["autor_cerca"]):
                    best = cand
        prev = it.get("verificacion") or {}
        if best and best["autor_cerca"]:
            v = {"estado": "verificada", "metodo": "literal", **best, "motivo": f"literal en {best['documento']}"}
        elif best:
            v = {"estado": "encontrada_sin_autor", "metodo": "literal", **best,
                 "motivo": f"literal en {best['documento']}, pero no junto a {it.get('autor')}: va sin nombre"}
        else:
            v = {"estado": "sin_verificar", "metodo": "literal", "documento": None, "url_fuente": None,
                 "motivo": f"no está literal en {[d['id'] for d in valid]}"}
        if prev.get("cita_original"):
            v["cita_original"] = prev["cita_original"]
        it["verificacion"] = v
        count[v["estado"]] += 1
        log.append(f"  [literal] {it['id']} {it.get('autor') or ''}: {v['estado']} — {v['motivo']}")
    for p in pool.get("personajes") or []:
        sur = _person_key(p["nombre"])[1]
        p["testigo_verificado"] = any(
            (q.get("verificacion") or {}).get("estado") == "verificada" and _person_key(q.get("autor") or "")[1] == sur
            for q in pool.get("citas") or [])
    return count


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
                       retry_model: str | None = None, tema: str = "") -> dict[str, int]:
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
            text, chunks = search(build_prompt(q, tema))
            store[key] = {"text": text, "chunks": chunks}
            if cache:
                cache.parent.mkdir(parents=True, exist_ok=True)
                cache.write_text(json.dumps(store, ensure_ascii=False, indent=1), encoding="utf-8")
        v = judge(_parse(store[key]["text"]), store[key]["chunks"])
        named = _named(q.get("autor") or "")
        if v["estado"] != "verificada" and retry_model and named:
            k2 = f"{key}|{retry_model}"
            if k2 not in store:
                store[k2] = dict(zip(("text", "chunks"), search(build_prompt(q, tema), retry_model)))
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
