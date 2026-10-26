"""F29 §D — Sonnet vs Flash como realizador en los caps 5 y 6 de Vajont.

El paso de forma del realizador (gfx_pool: para cada candidato elegido, la cláusula literal del recorte entre hasta 3
opciones; tipo, ventana, lado y duración los decide el realizador de forma determinista) corre con `claude-sonnet-5-5`
vía claude_helpers (effort low, JSON sin esquema forzado, respuesta cruda guardada), con el MISMO prompt que Flash: solo
cambia la llamada (`gfx_pool.FORMA_CALL`). Flash = lo que salió en C (`output/f8s3-vajont-f29`).
Copia del topic `f8s3-vajont-f29d` (mismos insumos que C) con los planes de ch01–ch04 de C (lo «ya mostrado» antes del
cap 5 es el mismo). Render de ch05 y ch06 con `fase2b --only-cap` en este proceso. Tope Claude US$ 2.
Salidas en `output/f8s3-vajont-f29/d/`: ch05_gfx_{flash,sonnet}.mp4, ch06_gfx_{flash,sonnet}.mp4 y sus planes;
`lab/hyperframes/f29/d/` costos, tiempos, crudos.
Uso: PYTHONIOENCODING=utf-8 python -I lab/hyperframes/f29/d/f29d_sonnet.py
"""
from __future__ import annotations

import json
import shutil
import sys
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path[:0] = [str(ROOT), str(ROOT / "lab" / "hyperframes" / "f29" / "c"), str(ROOT / "lab" / "hyperframes" / "f26" / "b")]
LAB = Path(__file__).resolve().parent
C_ID, D_ID = "f8s3-vajont-f29", "f8s3-vajont-f29d"
C_WORK = ROOT / "output" / C_ID / "_fase2b_work"
D_WORK = ROOT / "output" / D_ID / "_fase2b_work"
SALIDA = ROOT / "output" / C_ID / "d"
MODELO, EFFORT, TOPE = "claude-sonnet-5-5", "low", 2.00
CAPS = ("ch05", "ch06")
_LOCK = threading.Lock()
COSTOS = LAB / "costos_f29d.json"


def _costos() -> dict:
    return json.loads(COSTOS.read_text(encoding="utf-8")) if COSTOS.exists() else {"llamadas": [], "usd": 0.0}


def sonnet_call():
    import claude_helpers as hx

    def post(body: dict) -> dict:
        pin, pout = hx.PRICES[MODELO]
        worst = len(json.dumps(body)) / 2.5 / 1e6 * pin + 8000 / 1e6 * pout
        with _LOCK:
            if _costos()["usd"] + worst > TOPE:
                raise RuntimeError(f"tope Claude {TOPE}")
        t0 = time.time()
        r = hx._post(body)
        (LAB / "crudos").mkdir(exist_ok=True)
        (LAB / "crudos" / f"respuesta_{int(t0 * 1000)}.json").write_text(json.dumps(r, ensure_ascii=False, indent=1),
                                                                        encoding="utf-8")
        u = r.get("usage") or {}
        with _LOCK:
            c = _costos()
            c["llamadas"].append({"in": u.get("input_tokens"), "out": u.get("output_tokens"), "stop": r.get("stop_reason"),
                                  "usd": round(hx.cost_of(MODELO, u), 5), "segundos": round(time.time() - t0, 1)})
            c["usd"] = round(sum(x["usd"] for x in c["llamadas"]), 5)
            COSTOS.write_text(json.dumps(c, ensure_ascii=False, indent=1), encoding="utf-8")
        return r
    base = hx.make_call(MODELO, EFFORT, post=post)

    def _call(prompt, system_instruction=None, response_schema=None, thinking_budget=None, description=None):
        return base(prompt, system_instruction=system_instruction, response_schema=None, description=description)
    return _call


def preparar() -> None:
    import f29c_vajont as fc
    fc.DST = D_ID
    fc.preparar()
    for k in range(1, 5):
        f = C_WORK / f"gfx_plan_ch{k:02d}.resolved.json"
        if f.exists():
            shutil.copy2(f, D_WORK / f.name)


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    import f26b_produccion as f26b
    if f26b._firefox_open() or f26b._ram_free_gb() <= 14:
        raise SystemExit("no arranca: Firefox abierto o RAM ≤ 14 GB")
    preparar()
    SALIDA.mkdir(parents=True, exist_ok=True)
    for cap in CAPS:                                       # lo de Flash (C), apartado con su nombre
        for src, dst in ((C_WORK / f"{cap}_gfx.mp4", SALIDA / f"{cap}_gfx_flash.mp4"),
                         (C_WORK / f"gfx_plan_{cap}.resolved.json", SALIDA / f"gfx_plan_{cap}_flash.resolved.json")):
            if src.exists() and not dst.exists():
                shutil.copy2(src, dst)
    import fase2b
    from cost_tracker import cost_tracker
    from script_engine import gfx_pool
    gfx_pool.FORMA_CALL = sonnet_call()
    tiempos = {}
    for cap in CAPS:
        g0 = sum(e.total_cost for e in cost_tracker._all_entries() if "gemini" in e.service.lower())
        t0 = time.time()
        sys.argv = ["fase2b.py", D_ID, "--only-cap", cap, "--reuse-visuals", "--gfx", "--gfx-sparse", "--gfx-quality",
                    "looks"]
        try:
            rc = fase2b.main()
        except SystemExit as e:
            rc = e.code
        tiempos[cap] = {"rc": rc, "segundos": round(time.time() - t0, 1),
                        "gemini_usd": round(sum(e.total_cost for e in cost_tracker._all_entries()
                                                if "gemini" in e.service.lower()) - g0, 4)}
        for src, dst in ((D_WORK / f"{cap}_gfx.mp4", SALIDA / f"{cap}_gfx_sonnet.mp4"),
                         (D_WORK / f"gfx_plan_{cap}.resolved.json", SALIDA / f"gfx_plan_{cap}_sonnet.resolved.json")):
            if src.exists():
                shutil.copy2(src, dst)
        print(f"[{cap}] {tiempos[cap]}", flush=True)
    c = _costos()
    (LAB / "tiempos_f29d.json").write_text(json.dumps({"caps": tiempos, "claude_usd": c["usd"]}, ensure_ascii=False,
                                                      indent=1), encoding="utf-8")
    print(f"Claude US$ {c['usd']} · {tiempos}", flush=True)


if __name__ == "__main__":
    main()
