"""
modules/youtube_scanner.py

Módulo compartido para escaneo de YouTube.
Centraliza la lógica que antes estaba dentro de topic_validator.py para que
también pueda ser consumida por niche_discoverer.py (Modo SPY-ARBITRAGE y
Modo ARQUEOLOGÍA DIGITAL).

Arquitectura de 3 niveles (se conserva la regla de oro):
  1. scrapetube (primario)        — Feed real de YouTube con proxy scrapegw
  2. YouTube Data API v3 (fallback) — Si scrapetube falla, API oficial
  3. Nunca lanza — siempre devuelve estructura válida

Funciones públicas:
  - scan_competition(keyword)           → Competencia ES/EN (reemplazo 1:1
                                          de lo que hacía el validator).
  - search_viral_english(query, ...)    → Para Modo SPY-ARBITRAGE: busca
                                          videos EN virales del último mes.
  - count_competing_spanish(keyword, ...) → Para Modo ARQUEOLOGÍA DIGITAL:
                                            cuenta videos ES que superan
                                            N views en una ventana de meses
                                            (Regla 3-50-24).
  - detect_language(title)              → Helper público
  - is_fresh(time_text)                 → Helper público

IMPORTANTE — REGLAS DE ORO (no tocar):
  * Usa el mismo parche de urllib3.util.retry que el validator
  * Usa el proxy scrapegw con el mismo patrón de sesiones
  * El fallback a YouTube Data API v3 sigue siendo estrictamente secundario
"""

import random
import re
import string
from datetime import datetime, timedelta
from typing import Literal

import requests
import urllib3.util.retry

from config import api
from error_handler import error_handler, PipelineStage


# ═══════════════════════════════════════════════════════════════
#  PARCHE urllib3 (mismo que topic_validator.py)
# ═══════════════════════════════════════════════════════════════
# pytrends/scrapetube usan `method_whitelist` (Retry antiguo) pero
# urllib3 moderno lo renombró a `allowed_methods`. Sin este parche,
# scrapetube lanza TypeError al inicializar Retry.
_orig_retry_init = urllib3.util.retry.Retry.__init__


def _patched_retry_init(self, *args, **kwargs):
    if "method_whitelist" in kwargs:
        kwargs["allowed_methods"] = kwargs.pop("method_whitelist")
    _orig_retry_init(self, *args, **kwargs)


urllib3.util.retry.Retry.__init__ = _patched_retry_init


# ─── Imports que dependen del parche ───
import scrapetube
from langdetect import detect, DetectorFactory

DetectorFactory.seed = 0  # langdetect determinista


# ═══════════════════════════════════════════════════════════════
#  CONSTANTES
# ═══════════════════════════════════════════════════════════════

YT_LIMIT_DEFAULT: int = 25              # Videos a escanear por búsqueda
YT_LIMIT_ARBITRAGE: int = 30            # Para Modo SPY-ARBITRAGE (más amplio)
YT_LIMIT_ARCHAEOLOGY: int = 50          # Para Modo ARQUEOLOGÍA (ventana 24 meses)
API_MAX_RESULTS: int = 15               # Máximo por llamada a YT Data API v3


# ═══════════════════════════════════════════════════════════════
#  PROXY HELPERS
# ═══════════════════════════════════════════════════════════════

def _build_proxy_url(session_id: str | None = None) -> str:
    """Construye URL del proxy scrapegw con sesión opcional."""
    user = api.proxy_user
    if session_id:
        user = f"{user}-session-{session_id}"
    return f"http://{user}:{api.proxy_pass}@{api.proxy_host}"


def _proxies_dict() -> dict:
    """Dict de proxies para requests/scrapetube."""
    url = _build_proxy_url()
    return {"http": url, "https": url}


def _random_session_id() -> str:
    """Genera session_id aleatorio para rotación anti-ban."""
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=12))


# ═══════════════════════════════════════════════════════════════
#  DETECCIÓN DE IDIOMA Y FRESCURA
# ═══════════════════════════════════════════════════════════════

def detect_language(title: str) -> Literal["es", "en", "other"]:
    """Detecta idioma del título. 'es', 'en' o 'other'."""
    try:
        lang = detect(title)
        if lang == "es":
            return "es"
        if lang == "en":
            return "en"
        return "other"
    except Exception:
        return "other"


def is_fresh(time_text: str) -> bool:
    """Detecta si un video es reciente (última semana)."""
    t = time_text.lower()
    return any(x in t for x in ["hora", "día", "dia", "semana", "hour", "day", "week"])


def _parse_views_scrapetube(vid: dict) -> int:
    """
    Extrae el conteo de views de un objeto video de scrapetube.
    Scrapetube devuelve strings como '1.2M views' o '250K vistas'.
    Devuelve 0 si no se puede parsear.
    """
    try:
        views_text = vid.get("viewCountText", {}).get("simpleText", "")
        if not views_text:
            # A veces viene como "shortViewCountText"
            views_text = vid.get("shortViewCountText", {}).get("simpleText", "")
        if not views_text:
            return 0

        # "1.2M views", "250K vistas", "1,234,567 views"
        views_text = views_text.lower().replace(",", "").replace(".", "")
        match = re.search(r"([\d]+)\s*([kmb])?", views_text)
        if not match:
            return 0

        number = int(match.group(1))
        suffix = match.group(2) or ""
        multipliers = {"k": 1_000, "m": 1_000_000, "b": 1_000_000_000, "": 1}
        return number * multipliers.get(suffix, 1)
    except Exception:
        return 0


def _parse_date_scrapetube_months_ago(time_text: str) -> int:
    """
    Estima cuántos meses atrás fue publicado un video según scrapetube.
    "hace 2 días" → 0, "hace 3 semanas" → 0, "hace 2 meses" → 2, "hace 1 año" → 12.
    Devuelve 999 si no se puede parsear (conservador: lo considera viejo).
    """
    t = time_text.lower()
    match = re.search(r"(\d+)", t)
    if not match:
        return 999
    n = int(match.group(1))

    if "día" in t or "dia" in t or "day" in t or "hora" in t or "hour" in t or "semana" in t or "week" in t:
        return 0
    if "mes" in t or "month" in t:
        return n
    if "año" in t or "year" in t:
        return n * 12
    return 999


# ═══════════════════════════════════════════════════════════════
#  FILTRO DE PALABRAS-ANCLA (reduce falsos positivos por query genérica)
# ═══════════════════════════════════════════════════════════════
# YouTube/scrapetube buscan por relevancia, no por exact match. Una query
# como "El Bloop el sonido más fuerte del océano" matchea videos genéricos
# de "monstruos marinos" sin que mencionen Bloop. Este filtro descarta
# videos cuyo título no contiene al menos UNA palabra-ancla del keyword.

# Stopwords ES + genéricos del nicho marino/misterio (matchean cualquier
# video del tema y no sirven como ancla discriminante).
_STOPWORDS: set[str] = {
    # Artículos / preposiciones / conectores
    "el", "la", "los", "las", "un", "una", "unos", "unas",
    "de", "del", "en", "a", "al", "y", "o", "u", "que", "para",
    "por", "con", "sin", "sobre", "entre", "hasta", "hacia",
    "desde", "durante", "ante", "bajo", "contra", "según",
    "tras", "mediante", "mas", "pero", "sino", "si", "no",
    "ya", "también", "además", "así", "tan", "muy", "más",
    "menos", "mucho", "poco", "su", "sus", "mi", "mis",
    "tu", "tus", "cómo", "cuándo", "dónde", "qué", "quién",
    "es", "son", "fue", "fueron", "era", "eran", "ha", "han",
    "cerca", "donde", "cuando",
    # Genéricos del nicho marino/misterio
    "sonido", "sonidos", "ruido", "ruidos",
    "océano", "oceano", "mar", "mares", "marino", "marinos",
    "agua", "aguas", "profundidad", "profundo", "abismo",
    "año", "años", "día", "días", "mes", "meses",
    "fuerte", "fuertes", "extraño", "extraños",
    "misterio", "misterios", "misterioso", "misteriosa",
    "historia", "historias",
    "captado", "captados", "registrado", "registrados",
    "barco", "barcos", "submarino", "submarinos",
    "desaparición", "desaparecieron", "desaparecido",
}


def extract_anchors(text: str) -> list[str]:
    """
    Extrae palabras-ancla discriminantes de un keyword o título.

    Heurísticas (en orden de prioridad):
      1. Años (4 dígitos: 19XX o 20XX)
      2. Códigos alfanuméricos (USS, MV, K-129, SS-21, MS, etc.)
      3. Nombres propios (mayúscula inicial, no stopword, ≥4 letras)
      4. Fallback: cualquier palabra ≥5 letras no-stopword

    Returns:
        Lista ordenada de anclas en minúsculas, sin duplicados. Lista vacía
        si no se pudo extraer nada (en ese caso el filtro pasa todo).
    """
    anchors: set[str] = set()

    # 1. Años
    for year in re.findall(r"\b(19\d{2}|20\d{2})\b", text):
        anchors.add(year)

    # 2. Códigos: USS, MV, MS, K-129, SS-X, etc.
    for code in re.findall(r"\b[A-Z]{2,4}(?:[\-\s][A-Z0-9]+)?\b", text):
        clean = code.lower().replace(" ", "-")
        if clean and clean not in _STOPWORDS:
            anchors.add(clean)
            # Versión sin guión por si scrapetube los normaliza
            anchors.add(clean.replace("-", ""))

    # 3. Nombres propios: tokens con mayúscula inicial
    tokens = text.split()
    for tok in tokens:
        clean = re.sub(r"[^\wáéíóúñü]", "", tok, flags=re.IGNORECASE).lower()
        if not clean or clean in _STOPWORDS:
            continue
        if tok[0].isupper() and len(clean) >= 4:
            anchors.add(clean)

    # 4. Fallback: palabras ≥5 letras
    if not anchors:
        for tok in tokens:
            clean = re.sub(r"[^\wáéíóúñü]", "", tok, flags=re.IGNORECASE).lower()
            if clean and len(clean) >= 5 and clean not in _STOPWORDS:
                anchors.add(clean)

    return sorted(anchors)


def title_contains_anchor(title: str, anchors: list[str] | None) -> bool:
    """
    True si el título contiene al menos una palabra-ancla
    (case-insensitive, word-boundary). Sin anclas (None o []) = pasa todo.
    """
    if not anchors:
        return True
    title_lower = title.lower()
    for a in anchors:
        # Word boundary excepto para códigos cortos o con guión
        if "-" in a or len(a) <= 3:
            if a in title_lower:
                return True
        else:
            if re.search(rf"\b{re.escape(a)}\b", title_lower):
                return True
    return False



# ═══════════════════════════════════════════════════════════════
#  FUNCIÓN 1 — scan_competition (reemplaza lógica del validator)
# ═══════════════════════════════════════════════════════════════

@error_handler.retry(PipelineStage.TOPIC_VALIDATOR, max_retries=2)
def _scrape_es_en(keyword: str, limit: int = YT_LIMIT_DEFAULT) -> dict:
    """
    Primario — scrapetube. Cuenta videos ES/EN + frescos por idioma.
    Idéntica a la función que estaba en topic_validator.
    """
    report = {
        "source": "scrapetube",
        "es": {"total": 0, "fresh": 0, "titles": []},
        "en": {"total": 0, "fresh": 0, "titles": []},
        "other": 0,
        "error": None,
    }

    videos = list(
        scrapetube.get_search(
            keyword,
            limit=limit,
            proxies=_proxies_dict(),
        )
    )

    for vid in videos:
        try:
            title = vid["title"]["runs"][0]["text"]
        except (KeyError, IndexError):
            continue

        time_text = vid.get("publishedTimeText", {}).get("simpleText", "")
        lang = detect_language(title)

        if lang in ("es", "en"):
            report[lang]["total"] += 1
            if is_fresh(time_text):
                report[lang]["fresh"] += 1
            if len(report[lang]["titles"]) < 3:
                report[lang]["titles"].append(title[:80])
        else:
            report["other"] += 1

    return report


@error_handler.retry(PipelineStage.TOPIC_VALIDATOR, max_retries=2)
def _api_fallback_es_en(keyword: str) -> dict:
    """
    Fallback — YouTube Data API v3 (10K units/día, oficial).
    Se activa SOLO cuando scrapetube falla.
    """
    error_handler.log_warning(
        PipelineStage.TOPIC_VALIDATOR,
        f"[youtube_scanner] Activando fallback YouTube API para '{keyword}'",
    )

    report = {
        "source": "youtube_api_fallback",
        "es": {"total": 0, "fresh": 0, "titles": []},
        "en": {"total": 0, "fresh": 0, "titles": []},
        "other": 0,
        "error": None,
    }

    for lang_code in ("es", "en"):
        try:
            resp = requests.get(
                f"{api.youtube_base_url}/search",
                params={
                    "part": "snippet",
                    "q": keyword,
                    "type": "video",
                    "maxResults": API_MAX_RESULTS,
                    "order": "relevance",
                    "relevanceLanguage": lang_code,
                    "publishedAfter": (datetime.now() - timedelta(days=365)).isoformat("T") + "Z",
                    "key": api.youtube_api_key,
                },
                timeout=15,
            )
            resp.raise_for_status()
            items = resp.json().get("items", [])

            one_week_ago = datetime.now() - timedelta(days=7)
            for it in items:
                snippet = it.get("snippet", {})
                title = snippet.get("title", "")
                published = snippet.get("publishedAt", "")[:10]

                report[lang_code]["total"] += 1
                try:
                    pub_date = datetime.fromisoformat(published)
                    if pub_date > one_week_ago:
                        report[lang_code]["fresh"] += 1
                except Exception:
                    pass

                if len(report[lang_code]["titles"]) < 3:
                    report[lang_code]["titles"].append(title[:80])

        except Exception as e:
            report["error"] = f"YouTube API fallback falló en '{lang_code}': {e}"
            break

    return report


def scan_competition(keyword: str, limit: int = YT_LIMIT_DEFAULT) -> dict:
    """
    Función pública principal.
    Intenta scrapetube → cae a YouTube API si falla.
    SIEMPRE devuelve estructura válida (nunca lanza).

    Usada por:
      - topic_validator.py (validación de competencia de un topic)

    Returns:
        dict con claves: source, es{total,fresh,titles}, en{...}, other, error
    """
    try:
        return _scrape_es_en(keyword, limit=limit)
    except Exception as e:
        error_handler.log_warning(
            PipelineStage.TOPIC_VALIDATOR,
            f"[youtube_scanner] scrapetube falló para '{keyword}': {e}. Fallback API...",
        )
        try:
            return _api_fallback_es_en(keyword)
        except Exception as e2:
            error_handler.log_error(
                PipelineStage.TOPIC_VALIDATOR, e2,
                context={"keyword": keyword, "stage": "both_failed"},
            )
            return {
                "source": "FAILED",
                "es": {"total": -1, "fresh": -1, "titles": []},
                "en": {"total": -1, "fresh": -1, "titles": []},
                "other": 0,
                "error": f"Ambos fallaron: {e2}",
            }


# ═══════════════════════════════════════════════════════════════
#  FUNCIÓN 2 — search_viral_english (para SPY-ARBITRAGE)
# ═══════════════════════════════════════════════════════════════

@error_handler.retry(PipelineStage.NICHE_DISCOVERER, max_retries=2)
def _scrape_viral_english(query: str, min_views: int, limit: int) -> list[dict]:
    """
    Primario — scrapetube. Videos EN con >= min_views publicados en últimos 30 días.
    """
    results = []
    videos = list(
        scrapetube.get_search(
            query,
            limit=limit,
            proxies=_proxies_dict(),
        )
    )

    for vid in videos:
        try:
            title = vid["title"]["runs"][0]["text"]
        except (KeyError, IndexError):
            continue

        # Solo inglés
        if detect_language(title) != "en":
            continue

        time_text = vid.get("publishedTimeText", {}).get("simpleText", "")
        months_ago = _parse_date_scrapetube_months_ago(time_text)
        if months_ago > 6:  # último 6 meses
            continue

        views = _parse_views_scrapetube(vid)
        if views < min_views:
            continue

        results.append({
            "title": title,
            "views": views,
            "published_text": time_text,
            "video_id": vid.get("videoId", ""),
            "source": "scrapetube",
        })

    # Ordenar por views descendente
    results.sort(key=lambda x: x["views"], reverse=True)
    return results


@error_handler.retry(PipelineStage.NICHE_DISCOVERER, max_retries=2)
def _api_fallback_viral_english(query: str, min_views: int) -> list[dict]:
    """Fallback — YouTube Data API v3 para SPY-ARBITRAGE."""
    error_handler.log_warning(
        PipelineStage.NICHE_DISCOVERER,
        f"[youtube_scanner] Fallback API para viral EN '{query}'",
    )

    results = []
    one_month_ago = (datetime.now() - timedelta(days=30)).isoformat("T") + "Z"

    try:
        # Paso 1: search
        resp = requests.get(
            f"{api.youtube_base_url}/search",
            params={
                "part": "snippet",
                "q": query,
                "type": "video",
                "maxResults": API_MAX_RESULTS,
                "order": "viewCount",
                "relevanceLanguage": "en",
                "publishedAfter": one_month_ago,
                "key": api.youtube_api_key,
            },
            timeout=15,
        )
        resp.raise_for_status()
        items = resp.json().get("items", [])
        video_ids = [it["id"]["videoId"] for it in items if it.get("id", {}).get("videoId")]

        if not video_ids:
            return []

        # Paso 2: videos.list (para obtener viewCount real)
        resp2 = requests.get(
            f"{api.youtube_base_url}/videos",
            params={
                "part": "snippet,statistics",
                "id": ",".join(video_ids),
                "key": api.youtube_api_key,
            },
            timeout=15,
        )
        resp2.raise_for_status()
        videos_data = resp2.json().get("items", [])

        for v in videos_data:
            title = v.get("snippet", {}).get("title", "")
            views = int(v.get("statistics", {}).get("viewCount", 0))
            if views < min_views:
                continue
            results.append({
                "title": title,
                "views": views,
                "published_text": v.get("snippet", {}).get("publishedAt", "")[:10],
                "video_id": v.get("id", ""),
                "source": "youtube_api_fallback",
            })

    except Exception as e:
        error_handler.log_error(
            PipelineStage.NICHE_DISCOVERER, e,
            context={"query": query, "stage": "api_fallback_viral"},
        )
        return []

    results.sort(key=lambda x: x["views"], reverse=True)
    return results


def search_viral_english(
    query: str,
    min_views: int = 1_000_000,
    limit: int = YT_LIMIT_ARBITRAGE,
) -> list[dict]:
    """
    Busca videos virales en INGLÉS del último mes con >= min_views.

    Usada por:
      - niche_discoverer.py (Modo SPY-ARBITRAGE)

    Returns:
        Lista de dicts: [{title, views, published_text, video_id, source}, ...]
        Ordenada por views desc. Lista vacía si no hay resultados.
    """
    try:
        return _scrape_viral_english(query, min_views=min_views, limit=limit)
    except Exception as e:
        error_handler.log_warning(
            PipelineStage.NICHE_DISCOVERER,
            f"[youtube_scanner] scrapetube viral-EN falló: {e}. Fallback API...",
        )
        try:
            return _api_fallback_viral_english(query, min_views=min_views)
        except Exception as e2:
            error_handler.log_error(
                PipelineStage.NICHE_DISCOVERER, e2,
                context={"query": query, "stage": "viral_en_both_failed"},
            )
            return []


# ═══════════════════════════════════════════════════════════════
#  FUNCIÓN 3 — count_competing_spanish (ARQUEOLOGÍA / Regla 3-50-24)
# ═══════════════════════════════════════════════════════════════


@error_handler.retry(PipelineStage.NICHE_DISCOVERER, max_retries=2)
def _scrape_spanish_competition(
    keyword: str,
    min_views: int,
    window_months: int,
    limit: int,
    anchors: list[str] | None = None,
) -> dict:
    """
    Primario — scrapetube. Cuenta videos ES que:
      - Publicados en últimos `window_months` meses
      - Tienen >= min_views
      - Si `anchors` no es None/vacío: el título debe contener al menos
        una palabra-ancla (descarta falsos positivos por query genérica).
    """
    report = {
        "source": "scrapetube",
        "keyword": keyword,
        "competing_count": 0,
        "window_months": window_months,
        "min_views_threshold": min_views,
        "anchors_used": anchors or [],
        "top_titles": [],
        "error": None,
    }

    videos = list(
        scrapetube.get_search(
            keyword,
            limit=limit,
            proxies=_proxies_dict(),
        )
    )

    for vid in videos:
        try:
            title = vid["title"]["runs"][0]["text"]
        except (KeyError, IndexError):
            continue

        if detect_language(title) != "es":
            continue

        time_text = vid.get("publishedTimeText", {}).get("simpleText", "")
        months_ago = _parse_date_scrapetube_months_ago(time_text)
        if months_ago > window_months:
            continue

        views = _parse_views_scrapetube(vid)
        if views < min_views:
            continue

        # Filtro de ancla (compatible hacia atrás: si anchors es None/vacío, pasa)
        if not title_contains_anchor(title, anchors):
            continue

        report["competing_count"] += 1
        if len(report["top_titles"]) < 5:
            report["top_titles"].append({
                "title": title[:80],
                "views": views,
                "published_text": time_text,
            })

    return report

@error_handler.retry(PipelineStage.NICHE_DISCOVERER, max_retries=2)
def _api_fallback_spanish_competition(
    keyword: str,
    min_views: int,
    window_months: int,
    anchors: list[str] | None = None,
) -> dict:
    """Fallback — YouTube Data API v3 con filtro de anclas opcional."""
    error_handler.log_warning(
        PipelineStage.NICHE_DISCOVERER,
        f"[youtube_scanner] Fallback API para ES competition '{keyword}'",
    )

    report = {
        "source": "youtube_api_fallback",
        "keyword": keyword,
        "competing_count": 0,
        "window_months": window_months,
        "min_views_threshold": min_views,
        "anchors_used": anchors or [],
        "top_titles": [],
        "error": None,
    }

    cutoff = (datetime.now() - timedelta(days=30 * window_months)).isoformat("T") + "Z"

    try:
        # Paso 1: search
        resp = requests.get(
            f"{api.youtube_base_url}/search",
            params={
                "part": "snippet",
                "q": keyword,
                "type": "video",
                "maxResults": API_MAX_RESULTS,
                "order": "viewCount",
                "relevanceLanguage": "es",
                "publishedAfter": cutoff,
                "key": api.youtube_api_key,
            },
            timeout=15,
        )
        resp.raise_for_status()
        items = resp.json().get("items", [])
        video_ids = [it["id"]["videoId"] for it in items if it.get("id", {}).get("videoId")]

        if not video_ids:
            return report

        # Paso 2: videos.list
        resp2 = requests.get(
            f"{api.youtube_base_url}/videos",
            params={
                "part": "snippet,statistics",
                "id": ",".join(video_ids),
                "key": api.youtube_api_key,
            },
            timeout=15,
        )
        resp2.raise_for_status()
        videos_data = resp2.json().get("items", [])

        for v in videos_data:
            title = v.get("snippet", {}).get("title", "")
            views = int(v.get("statistics", {}).get("viewCount", 0))
            if views < min_views:
                continue

            # Filtro de ancla (compatible hacia atrás)
            if not title_contains_anchor(title, anchors):
                continue

            report["competing_count"] += 1
            if len(report["top_titles"]) < 5:
                report["top_titles"].append({
                    "title": title[:80],
                    "views": views,
                    "published_text": v.get("snippet", {}).get("publishedAt", "")[:10],
                })

    except Exception as e:
        report["error"] = f"API fallback falló: {e}"

    return report

def count_competing_spanish(
    keyword: str,
    min_views: int = 50_000,
    window_months: int = 24,
    limit: int = YT_LIMIT_ARCHAEOLOGY,
    anchors: list[str] | None = None,
) -> dict:
    """
    Cuenta videos ES que compiten con el tema (Regla 3-50-24).

    Args:
        keyword:       query a enviar a YouTube/scrapetube.
        min_views:     umbral mínimo de views.
        window_months: ventana temporal (meses).
        limit:         videos a inspeccionar.
        anchors:       palabras-ancla opcionales. Si se pasan, el título de
                       cada video debe contener al menos una para contar
                       como competidor. Reduce drásticamente los falsos
                       positivos por query genérica. Si es None/vacío,
                       comportamiento idéntico al original (compatibilidad).

    Usada por:
      - niche_discoverer.py (Modo ARQUEOLOGÍA + Modo SPY-ARBITRAGE) → con anclas
      - topic_validator.py  (chequeo APUESTA_VIRAL)                 → sin anclas

    Returns:
        dict con competing_count, top_titles, anchors_used, etc.
        Si competing_count <= 3 y el trend score > 70 → HUECO HISTÓRICO.
    """
    try:
        return _scrape_spanish_competition(
            keyword,
            min_views=min_views,
            window_months=window_months,
            limit=limit,
            anchors=anchors,
        )
    except Exception as e:
        error_handler.log_warning(
            PipelineStage.NICHE_DISCOVERER,
            f"[youtube_scanner] scrapetube ES-comp falló: {e}. Fallback API...",
        )
        try:
            return _api_fallback_spanish_competition(
                keyword,
                min_views=min_views,
                window_months=window_months,
                anchors=anchors,
            )
        except Exception as e2:
            error_handler.log_error(
                PipelineStage.NICHE_DISCOVERER, e2,
                context={"keyword": keyword, "stage": "es_comp_both_failed"},
            )
            return {
                "source": "FAILED",
                "keyword": keyword,
                "competing_count": -1,
                "window_months": window_months,
                "min_views_threshold": min_views,
                "anchors_used": anchors or [],
                "top_titles": [],
                "error": f"Ambos fallaron: {e2}",
            }
# ═══════════════════════════════════════════════════════════════
#  CLI de diagnóstico (opcional)
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Uso:")
        print("  python -m modules.youtube_scanner scan <keyword>")
        print("  python -m modules.youtube_scanner viral <query>")
        print("  python -m modules.youtube_scanner spanish <keyword>")
        sys.exit(1)

    mode, arg = sys.argv[1], sys.argv[2]

    if mode == "scan":
        result = scan_competition(arg)
    elif mode == "viral":
        result = search_viral_english(arg)
    elif mode == "spanish":
        result = count_competing_spanish(arg)
    else:
        print(f"Modo desconocido: {mode}")
        sys.exit(1)

    import json
    print(json.dumps(result, indent=2, ensure_ascii=False))
