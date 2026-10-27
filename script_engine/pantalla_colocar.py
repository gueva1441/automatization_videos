"""
script_engine/pantalla_colocar.py — dónde y cuánto va cada texto del guion en papel (F36 §A: movido de pantalla_entrada;
F37 §B.5: antes pantalla_colocar). `duracion`/`tiempos` (F37 §B.2: la lectura —caracteres ÷ 15— acotada entre
callout_dur_min y callout_dur_max, nunca después del corte), `instantes` y `pesos` (F37 §B.1: la escalera de intentos
de un bloque que no entra), `colocar` (los bloques del papel en el plan; ficha, cita como ficha con autor, papel =
recorte), `repartir` (nunca al mismo tiempo, DECISIONES 17:58, + el crítico en cada intento: mover en vez de cortar;
reemplaza a escena_final) y `hasta_el_corte` (el reloj). F36 §D: sin agua, contador, lupa ni ediciones del plan.
"""
from __future__ import annotations

from typing import Any, Callable

from script_engine import evidence as ev

LECTURA_CPS = 15.0             # §0: mínimo de lectura = caracteres ÷ 15 cps (estándar de subtitulado, el más lento)


def _escena_de(escenas: list[Any] | None, t: float) -> Any | None:
    if not escenas:
        return None
    for s in escenas:
        if s.start <= t < s.end:
            return s
    return escenas[-1]


def duracion(chars: int) -> tuple[float, float]:
    """F37 §B.2: (lectura, duración) de una ficha: lectura = caracteres ÷ 15 cps; duración = la lectura acotada entre
    `callout_dur_min` y `callout_dur_max` (identidad F3, perfil)."""
    from gfx_config import gfx_rules
    need = chars / LECTURA_CPS
    return need, min(max(need, float(gfx_rules.callout_dur_min)), float(gfx_rules.callout_dur_max))


def tiempos(t0: float, chars: int, escenas: list[Any] | None = None) -> tuple[float, str | None]:
    """F37 §B.2: (t1, motivo si no va). t1 = t0 + la duración de la ficha (`duracion`), nunca después del corte de la
    escena que contiene t0; si lo que queda no alcanza la lectura, no va desde ahí (antes: hasta el fin de la oración o
    de la siguiente, sin tope: T16 duraba 12.7 s)."""
    from gfx_config import gfx_rules
    need, dur = duracion(chars)
    t1 = t0 + dur
    sc = _escena_de(escenas, t0)
    if sc is not None:
        t1 = min(t1, sc.end)
    t1 = round(t1, 3)
    if t1 - t0 < need - 5e-4:                    # derivado: t1 va redondeado al milisegundo
        if need > float(gfx_rules.callout_dur_max):
            return t1, (f"sin tiempo de lectura: {chars} caracteres piden {need:.1f} s y una ficha dura como máximo "
                        f"{float(gfx_rules.callout_dur_max):.1f} s (callout_dur_max)")
        return t1, (f"sin tiempo de lectura: {chars} caracteres piden {need:.1f} s y hay {t1 - t0:.1f} s"
                    + (f" hasta el corte de escena ({sc.end:.1f} s)" if sc is not None and t1 == round(sc.end, 3) else ""))
    return t1, None


def instantes(sents: list[dict], si: int, escenas: list[Any] | None, *, ancla: float | None = None,
              peso: float | None = None) -> list[tuple[float, int, str]]:
    """F37 §B.1: los instantes que se prueban, en orden, para un bloque anclado a la oración `si` (sin números nuevos):
    1) dentro de la misma oración: el instante original (la palabra ancla de la ficha, la palabra de más peso del
       sello), después la palabra de más peso, el inicio de la oración y la palabra ancla;
    2) el inicio de la escena siguiente, si cae dentro de la misma oración;
    3) el inicio de la oración siguiente, si es del mismo beat.
    [(t, oración, cómo)], sin repetidos. El 4 (otra posición de pantalla) es del crítico: lo prueba quien reparte."""
    s = sents[si]
    out: list[tuple[float, int, str]] = []

    def add(t: float | None, k: int, como: str) -> None:
        if t is not None and all(abs(t - x) > 1e-6 for x, _, _ in out):
            out.append((round(float(t), 3), k, como))
    original = ancla if ancla is not None else peso
    add(original, si, "1 · palabra ancla" if ancla is not None else "1 · palabra de más peso")
    add(peso, si, "1 · palabra de más peso")
    add(s["t0"], si, "1 · inicio de la oración")
    add(ancla, si, "1 · palabra ancla")
    base = out[0][0] if out else float(s["t0"])
    for e in escenas or []:
        if base + 1e-6 < float(e.start) <= float(s["t1"]):
            add(float(e.start), si, f"2 · inicio de la escena {e.idx}")
            break
    if si + 1 < len(sents) and sents[si + 1].get("beat") == s.get("beat"):
        add(sents[si + 1]["t0"], si + 1, f"3 · oración siguiente [{si + 1}]")
    return out


def pesos(words: list[dict], time_offset: float, moods: dict | None) -> dict[int, float]:
    """F37 §B.1: {oración: instante de su palabra de más peso} (clima.peak_word sobre el léxico de moods; la oración
    sin palabra de peso no está). Las oraciones son las de gfx_peak.sentences = las de voz_utils.oraciones."""
    from script_engine.clima import peak_word
    from script_engine.gfx_peak import sentences
    out: dict[int, float] = {}
    if not moods:
        return out
    for k, s in enumerate(sentences(words, time_offset)):
        h = peak_word(s, words, moods)
        if h:
            out[k] = round(float(words[h["i"]]["start"]) + time_offset, 3)
    return out


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
    """Los bloques del guion en papel en el plan (F37 §B.4: el papel es el único camino). Con `words`, los
    filtros (`validar_papel`) corren con las escenas reales (el fin muere en el corte). Forma por estilo (aclaración 6):
    normal y nombre → ficha (el title card), cita → ficha con «dato» — autor, papel → recorte. Devuelve una fila por
    bloque (colocado o fuera, con la regla y el motivo)."""
    from script_engine.gfx_pool import short_source
    from script_engine.gfx_project import scene_at
    from script_engine.pantalla_filtros import FICHA, validar_papel   # F36 §A: filtros importa este módulo arriba
    its = ev.items(pool) if pool else {}
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
                "sin_alinear": b.get("sin_alinear"), "intentos": b.get("intentos") or [],
                "intentos_fallidos": b.get("intentos_fallidos") or []}
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
                         "motivo_faltan": v.get("motivo_faltan") or {}, "filas": filas, "error": res.get("error")}
    log.append(f"  rotulista: colocados {[(f['pool_id'], f['tipo'], f['texto']) for f in filas if f['accion'] == 'colocado']}"
               f" · fuera {[(f.get('pool_id'), f.get('regla'), f.get('motivo')) for f in filas if f['accion'] == 'fuera']}")
    return filas


# ═══════════════════════ repartir: nunca al mismo tiempo + crítico, moviendo (DECISIONES 17:58; F37 §B.1) ═══════════════════════

def choca(iv: list[tuple[float, float, str]], a: float, b: float) -> list[str]:
    """DECISIONES 2026-10-26 17:58 («nunca al mismo tiempo»): lo que ya está en pantalla y se solapa o se toca con
    [a, b] (intervalos cerrados: terminar justo cuando el otro empieza también choca)."""
    return [q for x, y, q in iv if a <= y + 1e-6 and x <= b + 1e-6]


OTRO_LADO = {"left": "right", "right": "left"}


def lados(b: dict[str, Any], kind: str) -> list[str]:
    """F37 §B.1 paso 4 (solo para el crítico): las posiciones que la plantilla YA soporta. El recorte y el sello van a
    la izquierda o a la derecha (gfx_project: `side`); la ficha tiene una sola (la del title card): sin paso 4."""
    lado = str(b.get("side") or "right")
    return [lado] if kind == "ficha" else [lado, OTRO_LADO.get(lado, "left")]


def probar(b: dict[str, Any], kind: str, intentos: list[dict[str, Any]], iv: list[tuple[float, float, str]],
           juez: Callable[..., dict] | None) -> tuple[dict[str, Any] | None, list[str], dict | None]:
    """Prueba los intentos de un bloque en orden: el primero que no choca con lo ya puesto y que el crítico no tira
    (en cada posición que la plantilla soporta) gana. (intento elegido con su lado, por qué falló cada uno, fila del
    crítico)."""
    fallas: list[str] = []
    for k, at in enumerate(intentos):
        t0, t1 = float(at["t0"]), float(at["t1"])
        hay = choca(iv, t0, t1)
        if hay:
            fallas.append(f"{at['como']} ({t0:.2f} s): se solapa con {', '.join(sorted(set(hay)))}")
            continue
        ls = lados(b, kind)
        for j, lado in enumerate(ls):
            cand = {**b, "start": round(t0, 3), "duration": round(t1 - t0, 3), "t1": round(t1, 3),
                    "sentence_idx": at.get("si", b.get("sentence_idx")), "side": lado}
            row = juez(kind, cand) if juez is not None else None
            if row is not None and not row["pasa"]:
                fallas.append(f"{at['como']} ({t0:.2f} s){' · lado ' + lado if len(ls) > 1 else ''}: estorba — "
                              f"{row['motivo']}")
                continue
            return {**at, "lado": lado, "lado_cambio": j > 0}, fallas, row
    return None, fallas, None


def repartir(plan: dict[str, Any], scenes: list[Any], ent: dict[str, Any], log: list[str], *,
             juez: Callable[..., dict] | None = None) -> list[dict[str, Any]]:
    """F37 §B.1 (reemplaza a escena_final): nunca al mismo tiempo (DECISIONES 17:58) y el crítico «¿estorba?» (B.2),
    moviendo en vez de cortar. Lo que el autor eligió no se corta por una razón mecánica: cada bloque prueba sus
    intentos (`instantes`: 1 otro instante de su oración, 2 el inicio de la escena siguiente dentro de ella, 3 la oración
    siguiente del beat; las fichas y recortes ya traen de los filtros los que entran en su lectura) y, contra el
    crítico, 4 las otras posiciones que la plantilla soporta (`lados`). Orden de reparto: el title card (fijo), los
    recortes y el reloj (información), las fichas (por prioridad: `a_pantalla`, después t0); los sellos los pone
    después clima.sellos_del_papel con la misma escalera. `juez(kind, bloque)` → fila del crítico
    (gfx_critic.estorba); sin juez, sin crítico. Si nada entra: «papel sin colocar» con cada intento y por qué falló."""
    from gfx_config import gfx_rules
    from script_engine.gfx_pool import TICKER_MIN
    filas: list[dict[str, Any]] = []
    rot = plan.setdefault("rotulista", {})
    rot["escena"] = filas
    plan["critico_rotulista"] = []
    if not scenes:
        return filas
    sents = ent["oraciones"]
    iv: list[tuple[float, float, str]] = []
    if plan.get("title_card"):
        iv.append((0.0, float(gfx_rules.title_dur), "title card"))

    def oracion_en(t: float) -> int:
        k = next((s["idx"] for s in sents if s["t0"] <= t <= s["t1"]), None)
        return k if k is not None else next((s["idx"] for s in sents if s["t0"] >= t), len(sents) - 1)

    def prio(b: dict) -> tuple:
        return (not b.get("a_pantalla"), float(b["start"]))

    def colocar_uno(campo: str, b: dict, kind: str) -> bool:
        intentos = b.get("intentos") or [{"t0": float(b["start"]), "t1": float(b["start"]) + float(b.get("duration") or 0),
                                          "si": b.get("sentence_idx"), "como": "1 · donde estaba"}]
        t_antes = float(b["start"])
        at, fallas, row = probar(b, kind, intentos, iv, juez)
        if at is None:
            filas.append({"pool_id": b.get("pool_id"), "tipo": b.get("tipo_rotulista"), "campo": campo,
                          "texto": b.get("text") or b.get("headline"), "t0": t_antes, "accion": "fuera",
                          "regla": "colocar", "quien": "colocar (intentos)",
                          "motivo": "no entra en ningún intento: " + " · ".join(fallas), "intentos": fallas})
            return False
        b["start"], b["t1"], b["duration"] = round(at["t0"], 3), round(at["t1"], 3), round(at["t1"] - at["t0"], 3)
        b["side"] = at["lado"]
        if at.get("si") is not None:
            b["sentence_idx"] = at["si"]
        if row is not None:
            b["critico"] = {"pregunta": "¿estorba?", "estorba": False if row["pasa"] else True,
                            "motivo_3": row["motivo"], **({"error": row["motivo"]} if row["veredicto"] == "error" else {})}
            plan["critico_rotulista"].append({**row, "pool_id": b.get("pool_id"), "a_pantalla": b.get("a_pantalla")})
        if fallas or abs(at["t0"] - t_antes) > 1e-6 or at.get("lado_cambio"):
            b["movido_escena"] = (f"{t_antes:.2f} → {at['t0']:.2f} s ({at['como']}"
                                  + (f", lado {at['lado']}" if at.get("lado_cambio") else "") + ")")
            filas.append({"pool_id": b.get("pool_id"), "tipo": b.get("tipo_rotulista"), "campo": campo,
                          "texto": b.get("text") or b.get("headline"), "t0": at["t0"], "accion": "movido",
                          "regla": "colocar", "motivo": b["movido_escena"] + (f" · antes: {' · '.join(fallas)}"
                                                                                if fallas else ""),
                          "intentos": fallas})
        iv.append((at["t0"], at["t1"], "recorte" if campo == "archive_clippings" else "ficha"))
        return True

    # 1. los recortes (el estilo papel)
    for a in sorted([a for a in plan.get("archive_clippings") or [] if a.get("rotulista")], key=prio):
        if not colocar_uno("archive_clippings", a, "recorte"):
            plan["archive_clippings"] = [x for x in plan["archive_clippings"] if x is not a]
    # 2. el reloj (F34 §A.3.1: el sello no lo frena): la misma escalera, sin crítico; queda ≥ TICKER_MIN en pantalla y no
    # arranca después de un cambio de fecha; hasta_el_corte (después) lo corta en el corte de su escena
    tk = plan.get("time_ticker")
    if tk:
        a0, end = float(tk["start"]), float(tk["start"]) + float(tk["duration"])
        cambios = [float(c["t"]) for c in tk.get("changes") or []]
        k = oracion_en(a0)
        fallas = []
        elegido = None
        for t, _, como in instantes(sents, k, scenes, ancla=a0, peso=(ent.get("peso") or {}).get(k)):
            if end - t < TICKER_MIN:
                fallas.append(f"{como} ({t:.2f} s): quedaría menos de {TICKER_MIN} s")
            elif any(min(a0, t) < c <= max(a0, t) for c in cambios):
                fallas.append(f"{como} ({t:.2f} s): pasa un cambio de fecha")
            elif choca(iv, t, end):
                fallas.append(f"{como} ({t:.2f} s): se solapa con {', '.join(sorted(set(choca(iv, t, end))))}")
            else:
                elegido = (t, como)
                break
        if elegido is None:
            filas.append({"bloque": "time_ticker", "texto": f"{tk.get('day')} {tk.get('month')}", "t0": a0,
                          "regla": "colocar", "quien": "colocar (intentos)", "accion": "fuera",
                          "motivo": "no entra en ningún intento: " + " · ".join(fallas), "intentos": fallas})
            plan["time_ticker"] = None
        else:
            t, como = elegido
            if abs(t - a0) > 1e-6:
                filas.append({"bloque": "time_ticker", "regla": "colocar", "accion": "movido",
                              "motivo": f"{a0:.2f} → {t:.2f} s ({como})" + (f" · antes: {' · '.join(fallas)}"
                                                                            if fallas else ""), "intentos": fallas})
            tk["start"], tk["duration"] = round(t, 3), round(end - t, 3)
            iv.append((t, end, "reloj"))
    # 3. las fichas (la cita es una ficha con autor)
    for c in sorted([c for c in plan.get("callouts") or [] if c.get("ficha")], key=prio):
        if not colocar_uno("callouts", c, "ficha"):
            plan["callouts"] = [x for x in plan["callouts"] if x is not c]
    plan["callouts"] = sorted(plan.get("callouts") or [], key=lambda c: c["start"])
    plan["archive_clippings"] = sorted(plan.get("archive_clippings") or [], key=lambda c: c["start"])
    log.append(f"  colocar (intentos): {[(f.get('pool_id') or f.get('bloque'), f['accion'], f['motivo']) for f in filas]}"
               f" · title card {gfx_rules.title_dur:.1f} s")
    return filas
