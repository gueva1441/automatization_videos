"""F5 §3.3: compara las simulaciones del director (plan_only) de v1 y v2 → lab/hyperframes/f5/SIM_v1_v2.md

Por cap y total: recortes (cuántos salen del pool, con fuente o con fecha), datos, veredictos del crítico, reloj,
pregunta de cierre, palabras de peso 3 sin material en pantalla, escenas del proxy.
Uso: PYTHONIOENCODING=utf-8 python lab/hyperframes/f5/analizar_sims.py
"""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SIMS = {"v1": ROOT / "output" / "ba6c3cac-a091-41c0-8dad-afd2f4364747" / "_fase2b_work_f5sim_v1",
        "v2": ROOT / "output" / "ba6c3cac-f5v2" / "_fase2b_work"}
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


def main() -> None:
    caps = [f"ch{n:02d}" for n in range(1, 8)]
    lines = ["# F5 §3 — Simulación del director (sin render): v1 vs v2", "",
             "Mismo código (F5) y mismas fotos (v1 como proxy). v1 = guion producido con sus 10 verified_facts; v2 = guion "
             "nuevo con evidence_pool. Fuente: `gfx_plan_chNN.resolved.json` de cada simulación.", ""]
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
    lines += ["## Totales (7 caps)", "", "| | v1 | v2 |", "|---|---|---|"]
    keys = ["recortes", "recortes_pool", "kicker_fuente", "kicker_fecha", "datos", "critico_suma", "critico_repite",
            "critico_estorba", "critico_error", "reloj", "pregunta", "peso3_sin_material"]
    lab = {"recortes": "recortes en pantalla", "recortes_pool": "recortes que salen del evidence_pool",
           "kicker_fuente": "kicker = fuente (Organización, año)", "kicker_fecha": "kicker = fecha/año",
           "datos": "datos en pantalla", "critico_suma": "crítico: suma", "critico_repite": "crítico: repite",
           "critico_estorba": "crítico: estorba", "critico_error": "crítico: sin veredicto",
           "reloj": "caps con reloj", "pregunta": "caps con pregunta de cierre",
           "peso3_sin_material": "palabras de peso 3 sin material en pantalla"}
    lines += [f"| {lab[k]} | {tot['v1'][k]} | {tot['v2'][k]} |" for k in keys]
    for cap, r in rows:
        lines += ["", f"## {cap}", "", "| | v1 | v2 |", "|---|---|---|"]
        fmt_arcs = lambda x: "<br>".join(f"«{a.get('headline')}» · {a.get('kicker') or '—'}"  # noqa: E731
                                         + (f" · [{a['pool_id']}]" if a.get("pool_id") else "")
                                         + (f" · ícono {a['icon']}" if a.get("icon") else "")
                                         + (f" · falta ícono {a['icon_missing']}" if a.get("icon_missing") else "")
                                         for a in x["arcs"]) or "—"
        lines.append(f"| recortes | {fmt_arcs(r['v1'])} | {fmt_arcs(r['v2'])} |")
        lines.append(f"| datos | {', '.join(map(str, r['v1']['datos'])) or '—'} | {', '.join(map(str, r['v2']['datos'])) or '—'} |")
        cr = lambda x: ", ".join(f"{k} {n}" for k, n in sorted(x["crit"].items())) or "—"  # noqa: E731
        lines.append(f"| crítico | {cr(r['v1'])} | {cr(r['v2'])} |")
        tkf = lambda x: (f"{x['tk']['day']} {x['tk']['month']} · {x['tk']['tail']}" + (f" [{x['tk']['pool_id']}]" if x['tk'].get('pool_id') else "")) if x["tk"] else "—"  # noqa: E731
        lines.append(f"| reloj | {tkf(r['v1'])} | {tkf(r['v2'])} |")
        lines.append(f"| pregunta | {r['v1']['q'] or '—'} | {r['v2']['q'] or '—'} |")
        lines.append(f"| peso 3 sin material | {', '.join(r['v1']['sin_mat']) or '—'} | {', '.join(r['v2']['sin_mat']) or '—'} |")
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[:22]))


if __name__ == "__main__":
    main()
