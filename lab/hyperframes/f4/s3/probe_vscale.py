"""F4 §3: ¿qué transform escala el <video> en el render de HyperFrames? 3 variantes, 1 s cada una, 640x360."""
import subprocess
import sys
from pathlib import Path

import numpy as np

R = Path(r"C:\CLAUDE_PROJECTS\automatization_videos")
sys.path.insert(0, str(R))
from script_engine import gfx_layer  # noqa: E402
from script_engine.gfx_project import GfxScene, write_project  # noqa: E402

OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)
W, H, FPS = 640, 360, 30
base = OUT / "base.mp4"
if not base.exists():
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"testsrc2=s={W}x{H}:r={FPS}:d=2",
                    "-c:v", "libx264", "-g", "30", "-pix_fmt", "yuv420p", str(base)], check=True)

VARIANTS = {
    "A_wrapper": 'tl.set("#vw01", { scale: 1.5 }, 0.0);',
    "B_video": 'tl.set("#v01", { scale: 1.5 }, 0.0);',
    "C_both_wrapper_css": None,   # CSS fijo en el wrapper
}


def frame(mp4: Path, t: float) -> np.ndarray:
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t}", "-i", str(mp4), "-frames:v", "1", "-f", "rawvideo",
                          "-pix_fmt", "gray", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(H, W).astype(np.float32)


ref = frame(base, 1.0)
for name, js in VARIANTS.items():
    proj = OUT / name
    (proj / "public").mkdir(parents=True, exist_ok=True)
    import shutil
    shutil.copy2(base, proj / "public" / "base.mp4")
    write_project({"chapter_number": 9}, [GfxScene(0, 0.0, 2.0)], proj, duration=2.0, width=W, height=H, fps=FPS, grade=False)
    sc = proj / "compositions" / "scene_01.html"
    s = sc.read_text(encoding="utf-8")
    if js:
        s = s.replace('var tl = gsap.timeline({ paused: true });', 'var tl = gsap.timeline({ paused: true });\n        ' + js)
    else:
        s = s.replace('class="vwrap">', 'class="vwrap" style="transform: scale(1.5)">')
    sc.write_text(s, encoding="utf-8")
    out = proj / "out.mp4"
    try:
        gfx_layer._render(proj, out, "draft")
    except Exception as e:  # noqa: BLE001
        print(name, "render falló", e)
        continue
    f = frame(out, 1.0)
    # escala 1.5 desde el centro: comparar contra la referencia escalada
    ys, xs = np.mgrid[0:H, 0:W]
    sy = ((ys - H / 2) / 1.5 + H / 2).astype(int).clip(0, H - 1)
    sx = ((xs - W / 2) / 1.5 + W / 2).astype(int).clip(0, W - 1)
    scaled = ref[sy, sx]
    print(f"{name}: dif vs sin escala {np.abs(f - ref).mean():.1f} · dif vs escalado 1.5 {np.abs(f - scaled).mean():.1f}")
