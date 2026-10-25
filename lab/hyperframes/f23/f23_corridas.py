"""F23 §2 — Kyshtym completo desde la semilla con todo F21–F23, y los perfiles nuevos de Orleans e Ycuá.

    perfiles  Orleans / Ycuá: `seed_profile` (1 Flash cada uno) con la misma semilla de siempre; de lo que devuelve se
              suman SOLO los campos nuevos (anio_inicio, anio_fin, tipo_evento, cobertura_ingles, idiomas_research): el
              resto del perfil (nombres, place_re, vocabulario) no se toca, porque esos pools no se rehacen. Respaldo
              `_perfil_f22.json`.
    research  Kyshtym: `run_seed` desde la semilla de F18 con el perfil NUEVO (el de F22 → `_perfil_f22.json`), R1 y
              R3 sin caché (→ `_f22/`; R3 tiene que leer `nombre_en_documento`/`autor_en_documento`), descargas
              reusadas. Pool de F22 → `00_pool_v3_f22.json`. Rojo → PARADA. `topics_db` no se toca.
    ficha     ficha v2.2 (Sol high) sobre el pool nuevo. La de F22 → `ficha_caso_f22.json`.
    escaleta  escaleta v2.1/f22-2 sin columna (Sol high).
    guion     guion v5.3 (Fable 5.1, effort high).
Topes (§2): research 3.50 · ficha 0.60 · escaleta 0.40 · guion 1.20 · total 6.00 (`costos_f23.json`). Freno antes de
cada llamada de Sol/Fable (lo gastado + el peor caso con la salida acotada) y una sola facturación por llamada; el
research, con el freno de F20 sobre cada llamada de Gemini.
Uso: python -I lab/hyperframes/f23/f23_corridas.py [perfiles research ficha escaleta guion]
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
sys.path[:0] = [str(LAB), str(ROOT), str(LAB.parent / "f13"), str(LAB.parent / "f22"), str(LAB.parent / "f22b")]
STEPS = ROOT / "data" / "scripts" / "_steps"
KYS = "f18-kyshtym-mayak"
TOPES = {"perfiles": 0.10, "research": 3.50, "ficha": 0.60, "escaleta": 0.40, "guion": 1.20}
TOPE_TOTAL = 6.00
MAX_OUT = {"ficha": 50000, "escaleta": 16000, "guion": 21000}   # peor caso de cada llamada dentro del tope del paso
MARGEN_GEMINI = 0.05
COSTOS = LAB / "costos_f23.json"
SEMILLAS = {
    "ba6c3cac-f7r3": {"seed_title": "La Prisión Parroquial de Orleans durante el huracán Katrina: los presos abandonados "
                                    "en sus celdas (Nueva Orleans, 29 de agosto de 2005)",
                      "idioma_local": "inglés (Nueva Orleans, EE. UU.)"},
    "f8s1-ycua-bolanos": {"seed_title": "El incendio del supermercado Ycuá Bolaños: las puertas que cerraron con la gente "
                                        "adentro (Asunción, 1 de agosto de 2004)",
                          "idioma_local": "español (Asunción, Paraguay); también guaraní"},
}
CAMPOS_NUEVOS = ("anio_inicio", "anio_fin", "tipo_evento", "cobertura_ingles", "idiomas_research")


class Parada(RuntimeError):
    pass


def _md5(s: str) -> str:
    return hashlib.md5(s.encode("utf-8")).hexdigest()


def _write(p: Path, obj) -> None:
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding="utf-8")


def _j(p: Path):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def _costos() -> dict:
    return _j(COSTOS) or {"etapas": [], "usd_total": 0.0}


def _gastado(etapa: str | None = None) -> float:
    return sum(x["usd"] for x in _costos()["etapas"] if etapa is None or x["etapa"] == etapa)


def _add_cost(etapa: str, rep, t0: float, extra: dict | None = None) -> dict:
    c = _costos()
    costo = {"etapa": etapa, "usd": round(getattr(rep, "total_cost", 0.0) or 0.0, 4), "segundos": round(time.time() - t0, 1),
             "llamadas": [{"servicio": e.service, "desc": e.description, "in": e.tokens_in, "out": e.tokens_out,
                           "thinking": e.tokens_thinking, "usd": round(e.total_cost, 4)}
                          for e in (getattr(rep, "entries", None) or [])], **(extra or {})}
    c["etapas"].append(costo)
    c["usd_total"] = round(sum(x["usd"] for x in c["etapas"]), 4)
    _write(COSTOS, c)
    print(f"  [{etapa}] US$ {costo['usd']:.4f} · {costo['segundos']:.0f} s · tanda US$ {c['usd_total']:.4f}", flush=True)
    return costo


def _freno(etapa: str, cur: float, worst: float, desc: str) -> None:
    paso, total = _gastado(etapa) + cur, _gastado() + cur
    if paso + worst > TOPES[etapa] or total + worst > TOPE_TOTAL:
        raise Parada(f"tope antes de «{desc}»: paso US$ {paso:.3f} + peor caso {worst:.3f} > {TOPES[etapa]:.2f} (o total "
                     f"{total + worst:.3f} > {TOPE_TOTAL:.2f})")


def llm_call(etapa: str, modelo: str):
    """Sol o Claude, effort high, salida acotada a MAX_OUT[etapa]; freno y una sola facturación por llamada."""
    from cost_tracker import cost_tracker
    if modelo.startswith("claude"):
        import claude_helpers as hx
    else:
        import gpt_helpers as hx
    hx.TIMEOUT_S = 2400
    pin, pout = hx.PRICES[modelo]

    def _call(prompt, system_instruction=None, response_schema=None, thinking_budget=None, description=None):
        cur = cost_tracker.current_video.total_cost if cost_tracker.current_video else 0.0
        worst = (len(prompt) + len(system_instruction or "")) / 3 / 1e6 * pin + MAX_OUT[etapa] / 1e6 * pout
        _freno(etapa, cur, worst, str(description))
        n = {"posts": 0}

        def post(body: dict) -> dict:
            if n["posts"]:
                raise Parada("la llamada ya facturó una vez (JSON roto o cortado): no hay reintento por el tope")
            body["max_tokens" if modelo.startswith("claude") else "max_completion_tokens"] = MAX_OUT[etapa]
            n["posts"] += 1
            return hx._post(body)
        return hx.make_call(modelo, "high", post=post)(prompt, system_instruction=system_instruction,
                                                       response_schema=response_schema, description=description)
    return _call


def _frenos_gemini(etapa: str):
    """El freno de F20: cada llamada de Gemini del research (o del perfil) mira lo gastado + un margen."""
    import gemini_helpers
    from cost_tracker import cost_tracker
    from researcher_steps import research_v3 as r3
    orig = {(gemini_helpers, "call_pro_json"): gemini_helpers.call_pro_json,
            (gemini_helpers, "call_flash_json"): gemini_helpers.call_flash_json,
            (r3, "search_pro"): r3.search_pro, (r3, "search_flash"): r3.search_flash}

    def wrap(fn, name):
        def _f(*a, **k):
            cur = cost_tracker.current_video.total_cost if cost_tracker.current_video else 0.0
            _freno(etapa, cur, MARGEN_GEMINI, name)
            return fn(*a, **k)
        return _f
    for (mod, name), fn in orig.items():
        setattr(mod, name, wrap(fn, name))

    def undo():
        for (mod, name), fn in orig.items():
            setattr(mod, name, fn)
    return undo


# ═══════════════════════════════════════════════════════════════

def etapa_perfiles() -> None:
    from cost_tracker import cost_tracker
    from researcher_steps import research_v3 as r3
    if (LAB / "perfiles_f23.json").exists():
        print("[perfiles] ya existe: se saltea", flush=True)
        return
    undo = _frenos_gemini("perfiles")
    cost_tracker.start_video("f23-perfiles")
    t0 = time.time()
    res = {}
    try:
        for tid, seed in SEMILLAS.items():
            d = STEPS / tid
            prof = _j(d / "_perfil.json") or {}
            if not (d / "_perfil_f22.json").exists():
                shutil.copy2(d / "_perfil.json", d / "_perfil_f22.json")
            nuevo = r3.seed_profile(seed)
            prof.update({k: nuevo.get(k) for k in CAMPOS_NUEVOS})
            prof["_f23"] = "anio_inicio/anio_fin/tipo_evento/cobertura_ingles/idiomas_research de seed_profile (Flash)"
            _write(d / "_perfil.json", prof)
            res[tid] = {k: prof.get(k) for k in ("anio_evento",) + CAMPOS_NUEVOS}
            print(f"[perfiles] {tid}: {res[tid]}", flush=True)
    finally:
        rep = cost_tracker.end_video()
        undo()
    _add_cost("perfiles", rep, t0, {"perfiles": res})
    _write(LAB / "perfiles_f23.json", res)


def etapa_research() -> None:
    from cost_tracker import cost_tracker
    from researcher_steps import pool_gate as pg
    from researcher_steps import research_v3 as r3
    d = STEPS / KYS
    if (d / "00_pool_v3_f22.json").exists() and (LAB / "kyshtym_research_f23.json").exists():
        print("[research] ya existe: se saltea", flush=True)
        return
    bak = d / "_f22"
    bak.mkdir(exist_ok=True)
    if not (d / "00_pool_v3_f22.json").exists():
        shutil.copy2(d / "00_pool_v3.json", d / "00_pool_v3_f22.json")
    if not (d / "_perfil_f22.json").exists():
        shutil.copy2(d / "_perfil.json", d / "_perfil_f22.json")
    for src in ("_perfil.json", "_r1_cache.json", "_r3_cache", "POOL_GATE.md", "fuentes.json"):
        if (d / src).exists() and not (bak / src).exists():
            shutil.move(str(d / src), str(bak / src))
    if (d / "fuentes" / "manifest.json").exists() and not (bak / "manifest.json").exists():
        shutil.copy2(d / "fuentes" / "manifest.json", bak / "manifest.json")
    seed = json.loads((LAB.parent / "f18" / "seed_f18.json").read_text(encoding="utf-8"))
    log: list[str] = []
    t0 = time.time()
    undo = _frenos_gemini("research")
    cost_tracker.start_video(f"{KYS}-f23-research")
    err, pool, gate = None, None, None
    try:
        pool, _, gate = r3.run_seed(seed, KYS, d, log=log)
    except pg.PoolGateRed as e:
        gate, err = e.gate, "rojo: " + "; ".join(e.gate["motivos"])
        pool = _j(d / "00_pool_v3.json")
    except Exception as e:  # noqa: BLE001
        err = f"{type(e).__name__}: {e}"
        log.append(traceback.format_exc())
    finally:
        rep = cost_tracker.end_video()
        undo()
        r3.set_vocabulario(None)
        r3.set_idiomas(None)
    (LAB / "run_research_detalle.log").write_text("\n".join(log), encoding="utf-8")
    for src, dst in ((d / "POOL_GATE.md", "POOL_GATE.md"), (d / "_perfil.json", "perfil_kyshtym_f23.json"),
                     (d / "fuentes.json", "fuentes_f23.json"), (d / "fuentes" / "manifest.json", "manifest_f23.json")):
        if src.exists():
            shutil.copy2(src, LAB / dst)
    _add_cost("research", rep, t0, {"color": (gate or {}).get("color"), "error": err})
    res = {"error": err, "gate": {k: (gate or {}).get(k) for k in ("color", "metricas", "motivos")}}
    if pool:
        res["personajes"] = [{k: p.get(k) for k in ("id", "nombre", "nombre_en_documento", "rol", "testigo",
                                                     "antagonista", "n_citas", "n_datos", "presente_en_evento",
                                                     "elegible_humano")} for p in pool.get("personajes") or []]
        res["citas"] = [{k: q.get(k) for k in ("id", "autor", "autor_en_documento", "doc_id")}
                        | {"estado": (q.get("verificacion") or {}).get("estado"),
                           "motivo": (q.get("verificacion") or {}).get("motivo")} for q in pool.get("citas") or []]
        res["descartados_contaminacion"] = [x for x in pool.get("_descartados") or []
                                            if str(x.get("motivo") or "").startswith("contaminación")]
    _write(LAB / "kyshtym_research_f23.json", res)
    if err:
        raise Parada(f"research: {err}")
    print(f"[research] compuerta {gate['color']} {gate['metricas']}", flush=True)


def etapa_ficha() -> None:
    import gpt_helpers
    from cost_tracker import cost_tracker
    from researcher_steps import ficha_caso as fc
    from script_engine.m01a_skeleton import STEPS_DIR
    d = STEPS / KYS
    if (LAB / "ficha_crudo_kyshtym.json").exists():
        print("[ficha] ya existe: se saltea", flush=True)
        return
    if not (LAB / "kyshtym_research_f23.json").exists():
        raise Parada("ficha: falta el research de F23")
    if (d / "ficha_caso.json").exists() and not (d / "ficha_caso_f22.json").exists():
        shutil.copy2(d / "ficha_caso.json", d / "ficha_caso_f22.json")
    import fase1_5 as f15
    titulo = f15._load_topic_by_id(KYS).get("video_title") or "Kyshtym"
    pool = _j(d / "00_pool_v3.json")
    sis, usr = fc.system(), fc.prompt(pool, titulo)
    (LAB / "prompt_kyshtym_f23_ficha.txt").write_text(
        f"===== SISTEMA (md5 {_md5(sis)}) =====\n{sis}\n\n===== USUARIO (md5 {_md5(usr)}) =====\n{usr}\n", encoding="utf-8")
    call = llm_call("ficha", "gpt-6.1-sol")
    cost_tracker.start_video(f"{KYS}-f23-ficha")
    t0 = time.time()
    try:
        res = fc.run(KYS, steps_dir=STEPS_DIR, title=titulo, tag="kyshtym", out_dirs=[LAB], call=call)
    finally:
        rep = cost_tracker.end_video()
    costo = _add_cost("ficha", rep, t0, {"prompt_md5": {"sistema": _md5(sis), "usuario": _md5(usr)}})
    _write(LAB / "ficha_crudo_kyshtym.json", res["crudo"])
    for p in (d / "ficha_caso.json", LAB / "ficha_caso.json"):
        f = _j(p)
        f["costo"] = costo
        f["chequeo_version"] = "f15b (afloje de cifras y sentidos)"
        _write(p, f)
    (LAB / "ficha_caso.json").replace(LAB / "ficha_kyshtym_f23.json")
    m = res["meta"]
    print(f"[ficha] crudo {m['conteos_crudo']}\n[ficha] final {m['conteos']} · sacados {m['sacados']}", flush=True)


def _topic() -> dict:
    """Como f22_corridas._topic (topics_db solo lectura + perfil cargado) pero con el pool NUEVO de F23."""
    import copy
    import fase1_5 as f15
    topic = copy.deepcopy(f15._load_topic_by_id(KYS))
    topic["evidence_pool"] = _j(STEPS / KYS / "00_pool_v3.json")
    if not (topic["evidence_pool"] or {}).get("_tiempo"):
        raise Parada("el 00_pool_v3.json de Kyshtym no es el de F23 (sin _tiempo)")
    topic.update(escaleta_notas=None, escaleta_solo_apoyo=None, guion_version=4)
    if not f15.cargar_perfil(KYS):
        raise Parada("kyshtym: sin _perfil.json")
    return topic


def _ficha() -> dict:
    from researcher_steps import ficha_caso as fc
    f = fc.load(KYS)
    if not f or f.get("prompt_version") != "f23-1":
        raise Parada("la ficha de Kyshtym en _steps no es la de F23")
    return f


def etapa_escaleta() -> None:
    from cost_tracker import cost_tracker
    from script_engine import m01a_escaleta as ma
    out = LAB / "escaleta_kyshtym_f23.json"
    if out.exists():
        print("[escaleta] ya existe: se saltea", flush=True)
        return
    ficha, topic = _ficha(), _topic()
    pool = topic["evidence_pool"]
    p1 = ma.build_prompt_v2(topic, pool, ficha)
    (LAB / "prompt_kyshtym_f23_escaleta.txt").write_text(
        f"===== SISTEMA (md5 {_md5(ma.SYSTEM_V2)}) =====\n{ma.SYSTEM_V2}\n\n===== USUARIO, intento 1 (md5 {_md5(p1)}) "
        f"=====\n{p1}\n", encoding="utf-8")
    log: list[str] = []
    crudos: list = []
    base = llm_call("escaleta", "gpt-6.1-sol")

    def call(*a, **k):
        r = base(*a, **k)
        crudos.append(r)
        return r
    cost_tracker.start_video(f"{KYS}-f23-escaleta")
    t0 = time.time()
    err, esc = None, None
    try:
        esc = ma.generate_escaleta(topic, call=call, log=log, persist=False, ficha=ficha, columna=None)
    except Exception as e:  # noqa: BLE001
        err = f"{type(e).__name__}: {e}"
    finally:
        rep = cost_tracker.end_video()
    _write(LAB / "escaleta_crudos_kyshtym_f23.json", crudos)
    _add_cost("escaleta", rep, t0, {"error": err, "log": log, "prompt_md5_intento1": {"sistema": _md5(ma.SYSTEM_V2),
                                                                                      "usuario": _md5(p1)}})
    print("\n".join(log), flush=True)
    if esc is None:
        raise Parada(f"escaleta: {err}")
    _write(out, esc)
    (LAB / "ESCALETA_kyshtym.md").write_text(ma.to_markdown(esc, pool), encoding="utf-8")
    print(f"[escaleta] {len(esc['beats'])} beats · {esc.get('prompt_version')} · intents "
          f"{[c.get('narrative_intent') for c in esc.get('caps') or []]}", flush=True)


def etapa_guion() -> None:
    from cost_tracker import cost_tracker
    from f13_corridas import PALABRAS_POR_SEG, repeticion_interna
    import f22b_corridas
    from f22b_corridas import narracion as narracion_md
    f22b_corridas.VERSION_NOMBRE.setdefault("f23-1", "v5.3")
    from script_engine import guion_v4 as g4
    from script_engine import m01b_guionista as mg
    out = LAB / "guion_kyshtym_f23.json"
    if out.exists():
        print("[guion] ya existe: se saltea", flush=True)
        return
    esc = _j(LAB / "escaleta_kyshtym_f23.json")
    if not esc:
        raise Parada("guion: falta la escaleta de F23")
    ficha, topic = _ficha(), _topic()
    modelo, version = g4.DEFAULT_MODELO_GUION, g4.PROMPT_VERSION
    sis, usr = g4.system(version), g4.prompt(topic, esc, ficha=ficha, version=version)
    (LAB / "prompt_kyshtym_f23_guion.txt").write_text(
        f"===== SISTEMA (md5 {_md5(sis)}) =====\n{sis}\n\n===== USUARIO (md5 {_md5(usr)}) =====\n{usr}\n", encoding="utf-8")
    res: dict = {"tema": "kyshtym", "modelo": modelo, "esfuerzo": g4.ESFUERZO.get(modelo), "version": version,
                 "max_tokens": MAX_OUT["guion"], "prompt_md5": {"sistema": _md5(sis), "usuario": _md5(usr)},
                 "nota_b": g4.nota_b()}
    cost_tracker.start_video(f"{KYS}-f23-guion")
    t0 = time.time()
    try:
        g = g4.write(topic, esc, call=llm_call("guion", modelo), ficha=ficha, version=version)
        res.update(prompt_version=g["prompt_version"], parrafos=g["parrafos"])
        res["bloqueantes"] = g4.bloqueantes(topic, esc, g["parrafos"], ficha=ficha, version=version)
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
    _write(out, res)
    if res.get("parrafos"):
        (LAB / "NARRACION_kyshtym_f23.md").write_text(
            narracion_md("K", esc, res, ficha, topic, modelo=modelo, version=version, tema="Kyshtym", fase="F23",
                         escaleta_txt="Escaleta v2.1/f22-2 sin columna (Sol, F23), ficha v2.2"), encoding="utf-8")
    m = res.get("metricas") or {}
    print("[guion] " + (f"ERROR {res['error']} · " if res.get("error") else "")
          + (f"{m['palabras']} palabras ≈ {res['minutos']} min · bloqueantes {len(res['bloqueantes'])} · citas "
             f"{m['citas']} · fechas por cap {m.get('fechas_literales_por_cap')}" if m else ""), flush=True)
    if res.get("error"):
        raise Parada(res["error"])


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    etapas = {"perfiles": etapa_perfiles, "research": etapa_research, "ficha": etapa_ficha,
              "escaleta": etapa_escaleta, "guion": etapa_guion}
    for e in [a for a in sys.argv[1:] if a in etapas] or list(etapas):
        try:
            etapas[e]()
        except Parada as x:
            print(f"PARADA ({e}): {x}", flush=True)
            break
    print(f"tanda US$ {_gastado():.4f}", flush=True)


if __name__ == "__main__":
    main()
