"""
script_engine/m01b_narrator.py — lo que queda del narrador viejo (Módulo 01b).

F41 (DECISIONES 2026-10-27 20:59, una sola cadena): el narrador cap por cap (`generate_narration`, `regenerate_caps`,
sus prompts, reintentos y esquemas) se borró con la cadena vieja de fase1_5. Queda el validador de un cap que usa la
cadena única:
  _validate_narration / NarrationValidationError   largo por rol, primera oración del hook, aperturas y cierres
                                                   prohibidos, conectores genéricos y (con `f5`) las reglas del pool
                                                   (m05_narrative.cap_problems) — lo llama m01b_guionista.review
  _len_range                                       la banda de caracteres por rol — m01d_particion.len_range
"""

import re


# ═══════════════════════════════════════════════════════════════
#  CONSTANTES
# ═══════════════════════════════════════════════════════════════

# Largos por rol (chars). F23 §1.2: derivados de video_length (palabras × 6; antes, fijos: 300–800 / 800–2000 /
# 400–1100)
from script_engine.video_length import char_band as _char_band  # noqa: E402
LEN_HOOK = _char_band("hook")
LEN_DEVELOPMENT = _char_band("development")
LEN_OUTRO = _char_band("reveal_outro")


# Hook: primera oración debe ser corta y de impacto
HOOK_FIRST_SENTENCE_MAX_WORDS = 12


# Frases prohibidas — clichés de YouTube que matan retención
FORBIDDEN_OPENINGS = (
    "hoy les voy a contar",
    "hoy te voy a contar",
    "en este video",
    "bienvenidos",
    "bienvenido a",
    "hola a todos",
    "qué tal",
)
FORBIDDEN_CLOSINGS = (
    "si te gustó",
    "suscríbete",
    "suscribite",
    "dejá tu comentario",
    "deja tu comentario",
    "compartí con",
    "comparte con",
    "hasta el próximo",
    "hasta la próxima",
    "no olvides darle like",
    "dale like",
)
GENERIC_CONNECTORS = (
    "a continuación",
    "por otra parte",
    "por otro lado",
    "sigamos con",
    "veamos ahora",
    "como vimos antes",
)


# ═══════════════════════════════════════════════════════════════
#  VALIDACIONES DETERMINÍSTICAS
# ═══════════════════════════════════════════════════════════════

class NarrationValidationError(ValueError):
    """Narración emitida por Flash no cumple el contrato del módulo 01b.

    `kind` tipa la falla para que el retry decida sin string-matchear el mensaje:
      "empty" | "length" | "first_sentence" | "phrase" | "other".
    `detail` lleva el dato accionable (p.ej. la frase prohibida emitida) para
    armar la dirección targeteada del reintento.
    """

    def __init__(self, msg: str, *, kind: str = "other", detail: str | None = None):
        super().__init__(msg)
        self.kind = kind
        self.detail = detail


_SENTENCE_END = re.compile(r"[.!?]+")


def _first_sentence(text: str) -> str:
    """Devuelve la primera oración del texto.

    Chat 32: ignora marcadores de pausa "..." al inicio. Si el hook abre con
    una pausa, la validación de ≤N palabras debe medir la PRIMERA FRASE REAL,
    no el "...".
    """
    text = text.strip()
    text = re.sub(r"^[.…\s]+", "", text).strip()  # saltar "..." / "…" iniciales
    m = _SENTENCE_END.search(text)
    if not m:
        return text
    return text[: m.end()].strip()


def _word_count(text: str) -> int:
    return len([w for w in text.split() if w.strip()])


def _contains_any(text: str, needles: tuple[str, ...]) -> str | None:
    """Devuelve el primer needle encontrado o None."""
    tl = text.lower()
    for n in needles:
        if n in tl:
            return n
    return None


def _len_range(role: str, min_factor: float = 1.0) -> tuple[int, int]:
    lo, hi = LEN_HOOK if role == "hook" else (LEN_OUTRO if role == "reveal_outro" else LEN_DEVELOPMENT)
    return min(int(round(lo * min_factor)), hi), hi


def _validate_narration(text: str, role: str, cap_number: int, f5: dict | None = None,
                        min_factor: float = 1.0) -> None:
    """Valida largo, primera oración (si hook), y frases prohibidas. Con `f5` ({pool, skeleton, previous}), además
    las reglas del evidence_pool (F5 §1.3) → kind="evidence" con la lista de problemas en `detail`."""
    if not isinstance(text, str) or not text.strip():
        raise NarrationValidationError(f"cap {cap_number}: narration vacía", kind="empty")

    n = len(text)

    # Largo según rol (F5d: `min_factor` sube el mínimo)
    lo, hi = _len_range(role, min_factor)

    if n < lo or n > hi:
        raise NarrationValidationError(
            f"cap {cap_number} ({role}): largo {n} fuera de rango [{lo}, {hi}]",
            kind="length",
        )

    # Hook: primera oración corta
    if role == "hook":
        first = _first_sentence(text)
        wc = _word_count(first)
        if wc > HOOK_FIRST_SENTENCE_MAX_WORDS:
            raise NarrationValidationError(
                f"cap 1 (hook): primera oración tiene {wc} palabras "
                f"(máx {HOOK_FIRST_SENTENCE_MAX_WORDS}): \"{first}\"",
                kind="first_sentence",
            )

    # Frases prohibidas en apertura
    head = text[:200].lower()
    bad = _contains_any(head, FORBIDDEN_OPENINGS)
    if bad:
        raise NarrationValidationError(
            f"cap {cap_number}: apertura prohibida — contiene \"{bad}\"",
            kind="phrase", detail=bad,
        )

    # Frases prohibidas en cierre (especialmente outro)
    tail = text[-200:].lower()
    bad = _contains_any(tail, FORBIDDEN_CLOSINGS)
    if bad:
        raise NarrationValidationError(
            f"cap {cap_number}: cierre prohibido — contiene \"{bad}\"",
            kind="phrase", detail=bad,
        )

    # Conectores genéricos en cualquier parte (suaves, sólo log/warn-style:
    # acá los hacemos bloqueantes para forzar reescritura)
    bad = _contains_any(text.lower(), GENERIC_CONNECTORS)
    if bad:
        raise NarrationValidationError(
            f"cap {cap_number}: conector genérico prohibido — contiene \"{bad}\"",
            kind="phrase", detail=bad,
        )

    if f5 and f5.get("pool"):                         # F5 §1.3: reglas del evidence_pool
        from script_engine.m05_narrative import cap_problems
        probs = cap_problems(text, cap=cap_number, pool=f5["pool"], skeleton=f5["skeleton"],
                             previous=f5.get("previous") or [], declared=f5.get("declared"))
        if probs:
            raise NarrationValidationError(
                f"cap {cap_number}: reglas del evidence_pool — " + " | ".join(probs),
                kind="evidence", detail="\n".join(f"- {x}" for x in probs),
            )
