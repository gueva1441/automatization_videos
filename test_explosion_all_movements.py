"""
test_explosion_all_movements.py
Testea los 6 movimientos DepthFlow sobre ch03_img_05.png (la explosión).

PARTE 1: introspección de la API DepthScene (rápida, sin render)
PARTE 2: render de los 6 movimientos con config v12
"""
import json
import subprocess
import sys
from pathlib import Path

IMG = Path(
    r"C:\CLAUDE_PROJECTS\automatization_videos\output"
    r"\7b52de57-eee6-4018-ac25-8357e9779d92\assets\ch03_img_05.png"
)
OUTPUT_DIR = Path(r"C:\CLAUDE_PROJECTS\automatization_videos\test_explosion_all")
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


# ═══════════════════════════════════════════════════════════════
#  PARTE 1: INTROSPECCIÓN
# ═══════════════════════════════════════════════════════════════

INTROSPECT_CODE = r"""
import json
from depthflow.scene import DepthScene

scene = DepthScene(backend="headless")

print("=" * 60)
print("STATE FIELDS (scene.state)")
print("=" * 60)
print(scene.state.model_dump_json(indent=2))

print("=" * 60)
print("CONFIG FIELDS (scene.config)")
print("=" * 60)
try:
    print(scene.config.model_dump_json(indent=2))
except Exception as e:
    print(f"  scene.config no tiene model_dump_json: {e}")
    print(f"  dir(scene.config) = {[m for m in dir(scene.config) if not m.startswith('_')]}")

print("=" * 60)
print("METHODS (scene.*)")
print("=" * 60)
methods = sorted(m for m in dir(scene) if not m.startswith('_'))
print(json.dumps(methods, indent=2))
"""


# ═══════════════════════════════════════════════════════════════
#  PARTE 2: RENDER DE 6 MOVIMIENTOS
# ═══════════════════════════════════════════════════════════════

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
print(f"[state] height={scene.state.height} mirror=False", file=sys.stderr)

movement = params["movement"]
mv_kwargs = params["mv_kwargs"]
print(f"[movement] scene.{movement}({mv_kwargs})", file=sys.stderr)

method = getattr(scene, movement)
method(**mv_kwargs)

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


MOVEMENTS = [
    # YA CONOCIDOS (réplica exacta de v12)
    {
        "name": "zoom_in",
        "movement": "zoom",
        "mv_kwargs": {"intensity": INTENSITY, "reverse": False, "smooth": True,
                      "loop": False, "phase": 0.0, "isometric": 0.8},
    },
    {
        "name": "zoom_out",
        "movement": "zoom",
        "mv_kwargs": {"intensity": INTENSITY, "reverse": True, "smooth": True,
                      "loop": False, "phase": 0.0, "isometric": 0.8},
    },
    {
        "name": "dolly",
        "movement": "dolly",
        "mv_kwargs": {"intensity": INTENSITY, "reverse": False, "smooth": True,
                      "loop": True, "phase": 0.0, "depth": 0.35},
    },
    {
        "name": "horizontal",
        "movement": "horizontal",
        "mv_kwargs": {"intensity": INTENSITY, "reverse": False, "smooth": True,
                      "loop": True, "phase": 0.0, "steady": 0.3, "isometric": 0.6},
    },

    # NUEVOS (kwargs mínimos — usan defaults oficiales para el resto)
    {
        "name": "vertical",
        "movement": "vertical",
        "mv_kwargs": {"intensity": INTENSITY, "smooth": True, "loop": True,
                      "phase": 0.0, "steady": 0.3, "isometric": 0.6},
    },
    {
        "name": "circle",
        "movement": "circle",
        "mv_kwargs": {"intensity": INTENSITY, "smooth": True, "loop": True,
                      "phase": 0.0},
    },
    {
        "name": "orbital",
        "movement": "orbital",
        "mv_kwargs": {"intensity": INTENSITY, "smooth": True, "loop": True,
                      "phase": 0.0, "depth": 0.5},
    },
]


def run_introspection():
    print("=" * 72)
    print("  PARTE 1: introspección de la API DepthScene")
    print("=" * 72)
    cmd = [str(PYTHON_DEPTHFLOW), "-c", INTROSPECT_CODE]
    result = subprocess.run(cmd, capture_output=True, timeout=60)
    print(result.stdout.decode("utf-8", errors="replace"))
    if result.returncode != 0:
        print("STDERR:", result.stderr.decode("utf-8", errors="replace")[-500:])


def run_movement(mv: dict) -> bool:
    out = OUTPUT_DIR / f"{mv['name']}.mp4"
    params = {
        "image_path":   str(IMG),
        "output_path":  str(out),
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
    print(f"  → {mv['name']:12s} ", end="", flush=True)
    try:
        result = subprocess.run(cmd, capture_output=True, timeout=180)
    except subprocess.TimeoutExpired:
        print("❌ TIMEOUT")
        return False
    if result.returncode != 0:
        stderr = (result.stderr or b"").decode("utf-8", errors="replace")
        print(f"❌ FAIL (rc={result.returncode})")
        print(f"     stderr: {stderr[-400:]}")
        return False
    size_kb = out.stat().st_size // 1024
    print(f"✅ {size_kb} KB")
    return True


def main() -> int:
    if not IMG.exists():
        print(f"❌ No existe imagen: {IMG}")
        return 1
    if not PYTHON_DEPTHFLOW.exists():
        print(f"❌ No existe venv DepthFlow: {PYTHON_DEPTHFLOW}")
        return 1

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Parte 1: introspección
    run_introspection()

    # Parte 2: render
    print("=" * 72)
    print(f"  PARTE 2: render de {len(MOVEMENTS)} movimientos sobre {IMG.name}")
    print(f"  state.height = {STATE_HEIGHT} (config v12)")
    print("=" * 72)
    failed = []
    for mv in MOVEMENTS:
        if not run_movement(mv):
            failed.append(mv["name"])
    print()
    print("=" * 72)
    if failed:
        print(f"  ⚠ Fallaron: {', '.join(failed)}")
    print(f"  Output: {OUTPUT_DIR}")
    print("=" * 72)
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())