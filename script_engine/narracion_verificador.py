"""
script_engine/narracion_verificador.py — F66 (F63 B a producción; DECISIONES 2026-10-31 16:13): el verificador de hechos de la
narración. Una llamada por cap, todas a la vez, a Claude Opus 5.5 medium, con el archivo del caso entero (cada dato con
su `contexto_fuente`) y las versiones en disputa: por oración separa las afirmaciones de hecho y dice si están
respaldadas, si contradicen el archivo o si no tienen respaldo. Encuentra lo que ningún filtro de palabras ve (la voz
dice lo contrario del archivo). No corrige nada: `fase1_5.run_verificacion` corrige lo que contradice.

    SYSTEM_B, FORMATO_B, archivo_b, user_b   literales de lab/hyperframes/f63/etapa_b_verificador.py (md5 del SYSTEM
                                             ce31cc515a077d74da72479e9693296e, candado en test_module_f66).
    verificar_caps(caps, archivo, disputas, *, post=None, log=None)
                                             las llamadas en paralelo, 2 intentos totales por cap (excepción de API o sin
                                             JSON, como llamar_modelo del lab); {por_cap, contradice, sin_respaldo, usd,
                                             segundos}. Un cap que falla dos veces queda con `error` y sin afirmaciones:
                                             no frena la cadena.
Modelo y effort: los de F63 B (constantes abajo). El costo se informa con hx.cost_of y hx._track(…, "m01b_verificador").
"""
from __future__ import annotations

import json
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable

MODELO = "claude-opus-5-5"     # F63 B (medido) · DECISIONES 2026-10-31 14:20: el mismo de pantalla_verificador
EFFORT = "medium"
INTENTOS = 2                   # como llamar_modelo de F63: excepción de API o sin JSON → un reintento de la misma llamada

SYSTEM_B = """Sos el verificador de hechos de un documental de historia en español. Recibís las oraciones numeradas de un capítulo y el archivo del caso: cada dato con su id, su texto, su fecha, su fuente y, en `contexto_fuente`, el fragmento original de la fuente; y las versiones en disputa del caso.

Para cada oración, separá las afirmaciones de hecho que quien escucha va a tomar como verdad: quién, qué, cuándo, cuánto, dónde, cómo era algo, quién dijo qué y en qué momento. No listes preguntas, transiciones ni frases que no afirman un hecho. No juzgues el estilo.

Para cada afirmación, un estado:
- respaldada: un dato del archivo la sostiene (poné su id);
- contradice: un dato del archivo, o su contexto_fuente, dice otra cosa (poné el id y el fragmento literal que lo muestra);
- sin_respaldo: nada del archivo la sostiene ni la contradice.
Una cita atribuida a una fecha o a un hecho distinto del que dice el archivo es «contradice». Si el archivo trae versiones en disputa y la oración da una sola como cierta, es «contradice» con las dos versiones en el fragmento.

Devolvé solo JSON."""

FORMATO_B = ('{"cap": "ch01", "afirmaciones": [{"oracion": 0, "afirmacion": "…", "estado": "respaldada" | "contradice" | '
             '"sin_respaldo", "ids": ["D85"], "fragmento": "…" | null}]}')


def archivo_b(ent_comp: dict) -> list[dict]:
    return [{k: x.get(k) for k in ("id", "texto", "fecha", "fuente", "contexto_fuente")} for x in ent_comp["archivo"]]


def user_b(cap: dict, archivo: list[dict], disputas: dict) -> str:
    u = {"cap": cap["cap"], "oraciones": [{"idx": s["idx"], "texto": s["texto"]} for s in cap["oraciones"]],
         "archivo": archivo, "disputas": disputas}
    return json.dumps(u, ensure_ascii=False) + "\n\nFormato de salida: " + FORMATO_B


def _llamar_cap(cap: dict, archivo: list[dict], disputas: dict, post: Callable[[dict], dict] | None, log: list[str]
                ) -> tuple[dict | None, dict[str, Any]]:
    """(respuesta JSON o None, {usage, usd, segundos, intentos, error}) de un cap. Sin JSON o error de API → un reintento."""
    import claude_helpers as hx
    from script_engine.m01e_pantalla import primer_json
    body = {"model": MODELO, "max_tokens": hx.MAX_TOKENS, "system": SYSTEM_B,
            "messages": [{"role": "user", "content": user_b(cap, archivo, disputas)}],
            "output_config": {"effort": EFFORT}}
    info: dict[str, Any] = {"usage": None, "usd": 0.0, "segundos": 0.0, "intentos": 0, "error": None}
    for k in range(INTENTOS):
        info["intentos"] = k + 1
        t0 = time.time()
        try:
            r = (post or hx._post)(body)
        except Exception as e:  # noqa: BLE001 — API, timeout: se anota y, si es el primero, se reintenta
            info["segundos"] = round(info["segundos"] + time.time() - t0, 1)
            info["error"] = f"{type(e).__name__}: {str(e)[:200]}"
            log.append(f"  verificador narración {cap['cap']} intento {k + 1}: {info['error']}")
            continue
        info["segundos"] = round(info["segundos"] + time.time() - t0, 1)
        u = r.get("usage") or {}
        info["usage"] = u
        info["usd"] = round(info["usd"] + hx.cost_of(MODELO, u), 5)
        if post is None:
            hx._track(r.get("model") or MODELO, u, "m01b_verificador")
        txt = "".join(c.get("text") or "" for c in r.get("content") or [] if c.get("type") == "text")
        resp = primer_json(txt)
        log.append(f"  verificador narración {cap['cap']} intento {k + 1}: in {u.get('input_tokens')} · out "
                   f"{u.get('output_tokens')} · US$ {hx.cost_of(MODELO, u):.4f} · {'JSON' if resp is not None else 'SIN JSON'}")
        if resp is not None:
            info["error"] = None
            return resp, info
        info["error"] = f"la respuesta no es JSON válido (stop_reason {r.get('stop_reason')})"
    return None, info


def verificar_caps(caps: list[dict], archivo: list[dict], disputas: dict, *, post: Callable[[dict], dict] | None = None,
                   log: list[str] | None = None) -> dict[str, Any]:
    """`caps` = los de `m01e_pantalla.entrada` (cap, oraciones [{idx, beat, texto, caben}]); `archivo` = `archivo_b(ent)`.
    Una llamada por cap, a la vez. Devuelve {por_cap: {cap: {afirmaciones, usage, usd, segundos, intentos, error}},
    contradice: [{cap, oracion, texto, beat, afirmacion, ids, fragmento}], sin_respaldo: [ídem], usd, segundos}. `oracion`
    es el idx que devolvió el modelo; `texto` y `beat` salen de la entrada (None si ese idx no existe)."""
    log = log if log is not None else []
    t0 = time.time()
    por_cap: dict[str, dict[str, Any]] = {}
    contradice: list[dict[str, Any]] = []
    sin_respaldo: list[dict[str, Any]] = []
    if not caps:
        return {"por_cap": por_cap, "contradice": contradice, "sin_respaldo": sin_respaldo, "usd": 0.0, "segundos": 0.0}
    with ThreadPoolExecutor(max_workers=len(caps)) as ex:
        res = list(ex.map(lambda c: _llamar_cap(c, archivo, disputas, post, log), caps))
    for cap, (resp, info) in zip(caps, res):
        afs = [a for a in (resp or {}).get("afirmaciones") or [] if isinstance(a, dict)]
        por_cap[cap["cap"]] = {"afirmaciones": afs, **info}
        ors = {s["idx"]: s for s in cap["oraciones"]}
        for a in afs:
            destino = {"contradice": contradice, "sin_respaldo": sin_respaldo}.get(str(a.get("estado")))
            if destino is None:
                continue
            s = ors.get(a.get("oracion")) or {}
            destino.append({"cap": cap["cap"], "oracion": a.get("oracion"), "texto": s.get("texto"), "beat": s.get("beat"),
                            "afirmacion": a.get("afirmacion"), "ids": list(a.get("ids") or []),
                            "fragmento": a.get("fragmento")})
    return {"por_cap": por_cap, "contradice": contradice, "sin_respaldo": sin_respaldo,
            "usd": round(sum(v["usd"] for v in por_cap.values()), 5), "segundos": round(time.time() - t0, 1)}
