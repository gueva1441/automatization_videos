"""F7b: R3 extracción por documento + R4 merge/contaminación + R5 verificación por texto → pool de Orleans v3-research.

Lee data/scripts/_steps/ba6c3cac-f7r3/fuentes/manifest.json (F7a). Por documento OK: 1 Pro por trozo de 60 k
caracteres (caché cruda en _r3_cache/), ítems validados en pool_doc_<id>.json. Después merge, contaminación, canon,
geocodificación y verificación literal → 00_pool_v3.json (y una copia en lab/hyperframes/f7/). Métricas contra el pool
de f6v3 (data/scripts/_steps/ba6c3cac-f6v3/01_facts_sources.json) → lab/hyperframes/f7/F7b_pool.md.
Uso: python -I lab/hyperframes/f7/f7b_pool_orleans.py [--solo F05] [--sin-llm]
    --solo F05   extrae solo ese documento (piloto) y no arma el pool
    --sin-llm    no llama a Pro: usa solo lo que está en caché (re-armar el pool gratis)
    --revalidar F01,F09   re-valida TODAS las respuestas en caché de esos documentos contra su txt actual (el txt se
                 rehízo: columnas, OCR), sin llamadas
"""
from __future__ import annotations

import copy
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
TOPIC = "ba6c3cac-f7r3"
STEPS = ROOT / "data" / "scripts" / "_steps" / TOPIC
SRC = STEPS / "fuentes"
OLD = ROOT / "data" / "scripts" / "_steps" / "ba6c3cac-f6v3" / "01_facts_sources.json"
LAB = Path(__file__).resolve().parent
EVENT_YEAR = 2005
sys.path.insert(0, str(LAB))
from f7a_fuentes_orleans import PLACE_RE, SEED  # noqa: E402


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")                # -I ignora PYTHONIOENCODING
    from cost_tracker import cost_tracker
    from researcher_steps import research_v3 as r3
    args = sys.argv[1:]
    solo = args[args.index("--solo") + 1] if "--solo" in args else None
    sin_llm = "--sin-llm" in args
    reval = args[args.index("--revalidar") + 1].split(",") if "--revalidar" in args else []
    man = json.loads((SRC / "manifest.json").read_text(encoding="utf-8"))
    docs = [d for d in man["documentos"] if d.get("ok")]
    log: list[str] = []
    per_doc, texts, costos = {}, {}, {}
    for d in docs:
        texts[d["id"]] = r3.DocText(d["id"], (SRC / d["txt"]).read_text(encoding="utf-8"))
        if solo and d["id"] != solo:
            continue
        why = r3.doc_contamination(d, EVENT_YEAR)
        if why:
            log.append(f"  [R3] {d['id']}: no se extrae ({why})")
            continue

        def _no_call(*a, **k):                             # --sin-llm: lo que no está en caché queda afuera
            raise RuntimeError("sin LLM")
        t0 = time.time()
        cost_tracker.start_video(TOPIC)
        try:
            part = r3.extract_document(SEED, d, texts[d["id"]].text, cache_dir=STEPS / "_r3_cache", log=log,
                                       place_re=PLACE_RE, call=_no_call if sin_llm else None,
                                       revalidate=d["id"] in reval)
        finally:
            rep = cost_tracker.end_video()
        costos[d["id"]] = {"usd": round(getattr(rep, "total_cost", 0.0) or 0.0, 4), "segundos": round(time.time() - t0, 1)}
        per_doc[d["id"]] = part
        (STEPS / f"pool_doc_{d['id']}.json").write_text(json.dumps(part, ensure_ascii=False, indent=1), encoding="utf-8")
        print(log[-1], costos[d["id"]], flush=True)
    if solo:
        print("\n".join(log))
        return
    from config import DATA_DIR
    pool = r3.build_pool(per_doc, docs, texts, event_year=EVENT_YEAR, geocode_cache=DATA_DIR / "geocode_cache.json",
                         log=log)
    prev_cost = json.loads((STEPS / "_r3_costos.json").read_text(encoding="utf-8")) if (STEPS / "_r3_costos.json").exists() else {}
    for k, v in costos.items():     # `ultimo` = la última extracción pagada (corrida limpia); `acumulado` = todo lo gastado
        c = prev_cost.setdefault(k, {"ultimo": 0.0, "acumulado": 0.0, "segundos": 0.0})
        if v["usd"] > 0:
            c.update({"ultimo": v["usd"], "acumulado": round(c["acumulado"] + v["usd"], 4), "segundos": v["segundos"]})
    (STEPS / "_r3_costos.json").write_text(json.dumps(prev_cost, ensure_ascii=False, indent=1), encoding="utf-8")
    pool["_research_v3"]["costo_r3"] = prev_cost
    out = json.dumps(pool, ensure_ascii=False, indent=1)
    (STEPS / "00_pool_v3.json").write_text(out, encoding="utf-8")
    (LAB / "00_pool_v3.json").write_text(out, encoding="utf-8")
    (LAB / "f7b_run.log").write_text("\n".join(log) + "\n", encoding="utf-8")
    print("\n".join(log))
    old = json.loads(OLD.read_text(encoding="utf-8"))["evidence_pool"]
    old_c = copy.deepcopy(old)
    old_c.setdefault("datos", []), old_c.setdefault("cronologia", []), old_c.setdefault("citas", [])
    r3.person_stats(old_c)
    m_new, m_old = r3.metrics(pool), r3.metrics(old_c)
    print(json.dumps({"nuevo": m_new, "f6v3": m_old}, ensure_ascii=False, indent=1))
    json.dumps(m_new)
    (LAB / "f7b_metricas.json").write_text(json.dumps({"nuevo": m_new, "f6v3": m_old, "costo_r3": prev_cost},
                                                      ensure_ascii=False, indent=1), encoding="utf-8")
    write_topic(pool)


def write_topic(pool: dict) -> None:
    """Topic nuevo `ba6c3cac-f7r3` (handoff §3): copia del research de f6v3 con el pool nuevo. Los pasos de f6v3 y la
    entrada de f5v2 en topics_db no se tocan; topics_db recibe una entrada NUEVA (copia de f5v2, la única de Orleans
    con evidence_pool en la base) con este pool y `research_version: 3`. Respaldo de topics_db antes de escribir."""
    from config import DATA_DIR
    src = json.loads(OLD.read_text(encoding="utf-8"))
    src["evidence_pool"] = pool
    src["_f7b"] = {"desde": "ba6c3cac-f6v3/01_facts_sources.json", "evidence_pool": "research v3 (00_pool_v3.json)"}
    (STEPS / "01_facts_sources.json").write_text(json.dumps(src, ensure_ascii=False, indent=1), encoding="utf-8")
    db_path = DATA_DIR / "topics_db.json"
    db = json.loads(db_path.read_text(encoding="utf-8"))
    base = next(t for t in db["topics"] if t.get("id") == "ba6c3cac-f5v2")
    new = {**copy.deepcopy(base), "id": TOPIC, "evidence_pool": pool, "research_version": 3,
           "f7_nota": "F7b: copia de ba6c3cac-f5v2 con el pool de research v3 (lab, no se publica)"}
    for k in ("assets_rendered_at", "video_generated_at", "video_path", "f5_nota"):
        new.pop(k, None)
    bak = LAB / "topics_db_pre_f7b.json"
    if not bak.exists():
        bak.write_text(db_path.read_text(encoding="utf-8"), encoding="utf-8")
    db["topics"] = [t for t in db["topics"] if t.get("id") != TOPIC] + [new]
    db_path.write_text(json.dumps(db, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"topic {TOPIC}: {STEPS / '01_facts_sources.json'} + entrada en topics_db (respaldo {bak.name})")


if __name__ == "__main__":
    main()
