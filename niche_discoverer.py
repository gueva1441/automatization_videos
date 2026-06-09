"""
niche_discoverer.py — Entry Hub / Dashboard de Inteligencia

REEMPLAZA el antiguo menú de "categorías numeradas" por un Dashboard con
3 métodos de entrada sobre 3 nichos raíz fijos (Océano / Espacio /
Lugares Abandonados):

  [A] 🕵️  SPY-ARBITRAGE
      Busca virales en INGLÉS del último mes → cruza con ES via scrapetube
      → detecta "Huecos de Mercado" (EN +1M views, ES sin competencia fresca
      con >50k views).

  [B] 🏛️  ARQUEOLOGÍA DIGITAL
      Gemini + Google Search busca misterios cíclicos o eventos
      fascinantes del período 1950-2000 → aplica Búsqueda Negativa
      (Regla 3-50-24) → si casi no hay competencia ES en 24 meses,
      es candidato a [APUESTA_VIRAL].

  [C] ✏️  INYECCIÓN MANUAL
      Input directo del usuario (ej. "el barco fantasma del ártico").

Salida: data/selected_seeds.json con lista de "seeds" (semillas de temas).
Cada seed lleva `discovery_mode` para trazabilidad en todo el pipeline.

Consume:
  - modules.youtube_scanner (search_viral_english, count_competing_spanish)
  - gemini_client (extracción de temas EN→ES + búsqueda arqueológica)
"""

import json
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import uuid
from datetime import datetime, timedelta
from pathlib import Path

from google.genai import types

from config import (
    api,
    apuesta_viral,
    gemini_client,
    DATA_DIR,
)
from error_handler import error_handler, PipelineStage
from cost_tracker import cost_tracker

from script_engine.youtube_scanner import (
    count_competing_spanish,
    extract_anchors,
    search_viral_english,
    compute_outlier_filter,        # CHAT 42: filtro de unión (outlier ratio OR volumen)
    score_spanish_saturation,      # CHAT 44: score de saturación ES (reemplaza count en spy-arbitrage)
    EN_CANDIDATES_PER_QUERY,
    _channel_baseline,             # CHAT 50: mediana del canal (fan-out enrichment)
    compute_ratio,                 # CHAT 50: vistas ÷ mediana
    BASELINE_N,                    # CHAT 50: uploads para la mediana (mismo que el directo)
    EN_OUTLIER_WORKERS,            # CHAT 50: workers paralelos para el fetch de baselines
)
# CHAT 52: matcher ES atómico vía juez-LLM (reemplaza score_spanish_saturation/substring en el
# camino atómico). Top-level para que _check_gap_es lo use (el fan-out ya lo importa lazy ~L530).
from script_engine.subtopic_measurer import _measure_es


# ═══════════════════════════════════════════════════════════════
#  CONSTANTES
# ═══════════════════════════════════════════════════════════════

SEEDS_FILE: Path = DATA_DIR / "selected_seeds.json"

# ─── Nichos raíz (FIJOS, no editables desde el menú) ───
ROOT_NICHES: dict = {
    "oceano": {
        "es_name": "Misterios del Océano",
        "emoji": "🌊",
        "en_queries": [
            "submarine disasters history",
            "deep sea diving accidents",
            "offshore oil rig disasters",
        ],
        "tags": ["océano", "misterio", "profundidades", "abismos"],
        "archaeology_focus": (
            "expediciones oceánicas fallidas, naufragios famosos, "
            "avistamientos extraños en el mar, criaturas mal documentadas"
        ),
    },
    "espacio": {
        "es_name": "Datos del Espacio",
        "emoji": "🌌",
        "en_queries": [
            "space program disasters",
            "soviet space program disasters",
            "abandoned space facilities",
        ],
        "tags": ["espacio", "NASA", "cosmos", "misterio"],
        "archaeology_focus": (
            "misiones espaciales clasificadas, transmisiones extrañas "
            "de sondas soviéticas y NASA, eventos astronómicos inexplicados"
        ),
    },
    "abandonados": {
        "es_name": "Lugares Abandonados",
        "emoji": "🏚️",
        "en_queries": [
            "abandoned asylum prison dark history",
            "ghost town disaster abandoned",
            "industrial disaster abandoned town",
        ],
        "tags": ["abandonados", "ruinas", "pueblos fantasma", "misterio"],
        "archaeology_focus": (
            "pueblos desaparecidos, bases militares clausuradas, "
            "instalaciones secretas abandonadas, catástrofes silenciadas"
        ),
    },
}

# ─── Límites operacionales ───
SPY_TOP_PER_QUERY: int = 3              # Top N virales EN por query
SPY_ES_WINDOW_MONTHS: int = 3           # Ventana "fresco" ES para hueco de mercado
SPY_ES_MIN_VIEWS: int = 50_000          # Umbral para contar como competencia
SPY_MAX_COMPETING_FOR_GAP: int = 1      # ≤1 video ES con ≥50k en 3 meses = hueco
ES_GAP_WORKERS: int = 3   # CHAT 44: workers del loop del hueco ES. 3 IPs rotadas (_proxies_dict).
                          # Compensa el 2× del doble-scrape (ES_SCRAPE_PASSES). Score es scrapetube
                          # puro → sin límite de cuota Gemini.
# DEPRECATED chat42: el filtro absoluto se reemplazó por el filtro de unión
# (youtube_scanner.compute_outlier_filter). Se CONSERVA solo como referencia de
# comparación ("viejo≥300k") en el dry-run. El tuning del filtro nuevo vive en
# youtube_scanner.py (OUTLIER_MIN / PISO_MEDIANA / ABS_FLOOR / PISO_DEMANDA).
SPY_MIN_EN_VIEWS: int = 300_000       # (deprecado como filtro; ref de comparación)

# CHAT 49 — fix spy-subtemas, rama INDIVIDUAL (contrato cerrado en addendums 1-3).
# Flag de cableado: OFF por default = comportamiento IDÉNTICO al de hoy (cero regresión).
# Activar con env var SUBTEMA_FANOUT=1. Cuando ON: lee el transcript del viral EN, clasifica
# ATÓMICO/CONTENEDOR; los contenedores se abren en N seeds (uno por sujeto-de-segmento que
# pase el medidor ES-primero+LAXO+relevancia), cap top-K por demanda EN.
SUBTEMA_FANOUT: bool = os.getenv("SUBTEMA_FANOUT", "0") == "1"
SUBTEMA_FANOUT_CAP_K: int = 8          # decisión Omar: top-K subtemas por demanda EN (top_rel_views)

# T1 (chat 49) — sentinel de "saltear el video": fallo de infra (transcript None o classify
# ERROR). Distinto de None (=cae al flujo de hoy, 1 seed) y de list (=subtemas). El caller
# hace `continue` sin crear seed: NO fabricar un atómico sobre un video que falló por infra.
_FANOUT_SKIP = object()

ARCH_MIN_CANDIDATES: int = 5            # Candidatos mínimos de Gemini
ARCH_MAX_CANDIDATES: int = 10           # Candidatos máximos (evita gasto excesivo)

DELAY_BETWEEN_CALLS_SEC: int = 2        # Respetar rate limits

# ─── Queries dinámicas (Gemini Flash) ───
DYNAMIC_QUERIES_CACHE: Path = DATA_DIR / "dynamic_queries_cache.json"
DYNAMIC_QUERIES_TTL_HOURS: int = 24     # Validez del caché
DYNAMIC_QUERIES_COUNT: int = 5          # Cuántas queries genera Gemini por nicho


# ═══════════════════════════════════════════════════════════════
#  PERSISTENCIA DE SEEDS
# ═══════════════════════════════════════════════════════════════

def _load_seeds() -> dict:
    """Carga el archivo de seeds (o devuelve estructura vacía)."""
    if SEEDS_FILE.exists():
        try:
            return json.loads(SEEDS_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"selected_at": "", "seeds": []}


def _save_seeds(seeds: list[dict]) -> None:
    """Persiste los seeds seleccionados a disco."""
    data = {
        "selected_at": datetime.now().isoformat(),
        "seeds": seeds,
    }
    SEEDS_FILE.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def _build_seed(
    title: str,
    mode: str,
    root_niche: str | None,
    evidence: dict,
    tags: list[str] | None = None,
    nombre_en: str | None = None,
) -> dict:
    """Construye un seed estandarizado con trazabilidad completa.

    CHAT 51 — nombre_en (entidad canónica) es opcional: SOLO el fan-out lo pasa (el seed_title
    lleva el ángulo, así que la entidad pelada se guarda aparte para display/provenance). El
    camino directo (path B) no lo pasa → el seed queda idéntico a antes (sin esa clave)."""
    if tags is None and root_niche and root_niche in ROOT_NICHES:
        tags = ROOT_NICHES[root_niche]["tags"]
    elif tags is None:
        tags = []

    seed = {
        "seed_id": str(uuid.uuid4()),
        "seed_title": title.strip(),
        "discovery_mode": mode,           # spy_arbitrage | digital_archaeology | manual
        "root_niche": root_niche,          # oceano | espacio | abandonados | None
        "tags": tags,
        "evidence": evidence,              # Datos crudos que justificaron la elección
        "created_at": datetime.now().isoformat(),
    }
    if nombre_en is not None:
        seed["nombre_en"] = nombre_en      # entidad canónica (solo fan-out)
    return seed


# ═══════════════════════════════════════════════════════════════
#  HELPERS DE PARSING GEMINI
# ═══════════════════════════════════════════════════════════════

def _extract_json_array(text: str) -> list:
    """Extrae un JSON array del output de Gemini (limpia markdown)."""
    if "```" in text:
        match = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)
        if match:
            text = match.group(1).strip()

    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end == -1 or end <= start:
        raise ValueError(f"No se encontró JSON array en: {text[:200]}")

    json_str = text[start:end + 1]
    json_str = json_str.replace("\n", " ").replace("\r", " ").replace("\t", " ")
    json_str = re.sub(r" {2,}", " ", json_str)
    return json.loads(json_str)


def _concat_response_text(response) -> str:
    """Concatena todas las parts de una respuesta Gemini con grounding."""
    raw = ""
    for part in (response.candidates[0].content.parts or []):
        if part.text:
            raw += part.text
    return raw.strip()


# ═══════════════════════════════════════════════════════════════
#  QUERIES DINÁMICAS (Gemini Flash + caché 24h + fallback)
# ═══════════════════════════════════════════════════════════════

def _load_dynamic_queries_cache() -> dict:
    """
    Carga el caché de queries dinámicas.
    Estructura: {"niche_key": {"generated_at": ISO, "queries": [...]}}
    Devuelve dict vacío si no existe o está corrupto.
    """
    if not DYNAMIC_QUERIES_CACHE.exists():
        return {}
    try:
        return json.loads(DYNAMIC_QUERIES_CACHE.read_text(encoding="utf-8"))
    except Exception:
        # Caché corrupto → lo ignoramos (fallback se encargará)
        return {}


def _save_dynamic_queries_cache(cache: dict) -> None:
    """Persiste el caché de queries dinámicas a disco."""
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        DYNAMIC_QUERIES_CACHE.write_text(
            json.dumps(cache, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except Exception as e:
        # No es crítico: si falla el guardado, seguimos con las queries en memoria
        print(f"  ⚠ No se pudo guardar caché de queries: {e}")


def _is_cache_fresh(entry: dict) -> bool:
    """Devuelve True si la entrada del caché es menor a DYNAMIC_QUERIES_TTL_HOURS."""
    try:
        generated_at = datetime.fromisoformat(entry.get("generated_at", ""))
        age = datetime.now() - generated_at
        return age < timedelta(hours=DYNAMIC_QUERIES_TTL_HOURS)
    except Exception:
        return False


@error_handler.retry(PipelineStage.NICHE_DISCOVERER)
def _gemini_generate_queries(niche_key: str) -> list[str]:
    """
    DEPRECATED chat42: frente invertido, ya NO se llama (las queries ahora son las
    PUERTAS fijas niche["en_queries"]). Se conserva para reversibilidad (ver §8 handoff).
    NO borrar.

    Llama a Gemini Flash para generar DYNAMIC_QUERIES_COUNT queries virales
    en inglés para el nicho dado.

    Pide 5 estructuras sintácticas distintas para evitar repetición de
    patrones saturados en YouTube.

    Lanza excepción si Gemini no devuelve JSON válido o menos de 3 queries.
    El @retry de error_handler se encarga de reintentos automáticos.
    """
    niche = ROOT_NICHES[niche_key]
    focus = niche["archaeology_focus"]
    es_name = niche["es_name"]

    system_prompt = f"""Eres un experto en descubrimiento de contenido viral en YouTube inglés.

Tu tarea: generar {DYNAMIC_QUERIES_COUNT} queries de búsqueda en INGLÉS para encontrar
videos virales sobre el nicho: "{es_name}".

Foco temático: {focus}

REGLAS ESTRICTAS:
- Genera EXACTAMENTE {DYNAMIC_QUERIES_COUNT} queries, cada una con ESTRUCTURA SINTÁCTICA DISTINTA:
  1. Pregunta directa (ej: "what happened to ...")
  2. Afirmación impactante (ej: "the real reason why ...")
  3. Misterio con nombre propio (entidad específica: lugar, persona, evento)
  4. Top numerado (ej: "7 ... that science can't explain")
  5. Hallazgo histórico (ej: "declassified footage of ...", "1987 incident ...")
- Enfoque en PATRONES que HISTÓRICAMENTE generan millones de vistas
  (NO tendencias inciertas del futuro, NO "2025 trends", NO "2026")
- Cada query: 4 a 8 palabras máximo
- Evita frases genéricas saturadas como "mysterious history",
  "top 10 mysteries", "unexplained phenomena" (están quemadas)
- En inglés natural, como buscaría un humano, no keyword stuffing

RESPONDE ÚNICAMENTE con un JSON array de strings. Sin markdown. Sin backticks.
Formato exacto:
["query 1", "query 2", "query 3", "query 4", "query 5"]"""

    response = gemini_client.models.generate_content(
        model=api.gemini_model,  # Flash: rápido y barato
        contents=f"Nicho: {es_name}\nGenera las {DYNAMIC_QUERIES_COUNT} queries ahora.",
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.9,  # Alta = más creatividad en las queries
        ),
    )

    # Tracking de costo (regla del proyecto)
    cost_tracker.track_gemini(
        description=f"dynamic_queries: {niche_key}",
        calls=1,
    )

    text = _concat_response_text(response)
    raw = _extract_json_array(text)

    # Filtrar solo strings no vacíos
    queries = [q.strip() for q in raw if isinstance(q, str) and q.strip()]

    if len(queries) < 3:
        raise ValueError(
            f"Gemini devolvió solo {len(queries)} queries válidas "
            f"(mínimo 3) para el nicho '{niche_key}'"
        )

    return queries[:DYNAMIC_QUERIES_COUNT]


def _get_dynamic_queries(niche_key: str) -> list[str]:
    """
    DEPRECATED chat42: frente invertido, ya NO se llama desde _run_spy_arbitrage
    (ahora usa niche["en_queries"] directo). Se conserva para reversibilidad. NO borrar.

    Devuelve las queries a usar para el nicho dado, priorizando:
      1. [CACHÉ]     — si existe y es reciente (<24h)
      2. [DINÁMICAS] — llamando a Gemini Flash
      3. [FALLBACK]  — queries estáticas de ROOT_NICHES si Gemini falla

    Siempre devuelve una lista no vacía (mínimo las estáticas).
    Loggea en consola qué fuente se usó para trazabilidad.
    """
    niche = ROOT_NICHES[niche_key]
    static_queries = niche["en_queries"]

    # ─── 1. Intentar caché ───
    cache = _load_dynamic_queries_cache()
    entry = cache.get(niche_key)
    if entry and _is_cache_fresh(entry):
        cached_queries = entry.get("queries", [])
        if cached_queries:
            print(f"      [CACHÉ] usando {len(cached_queries)} queries guardadas (<24h)")
            return cached_queries

    # ─── 2. Intentar generar dinámicas con Gemini ───
    try:
        dynamic = _gemini_generate_queries(niche_key)
        print(f"      [DINÁMICAS] Gemini generó {len(dynamic)} queries nuevas")

        # Actualizar caché
        cache[niche_key] = {
            "generated_at": datetime.now().isoformat(),
            "queries": dynamic,
        }
        _save_dynamic_queries_cache(cache)

        return dynamic

    except Exception as e:
        # ─── 3. Fallback a estáticas ───
        error_handler.log_error(
            PipelineStage.NICHE_DISCOVERER, e,
            context={"niche_key": niche_key, "step": "dynamic_queries"},
        )
        print(
            f"      [FALLBACK/ESTÁTICAS] Gemini falló → usando "
            f"{len(static_queries)} queries estáticas de ROOT_NICHES"
        )
        return static_queries


# ═══════════════════════════════════════════════════════════════
#  MODO A — SPY-ARBITRAGE
# ═══════════════════════════════════════════════════════════════

@error_handler.retry(PipelineStage.NICHE_DISCOVERER)
def _gemini_translate_viral_titles(viral_items: list[dict]) -> list[dict]:
    """
    Una sola llamada a Gemini que:
      1. Extrae el TEMA CENTRAL de cada título viral EN
      2. Lo traduce a español natural (sin clickbait)
      3. Devuelve pares {original_title, spanish_topic}

    Esto minimiza llamadas API: 1 request procesa todos los virales a la vez.
    """
    if not viral_items:
        return []

    # Compactar a un bloque numerado
    titles_block = "\n".join(
        f"{i+1}. {v['title']}"
        for i, v in enumerate(viral_items)
    )

    system_prompt = """Eres un traductor de contenido viral inglés→español.

Recibirás una lista numerada de títulos virales en inglés de YouTube.
Para CADA título, extrae el TEMA CENTRAL (no el clickbait) y tradúcelo a
español natural y corto, como si alguien fuera a buscarlo en Google.

REGLAS:
- PRESERVÁ LA ENTIDAD ESPECÍFICA: si el título inglés menciona un nombre propio, lugar,
  caso, persona o evento concreto (ej. "Corpsewood Manor", "Centralia", "USS Thresher"),
  CONSERVALO TAL CUAL en el spanish_topic. NO lo generalices a la categoría
  ("casa abandonada", "pueblo fantasma", "submarino hundido").
- Solo generalizá cuando el título inglés NO tenga una entidad nombrable (es genuinamente
  una compilación/listicle sin un caso único, ej. "top 10 lugares abandonados").
- Si el evento, obra o lugar se conoce en español con un nombre o título DISTINTO al inglés
  (películas/documentales con título traducido, nombres localizados), usá el nombre con el que
  REALMENTE se busca en español — no la transliteración del nombre inglés. La búsqueda en YouTube
  en español tiene que encontrar el contenido que ya existe sobre el tema.
- "spanish_topic": preferí 8 palabras o menos, PERO el límite es flexible si hace falta para
  conservar el nombre propio: preferí "Mansión Corpsewood crimen sin resolver Georgia"
  (específico) antes que "casa abandonada misteriosa Georgia" (genérico).
- Sin signos de interrogación ni exclamación
- Sin "cómo", "por qué", "sabías que", "te voy a contar"
- Tema concreto, buscable (ej: "misterio del triángulo de las bermudas")
- Mantén el orden original (1, 2, 3, ...)
- "event_key": slug corto en minúsculas del EVENTO REAL del título (ej. nombre propio del suceso).
  Títulos que tratan del MISMO suceso real deben llevar el MISMO event_key, aunque el wording difiera.
  Ante la duda, usá keys DISTINTAS (mejor no agrupar de más).

RESPONDE ÚNICAMENTE con un JSON array válido. Sin markdown. Sin backticks.
Formato:
[{"index":1,"spanish_topic":"tema en español corto","event_key":"slug-del-evento"}, ...]"""

    response = gemini_client.models.generate_content(
        model=api.gemini_model,  # Flash (rápido y barato)
        contents=f"Títulos virales a traducir:\n\n{titles_block}",
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.3,   # Baja temp = traducción consistente
        ),
    )

    text = _concat_response_text(response)
    translated = _extract_json_array(text)

    # Mapear de vuelta con metadata original
    result = []
    for t in translated:
        idx = t.get("index", 0) - 1
        if 0 <= idx < len(viral_items):
            original = viral_items[idx]
            result.append({
                "original_title": original["title"],
                "spanish_topic": t.get("spanish_topic", "").strip(),
                "views": original.get("views", 0),
                "video_id": original.get("video_id", ""),
                "source_query": original.get("source_query", ""),
                "root_niche": original.get("root_niche"),
                "en_age_months": original.get("en_age_months"),   # CHAT 44 D: edad del viral EN (ingrediente joya)
                "event_key": (t.get("event_key", "") or "").strip().lower(),
            })
    return result

def _print_dry_run_table(rows: list[dict]) -> None:
    """GATE 4 (chat 42): tabla de candidatos que pasaron el filtro de unión, con la
    evidencia (views/median/ratio/razón) para el ojo de Omar. viejo = filtro absoluto
    deprecado (≥300k) para comparar."""
    print(f"\n  {'nicho':<11} {'título':<42} {'views':>11} {'mediana':>10} "
          f"{'ratio':>7} {'razón':>8} {'viejo≥300k':>10}  {'puerta':<26}")
    print("  " + "─" * 132)
    for r in sorted(rows, key=lambda x: (x.get("root_niche") or "", x.get("source_query") or "", -(x.get("ratio") or 0))):
        t = r.get("original_title") or r.get("title") or ""
        t = (t[:40] + "…") if len(t) > 41 else t
        med = f"{r['median']:,.0f}" if r.get("median") is not None else "—"
        ratio = f"{r['ratio']:.1f}x" if r.get("ratio") else "—"
        old = "✅" if (r.get("views") or 0) >= SPY_MIN_EN_VIEWS else "·"
        sq = (r.get("source_query") or "")[:24]
        print(f"  {(r.get('root_niche') or '—'):<11} {t:<42} {r.get('views', 0):>11,} "
              f"{med:>10} {ratio:>7} {r.get('passed_reason', ''):>8} {old:>10}  {sq:<26}")


def _try_subtema_fanout(rep_item: dict, root_niche, worst_sat: dict, n_variants: int) -> list[dict] | None:
    """CHAT 49 — fan-out de subtemas (solo con SUBTEMA_FANOUT=1).

    Lee el transcript del viral EN, lo clasifica ATÓMICO/CONTENEDOR:
      - sin transcript / ATÓMICO / ERROR → devuelve None  → el caller cae al flujo de HOY
        (1 seed genérico, con el descarte ES-evento de siempre).
      - CONTENEDOR → SALTEA el descarte ES-evento (decisión Omar #4: medir ES por subtema),
        extrae sujetos-de-segmento, mide cada uno (ES-primero + LAXO + relevancia EN),
        emite top-K por demanda EN. Devuelve list[seed] (puede ser vacía).

    NO persiste — solo construye seeds. Imports locales (evitar cualquier circular).
    """
    from script_engine.transcript_fetch import fetch_transcript
    from script_engine.subtopic_classifier import classify
    from script_engine.subtopic_extractor import extract_segment_subjects, verify_names
    from script_engine.subtopic_measurer import (
        _measure_en_laxo, _measure_es, ES_SATURATED_LABEL,
    )

    vid = rep_item.get("video_id")
    en_title = rep_item.get("original_title") or rep_item.get("spanish_topic") or ""

    transcript = fetch_transcript(vid)
    if transcript is None:
        # T1: FALLO DE INFRA (no "sin subs"). NO fabricar atómico → saltear el video.
        print(f"        [fanout] FALLO DE INFRA al traer transcript ({vid}) → SKIP (no se crea seed)")
        return _FANOUT_SKIP
    if not transcript:
        print(f"        [fanout] sin transcript ({vid}) → flujo de hoy (1 seed)")
        return None

    cls = classify(en_title, transcript)
    tipo = cls.get("tipo")
    if tipo == "ERROR":
        # T1 (mismo principio que el transcript): clasificación falló por infra → SKIP, no
        # fabricar un seed atómico sobre un video cuya clasificación nunca corrió de verdad.
        print(f"        [fanout] classify ERROR ({vid}) → SKIP (no se crea seed): {cls.get('razon')}")
        return _FANOUT_SKIP
    if tipo != "CONTENEDOR":
        print(f"        [fanout] {tipo} → flujo de hoy (1 seed)")
        return None

    subjects = extract_segment_subjects(en_title, transcript)   # CHAT 51: dicts {nombre_en, search_query_en, angle_en}

    # ── T3: FASE EN (BARATA) para TODOS los sujetos → ordenar por demanda EN → cap top-K ──
    # Antes se medía EN+ES juntos por sujeto (se pagaba el ES caro de los que el cap tiraba).
    # Ahora: EN-only para todos, cap, y RECIÉN ES a los ≤K ganadores.
    # CHAT 51: BUSCA con search_query_en (angulado → on-topic), relevancia vs nombre_en (entidad).
    en_passing: list[tuple] = []                      # [(subj, en)]
    for subj in subjects:
        en = _measure_en_laxo(subj["search_query_en"], subj["nombre_en"])
        if en.get("error"):
            continue                                  # EN_ERROR → no compite
        if en.get("pasa_laxo"):
            en_passing.append((subj, en))
    en_passing.sort(key=lambda se: se[1].get("top_rel_views", 0), reverse=True)
    capped = en_passing[:SUBTEMA_FANOUT_CAP_K]
    dropped = len(en_passing) - len(capped)           # tirados por el cap ANTES de pagar ES

    # ── T3: FASE ES (CARA) solo a los ≤K ganadores. Compuerta ES-primero DENTRO del cap:
    # un ganador EN que salga SATURADO en ES cae igual (orden final = EN-cap → ES-gate → seed).
    survivors: list[tuple] = []                       # [(subj, en, es)]
    es_gated = 0
    for subj, en in capped:
        es = _measure_es(subj["search_query_en"], subj["nombre_en"])
        if es.get("label") == "ERROR":
            continue                                  # ES_ERROR → no emite
        if es.get("label") == ES_SATURATED_LABEL:
            es_gated += 1                             # ganador EN pero saturado en ES → cae
            continue
        survivors.append((subj, en, es))

    verif = verify_names([subj["nombre_en"] for subj, _, _ in survivors])  # review-flag (D4), por ENTIDAD, NUNCA dropea

    # ── CHAT 50: ratio + mediana del canal SOLO sobre los ≤K survivors (DESPUÉS del cap T3
    # y del ES-gate). El fetch get_channel es lo único caro → jamás antes del cap. En paralelo
    # (mismo patrón que compute_outlier_filter), cacheado por channel_id (dos subtemas pueden
    # compartir canal → un solo fetch). NO es filtro: se calcula como CAMPO (insumo del juez
    # Criterio #1 + trazabilidad), nunca como condición de descarte (D5/LAXO sigue siendo el gate).
    baseline_cache: dict[str, float | None] = {}
    cids_to_fetch: dict[str, int] = {}   # channel_id → exclude views (del primer survivor del canal)
    for _subj, en, _es in survivors:
        cid = en.get("top_rel_channel_id")
        if cid and cid not in cids_to_fetch:
            cids_to_fetch[cid] = int(en.get("top_rel_views") or 0)

    def _fetch_baseline(cid: str, exclude_views: int):
        return cid, _channel_baseline(cid, BASELINE_N, exclude=exclude_views)

    if cids_to_fetch:
        with ThreadPoolExecutor(max_workers=EN_OUTLIER_WORKERS) as ex:
            futures = [ex.submit(_fetch_baseline, cid, ev) for cid, ev in cids_to_fetch.items()]
            for fut in as_completed(futures):
                cid, median = fut.result()
                baseline_cache[cid] = median

    out: list[dict] = []
    for subj, en, es in survivors:
        nombre_en = subj["nombre_en"]
        angle_en = subj.get("angle_en") or nombre_en
        vf = verif.get(nombre_en, {})
        cid = en.get("top_rel_channel_id")
        views = int(en.get("top_rel_views") or 0)
        median = baseline_cache.get(cid) if cid else None
        ratio = compute_ratio(views, median) if median else 0.0
        # CHAT 51: el seed_title lleva el ÁNGULO (entidad + por-qué) → el research groundea sobre
        # la unidad correcta (no "Cambodia" pelado → research genérico). nombre_en va aparte.
        seed_title = f"{nombre_en}: {angle_en}" if angle_en and angle_en != nombre_en else nombre_en
        # CHAT 51: línea de auditoría — cada label trazable en vivo (search trajo data, cuántos
        # quedaron tras el juez, si el fallback over-narrow disparó).
        _fb = lambda b: "S" if b else "N"
        print(f"        [audit] {nombre_en} · EN q='{subj['search_query_en']}' "
              f"cands={en.get('n_cands')} rel={en.get('n_relevantes')} "
              f"fb={_fb(en.get('query_fallback'))} top={views}v")
        print(f"                ES q='{es.get('es_query')}' cands={es.get('n_cands_es')} "
              f"kept={es.get('ontopic_count')} fb={_fb(es.get('query_fallback'))} → {es.get('label')}")
        out.append(_build_seed(
            title=seed_title,
            mode="spy_arbitrage",
            root_niche=root_niche,
            nombre_en=nombre_en,
            evidence={
                "en_viral": {
                    "original_title": en.get("top_rel_title"),
                    "views": en.get("top_rel_views"),
                    "video_id": en.get("top_rel_video_id"),
                    "query": subj["search_query_en"],   # CHAT 51: lo que se buscó de verdad (trazabilidad)
                    "query_fallback": en.get("query_fallback", False),  # over-narrow → re-busca pelado
                    # CHAT 51: observabilidad — distinguir hueco real de búsqueda vacía.
                    "n_cands": en.get("n_cands"),                  # crudos del search EN
                    "n_relevantes": en.get("n_relevantes"),        # tras is_relevant
                    # CHAT 50: nombres idénticos al camino directo (path B) → el juez Criterio #1
                    # y el menú rico los leen sin ramas especiales.
                    "outlier_ratio": ratio,                        # 2.2 (solo survivors, post-cap)
                    "channel_median": median,                      # 2.2
                    "en_age_months": en.get("top_rel_age_months"),  # 2.1 (gratis)
                    "passed_reason": "laxo",
                },
                "es_gap": {
                    "saturation": es.get("saturation"),
                    "label": es.get("label"),
                    "heaviest": es.get("heaviest"),
                    "ontopic_count": es.get("ontopic_count"),
                    "anchors_used": es.get("anchors_used"),
                    "source": es.get("source"),
                    # CHAT 51: observabilidad ES — ontopic_count=0 ambiguo (juez descartó vs search vacío).
                    "es_query": es.get("es_query"),                # la query ES real usada
                    "n_cands_es": es.get("n_cands_es"),            # crudos ANTES del juez
                    "query_fallback": es.get("query_fallback", False),
                },
                "subtema_of_container": {
                    "parent_video_id": vid,
                    "parent_title": en_title,
                },
                "asr_verify": {"canonical": vf.get("canonical"), "is_real": vf.get("is_real")},
                "fanout": {"role": "subtema",
                           "subjects_extracted": len(subjects),
                           "en_passing": len(en_passing),
                           "emitted": len(survivors),
                           "dropped_by_cap": dropped,        # cap recortó ANTES de pagar ES
                           "es_gated_in_cap": es_gated},
            },
        ))
    es_paid = len(capped)            # mediciones ES nuevas
    es_old = len(subjects)           # lo que el flujo viejo (ES-primero a todos) habría pagado
    print(f"        [fanout] CONTENEDOR: {len(subjects)} sujetos · {len(en_passing)} pasan EN "
          f"→ cap K={SUBTEMA_FANOUT_CAP_K} ({dropped} drop pre-ES) · {es_gated} ES-saturados "
          f"→ {len(out)} seeds  [ES medido {es_paid} vs {es_old} viejo, ahorro {es_old - es_paid}]")
    return out


def _run_spy_arbitrage(niche_keys: list[str], dry_run: bool = False) -> list[dict]:
    """
    Modo A — SPY-ARBITRAGE (CHAT 42: flujo INVERTIDO).
    Flujo:
      1. Por nicho → PUERTAS FIJAS (niche["en_queries"]) → search_viral_english SIN
         filtro absoluto → compute_outlier_filter (ratio get_channel-fork OR volumen,
         + dedupe por video_id).                                          [NUEVO]
      2. Traduce títulos a ES en bulk con Gemini (1 sola llamada).        [SE QUEDA]
      3. Por cada tema ES → count_competing_spanish CON ANCLAS.           [SE QUEDA]
      4. Si competing_count ≤ 1 → HUECO DE MERCADO → se crea seed.

    dry_run=True (GATE 4): imprime la tabla de candidatos (views/median/ratio/passes)
    y los corta ANTES de traducir/competir/persistir (no gasta Gemini ni escribe nada).
    El frente Gemini viejo (_get_dynamic_queries) queda deprecado, no se llama.
    """
    print(f"\n  🕵️  Iniciando SPY-ARBITRAGE (flujo invertido) para {len(niche_keys)} nicho(s)\n")

    # ─── Paso 1: recolectar candidatos EN por PUERTAS + filtro de unión ───
    all_viral = []
    for niche_key in niche_keys:
        niche = ROOT_NICHES[niche_key]
        print(f"  {niche['emoji']} {niche['es_name']}")

        queries = niche["en_queries"]   # CHAT 42: PUERTAS FIJAS (ya NO _get_dynamic_queries)
        niche_candidates: list[dict] = []
        for query in queries:
            print(f"      🔍 '{query}'...")
            viral = search_viral_english(query)   # min_views=0 → sin filtro absoluto
            for v in viral[:EN_CANDIDATES_PER_QUERY]:
                v["root_niche"] = niche_key
                v["source_query"] = query
                niche_candidates.append(v)
            print(f"         → {min(len(viral), EN_CANDIDATES_PER_QUERY)} candidatos EN crudos")
            time.sleep(DELAY_BETWEEN_CALLS_SEC)

        # Filtro de UNIÓN (outlier ratio OR volumen) + dedupe — scrapea get_channel.
        print(f"      🧮 filtro de unión sobre {len(niche_candidates)} candidatos "
              f"(get_channel-fork por canal)...")
        passed = compute_outlier_filter(niche_candidates)
        print(f"         → {len(passed)} pasaron (de {len(niche_candidates)})")
        all_viral.extend(passed)

    if not all_viral:
        print("\n  ⚠ Ningún candidato EN pasó el filtro de unión.")
        print("     Posibles causas: proxy caído, rate limit, o get_channel del fork falló.")
        return []

    # ─── CHAT 42: dedupe CROSS-nicho (un video puede matchear puertas de 2 nichos,
    # ej. UFO en espacio Y oceano). compute_outlier_filter ya dedupea DENTRO de un
    # nicho; acá, sobre el pool unido, nos quedamos con la entrada de MAYOR ratio. ───
    by_vid: dict[str, dict] = {}
    for c in all_viral:
        vid = c.get("video_id") or ""
        if not vid:                       # sin video_id no se puede dedupe → conservar
            by_vid[f"_novid_{id(c)}"] = c
            continue
        prev = by_vid.get(vid)
        if prev is None or (c.get("ratio") or 0) > (prev.get("ratio") or 0):
            by_vid[vid] = c
    dropped = len(all_viral) - len(by_vid)
    if dropped:
        print(f"\n  🔁 dedupe cross-nicho: {dropped} duplicado(s) removido(s) "
              f"(se conservó el de mayor ratio)")
    all_viral = list(by_vid.values())

    # ─── GATE 4: dry-run → tabla + corte antes de Gemini/competencia/persistencia ───
    if dry_run:
        _print_dry_run_table(all_viral)
        print(f"\n  🧪 DRY-RUN: {len(all_viral)} candidatos pasaron el filtro EN. "
              f"NO se tradujo, NO se chequeó competencia ES, NO se escribió nada.")
        print(f"     (En run real: estos van a Gemini translate → count_competing_spanish "
              f"→ seed.)")
        return all_viral

    print(f"\n  📊 Total candidatos EN que pasaron: {len(all_viral)}")
    print(f"  🌐 Traduciendo y extrayendo temas centrales con Gemini...\n")

    # ─── Paso 2: traducir EN → ES ───
    try:
        translated = _gemini_translate_viral_titles(all_viral)
    except Exception as e:
        print(f"  ❌ Error traduciendo: {e}")
        return []

    if not translated:
        print("  ⚠ Gemini no devolvió traducciones válidas.")
        return []

    # CHAT 44: dedupe de spanish_topic. Gemini repite traducciones; cada dup se scrapearía aparte
    # con labels inconsistentes (flip-flop) e inflaría el conteo. Normaliza y deja el primero.
    _seen_topics: set[str] = set()
    _deduped = []
    for item in translated:
        _key = (item.get("spanish_topic") or "").strip().lower()
        if not _key or _key in _seen_topics:
            continue
        _seen_topics.add(_key)
        _deduped.append(item)
    print(f"     Dedupe ES: {len(translated)} → {len(_deduped)} temas únicos")
    translated = _deduped

    # ─── Paso 3: validar arbitraje (competencia ES con filtro de anclas) ───
    print(f"  🎯 Validando arbitraje (Regla <50k ES fresco, con anclas)...\n")
    seeds = []
    label_counts: dict[str, int] = {}

    # CHAT 42: lookup por video_id para sumar ratio/median al evidence (sin tocar el
    # traductor Gemini, que no propaga esos campos).
    evidence_by_vid = {v.get("video_id"): v for v in all_viral}

    # ─── worker paralelizable: anchors + score, SIN estado compartido ni prints ───
    def _check_gap_es(item):
        if not item.get("spanish_topic"):
            return None
        # CHAT 52: el atómico ya está en español → _measure_es(already_es=True): juez LLM en vez de
        # substring (el substring fallaba en ambas direcciones — ver lab atomic_es_matcher).
        sat = _measure_es(item["spanish_topic"], already_es=True)
        return (item, None, sat)

    print(f"  ⚙ Evaluando {len(translated)} temas con {ES_GAP_WORKERS} workers...\n")
    gap_results = []
    with ThreadPoolExecutor(max_workers=ES_GAP_WORKERS) as ex:
        futures = [ex.submit(_check_gap_es, it) for it in translated]
        for fut in as_completed(futures):
            try:
                r = fut.result()
            except Exception as e:
                print(f"     ⚠ Worker gap ES falló: {e}")
                continue
            if r:
                gap_results.append(r)

    # ─── post-proceso SECUENCIAL: agrupar variantes del MISMO evento real (event_key) ───
    from collections import defaultdict
    groups: dict[str, list] = defaultdict(list)
    for item, anchors, sat in gap_results:
        if sat["label"] == "ERROR":
            print(f"     ⚠ Error saturación ES '{item['spanish_topic']}': {sat.get('error')}")
            continue
        key = item.get("event_key") or (item.get("spanish_topic") or "").strip().lower()
        groups[key].append((item, anchors, sat))

    # un seed por evento; saturación del evento = la MÁS ALTA entre variantes
    for key, variants in groups.items():
        worst_item, worst_anchors, worst_sat = max(variants, key=lambda v: v[2]["saturation"])
        n = len(variants)
        tag = f" [{n} variantes]" if n > 1 else ""
        label_counts[worst_sat["label"]] = label_counts.get(worst_sat["label"], 0) + 1

        # representante EN = variante con más views (viral más fuerte); ES = la de mayor saturación
        rep_item = max(variants, key=lambda v: v[0].get("views", 0))[0]

        # CHAT 49 — fan-out de subtemas (solo con SUBTEMA_FANOUT=1). Si el viral es CONTENEDOR,
        # se abre en N seeds y se SALTEA el descarte ES-evento (decisión #4: ES por subtema).
        # Si devuelve None (flag OFF, sin transcript, o ATÓMICO) → cae al flujo de HOY.
        if SUBTEMA_FANOUT:
            fanned = _try_subtema_fanout(rep_item, rep_item.get("root_niche"), worst_sat, n)
            if fanned is _FANOUT_SKIP:
                # T1: fallo de infra (transcript None / classify ERROR) → saltear el video
                # SIN crear seed. NO caer al flujo de hoy (eso fabricaría un atómico falso).
                print(f"     ⏭  SKIP (fallo de infra en transcript/clasificación) · {key}{tag}")
                continue
            if fanned is not None:
                seeds.extend(fanned)
                continue

        if worst_sat["label"] == "SATURADO":
            print(f"     SATURADO ({worst_sat['saturation']:>11,.0f}) · {key}{tag} → descartado")
            continue

        print(f"     {worst_sat['label']:>9} ({worst_sat['saturation']:>11,.0f}) · {rep_item['spanish_topic']}{tag}")
        # CHAT 52: línea de auditoría ES para atómicos (espejo de la del fan-out ~L626-633; atómico =
        # solo lado ES, el viral EN es el original hallado). Trazable: search trajo data, cuántos
        # quedaron tras el juez, si el fallback over-narrow disparó.
        _fb = lambda b: "S" if b else "N"
        print(f"        [audit] {rep_item['spanish_topic']} · "
              f"ES q='{worst_sat.get('es_query')}' cands={worst_sat.get('n_cands_es')} "
              f"kept={worst_sat.get('ontopic_count')} fb={_fb(worst_sat.get('query_fallback'))} "
              f"→ {worst_sat.get('label')}")
        seed = _build_seed(
            title=rep_item["spanish_topic"],
            mode="spy_arbitrage",
            root_niche=rep_item["root_niche"],
            evidence={
                "en_viral": {
                    "original_title": rep_item["original_title"],
                    "views": rep_item["views"],
                    "video_id": rep_item["video_id"],
                    "query": rep_item["source_query"],
                    "en_age_months": rep_item.get("en_age_months"),
                    "channel_median": (evidence_by_vid.get(rep_item["video_id"]) or {}).get("median"),
                    "outlier_ratio": (evidence_by_vid.get(rep_item["video_id"]) or {}).get("ratio"),
                    "passed_reason": (evidence_by_vid.get(rep_item["video_id"]) or {}).get("passed_reason"),
                },
                "es_gap": {
                    "saturation": worst_sat["saturation"],
                    "label": worst_sat["label"],
                    "heaviest": worst_sat["heaviest"],
                    "ontopic_count": worst_sat["ontopic_count"],
                    "anchors_used": worst_sat["anchors_used"],
                    "source": worst_sat["source"],
                    "variants_grouped": n,
                },
            },
        )
        seeds.append(seed)

    if label_counts:
        print(f"\n  📊 Saturación ES: " + " · ".join(f"{k}={v}" for k, v in sorted(label_counts.items())))
        print(f"     → {len(seeds)} huecos (no-SATURADO) de {sum(label_counts.values())} temas evaluados")
    return seeds


# ═══════════════════════════════════════════════════════════════
#  MODO B — ARQUEOLOGÍA DIGITAL
# ═══════════════════════════════════════════════════════════════

@error_handler.retry(PipelineStage.NICHE_DISCOVERER)
def _gemini_archaeology_search(niche_keys: list[str]) -> list[dict]:
    """
    Usa Gemini Pro + Google Search grounding para encontrar misterios
    cíclicos o eventos fascinantes del período 1950-2000.
    """
    niches_block = "\n".join(
        f"- **{ROOT_NICHES[k]['es_name']}** (clave: {k}): "
        f"{ROOT_NICHES[k]['archaeology_focus']}"
        for k in niche_keys
    )

    system_prompt = f"""Eres un investigador de misterios históricos para contenido viral.

TAREA: Buscar en Google eventos fascinantes, misterios o historias poco
conocidas del período 1950-2000, dentro de los siguientes nichos:

{niches_block}

CRITERIOS ESTRICTOS:
- Evento/misterio ocurrido entre 1950 y 2000 (NO después)
- Tiene que estar documentado (no inventado), verificable
- Poco conocido hoy en 2026 (no el Triángulo de las Bermudas típico)
- Debe tener potencial narrativo: gancho → misterio → revelación/teoría
- Prioriza: expediciones perdidas, desapariciones, transmisiones extrañas,
  documentos desclasificados, catástrofes silenciadas

SUGERENCIAS DE FUENTES (si están disponibles, sin forzar URLs):
  * ArXiv.org para pre-publicaciones
  * The Black Vault y archivos desclasificados CIA (FOIA)
  * Reddit r/UnresolvedMysteries
  * BBC, National Geographic, Smithsonian

FORMATO — devuelve ENTRE {ARCH_MIN_CANDIDATES} Y {ARCH_MAX_CANDIDATES}
candidatos distribuidos entre los nichos solicitados.

REGLAS POR CANDIDATO:
- "title": máximo 8 palabras, en español, sin signos, buscable
- "year_range": rango de años (ej: "1962-1965")
- "context": 1-2 oraciones con datos verificables (nombres, fechas)
- "root_niche": exactamente una de las claves: oceano, espacio, abandonados

IMPORTANTE: Prioriza la PRECISIÓN del dato sobre las URLs. Si mencionas
un evento, asegúrate de que los nombres y años sean reales.

RESPONDE ÚNICAMENTE con un JSON array válido. Sin markdown. Sin backticks.
Formato:
[{{"title":"...","year_range":"1962-1965","context":"...","root_niche":"oceano"}}]"""

    user_prompt = (
        f"Busca misterios reales 1950-2000 en los nichos indicados. "
        f"Dame entre {ARCH_MIN_CANDIDATES} y {ARCH_MAX_CANDIDATES} "
        f"candidatos. Prioriza lo poco conocido pero verificable."
    )

    response = gemini_client.models.generate_content(
        model=api.gemini_model_research,  # Pro: mejor razonamiento histórico
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            tools=[types.Tool(google_search=types.GoogleSearch())],
            temperature=0.8,
        ),
    )

    text = _concat_response_text(response)
    candidates = _extract_json_array(text)

    # Validar estructura y filtrar basura
    valid = []
    for c in candidates:
        if not isinstance(c, dict):
            continue
        if not c.get("title") or not c.get("root_niche"):
            continue
        if c["root_niche"] not in ROOT_NICHES:
            continue
        # Truncar contexto si es muy largo
        if len(c.get("context", "")) > 300:
            c["context"] = c["context"][:297] + "..."
        valid.append(c)

    return valid


def _run_archaeology(niche_keys: list[str]) -> list[dict]:
    """
    Modo B — ARQUEOLOGÍA DIGITAL.
    Flujo:
      1. Gemini + Google Search → candidatos 1950-2000
      2. Por cada candidato → count_competing_spanish CON ANCLAS (Regla 3-50-24)
      3. Si competing_count ≤ 3 → HUECO HISTÓRICO → seed con potencial [APUESTA_VIRAL]
    """
    print(f"\n  🏛️  Iniciando ARQUEOLOGÍA DIGITAL para {len(niche_keys)} nicho(s)")
    print(f"      Buscando misterios 1950-2000 con Gemini + Google Search...\n")

    # ─── Paso 1: candidatos de Gemini ───
    try:
        candidates = _gemini_archaeology_search(niche_keys)
    except Exception as e:
        print(f"  ❌ Error en búsqueda Gemini: {e}")
        return []

    if not candidates:
        print("  ⚠ Gemini no devolvió candidatos válidos.")
        return []

    print(f"  📜 Candidatos encontrados: {len(candidates)}\n")
    for i, c in enumerate(candidates, 1):
        niche = ROOT_NICHES.get(c["root_niche"], {})
        print(f"     {i}. {niche.get('emoji', '•')} {c['title']} ({c.get('year_range', '?')})")

    # ─── Paso 2: aplicar Regla 3-50-24 con filtro de anclas ───
    print(f"\n  🎯 Aplicando Regla {apuesta_viral.max_competing_videos}-"
          f"{apuesta_viral.min_views_to_count // 1000}K-"
          f"{apuesta_viral.window_months} (con anclas)...\n")
    seeds = []

    for c in candidates:
        print(f"     Evaluando: '{c['title']}'...")

        # Anclas extraídas del título narrativo + año de year_range
        # (year_range es algo como "1955" o "1968-1974"; lo concatenamos
        # al título para que extract_anchors capture los años).
        text_for_anchors = f"{c['title']} {c.get('year_range', '')}"
        anchors = extract_anchors(text_for_anchors)
        if anchors:
            print(f"       🎯 Anclas: {anchors}")

        comp = count_competing_spanish(
            c["title"],
            min_views=apuesta_viral.min_views_to_count,
            window_months=apuesta_viral.window_months,
            anchors=anchors,
        )

        if comp["competing_count"] < 0:
            print(f"       ⚠ Error de competencia ES (fallo scraping)")
            time.sleep(DELAY_BETWEEN_CALLS_SEC)
            continue

        is_gap = comp["competing_count"] <= apuesta_viral.max_competing_videos

        status = "🏛️  HUECO HISTÓRICO" if is_gap else f"❌ Saturado ({comp['competing_count']} videos)"
        print(f"       {status}")

        if is_gap:
            seed = _build_seed(
                title=c["title"],
                mode="digital_archaeology",
                root_niche=c["root_niche"],
                evidence={
                    "historical": {
                        "year_range": c.get("year_range", ""),
                        "context": c.get("context", ""),
                    },
                    "es_negative_search": {
                        "rule": f"{apuesta_viral.max_competing_videos}-"
                                f"{apuesta_viral.min_views_to_count // 1000}K-"
                                f"{apuesta_viral.window_months}",
                        "competing_count": comp["competing_count"],
                        "anchors_used": comp.get("anchors_used", []),
                        "top_titles": comp.get("top_titles", []),
                        "source": comp.get("source", "unknown"),
                    },
                    # Bandera para el validator: este seed debe evaluarse
                    # como potencial [APUESTA_VIRAL] si pasa Trends > 70.
                    "is_apuesta_viral_candidate": True,
                },
            )
            seeds.append(seed)

        time.sleep(DELAY_BETWEEN_CALLS_SEC)

    return seeds

# ═══════════════════════════════════════════════════════════════
#  MODO C — INYECCIÓN MANUAL
# ═══════════════════════════════════════════════════════════════

def _run_manual() -> list[dict]:
    """
    Modo C — INYECCIÓN MANUAL.
    Loop: pide un tema; enter vacío termina.
    Pregunta el nicho raíz (opcional).
    """
    print("\n  ✏️  INYECCIÓN MANUAL")
    print("     Ingresá temas uno por uno. Enter vacío para terminar.\n")

    seeds = []
    while True:
        title = input("     📌 Tema: ").strip()
        if not title:
            break

        # Nicho raíz (opcional)
        print("        Nicho raíz:")
        for i, (key, niche) in enumerate(ROOT_NICHES.items(), 1):
            print(f"          [{i}] {niche['emoji']} {niche['es_name']}")
        print(f"          [0] Ninguno / otro")

        choice = input("        👉 ").strip()
        niche_keys = list(ROOT_NICHES.keys())
        root = None
        if choice.isdigit():
            idx = int(choice)
            if 1 <= idx <= len(niche_keys):
                root = niche_keys[idx - 1]

        seed = _build_seed(
            title=title,
            mode="manual",
            root_niche=root,
            evidence={
                "user_input": True,
                "entered_at": datetime.now().isoformat(),
            },
        )
        seeds.append(seed)
        print(f"        ✓ '{title}' agregado\n")

    return seeds


# ═══════════════════════════════════════════════════════════════
#  SELECTOR DE NICHOS (para Modos A y B)
# ═══════════════════════════════════════════════════════════════

def _select_niches_submenu() -> list[str]:
    """
    Pregunta qué nichos raíz escanear.
    Devuelve lista de claves (ej: ['oceano', 'espacio']).
    """
    print("\n  Selecciona nichos a escanear:")
    keys = list(ROOT_NICHES.keys())
    for i, key in enumerate(keys, 1):
        niche = ROOT_NICHES[key]
        print(f"    [{i}] {niche['emoji']} {niche['es_name']}")
    print(f"    [A] Todos")

    choice = input("  👉 (números separados por coma, o A): ").strip().upper()

    if choice == "A" or choice == "":
        return keys

    # Parse números
    selected = []
    for part in choice.replace(" ", "").split(","):
        if part.isdigit():
            idx = int(part)
            if 1 <= idx <= len(keys):
                selected.append(keys[idx - 1])

    return selected if selected else keys


# ═══════════════════════════════════════════════════════════════
#  DASHBOARD PRINCIPAL
# ═══════════════════════════════════════════════════════════════

def _print_dashboard_header() -> None:
    """Imprime el encabezado del Dashboard de Inteligencia."""
    print(f"\n{'═' * 60}")
    print(f"  🎯 NICHE DISCOVERER — Dashboard de Inteligencia")
    print(f"{'═' * 60}")
    print(f"\n  Nichos raíz activos:")
    for niche in ROOT_NICHES.values():
        print(f"    {niche['emoji']} {niche['es_name']}")
    print()


def _print_main_menu() -> None:
    """Muestra las 3 opciones principales."""
    print(f"  {'─' * 56}")
    print(f"  MÉTODOS DE DESCUBRIMIENTO:\n")
    print(f"  [A] 🕵️   SPY-ARBITRAGE")
    print(f"         Busca virales EN +1M views y detecta huecos en ES")
    print()
    print(f"  [B] 🏛️   ARQUEOLOGÍA DIGITAL")
    print(f"         Misterios 1950-2000 sin competencia ES actual")
    print()
    print(f"  [C] ✏️   INYECCIÓN MANUAL")
    print(f"         Ingresar temas libremente")
    print()
    print(f"  [S] Salir sin guardar")
    print(f"  {'─' * 56}")


def _print_seeds_summary(seeds: list[dict]) -> None:
    """Resumen final de seeds generados."""
    if not seeds:
        print(f"\n  ⚠ No se generaron seeds.")
        return

    print(f"\n{'═' * 60}")
    print(f"  📦 SEEDS GENERADOS: {len(seeds)}")
    print(f"{'═' * 60}\n")

    # Agrupar por modo
    by_mode: dict = {}
    for s in seeds:
        by_mode.setdefault(s["discovery_mode"], []).append(s)

    mode_emoji = {
        "spy_arbitrage": "🕵️ ",
        "digital_archaeology": "🏛️ ",
        "manual": "✏️ ",
    }
    mode_label = {
        "spy_arbitrage": "SPY-ARBITRAGE",
        "digital_archaeology": "ARQUEOLOGÍA DIGITAL",
        "manual": "MANUAL",
    }

    for mode, items in by_mode.items():
        emoji = mode_emoji.get(mode, "•")
        label = mode_label.get(mode, mode)
        print(f"  {emoji} {label} ({len(items)}):")
        for s in items:
            niche = ROOT_NICHES.get(s.get("root_niche") or "", {})
            niche_emoji = niche.get("emoji", "•")
            tag_viral = ""
            if s["evidence"].get("is_apuesta_viral_candidate"):
                tag_viral = "  [candidato APUESTA_VIRAL]"
            print(f"     {niche_emoji} {s['seed_title']}{tag_viral}")
        print()


# ═══════════════════════════════════════════════════════════════
#  FUNCIÓN PÚBLICA PRINCIPAL
# ═══════════════════════════════════════════════════════════════

def discover_niches() -> list[dict]:
    """
    Dashboard interactivo de descubrimiento.
    Loop hasta que usuario salga. Acumula seeds de todos los modos usados.
    Guarda en data/selected_seeds.json.

    Returns:
        Lista de seeds. Vacía si usuario salió sin generar.
    """
    all_seeds: list[dict] = []

    _print_dashboard_header()

    while True:
        _print_main_menu()
        if all_seeds:
            print(f"\n  📊 Seeds acumulados en esta sesión: {len(all_seeds)}")

        choice = input("\n  👉 ").strip().upper()

        # ─── Modo A ───
        if choice == "A":
            niche_keys = _select_niches_submenu()
            if not niche_keys:
                print("  ⚠ No seleccionaste ningún nicho.")
                continue
            try:
                new_seeds = _run_spy_arbitrage(niche_keys)
            except Exception as e:
                error_handler.log_error(
                    PipelineStage.NICHE_DISCOVERER, e,
                    context={"mode": "spy_arbitrage", "niches": niche_keys},
                )
                print(f"\n  ❌ Error en SPY-ARBITRAGE: {e}")
                continue
            print(f"\n  ✓ SPY-ARBITRAGE generó {len(new_seeds)} seed(s)")
            all_seeds.extend(new_seeds)

        # ─── Modo B ───
        elif choice == "B":
            niche_keys = _select_niches_submenu()
            if not niche_keys:
                print("  ⚠ No seleccionaste ningún nicho.")
                continue
            try:
                new_seeds = _run_archaeology(niche_keys)
            except Exception as e:
                error_handler.log_error(
                    PipelineStage.NICHE_DISCOVERER, e,
                    context={"mode": "digital_archaeology", "niches": niche_keys},
                )
                print(f"\n  ❌ Error en ARQUEOLOGÍA DIGITAL: {e}")
                continue
            print(f"\n  ✓ ARQUEOLOGÍA generó {len(new_seeds)} seed(s)")
            all_seeds.extend(new_seeds)

        # ─── Modo C ───
        elif choice == "C":
            new_seeds = _run_manual()
            print(f"\n  ✓ MANUAL generó {len(new_seeds)} seed(s)")
            all_seeds.extend(new_seeds)

        # ─── Salir ───
        elif choice == "S":
            if all_seeds:
                confirm = input(
                    f"\n  ¿Descartar {len(all_seeds)} seed(s) sin guardar? [s/N]: "
                ).strip().lower()
                if confirm in ("s", "si", "sí"):
                    return []
                # Si no confirma descarte, caemos al guardado final
                break
            return []

        else:
            print("  ⚠ Opción no válida.")
            continue

        # Preguntar si quiere seguir agregando desde otro modo
        more = input("\n  ¿Agregar más seeds desde otro modo? [s/N]: ").strip().lower()
        if more not in ("s", "si", "sí"):
            break

    # ─── Guardar resultado ───
    _print_seeds_summary(all_seeds)

    if all_seeds:
        _save_seeds(all_seeds)
        print(f"  💾 Guardados en: {SEEDS_FILE.name}")
        print(f"  ➡  Siguiente paso: python -m modules.topic_researcher\n")

    return all_seeds


# ═══════════════════════════════════════════════════════════════
#  CLI DIRECTO
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    seeds = discover_niches()
    if seeds:
        print(f"\n  ✅ {len(seeds)} seed(s) listos para investigar.")
