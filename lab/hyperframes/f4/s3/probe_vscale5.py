import subprocess, sys, shutil
from pathlib import Path
import numpy as np
R = Path(r"C:\CLAUDE_PROJECTS\automatization_videos"); sys.path.insert(0, str(R))
from script_engine import gfx_layer, gfx_project
from script_engine.gfx_project import GfxScene, write_project
OUT = Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)
W, H, FPS = 2560, 1440, 30
SRC = R / "output/ba6c3cac-a091-41c0-8dad-afd2f4364747/_fase2b_work/ch05_flux_visual.mp4"
proj = OUT / "real_grade"; (proj / "public").mkdir(parents=True, exist_ok=True)
base = proj / "public" / "base.mp4"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "76.87", "-t", "7.33", "-i", str(SRC), "-an", "-c:v", "libx264", "-g", "30",
                "-pix_fmt", "yuv420p", "-r", "30", str(base)], check=True)
gfx_project._extract_freeze = lambda base, t, out: False          # sin cuadro congelado: ¿escala el <video>?
plan = {"chapter_number": 5, "evidence_zoom": {"scene_idx": 0, "box": [0.387, 0.463, 0.121, 0.064], "start": 4.48}}
write_project(plan, [GfxScene(0, 0.0, 7.33)], proj, duration=7.33, width=W, height=H, fps=FPS, grade=True)
assert "zoomfz" not in (proj / "compositions" / "scene_01.html").read_text(encoding="utf-8")
out = proj / "out.mp4"; gfx_layer._render(proj, out, "looks")
def frame(mp4, t):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t}", "-i", str(mp4), "-frames:v", "1", "-vf", "scale=640:360",
                          "-f", "rawvideo", "-pix_fmt", "gray", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(360, 640).astype(np.float32)
for t in (3.0, 7.0):
    print(t, "dif out vs base", round(float(np.abs(frame(out, t) - frame(base, t)).mean()), 1))
subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "7.0", "-i", str(out), "-frames:v", "1", "-vf", "scale=960:-1", str(OUT / "grade_t7.png")])
