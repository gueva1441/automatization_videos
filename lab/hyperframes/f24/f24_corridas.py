"""F24 — B.3 (prueba de modelo en la escaleta, Kyshtym) y C (Pennhurst y Vajont de la semilla al guion, sin tocar código).

    modelo    B.3: ficha de Kyshtym de F23 → escaleta f24-1 con Fable ×2 (F1, F2) y Sol ×2 (S1, S2), en el orden F1, S1,
              S2, F2 → guion v5.3 con Fable de cada una, mientras entre en el tope de B.3 (US$ 2.00). Salidas en
              `lab/hyperframes/f24/b3/`.
    C, por tema (`pennhurst`, `vajont`), por el camino normal:
      research  `run_seed` (perfil nuevo → R1 unido con el registro → R2 → R3 → R4/R5 → compuerta); rojo → PARADA del tema.
      ficha     ficha v2.2 (Sol high).
      escaleta  escaleta f24-1 sin columna con el modelo que decidió B.3 (`modelo_escaleta_f24.json`; sin decisión, Sol).
      guion     guion v5.3 (Fable high) → `reparar` (la ronda única de siempre, con el mismo modelo).
      particion `m01d_particion.particionar` (títulos y recorte con Sol), en `_steps/<topic>/`.
Topes: B.3 2.00; por tema research 3.50 · ficha 0.60 · escaleta 0.40 · guion 1.20 (guion + reparación) · partición 0.20;
total de la tanda 14.00 (`costos_f24.json`; por tema, `<tema>/costos.json`). Freno antes de cada llamada (lo gastado + el
peor caso con la salida acotada) y una sola facturación por llamada; en el research, el freno de F20 sobre Gemini. Un paso
que falla por red o timeout se reintenta UNA vez; cualquier otro error = PARADA de ese tema (el otro sigue).
Uso: python -I lab/hyperframes/f24/f24_corridas.py modelo | pennhurst [research ficha escaleta guion particion] | vajont …
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
sys.path[:0] = [str(LAB), str(ROOT), str(LAB.parent / "f13"), str(LAB.parent / "f22"), str(LAB.parent / "f22b")]
STEPS = ROOT / "data" / "scripts" / "_steps"
KYS = "f18-kyshtym-mayak"
COSTOS = LAB / "costos_f24.json"
TOPE_TOTAL = 14.00
TOPES = {"modelo": 2.00, "research": 3.50, "ficha": 0.60, "escaleta": 0.40, "guion": 1.20, "particion": 0.20}
MAX_OUT = {("gpt-6.1-sol", "ficha"): 50000, ("gpt-6.1-sol", "escaleta"): 16000, ("claude-fable-5-1", "escaleta"): 16000,
           ("claude-fable-5-1", "guion"): 21000, ("claude-fable-5-1", "reparacion"): 8000,
           ("gpt-6.1-sol", "particion"): 4000}
MARGEN_GEMINI = 0.05
TEMAS = {"pennhurst": {"tid": "4ac37187-pennhurst", "seed_id": "4ac37187-ebbc-4a20-8051-1e23e7c607c2"},
         "vajont": {"tid": "f8s3-vajont", "seed_id": "f8s3-vajont"}}
RED = ("Timeout", "timeout", "Connection", "connection", "RemoteDisconnected", "502", "503", "504", "temporarily")


class Parada(RuntimeError):
    pass


def _md5(s: str) -> str:
    return hashlib.md5(s.encode("utf-8")).hexdigest()


def _write(p: Path, obj) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=1, default=str), encoding="utf-8")


def _j(p: Path):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def _costos() -> dict:
    return _j(COSTOS) or {"etapas": [], "usd_total": 0.0}


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
    if tema in TEMAS:
        _write(LAB / tema / "costos.json", {"etapas": [x for x in c["etapas"] if x["tema"] == tema],
                                            "usd_total": round(_gastado(tema), 4)})
    print(f"  [{tema} {etapa}] US$ {costo['usd']:.4f} · {costo['segundos']:.0f} s · tanda US$ {c['usd_total']:.4f}",
          flush=True)
    return costo


def _freno(tema: str, etapa: str, cur: float, worst: float, desc: str) -> None:
    tope_etapa = "guion" if etapa == "reparacion" else etapa
    paso = (_gastado(tema, tope_etapa) + (_gastado(tema, "reparacion") if tope_etapa == "guion" else 0)) + cur
    if tema == "modelo":
        paso = _gastado("modelo") + cur
        tope_etapa = "modelo"
    total = _gastado() + cur
    if paso + worst > TOPES[tope_etapa] or total + worst > TOPE_TOTAL:
        raise Parada(f"tope antes de «{desc}»: paso US$ {paso:.3f} + peor caso {worst:.3f} > {TOPES[tope_etapa]:.2f} "
                     f"(o total {total + worst:.3f} > {TOPE_TOTAL:.2f})")


def llm_call(tema: str, etapa: str, modelo: str):
    """Sol o Claude, effort high, salida acotada; freno y una sola facturación por llamada."""
    from cost_tracker import cost_tracker
    if modelo.startswith("claude"):
        import claude_helpers as hx
    else:
        import gpt_helpers as hx
    hx.TIMEOUT_S = 2400
    pin, pout = hx.PRICES[modelo]
    max_out = MAX_OUT[(modelo, etapa)]

    def _call(prompt, system_instruction=None, response_schema=None, thinking_budget=None, description=None):
        cur = cost_tracker.current_video.total_cost if cost_tracker.current_video else 0.0
        worst = (len(prompt) + len(system_instruction or "")) / 3 / 1e6 * pin + max_out / 1e6 * pout
        _freno(tema, etapa, cur, worst, str(description))
        n = {"posts": 0}

        def post(body: dict) -> dict:
            if n["posts"]:
                raise Parada("la llamada ya facturó una vez (JSON roto o cortado): no hay reintento por el tope")
            body["max_tokens" if modelo.startswith("claude") else "max_completion_tokens"] = max_out
            n["posts"] += 1
            return hx._post(body)
        return hx.make_call(modelo, "high", post=post)(prompt, system_instruction=system_instruction,
                                                       response_schema=response_schema, description=description)
    return _call


def _frenos_gemini(tema: str, etapa: str):
    import gemini_helpers
    from cost_tracker import cost_tracker
    from researcher_steps import research_v3 as r3
    orig = {(gemini_helpers, "call_pro_json"): gemini_helpers.call_pro_json,
            (gemini_helpers, "call_flash_json"): gemini_helpers.call_flash_json,
            (r3, "search_pro"): r3.search_pro, (r3, "search_flash"): r3.search_flash}

    def wrap(fn, name):
        def _f(*a, **k):
            cur = cost_tracker.current_video.total_cost if cost_tracker.current_video else 0.0
            _freno(tema, etapa, cur, MARGEN_GEMINI, name)
            return fn(*a, **k)
        return _f
    for (mod, name), fn in orig.items():
        setattr(mod, name, wrap(fn, name))

    def undo():
        for (mod, name), fn in orig.items():
            setattr(mod, name, fn)
    return undo


def _es_red(err: str) -> bool:
    return any(x in err for x in RED)


def _estado(tema: str, paso: str, estado: str, motivo: str = "") -> None:
    p = LAB / tema / "estado.json"
    e = _j(p) or {}
    e[paso] = {"estado": estado, "motivo": motivo}
    _write(p, e)


def _topic(tid: str, titulo: str) -> dict:
    """El topic en memoria (topics_db no se toca): título = el de la semilla, el pool de `_steps` y el perfil cargado."""
    import fase1_5 as f15
    pool = _j(STEPS / tid / "00_pool_v3.json")
    if not pool:
        raise Parada(f"{tid}: sin 00_pool_v3.json")
    if not f15.cargar_perfil(tid):
        raise Parada(f"{tid}: sin _perfil.json")
    return {"id": tid, "topic_id": tid, "video_title": titulo, "evidence_pool": pool, "escaleta_notas": None,
            "escaleta_solo_apoyo": None, "guion_version": 4}


def _seed(tema: str) -> dict:
    s = json.loads((ROOT / "data" / "selected_seeds.json").read_text(encoding="utf-8"))["seeds"]
    return next(x for x in s if x.get("seed_id") == TEMAS[tema]["seed_id"])


# ═══════════════════════════════════════════════════════════════
#  métricas de la escaleta y del guion (para B.3 y C)
# ═══════════════════════════════════════════════════════════════

def esc_metricas(esc: dict, crudo1: dict | None, pool: dict, ficha: dict) -> dict:
    from script_engine import m01a_escaleta as me
    caps = [b["cap"] for b in esc["beats"]]
    ids = {i for b in esc["beats"] for i in [b["dato_central"]] + list(b.get("datos_apoyo") or [])}
    m = {"beats": len(caps), "beats_por_cap": [caps.count(n) for n in range(1, 8)], "ids": len(ids),
         "apoyos_por_beat": round(sum(len(b.get("datos_apoyo") or []) for b in esc["beats"]) / max(1, len(caps)), 2),
         "promesa": esc.get("promesa_gancho"), "humano": (esc.get("humano") or {}).get("nombre"),
         "antagonista": esc.get("antagonista"), "intentos": [{"intento": x.get("intento"),
                                                              "bloqueantes": x.get("bloqueantes")}
                                                             for x in esc.get("_intentos") or []]}
    if crudo1:
        c1 = [int(b.get("cap") or 0) for b in crudo1.get("beats") or []]
        m["pasada1_beats_por_cap"] = [c1.count(n) for n in range(1, 8)]
        m["pasada1_caps_fuera_1_3"] = [n for n in range(1, 8) if not 1 <= c1.count(n) <= 3]
        m["pasada1_bloqueantes"] = me.bloqueantes(crudo1, pool, ficha)[1]
    return m


def guion_metricas(topic: dict, esc: dict, parrafos: list[dict], ficha: dict) -> dict:
    from f13_corridas import PALABRAS_POR_SEG
    from f22_compara import personas_por_cap
    from script_engine import guion_v4 as g4
    from script_engine import m01b_guionista as mg
    from script_engine.guion_v3_reglas import fechas_literales_por_cap, quotes_in
    caps = mg.caps_text(esc, parrafos)
    m = g4.metricas(topic, esc, parrafos)
    pc = personas_por_cap(caps, ficha)
    return {"palabras": m["palabras"], "minutos": round(m["palabras"] / PALABRAS_POR_SEG / 60, 1),
            "citas": m["citas"], "duras_v3": len(m.get("duras_v3") or []),
            "palabras_por_cap": {c["chapter_number"]: len(c["narration"].split()) for c in caps},
            "personas_por_cap": pc, "citas_por_cap": {c["chapter_number"]: sum(
                len(quotes_in(p["texto"])) for p in parrafos if p.get("cap") == c["chapter_number"]) for c in caps},
            "fechas_literales_por_cap": fechas_literales_por_cap(caps)}


# ═══════════════════════════════════════════════════════════════
#  B.3 — modelo de la escaleta
# ═══════════════════════════════════════════════════════════════

B3 = LAB / "b3"
# orden: Fable primero (su peor caso es el que no entra al final del tope), después Sol
B3_TAGS = (("F1", "claude-fable-5-1"), ("S1", "gpt-6.1-sol"), ("S2", "gpt-6.1-sol"), ("F2", "claude-fable-5-1"))


def _kys():
    sys.path.insert(0, str(LAB.parent / "f23"))
    import f23_corridas as f23
    return f23._ficha(), f23._topic()


def b3_escaleta(tag: str, modelo: str) -> dict | None:
    from cost_tracker import cost_tracker
    from script_engine import m01a_escaleta as ma
    out = B3 / f"escaleta_{tag}.json"
    if out.exists() or (B3 / f"escaleta_{tag}_rechazada.json").exists():
        return _j(out)
    ficha, topic = _kys()
    pool = topic["evidence_pool"]
    p1 = ma.build_prompt_v2(topic, pool, ficha)
    (B3 / f"prompt_escaleta_{tag}.txt").parent.mkdir(parents=True, exist_ok=True)
    (B3 / f"prompt_escaleta_{tag}.txt").write_text(
        f"===== SISTEMA (md5 {_md5(ma.SYSTEM_V2)}) =====\n{ma.SYSTEM_V2}\n\n===== USUARIO, intento 1 (md5 {_md5(p1)}) "
        f"=====\n{p1}\n", encoding="utf-8")
    crudos: list = []
    base = llm_call("modelo", "escaleta", modelo)

    def call(*a, **k):
        r = base(*a, **k)
        crudos.append(r)
        return r
    log: list[str] = []
    cost_tracker.start_video(f"{KYS}-f24-b3-{tag}-escaleta")
    t0 = time.time()
    err, esc = None, None
    try:
        esc = ma.generate_escaleta(topic, call=call, log=log, persist=False, ficha=ficha, columna=None)
    except Exception as e:  # noqa: BLE001
        err = f"{type(e).__name__}: {e}"
    finally:
        rep = cost_tracker.end_video()
    _write(B3 / f"escaleta_crudos_{tag}.json", crudos)
    _add_cost("modelo", f"escaleta {tag}", rep, t0, {"modelo": modelo, "error": err, "log": log})
    print("\n".join(log), flush=True)
    if esc is None:
        _write(B3 / f"escaleta_{tag}_rechazada.json", {"error": err, "log": log,
                                                       "metricas": esc_metricas({"beats": []}, crudos[0] if crudos else None,
                                                                                pool, ficha) if crudos else None})
        if err and "tope antes de" in err:            # el freno: lo que sigue tampoco entra
            raise Parada(err)
        return None
    esc["_modelo"] = modelo
    _write(out, esc)
    (B3 / f"ESCALETA_{tag}.md").write_text(ma.to_markdown(esc, pool), encoding="utf-8")
    return esc


def b3_guion(tag: str, esc: dict) -> None:
    from cost_tracker import cost_tracker
    from script_engine import guion_v4 as g4
    out = B3 / f"guion_{tag}.json"
    if out.exists():
        return
    ficha, topic = _kys()
    cost_tracker.start_video(f"{KYS}-f24-b3-{tag}-guion")
    t0 = time.time()
    res: dict = {"tag": tag, "modelo_escaleta": esc.get("_modelo"), "modelo": g4.DEFAULT_MODELO_GUION}
    try:
        g = g4.write(topic, esc, call=llm_call("modelo", "guion", g4.DEFAULT_MODELO_GUION), ficha=ficha)
        res["parrafos"] = g["parrafos"]
        res["bloqueantes"] = g4.bloqueantes(topic, esc, g["parrafos"], ficha=ficha)
        res["metricas"] = guion_metricas(topic, esc, g["parrafos"], ficha)
    except Exception as e:  # noqa: BLE001
        res["error"] = f"{type(e).__name__}: {e}"
    finally:
        rep = cost_tracker.end_video()
    res["costo"] = _add_cost("modelo", f"guion {tag}", rep, t0)
    if res.get("parrafos") or "tope antes de" not in str(res.get("error")):
        _write(out, res)
    if res.get("error"):
        raise Parada(res["error"])


def etapa_modelo() -> None:
    from script_engine import m01a_escaleta as ma
    escs = {}
    for tag, modelo in B3_TAGS:
        try:
            escs[tag] = b3_escaleta(tag, modelo)
        except Parada as e:
            print(f"PARADA (B.3 escaleta {tag}): {e}", flush=True)
            break
    for tag, _ in B3_TAGS:
        if escs.get(tag):
            try:
                b3_guion(tag, escs[tag])
            except Parada as e:
                print(f"PARADA (B.3 guion {tag}): {e}", flush=True)
                break
    ficha, topic = _kys()
    pool = topic["evidence_pool"]
    filas = {}
    for tag, modelo in B3_TAGS:
        esc, crudos = _j(B3 / f"escaleta_{tag}.json"), _j(B3 / f"escaleta_crudos_{tag}.json") or []
        rech = _j(B3 / f"escaleta_{tag}_rechazada.json")
        if not esc and not rech:
            filas[tag] = {"modelo": modelo, "corrio": False}
            continue
        fila = {"modelo": modelo, "corrio": True, "rechazada": bool(rech),
                "escaleta": esc_metricas(esc, crudos[0] if crudos else None, pool, ficha) if esc else
                (rech or {}).get("metricas")}
        g = _j(B3 / f"guion_{tag}.json")
        if g:
            fila["guion"] = {"bloqueantes": len(g.get("bloqueantes") or []), **(g.get("metricas") or {}),
                             "error": g.get("error")}
        filas[tag] = fila
    _write(B3 / "tabla_b3.json", filas)
    print(json.dumps({k: {"pasada1": (v.get("escaleta") or {}).get("pasada1_beats_por_cap"),
                          "final": (v.get("escaleta") or {}).get("beats_por_cap")} for k, v in filas.items()},
                     ensure_ascii=False), flush=True)
    print(f"B.3 US$ {_gastado('modelo'):.4f} · prompt escaleta {ma.PROMPT_VERSION_V2} {_md5(ma.SYSTEM_V2)}", flush=True)


# ═══════════════════════════════════════════════════════════════
#  C — un tema de la semilla al guion
# ═══════════════════════════════════════════════════════════════

def _paso(tema: str, paso: str, fn) -> None:
    """Corre un paso; red/timeout → UN reintento; otro error → Parada del tema."""
    for intento in (1, 2):
        try:
            fn()
            if intento == 2:
                _estado(tema, paso, "reintento", "falló una vez por red/timeout")
            elif (_j(LAB / tema / "estado.json") or {}).get(paso, {}).get("estado") != "reintento":
                _estado(tema, paso, "solo")
            return
        except Parada:
            raise
        except Exception as e:  # noqa: BLE001
            err = f"{type(e).__name__}: {e}"
            (LAB / tema / f"error_{paso}.txt").write_text(traceback.format_exc(), encoding="utf-8")
            if intento == 1 and _es_red(err):
                print(f"  [{tema} {paso}] falló por red/timeout ({err[:120]}): un reintento", flush=True)
                continue
            _estado(tema, paso, "paró", err[:400])
            raise Parada(f"{paso}: {err}") from e


def c_research(tema: str) -> None:
    from cost_tracker import cost_tracker
    from researcher_steps import pool_gate as pg
    from researcher_steps import research_v3 as r3
    tid = TEMAS[tema]["tid"]
    d, out = STEPS / tid, LAB / tema
    if (out / "research.json").exists():
        print(f"[{tema} research] ya existe: se saltea", flush=True)
        return
    d.mkdir(parents=True, exist_ok=True)
    out.mkdir(parents=True, exist_ok=True)
    if (d / "_perfil.json").exists() and not (d / "_perfil_pre_f24.json").exists():   # el perfil sale de nuevo
        shutil.move(str(d / "_perfil.json"), str(d / "_perfil_pre_f24.json"))
    if (d / "00_pool_v3.json").exists() and not (d / "00_pool_v3_pre_f24.json").exists():
        shutil.copy2(d / "00_pool_v3.json", d / "00_pool_v3_pre_f24.json")
    if (d / "POOL_GATE.md").exists() and not (d / "POOL_GATE_pre_f24.md").exists():
        shutil.move(str(d / "POOL_GATE.md"), str(d / "POOL_GATE_pre_f24.md"))
    seed = _seed(tema)
    log: list[str] = []
    t0 = time.time()
    undo = _frenos_gemini(tema, "research")
    cost_tracker.start_video(f"{tid}-f24-research")
    err, gate, pool = None, None, None
    try:
        pool, _, gate = r3.run_seed(seed, tid, d, log=log)
    except pg.PoolGateRed as e:
        gate, err = e.gate, "compuerta ROJA: " + "; ".join(e.gate["motivos"])
        pool = _j(d / "00_pool_v3.json")
    except Parada:
        raise
    except Exception as e:  # noqa: BLE001
        err = f"{type(e).__name__}: {e}"
        log.append(traceback.format_exc())
    finally:
        rep = cost_tracker.end_video()
        undo()
        (out / "research_detalle.log").write_text("\n".join(log), encoding="utf-8")
    _add_cost(tema, "research", rep, t0, {"color": (gate or {}).get("color"), "error": err})
    for src, dst in ((d / "POOL_GATE.md", "POOL_GATE.md"), (d / "fuentes.json", "registro_fuentes.json"),
                     (d / "fuentes_r1.json", "fuentes_r1.json"), (d / "fuentes" / "manifest.json", "manifest.json")):
        if src.exists():
            shutil.copy2(src, out / dst)
    prof = _j(d / "_perfil.json") or {}
    (out / "PERFIL.md").write_text("# Perfil — " + seed["seed_title"] + "\n\n" + "\n".join(
        f"- **{k}**: {prof.get(k)}" for k in ("anio_evento", "anio_inicio", "anio_fin", "tipo_evento", "idioma_local",
                                               "cobertura_ingles", "idiomas_research", "nombres_lugar", "place_re",
                                               "roles_testigo", "roles_antagonista")) + "\n", encoding="utf-8")
    res = {"error": err, "gate": {k: (gate or {}).get(k) for k in ("color", "metricas", "motivos")}}
    if pool:
        res["personajes"] = [{k: p.get(k) for k in ("id", "nombre", "nombre_en_documento", "rol", "testigo",
                                                     "antagonista", "n_citas", "presente_en_evento", "elegible_humano")}
                             for p in pool.get("personajes") or []]
        res["citas"] = {s: sum(1 for q in pool.get("citas") or [] if (q.get("verificacion") or {}).get("estado") == s)
                        for s in ("verificada", "verificada_parcial", "sin_verificar")}
        res["docs"] = [{k: x.get(k) for k in ("id", "url", "idioma", "caracteres")}
                       for x in (pool.get("_research_v3") or {}).get("documentos") or []]
    _write(out / "research.json", res)
    if err and not err.startswith("compuerta"):
        raise RuntimeError(err)
    if err:
        _estado(tema, "compuerta", "paró", err)
        raise Parada(err)
    print(f"[{tema} research] compuerta {gate['color']} {gate['metricas']}", flush=True)


def c_ficha(tema: str) -> None:
    from cost_tracker import cost_tracker
    from researcher_steps import ficha_caso as fc
    tid, out = TEMAS[tema]["tid"], LAB / tema
    if (out / "ficha_crudo.json").exists():
        return
    titulo = _seed(tema)["seed_title"]
    pool = _j(STEPS / tid / "00_pool_v3.json")
    sis, usr = fc.system(), fc.prompt(pool, titulo)
    (out / "prompt_ficha.txt").write_text(f"===== SISTEMA (md5 {_md5(sis)}) =====\n{sis}\n\n===== USUARIO (md5 "
                                          f"{_md5(usr)}) =====\n{usr}\n", encoding="utf-8")
    cost_tracker.start_video(f"{tid}-f24-ficha")
    t0 = time.time()
    try:
        res = fc.run(tid, steps_dir=STEPS, title=titulo, tag=tema, out_dirs=[out],
                     call=llm_call(tema, "ficha", "gpt-6.1-sol"))
    finally:
        rep = cost_tracker.end_video()
    _add_cost(tema, "ficha", rep, t0, {"prompt_md5": {"sistema": _md5(sis), "usuario": _md5(usr)}})
    _write(out / "ficha_crudo.json", res["crudo"])
    if (out / f"FICHA_{tema}.md").exists():
        (out / f"FICHA_{tema}.md").replace(out / "FICHA.md")
    if (out / "ficha_caso.json").exists():
        (out / "ficha_caso.json").replace(out / "ficha.json")
    print(f"[{tema} ficha] {res['meta']['conteos']} · sacados {res['meta']['sacados']}", flush=True)


def _ficha(tid: str) -> dict:
    from researcher_steps import ficha_caso as fc
    f = fc.load(tid)
    if not f or f.get("prompt_version") != "f23-1":
        raise Parada(f"{tid}: la ficha en _steps no es la v2.2")
    return f


def c_escaleta(tema: str) -> None:
    from cost_tracker import cost_tracker
    from script_engine import m01a_escaleta as ma
    tid, out = TEMAS[tema]["tid"], LAB / tema
    if (out / "escaleta.json").exists():
        return
    modelo = (_j(LAB / "modelo_escaleta_f24.json") or {}).get("modelo") or "gpt-6.1-sol"
    ficha, topic = _ficha(tid), _topic(tid, _seed(tema)["seed_title"])
    pool = topic["evidence_pool"]
    p1 = ma.build_prompt_v2(topic, pool, ficha)
    (out / "prompt_escaleta.txt").write_text(f"===== SISTEMA (md5 {_md5(ma.SYSTEM_V2)}) =====\n{ma.SYSTEM_V2}\n\n"
                                             f"===== USUARIO, intento 1 (md5 {_md5(p1)}) =====\n{p1}\n", encoding="utf-8")
    crudos: list = []
    base = llm_call(tema, "escaleta", modelo)

    def call(*a, **k):
        r = base(*a, **k)
        crudos.append(r)
        return r
    log: list[str] = []
    cost_tracker.start_video(f"{tid}-f24-escaleta")
    t0 = time.time()
    try:
        esc = ma.generate_escaleta(topic, call=call, log=log, persist=False, ficha=ficha, columna=None)
    finally:
        rep = cost_tracker.end_video()
        _write(out / "escaleta_crudos.json", crudos)
        _add_cost(tema, "escaleta", rep, t0, {"modelo": modelo, "log": log})
        (out / "escaleta.log").write_text("\n".join(log), encoding="utf-8")
    esc["_modelo"] = modelo
    _write(out / "escaleta.json", esc)
    _write(STEPS / tid / "01a_escaleta.json", esc)
    (out / "ESCALETA.md").write_text(ma.to_markdown(esc, pool), encoding="utf-8")
    _write(out / "escaleta_metricas.json", esc_metricas(esc, crudos[0] if crudos else None, pool, ficha))
    print(f"[{tema} escaleta] {len(esc['beats'])} beats · por cap "
          f"{[sum(1 for b in esc['beats'] if b['cap'] == n) for n in range(1, 8)]}", flush=True)


def c_guion(tema: str) -> None:
    from cost_tracker import cost_tracker
    from script_engine import guion_v4 as g4
    tid, out = TEMAS[tema]["tid"], LAB / tema
    if (out / "guion.json").exists():
        return
    esc = _j(out / "escaleta.json")
    if not esc:
        raise Parada("sin escaleta")
    ficha, topic = _ficha(tid), _topic(tid, _seed(tema)["seed_title"])
    modelo = g4.DEFAULT_MODELO_GUION
    sis, usr = g4.system(), g4.prompt(topic, esc, ficha=ficha)
    (out / "prompt_guion.txt").write_text(f"===== SISTEMA (md5 {_md5(sis)}) =====\n{sis}\n\n===== USUARIO (md5 "
                                          f"{_md5(usr)}) =====\n{usr}\n", encoding="utf-8")
    res: dict = {"modelo": modelo, "version": g4.PROMPT_VERSION, "prompt_md5": {"sistema": _md5(sis), "usuario": _md5(usr)},
                 "nota_b": g4.nota_b()}
    log: list[str] = []
    cost_tracker.start_video(f"{tid}-f24-guion")
    t0 = time.time()
    try:
        g = g4.write(topic, esc, call=llm_call(tema, "guion", modelo), ficha=ficha, log=log)
        res["parrafos_guionista"] = g["parrafos"]
    finally:
        rep = cost_tracker.end_video()
        _add_cost(tema, "guion", rep, t0, {"modelo": modelo})
        _write(out / "guion.json", res)
    cost_tracker.start_video(f"{tid}-f24-reparacion")
    t0 = time.time()
    try:
        r = g4.reparar(topic, esc, g["parrafos"], call=llm_call(tema, "reparacion", modelo), log=log, ficha=ficha)
        res["reparacion"] = {k: r.get(k) for k in ("bloqueantes_antes", "bloqueantes_despues", "parada", "pasos")}
        res["parrafos"] = r["parrafos"]
    except Parada as e:                        # el tope no deja reparar: queda el texto del guionista
        res["reparacion"] = {"error": str(e)}
        res["parrafos"] = g["parrafos"]
    finally:
        rep = cost_tracker.end_video()
        _add_cost(tema, "reparacion", rep, t0)
    res["bloqueantes"] = g4.bloqueantes(topic, esc, res["parrafos"], ficha=ficha)
    res["metricas"] = guion_metricas(topic, esc, res["parrafos"], ficha)
    res["log"] = log
    _write(out / "guion.json", res)
    import f22b_corridas
    f22b_corridas.VERSION_NOMBRE.setdefault("f23-1", "v5.3")
    m = res["metricas"]
    (out / f"NARRACION_{tema}_f24.md").write_text(f22b_corridas.narracion(
        tema[:1].upper(), esc, {**res, "minutos": m["minutos"], "metricas": g4.metricas(topic, esc, res["parrafos"])},
        ficha, topic, modelo=modelo, version=g4.PROMPT_VERSION, tema=tema.capitalize(), fase="F24",
        escaleta_txt=f"Escaleta f24-1 sin columna ({esc.get('_modelo')}), ficha v2.2"), encoding="utf-8")
    print(f"[{tema} guion] {m['palabras']} palabras ≈ {m['minutos']} min · bloqueantes {len(res['bloqueantes'])} · "
          f"citas {m['citas']} · por cap {m['palabras_por_cap']}", flush=True)


def c_particion(tema: str) -> None:
    from cost_tracker import cost_tracker
    from script_engine import m01d_particion as md
    tid, out = TEMAS[tema]["tid"], LAB / tema
    if (out / "particion.json").exists():
        return
    esc, g = _j(out / "escaleta.json"), _j(out / "guion.json")
    if not (esc and g and g.get("parrafos")):
        raise Parada("sin guion")
    topic = _topic(tid, _seed(tema)["seed_title"])
    sol = llm_call(tema, "particion", "gpt-6.1-sol")
    log: list[str] = []
    cost_tracker.start_video(f"{tid}-f24-particion")
    t0 = time.time()
    try:
        part = md.particionar(topic, esc, g["parrafos"], topic["evidence_pool"], log=log, call_titles=sol,
                              shorten=md.editor_shorten(sol))
    finally:
        rep = cost_tracker.end_video()
        _add_cost(tema, "particion", rep, t0, {"log": log})
    _write(out / "particion.json", {"notas": part["notas"], "titulos": [c.get("title") for c in
                                                                         part["narration"]["chapters"]],
                                    "palabras_por_cap": {c["chapter_number"]: len(c["narration"].split())
                                                         for c in part["narration"]["chapters"]}})
    print(f"[{tema} particion] {len(part['notas'])} nota(s)", flush=True)


def etapa_tema(tema: str, pasos: list[str]) -> None:
    fns = {"research": c_research, "ficha": c_ficha, "escaleta": c_escaleta, "guion": c_guion, "particion": c_particion}
    for paso in pasos or list(fns):
        try:
            _paso(tema, paso, lambda: fns[paso](tema))
        except Parada as e:
            if "tope" in str(e):
                _estado(tema, paso, "paró", str(e)[:400])
            print(f"PARADA ({tema} {paso}): {e}", flush=True)
            return


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    args = sys.argv[1:]
    if not args:
        raise SystemExit(__doc__)
    if args[0] == "modelo":
        etapa_modelo()
    else:
        etapa_tema(args[0], args[1:])
    print(f"tanda US$ {_gastado():.4f}", flush=True)


if __name__ == "__main__":
    main()
