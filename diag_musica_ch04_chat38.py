"""
diag_musica_ch04_chat38.py — MEDICIÓN (no fix): niveles narración vs música por cap.

Mide con ffmpeg volumedetect el mean/max volume (dB) de:
  - la narración de cada cap (output/audio/<VID>/chNN.mp3)
  - el track de música EFECTIVO de cada cap (resuelto desde music_map.json →
    audio_library/<track>_curated.mp3)

Tabula los 7 caps y calcula 2 deltas para ch04 (vs promedio de los otros).
LECTURA PURA: ffmpeg en modo análisis (-f null -), NO escribe audio/video.
NO toca params, sync_map, mp3 ni tracks.

USO:
    python diag_musica_ch04_chat38.py
"""
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

# Consola Windows en cp1252 no encodea ←/Δ/⇒/✓ — forzamos UTF-8 en stdout.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from config import BASE_DIR, OUTPUT_DIR

VID = "8286b193-ff82-4357-b32d-21ca30909c4d"
AUDIO_DIR = OUTPUT_DIR / "audio" / VID
MUSIC_MAP = AUDIO_DIR / "music_map.json"
CAPS = [f"ch{n:02d}" for n in range(1, 8)]

_FFMPEG = shutil.which("ffmpeg")

_MEAN_RE = re.compile(r"mean_volume:\s*(-?\d+(?:\.\d+)?)\s*dB")
_MAX_RE = re.compile(r"max_volume:\s*(-?\d+(?:\.\d+)?)\s*dB")


def _volumedetect(path: Path) -> tuple[float | None, float | None]:
    """Corre ffmpeg -af volumedetect y devuelve (mean_dB, max_dB) o (None,None)."""
    if not path.exists():
        print(f"  [MISS] no existe: {path}")
        return None, None
    proc = subprocess.run(
        [_FFMPEG, "-hide_banner", "-i", str(path), "-af", "volumedetect", "-f", "null", "-"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    out = (proc.stderr or "") + (proc.stdout or "")
    m_mean = _MEAN_RE.search(out)
    m_max = _MAX_RE.search(out)
    mean = float(m_mean.group(1)) if m_mean else None
    mx = float(m_max.group(1)) if m_max else None
    if mean is None or mx is None:
        print(f"  [WARN] ffmpeg no devolvió mean/max para {path.name}")
    return mean, mx


def _avg_others(rows: list[dict], key: str, exclude: str) -> float | None:
    vals = [r[key] for r in rows if r["cap"] != exclude and r[key] is not None]
    return (sum(vals) / len(vals)) if vals else None


def main() -> int:
    if _FFMPEG is None:
        print("[FAIL] ffmpeg no está en PATH.")
        return 1
    if not MUSIC_MAP.exists():
        print(f"[FAIL] no se encontró music_map.json en {MUSIC_MAP}")
        return 1

    mmap = json.loads(MUSIC_MAP.read_text(encoding="utf-8"))
    tracks = mmap.get("tracks_by_chapter", {})
    print(f"music_map: {MUSIC_MAP}")
    print(f"ffmpeg:    {_FFMPEG}\n")

    rows: list[dict] = []
    for cid in CAPS:
        narr_path = AUDIO_DIR / f"{cid}.mp3"
        tinfo = tracks.get(cid, {})
        track_id = tinfo.get("track_id", "?")
        mp3_rel = tinfo.get("mp3_path")
        music_path = (BASE_DIR / mp3_rel) if mp3_rel else None

        print(f"midiendo {cid} ...")
        n_mean, n_max = _volumedetect(narr_path)
        if music_path is None:
            print(f"  [MISS] {cid} sin mp3_path en music_map")
            m_mean, m_max = None, None
        else:
            m_mean, m_max = _volumedetect(music_path)

        rows.append({
            "cap": cid, "track": track_id,
            "narr_mean": n_mean, "narr_max": n_max,
            "mus_mean": m_mean, "mus_max": m_max,
        })

    # ── Tabla ──
    def fmt(v):
        return f"{v:>7.1f}" if v is not None else "   N/A "

    print("\n" + "=" * 78)
    print(f"  {'cap':5} {'narr_mean':>9} {'narr_max':>9}  {'music_track':22} {'mus_mean':>8} {'mus_max':>8}")
    print("=" * 78)
    for r in rows:
        mark = "  ← ch04" if r["cap"] == "ch04" else ""
        print(f"  {r['cap']:5} {fmt(r['narr_mean'])}dB {fmt(r['narr_max'])}dB  "
              f"{r['track']:22} {fmt(r['mus_mean'])}dB {fmt(r['mus_max'])}dB{mark}")

    # ── Deltas de ch04 vs promedio de los otros ──
    ch04 = next((r for r in rows if r["cap"] == "ch04"), None)
    print("\n" + "-" * 78)
    if ch04 and ch04["narr_mean"] is not None:
        avg_n = _avg_others(rows, "narr_mean", "ch04")
        if avg_n is not None:
            d = ch04["narr_mean"] - avg_n
            print(f"  Δ narr_mean(ch04) − prom(otros) = {ch04['narr_mean']:.1f} − {avg_n:.1f} "
                  f"= {d:+.1f} dB   (más NEGATIVO ⇒ voz de ch04 más BAJA ⇒ hipótesis 1)")
    else:
        print("  Δ narr_mean: no calculable (falta dato de ch04)")
    if ch04 and ch04["mus_mean"] is not None:
        avg_m = _avg_others(rows, "mus_mean", "ch04")
        if avg_m is not None:
            d = ch04["mus_mean"] - avg_m
            print(f"  Δ mus_mean(ch04)  − prom(otros) = {ch04['mus_mean']:.1f} − {avg_m:.1f} "
                  f"= {d:+.1f} dB   (más ALTO ⇒ música de ch04 más FUERTE ⇒ hipótesis 2)")
    else:
        print("  Δ mus_mean: no calculable (falta dato de ch04)")

    print(f"\n  ch04 track efectivo: {ch04['track'] if ch04 else '?'}")
    incomplete = [r["cap"] for r in rows
                  if None in (r["narr_mean"], r["narr_max"], r["mus_mean"], r["mus_max"])]
    if incomplete:
        print(f"  ⚠ caps con alguna medición faltante: {incomplete}")
        return 1
    print("  ✓ 7/7 caps medidos (narración + música) — tabla completa")
    return 0


if __name__ == "__main__":
    sys.exit(main())
