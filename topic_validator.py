"""
modules/topic_validator.py — Market Architect v3

Validador de mercado con arquitectura de 3 capas (INTACTA):

  Capa 1 — DEMANDA: Google Trends (vía pytrends + proxy scrapegw)
           Score 0-100 + auto-pivote a términos con más tráfico.

  Capa 2 — COMPETENCIA (primaria): scrapetube
  Capa 3 — COMPETENCIA (fallback): YouTube Data API v3
           AMBAS capas ahora viven en modules/youtube_scanner.py.
           Este validator consume scan_competition() del scanner.

CAMBIOS DE ESTA VERSIÓN (refactor aprobado):
  ✓ Migrado a youtube_scanner (sin duplicar scrapetube/API fallback)
  ✓ Umbrales de rigurosidad por video_type (short vs long) vía parámetro
  ✓ Lógica [APUESTA_VIRAL] — Regla 3-50-24:
      - Solo se evalúa si topic["discovery_mode"] == "digital_archaeology"
        y evidence_from_discovery.is_apuesta_viral_candidate == True
      - Si pasa Trend score > 70 Y competencia ES ≤ 3 videos con >50k en
        24 meses → se añade tag "[APUESTA_VIRAL]" al título
  ✓ Constantes apuesta viral en config.apuesta_viral

REGLAS DE ORO RESPETADAS:
  * Parche urllib3 (se aplica via import de youtube_scanner → idempotente)
  * Proxy scrapegw intacto
  * Arquitectura 3 capas intacta
  * Interfaz pública validate_topics() sin cambios (csv_exporter sigue OK)
"""

import json
import random
import re
import string
import time
from datetime import datetime, timedelta
from pathlib import Path

# ─── IMPORT ORDEN CRÍTICO ───
# youtube_scanner aplica el parche urllib3 al cargarse.
# Debe importarse ANTES que pytrends para que pytrends use el Retry parcheado.
from script_engine.youtube_scanner import (
    count_competing_spanish,
    scan_competition,
)

# Ahora sí, pytrends (depende del parche aplicado por el scanner)
from pytrends.request import TrendReq

from config import (
    api,
    apuesta_viral,
    gemini_client,
    validator_strictness,
    DATA_DIR,
)
from error_handler import error_handler, PipelineStage
from script_engine.topics_db import load_db, save_db
from google.genai import types as genai_types

# ═══════════════════════════════════════════════════════════════
#  CONFIG
# ═══════════════════════════════════════════════════════════════

TRENDS_CACHE_FILE: Path = DATA_DIR / "trends_cache.json"
CACHE_TTL_HOURS: int = 24

# Umbrales FIJOS (no dependen de video_type)
TREND_PIVOT_TRIGGER: int = 10    # Score bajo → disparar auto-pivote
YT_LIMIT_SCRAPE: int = 25        # Videos a escanear por búsqueda (pasado al scanner)
DELAY_BETWEEN_TOPICS_SEC: int = 5

# Los umbrales de "oro" y "score mínimo" ahora vienen de
# validator_strictness.get_for(video_type) — recibido por parámetro.


# ═══════════════════════════════════════════════════════════════
#  CACHÉ DE TRENDS (intacto)
# ═══════════════════════════════════════════════════════════════

def _load_cache() -> dict:
    if TRENDS_CACHE_FILE.exists():
        try:
            return json.loads(TRENDS_CACHE_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _save_cache(cache: dict) -> None:
    TRENDS_CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    TRENDS_CACHE_FILE.write_text(
        json.dumps(cache, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def _cache_get(key: str) -> dict | None:
    cache = _load_cache()
    entry = cache.get(key)
    if not entry:
        return None
    cached_at = datetime.fromisoformat(entry["cached_at"])
    if datetime.now() - cached_at > timedelta(hours=CACHE_TTL_HOURS):
        return None
    return entry["data"]


def _cache_set(key: str, data: dict) -> None:
    cache = _load_cache()
    cache[key] = {
        "cached_at": datetime.now().isoformat(),
        "data": data,
    }
    _save_cache(cache)


# ═══════════════════════════════════════════════════════════════
#  PROXY + PYTRENDS (intacto — solo para Capa 1)
# ═══════════════════════════════════════════════════════════════
# Nota: _build_proxy_url está duplicado intencionalmente desde el
# youtube_scanner para mantener el validator autónomo en su Capa 1.
# Son 10 líneas y evita acoplamiento cruzado.

def _build_proxy_url(session_id: str | None = None) -> str:
    """Construye URL del proxy scrapegw con sesión opcional."""
    user = api.proxy_user
    if session_id:
        user = f"{user}-session-{session_id}"
    return f"http://{user}:{api.proxy_pass}@{api.proxy_host}"


def _new_pytrends_client() -> TrendReq:
    """Crea cliente pytrends con sesión aleatoria (anti-ban)."""
    session_id = "".join(random.choices(string.ascii_lowercase + string.digits, k=12))
    proxy_url = _build_proxy_url(session_id)
    return TrendReq(hl="es-ES", tz=360, proxies=[proxy_url], retries=3, timeout=(10, 25))


# ═══════════════════════════════════════════════════════════════
#  CAPA 1 — TRENDS (Momentum + Breakout detection)
# ═══════════════════════════════════════════════════════════════

# Umbrales de la nueva lógica
MOMENTUM_RATIO: float = 3.0       # últimos 7d >= 3× promedio 23d anteriores → ORO
MOMENTUM_MIN_RECENT: float = 5.0  # evita dividir entre ruido (si últimos 7d < 5, ignorar)


@error_handler.retry(PipelineStage.TOPIC_VALIDATOR)
def _query_trend_score(pytrends: TrendReq, keyword: str) -> dict:
    """
    Consulta trend con análisis de Momentum + Breakout.

    Retorna:
      {
        "score": float,            # Promedio global (métrica legacy)
        "recent_avg": float,       # Promedio últimos 7 días
        "prior_avg": float,        # Promedio 23 días anteriores
        "momentum_ratio": float,   # recent_avg / prior_avg
        "has_momentum": bool,      # True si recent >= 3× prior (ORO)
        "has_breakout": bool,      # True si related_queries tiene "breakout"
        "error": str | None
      }

    Usa 1 SOLA llamada a pytrends (timeframe='today 1-m') y segmenta
    el DataFrame localmente. Esto minimiza riesgo de ban del proxy.

    IMPORTANTE: Todos los valores numéricos/booleanos se castean
    explícitamente a tipos Python nativos (float/bool) para evitar
    `TypeError: Object of type bool is not JSON serializable` cuando
    pandas/numpy filtran tipos como numpy.bool_ o numpy.float64.
    """
    result: dict = {
        "score": 0.0,
        "recent_avg": 0.0,
        "prior_avg": 0.0,
        "momentum_ratio": 0.0,
        "has_momentum": False,
        "has_breakout": False,
        "error": None,
    }

    try:
        # 1 sola llamada: último mes completo
        pytrends.build_payload([keyword], timeframe="today 1-m", geo="")
        df = pytrends.interest_over_time()

        if df.empty or keyword not in df:
            # Fallback ventana larga para temas de bajo volumen (arqueología)
            pytrends.build_payload([keyword], timeframe="today 3-m", geo="")
            df = pytrends.interest_over_time()
            if df.empty or keyword not in df:
                return result  # sin datos

        series = df[keyword]

        # Promedio global (cast a float Python nativo)
        result["score"] = round(float(series.mean()), 2)

        # ─── Momentum: últimos 7 puntos vs 23 anteriores ───
        if len(series) >= 14:
            recent = series.tail(7)
            prior = series.iloc[:-7]
            result["recent_avg"] = round(float(recent.mean()), 2)
            result["prior_avg"] = round(float(prior.mean()), 2)

            # Calcular ratio solo si hay volumen mínimo en recent
            if result["recent_avg"] >= MOMENTUM_MIN_RECENT:
                prior_safe = max(result["prior_avg"], 1.0)  # evitar div/0
                result["momentum_ratio"] = round(
                    float(result["recent_avg"] / prior_safe), 2
                )
                # bool() explícito: comparación pandas puede devolver numpy.bool_
                result["has_momentum"] = bool(
                    result["momentum_ratio"] >= MOMENTUM_RATIO
                )

        # ─── Breakout: related_queries con etiqueta 'breakout' ───
        try:
            related = pytrends.related_queries()
            kw_related = related.get(keyword, {}) if related else {}
            rising = kw_related.get("rising")
            if rising is not None and not rising.empty:
                # pytrends marca breakouts con 'value' == 'Breakout' (string)
                values = rising["value"].astype(str).str.lower()
                # bool() explícito: .any() devuelve numpy.bool_ que NO es JSON-serializable
                result["has_breakout"] = bool(
                    values.str.contains("breakout").any()
                )
        except Exception as e:
            # No crítico: sin related_queries seguimos con momentum
            error_handler.log_warning(
                PipelineStage.TOPIC_VALIDATOR,
                f"related_queries falló para '{keyword}': {str(e)[:80]}",
            )

        return result

    except Exception as e:
        result["error"] = str(e)[:100]
        result["score"] = -1
        return result

def _get_trend_with_pivot(keyword: str) -> dict:
    """
    Obtiene datos de Trends con auto-pivote y análisis Momentum/Breakout.

    Si el keyword original tiene score bajo, prueba sugerencias de Google
    y devuelve el término con mayor score absoluto. Propaga has_momentum
    y has_breakout del mejor candidato al resultado final.
    """
    cached = _cache_get(f"trend:{keyword}")
    if cached:
        error_handler.log_info(
            PipelineStage.TOPIC_VALIDATOR,
            f"Trend cacheado: '{keyword}' score={cached.get('final_score')}",
        )
        return cached

    pytrends = _new_pytrends_client()

    initial = _query_trend_score(pytrends, keyword)
    initial_score = initial["score"]

    result = {
        "original_topic": keyword,
        "original_score": initial_score,
        "final_topic": keyword,
        "final_score": initial_score,
        "origin": "ORIGINAL",
        "error": initial["error"],
        "suggestions_tried": [],
        # ─── Nuevos campos Momentum + Breakout ───
        "recent_avg": initial.get("recent_avg", 0.0),
        "prior_avg": initial.get("prior_avg", 0.0),
        "momentum_ratio": initial.get("momentum_ratio", 0.0),
        "has_momentum": initial.get("has_momentum", False),
        "has_breakout": initial.get("has_breakout", False),
    }

    # Auto-pivote si score bajo y no hubo error
    if 0 <= initial_score < TREND_PIVOT_TRIGGER:
        error_handler.log_info(
            PipelineStage.TOPIC_VALIDATOR,
            f"Score bajo ({initial_score}) para '{keyword}'. Buscando pivotes...",
        )
        try:
            suggs = pytrends.suggestions(keyword) or []
            candidates = [s["title"] for s in suggs[:3]]
            result["suggestions_tried"] = candidates

            for cand in candidates:
                cand_result = _query_trend_score(pytrends, cand)
                if cand_result["score"] > result["final_score"]:
                    result["final_score"] = cand_result["score"]
                    result["final_topic"] = cand
                    result["origin"] = "PIVOTED"
                    # Propagar Momentum/Breakout del mejor pivote
                    result["recent_avg"] = cand_result.get("recent_avg", 0.0)
                    result["prior_avg"] = cand_result.get("prior_avg", 0.0)
                    result["momentum_ratio"] = cand_result.get("momentum_ratio", 0.0)
                    result["has_momentum"] = cand_result.get("has_momentum", False)
                    result["has_breakout"] = cand_result.get("has_breakout", False)
                time.sleep(2)
        except Exception as e:
            error_handler.log_warning(
                PipelineStage.TOPIC_VALIDATOR,
                f"Pivote falló para '{keyword}': {e}",
            )

    _cache_set(f"trend:{keyword}", result)
    return result


# ═══════════════════════════════════════════════════════════════
#  VEREDICTO (ajustado por video_type)
# ═══════════════════════════════════════════════════════════════

def _compute_verdict(
    trend: dict,
    yt: dict,
    topic: dict | None = None,
    video_type: str = "short",
) -> dict:
    """
    Combina datos de Trends + YouTube en veredicto final.
    Los umbrales vienen de validator_strictness.get_for(video_type).

    Reglas (orden de prioridad):
      1. BYPASS ARQUEOLOGÍA — si topic es digital_archaeology + candidato
         APUESTA_VIRAL + competencia ES fresca = 0 → ORO automático.
      2. MOMENTUM — si has_momentum (últimos 7d ≥ 3× los 23d previos) y
         ES fresh ≤ umbral → ORO aunque el score absoluto sea bajo.
      3. Lógica clásica por score absoluto.
      4. BREAKOUT — si el veredicto sería "frio" o "caliente" pero hay
         breakout en related_queries → ARBITRAJE (🟡 oportunidad).

    Veredictos:
      🚀 oro       — Alta demanda + poca/ninguna competencia fresca en ES
      🟢 arbitraje — Alta demanda (o breakout) + más competencia EN que ES
      🟡 caliente  — Alta demanda + mucha competencia en ES
      💀 frio      — Sin demanda real
      ⚪ desconocido — Error/datos incompletos
    """
    strictness = validator_strictness.get_for(video_type)
    yt_max_fresh_for_gold = strictness["yt_max_fresh_for_gold"]
    trend_min_score = strictness["trend_min_score"]

    score = trend.get("final_score", -1)
    es_fresh = yt["es"].get("fresh", 0)
    en_fresh = yt["en"].get("fresh", 0)
    has_momentum = trend.get("has_momentum", False)
    has_breakout = trend.get("has_breakout", False)
    momentum_ratio = trend.get("momentum_ratio", 0.0)

    # ─── REGLA 1 — BYPASS DE ARQUEOLOGÍA ───
    # digital_archaeology + candidato APUESTA_VIRAL + 0 competencia ES = ORO
    if topic is not None and es_fresh == 0:
        evidence = topic.get("evidence_from_discovery") or {}
        if (topic.get("discovery_mode") == "digital_archaeology"
                and evidence.get("is_apuesta_viral_candidate")):
            return {
                "verdict": "oro",
                "emoji": "🚀",
                "reason": (
                    "Bypass arqueología: candidato APUESTA_VIRAL con "
                    "0 competencia ES fresca"
                ),
                "bypass": "digital_archaeology",
                "applied_strictness": strictness,
            }

    # ─── REGLA 2 — MOMENTUM ORO ───
    # Picos recientes (7d ≥ 3× 23d previos) con ES libre = ORO por momentum
    if has_momentum and es_fresh <= yt_max_fresh_for_gold:
        return {
            "verdict": "oro",
            "emoji": "🚀",
            "reason": (
                f"Momentum detectado (ratio {momentum_ratio}×) con "
                f"competencia ES ≤ {yt_max_fresh_for_gold}"
            ),
            "bypass": "momentum",
            "applied_strictness": strictness,
        }

    # ─── Error / sin datos ───
    if score < 0:
        return {
            "verdict": "desconocido",
            "emoji": "⚪",
            "reason": "Trend score no disponible",
            "applied_strictness": strictness,
        }

    # ─── Lógica clásica por score absoluto ───
    if score < trend_min_score:
        # REGLA 4 (parcial) — breakout rescata frío a arbitraje
        if has_breakout:
            return {
                "verdict": "arbitraje",
                "emoji": "🟡",
                "reason": (
                    f"Breakout detectado en related_queries (score {score} bajo). "
                    "Oportunidad emergente antes que Trends la refleje."
                ),
                "bypass": "breakout",
                "applied_strictness": strictness,
            }
        return {
            "verdict": "frio",
            "emoji": "💀",
            "reason": f"Trend score bajo ({score}/100, mín {trend_min_score})",
            "applied_strictness": strictness,
        }

    # Hay demanda suficiente — evaluar competencia
    if es_fresh <= yt_max_fresh_for_gold:
        return {
            "verdict": "oro",
            "emoji": "🚀",
            "reason": (
                f"Demanda ({score}) con competencia ES fresca ≤ "
                f"{yt_max_fresh_for_gold}"
            ),
            "applied_strictness": strictness,
        }

    if es_fresh < en_fresh:
        return {
            "verdict": "arbitraje",
            "emoji": "🟢",
            "reason": f"Demanda ({score}). ES fresco: {es_fresh} vs EN fresco: {en_fresh}",
            "applied_strictness": strictness,
        }

    # Saturado en ES — pero si hay breakout, rescata a arbitraje 🟡
    if has_breakout:
        return {
            "verdict": "arbitraje",
            "emoji": "🟡",
            "reason": (
                f"ES saturado ({es_fresh}) pero breakout activo: "
                "oportunidad de angulo diferente"
            ),
            "bypass": "breakout",
            "applied_strictness": strictness,
        }

    return {
        "verdict": "caliente",
        "emoji": "🟡",
        "reason": f"Demanda ({score}) pero ES saturado ({es_fresh} videos frescos)",
        "applied_strictness": strictness,
    }


# ═══════════════════════════════════════════════════════════════
#  SUGERENCIA DE FORMATO (🎬 LARGO / ⚡ SHORT)
# ═══════════════════════════════════════════════════════════════

def _compute_suggested_format(topic: dict, verdict_str: str) -> str:
    """
    Decide el formato sugerido según discovery_mode y veredicto.

    Reglas:
      - digital_archaeology + oro → 🎬 SUGERIDO LARGO (tema con profundidad
        histórica y poca competencia, justifica 8-10 min).
      - Cualquier otro caso       → ⚡ SUGERIDO SHORT (aprovechar el pico
        de demanda rápido antes que llegue la competencia).
    """
    discovery_mode = topic.get("discovery_mode", "")
    if discovery_mode == "digital_archaeology" and verdict_str == "oro":
        return "🎬 SUGERIDO LARGO"
    return "⚡ SUGERIDO SHORT"


# ═══════════════════════════════════════════════════════════════
#  HUMAN OPTIONS 3x3 (hooks + outros con Gemini)
# ═══════════════════════════════════════════════════════════════

_HUMAN_OPTIONS_PROMPT = """Eres un guionista viral especializado en contenido en español neutro
para Shorts y Reels (mystery/historia/datos). Tu trabajo: escribir hooks y outros
que peguen DURO porque están construidos con DATA REAL del topic, no con frases hechas.

═══════════════════════════════════════════════════
TOPIC INPUTS
═══════════════════════════════════════════════════
TÍTULO: {title}
BÚSQUEDA: {search_keyword}
ÁNGULO: {angle}
MISTERIO: {mystery}
REVELACIÓN: {reveal}

DATOS DUROS VERIFICADOS (úsalos como munición — fechas, cifras, nombres):
{verified_facts_block}

═══════════════════════════════════════════════════
TU TAREA
═══════════════════════════════════════════════════
Generá 3 GANCHOS (primera frase del video, máx 15 palabras) y 3 CIERRES
(última frase, máx 15 palabras). CADA UNO debe contener al menos UN dato
real (cifra, fecha, nombre, lugar) extraído de los inputs de arriba.

🚫 PROHIBIDO TOTAL — frases genéricas vacías:
  ✗ "Nadie ha explicado..."
  ✗ "Todo lo que te contaron es mentira"
  ✗ "Los registros oficiales revelan algo inquietante"
  ✗ "Lo que pasó realmente con [keyword]"
  ✗ Cualquier hook que funcione igual para CUALQUIER topic.

✅ OBLIGATORIO — cada hook debe ser único de ESTE topic:
  ✓ Cifras concretas (2,000 muertos, 161,000 toneladas, 46,840 hectáreas)
  ✓ Fechas exactas (1948, 1966, 2022)
  ✓ Nombres propios (Dr. Eric Saint, CSR, Banjima, río Fortescue)
  ✓ Contrastes temporales (X años después, Y décadas ignoradas)

═══════════════════════════════════════════════════
ESTILOS DE GANCHO (uno por cada, en orden)
═══════════════════════════════════════════════════

1. INTRIGA-CIFRA: planteá el misterio anclado en una cifra concreta.
   Ej genérico (NO copiar literal): "2,000 muertos. 50 años de silencio. Una sola pregunta sin respuesta."
   Ej genérico (NO copiar literal): "46,840 hectáreas envenenadas. Nadie quiere pagar por limpiarlas."

2. PARADOJA-FECHA: contrastá una advertencia/verdad temprana con la inacción posterior.
   Ej genérico (NO copiar literal): "Le advirtieron en 1948. Lo ignoraron 18 años. Eso bastó para matar a 2,000 personas."
   Ej genérico (NO copiar literal): "En 1962 supieron la verdad. Recién en 2022 lo admitieron oficialmente."

3. AUTORIDAD-NOMBRE: usá un nombre propio (persona, empresa, lugar) + dato técnico/histórico.
   Ej genérico (NO copiar literal): "El Dr. Eric Saint usó la palabra 'cosecha letal' en su informe. Lo guardaron en un cajón."
   Ej genérico (NO copiar literal): "CSR extrajo 161,000 toneladas. Nunca pagó por la limpieza."

═══════════════════════════════════════════════════
ESTILOS DE CIERRE (uno por cada, en orden)
═══════════════════════════════════════════════════

1. CLIFFHANGER-DATO: deja un dato pendiente que invite a quedarse hasta el final del video.
   Ej genérico (NO copiar literal): "Pero lo que encontraron en el río Fortescue en 2021 cambia todo."

2. COMPROMISO-MILESTONE: pide acción con promesa concreta atada al topic.
   Ej genérico (NO copiar literal): "Si llegamos a 20K likes, hago la parte 2 con los testimonios de las familias."

3. DEBATE-TENSIÓN: dispara comentarios con una pregunta que enfrente posturas reales.
   Ej genérico (NO copiar literal): "¿La culpa es de CSR, del gobierno australiano o de los dos?"

═══════════════════════════════════════════════════
REGLAS DE SEGURIDAD (importante)
═══════════════════════════════════════════════════
- Hablando de muertes/víctimas: usar "perdieron la vida", "fallecieron", "muertes",
  NO "víctimas de", "deadly", "tóxico letal" (esas frases tienen otros usos pero
  evitalas en hooks por consistencia con el resto del pipeline).
- No menores como protagonistas del hook si el topic involucra sustancias dañinas.
- Español NEUTRO (no "vos sos" todo el tiempo, alterná "tú/usted/uno").

═══════════════════════════════════════════════════
SALIDA
═══════════════════════════════════════════════════
Responde ÚNICAMENTE con JSON válido, sin markdown, sin backticks, formato EXACTO:
{{"hooks":["hook1","hook2","hook3"],"outros":["outro1","outro2","outro3"]}}"""



def _detect_safety_block(response) -> str | None:
    """
    Inspecciona la respuesta de Gemini para detectar bloqueo por seguridad.
    Returns: string descriptivo del bloqueo o None si no hay bloqueo detectable.
    """
    try:
        # prompt_feedback.block_reason: bloqueo a nivel prompt
        pf = getattr(response, "prompt_feedback", None)
        if pf is not None:
            br = getattr(pf, "block_reason", None)
            if br:
                return f"prompt_bloqueado:{br}"

        # candidates[0].finish_reason: bloqueo a nivel respuesta (SAFETY, RECITATION, etc.)
        cands = getattr(response, "candidates", None) or []
        if cands:
            fr = getattr(cands[0], "finish_reason", None)
            # finish_reason STOP = OK; cualquier otro valor distinto suele ser bloqueo
            if fr is not None:
                fr_str = str(fr).upper()
                if "SAFETY" in fr_str or "RECITATION" in fr_str or "BLOCK" in fr_str:
                    return f"respuesta_bloqueada:{fr_str}"
    except Exception:
        pass
    return None


def _generic_fallback_hooks_outros(topic: dict) -> dict:
    """
    Plan B: genera 3 hooks + 3 outros cuando Gemini falla.

    A diferencia de la versión anterior (que solo usaba search_keyword),
    esta versión EXPLOTA verified_facts para construir hooks data-driven.
    Si verified_facts está vacío (topics viejos pre-fix), cae a plantillas
    de keyword como último recurso.

    Mantiene los 3 estilos: INTRIGA-CIFRA, PARADOJA-FECHA, AUTORIDAD-NOMBRE
    (hooks) y CLIFFHANGER-DATO, COMPROMISO-MILESTONE, DEBATE-TENSIÓN (outros).

    Returns:
        {"hooks": [str, str, str], "outros": [str, str, str]}
    """
    import re as _re

    title: str = (topic.get("video_title") or "este caso").strip()
    keyword: str = (topic.get("search_keyword") or title).strip()
    short: str = keyword[:60] if len(keyword) > 60 else keyword
    mystery: str = (topic.get("mystery") or "").strip()
    reveal: str = (topic.get("reveal") or "").strip()

    facts: list[str] = topic.get("verified_facts") or []

    # ─── Heurísticas para extraer cifras/fechas/nombres de verified_facts ───
    def _find_fact_with(pattern: str) -> str | None:
        """Devuelve el primer fact que matchea el patrón regex (o None)."""
        for f in facts:
            if _re.search(pattern, f, flags=_re.IGNORECASE):
                return f
        return None

    # Patrones útiles
    fact_with_year = _find_fact_with(r"\b(18|19|20)\d{2}\b")
    fact_with_number = _find_fact_with(r"\b\d{1,3}(?:[.,]\d{3})+\b|\b\d{2,}\b")
    fact_with_name = _find_fact_with(r"\b(Dr\.|Sr\.|Prof\.|Ing\.|[A-Z][a-záéíóú]+ [A-Z][a-záéíóú]+)\b")

    # ─── Construcción de hooks ───
    hooks: list[str] = []

    # Hook 1 — INTRIGA-CIFRA: misterio anclado en una cifra
    if fact_with_number and mystery:
        # Tomar cifra + unidad si aparece en el mismo fact (hectáreas, muertos, toneladas, etc.)
        match = _re.search(
            r"(\b\d{1,3}(?:[.,]\d{3})+\b|\b\d{2,}\b)\s*([a-záéíóú]+)?",
            fact_with_number,
        )
        if match:
            cifra = match.group(1)
            unidad = (match.group(2) or "").lower().strip()
            unidades_validas = {"muertos", "muertes", "personas", "trabajadores",
                                "hectáreas", "hectareas", "toneladas", "kilómetros",
                                "kilometros", "casos", "víctimas", "victimas", "años", "anos"}
            if unidad in unidades_validas:
                hooks.append(f"{cifra} {unidad}. Y nadie quiere responder por qué.")
            else:
                hooks.append(f"{cifra}. Y nadie quiere responder por qué.")
        else:
            hooks.append("Miles afectados. Y nadie quiere responder por qué.")
    elif mystery:
        hooks.append(mystery if mystery.endswith(("?", ".")) else f"{mystery}.")
    else:
        hooks.append(f"Nadie ha explicado qué pasó con {short}.")

    # Hook 2 — PARADOJA-FECHA: contraste temporal
    if fact_with_year:
        match = _re.search(r"\b(18|19|20)\d{2}\b", fact_with_year)
        year = match.group() if match else "hace décadas"
        hooks.append(f"En {year} ya lo sabían. Igual lo dejaron pasar.")
    else:
        hooks.append(f"Lo supieron desde el principio. Y lo dejaron pasar.")

    # Hook 3 — AUTORIDAD-NOMBRE: usa nombre propio + dato
    
    # Hook 3 — AUTORIDAD-NOMBRE: usa nombre propio + dato.
    # Busca en TODOS los facts (no solo el primero) y prioriza títulos (Dr./Sr./Prof.).
    nombre_extraido: str | None = None
    name_patterns = [
        # Dr./Sr./Prof. + Nombre Apellido (corta antes de coma/punto)
        r"\b(Dr\.\s+[A-ZÁÉÍÓÚ][a-záéíóú]+(?:\s+[A-ZÁÉÍÓÚ][a-záéíóú]+)?)\b",
        r"\b(Sr\.\s+[A-ZÁÉÍÓÚ][a-záéíóú]+(?:\s+[A-ZÁÉÍÓÚ][a-záéíóú]+)?)\b",
        r"\b(Prof\.\s+[A-ZÁÉÍÓÚ][a-záéíóú]+(?:\s+[A-ZÁÉÍÓÚ][a-záéíóú]+)?)\b",
        # Nombre Apellido sin título (dos palabras capitalizadas)
        r"\b([A-ZÁÉÍÓÚ][a-záéíóú]+\s+[A-ZÁÉÍÓÚ][a-záéíóú]+)\b",
    ]
    # Buscar en facts + research_summary (más material disponible)
    search_blob = " ".join(facts) + " " + (topic.get("research_summary") or "")
    for pat in name_patterns:
        m = _re.search(pat, search_blob)
        if m:
            cand = m.group(1).strip().rstrip(",.;:")
            # Filtrar nombres de lugares comunes que matchean el patrón
            blacklist = {"Western Australia", "Southern Hemisphere", "Pilbara Region",
                         "Colonial Sugar", "Australian Blue", "Blue Murder"}
            if cand not in blacklist:
                nombre_extraido = cand
                break

    if nombre_extraido:
        hooks.append(f"{nombre_extraido} lo advirtió. Lo ignoraron durante años.")
    elif reveal:
        reveal_short = reveal[:80] + ("…" if len(reveal) > 80 else "")
        hooks.append(reveal_short)
    else:
        hooks.append(f"Los registros oficiales sobre {short} cuentan otra historia.")


    # ─── Construcción de outros (data-driven cuando hay material) ───
    outros: list[str] = []

    # Outro 1 — CLIFFHANGER-DATO
    if reveal:
        outros.append("Pero lo que descubrieron después cambia toda la historia.")
    else:
        outros.append("Lo que encontraron al final lo cambió todo.")

    # Outro 2 — COMPROMISO-MILESTONE
    outros.append("Si este video llega a 20K likes, hago la parte 2 con los detalles que faltan.")

    # Outro 3 — DEBATE-TENSIÓN
    if reveal and ("empresa" in reveal.lower() or "gobierno" in reveal.lower() or "negligencia" in reveal.lower()):
        outros.append("¿La culpa fue del gobierno, de la empresa o de los dos? Comentá.")
    else:
        outros.append("¿Vos qué creés: coincidencia, encubrimiento o algo más? Comentá.")

    return {"hooks": hooks, "outros": outros}

    
def _generate_human_options(topic: dict) -> dict:
    """
    Genera 3 hooks + 3 outros con Gemini para humanizar el contenido.

    Solo se llama para topics oro/arbitraje/caliente (los que van a producción).
    Resistente a fallos: si Gemini falla (error, bloqueo de seguridad,
    JSON malformado), cae a plantillas data-driven. NUNCA devuelve celdas
    vacías para topics viables — son temas de producción.

    Inputs enriquecidos vs versión anterior:
    - title, angle, search_keyword (ya estaban)
    - mystery, reveal (nuevos — anclan el misterio y la teoría)
    - verified_facts (nuevo — munición de cifras/fechas/nombres reales)

    Returns:
        {
          "hooks":  [str, str, str],
          "outros": [str, str, str],
          "source": "gemini" | "fallback_generic",
          "fallback_reason": str | None,
        }
    """
    title_safe: str = topic.get("video_title", "?")

    try:
        # ─── Construir bloque de verified_facts para el prompt ───
        facts: list[str] = topic.get("verified_facts") or []
        if facts:
            facts_block = "\n".join(f"  • {f}" for f in facts[:12])
        else:
            facts_block = "  (sin verified_facts disponibles — usar angle/mystery/reveal como base)"

        prompt = _HUMAN_OPTIONS_PROMPT.format(
            title=topic.get("video_title", ""),
            angle=topic.get("angle", ""),
            search_keyword=topic.get("search_keyword", topic.get("video_title", "")),
            mystery=topic.get("mystery", "(sin misterio definido)"),
            reveal=topic.get("reveal", "(sin reveal definido)"),
            verified_facts_block=facts_block,
        )

        response = gemini_client.models.generate_content(
            model=api.gemini_model,  # Flash: barato para esto
            contents=prompt,
            config=genai_types.GenerateContentConfig(
                temperature=0.85,
                max_output_tokens=2500,  # 6 strings + JSON wrapping con margen
                response_mime_type="application/json",
            ),
        )

        # ─── Chequeo explícito de bloqueo de seguridad ───
        block_reason = _detect_safety_block(response)
        if block_reason:
            error_handler.log_warning(
                PipelineStage.TOPIC_VALIDATOR,
                f"human_options BLOQUEADO por Gemini para '{title_safe}': "
                f"{block_reason}. Aplicando fallback data-driven.",
            )
            fb = _generic_fallback_hooks_outros(topic)
            fb["source"] = "fallback_generic"
            fb["fallback_reason"] = block_reason
            return fb

        # Extraer texto
        text: str = ""
        if hasattr(response, "text") and response.text:
            text = response.text
        elif hasattr(response, "candidates") and response.candidates:
            parts = response.candidates[0].content.parts
            text = "".join(getattr(p, "text", "") for p in parts)

        if not text.strip():
            raise ValueError("Gemini devolvió texto vacío")

        # Limpiar y parsear (con response_mime_type=json no debería tener
        # backticks, pero dejamos el strip por defensa)
        text = text.strip()
        if "```" in text:
            text = re.sub(r"```(?:json)?\s*|\s*```", "", text, flags=re.DOTALL).strip()

        data = json.loads(text)

        hooks = data.get("hooks", [])
        outros = data.get("outros", [])

        if not isinstance(hooks, list) or len(hooks) != 3:
            raise ValueError(f"hooks malformado: {hooks!r}")
        if not isinstance(outros, list) or len(outros) != 3:
            raise ValueError(f"outros malformado: {outros!r}")

        return {
            "hooks": [str(h).strip() for h in hooks],
            "outros": [str(o).strip() for o in outros],
            "source": "gemini",
            "fallback_reason": None,
        }

    except Exception as e:
        reason = f"{type(e).__name__}: {str(e)[:120]}"
        error_handler.log_warning(
            PipelineStage.TOPIC_VALIDATOR,
            f"human_options falló para '{title_safe}': {reason}. "
            f"Aplicando fallback data-driven (no se acepta celda vacía para temas viables).",
        )
        fb = _generic_fallback_hooks_outros(topic)
        fb["source"] = "fallback_generic"
        fb["fallback_reason"] = reason
        return fb


def _verdict_to_legacy_level(verdict: str) -> str:
    """
    Mapea veredicto al competition_level viejo (green/yellow/red)
    para no romper csv_exporter y topics_db.
    """
    return {
        "oro": "green",
        "arbitraje": "green",
        "caliente": "yellow",
        "frio": "red",
        "desconocido": "yellow",
    }.get(verdict, "yellow")


# ═══════════════════════════════════════════════════════════════
#  LÓGICA [APUESTA_VIRAL] — Regla 3-50-24
# ═══════════════════════════════════════════════════════════════

def _get_search_query(topic: dict) -> str:
    """
    Devuelve la query a enviar a Google Trends / YouTube.

    Prioridad:
      1. topic["search_keyword"] — entidad pura extraída por el researcher
      2. topic["video_title"] limpio del prefijo [APUESTA_VIRAL] si lo tiene
         (fallback para topics antiguos en DB sin search_keyword)

    El title narrativo NUNCA debe llegar a Trends porque nadie busca
    ganchos de YouTube en Google.
    """
    keyword = (topic.get("search_keyword") or "").strip()
    if keyword:
        return keyword

    # Fallback: title sin prefijo de tag
    title = topic.get("video_title", "").strip()
    return title.replace("[APUESTA_VIRAL]", "").strip()


def _is_apuesta_viral_candidate(topic: dict) -> bool:
    """
    Determina si un topic es ELEGIBLE para evaluación [APUESTA_VIRAL].
    Solo los topics del modo 'digital_archaeology' marcados por el
    discoverer con is_apuesta_viral_candidate=True pueden calificar.
    """
    if topic.get("discovery_mode") != "digital_archaeology":
        return False
    evidence = topic.get("evidence_from_discovery") or {}
    return bool(evidence.get("is_apuesta_viral_candidate", False))


def _check_apuesta_viral(topic: dict, trend: dict) -> dict:
    """
    Evalúa si el topic califica como [APUESTA_VIRAL] bajo la Regla 3-50-24.

    Criterios (TODOS deben cumplirse):
      1. discovery_mode == "digital_archaeology" + marcado como candidato
      2. Trend final_score > apuesta_viral.min_trend_score (default 70)
      3. competing_count ≤ apuesta_viral.max_competing_videos (default 3)
         en ventana apuesta_viral.window_months (default 24)
         con umbral apuesta_viral.min_views_to_count (default 50_000)

    Returns:
        dict con keys: qualifies, reason, rule, y datos del chequeo.
    """
    result: dict = {
        "qualifies": False,
        "rule": (
            f"{apuesta_viral.max_competing_videos}-"
            f"{apuesta_viral.min_views_to_count // 1000}K-"
            f"{apuesta_viral.window_months}"
        ),
        "min_trend_score": apuesta_viral.min_trend_score,
        "reason": "",
    }

    # Criterio 1 — Elegibilidad
    if not _is_apuesta_viral_candidate(topic):
        result["reason"] = "no elegible (no es digital_archaeology marcado)"
        return result

    # Criterio 2 — Trend score
    score = trend.get("final_score", -1)
    if score < 0:
        result["reason"] = f"Trend score no disponible ({score})"
        return result
    if score <= apuesta_viral.min_trend_score:
        result["reason"] = (
            f"Trend score {score} ≤ {apuesta_viral.min_trend_score}"
        )
        result["trend_score"] = score
        return result

    # Criterio 3 — Regla 3-50-24 vía count_competing_spanish
    search_query = _get_search_query(topic)
    error_handler.log_info(
        PipelineStage.TOPIC_VALIDATOR,
        f"[APUESTA_VIRAL] Evaluando Regla 3-50-24 para '{search_query}'...",
    )

    comp = count_competing_spanish(
        search_query,
        min_views=apuesta_viral.min_views_to_count,
        window_months=apuesta_viral.window_months,
    )

    competing_count = comp.get("competing_count", -1)

    if competing_count < 0:
        result["reason"] = (
            f"Error consultando competencia ES (regla 3-50-24): "
            f"{comp.get('error', 'desconocido')}"
        )
        result["trend_score"] = score
        return result

    result["trend_score"] = score
    result["competing_count"] = competing_count
    result["top_titles"] = comp.get("top_titles", [])
    result["source"] = comp.get("source", "unknown")

    if competing_count > apuesta_viral.max_competing_videos:
        result["reason"] = (
            f"{competing_count} videos ES cumplen el umbral "
            f"(límite {apuesta_viral.max_competing_videos})"
        )
        return result

    # ¡CALIFICA!
    result["qualifies"] = True
    result["reason"] = (
        f"Regla {result['rule']} cumplida: score={score}, "
        f"competing={competing_count}"
    )
    return result


def _apply_apuesta_viral_tag(topic: dict) -> None:
    """
    Añade el prefijo [APUESTA_VIRAL] al título del topic in-place,
    solo si aún no está presente.
    """
    tag = "[APUESTA_VIRAL]"
    current_title = topic.get("video_title", "")
    if tag not in current_title:
        topic["video_title"] = f"{tag} {current_title}".strip()


# ═══════════════════════════════════════════════════════════════
#  VALIDACIÓN INDIVIDUAL DE UN TOPIC
# ═══════════════════════════════════════════════════════════════

def _validate_topic(topic: dict, video_type: str = "short") -> dict:
    """
    Pipeline completo de validación de un topic.
    Ya no hace scraping directo — delega al youtube_scanner.

    Usa search_keyword (entidad pura) para Trends y YouTube.
    El title narrativo solo se usa para logs y el CSV.
    """
    title = topic["video_title"]
    query = _get_search_query(topic)

    error_handler.log_info(
        PipelineStage.TOPIC_VALIDATOR,
        f"Validando: {title}  |  query='{query}'  |  video_type={video_type}",
    )

    # Capa 1 — Trends con auto-pivote (apunta a search_keyword)
    trend = _get_trend_with_pivot(query)
    query_for_yt = trend["final_topic"]  # Usamos el pivote si aplica

    # Capas 2/3 — Delegadas al scanner (scrapetube → API fallback)
    yt = scan_competition(query_for_yt, limit=YT_LIMIT_SCRAPE)

    # Veredicto (con umbrales ajustados por video_type + bypass arqueología)
    verdict = _compute_verdict(trend, yt, topic, video_type=video_type)

    error_handler.log_success(
        PipelineStage.TOPIC_VALIDATOR,
        f"{verdict['emoji']} {title} → {verdict['verdict']} ({verdict['reason']})",
    )

    return {
        "trend": trend,
        "youtube": yt,
        "verdict": verdict,
    }


# ═══════════════════════════════════════════════════════════════
#  ORQUESTADOR PÚBLICO
# ═══════════════════════════════════════════════════════════════

def _get_pending_topics(db: dict) -> list[dict]:
    """Topics aún no validados."""
    return [t for t in db.get("topics", []) if t.get("competition_level") is None]


def validate_topics(video_type: str = "short") -> list[dict]:
    """
    Valida todos los topics pendientes en topics_db.

    Args:
        video_type: "short" o "long". Define umbrales de rigurosidad y
                    se guarda en cada topic como topic["video_type"] para
                    que script_generator y downstream lo hereden.

    Actualiza cada topic con:
      - competition_level    (legacy: green/yellow/red)
      - market_verdict       (oro/arbitraje/caliente/frio/desconocido)
      - competition_data     (trend + youtube + verdict completos)
      - is_apuesta_viral     (bool)
      - apuesta_viral_check  (detalles de la evaluación, si aplica)
      - status               ("validated")
      - title                (con prefijo [APUESTA_VIRAL] si califica)
      - video_type           (propagado para downstream)
      - suggested_format     ("🎬 SUGERIDO LARGO" | "⚡ SUGERIDO SHORT")
      - human_options        ({hooks: [3], outros: [3]}) solo oro/arbitraje/caliente

    Returns:
        Lista de topics validados.
    """
    if video_type not in ("short", "long"):
        raise ValueError(f"video_type debe ser 'short' o 'long', no '{video_type}'")

    db = load_db()
    pending = _get_pending_topics(db)

    if not pending:
        print("\n  ⚠ No hay topics pendientes de validar.")
        print("  ➡  Primero corré: python -m modules.topic_researcher\n")
        return []

    strictness_active = validator_strictness.get_for(video_type)

    print(f"\n{'═' * 60}")
    print(f"  🔍 TOPIC VALIDATOR v3 — Market Architect")
    print(f"  📺 video_type: {video_type.upper()}")
    print(f"  📊 Capas: Trends + scrapetube + fallback YouTube API")
    print(f"  🎯 Topics por validar: {len(pending)}")
    print(f"  ⚙️  Rigurosidad activa:")
    print(f"       - trend_min_score:       {strictness_active['trend_min_score']}")
    print(f"       - yt_max_fresh_for_gold: {strictness_active['yt_max_fresh_for_gold']}")
    print(f"{'═' * 60}")

    validated: list[dict] = []

    for i, topic in enumerate(pending, 1):
        print(f"\n  [{i}/{len(pending)}] {topic['video_title']}...")

        if i > 1:
            time.sleep(DELAY_BETWEEN_TOPICS_SEC)

        # ─── Validación normal (3 capas) ───
        try:
            result = _validate_topic(topic, video_type=video_type)
        except Exception as e:
            error_handler.log_error(
                PipelineStage.TOPIC_VALIDATOR, e,
                context={"topic": topic["video_title"]},
            )
            print(f"    ❌ Error: {e}")
            result = {
                "trend": {"final_score": -1, "error": str(e)[:100]},
                "youtube": {
                    "source": "FAILED",
                    "es": {"total": -1, "fresh": -1},
                    "en": {"total": -1, "fresh": -1},
                },
                "verdict": {
                    "verdict": "desconocido",
                    "emoji": "⚪",
                    "reason": str(e)[:100],
                },
            }

        verdict = result["verdict"]

        # ─── Chequeo [APUESTA_VIRAL] (solo aplica si es elegible) ───
        apuesta_check = _check_apuesta_viral(topic, result["trend"])
        topic["is_apuesta_viral"] = apuesta_check["qualifies"]
        topic["apuesta_viral_check"] = apuesta_check

        if apuesta_check["qualifies"]:
            _apply_apuesta_viral_tag(topic)
            print(f"    🏆 [APUESTA_VIRAL] — {apuesta_check['reason']}")

        # ─── Sugerencia de formato (🎬 LARGO / ⚡ SHORT) ───
        suggested_format = _compute_suggested_format(topic, verdict["verdict"])
        topic["suggested_format"] = suggested_format

        # ─── Enriquecimiento humanizado (solo para temas viables) ───
        # No malgastar tokens de Gemini en temas fríos/desconocidos.
        if verdict["verdict"] in ("oro", "arbitraje", "caliente"):
            print(f"    ✨ Generando human_options (hooks + outros)...")
            topic["human_options"] = _generate_human_options(topic)
        else:
            topic["human_options"] = {"hooks": [], "outros": []}

        # ─── Actualizar topic ───
        topic["competition_level"] = _verdict_to_legacy_level(verdict["verdict"])
        topic["market_verdict"] = verdict["verdict"]
        topic["competition_data"] = {
            "trend": result["trend"],
            "youtube": result["youtube"],
            "verdict": verdict,
            "validated_at": datetime.now().isoformat(),
            "video_type_at_validation": video_type,
        }
        topic["video_type"] = video_type     # ← propagado para downstream
        topic["status"] = "validated"
        validated.append(topic)

    save_db(db)
    _print_results(validated)
    return validated


# ═══════════════════════════════════════════════════════════════
#  REPORTE FINAL
# ═══════════════════════════════════════════════════════════════

def _print_results(topics: list[dict]) -> None:
    """Muestra resumen final ordenado por veredicto."""
    print(f"\n{'═' * 60}")
    print(f"  📊 RESULTADOS")
    print(f"{'═' * 60}")

    order = {"oro": 0, "arbitraje": 1, "caliente": 2, "frio": 3, "desconocido": 4}
    sorted_topics = sorted(
        topics,
        key=lambda t: order.get(t.get("market_verdict", "desconocido"), 5),
    )

    for t in sorted_topics:
        comp = t.get("competition_data", {})
        v = comp.get("verdict", {})
        trend = comp.get("trend", {})
        yt = comp.get("youtube", {})

        apuesta_tag = " 🏆[APUESTA_VIRAL]" if t.get("is_apuesta_viral") else ""
        mode_tag = f" ({t.get('discovery_mode', '?')})"

        print(f"\n  {v.get('emoji', '⚪')} {t.get('video_title', '?')}{apuesta_tag}{mode_tag}")
        print(f"     Trend: {trend.get('final_score', '?')}/100"
              f"  ({trend.get('origin', '?')}"
              f" → '{trend.get('final_topic', t.get('video_title', '?'))}')")
        print(f"     YT ES: {yt.get('es', {}).get('total', '?')} total"
              f" / {yt.get('es', {}).get('fresh', '?')} frescos")
        print(f"     YT EN: {yt.get('en', {}).get('total', '?')} total"
              f" / {yt.get('en', {}).get('fresh', '?')} frescos")
        print(f"     Fuente YT: {yt.get('source', '?')}")
        print(f"     Motivo:    {v.get('reason', '—')}")

        # Detalle [APUESTA_VIRAL] si aplica
        av = t.get("apuesta_viral_check", {})
        if av.get("qualifies"):
            print(f"     🏆 Regla {av.get('rule')}: score={av.get('trend_score')},"
                  f" competing={av.get('competing_count')}")

    # Totales
    counts = {"oro": 0, "arbitraje": 0, "caliente": 0, "frio": 0, "desconocido": 0}
    apuesta_count = 0
    for t in topics:
        v = t.get("market_verdict", "desconocido")
        counts[v] = counts.get(v, 0) + 1
        if t.get("is_apuesta_viral"):
            apuesta_count += 1

    print(f"\n{'─' * 60}")
    print(f"  🚀 {counts['oro']}  "
          f"🟢 {counts['arbitraje']}  "
          f"🟡 {counts['caliente']}  "
          f"💀 {counts['frio']}  "
          f"⚪ {counts['desconocido']}")

    if apuesta_count:
        print(f"  🏆 [APUESTA_VIRAL]: {apuesta_count}")

    gold_topics = [t for t in topics if t.get("market_verdict") == "oro"]
    if gold_topics:
        print(f"\n  🎯 OPORTUNIDADES DE ORO:")
        for t in gold_topics:
            av = " 🏆" if t.get("is_apuesta_viral") else ""
            print(f"     → {t.get('video_title', '?')}{av}")
    print(f"{'─' * 60}\n")


# ═══════════════════════════════════════════════════════════════
#  CLI DIRECTO
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    validate_topics()
