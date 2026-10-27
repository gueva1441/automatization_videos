"""
script_engine/gfx_guion.py — F32 §A: el guion de pantalla. Todo lo que se va a ver, en texto, antes de renderizar.

`fase2b --plan-only` corre director, rotulista, reglas y crítico (sin navegador ni render) y este módulo lee lo que
quedó en `_fase2b_work/` (plan resuelto, escenas, beats, crudas del rotulista) y escribe `output/<topic>/GUION_PANTALLA.md`
y `GUION_PANTALLA.json` (la misma información; el json es lo que leen después la hoja de cuadros y los chequeos):
    eventos    (§A.1) una línea por evento en el orden del mp4 final (intro y pre-roll ya sumados): title card, ficha,
               recorte, cita, persona, lupa, sello, reloj, nivel de agua, contador, punch, pregunta de cierre,
               transición, costura y silencio de voz; también lo que cada filtro cortó, con quién y por qué (✂).
    beats      (§A.2) por beat: función, ventana, escenas, propuestos (director / rotulista), cortados por regla,
               quedan; `⚠ BEAT VACÍO` y `⚠ CAP SIN TEXTO`.
    chequeos   (§A.3) cada uno ✓/✗ con el dato: dos bloques en una escena, bloque que cruza un corte, texto o pregunta
               sin lectura, cifra que contradice la voz, `a_pantalla` faltantes, costuras, inicio de voz por cap (sobre
               la mezcla de audio de previsualización, §A.4).
Lecturas declaradas (F32_REPORT): «silencio de voz» = hueco entre palabras mayor que la pausa más larga que el propio
guion marca en ese cap (las `[… pause]` del texto de la voz; sin marcas, la pausa más larga entre oraciones); «voz
presente» = el umbral del sidechain de la mezcla (`duck_threshold` del sync map); el inicio de voz medido es el corrimiento
de la voz dentro de la mezcla (correlación con su mp3) y la rampa mira los 100 ms antes de que la mezcla llegue a −18 dB.
"""
from __future__ import annotations

import json
import math
import re
import subprocess
import time
from pathlib import Path
from typing import Any

VERSION = "f36-c"
LECTURA_CPS = 15.0              # §0 (ya en F29c): caracteres ÷ 15 cps
PICO_DB = -18.0                 # §A.3: el ataque de la voz no salta de silencio a −18 dB …
RAMPA_S = 0.10                  # … en los 100 ms previos
VENTANA_S = 0.01                # ventana de nivel (10 ms)

TIPO_ROT = {"cifra": "ficha", "hecho": "ficha", "persona": "persona", "documento": "recorte", "cita": "cita",
            "lupa": "lupa"}
TEXTOS = ("ficha", "persona", "recorte", "cita", "contador")             # lo que se lee (lectura a 15 cps)
ANIMACIONES = ("sello", "reloj", "nivel de agua", "lupa")
REGLA_NOMBRE = {"no_dicho": "no dicho", "ya_mostrado": "ya mostrado", "lectura": "lectura", "cantidad": "cantidad",
                "spoiler": "spoiler", "coherencia": "coherencia", "zona": "zona", "candado": "candado",
                "anclaje": "anclaje", "forma": "forma"}


# ═══════════════════════ utilidades ═══════════════════════

def mmss(t: float) -> str:
    t = max(0.0, float(t))
    return f"{int(t // 60):02d}:{t % 60:04.1f}"


def _scene_at(escenas: list[dict], t: float) -> dict | None:
    for s in escenas:
        if s["start"] <= t < s["end"]:
            return s
    return escenas[-1] if escenas else None


def _beat_at(beats: list[dict], t: float) -> dict | None:
    for b in beats:
        if b["t0"] - 0.3 <= t <= b["t1"]:
            return b
    prev = [b for b in beats if b["t0"] <= t]
    return prev[-1] if prev else (beats[0] if beats else None)


def _oracion_en(sents: list[dict], t: float) -> int | None:
    k = next((i for i, s in enumerate(sents) if s["t0"] - 0.3 <= t <= s["t1"] + 0.3), None)
    if k is None:
        k = next((i for i, s in enumerate(sents) if s["t0"] >= t), None)
    return k


def _voz(sents: list[dict], k: int | None) -> tuple[str, str, str]:
    if k is None or not sents:
        return "—", "—", "—"
    k = max(0, min(int(k), len(sents) - 1))
    return ((sents[k - 1]["text"] if k > 0 else "—"), sents[k]["text"],
            (sents[k + 1]["text"] if k + 1 < len(sents) else "—"))


def _pcm(path: Path, t0: float, dur: float, sr: int) -> Any:
    """Muestras mono float32 de un tramo de audio (ffmpeg: wav o mp3)."""
    import numpy as np
    r = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{max(0.0, t0):.4f}", "-t", f"{dur:.4f}", "-i", str(path),
                        "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"], capture_output=True, timeout=120)
    return np.frombuffer(r.stdout, dtype=np.float32)


def niveles_db(path: Path, t0: float, dur: float, sr: int = 48000) -> list[float]:
    """RMS en dBFS por ventana de 10 ms de [t0, t0 + dur)."""
    import numpy as np
    a = _pcm(path, t0, dur, sr)
    w = int(round(sr * VENTANA_S))
    out = []
    for i in range(0, len(a) - w + 1, w):
        r = float(np.sqrt(np.mean(a[i:i + w].astype(np.float64) ** 2)))
        out.append(20 * math.log10(r) if r > 1e-9 else -120.0)
    return out


def db_de(amplitud: float) -> float:
    return 20 * math.log10(amplitud) if amplitud > 0 else -120.0


# ═══════════════════════ §A.3 inicio de voz ═══════════════════════

def _cruce_db(a: Any, sr: int, umbral: float) -> int | None:
    """Primera muestra donde el RMS de 10 ms (ventana deslizante, paso de 1 ms) llega a `umbral` dBFS."""
    import numpy as np
    w, h = int(round(sr * VENTANA_S)), max(1, sr // 1000)
    if len(a) < w:
        return None
    c = np.concatenate([[0.0], np.cumsum(a.astype(np.float64) ** 2)])
    pos = np.arange(0, len(a) - w + 1, h)
    rms = np.sqrt((c[pos + w] - c[pos]) / w)
    k = np.nonzero(rms >= 10 ** (umbral / 20))[0]
    return int(pos[k[0]]) if len(k) else None


def inicio_de_voz(mezcla: Path, voz: Path, esperado: float, primera: float, *, umbral_db: float, fps: int,
                  buscar_s: float = 0.5) -> dict[str, Any]:
    """Inicio de la voz de un cap en la mezcla. `esperado` = segundo de la primera palabra en el mp4 (intro + offset del
    cap + pre-roll + `primera`, el inicio de la primera palabra en su mp3).
    - medido: el corrimiento de la voz dentro de la mezcla (correlación con su mp3, ±`buscar_s`) + `primera`; ✓ si
      cae a ≤ 1 cuadro del esperado.
    - rampa: los 100 ms antes de que la mezcla llegue a −18 dB (RMS de 10 ms, paso de 1 ms) no son silencio: su
      energía (sin los últimos 10 ms, la ventana del salto mismo) está sobre la voz presente (`umbral_db`). Si no, la
      mezcla salta de silencio a −18 dB: «sin rampa»."""
    import numpy as np
    sr = 16000
    seg = 1.5                                        # lo que se correlaciona: la primera palabra y lo que sigue
    v = _pcm(voz, 0.0, primera + seg, sr).astype(np.float64)
    base = esperado - primera                        # dónde debería arrancar el mp3 dentro de la mezcla
    m = _pcm(mezcla, base - buscar_s, primera + seg + 2 * buscar_s, sr).astype(np.float64)
    lag = None
    if len(v) and len(m) > len(v):
        n = 1 << int(math.ceil(math.log2(len(m) + len(v))))
        c = np.fft.irfft(np.fft.rfft(m, n) * np.conj(np.fft.rfft(v, n)), n)[: len(m) - len(v) + 1]
        lag = base - buscar_s + int(np.argmax(c)) / sr
    medido = round(lag + primera, 3) if lag is not None else None
    sr2 = 48000
    desde = esperado - 2 * RAMPA_S
    a = _pcm(mezcla, desde, 2.0 + 2 * RAMPA_S, sr2)
    k = _cruce_db(a[int(RAMPA_S * sr2):], sr2, PICO_DB)       # el pico se busca desde 100 ms antes del esperado
    t18 = previo = None
    if k is not None:
        k += int(RAMPA_S * sr2)
        t18 = round(desde + k / sr2, 3)
        pre = a[max(0, k - int(RAMPA_S * sr2)):k - int(VENTANA_S * sr2)].astype(np.float64)   # sin la ventana del salto
        previo = round(db_de(float(np.sqrt(np.mean(pre ** 2)))) if len(pre) else -120.0, 1)
    rampa = previo is not None and previo >= umbral_db
    a_tiempo = medido is not None and abs(medido - esperado) <= 1.0 / fps + 1e-6
    return {"esperado": round(esperado, 3), "medido": medido, "t_18db": t18, "rampa": rampa, "a_tiempo": a_tiempo,
            "ok": bool(a_tiempo and rampa), "previo_db": previo, "umbral_db": round(umbral_db, 1)}


def linea_inicio(cap: str, r: dict[str, Any]) -> str:
    marca = "✓" if r["ok"] else "✗"
    med = f"{r['medido']:.2f}" if r["medido"] is not None else "—"
    t18 = f"{r['t_18db']:.2f} s" if r["t_18db"] is not None else "nunca (en 2 s)"
    ramp = (f"con rampa (100 ms previos: {r['previo_db']} dB)" if r["rampa"] else
            f"sin rampa (100 ms previos: {r['previo_db']} dB, bajo la voz presente {r['umbral_db']} dB)")
    return (f"{marca} {cap} · voz esperada {r['esperado']:.2f} s · medida {med} s"
            f"{'' if r['a_tiempo'] else ' (fuera de 1 cuadro)'} · llega a −18 dB en {t18} {ramp}")


# ═══════════════════════ §A.1 silencios de voz ═══════════════════════

def pausa_max_guion(raw: list[dict], tts_text: str) -> dict[str, Any]:
    """La pausa más larga que el propio guion marca en el cap: el hueco más largo en una marca `[… pause]` del texto
    de la voz (por posición de palabra, ±1 por si la marca cae corrida); sin marcas en medio del texto, el hueco más
    largo entre oraciones."""
    gaps = [(float(raw[i + 1]["start"]) - float(raw[i]["end"]), i) for i in range(len(raw) - 1)]
    pos, n = [], 0
    for tok in re.split(r"(\[[^\]]+\])", tts_text or ""):
        if tok.startswith("["):
            if "pause" in tok.lower() and 0 < n < len(raw):
                pos.append(n - 1)
        else:
            n += len(tok.split())
    en_marca = [max((g for g in gaps if abs(g[1] - p) <= 1), default=(0.0, p)) for p in pos]
    if en_marca:
        g, i = max(en_marca)
        return {"s": round(g, 2), "palabra": str(raw[i]["word"]), "como": "marca de pausa del guion"}
    fin = [g for g in gaps if re.search(r"[.!?…]$", str(raw[g[1]]["word"]).strip())]
    if fin:
        g, i = max(fin)
        return {"s": round(g, 2), "palabra": str(raw[i]["word"]), "como": "entre oraciones (sin marcas de pausa)"}
    return {"s": 0.0, "palabra": "", "como": "sin pausas"}


def silencios(raw: list[dict], umbral: float, time_offset: float) -> list[dict[str, Any]]:
    out = []
    for i in range(len(raw) - 1):
        g = float(raw[i + 1]["start"]) - float(raw[i]["end"])
        if g > umbral + 1e-6:
            out.append({"t": round(float(raw[i]["end"]) + time_offset, 3), "dur": round(g, 2),
                        "antes": str(raw[i]["word"]), "despues": str(raw[i + 1]["word"])})
    return out


# ═══════════════════════ eventos de un cap ═══════════════════════

def _crit_rot(c: dict | None) -> str:
    if not c:
        return ""
    if c.get("error"):
        return f" (crítico sin veredicto: {c['error']})"
    return (f" (crítico: (1) {'sí' if c.get('habla_de_eso') else 'no'} · (2) {'sí' if c.get('dice_algo_nuevo') else 'no'}"
            f" · (3) {'estorba' if c.get('estorba') else 'no estorba'})")


def _lectura(tipo: str, etiqueta: str | None, texto: str, autor: str = "") -> float:
    return round((len(etiqueta or "") + len(texto or "") + (len(autor) if tipo == "cita" else 0)) / LECTURA_CPS, 2)


def eventos_cap(c: dict[str, Any], *, title_dur: float, dip_frames: int, fps: int, intro: float) -> list[dict[str, Any]]:
    """Los eventos (y lo cortado) de un cap. `c` = lo que arma `cargar_cap`."""
    plan, escenas, beats, sents = c["plan"], c["escenas"], c["beats"], c["sents"]
    off = c["offset"]
    pool = c.get("pool_items") or {}
    ev: list[dict[str, Any]] = []

    def add(t: float, tipo: str, *, etiqueta: str | None = None, texto: str = "", dur: float | None = None,
            lectura: float | None = None, k: int | None = None, aporta: str | None = None, fuente: str | None = None,
            filtro: str = "pasó", queda: bool = True, extra: dict | None = None) -> dict:
        sc = _scene_at(escenas, t)
        bt = _beat_at(beats, t)
        kk = k if k is not None else _oracion_en(sents, t)
        vp, va, vn = _voz(sents, kk)
        e = {"t": round(t, 3), "t_mp4": round(off + t, 3), "cap": c["cap"], "beat": bt["n"] if bt else None,
             "funcion": bt["funcion"] if bt else "", "tipo": tipo, "etiqueta": etiqueta, "texto": texto,
             "dur": round(dur, 2) if dur is not None else None, "lectura_min": lectura,
             "escena": sc["idx"] if sc else None, "escena_t0": sc["start"] if sc else None,
             "escena_t1": sc["end"] if sc else None, "voz_prev": vp, "voz_ancla": va, "voz_next": vn,
             "aporta": aporta, "fuente": fuente, "filtro": filtro, "queda": queda, "papel": False, **(extra or {})}
        e["papel"] = bool(e["papel"])                  # F36 §C.4: vino del guion en papel (m01e_pantalla)
        ev.append(e)
        return e

    def fuente_de(pid: str | None) -> str | None:
        if not pid:
            return None
        it = pool.get(pid) or {}
        return f"{pid} · {it.get('fuente')}" if it.get("fuente") else pid

    # costura (negro → title → voz)
    v0 = c["primera_palabra"] + c["pre_pad"]
    tj0 = plan.get("tarjeta_inicial") if c["is_first"] else None
    if c["is_first"]:
        cuadro = (f"tarjeta «{tj0['texto']}» sobre negro, sin voz" if tj0 and tj0.get("texto") and not tj0.get("falta")
                  else "primer cuadro congelado, sin voz")         # F36 §B.9: la tarjeta reemplaza la intro
        txt = (f"intro {intro:.1f} s ({cuadro}) → title card {title_dur:.1f} s desde 0.0 s → "
               f"voz a {v0:.2f} s del cap (+{intro + v0:.2f} s del mp4)")
    else:
        bh = c.get("black_hold_prev") or {}
        sin_voz = f" sin voz (pre-roll {c['pre_roll']:.1f} s)" if c["pre_roll"] else ""
        txt = (f"negro {float(bh.get('duration') or 0):.1f} s (black hold de {c['prev']}) → corte → sube desde negro en "
               f"{dip_frames} cuadros ({dip_frames / fps:.2f} s) sobre el title card → title card {title_dur:.1f} s"
               f"{sin_voz} → voz a {v0:.2f} s del cap")
    add(0.0, "costura", texto=txt, k=None, extra={"tramos": {"negro_s": float((c.get("black_hold_prev") or {}).get("duration") or 0),
                                                         "sube_desde_negro_s": 0.0 if c["is_first"] else round(dip_frames / fps, 3),
                                                         "title_card_s": title_dur, "voz_s": round(v0, 3),
                                                         "intro_s": intro if c["is_first"] else 0.0}})
    tj = plan.get("tarjeta_inicial") if c["is_first"] else None
    if tj is not None:                                    # F34 §A.6: antes de la primera imagen, sobre negro
        e = add(0.0, "tarjeta fecha-hora", texto=tj.get("texto") or "⚠ falta fecha-hora", dur=title_dur, k=None,
                fuente=tj.get("fuente"), filtro=("pasó" if tj.get("texto") else f"⚠ falta fecha-hora: {tj.get('motivo')} "
                "(agregar con --plan-edit; nunca se inventa)") + (f" · {tj['difiere']}" if tj.get("difiere") else ""),
                extra={"sobre_negro": True, "papel": bool(tj.get("papel"))})
        e.update({"t": round(-intro, 3), "t_mp4": round(off - intro, 3), "escena": None, "beat": None, "funcion": ""})
    tc = plan.get("title_card")
    if tc:
        add(0.0, "title card", etiqueta=tc.get("kicker"), texto=tc.get("title", ""), dur=title_dur, k=None)
    for cb in plan.get("callouts") or []:
        tr = cb.get("tipo_rotulista") or ("persona" if cb.get("kind") == "name" else "cifra")
        add(float(cb["start"]), TIPO_ROT.get(tr, "ficha"), etiqueta=cb.get("kicker"), texto=cb.get("text", ""),
            dur=float(cb.get("duration", 0)), lectura=_lectura(tr, cb.get("kicker"), cb.get("text", "")),
            k=cb.get("sentence_idx"), aporta=cb.get("aporta"), fuente=fuente_de(cb.get("pool_id")),
            filtro="pasó" + _crit_rot(cb.get("critico")) + (" · editado a mano" if cb.get("editado") else ""),
            extra={"pool_id": cb.get("pool_id"), "a_pantalla": cb.get("a_pantalla"), "tipo_rotulista": tr,
                   "papel": cb.get("papel"), "estilo": cb.get("estilo"),
                   "word_idx": cb.get("word_idx"), "movido": cb.get("movido") or cb.get("movido_escena") or cb.get("movido_corte")})
    for a in plan.get("archive_clippings") or []:
        add(float(a["start"]), "recorte", etiqueta=a.get("kicker"), texto=a.get("headline", ""),
            dur=float(a.get("duration", 0)), lectura=_lectura("documento", a.get("kicker"), a.get("headline", "")),
            k=a.get("sentence_idx"), aporta=a.get("aporta"), fuente=fuente_de(a.get("pool_id")) or a.get("fuente"),
            filtro="pasó" + _crit_rot(a.get("critico")) + (" · editado a mano" if a.get("editado") else ""),
            extra={"pool_id": a.get("pool_id"), "a_pantalla": a.get("a_pantalla"), "papel": a.get("papel"),
                   "estilo": a.get("estilo"), "movido": a.get("movido") or a.get("movido_escena") or a.get("movido_corte"),
                   "forzado": a.get("forzado")})
    qc = plan.get("quote_card")
    if qc:
        add(float(qc["start"]), "cita", etiqueta=qc.get("author"), texto=qc.get("text", ""),
            dur=float(qc.get("duration", 0)), lectura=_lectura("cita", None, qc.get("text", ""), qc.get("author", "")),
            k=qc.get("sentence_idx"), aporta=qc.get("aporta"), fuente=fuente_de(qc.get("pool_id")),
            filtro="pasó" + _crit_rot(qc.get("critico")), extra={"pool_id": qc.get("pool_id")})
    z = plan.get("evidence_zoom")
    if z and "start" in z:
        add(float(z["start"]), "lupa", texto=str(z.get("detail") or z.get("anchor") or ""),
            dur=float(z.get("duration") or 0) or None, k=z.get("sentence_idx"), aporta=z.get("aporta"),
            fuente=fuente_de(z.get("pool_id")), filtro="pasó" + _crit_rot(z.get("critico")),
            extra={"pool_id": z.get("pool_id"), "caja": z.get("box")})
    wl = plan.get("water_level")
    if wl:
        add(float(wl["start"]), "nivel de agua", etiqueta=wl.get("etiqueta"),
            texto=f"{wl.get('value_text')} {wl.get('unit', '')}".strip(), dur=float(wl.get("duration") or 0),
            k=wl.get("sentence_idx"), aporta=wl.get("aporta"), fuente=fuente_de(wl.get("pool_id")),
            filtro="pasó" + _crit_rot(wl.get("critico")), extra={"pool_id": wl.get("pool_id"), "altura": wl.get("height"),
                                                                  "de_voz": bool(wl.get("de_voz"))})
    cu = plan.get("count_up")
    if cu:
        txt = f"{cu.get('value_text')} {cu.get('unit', '')}".strip()
        add(float(cu["start"]), "contador", etiqueta=cu.get("source") or None, texto=txt,
            dur=float(cu.get("duration") or 0) or None, lectura=_lectura("cifra", cu.get("source"), txt),
            k=cu.get("sentence_idx"), aporta=cu.get("aporta"), fuente=fuente_de(cu.get("pool_id")),
            filtro="pasó" + _crit_rot(cu.get("critico")), extra={"pool_id": cu.get("pool_id")})
    crit_sello = {round(float(r["t"]), 2): r for r in plan.get("critico") or [] if r.get("bloque") in ("sello", "icono")}
    for e in plan.get("emphasis") or []:
        r = crit_sello.get(round(float(e["start"]), 2))
        add(float(e["start"]), "sello", texto=str(e.get("word", "")), dur=float(e.get("duration", 0)),
            filtro="pasó" + (f" (crítico: {r['veredicto']})" if r else ""),
            extra={"tema": e.get("tema") or e.get("category"), "pico": bool(e.get("peak_word")), "lado": e.get("side"),
                   "clima": bool(e.get("clima")), "palabra_voz": e.get("palabra_voz"), "papel": e.get("papel")})
    tk = plan.get("time_ticker")
    if tk:
        add(float(tk["start"]), "reloj", texto=f"{tk.get('day')} {tk.get('month')} · {tk.get('tail', '')}".strip(" ·"),
            dur=float(tk.get("duration", 0)), fuente=tk.get("pool_id"),
            extra={"cambios": [f"{ch.get('day')} {ch.get('month')} @ {float(ch['t']):.1f}" for ch in tk.get("changes") or []],
                   "de_voz": bool(tk.get("de_voz"))})
    q = plan.get("chapter_question")
    if q:
        add(float(q["start"]), "pregunta de cierre", texto=q.get("text", ""), dur=float(q.get("duration", 0)),
            lectura=round(len(q.get("text", "")) / LECTURA_CPS, 2), k=len(sents) - 1 if sents else None,
            fuente=q.get("fuente"), extra={"pausa_s": q.get("pause")})
    bh = plan.get("black_hold")
    if bh:
        add(float(bh["start"]), "costura", texto=f"negro {float(bh['duration']):.1f} s al cierre del cap (black hold)",
            dur=float(bh["duration"]), k=len(sents) - 1 if sents else None)
    # transiciones (el zoom_punch del pico es el «punch»)
    by_idx = {s["idx"]: s for s in escenas}
    for k, tr in sorted(((int(k), v) for k, v in (plan.get("transitions") or {}).items()), key=lambda x: x[0]):
        s = by_idx.get(k)
        if s is None:
            continue
        kind = tr.get("kind", "cut")
        cuadros = f" {tr['frames']} cuadros" if tr.get("frames") else ""
        add(float(s["start"]), "punch" if kind == "zoom_punch" else "transición", texto=f"{kind}{cuadros}",
            extra={"razon": tr.get("why"), "saliente": k - 1, "entrante": k})
    # silencios de voz
    for g in c["silencios"]:
        add(g["t"], "silencio de voz", texto=f"{g['dur']:.2f} s entre «{g['antes']}» y «{g['despues']}»", dur=g["dur"],
            extra={"umbral_s": c["pausa_max"]["s"]})
    # lo que se cortó
    for r in c["cortes"]:
        t = r.get("t")
        if t is None:
            k = r.get("sentence_idx")
            t = sents[int(k)]["t0"] if isinstance(k, int) and 0 <= k < len(sents) else 0.0
        add(float(t), r["tipo"], etiqueta=r.get("etiqueta"), texto=str(r.get("texto") or ""), k=r.get("sentence_idx"),
            aporta=r.get("aporta"), fuente=fuente_de(r.get("pool_id")), filtro=f"cortó {r['quien']}: {r['motivo']}",
            queda=False, lectura=r.get("lectura"), extra={"pool_id": r.get("pool_id"), "regla": r["regla"],
                                                          "papel": r.get("papel")})
    ev.sort(key=lambda e: (e["t_mp4"], not e["queda"], e["tipo"] != "costura"))
    return ev


def cortes_cap(plan: dict[str, Any], rejected: list[dict], sents: list[dict]) -> list[dict[str, Any]]:
    """Lo que cada filtro sacó, en filas parejas {tipo, texto, etiqueta, pool_id, sentence_idx, t, regla, quien, motivo}."""
    out: list[dict[str, Any]] = []
    rot = plan.get("rotulista") or {}
    papel = plan.get("papel") is not None                 # F36 §C.4: con papel, los textos del rotulista son del papel
    for f in rot.get("filas") or []:
        if f.get("accion") != "fuera":
            continue
        tr = str(f.get("tipo") or "")
        out.append({"tipo": TIPO_ROT.get(tr, tr or "texto"), "texto": f.get("texto"), "etiqueta": f.get("etiqueta"),
                    "pool_id": f.get("pool_id"), "sentence_idx": f.get("sentence_idx"), "t": f.get("t0"),
                    "regla": REGLA_NOMBRE.get(f.get("regla"), f.get("regla")), "quien": f"rotulista ({REGLA_NOMBRE.get(f.get('regla'), f.get('regla'))})",
                    "motivo": f.get("motivo"), "aporta": f.get("aporta"), "papel": papel,
                    "lectura": _lectura(tr, f.get("etiqueta"), str(f.get("texto") or ""))})
    for f in rot.get("escena") or []:
        if f.get("accion") != "fuera":
            continue
        tr = str(f.get("tipo") or "")
        tipo = "reloj" if f.get("bloque") == "time_ticker" else TIPO_ROT.get(tr, tr or "texto")
        out.append({"tipo": tipo, "texto": f.get("texto"), "pool_id": f.get("pool_id"), "t": f.get("t0"),
                    "regla": "zona", "quien": "zona (nunca al mismo tiempo)", "motivo": f.get("motivo"),
                    "papel": papel and f.get("bloque") != "time_ticker"})
    real = plan.get("realizador") or {}
    for f in list(plan.get("sellos_tema") or []) + list(real.get("filas") or []):   # F32 §B.6: el catálogo de sellos
        if f.get("accion") != "fuera":
            continue
        b = f.get("bloque")
        tipo = {"emphasis": "sello", "punch_in": "punch_in", "count_up": "contador", "callouts": "ficha",
                "archive_clippings": "recorte", "quote_card": "cita"}.get(b, b or "bloque")
        out.append({"tipo": tipo, "texto": f.get("texto"), "pool_id": f.get("pool_id"), "t": f.get("t"),
                    "regla": f.get("regla") or "realizador",
                    "quien": f.get("quien") or "realizador", "motivo": f.get("motivo"), "papel": f.get("papel")})
    for r in plan.get("critico") or []:
        if r.get("pasa"):
            continue
        tipo = {"sello": "sello", "icono": "sello", "recorte": "recorte", "dato": "ficha", "ficha": "ficha",
                "cita": "cita", "contador": "contador", "nivel_agua": "nivel de agua", "zoom": "lupa"}.get(r.get("bloque"), r.get("bloque"))
        out.append({"tipo": tipo, "texto": r.get("texto"), "t": r.get("t"), "regla": "crítico",
                    "quien": "crítico", "motivo": f"{r.get('veredicto')}: {r.get('motivo')} (mira {r.get('mira')})"})
    for r in plan.get("critico_rotulista") or []:
        if r.get("pasa"):
            continue
        tipo = {"ficha": "ficha", "recorte": "recorte", "cita": "cita", "zoom": "lupa", "contador": "contador",
                "nivel_agua": "nivel de agua"}.get(r.get("bloque"), r.get("bloque"))
        mot = " · ".join(x for x in (
            f"(1) {r.get('motivo_1')}" if r.get("habla_de_eso") is False else "",
            f"(2) {r.get('motivo_2')}" if r.get("dice_algo_nuevo") is False else "",
            f"(3) {r.get('motivo_3')}" if r.get("estorba") is True else "") if x)
        out.append({"tipo": tipo, "texto": r.get("texto"), "pool_id": r.get("pool_id"), "t": r.get("t"),
                    "regla": "crítico", "quien": f"crítico (mira {r.get('mira')}" + (", ¿estorba?)" if r.get("pregunta")
                                                                                     else ")"),
                    "motivo": mot or "no pasa", "aporta": r.get("aporta"), "papel": papel})
    for r in rejected or []:
        out.append({"tipo": {"data_callout": "ficha", "archive_clipping": "recorte", "keyword_emphasis": "sello",
                             "water_level": "nivel de agua", "count_up": "contador", "time_ticker": "reloj",
                             "title_card": "title card"}.get(r.get("block"), r.get("block")),
                    "texto": r.get("text"), "t": None, "regla": "candado", "quien": "candado literal",
                    "motivo": f"«{r.get('field')}» no es literal de las fuentes"})
    return out


# ═══════════════════════ §A.2 resumen por beat ═══════════════════════

def resumen_beats(c: dict[str, Any], eventos: list[dict]) -> list[dict[str, Any]]:
    """Por beat: función, ventana, escenas, propuestos (director / rotulista), cortados por regla, quedan."""
    out = []
    for b in c["beats"]:
        evb = [e for e in eventos if e["beat"] == b["n"] and e["tipo"] not in ("costura", "transición", "punch",
                                                                                "silencio de voz", "title card")]
        dirc = [e for e in evb if e["tipo"] in ("sello", "reloj", "punch_in")]           # director (y el realizador)
        rotc = [e for e in evb if e not in dirc and e["tipo"] != "pregunta de cierre"]  # rotulista (la pregunta es la escaleta)
        punches = [e for e in eventos if e["beat"] == b["n"] and e["tipo"] == "punch"]
        cort: dict[str, list[str]] = {}
        for e in evb:
            if not e["queda"]:
                cort.setdefault(e.get("regla") or "?", []).append(
                    f"{e.get('pool_id') or e['tipo']} «{(e['texto'] or '')[:40]}»: {e['filtro'].split(': ', 1)[-1][:110]}")
        quedan = [e for e in evb if e["queda"]]
        escenas = sorted({s["idx"] for s in c["escenas"] if s["start"] < b["t1"] and s["end"] > b["t0"] - 0.3})
        out.append({"n": b["n"], "funcion": b["funcion"], "t0": b["t0"], "t1": b["t1"], "escenas": escenas,
                    "propuestos_director": len(dirc) + len(punches), "propuestos_rotulista": len(rotc),
                    "cortados": cort, "quedan": [f"{e['tipo']} «{(e['texto'] or '')[:40]}»" for e in quedan],
                    "punch": len(punches), "vacio": not quedan and not punches})
    return out


# ═══════════════════════ §A.3 chequeos ═══════════════════════

def _ocupa(e: dict, escenas: list[dict], title_dur: float) -> list[int]:
    if e["tipo"] == "title card":
        return [s["idx"] for s in escenas if s["start"] < title_dur]
    if e["tipo"] == "reloj":
        a, b = e["t"], e["t"] + float(e["dur"] or 0)
        return [s["idx"] for s in escenas if s["start"] < b and s["end"] > a]
    return [e["escena"]] if e["escena"] is not None else []


def chequeos(caps: list[dict[str, Any]], *, title_dur: float, fps: int, mezcla: dict[str, Any] | None,
             voz_video: list[str]) -> list[dict[str, Any]]:
    from script_engine.gfx_rotulista import contradicciones
    out = []
    # 1. dos bloques al mismo tiempo (DECISIONES 2026-10-26 17:58: «nunca al mismo tiempo» reemplaza a «una por
    # escena»: no se solapan ni se tocan; la escena deja de ser la unidad)
    lineas, ok = [], True
    for c in caps:
        bl = sorted([e for e in c["eventos"] if e["queda"] and e["tipo"] in TEXTOS + ANIMACIONES + ("title card",)],
                    key=lambda e: e["t"])
        for i, a in enumerate(bl):
            for b in bl[i + 1:]:
                a1, b1 = a["t"] + float(a["dur"] or 0), b["t"] + float(b["dur"] or 0)
                if a["t"] <= b1 + 1e-6 and b["t"] <= a1 + 1e-6:
                    ok = False
                    lineas.append(f"✗ {c['cap']} {a['tipo']} «{(a['texto'] or '')[:30]}» {a['t']:.1f}–{a1:.1f} s y "
                                  f"{b['tipo']} «{(b['texto'] or '')[:30]}» {b['t']:.1f}–{b1:.1f} s se solapan o se tocan")
    out.append({"nombre": "dos bloques al mismo tiempo", "ok": ok,
                "lineas": lineas or ["✓ ningún par de bloques (title card, textos y animaciones) se solapa ni se toca"]})
    # 2. bloque que cruza corte
    lineas, ok = [], True
    for c in caps:
        for e in c["eventos"]:
            if not e["queda"] or e["tipo"] not in TEXTOS + ("sello", "nivel de agua", "lupa") or not e["dur"]:
                continue
            fin = e["t"] + float(e["dur"])
            if e["escena_t1"] is not None and fin > float(e["escena_t1"]) + 1.0 / fps:
                ok = False
                lineas.append(f"✗ {c['cap']} {mmss(e['t_mp4'])} {e['tipo']} «{(e['texto'] or '')[:40]}» termina en "
                              f"{fin:.2f} s y la escena {e['escena']} corta en {float(e['escena_t1']):.2f} s")
    out.append({"nombre": "bloque que cruza un corte", "ok": ok,
                "lineas": lineas or ["✓ ningún texto, sello, nivel de agua ni lupa cruza un corte (el reloj de esquina no cuenta)"]})
    # 3. texto sin lectura · 4. pregunta sin lectura
    for nombre, tipos in (("texto sin lectura", TEXTOS), ("pregunta de cierre sin lectura", ("pregunta de cierre",))):
        lineas, ok = [], True
        n = 0
        for c in caps:
            for e in c["eventos"]:
                if e["queda"] and e["tipo"] in tipos and e["lectura_min"] is not None and e["dur"] is not None:
                    n += 1
                    if e["dur"] + 1e-6 < e["lectura_min"]:
                        ok = False
                        lineas.append(f"✗ {c['cap']} {mmss(e['t_mp4'])} {e['tipo']} «{(e['texto'] or '')[:40]}»: dura "
                                      f"{e['dur']:.2f} s y pide {e['lectura_min']:.2f} s")
        out.append({"nombre": nombre, "ok": ok, "lineas": lineas or [f"✓ {n} con su lectura a {LECTURA_CPS:.0f} cps"]})
    # 5. cifra que contradice la voz
    lineas, ok, n = [], True, 0
    for c in caps:
        for e in c["eventos"]:
            if e["queda"] and e["tipo"] in TEXTOS + ("nivel de agua",):
                n += 1
                con = contradicciones(f"{e.get('etiqueta') or ''} {e.get('texto') or ''}", voz_video,   # F36 §B.5
                                      cerca=[x for x in (e.get("voz_prev"), e.get("voz_ancla"), e.get("voz_next")) if x])
                if con:
                    ok = False
                    lineas.append(f"✗ {c['cap']} {mmss(e['t_mp4'])} «{e['texto']}»: " + "; ".join(con[:2]))
    out.append({"nombre": "cifra que contradice la voz", "ok": ok, "lineas": lineas or [f"✓ {n} textos sin contradicción"]})
    # 6. a_pantalla faltantes
    lineas, ok = [], True
    total = sum(len(c["a_pantalla"]) for c in caps)
    salen = 0
    for c in caps:
        en = {e.get("pool_id") for e in c["eventos"] if e["queda"] and e.get("pool_id")}
        for i in c["a_pantalla"]:
            if i in en:
                salen += 1
                continue
            ok = False
            mot = next((e["filtro"] for e in c["eventos"] if not e["queda"] and e.get("pool_id") == i), None) \
                or (c["plan"].get("rotulista") or {}).get("motivo_faltan", {}).get(i) or "el rotulista no lo propuso"
            lineas.append(f"✗ {c['cap']} {i}: {mot}")
    out.append({"nombre": "a_pantalla", "ok": ok, "lineas": [f"{'✓' if ok else '✗'} {salen}/{total} en pantalla"] + lineas})
    # 7. costuras
    lineas, ok = [], True
    for a, b in zip(caps, caps[1:]):
        bh = a["plan"].get("black_hold")
        fin = a["seg_dur"]
        if not bh:
            ok = False
            lineas.append(f"✗ {a['cap']}→{b['cap']}: el cap saliente no cierra en negro (sin black hold)")
            continue
        t0, t1 = float(bh["start"]), float(bh["start"]) + float(bh["duration"])
        hasta_corte = abs(t1 - fin) <= 1.0 / fps + 1e-3
        voz_db = None
        if mezcla and mezcla.get("narracion"):
            lv = niveles_db(Path(mezcla["narracion"]), a["offset"] - mezcla["intro"] + t0, t1 - t0)
            voz_db = round(max(lv), 1) if lv else None
        callada = voz_db is None or voz_db < mezcla["umbral_db"]
        good = hasta_corte and callada
        ok &= good
        lineas.append(f"{'✓' if good else '✗'} {a['cap']}→{b['cap']} ({mmss(a['offset'] + fin)}): negro {t0:.2f}–{t1:.2f} s "
                      f"{'hasta el corte' if hasta_corte else f'y el cap termina en {fin:.2f} s'} · voz "
                      f"{'callada' if callada else 'presente'}{f' (máx {voz_db} dB)' if voz_db is not None else ''} · "
                      f"el entrante sube desde negro (corte a negro, sin fadewhite)")
    out.append({"nombre": "costuras con cuadro no negro", "ok": ok, "lineas": lineas})
    # 8. inicio de voz por cap
    lineas, ok = [], True
    for c in caps:
        r = c.get("inicio_voz")
        if r is None:
            continue
        ok &= r["ok"]
        lineas.append(linea_inicio(c["cap"], r))
    out.append({"nombre": "inicio de voz por cap", "ok": ok, "lineas": lineas or ["(sin mezcla: no medido)"]})
    # 9. F34: el gancho nunca vacío de todo (0–1 texto, 1 reloj, 1 sello; DECISIONES 2026-10-26 02:52 y §0b de F34)
    lineas, ok = [], True
    for c in caps:
        for b in c["resumen"]:
            if b["funcion"] != "gancho":
                continue
            hay = [f"{e['tipo']} «{(e['texto'] or '')[:30]}»" for e in c["eventos"] if e["queda"] and e["beat"] == b["n"]
                   and e["tipo"] in TEXTOS + ANIMACIONES]
            ok &= bool(hay)
            lineas.append(f"{'✓' if hay else '✗'} {c['cap']} beat {b['n']} (gancho): {'; '.join(hay) or 'vacío de todo'}")
    out.append({"nombre": "gancho no vacío", "ok": ok, "lineas": lineas or ["(sin beat gancho)"]})
    # 10. F34 §A.7.2: la música de cada cap arranca con su title card (medido en la pista, ±1 cuadro)
    lineas, ok = [], True
    for r in (mezcla or {}).get("musica") or []:
        if r.get("ok") is None:
            lineas.append(f"· {r['cap']}: title card {mmss(r['title_card_s'])} — {r.get('motivo')}")
            continue
        ok &= bool(r["ok"])
        lineas.append(f"{'✓' if r['ok'] else '✗'} {r['cap']}: title card {r['title_card_s']:.3f} s · música medida "
                      f"{r['medido_s']:.3f} s · desvío {r['desvio_s']:+.3f} s ({r['desvio_cuadros']:+.2f} cuadros)")
    out.append({"nombre": "inicio de música por cap", "ok": ok and bool(lineas),
                "lineas": lineas or ["(sin música o sin mezcla: no medido)"]})
    # 11. F34 §A.6: la tarjeta fecha-hora
    tj = [e for c in caps for e in c["eventos"] if e["tipo"] == "tarjeta fecha-hora"]
    out.append({"nombre": "tarjeta fecha-hora", "ok": bool(tj) and all("falta" not in e["filtro"] for e in tj),
                "lineas": [f"{'✓' if 'falta' not in e['filtro'] else '✗'} {mmss(e['t_mp4'])} «{e['texto']}» · "
                           f"{e.get('fuente') or ''} · {e['filtro']}" for e in tj] or ["✗ sin tarjeta (ch01 sin plan)"]})
    # 12–14. F36 §C.4: el guion en papel (m01e_pantalla) contra lo que Fase 2 colocó
    out += chequeos_papel(caps)
    return out


def chequeos_papel(caps: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """«papel sin colocar» (fichas y sellos del papel que Fase 2 cortó, con el motivo), «papel sin alinear» (oraciones
    del papel que no son iguales a ninguna de la voz: se anclaron a la más parecida) y «relojes del papel» (aclaración
    4: el reloj es el de la voz; si el del papel difiere, se anota)."""
    con = [c for c in caps if c["plan"].get("papel") is not None]
    if not con:
        return [{"nombre": "papel sin colocar", "ok": False, "lineas": ["✗ ningún cap trae guion en papel"]}]
    sin_col, sin_al, rel = [], [], []
    for c in con:
        pp = c["plan"]["papel"]
        if pp.get("error"):
            sin_col.append(f"✗ {c['cap']}: {pp['error']}")
        quedan = {e.get("pool_id") for e in c["eventos"] if e["queda"] and e.get("pool_id")}
        for f in (c["plan"].get("rotulista") or {}).get("filas") or []:
            pid = f.get("pool_id")
            if pid in quedan:
                continue
            mot = next((e["filtro"] for e in c["eventos"] if not e["queda"] and e.get("pool_id") == pid), None)
            sin_col.append(f"✗ {c['cap']} ficha {pid} «{f.get('etiqueta') or ''} · {f.get('texto')}»: "
                           f"{mot or f.get('motivo') or 'sin motivo anotado'}")
        for f in pp.get("sin_colocar") or []:
            sin_col.append(f"✗ {c['cap']} ficha {f.get('pool_id')}: {f.get('motivo')}")
        for f in c["plan"].get("sellos_tema") or []:
            if f.get("papel") and f.get("accion") == "fuera":
                sin_col.append(f"✗ {c['cap']} sello {f.get('texto')}: {f.get('motivo')}")
        for a in pp.get("sin_alinear") or []:
            sin_al.append(f"✗ {c['cap']} [{a['papel']}] «{a['texto'][:70]}» → voz [{a['voz']}] «"
                          f"{str(a.get('voz_texto') or '')[:70]}» (parecido {a['parecido']})")
        tk = c["plan"].get("time_ticker")
        voz = f"{tk.get('day')} {tk.get('month')} {tk.get('tail')}".strip() if tk else None
        for r in pp.get("relojes") or []:
            igual = voz is not None and _norm_fecha(r.get("fecha")) == _norm_fecha(voz)
            rel.append(f"{'✓' if igual else '·'} {c['cap']} papel «{r.get('fecha')}» en [{r.get('sentence_idx')}] · "
                       f"reloj de la voz {('«' + voz + '»') if voz else '—'}" + ("" if igual else " → difiere (anotado)"))
        if voz and not pp.get("relojes"):
            rel.append(f"· {c['cap']} el papel no trae reloj · reloj de la voz «{voz}» → difiere (anotado)")
    return [{"nombre": "papel sin colocar", "ok": not sin_col, "lineas": sin_col or ["✓ todo lo del papel quedó en pantalla"]},
            {"nombre": "papel sin alinear", "ok": not sin_al,
             "lineas": sin_al or [f"✓ las oraciones del papel de {len(con)} caps alinean con la voz"]},
            {"nombre": "relojes del papel (informativo)", "ok": True, "lineas": rel or ["· sin relojes en el papel"]}]


def _norm_fecha(s: Any) -> str:
    from script_engine import evidence as ev
    return " ".join(re.findall(r"[^\W_]+", ev.norm(str(s or ""))))


# ═══════════════════════ armado y salida ═══════════════════════

def armar(caps_in: list[dict[str, Any]], *, title_dur: float, dip_frames: int, fps: int, intro: float,
          mezcla: dict[str, Any] | None, voz_video: list[str], topic: str, extra: dict | None = None) -> dict[str, Any]:
    """El guion entero. `caps_in` en orden; cada uno con plan, escenas, beats, sents, raw, offset, seg_dur, pre_pad,
    pre_roll, primera_palabra, tts_text, a_pantalla, pool_items, is_first, audio (mp3)."""
    caps = []
    prev = None
    for c in caps_in:
        c = dict(c)
        c["pausa_max"] = pausa_max_guion(c["raw"], c.get("tts_text") or "")
        c["silencios"] = silencios(c["raw"], c["pausa_max"]["s"], c["pre_pad"])
        c["cortes"] = cortes_cap(c["plan"], c.get("rejected") or [], c["sents"])
        c["prev"] = prev["cap"] if prev else None
        c["black_hold_prev"] = (prev["plan"].get("black_hold") if prev else None)
        c["eventos"] = eventos_cap(c, title_dur=title_dur, dip_frames=dip_frames, fps=fps, intro=intro)
        c["resumen"] = resumen_beats(c, c["eventos"])
        c["sin_texto"] = not any(e["queda"] and e["tipo"] in TEXTOS for e in c["eventos"])
        if mezcla and mezcla.get("mezcla") and c.get("audio"):
            c["inicio_voz"] = inicio_de_voz(Path(mezcla["mezcla"]), Path(c["audio"]),
                                            c["offset"] + c["pre_pad"] + c["primera_palabra"], c["primera_palabra"],
                                            umbral_db=mezcla["umbral_db"], fps=fps)
        caps.append(c)
        prev = c
    ch = chequeos(caps, title_dur=title_dur, fps=fps, mezcla=mezcla, voz_video=voz_video)
    keep = ("cap", "n", "titulo", "offset", "seg_dur", "pre_roll", "pre_pad", "primera_palabra", "pausa_max",
            "eventos", "resumen", "sin_texto", "inicio_voz", "a_pantalla")
    return {"version": VERSION, "topic": topic, "generado": time.strftime("%Y-%m-%d %H:%M:%S"), "intro_s": intro,
            "fps": fps, "title_dur": title_dur, "duracion_s": round(caps[-1]["offset"] + caps[-1]["seg_dur"], 3) if caps else 0,
            "mezcla": mezcla, "caps": [{k: c.get(k) for k in keep} for c in caps], "chequeos": ch, **(extra or {})}


def _linea(e: dict) -> str:
    et = f"{e['etiqueta']} | " if e.get("etiqueta") else ""
    partes = [mmss(e["t_mp4"]), e["cap"], f"beat {e['beat']} ({e['funcion']})" if e["beat"] is not None else "beat —",
              e["tipo"], f"«{et}{e['texto']}»"]
    if e.get("dur") is not None:
        partes.append(f"dura {e['dur']:.1f} s" + (f" (lectura mínima {e['lectura_min']:.1f} s)" if e.get("lectura_min") is not None else ""))
    elif e.get("lectura_min") is not None:
        partes.append(f"lectura mínima {e['lectura_min']:.1f} s")
    if e.get("escena") is not None:
        partes.append(f"escena {e['escena']} ({float(e['escena_t0']):.1f} a {float(e['escena_t1']):.1f} s)")
    if e["tipo"] in ("transición", "punch"):
        partes.append(f"razón: {e.get('razon')} · escena {e.get('saliente')} → {e.get('entrante')}")
    if e["tipo"] not in ("costura", "transición", "punch", "title card"):
        partes += [f"voz −1: {e['voz_prev']}", f"voz ancla: {e['voz_ancla']}", f"voz +1: {e['voz_next']}"]
    if e.get("aporta"):
        partes.append(f"aporta: {e['aporta']}")
    if e.get("fuente"):
        partes.append(f"fuente: {e['fuente']}")
    if e.get("movido"):
        partes.append(f"movido: {e['movido']}")
    if e["tipo"] not in ("costura", "transición", "punch", "silencio de voz"):
        partes.append(f"filtro: {e['filtro']}")
        partes.append(f"papel: {'sí' if e.get('papel') else 'no'}")
    return ("✂ " if not e["queda"] else "") + " · ".join(str(p) for p in partes)


def a_markdown(g: dict[str, Any]) -> str:
    L = [f"# Guion de pantalla — {g['topic']}", "",
         f"Generado {g['generado']} por `fase2b --plan-only` ({g['version']}). Duración del mp4: {mmss(g['duracion_s'])} "
         f"({g['duracion_s']:.1f} s; intro {g['intro_s']:.1f} s, title card {g['title_dur']:.1f} s). Tiempos = segundo del mp4 "
         f"final. `✂` = propuesto y cortado (quién y por qué).", ""]
    if g.get("mezcla") and g["mezcla"].get("mezcla"):
        L += [f"Mezcla de previsualización (voz + música + sfx, sin video): `{g['mezcla']['mezcla']}`.", ""]
    for c in g["caps"]:
        n_txt = sum(1 for e in c["eventos"] if e["queda"] and e["tipo"] in TEXTOS)
        L += [f"## {c['cap']} — {c.get('titulo') or ''} ({mmss(c['offset'])}–{mmss(c['offset'] + c['seg_dur'])})", "",
              f"Segmento {c['seg_dur']:.2f} s · pre-roll {c['pre_roll']:.1f} s · primera palabra a {c['pre_pad'] + c['primera_palabra']:.2f} s "
              f"del cap · pausa más larga del guion {c['pausa_max']['s']:.2f} s ({c['pausa_max']['como']}"
              f"{', en «' + c['pausa_max']['palabra'] + '»' if c['pausa_max']['palabra'] else ''}) · textos en pantalla {n_txt}"
              + (" · **⚠ CAP SIN TEXTO**" if c["sin_texto"] else ""), ""]
        L += [f"- {_linea(e)}" for e in c["eventos"]]
        L += ["", "| beat | función | ventana | escenas | propuestos (director · rotulista) | cortados por regla | quedan |",
              "|---|---|---|---|---|---|---|"]
        for b in c["resumen"]:
            cort = "<br>".join(f"**{r}** ({len(v)}): " + "; ".join(v) for r, v in sorted(b["cortados"].items())) or "—"
            qd = "; ".join(b["quedan"]) + (f"{'; ' if b['quedan'] else ''}punch ×{b['punch']}" if b["punch"] else "")
            L.append(f"| {b['n']}{' ⚠ BEAT VACÍO' if b['vacio'] else ''} | {b['funcion']} | {b['t0']:.1f}–{b['t1']:.1f} s | "
                     f"{', '.join(map(str, b['escenas']))} | {b['propuestos_director']} · {b['propuestos_rotulista']} | {cort} | "
                     f"{qd or '—'} |")
        L.append("")
    L += ["## Chequeos", ""]
    for ch in g["chequeos"]:
        L.append(f"### {'✓' if ch['ok'] else '✗'} {ch['nombre']}")
        L += [f"- {x}" for x in ch["lineas"]]
        L.append("")
    return "\n".join(L)


def escribir(g: dict[str, Any], out_dir: Path) -> tuple[Path, Path]:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    md, js = out_dir / "GUION_PANTALLA.md", out_dir / "GUION_PANTALLA.json"
    md.write_text(a_markdown(g), encoding="utf-8")
    js.write_text(json.dumps(g, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    return md, js
