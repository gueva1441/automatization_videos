"""
gfx_literal_lock.py — Candado literal de la capa gráfica (D7).

Todo string que aparece en pantalla debe existir LITERAL en las fuentes del cap:
verified_facts, narración del cap, título/bullets del skeleton, canonical. El cromo
declarado ("CAPÍTULO N", "DETALLE") queda fuera. Normalización idéntica al
lab/hyperframes/lab_cap/tools/check_literal.py: minúsculas + espacios colapsados
(NO quita tildes ni puntuación).

Rechazo = el bloque se QUITA del plan y se reporta; nunca se reescribe el texto.
"""
from __future__ import annotations

import copy
import re
from typing import Any

from gfx_config import chrome_strings


def normalize(text: str) -> str:
    """Minúsculas + espacios colapsados (igual que el candado del lab)."""
    return re.sub(r"\s+", " ", str(text)).strip().lower()


def find_source(text: str, sources: dict[str, str]) -> str | None:
    """Nombre de la fuente que contiene `text` literal (normalizado), o None."""
    needle = normalize(text)
    if not needle:
        return None
    for name, body in sources.items():
        if needle in normalize(body):
            return name
    return None


def is_literal(text: str, sources: dict[str, str], chapter_number: int) -> bool:
    """True si es cromo declarado o está literal en alguna fuente."""
    if text in chrome_strings(chapter_number):
        return True
    return find_source(text, sources) is not None


def lock(plan: dict[str, Any], sources: dict[str, str], *, chapter_number: int,
         question_sources: dict[str, str] | None = None) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Filtra un plan RESUELTO. Devuelve (plan_ok, rechazados).

    Cada rechazo: {"block", "field", "text"}. Un callout rechazado sale solo; title_card y archive_clipping salen
    enteros si cualquiera de sus strings falla. F37 §B.4: sin las ramas de los bloques borrados (contador, agua, matriz
    de figuras, etiqueta de fuente, sello por léxico) ni la de la pregunta reformulada por el director: la pregunta es
    el `cierre` de la escaleta (generada: excepción explícita) y los sellos son de clima (no repiten la voz: no son
    literales a propósito; corren después del candado). `question_sources` queda por compatibilidad del lab.
    """
    ok = copy.deepcopy(plan)
    rejected: list[dict[str, Any]] = []

    def _check(block: str, fields: dict[str, str]) -> bool:
        good = True
        for field, text in fields.items():
            if text and not is_literal(text, sources, chapter_number):
                rejected.append({"block": block, "field": field, "text": text})
                good = False
        return good

    tc = ok.get("title_card")
    if tc and not _check("title_card", {"title": tc.get("title", ""), "kicker": tc.get("kicker", "")}):
        ok["title_card"] = None

    # F29b §A.4.3: los bloques del papel (`rotulista: true`) traen su propio candado (cita = subcadena del dato;
    # ficha/recorte/persona = cada número, nombre propio y año en el texto fuente del dato) → excepción explícita
    ok["callouts"] = [c for c in ok.get("callouts", []) or []
                      if c.get("rotulista") or _check("data_callout", {"text": c.get("text", "")})]
    if ok.get("archive_clippings"):          # cada recorte sale entero si falla
        ok["archive_clippings"] = [r for r in ok["archive_clippings"]
                                   if r.get("rotulista") or _check("archive_clipping", {k: r.get(k, "") for k in ("kicker", "headline", "body")})]

    # F3: reloj = fecha/hora LITERAL del dato (lo que se muestra se deriva de ese texto: "29 de agosto de 2005" →
    # "29 AGO · 2005")
    tk = ok.get("time_ticker")
    if tk and not _check("time_ticker", {"source_text": tk.get("source_text", "")}):
        ok["time_ticker"] = None
    if tk and ok.get("time_ticker") and any(not _check("time_ticker", {"hora": h}) for h in tk.get("times") or []):
        ok["time_ticker"] = None
    if tk and ok.get("time_ticker"):            # F5f: cada fecha nueva del reloj sale de un dato literal; si no, no cambia
        ok["time_ticker"]["changes"] = [c for c in tk.get("changes") or []
                                        if _check("time_ticker", {"source_text": c.get("source_text", "")})]
    return ok, rejected


def plan_strings(plan: dict[str, Any]) -> list[str]:
    """Todos los strings en pantalla de un plan resuelto (para auditoría y tests)."""
    out: list[str] = []
    tc = plan.get("title_card")
    if tc:
        out += [tc.get("kicker", ""), tc.get("title", "")]
    out += [c.get("text", "") for c in plan.get("callouts", []) or []]
    for ar in plan.get("archive_clippings") or []:
        out += [ar.get("kicker", ""), ar.get("headline", ""), ar.get("body", "")]
    if plan.get("chapter_question"):
        out.append(plan["chapter_question"].get("text", ""))
    out += [e.get("word", "") for e in plan.get("emphasis", []) or [] if e.get("stamp")]
    return [s for s in out if s]
