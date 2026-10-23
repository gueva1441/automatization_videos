"""F15 §2 — Ycuá y Orleans: ficha v2 (historia y escenas) → escaleta nueva que las usa → guion v5 (prompt literal del
analista), Sol high, sin notas, sin reparación ni editor.

    ficha     researcher_steps.ficha_caso.run (UNA llamada a gpt-6.1-sol high, prompt f15-1) → _steps/<topic>/ficha_caso.json
              + FICHA_<tema>_f15.md. Antes se respalda la ficha anterior: Orleans → ficha_caso_f14.json (F14),
              Ycuá → ficha_caso_f12.json (F12). El crudo del modelo queda en ficha_crudo_<tema>.json.
    escaleta  m01a_escaleta.generate_escaleta(persist=False, ficha=…) — Gemini Pro como siempre, hasta 3 intentos →
              _steps/<topic>/01a_escaleta_f15.json + escaleta_<tema>_f15.json/.md. Ninguna escaleta anterior se pisa.
    guion     guion_v4.write (v5 por defecto: f15-1, largo abierto) con la ficha, Sol high, una llamada →
              guion_<tema>_f15.json + NARRACION_<tema>_f15.md. Bloqueantes con la ficha (el (d) mira sus
              personas_descartadas).

Cada etapa se saltea si su salida ya existe (reanudar sin gastar dos veces). Prompts guardados con md5.
Tope de la tanda: US$ 2.50 (costos_f15.json). Antes de cada llamada: lo gastado + el peor caso de esa llamada + una
reserva para lo que falta no puede pasar el tope (PARADA). Las llamadas a GPT llevan `max_completion_tokens` acotado y
una sola llamada que facture.
Uso: python -I lab/hyperframes/f15/f15_corridas.py [ycua orl] [ficha escaleta guion]
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
sys.path.insert(1, str(LAB.parent / "f13"))                 # repeticion_interna y narracion_md (solo medir/escribir)
TOPE_USD = 2.50
COSTOS = LAB / "costos_f15.json"
PRO_PEOR_USD = 0.30                    # peor caso por intento de escaleta con Pro
RESERVA_TEMA = {"ficha": 0.45, "escaleta": 0.10, "guion": 0.0}   # lo que un tema todavía necesita después de esa etapa
RESERVA_OTRO_TEMA = 1.00               # un tema que todavía no empezó (ficha + escaleta + guion, valores típicos)
TEMAS = {
    "ycua": {"tid": "f8s1-ycua-bolanos", "pool_md5": "5f3c6d0bc31ebf868dd432b2c79fdcec", "bak": "ficha_caso_f12.json",
             "titulo": "Ycuá Bolaños (Asunción, 1 de agosto de 2004)"},
    "orl": {"tid": "ba6c3cac-f7r3", "pool_md5": "e90d6ca9869077fd2759766817588741", "bak": "ficha_caso_f14.json",
            "titulo": "Prisión Parroquial de Orleans (Nueva Orleans, huracán Katrina, agosto–septiembre de 2005)"},
}
NOMBRE = {"ycua": "ycua", "orl": "orleans"}


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
    raw = (_steps(tema) / "00_pool_v3.json").read_bytes()
    if _md5b(raw) != TEMAS[tema]["pool_md5"]:
        raise SystemExit(f"00_pool_v3.json de {tema} no es el fijado: PARADA")
    topic = dict(f15._load_topic_by_id(TEMAS[tema]["tid"]))   # solo lectura: no se escribe topics_db
    topic["escaleta_notas"] = None                             # sin notas
    topic["escaleta_solo_apoyo"] = None
    topic["guion_version"] = 4
    return topic


def _reserva(tema: str, etapa: str, temas: list[str]) -> float:
    """Lo que hay que dejar libre: lo que le falta a este tema después de `etapa` + los temas que vienen después."""
    rest = RESERVA_TEMA[etapa]
    after = temas[temas.index(tema) + 1:]
    return rest + RESERVA_OTRO_TEMA * len(after)


def gpt_call(max_out: int):
    import gpt_helpers
    n = {"posts": 0}

    def post(body: dict) -> dict:
        if n["posts"]:
            raise Parada("la llamada ya facturó una vez (JSON roto o cortado): no hay reintento por el tope")
        body["max_completion_tokens"] = max_out
        n["posts"] += 1
        return gpt_helpers._post(body)
    return gpt_helpers.make_call("gpt-6.1-sol", "high", post=post)


def _max_out(chars_in: int, reserva: float, techo: int) -> int:
    import gpt_helpers
    pin, pout = gpt_helpers.PRICES["gpt-6.1-sol"]
    in_usd = chars_in / 3 / 1e6 * pin                       # cota por arriba (≈ 3.3–3.6 caracteres por token)
    return min(techo, int((TOPE_USD - _costos()["usd_total"] - in_usd - reserva) / pout * 1e6))


# ═══════════════════════════════════════════════════════════════

def etapa_ficha(tema: str, temas: list[str]) -> None:
    from cost_tracker import cost_tracker
    from researcher_steps import ficha_caso as fc
    from script_engine.m01a_skeleton import STEPS_DIR
    nom = NOMBRE[tema]
    if (LAB / f"ficha_crudo_{nom}.json").exists():
        print(f"[{tema} ficha] ya existe: se saltea", flush=True)
        return
    d = _steps(tema)
    cur, bak = d / "ficha_caso.json", d / TEMAS[tema]["bak"]
    if cur.exists() and not bak.exists():
        old = json.loads(cur.read_text(encoding="utf-8"))
        if old.get("prompt_version") != fc.PROMPT_VERSION:
            shutil.copy2(cur, bak)
            print(f"[{tema} ficha] respaldo {cur.name} ({old.get('prompt_version')}) → {bak.name}", flush=True)
    pool = json.loads((d / "00_pool_v3.json").read_text("utf-8"))
    sis, usr = fc.system(), fc.prompt(pool, TEMAS[tema]["titulo"])
    (LAB / f"prompt_{nom}_f15_ficha.txt").write_text(
        f"===== SISTEMA (md5 {_md5(sis)}) =====\n{sis}\n\n===== USUARIO (md5 {_md5(usr)}) =====\n{usr}\n", encoding="utf-8")
    max_out = _max_out(len(sis) + len(usr), _reserva(tema, "ficha", temas), 60000)
    print(f"[{tema} ficha] prompt {len(sis) + len(usr):,} car · max_completion_tokens {max_out:,}", flush=True)
    if max_out < 30000:
        raise Parada(f"no alcanza el tope para la ficha de {tema} (max_out {max_out})")
    import gpt_helpers
    gpt_helpers.TIMEOUT_S = 2400
    cost_tracker.start_video(f"{TEMAS[tema]['tid']}-f15-ficha")
    t0 = time.time()
    try:
        res = fc.run(TEMAS[tema]["tid"], steps_dir=STEPS_DIR, title=TEMAS[tema]["titulo"], tag=f"{nom}_f15",
                     out_dirs=[LAB / f"ficha_{nom}"], call=gpt_call(max_out))
    finally:
        rep = cost_tracker.end_video()
    costo = _add_cost(tema, "ficha", rep, t0, {"max_completion_tokens": max_out,
                                               "prompt_md5": {"sistema": _md5(sis), "usuario": _md5(usr)}})
    _write(LAB / f"ficha_crudo_{nom}.json", res["crudo"])
    for p in (d / "ficha_caso.json", LAB / f"ficha_{nom}" / "ficha_caso.json"):
        f = json.loads(p.read_text(encoding="utf-8"))
        f["costo"] = costo
        _write(p, f)
    m = res["meta"]
    print(f"[{tema} ficha] crudo {m['conteos_crudo']}\n[{tema} ficha] final {m['conteos']} · sacados {m['sacados']}",
          flush=True)
    for s in res["sacados"]:
        print(f"  sacado [{s['seccion']}] {s['que'][:90]} → {s['motivo'][:150]}", flush=True)


def etapa_escaleta(tema: str, temas: list[str]) -> None:
    import gemini_helpers
    from cost_tracker import cost_tracker
    from researcher_steps import ficha_caso as fc
    from script_engine import m01a_escaleta as ma
    nom = NOMBRE[tema]
    out = _steps(tema) / "01a_escaleta_f15.json"
    if out.exists():
        print(f"[{tema} escaleta] ya existe: se saltea", flush=True)
        return
    ficha = fc.load(TEMAS[tema]["tid"])
    if not ficha or ficha.get("prompt_version") != fc.PROMPT_VERSION:
        raise SystemExit(f"falta la ficha f15 de {tema}: correr la etapa ficha")
    topic = _topic(tema)
    pool = topic["evidence_pool"]
    p1 = ma.build_prompt(topic, pool, None, ficha)
    (LAB / f"prompt_{nom}_f15_escaleta.txt").write_text(
        f"===== SISTEMA (md5 {_md5(ma.SYSTEM)}) =====\n{ma.SYSTEM}\n\n===== USUARIO, intento 1 (md5 {_md5(p1)}) =====\n"
        f"{p1}\n", encoding="utf-8")
    spent0 = _costos()["usd_total"]
    reserva = _reserva(tema, "escaleta", temas)

    def call(prompt, **kw):
        now = spent0 + (cost_tracker.current_video.total_cost if cost_tracker.current_video else 0.0)
        if now + PRO_PEOR_USD + reserva > TOPE_USD:
            raise Parada(f"tope de costo: US$ {now:.3f} + peor caso de otro intento + reserva > {TOPE_USD:.2f}")
        return gemini_helpers.call_pro_json(prompt, **kw)
    log: list[str] = []
    cost_tracker.start_video(f"{TEMAS[tema]['tid']}-f15-escaleta")
    t0 = time.time()
    err = None
    try:
        esc = ma.generate_escaleta(topic, call=call, log=log, persist=False, ficha=ficha)
    except Exception as e:  # noqa: BLE001
        esc, err = None, f"{type(e).__name__}: {e}"
    finally:
        rep = cost_tracker.end_video()
    _add_cost(tema, "escaleta", rep, t0, {"prompt_md5_intento1": _md5(p1), "error": err})
    print("\n".join(log), flush=True)
    if esc is None:
        raise Parada(f"escaleta de {tema}: {err}")
    _write(out, esc)
    _write(LAB / f"escaleta_{nom}_f15.json", esc)
    (LAB / f"ESCALETA_{nom}_f15.md").write_text(ma.to_markdown(esc, pool), encoding="utf-8")
    print(f"[{tema} escaleta] {len(esc['beats'])} beats · humano {esc['humano'].get('nombre')} · pico beat "
          f"{esc['pico'].get('beat')} · avisos {esc.get('_avisos')}", flush=True)


def etapa_guion(tema: str, temas: list[str]) -> None:
    from cost_tracker import cost_tracker
    from f13_corridas import PALABRAS_POR_SEG, narracion_md, repeticion_interna
    from researcher_steps import ficha_caso as fc
    from script_engine import guion_v4 as g4
    from script_engine import m01b_guionista as mg
    nom = NOMBRE[tema]
    if (LAB / f"guion_{nom}_f15.json").exists():
        print(f"[{tema} guion] ya existe: se saltea", flush=True)
        return
    esc = json.loads((_steps(tema) / "01a_escaleta_f15.json").read_text(encoding="utf-8"))
    ficha = fc.load(TEMAS[tema]["tid"])
    topic = _topic(tema)
    sis, usr = g4.system(), g4.prompt(topic, esc, ficha=ficha)
    (LAB / f"prompt_{nom}_f15_guion.txt").write_text(
        f"===== SISTEMA (md5 {_md5(sis)}) =====\n{sis}\n\n===== USUARIO (md5 {_md5(usr)}) =====\n{usr}\n", encoding="utf-8")
    max_out = _max_out(len(sis) + len(usr), _reserva(tema, "guion", temas), 32000)
    if max_out < 8000:
        raise Parada(f"no alcanza el tope para el guion de {tema} (max_out {max_out})")
    import gpt_helpers
    gpt_helpers.TIMEOUT_S = 1200
    res: dict = {"tema": nom, "tid": TEMAS[tema]["tid"], "corrida": "f15", "modelo": "gpt-6.1-sol", "esfuerzo": "high",
                 "escaleta": "01a_escaleta_f15.json", "notas": None, "largo": "abierto", "max_completion_tokens": max_out,
                 "prompt_md5": {"sistema": _md5(sis), "usuario": _md5(usr)}}
    cost_tracker.start_video(f"{TEMAS[tema]['tid']}-f15-guion")
    t0 = time.time()
    try:
        g = g4.write(topic, esc, call=gpt_call(max_out), ficha=ficha)
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
    _write(LAB / f"guion_{nom}_f15.json", res)
    if res.get("parrafos"):
        md = narracion_md(nom, tema, esc, res).replace(f"largo abierto, gpt-6.1-sol high, corrida _f13_{tema}_abierto, F13",
                                                       "v5 (f15-1), gpt-6.1-sol high, ficha v2, F15")
        (LAB / f"NARRACION_{nom}_f15.md").write_text(md, encoding="utf-8")
    m = res.get("metricas") or {}
    print(f"[{tema} guion] " + (f"ERROR {res['error']} · " if res.get("error") else "")
          + (f"{m['palabras']} palabras ≈ {res['minutos']} min · bloqueantes {len(res['bloqueantes'])} · por cap "
             f"{[v[0] for v in m['palabras_por_cap'].values()]}" if m else ""), flush=True)
    if res.get("error"):
        raise Parada(res["error"])


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")                # -I ignora PYTHONIOENCODING
    etapas = {"ficha": etapa_ficha, "escaleta": etapa_escaleta, "guion": etapa_guion}
    temas = [a for a in sys.argv[1:] if a in TEMAS] or list(TEMAS)
    pedidas = [a for a in sys.argv[1:] if a in etapas] or list(etapas)
    for tema in temas:
        for e in pedidas:
            try:
                etapas[e](tema, temas)
            except Parada as x:
                print(f"PARADA ({tema} {e}): {x}", flush=True)
                sys.exit(2)


if __name__ == "__main__":
    main()
