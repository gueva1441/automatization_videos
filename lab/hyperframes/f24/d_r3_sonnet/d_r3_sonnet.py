"""F24 §D (pedido de Omar, después de C) — R3 con claude-sonnet-5-5 sobre los mismos documentos de Kyshtym de F23.

Sin buscar ni bajar nada: los 8 documentos del pool de F23 (`_research_v3.documentos`, txt en `_steps/…/fuentes/`), el
mismo seed y perfil, el mismo prompt (`build_extraction_prompt`), el mismo `R3_SYSTEM` y el mismo `R3_SCHEMA`. Solo cambia
`call` (Sonnet 5.5, effort high, max_tokens 32 000). Caché propia en esta carpeta (no toca `_r3_cache`). Después,
`build_pool` igual que `run_seed` (R4 + R5, deterministas) → `00_pool_v3_sonnet.json`, y la comparación pool contra pool
con el de F23. Código de producción: ninguno tocado. Tope US$ 5.00 (freno por llamada, una facturación por llamada).
Uso: python -I lab/hyperframes/f24/d_r3_sonnet/d_r3_sonnet.py
"""
from __future__ import annotations

import json
import sys
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
D = ROOT / "data" / "scripts" / "_steps" / "f18-kyshtym-mayak"
MODELO = "claude-sonnet-5-5"
TOPE = 5.00
MAX_OUT = 32000


class Parada(RuntimeError):
    pass


def _j(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def call_sonnet(gastado: list[float]):
    import claude_helpers as hx
    from cost_tracker import cost_tracker
    hx.TIMEOUT_S = 2400
    pin, pout = hx.PRICES[MODELO]

    def _call(prompt, system_instruction=None, response_schema=None, thinking_budget=None, description=None):
        cur = cost_tracker.current_video.total_cost if cost_tracker.current_video else 0.0
        worst = (len(prompt) + len(system_instruction or "")) / 2.5 / 1e6 * pin + MAX_OUT / 1e6 * pout
        if cur + worst > TOPE:
            raise Parada(f"tope antes de «{description}»: US$ {cur:.3f} + peor caso {worst:.3f} > {TOPE:.2f}")
        n = {"posts": 0}

        def post(body: dict) -> dict:
            if n["posts"]:
                raise Parada("la llamada ya facturó una vez: sin reintento")
            body["max_tokens"] = MAX_OUT
            n["posts"] += 1
            return hx._post(body)
        return hx.make_call(MODELO, "high", post=post)(prompt, system_instruction=system_instruction,
                                                       response_schema=response_schema, description=description)
    return _call


def resumen(pool: dict) -> dict:
    from script_engine import nombres
    pers = pool.get("personajes") or []
    est = Counter((q.get("verificacion") or {}).get("estado") for q in pool.get("citas") or [])
    desc = Counter(str(x.get("motivo") or "")[:45] for x in pool.get("_descartados") or [])
    return {"items": {k: len(pool.get(k) or []) for k in ("datos", "cronologia", "lugares", "citas", "personajes")},
            "personajes_es_persona": sum(1 for p in pers if nombres.es_persona(p.get("nombre") or "")),
            "personajes_nombres": sorted(p.get("nombre") for p in pers),
            "elegibles_humano": sum(1 for p in pers if p.get("elegible_humano")),
            "citas_estado": dict(est), "descartados": sum(desc.values()), "descartados_por_motivo": dict(desc.most_common())}


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    from config import DATA_DIR
    from cost_tracker import cost_tracker
    from researcher_steps import research_v3 as r3
    pool23 = _j(D / "00_pool_v3.json")
    if not pool23.get("_tiempo"):
        raise SystemExit("el 00_pool_v3.json de Kyshtym no es el de F23")
    prof = _j(D / "_perfil.json")
    seed = _j(ROOT / "lab" / "hyperframes" / "f18" / "seed_f18.json")
    s2 = {**seed, "lugar_idioma": seed.get("idioma_local") or prof.get("idioma_local") or None,
          "nombres_lugar": prof.get("nombres_lugar") or [], "idiomas_research": prof.get("idiomas_research") or [],
          **{k: prof.get(k) or [] for k in ("roles_testigo", "roles_antagonista")}}
    r3.set_vocabulario(prof)
    r3.set_idiomas(prof.get("idiomas_research"))
    man = {d["id"]: d for d in _j(ROOT / "lab" / "hyperframes" / "f23" / "manifest_f23.json")["documentos"]}
    ids = [d["id"] for d in pool23["_research_v3"]["documentos"]]
    docs = [man[i] for i in ids]
    tiempo = r3.tiempo_del_perfil(prof)
    texts, per_doc, log, t_doc = {}, {}, [], {}
    cost_tracker.start_video("f18-kyshtym-mayak-f24-d-r3-sonnet")
    t0 = time.time()
    err = None
    try:
        call = call_sonnet([])
        for d in docs:
            texts[d["id"]] = r3.DocText(d["id"], (D / "fuentes" / d["txt"]).read_text(encoding="utf-8"))
            if r3.doc_contamination(d, tiempo["anio_inicio"]):
                continue
            t1 = time.time()
            per_doc[d["id"]] = r3.extract_document(s2, d, texts[d["id"]].text, call=call, cache_dir=OUT / "_r3_cache",
                                                   log=log, place_re=prof["place_re"])
            per_doc[d["id"]].pop("_extraccion_fallida", None)
            t_doc[d["id"]] = round(time.time() - t1, 1)
            print(f"  [R3 sonnet] {d['id']}: {t_doc[d['id']]} s · US$ {cost_tracker.current_video.total_cost:.4f}",
                  flush=True)
    except Parada as e:
        err = str(e)
    finally:
        t_r3 = round(time.time() - t0, 1)
        rep = cost_tracker.end_video()
    llamadas = [{"desc": e.description, "in": e.tokens_in, "out": e.tokens_out, "usd": round(e.total_cost, 4)}
                for e in rep.entries]
    res = {"modelo": MODELO, "esfuerzo": "high", "max_tokens": MAX_OUT, "docs": ids, "error": err,
           "usd_r3": round(rep.total_cost, 4), "segundos_r3": t_r3, "segundos_por_doc": t_doc, "llamadas": llamadas}
    if not err:
        pool = r3.build_pool(per_doc, docs, texts, event_year=tiempo["anio_inicio"], anio_fin=tiempo["anio_fin"],
                             geocode_cache=DATA_DIR / "geocode_cache.json", log=log,
                             subject_re=r3.subject_re_del_perfil(prof))
        pool["_tiempo"] = tiempo
        (OUT / "00_pool_v3_sonnet.json").write_text(json.dumps(pool, ensure_ascii=False, indent=1), encoding="utf-8")
        from researcher_steps import pool_gate as pg
        res["sonnet"] = {**resumen(pool), "compuerta": {k: pg.evaluate(pool).get(k) for k in ("color", "metricas")}}
    res["gemini_f23"] = {**resumen(pool23), "compuerta": pool23.get("_pool_gate")}
    c23 = _j(ROOT / "lab" / "hyperframes" / "f23" / "costos_f23.json")
    r = next(x for x in c23["etapas"] if x["etapa"] == "research")
    res["gemini_f23"]["usd_r3"] = round(sum(x["usd"] for x in r["llamadas"] if str(x["desc"]).startswith("R3 ")), 4)
    res["gemini_f23"]["llamadas_r3"] = sum(1 for x in r["llamadas"] if str(x["desc"]).startswith("R3 "))
    (OUT / "comparacion.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    (OUT / "log.txt").write_text("\n".join(log), encoding="utf-8")
    r3.set_vocabulario(None)
    r3.set_idiomas(None)
    print(json.dumps({k: res.get(k) for k in ("error", "usd_r3", "segundos_r3")}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
