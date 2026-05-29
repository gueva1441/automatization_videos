"""
test_visual_complexity_classifier.py — Chat 21, primer test del clasificador visual.

═══════════════════════════════════════════════════════════════════════
PROPÓSITO
═══════════════════════════════════════════════════════════════════════

1. Recorre las 10 imágenes Flux de output/<topic_id>/assets/.
2. Por cada imagen:
   a. Gemini 2.5 Flash Vision la clasifica:
      - complicada=True  → explosiones, fuego, partículas, bordes filosos
      - complicada=False → sujetos sólidos, fondos continuos, profundidad gradual
   b. Crea folder test_classifier_out/<nombre_foto>/
   c. Copia la imagen al folder.
   d. Escribe classification.json con el veredicto del LLM.
   e. Renderiza los 4 movimientos DepthFlow (zoom_in, zoom_out, dolly,
      horizontal) usando EXACTO la config validada de test_movements_v12.py.
3. Escribe _summary.json con todas las clasificaciones juntas.

═══════════════════════════════════════════════════════════════════════
USO
═══════════════════════════════════════════════════════════════════════

  cd C:\\CLAUDE_PROJECTS\\automatization_videos
  C:\\CLAUDE_PROJECTS\\viral-video-pipeline\\.venv\\Scripts\\python.exe test_visual_complexity_classifier.py

Si pillow no está instalado:
  C:\\CLAUDE_PROJECTS\\viral-video-pipeline\\.venv\\Scripts\\pip.exe install pillow

═══════════════════════════════════════════════════════════════════════
NO TOCA PRODUCCIÓN
═══════════════════════════════════════════════════════════════════════
- Usa gemini_client de config.py (lectura).
- NO modifica gemini_helpers.py.
- NO modifica parallax_animator_v2.py.
- Genera todo en test_classifier_out/ (carpeta nueva).
"""
import json
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import PIL.Image
from google.genai import types

from config import api, gemini_client


# ═══════════════════════════════════════════════════════════════
#  PATHS
# ═══════════════════════════════════════════════════════════════

ASSETS_DIR = Path(
    r"C:\CLAUDE_PROJECTS\automatization_videos\output"
    r"\7b52de57-eee6-4018-ac25-8357e9779d92\assets"
)
OUTPUT_BASE = Path(r"C:\CLAUDE_PROJECTS\automatization_videos\test_classifier_out")
PYTHON_DEPTHFLOW = Path(
    r"C:\CLAUDE_PROJECTS\viral-video-pipeline\.venv-depthflow\Scripts\python.exe"
)


# ═══════════════════════════════════════════════════════════════
#  CONFIG DEPTHFLOW (réplica EXACTA de test_movements_v12.py)
# ═══════════════════════════════════════════════════════════════

DURATION = 6.0
WIDTH = 1080
HEIGHT = 1920
FPS = 30
SSAA = 1.5

INTENSITY = 1.0
STATE_HEIGHT = 0.05  # ← LA clave validada chat 20


RUNNER_CODE = r"""
import os, json, sys
os.environ.setdefault("TORCH_DEVICE", "cuda")
os.environ.setdefault("CUDA_VISIBLE_DEVICES", "0")

from depthflow.scene import DepthScene

params = json.loads(sys.argv[1])

scene = DepthScene(backend="headless")
scene.input(image=params["image_path"])

scene.state.height = params["state_height"]
print(f"[state] scene.state.height = {scene.state.height}", file=sys.stderr)

scene.state.mirror = False
print(f"[state] scene.state.mirror = False", file=sys.stderr)

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
    {
        "name": "zoom_in",
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
        "name": "zoom_out",
        "movement": "zoom",
        "mv_kwargs": {
            "intensity": INTENSITY,
            "reverse":   True,         # ← API correcta zoom_out (chat 20)
            "smooth":    True,
            "loop":      False,
            "phase":     0.0,
            "isometric": 0.8,
        },
    },
    {
        "name": "dolly",
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
        "name": "horizontal",
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
]


# ═══════════════════════════════════════════════════════════════
#  PROMPT GEMINI VISION
# ═══════════════════════════════════════════════════════════════

SYSTEM_INSTRUCTION = (
    "You are a visual complexity classifier for DepthFlow 2.5D parallax animation. "
    "Your job is to look at a still image and decide if it is COMPLICATED for DepthFlow "
    "(meaning the AI-estimated depth map will likely produce visible artifacts when the "
    "shader animates the image with camera movements). You answer in strict JSON only."
)

USER_PROMPT = """Analyze this image and decide whether it is COMPLICATED for DepthFlow 2.5D parallax animation.

DepthFlow estimates a depth map with DepthAnything and then displaces pixels to simulate 3D camera moves. It works well on some images and poorly on others.

==========================================
COMPLICATED for DepthFlow (return complicada=true)
==========================================
The image has any of these:
- Explosions, fire, dense smoke
- Thin vertical subjects against open sky (chimneys, poles, cables, antennas)
- Small dispersed particles (sparks, rain, snow, dust)
- Extreme depth contrast (close subject + very far background with no midground)
- Multiple chaotic visual elements with no clear depth hierarchy
- Sharp edges between subject and very distant background

==========================================
NOT complicated for DepthFlow (return complicada=false)
==========================================
The image has these properties:
- Solid compact subjects in defined zones
- Continuous backgrounds without sharp transitions
- Gradual predictable depth (clear foreground/midground/background)
- Soft edges (no thin lines against open space)
- Coherent tonal palette

==========================================
OUTPUT FORMAT (strict JSON, no prose)
==========================================
{
  "complicada": true | false,
  "reasoning": "1-2 sentences in Spanish explaining the call",
  "detected_issues": ["list of specific visual elements that drove the decision, in Spanish"],
  "confidence": "high" | "medium" | "low"
}
"""


def classify_image(image_path: Path) -> dict:
    """Llama a Gemini 2.5 Flash Vision con la imagen y devuelve el dict de clasificación."""
    img = PIL.Image.open(image_path)

    response = gemini_client.models.generate_content(
        model=api.gemini_model,
        contents=[img, USER_PROMPT],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            system_instruction=SYSTEM_INSTRUCTION,
        ),
    )

    raw = response.text.strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        return {
            "complicada": None,
            "reasoning": f"ERROR parseando JSON: {e}",
            "detected_issues": [],
            "confidence": "error",
            "_raw": raw,
        }


# ═══════════════════════════════════════════════════════════════
#  RENDER DEPTHFLOW
# ═══════════════════════════════════════════════════════════════

def render_movement(image_path: Path, movement: dict, output_path: Path) -> bool:
    params = {
        "image_path":   str(image_path),
        "output_path":  str(output_path),
        "movement":     movement["movement"],
        "mv_kwargs":    movement["mv_kwargs"],
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
        print(f"      ❌ {movement['name']} TIMEOUT")
        return False

    if result.returncode != 0:
        stderr = (result.stderr or b"").decode("utf-8", errors="replace")
        print(f"      ❌ {movement['name']} FAIL (rc={result.returncode})")
        print(f"      stderr: {stderr[-300:]}")
        return False

    size_kb = output_path.stat().st_size // 1024
    print(f"      ✅ {movement['name']:10s} ({size_kb} KB)")
    return True


# ═══════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════

def main() -> int:
    if not ASSETS_DIR.exists():
        print(f"❌ No existe carpeta de imágenes: {ASSETS_DIR}")
        return 1
    if not PYTHON_DEPTHFLOW.exists():
        print(f"❌ No existe venv DepthFlow: {PYTHON_DEPTHFLOW}")
        return 1

    images = sorted(ASSETS_DIR.glob("*.png"))
    if not images:
        print(f"❌ No hay .png en: {ASSETS_DIR}")
        return 1

    OUTPUT_BASE.mkdir(parents=True, exist_ok=True)

    print("=" * 72)
    print("  TEST CLASIFICADOR VISUAL — Chat 21")
    print("=" * 72)
    print(f"  Imágenes encontradas : {len(images)}")
    print(f"  Output base          : {OUTPUT_BASE}")
    print(f"  Modelo Gemini        : {api.gemini_model}")
    print(f"  Config DepthFlow     : v12 (state.height={STATE_HEIGHT}, mirror=False)")
    print(f"  Movimientos por foto : {len(MOVEMENTS)} ({', '.join(m['name'] for m in MOVEMENTS)})")
    print()

    summary = []

    for idx, img_path in enumerate(images, 1):
        stem = img_path.stem  # ej "ch03_img_05"
        folder = OUTPUT_BASE / stem
        folder.mkdir(parents=True, exist_ok=True)

        print(f"[{idx}/{len(images)}] {img_path.name}")

        # 1. Copiar imagen al folder de salida
        dest_img = folder / img_path.name
        if not dest_img.exists():
            shutil.copy2(img_path, dest_img)

        # 2. Clasificar con Gemini Vision
        t0 = time.time()
        try:
            classification = classify_image(img_path)
        except Exception as e:
            print(f"    ❌ Error en Gemini Vision: {e}")
            classification = {
                "complicada": None,
                "reasoning": f"ERROR de llamada: {e}",
                "detected_issues": [],
                "confidence": "error",
            }
        elapsed = time.time() - t0

        complicada = classification.get("complicada")
        label_str = "🔴 COMPLICADA" if complicada is True else (
            "🟢 simple    " if complicada is False else "⚠ ERROR     "
        )
        print(f"    {label_str}  ({elapsed:.1f}s)")
        if classification.get("reasoning"):
            print(f"    razón: {classification['reasoning']}")

        # 3. Persistir clasificación
        classification_record = {
            "image": img_path.name,
            "timestamp": datetime.now().isoformat(),
            "model": api.gemini_model,
            "elapsed_seconds": round(elapsed, 2),
            **classification,
        }
        (folder / "classification.json").write_text(
            json.dumps(classification_record, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        # 4. Renderizar movimientos según clasificación
        if complicada is True:
            movements_to_render = [m for m in MOVEMENTS if m["name"] == "horizontal"]
            print(f"    complicada → solo horizontal")
        elif complicada is False:
            movements_to_render = MOVEMENTS
            print(f"    simple → los 4 movimientos")
        else:
            movements_to_render = []
            print(f"    ⚠ clasificación con error, no se renderiza nada")

        movement_results = {}
        for mv in movements_to_render:
            out_mp4 = folder / f"{mv['name']}.mp4"
            ok = render_movement(img_path, mv, out_mp4)
            movement_results[mv["name"]] = "ok" if ok else "fail"
        summary.append({
            "image": img_path.name,
            "complicada": complicada,
            "confidence": classification.get("confidence"),
            "reasoning": classification.get("reasoning"),
            "detected_issues": classification.get("detected_issues", []),
            "movement_results": movement_results,
            "folder": str(folder),
        })
        print()

    # 5. Summary global
    summary_path = OUTPUT_BASE / "_summary.json"
    summary_path.write_text(
        json.dumps(
            {
                "timestamp": datetime.now().isoformat(),
                "model": api.gemini_model,
                "total_images": len(images),
                "complicadas": sum(1 for s in summary if s["complicada"] is True),
                "simples":     sum(1 for s in summary if s["complicada"] is False),
                "errores":     sum(1 for s in summary if s["complicada"] is None),
                "results": summary,
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print("=" * 72)
    print(f"  ✅ Done. Resumen en: {summary_path}")
    print(f"     Complicadas: {sum(1 for s in summary if s['complicada'] is True)}")
    print(f"     Simples    : {sum(1 for s in summary if s['complicada'] is False)}")
    print(f"     Errores    : {sum(1 for s in summary if s['complicada'] is None)}")
    print("=" * 72)
    return 0


if __name__ == "__main__":
    sys.exit(main())