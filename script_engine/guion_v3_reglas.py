"""
script_engine/guion_v3_reglas.py — F7c-2: reglas DURAS nuevas del guion v3 (validación del analista sobre F7c, confirmada
por Omar). Las llama `m01b_guionista.review` (y por lo tanto el editor, que re-revisa cada párrafo).

    citas       una cita literal por párrafo como máximo (texto entre comillas de más de 3 palabras)
F7c-3 (HANDOFF_F7 §9.1, reglas de oficio): rol de quien habla = su rol en el pool; párrafo sin id = relleno (salvo
transición de ≤ 2 frases); el antagonista con nombre si un dato verificado lo nombra (nunca «según alguien»); sin fotos
en ningún cap; sin voz de tráiler; ancla de lugar y fecha en el gancho; y, blanda para el editor, sin eco después de
una cita.
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

_DATE = re.compile(r"\b(\d{1,2} de (?:enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|setiembre|octubre|"
                   r"noviembre|diciembre)|(?:19|20)\d\d)\b", re.I)


def hook_problems(cap1: str, later_quotes: list[str], pool: dict[str, Any] | None = None) -> list[str]:
    """El gancho (cap 1) es la escena del peor momento, contada: sin fechas (salvo el ancla de lugar y fecha, F7c-3) y
    sin citas de después. `later_quotes`: textos (o fragmentos) de las citas que la escaleta pone en caps 2–7. Las fotos
    se controlan en todos los caps (`photo_problems`)."""
    out = []
    keep = set(anchor_sentences(cap1, pool)) if pool is not None else set()
    rest = " ".join(s for s in sentences_of(cap1) if s not in keep) if keep else (cap1 or "")
    dates = _DATE.findall(rest)
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


def review_v3(caps: list[dict], parrafos: list[dict], pool: dict[str, Any], esc: dict) -> tuple[list[str], list[str]]:
    """Todas las reglas juntas: (duras, blandas) que suma m01b_guionista.review."""
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
        out += hook_problems(caps[0].get("narration") or "", later, pool)
        out += hook_anchor_problems(caps[0].get("narration") or "", pool)               # F7c-3 §6
    for c in caps:
        t = c.get("narration") or ""
        out += [f"cap {c['chapter_number']}: {x}" for x in judgment_problems(t, pool)]
        out += [f"cap {c['chapter_number']}: {x}" for x in role_problems(t, pool)]     # F7c-3 §1
        out += [f"cap {c['chapter_number']}: {x}" for x in trailer_problems(t)]        # F7c-3 §5
    out += full_name_problems(caps, (esc.get("humano") or {}).get("nombre"))
    out += repetition_problems(caps, pool)
    out += empty_paragraph_problems(parrafos)                                           # F7c-3 §2
    out += antagonist_problems(caps, esc, pool)                                         # F7c-3 §3
    out += photo_problems(caps)                                                         # F7c-3 §4
    return out, echo_soft(parrafos)                                                     # F7c-3 §7 (blanda)


# ═══════════════════════════════════════════════════════════════
#  F7c-3 (HANDOFF_F7 §9.1) — reglas de oficio
# ═══════════════════════════════════════════════════════════════

_SENT = re.compile(r"(?<=[.!?…»”])\s+(?=[«“\"¿¡A-ZÁÉÍÓÚÑ])")


def sentences_of(text: str) -> list[str]:
    return [s.strip() for s in _SENT.split(text or "") if s.strip()]


# ── 1. rol de quien habla ─────────────────────────────────────────────────────

_ROLE_PRESO = re.compile(r"\b(reclus[oa]s?|pres[oa]s?|prisioner[oa]s?|intern[oa]s?|detenid[oa]s?|condenad[oa]s?|"
                         r"inmates?|prisoners?|sobrevivientes?)\b", re.I)
_ROLE_GUARDIA = re.compile(r"\b(guardias?|oficial(?:es)?|alguacil(?:es)?|ayudantes?|carceler[oa]s?|celador(?:es|as)?|"
                           r"sargentos?|sgt|capit[aá]n|teniente|deput(?:y|ies)|vigilantes?|custodios?)\b", re.I)


def role_class(text: str | None) -> str | None:
    """«preso» o «guardia» según el rol escrito (pool o narración); None si no es ninguno (abogada, alcalde)."""
    t = str(text or "")
    g, p = _ROLE_GUARDIA.search(t), _ROLE_PRESO.search(t)
    if g and p:                                     # «oficial que custodiaba presos»: manda la primera palabra de rol
        return "guardia" if g.start() < p.start() else "preso"
    return "guardia" if g else "preso" if p else None


_ROLE_BEFORE = re.compile(r"\b(?:el|la|los|las|un|una)\s+((?:\w+\s+){0,1}?(?:" + _ROLE_PRESO.pattern[3:-3] + "|"
                          + _ROLE_GUARDIA.pattern[3:-3] + r"))(?:\s+del?\s+\w+)?\s*$", re.I)


def role_problems(text: str, pool: dict[str, Any]) -> list[str]:
    """El rol con que la narración presenta a quien habla tiene que ser su rol en el pool (preso / guardia):
    «la reclusa Rhonda Ducre» (es guardia), «un guardia lo describió: «…»» (la cita es de un preso)."""
    out = []
    people = pool.get("personajes") or []
    for p in people:
        want = role_class(p.get("rol"))
        if not want:
            continue
        from researcher_steps.research_v3 import name_terms
        terms = name_terms(p, people)
        low = ev.norm(text)
        for t in terms:
            for m in re.finditer(rf"\b{re.escape(t)}\b", low):
                before = low[max(0, m.start() - 45):m.start()]
                rm = _ROLE_BEFORE.search(before)
                got = role_class(rm.group(1)) if rm else None
                if got and got != want:
                    out.append(f"«{rm.group(0).strip()} {p['nombre']}»: en el pool es {p.get('rol')} ({want})")
    # citas anónimas presentadas con un rol
    cits = pool.get("citas") or []
    for s in sentences_of(text):
        for q in quotes_in(s):
            nq = ev.norm(q)
            src = next((c for c in cits if nq and (nq in ev.norm(c.get("texto") or "")
                                                   or nq in ev.norm(c.get("fragmento") or ""))), None)
            if not src:
                continue
            per = next((x for x in people if (src.get("autor") or "") and ev.norm(x["nombre"]).split()[-1:]
                        == ev.norm(src.get("autor") or "").split()[-1:]), None)
            want = role_class(src.get("rol")) or role_class(src.get("autor")) or role_class((per or {}).get("rol"))
            intro = s.split("«")[0].split("“")[0]
            got = role_class(intro)
            if want and got and got != want and not any(ev.norm(w) in ev.norm(intro) for w in
                                                         (src.get("autor") or "").split()[-1:]):
                out.append(f"«{intro.strip()[:60]}» presenta la cita {src['id']} con otro rol: en el pool es de "
                           f"{src.get('autor')} ({src.get('rol') or want})")
    return list(dict.fromkeys(out))


# ── 2. párrafo sin id = relleno ───────────────────────────────────────────────

MAX_TRANSITION_SENTENCES = 2


def empty_paragraph_problems(parrafos: list[dict]) -> list[str]:
    """Todo párrafo lleva ≥ 1 id del pool o es una transición de ≤ 2 frases."""
    out = []
    for k, p in enumerate(parrafos):
        if p.get("ids_usados"):
            continue
        n = len(sentences_of(p.get("texto") or ""))
        if n > MAX_TRANSITION_SENTENCES:
            out.append(f"beat {p.get('beat')} (párrafo {k + 1}): {n} frases sin ningún dato del pool: es relleno "
                       f"(un párrafo lleva al menos un id, o es una transición de ≤ {MAX_TRANSITION_SENTENCES} frases)")
    return out


# ── 3. el antagonista con nombre ──────────────────────────────────────────────

_ANON_VOICE = re.compile(r"\bseg[uú]n alguien\b|\balguien (?:dijo|orden[oó]|decidi[oó]|declar[oó])\b|"
                         r"\buna voz oficial\b|\bseg[uú]n algunos\b", re.I)


def antagonist_problems(caps: list[dict], esc: dict, pool: dict[str, Any]) -> list[str]:
    """Si un cap usa un dato VERIFICADO que nombra al antagonista (la decisión del sheriff), la voz dice su apellido
    (aunque su cita sea verificada_parcial). Nunca «según alguien» ni «una voz oficial»."""
    out = []
    for c in caps:
        for m in _ANON_VOICE.finditer(c.get("narration") or ""):
            out.append(f"cap {c['chapter_number']}: «{m.group(0)}»: decí quién (el nombre está en los datos)")
    aid = (esc.get("antagonista") or {}).get("id")
    ant = next((p for p in pool.get("personajes") or [] if p["id"] == aid), None)
    if not ant:
        return out
    sur = ev.norm(ant["nombre"]).split()[-1]
    its = ev.items(pool)
    for c in caps:
        n = c["chapter_number"]
        ids = [i for b in esc.get("beats") or [] if b.get("cap") == n for i in [b["dato_central"]] + b["datos_apoyo"]]
        named = [i for i in ids if i in its and its[i]["_kind"] in ("datos", "cronologia")
                 and re.search(rf"\b{re.escape(sur)}\b", ev.norm(ev.text_of(its[i])))
                 and (its[i].get("verificacion") or {}).get("estado", "verificada") == "verificada"]
        if named and not re.search(rf"\b{re.escape(sur)}\b", ev.norm(c.get("narration") or "")):
            out.append(f"cap {n}: el antagonista ({ant['nombre']}) no se nombra, y {', '.join(named)} lo nombra como "
                       "hecho verificado: decí su nombre")
    return out


# ── 4. sin fotos en ningún cap ────────────────────────────────────────────────

_PHOTO_ANY = re.compile(r"\b(fotos?|fotograf\w*|fot[oó]graf[oa]s?|im[aá]gen(?:es)?|c[aá]maras?|retrat\w+|"
                        r"instant[aá]neas?)\b", re.I)


def photo_problems(caps: list[dict]) -> list[str]:
    out = []
    for c in caps:
        ph = _PHOTO_ANY.findall(c.get("narration") or "")
        if ph:
            out.append(f"cap {c['chapter_number']}: describe fotos o imágenes ({', '.join(sorted(set(x.lower() for x in ph)))}):"
                       " contá la escena, no la foto")
    return out


# ── 5. sin voz de tráiler ─────────────────────────────────────────────────────

TRAILER = [r"\b(?:esta|esa|[eé]sta) es la historia de\b", r"\bes la historia de\b", r"\blo que sigue\b",
           r"\ben este (?:video|documental|cap[ií]tulo)\b", r"\bte vamos a contar\b", r"\bvamos a (?:ver|contar)\b",
           r"\bacomp[aá][ñn]a(?:nos|me)\b", r"\bqu[eé]date\b", r"\blo que vas a (?:ver|escuchar)\b",
           r"\bse negaron a olvidar\b", r"\bdescubriremos\b", r"\besta historia\b", r"\bnuestra historia\b",
           r"\bhistoria que (?:nadie|pocos) (?:cuenta|conoce)\b"]


def trailer_problems(text: str) -> list[str]:
    return [f"voz de tráiler (el narrador habla del video): «{m.group(0)}»"
            for pat in TRAILER for m in re.finditer(pat, text or "", re.I)]


# ── 6. ancla de lugar y fecha en el gancho ────────────────────────────────────

ANCHOR_MAX_WORDS = 10
_YEAR = re.compile(r"\b(?:19|20)\d\d\b")


def _place_tokens(pool: dict[str, Any]) -> set[str]:
    return {w for lg in pool.get("lugares") or [] for w in ev.norm(lg.get("nombre") or "").split() if len(w) >= 5}


def anchor_sentences(cap1: str, pool: dict[str, Any]) -> list[str]:
    """Frases cortas (≤ ANCHOR_MAX_WORDS palabras) con un año y un lugar del pool: «Nueva Orleans, agosto de 2005»."""
    places = _place_tokens(pool)
    return [s for s in sentences_of(cap1) if len(s.split()) <= ANCHOR_MAX_WORDS and _YEAR.search(s)
            and set(ev.norm(s).split()) & places]


def hook_anchor_problems(cap1: str, pool: dict[str, Any]) -> list[str]:
    """El gancho lleva una frase corta con ciudad + año antes de la segunda cita."""
    anchors = anchor_sentences(cap1, pool)
    if not anchors:
        return ["gancho: falta el ancla de lugar y fecha (una frase corta con la ciudad y el año: «Nueva Orleans, agosto "
                "de 2005.») antes de la segunda cita"]
    qpos = [m.start() for m in _QUOTED.finditer(cap1 or "") if len(m.group(1).split()) > 3]
    if len(qpos) >= 2 and (cap1 or "").find(anchors[0]) > qpos[1]:
        return ["gancho: el ancla de lugar y fecha va antes de la segunda cita"]
    return []


# ── 7. cita fuerte, silencio después (blanda, para el editor) ─────────────────

ECHO_MAX_WORDS = 6


def echo_soft(parrafos: list[dict]) -> list[str]:
    """Una frase corta de eco justo después de una cita («Era la única opción.»): cortala (blanda; la ve el editor)."""
    out = []
    for k, p in enumerate(parrafos):
        ss = sentences_of(p.get("texto") or "")
        for a, b in zip(ss, ss[1:]):
            if re.search(r"[»”\"]\s*[.!?…]?\s*$", a) and len(b.split()) <= ECHO_MAX_WORDS and not re.search(r"\d", b) \
                    and "«" not in b and not b.startswith("¿"):
                out.append(f"párrafo {k}: eco después de la cita: «{b}»: cortalo, que la cita quede sola")
    return out
