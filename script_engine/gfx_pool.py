"""
gfx_pool.py — La pantalla se alimenta del evidence_pool (F5 §2). Todo detrás de `if pool`: un guion sin pool sigue
con verified_facts exactamente como antes.

    pool_sources()          textos del pool que el candado literal acepta (datos, citas, cronología, lugares, nombres,
                            fuentes cortas «Organización, año»)
    cap_candidates()        ids del pool para los recortes/datos de un cap: los suyos (skeleton) y los de los caps
                            ±1, sin los que ya salieron en pantalla en un cap anterior (dedupe por id)
    plan_pool_documents()   recortes: cláusula completa del dato que SUMA a la voz del tramo (gfx_fragments), kicker
                            = fuente del dato → su fecha → sin recorte; Flash elige entre las 3 mejores. Datos: la
                            cifra del pool en el instante en que la voz la nombra (R7 la saca si la voz la dice
                            literal). Nunca un texto de la narración.
    content_icon()          ícono del recorte/dato por el TEMA del dato, nunca por la palabra de la voz
                            (huracán → espiral, generadores → rayo tachado, cifras de personas → sin ícono)
    pool_ticker()           reloj desde la cronología del cap: con hora si la hay; si el cap no avanza de fecha, no sale
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Callable

from script_engine import evidence as ev

# (raíces en el texto del dato, ícono). Los que no están en el set aprobado se anotan y quedan sin ícono: espiral y
# rayo tachado se generan con el pipeline de los 12 (F5 es sin imágenes).
CONTENT_ICONS: tuple[tuple[tuple[str, ...], str], ...] = (
    (("huracan", "tormenta", "ciclon"), "espiral"),
    (("generador", "electric", "energia", "apagon", "sin luz"), "rayo_tachado"),
    (("demanda", "jurado", "indemniz", "juicio", "tribunal", "sentencia", "carta de hallazgos"), "balanza"),
    (("cadaver", "cuerpos", "muert", "fallec"), "calavera"),
    (("aguas residuales", "contamin", "enfermedad", "infecc"), "biohazard"),
    (("registro", "listas", "contabiliz", "desaparec"), "ojo_tachado"),
    (("celda", "encerr", "atrapad"), "candado"),
    (("agua", "inund", "dique", "pies", "metros"), "gota"),
)
_PEOPLE = ("personas", "reclusos", "presos", "prisioneros", "niños", "ninos", "hombres", "mujeres", "internos",
           "víctimas", "victimas", "almas", "turistas", "testimonios")
_YEAR = re.compile(r"\b(1[5-9]\d\d|20\d\d)\b")


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


def content_icon(it: dict[str, Any], available: set[str] | frozenset[str]) -> tuple[str | None, str | None]:
    """(ícono, ícono_faltante). Cifra de personas → sin ícono. Por tema del texto del dato, nunca por la voz."""
    txt = ev.norm(ev.text_of(it))
    if it.get("tipo") in ("cifra", "magnitud") and re.search(r"\d[\d.,]*\s+(?:\w+\s+)?(" + "|".join(_PEOPLE) + r")\b",
                                                             txt):
        return None, None
    for roots, icon in CONTENT_ICONS:
        if any(r in txt for r in roots):
            return (icon, None) if icon in available else (None, icon)
    return None, None


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
    its = ev.items(pool)
    by_cap = {c.get("chapter_number"): c.get("evidence_ids") or [] for c in skeleton.get("chapters") or []}
    ids = list(by_cap.get(cap, [])) + [i for n in (cap - 1, cap + 1) for i in by_cap.get(n, [])]
    out = []
    for i in dict.fromkeys(ids):
        it = its.get(i)
        if it and i not in used and (ev.is_hard(it) or it["_kind"] == "citas"):
            out.append(i)
    return out


def _sentence_for(it: dict[str, Any], sents: list[dict[str, Any]], own: bool) -> dict[str, Any] | None:
    """La oración de la voz que habla de lo mismo que el dato (≥ 2 palabras de contenido en común; 1 si es del cap)."""
    words = ev._content(ev.text_of(it))
    best, score = None, 0
    for s in sents:
        k = len(words & ev._content(s["text"])) + (2 if ev.used_in(s["text"], it) else 0)
        if k > score:
            best, score = s, k
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
    own = set(next((c.get("evidence_ids") or [] for c in skel.get("chapters") or [] if c.get("chapter_number") == n), []))
    used = used_ids_before(work_dir, n)
    cands = cap_candidates(pool, skel, n, used)
    sents = sentences(words, time_offset)
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
    rows, items = [], []
    for i in cands:
        if len(plan["archive_clippings"]) >= gfx_rules.archive_max_per_cap:
            break
        it = its[i]
        s = _sentence_for(it, sents, i in own)
        if s is None:
            rows.append({"id": i, "bloque": "recorte", "ahora": None, "motivo": "la voz no habla de esto en el cap"})
            continue
        sc = scene_at(scenes, s["t0"])
        span = narration_span(words, sc.start, sc.end, time_offset)
        text = ev.text_of(it)
        opts = sorted((f for f in clause_options(text) if adds_something(f, span) and lock_ok(f, text)
                       and _kicker(it, f)), key=lambda f: (_doc_rank(f, span, narr), f))[:3]
        if not opts:
            rows.append({"id": i, "bloque": "recorte", "ahora": None,
                         "motivo": "ninguna cláusula suma a la voz con fuente o fecha"})
            continue
        a = max(sc.start + 0.5, s["t0"] - 0.3)
        b = min(a + gfx_rules.archive_dur, dur - 0.3)
        if b - a < gfx_rules.archive_min_sec or not all(b <= x or a >= y for x, y in busy):
            rows.append({"id": i, "bloque": "recorte", "ahora": None, "motivo": f"no entra sin pisar otro bloque @ {a:.1f}s"})
            continue
        ico, missing = content_icon(it, ICON_WHITELIST)
        blk = {"kicker": _kicker(it, opts[0]), "headline": opts[0], "body": "", "scene_idx": sc.idx, "fact_idx": None,
               "pool_id": i, "fuente": it.get("fuente"), "era_decade": 2000, "start": round(a, 3),
               "duration": round(b - a, 3), "side": getattr(sc, "quiet_side", "right"),
               **({"icon": ico} if ico else {}), **({"icon_missing": missing} if missing else {})}
        plan["archive_clippings"].append(blk)
        busy.append((a, b))
        items.append({"blk": blk, "it": it, "options": opts, "span": span})
    # Flash elige entre las 3 mejores (misma mecánica que gfx_fragments en modo documento)
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
        anc = next((a for a in ev.anchors(it) if re.search(r"\d", a)), None)
        if not anc:
            continue
        num = anc.split()[0]
        k = next((j for j in range(len(words))
                  if ev.literal_in(num, " ".join(str(x.get("word", "")) for x in words[j:j + 4]))
                  and not ev.literal_in(num, " ".join(str(x.get("word", "")) for x in words[j + 1:j + 4]))), None)
        frag = next((f for f in clause_options(ev.text_of(it), 5) if num in f), None)
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
