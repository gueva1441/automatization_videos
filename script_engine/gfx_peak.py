"""
gfx_peak.py — El pico del capítulo y sus bloques grandes (F3, pedido de Omar 2026-10-20). Determinista, sin LLM.

    pico          la frase con más palabras de peso 3 del léxico (desempate: peso total, después la primera). Ahí va
                  UN solo bloque grande y se saca todo lo que ARRANCA a ±PEAK_CLEAR_SEC del pico.
    water_level   nivel de agua: palabra del mood agua en la frase + cifra en metros/pies que la voz dice en esa
                  frase y que está LITERAL en un dato. Línea que sube hasta la altura de la cifra. Máx 1 por VIDEO.
    zoom latido   zoom de evidencia (caja por visión, cacheada) + latido en la 2.ª palabra de peso 3 fuera del pico.
    time_ticker   reloj de esquina "29 AGO · 23:40": fecha/hora LITERAL de un dato que la voz dice; avanza solo si
                  los datos traen dos horas; si no, la fecha quieta. Máx 1 por cap. Termina antes del pico.
    black_hold    corte a negro al final, después de la pregunta de cierre (lo arma gfx_layer.closing_question).

Bloques grandes posibles para el pico, en orden: nivel de agua → zoom de evidencia con latido → recorte → (cita: §D).
"""
from __future__ import annotations

import re
import unicodedata
from typing import Any, Callable

from gfx_config import gfx_rules

PEAK_CLEAR_SEC = 5.0
WATER_DUR = (2.5, 2.0)              # subida, hold
WATER_FULL_M = 7.6                  # 4.6 m ≈ 60 % de la pantalla
MESES = {"enero": "ENE", "febrero": "FEB", "marzo": "MAR", "abril": "ABR", "mayo": "MAY", "junio": "JUN", "julio": "JUL",
         "agosto": "AGO", "septiembre": "SEP", "setiembre": "SEP", "octubre": "OCT", "noviembre": "NOV", "diciembre": "DIC"}
_DATE_RE = re.compile(r"\b(\d{1,2}) de (" + "|".join(MESES) + r")(?: de (\d{4}))?", re.I)
_TIME_RE = re.compile(r"\b([01]?\d|2[0-3]):([0-5]\d)\b")
_UNIT_RE = r"(metros|metro|pies|pie|m)\b"


def _plain(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", str(s).lower()) if unicodedata.category(c) != "Mn")


def _clean(w: str) -> str:
    return re.sub(r"^[¿¡\"«(]+|[.,;:!?\"»)]+$", "", str(w)).lower()


def sentences(words: list[dict], time_offset: float = 0.0) -> list[dict[str, Any]]:
    """Frases de la narración con sus palabras (índices) y tiempos."""
    out, cur = [], []
    for i, w in enumerate(words):
        if not str(w.get("word", "")).strip():
            continue
        cur.append(i)
        if re.search(r"[.!?…]$", str(w["word"]).strip()):
            out.append(cur)
            cur = []
    if cur:
        out.append(cur)
    return [{"idx": s, "t0": float(words[s[0]]["start"]) + time_offset, "t1": float(words[s[-1]]["end"]) + time_offset,
             "text": " ".join(str(words[i]["word"]).strip() for i in s)} for s in out]


def lexicon_hits(words: list[dict], moods: dict[str, dict], idxs: list[int] | None = None) -> list[dict[str, Any]]:
    hits = []
    for i in (idxs if idxs is not None else range(len(words))):
        k = _clean(words[i].get("word", ""))
        for cat, m in moods.items():
            if k in (m.get("triggers") or {}):
                hits.append({"i": i, "word": k, "category": cat, "weight": int(m["triggers"][k])})
                break
    return hits


def find_peak(words: list[dict], moods: dict[str, dict], time_offset: float = 0.0) -> dict[str, Any] | None:
    """La frase con más palabras de peso 3 (desempate: peso total, después la primera). None si no hay peso 3."""
    best, key = None, None
    for s in sentences(words, time_offset):
        hits = lexicon_hits(words, moods, s["idx"])
        n3 = sum(h["weight"] == 3 for h in hits)
        if not n3:
            continue
        k = (n3, sum(h["weight"] for h in hits))
        if key is None or k > key:
            h3 = next(h for h in hits if h["weight"] == 3)
            best, key = {**s, "hits": hits, "i": h3["i"], "word": h3["word"], "category": h3["category"],
                         "t": round(float(words[h3["i"]]["start"]) + time_offset, 3)}, k
    return best


WATER_PEAK_TOL = 0.1                 # F4b: una frase con cifra de agua a ≤ 0.1 de la máxima intensidad gana el pico


def peak_from_intensity(words: list[dict], moods: dict[str, dict], res: dict[str, Any],
                        time_offset: float = 0.0, si: int | None = None) -> dict[str, Any] | None:
    """F4b §1: pico GARANTIZADO = frase de mayor intensidad (empate: más cargas de peso 3). La palabra del pico es la
    de más peso del léxico del cap en esa frase; si no hay, la carga de esa frase; si tampoco, la palabra más larga."""
    from script_engine.gfx_intensity import peak_sentence
    sents = sentences(words, time_offset)
    if not sents or not res or len(res.get("intensidad") or []) != len(sents):
        return None
    si = peak_sentence(res) if si is None else si
    s = sents[si]
    hits = lexicon_hits(words, moods, s["idx"])
    if hits:
        h = max(hits, key=lambda x: (x["weight"], -x["i"]))
        i, word, cat = h["i"], h["word"], h["category"]
    else:
        cg = sorted((c for c in res["cargas"] if c["sentence_idx"] == si), key=lambda c: -c["peso"])
        i = next((j for c in cg for j in s["idx"] if _clean(words[j]["word"]) == c["word"]), None)
        if i is None:
            i = max(s["idx"], key=lambda j: len(_clean(words[j]["word"])))
        word, cat = _clean(words[i]["word"]), (cg[0]["categoria"] if cg else None)
    return {**s, "hits": hits, "i": i, "word": word, "category": cat, "sentence_idx": si,
            "intensity": res["intensidad"][si], "t": round(float(words[i]["start"]) + time_offset, 3)}


def _to_m(value: float, unit: str) -> float:
    return value * 0.3048 if unit.startswith("pie") else value


def water_level(peak: dict[str, Any], ctx: dict[str, Any], words: list[dict]) -> dict[str, Any] | None:
    """Nivel de agua en el pico: mood agua + cifra (m o pies) dicha en la frase y LITERAL en un dato elegible."""
    if not peak or not any(h["category"] == "agua" for h in peak["hits"]):
        return None
    said = [_clean(words[i]["word"]) for i in peak["idx"]]
    eligible = ctx.get("eligible") or {}
    for fi, fact in enumerate(ctx.get("facts") or []):
        if eligible and fi not in eligible:
            continue
        for m in re.finditer(r"(\d+(?:[.,]\d+)?)\s*" + _UNIT_RE, fact):
            num, unit = m.group(1), m.group(2)
            if num in said or num.replace(",", ".") in said:
                meters = _to_m(float(num.replace(",", ".")), unit)
                water_word = next(h for h in peak["hits"] if h["category"] == "agua")
                return {"value_text": num, "unit": unit, "meters": round(meters, 2),
                        "height": round(min(0.85, max(0.15, meters / WATER_FULL_M)), 3),
                        "start": round(float(words[water_word["i"]]["start"]), 3), "duration": sum(WATER_DUR),
                        "rise": WATER_DUR[0], "fact_idx": fi, "word": water_word["word"]}
    return None


def zoom_latido(peak: dict[str, Any] | None, words: list[dict], moods: dict[str, dict], scenes: list[Any],
                box_for: Callable[[int, str], list[float] | None], time_offset: float = 0.0,
                zoom_dur: float = 2.85, only_i: int | None = None) -> dict[str, Any] | None:
    """Zoom de evidencia (al FINAL de la escena, como siempre) + latido en una palabra de peso 3 fuera del pico,
    si visión ya dio una caja para esa escena."""
    lo, hi = ((peak["t"] - PEAK_CLEAR_SEC, peak["t"] + PEAK_CLEAR_SEC) if peak else (-1.0, -1.0))
    for h in sorted(lexicon_hits(words, moods), key=lambda x: (-x["weight"], x["i"])):
        t = float(words[h["i"]]["start"]) + time_offset
        if only_i is not None:
            if h["i"] != only_i:
                continue
        elif h["weight"] < 3 or lo <= t <= hi:
            continue
        sc = next((s for s in scenes if s.start <= t < s.end), None)
        if sc is None or sc.end - sc.start < zoom_dur + 0.2:
            continue
        box = box_for(sc.idx, h["word"])
        if not box:
            continue
        start = round(sc.end - zoom_dur, 3)
        return {"scene_idx": sc.idx, "box": box, "start": start, "anchor": h["word"],
                "latido": True, "latido_t": round(max(start + 0.7, min(t, sc.end - 0.6)), 3), "word": h["word"]}
    return None


def time_ticker(ctx: dict[str, Any], words: list[dict], clip_dur: float, peak: dict[str, Any] | None,
                time_offset: float = 0.0) -> dict[str, Any] | None:
    """Reloj de esquina con la fecha (y hora) LITERAL de un dato que la voz dice. None si no hay fecha dicha."""
    narr = _plain(" ".join(str(w.get("word", "")) for w in words))
    for fi, fact in enumerate(ctx.get("facts") or []):
        m = _DATE_RE.search(fact)
        if not m:
            continue
        day, month, year = m.group(1), m.group(2).lower(), m.group(3)
        if not re.search(rf"\b{day} de {_plain(month)}\b", narr):
            continue
        # palabra donde la voz dice el día de esa fecha
        wi = next((i for i in range(len(words) - 2) if _clean(words[i]["word"]) == day and
                   _plain(_clean(words[i + 2]["word"])) == _plain(month)), None)
        if wi is None:
            continue
        times = [(int(h), int(mi)) for h, mi in _TIME_RE.findall(" ".join(ctx.get("facts") or []))]
        if len(times) < gfx_rules.ticker_min_times:           # F4: sin horas verificadas el reloj no sale
            return None
        start = float(words[wi]["start"]) + time_offset
        end = clip_dur if not peak or peak["t"] < start else max(start + 2.0, peak["t"] - PEAK_CLEAR_SEC)
        tail = f"{times[0][0]:02d}:{times[0][1]:02d}" if times else (year or "")
        return {"day": day, "month": MESES[month], "tail": tail, "times": [f"{h:02d}:{mi:02d}" for h, mi in times[:2]],
                "advance": len(times) >= 2, "source_text": m.group(0), "fact_idx": fi,
                "start": round(start, 3), "duration": round(min(end, clip_dur) - start, 3)}
    return None


def ticker_corner(tk: dict[str, Any], plan: dict[str, Any]) -> dict[str, Any]:
    """El reloj va en la esquina superior que esté LIBRE mientras se ve (los datos, recortes y el contador también van
    arriba). Si las dos están ocupadas en algún momento, el reloj arranca cuando se libera una."""
    a0, a1 = tk["start"], tk["start"] + tk["duration"]
    top = [(x["start"], x["start"] + float(x.get("duration", 2.5)), x.get("side", "left")) for x in
           (plan.get("callouts") or []) + (plan.get("archive_clippings") or [])]
    if plan.get("count_up"):
        cu = plan["count_up"]
        top.append((cu["start"], cu["start"] + float(cu.get("duration", 3.7)), "left"))
    hits = [(s, e, side) for s, e, side in top if s < a1 and e > a0]
    sides = {side for _, _, side in hits}
    tk["side"] = "right" if "left" in sides and "right" not in sides else "left"
    if {"left", "right"} <= sides:                                  # las dos ocupadas → arranca después
        new0 = max(e for _, e, _ in hits) + 0.3
        tk["duration"] = round(a1 - new0, 3)
        tk["start"] = round(new0, 3)
    return tk


def _starts_near(t: float, x: dict | float | None) -> bool:
    s = x if isinstance(x, (int, float)) else (x or {}).get("start")
    return s is not None and abs(float(s) - t) <= PEAK_CLEAR_SEC


def clear_around(plan: dict[str, Any], t: float, keep: str) -> list[str]:
    """Saca todo lo que arranca a ±PEAK_CLEAR_SEC del pico (menos el bloque del pico, el título y la pregunta)."""
    gone: list[str] = []
    for key in ("callouts", "archive_clippings", "emphasis"):
        kept = []
        for x in plan.get(key) or []:
            if keep == key and x.get("peak"):
                kept.append(x)
            elif _starts_near(t, x):
                gone.append(f"{key}:{x.get('text') or x.get('headline') or x.get('word')}")
            else:
                kept.append(x)
        plan[key] = kept
    kept_p = []
    for p in plan.get("punch_in") or []:
        if _starts_near(t, p):
            gone.append(f"punch_in:{p}")
        else:
            kept_p.append(p)
    plan["punch_in"] = kept_p
    for key in ("count_up", "icon_array", "evidence_zoom", "water_level"):
        x = plan.get(key)
        if x and key != keep and _starts_near(t, x):
            gone.append(key)
            plan[key] = None
    return gone


def water_used_before(work_dir: Any, chapter_number: int) -> bool:
    """Máx 1 nivel de agua por VIDEO: ¿algún cap anterior ya lo usó? (planes resueltos en work_dir)."""
    import json
    from pathlib import Path
    for f in sorted(Path(work_dir).glob("gfx_plan_ch*.resolved.json")):
        m = re.search(r"ch(\d+)", f.name)
        if not m or int(m.group(1)) >= chapter_number:
            continue
        try:
            if (json.loads(f.read_text(encoding="utf-8")).get("plan") or {}).get("water_level"):
                return True
        except (OSError, ValueError):
            continue
    return False


def box_from_cache(cache: Any) -> Callable[[int, str], list[float] | None]:
    """Caja de zoom ya juzgada por visión para una escena (cache gfx_zoom_box_<cap>.json, claves 'idx' o 'idx|ancla')."""
    import json
    from pathlib import Path
    try:
        data = json.loads(Path(cache).read_text(encoding="utf-8")) if Path(cache).exists() else {}
    except (OSError, ValueError):
        data = {}

    def box_for(si: int, word: str) -> list[float] | None:
        for k, v in data.items():
            if k.split("|")[0] == str(si) and v.get("box") and float(v.get("confianza", 1.0) or 0) >= 0.7:
                return v["box"]
        return None
    return box_for


def plan_peak(plan: dict[str, Any], *, ctx: dict[str, Any], words: list[dict], scenes: list[Any], moods: dict[str, dict],
              clip_dur: float, box_for: Callable[[int, str], list[float] | None], water_used: bool = False,
              time_offset: float = 0.0, log: list[str] | None = None,
              intensity: dict[str, Any] | None = None) -> dict[str, Any]:
    """Plan resuelto → + pico (con UN bloque grande y ±5 s libres) + zoom con latido + reloj. Idempotente."""
    log = log if log is not None else []
    if plan.get("pico") is not None:
        return plan
    peak = (peak_from_intensity(words, moods, intensity, time_offset) if intensity else None) \
        or find_peak(words, moods, time_offset)
    if intensity and peak and not water_used and not water_level(peak, ctx, words):
        top = max(intensity["intensidad"])
        for si in sorted(range(len(intensity["intensidad"])), key=lambda i: -intensity["intensidad"][i]):
            if intensity["intensidad"][si] < top - WATER_PEAK_TOL:
                break
            alt = peak_from_intensity(words, moods, intensity, time_offset, si=si)
            if alt and water_level(alt, ctx, words):
                log.append(f"pico: frase {si} (intensidad {intensity['intensidad'][si]:.2f}, máx {top:.2f}) por la cifra de agua")
                peak = alt
                break
    plan["pico"] = None
    if peak:
        wl = None if water_used else water_level(peak, ctx, words)
        if wl:
            plan["water_level"] = wl
            block = "water_level"
        else:
            zl = zoom_latido(None, words, moods, scenes, box_for, time_offset, only_i=peak["i"])
            ok_zoom = bool(zl)
            block = "evidence_zoom" if ok_zoom else ("archive_clippings" if any(
                _starts_near(peak["t"], a) for a in plan.get("archive_clippings") or []) else None)
            if ok_zoom:
                plan["evidence_zoom"] = zl
            elif block == "archive_clippings":
                for a in plan["archive_clippings"]:
                    if _starts_near(peak["t"], a):
                        a["peak"] = True
                        break
            elif intensity:                           # F4b: pico garantizado → el mood + sello de la frase pico
                em = next((e for e in plan.get("emphasis") or [] if _starts_near(peak["t"], e)), None)
                if em:
                    em["peak"] = True
                    block = "emphasis"
        if block:
            gone = clear_around(plan, peak["t"], block)
            plan["pico"] = {"t": peak["t"], "block": block, "word": peak["word"], "sentence": peak["text"],
                            **({"intensity": peak["intensity"], "sentence_idx": peak["sentence_idx"]} if "intensity" in peak else {})}
            log.append(f"pico: «{peak['word']}» @ {peak['t']:.1f}s → {block}; fuera (±{PEAK_CLEAR_SEC:.0f} s): {gone or 'nada'}")
        else:
            plan["pico"] = {"t": peak["t"], "block": None, "word": peak["word"], "sentence": peak["text"]}
            log.append(f"pico: «{peak['word']}» @ {peak['t']:.1f}s sin bloque grande posible (sin cifra de agua, zoom ni recorte)")
    # zoom de evidencia con latido fuera del pico (si el plan no tiene ya un zoom)
    if not plan.get("evidence_zoom"):
        zl = zoom_latido(peak, words, moods, scenes, box_for, time_offset)
        if zl:
            plan["evidence_zoom"] = zl
            log.append(f"zoom + latido: «{zl['word']}» escena {zl['scene_idx']} @ {zl['start']:.1f}s (latido {zl['latido_t']:.1f}s)")
    tk = time_ticker(ctx, words, clip_dur, peak, time_offset)
    if tk:
        ticker_corner(tk, plan)
    if tk and tk["duration"] >= 2.0:
        plan["time_ticker"] = tk
        log.append(f"reloj: {tk['day']} {tk['month']} · {tk['tail']} @ {tk['start']:.1f}–{tk['start'] + tk['duration']:.1f}s")
    return plan
