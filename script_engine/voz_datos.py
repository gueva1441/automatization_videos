"""
script_engine/voz_datos.py — F36 §A: lo que sale de la voz y de la escaleta sin pasar por el modelo (movido de
gfx_rotulista sin cambios): el pico del cap (`pico_cap`, `pico_plan`), las fechas completas que dice la voz y su reloj
(`fechas_completas`, `reloj_de_voz`), el nivel de agua desde la voz (`agua_de_voz`) y la tarjeta fecha-hora del inicio
(`tarjeta_inicial`).
"""
from __future__ import annotations

import re
from typing import Any

from script_engine import evidence as ev
from script_engine.voz_utils import _DIG, _analiza, _fmt, _num_en, _toks, _w2n


# ═══════════════════════ pico del cap ═══════════════════════

def _raices(t: str) -> set[str]:
    from script_engine.gfx_realizador import _raices as r
    return r(t)


def pico_cap(cap: int, escaleta: dict, beats: list[dict], sents: list[dict], pool: dict | None) -> dict[str, Any] | None:
    """El pico ÚNICO del cap (lo leen el rotulista, el realizador y music_intensity): el beat de `escaleta.pico` si cae
    en este cap; si no, el beat más intenso del cap (empate: el primero, como music_intensity). La frase = la oración
    del beat con más raíces en común con su dato (el de `escaleta.pico` o el `dato_central`); empate: la primera."""
    from script_engine.music_intensity import beat_pico_de_cap
    if not beats or not sents:
        return None
    pk = escaleta.get("pico") or {}
    n = beat_pico_de_cap(beats, pk.get("beat"))
    b = next(x for x in beats if x["n"] == n)
    en_beat = [s for s in sents if b["t0"] - 0.3 <= s["t0"] <= b["t1"]] or sents[:1]
    its = ev.items(pool) if pool else {}
    dato = str(pk.get("id")) if pk.get("beat") == n and pk.get("id") else b["dato_central"]
    ref = _raices(ev.text_of(its[dato])) if dato in its else set()
    s = max(en_beat, key=lambda x: (len(ref & _raices(x["texto"])), -x["idx"]))
    return {"beat": n, "funcion": b["funcion"], "sentence_idx": s["idx"], "frase": s["texto"], "t": s["t0"],
            "dato": dato, "fuente": "escaleta.pico" if pk.get("beat") == n else "escaleta (beat más intenso del cap)"}


# ═══════════════════════ reloj y agua desde la voz, tarjeta fecha-hora (F34 §A.3.3, §A.5, §A.6) ═══════════════════════

_MES_RE = r"(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|setiembre|octubre|noviembre|diciembre)"


def _entero(toks: list[str]) -> int | None:
    """El entero que dicen esos tokens (dígitos o letras, «mil novecientos sesenta y tres»)."""
    from script_engine.num_es import parse_int
    s = " ".join(toks)
    if len(toks) == 1 and _DIG.fullmatch(toks[0]):
        return parse_int(toks[0])
    return _w2n().get(s)


def fechas_completas(texto: str) -> list[tuple[int, str, int]]:
    """F34 §A.3.3: las fechas con día, mes y año que dice un texto, en letras o dígitos: [(día, mes, año)]. El día es
    el tramo numérico más largo antes de «de <mes>» (1–31, calendario); el año, el más largo después de «de»."""
    toks = re.findall(r"\d+|[^\W\d_]+", ev.norm(texto or ""))
    out = []
    for i, t in enumerate(toks):
        if not re.fullmatch(_MES_RE, t) or i < 2 or toks[i - 1] != "de" or i + 2 >= len(toks) or toks[i + 1] != "de":
            continue
        dia = None
        for a in range(max(0, i - 4), i - 1):           # derivado: «treinta y uno» = 3 tokens + «de»
            n = _entero(toks[a:i - 1])
            if n is not None and 1 <= n <= 31:          # estándar: días del calendario
                dia = n
                break
        anio = None
        for e in range(min(len(toks), i + 8), i + 2, -1):   # derivado: «mil novecientos sesenta y tres» + margen
            n = _entero(toks[i + 2:e])
            if n is not None and n >= 100:              # derivado: un año con siglo (no «de dos» ni el día)
                anio = n
                break
        if dia is not None and anio is not None:
            out.append((dia, "setiembre" if t == "setiembre" else t, anio))
    return out


def reloj_de_voz(ent: dict[str, Any], clip_dur: float) -> dict[str, Any] | None:
    """F34 §A.3.3: el reloj de la primera oración del cap que dice una fecha completa (aunque el director no lo pida),
    en el formato del reloj de la cronología (gfx_pool.pool_ticker): desde el inicio de esa oración hasta TICKER_HOLD
    después de su fin (derivado: lo que el reloj sostiene una fecha nueva); no sale si queda < TICKER_MIN."""
    from script_engine.gfx_peak import MESES
    from script_engine.gfx_pool import TICKER_HOLD, TICKER_MIN
    for s in ent.get("oraciones") or []:
        fs = fechas_completas(s["texto"])
        if not fs:
            continue
        d, mes, y = fs[0]
        start = float(s["t0"])
        end = min(float(clip_dur), float(s["t1"]) + TICKER_HOLD)
        if end - start < TICKER_MIN:
            return None
        return {"day": str(d), "month": MESES["septiembre" if mes == "setiembre" else mes], "tail": str(y),
                "times": [], "advance": False, "source_text": s["texto"], "pool_id": None, "start": round(start, 3),
                "duration": round(end - start, 3), "changes": [], "de_voz": True, "sentence_idx": s["idx"]}
    return None


AGUA_ETIQUETAS = ("COTA AUTORIZADA", "COTA", "OLA", "NIVEL DEL EMBALSE", "NIVEL")   # §A.5: las de la oración


def _agua_de(texto: str, previa: str) -> tuple[str, float, str] | None:
    """(etiqueta, metros, cifra tal cual) si la oración dice una altura o nivel de agua con número (lectura declarada de
    §A.5): «ola de <n> metros» → OLA; «cota» con número en la oración (o la anterior) → COTA (AUTORIZADA si lo dice);
    «<n> metros sobre el nivel» o «nivel … <n> metros» → NIVEL (DEL EMBALSE si la oración nombra el embalse). El
    número: con unidad metros, o sin unidad al final de la oración («la cota autorizada fue de setecientos quince»);
    nunca metros cúbicos ni una diferencia."""
    toks = _toks(texto)
    nums, _ = _analiza(texto)
    tn = ev.norm(texto)

    def num_m(nn: list, desde: int = 0) -> tuple[float, int] | None:
        for v, u, p in nn:
            if p >= desde and u == "m":
                return v, p
        return None

    def num_fin(nn: list, tt: list[str], desde: int) -> tuple[float, int] | None:
        for v, u, p in nn:
            if p >= desde and u is None:
                _, j = _num_en(tt, p)
                if j >= len(tt):
                    return v, p
        return None
    if "cota" in toks:
        i = toks.index("cota")
        got = num_m(nums, i) or num_fin(nums, toks, i)
        if got is None and previa:
            pn, _ = _analiza(previa)
            got = num_m(pn) or num_fin(pn, _toks(previa), 0)
        if got:
            return ("COTA AUTORIZADA" if "autoriz" in tn else "COTA"), got[0], _fmt(got[0])
    for k, t in enumerate(toks):
        if t in ("ola", "olas") and k + 1 < len(toks) and toks[k + 1] == "de":
            got = num_m(nums, k + 2)
            if got and got[1] == k + 2:
                return "OLA", got[0], _fmt(got[0])
    if "nivel" in toks:
        i = toks.index("nivel")
        got = num_m(nums, i)
        if got is None and toks[max(0, i - 2):i] == ["sobre", "el"]:          # «<n> metros sobre el nivel»
            prev = [(v, p) for v, u, p in nums if u == "m" and p < i]
            got = prev[-1] if prev else None
        if got:
            return ("NIVEL DEL EMBALSE" if "embalse" in tn else "NIVEL"), got[0], _fmt(got[0])
    return None


def agua_de_voz(plan: dict[str, Any], ent: dict[str, Any], log: list[str]) -> dict[str, Any] | None:
    """F34 §A.5: un `water_level` desde la voz cuando una oración dice una altura o nivel con número (la única animación
    que puede repetir la cifra de la voz: es la imagen de esa frase). Uno por cap (el plan tiene un solo nivel de agua):
    el de la etiqueta más específica (AGUA_ETIQUETAS en orden), y entre iguales el primero. No pisa el del rotulista.
    Arranca con la oración y dura lo que ella (al menos la subida + el hold de la plantilla, WATER_DUR)."""
    from script_engine.gfx_peak import WATER_DUR, WATER_FULL_M
    if plan.get("water_level"):
        return None
    sents = ent.get("oraciones") or []
    hall = []
    for k, s in enumerate(sents):
        got = _agua_de(s["texto"], sents[k - 1]["texto"] if k else "")
        if got:
            hall.append((AGUA_ETIQUETAS.index(got[0]), k, got))
    if not hall:
        return None
    _, k, (etq, meters, txt) = min(hall)
    s = sents[k]
    dur = max(float(s["t1"]) - float(s["t0"]), sum(WATER_DUR))
    wl = {"start": round(float(s["t0"]), 3), "duration": round(dur, 3), "value_text": txt, "unit": "m",
          "meters": round(meters, 2), "height": round(min(0.85, max(0.15, meters / WATER_FULL_M)), 3),
          "rise": WATER_DUR[0], "etiqueta": etq, "word": None, "sentence_idx": s["idx"], "de_voz": True,
          "aporta": f"la imagen de «{s['texto'][:80]}»"}
    plan["water_level"] = wl
    log.append(f"  agua desde la voz: {etq} · {txt} m @ {wl['start']:.1f}s (oración [{s['idx']}]); candidatas "
               f"{[(sents[kk]['idx'], g[0], g[2]) for _, kk, g in hall]}")
    return wl


def tarjeta_inicial(escaleta: dict, pool: dict | None) -> dict[str, Any]:
    """F34 §A.6: la tarjeta fecha-hora del suceso central (antes de la primera imagen, sobre negro, title_dur). Fecha =
    la del ítem del pico de la escaleta (`escaleta.pico.id`); hora = la del propio ítem o, si no la trae, la de un ítem
    de la cronología de esa misma fecha cuya hora dice literalmente el `por_que` del pico (para Vajont: T57 + «22:39»
    de T66). Si no se puede derivar con certeza: `falta` (el guion lo marca y se agrega con --plan-edit)."""
    from script_engine.gfx_peak import MESES
    its = ev.items(pool) if pool else {}
    pk = escaleta.get("pico") or {}
    it = its.get(str(pk.get("id") or ""))
    fecha = str((it or {}).get("fecha") or "")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", fecha):
        return {"falta": True, "motivo": f"el ítem del pico ({pk.get('id')}) no trae fecha con día"}
    hora, de = (it.get("hora"), it["id"]) if it.get("hora") else (None, None)
    if hora is None:
        pq = str(pk.get("por_que") or "")
        for x in its.values():
            h = str(x.get("hora") or "")
            if x["_kind"] == "cronologia" and x.get("fecha") == fecha and h and re.search(rf"(?<!\d){re.escape(h)}(?!\d)", pq):
                hora, de = h, x["id"]
                break
    if hora is None:
        return {"falta": True, "motivo": f"la hora del pico ({pk.get('id')}, {fecha}) no se deriva con certeza"}
    y, m, d = fecha.split("-")
    texto = f"{int(d)} {MESES[ev.MESES[int(m) - 1]]} {y} · {hora}"
    return {"texto": texto, "fecha": fecha, "hora": hora, "pool_id": it["id"], "hora_de": de,
            "fuente": f"escaleta.pico {it['id']} (fecha) + {de} (hora)"}


# ═══════════════════════ pico (sello) ═══════════════════════

def pico_plan(plan: dict[str, Any], ent: dict[str, Any], *, words: list[dict], scenes: list[Any], moods: dict,
              intensity: dict | None, time_offset: float, freq: dict | None, log: list[str]) -> dict[str, Any] | None:
    """El pico del plan = el de la escaleta (pico_cap), sin privilegio de bloque: solo la palabra del pico (el sello de
    siempre, ≤ 1). gfx_peak no decide el pico cuando hay escaleta."""
    from script_engine.gfx_peak import add_peak_word, sentences
    pk = ent.get("pico")
    if not pk:
        return None
    s = sentences(words, time_offset)[pk["sentence_idx"]]
    peak = {**s, "t": pk["t"]}
    plan["pico"] = {"t": pk["t"], "block": None, "word": None, "sentence": pk["frase"], "sentence_idx": pk["sentence_idx"],
                    "beat": pk["beat"], "fuente": pk["fuente"]}
    from gfx_config import gfx_rules
    if gfx_rules.peak_word:
        em = add_peak_word(plan, peak, words=words, scenes=scenes, moods=moods, block=None, time_offset=time_offset,
                           freq=freq, log=log)
        if em is not None:
            plan["pico"]["word"] = plan["pico"]["palabra"] = em["word"]
    log.append(f"  pico (escaleta, beat {pk['beat']}): oración [{pk['sentence_idx']}] @ {pk['t']:.1f}s «{pk['frase'][:70]}»"
               f" · palabra {plan['pico'].get('word')!r}")
    return plan["pico"]
