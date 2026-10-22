"""
script_engine/guion_v3_reglas.py — F7c-2: reglas DURAS nuevas del guion v3 (validación del analista sobre F7c, confirmada
por Omar). Las llama `m01b_guionista.review` (y por lo tanto el editor, que re-revisa cada párrafo).

    citas       una cita literal por párrafo como máximo (texto entre comillas de más de 3 palabras)
    gancho      el cap 1 es un flash-forward sensorial: no describe fotos ni da fechas de fotos y no adelanta citas de
                caps siguientes
    juicios     ninguna frase de interpretación o juicio que no esté en el pool («caos deliberado», «no eran
                considerados humanos»): solo hechos, citas y preguntas
    nombre      el nombre COMPLETO del humano, como mucho una vez por cap; después, el apellido
    repetición  una frase de ≥ 3 palabras de contenido que ya se dijo en un cap anterior

Cada función devuelve la lista de problemas (vacía = pasa). Sin LLM.
"""
from __future__ import annotations

import re
from typing import Any

from script_engine import evidence as ev

_QUOTED = re.compile(r"[\"“«]([^\"”»]{3,}?)[\"”»]")
MAX_QUOTES_PER_PARAGRAPH = 1


def quotes_in(text: str) -> list[str]:
    """Citas literales de un texto: lo que va entre comillas con más de 3 palabras (un nombre corto no es una cita)."""
    return [m.group(1).strip() for m in _QUOTED.finditer(text or "") if len(m.group(1).split()) > 3]


def quotes_per_paragraph(parrafos: list[dict]) -> list[str]:
    out = []
    for k, p in enumerate(parrafos):
        qs = quotes_in(p.get("texto") or "")
        if len(qs) > MAX_QUOTES_PER_PARAGRAPH:
            out.append(f"beat {p.get('beat')} (párrafo {k + 1}): {len(qs)} citas literales; una por párrafo como máximo "
                       f"(el resto, con tus palabras): {['«' + q[:40] + '…»' for q in qs]}")
    return out


# ── gancho ────────────────────────────────────────────────────────────────────

_PHOTO = re.compile(r"\b(fotos?|fotograf\w*|fot[oó]graf[oa]s?|im[aá]gen(?:es)? de|c[aá]maras?|retrat\w+|instant[aá]nea)\b",
                    re.I)
_DATE = re.compile(r"\b(\d{1,2} de (?:enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|setiembre|octubre|"
                   r"noviembre|diciembre)|(?:19|20)\d\d)\b", re.I)


def hook_problems(cap1: str, later_quotes: list[str]) -> list[str]:
    """El gancho (cap 1) es la escena del peor momento, contada: sin fotos ni fechas de fotos, sin citas de después.
    `later_quotes`: textos (o fragmentos) de las citas que la escaleta pone en caps 2–7."""
    out = []
    ph = _PHOTO.findall(cap1 or "")
    if ph:
        out.append(f"gancho: describe una foto ({', '.join(sorted(set(x.lower() for x in ph)))}): contá la escena, no la "
                   "imagen")
    dates = _DATE.findall(cap1 or "")
    if dates:
        out.append(f"gancho: sin fechas en el flash-forward ({', '.join(dates)}); la fecha llega en el cap 2")
    n1 = ev.norm(cap1 or "")
    for q in later_quotes:
        ws = ev.norm(q).split()
        if len(ws) >= 4 and any(" ".join(ws[k:k + 4]) in n1 for k in range(len(ws) - 3)):
            out.append(f"gancho: adelanta una cita de un cap siguiente («{q[:50]}…»): que suene recién en su cap")
    return out


# ── juicios fuera del pool ────────────────────────────────────────────────────

# interpretación o juicio del narrador; cada patrón vale si su raíz (2.º elemento) ya está en el pool (lo dice un
# documento) y es dura si no
JUDGMENTS: list[tuple[str, str]] = [
    (r"\bdeliberad[oa]s?\b|\bdeliberadamente\b", "deliberad"),
    (r"\ba prop[oó]sito\b|\bintencional(?:mente)?\b", "a proposito"),
    (r"\bno (?:eran|fueron|los consideraban?) (?:considerados |tratados como )?(?:seres )?humanos\b", "humanos"),
    (r"\bdeshumaniz\w*|\binhuman\w*", "humaniz"),
    (r"\b(?:colapso|derrumbe) (?:moral|de la humanidad|de la humanidad b[aá]sica)\b|\bhumanidad b[aá]sica\b",
     "humanidad"),
    (r"\bcastig\w*", "castig"),
    (r"\bcrueldad\b|\bcrueles?\b|\bs[aá]dic\w*", "cruel"),
    (r"\bvenganza\b|\bdesprecio\b|\bindiferencia\b", "indiferencia"),
    (r"\bcomo (?:si fueran )?animales\b", "animales"),
    (r"\bnadie (?:les|le) importaba\b|\bno les importaba\b|\bno les import[oó]\b", "importaba"),
    (r"\bsab[ií]an (?:lo que|que)\b", "sabian"),
    (r"\bel sistema (?:los|las|la|lo) (?:abandon[oó]|olvid[oó]|trag[oó])\b", "el sistema"),
    (r"\bcaos (?:deliberado|calculado|organizado)\b", "caos"),
    (r"\bmonstruos[oa]s?\b|\bdiab[oó]lic\w*|\binfiern\w*", "infiern"),
]


def _pool_blob(pool: dict[str, Any]) -> str:
    return ev.norm(" ".join(ev.text_of(it) for it in ev.items(pool).values()))


def judgment_problems(text: str, pool: dict[str, Any]) -> list[str]:
    """Frases de interpretación o juicio del narrador cuya idea no está en ningún ítem del pool."""
    blob = _pool_blob(pool)
    out = []
    for pat, root in JUDGMENTS:
        for m in re.finditer(pat, text or "", re.I):
            if ev.norm(root) in blob:
                continue
            a, b = max(0, m.start() - 30), min(len(text), m.end() + 30)
            out.append(f"juicio que no está en el pool: «…{text[a:b].strip()}…»: contá el hecho, la cita o una pregunta")
    return list(dict.fromkeys(out))


# ── nombre completo del humano ────────────────────────────────────────────────

def full_name_problems(caps: list[dict], nombre: str | None) -> list[str]:
    """El nombre completo del humano (nombre + apellido, con o sin segundo nombre/apodo) más de una vez en un cap."""
    if not nombre:
        return []
    ws = [w for w in re.findall(r"[A-Za-zÁÉÍÓÚÑáéíóúñ]+", nombre) if w[:1].isupper()]
    if len(ws) < 2:
        return []
    first, last = ev.norm(ws[0]), ev.norm(ws[-1])
    pat = re.compile(rf"\b{re.escape(first)}\b(?:\s+\S+){{0,2}}?\s+{re.escape(last)}\b")
    out = []
    for c in caps:
        n = len(pat.findall(ev.norm(c.get("narration") or "")))
        if n > 1:
            out.append(f"cap {c['chapter_number']}: el nombre completo de {nombre} suena {n} veces; una vez por cap, "
                       "después solo el apellido")
    return out


# ── repetición entre caps ─────────────────────────────────────────────────────

_STOP = set("""a al algo algun alguna algunos ante antes aqui asi aun aunque bajo cada como con contra cual cuando de del
desde donde dos durante e el ella ellas ellos en entre era eran es esa esas ese eso esos esta estaba estaban estas este
esto estos fue fueron ha habia habian hacia han hasta hay la las le les lo los mas me mientras muy nada ni no nos o otra
otro otros para pero poco por porque que quien se sea segun ser si sin sobre solo su sus tambien tan tanto te tenia
tenian todo todos tras tu un una uno unos y ya""".split())


def _tokens(text: str) -> list[str]:
    return re.findall(r"[a-z0-9ñ]+", ev.norm(text))


def _entity_tokens(pool: dict[str, Any], texts: list[str]) -> set[str]:
    """Palabras de nombres propios: personas y lugares del pool, y las palabras con mayúscula en medio de una frase."""
    out: set[str] = set()
    for k in ("personajes", "lugares"):
        for it in pool.get(k) or []:
            out |= set(_tokens(it.get("nombre") or ""))
    for t in texts:
        out |= {ev.norm(m) for m in re.findall(r"(?<=[a-záéíóúñ,;] )[A-ZÁÉÍÓÚÑ][\wáéíóúñ]+", t or "")}
    return out


def repetition_problems(caps: list[dict], pool: dict[str, Any]) -> list[str]:
    """Frases de ≥ 3 palabras que se repiten entre caps: trigramas con ≥ 2 palabras de contenido (≥ 4 letras, no
    gramaticales) y sin nombres propios ni cifras (un nombre o una cifra repetida la controla otra regla)."""
    ent = _entity_tokens(pool, [c.get("narration") or "" for c in caps])
    seen: dict[tuple[str, ...], int] = {}
    out = []
    for c in caps:
        n = c["chapter_number"]
        toks = _tokens(c.get("narration") or "")
        here = set()
        for k in range(len(toks) - 2):
            tri = tuple(toks[k:k + 3])
            if any(t in ent or t.isdigit() for t in tri):
                continue
            if sum(1 for t in tri if len(t) >= 4 and t not in _STOP) < 2:
                continue
            here.add(tri)
        rep = sorted({" ".join(t) for t in here if t in seen and seen[t] != n})
        if rep:
            out.append(f"cap {n}: repite frases de caps anteriores ({'; '.join('«' + r + '»' for r in rep[:4])}"
                       + (f" y {len(rep) - 4} más" if len(rep) > 4 else "") + "): decilo de otra forma o no lo repitas")
        for t in here:
            seen.setdefault(t, n)
    return out


def review_v3(caps: list[dict], parrafos: list[dict], pool: dict[str, Any], esc: dict) -> list[str]:
    """Las cinco reglas juntas (lo que suma m01b_guionista.review a sus duras)."""
    its = ev.items(pool)
    later = []
    for b in esc.get("beats") or []:
        if b.get("cap", 1) >= 2:
            for i in [b.get("dato_central")] + list(b.get("datos_apoyo") or []):
                it = its.get(i)
                if it and it["_kind"] == "citas":
                    later.append(it.get("fragmento") or it["texto"])
    out = quotes_per_paragraph(parrafos)
    if caps and caps[0].get("chapter_number") == 1:
        out += hook_problems(caps[0].get("narration") or "", later)
    for c in caps:
        out += [f"cap {c['chapter_number']}: {x}" for x in judgment_problems(c.get("narration") or "", pool)]
    out += full_name_problems(caps, (esc.get("humano") or {}).get("nombre"))
    out += repetition_problems(caps, pool)
    return out
