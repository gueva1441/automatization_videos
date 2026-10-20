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
_DATE_RE = re.compile(rf"\d{{1,2}} de {_MONTHS}(?: de \d{{4}})?", re.IGNORECASE)


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
        if 0 < inside < d1 - d0:
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


def build_items(plan: dict[str, Any], *, facts: list[str], words: list[dict], scenes: list[Any], time_offset: float,
                key_words: set[str]) -> list[dict[str, Any]]:
    """Bloques del plan con sus opciones (la 1 = la de hoy)."""
    items = []
    for i, a in enumerate(plan.get("archive_clippings") or []):
        fi, cur = a.get("fact_idx"), a.get("headline", "")
        if fi is None or not cur:
            continue
        sc = next((s for s in scenes if s.idx == a.get("scene_idx")), None)
        span = narration_span(words, sc.start, sc.end, time_offset) if sc else ""
        # F4b E15: el recorte es un documento con fuente → de la narración del tramo solo entran fragmentos que
        # comparten una palabra de contenido con el fact («agua putrefacta» ↔ «El agua dentro…»; no «quinientas vidas»)
        fw = _content(facts[fi])
        nar = [f for f in fragments(span, 8, key_words=key_words) if _content(f) & fw]
        opts = [cur] + [f for f in sorted(fragments(facts[fi], 8, key_words=key_words) + nar,
                                          key=lambda f: (-sum(_tok(w) in key_words for w in f.split()), len(f.split()), f))
                        if f.lower() != cur.lower()]
        items.append({"id": f"recorte{i}", "kind": "archive", "idx": i, "options": _dedupe(opts)[:MAX_OPTIONS],
                      "fact": facts[fi], "span": span})
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
        lines += [f"  {n}. {o}" for n, o in enumerate(it["options"], start=1)]
        lines.append("")
    lines.append('Devolvé {"elecciones": [{"id": "...", "n": número}, ...]} con un elemento por bloque.')
    return "\n".join(lines)


def category_of(text: str, moods: dict[str, dict[str, Any]]) -> tuple[str | None, str | None]:
    """(categoría, palabra) del léxico del cap presente en el fragmento (la de más peso)."""
    best = (0, None, None)
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
    key_words = {w for m in moods.values() for w in (m.get("triggers") or {})}
    items = build_items(plan, facts=ctx["facts"], words=words, scenes=scenes, time_offset=time_offset, key_words=key_words)
    if not items:
        return []
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
            return []
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
    return table
