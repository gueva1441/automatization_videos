# learned_patterns.py
# Conocimiento aprendido por m05 (juez del motor de guion).
# Versionado en git desde el primer commit.
# Editable a mano si hace falta override.
#
# Responsabilidades:
#   1. ROOT_CAUSE_HEURISTICS: mapping declarativo categoría -> módulo causa raíz.
#      Usado por m05 para validar la propuesta del LLM (red de seguridad
#      determinística contra alucinaciones).
#   2. LEARNED_REGEX_PATTERNS: patrones regex aprendidos cuando el usuario
#      aprueba un issue cuyo proposed_regex_pattern viene poblado.
#   3. OTHER_OCCURRENCES: append-only de issues con category="other".
#      Cuando hay 2+ entradas similares -> m05 propone categoría nueva
#      automáticamente (auto-promoción con umbral, sin pedir Y/N al usuario).


# ─── Mapping causa raíz ────────────────────────────────────────────────────────

ROOT_CAUSE_HEURISTICS = {
    "name_leakage":             "m03",
    "text_in_image":            "m03",
    "era_mismatch_anchor":      "m03",
    "era_textual_in_canon":     "m00",
    "anchor_mismatch":          "m03",
    "profile_incoherence":      "m03",
    "anachronism_visual":       "m03",
    "narration_unvisualizable": "m01b",
    "other":                    None,  # LLM propone, sin heurística determinística
}


# ─── Patrones regex aprendidos ─────────────────────────────────────────────────

LEARNED_REGEX_PATTERNS = {
    "name_leakage":             [],
    "text_in_image":            [],
    "era_mismatch_anchor":      [],
    "era_textual_in_canon":     [],
    "anchor_mismatch":          [],
    "profile_incoherence":      [],
    "anachronism_visual":       [],
    "narration_unvisualizable": [],
}


# ─── Registro de "other" para auto-promoción ───────────────────────────────────

OTHER_OCCURRENCES = []
# Estructura por entrada:
# {
#   "topic_id": "...",
#   "issue_id": "cap3_img7_issue1",
#   "what_happened": "...",
#   "proposed_root_cause_module": "m03",
#   "timestamp": "2026-05-04T..."
# }


# ─── APIs ──────────────────────────────────────────────────────────────────────

def get_root_cause(category: str) -> str | None:
    """Heurística: dada una categoría, devolver el módulo causa raíz esperado.
    Devuelve None si la categoría es 'other' o no está mapeada."""
    return ROOT_CAUSE_HEURISTICS.get(category)


def add_learned_regex(category: str, pattern: str) -> None:
    """Agrega un patrón regex aprobado por el usuario al set de la categoría.
    Idempotente: no duplica si ya existe."""
    if category not in LEARNED_REGEX_PATTERNS:
        raise ValueError(
            f"Categoría desconocida: {category!r}. "
            f"Válidas: {list(LEARNED_REGEX_PATTERNS.keys())}"
        )
    if pattern not in LEARNED_REGEX_PATTERNS[category]:
        LEARNED_REGEX_PATTERNS[category].append(pattern)


def record_other(entry: dict) -> None:
    """Registra un issue con category='other' para análisis posterior.
    Lo consume maybe_promote_other()."""
    required = {"topic_id", "issue_id", "what_happened",
                "proposed_root_cause_module", "timestamp"}
    missing = required - set(entry.keys())
    if missing:
        raise ValueError(f"record_other: faltan campos {missing}")
    OTHER_OCCURRENCES.append(entry)


def maybe_promote_other(threshold: int = 2) -> dict | None:
    """Si hay >= threshold entradas en OTHER_OCCURRENCES con bugs similares,
    propone categoría nueva.

    Versión inicial (simplificada): agrupa por proposed_root_cause_module.
    Si 2+ ocurrencias comparten el mismo módulo causa raíz, propone categoría
    nueva con ese módulo asignado.

    TODO: clustering semántico real sobre what_happened (versión futura).

    Devuelve:
        {"proposed_module": "m03", "occurrences": [...], "count": N}
        o None si ninguna agrupación supera el umbral.
    """
    if len(OTHER_OCCURRENCES) < threshold:
        return None

    by_module: dict[str, list] = {}
    for entry in OTHER_OCCURRENCES:
        mod = entry["proposed_root_cause_module"]
        by_module.setdefault(mod, []).append(entry)

    for mod, entries in by_module.items():
        if len(entries) >= threshold:
            return {
                "proposed_module": mod,
                "occurrences": entries,
                "count": len(entries),
            }

    return None
