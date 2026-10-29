# -*- coding: utf-8 -*-
"""F50d C — 3 llamadas al canon desde la ficha sobre Wittenoom, en paralelo:
- corrida 1 = `fase1_5.asegurar_canon` (como en producción: la marca nueva no coincide, rehace el canon y lo guarda
  en topics_db y en 05_visual_canon.json);
- corridas 2 y 3 = `step_4e.canon_desde_ficha`, sin guardar en topics_db (solo medida).
El costo de las 3 va en UNA sesión de cost_tracker (`f50d-canon-varianza`, en cost_history): el tracker es uno solo
por proceso y no puede medir llamadas en paralelo por separado. En 01_v3_costos.json queda un paso «canon (F50d, 3
corridas)» con el total. Salidas: canon_corrida_{1,2,3}.json y CANON_VARIANZA.md.
Uso: python lab/hyperframes/f50d/canon_varianza.py
"""
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
F50D = Path(__file__).resolve().parent
TID = "123bbb64-9fca-4395-8bf4-57d60e219ef1"


def resumen(c: dict) -> dict:
    era = c.get("era_visual_canon") or {}
    return {"grupos": [{"id": g.get("id"), "where_when": g.get("where_when"),
                        "tramos": [t.get("years") for t in g.get("clothing_by_period") or []]}
                       for g in c.get("people_groups") or []],
            "periods": [p.get("years") for p in era.get("periods") or []],
            "primary_decade": era.get("primary_decade"), "spans": era.get("spans")}


def main() -> int:
    import fase1_5
    from cost_tracker import cost_tracker
    from researcher_steps import ficha_caso as fc
    from researcher_steps import step_4e_visual_canon as s4e
    from script_engine.topics_db import get_topic_by_id
    topic = get_topic_by_id(TID)
    ficha = fc.load(TID, fase1_5.STEPS_DIR)
    marca_vieja = topic.get("canon_ficha_md5")
    pasos = []
    fase1_5._step_cost = lambda tid, label, fn: pasos.append(label) or fn()   # el costo lo mide la sesión de abajo
    log: list[str] = []
    cost_tracker.start_video("f50d-canon-varianza")
    t0 = time.time()
    try:
        with ThreadPoolExecutor(max_workers=3) as ex:
            f1 = ex.submit(fase1_5.asegurar_canon, TID, topic, log)
            f2 = ex.submit(s4e.canon_desde_ficha, topic, ficha)
            f3 = ex.submit(s4e.canon_desde_ficha, topic, ficha)
            t1 = f1.result()
            c = [{k: t1.get(k) for k in fase1_5.CANON_KEYS}, f2.result(), f3.result()]
    finally:
        r = cost_tracker.end_video()
    usd = round(getattr(r, "total_cost", 0.0) or 0.0, 4)
    seg = round(time.time() - t0, 1)
    costos = fase1_5.STEPS_DIR / TID / "01_v3_costos.json"
    d = json.loads(costos.read_text(encoding="utf-8")) if costos.exists() else {}
    d.setdefault("_corridas", []).append({"paso": "canon (F50d, 3 corridas en paralelo; la 1 queda)", "usd": usd,
                                          "segundos": seg})
    costos.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    for i, x in enumerate(c, start=1):
        (F50D / f"canon_corrida_{i}.json").write_text(json.dumps(x, ensure_ascii=False, indent=1), encoding="utf-8")

    rs = [resumen(x) for x in c]
    L = ["# CANON_VARIANZA — 3 corridas del canon desde la ficha (Wittenoom, F50d C)", "",
         "Salida de `python lab/hyperframes/f50d/canon_varianza.py`. Flash, en paralelo. La corrida 1 es "
         "`asegurar_canon` (queda en producción: topics_db y `05_visual_canon.json`); la 2 y la 3 no se guardan.",
         f"Marca: {str(marca_vieja)[:8]} → {str(t1.get('canon_ficha_md5'))[:8]} · pasos que corrió asegurar_canon: "
         f"{pasos} · log: {' | '.join(s.strip() for s in log)}",
         f"Costo de las 3 (cost_tracker `f50d-canon-varianza`): US$ {usd} · {seg} s", "",
         "| corrida | grupos | periods | primary_decade · spans |", "|---|---:|---|---|"]
    L += [f"| {i} | {len(x['grupos'])} | {' · '.join(map(str, x['periods'])) or '—'} | "
          f"{x['primary_decade']} · {x['spans']} |" for i, x in enumerate(rs, start=1)]
    for i, x in enumerate(rs, start=1):
        L += ["", f"## Corrida {i}" + (" (en producción)" if i == 1 else ""), "",
              "| grupo | where_when | clothing_by_period |", "|---|---|---|"]
        L += [f"| `{g['id']}` | {g['where_when']} | {' · '.join(map(str, g['tramos'])) or '—'} |" for g in x["grupos"]]
    ids = [set(g["id"] for g in x["grupos"]) for x in rs]
    L += ["", f"Grupos en las 3: {sorted(ids[0] & ids[1] & ids[2]) or '—'}",
          f"Solo en alguna: {sorted((ids[0] | ids[1] | ids[2]) - (ids[0] & ids[1] & ids[2])) or '—'}", ""]
    (F50D / "CANON_VARIANZA.md").write_text("\n".join(L), encoding="utf-8")
    print(json.dumps({"usd": usd, "seg": seg, "pasos": pasos, "log": log,
                      "corridas": [{"grupos": len(x["grupos"]), "periods": x["periods"]} for x in rs]},
                     ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
