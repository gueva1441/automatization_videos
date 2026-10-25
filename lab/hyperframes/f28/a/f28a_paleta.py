"""F28 §A — paleta musical del canal: pista de prueba → 30 pistas (5 por intent) → medidas (0 API) → Gemini escucha →
hoja de espectros. PARADA: el analista elige 12.

Etapas (cada una idempotente; costos en costos_f28a.json; log en f28a.log):
    prueba    1 plan (hook) + 1 pista de 180 s → audio_library/_paleta_f28/_prueba_hook.mp3/.json; guarda las
              cabeceras de la respuesta (créditos) y el costo a US$ 0.15/min (precio de Music API, igual en todos los
              planes: elevenlabs.io/pricing/api, facturado en dólares).
    generar   30 pistas de 180 s, 5 por intent (hook, setup, rising_tension, shock, consequences, outro):
              m07.plan_composicion (Gemini Flash) → m07.generar_con_plan (endpoint detailed + composition_plan).
              2 a la vez (el plan admite 2). Freno con lock antes de cada llamada: ElevenLabs US$ 25 (30 × 3 min = 13.50) y Gemini US$ 3.
              Una sola facturación por pista (una falla se anota, no se reintenta). Sin gate, sin librería.
    medidas   numpy + ffmpeg (sin API): ebur128, pulso, melodía, tonalidad (Krumhansl), banda de la voz, costura,
              parecido (MFCC) → PALETA_medidas.json + poda (se marca, no se borra).
    escucha   Gemini 2.5 Pro con el mp3 (una llamada por pista; el sonido del canal literal) → escucha/<id>.json crudo.
    hoja      PALETA_espectros.jpg (6×5, ffmpeg showspectrumpic + PIL).
Uso: PYTHONIOENCODING=utf-8 python -I lab/hyperframes/f28/a/f28a_paleta.py <etapa>
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import threading
import time
import traceback
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[4]
sys.path[:0] = [str(ROOT)]
LAB = Path(__file__).resolve().parent
F28 = LAB.parent
PAL = ROOT / "audio_library" / "_paleta_f28"
COSTOS = LAB / "costos_f28a.json"
INTENTS = ("hook", "setup", "rising_tension", "shock", "consequences", "outro")
POR_INTENT = 5
LARGO_MS = 180_000
USD_POR_MIN = 0.15
TOPE_EL = 25.00
TOPE_GEMINI = 3.00
_LOCK = threading.Lock()
_RES = {"el": 0.0}


class Parada(RuntimeError):
    pass


def _j(p: Path):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def _w(p: Path, obj) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=1, default=str), encoding="utf-8")


def _log(msg: str) -> None:
    print(msg, flush=True)
    with (LAB / "f28a.log").open("a", encoding="utf-8") as fh:
        fh.write(f"[{time.strftime('%H:%M:%S')}] {msg}\n")


def _costos() -> dict:
    return _j(COSTOS) or {"elevenlabs": [], "el_usd": 0.0, "gemini": {}, "gemini_usd": 0.0}


def _gemini_del_proceso() -> float:
    from cost_tracker import cost_tracker
    with cost_tracker._lock:
        return sum(e.total_cost for e in cost_tracker._all_entries() if "gemini" in e.service.lower())


def _anotar_gemini(etapa: str) -> None:
    with _LOCK:
        c = _costos()
        c["gemini"][etapa] = round(c["gemini"].get(etapa, 0.0) + _gemini_del_proceso(), 4)   # acumula si se repite
        c["gemini_usd"] = round(sum(c["gemini"].values()), 4)
        _w(COSTOS, c)


def _freno_gemini(etapa: str, peor: float) -> None:
    c = _costos()
    ya = sum(c["gemini"].values()) + _gemini_del_proceso()
    if ya + peor > TOPE_GEMINI:
        raise Parada(f"tope Gemini ({etapa}): {ya:.3f} + {peor:.3f} > {TOPE_GEMINI:.2f}")


def duracion(p: Path) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                         capture_output=True, text=True).stdout.strip()
    return float(out or 0)


# ═══════════════════════ generación ═══════════════════════

def una_pista(tid: str, intent: str, etapa: str) -> dict:
    from music_config import SONIDO_DEL_CANAL
    from script_engine import m07_music_director as m7
    mp3p, jp = PAL / f"{tid}.mp3", PAL / f"{tid}.json"
    if jp.exists():
        return _j(jp)
    PAL.mkdir(parents=True, exist_ok=True)
    peor = LARGO_MS / 60000 * USD_POR_MIN
    reg: dict = {"id": tid, "intent": intent, "largo_pedido_ms": LARGO_MS}
    t0 = time.time()
    try:
        _freno_gemini(etapa, 0.02)
        plan = m7.plan_composicion(intent, SONIDO_DEL_CANAL, LARGO_MS)
        reg["plan"] = plan
        with _LOCK:
            c = _costos()
            if c["el_usd"] + _RES["el"] + peor > TOPE_EL:
                raise Parada(f"tope ElevenLabs ({tid}): {c['el_usd']:.2f} + reservado {_RES['el']:.2f} + {peor:.2f} "
                             f"> {TOPE_EL:.2f}")
            _RES["el"] += peor
        try:
            mp3, meta, hdr = m7.generar_con_plan(plan)
        finally:
            with _LOCK:
                _RES["el"] -= peor
        mp3p.write_bytes(mp3)
        seg = duracion(mp3p)
        usd = round(seg / 60 * USD_POR_MIN, 4)
        reg.update(duracion_s=round(seg, 2), usd=usd, cabeceras=hdr,
                   creditos={k: v for k, v in hdr.items() if any(x in k.lower() for x in ("credit", "char", "cost"))},
                   song_metadata=meta.get("song_metadata"), composition_plan_devuelto=meta.get("composition_plan"),
                   segundos=round(time.time() - t0, 1))
        with _LOCK:
            c = _costos()
            c["elevenlabs"].append({"id": tid, "segundos_audio": round(seg, 2), "usd": usd})
            c["el_usd"] = round(sum(x["usd"] for x in c["elevenlabs"]), 4)
            _w(COSTOS, c)
        _log(f"[{tid}] {seg:.1f} s · US$ {usd:.3f} · {reg['segundos']} s de pared · cabeceras de costo {reg['creditos']}")
    except Parada:
        raise
    except Exception as e:  # noqa: BLE001
        reg.update(error=f"{type(e).__name__}: {e}", traceback=traceback.format_exc()[-1200:],
                   segundos=round(time.time() - t0, 1))
        _log(f"[{tid}] ERROR {reg['error'][:300]}")
    _w(jp, reg)
    return reg


def prueba() -> None:
    r = una_pista("_prueba_hook", "hook", "prueba")
    _anotar_gemini("prueba")
    if r.get("error"):
        raise Parada(f"la pista de prueba falló: {r['error'][:300]}")
    usd30 = round(30 * r["duracion_s"] / 60 * USD_POR_MIN, 2)
    _log(f"prueba: {r['duracion_s']} s → US$ {r['usd']} · 30 pistas ≈ US$ {usd30} (tope 25 → "
         f"{'30 pistas' if usd30 <= 25 else ('20 pistas' if usd30 <= 40 else 'PARADA')})")


def generar() -> None:
    usd30 = 30 * LARGO_MS / 60000 * USD_POR_MIN
    n = POR_INTENT if usd30 <= 25 else 4                      # §A.0: > 25 → 20 pistas
    if usd30 > 40:
        raise Parada("30 pistas pasan de US$ 40")
    jobs = [(f"{i}_{k:02d}", i) for i in INTENTS for k in range(1, n + 1)]
    with ThreadPoolExecutor(max_workers=2) as ex:      # F28: el plan de ElevenLabs admite 2 pedidos a la vez (429 con 3)
        list(ex.map(lambda a: una_pista(a[0], a[1], "generar"), jobs))
    _anotar_gemini("generar")


# ═══════════════════════ medidas (numpy + ffmpeg, sin API) ═══════════════════════

SR = 22050
NFFT, HOP = 4096, 1024
KK_MAY = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
KK_MEN = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])
NOTAS = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")
TONOS_OK = ("D minor", "F major", "A minor")


def pcm(p: Path) -> np.ndarray:
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(p), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.float32).astype(np.float64)


def ebur128(p: Path) -> dict:
    err = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(p), "-af", "ebur128=peak=true", "-f", "null",
                          "-"], capture_output=True, text=True, encoding="utf-8", errors="replace").stderr
    resumen = err[err.rfind("Summary:"):]
    f = lambda pat: float(re.search(pat, resumen).group(1))  # noqa: E731
    return {"I_lufs": f(r"I:\s+(-?[\d.]+) LUFS"), "LRA_lu": f(r"LRA:\s+(-?[\d.]+) LU"),
            "pico_dbtp": f(r"Peak:\s+(-?[\d.]+) dBFS")}


def stft(x: np.ndarray) -> np.ndarray:
    n = 1 + (len(x) - NFFT) // HOP
    idx = np.arange(NFFT)[None, :] + HOP * np.arange(n)[:, None]
    return np.abs(np.fft.rfft(x[idx] * np.hanning(NFFT), axis=1))        # (frames, bins)


def _mel(nb: int, nm: int = 40) -> np.ndarray:
    hz = np.fft.rfftfreq(NFFT, 1 / SR)
    m = lambda f: 2595 * np.log10(1 + f / 700)  # noqa: E731
    pts = 700 * (10 ** (np.linspace(m(30), m(SR / 2), nm + 2) / 2595) - 1)
    fb = np.zeros((nm, nb))
    for i in range(nm):
        lo, c, hi = pts[i:i + 3]
        fb[i] = np.clip(np.minimum((hz - lo) / (c - lo), (hi - hz) / (hi - c)), 0, None)
    return fb


def medir(p: Path) -> dict:
    x = pcm(p)
    S = stft(x)
    P = S ** 2
    hz = np.fft.rfftfreq(NFFT, 1 / SR)
    fps = SR / HOP
    out = {"duracion_s": round(len(x) / SR, 2), **ebur128(p)}
    # pulso: autocorrelación de los ataques (flujo espectral positivo menos su media móvil de 0.5 s: sin eso un drone
    # que cambia lento da ~0.8), lags de 40–200 BPM. Calibrado: drone de prueba 0.08, hook_curated (con pulso) 0.83
    logS = np.log1p(S)
    flux = np.clip(np.diff(logS, axis=0), 0, None).sum(axis=1)
    wm = int(0.5 * fps)
    flux = np.clip(flux - np.convolve(flux, np.ones(wm) / wm, mode="same"), 0, None)
    flux = flux - flux.mean()
    ac = np.correlate(flux, flux, mode="full")[len(flux) - 1:]
    lo, hi = int(fps * 60 / 200), int(fps * 60 / 40)
    out["pulso"] = round(float(ac[lo:hi + 1].max() / ac[0]) if ac[0] > 0 else 0.0, 3)
    # pulso lento (15–40 BPM: golpes cada 1.5–4 s, que la hoja de espectros muestra y la ventana de arriba no ve);
    # informativo, no poda
    lo2, hi2 = int(fps * 60 / 40), int(fps * 60 / 15)
    out["pulso_lento"] = round(float(ac[lo2:hi2 + 1].max() / ac[0]) if ac[0] > 0 else 0.0, 3)
    # cromagrama (55 Hz–5 kHz)
    sel = (hz >= 55) & (hz <= 5000)
    pc = (np.round(69 + 12 * np.log2(hz[sel] / 440)) % 12).astype(int)
    chroma = np.zeros((P.shape[0], 12))
    for k in range(12):
        chroma[:, k] = P[:, sel][:, pc == k].sum(axis=1)
    # melodía: ventanas de 2 s → entropía, nota dominante, cambios de la dominante
    w = int(2 * fps)
    ent, dom, frac = [], [], []
    for i in range(0, chroma.shape[0] - w + 1, w):
        v = chroma[i:i + w].sum(axis=0)
        v = v / v.sum() if v.sum() > 0 else np.full(12, 1 / 12)
        ent.append(float(-(v * np.log2(v + 1e-12)).sum()))
        dom.append(int(v.argmax()))
        frac.append(float(v.max()))
    cambios = float(np.mean([a != b for a, b in zip(dom, dom[1:])])) if len(dom) > 1 else 0.0
    out.update(entropia_notas=round(float(np.mean(ent)), 3), dominancia=round(float(np.mean(frac)), 3),
               cambios_dominante=round(cambios, 3),
               melodia=bool(cambios >= 0.5 and np.mean(frac) >= 0.2))
    # tonalidad: Krumhansl–Kessler sobre el cromagrama total
    g = chroma.sum(axis=0)
    mejores = []
    for t in range(12):
        for modo, perf in (("major", KK_MAY), ("minor", KK_MEN)):
            mejores.append((float(np.corrcoef(g, np.roll(perf, t))[0, 1]), f"{NOTAS[t]} {modo}"))
    mejores.sort(reverse=True)
    out.update(tonalidad=mejores[0][1], tonalidad_r=round(mejores[0][0], 3),
               tonalidad_2=mejores[1][1], tonalidad_ok=mejores[0][1] in TONOS_OK)
    # brillo en la banda de la voz
    tot = P.sum()
    out["banda_voz"] = round(float(P[:, (hz >= 1000) & (hz <= 4000)].sum() / tot) if tot else 0.0, 4)
    out["centroide_hz"] = round(float((P * hz).sum() / tot) if tot else 0.0, 1)
    # costura: últimos 2 s contra primeros 2 s
    n2 = int(2 * SR)
    a, b = x[-n2:], x[:n2]
    rms = lambda v: 20 * np.log10(np.sqrt(np.mean(v ** 2)) + 1e-9)  # noqa: E731
    seg = [rms(x[i:i + SR]) for i in range(0, len(x) - SR, SR)]
    med = float(np.median(seg))
    fa, fb_ = np.log1p(np.abs(np.fft.rfft(a))), np.log1p(np.abs(np.fft.rfft(b)))
    out.update(costura_corr=round(float(np.dot(fa, fb_) / (np.linalg.norm(fa) * np.linalg.norm(fb_))), 3),
               rms_inicio_db=round(rms(b) - med, 2), rms_final_db=round(rms(a) - med, 2))
    out["fade"] = bool(out["rms_inicio_db"] < -6 or out["rms_final_db"] < -6)
    # cuánto dura el fade (segundos hasta llegar a −6 dB de la mediana, al principio y al final): si son pocos, se
    # recorta al cargar la pista (dato para el analista, no cambia la poda)
    rel = np.array(seg) - med
    ok = np.nonzero(rel >= -6)[0]
    out["fade_in_s"] = int(ok[0]) if len(ok) else None
    out["fade_out_s"] = int(len(rel) - 1 - ok[-1]) if len(ok) else None
    # huecos: segundos entre los fades con más de 20 dB por debajo de la mediana (silencio en el medio de la pista)
    out["huecos_s"] = int((rel[ok[0]:ok[-1] + 1] < -20).sum()) if len(ok) else None
    # MFCC medio (40 mel + DCT-II, 13 coeficientes)
    mel = np.log(P @ _mel(P.shape[1]).T + 1e-10)
    n = mel.shape[1]
    dct = np.cos(np.pi / n * (np.arange(n) + 0.5)[None, :] * np.arange(13)[:, None])
    out["_mfcc"] = (mel @ dct.T).mean(axis=0).round(4).tolist()
    # poda (se marca, no se borra)
    motivos = []
    if out["pulso"] > 0.35:
        motivos.append(f"pulso {out['pulso']}")
    if not out["tonalidad_ok"]:
        motivos.append(f"tonalidad {out['tonalidad']}")
    if out["LRA_lu"] > 12:
        motivos.append(f"LRA {out['LRA_lu']}")
    if out["banda_voz"] > 0.30:
        motivos.append(f"banda-voz {out['banda_voz']}")
    if out["fade"]:
        motivos.append(f"fade en la costura ({out['rms_inicio_db']} / {out['rms_final_db']} dB)")
    out["poda"] = motivos
    return out


def medidas() -> None:
    res = {}
    for p in sorted(PAL.glob("*.mp3")):
        res[p.stem] = medir(p)
        _log(f"[medidas] {p.stem}: {res[p.stem]['tonalidad']} · pulso {res[p.stem]['pulso']} · LRA "
             f"{res[p.stem]['LRA_lu']} · voz {res[p.stem]['banda_voz']} · poda {res[p.stem]['poda'] or '—'}")
    # parecido: distancia coseno de los MFCC medios entre pistas del mismo intent
    for i in INTENTS:
        ids = [k for k in res if k.startswith(i + "_") and not k.startswith("_")]
        for a in ids:
            va = np.array(res[a]["_mfcc"])
            d = {}
            for b in ids:
                if b != a:
                    vb = np.array(res[b]["_mfcc"])
                    d[b] = round(float(1 - np.dot(va, vb) / (np.linalg.norm(va) * np.linalg.norm(vb))), 4)
            res[a]["parecido"] = d
            res[a]["mas_parecida"] = min(d, key=d.get) if d else None
    quedan = {i: sum(1 for k, v in res.items() if k.startswith(i + "_") and not v["poda"]) for i in INTENTS}
    # lectura para el analista (no cambia la poda): cuántas quedan sin la regla de fade
    sin_fade = {i: sum(1 for k, v in res.items() if k.startswith(i + "_")
                       and not [m for m in v["poda"] if not m.startswith("fade")]) for i in INTENTS}
    _w(F28 / "PALETA_medidas.json", {"pistas": res, "quedan_por_intent": quedan, "quedan_sin_la_regla_de_fade": sin_fade,
                                     "reglas": "fuera si pulso > 0.35, tonalidad ∉ {D minor, F major, A minor}, LRA > 12, "
                                               "banda-voz (1–4 kHz) > 0.30, o fade en la costura (inicio o final "
                                               "más de 6 dB por debajo de la mediana)"})
    _log(f"medidas: quedan por intent {quedan}")


# ═══════════════════════ Gemini escucha ═══════════════════════

ESCUCHA_SCHEMA = {"type": "OBJECT", "properties": {
    "descripcion": {"type": "STRING"}, "instrumentos": {"type": "ARRAY", "items": {"type": "STRING"}},
    "tiene_melodia": {"type": "BOOLEAN"}, "tiene_pulso": {"type": "BOOLEAN"}, "suena_a_trailer": {"type": "BOOLEAN"},
    "compite_con_voz": {"type": "BOOLEAN"}, "nota_canal": {"type": "INTEGER"}, "mejor_intent": {"type": "STRING"}},
    "required": ["descripcion", "instrumentos", "tiene_melodia", "tiene_pulso", "suena_a_trailer", "compite_con_voz",
                 "nota_canal", "mejor_intent"]}


def prompt_escucha() -> str:
    from music_config import SONIDO_DEL_CANAL
    return f"""Escuchá esta pista instrumental. Es una candidata para el fondo musical de un canal de documentales.

El sonido del canal:
{SONIDO_DEL_CANAL}

Devolvé un JSON con:
- descripcion: 2–3 frases de qué se oye.
- instrumentos: los que se oyen.
- tiene_melodia: true si hay una melodía que se recuerda.
- tiene_pulso: true si hay un pulso o un ritmo marcado.
- suena_a_trailer: true si tiene subidas o golpes de tráiler.
- compite_con_voz: true si ocuparía el lugar de una voz que narra encima.
- nota_canal: de 1 a 10, cuánto se ajusta al sonido del canal de arriba.
- mejor_intent: el uso que mejor le queda, uno de: hook, setup, rising_tension, shock, consequences, outro."""


def una_escucha(p: Path) -> dict:
    from google.genai import types
    import gemini_helpers as gh
    from cost_tracker import cost_tracker
    out = LAB / "escucha" / f"{p.stem}.json"
    if out.exists():
        return _j(out)
    _freno_gemini("escucha", 0.05)
    t0 = time.time()
    resp = gh._with_retry(lambda: gh._client.models.generate_content(
        model=gh._cfg.gemini_model_research,
        contents=[types.Part.from_bytes(data=p.read_bytes(), mime_type="audio/mp3"), prompt_escucha()],
        config=types.GenerateContentConfig(response_mime_type="application/json", response_schema=ESCUCHA_SCHEMA)))
    cost_tracker.track_gemini_response(resp, gh._cfg.gemini_model_research, f"f28a escucha {p.stem}")
    crudo = {"id": p.stem, "texto": resp.text, "finish_reason": gh._motivo(resp),
             "usage": str(getattr(resp, "usage_metadata", "")), "segundos": round(time.time() - t0, 1)}
    try:
        crudo["json"] = json.loads(resp.text)
    except (TypeError, ValueError) as e:
        crudo["error"] = f"{type(e).__name__}: {e}"
    _w(out, crudo)
    j = crudo.get("json") or {}
    _log(f"[escucha] {p.stem}: nota {j.get('nota_canal')} · {j.get('mejor_intent')} · melodía {j.get('tiene_melodia')} "
         f"· pulso {j.get('tiene_pulso')} · tráiler {j.get('suena_a_trailer')}")
    return crudo


def escucha() -> None:
    ps = [p for p in sorted(PAL.glob("*.mp3")) if not p.stem.startswith("_")]
    with ThreadPoolExecutor(max_workers=4) as ex:
        list(ex.map(una_escucha, ps))
    _anotar_gemini("escucha")


# ═══════════════════════ hoja de espectros ═══════════════════════

def hoja() -> None:
    from PIL import Image, ImageDraw, ImageFont
    d = LAB / "espectros"
    d.mkdir(exist_ok=True)
    med = (_j(F28 / "PALETA_medidas.json") or {}).get("pistas", {})
    ids = [f"{i}_{k:02d}" for i in INTENTS for k in range(1, POR_INTENT + 1)]
    tiles = []
    for tid in ids:
        png = d / f"{tid}.png"
        src = PAL / f"{tid}.mp3"
        if src.exists() and not png.exists():
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-lavfi",
                            "showspectrumpic=s=600x220:legend=0:scale=log:fscale=log:color=intensity", str(png)],
                           check=True)
        im = Image.open(png).convert("RGB") if png.exists() else Image.new("RGB", (600, 220), (40, 0, 0))
        canvas = Image.new("RGB", (600, 250), (18, 18, 18))
        canvas.paste(im.resize((600, 220)), (0, 30))
        m = med.get(tid, {})
        txt = f"{tid} · {m.get('tonalidad', '?')} · pulso {m.get('pulso', '?')} · LRA {m.get('LRA_lu', '?')}"
        if m.get("poda"):
            txt += " · PODA"
        dr = ImageDraw.Draw(canvas)
        try:
            font = ImageFont.truetype("arial.ttf", 17)
        except OSError:
            font = ImageFont.load_default()
        dr.text((8, 6), txt, fill=(255, 90, 90) if m.get("poda") else (235, 235, 235), font=font)
        tiles.append(canvas)
    cols, rows = 5, 6                                             # una fila por intent, 5 pistas por fila
    sheet = Image.new("RGB", (cols * 600, rows * 250), (0, 0, 0))
    for k, t in enumerate(tiles):
        sheet.paste(t, ((k % cols) * 600, (k // cols) * 250))
    sheet.save(F28 / "PALETA_espectros.jpg", quality=85)
    _log(f"hoja: {F28 / 'PALETA_espectros.jpg'} ({len(tiles)} espectros, {rows} filas × {cols})")


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    etapa = sys.argv[1]
    t0 = time.time()
    try:
        {"prueba": prueba, "generar": generar, "medidas": medidas, "escucha": escucha, "hoja": hoja}[etapa]()
    except Parada as e:
        _log(f"PARADA ({etapa}): {e}")
        sys.exit(2)
    c = _costos()
    _log(f"[{etapa}] {time.time() - t0:.0f} s · ElevenLabs US$ {c['el_usd']} · Gemini US$ {c['gemini_usd']}")


if __name__ == "__main__":
    main()
