"""F4d: recorte 1:1 (sin escalar) de la marca de la esquina, antes (F4c: 4× + lanczos, +2 px) y después (+1 px).

La comparación se hace sobre el MISMO cuadro sin marca (`_bak_f4c_pre/chNN_segment_only.mp4`), con los mismos filtros FFmpeg del cosido:
    antes    mismo código, corner_dilate_px 2 (F4c)
    después  corner_dilate_px 1 (perfil actual, F4d)
    render   el cuadro real del segmento F4d (`chNN_segment_only.f4d_gfx.mp4`), para confirmar que el render coincide
Uso: PYTHONIOENCODING=utf-8 python lab/hyperframes/f4d/recorte_marca.py ch02 52.0
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
W = ROOT / "output" / "ba6c3cac-a091-41c0-8dad-afd2f4364747" / "_fase2b_work"
OUT = Path(__file__).resolve().parent / "capturas"
BOX = (40, 20, 240, 220)                      # 200×200 alrededor de la marca (x 3 %, y 3.5 %, alto 6 % de 1440)
WID, HEI = 2560, 1440


def frame(video: Path, t: float, dst: Path) -> Path:
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", str(video), "-frames:v", "1", str(dst)], check=True)
    return dst


def burn(gb, still: Path, out: Path, png_dir: Path, dilate: int | None = None) -> Image.Image:
    cfg = gb.config()
    if dilate is not None:
        cfg = {**cfg, "corner_dilate_px": dilate}
    cb, cf = gb.pngs(cfg, int(HEI * cfg["height_frac"]), png_dir, corner=True)
    g, last = gb.overlay_graph(cfg, {}, 10.0, width=WID, height=HEI, in_body=1, in_flame=2, last="v0", intro=False)
    graph = ";".join(["[0:v]format=yuv420p[v0]", *g, f"[{last}]format=rgb24[o]"])
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-i", str(still), "-loop", "1", "-i", str(cb),
                    "-loop", "1", "-i", str(cf), "-filter_complex", graph, "-map", "[o]", "-frames:v", "1", str(out)],
                   check=True)
    return Image.open(out)


def main(cap: str, t: float) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        base = frame(W / "_bak_f4c_pre" / f"{cap}_segment_only.mp4", t, tmp / "base.png")
        from script_engine import gfx_bug as new
        a = burn(new, base, tmp / "antes.png", tmp / "png_old", dilate=2).crop(BOX)
        d = burn(new, base, tmp / "despues.png", tmp / "png_new").crop(BOX)
        r = Image.open(frame(W / f"{cap}_segment_only.f4d_gfx.mp4", t, tmp / "render.png")).convert("RGB").crop(BOX)
    a.save(OUT / f"marca_{cap}_antes_1x1.png")
    d.save(OUT / f"marca_{cap}_despues_1x1.png")
    r.save(OUT / f"marca_{cap}_render_f4d_1x1.png")
    pair = Image.new("RGB", (a.width * 2 + 10, a.height), (255, 255, 255))
    pair.paste(a, (0, 0))
    pair.paste(d, (a.width + 10, 0))
    pair.save(OUT / f"marca_{cap}_antes_despues_1x1.png")
    print(f"{cap} t={t}: antes = +2 px, después = +1 px → {OUT}")


if __name__ == "__main__":
    main(sys.argv[1], float(sys.argv[2]))
