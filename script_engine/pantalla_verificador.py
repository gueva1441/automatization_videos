"""
script_engine/pantalla_verificador.py — F64 Etapa 3 (DECISIONES 2026-10-31 14:20): el verificador de las fichas del
papel. Los filtros del código (`no_dicho`, `spoiler`, `contradice`, `fecha_relato`) y la duda sobre un descarte
«la voz lo dice» (`voz_lo_dice`) ya no cortan ni le preguntan al autor: cada coincidencia es una MARCA, y todas las
marcas de una validación van en UNA llamada a Claude Opus 5.5 (medium) que decide hecho por hecho si la voz lo dice,
lo adelanta o lo contradice. Lo que el verificador salva, pasa; lo que corta, va a descartados con `quien:
"verificador"`. El verificador nunca propone fichas: solo juzga.

    pedido(marcas, caps)   puro: el USER (JSON con caps, fichas marcadas y descartes dudosos + «Formato de salida: …»).
    _leer(resp, marcas)    puro: los veredictos; uno cuyo (pool_id, cap, beat) (o pool_id en descartes) no está en
                           las marcas se ignora y se anota; una marca sin veredicto queda «pasa» (o «no_dicho») con
                           motivo «sin veredicto».
    verificar(...)         la llamada, como `m01e_pantalla.llamar.autor` (body con system, messages y
                           output_config.effort → hx._post; hx.cost_of; hx._track(…, "m01e_verificador")); 1 reintento
                           sin JSON (REINTENTOS, como dicho_verificador); si no hay JSON en dos intentos, las marcas
                           quedan «pasa» con motivo «sin veredicto» y una línea en el log (no se corta a ciegas, no se
                           frena el pipeline).
Modelo, effort y reintentos: tabla «Constantes» de HANDOFF_F64. SYSTEM_V y FORMATO_V, literales del handoff.
"""
from __future__ import annotations

import hashlib
import json
import time
from typing import Any, Callable

MODELO = "claude-opus-5-5"   # DECISIONES 2026-10-31 14:20
EFFORT = "medium"
REINTENTOS = 1               # como dicho_verificador (F55 A.2)

SYSTEM_V = """Sos el verificador de un documental de historia oscura en español. El rotulista propuso fichas (textos cortos en pantalla sobre una oración de la narración) y el código marcó en cada una una coincidencia con la voz: una palabra o un número que la voz también dice, una cifra distinta para algo parecido, o una fecha posterior al momento del relato. Las palabras y los números coinciden; vos decidís si coincide el hecho.

Recibís la narración completa del video (oraciones numeradas por capítulo), las fichas marcadas y, aparte, los datos que el rotulista descartó porque «la voz lo dice» y el código duda.

Para cada ficha, un veredicto:
- «pasa»: la voz no dice ese hecho en la oración ancla ni en las vecinas (la anterior y la siguiente), no lo cuenta más adelante en el video y no dice lo contrario. Que una palabra o un número coincidan hablando de otra cosa no cuenta. Que la ficha tenga fecha posterior al momento del relato no es motivo por sí solo. Una cifra con su propia fecha (un corte histórico: «para 1989, más de 500») no es la misma cifra que un total de hoy: ni lo contradice ni lo adelanta. Si la ficha suma algo que la voz no dice (una cifra, un nombre, una consecuencia), pasa aunque comparta parte del hecho.
- «corta»: la voz dice ese mismo hecho (con las mismas palabras o con otras) en la oración ancla o en una vecina; o lo cuenta más adelante en el video, en ese capítulo o en los siguientes, y la ficha lo adelantaría; o la voz da, para la misma cosa y el mismo momento, otra cifra u otra versión.
En una cita (Q), el hecho es la frase que la ficha muestra, no el testimonio entero: que la voz cite otra frase de la misma persona no cuenta.

Para cada descarte, un veredicto: «dicho» si alguna oración de los capítulos indicados dice el hecho principal del dato (con las mismas palabras o con otras; dicho como promesa, pregunta o adelanto también cuenta; aunque omita un detalle como quién lo anunció o la cifra exacta), o «no_dicho» si ninguna lo dice. Si `caps_que_lo_cuentan` dice «todo el video», cualquier oración cuenta.

Juzgá por el hecho, no por el estilo ni por si la ficha es buena. Devolvé solo JSON con el formato pedido, con un `motivo` de una línea por veredicto y, cuando cortás o decís «dicho», el cap y el idx de la oración de la voz que lo dice o lo contradice."""

FORMATO_V = ('{"fichas": [{"pool_id": "D23", "cap": "ch05", "beat": 10, "veredicto": "pasa" | "corta", "motivo": "…", '
             '"oracion": {"cap": "ch05", "idx": 12} | null}], "descartes": [{"pool_id": "D21", "veredicto": "dicho" | '
             '"no_dicho", "motivo": "…", "oracion": {"cap": "ch03", "idx": 28} | null}]}')

CAMPOS_FICHA = ("pool_id", "cap", "beat", "sentence_idx", "oracion_ancla", "etiqueta", "texto", "respaldo", "dato_archivo",
                "cita_completa", "regla", "coincidencia")
CAMPOS_DESCARTE = ("pool_id", "dato_archivo", "motivo_del_autor", "caps_que_lo_cuentan")


def pedido(marcas: list[dict[str, Any]], caps: list[dict[str, Any]]) -> str:
    """El USER, puro: `caps` (cap, oraciones [{idx, texto}]: la narración entera, la misma del autor), `fichas` (una por
    marca de ficha: pool_id, cap, beat, sentence_idx, oracion_ancla, etiqueta, texto, respaldo, dato_archivo —en una
    cita, la frase que la ficha muestra, y el testimonio entero en `cita_completa`—, regla, coincidencia {token, cap,
    idx, oracion}) y `descartes` (pool_id, dato_archivo, motivo_del_autor, caps_que_lo_cuentan), + la línea del formato."""
    fichas = [{k: m.get(k) for k in CAMPOS_FICHA if k in m} for m in marcas if m.get("que") != "descarte"]
    descartes = [{k: m.get(k) for k in CAMPOS_DESCARTE if k in m} for m in marcas if m.get("que") == "descarte"]
    cuerpo = {"caps": [{"cap": c["cap"], "oraciones": [{"idx": s["idx"], "texto": s["texto"]} for s in c["oraciones"]]}
                       for c in caps],
              "fichas": fichas, "descartes": descartes}
    return json.dumps(cuerpo, ensure_ascii=False) + "\n\nFormato de salida: " + FORMATO_V


def pedido_md5(user: str) -> str:
    return hashlib.md5(user.encode("utf-8")).hexdigest()


def _int(v: Any) -> int | None:
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def _oracion(v: Any) -> dict[str, Any] | None:
    if not isinstance(v, dict) or v.get("cap") is None:
        return None
    return {"cap": str(v.get("cap")), "idx": _int(v.get("idx"))}


def _leer(resp: Any, marcas: list[dict[str, Any]]) -> dict[str, Any]:
    """Los veredictos del modelo contra las marcas, puro: {veredictos_fichas: [{pool_id, cap, beat, veredicto, motivo,
    oracion}], veredictos_descartes: [{pool_id, veredicto, motivo, oracion}], ignorados: [...], sin_veredicto: [...]}.
    Un veredicto cuyo (pool_id, cap, beat) —o pool_id, en descartes— no está en las marcas se ignora y se anota; un
    veredicto que no es «pasa»/«corta» («dicho»/«no_dicho») también. Una marca sin veredicto queda «pasa» («no_dicho»)
    con motivo «sin veredicto»."""
    resp = resp if isinstance(resp, dict) else {}
    claves_f = {(str(m["pool_id"]), str(m["cap"]), _int(m.get("beat"))) for m in marcas if m.get("que") != "descarte"}
    claves_d = {str(m["pool_id"]) for m in marcas if m.get("que") == "descarte"}
    vf: dict[tuple, dict[str, Any]] = {}
    vd: dict[str, dict[str, Any]] = {}
    ignorados: list[dict[str, Any]] = []
    for v in resp.get("fichas") or []:
        if not isinstance(v, dict):
            ignorados.append({"veredicto": v, "motivo": "no es un objeto"})
            continue
        k = (str(v.get("pool_id")), str(v.get("cap")), _int(v.get("beat")))
        ver = str(v.get("veredicto") or "").strip().lower()
        if k not in claves_f:
            ignorados.append({"que": "ficha", "pool_id": k[0], "cap": k[1], "beat": k[2], "motivo": "no está en las marcas"})
        elif ver not in ("pasa", "corta"):
            ignorados.append({"que": "ficha", "pool_id": k[0], "cap": k[1], "beat": k[2],
                              "motivo": f"veredicto desconocido {v.get('veredicto')!r}"})
        elif k not in vf:
            vf[k] = {"pool_id": k[0], "cap": k[1], "beat": k[2], "veredicto": ver, "motivo": str(v.get("motivo") or ""),
                     "oracion": _oracion(v.get("oracion"))}
    for v in resp.get("descartes") or []:
        if not isinstance(v, dict):
            ignorados.append({"veredicto": v, "motivo": "no es un objeto"})
            continue
        pid = str(v.get("pool_id"))
        ver = str(v.get("veredicto") or "").strip().lower()
        if pid not in claves_d:
            ignorados.append({"que": "descarte", "pool_id": pid, "motivo": "no está en las marcas"})
        elif ver not in ("dicho", "no_dicho"):
            ignorados.append({"que": "descarte", "pool_id": pid, "motivo": f"veredicto desconocido {v.get('veredicto')!r}"})
        elif pid not in vd:
            vd[pid] = {"pool_id": pid, "veredicto": ver, "motivo": str(v.get("motivo") or ""), "oracion": _oracion(v.get("oracion"))}
    sin: list[dict[str, Any]] = []
    for k in sorted(claves_f, key=lambda t: (t[1], t[2] if t[2] is not None else -1, t[0])):
        if k not in vf:
            vf[k] = {"pool_id": k[0], "cap": k[1], "beat": k[2], "veredicto": "pasa", "motivo": "sin veredicto", "oracion": None}
            sin.append({"que": "ficha", "pool_id": k[0], "cap": k[1], "beat": k[2]})
    for pid in sorted(claves_d):
        if pid not in vd:
            vd[pid] = {"pool_id": pid, "veredicto": "no_dicho", "motivo": "sin veredicto", "oracion": None}
            sin.append({"que": "descarte", "pool_id": pid})
    return {"veredictos_fichas": list(vf.values()), "veredictos_descartes": list(vd.values()), "ignorados": ignorados,
            "sin_veredicto": sin}


def verificar(marcas: list[dict[str, Any]], caps: list[dict[str, Any]], *, post: Callable[[dict], dict] | None = None,
              log: list[str] | None = None) -> dict[str, Any]:
    """UNA llamada con todas las marcas (DECISIONES 14:20). Devuelve {veredictos_fichas, veredictos_descartes, ignorados,
    sin_veredicto, usage, usd, segundos, pedido_md5, intentos, error}. Sin marcas no llama (todo vacío, US$ 0). Si el
    modelo no devuelve JSON (o la API falla) en REINTENTOS + 1 intentos: todas las marcas «pasa»/«no_dicho» con motivo
    «sin veredicto», `error` con el motivo y una línea en el log."""
    import claude_helpers as hx
    from script_engine.m01e_pantalla import primer_json
    log = log if log is not None else []
    user = pedido(marcas, caps)
    h = pedido_md5(user)
    out: dict[str, Any] = {"usage": None, "usd": 0.0, "segundos": 0.0, "pedido_md5": h, "intentos": 0, "error": None,
                           "modelo": MODELO, "effort": EFFORT}
    if not marcas:
        return {**_leer({}, []), **out}
    body = {"model": MODELO, "max_tokens": hx.MAX_TOKENS, "system": SYSTEM_V,
            "messages": [{"role": "user", "content": user}], "output_config": {"effort": EFFORT}}
    resp = None
    t0 = time.time()
    usage_total = {"input_tokens": 0, "output_tokens": 0}
    for intento in range(REINTENTOS + 1):
        out["intentos"] = intento + 1
        try:
            r = (post or hx._post)(body)
            u = r.get("usage") or {}
            for k in usage_total:
                usage_total[k] += int(u.get(k) or 0)
            out["usd"] = round(out["usd"] + hx.cost_of(MODELO, u), 5)
            if post is None:
                hx._track(r.get("model") or MODELO, u, "m01e_verificador")
            txt = "".join(c.get("text") or "" for c in r.get("content") or [] if c.get("type") == "text")
            resp = primer_json(txt)
            if resp is not None:
                break
            out["error"] = f"la respuesta no es JSON válido (stop_reason {r.get('stop_reason')})"
        except Exception as e:  # noqa: BLE001 — API, timeout: se anota y se reintenta una vez
            out["error"] = f"{type(e).__name__}: {str(e)[:120]}"
        log.append(f"  verificador intento {intento + 1}: {out['error']}")
    out["usage"] = usage_total
    out["segundos"] = round(time.time() - t0, 1)
    if resp is None:
        log.append(f"  verificador: sin JSON en {REINTENTOS + 1} intentos → {len(marcas)} marca(s) quedan «pasa» con motivo "
                   f"«sin veredicto» (no se corta a ciegas)")
        return {**_leer({}, marcas), **out}
    out["error"] = None
    return {**_leer(resp, marcas), **out}
