"""
diag_musica_lufs_banda_chat39.py — MEDICIÓN descartable chat 39. NO toca nada.

Por cada mp3 de audio_library/ mide:
  A) LUFS integrado (loudnorm print_format=json → input_i) — outlier de nivel.
  B) mean_volume full-band y en banda de voz 1–4 kHz (highpass1000+lowpass4000)
     + delta = full − banda (delta chico = más energía en la banda de la voz).
Marca cuál track usa ch04 (desde music_map.json del topic Tuskegee).

LECTURA PURA: ffmpeg en modo análisis (-f null -). No escribe ni mueve nada.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

LIB = Path("audio_library")
TOPIC = "8286b193-ff82-4357-b32d-21ca30909c4d"
MUSIC_MAP = Path(f"output/audio/{TOPIC}/music_map.json")


def _ff(mp3: Path, af: str) -> str:
    r = subprocess.run(
        ["ffmpeg", "-hide_banner", "-nostats", "-i", str(mp3),
         "-af", af, "-f", "null", "-"],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120,
    )
    return (r.stderr or "") + (r.stdout or "")


def lufs(mp3: Path) -> float | None:
    out = _ff(mp3, "loudnorm=print_format=json")
    m = re.search(r'\{[^{}]*"input_i"[^{}]*\}', out, re.S)
    if not m:
        return None
    try:
        return float(json.loads(m.group(0))["input_i"])
    except (ValueError, KeyError, json.JSONDecodeError):
        return None


def mean_vol(mp3: Path, af: str) -> float | None:
    m = re.search(r"mean_volume:\s*(-?[\d.]+) dB", _ff(mp3, af))
    return float(m.group(1)) if m else None


def main() -> int:
    if not LIB.exists():
        print(f"[FAIL] no existe {LIB}")
        return 1

    ch04_track = None
    if MUSIC_MAP.exists():
        mm = json.loads(MUSIC_MAP.read_text(encoding="utf-8"))
        p = mm.get("tracks_by_chapter", {}).get("ch04", {}).get("mp3_path")
        if p:
            ch04_track = Path(p).name
    print(f"music_map: {MUSIC_MAP}  (existe={MUSIC_MAP.exists()})")
    print(f"ch04 track: {ch04_track}\n")

    rows = []
    for mp3 in sorted(LIB.glob("*.mp3")):
        print(f"midiendo {mp3.name} ...")
        li = lufs(mp3)
        full = mean_vol(mp3, "volumedetect")
        band = mean_vol(mp3, "highpass=f=1000,lowpass=f=4000,volumedetect")
        delta = (full - band) if (full is not None and band is not None) else None
        rows.append({"name": mp3.name, "lufs": li, "full": full,
                     "band": band, "delta": delta, "is04": mp3.name == ch04_track})

    def f(x):
        return f"{x:>9.1f}" if x is not None else f"{'?':>9}"

    print(f"\n{'track':28} {'LUFS_int':>9} {'mean_full':>10} {'mean_1-4k':>10} {'delta':>7}  ch04")
    print("-" * 80)
    for r in rows:
        mark = "<== CH04" if r["is04"] else ""
        print(f"{r['name']:28} {f(r['lufs'])} {f(r['full'])} {f(r['band'])} {f(r['delta'])}  {mark}")

    # ── Comparativa ch04 vs los otros (solo datos, sin proponer fix) ──
    ch04 = next((r for r in rows if r["is04"]), None)
    others = [r for r in rows if not r["is04"]]

    def _median(vals):
        vals = sorted(v for v in vals if v is not None)
        if not vals:
            return None
        n = len(vals)
        return vals[n // 2] if n % 2 else (vals[n // 2 - 1] + vals[n // 2]) / 2

    print("\n" + "-" * 80)
    if ch04:
        med_lufs = _median([r["lufs"] for r in others])
        med_band = _median([r["band"] for r in others])
        med_delta = _median([r["delta"] for r in others])
        if ch04["lufs"] is not None and med_lufs is not None:
            print(f"  LUFS_int:  ch04={ch04['lufs']:.1f}  mediana(otros)={med_lufs:.1f}  "
                  f"Δ={ch04['lufs'] - med_lufs:+.1f} LU")
        # ranking de mean_1-4k (mayor = más energía en banda de voz)
        ranked = sorted((r for r in rows if r["band"] is not None),
                        key=lambda r: r["band"], reverse=True)
        pos = next((i + 1 for i, r in enumerate(ranked) if r["is04"]), None)
        if pos:
            print(f"  mean_1-4k: ch04={ch04['band']:.1f} dB → puesto {pos}/{len(ranked)} "
                  f"(1 = más energía en banda de voz)")
        if ch04["delta"] is not None and med_delta is not None:
            print(f"  delta_banda: ch04={ch04['delta']:.1f}  mediana(otros)={med_delta:.1f}  "
                  f"(delta más chico = más concentrada en la voz)")

    incompletos = [r["name"] for r in rows
                   if None in (r["lufs"], r["full"], r["band"])]
    if incompletos:
        print(f"\n  ⚠ mp3 con alguna medición faltante: {incompletos}")
        return 1
    print(f"\n  ✓ {len(rows)} tracks medidos (LUFS + full + banda)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
