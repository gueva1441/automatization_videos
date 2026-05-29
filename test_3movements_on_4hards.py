"""
test_3movements_on_4hards.py
Confirma si horizontal + vertical + orbital aguantan en las otras 4 imágenes
"malas" según el ojo del usuario (img_01, 02, 08, 11).
"""
import json
import subprocess
import sys
from pathlib import Path

ASSETS_DIR = Path(
    r"C:\CLAUDE_PROJECTS\automatization_videos\output"
    r"\7b52de57-eee6-4018-ac25-8357e9779d92\assets"
)
OUTPUT_BASE = Path(r"C:\CLAUDE_PROJECTS\automatization_videos\test_3movs_on_4hards")
PYTHON_DEPTHFLOW = Path(
    r"C:\CLAUDE_PROJECTS\viral-video-pipeline\.venv-depthflow\Scripts\python.exe"
)

DURATION = 6.0
WIDTH = 1080
HEIGHT = 1920
FPS = 30
SSAA = 1.5
INTENSITY = 1.0
STATE_HEIGHT = 0.05

IMAGES = [
    "ch03_img_01.png",
    "ch03_img_02.png",
    "ch03_img_08.png",
    "ch03_img_11.png",
]

MOVEMENTS = [
    {
        "name": "horizontal",
        "movement": "horizontal",
        "mv_kwargs": {"intensity": INTENSITY, "reverse": False, "smooth": True,
                      "loop": True, "phase": 0.0, "steady": 0.3, "isometric": 0.6},
    },
    {
        "name": "vertical",
        "movement": "vertical",
        "mv_kwargs": {"intensity": INTENSITY, "smooth": True, "loop": True,
                      "phase": 0.0, "steady": 0.3, "isometric": 0.6},
    },
    {
        "name": "orbital",
        "movement": "orbital",
        "mv_kwargs": {"intensity": INTENSITY, "smooth": True, "loop": True,
                      "phase": 0.0, "depth": 0.5},
    },
]


RUNNER_CODE = r"""
import os, json, sys
os.environ.setdefault("TORCH_DEVICE", "cuda")
os.environ.setdefault("CUDA_VISIBLE_DEVICES", "0")

from depthflow.scene import DepthScene

params = json.loads(sys.argv[1])

scene = DepthScene(backend="headless")
scene.input(image=params["image_path"])

scene.state.height = params["state_height"]
scene.state.mirror = False

method = getattr(scene, params["movement"])
method(**params["mv_kwargs"])

scene.main(
    output=params["output_path"],
    render=True,
    width=params["width"],
    height=params["height"],
    fps=params["fps"],
    ssaa=params["ssaa"],
    time=params["duration"],
    ratio="9:16",
)
print("OK")
"""


def run_movement(image_path: Path, mv: dict, output_path: Path) -> bool:
    params = {
        "image_path":   str(image_path),
        "output_path":  str(output_path),
        "movement":     mv["movement"],
        "mv_kwargs":    mv["mv_kwargs"],
        "state_height": STATE_HEIGHT,
        "width":        WIDTH,
        "height":       HEIGHT,
        "fps":          FPS,
        "ssaa":         SSAA,
        "duration":     DURATION,
    }
    cmd = [str(PYTHON_DEPTHFLOW), "-c", RUNNER_CODE, json.dumps(params)]
    try:
        result = subprocess.run(cmd, capture_output=True, timeout=180)
    except subprocess.TimeoutExpired:
        print(f"      ❌ {mv['name']} TIMEOUT")
        return False
    if result.returncode != 0:
        stderr = (result.stderr or b"").decode("utf-8", errors="replace")
        print(f"      ❌ {mv['name']} FAIL")
        print(f"      stderr: {stderr[-300:]}")
        return False
    size_kb = output_path.stat().st_size // 1024
    print(f"      ✅ {mv['name']:11s} ({size_kb} KB)")
    return True


def main() -> int:
    OUTPUT_BASE.mkdir(parents=True, exist_ok=True)

    print("=" * 72)
    print(f"  Test: {len(MOVEMENTS)} movimientos × {len(IMAGES)} imágenes = {len(MOVEMENTS)*len(IMAGES)} videos")
    print("=" * 72)

    failed = []
    for i, img_name in enumerate(IMAGES, 1):
        img_path = ASSETS_DIR / img_name
        if not img_path.exists():
            print(f"[{i}/{len(IMAGES)}] ❌ No existe: {img_path}")
            continue
        folder = OUTPUT_BASE / img_path.stem
        folder.mkdir(exist_ok=True)
        print(f"\n[{i}/{len(IMAGES)}] {img_name}")

        for mv in MOVEMENTS:
            out_mp4 = folder / f"{mv['name']}.mp4"
            if not run_movement(img_path, mv, out_mp4):
                failed.append(f"{img_name}/{mv['name']}")

    print()
    print("=" * 72)
    if failed:
        print(f"  ⚠ Fallaron: {', '.join(failed)}")
    print(f"  Output: {OUTPUT_BASE}")
    print("=" * 72)
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())