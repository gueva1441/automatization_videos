"""F5f: tabla por cap de lo que salió en pantalla (plan resuelto del render en _fase2b_work) y lista de lo que la
simulación (_sim_gfx) prometía y no salió. Imprime markdown para F5f_REPORT.md.
Uso: PYTHONIOENCODING=utf-8 python lab/hyperframes/f5/tabla_f5f.py ch02 ch05 ch06 ch07
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "output" / "ba6c3cac-f5v2"
WORK, SIM = OUT / "_fase2b_work", OUT / "_sim_gfx"
CRIT_KIND = {"recorte": "recorte", "cita": "cita", "sello": "sello", "icono": "sello", "contador": "contador",
             "nivel_agua": "nivel de agua", "zoom": "zoom", "dato": "dato"}


def _plan(d: Path, cap: str) -> dict:
    p = d / f"gfx_plan_{cap}.resolved.json"
    return json.loads(p.read_text(encoding="utf-8"))["plan"] if p.exists() else {}


def blocks(p: dict) -> list[dict]:
    out = []
    if p.get("title_card"):
        tc = p["title_card"]
        out.append({"t": 0.0, "tipo": "título", "texto": f"{tc['kicker']} · {tc['title']}", "fuente": "skeleton"})
    for a in p.get("archive_clippings") or []:
        out.append({"t": a["start"], "tipo": "recorte" + (" (reservado)" if a.get("reserved") else ""),
                    "texto": a["headline"], "fuente": f"{a.get('kicker')} · {a.get('pool_id')}"})
    if p.get("quote_card"):
        q = p["quote_card"]
        out.append({"t": q["start"], "tipo": "cita", "texto": q["text"], "fuente": f"— {q['author']} · {q['pool_id']}"})
    for e in p.get("emphasis") or []:
        out.append({"t": e["start"], "tipo": "sello" + (" (pico)" if e.get("peak_word") else ""),
                    "texto": e["word"] + (f" + {e['icon']}" if e.get("icon") else ""),
                    "fuente": f"mood {e['category']}, peso {e.get('weight')}"})
    if p.get("count_up"):
        c = p["count_up"]
        out.append({"t": c["start"], "tipo": "contador", "texto": f"{c['value_text']} {c.get('unit', '')}",
                    "fuente": c.get("pool_id") or c.get("source") or f"fact {c.get('fact_idx')}"})
    if p.get("water_level"):
        w = p["water_level"]
        out.append({"t": w["start"], "tipo": "nivel de agua", "texto": f"{w['value_text']} {w['unit']}",
                    "fuente": w.get("pool_id") or f"fact {w.get('fact_idx')}"})
    if p.get("evidence_zoom"):
        z = p["evidence_zoom"]
        out.append({"t": z["start"], "tipo": "zoom", "texto": z.get("detail") or z.get("anchor") or "",
                    "fuente": "visión sobre la foto"})
    for c in p.get("callouts") or []:
        out.append({"t": c["start"], "tipo": "dato", "texto": c["text"], "fuente": c.get("pool_id") or c.get("source")})
    if p.get("time_ticker"):
        tk = p["time_ticker"]
        ch = "".join(f" → {x['day']} {x['month']} @ {x['t']:.1f}s" for x in tk.get("changes") or [])
        out.append({"t": tk["start"], "tipo": "reloj", "texto": f"{tk['day']} {tk['month']} · {tk['tail']}{ch}",
                    "fuente": tk.get("pool_id")})
    if p.get("chapter_question"):
        q = p["chapter_question"]
        out.append({"t": q["start"], "tipo": "pregunta", "texto": q["text"], "fuente": "generada (gfx_question)"})
    return sorted(out, key=lambda b: b["t"])


def why(b: dict, p: dict) -> str:
    for r in p.get("critico") or []:
        if CRIT_KIND.get(r["bloque"]) and b["tipo"].startswith(CRIT_KIND[r["bloque"]]) and abs(r["t"] - b["t"]) < 0.05:
            return f"crítico {r['veredicto'].upper()}{' (reservado: queda)' if r.get('reservado') and r['veredicto'] != 'suma' else ''}: {r['motivo']}"
    return {"título": "abre el capítulo", "reloj": "ubica la fecha que narra la voz (cronología del pool)",
            "pregunta": "cierre del cap: engancha con el siguiente"}.get(b["tipo"], "sin juicio del crítico")


def _key(b: dict) -> tuple[str, str]:
    return b["tipo"].split(" (")[0], b["texto"]


def main(caps: list[str]) -> None:
    lines = []
    missing = []
    for cap in caps:
        p, s = _plan(WORK, cap), _plan(SIM, cap)
        lines += [f"### {cap}", "", "| t | bloque | texto | fuente / kicker | por qué suma |", "|---|---|---|---|---|"]
        for b in blocks(p):
            txt = b["texto"].replace("|", "\\|")
            lines.append(f"| {b['t']:.1f} s | {b['tipo']} | {txt} | {b['fuente']} | {why(b, p).replace('|', '/')} |")
        lines.append("")
        got = {_key(b) for b in blocks(p)}
        for b in blocks(s):
            if _key(b) not in got:
                gone = next((r for r in p.get("critico") or [] if not r["pasa"] and abs(r["t"] - b["t"]) < 0.05), None)
                missing.append(f"- {cap} · {b['tipo']} «{b['texto']}» @ {b['t']:.1f} s"
                               + (f" — lo sacó el crítico ({gone['veredicto']}: {gone['motivo']})" if gone else ""))
    print("\n".join(lines))
    print("\n## Lo que SIM_F5f prometía y no salió\n")
    print("\n".join(missing) or "- nada")


if __name__ == "__main__":
    main(sys.argv[1:] or ["ch02", "ch05", "ch06", "ch07"])
