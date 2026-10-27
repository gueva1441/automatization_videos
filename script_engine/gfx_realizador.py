"""
script_engine/gfx_realizador.py — F29 §A: el gfx obedece a la escaleta. «El bloque aporta lo que la voz no dice, sobre
lo que la voz está contando ahora. Nunca repite el subtítulo; nunca adelanta un beat posterior.»

Con `01a_escaleta.json` en `_steps/<topic>/` (y la narración por beat, `01b_narracion_v3.json`), gfx_layer arma por cap:
    ventanas   cada beat del cap → [t0, t1] en la voz (primera y última palabra de sus párrafos; tiempos del plan, es
               decir con el `time_offset` del gancho) → `gfx_beats_chNN.json`.
    candidatos (en este orden y solo estos)
               obligatorios: los `a_pantalla` del cap, cada uno en la ventana de su beat (el que lo trae en
               `dato_central`/`datos_apoyo`; si ninguno, el que describe su `por_que`; si no se puede decidir, el
               último beat del cap);
               opcionales: `dato_central` (primero, en un giro) y `datos_apoyo` de cada beat que la voz NO dijo en esa
               ventana (mismo número, mismo nombre o la misma cláusula → fuera). Datos duros y citas, como el pool.
    finalizar  F37 §B.4 (el papel es el único camino): solo los sellos del papel y ningún punch_in (ver la función).
    pregunta   = `cierre` del último beat del cap, literal.
Sin escaleta (topics viejos, v3) nada de esto corre: gfx_layer sigue por el camino de siempre, con aviso.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from script_engine import evidence as ev

_NUM_PALABRA = {"uno", "una", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho", "nueve", "diez", "once",
                "doce", "trece", "veinte", "treinta", "cuarenta", "cincuenta", "sesenta", "setenta", "ochenta",
                "noventa", "cien", "ciento", "cientos", "mil", "millones", "novecientos", "novecientas", "quinientos",
                "trescientos", "doscientos", "cuatrocientos", "seiscientos", "setecientos", "ochocientos"}


# ═══════════════════════ carga ═══════════════════════

def cargar(topic_id: str, steps_dir: Path) -> dict[str, Any] | None:
    """{escaleta, parrafos} del topic, o None si falta la escaleta o la narración por beat."""
    sd = Path(steps_dir) / topic_id
    fe, fn = sd / "01a_escaleta.json", sd / "01b_narracion_v3.json"
    if not fe.exists() or not fn.exists():
        return None
    try:
        esc = json.loads(fe.read_text(encoding="utf-8"))
        nar = json.loads(fn.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not esc.get("beats"):
        return None
    return {"escaleta": esc, "parrafos": nar.get("parrafos") or []}


# ═══════════════════════ ventanas ═══════════════════════

def _palabras(t: str) -> list[str]:
    return re.findall(r"\S+", t or "")


def ventanas(cap: int, escaleta: dict, parrafos: list[dict], words: list[dict], time_offset: float = 0.0
             ) -> list[dict[str, Any]]:
    """Los beats del cap con su ventana [t0, t1] en la voz (la palabra del texto → la de la voz, por proporción: la voz
    normalizada puede tener otra cantidad de palabras)."""
    from script_engine.music_intensity import tiempos_por_palabra
    bc = [b for b in escaleta.get("beats") or [] if int(b.get("cap") or 0) == cap]
    pc = [p for p in parrafos if int(p.get("cap") or 0) == cap]
    tw = tiempos_por_palabra(pc, words)
    span: dict[int, list[int]] = {}
    k = 0
    for p in pc:
        n = len(_palabras(p["texto"]))
        s = span.setdefault(int(p.get("beat") or 0), [k, k + n - 1])
        s[1] = k + n - 1
        k += n
    out = []
    for b in bc:
        n = int(b["n"])
        s = span.get(n)
        if not s or not tw or s[0] >= len(tw):
            continue
        out.append({"n": n, "funcion": str(b.get("funcion") or ""), "intensidad": int(b.get("intensidad") or 0),
                    "t0": round(tw[s[0]][0] + time_offset, 3), "t1": round(tw[min(s[1], len(tw) - 1)][1] + time_offset, 3),
                    "dato_central": str(b.get("dato_central") or ""),
                    "datos_apoyo": [str(x) for x in b.get("datos_apoyo") or []],
                    "cierre": str(b.get("cierre") or "").strip(),
                    "texto": " ".join(p["texto"] for p in pc if int(p.get("beat") or 0) == n),
                    "campos": " ".join(str(b.get(c) or "") for c in ("emocion", "imagen_sensorial", "pregunta_abierta",
                                                                     "cierre"))})
    return out


def _raices(t: str) -> set[str]:
    return {w[:5] for w in re.findall(r"[^\W\d_]{5,}", ev.norm(t)) if w not in _NUM_PALABRA and w not in ev._FUNC}


def beat_de_pantalla(a: dict, beats: list[dict]) -> tuple[int | None, str]:
    """El beat de un `a_pantalla`: el que lo trae en sus ids; si ninguno, el que describe su `por_que` (raíces de 5
    letras en común con el texto y los campos del beat, sin números en palabras; empate → el posterior); si no se puede
    decidir, el último beat del cap."""
    i = str(a.get("id"))
    for b in beats:
        if i == b["dato_central"] or i in b["datos_apoyo"]:
            return b["n"], "ids del beat"
    pq = _raices(str(a.get("por_que") or ""))
    best, sc = None, 0
    for b in beats:
        s = len(pq & _raices(b["texto"] + " " + b["campos"]))
        if s >= sc and s > 0:
            best, sc = b["n"], s
    if best is not None:
        return best, f"por_que ({sc} raíces en común)"
    return (beats[-1]["n"] if beats else None), "último beat del cap"


# ═══════════════════════ candidatos ═══════════════════════

def ya_dicho(it: dict[str, Any], voz: str) -> bool:
    """¿La voz ya lo dijo en ese tramo? Mismo número/fecha/nombre (anchors literales) o la misma cláusula (≥ 60 % de
    sus palabras de contenido)."""
    if ev.used_in(voz, it):
        return True
    c = ev._content(ev.text_of(it))
    return bool(c) and len(c & ev._content(voz)) >= 0.6 * len(c)


def _voz_en(words: list[dict], t0: float, t1: float, time_offset: float) -> str:
    return " ".join(str(w.get("word", "")) for w in words if t0 - 0.05 <= float(w["start"]) + time_offset <= t1 + 0.05)


def candidatos(cap: int, escaleta: dict, beats: list[dict], pool: dict | None, words: list[dict],
               time_offset: float = 0.0, ya_mostrados: set[str] | None = None) -> list[dict[str, Any]]:
    its = ev.items(pool) if pool else {}
    usados = set(ya_mostrados or ())
    out: list[dict[str, Any]] = []
    vistos: set[str] = set()
    por_n = {b["n"]: b for b in beats}
    for a in escaleta.get("a_pantalla") or []:
        if int(a.get("cap") or 0) != cap:
            continue
        n, como = beat_de_pantalla(a, beats)
        i = str(a.get("id"))
        if n is None or i in vistos:
            continue
        b = por_n[n]
        out.append({"id": i, "beat": n, "funcion": b["funcion"], "t0": b["t0"], "t1": b["t1"], "obligatorio": True,
                    "como": como, "ya_dicho": False, "por_que": a.get("por_que")})
        vistos.add(i)
    for b in beats:
        ids = ([b["dato_central"]] if b["funcion"] == "giro" else []) + b["datos_apoyo"] + \
              ([] if b["funcion"] == "giro" else [b["dato_central"]])
        voz = _voz_en(words, b["t0"], b["t1"], time_offset)
        for i in ids:
            if not i or i in vistos or i in usados:
                continue
            it = its.get(i)
            if not it or not (ev.is_hard(it) or it["_kind"] == "citas"):
                continue
            dicho = ya_dicho(it, voz)
            out.append({"id": i, "beat": b["n"], "funcion": b["funcion"], "t0": b["t0"], "t1": b["t1"],
                        "obligatorio": False, "como": "dato_central" if i == b["dato_central"] else "datos_apoyo",
                        "ya_dicho": dicho})
            vistos.add(i)
    return out


def preparar(cap: int, carga: dict, pool: dict | None, words: list[dict], time_offset: float, work_dir: Path,
             cap_id: str, ya_mostrados: set[str] | None = None) -> dict[str, Any]:
    esc, pars = carga["escaleta"], carga["parrafos"]
    bs = ventanas(cap, esc, pars, words, time_offset)
    cs = candidatos(cap, esc, bs, pool, words, time_offset, ya_mostrados)
    real = {"cap": cap, "beats": bs, "candidatos": cs, "pico_escaleta": (esc.get("pico") or {}).get("beat")}
    (Path(work_dir) / f"gfx_beats_{cap_id}.json").write_text(json.dumps(real, ensure_ascii=False, indent=1),
                                                             encoding="utf-8")
    return real


def pregunta_cierre(real: dict) -> str | None:
    """La pregunta del cap = `cierre` del último beat, literal."""
    return (real["beats"][-1]["cierre"] or None) if real.get("beats") else None


# ═══════════════════════ finalizar ═══════════════════════

def finalizar(plan: dict[str, Any], real: dict[str, Any], log: list[str]) -> list[dict[str, Any]]:
    """El cierre del plan. F37 §B.4: el papel es el único camino (no hay borrador del director): los textos ya pasaron
    sus filtros, su reparto y su crítico (pantalla_filtros, pantalla_colocar.repartir). Acá queda: los sellos, solo los
    del guion en papel (clima.sellos_del_papel, `por_tema`), y ningún punch_in (DECISIONES F32: el único golpe es el
    zoom_punch del pico). Se borraron las ramas del camino sin papel (candidatos, ventanas, duración por texto, topes
    por función y por cap), la del contador y la de los íconos. Devuelve una fila por bloque quitado."""
    filas: list[dict[str, Any]] = []
    sellos = list(plan.get("emphasis") or [])
    keep = [e for e in sellos if e.get("por_tema")]
    for e in sellos:
        if e not in keep:
            filas.append({"bloque": "emphasis", "texto": e.get("word"), "t": e.get("start"), "accion": "fuera",
                          "motivo": "sello que no viene del guion en papel"})
    plan["emphasis"] = keep
    for p in plan.get("punch_in") or []:
        t = float(p) if isinstance(p, (int, float)) else float((p or {}).get("t", (p or {}).get("start", -1)))
        filas.append({"bloque": "punch_in", "texto": "acercamiento", "t": t, "accion": "fuera", "regla": "duplica",
                      "motivo": "punch_in: lo reemplaza el zoom_punch del pico (F30b)"})
    plan["punch_in"] = []
    log.append(f"  realizador: {len(filas)} ajuste(s)")
    plan["realizador"] = {"filas": filas}
    return filas


def cerrar(plan: dict[str, Any], real: dict[str, Any] | None, pool: dict | None, log: list[str], *,
           criticar: Any, rotulista: bool, side: str = "right", escena: Any = None) -> None:
    """El final del plan, en orden: (con el papel) `escena()` —reparto con el crítico, reloj contra el corte, sellos—
    → finalizar → crítico (`criticar()`: junta las filas). F36 §D: sin el rótulo de respaldo del pico."""
    if rotulista and escena is not None:
        escena()
    if real:
        finalizar(plan, real, log)
    criticar()
