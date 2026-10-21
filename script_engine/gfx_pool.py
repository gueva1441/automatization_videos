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
                            out.append(sx)
    return _dedupe(out)


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
        for b in (plan.get("archive_clippings") or []) + (plan.get("callouts") or []):
            if b.get("pool_id"):
                out.add(b["pool_id"])
    return out


def cap_candidates(pool: dict[str, Any], skeleton: dict[str, Any], cap: int, used: set[str]) -> list[str]:
    """F5b S3: los ids del cap y después los del cap ANTERIOR (nunca del siguiente: el cliffhanger no se destripa),
    datos duros y citas, sin los que cuentan un hecho ya mostrado en un cap anterior (mismo id o mismo hecho)."""
    its = ev.items(pool)
    by_cap = {c.get("chapter_number"): c.get("evidence_ids") or [] for c in skeleton.get("chapters") or []}
    ids = list(by_cap.get(cap, [])) + list(by_cap.get(cap - 1, []))
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
                  allowed: list[bool] | None = None) -> dict[str, Any] | None:
    """La oración de la voz que habla de lo mismo que el dato (≥ 2 palabras de contenido en común; 1 si es del cap).
    `allowed`: oraciones donde el dato puede salir (S2: la voz ya llegó a su fecha)."""
    words = ev._content(ev.text_of(it))
    best, score = None, 0
    for k, s in enumerate(sents):
        if allowed is not None and not allowed[k]:
            continue
        sc = len(words & ev._content(s["text"])) + (2 if ev.used_in(s["text"], it) else 0)
        if sc > score:
            best, score = s, sc
    return best if best and score >= (1 if own else 2) else None


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
    own_ids = next((c.get("evidence_ids") or [] for c in skel.get("chapters") or [] if c.get("chapter_number") == n), [])
    own = set(own_ids)
    used = used_ids_before(work_dir, n)
    cands = cap_candidates(pool, skel, n, used)
    sents = sentences(words, time_offset)
    year = _default_year(pool, own_ids)
    told = narrated_dates(sents, year)
    narr = " ".join(str(w.get("word", "")) for w in words)
    dur = scenes[-1].end
    old = [a.get("headline") for a in plan.get("archive_clippings") or []]
    plan["archive_clippings"] = []
    busy = [(float(b["start"]), float(b["start"]) + float(b.get("duration", 2.5)))
            for k in ("callouts", "emphasis") for b in plan.get(k) or []]
    for k, d in (("count_up", 3.7), ("water_level", 4.5), ("evidence_zoom", 2.85), ("chapter_question", 3.0)):
        if plan.get(k) and "start" in plan[k]:
            busy.append((float(plan[k]["start"]), float(plan[k]["start"]) + float(plan[k].get("duration", d))))
    if plan.get("title_card"):
        busy.append((0.0, gfx_rules.title_dur))
    rows, items, placed = [], [], []
    for i in cands:
        if len(plan["archive_clippings"]) >= gfx_rules.archive_max_per_cap:
            break
        it = its[i]
        if any(ev.same_fact(it, p) for p in placed):                       # S3: mismo hecho, un solo bloque
            rows.append({"id": i, "bloque": "recorte", "ahora": None, "motivo": "mismo hecho que otro bloque del cap"})
            continue
        when = ev.item_date(it, year)
        allowed = [d is None or when is None or when <= d for d in told]   # S2: nunca un hecho posterior a la voz
        s = _sentence_for(it, sents, i in own, allowed)
        if s is None:
            later = when and _sentence_for(it, sents, i in own) is not None
            rows.append({"id": i, "bloque": "recorte", "ahora": None,
                         "motivo": f"hecho del {when}, posterior a lo que narra la voz" if later
                         else "la voz no habla de esto en el cap"})
            continue
        sc = scene_at(scenes, s["t0"])
        span = narration_span(words, sc.start, sc.end, time_offset)
        text = ev.text_of(it)
        opts = sorted((f for f in pool_clause_options(text) if adds_something(f, span) and lock_ok(f, text)
                       and _kicker(it, f)), key=lambda f: (_doc_rank(f, span, narr), f))[:3]
        if not opts:
            rows.append({"id": i, "bloque": "recorte", "ahora": None,
                         "motivo": "ninguna cláusula completa (≤ 10 palabras, métrica) suma a la voz con fuente o fecha"})
            continue
        a = max(sc.start + 0.5, s["t0"] - 0.3)
        b = min(a + gfx_rules.archive_dur, dur - 0.3)
        if b - a < gfx_rules.archive_min_sec or not all(b <= x or a >= y for x, y in busy):
            rows.append({"id": i, "bloque": "recorte", "ahora": None, "motivo": f"no entra sin pisar otro bloque @ {a:.1f}s"})
            continue
        blk = {"kicker": _kicker(it, opts[0]), "headline": opts[0], "body": "", "scene_idx": sc.idx, "fact_idx": None,
               "pool_id": i, "fuente": it.get("fuente"), "era_decade": 2000, "start": round(a, 3),
               "duration": round(b - a, 3), "side": getattr(sc, "quiet_side", "right")}
        plan["archive_clippings"].append(blk)
        busy.append((a, b))
        placed.append(it)
        items.append({"blk": blk, "it": it, "options": opts, "span": span})
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
                         "icono_faltante": x["blk"].get("icon_missing"), "opciones": x["options"]})
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
        if not all(t + 2.5 <= x or t >= y for x, y in busy) or len(calls_out) >= 2:
            continue
        sc = scene_at(scenes, t)
        calls_out.append({"text": frag, "start": round(t, 3), "kind": "figure", "duration": 2.5,
                          "side": getattr(sc, "quiet_side", "left"), "fact_idx": None, "pool_id": i,
                          "source": short_source(it.get("fuente"))})
        busy.append((t, t + 2.5))
        placed.append(it)
        rows.append({"id": i, "bloque": "dato", "ahora": frag, "fuente": it.get("fuente")})
    n_old_calls = len(plan.get("callouts") or [])
    plan["callouts"] = sorted(calls_out, key=lambda c: c["start"])
    log.append(f"  pool: recortes {[(x['pool_id'], x['headline'], x['kicker']) for x in plan['archive_clippings']]} "
               f"(antes, de verified_facts: {old}) · datos {[(c['pool_id'], c['text']) for c in plan['callouts']]} "
               f"(antes {n_old_calls}) · candidatos {len(cands)} · ya mostrados en caps anteriores {sorted(used)}")
    return rows


def pool_ticker(ctx: dict[str, Any], words: list[dict], clip_dur: float, time_offset: float = 0.0
                ) -> dict[str, Any] | None:
    """Reloj desde la cronología del cap. Sale solo si el cap avanza de fecha (≥ 2 fechas distintas) o trae hora.
    Muestra la primera fecha (o hora) desde que la voz la nombra hasta que nombra la siguiente."""
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
    nxt = next((c for c in crono if c["fecha"] > first["fecha"] and _when(c) is not None), None)
    start = _when(first)
    end = _when(nxt) if nxt else min(clip_dur, start + 12.0)
    month = MESES[ev.MESES[int(m) - 1]]
    tail = first.get("hora") or y
    if end - start < 2.0:
        return None
    return {"day": str(int(d)), "month": month, "tail": tail, "times": [first["hora"]] if first.get("hora") else [],
            "advance": False, "source_text": ev.text_of(first), "pool_id": first["id"],
            "start": round(start, 3), "duration": round(end - start, 3)}
