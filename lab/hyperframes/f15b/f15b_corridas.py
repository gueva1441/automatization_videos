"""F15b §2 — Ycuá y Orleans: re-chequeo de las fichas v2 de F15 (afloje §1.3, SIN llamada) → escaleta nueva (gancho y
pico desde las escenas, §1.2) → guion v5.1 (prompt literal del analista, f15b-1) con Sol high, sin notas, sin
reparación ni editor.

    rechequeo  ficha_caso.save sobre el crudo guardado de F15 (lab/hyperframes/f15/ficha_crudo_<tema>.json); antes se
               respalda la ficha de F15 en _steps como ficha_caso_f15.json. Salida: _steps/<topic>/ficha_caso.json +
               ficha_<tema>/ (FICHA_<tema>_f15b.md) en esta carpeta.
    escaleta   m01a_escaleta.generate_escaleta(persist=False, ficha=…), Gemini Pro como siempre, hasta 3 intentos →
               _steps/<topic>/01a_escaleta_f15b.json (las de F15 quedan como _f15) + escaleta_<tema>_f15b.json/.md.
    guion      guion_v4.write (v5.1 por defecto) con la ficha, Sol high, una llamada → guion_<tema>_f15b.json +
               NARRACION_<tema>_f15b.md.

Cada etapa se saltea si su salida ya existe. Prompts guardados con md5. Tope de la tanda: US$ 1.50 (costos_f15b.json);
antes de cada llamada, lo gastado + el peor caso + una reserva para lo que falta no puede pasar el tope (PARADA).
Uso: python -I lab/hyperframes/f15b/f15b_corridas.py [ycua orl] [rechequeo escaleta guion]
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
F15 = LAB.parent / "f15"
sys.path.insert(1, str(LAB.parent / "f13"))
TOPE_USD = 1.50
COSTOS = LAB / "costos_f15b.json"
PRO_PEOR_USD = 0.30
RESERVA = {"escaleta": 0.15, "guion": 0.0}           # lo que el tema necesita después de esa etapa
RESERVA_OTRO_TEMA = 0.60                             # un tema que todavía no hizo escaleta + guion
TEMAS = {
    "ycua": {"tid": "f8s1-ycua-bolanos", "pool_md5": "5f3c6d0bc31ebf868dd432b2c79fdcec",
             "titulo": "Ycuá Bolaños (Asunción, 1 de agosto de 2004)"},
    "orl": {"tid": "ba6c3cac-f7r3", "pool_md5": "e90d6ca9869077fd2759766817588741",
            "titulo": "Prisión Parroquial de Orleans (Nueva Orleans, huracán Katrina, agosto–septiembre de 2005)"},
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


def _raw_pool(tema: str) -> bytes:
    raw = (_steps(tema) / "00_pool_v3.json").read_bytes()
    if hashlib.md5(raw).hexdigest() != TEMAS[tema]["pool_md5"]:
        raise SystemExit(f"00_pool_v3.json de {tema} no es el fijado: PARADA")
    return raw


def _topic(tema: str) -> dict:
    import fase1_5 as f15
    _raw_pool(tema)
    topic = dict(f15._load_topic_by_id(TEMAS[tema]["tid"]))   # solo lectura: no se escribe topics_db
    topic["escaleta_notas"] = None
    topic["escaleta_solo_apoyo"] = None
    topic["guion_version"] = 4
    return topic


def _reserva(tema: str, etapa: str, temas: list[str]) -> float:
    return RESERVA[etapa] + RESERVA_OTRO_TEMA * len(temas[temas.index(tema) + 1:])


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


# ═══════════════════════════════════════════════════════════════

def etapa_rechequeo(tema: str, temas: list[str]) -> None:
    from researcher_steps import ficha_caso as fc
    from script_engine.m01a_skeleton import STEPS_DIR
    nom = NOMBRE[tema]
    out_dir = LAB / f"ficha_{nom}"
    if (out_dir / "ficha_caso.json").exists():
        print(f"[{tema} rechequeo] ya existe: se saltea", flush=True)
        return
    d = _steps(tema)
    cur, bak = d / "ficha_caso.json", d / "ficha_caso_f15.json"
    if not bak.exists():
        shutil.copy2(cur, bak)
        print(f"[{tema} rechequeo] respaldo {cur.name} (F15) → {bak.name}", flush=True)
    antes = json.loads(bak.read_text(encoding="utf-8"))
    raw = json.loads((F15 / f"ficha_crudo_{nom}.json").read_text(encoding="utf-8"))
    res = fc.save(TEMAS[tema]["tid"], raw, _raw_pool(tema), steps_dir=STEPS_DIR, title=TEMAS[tema]["titulo"],
                  tag=f"{nom}_f15b", out_dirs=[out_dir], usd=0.0)
    vuelven = [s for s in antes["chequeo"]["sacados"]
               if not any(s["item"] == x["item"] for x in res["sacados"])]
    for p in (d / "ficha_caso.json", out_dir / "ficha_caso.json"):
        f = json.loads(p.read_text(encoding="utf-8"))
        f["chequeo_version"] = "f15b (afloje de cifras y sentidos)"
        f["costo"] = {"usd": 0.0, "nota": "re-chequeo sin llamada; la llamada de la ficha es de F15"}
        f["rechequeo"] = {"conteos_f15": antes["conteos"], "sacados_f15": len(antes["chequeo"]["sacados"]),
                          "vuelven": [{"seccion": s["seccion"], "que": s["que"], "motivo_f15": s["motivo"]}
                                      for s in vuelven]}
        _write(p, f)
    print(f"[{tema} rechequeo] F15 {antes['conteos']} · sacados {len(antes['chequeo']['sacados'])}\n"
          f"[{tema} rechequeo] F15b {res['meta']['conteos']} · sacados {len(res['sacados'])} · vuelven {len(vuelven)}",
          flush=True)
    for s in res["sacados"]:
        print(f"  sigue afuera [{s['seccion']}] {s['que'][:80]} → {s['motivo'][:120]}", flush=True)


def etapa_escaleta(tema: str, temas: list[str]) -> None:
    import gemini_helpers
    from cost_tracker import cost_tracker
    from researcher_steps import ficha_caso as fc
    from script_engine import m01a_escaleta as ma
    nom = NOMBRE[tema]
    out = _steps(tema) / "01a_escaleta_f15b.json"
    if out.exists():
        print(f"[{tema} escaleta] ya existe: se saltea", flush=True)
        return
    ficha = fc.load(TEMAS[tema]["tid"])
    if not ficha or not ficha.get("chequeo_version", "").startswith("f15b"):
        raise SystemExit(f"falta la ficha re-chequeada de {tema}: correr la etapa rechequeo")
    topic = _topic(tema)
    pool = topic["evidence_pool"]
    p1 = ma.build_prompt(topic, pool, None, ficha)
    (LAB / f"prompt_{nom}_f15b_escaleta.txt").write_text(
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
    cost_tracker.start_video(f"{TEMAS[tema]['tid']}-f15b-escaleta")
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
    _write(LAB / f"escaleta_{nom}_f15b.json", esc)
    (LAB / f"ESCALETA_{nom}_f15b.md").write_text(ma.to_markdown(esc, pool), encoding="utf-8")
    pb = (esc.get("pico") or {}).get("beat")
    idx = {b["n"]: b.get("escena_idx") for b in esc["beats"]}
    print(f"[{tema} escaleta] {len(esc['beats'])} beats · humano {esc['humano'].get('nombre')} · pico beat {pb} · "
          f"escena gancho {idx.get(1)} · escena pico {idx.get(pb)} · escenas {sorted(v for v in idx.values() if v)} · "
          f"avisos {esc.get('_avisos')}", flush=True)


def etapa_guion(tema: str, temas: list[str]) -> None:
    import gpt_helpers
    from cost_tracker import cost_tracker
    from f13_corridas import PALABRAS_POR_SEG, narracion_md, repeticion_interna
    from researcher_steps import ficha_caso as fc
    from script_engine import guion_v4 as g4
    from script_engine import m01b_guionista as mg
    nom = NOMBRE[tema]
    # --escaleta-f15: si la escaleta F15b no salió, el guion v5.1 sobre la escaleta de F15 (sustituto, marcado aparte)
    sufijo, esc_name = ("_escf15", "01a_escaleta_f15.json") if "--escaleta-f15" in sys.argv else ("", "01a_escaleta_f15b.json")
    if (LAB / f"guion_{nom}_f15b{sufijo}.json").exists():
        print(f"[{tema} guion] ya existe: se saltea", flush=True)
        return
    esc = json.loads((_steps(tema) / esc_name).read_text(encoding="utf-8"))
    ficha = fc.load(TEMAS[tema]["tid"])
    topic = _topic(tema)
    sis, usr = g4.system(), g4.prompt(topic, esc, ficha=ficha)
    (LAB / f"prompt_{nom}_f15b{sufijo}_guion.txt").write_text(
        f"===== SISTEMA (md5 {_md5(sis)}) =====\n{sis}\n\n===== USUARIO (md5 {_md5(usr)}) =====\n{usr}\n", encoding="utf-8")
    pin, pout = gpt_helpers.PRICES["gpt-6.1-sol"]
    in_usd = (len(sis) + len(usr)) / 3 / 1e6 * pin
    max_out = min(32000, int((TOPE_USD - _costos()["usd_total"] - in_usd - _reserva(tema, "guion", temas)) / pout * 1e6))
    if max_out < 8000:
        raise Parada(f"no alcanza el tope para el guion de {tema} (max_out {max_out})")
    gpt_helpers.TIMEOUT_S = 1200
    res: dict = {"tema": nom, "tid": TEMAS[tema]["tid"], "corrida": "f15b", "modelo": "gpt-6.1-sol", "esfuerzo": "high",
                 "escaleta": esc_name, "notas": None, "largo": "abierto", "max_completion_tokens": max_out,
                 "prompt_md5": {"sistema": _md5(sis), "usuario": _md5(usr)}}
    cost_tracker.start_video(f"{TEMAS[tema]['tid']}-f15b-guion")
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
    _write(LAB / f"guion_{nom}_f15b{sufijo}.json", res)
    if res.get("parrafos"):
        md = narracion_md(nom, tema, esc, res).replace(f"largo abierto, gpt-6.1-sol high, corrida _f13_{tema}_abierto, F13",
                                                       "v5.1 (f15b-1), gpt-6.1-sol high, ficha v2 re-chequeada, F15b")
        if sufijo:
            md = md.replace("ficha v2 re-chequeada, F15b", "ficha v2 re-chequeada, escaleta de F15 (la F15b no salió), F15b")
        (LAB / f"NARRACION_{nom}_f15b{sufijo}.md").write_text(md, encoding="utf-8")
    m = res.get("metricas") or {}
    print(f"[{tema} guion] " + (f"ERROR {res['error']} · " if res.get("error") else "")
          + (f"{m['palabras']} palabras ≈ {res['minutos']} min · bloqueantes {len(res['bloqueantes'])} · párrafos "
             f"{len(res['parrafos'])} · por cap {[v[0] for v in m['palabras_por_cap'].values()]}" if m else ""), flush=True)
    if res.get("error"):
        raise Parada(res["error"])


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")                # -I ignora PYTHONIOENCODING
    etapas = {"rechequeo": etapa_rechequeo, "escaleta": etapa_escaleta, "guion": etapa_guion}
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
