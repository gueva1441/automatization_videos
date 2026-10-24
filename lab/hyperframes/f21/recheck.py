"""F21 §2 — re-chequeo SIN API de lo que ya está en disco, para comparar el código de antes (08d63d9) con F21.

Por tema (Orleans `ba6c3cac-f7r3`, Ycuá `f8s1-ycua-bolanos`, Kyshtym `f18-kyshtym-mayak`):
  1. pool: perfil → `set_vocabulario`; sobre una copia del pool, los pasos deterministas de R4/R5 que dependen de
     nombres (`add_quote_authors`, `canonical_names`, `presence_v3`, `person_stats`, `verify_pool` con los txt ya
     bajados, `person_stats` otra vez) y las cifras canónicas (`canonical_v3`, `population_canon`) → compuerta.
  2. ficha: `ficha_caso.check` sobre la ficha guardada (lo que hoy sacaría).
  3. columna: `m01a_columna.chequeo`.
  4. escaleta: `m01a_escaleta.bloqueantes` (la guardada; en Kyshtym, el crudo del pase 2 de F18 con `ids_v2`).
  5. guion: `guion_v4.bloqueantes(…, ficha=…)` y `guion_v4.metricas` sobre la última narración (F16).
Kyshtym: el pool es el de F20; ficha, columna y escaleta son las de F18 y se chequean contra el pool de F18 (sus ids
son de ese pool). Kyshtym no tiene guion (F18 paró en la escaleta y F19 en el research).
Uso: python -I lab/hyperframes/f21/recheck.py <etiqueta>   → lab/hyperframes/f21/recheck_<etiqueta>.json
"""
from __future__ import annotations

import copy
import json
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LAB = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
STEPS = ROOT / "data" / "scripts" / "_steps"
F16, F18 = LAB.parent / "f16", LAB.parent / "f18"
TEMAS = {
    "orleans": {"tid": "ba6c3cac-f7r3", "anio": 2005, "perfil": "_perfil_f20.json", "pool": "00_pool_v3.json",
                "ficha": "ficha_caso.json", "columna": None, "escaleta": "01a_escaleta_f16.json",
                "guion": F16 / "guion_orleans_f16.json"},
    "ycua": {"tid": "f8s1-ycua-bolanos", "anio": 2004, "perfil": "_perfil_f20.json", "pool": "00_pool_v3.json",
             "ficha": "ficha_caso.json", "columna": "01a_columna.json", "escaleta": "01a_escaleta_f16.json",
             "guion": F16 / "guion_ycua_f16.json"},
    "kyshtym": {"tid": "f18-kyshtym-mayak", "anio": 1957, "perfil": "_perfil.json", "pool": "00_pool_v3.json",
                "pool_f18": "00_pool_v3_f18.json", "ficha": "_f18/ficha_caso.json", "columna": "_f18/01a_columna.json",
                "escaleta_crudo": F18 / "escaleta_crudos_pase2.json", "guion": None},
}


def _j(p: Path):
    return json.loads(p.read_text(encoding="utf-8")) if p and p.exists() else None


def _texts(d: Path, pool: dict) -> tuple[dict, list[dict]]:
    from researcher_steps import research_v3 as r3
    docs = (pool.get("_research_v3") or {}).get("documentos") or []
    texts = {}
    for x in docs:
        f = d / "fuentes" / str(x.get("txt") or "")
        if x.get("txt") and f.exists():
            texts[x["id"]] = r3.DocText(x["id"], f.read_text(encoding="utf-8"))
    return texts, docs


def paso_pool(tema: str, cfg: dict) -> dict:
    from researcher_steps import pool_gate as pg
    from researcher_steps import research_v3 as r3
    d = STEPS / cfg["tid"]
    perfil = _j(d / cfg["perfil"]) or {}
    pool = copy.deepcopy(_j(d / cfg["pool"]))
    r3.set_vocabulario(perfil)
    texts, docs = _texts(d, pool)
    year = perfil.get("anio_evento") or cfg["anio"]
    log: list[str] = []
    r3.add_quote_authors(pool, log)
    r3.canonical_names(pool, texts)
    r3.presence_v3(pool, texts, log)
    r3.person_stats(pool, year)
    r3.canonical_v3(pool, docs, log)
    sre = r3.subject_re_del_perfil(perfil) if hasattr(r3, "subject_re_del_perfil") else r3.SUBJECT_RE_DEFAULT
    pop = r3.population_canon(pool, docs, sre, log)
    if pop:
        pool["cifras_canonicas"] = [pop] + [g for g in pool["cifras_canonicas"]
                                            if g["oficial"] not in {v["id"] for v in pop["variantes"]} | {pop["oficial"]}]
    ver = r3.verify_pool(pool, texts, docs, log)
    r3.person_stats(pool, year)
    gate = pg.evaluate(pool)
    r3.set_vocabulario(None)
    citas = pool.get("citas") or []
    return {"color": gate["color"], "metricas": gate["metricas"], "motivos": gate["motivos"],
            "personajes": [{k: p.get(k) for k in ("nombre", "rol", "testigo", "antagonista", "n_citas", "n_datos",
                                                 "presente_en_evento", "elegible_humano")}
                           for p in pool.get("personajes") or []],
            "elegibles": [p["nombre"] for p in pool.get("personajes") or [] if p.get("elegible_humano")],
            "citas_verificadas": sum(1 for q in citas if (q.get("verificacion") or {}).get("estado") == "verificada"),
            "verificacion": ver, "textos": len(texts),
            "canonicas": [{"valor": c.get("valor"), "variantes": [v.get("valor") for v in c.get("variantes") or []]}
                          for c in pool.get("cifras_canonicas") or []],
            "log": [x for x in log if "población" in x or "autores de cita" in x]}


def paso_ficha(cfg: dict) -> dict | None:
    from researcher_steps import ficha_caso as fc
    d = STEPS / cfg["tid"]
    ficha = _j(d / cfg["ficha"])
    if not ficha:
        return None
    pool = _j(d / (cfg.get("pool_f18") or cfg["pool"]))
    raw = {k: ficha.get(k) for k in fc.SECCIONES if k in ficha} | {"historia": ficha.get("historia"),
                                                                     "escenas": ficha.get("escenas")}
    _, sacados = fc.check(raw, pool)
    return {"problemas": len(sacados), "sacados": [f"[{s['seccion']}] {str(s['que'])[:70]} → {str(s['motivo'])[:110]}"
                                                   for s in sacados]}


def paso_columna(cfg: dict) -> dict | None:
    from script_engine import m01a_columna as mc
    d = STEPS / cfg["tid"]
    col = _j(d / cfg["columna"]) if cfg.get("columna") else None
    if not col:
        return None
    pool = _j(d / (cfg.get("pool_f18") or cfg["pool"]))
    ficha = _j(d / cfg["ficha"])
    prob = mc.chequeo(col, pool, ficha)
    return {"problemas": prob, "personas": mc.personas_con_nombre(col, ficha)}


def paso_escaleta(cfg: dict) -> dict | None:
    from script_engine import m01a_escaleta as ma
    d = STEPS / cfg["tid"]
    pool = _j(d / (cfg.get("pool_f18") or cfg["pool"]))
    ficha = _j(d / cfg["ficha"])
    if cfg.get("escaleta"):
        esc = _j(d / cfg["escaleta"])
        raw = {k: v for k, v in esc.items() if not k.startswith("_")}
    elif cfg.get("escaleta_crudo"):
        raw, _ = ma.ids_v2((_j(cfg["escaleta_crudo"]) or [None])[0])
    else:
        return None
    _, bloq, rep, otros = ma.bloqueantes(raw, pool, ficha)
    return {"bloqueantes": bloq, "no_bloqueantes": len(otros)}


def paso_guion(cfg: dict) -> dict | None:
    import fase1_5 as f15
    from script_engine import guion_v4 as g4
    if not cfg.get("guion"):
        return None
    d = STEPS / cfg["tid"]
    g = _j(cfg["guion"])
    esc = _j(d / cfg["escaleta"])
    ficha = _j(d / cfg["ficha"])
    topic = dict(f15._load_topic_by_id(cfg["tid"]))
    topic["guion_version"] = 4
    bl = g4.bloqueantes(topic, esc, g["parrafos"], ficha=ficha)
    m = g4.metricas(topic, esc, g["parrafos"])
    keep = {k: m[k] for k in ("palabras", "citas", "humano_caps", "cierre") if k in m}
    keep["duras_v3"] = len(m.get("duras_v3") or [])
    keep["duras_v3_lista"] = [str(x)[:120] for x in m.get("duras_v3") or []]
    return {"bloqueantes": [{k: b.get(k) for k in ("codigo", "cap", "beat", "motivo")} for b in bl], "metricas": keep}


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")                # -I ignora PYTHONIOENCODING
    etiqueta = sys.argv[1] if len(sys.argv) > 1 else "x"
    out: dict = {}
    for tema, cfg in TEMAS.items():
        r: dict = {}
        for nombre, fn in (("pool", lambda: paso_pool(tema, cfg)), ("ficha", lambda: paso_ficha(cfg)),
                           ("columna", lambda: paso_columna(cfg)), ("escaleta", lambda: paso_escaleta(cfg)),
                           ("guion", lambda: paso_guion(cfg))):
            try:
                r[nombre] = fn()
            except Exception as e:  # noqa: BLE001 — se anota y se sigue
                r[nombre] = {"error": f"{type(e).__name__}: {e}", "traceback": traceback.format_exc()[-1500:]}
        out[tema] = r
        p = r["pool"] or {}
        print(f"[{etiqueta} {tema}] pool {p.get('color')} {p.get('metricas')} · elegibles {len(p.get('elegibles') or [])}"
              f" · ficha {(r['ficha'] or {}).get('problemas')} · columna {(r['columna'] or {}).get('problemas')} · "
              f"escaleta {len((r['escaleta'] or {}).get('bloqueantes') or [])} · guion "
              f"{len((r['guion'] or {}).get('bloqueantes') or []) if r['guion'] else '—'}", flush=True)
    (LAB / f"recheck_{etiqueta}.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
