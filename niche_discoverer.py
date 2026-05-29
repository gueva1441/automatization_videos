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
import re
import time
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
)


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
            "deep ocean mysteries unexplained",
            "terrifying ocean discoveries",
            "declassified ocean phenomena",
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
            "NASA declassified space mysteries",
            "unexplained cosmic anomalies",
            "lost space missions secrets",
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
            "abandoned places mysterious history",
            "ghost towns unexplained disappearance",
            "forbidden abandoned military bases",
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
SPY_MIN_EN_VIEWS: int = 300_000       # Viral EN = ≥ 1M views último mes

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
) -> dict:
    """Construye un seed estandarizado con trazabilidad completa."""
    if tags is None and root_niche and root_niche in ROOT_NICHES:
        tags = ROOT_NICHES[root_niche]["tags"]
    elif tags is None:
        tags = []

    return {
        "seed_id": str(uuid.uuid4()),
        "seed_title": title.strip(),
        "discovery_mode": mode,           # spy_arbitrage | digital_archaeology | manual
        "root_niche": root_niche,          # oceano | espacio | abandonados | None
        "tags": tags,
        "evidence": evidence,              # Datos crudos que justificaron la elección
        "created_at": datetime.now().isoformat(),
    }


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
- "spanish_topic": máximo 8 palabras
- Sin signos de interrogación ni exclamación
- Sin "cómo", "por qué", "sabías que", "te voy a contar"
- Tema concreto, buscable (ej: "misterio del triángulo de las bermudas")
- Mantén el orden original (1, 2, 3, ...)

RESPONDE ÚNICAMENTE con un JSON array válido. Sin markdown. Sin backticks.
Formato:
[{"index":1,"spanish_topic":"tema en español corto"}, ...]"""

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
            })
    return result

def _run_spy_arbitrage(niche_keys: list[str]) -> list[dict]:
    """
    Modo A — SPY-ARBITRAGE.
    Flujo:
      1. Por cada nicho y query → search_viral_english (top N)
      2. Traduce títulos a ES en bulk con Gemini (1 sola llamada)
      3. Por cada tema ES → count_competing_spanish CON ANCLAS (últimos 3 meses)
      4. Si competing_count ≤ 1 → HUECO DE MERCADO → se crea seed
    """
    print(f"\n  🕵️  Iniciando SPY-ARBITRAGE para {len(niche_keys)} nicho(s)\n")

    # ─── Paso 1: recolectar virales EN ───
    all_viral = []
    for niche_key in niche_keys:
        niche = ROOT_NICHES[niche_key]
        print(f"  {niche['emoji']} {niche['es_name']}")

        # Queries dinámicas (con caché 24h + fallback a estáticas)
        queries = _get_dynamic_queries(niche_key)

        for query in queries:
            print(f"      🔍 '{query}'...")
            viral = search_viral_english(
                query,
                min_views=SPY_MIN_EN_VIEWS,
            )
            for v in viral[:SPY_TOP_PER_QUERY]:
                v["root_niche"] = niche_key
                v["source_query"] = query
                all_viral.append(v)
            print(f"         → {min(len(viral), SPY_TOP_PER_QUERY)} virales encontrados")
            time.sleep(DELAY_BETWEEN_CALLS_SEC)

    if not all_viral:
        print("\n  ⚠ No se encontraron virales EN con ≥1M views.")
        print("     Posibles causas: proxy caído, rate limit, o queries muy específicas.")
        return []

    print(f"\n  📊 Total virales EN: {len(all_viral)}")
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

    # ─── Paso 3: validar arbitraje (competencia ES con filtro de anclas) ───
    print(f"  🎯 Validando arbitraje (Regla <50k ES fresco, con anclas)...\n")
    seeds = []

    for item in translated:
        if not item["spanish_topic"]:
            continue

        print(f"     Evaluando: '{item['spanish_topic']}'...")

        # Anclas extraídas del título ES para filtrar falsos positivos
        anchors = extract_anchors(item["spanish_topic"])
        if anchors:
            print(f"       🎯 Anclas: {anchors}")

        comp = count_competing_spanish(
            item["spanish_topic"],
            min_views=SPY_ES_MIN_VIEWS,
            window_months=SPY_ES_WINDOW_MONTHS,
            anchors=anchors,
        )

        if comp["competing_count"] < 0:
            print(f"       ⚠ Error de competencia ES (fallo scraping)")
            time.sleep(DELAY_BETWEEN_CALLS_SEC)
            continue

        is_gap = comp["competing_count"] <= SPY_MAX_COMPETING_FOR_GAP

        status = "🎯 HUECO DE MERCADO" if is_gap else f"❌ Saturado ({comp['competing_count']} videos ≥50k)"
        print(f"       {status}")

        if is_gap:
            seed = _build_seed(
                title=item["spanish_topic"],
                mode="spy_arbitrage",
                root_niche=item["root_niche"],
                evidence={
                    "en_viral": {
                        "original_title": item["original_title"],
                        "views": item["views"],
                        "video_id": item["video_id"],
                        "query": item["source_query"],
                    },
                    "es_gap": {
                        "competing_count": comp["competing_count"],
                        "window_months": SPY_ES_WINDOW_MONTHS,
                        "min_views_threshold": SPY_ES_MIN_VIEWS,
                        "anchors_used": comp.get("anchors_used", []),
                        "top_titles": comp.get("top_titles", []),
                        "source": comp.get("source", "unknown"),
                    },
                },
            )
            seeds.append(seed)

        time.sleep(DELAY_BETWEEN_CALLS_SEC)

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
