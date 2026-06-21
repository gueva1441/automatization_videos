"""name_matching.py — único dueño de la lógica "qué string cuenta como nombre documentado".

Movido desde m05_judge.py (chat 87, B-name-scrub) para que m03 pueda reusar el matcher sin
crear una dependencia m03→m05. Provee:
  - los helpers de normalización (`_normalize_text`, `_extract_last_name`) que m05 sigue consumiendo,
  - la primitiva compartida `iter_name_patterns` (gating de full_name / last_name en un solo lugar),
  - el scrub determinístico post-LLM `scrub_documented_names` que usa m03.

INVARIANTE: el scrub solo toca el texto de PROMPT que va a Kling. Nunca la narración ni el
`narration_anchor` (sync temporal, substring exacto). Ver HANDOFF B-name-scrub.
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


def _extract_last_name(full_name: str) -> str:
    """Extrae el last_name normalizado de un nombre completo."""
    tokens = (full_name or "").strip().split()
    if not tokens:
        return ""
    if len(tokens) == 1:
        return _normalize_text(tokens[0])

    last_tokens = [tokens[-1]]
    i = len(tokens) - 2
    while i >= 1 and _normalize_text(tokens[i]) in _COMPOUND_PARTICLES:
        last_tokens.insert(0, tokens[i])
        i -= 1
    return _normalize_text(" ".join(last_tokens))


def iter_name_patterns(documented_people):
    """Único dueño de "qué string cuenta como nombre".

    Yield (regex_pattern, label, person). full_name siempre; last_name solo si
    len>=_MIN_LAST_NAME_LEN y su token core no está en la blacklist. El `regex_pattern`
    es sobre el texto crudo (lo usa el scrub con IGNORECASE); el `label` es el string
    documentado (lo reporta m05 como matched_pattern: full crudo / last normalizado).
    """
    for person in documented_people or []:
        full = (person.get("name") or "").strip()
        if not full:
            continue
        yield (rf"\b{re.escape(full)}\b", full, person)
        last = _extract_last_name(full)
        if (last and len(last.replace(" ", "")) >= _MIN_LAST_NAME_LEN
                and last.split()[-1] not in COMMON_LAST_NAME_BLACKLIST):
            yield (rf"\b{re.escape(last)}\b", last, person)


def _neutral_descriptor(person):
    """(b) rol+era breve. NO inventar: usar campos del documented_people."""
    role = (person.get("role") or "").strip()
    era = (person.get("era") or "").strip()
    if role and era:
        return f"a {role} of the {era} era"
    if role:
        return f"a {role}"
    return "a person of the era"


def scrub_documented_names(prompt, documented_people):
    """Reemplaza nombres documentados por un descriptor neutro.

    CASE-INSENSITIVE sobre el prompt ORIGINAL (el reemplazo va en el texto real, no en el
    normalizado). Devuelve (prompt_scrubeado, [hits para log]). No-op si no hay prompt o
    no hay gente documentada.
    """
    if not prompt or not documented_people:
        return prompt, []
    out, hits = prompt, []
    for pat, label, person in iter_name_patterns(documented_people):
        repl = _neutral_descriptor(person)
        new = re.sub(pat, repl, out, flags=re.IGNORECASE)
        if new != out:
            hits.append({"matched": label, "repl": repl})
            out = new
    return out, hits
