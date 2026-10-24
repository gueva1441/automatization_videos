"""F21c §2 — el perfil de Orleans no tiene `nombres_lugar` (su `place_re` de F7 se escribió a mano): se genera con el
mismo paso que hoy produce el perfil (`research_v3.seed_profile`, 1 Flash) y se suma al vocabulario que ya tiene (F20).
Respaldo del actual: `_perfil_f21b.json`. Tope US$ 0.10 (una sola llamada; se mide con cost_tracker).
Uso: python -I lab/hyperframes/f21/f21c_perfil_orleans.py
"""
from __future__ import annotations

import json
import shutil
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LAB = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
TID = "ba6c3cac-f7r3"
TOPE = 0.10
# el mismo título de semilla que usó F20 para el vocabulario de Orleans (lab/hyperframes/f20/f20_corridas.py)
SEED = {"seed_title": "La Prisión Parroquial de Orleans durante el huracán Katrina: los presos abandonados en sus celdas "
                      "(Nueva Orleans, 29 de agosto de 2005)",
        "idioma_local": "inglés (Nueva Orleans, EE. UU.)"}


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    from cost_tracker import cost_tracker
    from researcher_steps import research_v3 as r3
    from script_engine.m01a_skeleton import STEPS_DIR
    d = STEPS_DIR / TID
    actual = json.loads((d / "_perfil.json").read_text(encoding="utf-8"))
    if actual.get("nombres_lugar"):
        print("ya tiene nombres_lugar: no se llama", flush=True)
        return
    if not (d / "_perfil_f21b.json").exists():
        shutil.copy2(d / "_perfil.json", d / "_perfil_f21b.json")
    t0 = time.time()
    cost_tracker.start_video(f"{TID}-f21c-perfil")
    try:
        prof = r3.seed_profile(SEED)
    finally:
        rep = cost_tracker.end_video()
    usd = round(getattr(rep, "total_cost", 0.0) or 0.0, 4)
    if usd > TOPE:
        print(f"PARADA: el perfil costó US$ {usd} > {TOPE}", flush=True)
    nuevo = {**prof, **{k: actual[k] for k in ("roles_testigo", "roles_antagonista", "sustantivos_conteo") if k in actual},
             "_f21c": "nombres_lugar/nombres_locales/place_re de seed_profile (Flash); vocabulario de F20"}
    (d / "_perfil.json").write_text(json.dumps(nuevo, ensure_ascii=False, indent=1), encoding="utf-8")
    res = {"usd": usd, "segundos": round(time.time() - t0, 1), "seed": SEED, "perfil": nuevo}
    (LAB / "f21c_perfil_orleans.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"US$ {usd} · nombres_lugar {nuevo.get('nombres_lugar')} · locales {nuevo.get('nombres_locales')} · "
          f"año {nuevo.get('anio_evento')}", flush=True)


if __name__ == "__main__":
    main()
