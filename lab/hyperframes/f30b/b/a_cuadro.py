"""F30b §B.3: 3 bloques medidos a cuadro en los segmentos de v4 y v5 (el primer cuadro en que cambia la zona del bloque,
buscando desde 0.1 s antes del t del plan, así un corte de escena anterior no cuenta)."""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[4]
WD = ROOT / "output" / "f8s3-vajont-f30" / "_fase2b_work"
FPS = 30
CASOS = [("ch06", "ficha D128", 124.3, (0.06, 0.24, 0.60, 0.46)), ("ch07", "ficha D32", 112.5, (0.06, 0.24, 0.80, 0.46)),
         ("ch06", "sello «fisura»", 22.42, (0.55, 0.38, 0.97, 0.56))]


def aparece(seg: Path, t: float, box) -> float | None:
    a = t - 0.1
    r = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{a:.4f}", "-i", str(seg), "-frames:v", "30", "-vf",
                        "scale=256:144,format=gray", "-f", "rawvideo", "-"], capture_output=True, check=True)
    fr = np.frombuffer(r.stdout, np.uint8).reshape(-1, 144, 256).astype(float)
    x0, y0, x1, y1 = int(box[0] * 256), int(box[1] * 144), int(box[2] * 256), int(box[3] * 144)
    d = np.abs(fr[1:, y0:y1, x0:x1] - fr[0, y0:y1, x0:x1]).mean(axis=(1, 2))
    k = np.argmax(d > 2.0) if (d > 2.0).any() else None
    return None if k is None else round(a + (int(k) + 1) / FPS, 3)


out = []
for cap, nombre, t4, box in CASOS:
    i = int(cap[2:])
    a4 = aparece(WD / "_bak_v4" / f"seg_{i:02d}_{cap}.mp4", t4, box)
    a5 = aparece(WD / f"seg_{i:02d}_{cap}.mp4", t4 + 3.0, box)
    out.append({"cap": cap, "bloque": nombre, "t_plan_v4": t4, "t_plan_v5": t4 + 3.0, "aparece_v4": a4, "aparece_v5": a5,
                "delta_cuadros": round((a5 - a4) * FPS) if a4 is not None and a5 is not None else None})
(Path(__file__).with_name("a_cuadro.json")).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
sys.stdout.reconfigure(encoding="utf-8")
print(json.dumps(out, ensure_ascii=False, indent=1))
