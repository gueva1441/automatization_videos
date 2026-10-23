"""F11 §2 — prueba de convergencia del guion v4: escaletas fijas (las de las versiones buenas), sin notas, dos corridas
independientes (A y B) por tema.

    Orleans  ba6c3cac-f7r3      01a_escaleta.json     (md5 2f794418…, = F7c-3, 8 beats, humano Reed)
    Ycuá     f8s1-ycua-bolanos  01a_escaleta_v1.json  (md5 e1ba1a48…, 12 beats, Liz Torres) — NO la del ajuste

Cada corrida: guion_v4.write (una llamada) → guion_v4.reparar (una ronda) → m01d.particionar (persist=False) → juez m05.
Salidas con sufijo _v4A / _v4B en _steps/<topic>/ y en lab/hyperframes/f11/; no pisa _v1, _ajuste ni los archivos
vigentes; no escribe en topics_db. Tope de la tanda: US$ 2.00 (antes de cada corrida, si lo gastado + la estimación
de una corrida lo pasa, PARADA).
Además (gratis): bloqueantes y métricas de las v3 (F7c-3 y Ycuá v1) y tokens del prompt v3 vs v4.
Uso: python -I lab/hyperframes/f11/f11_convergencia.py [orleans:A ycua:A orleans:B ycua:B] [--solo-v3]
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
LAB = Path(__file__).resolve().parent
TOPE_USD = 2.00
ESTIMADO_CORRIDA = 0.50
TEMAS = {
    "orleans": {"tid": "ba6c3cac-f7r3", "esc": "01a_escaleta.json", "md5": "2f794418",
                "v3": "01b_editor_v3.json", "v3_nombre": "F7c-3"},
    "ycua": {"tid": "f8s1-ycua-bolanos", "esc": "01a_escaleta_v1.json", "md5": "e1ba1a48",
             "v3": "01b_editor_v3_v1.json", "v3_nombre": "v1"},
}
COSTOS = LAB / "costos_f11.json"


def wc(s: str) -> int:
    return len(re.findall(r"[\wáéíóúñü]+", s or "", re.I))


def _steps(tid: str) -> Path:
    from script_engine.m01a_skeleton import STEPS_DIR
    return STEPS_DIR / tid


def _load(tema: str) -> tuple[dict, dict]:
    import fase1_5 as f15
    t = TEMAS[tema]
    raw = (_steps(t["tid"]) / t["esc"]).read_bytes()
    if not hashlib.md5(raw).hexdigest().startswith(t["md5"]):
        raise SystemExit(f"{tema}: la escaleta {t['esc']} no es la fijada (md5 {t['md5']}…)")
    topic = dict(f15._load_topic_by_id(t["tid"]))          # solo lectura: no se escribe topics_db
    topic["guion_version"] = 4
    return topic, json.loads(raw.decode("utf-8"))


def _costos() -> dict:
    return json.loads(COSTOS.read_text(encoding="utf-8")) if COSTOS.exists() else {"corridas": [], "usd_total": 0.0}


def _write(p: Path, obj) -> None:
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding="utf-8")


def narracion_md(tema: str, tag: str, esc: dict, res: dict) -> str:
    beats = {b["n"]: b for b in esc["beats"]}
    ps = res["reparacion"]["parrafos"]
    m = res["metricas"]
    titles = {c["chapter_number"]: c["title"] for c in (res.get("skeleton") or {}).get("chapters") or []}
    bl = res["reparacion"]["bloqueantes_despues"]
    lines = [f"# Narración — {tema.capitalize()} (guion v4, corrida {tag}, F11)", "",
             f"**{m['palabras']} palabras** · bloqueantes finales: {len(bl)} · duras v3 re-medidas: "
             f"{len(m['duras_v3'])} · citas: {m['citas']} · humano por nombre en los caps {m['humano_caps']} · "
             f"cierre: {m['cierre']} · US$ {res['costo']['usd']:.3f}", ""]
    for x in bl:
        lines.append(f"- bloqueante ({x['codigo']}) cap {x['cap']} beat {x['beat']}: {x['motivo']}"
                     + (f" — «{x['frase']}»" if x["frase"] else ""))
    if res.get("error"):
        lines += ["", f"**Partición:** {res['error']}"]
    lines.append("")
    for n in range(1, 8):
        cps = [p for p in ps if p["cap"] == n]
        w, tgt = m["palabras_por_cap"].get(n) or m["palabras_por_cap"].get(str(n)) or [0, 0]
        lines += [f"## Cap {n}" + (f" — {titles[n]}" if n in titles else "") + f" · {w}/{tgt} palabras", ""]
        for p in cps:
            b = beats.get(p["beat"], {})
            lines += [f"**Beat {p['beat']}** · {b.get('funcion')} · ids {', '.join(p.get('ids_usados') or [])}", "",
                      p["texto"], ""]
    return "\n".join(lines)


def corrida(tema: str, tag: str) -> dict:
    from cost_tracker import cost_tracker
    from script_engine import guion_v4 as g4
    from script_engine import m01d_particion as md
    from script_engine.m05_narrative import judge_narration
    t = TEMAS[tema]
    topic, esc = _load(tema)
    pool = topic["evidence_pool"]
    log: list[str] = []
    res: dict = {"tema": tema, "tid": t["tid"], "corrida": tag, "escaleta": t["esc"], "notas": None}
    cost_tracker.start_video(f"{t['tid']}-v4{tag}")
    t0 = time.time()
    try:
        g = g4.write(topic, esc, log=log)
        res["crudo"] = g["parrafos"]
        res["prompt_version"] = g["prompt_version"]
        res["bloqueantes_crudo"] = g4.bloqueantes(topic, esc, g["parrafos"])
        res["metricas_crudo"] = g4.metricas(topic, esc, g["parrafos"])
        r = g4.reparar(topic, esc, g["parrafos"], log=log)
        res["reparacion"] = r
        res["metricas"] = g4.metricas(topic, esc, r["parrafos"])
        try:
            part = md.particionar(topic, esc, r["parrafos"], pool, persist=False, shorten=md.editor_shorten(), log=log)
            res["skeleton"], res["particion_notas"] = part["skeleton"], part["notas"]
            d = _steps(t["tid"])
            _write(d / f"01a_skeleton_v4{tag}.json", part["skeleton"])
            _write(d / f"01b_narration_v4{tag}.json", part["narration"])
            _write(d / f"01b_narracion_v3_v4{tag}.json", part["narracion_v3"])
            judge_narration(t["tid"], pool=pool, narration=part["narration"], skeleton=part["skeleton"],
                            out_name=f"06_judge_narrative_v4{tag}.json")
        except md.ParticionError as e:
            res["error"] = str(e)
    finally:
        rep = cost_tracker.end_video()
    res["costo"] = {"usd": round(getattr(rep, "total_cost", 0.0) or 0.0, 4), "segundos": round(time.time() - t0, 1),
                    "llamadas": [{"desc": e.description, "in": e.tokens_in, "out": e.tokens_out,
                                  "thinking": e.tokens_thinking, "usd": round(e.total_cost, 4)}
                                 for e in (getattr(rep, "entries", None) or [])]}
    res["log"] = log
    _write(_steps(t["tid"]) / f"01b_guionista_v4{tag}.json", res)
    _write(LAB / f"guion_{tema}_v4{tag}.json", res)
    (LAB / f"NARRACION_{tema}_v4{tag}.md").write_text(narracion_md(tema, tag, esc, res), encoding="utf-8")
    c = _costos()
    c["corridas"].append({"tema": tema, "corrida": tag, "usd": res["costo"]["usd"], "segundos": res["costo"]["segundos"]})
    c["usd_total"] = round(sum(x["usd"] for x in c["corridas"]), 4)
    _write(COSTOS, c)
    print(f"[{tema} {tag}] bloqueantes {len(res['bloqueantes_crudo'])} → {len(r['bloqueantes_despues'])} · "
          f"{res['metricas']['palabras']} palabras · US$ {res['costo']['usd']:.3f} · total US$ {c['usd_total']:.3f}",
          flush=True)
    return res


def v3_y_tokens() -> None:
    """Gratis: bloqueantes §1.2 y métricas de las v3 guardadas; tokens del prompt v3 vs v4 (count_tokens)."""
    from gemini_helpers import _cfg, _client
    from script_engine import guion_v4 as g4
    from script_engine import m01b_guionista as mg
    out, tok = {}, {}
    for tema, t in TEMAS.items():
        topic, esc = _load(tema)
        ps = json.loads((_steps(t["tid"]) / t["v3"]).read_text(encoding="utf-8"))["parrafos"]
        out[tema] = {"version": t["v3_nombre"], "archivo": t["v3"], "parrafos": ps,
                     "bloqueantes": g4.bloqueantes(topic, esc, ps), "metricas": g4.metricas(topic, esc, ps, declared=True)}
        p3, p4 = mg.build_prompt(topic, esc), g4.prompt(topic, esc)
        tok[tema] = {k: _client.models.count_tokens(model=_cfg.gemini_model_research,
                                                    contents=mg.SYSTEM + "\n" + p).total_tokens
                     for k, p in (("v3", p3), ("v4", p4))}
        tok[tema].update({"chars_v3": len(p3), "chars_v4": len(p4)})
        (LAB / f"prompt_{tema}_v4.txt").write_text(p4, encoding="utf-8")
    _write(LAB / "v3_remedido.json", out)
    _write(LAB / "tokens_prompt.json", tok)
    print(json.dumps(tok), flush=True)


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")                # -I ignora PYTHONIOENCODING
    v3_y_tokens()
    if "--solo-v3" in sys.argv:
        return
    plan = [a for a in sys.argv[1:] if ":" in a] or ["orleans:A", "ycua:A", "orleans:B", "ycua:B"]
    for item in plan:
        tema, tag = item.split(":")
        spent = _costos()["usd_total"]
        if spent + ESTIMADO_CORRIDA > TOPE_USD:
            print(f"PARADA por costo: gastado US$ {spent:.3f}; {item} no corre (tope US$ {TOPE_USD:.2f})", flush=True)
            break
        corrida(tema, tag)


if __name__ == "__main__":
    main()
