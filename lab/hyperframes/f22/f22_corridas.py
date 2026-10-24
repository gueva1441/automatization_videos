"""F22 §2 — las dos corridas con los prompts nuevos (ficha v2.1, columna v1.1, escaleta v2.1, guion v5.2).

    ycua     ficha v2 de F15b tal cual (no se rehace) → columna → escaleta (con la columna) → guion.     tope US$ 1.00
    kyshtym  pool de F21c (los pasos deterministas de F21c sobre el pool de F20 en disco, sin API: `pool`) → ficha
             nueva → columna → escaleta → guion.                                                       tope US$ 2.00
Tope total US$ 3.00 (costos_f22.json). Cada llamada de Sol pasa por un freno ANTES de facturar: lo gastado (en el paso,
en el tema y en la tanda) + el peor caso con `max_completion_tokens` acotado no puede pasar ningún tope; factura una
sola vez (sin reintento). El perfil del seed se carga (`fase1_5.cargar_perfil`) antes de columna, escaleta y guion.
Respaldos de lo que se pisa: Ycuá `01a_columna`, `01a_escaleta`, `01b_*` → `*_f17.json`; Kyshtym `00_pool_v3.json` →
`00_pool_v3_f20.json` y la ficha de F18 → `ficha_caso_f18.json`. `topics_db` no se toca: el topic se arma en memoria con
el pool de `_steps` (en Kyshtym, el de F21c).
Si la columna o la escaleta paran después de su regeneración, o el guion trae bloqueantes: PARADA de ese tema con el
crudo guardado (no se parchea). Cada etapa se saltea si su salida ya existe.
Uso: python -I lab/hyperframes/f22/f22_corridas.py [ycua kyshtym] [pool ficha columna escaleta guion]
"""
from __future__ import annotations

import copy
import hashlib
import json
import shutil
import sys
import time
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LAB = Path(__file__).resolve().parent
sys.path.insert(0, str(LAB))
sys.path.insert(1, str(ROOT))
sys.path.insert(2, str(LAB.parent / "f13"))

TEMAS = {"ycua": {"tid": "f8s1-ycua-bolanos", "pool_md5": "5f3c6d0bc31ebf868dd432b2c79fdcec", "tope": 1.00},
         "kyshtym": {"tid": "f18-kyshtym-mayak", "pool_md5": None, "tope": 2.00}}
TOPE_TOTAL = 3.00
# Pase 1 de Ycuá: escaleta 0.45 con 30 000 tokens de salida → el freno cortó la regeneración (peor caso 0.34 por
# llamada). Desde el pase 2: salida como F18 (escaleta 20 000, guion 24 000) y el paso de escaleta de Ycuá en 0.65 (lo
# gastado en el pase 1 cuenta).
TOPES = {("ycua", "columna"): 0.20, ("ycua", "escaleta"): 0.65, ("ycua", "guion"): 0.32,
         ("kyshtym", "ficha"): 0.80, ("kyshtym", "columna"): 0.20, ("kyshtym", "escaleta"): 0.55,
         ("kyshtym", "guion"): 0.32}
MAX_OUT = {"ficha": 60000, "columna": 16000, "escaleta": 20000, "guion": 24000}
COSTOS = LAB / "costos_f22.json"


class Parada(RuntimeError):
    pass


def _md5(s: str) -> str:
    return hashlib.md5(s.encode("utf-8")).hexdigest()


def _write(p: Path, obj) -> None:
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding="utf-8")


def _costos() -> dict:
    return json.loads(COSTOS.read_text(encoding="utf-8")) if COSTOS.exists() else {"etapas": [], "usd_total": 0.0}


def _gastado(tema: str | None = None, etapa: str | None = None) -> float:
    return sum(x["usd"] for x in _costos()["etapas"]
               if (tema is None or x["tema"] == tema) and (etapa is None or x["etapa"] == etapa))


def _add_cost(tema: str, etapa: str, rep, t0: float, extra: dict | None = None) -> dict:
    c = _costos()
    costo = {"tema": tema, "etapa": etapa, "usd": round(getattr(rep, "total_cost", 0.0) or 0.0, 4),
             "segundos": round(time.time() - t0, 1),
             "llamadas": [{"servicio": e.service, "desc": e.description, "in": e.tokens_in, "out": e.tokens_out,
                           "thinking": e.tokens_thinking, "usd": round(e.total_cost, 4)}
                          for e in (getattr(rep, "entries", None) or [])], **(extra or {})}
    c["etapas"].append(costo)
    c["usd_total"] = round(sum(x["usd"] for x in c["etapas"]), 4)
    _write(COSTOS, c)
    print(f"  [{tema} {etapa}] US$ {costo['usd']:.4f} · {costo['segundos']:.0f} s · tema US$ {_gastado(tema):.4f} · "
          f"tanda US$ {c['usd_total']:.4f}", flush=True)
    return costo


def _freno(tema: str, etapa: str, cur: float, worst: float, desc: str) -> None:
    paso, t, total = _gastado(tema, etapa) + cur, _gastado(tema) + cur, _gastado() + cur
    for nombre, ya, tope in (("paso", paso, TOPES[(tema, etapa)]), ("tema", t, TEMAS[tema]["tope"]),
                             ("total", total, TOPE_TOTAL)):
        if ya + worst > tope:
            raise Parada(f"tope de costo ({nombre}) antes de «{desc}»: US$ {ya:.3f} + peor caso {worst:.3f} > "
                         f"{tope:.2f}")


def sol_call(tema: str, etapa: str, max_out: int):
    """Sol high; cada invocación: freno (paso, tema, total) y UNA llamada que facture con `max_completion_tokens`."""
    import gpt_helpers
    from cost_tracker import cost_tracker
    pin, pout = gpt_helpers.PRICES["gpt-6.1-sol"]

    def _call(prompt, system_instruction=None, response_schema=None, thinking_budget=None, description=None):
        cur = cost_tracker.current_video.total_cost if cost_tracker.current_video else 0.0
        worst = (len(prompt) + len(system_instruction or "")) / 3 / 1e6 * pin + max_out / 1e6 * pout
        _freno(tema, etapa, cur, worst, str(description))
        n = {"posts": 0}

        def post(body: dict) -> dict:
            if n["posts"]:
                raise Parada("la llamada ya facturó una vez (JSON roto o cortado): no hay reintento por el tope")
            body["max_completion_tokens"] = max_out
            n["posts"] += 1
            return gpt_helpers._post(body)
        return gpt_helpers.make_call("gpt-6.1-sol", "high", post=post)(
            prompt, system_instruction=system_instruction, response_schema=response_schema, description=description)
    return _call


def _steps(tema: str) -> Path:
    from script_engine.m01a_skeleton import STEPS_DIR
    return STEPS_DIR / TEMAS[tema]["tid"]


def _backup(src: Path, dst: Path) -> None:
    if src.exists() and not dst.exists():
        shutil.copy2(src, dst)
        print(f"  respaldo {src.name} → {dst.name}", flush=True)


def _pool(tema: str) -> dict:
    raw = (_steps(tema) / "00_pool_v3.json").read_bytes()
    if TEMAS[tema]["pool_md5"] and hashlib.md5(raw).hexdigest() != TEMAS[tema]["pool_md5"]:
        raise Parada(f"00_pool_v3.json de {tema} no es el fijado")
    return json.loads(raw.decode("utf-8"))


def _topic(tema: str) -> dict:
    """El topic de topics_db (solo lectura) con el pool de `_steps` y el perfil del seed cargado."""
    import fase1_5 as f15
    topic = copy.deepcopy(f15._load_topic_by_id(TEMAS[tema]["tid"]))
    topic["evidence_pool"] = _pool(tema)
    topic["escaleta_notas"] = None
    topic["escaleta_solo_apoyo"] = None
    topic["guion_version"] = 4
    if not f15.cargar_perfil(TEMAS[tema]["tid"]):
        raise Parada(f"{tema}: sin _perfil.json")
    return topic


def _ficha(tema: str) -> dict:
    from researcher_steps import ficha_caso as fc
    f = fc.load(TEMAS[tema]["tid"])
    if not f or "historia" not in f:
        raise Parada(f"{tema}: falta la ficha v2")
    if tema == "ycua" and not (str(f.get("chequeo_version") or "").startswith("f15b") and f.get("prompt_version") == "f15-1"):
        raise Parada("la ficha de Ycuá en _steps no es la v2 de F15b")
    if tema == "kyshtym" and f.get("prompt_version") != "f22-1":
        raise Parada("la ficha de Kyshtym en _steps no es la de F22")
    return f


def _prompt_file(tema: str, etapa: str, sis: str, usr: str) -> dict:
    (LAB / f"prompt_{tema}_f22_{etapa}.txt").write_text(
        f"===== SISTEMA (md5 {_md5(sis)}) =====\n{sis}\n\n===== USUARIO, intento 1 (md5 {_md5(usr)}) =====\n{usr}\n",
        encoding="utf-8")
    return {"sistema": _md5(sis), "usuario": _md5(usr)}


# ═══════════════════════════════════════════════════════════════

def etapa_pool(tema: str) -> None:
    """Kyshtym: el pool de F21c = los pasos deterministas de `lab/hyperframes/f21/recheck.py` (paso_pool) sobre el pool
    de F20 en disco, con el código de hoy y los txt ya bajados. Sin API. Se guarda como `00_pool_v3.json` (el de F20
    queda en `00_pool_v3_f20.json`)."""
    if tema != "kyshtym":
        return
    from researcher_steps import pool_gate as pg
    from researcher_steps import research_v3 as r3
    d = _steps(tema)
    if (d / "00_pool_v3_f20.json").exists():
        print("[kyshtym pool] ya existe: se saltea", flush=True)
        return
    perfil = json.loads((d / "_perfil.json").read_text(encoding="utf-8"))
    pool = json.loads((d / "00_pool_v3.json").read_text(encoding="utf-8"))
    r3.set_vocabulario(perfil)
    docs = (pool.get("_research_v3") or {}).get("documentos") or []
    texts = {x["id"]: r3.DocText(x["id"], (d / "fuentes" / x["txt"]).read_text(encoding="utf-8"))
             for x in docs if x.get("txt") and (d / "fuentes" / x["txt"]).exists()}
    year = perfil.get("anio_evento") or 1957
    log: list[str] = []
    r3.add_quote_authors(pool, log)
    r3.canonical_names(pool, texts)
    r3.presence_v3(pool, texts, log)
    r3.person_stats(pool, year)
    r3.canonical_v3(pool, docs, log)
    pop = r3.population_canon(pool, docs, r3.subject_re_del_perfil(perfil), log)
    if pop:
        pool["cifras_canonicas"] = [pop] + [g for g in pool["cifras_canonicas"]
                                            if g["oficial"] not in {v["id"] for v in pop["variantes"]} | {pop["oficial"]}]
    ver = r3.verify_pool(pool, texts, docs, log)
    r3.person_stats(pool, year)
    gate = pg.evaluate(pool)
    r3.set_vocabulario(None)
    pool.setdefault("_research_v3", {})["recalculo_f22"] = {
        "desde": "00_pool_v3_f20.json (F20)", "pasos": "recheck.paso_pool de F21 con el código de F22 (sin API)",
        "textos": len(texts), "verificacion": ver, "compuerta": {k: gate[k] for k in ("color", "metricas", "motivos")}}
    shutil.copy2(d / "00_pool_v3.json", d / "00_pool_v3_f20.json")
    _write(d / "00_pool_v3.json", pool)
    pers = [(p["id"], p["nombre"], p.get("elegible_humano")) for p in pool["personajes"]]
    _write(LAB / "pool_kyshtym_f22.json", {"compuerta": gate["color"], "metricas": gate["metricas"],
                                           "motivos": gate["motivos"], "verificacion": ver, "personajes": pers,
                                           "log": log})
    print(f"[kyshtym pool] compuerta {gate['color']} · {gate['metricas']} · personajes {pers}", flush=True)


def etapa_ficha(tema: str) -> None:
    if tema != "kyshtym":
        return
    import gpt_helpers
    from cost_tracker import cost_tracker
    from researcher_steps import ficha_caso as fc
    from script_engine.m01a_skeleton import STEPS_DIR
    d = _steps(tema)
    if (LAB / f"ficha_crudo_{tema}.json").exists():
        print(f"[{tema} ficha] ya existe: se saltea", flush=True)
        return
    if not (d / "00_pool_v3_f20.json").exists():
        raise Parada("kyshtym: falta el pool de F21c (etapa pool)")
    _backup(d / "_f18" / "ficha_caso.json", d / "ficha_caso_f18.json")
    _backup(d / "ficha_caso.json", d / "ficha_caso_pre_f22.json")
    import fase1_5 as f15
    titulo = f15._load_topic_by_id(TEMAS[tema]["tid"]).get("video_title") or "Kyshtym"
    pool = _pool(tema)
    sis, usr = fc.system(), fc.prompt(pool, titulo)
    md5s = _prompt_file(tema, "ficha", sis, usr)
    pin, pout = gpt_helpers.PRICES["gpt-6.1-sol"]
    worst = (len(sis) + len(usr)) / 3 / 1e6 * pin + MAX_OUT["ficha"] / 1e6 * pout
    _freno(tema, "ficha", 0.0, worst, "ficha_caso")
    print(f"[{tema} ficha] prompt {len(sis) + len(usr):,} car · max_completion_tokens {MAX_OUT['ficha']:,} · "
          f"peor caso US$ {worst:.3f}", flush=True)
    gpt_helpers.TIMEOUT_S = 2400
    n = {"posts": 0}

    def post(body: dict) -> dict:
        if n["posts"]:
            raise Parada("la llamada de la ficha ya facturó una vez: no hay reintento por el tope")
        body["max_completion_tokens"] = MAX_OUT["ficha"]
        n["posts"] += 1
        return gpt_helpers._post(body)
    cost_tracker.start_video(f"{TEMAS[tema]['tid']}-f22-ficha")
    t0 = time.time()
    try:
        res = fc.run(TEMAS[tema]["tid"], steps_dir=STEPS_DIR, title=titulo, tag=tema, out_dirs=[LAB],
                     call=gpt_helpers.make_call("gpt-6.1-sol", "high", post=post))
    finally:
        rep = cost_tracker.end_video()
    costo = _add_cost(tema, "ficha", rep, t0, {"max_completion_tokens": MAX_OUT["ficha"], "prompt_md5": md5s})
    _write(LAB / f"ficha_crudo_{tema}.json", res["crudo"])
    for p in (d / "ficha_caso.json", LAB / "ficha_caso.json"):
        f = json.loads(p.read_text(encoding="utf-8"))
        f["costo"] = costo
        f["chequeo_version"] = "f15b (afloje de cifras y sentidos)"     # el chequeo de hoy ya trae los aflojes
        _write(p, f)
    (LAB / "ficha_caso.json").rename(LAB / f"ficha_{tema}_f22.json")
    m = res["meta"]
    print(f"[{tema} ficha] crudo {m['conteos_crudo']}\n[{tema} ficha] final {m['conteos']} · sacados {m['sacados']}",
          flush=True)
    for s in res["sacados"]:
        print(f"  sacado [{s['seccion']}] {s['que'][:90]} → {s['motivo'][:150]}", flush=True)


def etapa_columna(tema: str) -> None:
    import gpt_helpers
    from cost_tracker import cost_tracker
    from script_engine import m01a_columna as mc
    d = _steps(tema)
    if (LAB / f"columna_{tema}_f22.json").exists():
        print(f"[{tema} columna] ya existe: se saltea", flush=True)
        return
    ficha, topic = _ficha(tema), _topic(tema)
    pool = topic["evidence_pool"]
    md5s = _prompt_file(tema, "columna", mc.SYSTEM, mc.build_prompt(topic, pool, ficha))
    gpt_helpers.TIMEOUT_S = 1800
    log: list[str] = []
    crudos: list = []
    base = sol_call(tema, "columna", MAX_OUT["columna"])

    def call(*a, **k):
        r = base(*a, **k)
        crudos.append(r)
        return r
    cost_tracker.start_video(f"{TEMAS[tema]['tid']}-f22-columna")
    t0 = time.time()
    err, col = None, None
    try:
        col = mc.generate_columna(topic, pool, ficha, call=call, log=log, persist=False)
    except Exception as e:  # noqa: BLE001
        err = f"{type(e).__name__}: {e}"
    finally:
        rep = cost_tracker.end_video()
    _write(LAB / f"columna_crudos_{tema}.json", crudos)
    _add_cost(tema, "columna", rep, t0, {"prompt_md5_intento1": md5s, "error": err, "log": log})
    print("\n".join(log), flush=True)
    if col is None:
        raise Parada(f"columna de {tema}: {err}")
    if tema == "ycua":
        _backup(d / "01a_columna.json", d / "01a_columna_f17.json")
    mc.save(TEMAS[tema]["tid"], col)
    _write(LAB / f"columna_{tema}_f22.json", col)
    (LAB / f"COLUMNA_{tema}.md").write_text(mc.to_markdown(col, topic.get("video_title") or tema), encoding="utf-8")
    a = col.get("antagonista") or {}
    print(f"[{tema} columna] humano {col['humano'].get('nombre')} · quién decide {a.get('tipo')} «{a.get('nombre')}» · "
          f"pico cap {col['pico'].get('cap')} · personas con nombre {col['_metricas']['personas_con_nombre']}",
          flush=True)


def etapa_escaleta(tema: str) -> None:
    import gpt_helpers
    from cost_tracker import cost_tracker
    from script_engine import m01a_columna as mc
    from script_engine import m01a_escaleta as ma
    d = _steps(tema)
    out = d / "01a_escaleta_f22.json"
    if out.exists():
        print(f"[{tema} escaleta] ya existe: se saltea", flush=True)
        return
    if not (LAB / f"columna_{tema}_f22.json").exists():
        raise Parada(f"escaleta de {tema}: falta la columna de F22")
    col = mc.load(TEMAS[tema]["tid"])
    ficha, topic = _ficha(tema), _topic(tema)
    pool = topic["evidence_pool"]
    md5s = _prompt_file(tema, "escaleta", ma.SYSTEM_V2, ma.build_prompt_v2(topic, pool, ficha, columna=col))
    gpt_helpers.TIMEOUT_S = 1800
    log: list[str] = []
    crudos: list = []
    base = sol_call(tema, "escaleta", MAX_OUT["escaleta"])

    def call(*a, **k):                                       # guarda cada respuesta (las rechazadas también)
        r = base(*a, **k)
        crudos.append(r)
        return r
    cost_tracker.start_video(f"{TEMAS[tema]['tid']}-f22-escaleta")
    t0 = time.time()
    err, esc = None, None
    try:
        esc = ma.generate_escaleta(topic, call=call, log=log, persist=False, ficha=ficha, columna=col)
    except Exception as e:  # noqa: BLE001
        err = f"{type(e).__name__}: {e}"
    finally:
        rep = cost_tracker.end_video()
    _write(LAB / f"escaleta_crudos_{tema}.json", crudos)
    _add_cost(tema, "escaleta", rep, t0, {"prompt_md5_intento1": md5s, "error": err, "log": log})
    print("\n".join(log), flush=True)
    if esc is None:
        raise Parada(f"escaleta de {tema}: {err}")
    if tema == "ycua":
        _backup(d / "01a_escaleta.json", d / "01a_escaleta_f17.json")
    _write(out, esc)
    _write(LAB / f"escaleta_{tema}_f22.json", esc)
    (LAB / f"ESCALETA_{tema}.md").write_text(ma.to_markdown(esc, pool), encoding="utf-8")
    m, mcol = esc["_metricas"], esc["_metricas"]["columna"]
    print(f"[{tema} escaleta] {len(esc['beats'])} beats · humano {esc['humano'].get('nombre')} (= columna "
          f"{mcol['humano_es_el_de_la_columna']}) · antagonista {m['antagonista_tipo']} (= columna "
          f"{mcol['antagonista_es_el_de_la_columna']}) en caps {m['antagonista_caps']} · pico beat "
          f"{esc['pico'].get('beat')} · escenas {m['escenas_usadas']}", flush=True)


def etapa_guion(tema: str) -> None:
    import gpt_helpers
    from cost_tracker import cost_tracker
    from f13_corridas import PALABRAS_POR_SEG, narracion_md, repeticion_interna
    from script_engine import guion_v4 as g4
    from script_engine import m01b_guionista as mg
    d = _steps(tema)
    if (LAB / f"guion_{tema}_f22.json").exists():
        print(f"[{tema} guion] ya existe: se saltea", flush=True)
        return
    if not (d / "01a_escaleta_f22.json").exists():
        raise Parada(f"guion de {tema}: falta la escaleta de F22")
    esc = json.loads((d / "01a_escaleta_f22.json").read_text(encoding="utf-8"))
    ficha, topic = _ficha(tema), _topic(tema)
    sis, usr = g4.system(), g4.prompt(topic, esc, ficha=ficha)
    md5s = _prompt_file(tema, "guion", sis, usr)
    gpt_helpers.TIMEOUT_S = 1200
    res: dict = {"tema": tema, "tid": TEMAS[tema]["tid"], "corrida": "f22", "modelo": "gpt-6.1-sol", "esfuerzo": "high",
                 "escaleta": "01a_escaleta_f22.json", "notas": None, "largo": "abierto",
                 "max_completion_tokens": MAX_OUT["guion"], "prompt_md5": md5s, "nota_b": g4.nota_b()}
    cost_tracker.start_video(f"{TEMAS[tema]['tid']}-f22-guion")
    t0 = time.time()
    try:
        g = g4.write(topic, esc, call=sol_call(tema, "guion", MAX_OUT["guion"]), ficha=ficha)
        res.update(prompt_version=g["prompt_version"], ficha=g.get("ficha"), parrafos=g["parrafos"])
        res["bloqueantes"] = g4.bloqueantes(topic, esc, g["parrafos"], ficha=ficha)
        res["metricas"] = g4.metricas(topic, esc, g["parrafos"])
        res["repeticion_por_cap"] = {c["chapter_number"]: repeticion_interna(c["narration"])
                                     for c in mg.caps_text(esc, g["parrafos"])}
        res["minutos"] = round(res["metricas"]["palabras"] / PALABRAS_POR_SEG / 60, 1)
    except Exception as e:  # noqa: BLE001
        res["error"] = f"{type(e).__name__}: {e}"
        res["traceback"] = traceback.format_exc()[-2000:]
    finally:
        rep = cost_tracker.end_video()
    res["costo"] = _add_cost(tema, "guion", rep, t0)
    if tema == "ycua":
        for p in sorted(d.glob("01b_*.json")):
            if not any(p.stem.endswith(s) for s in ("_v1", "_ajuste", "_f17")) and "_v4" not in p.stem:
                _backup(p, d / f"{p.stem}_f17.json")
    _write(LAB / f"guion_{tema}_f22.json", res)
    if res.get("parrafos"):
        md = narracion_md(tema, tema, esc, res).replace(f"largo abierto, gpt-6.1-sol high, corrida _f13_{tema}_abierto, F13",
                                                        "v5.2 (f22-1), gpt-6.1-sol high, columna v1.1 + escaleta v2.1, F22")
        (LAB / f"NARRACION_{tema}_f22.md").write_text(md, encoding="utf-8")
    m = res.get("metricas") or {}
    print(f"[{tema} guion] " + (f"ERROR {res['error']} · " if res.get("error") else "")
          + (f"{m['palabras']} palabras ≈ {res['minutos']} min · bloqueantes {len(res['bloqueantes'])} · párrafos "
             f"{len(res['parrafos'])} · por cap {[v[0] for v in m['palabras_por_cap'].values()]} · antagonista "
             f"{m['antagonista_tipo']} en caps {m['antagonista_caps']}" if m else ""), flush=True)
    if res.get("error"):
        raise Parada(res["error"])
    if res.get("bloqueantes"):
        raise Parada(f"guion de {tema}: {len(res['bloqueantes'])} bloqueante(s) (crudo guardado, no se parchea)")


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")                # -I ignora PYTHONIOENCODING
    etapas = {"pool": etapa_pool, "ficha": etapa_ficha, "columna": etapa_columna, "escaleta": etapa_escaleta,
              "guion": etapa_guion}
    temas = [a for a in sys.argv[1:] if a in TEMAS] or list(TEMAS)
    pedidas = [a for a in sys.argv[1:] if a in etapas] or list(etapas)
    for tema in temas:
        for e in pedidas:
            try:
                etapas[e](tema)
            except Parada as x:
                print(f"PARADA ({tema} {e}): {x}", flush=True)
                break                                       # ese tema queda en PARADA; el otro sigue
    print(f"tanda US$ {_gastado():.4f}", flush=True)


if __name__ == "__main__":
    main()
