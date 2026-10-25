"""F22b — cinco guiones de Ycuá sobre la MISMA escaleta de F22 (`lab/hyperframes/f22/escaleta_ycua_f22.json`), solo el
paso del guion, con la misma ficha v2 de F15b y el perfil del seed cargado:

    sol52a, sol52b   gpt-6.1-sol high, guion v5.2 (f22-1)
    sol51            gpt-6.1-sol high, guion v5.1 (f15b-1)  — el pedido dice system("f15-1"), que en guion_v4 es el v5;
                                                              se corre el v5.1, que es lo que dicen la etiqueta y el nombre
    opus52a, opus52b claude-opus-5-5 effort high, guion v5.2 (f22-1)

Tope US$ 4.00 entre las dos APIs (costos_f22b.json, con la llamada de prueba de la llave): antes de cada llamada, lo
gastado + el peor caso (`max_tokens` / `max_completion_tokens` = 24 000) no puede pasar el tope; cada llamada factura una
sola vez. Bloqueantes con `guion_v4.bloqueantes(..., version=...)` (F22b: acepta las cifras de lo que recibió el
guionista). Sin reparación (como F16–F22). Cada corrida se saltea si su salida ya existe.
Salidas: guion_ycua_f22b_<tag>.json + NARRACION_ycua_f22b_<tag>.md.
Uso: python -I lab/hyperframes/f22b/f22b_corridas.py [sol52a sol52b sol51 opus52a opus52b]
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
F22 = LAB.parent / "f22"
sys.path.insert(0, str(LAB))
sys.path.insert(1, str(ROOT))
sys.path.insert(2, str(F22))
sys.path.insert(3, str(LAB.parent / "f13"))

TOPE = 4.00
MAX_OUT = 24000
COSTOS = LAB / "costos_f22b.json"
CORRIDAS = {"sol52a": ("gpt-6.1-sol", "f22-1"), "sol52b": ("gpt-6.1-sol", "f22-1"), "sol51": ("gpt-6.1-sol", "f15b-1"),
            "opus52a": ("claude-opus-5-5", "f22-1"), "opus52b": ("claude-opus-5-5", "f22-1")}
VERSION_NOMBRE = {"f22-1": "v5.2", "f15b-1": "v5.1"}


class Parada(RuntimeError):
    pass


def _md5(s: str) -> str:
    return hashlib.md5(s.encode("utf-8")).hexdigest()


def _write(p: Path, obj) -> None:
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding="utf-8")


def _costos() -> dict:
    if COSTOS.exists():
        return json.loads(COSTOS.read_text(encoding="utf-8"))
    c = {"etapas": [], "usd_total": 0.0}
    prueba = LAB / "prueba_llave.json"
    if prueba.exists():                                     # la llamada de 10 tokens (no pasó por cost_tracker)
        p = json.loads(prueba.read_text(encoding="utf-8"))
        c["etapas"].append({"corrida": "prueba_llave", "modelo": p["modelo"], "usd": p["usd"], "segundos": 0,
                            "llamadas": [{"servicio": "Anthropic claude-opus-5-5", "desc": "prueba 10 tokens",
                                          "in": p["usage"]["input_tokens"], "out": p["usage"]["output_tokens"],
                                          "usd": p["usd"]}]})
        c["usd_total"] = p["usd"]
    return c


def _gastado() -> float:
    return sum(x["usd"] for x in _costos()["etapas"])


def _add_cost(tag: str, modelo: str, rep, t0: float) -> dict:
    c = _costos()
    costo = {"corrida": tag, "modelo": modelo, "usd": round(getattr(rep, "total_cost", 0.0) or 0.0, 4),
             "segundos": round(time.time() - t0, 1),
             "llamadas": [{"servicio": e.service, "desc": e.description, "in": e.tokens_in, "out": e.tokens_out,
                           "thinking": e.tokens_thinking, "usd": round(e.total_cost, 4)}
                          for e in (getattr(rep, "entries", None) or [])]}
    c["etapas"].append(costo)
    c["usd_total"] = round(sum(x["usd"] for x in c["etapas"]), 4)
    _write(COSTOS, c)
    print(f"  [{tag}] US$ {costo['usd']:.4f} · {costo['segundos']:.0f} s · tanda US$ {c['usd_total']:.4f}", flush=True)
    return costo


def make_call(modelo: str):
    """Freno antes de cada llamada (lo gastado + el peor caso ≤ TOPE) y UNA facturación por llamada."""
    from cost_tracker import cost_tracker
    if modelo.startswith("claude"):
        import claude_helpers as hx
        pin, pout = hx.PRICES[modelo]
        hx.TIMEOUT_S = 1800
    else:
        import gpt_helpers as hx
        pin, pout = hx.PRICES[modelo]
        hx.TIMEOUT_S = 1800
    total0 = _gastado()

    def _call(prompt, system_instruction=None, response_schema=None, thinking_budget=None, description=None):
        cur = cost_tracker.current_video.total_cost if cost_tracker.current_video else 0.0
        worst = (len(prompt) + len(system_instruction or "")) / 3 / 1e6 * pin + MAX_OUT / 1e6 * pout
        if total0 + cur + worst > TOPE:
            raise Parada(f"tope antes de «{description}»: US$ {total0 + cur:.3f} + peor caso {worst:.3f} > {TOPE:.2f}")
        n = {"posts": 0}

        def post(body: dict) -> dict:
            if n["posts"]:
                raise Parada("la llamada ya facturó una vez (JSON roto o cortado): no hay reintento por el tope")
            body["max_tokens" if modelo.startswith("claude") else "max_completion_tokens"] = MAX_OUT
            n["posts"] += 1
            return hx._post(body)
        if modelo.startswith("claude"):
            return hx.make_call(modelo, "high", post=post)(prompt, system_instruction=system_instruction,
                                                           response_schema=response_schema, description=description)
        return hx.make_call(modelo, "high", post=post)(prompt, system_instruction=system_instruction,
                                                       response_schema=response_schema, description=description)
    return _call


def correr(tag: str) -> None:
    import f22_corridas as f22
    from cost_tracker import cost_tracker
    from f13_corridas import PALABRAS_POR_SEG, narracion_md, repeticion_interna
    from script_engine import guion_v4 as g4
    from script_engine import m01b_guionista as mg
    out = LAB / f"guion_ycua_f22b_{tag}.json"
    if out.exists():
        print(f"[{tag}] ya existe: se saltea", flush=True)
        return
    modelo, version = CORRIDAS[tag]
    esc = json.loads((F22 / "escaleta_ycua_f22.json").read_text(encoding="utf-8"))
    ficha, topic = f22._ficha("ycua"), f22._topic("ycua")
    sis, usr = g4.system(version), g4.prompt(topic, esc, ficha=ficha, version=version)
    (LAB / f"prompt_ycua_f22b_{tag}.txt").write_text(
        f"===== SISTEMA (md5 {_md5(sis)}) =====\n{sis}\n\n===== USUARIO (md5 {_md5(usr)}) =====\n{usr}\n", encoding="utf-8")
    res: dict = {"tag": tag, "tema": "ycua", "modelo": modelo, "esfuerzo": "high", "version": version,
                 "escaleta": "lab/hyperframes/f22/escaleta_ycua_f22.json", "max_tokens": MAX_OUT,
                 "prompt_md5": {"sistema": _md5(sis), "usuario": _md5(usr)}, "nota_b": g4.nota_b()}
    cost_tracker.start_video(f"f8s1-ycua-bolanos-f22b-{tag}")
    t0 = time.time()
    try:
        g = g4.write(topic, esc, call=make_call(modelo), ficha=ficha, version=version)
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
    res["costo"] = _add_cost(tag, modelo, rep, t0)
    _write(out, res)
    if res.get("parrafos"):
        (LAB / f"NARRACION_ycua_f22b_{tag}.md").write_text(narracion(tag, esc, res, ficha, topic), encoding="utf-8")
    m = res.get("metricas") or {}
    print(f"[{tag}] " + (f"ERROR {res['error']} · " if res.get("error") else "")
          + (f"{m['palabras']} palabras ≈ {res['minutos']} min · bloqueantes {len(res['bloqueantes'])} · citas "
             f"{m['citas']}" if m else ""), flush=True)
    if res.get("error") and "Parada" in res["error"]:
        raise Parada(res["error"])


def vista(esc: dict, res: dict, ficha: dict, topic: dict) -> dict:
    import f22_compara as fc2
    return fc2.guion_view("ycua", res, esc, ficha, topic["evidence_pool"])


def narracion(tag: str, esc: dict, res: dict, ficha: dict, topic: dict, *, modelo: str | None = None,
              version: str | None = None, tema: str = "Ycuá", fase: str = "F22b",
              escaleta_txt: str = "Misma escaleta de F22 (`escaleta_ycua_f22.json`)") -> str:
    """F22c reusa la página con `modelo`, `version`, `tema`, `fase` y `escaleta_txt` (por defecto, lo de F22b)."""
    v = vista(esc, res, ficha, topic)
    modelo, version = (modelo, version) if modelo else CORRIDAS[tag]
    L = [f"# Narración {tema} — {fase} `{tag}` ({modelo} high, guion {VERSION_NOMBRE[version]} `{version}`)", "",
         f"{escaleta_txt} · sistema md5 `{res['prompt_md5']['sistema'][:8]}` · usuario "
         f"md5 `{res['prompt_md5']['usuario'][:8]}` · US$ {res['costo']['usd']:.4f} · {res['costo']['segundos']:.0f} s", "",
         f"**{v['palabras']} palabras ≈ {res['minutos']} min** · bloqueantes **{v['bloqueantes']}** · citas "
         f"{res['metricas']['citas']} · personas con nombre {len(v['personas_total'])} · cierre "
         f"{res['metricas']['cierre']}", "",
         "| cap | palabras | personas con nombre | citas | bloqueantes |", "|---|---|---|---|---|"]
    for n in range(1, 8):
        c = v["por_cap"].get(n) or {}
        L.append(f"| {n} | {c.get('palabras')} | {', '.join(c.get('personas') or []) or '—'} | {c.get('citas')} | "
                 f"{c.get('bloqueantes')} |")
    if v["bloqueantes_lista"]:
        L += ["", "**Bloqueantes:**"] + [f"- ({b['codigo']}) cap {b.get('cap')}, beat {b.get('beat')}: {b['motivo']} — "
                                         f"«{str(b.get('frase'))[:160]}»" for b in v["bloqueantes_lista"]]
    L.append("")
    beats = {b["n"]: b for b in esc["beats"]}
    cap = None
    for p in res["parrafos"]:
        if p["cap"] != cap:
            cap = p["cap"]
            L += [f"## Cap {cap}", ""]
        L += [f"<sub>beat {p['beat']} · {beats.get(p['beat'], {}).get('funcion')}</sub>", "", p["texto"], ""]
    return "\n".join(L)


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    tags = [a for a in sys.argv[1:] if a in CORRIDAS] or list(CORRIDAS)
    for t in tags:
        try:
            correr(t)
        except Parada as x:
            print(f"PARADA ({t}): {x}", flush=True)
            break
    print(f"tanda US$ {_gastado():.4f}", flush=True)


if __name__ == "__main__":
    main()
