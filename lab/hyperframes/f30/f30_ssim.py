"""F30 — SSIM cuadro a cuadro entre el chNN_gfx.mp4 de v3 y el de una corrida nueva (ffmpeg ssim), por escena y en
ventanas de ±1 s alrededor de cortes, y la hoja de contactos de escenas elegidas (inicio / mitad / fin, v3 | nuevo).

    python -I lab/hyperframes/f30/f30_ssim.py escenas <cap> <etiqueta> <idx,idx,idx>
    python -I lab/hyperframes/f30/f30_ssim.py cortes  <cap> <etiqueta> <idx,idx,...>
Escenas: las de v3 (snapped) del proyecto disperso de v3 cuando fue 1 ventana (ch02–ch06), o del log.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LAB = Path(__file__).resolve().parent
V3 = ROOT / "output" / "f8s3-vajont-f29" / "_fase2b_work"
FPS = 30


def escenas(cap: str) -> list[tuple[float, float]]:
    idx = V3 / f"gfx_{cap}_sparse" / "index.html"
    log = (V3 / f"gfx_{cap}.log").read_text(encoding="utf-8")
    m = list(re.finditer(r"sparse: (\d+) ventanas", log))
    if idx.exists() and m and m[-1].group(1) == "1":
        h = idx.read_text(encoding="utf-8")
        return [(float(a), float(a) + float(d)) for a, d in
                re.findall(r'class="scene clip"[^>]*data-start="([\d.]+)" data-duration="([\d.]+)"', h)]
    line = [l for l in log.splitlines() if "escenas:" in l][-1]
    st = [float(x) for x in re.findall(r"(\d+\.\d+)R\d", line)]
    dur = float(re.findall(r"sparse: \d+ ventanas, [\d.]+s de ([\d.]+)s", log)[-1])
    return list(zip(st, st[1:] + [dur]))


def ssim_por_cuadro(a: Path, b: Path, out: Path) -> list[float]:
    st = out.with_suffix(".ssim.txt")
    sf = st.as_posix().replace(":", "\\:")
    subprocess.run(["ffmpeg", "-v", "error", "-i", str(a), "-i", str(b), "-lavfi",
                    f"[0:v][1:v]ssim=stats_file='{sf}'", "-f", "null", "-"], check=True, capture_output=True)
    v = [float(x) for x in re.findall(r"All:([\d.]+)", st.read_text())]
    st.unlink()
    return v


def resumen(v: list[float], a: float, b: float) -> dict:
    k0, k1 = round(a * FPS), min(len(v), round(b * FPS))
    x = v[k0:k1]
    return {"t0": round(a, 3), "t1": round(b, 3), "cuadros": len(x), "ssim_media": round(sum(x) / len(x), 4) if x else None,
            "ssim_min": round(min(x), 4) if x else None}


def hoja(cap: str, nuevo: Path, elegidas: list[tuple[int, float, float]], dst: Path) -> None:
    from PIL import Image, ImageDraw
    filas = []
    for i, a, b in elegidas:
        for t in (a + 0.2, (a + b) / 2, b - 0.2):
            pair = []
            for src in (V3 / f"{cap}_gfx.mp4", nuevo):
                f = dst.parent / f"_f_{i}_{t:.2f}_{src.parent.name}.jpg"
                subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", str(src), "-frames:v", "1",
                                "-vf", "scale=640:-2", str(f)], check=True)
                pair.append(Image.open(f).convert("RGB"))
                f.unlink()
            filas.append((i, t, pair))
    w, h = filas[0][2][0].size
    sheet = Image.new("RGB", (2 * w + 24, len(filas) * (h + 30) + 8), (18, 18, 18))
    d = ImageDraw.Draw(sheet)
    for k, (i, t, (p3, pn)) in enumerate(filas):
        y = 8 + k * (h + 30)
        sheet.paste(p3, (8, y + 22))
        sheet.paste(pn, (16 + w, y + 22))
        d.text((8, y + 4), f"{cap} escena {i} · t {t:.2f}s · v3 (HF)", fill=(240, 232, 210))
        d.text((16 + w, y + 4), f"nuevo ({nuevo.parent.name})", fill=(240, 232, 210))
    sheet.save(dst, quality=88)


def main() -> None:
    modo, cap, etq = sys.argv[1], sys.argv[2], sys.argv[3]
    ids = [int(x) for x in sys.argv[4].split(",")] if len(sys.argv) > 4 else []
    nuevo = LAB / "corridas" / etq / f"{cap}_gfx.mp4"
    out = LAB / "corridas" / etq / f"ssim_{cap}_{modo}.json"
    v = ssim_por_cuadro(V3 / f"{cap}_gfx.mp4", nuevo, out)
    sc = escenas(cap)
    res: dict = {"cap": cap, "etiqueta": etq, "cuadros": len(v), "ssim_media_cap": round(sum(v) / len(v), 4),
                 "ssim_min_cap": round(min(v), 4)}
    if modo == "escenas":
        res["por_escena"] = {i: resumen(v, a, b) for i, (a, b) in enumerate(sc)}
        res["elegidas"] = ids
        resto = [x for k, x in enumerate(v) if not any(round(sc[i][0] * FPS) <= k < round(sc[i][1] * FPS) for i in ids)]
        res["resto"] = {"cuadros": len(resto), "ssim_media": round(sum(resto) / len(resto), 4), "ssim_min": round(min(resto), 4)}
        hoja(cap, nuevo, [(i, *sc[i]) for i in ids], LAB / "corridas" / etq / f"hoja_safe_{cap}.jpg")
    else:
        res["cortes"] = {i: resumen(v, sc[i][0] - 1.0, sc[i][0] + 1.0) for i in ids}
    out.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: res[k] for k in res if k != "por_escena"}, ensure_ascii=False), flush=True)
    if "por_escena" in res:
        for i, r in res["por_escena"].items():
            print(i, r, flush=True)


if __name__ == "__main__":
    main()
