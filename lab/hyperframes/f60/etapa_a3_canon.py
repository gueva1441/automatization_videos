# -*- coding: utf-8 -*-
"""F60 Etapa A3.2 paso 1 — canon visual NUEVO de Wittenoom con Opus, sobre la copia de lab (NUNCA topics_db ni _steps reales).

- ficha = fc.load(TID, <copia>/data/scripts/_steps) (00_pool_v3 y ficha_caso de la copia).
- topic leído con fase1_5._load_topic_by_id (lectura de topics_db; NO se llama asegurar_canon, que escribe con save_db).
- s4e.canon_desde_ficha(topic, ficha) envuelto en cost_tracker → a3/05_visual_canon_a3.json (+ a3/canon_a3.log).
- Imprime appearance_canon antes (canon de la copia) → después y condition_by_period por persona, para el PARÁ a mano.
Cero fotos. USO: PYTHONIOENCODING=utf-8 python lab/hyperframes/f60/etapa_a3_canon.py
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
F60 = Path(__file__).resolve().parent
A3 = F60 / "a3"
TID = "123bbb64-9fca-4395-8bf4-57d60e219ef1"
STEPS_COPIA = F60 / "base/data/scripts/_steps"
LOG: list[str] = []


def log(s: str) -> None:
    print(s, flush=True)
    LOG.append(s)


def main() -> int:
    A3.mkdir(exist_ok=True)
    from researcher_steps import step_4e_visual_canon as s4e
    from researcher_steps import ficha_caso as fc
    from fase1_5 import _load_topic_by_id, CANON_KEYS
    from cost_tracker import cost_tracker

    ficha = fc.load(TID, STEPS_COPIA)
    assert ficha, "sin ficha en la copia"
    topic = _load_topic_by_id(TID)
    viejo = json.loads((STEPS_COPIA / TID / "05_visual_canon.json").read_text(encoding="utf-8"))
    pedido = s4e.pedido_canon(topic, ficha)
    assert "- condition_by_period: una entrada por cada tramo de años" in pedido and "naval officer with focused" not in pedido
    log(f"pedido del canon: {len(pedido)} chars · trae condition_by_period y el ejemplo nuevo · modelo {s4e.MODELO_CANON} esfuerzo {s4e.ESFUERZO_CANON}")
    cost_tracker.start_video(TID)
    t0 = time.time()
    try:
        canon = s4e.canon_desde_ficha(topic, ficha)
    finally:
        r = cost_tracker.end_video()
        usd = round(getattr(r, "total_cost", 0.0) or 0.0, 4)
        seg = round(time.time() - t0, 1)
    log(f"canon nuevo: {seg} s · US$ {usd} · claves {sorted(canon.keys())}")
    faltan = [k for k in CANON_KEYS if k not in canon]
    log(f"CANON_KEYS faltantes: {faltan}")
    (A3 / "05_visual_canon_a3.json").write_text(json.dumps(canon, ensure_ascii=False, indent=2), encoding="utf-8")
    v_by = {p["name"]: p for p in viejo.get("documented_people") or []}
    log("\n== PERSONAS: appearance_canon antes → después · condition_by_period")
    for p in canon.get("documented_people") or []:
        v = v_by.get(p["name"]) or {}
        log(f"- {p['name']} (role: {p.get('role')}; era {p.get('era')}; age {p.get('age_at_event')})")
        log(f"    antes : {v.get('appearance_canon', '(no estaba)')}")
        log(f"    ahora : {p.get('appearance_canon')}")
        for c in p.get("condition_by_period") or []:
            log(f"    condition {c['years']}: {c['condition']}")
    nuevos = [p["name"] for p in canon.get("documented_people") or [] if p["name"] not in v_by]
    idos = [n for n in v_by if n not in {p["name"] for p in canon.get("documented_people") or []}]
    log(f"personas nuevas: {nuevos} · desaparecidas: {idos}")
    res = {"usd": usd, "segundos": seg, "faltan": faltan, "nuevas": nuevos, "idas": idos, "log": LOG}
    (A3 / "canon_a3.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    (A3 / "canon_a3.log").write_text("\n".join(LOG), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
