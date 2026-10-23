"""F11c §2 — dos corridas del guion v4 reestructurado (sistema: rol, voz, oficio, ejemplos; usuario: datos y la tarea al
final) sobre Ycuá, con el MISMO prompt exacto.

    Ycuá  f8s1-ycua-bolanos  01a_escaleta_v1.json  (md5 e1ba1a48…, 12 beats, Liz Torres), sin notas

    argon  gemini-4-argon   esfuerzo por defecto (sin temperature, top_p, top_k ni thinking_budget)
    sol    gpt-6.1-sol      esfuerzo high

Cada corrida: guion_v4.write (una llamada) → guion_v4.reparar (una ronda; sin el editor m01c si el crudo tiene 0
bloqueantes) → m01d.particionar (persist=False) → juez m05 (el de siempre). Toda la cadena v4 usa el `call` del modelo.
El sistema y el usuario se guardan UNA vez en `prompt_ycua_v4c_{sistema,usuario}.txt` (con su md5 en
`prompt_ycua_v4c.md5`); cada corrida verifica, byte a byte, que lo que manda el guionista es eso.
Salidas `_v4c_<tag>` en _steps/f8s1-ycua-bolanos/ y en lab/hyperframes/f11c/; no pisa nada anterior ni escribe en
topics_db. Tope de la tanda: US$ 1.50 (humo incluido). Antes de cada corrida, si lo gastado + la estimación lo pasa,
PARADA; antes de cada llamada, si lo gastado + lo que va de la corrida lo pasa, la corrida se corta (PARADA).
Si un modelo falla, se reporta: no se reemplaza por otro.
Uso: python -I lab/hyperframes/f11c/f11c_corridas.py [argon sol]
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
TOPE_USD = 1.50
TID, ESC, MD5 = "f8s1-ycua-bolanos", "01a_escaleta_v1.json", "e1ba1a48"
MODELOS = {"argon": ("gemini-4-argon", 0.45), "sol": ("gpt-6.1-sol", 0.35)}
P_SIS, P_USR, P_MD5 = LAB / "prompt_ycua_v4c_sistema.txt", LAB / "prompt_ycua_v4c_usuario.txt", LAB / "prompt_ycua_v4c.md5"
COSTOS = LAB / "costos_f11c.json"


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


def _md5(s: str) -> str:
    return hashlib.md5(s.encode("utf-8")).hexdigest()


def _costos() -> dict:
    return json.loads(COSTOS.read_text(encoding="utf-8")) if COSTOS.exists() else {"corridas": [], "usd_total": 0.0}


def _write(p: Path, obj) -> None:
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding="utf-8")


def guarded(call, sis_ok: str, usr_ok: str, spent: float):
    """El `call` del modelo con dos frenos: el sistema y el usuario del guionista tienen que ser los guardados, y lo
    gastado + lo que va de la corrida no puede pasar el tope."""
    from cost_tracker import cost_tracker

    def _c(prompt, **kw):
        if kw.get("description") == "guion_v4 guionista" and (prompt != usr_ok or kw.get("system_instruction") != sis_ok):
            raise Parada("el prompt del guionista no es el de prompt_ycua_v4c_{sistema,usuario}.txt")
        now = spent + (cost_tracker.current_video.total_cost if cost_tracker.current_video else 0.0)
        if now > TOPE_USD:
            raise Parada(f"tope de costo: US$ {now:.3f} > {TOPE_USD:.2f} antes de «{kw.get('description')}»")
        return call(prompt, **kw)
    return _c


def _texto(lines: list[str], ps: list[dict], beats: dict, m: dict, titles: dict) -> None:
    for n in range(1, 8):
        cps = [p for p in ps if p["cap"] == n]
        w, tgt = (m.get("palabras_por_cap") or {}).get(n) or (m.get("palabras_por_cap") or {}).get(str(n)) or [0, 0]
        lines += [f"### Cap {n}" + (f" — {titles[n]}" if n in titles else "") + f" · {w}/{tgt} palabras", ""]
        for p in cps:
            b = beats.get(p["beat"], {})
            lines += [f"**Beat {p['beat']}** · {b.get('funcion')} · ids {', '.join(p.get('ids_usados') or [])}", "",
                      p["texto"], ""]


def narracion_md(tag: str, modelo: str, esc: dict, res: dict) -> str:
    beats = {b["n"]: b for b in esc["beats"]}
    r = res.get("reparacion") or {}
    titles = {c["chapter_number"]: c["title"] for c in (res.get("skeleton") or {}).get("chapters") or []}
    lines = [f"# Narración — Ycuá Bolaños (guion v4c, {modelo}, corrida _v4c_{tag}, F11c)", "",
             f"Prompt `{res.get('prompt_version')}` · sistema md5 `{res['prompt_md5']['sistema'][:8]}` · usuario md5 "
             f"`{res['prompt_md5']['usuario'][:8]}` · US$ {res['costo']['usd']:.3f} · {res['costo']['segundos']:.0f} s",
             ""]
    if res.get("error"):
        lines += [f"**Error:** {res['error']}", ""]
    if res.get("particion_error"):
        lines += [f"**Partición:** {res['particion_error']}", ""]
    for nombre, ps, m, bl in (("Crudo (lo que escribió el guionista)", res.get("crudo") or [],
                               res.get("metricas_crudo") or {}, res.get("bloqueantes_crudo") or []),
                              ("Final (después de la ronda)", r.get("parrafos") or [], res.get("metricas") or {},
                               r.get("bloqueantes_despues") or [])):
        if not ps:
            continue
        lines += [f"## {nombre}", ""]
        if m:
            lines += [f"**{m['palabras']} palabras** · bloqueantes: {len(bl)} · duras v3 re-medidas: "
                      f"{len(m['duras_v3'])} · citas: {m['citas']} · humano por nombre en los caps {m['humano_caps']}"
                      f" · cierre: {m['cierre']}", ""]
        for x in bl:
            lines.append(f"- bloqueante ({x['codigo']}) cap {x['cap']} beat {x['beat']}: {x['motivo']}"
                         + (f" — «{x['frase']}»" if x["frase"] else ""))
        if bl:
            lines.append("")
        _texto(lines, ps, beats, m, titles)
    return "\n".join(lines)


def corrida(tag: str, sis: str, usr: str, spent: float) -> dict:
    from cost_tracker import cost_tracker
    from script_engine import guion_v4 as g4
    from script_engine import m01d_particion as md
    from script_engine.m05_narrative import judge_narration
    modelo = MODELOS[tag][0]
    topic, esc = _load()
    pool = topic["evidence_pool"]
    log: list[str] = []
    res: dict = {"tema": "ycua", "tid": TID, "corrida": f"v4c_{tag}", "modelo": modelo,
                 "esfuerzo": g4.ESFUERZO.get(modelo), "escaleta": ESC, "notas": None,
                 "prompt_md5": {"sistema": _md5(sis), "usuario": _md5(usr)}}
    cost_tracker.start_video(f"{TID}-v4c_{tag}")
    t0 = time.time()
    try:
        call = guarded(g4.call_for(modelo), sis, usr, spent)
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
            _write(d / f"01a_skeleton_v4c_{tag}.json", part["skeleton"])
            _write(d / f"01b_narration_v4c_{tag}.json", part["narration"])
            _write(d / f"01b_narracion_v3_v4c_{tag}.json", part["narracion_v3"])
            res["juez"] = judge_narration(TID, pool=pool, narration=part["narration"], skeleton=part["skeleton"],
                                          out_name=f"06_judge_narrative_v4c_{tag}.json").get("video")
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
    _write(_steps() / f"01b_guionista_v4c_{tag}.json", res)
    _write(LAB / f"guion_ycua_v4c_{tag}.json", res)
    (LAB / f"NARRACION_ycua_v4c_{tag}.md").write_text(narracion_md(tag, modelo, esc, res), encoding="utf-8")
    c = _costos()
    c["corridas"].append({"corrida": tag, "modelo": modelo, "usd": res["costo"]["usd"],
                          "segundos": res["costo"]["segundos"], "error": res.get("error")})
    c["usd_total"] = round(sum(x["usd"] for x in c["corridas"]), 4)
    _write(COSTOS, c)
    r = res.get("reparacion") or {}
    print(f"[{tag} {modelo}] " + (f"ERROR {res['error']} · " if res.get("error") else "")
          + (f"bloqueantes {len(res['bloqueantes_crudo'])} → {len(r['bloqueantes_despues'])} · "
             f"{res['metricas_crudo']['palabras']} → {res['metricas']['palabras']} palabras · " if r else "")
          + f"US$ {res['costo']['usd']:.3f} · total US$ {c['usd_total']:.3f}", flush=True)
    return res


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")                # -I ignora PYTHONIOENCODING
    from script_engine import guion_v4 as g4
    topic, esc = _load()
    sis, usr = g4.system(), g4.prompt(topic, esc)
    for p, s in ((P_SIS, sis), (P_USR, usr)):
        if p.exists() and p.read_text(encoding="utf-8") != s:
            raise SystemExit(f"{p.name} existe y es distinto del prompt actual: PARADA")
        p.write_text(s, encoding="utf-8")
    P_MD5.write_text(f"{_md5(sis)}  {P_SIS.name}\n{_md5(usr)}  {P_USR.name}\n", encoding="utf-8")
    print(f"sistema {len(sis)} car · md5 {_md5(sis)[:8]} · usuario {len(usr)} car · md5 {_md5(usr)[:8]}", flush=True)
    for tag in [a for a in sys.argv[1:] if a in MODELOS] or list(MODELOS):
        spent = _costos()["usd_total"]
        if spent + MODELOS[tag][1] > TOPE_USD:
            print(f"PARADA por costo: gastado US$ {spent:.3f}; {tag} no corre (tope US$ {TOPE_USD:.2f})", flush=True)
            break
        res = corrida(tag, sis, usr, spent)
        if isinstance(res.get("error"), str) and res["error"].startswith("Parada"):
            print("PARADA: " + res["error"], flush=True)
            break


if __name__ == "__main__":
    main()
