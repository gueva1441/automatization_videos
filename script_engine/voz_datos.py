"""
script_engine/voz_datos.py — F36 §A: lo que sale de la voz y de la escaleta sin pasar por el modelo (movido de
gfx_rotulista sin cambios): el pico del cap (`pico_cap`, `pico_plan`), las fechas completas que dice la voz y su reloj
(`fechas_completas`, `reloj_de_voz`) y la tarjeta fecha-hora derivada de la escaleta (`tarjeta_inicial`; desde F36 C
solo para comparar con la del guion en papel). F36 §D: se borró el nivel de agua desde la voz.
"""
from __future__ import annotations

import re
from typing import Any

from script_engine import evidence as ev
from script_engine.voz_utils import _DIG, _w2n


MESES = {"enero": "ENE", "febrero": "FEB", "marzo": "MAR", "abril": "ABR", "mayo": "MAY", "junio": "JUN", "julio": "JUL",
         "agosto": "AGO", "septiembre": "SEP", "setiembre": "SEP", "octubre": "OCT", "noviembre": "NOV", "diciembre": "DIC"}


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


def tarjeta_inicial(escaleta: dict, pool: dict | None) -> dict[str, Any]:
    """F34 §A.6: la tarjeta fecha-hora del suceso central (antes de la primera imagen, sobre negro, title_dur). Fecha =
    la del ítem del pico de la escaleta (`escaleta.pico.id`); hora = la del propio ítem o, si no la trae, la de un ítem
    de la cronología de esa misma fecha cuya hora dice literalmente el `por_que` del pico (para Vajont: T57 + «22:39»
    de T66). Si no se puede derivar con certeza: `falta` (el guion lo marca y se agrega con --plan-edit)."""
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
    """El pico del plan = el de la escaleta (pico_cap), sin privilegio de bloque. F36 §D: sin sello propio de la palabra
    del pico (los sellos vienen del guion en papel); el pico marca dónde va el zoom_punch."""
    pk = ent.get("pico")
    if not pk:
        return None
    plan["pico"] = {"t": pk["t"], "block": None, "word": None, "sentence": pk["frase"], "sentence_idx": pk["sentence_idx"],
                    "beat": pk["beat"], "fuente": pk["fuente"]}
    log.append(f"  pico (escaleta, beat {pk['beat']}): oración [{pk['sentence_idx']}] @ {pk['t']:.1f}s «{pk['frase'][:70]}»")
    return plan["pico"]


# ═══════════════════════ reloj en la esquina y palabra del pico (de gfx_peak, F36 §D) ═══════════════════════

def ticker_corner(tk: dict[str, Any], plan: dict[str, Any]) -> dict[str, Any]:
    """El reloj va en la esquina superior que esté LIBRE mientras se ve (los datos, recortes y el contador también van
    arriba). Si las dos están ocupadas en algún momento, el reloj arranca cuando se libera una."""
    a0, a1 = tk["start"], tk["start"] + tk["duration"]
    top = [(x["start"], x["start"] + float(x.get("duration", 2.5)), x.get("side", "left")) for x in
           (plan.get("callouts") or []) + (plan.get("archive_clippings") or [])]
    hits = [(s, e, side) for s, e, side in top if s < a1 and e > a0]
    sides = {side for _, _, side in hits}
    tk["side"] = "right" if "left" in sides and "right" not in sides else "left"
    if {"left", "right"} <= sides:                                  # las dos ocupadas → arranca después
        new0 = max(e for _, e, _ in hits) + 0.3
        tk["duration"] = round(a1 - new0, 3)
        tk["start"] = round(new0, 3)
    return tk


