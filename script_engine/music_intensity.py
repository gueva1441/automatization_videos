"""
script_engine/music_intensity.py — F28 §B.2: mapa de intensidad de la música por cap.

Desde los beats de la escaleta (`01a_escaleta.json`), los párrafos de la narración (`01b_narracion_v3.json`: cap,
beat, texto) y los timestamps de la voz (`output/audio/<id>/chNN_timestamps.json`), marca tramos
`silencio | fondo | sube | golpe` con tiempos (segundos desde el inicio del audio del cap). fase2b los aplica como
envolvente de volumen sobre la pieza de música del cap. Es un mapa de niveles, no audio nuevo. Sin gate, sin LLM.

Reglas fijas (HANDOFF_F28 §B.2):
    fondo     todo el cap, ganancia 0 dB (= music_volume del track).
    sube      los beats del cap con intensidad ≥ 4 que no son el pico del video: +3 dB (rampas de 1 s).
    golpe     solo el beat de pico del video (funcion «pico»): +5 dB al empezar y vuelta a fondo en 4 s.
    silencio  solo (a) en los 1.5 s antes del beat más intenso del cap y (b) durante una cita de testigo (« … » en un
              beat que trae una cita del pool con testigo=True). Fade de 1.5 s a −∞ y de vuelta. Nunca más de 2 por
              cap; (a) va primero.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import numpy as np

GANANCIA_DB = {"fondo": 0.0, "sube": 3.0, "golpe": 5.0}
FADE_SILENCIO_S = 1.5
SILENCIO_PREVIO_S = 1.5
VUELTA_GOLPE_S = 4.0
RAMPA_SUBE_S = 1.0
MAX_SILENCIOS = 2
SUBE_DESDE = 4
ENV_HZ = 100                       # resolución de la envolvente
_CITA = re.compile(r"«[^»]+»")


def _palabras(texto: str) -> list[str]:
    return re.findall(r"\S+", texto or "")


def tiempos_por_palabra(parrafos_cap: list[dict], timestamps: list[dict]) -> list[tuple[float, float]]:
    """(inicio, fin) de cada palabra del texto del cap, por proporción contra los timestamps de la voz (la voz puede
    tener otra cantidad de palabras: la narración normalizada expande cifras)."""
    n_txt = sum(len(_palabras(p["texto"])) for p in parrafos_cap)
    n_ts = len(timestamps)
    if not n_txt or not n_ts:
        return []
    out = []
    for i in range(n_txt):
        j0 = min(n_ts - 1, int(i * n_ts / n_txt))
        j1 = min(n_ts - 1, max(j0, int((i + 1) * n_ts / n_txt) - 1))
        out.append((float(timestamps[j0]["start"]), float(timestamps[j1]["end"])))
    return out


def tramos_de_cap(cap: int, beats: list[dict], parrafos: list[dict], timestamps: list[dict],
                  testigos: set[str], duracion: float) -> list[dict[str, Any]]:
    """Los tramos de un cap (ordenados por inicio). `beats` = todos los de la escaleta; `parrafos` = los del cap
    (cap, beat, texto, en orden); `testigos` = ids de citas del pool con testigo=True."""
    bc = [b for b in beats if int(b.get("cap") or 0) == cap]
    pc = [p for p in parrafos if int(p.get("cap") or 0) == cap]
    tw = tiempos_por_palabra(pc, timestamps)
    tramos: list[dict[str, Any]] = [{"nivel": "fondo", "t0": 0.0, "t1": round(duracion, 3)}]
    if not bc or not tw:
        return tramos
    # palabra de inicio y fin de cada beat y de cada cita
    beat_span: dict[int, list[int]] = {}
    citas: list[tuple[int, int, int]] = []          # (beat, palabra inicio, palabra fin)
    k = 0
    for p in pc:
        ws = _palabras(p["texto"])
        b = int(p.get("beat") or 0)
        s = beat_span.setdefault(b, [k, k + len(ws) - 1])
        s[1] = k + len(ws) - 1
        for m in _CITA.finditer(p["texto"]):
            a = len(_palabras(p["texto"][:m.start()]))
            citas.append((b, k + a, k + a + len(_palabras(m.group(0))) - 1))
        k += len(ws)
    t_beat = {b: (tw[s][0], tw[e][1]) for b, (s, e) in beat_span.items() if s < len(tw)}
    intens = {int(b["n"]): int(b.get("intensidad") or 0) for b in bc}
    pico_video = {int(b["n"]) for b in bc if str(b.get("funcion")) == "pico"}
    # sube
    for n, v in sorted(intens.items()):
        if v >= SUBE_DESDE and n not in pico_video and n in t_beat:
            tramos.append({"nivel": "sube", "t0": round(t_beat[n][0], 3), "t1": round(t_beat[n][1], 3), "beat": n})
    # golpe (solo el beat de pico del video)
    for n in sorted(pico_video):
        if n in t_beat:
            t0 = t_beat[n][0]
            tramos.append({"nivel": "golpe", "t0": round(t0, 3), "t1": round(min(duracion, t0 + VUELTA_GOLPE_S), 3),
                           "beat": n})
    # silencios: (a) antes del beat más intenso del cap, (b) citas de testigo
    sil: list[dict[str, Any]] = []
    if intens:
        top = max(sorted(intens), key=lambda n: intens[n])
        if top in t_beat and t_beat[top][0] >= SILENCIO_PREVIO_S + FADE_SILENCIO_S:
            t0 = t_beat[top][0]
            sil.append({"nivel": "silencio", "t0": round(t0 - SILENCIO_PREVIO_S, 3), "t1": round(t0, 3),
                        "motivo": f"antes del pico del cap (beat {top})"})
    ids_beat = {int(b["n"]): {str(b.get("dato_central") or "")} | {str(x) for x in (b.get("datos_apoyo") or [])}
                for b in bc}
    golpes = [(x["t0"] - FADE_SILENCIO_S, x["t1"] + FADE_SILENCIO_S) for x in tramos if x["nivel"] == "golpe"]
    for b, s, e in citas:
        if len(sil) >= MAX_SILENCIOS:
            break
        if e >= len(tw) or any(tw[s][0] - FADE_SILENCIO_S < g1 and tw[e][1] + FADE_SILENCIO_S > g0
                               for g0, g1 in golpes):
            continue                                   # el silencio no tapa el golpe del pico
        if ids_beat.get(b, set()) & testigos:
            sil.append({"nivel": "silencio", "t0": round(tw[s][0], 3), "t1": round(tw[e][1], 3),
                        "motivo": f"cita de testigo (beat {b})"})
    tramos += sil[:MAX_SILENCIOS]
    return sorted(tramos, key=lambda x: (x["t0"], x["nivel"] != "fondo"))


def ganancias(tramos: list[dict], duracion: float, hz: int = ENV_HZ) -> np.ndarray:
    """La envolvente lineal (no dB) a `hz` muestras por segundo. Prioridad: silencio > golpe > sube > fondo."""
    n = max(1, int(np.ceil(duracion * hz)) + 1)
    t = np.arange(n) / hz
    db = np.zeros(n)
    for tr in tramos:
        if tr["nivel"] != "sube":
            continue
        a, b = tr["t0"], tr["t1"]
        up = np.clip((t - (a - RAMPA_SUBE_S)) / RAMPA_SUBE_S, 0, 1)
        down = np.clip(((b + RAMPA_SUBE_S) - t) / RAMPA_SUBE_S, 0, 1)
        db = np.maximum(db, GANANCIA_DB["sube"] * np.minimum(up, down))
    for tr in tramos:
        if tr["nivel"] != "golpe":
            continue
        a = tr["t0"]
        caida = np.clip(1 - (t - a) / VUELTA_GOLPE_S, 0, 1) * (t >= a)
        db = np.maximum(db, GANANCIA_DB["golpe"] * caida)
    g = 10 ** (db / 20)
    for tr in tramos:
        if tr["nivel"] != "silencio":
            continue
        a, b = tr["t0"], tr["t1"]
        baja = np.clip((a - t) / FADE_SILENCIO_S, 0, 1)            # 1 lejos antes, 0 en a
        sube = np.clip((t - b) / FADE_SILENCIO_S, 0, 1)            # 0 en b, 1 después
        g = g * np.where(t < a, baja, np.where(t > b, sube, 0.0))
    return g


def aplicar_a_wav(wav: Path, tramos: list[dict]) -> None:
    """Aplica la envolvente a un WAV PCM 16-bit (in place). La duración sale del archivo."""
    import wave
    with wave.open(str(wav), "rb") as w:
        params = w.getparams()
        raw = w.readframes(params.nframes)
    x = np.frombuffer(raw, dtype=np.int16).reshape(-1, params.nchannels).astype(np.float64)
    sr = params.framerate
    env = ganancias(tramos, len(x) / sr)
    ts = np.arange(len(x)) / sr
    g = np.interp(ts, np.arange(len(env)) / ENV_HZ, env)
    y = np.clip(np.round(x * g[:, None]), -32768, 32767).astype(np.int16)
    with wave.open(str(wav), "wb") as w:
        w.setparams(params)
        w.writeframes(y.tobytes())


def mapa_del_topic(topic_id: str, steps_dir: Path, audio_dir: Path, duraciones: dict[str, float]) -> dict[str, Any]:
    """{chNN: [tramos]} para los caps con escaleta, narración y timestamps. `duraciones` = {chNN: segundos del
    segmento de música del cap} (audio + pausa de cierre)."""
    sd = steps_dir / topic_id
    esc = json.loads((sd / "01a_escaleta.json").read_text(encoding="utf-8"))
    nar = json.loads((sd / "01b_narracion_v3.json").read_text(encoding="utf-8"))
    pool = json.loads((sd / "00_pool_v3.json").read_text(encoding="utf-8"))
    testigos = {str(q.get("id")) for q in pool.get("citas") or [] if q.get("testigo") is True}
    out: dict[str, Any] = {}
    for ch, dur in duraciones.items():
        cap = int(str(ch).lstrip("ch"))
        tsf = audio_dir / f"{ch}_timestamps.json"
        ts = json.loads(tsf.read_text(encoding="utf-8")) if tsf.exists() else []
        out[ch] = tramos_de_cap(cap, esc.get("beats") or [], nar.get("parrafos") or [], ts, testigos, dur)
    return out
