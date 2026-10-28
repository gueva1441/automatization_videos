"""
topic_researcher.py — Investigación de temas (REDISEÑO MODULAR)

CAMBIOS vs versión vieja:
  - El monolito _synthesize_deep_research (4ta llamada con 11 tareas) se ELIMINA.
  - LONG ahora corre 4 sub-pasos Flash separados que viven en researcher_steps/:
      step_4a_facts        → verified_facts (etiquetados) + sources
      step_4b_canonical    → canonical_subject_description
      step_4c_meta         → video_title + search_keyword + hook + mystery + reveal + angle + virality_score
      step_4d_summary      → research_summary masivo
      (el ex 4e, canon visual, lo arma fase1_5.asegurar_canon desde la ficha: F50 A)
  - Cada sub-paso recibe los anteriores ya cerrados como input fijo.
    Imposible auto-contradicción.
  - Persistencia intermedia: cada sub-paso guarda su output en
      data/scripts/_steps/{topic_id}/0X_*.json
    para debuggeo y reanudación si crashea.

  - SHORT mantiene su flujo actual (1 llamada Pro simple).
  - Las 4 angle queries Pro+grounding (TÉCNICA/HUMANA/MISTERIO/VISUAL) se reusan
    intactas — ya están bien diseñadas (SRP correcto).

CONTRATO DE SALIDA (topic en topics_db) — sin canon visual (F50: lo arma fase1_5.asegurar_canon desde la ficha):
  {
    "id": uuid,
    "seed_id": ...,
    "discovery_mode": ...,
    "video_title": "...",
    "search_keyword": "...",
    "hook": "...",
    "mystery": "...",
    "reveal": "...",
    "angle": "...",
    "canonical_subject_description": "...",
    "research_summary": "...",   (LONG: masivo, SHORT: corto)
    "sources": [...],
    "verified_facts": [...],     (LONG: list[{fact, source_block}], SHORT: list[str])
    "virality_score": int 1-10,
    "status": "researched",
    "created_at": iso
  }
"""

import json
import re
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

from google.genai import types

from config import api, gemini_client, DATA_DIR
from cost_tracker import cost_tracker   # HANDOFF_133: telemetría de las deep-research Pro+search
from error_handler import error_handler, PipelineStage

from researcher_steps.step_4a_facts import extract_facts_and_sources
from researcher_steps.step_4b_canonical import extract_canonical
from researcher_steps.step_4c_meta import extract_meta
from researcher_steps.step_4d_summary import extract_research_summary


# ═══════════════════════════════════════════════════════════════
#  PATHS
# ═══════════════════════════════════════════════════════════════

SEEDS_FILE: Path = DATA_DIR / "selected_seeds.json"
SEEDS_ARCHIVE_FILE: Path = DATA_DIR / "seeds_archive.json"
TOPICS_DB_FILE: Path = DATA_DIR / "topics_db.json"
STEPS_DIR: Path = DATA_DIR / "scripts" / "_steps"

DELAY_BETWEEN_CALLS_SEC: int = 8     # Entre seeds
DELAY_BETWEEN_ANGLES_SEC: int = 6    # Entre queries angulares del mismo seed


# ═══════════════════════════════════════════════════════════════
#  ANGLE QUERIES (DEEP RESEARCH para video_type == "long")
# ═══════════════════════════════════════════════════════════════
#
# Las 4 angle queries Pro+grounding se mantienen intactas (SRP correcto).
# Lo que se rediseñó es la 4ta llamada (síntesis), ahora partida en 4
# sub-pasos Flash que viven en researcher_steps/.

DEEP_RESEARCH_ANGLES: list[dict] = [
    {
        "key": "tecnico",
        "label": "TÉCNICA/CIENTÍFICA",
        "focus": (
            "Datos duros verificables: fechas exactas (día/mes/año), "
            "coordenadas, nombres de instituciones, documentos oficiales, "
            "números (tonelaje, profundidad, víctimas, fallas técnicas), "
            "investigaciones oficiales, reportes forenses. Cronología minuto "
            "a minuto si existe."
        ),
    },
    {
        "key": "humano",
        "label": "HUMANA/HISTÓRICA",
        "focus": (
            "Las personas detrás del evento: nombres reales de testigos, "
            "víctimas, investigadores, autoridades involucradas. Contexto "
            "histórico (qué estaba pasando en el mundo ese año). "
            "Testimonios documentados con citas textuales cuando sea posible. "
            "Destinos posteriores de los sobrevivientes."
        ),
    },
    {
        "key": "misterio",
        "label": "MISTERIO/TEORÍAS",
        "focus": (
            "Qué queda sin explicar. Teorías alternativas (oficiales y no "
            "oficiales). Coincidencias extrañas. Documentos desclasificados. "
            "Reportes contradictorios. Por qué el caso sigue abierto. "
            "Paralelos con otros casos similares. Qué investigadores serios "
            "siguen estudiando hoy."
        ),
    },
    # ─── ESLABÓN 1: 4º ángulo VISUAL/MATERIAL ───
    # Foco SOURCED-vs-INFERIDO (del probe _lab_4e_visual_canon_v3).
    # OJO: este ángulo NO usa el builder genérico (pierde [ARQUITECTURA]/
    # [SOURCED vs INFERIDO]); tiene su propio _build_visual_angle_prompt.
    # Por ahora solo se PRODUCE y persiste en angle_blocks; nadie lo
    # consume aguas abajo todavía (eso es eslabón 2).
    {
        "key": "visual",
        "label": "VISUAL/MATERIAL",
        "focus": (
            "Como se ve REALMENTE el tema segun FUENTES DOCUMENTADAS (fotos, "
            "footage, planos, registros de archivo), NO inferencia de epoca. "
            "Arquitectura del lugar puntual: estilo constructivo, materiales y "
            "texturas de fachada e interior, dimensiones (altura, pisos, "
            "huella/escala), y los rasgos distintivos que identifican a ESTE "
            "lugar y no a otro de su tipo. Paleta de color exterior e interior. "
            "Condicion fisica y su evolucion en el tiempo (de intacto a "
            "deterioro o demolicion). Composicion demografica documentada de la "
            "poblacion o del rol del lugar (etnia, nacionalidad, perfil del "
            "grupo), tratada como GRUPO o ROL, nunca como rasgo de un individuo "
            "nombrable. Vestimenta y uniformes especificos del lugar o funcion, "
            "documentados, no genericos de la decada. Por CADA afirmacion visual "
            "indica si proviene de FUENTE REAL (foto/footage/plano/archivo "
            "identificable) o si es INFERENCIA de contexto. Lista que "
            "referencias visuales reales sobreviven hoy y donde."
        ),
    },
]


# F5e: el ángulo técnico suma la magnitud del evento, sin tope (la pantalla y el guion la usan: categoría, viento,
# marea, altura del agua, muertos, área)
MAGNITUDE_SECTION = """
[DATOS DE MAGNITUD]
(todas las que el evento tenga, sin tope; cada una con su cifra, su unidad y su fuente)
- categoría / escala (ej. «huracán de categoría 3 al tocar tierra»)
- vientos máximos (km/h y mph)
- marea de tormenta / crecida (metros y pies)
- altura máxima del agua en el lugar (metros y pies)
- muertos y desaparecidos (cifra oficial y estimaciones, cada una con quién la da)
- área afectada (km², % de la ciudad o región)
- ..."""


# F6a: testimonios de personas que ESTUVIERON AHÍ (el guion v3 sigue a un humano con nombre). Ángulos humano y misterio.
TESTIMONIOS_SECTION = """
[TESTIMONIOS]
(citas TEXTUALES, entre comillas, de personas que ESTUVIERON AHÍ: presos, guardias, familiares, rescatistas, vecinos,
médicos; sin tope. NO funcionarios hablando desde afuera)
- "cita textual" — Nombre Apellido, rol (preso de…, guardia de…, madre de…), fecha AAAA-MM-DD si se sabe — Fuente (autor/publicación, año)
- ...
(Para cada testigo con nombre, en qué momentos estuvo: «Nombre Apellido estuvo en <lugar> el AAAA-MM-DD …».
Si no hay testimonios con nombre, escribí «SIN TESTIMONIOS CON NOMBRE» y listá los anónimos con rol y fuente:
- "cita textual" — un preso de <lugar>, <edad si se sabe> — Fuente)"""
TESTIMONIO_ANGLES = ("humano", "misterio")


def _build_angle_query_prompt(seed: dict, angle: dict) -> str:
    """Prompt para UNA query angular (3 llamadas × seed en LONG). F5e: el ángulo técnico pide además
    [DATOS DE MAGNITUD]. F6a: humano y misterio piden además [TESTIMONIOS]."""
    magnitude = MAGNITUDE_SECTION if angle.get("key") == "tecnico" else ""
    magnitude += TESTIMONIOS_SECTION if angle.get("key") in TESTIMONIO_ANGLES else ""
    return f"""Eres un investigador de documentales para History Channel / Netflix.

TEMA: "{seed['seed_title']}"
ÁNGULO DE ESTA QUERY: {angle['label']}

FOCO DE ESTA INVESTIGACIÓN:
{angle['focus']}

INSTRUCCIONES:
1. Investigá el tema EN PROFUNDIDAD con Google Search grounding.
2. Enfocate EXCLUSIVAMENTE en el ángulo asignado ({angle['label']}).
3. Extraé TODOS los datos concretos que encuentres (fechas, nombres,
   lugares, cifras). Sin adjetivos vacíos.
4. Documentá cronologías cuando apliquen.
5. Cuando cites fuentes, usá formato textual con autor/publicación/año.
   NO inventes URLs.

FORMATO DE SALIDA — texto plano estructurado:

=== HALLAZGOS DEL ÁNGULO {angle['label']} ===

[DATOS DUROS]
- dato 1 (con fecha/nombre/cifra)
- dato 2
- ...
{magnitude}
[CRONOLOGÍA]
- YYYY-MM-DD: evento
- YYYY-MM-DD: evento
- ...

[FUENTES CONSULTADAS]
- Nombre autor/publicación, año, título del trabajo
- ...

[OBSERVACIONES DEL INVESTIGADOR]
(2-3 párrafos con tus conclusiones desde este ángulo específico)

RESPONDE SOLO CON EL BLOQUE DE TEXTO ESTRUCTURADO ARRIBA.
Sin preámbulos. Sin cierres. Sin markdown."""


def _build_visual_angle_prompt(seed: dict, angle: dict) -> str:
    """Prompt del ángulo VISUAL/MATERIAL (ESLABÓN 1).

    Builder PROPIO: el genérico (_build_angle_query_prompt) usaría
    [DATOS DUROS]/[CRONOLOGÍA] y perdería la estructura que necesita el
    canon visual ([ARQUITECTURA / MATERIALES], [SOURCED vs INFERIDO], etc.).
    Portado verbatim del probe _lab_4e_visual_canon_v3._build_visual_angle_prompt.
    """
    seed_title = seed["seed_title"]
    return f"""Eres un investigador de documentales para History Channel / Netflix.

TEMA: "{seed_title}"
ANGULO DE ESTA QUERY: {angle['label']}

FOCO DE ESTA INVESTIGACION:
{angle['focus']}

INSTRUCCIONES:
1. Investiga el tema EN PROFUNDIDAD con Google Search grounding.
2. Enfocate EXCLUSIVAMENTE en el angulo visual/material.
3. Extrae datos concretos (materiales, dimensiones, colores, condicion). Sin
   adjetivos vacios.
4. Cuando cites fuentes, usa formato textual con autor/publicacion/anio.
   NO inventes URLs.

FORMATO DE SALIDA -- texto plano estructurado:

=== HALLAZGOS VISUALES: {seed_title} ===

[ARQUITECTURA / MATERIALES]
- estilo constructivo, materiales y texturas (fachada e interior)
- dimensiones: altura / pisos / huella / escala
- rasgos distintivos que identifican a ESTE lugar

[OBJETOS / EQUIPO RECURRENTE]  (objetos fisicos que NO son el escenario ni el sujeto principal)
- incluí los objetos que cumplan LAS TRES: (a) aparecen de forma recurrente en el tema;
  (b) el caso NO EXISTIRIA sin este objeto: el evento central gira alrededor de el, es aquello
      sobre lo que trata la historia. Test: si este objeto no hubiera estado, ¿el tema sigue siendo
      el mismo tema? Si la respuesta es "si, pasa igual" → NO entra (es contexto o acompañamiento,
      por mas que aparezca seguido). El PAPEL en la historia decide, NO la categoria del objeto:
      una herramienta, un instrumento o un arma PUEDEN ser centrales si el caso gira sobre ellos;
  (c) son ESTE objeto puntual del caso (un modelo/unidad especifica), no un generico.
  NO exijas que su forma ya sea conocida para incluirlo: la forma se evalua ABAJO, no en la puerta.
- por CADA objeto incluido, completá 6 datos: silueta · proporcion · orientacion · rasgos · material/color · escala
- llená CADA dato siguiendo esta jerarquia, en orden:
    1. EJEMPLAR: hay fuente de la forma de ESTE ejemplar exacto → usala.  Marcá (EJEMPLAR: fuente).
    2. TIPO:     el ejemplar exacto no tiene forma documentada, pero su tipo/modelo/clase SI →
                 traé la forma del TIPO.  Marcala (TIPO: fuente). Es representativa de la categoria,
                 NO del ejemplar exacto.
    3. HUECO:    ni ejemplar ni tipo tienen forma documentada → HUECO. NO inventes.
  DEFAULT = bajar lo MAS especifico que exista (EJEMPLAR antes que TIPO antes que HUECO).
  Un TIPO honestamente marcado vale; un dato inventado NO. Nunca rellenes con suposiciones.
- si ningun objeto cumple (a)+(b)+(c), dejá esta seccion vacia.

[PALETA DE COLOR]
- exterior:
- interior:

[CONDICION Y EVOLUCION]
- estado en la epoca del evento -> estado posterior

[DEMOGRAFIA DOCUMENTADA]  (grupo/rol, NUNCA individuo nombrable)
- composicion etnica/nacional de la poblacion o rol del lugar
- vestimenta/uniformes especificos del lugar o funcion

[REFERENCIAS VISUALES SOBREVIVIENTES]
- que material visual real existe hoy (fotos/footage/planos/archivo) y donde

[SOURCED vs INFERIDO]
- por cada afirmacion de arriba: (FUENTE REAL: ...) o (INFERENCIA)

RESPONDE SOLO CON EL BLOQUE DE TEXTO. Sin preambulos. Sin cierres. Sin markdown."""


# Builder por key: el ángulo visual usa el propio; el resto, el genérico.
_ANGLE_PROMPT_BUILDERS = {"visual": _build_visual_angle_prompt}


@error_handler.retry(PipelineStage.TOPIC_RESEARCHER)
def _research_angle(seed: dict, angle: dict) -> str:
    """
    Ejecuta UNA query angular sobre el seed con Gemini Pro + Google Search.
    Devuelve texto plano estructurado (no JSON). Si falla → string vacío.
    """
    error_handler.log_info(
        PipelineStage.TOPIC_RESEARCHER,
        f"  [deep-{angle['key']}] investigando '{seed['seed_title']}'...",
    )

    builder = _ANGLE_PROMPT_BUILDERS.get(angle["key"], _build_angle_query_prompt)
    prompt = builder(seed, angle)

    response = gemini_client.models.generate_content(
        model=api.gemini_model_research,
        contents=prompt,
        config=types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearch())],
            temperature=0.7,
        ),
    )
    # Tracking de costo por tokens (HANDOFF_133) — Pro + google_search (deep-research, caro).
    cost_tracker.track_gemini_response(response, api.gemini_model_research, f"deep-{angle['key']}")

    raw = ""
    try:
        for part in (response.candidates[0].content.parts or []):
            if getattr(part, "text", None):
                raw += part.text
    except Exception:
        return ""

    return raw.strip()


# HANDOFF_121: wrapper de backoff canónico (error_handler.retry → exponential + jitter ante
# 429/503). Gemini NO hace cola como fal: un burst paralelo puede pegar el RPM → 429. NO toca
# _research_angle (invariante ⑥): solo envuelve la invocación. max_server_retries=3 (spec §3).
@error_handler.retry(PipelineStage.TOPIC_RESEARCHER, max_server_retries=3)
def _research_angle_with_backoff(seed: dict, angle: dict) -> str:
    return _research_angle(seed, angle)


TESTIMONIOS_ANGLE = {
    "key": "testimonios",
    "label": "TESTIMONIOS",
    "focus": ("Las PERSONAS que estuvieron ahí y lo contaron: presos, guardias, familiares, rescatistas, vecinos, "
              "médicos. Sus palabras textuales, con nombre, rol y fuente; en qué momento y lugar estaba cada una. "
              "Informes de organizaciones (HRW, ACLU, tribunales, prensa) que recogieron declaraciones con nombre."),
}


def _build_testimonios_prompt(seed: dict, angle: dict) -> str:
    """F6a: query de UN solo tema (re-research de la sección [TESTIMONIOS] de un topic ya investigado)."""
    return f"""Eres un investigador de documentales para History Channel / Netflix.

TEMA: "{seed['seed_title']}"
ÁNGULO DE ESTA QUERY: {angle['label']}

FOCO DE ESTA INVESTIGACIÓN:
{angle['focus']}

INSTRUCCIONES:
1. Investigá con Google Search grounding: informes con declaraciones, prensa, expedientes judiciales, entrevistas.
2. Copiá las citas TEXTUALES (no las parafrasees) con quién las dijo y dónde se publicaron.
3. Nunca inventes un nombre, una cita ni una fuente. Si no hay, decilo.

FORMATO DE SALIDA — texto plano estructurado:

=== HALLAZGOS DEL ÁNGULO {angle['label']} ===
{TESTIMONIOS_SECTION}

[CRONOLOGÍA]
- YYYY-MM-DD: evento que vivió un testigo (con su nombre)
- ...

[FUENTES CONSULTADAS]
- Nombre autor/publicación, año, título del trabajo
- ...

RESPONDE SOLO CON EL BLOQUE DE TEXTO ESTRUCTURADO ARRIBA.
Sin preámbulos. Sin cierres. Sin markdown."""


def research_testimonios(seed: dict) -> str:
    """F6a: una query Pro + Google Search solo de testimonios (≈ US$ 0.50). Devuelve el bloque o ""."""
    _ANGLE_PROMPT_BUILDERS.setdefault("testimonios", _build_testimonios_prompt)
    return _research_angle_with_backoff(seed, TESTIMONIOS_ANGLE)


def _gather_angle_blocks(seed: dict) -> dict[str, str]:
    """HANDOFF_121 · corre los N ángulos EN PARALELO (ThreadPool, porque _research_angle es
    SYNC), cada uno con backoff 429/503 y aislamiento de fallo por-ángulo (block='' y sigue —
    invariante ③). Devuelve {key: block} SOLO para los ángulos que devolvieron texto → forma y
    contenido idénticos al serial (invariante ①; el orden de escritura del dict no importa)."""
    def _worker(angle: dict) -> tuple[str, str, str]:
        try:
            block = _research_angle_with_backoff(seed, angle)
        except Exception as e:
            error_handler.log_warning(
                PipelineStage.TOPIC_RESEARCHER,
                f"  ángulo '{angle['key']}' falló para '{seed['seed_title']}': {e}",
            )
            block = ""
        return angle["key"], angle["label"], block

    blocks: dict[str, str] = {}
    with ThreadPoolExecutor(max_workers=len(DEEP_RESEARCH_ANGLES)) as pool:
        futures = [pool.submit(_worker, angle) for angle in DEEP_RESEARCH_ANGLES]
        for fut in as_completed(futures):
            key, label, block = fut.result()
            if block:
                blocks[key] = block
                print(f"       ✓ ángulo {label}: {len(block)} chars")
            else:
                print(f"       ⚠ ángulo {label}: vacío")
    return blocks


# ═══════════════════════════════════════════════════════════════
#  SANITIZADORES DE search_keyword (reusados del archivo viejo)
# ═══════════════════════════════════════════════════════════════

def _sanitize_search_keyword(raw: str) -> str:
    """
    Sanitiza la search_keyword aunque Gemini desobedezca el prompt:
      1. Quita años de 4 dígitos (1800-2099)
      2. Quita prefijos ruido ("El misterio de X" → "X")
      3. Limita a máximo 3 palabras significativas
    """
    if not raw or not isinstance(raw, str):
        return raw

    original = raw.strip()
    s = original

    s = re.sub(r"\b(1[89]\d{2}|20\d{2})\b", "", s)

    noise_prefixes = [
        r"(el|la|los|las)\s+misterio(s)?\s+(de|del)\s+",
        r"misterio(s)?\s+(de|del)\s+",
        r"(el|la|los|las)\s+incidente\s+(de|del)\s+",
        r"incidente(\s+(ovni|nuclear))?\s+(de|del)?\s*",
        r"(el|la)\s+desastre\s+(nuclear\s+)?(de\s+|del\s+)?",
        r"desastre\s+(nuclear\s+)?(de\s+|del\s+)?",
        r"caso\s+(de|del)\s+",
        r"(el|la)\s+desaparición\s+(de|del)\s+",
        r"(el|la)\s+naufragio\s+(de|del)\s+",
        r"(el|la)\s+implosión\s+(de|del)\s+",
        r"(el|la)\s+rescate\s+(secreto\s+)?(de|del)\s+",
        r"^(el|la|los|las|un|una)\s+",
    ]
    for pat in noise_prefixes:
        s = re.sub(pat, "", s, flags=re.IGNORECASE)

    s = re.sub(r"[,;:.]+", " ", s)
    s = re.sub(r"\s{2,}", " ", s).strip()

    words = s.split()
    if len(words) > 3:
        s = " ".join(words[:3])

    s = s.strip(" ,;:.-")
    if len(s) < 2:
        return original
    return s


def _extract_search_keyword_fallback(title: str, seed_title: str = "") -> str:
    """Extrae search_keyword heurísticamente cuando Gemini no la devolvió."""
    source = (title or seed_title or "").strip()
    if not source:
        return "misterio sin título"

    multi_token_pattern = re.compile(
        r"\b(?:[A-ZÁÉÍÓÚÑ][a-záéíóúñ]*|[A-Z]{2,}|K-\d+|\d{4})"
        r"(?:\s+(?:[A-ZÁÉÍÓÚÑ][a-záéíóúñ]*|[A-Z]{2,}|K-\d+|\d{4})){1,3}\b"
    )
    match = multi_token_pattern.search(source)
    if match:
        return match.group(0).strip()

    standalone_pattern = re.compile(r"\b(?:K-\d+|[A-Z]{3,}|[A-Z]+-\d+)\b")
    match = standalone_pattern.search(source)
    if match:
        return match.group(0).strip()

    stopwords = {
        "el", "la", "los", "las", "un", "una", "unos", "unas",
        "de", "del", "al", "a", "en", "con", "sin", "por", "para",
        "que", "qué", "y", "o", "u", "e", "es", "son", "era",
        "lo", "su", "sus", "se", "me", "te", "le", "les",
        "misterio", "misterios", "historia", "historias",
        "the", "of", "and", "an",
    }
    words = re.findall(r"\b[\wÁÉÍÓÚÑáéíóúñ]+\b", source)
    significant = [w for w in words if w.lower() not in stopwords and len(w) > 2]
    if significant:
        top = sorted(significant, key=len, reverse=True)[:3]
        keyword = " ".join(w for w in significant if w in top)[:60]
        if keyword:
            return keyword

    return (seed_title or source)[:60].strip()


# ═══════════════════════════════════════════════════════════════
#  PERSISTENCIA INTERMEDIA (cada sub-paso a disco)
# ═══════════════════════════════════════════════════════════════

def _save_step_output(topic_id: str, step_name: str, data: dict) -> None:
    """Guarda el output de un sub-paso en data/scripts/_steps/{topic_id}/{step_name}.json"""
    step_dir = STEPS_DIR / topic_id
    step_dir.mkdir(parents=True, exist_ok=True)
    step_file = step_dir / f"{step_name}.json"
    step_file.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


# ═══════════════════════════════════════════════════════════════
#  ORQUESTADOR DEEP (LONG) — los 4 sub-pasos en secuencia
# ═══════════════════════════════════════════════════════════════

def _research_seed_deep(seed: dict, existing_titles: list[str], topic_id: str | None = None) -> dict:
    """
    Deep Research para LONG: 4 angle queries Pro (incl. visual/material) + sub-pasos Flash.

    Flujo:
      1. Pre-genera topic_id (para persistencia incremental); F39: si viene `topic_id`, se usa ese (investigar_semilla)
      2. Corre las 4 angle queries EN PARALELO → angle_blocks
      3. Sub-paso 4a → verified_facts + sources
      4. Sub-paso 4b → canonical
      5. Sub-paso 4c → meta (title, search_keyword, hook, mystery, reveal, angle, virality)
      6. Sub-paso 4d → research_summary
      7. Consolida todo en un dict final con la firma esperada por el resto del pipeline.

    Cada sub-paso recibe los anteriores cerrados como input fijo.
    """
    topic_id = topic_id or str(uuid.uuid4())

    # ─── F7d: research v3 por defecto (documentos bajados y leídos; RESEARCH_V3=0 → el camino de abajo) ───
    # La compuerta del pool corre adentro: rojo → PoolGateRed (research_topics deja el seed en el inbox con el motivo).
    # Los bloques angulares para 4a–4d se arman con el pool (sin las 4 búsquedas de resumen).
    from researcher_steps.research_v3 import research_v3_enabled
    v3_pool = None
    if research_v3_enabled():
        from researcher_steps.research_v3 import run_seed
        v3_pool, angle_blocks, _ = run_seed(seed, topic_id, STEPS_DIR / topic_id)
    else:
        # ─── Paso 1: 4 angle queries Pro EN PARALELO (HANDOFF_121) ───
        # Cada ángulo depende SOLO de (seed, angle) → independiente. Antes: serie + sleeps entre
        # ángulos (~4×T). Ahora: ThreadPool con backoff 429/503 por ángulo → ~1×T + overhead.
        angle_blocks = _gather_angle_blocks(seed)

    if not angle_blocks:
        raise RuntimeError(
            "Los 4 ángulos de Deep Research fallaron. Seed no investigado."
        )

    # Persistir bloques crudos
    _save_step_output(topic_id, "00_pool_etiquetado", {"angle_blocks": angle_blocks})

    time.sleep(DELAY_BETWEEN_ANGLES_SEC)

    # ─── Sub-paso 4a: facts + sources etiquetados ───
    print(f"       → 4a: extrayendo facts + sources...")
    if v3_pool is None:
        step_4a = extract_facts_and_sources(angle_blocks)
    else:                                       # F7d: el evidence_pool es el de research v3 (no se re-extrae)
        step_4a = {**extract_facts_and_sources(angle_blocks, with_pool=False), "evidence_pool": v3_pool}
    _save_step_output(topic_id, "01_facts_sources", step_4a)
    verified_facts = step_4a.get("verified_facts", [])
    sources = step_4a.get("sources", [])

    # ─── Sub-paso 4b: canonical ───
    print(f"       → 4b: extrayendo canonical...")
    step_4b = extract_canonical(seed, angle_blocks, verified_facts)
    _save_step_output(topic_id, "02_canonical", step_4b)
    canonical = step_4b.get("canonical_subject_description", "")

    # ─── Sub-paso 4c: meta narrativa ───
    print(f"       → 4c: extrayendo meta narrativa...")
    step_4c = extract_meta(seed, angle_blocks, verified_facts, canonical)
    _save_step_output(topic_id, "03_meta", step_4c)

    # ─── Sub-paso 4d: research_summary ───
    print(f"       → 4d: extrayendo research_summary...")
    step_4d = extract_research_summary(
        seed, angle_blocks, verified_facts, canonical, step_4c
    )
    _save_step_output(topic_id, "04_summary", step_4d)
    research_summary = step_4d.get("research_summary", "")

    # F50 A: el canon visual (ex 4e) ya no nace en el research: lo arma fase1_5.asegurar_canon desde la ficha.

    # ─── Consolidación final ───
    data = {
        "_pre_topic_id": topic_id,  # Se reusa al enriquecer
        "video_title": step_4c.get("video_title", seed["seed_title"]),
        "search_keyword": step_4c.get("search_keyword", ""),
        "hook": step_4c.get("hook", ""),
        "mystery": step_4c.get("mystery", ""),
        "reveal": step_4c.get("reveal", ""),
        "angle": step_4c.get("angle", ""),
        "virality_score": step_4c.get("virality_score", 5),
        "canonical_subject_description": canonical,
        "research_summary": research_summary,
        "sources": sources,
        "verified_facts": verified_facts,
        "evidence_pool": step_4a.get("evidence_pool"),          # F5 §1.1 (None en topics viejos)
    }
    if v3_pool is not None:
        data["research_version"] = 3                                # F7d

    # ─── Sanitización defensiva (espejo del archivo viejo) ───
    if not data.get("video_title"):
        data["video_title"] = seed["seed_title"]

    if not data.get("search_keyword"):
        data["search_keyword"] = _extract_search_keyword_fallback(
            data["video_title"], seed.get("seed_title", "")
        )
    data["search_keyword"] = _sanitize_search_keyword(data["search_keyword"])

    # Truncados
    if len(data.get("angle", "")) > 240:
        data["angle"] = data["angle"][:237] + "..."
    if len(data.get("hook", "")) > 80:
        data["hook"] = data["hook"][:77] + "..."
    if len(data.get("video_title", "")) > 100:
        data["video_title"] = data["video_title"][:97] + "..."
    if len(data.get("search_keyword", "")) > 60:
        data["search_keyword"] = data["search_keyword"][:60].strip()

    # Validar virality_score: int 1-10
    try:
        vs = int(data.get("virality_score", 5))
        if vs < 1 or vs > 10:
            vs = 5
    except (ValueError, TypeError):
        vs = 5
    data["virality_score"] = vs

    rs_len = len(data.get("research_summary") or "")
    error_handler.log_success(
        PipelineStage.TOPIC_RESEARCHER,
        f"✓ [DEEP] {data['video_title']} · research_summary={rs_len} chars · "
        f"sources={len(data['sources'])} · facts={len(data['verified_facts'])}",
    )
    return data


# ═══════════════════════════════════════════════════════════════
#  RESEARCH SHORT (1 llamada simple — flujo viejo, no se toca)
# ═══════════════════════════════════════════════════════════════

@error_handler.retry(PipelineStage.TOPIC_RESEARCHER)
def _research_seed_simple(seed: dict, existing_titles: list[str]) -> dict:
    """
    Research simple para SHORT: 1 llamada Pro + grounding.
    Para SHORT el guion es corto, no necesita los 4 sub-pasos.
    """
    existing = ", ".join(existing_titles[-20:]) if existing_titles else "ninguno"

    prompt = f"""Eres un investigador para contenido viral en español.

TEMA: "{seed['seed_title']}"
NICHO: {seed.get('root_niche', 'general')}

Investigá con Google Search y devolvé UN objeto JSON con:

{{
  "video_title": "título refinado, ≤62 chars (apuntá a 6-10 palabras)",
  "search_keyword": "ENTIDAD PURA, máx 2-3 palabras, sin años ni artículos",
  "hook": "scroll-stopper ≤12 palabras",
  "mystery": "1 oración con el enigma central",
  "reveal": "1 oración con la teoría/respuesta",
  "angle": "2 oraciones con datos duros",
  "sources": ["3-5 fuentes textuales (autor/publicación/año)"],
  "verified_facts": ["4-6 datos duros verificables"],
  "virality_score": 7
}}

Evita títulos ya investigados: {existing}

RESPONDE SOLO CON EL JSON. Sin markdown."""

    response = gemini_client.models.generate_content(
        model=api.gemini_model_research,
        contents=prompt,
        config=types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearch())],
            temperature=0.7,
        ),
    )
    # Tracking de costo por tokens (HANDOFF_133) — Pro + google_search (research seed simple).
    cost_tracker.track_gemini_response(response, api.gemini_model_research, "research_seed_simple")

    raw = ""
    for part in (response.candidates[0].content.parts or []):
        if getattr(part, "text", None):
            raw += part.text

    text = raw.strip()
    if "```" in text:
        match = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)
        if match:
            text = match.group(1).strip()

    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError(f"No JSON en respuesta: {text[:200]}")

    json_str = text[start:end + 1]
    json_str = re.sub(r"\s+", " ", json_str)
    data = json.loads(json_str)

    # Sanitización
    if not data.get("video_title"):
        data["video_title"] = seed["seed_title"]
    if not data.get("search_keyword"):
        data["search_keyword"] = _extract_search_keyword_fallback(
            data["video_title"], seed.get("seed_title", "")
        )
    data["search_keyword"] = _sanitize_search_keyword(data["search_keyword"])

    data.setdefault("mystery", "")
    data.setdefault("reveal", "")
    data.setdefault("angle", "")
    data.setdefault("research_summary", "")
    data.setdefault("canonical_subject_description", None)

    if not isinstance(data.get("sources"), list):
        data["sources"] = []
    if not isinstance(data.get("verified_facts"), list):
        data["verified_facts"] = []

    # Validar virality_score: int 1-10
    try:
        vs = int(data.get("virality_score", 5))
        if vs < 1 or vs > 10:
            vs = 5
    except (ValueError, TypeError):
        vs = 5
    data["virality_score"] = vs

    return data


# ═══════════════════════════════════════════════════════════════
#  PERSISTENCIA: SEEDS + TOPICS DB
# ═══════════════════════════════════════════════════════════════

def _load_seeds() -> list[dict]:
    if not SEEDS_FILE.exists():
        return []
    try:
        data = json.loads(SEEDS_FILE.read_text(encoding="utf-8"))
        return data.get("seeds", [])
    except Exception:
        return []


def _remove_seed_from_inbox(seed_id: str) -> bool:
    if not SEEDS_FILE.exists():
        return False
    try:
        payload = json.loads(SEEDS_FILE.read_text(encoding="utf-8"))
        seeds = payload.get("seeds", [])
        new_seeds = [s for s in seeds if s.get("seed_id") != seed_id]
        if len(new_seeds) == len(seeds):
            return False
        payload["seeds"] = new_seeds
        SEEDS_FILE.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return True
    except Exception:
        return False


def _flag_seed_in_inbox(seed_id: str, gate: dict) -> bool:
    """F7d: el seed cuyo pool dio ROJO se queda en el inbox con `pool_gate` (color, métricas, motivos, fecha): no se
    vuelve a investigar a ciegas y el motivo queda a la vista."""
    if not SEEDS_FILE.exists():
        return False
    try:
        payload = json.loads(SEEDS_FILE.read_text(encoding="utf-8"))
        for s in payload.get("seeds", []):
            if s.get("seed_id") == seed_id:
                s["pool_gate"] = {"color": gate["color"], "metricas": gate["metricas"], "motivos": gate["motivos"],
                                  "fecha": datetime.now().isoformat(timespec="seconds")}
                SEEDS_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
                return True
        return False
    except Exception:
        return False


def _archive_seed(seed: dict, topic_id: str) -> bool:
    try:
        archive: dict = {"archived": []}
        if SEEDS_ARCHIVE_FILE.exists():
            try:
                loaded = json.loads(SEEDS_ARCHIVE_FILE.read_text(encoding="utf-8"))
                if isinstance(loaded, dict):
                    archive = loaded
                    if not isinstance(archive.get("archived"), list):
                        archive["archived"] = []
            except Exception:
                pass

        entry = {
            "seed_id": seed.get("seed_id", ""),
            "seed_title": seed.get("seed_title", ""),
            "discovery_mode": seed.get("discovery_mode", ""),
            "root_niche": seed.get("root_niche"),
            "topic_id": topic_id,
            "archived_at": datetime.now().isoformat(),
            "original_seed": seed,
        }
        archive["archived"].append(entry)

        DATA_DIR.mkdir(parents=True, exist_ok=True)
        SEEDS_ARCHIVE_FILE.write_text(
            json.dumps(archive, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return True
    except Exception:
        return False


def _load_topics_db() -> dict:
    if TOPICS_DB_FILE.exists():
        try:
            db = json.loads(TOPICS_DB_FILE.read_text(encoding="utf-8"))
            if isinstance(db, dict):
                db.setdefault("topics", [])
                db.setdefault("created_at", datetime.now().isoformat())
                return db
            # si quedó como lista (formato viejo), envolver
            if isinstance(db, list):
                return {"created_at": datetime.now().isoformat(), "topics": db}
        except Exception:
            pass
    return {"created_at": datetime.now().isoformat(), "topics": []}


def _save_topics_db(db: dict) -> None:
    TOPICS_DB_FILE.write_text(
        json.dumps(db, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def _get_existing_titles(db: dict) -> list[str]:
    return [t["video_title"] for t in db.get("topics", []) if t.get("video_title")]


def _get_existing_seed_ids(db: dict) -> set[str]:
    return {t.get("seed_id") for t in db.get("topics", []) if t.get("seed_id")}


# ═══════════════════════════════════════════════════════════════
#  ENRIQUECIMIENTO CON METADATA DEL SEED
# ═══════════════════════════════════════════════════════════════

def _enrich_with_seed_metadata(topic_data: dict, seed: dict, video_type: str | None = None) -> dict:
    """Agrega trazabilidad del seed original al topic final. F41 §A.2: con `video_type`, el topic lo guarda (el tipo
    pedido al research; antes solo lo ponía el validador y los topics de `investigar_semilla` quedaban en None)."""
    # Si el deep ya pre-generó topic_id, lo reusamos para no romper persistencia
    topic_id = topic_data.pop("_pre_topic_id", None) or str(uuid.uuid4())

    return {
        "id": topic_id,
        "seed_id": seed["seed_id"],
        "discovery_mode": seed["discovery_mode"],
        "root_niche": seed.get("root_niche"),
        "tags": seed.get("tags", []),
        "evidence_from_discovery": seed.get("evidence", {}),
        "judge": seed.get("judge"),   # veredicto del juez pre-grounding (None si no aplica)
        "video_title": topic_data["video_title"],
        "search_keyword": topic_data.get("search_keyword", ""),
        "hook": topic_data.get("hook", ""),
        "mystery": topic_data.get("mystery", ""),
        "reveal": topic_data.get("reveal", ""),
        "angle": topic_data.get("angle", ""),
        "canonical_subject_description": topic_data.get("canonical_subject_description"),
        "research_summary": topic_data.get("research_summary", ""),
        "sources": topic_data.get("sources", []),
        "verified_facts": topic_data.get("verified_facts", []),
        "virality_score": topic_data.get("virality_score", 5),
        # F10: el pool de research v3 viaja al topic (antes se perdía acá y el guion v3 no corría sin carga a mano)
        **({"evidence_pool": topic_data["evidence_pool"]} if topic_data.get("evidence_pool") else {}),
        **({"research_version": topic_data["research_version"]} if topic_data.get("research_version") else {}),
        **({"video_type": video_type} if video_type else {}),
        "status": "researched",
        "competition_level": None,
        "market_verdict": None,
        "competition_data": None,
        "created_at": datetime.now().isoformat(),
    }


# ═══════════════════════════════════════════════════════════════
#  FUNCIÓN PÚBLICA — investigar_semilla (F39 §A.3: una semilla en un topic dado)
# ═══════════════════════════════════════════════════════════════

def _topic_registrado(db: dict, topic_id: str) -> bool:
    return any(t.get("id") == topic_id for t in db.get("topics", []))


def investigar_semilla(seed: dict, topic_id: str) -> dict:
    """F39 §A.3: investiga UNA semilla en el topic `topic_id` y la registra en topics_db.

    La misma cadena que `research_topics(video_type="long")`: `_research_seed_deep` (research v3 `run_seed` en
    `STEPS_DIR / topic_id` + sub-pasos 4a–4d) + `_enrich_with_seed_metadata`, pero:
      - el topic queda con `id == topic_id` (no uuid4) y guarda `seed_title` (el título de la ficha, como F23/F24);
      - sin el filtro de semillas ya investigadas;
      - no toca el inbox (`selected_seeds.json`) ni el archivo de semillas (`seeds_archive.json`);
      - F41 §A.2: guarda `video_type: "long"` (es la cadena long; ningún llamador pide otro tipo).
    `topic_id` ya en topics_db → ValueError antes de gastar (y de nuevo al registrar: no pisa).
    Compuerta del pool en rojo → `PoolGateRed` se propaga (no se registra nada).
    Devuelve el topic tal como quedó guardado."""
    if not topic_id:
        raise ValueError("investigar_semilla necesita un topic_id")
    faltan = [k for k in ("seed_id", "seed_title", "discovery_mode") if k not in seed]   # los pide _enrich_…, al final
    if faltan:
        raise ValueError(f"la semilla no tiene {', '.join(faltan)}: no se investiga")
    if _topic_registrado(_load_topics_db(), topic_id):
        raise ValueError(f"{topic_id} ya está en topics_db: no se pisa")
    print(f"\n  🔬 Investigando la semilla «{seed['seed_title']}» en el topic {topic_id} (LONG)...")
    topic_data = _research_seed_deep(seed, _get_existing_titles(_load_topics_db()), topic_id=topic_id)
    topic = {**_enrich_with_seed_metadata(topic_data, seed, video_type="long"), "seed_title": seed["seed_title"]}
    db = _load_topics_db()                      # releído: el research tarda minutos
    if _topic_registrado(db, topic_id):
        raise ValueError(f"{topic_id} apareció en topics_db durante el research: no se pisa")
    db["topics"].append(topic)
    _save_topics_db(db)
    print(f"     ✓ {topic_id} registrado · título: {topic['video_title']} · "
          f"fuentes: {len(topic.get('sources', []))} · datos: {len(topic.get('verified_facts', []))}")
    return topic


# ═══════════════════════════════════════════════════════════════
#  FUNCIÓN PÚBLICA — research_topics (firma intacta)
# ═══════════════════════════════════════════════════════════════

class Investigados(list):
    """F42b: la lista de topics investigados, más `fallas`: las semillas cuyo research tiró un error (cada una con
    seed_id, seed_title y el error). La compuerta del pool (`PoolGateRed`) no es una falla: devuelve la semilla."""

    def __init__(self, *a):
        super().__init__(*a)
        self.fallas: list[dict] = []


def research_topics(
    seeds: list[dict] | None = None,
    video_type: str = "short",
) -> Investigados:
    """
    Investiga seeds y guarda topics en topics_db.

    Args:
        seeds: lista de seeds. Si None, carga de selected_seeds.json.
        video_type: "short" (1 llamada Pro) | "long" (4 angle queries en paralelo + 4 sub-pasos Flash)

    Returns:
        Lista de topics investigados; en `.fallas`, las semillas que fallaron con su error (siguen en la bandeja).
    """
    if video_type not in ("short", "long"):
        raise ValueError(f"video_type debe ser 'short' o 'long', no '{video_type}'")

    if seeds is None:
        seeds = _load_seeds()

    if not seeds:
        print("\n  ⚠ No hay seeds para investigar.")
        return Investigados()

    db = _load_topics_db()
    existing_seed_ids = _get_existing_seed_ids(db)
    existing_titles = _get_existing_titles(db)

    # Filtrar seeds ya procesados
    pending = [s for s in seeds if s["seed_id"] not in existing_seed_ids]
    if not pending:
        print("\n  ✓ Todos los seeds ya estaban investigados.")
        return Investigados()

    print(f"\n  🔬 Investigando {len(pending)} seed(s) en modo {video_type.upper()}...")
    if video_type == "long":
        print(f"     (4 angle queries Pro en paralelo + 4 sub-pasos Flash por seed)")

    researched = Investigados()

    for i, seed in enumerate(pending):
        print(f"\n  [{i+1}/{len(pending)}] {seed['seed_title']}")

        if i > 0:
            time.sleep(DELAY_BETWEEN_CALLS_SEC)

        try:
            if video_type == "long":
                topic_data = _research_seed_deep(seed, existing_titles)
            else:
                topic_data = _research_seed_simple(seed, existing_titles)
        except Exception as e:
            from researcher_steps.pool_gate import PoolGateRed
            if isinstance(e, PoolGateRed):              # F7d: el seed se queda en el inbox, con el motivo
                _flag_seed_in_inbox(seed["seed_id"], e.gate)
                print(f"     🔴 Compuerta del pool: {'; '.join(e.gate['motivos'])} → vuelve al inbox")
                continue
            error_handler.log_error(
                PipelineStage.TOPIC_RESEARCHER, e,
                context={"seed_title": seed.get("seed_title", "?")}
            )
            # F42b: la falla no se traga: vuelve a quien llamó (la semilla sigue en la bandeja)
            researched.fallas.append({"seed_id": seed.get("seed_id"), "seed_title": seed.get("seed_title", "?"),
                                      "error": f"{type(e).__name__}: {e}"})
            print(f"     ❌ Falló: {type(e).__name__}: {e} — la semilla sigue en la bandeja")
            continue

        topic = _enrich_with_seed_metadata(topic_data, seed, video_type=video_type)   # F41 §A.2: el tipo pedido
        db["topics"].append(topic)
        researched.append(topic)
        existing_titles.append(topic["video_title"])

        # Persistir DB incremental (resistente a crashes)
        _save_topics_db(db)
        _archive_seed(seed, topic_id=topic["id"])
        _remove_seed_from_inbox(seed["seed_id"])

        print(f"     ✓ Título: {topic['video_title']}")
        if topic.get("hook"):
            print(f"     🪝 Hook:  {topic['hook'][:70]}")
        print(f"     📎 Fuentes: {len(topic.get('sources', []))}  ·  "
              f"Datos: {len(topic.get('verified_facts', []))}")
        if video_type == "long":
            rs_len = len(topic.get("research_summary") or "")
            print(f"     📜 research_summary: {rs_len} chars")

    _save_topics_db(db)

    print(f"\n{'─' * 60}")
    print(f"  ✅ {len(researched)} topic(s) investigado(s)")

    by_mode: dict = {}
    for t in researched:
        by_mode.setdefault(t["discovery_mode"], 0)
        by_mode[t["discovery_mode"]] += 1
    for mode, count in by_mode.items():
        print(f"     - {mode}: {count}")

    if researched.fallas:
        print(f"  ❌ {len(researched.fallas)} semilla(s) fallaron (siguen en la bandeja)")

    remaining_seeds = _load_seeds()
    print(f"\n  📥 Bandeja: {len(remaining_seeds)} seed(s) pendiente(s)")
    if not researched.fallas:
        print(f"\n  ➡  Siguiente paso: topic_validator\n")

    return researched


# ═══════════════════════════════════════════════════════════════
#  CLI DIRECTO
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # F26 §C: `--workers N` = hilos de R2/R3 del research v3 (por defecto research_v3.WORKERS = 8; 1 = en fila)
    import sys
    if "--workers" in sys.argv:
        _k = sys.argv.index("--workers")
        from researcher_steps import research_v3 as _rv3
        _rv3.WORKERS = int(sys.argv[_k + 1])
        del sys.argv[_k:_k + 2]
    research_topics()
