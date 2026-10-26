"""
script_engine/rotulista_colocar.py — F36 §A: dónde y cuánto va cada bloque del rotulista (movido de gfx_rotulista sin
cambios). `tiempos` y `despues_del_corte` (§A.2: fin de la oración ancla, lectura caracteres ÷ 15, nunca después del
corte), `colocar` (cifra/hecho/persona → ficha, documento → recorte, cita, lupa; la cifra como agua o contador con
`animacion_de_cifra`), las ediciones a mano (`fase2b --plan-edit`: `aplicar_ediciones`, `guardar_ediciones`,
`mover_a_escena`), la caja de la lupa y la escena (`unidades`, `escena_final`: una cosa por escena u oración).
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Callable

from script_engine import evidence as ev
from script_engine.voz_utils import _MAGNITUD, _UNIDAD_1, _analiza, _num_tok, _toks, numero_en

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
    """Lo que se lee del bloque: etiqueta + dato (la cita, con su autor)."""
    return len(etiqueta or "") + len(texto) + (len(autor) if tipo == "cita" else 0)


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
    """F36 §B.4: el agua y el reloj no cruzan el corte de la escena donde arrancan: duración = min(la que traen,
    corte − inicio − 1 cuadro) (derivado). Corre después de escena_final (que puede mover el reloj)."""
    from script_engine.gfx_project import scene_at
    filas: list[dict[str, Any]] = []
    if not scenes:
        return filas
    for campo in ("water_level", "time_ticker"):
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
    log.append(f"  agua y reloj contra el corte: {[(f['bloque'], f['motivo']) for f in filas] or 'nada que acortar'}")
    return filas


# ═══════════════════════ colocar ═══════════════════════

KIND_FICHA = {"cifra": "figure", "persona": "name", "hecho": "fact"}
UNIDAD_CONTADOR = ("personas", "liras")      # §B.7: cantidad de personas o dinero → contador


def animacion_de_cifra(b: dict[str, Any], fuente: str) -> tuple[str, dict[str, Any]] | None:
    """F32 §B.7: la cifra del rotulista (con su `unidad` y `valor`) como animación. Metros de un nivel (el texto o su
    dato nombran el nivel o la cota) → water_level; personas o dinero → count_up. Lo que se muestra es la cifra tal
    como está en el texto (para el candado literal); si no se puede, None (queda la ficha). Sin `unidad`/`valor` en la
    respuesta (el formato de salida del USER no los nombra y el prompt no se toca más que por la línea de §B.7), se
    leen del texto del bloque: la primera cifra seguida de una unidad conocida (lectura declarada, F32_REPORT)."""
    from gfx_config import gfx_rules
    from script_engine.gfx_peak import WATER_DUR, WATER_FULL_M
    from script_engine.gfx_project import format_count, parse_count_literal
    u = _UNIDAD_1.get(ev.norm(str(b.get("unidad") or "")).replace("³", "3"), None)
    txt = str(b.get("pantalla") or b.get("texto") or "")
    try:
        val = float(str(b.get("valor")).replace(",", "."))
    except (TypeError, ValueError):
        val = None
    if u is None and val is None:                    # respaldo: la cifra y su unidad, del texto del bloque
        for v, uu, _ in _analiza(txt)[0]:
            if uu and uu != "diferencia":
                u, val = uu, v
                break
    if u is None or val is None:
        return None
    for m in re.finditer(r"(\d[\d.,]*\d|\d)\s*([^\W\d_]+|m³)?", txt):
        num, unit_w = m.group(1), m.group(2) or ""
        if not numero_en(num, str(b.get("valor"))) and abs((_num_tok(num) or -1) - val) > 1e-9:
            continue
        if u == "m" and unit_w and _UNIDAD_1.get(ev.norm(unit_w)) == "m" and any(
                any(t.startswith(r) for r in _MAGNITUD["nivel"]) for t in _toks(f"{txt} {b.get('etiqueta') or ''} {fuente}")):
            meters = val
            return "water_level", {"value_text": num, "unit": unit_w, "meters": round(meters, 2),
                                   "height": round(min(0.85, max(0.15, meters / WATER_FULL_M)), 3), "rise": WATER_DUR[0]}
        if u in UNIDAD_CONTADOR and unit_w and _UNIDAD_1.get(ev.norm(unit_w)) == u:
            spec = parse_count_literal(num)
            dur_cu = gfx_rules.count_dur + gfx_rules.count_hold_sec          # el contador dura lo que dura (plantilla)
            if spec is not None and format_count(spec["value"], spec) == num and float(b.get("lectura_s") or 0) <= dur_cu:
                return "count_up", {"value_text": num, "unit": unit_w, "source": b.get("etiqueta") or "",
                                    "duration": round(dur_cu, 3)}
    return None


def colocar(plan: dict[str, Any], res: dict[str, Any], ent: dict[str, Any], *, scenes: list[Any], pool: dict | None,
            used_before: set[str], lupa_box: Callable[[int, str], tuple[list[float], str] | None] | None,
            zoom_dur: float, log: list[str], words: list[dict] | None = None, time_offset: float = 0.0
            ) -> list[dict[str, Any]]:
    """Los bloques del rotulista en el plan (reemplazan recortes, datos, cita, contador, nivel de agua y el zoom del
    director). Con `words`, la validación se rehace con las escenas reales (el fin muere en el corte). Devuelve una fila
    por bloque (colocado o fuera, con la regla y el motivo)."""
    from script_engine.gfx_pool import short_source
    from script_engine.gfx_project import scene_at
    from script_engine.rotulista_filtros import FICHA, validar      # F36 §A: filtros importa este módulo arriba
    its = ev.items(pool) if pool else {}
    viejos = {k: plan.get(k) for k in ("archive_clippings", "callouts", "quote_card", "count_up", "water_level",
                                       "evidence_zoom")}
    plan["archive_clippings"], plan["callouts"] = [], []
    for k in ("quote_card", "count_up", "water_level", "evidence_zoom"):
        plan[k] = None
    filas: list[dict[str, Any]] = []
    if words is not None and res.get("final") is not None:
        v = validar(res["final"], ent, words, time_offset, escenas=scenes)
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
                "forzado": b.get("forzado"), **({"editado": True} if b.get("editado") else {})}
        fila = {"pool_id": pid, "tipo": b["tipo"], "etiqueta": b["etiqueta"], "texto": b["pantalla"],
                "sentence_idx": b["sentence_idx"], "word_idx": b["word_idx"], "palabra": b.get("palabra"), "t0": t0,
                "t1": b["t1"], "aporta": b.get("aporta"), "beat": b["beat"], "a_pantalla": b["a_pantalla"],
                "movido": b.get("movido")}
        if pid in used_before:
            filas.append({**fila, "accion": "fuera", "regla": "ya_mostrado", "motivo": "ya se mostró en un cap anterior"})
            continue
        anim = animacion_de_cifra(b, str(it and ev.text_of(it) or "")) if b["tipo"] == "cifra" else None   # F32 §B.7
        if anim and plan.get(anim[0]) is None:
            campo, extra = anim
            plan[campo] = {"start": t0, "duration": dur, **extra, "etiqueta": b["etiqueta"], "word": b.get("palabra"),
                           **meta}
            filas.append({**fila, "accion": "colocado", "como": campo})
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
        elif b["tipo"] == "cita":
            if not it.get("autor"):
                filas.append({**fila, "accion": "fuera", "regla": "zona", "motivo": "la cita no tiene autor"})
                continue
            plan["quote_card"] = {"text": b["pantalla"], "author": it["autor"], "start": t0, "duration": dur, **meta}
        elif b["tipo"] == "lupa":
            got = lupa_box(sc.idx, b["pantalla"]) if lupa_box else None
            if got is None:
                filas.append({**fila, "accion": "fuera", "regla": "zona",
                              "motivo": f"visión no encuentra «{b['pantalla']}» en la escena {sc.idx}"})
                continue
            if sc.end - t0 < zoom_dur:
                filas.append({**fila, "accion": "fuera", "regla": "lectura",
                              "motivo": f"la escena termina {sc.end - t0:.1f} s después (el zoom pide {zoom_dur:.1f})"})
                continue
            box, label = got
            plan["evidence_zoom"] = {"scene_idx": sc.idx, "box": box, "start": t0, "anchor": label, "detail": label,
                                     "como": "rotulista", **meta}
        filas.append({**fila, "accion": "colocado"})
    plan["callouts"].sort(key=lambda c: c["start"])
    plan["archive_clippings"].sort(key=lambda c: c["start"])
    plan["rotulista"] = {"modelo": res.get("modelo"), "faltan_a_pantalla": v.get("faltan"),
                         "motivo_faltan": v.get("motivo_faltan") or {},
                         "a_pantalla_incompletos": v.get("incompletos") or {}, "filas": filas,
                         "error": res.get("error"),
                         "director_antes": {k: (len(x) if isinstance(x, list) else bool(x)) for k, x in viejos.items()}}
    log.append(f"  rotulista: colocados {[(f['pool_id'], f['tipo'], f['texto']) for f in filas if f['accion'] == 'colocado']}"
               f" · fuera {[(f.get('pool_id'), f.get('regla'), f.get('motivo')) for f in filas if f['accion'] == 'fuera']}")
    return filas


# ═══════════════════════ ediciones a mano (F32 §A.5: fase2b --plan-edit) ═══════════════════════

EDICIONES = "plan_edits.json"
CAMPOS_EDITABLES = ("texto", "etiqueta", "word_idx", "sentence_idx", "tipo", "aporta")


def ediciones_de(work_dir: Path, cap_id: str) -> list[dict[str, Any]]:
    """Las ediciones guardadas para un cap (`_fase2b_work/plan_edits.json`, en el orden en que se pidieron)."""
    f = Path(work_dir) / EDICIONES
    try:
        data = json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}
    except (OSError, ValueError):
        return []
    return [e for e in data.get("ediciones") or [] if str(e.get("cap")) == cap_id]


def guardar_ediciones(work_dir: Path, nuevas: list[dict[str, Any]]) -> Path:
    """Suma ediciones a las guardadas (las nuevas van después: si tocan lo mismo, ganan)."""
    f = Path(work_dir) / EDICIONES
    try:
        data = json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}
    except (OSError, ValueError):
        data = {}
    data["ediciones"] = list(data.get("ediciones") or []) + list(nuevas)
    f.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    return f


def aplicar_ediciones(res: dict[str, Any], edits: list[dict[str, Any]], ent: dict[str, Any], log: list[str]
                      ) -> dict[str, Any]:
    """Las ediciones sobre la respuesta del rotulista (una copia: la caché no se toca): cambiar `texto`, `etiqueta`,
    `word_idx`, `sentence_idx`, `tipo` o `aporta` de un bloque (por `pool_id`), `borrar` un bloque o `agregar` uno de un
    ítem del pool. Después, el bloque editado pasa por todas las reglas (validar, colocar, escena, crítico) como
    cualquier otro; el crítico vuelve a mirar solo lo editado (su caché es por identidad del bloque)."""
    import copy
    out = copy.deepcopy(res)
    fin = out.get("final") if isinstance(out.get("final"), dict) else {"bloques": []}
    bl = [b for b in fin.get("bloques") or [] if isinstance(b, dict)]
    for e in edits:
        pid = str(e.get("pool_id") or (e.get("agregar") or {}).get("pool_id") or "")
        if e.get("agregar"):
            nb = {**e["agregar"], "rank": int(e["agregar"].get("rank") or 1), "editado": True}
            nb.setdefault("aporta", "(edición a mano)")
            bl.append(nb)
            log.append(f"  edición: agrega {pid} en la oración [{nb.get('sentence_idx')}]")
            continue
        if e.get("borrar"):
            antes = len(bl)
            bl = [b for b in bl if str(b.get("pool_id")) != pid]
            log.append(f"  edición: borra {pid} ({antes - len(bl)} bloque(s))")
            continue
        hit = [b for b in bl if str(b.get("pool_id")) == pid]
        if not hit:
            log.append(f"  edición: {pid} no está en la respuesta del rotulista (nada que cambiar)")
            continue
        for b in hit:
            for k in CAMPOS_EDITABLES:
                if k in e:
                    b[k] = e[k]
            b["editado"] = True
        cambios = [k for k in CAMPOS_EDITABLES if k in e]
        if cambios:
            log.append(f"  edición: {pid} cambia {cambios}")
    fin["bloques"] = bl
    out["final"] = fin
    out["validacion"] = None
    return out


def mover_a_escena(plan: dict[str, Any], edits: list[dict[str, Any]], scenes: list[Any], ent: dict[str, Any],
                   log: list[str]) -> None:
    """«escena»: el bloque (por `pool_id`) arranca en el primer cuadro de la escena k; su fin se recalcula con §A.2."""
    por_idx = {s.idx: s for s in scenes}
    for e in edits:
        if "escena" not in e:
            continue
        pid, sc = str(e.get("pool_id")), por_idx.get(int(e["escena"]))
        if sc is None:
            log.append(f"  edición: escena {e['escena']} no existe ({pid})")
            continue
        for campo in ("callouts", "archive_clippings", "quote_card", "water_level", "count_up"):
            bs = plan.get(campo)
            for b in (bs if isinstance(bs, list) else [bs] if bs else []):
                if str(b.get("pool_id")) != pid:
                    continue
                sents = ent["oraciones"]
                si = next((s["idx"] for s in sents if s["t0"] <= sc.start <= s["t1"]),
                          next((s["idx"] for s in sents if s["t0"] >= sc.start), len(sents) - 1))
                chars = caracteres(b.get("tipo_rotulista", ""), b.get("kicker") or b.get("etiqueta"),
                                   str(b.get("text") or b.get("headline") or b.get("value_text") or ""),
                                   str(b.get("author") or ""))
                t1, sin_t = tiempos(sents, si, round(sc.start, 3), chars, scenes)
                b["start"], b["t1"], b["duration"] = round(sc.start, 3), t1, round(t1 - sc.start, 3)
                b["editado"] = True
                if "scene_idx" in b:
                    b["scene_idx"] = sc.idx
                log.append(f"  edición: {pid} arranca en la escena {sc.idx} ({sc.start:.2f} s)"
                           + (f" — {sin_t}" if sin_t else ""))


def lupa_de_detalles(details: dict[int, list[dict]], verify: Callable[[int, dict], bool]
                     ) -> Callable[[int, str], tuple[list[float], str] | None]:
    """La caja del detalle que nombra la lupa: el detalle de visión de esa escena con más raíces en común con el texto
    (≥ 1), confirmado recortando la caja."""
    def box(si: int, texto: str) -> tuple[list[float], str] | None:
        want = {w[:4] for w in re.findall(r"[^\W\d_]{4,}", ev.norm(texto))}
        cands = sorted(((len(want & {w[:4] for w in re.findall(r"[^\W\d_]{4,}", ev.norm(d["label"]))}), d)
                        for d in details.get(si) or []), key=lambda x: -x[0])
        for n, d in cands:
            if n >= 1 and verify(si, d):
                return d["box"], d["label"]
        return None
    return box


# ═══════════════════════ escena (§0 animaciones, §A.5 zona de la ficha) ═══════════════════════

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


def escena_final(plan: dict[str, Any], scenes: list[Any], ent: dict[str, Any], log: list[str]) -> list[dict[str, Any]]:
    """Una cosa por escena (después del reloj y del sello, antes del realizador y del crítico):
    - F34 §A.3.2: en un cap de una sola escena la unidad es la oración (`unidades`): dos bloques nunca en la misma
      oración ni solapados en el tiempo (cada bloque ocupa todas las oraciones que toca);
    - F34 §A.3.1: información > clima: el sello (también el del pico) no es fijo ni frena al reloj, al agua ni a los
      textos; lo coloca después sellos_por_tema en lo que queda libre;
    - fijo: el title card (sus escenas);
    - los textos que no son ficha (documento, cita, lupa), por prioridad (`a_pantalla`, después t0): si su escena ya
      tiene otra cosa, el documento y la cita esperan a la escena siguiente del beat (la lupa no: su detalle está en esa
      foto) o no van;
    - el reloj (animación): nunca encima de un texto que no sea ficha ni en la escena del sello; uno por beat (si su
      beat tiene sello o lupa, no va); si choca, arranca en la escena siguiente de su beat (sin pasar un cambio de fecha
      y con ≥ TICKER_MIN en pantalla) o no va;
    - las fichas (§A.5): si en su escena hay title card, reloj, sello u otro bloque, esperan a la escena siguiente del
      beat o no van.
    Al moverse, un bloque arranca en el corte de la escena nueva y su fin se recalcula con §A.2. Devuelve las filas."""
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

    def beat_en(t: float) -> dict | None:
        for b in beats:
            if b["t0"] - 0.3 <= t <= b["t1"]:
                return b
        prev = [b for b in beats if b["t0"] <= t]
        return prev[-1] if prev else (beats[0] if beats else None)

    def escenas_del_beat_desde(sc: Any, b: dict | None) -> list[Any]:
        return [s for s in us if s.start > sc.start and b is not None and b["t0"] - 0.3 <= s.start <= b["t1"]]

    def oracion_en(t: float) -> int:
        k = next((s["idx"] for s in sents if s["t0"] <= t <= s["t1"]), None)
        return k if k is not None else next((s["idx"] for s in sents if s["t0"] >= t), len(sents) - 1)

    ocupa: dict[int, list[str]] = {}

    def marca(si: int, que: str) -> None:
        ocupa.setdefault(si, []).append(que)

    def marca_bloque(b: dict, que: str) -> None:
        """Por escena: la del inicio (como siempre). Por oración: todas las que el bloque toca."""
        a = float(b["start"])
        if not por_oracion:
            marca(scene_at(us, a).idx, que)
            return
        for u in _cubre(us, a, a + float(b.get("duration") or 0.0)):
            marca(u.idx, que)

    def libre_iv(u: Any, b: dict, a: float | None = None) -> bool:
        """Por oración: el bloque, arrancando en `a` (por defecto el inicio de `u`), no toca ninguna oración ocupada."""
        if not por_oracion:
            return not ocupa.get(u.idx)
        a = float(u.start) if a is None else a
        return not any(ocupa.get(x.idx) for x in _cubre(us, a, a + float(b.get("duration") or 0.0)))

    if plan.get("title_card"):
        for s in us:                           # todas las escenas (u oraciones) que pisa el title card (title_dur)
            if s.start < gfx_rules.title_dur:
                marca(s.idx, "title card")

    def mover(b: dict, desde: Any, libre: Callable[[Any], bool]) -> str | None:
        """Mueve el bloque a la primera escena libre de su beat; devuelve el motivo si no puede."""
        bt = beat_en(float(b["start"]))
        for s2 in escenas_del_beat_desde(desde, bt):
            if not libre(s2):
                continue
            si = oracion_en(s2.start)
            chars = caracteres(b.get("tipo_rotulista", ""), b.get("kicker") or b.get("etiqueta"),
                               str(b.get("text") or b.get("headline") or b.get("value_text") or ""), str(b.get("author") or ""))
            t1, sin_t = tiempos(sents, si, round(s2.start, 3), chars, scenes)
            if sin_t:
                continue
            b["movido_escena"] = f"{float(b['start']):.2f} → {s2.start:.2f} s (escena {desde.idx} → {s2.idx})"
            b["start"], b["t1"], b["duration"] = round(s2.start, 3), t1, round(t1 - s2.start, 3)
            if "scene_idx" in b:
                b["scene_idx"] = s2.idx
            return None
        return "no hay otra escena libre en su beat (con tiempo de lectura)"

    def fuera(campo: str, b: dict, motivo: str) -> None:
        filas.append({"pool_id": b.get("pool_id"), "tipo": b.get("tipo_rotulista"),
                      "texto": b.get("text") or b.get("headline") or b.get("detail"), "t0": b.get("start"),
                      "regla": "zona", "accion": "fuera", "motivo": motivo, "campo": campo})

    def prio(b: dict) -> tuple:
        return (not b.get("a_pantalla"), float(b["start"]))

    nombre = "la oración" if por_oracion else "la escena"
    # 1. textos que no son ficha (y las animaciones del rotulista y el agua de la voz, F34 §A.5)
    otros: list[tuple[str, dict]] = [("archive_clippings", a) for a in plan.get("archive_clippings") or []
                                     if a.get("rotulista")]
    for k in ("quote_card", "evidence_zoom", "water_level", "count_up"):      # F32 §B.7: agua y contador también
        if plan.get(k) and (plan[k].get("rotulista") or plan[k].get("de_voz")):
            otros.append((k, plan[k]))
    for campo, b in sorted(otros, key=lambda x: prio(x[1])):
        sc = scene_at(us, float(b["start"]))
        if libre_iv(sc, b, float(b["start"])):
            marca_bloque(b, campo)
            continue
        hay = sorted({q for x in (_cubre(us, sc.start, sc.start + float(b.get("duration") or 0.0)) if por_oracion
                                  else [sc]) for q in ocupa.get(x.idx) or []})
        motivo = (f"{nombre} {sc.idx} ya tiene {', '.join(hay)}" +
                  ("; la lupa no se mueve (su detalle está en esa foto)" if campo == "evidence_zoom" else ""))
        no = motivo if campo == "evidence_zoom" else mover(b, sc, lambda s2, b=b: libre_iv(s2, b))
        if no:
            fuera(campo, b, motivo if no == motivo else f"{motivo}; {no}")
            filas[-1]["texto"] = filas[-1]["texto"] or b.get("value_text")
            if campo == "archive_clippings":
                plan[campo] = [a for a in plan[campo] if a is not b]
            else:
                plan[campo] = None
        else:
            marca_bloque(b, campo)
    # 2. el reloj (F34 §A.3.1: el sello ya no lo frena; lo frenan la lupa y el agua de su beat)
    tk = plan.get("time_ticker")
    reloj: tuple[float, float] | None = None
    if tk:
        end = float(tk["start"]) + float(tk["duration"])
        bt = beat_en(float(tk["start"]))
        anim_beat = []
        if plan.get("evidence_zoom") and beat_en(float(plan["evidence_zoom"]["start"])) is bt:
            anim_beat.append("lupa")
        if plan.get("water_level") and beat_en(float(plan["water_level"]["start"])) is bt:   # F32 §B.7
            anim_beat.append("nivel de agua")

        def choca(st: float) -> list[str]:
            return [f"{'oración' if por_oracion else 'escena'} {s.idx}: {', '.join(ocupa[s.idx])}" for s in us
                    if s.start < end and s.end > st and ocupa.get(s.idx)]
        motivo = None
        if anim_beat:
            motivo = f"una animación por beat: el beat {bt['n'] if bt else '?'} ya tiene {', '.join(anim_beat)}"
        elif choca(float(tk["start"])):
            c0 = choca(float(tk["start"]))
            cambios = [float(c["t"]) for c in tk.get("changes") or []]
            nuevo = next((s.start for s in escenas_del_beat_desde(scene_at(us, float(tk["start"])), bt)
                          if not choca(s.start) and end - s.start >= TICKER_MIN
                          and not any(float(tk["start"]) < c <= s.start for c in cambios)), None)
            if nuevo is None:
                motivo = f"encima de otra cosa ({'; '.join(c0)}) y sin otra {'oración' if por_oracion else 'escena'} libre en su beat"
            else:
                filas.append({"bloque": "time_ticker", "regla": "zona", "accion": "movido",
                              "motivo": f"{float(tk['start']):.2f} → {nuevo:.2f} s ({'; '.join(c0)})"})
                tk["start"], tk["duration"] = round(nuevo, 3), round(end - nuevo, 3)
        if motivo:
            filas.append({"bloque": "time_ticker", "texto": f"{tk.get('day')} {tk.get('month')}", "t0": tk["start"],
                          "regla": "zona", "accion": "fuera", "motivo": motivo})
            plan["time_ticker"] = None
        else:
            reloj = (float(tk["start"]), float(tk["start"]) + float(tk["duration"]))
            for u in _cubre(us, reloj[0], reloj[1]):
                if por_oracion:
                    marca(u.idx, "reloj")
    # 3. las fichas
    fichas = [c for c in plan.get("callouts") or [] if c.get("ficha")]

    def libre_ficha(s2: Any, c: dict, a: float | None = None) -> bool:
        """La escena (u oración) s2 está libre para la ficha que arranca en `a` (por defecto, el inicio de s2)."""
        a = float(s2.start) if a is None else a
        if not por_oracion:
            return not ocupa.get(s2.idx) and not (reloj and s2.start < reloj[1] and s2.end > reloj[0])
        b = a + float(c.get("duration") or 0.0)
        return (not any(ocupa.get(x.idx) for x in _cubre(us, a, b))
                and not (reloj and a < reloj[1] and b > reloj[0]))
    for c in sorted(fichas, key=prio):
        sc = scene_at(us, float(c["start"]))
        if libre_ficha(sc, c, float(c["start"])):
            marca_bloque(c, "ficha")
            continue
        hay = sorted({q for x in (_cubre(us, float(c["start"]), float(c["start"]) + float(c.get("duration") or 0.0))
                                  if por_oracion else [sc]) for q in ocupa.get(x.idx) or []})
        hay += ["reloj"] if reloj and "reloj" not in hay and sc.start < reloj[1] and sc.end > reloj[0] else []
        motivo = f"{nombre} {sc.idx} ya tiene {', '.join(hay)}"
        no = mover(c, sc, lambda s2, c=c: libre_ficha(s2, c))
        if no:
            fuera("callouts", c, f"{motivo}; {no}")
            plan["callouts"] = [x for x in plan["callouts"] if x is not c]
        else:
            filas.append({"pool_id": c.get("pool_id"), "tipo": c.get("tipo_rotulista"), "texto": c["text"],
                          "regla": "zona", "accion": "movido", "motivo": f"{motivo} → {c['movido_escena']}"})
            marca_bloque(c, "ficha")
    plan["callouts"] = sorted(plan.get("callouts") or [], key=lambda c: c["start"])
    rot = plan.setdefault("rotulista", {})
    rot["escena"] = filas
    log.append(f"  rotulista escena: {[(f.get('pool_id') or f.get('bloque'), f['accion'], f['motivo']) for f in filas]}"
               f" · title card {gfx_rules.title_dur:.1f} s")
    return filas
