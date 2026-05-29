"""
test_3movs_plus_effects.py
PARTE A: horizontal + vertical + orbital sobre las 4 imágenes "malas".
PARTE B: zoom_in sobre ch03_img_05 (explosión) con efectos post-process
         (vignette, lens, blur, blur+vignette) para ver si esconden los streaks.
"""
import json
import subprocess
import sys
from pathlib import Path

ASSETS_DIR = Path(
    r"C:\CLAUDE_PROJECTS\automatization_videos\output"
    r"\7b52de57-eee6-4018-ac25-8357e9779d92\assets"
)
OUTPUT_BASE = Path(r"C:\CLAUDE_PROJECTS\automatization_videos\test_3movs_plus_effects")
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

# ═══ PARTE A ═══
IMAGES_HARD = ["ch03_img_01.png", "ch03_img_02.png", "ch03_img_08.png", "ch03_img_11.png"]
MOVEMENTS_A = [
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

# ═══ PARTE B ═══
EXPLOSION_IMG = "ch03_img_05.png"
ZOOM_KWARGS = {"intensity": INTENSITY, "reverse": False, "smooth": True,
               "loop": False, "phase": 0.0, "isometric": 0.8}

EFFECTS_TESTS = [
    {
        "name": "zoom_in_baseline",
        "effects": {},  # sin efectos
    },
    {
        "name": "zoom_in_vignette",
        "effects": {
            "vignette": {"enable": True, "intensity": 0.6, "decay": 20.0},
        },
    },
    {
        "name": "zoom_in_lens",
        "effects": {
            "lens": {"enable": True, "intensity": 0.3, "decay": 0.4, "quality": 30},
        },
    },
    {
        "name": "zoom_in_blur_strong",
        "effects": {
            # blur depth-based: borrosea desde start (cerca) hasta end (lejos)
            "blur": {"enable": True, "intensity": 1.5, "start": 0.4,
                     "end": 1.0, "exponent": 2.0, "quality": 4, "directions": 16},
        },
    },
    {
        "name": "zoom_in_blur_plus_vignette",
        "effects": {
            "blur":     {"enable": True, "intensity": 1.5, "start": 0.4,
                         "end": 1.0, "exponent": 2.0, "quality": 4, "directions": 16},
            "vignette": {"enable": True, "intensity": 0.5, "decay": 20.0},
        },
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

# Aplicar efectos post-process si los hay
effects = params.get("effects", {})
for effect_name, effect_params in effects.items():
    target = getattr(scene.state, effect_name)
    for k, v in effect_params.items():
        setattr(target, k, v)
    print(f"[effect] {effect_name} = {effect_params}", file=sys.stderr)

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


def run_render(image_path: Path, movement: str, mv_kwargs: dict,
               effects: dict, output_path: Path, label: str) -> bool:
    params = {
        "image_path":   str(image_path),
        "output_path":  str(output_path),
        "movement":     movement,
        "mv_kwargs":    mv_kwargs,
        "effects":      effects,
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
        print(f"      ❌ {label} TIMEOUT")
        return False
    if result.returncode != 0:
        stderr = (result.stderr or b"").decode("utf-8", errors="replace")
        print(f"      ❌ {label} FAIL")
        print(f"      stderr: {stderr[-300:]}")
        return False
    size_kb = output_path.stat().st_size // 1024
    print(f"      ✅ {label:30s} ({size_kb} KB)")
    return True


def main() -> int:
    OUTPUT_BASE.mkdir(parents=True, exist_ok=True)
    failed = []

    # ═══ PARTE A: 3 movimientos × 4 imágenes ═══
    print("=" * 72)
    print(f"  PARTE A: horizontal + vertical + orbital × 4 imágenes ({len(MOVEMENTS_A)*len(IMAGES_HARD)} videos)")
    print("=" * 72)
    part_a_dir = OUTPUT_BASE / "A_movements"
    part_a_dir.mkdir(exist_ok=True)

    for i, img_name in enumerate(IMAGES_HARD, 1):
        img_path = ASSETS_DIR / img_name
        if not img_path.exists():
            print(f"[{i}/{len(IMAGES_HARD)}] ❌ No existe: {img_path}")
            continue
        folder = part_a_dir / img_path.stem
        folder.mkdir(exist_ok=True)
        print(f"\n[{i}/{len(IMAGES_HARD)}] {img_name}")
        for mv in MOVEMENTS_A:
            out = folder / f"{mv['name']}.mp4"
            if not run_render(img_path, mv["movement"], mv["mv_kwargs"], {}, out, mv["name"]):
                failed.append(f"A:{img_name}/{mv['name']}")

    # ═══ PARTE B: zoom_in + efectos sobre la explosión ═══
    print()
    print("=" * 72)
    print(f"  PARTE B: zoom_in + efectos sobre {EXPLOSION_IMG} ({len(EFFECTS_TESTS)} videos)")
    print("=" * 72)
    part_b_dir = OUTPUT_BASE / "B_effects_on_explosion"
    part_b_dir.mkdir(exist_ok=True)
    img_path = ASSETS_DIR / EXPLOSION_IMG
    if not img_path.exists():
        print(f"❌ No existe: {img_path}")
    else:
        for test in EFFECTS_TESTS:
            out = part_b_dir / f"{test['name']}.mp4"
            if not run_render(img_path, "zoom", ZOOM_KWARGS, test["effects"], out, test["name"]):
                failed.append(f"B:{test['name']}")

    print()
    print("=" * 72)
    if failed:
        print(f"  ⚠ Fallaron: {', '.join(failed)}")
    print(f"  Output: {OUTPUT_BASE}")
    print()
    print("  Estructura:")
    print(f"    {OUTPUT_BASE}\\A_movements\\<img>\\horizontal.mp4 + vertical.mp4 + orbital.mp4")
    print(f"    {OUTPUT_BASE}\\B_effects_on_explosion\\zoom_in_<efecto>.mp4")
    print("=" * 72)
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())