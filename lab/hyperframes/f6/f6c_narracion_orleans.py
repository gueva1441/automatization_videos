"""F6c: narración v3 de Orleans — m01b_guionista (Pro, texto completo, best_of_2) + m01c_editor (Pro) + validadores
duros otra vez. Usa la escaleta f6b-4 (data/scripts/_steps/ba6c3cac-f6v3/01a_escaleta.json) y el pool verificado.
Deja en data/scripts/_steps/ba6c3cac-f6v3/: 01b_guionista_v3.json, 01b_editor_v3.json, 01b_narracion_v3.json (texto
final por párrafo y por cap; el contrato de 7 caps de 01b_narration.json es F6d) y lab/hyperframes/f6/NARRACION_orleans_v3.md.
Con --solo-editor reusa el guionista guardado.
Uso: PYTHONIOENCODING=utf-8 python lab/hyperframes/f6/f6c_narracion_orleans.py [--solo-editor]
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))
STEPS = ROOT / "data" / "scripts" / "_steps" / "ba6c3cac-f6v3"
LAB = Path(__file__).resolve().parent


def _dump(p: Path, d) -> None:
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    from cost_tracker import cost_tracker
    from f6b_escaleta_orleans import topic_v3
    from script_engine import m01b_guionista as mg
    from script_engine import m01c_editor as mc
    from script_engine.m05_narrative import adjectives
    topic = topic_v3()
    esc = json.loads((STEPS / "01a_escaleta.json").read_text(encoding="utf-8"))
    log: list[str] = []
    cost = {}
    gfile = STEPS / "01b_guionista_v3.json"
    if "--solo-editor" in sys.argv and gfile.exists():
        g = json.loads(gfile.read_text(encoding="utf-8"))
    else:
        cost_tracker.start_video("ba6c3cac-f6v3")
        t0 = time.time()
        try:
            g = mg.write(topic, esc, log=log)
        finally:
            r = cost_tracker.end_video()
        g["_costo"] = {"usd": round(getattr(r, "total_cost", 0.0) or 0.0, 4), "segundos": round(time.time() - t0, 1)}
        _dump(gfile, g)
    cost["guionista"] = g["_costo"]
    cost_tracker.start_video("ba6c3cac-f6v3")
    t0 = time.time()
    try:
        e = mc.edit(topic, esc, g["parrafos"], log=log)
    finally:
        r = cost_tracker.end_video()
    e["_costo"] = {"usd": round(getattr(r, "total_cost", 0.0) or 0.0, 4), "segundos": round(time.time() - t0, 1)}
    cost["editor"] = e["_costo"]
    _dump(STEPS / "01b_editor_v3.json", e)
    final = e["parrafos"]
    caps = mg.caps_text(esc, final)
    _dump(STEPS / "01b_narracion_v3.json", {"topic_id": "ba6c3cac-f6v3", "parrafos": final, "caps": caps,
                                            "revision": e["revision_despues"], "costo": cost})

    rv0, rv1 = e["revision_antes"], e["revision_despues"]
    beats = {b["n"]: b for b in esc["beats"]}
    full = " ".join(c["narration"] for c in caps)
    nw = mg.wc(full)
    intentos = "; ".join("intento %s: %d duras, %s blandas" % (x["intento"], len(x["duras"]), x["blandas"])
                         for x in g["_intentos"])
    L = ["# Narración v3 — Orleans (F6c: guionista + editor)", "",
         f"- Escaleta: f6b-4 (`escaleta_orleans.json`). Guionista: Pro, texto completo, best_of_{mg.BEST_OF} → elegido el "
         f"intento {g['elegido']} ({intentos}).",
         f"- Editor: {len(e['cambios'])} párrafo(s) editado(s), {e['aceptados']} aceptado(s). Duras: guionista "
         f"{len(rv0['hard'])} → final {len(rv1['hard'])} · blandas {len(rv0['soft'])} → {len(rv1['soft'])}.",
         f"- {nw} palabras · {round(100 * len(adjectives(full)) / max(nw, 1), 2)} adjetivos/100 · costo guionista US$ "
         f"{cost['guionista']['usd']} + editor US$ {cost['editor']['usd']}.", ""]
    if rv1["hard"]:
        L += ["## Problemas duros que quedan", ""] + [f"- {x}" for x in rv1["hard"]] + [""]
    for c in caps:
        n = c["chapter_number"]
        pc = rv1["por_cap"].get(n) or {}
        L += [f"## Cap {n} · {pc.get('palabras')} palabras (objetivo {pc.get('objetivo')})", ""]
        for p in [p for p in final if p["cap"] == n]:
            b = beats.get(p["beat"], {})
            L += [f"**[beat {p['beat']} · {b.get('funcion')} · intensidad {b.get('intensidad')}]** "
                  f"`ids_usados: {', '.join(p['ids_usados']) or '—'}`", "", p["texto"], ""]
        if pc.get("blandas"):
            L += ["<details><summary>Avisos (blandas)</summary>", ""] + [f"- {x}" for x in pc["blandas"]] + ["", "</details>", ""]
    L += ["## Cambios del editor (`cambios[]`)", ""]
    for x in e["cambios"]:
        L += [f"### Párrafo {x['parrafo']} (beat {x['beat']}) — **{x['estado']}**"
              + (f" · {x['motivo']}" if x.get("motivo") else "")
              + (f" · rechazo: {x['motivo_rechazo']}" if x.get("motivo_rechazo") else ""), "",
              f"- Antes: {x['antes']}", f"- Después: {x['despues']}", ""]
    if g.get("_intentos"):
        L += ["## Intentos del guionista", ""] + [f"- intento {x['intento']}: duras {x['duras'][:6]}" for x in g["_intentos"]]
    L += ["", "## Log", ""] + [f"- {x.strip()}" for x in log]
    (LAB / "NARRACION_orleans_v3.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L[:12]))


if __name__ == "__main__":
    main()
