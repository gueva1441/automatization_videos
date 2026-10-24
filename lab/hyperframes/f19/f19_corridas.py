"""F19 — Kyshtym otra vez: el research con cirílico (perfil con `nombres_locales`, `place_re` con las formas locales),
y la misma cadena de F18 (ficha → columna → escaleta → guion) con los arreglos de F19 §1.2 (antagonista persona o
institución), §1.3 (rango de beats de la compuerta en el usuario) y §2 (citas con traducción). Sin paradas.

    research  rehace run_seed para el mismo topic (`f18-kyshtym-mayak`) con la semilla de F18 (lab/hyperframes/f18/
              seed_f18.json). Antes respalda lo de F18 en _steps/<topic>/_f18/ (perfil, fuentes/, POOL_GATE, ficha,
              columna, la caché R3 de los documentos que no estaban en el pool) y el pool como 00_pool_v3_f18.json.
              Se reusan la caché R1 (las mismas 16 fuentes: la comparación aísla el cirílico) y las cachés R3 de los
              documentos que ya aportaban ítems. Perfil y descargas se rehacen (`download_sources` reusa
              `nombra_evento` del manifiesto anterior: con el manifiesto de F18 los rusos seguirían afuera).
              El pool nuevo entra en el topic de topics_db (`evidence_pool`), respaldado como topics_db.pre_f19.json.
    ficha · columna · escaleta · guion: como F18 (`f18_corridas.py`), con salidas _f19.

Topes (F19 §2): research 3.00 · ficha 0.60 · columna 0.30 · escaleta 0.60 · guion 0.30 · total 5.00 (costos_f19.json).
Cada etapa se saltea si su salida ya existe.
Uso: python -I lab/hyperframes/f19/f19_corridas.py [research ficha columna escaleta guion]
"""
from __future__ import annotations

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

TID = "f18-kyshtym-mayak"
SEED_ID = "b6b84f96-03b7-40cd-8173-414d60514c76"
NOM = "kyshtym"
IDIOMA_LOCAL = "ruso (Ozyorsk / Kyshtym, óblast de Cheliábinsk, Rusia); también español"
TOPES = {"research": 3.00, "ficha": 0.60, "columna": 0.30, "escaleta": 0.60, "guion": 0.30}
TOPE_TOTAL = 5.00
MAX_OUT = {"columna": 16000, "escaleta": 24000, "guion": 24000}
COSTOS = LAB / "costos_f19.json"


class Parada(RuntimeError):
    pass


def _md5(s: str) -> str:
    return hashlib.md5(s.encode("utf-8")).hexdigest()


def _write(p: Path, obj) -> None:
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding="utf-8")


def _costos() -> dict:
    return json.loads(COSTOS.read_text(encoding="utf-8")) if COSTOS.exists() else {"etapas": [], "usd_total": 0.0}


def _gastado(etapa: str | None = None) -> float:
    return sum(x["usd"] for x in _costos()["etapas"] if etapa is None or x["etapa"] == etapa)


def _add_cost(etapa: str, rep, t0: float, extra: dict | None = None) -> dict:
    c = _costos()
    costo = {"etapa": etapa, "usd": round(getattr(rep, "total_cost", 0.0) or 0.0, 4),
             "segundos": round(time.time() - t0, 1),
             "llamadas": [{"servicio": e.service, "desc": e.description, "in": e.tokens_in, "out": e.tokens_out,
                           "thinking": e.tokens_thinking, "usd": round(e.total_cost, 4)}
                          for e in (getattr(rep, "entries", None) or [])], **(extra or {})}
    c["etapas"].append(costo)
    c["usd_total"] = round(sum(x["usd"] for x in c["etapas"]), 4)
    _write(COSTOS, c)
    print(f"  [{etapa}] US$ {costo['usd']:.4f} · {costo['segundos']:.0f} s · tanda US$ {c['usd_total']:.4f}", flush=True)
    return costo


def _steps() -> Path:
    from script_engine.m01a_skeleton import STEPS_DIR
    return STEPS_DIR / TID


def sol_call(etapa: str, max_out: int):
    """Sol high; cada invocación: freno (paso y total) y UNA llamada que facture con `max_completion_tokens` acotado."""
    import gpt_helpers
    from cost_tracker import cost_tracker
    pin, pout = gpt_helpers.PRICES["gpt-6.1-sol"]
    paso0, total0 = _gastado(etapa), _gastado()

    def _call(prompt, system_instruction=None, response_schema=None, thinking_budget=None, description=None):
        cur = cost_tracker.current_video.total_cost if cost_tracker.current_video else 0.0
        worst = (len(prompt) + len(system_instruction or "")) / 3 / 1e6 * pin + max_out / 1e6 * pout
        if paso0 + cur + worst > TOPES[etapa] or total0 + cur + worst > TOPE_TOTAL:
            raise Parada(f"tope de costo antes de «{description}»: paso {paso0 + cur:.3f} + peor caso {worst:.3f} > "
                         f"{TOPES[etapa]:.2f} (o total {total0 + cur + worst:.3f} > {TOPE_TOTAL:.2f})")
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


def _topic() -> dict:
    import fase1_5 as f15
    topic = dict(f15._load_topic_by_id(TID))               # solo lectura
    topic["escaleta_notas"] = None
    topic["escaleta_solo_apoyo"] = None
    topic["guion_version"] = 4
    return topic


def _ficha() -> dict:
    from researcher_steps import ficha_caso as fc
    f = fc.load(TID)
    if not f or "historia" not in f:
        raise Parada("falta la ficha v2 de Kyshtym")
    return f


# ═══════════════════════════════════════════════════════════════

def etapa_research() -> None:
    import fase1_5 as f15
    from config import DATA_DIR
    from cost_tracker import cost_tracker
    from researcher_steps import pool_gate as pg
    from researcher_steps import research_v3 as r3
    d = _steps()
    if (d / "00_pool_v3_f18.json").exists() and (d / "_perfil.json").exists() and \
            "nombres_locales" in json.loads((d / "_perfil.json").read_text(encoding="utf-8")):
        print("[research] ya existe (perfil con nombres_locales): se saltea", flush=True)
        return
    seed = json.loads((LAB.parent / "f18" / "seed_f18.json").read_text(encoding="utf-8"))
    bak = d / "_f18"
    bak.mkdir(exist_ok=True)
    if not (d / "00_pool_v3_f18.json").exists():
        shutil.copy2(d / "00_pool_v3.json", d / "00_pool_v3_f18.json")
    for name in ("_perfil.json", "POOL_GATE.md", "fuentes.json", "ficha_caso.json", "FICHA_kyshtym.md",
                 "01a_columna.json", "fuentes"):
        if (d / name).exists() and not (bak / name).exists():
            shutil.move(str(d / name), str(bak / name))
    man18 = json.loads((bak / "fuentes" / "manifest.json").read_text(encoding="utf-8"))
    pool18 = json.loads((d / "00_pool_v3_f18.json").read_text(encoding="utf-8"))
    con_items = {x for k in ("datos", "cronologia", "citas", "personajes", "lugares") for it in pool18.get(k) or []
                 for x in it.get("docs") or []}
    (bak / "_r3_cache").mkdir(exist_ok=True)
    for doc in man18["documentos"]:                     # R3 de nuevo para los que no aportaban (los rusos)
        c = d / "_r3_cache" / f"r3_{doc['id']}.json"
        if c.exists() and doc["id"] not in con_items:
            shutil.move(str(c), str(bak / "_r3_cache" / c.name))
    db = DATA_DIR / "topics_db.json"
    if not (DATA_DIR / "topics_db.pre_f19.json").exists():
        shutil.copy2(db, DATA_DIR / "topics_db.pre_f19.json")
    log: list[str] = []
    t0 = time.time()
    cost_tracker.start_video(f"{TID}-f19-research")
    err, pool, color = None, None, None
    try:
        pool, _, gate = r3.run_seed(seed, TID, d, log=log)
        color = gate["color"] if gate else None
    except pg.PoolGateRed as e:
        color, err = pg.RED, "rojo: " + "; ".join(e.gate["motivos"])
    except Exception as e:  # noqa: BLE001
        err = f"{type(e).__name__}: {e}"
        log.append(traceback.format_exc())
    finally:
        rep = cost_tracker.end_video()
    (LAB / "run_research_detalle.log").write_text("\n".join(log), encoding="utf-8")
    for src, dst in ((d / "POOL_GATE.md", "POOL_GATE.md"), (d / "fuentes.json", "fuentes.json"),
                     (d / "fuentes" / "manifest.json", "manifest.json"), (d / "_perfil.json", "perfil.json")):
        if src.exists():
            shutil.copy2(src, LAB / dst)
    _add_cost("research", rep, t0, {"color": color, "error": err})
    if pool is None:
        raise Parada(f"research: {err}")
    raw = json.loads(db.read_text(encoding="utf-8"))           # el pool nuevo entra en el topic (solo este topic)
    topics = raw["topics"] if isinstance(raw, dict) else raw
    t = next(x for x in topics if x.get("id") == TID)
    t["evidence_pool"] = pool
    db.write_text(json.dumps(raw, indent=2, ensure_ascii=False), encoding="utf-8")
    if f15._load_topic_by_id(TID)["evidence_pool"].get("datos") != pool.get("datos"):
        raise Parada("el pool del topic no quedó igual al de _steps")
    if _gastado("research") > TOPES["research"]:
        raise Parada(f"research gastó US$ {_gastado('research'):.3f} > tope {TOPES['research']:.2f}")
    print(f"[research] compuerta {color} · datos {len(pool.get('datos') or [])} · citas {len(pool.get('citas') or [])}"
          f" · personajes {len(pool.get('personajes') or [])}", flush=True)


def etapa_ficha() -> None:
    from cost_tracker import cost_tracker
    from researcher_steps import ficha_caso as fc
    from script_engine.m01a_skeleton import STEPS_DIR
    import gpt_helpers
    if (LAB / f"ficha_crudo_{NOM}.json").exists():
        print("[ficha] ya existe: se saltea", flush=True)
        return
    topic = _topic()
    titulo = topic.get("video_title") or "Kyshtym"
    pool = json.loads((_steps() / "00_pool_v3.json").read_text("utf-8"))
    sis, usr = fc.system(), fc.prompt(pool, titulo)
    (LAB / f"prompt_{NOM}_f19_ficha.txt").write_text(
        f"===== SISTEMA (md5 {_md5(sis)}) =====\n{sis}\n\n===== USUARIO (md5 {_md5(usr)}) =====\n{usr}\n", encoding="utf-8")
    pin, pout = gpt_helpers.PRICES["gpt-6.1-sol"]
    in_usd = (len(sis) + len(usr)) / 3 / 1e6 * pin
    max_out = min(60000, int((min(TOPES["ficha"], TOPE_TOTAL - _gastado()) - in_usd) / pout * 1e6))
    print(f"[ficha] prompt {len(sis) + len(usr):,} car · max_completion_tokens {max_out:,}", flush=True)
    if max_out < 20000:
        raise Parada(f"no alcanza el tope para la ficha (max_out {max_out})")
    gpt_helpers.TIMEOUT_S = 2400
    n = {"posts": 0}

    def post(body: dict) -> dict:
        if n["posts"]:
            raise Parada("la llamada de la ficha ya facturó una vez: no hay reintento por el tope")
        body["max_completion_tokens"] = max_out
        n["posts"] += 1
        return gpt_helpers._post(body)
    cost_tracker.start_video(f"{TID}-f19-ficha")
    t0 = time.time()
    try:
        res = fc.run(TID, steps_dir=STEPS_DIR, title=titulo, tag=NOM, out_dirs=[LAB],
                     call=gpt_helpers.make_call("gpt-6.1-sol", "high", post=post))
    finally:
        rep = cost_tracker.end_video()
    costo = _add_cost("ficha", rep, t0, {"max_completion_tokens": max_out,
                                         "prompt_md5": {"sistema": _md5(sis), "usuario": _md5(usr)}})
    _write(LAB / f"ficha_crudo_{NOM}.json", res["crudo"])
    for p in (_steps() / "ficha_caso.json", LAB / "ficha_caso.json"):
        f = json.loads(p.read_text(encoding="utf-8"))
        f["costo"] = costo
        f["chequeo_version"] = "f15b (afloje de cifras y sentidos)"     # el chequeo de hoy ya trae los aflojes
        _write(p, f)
    m = res["meta"]
    print(f"[ficha] crudo {m['conteos_crudo']}\n[ficha] final {m['conteos']} · sacados {m['sacados']}", flush=True)
    for s in res["sacados"]:
        print(f"  sacado [{s['seccion']}] {s['que'][:90]} → {s['motivo'][:150]}", flush=True)


def etapa_columna() -> None:
    import gpt_helpers
    from cost_tracker import cost_tracker
    from script_engine import m01a_columna as mc
    if mc.load(TID):
        print("[columna] ya existe: se saltea", flush=True)
        return
    ficha, topic = _ficha(), _topic()
    pool = topic["evidence_pool"]
    p1 = mc.build_prompt(topic, pool, ficha)
    (LAB / f"prompt_{NOM}_f19_columna.txt").write_text(
        f"===== SISTEMA (md5 {_md5(mc.SYSTEM)}) =====\n{mc.SYSTEM}\n\n===== USUARIO, intento 1 (md5 {_md5(p1)}) "
        f"=====\n{p1}\n", encoding="utf-8")
    gpt_helpers.TIMEOUT_S = 1800
    log: list[str] = []
    cost_tracker.start_video(f"{TID}-f19-columna")
    t0 = time.time()
    err, col = None, None
    try:
        col = mc.generate_columna(topic, pool, ficha, call=sol_call("columna", MAX_OUT["columna"]), log=log,
                                  persist=False)
    except Exception as e:  # noqa: BLE001
        err = f"{type(e).__name__}: {e}"
    finally:
        rep = cost_tracker.end_video()
    _add_cost("columna", rep, t0, {"prompt_md5_intento1": {"sistema": _md5(mc.SYSTEM), "usuario": _md5(p1)},
                                   "error": err, "log": log})
    print("\n".join(log), flush=True)
    if col is None:
        raise Parada(f"columna: {err}")
    mc.save(TID, col)
    _write(LAB / f"columna_{NOM}_f19.json", col)
    (LAB / f"COLUMNA_{NOM}.md").write_text(mc.to_markdown(col, topic.get("video_title") or NOM), encoding="utf-8")
    print(f"[columna] humano {col['humano'].get('nombre')} · pico cap {col['pico'].get('cap')} · personas con nombre "
          f"{col['_metricas']['personas_con_nombre']} · afuera {len(col.get('afuera') or [])}", flush=True)


def etapa_escaleta() -> None:
    import gpt_helpers
    from cost_tracker import cost_tracker
    from script_engine import m01a_columna as mc
    from script_engine import m01a_escaleta as ma
    out = _steps() / "01a_escaleta_f19.json"
    if out.exists():
        print("[escaleta] ya existe: se saltea", flush=True)
        return
    col = mc.load(TID)
    if not col:
        raise Parada("escaleta: falta la columna")
    ficha, topic = _ficha(), _topic()
    pool = topic["evidence_pool"]
    p1 = ma.build_prompt_v2(topic, pool, ficha, columna=col)
    (LAB / f"prompt_{NOM}_f19_escaleta.txt").write_text(
        f"===== SISTEMA (md5 {_md5(ma.SYSTEM_V2)}) =====\n{ma.SYSTEM_V2}\n\n===== USUARIO, intento 1 (md5 {_md5(p1)}) "
        f"=====\n{p1}\n", encoding="utf-8")
    gpt_helpers.TIMEOUT_S = 1800
    log: list[str] = []
    pase = 1 + sum(1 for x in _costos()["etapas"] if x["etapa"] == "escaleta")
    crudos: list = []
    base = sol_call("escaleta", MAX_OUT["escaleta"])

    def call(*a, **k):                                       # guarda cada respuesta (las rechazadas también)
        r = base(*a, **k)
        crudos.append(r)
        return r
    cost_tracker.start_video(f"{TID}-f19-escaleta")
    t0 = time.time()
    err, esc = None, None
    try:
        esc = ma.generate_escaleta(topic, call=call, log=log, persist=False, ficha=ficha, columna=col)
    except Exception as e:  # noqa: BLE001
        err = f"{type(e).__name__}: {e}"
    finally:
        rep = cost_tracker.end_video()
    _write(LAB / f"escaleta_crudos_pase{pase}.json", crudos)
    _add_cost("escaleta", rep, t0, {"pase": pase, "prompt_md5_intento1": {"sistema": _md5(ma.SYSTEM_V2),
                                                                         "usuario": _md5(p1)},
                                    "error": err, "log": log})
    print("\n".join(log), flush=True)
    if esc is None:
        raise Parada(f"escaleta: {err}")
    _write(out, esc)
    _write(LAB / f"escaleta_{NOM}_f19.json", esc)
    (LAB / f"ESCALETA_{NOM}.md").write_text(ma.to_markdown(esc, pool), encoding="utf-8")
    m, mcol = esc["_metricas"], esc["_metricas"]["columna"]
    print(f"[escaleta] {len(esc['beats'])} beats · humano {esc['humano'].get('nombre')} (= columna "
          f"{mcol['humano_es_el_de_la_columna']}) · caps con personas fuera {mcol['caps_con_personas_fuera']} · cierres "
          f"iguales {mcol['cierres_iguales']}/7 · pico beat {esc['pico'].get('beat')} · escenas {m['escenas_usadas']}",
          flush=True)


def etapa_guion() -> None:
    import gpt_helpers
    from cost_tracker import cost_tracker
    from f13_corridas import PALABRAS_POR_SEG, narracion_md, repeticion_interna
    from script_engine import guion_v4 as g4
    from script_engine import m01b_guionista as mg
    if (LAB / f"guion_{NOM}_f19.json").exists():
        print("[guion] ya existe: se saltea", flush=True)
        return
    esc = json.loads((_steps() / "01a_escaleta_f19.json").read_text(encoding="utf-8"))
    ficha, topic = _ficha(), _topic()
    sis, usr = g4.system(), g4.prompt(topic, esc, ficha=ficha)
    (LAB / f"prompt_{NOM}_f19_guion.txt").write_text(
        f"===== SISTEMA (md5 {_md5(sis)}) =====\n{sis}\n\n===== USUARIO (md5 {_md5(usr)}) =====\n{usr}\n", encoding="utf-8")
    gpt_helpers.TIMEOUT_S = 1200
    res: dict = {"tema": NOM, "tid": TID, "corrida": "f19", "modelo": "gpt-6.1-sol", "esfuerzo": "high",
                 "escaleta": "01a_escaleta_f19.json", "notas": None, "largo": "abierto",
                 "max_completion_tokens": MAX_OUT["guion"], "prompt_md5": {"sistema": _md5(sis), "usuario": _md5(usr)}}
    cost_tracker.start_video(f"{TID}-f19-guion")
    t0 = time.time()
    try:
        g = g4.write(topic, esc, call=sol_call("guion", MAX_OUT["guion"]), ficha=ficha)
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
    res["costo"] = _add_cost("guion", rep, t0)
    _write(LAB / f"guion_{NOM}_f19.json", res)
    if res.get("parrafos"):
        md = narracion_md(NOM, NOM, esc, res).replace(f"largo abierto, gpt-6.1-sol high, corrida _f13_{NOM}_abierto, F13",
                                                      "v5.1 (f15b-1), gpt-6.1-sol high, columna + escaleta v2 (f17-1), F19")
        (LAB / f"NARRACION_{NOM}_f19.md").write_text(md, encoding="utf-8")
    m = res.get("metricas") or {}
    print("[guion] " + (f"ERROR {res['error']} · " if res.get("error") else "")
          + (f"{m['palabras']} palabras ≈ {res['minutos']} min · bloqueantes {len(res['bloqueantes'])} · párrafos "
             f"{len(res['parrafos'])} · por cap {[v[0] for v in m['palabras_por_cap'].values()]}" if m else ""), flush=True)
    if res.get("error"):
        raise Parada(res["error"])


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")                # -I ignora PYTHONIOENCODING
    etapas = {"research": etapa_research, "ficha": etapa_ficha, "columna": etapa_columna, "escaleta": etapa_escaleta,
              "guion": etapa_guion}
    pedidas = [a for a in sys.argv[1:] if a in etapas] or list(etapas)
    for e in pedidas:
        try:
            etapas[e]()
        except Parada as x:
            print(f"PARADA ({e}): {x}", flush=True)
            break
    print(f"tanda US$ {_gastado():.4f}", flush=True)


if __name__ == "__main__":
    main()
