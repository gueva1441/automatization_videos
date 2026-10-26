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
    # F29b §A.4.3: los bloques del rotulista (`rotulista: true`) traen su propio candado (cita = subcadena del dato;
    # cifra/recorte/persona/lupa = cada número, nombre propio y año en el texto fuente del dato) → excepción explícita
    for c in ok.get("callouts", []) or []:
        if c.get("rotulista") or _check("data_callout", {"text": c.get("text", "")}):
            kept.append(c)
    ok["callouts"] = kept

    ar = ok.get("archive_clipping")
    if ar and not _check("archive_clipping", {k: ar.get(k, "") for k in ("kicker", "headline", "body")}):
        ok["archive_clipping"] = None
    if ok.get("archive_clippings"):          # F2: hasta 2 recortes; cada uno sale entero si falla
        ok["archive_clippings"] = [r for r in ok["archive_clippings"]
                                   if r.get("rotulista") or _check("archive_clipping", {k: r.get(k, "") for k in ("kicker", "headline", "body")})]

    cu = ok.get("count_up")
    if cu and not _check("count_up", {"value_text": cu.get("value_text", ""), "unit": cu.get("unit", "")}):
        ok["count_up"] = None

    # F2 §0d: source_tag literal de sources[]; si falla, se quita SOLO la etiqueta
    for blk in ([c for c in ok.get("callouts", [])] + ([ok["count_up"]] if ok.get("count_up") else [])):
        if blk.get("source") and not _check("source_tag", {"source": blk["source"]}):
            blk["source"] = ""

    # F2b §2: el sello de énfasis muestra la palabra LITERAL de la voz; si falla, sale el énfasis entero
    if ok.get("emphasis"):
        ok["emphasis"] = [e for e in ok["emphasis"] if not e.get("stamp") or _check("keyword_emphasis", {"word": e.get("word", "")})]

    # F3: nivel de agua = cifra + unidad LITERALES del dato; reloj = fecha/hora LITERAL del dato (lo que se muestra
    # se deriva de ese texto: "29 de agosto de 2005" → "29 AGO · 2005")
    wl = ok.get("water_level")
    if wl and not _check("water_level", {"value": f"{wl.get('value_text', '')} {wl.get('unit', '')}".strip()}):
        ok["water_level"] = None
    qc = ok.get("quote_card")                # F5f: la cita entera y su autor, literales del pool
    if qc and not qc.get("rotulista") and not _check("quote_card", {"text": qc.get("text", ""), "author": qc.get("author", "")}):
        ok["quote_card"] = None
    tk = ok.get("time_ticker")
    if tk and not _check("time_ticker", {"source_text": tk.get("source_text", "")}):
        ok["time_ticker"] = None
    if tk and ok.get("time_ticker") and any(not _check("time_ticker", {"hora": h}) for h in tk.get("times") or []):
        ok["time_ticker"] = None
    if tk and ok.get("time_ticker"):            # F5f: cada fecha nueva del reloj sale de un dato literal; si no, no cambia
        ok["time_ticker"]["changes"] = [c for c in tk.get("changes") or []
                                        if _check("time_ticker", {"source_text": c.get("source_text", "")})]

    # F2b §3: la etiqueta del icon_array ('12 de los 300') es fragmento literal del fact
    ia = ok.get("icon_array")
    if ia and not _check("icon_array", {"label": ia.get("label", "")}):
        ok["icon_array"] = None

    # F2 §0d: chapter_question es reformulación (no literal): su candado es "toda palabra de contenido
    # existe en bullets/narración del próximo cap"
    q = ok.get("chapter_question")
    # F3: la pregunta generada por gfx_question (Flash, con su propio validador) NO es texto del guion → excepción
    # explícita al candado, marcada generated: true (igual que la manual que escribe Omar en el lab)
    if q and not q.get("generated"):
        from script_engine.gfx_director import question_ok
        if not question_ok(q.get("text", ""), question_sources or {}):
            rejected.append({"block": "chapter_question", "field": "text", "text": q.get("text", "")})
            ok["chapter_question"] = None

    return ok, rejected


def plan_strings(plan: dict[str, Any]) -> list[str]:
    """Todos los strings en pantalla de un plan resuelto (para auditoría y tests)."""
    out: list[str] = []
    tc = plan.get("title_card")
    if tc:
        out += [tc.get("kicker", ""), tc.get("title", "")]
    out += [c.get("text", "") for c in plan.get("callouts", []) or []]
    for ar in ([plan["archive_clipping"]] if plan.get("archive_clipping") else []) + list(plan.get("archive_clippings") or []):
        out += [ar.get("kicker", ""), ar.get("headline", ""), ar.get("body", "")]
    cu = plan.get("count_up")
    if cu:
        out += [cu.get("value_text", ""), cu.get("unit", "")]
    if plan.get("evidence_zoom"):
        out.append("DETALLE")
    out += [c.get("source", "") for c in plan.get("callouts", []) or []]
    if cu:
        out.append(cu.get("source", ""))
    if plan.get("chapter_question"):
        out.append(plan["chapter_question"].get("text", ""))
    out += [e.get("word", "") for e in plan.get("emphasis", []) or [] if e.get("stamp")]
    if plan.get("icon_array"):
        out.append(plan["icon_array"].get("label", ""))
    if plan.get("quote_card"):
        out += [plan["quote_card"].get("text", ""), plan["quote_card"].get("author", "")]
    return [s for s in out if s]
