# -*- coding: utf-8 -*-
"""
F63 Parte A — ¿el papel mejora si lo escribe Opus con toda la información? (solo lab, solo texto)

Cuatro brazos × 2 corridas, las 8 llamadas a la vez (HANDOFF_F63_papel_opus.md §Parte A):
  S  = Sonnet 5.5 medium, entrada de hoy, PANTALLA_SYSTEM tal cual
  O1 = Opus 5.5 medium,  entrada de hoy, PANTALLA_SYSTEM tal cual
  O2 = Opus 5.5 medium,  entrada completa (A.1), SYSTEM con la oración 2 reemplazada (A.2)
  O3 = Opus 5.5 high,    entrada completa,       igual que O2
De m01e_pantalla SOLO se importa (cargar, entrada, entrada_md5, _para_modelo, PANTALLA_SYSTEM, FORMATO_SALIDA, validar,
armar, a_markdown, estilo_de, primer_json). Nunca se llama a `llamar` ni a `generar`. El modelo se llama con hx._post
directo, el costo se registra con hx._track (sin cost_tracker.start_video: no se escribe data/cost_history.json).
Solo intento 1: sin reintento de corrección ni vueltas. Si la respuesta no trae JSON (o la API falla): un reintento de
la misma llamada; si falla de nuevo, se anota y sigue el resto.
Salida: a/<brazo>_<n>.md, a/<brazo>_<n>.raw.json, a/tabla_a.json, a/ciego/ (copias sin brazo ni md5) + a/clave_ciego.json.
Producción no se toca (lectura de _steps; mtimes antes/después en el reporte).
"""
from __future__ import annotations

import copy
import hashlib
import json
import random
import re
import sys
import time
import traceback
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

import claude_helpers as hx                                            # noqa: E402
import script_engine.m01e_pantalla as m                                # noqa: E402
from script_engine import evidence as ev                               # noqa: E402
from script_engine.clima import vocabulario_clima                      # noqa: E402

TID = "123bbb64-9fca-4395-8bf4-57d60e219ef1"
STEPS = ROOT / "data" / "scripts" / "_steps"
AQUI = Path(__file__).resolve().parent
DIR_A = AQUI / "a"

# Constantes del handoff (tabla «Constantes»)
SONNET = "claude-sonnet-5-5"       # m01e_pantalla.MODELO (Omar 2026-10-26)
OPUS = "claude-opus-5-5"           # id ya usado en el proyecto (F50f); está en hx.PRICES
ENTRADA_MD5_HOY = "a2b19d01f425b58b959b455d2e691c89"     # entrada_md5 de 01e_pantalla.raw.json
SYSTEM_O2_MD5 = "85d094bed6090b14d1802ca97433d982"       # A.2
A_PANTALLA_ESC = ("D01", "D23", "D34", "D40", "D51", "D61")   # 01a_escaleta.json (derivado)

# A.2: la oración 2 del primer párrafo, byte a byte (antes → después)
ORACION2_ANTES = ("Recibís la narración completa de un video (7 capítulos, oraciones numeradas), la escaleta (qué cuenta "
                  "cada beat y cuál es el pico de cada capítulo), el archivo del caso (datos con cifra, fecha, cita o "
                  "persona, con su fuente) y una lista de palabras de clima.")
ORACION2_DESPUES = ("Recibís la narración completa de un video (7 capítulos, oraciones numeradas), la escaleta (qué cuenta "
                    "cada beat y cuál es el pico de cada capítulo; en `escaleta_video`, la promesa del gancho, las "
                    "preguntas que el video deja abiertas y dónde las paga, y el pico del video), el archivo del caso "
                    "(todo lo que encontró la investigación: datos, fechas, citas, personas y lugares, cada uno con su "
                    "fuente y, en `contexto_fuente`, el fragmento original de la fuente), las versiones en disputa del "
                    "caso (`disputas`) y una lista de palabras de clima. El `respaldo` se copia siempre del `texto` del "
                    "dato, nunca de `contexto_fuente`.")

BRAZOS = {  # brazo → (modelo, effort, entrada completa?)
    "S": (SONNET, "medium", False),
    "O1": (OPUS, "medium", False),
    "O2": (OPUS, "medium", True),
    "O3": (OPUS, "high", True),
}
CORRIDAS = (1, 2)


def md5(s: str) -> str:
    return hashlib.md5(s.encode("utf-8")).hexdigest()


def system_de(completa: bool) -> str:
    if not completa:
        return m.PANTALLA_SYSTEM
    assert m.PANTALLA_SYSTEM.count(ORACION2_ANTES) == 1, "la oración 2 no aparece una vez en PANTALLA_SYSTEM"
    return m.PANTALLA_SYSTEM.replace(ORACION2_ANTES, ORACION2_DESPUES)


# ═══════════════════════ entradas ═══════════════════════

def _lee(nombre: str) -> dict:
    return json.loads((STEPS / TID / nombre).read_text(encoding="utf-8"))


def entrada_hoy() -> tuple[dict, dict]:
    """La entrada de producción (S, O1): cargar + entrada + chequeo de entrada_md5 (PARÁ si no da)."""
    carga = m.cargar(TID, STEPS)
    ent = m.entrada(carga, vocabulario_clima())
    h = m.entrada_md5(ent)
    if h != ENTRADA_MD5_HOY:
        raise SystemExit(f"PARÁ: entrada_md5 de hoy {h} ≠ {ENTRADA_MD5_HOY} (seg_por_palabra={ent['seg_por_palabra']})")
    return carga, ent


def _tipo_todo(it: dict[str, Any]) -> str | None:
    """A.1.1: todo ítem del pool entra al archivo (D/T/Q/P/L por `_kind`)."""
    return {"datos": "D", "cronologia": "T", "citas": "Q", "personajes": "P", "lugares": "L"}.get(it["_kind"])


def contexto_fuente(it: dict[str, Any]) -> str:
    cl = it.get("cita_literal")
    if not cl:
        evd = it.get("evidencia") or []
        cl = (evd[0] or {}).get("cita_literal") if evd else ""
    return re.sub(r"\s+", " ", str(cl or "")).strip()


def entrada_completa(carga: dict) -> tuple[dict, dict, dict]:
    """A.1: (ent completa para validar, escaleta_video, disputas). `ent` lleva el archivo entero (+ contexto_fuente, L
    como «nombre — rol») y los beats con emocion/imagen_sensorial/pregunta_abierta/paga."""
    orig = m._tipo
    m._tipo = _tipo_todo
    try:
        ent = m.entrada(carga, vocabulario_clima())
    finally:
        m._tipo = orig
    its = ev.items(carga["pool"])
    for x in ent["archivo"]:
        it = its[x["id"]]
        if it["_kind"] == "lugares":
            x["texto"] = f"{it.get('nombre') or ''} — {it.get('rol') or ''}".strip(" —")
        x["contexto_fuente"] = contexto_fuente(it)
    esc = carga["escaleta"]
    por_n = {int(b["n"]): b for b in esc.get("beats") or []}
    for b in ent["beats"]:
        e = por_n.get(b["n"]) or {}
        for k in ("emocion", "imagen_sensorial", "pregunta_abierta", "paga"):
            b[k] = e.get(k)
    escaleta_video = {k: esc.get(k) for k in ("promesa_gancho", "loops", "recuerda_loop", "pico", "humano",
                                             "antagonista", "cierre_humano")}
    ficha = _lee("ficha_caso.json")
    disputas = {"versiones": ficha.get("versiones"), "contradicciones": ficha.get("contradicciones")}
    return ent, escaleta_video, disputas


def user_de(ent: dict, extra: dict | None = None) -> str:
    """USER como m01e_pantalla.pedido (+ escaleta_video y disputas en la entrada completa)."""
    pm = m._para_modelo(ent)
    if extra:
        pm = {**pm, **extra}
    return json.dumps(pm, ensure_ascii=False) + "\n\nFormato de salida: " + m.FORMATO_SALIDA


# ═══════════════════════ la llamada ═══════════════════════

def llamar_modelo(model: str, effort: str, system: str, user: str, etiqueta: str, log: list[str]) -> dict[str, Any]:
    """Como m01e_pantalla.llamar.autor: body → hx._post; costo hx.cost_of; registro hx._track(…, etiqueta).
    Devuelve {body, intentos: [{texto, respuesta, usage, stop, usd, segundos, error?}], respuesta, usage, usd, segundos}.
    Sin JSON o error de API → un reintento de la misma llamada."""
    body = {"model": model, "max_tokens": hx.MAX_TOKENS, "system": system,
            "messages": [{"role": "user", "content": user}], "output_config": {"effort": effort}}
    out: dict[str, Any] = {"body": body, "intentos": [], "respuesta": None, "usage": None, "usd": 0.0, "segundos": 0.0}
    for k in range(2):
        t0 = time.time()
        try:
            r = hx._post(body)
        except Exception as e:  # noqa: BLE001 — se anota y, si es el primero, se reintenta
            seg = round(time.time() - t0, 1)
            out["intentos"].append({"error": f"{type(e).__name__}: {e}", "segundos": seg})
            out["segundos"] += seg
            log.append(f"{etiqueta} intento {k + 1}: ERROR {type(e).__name__}: {str(e)[:200]} ({seg} s)")
            continue
        seg = round(time.time() - t0, 1)
        u = r.get("usage") or {}
        usd = round(hx.cost_of(model, u), 5)
        hx._track(r.get("model") or model, u, etiqueta)
        txt = "".join(c.get("text") or "" for c in r.get("content") or [] if c.get("type") == "text")
        resp = m.primer_json(txt)
        out["intentos"].append({"texto": txt, "respuesta": resp, "usage": u, "stop": r.get("stop_reason"),
                                "usd": usd, "segundos": seg})
        out["usd"] = round(out["usd"] + usd, 5)
        out["segundos"] = round(out["segundos"] + seg, 1)
        log.append(f"{etiqueta} intento {k + 1}: in {u.get('input_tokens')} · out {u.get('output_tokens')} · "
                   f"US$ {usd:.4f} · {seg} s · {'JSON' if resp is not None else 'SIN JSON'} · stop {r.get('stop_reason')}")
        if resp is not None:
            out["respuesta"], out["usage"] = resp, u
            break
    return out


# ═══════════════════════ A.3 validación «solo anotar» y A.4 salida ═══════════════════════

def validar_y_armar(resp: dict | None, ent: dict, carga: dict, brazo: str, n: int, llamada: dict,
                    system_md5: str) -> tuple[dict, dict]:
    ent = copy.deepcopy(ent)
    ent["_pool"] = carga["pool"]
    val = m.validar(resp if resp is not None else {}, ent, {}, final=True)
    modelo, effort, _ = BRAZOS[brazo]
    u = llamada.get("usage") or {}
    res = {"validacion": val, "modelo": modelo, "effort": effort, "entrada_md5": m.entrada_md5(ent) if not BRAZOS[brazo][2]
           else md5(user_de(ent)), "intentos": [i for i in llamada["intentos"] if "usage" in i],
           "usd": llamada["usd"], "tokens_in": u.get("input_tokens"),
           "tope": {"usd": "sin tope", "de": "lab F63 (DECISIONES 2026-10-29: el costo se informa)"},
           "error": None if resp is not None else "sin JSON en dos intentos",
           "reintento": {"tipo": None, "beats": [], "aplicados": [], "ignorados": [], "sin_beat": [], "vueltas": [],
                         "cierre": "solo intento 1 (F63: sin vueltas)", "cortados_al_cierre": []},
           "motivos": [], "confirmados": {}}
    p = m.armar(ent, res)
    p["prompt_md5"] = system_md5                      # A.4.1(b): el md5 del SYSTEM del brazo
    p["prompt_version"] = "m01e-6" if not BRAZOS[brazo][2] else "m01e-6 + A.2 (F63)"
    return p, val


def _propuestas(resp: dict | None) -> list[dict]:
    out = []
    for b in (resp or {}).get("beats") or []:
        if isinstance(b, dict) and isinstance(b.get("ficha"), dict):
            out.append({"cap": str(b.get("cap")), "beat": m._int(b.get("beat")), "ficha": b["ficha"]})
    return out


def markdown_f63(p: dict, resp: dict | None, val: dict) -> str:
    """a_markdown + A.4.1(a): después de cada línea de beat, cada ficha que propuso el modelo con «pasa» o
    «cortaría: <regla> — <motivo>»."""
    md = m.a_markdown(p)
    props = _propuestas(resp)
    caidas = [d for d in val["descartados"] if d.get("quien") == "validación" and d.get("que") == "ficha"]
    pasan = {(b["cap"], b["beat"]): b["ficha"] for b in val["beats"] if b.get("ficha")}
    lines, cap = [], None
    for ln in md.split("\n"):
        lines.append(ln)
        mc = re.match(r"^## (ch\d\d) — ", ln)
        if mc:
            cap = mc.group(1)
            continue
        mb = re.match(r"^- beat (\d+) · ", ln)
        if mb and cap:
            nb = int(mb.group(1))
            usados = []
            for pr in [x for x in props if x["cap"] == cap and x["beat"] == nb]:
                fi = pr["ficha"]
                pid = str(fi.get("pool_id"))
                que = f"propuesta **{pid}** «{fi.get('etiqueta')} · {fi.get('texto')}» en [{fi.get('sentence_idx')}]"
                ok = pasan.get((cap, nb))
                if ok and ok["pool_id"] == pid and pid not in usados:
                    usados.append(pid)
                    lines.append(f"  - {que} → pasa")
                    continue
                d = next((d for d in caidas if d.get("cap") == cap and d.get("beat") == nb and str(d.get("pool_id")) == pid
                          and d.get("sentence_idx") == fi.get("sentence_idx") and id(d) not in usados), None)
                if d:
                    usados.append(id(d))
                    lines.append(f"  - {que} → cortaría: **{d['regla']}** — {d['motivo']}")
                else:
                    lines.append(f"  - {que} → (sin veredicto: no se encontró en la validación)")
    return "\n".join(lines)


def metricas(brazo: str, n: int, resp: dict | None, val: dict, ent: dict, llamada: dict) -> dict[str, Any]:
    props = _propuestas(resp)
    pasan = [b for b in val["beats"] if b.get("ficha")]
    caidas = [d for d in val["descartados"] if d.get("quien") == "validación" and d.get("que") == "ficha"]
    ids_pasan = [b["ficha"]["pool_id"] for b in pasan]
    esc_ids = set()
    for b in ent["beats"]:
        esc_ids.update([b["dato_central"]] + list(b["apoyo"]))
    esc_ids.discard("")
    esc_ids |= set(A_PANTALLA_ESC)
    gancho = next((b for b in val["beats"] if b.get("funcion") == "gancho"), None)
    picos = [b for b in val["beats"] if b.get("pico")]
    u = llamada.get("usage") or {}
    return {"brazo": brazo, "corrida": n, "modelo": BRAZOS[brazo][0], "effort": BRAZOS[brazo][1],
            "entrada": "completa" if BRAZOS[brazo][2] else "hoy",
            "json": resp is not None,
            "fichas_propuestas": len(props), "fichas_pasan": len(pasan),
            "cortadas_por_regla": dict(Counter(d["regla"] for d in caidas)),
            "gancho_ficha": (gancho or {}).get("ficha", {}) and gancho["ficha"]["pool_id"] if gancho else None,
            "picos_con_ficha": f"{sum(1 for b in picos if b.get('ficha'))}/{len(picos)}",
            "picos_vacios": val.get("picos_vacios"),
            "a_pantalla_cubiertos": f"{len([i for i in A_PANTALLA_ESC if i in ids_pasan])}/{len(A_PANTALLA_ESC)}",
            "a_pantalla_ids": [i for i in A_PANTALLA_ESC if i in ids_pasan],
            "a_pantalla_vacios": val.get("a_pantalla_vacios"),
            "ids_escaleta_usados": sorted(i for i in ids_pasan if i in esc_ids),
            "ids_fuera_escaleta": sorted(i for i in ids_pasan if i not in esc_ids),
            "ids_pasan_por_beat": {f"{b['cap']} b{b['beat']}": b["ficha"]["pool_id"] for b in pasan},
            "sellos": sum(1 for b in val["beats"] if b.get("sello")),
            "sellos_cortados": sum(1 for d in val["descartados"] if d.get("quien") == "validación" and d.get("que") == "sello"),
            "relojes": len(val["relojes"]), "relojes_con_error": sum(1 for r in val["relojes"] if r.get("error")),
            "descartados_modelo": sum(1 for d in val["descartados"] if d.get("quien") == "modelo"),
            "tokens_in": u.get("input_tokens"), "tokens_out": u.get("output_tokens"),
            "usd": llamada["usd"], "segundos": llamada["segundos"], "intentos": len(llamada["intentos"])}


def coincidencia(m1: dict, m2: dict, n_beats: int = 13) -> dict[str, Any]:
    """Constantes: beats (de 13) con el mismo pool_id de ficha en las dos corridas, ÷ 13."""
    a, b = m1["ids_pasan_por_beat"], m2["ids_pasan_por_beat"]
    iguales = sorted(k for k in a if k in b and a[k] == b[k])
    ambos_sin = n_beats - len(set(a) | set(b))
    return {"beats_mismo_id": iguales, "n": len(iguales), "de": n_beats, "valor": round(len(iguales) / n_beats, 3),
            "beats_ambos_sin_ficha": ambos_sin}


# ═══════════════════════ corrida ═══════════════════════

def tarea(brazo: str, n: int, ent: dict, carga: dict, user: str, system: str, log: list[str]) -> dict[str, Any]:
    modelo, effort, completa = BRAZOS[brazo]
    etiqueta = f"lab_f63_{brazo}_{n}"
    try:
        ll = llamar_modelo(modelo, effort, system, user, etiqueta, log)
        resp = ll["respuesta"]
        p, val = validar_y_armar(resp, ent, carga, brazo, n, ll, md5(system))
        md = markdown_f63(p, resp, val)
        (DIR_A / f"{brazo}_{n}.md").write_text(md, encoding="utf-8", newline="\n")
        raw = {"brazo": brazo, "corrida": n, "modelo": modelo, "effort": effort, "entrada": "completa" if completa else "hoy",
               "system_md5": md5(system), "user_md5": md5(user), "body": ll["body"], "intentos": ll["intentos"],
               "respuesta": resp, "validacion": val, "usage": ll["usage"], "usd": ll["usd"], "segundos": ll["segundos"]}
        (DIR_A / f"{brazo}_{n}.raw.json").write_text(json.dumps(raw, ensure_ascii=False, indent=1), encoding="utf-8")
        return metricas(brazo, n, resp, val, ent, ll)
    except Exception as e:  # noqa: BLE001
        log.append(f"{etiqueta}: EXCEPCIÓN {type(e).__name__}: {e}\n{traceback.format_exc()}")
        return {"brazo": brazo, "corrida": n, "error": f"{type(e).__name__}: {e}"}


def main() -> int:
    DIR_A.mkdir(parents=True, exist_ok=True)
    (DIR_A / "ciego").mkdir(exist_ok=True)
    log: list[str] = []
    t0 = time.time()
    carga, ent_hoy = entrada_hoy()
    ent_comp, esc_video, disputas = entrada_completa(carga)
    sys_hoy, sys_comp = system_de(False), system_de(True)
    if md5(sys_comp) != SYSTEM_O2_MD5:
        raise SystemExit(f"PARÁ: md5 del SYSTEM O2/O3 {md5(sys_comp)} ≠ {SYSTEM_O2_MD5}")
    user_hoy = user_de(ent_hoy)
    assert md5(user_hoy) == ENTRADA_MD5_HOY
    user_comp = user_de(ent_comp, {"escaleta_video": esc_video, "disputas": disputas})
    cab = {"entrada_md5_hoy": md5(user_hoy), "system_md5_hoy": md5(sys_hoy), "system_md5_o2o3": md5(sys_comp),
           "user_md5_completa": md5(user_comp), "chars_user_hoy": len(user_hoy), "chars_user_completa": len(user_comp),
           "archivo_hoy": len(ent_hoy["archivo"]), "archivo_completa": len(ent_comp["archivo"]),
           "pool": len(ev.items(carga["pool"])), "seg_por_palabra": ent_hoy["seg_por_palabra"]}
    print(json.dumps(cab, ensure_ascii=False, indent=1))
    (AQUI / "entrada_completa_muestra.json").write_text(json.dumps(
        {"escaleta_video": esc_video, "disputas": disputas, "beats": ent_comp["beats"][:2],
         "archivo_muestra": [x for x in ent_comp["archivo"] if x["id"] in ("D85", "D34", "L01", "Q25")]},
        ensure_ascii=False, indent=1), encoding="utf-8")
    trabajos = []
    for brazo, (_, _, completa) in BRAZOS.items():
        for n in CORRIDAS:
            trabajos.append((brazo, n, ent_comp if completa else ent_hoy, carga, user_comp if completa else user_hoy,
                             sys_comp if completa else sys_hoy))
    with ThreadPoolExecutor(max_workers=len(trabajos)) as ex:
        futs = [ex.submit(tarea, *t, log) for t in trabajos]
        mets = [f.result() for f in futs]
    coin = {}
    for brazo in BRAZOS:
        ms = [x for x in mets if x["brazo"] == brazo and "error" not in x]
        if len(ms) == 2:
            coin[brazo] = coincidencia(ms[0], ms[1], len(ent_hoy["beats"]))
    # A.4.4: copias a ciegas
    mds = sorted(DIR_A.glob("*_[12].md"))
    orden = list(mds)
    random.Random(63).shuffle(orden)
    clave = {}
    for k, f in enumerate(orden, start=1):
        txt = f.read_text(encoding="utf-8").split("\n")
        out = []
        for ln in txt:
            if ln.startswith("`m01e_pantalla` ") or ln.startswith("Segundos por palabra "):
                out.append("(encabezado quitado: copia a ciegas)")
            else:
                out.append(ln)
        nombre = f"papel_{k:02d}.md"
        (DIR_A / "ciego" / nombre).write_text("\n".join(out), encoding="utf-8", newline="\n")
        clave[nombre] = f.name
    (DIR_A / "clave_ciego.json").write_text(json.dumps(clave, ensure_ascii=False, indent=1), encoding="utf-8")
    total = {"cabecera": cab, "metricas": mets, "coincidencia": coin,
             "usd_total": round(sum(x.get("usd") or 0 for x in mets), 4), "segundos_total": round(time.time() - t0, 1),
             "log": log}
    (DIR_A / "tabla_a.json").write_text(json.dumps(total, ensure_ascii=False, indent=1), encoding="utf-8")
    (DIR_A / "etapa_a.log").write_text("\n".join(log) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in total.items() if k != "log"}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
