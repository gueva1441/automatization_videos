# -*- coding: utf-8 -*-
"""F52 etapa 3 — hoja ciega: por cap, un mp4 2×2 lado a lado (sin audio) con los 4 clips etiquetados 1–4 en orden
aleatorio, y una hoja de contactos (filas = 1–4, columnas = cuadros a 0, 2, 4, 6 y 8 s). La llave número → modelo va
aparte en `LLAVE.md`. El orden sale de `secrets` (no reproducible a propósito: es ciego) y queda solo en la llave.
Un clip que no salió (rechazo o error) ocupa su casillero en negro con «sin clip».

Salida: `hoja_ciega/cap01_2x2.mp4`, `cap07_2x2.mp4`, `cap01_contactos.png`, `cap07_contactos.png` y `LLAVE.md`.
Uso: python lab/hyperframes/f52/hoja_ciega.py
"""
import json
import secrets
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

F52 = Path(__file__).resolve().parent
CLIPS, SALIDA = F52 / "clips", F52 / "hoja_ciega"
MODELOS = {"K": "Kling 4.0", "S": "Seedance 2.5", "F": "FLUX 3 Max", "G": "Gemini Omni Flash 1.1"}
FUENTE = "C\\:/Windows/Fonts/arial.ttf"
W, H, DUR, FPS = 960, 540, 8, 24
TIEMPOS = (0, 2, 4, 6, 8)


def ff(*args) -> None:
    r = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *map(str, args)],
                       capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(r.stderr[-800:])


def duracion(p: Path) -> float:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                       capture_output=True, text=True)
    return float(r.stdout.strip() or 0)


def etiqueta(txt: str, tam: int = 64) -> str:
    return (f"drawtext=fontfile='{FUENTE}':text='{txt}':x=24:y=18:fontsize={tam}:fontcolor=white:"
            f"box=1:boxcolor=black@0.6:boxborderw=12")


def panel(src: Path | None, num: int, dst: Path) -> None:
    """Un casillero 960×540, 8 s a 24 fps, sin audio, con su número."""
    if src is None:
        ff("-f", "lavfi", "-i", f"color=c=black:s={W}x{H}:d={DUR}:r={FPS}",
           "-vf", f"{etiqueta(str(num))},{etiqueta('sin clip', 48).replace('x=24:y=18', 'x=(w-tw)/2:y=(h-th)/2')}",
           "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p", dst)
        return
    ff("-i", src, "-vf",
       f"fps={FPS},scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,"
       f"tpad=stop_mode=clone:stop_duration={DUR},trim=duration={DUR},setpts=PTS-STARTPTS,{etiqueta(str(num))}",
       "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p", dst)


def main() -> int:
    SALIDA.mkdir(exist_ok=True)
    llave = ["# LLAVE — hoja ciega de F52 (número → modelo)", "",
             "**No abrir antes de elegir.** El orden se sorteó con `secrets` al armar la hoja; solo queda acá.", ""]
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        for n in (1, 7):
            letras = list(MODELOS)
            orden = [letras.pop(secrets.randbelow(len(letras))) for _ in range(len(MODELOS))]   # orden[i] = número i+1
            llave += [f"## Cap {n}", "", "| número | modelo | clip |", "|---|---|---|"]
            paneles = []
            for i, k in enumerate(orden, start=1):
                src = CLIPS / f"cap{n:02d}_{k}.mp4"
                src = src if src.exists() else None
                llave += [f"| {i} | {k} — {MODELOS[k]} | {src.name if src else 'sin clip'} |"]
                p = tmp / f"c{n}_{i}.mp4"
                panel(src, i, p)
                paneles.append(p)
            llave += [""]
            ff(*sum((["-i", p] for p in paneles), []), "-filter_complex",
               "[0:v][1:v]hstack=inputs=2[a];[2:v][3:v]hstack=inputs=2[b];[a][b]vstack=inputs=2[v]",
               "-map", "[v]", "-an", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
               SALIDA / f"cap{n:02d}_2x2.mp4")
            # hoja de contactos: fila = número, columna = segundo
            idx = 0
            for i, p in enumerate(paneles, start=1):
                for t in TIEMPOS:
                    idx += 1
                    ts = min(t, DUR - 1 / FPS)
                    ff("-ss", f"{ts:.3f}", "-i", p, "-frames:v", "1", "-vf",
                       f"scale=480:270,{etiqueta(f'{i} · {t} s', 28)}", tmp / f"k{n}_{idx:03d}.png")
            ff("-framerate", "1", "-i", tmp / f"k{n}_%03d.png", "-vf", f"tile={len(TIEMPOS)}x{len(paneles)}",
               "-frames:v", "1", SALIDA / f"cap{n:02d}_contactos.png")
    (F52 / "LLAVE.md").write_text("\n".join(llave) + "\n", encoding="utf-8")
    print("hoja ciega lista:", ", ".join(sorted(x.name for x in SALIDA.iterdir())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
