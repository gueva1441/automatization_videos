"""F11b — humo del helper GPT antes de las corridas: una llamada mínima por modelo (esquema JSON + esfuerzo), para no
gastar una corrida entera en un error de transporte. El costo se suma a costos_f11b.json (corrida «humo»).
Uso: python -I lab/hyperframes/f11b/f11b_humo.py
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
LAB = Path(__file__).resolve().parent
sys.path.insert(1, str(LAB))                                 # -I no pone la carpeta del script en sys.path


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    from cost_tracker import cost_tracker
    from script_engine import guion_v4 as g4
    from f11b_corridas import COSTOS, _costos, _write
    cost_tracker.start_video("f11b-humo")
    out = []
    try:
        for modelo in ("gpt-6.1-sol", "gpt-6-astra"):
            t0 = time.time()
            try:
                r = g4.call_for(modelo)("Devolvé el texto «hola» en el campo texto.", system_instruction="Respondé en JSON.",
                                        response_schema=g4.EDIT_SCHEMA, description=f"humo {modelo}")
                out.append({"modelo": modelo, "ok": True, "respuesta": r, "segundos": round(time.time() - t0, 1)})
            except Exception as e:  # noqa: BLE001
                out.append({"modelo": modelo, "ok": False, "error": f"{type(e).__name__}: {e}"})
    finally:
        rep = cost_tracker.end_video()
    usd = round(getattr(rep, "total_cost", 0.0) or 0.0, 4)
    for x in out:
        print(json.dumps(x, ensure_ascii=False), flush=True)
    print(f"humo US$ {usd:.4f}", flush=True)
    c = _costos()
    c["corridas"].append({"corrida": "humo", "modelo": "gpt-6.1-sol + gpt-6-astra", "usd": usd, "segundos": 0,
                          "error": None if all(x["ok"] for x in out) else "ver humo"})
    c["usd_total"] = round(sum(x["usd"] for x in c["corridas"]), 4)
    _write(COSTOS, c)
    _write(LAB / "humo_gpt.json", {"resultados": out, "usd": usd})


if __name__ == "__main__":
    main()
