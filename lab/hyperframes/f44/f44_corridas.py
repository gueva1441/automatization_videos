"""F44 §1 — A/B de la ficha del caso en Wittenoom: ¿la ficha mejora si ve el caso (ángulo, misterio, revelación)?

    A (producción, solo lectura): `data/scripts/_steps/<tid>/ficha_caso.json` (f23-1, 23:45) y `01a_escaleta.json`
      (f26-1, 23:51). No se regenera nada: se copia a `lab/hyperframes/f44/A/`.
    B (lab): el mismo `00_pool_v3.json` (md5 verificado) en `lab/hyperframes/f44/B/_steps/<tid>/` → ficha con
      `caso={angle, mystery, reveal}` del topic y el mismo título que A (f44-1, mismo modelo y esfuerzo) → escaleta
      `generate_escaleta_v2` (prompt vigente f26-1, sin columna) con el mismo topic dict que A (`fase1_5._topic_v3`:
      el `evidence_pool` de topics_db y el perfil del caso), `persist=False` y la salida escrita en el lab.
Una llamada paga por vez (ficha → escaleta). Freno antes de cada llamada: lo gastado (cost_tracker, sin `end_video`:
nada en data/) + lo que costó esa llamada en A (medido: ficha 0,3533; escaleta 1,8637 / 2 intentos) no pasa el tope.

    python lab/hyperframes/f44/f44_corridas.py a        → copia A
    python lab/hyperframes/f44/f44_corridas.py b        → ficha B → escaleta B (pagas)
"""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LAB = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
TID = "123bbb64-9fca-4395-8bf4-57d60e219ef1"
PROD = ROOT / "data" / "scripts" / "_steps" / TID
A_DIR = LAB / "A"
B_STEPS = LAB / "B" / "_steps"
B_DIR = B_STEPS / TID
COSTOS = LAB / "B" / "costos.json"
POOL_MD5 = "3eef2b448a82cfefa4abd4574341c985"       # handoff F44: el pool de A
TOPE_USD = 3.00                                     # handoff F44, tabla de constantes (Omar lo confirma)
USD_FICHA_A = 0.3533                                # medido: 01_v3_costos.json de A
USD_ESCALETA_LLAMADA_A = 1.8637 / 2                 # medido: escaleta A = 1,8637 en 2 intentos


class Parada(RuntimeError):
    pass


def _j(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def _w(p: Path, obj) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=1, default=str), encoding="utf-8")


def copia_a() -> None:
    A_DIR.mkdir(parents=True, exist_ok=True)
    for n in ("ficha_caso.json", f"FICHA_{TID}.md", "01a_escaleta.json", "01_v3_costos.json", "03_meta.json",
              "POOL_GATE.md"):
        shutil.copy2(PROD / n, A_DIR / n)
    print(f"A copiada a {A_DIR.relative_to(ROOT).as_posix()}")


def _gastado() -> float:
    from cost_tracker import cost_tracker
    cv = cost_tracker.current_video
    return round(cv.total_cost, 4) if cv else 0.0


def _freno(estimado: float, que: str) -> None:
    g = _gastado()
    if g + estimado > TOPE_USD:
        raise Parada(f"freno: {que} — gastado {g:.4f} + estimado {estimado:.4f} > tope {TOPE_USD:.2f}")
    print(f"  [freno] {que}: gastado {g:.4f} + estimado {estimado:.4f} ≤ {TOPE_USD:.2f} → sigue", flush=True)


def corre_b() -> None:
    import fase1_5
    from cost_tracker import cost_tracker
    from researcher_steps import ficha_caso as fc
    from script_engine import m01a_escaleta as me

    B_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(PROD / "00_pool_v3.json", B_DIR / "00_pool_v3.json")
    md5 = hashlib.md5((B_DIR / "00_pool_v3.json").read_bytes()).hexdigest()
    if md5 != POOL_MD5:
        raise Parada(f"pool copiado con md5 {md5} ≠ {POOL_MD5}")
    print(f"  pool B: md5 {md5} = A ✓", flush=True)
    a = _j(PROD / "ficha_caso.json")
    topic = fase1_5._topic_v3(TID)                   # solo lectura de topics_db y del _perfil.json de A
    caso = {k: topic.get(k) for k in ("angle", "mystery", "reveal")}
    _w(B_DIR / "caso.json", {"titulo": a["titulo"], **caso})
    pasos = []
    cost_tracker.start_video(f"f44-B-{TID}")         # en memoria; no se llama end_video (escribe en data/)

    _freno(USD_FICHA_A, "ficha B")
    t0, g0 = time.time(), _gastado()
    res = fc.run(TID, steps_dir=B_STEPS, title=a["titulo"], tag=TID, caso=caso)
    pasos.append({"paso": "ficha", "usd": round(_gastado() - g0, 4), "segundos": round(time.time() - t0, 1)})
    fb = _j(B_DIR / "ficha_caso.json")
    fb["usd"] = pasos[-1]["usd"]                     # como en A: el costo del paso, no el acumulado
    _w(B_DIR / "ficha_caso.json", fb)
    _w(COSTOS, {"total_usd": _gastado(), "pasos": pasos})
    print(f"  ficha B: {res['meta']['prompt_version']} · {res['meta']['conteos']} · sacados {res['meta']['sacados']}"
          f" · US$ {pasos[-1]['usd']}", flush=True)

    base = me.call_escaleta(None)                    # el mismo default que A (fase1_5.run_escaleta_v3, modelo=None)

    def call(*a_, **k):
        _freno(USD_ESCALETA_LLAMADA_A, f"escaleta B ({k.get('description')})")
        return base(*a_, **k)
    ficha_b = fc.load(TID, B_STEPS)
    pool = topic.get("evidence_pool") or {}
    log: list[str] = []
    gate = me.pool_gate_profile(topic, pool, persist=False, log=log)
    t0, g0 = time.time(), _gastado()
    try:
        esc = me.generate_escaleta_v2(topic, pool, ficha_b, call=call, log=log, persist=False, gate=gate,
                                      topic_id=TID)
        _w(B_DIR / "01a_escaleta.json", esc)
        estado = "ok"
    except me.EscaletaValidationError as e:
        estado = f"rechazada: {e}"
    finally:
        pasos.append({"paso": "escaleta", "usd": round(_gastado() - g0, 4), "segundos": round(time.time() - t0, 1)})
        _w(COSTOS, {"total_usd": _gastado(), "pasos": pasos})
        (LAB / "B" / "escaleta_log.txt").write_text("\n".join(log) + "\n", encoding="utf-8")
    print("\n".join(log))
    print(f"  escaleta B: {estado} · US$ {pasos[-1]['usd']} · total B US$ {_gastado()}", flush=True)


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    que = sys.argv[1] if len(sys.argv) > 1 else ""
    if que == "a":
        copia_a()
    elif que == "b":
        try:
            corre_b()
        except Parada as e:
            print(f"⛔ PARADA: {e}")
            return 1
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
