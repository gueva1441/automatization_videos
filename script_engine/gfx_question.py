"""
gfx_question.py — Pregunta de cierre automática por capítulo (F3, pedido de Omar 2026-10-20).

Contrato:
    entrada  últimas 3 frases del cap + primeras 3 del cap siguiente
    salida   UNA pregunta ≤ 8 palabras (token question_max_words_auto), abierta (Qué / Cómo / Por qué / Quién /
             Cuánto / Dónde), CONCRETA (sujeto reconocible: personas, lugar u objeto del cap siguiente; F4 §1.2, few-shot
             con las de Omar), que apunte a lo que viene en el cap siguiente, sin sí/no y sin repetir una cifra ya dicha
    valida   rechaza si empieza con "¿El/La/Los/Las…" (sí/no), si no empieza con un interrogativo abierto, si pasa de
             8 palabras, si es abstracta (moral, destino, transformó…), si repite una cifra ya dicha o si no comparte
             ningún sustantivo con las 3 primeras frases del cap siguiente. 2 reintentos; si fallan → sin pregunta.
    candado  NO es texto del guion: se guarda con generated: true (excepción explícita en gfx_literal_lock).

La respuesta se cachea en work_dir/gfx_question_chNN.json (el lab la puede regenerar o editar ahí mismo).
"""
from __future__ import annotations

import json
import re
import time
import unicodedata
from pathlib import Path
from typing import Any, Callable

OPEN_STARTS = ("qué", "cómo", "por qué", "quién", "quiénes", "cuánto", "cuánta", "cuántos", "cuántas", "dónde")
YESNO_STARTS = ("el", "la", "los", "las")
MAX_WORDS = 8                      # F4 §1.2 (antes 12); el perfil lo pisa con question_max_words_auto
ATTEMPTS = 3                       # 1 + 2 reintentos
# F4 §1.2: preguntas del tipo que escribió Omar (concretas, cortas, sujeto reconocible)
FEW_SHOT = ("¿Quién fue el culpable?", "¿Qué pasó con los presos del tercer piso?", "¿Por qué nadie abrió las celdas?")
# raíces (sin tildes, 5 letras) de palabras abstractas: la pregunta tiene que apuntar a un hecho, no a una reflexión
_ABSTRACT = {"moral", "desti", "alma", "almas", "signi", "senti", "esper", "human", "trans", "verda", "conci", "espir",
             "simbo", "esenc", "ident", "natur", "legad", "lecci", "justi", "liber"}

# palabras que NO cuentan como "sustantivo compartido" (funcionales y verbos/adverbios muy comunes)
_NOT_NOUN = {
    "este", "esta", "estos", "estas", "ese", "esa", "esos", "esas", "aquel", "aquella", "ellos", "ellas", "todo", "toda",
    "todos", "todas", "otro", "otra", "otros", "otras", "cada", "mucho", "mucha", "muchos", "muchas", "poco", "pocos",
    "sobre", "entre", "desde", "hasta", "hacia", "pero", "porque", "cuando", "donde", "mientras", "aunque", "también",
    "solo", "sólo", "tan", "tanto", "tras", "ante", "bajo", "según", "durante", "sería", "serían", "había", "habían",
    "estaba", "estaban", "fueron", "eran", "tenía", "tenían", "podría", "podrían", "puede", "pueden", "nuevo", "nueva",
    "aquel", "aquellos", "aquellas", "algo", "nada", "nadie", "alguien", "mismo", "misma", "ellos", "ahora", "luego",
    "entonces", "después", "antes", "siempre", "nunca", "aún", "todavía", "ya", "realmente", "quizás",
}
_FUNC = {"de", "del", "la", "las", "el", "los", "un", "una", "unos", "unas", "y", "o", "en", "a", "al", "que", "qué",
         "por", "con", "para", "sin", "se", "su", "sus", "lo", "le", "les", "es", "fue", "era", "cómo", "como", "cuál",
         "cuáles", "cuánto", "cuántos", "cuántas", "quién", "quiénes", "dónde", "cuándo", "más", "muy", "no"}

SYSTEM = ("Sos guionista de un canal documental de misterios. Escribís la PREGUNTA DE CIERRE de un capítulo: la que el "
          "espectador se lleva y que se responde en el capítulo siguiente. Respondés SOLO JSON.")


def _strip_accents(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def sentences(text: str) -> list[str]:
    """Frases de una narración (corte en . ! ? … sin perder ¿…? completas)."""
    parts = re.split(r"(?<=[.!?…])\s+", re.sub(r"\s+", " ", str(text)).strip())
    return [p.strip() for p in parts if p.strip()]


def nouns(text: str) -> set[str]:
    """Aproximación de sustantivos sin etiquetador: palabras de contenido ≥ 4 letras que no son funcionales ni
    verbos/adverbios comunes, comparadas por raíz de 5 letras sin tildes (cubre singular/plural y género)."""
    out = set()
    for w in re.findall(r"[a-záéíóúñü]+", str(text).lower()):
        if len(w) >= 4 and w not in _FUNC and w not in _NOT_NOUN:
            out.add(_strip_accents(w)[:5])
    return out


def figures(text: str) -> set[str]:
    """Cifras escritas en el texto, normalizadas (6,500 → 6500)."""
    return {re.sub(r"[.,]", "", f) for f in re.findall(r"\d[\d.,]*", str(text))}


def clean(q: str) -> str:
    q = re.sub(r"\s+", " ", str(q)).strip().strip('"').strip()
    q = q.rstrip(".")
    if not q.startswith("¿"):
        q = "¿" + q
    if not q.endswith("?"):
        q += "?"
    return q


def max_words() -> int:
    try:
        from gfx_config import gfx_rules
        return int(gfx_rules.question_max_words_auto)
    except Exception:  # noqa: BLE001 — sin motor (tests aislados) → constante del contrato
        return MAX_WORDS


def abstract_words(body: str) -> list[str]:
    return [w for w in re.findall(r"[a-záéíóúñü]+", body.lower()) if _strip_accents(w)[:5] in _ABSTRACT]


def validate(q: str, next_first3: list[str], said_before: str) -> str | None:
    """None si la pregunta cumple el contrato; si no, el motivo del rechazo (corto, para el log y el lab)."""
    body = clean(q)[1:-1].strip()
    low = body.lower()
    first = re.findall(r"[a-záéíóúñü]+", low)[:2]
    if not first:
        return "vacía"
    if first[0] in YESNO_STARTS:
        return f"se responde con sí/no (empieza con «{first[0]}»)"
    if not any(low.startswith(s) for s in OPEN_STARTS):
        return f"no empieza con Qué/Cómo/Por qué/Quién/Cuánto/Dónde («{first[0]}»)"
    n, top = len(body.split()), max_words()
    if n > top:
        return f"{n} palabras (máx {top})"
    abst = abstract_words(body)
    if abst:
        return f"abstracta ({', '.join(abst)}): tiene que apuntar a un hecho concreto"
    rep = figures(body) & figures(said_before)
    if rep:
        return f"repite una cifra ya dicha ({', '.join(sorted(rep))})"
    if not nouns(body) & nouns(" ".join(next_first3)):
        return "no comparte ningún sustantivo con el inicio del capítulo siguiente"
    return None


def build_prompt(last3: list[str], next_first3: list[str], rejected: list[tuple[str, str]]) -> str:
    rej = "".join(f"\n- «{q}» → rechazada: {why}" for q, why in rejected)
    return (
        "FINAL DEL CAPÍTULO ACTUAL (últimas 3 frases):\n" + "\n".join(f"- {s}" for s in last3) +
        "\n\nCOMIENZO DEL CAPÍTULO SIGUIENTE (primeras 3 frases, el espectador todavía NO las escuchó):\n" +
        "\n".join(f"- {s}" for s in next_first3) +
        "\n\nEscribí UNA pregunta de cierre en español rioplatense neutro:\n"
        f"- máximo {max_words()} palabras;\n"
        "- CONCRETA: un sujeto que el espectador reconoce (personas, un lugar, un objeto) y un hecho; nada abstracto "
        "(moral, destino, transformación, significado);\n"
        "- abierta: empieza con ¿Qué, ¿Cómo, ¿Por qué, ¿Quién, ¿Cuánto o ¿Dónde (nunca algo que se conteste sí/no);\n"
        "- apunta a lo que viene en el capítulo siguiente, usando al menos un sustantivo de esas 3 frases, sin responderlo;\n"
        "- sin cifras que ya se dijeron.\n"
        "\nASÍ SON las preguntas de este canal (el tono, no el contenido): " + " · ".join(FEW_SHOT) + "\n"
        + (f"\nIntentos anteriores que NO sirvieron:{rej}\n" if rej else "") +
        '\nDevolvé {"pregunta": "¿…?"}'
    )


def generate(narr_cap: str, narr_next: str, said_before: str, *,
             call: Callable[..., dict] | None = None, attempts: int = ATTEMPTS) -> dict[str, Any]:
    """{"text": pregunta | None, "intentos": [{"pregunta", "rechazo"}…]}. `call` = call_flash_json (inyectable)."""
    if call is None:
        from gemini_helpers import call_flash_json as call
    last3, next3 = sentences(narr_cap)[-3:], sentences(narr_next)[:3]
    tried: list[dict[str, Any]] = []
    rejected: list[tuple[str, str]] = []
    if not last3 or not next3:
        return {"text": None, "intentos": [], "motivo": "sin capítulo siguiente"}
    for _ in range(attempts):
        try:
            raw = call(build_prompt(last3, next3, rejected), system_instruction=SYSTEM,
                       response_schema={"type": "OBJECT", "properties": {"pregunta": {"type": "STRING"}}, "required": ["pregunta"]},
                       thinking_budget=0, description="gfx_question")
            q = clean((raw or {}).get("pregunta", ""))
        except Exception as e:  # noqa: BLE001 — un intento fallido cuenta como rechazo
            tried.append({"pregunta": "", "rechazo": f"error: {type(e).__name__}"})
            continue
        why = validate(q, next3, said_before)
        tried.append({"pregunta": q, "rechazo": why})
        if why is None:
            return {"text": q, "intentos": tried}
        rejected.append((q, why))
    return {"text": None, "intentos": tried, "motivo": "los 3 intentos fallaron el validador"}


def question_for(work_dir: Path, cap: str, chapter_number: int, chapters: list[dict[str, Any]], *,
                 regenerate: bool = False, call: Callable[..., dict] | None = None) -> dict[str, Any]:
    """Pregunta del cap (cache work_dir/gfx_question_<cap>.json). Sin cap siguiente → text None."""
    cache = Path(work_dir) / f"gfx_question_{cap}.json"
    if cache.exists() and not regenerate:
        try:
            return json.loads(cache.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            pass
    by_n = {int(c.get("chapter_number", i + 1)): c for i, c in enumerate(chapters)}
    cur, nxt = by_n.get(chapter_number), by_n.get(chapter_number + 1)
    if cur is None or nxt is None:
        res: dict[str, Any] = {"text": None, "intentos": [], "motivo": "último capítulo: sin pregunta"}
    else:
        said = " ".join(str(by_n[k].get("narration", "")) for k in sorted(by_n) if k <= chapter_number)
        res = generate(str(cur.get("narration", "")), str(nxt.get("narration", "")), said, call=call)
    res.update({"cap": cap, "generated": True, "generado_en": time.strftime("%Y-%m-%d %H:%M:%S")})
    cache.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    return res


def save_edited(work_dir: Path, cap: str, text: str) -> dict[str, Any]:
    """El lab guarda la pregunta editada por Omar (manual: true, sigue fuera del candado literal)."""
    cache = Path(work_dir) / f"gfx_question_{cap}.json"
    try:
        res = json.loads(cache.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        res = {"cap": cap, "intentos": []}
    res.update({"text": clean(text) if text.strip() else None, "generated": True, "manual": bool(text.strip()),
                "editado_en": time.strftime("%Y-%m-%d %H:%M:%S")})
    cache.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    return res
