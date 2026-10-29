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
                   r"noviembre|diciembre)|(?:1[0-9]{3}|20\d\d))\b", re.I)


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
    # F21: solo los estructurales (intención atribuida); los patrones de Orleans/Ycuá («como animales», «el sistema
    # los abandonó», «fue una masacre», «esperar un milagro», «castig…»…) se borraron
    (r"\bdeliberad[oa]s?\b|\bdeliberadamente\b", "deliberad"),
    (r"\ba prop[oó]sito\b|\bintencional(?:mente)?\b", "a proposito"),
    (r"\bsab[ií]an (?:lo que|que)\b", "sabian"),
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
    out += date_problems(caps)                                                          # F10
    return out, echo_soft(parrafos)                                                     # F7c-3 §7 (blanda)


# ── F10: fechas literales ─────────────────────────────────────────────────────

MESES = "enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|setiembre|octubre|noviembre|diciembre"
DATE_RE = re.compile(rf"\b(?:\d{{1,2}}|primero)\s+de\s+(?:{MESES})(?:\s+de\s+(\d{{4}}))?\b", re.I)
DATE_MAX_PER_CAP = 1                 # F23 §1.1: métrica («fechas literales por cap»), ya no es un problema
# lo que reemplaza una fecha ya dicha (el chequeo de «dato literal» de m05 lo acepta para un evento con fecha, solo si
# el caso es puntual). F23: + «ese año», «ese invierno», «esa primavera», «ese mes»
DATE_PARAPHRASE = re.compile(r"\b(?:ese|aquel|aquél) (?:domingo|lunes|martes|miércoles|jueves|viernes|sábado|día|"
                             r"mediodía|mismo día|año|invierno|mes)\b|\besa (?:mañana|tarde|noche|madrugada|"
                             r"primavera)\b", re.I)


# F23 §1.1: `replace_repeated_dates` (con el día de la semana fijo) se borró; la buena es
# `guion_v4.replace_repeated_dates`.


def fechas_literales_por_cap(caps: list[dict]) -> dict[int, int]:
    """F23 §1.1 (métrica): cuántas fechas literales («14 de marzo», con o sin año) dice cada cap."""
    return {c["chapter_number"]: len(DATE_RE.findall(c.get("narration") or "")) for c in caps}


def anios_por_cap(caps: list[dict]) -> dict[int, int]:
    """F54 A.3 (métrica, sin freno): cuántos años literales dice cada cap, en cifras («1962») o en letras («mil
    novecientos sesenta y dos», «dos mil siete»); cada mención cuenta."""
    from script_engine.m01a_escaleta import NUM_PALABRA
    rx = re.compile(rf"\b(?:\d{{4}}|mil (?:ochocientos|novecientos)(?: (?:{NUM_PALABRA}))?|dos mil (?:{NUM_PALABRA}))\b")
    return {c["chapter_number"]: len(rx.findall(ev.norm(c.get("narration") or ""))) for c in caps}


def datos_por_min(caps: list[dict], palabras_por_seg: float) -> dict[int, float]:
    """F54 A.3 (métrica, sin freno): ids usados del cap (`datos_usados`) por minuto de duración estimada
    (palabras / `palabras_por_seg`)."""
    out = {}
    for c in caps:
        w = len((c.get("narration") or "").split())
        out[c["chapter_number"]] = round(len(c.get("datos_usados") or []) / (w / palabras_por_seg / 60), 1) if w else 0.0
    return out


def date_problems(caps: list[dict]) -> list[str]:
    """F10 (Omar): la fecha completa (con año) de un día una sola vez en el video. F23 §1.1: el tope de una fecha
    literal por cap (DATE_MAX_PER_CAP) pasó a métrica (`fechas_literales_por_cap`)."""
    out, seen = [], {}
    for c in caps:
        for m in DATE_RE.finditer(c.get("narration") or ""):
            if m.group(1):
                k = ev.norm(m.group(0))
                if k in seen:
                    out.append(f"cap {c['chapter_number']}: la fecha completa «{m.group(0)}» ya se dijo en el cap "
                               f"{seen[k]}: una sola vez en el video")
                seen.setdefault(k, c["chapter_number"])
    return list(dict.fromkeys(out))


# ═══════════════════════════════════════════════════════════════
#  F7c-3 (HANDOFF_F7 §9.1) — reglas de oficio
# ═══════════════════════════════════════════════════════════════

_SENT = re.compile(r"(?<=[.!?…»”])\s+(?=[«“\"¿¡A-ZÁÉÍÓÚÑ])")


def sentences_of(text: str) -> list[str]:
    return [s.strip() for s in _SENT.split(text or "") if s.strip()]


# ── 1. rol de quien habla ─────────────────────────────────────────────────────

# F21: sin la dicotomía preso/guardia de Orleans. Las clases son las del perfil del caso: `roles_testigo` y
# `roles_antagonista` (`research_v3.vocabulario()`, las mismas que lee el research). Sin perfil, ninguna: (b) no
# evalúa nada.
def _roles() -> dict[str, list[str]]:
    from researcher_steps.research_v3 import vocabulario
    from script_engine import nombres
    v = vocabulario()
    return {k: sorted({nombres.norm(r) for r in v.get(f"roles_{k}") or [] if nombres.norm(r)}, key=len, reverse=True)
            for k in ("testigo", "antagonista")}


def _alt(words: list[str]) -> str:
    return "|".join(re.escape(w) for w in words)


def role_class(text: str | None) -> str | None:
    """«testigo» o «antagonista» según el rol escrito (pool o narración), con las palabras del perfil del caso; None si
    no es ninguno o si no hay perfil."""
    from script_engine import nombres
    r = _roles()
    t = nombres.norm(text)
    found = []
    for k in ("testigo", "antagonista"):
        if r[k]:
            m = re.search(rf"(?<![^\W\d_])(?:{_alt(r[k])})(?![^\W\d_])", t)
            if m:
                found.append((m.start(), k))
    return min(found)[1] if found else None            # las dos: manda la primera palabra de rol


def _role_before() -> re.Pattern | None:
    r = _roles()
    words = r["testigo"] + r["antagonista"]
    if not words:
        return None
    return re.compile(r"\b(?:el|la|los|las|un|una)\s+((?:\w+\s+){0,1}?(?:" + _alt(words) + r"))(?:\s+del?\s+\w+)?\s*$",
                      re.I)


def _role_after() -> re.Pattern | None:
    r = _roles()
    words = r["testigo"] + r["antagonista"]
    if not words:
        return None
    return re.compile(r"\s*,\s*(?:el|la|un|una)\s+((?:\w+\s+){0,1}?(?:" + _alt(words) + r"))(?![^\W\d_])", re.I)


def role_problems(text: str, pool: dict[str, Any]) -> list[str]:
    """El rol con que la narración presenta a quien habla tiene que ser su rol en el pool (preso / guardia):
    «la reclusa Rhonda Ducre» (es guardia), «un guardia lo describió: «…»» (la cita es de un preso)."""
    from script_engine import nombres
    out = []
    people = pool.get("personajes") or []
    before_re, after_re = _role_before(), _role_after()
    if before_re is None:                               # sin perfil del caso: (b) no evalúa nada
        return []
    low = nombres.norm(text)
    for p in people:
        want = role_class(p.get("rol"))
        if not want:
            continue
        terms = nombres.terminos(p, people)
        for t in terms:
            for m in re.finditer(rf"(?<![^\W\d_]){re.escape(t)}(?![^\W\d_])", low):
                before = low[max(0, m.start() - 45):m.start()]
                rm = before_re.search(before)
                got = role_class(rm.group(1)) if rm else None
                if got and got != want:
                    out.append(f"«{rm.group(0).strip()} {p['nombre']}»: en el pool es {p.get('rol')} ({want})")
                after = low[m.end():m.end() + 40]                 # en aposición: «Brady Richard, un preso,»
                am = after_re.match(after)
                got = role_class(am.group(1)) if am else None
                if got and got != want:
                    out.append(f"«{p['nombre']}{am.group(0).rstrip()}»: en el pool es {p.get('rol')} ({want})")
    # citas anónimas presentadas con un rol
    cits = pool.get("citas") or []
    for s in sentences_of(text):
        for q in quotes_in(s):
            nq = ev.norm(q)
            src = next((c for c in cits if nq and (nq in ev.norm(c.get("texto") or "")
                                                   or nq in ev.norm(c.get("fragmento") or ""))), None)
            if not src:
                continue
            per = next((x for x in people if (src.get("autor") or "") and nombres.misma(x["nombre"], src.get("autor"))),
                       None)
            want = role_class(src.get("rol")) or role_class(src.get("autor")) or role_class((per or {}).get("rol"))
            intro = s.split("«")[0].split("“")[0]
            got = role_class(intro)
            sur = nombres.apellido(src.get("autor") or "")
            if want and got and got != want and not (sur and nombres.menciona(intro, sur)):
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


def antagonista_tipo(esc: dict) -> str:
    """F22 §1.2: persona / institucion / ninguno. Una escaleta sin `tipo` (v1, F16 y antes) es de persona."""
    return str((esc.get("antagonista") or {}).get("tipo") or "persona")


def antagonist_problems(caps: list[dict], esc: dict, pool: dict[str, Any]) -> list[str]:
    """Si un cap usa un dato VERIFICADO que nombra al antagonista (la decisión de quien decide), la voz dice su
    apellido (aunque su cita sea verificada_parcial). Nunca «según alguien» ni «una voz oficial».
    F22 §1.2: solo con un antagonista persona; con una institución o ninguno no se evalúa (la institución va a la
    métrica `antagonista_caps`)."""
    out: list[str] = []
    if antagonista_tipo(esc) != "persona":
        return out
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


def antagonista_terminos(esc: dict, pool: dict[str, Any]) -> list[str]:
    """F22 §1.2: cómo buscar al antagonista en la narración (normalizado). Persona: los términos de `nombres.terminos`
    (su P## del pool). Institución: su nombre y sus variantes (las de la ficha, que la escaleta copia), sin el artículo.
    Ninguno: []."""
    from script_engine import nombres
    ag = esc.get("antagonista") or {}
    tipo = antagonista_tipo(esc)
    if tipo == "persona":
        people = pool.get("personajes") or []
        p = next((x for x in people if x.get("id") == ag.get("id")), None)
        if not p:
            return []
        completos = [nombres.norm(n) for n in [p.get("nombre"), *(p.get("variantes_nombre") or [])] if n]
        return list(dict.fromkeys(nombres.terminos(p, people) + [n for n in completos if len(n.split()) >= 2]))
    if tipo != "institucion":
        return []
    out = []
    for n in [ag.get("nombre"), *(ag.get("variantes") or [])]:
        t = re.sub(r"^(el|la|los|las|the) ", "", nombres.norm(n or ""))
        if len(t) >= 3:
            out.append(t)
    return list(dict.fromkeys(out))


def antagonista_caps(caps: list[dict], esc: dict, pool: dict[str, Any]) -> list[int]:
    """F22 §1.2 (métrica informativa): los caps donde la narración nombra al antagonista (`nombres.menciona`)."""
    from script_engine import nombres
    ts = antagonista_terminos(esc, pool)
    return [c["chapter_number"] for c in caps if any(nombres.menciona(c.get("narration") or "", t) for t in ts)]


# ── 4. sin fotos en ningún cap ────────────────────────────────────────────────

# F21: solo la foto; «cámara», «imagen», «retrato», «instantánea» pueden ser hechos («la cámara de reacción», «la imagen
# satelital»)
_PHOTO_ANY = re.compile(r"\b(fotos?|fotograf\w*|fot[oó]graf[oa]s?)\b", re.I)


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
           r"\bse nieg\w+ a olvidar\b|\bse negaron a olvidar\b", r"\bdescubriremos\b", r"\besta historia\b", r"\bnuestra historia\b",
           r"\bhistoria que (?:nadie|pocos) (?:cuenta|conoce)\b"]


def trailer_problems(text: str) -> list[str]:
    return [f"voz de tráiler (el narrador habla del video): «{m.group(0)}»"
            for pat in TRAILER for m in re.finditer(pat, text or "", re.I)]


# ── 6. ancla de lugar y fecha en el gancho ────────────────────────────────────

ANCHOR_MAX_WORDS = 10
_YEAR = re.compile(r"\b(?:1[0-9]{3}|20\d\d)\b")


def _place_tokens(pool: dict[str, Any]) -> set[str]:
    return {w for lg in pool.get("lugares") or [] for w in _tokens(lg.get("nombre") or "") if len(w) >= 5}


def anchor_sentences(cap1: str, pool: dict[str, Any]) -> list[str]:
    """Frases cortas (≤ ANCHOR_MAX_WORDS palabras) con un año y un lugar del pool («<lugar>, <mes> de <año>»)."""
    places = _place_tokens(pool)
    return [s for s in sentences_of(cap1) if len(s.split()) <= ANCHOR_MAX_WORDS and _YEAR.search(s)
            and set(_tokens(s)) & places]


def _ancla_modelo() -> str:
    """F22 §1.1: el ejemplo del ancla, con el lugar y el año del seed actual (`research_v3.caso()`); sin perfil, nada
    (antes, el ancla de Orleans para cualquier caso)."""
    from researcher_steps.research_v3 import caso
    c = caso()
    return f": «{c['lugar']}, {c['anio']}.»" if c.get("lugar") and c.get("anio") else ""


def hook_anchor_problems(cap1: str, pool: dict[str, Any]) -> list[str]:
    """El gancho lleva una frase corta con ciudad + año antes de la segunda cita."""
    anchors = anchor_sentences(cap1, pool)
    if not anchors:
        return [f"gancho: falta el ancla de lugar y fecha (una frase corta con el lugar y el año{_ancla_modelo()}) "
                "antes de la segunda cita"]
    qpos = [m.start() for m in _QUOTED.finditer(cap1 or "") if len(m.group(1).split()) > 3]
    if len(qpos) >= 2 and (cap1 or "").find(anchors[0]) > qpos[1]:
        return ["gancho: el ancla de lugar y fecha va antes de la segunda cita"]
    return []


# ── 7. cita fuerte, silencio después (blanda, para el editor) ─────────────────

ECHO_MAX_WORDS = 6


def closing_soft(parrafos: list[dict]) -> list[str]:
    """F8 §2 (blanda, al editor): la última frase del video es una cita o una pregunta, nunca un resumen
    («Cientos de familias nunca supieron…» → termina en la cita). El editor no agrega citas: reordena o corta dentro
    del último párrafo para que lo último que suene sea la cita o la pregunta que ya tiene."""
    if not parrafos:
        return []
    k = len(parrafos) - 1
    ss = sentences_of(parrafos[k].get("texto") or "")
    if not ss:
        return []
    last = ss[-1].strip()
    if re.search(r"\?\W*$", last) or re.search(r"[«“\"]", last):     # pregunta, o cita (con su atribución)
        return []
    has_q = any(re.search(r"[«“\"]", s) or s.strip().endswith("?") for s in ss[:-1])
    how = ("mové la cita o la pregunta de este párrafo al final, o cortá lo que viene después" if has_q else
           "cortá la frase-resumen si el párrafo ya cierra con algo concreto antes")
    return [f"párrafo {k} (último del video): la última frase «{last}» es un resumen; el video termina en una cita "
            f"o una pregunta: {how}"]


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
