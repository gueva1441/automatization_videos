"""
gfx_fragments.py — Fragmento literal más impactante (F4b §2). El LLM ELIGE UN NÚMERO, nunca escribe.

Para cada recorte y dato ya ubicados en el cap:
    opciones = fragmentos LITERALES de ≤ 8 palabras: el recorte, del fact y de la narración del tramo que comparte una
               palabra con el fact (documento con fuente); el dato, del fact
               y de la narración alrededor (±4 s), ≤ 1 palabra más que hoy y con todas sus cifras y nombres propios;
               cortados por cláusula (comas/puntos) y sin palabras funcionales en los bordes. La opción 1 es la de hoy
               (titular determinista / texto del director), así "fuera de la lista" = comportamiento de hoy.
    dato     las opciones tienen que contener el mismo núcleo (la cifra o el nombre) que el texto de hoy.
    llamada  UNA por cap (todos los bloques juntos); respuesta [{id, n}]; n inválido → 1.
    después  el fragmento elegido fija la categoría del bloque (léxico del cap): si tiene ícono aprobado, el recorte /
             dato sale "con ícono". Dedupe: un titular ya usado en un cap anterior no se repite (vuelve al de hoy).
El candado literal se vuelve a pasar después (gfx_layer).

F4c (doctrina del director, tokens doc_clippings / callout_no_repeat):
    R6 recorte  es un DOCUMENTO: opciones solo del fact (nunca de la narración), y cada una suma algo que la voz del
                tramo no dice (cifra, fecha, nombre, «informaron/según…» o una palabra de contenido que no suena).
                Kicker obligatorio: fuente del fact → año del fact → fecha del fact → el único año que dice la voz del
                cap. Sin opción que sume o sin kicker → el recorte se quita (nunca un pie de foto).
    F4d        las opciones del recorte son CLÁUSULAS COMPLETAS del fact (clause_options: ≤ 10 palabras, terminan
                donde termina la cláusula —coma, punto o «mientras/cuando/…»—, empiezan en sustantivo, nombre o
                artículo y tienen sujeto), ordenadas por aporte (_doc_rank); Flash elige entre las DOC_TOP mejores.
    R7 dato     no repite: si el texto del dato suena LITERAL en la voz (±4 s) se quita; una cifra en dígitos que la
                voz dice en letras (precisión extra) se queda.
"""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any, Callable

MAX_OPTIONS = 12
EDGE_STOP = {"de", "del", "la", "las", "el", "los", "un", "una", "unos", "unas", "y", "o", "e", "en", "a", "al", "que",
             "por", "con", "para", "sin", "se", "su", "sus", "lo", "como", "según", "hasta", "durante", "pero", "mientras",
             "haber", "había", "habían", "ser", "sido", "estar", "fue", "fueron", "era", "eran", "es", "muy", "más"}
SYSTEM = ("Sos editor de un documental de misterio. Para cada bloque gráfico elegís, de una lista NUMERADA de fragmentos "
          "copiados del guion, el que más impacto tiene en pantalla. Criterio: impacto emocional > concreción > "
          "brevedad. Respondés SOLO JSON con números; nunca escribís texto.")
EXAMPLES = ("«agua putrefacta» es mejor que «agua hasta el pecho»",
            "«6,500 almas» es mejor que «aproximadamente 6,500 personas»",
            "«cadáveres flotando» es mejor que «se veían objetos en el agua»",
            "«celdas herméticamente cerradas» es mejor que «en ese momento»",
            "«nadie abrió las celdas» es mejor que «las autoridades informaron»")
SCHEMA: dict[str, Any] = {"type": "OBJECT", "properties": {"elecciones": {"type": "ARRAY", "items": {
    "type": "OBJECT", "properties": {"id": {"type": "STRING"}, "n": {"type": "INTEGER"}}, "required": ["id", "n"]}}},
    "required": ["elecciones"]}


# bordes que dejan la frase colgada: verbos conjugados / gerundios / infinitivos (los participios -ado/-ido sí van:
# "celdas cerradas"); y una fecha nunca se parte ("tocó tierra el 29")
_VERB_EDGE = re.compile(r"(ó|aron|ieron|eron|ando|endo|iendo|aba|aban|ía|ían|ar|er|ir|amos|aron|an|en)$")
_KEEP_EDGE = {"orleans", "katrina", "pies", "metros", "personas", "almas", "presos", "prisioneros", "agua", "aguas",
              "tren", "orden", "joven", "volumen", "crimen", "origen", "imagen", "examen", "hombre", "mujeres"}
_MONTHS = r"(?:enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|setiembre|octubre|noviembre|diciembre)"
_DATE_RE = re.compile(rf"\b\d{{1,2}} de {_MONTHS}(?: de \d{{4}})?", re.IGNORECASE)


def _verb_edge(w: str) -> bool:
    t = _tok(w)
    return bool(t) and not t[:1].isdigit() and t not in _KEEP_EDGE and not w[:1].isupper() and len(t) > 3         and bool(_VERB_EDGE.search(t))


def _splits_date(clause: list[str], s: int, e: int) -> bool:
    """¿La ventana [s, e) corta una fecha a la mitad?"""
    text = " ".join(clause)
    for m in _DATE_RE.finditer(text):
        d0 = len(text[:m.start()].split())
        d1 = d0 + len(m.group(0).split())
        inside = max(0, min(e, d1) - max(s, d0))
        # F4c R6: «el 29 de agosto» sin «de 2005» vale (el año va al kicker); partir el día del mes, no
        if 0 < inside < d1 - d0 and not (d1 - d0 == 5 and s <= d0 and e == d0 + 3):
            return True
    return False


def _tok(w: str) -> str:
    return re.sub(r"^[¿¡\"'«“(]+|[.,;:!?…\"'»”)]+$", "", str(w)).lower()


def _clauses(text: str) -> list[list[str]]:
    text = re.sub(r"\s+", " ", str(text)).strip()
    # los paréntesis también cortan: «15 pies (4.6 metros)» no puede dar «15 pies 4.6»
    return [c.split() for c in re.split(r"[,.;:!?…](?=\s|$)|\s[—–-]\s|[()]", text) if c.strip()]


def _trim(ws: list[str]) -> list[str]:
    ws = [w.strip("¿¡\"'«»“”()") for w in ws]
    while ws and (ws[0].lower() in EDGE_STOP or not ws[0] or _verb_edge(ws[0])):
        ws = ws[1:]
    while ws and (ws[-1].lower() in EDGE_STOP or not ws[-1] or _verb_edge(ws[-1])):
        ws = ws[:-1]
    return ws


def fragments(text: str, max_words: int = 8, must: str | None = None, key_words: set[str] | None = None) -> list[str]:
    """Fragmentos literales (contiguos) de ≤ max_words palabras, por cláusula. Con `must`, solo los que contienen ese
    núcleo. Orden: los que traen una palabra de carga (key_words) primero, después los más cortos."""
    out: list[str] = []
    seen: set[str] = set()
    for ws in _clauses(text):
        n = len(ws)
        for L in range(2, max_words + 1):
            for s in range(0, max(1, n - L + 1)):
                if _splits_date(ws, s, s + L):
                    continue
                frag = _trim(ws[s:s + L])
                if len(frag) < 2 or len(frag) > max_words:
                    continue
                f = " ".join(frag)
                if f.lower() in seen or (must and must.lower() not in f.lower()):
                    continue
                if not re.search(r"[A-Za-zÁÉÍÓÚáéíóúñÑ\d]{3,}", f):
                    continue
                seen.add(f.lower())
                out.append(f)
    kw = key_words or set()
    out.sort(key=lambda f: (-sum(_tok(w) in kw for w in f.split()), len(f.split()), f))
    return out


def _content(text: str) -> set[str]:
    return {_tok(w)[:5] for w in str(text).split() if len(_tok(w)) >= 4 and _tok(w) not in EDGE_STOP}


def literal_in(frag: str, text: str) -> bool:
    norm = lambda s: re.sub(r"\s+", " ", re.sub(r"[¿¡\"'«»“”()]", "", s)).lower()  # noqa: E731
    return norm(frag) in norm(text)


def core_token(text: str) -> str | None:
    """Núcleo de un dato: la cifra (con su formato) o la palabra con mayúscula más larga."""
    m = re.search(r"\d[\d.,]*", text)
    if m:
        return m.group(0).rstrip(".,")
    caps = [w.strip(".,;:") for w in text.split() if w[:1].isupper()]
    return max(caps, key=len) if caps else None


def narration_span(words: list[dict], t0: float, t1: float, time_offset: float = 0.0) -> str:
    return " ".join(str(w["word"]) for w in words if t0 - 0.05 <= float(w["start"]) + time_offset < t1)


REPORT_WORDS = {"informaron", "informó", "informe", "según", "reportaron", "denunciaron", "declararon", "testigos",
                "testimonio", "relataron", "afirmaron", "documentó", "registraron"}


def _root(w: str) -> str:
    import unicodedata
    t = "".join(c for c in unicodedata.normalize("NFD", _tok(w)) if unicodedata.category(c) != "Mn")
    return t[:5]


_VAGUE = {"algunos", "algunas", "casos", "otros", "otras", "todos", "todas", "mismo", "misma", "cosas", "parte", "partes",
          "veces", "manera", "forma"}


def novelty(frag: str, span: str) -> tuple[list[str], list[str]]:
    """F4c R6: (elementos duros, palabras nuevas) que el fragmento suma a la voz del tramo. Duros = fecha, cifra,
    nombre propio o «informaron/según…»; palabras nuevas = contenido ≥ 5 letras cuya raíz no suena en el tramo."""
    said = {_tok(w) for w in span.split()}
    said_roots = {_root(w) for w in span.split() if len(_tok(w)) >= 4}
    hard: list[str] = []
    dates = [m.group(0) for m in _DATE_RE.finditer(frag) if not literal_in(m.group(0), span)]
    hard += [f"fecha «{d}»" for d in dates]
    in_date = {t for d in dates for t in d.split()}
    for d in re.findall(r"\d[\d.,]*\d|\d", frag):
        if d not in said and d.rstrip(".,") not in said and d not in in_date:
            hard.append(f"cifra «{d}»")
    ws = frag.split()
    soft: list[str] = []
    for k, w in enumerate(ws):
        t = _tok(w)
        if t in REPORT_WORDS and t not in said:
            hard.append(f"fuente «{t}»")
        elif k > 0 and w[:1].isupper() and len(t) >= 3 and t not in said:
            hard.append(f"nombre «{w.strip('.,;:')}»")
        elif (len(t) >= 5 and t not in EDGE_STOP and t not in _VAGUE and t not in in_date and not t[:1].isdigit()
              and not _VERB_EDGE.search(t) and _root(w) not in said_roots):
            soft.append(f"«{t}»")
    return hard, soft


def adds_something(frag: str, span: str) -> str | None:
    """F4c R6: lo que el fragmento suma a la voz del tramo (para el log), o None si solo repite."""
    hard, soft = novelty(frag, span)
    return (hard or [f"palabra {x}" for x in soft] or [None])[0]


def _doc_rank(frag: str, span: str, cap_narr: str = "") -> tuple[int, int, int]:
    """Orden de los recortes por aporte: más elementos duros (fecha, cifra, nombre, fuente), después más palabras que
    no suenan en TODO el cap (lo que de verdad suma: «aguas residuales»), después la cláusula más completa (≤ 10)."""
    hard, soft = novelty(frag, span)
    roots = {_root(w) for w in cap_narr.split() if len(_tok(w)) >= 4}
    cap_new = [x for x in soft if _root(x.strip("«»")) not in roots]
    return (-len(hard), -len(cap_new), -len(frag.split()))


DOC_TOP = 3                          # F4d: Flash elige entre las 3 opciones que más aportan
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
    if not re.match(r"[A-Za-zÁÉÍÓÚÑáéíóúñ]", w) or re.search(r"[\"'«»“”]$", w):
        return False
    if t in _ARTICLES or w[:1].isupper():
        return True
    if t in EDGE_STOP or t in _VAGUE or t in _IRREG_PART or t.endswith("mente"):
        return False
    return len(t) >= 4 and not _verb_edge(w) and not _PARTICIPLE.search(t)


def _has_subject(ws: list[str]) -> bool:
    return any(len(_tok(w)) >= 4 and not _tok(w)[:1].isdigit() and _tok(w) not in _MONTH_SET and _tok(w) not in EDGE_STOP
               for w in ws)


def clause_options(fact: str, max_words: int = DOC_MAX_WORDS) -> list[str]:
    """F4d: cláusulas completas del fact (y sus colas que arrancan en sustantivo/nombre/artículo), ≤ max_words.
    Una fecha al final puede perder «de AAAA» (el año va al kicker). Literales: conservan las comillas del fact."""
    text = re.sub(r"\s+", " ", str(fact)).strip()
    out: list[str] = []
    for part in re.split(r"[,.;:!?…()](?=\s|$)|\s[—–-]\s", text):
        ws = part.split()
        cl: list[list[str]] = [[]]
        for w in ws:                                   # «mientras/cuando/…» abren otra cláusula
            if _tok(w) in _SUBORD and cl[-1]:
                cl.append([])
            cl[-1].append(w)
        for c in cl:
            for st in range(len(c)):
                frag = c[st:]
                vs = [frag]
                if (len(frag) >= 5 and re.fullmatch(r"\d{4}", _tok(frag[-1])) and _tok(frag[-2]) == "de"
                        and _tok(frag[-3]) in _MONTH_SET):
                    vs.append(frag[:-2])
                for v in vs:
                    if 2 <= len(v) <= max_words and _start_ok(v[0]) and _has_subject(v):
                        out.append(" ".join(v))
    return _dedupe(out)


def lock_ok(frag: str, fact: str) -> bool:
    """El fragmento pasa el candado literal (misma normalización que gfx_literal_lock: sin sacar comillas)."""
    from script_engine.gfx_literal_lock import normalize
    return bool(frag.strip()) and normalize(frag) in normalize(fact)


def doc_kicker(fact: str, source: str, headline: str, narration: str) -> str:
    """F4c R6: kicker obligatorio del recorte. Fuente del fact → año del fact → fecha del fact → el único año que dice
    la voz del cap (el del hecho). Nunca lo que ya dice el titular. "" = sin kicker posible."""
    from script_engine.gfx_director import _YEAR_RE
    low = headline.lower()
    cands = [source]
    y = _YEAR_RE.search(fact)
    cands.append(y.group(1) if y else "")
    d = _DATE_RE.search(fact)
    cands.append(d.group(0) if d else "")
    ys = set(_YEAR_RE.findall(narration))
    cands.append(next(iter(ys)) if len(ys) == 1 else "")
    return next((c for c in cands if c and c.lower() not in low), "")


def enforce_documents(plan: dict[str, Any], *, ctx: dict[str, Any], words: list[dict], scenes: list[Any],
                      time_offset: float, log: list[str]) -> list[dict[str, Any]]:
    """F4c R6 antes de que Flash elija: cada recorte queda con kicker obligatorio y titular que sume; si no se puede,
    se quita. Devuelve las filas para la tabla (las quitadas con ahora=None)."""
    facts, fsrc = ctx["facts"], ctx.get("fact_source") or {}
    narr = " ".join(str(w.get("word", "")) for w in words)
    kept, rows = [], []
    for a in plan.get("archive_clippings") or []:
        fi, cur = a.get("fact_idx"), a.get("headline", "")
        if fi is None:
            kept.append(a)
            continue
        sc = next((s for s in scenes if s.idx == a.get("scene_idx")), None)
        span = narration_span(words, sc.start, sc.end, time_offset) if sc else ""
        opts = [f for f in clause_options(facts[fi])
                if adds_something(f, span) and lock_ok(f, facts[fi]) and doc_kicker(facts[fi], fsrc.get(fi, ""), f, narr)]
        head = min(opts, key=lambda f: _doc_rank(f, span, narr)) if opts else ""
        kick = doc_kicker(facts[fi], fsrc.get(fi, ""), head, narr) if head else ""
        if not head or not kick:
            why = ("ningún fragmento del fact suma a la voz (con kicker posible y literal)" if not head
                   else "sin fuente, año ni fecha para el kicker")
            log.append(f"  recorte quitado (R6, {why}): «{cur}»")
            rows.append({"bloque": f"recorte@{a.get('start')}", "antes": cur, "ahora": None, "motivo": why})
            continue
        if head != cur:
            log.append(f"  recorte (R6): «{cur}» → «{head}» (suma {adds_something(head, span)})")
        a["headline"], a["kicker"] = head, kick
        if a.get("body") and (literal_in(head, a["body"]) or literal_in(a["body"], head)):
            a["body"] = ""
        kept.append(a)
    plan["archive_clippings"] = kept
    return rows


def drop_repeated_callouts(plan: dict[str, Any], *, words: list[dict], time_offset: float,
                           log: list[str]) -> list[dict[str, Any]]:
    """F4c R7: el dato que la voz dice LITERAL en su tramo (±4 s) se quita (tercer texto igual en pantalla)."""
    kept, rows = [], []
    for c in plan.get("callouts") or []:
        t = float(c.get("start", 0.0))
        span = narration_span(words, t - 4.0, t + 4.0, time_offset)
        if c.get("text") and literal_in(c["text"], span):
            log.append(f"  dato quitado (R7, la voz lo dice en ese tramo): «{c['text']}»")
            rows.append({"bloque": f"dato@{t:.1f}", "antes": c["text"], "ahora": None, "motivo": "la voz lo dice"})
            continue
        kept.append(c)
    plan["callouts"] = kept
    return rows


def build_items(plan: dict[str, Any], *, facts: list[str], words: list[dict], scenes: list[Any], time_offset: float,
                key_words: set[str], documents: bool = False,
                fact_source: dict[int, str] | None = None) -> list[dict[str, Any]]:
    """Bloques del plan con sus opciones (la 1 = la de hoy). documents=True (F4c R6): las del recorte solo del fact y
    sumando algo a la voz del tramo."""
    items = []
    narr = " ".join(str(w.get("word", "")) for w in words)
    fsrc = fact_source or {}
    for i, a in enumerate(plan.get("archive_clippings") or []):
        fi, cur = a.get("fact_idx"), a.get("headline", "")
        if fi is None or not cur:
            continue
        sc = next((s for s in scenes if s.idx == a.get("scene_idx")), None)
        span = narration_span(words, sc.start, sc.end, time_offset) if sc else ""
        # F4b E15: el recorte es un documento con fuente → de la narración del tramo solo entran fragmentos que
        # comparten una palabra de contenido con el fact («agua putrefacta» ↔ «El agua dentro…»; no «quinientas vidas»)
        fw = _content(facts[fi])
        nar = [] if documents else [f for f in fragments(span, 8, key_words=key_words) if _content(f) & fw]
        opts = [cur] + [f for f in sorted(fragments(facts[fi], 8, key_words=key_words) + nar,
                                          key=lambda f: (-sum(_tok(w) in key_words for w in f.split()), len(f.split()), f))
                        if f.lower() != cur.lower() and (not documents or (
                            adds_something(f, span) and lock_ok(f, facts[fi])
                            and doc_kicker(facts[fi], fsrc.get(fi, ""), f, narr)))]
        if documents:                # F4d: cláusulas completas del fact, las DOC_TOP que más aportan
            opts = sorted((f for f in clause_options(facts[fi]) if adds_something(f, span) and lock_ok(f, facts[fi])
                           and doc_kicker(facts[fi], fsrc.get(fi, ""), f, narr)),
                          key=lambda f: (_doc_rank(f, span, narr), f))[:DOC_TOP] or [cur]
        items.append({"id": f"recorte{i}", "kind": "archive", "idx": i, "options": _dedupe(opts)[:MAX_OPTIONS],
                      "fact": facts[fi], "span": span, "documents": documents})
    for i, c in enumerate(plan.get("callouts") or []):
        cur, fi = c.get("text", ""), c.get("fact_idx")
        core = core_token(cur)
        if not cur or core is None or fi is None or c.get("kind") == "year" or _DATE_RE.search(cur):
            continue                                            # años y fechas: el sello ya es el dato justo
        top = min(5, len(cur.split()) + 1)                      # un dato es corto: como mucho 1 palabra más que hoy
        t = float(c.get("start", 0.0))
        span = narration_span(words, t - 4.0, t + 4.0, time_offset)
        keep = [w.strip(".,;:") for w in cur.split() if w[:1].isdigit() or w[:1].isupper()]   # cifras y nombres
        opts = [cur] + [f for f in fragments(f"{facts[fi]}. {span}", top, must=core, key_words=key_words)
                        if f.lower() != cur.lower() and all(k in f for k in keep)]
        if len(opts) > 1:
            items.append({"id": f"dato{i}", "kind": "callout", "idx": i, "options": _dedupe(opts)[:MAX_OPTIONS],
                          "fact": facts[fi], "span": span})
    return items


def _dedupe(opts: list[str]) -> list[str]:
    seen, out = set(), []
    for o in opts:
        if o.lower() not in seen:
            seen.add(o.lower())
            out.append(o)
    return out


def build_prompt(items: list[dict[str, Any]]) -> str:
    lines = ["Ejemplos del criterio:", *[f"- {e}" for e in EXAMPLES], "",
             "Para cada bloque, elegí UN número de su lista (el texto que se verá en pantalla):", ""]
    for it in items:
        lines.append(f"[{it['id']}] {'titular de recorte de diario' if it['kind'] == 'archive' else 'dato en pantalla'}")
        if it.get("documents"):      # F4c R6: el recorte es un documento → que sume lo que la voz no dice
            lines.append(f"  La voz en ese tramo ya dice: «{it['span']}». El recorte es un DOCUMENTO: elegí el que más "
                         "suma lo que la voz NO dice (fecha, cifra, nombre, fuente, detalle concreto); nunca uno que solo repite.")
            for n, o in enumerate(it["options"], start=1):
                hard, soft = novelty(o, it["span"])
                tag = ", ".join(hard + soft[:3])
                lines.append(f"  {n}. {o}" + (f"   (suma: {tag})" if tag else ""))
        else:
            lines += [f"  {n}. {o}" for n, o in enumerate(it["options"], start=1)]
        lines.append("")
    lines.append('Devolvé {"elecciones": [{"id": "...", "n": número}, ...]} con un elemento por bloque.')
    return "\n".join(lines)


def category_of(text: str, moods: dict[str, dict[str, Any]]) -> tuple[str | None, str | None]:
    """(categoría, palabra) del léxico del cap presente en el fragmento (la de más peso). F4c R4: peso ≥ 2."""
    best = (1, None, None)
    for w in text.split():
        t = _tok(w)
        for cat, m in moods.items():
            wt = int((m.get("triggers") or {}).get(t, 0))
            if wt > best[0]:
                best = (wt, cat, t)
    return best[1], best[2]


def category_icon(cat: str, word: str | None, moods: dict[str, dict[str, Any]]) -> str | None:
    """Ícono de la palabra si el léxico lo mapea; si no, el ícono más común de la categoría (veneno → calavera)."""
    iw = (moods.get(cat) or {}).get("icon_words") or {}
    if word and word in iw:
        return iw[word]
    common = Counter(iw.values()).most_common(1)
    return common[0][0] if common else None


def used_headlines_before(work_dir: Path, chapter_number: int) -> set[str]:
    out: set[str] = set()
    for f in sorted(Path(work_dir).glob("gfx_plan_ch*.resolved.json")):
        m = re.search(r"ch(\d+)", f.name)
        if not m or int(m.group(1)) >= chapter_number:
            continue
        try:
            for a in (json.loads(f.read_text(encoding="utf-8")).get("plan") or {}).get("archive_clippings") or []:
                out.add(str(a.get("headline", "")).lower())
        except (OSError, ValueError):
            continue
    return out


def choose_fragments(plan: dict[str, Any], *, ctx: dict[str, Any], words: list[dict], scenes: list[Any],
                     time_offset: float, moods: dict[str, dict[str, Any]], work_dir: Path, cap: str,
                     call: Callable[..., dict] | None = None, log: list[str] | None = None) -> list[dict[str, Any]]:
    """Aplica las elecciones al plan (in place). Devuelve la tabla antes/después para el reporte."""
    log = log if log is not None else []
    from gfx_config import gfx_rules
    docs = bool(gfx_rules.doc_clippings)
    pre = enforce_documents(plan, ctx=ctx, words=words, scenes=scenes, time_offset=time_offset, log=log) if docs else []
    key_words = {w for m in moods.values() for w in (m.get("triggers") or {})}
    items = build_items(plan, facts=ctx["facts"], words=words, scenes=scenes, time_offset=time_offset, key_words=key_words,
                        documents=docs, fact_source=ctx.get("fact_source"))
    if not items:
        return pre
    cache = Path(work_dir) / f"gfx_fragments_{cap}.json"
    prompt = build_prompt(items)
    raw = None
    if cache.exists():
        try:
            c = json.loads(cache.read_text(encoding="utf-8"))
            raw = c.get("raw") if c.get("prompt") == prompt else None
        except (OSError, ValueError):
            raw = None
    if raw is None:
        if call is None:
            from gemini_helpers import call_flash_json as call
        try:
            raw = call(prompt, system_instruction=SYSTEM, response_schema=SCHEMA, thinking_budget=0,
                       description=f"gfx_fragments {cap}")
            cache.write_text(json.dumps({"prompt": prompt, "raw": raw}, ensure_ascii=False, indent=1), encoding="utf-8")
        except Exception as e:  # noqa: BLE001 — sin LLM → los textos de hoy
            log.append(f"  fragmentos: Flash falló ({type(e).__name__}) → textos de hoy")
            return pre
    picks = {str(x.get("id")): x.get("n") for x in (raw or {}).get("elecciones") or [] if isinstance(x, dict)}
    used = used_headlines_before(work_dir, ctx["chapter_number"])
    table = []
    for it in items:
        n = picks.get(it["id"])
        n = n if isinstance(n, int) and 1 <= n <= len(it["options"]) else 1
        new, old = it["options"][n - 1], it["options"][0]
        src_ok = literal_in(new, it["fact"]) or literal_in(new, it["span"])
        if not src_ok or (it["kind"] == "archive" and new.lower() in used):
            new = old
        blk = (plan["archive_clippings"] if it["kind"] == "archive" else plan["callouts"])[it["idx"]]
        if it["kind"] == "archive":
            blk["headline"] = new
            if it.get("documents"):          # F4c R6: el kicker se recalcula con el titular elegido (nunca repetido)
                blk["kicker"] = doc_kicker(it["fact"], (ctx.get("fact_source") or {}).get(blk.get("fact_idx"), ""), new,
                                           " ".join(str(w.get("word", "")) for w in words))
        else:
            blk["text"] = new
        cat, word = category_of(new, moods)
        ico = None
        if cat:
            from script_engine.gfx_icons import icon_svg
            ico = category_icon(cat, word, moods)
            if ico and icon_svg(ico) is not None and not blk.get("icon"):
                blk["icon"] = ico
                blk["category"] = cat
        table.append({"bloque": it["id"], "antes": old, "ahora": new, "categoria": cat, "icono": blk.get("icon"),
                      "opciones": len(it["options"])})
    log.append("  fragmentos: " + "; ".join(f"{r['bloque']} «{r['antes']}» → «{r['ahora']}»" for r in table))
    return pre + table
