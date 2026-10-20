"""F4c: tabla antes/después por bloque (ch02, ch05) desde los planes resueltos.

    antes    _fase2b_work/_bak_f4c_pre/gfx_plan_chNN.resolved.json (F4b)
    después  _fase2b_work/gfx_plan_chNN.resolved.json (F4c)
Uso: PYTHONIOENCODING=utf-8 python lab/hyperframes/f4c/tabla_antes_despues.py > lab/hyperframes/f4c/TABLA_antes_despues.md
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
W = ROOT / "output" / "ba6c3cac-a091-41c0-8dad-afd2f4364747" / "_fase2b_work"


def _plan(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))["plan"]


def _t(x: float) -> str:
    return f"{int(x // 60)}:{x % 60:04.1f}"


def blocks(plan: dict) -> list[tuple[float, str, str]]:
    out = []
    for c in plan.get("callouts") or []:
        out.append((c["start"], "dato", f"«{c['text']}»"))
    for a in plan.get("archive_clippings") or []:
        k = a.get("kicker") or "—"
        out.append((a["start"], "recorte", f"«{a['headline']}» · kicker {k}" + (f" · ícono {a['icon']}" if a.get("icon") else "")
                    + (" · PICO" if a.get("peak") else "")))
    for e in plan.get("emphasis") or []:
        ico = e.get("icon") if e.get("icon_callout") else None
        out.append((e["start"], "sello+mood", f"{str(e['word']).upper()} ({e['category']}, capa {e.get('layer')}, peso {e.get('weight')})"
                    + (f" · ícono {ico}" if ico else "") + (" · PALABRA DEL PICO" if e.get("peak_word") else "")))
    if plan.get("water_level"):
        w = plan["water_level"]
        out.append((w["start"], "nivel de agua", f"{w['value_text']} {w['unit']}"))
    if plan.get("count_up"):
        c = plan["count_up"]
        out.append((c["start"], "contador", f"{c['value_text']} {c['unit']}"))
    if plan.get("evidence_zoom"):
        z = plan["evidence_zoom"]
        out.append((z["start"], "zoom", f"«{z.get('anchor')}»"))
    if plan.get("chapter_question"):
        q = plan["chapter_question"]
        out.append((q["start"], "pregunta", f"{q['text']}" + (" (manual de Omar)" if q.get("manual") else " (automática)")))
    return sorted(out)


def main() -> None:
    print("# F4c — Tabla antes/después por bloque (ch02, ch05)\n")
    print("Antes = F4b (`_bak_f4c_pre`), después = F4c (doctrina R1–R8). Tiempos del cap.\n")
    for cap in ("ch02", "ch05"):
        a, d = _plan(W / "_bak_f4c_pre" / f"gfx_plan_{cap}.resolved.json"), _plan(W / f"gfx_plan_{cap}.resolved.json")
        print(f"## {cap}\n")
        print(f"Pico: antes «{(a.get('pico') or {}).get('word')}» → {(a.get('pico') or {}).get('block')} · "
              f"después «{(d.get('pico') or {}).get('word')}» → {(d.get('pico') or {}).get('block')}"
              f" + palabra «{(d.get('pico') or {}).get('palabra')}»\n")
        ia = json.loads((W / "_bak_f4c_pre" / f"gfx_intensity_{cap}.json").read_text(encoding="utf-8"))["raw"]["cargas"]
        idd = json.loads((W / f"gfx_intensity_{cap}.json").read_text(encoding="utf-8"))["raw"]["cargas"]
        print(f"Cargas de Flash: antes {len(ia)} → se usaban las 5 primeras {[c['word'] for c in ia[:5]]}; "
              f"después {len(idd)} propuestas {[(c['word'], c['peso']) for c in idd]}\n")
        print("| t | tipo | antes (F4b) | después (F4c) |\n|---|---|---|---|")
        ba, bd = blocks(a), blocks(d)
        used = set()
        for t, kind, txt in ba:
            j = next((k for k, (t2, k2, _) in enumerate(bd) if k not in used and k2 == kind and abs(t2 - t) < 6.0), None)
            if j is None:
                print(f"| {_t(t)} | {kind} | {txt} | — (quitado) |")
            else:
                used.add(j)
                print(f"| {_t(t)} | {kind} | {txt} | {bd[j][2]}" + (f" @ {_t(bd[j][0])}" if abs(bd[j][0] - t) > 0.5 else "") + " |")
        for k, (t, kind, txt) in enumerate(bd):
            if k not in used:
                print(f"| {_t(t)} | {kind} | — | {txt} (nuevo) |")
        print(f"\nTotal de bloques: antes {len(ba)} → después {len(bd)}\n")
        rej = json.loads((W / f"gfx_plan_{cap}.resolved.json").read_text(encoding="utf-8")).get("rejected") or []
        print(f"Candado literal: {len(rej)} rechazo(s) {[r.get('text') or r for r in rej][:4]}\n")


if __name__ == "__main__":
    main()
