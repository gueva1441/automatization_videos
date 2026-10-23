"""F12 §2 — la ficha del caso de Ycuá (`f8s1-ycua-bolanos`): UNA llamada a gpt-6.1-sol high → chequeo determinista →
ficha_caso.json + FICHA_ycua.md en _steps/f8s1-ycua-bolanos/ y en lab/hyperframes/f12/. No corre escaleta ni guion;
no toca el pool ni topics_db.

Tope US$ 0.50. Antes de la llamada se estima el costo de entrada (caracteres / 3, conservador) y el tope de salida +
razonamiento (`max_completion_tokens`) se fija para que lo peor posible no pase el tope. Una sola llamada: si la API
quiere reintentar después de una llamada que ya facturó (JSON roto), PARADA.
Uso: python -I lab/hyperframes/f12/f12_ficha.py
"""
from __future__ import annotations

import json
import sys
import time
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
LAB = Path(__file__).resolve().parent
TOPE_USD = 0.50
TID, TAG, TITULO = "f8s1-ycua-bolanos", "ycua", "Ycuá Bolaños (Asunción, 1 de agosto de 2004)"
POOL_MD5 = "5f3c6d0bc31ebf868dd432b2c79fdcec"
COSTOS = LAB / "costos_f12.json"


class Parada(RuntimeError):
    pass


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")                # -I ignora PYTHONIOENCODING
    import hashlib

    import gpt_helpers
    from cost_tracker import cost_tracker
    from researcher_steps import ficha_caso as fc
    from script_engine.m01a_skeleton import STEPS_DIR
    raw_pool = (STEPS_DIR / TID / "00_pool_v3.json").read_bytes()
    if hashlib.md5(raw_pool).hexdigest() != POOL_MD5:
        raise SystemExit("00_pool_v3.json no es el fijado: PARADA")
    pool = json.loads(raw_pool.decode("utf-8"))
    if "--rechequear" in sys.argv:
        # el chequeo determinista otra vez, sobre la MISMA salida del modelo (ficha_crudo_ycua.json): sin llamada
        raw = json.loads((LAB / "ficha_crudo_ycua.json").read_text(encoding="utf-8"))
        costo = json.loads(COSTOS.read_text(encoding="utf-8"))
        res = fc.save(TID, raw, raw_pool, steps_dir=STEPS_DIR, title=TITULO, tag=TAG, out_dirs=[LAB],
                      usd=costo["usd"])
        _final(res, {k: v for k, v in costo.items() if k not in ("corrida", "error")}, STEPS_DIR)
        return
    sis, usr = fc.system(), fc.prompt(pool, TITULO)
    pin, pout = gpt_helpers.PRICES[fc.MODELO]
    in_usd = (len(sis) + len(usr)) / 3 / 1e6 * pin             # ≥ lo real (≈ 3.3–3.6 caracteres por token)
    max_out = int((TOPE_USD - in_usd) / pout * 1e6) - 500
    print(f"entrada ≈ US$ {in_usd:.3f} (cota) · max_completion_tokens {max_out:,} · peor caso US$ "
          f"{in_usd + max_out / 1e6 * pout:.3f}", flush=True)
    n = {"posts": 0}

    def post(body: dict) -> dict:
        if n["posts"]:
            raise Parada("la llamada ya facturó una vez (JSON roto o cortado): no hay reintento por el tope")
        body["max_completion_tokens"] = max_out
        n["posts"] += 1
        return gpt_helpers._post(body)

    gpt_helpers.TIMEOUT_S = 1800                            # 50 k de entrada + razonamiento high: más de 600 s
    call = gpt_helpers.make_call(fc.MODELO, fc.ESFUERZO, post=post)
    cost_tracker.start_video(f"{TID}-f12-ficha")
    t0 = time.time()
    res: dict = {}
    try:
        res = fc.run(TID, steps_dir=STEPS_DIR, title=TITULO, tag=TAG, out_dirs=[LAB], call=call)
    except Exception as e:  # noqa: BLE001 — se reporta tal cual
        res = {"error": f"{type(e).__name__}: {e}", "traceback": traceback.format_exc()[-2000:]}
    finally:
        rep = cost_tracker.end_video()
    costo = {"usd": round(getattr(rep, "total_cost", 0.0) or 0.0, 4), "segundos": round(time.time() - t0, 1),
             "llamadas": [{"servicio": e.service, "desc": e.description, "in": e.tokens_in, "out": e.tokens_out,
                           "thinking": e.tokens_thinking, "usd": round(e.total_cost, 4)}
                          for e in (getattr(rep, "entries", None) or [])],
             "max_completion_tokens": max_out, "caracteres": {"sistema": len(sis), "usuario": len(usr)}}
    COSTOS.write_text(json.dumps({"corrida": "ficha_ycua", **costo, "error": res.get("error")}, ensure_ascii=False,
                                 indent=1), encoding="utf-8")
    if res.get("error"):
        print("ERROR / PARADA: " + res["error"], flush=True)
        sys.exit(2)
    (LAB / "ficha_crudo_ycua.json").write_text(json.dumps(res["crudo"], ensure_ascii=False, indent=1),
                                               encoding="utf-8")
    _final(res, costo, STEPS_DIR)


def _final(res: dict, costo: dict, steps_dir: Path) -> None:
    """El json de la ficha lleva además el costo medido; resumen en pantalla."""
    for d in (steps_dir / TID, LAB):
        p = d / "ficha_caso.json"
        f = json.loads(p.read_text(encoding="utf-8"))
        f["costo"] = costo
        p.write_text(json.dumps(f, ensure_ascii=False, indent=1), encoding="utf-8")
    m = res["meta"]
    print(f"conteos crudo {m['conteos_crudo']}", flush=True)
    print(f"conteos ficha {m['conteos']} · sacados por el chequeo {m['sacados']} · US$ {costo['usd']:.3f} · "
          f"{costo['segundos']:.0f} s", flush=True)
    for s in res["sacados"]:
        print(f"  sacado [{s['seccion']}] {s['que'][:90]} → {s['motivo'][:160]}", flush=True)


if __name__ == "__main__":
    main()
