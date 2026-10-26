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
    finalizar  (después del plan, el pico, el zoom y la pregunta; antes del crítico): fuera los bloques que no salen de
               un candidato (los «datos» de VERIFIED_FACTS, el contador de una cifra que dice la voz) o que caen fuera
               de la ventana de su beat; duración por texto (max(2.5, palabras/3 + 1), tope 8) en rótulos, recortes y
               citas; tope por función del beat y 5 por cap (sin reloj, pregunta ni título); sellos: solo el del pico
               (`pico.word`), sin ícono figurativo; punch_in solo acompañando un bloque.
    pico       (después del crítico) 1 bloque grande obligatorio en la frase del pico (`pico.t`): si gfx_peak no puso
               nivel de agua, zoom ni recorte, un rótulo con el candidato del beat del pico.
    pregunta   = `cierre` del último beat del cap, literal.
Sin escaleta (topics viejos, v3) nada de esto corre: gfx_layer sigue por el camino de siempre, con aviso.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from script_engine import evidence as ev

TOPE_POR_FUNCION: dict[str, int] = {"gancho": 1, "planteo": 1, "escalada": 2, "giro": 2, "pico": 1, "respiro": 1,
                                    "revelacion": 2, "cierre": 1}
TOPE_CAP = 5
DUR_MIN, DUR_MAX = 2.5, 8.0
ICONOS_ABSTRACTOS = {"sello", "tinta", "prensa"}
GRANDES = ("water_level", "evidence_zoom", "archive_clippings", "callouts", "quote_card")
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


def para_pool(real: dict) -> tuple[list[str], set[str], dict[str, tuple[float, float]]]:
    """(ids en orden, obligatorios, ventana por id) para gfx_pool: solo lo que la voz no dijo."""
    cs = [c for c in real["candidatos"] if c["obligatorio"] or not c["ya_dicho"]]
    return [c["id"] for c in cs], {c["id"] for c in cs if c["obligatorio"]}, {c["id"]: (c["t0"], c["t1"]) for c in cs}


def pregunta_cierre(real: dict) -> str | None:
    """La pregunta del cap = `cierre` del último beat, literal."""
    return (real["beats"][-1]["cierre"] or None) if real.get("beats") else None


# ═══════════════════════ finalizar ═══════════════════════

def duracion_texto(texto: str) -> float:
    return round(min(DUR_MAX, max(DUR_MIN, len(_palabras(texto)) / 3 + 1)), 2)


def _beat_en(real: dict, t: float) -> dict | None:
    for b in real["beats"]:
        if b["t0"] - 0.3 <= t <= b["t1"] + 0.3:
            return b
    prev = [b for b in real["beats"] if b["t0"] <= t]
    return prev[-1] if prev else (real["beats"][0] if real["beats"] else None)


def _lista(plan: dict, k: str) -> list[dict]:
    return list(plan.get(k) or [])


def finalizar(plan: dict[str, Any], real: dict[str, Any], log: list[str]) -> list[dict[str, Any]]:
    """Ver el docstring del módulo. Devuelve una fila por bloque quitado o ajustado."""
    cand = {c["id"]: c for c in real["candidatos"]}
    filas: list[dict[str, Any]] = []

    def fuera(k: str, b: dict, motivo: str) -> None:
        filas.append({"bloque": k, "texto": b.get("headline") or b.get("text") or b.get("word") or b.get("value_text"),
                      "t": b.get("start"), "pool_id": b.get("pool_id"), "accion": "fuera", "motivo": motivo})

    # F29b: con el rotulista, los bloques de texto ya pasaron su anclaje, sus ventanas, su duración y sus topes (A.4):
    # acá quedan los sellos, el contador y el punch_in
    rot = bool(plan.get("rotulista"))
    # 1. solo candidatos, y dentro de la ventana de su beat
    for k in (() if rot else ("archive_clippings", "callouts")):
        keep = []
        for b in _lista(plan, k):
            c = cand.get(b.get("pool_id") or "")
            if c is None:
                fuera(k, b, "no sale de un candidato de los beats del cap (VERIFIED_FACTS u otro cap)")
            elif c["ya_dicho"] and not c["obligatorio"]:
                fuera(k, b, f"la voz ya lo dice en el beat {c['beat']}")
            elif not (c["t0"] - 0.3 <= float(b["start"]) <= c["t1"]):
                fuera(k, b, f"fuera de la ventana del beat {c['beat']} ({c['t0']:.1f}–{c['t1']:.1f} s)")
            else:
                b["beat"] = c["beat"]
                keep.append(b)
        plan[k] = keep
    q = plan.get("quote_card")
    if q and not rot:
        c = cand.get(q.get("pool_id") or "")
        if c is None or (c["ya_dicho"] and not c["obligatorio"]) or not (c["t0"] - 0.3 <= float(q["start"]) <= c["t1"]):
            fuera("quote_card", q, "cita fuera de los candidatos o de la ventana de su beat")
            plan["quote_card"] = None
        else:
            q["beat"] = c["beat"]
    if plan.get("count_up"):
        fuera("count_up", plan["count_up"], "contador de una cifra que dice la voz (repite el subtítulo)")
        plan["count_up"] = None
    # 2. sellos: solo el del pico, sin ícono figurativo
    pk = plan.get("pico") or {}
    sellos = _lista(plan, "emphasis")
    keep_s = [e for e in sellos if e.get("peak_word") or (pk.get("word") and str(e.get("word", "")).lower().strip(".,;:")
                                                           == str(pk.get("word")).lower().strip(".,;:"))][:1]
    for e in sellos:
        if e not in keep_s:
            fuera("emphasis", e, "sello por léxico (solo queda el de la palabra del pico)")
    for e in keep_s:
        if e.get("icon") and e["icon"] not in ICONOS_ABSTRACTOS:
            filas.append({"bloque": "emphasis", "texto": e.get("word"), "t": e.get("start"),
                          "accion": f"ícono figurativo «{e['icon']}» fuera"})
            e.pop("icon", None)
            e.pop("icon_callout", None)
    plan["emphasis"] = keep_s
    # 3. duración por texto
    for k, campo in (("archive_clippings", "headline"), ("callouts", "text")):
        for b in plan.get(k) or []:
            if not b.get("rotulista"):
                b["duration"] = duracion_texto(str(b.get(campo) or ""))
    if plan.get("quote_card") and not plan["quote_card"].get("rotulista"):
        plan["quote_card"]["duration"] = duracion_texto(plan["quote_card"].get("text", ""))
    # 4. tope por función del beat y por cap (lo obligatorio y lo del pico primero; después por orden)
    vivos: list[tuple[str, int | None, dict]] = []
    for k in (() if rot else ("archive_clippings", "callouts", "emphasis", "icon_array")):
        for idx, b in enumerate(plan.get(k) or []):
            vivos.append((k, idx, b))
    for k in (() if rot else ("quote_card", "evidence_zoom", "water_level")):
        if plan.get(k) and "start" in plan[k]:
            vivos.append((k, None, plan[k]))

    def prio(x: tuple[str, int | None, dict]) -> tuple:
        k, _, b = x
        c = cand.get(b.get("pool_id") or "")
        es_pico = k == pk.get("block") or b.get("pico") or b.get("peak_word")
        return (0 if es_pico else 1, 0 if (c and c["obligatorio"]) else 1, float(b.get("start", 0)))
    por_beat: dict[int, int] = {}
    quedan, sacar = 0, []
    for k, idx, b in sorted(vivos, key=prio):
        bt = _beat_en(real, float(b.get("start", 0)))
        n = bt["n"] if bt else -1
        tope = TOPE_POR_FUNCION.get(bt["funcion"], 2) if bt else 2
        c = cand.get(b.get("pool_id") or "")
        obligatorio = bool(c and c["obligatorio"])
        if quedan >= TOPE_CAP or (por_beat.get(n, 0) >= tope and not obligatorio):
            sacar.append((k, idx, b))
            continue
        por_beat[n] = por_beat.get(n, 0) + 1
        quedan += 1
    for k, idx, b in sacar:
        fuera(k, b, f"tope ({TOPE_CAP} por cap o el de la función del beat)")
        if idx is None:
            plan[k] = None
        else:
            plan[k] = [x for x in plan[k] if x is not b]
    # 5. punch_in solo acompañando un bloque
    iv = [(float(b["start"]), float(b["start"]) + float(b.get("duration", 2.5)))
          for k in ("archive_clippings", "callouts", "emphasis") for b in plan.get(k) or []]
    iv += [(float(plan[k]["start"]), float(plan[k]["start"]) + float(plan[k].get("duration", 3)))
           for k in ("quote_card", "evidence_zoom", "water_level") if plan.get(k) and "start" in plan[k]]
    pis = plan.get("punch_in") or []
    def _t(p: Any) -> float:
        return float(p) if isinstance(p, (int, float)) else float((p or {}).get("t", (p or {}).get("start", -1)))
    keep_p = [p for p in pis if any(a - 0.2 <= _t(p) <= b for a, b in iv)]
    if len(keep_p) != len(pis):
        filas.append({"bloque": "punch_in", "accion": f"{len(pis) - len(keep_p)} fuera (sin bloque que acompañar)"})
    plan["punch_in"] = keep_p
    log.append(f"  realizador: {len(filas)} ajuste(s) · quedan {quedan} bloque(s) · por beat {por_beat}")
    plan["realizador"] = {"filas": filas, "por_beat": por_beat}
    return filas


PICO_DESPUES_S = 5.0          # un bloque grande que arranca hasta 5 s después de la frase del pico es el bloque del pico


def _hay_grande_en_pico(plan: dict, t: float) -> str | None:
    def cerca(b: dict) -> bool:
        a = float(b["start"])
        return a - 2.0 <= t <= a + float(b.get("duration", 3)) + 0.5 or t <= a <= t + PICO_DESPUES_S
    for k in ("water_level", "evidence_zoom", "quote_card"):
        b = plan.get(k)
        if b and "start" in b and cerca(b):
            return k
    for k in ("archive_clippings", "callouts"):
        for b in plan.get(k) or []:
            if cerca(b):
                return k
    return None


def garantizar_pico(plan: dict[str, Any], real: dict[str, Any], pool: dict | None, log: list[str],
                    side: str = "right") -> str | None:
    """1 bloque grande en la frase del pico. Si no hay, un rótulo con el candidato del beat del pico (obligatorio
    primero, después uno que la voz no dijo; si no hay, el dato central del beat). Devuelve el bloque del pico."""
    pk = plan.get("pico")
    if not pk or pk.get("t") is None:
        # gfx_peak no encontró pico (sin cifra de agua ni palabra de carga): el pico es el beat más intenso del cap
        top = max(real["beats"], key=lambda b: (b["intensidad"], b["n"])) if real.get("beats") else None
        if top is None:
            return None
        pk = plan["pico"] = {**(pk or {}), "t": round(top["t0"] + 0.5, 3), "word": None, "block": None,
                             "fuente": f"escaleta (beat {top['n']}, intensidad {top['intensidad']})"}
        log.append(f"  realizador: sin pico de gfx_peak → beat {top['n']} de la escaleta @ {pk['t']:.1f}s")
    t = float(pk["t"])
    ya = _hay_grande_en_pico(plan, t)
    if ya:
        pk["block"] = pk.get("block") if pk.get("block") in GRANDES else ya
        return ya
    bt = _beat_en(real, t)
    its = ev.items(pool) if pool else {}
    puestos = {b.get("pool_id") for k in ("archive_clippings", "callouts") for b in plan.get(k) or []}
    puestos |= {(plan.get("quote_card") or {}).get("pool_id")}
    cs = [c for c in real["candidatos"] if bt and c["beat"] == bt["n"] and c["id"] not in puestos]   # nunca dos veces
    orden = [c for c in cs if c["obligatorio"]] + [c for c in cs if not c["obligatorio"] and not c["ya_dicho"]]
    if not orden and bt and bt["dato_central"] not in puestos:
        orden = [{"id": bt["dato_central"], "beat": bt["n"], "obligatorio": False}]
    for c in orden:
        it = its.get(c["id"])
        if not it:
            continue
        from script_engine.gfx_pool import pool_clause_options
        txt = re.sub(r"\s+", " ", ev.text_of(it)).strip()
        opts = pool_clause_options(txt, 12) or [txt]
        frag = opts[0]
        blk = {"text": frag, "start": round(t, 3), "kind": "figure", "duration": duracion_texto(frag), "side": side,
               "fact_idx": None, "pool_id": c["id"], "pico": True, "beat": c["beat"]}
        plan["callouts"] = sorted((plan.get("callouts") or []) + [blk], key=lambda b: float(b["start"]))
        pk["block"] = "callouts"
        pk["block_realizador"] = c["id"]
        log.append(f"  realizador: pico sin bloque grande → rótulo {c['id']} «{frag}» @ {t:.1f}s (beat {c['beat']})")
        return "callouts"
    log.append("  realizador: pico sin bloque grande y sin candidato en su beat")
    return None


def cerrar(plan: dict[str, Any], real: dict[str, Any] | None, pool: dict | None, log: list[str], *,
           criticar: Any, rotulista: bool, garantizar: bool, side: str = "right", escena: Any = None) -> None:
    """El final del plan, en orden. F29 (sin rotulista, como v3): finalizar → crítico → garantizar_pico. F29b (con
    rotulista, §A.6): finalizar → garantizar_pico (respaldo; apagado por defecto) → crítico, así todo bloque que entre
    por respaldo también se juzga. `criticar()` corre el crítico sobre el plan (in place). F29c: con rotulista,
    `escena()` (una cosa por escena: gfx_rotulista.escena_final) corre antes de todo."""
    if rotulista and escena is not None:
        escena()
    if real:
        finalizar(plan, real, log)
    if not rotulista:
        criticar()
        if real and garantizar:
            garantizar_pico(plan, real, pool, log, side=side)
        return
    if real and garantizar:
        garantizar_pico(plan, real, pool, log, side=side)
    criticar()
