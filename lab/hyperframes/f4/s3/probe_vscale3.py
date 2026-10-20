import subprocess, sys, shutil
from pathlib import Path
import numpy as np
R = Path(r"C:\CLAUDE_PROJECTS\automatization_videos"); sys.path.insert(0, str(R))
from script_engine import gfx_layer
from script_engine.gfx_project import GfxScene, write_project
OUT = Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)
W, H, FPS = 1280, 720, 30
base = OUT / "base.mp4"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"testsrc2=s={W}x{H}:r={FPS}:d=4",
                "-c:v", "libx264", "-g", "30", "-pix_fmt", "yuv420p", str(base)], check=True)
def frame(mp4, t):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t}", "-i", str(mp4), "-frames:v", "1", "-f", "rawvideo",
                          "-pix_fmt", "gray", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(H, W).astype(np.float32)
proj = OUT / "multi"; (proj / "public").mkdir(parents=True, exist_ok=True); shutil.copy2(base, proj / "public" / "base.mp4")
plan = {"chapter_number": 9, "transitions": {"1": {"kind": "cut", "frames": 0, "rank": "R3"}}}
write_project(plan, [GfxScene(0, 0.0, 2.0), GfxScene(1, 2.0, 4.0)], proj, duration=4.0, width=W, height=H, fps=FPS, grade=False)
sc = proj / "compositions" / "scene_02.html"; s = sc.read_text(encoding="utf-8")
s = s.replace('var tl = gsap.timeline({ paused: true });', 'var tl = gsap.timeline({ paused: true });\n        tl.to("#vw02", { scale: 1.5, duration: 0.4 }, 0.2);')
sc.write_text(s, encoding="utf-8")
out = proj / "out.mp4"; gfx_layer._render(proj, out, "looks")
ref, f = frame(base, 3.0), frame(out, 3.0)
ys, xs = np.mgrid[0:H, 0:W]
sc_ = ref[((ys - H/2)/1.5 + H/2).astype(int).clip(0, H-1), ((xs - W/2)/1.5 + W/2).astype(int).clip(0, W-1)]
print(f"multi escena 2: dif sin escala {np.abs(f-ref).mean():.1f} · dif escalado {np.abs(f-sc_).mean():.1f}")
