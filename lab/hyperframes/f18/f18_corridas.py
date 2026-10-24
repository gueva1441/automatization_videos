"""F18 — Kyshtym / Mayak: la cadena completa en un tema nuevo, sin paradas intermedias.

    research  topic_researcher.research_topics(long) con la semilla b6b84f96 de data/selected_seeds.json, tal cual, más
              el idioma local (ruso; también español) e id fijo `f18-kyshtym-mayak` (como f10_topic_ycua.py): run_seed
              (R1–R5 + compuerta) → 4a–4e → topics_db. Rojo → PARADA con POOL_GATE.md. Copia POOL_GATE.md a lab/.
    ficha     researcher_steps.ficha_caso.run (prompt f15-1, chequeo con los aflojes de F15b) → FICHA_kyshtym.md.
    columna   m01a_columna.generate_columna (f17-1, sin notas; una regeneración) → COLUMNA_kyshtym.md.
    escaleta  m01a_escaleta.generate_escaleta(ficha=…, columna=…) (f17-1; 13 bloqueantes; una regeneración).
    guion     guion_v4.write (v5.1, Sol high) → NARRACION_kyshtym_f18.md.

Topes (§2): research 3.00 · ficha 0.60 · columna 0.30 · escaleta 0.60 · guion 0.30 · total 5.00 (costos_f18.json).
Las llamadas de Sol pasan por un freno ANTES de facturar (lo gastado en el paso + el peor caso con
`max_completion_tokens` acotado no puede pasar el tope del paso ni el total) y facturan una sola vez. El research
(Gemini, adentro de research_v3) no se puede frenar por llamada sin tocar research_v3: se mide al final y si pasó su
tope la cadena se corta (PARADA).
Cada etapa se saltea si su salida ya existe.
Uso: python -I lab/hyperframes/f18/f18_corridas.py [research ficha columna escaleta guion]
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
COSTOS = LAB / "costos_f18.json"


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
    import topic_researcher as tr
    from cost_tracker import cost_tracker
    from researcher_steps import pool_gate as pg
    from config import DATA_DIR
    d = _steps()
    if (d / "00_pool_v3.json").exists() and any(t.get("id") == TID for t in tr._load_topics_db()["topics"]):
        print("[research] ya existe: se saltea", flush=True)
        return
    seeds = [s for s in tr._load_seeds() if s.get("seed_id") == SEED_ID]
    if not seeds:
        raise Parada(f"la semilla {SEED_ID} no está en data/selected_seeds.json")
    seed = {**seeds[0], "idioma_local": IDIOMA_LOCAL}           # §1.2: ruso además de inglés y español
    _write(LAB / "seed_f18.json", seed)
    db = DATA_DIR / "topics_db.json"
    if db.exists() and not (DATA_DIR / "topics_db.pre_f18.json").exists():
        shutil.copy2(db, DATA_DIR / "topics_db.pre_f18.json")

    class _FixedUUID:
        def __str__(self) -> str:
            return TID
    tr.uuid.uuid4 = lambda: _FixedUUID()                     # el topic_id = la carpeta de pasos
    t0 = time.time()
    cost_tracker.start_video(f"{TID}-research")
    err = None
    try:
        out = tr.research_topics(seeds=[seed], video_type="long")
    except Exception as e:  # noqa: BLE001
        out, err = [], f"{type(e).__name__}: {e}"
        traceback.print_exc()
    finally:
        rep = cost_tracker.end_video()
    gate_md = d / "POOL_GATE.md"
    if gate_md.exists():
        shutil.copy2(gate_md, LAB / "POOL_GATE.md")
    for src, dst in ((d / "fuentes.json", "fuentes.json"), (d / "fuentes" / "manifest.json", "manifest.json"),
                     (d / "_perfil.json", "perfil.json")):
        if src.exists():
            shutil.copy2(src, LAB / dst)
    pool = json.loads((d / "00_pool_v3.json").read_text(encoding="utf-8")) if (d / "00_pool_v3.json").exists() else {}
    gate = pg.evaluate(pool) if pool else {}                # solo lee: el POOL_GATE.md ya lo escribió run_seed
    color = gate.get("color")
    _add_cost("research", rep, t0, {"topics": [t.get("id") for t in out], "color": color,
                                    "metricas": gate.get("metricas"), "motivos": gate.get("motivos"), "error": err})
    if not out:
        raise Parada(f"research sin topic (compuerta {color}; ver POOL_GATE.md){': ' + err if err else ''}")
    if _gastado("research") > TOPES["research"]:
        raise Parada(f"research gastó US$ {_gastado('research'):.3f} > tope {TOPES['research']:.2f}")
    print(f"[research] topic {out[0].get('id')} · «{out[0].get('video_title')}» · compuerta {color}", flush=True)


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
    (LAB / f"prompt_{NOM}_f18_ficha.txt").write_text(
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
    cost_tracker.start_video(f"{TID}-f18-ficha")
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
    (LAB / f"prompt_{NOM}_f18_columna.txt").write_text(
        f"===== SISTEMA (md5 {_md5(mc.SYSTEM)}) =====\n{mc.SYSTEM}\n\n===== USUARIO, intento 1 (md5 {_md5(p1)}) "
        f"=====\n{p1}\n", encoding="utf-8")
    gpt_helpers.TIMEOUT_S = 1800
    log: list[str] = []
    cost_tracker.start_video(f"{TID}-f18-columna")
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
    _write(LAB / f"columna_{NOM}_f18.json", col)
    (LAB / f"COLUMNA_{NOM}.md").write_text(mc.to_markdown(col, topic.get("video_title") or NOM), encoding="utf-8")
    print(f"[columna] humano {col['humano'].get('nombre')} · pico cap {col['pico'].get('cap')} · personas con nombre "
          f"{col['_metricas']['personas_con_nombre']} · afuera {len(col.get('afuera') or [])}", flush=True)


def etapa_escaleta() -> None:
    import gpt_helpers
    from cost_tracker import cost_tracker
    from script_engine import m01a_columna as mc
    from script_engine import m01a_escaleta as ma
    out = _steps() / "01a_escaleta_f18.json"
    if out.exists():
        print("[escaleta] ya existe: se saltea", flush=True)
        return
    col = mc.load(TID)
    if not col:
        raise Parada("escaleta: falta la columna")
    ficha, topic = _ficha(), _topic()
    pool = topic["evidence_pool"]
    p1 = ma.build_prompt_v2(topic, pool, ficha, columna=col)
    (LAB / f"prompt_{NOM}_f18_escaleta.txt").write_text(
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
    cost_tracker.start_video(f"{TID}-f18-escaleta")
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
    _write(LAB / f"escaleta_{NOM}_f18.json", esc)
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
    if (LAB / f"guion_{NOM}_f18.json").exists():
        print("[guion] ya existe: se saltea", flush=True)
        return
    esc = json.loads((_steps() / "01a_escaleta_f18.json").read_text(encoding="utf-8"))
    ficha, topic = _ficha(), _topic()
    sis, usr = g4.system(), g4.prompt(topic, esc, ficha=ficha)
    (LAB / f"prompt_{NOM}_f18_guion.txt").write_text(
        f"===== SISTEMA (md5 {_md5(sis)}) =====\n{sis}\n\n===== USUARIO (md5 {_md5(usr)}) =====\n{usr}\n", encoding="utf-8")
    gpt_helpers.TIMEOUT_S = 1200
    res: dict = {"tema": NOM, "tid": TID, "corrida": "f18", "modelo": "gpt-6.1-sol", "esfuerzo": "high",
                 "escaleta": "01a_escaleta_f18.json", "notas": None, "largo": "abierto",
                 "max_completion_tokens": MAX_OUT["guion"], "prompt_md5": {"sistema": _md5(sis), "usuario": _md5(usr)}}
    cost_tracker.start_video(f"{TID}-f18-guion")
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
    _write(LAB / f"guion_{NOM}_f18.json", res)
    if res.get("parrafos"):
        md = narracion_md(NOM, NOM, esc, res).replace(f"largo abierto, gpt-6.1-sol high, corrida _f13_{NOM}_abierto, F13",
                                                      "v5.1 (f15b-1), gpt-6.1-sol high, columna + escaleta v2 (f17-1), F18")
        (LAB / f"NARRACION_{NOM}_f18.md").write_text(md, encoding="utf-8")
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
