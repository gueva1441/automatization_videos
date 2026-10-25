"""F26 §E (opcional) — ficha de Kyshtym (pool y perfil de F23) con Opus 5.5 ×2 (fO3, fO4) con la forma de los campos
DICHA EN EL PEDIDO: el prompt de producción (`ficha_caso.prompt`) con un párrafo al final de <tarea> que nombra, sección
por sección, los campos exactos (sacados de `ficha_caso.SCHEMA`), sin esquema forzado (claude_helpers: streaming, 100k,
medium, JSON sacado del texto). El sistema de la ficha, sin tocar. Nada cambia en producción: es para decidir después.
Tope US$ 4 de Claude (`costos_f26e.json`): antes de cada llamada se reserva el peor caso (100 000 de salida) con lock;
por eso van en fila (dos peores casos a la vez no entran en 4). Una sola facturación por llamada; respuesta cruda en
`<tag>/ficha_respuesta_cruda.json`. Tabla contra fS2 (Sol, F25a/F25b) en `TABLA_E.md`.
Uso: python -I lab/hyperframes/f26/e/f26e_fichas.py
"""
from __future__ import annotations

import json
import shutil
import sys
import threading
import time
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
LAB = Path(__file__).resolve().parent
HF = LAB.parent.parent
sys.path[:0] = [str(LAB), str(ROOT), str(HF / "f23"), str(HF / "f25a")]
import f25a_corridas as f25a  # noqa: E402

KYS = "f18-kyshtym-mayak"
OPUS = "claude-opus-5-5"
TAGS = ("fO3", "fO4")
TOPE = 4.00
SALIDA = 100_000
COSTOS = LAB / "costos_f26e.json"
_LOCK = threading.Lock()


class Parada(RuntimeError):
    pass


def _forma(sch: dict) -> str:
    """Los nombres de los campos de un nodo del esquema, como se escriben en JSON: {a, b: [{c, d}], e: {f}}."""
    t = sch.get("type")
    if t == "ARRAY":
        return f"[{_forma(sch['items'])}]"
    if t == "OBJECT":
        partes = []
        for k, v in sch["properties"].items():
            sub = _forma(v)
            partes.append(f"{k}: {sub}" if sub else k)
        return "{" + ", ".join(partes) + "}"
    return ""


def parrafo_campos() -> str:
    from researcher_steps import ficha_caso as fc
    secs = "; ".join(f"{k}: {_forma(v)}" for k, v in fc.SCHEMA["properties"].items())
    return ("Forma del JSON: un objeto con estas claves y, adentro, exactamente estos nombres de campo (ni otros nombres "
            "ni campos anidados nuevos; los ids van siempre en un campo `ids` que es una lista de ids del pool): "
            f"{secs}.")


def prompt_e(pool: dict, titulo: str) -> str:
    from researcher_steps import ficha_caso as fc
    p = fc.prompt(pool, titulo)
    assert p.endswith("</tarea>")
    return p[:-len("</tarea>")] + "\n\n" + parrafo_campos() + "</tarea>"


def _costos() -> dict:
    return f25a._j(COSTOS) or {"llamadas": [], "usd": 0.0}


def _post_con_freno(tag: str, prompt_chars: int):
    import claude_helpers as hx
    hx.TIMEOUT_S = 3000
    pin, pout = hx.PRICES[OPUS]
    worst = prompt_chars / 2.5 / 1e6 * pin + SALIDA / 1e6 * pout
    n = {"posts": 0}

    def post(body: dict) -> dict:
        if n["posts"]:
            raise Parada(f"{tag}: la llamada ya facturó una vez (cortada o JSON roto): no se reintenta, se anota")
        with _LOCK:
            gastado = _costos()["usd"]
            if gastado + worst > TOPE:
                raise Parada(f"tope ({tag}): gastado {gastado:.3f} + peor caso {worst:.3f} > {TOPE:.2f}")
        n["posts"] += 1
        t0 = time.time()
        r = hx._post(body)
        u = r.get("usage") or {}
        reg = {"tag": tag, "modelo": OPUS, "max_tokens": body.get("max_tokens"),
               "effort": (body.get("output_config") or {}).get("effort"),
               "esquema": bool((body.get("output_config") or {}).get("format")), "in": u.get("input_tokens") or 0,
               "out": u.get("output_tokens") or 0, "stop": r.get("stop_reason"),
               "cortada": r.get("stop_reason") == "max_tokens", "usd": round(hx.cost_of(OPUS, u), 4),
               "segundos": round(time.time() - t0, 1)}
        with _LOCK:
            c = _costos()
            c["llamadas"].append(reg)
            c["usd"] = round(sum(x["usd"] for x in c["llamadas"]), 4)
            f25a._write(COSTOS, c)
        print(f"  [{tag}] in {reg['in']} · out {reg['out']} · stop {reg['stop']} · US$ {reg['usd']:.4f} · "
              f"{reg['segundos']} s", flush=True)
        return r
    return post


def una_ficha(tag: str, titulo: str) -> dict:
    from researcher_steps import ficha_caso as fc
    d = LAB / tag
    if (d / "resultado.json").exists():
        return f25a._j(d / "resultado.json")
    d.mkdir(parents=True, exist_ok=True)
    raw_pool = (ROOT / "data" / "scripts" / "_steps" / KYS / "00_pool_v3.json").read_bytes()
    pool = json.loads(raw_pool.decode("utf-8"))
    sis, usr = fc.system(), prompt_e(pool, titulo)
    (d / "prompt_ficha.txt").write_text(f"===== SISTEMA (md5 {f25a._md5(sis)}) =====\n{sis}\n\n===== USUARIO (md5 "
                                        f"{f25a._md5(usr)}) =====\n{usr}\n", encoding="utf-8")
    t0 = time.time()
    res: dict = {"tag": tag, "modelo": OPUS, "esfuerzo": fc.esfuerzo_de(OPUS),
                 "prompt_md5": {"sistema": f25a._md5(sis), "usuario": f25a._md5(usr)}, "parrafo": parrafo_campos()}
    try:
        call = fc.call_for(OPUS, crudo=d / "ficha_respuesta_cruda.json", post=_post_con_freno(tag, len(sis) + len(usr)))
        raw = call(usr, system_instruction=sis, response_schema=fc.SCHEMA, description="ficha_caso") or {}
        f25a._write(d / "ficha_crudo.json", raw)
        usd = round(sum(x["usd"] for x in _costos()["llamadas"] if x["tag"] == tag), 4)
        fc.save(KYS, raw, raw_pool, steps_dir=d / "_steps", title=titulo, tag=tag, out_dirs=[d], usd=usd, modelo=OPUS)
        shutil.copy2(d / f"FICHA_{tag}.md", LAB / f"FICHA_{tag}.md")
        f = f25a._j(d / "ficha_caso.json")
        m = f25a.ficha_metricas(f)
        m["arcos"] = [{"nombre": h.get("nombre"), "arco": h.get("arco"), "citas_verificadas": h.get("citas_verificadas")}
                      for h in (f.get("historia") or {}).get("humanos_candidatos") or []]
        res["metricas"] = m
    except Exception as e:  # noqa: BLE001
        res["error"] = f"{type(e).__name__}: {e}"
        res["traceback"] = traceback.format_exc()[-1500:]
    ll = [x for x in _costos()["llamadas"] if x["tag"] == tag]
    res.update(usd=round(sum(x["usd"] for x in ll), 4), segundos=round(time.time() - t0, 1),
               cortada=any(x["cortada"] for x in ll), llamadas=ll)
    f25a._write(d / "resultado.json", res)
    m = res.get("metricas") or {}
    print(f"[{tag}] " + (f"ERROR {res['error'][:200]}" if res.get("error") else
                         f"problemas {m['problemas_chequeo']} · cifras {m.get('cifras')} · citas {m['citas']} "
                         f"({m['citas_verificadas']} verif.) · escenas {m['escenas']}") +
          f" · US$ {res['usd']} · {res['segundos']} s", flush=True)
    return res


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    titulo = f25a._kys().get("video_title") or "Kyshtym"
    t0 = time.time()
    for t in TAGS:
        try:
            una_ficha(t, titulo)
        except Parada as e:
            print(f"[{t}] PARADA {e}", flush=True)
    c = _costos()
    c["pared_s"] = round(time.time() - t0, 1)
    f25a._write(COSTOS, c)
    print(f"tanda E: Claude US$ {c['usd']:.4f} · pared {c['pared_s']} s", flush=True)


if __name__ == "__main__":
    main()
