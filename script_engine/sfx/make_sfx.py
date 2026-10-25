"""
make_sfx.py — La librería de SFX de la capa gráfica, generada con ElevenLabs Sound Effects (F29 §B).

Antes (F2 §0d) se sintetizaban con osciladores FFmpeg; esos wav quedaron en `_f2_sintetizados/` (con el script viejo,
`make_sfx_f2.py`). Ahora cada sonido sale de ElevenLabs con el prompt de abajo (inglés: el modelo lee inglés), mismos
nombres y duraciones, y se procesa igual para todos:
    1. se pide con `duration_seconds` = max(0.5, duración) (el endpoint no baja de 0.5 s);
    2. se saca el silencio del principio y se corta a la duración, con fades de 5 ms (entrada) y 20 ms (salida);
    3. se normaliza a −20 LUFS integrado (medido con el sonido rellenado de silencio a 3 s: el gate de −70 LUFS deja
       afuera el relleno) con techo de pico de −1 dBFS; la ganancia por bloque del perfil (`gfx_config`) va encima.
Caché: `_prompts.json` guarda prompt, duración y modelo de cada wav; si el wav existe y nada de eso cambió, no se llama.
Costo: precio publicado de la API, US$ 0.12 por minuto generado (se anota en `_prompts.json`).

Uso: python script_engine/sfx/make_sfx.py [nombre ...]      (sin nombres: los 15; los que estén en caché no se piden)
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import time
from pathlib import Path

SFX_DIR: Path = Path(__file__).parent
SR: int = 48_000
LUFS_OBJETIVO: float = -20.0
PICO_MAX_DB: float = -1.0
MODELO: str = "eleven_text_to_sound_v2"
PROMPT_INFLUENCE: float = 0.5
USD_POR_MIN: float = 0.12
API_URL: str = "https://api.elevenlabs.io/v1/sound-generation"
CACHE: Path = SFX_DIR / "_prompts.json"

# nombre → (duración s, prompt). Nada metálico, nada de cine de acción; todo seco y cerca, bajo la voz.
_SOUNDS: dict[str, tuple[float, str]] = {
    "tipeo": (0.75, "a few dry keystrokes of an old mechanical typewriter, close microphone, dry room, no reverb, "
                    "no bell"),
    "sello": (0.35, "a rubber stamp pressed once onto paper on a wooden desk, soft dull thud, close, dry, no reverb"),
    "papel": (0.6, "a sheet of paper sliding over a wooden table, close microphone, dry, no reverb"),
    "golpe_grave": (1.2, "a deep muffled low thud, distant, no tail, no reverb, not cinematic, not an explosion"),
    "whoosh": (0.8, "a short soft whoosh of air, gentle, low, smooth, no metallic sound"),
    "click": (0.08, "a single soft dry click of a small mechanism, close, no reverb"),
    "tic": (0.18, "a single soft dry tick of a small mechanism, close, no reverb"),
    "tic_sordo": (0.22, "a single muffled low tick, soft and dull, close, dry, no reverb"),
    "drone_subida": (3.0, "a low dark drone slowly rising in pitch and swelling, deep and quiet, no impact at the end, "
                          "no metallic sound, ambient"),
    "latido": (0.9, "a single slow heartbeat, two low muffled thumps, close, dry"),
    "brasa": (0.9, "soft crackling of small embers, close, quiet, dry"),
    "rumor": (1.2, "a low rumble of earth, distant and deep, quiet, no impact"),
    "zumbido": (0.9, "a faint low electrical hum with a few soft clicks of a counter, quiet, close"),
    "viento": (1.4, "a soft cold gust of wind, low, quiet, no whistle"),
    "vacio": (1.2, "a very low soft sub-bass tone that fades away, empty, quiet, no attack"),
}


def _cache() -> dict:
    return json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}


def lufs(path: Path) -> tuple[float, float]:
    """(LUFS integrado, pico dBFS) de un sonido corto: se rellena de silencio a 3 s para que el integrado exista."""
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af",
                        "apad=whole_dur=3,ebur128=peak=sample", "-f", "null", "-"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    s = r.stderr[r.stderr.rfind("Summary:"):]
    i = float(re.search(r"I:\s+(-?[\d.]+) LUFS", s).group(1))
    pk = re.search(r"Peak:\s+(-?[\d.inf]+) dBFS", s)
    return i, float(pk.group(1)) if pk else 0.0


def _pedir(prompt: str, dur: float) -> bytes:
    import requests
    sys.path.insert(0, str(SFX_DIR.parents[1]))
    from config import api
    r = requests.post(API_URL, headers={"xi-api-key": api.elevenlabs_api_key, "Content-Type": "application/json"},
                      json={"text": prompt, "duration_seconds": max(0.5, dur), "prompt_influence": PROMPT_INFLUENCE,
                            "model_id": MODELO}, params={"output_format": "mp3_44100_128"}, timeout=120)
    if r.status_code != 200:
        raise RuntimeError(f"ElevenLabs SFX HTTP {r.status_code}: {r.text[:300]}")
    return r.content


def _procesar(raw: Path, dst: Path, dur: float) -> dict:
    tmp = dst.with_name(f"_{dst.stem}.tmp.wav")
    fade_out = min(0.02, dur / 4)
    for recorte in ("silenceremove=start_periods=1:start_threshold=-50dB,", ""):
        # un sonido que arranca bajo (drone, zumbido) queda entero bajo −50 dB: el recorte lo vacía → sin recorte
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-af",
                        f"{recorte}atrim=0:{dur},apad=whole_dur={dur},"
                        f"afade=t=in:d=0.005,afade=t=out:st={dur - fade_out:.3f}:d={fade_out:.3f}",
                        "-ar", str(SR), "-ac", "1", "-c:a", "pcm_s16le", str(tmp)], check=True, timeout=60)
        det = subprocess.run(["ffmpeg", "-v", "info", "-i", str(tmp), "-af", "volumedetect", "-f", "null", "-"],
                             capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60).stderr
        m = re.search(r"max_volume: (-?[\d.]+) dB", det)
        if m and float(m.group(1)) > -90:
            break
    # pico a −1 dBFS antes de medir: un sonido muy bajo cae bajo el gate absoluto de −70 LUFS y ebur128 no lo mide
    pico = float(m.group(1)) if m else 0.0
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(tmp), "-af", f"volume={PICO_MAX_DB - pico:.2f}dB",
                    "-c:a", "pcm_s16le", str(tmp.with_suffix(".pk.wav"))], check=True, timeout=60)
    tmp.with_suffix(".pk.wav").replace(tmp)
    i0, _ = lufs(tmp)
    gain = LUFS_OBJETIVO - i0
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(tmp), "-af",
                    f"volume={gain:.2f}dB,alimiter=limit={10 ** (PICO_MAX_DB / 20):.4f}:level=false",
                    "-ar", str(SR), "-ac", "1", "-c:a", "pcm_s16le", str(dst)], check=True, timeout=60)
    tmp.unlink(missing_ok=True)
    i1, pk = lufs(dst)
    return {"lufs_crudo": i0, "ganancia_db": round(gain, 2), "lufs": i1, "pico_db": pk}


def make_all(out_dir: Path = SFX_DIR, only: list[str] | None = None, tope_usd: float | None = None) -> list[dict]:
    """Genera (o deja de la caché) los SFX. Devuelve un registro por sonido."""
    cache = _cache()
    out, gastado = [], 0.0
    for name, (dur, prompt) in _SOUNDS.items():
        if only and name not in only:
            continue
        dst = out_dir / f"{name}.wav"
        clave = {"prompt": prompt, "duracion": dur, "modelo": MODELO, "prompt_influence": PROMPT_INFLUENCE}
        if dst.exists() and {k: cache.get(name, {}).get(k) for k in clave} == clave:
            out.append({"nombre": name, **cache[name], "en_cache": True})
            continue
        usd = round(max(0.5, dur) / 60 * USD_POR_MIN, 5)
        if tope_usd is not None and gastado + usd > tope_usd:
            raise RuntimeError(f"tope de US$ {tope_usd} para los SFX")
        t0 = time.time()
        raw = out_dir / f"_{name}.raw.mp3"
        raw.write_bytes(_pedir(prompt, dur))
        info = _procesar(raw, dst, dur)
        raw.unlink(missing_ok=True)
        gastado += usd
        cache[name] = {**clave, **info, "usd": usd, "segundos": round(time.time() - t0, 1)}
        CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")
        out.append({"nombre": name, **cache[name], "en_cache": False})
    return out


if __name__ == "__main__":
    for r in make_all(only=sys.argv[1:] or None, tope_usd=3.0):        # python make_sfx.py tic_sordo → solo ese
        extra = " (caché)" if r["en_cache"] else f" · US$ {r.get('usd')}"
        print(f"{r['nombre']:<13} {r['duracion']:>4}s · {r['lufs']} LUFS · pico {r['pico_db']} dBFS{extra}")
