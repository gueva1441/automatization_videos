"""
diag_shock_curated_ventanas_chat38.py — MEDICIÓN (no fix): perfil de energía de
shock_curated por ventanas de 5s.

Resuelve el track de ch04 desde music_map.json (intent shock → *_curated.mp3),
mide mean_volume por bloques de 5s (ffmpeg -ss/-t + volumedetect) a lo largo de
TODO el track, marca la franja 5–44s (= 4:12–4:51 del video) y calcula el delta
franja-vs-resto para distinguir escenario A (pico puntual) de B (parejo).

LECTURA PURA: ffmpeg en modo análisis (-f null -), NO escribe audio/video.
NO toca tracks, params, sync_map, mp3 ni código de producción.

USO:
    python diag_shock_curated_ventanas_chat38.py
"""
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

# Consola Windows cp1252 no encodea ←/Δ/✓ — forzamos UTF-8 en stdout.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from config import BASE_DIR, OUTPUT_DIR

VID = "8286b193-ff82-4357-b32d-21ca30909c4d"
AUDIO_DIR = OUTPUT_DIR / "audio" / VID
MUSIC_MAP = AUDIO_DIR / "music_map.json"
WINDOW = 5.0                      # segundos por ventana
BAND_START, BAND_END = 5.0, 44.0  # franja que molesta (0:05–0:44 del track)

_FFMPEG = shutil.which("ffmpeg")
_FFPROBE = shutil.which("ffprobe")
_MEAN_RE = re.compile(r"mean_volume:\s*(-?\d+(?:\.\d+)?)\s*dB")


def _duration(path: Path) -> float | None:
    if _FFPROBE:
        proc = subprocess.run(
            [_FFPROBE, "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        try:
            return float(proc.stdout.strip())
        except (ValueError, AttributeError):
            return None
    return None


def _mean_window(path: Path, start: float, dur: float) -> float | None:
    proc = subprocess.run(
        [_FFMPEG, "-hide_banner", "-ss", f"{start}", "-t", f"{dur}",
         "-i", str(path), "-af", "volumedetect", "-f", "null", "-"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    out = (proc.stderr or "") + (proc.stdout or "")
    m = _MEAN_RE.search(out)
    return float(m.group(1)) if m else None


def main() -> int:
    if _FFMPEG is None:
        print("[FAIL] ffmpeg no está en PATH.")
        return 1
    if not MUSIC_MAP.exists():
        print(f"[FAIL] no se encontró music_map.json en {MUSIC_MAP}")
        return 1

    mmap = json.loads(MUSIC_MAP.read_text(encoding="utf-8"))
    ch04 = mmap.get("tracks_by_chapter", {}).get("ch04", {})
    mp3_rel = ch04.get("mp3_path")
    if not mp3_rel:
        print("[FAIL] ch04 no tiene mp3_path en music_map.")
        return 1
    track = BASE_DIR / mp3_rel
    if not track.exists():
        print(f"[FAIL] track no encontrado: {track}")
        return 1

    dur = _duration(track)
    print(f"music_map: {MUSIC_MAP}")
    print(f"track ch04 (intent shock): {ch04.get('track_id')} → {track}")
    print(f"duración total: {dur:.2f}s" if dur else "duración total: (ffprobe no disponible)")
    print(f"ventana: {WINDOW:.0f}s · franja marcada: {BAND_START:.0f}–{BAND_END:.0f}s\n")

    if not dur:
        # Sin ffprobe, medimos hasta que un bloque venga vacío (~fin del track).
        dur = 9999.0

    # ── Medir ventanas ──
    rows: list[tuple[float, float, float | None]] = []
    start = 0.0
    while start < dur:
        w = min(WINDOW, dur - start) if dur < 9999 else WINDOW
        mean = _mean_window(track, start, w)
        rows.append((start, start + w, mean))
        if mean is None and dur >= 9999:
            break  # fin del track (bloque vacío) cuando no teníamos duración
        start += WINDOW

    # Si medimos a ciegas, recortar la última fila vacía.
    if rows and rows[-1][2] is None and not _FFPROBE:
        rows.pop()

    # ── Tabla ──
    def in_band(a: float, b: float) -> bool:
        # la ventana solapa con [BAND_START, BAND_END]
        return a < BAND_END and b > BAND_START

    print("=" * 50)
    print(f"  {'ventana(s)':14} {'mean_volume(dB)':>15}   franja")
    print("=" * 50)
    band_vals, rest_vals = [], []
    missing = []
    for a, b, mean in rows:
        flag = "← franja" if in_band(a, b) else ""
        if mean is None:
            missing.append(f"{a:.0f}-{b:.0f}")
            print(f"  {a:5.0f}-{b:<7.0f} {'N/A':>15}   {flag}")
            continue
        if in_band(a, b):
            band_vals.append(mean)
        else:
            rest_vals.append(mean)
        print(f"  {a:5.0f}-{b:<7.0f} {mean:>15.1f}   {flag}")

    # ── Delta franja vs resto ──
    print("\n" + "-" * 50)
    band_mean = sum(band_vals) / len(band_vals) if band_vals else None
    rest_mean = sum(rest_vals) / len(rest_vals) if rest_vals else None
    all_vals = band_vals + rest_vals
    spread = (max(all_vals) - min(all_vals)) if all_vals else None

    if band_mean is not None:
        print(f"  mean(franja 5–44s)  = {band_mean:.1f} dB  ({len(band_vals)} ventanas)")
    if rest_mean is not None:
        print(f"  mean(resto track)   = {rest_mean:.1f} dB  ({len(rest_vals)} ventanas)")
    if band_mean is not None and rest_mean is not None:
        delta = band_mean - rest_mean
        print(f"  Δ franja − resto    = {delta:+.1f} dB")
    if spread is not None:
        print(f"  spread total (max−min de ventanas) = {spread:.1f} dB")

    # ── Veredicto crudo (solo el dato, sin proponer fix) ──
    if band_mean is not None and rest_mean is not None:
        delta = band_mean - rest_mean
        print("\n  VEREDICTO CRUDO:")
        if delta >= 3.0:
            print(f"    franja +{delta:.1f} dB sobre el resto → consistente con ESCENARIO A (pico puntual)")
        elif spread is not None and spread < 2.0:
            print(f"    spread {spread:.1f} dB <2 y Δ {delta:+.1f} → consistente con ESCENARIO B (track parejo)")
        else:
            print(f"    Δ {delta:+.1f} dB, spread {spread:.1f} dB → zona gris (ni pico claro ni perfectamente parejo)")

    if missing:
        print(f"\n  ⚠ ventanas sin medición: {missing}")
        return 1
    print(f"\n  ✓ track medido completo en ventanas de {WINDOW:.0f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
