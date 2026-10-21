"""F5 §3.3: compara las simulaciones del director (plan_only) de v1 y v2 → lab/hyperframes/f5/SIM_v1_v2.md

Por cap y total: recortes (cuántos salen del pool, con fuente o con fecha), datos, veredictos del crítico, reloj,
pregunta de cierre, palabras de peso 3 sin material en pantalla, escenas del proxy.
F5b: tercera columna «v2 F5» (la simulación de F5, respaldada en output/<V2>/_bak_f5b_pre) y un chequeo de las
reglas S1–S5 sobre la v2 nueva (cláusula completa, cronología, mismo hecho / cap siguiente, ícono literal, metros).
Uso: PYTHONIOENCODING=utf-8 python lab/hyperframes/f5/analizar_sims.py
"""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
import sys
sys.path.insert(0, str(ROOT))
SIMS = {"v1": ROOT / "output" / "ba6c3cac-a091-41c0-8dad-afd2f4364747" / "_fase2b_work_f5sim_v1",
        "v2 F5": ROOT / "output" / "ba6c3cac-f5v2" / "_bak_f5b_pre" / "_fase2b_work",
        "v2 F5b": ROOT / "output" / "ba6c3cac-f5v2" / "_bak_f5c_pre" / "_fase2b_work",
        "v2 F5c": ROOT / "output" / "ba6c3cac-f5v2" / "_bak_f5d_pre" / "_fase2b_work",
        "v2": ROOT / "output" / "ba6c3cac-f5v2" / "_fase2b_work"}
SIMS = {k: v for k, v in SIMS.items() if (v / "gfx_plan_ch01.resolved.json").exists()}
STEPS = ROOT / "data" / "scripts" / "_steps" / "ba6c3cac-f5v2"
OUT = Path(__file__).resolve().parent / "SIM_v1_v2.md"
_ORG = re.compile(r"[A-Za-z].*,\s*(19|20)\d\d$")


def _plan(work: Path, cap: str) -> dict:
    return json.loads((work / f"gfx_plan_{cap}.resolved.json").read_text(encoding="utf-8"))["plan"]


def _kicker_kind(k: str) -> str:
    if not k:
        return "sin kicker"
    if _ORG.match(k):
        return "fuente"
    return "fecha" if re.search(r"\d", k) else "otro"


def _intensity(work: Path, cap: str) -> list[dict]:
    f = work / f"gfx_intensity_{cap}.json"
    try:
        return (json.loads(f.read_text(encoding="utf-8")).get("raw") or {}).get("cargas") or []
    except (OSError, ValueError):
        return []


def _shown_words(p: dict) -> str:
    parts = [str(e.get("word", "")) for e in p.get("emphasis") or []]
    parts += [str(a.get("headline", "")) for a in p.get("archive_clippings") or []]
    parts += [str(c.get("text", "")) for c in p.get("callouts") or []]
    return " ".join(parts).lower()


def audit_f5b() -> list[str]:
    """Chequeo de S1–S5 sobre la simulación v2 (F5b), bloque por bloque."""
    from script_engine import evidence as ev
    from script_engine import gfx_pool as gp
    from script_engine.gfx_peak import sentences
    from script_engine.m05_narrative import adjectives
    work = SIMS.get("v2")
    if work is None:
        return []
    pool = json.loads((STEPS / "01_facts_sources.json").read_text(encoding="utf-8"))["evidence_pool"]
    skel = json.loads((STEPS / "01a_skeleton.json").read_text(encoding="utf-8"))
    its = ev.items(pool)
    by_cap = {c["chapter_number"]: set(c.get("evidence_ids") or []) for c in skel["chapters"]}
    imap = gp.literal_icon_map()
    out = {"S1": [], "S2": [], "S3": [], "S4": [], "S5": []}
    shown: list[tuple[str, dict]] = []
    n_arcs = n_icons = 0
    for n in range(1, 8):
        cap = f"ch{n:02d}"
        p = _plan(work, cap)
        words = json.loads((work / f"_sim_{cap}_timestamps.json").read_text(encoding="utf-8"))
        sents = sentences(words, 1.8 if n == 1 else 0.0)
        year = gp._default_year(pool, sorted(by_cap.get(n, [])))
        told = gp.narrated_dates(sents, year)
        for a in p.get("archive_clippings") or []:
            i = a.get("pool_id")
            if not i or i not in its:
                continue
            n_arcs += 1
            it = its[i]
            if a["headline"] not in gp.pool_clause_options(ev.text_of(it)):
                out["S1"].append(f"{cap} «{a['headline']}» [{i}] no es una cláusula completa del dato")
            k = max([j for j, s in enumerate(sents) if s["t0"] <= a["start"] + 0.31] or [0])
            d, when = told[k] if told else None, ev.item_date(it, year)
            if d and when and when > d:
                out["S2"].append(f"{cap} @ {a['start']:.1f}s «{a['headline']}» es del {when}; la voz narra el {d}")
            if i in by_cap.get(n + 1, set()) and i not in by_cap.get(n, set()):
                out["S3"].append(f"{cap} «{a['headline']}» [{i}] es del cap {n + 1} (destripa el cliffhanger)")
        for b in (p.get("archive_clippings") or []) + (p.get("callouts") or []):
            i = b.get("pool_id")
            if i in its:
                twin = next((f"{c} [{j}]" for c, j_it in shown for j in [j_it["id"]] if ev.same_fact(its[i], j_it)), None)
                if twin:
                    out["S3"].append(f"{cap} [{i}] «{b.get('headline') or b.get('text')}» = mismo hecho que {twin}")
                shown.append((cap, its[i]))
        for e in (p.get("emphasis") or []):
            if e.get("icon") and e.get("icon_callout"):
                n_icons += 1
                w = ev.norm(str(e.get("word", "")).lower())
                if w not in imap or adjectives(str(e.get("word", ""))):
                    out["S4"].append(f"{cap} énfasis «{e['word']}» con ícono {e['icon']} (no está en el mapa literal)")
        for a in p.get("archive_clippings") or []:
            if a.get("icon"):
                n_icons += 1
                if not any(re.search(rf"(?<!\w){re.escape(k_)}(?!\w)", ev.norm(a["headline"])) and v_ == a["icon"]
                           for k_, v_ in imap.items()):
                    out["S4"].append(f"{cap} recorte «{a['headline']}» con ícono {a['icon']} sin palabra del mapa")
        texts = [a.get("headline", "") for a in p.get("archive_clippings") or []] + \
                [c.get("text", "") for c in p.get("callouts") or []]
        for k_ in ("water_level", "count_up"):
            if p.get(k_):
                texts.append(f"{p[k_].get('value_text')} {p[k_].get('unit', '')}")
        for t in texts:
            if gp.IMPERIAL.search(str(t)):
                out["S5"].append(f"{cap} «{t}» (unidad no métrica)")
    names = {"S1": "recorte = cláusula completa", "S2": "nunca un hecho posterior a la voz",
             "S3": "un hecho, un bloque; nada del cap siguiente", "S4": "ícono solo por el mapa literal",
             "S5": "en pantalla, unidades métricas"}
    L = ["", "## Chequeo de las reglas de pantalla F5b sobre v2 F5d (S1–S5)", "",
         f"{n_arcs} recortes del pool y {n_icons} íconos en pantalla en los 7 caps.", "", "| regla | fallas | detalle |",
         "|---|---|---|"]
    for k_, v_ in out.items():
        L.append(f"| {k_} {names[k_]} | {len(v_)} | {'<br>'.join(v_) or '—'} |")
    return L


def main() -> None:
    caps = [f"ch{n:02d}" for n in range(1, 8)]
    lines = ["# F5d — Simulación del director (sin render): v1 vs v2", "",
             "Mismas fotos (v1 como proxy). v1 = guion producido con sus 10 verified_facts, simulado con el código de "
             "F5d; «v2 F5», «v2 F5b» y «v2 F5c» = las simulaciones anteriores (respaldadas); v2 = guion F5d con los datos "
             "reservados para pantalla. "
             "Fuente: `gfx_plan_chNN.resolved.json` de cada simulación.", ""]
    tot = {v: Counter() for v in SIMS}
    rows = []
    for cap in caps:
        r = {}
        for v, w in SIMS.items():
            p = _plan(w, cap)
            arcs = p.get("archive_clippings") or []
            kk = Counter(_kicker_kind(a.get("kicker", "")) for a in arcs)
            crit = Counter(x["veredicto"] for x in p.get("critico") or [])
            cargas3 = [c["word"] for c in _intensity(w, cap) if c.get("peso") == 3]
            shown = _shown_words(p)
            sin_mat = [x for x in cargas3 if x.lower() not in shown]
            q = p.get("chapter_question") or {}
            tk = p.get("time_ticker")
            r[v] = {"arcs": arcs, "kk": kk, "crit": crit, "sin_mat": sin_mat, "q": q.get("text"), "tk": tk,
                    "datos": [c.get("text") for c in p.get("callouts") or []], "pool_arcs": sum(1 for a in arcs if a.get("pool_id"))}
            tot[v]["recortes"] += len(arcs)
            tot[v]["recortes_pool"] += r[v]["pool_arcs"]
            tot[v]["kicker_fuente"] += kk["fuente"]
            tot[v]["kicker_fecha"] += kk["fecha"]
            tot[v]["datos"] += len(r[v]["datos"])
            for k_, n_ in crit.items():
                tot[v][f"critico_{k_}"] += n_
            tot[v]["peso3_sin_material"] += len(sin_mat)
            tot[v]["reloj"] += bool(tk)
            tot[v]["pregunta"] += bool(q.get("text"))
        rows.append((cap, r))
    cols = list(SIMS)
    lines += ["## Totales (7 caps)", "", "| | " + " | ".join(cols) + " |", "|---|" + "---|" * len(cols)]
    keys = ["recortes", "recortes_pool", "kicker_fuente", "kicker_fecha", "datos", "critico_suma", "critico_repite",
            "critico_estorba", "critico_error", "reloj", "pregunta", "peso3_sin_material"]
    lab = {"recortes": "recortes en pantalla", "recortes_pool": "recortes que salen del evidence_pool",
           "kicker_fuente": "kicker = fuente (Organización, año)", "kicker_fecha": "kicker = fecha/año",
           "datos": "datos en pantalla", "critico_suma": "crítico: suma", "critico_repite": "crítico: repite",
           "critico_estorba": "crítico: estorba", "critico_error": "crítico: sin veredicto",
           "reloj": "caps con reloj", "pregunta": "caps con pregunta de cierre",
           "peso3_sin_material": "palabras de peso 3 sin material en pantalla"}
    lines += [f"| {lab[k]} | " + " | ".join(str(tot[c][k]) for c in cols) + " |" for k in keys]
    lines += audit_f5b()
    for cap, r in rows:
        lines += ["", f"## {cap}", "", "| | " + " | ".join(cols) + " |", "|---|" + "---|" * len(cols)]
        fmt_arcs = lambda x: "<br>".join(f"«{a.get('headline')}» · {a.get('kicker') or '—'}"  # noqa: E731
                                         + (f" · [{a['pool_id']}]" if a.get("pool_id") else "")
                                         + (f" · ícono {a['icon']}" if a.get("icon") else "")
                                         + (f" · falta ícono {a['icon_missing']}" if a.get("icon_missing") else "")
                                         for a in x["arcs"]) or "—"
        cr = lambda x: ", ".join(f"{k} {n}" for k, n in sorted(x["crit"].items())) or "—"  # noqa: E731
        tkf = lambda x: (f"{x['tk']['day']} {x['tk']['month']} · {x['tk']['tail']}" + (f" [{x['tk']['pool_id']}]" if x['tk'].get('pool_id') else "")) if x["tk"] else "—"  # noqa: E731
        row = lambda name, f: lines.append(f"| {name} | " + " | ".join(f(r[c]) for c in cols) + " |")  # noqa: E731
        row("recortes", fmt_arcs)
        row("datos", lambda x: ", ".join(map(str, x["datos"])) or "—")
        row("crítico", cr)
        row("reloj", tkf)
        row("pregunta", lambda x: x["q"] or "—")
        row("peso 3 sin material", lambda x: ", ".join(x["sin_mat"]) or "—")
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[:22]))


if __name__ == "__main__":
    main()
