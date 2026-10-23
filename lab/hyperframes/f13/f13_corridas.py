"""F13 §2 — largo abierto: dos corridas del guion v4 con `largo="abierto"` (prompt `f13-1`), Sol high, UNA llamada cada
una, sin notas, sin reparación ni editor.

    orl   Orleans  ba6c3cac-f7r3       01a_escaleta.json     (md5 2f794418…)
    ycua  Ycuá     f8s1-ycua-bolanos   01a_escaleta_v1.json  (md5 e1ba1a48…)

Cada corrida: guion_v4.write(largo="abierto") → bloqueantes(largo="abierto") y métricas (solo miden). Salidas en
lab/hyperframes/f13/: prompt_<tema>_f13.txt (sistema + usuario), guion_<tema>_f13_abierto.json y
NARRACION_<tema>_f13_abierto.md. No escribe en _steps ni en topics_db.
Tope de la tanda: US$ 0.50. Antes de cada llamada se fija `max_completion_tokens` para que lo peor posible no lo pase;
una sola llamada que facture por corrida (si el JSON viene roto, PARADA: no hay reintento).
Uso: python -I lab/hyperframes/f13/f13_corridas.py [orl ycua]
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
LAB = Path(__file__).resolve().parent
TOPE_USD = 0.50
MODELO = "gpt-6.1-sol"
TEMAS = {"orl": ("orleans", "ba6c3cac-f7r3", "01a_escaleta.json", "2f794418"),
         "ycua": ("ycua", "f8s1-ycua-bolanos", "01a_escaleta_v1.json", "e1ba1a48")}
COSTOS = LAB / "costos_f13.json"
PALABRAS_POR_SEG = 2.05


class Parada(RuntimeError):
    pass


def load(tag: str) -> tuple[dict, dict]:
    import fase1_5 as f15
    from script_engine.m01a_skeleton import STEPS_DIR
    _, tid, esc_name, md5 = TEMAS[tag]
    raw = (STEPS_DIR / tid / esc_name).read_bytes()
    if not hashlib.md5(raw).hexdigest().startswith(md5):
        raise SystemExit(f"la escaleta {tid}/{esc_name} no es la fijada (md5 {md5}…)")
    topic = dict(f15._load_topic_by_id(tid))               # solo lectura: no se escribe topics_db
    topic["guion_version"] = 4
    return topic, json.loads(raw.decode("utf-8"))


def _costos() -> dict:
    return json.loads(COSTOS.read_text(encoding="utf-8")) if COSTOS.exists() else {"corridas": [], "usd_total": 0.0}


def _write(p: Path, obj) -> None:
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding="utf-8")


def repeticion_interna(texto: str) -> float:
    """% de 3-gramas de contenido (m05._trigrams) del cap que aparecen en dos o más de sus oraciones. Mide el relleno:
    no rechaza nada."""
    from script_engine import m01b_guionista as mg
    from script_engine.m05_narrative import _trigrams
    per = [_trigrams(s) for s in mg.sentences(texto)]
    allg = set().union(*per) if per else set()
    if not allg:
        return 0.0
    rep = {g for g in allg if sum(g in s for s in per) >= 2}
    return round(100 * len(rep) / len(allg), 1)


def narracion_md(tema: str, tag: str, esc: dict, res: dict) -> str:
    beats = {b["n"]: b for b in esc["beats"]}
    m = res.get("metricas") or {}
    ps = res.get("parrafos") or []
    L = [f"# Narración — {tema} (guion v4, largo abierto, {MODELO} high, corrida _f13_{tag}_abierto, F13)", "",
         f"Prompt `{res.get('prompt_version')}` · sistema md5 `{res['prompt_md5']['sistema'][:8]}` · usuario md5 "
         f"`{res['prompt_md5']['usuario'][:8]}` · US$ {res['costo']['usd']:.3f} · {res['costo']['segundos']:.0f} s", ""]
    if res.get("error"):
        L += [f"**Error:** {res['error']}", ""]
    if m:
        L += [f"**{m['palabras']} palabras ≈ {res['minutos']} min** (a {PALABRAS_POR_SEG} palabras/s) · bloqueantes "
              f"{len(res['bloqueantes'])} · duras v3 re-medidas {len(m['duras_v3'])} · citas {m['citas']} · "
              f"cierre {m['cierre']}", ""]
    for x in res.get("bloqueantes") or []:
        L.append(f"- bloqueante ({x['codigo']}) cap {x['cap']} beat {x['beat']}: {x['motivo']}"
                 + (f" — «{x['frase'][:200]}»" if x["frase"] else ""))
    L.append("")
    for n in range(1, 8):
        cps = [p for p in ps if p["cap"] == n]
        w, tgt = (m.get("palabras_por_cap") or {}).get(n) or [0, 0]
        L += [f"## Cap {n} · {w} palabras (el objetivo de la escaleta era {tgt}; no se le dijo al modelo) · "
              f"repetición interna {res['repeticion_por_cap'].get(str(n), res['repeticion_por_cap'].get(n, 0))} %", ""]
        for p in cps:
            b = beats.get(p["beat"], {})
            L += [f"**Beat {p['beat']}** · {b.get('funcion')} · ids {', '.join(p.get('ids_usados') or [])}", "",
                  p["texto"], ""]
    return "\n".join(L)


def corrida(tag: str) -> dict:
    import gpt_helpers
    from cost_tracker import cost_tracker
    from script_engine import guion_v4 as g4
    tema, tid, esc_name, _ = TEMAS[tag]
    topic, esc = load(tag)
    sis, usr = g4.system(), g4.prompt(topic, esc, "abierto")
    (LAB / f"prompt_{tema}_f13.txt").write_text(
        f"===== SISTEMA (md5 {hashlib.md5(sis.encode()).hexdigest()}) =====\n{sis}\n\n"
        f"===== USUARIO (md5 {hashlib.md5(usr.encode()).hexdigest()}) =====\n{usr}\n", encoding="utf-8")
    spent = _costos()["usd_total"]
    pin, pout = gpt_helpers.PRICES[MODELO]
    in_usd = (len(sis) + len(usr)) / 3 / 1e6 * pin
    max_out = min(gpt_helpers.MAX_COMPLETION_TOKENS, int((TOPE_USD - spent - in_usd) / pout * 1e6) - 500)
    if max_out < 8000:
        raise Parada(f"tope de costo: gastado US$ {spent:.3f}, no alcanza para otra llamada")
    n = {"posts": 0}

    def post(body: dict) -> dict:
        if n["posts"]:
            raise Parada("la llamada ya facturó (JSON roto): no hay reintento por el tope")
        body["max_completion_tokens"] = max_out
        n["posts"] += 1
        return gpt_helpers._post(body)

    call = gpt_helpers.make_call(MODELO, g4.ESFUERZO.get(MODELO), post=post)
    res: dict = {"tema": tema, "tid": tid, "corrida": f"f13_{tag}_abierto", "modelo": MODELO, "esfuerzo": "high",
                 "escaleta": esc_name, "notas": None, "largo": "abierto", "max_completion_tokens": max_out,
                 "prompt_md5": {"sistema": hashlib.md5(sis.encode()).hexdigest(),
                                "usuario": hashlib.md5(usr.encode()).hexdigest()}}
    cost_tracker.start_video(f"{tid}-f13-abierto")
    t0 = time.time()
    try:
        g = g4.write(topic, esc, call=call, largo="abierto")
        res["prompt_version"] = g["prompt_version"]
        res["parrafos"] = g["parrafos"]
        res["bloqueantes"] = g4.bloqueantes(topic, esc, g["parrafos"], largo="abierto")
        res["metricas"] = g4.metricas(topic, esc, g["parrafos"])
        from script_engine import m01b_guionista as mg
        res["repeticion_por_cap"] = {n_: repeticion_interna(c["narration"]) for c in mg.caps_text(esc, g["parrafos"])
                                     for n_ in [c["chapter_number"]]}
        res["minutos"] = round(res["metricas"]["palabras"] / PALABRAS_POR_SEG / 60, 1)
    except Exception as e:  # noqa: BLE001 — se reporta tal cual
        res["error"] = f"{type(e).__name__}: {e}"
        res["traceback"] = traceback.format_exc()[-2000:]
    finally:
        rep = cost_tracker.end_video()
    res["costo"] = {"usd": round(getattr(rep, "total_cost", 0.0) or 0.0, 4), "segundos": round(time.time() - t0, 1),
                    "llamadas": [{"servicio": e.service, "desc": e.description, "in": e.tokens_in,
                                  "out": e.tokens_out, "thinking": e.tokens_thinking, "usd": round(e.total_cost, 4)}
                                 for e in (getattr(rep, "entries", None) or [])]}
    _write(LAB / f"guion_{tema}_f13_abierto.json", res)
    if res.get("parrafos"):
        (LAB / f"NARRACION_{tema}_f13_abierto.md").write_text(narracion_md(tema, tag, esc, res), encoding="utf-8")
    c = _costos()
    c["corridas"].append({"corrida": tag, "usd": res["costo"]["usd"], "segundos": res["costo"]["segundos"],
                          "error": res.get("error")})
    c["usd_total"] = round(sum(x["usd"] for x in c["corridas"]), 4)
    _write(COSTOS, c)
    m = res.get("metricas") or {}
    print(f"[{tag}] " + (f"ERROR {res['error']} · " if res.get("error") else "")
          + (f"{m['palabras']} palabras ≈ {res['minutos']} min · bloqueantes {len(res['bloqueantes'])} · "
             f"por cap {[v[0] for v in m['palabras_por_cap'].values()]} · rep {res['repeticion_por_cap']} · " if m else "")
          + f"US$ {res['costo']['usd']:.3f} · total US$ {c['usd_total']:.3f}", flush=True)
    return res


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")                # -I ignora PYTHONIOENCODING
    import gpt_helpers
    gpt_helpers.TIMEOUT_S = 1200
    for tag in [a for a in sys.argv[1:] if a in TEMAS] or list(TEMAS):
        try:
            res = corrida(tag)
        except Parada as e:
            print(f"PARADA: {e}", flush=True)
            break
        if isinstance(res.get("error"), str) and res["error"].startswith("Parada"):
            print("PARADA: " + res["error"], flush=True)
            break


if __name__ == "__main__":
    main()
