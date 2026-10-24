"""
researcher_steps/research_v3.py — F7: research v3. Leer documentos, no resumir Google.

    seed ─► R1 descubrimiento de fuentes (Pro + Google Search) ─► fuentes.json (url, tipo, año, por qué)
         ─► R2 descarga (HTML/PDF → txt) ─► fuentes/<slug>.<ext> + <slug>.txt + fuentes/manifest.json
         ─► R3 extracción por documento (Pro) ─► pool_doc_<id>.json (cada ítem con doc_id + cita literal + offset)
         ─► R4 merge + dedupe + canon + contaminación ─► evidence_pool (contrato de evidence_pool.py + campos nuevos)
         ─► R5 verificación por texto (gratis) ─► verificada / verificada_parcial / sin_verificar

Reglas (handoff F7 §2–§3):
    url        solo las URLs del grounding de la búsqueda (las fuentes reales que devolvió Google, resueltas desde
               el enlace de redirección). Una URL que el modelo escribió y no está en el grounding se descarta.
    descarga   1 request por URL (+ 1 a la Wayback Machine si falla), UA de navegador con identificador del
               proyecto, sin login ni bypass de paywall; 403/429 se anotan y se sigue. ≤ MAX_DOC_CHARS por
               documento, recortado por secciones (notas/apéndices primero) y nunca a mitad de párrafo.
    extracción solo lo que está en el documento; cada ítem trae `cita_literal` (≤ 300 caracteres, idioma original)
               y el código la busca en el txt (`find_literal`): la que no está, se descarta y se registra.
    pool       mismas claves que hoy (datos, cronologia, lugares, citas, personajes, _descartados,
               cifras_canonicas); lo nuevo es aditivo (doc_id, docs, n_fuentes, cita_literal, offset, idioma,
               texto_original, texto_es, testigo, presente_en, n_citas, n_datos).
F7d: v3 es el default de `topic_researcher._research_seed_deep` para seeds nuevos (`run_seed`); el camino viejo
(4 ángulos resumidos) queda detrás de RESEARCH_V3=0, sin cambios.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import time
import unicodedata
from datetime import date
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlparse

PROMPT_VERSION_R1 = "f7a-1"
TIPOS_FUENTE = ("informe_oficial", "fallo_judicial", "prensa_epoca", "prensa_posterior", "documental", "libro",
                "testimonio", "academico", "foia")
MIN_FUENTES, MAX_FUENTES = 8, 20
MAX_DESCARGAS_OK = 10
MAX_DOC_CHARS = 300_000
MIN_DOC_CHARS = 3_000                    # menos que esto: página vacía, paywall, resumen o portada de un libro
NO_TEXT_SITES = ("youtube.com", "youtu.be", "vimeo.com", "amazon.com", "books.google.com")  # sin texto que leer
EVENT_CHECK_CHARS = 5_000
TIMEOUT_S = 20
USER_AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
              "Chrome/124.0 Safari/537.36 automatization_videos-research/0.7 (documental; 1 request por URL)")


def research_v3_enabled(topic: dict | None = None) -> bool:
    """F7d: v3 es el DEFAULT para seeds nuevos; RESEARCH_V3=0 vuelve al camino viejo (4 ángulos resumidos)."""
    if topic and topic.get("research_version") == 3:
        return True
    return os.environ.get("RESEARCH_V3", "1") != "0"


# ═══════════════════════════════════════════════════════════════
#  URLs y grounding
# ═══════════════════════════════════════════════════════════════

def norm_url(u: str) -> str:
    """URL comparable: sin esquema, sin www, sin barra final, sin fragmento ni parámetros de rastreo."""
    u = str(u or "").strip()
    if not u:
        return ""
    p = urlparse(u if "://" in u else "https://" + u)
    host = p.netloc.lower()
    host = host[4:] if host.startswith("www.") else host
    q = "&".join(x for x in p.query.split("&") if x and not x.lower().startswith(("utm_", "fbclid", "gclid")))
    path = re.sub(r"/+$", "", p.path)
    return host + path + (("?" + q) if q else "")


def domain(u: str) -> str:
    return norm_url(u).split("/")[0]


def grounding_urls(chunks: list[dict[str, str]], resolve: Callable[[str], str | None] | None) -> list[dict[str, str]]:
    """Fuentes reales de la búsqueda: [{"title", "uri", "url"}] con `url` = destino final de la redirección."""
    out, seen = [], set()
    for c in chunks:
        uri = c.get("uri") or ""
        final = uri
        if resolve is not None and "vertexaisearch" in uri:
            final = resolve(uri) or ""
        if not final or "vertexaisearch" in final:
            continue
        k = norm_url(final)
        if k in seen:
            continue
        seen.add(k)
        out.append({"title": c.get("title") or "", "uri": uri, "url": final})
    return out


# ═══════════════════════════════════════════════════════════════
#  R1 — descubrimiento de fuentes
# ═══════════════════════════════════════════════════════════════

def build_discovery_prompt(seed: dict, foco: str, pistas: list[str] | None = None) -> str:
    lugar = seed.get("lugar_idioma") or "el idioma del lugar donde ocurrió el evento"
    pistas_txt = ""
    if pistas:
        pistas_txt = ("\nDOCUMENTOS QUE SABEMOS QUE EXISTEN (buscá la página o el PDF de cada uno; si no lo encontrás, "
                      "no lo pongas):\n" + "\n".join(f"- {p}" for p in pistas) + "\n")
    return f"""Sos un documentalista. Tu trabajo es encontrar DOCUMENTOS que se puedan leer completos, no resumir hechos.

TEMA: "{seed['seed_title']}"
FOCO DE ESTA BÚSQUEDA: {foco}

Buscá con Google en INGLÉS y en {lugar}. Quiero las páginas o PDFs PRIMARIOS donde está la información:
informe oficial o de ONG (texto completo), fallo o expediente judicial, prensa local de los días del evento,
prensa de aniversario o seguimiento, documental o transcripción, libro o capítulo, historia oral o testimonios,
FOIA o archivo. Preferí el documento original sobre una nota que lo resume.
{pistas_txt}
REGLAS:
- Cada URL tiene que ser una página que viste en la búsqueda. Nunca inventes ni completes una URL.
- Entre {MIN_FUENTES} y {MAX_FUENTES} fuentes, sin repetir la misma página.
- prioridad: 1 = imprescindible (texto primario largo, con testimonios o cifras oficiales), 2 = útil, 3 = complemento.

Respondé SOLO un JSON, sin markdown:
{{"fuentes":[{{"url":"…","titulo":"…","tipo":"{'|'.join(TIPOS_FUENTE)}","anio":2006,"idioma":"en","por_que":"una línea: qué tiene que no tengan las otras","prioridad":1}}]}}"""


DISCOVERY_FOCOS = (
    "informes completos (oficiales y de ONG) e historia oral: testimonios con nombre de las personas que estuvieron "
    "ahí, cartas, declaraciones juradas.",
    "fallos, demandas y expedientes judiciales; cartas e informes del gobierno (PDF); FOIA y archivos.",
    "prensa local y de agencias de los días del evento (la primera semana), con testigos y horas.",
    "prensa de aniversario y seguimiento, documentales o transcripciones, libros o capítulos, trabajos académicos.",
)
# páginas de listado (categorías, etiquetas, búsquedas): no son documentos
_LISTING = re.compile(r"/(category|categories|tag|tags|topics?|search|author|page/\d+)(/|$)", re.I)
_PATH_STOP = {"www", "html", "htm", "php", "aspx", "news", "article", "articles", "story", "en", "es", "the", "and",
              "of", "in", "to", "for", "a", "on", "pdf", "sites", "default", "files", "publications", "report",
              "reports", "documents", "other", "media", "doc", "details"}


R1_TEMPERATURE = 0.7                     # como el research viejo: con 0.0, Pro contestó de memoria sin buscar


def search_pro(prompt: str) -> tuple[str, list[dict[str, str]]]:
    """Pro + Google Search → (texto, chunks del grounding)."""
    from google.genai import types

    from config import api, gemini_client
    from cost_tracker import cost_tracker
    from researcher_steps.verify_quotes import _grounding
    model = api.gemini_model_research
    resp = gemini_client.models.generate_content(
        model=model, contents=prompt,
        config=types.GenerateContentConfig(tools=[types.Tool(google_search=types.GoogleSearch())],
                                           temperature=R1_TEMPERATURE))
    cost_tracker.track_gemini_response(resp, model, "R1 descubrimiento")
    text = ""
    try:
        text = "".join(p.text for p in resp.candidates[0].content.parts or [] if getattr(p, "text", None))
    except (AttributeError, IndexError, TypeError):
        pass
    return text, _grounding(resp)


R1_RETRIES = 3                           # F8b: 3 reintentos (antes 2) con la misma temperatura 0.7
R1_FORCE_SEARCH = ("\n\nIMPORTANTE: no respondas de memoria. Hacé ahora varias búsquedas en Google (una por tipo de "
                   "documento) y listá solo páginas que aparezcan en esos resultados.")


def search_flash(prompt: str) -> tuple[str, list[dict[str, str]]]:
    """F8b: Flash + Google Search → (texto, chunks del grounding): la búsqueda alternativa cuando Pro no busca."""
    from google.genai import types

    from config import api, gemini_client
    from cost_tracker import cost_tracker
    from researcher_steps.verify_quotes import _grounding
    model = api.gemini_model
    resp = gemini_client.models.generate_content(
        model=model, contents=prompt,
        config=types.GenerateContentConfig(tools=[types.Tool(google_search=types.GoogleSearch())],
                                           temperature=R1_TEMPERATURE))
    cost_tracker.track_gemini_response(resp, model, "R1 descubrimiento (Flash)")
    text = ""
    try:
        text = "".join(p.text for p in resp.candidates[0].content.parts or [] if getattr(p, "text", None))
    except (AttributeError, IndexError, TypeError):
        pass
    return text, _grounding(resp)


def build_alt_prompt(seed: dict, foco: str) -> str:
    """F8b: query corta para Flash + búsqueda, con las palabras clave del seed en el idioma local."""
    names = [n for n in seed.get("nombres_lugar") or [] if n] or [seed["seed_title"]]
    lugar = seed.get("lugar_idioma") or "el idioma del lugar"
    return f"""Buscá en Google, en {lugar} y en inglés, con estas palabras clave: {" · ".join(f'"{n}"' for n in names[:6])}.
Qué busco: {foco}
Listá SOLO páginas que aparezcan en los resultados de la búsqueda (nunca inventes ni completes una URL), entre 5 y 12.
Respondé SOLO un JSON, sin markdown:
{{"fuentes":[{{"url":"…","titulo":"…","tipo":"{'|'.join(TIPOS_FUENTE)}","anio":2006,"idioma":"it","por_que":"una línea","prioridad":1}}]}}"""


def _parse_json(text: str) -> dict[str, Any]:
    m = re.search(r"\{.*\}", text or "", re.S)
    if not m:
        return {}
    try:
        return json.loads(m.group(0))
    except ValueError:
        return {}


def _site(u: str) -> str:
    """Dominio registrable aproximado (las dos últimas etiquetas): www.aclu.org y aclu.org son el mismo sitio."""
    return ".".join(domain(u).split(".")[-2:])


def _path_tokens(u: str) -> set[str]:
    path = norm_url(u)[len(domain(u)):]
    return {t for t in re.findall(r"[a-z0-9]+", path.lower()) if len(t) >= 3 and t not in _PATH_STOP}


def url_similarity(a: str, b: str) -> float:
    """1.0 = la misma URL; si no, solapamiento de las palabras de la ruta dentro del mismo sitio (0 si otro sitio)."""
    if norm_url(a) == norm_url(b):
        return 1.0
    if _site(a) != _site(b):
        return 0.0
    ta, tb = _path_tokens(a), _path_tokens(b)
    return len(ta & tb) / min(len(ta), len(tb)) if ta and tb else 0.0


SIMILAR_MIN = 0.5


def year_in_url(u: str) -> int | None:
    """El año de la ruta (/2005/09/21/…), que manda sobre el de la ficha; None si no hay."""
    m = re.search(r"/((?:19|20)\d\d)/", urlparse(u).path)
    return int(m.group(1)) if m else None


def match_grounding(fuentes: list[dict], ground: list[dict[str, str]]) -> tuple[list[dict], list[dict], list[dict]]:
    """Los CANDIDATOS son las URLs del grounding (las páginas que la búsqueda vio de verdad); el modelo solo aporta la
    ficha (tipo, año, título, por qué, prioridad) de la que más se le parece (misma URL, o mismo sitio y ≥ SIMILAR_MIN
    de las palabras de la ruta). Devuelve (con ficha, sin ficha, fichas del modelo sin URL del grounding)."""
    ground = [g for g in ground if not _LISTING.search(urlparse(g["url"]).path)]
    by_uri = {g["uri"]: g for g in ground}
    used: set[int] = set()
    ok = []
    for i, f in enumerate(fuentes):
        url = str(f.get("url") or "").strip()
        g = by_uri.get(url)
        score = 1.0 if g else 0.0
        if g is None:
            best = max(ground, key=lambda g: url_similarity(url, g["url"]), default=None)
            score = url_similarity(url, best["url"]) if best else 0.0
            g = best if score >= SIMILAR_MIN else None
        if g is None:
            continue
        used.add(i)
        ok.append({**f, "url": g["url"], "url_modelo": url, "match": "exacta" if score == 1.0 else f"similar {score:.2f}",
                   "grounding_title": g["title"], "anio": year_in_url(g["url"]) or f.get("anio")})
    bad = [{**f, "motivo": "ninguna URL del grounding se le parece"} for i, f in enumerate(fuentes) if i not in used]
    have = {norm_url(f["url"]) for f in ok}
    rest = [g for g in ground if norm_url(g["url"]) not in have]
    return ok, rest, bad


ANNOTATE_SCHEMA: dict[str, Any] = {"type": "OBJECT", "properties": {"fuentes": {"type": "ARRAY", "items": {
    "type": "OBJECT", "properties": {
        "url": {"type": "STRING"}, "relevante": {"type": "BOOLEAN"}, "titulo": {"type": "STRING"},
        "tipo": {"type": "STRING", "enum": list(TIPOS_FUENTE)}, "anio": {"type": "INTEGER"},
        "idioma": {"type": "STRING"}, "por_que": {"type": "STRING"}, "prioridad": {"type": "INTEGER"}},
    "required": ["url", "relevante", "tipo", "prioridad"]}}}, "required": ["fuentes"]}


def annotate_unmatched(seed: dict, rest: list[dict], notes: str, *, call: Callable[..., dict] | None = None) -> list[dict]:
    """Ficha para las URLs del grounding que el modelo no listó: 1 Flash sin búsqueda, solo con la URL, el sitio y lo
    que el modelo escribió en la búsqueda. Las que no son del tema (relevante=false) quedan fuera."""
    if not rest:
        return []
    if call is None:
        from gemini_helpers import call_flash_json as call
    lista = "\n".join(f"- {g['url']} (sitio: {g['title']})" for g in rest)
    prompt = f"""TEMA: "{seed['seed_title']}"
Estas páginas salieron en una búsqueda sobre el tema. Para cada una, deducí de la URL y de las notas de la búsqueda qué
documento es. relevante=false si es una portada genérica, un listado o algo de otro tema. No inventes: si no sabés el
año, 0. prioridad 1 = documento primario largo, 2 = útil, 3 = complemento.

URLS:
{lista}

NOTAS DE LA BÚSQUEDA:
{notes[:6000]}"""
    raw = call(prompt, response_schema=ANNOTATE_SCHEMA, description="R1 fichas del grounding") or {}
    by = {norm_url(g["url"]): g for g in rest}
    out = []
    for f in raw.get("fuentes") or []:
        g = by.get(norm_url(f.get("url") or ""))
        if g is None or not f.get("relevante"):
            continue
        c = _clean_fuente({**f, "url": g["url"]})
        c["anio"] = c["anio"] or None
        out.append({**c, "url_modelo": None, "match": "ficha_flash", "grounding_title": g["title"]})
    return out


def _clean_fuente(f: dict) -> dict:
    tipo = str(f.get("tipo") or "").strip()
    try:
        anio = int(str(f.get("anio") or "")[:4])
    except ValueError:
        anio = None
    try:
        prio = int(f.get("prioridad") or 3)
    except (TypeError, ValueError):
        prio = 3
    return {"url": str(f.get("url") or "").strip(), "titulo": str(f.get("titulo") or "").strip(),
            "tipo": tipo if tipo in TIPOS_FUENTE else "prensa_posterior", "anio": anio,
            "idioma": str(f.get("idioma") or "").strip()[:5] or None, "por_que": str(f.get("por_que") or "").strip(),
            "prioridad": max(1, min(3, prio))}


def build_pista_prompt(seed: dict, pista: str) -> str:
    return f"""Buscá con Google la página o el PDF de ESTE documento (tema: "{seed['seed_title']}"):

{pista}

Si encontrás el original y también copias o notas que lo reproducen completo, listalas también (la original primero).
Nunca inventes ni completes una URL: solo páginas que aparezcan en los resultados de la búsqueda.

Respondé SOLO un JSON, sin markdown:
{{"fuentes":[{{"url":"…","titulo":"…","tipo":"{'|'.join(TIPOS_FUENTE)}","anio":2006,"idioma":"en","por_que":"una línea","prioridad":1}}]}}"""


def _words(s: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9]+", _ascii(s).lower()) if len(w) >= 4} - {"orleans", "parish", "prison",
                                                                                         "katrina", "hurricane"}


def pista_covered(pista: str, f: dict) -> bool:
    """¿La fuente (con URL del grounding) es el documento de la pista? ≥ 50 % de las palabras distintivas del título."""
    a, b = _words(f.get("titulo") or ""), _words(pista)
    return bool(a and b) and len(a & b) / min(len(a), len(b)) >= 0.5


def _dedupe_ground(ground: list[dict]) -> list[dict]:
    seen: set[str] = set()
    return [g for g in ground if not (norm_url(g["url"]) in seen or seen.add(norm_url(g["url"])))]


def discover_sources(seed: dict, *, search: Callable[[str], tuple[str, list[dict]]] | None = None,
                     resolve: Callable[[str], str | None] | None = None, pistas: list[str] | None = None,
                     cache: Path | None = None, log: list[str] | None = None,
                     annotate: Callable[..., dict] | None = None,
                     search_alt: Callable[[str], tuple[str, list[dict]]] | None = None) -> dict[str, Any]:
    """R1: 1 llamada Pro + Google Search por foco (DISCOVERY_FOCOS) + 1 Flash para la ficha de las URLs del grounding
    que el modelo no listó. Devuelve {"fuentes": [...], "_descartadas": [...], "_grounding": [...],
    "prompt_version"}; caché por prompt."""
    from researcher_steps.verify_quotes import resolve_redirect
    log = log if log is not None else []
    resolve = resolve if resolve is not None else resolve_redirect
    search = search or search_pro
    search_alt = search_alt or search_flash
    store = json.loads(cache.read_text(encoding="utf-8")) if cache and cache.exists() else {}
    fuentes, ground_all, notes = [], [], []
    focos_grounding = {"pro": 0, "flash": 0, "sin": 0}       # F8b: cuántos focos salieron con grounding y por qué vía

    def _save() -> None:
        if cache:
            cache.parent.mkdir(parents=True, exist_ok=True)
            cache.write_text(json.dumps(store, ensure_ascii=False, indent=1), encoding="utf-8")

    def _run(prompt: str, label: str, alt_prompt: str | None = None) -> None:
        key = f"{PROMPT_VERSION_R1}|" + hashlib.sha1(prompt.encode("utf-8")).hexdigest()[:16]
        if key not in store or not store[key]["chunks"]:
            text, chunks = search(prompt)
            for _ in range(R1_RETRIES):                 # sin grounding = respondió de memoria: no sirve
                if chunks:
                    break
                log.append(f"  [R1] {label}: sin grounding (de memoria) → reintento")
                text, chunks = search(prompt + R1_FORCE_SEARCH)
            via = "pro"
            if not chunks and alt_prompt:               # F8b: Flash + búsqueda con las palabras clave del seed
                log.append(f"  [R1] {label}: Pro sin grounding tras {R1_RETRIES} reintentos → Flash con búsqueda")
                text, chunks = search_alt(alt_prompt)
                via = "flash"
            store[key] = {"text": text, "chunks": chunks, "via": via if chunks else "sin"}
            _save()
        entry = store[key]
        if label.startswith("foco"):
            focos_grounding[entry.get("via") or ("pro" if entry["chunks"] else "sin")] += 1
        if "ground" not in entry:
            entry["ground"] = grounding_urls(entry["chunks"], resolve)
            _save()
        raw = [_clean_fuente(f) for f in (_parse_json(entry["text"]).get("fuentes") or []) if isinstance(f, dict)]
        fuentes.extend(raw)
        ground_all.extend(entry["ground"])
        notes.append(entry["text"] or "")
        log.append(f"  [R1] {label}: {len(raw)} fichas del modelo, {len(entry['ground'])} URLs en el grounding")

    for n, foco in enumerate(DISCOVERY_FOCOS, start=1):
        _run(build_discovery_prompt(seed, foco, pistas), f"foco {n}", build_alt_prompt(seed, foco))
    log.append(f"  [R1] focos con grounding: {focos_grounding['pro']} por Pro, {focos_grounding['flash']} por Flash, "
               f"{focos_grounding['sin']} sin grounding (de {len(DISCOVERY_FOCOS)})")
    # una búsqueda por cada pista del analista que los focos no trajeron (con URL del grounding)
    for p in pistas or []:
        ok_now, _, _ = match_grounding(fuentes, _dedupe_ground(ground_all))
        if not any(pista_covered(p, f) for f in ok_now):
            _run(build_pista_prompt(seed, p), f"pista «{p[:50]}»")
    ground_all[:] = _dedupe_ground(ground_all)
    ok, rest, descartadas = match_grounding(fuentes, ground_all)
    akey = "annotate|" + hashlib.sha1("|".join(sorted(norm_url(g["url"]) for g in rest)).encode()).hexdigest()[:16]
    if akey not in store:
        store[akey] = annotate_unmatched(seed, rest, "\n".join(notes), call=annotate)
        _save()
    flash = store[akey]
    log.append(f"  [R1] {len(ground_all)} URLs reales: {len(ok)} con ficha del modelo, {len(flash)} con ficha de "
               f"Flash, {len(rest) - len(flash)} fuera (no relevantes o listados) · {len(descartadas)} fichas del "
               f"modelo sin URL del grounding")
    fuentes = ok + flash
    out, seen = [], set()
    for f in sorted(fuentes, key=lambda f: f["prioridad"]):
        k = norm_url(f["url"])
        if k in seen:
            continue
        seen.add(k)
        out.append(f)
    out = out[:MAX_FUENTES]
    for i, f in enumerate(out, start=1):
        f["id"] = f"F{i:02d}"
        f["slug"] = slugify(f)
    return {"fuentes": out, "_descartadas": descartadas, "_grounding": ground_all, "prompt_version": PROMPT_VERSION_R1,
            "_focos_grounding": focos_grounding}


def slugify(f: dict) -> str:
    base = f"{domain(f['url']).split('.')[-2] if '.' in domain(f['url']) else domain(f['url'])}_{f.get('anio') or ''}_"
    words = re.findall(r"[a-z0-9]+", _ascii(f.get("titulo") or "").lower())
    s = base + "_".join(words[:5])
    return re.sub(r"_+", "_", s).strip("_")[:60]


def _ascii(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


# ═══════════════════════════════════════════════════════════════
#  R2 — descarga y texto
# ═══════════════════════════════════════════════════════════════

_STOP = {
    "en": {"the", "and", "of", "to", "was", "were", "in", "that", "with", "they", "for"},
    "es": {"el", "la", "de", "que", "los", "las", "en", "y", "fue", "con", "por"},
    "fr": {"le", "la", "les", "des", "et", "est", "dans", "une", "que", "pour"},
    "it": {"il", "di", "che", "della", "delle", "degli", "sono", "nel", "gli", "anche", "questo"},   # F8 (Vajont)
}


def detect_lang(text: str) -> str:
    toks = re.findall(r"[a-záéíóúñèàç]+", text[:20000].lower())
    score = {k: sum(1 for t in toks if t in v) for k, v in _STOP.items()}
    best = max(score, key=score.get)
    return best if score[best] else "?"


def html_to_text(raw: bytes) -> str:
    s = raw.decode("utf-8", errors="replace")
    try:
        import trafilatura
        t = trafilatura.extract(s, include_comments=False, include_tables=True, favor_recall=True)
        if t and len(t) >= MIN_DOC_CHARS:
            return t
    except Exception:  # noqa: BLE001
        pass
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(s, "html.parser")
    for tag in soup(["script", "style", "nav", "header", "footer", "aside", "form"]):
        tag.decompose()
    t = soup.get_text("\n")
    return re.sub(r"\n\s*\n+", "\n\n", re.sub(r"[ \t]+", " ", t)).strip()


def _page_text(page: Any) -> str:
    """Texto de una página; si es a dos columnas (un canal vertical que casi ninguna palabra cruza), primero la
    columna izquierda y después la derecha (pdfplumber solo intercalaría las líneas de las dos)."""
    page = page.filter(lambda o: o.get("object_type") != "char" or o.get("upright", True))   # fuera el texto girado
    words = page.extract_words() or []
    w = float(page.width)
    if len(words) < 40:
        return page.extract_text() or ""
    best = None
    for x in range(int(w * 0.35), int(w * 0.65), 2):
        cross = sum(1 for t in words if t["x0"] < x - 1 and t["x1"] > x + 1)
        if best is None or cross < best[1]:
            best = (x, cross)
    x, cross = best
    left = sum(1 for t in words if t["x1"] <= x)
    right = sum(1 for t in words if t["x0"] >= x)
    if cross > 0.03 * len(words) or min(left, right) < 0.2 * len(words):
        return page.extract_text() or ""
    # letras SUELTAS en el canal (un rótulo vertical, letra por letra) no son de ninguna columna: fuera
    lx = sorted(t["x1"] for t in words if t["x1"] <= x)
    rx = sorted(t["x0"] for t in words if t["x0"] >= x)
    l_edge, r_edge = lx[int(len(lx) * 0.9)], rx[int(len(rx) * 0.05)]
    stray = {(round(t["x0"], 1), round(t["top"], 1)) for t in words
             if len(t["text"]) == 1 and t["x0"] >= l_edge - 2 and t["x1"] <= r_edge + 2}
    if stray:
        page = page.filter(lambda o: o.get("object_type") != "char"
                           or (round(o["x0"], 1), round(o["top"], 1)) not in stray)
    h = float(page.height)
    return ((page.crop((0, 0, x, h)).extract_text() or "") + "\n"
            + (page.crop((x, 0, w, h)).extract_text() or ""))


def _pdftotext(path: Path) -> str | None:
    """poppler `pdftotext` (orden de lectura por bloques: columnas, recuadros y rótulos bien) si está instalado."""
    import shutil
    import subprocess
    exe = shutil.which("pdftotext")
    if not exe:
        return None
    try:
        r = subprocess.run([exe, "-enc", "UTF-8", str(path), "-"], capture_output=True, timeout=120)
    except (OSError, subprocess.SubprocessError):
        return None
    t = r.stdout.decode("utf-8", errors="replace").replace("\x0c", "\n\n") if r.returncode == 0 else ""
    return t if len(t.strip()) >= MIN_DOC_CHARS else None


def pdf_to_text(path: Path) -> str:
    """PDF → texto: pdftotext si está; si no, pdfplumber por columnas; si no, pypdf. Siempre con `dehyphenate`."""
    t = _pdftotext(path)
    if t:
        return dehyphenate(t)
    try:
        import pdfplumber
        with pdfplumber.open(str(path)) as pdf:
            pages = [_page_text(p) for p in pdf.pages]
        t = "\n\n".join(pages)
        if len(t.strip()) >= MIN_DOC_CHARS:
            return dehyphenate(t)
    except Exception:  # noqa: BLE001
        pass
    from pypdf import PdfReader
    t = "\n\n".join((p.extract_text() or "") for p in PdfReader(str(path)).pages)
    return dehyphenate(t)


def dehyphenate(t: str) -> str:
    """Une las palabras cortadas al final de línea («concen-\\ntration» → «concentration») y saca las llamadas a nota
    pegadas al texto («prisoners.11This», «OPP,17$2.00», «charges,14»): 1–3 dígitos justo después de una letra (o de
    letra + puntuación) y antes de un espacio, una mayúscula, «$» o una comilla. Una cifra («$24.39», «1,300») no
    entra: delante tiene un dígito o un espacio."""
    t = re.sub(r"(\w)-\n(\w)", r"\1\2", t)
    return re.sub(r"(?<=[A-Za-z][.,;:])\d{1,3}(?=\s|[A-Z$“\"])|(?<=[A-Za-z”’)])\d{1,3}(?=\s|[A-Z$“\"])", "", t)


_TAIL_HEAD = re.compile(r"^\s*(end ?notes|notes|appendix|appendices|references|bibliography|sources|footnotes)\b.{0,40}$",
                        re.I | re.M)


def cap_text(text: str, limit: int = MAX_DOC_CHARS) -> tuple[str, str | None]:
    """≤ limit caracteres, por secciones: primero se va la cola de notas/apéndices (un título así en la segunda
    mitad); si todavía sobra, se corta en el último fin de párrafo antes del límite. Devuelve (texto, motivo)."""
    if len(text) <= limit:
        return text, None
    motivo = []
    heads = [m for m in _TAIL_HEAD.finditer(text) if m.start() > len(text) // 2]
    if heads:
        cut = heads[0].start()
        motivo.append(f"fuera la cola desde «{heads[0].group(0).strip()[:40]}» ({len(text) - cut} caracteres)")
        text = text[:cut]
    if len(text) > limit:
        cut = text.rfind("\n\n", 0, limit)
        cut = cut if cut > limit // 2 else text.rfind("\n", 0, limit)
        cut = cut if cut > limit // 2 else limit
        motivo.append(f"cortado en el último párrafo antes de {limit} ({len(text) - cut} caracteres fuera)")
        text = text[:cut]
    return text.rstrip(), "; ".join(motivo)


def names_event(text: str, place_re: str, titulo: str = "") -> bool:
    """¿El documento nombra el lugar o el evento en su título o en sus primeros EVENT_CHECK_CHARS caracteres?"""
    return bool(re.search(place_re, titulo or "", re.I) or re.search(place_re, text[:EVENT_CHECK_CHARS], re.I))


def _http_get(url: str) -> tuple[int, bytes, str, str]:
    """(status, contenido, content-type, url final). Un solo request, sin reintentos."""
    import requests
    r = requests.get(url, headers={"User-Agent": USER_AGENT, "Accept-Language": "en,es;q=0.8"}, timeout=TIMEOUT_S,
                     allow_redirects=True)
    return r.status_code, r.content, r.headers.get("content-type", ""), r.url


def _is_pdf(content: bytes, ctype: str, url: str) -> bool:
    return content[:5] == b"%PDF-" or "pdf" in ctype.lower() or url.lower().split("?")[0].endswith(".pdf")


WAYBACK_API = "https://archive.org/wayback/available"
WAYBACK_PAUSE_S = 3.0


def wayback_snapshot(url: str, year: int | None, get: Callable) -> str | None:
    """La copia más cercana en la Wayback Machine (API de disponibilidad, 1 request), en modo crudo (`id_`: sin la
    barra de la Wayback). None si no hay copia."""
    time.sleep(WAYBACK_PAUSE_S)
    from urllib.parse import quote
    status, content, _, _ = get(f"{WAYBACK_API}?url={quote(url, safe='')}&timestamp={year or 2006}0901")
    if status != 200:
        raise RuntimeError(f"HTTP {status} de la API de disponibilidad")
    try:
        snap = json.loads(content.decode("utf-8")).get("archived_snapshots", {}).get("closest") or {}
    except ValueError:
        return None
    if not snap.get("available") or not snap.get("url"):
        return None
    time.sleep(WAYBACK_PAUSE_S)
    return re.sub(r"/web/(\d{14})/", r"/web/\1id_/", snap["url"], count=1)


PDF_LINK_MAX_TEXT = 6_000                # una portada con menos texto que esto y un PDF del mismo sitio: se baja el PDF


def linked_pdf(html: bytes, page_url: str) -> str | None:
    """El primer enlace a PDF del mismo sitio en una página (portada de un informe). None si no hay."""
    from urllib.parse import urljoin
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html.decode("utf-8", errors="replace"), "html.parser")
    for a in soup.find_all("a", href=True):
        u = urljoin(page_url, a["href"])
        if u.lower().split("?")[0].endswith(".pdf") and _site(u) == _site(page_url):
            return u
    return None


def download_sources(fuentes: list[dict], dest: Path, *, place_re: str, get: Callable[[str], tuple] | None = None,
                     local: dict[str, Path] | None = None, max_ok: int = MAX_DESCARGAS_OK, wayback: bool = True,
                     log: list[str] | None = None) -> dict[str, Any]:
    """R2: baja por prioridad hasta `max_ok` documentos OK. `local` = {url_normalizada: archivo ya bajado} (no se
    vuelve a pedir). Deja dest/<slug>.<ext>, dest/<slug>.txt y dest/manifest.json; devuelve el manifest."""
    log = log if log is not None else []
    get = get or _http_get
    dest.mkdir(parents=True, exist_ok=True)
    man_path = dest / "manifest.json"
    prev = {}
    if man_path.exists():
        try:
            prev = {d["url"]: d for d in json.loads(man_path.read_text(encoding="utf-8"))["documentos"]}
        except (OSError, ValueError, KeyError):
            prev = {}
    docs, n_ok = [], 0
    for f in sorted(fuentes, key=lambda f: (f["prioridad"], f["id"])):
        if n_ok >= max_ok:
            docs.append({**_meta(f), "ok": False, "estado": "no_intentada", "motivo": f"ya hay {max_ok} documentos"})
            continue
        p = prev.get(f["url"])
        if any(_site(f["url"]) == s or domain(f["url"]).endswith(s) for s in NO_TEXT_SITES):
            docs.append({**_meta(f), "ok": False, "estado": "sin_texto", "intentos": [],
                         "motivo": "video o tienda: no hay texto que bajar"})
            continue
        if p and p.get("ok") and (dest / p["txt"]).exists() and p.get("caracteres", 0) >= MIN_DOC_CHARS:
            d = {**p, **_meta(f)}                       # ya bajado: no se vuelve a pedir (ids nuevos, mismo archivo)
        elif p and p.get("ok"):                         # bajado antes, pero corto para el mínimo de ahora
            d = {**p, **_meta(f), "ok": False, "estado": "error",
                 "motivo": f"texto de {p.get('caracteres')} caracteres (< {MIN_DOC_CHARS}: resumen o portada)"}
        else:
            d = _fetch_one(f, dest, place_re=place_re, get=get, local=local or {}, wayback=wayback, log=log)
        twin = next((x for x in docs if d["ok"] and x.get("ok") and same_document(dest, x, d)), None)
        if twin is not None:                            # el mismo documento desde otra página (portada → mismo PDF)
            d.update({"ok": False, "estado": "duplicado", "motivo": f"mismo documento que {twin['id']}"})
            log.append(f"  [R2] {f['id']}: duplicado de {twin['id']}")
        docs.append(d)
        n_ok += int(bool(d["ok"] and d.get("nombra_evento")))   # uno que no nombra el evento no ocupa cupo
    man = {"generado": date.today().isoformat(), "place_re": place_re, "max_doc_chars": MAX_DOC_CHARS,
           "documentos": docs}
    man_path.write_text(json.dumps(man, ensure_ascii=False, indent=1), encoding="utf-8")
    log.append(f"  [R2] {n_ok} documentos OK de {sum(1 for d in docs if d['estado'] != 'no_intentada')} intentados")
    return man


def rebuild_texts(man: dict, dest: Path, place_re: str, ids: list[str] | None = None,
                  log: list[str] | None = None) -> dict:
    """Rehace el txt de los PDF ya bajados (sin pedir nada a la red) con la extracción actual. In place."""
    log = log if log is not None else []
    for d in man["documentos"]:
        if not d.get("ok") or not str(d.get("archivo") or "").endswith(".pdf") or (ids and d["id"] not in ids):
            continue
        text = re.sub(r"[ \t]+\n", "\n", pdf_to_text(dest / d["archivo"])).strip()
        full = len(text)
        text, recorte = cap_text(text)
        (dest / d["txt"]).write_text(text, encoding="utf-8")
        d.update({"caracteres": len(text), "caracteres_total": full, "recorte": recorte,
                  "nombra_evento": names_event(text, place_re, d.get("titulo") or "")})
        log.append(f"  [R2] {d['id']}: txt rehecho ({len(text)} caracteres)")
    return man


FICHA_HEAD_CHARS = 2_500
FICHA_SCHEMA: dict[str, Any] = {"type": "OBJECT", "properties": {"documentos": {"type": "ARRAY", "items": {
    "type": "OBJECT", "properties": {
        "id": {"type": "STRING"}, "titulo": {"type": "STRING"}, "autor": {"type": "STRING"},
        "tipo": {"type": "STRING", "enum": list(TIPOS_FUENTE)}, "anio": {"type": "INTEGER"}},
    "required": ["id", "titulo", "tipo", "anio"]}}}, "required": ["documentos"]}


def refine_fichas(man: dict, dest: Path, seed: dict, *, call: Callable[..., dict] | None = None,
                  log: list[str] | None = None) -> dict:
    """La ficha (título, autor, tipo, año) leída del ENCABEZADO de cada documento bajado (1 Flash para todos): la de
    la búsqueda es una conjetura sobre la URL. La de la búsqueda queda en `ficha_busqueda`. In place + devuelve man."""
    log = log if log is not None else []
    docs = [d for d in man["documentos"] if d.get("ok")]
    heads = {d["id"]: (dest / d["txt"]).read_text(encoding="utf-8")[:FICHA_HEAD_CHARS] for d in docs}
    h = hashlib.sha1(json.dumps(heads, sort_keys=True).encode("utf-8")).hexdigest()[:16]
    if (man.get("_fichas") or {}).get("hash") != h:
        if call is None:
            from gemini_helpers import call_flash_json as call
        body = "\n\n".join(f"=== {i} — URL {next(d['url'] for d in docs if d['id'] == i)}\n{t}" for i, t in heads.items())
        prompt = (f"TEMA: \"{seed['seed_title']}\"\nPara cada documento, su ficha según su PROPIO encabezado: título, "
                  f"autor u organización, tipo ({', '.join(TIPOS_FUENTE)}; un informe de ONG es informe_oficial) y año "
                  f"de publicación (0 si el encabezado no lo dice).\n\n{body}")
        man["_fichas"] = {"hash": h, "raw": call(prompt, response_schema=FICHA_SCHEMA,
                                                  description="R2 fichas desde el texto")}
    by = {x.get("id"): x for x in (man["_fichas"]["raw"] or {}).get("documentos") or []}
    for d in docs:
        x = by.get(d["id"])
        if not x:
            continue
        d.setdefault("ficha_busqueda", {k: d.get(k) for k in ("titulo", "tipo", "anio")})
        d["titulo"] = (x.get("titulo") or d["titulo"]).strip()
        d["autor"] = (x.get("autor") or "").strip() or None
        d["tipo"] = x["tipo"] if x.get("tipo") in TIPOS_FUENTE else d["tipo"]
        d["anio"] = int(x["anio"]) if x.get("anio") else d.get("anio")
        log.append(f"  [R2] ficha {d['id']}: {d['tipo']} {d['anio']} «{d['titulo'][:60]}»")
    return man


DUP_SHINGLE = 6
DUP_MIN = 0.8


def _shingles(text: str, n: int = DUP_SHINGLE) -> set[str]:
    ws = re.findall(r"\w+", text.lower()[:40_000])
    return {" ".join(ws[i:i + n]) for i in range(0, max(0, len(ws) - n), 3)}


def same_document(dest: Path, a: dict, b: dict) -> bool:
    """El mismo documento (mismo archivo, u otra edición del mismo PDF): mismo hash o ≥ DUP_MIN de los tramos de
    DUP_SHINGLE palabras de los primeros 40 k caracteres en común."""
    if a.get("sha1") and a.get("sha1") == b.get("sha1"):
        return True
    try:
        sa = _shingles((dest / a["txt"]).read_text(encoding="utf-8"))
        sb = _shingles((dest / b["txt"]).read_text(encoding="utf-8"))
    except (OSError, KeyError):
        return False
    return bool(sa and sb) and len(sa & sb) / min(len(sa), len(sb)) >= DUP_MIN


def _meta(f: dict) -> dict:
    return {k: f.get(k) for k in ("id", "slug", "url", "titulo", "tipo", "anio", "prioridad", "por_que")}


def _fetch_one(f: dict, dest: Path, *, place_re: str, get: Callable, local: dict[str, Path], wayback: bool,
               log: list[str]) -> dict:
    d = {**_meta(f), "descargado": date.today().isoformat(), "intentos": []}
    tries = [("original", f["url"])] + ([("wayback", None)] if wayback else [])
    i = 0
    while i < len(tries):
        via, url = tries[i]
        i += 1
        if via == "wayback":
            try:
                url = wayback_snapshot(f["url"], f.get("anio"), get)
            except Exception as e:  # noqa: BLE001
                d["intentos"].append({"via": via, "error": f"API: {type(e).__name__}: {str(e)[:120]}"})
                continue
            if url is None:
                d["intentos"].append({"via": via, "error": "sin copia en la Wayback Machine"})
                continue
        content, ctype, final, status = b"", "", url, None
        lp = local.get(norm_url(url)) if via != "wayback" else None
        if lp is not None and lp.exists():
            content, status, final = lp.read_bytes(), 200, url
            ctype = "application/pdf" if lp.suffix == ".pdf" else "text/html"
            d["intentos"].append({"via": via, "copia_local": str(lp.name), "url": url, "status": 200})
        else:
            try:
                status, content, ctype, final = get(url)
            except Exception as e:  # noqa: BLE001
                d["intentos"].append({"via": via, "url": url, "error": f"{type(e).__name__}: {str(e)[:120]}"})
                continue
            d["intentos"].append({"via": via, "url": url, "status": status, "bytes": len(content)})
            time.sleep(0.5)
        if status is None or status >= 400:
            continue
        if not _is_pdf(content, ctype, final) and via != "pdf_enlazado":
            pdf = linked_pdf(content, final)
            if pdf and len(html_to_text(content)) < PDF_LINK_MAX_TEXT:
                tries.insert(i, ("pdf_enlazado", pdf))
                d["intentos"][-1]["nota"] = f"portada corta con PDF enlazado: {pdf}"
                continue
        ext = ".pdf" if _is_pdf(content, ctype, final) else ".html"
        raw = dest / f"{f['slug']}{ext}"
        raw.write_bytes(content)
        try:
            text = pdf_to_text(raw) if ext == ".pdf" else html_to_text(content)
        except Exception as e:  # noqa: BLE001
            d["intentos"][-1]["error"] = f"texto: {type(e).__name__}: {str(e)[:120]}"
            continue
        text = re.sub(r"[ \t]+\n", "\n", text).strip()
        if len(text) < MIN_DOC_CHARS:
            d["intentos"][-1]["error"] = f"texto de {len(text)} caracteres (< {MIN_DOC_CHARS}: ¿paywall o portada?)"
            continue
        if via == "pdf_enlazado" and not names_event(text, place_re, ""):
            # F8b: el PDF enlazado desde una portada corta tiene que nombrar el evento/lugar en sus primeros
            # EVENT_CHECK_CHARS caracteres (el título de la ficha es el de la portada, no el del PDF): si no, fuera
            d["intentos"][-1]["error"] = (f"PDF enlazado que no nombra el evento en sus primeros {EVENT_CHECK_CHARS} "
                                          f"caracteres: descartado")
            log.append(f"  [R2] {f['id']} {f['slug']}: PDF enlazado descartado (no nombra el evento): {url}")
            continue
        full = len(text)
        text, recorte = cap_text(text)
        (dest / f"{f['slug']}.txt").write_text(text, encoding="utf-8")
        ok_ev = names_event(text, place_re, f.get("titulo") or "")
        d.update({"ok": True, "estado": "ok", "via": via, "url_descarga": final, "archivo": raw.name,
                  "txt": f"{f['slug']}.txt", "bytes": len(content), "caracteres": len(text), "caracteres_total": full,
                  "recorte": recorte, "sha1": hashlib.sha1(content).hexdigest(), "idioma": detect_lang(text),
                  "nombra_evento": ok_ev})
        log.append(f"  [R2] {f['id']} {f['slug']}: OK ({via}) {len(text)} caracteres"
                   + (f" · recorte: {recorte}" if recorte else "") + ("" if ok_ev else " · NO nombra el evento"))
        return d
    last = d["intentos"][-1] if d["intentos"] else {}
    d.update({"ok": False, "estado": "error", "motivo": last.get("error") or f"HTTP {last.get('status')}"})
    log.append(f"  [R2] {f['id']} {f['slug']}: FALLÓ — {d['motivo']}")
    return d


# ═══════════════════════════════════════════════════════════════
#  Literalidad con posición en el txt crudo
# ═══════════════════════════════════════════════════════════════

def _nz_map(text: str) -> tuple[str, list[int]]:
    """El texto normalizado como `verify_quotes._nz` (minúsculas, sin tildes, puntuación → espacio, espacios
    colapsados) y, por cada carácter normalizado, su posición en el texto crudo."""
    from researcher_steps.verify_quotes import FFFD
    out: list[str] = []
    idx: list[int] = []
    for i, ch in enumerate(text):
        for c in unicodedata.normalize("NFD", ch):
            if unicodedata.category(c) == "Mn":
                continue
            c = c.lower()
            if len(c) != 1 or not (c.isalnum() or c == "_" or c == FFFD):
                c = " "
            if c == " " and (not out or out[-1] == " "):
                continue
            out.append(c)
            idx.append(i)
    return "".join(out), idx


_ELLIPSIS = re.compile(r"\s*(?:\[\s*\.\.\.\s*\]|\.\.\.|…)\s*")


class DocText:
    """Un documento bajado con su versión normalizada (se calcula una vez)."""

    def __init__(self, doc_id: str, text: str):
        self.id, self.text = doc_id, text
        self.nz, self.idx = _nz_map(text)
        self._padded = f" {self.nz} "
        self._ns = None                                 # versión sin espacios (OCR que pega palabras), a pedido

    def locate(self, quote: str) -> int | None:
        """Posición (en el txt crudo) de la cita literal; con «...» cada tramo de ≥ 3 palabras tiene que estar, en
        orden y cerca del anterior. Si no está, un segundo intento sin espacios (OCR que pega o separa palabras:
        «andefficientlyevacuatingthe»), solo para citas de ≥ 8 palabras. None si no está."""
        k = self._locate(quote)
        if k is None and len(re.findall(r"\w+", str(quote or ""))) >= 8:
            k = self._locate_nospace(quote)
        return k

    def _locate_nospace(self, quote: str) -> int | None:
        from researcher_steps.verify_quotes import _nz
        if self._ns is None:
            keep = [i for i, c in enumerate(self.nz) if c != " "]
            self._ns = ("".join(self.nz[i] for i in keep), [self.idx[i] for i in keep])
        q = _nz(_ELLIPSIS.split(str(quote))[0]).replace(" ", "")
        k = self._ns[0].find(q) if len(q) >= 30 else -1
        return self._ns[1][k] if k >= 0 else None

    def _locate(self, quote: str) -> int | None:
        from researcher_steps.verify_quotes import _pattern
        pieces = [p for p in _ELLIPSIS.split(str(quote or "")) if len(re.findall(r"\w+", p)) >= 3]
        if not pieces:
            return None
        first, pos = None, 0
        for p in pieces:
            pat = _pattern(p)
            if pat is None:
                return None
            m = pat.search(self.nz, pos)
            if m is None or (first is not None and self.idx[m.start()] - first > 3000 + len(quote) * 2):
                return None
            if first is None:
                first = self.idx[m.start()]
            pos = m.end()
        return first

    def longest_run(self, quote: str, min_words: int = 5) -> int:
        """Largo (en palabras) del tramo consecutivo más largo de la cita que está literal (0 si < min_words)."""
        from researcher_steps.verify_quotes import _nz
        ws = _nz(quote).split()
        best, i = 0, 0
        while i + min_words <= len(ws):
            j = i + min_words
            if f" {' '.join(ws[i:j])} " not in self._padded:
                i += 1
                continue
            while j < len(ws) and f" {' '.join(ws[i:j + 1])} " in self._padded:
                j += 1
            best = max(best, j - i)
            i = j
        return best


# ═══════════════════════════════════════════════════════════════
#  R3 — extracción por documento
# ═══════════════════════════════════════════════════════════════

PROMPT_VERSION_R3 = "f7b-1"
CHUNK_CHARS = 60_000
CHUNK_OVERLAP = 3_000
CITA_MAX = 300
CITA_MIN_WORDS = 3
R3_THINKING = 2048
TIPOS_DATO = ("magnitud", "cifra", "fecha", "nombre", "lugar", "cita", "contradiccion")

R3_RETRIES = 2                           # F8b: reintentos de Pro por trozo (backoff R3_BACKOFF_S × intento)
R3_BACKOFF_S = 10.0

R3_SYSTEM = ("Sos un documentalista que extrae evidencia de UN documento. Todo lo que devolvés sale de ese documento y "
             "trae el fragmento EXACTO de donde sale. Nunca agregás conocimiento propio ni de otras fuentes. "
             "Respondés SOLO JSON.")

_S, _B = {"type": "STRING"}, {"type": "BOOLEAN"}
R3_SCHEMA: dict[str, Any] = {
    "type": "OBJECT",
    "properties": {
        "datos": {"type": "ARRAY", "items": {"type": "OBJECT", "properties": {
            "texto": _S, "tipo": {"type": "STRING", "enum": list(TIPOS_DATO)}, "valor": _S, "fecha": _S,
            "cita_literal": _S}, "required": ["texto", "tipo", "cita_literal"]}},
        "cronologia": {"type": "ARRAY", "items": {"type": "OBJECT", "properties": {
            "fecha": _S, "hora": _S, "evento": _S, "lugar": _S, "cita_literal": _S},
            "required": ["fecha", "evento", "cita_literal"]}},
        "lugares": {"type": "ARRAY", "items": {"type": "OBJECT", "properties": {
            "nombre": _S, "rol": _S, "cita_literal": _S}, "required": ["nombre", "cita_literal"]}},
        "citas": {"type": "ARRAY", "items": {"type": "OBJECT", "properties": {
            "autor": _S, "rol": _S, "testigo": _B, "lugar": _S, "fecha": _S, "texto_original": _S, "texto_es": _S,
            "cita_literal": _S}, "required": ["autor", "texto_original", "texto_es", "testigo", "cita_literal"]}},
        "personajes": {"type": "ARRAY", "items": {"type": "OBJECT", "properties": {
            "nombre": _S, "rol": _S, "antagonista": _B, "testigo": _B,
            "fechas_presente": {"type": "ARRAY", "items": _S}, "lugar": _S, "cita_literal": _S},
            "required": ["nombre", "rol", "testigo", "cita_literal"]}},
    },
    "required": ["datos", "cronologia", "lugares", "citas", "personajes"],
}


def build_extraction_prompt(seed: dict, doc: dict, chunk: str, part: tuple[int, int]) -> str:
    parte = f" (parte {part[0]} de {part[1]})" if part[1] > 1 else ""
    return f"""TEMA DEL VIDEO: "{seed['seed_title']}"
DOCUMENTO{parte}: {doc.get('titulo')} — {doc.get('tipo')}, {doc.get('anio') or 's/f'} — {doc.get('url')}

Extraé TODA la evidencia sobre el tema que hay en este texto. Preferí muchos ítems chicos (un hecho por dato) a pocos
grandes. Lo que no es del tema (otro lugar, otra época, otro caso, notas al pie, créditos, índices) no va.

REGLAS:
1. Solo lo que dice ESTE texto. Nada de lo que sepas por otro lado.
2. `cita_literal` en cada ítem: el fragmento del texto del que sale, copiado EXACTO (mismo idioma, mismas palabras y
   en el mismo orden, sin corregir ni resumir), de 8 a 50 palabras, continuo (sin «...»).
3. `texto` (datos) y `evento` (cronología) en español: una oración fiel con quién, qué y dónde; cifras en dígitos y con
   su unidad; sin adjetivos que el documento no use.
4. datos.tipo: magnitud (dimensiones, niveles, duración), cifra (conteos), fecha, nombre, lugar, cita, contradiccion
   (dos versiones del mismo hecho en el documento). `valor`: la cifra o el nombre tal como está en `texto`.
5. Cronología: fecha AAAA-MM-DD (AAAA-MM si no hay día); `hora` HH:MM (24 h) SOLO si el texto la da; `lugar` si lo dice.
6. Citas: palabras que alguien dijo o escribió, entre comillas o en declaración atribuida. `texto_original` exacto;
   `texto_es` traducción natural y fiel (igual al original si ya está en español). `autor`: el nombre como lo da el
   texto; si es anónimo, la descripción que da el texto («un preso de Templeman III»). NUNCA inventes un nombre.
   `testigo` = true si quien habla estuvo en el lugar de los hechos (preso, guardia, familiar, rescatista, vecino);
   false para funcionarios, abogados o expertos que hablan desde afuera. `lugar`: dónde estaba quien habla.
7. Personajes: personas con nombre propio que hacen algo o declaran en el texto (no organizaciones). `testigo` como en
   6; `fechas_presente`: los días AAAA-MM-DD en que el texto la ubica en el lugar; `antagonista` = true si el texto le
   atribuye decisiones que causaron el daño.

TEXTO:
<<<
{chunk}
>>>"""


def chunk_text(text: str, size: int = CHUNK_CHARS, overlap: int = CHUNK_OVERLAP) -> list[tuple[int, str]]:
    """Trozos de ≤ size caracteres cortados en fin de línea, con ~`overlap` de solape. [(inicio, trozo)]."""
    if len(text) <= size:
        return [(0, text)]
    out, start = [], 0
    while start < len(text):
        end = min(len(text), start + size)
        if end < len(text):
            cut = text.rfind("\n", start + size // 2, end)
            end = cut if cut > 0 else end
        out.append((start, text[start:end]))
        if end >= len(text):
            break
        nxt = text.rfind("\n", end - overlap, end - overlap // 3)
        start = nxt + 1 if nxt > start else end - overlap
    return out


FOCUS_MIN_CHARS = 50_000
FOCUS_DENSITY = 1 / 20_000               # menos de 1 mención del lugar/evento cada 20 k caracteres: documento de otra cosa
FOCUS_WINDOW = 4_000


def focus_text(text: str, place_re: str | None) -> tuple[str, str | None]:
    """Un documento largo que casi no habla del tema (p. ej. una lista de casos del DOJ) se lee solo en las ventanas de
    ±FOCUS_WINDOW caracteres alrededor de cada mención del lugar/evento (unidas si se tocan). Devuelve (texto, nota)."""
    if not place_re or len(text) < FOCUS_MIN_CHARS:
        return text, None
    hits = [m.start() for m in re.finditer(place_re, text, re.I)]
    if len(hits) >= len(text) * FOCUS_DENSITY:
        return text, None
    spans: list[list[int]] = []
    for h in hits:
        a, b = max(0, h - FOCUS_WINDOW), min(len(text), h + FOCUS_WINDOW)
        if spans and a <= spans[-1][1]:
            spans[-1][1] = b
        else:
            spans.append([a, b])
    out = "\n[…]\n".join(text[a:b] for a, b in spans)
    return out, f"{len(hits)} menciones en {len(text)} caracteres: se leen {len(spans)} ventanas ({len(out)} caracteres)"


def _str(x: Any) -> str:
    return str(x or "").strip()


def validate_doc_items(raw: dict, doc: dict, dt: DocText, log: list[str]) -> dict[str, list[dict]]:
    """Cada ítem con su cita_literal encontrada en el txt (posición cruda en `offset`); lo que no, a _descartados."""
    from researcher_steps.evidence_pool import fix_caps
    out: dict[str, list[dict]] = {k: [] for k in ("datos", "cronologia", "lugares", "citas", "personajes")}
    out["_descartados"] = []
    fuente = f"{doc.get('titulo')}, {doc.get('anio') or 's/f'}"
    base = {"doc_id": doc["id"], "bloque": doc["id"], "fuente": fuente, "idioma": doc.get("idioma")}
    key = {"datos": "texto", "cronologia": "evento", "lugares": "nombre", "citas": "texto_original",
           "personajes": "nombre"}

    def _drop(kind: str, it: dict, why: str) -> None:
        # kind «<tipo>_r3»: un descarte de lectura (sin cita literal, «Preso #13» no es un nombre) no es un personaje
        # «que no hace nada»: m05.silent_names lee los `personajes` descartados y vetaría «preso» en la narración
        out["_descartados"].append({"kind": f"{kind}_r3", "doc_id": doc["id"], "texto": _str(it.get(key[kind]))[:200],
                                    "cita_literal": _str(it.get("cita_literal"))[:200], "motivo": why})
    for kind in key:
        for it in raw.get(kind) or []:
            if not isinstance(it, dict) or not _str(it.get(key[kind])):
                continue
            lit = _str(it.get("cita_literal"))
            off = dt.locate(lit)
            if off is None and kind == "citas":                 # la cita misma también sirve de ancla
                off, lit = dt.locate(_str(it.get("texto_original"))), _str(it.get("texto_original"))
            if off is None:
                _drop(kind, it, "cita_literal no está en el documento")
                continue
            lit = lit[:CITA_MAX]
            if kind == "datos":
                t = fix_caps(_str(it["texto"]))
                v = _str(it.get("valor")) or None
                item = {"texto": t, "tipo": it.get("tipo") if it.get("tipo") in TIPOS_DATO else "cifra",
                        "valor": v if v and v.lower() in t.lower() else None, "fecha": _str(it.get("fecha")) or None}
            elif kind == "cronologia":
                f = _str(it.get("fecha"))
                if not re.match(r"^\d{4}(-\d{2}){0,2}$", f):
                    _drop(kind, it, f"fecha «{f}» no es AAAA-MM-DD")
                    continue
                years = set(re.findall(r"\b(?:19|20)\d\d\b", lit))
                if years and f[:4] not in years:            # «On August 10, 2001» fechado 2005-08-10
                    _drop(kind, it, f"fecha {f} no coincide con el año de la cita literal ({', '.join(sorted(years))})")
                    continue
                h = _str(it.get("hora"))
                item = {"fecha": f, "hora": h if re.match(r"^\d{1,2}:\d{2}$", h) else None,
                        "evento": fix_caps(_str(it["evento"])), "lugar": _str(it.get("lugar")) or None}
            elif kind == "lugares":
                n = _str(it["nombre"])
                if n.lower() not in dt.text.lower() and dt.locate(n) is None:
                    _drop(kind, it, "el nombre del lugar no está en el documento")
                    continue
                item = {"nombre": n, "rol": _str(it.get("rol")) or None}
            elif kind == "citas":
                if len(re.findall(r"\w+", _str(it["texto_original"]))) < CITA_MIN_WORDS:
                    # «no» (un guardia): no es una cita; además choca con cualquier frase («años») en los chequeos
                    _drop(kind, it, f"cita de menos de {CITA_MIN_WORDS} palabras")
                    continue
                es = _str(it.get("texto_es")) or _str(it["texto_original"])
                item = {"texto": es, "autor": _str(it.get("autor")), "fecha": _str(it.get("fecha")) or None,
                        "rol": _str(it.get("rol")) or None, "testimonio": bool(it.get("testigo")),
                        "testigo": bool(it.get("testigo")), "texto_original": _str(it["texto_original"]),
                        "texto_es": es, "presente_en": [_str(it["lugar"])] if _str(it.get("lugar")) else []}
            else:
                n = _str(it["nombre"])
                if not is_named_person(n):
                    _drop(kind, it, "no es una persona con nombre propio")
                    continue
                if n.split()[-1].strip(".,").lower() not in dt.text.lower():
                    _drop(kind, it, "el apellido no está en el documento")
                    continue
                fp = [x for x in (it.get("fechas_presente") or []) if re.match(r"^\d{4}-\d{2}-\d{2}$", str(x))]
                item = {"nombre": n, "rol": _str(it.get("rol")) or None, "antagonista": bool(it.get("antagonista")),
                        "testigo": bool(it.get("testigo")), "fechas_presente": fp, "lugar": _str(it.get("lugar")) or None}
            out[kind].append({**item, **base, "cita_literal": lit, "offset": off})
    n_ok = sum(len(out[k]) for k in key)
    log.append(f"  [R3] {doc['id']}: {n_ok} ítems con cita literal, {len(out['_descartados'])} descartados")
    return out


def extract_document(seed: dict, doc: dict, text: str, *, call: Callable[..., dict] | None = None,
                     cache_dir: Path | None = None, log: list[str] | None = None,
                     place_re: str | None = None, revalidate: bool = False) -> dict[str, list[dict]]:
    """R3: 1 llamada Pro por trozo de CHUNK_CHARS (solape CHUNK_OVERLAP); caché cruda por trozo. Las posiciones son
    siempre las del txt completo (aunque se lean solo ventanas, `focus_text`)."""
    log = log if log is not None else []
    read, nota = focus_text(text, place_re)
    if nota:
        log.append(f"  [R3] {doc['id']}: {nota}")
    if call is None:
        from gemini_helpers import call_pro_json

        def call(prompt: str, **kw: Any) -> dict:
            return call_pro_json(prompt, thinking_budget=R3_THINKING, **kw)
    dt = DocText(doc["id"], text)
    if revalidate:                                      # el txt cambió (p. ej. columnas): re-validar lo ya extraído
        cpath = cache_dir / f"r3_{doc['id']}.json" if cache_dir else None
        store = json.loads(cpath.read_text(encoding="utf-8")) if cpath and cpath.exists() else {}
        merged = {k: [] for k in ("datos", "cronologia", "lugares", "citas", "personajes", "_descartados")}
        for raw in store.values():
            part = validate_doc_items(raw or {}, doc, dt, log)
            for kk in merged:
                merged[kk] += part.get(kk) or []
        log.append(f"  [R3] {doc['id']}: re-validado desde la caché ({len(store)} respuestas, sin llamadas)")
        return merged
    chunks = chunk_text(read)
    merged: dict[str, list[dict]] = {k: [] for k in ("datos", "cronologia", "lugares", "citas", "personajes",
                                                      "_descartados")}
    store: dict[str, Any] = {}
    cpath = cache_dir / f"r3_{doc['id']}.json" if cache_dir else None
    if cpath and cpath.exists():
        store = json.loads(cpath.read_text(encoding="utf-8"))
    for i, (_, ch) in enumerate(chunks, start=1):
        prompt = build_extraction_prompt(seed, doc, ch, (i, len(chunks)))
        k = f"{PROMPT_VERSION_R3}|{hashlib.sha1(prompt.encode('utf-8')).hexdigest()[:16]}"
        if k not in store:
            res, err = None, None
            for attempt in range(R3_RETRIES + 1):        # F8b: una caída de Pro no tira el documento
                try:
                    res = call(prompt, system_instruction=R3_SYSTEM, response_schema=R3_SCHEMA,
                               description=f"R3 {doc['id']} {i}/{len(chunks)}")
                    break
                except Exception as e:  # noqa: BLE001
                    err = e
                    log.append(f"  [R3] {doc['id']} parte {i}: Pro falló ({type(e).__name__}: {str(e)[:100]})"
                               + (f" → reintento {attempt + 1}" if attempt < R3_RETRIES else " → extracción fallida"))
                    if attempt < R3_RETRIES:
                        time.sleep(R3_BACKOFF_S * (attempt + 1))
            if res is None:
                merged.setdefault("_extraccion_fallida", []).append(
                    {"parte": i, "de": len(chunks), "error": f"{type(err).__name__}: {str(err)[:200]}"})
                continue
            store[k] = res
            if cpath:
                cpath.parent.mkdir(parents=True, exist_ok=True)
                cpath.write_text(json.dumps(store, ensure_ascii=False, indent=1), encoding="utf-8")
        part = validate_doc_items(store[k] or {}, doc, dt, log)
        for kk in merged:
            merged[kk] += part.get(kk) or []
    return merged


# ═══════════════════════════════════════════════════════════════
#  R4 — merge entre documentos, contaminación, canon
# ═══════════════════════════════════════════════════════════════

OFFICIAL_TIPOS = ("fallo_judicial", "informe_oficial", "foia")
KINDS = ("datos", "cronologia", "lugares", "citas", "personajes")
_PREFIX = {"datos": "D", "cronologia": "T", "lugares": "L", "citas": "Q", "personajes": "P"}


def _overlap(a: set, b: set) -> float:
    return len(a & b) / min(len(a), len(b)) if a and b else 0.0


def _nums(t: str) -> frozenset[str]:
    return frozenset(re.sub(r"[,.](?=\d{3}\b)", "", x) for x in re.findall(r"\d[\d,.]*\d|\d", t or ""))


_TITLES = {"sheriff", "deputy", "sgt", "sergeant", "lieutenant", "lt", "captain", "capt", "capitan", "colonel", "col",
           "officer", "ranking", "warden", "chief", "jefe", "mr", "mrs", "ms", "dr", "secretary", "secretario",
           "alguacil", "teniente", "sargento", "oficial", "jr", "sr", "iii", "ii"}
# descripciones de grupo o de cargo, no personas: «Abogado del Sheriff», «Oficiales en Conchetta», «National Guard
# Officers», «Criminal Justice Working Group»
_NOT_PERSON = re.compile(r"\b(del?|en|at|of|the|según|segun|group|officers|oficiales|guardias|guards|deputies|"
                         r"abogado|abogada|attorney|warden|inmate|recluso|reclusa|preso|presa)\b", re.I)


def person_key(name: str) -> tuple[str, str]:
    """(nombre, apellido) sin cargos ni tratamientos: «Sgt. Bell» y «Sergeant Bell» → ("", "bell")."""
    ws = [_ascii(w).lower() for w in re.findall(r"[A-Za-zÁÉÍÓÚÑáéíóúñ]+", name) if w[:1].isupper()]
    ws = [w for w in ws if w not in _TITLES and len(w) >= 2]
    if not ws:
        return ("", "")
    return (ws[0] if len(ws) > 1 else "", ws[-1])


def is_named_person(name: str) -> bool:
    """Persona con nombre propio (no un cargo ni un grupo): evidence_pool.is_person y sin palabras de grupo/cargo, o un
    cargo + apellido («Deputy Foster»)."""
    from researcher_steps.evidence_pool import is_person
    return bool(is_person(name) and not _NOT_PERSON.search(name) and person_key(name)[1])


def same_person(a: str, b: str) -> bool:
    """Mismo apellido y nombre compatible: igual, o uno de los dos sin nombre de pila, o las 3 primeras letras iguales
    («Marlin» / «Martin»: errata del documento)."""
    (fa, la), (fb, lb) = person_key(a), person_key(b)
    return bool(la) and la == lb and (not fa or not fb or fa[:3] == fb[:3])


def same_fact(kind: str, a: dict, b: dict) -> bool:
    """¿Dos ítems (de documentos distintos o de trozos solapados) cuentan lo mismo?"""
    from researcher_steps.evidence_pool import _content_set, norm
    if kind == "datos":
        if norm(a["texto"]) == norm(b["texto"]):
            return True
        na, nb = _nums(a["texto"]), _nums(b["texto"])
        ov = _overlap(_content_set(a["texto"]), _content_set(b["texto"]))
        return (bool(na) and na == nb and ov >= 0.5) or (not na and not nb and ov >= 0.75)
    if kind == "cronologia":
        return a["fecha"] == b["fecha"] and _overlap(_content_set(a["evento"]), _content_set(b["evento"])) >= 0.5
    if kind == "lugares":
        x, y = sorted((norm(a["nombre"]), norm(b["nombre"])), key=len)
        return x == y or (len(x.split()) >= 2 and x in y)
    if kind == "citas":
        x, y = sorted((norm(a["texto_original"]), norm(b["texto_original"])), key=len)
        if len(x.split()) >= 4 and x in y:
            return True
        return (person_key(a["autor"])[1] == person_key(b["autor"])[1]
                and _overlap(_content_set(a["texto_original"]), _content_set(b["texto_original"])) >= 0.8)
    return same_person(a["nombre"], b["nombre"])


ITEM_YEARS = 20
# F8b: lo que puede estar lejos del evento sin ser de OTRA historia: el juicio, la consecuencia, el aniversario (después)
# y los antecedentes del lugar (antes). Español, inglés e italiano.
LATE_OK = re.compile(r"\b(juicio|proceso|sentencia|condena\w*|fallo|tribunal|apelaci\w+|casaci\w+|absuel\w+|demanda\w*|"
                     r"indemniza\w+|aniversario|homenaje|memorial|monumento|conmemora\w+|reabr\w+|investigaci\w+|"
                     r"trial|verdict|sentenced|convict\w*|acquitt\w*|court|appeal|lawsuit|settlement|compensation|"
                     r"anniversary|memorial|commemorat\w+|processo|sentenza|condann\w+|assolt\w+|risarciment\w+|"
                     r"anniversario|commemorazion\w+|cerimonia|legislatura|inquiry|commission|comisi[oó]n|commissione)\b",
                     re.I)
EARLY_OK = re.compile(r"\b(constru\w+|fund\w+|inaugur\w+|habilit\w+|proyect\w+|built|founded|opened|construct\w+|"
                      r"designed|costru\w+|progett\w+|inaugurat\w+|concession\w*|concesi[oó]n)\b", re.I)


def contamination(item: dict, event_year: int) -> str | None:
    """Motivo por el que un ítem es de OTRO tiempo; None si vale. F8b: la antigüedad se mide POR ÍTEM (su `fecha`
    contra el año del evento, ±ITEM_YEARS); después del margen valen el juicio, la consecuencia y el aniversario; antes,
    los antecedentes del lugar (construcción, fundación, habilitación)."""
    f = _str(item.get("fecha"))
    m = re.match(r"^(\d{4})", f)
    if not m:
        return None
    y = int(m.group(1))
    text = " ".join(_str(item.get(k)) for k in ("texto", "evento", "cita_literal", "tipo"))
    if y > event_year + ITEM_YEARS and not LATE_OK.search(text):
        return f"fecha {f} > evento + {ITEM_YEARS} años ({event_year + ITEM_YEARS}) y no es juicio/consecuencia/aniversario"
    if y < event_year - ITEM_YEARS and not EARLY_OK.search(text):
        return f"fecha {f} < evento − {ITEM_YEARS} años ({event_year - ITEM_YEARS}) y no es un antecedente del lugar"
    return None


def doc_contamination(doc: dict, event_year: int) -> str | None:
    """Motivo por el que TODO un documento queda fuera: no nombra el lugar/evento al principio (ni en el título). F8b:
    el año del documento ya no cuenta (un documento de 2014 sobre 1963 vale); la antigüedad se mide por ítem."""
    if not doc.get("nombra_evento"):
        return f"el documento no nombra el lugar/evento en sus primeros {EVENT_CHECK_CHARS} caracteres ni en el título"
    return None


def _doc_rank(doc: dict) -> tuple:
    t = doc.get("tipo") or ""
    off = OFFICIAL_TIPOS.index(t) if t in OFFICIAL_TIPOS else len(OFFICIAL_TIPOS)
    return (off, not domain(doc.get("url") or "").endswith(".gov"), doc.get("prioridad") or 3, doc.get("id") or "")


def merge_docs(per_doc: dict[str, dict[str, list[dict]]], docs: list[dict], *, event_year: int,
               log: list[str] | None = None) -> dict[str, Any]:
    """R4: un pool con ids nuevos. Documentos en orden de autoridad (fallo > informe oficial (.gov primero) > resto,
    luego prioridad); lo repetido entre documentos (o entre trozos) es UN ítem con `docs` y `n_fuentes`."""
    log = log if log is not None else []
    meta = {d["id"]: d for d in docs}
    pool: dict[str, Any] = {k: [] for k in KINDS}
    pool["_descartados"] = []
    for did in sorted(per_doc, key=lambda i: _doc_rank(meta.get(i, {"id": i}))):
        part = per_doc[did]
        pool["_descartados"] += part.get("_descartados") or []
        why_doc = doc_contamination(meta.get(did, {}), event_year)
        for kind in KINDS:
            for it in sorted(part.get(kind) or [], key=lambda x: x.get("offset") or 0):
                why = why_doc or contamination(it, event_year)
                if why:
                    pool["_descartados"].append({"kind": kind, "doc_id": did, "texto": _str(
                        it.get("texto") or it.get("evento") or it.get("nombre"))[:200], "motivo": f"contaminación: {why}"})
                    continue
                prev = next((x for x in pool[kind] if same_fact(kind, x, it)), None)
                ref = {"doc_id": did, "offset": it["offset"], "cita_literal": it["cita_literal"]}
                if prev is None:
                    pool[kind].append({**it, "docs": [did], "n_fuentes": 1, "evidencia": [ref]})
                    continue
                if did not in prev["docs"]:
                    prev["docs"].append(did)
                    prev["n_fuentes"] = len(prev["docs"])
                prev["evidencia"].append(ref)
                if kind == "cronologia" and not prev.get("hora") and it.get("hora"):
                    prev["hora"] = it["hora"]
                if kind == "personajes":
                    prev["testigo"] = prev.get("testigo") or it.get("testigo")
                    prev["antagonista"] = prev.get("antagonista") or it.get("antagonista")
                    prev["fechas_presente"] = sorted(set(prev.get("fechas_presente") or [])
                                                     | set(it.get("fechas_presente") or []))
                    if it["nombre"] != prev["nombre"] and it["nombre"] not in prev.setdefault("variantes_nombre", []):
                        prev["variantes_nombre"].append(it["nombre"])
                if kind == "citas" and it.get("testimonio") and not prev.get("testimonio"):
                    prev["testimonio"] = prev["testigo"] = True
    pool["cronologia"].sort(key=lambda c: (c["fecha"], c.get("hora") or ""))
    for kind, pre in _PREFIX.items():
        pool[kind] = [{"id": f"{pre}{i:02d}", **it} for i, it in enumerate(pool[kind], start=1)]
    n_multi = sum(1 for k in KINDS for it in pool[k] if it["n_fuentes"] > 1)
    log.append("  [R4] merge: " + " · ".join(f"{k} {len(pool[k])}" for k in KINDS)
               + f" · {n_multi} ítems con ≥ 2 documentos · {len(pool['_descartados'])} descartados")
    return pool


def add_quote_authors(pool: dict[str, Any], log: list[str]) -> None:
    """Un autor de cita con nombre propio que no está en personajes entra como personaje (con su rol y si es testigo)."""
    n = len(pool["personajes"])
    added = []
    for q in pool["citas"]:
        a = q.get("autor") or ""
        if not is_named_person(a) or any(same_person(a, p["nombre"]) for p in pool["personajes"]):
            continue
        n += 1
        pool["personajes"].append({"id": f"P{n:02d}", "nombre": a, "rol": q.get("rol"), "antagonista": False,
                                   "testigo": bool(q.get("testimonio")), "fechas_presente": [], "lugar": None,
                                   "doc_id": q["doc_id"], "bloque": q["doc_id"], "fuente": q.get("fuente"),
                                   "idioma": q.get("idioma"), "cita_literal": q["cita_literal"], "offset": q["offset"],
                                   "docs": list(q["docs"]), "n_fuentes": q["n_fuentes"],
                                   "evidencia": list(q["evidencia"]), "desde_cita": q["id"]})
        added.append(a)
    if added:
        log.append(f"  [R4] autores de cita sumados como personajes: {added}")


def person_stats(pool: dict[str, Any], event_year: int | None = None) -> None:
    """`n_citas` (citas suyas), `n_datos` (datos y eventos que lo nombran) y `elegible_humano` (testigo, no antagonista,
    con ≥ 3 citas o ≥ 3 datos propios y, si se da `event_year`, con alguna fecha de presencia en ese año: un preso
    muerto años antes, que el informe cuenta como antecedente, no es el humano del evento)."""
    crono = {c["id"]: str(c["fecha"]) for c in pool.get("cronologia") or []}
    people = pool["personajes"]
    for p in people:
        terms = name_terms(p, people)                   # F7c: Tyrone y Duane Lewis no se cuentan uno al otro
        p["n_citas"] = sum(1 for q in pool["citas"] if same_person(q.get("autor") or "", p["nombre"]))
        p["n_datos"] = sum(1 for x in pool["datos"] + pool["cronologia"]
                           if _names_in(terms, x.get("texto") or x.get("evento")) or _names_in(terms, x.get("cita_literal")))
        days = [crono.get(i, "") for i in p.get("presente_en") or []]       # F7c: presencia real, nunca rangos
        said = any(q.get("testimonio") and (q.get("verificacion") or {}).get("estado") == "verificada"
                   and same_person(q.get("autor") or "", p["nombre"]) for q in pool["citas"])
        # presencia real: un evento del año que lo nombra (o en su párrafo), o su propio testimonio verificado
        in_event = event_year is None or said or any(str(d).startswith(str(event_year)) for d in days)
        p["elegible_humano"] = bool(p.get("testigo") and not p.get("antagonista") and in_event
                                    and (p["n_citas"] >= 3 or p["n_datos"] >= 3))


def canonical_names(pool: dict[str, Any], texts: dict[str, "DocText"]) -> None:
    """El nombre de cada personaje = la variante (de todas las que se fusionaron) que más aparece en los documentos,
    sin cargo delante («Sheriff Martin Gusman», errata de un documento → «Marlin N. Gusman»). In place."""
    blob = "\n".join(t.text for t in texts.values())
    for p in pool["personajes"]:
        vs = list(dict.fromkeys([p["nombre"]] + (p.get("variantes_nombre") or [])))
        full = [re.sub(rf"^(?:(?:{'|'.join(_TITLES)})\.?\s+)+", "", v, flags=re.I) for v in vs if person_key(v)[0]]
        # con nombre y apellido si alguna variante lo tiene («Marlin N. Gusman», no «Gusman»); si no, tal cual
        best = max(full or vs, key=lambda v: (blob.count(v), len(v)))
        if best != p["nombre"]:
            p["variantes_nombre"] = [v for v in vs if v != best]
            p["nombre"] = best


_COUNT_OF = re.compile(r"(?<![\d,.])(\d{1,3}(?:[,.]\d{3})+|\d{4,})\s+(?:[a-záéíóúñ]+\s+){0,2}?"
                       r"(reclusos|reclusas|presos|presas|prisioneros|prisioneras|internos|detenidos|personas|"
                       r"evacuados|individuos)\b", re.I)


CANON_TOPIC = 0.35
CANON_RATIO = 1.25                      # más estricto que en v2 (1.5): acá hay cientos de cifras


def fmt_count(n: int) -> str:
    """6375 → «6,375»: la forma de cifra que leen los validadores (m05.non_canonical, evidence._num_forms)."""
    return f"{n:,}"


def count_value(texto: str) -> tuple[str, int] | None:
    """La cifra de un CONTEO de personas presas: el número pegado (≤ 2 palabras) al sustantivo («6,375 presos», «8,000
    reclusos más»), no cualquier número del texto (un año, una capacidad, otra cifra). None si no hay; si el texto trae
    dos conteos distintos, None (es un rango o una comparación, no una cifra canónica)."""
    ms = {m.group(1): int(re.sub(r"[,.]", "", m.group(1))) for m in _COUNT_OF.finditer(texto or "")}
    if len(set(ms.values())) != 1:
        return None
    k = next(iter(ms))
    return k, ms[k]


def canonical_v3(pool: dict[str, Any], docs: list[dict], log: list[str]) -> None:
    """Cifras del mismo conteo (≥ 1000, mismo sustantivo, la mayor ≤ CANON_RATIO × la menor) entre documentos: la de
    la fuente más oficial (fallo > informe oficial .gov > informe) es la canónica; las otras, «estimación de <fuente>»."""
    meta = {d["id"]: d for d in docs}

    def _val(d: dict) -> int | None:
        m = count_value(d["texto"])
        return m[1] if m else None
    from researcher_steps.evidence_pool import _content_set

    def _topic(d: dict) -> set:
        return {w for w in _content_set(d["texto"]) if not w[:1].isdigit()}
    cands = [d for d in pool["datos"] if (_val(d) or 0) >= 1000]
    # el mismo conteo = cifras cercanas (la mayor ≤ CANON_RATIO × la menor) Y el mismo asunto (≥ CANON_TOPIC de las
    # palabras en común con el primero del grupo): con cientos de datos, la cercanía sola junta capacidad y población
    groups: list[list[dict]] = []
    for d in sorted(cands, key=lambda d: _doc_rank(meta.get(d["doc_id"], {"id": d["doc_id"]}))):
        g = next((g for g in groups if max(_val(d), _val(g[0])) <= CANON_RATIO * min(_val(d), _val(g[0]))
                  and _overlap(_topic(d), _topic(g[0])) >= CANON_TOPIC), None)
        (g.append(d) if g is not None else groups.append([d]))
    out = []
    for g in groups:
        if len({_val(d) for d in g}) < 2:
            continue
        g.sort(key=lambda d: _doc_rank(meta.get(d["doc_id"], {"id": d["doc_id"]})))
        o = g[0]
        if (meta.get(o["doc_id"]) or {}).get("tipo") not in OFFICIAL_TIPOS:
            continue
        o["estatus"] = "oficial"
        var, seen = [], {_val(o)}
        for d in g[1:]:
            if _val(d) in seen:
                continue
            seen.add(_val(d))
            d["estatus"] = f"estimación de {(meta.get(d['doc_id']) or {}).get('titulo') or d['doc_id']}"[:120]
            var.append({"id": d["id"], "valor": fmt_count(_val(d)), "estatus": d["estatus"]})
        if var:
            out.append({"oficial": o["id"], "valor": fmt_count(_val(o)), "fuente": o["doc_id"],
                        "variantes": var})
    pool["cifras_canonicas"] = out
    if out:
        log.append(f"  [R4] cifras canónicas: {[(c['valor'], c['fuente'], [v['valor'] for v in c['variantes']]) for c in out]}")


# ═══════════════════════════════════════════════════════════════
#  R5 — verificación por texto (gratis, determinista)
# ═══════════════════════════════════════════════════════════════

AUTHOR_WINDOW = 400
PARTIAL_WORDS = 5


def verify_pool(pool: dict[str, Any], texts: dict[str, DocText], docs: list[dict],
                log: list[str] | None = None) -> dict[str, int]:
    """In place: `verificacion` de cada ítem contra los txt bajados.
    citas      verificada = `texto_original` literal en uno de sus documentos y, si el autor tiene nombre propio, su
               apellido a ≤ AUTHOR_WINDOW caracteres; verificada_parcial = ≥ PARTIAL_WORDS palabras seguidas literales,
               o literal sin el apellido cerca (en los dos casos va SIN nombre); sin_verificar = lo demás.
    el resto   verificada = su `cita_literal` está en el documento (R3 ya lo exige: queda la constancia)."""
    log = log if log is not None else []
    meta = {d["id"]: d for d in docs}
    count = {"verificada": 0, "verificada_parcial": 0, "sin_verificar": 0}
    for kind in KINDS:
        for it in pool[kind]:
            if kind != "citas":
                d = meta.get(it["doc_id"]) or {}
                it["verificacion"] = {"estado": "verificada", "metodo": "literal_v3", "documento": it["doc_id"],
                                      "url_fuente": d.get("url"), "offset": it["offset"],
                                      "motivo": f"cita_literal en {it['doc_id']}"}
                continue
            sur = person_key(it.get("autor") or "")[1] if is_named_person(it.get("autor") or "") else ""
            best: dict[str, Any] | None = None
            for did in it.get("docs") or [it["doc_id"]]:
                dt = texts.get(did)
                if dt is None:
                    continue
                k = dt.locate(it["texto_original"])
                if k is not None:
                    near = _ascii(dt.text[max(0, k - AUTHOR_WINDOW):k + len(it["texto_original"]) + AUTHOR_WINDOW]).lower()
                    cand = {"documento": did, "offset": k, "autor_cerca": not sur or sur in near, "run": 999}
                else:
                    run = dt.longest_run(it["texto_original"], PARTIAL_WORDS)
                    if not run:
                        continue
                    cand = {"documento": did, "offset": None, "autor_cerca": False, "run": run}
                if best is None or (cand["run"], cand["autor_cerca"]) > (best["run"], best["autor_cerca"]):
                    best = cand
            d = meta.get((best or {}).get("documento") or "") or {}
            if best and best["run"] == 999 and best["autor_cerca"]:
                v = {"estado": "verificada", "motivo": f"literal en {best['documento']}"
                     + (f", con «{sur}» a ≤ {AUTHOR_WINDOW} caracteres" if sur else " (autor sin nombre propio)")}
            elif best and best["run"] == 999:
                v = {"estado": "verificada_parcial",
                     "motivo": f"literal en {best['documento']}, pero sin «{sur}» cerca: va sin nombre"}
            elif best:
                v = {"estado": "verificada_parcial",
                     "motivo": f"{best['run']} palabras seguidas literales en {best['documento']}: va sin nombre"}
            else:
                v = {"estado": "sin_verificar", "motivo": f"no está en {it.get('docs')}"}
            it["verificacion"] = {**v, "metodo": "literal_v3", "documento": (best or {}).get("documento"),
                                  "url_fuente": d.get("url"), "fecha_documento": str(d["anio"]) if d.get("anio") else None,
                                  "offset": (best or {}).get("offset"), "cita_original": it["texto_original"]}
            count[v["estado"]] += 1
    for p in pool["personajes"]:
        p["testigo_verificado"] = any(
            (q.get("verificacion") or {}).get("estado") == "verificada" and same_person(q.get("autor") or "", p["nombre"])
            for q in pool["citas"])
    log.append(f"  [R5] citas: {count}")
    return count


def build_pool(per_doc: dict[str, dict], docs: list[dict], texts: dict[str, DocText], *, event_year: int,
               geocode_cache: Path | None = None, fetch: Callable | None = None,
               log: list[str] | None = None, subject_re: str | None = None) -> dict[str, Any]:
    """R4 + R5: merge, contaminación, autores de cita, acción, presencia, estadísticas de personajes, cifras canónicas,
    geocodificación (si hay caché) y verificación. Mismo contrato que `extract_evidence_pool` + campos nuevos."""
    from researcher_steps.evidence_pool import acting_filter, anchor_place, geocode
    log = log if log is not None else []
    pool = merge_docs(per_doc, docs, event_year=event_year, log=log)
    add_quote_authors(pool, log)
    canonical_names(pool, texts)
    # el filtro de acción (verbos en español) es para los bloques resumidos: acá un testigo ya está probado por su
    # cita_literal en el documento y no pasa por el filtro (si no, se pierden testigos de la ACLU)
    es_texts = [x.get("texto") or x.get("evento") or "" for k in ("datos", "cronologia", "citas") for x in pool[k]]
    testigos = [p for p in pool["personajes"] if p.get("testigo")]
    pool["personajes"] = [p for p in pool["personajes"] if not p.get("testigo")]
    acting_filter(pool, ["\n".join(es_texts)], log)
    pool["personajes"] = sorted(pool["personajes"] + testigos, key=lambda p: int(p["id"][1:]))
    presence_v3(pool, texts, log)                         # F7c: por párrafo (antes: evidence_pool.presence)
    person_stats(pool, event_year)
    canonical_v3(pool, docs, log)
    pop = population_canon(pool, docs, subject_re or SUBJECT_RE_DEFAULT, log)   # F7c: la población con todas sus variantes, primero
    if pop:
        pool["cifras_canonicas"] = [pop] + [g for g in pool["cifras_canonicas"]
                                            if g["oficial"] not in {v["id"] for v in pop["variantes"]} | {pop["oficial"]}]
    if geocode_cache is not None:
        texts_es = [d["texto"] for d in pool["datos"]] + [c["evento"] for c in pool["cronologia"]]
        geocode(pool["lugares"], geocode_cache, fetch=fetch, log=log, anchor=anchor_place(pool["lugares"], texts_es))
    verify_pool(pool, texts, docs, log)
    person_stats(pool, event_year)                        # F7c: otra vez, ya con las citas verificadas
    add_fragments(pool)                                   # F7c-2: lo que la voz cita literal (≤ 25 palabras)
    pool["digest"] = build_digest(pool, docs, event_year=event_year)   # F7c: lo que lee la escaleta
    pool["_research_v3"] = {"prompt_r1": PROMPT_VERSION_R1, "prompt_r3": PROMPT_VERSION_R3,
                            "documentos": [{k: d.get(k) for k in ("id", "titulo", "tipo", "anio", "url", "txt",
                                                                  "caracteres", "idioma")} for d in docs]}
    return pool


def metrics(pool: dict[str, Any]) -> dict[str, Any]:
    """Métricas del criterio de éxito (handoff F7 §1) para comparar pools."""
    citas = pool.get("citas") or []
    ver = [q for q in citas if (q.get("verificacion") or {}).get("estado") == "verificada"]
    named_w = [q for q in ver if q.get("testimonio") and is_named_person(q.get("autor") or "")]
    items = [it for k in KINDS for it in pool.get(k) or []]
    pers = pool.get("personajes") or []
    return {
        "datos": len(pool.get("datos") or []), "cronologia": len(pool.get("cronologia") or []),
        "cronologia_con_hora": sum(1 for c in pool.get("cronologia") or [] if c.get("hora")),
        "lugares": len(pool.get("lugares") or []), "citas": len(citas), "citas_verificadas": len(ver),
        "citas_testigo_con_nombre_verificadas": len(named_w),
        "testigos_con_nombre_citados": len({q["autor"] for q in named_w}),
        "personajes": len(pers), "testigos": sum(1 for p in pers if p.get("testigo")),
        "testigos_3_citas": sum(1 for p in pers if p.get("testigo") and (p.get("n_citas") or 0) >= 3),
        "elegibles_humano": sum(1 for p in pers if p.get("elegible_humano")),
        "pct_doc_y_posicion": round(100 * sum(1 for it in items if it.get("doc_id") and it.get("offset") is not None)
                                    / max(len(items), 1), 1),
        "items_2_fuentes": sum(1 for it in items if (it.get("n_fuentes") or 1) > 1),
    }


# ═══════════════════════════════════════════════════════════════
#  F7c (validación del analista sobre F7b) — presencia por párrafo, población, digest
# ═══════════════════════════════════════════════════════════════

PRESENCE_WINDOW = 500


def name_terms(p: dict, people: list[dict]) -> list[str]:
    """Cómo se busca a una persona en un texto (sin tildes, minúsculas): sus nombres completos (nombre + apellido, de
    todas sus variantes) y el apellido solo si ninguna otra persona del pool lo comparte (Tyrone y Duane Lewis no)."""
    out = []
    for v in [p["nombre"]] + list(p.get("variantes_nombre") or []):
        f, last = person_key(v)
        if f and last:
            out.append(f"{f} {last}")
    sur = person_key(p["nombre"])[1]
    if sur and sum(1 for q in people if person_key(q["nombre"])[1] == sur) == 1:
        out.append(sur)
    return list(dict.fromkeys(out))


def _names_in(terms: list[str], text: str) -> bool:
    t = " " + re.sub(r"[^a-z0-9ñ]+", " ", _ascii(str(text or "")).lower()) + " "
    return any(f" {x} " in t for x in terms)


def presence_v3(pool: dict[str, Any], texts: dict[str, "DocText"], log: list[str] | None = None) -> None:
    """In place: `presente_en` = los eventos de la cronología donde la persona está DE VERDAD: la cita literal del evento
    (o su texto) la nombra, o el evento está en el mismo párrafo del documento que una mención suya (±PRESENCE_WINDOW
    caracteres de su posición). Nunca por fechas ni rangos (`fechas_presente` queda como dato del modelo, sin usar).
    `testigo`: lo marcó el modelo o dice una cita de testigo."""
    people = pool.get("personajes") or []
    crono = pool.get("cronologia") or []
    for p in people:
        terms = name_terms(p, people)
        pos: dict[str, list[int]] = {}
        for did, dt in texts.items():
            low = _ascii(dt.text).lower()                 # _ascii conserva el largo (una letra por letra)
            hits = []
            for x in terms:
                pat = r"\b" + r"[ .]+".join(re.escape(w) for w in x.split()) + r"\b"
                hits += [m.start() for m in re.finditer(pat, low)]
            pos[did] = sorted(hits)
        ids = []
        for c in crono:
            refs = c.get("evidencia") or [{"doc_id": c.get("doc_id"), "offset": c.get("offset"),
                                           "cita_literal": c.get("cita_literal")}]
            if _names_in(terms, c.get("evento")) or any(
                    _names_in(terms, r.get("cita_literal")) or any(abs(k - (r.get("offset") or -10 ** 9))
                                                                   <= PRESENCE_WINDOW for k in pos.get(r.get("doc_id"), []))
                    for r in refs):
                ids.append(c["id"])
        p["presente_en"] = ids
        p["testigo"] = bool(p.get("testigo") or any(q.get("testimonio") and same_person(q.get("autor") or "", p["nombre"])
                                                    for q in pool.get("citas") or []))
        p.setdefault("fechas_presente", [])
    if log is not None:
        log.append(f"  [R4] presencia por párrafo: {sum(len(p['presente_en']) for p in people)} vínculos persona-evento "
                   f"({sum(1 for p in people if p['presente_en'])} personas con alguno)")


SUBJECT_RE_DEFAULT = (r"\b(OPP|Prisi[oó]n Parroquial de Orleans|Orleans Parish Prison|c[aá]rcel de (?:Nueva )?Orleans|"
                      r"complejo carcelario)\b")
_OTHER_PLACE = re.compile(r"\b(Hunt|Angola|Jena|Elayn|Rapides|Templeman (?:I|II|III|IV|V)\b|Conchetta|paso elevado|"
                          r"overpass)", re.I)
# la cifra se ATRIBUYE a una fuente oficial («según el sheriff», «el conteo oficial de 6375»), no solo la nombra («el
# sheriff tenía 3 botes para casi 7000 presos»)
_OFFICIAL_SAYS = re.compile(r"seg[uú]n (?:el |la |las |los )?(?:sheriff|alguacil|estad[ií]sticas|registros|cifras? "
                            r"oficial)|conteo oficial|cifra oficial|estad[ií]sticas del (?:sheriff|alguacil)|"
                            r"oficialmente|registros oficiales", re.I)
POP_BAND = (0.6, 1.4)                    # el conteo total: dentro de 0.6–1.4 × la mediana (fuera los subconjuntos)


def population_canon(pool: dict[str, Any], docs: list[dict], subject_re: str = SUBJECT_RE_DEFAULT,
                     log: list[str] | None = None) -> dict[str, Any] | None:
    """La cifra de POBLACIÓN del lugar del video con TODAS sus variantes y su fuente (6,295 / 6,375 / 6,500 / 8,000…):
    datos con un conteo ≥ 1000 de personas (`count_value`) que nombran al sujeto (`subject_re`), no hablan de otro
    lugar (Hunt, el paso elevado, un edificio) y caen en POP_BAND × la mediana (fuera los subconjuntos: los 2,000 presos
    del DOC, los 1,300 evacuados que escribieron). Oficial = la de un documento informe_oficial / fallo_judicial / foia,
    primero la que se atribuye al sheriff o a registros oficiales; si no hay, `oficial: None` y `sin_oficial: true`
    (la voz dice «según <fuente>»). Devuelve el grupo (o None) para ponerlo primero en `cifras_canonicas`."""
    meta = {d["id"]: d for d in docs}
    rows = []
    for d in pool.get("datos") or []:
        cv = count_value(d["texto"])
        about = re.search(subject_re, d["texto"], re.I) or _OFFICIAL_SAYS.search(d["texto"])   # «del sheriff»
        if not cv or cv[1] < 1000 or not about or _OTHER_PLACE.search(d["texto"]):
            continue
        m = meta.get(d["doc_id"]) or {}
        rows.append({"id": d["id"], "valor": fmt_count(cv[1]), "n": cv[1], "doc_id": d["doc_id"],
                     "fuente": f"{m.get('titulo') or d['doc_id']} ({m.get('anio') or 's/f'})", "tipo_doc": m.get("tipo"),
                     "texto": d["texto"], "atribuida_oficial": bool(_OFFICIAL_SAYS.search(d["texto"]))})
    if rows:
        ns = sorted(r["n"] for r in rows)
        med = ns[len(ns) // 2]
        rows = [r for r in rows if POP_BAND[0] * med <= r["n"] <= POP_BAND[1] * med]
    if len({r["n"] for r in rows}) < 2:
        return None
    of = sorted([r for r in rows if r["tipo_doc"] in OFFICIAL_TIPOS],
                key=lambda r: (not r["atribuida_oficial"], _doc_rank(meta.get(r["doc_id"], {"id": r["doc_id"]}))))
    o = of[0] if of else None
    var = []
    for r in sorted(rows, key=lambda r: (r["n"], r["id"])):
        if o and r["id"] == o["id"]:
            continue
        est = "oficial (mismo valor)" if o and r["n"] == o["n"] else f"según {r['fuente']}"
        var.append({"id": r["id"], "valor": r["valor"], "estatus": est, "fuente": r["fuente"], "texto": r["texto"]})
    for r in rows:
        d = next(x for x in pool["datos"] if x["id"] == r["id"])
        d["estatus"] = "oficial" if o and (r["id"] == o["id"] or r["n"] == o["n"]) else f"según {r['fuente']}"[:140]
    g = {"tipo": "poblacion", "oficial": o["id"] if o else None, "valor": o["valor"] if o else None,
         "fuente": o["doc_id"] if o else None, "fuente_titulo": o["fuente"] if o else None, "sin_oficial": o is None,
         "variantes": var}
    if log is not None:
        log.append(f"  [R4] población: oficial {g['valor']} ({g['fuente']}) · variantes "
                   f"{[(v['valor'], v['id']) for v in var]}" if o else
                   f"  [R4] población SIN OFICIAL: {[(v['valor'], v['fuente']) for v in var]}")
    return g


DIGEST_VERSION = "f7c-1"
DIGEST_DATOS_POR_DOC = 25
DIGEST_CRONO_SIN_HORA = 20
DIGEST_CITAS_ANONIMAS = 10
DIGEST_CITAS_CON_NOMBRE = 12
DIGEST_LUGARES = 30
DIGEST_FUENTE_CHARS = 40


def _short_src(fuente: str | None) -> str:
    """«Abandoned & Abused: Orleans Parish Prisoners in the Wake of Hurricane Katrina, 2006» → «Abandoned & Abused:
    Orleans Parish Prisoners…, 2006»: la fuente se repite en cada línea del digest; el título entero, en el pool."""
    f = str(fuente or "")
    head, _, year = f.rpartition(", ")
    if not head:
        head, year = f, ""
    head = head if len(head) <= DIGEST_FUENTE_CHARS else head[:DIGEST_FUENTE_CHARS].rstrip() + "…"
    return head + (f", {year}" if year else "")


def _q_line(q: dict) -> str:
    """Línea de cita del digest: con fragmento, la voz cita SOLO el fragmento y parafrasea el resto (F7c-2)."""
    v = (q.get("verificacion") or {}).get("estado")
    tag = (" · TESTIMONIO (estuvo ahí)" if q.get("testimonio") else "") + (
        "" if not v else " · VERIFICADA" if v == "verificada" else " · SIN VERIFICAR (se usa sin el nombre)")
    rol = f" ({q['rol']})" if q.get("rol") else ""
    frag = q.get("fragmento") or q["texto"]
    rest = (f" (la cita entera tiene {len(q['texto'].split())} palabras: el resto se parafrasea)"
            if frag != q["texto"] else "")
    return (f'  [{q["id"]}] CITA: "{frag}"{rest} — {q.get("autor")}{rol}{tag} · '
            f'fuente: {_short_src(q.get("fuente"))}')


def _d_line(it: dict, kind: str) -> str:
    if kind == "cronologia":
        h = f" {it['hora']}" if it.get("hora") else ""
        return f"  [{it['id']}] CRONO: {it['evento']} ({it['fecha']}{h}) · fuente: {_short_src(it.get('fuente'))}"
    if kind == "lugares":
        return f"  [{it['id']}] LUGAR: {it['nombre']}" + (f" — {it['rol']}" if it.get("rol") else "")
    v = f" [valor: {it['valor']}]" if it.get("valor") else ""
    n = f" · {it['n_fuentes']} documentos" if (it.get("n_fuentes") or 1) > 1 else ""
    return f"  [{it['id']}] DATO: {it['texto']}{v}{n}"


def build_digest(pool: dict[str, Any], docs: list[dict], *, event_year: int) -> dict[str, Any]:
    """`pool["digest"]` (aditivo): la sección del pool que lee la escaleta cuando el pool es grande. Con ids reales del
    pool (la escaleta y sus validadores siguen usando el pool entero):
      personas    las elegibles como humano, completas (rol, testigo, verificado, en qué eventos estuvo, sus datos), y
                  los antagonistas con ≥ 3 citas o datos; todas sus citas
      citas       además, testimonios verificados: hasta DIGEST_CITAS_CON_NOMBRE de otros testigos con nombre y hasta
                  DIGEST_CITAS_ANONIMAS sin nombre propio (los más confirmados, los más cortos)
      cifras      las canónicas (la población primero, con todas sus variantes y fuente)
      cronología  todos los eventos con hora + hasta DIGEST_CRONO_SIN_HORA del año del evento (los más confirmados)
      lugares     los DIGEST_LUGARES más nombrados en datos y cronología
      datos       por documento, hasta DIGEST_DATOS_POR_DOC (más documentos que lo confirman, cifras, personas
                  elegibles), en el orden del documento
    Devuelve {"version", "texto", "ids", "caracteres"}."""
    meta = {d["id"]: d for d in docs}
    people = pool.get("personajes") or []
    chosen = [p for p in people if p.get("elegible_humano")] + [
        p for p in people if p.get("antagonista") and (p.get("n_citas") or 0) + (p.get("n_datos") or 0) >= 3]
    terms = {p["id"]: name_terms(p, people) for p in chosen}
    ids: list[str] = []
    L = ["PERSONAS (las elegibles como humano y los antagonistas; el resto del pool no se lista):"]
    for p in chosen:
        tags = [t for t, on in (("TESTIGO", p.get("testigo")), ("VERIFICADO", p.get("testigo_verificado")),
                                ("ANTAGONISTA", p.get("antagonista")), ("ELEGIBLE COMO HUMANO", p.get("elegible_humano")))
                if on]
        own = [x["id"] for k in ("datos", "cronologia") for x in pool[k]
               if _names_in(terms[p["id"]], x.get("texto") or x.get("evento"))][:12]
        L.append(f"  [{p['id']}] PERSONA: {p['nombre']} — {p.get('rol') or ''} · {' · '.join(tags)}"
                 + (f" · estuvo en {', '.join(p['presente_en'][:10])}" if p.get("presente_en") else "")
                 + (f" · sus datos: {', '.join(own)}" if own else ""))
        ids += [p["id"]] + own
    L += ["", "CITAS (de esas personas; otros testigos con nombre y testimonios sin nombre, verificados):"]
    qs = [q for q in pool["citas"] if any(same_person(q.get("autor") or "", p["nombre"]) for p in chosen)]
    def _best(cands: list[dict], n: int) -> list[dict]:
        return sorted([q for q in cands if q.get("testimonio") and q not in qs
                       and (q.get("verificacion") or {}).get("estado") == "verificada"],
                      key=lambda q: (-(q.get("n_fuentes") or 1), len(q["texto"])))[:n]
    named = _best([q for q in pool["citas"] if is_named_person(q.get("autor") or "")], DIGEST_CITAS_CON_NOMBRE)
    anon = _best([q for q in pool["citas"] if not is_named_person(q.get("autor") or "")], DIGEST_CITAS_ANONIMAS)
    for q in qs + named + anon:
        L.append(_q_line(q))
        ids.append(q["id"])
    L += ["", "CIFRAS CANÓNICAS:"]
    for g in pool.get("cifras_canonicas") or []:
        if g.get("tipo") == "poblacion":
            head = (f"  POBLACIÓN: la OFICIAL es [{g['oficial']}] {g['valor']} ({g['fuente_titulo']}). Usá esa."
                    if not g.get("sin_oficial") else "  POBLACIÓN: SIN CIFRA OFICIAL; la voz dice «según <fuente>».")
            L.append(head)
            L += [f"    variante [{v['id']}] {v['valor']} — {v['estatus']}" for v in g["variantes"]]
        else:
            L.append(f"  {g['valor']}: la OFICIAL es [{g['oficial']}]; variantes "
                     + ", ".join(f"{v['id']} ({v['valor']}, {v['estatus']})" for v in g["variantes"]))
        ids += [x for x in [g.get("oficial")] + [v["id"] for v in g["variantes"]] if x]
    L += ["", "CRONOLOGÍA (con hora, y los días del evento más confirmados):"]
    con = [c for c in pool["cronologia"] if c.get("hora")]
    sin = sorted([c for c in pool["cronologia"] if not c.get("hora") and str(c["fecha"]).startswith(str(event_year))],
                 key=lambda c: (-(c.get("n_fuentes") or 1), c["id"]))[:DIGEST_CRONO_SIN_HORA]
    for c in sorted(con + sin, key=lambda c: (c["fecha"], c.get("hora") or "")):
        L.append(_d_line(c, "cronologia"))
        ids.append(c["id"])
    blob = " ".join((x.get("texto") or x.get("evento") or "") for k in ("datos", "cronologia") for x in pool[k]).lower()
    lug = sorted(pool["lugares"], key=lambda x: -blob.count(x["nombre"].lower()))[:DIGEST_LUGARES]
    L += ["", f"LUGARES (los {DIGEST_LUGARES} más nombrados):"] + [_d_line(x, "lugares") for x in lug]
    ids += [x["id"] for x in lug]
    all_terms = [t for ts in terms.values() for t in ts]
    L += ["", f"DATOS POR DOCUMENTO (hasta {DIGEST_DATOS_POR_DOC} por documento):"]
    for did in sorted({d["doc_id"] for d in pool["datos"]}, key=lambda i: _doc_rank(meta.get(i, {"id": i}))):
        ds = [d for d in pool["datos"] if d["doc_id"] == did]
        sc = sorted(ds, key=lambda d: (-((d.get("n_fuentes") or 1) * 3
                                         + 2 * (d.get("tipo") in ("cifra", "magnitud", "contradiccion"))
                                         + 2 * _names_in(all_terms, d["texto"]) + bool(re.search(r"\d", d["texto"]))),
                                       d.get("offset") or 0))[:DIGEST_DATOS_POR_DOC]
        sc.sort(key=lambda d: d.get("offset") or 0)
        m = meta.get(did) or {}
        L.append(f"── {did}: {m.get('titulo')} ({m.get('tipo')}, {m.get('anio') or 's/f'}) — {len(sc)} de {len(ds)} datos")
        L += [_d_line(d, "datos") for d in sc]
        ids += [d["id"] for d in sc]
    texto = "\n".join(L)
    return {"version": DIGEST_VERSION, "texto": texto, "ids": list(dict.fromkeys(ids)), "caracteres": len(texto)}


# ═══════════════════════════════════════════════════════════════
#  F7c-2 (validación del analista sobre F7c) — fragmento citable
# ═══════════════════════════════════════════════════════════════

FRAGMENT_MAX_WORDS = 25
FRAGMENT_MIN_WORDS = 6
_SENT_END = re.compile(r"(?<=[.!?…])\s+")
_CLAUSE_END = re.compile(r"(?<=[,;:])\s+")


def quote_fragment(texto: str) -> str:
    """El pedazo de la cita que la voz dice LITERAL (≤ FRAGMENT_MAX_WORDS palabras, tal cual está en `texto`); el resto
    lo parafrasea el narrador. Una cita corta es su propio fragmento. Si no: la PRIMERA oración que entra (≥
    FRAGMENT_MIN_WORDS palabras: la frase fuerte de un testimonio suele ir primero); si ninguna entra, la primera oración cortada en el último fin de cláusula (coma, punto
    y coma) que entra; si tampoco, sus primeras FRAGMENT_MAX_WORDS palabras. Siempre una subcadena de `texto`."""
    t = str(texto or "").strip()
    if len(t.split()) <= FRAGMENT_MAX_WORDS:
        return t
    sents = [s.strip() for s in _SENT_END.split(t) if s.strip()]
    fit = [s for s in sents if FRAGMENT_MIN_WORDS <= len(s.split()) <= FRAGMENT_MAX_WORDS]
    if fit:
        return fit[0]
    first = sents[0] if sents else t
    acc = ""
    for c in _CLAUSE_END.split(first):
        nxt = (acc + " " + c).strip() if acc else c
        if len(nxt.split()) > FRAGMENT_MAX_WORDS:
            break
        acc = nxt
    if len(acc.split()) >= FRAGMENT_MIN_WORDS:
        return acc.rstrip(",;: ")
    return " ".join(first.split()[:FRAGMENT_MAX_WORDS]).rstrip(",;: ")


def add_fragments(pool: dict[str, Any]) -> None:
    """In place: `fragmento` en cada cita (aditivo; ver quote_fragment)."""
    for q in pool.get("citas") or []:
        q["fragmento"] = quote_fragment(q.get("texto") or "")


# ═══════════════════════════════════════════════════════════════
#  F7d — research v3 de punta a punta para un seed nuevo (topic_researcher, RESEARCH_V3=1 por defecto)
# ═══════════════════════════════════════════════════════════════

PROFILE_SCHEMA: dict[str, Any] = {"type": "OBJECT", "properties": {
    "anio_evento": {"type": "INTEGER"}, "lugar_principal": {"type": "STRING"},
    "nombres_lugar": {"type": "ARRAY", "items": {"type": "STRING"}}, "idioma_local": {"type": "STRING"},
    "nombres_locales": {"type": "ARRAY", "items": {"type": "STRING"}}},
    "required": ["anio_evento", "nombres_lugar", "idioma_local"]}


def place_regex(names: list[str], locales: list[str] | None = None, fallback: str = "") -> str:
    """`place_re`: los nombres latinos con el patrón de siempre (`\\b…\\b`) y, F19, las formas en el alfabeto local con
    límites de letra por lookaround (en cirílico `\\b` falla en algunos límites). Sin locales, el mismo de antes."""
    parts = [rf"\b{re.escape(n)}\b" for n in names]
    parts += [rf"(?<!\w){re.escape(n)}(?!\w)" for n in locales or [] if n not in names]
    return "|".join(parts) or re.escape(fallback)


def seed_profile(seed: dict, *, call: Callable[..., dict] | None = None) -> dict[str, Any]:
    """Año del evento y nombres del lugar/evento (en inglés y en el idioma local) para la contaminación y el «nombra el
    evento» de R2 (1 Flash, sin búsqueda). `place_re` = esos nombres como alternativa.
    F19: `nombres_locales` = las formas del lugar y del evento en el alfabeto del idioma local (cirílico para Kyshtym);
    entran en `place_re` además de los latinos."""
    if call is None:
        from gemini_helpers import call_flash_json as call
    raw = call(f"""TEMA: "{seed['seed_title']}"
Devolvé el año en que ocurrió el evento central, el lugar principal y de 3 a 6 nombres con los que un documento en
inglés o en el idioma del lugar nombraría el lugar o el evento (nombre oficial, sigla, nombre corto, nombre del evento),
y el idioma local («inglés (Nueva Orleans, EE. UU.)»).
En `nombres_locales`, de 3 a 8 formas del lugar y del evento escritas en el alfabeto del idioma local, tal como las
escribe un documento en ese idioma (nombre oficial, sigla, nombre corto, nombre del evento).""",
               response_schema=PROFILE_SCHEMA, description="research v3 perfil del seed") or {}
    names = [str(n).strip() for n in raw.get("nombres_lugar") or [] if len(str(n).strip()) >= 3]
    locales = [str(n).strip() for n in raw.get("nombres_locales") or [] if len(str(n).strip()) >= 3]
    return {"anio_evento": int(raw.get("anio_evento") or 0), "lugar_principal": raw.get("lugar_principal") or "",
            "idioma_local": raw.get("idioma_local") or "", "nombres_lugar": names, "nombres_locales": locales,
            "place_re": place_regex(names, locales, seed["seed_title"][:30])}


def pool_to_blocks(pool: dict[str, Any]) -> dict[str, str]:
    """Bloques angulares (tecnico, humano, misterio, visual) armados con el pool leído de documentos, para que 4a–4e
    sigan recibiendo lo de siempre sin las 4 búsquedas de resumen. Cada línea es un ítem del pool con su fuente."""
    def line(it: dict, txt: str) -> str:
        return f"- {txt} (fuente: {it.get('fuente')})"
    srcs = sorted({it.get("fuente") for k in KINDS for it in pool.get(k) or [] if it.get("fuente")})
    fuentes = "[FUENTES CONSULTADAS]\n" + "\n".join(f"- {s}" for s in srcs)
    crono = "\n".join(line(c, f"{c['fecha']}{' ' + c['hora'] if c.get('hora') else ''}: {c['evento']}")
                      for c in pool.get("cronologia") or [])
    datos = "\n".join(line(d, d["texto"]) for d in pool.get("datos") or [] if d.get("tipo") in
                      ("cifra", "magnitud", "fecha", "contradiccion"))
    gente = "\n".join(f"- {p['nombre']} — {p.get('rol') or ''}{' · testigo' if p.get('testigo') else ''}"
                      for p in pool.get("personajes") or [])
    citas = "\n".join(line(q, f"«{q['texto']}» — {q.get('autor')}") for q in pool.get("citas") or []
                      if (q.get("verificacion") or {}).get("estado") == "verificada")
    canon = "\n".join(f"- {g.get('valor')} ({g.get('fuente_titulo') or g.get('fuente')}); variantes: "
                      + ", ".join(f"{v['valor']} ({v['estatus']})" for v in g["variantes"])
                      for g in pool.get("cifras_canonicas") or [])
    otros = "\n".join(line(d, d["texto"]) for d in pool.get("datos") or [] if d.get("tipo") not in
                      ("cifra", "magnitud", "fecha", "contradiccion"))
    lugares = "\n".join(f"- {lg['nombre']}{' — ' + lg['rol'] if lg.get('rol') else ''}" for lg in pool.get("lugares") or [])
    return {
        "tecnico": f"=== HALLAZGOS: TÉCNICO ===\n[CRONOLOGÍA]\n{crono}\n\n[DATOS DUROS]\n{datos}\n\n{fuentes}",
        "humano": f"=== HALLAZGOS: HUMANO ===\n[PERSONAS]\n{gente}\n\n[TESTIMONIOS]\n{citas}\n\n{fuentes}",
        "misterio": f"=== HALLAZGOS: MISTERIO ===\n[CIFRAS EN DISPUTA]\n{canon or '- (ninguna)'}\n\n[OTROS DATOS]\n{otros}\n\n"
                    f"{fuentes}",
        "visual": f"=== HALLAZGOS VISUALES ===\n[LUGARES]\n{lugares}\n\n[DATOS FÍSICOS]\n{datos}\n\n{fuentes}",
    }


def run_seed(seed: dict, topic_id: str, steps_dir: Path, *, log: list[str] | None = None,
             gate: bool = True) -> tuple[dict[str, Any], dict[str, str], dict[str, Any] | None]:
    """Research v3 de un seed: perfil → R1 → R2 (+ fichas) → R3 → R4/R5 → compuerta del pool (rojo → PoolGateRed).
    Deja en `steps_dir`: _perfil.json, fuentes.json, fuentes/ (+ manifest), _r3_cache/, 00_pool_v3.json, POOL_GATE.md.
    Devuelve (pool, bloques angulares para 4a–4e, gate)."""
    from config import DATA_DIR
    log = log if log is not None else []
    steps_dir.mkdir(parents=True, exist_ok=True)
    pf = steps_dir / "_perfil.json"
    prof = json.loads(pf.read_text(encoding="utf-8")) if pf.exists() else seed_profile(seed)
    pf.write_text(json.dumps(prof, ensure_ascii=False, indent=1), encoding="utf-8")
    s2 = {**seed, "lugar_idioma": seed.get("idioma_local") or prof.get("idioma_local") or None,  # F8: el del seed manda
          "nombres_lugar": prof.get("nombres_lugar") or []}                                       # F8b: R1 alternativo
    r1 = discover_sources(s2, cache=steps_dir / "_r1_cache.json", log=log)
    (steps_dir / "fuentes.json").write_text(json.dumps(r1, ensure_ascii=False, indent=1), encoding="utf-8")
    src = steps_dir / "fuentes"
    man = download_sources(r1["fuentes"], src, place_re=prof["place_re"], log=log)
    refine_fichas(man, src, seed, log=log)
    (src / "manifest.json").write_text(json.dumps(man, ensure_ascii=False, indent=1), encoding="utf-8")
    docs = [d for d in man["documentos"] if d.get("ok")]
    texts, per_doc = {}, {}
    year = prof.get("anio_evento") or date.today().year
    for d in docs:
        texts[d["id"]] = DocText(d["id"], (src / d["txt"]).read_text(encoding="utf-8"))
        if doc_contamination(d, year):
            continue
        per_doc[d["id"]] = extract_document(seed, d, texts[d["id"]].text, cache_dir=steps_dir / "_r3_cache", log=log,
                                            place_re=prof["place_re"])
        fail = per_doc[d["id"]].pop("_extraccion_fallida", None)
        if fail:                                         # F8b: el pool sigue; el documento queda marcado
            d["extraccion_fallida"] = fail
            log.append(f"  [R3] {d['id']}: extracción fallida en {len(fail)} parte(s): el pool sigue sin ellas")
    if any(d.get("extraccion_fallida") for d in docs):
        (src / "manifest.json").write_text(json.dumps(man, ensure_ascii=False, indent=1), encoding="utf-8")
    pool = build_pool(per_doc, docs, texts, event_year=year, geocode_cache=DATA_DIR / "geocode_cache.json", log=log)
    (steps_dir / "00_pool_v3.json").write_text(json.dumps(pool, ensure_ascii=False, indent=1), encoding="utf-8")
    g = None
    if gate:
        from researcher_steps import pool_gate as pg
        g = pg.check(pool, topic_id, steps_dir)                      # rojo → PoolGateRed (el seed vuelve al inbox)
        pool["_pool_gate"] = {k: g[k] for k in ("color", "metricas", "motivos")}
    return pool, pool_to_blocks(pool), g
