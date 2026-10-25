"""F22c — ¿la escaleta con columna sale más floja que sin columna? Sin cambios de código: el modelo del guion se elige
con `guion_v4.call_for`/`claude_helpers` (F22b).

    A1, A2   Ycuá: escaleta v2.1 SIN columna (lo que hace `fase1_5 --sin-columna`: `generate_escaleta(columna=None)`),
             Sol high → guion Opus 5.5 v5.2 (effort high)
    B1, B2   Ycuá: escaleta v2.1 CON la columna de F22 (`lab/hyperframes/f22/columna_ycua_f22.json`, no se regenera),
             Sol high → guion Opus 5.5 v5.2
    K        Kyshtym: guion Opus 5.5 v5.2 sobre `lab/hyperframes/f22/escaleta_kyshtym_f22.json` tal cual

Ficha v2 existente de cada tema y perfil del seed cargado (`f22_corridas._topic/_ficha`). Las escaletas NO se guardan en
`_steps` (no se pisa `01a_escaleta_f22.json`): van a `escaleta_ycua_f22c_<tag>.json`. Tope US$ 3.00 (costos_f22c.json):
antes de cada llamada, lo gastado + el peor caso (Sol 20 000 / Opus 32 000 tokens de salida) no puede pasarlo; una sola
facturación por llamada. Escaleta: 13 bloqueantes y una regeneración (si vuelve a fallar, ese tag no tiene guion).
Guion sin reparación (como F16–F22b). Cada paso se saltea si su salida ya existe.
Uso: python -I lab/hyperframes/f22c/f22c_corridas.py [A1 B1 A2 B2 K]
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LAB = Path(__file__).resolve().parent
F22, F22B = LAB.parent / "f22", LAB.parent / "f22b"
sys.path.insert(0, str(LAB))
sys.path.insert(1, str(ROOT))
sys.path.insert(2, str(F22))
sys.path.insert(3, str(F22B))
sys.path.insert(4, str(LAB.parent / "f13"))

TOPE = 3.00
MAX_OUT = {"gpt-6.1-sol": 20000, "claude-opus-5-5": 32000}   # A1 intento 1: Opus cortó en 20 000
COSTOS = LAB / "costos_f22c.json"
TAGS = {"A1": ("ycua", False), "B1": ("ycua", True), "A2": ("ycua", False), "B2": ("ycua", True), "K": ("kyshtym", None)}
GUION = ("claude-opus-5-5", "f22-1")


class Parada(RuntimeError):
    pass


def _md5(s: str) -> str:
    return hashlib.md5(s.encode("utf-8")).hexdigest()


def _write(p: Path, obj) -> None:
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding="utf-8")


def _costos() -> dict:
    return json.loads(COSTOS.read_text(encoding="utf-8")) if COSTOS.exists() else {"etapas": [], "usd_total": 0.0}


def _gastado() -> float:
    return sum(x["usd"] for x in _costos()["etapas"])


def _add_cost(tag: str, paso: str, modelo: str, rep, t0: float, extra: dict | None = None) -> dict:
    c = _costos()
    costo = {"tag": tag, "paso": paso, "modelo": modelo, "usd": round(getattr(rep, "total_cost", 0.0) or 0.0, 4),
             "segundos": round(time.time() - t0, 1),
             "llamadas": [{"servicio": e.service, "desc": e.description, "in": e.tokens_in, "out": e.tokens_out,
                           "thinking": e.tokens_thinking, "usd": round(e.total_cost, 4)}
                          for e in (getattr(rep, "entries", None) or [])], **(extra or {})}
    c["etapas"].append(costo)
    c["usd_total"] = round(sum(x["usd"] for x in c["etapas"]), 4)
    _write(COSTOS, c)
    print(f"  [{tag} {paso}] US$ {costo['usd']:.4f} · {costo['segundos']:.0f} s · tanda US$ {c['usd_total']:.4f}",
          flush=True)
    return costo


def make_call(modelo: str):
    """Freno (lo gastado + el peor caso ≤ TOPE) y UNA facturación por llamada; Sol o Opus, effort high."""
    from cost_tracker import cost_tracker
    if modelo.startswith("claude"):
        import claude_helpers as hx
    else:
        import gpt_helpers as hx
    hx.TIMEOUT_S = 1800
    pin, pout = hx.PRICES[modelo]
    total0 = _gastado()

    def _call(prompt, system_instruction=None, response_schema=None, thinking_budget=None, description=None):
        cur = cost_tracker.current_video.total_cost if cost_tracker.current_video else 0.0
        worst = (len(prompt) + len(system_instruction or "")) / 3 / 1e6 * pin + MAX_OUT[modelo] / 1e6 * pout
        if total0 + cur + worst > TOPE:
            raise Parada(f"tope antes de «{description}»: US$ {total0 + cur:.3f} + peor caso {worst:.3f} > {TOPE:.2f}")
        n = {"posts": 0}

        def post(body: dict) -> dict:
            if n["posts"]:
                raise Parada("la llamada ya facturó una vez (JSON roto o cortado): no hay reintento por el tope")
            body["max_tokens" if modelo.startswith("claude") else "max_completion_tokens"] = MAX_OUT[modelo]
            n["posts"] += 1
            return hx._post(body)
        return hx.make_call(modelo, "high", post=post)(prompt, system_instruction=system_instruction,
                                                       response_schema=response_schema, description=description)
    return _call


def escaleta(tag: str) -> dict | None:
    import f22_corridas as f22
    from cost_tracker import cost_tracker
    from script_engine import m01a_escaleta as ma
    tema, con_columna = TAGS[tag]
    if tema != "ycua":
        return json.loads((F22 / "escaleta_kyshtym_f22.json").read_text(encoding="utf-8"))
    out = LAB / f"escaleta_ycua_f22c_{tag}.json"
    if out.exists():
        print(f"[{tag} escaleta] ya existe: se usa", flush=True)
        return json.loads(out.read_text(encoding="utf-8"))
    if (LAB / f"escaleta_ycua_f22c_{tag}_rechazada.json").exists():
        print(f"[{tag} escaleta] rechazada en una corrida anterior: sin guion", flush=True)
        return None
    ficha, topic = f22._ficha("ycua"), f22._topic("ycua")
    col = json.loads((F22 / "columna_ycua_f22.json").read_text(encoding="utf-8")) if con_columna else None
    pool = topic["evidence_pool"]
    p1 = ma.build_prompt_v2(topic, pool, ficha, columna=col)
    (LAB / f"prompt_ycua_f22c_{tag}_escaleta.txt").write_text(
        f"===== SISTEMA (md5 {_md5(ma.SYSTEM_V2)}) =====\n{ma.SYSTEM_V2}\n\n===== USUARIO, intento 1 (md5 {_md5(p1)}) "
        f"=====\n{p1}\n", encoding="utf-8")
    log: list[str] = []
    crudos: list = []
    base = make_call("gpt-6.1-sol")

    def call(*a, **k):
        r = base(*a, **k)
        crudos.append(r)
        return r
    cost_tracker.start_video(f"f8s1-ycua-bolanos-f22c-{tag}-escaleta")
    t0 = time.time()
    err, esc = None, None
    try:
        esc = ma.generate_escaleta(topic, call=call, log=log, persist=False, ficha=ficha, columna=col)
    except Exception as e:  # noqa: BLE001
        err = f"{type(e).__name__}: {e}"
    finally:
        rep = cost_tracker.end_video()
    _write(LAB / f"escaleta_crudos_ycua_f22c_{tag}.json", crudos)
    _add_cost(tag, "escaleta", "gpt-6.1-sol", rep, t0, {"con_columna": con_columna, "error": err, "log": log,
                                                       "prompt_md5_intento1": {"sistema": _md5(ma.SYSTEM_V2),
                                                                               "usuario": _md5(p1)}})
    print("\n".join(log), flush=True)
    if esc is None:
        _write(LAB / f"escaleta_ycua_f22c_{tag}_rechazada.json", {"error": err, "log": log})
        if err and "Parada" in err and "tope" in err:
            raise Parada(err)
        print(f"[{tag} escaleta] PARADA: {err}", flush=True)
        return None
    _write(out, esc)
    (LAB / f"ESCALETA_ycua_f22c_{tag}.md").write_text(ma.to_markdown(esc, pool), encoding="utf-8")
    print(f"[{tag} escaleta] {len(esc['beats'])} beats · prompt {esc.get('prompt_version')} · columna "
          f"{'sí' if con_columna else 'no'}", flush=True)
    return esc


def guion(tag: str, esc: dict) -> None:
    import f22_corridas as f22
    from cost_tracker import cost_tracker
    from f13_corridas import PALABRAS_POR_SEG, repeticion_interna
    from f22b_corridas import narracion as narracion_md
    from script_engine import guion_v4 as g4
    from script_engine import m01b_guionista as mg
    tema = TAGS[tag][0]
    nom = f"{tema}_f22c_{tag}"
    out = LAB / f"guion_{nom}.json"
    if out.exists():
        print(f"[{tag} guion] ya existe: se saltea", flush=True)
        return
    modelo, version = GUION
    ficha, topic = f22._ficha(tema), f22._topic(tema)
    sis, usr = g4.system(version), g4.prompt(topic, esc, ficha=ficha, version=version)
    (LAB / f"prompt_{nom}_guion.txt").write_text(
        f"===== SISTEMA (md5 {_md5(sis)}) =====\n{sis}\n\n===== USUARIO (md5 {_md5(usr)}) =====\n{usr}\n", encoding="utf-8")
    res: dict = {"tag": tag, "tema": tema, "modelo": modelo, "esfuerzo": "high", "version": version,
                 "max_tokens": MAX_OUT[modelo], "prompt_md5": {"sistema": _md5(sis), "usuario": _md5(usr)},
                 "nota_b": g4.nota_b()}
    cost_tracker.start_video(f"{f22.TEMAS[tema]['tid']}-f22c-{tag}-guion")
    t0 = time.time()
    try:
        g = g4.write(topic, esc, call=make_call(modelo), ficha=ficha, version=version)
        res.update(prompt_version=g["prompt_version"], parrafos=g["parrafos"])
        res["bloqueantes"] = g4.bloqueantes(topic, esc, g["parrafos"], ficha=ficha, version=version)
        res["metricas"] = g4.metricas(topic, esc, g["parrafos"])
        res["repeticion_por_cap"] = {c["chapter_number"]: repeticion_interna(c["narration"])
                                     for c in mg.caps_text(esc, g["parrafos"])}
        res["minutos"] = round(res["metricas"]["palabras"] / PALABRAS_POR_SEG / 60, 1)
    except Exception as e:  # noqa: BLE001
        res["error"] = f"{type(e).__name__}: {e}"
        res["traceback"] = traceback.format_exc()[-2000:]
    finally:
        rep = cost_tracker.end_video()
    res["costo"] = _add_cost(tag, "guion", modelo, rep, t0)
    _write(out, res)
    if res.get("parrafos"):
        etxt = {"A1": "Escaleta v2.1 sin columna (Sol, F22c A1)", "A2": "Escaleta v2.1 sin columna (Sol, F22c A2)",
                "B1": "Escaleta v2.1 con la columna de F22 (Sol, F22c B1)",
                "B2": "Escaleta v2.1 con la columna de F22 (Sol, F22c B2)",
                "K": "Escaleta de Kyshtym de F22 (`escaleta_kyshtym_f22.json`)"}[tag]
        md = narracion_md(tag, esc, res, ficha, topic, modelo=modelo, version=version,
                          tema="Ycuá" if tema == "ycua" else "Kyshtym", fase="F22c", escaleta_txt=etxt)
        (LAB / f"NARRACION_{nom}.md").write_text(md, encoding="utf-8")
    m = res.get("metricas") or {}
    print(f"[{tag} guion] " + (f"ERROR {res['error']} · " if res.get("error") else "")
          + (f"{m['palabras']} palabras ≈ {res['minutos']} min · bloqueantes {len(res['bloqueantes'])} · citas "
             f"{m['citas']}" if m else ""), flush=True)
    if res.get("error") and "Parada" in res["error"] and "tope" in res["error"]:
        raise Parada(res["error"])


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    tags = [a for a in sys.argv[1:] if a in TAGS] or list(TAGS)
    for t in tags:
        try:
            esc = escaleta(t)
            if esc is not None:
                guion(t, esc)
        except Parada as x:
            print(f"PARADA ({t}): {x}", flush=True)
            break
    print(f"tanda US$ {_gastado():.4f}", flush=True)


if __name__ == "__main__":
    main()
