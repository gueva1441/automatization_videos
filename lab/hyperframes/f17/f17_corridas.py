"""F17 §2 — la columna vertebral: ficha v2 (F15b, sin rehacer) → columna (Sol high) → escaleta v2 con columna (Sol
high, 13 bloqueantes) → guion v5.1 (Sol high, sin cambios).

    columna   m01a_columna.generate_columna(persist=False) → _steps/<topic>/01a_columna.json + columna_<tema>_f17.json +
              COLUMNA_<tema>.md. Si existe _steps/<topic>/columna_notas.md y la columna guardada no tiene notas, se
              regenera UNA vez con las notas en la tarea (la anterior queda como 01a_columna_v1.json y COLUMNA_<tema>_v1.md).
    escaleta  m01a_escaleta.generate_escaleta(persist=False, ficha=…, columna=<la de arriba>) →
              _steps/<topic>/01a_escaleta_f17.json (no se pisa _f16) + escaleta_<tema>_f17.json/.md.
    guion     guion_v4.write (v5.1) con la ficha → guion_<tema>_f17.json + NARRACION_<tema>_f17.md.

Cada etapa se saltea si su salida ya existe. Prompts guardados con md5. Tope de la tanda: US$ 2.00 (costos_f17.json):
antes de cada llamada, lo gastado + el peor caso (`max_completion_tokens` acotado) + la reserva para lo que falta no
puede pasar el tope (PARADA). Una sola llamada que facture por invocación (`f16_corridas.sol_call`).
Uso: python -I lab/hyperframes/f17/f17_corridas.py [ycua orl] [columna escaleta guion]
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LAB = Path(__file__).resolve().parent
sys.path.insert(0, str(LAB))
sys.path.insert(1, str(ROOT))
sys.path.insert(2, str(LAB.parent / "f16"))
sys.path.insert(3, str(LAB.parent / "f13"))
import f16_corridas as f16  # noqa: E402

TOPE_USD = 2.00
COSTOS = LAB / "costos_f17.json"
MAX_OUT_COL, MAX_OUT_ESC, MAX_OUT_GUION = 16000, 30000, 32000
RESERVA = {"columna": 0.55, "escaleta": 0.15, "guion": 0.0}     # lo que el tema necesita después de esa etapa
RESERVA_OTRO_TEMA = 0.80                                        # un tema que todavía no hizo columna + escaleta + guion
TEMAS, NOMBRE = f16.TEMAS, f16.NOMBRE
Parada = f16.Parada
f16.TOPE_USD = TOPE_USD


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


def _reserva(tema: str, etapa: str, temas: list[str]) -> float:
    return RESERVA[etapa] + RESERVA_OTRO_TEMA * len(temas[temas.index(tema) + 1:])


def _call(max_out: int, tema: str, etapa: str, temas: list[str]):
    return f16.sol_call(max_out, _reserva(tema, etapa, temas), _costos()["usd_total"])


# ═══════════════════════════════════════════════════════════════

def etapa_columna(tema: str, temas: list[str]) -> None:
    import gpt_helpers
    from cost_tracker import cost_tracker
    from script_engine import m01a_columna as mc
    nom = NOMBRE[tema]
    out = f16._steps(tema) / "01a_columna.json"
    notas_f = f16._steps(tema) / "columna_notas.md"
    notas = notas_f.read_text(encoding="utf-8").strip() if notas_f.exists() else None
    previa = json.loads(out.read_text(encoding="utf-8")) if out.exists() else None
    if previa and (not notas or previa.get("notas")):
        print(f"[{tema} columna] ya existe: se saltea", flush=True)
        return
    if previa and notas:                                     # F17 §2: UNA regeneración con las notas de Omar
        _write(f16._steps(tema) / "01a_columna_v1.json", previa)
        _write(LAB / f"columna_{nom}_f17_v1.json", previa)
        (LAB / f"COLUMNA_{nom}_v1.md").write_text(
            (LAB / f"COLUMNA_{nom}.md").read_text(encoding="utf-8"), encoding="utf-8")
    ficha = f16._ficha(tema)
    topic = f16._topic(tema)
    pool = topic["evidence_pool"]
    p1 = mc.build_prompt(topic, pool, ficha, notas=notas)
    sufijo = "_notas" if notas else ""
    (LAB / f"prompt_{nom}_f17_columna{sufijo}.txt").write_text(
        f"===== SISTEMA (md5 {_md5(mc.SYSTEM)}) =====\n{mc.SYSTEM}\n\n===== USUARIO, intento 1 (md5 {_md5(p1)}) "
        f"=====\n{p1}\n", encoding="utf-8")
    gpt_helpers.TIMEOUT_S = 1800
    log: list[str] = []
    cost_tracker.start_video(f"{TEMAS[tema]['tid']}-f17-columna")
    t0 = time.time()
    err, col = None, None
    try:
        col = mc.generate_columna(topic, pool, ficha, call=_call(MAX_OUT_COL, tema, "columna", temas), log=log,
                                  persist=False, notas=notas)
    except Exception as e:  # noqa: BLE001
        err = f"{type(e).__name__}: {e}"
    finally:
        rep = cost_tracker.end_video()
    _add_cost(tema, "columna" + sufijo, rep, t0,
              {"prompt_md5_intento1": {"sistema": _md5(mc.SYSTEM), "usuario": _md5(p1)}, "error": err})
    print("\n".join(log), flush=True)
    if col is None:
        raise Parada(f"columna de {tema}: {err}")
    mc.save(TEMAS[tema]["tid"], col)
    _write(LAB / f"columna_{nom}_f17.json", col)
    (LAB / f"COLUMNA_{nom}.md").write_text(mc.to_markdown(col, topic.get("video_title") or nom), encoding="utf-8")
    print(f"[{tema} columna] humano {col['humano'].get('nombre')} · pico cap {col['pico'].get('cap')} · personas con "
          f"nombre {col['_metricas']['personas_con_nombre']} · afuera {len(col.get('afuera') or [])}", flush=True)


def etapa_escaleta(tema: str, temas: list[str]) -> None:
    import gpt_helpers
    from cost_tracker import cost_tracker
    from script_engine import m01a_columna as mc
    from script_engine import m01a_escaleta as ma
    nom = NOMBRE[tema]
    out = f16._steps(tema) / "01a_escaleta_f17.json"
    if out.exists():
        print(f"[{tema} escaleta] ya existe: se saltea", flush=True)
        return
    col = mc.load(TEMAS[tema]["tid"])
    if not col:
        raise Parada(f"escaleta de {tema}: falta la columna")
    ficha = f16._ficha(tema)
    topic = f16._topic(tema)
    pool = topic["evidence_pool"]
    p1 = ma.build_prompt_v2(topic, pool, ficha, columna=col)
    (LAB / f"prompt_{nom}_f17_escaleta.txt").write_text(
        f"===== SISTEMA (md5 {_md5(ma.SYSTEM_V2)}) =====\n{ma.SYSTEM_V2}\n\n===== USUARIO, intento 1 (md5 {_md5(p1)}) "
        f"=====\n{p1}\n", encoding="utf-8")
    gpt_helpers.TIMEOUT_S = 1800
    log: list[str] = []
    cost_tracker.start_video(f"{TEMAS[tema]['tid']}-f17-escaleta")
    t0 = time.time()
    err, esc = None, None
    try:
        esc = ma.generate_escaleta(topic, call=_call(MAX_OUT_ESC, tema, "escaleta", temas), log=log, persist=False,
                                   ficha=ficha, columna=col)
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
    _write(LAB / f"escaleta_{nom}_f17.json", esc)
    (LAB / f"ESCALETA_{nom}_f17.md").write_text(ma.to_markdown(esc, pool), encoding="utf-8")
    m = esc["_metricas"]
    mcol = m["columna"]
    print(f"[{tema} escaleta] {len(esc['beats'])} beats · humano {esc['humano'].get('nombre')} (= columna "
          f"{mcol['humano_es_el_de_la_columna']}) · caps con personas fuera {mcol['caps_con_personas_fuera']} · cierres "
          f"iguales {mcol['cierres_iguales']}/7 · pico beat {esc['pico'].get('beat')} · escenas {m['escenas_usadas']}",
          flush=True)


def etapa_guion(tema: str, temas: list[str]) -> None:
    import gpt_helpers
    from cost_tracker import cost_tracker
    from f13_corridas import PALABRAS_POR_SEG, narracion_md, repeticion_interna
    from script_engine import guion_v4 as g4
    from script_engine import m01b_guionista as mg
    nom = NOMBRE[tema]
    if (LAB / f"guion_{nom}_f17.json").exists():
        print(f"[{tema} guion] ya existe: se saltea", flush=True)
        return
    esc = json.loads((f16._steps(tema) / "01a_escaleta_f17.json").read_text(encoding="utf-8"))
    ficha = f16._ficha(tema)
    topic = f16._topic(tema)
    sis, usr = g4.system(), g4.prompt(topic, esc, ficha=ficha)
    (LAB / f"prompt_{nom}_f17_guion.txt").write_text(
        f"===== SISTEMA (md5 {_md5(sis)}) =====\n{sis}\n\n===== USUARIO (md5 {_md5(usr)}) =====\n{usr}\n", encoding="utf-8")
    gpt_helpers.TIMEOUT_S = 1200
    res: dict = {"tema": nom, "tid": TEMAS[tema]["tid"], "corrida": "f17", "modelo": "gpt-6.1-sol", "esfuerzo": "high",
                 "escaleta": "01a_escaleta_f17.json", "notas": None, "largo": "abierto",
                 "max_completion_tokens": MAX_OUT_GUION, "prompt_md5": {"sistema": _md5(sis), "usuario": _md5(usr)}}
    cost_tracker.start_video(f"{TEMAS[tema]['tid']}-f17-guion")
    t0 = time.time()
    try:
        g = g4.write(topic, esc, call=_call(MAX_OUT_GUION, tema, "guion", temas), ficha=ficha)
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
    _write(LAB / f"guion_{nom}_f17.json", res)
    if res.get("parrafos"):
        md = narracion_md(nom, tema, esc, res).replace(f"largo abierto, gpt-6.1-sol high, corrida _f13_{tema}_abierto, F13",
                                                       "v5.1 (f15b-1), gpt-6.1-sol high, columna + escaleta v2 (f17-1), F17")
        (LAB / f"NARRACION_{nom}_f17.md").write_text(md, encoding="utf-8")
    m = res.get("metricas") or {}
    print(f"[{tema} guion] " + (f"ERROR {res['error']} · " if res.get("error") else "")
          + (f"{m['palabras']} palabras ≈ {res['minutos']} min · bloqueantes {len(res['bloqueantes'])} · párrafos "
             f"{len(res['parrafos'])} · por cap {[v[0] for v in m['palabras_por_cap'].values()]}" if m else ""), flush=True)
    if res.get("error"):
        raise Parada(res["error"])


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")                # -I ignora PYTHONIOENCODING
    etapas = {"columna": etapa_columna, "escaleta": etapa_escaleta, "guion": etapa_guion}
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
