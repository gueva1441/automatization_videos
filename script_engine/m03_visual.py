"""
script_engine/m03_visual.py — Módulo 03: extractor visual.

TAREA ÚNICA: a partir de topic + skeleton (01a) + narración (01b),
generar los `image_prompts[]` en INGLÉS con `narration_anchor` explícito por imagen.

CONCEPTO CLAVE — `narration_anchor`:
  Cada imagen lleva pegada un substring EXACTO de la narración del cap. Esto:
    1. Define qué frase concreta ilustra la imagen (ata semánticamente).
    2. Define el orden cronológico de las imágenes en el array.
    3. Permite a fase2b sincronizar imagen↔audio por palabra (timestamps reales
       del sync_map de ElevenLabs).

APPROACH (chat 19): catálogo art_profiles desconectado del flujo activo.
  El LLM emite el prompt COMPLETO (subject + action + environment + marcador
  temporal + lighting/atmosphere específico de la escena), guiado por el
  system_instruction "documentary photography style, period-correct natural
  lighting per scene, slightly desaturated palette, no cinematic effects".
  Python ya NO concatena nada después: el prompt sale completo del LLM.

  La key "art_profile" del JSON output queda como "" (string vacío hardcoded)
  para mantener compat con consumidores aguas abajo (asset_manager, fase2b).

INPUT:
  topic     — dict (topics_db.json post módulo 00)
  skeleton  — dict {topic_id, chapters[7]} (output 01a, sin _distribution_plan)
  narration — dict {topic_id, chapters[7] con narration} (output 01b)

OUTPUT:
  {
    "topic_id": "uuid",
    "chapters": [
      // Cap 1 y 7 (veo) — prompt completo emitido por el LLM:
      {
        "chapter_number": 1,
        "image_prompt": "string EN completo (subject+action+env+temporal+lighting)",
        "video_prompt": "string EN completo (motion + ambient)",
        "subject_ref": "main_subject",
        "art_profile": "",
        "narration_anchor": "substring EXACTO de la narración del cap"
      },
      // Cap 2-6 (flux) — cada prompt completo:
      {
        "chapter_number": 2,
        "image_prompts": [
          {
            "prompt": "string EN completo",
            "art_profile": "",
            "subject_ref": "main_subject",
            "emotional_rank": "R1" | "R2" | "R3",
            "narration_anchor": "substring EXACTO de la narración del cap"
          },
          ... (N items, N = clamp(round(duration_sec/7) + bonus_position, 6, 18))
        ]
      },
      ...
    ]
  }

ESTRUCTURA INTERNA (1 archivo, funciones privadas + 1 pública):
  _calculate_image_count(cap_duration_sec, chapter_number, total_chapters)  → int
  _format_facts(verified_facts)                 → str
  _build_topic_block(topic)                     → str (header común)
  _build_rules_block()                          → str (11 reglas inviolables)
  _build_veo_prompt(topic, cap_data,
                    narration_text)             → str
  _build_flux_prompt(topic, cap_data,
                     narration_text, n_images)  → str
  _validate_prompt_length(prompt, label)        → None | raise
  _validate_no_text_leakage(prompt, label)      → None | raise
  _validate_veo_cap(parsed, narration, n)       → dict (raise si falla)
  _validate_flux_cap(parsed, narration, n,
                     n_expected)                → dict (raise si falla)
  _stitch_zone2_into_cap_veo(cap_out)           → dict (no-op desde chat 19)
  _stitch_zone2_into_cap_flux(cap_out)          → dict (no-op desde chat 19)
  _call_with_validation_retry(prompt, validator,
                               cap_n, sys_inst) → dict
  _persist(topic_id, data)                      → escribe 03_visual.json
  assign_visual_prompts(topic, skel, narr)      → dict       # PÚBLICA

LLAMADAS GEMINI: 7 (Flash, 1 por cap, secuencial). ~$0.010/video.

VALIDACIÓN DURA POST-FLASH (caps flux):
  1. len(image_prompts) == N exacto (fórmula duration_sec/7 + bonus_position, clamp 6-18).
  2. Cada item tiene los campos requeridos (prompt, subject_ref,
     emotional_rank, narration_anchor).
  3. emotional_rank ∈ {R1, R2, R3}.
  4. prompt en rango 120-400 chars (target 180-300).
  5. narration_anchor es substring EXACTO de la narración del cap.
  6. anchors en orden estrictamente creciente.
  7. anchors sin solapamiento.

VALIDACIÓN DURA POST-FLASH (caps veo):
  1. Existen image_prompt, video_prompt, subject_ref, narration_anchor.
  2. image_prompt y video_prompt en rango 120-400 chars (target 180-300).
  3. narration_anchor es substring EXACTO de la narración del cap.

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
from nicho_config import get_active_nicho


# ═══════════════════════════════════════════════════════════════
#  SYSTEM INSTRUCTION (documentary photography style — chat 19)
# ═══════════════════════════════════════════════════════════════
#
# Reemplaza el catálogo ART_PROFILES como guía estética del LLM. El LLM
# ya no recibe un catálogo de profiles ni elige un art_profile por imagen:
# emite el prompt completo (subject + action + environment + marcador
# temporal + lighting/atmosphere inline) bajo este system_instruction.

SYSTEM_INSTRUCTION_VISUAL = """You are a Literal Translator. You convert Spanish narrative prose into pure
physical matter prompts for Flux 2 Pro, optimized for vertical TikTok/Shorts retention.

CRITICAL — OUTPUT LANGUAGE:
ALL prompts MUST be in ENGLISH. Flux thinks in English. Spanish in the prompt
produces Latin script gibberish on surfaces in the image.

OUTPUT: JSON array of N objects. Each object has ONE field `prompt` (plus the
metadata fields defined in user prompt). The `prompt` field is a single
natural-language sentence following Flux 2 Pro best practices.

PROMPT STRUCTURE (CRITICAL — Flux 2 Pro spec):
The `prompt` field MUST follow this priority order:
  Subject (with physical descriptors integrated) → Action → Setting → Mood
Flux 2 Pro weights tokens at the START heaviest. Put the main human/subject
FIRST, never bury it after long environmental descriptions.

PROMPT LENGTH:
Target 30-80 words per prompt. Hard maximum 120 words.

HARD RULES:

1. ETHNIC DEFAULT FOR HUMANS:
   For any human subject, integrate ethnicity into the subject phrase at the
   START. DEFAULT = local ethnicity of the topic's GEO (e.g. Cameroonian for
   Lake Nyos, Soviet/Russian for Chernobyl). Use a different ethnicity ONLY
   if the narration explicitly names the subject as a foreigner (e.g. the
   narration says "the USGS team arrived from Washington").
   ✓ "A Cameroonian woman in her 40s, dark skin, weathered features, wearing
      a 1980s rural cotton wrap, ..."
   ✓ "A Soviet engineer in his 50s, pale Slavic features, in a grey wool
      uniform, ..."
   (If the narration explicitly says American/French/etc, use that ethnicity
   instead. Default = local.)

2. POSITIVE DESCRIPTIONS ONLY (Flux 2 has no negative prompts):
   Describe what you WANT to see. Never describe what you DON'T want.
   ✓ "clean concrete wall" (not "wall without text")
   ✓ "empty street" (not "street with no people")
   ✓ "sharp focus throughout" (not "no blur")
   For surfaces that could have text but shouldn't: simply do not mention
   text. Do not write "no readable text", "no inscriptions", "no labels",
   or any equivalent negative phrasing.

3. PHYSICAL DESCRIPTIONS ONLY (no abstract roles, no proper names):
   ✗ "an astronaut", "an engineer", "a victim", "a doctor"
   ✓ specific physical appearance (ethnicity + age + clothing material + action)
   ✗ Proper names of missions, vehicles, agencies (regardless of how they
     appear in the narration)
   ✓ Describe physically by materials, shape, color, era cues
   ✗ Letter/number model codes for equipment
   ✓ Describe equipment by visual characteristics

4. PERIOD-ACCURATE DETAILS:
   Identify the year/era from the narration. Anchor every physical detail to
   that period (clothing materials, equipment, vehicles, technology).
   Phrasing: "1980s industrial control panel with analog dials and bakelite
   switches", not generic descriptions.
   PRESENT-DAY / MODERN scenes (when the narration is in the present): anchor
   to a concrete recent decade (2010s-2020s) with TANGIBLE, physical
   technology — real monitors, printed documents, physical lab equipment.
   NEVER holographic displays, floating or projected UI, glowing 3D interfaces,
   or sci-fi aesthetics. "Modern" means a real present-day room, not science
   fiction.

5. SAFE PORTRAYAL OF DISASTER/VIOLENCE (Flux 2 + Veo content filters):
   Disaster narratives can be conveyed through atmosphere, not through
   depicting injury or death directly.
   For violent events: describe environmental consequences (displaced
   materials, scattered debris, structural damage).
   For human suffering: describe physical posture and exhaustion (tired
   expression, resting head against wall, eyes closed in fatigue, hands
   shaking slightly, slow breathing).
   IMPLIED DEATH — people, animals, or mass casualties: do NOT depict bodies,
   motionless figures, or the aftermath of death. Even still or lying figures
   trip the content filter. Depict the CALM BEFORE instead: living beings at
   peace, an ambient quiet scene (a peaceful village at dusk, livestock
   grazing at dawn, soft lamplight through a window). The narration carries
   the death; the image stays alive and calm.
   Avoid: graphic injury, visible distress symptoms, anything depicting the
   moment of harm itself.

6. PHYSICAL TRANSLATION OF METAPHORS:
   If the narration uses a metaphor (e.g. "the silent killer"), identify the
   underlying physical event (e.g. "a colorless dense gas creeping over the
   ground") and describe THAT.

7. NO TEXT TO BE READ:
   If the narration mentions a spoken word or named thing, do NOT render the
   word as visible text in the image. Describe the speaker or object
   physically. Surfaces in the image should be described as plain or
   weathered, not "with text".
   Screens, monitors, displays, data projections and control panels: describe
   them as abstract glowing patterns, soft indistinct light, or blurred
   surfaces — never with data, readings, numbers, words, labels, place names
   or country names. A "data projection" or "lab display" must be rendered as
   abstract light, not legible information.

8. RETENTION FOR VERTICAL FORMAT (TikTok/Shorts, 3s decision window):
   - One dominant subject, clearly visible
   - Subject doing a specific action, not standing still
   - Dense visual texture (materials, surfaces, weather)
   - Compositions readable at a glance

9. DIVERSITY across the N prompts:
   Each prompt must describe DIFFERENT subject matter (different framing,
   different focus, different location detail). No near-identical images.

JSON only. No markdown. No preamble.
"""


# ═══════════════════════════════════════════════════════════════
#  PATHS Y CONSTANTES
# ═══════════════════════════════════════════════════════════════

STEPS_DIR: Path = DATA_DIR / "scripts" / "_steps"

EXPECTED_CHAPTER_COUNT = 7
VEO_CHAPTERS = (1, 7)
FLUX_CHAPTERS = (2, 3, 4, 5, 6)

# 7.0s ≈ DepthFlow activo (validado a 6s en test_movements_v12; gradiente
# físico lineal: 1 ciclo / duración del clip vía loop=True).
# A 7s: 1 ciclo / 7s = 51°/seg — margen de seguridad sobre los 60°/seg de 6s.
SECONDS_PER_IMAGE_TARGET = 7.0
MIN_IMAGES_FLUX = 6
MAX_IMAGES_FLUX = 18   # subido de 12 en chat 27 PR 3, acorde a backlog #176

# Híbrido Veo+Flux ch01/ch07 (chat 29 #175).
# Duración nominal del clip Veo 3.1 Lite (fal.ai). El clip real puede
# variar ±0.2s; fase2b mide la duración exacta del MP4 generado y
# calcula el segmento Flux como audio_duration - veo_actual_duration.
VEO_CLIP_DURATION_SEC = 8.0

# Mínimo y máximo de supplementals por cap veo. MIN=4 fuerza que el
# híbrido SIEMPRE aplique (sin esto, caps cortos volverían al loop).
MIN_FLUX_EXTRAS = 4
MAX_FLUX_EXTRAS = 14

# Bonus por posición narrativa del cap (development only).
# Preservados del cálculo anterior. Caps first_third (intro) y last_third
# (climax) reciben +1 img.
BONUS_POSITION_FIRST_THIRD = 1
BONUS_POSITION_LAST_THIRD = 1
BONUS_POSITION_MIDDLE = 0

# Rango de chars para los prompts EN.
# Refactor v6 chat 27: el prompt final = ANCLA_GLOBAL (~150 chars) + 3 slots
# del Traductor. Empíricamente los 3 slots combinados caen consistentemente
# en 350-550 chars (sujeto verboso por reglas anti-text + anti-acronym +
# anti-abstract-roles). Budget para los slots = PROMPT_MAX - ancla = 550 chars
# con PROMPT_MAX=700, dando headroom realista al LLM en el 1er intento.
# Caps veo (1, 7) siguen formato viejo y no requieren ensamblaje.
PROMPT_MIN_CHARS = 120
PROMPT_MAX_CHARS = 700

VALID_RANKS = frozenset({"R1", "R2", "R3"})

MAX_RETRY_ATTEMPTS = 3
# 1 intento original + 2 retries con feedback enriquecido. Cap más cargado
# (10 imgs sobre narr ~2000 chars) puede necesitar la 3ra vuelta cuando
# falla por anchor parafraseado en la última img. Costo: ~$0.001 extra
# en peor caso. Comportamiento normal sigue siendo 0-1 retries.

# ─── Validación regla 3 (anti-text-leakage) ───
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

# ═══════════════════════════════════════════════════════════════
#  EXCEPCIÓN
# ═══════════════════════════════════════════════════════════════

class VisualValidationError(ValueError):
    """Output del Flash no cumple el contrato del módulo 03."""


# ═══════════════════════════════════════════════════════════════
#  CÁLCULO DE N (cantidad de imgs por cap flux)
# ═══════════════════════════════════════════════════════════════

def _calculate_image_count(
    cap_duration_sec: float,
    chapter_number: int = None,
    total_chapters: int = 7,
) -> int:
    """
    Cantidad adaptativa de imgs por cap según DURACIÓN REAL del audio TTS.

    PR 3 chat 27: reemplaza el cálculo legacy basado en len(narration)/CHARS_PER_IMAGE
    que era proxy de duración. Ahora usa duration_sec del sync_map de ElevenLabs.

    Args:
        cap_duration_sec: duración del audio del cap en segundos
            (de sync_map["chapters"][i]["duration_sec"]).
        chapter_number: número del cap (1..total_chapters). Si None, no aplica
            bonus de posición.
        total_chapters: típicamente 7 (1 hook + 5 development + 1 outro).

    Returns:
        n_images: int en rango [MIN_IMAGES_FLUX, MAX_IMAGES_FLUX].
    """
    base = round(cap_duration_sec / SECONDS_PER_IMAGE_TARGET)

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
            # else: middle, bonus = 0

    n = base + bonus_position
    return max(MIN_IMAGES_FLUX, min(MAX_IMAGES_FLUX, n))


def _calculate_flux_extras_count(cap_audio_duration_sec: float) -> int:
    """
    Cantidad de Flux supplementals para un cap híbrido veo (chat 29 #175).

    El cap audio dura ~45-75s. Veo ocupa VEO_CLIP_DURATION_SEC=8s del cap.
    El resto se cubre con Flux DepthFlow. La fórmula es la misma que
    _calculate_image_count para flux puros, pero sin bonus de posición y
    clampeada al rango [MIN_FLUX_EXTRAS, MAX_FLUX_EXTRAS].
    """
    flux_segment_sec = max(0.0, cap_audio_duration_sec - VEO_CLIP_DURATION_SEC)
    n = round(flux_segment_sec / SECONDS_PER_IMAGE_TARGET)
    return max(MIN_FLUX_EXTRAS, min(MAX_FLUX_EXTRAS, n))


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
            "  rol+aspecto+era genérico (NUNCA por nombre — ver regla 4)."
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
    """Las 11 reglas inviolables. NOTA (chat 32): hoy SOLO las inyecta
    _build_veo_prompt; el path Flux (_build_flux_prompt, refactor v6 chat 27)
    se apoya en SYSTEM_INSTRUCTION_VISUAL. Mantener sincronizado el criterio
    de ambos."""
    return f"""1. **PROMPT EN INGLÉS.** Sin excepciones. Flux/Veo no entienden español.

2. **NO INVENTAR DATOS DE LUGAR/FECHA.** Cifras, fechas y lugares solo
   pueden venir de verified_facts [F##] o de la narración del cap.
   (Esta regla es para datos NO-PERSONAS. Para personas ver regla 4.)

3. **NO TEXTO/NÚMEROS/LETRAS VISIBLES EN LAS IMÁGENES.** Esto incluye:
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
   ✓ BIEN: "abstract technical blueprint with indistinct mechanical schematics"
   ✓ BIEN: "vintage sonar display with glowing abstract pulses"
   ✓ BIEN: "folded period newspaper, headline area blurred and indistinct"

   REGLA DE ORO: si tu prompt nombra cualquier sello/pantalla/papel/cartel,
   describí la superficie en POSITIVO como "indistinct", "blurred",
   "abstract" u "obscured". Flux/Veo IGNORAN los negativos tipo "no readable
   text" (AP2) — no los uses, no sirven. NUNCA pongas la palabra que está
   dentro del sello/cartel/pantalla, ni siquiera entre comillas.

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

4. **PROHIBIDO ESCRIBIR NOMBRES PROPIOS DE PERSONAS** en `prompt` o
   `video_prompt`, INCLUSO si el nombre aparece en verified_facts o en
   la narración del cap.

   Para personas que figuran en el bloque "PERSONAS DOCUMENTADAS"
   (sección DATOS VISUALES CANÓNICOS arriba): usá DIRECTAMENTE su
   `appearance_canon` tal cual está escrito.

   Para personas no listadas: describí rol+aspecto+era+etnia coherente
   con el GEO del topic (ej. "a middle-aged Cameroonian villager in
   1980s rural attire"). La etnia es OBLIGATORIA si hay humanos
   visibles, salvo que el sujeto sea explícitamente extranjero al GEO
   (ej. "an American researcher visiting Cameroon").

   ✗ MAL: "Commander Francis Slattery on the bridge..."
   ✗ MAL: "Dr. Eric Saint examining a patient..."
   ✓ BIEN: "a mid-30s American naval officer in 1960s U.S. Navy service
            uniform, with an authoritative demeanor, on the control bridge"
            (usando appearance_canon de PERSONAS DOCUMENTADAS)

5. **NO METADATOS TÉCNICOS NI PARÁMETROS DE FORMATO.**
   Prohibido en tu output:
   - Cámaras / sensores: "shot with Sony A7", "Canon R5", "Hasselblad",
     "ARRI Alexa", "Red Komodo".
   - Specs ópticas: "f/2.8", "f/1.4", "ISO 400", "1/250 shutter".
   - Aspect ratios y formatos: "--ar 16:9", "16:9", "4:3", "vertical 9:16".
   - Calidad / resolución: "8k", "4k", "HDR", "RAW", "high resolution".
   - Engine tags: "Midjourney style", "Stable Diffusion", "DALL-E".
   - Prompt-engineering tokens: "(word:1.2)", "[word]", negative-prompt
     syntax, seed values, LoRA weights, "::weight".

   (El estilo general — documentary photography, period-correct natural
    lighting, slightly desaturated palette — viene del system_instruction.
    Vos decidís el lighting específico de cada escena dentro de ese marco:
    'harsh midday sun', 'overcast afternoon', 'dim interior with single
    bulb', 'foggy morning', etc.)

6. **LARGO DE PROMPT — target 180-300 chars, máximo 400, mínimo 120.**
   El prompt incluye Subject + Action + Environment + marcador temporal +
   lighting/atmosphere específico de la escena. NO contar palabras,
   contar caracteres. Pasarte de 400 indica que metiste metadatos técnicos
   (regla 5) o redundancia.

7. **ANCHORS = SUBSTRING EXACTO.** El narration_anchor debe ser una
   porción literal y contigua de la narración del cap. Sin reformular,
   sin agregar puntuación, sin traducir, sin recortar palabras.

8. **ANCHORS EN ORDEN.** Cada anchor debe aparecer DESPUÉS del anterior
    en la narración. Sin solapamiento (el final de uno < el inicio del
    siguiente). El array de imgs es la línea de tiempo del cap.

9. **ANCLAJE TEMPORAL OBLIGATORIO EN CADA PROMPT.** Cada `prompt`
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

10. **NO METÁFORAS NI ABSTRACTOS NO-VISUALES EN EL PROMPT.**
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

11. **FIDELITY AL ANCHOR.** El prompt ilustra lo que el anchor describe,
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
    cap_audio_duration_sec: float,
    n_flux_extras: int,
    veo_position: str,
    veo_zone_chars: int,
) -> str:
    """
    Prompt para caps veo HÍBRIDOS (chat 29 #175): 1 par image/video_prompt Veo
    + N supplemental_image_prompts Flux que cubren el resto del audio del cap.

    Args:
        cap_audio_duration_sec: duración total del audio del cap (sync_map).
        n_flux_extras: cantidad de supplementals a pedir
            (calculado por _calculate_flux_extras_count).
        veo_position: "start" si role=="hook" (Veo cubre primeros 8s),
            "end" si role=="reveal_outro" (Veo cubre últimos 8s).
        veo_zone_chars: cantidad de chars de la narración que cubre el clip
            Veo (chat 31 #219 — aproximación lineal chars/segundos). Usado
            para indicarle al LLM la zona literal en la que debe estar el
            anchor del Veo y la zona disjunta donde van los supplementals.
    """
    cap_n = cap_data["chapter_number"]
    role = cap_data.get("role") or "?"
    cap_title = cap_data.get("title") or "(sin título)"
    bullets_block = _format_bullets(cap_data.get("bullets") or [])

    topic_block = _build_topic_block(topic)
    visual_canon_block = _format_visual_canon_block(topic)
    rules_block = _build_rules_block()

    remaining_sec = max(0.0, cap_audio_duration_sec - VEO_CLIP_DURATION_SEC)

    # Chat 31 #219: zonas literales de chars en la narración.
    narration_len = len(narration_text)
    if veo_position == "start":
        veo_zone_lo, veo_zone_hi = 0, veo_zone_chars
        supps_zone_lo, supps_zone_hi = veo_zone_chars, narration_len
    else:  # "end"
        veo_zone_lo = narration_len - veo_zone_chars
        veo_zone_hi = narration_len
        supps_zone_lo, supps_zone_hi = 0, narration_len - veo_zone_chars

    veo_zone_text = narration_text[veo_zone_lo:veo_zone_hi]
    supps_zone_text = narration_text[supps_zone_lo:supps_zone_hi]

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
REGLAS INVIOLABLES
═══════════════════════════════════════════════════
{rules_block}

═══════════════════════════════════════════════════
ESPECÍFICO PARA VEO (este cap)
═══════════════════════════════════════════════════

Este cap es {role}, render_engine=veo. Generás:
- 1 image_prompt: la escena completa (Subject + Action + Environment +
  marcador temporal + lighting/atmosphere específico de la escena).
  120-400 chars EN, target 180-300. El lighting lo decidís vos según el
  contenido de la escena, dentro del marco "documentary photography,
  period-correct natural lighting, slightly desaturated palette" del
  system_instruction.
- 1 video_prompt: cómo se mueve el SUJETO y el AMBIENT específico de la
  escena (120-400 chars EN, target 180-300). Describe MOVIMIENTO concreto:
  movimiento del sujeto (coat swaying, eyes blinking, hair in wind),
  camera arc específico al cap (slow push in al rostro, slow pull out),
  y ambient particular de la escena (smoke from cigarette, water dripping,
  dust drifting). PROHIBIDO cuts, jumps, fast cuts, zoom rapid.
- 1 subject_ref: identificador del sujeto. "main_subject" si es el
  protagonista; otros nombres si la escena no tiene protagonista humano
  (ej. "establishing_shot", "interior_scene", "landscape_view").
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
HÍBRIDO VEO + FLUX SUPPLEMENTALS (chat 29 #175)
═══════════════════════════════════════════════════

Este cap dura ~{cap_audio_duration_sec:.0f}s de audio. El clip Veo cubre
SOLO {VEO_CLIP_DURATION_SEC:.0f}s del cap. El resto ({remaining_sec:.0f}s) se
cubre con {n_flux_extras} imágenes Flux estáticas animadas con DepthFlow.

POSICIÓN DEL VEO EN EL CAP: {veo_position}

La narración del cap tiene {narration_len} caracteres totales. El clip Veo
cubre ~{VEO_CLIP_DURATION_SEC:.0f}s de audio, lo que equivale a ~{veo_zone_chars}
caracteres de la narración (aproximación lineal chars/segundos).

ZONAS LITERALES DE LA NARRACIÓN:

[ZONA VEO]  (chars [{veo_zone_lo}..{veo_zone_hi}], usar SOLO para el anchor del Veo):
\"\"\"
{veo_zone_text}
\"\"\"

[ZONA SUPPLEMENTALS]  (chars [{supps_zone_lo}..{supps_zone_hi}], usar SOLO para los anchors de los supplementals):
\"\"\"
{supps_zone_text}
\"\"\"

REGLAS DEL HÍBRIDO (estrictas, validador rechaza si se violan):
1. El `narration_anchor` del Veo DEBE ser substring exacto de [ZONA VEO]
   arriba. NO mezclar con texto de [ZONA SUPPLEMENTALS].
2. Cada `narration_anchor` de supplemental DEBE ser substring exacto de
   [ZONA SUPPLEMENTALS] arriba. NO mezclar con texto de [ZONA VEO].
3. Los anchors de supplementals DEBEN estar en orden cronológico estricto
   ascendente (cada anchor aparece después del anterior en el texto).
4. Los anchors de supplementals NO se solapan entre sí.
5. Cada supplemental.prompt sigue las mismas reglas visuales que un cap
   flux puro (EN, marcador temporal, lighting de escena, sin metadata).
6. Cantidad EXACTA de supplementals: {n_flux_extras}.

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

✓ CORRECTO (cap hook documental, marcador temporal explícito + lighting de escena):
{{
  "image_prompt": "An elderly miner in dusty 1960s work clothes standing alone on a deserted outback road, vast emptiness around the figure, distant period-correct mining headframe barely visible on the horizon, harsh midday outback sun, drifting fine red dust, wide shot of the open terrain",
  "video_prompt": "The miner's coat swaying gently in the wind, fine dust particles drifting slowly through the air, distant heat shimmer warping the horizon line, the figure standing still while the desert breathes around him",
  "subject_ref": "main_subject",
  "narration_anchor": "Más de 2,000 personas perdieron la vida en Wittenoom, un pueblo minero borrado de los mapas en 2007"
}}

✓ CORRECTO (cap reveal, persona de DOCUMENTED_PEOPLE, lighting de interior):
{{
  "image_prompt": "A mid-30s American naval officer in 1960s U.S. Navy service uniform on the cramped control bridge of a 1968 Skipjack-class submarine, focused authoritative expression, period-correct analog instruments around him, brass detail visible on the bulkhead behind, dim interior lit by warm overhead bulbs and the glow of analog gauges",
  "video_prompt": "Slow push in toward the officer's face, instrument needles flickering subtly, faint vapor drifting through the cramped compartment, his shoulders rising slowly with controlled breathing",
  "subject_ref": "main_subject",
  "narration_anchor": "el comandante revisó por última vez la posición del submarino, sin saber que esa sería la última transmisión que enviaría al mando"
}}
   ↑ Nota: usa el `appearance_canon` de PERSONAS DOCUMENTADAS sin nombre,
     y ancla temporalmente con "1960s", "1968", "period-correct". El
     image_prompt incluye el lighting específico de la escena (dim interior
     lit by warm overhead bulbs and the glow of analog gauges), elegido por
     el contenido (interior submarino) dentro del marco documental.

✗ INCORRECTO (varios errores):
{{
  "image_prompt": "John Smith born 1932 mining at Wittenoom in 1956",   ← inventó nombre, nombre propio prohibido
  "video_prompt": "Fast cuts between three locations, dramatic zoom",   ← prohibido cuts/fast/zoom rapid
  "subject_ref": "main_subject",
  "narration_anchor": "más de dos mil personas murieron"   ← reformulado, no substring exacto
}}

═══════════════════════════════════════════════════
FORMATO DE OUTPUT (JSON estricto, nada más)
═══════════════════════════════════════════════════

{{
  "image_prompt": "string EN, 120-400 chars (target 180-300) — Subject + Action + Environment + marcador temporal + lighting/atmosphere de la escena",
  "video_prompt": "string EN, 120-400 chars (target 180-300) — motion del sujeto + camera arc + ambient específico",
  "subject_ref": "main_subject",
  "narration_anchor": "string ES (substring EXACTO de la zona Veo: primeros 8s si position=start, últimos 8s si position=end)",
  "supplemental_image_prompts": [
    {{
      "prompt": "string EN, 120-400 chars — formato Flux puro (Subject + Action + Environment + marcador temporal + lighting)",
      "narration_anchor": "string ES (substring EXACTO de la zona NO-Veo, orden cronológico)"
    }}
    // ... EXACTAMENTE {n_flux_extras} items, NO MÁS NO MENOS
  ]
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
    """
    Refactor v6 chat 27: el LLM recibe TRADUCTOR_SYSTEM y emite JSON con N items,
    cada uno con 3 slots (sujeto_fisico, anclas_temporales_o_tecnicas,
    modificador_de_escena) + narration_anchor + subject_ref + emotional_rank.

    El ensamblaje del prompt final (ANCLA_GLOBAL + slots) se hace DESPUÉS
    del LLM en assign_visual_prompts, no acá. Esta función solo construye
    el user prompt que va al Flash.

    Source of truth de las 9 hard rules del Traductor: test_lab_v6.py.
    Source of truth del Ancla Global: nicho_config.NICHO_DARK_HISTORY.
    """
    cap_n = cap_data["chapter_number"]
    role = cap_data.get("role") or "development"
    cap_title = cap_data.get("title") or "(sin título)"

    return f"""Narration (Spanish, for context only — emit JSON in English):

{narration_text}

CAP {cap_n} — {role}, title: {cap_title}

Generate EXACTLY {n_images} prompts as JSON array. Each item MUST have:

{{
  "prompt": "string EN — single natural-language sentence, 30-80 words, following PROMPT STRUCTURE in system instruction (Subject with physical descriptors integrated → Action → Setting → Mood). Subject FIRST.",
  "subject_ref": "main_subject" | "establishing_shot" | "interior_scene" | etc,
  "emotional_rank": "R1" | "R2" | "R3",
  "narration_anchor": "EXACT substring of the Spanish narration above"
}}

DISTRIBUTION OF narration_anchors (CRITICAL — read twice):
- Partition the Spanish narration mentally into {n_images} segments in order.
- Each anchor covers ONE segment in chronological order.
- Anchor of item 1 = first segment. Anchor of item N = last segment.
- Anchors don't need to cover 100% of text (transitions can be skipped),
  BUT covered segments must be in strict ascending order, non-overlapping.
- Min 25 chars, max 200 chars, target 60-120 chars.

DISTRIBUTION OF emotional_rank:
- 1-2 items R1 (peak of cap: closing, revelation, biggest impact).
- 2-3 items R2 (action, strong transition, person in tension).
- Rest R3 (descriptive scene, context, ambience).

JSON only. No markdown. No preamble.
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


def _validate_no_text_leakage(prompt: str, label: str) -> None:
    """Regla 3: detecta patrones de instrucción de texto en imagen.

    El LLM a veces esquiva la regla 3 del prompt con eufemismos tipo
    "blurred area where name was". Acá los detectamos por regex.
    Raise VisualValidationError con mensaje educativo si encuentra match.
    """
    prompt_lc = prompt.lower()
    for pattern in TEXT_LEAKAGE_PATTERNS:
        m = re.search(pattern, prompt_lc, re.IGNORECASE)
        if m:
            matched_fragment = m.group(0)
            raise VisualValidationError(
                f"{label}: regla 3 violada (text-leakage detectado).\n"
                f"  FRAGMENTO PROBLEMÁTICO: '{matched_fragment}'\n"
                f"  CAUSA: el prompt indica al image generator que dibuje "
                f"texto/nombres aunque sea blurred o indistinct.\n"
                f"  REGLA 3: el prompt NO debe describir áreas, sellos, "
                f"carteles ni espacios que 'tenían texto'. Si querés mostrar "
                f"ausencia, describí un OBJETO sin texto (poste vacío sin "
                f"cartel, mapa con manchas de tiempo en lugar de área "
                f"borrada con nombre).\n"
                f"  Reescribí el prompt eliminando cualquier referencia a "
                f"'name', 'text', 'label', 'words' o lo equivalente."
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


def _normalize_for_anchor_match(text: str) -> tuple[str, list[int]]:
    """Normaliza texto para match tolerante de anchors (chat 32, #205).

    Colapsa runs de whitespace a un solo espacio y elimina marcadores de pausa
    "..." / "…", para que un anchor que el LLM "limpió" (recortó la pausa o
    colapsó un salto de párrafo) siga matcheando una porción REAL de la
    narración.

    Devuelve (texto_normalizado, index_map) donde index_map[i] = índice en el
    texto ORIGINAL del char i del texto normalizado. Permite traducir una
    posición encontrada en el normalizado de vuelta al original (necesario
    porque el offset se usa para orden/overlap en los validadores de cap).
    """
    norm_chars: list[str] = []
    index_map: list[int] = []
    i = 0
    n = len(text)
    prev_was_space = False
    while i < n:
        ch = text[i]
        # Eliminar marcadores de pausa: "..." (3+) o "…" (carácter único)
        if ch == "." and text[i:i + 3] == "...":
            j = i
            while j < n and text[j] == ".":
                j += 1
            i = j
            continue
        if ch == "…":  # "…"
            i += 1
            continue
        if ch.isspace():
            if not prev_was_space:
                norm_chars.append(" ")
                index_map.append(i)
                prev_was_space = True
            i += 1
            continue
        norm_chars.append(ch)
        index_map.append(i)
        prev_was_space = False
        i += 1
    return "".join(norm_chars), index_map


def _validate_anchor_substring(
    anchor: str,
    narration: str,
    label: str,
) -> tuple[int, int]:
    """Valida que anchor sea una porción real de narration. Devuelve
    (pos, end) en coordenadas del texto ORIGINAL.

    `end` es el final REAL del span en el original — calculado desde el
    index_map en la rama tolerante (NO `pos + len(anchor)`, porque el anchor
    que mandó el LLM puede ser más corto que el span original si recortó una
    pausa "..." o colapsó un "\\n\\n"). Los consumidores usan `end` para el
    chequeo de overlap; recalcular con len(anchor) da falsos solapamientos.

    Chat 32 (#205): match TOLERANTE a whitespace y a "..." (pausas). Primero
    intenta match exacto (camino feliz, sin costo). Si falla, reintenta sobre
    versiones normalizadas y traduce la posición de vuelta al texto original.
    El anchor sigue obligado a ser una porción REAL: la normalización no toca
    el contenido alfabético, así que un anchor parafraseado NO matchea.
    """
    if not isinstance(anchor, str) or not anchor.strip():
        raise VisualValidationError(f"{label}: anchor vacío o no string")

    # 1. Camino feliz: match exacto byte-a-byte. El anchor es literal, así que
    #    su largo coincide con el span real.
    pos = narration.find(anchor)
    if pos >= 0:
        return pos, pos + len(anchor)

    # 2. Match tolerante: normalizar ambos lados, buscar, re-mapear offset.
    norm_narr, index_map = _normalize_for_anchor_match(narration)
    norm_anchor, _ = _normalize_for_anchor_match(anchor)
    norm_anchor = norm_anchor.strip()
    if norm_anchor:
        npos = norm_narr.find(norm_anchor)
        if npos >= 0:
            # npos es índice en norm_narr → traducir al original vía index_map.
            # El inicio mapea directo; el final usa el ÚLTIMO char del span
            # normalizado → su posición original + 1 (final exclusivo).
            start_orig = index_map[npos]
            last_char_norm_idx = npos + len(norm_anchor) - 1
            end_orig = index_map[last_char_norm_idx] + 1
            return start_orig, end_orig

    # 3. Falla real: el anchor no es una porción de la narración ni tolerando
    #    pausas/espacios. Guiar el retry con el fragmento más parecido.
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
            f"  Regla 7: el anchor debe ser una porción literal y contigua de la narración. "
            f"NO traducir, NO reformular, NO recortar palabras intermedias."
        )
    raise VisualValidationError(
        f"{label}: el narration_anchor NO es substring exacto de la narración. "
        f"Anchor recibido: '{anchor_preview}'. "
        f"Debe ser una porción literal y contigua de la narración del cap."
    )


def _validate_veo_cap(
    parsed: dict,
    narration: str,
    cap_number: int,
    veo_position: str = "start",
) -> dict:
    """Valida output de un cap veo HÍBRIDO (chat 29 #175). Devuelve dict normalizado.

    Schema esperado: 1 par image/video_prompt Veo + N supplemental_image_prompts
    Flux. Los supplementals cubren el resto del audio del cap.

    Args:
        veo_position: "start" o "end". Se propaga al output para que fase2b
            sepa en qué extremo del cap montar el clip Veo.
    """
    if not isinstance(parsed, dict):
        raise VisualValidationError(
            f"cap {cap_number} (veo): output no es dict ({type(parsed).__name__})"
        )

    image_prompt = parsed.get("image_prompt")
    if not isinstance(image_prompt, str) or not image_prompt.strip():
        raise VisualValidationError(f"cap {cap_number} (veo): image_prompt vacío o no string")
    image_prompt = image_prompt.strip()
    _validate_prompt_length(image_prompt, f"cap {cap_number} (veo) image_prompt")

    video_prompt = parsed.get("video_prompt")
    if not isinstance(video_prompt, str) or not video_prompt.strip():
        raise VisualValidationError(f"cap {cap_number} (veo): video_prompt vacío o no string")
    video_prompt = video_prompt.strip()
    _validate_prompt_length(video_prompt, f"cap {cap_number} (veo) video_prompt")

    subject_ref = parsed.get("subject_ref")
    if not isinstance(subject_ref, str) or not subject_ref.strip():
        raise VisualValidationError(f"cap {cap_number} (veo): subject_ref vacío o no string")
    subject_ref = subject_ref.strip()

    anchor = parsed.get("narration_anchor")
    veo_anchor_pos, veo_anchor_end = _validate_anchor_substring(anchor, narration, f"cap {cap_number} (veo)")
    anchor = anchor.strip()

    # ─── Validación supplementals (chat 29 #175) ───
    supplementals = parsed.get("supplemental_image_prompts")
    if not isinstance(supplementals, list):
        raise VisualValidationError(
            f"cap {cap_number} (veo): supplemental_image_prompts no es lista"
        )
    if len(supplementals) < MIN_FLUX_EXTRAS or len(supplementals) > MAX_FLUX_EXTRAS:
        raise VisualValidationError(
            f"cap {cap_number} (veo): {len(supplementals)} supplementals "
            f"(esperado {MIN_FLUX_EXTRAS}-{MAX_FLUX_EXTRAS})"
        )

    validated_supplementals: list[dict] = []
    last_pos = -1
    last_end = -1
    for idx, item in enumerate(supplementals, start=1):
        sup_label = f"cap {cap_number} (veo) supp {idx}"
        if not isinstance(item, dict):
            raise VisualValidationError(f"{sup_label}: no es dict")

        sp_prompt = item.get("prompt")
        if not isinstance(sp_prompt, str) or not sp_prompt.strip():
            raise VisualValidationError(f"{sup_label}: prompt vacío o no string")
        sp_prompt = sp_prompt.strip()
        _validate_prompt_length(sp_prompt, sup_label)

        sp_anchor = item.get("narration_anchor")
        sp_pos, sp_end = _validate_anchor_substring(sp_anchor, narration, sup_label)
        sp_anchor = sp_anchor.strip()

        # Orden cronológico estricto entre supplementals
        if sp_pos <= last_pos:
            raise VisualValidationError(
                f"{sup_label}: anchor fuera de orden. Pos actual ({sp_pos}) "
                f"<= pos del anchor previo ({last_pos}). Los anchors de "
                f"supplementals deben estar en orden cronológico estricto."
            )
        if sp_pos < last_end:
            raise VisualValidationError(
                f"{sup_label}: anchor solapa con el supplemental anterior."
            )

        # No solapamiento con el anchor del Veo según veo_position
        if veo_position == "start" and sp_pos < veo_anchor_end:
            raise VisualValidationError(
                f"{sup_label}: anchor solapa con la zona Veo "
                f"(veo_position=start, veo_anchor_end={veo_anchor_end}, "
                f"sp_pos={sp_pos}). Los supplementals deben venir DESPUÉS "
                f"del anchor Veo."
            )
        if veo_position == "end" and sp_end > veo_anchor_pos:
            raise VisualValidationError(
                f"{sup_label}: anchor solapa con la zona Veo "
                f"(veo_position=end, veo_anchor_pos={veo_anchor_pos}, "
                f"sp_end={sp_end}). Los supplementals deben venir ANTES "
                f"del anchor Veo."
            )

        last_pos = sp_pos
        last_end = sp_end

        validated_supplementals.append({
            "prompt": sp_prompt,
            "narration_anchor": sp_anchor,
            "art_profile": "",
        })

    return {
        "chapter_number": cap_number,
        "image_prompt": image_prompt,
        "video_prompt": video_prompt,
        "subject_ref": subject_ref,
        "art_profile": "",
        "narration_anchor": anchor,
        "veo_position": veo_position,
        "supplemental_image_prompts": validated_supplementals,
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

    # Refactor v6 chat 27: el budget de chars para los 3 slots se calcula
    # restando el ancla_global del PROMPT_MAX_CHARS, para validar IN-LOOP
    # y disparar retry del LLM si algún item se pasa.
    ancla_global = get_active_nicho()["ancla_global"]
    ancla_len = len(ancla_global)

    for i, item in enumerate(items, start=1):
        label = f"cap {cap_number} img #{i}"
        if not isinstance(item, dict):
            raise VisualValidationError(f"{label}: item no es dict")

        # 1. Validar el campo `prompt` (refactor v7 chat 30, schema colapsado).
        # El LLM emite UN solo campo `prompt` en prosa natural, sin 3 slots.
        # Ver MODEL_PROMPTING_RULES.md §1 (Flux 2 Pro).
        if "prompt" not in item:
            raise VisualValidationError(
                f"{label}: falta campo 'prompt'. "
                f"Refactor v7 chat 30 requiere un solo campo `prompt`."
            )
        if not isinstance(item["prompt"], str):
            raise VisualValidationError(
                f"{label}: campo 'prompt' debe ser str, "
                f"recibido {type(item['prompt']).__name__}."
            )
        if not item["prompt"].strip():
            raise VisualValidationError(f"{label}: prompt vacío.")
        prompt_text = item["prompt"].strip()

        # 1b. Validar longitud del prompt (post-Ancla budget).
        # El ancla se concatena al FINAL en el ensamblaje, así que el
        # budget del prompt es PROMPT_MAX - ancla_len - 1 (espacio).
        PROMPT_BUDGET = PROMPT_MAX_CHARS - ancla_len - 1
        if len(prompt_text) > PROMPT_BUDGET:
            raise VisualValidationError(
                f"{label}: prompt {len(prompt_text)} chars excede budget "
                f"{PROMPT_BUDGET} (PROMPT_MAX={PROMPT_MAX_CHARS} - "
                f"ancla={ancla_len} - 1). Acortá el prompt."
            )

        # 2. subject_ref
        subject_ref = item.get("subject_ref")
        if not isinstance(subject_ref, str) or not subject_ref.strip():
            raise VisualValidationError(f"{label}: subject_ref vacío o no string")
        subject_ref = subject_ref.strip()

        # 3. emotional_rank
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

        # 4. narration_anchor — substring exacto (o tolerante a pausas/ws)
        anchor = item.get("narration_anchor")
        pos, anchor_end = _validate_anchor_substring(anchor, narration, label)
        anchor = anchor.strip() if isinstance(anchor, str) else anchor

        # 5. orden estricto
        if pos <= last_pos:
            raise VisualValidationError(
                f"{label}: anchor fuera de orden. Posición actual ({pos}) "
                f"<= posición del anchor previo ({last_pos}). "
                f"Los anchors deben aparecer en orden ESTRICTAMENTE creciente."
            )

        # 6. sin solapamiento
        if pos < last_end:
            raise VisualValidationError(
                f"{label}: anchor solapa con el anterior. Inicio actual ({pos}) "
                f"< final del anterior ({last_end}). Sin solapamiento."
            )

        last_pos = pos
        last_end = anchor_end

        normalized.append({
            "prompt": prompt_text,
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
    system_instruction: str | None = None,
    max_attempts: int = MAX_RETRY_ATTEMPTS,
) -> dict:
    """Llama Flash, valida, reintenta con feedback si falla.

    El feedback incluye un CHECKLIST acumulativo de reglas críticas en cada
    retry. Razón (chat 14): el LLM tiende a hiper-enfocarse en el último
    error reportado y rompe reglas que ya cumplía. El checklist le recuerda
    todo lo que tiene que mantener cumpliéndose simultáneamente.

    Args:
        prompt: prompt completo a enviar a Flash.
        validator_fn: callable(parsed_dict) -> dict normalizado o raise.
        cap_number: para logs.
        system_instruction: system_instruction opcional para call_flash_json
            (chat 19: documentary photography style).
        max_attempts: incluye el intento original. 2 = 1 intento + 1 retry.
    """
    attempt_prompt = prompt
    last_error: VisualValidationError | None = None

    for attempt in range(1, max_attempts + 1):
        raw = call_flash_json(attempt_prompt, system_instruction=system_instruction)
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

  □ REGLA 6 — Largo del prompt: 120-400 chars (target 180-300).
    Pasarte de 400 indica metadatos técnicos o redundancia.

  □ REGLA 7 — narration_anchor = SUBSTRING EXACTO de la narración del
    cap. Sin reformular, sin traducir, sin recortar palabras del medio,
    sin cambiar puntuación. Copiá literal.

  □ REGLA 8 — anchors en orden ESTRICTAMENTE creciente sobre la
    narración, SIN solapamiento (el final de un anchor < el inicio
    del siguiente).

  □ REGLA 9 — Cada prompt incluye al menos UN marcador temporal
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
#  STITCHING (no-op desde chat 19)
# ═══════════════════════════════════════════════════════════════
#
# El catálogo art_profiles quedó desconectado del flujo activo en chat 19:
# el LLM emite el prompt completo (subject + action + environment + marcador
# temporal + lighting/atmosphere inline), guiado por el system_instruction
# de "documentary photography style". Ya no hay zona 2 que se concatene
# después.
#
# Estas funciones se mantienen como no-ops para preservar la firma pública
# y los call sites en assign_visual_prompts.

def _stitch_zone2_into_cap_veo(cap_out: dict) -> dict:
    """No-op desde refactor chat 19 (catálogo desconectado).
    El prompt ya viene completo del LLM."""
    return cap_out


def _stitch_zone2_into_cap_flux(cap_out: dict) -> dict:
    """No-op desde refactor chat 19 (catálogo desconectado).
    El prompt ya viene completo del LLM."""
    return cap_out


# ═══════════════════════════════════════════════════════════════
#  FUNCIÓN PÚBLICA
# ═══════════════════════════════════════════════════════════════

def assign_visual_prompts(
    topic: dict,
    skeleton: dict,
    narration: dict,
    sync_map: dict | None = None,
) -> dict:
    """Genera image_prompts[] EN con narration_anchor por imagen.

    Args:
        topic     : dict (formato post módulo 00, con verified_facts y canonical_*).
        skeleton  : dict {topic_id, chapters[7]} (output 01a, sin _distribution_plan).
        narration : dict {topic_id, chapters[7] con narration} (output 01b).
        sync_map  : dict REQUERIDO para caps flux (PR 3 chat 27). Output de
                    audio_manager.process_script. Su campo chapters[i].duration_sec
                    es el input de _calculate_image_count. Si es None y hay caps flux,
                    assign_visual_prompts levanta ValueError. Para caps veo (1, 7)
                    todavía no se usa.

    Returns:
        {
          "topic_id": str,
          "chapters": [
            {chapter_number, image_prompt, video_prompt, subject_ref,
             narration_anchor},                                   # caps 1, 7 (veo)
            {chapter_number, image_prompts: [...]},                # caps 2-6 (flux)
            ... (7 items total)
          ],
          "_sync_map_ref": str | None,  # video_id del sync_map si fue provisto
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
            # Chat 29 #175: sync_map ahora requerido también para caps veo
            # (para calcular n_flux_extras según audio_duration del cap).
            if sync_map is None:
                raise ValueError(
                    f"cap {cap_n}: sync_map es requerido para caps veo "
                    f"híbridos (chat 29 #175). Re-correr desde audio: --from audio"
                )
            cap_id = f"ch{cap_n:02d}"
            cap_audio_entry = next(
                (c for c in sync_map.get("chapters", []) if c.get("id") == cap_id),
                None,
            )
            if cap_audio_entry is None:
                raise ValueError(
                    f"cap {cap_n}: sync_map no tiene entry para id={cap_id}"
                )
            cap_duration_sec = float(cap_audio_entry["duration_sec"])

            # Inferir veo_position por role del cap (NO por LLM).
            role = (sch.get("role") or "").strip().lower()
            veo_position = "end" if role == "reveal_outro" else "start"

            n_flux_extras = _calculate_flux_extras_count(cap_duration_sec)

            # Chat 31 #219: aproximación lineal chars↔segundos para acotar la zona
            # Veo en chars concretos. Resuelve flakiness del LLM al adivinar "los
            # primeros/últimos 8s del cap" sin coordenadas. Bill TTS es voz neural
            # consistente — el error de aproximación lineal cae dentro del rango
            # que el validator tolera (anchor flexible dentro de la zona).
            if cap_duration_sec > 0:
                chars_per_sec = len(narration_text) / cap_duration_sec
                veo_zone_chars = int(VEO_CLIP_DURATION_SEC * chars_per_sec)
            else:
                veo_zone_chars = 0  # defensivo, no debería ocurrir
            # Clamp a [1, len(narration_text)-1] para evitar zonas degeneradas
            veo_zone_chars = max(1, min(veo_zone_chars, len(narration_text) - 1))

            print(
                f"  [03] cap {cap_n} (veo, pos={veo_position}) → "
                f"1 clip Veo {VEO_CLIP_DURATION_SEC:.0f}s + {n_flux_extras} "
                f"Flux extras (audio {cap_duration_sec:.1f}s, "
                f"veo_zone≈{veo_zone_chars} chars), llamando Flash..."
            )
            prompt = _build_veo_prompt(
                topic, sch, narration_text,
                cap_duration_sec, n_flux_extras, veo_position,
                veo_zone_chars,
            )
            cap_out = _call_with_validation_retry(
                prompt,
                validator_fn=lambda parsed, n=narration_text, cn=cap_n, vp=veo_position: _validate_veo_cap(parsed, n, cn, vp),
                cap_number=cap_n,
                system_instruction=SYSTEM_INSTRUCTION_VISUAL,
            )
            # No-op desde chat 19 (catálogo desconectado): el prompt ya
            # viene completo del LLM. Llamada preservada por compat.
            cap_out = _stitch_zone2_into_cap_veo(cap_out)
            print(
                f"  [03] cap {cap_n} (veo)  ✓ Veo prompt + "
                f"{len(cap_out['supplemental_image_prompts'])} supplementals"
            )

        elif engine == "flux":
            # PR 3 chat 27: lookup duración real del audio del cap en sync_map.
            if sync_map is None:
                raise ValueError(
                    f"cap {cap_n}: sync_map es requerido para caps flux "
                    f"(PR 3 chat 27). Re-correr desde audio: --from audio"
                )
            cap_id = f"ch{cap_n:02d}"
            cap_audio_entry = next(
                (c for c in sync_map.get("chapters", []) if c.get("id") == cap_id),
                None,
            )
            if cap_audio_entry is None:
                raise ValueError(
                    f"cap {cap_n}: sync_map no tiene entry para id={cap_id}"
                )
            cap_duration_sec = float(cap_audio_entry["duration_sec"])
            n_images = _calculate_image_count(
                cap_duration_sec=cap_duration_sec,
                chapter_number=cap_n,
                total_chapters=EXPECTED_CHAPTER_COUNT,
            )
            print(
                f"  [03] cap {cap_n} (flux) → {n_images} imgs "
                f"(audio {cap_duration_sec:.1f}s ÷ {SECONDS_PER_IMAGE_TARGET}s "
                f"target, role={sch.get('role','?')}), llamando Flash..."
            )
            prompt = _build_flux_prompt(topic, sch, narration_text, n_images)
            cap_out = _call_with_validation_retry(
                prompt,
                validator_fn=lambda parsed, n=narration_text, cn=cap_n, ni=n_images: _validate_flux_cap(parsed, n, cn, ni),
                cap_number=cap_n,
                system_instruction=SYSTEM_INSTRUCTION_VISUAL,
            )

            # Ensamblaje v7 chat 30: el LLM emite el prompt completo en prosa.
            # m03 solo agrega el style del nicho AL FINAL (subject-first según
            # MODEL_PROMPTING_RULES.md §1 R1 — el sujeto va primero).
            # Se persiste el raw_llm_prompt para auditoría m05.
            nicho = get_active_nicho()
            ancla_global = nicho["ancla_global"]
            for item in cap_out.get("image_prompts", []):
                raw_prompt = item["prompt"].strip()
                prompt_final = raw_prompt + " " + ancla_global
                if not (PROMPT_MIN_CHARS <= len(prompt_final) <= PROMPT_MAX_CHARS):
                    raise VisualValidationError(
                        f"cap {cap_n}: prompt ensamblado fuera de rango "
                        f"({len(prompt_final)} chars, target "
                        f"{PROMPT_MIN_CHARS}-{PROMPT_MAX_CHARS})."
                    )
                item["raw_llm_prompt"] = raw_prompt  # auditoría m05
                item["prompt"] = prompt_final
                item["art_profile"] = ""

            # No-op desde chat 19 (catálogo desconectado).
            cap_out = _stitch_zone2_into_cap_flux(cap_out)
            print(f"  [03] cap {cap_n} (flux) ✓ {len(cap_out['image_prompts'])} imgs validadas")

        else:
            raise ValueError(
                f"cap {cap_n}: render_engine='{engine}' inválido (esperado 'veo' o 'flux')"
            )

        output_chapters.append(cap_out)

    output = {
        "topic_id": topic_id,
        "chapters": output_chapters,
    }

    # PR 1 chat 24: persistir solo el video_id como referencia. El sync_map
    # autoritativo vive en output/audio/<id>/sync_map.json — duplicarlo acá
    # crearía drift. PR 3 lo cargará desde el path autoritativo.
    if sync_map is not None:
        output["_sync_map_ref"] = sync_map.get("video_id")

    _persist(topic_id, output)
    return output
