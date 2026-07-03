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
  _validate_prompt_length(prompt, label)        → None | raise
  _validate_no_text_leakage(prompt, label)      → None | raise
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
from concurrent.futures import ThreadPoolExecutor, as_completed
from difflib import SequenceMatcher
from pathlib import Path

from config import DATA_DIR, OUTPUT_DIR, api
from gemini_helpers import call_flash_json, call_pro_json
from nicho_config import get_active_nicho
from anchor_timing import compute_anchor_starts
from script_engine.name_matching import scrub_documented_names
from engine_profiles import select_profile


# Enums de shot_scale / light_mode. VALID_SHOT_SCALES lo usa el post-check de slots del skeleton seedream.
VALID_SHOT_SCALES = frozenset({"extreme_wide", "wide", "medium", "close", "detail"})
VALID_LIGHT_MODES = frozenset({"night", "day", "golden"})


# ═══════════════════════════════════════════════════════════════
#  SEEDREAM 4.5 — SKELETON + FLUIDIFICADOR + GUARDA 1 (eslabón 3b)
# ═══════════════════════════════════════════════════════════════
#
# Corazón de B (DOC_SKELETON + HANDOFF_PROBE_FASE_B, validado lab 102). El LLM
# NO redacta prosa libre: RELLENA SLOTS (skeleton). Un fluidificador (2º call
# Pro) teje los slots en prosa Seedream siguiendo el ORDEN del perfil (3a). Un
# POST-CHECK determinista LOCKEA las cifras-con-significado (Guarda 1) — atrapa
# si el fluidificador redondea/borra/traduce un número.
#
# Camino aditivo: se activa con api.image_engine == "seedream". Kling/Flux quedan
# byte-idénticos (FALLBACK vivo). El craft del director Kling se CONSERVA acá como
# definición de cada slot (no se re-inventa, se re-ordena).

# Slots que emite el LLM (craft Kling re-empaquetado como casilleros).
SEEDREAM_SLOT_KEYS = (
    "subject", "action", "gaze_interaction", "setting", "color_palette",
    "props_detail", "shot_scale", "camera_angle", "lens_technique",
    "lighting", "mood", "style",
)

# Paralelismo del fluidificador per-imagen (el 55% de las ~90 llamadas Pro por topic).
# Los ítems son independientes (cada uno muta su propio slot-dict; sin estado compartido;
# call_pro_json no toca cost_tracker). Techo real = límite RPM de Gemini Pro (1000) → sobra;
# 16 es conservador (pico ~16 RPM). Bajalo si otro proceso comparte la cuota del proyecto.
FLUIDIFY_MAX_WORKERS = 16

# Paralelismo por-CAP (los 7 caps son independientes: leen skel/narr/sync_map read-only,
# escriben solo su propio cap_out). Solapa las 7 llamadas de "slots" (1/cap), el cuello que
# queda tras paralelizar el fluidify. Anidado con el fluidify → pico ≈ CAP×FLUIDIFY llamadas Pro
# concurrentes; con 7×16=112 seguís al ~11% del límite RPM (1000), pero bajá si el SDK se ahoga.
CAP_MAX_WORKERS = 7

SYSTEM_INSTRUCTION_VISUAL_SEEDREAM = """You are the IMAGE DIRECTOR of a faceless dark-history documentary channel. You do NOT write a free prose prompt: you FILL the slots (casilleros) of EACH image. Emit a JSON ARRAY of N slot-objects, one per given narration fragment, in the SAME order (item i fills the slots for fragment i). All slot VALUES in ENGLISH.

Definition of each slot (what goes in each casillero — this is the craft, model-agnostic):

- subject: who/what is the focus. For people: integrate the LOCAL ethnicity of the topic's GEO (R1), period-correct, NEVER a person's proper name (R3a) — describe by appearance/role. — if the focus object is in foto_madre_ref, name it but do NOT re-describe its shape/pose (the anchor holds it).
- action: the VERB of the anchor — the EXACT moment it narrates (R11), not the aftermath. What is happening. For a place/object with no human action, the state/movement of the scene. — for an anchored object, narrate the action WITHOUT forcing its orientation or structure (no "suspended vertically", no "encased in").
- gaze_interaction: where the subject looks / how it touches objects; on an R1 hero beat the face/eyes to the front (R8). If no human, the focal direction of the scene.
- setting: the place, period-correct (R4, anti-medieval), dressed/placed by the narration of THIS beat, not by cliché (R10). No striped prison uniforms.
- color_palette: the palette of the era AND of THIS specific place (from the visual canon provided — era layer + sourced place layer).
- props_detail: ONE loaded focal prop, never an empty plate (R8). — never restate the form of an object already in foto_madre_ref.
- shot_scale: one of extreme_wide|wide|medium|close|detail. WIDE/EXTREME_WIDE dominates for establishing/architecture/scale/mass events; medium/close ONLY for one human emotion or one texture detail (R7).
- camera_angle: e.g. low angle for scale, eye-level, high angle (R7).
- lens_technique: e.g. deep depth of field, shallow depth of field, 85mm lens.
- lighting: light by the EVENT (R12) — beats of the SAME event share ONE light. overcast daylight, golden hour, low-key night, etc.
- mood: the emotional tone, WITHIN the monetization ceiling (R5, HARD CAP, do not soften): terror is built from SCALE + LIGHT + EMPTY apparatus + loaded LIVING faces — NEVER lifeless bodies, never fresh graphic blood, never the moment of harm. Show the OUTCOME/charged empty space, never the mechanism centered.
- style: the channel constant — documentary photographic realism, dark-history, faceless. (This is a slot, NOT a harness tail.)
- text_in_image: a label when the scene legitimately carries text — a literal sign/inscription/number (building number, carved place name), OR a period newspaper headline / wanted-notice when the anchor narrates a notable EVENT (an escape, a scandal, a ruling) and a headline would authentically illustrate it. Use SPARINGLY — only when it ADDS to the beat, never decorative, a minority of images per cap at most. present=false for ordinary people/atmosphere scenes with no narrated text; NEVER a person's proper name. If present=true: text = the literal content IN SPANISH (the audience reads Spanish — a headline reads 'PRÓFUGO', not 'ESCAPED'), font (carved/block/serif/newsprint...), location (over the entrance / front page...). Seedream renders quoted text legibly — allowed and intended.
- hard_fact_ids: the F-labels (e.g. ["F03","F10"]) of the provided verified_facts whose FIGURES this image actually shows, copied EXACTLY as labeled in the list. Do NOT write the figures yourself — ONLY pick labels RELEVANT to THIS anchor's moment AND place. A figure belongs here only if THIS image depicts it: do NOT attach a building's structural figures (floors, height, year built) to a people/farm/landscape anchor, nor foundation/closing figures to a peak beat. When in doubt, leave it EMPTY — an honest [] is better than an irrelevant figure forced into the scene (which the locked-figures guard will reject downstream). [] if none apply.
- subject_ref: "main_subject" if there is a protagonist; else "establishing_shot" / "interior_scene" / "landscape_view".
- foto_madre_ref: a LIST (array) of the recurring documented objects this image DEPICTS as its focus — usually one, sometimes none, at most TWO. The visual canon above names the central subject and any documented objects. Include an object's canonical name in the list when THIS beat's focus IS that recurring object — even when the narration refers to it by metaphor, function or material rather than plainly (its identity is the same object). Use the exact string "__subject__" for the central recurring subject, or the exact name shown after "objeto:" in OBJETOS DOCUMENTADOS for a documented object. Default []: leave the list EMPTY unless an object is the actual focus of THIS image — an object merely mentioned, alluded to, or sitting in the background does NOT go in the list (its form is already held by the prose slots). Up to TWO refs: list a ref for EACH documented object that is a genuine co-focus of THIS beat — e.g. a cutaway/composite that shows two anchored objects together. NEVER more than two. If only one object is the focus, list just that one. This slot is routing only — it is NOT rendered as text. ANCHOR HOLDS THE FORM: when an object is listed in foto_madre_ref, a reference image already fixes its shape, proportion, orientation and internal structure. Therefore, in the other slots, describe only what that object DOES and WHERE it is (its action, its place in the scene) — NEVER its form, pose, angle, or how it is built. Do NOT write a verb or a prop detail that forces a specific orientation or adds structure to an anchored object (e.g. "suspended vertically", "laid along the hull", "encased in a frame", "lowered into the core"). Narrate the moment at a level that leaves the object's physical form entirely to its reference image. This applies ONLY to objects that are in foto_madre_ref; unanchored objects are still described in full by the prose as before. ✓ conceptual: "the crew lowers the vessel into place" (action only, no form) · ✗ "the tall vertical vessel is lowered" (imposes form on an anchored object).
- emotional_rank: "R1" (peak/hero) | "R2" (action) | "R3" (atmosphere) — see distribution in the user prompt.

Fill ALL slots for EVERY item. Each value is a SHORT English phrase (not a paragraph). Do NOT write aspect ratio, negations, or a style/grain tail — the profile/assembler adds those afterward.

TEXT DISCIPLINE: any text meant to appear in the image goes ONLY through the text_in_image slot, in Spanish. The prose slots (subject/action/setting/...) describe the scene — never embed letters or words to be rendered inside them.

JSON only. No markdown. No preamble."""


def _seedream_slots_schema(n: int) -> dict:
    """Schema de los SLOTS (array de N). response_schema vuelve todo required
    (gemini_helpers) — text_in_image lleva present:false cuando no aplica."""
    return {
        "type": "ARRAY",
        "items": {
            "type": "OBJECT",
            "properties": {
                "subject": {"type": "STRING"},
                "action": {"type": "STRING"},
                "gaze_interaction": {"type": "STRING"},
                "setting": {"type": "STRING"},
                "color_palette": {"type": "STRING"},
                "props_detail": {"type": "STRING"},
                "shot_scale": {"type": "STRING",
                               "enum": ["extreme_wide", "wide", "medium", "close", "detail"]},
                "camera_angle": {"type": "STRING"},
                "lens_technique": {"type": "STRING"},
                "lighting": {"type": "STRING"},
                "mood": {"type": "STRING"},
                "style": {"type": "STRING"},
                "text_in_image": {
                    "type": "OBJECT",
                    "properties": {
                        "present": {"type": "BOOLEAN"},
                        "text": {"type": "STRING"},
                        "font": {"type": "STRING"},
                        "location": {"type": "STRING"},
                    },
                    "required": ["present", "text", "font", "location"],
                },
                "hard_fact_ids": {"type": "ARRAY", "items": {"type": "STRING"}},
                "subject_ref": {"type": "STRING"},
                "foto_madre_ref": {"type": "ARRAY", "items": {"type": "STRING"}},
                "emotional_rank": {"type": "STRING"},
            },
            "required": list(SEEDREAM_SLOT_KEYS) + [
                "text_in_image", "hard_fact_ids", "subject_ref", "emotional_rank",
                "foto_madre_ref"],
        },
    }


def _format_seedream_canon_block(topic: dict) -> str:
    """Canon de 2 CAPAS para el user-prompt del skeleton (eslabón 3b cablea el 2).

    Espejo de _format_visual_canon_block PERO extendido con la capa SOURCED del
    sujeto puntual (eslabón 2): materials_textures, color_palette, scale_dimensions,
    distinctive_features, demographics, visual_reference_availability,
    condition_evolution. NO modifica el bloque viejo (Kling/Flux byte-idénticos);
    es una función aparte que solo usa el path seedream.
    """
    era = topic.get("era_visual_canon") or {}
    people = topic.get("documented_people") or []
    blocklist = topic.get("anachronism_blocklist") or []
    props = topic.get("documented_props") or []

    if era.get("primary_decade"):
        epoca = [
            "ERA (capa genérica de la época):",
            f"  primary_decade        : {era.get('primary_decade', '')}",
            f"  spans                 : {era.get('spans', '')}",
            f"  clothing              : {era.get('clothing', '')}",
            f"  technology            : {era.get('technology', '')}",
            f"  vehicles_machinery    : {era.get('vehicles_machinery', '')}",
            f"  interiors             : {era.get('interiors', '')}",
            f"  forbidden_anachronisms: {era.get('forbidden_anachronisms', '')}",
        ]
        cond = era.get("condition_evolution") or {}
        sourced = [
            "LUGAR PUNTUAL (capa sourced — específica de ESTE lugar, eslabón 2):",
            f"  materials_textures           : {era.get('materials_textures', '')}",
            f"  color_palette                : {era.get('color_palette', '')}",
            f"  scale_dimensions             : {era.get('scale_dimensions', '')}",
            f"  distinctive_features         : {era.get('distinctive_features', '')}",
            f"  demographics                 : {era.get('demographics', '')}",
            f"  visual_reference_availability : {era.get('visual_reference_availability', '')}",
            f"  condition_evolution.at_event : {cond.get('at_event', '')}",
            f"  condition_evolution.later    : {cond.get('later', '')}",
        ]
        era_block = "\n".join(epoca) + "\n\n" + "\n".join(sourced)
    else:
        era_block = ("CANON VISUAL: (vacío — no disponible). Inferí de verified_facts "
                     "y canonical_subject_description.")

    if people:
        plines = ["PERSONAS DOCUMENTADAS (usar appearance_canon, NUNCA el nombre):"]
        for p in people:
            age = p.get("age_at_event")
            age_str = f"age {age}" if age is not None else "age unknown"
            plines.append(f"  • role: {p.get('role','?')} | {age_str} | era: {p.get('era','?')}")
            plines.append(f"    appearance_canon: {p.get('appearance_canon','')}")
        people_block = "\n".join(plines)
    else:
        people_block = ("PERSONAS DOCUMENTADAS: (vacío) — si la narración nombra a alguien, "
                        "describilo por rol+aspecto+era, NUNCA por nombre.")

    # OBJETOS DOCUMENTADOS (eslabón 3): espejo de personas. SOLO nombre + forma
    # (anclado/foto_madre NO se surfacean acá — es el NUDO 2, aparte). Contexto pasivo.
    if props:
        prlines = ["OBJETOS DOCUMENTADOS (mantené la FORMA GENERAL constante entre imágenes;",
                   "la narración puede nombrarlos por metáfora, función o material):"]
        for p in props:
            prlines.append(f"  • objeto: {p.get('nombre','?')}")
            prlines.append(f"    forma: {p.get('forma','')}")
        props_block = "\n".join(prlines)
    else:
        props_block = ("OBJETOS DOCUMENTADOS: (vacío) — describí cualquier objeto que nombre la "
                       "narración por su forma física según el relato, sin inventar detalles no dichos.")

    if blocklist:
        blocklist_block = "ANACRONISMOS PROHIBIDOS:\n" + "\n".join(f"  - {b}" for b in blocklist)
    else:
        blocklist_block = "ANACRONISMOS PROHIBIDOS: (vacío)."

    return f"""{era_block}

{people_block}

{props_block}

{blocklist_block}

USO (2 capas): la capa ÉPOCA es genérica; la capa LUGAR PUNTUAL es específica de
ESTE lugar (úsala para color_palette / setting / props_detail / subject).
OBJETOS: cuando un beat se refiere a uno de estos objetos —aunque el relato lo
llame por metáfora o por su función— su forma general NO cambia entre imágenes:
usá la forma canónica del catálogo, no reinventes su silueta. GUARDA-B:
el canon NUNCA pisa una cifra más precisa de los verified_facts — "over 800 acres"
(canon) NO reemplaza "873 acres" (fact). Donde hay fact, manda el fact; el canon
llena lo que el fact no tiene."""


# ── GUARDA 1: candado de cifras por SIGNIFICADO (DOC_GUARDA1_CANDADO) ──
# Lockea MEDIDA (numeral + unidad) y FECHA (año), NUNCA NOMBRE ("Building 93").
# El fact puede venir en ES; se lockea el NUMERAL (invariante de idioma) y el
# fluidificador escribe la unidad en inglés. Ante la duda → NO lockear.
# Unidades de medida agrupadas por TIPO (CANDADO_2BIS). El post-check exige el PAR
# (número + unidad EN DEL MISMO TIPO): "13 rows" falla (rows ∉ unidad); "111 feet"
# para un fact "111 años" TAMBIÉN falla (feet=length ≠ duration). "13 floors" pasa.
# Cada grupo lista (unidades_EN, unidades_ES) — el fact puede venir en español; la
# DETECCIÓN usa EN+ES, la ADYACENCIA en la prosa inglesa usa solo EN del grupo.
_UNIT_GROUPS: dict[str, tuple[str, str]] = {
    "length":    (r"feet|foot|ft|yards?|met(?:er|re)s?|inches|miles?|kilomet(?:er|re)s?|km",
                  r"pies|metros?|millas?|kil[oó]metros?"),
    "height":    (r"floors?|stor(?:y|ies)|storeys?", r"pisos?"),
    "area":      (r"acres?|hectares?", r"hect[aá]reas?"),
    "duration":  (r"years?|months?|weeks?|days?|hours?", r"a[ñn]os?|meses|d[ií]as?|horas?|semanas?"),
    "count_ppl": (r"patients?|inmates?|victims?|deaths?|graves?|beds?",
                  r"pacientes?|internos?|v[ií]ctimas?|muertos?|tumbas?|camas?"),
    "mass":      (r"tons?|tonnes?|pounds?|lbs?|kg", r"toneladas?"),
    "count_bld": (r"buildings?", r"edificios?"),
}
_GROUP_EN: dict[str, str] = {g: en for g, (en, es) in _UNIT_GROUPS.items()}
_GROUP_ANY_RE: dict[str, "re.Pattern"] = {
    g: re.compile(rf"^(?:{en}|{es})$", re.I) for g, (en, es) in _UNIT_GROUPS.items()
}
_MEASURE_UNITS_EN = "|".join(en for en, es in _UNIT_GROUPS.values())
_MEASURE_UNITS_ES = "|".join(es for en, es in _UNIT_GROUPS.values())
_MEASURE_UNITS = _MEASURE_UNITS_EN + r"|" + _MEASURE_UNITS_ES   # detección (EN+ES)
_NAME_PREFIX_RE = re.compile(
    r"\b(?:building|ward|room|block|route|unit|section|cottage|wing|hall|gate|pier|"
    r"edificio|sala|pabell[oó]n|bloque|unidad|secci[oó]n|ala|sector)\s*$", re.I)
# group(1)=numeral, group(2)=unidad (CAPTURADA → se mapea a su TIPO).
_MEASURE_RE = re.compile(rf"(\d[\d.,]*\d|\d)\s*[-–]?\s*({_MEASURE_UNITS})\b", re.I)
_YEAR_RE = re.compile(r"\b(1[0-9]\d{2}|20\d{2}|21\d{2})\b")


def _unit_to_mtype(unit: str) -> str | None:
    """Mapea una unidad (EN o ES) a su grupo de TIPO. None si no encaja (→ fallback
    a 'cualquier unidad EN' en la adyacencia, comportamiento previo, no rompe)."""
    u = unit.strip().lower()
    for g, rx in _GROUP_ANY_RE.items():
        if rx.match(u):
            return g
    return None


def _has_name_prefix(text: str, num_start: int) -> bool:
    """True si el número en num_start viene PEGADO a un sustantivo identificador
    (Building/Ward/...) → es NOMBRE, no cifra."""
    return bool(_NAME_PREFIX_RE.search(text[:num_start]))


def _classify_locked_facts(verbatim_facts: list[str]) -> list[dict]:
    """Devuelve las CIFRAS-CON-SIGNIFICADO a lockear, cada una con su CAJÓN:
      {"num": "13",   "kind": "measure"}   ← se lockea el PAR (num + unidad EN en prosa)
      {"num": "1939", "kind": "year"}      ← se lockea el numeral pelado
    NOMBRE ("Building 93") nunca entra. Dedup por num (el primer cajón gana).
    Ante la duda (pelado sin unidad/año/prefijo) → no entra (asimetría DOC §4)."""
    out: list[dict] = []
    seen: set[str] = set()

    def _add(num: str, kind: str, mtype: str | None = None):
        num = num.strip(" .,")
        if num and num not in seen:
            seen.add(num)
            entry = {"num": num, "kind": kind}
            if kind == "measure":
                entry["mtype"] = mtype     # CANDADO_2BIS: el TIPO de la unidad detectada
            out.append(entry)

    for ft in verbatim_facts:
        if not ft:
            continue
        # MEDIDA primero (gana sobre año si un mismo numeral cae en ambos, ej "1500 patients").
        for m in _MEASURE_RE.finditer(ft):
            if not _has_name_prefix(ft, m.start()):
                mtype = _unit_to_mtype(m.group(2))
                if mtype == "duration":        # duraciones NO se lockean: no son dibujables
                    continue
                _add(m.group(1), "measure", mtype)
        for m in _YEAR_RE.finditer(ft):
            if not _has_name_prefix(ft, m.start()):    # "Building 1939" → NOMBRE, no fecha
                _add(m.group(1), "year")
    return out


# B1 · RAÍZ (productor, chat 114 §2-B): el skeleton no debe encajar >1 medida en una
# imagen que no puede hospedar dos unidades distintas (el fluidificador no puede cumplir
# las dos → Guarda 1 muere). Tope tweakable, NO hardcodeado inline.
MAX_MEASURES_PER_IMAGE = 1


def _enforce_measure_fit(locked: list[dict], label: str,
                         max_measures: int = MAX_MEASURES_PER_IMAGE) -> list[dict]:
    """Control de FIT determinístico: si una imagen trae más de `max_measures` cifras-MEDIDA,
    conserva las primeras (la 1ra medida = la del primer hard_fact, proxy de centralidad) y
    SUELTA las sobrantes ANTES de lockear, con WARN ruidoso. Los AÑOS no se tocan (un año y
    una medida coexisten sin romper la guarda). Así el fluidificador nunca recibe carga
    imposible. Devuelve el locked filtrado (no muta el original)."""
    kept: list[dict] = []
    dropped: list[dict] = []
    seen_measures = 0
    for it in locked:
        if it["kind"] == "measure":
            if seen_measures >= max_measures:
                dropped.append(it)
                continue
            seen_measures += 1
        kept.append(it)
    if dropped:
        drop_str = ", ".join(f'{d["num"]} (+{d.get("mtype") or "measure"})' for d in dropped)
        print(f"  ⚠ [m03] {label}: FIT — {len(dropped)} medida(s) sobrante(s) soltada(s) "
              f"antes de lockear (máx {max_measures}/imagen): {drop_str}")
    return kept


def _digit_variants(d: str) -> set[str]:
    """ES usa '.' como separador de miles, EN usa ','. Aceptar ambas formas."""
    return {d, d.replace(",", "."), d.replace(".", ",")}


_SPANISH_UNIT_WORDS = (
    "pisos", "piso", "pies", "pacientes", "paciente", "internos", "tumbas",
    "años", "año", "anos", "edificios", "metros", "muertos",
    "víctimas", "victimas", "millas", "toneladas", "hectáreas",
)


def _measure_unit_adjacent(prose: str, num: str, mtype: str | None = None) -> bool:
    """True si el numeral aparece en la prosa PEGADO a una unidad de medida EN
    DEL MISMO TIPO (CANDADO_2BIS). "13 floors"/"13-story" (height) → True;
    "13 rows" → False (rows ∉ unidad); "111 feet" con mtype=duration → False
    (feet=length ≠ duration) → atrapa el "111 años" disfrazado de longitud.
    mtype None → fallback a CUALQUIER unidad EN (comportamiento previo, no rompe)."""
    en_units = _GROUP_EN.get(mtype, _MEASURE_UNITS_EN) if mtype else _MEASURE_UNITS_EN
    for v in _digit_variants(num):
        if re.search(rf"{re.escape(v)}\s*[-–]?\s*(?:{en_units})\b", prose, re.I):
            return True
    return False


def _post_check_locked(prose: str, locked: list[dict]) -> tuple[list[str], list[str]]:
    """Guarda dura determinista (DOC_GUARDA1 §2 + CANDADO_2BIS):
      - MEDIDA: el numeral debe aparecer PEGADO a su unidad EN DEL MISMO TIPO.
                "13 rows" → FALLA (sin unidad); "111 feet" cuando el fact era
                "111 años" → FALLA (length ≠ duration).
      - AÑO:    el numeral pelado debe aparecer (tolerando separador ES/EN).
    Además: ninguna unidad española suelta debe quedar en la prosa inglesa.
    Devuelve (missing, spanish_left). missing etiqueta cajón+tipo para el log."""
    missing: list[str] = []
    for it in locked:
        num, kind = it["num"], it["kind"]
        if kind == "measure":
            mtype = it.get("mtype")
            ok = _measure_unit_adjacent(prose, num, mtype)
            if not ok:
                missing.append(f"{num} (+{mtype or 'measure'} unit EN)")
        else:  # year
            ok = any(v in prose for v in _digit_variants(num))
            if not ok:
                missing.append(num)
    # El titular (text_in_image) va entre comillas y en español A PROPÓSITO (camino C).
    # Se excluye del chequeo de "español suelto", que caza traducciones olvidadas en la
    # prosa DESCRIPTIVA. El español dentro de comillas es intencional (mismo criterio que
    # el control 3 con allow_intentional_text); el español FUERA de comillas se sigue cazando.
    prose_sin_titular = re.sub(r"['\"][^'\"]*['\"]", " ", prose)
    spanish = sorted({u for u in _SPANISH_UNIT_WORDS
                      if re.search(rf"\b{re.escape(u)}\b", prose_sin_titular, re.I)})
    return missing, spanish


# ── FLUIDIFICADOR (2º call Pro): teje los slots en prosa Seedream ──
FLUIDIFICADOR_SYSTEM = """You are an image-prompt editor for Seedream 4.5. You receive the SLOTS of ONE image (already decided — do NOT change them) in formula order, and a list of MANDATORY NUMBERS. Your only task: WEAVE them into ONE natural, fluent English prose prompt.

HARD RULES:
- Complete sentences, one cohesive description. FORBIDDEN: token lists, double commas, fragments capitalized mid-sentence, "An wide shot".
- Follow the ORDER of the slots as given.
- The MANDATORY NUMBERS appear EXACT and as NUMERALS (do not spell them out), each with its unit IN ENGLISH: e.g. "13 floors", "159 feet", "873 acres", "9,303 patients"; years as-is ("1885", "1939"). Do NOT round, do NOT drop, do NOT use a Spanish unit word.
- Do NOT add new facts. Do NOT use any person's proper name (describe by appearance/role).
- If TEXT_IN_IMAGE is present: render the label with the Seedream recipe — a sign/inscription/headline reads "THE TEXT" in the given font and location, in clear crisp lettering. COPY the label text VERBATIM in its original language (usually Spanish) — NEVER translate it, never alter the digits inside it. The label is of a PLACE/object/event headline, NEVER a person's name.
- Close EXACTLY with the aspect-ratio line given in the input. Do NOT add anachronism negations (those are added later by the reviewer).

Return ONLY the prose field (no wrapping quotes, no markdown)."""

_FLUIDIFICADOR_SCHEMA = {"type": "OBJECT",
                         "properties": {"prose": {"type": "STRING"}},
                         "required": ["prose"]}


def _build_fluidificador_user(slots: dict, locked: list[dict], profile) -> str:
    """Arma el input del fluidificador caminando profile.formula (orden del perfil)."""
    tii = slots.get("text_in_image") or {}
    if tii.get("present"):
        text_line = (f'render: reads "{tii.get("text","")}" · font={tii.get("font","")} '
                     f'· location={tii.get("location","")}')
    else:
        text_line = "(none — do not render text)"
    lines = ["SLOTS (in profile formula order):"]
    for key in profile.formula:
        if key in SEEDREAM_SLOT_KEYS:
            lines.append(f"  {key}: {(slots.get(key) or '').strip()}")
        elif key == "text_in_image":
            lines.append(f"  text_in_image: {text_line}")
        # hard_facts / aspect_ratio / negations se manejan abajo (no son slots de texto libre)
    body = "\n".join(lines)
    measures = [it["num"] for it in locked if it["kind"] == "measure"]
    years = [it["num"] for it in locked if it["kind"] == "year"]
    meas_str = ", ".join(measures) if measures else "(none)"
    years_str = ", ".join(years) if years else "(none)"
    return f"""{body}

MANDATORY MEASURES — each MUST appear in the prose as the numeral IMMEDIATELY
followed by its English measure unit (e.g. "13 floors", "159 feet", "873 acres",
"9,303 patients"). Pick the correct unit for what THIS image actually shows; if a
number does not fit this image, it does NOT belong here — do not invent a unit: {meas_str}
MANDATORY YEARS (exact, as-is, e.g. "1885", "1939"): {years_str}

Weave everything into ONE fluent English prose prompt following the order above,
and close with: {profile.aspect_ratio_text}"""


def _fluidify_item(slots: dict, locked: list[dict], profile, label: str,
                   max_attempts: int = 3) -> str:
    """Llama el fluidificador y verifica la Guarda 1 (post-check determinista).
    Reintenta si una cifra se perdió/redondeó o quedó unidad española.

    BACKSTOP (chat 114 §2-A): si tras max_attempts sigue fallando, NO mata el run.
    DEGRADA: acepta la MEJOR prosa producida (la de menos faltantes), soltando las
    cifras que no entraron, con WARN ruidoso (qué cifra, qué cap/img). Honra el propio
    prompt del fluidificador ("si una cifra no entra, no la metas"). Solo si NINGÚN
    intento devolvió prosa utilizable → VisualValidationError (fallo legítimo)."""
    user = _build_fluidificador_user(slots, locked, profile)
    last_missing: list[str] = []
    last_spanish: list[str] = []
    best_prose: str = ""
    best_score: int | None = None
    best_missing: list[str] = []
    best_spanish: list[str] = []
    for attempt in range(1, max_attempts + 1):
        out = call_pro_json(user, system_instruction=FLUIDIFICADOR_SYSTEM,
                            response_schema=_FLUIDIFICADOR_SCHEMA)
        prose = (out or {}).get("prose", "") if isinstance(out, dict) else ""
        prose = re.sub(r"\s+", " ", prose).strip()
        missing, spanish = _post_check_locked(prose, locked)
        if not missing and not spanish and prose:
            return prose
        # Trackear la MEJOR prosa parcial (menos faltantes+ES) para el backstop.
        score = len(missing) + len(spanish)
        if prose and (best_score is None or score < best_score):
            best_score, best_prose = score, prose
            best_missing, best_spanish = missing, spanish
        last_missing, last_spanish = missing, spanish
        if attempt < max_attempts:
            user = (_build_fluidificador_user(slots, locked, profile) +
                    f"\n\nRETRY: the previous weave broke Guarda 1. Missing numerals: "
                    f"{missing or '-'}. Spanish unit words left: {spanish or '-'}. "
                    f"Re-weave keeping EVERY mandatory number exact (numeral) with its "
                    f"English unit.")
    # ── BACKSTOP §2-A: degradar en vez de raise (el run SIGUE) ──
    if best_prose:
        print(f"  ⚠ [m03] {label}: Guarda 1 DEGRADADA tras {max_attempts} intentos — "
              f"cifras no embebidas: {best_missing or '-'}; unidades ES residuales: "
              f"{best_spanish or '-'}. Prosa aceptada SIN esas cifras (run sigue).")
        return best_prose
    # Ningún intento devolvió prosa utilizable → fallo legítimo (no hay qué degradar).
    raise VisualValidationError(
        f"{label}: fluidificador no devolvió prosa utilizable en {max_attempts} intentos "
        f"(missing={last_missing}, spanish_units={last_spanish})."
    )


def _seedream_facts_verbatim(hard_fact_ids, facts: list) -> list[str]:
    """verbatim de los facts elegidos por el LLM (para el candado).

    El LLM manda las ETIQUETAS F## tal como las VE en el display (_format_facts usa
    enumerate(..., start=1) → "F01"=facts[0], "F11"=facts[10]). Se resuelve por CLAVE,
    nunca por posición — eso mata el off-by-one (el display base-1 chocaba con el
    consumer base-0). Etiqueta inexistente/mal formada → se descarta (no fatal),
    igual que antes filtraba el índice fuera de rango."""
    by_label = {f"F{i:02d}": f for i, f in enumerate(facts, start=1)}
    out = []
    for fid in (hard_fact_ids or []):
        f = by_label.get(str(fid).strip().upper()) if fid is not None else None
        if f is None:
            continue
        out.append((f.get("fact", "") if isinstance(f, dict) else str(f)))
    return out


# ═══════════════════════════════════════════════════════════════
#  DIRECCIÓN VISUAL POR INTENT (arco de retención · chat 108)
#  Espejo de TONE_INSTRUCTIONS_BY_INTENT de m01b, pero para la imagen.
#  STEERING al LLM de la Etapa 1 — NO re-reparte emotional_rank (eso es versión B).
# ═══════════════════════════════════════════════════════════════
VISUAL_INTENT_BY_INTENT: dict[str, str] = {
    "hook":           "Wide, distant framing. A figure or scene seen from afar, partly hidden. Fog/haze, cold muted palette. Mystery — pose a visual question. Avoid close detail.",
    "setup":          "Establishing, calm framing. Context-rich, neutral light. Steady and observational. Low visual tension.",
    "rising_tension": "Tighter framing creeping in. Growing shadows, off-balance composition. Unease building. Medium tension.",
    "shock":          "Close-up or extreme close-up on the decisive detail. Hard, high-contrast light. Claustrophobic, the instant itself. Peak visual tension.",
    "consequences":   "Medium framing, heavier mood. Emptiness, aftermath, weight. Subdued light. Reflective.",
    "resolution":     "Framing opens up again. Softer, calmer light. Tension releasing. Settled.",
    "outro":          "Wide, often elevated/aerial. Stillness, dawn or quiet. An open, suspended note — the silence after. Calm.",
}


def _visual_arc_block(narrative_intent: str | None) -> str:
    """Bloque DIRECCIÓN VISUAL para inyectar en el prompt de la Etapa 1.
    Si intent es None o desconocido → string vacío (fallback seguro, el prompt
    funciona igual que hoy)."""
    if not narrative_intent:
        return ""
    instr = VISUAL_INTENT_BY_INTENT.get(narrative_intent)
    if not instr:
        return ""
    return f"""
═══════════════════════════════════════════════════
VISUAL ARC OF THIS CAP — narrative_intent={narrative_intent!r}
═══════════════════════════════════════════════════
Bias the shot_scale, lighting and mood of these images toward:
{instr}
"""


def _build_seedream_prompt_step2(topic, cap_data, narration_text, anchors) -> str:
    """User-prompt del skeleton seedream: canon 2-capas + facts + anchors → pedir
    N slot-sets (uno por fragmento). El LLM elige hard_fact_ids; NO escribe cifras."""
    cap_n = cap_data["chapter_number"]
    role = cap_data.get("role") or "development"
    cap_title = cap_data.get("title") or "(sin título)"
    n = len(anchors)
    anchor_list = "\n".join(f"  [{i + 1}] «{a}»" for i, a in enumerate(anchors))
    topic_block = _build_topic_block(topic)
    canon_block = _format_seedream_canon_block(topic)
    arc_block = _visual_arc_block(cap_data.get("narrative_intent"))
    return f"""Narration (Spanish, for context only — emit JSON in English):

{narration_text}

CAP {cap_n} — {role}, title: {cap_title}

═══════════════════════════════════════════════════
TEMA
═══════════════════════════════════════════════════
{topic_block}

═══════════════════════════════════════════════════
CANON VISUAL (2 capas — verdad sellada, NO re-inferir)
═══════════════════════════════════════════════════
{canon_block}

═══════════════════════════════════════════════════
ANCHORS YA ELEGIDOS (Paso 1) — NO los elijas, ya están DADOS
═══════════════════════════════════════════════════
Fill the slots for EACH fragment below, in the SAME order (item i ↔ fragment i):
{anchor_list}

Emit EXACTLY {n} slot-objects as a JSON array.
{arc_block}
DISTRIBUTION OF emotional_rank:
- 1-2 items R1 (peak of cap: closing, revelation, biggest impact).
- 2-3 items R2 (action, strong transition, person in tension).
- Rest R3 (descriptive scene, context, ambience).

For hard_fact_ids: pick the F-labels (e.g. "F03") of verified_facts whose FIGURES
this image weaves, copied EXACTLY as labeled — and ONLY those relevant to THIS
anchor's moment (do NOT bring foundation-era figures into a peak-era beat). Do NOT
rewrite the figures.

JSON only. No markdown. No preamble."""


def _render_prompts_seedream(topic, cap_data, narration, plan, cap_number):
    """Paso 2 SEEDREAM (caps flux): skeleton (slots, Pro) → fluidificador per-item
    (teje prosa + Guarda 1 post-check) → scrub nombres + text-leakage invertida.
    Devuelve el MISMO shape de fase2a (image_prompts con prompt final),
    contrato fase2a intacto."""
    anchors = [a["anchor"] for a in plan["anchors"]]
    n = len(anchors)
    facts = topic.get("verified_facts") or []
    documented = topic.get("documented_people")
    profile = select_profile("seedream")
    prompt = _build_seedream_prompt_step2(topic, cap_data, narration, anchors)

    def _validator(parsed):
        items = parsed.get("image_prompts") if isinstance(parsed, dict) else None
        if not isinstance(items, list) or len(items) != n:
            got = len(items) if isinstance(items, list) else "no-lista"
            raise VisualValidationError(
                f"cap {cap_number} (seedream paso2): se esperaban EXACTAMENTE {n} "
                f"slot-objects, llegaron {got}."
            )
        for i, it in enumerate(items, start=1):
            if not isinstance(it, dict):
                raise VisualValidationError(f"cap {cap_number} (seedream) item {i}: no es objeto")
            ss = it.get("shot_scale")
            if ss not in VALID_SHOT_SCALES:
                raise VisualValidationError(
                    f"cap {cap_number} (seedream) item {i}: shot_scale inválido ({ss!r})")
            if not (it.get("subject") or "").strip():
                raise VisualValidationError(
                    f"cap {cap_number} (seedream) item {i}: slot 'subject' vacío")
        # candado #2: narration_anchor VERBATIM del Paso 1 (nunca del eco del LLM).
        assembled = {"image_prompts": [
            {**items[i], "narration_anchor": anchors[i]} for i in range(n)
        ]}
        return assembled

    slots_out = _call_with_validation_retry(
        prompt, _validator, cap_number,
        system_instruction=SYSTEM_INSTRUCTION_VISUAL_SEEDREAM,
        response_schema=_seedream_slots_schema(n),
        use_pro=True,
    )

    # ── fluidificador per-item + Guarda 1 + scrub + text-leakage (R3 invertida) ──
    # PARALELO: los ítems son INDEPENDIENTES (cada uno muta SÓLO su propio `it`; facts/profile/
    # documented son read-only; call_pro_json NO toca cost_tracker → sin estado compartido). Era
    # el grueso de las ~90 llamadas Pro secuenciales del topic. Orden PRESERVADO: se muta `it`
    # in-place, la lista NO se reordena. Una excepción de cualquier ítem (Guarda 1 / leakage /
    # rango) se re-lanza → falla el cap IGUAL que la versión secuencial. Cuerpo byte-idéntico.
    def _fluidify_one(i: int, it: dict) -> None:
        verbatim = _seedream_facts_verbatim(it.get("hard_fact_ids"), facts)
        locked = _classify_locked_facts(verbatim)
        # B1 §2-B: suelta medidas sobrantes (>1/imagen) ANTES de lockear → el fluidificador
        # nunca recibe una carga imposible (raíz del crash Guarda 1).
        locked = _enforce_measure_fit(locked, f"cap {cap_number} img #{i}")
        prose = _fluidify_item(it, locked, profile, f"cap {cap_number} img #{i}")
        # raw_llm_prompt = los slots crudos (auditoría m05, se conserva)
        it["raw_llm_prompt"] = json.dumps(
            {k: it.get(k) for k in (*SEEDREAM_SLOT_KEYS, "text_in_image", "hard_fact_ids")},
            ensure_ascii=False)
        # scrub nombres de PERSONA (conservado, los dos motores) ANTES del leakage.
        prose, _ = scrub_documented_names(prose, documented)
        # R3 invertida: text_in_image (rótulo de lugar) PERMITIDO; eufemismos siguen prohibidos.
        _validate_no_text_leakage(prose, f"cap {cap_number} (seedream) img #{i}",
                                  allow_intentional_text=True,
                                  intentional_text=(it.get("text_in_image") or {}).get("text", ""))
        if not (PROMPT_MIN_CHARS <= len(prose) <= KLING_PROMPT_MAX_CHARS):
            raise VisualValidationError(
                f"cap {cap_number} (seedream) img #{i}: prosa fuera de rango "
                f"({len(prose)} chars, target {PROMPT_MIN_CHARS}-{KLING_PROMPT_MAX_CHARS}).")
        it["prompt"] = prose
        it["art_profile"] = ""

    items = list(enumerate(slots_out["image_prompts"], start=1))
    if len(items) <= 1:
        for i, it in items:
            _fluidify_one(i, it)
    else:
        with ThreadPoolExecutor(max_workers=min(FLUIDIFY_MAX_WORKERS, len(items))) as _ex:
            _futs = [_ex.submit(_fluidify_one, i, it) for i, it in items]
            for _f in as_completed(_futs):
                _f.result()   # re-lanza la 1ª excepción (falla el cap, como la versión secuencial)
    slots_out["chapter_number"] = cap_number
    return slots_out


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

# Chat 54 — timing-aware anchor merge. Piso temporal entre starts de anchors
# consecutivos: si dos anchors caen más juntos que esto en el audio, la imagen del
# segundo se mostraría <este_gap y DepthFlow comprime su ciclo entero → flash
# (caso ch07 supp #3 a 0.60s). m03 fusiona el anchor apretado ANTES del Paso 2
# (la imagen anterior absorbe el tiempo). PERILLA a calibrar mirando videos; no
# clavada a fuego. Calibrado a 1.0s (chat 54): mata el flash de 0.60s pero deja
# pasar gaps ~2s que se leen bien (con 2.0s fusionaba un 1.98s sano de cap3).
MIN_ANCHOR_GAP_SEC = 1.0

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
KLING_PROMPT_MAX_CHARS = 2500   # endpoint Kling clampa a 2500; prompts densos (no aplica el 700 de Flux)

VALID_RANKS = frozenset({"R1", "R2", "R3"})

MAX_RETRY_ATTEMPTS = 3
# 1 intento original + 2 retries con feedback enriquecido. Cap más cargado
# (10 imgs sobre narr ~2000 chars) puede necesitar la 3ra vuelta cuando
# falla por anchor parafraseado en la última img. Costo: ~$0.001 extra
# en peor caso. Comportamiento normal sigue siendo 0-1 retries.

# ─── Validación regla 3 (anti-text-leakage) ───
# Patrones que indican intent de renderizar texto en la imagen, incluso si
# el LLM intenta camuflarlos con "blurred", "faded", "indistinct" etc.
#
# DOS GRUPOS por razón de CASING (no juntar):
#   - TEXT_LEAKAGE_PATTERNS: eufemismos en inglés → se corren sobre prompt.lower()
#     con IGNORECASE (matchean en cualquier capitalización, que es lo deseado).
#   - TEXT_LEAKAGE_PATTERN_PROPER_NOUN: nombre propio CAPITALIZADO entre comillas
#     (= cartel/signage literal). Depende de [A-Z] → se corre CASE-SENSITIVE sobre
#     el prompt ORIGINAL. Correrlo sobre prompt.lower()+IGNORECASE anula el [A-Z]
#     y la regla pasa a cazar "cualquier palabra de 4+ letras entre comillas",
#     disparando falsos positivos sobre comillas de énfasis ("scarred", "echoes").
#     Bug latente desde chat 32, despertado por la prosa densa de la doctrina Kling.
TEXT_LEAKAGE_PATTERNS = (
    # Frases tipo "where X name/text/label was/once was"
    r"\bwhere\s+(?:the\s+|a\s+|an\s+)?(?:name|text|label|word|words|inscription|title|sign)\s+(?:was|once was|used to be|had been)\b",
    r"\bwhere\s+(?:a\s+|the\s+)?town\s+name\b",
    # "blurred/faded/indistinct + area + name/text"
    r"\b(?:blurred|faded|indistinct|obscured)\s+(?:area|patch|spot|region)\s+(?:where|with|of|showing)\s+(?:name|text|word|label)\b",
    # "the name/word X" cuando X es algo que el LLM va a dibujar
    r"\bthe\s+(?:name|word|label|inscription)\s+['\"][^'\"]+['\"]",
    # "showing the X name/text" donde X es ubicación o entidad
    r"\bshowing\s+the\s+\w+\s+(?:name|text|label|title)\b",
)

# Nombre propio capitalizado entre comillas (cartel literal). CASE-SENSITIVE,
# se corre sobre el prompt ORIGINAL (ver comentario arriba — NO lowercasear).
TEXT_LEAKAGE_PATTERN_PROPER_NOUN = r"['\"][A-Z][a-zA-Z]{3,}['\"]"

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


_VEO_VIDEO_PROMPT_STRUCT = """ESTRUCTURA video_prompt:
- Camera movement: slow push in, slow pull out, slow pan left/right,
  static with subtle drift, orbit. PROHIBIDO cuts, jumps, fast cuts,
  zoom rapid.
- Ambient: dust drifting, fog rolling, water flowing, wind through grass,
  light slowly intensifying.
- Motion sutil sobre el sujeto: figure breathing, hair moving in wind,
  eyes blinking. NO acción fuerte (Veo prioriza estabilidad).
- Lighting consistency: la luz no cambia durante el clip.
- COMPATIBILIDAD: el video_prompt debe describir movimiento de elementos
  que ya están en el image_prompt. No agregar elementos nuevos."""


# ═══════════════════════════════════════════════════════════════
#  PASO 1 — PLANIFICACIÓN DE ANCHORS (chat 52, m03 two-step)
#
#  El LLM elige SOLO las ventanas (anchors), como un productor que marca
#  beats. NO escribe prompts de imagen (eso es el Paso 2). Schema fuerza la
#  CANTIDAD; _validate_anchor_substring + _check_supp_ordering son la red real
#  (un "" pasa el schema pero NO la validación); el fallback determinístico es
#  el último seguro y SIEMPRE devuelve exactamente n ventanas válidas.
# ═══════════════════════════════════════════════════════════════

def _carve_veo_zones(narration_text: str, veo_position: str, veo_zone_chars: int) -> tuple:
    """Carveo de zonas (zona Veo + zonas de supplementals). Devuelve
    (veo_lo, veo_hi, supps_lo, supps_hi)."""
    narration_len = len(narration_text)
    if veo_position == "start":
        return 0, veo_zone_chars, veo_zone_chars, narration_len
    # "end"
    return narration_len - veo_zone_chars, narration_len, 0, narration_len - veo_zone_chars


# ─── FALLBACK determinístico (candado de Omar #3: EXACTAMENTE n ventanas, SIEMPRE) ───

def _sentence_content_spans(text: str, lo: int, hi: int) -> list[tuple]:
    """Spans (start,end) de oraciones CON contenido dentro de [lo,hi). Corta tras .!?…"""
    spans: list[tuple] = []
    start = lo
    for m in re.finditer(r"[.!?…]+", text[lo:hi]):
        end = lo + m.end()
        if text[start:end].strip():
            spans.append((start, end))
        start = end
    if start < hi and text[start:hi].strip():
        spans.append((start, hi))
    return spans


def _merge_spans_to_n(spans: list[tuple], n: int) -> list[tuple]:
    """Funde S>=n spans en EXACTAMENTE n buckets contiguos, lo más parejo posible."""
    S = len(spans)
    base, extra, idx, out = S // n, S % n, 0, []
    for g in range(n):
        size = base + (1 if g < extra else 0)
        grp = spans[idx:idx + size]
        idx += size
        out.append((grp[0][0], grp[-1][1]))
    return out


def _merge_indices_to_n(indices: list[int], n: int) -> list[tuple]:
    """Funde C>=n índices de char en EXACTAMENTE n spans contiguos (span = first..last+1)."""
    C = len(indices)
    base, extra, idx, out = C // n, C % n, 0, []
    for g in range(n):
        size = base + (1 if g < extra else 0)
        grp = indices[idx:idx + size]
        idx += size
        out.append((grp[0], grp[-1] + 1))
    return out


def _fallback_anchor_windows(text: str, lo: int, hi: int, n: int) -> list[tuple]:
    """Devuelve EXACTAMENTE n (anchor, pos, end) contiguos, no-vacíos, no-solapados, en [lo,hi).
    Degradación (candado #3): oraciones → palabras → caracteres, para garantizar n ventanas
    incluso si hay menos oraciones (o palabras) que n. pos/end son los del span ya recortado
    (NO via narration.find → evita colisiones con substrings repetidos)."""
    sents = _sentence_content_spans(text, lo, hi)
    if len(sents) >= n:
        spans = _merge_spans_to_n(sents, n)
    else:
        words = [(lo + m.start(), lo + m.end()) for m in re.finditer(r"\S+", text[lo:hi])]
        if len(words) >= n:
            spans = _merge_spans_to_n(words, n)
        else:
            chars = [lo + i for i in range(hi - lo) if not text[lo + i].isspace()]
            if len(chars) < n:
                raise VisualValidationError(
                    f"fallback: zona [{lo},{hi}) tiene {len(chars)} chars de contenido < n={n}"
                )
            spans = _merge_indices_to_n(chars, n)

    out: list[tuple] = []
    for s, e in spans:
        raw = text[s:e]
        lead = len(raw) - len(raw.lstrip())
        anchor = raw.strip()
        pos = s + lead
        out.append((anchor, pos, pos + len(anchor)))
    return out


# ─── Schemas (R4): el schema fuerza la CANTIDAD, no el contenido ───

def _veo_anchor_schema(n: int) -> dict:
    return {
        "type": "OBJECT",
        "properties": {
            "veo_anchor": {"type": "STRING"},
            "supplemental_anchors": {
                "type": "ARRAY", "items": {"type": "STRING"},
                "minItems": n, "maxItems": n,
            },
        },
        "required": ["veo_anchor", "supplemental_anchors"],
    }


def _flux_anchor_schema(n: int) -> dict:
    return {
        "type": "OBJECT",
        "properties": {
            "anchors": {
                "type": "ARRAY", "items": {"type": "STRING"},
                "minItems": n, "maxItems": n,
            },
        },
        "required": ["anchors"],
    }


# ─── Prompts del Paso 1 (SOLO anchors; NADA de reglas de prompt de imagen) ───

def _build_plan_anchors_prompt_veo(narration_text, n, veo_position, veo_zone_text, supps_zone_text):
    return f"""Sos un editor de documentales. Tu ÚNICA tarea es ELEGIR los cortes de la narración
(anchors) que se van a ilustrar, como un productor que marca beats con sentido. NO escribís prompts
de imagen ni descripciones visuales — SOLO seleccionás fragmentos LITERALES de la narración.

El cap se ilustra con 1 clip Veo (posición={veo_position}) + {n} imágenes Flux supplementals.

[ZONA VEO] (de acá sale el anchor GLOBAL del clip Veo, 1 solo):
\"\"\"
{veo_zone_text}
\"\"\"

[ZONA SUPPLEMENTALS] (de acá salen los {n} anchors de las imágenes Flux):
\"\"\"
{supps_zone_text}
\"\"\"

REGLAS (el validador rechaza si se violan):
1. Cada anchor es substring EXACTO y literal de SU zona (copiá tal cual: sin reformular, sin
   traducir, sin recortar palabras del medio, sin cambiar puntuación).
2. EXACTAMENTE {n} anchors de supplementals, en ORDEN cronológico ascendente, SIN solaparse.
3. El `veo_anchor` sale SOLO de [ZONA VEO]; los supplementals SOLO de [ZONA SUPPLEMENTALS].
4. Cada anchor abarca un beat con sentido (no una palabra suelta). Apuntá ~40-200 chars.

OUTPUT (JSON estricto, nada más):
{{"veo_anchor": "<substring literal de ZONA VEO>", "supplemental_anchors": ["<substring 1>", "... EXACTAMENTE {n} items"]}}

NO agregues texto fuera del JSON. NO uses markdown.
"""


def _build_plan_anchors_prompt_flux(narration_text, n):
    return f"""Sos un editor de documentales. Tu ÚNICA tarea es ELEGIR los cortes de la narración
(anchors) que se van a ilustrar, como un productor que marca beats con sentido. NO escribís prompts
de imagen ni descripciones visuales — SOLO seleccionás fragmentos LITERALES de la narración.

NARRACIÓN COMPLETA DEL CAP:
\"\"\"
{narration_text}
\"\"\"

REGLAS (el validador rechaza si se violan):
1. Cada anchor es substring EXACTO y literal de la narración (sin reformular/traducir/recortar
   palabras del medio/cambiar puntuación).
2. EXACTAMENTE {n} anchors, en ORDEN cronológico ascendente, SIN solaparse. Partí mentalmente la
   narración en {n} segmentos en orden: el anchor 1 cae en el primero, el anchor {n} en el último.
3. Cada anchor abarca un beat con sentido (no una palabra suelta). Apuntá ~40-200 chars.

OUTPUT (JSON estricto, nada más):
{{"anchors": ["<substring 1>", "... EXACTAMENTE {n} items en orden"]}}

NO agregues texto fuera del JSON. NO uses markdown.
"""


# ─── Validadores del Paso 1 (reusan _validate_anchor_substring + _check_supp_ordering) ───

def _validate_plan_veo(parsed, narration, n, veo_position, cap_number):
    if not isinstance(parsed, dict):
        raise VisualValidationError(f"cap {cap_number} (plan veo): output no es dict ({type(parsed).__name__})")
    veo_anchor = parsed.get("veo_anchor")
    va_pos, va_end = _validate_anchor_substring(veo_anchor, narration, f"cap {cap_number} (plan veo) veo_anchor")

    supps = parsed.get("supplemental_anchors")
    if not isinstance(supps, list):
        raise VisualValidationError(f"cap {cap_number} (plan veo): supplemental_anchors no es lista")
    if len(supps) != n:
        raise VisualValidationError(
            f"cap {cap_number} (plan veo): {len(supps)} anchors (esperado EXACTAMENTE {n})"
        )
    out_supps: list[dict] = []
    last_pos = last_end = -1
    for idx, a in enumerate(supps, start=1):
        lbl = f"cap {cap_number} (plan veo) supp {idx}"
        pos, end = _validate_anchor_substring(a, narration, lbl)
        _check_supp_ordering(pos, end, last_pos, last_end, lbl,
                             veo_position=veo_position, veo_anchor_pos=va_pos, veo_anchor_end=va_end)
        last_pos, last_end = pos, end
        out_supps.append({"anchor": a.strip(), "pos": pos, "end": end})
    return {"veo_anchor": {"anchor": veo_anchor.strip(), "pos": va_pos, "end": va_end},
            "supplementals": out_supps}


def _validate_plan_flux(parsed, narration, n, cap_number):
    if not isinstance(parsed, dict):
        raise VisualValidationError(f"cap {cap_number} (plan flux): output no es dict ({type(parsed).__name__})")
    anchors = parsed.get("anchors")
    if not isinstance(anchors, list):
        raise VisualValidationError(f"cap {cap_number} (plan flux): 'anchors' no es lista")
    if len(anchors) != n:
        raise VisualValidationError(
            f"cap {cap_number} (plan flux): {len(anchors)} anchors (esperado EXACTAMENTE {n})"
        )
    out: list[dict] = []
    last_pos = last_end = -1
    for idx, a in enumerate(anchors, start=1):
        lbl = f"cap {cap_number} (plan flux) anchor {idx}"
        pos, end = _validate_anchor_substring(a, narration, lbl)
        _check_supp_ordering(pos, end, last_pos, last_end, lbl)  # veo_position=None → sin disjunción Veo
        last_pos, last_end = pos, end
        out.append({"anchor": a.strip(), "pos": pos, "end": end})
    return {"anchors": out}


def _plan_anchors(
    narration_text: str,
    n: int,
    engine: str,
    veo_position: str | None = None,
    veo_zone_chars: int | None = None,
    cap_number: int = 0,
) -> dict:
    """PASO 1 — el LLM elige los anchors (productor). Schema fuerza cantidad; validación real =
    _validate_anchor_substring + _check_supp_ordering; si no converge → fallback determinístico
    (EXACTAMENTE n ventanas SIEMPRE). OUT (pos/end ya calculados para que el Paso 2 no recompute):

      veo : {"veo_anchor": {anchor,pos,end}, "supplementals": [{anchor,pos,end} × n]}
      flux: {"anchors": [{anchor,pos,end} × n]}
    """
    engine = (engine or "").lower()
    if engine == "veo":
        vlo, vhi, slo, shi = _carve_veo_zones(narration_text, veo_position, veo_zone_chars)
        prompt = _build_plan_anchors_prompt_veo(
            narration_text, n, veo_position, narration_text[vlo:vhi], narration_text[slo:shi])
        try:
            return _call_with_validation_retry(
                prompt,
                validator_fn=lambda p: _validate_plan_veo(p, narration_text, n, veo_position, cap_number),
                cap_number=cap_number,
                checklist=_ANCHOR_ONLY_RETRY_CHECKLIST,
                response_schema=_veo_anchor_schema(n),
            )
        except VisualValidationError as e:
            print(f"  [03] cap {cap_number}: anchors por fallback determinístico (LLM no convergió) — {str(e)[:80]}")
            va = _fallback_anchor_windows(narration_text, vlo, vhi, 1)[0]
            supps = _fallback_anchor_windows(narration_text, slo, shi, n)
            return {"veo_anchor": {"anchor": va[0], "pos": va[1], "end": va[2]},
                    "supplementals": [{"anchor": a, "pos": p, "end": e} for (a, p, e) in supps]}

    elif engine == "flux":
        prompt = _build_plan_anchors_prompt_flux(narration_text, n)
        try:
            return _call_with_validation_retry(
                prompt,
                validator_fn=lambda p: _validate_plan_flux(p, narration_text, n, cap_number),
                cap_number=cap_number,
                checklist=_ANCHOR_ONLY_RETRY_CHECKLIST,
                response_schema=_flux_anchor_schema(n),
            )
        except VisualValidationError as e:
            print(f"  [03] cap {cap_number}: anchors por fallback determinístico (LLM no convergió) — {str(e)[:80]}")
            w = _fallback_anchor_windows(narration_text, 0, len(narration_text), n)
            return {"anchors": [{"anchor": a, "pos": p, "end": e} for (a, p, e) in w]}

    raise ValueError(f"_plan_anchors: engine '{engine}' inválido (esperado 'veo' o 'flux')")


# ═══════════════════════════════════════════════════════════════
#  RECONCILIACIÓN TEMPORAL (chat 54 — timing-aware anchor merge)
# ═══════════════════════════════════════════════════════════════

def _load_cap_word_timestamps(video_id: str, cap_id: str) -> list[dict] | None:
    """Carga los word-timestamps del cap (output/audio/{video_id}/{cap_id}_timestamps.json).

    MISMO path que fase2b. Estos archivos los escribe audio_manager ANTES de m03
    (el audio corre antes de los prompts). None si no existe/ilegible → sin
    reconciliación (fallback seguro: el cap conserva su n original).
    """
    p = OUTPUT_DIR / "audio" / video_id / f"{cap_id}_timestamps.json"
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def _reconcile_anchor_timing(
    plan: dict,
    engine: str,
    words: list[dict],
    min_count: int,
    cap_number: int = 0,
) -> tuple[dict, int]:
    """Fusiona anchors temporalmente apretados ANTES del Paso 2 (sin LLM).

    Mide el `start` de cada anchor con el MISMO matcher que fase2b
    (compute_anchor_starts). Si gap[i+1]-gap[i] < MIN_ANCHOR_GAP_SEC, descarta el
    anchor i+1 (el apretado) → el anterior (i) absorbe su tiempo. Repite hasta que
    todos los gaps queden ≥ el piso. Fusionar = sacar el dict entero de la lista.

    Guarda de mínimo: nunca baja de `min_count` (MIN_IMAGES_FLUX flux /
    MIN_FLUX_EXTRAS veo). Si tocaría el mínimo, deja de fusionar y loguea [audit].

    Si el matcher falla (algún anchor no matchea / starts no crecientes) → no toca
    nada (fallback seguro; fase2b igual repartirá con su piso 0.05 como última red).

    Aplica a AMBOS caminos: el plan trae los anchors en `anchors` (flux) o en
    `supplementals` (veo). El `veo_anchor` (el clip Veo) NO se toca.

    Returns:
        (plan, n_dropped). El plan tiene la lista reducida; n' = len(lista). Los
        renderers (_render_prompts_*) derivan n de len(plan[...]) → reciben n' solo.
    """
    key = "supplementals" if engine == "veo" else "anchors"
    items = plan.get(key) or []
    if len(items) < 2:
        return plan, 0

    starts = compute_anchor_starts([it.get("anchor", "") for it in items], words)
    if starts is None:
        print(f"  [03][audit] cap {cap_number}: matcher anchor→tiempo no resolvió "
              f"(anchor sin match o starts no crecientes) — sin reconciliación temporal")
        return plan, 0

    survivors = list(items)
    s = list(starts)
    dropped = 0
    i = 0
    while i + 1 < len(survivors):
        gap = s[i + 1] - s[i]
        if gap < MIN_ANCHOR_GAP_SEC:
            if len(survivors) <= min_count:
                print(f"  [03][audit] cap {cap_number}: gap {gap:.2f}s < "
                      f"{MIN_ANCHOR_GAP_SEC}s en img #{i + 2} pero ya en mínimo "
                      f"({min_count}) — NO fusiono (¿_calculate_*_count pidió de más?)")
                break
            # Descartar el anchor apretado (i+1): el anterior (i) absorbe su tiempo.
            # NO avanzar i: re-chequear el gap del nuevo i+1 contra el mismo i.
            del survivors[i + 1]
            del s[i + 1]
            dropped += 1
        else:
            i += 1

    if dropped:
        plan[key] = survivors
        print(f"  [03] cap {cap_number}: timing-aware merge — {dropped} anchor(s) "
              f"fusionado(s) por gap < {MIN_ANCHOR_GAP_SEC}s → {len(survivors)} "
              f"{'supplementals' if engine == 'veo' else 'imgs'} (el anterior absorbe el tiempo)")

    return plan, dropped


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


def _validate_no_text_leakage(prompt: str, label: str,
                              allow_intentional_text: bool = False,
                              intentional_text: str = "") -> None:
    """Regla 3: detecta patrones de instrucción de texto en imagen.

    El LLM a veces esquiva la regla 3 del prompt con eufemismos tipo
    "blurred area where name was". Acá los detectamos por regex.
    Raise VisualValidationError con mensaje educativo si encuentra match.

    Dos pasadas por CASING (ver comentario en TEXT_LEAKAGE_PATTERNS):
      1) eufemismos en inglés → case-insensitive sobre prompt.lower()
      2) nombre propio capitalizado entre comillas → CASE-SENSITIVE sobre el
         prompt ORIGINAL (si se lowercasea o se usa IGNORECASE, [A-Z] queda
         anulado y caza comillas de énfasis = falso positivo).

    allow_intentional_text (eslabón 3b, R3 INVERTIDA para Seedream): cuando True,
    se SALTEA la pasada 2 (texto entrecomillado = rótulo intencional del slot
    text_in_image, herramienta legítima de Seedream). La pasada 1 (eufemismos)
    se mantiene; los nombres de PERSONA los sigue cortando scrub_documented_names
    (aplicado aparte, en los dos motores). Default False → Kling/Flux intactos.

    intentional_text (camino C, fix 110b): el TITULAR sancionado del slot
    text_in_image. Con allow_intentional_text=True, si un patrón de Pasada 1 matchea
    pero el texto ENTRE COMILLAS del match es ese titular (normalizado), NO es fuga —
    es la propia salida legítima de Seedream → se exime y se sigue. Los eufemismos sin
    comillas (ocultar texto) no tienen contenido comparable → siguen FATALES. Vacío
    (default) → no exime nada (present=false: cualquier comilla sigue siendo fuga real).
    """
    matched_fragment = None
    norm_intentional = intentional_text.strip().casefold() if intentional_text else ""

    # Pasada 1 — eufemismos (case-insensitive sobre minúscula). SIEMPRE corre.
    prompt_lc = prompt.lower()
    for pattern in TEXT_LEAKAGE_PATTERNS:
        m = re.search(pattern, prompt_lc, re.IGNORECASE)
        if not m:
            continue
        frag = m.group(0)
        # Camino C: si el match es el TITULAR sancionado (texto entre comillas ==
        # intentional_text, normalizado, igual o uno contiene al otro) → NO es fuga;
        # seguir evaluando los demás patrones. Sin comillas (eufemismo) → no exime.
        if allow_intentional_text and norm_intentional:
            q = re.search(r"['\"]([^'\"]+)['\"]", frag)
            if q:
                qn = q.group(1).strip().casefold()
                if qn == norm_intentional or qn in norm_intentional or norm_intentional in qn:
                    continue
        matched_fragment = frag
        break

    # Pasada 2 — nombre propio capitalizado entre comillas (case-sensitive,
    # prompt ORIGINAL, SIN IGNORECASE). Solo si la pasada 1 no encontró nada.
    # Seedream (allow_intentional_text) la saltea: las comillas son su herramienta.
    if matched_fragment is None and not allow_intentional_text:
        m = re.search(TEXT_LEAKAGE_PATTERN_PROPER_NOUN, prompt)
        if m:
            matched_fragment = m.group(0)

    if matched_fragment is not None:
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


def _check_supp_ordering(
    sp_pos: int,
    sp_end: int,
    last_pos: int,
    last_end: int,
    sup_label: str,
    veo_position: str | None = None,
    veo_anchor_pos: int | None = None,
    veo_anchor_end: int | None = None,
) -> None:
    """Chequeos de orden cronológico estricto + no-solapa entre anchors + disjunción con la zona
    Veo. Extraído VERBATIM del loop de validación de caps (chat 52 m03 two-step) para REUSO en
    _plan_anchors (Paso 1). Lógica y mensajes idénticos. Raises VisualValidationError; no devuelve.

    veo_position=None (camino flux/plan sin Veo) → se saltean los dos checks de disjunción con Veo.
    """
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
    if veo_position == "start" and veo_anchor_end is not None and sp_pos < veo_anchor_end:
        raise VisualValidationError(
            f"{sup_label}: anchor solapa con la zona Veo "
            f"(veo_position=start, veo_anchor_end={veo_anchor_end}, "
            f"sp_pos={sp_pos}). Los supplementals deben venir DESPUÉS "
            f"del anchor Veo."
        )
    if veo_position == "end" and veo_anchor_pos is not None and sp_end > veo_anchor_pos:
        raise VisualValidationError(
            f"{sup_label}: anchor solapa con la zona Veo "
            f"(veo_position=end, veo_anchor_pos={veo_anchor_pos}, "
            f"sp_end={sp_end}). Los supplementals deben venir ANTES "
            f"del anchor Veo."
        )


# ═══════════════════════════════════════════════════════════════
#  LLAMADA FLASH CON RETRY POR FEEDBACK
# ═══════════════════════════════════════════════════════════════

# Checklist por defecto (caps veo/flux completos): reglas de prompt 6/9 + anchor 7/8.
_DEFAULT_RETRY_CHECKLIST = """  □ REGLA 6 — Largo del prompt: 120-400 chars (target 180-300).
    Pasarte de 400 indica metadatos técnicos o redundancia.

  □ REGLA 7 — narration_anchor = SUBSTRING EXACTO de la narración del
    cap. Sin reformular, sin traducir, sin recortar palabras del medio,
    sin cambiar puntuación. Copiá literal.

  □ REGLA 8 — anchors en orden ESTRICTAMENTE creciente sobre la
    narración, SIN solapamiento (el final de un anchor < el inicio
    del siguiente).

  □ REGLA 9 — Cada prompt incluye al menos UN marcador temporal
    explícito ('1960s', 'vintage', 'period-correct', '1968', etc.)."""

# Checklist recortado SOLO a reglas 7/8 (Paso 1 _plan_anchors: solo elige anchors, sin reglas
# de prompt — esas viven en el Paso 2). Chat 52 m03 two-step.
_ANCHOR_ONLY_RETRY_CHECKLIST = """  □ REGLA 7 — cada anchor = SUBSTRING EXACTO de la narración del cap.
    Sin reformular, sin traducir, sin recortar palabras del medio, sin
    cambiar puntuación. Copiá literal de la zona indicada.

  □ REGLA 8 — anchors en orden ESTRICTAMENTE creciente sobre la
    narración, SIN solapamiento (el final de un anchor < el inicio del
    siguiente). Cantidad EXACTA pedida, ni más ni menos."""


def _call_with_validation_retry(
    prompt: str,
    validator_fn,
    cap_number: int,
    system_instruction: str | None = None,
    max_attempts: int = MAX_RETRY_ATTEMPTS,
    checklist: str | None = None,
    response_schema=None,
    use_pro: bool = False,
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
        checklist: bloque de checklist para el feedback. None (default) usa el
            checklist completo 6/7/8/9 (comportamiento idéntico al previo).
            _plan_anchors pasa el recortado a 7/8.
        response_schema: opcional, se pasa a call_flash_json (R4). None (default)
            = sin schema, comportamiento idéntico al previo.
    """
    checklist_block = checklist if checklist is not None else _DEFAULT_RETRY_CHECKLIST
    attempt_prompt = prompt
    last_error: VisualValidationError | None = None
    # use_pro (eslabón 3b): el skeleton seedream razona (slots + relevancia de facts) →
    # Pro, como el lab. Kling/Flux quedan en Flash (default) → byte-idénticos.
    _caller = call_pro_json if use_pro else call_flash_json

    for attempt in range(1, max_attempts + 1):
        raw = _caller(attempt_prompt, system_instruction=system_instruction,
                      response_schema=response_schema)
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

{checklist_block}

CORREGÍLO. Reescribí el JSON COMPLETO respetando TODAS las reglas
de arriba a la vez. Generá la respuesta nueva desde cero, no parches
sobre la anterior.
"""
            attempt_prompt = prompt + feedback

    # Inalcanzable en teoría
    if last_error:
        raise last_error
    raise VisualValidationError(f"cap {cap_number}: retry exhausted sin error capturado")


# ── SEEDREAM path VEO (eslabón VEO_SEEDREAM_1080 · FIX A) ──
# Un cap veo es HÍBRIDO: 1 foto Veo (image_prompt, animada con i2v) + N stills
# DepthFlow (supplementals). TODAS las fotos son fotos → van por el skeleton
# seedream (canon 2-capas + slots + fluidificador + candado), igual que caps 2-6.
# Lo único que NO es foto es el video_prompt (movimiento de la foto Veo): no es
# slot del skeleton → call de motion dedicada, sembrada por el first-frame.

_SEEDREAM_MOTION_SYSTEM = """You are a Veo motion editor. Given a FIRST-FRAME still (already final — do NOT change it) you write ONLY the camera/ambient motion that animates THAT still. Describe movement of elements ALREADY present in the first-frame; add NO new elements, NO new facts, NO numbers, NO on-image text, NO person names. Keep lighting constant during the clip. English prose, 2-3 sentences. Return ONLY the video_prompt field."""

_SEEDREAM_MOTION_SCHEMA = {"type": "OBJECT",
                          "properties": {"video_prompt": {"type": "STRING"}},
                          "required": ["video_prompt"]}


def _seedream_video_prompt(image_prompt: str, label: str, max_attempts: int = 3) -> str:
    """Genera el video_prompt (motion) de la foto Veo con una call Pro dedicada,
    sembrada por la prosa del first-frame + la doctrina _VEO_VIDEO_PROMPT_STRUCT.
    El motion NO pasa por el candado (no lleva cifras) — el system le prohíbe
    inventar datos/texto. Reintenta si la longitud cae fuera de rango."""
    user = f"""FIRST-FRAME (the still that Veo will animate — already final):
{image_prompt}

{_VEO_VIDEO_PROMPT_STRUCT}

Write ONLY the Veo motion prompt for THIS first-frame: camera movement + ambient
motion + subtle motion on the subject, all of elements ALREADY in the first-frame.
2-3 sentences of fluent English."""
    last = ""
    for attempt in range(1, max_attempts + 1):
        out = call_pro_json(user, system_instruction=_SEEDREAM_MOTION_SYSTEM,
                            response_schema=_SEEDREAM_MOTION_SCHEMA)
        vp = (out or {}).get("video_prompt", "") if isinstance(out, dict) else ""
        vp = re.sub(r"\s+", " ", vp).strip()
        last = vp
        try:
            _validate_prompt_length(vp, label)
            return vp
        except VisualValidationError:
            if attempt < max_attempts:
                user += (f"\n\nRETRY: the previous motion was {len(vp)} chars; it must be "
                         f"between {PROMPT_MIN_CHARS} and {PROMPT_MAX_CHARS} chars. Adjust length.")
    # último intento: revalidar para propagar el error real (RUIDOSO)
    _validate_prompt_length(last, label)
    return last


def _render_prompts_seedream_veo(topic, cap_data, narration, plan, veo_position, cap_number):
    """Paso 2 VEO bajo seedream. Reusa el skeleton de caps flux para TODAS las fotos
    vía un plan sintético [veo_anchor]+supplementals → resultado[0]=foto Veo
    (image_prompt), resultado[1..N]=stills DepthFlow (supplementals). El video_prompt
    (motion de la foto Veo) sale de una call dedicada. Devuelve el MISMO shape
    de fase2a (contrato intacto)."""
    veo_anchor = plan["veo_anchor"]["anchor"]
    supp_anchors = [s["anchor"] for s in plan["supplementals"]]

    # Plan sintético: la foto Veo PRIMERO, luego las N stills. El skeleton trata a
    # todas como fotos (canon 2-capas + candado), igual que caps 2-6.
    synth_plan = {"anchors": [{"anchor": veo_anchor}] + [{"anchor": a} for a in supp_anchors]}
    seed_out = _render_prompts_seedream(topic, cap_data, narration, synth_plan, cap_number)
    items = seed_out["image_prompts"]
    if not items:
        raise VisualValidationError(f"cap {cap_number} (veo-seedream): skeleton no devolvió fotos")
    image_item = items[0]
    supp_items = items[1:]

    # video_prompt (motion) de la foto Veo — call dedicada, sembrada por el first-frame.
    video_prompt = _seedream_video_prompt(
        image_item["prompt"], f"cap {cap_number} (veo-seedream) video_prompt")

    return {
        "chapter_number": cap_number,
        "image_prompt": image_item["prompt"],
        "video_prompt": video_prompt,
        "subject_ref": (image_item.get("subject_ref") or "establishing_shot"),
        "art_profile": "",
        "narration_anchor": veo_anchor,
        "veo_position": veo_position,
        "supplemental_image_prompts": [
            {"prompt": it["prompt"],
             "narration_anchor": it["narration_anchor"],
             "art_profile": "",
             "raw_llm_prompt": it.get("raw_llm_prompt")}
            for it in supp_items
        ],
    }


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

    # chat 117: m03 solo soporta seedream. Los paths flux/kling/veo-old fueron removidos
    # → un misconfig futuro falla RUIDOSO acá, no contra código borrado.
    if api.image_engine != "seedream":
        raise ValueError(
            "m03 solo soporta image_engine='seedream'. Los paths flux/kling/veo-old "
            "fueron removidos en chat 117. Ajustá config.image_engine='seedream'.")

    # Chat 54: video_id para resolver los chXX_timestamps.json (timing-aware merge).
    # En este pipeline video_id == topic_id; el sync_map lo trae explícito.
    video_id = (sync_map or {}).get("video_id") or topic_id

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

    def _process_one_cap(cap_n: int) -> dict:
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
            # CHAT 52 (m03 two-step): PASO 1 elige los anchors (productor LLM + fallback
            # determinístico), PASO 2 escribe los prompts con cada anchor YA fijo. El "anchor vacío"
            # es imposible por construcción (anchor = input). cap_out sale del render seedream-veo
            # con shape idéntico al contrato fase2a (sagrado).
            plan = _plan_anchors(
                narration_text, n_flux_extras, "veo",
                veo_position=veo_position, veo_zone_chars=veo_zone_chars, cap_number=cap_n,
            )
            # Chat 54: reconciliación temporal — fusiona supplementals apretados
            # (mata el flash de DepthFlow) ANTES del Paso 2. Guarda: MIN_FLUX_EXTRAS.
            words_ts = _load_cap_word_timestamps(video_id, cap_id)
            if words_ts:
                plan, _ = _reconcile_anchor_timing(
                    plan, "veo", words_ts, MIN_FLUX_EXTRAS, cap_n)
            # chat 117: motor único seedream. Las fotos del cap veo (foto Veo + N stills)
            # van por el skeleton; el motion por call dedicada. Prosa FINAL → sin tail-bake.
            cap_out = _render_prompts_seedream_veo(topic, sch, narration_text, plan, veo_position, cap_n)
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
            # CHAT 52 (m03 two-step): PASO 1 elige los anchors (productor LLM + fallback
            # determinístico), PASO 2 escribe los prompts con cada anchor YA fijo. Mata el "anchor
            # vacío" Y el "anchor fuera de orden" (el Paso 1 los ordena). cap_out sale del render
            # seedream con shape idéntico al contrato fase2a.
            plan = _plan_anchors(narration_text, n_images, "flux", cap_number=cap_n)
            # Chat 54: reconciliación temporal — fusiona anchors apretados (mata el
            # flash de DepthFlow) ANTES del Paso 2. Guarda: MIN_IMAGES_FLUX.
            words_ts = _load_cap_word_timestamps(video_id, cap_id)
            if words_ts:
                plan, _ = _reconcile_anchor_timing(
                    plan, "flux", words_ts, MIN_IMAGES_FLUX, cap_n)
            # ESLABÓN 3b: Seedream usa el skeleton + fluidificador (prosa ya FINAL,
            # con Guarda 1 aplicada dentro) → NO tail-bake.
            cap_out = _render_prompts_seedream(topic, sch, narration_text, plan, cap_n)
            # No-op desde chat 19 (catálogo desconectado). NO tocar.
            cap_out = _stitch_zone2_into_cap_flux(cap_out)
            print(f"  [03] cap {cap_n} (flux) ✓ {len(cap_out['image_prompts'])} imgs validadas")

        else:
            raise ValueError(
                f"cap {cap_n}: render_engine='{engine}' inválido (esperado 'veo' o 'flux')"
            )

        return cap_out

    # PARALELO por-cap: corre los 7 caps a la vez (solapa las llamadas de slots). Reensamblado
    # POR ÍNDICE (no por orden de llegada). Excepción de cualquier cap se re-lanza → falla el m03
    # igual que la versión secuencial. Anidado con el fluidify paralelo de _render_prompts_seedream.
    _cap_ns = list(range(1, EXPECTED_CHAPTER_COUNT + 1))
    _cap_results: dict[int, dict] = {}
    with ThreadPoolExecutor(max_workers=min(CAP_MAX_WORKERS, len(_cap_ns))) as _cex:
        _cfuts = {_cex.submit(_process_one_cap, n): n for n in _cap_ns}
        for _cf in as_completed(_cfuts):
            _cap_results[_cfuts[_cf]] = _cf.result()   # re-lanza excepción del cap
    output_chapters = [_cap_results[n] for n in _cap_ns]   # orden por índice, no por llegada

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
