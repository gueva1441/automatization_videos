"""F25a — ¿qué modelo para la ficha y la escaleta? Kyshtym, pool y perfil de F23, sin research. Cero cambios de prompts y
de chequeos; solo este runner, que corre cada etapa EN PARALELO (ThreadPool, 4 workers).

    1  ficha v2.2: fS1, fS2 (gpt-6.1-sol high) y fF1, fF2 (claude-fable-5-1 high, max_tokens 32 000), las cuatro a la vez.
    2  escaleta f24-1 sin columna sobre la mejor ficha de Sol y la mejor de Fable (menos problemas del chequeo; empate →
       más citas verificadas): eS1, eS2 (ficha Sol) con Sol y eF1, eF2 (ficha Fable) con Fable, a la vez.
    3  guion v5.3 con Fable de las cuatro escaletas, a la vez (gS1, gS2, gF1, gF2).
Topes: US$ 15 de Claude y US$ 4 de OpenAI (`costos_f25a.json`). Antes de cada llamada se reserva su peor caso
(entrada ≈ caracteres / 2.5 tokens + la salida acotada) contra lo gastado y lo reservado por los otros hilos; al volver,
se cobra lo que dice `usage`. Una sola facturación por llamada: si el modelo se corta por max_tokens (o el JSON viene
roto), no se reintenta y se anota. El costo por llamada sale de `usage` × PRICES (`cost_of` de cada helper), no del
cost_tracker (que es uno solo para todos los hilos). La ficha se guarda en `f25a/<tag>/` (nunca en `_steps`).
Uso: python -I lab/hyperframes/f25a/f25a_corridas.py [1 2 3]
"""
from __future__ import annotations

import hashlib
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
HF = LAB.parent
sys.path[:0] = [str(LAB), str(ROOT), str(HF / "f13"), str(HF / "f22"), str(HF / "f22b"), str(HF / "f23"), str(HF / "f24")]
KYS = "f18-kyshtym-mayak"
SOL, FABLE = "gpt-6.1-sol", "claude-fable-5-1"
TOPES = {"claude": 15.00, "openai": 4.00}
# F25a (regla de Omar): Claude con claude_helpers.MAX_TOKENS (100 000, streaming) y el effort de su etapa
# (claude_helpers.ESFUERZO_POR_ETAPA: high solo en el guion); la ficha sin esquema forzado (claude_helpers.SALIDA_GRANDE).
# La primera tanda de Fable (fF1/fF2 cortadas, eF1/eF2, gF1/gF2) corrió antes de la regla: max_tokens 32 000, high.
import claude_helpers as _ch  # noqa: E402
MAX_OUT = {(SOL, "ficha"): 40000, (SOL, "escaleta"): 16000, (FABLE, "ficha"): _ch.MAX_TOKENS,
           (FABLE, "escaleta"): _ch.MAX_TOKENS, (FABLE, "guion"): _ch.MAX_TOKENS}
ESFUERZO = {SOL: {"ficha": "high", "escaleta": "high"}, FABLE: _ch.ESFUERZO_POR_ETAPA}
# peor caso para el freno de Claude: la salida que se reserva (no los 100 000 enteros, que bloquearían todo con el tope
# de US$ 15); si la llamada se pasa, lo cobrado es el `usage` real y el freno de la siguiente lo ve
RESERVA_OUT = {(FABLE, "ficha"): 60000}
COSTOS = LAB / "costos_f25a.json"
WORKERS = 4
_LOCK = threading.Lock()
_RES: dict[str, float] = {"claude": 0.0, "openai": 0.0}      # reservado (en vuelo)


class Parada(RuntimeError):
    pass


def _md5(s: str) -> str:
    return hashlib.md5(s.encode("utf-8")).hexdigest()


def _write(p: Path, obj) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=1, default=str), encoding="utf-8")


def _j(p: Path):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def _prov(modelo: str) -> str:
    return "claude" if modelo.startswith("claude") else "openai"


def _costos() -> dict:
    return _j(COSTOS) or {"llamadas": [], "etapas": {}, "usd": {"claude": 0.0, "openai": 0.0}}


def _cobrar(reg: dict) -> None:
    with _LOCK:
        c = _costos()
        c["llamadas"].append(reg)
        for p in ("claude", "openai"):
            c["usd"][p] = round(sum(x["usd"] for x in c["llamadas"] if x["proveedor"] == p), 4)
        _write(COSTOS, c)


def llm_call(tag: str, etapa: str, modelo: str, log: list):
    """effort high, salida acotada; reserva del peor caso con lock; una sola facturación; costo desde `usage`."""
    if modelo.startswith("claude"):
        import claude_helpers as hx
    else:
        import gpt_helpers as hx
    hx.TIMEOUT_S = 3000
    prov = _prov(modelo)
    pin, pout = hx.PRICES[modelo]
    max_out = MAX_OUT[(modelo, etapa)]

    def _call(prompt, system_instruction=None, response_schema=None, thinking_budget=None, description=None):
        worst = (len(prompt) + len(system_instruction or "")) / 2.5 / 1e6 * pin             + RESERVA_OUT.get((modelo, etapa), max_out) / 1e6 * pout
        with _LOCK:
            gastado = _costos()["usd"][prov]
            if gastado + _RES[prov] + worst > TOPES[prov]:
                raise Parada(f"tope {prov} antes de «{description}» ({tag}): gastado {gastado:.3f} + reservado "
                             f"{_RES[prov]:.3f} + peor caso {worst:.3f} > {TOPES[prov]:.2f}")
            _RES[prov] += worst
        n = {"posts": 0}
        t0 = time.time()

        def post(body: dict) -> dict:
            if n["posts"]:
                raise Parada(f"{tag}: la llamada ya facturó una vez (cortada por max_tokens o JSON roto): no se "
                             "reintenta, se anota")
            body["max_tokens" if modelo.startswith("claude") else "max_completion_tokens"] = max_out
            n["posts"] += 1
            r = hx._post(body)
            u = r.get("usage") or {}
            stop = r.get("stop_reason") or ((r.get("choices") or [{}])[0].get("finish_reason"))
            reg = {"tag": tag, "etapa": etapa, "modelo": modelo, "proveedor": prov, "desc": description,
                   "in": u.get("input_tokens") or u.get("prompt_tokens") or 0,
                   "out": u.get("output_tokens") or u.get("completion_tokens") or 0, "stop": stop,
                   "cortada": stop in ("max_tokens", "length"), "usd": round(hx.cost_of(modelo, u), 4),
                   "segundos": round(time.time() - t0, 1)}
            _cobrar(reg)
            crudo = LAB / tag / f"respuesta_{etapa}_{int(t0)}.json"   # la respuesta tal cual (que no se pierda una)
            _write(crudo, r)
            log.append(f"  [{tag}] {description}: in {reg['in']} · out {reg['out']} · stop {stop} · US$ {reg['usd']:.4f}"
                       f" · {reg['segundos']} s")
            return r
        try:
            return hx.make_call(modelo, ESFUERZO[modelo][etapa], post=post)(
                prompt, system_instruction=system_instruction, response_schema=response_schema, description=description)
        finally:
            with _LOCK:
                _RES[prov] -= worst
    return _call


def _usd(tag: str) -> float:
    return round(sum(x["usd"] for x in _costos()["llamadas"] if x["tag"] == tag), 4)


def _cortes(tag: str) -> list[str]:
    return [x["desc"] for x in _costos()["llamadas"] if x["tag"] == tag and x["cortada"]]


def _kys():
    import f23_corridas as f23
    return f23._topic()


# ═══════════════════════════════════════════════════════════════
#  1 — fichas
# ═══════════════════════════════════════════════════════════════

FICHAS = (("fS1", SOL), ("fS2", SOL), ("fF1", FABLE), ("fF2", FABLE))


def ficha_metricas(f: dict) -> dict:
    """Citas verificadas = las citas de la ficha cuyo id del pool (Q##) tiene `verificacion.estado == "verificada"`
    (el campo `verificacion` de la ficha es texto libre del modelo)."""
    from researcher_steps import ficha_caso as fc
    pool = _j(ROOT / "data" / "scripts" / "_steps" / KYS / "00_pool_v3.json")
    ver = {q["id"] for q in pool.get("citas") or [] if (q.get("verificacion") or {}).get("estado") == "verificada"}
    h = f.get("historia") or {}
    return {"problemas_chequeo": f.get("sacados"), "conteos": fc.counts(f),
            "hechos_nivel_1": sum(1 for x in f.get("hechos") or [] if str(x.get("nivel")) == "1"),
            "hechos_nivel_2": sum(1 for x in f.get("hechos") or [] if str(x.get("nivel")) == "2"),
            "citas": len(f.get("citas") or []),
            "citas_verificadas": sum(1 for x in f.get("citas") or [] if set(x.get("ids") or []) & ver),
            "escenas": len(f.get("escenas") or []),
            "humanos_candidatos": [x.get("nombre") for x in h.get("humanos_candidatos") or f.get("humanos_candidatos") or []],
            "personas": len(f.get("personas") or [])}


def una_ficha(tag: str, modelo: str, topic: dict) -> dict:
    from researcher_steps import ficha_caso as fc
    d = LAB / tag
    if (d / "resultado.json").exists():
        res = _j(d / "resultado.json")
        if (d / "ficha_caso.json").exists():          # métricas recalculadas sin API (la de citas verificadas)
            res["metricas"] = ficha_metricas(_j(d / "ficha_caso.json"))
            _write(d / "resultado.json", res)
        return res
    d.mkdir(parents=True, exist_ok=True)
    raw_pool =(ROOT / "data" / "scripts" / "_steps" / KYS / "00_pool_v3.json").read_bytes()
    pool, titulo = json.loads(raw_pool.decode("utf-8")), topic.get("video_title") or "Kyshtym"
    log: list[str] = []
    t0 = time.time()
    res = {"tag": tag, "modelo": modelo, "prompt_md5": {"sistema": _md5(fc.system()),
                                                         "usuario": _md5(fc.prompt(pool, titulo))}}
    try:
        raw = fc.build(pool, titulo, call=llm_call(tag, "ficha", modelo, log)) or {}
        _write(d / "ficha_crudo.json", raw)
        fc.save(KYS, raw, raw_pool, steps_dir=d / "_steps", title=titulo, tag=tag, out_dirs=[d], usd=_usd(tag))
        f = _j(d / "ficha_caso.json")
        f["modelo"] = modelo
        _write(d / "ficha_caso.json", f)
        shutil.copy2(d / f"FICHA_{tag}.md", LAB / f"FICHA_{tag}.md")
        res["metricas"] = ficha_metricas(f)
    except Exception as e:  # noqa: BLE001
        res["error"] = f"{type(e).__name__}: {e}"
        res["traceback"] = traceback.format_exc()[-1500:]
    res.update(usd=_usd(tag), segundos=round(time.time() - t0, 1), cortada=_cortes(tag), log=log)
    _write(d / "resultado.json", res)
    print(f"[{tag}] {'ERROR ' + res['error'][:150] if res.get('error') else res['metricas']} · US$ {res['usd']} · "
          f"{res['segundos']} s", flush=True)
    return res


def mejor(res: list[dict]) -> str | None:
    ok = [r for r in res if r.get("metricas")]
    if not ok:
        return None
    return min(ok, key=lambda r: (r["metricas"]["problemas_chequeo"], -r["metricas"]["citas_verificadas"], r["tag"]))["tag"]


# ═══════════════════════════════════════════════════════════════
#  2 — escaletas · 3 — guiones
# ═══════════════════════════════════════════════════════════════

def una_escaleta(tag: str, modelo: str, ficha_tag: str, topic: dict) -> dict:
    from f24_corridas import esc_metricas
    from script_engine import m01a_escaleta as ma
    d = LAB / tag
    if (d / "resultado.json").exists():
        return _j(d / "resultado.json")
    d.mkdir(parents=True, exist_ok=True)
    ficha = _j(LAB / ficha_tag / "ficha_caso.json")
    pool = topic["evidence_pool"]
    p1 = ma.build_prompt_v2(topic, pool, ficha)
    (d / "prompt_escaleta.txt").write_text(f"===== SISTEMA (md5 {_md5(ma.SYSTEM_V2)}) =====\n{ma.SYSTEM_V2}\n\n===== "
                                           f"USUARIO, intento 1 (md5 {_md5(p1)}) =====\n{p1}\n", encoding="utf-8")
    log: list[str] = []
    crudos: list = []
    base = llm_call(tag, "escaleta", modelo, log)

    def call(*a, **k):
        r = base(*a, **k)
        crudos.append(r)
        return r
    t0 = time.time()
    res: dict = {"tag": tag, "modelo": modelo, "ficha": ficha_tag, "prompt_md5": {"sistema": _md5(ma.SYSTEM_V2),
                                                                                "usuario_intento1": _md5(p1)}}
    try:
        esc = ma.generate_escaleta(topic, call=call, log=log, persist=False, ficha=ficha, columna=None)
        esc["_modelo"], esc["_ficha"] = modelo, ficha_tag
        _write(d / "escaleta.json", esc)
        (LAB / f"ESCALETA_{tag}.md").write_text(ma.to_markdown(esc, pool), encoding="utf-8")
        m = esc_metricas(esc, crudos[0] if crudos else None, pool, ficha)
        m["cierre_humano"] = esc.get("cierre_humano")
        res["metricas"] = m
    except Exception as e:  # noqa: BLE001
        res["error"] = f"{type(e).__name__}: {e}"
        if crudos:
            res["metricas_pasada1"] = esc_metricas({"beats": []}, crudos[0], pool, ficha)
    _write(d / "escaleta_crudos.json", crudos)
    res.update(usd=_usd(tag), segundos=round(time.time() - t0, 1), cortada=_cortes(tag), log=log)
    _write(d / "resultado.json", res)
    m = res.get("metricas") or {}
    print(f"[{tag}] " + (f"ERROR {res['error'][:150]}" if res.get("error") else
                         f"beats {m.get('beats_por_cap')} · intentos {[len(x['bloqueantes'] or []) for x in m.get('intentos') or []]}")
          + f" · US$ {res['usd']} · {res['segundos']} s", flush=True)
    return res


def un_guion(tag: str, esc_tag: str, topic: dict) -> dict:
    import f22b_corridas
    from f24_corridas import guion_metricas
    from script_engine import guion_v4 as g4
    d = LAB / tag
    if (d / "resultado.json").exists():
        return _j(d / "resultado.json")
    d.mkdir(parents=True, exist_ok=True)
    esc = _j(LAB / esc_tag / "escaleta.json")
    ficha = _j(LAB / esc["_ficha"] / "ficha_caso.json")
    sis, usr = g4.system(), g4.prompt(topic, esc, ficha=ficha)
    log: list[str] = []
    t0 = time.time()
    res: dict = {"tag": tag, "escaleta": esc_tag, "ficha": esc["_ficha"], "modelo": FABLE, "version": g4.PROMPT_VERSION,
                 "prompt_md5": {"sistema": _md5(sis), "usuario": _md5(usr)}, "nota_b": g4.nota_b()}
    try:
        g = g4.write(topic, esc, call=llm_call(tag, "guion", FABLE, log), ficha=ficha, log=log)
        res["parrafos"] = g["parrafos"]
        res["bloqueantes"] = g4.bloqueantes(topic, esc, g["parrafos"], ficha=ficha)
        res["metricas"] = guion_metricas(topic, esc, g["parrafos"], ficha)
    except Exception as e:  # noqa: BLE001
        res["error"] = f"{type(e).__name__}: {e}"
        res["traceback"] = traceback.format_exc()[-1500:]
    res.update(usd=_usd(tag), segundos=round(time.time() - t0, 1), cortada=_cortes(tag), log=log)
    _write(d / "resultado.json", res)
    if res.get("parrafos"):
        f22b_corridas.VERSION_NOMBRE.setdefault("f23-1", "v5.3")
        (LAB / f"NARRACION_{tag}.md").write_text(f22b_corridas.narracion(
            tag, esc, {**res, "costo": {"usd": res["usd"], "segundos": res["segundos"]},
                       "minutos": res["metricas"]["minutos"], "metricas": g4.metricas(topic, esc, res["parrafos"])},
            ficha, topic, modelo=FABLE, version=g4.PROMPT_VERSION, tema="Kyshtym", fase="F25a",
            escaleta_txt=f"Escaleta {esc_tag} ({esc['_modelo']}) sobre la ficha {esc['_ficha']}"), encoding="utf-8")
    m = res.get("metricas") or {}
    print(f"[{tag}] " + (f"ERROR {res['error'][:150]}" if res.get("error") else
                         f"{m['palabras']} palabras · bloqueantes {len(res['bloqueantes'])} · citas {m['citas']} · "
                         f"por cap {m['palabras_por_cap']}") + f" · US$ {res['usd']} · {res['segundos']} s", flush=True)
    return res


def _pool_run(jobs: list) -> list:
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs = [ex.submit(fn, *args) for fn, *args in jobs]
        return [f.result() for f in futs]


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    etapas = [a for a in sys.argv[1:] if a in ("1", "2", "3")] or ["1", "2", "3"]
    topic = _kys()
    t0 = time.time()
    if "1" in etapas:
        t = time.time()
        res = _pool_run([(una_ficha, tag, m, topic) for tag, m in FICHAS])
        c = _costos()
        c["etapas"]["1"] = {"pared_s": round(time.time() - t, 1), "mejor_sol": mejor([r for r in res if r["modelo"] == SOL]),
                            "mejor_fable": mejor([r for r in res if r["modelo"] == FABLE])}
        _write(COSTOS, c)
        print(f"[etapa 1] {c['etapas']['1']}", flush=True)
    if "2" in etapas:
        e1 = _costos()["etapas"].get("1") or {}
        jobs = []
        if e1.get("mejor_sol"):
            jobs += [(una_escaleta, "eS1", SOL, e1["mejor_sol"], topic), (una_escaleta, "eS2", SOL, e1["mejor_sol"], topic)]
        # sin ficha de Fable (las dos cortadas por max_tokens), eF1/eF2 van con Fable sobre la mejor ficha de Sol:
        # así la escaleta se compara con la misma entrada
        ff = e1.get("mejor_fable") or e1.get("mejor_sol")
        if ff:
            jobs += [(una_escaleta, "eF1", FABLE, ff, topic), (una_escaleta, "eF2", FABLE, ff, topic)]
        t = time.time()
        _pool_run(jobs)
        c = _costos()
        c["etapas"]["2"] = {"pared_s": round(time.time() - t, 1)}
        _write(COSTOS, c)
    if "3" in etapas:
        jobs = [(un_guion, "g" + e[1:], e, topic) for e in ("eS1", "eS2", "eF1", "eF2")
                if (LAB / e / "escaleta.json").exists()]
        t = time.time()
        _pool_run(jobs)
        c = _costos()
        c["etapas"]["3"] = {"pared_s": round(time.time() - t, 1)}
        _write(COSTOS, c)
    c = _costos()
    c["pared_total_s"] = round((c.get("pared_total_s") or 0) + time.time() - t0, 1)
    _write(COSTOS, c)
    print(f"tanda: Claude US$ {c['usd']['claude']:.4f} · OpenAI US$ {c['usd']['openai']:.4f} · pared "
          f"{c['pared_total_s']} s", flush=True)


if __name__ == "__main__":
    main()
