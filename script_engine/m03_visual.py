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
from gemini_helpers import call_flash_json
from nicho_config import get_active_nicho
from anchor_timing import compute_anchor_starts
from engine_profiles import select_profile
from script_engine import m03_imagenes_v3 as v3img
from script_engine import m03_expediente as mexp


# Enums de shot_scale / light_mode. VALID_SHOT_SCALES lo usa el post-check de slots del skeleton seedream.
VALID_SHOT_SCALES = frozenset({"extreme_wide", "wide", "medium", "close", "detail"})
VALID_LIGHT_MODES = frozenset({"night", "day", "golden"})


# ═══════════════════════════════════════════════════════════════
#  SEEDREAM — CASILLEROS (Opus) + EXPEDIENTE + ARMADO POR CÓDIGO (F50)
# ═══════════════════════════════════════════════════════════════
#
# El LLM NO redacta prosa libre: RELLENA SLOTS (casilleros) con un expediente por foto (año, lugar, párrafo de la
# voz, escenas, hechos, citas, personas, grupos de gente del canon). El código arma la prosa en el orden medido y F8
# la revisa (si queda un problema se saca la frase). F50 borró el tejido de Flash, la Guarda 1 / candado de cifras y
# el re-tejido: la candidata de F46b–F49 los reemplazó (DECISIONES 2026-10-28 11:15).

# Slots que emite el LLM (craft Kling re-empaquetado como casilleros).
SEEDREAM_SLOT_KEYS = (
    "subject", "action", "gaze_interaction", "setting", "color_palette",
    "props_detail", "shot_scale", "camera_angle", "lens_technique",
    "lighting", "mood", "style",
)

# F50 B/C: Opus llena los casilleros de las fotos y escribe el movimiento del clip Veo; el código arma la prosa (sin
# tejido de Flash). Una sola fuente de modelo para las dos cosas.
MODELO_CASILLEROS = "claude-opus-5-5"     # DECISIONES: 2026-10-28 03:30–03:34 y 11:15 (Opus se queda)

# Paralelismo por-CAP (los 7 caps son independientes: leen skel/narr/sync_map read-only,
# escriben solo su propio cap_out). Solapa las 7 llamadas de casilleros (1/cap).
CAP_MAX_WORKERS = 7

# HANDOFF_138a: la doctrina Seedream se NOMBRA en bloques para compartirla con m09
# (hero de miniaturas) SIN copiar-pegar. El SI ensamblado abajo queda IDÉNTICO char-a-char
# al anterior — cero cambio de doctrina, solo se nombra (concatenación, no f-string).
DOCTRINE_R6_PHYSICAL_TRANSLATION = """PHYSICAL TRANSLATION — THE ENGINE IS A PAINTER, NOT AN ACTOR (R6):
- Internal states DO NOT render. Never write a bare abstract emotion ("fear",
  "terror", "dread", "panic", "despair") and never stack two or more emotions on
  one face (a triple like "terror, defiance and plea" renders as a neutral
  composite). ONE dominant emotion per face.
- Every emotion is written ONLY as its paintable physical evidence: facial
  musculature (jaw clenched, lips pressed thin, brow knotted), eyes (pupils
  dilated, whites visible above the iris, eyelids strained open), posture
  (shoulders drawn up, knuckles white around a bar, body pressed against a wall),
  and involuntary signs (tears cutting clean tracks through grime, a trembling
  jaw, rapid shallow breathing shown as a half-open mouth).
- State the emotion through 2-3 concrete physical signs — the emotion word alone
  is FORBIDDEN in any slot."""

DOCTRINE_BODY_CARRIES = """BODY CARRIES THE SITUATION (applies to EVERY human figure): the body physically
wears the conditions THIS beat narrates, BEFORE the face even shows emotion.
Chest-deep floodwater → clothes soaked dark and clinging, hair plastered to the
skull, skin slick with dirty water, grime waterlines on face and neck. Days
trapped without rescue → hollow exhausted eyes, cracked lips, accumulated filth.
Fire or smoke → soot streaks, sweat tracks through ash. A clean, dry, groomed
face in a disaster scene is a CONTINUITY ERROR. Draw the specific marks from the
beat's narrated conditions; never default to a presentable face."""

DOCTRINE_PEOPLE = """PEOPLE:
- DEMOGRAPHY IS MANDATORY: every human figure states ethnicity + approximate age + build, taken from demographics (and from a documented person's appearance_canon when it is one), matching what the beat narrates. State the ethnicity explicitly whenever the canon gives it — a vague collective descriptor for a crowd (e.g. "a diverse group") does not satisfy this.
- GROUPS — compose first, then individuate: in a group shot most figures read by FORM, not face — shown from behind, in a wide plane within the architecture, by a detail of hands or feet, or as a rim-lit silhouette whose shape reads cleanly. A front-lit face sunk into flat black shadow is NOT a valid technique; it reads as a mistake. The 2-3 figures that DO show a face are each described distinctly and concretely (its own age, build, position and action) — never one collective description applied to N people.
- ORDINARY PERIOD FACES: visible faces carry ordinary, period-worn features (weathered, lined, work-hardened, an incomplete set of teeth). Describe by appearance and era, never by a proper name, and never by reference to an actor, a celebrity or a film character."""

DOCTRINE_R5_CEILING = """WITHIN the monetization ceiling (R5, HARD CAP, do not soften): terror is built from SCALE + LIGHT + EMPTY apparatus + loaded LIVING faces — NEVER lifeless bodies, never fresh graphic blood, never the moment of harm. Show the OUTCOME/charged empty space, never the mechanism centered."""

SYSTEM_INSTRUCTION_VISUAL_SEEDREAM = (
    """You are the IMAGE DIRECTOR of a faceless dark-history documentary channel. You do NOT write a free prose prompt: you FILL the slots (casilleros) of EACH image. Emit a JSON ARRAY of N slot-objects, one per given narration fragment, in the SAME order (item i fills the slots for fragment i). All slot VALUES in ENGLISH.

Definition of each slot (what goes in each casillero — this is the craft, model-agnostic):

- subject: who/what is the focus. For people: integrate the LOCAL ethnicity of the topic's GEO (R1), period-correct, NEVER a person's proper name (R3a) — describe by appearance/role. — if the focus object is in foto_madre_ref, name it but do NOT re-describe its shape/pose (the anchor holds it).
- action: the VERB of the anchor — the EXACT moment it narrates (R11), not the aftermath. What is happening. For a place/object with no human action, the state/movement of the scene. — for an anchored object, narrate the action WITHOUT forcing its orientation or structure (no "suspended vertically", no "encased in").
- gaze_interaction: where the subject looks / how it touches objects; on an R1 hero beat the face/eyes to the front (R8). If no human, the focal direction of the scene. Emotion on the face follows PHYSICAL TRANSLATION (R6): physical signs, never the emotion word.
- setting: the place, period-correct (R4, anti-medieval), dressed/placed by the narration of THIS beat, not by cliché (R10). No striped prison uniforms.
- color_palette: the palette of the era AND of THIS specific place (from the visual canon provided — era layer + sourced place layer).
- props_detail: ONE loaded focal prop, never an empty plate (R8). — never restate the form of an object already in foto_madre_ref.
- shot_scale: one of extreme_wide|wide|medium|close|detail. WIDE/EXTREME_WIDE dominates for establishing/architecture/scale/mass events; medium/close ONLY for one human emotion or one texture detail (R7).
- camera_angle: e.g. low angle for scale, eye-level, high angle (R7).
- lens_technique: e.g. deep depth of field, shallow depth of field, 85mm lens.
- lighting: light by the EVENT (R12) — beats of the SAME event share ONE light. overcast daylight, golden hour, low-key night, etc.
- mood: the emotional register stated ONLY through paintable physics (R6): light, weather, and the human physical signs defined in PHYSICAL TRANSLATION — never a bare emotion word. """ + DOCTRINE_R5_CEILING + """
- style: the channel constant — documentary photographic realism, dark-history, faceless. (This is a slot, NOT a harness tail.)
- text_in_image: a label when the scene legitimately carries text — a literal sign/inscription/number (building number, carved place name), OR a period newspaper headline / wanted-notice when the anchor narrates a notable EVENT (an escape, a scandal, a ruling) and a headline would authentically illustrate it. Use SPARINGLY — only when it ADDS to the beat, never decorative, a minority of images per cap at most. present=false for ordinary people/atmosphere scenes with no narrated text; NEVER a person's proper name. If present=true: text = the literal content IN SPANISH (the audience reads Spanish — a headline reads 'PRÓFUGO', not 'ESCAPED'), font (carved/block/serif/newsprint...), location (over the entrance / front page...). Seedream renders quoted text legibly — allowed and intended.
- hard_fact_ids: the F-labels (e.g. ["F03","F10"]) of the provided verified_facts whose FIGURES this image actually shows, copied EXACTLY as labeled in the list. Do NOT write the figures yourself — ONLY pick labels RELEVANT to THIS anchor's moment AND place. A figure belongs here only if THIS image depicts it: do NOT attach a building's structural figures (floors, height, year built) to a people/farm/landscape anchor, nor foundation/closing figures to a peak beat. When in doubt, leave it EMPTY — an honest [] is better than an irrelevant figure forced into the scene (which the locked-figures guard will reject downstream). [] if none apply.
- subject_ref: "main_subject" if there is a protagonist; else "establishing_shot" / "interior_scene" / "landscape_view".
- foto_madre_ref: a LIST (array) of the recurring documented objects this image DEPICTS as its focus — usually one, sometimes none, at most TWO. The visual canon above names the central subject and any documented objects. Include an object's canonical name in the list when THIS beat's focus IS that recurring object — even when the narration refers to it by metaphor, function or material rather than plainly (its identity is the same object). Use the exact string "__subject__" for the central recurring subject, or the exact name shown after "objeto:" in OBJETOS DOCUMENTADOS for a documented object. Default []: leave the list EMPTY unless an object is the actual focus of THIS image — an object merely mentioned, alluded to, or sitting in the background does NOT go in the list (its form is already held by the prose slots). Up to TWO refs: list a ref for EACH documented object that is a genuine co-focus of THIS beat — e.g. a cutaway/composite that shows two anchored objects together. NEVER more than two. If only one object is the focus, list just that one. This slot is routing only — it is NOT rendered as text. ANCHOR HOLDS THE FORM: when an object is listed in foto_madre_ref, a reference image already fixes its shape, proportion, orientation and internal structure. Therefore, in the other slots, describe only what that object DOES and WHERE it is (its action, its place in the scene) — NEVER its form, pose, angle, or how it is built. Do NOT write a verb or a prop detail that forces a specific orientation or adds structure to an anchored object (e.g. "suspended vertically", "laid along the hull", "encased in a frame", "lowered into the core"). Narrate the moment at a level that leaves the object's physical form entirely to its reference image. This applies ONLY to objects that are in foto_madre_ref; unanchored objects are still described in full by the prose as before. ✓ conceptual: "the crew lowers the vessel into place" (action only, no form) · ✗ "the tall vertical vessel is lowered" (imposes form on an anchored object). STATE MUST MATCH THE BEAT: the reference image fixes the subject's CANONICAL form (the distinctive_features form). If THIS beat narrates the subject in a materially DIFFERENT physical configuration — before a major remodelling, under construction, ruined or mutilated, with parts the canonical form lacks or missing parts it has — then leave foto_madre_ref EMPTY for this image and let the prose describe that narrated state IN DETAIL, drawn from condition_evolution (at_event or later, per the beat's moment). Keep the anchor only when the beat shows the subject in its recognisable canonical form. ✓ conceptual: a beat set before the subject's great rebuild → no anchor, the prose draws the original configuration from at_event · ✓ a beat showing the subject in its recognisable form → normal anchor. PLACES: when the central subject is a PLACE or establishment (a fixed site, not a movable object), its reference image is the ESTABLISHING/AERIAL view of the whole complex. Use __subject__ ONLY on establishing/exterior beats that show the site from outside or above — its identifying silhouette, footprint, towers and building arrangement (subject_ref establishing_shot or an exterior main_subject). Interior scenes, generic rooms, corridors and close detail shots leave foto_madre_ref EMPTY: their identity is NOT the building's exterior form, and the anchor would fight the scene. ✓ conceptual: an aerial of the whole compound → __subject__ · ✗ a lone cell interior → empty.
- emotional_rank: "R1" (peak/hero) | "R2" (action) | "R3" (atmosphere) — see distribution in the user prompt.

DIRECTIVES — the visual canon is a CONTRACT, not decoration. Draw from it:

STATE BY BEAT (applies to EVERY item, anchored or not): each image declares the subject's physical state consistent with the moment it narrates, drawing that state from condition_evolution (at_event for the event moment, later for the aftermath). Never blend two states in one image.

"""
    + DOCTRINE_R6_PHYSICAL_TRANSLATION + """

"""
    + DOCTRINE_BODY_CARRIES + """

"""
    + DOCTRINE_PEOPLE + """

ERA FIELDS ON DEMAND: when a beat enters a field's terrain, its material comes from the canon, not from invention — people present → clothing · an interior → interiors (including any unique features listed there) · transport, tools or lighting → vehicles_machinery / technology. When the beat does not touch that terrain, do not force the field in.

Fill ALL slots for EVERY item. Each value is a SHORT English phrase (not a paragraph). Do NOT write aspect ratio, negations, or a style/grain tail — the profile/assembler adds those afterward.

TEXT DISCIPLINE: any text meant to appear in the image goes ONLY through the text_in_image slot, in Spanish. The prose slots (subject/action/setting/...) describe the scene — never embed letters or words to be rendered inside them.

JSON only. No markdown. No preamble."""
)


# F8 §1 C–E (guion v3): la doctrina R6 sin los clichés de cara (jaw clenched, pupils dilated…) + reglas de composición
# y de contenido sensible. El SI de arriba (v2 y m09) no cambia.
SYSTEM_INSTRUCTION_VISUAL_SEEDREAM_V3 = (
    SYSTEM_INSTRUCTION_VISUAL_SEEDREAM.replace(DOCTRINE_R6_PHYSICAL_TRANSLATION, v3img.DOCTRINE_R6_V3)
    # F8b §2.3 y §2.5: el texto va en el idioma del lugar (no en español) y el cuerpo no lleva clichés de cara
    .replace("text = the literal content IN SPANISH (the audience reads Spanish — a headline reads 'PRÓFUGO', not "
             "'ESCAPED')", "text = the literal content in the LANGUAGE OF THE PLACE of the event (given in the user "
             "prompt), at most 3 words")
    .replace("goes ONLY through the text_in_image slot, in Spanish.", "goes ONLY through the text_in_image slot.")
    .replace("hollow exhausted eyes, cracked lips, accumulated filth", "slumped exhausted posture, accumulated filth")
    .replace("JSON only. No markdown. No preamble.", v3img.COMPOSITION_RULES_V3 + "\n\nJSON only. No markdown. No preamble.")
)


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


# ── F50 B: el pedido de los casilleros (textos del lab, tal cual: F46b texto 2, F48 TEXTO_S4_YEAR) ──
TEXTO_2_PEOPLE_GROUP = ("- people_group: a LIST of ids from PEOPLE GROUPS whose members are visible in THIS image "
                        "(usually one); [] if no person is visible. Routing only — not rendered as text.")
TEXTO_S4_YEAR = ("- year: the year (YYYY) in which THIS image's scene takes place, read from the narration fragment, its "
                 "paragraph and the case file (a year said earlier in the paragraph, «ten years before» a stated year, "
                 "«now» = the most recent year in the case file). Routing only — not rendered as text.")


def _si_casilleros() -> str:
    """El SI v3 con `people_group` y `year` después de la línea `- foto_madre_ref:`."""
    si = SYSTEM_INSTRUCTION_VISUAL_SEEDREAM_V3
    fin = si.index("\n", si.index("- foto_madre_ref:"))
    return si[:fin] + "\n" + TEXTO_2_PEOPLE_GROUP + "\n" + TEXTO_S4_YEAR + si[fin:]


SYSTEM_INSTRUCTION_CASILLEROS = _si_casilleros()


def _casilleros_schema(n: int) -> dict:
    """El esquema de los slots + `year` + `people_group` (en ese orden en `required`, como se midió). `mood`, `style`
    y `hard_fact_ids` se siguen pidiendo aunque el armado no los use (así se midió)."""
    s = _seedream_slots_schema(n)
    s["items"]["properties"]["year"] = {"type": "STRING"}
    s["items"]["required"].append("year")
    s["items"]["properties"]["people_group"] = {"type": "ARRAY", "items": {"type": "STRING"}}
    s["items"]["required"].append("people_group")
    return s


class CasillerosParada(RuntimeError):
    """Opus no llenó los casilleros o el movimiento (negativa o error de la API): el cap queda en PARADA, sin volver a
    Pro en silencio."""


def _llamar_casilleros(prompt, system_instruction=None, response_schema=None, description=None, **_):
    """La llamada a Opus con la firma de call_flash_json; un arreglo en la raíz vuelve como {"image_prompts": …}
    (igual que gemini_helpers con los esquemas de arreglo)."""
    import claude_helpers
    from script_engine import guion_v4
    raw = claude_helpers.call_json(prompt, model=MODELO_CASILLEROS, system_instruction=system_instruction,
                                   response_schema=response_schema, effort=guion_v4.ESFUERZO[MODELO_CASILLEROS],
                                   description=description)
    return {"image_prompts": raw} if isinstance(raw, list) else raw


def _geo_era(topic_id: str, narration: dict) -> dict:
    """F48 S1: GEO = `lugar_principal` del perfil del research (`_steps/<id>/_perfil.json`); ERA = «primer año–último
    año» dichos en la narración del video. Nadie escribía `canonical_geo` / `canonical_era`: el pedido decía
    «(sin geo)» / «(sin era)». Lo que no se puede leer no se pone (queda el respaldo de `_build_topic_block`)."""
    from script_engine import voz_utils
    out: dict = {}
    perfil = STEPS_DIR / topic_id / "_perfil.json"
    if perfil.exists():
        lugar = (json.loads(perfil.read_text(encoding="utf-8")) or {}).get("lugar_principal")
        if lugar:
            out["canonical_geo"] = lugar
    texto = " ".join(ch.get("narration") or "" for ch in (narration or {}).get("chapters") or [])
    anios = sorted(int(y) for y in voz_utils.numeros(texto)
                   if re.fullmatch(r"\d{4}", y) and 1800 <= int(y) <= 2100)   # derivado: handoff F48 §Constantes (años 1800–2100)
    if anios:
        out["canonical_era"] = f"{anios[0]}–{anios[-1]}"
    return out


def _punta(tok: str, hoy: int):
    """F50d B: un extremo del tramo → (desde, hasta): «1958» → (1958, 1958); «1950s» → (1950, 1959);
    «present» → (hoy, hoy); otra cosa → None."""
    tok = tok.strip().lower()
    if re.fullmatch(r"\d{4}", tok):
        return int(tok), int(tok)
    if re.fullmatch(r"\d{3}0'?s", tok):
        return int(tok[:4]), int(tok[:4]) + 9
    if tok in ("present", "now", "today"):
        return hoy, hoy
    return None


def _tramo(years, hoy: int | None = None) -> tuple[int, int] | None:
    """F50d B: `years` del canon → (inicio, fin). Formatos de Flash: «1958-1966», «1950s-1970s» (1950–1979),
    «1937-1950s» (1937–1959), «2000s-present», un año o una década suelta. Ilegible → None (no cruza)."""
    import datetime
    hoy = hoy or datetime.date.today().year
    partes = re.split(r"\s*(?:-|–|—|\bto\b)\s*", str(years or "").strip())
    if not 1 <= len(partes) <= 2:
        return None
    puntas = [_punta(t, hoy) for t in partes]
    if None in puntas or puntas[0][0] > puntas[-1][1]:
        return None
    return puntas[0][0], puntas[-1][1]


def _periods_del_cap(periods: list, anios, hoy: int | None = None) -> list:
    """F50d B: los `period` del canon para los años de las fotos del cap, foto por foto: el/los que cruzan
    ese año; si ninguno lo cruza, el/los más cercanos (menor distancia en años; empate → todos). Se juntan
    en el orden del canon. Sin años en el cap → todos. `years` ilegible → no cruza ni es el más cercano;
    si ninguno es legible → [] (y el bloque vuelve a los campos únicos)."""
    ys = sorted({int(m) for a in anios or [] for m in re.findall(r"\d{4}", str(a or ""))})
    if not ys:
        return list(periods)
    tramos = {i: t for i, pe in enumerate(periods) if (t := _tramo(pe.get("years"), hoy))}
    elegidos = set()
    for y in ys:
        d = {i: max(t[0] - y, y - t[1], 0) for i, t in tramos.items()}
        elegidos |= {i for i in d if d[i] == min(d.values())}
    return [periods[i] for i in sorted(elegidos)]


def _lineas_epoca(era: dict, anios=None) -> list:
    """F50d B: las 4 líneas clothing/technology/vehicles_machinery/interiors; con `periods`, una tanda
    por period del cap (cabecera `  period AAAA-AAAA:`); sin `periods` (topic viejo), los campos únicos."""
    def cuatro(d):
        return [f"  clothing              : {d.get('clothing', '')}",
                f"  technology            : {d.get('technology', '')}",
                f"  vehicles_machinery    : {d.get('vehicles_machinery', '')}",
                f"  interiors             : {d.get('interiors', '')}"]
    periods = [pe for pe in era.get("periods") or [] if isinstance(pe, dict)]
    elegidos = _periods_del_cap(periods, anios) if periods else []
    if not elegidos:                       # topic viejo, o ningún period legible
        return cuatro(era)
    out = []
    for pe in elegidos:
        out += [f"  period {pe.get('years', '')}:", *cuatro(pe)]
    return out


def _log_sin_period(topic: dict, anios, cap_number) -> str:
    """F50f: cuántas fotos del cap no cruzan ningún period del canon y qué tramo les dio la regla del más cercano."""
    periods = [pe for pe in (topic.get("era_visual_canon") or {}).get("periods") or [] if isinstance(pe, dict)]
    if not periods:
        return f"cap {cap_number}: canon sin periods (época única)"
    sin = {}
    for a in anios or []:
        y = next(iter(re.findall(r"\d{4}", str(a or ""))), None)
        if y and not any((t := _tramo(pe.get("years"))) and t[0] <= int(y) <= t[1] for pe in periods):
            sin[y] = [pe.get("years") for pe in _periods_del_cap(periods, [y])]
    n = sum(1 for a in anios or [] if next(iter(re.findall(r"\d{4}", str(a or ""))), None) in sin)
    return (f"cap {cap_number}: {n} de {len(anios or [])} fotos sin period"
            + ("" if not sin else " → " + "; ".join(f"{y}: {' · '.join(t)}" for y, t in sorted(sin.items()))))


def _format_seedream_canon_block(topic: dict, anios=None) -> str:
    """Canon de 2 CAPAS para el user-prompt del skeleton (eslabón 3b cablea el 2).

    Espejo de _format_visual_canon_block PERO extendido con la capa SOURCED del
    sujeto puntual (eslabón 2): materials_textures, color_palette, scale_dimensions,
    distinctive_features, demographics, condition_evolution (HANDOFF_133 R4:
    visual_reference_availability ya NO se surfacea — meta-info de research inútil
    para pintar). NO modifica el bloque viejo; es una función aparte del path seedream.
    F50d B: `anios` = años de las fotos del cap (expediente); con `era.periods` imprime los tramos del cap.
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
            *_lineas_epoca(era, anios),            # F50d B: por tramo si el canon trae periods
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
            # visual_reference_availability ECHADO (HANDOFF_133 R4): meta-info de research
            # (qué fotos existen en archivos), inútil para pintar → menos ruido × 81 prompts.
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


# ═══════════════════════════════════════════════════════════════
#  DIRECCIÓN VISUAL POR INTENT (arco de retención · chat 108)
#  Espejo de TONE_INSTRUCTIONS_BY_INTENT de m01b, pero para la imagen.
#  STEERING al LLM de la Etapa 1 — NO re-reparte emotional_rank (eso es versión B).
# ═══════════════════════════════════════════════════════════════
VISUAL_INTENT_BY_INTENT: dict[str, str] = {
    "hook":           "Close or medium framing on a single charged object or human detail that carries the dread by implication — a legible carved number, a marked grave, a personal object left behind, hands or a face caught in the decisive instant. Cold, desaturated blue-grey palette matching the channel's documentary look — overcast or hard COLD directional light isolating the detail; explicitly NO warm, golden, amber or memorial glow. Morbid pull through the loaded evidence, NOT through gore: no corpses, no still bodies, no full killing apparatus — the narration carries the death, the image shows the charged trace it left.",
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


def _build_seedream_prompt_step2(topic, cap_data, narration_text, anchors, extra_block: str = "",
                                 anios=None) -> str:
    """User-prompt del skeleton seedream: canon 2-capas + facts + anchors → pedir
    N slot-sets (uno por fragmento). El LLM elige hard_fact_ids; NO escribe cifras."""
    cap_n = cap_data["chapter_number"]
    role = cap_data.get("role") or "development"
    cap_title = cap_data.get("title") or "(sin título)"
    n = len(anchors)
    anchor_list = "\n".join(f"  [{i + 1}] «{a}»" for i, a in enumerate(anchors))
    topic_block = _build_topic_block(topic)
    canon_block = _format_seedream_canon_block(topic, anios)   # F50d B: años de las fotos del cap
    arc_block = _visual_arc_block(cap_data.get("narrative_intent"))
    # HANDOFF_142b PALANCA B.1: en el HOOK, el item [1] es el beat del CLIP de apertura (lo PRIMERO
    # que ve el espectador). Regla dura: close/medium sobre el detalle, NUNCA establishing/aéreo/wide.
    # El hook es siempre el cap veo (cap1); ningún cap flux tiene narrative_intent=="hook".
    opening_clip_rule = ""
    if cap_data.get("narrative_intent") == "hook":
        opening_clip_rule = (
            "\nOPENING MOTION CLIP — SOLO el item [1]: es lo PRIMERO que ve el espectador. DEBE ser "
            "un plano close o medium sobre el ÚNICO detalle cargado de su anchor. Un plano "
            "establishing / aéreo / wide del sitio entero está PROHIBIDO para el item [1], aunque su "
            "narración introduzca el lugar — elegí el detalle DENTRO de esa narración, no el panorama. "
            "Para el item [1]: shot_scale ∈ {detail, close, medium}, NUNCA wide/extreme_wide.\n"
        )
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
{arc_block}{opening_clip_rule}{extra_block}
DISTRIBUTION OF emotional_rank:
- 1-2 items R1 (peak of cap: closing, revelation, biggest impact).
- 2-3 items R2 (action, strong transition, person in tension).
- Rest R3 (descriptive scene, context, ambience).

For hard_fact_ids: pick the F-labels (e.g. "F03") of verified_facts whose FIGURES
this image weaves, copied EXACTLY as labeled — and ONLY those relevant to THIS
anchor's moment (do NOT bring foundation-era figures into a peak-era beat). Do NOT
rewrite the figures.

JSON only. No markdown. No preamble."""


# RUTA B (HANDOFF_134d): subject_ref que cuentan como EXTERIOR del lugar → anclan la madre-
# establecimiento. El resto (interior_scene, landscape_view) y los detalles van t2i.
_PLACE_EXTERIOR_SUBJECT_REFS = frozenset({"establishing_shot", "main_subject"})


def _apply_place_exterior_filter(image_prompts, is_place: bool) -> None:
    """kind=place: la madre es la vista del ESTABLECIMIENTO (exterior/aéreo). Deja __subject__
    SOLO en los beats exteriores; interiores/landscape/detalle → sin ancla (t2i), porque una
    celda genérica no driftea de identidad y anclarla a la aérea saldría mal. Filtro
    DETERMINÍSTICO: red de seguridad del rule del prompt (que el LLM puede filtrar mal, 133).
    Muta in-place. No-op si no es place o si el beat no tenía __subject__."""
    if not is_place:
        return
    for it in image_prompts:
        refs = it.get("foto_madre_ref") or []
        if "__subject__" not in refs:
            continue
        sref = (it.get("subject_ref") or "").strip()
        exterior = sref in _PLACE_EXTERIOR_SUBJECT_REFS and it.get("shot_scale") != "detail"
        if not exterior:
            it["foto_madre_ref"] = [r for r in refs if r != "__subject__"]


def _render_prompts_seedream(topic, cap_data, narration, plan, cap_number):
    """F50 B — paso 2 de las fotos: Opus llena los casilleros de cada ancla con su expediente (año, lugar, párrafo,
    escenas, hechos, citas, personas y los grupos del canon); el código arma la prosa (`v3img.armar`) y F8 la revisa
    (`v3img.f8_backstop`: si queda un problema se saca la frase, sin re-tejido); la pasada 1 del filtro de texto
    legible queda de backstop que saca la frase. Devuelve el mismo shape de fase2a (image_prompts con su prompt)."""
    import claude_helpers
    anchors = [a["anchor"] for a in plan["anchors"]]
    n = len(anchors)
    f8 = topic.get("_f8")
    if not f8:
        raise VisualValidationError(f"cap {cap_number}: sin escaleta (guion v3) no hay expediente ni casilleros (F50)")
    documented = topic.get("documented_people")
    cap_beats = (f8.get("beats") or {}).get(cap_number) or []
    assign = ((f8.get("force_assign") or v3img.assign_beats(narration, anchors, cap_beats)) if cap_beats
              else [{"beat": None, "cerrada": False} for _ in anchors])
    exps = mexp.expedientes(topic, f8.get("fuentes") or {}, cap_beats, anchors, assign,
                            (f8.get("anio_prev") or {}).get(cap_number), f8.get("year") or "")
    extra = v3img.beats_block(cap_beats, assign, cap_data.get("bullets"), f8.get("lang")) if cap_beats else ""
    if f8.get("note"):
        extra += f"\nFOR THIS IMAGE: {f8['note']}\n"
    extra += mexp.bloque(exps, topic.get("people_groups") or [])
    # F50d B: año de cada foto = el del expediente (ancla, si no el respaldo) → elige los tramos del canon
    anios = [e.get("anio_ancla") or (e.get("respaldo") or ("",))[0] for e in exps]
    if not f8.get("refill"):
        print(f"  [03] {_log_sin_period(topic, anios, cap_number)}")     # F50f: medida, no freno
    prompt = _build_seedream_prompt_step2(topic, cap_data, narration, anchors, extra, anios)

    def _validator(parsed):
        items = parsed.get("image_prompts") if isinstance(parsed, dict) else None
        if not isinstance(items, list) or len(items) != n:
            got = len(items) if isinstance(items, list) else "no-lista"
            raise VisualValidationError(
                f"cap {cap_number} (casilleros): se esperaban EXACTAMENTE {n} slot-objects, llegaron {got}.")
        for i, it in enumerate(items, start=1):
            if not isinstance(it, dict):
                raise VisualValidationError(f"cap {cap_number} (casilleros) item {i}: no es objeto")
            ss = it.get("shot_scale")
            if ss not in VALID_SHOT_SCALES:
                raise VisualValidationError(f"cap {cap_number} (casilleros) item {i}: shot_scale inválido ({ss!r})")
            if not (it.get("subject") or "").strip():
                raise VisualValidationError(f"cap {cap_number} (casilleros) item {i}: slot 'subject' vacío")
        # candado #2: narration_anchor VERBATIM del Paso 1 (nunca del eco del LLM).
        return {"image_prompts": [{**items[i], "narration_anchor": anchors[i]} for i in range(n)]}

    try:
        slots_out = _call_with_validation_retry(
            prompt, _validator, cap_number, system_instruction=SYSTEM_INSTRUCTION_CASILLEROS,
            response_schema=_casilleros_schema(n), caller=_llamar_casilleros, description="m03:casilleros")
    except claude_helpers.ClaudeError as e:
        raise CasillerosParada(f"cap {cap_number}: {MODELO_CASILLEROS} no llenó los casilleros: {e}") from e
    for k, it in enumerate(slots_out["image_prompts"]):
        it["beat"], it["cerrada"] = assign[k]["beat"], assign[k]["cerrada"]
        gone = v3img.scrub_slots(it)                   # D2–D3, E: clichés y prohibidas fuera ANTES de armar
        why = v3img.fix_text_slot(it, f8.get("lang") or "en")   # F8b §2.3: idioma del lugar, ≤ 3 palabras
        if why:
            gone.append(f"text_in_image: {why}")
        if gone:
            it["_f8_slots_scrub"] = gone

    # RUTA B (HANDOFF_134d): kind=place ancla la madre-establecimiento SOLO en exteriores.
    _apply_place_exterior_filter(
        slots_out["image_prompts"],
        (topic.get("central_subject") or {}).get("kind") == "place")

    # ── armado por código + F8 (backstop: se saca la frase) ──
    grupos = {g["id"]: g for g in topic.get("people_groups") or [] if isinstance(g, dict) and g.get("id")}
    by_n = {b["n"]: b for b in cap_beats}
    for it, e in zip(slots_out["image_prompts"], exps):
        anio, fuente = v3img.anio_final(e, it)
        armado = v3img.armar(it, anio, grupos)
        prose, notas = v3img.f8_backstop(armado["prompt"], it, bool((by_n.get(it.get("beat")) or {}).get("escala")))
        tii = it.get("text_in_image") or {}
        prose, fuera = _sacar_frases_con_texto(prose, (tii.get("text") or "") if tii.get("present") else "")
        # raw_llm_prompt = los casilleros crudos (auditoría)
        it["raw_llm_prompt"] = json.dumps(
            {k: it.get(k) for k in (*SEEDREAM_SLOT_KEYS, "text_in_image", "hard_fact_ids", "people_group", "year")},
            ensure_ascii=False)
        it["prompt"], it["art_profile"] = prose, ""
        it["anio"], it["anio_fuente"] = anio, fuente
        if notas:
            it["_f8_problemas"] = notas
        if fuera:
            it["_f8_texto_fuera"] = fuera
        it["sensible"] = v3img.is_body(prose)
        it["motivos"] = sorted(v3img.motifs_of(prose))
    slots_out["chapter_number"] = cap_number
    if not f8.get("refill"):
        _f8_fix_cap(topic, cap_data, narration, slots_out["image_prompts"], cap_number)
    return slots_out


def _sacar_frases_con_texto(prose: str, intentional_text: str) -> tuple[str, list[str]]:
    """Backstop de texto legible: la frase que dispara la pasada 1 de `_validate_no_text_leakage` (eufemismos de
    texto: «where the name was», «the word 'X'»…) se saca. La frase del cartel (`intentional_text`) queda exenta,
    como antes."""
    quedan, fuera = [], []
    for s in re.split(r"(?<=[.!?])\s+", prose):
        try:
            _validate_no_text_leakage(s, "f8", allow_intentional_text=True, intentional_text=intentional_text)
            quedan.append(s)
        except VisualValidationError:
            fuera.append(s)
    return " ".join(quedan).strip(), fuera


def _f8_refill(topic: dict, cap_data: dict, narration: str, item: dict, cap_number: int, note: str) -> dict:
    """Rehace UNA imagen (casilleros con Opus + armado) con su mismo ancla y beat y una indicación (`note`). Sin
    arreglos de cap. Si Opus se niega: CasillerosParada con la foto (sin volver a Pro)."""
    f8 = dict(topic["_f8"], refill=True, note=note,
              force_assign=[{"beat": item.get("beat"), "cerrada": item.get("cerrada", False)}])
    try:
        out = _render_prompts_seedream({**topic, "_f8": f8}, cap_data, narration,
                                       {"anchors": [{"anchor": item["narration_anchor"]}]}, cap_number)
    except CasillerosParada as e:
        raise CasillerosParada(f"{e} · re-hechura de la foto «{item['narration_anchor'][:60]}»") from e
    new = out["image_prompts"][0]
    new["_f8_rehecha"] = note
    return new


F8_FIX_PASSES = 2
F8_NOTE_BODY_HOOK ="NO dead bodies in this image (it is the hook): show what was left — objects, water, empty space."
F8_NOTE_CERRADA = ("TIGHTEST framing of the cap (shot_scale close or detail) on the beat's sensory image, at HUMAN "
                   "scale: a person in posture or a human trace (belongings, clothes, a bunk); never an object or a "
                   "weapon in detail, never a face macro, never hands. The camera is with the victims or the witness.")
F8_NOTE_ARMA = ("WEAPON BEAT told from the victims or the witness: people crouching in the water, a witness watching "
                "from a terrace or a window, still silhouettes on a far rooftop. NO shooter or weapon as subject, no "
                "muzzle flash, no aiming; a weapon only at rest, far away, from behind.")
F8_NOTE_ESTABLISHING = ("ESTABLISHING EXTERIOR: the place of this fragment seen from outside or from above, wide or "
                        "extreme wide; people small or absent.")


def _f8_fix_cap(topic: dict, cap_data: dict, narration: str, items: list[dict], cap_number: int) -> None:
    """Arreglos que se ven en el cap: sin cuerpos en el cap 1 (E) y ≥ 1 establecimiento/exterior (D5)."""
    for k, it in enumerate(items):
        if cap_number == 1 and it.get("sensible"):
            items[k] = _f8_refill(topic, cap_data, narration, it, cap_number, F8_NOTE_BODY_HOOK)
        elif v3img.weapon_subject(it):                                                   # F8b §2.1
            items[k] = _f8_refill(topic, cap_data, narration, it, cap_number, F8_NOTE_ARMA)
        elif it.get("cerrada") and (it.get("shot_scale") not in ("close", "detail") or not v3img.human_scale(it)):
            items[k] = _f8_refill(topic, cap_data, narration, it, cap_number, F8_NOTE_CERRADA)   # §1 B + F8b §2.2
    # con menos de MIN_FLUX_EXTRAS imágenes (humo, pruebas) no hay proporción que cuidar: no se rehace la del beat
    if len(items) >= MIN_FLUX_EXTRAS and not any(v3img.establishing(it) for it in items):
        cand = [k for k, it in enumerate(items) if not it.get("cerrada") and k > 0] or [len(items) - 1]
        k = next((x for x in reversed(cand) if items[x].get("emotional_rank") == "R3"), cand[-1])
        items[k] = _f8_refill(topic, cap_data, narration, items[k], cap_number, F8_NOTE_ESTABLISHING)


def _f8_fix_video(topic: dict, skel_by_n: dict, narr_by_n: dict, items_by_cap: dict[int, list[dict]]) -> dict:
    """Arreglos del video entero (D1 motivos, E cuerpos, D5 humanos en plano medio): hasta F8_FIX_PASSES pasadas de
    re-hechura por imagen en exceso (cada nota junta todos sus motivos y avisa los motivos ya saturados) y una
    auditoría final. En los caps Veo no se rehace la imagen 0 (el primer cuadro del clip: su movimiento ya está escrito);
    el que llama vuelve a coser los supplementals."""
    beats = topic["_f8"]["beats"]

    def _caps() -> list[list[dict]]:
        return [items_by_cap.get(n) or [] for n in range(1, EXPECTED_CHAPTER_COUNT + 1)]
    before = cur = v3img.video_audit(_caps(), beats)
    rehechas = []
    for _pass in range(F8_FIX_PASSES):
        notes: dict[tuple[int, int], list[str]] = {}
        for cap, i, m in cur["exceso_motivos"]:
            notes.setdefault((cap, i), []).append(f"do NOT show the motif «{m}» (already used twice in this video)")
        for cap, i in cur["exceso_cuerpos"]:
            notes.setdefault((cap, i), []).append("NO dead bodies: show what they left — objects, water, empty space")
        for cap, i in cur["exceso_humano_medio"]:
            notes.setdefault((cap, i), []).append("NO person in medium shot: a wide shot of the place, people small, "
                                                  "far or absent")
        notes = {k: v for k, v in notes.items() if not (k[0] in VEO_CHAPTERS and k[1] == 0)}
        if not notes:
            break
        full = sorted(m for m, v in cur["motivos"].items() if len(v) >= v3img.MOTIF_MAX)
        for (cap, i), why in sorted(notes.items()):
            note = "; ".join(why) + (f". Motifs already used twice in this video (avoid them all): {', '.join(full)}"
                                     if full else "") + ". Show another part of the beat's sensory image."
            items_by_cap[cap][i] = _f8_refill(topic, skel_by_n[cap], (narr_by_n[cap].get("narration") or "").strip(),
                                              items_by_cap[cap][i], cap, note)
            rehechas.append({"cap": cap, "img": i + 1, "pasada": _pass + 1, "motivo": note})
        cur = v3img.video_audit(_caps(), beats)
    after = cur

    def _brief(a: dict) -> dict:
        return {"total": a["total"], "motivos": {k: len(v) for k, v in a["motivos"].items()},
                "exceso_motivos": a["exceso_motivos"], "cuerpos": a["cuerpos"], "exceso_cuerpos": a["exceso_cuerpos"],
                "humano_medio": len(a["humano_medio"]), "caps_sin_establecimiento": a["caps_sin_establecimiento"]}
    return {"antes": _brief(before), "rehechas": rehechas, "despues": _brief(after)}


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
    capped: bool = True,
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
    if not capped:                                      # F8 §1 F: lo que pide la duración (sin el tope por video)
        return max(MIN_IMAGES_FLUX, min(MAX_IMAGES_FLUX, n))
    # HANDOFF_F7 §8.2: tope por video (config.long_video.max_images_per_video, 90): lo que dejan los caps veo (a su
    # duración nominal) repartido entre los caps de desarrollo. Con 105 s por cap: 16 fotos por cap como máximo.
    from script_engine.video_length import get
    veo_extras = 2 * _calculate_flux_extras_count(get("hook_cap_seconds"))
    cap_max = max(MIN_IMAGES_FLUX, (get("max_images_per_video") - veo_extras) // max(1, total_chapters - 2))
    return max(MIN_IMAGES_FLUX, min(MAX_IMAGES_FLUX, cap_max, n))


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
    (veo_lo, veo_hi, supps_lo, supps_hi).

    F51c: el corte va al final de oración más cercano a `veo_zone_chars` (el regex de
    _sentence_content_spans); sin final de oración en la narración, al espacio más cercano;
    empate → el que deja la zona Veo más corta (el clip dura 8 s fijos)."""
    narration_len = len(narration_text)
    cut = veo_zone_chars if veo_position == "start" else narration_len - veo_zone_chars
    cands = ([m.end() for m in re.finditer(r"[.!?…]+", narration_text) if 0 < m.end() < narration_len]
             or [m.start() for m in re.finditer(r"\s", narration_text) if 0 < m.start() < narration_len])
    if cands:
        largo_veo = (lambda c: c) if veo_position == "start" else (lambda c: narration_len - c)
        cut = min(cands, key=lambda c: (abs(c - cut), largo_veo(c)))
    if veo_position == "start":
        return 0, cut, cut, narration_len
    # "end"
    return cut, narration_len, 0, cut


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
    # HANDOFF_142b PALANCA A: SOLO el hook (veo_position=="start") — forzar que el veo_anchor
    # caiga en el DETALLE cargado, no en la presentación del sitio. El outro (pos=="end") NO.
    hook_rule = ""
    if veo_position == "start":
        hook_rule = (
            "\n5. REGLA HOOK (solo clip de apertura): el `veo_anchor` DEBE caer en el fragmento de "
            "[ZONA VEO] que nombra el DETALLE más concreto y cargado (un número, una tumba/lápida, "
            "una persona, un gesto en el instante decisivo) — NUNCA el fragmento que solo presenta "
            "o nombra el LUGAR/sitio. El opener ilustra el detalle visceral, no la presentación del "
            "sitio. Si la zona tiene varios, elegí el más impactante."
        )
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
4. Cada anchor abarca un beat con sentido (no una palabra suelta). Apuntá ~40-200 chars.{hook_rule}

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
    se mantiene (F51c: los nombres de PERSONA ya no se borran después). Default False →
    Kling/Flux intactos.

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
    caller=None,
    description: str | None = None,
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
        caller: con la firma de call_flash_json (F50: los casilleros pasan `_llamar_casilleros`, Opus); None = Flash.
    """
    checklist_block = checklist if checklist is not None else _DEFAULT_RETRY_CHECKLIST
    attempt_prompt = prompt
    last_error: VisualValidationError | None = None
    _caller = caller or call_flash_json

    for attempt in range(1, max_attempts + 1):
        raw = _caller(attempt_prompt, system_instruction=system_instruction,
                      response_schema=response_schema, description=description)
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
# Un cap veo es HÍBRIDO: 1 foto Veo (image_prompt, animada con i2v) + N stills DepthFlow (supplementals). TODAS las
# fotos van por los casilleros (F50 B), igual que caps 2-6. Lo único que NO es foto es el video_prompt (movimiento de
# la foto Veo): F50 C lo escribe Opus con el orden de la guía de Google (plano y tono → cámara → qué se mueve → luz y
# lugar → gente quieta); lo que no tiene que pasar va en el negative_prompt que agrega asset_manager.

_VEO_MOTION_SYSTEM = """You write the motion prompt for an image-to-video model (Google Veo) that animates ONE documentary still. The still is the first frame and it is final: everything visible in it stays as it is. Follow Google's order: shot type and tone first, then the camera, then what moves, then light and place.

Write 3 to 5 sentences of plain English, between 120 and 700 characters, in this order:
1. Shot and tone: the kind of shot and its tone, in the still's own photographic style (for example: "A slow, somber documentary shot on grainy 35mm film, muted colors.").
2. Camera: ONE camera movement in film terms (slow push-in, slow pull-out, slow pan, slow tilt, locked-off shot with a subtle drift, slow orbit), its speed, and the framing where it starts and where it ends.
3. Motion: what moves, using only things already in the still (dust, smoke, water, cloth, grass, hair, a person breathing or slowly turning the head). If more than one thing moves, describe it step by step ("first ..., then ...").
4. Light and place: the still's light and place, the same for the whole clip.
5. People, only if the still shows people: they stay in their places, faces and bodies steady.

Write only what should be seen. Anything that must not happen goes in a separate negative prompt that the code adds, so do not write negations. No names, numbers or on-screen text.
Return only the JSON field video_prompt."""

_SEEDREAM_MOTION_SCHEMA = {"type": "OBJECT",
                          "properties": {"video_prompt": {"type": "STRING"}},
                          "required": ["video_prompt"]}


def voz_del_clip(narracion: str, veo_position: str, ventana_chars: int) -> str:
    """F57 A1: las palabras de la narración que la voz dice durante el clip (sin LLM). `start` → las palabras (\\S+)
    que EMPIEZAN antes del carácter `ventana_chars`; `end` → las que TERMINAN después de `len − ventana_chars`. Corte
    por palabra, texto original tal cual (sin agregar ni quitar nada); ventana ≥ narración → la narración entera."""
    palabras = list(re.finditer(r"\S+", narracion))
    if not palabras:
        return ""
    if veo_position == "end":
        dentro = [m for m in palabras if m.end() > len(narracion) - ventana_chars]
    else:
        dentro = [m for m in palabras if m.start() < ventana_chars]
    if not dentro:
        return ""
    return narracion[dentro[0].start():dentro[-1].end()]


def _seedream_video_prompt(image_prompt: str, voz_clip: str, label: str, max_attempts: int = 3) -> str:
    """El video_prompt (movimiento) de la foto Veo: Opus (MODELO_CASILLEROS) con el sistema de F50 C, sembrado por la
    prosa del primer cuadro y la voz entera del clip (F57: `voz_clip`, antes el ancla). Reintenta si el largo cae
    fuera de 120–700."""
    import claude_helpers
    user = (f"FIRST FRAME (final):\n{image_prompt}\n\nNARRATOR OVER THIS CLIP (Spanish, context only): «{voz_clip}»\n\n"
            f"CLIP LENGTH: {VEO_CLIP_DURATION_SEC:g} seconds.")
    last = ""
    for attempt in range(1, max_attempts + 1):
        try:
            out = _llamar_casilleros(user, system_instruction=_VEO_MOTION_SYSTEM,
                                     response_schema=_SEEDREAM_MOTION_SCHEMA, description="m03:motion")
        except claude_helpers.ClaudeError as e:
            raise CasillerosParada(f"{label}: {MODELO_CASILLEROS} no escribió el movimiento: {e}") from e
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


# F50 D: lo que el papel de fotos necesita de cada foto de un cap Veo (los caps flux guardan el ítem entero)
CLAVES_F8_PAPEL = ("anio", "anio_fuente", "people_group", "shot_scale", "camera_angle", "lens_technique",
                   "_f8_problemas", "_f8_slots_scrub", "_f8_texto_fuera", "_f8_rehecha")


def _render_prompts_seedream_veo(topic, cap_data, narration, plan, veo_position, cap_number, veo_zone_chars):
    """Paso 2 VEO bajo seedream. Reusa el skeleton de caps flux para TODAS las fotos
    vía un plan sintético [veo_anchor]+supplementals → resultado[0]=foto Veo
    (image_prompt), resultado[1..N]=stills DepthFlow (supplementals). El video_prompt
    (motion de la foto Veo) sale de una call dedicada, sembrada por `voz_clip` (F57: las
    palabras de la voz en los 8 s del clip, `voz_del_clip` con la ventana en caracteres que
    ya calcula `_process_one_cap`); la foto inicial sigue saliendo del `veo_anchor`.
    Devuelve el MISMO shape de fase2a + `voz_clip`."""
    veo_anchor = plan["veo_anchor"]["anchor"]
    voz_clip = voz_del_clip(narration, veo_position, veo_zone_chars)
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

    # video_prompt (motion) de la foto Veo — call dedicada, sembrada por el first-frame y la voz del clip (F57).
    video_prompt = _seedream_video_prompt(
        image_item["prompt"], voz_clip, f"cap {cap_number} (veo-seedream) video_prompt")

    return {
        "chapter_number": cap_number,
        "image_prompt": image_item["prompt"],
        "video_prompt": video_prompt,
        # HANDOFF_142b PALANCA B.2: en el HOOK (veo_position=="start") NO defaultear a
        # establishing_shot (fuerza aéreo + ancla la madre aérea vía _apply_place_exterior_filter).
        # Default no-exterior "detail" → el opener queda close/sin-ancla. El outro (pos=="end")
        # conserva su default establishing (correcto para el cierre).
        "subject_ref": (image_item.get("subject_ref")
                        or ("detail" if veo_position == "start" else "establishing_shot")),
        "art_profile": "",
        "narration_anchor": veo_anchor,
        "voz_clip": voz_clip,
        "veo_position": veo_position,
        "supplemental_image_prompts": [
            {"prompt": it["prompt"],
             "narration_anchor": it["narration_anchor"],
             "art_profile": "",
             "raw_llm_prompt": it.get("raw_llm_prompt"),
             **({k: it[k] for k in ("beat", "sensible", "motivos", *CLAVES_F8_PAPEL) if k in it}
                if topic.get("_f8") else {})}
            for it in supp_items
        ],
        **({"image_sensible": image_item.get("sensible", False), "_f8_items": items,
            "image_f8": {k: image_item[k] for k in ("beat", "motivos", "raw_llm_prompt", *CLAVES_F8_PAPEL)
                         if k in image_item}} if topic.get("_f8") else {}),
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
    topic = {**topic, **_geo_era(topic_id, narration)}      # F48 S1: GEO y ERA del pedido

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

    # F8 §1 B–F: con escaleta (guion v3) las imágenes siguen los beats; sin escaleta (v2), todo como antes
    f8_beats = v3img.load_beats(topic, STEPS_DIR)
    if f8_beats:
        topic = {**topic, "_f8": {"beats": f8_beats, "year": v3img.topic_year(topic, f8_beats),
                                  "lang": v3img.place_language(topic),
                                  "fuentes": mexp.fuentes(topic_id, STEPS_DIR),          # F50 B: el expediente
                                  "anio_prev": {n: mexp.anio_previo(narr_chapters, n)
                                                for n in range(1, EXPECTED_CHAPTER_COUNT + 1)}}}

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
                f"veo_zone≈{veo_zone_chars} chars), casilleros {MODELO_CASILLEROS} + armado..."
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
            cap_out = _render_prompts_seedream_veo(topic, sch, narration_text, plan, veo_position, cap_n,
                                                   veo_zone_chars)
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
                f"target, role={sch.get('role','?')}), casilleros {MODELO_CASILLEROS} + armado..."
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
            # Seedream: casilleros + armado por código (F50; prosa ya FINAL, con F8 aplicada) → NO tail-bake.
            cap_out = _render_prompts_seedream(topic, sch, narration_text, plan, cap_n)
            if f8_beats:                                  # F8 §1 F: planos que pide la duración por encima del tope
                pedidas = _calculate_image_count(cap_duration_sec, cap_n, EXPECTED_CHAPTER_COUNT, capped=False)
                ranked = sorted(range(1, len(cap_out["image_prompts"]) + 1),
                                key=lambda k: (cap_out["image_prompts"][k - 1].get("emotional_rank") or "R3", k))
                cap_out["reencuadres_propuestos"] = v3img.reencuadres(pedidas, len(cap_out["image_prompts"]), ranked)
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
    if f8_beats:                                          # F8 §1 D–E: motivos, cuerpos y planos medios del video
        by_cap = {c["chapter_number"]: (c.get("image_prompts") if "image_prompts" in c else c.pop("_f8_items", []))
                  for c in output_chapters}
        output["_f8_imagenes"] = _f8_fix_video(topic, skel_by_n, narr_by_n, by_cap)
        for c in output_chapters:
            c.pop("_f8_items", None)
            if "supplemental_image_prompts" in c:         # caps Veo: los supplementals rehechos vuelven a su forma
                c["supplemental_image_prompts"] = [
                    {"prompt": it["prompt"], "narration_anchor": it["narration_anchor"], "art_profile": "",
                     "raw_llm_prompt": it.get("raw_llm_prompt"),
                     **{k: it[k] for k in ("beat", "sensible", "motivos", *CLAVES_F8_PAPEL) if k in it}}
                    for it in by_cap[c["chapter_number"]][1:]]

    # PR 1 chat 24: persistir solo el video_id como referencia. El sync_map
    # autoritativo vive en output/audio/<id>/sync_map.json — duplicarlo acá
    # crearía drift. PR 3 lo cargará desde el path autoritativo.
    if sync_map is not None:
        output["_sync_map_ref"] = sync_map.get("video_id")

    _persist(topic_id, output)
    return output
