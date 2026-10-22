"""F8 §3: tres semillas por research v3 + compuerta del pool, SIN escaleta, guion ni imágenes.

Uso: python -I lab/hyperframes/f8/f8_semillas.py --seed S1|S2|S3 [--inbox]
    --inbox   solo agrega las tres semillas a data/selected_seeds.json (si no están) y sale
Por semilla deja en data/scripts/_steps/<topic>/: _perfil.json, fuentes.json, fuentes/ (+ manifest.json),
_r3_cache/, 00_pool_v3.json, POOL_GATE.md, _f8_costo.json; y copia POOL_GATE.md, fuentes.json, manifest.json y el
costo a lab/hyperframes/f8/semillas/<S#>/. Un rojo no se reintenta (§3): queda anotado qué faltó.
"""
from __future__ import annotations

import json
import shutil
import sys
import time
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
LAB = Path(__file__).resolve().parent / "semillas"

SEEDS = {
    "S1": {"seed_id": "f8s1-ycua-bolanos", "topic_id": "f8s1-ycua-bolanos",
           "seed_title": "El incendio del supermercado Ycuá Bolaños: las puertas que cerraron con la gente adentro "
                         "(Asunción, 1 de agosto de 2004)",
           "geo": "Asunción, Paraguay", "idioma_local": "español (Asunción, Paraguay); también guaraní",
           "idiomas_busqueda": ["es", "gn"]},
    "S2": {"seed_id": "f8s2-cromanon", "topic_id": "f8s2-cromanon",
           "seed_title": "La tragedia de República Cromañón: 194 muertos en un boliche con las salidas de emergencia "
                         "encadenadas (Buenos Aires, 30 de diciembre de 2004)",
           "geo": "Buenos Aires, Argentina", "idioma_local": "español (Buenos Aires, Argentina)",
           "idiomas_busqueda": ["es"]},
    "S3": {"seed_id": "f8s3-vajont", "topic_id": "f8s3-vajont",
           "seed_title": "La represa de Vajont: la ola que borró Longarone y los ingenieros que sabían "
                         "(Italia, 9 de octubre de 1963)",
           "geo": "Longarone, Véneto, Italia", "idioma_local": "italiano (Longarone, Véneto, Italia); también español",
           "idiomas_busqueda": ["it", "en", "es"]},
}
COMMON = {"discovery_mode": "manual_f8", "root_niche": "tragedias", "tags": ["tragedia", "negligencia", "juicio"],
          "created_at": "2026-10-22T00:00:00", "nota": "F8 §3: solo research v3 + compuerta; Omar elige al volver"}


def to_inbox() -> None:
    from config import DATA_DIR
    f = DATA_DIR / "selected_seeds.json"
    payload = json.loads(f.read_text(encoding="utf-8")) if f.exists() else {"seeds": []}
    have = {s.get("seed_id") for s in payload.get("seeds", [])}
    for k, s in SEEDS.items():
        if s["seed_id"] not in have:
            payload.setdefault("seeds", []).append({**COMMON, **{x: s[x] for x in s if x != "topic_id"}})
            print(f"  inbox: + {k} {s['seed_id']}")
    f.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def run(key: str) -> None:
    from cost_tracker import cost_tracker
    from researcher_steps import pool_gate as pg
    from researcher_steps import research_v3 as r3
    from script_engine.m01a_skeleton import STEPS_DIR
    seed = {**COMMON, **SEEDS[key]}
    topic = seed["topic_id"]
    steps = STEPS_DIR / topic
    out = LAB / key
    out.mkdir(parents=True, exist_ok=True)
    log: list[str] = []
    t0 = time.time()
    cost_tracker.start_video(topic)
    estado = "ok"
    try:
        _, _, gate = r3.run_seed(seed, topic, steps, log=log)
        color = gate["color"] if gate else "?"
    except pg.PoolGateRed as e:
        color, estado = pg.RED, "rojo: " + "; ".join(e.gate["motivos"])
    except Exception as e:  # noqa: BLE001 — se anota y se sigue (§3: no reintentar)
        color, estado = "error", f"{type(e).__name__}: {e}"
        log.append(traceback.format_exc())
    finally:
        rep = cost_tracker.end_video()
    costo = {"usd": round(getattr(rep, "total_cost", 0.0) or 0.0, 4), "segundos": round(time.time() - t0, 1),
             "color": color, "estado": estado}
    (steps / "_f8_costo.json").write_text(json.dumps(costo, ensure_ascii=False, indent=1), encoding="utf-8")
    (out / "run.log").write_text("\n".join(log), encoding="utf-8")
    for src, dst in ((steps / "POOL_GATE.md", "POOL_GATE.md"), (steps / "fuentes.json", "fuentes.json"),
                     (steps / "fuentes" / "manifest.json", "manifest.json"), (steps / "_f8_costo.json", "costo.json"),
                     (steps / "_perfil.json", "perfil.json")):
        if src.exists():
            shutil.copy2(src, out / dst)
    print(f"[{key}] {topic}: {color} · {estado} · US$ {costo['usd']} · {costo['segundos']} s", flush=True)


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")                # -I ignora PYTHONIOENCODING
    a = sys.argv[1:]
    if "--inbox" in a:
        to_inbox()
        return
    run(a[a.index("--seed") + 1])


if __name__ == "__main__":
    main()
