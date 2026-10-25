"""F22d — Kyshtym con los caminos nuevos por defecto: ficha de F22 (`lab/hyperframes/f22/ficha_kyshtym_f22.json`, la
misma que `_steps/f18-kyshtym-mayak/ficha_caso.json`) → escaleta v2.1 SIN columna (Sol high, `columna=None`, el camino
por defecto de fase1_5 desde F22d) → guion v5.2 con el modelo del guion por defecto (`guion_v4.DEFAULT_MODELO_GUION` =
claude-opus-5-5, effort high, max_tokens 32 000).

Tope US$ 1.50 (costos_f22d.json): antes de cada llamada, lo gastado + el peor caso (Sol 20 000 / Opus 32 000 tokens
de salida) no puede pasarlo; una facturación por llamada. Escaleta con sus 13 bloqueantes y una regeneración; guion
sin reparación (como F16–F22c). La escaleta no se guarda en `_steps`. Cada paso se saltea si su salida ya existe.
Salidas: ESCALETA_kyshtym.md, escaleta_kyshtym_f22d.json, NARRACION_kyshtym_f22d.md, guion_kyshtym_f22d.json.
Uso: python -I lab/hyperframes/f22d/f22d_corridas.py
"""
from __future__ import annotations

import json
import sys
import time
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LAB = Path(__file__).resolve().parent
F22 = LAB.parent / "f22"
sys.path[:0] = [str(LAB), str(ROOT), str(F22), str(LAB.parent / "f22b"), str(LAB.parent / "f22c"), str(LAB.parent / "f13")]
import f22c_corridas as f22c  # noqa: E402

f22c.TOPE = 1.50                                   # make_call y _add_cost leen estos globales al llamar
f22c.COSTOS = LAB / "costos_f22d.json"
TEMA = "kyshtym"


def escaleta() -> dict | None:
    import f22_corridas as f22
    from cost_tracker import cost_tracker
    from script_engine import m01a_escaleta as ma
    out = LAB / "escaleta_kyshtym_f22d.json"
    if out.exists():
        print("[escaleta] ya existe: se usa", flush=True)
        return json.loads(out.read_text(encoding="utf-8"))
    ficha, topic = f22._ficha(TEMA), f22._topic(TEMA)
    pool = topic["evidence_pool"]
    p1 = ma.build_prompt_v2(topic, pool, ficha)
    (LAB / "prompt_kyshtym_f22d_escaleta.txt").write_text(
        f"===== SISTEMA (md5 {f22c._md5(ma.SYSTEM_V2)}) =====\n{ma.SYSTEM_V2}\n\n===== USUARIO, intento 1 (md5 "
        f"{f22c._md5(p1)}) =====\n{p1}\n", encoding="utf-8")
    log: list[str] = []
    crudos: list = []
    base = f22c.make_call("gpt-6.1-sol")

    def call(*a, **k):
        r = base(*a, **k)
        crudos.append(r)
        return r
    cost_tracker.start_video("f18-kyshtym-mayak-f22d-escaleta")
    t0 = time.time()
    err, esc = None, None
    try:
        esc = ma.generate_escaleta(topic, call=call, log=log, persist=False, ficha=ficha, columna=None)
    except Exception as e:  # noqa: BLE001
        err = f"{type(e).__name__}: {e}"
    finally:
        rep = cost_tracker.end_video()
    f22c._write(LAB / "escaleta_crudos_kyshtym_f22d.json", crudos)
    f22c._add_cost("K", "escaleta", "gpt-6.1-sol", rep, t0, {"error": err, "log": log})
    print("\n".join(log), flush=True)
    if esc is None:
        print(f"PARADA (escaleta): {err}", flush=True)
        return None
    f22c._write(out, esc)
    (LAB / "ESCALETA_kyshtym.md").write_text(ma.to_markdown(esc, pool), encoding="utf-8")
    print(f"[escaleta] {len(esc['beats'])} beats · {esc.get('prompt_version')} · sin columna", flush=True)
    return esc


def guion(esc: dict) -> None:
    import f22_corridas as f22
    from cost_tracker import cost_tracker
    from f13_corridas import PALABRAS_POR_SEG, repeticion_interna
    from f22b_corridas import narracion as narracion_md
    from script_engine import guion_v4 as g4
    from script_engine import m01b_guionista as mg
    out = LAB / "guion_kyshtym_f22d.json"
    if out.exists():
        print("[guion] ya existe: se saltea", flush=True)
        return
    modelo, version = g4.DEFAULT_MODELO_GUION, g4.PROMPT_VERSION
    ficha, topic = f22._ficha(TEMA), f22._topic(TEMA)
    sis, usr = g4.system(version), g4.prompt(topic, esc, ficha=ficha, version=version)
    (LAB / "prompt_kyshtym_f22d_guion.txt").write_text(
        f"===== SISTEMA (md5 {f22c._md5(sis)}) =====\n{sis}\n\n===== USUARIO (md5 {f22c._md5(usr)}) =====\n{usr}\n",
        encoding="utf-8")
    res: dict = {"tema": TEMA, "modelo": modelo, "esfuerzo": g4.ESFUERZO.get(modelo), "version": version,
                 "max_tokens": f22c.MAX_OUT[modelo],
                 "prompt_md5": {"sistema": f22c._md5(sis), "usuario": f22c._md5(usr)}, "nota_b": g4.nota_b()}
    cost_tracker.start_video("f18-kyshtym-mayak-f22d-guion")
    t0 = time.time()
    try:
        g = g4.write(topic, esc, call=f22c.make_call(modelo), ficha=ficha, version=version)
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
    res["costo"] = f22c._add_cost("K", "guion", modelo, rep, t0)
    f22c._write(out, res)
    if res.get("parrafos"):
        (LAB / "NARRACION_kyshtym_f22d.md").write_text(
            narracion_md("K", esc, res, ficha, topic, modelo=modelo, version=version, tema="Kyshtym", fase="F22d",
                         escaleta_txt="Escaleta v2.1 sin columna (Sol, F22d)"), encoding="utf-8")
    m = res.get("metricas") or {}
    print("[guion] " + (f"ERROR {res['error']} · " if res.get("error") else "")
          + (f"{m['palabras']} palabras ≈ {res['minutos']} min · bloqueantes {len(res['bloqueantes'])} · citas "
             f"{m['citas']}" if m else ""), flush=True)


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    try:
        esc = escaleta()
        if esc is not None:
            guion(esc)
    except f22c.Parada as x:
        print(f"PARADA: {x}", flush=True)
    print(f"tanda US$ {f22c._gastado():.4f}", flush=True)


if __name__ == "__main__":
    main()
