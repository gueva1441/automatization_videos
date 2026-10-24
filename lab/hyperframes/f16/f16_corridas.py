"""F16 §2 — Ycuá y Orleans: escaleta v2 (prompt literal del analista, Sol high, 13 bloqueantes, una sola
regeneración) sobre la ficha v2 re-chequeada de F15b (no se rehace) → guion v5.1 (Sol high).

    escaleta  m01a_escaleta.generate_escaleta(persist=False, ficha=…) → con ficha v2 va a `generate_escaleta_v2` →
              _steps/<topic>/01a_escaleta_f16.json (las de F15 y F15b quedan como están) + escaleta_<tema>_f16.json/.md.
              Si después de la regeneración siguen los bloqueantes: PARADA de ese tema (se reporta).
    guion     guion_v4.write (v5.1) con la ficha, Sol high, una llamada → guion_<tema>_f16.json + NARRACION_<tema>_f16.md.

Cada etapa se saltea si su salida ya existe. Prompts guardados con md5. Tope de la tanda: US$ 2.00 (costos_f16.json):
antes de cada llamada, lo gastado + el peor caso de esa llamada (`max_completion_tokens` acotado) + la reserva para lo
que falta no puede pasar el tope (PARADA). Una sola llamada que facture por invocación.
Uso: python -I lab/hyperframes/f16/f16_corridas.py [ycua orl] [escaleta guion]
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
LAB = Path(__file__).resolve().parent
sys.path.insert(1, str(LAB.parent / "f13"))
TOPE_USD = 2.00
COSTOS = LAB / "costos_f16.json"
MAX_OUT_ESC, MAX_OUT_GUION = 30000, 32000
RESERVA = {"escaleta": 0.40, "guion": 0.0}          # lo que el tema necesita después de esa etapa
RESERVA_OTRO_TEMA = 0.90                           # un tema que todavía no hizo escaleta + guion
TEMAS = {
    "ycua": {"tid": "f8s1-ycua-bolanos", "pool_md5": "5f3c6d0bc31ebf868dd432b2c79fdcec"},
    "orl": {"tid": "ba6c3cac-f7r3", "pool_md5": "e90d6ca9869077fd2759766817588741"},
}
NOMBRE = {"ycua": "ycua", "orl": "orleans"}


class Parada(RuntimeError):
    pass


def _md5(s: str) -> str:
    return hashlib.md5(s.encode("utf-8")).hexdigest()


def _write(p: Path, obj) -> None:
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding="utf-8")


def _costos() -> dict:
    return json.loads(COSTOS.read_text(encoding="utf-8")) if COSTOS.exists() else {"etapas": [], "usd_total": 0.0}


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
    print(f"  [{tema} {etapa}] US$ {costo['usd']:.4f} · {costo['segundos']:.0f} s · tanda US$ {c['usd_total']:.4f}",
          flush=True)
    return costo


def _steps(tema: str) -> Path:
    from script_engine.m01a_skeleton import STEPS_DIR
    return STEPS_DIR / TEMAS[tema]["tid"]


def _topic(tema: str) -> dict:
    import fase1_5 as f15
    if hashlib.md5((_steps(tema) / "00_pool_v3.json").read_bytes()).hexdigest() != TEMAS[tema]["pool_md5"]:
        raise SystemExit(f"00_pool_v3.json de {tema} no es el fijado: PARADA")
    topic = dict(f15._load_topic_by_id(TEMAS[tema]["tid"]))   # solo lectura: no se escribe topics_db
    topic["escaleta_notas"] = None
    topic["escaleta_solo_apoyo"] = None
    topic["guion_version"] = 4
    return topic


def _ficha(tema: str) -> dict:
    from researcher_steps import ficha_caso as fc
    f = fc.load(TEMAS[tema]["tid"])
    if not f or "historia" not in f or not str(f.get("chequeo_version") or "").startswith("f15b"):
        raise SystemExit(f"la ficha de {tema} en _steps no es la v2 re-chequeada de F15b: PARADA")
    return f


def _reserva(tema: str, etapa: str, temas: list[str]) -> float:
    return RESERVA[etapa] + RESERVA_OTRO_TEMA * len(temas[temas.index(tema) + 1:])


def sol_call(max_out: int, reserva: float, spent0: float):
    """Sol high; cada invocación: freno de costo y UNA llamada que facture con `max_completion_tokens` = max_out."""
    import gpt_helpers
    from cost_tracker import cost_tracker
    pin, pout = gpt_helpers.PRICES["gpt-6.1-sol"]

    def _call(prompt, system_instruction=None, response_schema=None, thinking_budget=None, description=None):
        now = spent0 + (cost_tracker.current_video.total_cost if cost_tracker.current_video else 0.0)
        worst = (len(prompt) + len(system_instruction or "")) / 3 / 1e6 * pin + max_out / 1e6 * pout
        if now + worst + reserva > TOPE_USD:
            raise Parada(f"tope de costo: US$ {now:.3f} + peor caso {worst:.3f} + reserva {reserva:.2f} > {TOPE_USD:.2f}"
                         f" antes de «{description}»")
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


# ═══════════════════════════════════════════════════════════════

def etapa_escaleta(tema: str, temas: list[str]) -> None:
    import gpt_helpers
    from cost_tracker import cost_tracker
    from script_engine import m01a_escaleta as ma
    nom = NOMBRE[tema]
    out = _steps(tema) / "01a_escaleta_f16.json"
    if out.exists():
        print(f"[{tema} escaleta] ya existe: se saltea", flush=True)
        return
    ficha = _ficha(tema)
    topic = _topic(tema)
    pool = topic["evidence_pool"]
    p1 = ma.build_prompt_v2(topic, pool, ficha)
    (LAB / f"prompt_{nom}_f16_escaleta.txt").write_text(
        f"===== SISTEMA (md5 {_md5(ma.SYSTEM_V2)}) =====\n{ma.SYSTEM_V2}\n\n===== USUARIO, intento 1 (md5 {_md5(p1)}) "
        f"=====\n{p1}\n", encoding="utf-8")
    gpt_helpers.TIMEOUT_S = 1800
    log: list[str] = []
    cost_tracker.start_video(f"{TEMAS[tema]['tid']}-f16-escaleta")
    t0 = time.time()
    err, esc = None, None
    try:
        esc = ma.generate_escaleta(topic, call=sol_call(MAX_OUT_ESC, _reserva(tema, "escaleta", temas),
                                                        _costos()["usd_total"]),
                                   log=log, persist=False, ficha=ficha)
    except Exception as e:  # noqa: BLE001
        err = f"{type(e).__name__}: {e}"
    finally:
        rep = cost_tracker.end_video()
    _add_cost(tema, "escaleta", rep, t0, {"prompt_md5_intento1": {"sistema": _md5(ma.SYSTEM_V2), "usuario": _md5(p1)},
                                          "error": err})
    print("\n".join(log), flush=True)
    if esc is None:
        raise Parada(f"escaleta de {tema}: {err}")
    _write(out, esc)
    _write(LAB / f"escaleta_{nom}_f16.json", esc)
    (LAB / f"ESCALETA_{nom}_f16.md").write_text(ma.to_markdown(esc, pool), encoding="utf-8")
    m = esc["_metricas"]
    print(f"[{tema} escaleta] {len(esc['beats'])} beats · humano {esc['humano'].get('nombre')} (candidato "
          f"{m['humano_en_candidatos']}) · pico beat {esc['pico'].get('beat')} (el de la ficha {m['pico_es_el_de_la_ficha']})"
          f" · curva {m['curva_intensidad']} · ff {m['flash_forward_beat1']} · escenas {m['escenas_usadas']} (gancho "
          f"{m['escena_gancho']}, pico {m['escena_pico']}) · giros {m['giros_con_beat']}/{m['giros_total']}", flush=True)


def etapa_guion(tema: str, temas: list[str]) -> None:
    import gpt_helpers
    from cost_tracker import cost_tracker
    from f13_corridas import PALABRAS_POR_SEG, narracion_md, repeticion_interna
    from script_engine import guion_v4 as g4
    from script_engine import m01b_guionista as mg
    nom = NOMBRE[tema]
    if (LAB / f"guion_{nom}_f16.json").exists():
        print(f"[{tema} guion] ya existe: se saltea", flush=True)
        return
    esc = json.loads((_steps(tema) / "01a_escaleta_f16.json").read_text(encoding="utf-8"))
    ficha = _ficha(tema)
    topic = _topic(tema)
    sis, usr = g4.system(), g4.prompt(topic, esc, ficha=ficha)
    (LAB / f"prompt_{nom}_f16_guion.txt").write_text(
        f"===== SISTEMA (md5 {_md5(sis)}) =====\n{sis}\n\n===== USUARIO (md5 {_md5(usr)}) =====\n{usr}\n", encoding="utf-8")
    gpt_helpers.TIMEOUT_S = 1200
    res: dict = {"tema": nom, "tid": TEMAS[tema]["tid"], "corrida": "f16", "modelo": "gpt-6.1-sol", "esfuerzo": "high",
                 "escaleta": "01a_escaleta_f16.json", "notas": None, "largo": "abierto",
                 "max_completion_tokens": MAX_OUT_GUION, "prompt_md5": {"sistema": _md5(sis), "usuario": _md5(usr)}}
    cost_tracker.start_video(f"{TEMAS[tema]['tid']}-f16-guion")
    t0 = time.time()
    try:
        call = sol_call(MAX_OUT_GUION, _reserva(tema, "guion", temas), _costos()["usd_total"])
        g = g4.write(topic, esc, call=call, ficha=ficha)
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
    _write(LAB / f"guion_{nom}_f16.json", res)
    if res.get("parrafos"):
        md = narracion_md(nom, tema, esc, res).replace(f"largo abierto, gpt-6.1-sol high, corrida _f13_{tema}_abierto, F13",
                                                       "v5.1 (f15b-1), gpt-6.1-sol high, escaleta v2 (f16-1), F16")
        (LAB / f"NARRACION_{nom}_f16.md").write_text(md, encoding="utf-8")
    m = res.get("metricas") or {}
    print(f"[{tema} guion] " + (f"ERROR {res['error']} · " if res.get("error") else "")
          + (f"{m['palabras']} palabras ≈ {res['minutos']} min · bloqueantes {len(res['bloqueantes'])} · párrafos "
             f"{len(res['parrafos'])} · por cap {[v[0] for v in m['palabras_por_cap'].values()]}" if m else ""), flush=True)
    if res.get("error"):
        raise Parada(res["error"])


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")                # -I ignora PYTHONIOENCODING
    etapas = {"escaleta": etapa_escaleta, "guion": etapa_guion}
    temas = [a for a in sys.argv[1:] if a in TEMAS] or list(TEMAS)
    pedidas = [a for a in sys.argv[1:] if a in etapas] or list(etapas)
    for tema in temas:
        for e in pedidas:
            try:
                etapas[e](tema, temas)
            except Parada as x:
                print(f"PARADA ({tema} {e}): {x}", flush=True)
                break                                       # ese tema queda en PARADA; el otro sigue
    print(f"tanda US$ {_costos()['usd_total']:.4f}", flush=True)


if __name__ == "__main__":
    main()
