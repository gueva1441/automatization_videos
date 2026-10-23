"""F10 §4.2 (paso previo): completa el topic de Ycuá Bolaños en topics_db.

En F8 la semilla S1 solo pasó por research v3 + compuerta (`run_seed`); faltan 4a–4e (meta, canon visual, personas
documentadas) y la entrada en topics_db, que la tubería de producción necesita. Esto corre el camino LONG v3 de
`topic_researcher.research_topics` para esa semilla con el topic_id fijado en `f8s1-ycua-bolanos`, así `run_seed`
reusa las cachés de R1/R3 de F8 (sin pagar de nuevo la lectura de documentos).
Uso: python -I lab/hyperframes/f10/f10_topic_ycua.py
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
TOPIC = "f8s1-ycua-bolanos"


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")                # -I ignora PYTHONIOENCODING
    import topic_researcher as tr
    from cost_tracker import cost_tracker
    seeds = [s for s in tr._load_seeds() if s.get("seed_id") == TOPIC]
    if not seeds:
        raise SystemExit(f"la semilla {TOPIC} no está en el inbox")

    class _FixedUUID:
        def __str__(self) -> str:
            return TOPIC
    tr.uuid.uuid4 = lambda: _FixedUUID()                     # el topic_id = la carpeta de pasos de F8
    t0 = time.time()
    cost_tracker.start_video(f"{TOPIC}-m00")
    try:
        out = tr.research_topics(seeds=seeds, video_type="long")
    finally:
        rep = cost_tracker.end_video()
    res = {"topics": [t.get("id") for t in out], "usd": round(getattr(rep, "total_cost", 0.0) or 0.0, 4),
           "segundos": round(time.time() - t0, 1)}
    (Path(__file__).resolve().parent / "topic_ycua_costo.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    print(res, flush=True)


if __name__ == "__main__":
    main()
