"""F25b — fichas v2.2 de Kyshtym (pool y perfil de F23) con Opus 5.5 ×2 (fO1, fO2) y Sol ×2 (fS1, fS2), las cuatro a la vez
(el ThreadPool de F25a). Cada `call` sale de `ficha_caso.call_for(modelo)` (el camino de producción de F25b: Claude por
claude_helpers con streaming, max_tokens 100 000, effort medium, sin esquema; Sol high) con la respuesta cruda en
`<tag>/ficha_respuesta_cruda.json`. Prompts sin tocar. Topes: US$ 6 de Claude y US$ 1 de OpenAI (`costos_f25b.json`):
antes de cada llamada se reserva el peor caso con lock (Opus con los 100 000 de salida; Sol con 40 000, su salida
acotada); una sola facturación por llamada (cortada o JSON roto → se anota, no se reintenta).
Uso: python -I lab/hyperframes/f25b/f25b_corridas.py
"""
from __future__ import annotations

import json
import shutil
import sys
import threading
import time
import traceback
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LAB = Path(__file__).resolve().parent
sys.path[:0] = [str(LAB), str(ROOT), str(LAB.parent / "f23"), str(LAB.parent / "f25a")]
import f25a_corridas as f25a  # noqa: E402

KYS = "f18-kyshtym-mayak"
OPUS, SOL = "claude-opus-5-5", "gpt-6.1-sol"
FICHAS = (("fO1", OPUS), ("fO2", OPUS), ("fS1", SOL), ("fS2", SOL))
TOPES = {"claude": 6.00, "openai": 1.00}
SALIDA = {OPUS: 100_000, SOL: 40_000}
COSTOS = LAB / "costos_f25b.json"
_LOCK = threading.Lock()
_RES = {"claude": 0.0, "openai": 0.0}


class Parada(RuntimeError):
    pass


def _costos() -> dict:
    return f25a._j(COSTOS) or {"llamadas": [], "usd": {"claude": 0.0, "openai": 0.0}}


def _post_con_freno(tag: str, modelo: str, prompt_chars: int):
    if modelo.startswith("claude"):
        import claude_helpers as hx
    else:
        import gpt_helpers as hx
    hx.TIMEOUT_S = 3000
    prov = "claude" if modelo.startswith("claude") else "openai"
    pin, pout = hx.PRICES[modelo]
    worst = prompt_chars / 2.5 / 1e6 * pin + SALIDA[modelo] / 1e6 * pout
    n = {"posts": 0}

    def post(body: dict) -> dict:
        if n["posts"]:
            raise Parada(f"{tag}: la llamada ya facturó una vez (cortada o JSON roto): no se reintenta, se anota")
        with _LOCK:
            gastado = _costos()["usd"][prov]
            if gastado + _RES[prov] + worst > TOPES[prov]:
                raise Parada(f"tope {prov} ({tag}): gastado {gastado:.3f} + reservado {_RES[prov]:.3f} + peor caso "
                             f"{worst:.3f} > {TOPES[prov]:.2f}")
            _RES[prov] += worst
        n["posts"] += 1
        t0 = time.time()
        try:
            if not modelo.startswith("claude"):
                body["max_completion_tokens"] = SALIDA[modelo]
            r = hx._post(body)
        finally:
            with _LOCK:
                _RES[prov] -= worst
        u = r.get("usage") or {}
        stop = r.get("stop_reason") or ((r.get("choices") or [{}])[0].get("finish_reason"))
        reg = {"tag": tag, "modelo": modelo, "proveedor": prov, "max_tokens": body.get("max_tokens") or
               body.get("max_completion_tokens"), "effort": (body.get("output_config") or {}).get("effort") or
               body.get("reasoning_effort"), "esquema": bool((body.get("output_config") or {}).get("format") or
                                                              body.get("response_format", {}).get("json_schema")),
               "in": u.get("input_tokens") or u.get("prompt_tokens") or 0,
               "out": u.get("output_tokens") or u.get("completion_tokens") or 0, "stop": stop,
               "cortada": stop in ("max_tokens", "length"), "usd": round(hx.cost_of(modelo, u), 4),
               "segundos": round(time.time() - t0, 1)}
        with _LOCK:
            c = _costos()
            c["llamadas"].append(reg)
            for p in ("claude", "openai"):
                c["usd"][p] = round(sum(x["usd"] for x in c["llamadas"] if x["proveedor"] == p), 4)
            f25a._write(COSTOS, c)
        print(f"  [{tag}] in {reg['in']} · out {reg['out']} · stop {stop} · US$ {reg['usd']:.4f} · {reg['segundos']} s",
              flush=True)
        return r
    return post


def una_ficha(tag: str, modelo: str, titulo: str) -> dict:
    from researcher_steps import ficha_caso as fc
    d = LAB / tag
    if (d / "resultado.json").exists():
        return f25a._j(d / "resultado.json")
    d.mkdir(parents=True, exist_ok=True)
    raw_pool = (ROOT / "data" / "scripts" / "_steps" / KYS / "00_pool_v3.json").read_bytes()
    pool = json.loads(raw_pool.decode("utf-8"))
    sis, usr = fc.system(), fc.prompt(pool, titulo)
    t0 = time.time()
    res: dict = {"tag": tag, "modelo": modelo, "esfuerzo": fc.esfuerzo_de(modelo),
                 "prompt_md5": {"sistema": f25a._md5(sis), "usuario": f25a._md5(usr)}}
    try:
        call = fc.call_for(modelo, crudo=d / "ficha_respuesta_cruda.json",
                           post=_post_con_freno(tag, modelo, len(sis) + len(usr)))
        raw = fc.build(pool, titulo, call=call) or {}
        f25a._write(d / "ficha_crudo.json", raw)
        usd = round(sum(x["usd"] for x in _costos()["llamadas"] if x["tag"] == tag), 4)
        fc.save(KYS, raw, raw_pool, steps_dir=d / "_steps", title=titulo, tag=tag, out_dirs=[d], usd=usd, modelo=modelo)
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
                         f"problemas {m['problemas_chequeo']} · hechos {m['hechos_nivel_1']}/{m['hechos_nivel_2']} · "
                         f"citas {m['citas']} ({m['citas_verificadas']} verif.) · escenas {m['escenas']} · personas "
                         f"{m['personas']}") + f" · US$ {res['usd']} · {res['segundos']} s", flush=True)
    return res


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    titulo = f25a._kys().get("video_title") or "Kyshtym"
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=4) as ex:
        list(ex.map(lambda a: una_ficha(*a, titulo), FICHAS))
    c = _costos()
    c["pared_s"] = round(time.time() - t0, 1)
    f25a._write(COSTOS, c)
    print(f"tanda: Claude US$ {c['usd']['claude']:.4f} · OpenAI US$ {c['usd']['openai']:.4f} · pared {c['pared_s']} s",
          flush=True)


if __name__ == "__main__":
    main()
