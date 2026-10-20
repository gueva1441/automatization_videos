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

F4c R8 (token question_rubric): la pregunta es un GANCHO, no trivia. Flash propone 3; un filtro duro descarta las que
no cumplen (a) nombra algo que el espectador YA conoce (sustantivo de este cap o de los anteriores), (c) ≤ 8 palabras,
(d) sin nombres propios nuevos ni términos administrativos (indemnización, generadores, registros…); y un segundo paso
elige entre las que quedan por (b) consecuencia o culpa no resuelta. Modelo: «¿Quién fue el culpable?». El requisito
viejo «comparte sustantivo con el cap siguiente» (empujaba a la trivia procesal) no aplica en este modo.

La respuesta se cachea en work_dir/gfx_question_chNN.json (el lab la puede regenerar o editar ahí mismo). Una pregunta
manual de Omar nunca se pisa.
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

RUBRIC_VERSION = "f4c-r8"
RUBRIC_MODELS = ("¿Quién fue el culpable?", "¿Qué pasó con los 500 presos?", "¿Por qué nadie abrió las celdas?")
# términos administrativos / procesales: trivia que el espectador no se lleva (raíces sin tildes, 5 letras)
_ADMIN = {"indem", "gener", "regis", "deman", "exped", "trami", "compe", "proce", "respa", "abogad", "juici", "senten",
          "litig", "acuer", "audie", "infor", "estad", "admin", "buroc", "contr", "fallo"}
_HOOK_ROOTS = {"culpa", "respo", "verda", "secre"}     # palabras del gancho mismo (culpa/responsable/verdad/secreto)

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


def proper_names(text: str) -> set[str]:
    """Palabras con mayúscula que no abren la oración (sin el ¿ inicial), en minúscula."""
    ws = re.findall(r"[A-Za-zÁÉÍÓÚÑáéíóúñü]+", str(text))
    return {w.lower() for k, w in enumerate(ws) if k > 0 and w[:1].isupper()}


def validate_rubric(q: str, said_before: str) -> str | None:
    """F4c R8 filtro duro: None si la pregunta puede ser gancho; si no, el motivo."""
    body = clean(q)[1:-1].strip()
    low = body.lower()
    first = re.findall(r"[a-záéíóúñü]+", low)[:1]
    if not first:
        return "vacía"
    if first[0] in YESNO_STARTS or not any(low.startswith(s) for s in OPEN_STARTS):
        return f"no es abierta («{first[0]}»)"
    n = len(body.split())
    if n > MAX_WORDS:
        return f"{n} palabras (máx {MAX_WORDS})"
    abst = abstract_words(body)
    if abst:
        return f"abstracta ({', '.join(abst)})"
    adm = [w for w in re.findall(r"[a-záéíóúñü]+", low) if _strip_accents(w)[:5] in _ADMIN]
    if adm:
        return f"término administrativo ({', '.join(adm)})"
    new = proper_names(body) - {w.lower() for w in re.findall(r"[A-Za-zÁÉÍÓÚÑáéíóúñü]+", said_before)}
    if new:
        return f"nombre propio nuevo ({', '.join(sorted(new))})"
    own = nouns(body) - _HOOK_ROOTS                       # «culpable», «responsable»: el gancho, no un tema nuevo
    if own and not own & nouns(said_before):
        return "no nombra nada que el espectador ya conozca"
    return None


def build_rubric_prompt(last3: list[str], next_first3: list[str], rejected: list[tuple[str, str]]) -> str:
    rej = "".join(f"\n- «{q}» → rechazada: {why}" for q, why in rejected)
    return (
        "FINAL DEL CAPÍTULO ACTUAL (últimas 3 frases):\n" + "\n".join(f"- {s}" for s in last3) +
        "\n\nLO QUE VIENE (primeras 3 frases del capítulo siguiente; el espectador todavía NO las escuchó):\n" +
        "\n".join(f"- {s}" for s in next_first3) +
        "\n\nEscribí TRES preguntas de cierre distintas, en español rioplatense neutro. Cada una es un GANCHO, no trivia:\n"
        "(a) nombra algo que el espectador YA conoce (una persona, grupo o lugar de lo que ya escuchó);\n"
        "(b) implica una consecuencia o una culpa sin resolver;\n"
        f"(c) máximo {MAX_WORDS} palabras, abierta (¿Qué / ¿Cómo / ¿Por qué / ¿Quién / ¿Cuánto / ¿Dónde);\n"
        "(d) sin nombres propios nuevos ni términos administrativos (indemnización, generadores, registros, demanda).\n"
        "ASÍ SON (el tono, no el contenido): " + " · ".join(RUBRIC_MODELS) + "\n"
        + (f"\nIntentos anteriores que NO sirvieron:{rej}\n" if rej else "") +
        '\nDevolvé {"preguntas": ["¿…?", "¿…?", "¿…?"]}'
    )


def generate_rubric(narr_cap: str, narr_next: str, said_before: str, *,
                    call: Callable[..., dict] | None = None, attempts: int = ATTEMPTS) -> dict[str, Any]:
    """F4c R8: {"text", "intentos": [{"pregunta", "rechazo"}…], "eleccion"}. `call` = call_flash_json (inyectable)."""
    if call is None:
        from gemini_helpers import call_flash_json as call
    last3, next3 = sentences(narr_cap)[-3:], sentences(narr_next)[:3]
    if not last3 or not next3:
        return {"text": None, "intentos": [], "motivo": "sin capítulo siguiente", "v": RUBRIC_VERSION}
    tried: list[dict[str, Any]] = []
    rejected: list[tuple[str, str]] = []
    for _ in range(attempts):
        try:
            raw = call(build_rubric_prompt(last3, next3, rejected), system_instruction=SYSTEM,
                       response_schema={"type": "OBJECT", "properties": {"preguntas": {"type": "ARRAY", "items": {"type": "STRING"}}},
                                        "required": ["preguntas"]}, thinking_budget=0, description="gfx_question rubrica")
            qs = [clean(x) for x in (raw or {}).get("preguntas") or [] if str(x).strip()][:3]
        except Exception as e:  # noqa: BLE001
            tried.append({"pregunta": "", "rechazo": f"error: {type(e).__name__}"})
            continue
        ok = []
        for q in qs:
            why = validate_rubric(q, said_before)
            tried.append({"pregunta": q, "rechazo": why})
            (ok.append(q) if why is None else rejected.append((q, why)))
        if not ok:
            continue
        pick = 1
        if len(ok) > 1:                                   # segundo paso: la que más engancha por (b)
            try:
                r2 = call("Elegí la pregunta de cierre que más engancha: la que implica una consecuencia o una culpa sin "
                          "resolver sobre algo que el espectador ya conoce. Respondé solo el número.\n"
                          + "\n".join(f"{k}. {q}" for k, q in enumerate(ok, start=1)) + '\nDevolvé {"n": número}',
                          system_instruction=SYSTEM, response_schema={"type": "OBJECT", "properties": {"n": {"type": "INTEGER"}},
                                                                      "required": ["n"]},
                          thinking_budget=0, description="gfx_question eleccion")
                n = (r2 or {}).get("n")
                pick = n if isinstance(n, int) and 1 <= n <= len(ok) else 1
            except Exception:  # noqa: BLE001 — sin juez → la primera que pasó el filtro
                pick = 1
        return {"text": ok[pick - 1], "intentos": tried, "eleccion": {"opciones": ok, "n": pick}, "v": RUBRIC_VERSION}
    return {"text": None, "intentos": tried, "motivo": "ninguna pasó la rúbrica", "v": RUBRIC_VERSION}


def _rubric_on() -> bool:
    try:
        from gfx_config import gfx_rules
        return bool(gfx_rules.question_rubric)
    except Exception:  # noqa: BLE001
        return False


def question_for(work_dir: Path, cap: str, chapter_number: int, chapters: list[dict[str, Any]], *,
                 regenerate: bool = False, call: Callable[..., dict] | None = None) -> dict[str, Any]:
    """Pregunta del cap (cache work_dir/gfx_question_<cap>.json). Sin cap siguiente → text None."""
    cache = Path(work_dir) / f"gfx_question_{cap}.json"
    rubric = _rubric_on()
    if cache.exists() and not regenerate:
        try:
            old = json.loads(cache.read_text(encoding="utf-8"))
            # F4c R8: con rúbrica, una pregunta automática vieja se regenera; la manual de Omar nunca
            if not rubric or old.get("manual") or old.get("v") == RUBRIC_VERSION:
                return old
        except (OSError, ValueError):
            pass
    by_n = {int(c.get("chapter_number", i + 1)): c for i, c in enumerate(chapters)}
    cur, nxt = by_n.get(chapter_number), by_n.get(chapter_number + 1)
    if cur is None or nxt is None:
        res: dict[str, Any] = {"text": None, "intentos": [], "motivo": "último capítulo: sin pregunta"}
    else:
        said = " ".join(str(by_n[k].get("narration", "")) for k in sorted(by_n) if k <= chapter_number)
        gen = generate_rubric if rubric else generate
        res = gen(str(cur.get("narration", "")), str(nxt.get("narration", "")), said, call=call)
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
