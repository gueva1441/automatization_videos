"""F7c: Orleans `ba6c3cac-f7r3` (pool de research v3) por la tubería v3 de F6 SIN cambios: m01a_escaleta (lee el
digest del pool) → m01b_guionista → m01c_editor → validadores (m01b_guionista.review).

Topic = la entrada `ba6c3cac-f7r3` de topics_db (copia de f5v2: hook, misterio, ángulo) con el evidence_pool de
data/scripts/_steps/ba6c3cac-f7r3/01_facts_sources.json y guion_version 3. SIN `escaleta_notas`: las notas del analista
de F6c (NOTAS_F6B4) hablan de ids del pool viejo; la prueba es si la narración sube sola con el pool nuevo.
Deja en data/scripts/_steps/ba6c3cac-f7r3/: 01a_escaleta.json, 01b_guionista_v3.json, 01b_editor_v3.json,
01b_narracion_v3.json; en lab/hyperframes/f7/: escaleta_orleans_v3r.json, ESCALETA_orleans_v3r.md,
NARRACION_orleans_v3r.md, f7c_costos.json.
Uso: python -I lab/hyperframes/f7/f7c_orleans.py [--desde guionista|editor]
"""
from __future__ import annotations

import json
import shutil
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
TOPIC = "ba6c3cac-f7r3"
STEPS = ROOT / "data" / "scripts" / "_steps" / TOPIC
LAB = Path(__file__).resolve().parent
ESC_ATTEMPTS = 5


def _dump(p: Path, d) -> None:
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")


def topic_v3r() -> dict:
    db = json.loads((ROOT / "data" / "topics_db.json").read_text(encoding="utf-8"))
    t = json.loads(json.dumps(next(t for t in db["topics"] if t["id"] == TOPIC)))
    t.update({"video_id": TOPIC, "guion_version": 3,
              "evidence_pool": json.loads((STEPS / "01_facts_sources.json").read_text(encoding="utf-8"))["evidence_pool"]})
    return t


def _timed(fn, label: str, cost: dict):
    from cost_tracker import cost_tracker
    cost_tracker.start_video(TOPIC)
    t0 = time.time()
    try:
        out = fn()
    finally:                                            # el costo queda aunque el paso falle
        r = cost_tracker.end_video()
        cost[label] = {"usd": round(getattr(r, "total_cost", 0.0) or 0.0, 4), "segundos": round(time.time() - t0, 1)}
        cost.setdefault("_corridas", []).append({"paso": label, **cost[label]})
        _dump(LAB / "f7c_costos.json", cost)
    return out


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    from script_engine import m01a_escaleta as me
    from script_engine import m01b_guionista as mg
    from script_engine import m01c_editor as mc
    from script_engine.m05_narrative import adjectives
    args = sys.argv[1:]
    desde = args[args.index("--desde") + 1] if "--desde" in args else "escaleta"
    topic = topic_v3r()
    pool = topic["evidence_pool"]
    log: list[str] = []
    cpath = LAB / "f7c_costos.json"
    cost = json.loads(cpath.read_text(encoding="utf-8")) if cpath.exists() else {}
    if desde == "escaleta":
        # 5 intentos (el default es 3): en la 1.ª corrida los 3 fallaron, cada uno por algo distinto
        esc = _timed(lambda: me.generate_escaleta(topic, log=log, attempts=ESC_ATTEMPTS), "escaleta", cost)
        esc["_costo"] = cost["escaleta"]
        _dump(STEPS / "01a_escaleta.json", esc)
        _dump(cpath, cost)
        print("\n".join(log), flush=True)
    esc = json.loads((STEPS / "01a_escaleta.json").read_text(encoding="utf-8"))
    shutil.copy2(STEPS / "01a_escaleta.json", LAB / "escaleta_orleans_v3r.json")
    (LAB / "ESCALETA_orleans_v3r.md").write_text(
        me.to_markdown(esc, pool) + f"\n---\nCosto: US$ {cost.get('escaleta', {}).get('usd')} · intentos: "
        f"{len(esc.get('_intentos') or [])}\n", encoding="utf-8")
    gfile = STEPS / "01b_guionista_v3.json"
    if desde in ("escaleta", "guionista"):
        g = _timed(lambda: mg.write(topic, esc, log=log), "guionista", cost)
        g["_costo"] = cost["guionista"]
        _dump(gfile, g)
        _dump(cpath, cost)
        print("\n".join(log[-12:]), flush=True)
    g = json.loads(gfile.read_text(encoding="utf-8"))
    e = _timed(lambda: mc.edit(topic, esc, g["parrafos"], log=log), "editor", cost)
    e["_costo"] = cost["editor"]
    _dump(STEPS / "01b_editor_v3.json", e)
    _dump(cpath, cost)
    final = e["parrafos"]
    caps = mg.caps_text(esc, final)
    _dump(STEPS / "01b_narracion_v3.json", {"topic_id": TOPIC, "parrafos": final, "caps": caps,
                                            "revision": e["revision_despues"], "costo": cost})
    rv0, rv1 = e["revision_antes"], e["revision_despues"]
    full = " ".join(c["narration"] for c in caps)
    nw = mg.wc(full)
    intentos = "; ".join("intento %s: %d duras, %s blandas" % (x["intento"], len(x["duras"]), x["blandas"])
                         for x in g["_intentos"])
    beats = {b["n"]: b for b in esc["beats"]}
    L = ["# Narración v3 con el pool de research v3 — Orleans `ba6c3cac-f7r3` (F7c)", "",
         f"- Escaleta: `escaleta_orleans_v3r.json` ({len(esc.get('_intentos') or [])} intento(s), digest del pool). "
         f"Guionista: Pro, best_of_{mg.BEST_OF} → elegido el intento {g['elegido']} ({intentos}).",
         f"- Editor: {len(e['cambios'])} párrafo(s) editado(s), {e['aceptados']} aceptado(s). Duras: guionista "
         f"{len(rv0['hard'])} → final {len(rv1['hard'])} · blandas {len(rv0['soft'])} → {len(rv1['soft'])}.",
         f"- {nw} palabras · {round(100 * len(adjectives(full)) / max(nw, 1), 2)} adjetivos/100 · costo: escaleta US$ "
         f"{cost.get('escaleta', {}).get('usd')} + guionista US$ {cost['guionista']['usd']} + editor US$ "
         f"{cost['editor']['usd']}.", ""]
    if rv1["hard"]:
        L += ["## Problemas duros que quedan", ""] + [f"- {x}" for x in rv1["hard"]] + [""]
    if rv1["soft"]:
        L += ["## Avisos", ""] + [f"- {x}" for x in rv1["soft"]] + [""]
    for c in caps:
        n = c["chapter_number"]
        L += [f"## Cap {n}", ""]
        for p in [p for p in final if beats.get(p["beat"], {}).get("cap") == n]:
            L += [p["texto"], f"<sub>beat {p['beat']} · ids {', '.join(p.get('ids_usados') or [])}</sub>", ""]
    (LAB / "NARRACION_orleans_v3r.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L[:8]))


if __name__ == "__main__":
    main()
