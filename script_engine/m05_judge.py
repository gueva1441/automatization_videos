"""
script_engine/m05_judge.py — Módulo 05: Juez visual del pipeline.

Audita los outputs de m03 (image_prompts + narration_anchors) en busca de
incoherencias entre lo que dice el narrador y lo que mostrará la imagen.

Arquitectura híbrida (LLM as teacher, regex as student — patrón #25):
  - Stage 1: pre-detección determinística en Python (3 categorías regex-ables).
  - Stage 2: auditoría semántica completa en Flash sobre las 8 categorías.
  - Merge: Stage 2 tiene la última palabra (Regla 14 del prompt).

Refactor chat 19: art_profile fue desconectado del flujo activo. m05 audita
anchor↔prompt sin considerar profile (categoría profile_incoherence eliminada,
catálogo ART_PROFILES ya no se inyecta al LLM).

ROADMAP — 8 piezas (implementación incremental):
  ✅ Pieza 1 — Stage 1: pre-detección determinística (Python puro)
  ✅ Pieza 2 — Stage 2: ensamblaje del prompt + llamada Flash
  ✅ Pieza 3 — Validación dura post-Flash
  ✅ Pieza 4 — Merge Stage 1/Stage 2 + heurística de causa raíz
  ✅ Pieza 5 — Cálculo determinístico del costo del fix
  ✅ Pieza 6 — Reporte gerencial (castellano natural)
  ✅ Pieza 7 — Loop de las 7 llamadas + persistencia (judge_topic)
  ✅ Pieza 8 — Acciones interactivas [V][A][R][S]
"""

# ════════════════════════════════════════════════════════════════════════
#  IMPORTS
# ════════════════════════════════════════════════════════════════════════
import json
import re
from difflib import SequenceMatcher
from pathlib import Path

from gemini_helpers import call_flash_json

from script_engine.learned_patterns import LEARNED_REGEX_PATTERNS, get_root_cause
# B-name-scrub (chat 87): la lógica de matcheo de nombres documentados vive ahora en
# name_matching (módulo hoja, único dueño). m05 la consume y re-exporta los helpers que
# su test sigue importando por nombre (_normalize_text, _extract_last_name); m03 reusa el
# mismo matcher vía scrub_documented_names.
from script_engine.name_matching import (
    _extract_last_name,
    _normalize_text,
    iter_name_patterns,
)

# Form asistido (contrato chat 61): marcadores env-gated por QA_FORM, emitidos ANTES de
# cada input() del juez. Sin QA_FORM no emite → terminal byte-idéntica. El input()/parseo
# de _read_main_menu_choice / _read_issue_choice NO se tocan.
from qa_form_markers import QA_FORM, emit_choice_marker


# ════════════════════════════════════════════════════════════════════════
#  EXCEPCIÓN PROPIA (espejo de VisualValidationError de m03)
# ════════════════════════════════════════════════════════════════════════

class M05ValidationError(ValueError):
    """Levantada cuando Flash no produce JSON válido tras N retries
    o cuando el output no respeta el contrato esperado.

    NO se hace fallback silencioso. NO se degrada a verdict parcial.
    Coherente con el patrón ganador #4 del proyecto.
    """
    pass


# ════════════════════════════════════════════════════════════════════════
#  CONSTANTES — STAGE 1
# ════════════════════════════════════════════════════════════════════════

#: COMMON_LAST_NAME_BLACKLIST / _COMPOUND_PARTICLES / _MIN_LAST_NAME_LEN movidos a
#: name_matching (B-name-scrub, chat 87). El gating de nombres vive ahí; m05 lo consume
#: vía iter_name_patterns.

#: Regex predefinidos para detect_text_in_image. Aplicados case-insensitive.
PREDEFINED_TEXT_REGEX = (
    r"\b\d{1,2}\s+(january|february|march|april|may|june|july|august|september|october|november|december)\b",
    r"\b(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2}\b",
    r"'[^']{2,}'",
    r'"[^"]{2,}"',
    r"\b(letters?|words?|writing|inscription|text)\s+(written|inscribed|visible|readable|showing)\b",
    r"\bshowing\s+(legible|readable|visible)\b",
    r"\b(stamp|sign|label|poster|placard|plaque)\s+(showing|reading|with\s+text|with\s+writing)\b",
)


# ════════════════════════════════════════════════════════════════════════
#  CONSTANTES — STAGE 2
# ════════════════════════════════════════════════════════════════════════

_PROMPT_PATH = Path(__file__).parent / "m05_PROMPT_v1.txt"
_PROMPT_FIXED_START_MARKER = "PARTE FIJA DEL PROMPT (igual en las 7 llamadas)"
_PROMPT_FIXED_END_MARKER = "PARTE VARIABLE DEL PROMPT (cambia por cap, se ensambla en código)"
MAX_RETRY_ATTEMPTS_M05 = 3


# ════════════════════════════════════════════════════════════════════════
#  CONSTANTES — VALIDACIÓN DURA (Pieza 3)
# ════════════════════════════════════════════════════════════════════════

#: Categorías del enum cerrado del schema. Refactor v6 chat 27 agregó
#: `acronym_leak` y `commercial_brand_leak` para el nuevo formato de prompts.
VALID_CATEGORIES = frozenset({
    "name_leakage",
    "text_in_image",
    "era_mismatch_anchor",
    "era_textual_in_canon",
    "anchor_mismatch",
    "anachronism_visual",
    "narration_unvisualizable",
    # Refactor v6 chat 27: 2 categorías nuevas para el nuevo formato de prompts
    "acronym_leak",           # Flux renderizando códigos modelo como texto
    "commercial_brand_leak",  # marcas comerciales (en Ancla o sujeto) renderizadas
    "other",
})

#: Las 3 severities permitidas.
VALID_SEVERITIES = frozenset({"low", "medium", "high"})

#: Los módulos válidos como causa raíz.
VALID_ROOT_CAUSE_MODULES = frozenset({"m00", "m01a", "m01b", "m02", "m03"})

#: Los 2 valores de verdict.
VALID_VERDICTS = frozenset({"PASS", "FLAG"})

#: Los 10 campos mandatorios de cada issue.
ISSUE_REQUIRED_FIELDS = (
    "issue_id",
    "image_index",
    "anchor_excerpt",
    "category",
    "severity",
    "what_happened",
    "why_happened",
    "how_to_fix",
    "proposed_root_cause_module",
    "proposed_regex_pattern",
)

#: Strings narrativos que NO pueden estar vacíos. proposed_regex_pattern queda
#: fuera porque puede ser null. issue_id, anchor_excerpt y los enums se validan
#: aparte con reglas más estrictas.
ISSUE_NONEMPTY_STRING_FIELDS = (
    "what_happened",
    "why_happened",
    "how_to_fix",
)

#: Min palabras en anchor_excerpt. La regla 6 del prompt pide 10-25 palabras
#: pero el LLM a veces lo recorta — aceptamos ≥5 para no romper en exceso.
ANCHOR_EXCERPT_MIN_WORDS = 5

#: Threshold de similitud para anchor_excerpt vs anchor real (Substring fuzzy
#: tolerando typos menores). 0.85 = lo definido en el HANDOFF.
ANCHOR_EXCERPT_SIMILARITY_THRESHOLD = 0.85

#: Regex del formato issue_id.
_ISSUE_ID_REGEX = re.compile(r"^cap\d+_img\d+_issue\d+$")


# ════════════════════════════════════════════════════════════════════════
#  RESPONSE SCHEMA (HANDOFF 66b · R4) — derivado de _validate_chapter_output
#  / _validate_single_issue. Cubre AMBAS formas: PASS (issues=[]) y FLAG
#  (issues con ≥1 item). issues siempre presente (ARRAY); los items, cuando
#  existen, traen los 10 campos mandatorios. Fuerza JSON válido en la fuente.
# ════════════════════════════════════════════════════════════════════════

def _judge_schema() -> dict:
    return {
        "type": "OBJECT",
        "properties": {
            "chapter_id": {"type": "INTEGER"},
            "verdict": {"type": "STRING", "enum": sorted(VALID_VERDICTS)},
            "issues": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "issue_id": {"type": "STRING"},
                        "image_index": {"type": "INTEGER"},
                        "anchor_excerpt": {"type": "STRING"},
                        "category": {"type": "STRING", "enum": sorted(VALID_CATEGORIES)},
                        "severity": {"type": "STRING", "enum": sorted(VALID_SEVERITIES)},
                        "what_happened": {"type": "STRING"},
                        "why_happened": {"type": "STRING"},
                        "how_to_fix": {"type": "STRING"},
                        "proposed_root_cause_module": {
                            "type": "STRING", "enum": sorted(VALID_ROOT_CAUSE_MODULES)},
                        "proposed_regex_pattern": {"type": "STRING"},
                    },
                    "required": list(ISSUE_REQUIRED_FIELDS),
                },
            },
        },
        "required": ["chapter_id", "verdict", "issues"],
    }


# ════════════════════════════════════════════════════════════════════════
#  HELPERS — NORMALIZACIÓN
# ════════════════════════════════════════════════════════════════════════
# _normalize_text + _extract_last_name movidos a name_matching (B-name-scrub, chat 87) y
# se importan arriba. m05 los sigue usando idéntico (sin cambio de comportamiento).


# ════════════════════════════════════════════════════════════════════════
#  STAGE 1 — DETECCIÓN DETERMINÍSTICA (Pieza 1)
# ════════════════════════════════════════════════════════════════════════

def detect_name_leakage(prompt: str, documented_people: list) -> list:
    """Detecta menciones explícitas de personas documentadas en el prompt.

    B-name-scrub (chat 87): el set de patrones (full_name siempre / last_name gateado por
    largo+blacklist) lo provee iter_name_patterns — único dueño del gating. El matcheo se
    mantiene sobre el texto NORMALIZADO y conserva el comportamiento original: si el full_name
    caza para una persona, su last_name NO se chequea (evita el doble hit full+last del mismo
    nombre).
    """
    if not prompt or not documented_people:
        return []

    norm_prompt = _normalize_text(prompt)
    hits = []
    seen_patterns = set()
    matched_people = set()  # id(person) cuyo full_name ya cazó → saltear su last_name

    for _pat, label, person in iter_name_patterns(documented_people):
        if id(person) in matched_people:
            continue
        if re.search(rf"\b{re.escape(_normalize_text(label))}\b", norm_prompt):
            matched_people.add(id(person))
            if label not in seen_patterns:
                hits.append({
                    "category": "name_leakage",
                    "matched_pattern": label,
                })
                seen_patterns.add(label)

    return hits


def detect_text_in_image(prompt: str) -> list:
    """Detecta menciones de texto/letras/firmas legibles en el prompt."""
    if not prompt:
        return []

    hits = []
    seen = set()

    learned = LEARNED_REGEX_PATTERNS.get("text_in_image", []) or []
    all_patterns = list(PREDEFINED_TEXT_REGEX) + list(learned)

    for pat in all_patterns:
        try:
            for m in re.finditer(pat, prompt, flags=re.IGNORECASE):
                matched = m.group(0)
                key = matched.lower()
                if key not in seen:
                    hits.append({
                        "category": "text_in_image",
                        "matched_pattern": matched,
                    })
                    seen.add(key)
        except re.error:
            continue

    return hits


def detect_anachronism_visual(prompt: str, blocklist: list) -> list:
    """Detecta términos del anachronism_blocklist que aparecen literal en el prompt."""
    if not prompt or not blocklist:
        return []

    norm_prompt = _normalize_text(prompt)
    hits = []
    seen = set()

    for term in blocklist:
        term_clean = (term or "").strip()
        if not term_clean:
            continue
        norm_term = _normalize_text(term_clean)
        if not norm_term:
            continue

        if " " in norm_term:
            pat = re.escape(norm_term)
        else:
            pat = rf"\b{re.escape(norm_term)}\b"

        if re.search(pat, norm_prompt):
            if term_clean not in seen:
                hits.append({
                    "category": "anachronism_visual",
                    "matched_pattern": term_clean,
                })
                seen.add(term_clean)

    return hits


def stage1_predetect(images: list, topic_data: dict) -> list:
    """Orquesta las 3 detecciones sobre todas las imgs de un cap."""
    documented_people = topic_data.get("documented_people") or []
    blocklist = topic_data.get("anachronism_blocklist") or []

    pre_detected = []

    for img in images:
        idx = img.get("image_index")
        prompt = img.get("prompt") or ""
        if idx is None or not prompt:
            continue

        for hit in detect_name_leakage(prompt, documented_people):
            pre_detected.append({
                "image_index": idx,
                "category": hit["category"],
                "matched_pattern": hit["matched_pattern"],
            })
        for hit in detect_text_in_image(prompt):
            pre_detected.append({
                "image_index": idx,
                "category": hit["category"],
                "matched_pattern": hit["matched_pattern"],
            })
        for hit in detect_anachronism_visual(prompt, blocklist):
            pre_detected.append({
                "image_index": idx,
                "category": hit["category"],
                "matched_pattern": hit["matched_pattern"],
            })

    return pre_detected


# ════════════════════════════════════════════════════════════════════════
#  STAGE 2 — LLAMADA A FLASH (Pieza 2)
# ════════════════════════════════════════════════════════════════════════

def _load_system_prompt() -> str:
    """Carga la PARTE FIJA del prompt desde m05_PROMPT_v1.txt al import."""
    if not _PROMPT_PATH.exists():
        raise RuntimeError(
            f"m05_judge: no se encontró el prompt en {_PROMPT_PATH}. "
            "Asegurate de que m05_PROMPT_v1.txt esté al lado de m05_judge.py."
        )

    raw = _PROMPT_PATH.read_text(encoding="utf-8")

    if _PROMPT_FIXED_START_MARKER not in raw:
        raise RuntimeError(
            f"m05_judge: marcador '{_PROMPT_FIXED_START_MARKER}' no encontrado."
        )
    if _PROMPT_FIXED_END_MARKER not in raw:
        raise RuntimeError(
            f"m05_judge: marcador '{_PROMPT_FIXED_END_MARKER}' no encontrado."
        )

    after_start = raw.split(_PROMPT_FIXED_START_MARKER, 1)[1]
    fixed_section = after_start.split(_PROMPT_FIXED_END_MARKER, 1)[0]

    lines = fixed_section.splitlines()
    while lines and (lines[0].strip().startswith("=") or not lines[0].strip()):
        lines.pop(0)
    while lines and (lines[-1].strip().startswith("=") or not lines[-1].strip()):
        lines.pop()

    result = "\n".join(lines).strip()

    if not result.startswith("You are"):
        raise RuntimeError(
            f"m05_judge: contenido del prompt extraído no arranca como esperado. "
            f"Primeros 80 chars: {result[:80]!r}"
        )
    return result


SYSTEM_PROMPT_FIXED: str = _load_system_prompt()


def _format_images_block(images: list) -> str:
    """Construye el bloque IMAGES TO AUDIT del input variable."""
    lines = []
    for img in images:
        idx = img.get("image_index")
        anchor = (img.get("narration_anchor") or "").strip()
        prompt_str = (img.get("prompt") or "").strip()
        lines.append(f"  IMG {idx}:")
        lines.append(f"    anchor: {anchor!r}")
        lines.append(f"    prompt: {prompt_str!r}")
        lines.append("")
    return "\n".join(lines).rstrip()


def _format_pre_detected_block(pre_detected: list) -> str:
    """Construye el bloque PRE_DETECTED_ISSUES del input variable."""
    if not pre_detected:
        return "[]"
    return json.dumps(pre_detected, indent=2, ensure_ascii=False)


def build_chapter_prompt(
    chapter_id: int,
    images: list,
    profile: dict,
    topic_data: dict,
    pre_detected: list,
) -> str:
    """Concatena SYSTEM_PROMPT_FIXED + variable_block del cap."""
    era_canon = topic_data.get("era_visual_canon") or {}
    expected_era = (
        era_canon.get("spans")
        or era_canon.get("primary_decade")
        or "(unknown)"
    )
    documented_people = topic_data.get("documented_people") or []
    anachronism_blocklist = topic_data.get("anachronism_blocklist") or []

    images_block = _format_images_block(images)
    pre_detected_block = _format_pre_detected_block(pre_detected)

    variable_block = f"""

--- INPUT -----------------------------------------------------------

TOPIC CONTEXT:
  expected_era: {expected_era!r}
  documented_people: {documented_people}
  anachronism_blocklist: {anachronism_blocklist}

CHAPTER {chapter_id}:
  (Stylistic profile catalog removed in chat 19 refactor — judge each
   image by anchor↔prompt coherence only. Visual style is now governed
   by a single "documentary photography" system_instruction at m03 time.)

IMAGES TO AUDIT ({len(images)} imgs):

{images_block}

PRE_DETECTED_ISSUES (from Stage 1):
{pre_detected_block}

--- YOUR JUDGMENT ---------------------------------------------------

Audit the {len(images)} images above. Return raw JSON.
"""

    return SYSTEM_PROMPT_FIXED + variable_block


def _default_validator(parsed):
    """Validador placeholder (Pieza 2). Reemplazado por Pieza 3 en runtime."""
    if not isinstance(parsed, dict):
        raise M05ValidationError(
            f"Flash devolvió {type(parsed).__name__}, esperaba dict"
        )
    return parsed


def call_flash_for_chapter(
    chapter_id: int,
    images: list,
    profile: dict,
    topic_data: dict,
    pre_detected: list,
    validator_fn=None,
    max_attempts: int = MAX_RETRY_ATTEMPTS_M05,
) -> dict:
    """Llama Flash con el prompt completo, valida, reintenta con feedback.

    Replica el patrón _call_with_validation_retry de m03 (HANDOFF Detalle
    Técnico #3: NO inventar invocación, replicar de m03).

    Args:
      validator_fn: callable(parsed_dict) -> dict normalizado o
                    raise M05ValidationError. Si None usa _default_validator
                    (solo isinstance dict). Para validación dura completa
                    usar build_chapter_validator() — Pieza 3.
      max_attempts: incluye el intento original. 3 = 1 + 2 retries.
    """
    base_prompt = build_chapter_prompt(
        chapter_id, images, profile, topic_data, pre_detected
    )

    if validator_fn is None:
        validator_fn = _default_validator

    attempt_prompt = base_prompt
    last_error = None
    last_raw = None

    for attempt in range(1, max_attempts + 1):
        raw = call_flash_json(attempt_prompt, response_schema=_judge_schema())  # HANDOFF 66b (R4)
        last_raw = raw
        try:
            return validator_fn(raw)
        except M05ValidationError as e:
            last_error = e
            if attempt == max_attempts:
                raise M05ValidationError(
                    f"cap {chapter_id}: Flash falló validación {max_attempts} veces. "
                    f"Último error: {str(e)[:200]}. "
                    f"Último output (truncado): {str(last_raw)[:500]}..."
                ) from e
            print(
                f"  [05] cap {chapter_id}: validación falló intento "
                f"{attempt}/{max_attempts}: {str(e)[:120]}..."
            )
            feedback = f"""

═══════════════════════════════════════════════════
RETRY {attempt + 1}/{max_attempts} — YOUR PREVIOUS ATTEMPT FAILED
═══════════════════════════════════════════════════
PROBLEM DETECTED:
{str(e)}

FIX IT. Rewrite the COMPLETE JSON respecting ALL non-negotiable
rules and the schema. Generate the response from scratch, not
patches over the previous one.
"""
            attempt_prompt = base_prompt + feedback

    raise M05ValidationError(
        f"cap {chapter_id}: retry exhausted sin error capturado "
        f"(last_error={last_error!r})"
    )


# ════════════════════════════════════════════════════════════════════════
#  PIEZA 3 — VALIDACIÓN DURA POST-FLASH
# ════════════════════════════════════════════════════════════════════════

def _is_substring_match(excerpt: str, anchor: str) -> bool:
    """Chequea si excerpt es substring 'real' del anchor (con tolerancia).

    Estrategia (3 caminos, primer match gana):
      1. Match exacto post-normalización (substring literal): TRUE.
      2. Longitudes cercanas (±15%): comparación global con ratio().
         Cubre typos distribuidos que pueden agregar/quitar chars.
      3. Excerpt más corto: ventana sliding sobre anchor + ratio() por
         ventana. Cubre substring real con typos menores.

    Threshold: ANCHOR_EXCERPT_SIMILARITY_THRESHOLD (0.85).

    Args:
      excerpt: texto declarado por el LLM como anchor_excerpt.
      anchor:  narration_anchor real de la imagen.

    Returns:
      True si excerpt está contenido en anchor con tolerancia razonable.
    """
    if not excerpt or not anchor:
        return False

    norm_excerpt = _normalize_text(excerpt)
    norm_anchor = _normalize_text(anchor)

    # 1. Substring exacto post-normalización (caso happy)
    if norm_excerpt in norm_anchor:
        return True

    excerpt_len = len(norm_excerpt)
    anchor_len = len(norm_anchor)
    if anchor_len == 0:
        return False

    # 2. Longitudes cercanas (±15%): ratio global tolera typos distribuidos
    length_ratio = excerpt_len / anchor_len
    if 0.85 <= length_ratio <= 1.15:
        ratio = SequenceMatcher(None, norm_excerpt, norm_anchor, autojunk=False).ratio()
        if ratio >= ANCHOR_EXCERPT_SIMILARITY_THRESHOLD:
            return True

    # 3. Excerpt más corto: ventana sliding sobre el anchor
    if excerpt_len < anchor_len:
        for start in range(anchor_len - excerpt_len + 1):
            window = norm_anchor[start:start + excerpt_len]
            ratio = SequenceMatcher(None, norm_excerpt, window, autojunk=False).ratio()
            if ratio >= ANCHOR_EXCERPT_SIMILARITY_THRESHOLD:
                return True

    return False


def _validate_single_issue(
    issue,
    position: int,
    chapter_id: int,
    images_by_index: dict,
    full_cap_anchor: str,
) -> bool:
    """Valida un issue individual. Levanta M05ValidationError en fallos ESTRUCTURALES
    (schema, enums, image_index inexistente, regex inválido). El único fallo NO-fatal es
    el anchor_excerpt que no matchea la narración: ahí descarta el issue y devuelve False.

    Args:
      issue:           el dict del issue (1 entry de la lista issues).
      position:        índice en la lista (0-based) — solo para mensajes.
      chapter_id:      el chapter_id esperado.
      images_by_index: dict {image_index: img_dict} (para chequear que image_index existe).
      full_cap_anchor: narración COMPLETA del cap (superset de los anchors) contra la que
                       se valida el anchor_excerpt (A1).

    Returns:
      True  → issue válido, conservar.
      False → anchor_excerpt no matchea la narración del cap → DESCARTAR (no-fatal, A2).
    """
    label = f"issue at position {position}"

    if not isinstance(issue, dict):
        raise M05ValidationError(
            f"{label}: must be a dict, got {type(issue).__name__}"
        )

    # 1. Campos mandatorios presentes
    for field in ISSUE_REQUIRED_FIELDS:
        if field not in issue:
            raise M05ValidationError(
                f"{label}: missing mandatory field '{field}'. "
                f"All 10 fields are required: {list(ISSUE_REQUIRED_FIELDS)}"
            )

    # 2. image_index es int
    if not isinstance(issue["image_index"], int):
        raise M05ValidationError(
            f"{label}: image_index must be int, got {type(issue['image_index']).__name__}"
        )

    # 3. Strings no vacíos en campos narrativos
    for f in ISSUE_NONEMPTY_STRING_FIELDS:
        v = issue[f]
        if not isinstance(v, str) or not v.strip():
            raise M05ValidationError(
                f"{label}: field '{f}' must be a non-empty string, "
                f"got {type(v).__name__}={v!r}"
            )

    # 4. Enums
    if issue["category"] not in VALID_CATEGORIES:
        raise M05ValidationError(
            f"{label}: invalid category {issue['category']!r}. "
            f"Must be one of: {sorted(VALID_CATEGORIES)}"
        )
    if issue["severity"] not in VALID_SEVERITIES:
        raise M05ValidationError(
            f"{label}: invalid severity {issue['severity']!r}. "
            f"Must be one of: {sorted(VALID_SEVERITIES)}"
        )
    if issue["proposed_root_cause_module"] not in VALID_ROOT_CAUSE_MODULES:
        raise M05ValidationError(
            f"{label}: invalid proposed_root_cause_module "
            f"{issue['proposed_root_cause_module']!r}. "
            f"Must be one of: {sorted(VALID_ROOT_CAUSE_MODULES)}"
        )

    # 5. issue_id formato y consistencia con chapter_id/image_index
    issue_id = issue["issue_id"]
    if not isinstance(issue_id, str) or not _ISSUE_ID_REGEX.match(issue_id):
        raise M05ValidationError(
            f"{label}: invalid issue_id format {issue_id!r}. "
            f"Expected pattern: 'cap{{N}}_img{{M}}_issue{{K}}' "
            f"(e.g., 'cap{chapter_id}_img{issue['image_index']}_issue1')"
        )
    expected_prefix = f"cap{chapter_id}_img{issue['image_index']}_issue"
    if not issue_id.startswith(expected_prefix):
        raise M05ValidationError(
            f"{label}: issue_id {issue_id!r} inconsistent with "
            f"chapter_id={chapter_id} and image_index={issue['image_index']}. "
            f"Expected prefix: {expected_prefix!r}"
        )

    # 6. image_index existe en el cap
    img_idx = issue["image_index"]
    if img_idx not in images_by_index:
        raise M05ValidationError(
            f"{label}: image_index={img_idx} does not exist in chapter "
            f"{chapter_id}. Valid indexes: {sorted(images_by_index.keys())}"
        )

    # 7. anchor_excerpt no vacío + ≥5 palabras + substring real del anchor
    excerpt = issue["anchor_excerpt"]
    if not isinstance(excerpt, str) or not excerpt.strip():
        raise M05ValidationError(
            f"{label}: anchor_excerpt must be a non-empty string, "
            f"got {type(excerpt).__name__}={excerpt!r}"
        )
    excerpt = excerpt.strip()
    word_count = len(excerpt.split())
    if word_count < ANCHOR_EXCERPT_MIN_WORDS:
        raise M05ValidationError(
            f"{label}: anchor_excerpt too short ({word_count} words). "
            f"Should be a 10-25 word verbatim substring of the anchor."
        )

    # A1: validar contra la narración COMPLETA del cap (full_cap_anchor = superset de todos
    # los anchors), NO la rebanada de 1 imagen. Flash cita narración real cruzando el borde
    # entre rebanadas; con la rebanada angosta el fuzzy 0.85 rechazaba un excerpt legítimo.
    # A2: el mismatch NO es fatal — se DESCARTA el issue (cita = metadata diagnóstica) y se
    # sigue. Una cita mal copiada nunca debe matar el topic; los demás issues sobreviven.
    if not _is_substring_match(excerpt, full_cap_anchor):
        print(
            f"  [05] {label}: anchor_excerpt no matchea la narración del cap "
            f"(image_index={img_idx}) — issue DESCARTADO (no-fatal). "
            f"Excerpt: {excerpt[:60]!r}..."
        )
        return False

    # 8. proposed_regex_pattern: null o regex válido
    regex = issue["proposed_regex_pattern"]
    if regex is not None:
        if not isinstance(regex, str):
            raise M05ValidationError(
                f"{label}: proposed_regex_pattern must be null or a string, "
                f"got {type(regex).__name__}"
            )
        try:
            re.compile(regex)
        except re.error as e:
            raise M05ValidationError(
                f"{label}: proposed_regex_pattern {regex!r} is not a valid "
                f"Python regex: {e}"
            )

    return True


def validate_chapter_output(
    parsed,
    chapter_id: int,
    images: list,
) -> dict:
    """Validación dura del output de Flash para 1 cap (Pieza 3).

    Aplica las 14 reglas inviolables del schema. Si falla, levanta
    M05ValidationError con mensaje específico para feedback de retry.

    Args:
      parsed: dict directamente de Flash (post call_flash_json).
      chapter_id: el chapter_id esperado.
      images: lista de imgs del cap (con image_index y narration_anchor).

    Returns:
      Dict validado (igual al input si todo OK).

    Raises:
      M05ValidationError con mensaje accionable.
    """
    # 1. Shape global
    if not isinstance(parsed, dict):
        raise M05ValidationError(
            f"Flash output must be a dict, got {type(parsed).__name__}"
        )

    # 2. chapter_id presente y correcto
    cid = parsed.get("chapter_id")
    if cid != chapter_id:
        raise M05ValidationError(
            f"Output chapter_id={cid!r} does not match expected {chapter_id}. "
            f"Make sure chapter_id is an integer matching the chapter you're auditing."
        )

    # 3. verdict en enum
    verdict = parsed.get("verdict")
    if verdict not in VALID_VERDICTS:
        raise M05ValidationError(
            f"Invalid verdict {verdict!r}. Must be one of: {sorted(VALID_VERDICTS)}"
        )

    # 4. issues es lista
    issues = parsed.get("issues")
    if not isinstance(issues, list):
        raise M05ValidationError(
            f"'issues' must be a list, got {type(issues).__name__}"
        )

    # 5. PASS implica issues vacíos
    if verdict == "PASS" and len(issues) > 0:
        raise M05ValidationError(
            f"verdict='PASS' but issues array has {len(issues)} entries. "
            f"PASS requires an empty issues array."
        )

    # 6. FLAG implica al menos 1 issue
    if verdict == "FLAG" and len(issues) == 0:
        raise M05ValidationError(
            "verdict='FLAG' but issues array is empty. "
            "FLAG requires at least one issue."
        )

    # 7. Validar cada issue
    images_by_index = {
        img["image_index"]: img
        for img in images
        if "image_index" in img
    }
    # A1: superset = unión de los anchors de TODAS las imágenes del cap (orden de image_index),
    # construido 1 vez por cap. El anchor_excerpt (narración real que cruza bordes entre
    # rebanadas) matchea contra el superset aunque no caiga dentro de una sola rebanada.
    full_cap_anchor = " ".join(
        (images_by_index[i].get("narration_anchor") or "")
        for i in sorted(images_by_index)
    )
    # A2: los issues cuyo anchor_excerpt no matchea se DESCARTAN (no-fatal); el resto sobrevive.
    kept_issues = [
        issue
        for position, issue in enumerate(issues)
        if _validate_single_issue(
            issue, position, chapter_id, images_by_index, full_cap_anchor
        )
    ]
    parsed["issues"] = kept_issues

    return parsed


def build_chapter_validator(chapter_id: int, images: list):
    """Fábrica de closure para usar como validator_fn de call_flash_for_chapter.

    Captura chapter_id e images para que el validator se pueda invocar como
    `validator(parsed_dict)` sin parámetros extra.

    Returns:
      callable(parsed) -> dict, raise M05ValidationError on failure.
    """
    def _validator(parsed):
        return validate_chapter_output(parsed, chapter_id, images)
    return _validator


# ════════════════════════════════════════════════════════════════════════
#  PIEZA 4 — MERGE STAGE 1 ↔ STAGE 2 + HEURÍSTICA DE CAUSA RAÍZ
# ════════════════════════════════════════════════════════════════════════

def merge_stage1_stage2(
    stage2_issues: list,
    stage1_predetected: list,
    chapter_id: int = None,
) -> list:
    """Merge entre Stage 1 (pre-detección Python) y Stage 2 (LLM).

    Implementa la Regla 14 del prompt: el LLM tiene autoridad final.

    Lógica:
      - stage2_issues se respeta tal cual (LLM as teacher — patrón #25).
      - Si Stage 1 detectó algo y Stage 2 lo re-emitió → respetado.
      - Si Stage 1 detectó algo y Stage 2 NO lo re-emitió → falso positivo
        desde el punto de vista del LLM. Se descarta silenciosamente con
        un log informativo (audit, no acción).
      - Stage 1 NUNCA agrega issues que Stage 2 no haya confirmado.

    Args:
      stage2_issues: lista de issues validada que devolvió el LLM (Pieza 3).
      stage1_predetected: lista de hits de Stage 1 (pre-Flash).
      chapter_id: opcional, solo para logs informativos.

    Returns:
      Lista de issues final (= stage2_issues sin modificar).
    """
    if not stage1_predetected:
        return stage2_issues

    # Auditar Stage 1 hits que NO fueron re-emitidos por Stage 2
    cap_label = f"cap {chapter_id}" if chapter_id is not None else "cap ?"
    for s1_hit in stage1_predetected:
        s1_idx = s1_hit.get("image_index")
        s1_cat = s1_hit.get("category")
        confirmed = any(
            issue.get("image_index") == s1_idx and issue.get("category") == s1_cat
            for issue in stage2_issues
        )
        if not confirmed:
            pattern = s1_hit.get("matched_pattern", "?")
            print(
                f"  [05] {cap_label}: Stage 1 detectó {s1_cat!r} en img "
                f"{s1_idx} (pattern={pattern!r}) pero LLM lo silenció. "
                "Tratando como falso positivo (Regla 14)."
            )

    return stage2_issues


def validate_root_cause(issue: dict) -> dict:
    """Compara la propuesta de causa raíz del LLM con la heurística declarativa.

    Mutación in-place del issue:
      - Agrega 'root_cause_conflict' (bool).
      - Si hay conflicto, agrega 'heuristic_root_cause_module' (str) con el
        valor que la heurística esperaba. El reporte gerencial (Pieza 6)
        muestra ambos valores cuando hay conflicto para que el usuario
        decida.

    Reglas:
      - heuristic == llm_proposed         → no conflict.
      - heuristic is None (category='other'
        o categoría desconocida)         → no conflict (LLM tiene autoridad).
      - heuristic != llm_proposed         → conflict.

    NOTA: esta función NO levanta excepciones. Un conflicto de causa raíz
    es información para el reporte, no una falla del módulo.

    Args:
      issue: dict del issue ya validado por Pieza 3 (debe tener 'category'
             y 'proposed_root_cause_module').

    Returns:
      El mismo dict, mutado.
    """
    category = issue.get("category")
    llm_proposed = issue.get("proposed_root_cause_module")
    heuristic = get_root_cause(category)

    if heuristic is None or heuristic == llm_proposed:
        issue["root_cause_conflict"] = False
        return issue

    # Conflicto: ambas propuestas se preservan para el reporte
    issue["root_cause_conflict"] = True
    issue["heuristic_root_cause_module"] = heuristic
    return issue


# ════════════════════════════════════════════════════════════════════════
#  PIEZA 5 — CÁLCULO DETERMINÍSTICO DEL COSTO DEL FIX
# ════════════════════════════════════════════════════════════════════════

#: Tabla de costos por módulo. Valores del HANDOFF Bloque 4 Pieza 5.
#:
#: - cost_usd:  costo aprox de re-correr ese módulo sobre 1 topic.
#: - minutes:   tiempo aprox de re-corrida.
#: - downstream: módulos que dependen de este y deben re-correrse después.
#:
#: m05 incluido (re-juzgar siempre tras un fix). Coherente con el costo
#: runtime proyectado del HANDOFF (~$0.005/video para m05).
COST_TABLE = {
    "m00":  {"cost_usd": 0.025, "minutes": 5, "downstream": ["m01a", "m01b", "m02", "m03"]},
    "m01a": {"cost_usd": 0.005, "minutes": 1, "downstream": ["m01b", "m02", "m03"]},
    "m01b": {"cost_usd": 0.015, "minutes": 3, "downstream": ["m02", "m03"]},
    "m02":  {"cost_usd": 0.001, "minutes": 1, "downstream": ["m03"]},
    "m03":  {"cost_usd": 0.012, "minutes": 2, "downstream": []},
    "m05":  {"cost_usd": 0.005, "minutes": 1, "downstream": []},
}


def estimate_fix_cost(root_cause_module: str) -> dict:
    """Estima costo + tiempo de aplicar un fix con causa raíz dada.

    Cadena de ejecución:
      [root_cause_module] + downstream(root_cause_module) + ["m05"]

    Args:
      root_cause_module: módulo causa raíz declarado en el issue. Debe ser
        clave válida de COST_TABLE excluyendo m05.

    Returns:
      {
        "total_cost_usd": float,    # suma de todos los módulos en la cadena
        "total_minutes":  int,      # suma de minutos
        "chain":          list,     # módulos en orden de ejecución
        "chain_str":      str,      # "m00 → m01a → m01b → m02 → m03 → m05"
      }

    Raises:
      ValueError: si root_cause_module no está en COST_TABLE o es 'm05'
        (m05 nunca puede ser causa raíz de un issue: el juez juzga,
        no es juzgado).
    """
    if root_cause_module not in COST_TABLE:
        raise ValueError(
            f"estimate_fix_cost: módulo desconocido {root_cause_module!r}. "
            f"Válidos: {sorted(COST_TABLE.keys())}"
        )
    if root_cause_module == "m05":
        raise ValueError(
            "estimate_fix_cost: 'm05' no puede ser causa raíz de un issue. "
            "El juez no se audita a sí mismo."
        )

    entry = COST_TABLE[root_cause_module]
    chain = [root_cause_module] + list(entry["downstream"]) + ["m05"]

    total_cost_usd = 0.0
    total_minutes = 0
    for module in chain:
        m_entry = COST_TABLE[module]
        total_cost_usd += m_entry["cost_usd"]
        total_minutes += m_entry["minutes"]

    return {
        "total_cost_usd": round(total_cost_usd, 4),
        "total_minutes": total_minutes,
        "chain": chain,
        "chain_str": " → ".join(chain),
    }


# ════════════════════════════════════════════════════════════════════════
#  PIEZA 6 — REPORTE GERENCIAL (CASTELLANO NATURAL)
# ════════════════════════════════════════════════════════════════════════

#: Orden lineal del pipeline. Para deduplicar cadenas de fix.
_MODULE_PIPELINE_ORDER = ("m00", "m01a", "m01b", "m02", "m03", "m05")

#: Ancho del separador visual del reporte.
_REPORT_WIDTH = 64

#: Mapeo severity → emoji.
_SEVERITY_EMOJI = {
    "low":    "🟢",
    "medium": "🟡",
    "high":   "🔴",
}


def _earliest_module(modules: list) -> str:
    """Devuelve el módulo más upstream (más temprano en el pipeline)."""
    return min(modules, key=lambda m: _MODULE_PIPELINE_ORDER.index(m))


def _compute_global_fix_plan(issues: list) -> dict:
    """Calcula la cadena de fix DEDUPLICADA y el costo total.

    Lógica: como el pipeline es lineal, la cadena del módulo más upstream
    subsume a todas las cadenas más cortas. Si hay issues con causa raíz
    m02 y m03, basta correr m02 → m03 → m05 una sola vez para arreglar
    todo.

    Args:
      issues: lista de issues (cada uno con 'proposed_root_cause_module').

    Returns:
      Dict con chain, total_cost_usd, total_minutes, chain_str.
      Si no hay issues: chain=[], cost=0.0, minutes=0.
    """
    if not issues:
        return {
            "chain": [],
            "total_cost_usd": 0.0,
            "total_minutes": 0,
            "chain_str": "",
        }

    root_modules = [
        issue.get("proposed_root_cause_module")
        for issue in issues
        if issue.get("proposed_root_cause_module")
    ]
    if not root_modules:
        return {
            "chain": [],
            "total_cost_usd": 0.0,
            "total_minutes": 0,
            "chain_str": "",
        }

    earliest = _earliest_module(root_modules)
    return estimate_fix_cost(earliest)


def _global_verdict_emoji(verdict: str, issues: list) -> str:
    """Devuelve el emoji que va con el veredicto global.

    PASS → 🟢
    FLAG con cualquier severity=high → 🔴
    FLAG sin highs → 🟡
    """
    if verdict == "PASS":
        return "🟢"
    if any(issue.get("severity") == "high" for issue in issues):
        return "🔴"
    return "🟡"


def _format_issue_block(issue: dict, position: int, total: int) -> str:
    """Formatea un issue individual del reporte.

    Args:
      issue: dict del issue (debe tener 'chapter_id' inyectado por Pieza 7).
        Si tiene 'cohort' y 'cohort_total' (de Pieza 9 voting), se muestra
        la cohorte en el header del issue.
      position: número 1-indexed del issue.
      total: total de issues en el reporte.

    Returns:
      Bloque string del issue listo para concatenar.
    """
    sep = "─" * _REPORT_WIDTH
    sev = issue.get("severity", "medium")
    sev_emoji = _SEVERITY_EMOJI.get(sev, "🟡")
    chapter_id = issue.get("chapter_id", "?")
    img_idx = issue.get("image_index", "?")

    # Pieza 9: header de cohorte si el issue viene de un voting merge
    cohort = issue.get("cohort")
    cohort_total = issue.get("cohort_total")
    cohort_str = ""
    if cohort is not None and cohort_total is not None:
        if cohort == cohort_total:
            cohort_emoji = "🎯"  # consenso unánime
            cohort_label = "alta confianza"
        elif cohort * 2 > cohort_total:
            cohort_emoji = "⚠"  # mayoría
            cohort_label = "mayoría"
        else:
            cohort_emoji = "❓"  # minoría
            cohort_label = "baja confianza"
        cohort_str = (
            f"   ·   {cohort_emoji} {cohort}/{cohort_total} ({cohort_label})"
        )

    lines = []
    lines.append(sep)
    lines.append(
        f"  ISSUE {position} de {total}   ·   {sev_emoji} {sev}"
        f"   ·   Capítulo {chapter_id}, imagen {img_idx}{cohort_str}"
    )
    lines.append(sep)
    lines.append(f"  Categoría: {issue.get('category', '?')}")
    lines.append("")
    lines.append(f"  📖 Anchor: \"{issue.get('anchor_excerpt', '')}\"")
    lines.append("")
    lines.append("  🐛 Qué pasó:")
    lines.append(f"     {issue.get('what_happened', '')}")
    lines.append("")
    lines.append("  🔍 Por qué pasó:")
    lines.append(f"     {issue.get('why_happened', '')}")
    lines.append("")
    lines.append("  🛠 Cómo arreglarlo:")
    lines.append(f"     {issue.get('how_to_fix', '')}")
    lines.append("")

    # Costo individual del fix de ESTE issue
    rc = issue.get("proposed_root_cause_module")
    if rc and rc in COST_TABLE and rc != "m05":
        cost_data = estimate_fix_cost(rc)
        lines.append(
            f"  ⏱ Costo del fix: ${cost_data['total_cost_usd']:.3f} "
            f"(~{cost_data['total_minutes']} min)"
        )
        lines.append(f"     Cadena: {cost_data['chain_str']}")
        lines.append("")

    # Patrón regex sugerido (si aplica)
    regex = issue.get("proposed_regex_pattern")
    if regex:
        lines.append("  🔧 Patrón regex sugerido:")
        lines.append(f"     {regex}")
        lines.append("")

    # Conflicto de causa raíz (si aplica)
    if issue.get("root_cause_conflict"):
        heuristic = issue.get("heuristic_root_cause_module", "?")
        lines.append("  ⚠ Conflicto de causa raíz:")
        lines.append(f"     LLM propone:     {rc}")
        lines.append(f"     Heurística dice: {heuristic}")
        lines.append("     (decidí cuál preferís — afecta el costo del fix)")
        lines.append("")

    return "\n".join(lines)


def render_report(
    topic_title: str,
    all_issues: list,
    global_verdict: str,
) -> str:
    """Genera el reporte gerencial completo, listo para print().

    Args:
      topic_title: título humano del topic, para el header.
      all_issues: lista de TODOS los issues acumulados de los 7 caps.
        Cada issue debe tener 'chapter_id' inyectado por Pieza 7.
      global_verdict: 'PASS' | 'FLAG'.

    Returns:
      String multi-línea con el reporte completo (header + issues + footer).
    """
    sep_thick = "═" * _REPORT_WIDTH
    parts = []

    # ─── HEADER ──────────────────────────────────────────────────
    parts.append(sep_thick)
    parts.append(f"  m05 — VEREDICTO PARA \"{topic_title}\"")
    parts.append(sep_thick)
    parts.append("")

    verdict_emoji = _global_verdict_emoji(global_verdict, all_issues)
    if global_verdict == "PASS":
        parts.append(f"  Estado global: {verdict_emoji} PASS — sin issues. ¡Listo para m04!")
        parts.append("")
        parts.append(sep_thick)
        parts.append("")
        return "\n".join(parts)

    # FLAG: hay issues
    n_issues = len(all_issues)
    parts.append(
        f"  Estado global: {verdict_emoji} FLAG ({n_issues} "
        f"issue{'s' if n_issues != 1 else ''} encontrado{'s' if n_issues != 1 else ''})"
    )

    # ─── COSTO TOTAL DEDUPLICADO ─────────────────────────────────
    plan = _compute_global_fix_plan(all_issues)
    if plan["chain"]:
        parts.append(
            f"  Costo total estimado para aplicar todos los fixes: "
            f"${plan['total_cost_usd']:.3f} (~{plan['total_minutes']} min)"
        )
        parts.append(f"  Plan: {plan['chain_str']}")

    parts.append("")

    # ─── ISSUES ──────────────────────────────────────────────────
    for i, issue in enumerate(all_issues, start=1):
        parts.append(_format_issue_block(issue, i, n_issues))

    # ─── FOOTER ──────────────────────────────────────────────────
    parts.append(sep_thick)
    parts.append("  ¿Qué hacés?")
    parts.append("")
    parts.append("    [V] Ver issue por issue (decidir uno a uno)")
    parts.append("    [A] Aprobar todos y aplicar fixes")
    parts.append("    [R] Rechazar todos")
    parts.append("    [S] Salir sin acción")
    parts.append(sep_thick)
    parts.append("")

    return "\n".join(parts)


# ════════════════════════════════════════════════════════════════════════
#  PIEZA 7 — LOOP DE LAS 7 LLAMADAS + PERSISTENCIA (judge_topic)
# ════════════════════════════════════════════════════════════════════════

#: Nombre del archivo de output de m05.
_JUDGE_OUTPUT_FILENAME = "05_judge.json"

#: Nombres de los inputs upstream (los archivos que m05 consume).
_UPSTREAM_FILES = {
    "skeleton": "01a_skeleton.json",
    "narration": "01b_narration.json",
    "profiles":  "02_profiles.json",   # opcional desde FASE 5
    "visual":    "03_visual.json",
}


def _resolve_data_paths(data_root: Path = None) -> tuple:
    """Resuelve las rutas a topics_db.json y _steps/.

    Si data_root es None, usa config.DATA_DIR de producción (lazy import).
    Si se provee, lo usa directo (testing con tempdir).
    """
    if data_root is None:
        from config import DATA_DIR  # lazy: evita romper imports en tests
        data_root = DATA_DIR
    data_root = Path(data_root)
    topics_db_path = data_root / "topics_db.json"
    steps_dir = data_root / "scripts" / "_steps"
    return topics_db_path, steps_dir


def _load_topic_by_id(topic_id: str, topics_db_path: Path) -> dict:
    """Carga un topic específico desde topics_db.json.

    Raises:
      FileNotFoundError: si topics_db.json no existe.
      KeyError:          si no hay un topic con ese topic_id.
    """
    if not topics_db_path.exists():
        raise FileNotFoundError(
            f"m05: topics_db.json no encontrado en {topics_db_path}"
        )

    raw = json.loads(topics_db_path.read_text(encoding="utf-8"))
    # Soportar ambos shapes vistos en el repo (lista directa o dict con 'topics')
    if isinstance(raw, dict) and "topics" in raw:
        topics = raw["topics"]
    elif isinstance(raw, list):
        topics = raw
    else:
        raise ValueError(
            f"m05: topics_db.json tiene shape desconocido (ni list ni dict con 'topics')"
        )

    for topic in topics:
        # Coherente con m03: matchea por 'id' (campo real en DB) o
        # 'topic_id' (alias usado en outputs intermedios)
        if topic.get("id") == topic_id or topic.get("topic_id") == topic_id:
            return topic

    raise KeyError(
        f"m05: topic_id {topic_id!r} no encontrado en {topics_db_path}"
    )


def _load_upstream_step(topic_id: str, filename: str, steps_dir: Path) -> dict:
    """Carga un archivo upstream desde _steps/{topic_id}/{filename}.

    Raises:
      FileNotFoundError: si el archivo no existe (módulo upstream no corrió).
    """
    path = steps_dir / topic_id / filename
    if not path.exists():
        raise FileNotFoundError(
            f"m05: archivo {filename} no encontrado en {path}. "
            f"Asegurate de haber corrido el módulo correspondiente antes de m05."
        )
    return json.loads(path.read_text(encoding="utf-8"))


def _normalize_chapter_images(
    cap_visual: dict, render_engine: str, cap_profile: str
) -> list:
    """Convierte el shape de m03 a [{image_index, prompt, narration_anchor,
    art_profile}, ...].

    Refactor chat 19: art_profile fue desconectado del flujo activo. La key
    se mantiene en el dict como string vacío para backward compat — m05 ya
    no la usa para audit.

    flux: cap tiene image_prompts[] con cada item con 'prompt' +
          'narration_anchor'.
    veo:  cap tiene image_prompt + narration_anchor.

    Args:
        cap_visual:    dict con el cap del 03_visual.json.
        render_engine: 'flux' o 'veo'.
        cap_profile:   art_profile cap-level legacy. Backward-compat solo;
                       no afecta el audit.

    Raises:
        ValueError: si render_engine no es 'flux' ni 'veo'.
    """
    if render_engine == "veo":
        # Item base del clip Veo (siempre, incluso si el cap no es híbrido).
        items: list[dict] = [{
            "image_index": 1,
            "prompt": (cap_visual.get("image_prompt") or "").strip(),
            "narration_anchor": (cap_visual.get("narration_anchor") or "").strip(),
            "art_profile": (cap_visual.get("art_profile") or cap_profile).strip(),
            "subtype": "veo_clip",
        }]
        # Chat 29 #175: supplementals del cap híbrido. Cada uno se audita como
        # Flux puro (anchor substring, prompt EN, regex patterns, metadata leak).
        # Si supplemental_image_prompts es None/[] (cap veo legacy o pre-chat29),
        # items queda con solo el veo_clip → comportamiento backward-compat.
        # NO escondemos supps con prompt vacío: los incluimos para que m05 los
        # flagee como issue.
        supplementals = cap_visual.get("supplemental_image_prompts") or []
        for offset, supp in enumerate(supplementals, start=1):
            items.append({
                "image_index": 1 + offset,
                "prompt": (supp.get("prompt") or "").strip(),
                "narration_anchor": (supp.get("narration_anchor") or "").strip(),
                "art_profile": (supp.get("art_profile") or cap_profile).strip(),
                "subtype": "flux_supplemental",
            })
        return items
    if render_engine == "flux":
        items = cap_visual.get("image_prompts") or []
        return [
            {
                "image_index": idx + 1,
                "prompt": (item.get("prompt") or "").strip(),
                "narration_anchor": (item.get("narration_anchor") or "").strip(),
                "art_profile": (item.get("art_profile") or cap_profile).strip(),
            }
            for idx, item in enumerate(items)
        ]
    raise ValueError(
        f"m05: render_engine desconocido: {render_engine!r}. "
        f"Esperado 'flux' o 'veo'."
    )


def _persist_judge_output(topic_id: str, output: dict, steps_dir: Path) -> Path:
    """Persiste el output de m05 en _steps/{topic_id}/05_judge.json."""
    step_dir = steps_dir / topic_id
    step_dir.mkdir(parents=True, exist_ok=True)
    out_file = step_dir / _JUDGE_OUTPUT_FILENAME
    out_file.write_text(
        json.dumps(output, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return out_file


def judge_topic(topic_id: str, data_root: Path = None, interactive: bool = False) -> dict:
    """API pública de m05. Audita las visualizaciones de un topic completo.

    Carga inputs (topic + outputs de m01a, m01b, m03; m02 opcional —
    catálogo art_profiles desconectado en chat 19), corre las 7 llamadas
    Flash (1 por cap) con Stage 1 + Stage 2 + validación + merge, valida
    causa raíz, genera reporte gerencial y persiste resultado.

    Args:
      topic_id: UUID del topic a auditar.
      data_root: opcional. Path raíz de datos (default: config.DATA_DIR).
                 Útil para tests con tempdir.
      interactive: si True, imprime el reporte y pide acción al usuario
                   ([V][A][R][S]). Default False (función pura, no lee stdin).

    Returns:
      Dict con todo el resultado:
        {
          "topic_id":        str,
          "topic_title":     str,
          "global_verdict":  "PASS" | "FLAG",
          "chapters":        list[{chapter_id, verdict, issues}],
          "all_issues":      list[issue]  # plana con chapter_id inyectado
          "cost_data":       dict (de _compute_global_fix_plan),
          "report_str":      str (renderizado por render_report),
          "user_decision":   dict (solo si interactive=True),
        }

    Raises:
      FileNotFoundError: si falta topics_db.json o algún input upstream.
      KeyError:          si topic_id no existe.
      ValueError:        si render_engine de algún cap es desconocido.
      M05ValidationError: si algún cap falla validación tras 3 retries.
    """
    topics_db_path, steps_dir = _resolve_data_paths(data_root)

    # 1. Cargar inputs
    print(f"  [05] Auditando topic {topic_id}...")
    topic = _load_topic_by_id(topic_id, topics_db_path)
    skeleton = _load_upstream_step(topic_id, _UPSTREAM_FILES["skeleton"], steps_dir)
    # profiles_data es opcional: catálogo art_profiles desconectado en chat 19.
    # Si 02_profiles.json existe (topics viejos), se carga como contexto legacy
    # pero ya no afecta el audit.
    try:
        profiles_data = _load_upstream_step(topic_id, _UPSTREAM_FILES["profiles"], steps_dir)
    except FileNotFoundError:
        profiles_data = None
    visual = _load_upstream_step(topic_id, _UPSTREAM_FILES["visual"], steps_dir)
    # Nota: 01b_narration.json NO se carga porque las narrations ya viajan
    # como narration_anchor dentro del 03_visual.json. Se mantiene como
    # parte del contrato upstream pero m05 no lo necesita directamente.

    # Indexar por chapter_number para acceso O(1).
    # Si profiles_data es None (catálogo desconectado en chat 19), profiles_by_cap
    # queda vacío y el loop downstream tolera la ausencia.
    profiles_by_cap = (
        {p["chapter_number"]: p for p in profiles_data.get("chapters", [])}
        if profiles_data
        else {}
    )
    visual_by_cap = {
        v["chapter_number"]: v
        for v in visual.get("chapters", [])
    }
    skeleton_by_cap = {
        s["chapter_number"]: s
        for s in skeleton.get("chapters", [])
    }

    if not visual_by_cap:
        raise ValueError(
            f"m05: 03_visual.json para topic {topic_id} no tiene chapters."
        )

    # 2. Loop por cap (orden creciente)
    chapters_results = []
    all_issues = []

    for chapter_id in sorted(visual_by_cap.keys()):
        sch = skeleton_by_cap.get(chapter_id, {})
        render_engine = sch.get("render_engine", "flux")
        cap_visual = visual_by_cap[chapter_id]
        # profile cap-level es opcional (legacy desde chat 19). Si existe se
        # carga, pero ya no se usa para audit; queda solo para backward compat
        # del shape de los dicts de imagen.
        profile = profiles_by_cap.get(chapter_id) or {}
        cap_profile_label = (profile.get("art_profile") or "").strip()
        images = _normalize_chapter_images(
            cap_visual, render_engine, cap_profile_label
        )
        print(
            f"  [05] cap {chapter_id} ({render_engine}): {len(images)} imgs"
        )

        # 2b. Stage 1 — pre-detección determinística
        pre_detected = stage1_predetect(images, topic)

        # 2c. Stage 2 — Flash con validator dura
        validator = build_chapter_validator(chapter_id, images)
        chapter_output = call_flash_for_chapter(
            chapter_id,
            images,
            profile,
            topic,
            pre_detected,
            validator_fn=validator,
        )

        # 2d. Merge Stage 1/Stage 2 + auditar silenciados
        merged_issues = merge_stage1_stage2(
            chapter_output["issues"],
            pre_detected,
            chapter_id=chapter_id,
        )

        # 2e. Validar causa raíz + inyectar chapter_id en cada issue
        for issue in merged_issues:
            validate_root_cause(issue)
            issue["chapter_id"] = chapter_id

        chapters_results.append({
            "chapter_id": chapter_id,
            "verdict": chapter_output["verdict"],
            "issues": merged_issues,
        })
        all_issues.extend(merged_issues)

    # 3. Verdict global
    global_verdict = (
        "FLAG"
        if any(c["verdict"] == "FLAG" for c in chapters_results)
        else "PASS"
    )

    # 4. Costo total deduplicado
    cost_data = _compute_global_fix_plan(all_issues)

    # 5. Reporte gerencial
    topic_title = topic.get("video_title", topic_id)
    report_str = render_report(topic_title, all_issues, global_verdict)

    # 6. Persistir output
    output = {
        "topic_id": topic_id,
        "topic_title": topic_title,
        "global_verdict": global_verdict,
        "chapters": chapters_results,
        "all_issues": all_issues,
        "cost_data": cost_data,
        "report_str": report_str,
    }
    _persist_judge_output(topic_id, output, steps_dir)

    # 7. Modo interactivo (opcional)
    if interactive:
        print(report_str)
        user_decision = prompt_user_action(output)
        output["user_decision"] = user_decision

    return output


# ════════════════════════════════════════════════════════════════════════
#  PIEZA 8 — ACCIONES INTERACTIVAS [V][A][R][S]
# ════════════════════════════════════════════════════════════════════════
#
# Esta pieza SOLO registra la decisión del usuario. NO ejecuta re-runs ni
# borra archivos ni toca el estado del proyecto. El actuador completo
# (re-run desde causa raíz, manejo de __bak_previous, opción [C][B][S]
# post-rerun) está reservado para Bloque 6.

#: Set de teclas válidas del menú principal.
_MAIN_MENU_KEYS = frozenset({"V", "A", "R", "S"})

#: Set de teclas válidas del prompt por issue (modo Ver).
_PER_ISSUE_KEYS = frozenset({"y", "n", "s"})

#: Mapeo de tecla del prompt por issue → decisión registrada.
_DECISION_MAP = {"y": "approved", "n": "rejected", "s": "skipped"}


def _read_main_menu_choice() -> str:
    """Lee tecla del menú principal del usuario, re-pidiendo si es inválida."""
    while True:
        choice = input("Opción [V/A/R/S]: ").strip().upper()
        if choice in _MAIN_MENU_KEYS:
            return choice
        print(f"  Opción {choice!r} inválida. Usá V, A, R o S.")


def _read_issue_choice() -> str:
    """Lee tecla del prompt por issue (y/n/s)."""
    while True:
        sub = input("    ¿Aprobar? [y]es / [n]o / [s]kip: ").strip().lower()
        if sub in _PER_ISSUE_KEYS:
            return sub
        print(f"    Opción {sub!r} inválida.")


def prompt_user_action(judge_output: dict) -> dict:
    """Lee acción del usuario sobre el reporte (V/A/R/S).

    NO ejecuta re-runs. Solo registra la decisión. El actuador real
    está reservado para Bloque 6 (loop autocorrectivo Estrategia A).

    Si el verdict global es PASS, no hay nada que decidir y retorna
    'no_op_pass' silenciosamente.

    Args:
      judge_output: dict que devolvió judge_topic.

    Returns:
      Dict con la decisión:
        {
          "action":    "no_op_pass" | "viewed" | "approved_all" |
                       "rejected_all" | "exited",
          "decisions": list[{issue_id, decision}],  # solo viewed
          "plan_str":  str | None,                  # solo approved_all
        }
    """
    if judge_output.get("global_verdict") == "PASS":
        return {"action": "no_op_pass", "decisions": [], "plan_str": None}

    issues = judge_output.get("all_issues", []) or []
    # GATE JUEZ (form): PASS ya salió arriba sin marcador → la barra sigue sola. Acá hay
    # issues: emitimos el marcador (display-only) ANTES del input de SIEMPRE, que no se toca.
    if QA_FORM:
        emit_choice_marker(
            menu="judge_action",
            prompt=f"El juez marcó {len(issues)} issue(s) — revisá antes de gastar en imágenes",
            options=[
                {"key": "V", "label": "Ver issues uno por uno"},
                {"key": "A", "label": "Aprobar todos los fixes"},
                {"key": "R", "label": "Rechazar todos (seguir igual)"},
                {"key": "S", "label": "Salir sin acción"},
            ],
            default="R",
            payload={
                "verdict": judge_output.get("global_verdict"),
                "issues": [
                    {
                        "id": i.get("issue_id"),
                        "cap": i.get("chapter_id"),
                        "img": i.get("image_index"),
                        "cat": i.get("category"),
                        "sev": i.get("severity"),
                        "cohort": i.get("cohort"),
                        "cohort_total": i.get("cohort_total"),
                        "reason": (i.get("what_happened") or "")[:200],
                    }
                    for i in issues
                ],
            },
        )
    choice = _read_main_menu_choice()

    if choice == "S":
        print("  Saliendo sin acción.")
        return {"action": "exited", "decisions": [], "plan_str": None}

    if choice == "R":
        print("  Todos los issues rechazados. Sin cambios.")
        return {"action": "rejected_all", "decisions": [], "plan_str": None}

    if choice == "A":
        cost = judge_output.get("cost_data") or {}
        plan_str = (
            f"Plan: {cost.get('chain_str', '?')} "
            f"(~${cost.get('total_cost_usd', 0):.3f}, "
            f"~{cost.get('total_minutes', 0)} min)"
        )
        print(f"\n  ✓ Aprobaste todos los fixes ({len(issues)} issues).")
        print(f"  {plan_str}")
        print(
            "  ⚠ Pieza 8 solo registra la decisión. "
            "El actuador real lo trae Bloque 6 (loop autocorrectivo)."
        )
        return {
            "action": "approved_all",
            "decisions": [
                {"issue_id": i.get("issue_id"), "decision": "approved"}
                for i in issues
            ],
            "plan_str": plan_str,
        }

    # choice == "V": loop por issue
    decisions = []
    total = len(issues)
    for i, issue in enumerate(issues, start=1):
        print(
            f"\n  Issue {i}/{total}: {issue.get('issue_id', '?')} "
            f"({issue.get('category', '?')})"
        )
        print(
            f"    Cap {issue.get('chapter_id', '?')}, "
            f"img {issue.get('image_index', '?')}, "
            f"severity={issue.get('severity', '?')}"
        )
        # SUB-GATE JUEZ (form): el sub-loop [y/n/s] también necesita su marcador, o cuelga
        # mudo. Env-gated, ANTES del input de _read_issue_choice (que no se toca).
        if QA_FORM:
            emit_choice_marker(
                menu="judge_issue",
                prompt=f"Issue {i}/{total}: {issue.get('category', '?')} — ¿aprobar el fix?",
                options=[
                    {"key": "y", "label": "Aprobar este fix"},
                    {"key": "n", "label": "Rechazar"},
                    {"key": "s", "label": "Saltear"},
                ],
                default="s",
                body=(
                    f"Cap {issue.get('chapter_id', '?')} · img {issue.get('image_index', '?')} "
                    f"· severidad {issue.get('severity', '?')}\n\n"
                    f"Qué pasó:\n{issue.get('what_happened', '')}\n\n"
                    f"Cómo arreglar:\n{issue.get('how_to_fix', '')}"
                ),
            )
        sub = _read_issue_choice()
        decisions.append({
            "issue_id": issue.get("issue_id"),
            "decision": _DECISION_MAP[sub],
        })

    summary = {d["decision"]: 0 for d in (
        {"decision": "approved"}, {"decision": "rejected"}, {"decision": "skipped"}
    )}
    for d in decisions:
        summary[d["decision"]] += 1
    print(
        f"\n  Resumen: {summary['approved']} aprobados, "
        f"{summary['rejected']} rechazados, "
        f"{summary['skipped']} salteados."
    )
    print(
        "  ⚠ Pieza 8 solo registra la decisión. "
        "El actuador real lo trae Bloque 6."
    )

    return {"action": "viewed", "decisions": decisions, "plan_str": None}


# ════════════════════════════════════════════════════════════════════════
#  PIEZA 9 — VOTING (N corridas con dedup + cohorte)
# ════════════════════════════════════════════════════════════════════════
#
# El juez tiene varianza inherente al modelo (Flash). Misma entrada puede
# devolver issues distintos en corridas distintas. Empíricamente medimos
# ~50% de issues coincidentes entre 2 corridas sobre el mismo input.
#
# Voting: corremos m05 N veces, agrupamos issues por clave canónica
# (chapter_id, image_index, category) y emitimos cada issue ÚNICO con
# su cohorte (cuántas de las N corridas lo detectaron).
#
# Diseño:
#   - 3/3 → 🎯 alta confianza (consenso unánime)
#   - 2/3 → ⚠ mayoría (probable bug real con divergencia menor)
#   - 1/3 → ❓ baja confianza (probable ruido del juez, revisar manualmente)
#
# Por decisión arquitectónica del usuario: se reportan TODOS los issues
# (cohorte ≥1), no se filtra. La cohorte es metadata informativa que el
# usuario revisa al decidir qué fixes aplicar.
# ════════════════════════════════════════════════════════════════════════


def _voting_key(issue: dict) -> tuple:
    """Clave canónica para deduplicar issues entre corridas.

    Returns:
      Tuple (chapter_id, image_index, category) — los 3 ejes del schema
      que identifican un issue distinto. Dos issues con la misma clave
      son la "misma observación" en N corridas.
    """
    return (
        issue.get("chapter_id"),
        issue.get("image_index"),
        issue.get("category"),
    )


def _merge_runs_with_voting(runs: list[dict], n_runs: int) -> dict:
    """Merge de N outputs de judge_topic agregando cohorte a cada issue.

    Args:
      runs: lista de N outputs de judge_topic (cada uno con 'all_issues').
      n_runs: total de corridas (para validar y para metadata).

    Returns:
      Dict con shape similar a judge_topic + 'cohort' en cada issue:
        {
          "topic_id":       str,
          "topic_title":    str,
          "global_verdict": "FLAG" | "PASS",
          "all_issues":     list[issue+cohort],  # ordenados por cohort desc
          "n_runs":         int,
          "voting_stats":   dict (counts por cohort),
        }

    Notas:
      - Para cada issue único, conservamos la versión del PRIMER run que
        lo detectó (consistencia de campos como what_happened/proposed_*).
      - global_verdict es "PASS" solo si TODAS las corridas dijeron PASS.
      - Issues con cohort=N (todas las corridas) van primero en all_issues.
    """
    if not runs:
        raise ValueError("_merge_runs_with_voting: lista de runs vacía")

    # Acumular issues por clave canónica
    by_key: dict[tuple, dict] = {}
    cohort_counts: dict[tuple, int] = {}

    for run in runs:
        # Set de claves vistas en ESTE run (para no contar 2 veces si una
        # corrida emite el mismo issue duplicado por algún bug raro)
        seen_in_run: set[tuple] = set()
        for issue in run.get("all_issues", []):
            key = _voting_key(issue)
            if key in seen_in_run:
                continue
            seen_in_run.add(key)
            cohort_counts[key] = cohort_counts.get(key, 0) + 1
            # Conservar la primera versión del issue (por orden de runs)
            if key not in by_key:
                by_key[key] = dict(issue)  # copia defensiva

    # Inyectar cohort en cada issue + ordenar por cohort desc, luego severity
    _SEVERITY_RANK = {"high": 0, "medium": 1, "low": 2}
    merged_issues = []
    for key, issue in by_key.items():
        issue["cohort"] = cohort_counts[key]
        issue["cohort_total"] = n_runs
        merged_issues.append(issue)

    merged_issues.sort(
        key=lambda i: (
            -i["cohort"],  # cohort alto primero
            _SEVERITY_RANK.get(i.get("severity", "medium"), 1),  # high primero
            i.get("chapter_id", 0),
            i.get("image_index", 0),
        )
    )

    # Veredicto global: PASS solo si TODAS las corridas dijeron PASS
    all_pass = all(r.get("global_verdict") == "PASS" for r in runs)
    global_verdict = "PASS" if all_pass and not merged_issues else "FLAG"

    # Stats de voting
    voting_stats = {
        f"cohort_{c}_of_{n_runs}": sum(1 for k, v in cohort_counts.items() if v == c)
        for c in range(1, n_runs + 1)
    }
    voting_stats["total_unique_issues"] = len(merged_issues)
    voting_stats["total_runs"] = n_runs

    return {
        "topic_id": runs[0].get("topic_id"),
        "topic_title": runs[0].get("topic_title"),
        "global_verdict": global_verdict,
        "all_issues": merged_issues,
        "n_runs": n_runs,
        "voting_stats": voting_stats,
        "individual_runs": [r.get("all_issues", []) for r in runs],
    }


def judge_topic_with_voting(
    topic_id: str,
    n: int = 3,
    data_root: Path = None,
) -> dict:
    """Wrapper de judge_topic que corre N veces y devuelve issues con cohorte.

    Cada corrida es una llamada independiente a judge_topic (con sus 7
    llamadas Flash internas). El costo total es ~N x el de una sola corrida.

    Args:
      topic_id: UUID del topic a auditar.
      n: cantidad de corridas (default 3). Recomendado 2-5.
      data_root: opcional. Path raíz de datos (default: config.DATA_DIR).

    Returns:
      Dict con shape similar a judge_topic, con extras:
        - all_issues: cada issue tiene 'cohort' (1..N) y 'cohort_total' (N)
        - n_runs: int
        - voting_stats: counts por cohort
        - individual_runs: list[list[issue]] para inspección
        - report_str: render con cohortes visibles
        - cost_data: del primer run (válido representativo)

    Notas:
      - Las corridas individuales NO se persisten en disco por esta función
        — eso queda para el caller (test_module_05_voting_live.py).
      - El reporte final REEMPLAZA al de las corridas individuales.
    """
    if n < 2:
        raise ValueError(f"judge_topic_with_voting: n debe ser ≥ 2 (recibí {n})")
    if n > 10:
        raise ValueError(f"judge_topic_with_voting: n > 10 es prohibitivo (recibí {n})")

    print(f"  [05-voting] Corriendo m05 {n} veces sobre topic {topic_id}...")
    runs = []
    for i in range(1, n + 1):
        print(f"\n  ── Corrida {i}/{n} ─────────────────────────────────────")
        run_output = judge_topic(topic_id, data_root=data_root, interactive=False)
        runs.append(run_output)
        run_issues = len(run_output.get("all_issues", []))
        print(f"  ← Corrida {i}/{n} completada: {run_issues} issues")

    print(f"\n  [05-voting] Mergeando {n} corridas con dedup por (cap, img, category)...")
    merged = _merge_runs_with_voting(runs, n_runs=n)

    # Reporte final con cohortes
    merged["report_str"] = render_report(
        topic_title=merged["topic_title"],
        all_issues=merged["all_issues"],
        global_verdict=merged["global_verdict"],
    )

    # cost_data del primer run como representativo (los demás son ~iguales)
    if runs:
        merged["cost_data"] = runs[0].get("cost_data", {})

    # Gate interactivo post-voting (chat 26: Omar pide auditoría siempre)
    print(merged["report_str"])
    user_decision = prompt_user_action(merged)
    merged["user_decision"] = user_decision

    return merged


# ════════════════════════════════════════════════════════════════════════
