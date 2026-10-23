"""F11b §2 — tres corridas del guion v4 (con la línea de largo) sobre Ycuá, una por modelo, con el MISMO prompt exacto.

    Ycuá  f8s1-ycua-bolanos  01a_escaleta_v1.json  (md5 e1ba1a48…, 12 beats, Liz Torres), sin notas

    gem    Gemini Pro (el de siempre)   esfuerzo —
    sol    gpt-6.1-sol                  esfuerzo high
    astra  gpt-6-astra                  esfuerzo el de la API

Cada corrida: guion_v4.write (una llamada) → guion_v4.reparar (una ronda) → m01d.particionar (persist=False; acorta
con el editor de siempre) → juez m05 (el de siempre). Toda la cadena v4 (guionista, regeneración, edición de
oración, editor) usa el `call` del modelo (`guion_v4.call_for`).
El prompt del guionista se guarda UNA vez en `prompt_ycua_v4b.txt`; cada corrida verifica que el que manda es ese,
byte a byte. Salidas `_v4b_<tag>` en _steps/f8s1-ycua-bolanos/ y en lab/hyperframes/f11b/; no pisa F11, _v1, _ajuste
ni los vigentes; no escribe en topics_db.
Tope de la tanda: US$ 2.00. Antes de cada corrida, si lo gastado + la estimación la pasa, PARADA; además, antes de
cada llamada, si lo gastado + lo que va de la corrida pasa el tope, la corrida se corta (PARADA).
Si un modelo no existe o falla, se reporta: no se reemplaza por otro.
Uso: python -I lab/hyperframes/f11b/f11b_corridas.py [gem sol astra]
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
TOPE_USD = 2.00
TID, ESC, MD5 = "f8s1-ycua-bolanos", "01a_escaleta_v1.json", "e1ba1a48"
MODELOS = {"gem": ("gemini-pro", 0.50), "sol": ("gpt-6.1-sol", 0.35), "astra": ("gpt-6-astra", 1.00)}
PROMPT = LAB / "prompt_ycua_v4b.txt"
COSTOS = LAB / "costos_f11b.json"


class Parada(RuntimeError):
    pass


def _steps() -> Path:
    from script_engine.m01a_skeleton import STEPS_DIR
    return STEPS_DIR / TID


def _load() -> tuple[dict, dict]:
    import fase1_5 as f15
    raw = (_steps() / ESC).read_bytes()
    if not hashlib.md5(raw).hexdigest().startswith(MD5):
        raise SystemExit(f"la escaleta {ESC} no es la fijada (md5 {MD5}…)")
    topic = dict(f15._load_topic_by_id(TID))               # solo lectura: no se escribe topics_db
    topic["guion_version"] = 4
    return topic, json.loads(raw.decode("utf-8"))


def _costos() -> dict:
    return json.loads(COSTOS.read_text(encoding="utf-8")) if COSTOS.exists() else {"corridas": [], "usd_total": 0.0}


def _write(p: Path, obj) -> None:
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding="utf-8")


def guarded(call, prompt_ok: str, spent: float):
    """El `call` del modelo con dos frenos: el prompt del guionista tiene que ser el guardado, y lo gastado + lo que va
    de la corrida no puede pasar el tope."""
    from cost_tracker import cost_tracker

    def _c(prompt, **kw):
        if kw.get("description") == "guion_v4 guionista" and prompt != prompt_ok:
            raise Parada("el prompt del guionista no es el de prompt_ycua_v4b.txt")
        now = spent + (cost_tracker.current_video.total_cost if cost_tracker.current_video else 0.0)
        if now > TOPE_USD:
            raise Parada(f"tope de costo: US$ {now:.3f} > {TOPE_USD:.2f} antes de «{kw.get('description')}»")
        return call(prompt, **kw)
    return _c


def narracion_md(tag: str, modelo: str, esc: dict, res: dict) -> str:
    beats = {b["n"]: b for b in esc["beats"]}
    r = res.get("reparacion") or {}
    ps = r.get("parrafos") or []
    m = res.get("metricas") or {}
    titles = {c["chapter_number"]: c["title"] for c in (res.get("skeleton") or {}).get("chapters") or []}
    bl = r.get("bloqueantes_despues") or []
    lines = [f"# Narración — Ycuá Bolaños (guion v4b, {modelo}, corrida _v4b_{tag}, F11b)", ""]
    if res.get("error"):
        lines += [f"**Error:** {res['error']}", ""]
    if m:
        ipp = m.get("ids_por_parrafo") or {}
        lines += [f"**{m['palabras']} palabras** · bloqueantes finales: {len(bl)} · duras v3 re-medidas: "
                  f"{len(m['duras_v3'])} · citas: {m['citas']} · humano por nombre en los caps {m['humano_caps']} · "
                  f"cierre: {m['cierre']} · ids por párrafo {ipp.get('antes')} → {ipp.get('despues')} · "
                  f"US$ {res['costo']['usd']:.3f} · {res['costo']['segundos']:.0f} s", ""]
    for x in bl:
        lines.append(f"- bloqueante ({x['codigo']}) cap {x['cap']} beat {x['beat']}: {x['motivo']}"
                     + (f" — «{x['frase']}»" if x["frase"] else ""))
    if res.get("particion_error"):
        lines += ["", f"**Partición:** {res['particion_error']}"]
    lines.append("")
    for n in range(1, 8):
        cps = [p for p in ps if p["cap"] == n]
        w, tgt = (m.get("palabras_por_cap") or {}).get(n) or [0, 0]
        lines += [f"## Cap {n}" + (f" — {titles[n]}" if n in titles else "") + f" · {w}/{tgt} palabras", ""]
        for p in cps:
            b = beats.get(p["beat"], {})
            lines += [f"**Beat {p['beat']}** · {b.get('funcion')} · ids {', '.join(p.get('ids_usados') or [])}", "",
                      p["texto"], ""]
    return "\n".join(lines)


def corrida(tag: str, prompt_ok: str, spent: float) -> dict:
    from cost_tracker import cost_tracker
    from script_engine import guion_v4 as g4
    from script_engine import m01d_particion as md
    from script_engine.m05_narrative import judge_narration
    modelo = MODELOS[tag][0]
    topic, esc = _load()
    pool = topic["evidence_pool"]
    log: list[str] = []
    res: dict = {"tema": "ycua", "tid": TID, "corrida": f"v4b_{tag}", "modelo": modelo,
                 "esfuerzo": g4.ESFUERZO.get(modelo), "escaleta": ESC, "notas": None,
                 "prompt_md5": hashlib.md5(prompt_ok.encode("utf-8")).hexdigest()}
    cost_tracker.start_video(f"{TID}-v4b_{tag}")
    t0 = time.time()
    try:
        call = guarded(g4.call_for(modelo), prompt_ok, spent)
        g = g4.write(topic, esc, call=call, log=log)
        res["crudo"] = g["parrafos"]
        res["prompt_version"] = g["prompt_version"]
        res["segundos_guionista"] = round(time.time() - t0, 1)
        res["bloqueantes_crudo"] = g4.bloqueantes(topic, esc, g["parrafos"])
        res["metricas_crudo"] = g4.metricas(topic, esc, g["parrafos"])
        r = g4.reparar(topic, esc, g["parrafos"], call=call, log=log)
        res["reparacion"] = r
        res["metricas"] = g4.metricas(topic, esc, r["parrafos"])
        try:
            part = md.particionar(topic, esc, r["parrafos"], pool, persist=False, shorten=md.editor_shorten(),
                                  log=log)
            res["skeleton"], res["particion_notas"] = part["skeleton"], part["notas"]
            d = _steps()
            _write(d / f"01a_skeleton_v4b_{tag}.json", part["skeleton"])
            _write(d / f"01b_narration_v4b_{tag}.json", part["narration"])
            _write(d / f"01b_narracion_v3_v4b_{tag}.json", part["narracion_v3"])
            res["juez"] = judge_narration(TID, pool=pool, narration=part["narration"], skeleton=part["skeleton"],
                                          out_name=f"06_judge_narrative_v4b_{tag}.json").get("video")
        except md.ParticionError as e:
            res["particion_error"] = str(e)
    except Exception as e:  # noqa: BLE001 — se reporta tal cual; no se reemplaza el modelo
        res["error"] = f"{type(e).__name__}: {e}"
        res["traceback"] = traceback.format_exc()[-2000:]
    finally:
        rep = cost_tracker.end_video()
    res["costo"] = {"usd": round(getattr(rep, "total_cost", 0.0) or 0.0, 4), "segundos": round(time.time() - t0, 1),
                    "llamadas": [{"servicio": e.service, "desc": e.description, "in": e.tokens_in,
                                  "out": e.tokens_out, "thinking": e.tokens_thinking, "usd": round(e.total_cost, 4)}
                                 for e in (getattr(rep, "entries", None) or [])]}
    res["log"] = log
    _write(_steps() / f"01b_guionista_v4b_{tag}.json", res)
    _write(LAB / f"guion_ycua_v4b_{tag}.json", res)
    (LAB / f"NARRACION_ycua_v4b_{tag}.md").write_text(narracion_md(tag, modelo, esc, res), encoding="utf-8")
    c = _costos()
    c["corridas"].append({"corrida": tag, "modelo": modelo, "usd": res["costo"]["usd"],
                          "segundos": res["costo"]["segundos"], "error": res.get("error")})
    c["usd_total"] = round(sum(x["usd"] for x in c["corridas"]), 4)
    _write(COSTOS, c)
    r = res.get("reparacion") or {}
    print(f"[{tag} {modelo}] " + (f"ERROR {res['error']} · " if res.get("error") else "")
          + (f"bloqueantes {len(res['bloqueantes_crudo'])} → {len(r['bloqueantes_despues'])} · "
             f"{res['metricas']['palabras']} palabras · " if r else "")
          + f"US$ {res['costo']['usd']:.3f} · total US$ {c['usd_total']:.3f}", flush=True)
    return res


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")                # -I ignora PYTHONIOENCODING
    from script_engine import guion_v4 as g4
    topic, esc = _load()
    p = g4.prompt(topic, esc)
    if PROMPT.exists() and PROMPT.read_text(encoding="utf-8") != p:
        raise SystemExit("prompt_ycua_v4b.txt existe y es distinto del prompt actual: PARADA")
    PROMPT.write_text(p, encoding="utf-8")
    print(f"prompt {len(p)} caracteres · md5 {hashlib.md5(p.encode('utf-8')).hexdigest()[:8]}", flush=True)
    for tag in [a for a in sys.argv[1:] if a in MODELOS] or list(MODELOS):
        spent = _costos()["usd_total"]
        if spent + MODELOS[tag][1] > TOPE_USD:
            print(f"PARADA por costo: gastado US$ {spent:.3f}; {tag} no corre (tope US$ {TOPE_USD:.2f})", flush=True)
            break
        res = corrida(tag, p, spent)
        if isinstance(res.get("error"), str) and res["error"].startswith("Parada"):
            print("PARADA: " + res["error"], flush=True)
            break


if __name__ == "__main__":
    main()
