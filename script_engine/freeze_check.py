"""
script_engine/freeze_check.py — F10 B1: validador post-render de cuadro congelado.

Corre `freezedetect` de FFmpeg sobre un cap (o el final) y devuelve los tramos quietos de más de `min_sec`. Los
tramos que son quietos A PROPÓSITO (pausa de la pregunta de cierre, corte a negro, foto fija con movimiento nulo) se
pasan en `allow` y no cuentan. Uso: después del render de fase2b, sobre cada `_fase2b_work/chNN_gfx.mp4`.
    python -I -m script_engine.freeze_check <mp4> [<mp4> …]
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

NOISE = 0.002          # diferencia mínima entre cuadros (freezedetect n)
MIN_SEC = 1.5          # una foto con DepthFlow/Ken Burns nunca queda quieta 1.5 s


def freezes(path: Path, *, noise: float = NOISE, min_sec: float = MIN_SEC) -> list[tuple[float, float]]:
    """[(inicio, duración)] de los tramos quietos de `path`."""
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(path), "-map", "0:v", "-vf",
                        f"freezedetect=n={noise}:d={min_sec}", "-f", "null", "-"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    starts = [float(x) for x in re.findall(r"freeze_start: ([\d.]+)", r.stderr)]
    durs = [float(x) for x in re.findall(r"freeze_duration: ([\d.]+)", r.stderr)]
    out = list(zip(starts, durs))
    if len(starts) > len(durs):                              # quieto hasta el final del archivo
        out.append((starts[-1], float("inf")))
    return out


def check(path: Path, allow: list[tuple[float, float]] | None = None, **kw) -> dict:
    """{"archivo", "congelados": [(t, dur)], "ok"}: un congelado cuenta si no cae entero dentro de un tramo `allow`."""
    allow = allow or []
    bad = [(round(t, 2), round(d, 2)) for t, d in freezes(path, **kw)
           if not any(a - 0.1 <= t and t + (d if d != float("inf") else 0) <= b + 0.1 for a, b in allow)]
    return {"archivo": str(path), "congelados": bad, "ok": not bad}


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps([check(Path(p)) for p in sys.argv[1:]], ensure_ascii=False, indent=1))
