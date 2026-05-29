"""
test_movements_v12.py — La clave que faltaba: state.height bajo.

═══════════════════════════════════════════════════════════════════════
HALLAZGO de la investigación (foro polycount, biblia del parallax mapping)
═══════════════════════════════════════════════════════════════════════

  "You've got WAY too much parallax going on. Try lowering the contrast
   on your heightmap. A lot."
  
  "In your heightmap, try to avoid sharp/steep edges and tall
   high-frequency details. Those can cause texture-stretching and
   rendering artifacts."

El depth map estimado por DepthAnything sobre la explosión Pripyat tiene
bordes filosos (chimeneas sobresaliendo, edificios verticales). Con
state.height alto, esos bordes producen "texture-stretching" — los streaks
que veníamos persiguiendo todo el chat.

Default DepthFlow: state.height = 0.20 (para fotos suaves).
Para imágenes complejas con sujetos verticales: 0.05 (recomendación pro).

═══════════════════════════════════════════════════════════════════════
3 movimientos en test
═══════════════════════════════════════════════════════════════════════

  zoom_in     → cámara se acerca
  dolly       → cíclico, zoom + cambio de foco
  horizontal  → swing lateral cíclico

Configuración:
  - state.height = 0.05            ← LA clave que faltaba
  - state.mirror = False           ← apagar espejos
  - intensity = 1.0                ← default oficial
  - SIN upscaler, SIN Large, SIN nada experimental

Output: C:\\CLAUDE_PROJECTS\\automatization_videos\\test_depthflow_out\\
"""
import json
import subprocess
import sys
from pathlib import Path

IMAGE_PATH = Path(
    r"C:\CLAUDE_PROJECTS\automatization_videos\output"
    r"\7b52de57-eee6-4018-ac25-8357e9779d92\assets\ch03_img_05.png"
)
OUTPUT_DIR = Path(r"C:\CLAUDE_PROJECTS\automatization_videos\test_depthflow_out")
PYTHON_DEPTHFLOW = Path(
    r"C:\CLAUDE_PROJECTS\viral-video-pipeline\.venv-depthflow\Scripts\python.exe"
)

DURATION = 6.0
WIDTH = 1080
HEIGHT = 1920
FPS = 30
SSAA = 1.5

INTENSITY = 1.0
STATE_HEIGHT = 0.05  # ← LA clave: bajar contraste del heightmap


RUNNER_CODE = r"""
import os, json, sys
os.environ.setdefault("TORCH_DEVICE", "cuda")
os.environ.setdefault("CUDA_VISIBLE_DEVICES", "0")

from depthflow.scene import DepthScene

params = json.loads(sys.argv[1])

scene = DepthScene(backend="headless")
scene.input(image=params["image_path"])

# State.height bajo = menos texture-stretching en bordes filosos
scene.state.height = params["state_height"]
print(f"[state] scene.state.height = {scene.state.height}", file=sys.stderr)

# Apagar mirror (default true)
scene.state.mirror = False
print(f"[state] scene.state.mirror = False", file=sys.stderr)

# Aplicar el movimiento
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


TESTS = [
    {
        "name": "test_v12a_zoom_in",
        "movement": "zoom",
        "mv_kwargs": {
            "intensity": INTENSITY,
            "reverse":   False,
            "smooth":    True,
            "loop":      False,
            "phase":     0.0,
            "isometric": 0.8,
        },
    },
    {
        "name": "test_v12b_dolly",
        "movement": "dolly",
        "mv_kwargs": {
            "intensity": INTENSITY,
            "reverse":   False,
            "smooth":    True,
            "loop":      True,
            "phase":     0.0,
            "depth":     0.35,
        },
    },
    {
        "name": "test_v12c_horizontal",
        "movement": "horizontal",
        "mv_kwargs": {
            "intensity": INTENSITY,
            "reverse":   False,
            "smooth":    True,
            "loop":      True,
            "phase":     0.0,
            "steady":    0.3,
            "isometric": 0.6,
        },
    },

    {
        "name": "test_v12d_zoom_out",
        "movement": "zoom",
        "mv_kwargs": {
            "intensity": INTENSITY,
            "reverse":   True,         # ← zoom_out (la API correcta)
            "smooth":    True,
            "loop":      False,
            "phase":     0.0,
            "isometric": 0.8,
        },
    },
]


def run_test(test: dict) -> bool:
    out = OUTPUT_DIR / f"{test['name']}.mp4"
    params = {
        "image_path":   str(IMAGE_PATH),
        "output_path":  str(out),
        "movement":     test["movement"],
        "mv_kwargs":    test["mv_kwargs"],
        "state_height": STATE_HEIGHT,
        "width":        WIDTH,
        "height":       HEIGHT,
        "fps":          FPS,
        "ssaa":         SSAA,
        "duration":     DURATION,
    }
    print(f"  → {test['name']}  ({test['movement']})")

    cmd = [str(PYTHON_DEPTHFLOW), "-c", RUNNER_CODE, json.dumps(params)]
    try:
        result = subprocess.run(cmd, capture_output=True, timeout=180)
        result_stderr = (result.stderr or b"").decode("utf-8", errors="replace")
    except subprocess.TimeoutExpired:
        print(f"    ❌ TIMEOUT")
        return False

    if result_stderr:
        for line in result_stderr.splitlines():
            if line.startswith("[state]") or line.startswith("[movement]"):
                print(f"    {line}")

    if result.returncode != 0:
        print(f"    ❌ FAIL (rc={result.returncode})")
        print(f"    stderr: {result_stderr[-500:]}")
        return False

    print(f"    ✅ OK ({out.stat().st_size // 1024} KB)")
    return True


def main() -> int:
    if not IMAGE_PATH.exists():
        print(f"❌ No existe la imagen: {IMAGE_PATH}")
        return 1
    if not PYTHON_DEPTHFLOW.exists():
        print(f"❌ No existe python venv: {PYTHON_DEPTHFLOW}")
        return 1

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 72)
    print("  TEST v12 — 3 movimientos + state.height BAJO (la clave que faltaba)")
    print("=" * 72)
    print(f"  Imagen          : {IMAGE_PATH.name}")
    print(f"  state.height    : {STATE_HEIGHT}  (default es 0.20 — bajamos para")
    print(f"                     evitar texture-stretching de bordes filosos)")
    print(f"  intensity       : {INTENSITY}")
    print(f"  state.mirror    : False")
    print()

    failed: list[str] = []
    for t in TESTS:
        if not run_test(t):
            failed.append(t["name"])

    print()
    print("=" * 72)
    if failed:
        print(f"  ⚠ Fallaron: {', '.join(failed)}")
        return 1

    print("  ✅ Los 3 clips listos. Abrilos y decime cuáles van bien:")
    print()
    print("    test_v12a_zoom_in.mp4    → cámara acercándose")
    print("    test_v12b_dolly.mp4      → cíclico, zoom + cambio de foco")
    print("    test_v12c_horizontal.mp4 → swing lateral (loop)")
    print()
    print("  Si funcionan: probamos test_v12d con zoom_out (el difícil) usando")
    print("  state.height = 0.05 también, a ver si revive.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
