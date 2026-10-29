"""name_matching.py — único dueño de la lógica "qué string cuenta como nombre documentado".

Movido desde m05_judge.py (chat 87, B-name-scrub) para que m03 pueda reusar el matcher sin
crear una dependencia m03→m05. Provee:
  - los helpers de normalización (`_normalize_text`, `_extract_last_name`) que m05 sigue consumiendo,
  - la primitiva compartida `iter_name_patterns` (gating de full_name / last_name en un solo lugar).

F51c: se borró el scrub post-LLM `scrub_documented_names` (en Wittenoom, 0 nombres reales en 96 fotos
y 1 falso positivo: «Court» en «Supreme Court»).
"""
import re
import unicodedata

#: Apellidos comunes en inglés que generan falsos positivos masivos.
COMMON_LAST_NAME_BLACKLIST = frozenset({
    "smith", "king", "wood", "brown", "white", "black", "green", "young",
    "hall", "ford", "lake", "stone", "rivers", "fields", "hills", "lane",
    "page", "cook", "bell", "may", "moore", "long", "short", "small",
    "free", "rich", "rose", "fair", "wise", "best", "key", "reed",
})

#: Partículas de last_names compuestos (von Braun, de la Cruz, ...).
_COMPOUND_PARTICLES = frozenset({
    "von", "van", "de", "del", "la", "da", "di", "der", "den", "du", "le",
})

#: Min length de un last_name antes del chequeo de blacklist.
_MIN_LAST_NAME_LEN = 5


def _normalize_text(s: str) -> str:
    """NFKD-normaliza, decompone diacríticos, lowercase. Idempotente."""
    if not s:
        return ""
    nfkd = unicodedata.normalize("NFKD", s)
    return "".join(c for c in nfkd if not unicodedata.combining(c)).lower()


def _extract_last_name(full_name: str, raw: bool = False) -> str:
    """Extrae el last_name de un nombre completo.
    raw=False (default): normalizado (minúscula, sin diacríticos) — blacklist-check + label.
    raw=True: PRESERVA el caso original — para el pattern case-sensitive."""
    tokens = (full_name or "").strip().split()
    if not tokens:
        return ""
    if len(tokens) == 1:
        return tokens[0] if raw else _normalize_text(tokens[0])

    last_tokens = [tokens[-1]]
    i = len(tokens) - 2
    while i >= 1 and _normalize_text(tokens[i]) in _COMPOUND_PARTICLES:
        last_tokens.insert(0, tokens[i])
        i -= 1
    joined = " ".join(last_tokens)
    return joined if raw else _normalize_text(joined)


def iter_name_patterns(documented_people):
    """Único dueño de "qué string cuenta como nombre".

    Yield (regex_pattern, label, person). full_name siempre; last_name solo si
    len>=_MIN_LAST_NAME_LEN y su token core no está en la blacklist. El `regex_pattern`
    es sobre el texto crudo (m05 lo busca con IGNORECASE); el `label` es el string
    documentado (lo reporta m05 como matched_pattern: full crudo / last normalizado).
    """
    for person in documented_people or []:
        full = (person.get("name") or "").strip()
        if not full:
            continue
        yield (rf"\b{re.escape(full)}\b", full, person)
        last = _extract_last_name(full)               # normalizado: blacklist-check + label (m05)
        raw_last = _extract_last_name(full, raw=True)  # caso preservado: para el pattern
        if (last and len(last.replace(" ", "")) >= _MIN_LAST_NAME_LEN
                and last.split()[-1] not in COMMON_LAST_NAME_BLACKLIST):
            # (?-i:...) sobre la forma CAPITALIZADA: "Orange" (apellido) matchea,
            # "orange" (color) NO. El label yieldeado sigue normalizado (m05 lo espera así).
            yield (rf"\b(?-i:{re.escape(raw_last)})\b", last, person)

