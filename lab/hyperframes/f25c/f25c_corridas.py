"""F25c — escaleta f25-1 con Fable ×2 y guion v5.4 con Fable de cada una, en Kyshtym (ficha fS2 de F25a, pool F23) y en
Vajont (ficha de F24, pool de F24). Un proceso por tema: el perfil del caso es un global del proceso
(`research_v3.set_vocabulario`) y Kyshtym y Vajont no lo pueden compartir. Cada proceso corre sus 2 escaletas a la vez
y después sus 2 guiones a la vez; lanzando los dos procesos juntos quedan 4 + 4 en paralelo.
Modelos por el camino de producción: escaleta = `m01a_escaleta.DEFAULT_MODELO_ESCALETA` (Fable 5.1) con el effort de
la escaleta (`claude_helpers.ESFUERZO_POR_ETAPA`, medium) y el esquema de siempre; guion = `guion_v4.DEFAULT_MODELO_GUION`
con `guion_v4.ESFUERZO` (high). Las dos por claude_helpers: streaming, max_tokens 100 000; la respuesta cruda de cada
llamada se guarda en `<tag>/respuesta_*.json`.
Tope US$ 14 de Claude, 7 por tema (`costos_<tema>.json`): antes de cada llamada se reserva su peor caso con lock
(entrada ≈ caracteres / 2.5 tokens + RESERVA_OUT de salida; no los 100 000, que no dejarían correr nada) y al volver se
cobra el `usage`. Una sola facturación por llamada (cortada o JSON roto → se anota, no se reintenta).
Uso: python -I lab/hyperframes/f25c/f25c_corridas.py kyshtym|vajont escaleta|guion
"""
from __future__ import annotations

import copy
import hashlib
import json
import re
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
TOPE_TEMA = 7.00
RESERVA_OUT = {"escaleta": 40_000, "guion": 30_000}
TEMAS = {"kyshtym": {"ficha": HF / "f25a" / "fS2" / "ficha_caso.json", "tags": ("kE1", "kE2")},
         "vajont": {"ficha": HF / "f24" / "vajont" / "ficha.json", "tags": ("vE1", "vE2")}}
_LOCK = threading.Lock()
_RES = {"usd": 0.0}


class Parada(RuntimeError):
    pass


def _md5(s: str) -> str:
    return hashlib.md5(s.encode("utf-8")).hexdigest()


def _write(p: Path, obj) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=1, default=str), encoding="utf-8")


def _j(p: Path):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def _costos(tema: str) -> dict:
    return _j(LAB / f"costos_{tema}.json") or {"llamadas": [], "usd": 0.0, "etapas": {}}


def call_claude(tema: str, tag: str, etapa: str, modelo: str, effort: str):
    import claude_helpers as hx
    hx.TIMEOUT_S = 3000
    pin, pout = hx.PRICES[modelo]

    def _call(prompt, system_instruction=None, response_schema=None, thinking_budget=None, description=None):
        worst = (len(prompt) + len(system_instruction or "")) / 2.5 / 1e6 * pin + RESERVA_OUT[etapa] / 1e6 * pout
        n = {"posts": 0}

        def post(body: dict) -> dict:
            if n["posts"]:
                raise Parada(f"{tag}: la llamada ya facturó una vez (cortada o JSON roto): no se reintenta, se anota")
            with _LOCK:
                gastado = _costos(tema)["usd"]
                if gastado + _RES["usd"] + worst > TOPE_TEMA:
                    raise Parada(f"tope ({tag}, {description}): gastado {gastado:.3f} + reservado {_RES['usd']:.3f} + "
                                 f"peor caso {worst:.3f} > {TOPE_TEMA:.2f}")
                _RES["usd"] += worst
            n["posts"] += 1
            t0 = time.time()
            try:
                r = hx._post(body)
            finally:
                with _LOCK:
                    _RES["usd"] -= worst
            _write(LAB / tag / f"respuesta_{etapa}_{int(t0)}.json", r)
            u = r.get("usage") or {}
            reg = {"tag": tag, "etapa": etapa, "desc": description, "modelo": modelo, "effort": effort,
                   "max_tokens": body.get("max_tokens"), "stream": True,
                   "esquema": bool((body.get("output_config") or {}).get("format")), "in": u.get("input_tokens") or 0,
                   "out": u.get("output_tokens") or 0, "stop": r.get("stop_reason"),
                   "cortada": r.get("stop_reason") == "max_tokens", "usd": round(hx.cost_of(modelo, u), 4),
                   "segundos": round(time.time() - t0, 1)}
            with _LOCK:
                c = _costos(tema)
                c["llamadas"].append(reg)
                c["usd"] = round(sum(x["usd"] for x in c["llamadas"]), 4)
                _write(LAB / f"costos_{tema}.json", c)
            print(f"  [{tag}] {description}: in {reg['in']} · out {reg['out']} · {reg['stop']} · US$ {reg['usd']:.4f} · "
                  f"{reg['segundos']} s", flush=True)
            return r
        return hx.make_call(modelo, effort, post=post)(prompt, system_instruction=system_instruction,
                                                       response_schema=response_schema, description=description)
    return _call


def _topic(tema: str) -> dict:
    if tema == "kyshtym":
        import f23_corridas as f23
        return f23._topic()
    import f24_corridas as f24
    return f24._topic(f24.TEMAS["vajont"]["tid"], f24._seed("vajont")["seed_title"])


def _usd(tema: str, tag: str) -> float:
    return round(sum(x["usd"] for x in _costos(tema)["llamadas"] if x["tag"] == tag), 4)


def una_escaleta(tema: str, tag: str, topic: dict, ficha: dict) -> dict:
    import claude_helpers
    from f24_corridas import esc_metricas
    from script_engine import m01a_escaleta as ma
    d = LAB / tag
    if (d / "resultado.json").exists():
        return _j(d / "resultado.json")
    d.mkdir(parents=True, exist_ok=True)
    pool = topic["evidence_pool"]
    modelo, effort = ma.DEFAULT_MODELO_ESCALETA, claude_helpers.ESFUERZO_POR_ETAPA["escaleta"]
    p1 = ma.build_prompt_v2(topic, pool, ficha)
    (d / "prompt_escaleta.txt").write_text(f"===== SISTEMA (md5 {_md5(ma.SYSTEM_V2)}) =====\n{ma.SYSTEM_V2}\n\n===== "
                                           f"USUARIO, intento 1 (md5 {_md5(p1)}) =====\n{p1}\n", encoding="utf-8")
    log: list[str] = []
    crudos: list = []
    base = call_claude(tema, tag, "escaleta", modelo, effort)

    def call(*a, **k):
        r = base(*a, **k)
        crudos.append(r)
        return r
    t0 = time.time()
    res: dict = {"tag": tag, "tema": tema, "modelo": modelo, "effort": effort, "prompt_version": ma.PROMPT_VERSION_V2,
                 "prompt_md5": {"sistema": _md5(ma.SYSTEM_V2), "usuario_intento1": _md5(p1)}}
    try:
        esc = ma.generate_escaleta(topic, call=call, log=log, persist=False, ficha=ficha, columna=None)
        esc["_modelo"] = modelo
        _write(d / "escaleta.json", esc)
        (LAB / f"ESCALETA_{tag}.md").write_text(ma.to_markdown(esc, pool), encoding="utf-8")
        m = esc_metricas(esc, crudos[0] if crudos else None, pool, ficha)
        m["cierre_humano"] = esc.get("cierre_humano")
        res["metricas"] = m
    except Exception as e:  # noqa: BLE001
        res["error"] = f"{type(e).__name__}: {e}"
        res["log"] = log
    _write(d / "escaleta_crudos.json", crudos)
    res.update(usd=_usd(tema, tag), segundos=round(time.time() - t0, 1), log=log)
    _write(d / "resultado.json", res)
    m = res.get("metricas") or {}
    print(f"[{tag}] " + (f"ERROR {res['error'][:200]}" if res.get("error") else
                         f"beats {m.get('beats_por_cap')} · intentos "
                         f"{[len(x['bloqueantes'] or []) for x in m.get('intentos') or []]} · promesa «{m.get('promesa')}»")
          + f" · US$ {res['usd']} · {res['segundos']} s", flush=True)
    return res


def primera_frase(texto: str) -> str:
    m = re.match(r"\s*(.+?[.!?…»](?=\s|$))", texto or "", re.S)
    return (m.group(1) if m else (texto or "")[:200]).strip()


def un_guion(tema: str, tag: str, esc_tag: str, topic: dict, ficha: dict) -> dict:
    import f22b_corridas
    from f24_corridas import guion_metricas
    from script_engine import guion_v4 as g4
    from script_engine import m01b_guionista as mg
    d = LAB / tag
    if (d / "resultado.json").exists():
        return _j(d / "resultado.json")
    d.mkdir(parents=True, exist_ok=True)
    esc = _j(LAB / esc_tag / "escaleta.json")
    modelo = g4.DEFAULT_MODELO_GUION
    sis, usr = g4.system(), g4.prompt(topic, esc, ficha=ficha)
    (d / "prompt_guion.txt").write_text(f"===== SISTEMA (md5 {_md5(sis)}) =====\n{sis}\n\n===== USUARIO (md5 "
                                        f"{_md5(usr)}) =====\n{usr}\n", encoding="utf-8")
    log: list[str] = []
    t0 = time.time()
    res: dict = {"tag": tag, "tema": tema, "escaleta": esc_tag, "modelo": modelo, "effort": g4.ESFUERZO.get(modelo),
                 "version": g4.PROMPT_VERSION, "prompt_md5": {"sistema": _md5(sis), "usuario": _md5(usr)},
                 "nota_b": g4.nota_b(), "promesa_escaleta": esc.get("promesa_gancho")}
    try:
        g = g4.write(topic, esc, call=call_claude(tema, tag, "guion", modelo, g4.ESFUERZO.get(modelo)), ficha=ficha,
                     log=log)
        res["parrafos"] = g["parrafos"]
        res["bloqueantes"] = g4.bloqueantes(topic, esc, g["parrafos"], ficha=ficha)
        res["metricas"] = guion_metricas(topic, esc, g["parrafos"], ficha)
        res["metricas"]["largo"] = g4.largo_txt(res["metricas"]["palabras"])
        cap1 = next((c["narration"] for c in mg.caps_text(esc, g["parrafos"]) if c["chapter_number"] == 1), "")
        res["gancho_primera_frase"] = primera_frase(cap1)
        res["gancho_cap1"] = cap1
    except Exception as e:  # noqa: BLE001
        res["error"] = f"{type(e).__name__}: {e}"
        res["traceback"] = traceback.format_exc()[-1500:]
    res.update(usd=_usd(tema, tag), segundos=round(time.time() - t0, 1), log=log)
    _write(d / "resultado.json", res)
    if res.get("parrafos"):
        f22b_corridas.VERSION_NOMBRE.setdefault("f25-1", "v5.4")
        (LAB / f"NARRACION_{tag}.md").write_text(f22b_corridas.narracion(
            tag, esc, {**res, "costo": {"usd": res["usd"], "segundos": res["segundos"]},
                       "minutos": res["metricas"]["minutos"], "metricas": g4.metricas(topic, esc, res["parrafos"])},
            ficha, topic, modelo=modelo, version=g4.PROMPT_VERSION, tema=tema.capitalize(), fase="F25c",
            escaleta_txt=f"Escaleta {esc_tag} (f25-1, {esc.get('_modelo')})"), encoding="utf-8")
    m = res.get("metricas") or {}
    print(f"[{tag}] " + (f"ERROR {res['error'][:200]}" if res.get("error") else
                         f"{m['largo']} · bloqueantes {len(res['bloqueantes'])} · citas {m['citas']} · primera frase "
                         f"«{res['gancho_primera_frase']}»") + f" · US$ {res['usd']} · {res['segundos']} s", flush=True)
    return res


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    tema, etapa = sys.argv[1], sys.argv[2]
    if len(sys.argv) > 3:            # tope del tema (por defecto 7 = 14 / 2); la rehecha de vE2 usa lo que queda de 14
        global TOPE_TEMA
        TOPE_TEMA = float(sys.argv[3])
    topic = _topic(tema)
    ficha = _j(TEMAS[tema]["ficha"])
    tags = TEMAS[tema]["tags"]
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=2) as ex:
        if etapa == "escaleta":
            list(ex.map(lambda t: una_escaleta(tema, t, topic, copy.deepcopy(ficha)), tags))
        else:
            jobs = [("g" + t, t) for t in tags if (LAB / t / "escaleta.json").exists()]   # gkE2, gvE2 (sin choque)
            list(ex.map(lambda a: un_guion(tema, a[0], a[1], topic, copy.deepcopy(ficha)), jobs))
    c = _costos(tema)
    c["etapas"][etapa] = {"inicio": round(t0, 1), "fin": round(time.time(), 1), "pared_s": round(time.time() - t0, 1)}
    _write(LAB / f"costos_{tema}.json", c)
    print(f"[{tema} {etapa}] US$ {c['usd']:.4f} · pared {c['etapas'][etapa]['pared_s']} s", flush=True)


if __name__ == "__main__":
    main()
