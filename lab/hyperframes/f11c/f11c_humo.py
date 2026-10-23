"""F11c §1.2 — humo de `gemini-4-argon` antes de las corridas: UNA llamada mínima (esquema JSON, sin temperature ni
thinking) para confirmar que la llave lo acepta. Si falla: PARADA y se reporta; no se reemplaza por otro modelo.
El costo se suma a costos_f11c.json (corrida «humo»).
Uso: python -I lab/hyperframes/f11c/f11c_humo.py
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
LAB = Path(__file__).resolve().parent
COSTOS = LAB / "costos_f11c.json"
MODELO = "gemini-4-argon"


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")                # -I ignora PYTHONIOENCODING
    from cost_tracker import cost_tracker
    import gemini_helpers as gh
    schema = {"type": "OBJECT", "properties": {"texto": {"type": "STRING"}}, "required": ["texto"]}
    cost_tracker.start_video("f11c-humo")
    t0 = time.time()
    try:
        r = gh.make_call(MODELO)("Devolvé el texto «hola» en el campo texto.", system_instruction="Respondé en JSON.",
                                 response_schema=schema, description=f"humo {MODELO}")
        out = {"modelo": MODELO, "ok": True, "respuesta": r, "segundos": round(time.time() - t0, 1)}
    except Exception as e:  # noqa: BLE001 — se reporta tal cual (sin la llave: el SDK no la incluye en el error)
        out = {"modelo": MODELO, "ok": False, "error": f"{type(e).__name__}: {str(e)[:500]}"}
    finally:
        rep = cost_tracker.end_video()
    usd = round(getattr(rep, "total_cost", 0.0) or 0.0, 5)
    out["usd"] = usd
    out["llamadas"] = [{"servicio": e.service, "in": e.tokens_in, "out": e.tokens_out, "thinking": e.tokens_thinking,
                        "usd": round(e.total_cost, 5)} for e in (getattr(rep, "entries", None) or [])]
    print(json.dumps(out, ensure_ascii=False), flush=True)
    c = json.loads(COSTOS.read_text(encoding="utf-8")) if COSTOS.exists() else {"corridas": [], "usd_total": 0.0}
    c["corridas"].append({"corrida": "humo", "modelo": MODELO, "usd": usd, "segundos": out.get("segundos", 0),
                          "error": out.get("error")})
    c["usd_total"] = round(sum(x["usd"] for x in c["corridas"]), 5)
    COSTOS.write_text(json.dumps(c, ensure_ascii=False, indent=1), encoding="utf-8")
    (LAB / "humo_argon.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    if not out["ok"]:
        print("PARADA: la llave no acepta gemini-4-argon", flush=True)
        sys.exit(2)


if __name__ == "__main__":
    main()
