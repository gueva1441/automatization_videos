"""F30 §C.3 — costura entre caps, SOLO medir (no se arregla en esta tanda: F30b).

En cada archivo de la cadena (chNN_gfx.mp4 → seg_NN_chNN.mp4 → _concat_video.ts → mp4 final) busca los cuadros
«planos» (desvío de luma < 6): gris ≈ 50 % (luma media 100–156) y blanco (≥ 200), con su tiempo y, en los segmentos,
si caen en los 6 cuadros del borde. Dice en qué archivo aparece por primera vez cada cosa.
    python -I lab/hyperframes/f30/f30_costura.py <topic> [<mp4 final>]
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
LAB = Path(__file__).resolve().parent
FPS, W, H = 30, 64, 36


def planos(video: Path) -> tuple[list[dict], int]:
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", str(video), "-vf", f"fps={FPS},scale={W}:{H},format=gray",
                        "-f", "rawvideo", "-"], capture_output=True, timeout=3600)
    fr = np.frombuffer(r.stdout, np.uint8).reshape(-1, H, W).astype(np.float32)
    mu, sd = fr.mean(axis=(1, 2)), fr.std(axis=(1, 2))
    out = []
    for k in np.where(sd < 6.0)[0]:
        tipo = "blanco" if mu[k] >= 200 else ("gris" if 100 <= mu[k] <= 156 else ("negro" if mu[k] < 30 else None))
        if tipo in ("gris", "blanco"):
            out.append({"cuadro": int(k), "t": round(k / FPS, 3), "tipo": tipo, "luma": round(float(mu[k]), 1),
                        "desvio": round(float(sd[k]), 2)})
    return out, len(fr)


def main() -> None:
    topic = sys.argv[1]
    final = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    wd = ROOT / "output" / topic / "_fase2b_work"
    res: dict = {"topic": topic, "archivos": {}}
    for f in sorted(wd.glob("ch0*_gfx.mp4")) + sorted(wd.glob("seg_*_ch*.mp4")) + [wd / "_concat_video.ts"] + \
            ([final] if final else []):
        if not f.exists():
            continue
        p, n = planos(f)
        borde = [x for x in p if x["cuadro"] < 6 or x["cuadro"] >= n - 6]
        res["archivos"][f.name] = {"cuadros": n, "planos": p, "en_los_6_del_borde": borde}
        print(f"{f.name}: {n} cuadros · gris {sum(x['tipo'] == 'gris' for x in p)} · blanco "
              f"{sum(x['tipo'] == 'blanco' for x in p)} · en el borde {[(x['cuadro'], x['tipo']) for x in borde]}",
              flush=True)
    primero: dict = {}
    for name, d in res["archivos"].items():
        for x in d["planos"]:
            primero.setdefault(x["tipo"], name)
    res["primera_aparicion"] = primero
    (LAB / "c").mkdir(exist_ok=True)
    (LAB / "c" / f"costura_{topic}.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print("primera aparición:", primero, flush=True)


if __name__ == "__main__":
    main()
