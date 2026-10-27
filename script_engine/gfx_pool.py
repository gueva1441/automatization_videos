"""
gfx_pool.py — La pantalla se alimenta del evidence_pool (F5 §2). Todo detrás de `if pool`: un guion sin pool sigue
con verified_facts exactamente como antes.

    pool_sources()          textos del pool que el candado literal acepta (datos, citas, cronología, lugares, nombres,
                            fuentes cortas «Organización, año»)
    cap_candidates()        ids del pool para los recortes/datos de un cap: los suyos (skeleton) y los del cap
                            ANTERIOR, sin los hechos que ya salieron en pantalla en un cap anterior
    plan_pool_documents()   recortes: cláusula completa del dato que SUMA a la voz del tramo, kicker = fuente del dato →
                            su fecha → sin recorte; Flash elige entre las 3 mejores. Datos: la cifra del pool en el
                            instante en que la voz la nombra (R7 la saca si la voz la dice literal). Nunca un texto de
                            la narración.
    content_icon()          ícono del recorte/dato por el mapa LITERAL palabra→ícono del perfil (icon_words)
    pool_ticker()           reloj desde la cronología del cap: con hora si la hay; si el cap no avanza de fecha, no sale

F5b (VALIDACION_F5 §5, P1–P6):
    S1 cláusula   pool_clause_options: el recorte arranca donde arranca la cláusula (su sujeto) y termina donde termina
                  la cláusula o en un borde de frase después del objeto («Un jurado federal otorga más de $650,000»).
                  Nunca una cola («federal otorga…», «piso comienzan…», «la prisión no finalizó…»). Sin opción → sin
                  recorte (Flash solo ELIGE entre esas opciones).
    S2 cronología un recorte no muestra un hecho POSTERIOR a la fecha que la voz viene narrando en ese tramo.
    S3 hecho      dedupe por hecho (evidence.same_fact: misma cifra + entidad = uno), entre caps y dentro del cap; los
                  candidatos salen del cap actual y del anterior, nunca del siguiente (no destripa el cliffhanger).
    S4 ícono      solo por el mapa literal del perfil; un adjetivo nunca; la categoría solo decide el mood.
    S5 unidades   en pantalla, unidades métricas: una opción con pies/millas/libras/°F queda fuera (el pool guarda
                  «15 pies (4.6 metros)»: sale la cláusula métrica o nada).

F5f (después de ver Orleans v2 F5e):
    reservado     un dato reservado para pantalla desplaza sellos, moods, datos, contador y zoom (nunca al revés); solo
                  cede ante título, pregunta y nivel de agua. Cada uno que no entra queda con el bloque que choca.
    eco           un recorte con una cifra que la voz dice a ± archive_figure_echo_sec queda fuera; entre recortes,
                  archive_min_gap_sec libres.
    comillas      un titular nunca termina con una comilla abierta: se cierra si la cita entera entra, si no se corta
                  antes de la comilla (si queda una cláusula) o la opción se descarta.
    cita          bloque nuevo `quote_card`: una cita del cap, texto LITERAL + autor, 4–5 s sobre la foto oscurecida,
                  cuando la voz la dice (o en su oración). Prioridad de reservado.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Callable

from script_engine import evidence as ev

# Íconos que el handoff pide y todavía no existen (F5 J33): se anotan en el bloque y salen sin ícono.
MISSING_ICONS: tuple[tuple[tuple[str, ...], str], ...] = (
    (("huracan", "tormenta", "ciclon"), "espiral"),
    (("generador", "apagon"), "rayo_tachado"),
)
_PEOPLE = ("personas", "reclusos", "presos", "prisioneros", "niños", "ninos", "hombres", "mujeres", "internos",
           "víctimas", "victimas", "almas", "turistas", "testimonios")
_YEAR = re.compile(r"\b(1[5-9]\d\d|20\d\d)\b")
IMPERIAL = re.compile(r"\b(?:pies?|millas?|yardas?|pulgadas?|libras?|galones?|fahrenheit)\b|°\s?F\b", re.I)
_NEVER_ICON_ALONE = {"agua", "aguas"}             # F4c R4: «agua» sola nunca lleva gota


def short_source(src: str | None) -> str:
    """«Human Rights Watch, 2005, "New Orleans…"» → «Human Rights Watch, 2005» (literal: pasa el candado)."""
    if not src:
        return ""
    m = _YEAR.search(src)
    return src[:m.end()].strip() if m else src.split(",")[0].strip()


def pool_sources(pool: dict[str, Any] | None) -> dict[str, str]:
    out: dict[str, str] = {}
    for i, it in ev.items(pool).items():
        out[f"pool.{i}"] = ev.text_of(it)
        if it.get("autor"):
            out[f"pool.{i}.autor"] = it["autor"]
        if it.get("fuente"):
            out[f"pool.{i}.fuente"] = it["fuente"]
    return out


# ═══════════════════════════════════════════════════════════════
#  S4 — ícono por el mapa literal del perfil
# ═══════════════════════════════════════════════════════════════

def literal_icon_map(moods: dict[str, dict[str, Any]] | None = None) -> dict[str, str]:
    """{palabra normalizada: ícono} de los icon_words de todos los moods del perfil."""
    if moods is None:
        from gfx_config import active_moods
        moods = active_moods()
    return {ev.norm(w): ico for m in (moods or {}).values() for w, ico in ((m or {}).get("icon_words") or {}).items()}


def content_icon(it: dict[str, Any], available: set[str] | frozenset[str], moods: dict[str, dict[str, Any]] | None = None,
                 headline: str | None = None) -> tuple[str | None, str | None]:
    """(ícono, ícono_faltante) del recorte/dato. F5b S4: la primera palabra del titular (o del texto del dato) que
    está en el mapa literal del perfil; un adjetivo nunca; cifra de personas → sin ícono. Huracán/generadores →
    anotados como faltantes (no existen en el set)."""
    from script_engine.m05_narrative import adjectives
    shown = headline if headline is not None else ev.text_of(it)
    txt = ev.norm(shown)
    if it.get("tipo") in ("cifra", "magnitud") and re.search(r"\d[\d.,]*\s+(?:\w+\s+)?(" + "|".join(_PEOPLE) + r")\b",
                                                             txt):
        return None, None
    adj = {ev.norm(a) for a in adjectives(shown)}
    imap = literal_icon_map(moods)
    hits = []
    for key, ico in imap.items():
        if key in _NEVER_ICON_ALONE or key in adj:
            continue
        m = re.search(rf"(?<!\w){re.escape(key)}(?!\w)", txt)
        if m:
            hits.append((m.start(), -len(key), ico))
    if hits:
        ico = min(hits)[2]
        return (ico, None) if ico in available else (None, ico)
    for roots, ico in MISSING_ICONS:
        if any(r in txt for r in roots):
            return (ico, None) if ico in available else (None, ico)
    return None, None


# ═══════════════════════════════════════════════════════════════
#  S1 — cláusula completa (nunca una cola)
# ═══════════════════════════════════════════════════════════════

# F36 §D: piezas de gfx_fragments (borrado) que usan pool_clause_options y _kicker (m01a_skeleton, Fase 1),
# movidas sin cambios
EDGE_STOP = {"de", "del", "la", "las", "el", "los", "un", "una", "unos", "unas", "y", "o", "e", "en", "a", "al", "que",
             "por", "con", "para", "sin", "se", "su", "sus", "lo", "como", "según", "hasta", "durante", "pero", "mientras",
             "haber", "había", "habían", "ser", "sido", "estar", "fue", "fueron", "era", "eran", "es", "muy", "más"}

_VERB_EDGE = re.compile(r"(ó|aron|ieron|eron|ando|endo|iendo|aba|aban|ía|ían|ar|er|ir|amos|aron|an|en)$")

_KEEP_EDGE = {"orleans", "katrina", "pies", "metros", "personas", "almas", "presos", "prisioneros", "agua", "aguas",
              "tren", "orden", "joven", "volumen", "crimen", "origen", "imagen", "examen", "hombre", "mujeres"}

_MONTHS = r"(?:enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|setiembre|octubre|noviembre|diciembre)"

_DATE_RE = re.compile(rf"\b\d{{1,2}} de {_MONTHS}(?: de \d{{4}})?", re.IGNORECASE)

def _verb_edge(w: str) -> bool:
    t = _tok(w)
    return bool(t) and not t[:1].isdigit() and t not in _KEEP_EDGE and not w[:1].isupper() and len(t) > 3         and bool(_VERB_EDGE.search(t))

def _tok(w: str) -> str:
    return re.sub(r"^[¿¡\"'«“(]+|[.,;:!?…\"'»”)]+$", "", str(w)).lower()

_VAGUE = {"algunos", "algunas", "casos", "otros", "otras", "todos", "todas", "mismo", "misma", "cosas", "parte", "partes",
          "veces", "manera", "forma"}

DOC_MAX_WORDS = 10

_SUBORD = {"mientras", "cuando", "aunque", "porque", "donde"}

_ARTICLES = {"el", "la", "los", "las", "un", "una", "unos", "unas"}

_PARTICIPLE = re.compile(r"(ado|ada|ados|adas|ido|ida|idos|idas)$")

_IRREG_PART = {"visto", "vista", "hecho", "hecha", "dicho", "dicha", "puesto", "puesta", "escrito", "abierto",
               "abierta", "cubierto", "cubierta", "vuelto"}

_MONTH_SET = set(_MONTHS.strip("(?:)").split("|"))

def _start_ok(w: str) -> bool:
    """La opción arranca en artículo, nombre o sustantivo (no en verbo, participio, adverbio ni palabra funcional)."""
    t = _tok(w)
    if re.fullmatch(r"\$?\d[\d.,]*%?", w):            # F5: una cifra arranca bien («517 prisioneros…»)
        return True
    if not re.match(r"[A-Za-zÁÉÍÓÚÑáéíóúñ]", w) or re.search(r"[\"'«»“”]$", w):
        return False
    if t in _ARTICLES or w[:1].isupper():
        return True
    if t in EDGE_STOP or t in _VAGUE or t in _IRREG_PART or t.endswith("mente") or re.search(r"(ar|er|ir)se$", t):
        return False                                    # «inundarse y…» arranca en verbo
    return len(t) >= 4 and not _verb_edge(w) and not _PARTICIPLE.search(t)

def _has_subject(ws: list[str]) -> bool:
    return any(len(_tok(w)) >= 4 and not _tok(w)[:1].isdigit() and _tok(w) not in _MONTH_SET and _tok(w) not in EDGE_STOP
               for w in ws)

def _dedupe(opts: list[str]) -> list[str]:
    seen, out = set(), []
    for o in opts:
        if o.lower() not in seen:
            seen.add(o.lower())
            out.append(o)
    return out


_BREAK = {"a", "al", "en", "hasta", "para", "por", "con", "sobre", "durante", "tras", "desde", "que", "y", "e", "o",
          "mientras", "cuando", "donde", "según", "antes", "después", "como", "sin", "entre", "contra"}
_AUX = {"es", "son", "fue", "fueron", "era", "eran", "está", "están", "estaba", "estaban", "hay", "había", "habían",
        "tiene", "tienen", "tenía", "tenían", "queda", "quedan", "sigue", "siguen"}
_PAST = re.compile(r"(ó|aron|ieron|eron|aba|aban|ía|ían)$")
_NOT_VERB = {"agua", "aguas", "noche", "parte", "celda", "orden", "joven", "origen", "imagen", "crimen", "examen",
             "volumen", "huelga", "tormenta", "guardia", "guardias", "prisión", "evacuación", "inundación", "comida",
             "cárcel", "medianoche", "fuente", "fuentes", "gente", "frente", "ayuda", "pública", "público",
             "contra", "entre", "sobre", "hacia", "desde", "durante", "mediante", "según", "antes", "mientras"}
# «EE. UU.», «Jr.», «St.», «N.» no cortan la cláusula
_ABBR = re.compile(r"\b(EE|UU|Jr|Sr|St|Dr|[A-Z])\.(?=\s)")
# una sigla entre paréntesis es parte de la cláusula: «La Prisión de Orleans Parish (OPP) albergaba a 6,375…»
_ACRO_PAREN = re.compile(r"\(([A-Z][A-Za-z.]{1,7})\)")


def _is_verb(w: str, prev: str = "", first: bool = False) -> bool:
    """Heurística (sin etiquetador): auxiliar, pretérito/imperfecto (-ó, -aron, -ía…) o presente (-a/-e/-an/-en) que
    no sigue a un artículo ni a una preposición («la celda» no; «federal otorga» sí). `first`: la 1.ª palabra de la
    cláusula puede ser el verbo con mayúscula («Comienza la evacuación…»)."""
    t = _tok(w)
    if t in _AUX and not w[:1].isupper():
        return True
    if not t or t[:1].isdigit() or t in _NOT_VERB or t.endswith("mente") or t in EDGE_STOP:
        return False
    plain = ev.norm(t)                                    # «serán» termina en -an
    present = len(t) >= 5 and plain.endswith(("a", "e", "an", "en"))
    if first:
        return (len(t) >= 4 and bool(_PAST.search(t))) or (len(t) >= 4 and plain.endswith(("a", "e", "an", "en")))
    if w[:1].isupper():
        return False
    if len(t) >= 4 and _PAST.search(t):
        return True
    p = _tok(prev)
    return present and bool(p) and p not in EDGE_STOP and p not in _BREAK


def _verbs(ws: list[str]) -> list[int]:
    """Índices de los verbos de la cláusula (la 1.ª palabra solo si arranca en verbo seguido de artículo:
    «Comienza la evacuación…»; «Templeman 1» no)."""
    return [k for k in range(len(ws)) if (_is_verb(ws[k], ws[k - 1]) if k else
                                          len(ws) > 1 and _tok(ws[1]) in _ARTICLES and _is_verb(ws[0], first=True))]


def _has_verb(ws: list[str]) -> int | None:
    """Índice del primer verbo de la cláusula, o None."""
    v = _verbs(ws)
    return v[0] if v else None


# marcadores internos (no aparecen en un texto del pool): un punto de abreviatura, los paréntesis de una sigla y la
# coma de «Morgan, Jr.» no cortan la cláusula
_DOT, _LP, _RP, _COMMA = chr(0x2024), chr(0x2768), chr(0x2769), chr(0x201A)


def _bare_figure(c: list[str]) -> bool:
    """Una parte sin verbo vale si trae una cifra que no es parte de un nombre («un huracán de categoría 3»,
    «Aproximadamente 6,500 personas»; no «Templeman 1 y 2» ni «A la medianoche»)."""
    return any(re.match(r"\$?\d", w) and (k == 0 or (c[k - 1][:1].islower() and _tok(c[k - 1]) not in {"y", "e"}))
               for k, w in enumerate(c))


def _cut_ok(c: list[str], e: int, vk: list[int]) -> bool:
    """¿Se puede cortar la cláusula antes de c[e]? En un borde de frase y con el verbo ya dicho:
    - preposición, «que», «y»… (o «de» + artículo: «evacuados | de la Prisión») DESPUÉS de verbo + objeto: «… no
      finalizó | hasta el viernes» no corta (el verbo pide su complemento);
    - una fecha («fallaron | el 29 de agosto») puede cortar justo después del verbo: la fecha va al kicker;
    - nunca dentro de «más de 50» / «menos de…»."""
    nxt = c[e + 1] if e + 1 < len(c) else ""
    if _tok(c[e - 1]) in EDGE_STOP or _tok(c[e - 1]) in {"más", "menos"} or re.match(r"\$?\d", nxt):
        if not (_tok(c[e]) in {"el", "del"} and re.match(r"\d", nxt)):
            return False
    last = max(k for k in vk if k < e) if any(k < e for k in vk) else None
    if last is None:
        return False
    if _tok(c[e]) in {"el", "del"} and re.match(r"\d", nxt):          # «… el 29 de agosto»
        return _tok(c[e - 1]) not in EDGE_STOP
    brk = _tok(c[e]) in _BREAK or (_tok(c[e]) == "de" and _tok(nxt) in _ARTICLES)
    return brk and last <= e - 2


def _unprotect(s: str) -> str:
    return s.replace(_DOT, ".").replace(_LP, "(").replace(_RP, ")").replace(_COMMA, ",")


def pool_clause_options(text: str, max_words: int | None = None) -> list[str]:
    """F5b S1: opciones de recorte que son CLÁUSULAS COMPLETAS del texto del pool: arrancan en el arranque de la
    cláusula (su sujeto: artículo, nombre, cifra o sustantivo) y terminan donde termina la cláusula, o en un borde de
    frase (preposición, «que», «y», «el 29 de…») DESPUÉS de verbo + objeto. ≤ max_words. Una coordinada o una
    subordinada con sujeto y verbo propios («y las aguas residuales refluyen») es otra cláusula; un sujeto coordinado
    («Robie Waganfeald y Paul Kunkel Jr.») no. Una parte entre comas sin verbo (aposición, rótulo) vale entera.
    Nunca una cola que arranca a mitad de frase. Sin unidades imperiales (S5)."""
    max_words = max_words or DOC_MAX_WORDS
    prot = _ABBR.sub(lambda m: m.group(1) + _DOT, re.sub(r"\s+", " ", str(text)).strip())
    prot = _ACRO_PAREN.sub(lambda m: _LP + m.group(1) + _RP, prot)
    prot = re.sub(r",(\s+(?:Jr|Sr)\b)", _COMMA + r"\1", prot)
    out: list[str] = []
    for part in re.split(r"[,.;:!?…](?=\s|$)|[()]|\s[—–-]\s", prot):
        ws = part.split()
        if not ws or (ws[0][:1].islower() and _is_verb(ws[0], first=True)):
            continue                                   # «toca tierra en…»: el predicado sin su sujeto (otra parte)
        cand = [k + 1 for k in range(len(ws) - 2) if (_tok(ws[k]) in {"y", "e", "que"} | _SUBORD)
                and _start_ok(ws[k + 1])]
        for _ in range(2):                             # cada cláusula, con verbo propio hasta la siguiente
            bounds = [0] + cand + [len(ws) + 1]
            cand = [st for j, st in enumerate(cand, start=1)
                    if _has_verb(ws[st:bounds[j + 1] - 1]) is not None
                    and (_tok(ws[st - 1]) not in {"y", "e"} or _has_verb(ws[bounds[j - 1]:st - 1]) is not None)]
        starts = [0] + cand
        for si, st in enumerate(starts):
            end = starts[si + 1] - 1 if si + 1 < len(starts) else len(ws)
            spans = [ws[st:end]] + ([ws[st:]] if end < len(ws) else [])     # la cláusula sola y con su coordinada
            for c in spans:
                if not c or not _start_ok(c[0]):
                    continue
                vk = _verbs(c)
                if not vk and (st > 0 or len(spans) > 1 or not _bare_figure(c)):
                    continue                           # sin verbo: solo una parte entera entre comas, con su cifra
                ends = {len(c)}
                if vk:
                    ends |= {e for e in range(vk[0] + 1, len(c)) if _cut_ok(c, e, vk)}
                for e in sorted(ends):
                    frag = c[:e]
                    vs = [frag]
                    if (len(frag) >= 5 and re.fullmatch(r"\d{4}", _tok(frag[-1])) and _tok(frag[-2]) == "de"
                            and _tok(frag[-3]) in _MONTH_SET):
                        vs.append(frag[:-2])                         # «… 2 de septiembre» (el año va al kicker)
                    for x in vs:
                        sx = _unprotect(" ".join(x))
                        if (2 <= len(x) <= max_words and _has_subject(x) and _tok(x[-1]) not in EDGE_STOP
                                and not IMPERIAL.search(sx)):
                            sx = close_quotes(sx, str(text), max_words)
                            if sx:
                                out.append(sx)
    return _dedupe(out)


_QUOTE_PAIRS = (('"', '"'), ("«", "»"), ("“", "”"))


def _open_quote(t: str) -> int | None:
    """Posición de la comilla que queda ABIERTA en `t` (None si todas cierran)."""
    for o, c in _QUOTE_PAIRS:
        if o == c:
            k = [m.start() for m in re.finditer(re.escape(o), t)]
            if len(k) % 2:
                return k[-1]
        elif t.count(o) > t.count(c):
            return t.rfind(o)
    return None


def close_quotes(head: str, text: str, max_words: int) -> str | None:
    """F5f: un titular nunca termina con una comilla abierta. Se cierra con el texto LITERAL hasta la comilla de cierre
    si la cita entera entra en max_words; si no, se corta antes de la comilla (si queda una cláusula de ≥ 3 palabras);
    si tampoco, None (la opción se descarta)."""
    k = _open_quote(head)
    if k is None:
        return head
    flat = re.sub(r"\s+", " ", text)
    j = flat.find(head)
    if j >= 0:
        o = head[k]
        c = dict(_QUOTE_PAIRS)[o]
        e = flat.find(c, j + k + 1)
        full = flat[j:e + 1] if e > 0 else ""
        if full and len(full.split()) <= max_words:
            return full
    cut = head[:k].rstrip(" ,:;—–-")
    ws = cut.split()
    return cut if len(ws) >= 3 and _tok(ws[-1]) not in EDGE_STOP and _has_verb(ws) is not None else None


# ═══════════════════════════════════════════════════════════════
#  S2 — cronología: la fecha que viene narrando la voz
# ═══════════════════════════════════════════════════════════════


# ═══════════════════════════════════════════════════════════════
#  S3 — candidatos y dedupe por hecho
# ═══════════════════════════════════════════════════════════════

def used_ids_before(work_dir: Path, chapter_number: int) -> set[str]:
    """Ids del pool ya mostrados en pantalla (recortes/datos) en caps anteriores."""
    out: set[str] = set()
    for f in sorted(Path(work_dir).glob("gfx_plan_ch*.resolved.json")):
        m = re.search(r"ch(\d+)", f.name)
        if not m or int(m.group(1)) >= chapter_number:
            continue
        try:
            plan = json.loads(f.read_text(encoding="utf-8")).get("plan") or {}
        except (OSError, ValueError):
            continue
        for b in (plan.get("archive_clippings") or []) + (plan.get("callouts") or []) + \
                ([plan["quote_card"]] if plan.get("quote_card") else []):
            if b.get("pool_id"):
                out.add(b["pool_id"])
    return out


def cap_candidates(pool: dict[str, Any], skeleton: dict[str, Any], cap: int, used: set[str]) -> list[str]:
    """F5b S3: los ids del cap y después los del cap ANTERIOR (nunca del siguiente: el cliffhanger no se destripa),
    datos duros y citas, sin los que cuentan un hecho ya mostrado en un cap anterior (mismo id o mismo hecho).
    F5d: primero los RESERVADOS PARA PANTALLA del cap (`pantalla_ids`: el narrador no los dice)."""
    its = ev.items(pool)
    by_cap = {c.get("chapter_number"): c.get("evidence_ids") or [] for c in skeleton.get("chapters") or []}
    scr = {c.get("chapter_number"): c.get("pantalla_ids") or [] for c in skeleton.get("chapters") or []}
    ids = list(scr.get(cap, [])) + list(by_cap.get(cap, [])) + list(by_cap.get(cap - 1, []))
    shown = [its[i] for i in used if i in its]
    out = []
    for i in dict.fromkeys(ids):
        it = its.get(i)
        if not it or i in used or not (ev.is_hard(it) or it["_kind"] == "citas"):
            continue
        if any(ev.same_fact(it, s) for s in shown):
            continue
        out.append(i)
    return out


# F29 §D: el `call` del paso de forma de los recortes (Flash elige la cláusula); None = Gemini Flash, como siempre
FORMA_CALL: Callable[..., dict] | None = None


def _hits(a: float, b: float, busy: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [x for x in busy if x["a"] < b and x["b"] > a]


_NUM = re.compile(r"\d[\d.,]*\d|\d")


def _kicker(it: dict[str, Any], headline: str) -> str:
    """F5: fuente del dato → su fecha (literal en el texto, o el año) → "" (sin recorte)."""
    low = headline.lower()
    cands = [short_source(it.get("fuente"))]
    d = _DATE_RE.search(ev.text_of(it))
    cands.append(d.group(0) if d else "")
    y = _YEAR.search(ev.text_of(it)) or _YEAR.search(str(it.get("fecha") or ""))
    cands.append(y.group(1) if y else "")
    return next((c for c in cands if c and c.lower() not in low), "")


def pool_ticker(ctx: dict[str, Any], words: list[dict], clip_dur: float, time_offset: float = 0.0
                ) -> dict[str, Any] | None:
    """Reloj desde la cronología del cap. Sale solo si el cap avanza de fecha (≥ 2 fechas distintas) o trae hora.
    Muestra la primera fecha (o hora) desde que la voz la nombra. F5f: cuando la voz nombra la fecha siguiente, el
    reloj CAMBIA de fecha con animación (`changes`, hasta 2) y la sostiene TICKER_HOLD s; antes terminaba ahí."""
    from script_engine.gfx_peak import sentences
    from script_engine.voz_datos import MESES
    pool, skel = ctx.get("pool"), ctx.get("skeleton_all") or {}
    its = ev.items(pool)
    n = ctx["chapter_number"]
    ids = next((c.get("evidence_ids") or [] for c in skel.get("chapters") or [] if c.get("chapter_number") == n), [])
    crono = sorted((its[i] for i in ids if i in its and its[i]["_kind"] == "cronologia"
                    and re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(its[i].get("fecha") or ""))),
                   key=lambda c: (c["fecha"], c.get("hora") or ""))
    dates = list(dict.fromkeys(c["fecha"] for c in crono))
    has_hour = any(c.get("hora") for c in crono)
    if len(dates) < 2 and not has_hour:
        return None
    sents = sentences(words, time_offset)

    def _when(c: dict[str, Any]) -> float | None:
        return next((s["t0"] for s in sents if ev.used_in(s["text"], c)), None)
    first = next((c for c in crono if _when(c) is not None), None)
    if first is None:
        return None
    y, m, d = first["fecha"].split("-")
    start = _when(first)
    changes, last, cur = [], start, first
    for c in crono:                                  # fechas siguientes, en orden de fecha y de voz
        t = _when(c)
        if len(changes) >= 2 or t is None or c["fecha"] <= cur["fecha"] or t < last + 2.0:
            continue
        cy, cm, cd = c["fecha"].split("-")
        changes.append({"t": round(t, 3), "day": str(int(cd)), "month": MESES[ev.MESES[int(cm) - 1]],
                        "tail": c.get("hora") or cy, "source_text": ev.text_of(c), "pool_id": c["id"]})
        last, cur = t, c
    end = min(clip_dur, (changes[-1]["t"] + TICKER_HOLD) if changes else start + 12.0)
    month = MESES[ev.MESES[int(m) - 1]]
    tail = first.get("hora") or y
    if end - start < TICKER_MIN:
        return None
    return {"day": str(int(d)), "month": month, "tail": tail, "times": [first["hora"]] if first.get("hora") else [],
            "advance": False, "source_text": ev.text_of(first), "pool_id": first["id"],
            "start": round(start, 3), "duration": round(end - start, 3), "changes": changes}


TICKER_HOLD = 4.0                    # F5f: la fecha nueva queda en pantalla 4 s después del cambio
TICKER_MIN = 2.0                     # el reloj no sale si queda menos de 2 s en pantalla (F29c: también al moverlo)


# ═══════════════════════════════════════════════════════════════
#  F5e — un contador por hecho (517 y «más de 500» son el mismo)
# ═══════════════════════════════════════════════════════════════

_COUNT_NOUNS = r"(personas|reclusos|presos|prisioneros|evacuados|internos|desaparecidos|fugitivos|víctimas|muertos)"
_APPROX = re.compile(r"\b(más de|aproximadamente|alrededor de|cerca de|unos|unas|hasta|casi)\s*$", re.I)
COUNT_SAME_TOL = 0.15                   # dos cifras del mismo conteo: a ±15 %


def count_groups(pool: dict[str, Any]) -> list[dict[str, Any]]:
    """Cifras de personas (≥ 100) que cuentan lo mismo: mismo sustantivo de conteo y a ±15 % (517 reclusos «no
    contabilizados» y «más de 500» prisioneros que no figuraban). La canónica es la PRECISA (sin «más de», «hasta»…);
    si hay varias, la primera del pool. [{"canon": {"id","num","unit","texto"}, "nums": {"517", "500"}}]"""
    rows = []
    for it in pool.get("datos") or []:
        if it.get("tipo") not in ("cifra", "magnitud", "contradiccion"):
            continue
        for m in re.finditer(r"(\d[\d,.]*\d|\d+)\s+(?:\w+\s+)?" + _COUNT_NOUNS, it["texto"], re.I):
            n = int(re.sub(r"[,.]", "", m.group(1)))
            if n < 100:
                continue
            approx = bool(_APPROX.search(it["texto"][:m.start()]))
            rows.append({"id": it["id"], "num": m.group(1), "n": n, "unit": m.group(2).lower(), "approx": approx,
                         "texto": it["texto"], "fuente": it.get("fuente")})
    groups: list[list[dict]] = []
    for r in sorted(rows, key=lambda r: r["n"]):
        g = next((g for g in groups if abs(r["n"] - g[0]["n"]) <= COUNT_SAME_TOL * g[0]["n"]), None)
        (g.append(r) if g is not None else groups.append([r]))
    out = []
    for g in groups:
        if len({r["n"] for r in g}) < 2:
            continue
        canon = next((r for r in g if not r["approx"]), None)
        if canon:
            out.append({"canon": canon, "nums": {r["num"] for r in g} | {str(r["n"]) for r in g}})
    return out


