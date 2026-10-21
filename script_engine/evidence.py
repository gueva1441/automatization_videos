"""
script_engine/evidence.py — Helpers del evidence_pool (F5) compartidos por m01a, m01b, las métricas del juez y gfx.

    items(pool)            {id: ítem} de datos, cronología, citas, lugares y personajes
    text_of(item)          el texto literal del ítem (texto / evento / cita / nombre)
    anchors(item)          lo que tiene que sonar LITERAL en la narración cuando se usa el ítem: la cifra/fecha/nombre
                           (`valor`), o la fecha del evento, o el autor de la cita, o el nombre del personaje
    format_pool(pool)      el pool numerado para un prompt (ids entre corchetes)
    used_in(text, item)    ¿la narración usa el ítem? (alguno de sus anchors literal)
Todo detrás de `if pool`: un guion sin evidence_pool sigue con verified_facts.
"""
from __future__ import annotations

import re
import unicodedata
from typing import Any

KINDS = ("datos", "cronologia", "citas", "lugares", "personajes")
MESES = ("enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre",
         "noviembre", "diciembre")


def norm(s: str) -> str:
    s = "".join(c for c in unicodedata.normalize("NFD", str(s or "").lower()) if unicodedata.category(c) != "Mn")
    s = s.translate(str.maketrans({"“": '"', "”": '"', "«": '"', "»": '"', "’": "'"}))
    return re.sub(r"\s+", " ", s).strip()


def items(pool: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for k in KINDS:
        for it in (pool or {}).get(k) or []:
            if it.get("id"):
                out[it["id"]] = {**it, "_kind": k}
    return out


def text_of(it: dict[str, Any]) -> str:
    return str(it.get("texto") or it.get("evento") or it.get("nombre") or "")


def spoken_date(iso: str | None) -> str | None:
    """'2005-08-29' → '29 de agosto' (lo que la voz dice); '2006-08' → 'agosto de 2006'; '2010' → '2010'."""
    if not iso:
        return None
    m = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", iso)
    if m:
        return f"{int(m.group(3))} de {MESES[int(m.group(2)) - 1]}"
    m = re.fullmatch(r"(\d{4})-(\d{2})", iso)
    if m:
        return f"{MESES[int(m.group(2)) - 1]} de {m.group(1)}"
    return iso if re.fullmatch(r"\d{4}", iso) else None


def _surname(name: str) -> str:
    ws = [w for w in re.findall(r"[A-Za-zÁÉÍÓÚÑáéíóúñ]+", name) if w[:1].isupper() and len(w) > 2
          and w.lower() not in {"jr", "sr", "sheriff"}]
    return ws[-1] if ws else name


def anchors(it: dict[str, Any]) -> list[str]:
    """Formas literales que prueban que la narración usó el ítem (cualquiera alcanza)."""
    k = it.get("_kind")
    if k == "datos":
        v = it.get("valor")
        out = [v] if v else []
        if it.get("fecha"):
            out.append(spoken_date(it["fecha"]))
        return [x for x in out if x]
    if k == "cronologia":
        return [x for x in (spoken_date(it.get("fecha")),) if x]
    if k == "citas":
        return [it["texto"]]
    if k == "personajes":
        return [_surname(it["nombre"])]
    if k == "lugares":
        return [it["nombre"]]
    return []


def _num_forms(a: str) -> list[str]:
    """6,500 ↔ 6.500 ↔ 6500 (la voz puede escribir la cifra con otro separador)."""
    d = re.sub(r"[.,](?=\d{3}\b)", "", a)
    return list({a, d, re.sub(r"(\d)(?=(\d{3})+\b)", r"\1,", d), re.sub(r"(\d)(?=(\d{3})+\b)", r"\1.", d)})


def literal_in(anchor: str, text: str) -> bool:
    t = norm(text)
    for f in _num_forms(anchor) if re.search(r"\d", anchor) else [anchor]:
        f = norm(f).strip(" .,;:")
        if f and re.search(rf"(?<![\w]){re.escape(f)}(?![\w])", t):
            return True
    return False


def used_in(text: str, it: dict[str, Any]) -> bool:
    return any(literal_in(a, text) for a in anchors(it))


def format_pool(pool: dict[str, Any] | None, ids: list[str] | None = None) -> str:
    """Pool numerado para prompts. Con `ids`, solo esos (en ese orden)."""
    its = items(pool)
    sel = [its[i] for i in ids if i in its] if ids is not None else list(its.values())
    lab = {"datos": "DATO", "cronologia": "CRONO", "citas": "CITA", "lugares": "LUGAR", "personajes": "PERSONA"}
    out = []
    for it in sel:
        k = it["_kind"]
        extra = ""
        if k == "cronologia":
            extra = f" ({it.get('fecha')}{' ' + it['hora'] if it.get('hora') else ''})"
        elif k == "citas":
            extra = f" — {it.get('autor')}"
        elif k == "personajes":
            extra = f" — {it.get('rol') or ''}{' · ANTAGONISTA' if it.get('antagonista') else ''}"
        elif k == "datos" and it.get("valor"):
            extra = f" [valor: {it['valor']}]"
        src = f" · fuente: {it['fuente']}" if it.get("fuente") else ""
        txt = f'"{it["texto"]}"' if k == "citas" else text_of(it)
        out.append(f"  [{it['id']}] {lab[k]}: {txt}{extra}{src}")
    return "\n".join(out) if out else "(sin evidence_pool)"


def antagonists(pool: dict[str, Any] | None) -> list[dict[str, Any]]:
    return [p for p in (pool or {}).get("personajes") or [] if p.get("antagonista")]
