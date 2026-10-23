"""F14 §2 — la prueba de Orleans (`ba6c3cac-f7r3`): ficha con criterios → escaleta nueva que lee la ficha → guion v4
abierto con Sol high y los datos de la ficha. Sin notas.

    ficha     researcher_steps.ficha_caso.run (UNA llamada a gpt-6.1-sol high, prompt f14-1) → _steps/<topic>/ficha_caso.json
              + FICHA_orleans.md (también en esta carpeta). El crudo del modelo queda en ficha_crudo_orleans.json.
    escaleta  m01a_escaleta.generate_escaleta(persist=False) — lee la ficha del disco (no el digest), apoyos 0–6, Gemini
              Pro como siempre, hasta 3 intentos → _steps/<topic>/01a_escaleta_f14.json + escaleta_orleans_f14.json/.md.
              La escaleta de F7c-3 (01a_escaleta.json, md5 2f794418…) NO se pisa: se copia a 01a_escaleta_f7c3.json.
    guion     guion_v4.write(largo="abierto", ficha=…) con Sol high, una llamada, sin reparación ni editor →
              guion_orleans_f14.json + NARRACION_orleans_f14.md.

Cada etapa se saltea si su salida ya existe (para reanudar sin gastar dos veces). Prompts guardados con md5.
Tope de la tanda: US$ 1.50 (costos_f14.json). Antes de cada llamada: si lo gastado + el peor caso de esa llamada pasa
el tope, PARADA. Las llamadas a GPT llevan `max_completion_tokens` acotado; una sola llamada que facture por etapa GPT.
Uso: python -I lab/hyperframes/f14/f14_orleans.py [ficha escaleta guion]
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
sys.path.insert(0, str(ROOT))
LAB = Path(__file__).resolve().parent
sys.path.insert(1, str(LAB.parent / "f13"))                 # repeticion_interna (solo medir)
TOPE_USD = 1.50
TID = "ba6c3cac-f7r3"
POOL_MD5 = "e90d6ca9869077fd2759766817588741"
ESC_F7C3_MD5 = "2f79441804f158aa23f8af5ca03391d1"
COSTOS = LAB / "costos_f14.json"
PRO_PEOR_USD = 0.30                    # peor caso por intento de escaleta con Pro (entrada + salida + thinking)
RESERVA_USD = 0.45                     # lo que la ficha deja libre para la escaleta (≥ 1 intento) y el guion


class Parada(RuntimeError):
    pass


def _md5b(b: bytes) -> str:
    return hashlib.md5(b).hexdigest()


def _md5(s: str) -> str:
    return _md5b(s.encode("utf-8"))


def _write(p: Path, obj) -> None:
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding="utf-8")


def _costos() -> dict:
    return json.loads(COSTOS.read_text(encoding="utf-8")) if COSTOS.exists() else {"etapas": [], "usd_total": 0.0}


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


def _topic() -> dict:
    import fase1_5 as f15
    raw = (_steps() / "00_pool_v3.json").read_bytes()
    if _md5b(raw) != POOL_MD5:
        raise SystemExit("00_pool_v3.json no es el fijado: PARADA")
    topic = dict(f15._load_topic_by_id(TID))               # solo lectura: no se escribe topics_db
    topic["escaleta_notas"] = None                          # sin notas
    topic["escaleta_solo_apoyo"] = None
    return topic


def gpt_call(max_out: int):
    """Sol high con `max_completion_tokens` = max_out y una sola llamada que facture."""
    import gpt_helpers
    n = {"posts": 0}

    def post(body: dict) -> dict:
        if n["posts"]:
            raise Parada("la llamada ya facturó una vez (JSON roto o cortado): no hay reintento por el tope")
        body["max_completion_tokens"] = max_out
        n["posts"] += 1
        return gpt_helpers._post(body)
    return gpt_helpers.make_call("gpt-6.1-sol", "high", post=post)


def _max_out(chars_in: int) -> int:
    import gpt_helpers
    pin, pout = gpt_helpers.PRICES["gpt-6.1-sol"]
    spent = _costos()["usd_total"]
    in_usd = chars_in / 3 / 1e6 * pin                       # cota por arriba (≈ 3.3–3.6 caracteres por token)
    return int((TOPE_USD - spent - in_usd) / pout * 1e6) - 500


# ═══════════════════════════════════════════════════════════════

def etapa_ficha() -> None:
    from cost_tracker import cost_tracker
    from researcher_steps import ficha_caso as fc
    from script_engine.m01a_skeleton import STEPS_DIR
    if (LAB / "ficha_crudo_orleans.json").exists():
        print("[ficha] ya existe: se saltea", flush=True)
        return
    topic = _topic()
    titulo = f"{topic.get('video_title')} (Nueva Orleans, huracán Katrina, agosto–septiembre de 2005)"
    sis, usr = fc.system(), fc.prompt(json.loads((_steps() / "00_pool_v3.json").read_text("utf-8")), titulo)
    (LAB / "prompt_orleans_f14_ficha.txt").write_text(
        f"===== SISTEMA (md5 {_md5(sis)}) =====\n{sis}\n\n===== USUARIO (md5 {_md5(usr)}) =====\n{usr}\n", encoding="utf-8")
    max_out = min(60000, _max_out(len(sis) + len(usr)) - int(RESERVA_USD / 10 * 1e6))
    print(f"[ficha] prompt {len(sis) + len(usr):,} car · max_completion_tokens {max_out:,}", flush=True)
    if max_out < 30000:
        raise Parada(f"no alcanza el tope para la ficha (max_out {max_out})")
    import gpt_helpers
    gpt_helpers.TIMEOUT_S = 2400
    cost_tracker.start_video(f"{TID}-f14-ficha")
    t0 = time.time()
    try:
        res = fc.run(TID, steps_dir=STEPS_DIR, title=titulo, tag="orleans", out_dirs=[LAB], call=gpt_call(max_out))
    finally:
        rep = cost_tracker.end_video()
    costo = _add_cost("ficha", rep, t0, {"max_completion_tokens": max_out,
                                         "prompt_md5": {"sistema": _md5(sis), "usuario": _md5(usr)}})
    _write(LAB / "ficha_crudo_orleans.json", res["crudo"])
    for d in (_steps(), LAB):                                # el costo dentro de la ficha
        p = d / "ficha_caso.json"
        f = json.loads(p.read_text(encoding="utf-8"))
        f["costo"] = costo
        _write(p, f)
    m = res["meta"]
    print(f"[ficha] crudo {m['conteos_crudo']}\n[ficha] final {m['conteos']} · sacados {m['sacados']}", flush=True)
    for s in res["sacados"]:
        print(f"  sacado [{s['seccion']}] {s['que'][:90]} → {s['motivo'][:150]}", flush=True)


def etapa_escaleta() -> None:
    import gemini_helpers
    from cost_tracker import cost_tracker
    from researcher_steps import ficha_caso as fc
    from script_engine import m01a_escaleta as ma
    out = _steps() / "01a_escaleta_f14.json"
    if out.exists():
        print("[escaleta] ya existe: se saltea", flush=True)
        return
    f7 = _steps() / "01a_escaleta.json"
    if _md5b(f7.read_bytes()) != ESC_F7C3_MD5:
        raise SystemExit("01a_escaleta.json no es la de F7c-3: PARADA (no se toca)")
    bak = _steps() / "01a_escaleta_f7c3.json"
    if not bak.exists():
        shutil.copy2(f7, bak)
    ficha = fc.load(TID)
    if not ficha or ficha.get("prompt_version") != fc.PROMPT_VERSION:
        raise SystemExit("falta la ficha f14 de Orleans: correr la etapa ficha")
    topic = _topic()
    pool = topic["evidence_pool"]
    p1 = ma.build_prompt(topic, pool, None, ficha)
    (LAB / "prompt_orleans_f14_escaleta.txt").write_text(
        f"===== SISTEMA (md5 {_md5(ma.SYSTEM)}) =====\n{ma.SYSTEM}\n\n===== USUARIO, intento 1 (md5 {_md5(p1)}) =====\n"
        f"{p1}\n", encoding="utf-8")
    spent0 = _costos()["usd_total"]

    def call(prompt, **kw):
        now = spent0 + (cost_tracker.current_video.total_cost if cost_tracker.current_video else 0.0)
        if now + PRO_PEOR_USD > TOPE_USD:
            raise Parada(f"tope de costo: US$ {now:.3f} + peor caso de otro intento > {TOPE_USD:.2f}")
        return gemini_helpers.call_pro_json(prompt, **kw)
    log: list[str] = []
    cost_tracker.start_video(f"{TID}-f14-escaleta")
    t0 = time.time()
    err = None
    try:
        esc = ma.generate_escaleta(topic, call=call, log=log, persist=False, ficha=ficha)
    except Exception as e:  # noqa: BLE001
        esc, err = None, f"{type(e).__name__}: {e}"
    finally:
        rep = cost_tracker.end_video()
    _add_cost("escaleta", rep, t0, {"prompt_md5_intento1": _md5(p1), "error": err})
    print("\n".join(log), flush=True)
    if esc is None:
        raise Parada(f"escaleta: {err}")
    _write(out, esc)
    _write(LAB / "escaleta_orleans_f14.json", esc)
    (LAB / "ESCALETA_orleans_f14.md").write_text(ma.to_markdown(esc, pool), encoding="utf-8")
    print(f"[escaleta] {len(esc['beats'])} beats · humano {esc['humano'].get('nombre')} · pico beat "
          f"{esc['pico'].get('beat')}", flush=True)


def etapa_guion() -> None:
    from cost_tracker import cost_tracker
    from f13_corridas import PALABRAS_POR_SEG, repeticion_interna
    from researcher_steps import ficha_caso as fc
    from script_engine import guion_v4 as g4
    from script_engine import m01b_guionista as mg
    if (LAB / "guion_orleans_f14.json").exists():
        print("[guion] ya existe: se saltea", flush=True)
        return
    esc = json.loads((_steps() / "01a_escaleta_f14.json").read_text(encoding="utf-8"))
    ficha = fc.load(TID)
    topic = _topic()
    topic["guion_version"] = 4
    sis, usr = g4.system(), g4.prompt(topic, esc, "abierto", ficha)
    (LAB / "prompt_orleans_f14_guion.txt").write_text(
        f"===== SISTEMA (md5 {_md5(sis)}) =====\n{sis}\n\n===== USUARIO (md5 {_md5(usr)}) =====\n{usr}\n", encoding="utf-8")
    max_out = min(32000, _max_out(len(sis) + len(usr)))
    if max_out < 8000:
        raise Parada(f"no alcanza el tope para el guion (max_out {max_out})")
    import gpt_helpers
    gpt_helpers.TIMEOUT_S = 1200
    res: dict = {"tema": "orleans", "tid": TID, "corrida": "f14", "modelo": "gpt-6.1-sol", "esfuerzo": "high",
                 "escaleta": "01a_escaleta_f14.json", "notas": None, "largo": "abierto", "max_completion_tokens": max_out,
                 "prompt_md5": {"sistema": _md5(sis), "usuario": _md5(usr)}}
    cost_tracker.start_video(f"{TID}-f14-guion")
    t0 = time.time()
    try:
        g = g4.write(topic, esc, call=gpt_call(max_out), largo="abierto", ficha=ficha)
        res.update(prompt_version=g["prompt_version"], ficha=g.get("ficha"), parrafos=g["parrafos"])
        res["bloqueantes"] = g4.bloqueantes(topic, esc, g["parrafos"], largo="abierto")
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
    _write(LAB / "guion_orleans_f14.json", res)
    if res.get("parrafos"):
        from f13_corridas import narracion_md
        md = narracion_md("orleans", "orl", esc, res).replace("corrida _f13_orl_abierto, F13", "corrida f14, F14 (ficha)")
        (LAB / "NARRACION_orleans_f14.md").write_text(md, encoding="utf-8")
    m = res.get("metricas") or {}
    print(f"[guion] " + (f"ERROR {res['error']} · " if res.get("error") else "")
          + (f"{m['palabras']} palabras ≈ {res['minutos']} min · bloqueantes {len(res['bloqueantes'])} · por cap "
             f"{[v[0] for v in m['palabras_por_cap'].values()]}" if m else ""), flush=True)
    if res.get("error"):
        raise Parada(res["error"])


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")                # -I ignora PYTHONIOENCODING
    etapas = {"ficha": etapa_ficha, "escaleta": etapa_escaleta, "guion": etapa_guion}
    for e in [a for a in sys.argv[1:] if a in etapas] or list(etapas):
        try:
            etapas[e]()
        except Parada as x:
            print(f"PARADA ({e}): {x}", flush=True)
            sys.exit(2)


if __name__ == "__main__":
    main()
