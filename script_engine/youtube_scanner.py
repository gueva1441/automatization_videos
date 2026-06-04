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
import statistics
import string
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
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
    """Dict de proxies para requests/scrapetube.

    CHAT 42: ahora ROTA la sesión (IP residencial fresca) en cada llamada vía
    _random_session_id() — antes la rotación estaba construida pero MUERTA (IP única).
    El flujo invertido de Mode A multiplica las llamadas (get_channel por candidato);
    sin rotación, varias puertas devolvían 0 por throttling. La sesión queda fija
    DENTRO de una sola llamada scrapetube (la paginación de un get_channel usa el mismo
    proxies dict), pero distintas llamadas top-level reciben IPs distintas (anti-ban)."""
    url = _build_proxy_url(_random_session_id())
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
    Extrae el conteo de views de un objeto video de get_search (estructura vieja).
    Scrapetube devuelve strings como '1.2M views' o '250K vistas'.

    CHAT 42: el cuerpo ahora usa parse_views_fixed (ver abajo) → arregla de paso el
    bug del decimal ('1.2M' daba 12M con el .replace('.','') viejo). La firma pública
    se mantiene para no romper callers (count_competing_spanish, scan_competition, etc.).
    Devuelve 0 si no se puede parsear.
    """
    try:
        views_text = vid.get("viewCountText", {}).get("simpleText", "")
        if not views_text:
            # A veces viene como "shortViewCountText"
            views_text = vid.get("shortViewCountText", {}).get("simpleText", "")
        return parse_views_fixed(views_text)
    except Exception:
        return 0


def _parse_length_scrapetube(vid: dict) -> int | None:
    """Duración en segundos desde lengthText de get_search ('M:SS'|'MM:SS'|'H:MM:SS').
    None si falta/no parsea (fail-open → no descarta por las dudas)."""
    txt = (vid.get("lengthText", {}) or {}).get("simpleText", "")
    if not txt or ":" not in txt:
        return None
    try:
        parts = [int(p) for p in txt.split(":")]
    except ValueError:
        return None
    secs = 0
    for p in parts:
        secs = secs * 60 + p
    return secs


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

# ═══════════════════════════════════════════════════════════════
#  FILTRO OUTLIER EN — flujo invertido Mode A (chat 42)
# ═══════════════════════════════════════════════════════════════
# Portado del lab _lab_molde1_chat42.py (validado end-to-end con 28 videos reales).
# El volumen calibrado de la fórmula NO se cambia sin Omar.
#
# NOTA de ubicación (desvío honesto del handoff §1): el handoff pedía estas
# constantes en niche_discoverer.py "junto a SPY_*". Pero compute_outlier_filter
# (handoff §3.2) vive ACÁ, y niche_discoverer IMPORTA youtube_scanner (no al revés)
# → ponerlas allá crearía import circular. Viven con el filtro que las usa. El
# tuning de Omar es sobre estas constantes.

OUTLIER_MIN: float = 3.0          # ratio mínimo vs mediana del canal
PISO_MEDIANA: int = 2_000         # mediana del canal mínima para CREER el ratio (mata canal muerto)
ABS_FLOOR: int = 50_000           # views mínimas (chat 43: 80K→50K, +2 joyas temáticas canal sano)
PISO_DEMANDA: int = 3_000_000     # views que entran solo por VOLUMEN (demanda probada)
BASELINE_N: int = 30              # uploads del canal para la mediana
MIN_BASELINE_VIDEOS: int = 5      # < esto → baseline no confiable → no pasa por outlier
EN_CANDIDATES_PER_QUERY: int = 20  # tope de candidatos EN por puerta (chat 43: 5→20, joyas viven pos 9-17)
EN_OUTLIER_SLEEP_SEC: float = 2.0  # anti-ban entre get_channel
EN_MIN_DURATION_SEC: int = 5 * 60    # CHAT 44: piso de duración (mata clips muy cortos). TUNABLE.
EN_MAX_DURATION_SEC: int = 50 * 60   # CHAT 44: techo (mata compilaciones 2-4h). ← el de alto valor.
EN_OUTLIER_WORKERS: int = 3   # CHAT 44: workers para fetch de baselines (ceiling = proxy concurrency)

# CHAT 44: score de saturación ES (reemplaza ≥50k/3meses en spy-arbitrage). Cortes del medio
# (HUECO/DISPUTADO) son etiquetas BLANDAS para el ojo humano, no gates duros → tunables sin estrés.
ES_DECAY_TIERS: list = [(12, 1.0), (36, 0.6), (60, 0.3)]   # (meses_max, peso); más viejo → floor
ES_DECAY_FLOOR: float = 0.1
ES_SAT_HUECO: int = 30_000        # >0 y < esto = HUECO
ES_SAT_DISPUTADO: int = 150_000   # < esto = DISPUTADO; >= esto = SATURADO (se descarta)


def parse_views_fixed(text: str) -> int:
    """
    Parser numérico CORREGIDO (lab 41/42). Saca SOLO las comas (no el punto), captura
    [\\d.]+ como float, multiplica por k/m/b. Así '1.2M'→1_200_000 (el viejo hacía
    .replace('.','') → '12m' = 12M). '250K'→250_000, '1,234,567'→1_234_567.
    """
    if not text:
        return 0
    t = text.lower().replace(",", "")
    m = re.search(r"([\d.]+)\s*([kmb])?", t)
    if not m:
        return 0
    try:
        number = float(m.group(1))
    except ValueError:
        return 0
    mult = {"k": 1_000, "m": 1_000_000, "b": 1_000_000_000, "": 1}
    return int(number * mult.get(m.group(2) or "", 1))


# Paths candidatos donde get_search (estructura VIEJA) esconde el channelId (UC...).
_CHANNEL_ID_PATHS = ["longBylineText", "ownerText", "shortBylineText"]


def extract_channel_id(vid: dict) -> tuple[str | None, str | None]:
    """Sobre un objeto de GET_SEARCH (estructura vieja, NO cambió). Devuelve
    (channel_id, path_usado) o (None, None)."""
    for key in _CHANNEL_ID_PATHS:
        try:
            cid = (vid[key]["runs"][0]["navigationEndpoint"]
                   ["browseEndpoint"]["browseId"])
            if isinstance(cid, str) and cid.startswith("UC"):
                return cid, key
        except (KeyError, IndexError, TypeError):
            continue
    return None, None


def _channel_name_of_search(vid: dict) -> str:
    try:
        return vid["longBylineText"]["runs"][0]["text"]
    except (KeyError, IndexError, TypeError):
        return ""


def median_excluding(values: list[int], exclude_value: int | None = None) -> float | None:
    """Mediana de `values` > 0, quitando UNA ocurrencia de exclude_value (no medir el
    candidato contra sí mismo). None si quedan < MIN_BASELINE_VIDEOS."""
    vals = [v for v in values if v > 0]
    if exclude_value is not None and exclude_value in vals:
        vals.remove(exclude_value)
    if len(vals) < MIN_BASELINE_VIDEOS:
        return None
    return statistics.median(vals)


def compute_ratio(views: int, baseline: float | None) -> float:
    return views / baseline if baseline and baseline > 0 else 0.0


# ── Extractores del FORK night-0909 en get_channel (estructura NUEVA lockup/metadataRows) ──
# Sondeados y validados en el lab chat 42 (3 baches reales: tupla channelId, título
# string pelado, views en content O accessibilityLabel). Copiar EXACTO, no de memoria.

def _fork_metadata_rows(vid: dict) -> list:
    try:
        return (vid["metadata"]["lockupMetadataViewModel"]["metadata"]
                ["contentMetadataViewModel"]["metadataRows"])
    except (KeyError, TypeError):
        return []


def fork_views_text(vid: dict) -> str:
    """Identifica la parte de VIEWS recorriendo todas las metadataRows/metadataParts
    (la estructura VARÍA por canal: a veces content='191 views', a veces content='2.2K'
    + accessibilityLabel='2.2 thousand views'). Devuelve el content compacto que
    parse_views_fixed sabe leer ('2.2K'→2200)."""
    for row in _fork_metadata_rows(vid):
        for part in (row.get("metadataParts") or []):
            txt = (((part or {}).get("text") or {}).get("content")) or ""
            label = ((part or {}).get("accessibilityLabel")) or ""
            if any(w in s.lower() for s in (txt, label) for w in ("view", "vista")):
                return txt or label
    return ""


def fork_title(vid: dict) -> str:
    # En el fork, v["title"] es un STRING pelado (no {"content": ...}). Soportar ambas.
    t = vid.get("title")
    if isinstance(t, str):
        return t or "<sin título>"
    if isinstance(t, dict):
        return t.get("content") or "<sin título>"
    return "<sin título>"


def fork_views(vid: dict) -> int:
    return parse_views_fixed(fork_views_text(vid))


def _get_channel_videos(channel_id: str, limit: int) -> list:
    """get_channel del FORK con fallback si la versión no acepta proxies. Nunca lanza.

    CHAT 42 — rotación POR CANAL (no por request): se pide UNA IP fresca para ESTE canal
    (proxies se evalúa UNA vez acá) y se reusa en TODA su paginación interna → session_id
    fijo → scrapegw sticky a la misma IP para todo el get_channel. El SIGUIENTE canal
    (otra llamada a esta función) pide otra IP. NO rotar por request dentro de un canal:
    rompería la paginación. proxies se captura en variable a propósito (no inline) para
    que esta garantía sea explícita y no regrese."""
    proxies = _proxies_dict()   # una IP para todo este canal (toda su paginación)
    try:
        return list(scrapetube.get_channel(
            channel_id=channel_id, limit=limit, proxies=proxies))
    except TypeError:
        try:
            return list(scrapetube.get_channel(channel_id=channel_id, limit=limit))
        except Exception:  # noqa: BLE001
            return []
    except Exception:  # noqa: BLE001
        return []


def _channel_baseline(channel_id: str, n: int, exclude: int) -> float | None:
    """Mediana de las views (parser corregido, vía extractor del fork) de los uploads
    del canal, excluyendo el video candidato. None si < MIN_BASELINE_VIDEOS parseables."""
    ups = _get_channel_videos(channel_id, n)
    views_list = [fork_views(u) for u in ups]
    return median_excluding(views_list, exclude_value=exclude)


def passes_en_filter(views: int, ratio: float, median: float | None) -> bool:
    """Filtro de UNIÓN: pasa por VOLUMEN (demanda probada) O por OUTLIER (ratio sobre
    un canal vivo). Calibrado chat 42 — NO cambiar los números sin Omar."""
    volumen = views >= PISO_DEMANDA
    outlier = (median is not None and median >= PISO_MEDIANA
               and ratio >= OUTLIER_MIN and views >= ABS_FLOOR)
    return volumen or outlier


def compute_outlier_filter(candidates: list[dict]) -> list[dict]:
    """
    Toma los candidatos EN crudos de todas las puertas de un nicho y devuelve los que
    pasan el filtro de unión. Dedupe por video_id; baseline por canal cacheado
    (get_channel-fork); enriquece cada dict con {views, median, ratio} para trazabilidad.
    """
    # dedupe por video_id (un video sale en varias puertas)
    seen: set[str] = set()
    deduped: list[dict] = []
    for c in candidates:
        vid_id = c.get("video_id") or ""
        if vid_id and vid_id in seen:
            continue
        if vid_id:
            seen.add(vid_id)
        deduped.append(c)

    # CHAT 44: baselines por canal en PARALELO (3 workers). Cada get_channel monta su IP via
    # _proxies_dict() (rotación sticky por canal) → 3 workers = 3 IPs → spreads, no apila. Se quita
    # el sleep secuencial (la rotación maneja el ban). La MATEMÁTICA del filtro NO cambia.
    # exclude = views del PRIMER candidato de cada canal (mirror exacto del comportamiento secuencial).
    first_views_by_cid: dict[str, int] = {}
    for c in deduped:
        cid = c.get("channel_id")
        if cid and cid not in first_views_by_cid:
            first_views_by_cid[cid] = int(c.get("views") or 0)

    baseline_cache: dict[str, float | None] = {}

    def _fetch_baseline(cid: str, exclude_views: int):
        return cid, _channel_baseline(cid, BASELINE_N, exclude=exclude_views)

    with ThreadPoolExecutor(max_workers=EN_OUTLIER_WORKERS) as ex:
        futures = [ex.submit(_fetch_baseline, cid, ev) for cid, ev in first_views_by_cid.items()]
        for fut in as_completed(futures):
            cid, median = fut.result()
            baseline_cache[cid] = median

    kept: list[dict] = []
    for c in deduped:
        views = int(c.get("views") or 0)
        cid = c.get("channel_id")
        median = baseline_cache.get(cid) if cid else None
        ratio = compute_ratio(views, median) if median else 0.0
        enriched = {**c, "views": views, "median": median, "ratio": ratio,
                    "passed_reason": ("volumen" if views >= PISO_DEMANDA
                                      else ("outlier" if passes_en_filter(views, ratio, median)
                                            else ""))}
        if passes_en_filter(views, ratio, median):
            kept.append(enriched)
    return kept


@error_handler.retry(PipelineStage.NICHE_DISCOVERER, max_retries=2)
def _scrape_viral_english(query: str, min_views: int, limit: int) -> list[dict]:
    """
    Primario — scrapetube. Videos EN publicados en últimos meses.

    CHAT 42 (flujo invertido): ya NO filtra por views absolutas (min_views default 0
    = no-op). El filtro real es posterior (compute_outlier_filter, unión ratio/volumen).
    Agrega `channel_id` + `channel_name` al dict (necesarios para el baseline del canal).
    """
    results = []
    dropped_dur = 0
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
        # CHAT 42: ventana temporal QUITADA del flujo invertido. El filtro outlier busca
        # contenido PROBADO (no solo fresco) — igual que el lab que calibró la fórmula
        # (sin ventana). El frescor ya no decide; lo decide ratio/volumen (filtro unión).
        # (Se mantiene published_text en el dict para trazabilidad.)

        views = _parse_views_scrapetube(vid)
        if views < min_views:   # CHAT 42: no-op con min_views=0 (filtro real = unión)
            continue

        # CHAT 44: filtro de duración (lengthText gratis). Mata compilaciones 2-4h ANTES del
        # compute_outlier_filter (ahorra get_channel). Fail-open: si no parsea, NO descarta.
        dur = _parse_length_scrapetube(vid)
        if dur is not None and not (EN_MIN_DURATION_SEC <= dur <= EN_MAX_DURATION_SEC):
            dropped_dur += 1
            continue

        cid, _ = extract_channel_id(vid)   # CHAT 42: para el baseline del canal
        results.append({
            "title": title,
            "views": views,
            "published_text": time_text,
            "video_id": vid.get("videoId", ""),
            "channel_id": cid,
            "channel_name": _channel_name_of_search(vid),
            "source": "scrapetube",
        })

    if dropped_dur:
        print(f"      ⏱ '{query}': {dropped_dur} descartados por duración "
              f"({EN_MIN_DURATION_SEC // 60}-{EN_MAX_DURATION_SEC // 60} min)")
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
    min_views: int = 0,
    limit: int = YT_LIMIT_ARBITRAGE,
) -> list[dict]:
    """
    Busca videos EN del último(s) mes(es). CHAT 42: min_views default 0 → ya NO filtra
    por views absolutas (el filtro real es compute_outlier_filter, unión ratio/volumen).
    El arg se mantiene por compat.

    Usada por:
      - niche_discoverer.py (Modo SPY-ARBITRAGE, flujo invertido)

    Returns:
        Lista de dicts: [{title, views, published_text, video_id, channel_id,
        channel_name, source}, ...]. Ordenada por views desc. Lista vacía si no hay.
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


def _es_age_decay(months: int) -> float:
    for max_m, w in ES_DECAY_TIERS:
        if months <= max_m:
            return w
    return ES_DECAY_FLOOR


def _es_saturation_label(sat: float) -> str:
    if sat <= 0:                  return "VACIO"
    if sat < ES_SAT_HUECO:        return "HUECO"
    if sat < ES_SAT_DISPUTADO:    return "DISPUTADO"
    return "SATURADO"


def _es_pub_text(vid: dict) -> str:
    """Texto de fecha robusto: simpleText, y si vacío cae a runs[].text."""
    p = vid.get("publishedTimeText", {}) or {}
    if p.get("simpleText"):
        return p["simpleText"]
    return "".join(r.get("text", "") for r in (p.get("runs") or []))


def score_spanish_saturation(keyword: str, anchors: list[str] | None = None,
                             limit: int = YT_LIMIT_ARCHAEOLOGY) -> dict:
    """CHAT 44: mide saturación ES por cobertura ponderada (views × decay de edad), SIN ventana
    cliff ni piso de 50k. Saturación del tema = competidor más pesado (max views efectivas).
    Reemplaza count_competing_spanish SOLO en spy-arbitrage. (count_competing_spanish queda intacto
    para topic_validator y Mode B.) Validado en lab chat 44: Apolo→SATURADO, Kielland→VACIO,
    Kursk→SATURADO (cazó el viral ES fresco que el chequeo viejo se salteaba)."""
    report = {"source": "scrapetube", "keyword": keyword, "saturation": 0.0, "label": "VACIO",
              "heaviest": None, "ontopic_count": 0, "anchors_used": anchors or [], "error": None}
    try:
        vids = list(scrapetube.get_search(keyword, limit=limit, proxies=_proxies_dict()))
    except Exception as e:
        report["error"] = str(e); report["saturation"] = -1.0; report["label"] = "ERROR"
        return report

    best = None
    count = 0
    for v in vids:
        try:
            title = v["title"]["runs"][0]["text"]
        except (KeyError, IndexError):
            continue
        if detect_language(title) != "es":
            continue
        if not title_contains_anchor(title, anchors):
            continue
        months = _parse_date_scrapetube_months_ago(_es_pub_text(v))
        views = _parse_views_scrapetube(v)
        decay = _es_age_decay(months)
        eff = views * decay
        count += 1
        if best is None or eff > best["eff"]:
            best = {"title": title[:80], "views": views, "months": months, "decay": decay, "eff": eff}

    report["ontopic_count"] = count
    if best:
        report["saturation"] = best["eff"]
        report["heaviest"] = best
        report["label"] = _es_saturation_label(best["eff"])
    return report


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
