"""
script_engine/m03_visual.py — Módulo 03: extractor visual.

TAREA ÚNICA: a partir de topic + skeleton (01a) + narración (01b) + profiles (02),
generar los `image_prompts[]` en INGLÉS con `narration_anchor` explícito por imagen.
Reemplaza `_generate_image_prompts_for_long_chapter` del pipeline viejo.

CONCEPTO CLAVE — `narration_anchor`:
  Cada imagen lleva pegada un substring EXACTO de la narración del cap. Esto:
    1. Define qué frase concreta ilustra la imagen (ata semánticamente).
    2. Define el orden cronológico de las imágenes en el array.
    3. Permite a fase2b sincronizar imagen↔audio por palabra (timestamps reales
       del sync_map de ElevenLabs).
  Cierra el bug viejo de "imagen no concuerda con narración" (ej: barco en pantalla
  cuando se habla de una persona).

APPROACH 2-ZONA (chat 14, cierra bug `profile_incoherence` de raíz):
  El LLM emite SOLO zona 1 (Subject + Action + Environment, con marcador
  temporal). Después del LLM, Python concatena zona 2 (lighting/palette/
  optics/grain desde ART_PROFILES, y para Veo video_prompt el motion
  universal del profile desde VEO_MOTION).
    zona 1 (LLM)   : "An elderly miner in 1960s clothes on outback road, ..."
    zona 2 (Python): + "Cinematic desert expedition photography, scorched
                       ochre and burnt sienna palette, ..."
  Make illegal states unrepresentable: si la paleta no la decide el LLM,
  el LLM no puede equivocarse en ella. El validador `_validate_zone1_clean`
  rechaza si el LLM mete términos de zona 2 en su output (lighting/palette/
  style/optics) y dispara retry-with-feedback explicando qué encontró.

INPUT:
  topic     — dict (topics_db.json post módulo 00)
  skeleton  — dict {topic_id, chapters[7]} (output 01a, sin _distribution_plan)
  narration — dict {topic_id, chapters[7] con narration} (output 01b)
  profiles  — dict {topic_id, chapters[7] con art_profile} (output 02)

OUTPUT:
  {
    "topic_id": "uuid",
    "chapters": [
      // Cap 1 y 7 (veo) — prompts ya stitcheados con ART_PROFILES + VEO_MOTION:
      {
        "chapter_number": 1,
        "image_prompt": "string EN, zona 1 + ART_PROFILES suffix",
        "video_prompt": "string EN, zona 1 + ART_PROFILES + VEO_MOTION suffix",
        "subject_ref": "main_subject",
        "narration_anchor": "substring EXACTO de la narración del cap"
      },
      // Cap 2-6 (flux) — cada prompt stitcheado con su ART_PROFILES:
      {
        "chapter_number": 2,
        "image_prompts": [
          {
            "prompt": "string EN, zona 1 + ART_PROFILES suffix",
            "art_profile": "INDUSTRIAL",
            "subject_ref": "main_subject",
            "emotional_rank": "R1" | "R2" | "R3",
            "narration_anchor": "substring EXACTO de la narración del cap"
          },
          ... (N items, N = clamp(round(chars/200), 7, 10))
        ]
      },
      ...
    ]
  }

ESTRUCTURA INTERNA (1 archivo, ~14 funciones privadas + 1 pública):
  _calculate_image_count(narration_text, chapter_number, total_chapters)  → int
                                                  (fórmula chars/150 + bonus pos + bonus long)
  _format_facts(verified_facts)                 → str
  _format_profiles_guide()                      → str (PROFILE_GUIDE legible)
  _build_topic_block(topic)                     → str (header común)
  _build_rules_block(default_profile)           → str (reglas inviolables)
  _build_veo_prompt(topic, cap_data, profile,
                    narration_text)             → str
  _build_flux_prompt(topic, cap_data, profile,
                     narration_text, n_images)  → str
  _validate_prompt_length_zona1(prompt, label)  → None | raise
  _validate_no_text_leakage(prompt, label)      → None | raise
  _validate_zone1_clean(prompt, label)          → None | raise (regla 2)
  _validate_profile_palette_coherence(...)      → None | raise (regla 15)
  _validate_veo_cap(parsed, narration, n)       → dict zona1 (raise si falla)
  _validate_flux_cap(parsed, narration, n,
                     n_expected)                → dict zona1 (raise si falla)
  _stitch_zone2_into_cap_veo(cap_out, profile)  → dict (zona1+zona2)
  _stitch_zone2_into_cap_flux(cap_out)          → dict (zona1+zona2 por item)
  _call_with_validation_retry(prompt, validator,
                               cap_n, ...)      → dict
  _persist(topic_id, data)                      → escribe 03_visual.json
  assign_visual_prompts(topic, skel,
                        narr, profiles)         → dict       # PÚBLICA

LLAMADAS GEMINI: 7 (Flash, 1 por cap, secuencial). ~$0.010/video.

VALIDACIÓN DURA POST-FLASH (caps flux):
  1. len(image_prompts) == N exacto (fórmula chars/200, clamp 7-10).
  2. Cada item tiene los 5 campos.
  3. art_profile ∈ VALID_PROFILES.
  4. emotional_rank ∈ {R1, R2, R3}.
  5. prompt en rango zona 1: 80-240 chars.
  6. zona 1 limpia (sin lighting/palette/style — regla 2).
  7. narration_anchor es substring EXACTO de la narración del cap.
  8. anchors en orden estrictamente creciente.
  9. anchors sin solapamiento.

VALIDACIÓN DURA POST-FLASH (caps veo):
  1. Existen image_prompt, video_prompt, subject_ref, narration_anchor.
  2. image_prompt y video_prompt en rango zona 1: 80-240 chars.
  3. zona 1 limpia (sin lighting/palette/style — regla 2).
  4. narration_anchor es substring EXACTO de la narración del cap.

RETRY:
  Hasta 2 reintentos por cap si la validación falla. Feedback con mensaje
  específico del error. Después del 2do retry: VisualValidationError.
"""

import json
import re
from difflib import SequenceMatcher
from pathlib import Path

from config import DATA_DIR
from gemini_helpers import call_flash_json
from art_profiles import (
    ART_PROFILES,
    PROFILE_GUIDE,
    VALID_PROFILES,
    VEO_MOTION,
    stitch_prompt,
    stitch_veo_video_prompt,
)


# ═══════════════════════════════════════════════════════════════
#  PATHS Y CONSTANTES
# ═══════════════════════════════════════════════════════════════

STEPS_DIR: Path = DATA_DIR / "scripts" / "_steps"

EXPECTED_CHAPTER_COUNT = 7
VEO_CHAPTERS = (1, 7)
FLUX_CHAPTERS = (2, 3, 4, 5, 6)

# 150 chars de narración española post-TTS ≈ 11.5s con pausas de ElevenLabs.
# Estimación conservadora: el TTS infla ~10% la duración respecto a chars puros.
# Clamp [6, 14]: techo más generoso que antes (10) para caps largos densos.
CHARS_PER_IMAGE = 150
MIN_IMAGES_FLUX = 6
MAX_IMAGES_FLUX = 12

# Bonus por posición narrativa del cap (development only).
# Caps en first_third (problema/intro) y last_third (clímax) reciben +1 img
# para densificar momentos de mayor peso emocional.
BONUS_POSITION_FIRST_THIRD = 1
BONUS_POSITION_LAST_THIRD = 1
BONUS_POSITION_MIDDLE = 0

# Bonus por densidad de narración. Caps con narración muy larga tienden a
# tener más subtramas que requieren imágenes adicionales.
BONUS_LONG_NARRATION_THRESHOLD = 1800   # chars
BONUS_LONG_NARRATION_VALUE = 2

# Rango de chars para los prompts EN.
# <150: pierde detalle visual. >320: Flux/Veo ignoran tokens finales.
# Techo subido a 320 (de 300) post-ajuste 4e: los prompts ahora cargan
# era + marcador temporal + appearance_canon + escena en una sola pieza,
# y 300 quedó justo. 320 mantiene a Flux dentro de su ventana de atención
# útil (~400 chars) y le da margen al modelo para no sacrificar el anclaje.
PROMPT_MIN_CHARS = 150
PROMPT_MAX_CHARS = 320

# Rango de chars para zona 1 (lo que el LLM emite SIN lighting/palette/style).
# Después del LLM, Python concatena ART_PROFILES[profile] (~250 chars) y para
# Veo video_prompt además VEO_MOTION[profile] (~200 chars). El output final
# tras el stitching cae en ~370-490 chars (Flux + Veo image_prompt) y
# ~570-690 chars (Veo video_prompt) — Flux/Veo ignoran tokens más allá de
# ~400, por eso zona 1 va al inicio (subject pondera más) y zona 2 detrás.
#
# Max subido a 240 (chat 14, post primer live test): 200 era muy ajustado.
# El LLM, instruido a meter subject + action + environment + marcador
# temporal + framing en una frase rica, naturalmente apunta a 200-240 chars.
# 240 deja margen sin permitir contrabando de zona 2 (las descripciones de
# lighting/palette suelen sumar 80-120 chars cuando el LLM las mete).
PROMPT_MIN_CHARS_ZONA1 = 80
PROMPT_MAX_CHARS_ZONA1 = 260

VALID_RANKS = frozenset({"R1", "R2", "R3"})

MAX_RETRY_ATTEMPTS = 3
# 1 intento original + 2 retries con feedback enriquecido. Cap más cargado
# (10 imgs sobre narr ~2000 chars) puede necesitar la 3ra vuelta cuando
# falla por anchor parafraseado en la última img. Costo: ~$0.001 extra
# en peor caso. Comportamiento normal sigue siendo 0-1 retries.

# ─── Validación regla 14 (anti-text-leakage) ───
# Patrones que indican intent de renderizar texto en la imagen, incluso si
# el LLM intenta camuflarlos con "blurred", "faded", "indistinct" etc.
TEXT_LEAKAGE_PATTERNS = (
    # Frases tipo "where X name/text/label was/once was"
    r"\bwhere\s+(?:the\s+|a\s+|an\s+)?(?:name|text|label|word|words|inscription|title|sign)\s+(?:was|once was|used to be|had been)\b",
    r"\bwhere\s+(?:a\s+|the\s+)?town\s+name\b",
    # "blurred/faded/indistinct + area + name/text"
    r"\b(?:blurred|faded|indistinct|obscured)\s+(?:area|patch|spot|region)\s+(?:where|with|of|showing)\s+(?:name|text|word|label)\b",
    # Construcciones con comillas que el LLM mete como nombre literal
    r"['\"][A-Z][a-zA-Z]{3,}['\"]",  # texto entre comillas con palabra capitalizada
    # "the name/word X" cuando X es algo que el LLM va a dibujar
    r"\bthe\s+(?:name|word|label|inscription)\s+['\"][^'\"]+['\"]",
    # "showing the X name/text" donde X es ubicación o entidad
    r"\bshowing\s+the\s+\w+\s+(?:name|text|label|title)\b",
)

# ─── Validación regla 15 (paleta coherente con profile) ───
# Para cada profile, palabras prohibidas en el prompt si ese profile es
# image_art_profile. La intersección entre profile e palette-words es lo
# que detectamos.
PROFILE_FORBIDDEN_PALETTE_WORDS = {
    "INDUSTRIAL": (
        "amber", "golden", "ochre", "sepia", "warm sunlight",
        "scorched", "harsh sun", "afternoon sun", "sunset glow",
        "warm afternoon", "warm light", "amber light", "golden hour",
    ),
    "INTERIOR": (
        "sterile", "clinical", "antiseptic", "operating room",
        "cold blue light", "harsh fluorescent",
    ),
    "WILDERNESS": (
        "arid", "desert", "scorched", "ochre", "drought",
        "outback", "dust haze", "red rock",
    ),
    "DESERT": (
        "overcast", "rainy", "wet", "lush", "verdant",
        "tropical", "jungle", "snow", "frost",
    ),
    "POLAR": (
        "warm", "amber", "tropical", "lush", "green canopy",
        "desert", "ochre", "sand",
    ),
    "JUNGLE": (
        "arid", "desert", "dust", "snow", "polar",
        "frozen", "outback", "bare",
    ),
    "SUBMARINE": (
        "sunlight", "daylight", "sun-drenched", "bright noon",
        "amber sun", "golden hour",
    ),
    "MARITIME_EXTERIOR": (
        "interior", "indoor", "underground", "cave",
    ),
    "UNDERGROUND": (
        "open sky", "horizon", "sun", "outdoor", "exterior daylight",
        "ocean", "sea",
    ),
    "URBAN": (
        "wilderness", "rural", "outback", "desert sand",
        "jungle", "tropical",
    ),
    "AERIAL": (
        "ground level", "interior", "indoor", "underground",
    ),
    "HISTORICAL": (
        "modern", "contemporary", "21st century", "smartphone",
        "computer", "neon", "led",
    ),
    "SPACE": (
        "atmosphere", "blue sky", "clouds", "ocean", "vegetation",
        "trees", "grass", "rain",
    ),
}


# ─── Validación zona 1 (approach 2-zona, chat 14) ───
# El LLM hoy escribe Subject+Action+Environment+Lighting+Style. El approach
# 2-zona separa: el LLM escribe SOLO Subject+Action+Environment (zona 1) y
# Python concatena lighting/palette/optics/grain desde ART_PROFILES (zona 2).
# Estas listas detectan si el LLM mete zona 2 en su output y dispara retry.
# Las listas viven duplicadas en la regla 2 del prompt para que el LLM las
# vea explícitamente — si cambian acá, actualizar también la regla 2 en
# _build_rules_block().

ZONA1_FORBIDDEN_LIGHTING = (
    "golden hour", "warm light", "cold light", "harsh sun",
    "soft daylight", "dim lighting", "moody lighting",
    "atmospheric lighting", "dramatic lighting", "backlit",
    "rim light", "hard shadows", "deep shadows", "soft shadows",
)

ZONA1_FORBIDDEN_PALETTE = (
    "amber", "ochre", "sepia", "cyan", "teal",
    "slate-blue", "ash-grey", "warm tones", "cold tones",
    "muted palette", "saturated", "desaturated",
    "warm air", "cold air",
)

ZONA1_FORBIDDEN_STYLE = (
    "cinematic", "establishing shot", "anamorphic",
    "35mm", "16mm", "65mm", "70mm", "film grain", "fine grain",
    "shallow depth of field", "bokeh", "lens flare",
    "chromatic aberration", "vintage optics", "documentary aesthetic",
)

# Hints de reemplazo para términos prohibidos que tienen un equivalente
# conceptual válido en zona 1. El validador `_validate_zone1_clean` los
# inserta en el feedback de error para guiar al LLM en el retry. Solo
# entran términos donde existe un "qué escribir en su lugar" claro;
# para el resto, el feedback genérico "borralo, lo agrega el código" basta.
ZONA1_REPLACEMENT_HINTS: dict[str, str] = {
    # Style/camera: el "establishing shot" cinematográfico equivale a un
    # wide shot funcional (framing) — el resto del flavor lo agrega el profile.
    "establishing shot": "wide shot",
}


# ═══════════════════════════════════════════════════════════════
#  EXCEPCIÓN
# ═══════════════════════════════════════════════════════════════

class VisualValidationError(ValueError):
    """Output del Flash no cumple el contrato del módulo 03."""


# ═══════════════════════════════════════════════════════════════
#  CÁLCULO DE N (cantidad de imgs por cap flux)
# ═══════════════════════════════════════════════════════════════

def _calculate_image_count(
    narration_text: str,
    chapter_number: int = None,
    total_chapters: int = 7,
) -> int:
    """
    Cantidad adaptativa de imgs por cap según:
      - longitud de narración (base, divisor CHARS_PER_IMAGE)
      - posición narrativa (first_third / middle / last_third)
      - bonus si narración > BONUS_LONG_NARRATION_THRESHOLD chars

    Args:
        narration_text: el texto de la narración del cap.
        chapter_number: número del cap (1..total_chapters). Si None, no aplica
            bonus de posición.
        total_chapters: típicamente 7 (1 hook + 5 development + 1 outro).

    Returns:
        n_images: int en rango [MIN_IMAGES_FLUX, MAX_IMAGES_FLUX].

    Posición se calcula sobre los caps DEVELOPMENT (excluyendo hook+outro):
      - development_index = chapter_number - 2  (cap 2 → 0, cap 6 → 4)
      - n_dev = total_chapters - 2  (típicamente 5)
      - first_third: development_index < n_dev/3
      - last_third: development_index >= 2*n_dev/3
      - middle: en medio
    """
    base = round(len(narration_text) / CHARS_PER_IMAGE)

    # Bonus por posición (solo si tenemos chapter_number y es development)
    bonus_position = 0
    if chapter_number is not None and 2 <= chapter_number <= total_chapters - 1:
        development_index = chapter_number - 2
        n_dev = total_chapters - 2  # 5 si total=7
        if n_dev > 0:
            third = n_dev / 3.0
            if development_index < third:
                bonus_position = BONUS_POSITION_FIRST_THIRD
            elif development_index >= 2 * third:
                bonus_position = BONUS_POSITION_LAST_THIRD
            else:
                bonus_position = BONUS_POSITION_MIDDLE

    # Bonus por narración larga
    bonus_long = (
        BONUS_LONG_NARRATION_VALUE
        if len(narration_text) > BONUS_LONG_NARRATION_THRESHOLD
        else 0
    )

    n = base + bonus_position + bonus_long
    return max(MIN_IMAGES_FLUX, min(MAX_IMAGES_FLUX, n))


# ═══════════════════════════════════════════════════════════════
#  FORMAT HELPERS (texto del prompt)
# ═══════════════════════════════════════════════════════════════

def _format_facts(verified_facts: list) -> str:
    """Enumera verified_facts numerados [F##]. Mismo formato que 01a/01b/02."""
    if not verified_facts:
        return "(sin facts)"
    lines = []
    for i, f in enumerate(verified_facts, start=1):
        if isinstance(f, dict):
            text = (f.get("fact") or "").strip()
            block = (f.get("source_block") or "").strip()
            tag = f" [{block}]" if block else ""
            lines.append(f"  [F{i:02d}] {text}{tag}")
        elif isinstance(f, str):
            lines.append(f"  [F{i:02d}] {f.strip()}")
    return "\n".join(lines)


def _format_profiles_guide() -> str:
    """Catálogo de 13 profiles legible (importado desde m02)."""
    lines = []
    for name in sorted(PROFILE_GUIDE.keys()):
        lines.append(f"  • {name}")
        lines.append(f"      {PROFILE_GUIDE[name]}")
    return "\n".join(lines)


def _format_profiles_aesthetics() -> str:
    """Aesthetic descriptions completas de cada profile (importado de art_profiles).

    Complementa _format_profiles_guide() — mientras esa dice CUÁNDO usar cada
    profile (selección), esta dice QUÉ SE VE concretamente cada profile (paleta,
    óptica, grain). El LLM necesita ambas para hacer override informado.

    Sin este bloque, el LLM solo ve la etiqueta del profile y no respeta su
    aesthetic — bug detectado por m05 en Wittenoom (cap 6, 9 issues
    profile_incoherence).
    """
    lines = []
    for name in sorted(ART_PROFILES.keys()):
        lines.append(f"  • {name}:")
        lines.append(f"      {ART_PROFILES[name]}")
    return "\n".join(lines)


def _format_bullets(bullets: list) -> str:
    if not bullets:
        return "      (sin bullets)"
    return "\n".join(f"      - {b}" for b in bullets)


def _format_visual_canon_block(topic: dict) -> str:
    """Bloque DATOS VISUALES CANÓNICOS — verdad sellada del topic (4e).

    Lee era_visual_canon, documented_people y anachronism_blocklist del
    topic (poblados por step_4e_visual_canon en el módulo 00). Si los
    campos vienen vacíos (topic viejo no migrado, o Flash falló en el 4e),
    el bloque emite una nota de fallback que le dice al modelo que derive
    de verified_facts y canonical, manteniendo las reglas 4/5/11 inviolables.

    Returns:
        str: bloque listo para inyectar entre topic_block y rules_block.
    """
    era = topic.get("era_visual_canon") or {}
    people = topic.get("documented_people") or []
    blocklist = topic.get("anachronism_blocklist") or []

    has_era = bool(era.get("primary_decade"))
    has_people = bool(people)
    has_blocklist = bool(blocklist)

    # ─── ERA VISUAL ───
    if has_era:
        era_lines = [
            f"  primary_decade        : {era.get('primary_decade', '')}",
            f"  spans                 : {era.get('spans', '')}",
            f"  clothing              : {era.get('clothing', '')}",
            f"  technology            : {era.get('technology', '')}",
            f"  vehicles_machinery    : {era.get('vehicles_machinery', '')}",
            f"  interiors             : {era.get('interiors', '')}",
            f"  forbidden_anachronisms: {era.get('forbidden_anachronisms', '')}",
        ]
        era_block = "ERA VISUAL (cómo se ve el mundo del tema):\n" + "\n".join(era_lines)
    else:
        era_block = (
            "ERA VISUAL: (vacío — no disponible en este topic)\n"
            "  Inferí la era de verified_facts y canonical_subject_description."
        )

    # ─── PERSONAS DOCUMENTADAS ───
    if has_people:
        people_lines = ["PERSONAS DOCUMENTADAS (usar appearance_canon, NUNCA el nombre):"]
        for p in people:
            role = p.get("role", "?")
            age = p.get("age_at_event")
            era_p = p.get("era", "?")
            appearance = p.get("appearance_canon", "")
            age_str = f"age {age}" if age is not None else "age unknown"
            people_lines.append(f"  • role: {role}  |  {age_str}  |  era: {era_p}")
            people_lines.append(f"    appearance_canon: {appearance}")
        people_block = "\n".join(people_lines)
    else:
        people_block = (
            "PERSONAS DOCUMENTADAS: (vacío — no hay lista canónica)\n"
            "  Si la narración menciona a alguien por nombre, describilo por\n"
            "  rol+aspecto+era genérico (NUNCA por nombre — ver regla 5)."
        )

    # ─── BLOCKLIST DE ANACRONISMOS ───
    if has_blocklist:
        blocklist_lines = ["ANACRONISMOS PROHIBIDOS (jamás aparecen en los prompts):"]
        for item in blocklist:
            blocklist_lines.append(f"  - {item}")
        blocklist_block = "\n".join(blocklist_lines)
    else:
        blocklist_block = (
            "ANACRONISMOS PROHIBIDOS: (vacío — sin lista específica)\n"
            "  Las reglas 4 y 11 + el negative prompt de Flux son la defensa."
        )

    # ─── NOTA DE USO ───
    usage_note = (
        "USO: Estos datos son VERDAD SELLADA del topic. NO los re-inferir.\n"
        "Reutilizá clothing/technology/vehicles_machinery/interiors textualmente\n"
        "en los prompts cuando aporten anclaje visual. Reutilizá appearance_canon\n"
        "de PERSONAS DOCUMENTADAS sin modificar para personajes mencionados.\n"
        "Si algún campo viene vacío, las reglas 4, 5 y 11 siguen siendo inviolables."
    )

    return f"""{era_block}

{people_block}

{blocklist_block}

{usage_note}"""


# ═══════════════════════════════════════════════════════════════
#  CONSTRUCCIÓN DE BLOQUES COMPARTIDOS DEL PROMPT
# ═══════════════════════════════════════════════════════════════

def _build_topic_block(topic: dict) -> str:
    """Header común: título, geo, era, facts, canonical, summary."""
    title = topic.get("video_title") or "(sin título)"
    geo = topic.get("canonical_geo") or "(sin geo)"
    era = topic.get("canonical_era") or "(sin era)"
    canonical = topic.get("canonical_subject_description") or "(sin canonical)"
    summary = topic.get("research_summary") or "(sin summary)"
    facts_block = _format_facts(topic.get("verified_facts") or [])

    return f"""Título  : {title}
GEO     : {geo}
ERA     : {era}

DATOS DUROS (verified_facts — única fuente válida para cifras/fechas/nombres):
{facts_block}

DESCRIPCIÓN CANÓNICA DEL SUJETO RECURRENTE:
{canonical}

CONTEXTO NARRATIVO (research_summary):
{summary}"""


def _build_rules_block() -> str:
    """Las 11 reglas inviolables que se repiten en ambos prompts."""
    return f"""1. **PROMPT EN INGLÉS.** Sin excepciones. Flux/Veo no entienden español.

2. **ESTRUCTURA OBLIGATORIA** (orden de tokens):
   Subject → Action → Environment. STOP.
   El sujeto al PRINCIPIO. Flux pondera tokens iniciales con más peso.

   ESCRIBÍ SOLO: qué hay (subject), qué pasa (action), dónde está
   (environment). El marcador temporal de la regla 11 (ej. "1960s",
   "vintage", "period-correct") SÍ va dentro del environment — eso NO
   es lighting ni style.

   PROHIBIDO en tu output (estos elementos los agrega el código DESPUÉS,
   sacados del art_profile elegido. Si los escribís vos, contradicen al
   profile y el output será rechazado por el validador runtime):

   - Lighting words: "golden hour", "warm light", "cold light",
     "harsh sun", "soft daylight", "dim lighting", "moody lighting",
     "atmospheric lighting", "dramatic lighting", "backlit", "rim light",
     "hard shadows", "deep shadows", "soft shadows".

   - Palette words: "amber", "ochre", "sepia", "cyan", "teal",
     "slate-blue", "ash-grey", "warm tones", "cold tones", "muted
     palette", "saturated", "desaturated", "warm air", "cold air".

   - Style/optics words: "cinematic", "establishing shot", "anamorphic",
     "35mm", "16mm", "65mm", "70mm", "film grain", "fine grain",
     "shallow depth of field", "bokeh", "lens flare", "chromatic
     aberration", "vintage optics", "documentary aesthetic".

   PERMITIDO en zona 1 (es framing, no estética):
   "wide shot", "medium shot", "close-up", "low angle", "high angle",
   "overhead view", "aerial view", "side view", "POV", "seen from
   above/below/behind".

   ✗ MAL: "An elderly miner in 1960s clothes on a deserted road,
           golden hour light cutting low, cinematic wide shot,
           cold steel-blue tones"
          (lighting + style + palette → todo rechazado)

   ✓ BIEN: "An elderly miner in 1960s clothes on a deserted road,
            distant period-correct mining headframe on the horizon,
            wide shot of the empty terrain around him"
           (subject + action + environment + framing permitido,
            con marcador temporal embebido)

3. **NO INVENTAR DATOS DE LUGAR/FECHA.** Cifras, fechas y lugares solo
   pueden venir de verified_facts [F##] o de la narración del cap.
   (Esta regla es para datos NO-PERSONAS. Para personas ver regla 5.)

4. **NO TEXTO/NÚMEROS/LETRAS VISIBLES EN LAS IMÁGENES.** Esto incluye:
   - signs, labels, stamps, headlines, banners
   - blueprints with annotations or callouts
   - screens displaying coordinates, data, or readable values
   - sonar/radar/computer screens with numerical readouts
   - paperwork, documents or memos with visible writing
   - gravestones with names, plaques with text
   - newspapers, books, posters with text

   Si la idea es un documento técnico → "stack of faded technical paperwork"
   SIN especificar texto. Si es una pantalla con datos → "vintage screen
   with abstract pings and glowing patterns" SIN números literales.

   ✗ MAL: "blueprint overlaid with a faded stamp showing legible letters/words"
          (cualquier palabra dentro del sello — el stamp NO debe contener texto)
   ✗ MAL: "sonar screen displaying coordinates with readable numbers"
          (cualquier número visible en pantalla)
   ✗ MAL: "newspaper headline with readable words/text"
          (cualquier texto del titular es prohibido)
   ✓ BIEN: "abstract technical blueprint with mechanical schematics, no readable marks"
   ✓ BIEN: "vintage sonar display with glowing pulses, no readable text"
   ✓ BIEN: "folded period newspaper, headline area blurred and indistinct"

   REGLA DE ORO: si tu prompt nombra cualquier sello/pantalla/papel/cartel,
   debe terminar con "no readable text" o un descriptor equivalente
   ("indistinct", "blurred", "abstract", "obscured"). NUNCA pongas la
   palabra que está dentro del sello/cartel/pantalla, ni siquiera entre
   comillas.

   AMPLIACIÓN CRÍTICA — fechas y nombres propios:

   El image generator también intenta renderizar como texto cualquier
   FECHA LITERAL o NOMBRE PROPIO ENTRE COMILLAS que aparezca en el prompt,
   aunque no esté describiendo un cartel. Esto produce números garabateados
   y palabras inventadas en la imagen final. Está PROHIBIDO incluir:

   a) Fechas literales en cualquier formato:
      - "April 26, 1986"
      - "1986-04-26"
      - "26/04/1986"
      - "the morning of April 26"
      Si necesitás establecer la era, usá descriptores temporales
      indirectos ("a 1980s Soviet plant", "early-spring industrial scene",
      "post-disaster era") sin la fecha exacta.

   b) Nombres propios entre comillas, paréntesis o como labels:
      - "Object 'Shelter'"
      - "the 'Refugio' sarcophagus"
      - "USS Scorpion"
      - "(former 'Wittenoom Steel')"
      Si necesitás referirte a la cosa, describila visualmente sin el
      nombre ("the massive concrete sarcophagus", "the steel-hulled
      submarine", "the abandoned mining facility").

   ✗ MAL: "...explosion at the April 26, 1986 Chernobyl plant..."
   ✗ MAL: "...construction of the Object 'Shelter' sarcophagus..."
   ✗ MAL: "...the original 'Refugio' barrier nearing completion..."
   ✗ MAL: "...USS Scorpion sinking into the Atlantic..."

   ✓ BIEN: "...explosion at a 1980s Soviet nuclear plant, debris scattering..."
   ✓ BIEN: "...construction of the massive concrete sarcophagus, scaffolding,
            1986 industrial equipment..."
   ✓ BIEN: "...the imposing weathered concrete shell encasing the ruined
            reactor..."
   ✓ BIEN: "...a steel-hulled American submarine descending into deep
            Atlantic waters..."

   La narración del usuario MENCIONA fechas y nombres porque son
   verificables y dan credibilidad documental. El prompt visual los
   TRADUCE a descripciones concretas sin reproducirlos como texto.

5. **PROHIBIDO ESCRIBIR NOMBRES PROPIOS DE PERSONAS** en `prompt` o
   `video_prompt`, INCLUSO si el nombre aparece en verified_facts o en
   la narración del cap.

   Para personas que figuran en el bloque "PERSONAS DOCUMENTADAS"
   (sección DATOS VISUALES CANÓNICOS arriba): usá DIRECTAMENTE su
   `appearance_canon` tal cual está escrito.

   Para personas no listadas: describí solo rol+aspecto+era genérico
   (ej. "a middle-aged American mining inspector in 1960s field attire").

   ✗ MAL: "Commander Francis Slattery on the bridge..."
   ✗ MAL: "Dr. Eric Saint examining a patient..."
   ✓ BIEN: "a mid-30s American naval officer in 1960s U.S. Navy service
            uniform, with an authoritative demeanor, on the control bridge"
            (usando appearance_canon de PERSONAS DOCUMENTADAS)

6. **NO METADATOS TÉCNICOS NI PARÁMETROS DE FORMATO.**
   Prohibido en tu output:
   - Cámaras / sensores: "shot with Sony A7", "Canon R5", "Hasselblad",
     "ARRI Alexa", "Red Komodo".
   - Specs ópticas: "f/2.8", "f/1.4", "ISO 400", "1/250 shutter".
   - Aspect ratios y formatos: "--ar 16:9", "16:9", "4:3", "vertical 9:16".
   - Calidad / resolución: "8k", "4k", "HDR", "RAW", "high resolution".
   - Engine tags: "Midjourney style", "Stable Diffusion", "DALL-E".
   - Prompt-engineering tokens: "(word:1.2)", "[word]", negative-prompt
     syntax, seed values, LoRA weights, "::weight".

   (El estilo cinematográfico, la paleta, la óptica y el grain de film
    se agregan automáticamente después del LLM desde el art_profile.
    Si los escribís en zona 1, ver regla 2 — son rechazados ahí.)

7. **LARGO DE PROMPT (ZONA 1) — target 120-200 chars, máximo 240, mínimo 80.**
   Apuntá a 120-200 chars para zona 1 (subject + action + environment +
   marcador temporal). Pasarte de 240 es señal de que estás escribiendo
   lighting/palette/style — eso va en zona 2 (regla 2). Más corto que
   80 pierde detalle visual.
   Si te quedás cerca del techo: priorizá Subject + Action + Environment
   + UN marcador temporal + UN ancla visual del bloque DATOS VISUALES
   CANÓNICOS. Recortá adjetivos secundarios y descripciones de fondo
   antes que sacrificar el anclaje temporal.
   NO contar palabras, contar caracteres.
   El art_profile (lighting/palette/optics/grain) se concatena DESPUÉS
   automáticamente — no cuenta para tu rango.

8. **ART_PROFILE POR IMAGEN, SIN DEFAULTS.** Elegí una etiqueta del
   catálogo (mayúsculas exactas) por cada imagen, basándote en la
   SEMÁNTICA de la escena que estás describiendo (interior/exterior,
   cálido/frío, árido/templado, natural/industrial, superficie/submarino,
   tierra/aire/espacio). El criterio es el TIPO de escena, no la paleta:
   la paleta la pega el código desde art_profiles. Si dos profiles encajan
   semánticamente, elegí el más específico (ej. DESERT antes que
   WILDERNESS para outback árido, MARITIME_EXTERIOR antes que AERIAL
   para barco en superficie visto desde lejos). Cada imagen del cap
   decide independiente — es esperable que un mismo cap tenga 2-4
   profiles distintos si las escenas saltan entre tipos.

9. **ANCHORS = SUBSTRING EXACTO.** El narration_anchor debe ser una
   porción literal y contigua de la narración del cap. Sin reformular,
   sin agregar puntuación, sin traducir, sin recortar palabras.

10. **ANCHORS EN ORDEN.** Cada anchor debe aparecer DESPUÉS del anterior
    en la narración. Sin solapamiento (el final de uno < el inicio del
    siguiente). El array de imgs es la línea de tiempo del cap.

11. **ANCLAJE TEMPORAL OBLIGATORIO EN CADA PROMPT.** Cada `prompt`
    (y `video_prompt` en caps veo) DEBE incluir AL MENOS UN marcador
    temporal explícito coherente con la ERA VISUAL del bloque DATOS
    VISUALES CANÓNICOS arriba. Ejemplos válidos de marcador:
    - "1960s naval uniform"
    - "vintage 1950s typewriter"
    - "period-correct 1968 control panel"
    - "early 20th century work clothes"
    - "mid-century industrial equipment"

    Sin marcador temporal explícito → Flux defaultea a estética moderna →
    BUG anacrónico. Usá elementos concretos del bloque ERA VISUAL
    (clothing, technology, vehicles_machinery, interiors) para anclar
    la escena en su época.

12. **NO METÁFORAS NI ABSTRACTOS NO-VISUALES EN EL PROMPT.**
    Frases prohibidas (no se pueden dibujar):
    - "sense of impending doom", "feeling of dread", "atmosphere of unease"
    - "eerie silence" (el silencio es auditivo, no visual)
    - "metaphor for X", "symbol of Y", "evoking Z", "essence of W"
    - "subtle sense of...", "haunting...", "ominous feeling..."

    Si el anchor usa lenguaje metafórico/poético (ej: "respirando su
    destino", "veneno puro"), NO copies la metáfora al prompt. Extraé
    la intención visual concreta y describí solo lo físicamente
    representable.

    ✗ MAL: "An Australian child playing innocently, a subtle sense of
            impending doom in the background, harsh desert sun"
    ✓ BIEN: "An Australian child playing innocently, surrounded by
             drifting blue dust visible in the harsh desert sun, hazy
             distorted horizon behind"

    ✗ MAL: "stark shadows, eerie silence, metaphor for hidden danger"
    ✓ BIEN: "stark shadows, abandoned plaza without people, faded
             warning sign half-buried in dust (no readable text)"

    REGLA DE ORO: si tu prompt contiene "sense of", "feeling of",
    "metaphor of", "essence of", "haunting", borralo. Reemplazá con
    elementos visuales concretos.

13. **FIDELITY AL ANCHOR.** El prompt ilustra lo que el anchor describe,
    no su contexto general. Sub-reglas:

    a) **Plurales:** si el anchor menciona varios sujetos (ej: "Niños
       como Philip Noble y Ross Munro"), el prompt debe mostrar ≥2
       sujetos ("Two Australian children"), no uno solo. Anonimizá los
       nombres pero PRESERVÁ la cantidad.

    b) **Preguntas/eventos específicos:** si el anchor pregunta o
       describe un evento concreto ("¿Cuándo cerró la mina?"), ilustrá
       el EVENTO (la mina cerrada el día final, una boca de mina sellada
       con cadena, carteles 'CERRADO' sin texto legible), NO el aftermath
       general (zona contaminada actual).

    c) **Era del anchor, no del tema:** mirá los tiempos verbales del
       anchor. Si el anchor habla en presente o describe una medición
       o declaración actual ("se extiende a lo largo de 46,840
       hectáreas"), la era visual del prompt debe ser CONTEMPORÁNEA al
       anchor (presente), NO al origen del problema (1940s). Confundir
       la era de la causa con la era de la medición es bug.

    d) **Outcome > antecedente:** si el anchor menciona consecuencias
       ("cosecha de casos de asbestosis", "tributo humano", "vidas
       perdidas"), el prompt debe ilustrar la CONSECUENCIA (gente
       enferma de la era, sala de hospital, figuras humanas
       afectadas), NO las advertencias previas (papeleo, memos
       técnicos)."""


# ═══════════════════════════════════════════════════════════════
#  PROMPT VEO (caps 1, 7)
# ═══════════════════════════════════════════════════════════════

def _build_veo_prompt(
    topic: dict,
    cap_data: dict,
    narration_text: str,
) -> str:
    """Prompt para caps veo (hook, reveal_outro). 1 image_prompt + 1 video_prompt."""
    cap_n = cap_data["chapter_number"]
    role = cap_data.get("role") or "?"
    cap_title = cap_data.get("title") or "(sin título)"
    bullets_block = _format_bullets(cap_data.get("bullets") or [])

    topic_block = _build_topic_block(topic)
    visual_canon_block = _format_visual_canon_block(topic)
    rules_block = _build_rules_block()
    profiles_guide = _format_profiles_guide()
    profiles_aesthetics = _format_profiles_aesthetics()

    return f"""Sos un director de fotografía documental. Generás prompts visuales
en INGLÉS para Veo (motion video) que ilustran narraciones documentales en
español. Tu output es JSON puro, sin markdown.

═══════════════════════════════════════════════════
TEMA
═══════════════════════════════════════════════════
{topic_block}

═══════════════════════════════════════════════════
DATOS VISUALES CANÓNICOS (verdad sellada — NO re-inferir)
═══════════════════════════════════════════════════
{visual_canon_block}

═══════════════════════════════════════════════════
CATÁLOGO DE PROFILES (referencia visual)
═══════════════════════════════════════════════════
{profiles_guide}

═══════════════════════════════════════════════════
AESTHETIC DE CADA PROFILE (referencia — la pega el código, NO el LLM)
═══════════════════════════════════════════════════
{profiles_aesthetics}

⚠ Vos elegís el `art_profile` para esta imagen del catálogo de arriba.
   La paleta, lighting, óptica y grain del aesthetic se concatenan
   AUTOMÁTICAMENTE al final de tu prompt según el profile que elijas —
   vos NO los escribís (regla 2). Este catálogo está acá solo para que
   elijas bien el profile según la SEMÁNTICA de la escena (interior
   cálido vs frío, exterior árido vs templado, natural vs industrial,
   superficie vs submarino, etc.). NO intentes "ajustar" tu prompt a
   la paleta — el LLM no escribe paleta en este pipeline.

═══════════════════════════════════════════════════
REGLAS INVIOLABLES
═══════════════════════════════════════════════════
{rules_block}

═══════════════════════════════════════════════════
ESPECÍFICO PARA VEO (este cap)
═══════════════════════════════════════════════════

Este cap es {role}, render_engine=veo. Generás:
- 1 image_prompt: la escena base (Subject→Action→Environment, 80-240 chars EN, target 120-200). Sin lighting/palette/style — eso va en zona 2 (regla 2).
- 1 video_prompt: cómo se mueve el SUJETO y el AMBIENT específico de esta escena
  (80-240 chars EN, target 120-200). Describe MOVIMIENTO. NO escribas camera arc
  genérico ("subtle drift", "no cuts") ni motion del profile (dust drifting,
  marine snow) — eso lo agrega VEO_MOTION después. Vos describí: movimiento
  del sujeto (coat swaying, eyes blinking, hair in wind), camera arc específico
  al cap (slow push in al rostro, slow pull out), y ambient particular de la
  escena que NO es del profile (ej: smoke from cigarette, water dripping
  from this specific machine).
- 1 subject_ref: identificador del sujeto. "main_subject" si es el
  protagonista; otros nombres si la escena no tiene protagonista humano
  (ej. "establishing_shot", "interior_scene", "landscape_view").
- 1 art_profile: del catálogo (mayúsculas exactas). Elegí el que mejor
  encaje semánticamente con la escena de este cap (interior/exterior,
  cálido/frío, árido/templado, natural/industrial, superficie/submarino).
  Sin defaults: cada cap veo decide su profile basado en su contenido.
- 1 narration_anchor GLOBAL del cap: substring EXACTO y AMPLIO de la
  narración del cap. Debe abarcar la idea central del cap entero, no una
  frase breve aislada. Apuntá a 60-200 chars (~10-30 palabras). NO recortes
  a una frase corta de impacto: el anchor representa el cap completo para
  validación cruzada en m05.

ESTRUCTURA video_prompt:
- Camera movement: slow push in, slow pull out, slow pan left/right,
  static with subtle drift, orbit. PROHIBIDO cuts, jumps, fast cuts,
  zoom rapid.
- Ambient: dust drifting, fog rolling, water flowing, wind through grass,
  light slowly intensifying.
- Motion sutil sobre el sujeto: figure breathing, hair moving in wind,
  eyes blinking. NO acción fuerte (Veo prioriza estabilidad).
- Lighting consistency: la luz no cambia durante el clip.
- COMPATIBILIDAD: el video_prompt debe describir movimiento de elementos
  que ya están en el image_prompt. No agregar elementos nuevos.

═══════════════════════════════════════════════════
CAP {cap_n} — {role}
═══════════════════════════════════════════════════
title         : {cap_title}
bullets       :
{bullets_block}

NARRACIÓN COMPLETA DEL CAP (fuente del narration_anchor):
{narration_text}

═══════════════════════════════════════════════════
EJEMPLOS
═══════════════════════════════════════════════════

✓ CORRECTO (cap hook documental, profile DESERT, marcador temporal explícito):
{{
  "image_prompt": "An elderly miner in dusty 1960s work clothes standing alone on a deserted outback road, vast emptiness around the figure, distant period-correct mining headframe barely visible on the horizon, wide shot of the open terrain",
  "video_prompt": "The miner's coat swaying gently in the wind, fine dust particles drifting slowly through the air, distant heat shimmer warping the horizon line, the figure standing still while the desert breathes around him",
  "subject_ref": "main_subject",
  "art_profile": "DESERT",
  "narration_anchor": "Más de 2,000 personas perdieron la vida en Wittenoom, un pueblo minero borrado de los mapas en 2007"
}}

✓ CORRECTO (cap reveal, profile INDUSTRIAL, persona de DOCUMENTED_PEOPLE):
{{
  "image_prompt": "A mid-30s American naval officer in 1960s U.S. Navy service uniform on the cramped control bridge of a 1968 Skipjack-class submarine, focused authoritative expression, period-correct analog instruments around him, brass detail visible on the bulkhead behind",
  "video_prompt": "Slow push in toward the officer's face, instrument needles flickering subtly, faint vapor drifting through the cramped compartment, his shoulders rising slowly with controlled breathing",
  "subject_ref": "main_subject",
  "art_profile": "INDUSTRIAL",
  "narration_anchor": "el comandante revisó por última vez la posición del submarino, sin saber que esa sería la última transmisión que enviaría al mando"
}}
   ↑ Nota: usa el `appearance_canon` de PERSONAS DOCUMENTADAS sin nombre,
     y ancla temporalmente con "1960s", "1968", "period-correct". El
     image_prompt NO menciona lighting ni paleta — eso lo agrega el código
     desde art_profile. El video_prompt menciona movimiento del sujeto y
     ambient específico de la escena (instrument needles flickering, vapor
     drifting) — el "no cuts" y motion universal del profile lo agrega
     VEO_MOTION después.

✗ INCORRECTO (varios errores):
{{
  "image_prompt": "John Smith born 1932 mining at Wittenoom in 1956",   ← inventó nombre, nombre propio prohibido
  "video_prompt": "Fast cuts between three locations, dramatic zoom",   ← prohibido cuts/fast/zoom rapid
  "subject_ref": "main_subject",
  "art_profile": "DESERT",
  "narration_anchor": "más de dos mil personas murieron"   ← reformulado, no substring exacto
}}

✗ INCORRECTO (sin marcador temporal Y con lighting/style en zona 1):
{{
  "image_prompt": "A naval officer on a submarine bridge with instruments around him, focused expression, dim lighting, tense atmosphere",   ← falta marcador temporal + "dim lighting" prohibido en zona 1
  "video_prompt": "Slow push in, instruments glowing, atmospheric mood, cinematic feel",   ← "atmospheric mood" + "cinematic" prohibidos en zona 1
  "subject_ref": "main_subject",
  "art_profile": "INDUSTRIAL",
  "narration_anchor": "el comandante revisó la posición"
}}

═══════════════════════════════════════════════════
FORMATO DE OUTPUT (JSON estricto, nada más)
═══════════════════════════════════════════════════

{{
  "image_prompt": "string EN, 80-240 chars (target 120-200) — zona 1 sin lighting/palette",
  "video_prompt": "string EN, 80-240 chars (target 120-200) — zona 1 motion específico de la escena",
  "subject_ref": "string",
  "art_profile": "PROFILE_DEL_CATALOGO (mayúsculas exactas)",
  "narration_anchor": "string ES (substring EXACTO y AMPLIO, 60-200 chars, GLOBAL del cap)"
}}

NO agregues texto fuera del JSON. NO uses bloque markdown ```.
"""


# ═══════════════════════════════════════════════════════════════
#  PROMPT FLUX (caps 2-6)
# ═══════════════════════════════════════════════════════════════

def _build_flux_prompt(
    topic: dict,
    cap_data: dict,
    narration_text: str,
    n_images: int,
) -> str:
    """Prompt para caps flux (development). Array de N items con anchors."""
    cap_n = cap_data["chapter_number"]
    role = cap_data.get("role") or "development"
    cap_title = cap_data.get("title") or "(sin título)"
    bullets_block = _format_bullets(cap_data.get("bullets") or [])

    topic_block = _build_topic_block(topic)
    visual_canon_block = _format_visual_canon_block(topic)
    rules_block = _build_rules_block()
    profiles_guide = _format_profiles_guide()
    profiles_aesthetics = _format_profiles_aesthetics()
    valid_list = ", ".join(sorted(VALID_PROFILES))

    return f"""Sos un director de fotografía documental. Generás prompts visuales
en INGLÉS para Flux que ilustran narraciones documentales en español.
Tu output es JSON puro, sin markdown.

═══════════════════════════════════════════════════
TEMA
═══════════════════════════════════════════════════
{topic_block}

═══════════════════════════════════════════════════
DATOS VISUALES CANÓNICOS (verdad sellada — NO re-inferir)
═══════════════════════════════════════════════════
{visual_canon_block}

═══════════════════════════════════════════════════
CATÁLOGO DE PROFILES (referencia visual)
═══════════════════════════════════════════════════
{profiles_guide}

PROFILES VÁLIDOS (uso literal en mayúsculas):
  {valid_list}

═══════════════════════════════════════════════════
AESTHETIC DE CADA PROFILE (referencia — la pega el código, NO el LLM)
═══════════════════════════════════════════════════
{profiles_aesthetics}

⚠ Por cada imagen elegís el `art_profile` del catálogo de arriba que
   mejor encaje con la escena. La paleta, lighting, óptica y grain del
   aesthetic se concatenan AUTOMÁTICAMENTE a CADA prompt según el profile
   que elijas — vos NO los escribís (regla 2). Este catálogo está acá
   solo para que elijas bien por imagen según la SEMÁNTICA de la escena
   (interior cálido vs frío, exterior árido vs templado, natural vs
   industrial, superficie vs submarino, etc.). Sin defaults: cada imagen
   decide su profile independiente, viendo todo el cap. NO intentes
   "ajustar" tu prompt a la paleta — el LLM no escribe paleta en este
   pipeline.

═══════════════════════════════════════════════════
REGLAS INVIOLABLES
═══════════════════════════════════════════════════
{rules_block}

═══════════════════════════════════════════════════
ESPECÍFICO PARA FLUX (este cap)
═══════════════════════════════════════════════════

Este cap es {role}, render_engine=flux. Generás un array de
EXACTAMENTE {n_images} image_prompts.

Para CADA item del array:
- prompt: Subject→Action→Environment. 80-240 chars EN, target 120-200. Zona 1
  sin lighting/palette/style — eso lo agrega el código desde art_profile (regla 2).
- art_profile: del catálogo (mayúsculas exactas). Por imagen, sin defaults.
  Elegí el que mejor encaje semánticamente con la escena específica de
  cada imagen (interior/exterior, cálido/frío, árido/templado,
  natural/industrial, superficie/submarino).
- subject_ref: "main_subject" para el protagonista, otros para escenas
  sin protagonista humano (ej. "establishing_shot", "interior_scene").
- emotional_rank: R1 / R2 / R3.
- narration_anchor: substring EXACTO de la narración del cap.

DISTRIBUCIÓN DE narration_anchors (CRÍTICO — leer dos veces):
- Partí mentalmente la narración del cap en {n_images} segmentos en orden.
- Cada anchor cubre uno de esos segmentos en orden cronológico.
- Anchor de imagen 1 = primer segmento de la narración.
- Anchor de imagen N = último segmento.
- NO necesitan cubrir el 100% del texto (puede haber huecos en frases
  reflexivas/transiciones), PERO los segmentos que cubrís deben estar
  en orden estricto y sin solaparse.
- Anchor mínimo: 25 chars. Anchor máximo: 200 chars. Apuntar 60-120 chars.

DISTRIBUCIÓN DE emotional_rank:
- 1-2 imgs R1 (pico del cap: cierre, revelación, momento más impactante).
- 2-3 imgs R2 (acción, transición fuerte, persona en tensión).
- Resto R3 (escena descriptiva, contexto, ambiente).
- NO todas R1, NO todas R3. Mezclá según el peso emocional de cada anchor.

VARIACIÓN VISUAL (importante para retención):
- NO repetir la misma escena con variaciones mínimas.
- Alterná escalas (wide / medium / close-up).
- Alterná sujetos cuando sea posible (persona / lugar / objeto / detalle).
- Si todas las {n_images} imgs muestran lo mismo desde el mismo ángulo,
  fallaste. Buscá ángulos y motivos visuales distintos para cada anchor.

═══════════════════════════════════════════════════
CAP {cap_n} — {role}
═══════════════════════════════════════════════════
title         : {cap_title}
n_images      : {n_images}     ← array DEBE tener exactamente esta cantidad
bullets       :
{bullets_block}

NARRACIÓN COMPLETA DEL CAP (única fuente para anchors):
{narration_text}

═══════════════════════════════════════════════════
EJEMPLOS
═══════════════════════════════════════════════════

✓ CORRECTO (fragmento, 3 imgs de un cap, profile MARITIME_EXTERIOR):
[
  {{
    "prompt": "A 1968 Skipjack-class nuclear submarine departing a 1960s naval base at dawn, calm waters reflecting the steel hull, distant period-correct control tower silhouette on the shoreline, gulls circling above the hull, wide shot of the harbor",
    "art_profile": "MARITIME_EXTERIOR",
    "subject_ref": "main_subject",
    "emotional_rank": "R3",
    "narration_anchor": "El submarino zarpó de Norfolk en febrero"
  }},
  {{
    "prompt": "A vintage 1960s nuclear submarine cutting through dark Atlantic waves seen from above, white wake trailing behind the hull, low Cold War-era cloud cover pressing over the horizon, vast open sea around the vessel",
    "art_profile": "MARITIME_EXTERIOR",
    "subject_ref": "main_subject",
    "emotional_rank": "R2",
    "narration_anchor": "Cruzó el Atlántico sin incidentes"
  }},
  {{
    "prompt": "Interior of a 1968 submarine, narrow steel corridor with crew in 1960s U.S. Navy working uniforms at vintage analog control panels, period-correct gauges and brass valves around them, no readable screens, medium shot of focused expressions",
    "art_profile": "INDUSTRIAL",
    "subject_ref": "interior_scene",
    "emotional_rank": "R2",
    "narration_anchor": "La tripulación cumplía rutinas técnicas"
  }}
]
   ↑ Notá: cada prompt ancla en una década o año específico ("1968",
     "1960s", "Cold War-era"). Las personas se describen por aspecto+era,
     nunca por nombre. Las pantallas se mencionan como "no readable screens".
     NINGÚN prompt menciona lighting ni paleta — eso lo agrega el código
     desde art_profile después. El framing ("wide shot", "medium shot",
     "seen from above") SÍ está permitido en zona 1.

✓ CORRECTO (cap con persona de DOCUMENTED_PEOPLE, profile INDUSTRIAL):
{{
  "prompt": "A mid-30s American naval officer in 1960s U.S. Navy service uniform reviewing a vintage nautical chart in a cramped 1968 submarine compartment, focused authoritative expression, period-correct analog instruments around him, brass detail on the bulkhead behind, close-up of his hands on the chart",
  "art_profile": "INDUSTRIAL",
  "subject_ref": "main_subject",
  "emotional_rank": "R1",
  "narration_anchor": "el comandante revisó por última vez la posición"
}}
   ↑ Notá: usa appearance_canon de PERSONAS DOCUMENTADAS sin nombre, y
     ancla con "1960s", "1968", "vintage", "period-correct". Sin lighting
     ni paleta en zona 1 — el código las agrega desde INDUSTRIAL.

✗ INCORRECTO (errores típicos):
- 8 imgs todas del exterior del submarino → falta variación visual.
- anchor "Cruzó el Atlántico" antes que "El submarino zarpó" → fuera de orden.
- todas con emotional_rank=R1 → distribución mala.
- "El submarino zarpó de Norfolk" si en la narración dice "El USS Scorpion
  zarpó del puerto de Norfolk" → no es substring exacto.
- prompt en español → prohibido.
- "Commander Slattery on the bridge..." → nombre propio prohibido (regla 5).
- "sonar screen displaying coordinates with readable numbers" → texto/números
  visibles prohibidos (regla 4). Usar "no readable text" o equivalente.
- "A naval officer on a submarine bridge" → falta marcador temporal
  (regla 11). Flux defaultea a estética moderna.

═══════════════════════════════════════════════════
FORMATO DE OUTPUT (JSON estricto, nada más)
═══════════════════════════════════════════════════

{{
  "image_prompts": [
    {{
      "prompt": "string EN, 80-240 chars (target 120-200) — zona 1 sin lighting/palette",
      "art_profile": "PROFILE_DEL_CATALOGO",
      "subject_ref": "string",
      "emotional_rank": "R1" | "R2" | "R3",
      "narration_anchor": "substring EXACTO de la narración"
    }}
    // ... exactamente {n_images} items
  ]
}}

NO agregues texto fuera del JSON. NO uses bloque markdown ```.
"""


# ═══════════════════════════════════════════════════════════════
#  VALIDACIÓN
# ═══════════════════════════════════════════════════════════════

def _validate_prompt_length(prompt: str, label: str) -> None:
    n = len(prompt)
    if n < PROMPT_MIN_CHARS:
        raise VisualValidationError(
            f"{label}: {n} chars (mínimo {PROMPT_MIN_CHARS}). "
            f"Demasiado corto, agregá más detalle visual."
        )
    if n > PROMPT_MAX_CHARS:
        raise VisualValidationError(
            f"{label}: {n} chars (máximo {PROMPT_MAX_CHARS}). "
            f"Demasiado largo, recortá descripciones secundarias."
        )


def _validate_prompt_length_zona1(prompt: str, label: str) -> None:
    """Valida longitud de zona 1 (output crudo del LLM, sin stitch).

    Diferente de _validate_prompt_length: este valida EL OUTPUT DEL LLM
    antes de concatenar zona 2. El rango es más bajo porque zona 1 son
    solo Subject+Action+Environment (sin lighting/palette/style).
    """
    n = len(prompt)
    if n < PROMPT_MIN_CHARS_ZONA1:
        raise VisualValidationError(
            f"{label}: {n} chars (mínimo zona 1 {PROMPT_MIN_CHARS_ZONA1}). "
            f"Demasiado corto, agregá más subject/action/environment "
            f"(sin lighting/palette — eso lo agrega el código)."
        )
        # Sin tope superior duro: si el LLM se pasa de zona 1 max es señal
        # de que metió lighting/palette/style — lo va a atrapar
        # _validate_zone1_clean con un mensaje de feedback más útil.
    if n > PROMPT_MAX_CHARS_ZONA1:
        raise VisualValidationError(
            f"{label}: {n} chars (máximo zona 1 {PROMPT_MAX_CHARS_ZONA1}). "
            f"Demasiado largo. Probable causa: estás escribiendo lighting/"
            f"palette/style (zona 2). Reescribí solo subject+action+"
            f"environment — el código agrega lo demás."
        )


def _validate_no_text_leakage(prompt: str, label: str) -> None:
    """Regla 14: detecta patrones de instrucción de texto en imagen.

    El LLM a veces esquiva la regla 14 del prompt con eufemismos tipo
    "blurred area where name was". Acá los detectamos por regex.
    Raise VisualValidationError con mensaje educativo si encuentra match.
    """
    prompt_lc = prompt.lower()
    for pattern in TEXT_LEAKAGE_PATTERNS:
        m = re.search(pattern, prompt_lc, re.IGNORECASE)
        if m:
            matched_fragment = m.group(0)
            raise VisualValidationError(
                f"{label}: regla 14 violada (text-leakage detectado).\n"
                f"  FRAGMENTO PROBLEMÁTICO: '{matched_fragment}'\n"
                f"  CAUSA: el prompt indica al image generator que dibuje "
                f"texto/nombres aunque sea blurred o indistinct.\n"
                f"  REGLA 14: el prompt NO debe describir áreas, sellos, "
                f"carteles ni espacios que 'tenían texto'. Si querés mostrar "
                f"ausencia, describí un OBJETO sin texto (poste vacío sin "
                f"cartel, mapa con manchas de tiempo en lugar de área "
                f"borrada con nombre).\n"
                f"  Reescribí el prompt eliminando cualquier referencia a "
                f"'name', 'text', 'label', 'words' o lo equivalente."
            )


def _validate_zone1_clean(prompt: str, label: str) -> None:
    """Approach 2-zona: rechaza si el LLM mete lighting/palette/style en su output.

    El LLM debería escribir SOLO Subject+Action+Environment (zona 1). Si
    detecta términos prohibidos (lighting/palette/style/optics), levanta
    VisualValidationError y `_call_with_validation_retry` reintenta con
    feedback explicando qué encontró y dónde.

    Las listas viven en ZONA1_FORBIDDEN_LIGHTING / _PALETTE / _STYLE
    arriba en este archivo, y se duplican textualmente en la regla 2 del
    prompt para que el LLM las vea explícitamente. Si cambian acá hay
    que actualizar también la regla 2 (ver _build_rules_block).

    Match por palabra completa (\\b...\\b) salvo para multi-palabra
    (ej: "golden hour"), donde el match es por substring exacto.
    """
    prompt_lc = prompt.lower()
    hits_lighting: list[str] = []
    hits_palette: list[str] = []
    hits_style: list[str] = []

    def _check(term: str, prompt_lc: str) -> bool:
        # Multi-palabra (contiene espacio o guión-medio): substring exacto.
        # Mono-palabra: word boundary, evita falsos positivos tipo "warmly".
        if " " in term or "-" in term:
            return term in prompt_lc
        return bool(re.search(rf"\b{re.escape(term)}\b", prompt_lc))

    for term in ZONA1_FORBIDDEN_LIGHTING:
        if _check(term, prompt_lc):
            hits_lighting.append(term)
    for term in ZONA1_FORBIDDEN_PALETTE:
        if _check(term, prompt_lc):
            hits_palette.append(term)
    for term in ZONA1_FORBIDDEN_STYLE:
        if _check(term, prompt_lc):
            hits_style.append(term)

    if not (hits_lighting or hits_palette or hits_style):
        return

    parts = []
    if hits_lighting:
        parts.append(f"  - LIGHTING: {sorted(hits_lighting)}")
    if hits_palette:
        parts.append(f"  - PALETTE:  {sorted(hits_palette)}")
    if hits_style:
        parts.append(f"  - STYLE:    {sorted(hits_style)}")
    hits_summary = "\n".join(parts)

    # Hints contextuales: si algún término tiene reemplazo conceptual válido
    # en zona 1, lo sugerimos explícitamente. Para el resto del LLM va a
    # tener que borrar (el código los agrega desde art_profile).
    all_hits = hits_lighting + hits_palette + hits_style
    contextual_hints = []
    for term in all_hits:
        if term in ZONA1_REPLACEMENT_HINTS:
            contextual_hints.append(
                f"    • '{term}' → reemplazá por '{ZONA1_REPLACEMENT_HINTS[term]}' "
                f"(framing equivalente, permitido en zona 1)"
            )
    hints_block = ""
    if contextual_hints:
        hints_block = (
            "\n  REEMPLAZOS SUGERIDOS (mantienen tu intención sin violar regla 2):\n"
            + "\n".join(contextual_hints)
        )

    raise VisualValidationError(
        f"{label}: regla 2 violada (zona 1 contiene términos de zona 2).\n"
        f"  TÉRMINOS PROHIBIDOS DETECTADOS:\n"
        f"{hits_summary}"
        f"{hints_block}\n"
        f"  CAUSA: estos elementos pertenecen al art_profile y los agrega\n"
        f"  el código DESPUÉS del LLM. Si los escribís vos, contradicen\n"
        f"  la paleta/lighting del profile y el output queda incoherente.\n"
        f"  REGLA 2: zona 1 = SOLO Subject + Action + Environment\n"
        f"  (con marcador temporal de regla 11 en el environment).\n"
        f"  Para términos sin reemplazo sugerido: borralos. El estilo,\n"
        f"  paleta, lighting, óptica y grain los agrega el código."
    )


def _validate_profile_palette_coherence(
    prompt: str, profile: str, label: str
) -> None:
    """Regla 15: chequea que el prompt no contenga palabras de paleta
    incompatible con el profile elegido.

    Cada profile tiene una lista de palabras prohibidas (semánticamente
    contradictorias). Si encuentra match, raise VisualValidationError con
    sugerencia de profile alternativo cuando aplica.
    """
    forbidden = PROFILE_FORBIDDEN_PALETTE_WORDS.get(profile, ())
    if not forbidden:
        return  # profile sin reglas específicas, OK

    prompt_lc = prompt.lower()
    matches = []
    for word in forbidden:
        # Match por palabra completa para evitar falsos positivos
        # (ej: "warm" matchea "warmly" no queremos)
        if re.search(rf"\b{re.escape(word)}\b", prompt_lc):
            matches.append(word)

    if matches:
        # Sugerencia de profile alternativo según la palabra encontrada
        suggestion = ""
        match_set = set(matches)
        if profile == "INDUSTRIAL" and match_set & {"amber", "golden", "ochre", "warm afternoon", "warm light"}:
            suggestion = " Considerá usar INTERIOR (paleta cálida) o DESERT si la escena es exterior árido."
        elif profile == "WILDERNESS" and match_set & {"arid", "desert", "scorched", "ochre"}:
            suggestion = " Considerá usar DESERT (paleta árida ochre) en lugar de WILDERNESS (verde templado)."
        elif profile == "INTERIOR" and "sterile" in match_set:
            suggestion = " Considerá usar INDUSTRIAL para escenas frías/clínicas."

        raise VisualValidationError(
            f"{label}: regla 15 violada (paleta incoherente con profile).\n"
            f"  PROFILE ELEGIDO: {profile}\n"
            f"  PALABRAS PROHIBIDAS PRESENTES: {sorted(matches)}\n"
            f"  CAUSA: la paleta del profile {profile} no encaja con esas "
            f"palabras del prompt.{suggestion}\n"
            f"  REGLA 15: si elegís un profile, todas las palabras de paleta "
            f"del prompt deben ser coherentes con la paleta del profile. "
            f"Reescribí el prompt o cambiá el profile."
        )


def _find_closest_narration_fragment(anchor: str, narration: str) -> str | None:
    """Busca el fragmento de narración más parecido al anchor recibido.

    Cuando el modelo parafrasea un anchor (lo escribe casi-literal en lugar
    de copiar substring exacto), esta función encuentra qué porción real
    de la narración tenía en mente. Sirve para enriquecer el feedback del
    retry: en lugar de "no es substring exacto", le mostramos al modelo
    "querías esto, en realidad la narración dice esto otro — copiá literal".

    Estrategia: ventana deslizante del tamaño del anchor sobre la narración,
    SequenceMatcher.ratio() para medir similitud. Después expande el ganador
    a bordes de palabra para que el feedback no quede truncado a la mitad.

    Returns:
        El fragmento (con palabras completas) más parecido si supera umbral
        de similitud (0.5), None si el modelo escribió algo no relacionado.
    """
    if not anchor or not narration or len(narration) < 30:
        return None
    target_len = len(anchor)
    if target_len < 20:
        return None

    step = max(5, target_len // 8)
    best_ratio = 0.0
    best_start = -1

    anchor_lc = anchor.lower()
    narr_len = len(narration)

    for start in range(0, narr_len, step):
        end = min(start + target_len, narr_len)
        if end - start < target_len // 2:
            break
        window = narration[start:end]
        ratio = SequenceMatcher(None, anchor_lc, window.lower()).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best_start = start

    if best_ratio < 0.5 or best_start < 0:
        return None

    # ─── Expandir a bordes de palabra ───
    s = best_start
    e = min(best_start + target_len, narr_len)

    # Izquierda: si cayó dentro de palabra, retroceder al espacio anterior
    while s > 0 and not narration[s - 1].isspace():
        s -= 1
    # Derecha: si cayó dentro de palabra, avanzar al próximo espacio o puntuación
    while e < narr_len and not narration[e].isspace() and narration[e] not in ".,;:!?":
        e += 1

    return narration[s:e].strip()


def _validate_anchor_substring(
    anchor: str,
    narration: str,
    label: str,
) -> int:
    """Valida que anchor sea substring exacto de narration. Devuelve la posición.

    Si falla, busca el fragmento parecido en la narración y lo incluye en el
    mensaje de error para que el retry tenga material concreto donde anclarse.
    """
    if not isinstance(anchor, str) or not anchor.strip():
        raise VisualValidationError(f"{label}: anchor vacío o no string")
    pos = narration.find(anchor)
    if pos < 0:
        # Buscar fragmento parecido para guiar el retry
        closest = _find_closest_narration_fragment(anchor, narration)
        anchor_preview = anchor[:100] + ("..." if len(anchor) > 100 else "")
        if closest:
            closest_preview = closest[:120] + ("..." if len(closest) > 120 else "")
            raise VisualValidationError(
                f"{label}: el narration_anchor NO es substring exacto.\n"
                f"  ANCHOR QUE ENVIASTE (parafraseado, INVÁLIDO):\n"
                f"    '{anchor_preview}'\n"
                f"  EN LA NARRACIÓN HAY ESTO PARECIDO (copialo LITERAL, sin reformular):\n"
                f"    '{closest_preview}'\n"
                f"  Regla 9: el anchor debe ser una porción literal y contigua de la narración. "
                f"NO traducir, NO reformular, NO recortar palabras intermedias."
            )
        raise VisualValidationError(
            f"{label}: el narration_anchor NO es substring exacto de la narración. "
            f"Anchor recibido: '{anchor_preview}'. "
            f"Debe ser una porción literal y contigua de la narración del cap."
        )
    return pos


def _validate_veo_cap(parsed: dict, narration: str, cap_number: int) -> dict:
    """Valida output de un cap veo. Devuelve dict normalizado o raise.

    El dict devuelto contiene los prompts en ZONA 1 cruda (sin stitch de
    zona 2). El stitching se aplica más tarde con _stitch_zone2_into_cap_veo
    desde assign_visual_prompts, después de pasar todas las validaciones.
    """
    if not isinstance(parsed, dict):
        raise VisualValidationError(
            f"cap {cap_number} (veo): output no es dict ({type(parsed).__name__})"
        )

    image_prompt = parsed.get("image_prompt")
    if not isinstance(image_prompt, str) or not image_prompt.strip():
        raise VisualValidationError(f"cap {cap_number} (veo): image_prompt vacío o no string")
    image_prompt = image_prompt.strip()
    _validate_prompt_length_zona1(image_prompt, f"cap {cap_number} (veo) image_prompt")

    video_prompt = parsed.get("video_prompt")
    if not isinstance(video_prompt, str) or not video_prompt.strip():
        raise VisualValidationError(f"cap {cap_number} (veo): video_prompt vacío o no string")
    video_prompt = video_prompt.strip()
    _validate_prompt_length_zona1(video_prompt, f"cap {cap_number} (veo) video_prompt")

    # ─── art_profile (nuevo desde FASE 1: m03 elige por imagen también en veo) ───
    profile = parsed.get("art_profile")
    if not isinstance(profile, str):
        raise VisualValidationError(
            f"cap {cap_number} (veo): art_profile no es string ({type(profile).__name__})"
        )
    profile_norm = profile.strip().upper()
    if profile_norm not in VALID_PROFILES:
        raise VisualValidationError(
            f"cap {cap_number} (veo): art_profile='{profile}' no está en el catálogo. "
            f"Válidos: {sorted(VALID_PROFILES)}"
        )

    subject_ref = parsed.get("subject_ref")
    if not isinstance(subject_ref, str) or not subject_ref.strip():
        raise VisualValidationError(f"cap {cap_number} (veo): subject_ref vacío o no string")
    subject_ref = subject_ref.strip()

    anchor = parsed.get("narration_anchor")
    _validate_anchor_substring(anchor, narration, f"cap {cap_number} (veo)")
    anchor = anchor.strip() if isinstance(anchor, str) else anchor

    # ─── Regla 2 (zona 1 limpia) ───
    # Reglas 14 (text-leakage) y 15 (paleta coherente) eliminadas en
    # chat 16: producían demasiados falsos positivos contra terminología
    # histórica legítima ("Liquidator", "Shelter Object", "sterile" para
    # escenas clínicas). La auditoría semántica de m05 (con voting N=3)
    # detecta los casos reales sin bloquear los falsos positivos.
    _validate_zone1_clean(image_prompt, f"cap {cap_number} (veo) image_prompt")
    _validate_zone1_clean(video_prompt, f"cap {cap_number} (veo) video_prompt")

    return {
        "chapter_number": cap_number,
        "image_prompt": image_prompt,
        "video_prompt": video_prompt,
        "subject_ref": subject_ref,
        "art_profile": profile_norm,
        "narration_anchor": anchor,
    }


def _validate_flux_cap(
    parsed: dict,
    narration: str,
    cap_number: int,
    n_expected: int,
) -> dict:
    """Valida output de un cap flux. Devuelve dict normalizado o raise."""
    if not isinstance(parsed, dict):
        raise VisualValidationError(
            f"cap {cap_number} (flux): output no es dict ({type(parsed).__name__})"
        )

    items = parsed.get("image_prompts")
    if not isinstance(items, list):
        raise VisualValidationError(
            f"cap {cap_number} (flux): falta lista 'image_prompts'"
        )
    if len(items) != n_expected:
        raise VisualValidationError(
            f"cap {cap_number} (flux): se esperaban EXACTAMENTE {n_expected} imgs, "
            f"llegaron {len(items)}. Generá un array con la cantidad exacta."
        )

    normalized: list[dict] = []
    last_pos = -1
    last_end = -1

    for i, item in enumerate(items, start=1):
        label = f"cap {cap_number} img #{i}"
        if not isinstance(item, dict):
            raise VisualValidationError(f"{label}: item no es dict")

        # 1. prompt
        prompt = item.get("prompt")
        if not isinstance(prompt, str) or not prompt.strip():
            raise VisualValidationError(f"{label}: prompt vacío o no string")
        prompt = prompt.strip()
        _validate_prompt_length_zona1(prompt, f"{label} prompt")

        # 2. art_profile
        profile = item.get("art_profile")
        if not isinstance(profile, str):
            raise VisualValidationError(
                f"{label}: art_profile no es string ({type(profile).__name__})"
            )
        profile_norm = profile.strip().upper()
        if profile_norm not in VALID_PROFILES:
            raise VisualValidationError(
                f"{label}: art_profile='{profile}' no está en el catálogo. "
                f"Válidos: {sorted(VALID_PROFILES)}"
            )

        # 3. subject_ref
        subject_ref = item.get("subject_ref")
        if not isinstance(subject_ref, str) or not subject_ref.strip():
            raise VisualValidationError(f"{label}: subject_ref vacío o no string")
        subject_ref = subject_ref.strip()

        # 4. emotional_rank
        rank = item.get("emotional_rank")
        if not isinstance(rank, str):
            raise VisualValidationError(
                f"{label}: emotional_rank no es string ({type(rank).__name__})"
            )
        rank_norm = rank.strip().upper()
        if rank_norm not in VALID_RANKS:
            raise VisualValidationError(
                f"{label}: emotional_rank='{rank}' inválido. "
                f"Válidos: {sorted(VALID_RANKS)}"
            )

        # 5. narration_anchor — substring exacto
        anchor = item.get("narration_anchor")
        pos = _validate_anchor_substring(anchor, narration, label)
        anchor = anchor.strip() if isinstance(anchor, str) else anchor
        anchor_end = pos + len(anchor)

        # 6. orden estricto
        if pos <= last_pos:
            raise VisualValidationError(
                f"{label}: anchor fuera de orden. Posición actual ({pos}) "
                f"<= posición del anchor previo ({last_pos}). "
                f"Los anchors deben aparecer en orden ESTRICTAMENTE creciente."
            )

        # 7. sin solapamiento
        if pos < last_end:
            raise VisualValidationError(
                f"{label}: anchor solapa con el anterior. Inicio actual ({pos}) "
                f"< final del anterior ({last_end}). Sin solapamiento."
            )

        last_pos = pos
        last_end = anchor_end

        # ─── Regla 2 (zona 1 limpia) ───
        # Reglas 14 (text-leakage) y 15 (paleta coherente) eliminadas en
        # chat 16: producían demasiados falsos positivos contra terminología
        # histórica legítima. m05 audita semánticamente con voting.
        _validate_zone1_clean(prompt, label)

        normalized.append({
            "prompt": prompt,
            "art_profile": profile_norm,
            "subject_ref": subject_ref,
            "emotional_rank": rank_norm,
            "narration_anchor": anchor,
        })

    return {
        "chapter_number": cap_number,
        "image_prompts": normalized,
    }


# ═══════════════════════════════════════════════════════════════
#  LLAMADA FLASH CON RETRY POR FEEDBACK
# ═══════════════════════════════════════════════════════════════

def _call_with_validation_retry(
    prompt: str,
    validator_fn,
    cap_number: int,
    max_attempts: int = MAX_RETRY_ATTEMPTS,
) -> dict:
    """Llama Flash, valida, reintenta con feedback si falla.

    El feedback incluye un CHECKLIST acumulativo de reglas críticas en cada
    retry. Razón (chat 14): el LLM tiende a hiper-enfocarse en el último
    error reportado y rompe reglas que ya cumplía. Ej: arregla regla 2
    pero parafrasea el anchor (rompe regla 9). El checklist le recuerda
    todo lo que tiene que mantener cumpliéndose simultáneamente.

    Args:
        prompt: prompt completo a enviar a Flash.
        validator_fn: callable(parsed_dict) -> dict normalizado o raise.
        cap_number: para logs.
        max_attempts: incluye el intento original. 2 = 1 intento + 1 retry.
    """
    attempt_prompt = prompt
    last_error: VisualValidationError | None = None

    for attempt in range(1, max_attempts + 1):
        raw = call_flash_json(attempt_prompt)
        try:
            return validator_fn(raw)
        except VisualValidationError as e:
            last_error = e
            if attempt == max_attempts:
                raise
            print(
                f"  [03] cap {cap_number}: validación falló intento {attempt}/{max_attempts}: "
                f"{str(e)[:120]}..."
            )
            feedback = f"""

═══════════════════════════════════════════════════
RETRY {attempt + 1}/{max_attempts} — TU INTENTO PREVIO FALLÓ
═══════════════════════════════════════════════════
PROBLEMA DETECTADO EN ESTE INTENTO:
{str(e)}

═══════════════════════════════════════════════════
CHECKLIST DE REGLAS CRÍTICAS — TODAS deben cumplirse a la vez
═══════════════════════════════════════════════════
Mientras arreglás el problema de arriba, NO rompas ninguna de estas:

  □ REGLA 2 — Zona 1 limpia. Cada `prompt` (y `image_prompt`/`video_prompt`
    en veo) contiene SOLO Subject + Action + Environment + framing
    permitido + marcador temporal. NO escribas: lighting words ('golden
    hour', 'warm light', 'dim', 'harsh sun'), palette words ('amber',
    'ochre', 'cyan', 'slate-blue'), style/optics words ('cinematic',
    'establishing shot' → usá 'wide shot', 'anamorphic', '35mm', 'film
    grain', 'bokeh').

  □ REGLA 7 — Largo zona 1: 80-260 chars (target 120-200). Pasarte de
    260 indica que metiste lighting/palette/style. La paleta y el grain
    los agrega el código DESPUÉS — no cuentan para tu rango.

  □ REGLA 9 — narration_anchor = SUBSTRING EXACTO de la narración del
    cap. Sin reformular, sin traducir, sin recortar palabras del medio,
    sin cambiar puntuación. Copiá literal.

  □ REGLA 10 — anchors en orden ESTRICTAMENTE creciente sobre la
    narración, SIN solapamiento (el final de un anchor < el inicio
    del siguiente).

  □ REGLA 11 — Cada prompt incluye al menos UN marcador temporal
    explícito ('1960s', 'vintage', 'period-correct', '1968', etc.).

CORREGÍLO. Reescribí el JSON COMPLETO respetando TODAS las reglas
de arriba a la vez. Generá la respuesta nueva desde cero, no parches
sobre la anterior.
"""
            attempt_prompt = prompt + feedback

    # Inalcanzable en teoría
    if last_error:
        raise last_error
    raise VisualValidationError(f"cap {cap_number}: retry exhausted sin error capturado")

# ═══════════════════════════════════════════════════════════════
#  PERSISTENCIA
# ═══════════════════════════════════════════════════════════════

def _persist(topic_id: str, data: dict) -> Path:
    """Escribe data/scripts/_steps/{topic_id}/03_visual.json."""
    step_dir = STEPS_DIR / topic_id
    step_dir.mkdir(parents=True, exist_ok=True)
    out_file = step_dir / "03_visual.json"
    out_file.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return out_file


# ═══════════════════════════════════════════════════════════════
#  STITCHING ZONA 2 (post-validación)
# ═══════════════════════════════════════════════════════════════
#
# Approach 2-zona: el LLM emite zona 1 cruda (subject+action+environment),
# el validador chequea que esté limpia, y acá se le concatena la zona 2
# (lighting/palette/optics/grain desde ART_PROFILES, y para Veo video_prompt
# el motion universal desde VEO_MOTION).
#
# Estas funciones se aplican DESPUÉS de _call_with_validation_retry y ANTES
# de persistir el cap_out. La validación del LLM no ve la zona 2 — solo
# valida que zona 1 esté limpia.

def _stitch_zone2_into_cap_veo(cap_out: dict) -> dict:
    """Stitchea zona 2 en un cap veo ya validado.

    image_prompt → ART_PROFILES[profile] al final (igual que Flux).
    video_prompt → ART_PROFILES[profile] + VEO_MOTION[profile] al final.

    El profile se lee de cap_out["art_profile"] (elegido por el LLM,
    validado por _validate_veo_cap). FASE 1: ya no se pasa default_profile
    externo — m03 elige profile por imagen también en caps veo.

    Args:
        cap_out: dict normalizado devuelto por _validate_veo_cap, con
            prompts en zona 1 cruda y art_profile elegido por el LLM.

    Returns:
        Mismo dict con image_prompt y video_prompt stitcheados.
    """
    profile = cap_out["art_profile"]
    cap_out["image_prompt"] = stitch_prompt(profile, cap_out["image_prompt"])
    cap_out["video_prompt"] = stitch_veo_video_prompt(profile, cap_out["video_prompt"])
    return cap_out


def _stitch_zone2_into_cap_flux(cap_out: dict) -> dict:
    """Stitchea zona 2 en un cap flux ya validado.

    Para cada item de image_prompts[]: agrega ART_PROFILES[item.art_profile]
    al final. Cada item respeta SU PROPIO art_profile (override por imagen
    permitido), no el default del cap.

    Args:
        cap_out: dict normalizado devuelto por _validate_flux_cap.

    Returns:
        Mismo dict con cada prompt stitcheado.
    """
    for item in cap_out.get("image_prompts", []):
        item["prompt"] = stitch_prompt(item["art_profile"], item["prompt"])
    return cap_out


# ═══════════════════════════════════════════════════════════════
#  FUNCIÓN PÚBLICA
# ═══════════════════════════════════════════════════════════════

def assign_visual_prompts(
    topic: dict,
    skeleton: dict,
    narration: dict,
) -> dict:
    """Genera image_prompts[] EN con narration_anchor por imagen.

    Args:
        topic     : dict (formato post módulo 00, con verified_facts y canonical_*).
        skeleton  : dict {topic_id, chapters[7]} (output 01a, sin _distribution_plan).
        narration : dict {topic_id, chapters[7] con narration} (output 01b).

    Returns:
        {
          "topic_id": str,
          "chapters": [
            {chapter_number, image_prompt, video_prompt, subject_ref,
             narration_anchor},                                   # caps 1, 7 (veo)
            {chapter_number, image_prompts: [...]},                # caps 2-6 (flux)
            ... (7 items total)
          ]
        }

    Raises:
        VisualValidationError si Flash devuelve algo fuera de contrato
        después de los retries permitidos.
        ValueError si los inputs están malformados.
    """
    topic_id = topic.get("id") or topic.get("topic_id")
    if not topic_id:
        raise ValueError("topic sin 'id' ni 'topic_id'")

    skel_chapters = skeleton.get("chapters") or []
    narr_chapters = narration.get("chapters") or []

    if len(skel_chapters) != EXPECTED_CHAPTER_COUNT:
        raise ValueError(
            f"skeleton tiene {len(skel_chapters)} caps (esperado {EXPECTED_CHAPTER_COUNT})"
        )
    if len(narr_chapters) != EXPECTED_CHAPTER_COUNT:
        raise ValueError(
            f"narration tiene {len(narr_chapters)} caps (esperado {EXPECTED_CHAPTER_COUNT})"
        )

    skel_by_n = {ch["chapter_number"]: ch for ch in skel_chapters}
    narr_by_n = {ch["chapter_number"]: ch for ch in narr_chapters}

    output_chapters: list[dict] = []

    for cap_n in range(1, EXPECTED_CHAPTER_COUNT + 1):
        sch = skel_by_n.get(cap_n) or {}
        nch = narr_by_n.get(cap_n) or {}

        narration_text = (nch.get("narration") or "").strip()
        if not narration_text:
            raise ValueError(f"cap {cap_n}: narración vacía")

        engine = (sch.get("render_engine") or "").strip().lower()

        if engine == "veo":
            print(f"  [03] cap {cap_n} (veo)  → llamando Flash...")
            prompt = _build_veo_prompt(topic, sch, narration_text)
            cap_out = _call_with_validation_retry(
                prompt,
                validator_fn=lambda parsed, n=narration_text, cn=cap_n: _validate_veo_cap(parsed, n, cn),
                cap_number=cap_n,
            )
            # Approach 2-zona: stitchear ART_PROFILES + VEO_MOTION en zona 1 cruda.
            cap_out = _stitch_zone2_into_cap_veo(cap_out)
            print(f"  [03] cap {cap_n} (veo)  ✓ image_prompt + video_prompt + anchor (stitched)")

        elif engine == "flux":
            n_images = _calculate_image_count(
                narration_text,
                chapter_number=cap_n,
                total_chapters=EXPECTED_CHAPTER_COUNT,
            )
            print(f"  [03] cap {cap_n} (flux) → {n_images} imgs (narr {len(narration_text)} chars, role={sch.get('role','?')}), llamando Flash...")
            prompt = _build_flux_prompt(topic, sch, narration_text, n_images)
            cap_out = _call_with_validation_retry(
                prompt,
                validator_fn=lambda parsed, n=narration_text, cn=cap_n, ni=n_images: _validate_flux_cap(parsed, n, cn, ni),
                cap_number=cap_n,
            )
            # Approach 2-zona: stitchear ART_PROFILES por item (cada item tiene su profile).
            cap_out = _stitch_zone2_into_cap_flux(cap_out)
            print(f"  [03] cap {cap_n} (flux) ✓ {len(cap_out['image_prompts'])} imgs validadas (stitched)")

        else:
            raise ValueError(
                f"cap {cap_n}: render_engine='{engine}' inválido (esperado 'veo' o 'flux')"
            )

        output_chapters.append(cap_out)

    output = {
        "topic_id": topic_id,
        "chapters": output_chapters,
    }

    _persist(topic_id, output)
    return output
