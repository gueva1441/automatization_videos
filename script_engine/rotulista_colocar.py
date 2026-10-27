"""
script_engine/rotulista_colocar.py — F36 §A: dónde y cuánto va cada texto de pantalla (movido de gfx_rotulista).
`tiempos` y `despues_del_corte` (§A.2: fin de la oración ancla, lectura caracteres ÷ 15, nunca después del corte),
`colocar` (F36 §C: los bloques del guion en papel; ficha, cita como ficha con autor, papel = recorte), `hasta_el_corte`
(el reloj) y `escena_final` («nunca al mismo tiempo», DECISIONES 17:58). F36 §D: se borraron el agua, el contador, la
lupa y las ediciones del plan (`--plan-edit` edita el papel).
"""
from __future__ import annotations

from typing import Any

from script_engine import evidence as ev

LECTURA_CPS = 15.0             # §0: mínimo de lectura = caracteres ÷ 15 cps (estándar de subtitulado, el más lento)


def _escena_de(escenas: list[Any] | None, t: float) -> Any | None:
    if not escenas:
        return None
    for s in escenas:
        if s.start <= t < s.end:
            return s
    return escenas[-1]


def tiempos(sents: list[dict], si: int, t0: float, chars: int, escenas: list[Any] | None = None
            ) -> tuple[float, str | None]:
    """§A.2: (t1, motivo si no va). t1 = fin de la oración ancla; si no alcanza el mínimo de lectura (caracteres ÷ 15),
    el fin de la oración siguiente; nunca después del corte de la escena que contiene t0."""
    need = chars / LECTURA_CPS
    t1 = sents[si]["t1"]
    if t1 - t0 < need and si + 1 < len(sents):
        t1 = sents[si + 1]["t1"]
    sc = _escena_de(escenas, t0)
    if sc is not None:
        t1 = min(t1, sc.end)
    t1 = round(t1, 3)
    if t1 - t0 < need:
        return t1, (f"sin tiempo de lectura: {chars} caracteres piden {need:.1f} s y hay {t1 - t0:.1f} s"
                    + (f" hasta el corte de escena ({sc.end:.1f} s)" if sc is not None and t1 == round(sc.end, 3) else ""))
    return t1, None


def despues_del_corte(sents: list[dict], si: int, t0: float, chars: int, escenas: list[Any]
                      ) -> tuple[float, float, str] | None:
    """F32 §B.3: el bloque que no cabe antes del corte de su escena arranca en el primer cuadro de la escena siguiente,
    anclado a la misma oración o a la siguiente (del mismo beat); (t0, t1, motivo) si ahí cabe, None si tampoco."""
    sc = _escena_de(escenas, t0)
    nxt = next((e for e in escenas if e.start >= sc.end - 1e-6 and e is not sc), None) if sc is not None else None
    if nxt is None:
        return None
    t0b = round(nxt.start, 3)
    si2 = next((ss["idx"] for ss in sents if ss["t0"] <= t0b <= ss["t1"]),
               next((ss["idx"] for ss in sents if ss["t0"] >= t0b), None))
    if si2 is None or si2 not in (si, si + 1) or sents[si2].get("beat") != sents[si].get("beat"):
        return None
    t1b, sin_b = tiempos(sents, si2, t0b, chars, escenas)
    if sin_b:
        return None
    return t0b, t1b, f"{t0:.2f} → {t0b:.2f} s: no cabía antes del corte de {sc.end:.2f} s, arranca en la escena {nxt.idx}"


def caracteres(tipo: str, etiqueta: str | None, texto: str, autor: str = "") -> int:
    """Lo que se lee del bloque: etiqueta + dato (la cita, con su autor). F36 §C.4: la cita se dibuja «dato» — autor,
    y se cuentan también las comillas y la raya (5 caracteres, derivado: lo que se dibuja)."""
    return len(etiqueta or "") + len(texto) + ((len(autor) + 5 if autor else 0) if tipo == "cita" else 0)


def caben(sents: list[dict], si: int, escenas: list[Any] | None) -> int | None:
    """F36 §B.8 (y C.2): cuántos caracteres caben en un bloque anclado a la oración `si` = segundos desde su inicio
    hasta el próximo corte de escena × 15 cps (derivado: la lectura de §A.2). En un cap de una sola escena, hasta el
    fin de la oración siguiente. Sin escenas, None."""
    if not escenas or not 0 <= si < len(sents):
        return None
    t0 = float(sents[si]["t0"])
    if len(escenas) == 1:
        fin = float(sents[min(si + 1, len(sents) - 1)]["t1"])
    else:
        fin = float(_escena_de(escenas, t0).end)
    return max(0, int((fin - t0) * LECTURA_CPS))


def hasta_el_corte(plan: dict[str, Any], scenes: list[Any], fps: float, log: list[str]) -> list[dict[str, Any]]:
    """F36 §B.4: el reloj no cruza el corte de la escena donde arranca: duración = min(la que trae, corte − inicio − 1
    cuadro) (derivado). Corre después de escena_final (que puede mover el reloj). F36 §D: sin agua."""
    from script_engine.gfx_project import scene_at
    filas: list[dict[str, Any]] = []
    if not scenes:
        return filas
    for campo in ("time_ticker",):
        b = plan.get(campo)
        if not b or "start" not in b:
            continue
        a = float(b["start"])
        sc = scene_at(scenes, a)
        tope = round(float(sc.end) - a - 1.0 / float(fps), 3)
        if float(b.get("duration") or 0.0) > tope:
            filas.append({"bloque": campo, "t0": a, "accion": "acortado", "regla": "corte",
                          "motivo": f"{float(b['duration']):.2f} → {tope:.2f} s: la escena {sc.idx} corta en "
                                    f"{float(sc.end):.2f} s"})
            b["duration"] = tope
    plan.setdefault("rotulista", {})["corte"] = filas
    log.append(f"  reloj contra el corte: {[(f['bloque'], f['motivo']) for f in filas] or 'nada que acortar'}")
    return filas


# ═══════════════════════ colocar ═══════════════════════

KIND_FICHA = {"cifra": "figure", "persona": "name", "hecho": "fact"}


def colocar(plan: dict[str, Any], res: dict[str, Any], ent: dict[str, Any], *, scenes: list[Any], pool: dict | None,
            used_before: set[str], log: list[str], words: list[dict] | None = None, time_offset: float = 0.0
            ) -> list[dict[str, Any]]:
    """Los bloques del guion en papel en el plan (reemplazan recortes, datos y cita del director). Con `words`, los
    filtros (`validar_papel`) corren con las escenas reales (el fin muere en el corte). Forma por estilo (aclaración 6):
    normal y nombre → ficha (el title card), cita → ficha con «dato» — autor, papel → recorte. Devuelve una fila por
    bloque (colocado o fuera, con la regla y el motivo)."""
    from script_engine.gfx_pool import short_source
    from script_engine.gfx_project import scene_at
    from script_engine.rotulista_filtros import FICHA, validar_papel   # F36 §A: filtros importa este módulo arriba
    its = ev.items(pool) if pool else {}
    viejos = {k: plan.get(k) for k in ("archive_clippings", "callouts", "quote_card")}
    plan["archive_clippings"], plan["callouts"], plan["quote_card"] = [], [], None
    filas: list[dict[str, Any]] = []
    if words is not None and res.get("final") is not None:
        v = validar_papel(res["final"].get("bloques") or [], ent, words, time_offset, escenas=scenes)
    else:
        v = res.get("validacion") or {"bloques": [], "rechazos": [], "faltan": []}
    for r in v["rechazos"]:
        filas.append({**r, "accion": "fuera"})
    for b in v["bloques"]:
        pid, t0, dur = b["pool_id"], b["t0"], b["dur"]
        it = its.get(pid) or {}
        sc = scene_at(scenes, t0)
        side = getattr(sc, "quiet_side", "right") or "right"
        meta = {"pool_id": pid, "rotulista": True, "beat": b["beat"], "sentence_idx": b["sentence_idx"],
                "word_idx": b["word_idx"], "aporta": b.get("aporta"), "tipo_rotulista": b["tipo"],
                "a_pantalla": b["a_pantalla"], "por_que": b.get("por_que") or "", "t1": b["t1"],
                "lectura_s": b["lectura_s"], "movido": b.get("movido"), "movido_corte": b.get("movido_corte"),
                "forzado": b.get("forzado"), **({"editado": True} if b.get("editado") else {}),
                "papel": True, "estilo": b.get("estilo"), "ancla_palabra": b.get("ancla_palabra"),
                "sin_alinear": b.get("sin_alinear")}
        fila = {"pool_id": pid, "tipo": b["tipo"], "etiqueta": b["etiqueta"], "texto": b["pantalla"],
                "sentence_idx": b["sentence_idx"], "word_idx": b["word_idx"], "palabra": b.get("palabra"), "t0": t0,
                "t1": b["t1"], "aporta": b.get("aporta"), "beat": b["beat"], "a_pantalla": b["a_pantalla"],
                "movido": b.get("movido")}
        if pid in used_before:
            filas.append({**fila, "accion": "fuera", "regla": "ya_mostrado", "motivo": "ya se mostró en un cap anterior"})
            continue
        if b["tipo"] == "cita":                        # F36 aclaración 6: la cita es una ficha (title card) con autor
            if not it.get("autor"):
                filas.append({**fila, "accion": "fuera", "regla": "zona", "motivo": "la cita no tiene autor"})
                continue
            plan["callouts"].append({"text": f"«{b['pantalla']}» — {it['autor']}", "kicker": b["etiqueta"] or "",
                                     "author": it["autor"], "ficha": True, "start": t0, "kind": "quote",
                                     "duration": dur, "side": "left", "fact_idx": None, **meta})
            filas.append({**fila, "accion": "colocado", "como": "ficha (cita)"})
            continue
        if b["tipo"] in FICHA:
            plan["callouts"].append({"text": b["pantalla"], "kicker": b["etiqueta"] or "", "ficha": True, "start": t0,
                                     "kind": KIND_FICHA[b["tipo"]], "duration": dur, "side": "left", "fact_idx": None,
                                     **meta})
        elif b["tipo"] == "documento":
            plan["archive_clippings"].append({"kicker": b["etiqueta"] or short_source(it.get("fuente")),
                                              "headline": b["pantalla"], "body": "", "scene_idx": sc.idx,
                                              "fact_idx": None, "fuente": it.get("fuente"), "era_decade": 2000,
                                              "start": t0, "duration": dur, "side": side, **meta})
        filas.append({**fila, "accion": "colocado"})
    plan["callouts"].sort(key=lambda c: c["start"])
    plan["archive_clippings"].sort(key=lambda c: c["start"])
    plan["rotulista"] = {"modelo": res.get("modelo"), "faltan_a_pantalla": v.get("faltan"),
                         "motivo_faltan": v.get("motivo_faltan") or {}, "filas": filas, "error": res.get("error"),
                         "director_antes": {k: (len(x) if isinstance(x, list) else bool(x)) for k, x in viejos.items()}}
    log.append(f"  rotulista: colocados {[(f['pool_id'], f['tipo'], f['texto']) for f in filas if f['accion'] == 'colocado']}"
               f" · fuera {[(f.get('pool_id'), f.get('regla'), f.get('motivo')) for f in filas if f['accion'] == 'fuera']}")
    return filas


# ═══════════════════════ ediciones a mano (F32 §A.5: fase2b --plan-edit) ═══════════════════════


# ═══════════════════════ nunca al mismo tiempo (DECISIONES 17:58; §0 animaciones, §A.5 zona de la ficha) ═══════════════════════

def unidades(scenes: list[Any], ent: dict[str, Any]) -> list[Any]:
    """F34 §A.3.2: la unidad de «una cosa por …». Con más de una escena, las escenas. En un cap de UNA sola escena (Veo),
    las oraciones: cada una va de su inicio al inicio de la siguiente (la primera desde el inicio de la escena, la última
    hasta su fin); `idx` = la oración."""
    from types import SimpleNamespace
    sents = ent.get("oraciones") or []
    if len(scenes) != 1 or not sents:
        return list(scenes)
    sc = scenes[0]
    out = []
    for k, s in enumerate(sents):
        a = float(sc.start) if k == 0 else float(s["t0"])
        b = float(sents[k + 1]["t0"]) if k + 1 < len(sents) else float(sc.end)
        out.append(SimpleNamespace(idx=s["idx"], start=round(a, 3), end=round(max(a, b), 3),
                                   quiet_side=getattr(sc, "quiet_side", "right"), oracion=True))
    return out


def _cubre(us: list[Any], a: float, b: float) -> list[Any]:
    """Las unidades que toca el tramo [a, b) (al menos la de `a`)."""
    from script_engine.gfx_project import scene_at
    out = [u for u in us if u.start < b and u.end > a]
    return out or [scene_at(us, a)]


def choca(iv: list[tuple[float, float, str]], a: float, b: float) -> list[str]:
    """DECISIONES 2026-10-26 17:58 («nunca al mismo tiempo»): lo que ya está en pantalla y se solapa o se toca con
    [a, b] (intervalos cerrados: terminar justo cuando el otro empieza también choca)."""
    return [q for x, y, q in iv if a <= y + 1e-6 and x <= b + 1e-6]


def escena_final(plan: dict[str, Any], scenes: list[Any], ent: dict[str, Any], log: list[str]) -> list[dict[str, Any]]:
    """Nunca al mismo tiempo (DECISIONES 17:58; antes «una cosa por escena», F29c–F34): dos bloques —title card, texto,
    reloj— no se solapan ni se tocan; la escena deja de ser la unidad (las de Veo duran 40–100 s). Corre después del
    crítico de los candidatos y antes del reloj contra el corte y de los sellos:
    - fijo: el title card (0 → title_dur);
    - los recortes (estilo papel), por prioridad (`a_pantalla`, después t0): si chocan con algo, esperan al inicio de la
      escena siguiente de su beat (en un cap de una sola escena, la oración siguiente: `unidades`) donde no choquen; si
      no hay lugar, no van;
    - el reloj: si choca, arranca en la escena siguiente de su beat (sin pasar un cambio de fecha y con ≥ TICKER_MIN en
      pantalla) o no va;
    - las fichas (§A.5): si chocan, esperan a la escena siguiente del beat o no van.
    Información > clima (F34 §A.3.1): los sellos los pone después clima.sellos_del_papel en lo que queda libre. Al
    moverse, un bloque arranca en el corte nuevo y su fin se recalcula con §A.2. Devuelve las filas."""
    from gfx_config import gfx_rules
    from script_engine.gfx_pool import TICKER_MIN
    from script_engine.gfx_project import scene_at
    filas: list[dict[str, Any]] = []
    if not scenes:
        return filas
    sents = ent["oraciones"]
    beats = ent["beats"]
    us = unidades(scenes, ent)
    por_oracion = len(us) != len(scenes) or (us and getattr(us[0], "oracion", False))
    nombre = "oración" if por_oracion else "escena"

    def beat_en(t: float) -> dict | None:
        for b in beats:
            if b["t0"] - 0.3 <= t <= b["t1"]:
                return b
        prev = [b for b in beats if b["t0"] <= t]
        return prev[-1] if prev else (beats[0] if beats else None)

    def momentos_del_beat_desde(t: float, b: dict | None) -> list[Any]:
        return [s for s in us if s.start > t + 1e-6 and b is not None and b["t0"] - 0.3 <= s.start <= b["t1"]]

    def oracion_en(t: float) -> int:
        k = next((s["idx"] for s in sents if s["t0"] <= t <= s["t1"]), None)
        return k if k is not None else next((s["idx"] for s in sents if s["t0"] >= t), len(sents) - 1)

    iv: list[tuple[float, float, str]] = []

    def tramo(b: dict) -> tuple[float, float]:
        return float(b["start"]), float(b["start"]) + float(b.get("duration") or 0.0)

    def ocupa(b: dict, que: str) -> None:
        iv.append((*tramo(b), que))
    if plan.get("title_card"):
        iv.append((0.0, float(gfx_rules.title_dur), "title card"))

    def mover(b: dict) -> str | None:
        """Mueve el bloque al primer momento de su beat (inicio de escena u oración) donde no choca; el motivo si no."""
        a0 = float(b["start"])
        for s2 in momentos_del_beat_desde(a0, beat_en(a0)):
            si = oracion_en(s2.start)
            chars = caracteres(b.get("tipo_rotulista", ""), b.get("kicker") or b.get("etiqueta"),
                               str(b.get("text") or b.get("headline") or ""), str(b.get("author") or ""))
            t1, sin_t = tiempos(sents, si, round(s2.start, 3), chars, scenes)
            if sin_t or choca(iv, s2.start, t1):
                continue
            b["movido_escena"] = (f"{a0:.2f} → {s2.start:.2f} s ({nombre} {scene_at(us, a0).idx} → {s2.idx})")
            b["start"], b["t1"], b["duration"] = round(s2.start, 3), t1, round(t1 - s2.start, 3)
            if "scene_idx" in b:
                b["scene_idx"] = s2.idx
            return None
        return "no hay otro momento libre en su beat (con tiempo de lectura)"

    def fuera(campo: str, b: dict, motivo: str) -> None:
        filas.append({"pool_id": b.get("pool_id"), "tipo": b.get("tipo_rotulista"),
                      "texto": b.get("text") or b.get("headline"), "t0": b.get("start"),
                      "regla": "zona", "accion": "fuera", "motivo": motivo, "campo": campo})

    def prio(b: dict) -> tuple:
        return (not b.get("a_pantalla"), float(b["start"]))

    # 1. los recortes (el estilo papel)
    for a in sorted([a for a in plan.get("archive_clippings") or [] if a.get("rotulista")], key=prio):
        hay = choca(iv, *tramo(a))
        if not hay:
            ocupa(a, "archive_clippings")
            continue
        motivo = f"se solapa con {', '.join(sorted(set(hay)))}"
        no = mover(a)
        if no:
            fuera("archive_clippings", a, f"{motivo}; {no}")
            plan["archive_clippings"] = [x for x in plan["archive_clippings"] if x is not a]
        else:
            ocupa(a, "archive_clippings")
    # 2. el reloj (F34 §A.3.1: el sello no lo frena)
    tk = plan.get("time_ticker")
    if tk:
        end = float(tk["start"]) + float(tk["duration"])
        bt = beat_en(float(tk["start"]))
        motivo = None
        c0 = choca(iv, float(tk["start"]), end)
        if c0:
            cambios = [float(c["t"]) for c in tk.get("changes") or []]
            nuevo = next((s.start for s in momentos_del_beat_desde(float(tk["start"]), bt)
                          if not choca(iv, s.start, end) and end - s.start >= TICKER_MIN
                          and not any(float(tk["start"]) < c <= s.start for c in cambios)), None)
            if nuevo is None:
                motivo = f"se solapa con {', '.join(sorted(set(c0)))} y no hay otro momento libre en su beat"
            else:
                filas.append({"bloque": "time_ticker", "regla": "zona", "accion": "movido",
                              "motivo": f"{float(tk['start']):.2f} → {nuevo:.2f} s (se solapaba con "
                                        f"{', '.join(sorted(set(c0)))})"})
                tk["start"], tk["duration"] = round(nuevo, 3), round(end - nuevo, 3)
        if motivo:
            filas.append({"bloque": "time_ticker", "texto": f"{tk.get('day')} {tk.get('month')}", "t0": tk["start"],
                          "regla": "zona", "accion": "fuera", "motivo": motivo})
            plan["time_ticker"] = None
        else:
            ocupa(tk, "reloj")
    # 3. las fichas
    for c in sorted([c for c in plan.get("callouts") or [] if c.get("ficha")], key=prio):
        hay = choca(iv, *tramo(c))
        if not hay:
            ocupa(c, "ficha")
            continue
        motivo = f"se solapa con {', '.join(sorted(set(hay)))}"
        no = mover(c)
        if no:
            fuera("callouts", c, f"{motivo}; {no}")
            plan["callouts"] = [x for x in plan["callouts"] if x is not c]
        else:
            filas.append({"pool_id": c.get("pool_id"), "tipo": c.get("tipo_rotulista"), "texto": c["text"],
                          "regla": "zona", "accion": "movido", "motivo": f"{motivo} → {c['movido_escena']}"})
            ocupa(c, "ficha")
    plan["callouts"] = sorted(plan.get("callouts") or [], key=lambda c: c["start"])
    rot = plan.setdefault("rotulista", {})
    rot["escena"] = filas
    log.append(f"  rotulista (nunca al mismo tiempo): {[(f.get('pool_id') or f.get('bloque'), f['accion'], f['motivo']) for f in filas]}"
               f" · title card {gfx_rules.title_dur:.1f} s")
    return filas
