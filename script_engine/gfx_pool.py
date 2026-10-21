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
    from script_engine.gfx_fragments import EDGE_STOP, _tok
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
    from script_engine.gfx_fragments import _ARTICLES, _tok
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
    from script_engine.gfx_fragments import _tok
    return any(re.match(r"\$?\d", w) and (k == 0 or (c[k - 1][:1].islower() and _tok(c[k - 1]) not in {"y", "e"}))
               for k, w in enumerate(c))


def _cut_ok(c: list[str], e: int, vk: list[int]) -> bool:
    """¿Se puede cortar la cláusula antes de c[e]? En un borde de frase y con el verbo ya dicho:
    - preposición, «que», «y»… (o «de» + artículo: «evacuados | de la Prisión») DESPUÉS de verbo + objeto: «… no
      finalizó | hasta el viernes» no corta (el verbo pide su complemento);
    - una fecha («fallaron | el 29 de agosto») puede cortar justo después del verbo: la fecha va al kicker;
    - nunca dentro de «más de 50» / «menos de…»."""
    from script_engine.gfx_fragments import _ARTICLES, _tok
    from script_engine.gfx_fragments import EDGE_STOP
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
    from script_engine.gfx_fragments import DOC_MAX_WORDS, EDGE_STOP, _MONTH_SET, _SUBORD, _dedupe, _has_subject, \
        _start_ok, _tok
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
    from script_engine.gfx_fragments import EDGE_STOP, _tok
    ws = cut.split()
    return cut if len(ws) >= 3 and _tok(ws[-1]) not in EDGE_STOP and _has_verb(ws) is not None else None


# ═══════════════════════════════════════════════════════════════
#  S2 — cronología: la fecha que viene narrando la voz
# ═══════════════════════════════════════════════════════════════

def _default_year(pool: dict[str, Any], ids: list[str]) -> str | None:
    its = ev.items(pool)
    ys = [str(its[i].get("fecha"))[:4] for i in ids if i in its and re.match(r"\d{4}", str(its[i].get("fecha") or ""))]
    ys = ys or [str(c.get("fecha"))[:4] for c in pool.get("cronologia") or [] if c.get("fecha")]
    return max(set(ys), key=ys.count) if ys else None


def narrated_dates(sents: list[dict[str, Any]], year: str | None) -> list[str | None]:
    """Por oración, la fecha (ISO) que la voz viene narrando: la última fecha con día dicha hasta esa oración
    (inclusive). Antes de la primera, la primera que dice el cap (la voz todavía no avanzó). None si no dice fechas."""
    seen = [ev.spoken_dates(s["text"], year) for s in sents]
    first = next((d[0] for d in seen if d), None)
    out, cur = [], None
    for d in seen:
        cur = d[-1] if d else cur
        out.append(cur or first)
    return out


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


def _sentence_for(it: dict[str, Any], sents: list[dict[str, Any]], own: bool,
                  allowed: list[bool] | None = None, reserved: bool = False) -> dict[str, Any] | None:
    """La oración de la voz que habla de lo mismo que el dato (≥ 2 palabras de contenido en común; 1 si es del cap).
    `allowed`: oraciones donde el dato puede salir (S2: la voz ya llegó a su fecha). F5e: un dato RESERVADO PARA
    PANTALLA es del cap aunque la voz no lo nombre (no lo dice a propósito): va en la oración más cercana en tema, o
    en la segunda del cap si ninguna comparte palabras."""
    words = ev._content(ev.text_of(it))
    best, score = None, 0
    for k, s in enumerate(sents):
        if allowed is not None and not allowed[k]:
            continue
        sc = len(words & ev._content(s["text"])) + (2 if ev.used_in(s["text"], it) else 0)
        if sc > score:
            best, score = s, sc
    if reserved and best is None:
        ok = [s for k, s in enumerate(sents) if allowed is None or allowed[k]]
        return ok[1] if len(ok) > 1 else (ok[0] if ok else None)
    return best if best and score >= (1 if own else 2) else None


def _free_slot(a: float, sc: Any, dur: float, busy: list[tuple[float, float]], length: float,
               min_len: float, step: float = 0.5) -> tuple[float, float] | None:
    """F5e: la primera ventana libre desde `a` dentro de la escena (corriéndose de a 0.5 s), de `length` s (mínimo
    `min_len`). None si no hay."""
    t = a
    while t + min_len <= min(sc.end, dur - 0.3) + 1e-6:
        b = min(t + length, dur - 0.3)
        if b - t >= min_len and all(b <= x or t >= y for x, y in busy):
            return round(t, 3), round(b, 3)
        t += step
    return None


HARD_KINDS = ("title_card", "chapter_question", "water_level")   # F5f: lo único ante lo que cede un reservado


def _busy_blocks(plan: dict[str, Any]) -> list[dict[str, Any]]:
    """F5f: bloques ya puestos en el plan, con nombre: {a, b, kind, label, obj}."""
    from gfx_config import gfx_rules
    out = []
    for k in ("callouts", "emphasis"):
        for x in plan.get(k) or []:
            a = float(x["start"])
            out.append({"a": a, "b": a + float(x.get("duration", 2.5)), "kind": k,
                        "label": f"{'dato' if k == 'callouts' else 'sello'} «{x.get('text') or x.get('word')}»", "obj": x})
    for k, d, name in (("count_up", 3.7, "contador"), ("water_level", 4.5, "nivel de agua"),
                       ("evidence_zoom", 2.85, "zoom"), ("chapter_question", 3.0, "pregunta"),
                       ("icon_array", 3.0, "íconos")):
        x = plan.get(k)
        if x and "start" in x:
            a = float(x["start"])
            out.append({"a": a, "b": a + float(x.get("duration", d)), "kind": k,
                        "label": f"{name} «{x.get('value_text') or x.get('text') or x.get('anchor') or ''}»".replace(" «»", ""),
                        "obj": x})
    if plan.get("title_card"):
        out.append({"a": 0.0, "b": gfx_rules.title_dur, "kind": "title_card", "label": "título", "obj": plan["title_card"]})
    return out


def _hits(a: float, b: float, busy: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [x for x in busy if x["a"] < b and x["b"] > a]


def displace(plan: dict[str, Any], victims: list[dict[str, Any]], busy: list[dict[str, Any]]) -> list[str]:
    """F5f: saca del plan (y de busy) los bloques blandos que pisa un reservado. Devuelve sus nombres."""
    gone = []
    for v in victims:
        if v["kind"] in ("callouts", "emphasis"):
            plan[v["kind"]] = [x for x in plan.get(v["kind"]) or [] if x is not v["obj"]]
        elif v["kind"] in ("count_up", "evidence_zoom", "icon_array"):
            plan[v["kind"]] = None
        else:
            continue
        if v in busy:
            busy.remove(v)
        gone.append(v["label"])
    return gone


DISPLACE_COST = {"emphasis": 1, "callouts": 2, "icon_array": 2, "evidence_zoom": 3, "count_up": 5}


def reserved_slot(a: float, sc: Any, dur: float, busy: list[dict[str, Any]], gap_busy: list[tuple[float, float]],
                  length: float, min_len: float, step: float = 0.5) -> tuple[tuple[float, float] | None, list[dict[str, Any]]]:
    """F5f: ventana del reservado. Primero sin pisar nada (corriéndose dentro de la escena); si no hay, la que no pisa
    título, pregunta, nivel de agua, la cita ni otro recorte (± el aire entre recortes) y desplaza lo MENOS valioso
    (sello < dato < zoom < contador; empate: la más cercana a su oración), en la escena hacia adelante y hacia atrás; si
    en la escena no entra, cruzando el corte (± un recorte: el reservado no cede ante un corte de escena)."""
    all_iv = [(x["a"], x["b"]) for x in busy] + gap_busy
    slot = _free_slot(a, sc, dur, all_iv, length, min_len)
    if slot is not None:
        return slot, []
    hard_k = HARD_KINDS + ("quote_card", "recorte")
    hard = [(x["a"], x["b"]) for x in busy if x["kind"] in hard_k] + gap_busy
    lo, hi = max(0.0, min(a, sc.start + 0.5) - length), min(dur - 0.3, max(a, sc.end) + length)   # ± un recorte
    best = None
    t = lo
    while t + min_len <= hi + 1e-6:
        for ln in (length, min_len):                     # de 6 s o, si así desplaza menos, del mínimo (4 s)
            b = min(t + ln, hi)
            if b - t >= min_len and all(b <= x or t >= y for x, y in hard):
                soft = [x for x in _hits(t, b, busy) if x["kind"] not in hard_k]
                out_scene = max(0.0, b - sc.end) + max(0.0, sc.start - t)
                key = (out_scene > 0, sum(DISPLACE_COST.get(x["kind"], 1) for x in soft), -(b - t), abs(t - a))
                if best is None or key < best[0]:
                    best = (key, (round(t, 3), round(b, 3)), soft)
        t += step
    if best is None:
        return None, []
    return best[1], best[2]


_NUM = re.compile(r"\d[\d.,]*\d|\d")


def figure_echo(headline: str, words: list[dict], t: float, time_offset: float, sec: float) -> str | None:
    """F5f: la cifra del titular que la voz dice a ±sec del recorte (un año no cuenta). None si ninguna."""
    near = " ".join(str(w.get("word", "")) for w in words
                    if abs(float(w.get("start", 0.0)) + time_offset - t) <= sec)
    for m in _NUM.finditer(headline):
        num = m.group(0)
        if re.fullmatch(r"(1[5-9]|20)\d\d", num):
            continue
        if ev.literal_in(num, near):
            return num
    return None


def _kicker(it: dict[str, Any], headline: str) -> str:
    """F5: fuente del dato → su fecha (literal en el texto, o el año) → "" (sin recorte)."""
    from script_engine.gfx_fragments import _DATE_RE
    low = headline.lower()
    cands = [short_source(it.get("fuente"))]
    d = _DATE_RE.search(ev.text_of(it))
    cands.append(d.group(0) if d else "")
    y = _YEAR.search(ev.text_of(it)) or _YEAR.search(str(it.get("fecha") or ""))
    cands.append(y.group(1) if y else "")
    return next((c for c in cands if c and c.lower() not in low), "")


def plan_pool_documents(plan: dict[str, Any], *, ctx: dict[str, Any], words: list[dict], scenes: list[Any],
                        time_offset: float, work_dir: Path, cap: str, log: list[str],
                        call: Callable[..., dict] | None = None) -> list[dict[str, Any]]:
    """Recortes y datos del cap salen del pool (reemplaza los de verified_facts). Devuelve filas para el reporte."""
    from gfx_config import gfx_rules
    from script_engine.gfx_fragments import _doc_rank, adds_something, clause_options, lock_ok, narration_span
    from script_engine.gfx_icons import ICON_WHITELIST
    from script_engine.gfx_peak import sentences
    from script_engine.gfx_project import scene_at
    pool, skel = ctx["pool"], ctx.get("skeleton_all") or {}
    its = ev.items(pool)
    n = ctx["chapter_number"]
    ch_n = next((c for c in skel.get("chapters") or [] if c.get("chapter_number") == n), {})
    own_ids = list(ch_n.get("evidence_ids") or [])
    reserved = set(ch_n.get("pantalla_ids") or [])
    own = set(own_ids) | reserved                                       # F5d: los de pantalla son del cap
    used = used_ids_before(work_dir, n)
    cands = cap_candidates(pool, skel, n, used)
    sents = sentences(words, time_offset)
    year = _default_year(pool, own_ids)
    told = narrated_dates(sents, year)
    narr = " ".join(str(w.get("word", "")) for w in words)
    dur = scenes[-1].end
    old = [a.get("headline") for a in plan.get("archive_clippings") or []]
    plan["archive_clippings"] = []
    blocks = _busy_blocks(plan)
    rows, items, placed = [], [], []
    q = plan_pool_quote(plan, ctx=ctx, words=words, scenes=scenes, time_offset=time_offset, busy=blocks,
                        cands=list(dict.fromkeys(list(reserved) + own_ids)), used=used, log=log)
    if q:
        rows.append(q)
        if plan.get("quote_card"):
            placed.append(its[plan["quote_card"]["pool_id"]])
    water_used = _water_used(work_dir, n)
    gap = gfx_rules.archive_min_gap_sec
    for i in cands:
        if len(plan["archive_clippings"]) >= gfx_rules.archive_max_per_cap:
            break
        it = its[i]
        if plan.get("quote_card") and plan["quote_card"].get("pool_id") == i:
            continue
        if i in reserved and not water_used and _is_water_height(it):
            rows.append({"id": i, "bloque": "recorte", "ahora": None, "motivo": "va como nivel de agua (dato reservado de altura)"})
            continue
        if any(ev.same_fact(it, p) for p in placed):                       # S3: mismo hecho, un solo bloque
            rows.append({"id": i, "bloque": "recorte", "ahora": None, "motivo": "mismo hecho que otro bloque del cap"})
            continue
        when = ev.item_date(it, year)
        allowed = [d is None or when is None or when <= d for d in told]   # S2: nunca un hecho posterior a la voz
        s = _sentence_for(it, sents, i in own, allowed, reserved=i in reserved)
        if s is None:
            later = when and _sentence_for(it, sents, i in own) is not None
            rows.append({"id": i, "bloque": "recorte", "ahora": None,
                         "motivo": f"hecho del {when}, posterior a lo que narra la voz" if later
                         else "la voz no habla de esto en el cap"})
            continue
        sc = scene_at(scenes, s["t0"])
        span = narration_span(words, sc.start, sc.end, time_offset)
        text = ev.text_of(it)
        # G2/F5e: en pantalla, hasta archive_head_max_words_pool (12) palabras; > 8 baja el cuerpo (archive_head_px).
        # Una cláusula más larga no se corta: no hay recorte
        opts = sorted((f for f in pool_clause_options(text, gfx_rules.archive_head_max_words_pool)
                       if adds_something(f, span) and lock_ok(f, text)
                       and _kicker(it, f)), key=lambda f: (_doc_rank(f, span, narr), f))[:3]
        if not opts:
            rows.append({"id": i, "bloque": "recorte", "ahora": None,
                         "motivo": "ninguna cláusula completa (≤ 12 palabras, métrica) suma a la voz con fuente o fecha"})
            continue
        a = max(sc.start + 0.5, s["t0"] - 0.3)
        # F5e: si choca, se corre dentro de la escena (de a 0.5 s) antes de rendirse. F5f: con aire entre recortes; un
        # reservado desplaza lo blando y solo cede ante título, pregunta y nivel de agua
        gap_busy = [(x["a"] - gap, x["b"] + gap) for x in blocks if x["kind"] == "recorte"]
        if i in reserved:
            slot, victims = reserved_slot(a, sc, dur, blocks, gap_busy, gfx_rules.archive_dur, gfx_rules.archive_min_sec)
        else:
            slot, victims = _free_slot(a, sc, dur, [(x["a"], x["b"]) for x in blocks] + gap_busy, gfx_rules.archive_dur,
                                       gfx_rules.archive_min_sec), []
        if slot is None:
            hit = _hits(a, a + gfx_rules.archive_dur, blocks)
            near = [x for x in blocks if x["kind"] == "recorte" and x["a"] - gap < a + gfx_rules.archive_dur and x["b"] + gap > a]
            why = [x["label"] for x in (hit if i not in reserved else [h for h in hit if h["kind"] in HARD_KINDS + ("quote_card", "recorte")])]
            why += [f"{x['label']} (menos de {gap:.0f} s)" for x in near if x["label"] not in why]
            rows.append({"id": i, "bloque": "recorte", "ahora": None,
                         "motivo": f"no entra sin pisar otro bloque @ {a:.1f}s (escena {sc.start:.1f}–{sc.end:.1f}s): "
                                   + (", ".join(dict.fromkeys(why)) or "la escena se termina antes")})
            continue
        a, b = slot
        echo = None
        keep_opts = []
        for f in opts:
            e = figure_echo(f, words, a, time_offset, gfx_rules.archive_figure_echo_sec)
            if e:
                echo = echo or e
            else:
                keep_opts.append(f)
        if not keep_opts:
            rows.append({"id": i, "bloque": "recorte", "ahora": None,
                         "motivo": f"repite la cifra {echo} que la voz dice a ±{gfx_rules.archive_figure_echo_sec:.0f} s"})
            continue
        opts = keep_opts
        gone = displace(plan, victims, blocks) if victims else []
        if gone:
            log.append(f"  pool: reservado {i} @ {a:.1f}s desplaza {gone}")
        blk = {"kicker": _kicker(it, opts[0]), "headline": opts[0], "body": "", "scene_idx": sc.idx, "fact_idx": None,
               "pool_id": i, "fuente": it.get("fuente"), "era_decade": 2000, "start": round(a, 3),
               "duration": round(b - a, 3), "side": getattr(sc, "quiet_side", "right"),
               **({"reserved": True} if i in reserved else {})}
        plan["archive_clippings"].append(blk)
        blocks.append({"a": a, "b": b, "kind": "recorte", "label": f"recorte {i} «{opts[0]}»", "obj": blk})
        placed.append(it)
        items.append({"blk": blk, "it": it, "options": opts, "span": span, "desplaza": gone})
    # Flash elige entre las 3 mejores (misma mecánica que gfx_fragments en modo documento)
    moods = ctx.get("moods")
    if items:
        from script_engine.gfx_fragments import SCHEMA, SYSTEM
        prompt_lines = ["Para cada recorte de diario elegí UN número: el que más suma lo que la voz NO dice.", ""]
        for k, x in enumerate(items):
            prompt_lines.append(f"[recorte{k}] La voz dice: «{x['span']}»")
            prompt_lines += [f"  {j}. {o}" for j, o in enumerate(x["options"], start=1)]
        prompt = "\n".join(prompt_lines + ["", 'Devolvé {"elecciones": [{"id": "recorte0", "n": 1}, …]}'])
        cache = Path(work_dir) / f"gfx_pool_docs_{cap}.json"
        raw = None
        try:
            c = json.loads(cache.read_text(encoding="utf-8")) if cache.exists() else {}
            raw = c.get("raw") if c.get("prompt") == prompt else None
        except (OSError, ValueError):
            raw = None
        if raw is None:
            if call is None:
                from gemini_helpers import call_flash_json as call
            try:
                raw = call(prompt, system_instruction=SYSTEM, response_schema=SCHEMA, thinking_budget=0,
                           description=f"gfx_pool_docs {cap}")
                cache.write_text(json.dumps({"prompt": prompt, "raw": raw}, ensure_ascii=False, indent=1), encoding="utf-8")
            except Exception as e:  # noqa: BLE001 — sin Flash: la que más aporta
                log.append(f"  pool: Flash falló ({type(e).__name__}) → recorte = la cláusula que más aporta")
                raw = {}
        picks = {str(x.get("id")): x.get("n") for x in (raw or {}).get("elecciones") or [] if isinstance(x, dict)}
        for k, x in enumerate(items):
            nn = picks.get(f"recorte{k}")
            nn = nn if isinstance(nn, int) and 1 <= nn <= len(x["options"]) else 1
            x["blk"]["headline"] = x["options"][nn - 1]
            x["blk"]["kicker"] = _kicker(x["it"], x["blk"]["headline"])
            ico, missing = content_icon(x["it"], ICON_WHITELIST, moods, x["blk"]["headline"])
            x["blk"].pop("icon", None)
            x["blk"].pop("icon_missing", None)
            if ico:
                x["blk"]["icon"] = ico
            if missing:
                x["blk"]["icon_missing"] = missing
            rows.append({"id": x["it"]["id"], "bloque": "recorte", "ahora": x["blk"]["headline"],
                         "kicker": x["blk"]["kicker"], "fuente": x["it"].get("fuente"), "icono": x["blk"].get("icon"),
                         "icono_faltante": x["blk"].get("icon_missing"), "opciones": x["options"],
                         **({"reservado": True, "desplaza": x["desplaza"]} if x["blk"].get("reserved") else {})})
    # datos: la cifra del pool donde la voz la nombra (nunca la narración); R7 saca los que la voz dice literal
    calls_out = []
    for c in plan.get("callouts") or []:
        if c.get("pool_id"):
            calls_out.append(c)
    for i in cands:
        it = its[i]
        if it["_kind"] != "datos" or it.get("tipo") not in ("cifra", "magnitud") or any(
                x.get("pool_id") == i for x in plan["archive_clippings"]):
            continue
        if any(ev.same_fact(it, p) for p in placed):                       # S3
            continue
        anc = next((a for a in ev.anchors(it) if re.search(r"\d", a) and not IMPERIAL.search(a)), None)   # S5
        if not anc:
            continue
        num = anc.split()[0]
        k = next((j for j in range(len(words))
                  if ev.literal_in(num, " ".join(str(x.get("word", "")) for x in words[j:j + 4]))
                  and not ev.literal_in(num, " ".join(str(x.get("word", "")) for x in words[j + 1:j + 4]))), None)
        frag = next((f for f in clause_options(ev.text_of(it), 5) if num in f and not IMPERIAL.search(f)), None)
        if k is None or not frag:
            continue
        t = float(words[k]["start"]) + time_offset
        if _hits(t, t + 2.5, [x for x in blocks if x["kind"] != "callouts" or x["obj"] in calls_out]) \
                or len(calls_out) >= 2:
            continue
        sc = scene_at(scenes, t)
        calls_out.append({"text": frag, "start": round(t, 3), "kind": "figure", "duration": 2.5,
                          "side": getattr(sc, "quiet_side", "left"), "fact_idx": None, "pool_id": i,
                          "source": short_source(it.get("fuente"))})
        blocks.append({"a": t, "b": t + 2.5, "kind": "callouts", "label": f"dato «{frag}»", "obj": calls_out[-1]})
        placed.append(it)
        rows.append({"id": i, "bloque": "dato", "ahora": frag, "fuente": it.get("fuente")})
    n_old_calls = len(plan.get("callouts") or [])
    plan["callouts"] = sorted(calls_out, key=lambda c: c["start"])
    for r in rows:                                   # F5f: por qué no entra cada uno, con el bloque que choca
        if r.get("ahora") is None and r.get("motivo") and r["id"] in reserved | {(plan.get("quote_card") or {}).get("pool_id")}:
            log.append(f"  pool: reservado {r['id']} fuera — {r['motivo']}")
    log.append(f"  pool: recortes {[(x['pool_id'], x['headline'], x['kicker']) for x in plan['archive_clippings']]} "
               f"(antes, de verified_facts: {old}) · datos {[(c['pool_id'], c['text']) for c in plan['callouts']]} "
               f"(antes {n_old_calls}) · candidatos {len(cands)} · ya mostrados en caps anteriores {sorted(used)}")
    return rows


def _water_used(work_dir: Path, n: int) -> bool:
    from script_engine.gfx_peak import water_used_before
    return water_used_before(work_dir, n)


def _is_water_height(it: dict[str, Any]) -> bool:
    from script_engine.gfx_peak import _METRIC_H, _WATER_CTX
    t = ev.text_of(it)
    return bool(_METRIC_H.search(t) and _WATER_CTX.search(t))


def _spoken_at(text: str, words: list[dict], time_offset: float) -> tuple[float, float] | None:
    """(inicio, fin) de la voz diciendo `text` literal (las 3 primeras y las 2 últimas palabras en orden)."""
    from script_engine.gfx_fragments import _tok
    want = [_tok(w) for w in text.split() if _tok(w)]
    toks = [_tok(str(w.get("word", ""))) for w in words]
    if len(want) < 3:
        return None
    for j in range(len(toks) - 2):
        if toks[j:j + 3] == want[:3]:
            for k in range(j + 2, min(len(toks) - 1, j + len(want) + 6)):
                if toks[k - 1:k + 1] == want[-2:]:
                    return float(words[j]["start"]) + time_offset, float(words[k].get("end", words[k]["start"])) + time_offset
            return float(words[j]["start"]) + time_offset, float(words[j]["start"]) + time_offset + 5.0
    return None


def plan_pool_quote(plan: dict[str, Any], *, ctx: dict[str, Any], words: list[dict], scenes: list[Any],
                    time_offset: float, busy: list[dict[str, Any]], cands: list[str], used: set[str],
                    log: list[str]) -> dict[str, Any] | None:
    """F5f: bloque `quote_card` (in place): la primera cita del cap (reservados y propios) que no salió antes, entera y
    LITERAL (≤ quote_max_words) con su autor; 4–5 s desde que la voz la dice (si no la dice, desde su oración), sobre
    la foto oscurecida. Prioridad de reservado: desplaza sellos, datos, contador y zoom; cede ante título, pregunta y
    nivel de agua. Devuelve la fila del reporte (o None si el cap no tiene citas)."""
    from gfx_config import gfx_rules
    from script_engine.gfx_peak import sentences
    plan["quote_card"] = None
    its = ev.items(ctx.get("pool"))
    qs = [i for i in cands if i in its and its[i]["_kind"] == "citas" and i not in used]
    if not qs:
        return None
    dur = scenes[-1].end
    fail = None
    for i in qs:
        it = its[i]
        text = re.sub(r"\s+", " ", ev.text_of(it)).strip()
        if not it.get("autor"):
            fail = {"id": i, "bloque": "cita", "ahora": None, "motivo": "la cita no tiene autor"}
            continue
        if len(text.split()) < gfx_rules.quote_min_words:
            fail = {"id": i, "bloque": "cita", "ahora": None,
                    "motivo": f"{len(text.split())} palabras (mínimo {gfx_rules.quote_min_words}): no es un bloque de cita"}
            continue
        if len(text.split()) > gfx_rules.quote_max_words:
            fail = {"id": i, "bloque": "cita", "ahora": None,
                    "motivo": f"{len(text.split())} palabras (tope {gfx_rules.quote_max_words}); no se corta una cita"}
            continue
        said = _spoken_at(text, words, time_offset)
        if said is None:
            s = _sentence_for(it, sentences(words, time_offset), True, reserved=True)
            if s is None:
                fail = {"id": i, "bloque": "cita", "ahora": None, "motivo": "la voz no habla de esto en el cap"}
                continue
            said = (float(s["t0"]), float(s["t1"]))
        length = max(gfx_rules.quote_min_sec, min(gfx_rules.quote_dur, said[1] - said[0]))
        hard = [(x["a"], x["b"]) for x in busy if x["kind"] in HARD_KINDS + ("recorte",)]
        win = type("W", (), {"start": said[0], "end": said[0] + 3.0 + length})()  # se corre hasta 3 s, no más
        slot = _free_slot(said[0], win, dur, hard, length, gfx_rules.quote_min_sec, step=0.25)
        if slot is None:
            why = [x["label"] for x in _hits(said[0], said[0] + length, busy) if x["kind"] in HARD_KINDS + ("recorte",)]
            fail = {"id": i, "bloque": "cita", "ahora": None,
                    "motivo": f"no entra @ {said[0]:.1f}s: choca con {', '.join(why) or 'el final del cap'}"}
            continue
        a, b = slot
        gone = displace(plan, [x for x in _hits(a, b, busy) if x["kind"] not in HARD_KINDS + ("recorte",)], busy)
        plan["quote_card"] = {"text": text, "author": it["autor"], "start": round(a, 3), "duration": round(b - a, 3),
                              "pool_id": i, "reserved": True}
        busy.append({"a": a, "b": b, "kind": "quote_card", "label": f"cita {i}", "obj": plan["quote_card"]})
        log.append(f"  pool: cita {i} «{text[:60]}…» — {it['autor']} @ {a:.1f}s ({b - a:.1f} s) · desplaza {gone or 'nada'}")
        return {"id": i, "bloque": "cita", "ahora": text, "autor": it["autor"], "desplaza": gone}
    return fail


def enforce_reserved(plan: dict[str, Any], log: list[str]) -> list[str]:
    """F5f (al final del plan, después del pico, el zoom y la pregunta): un reservado (recorte reservado o cita) desplaza
    lo blando que se le haya puesto encima después; si lo pisa título, pregunta o nivel de agua, el reservado cede."""
    busy = _busy_blocks(plan)
    out: list[str] = []
    res = [("archive_clippings", x) for x in plan.get("archive_clippings") or [] if x.get("reserved")]
    if plan.get("quote_card"):
        res.append(("quote_card", plan["quote_card"]))
    for key, r in res:
        a, b = float(r["start"]), float(r["start"]) + float(r.get("duration", 5.0))
        hits = _hits(a, b, busy)
        hard = [h for h in hits if h["kind"] in HARD_KINDS]
        if hard:
            if key == "quote_card":
                plan["quote_card"] = None
            else:
                plan["archive_clippings"] = [x for x in plan["archive_clippings"] if x is not r]
            out.append(f"{r.get('pool_id')} cede ante {[h['label'] for h in hard]}")
            continue
        # la palabra del pico se queda si el reservado ES el bloque del pico (va del otro lado, como siempre)
        soft = [h for h in hits if not (h["kind"] == "emphasis" and h["obj"].get("peak_word") and r.get("peak"))]
        gone = displace(plan, soft, busy)
        if gone:
            out.append(f"{r.get('pool_id')} desplaza {gone}")
    if out:
        log.append(f"  reservados: {out}")
    return out


def pool_ticker(ctx: dict[str, Any], words: list[dict], clip_dur: float, time_offset: float = 0.0
                ) -> dict[str, Any] | None:
    """Reloj desde la cronología del cap. Sale solo si el cap avanza de fecha (≥ 2 fechas distintas) o trae hora.
    Muestra la primera fecha (o hora) desde que la voz la nombra. F5f: cuando la voz nombra la fecha siguiente, el
    reloj CAMBIA de fecha con animación (`changes`, hasta 2) y la sostiene TICKER_HOLD s; antes terminaba ahí."""
    from script_engine.gfx_peak import MESES, sentences
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
    if end - start < 2.0:
        return None
    return {"day": str(int(d)), "month": month, "tail": tail, "times": [first["hora"]] if first.get("hora") else [],
            "advance": False, "source_text": ev.text_of(first), "pool_id": first["id"],
            "start": round(start, 3), "duration": round(end - start, 3), "changes": changes}


TICKER_HOLD = 4.0                    # F5f: la fecha nueva queda en pantalla 4 s después del cambio


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


def pool_count_up(plan: dict[str, Any], *, ctx: dict[str, Any], words: list[dict], time_offset: float,
                  log: list[str]) -> None:
    """F5e (in place): un hecho contado con varias cifras se anima UNA vez, con la cifra precisa, en el primer cap cuya
    voz la dice. En ese cap el contador es la canónica (reemplaza a uno del mismo hecho); en los demás caps se saca
    cualquier contador o dato de ese hecho. El dedupe por hecho nunca deja el hecho sin su contador."""
    from gfx_config import gfx_rules
    pool = ctx.get("pool") or {}
    n = ctx["chapter_number"]
    chs = sorted(ctx.get("chapters") or [], key=lambda c: c.get("chapter_number", 0))
    for g in count_groups(pool):
        c = g["canon"]
        home = next((ch.get("chapter_number") for ch in chs if ev.literal_in(c["num"], ch.get("narration") or "")), None)
        cu = plan.get("count_up") or {}
        same = re.sub(r"[,.]", "", str(cu.get("value_text") or "")) in {re.sub(r"[,.]", "", x) for x in g["nums"]}
        if n != home:
            if cu and same:
                plan["count_up"] = None
                log.append(f"  contador {cu.get('value_text')}: mismo hecho que {c['num']} (se anima en el cap {home})")
            plan["callouts"] = [x for x in plan.get("callouts") or []
                                if not any(ev.literal_in(v, x.get("text", "")) for v in g["nums"])]
            continue
        if cu and not same:
            log.append(f"  contador {c['num']} {c['unit']}: el cap ya tiene otro contador ({cu.get('value_text')})")
            continue
        k = next((j for j in range(len(words))
                  if ev.literal_in(c["num"], " ".join(str(x.get("word", "")) for x in words[j:j + 3]))
                  and not ev.literal_in(c["num"], " ".join(str(x.get("word", "")) for x in words[j + 1:j + 3]))), None)
        if k is None:
            continue
        t = round(float(words[k]["start"]) + time_offset, 3)
        plan["count_up"] = {"value_text": c["num"], "unit": c["unit"], "start": t,
                            "duration": round(gfx_rules.count_dur + gfx_rules.count_hold_sec, 3), "fact_idx": None,
                            "source": short_source(c.get("fuente")), "pool_id": c["id"]}
        plan["callouts"] = [x for x in plan.get("callouts") or []
                            if not any(ev.literal_in(v, x.get("text", "")) for v in g["nums"])]
        log.append(f"  contador del hecho: {c['num']} {c['unit']} [{c['id']}] @ {t:.1f}s (mismo hecho: "
                   f"{sorted(g['nums'])})")
