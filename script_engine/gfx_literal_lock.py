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


def lock(plan: dict[str, Any], sources: dict[str, str], *, chapter_number: int
         ) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Filtra un plan RESUELTO. Devuelve (plan_ok, rechazados).

    Cada rechazo: {"block", "field", "text"}. Un callout rechazado sale solo; title_card,
    archive_clipping y count_up salen enteros si cualquiera de sus strings falla.
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

    kept = []
    for c in ok.get("callouts", []) or []:
        if _check("data_callout", {"text": c.get("text", "")}):
            kept.append(c)
    ok["callouts"] = kept

    ar = ok.get("archive_clipping")
    if ar and not _check("archive_clipping", {k: ar.get(k, "") for k in ("kicker", "headline", "body")}):
        ok["archive_clipping"] = None

    cu = ok.get("count_up")
    if cu and not _check("count_up", {"value_text": cu.get("value_text", ""), "unit": cu.get("unit", "")}):
        ok["count_up"] = None

    return ok, rejected


def plan_strings(plan: dict[str, Any]) -> list[str]:
    """Todos los strings en pantalla de un plan resuelto (para auditoría y tests)."""
    out: list[str] = []
    tc = plan.get("title_card")
    if tc:
        out += [tc.get("kicker", ""), tc.get("title", "")]
    out += [c.get("text", "") for c in plan.get("callouts", []) or []]
    ar = plan.get("archive_clipping")
    if ar:
        out += [ar.get("kicker", ""), ar.get("headline", ""), ar.get("body", "")]
    cu = plan.get("count_up")
    if cu:
        out += [cu.get("value_text", ""), cu.get("unit", "")]
    if plan.get("evidence_zoom"):
        out.append("DETALLE")
    return [s for s in out if s]
