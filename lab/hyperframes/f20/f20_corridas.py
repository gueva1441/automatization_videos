"""F20 (parte 1) — el research se adapta al tema: vocabulario del perfil, descargas por idioma, humano elegible.

    recalculo  Orleans (`ba6c3cac-f7r3`) e Ycuá (`f8s1-ycua-bolanos`), SIN research: el vocabulario del caso
               (`research_v3.seed_vocabulario`, 1 Flash con el seed y las fuentes de R1 que ya están en `fuentes.json`)
               → `_perfil_f20.json` (el perfil de siempre + los tres campos; `_perfil.json` no se toca) →
               `set_vocabulario` → sobre una copia del pool: `person_stats` + cifras canónicas (`canonical_v3` y
               `population_canon`, como en `build_pool`) → compuerta → `POOL_GATE_f20.md` y `00_pool_v3_f20_recalculo.json`
               al lado de lo de siempre. No se pisa nada.
    research   Kyshtym (`f18-kyshtym-mayak`): respaldo de F19 (`00_pool_v3_f19.json`, `_f19/`: POOL_GATE, perfil,
               manifiesto) → `run_seed` (el perfil de F19 sin vocabulario: lo completa después de R1; caché R1 de F19,
               las mismas fuentes; descargas por idioma; R3 de nuevo porque el prompt cambia) → compuerta. Si no es
               rojo, el pool nuevo entra en el topic de topics_db (respaldo `topics_db.pre_f20.json`).
Tope del research: US$ 3.50 (`costos_f20.json`). Freno antes de cada llamada Gemini que pasa por `gemini_helpers`
(call_pro_json, call_flash_json) o por `research_v3.search_pro/search_flash`: lo gastado + un margen por llamada no
puede pasar el tope. Las llamadas de `verify_quotes` (grounding directo) no pasan por el freno: se miden al final.
    vocab_kyshtym  ver `etapa_vocab_kyshtym` (el vocabulario de Kyshtym con las formas pegadas, regenerado).
Uso: python -I lab/hyperframes/f20/f20_corridas.py [recalculo research vocab_kyshtym]
"""
from __future__ import annotations

import copy
import json
import shutil
import sys
import time
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LAB = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
COSTOS = LAB / "costos_f20.json"
TOPE_RESEARCH = 3.50
MARGEN_LLAMADA = 0.12                   # peor caso de una llamada Pro de R3 (trozo grande + razonamiento)
KYSHTYM = "f18-kyshtym-mayak"
RECALCULO = {
    "orleans": {"tid": "ba6c3cac-f7r3", "anio": 2005, "idiomas": "inglés (Nueva Orleans, EE. UU.)",
                "seed_title": "La Prisión Parroquial de Orleans durante el huracán Katrina: los presos abandonados en "
                              "sus celdas (Nueva Orleans, 29 de agosto de 2005)"},
    "ycua": {"tid": "f8s1-ycua-bolanos", "anio": 2004, "idiomas": "español (Asunción, Paraguay); también guaraní",
             "seed_title": "El incendio del supermercado Ycuá Bolaños: las puertas que cerraron con la gente adentro "
                           "(Asunción, 1 de agosto de 2004)"},
}


class Parada(RuntimeError):
    pass


def _write(p: Path, obj) -> None:
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding="utf-8")


def _costos() -> dict:
    return json.loads(COSTOS.read_text(encoding="utf-8")) if COSTOS.exists() else {"etapas": [], "usd_total": 0.0}


def _add_cost(etapa: str, rep, t0: float, extra: dict | None = None) -> dict:
    c = _costos()
    costo = {"etapa": etapa, "usd": round(getattr(rep, "total_cost", 0.0) or 0.0, 4),
             "segundos": round(time.time() - t0, 1), "llamadas": len(getattr(rep, "entries", None) or []),
             **(extra or {})}
    c["etapas"].append(costo)
    c["usd_total"] = round(sum(x["usd"] for x in c["etapas"]), 4)
    _write(COSTOS, c)
    print(f"  [{etapa}] US$ {costo['usd']:.4f} · {costo['segundos']:.0f} s · tanda US$ {c['usd_total']:.4f}", flush=True)
    return costo


def _steps(tid: str) -> Path:
    from script_engine.m01a_skeleton import STEPS_DIR
    return STEPS_DIR / tid


def resumen_pool(pool: dict) -> dict:
    """Lo que compara el reporte: elegibles (nombres), conteos canónicos, color."""
    from researcher_steps import pool_gate as pg
    g = pg.evaluate(pool)
    return {"color": g["color"], "metricas": g["metricas"], "motivos": g["motivos"],
            "elegibles": [p["nombre"] for p in pool.get("personajes") or [] if p.get("elegible_humano")],
            "canonicas": [{"tipo": c.get("tipo"), "valor": c.get("valor"), "oficial": c.get("oficial"),
                           "variantes": [v.get("valor") for v in c.get("variantes") or []]}
                          for c in pool.get("cifras_canonicas") or []]}


# ═══════════════════════════════════════════════════════════════

def etapa_recalculo() -> None:
    from cost_tracker import cost_tracker
    from researcher_steps import pool_gate as pg
    from researcher_steps import research_v3 as r3
    out: dict = json.loads((LAB / "recalculo_f20.json").read_text(encoding="utf-8")) \
        if (LAB / "recalculo_f20.json").exists() else {}
    for tema, cfg in RECALCULO.items():
        if tema in out:
            print(f"[recalculo {tema}] ya existe: se saltea", flush=True)
            continue
        d = _steps(cfg["tid"])
        pool0 = json.loads((d / "00_pool_v3.json").read_text(encoding="utf-8"))
        antes = resumen_pool(pool0)
        prof0 = json.loads((d / "_perfil.json").read_text(encoding="utf-8")) if (d / "_perfil.json").exists() else {}
        fuentes = (json.loads((d / "fuentes.json").read_text(encoding="utf-8")) if (d / "fuentes.json").exists()
                   else {}).get("fuentes") or []
        seed = {"seed_title": cfg["seed_title"]}
        if (d / "_perfil_f20.json").exists():                # ya generado: se reusa (sin otra llamada)
            perfil = json.loads((d / "_perfil_f20.json").read_text(encoding="utf-8"))
        else:
            t0 = time.time()
            cost_tracker.start_video(f"{cfg['tid']}-f20-perfil")
            try:
                voc = r3.seed_vocabulario(seed, fuentes, idiomas=cfg["idiomas"])
            finally:
                rep = cost_tracker.end_video()
            _add_cost(f"perfil {tema}", rep, t0)
            perfil = {**prof0, **voc, "_f20": "vocabulario del caso, sin research (F20 §2.1)"}
        _write(d / "_perfil_f20.json", perfil)
        r3.set_vocabulario(perfil)
        pool = copy.deepcopy(pool0)
        docs = (pool.get("_research_v3") or {}).get("documentos") or []
        year = perfil.get("anio_evento") or cfg["anio"]
        r3.person_stats(pool, year)
        log: list[str] = []
        r3.canonical_v3(pool, docs, log)
        pop = r3.population_canon(pool, docs, r3.SUBJECT_RE_DEFAULT, log)
        if pop:
            pool["cifras_canonicas"] = [pop] + [g for g in pool["cifras_canonicas"] if g["oficial"] not in
                                                {v["id"] for v in pop["variantes"]} | {pop["oficial"]}]
        gate = pg.evaluate(pool)
        (d / "POOL_GATE_f20.md").write_text(pg.report(gate, cfg["tid"]), encoding="utf-8")
        shutil.copy2(d / "POOL_GATE_f20.md", LAB / f"POOL_GATE_{tema}_f20.md")
        _write(d / "00_pool_v3_f20_recalculo.json", pool)
        despues = resumen_pool(pool)
        out[tema] = {"tid": cfg["tid"], "perfil": perfil, "antes": antes, "despues": despues, "log": log,
                     "personajes": [{k: p.get(k) for k in ("nombre", "rol", "testigo", "antagonista", "n_citas", "n_datos",
                                                          "presente_en_evento", "elegible_humano")}
                                    for p in pool["personajes"]]}
        _write(LAB / "recalculo_f20.json", out)
        _write(LAB / f"perfil_{tema}_f20.json", perfil)
        print(f"[recalculo {tema}] {antes['color']} → {despues['color']} · elegibles {len(antes['elegibles'])} → "
              f"{len(despues['elegibles'])} · canónicas {[c['valor'] for c in antes['canonicas']]} → "
              f"{[c['valor'] for c in despues['canonicas']]}", flush=True)
    r3.set_vocabulario(None)


def _frenos(spent0: float):
    """Envuelve las llamadas Gemini del research con el freno de costo. Devuelve una función que deshace."""
    import gemini_helpers
    from cost_tracker import cost_tracker
    from researcher_steps import research_v3 as r3
    orig = {(gemini_helpers, "call_pro_json"): gemini_helpers.call_pro_json,
            (gemini_helpers, "call_flash_json"): gemini_helpers.call_flash_json,
            (r3, "search_pro"): r3.search_pro, (r3, "search_flash"): r3.search_flash}

    def wrap(fn, name):
        def _f(*a, **k):
            cur = cost_tracker.current_video.total_cost if cost_tracker.current_video else 0.0
            if spent0 + cur + MARGEN_LLAMADA > TOPE_RESEARCH:
                raise Parada(f"tope del research: US$ {spent0 + cur:.3f} + margen {MARGEN_LLAMADA} > {TOPE_RESEARCH} "
                             f"antes de {name}")
            return fn(*a, **k)
        return _f
    for (mod, name), fn in orig.items():
        setattr(mod, name, wrap(fn, name))

    def undo():
        for (mod, name), fn in orig.items():
            setattr(mod, name, fn)
    return undo


def etapa_research() -> None:
    from config import DATA_DIR
    from cost_tracker import cost_tracker
    from researcher_steps import pool_gate as pg
    from researcher_steps import research_v3 as r3
    d = _steps(KYSHTYM)
    if (d / "00_pool_v3_f19.json").exists() and "roles_testigo" in json.loads(
            (d / "_perfil.json").read_text(encoding="utf-8")):
        print("[research] ya existe (perfil con vocabulario): se saltea", flush=True)
        return
    bak = d / "_f19"
    bak.mkdir(exist_ok=True)
    if not (d / "00_pool_v3_f19.json").exists():
        shutil.copy2(d / "00_pool_v3.json", d / "00_pool_v3_f19.json")
    for src, dst in ((d / "POOL_GATE.md", bak / "POOL_GATE.md"), (d / "_perfil.json", bak / "_perfil.json"),
                     (d / "fuentes" / "manifest.json", bak / "manifest.json"), (d / "fuentes.json", bak / "fuentes.json")):
        if src.exists() and not dst.exists():
            shutil.copy2(src, dst)
    antes = resumen_pool(json.loads((d / "00_pool_v3_f19.json").read_text(encoding="utf-8")))
    seed = json.loads((LAB.parent / "f18" / "seed_f18.json").read_text(encoding="utf-8"))
    db = DATA_DIR / "topics_db.json"
    if not (DATA_DIR / "topics_db.pre_f20.json").exists():
        shutil.copy2(db, DATA_DIR / "topics_db.pre_f20.json")
    log: list[str] = []
    t0 = time.time()
    spent0 = sum(x["usd"] for x in _costos()["etapas"] if x["etapa"].startswith("research"))
    undo = _frenos(spent0)
    cost_tracker.start_video(f"{KYSHTYM}-f20-research")
    err, pool, color = None, None, None
    try:
        pool, _, gate = r3.run_seed(seed, KYSHTYM, d, log=log)
        color = gate["color"] if gate else None
    except pg.PoolGateRed as e:
        color, err = pg.RED, "rojo: " + "; ".join(e.gate["motivos"])
        pool = json.loads((d / "00_pool_v3.json").read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        err = f"{type(e).__name__}: {e}"
        log.append(traceback.format_exc())
    finally:
        rep = cost_tracker.end_video()
        undo()
        r3.set_vocabulario(None)
    (LAB / "run_research_detalle.log").write_text("\n".join(log), encoding="utf-8")
    for src, dst in ((d / "POOL_GATE.md", "POOL_GATE_kyshtym_f20.md"), (d / "fuentes.json", "fuentes.json"),
                     (d / "fuentes" / "manifest.json", "manifest.json"), (d / "_perfil.json", "perfil_kyshtym_f20.json")):
        if src.exists():
            shutil.copy2(src, LAB / dst)
    despues = resumen_pool(pool) if pool else None
    _add_cost("research kyshtym", rep, t0, {"color": color, "error": err})
    res = {"antes_f19": antes, "despues": despues, "error": err,
           "personajes": [{k: p.get(k) for k in ("id", "nombre", "rol", "testigo", "antagonista", "n_citas", "n_datos",
                                                 "presente_en_evento", "elegible_humano", "docs")}
                          for p in (pool or {}).get("personajes") or []]}
    if pool:
        its = {q["id"]: q for q in pool.get("citas") or []}
        res["citas"] = [{k: q.get(k) for k in ("id", "autor", "texto", "idioma", "doc_id", "testimonio")}
                        | {"verificada": (q.get("verificacion") or {}).get("estado") == "verificada"} for q in its.values()]
    _write(LAB / "kyshtym_f20.json", res)
    if pool and color != pg.RED:
        raw = json.loads(db.read_text(encoding="utf-8"))
        t = next(x for x in (raw["topics"] if isinstance(raw, dict) else raw) if x.get("id") == KYSHTYM)
        t["evidence_pool"] = pool
        db.write_text(json.dumps(raw, indent=2, ensure_ascii=False), encoding="utf-8")
    if err and color != pg.RED:
        raise Parada(f"research: {err}")
    print(f"[research] compuerta {antes['color']} → {color} · elegibles {antes['elegibles']} → "
          f"{(despues or {}).get('elegibles')}", flush=True)


def etapa_vocab_kyshtym() -> None:
    """El vocabulario del research de Kyshtym salió con las formas pegadas («testigo witness очевидец»): con el esquema
    nuevo (`{es, otras}`) se regenera (1 Flash, con las mismas fuentes de R1) y, sin rehacer el research, se recalculan
    sobre el pool `person_stats`, las cifras canónicas y la compuerta (como en `etapa_recalculo`). Lo del intento 1
    queda como `_perfil_f20_intento1.json` y `00_pool_v3_f20_intento1.json`. R3 ya corrió con los roles pegados."""
    from config import DATA_DIR
    from cost_tracker import cost_tracker
    from researcher_steps import pool_gate as pg
    from researcher_steps import research_v3 as r3
    d = _steps(KYSHTYM)
    if (d / "_perfil_f20_intento1.json").exists():
        print("[vocab kyshtym] ya existe: se saltea", flush=True)
        return
    prof = json.loads((d / "_perfil.json").read_text(encoding="utf-8"))
    pool0 = json.loads((d / "00_pool_v3.json").read_text(encoding="utf-8"))
    shutil.copy2(d / "_perfil.json", d / "_perfil_f20_intento1.json")
    shutil.copy2(d / "00_pool_v3.json", d / "00_pool_v3_f20_intento1.json")
    shutil.copy2(d / "POOL_GATE.md", d / "POOL_GATE_f20_intento1.md")
    seed = json.loads((LAB.parent / "f18" / "seed_f18.json").read_text(encoding="utf-8"))
    fuentes = json.loads((d / "fuentes.json").read_text(encoding="utf-8")).get("fuentes") or []
    t0 = time.time()
    cost_tracker.start_video(f"{KYSHTYM}-f20-vocab")
    try:
        voc = r3.seed_vocabulario(seed, fuentes, idiomas=seed.get("idioma_local") or "")
    finally:
        rep = cost_tracker.end_video()
    _add_cost("perfil kyshtym (vocabulario, 2.º)", rep, t0)
    prof.update(voc)
    _write(d / "_perfil.json", prof)
    r3.set_vocabulario(prof)
    pool = copy.deepcopy(pool0)
    docs = (pool.get("_research_v3") or {}).get("documentos") or []
    r3.person_stats(pool, prof.get("anio_evento") or 1957)
    log: list[str] = []
    r3.canonical_v3(pool, docs, log)
    pop = r3.population_canon(pool, docs, r3.SUBJECT_RE_DEFAULT, log)
    if pop:
        pool["cifras_canonicas"] = [pop] + [g for g in pool["cifras_canonicas"] if g["oficial"] not in
                                            {v["id"] for v in pop["variantes"]} | {pop["oficial"]}]
    gate = pg.evaluate(pool)
    pool["_pool_gate"] = {k: gate[k] for k in ("color", "metricas", "motivos")}
    r3.set_vocabulario(None)
    _write(d / "00_pool_v3.json", pool)
    pg.write_report(gate, KYSHTYM, d)
    shutil.copy2(d / "POOL_GATE.md", LAB / "POOL_GATE_kyshtym_f20.md")
    shutil.copy2(d / "_perfil.json", LAB / "perfil_kyshtym_f20.json")
    shutil.copy2(d / "_perfil_f20_intento1.json", LAB / "perfil_kyshtym_f20_intento1.json")
    res = json.loads((LAB / "kyshtym_f20.json").read_text(encoding="utf-8"))
    res["intento1"] = {"despues": res.get("despues"), "personajes": res.get("personajes")}
    res["despues"] = resumen_pool(pool)
    res["log_vocab"] = log
    res["personajes"] = [{k: p.get(k) for k in ("id", "nombre", "rol", "testigo", "antagonista", "n_citas", "n_datos",
                                                "presente_en_evento", "elegible_humano", "docs")}
                         for p in pool.get("personajes") or []]
    _write(LAB / "kyshtym_f20.json", res)
    if gate["color"] != pg.RED:
        db = DATA_DIR / "topics_db.json"
        raw = json.loads(db.read_text(encoding="utf-8"))
        t = next(x for x in (raw["topics"] if isinstance(raw, dict) else raw) if x.get("id") == KYSHTYM)
        t["evidence_pool"] = pool
        db.write_text(json.dumps(raw, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[vocab kyshtym] {voc} · compuerta {gate['color']} {gate['metricas']} · canónicas "
          f"{[c.get('valor') for c in pool.get('cifras_canonicas') or []]}", flush=True)


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")                # -I ignora PYTHONIOENCODING
    etapas = {"recalculo": etapa_recalculo, "research": etapa_research, "vocab_kyshtym": etapa_vocab_kyshtym}
    for e in [a for a in sys.argv[1:] if a in etapas] or list(etapas):
        try:
            etapas[e]()
        except Parada as x:
            print(f"PARADA ({e}): {x}", flush=True)
            break
    print(f"tanda US$ {_costos()['usd_total']:.4f}", flush=True)


if __name__ == "__main__":
    main()
