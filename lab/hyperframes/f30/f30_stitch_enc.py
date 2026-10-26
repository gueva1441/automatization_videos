"""F30 §C.2 — el stitch + grade de ch06 con libx264 ultrafast crf 16 contra NVENC cq 23 (mismas entradas, mismas
ventanas y transiciones que la corrida de ch06 en f8s3-vajont-f30; solo cambia el encoder del intermedio).
Uso: python -I lab/hyperframes/f30/f30_stitch_enc.py"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
LAB = Path(__file__).resolve().parent
WD = ROOT / "output" / "f8s3-vajont-f30" / "_fase2b_work"
V3 = ROOT / "output" / "f8s3-vajont-f29" / "_fase2b_work"


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    from gfx_config import gfx_render, gfx_rules
    from script_engine import gfx_sparse as sp
    from script_engine.gfx_project import GfxScene
    h = (V3 / "gfx_ch06_sparse" / "index.html").read_text(encoding="utf-8")
    sc = [GfxScene(i, float(a), round(float(a) + float(d), 3), "R3") for i, (a, d) in
          enumerate(re.findall(r'class="scene clip"[^>]*data-start="([\d.]+)" data-duration="([\d.]+)"', h))]
    plan = json.loads((WD / "gfx_plan_ch06.resolved.json").read_text(encoding="utf-8"))["plan"]
    sj = json.loads((WD / "gfx_sparse_ch06.json").read_text(encoding="utf-8"))
    dur = sj["duracion"]
    win = [tuple(w) for w in sj["ventanas"]]
    _, _, _, offs = sp.compose_sparse(plan, sc, win, 30)
    trs = sp.stitch_transitions(plan, sc, win)
    pub = WD / "gfx_ch06" / "public"
    res = {}
    for name, enc in (("x264", None), ("nvenc", list(gfx_render.stitch_nvenc))):
        out = LAB / "c" / f"_stitch_{name}.mp4"
        t0 = time.time()
        sp.stitch(pub / "base_cocido.mp4", WD / "gfx_ch06_sparse" / "renders" / "ch06_sparse.mp4", win, offs, dur, out,
                  width=2560, height=1440, fps=30, vignette=pub / "vignette.png", grain=pub / "grain.png",
                  grain_opacity=gfx_rules.grain_opacity, bug=None, transitions=trs, encoder=enc)
        res[name] = {"segundos": round(time.time() - t0, 1), "bytes": out.stat().st_size}
        print(name, res[name], flush=True)
    st = LAB / "c" / "_ssim.txt"
    subprocess.run(["ffmpeg", "-v", "error", "-i", str(LAB / "c" / "_stitch_nvenc.mp4"), "-i", str(LAB / "c" / "_stitch_x264.mp4"),
                    "-lavfi", f"ssim=stats_file='{st.as_posix().replace(':', chr(92) + ':')}'", "-f", "null", "-"], check=True)
    v = [float(x) for x in re.findall(r"All:([\d.]+)", st.read_text())]
    res["ssim_nvenc_vs_x264"] = {"media": round(sum(v) / len(v), 4), "min": round(min(v), 4)}
    st.unlink()
    for name in ("x264", "nvenc"):
        (LAB / "c" / f"_stitch_{name}.mp4").unlink()
    (LAB / "c" / "stitch_encoder.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(res, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
