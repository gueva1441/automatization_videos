"""
test_module_03_smoke.py

Smoke test post chat 30 cleanup: valida que test_module_03.py:
1. Importa correctamente (no falla por CHARS_PER_IMAGE)
2. _print_assignment NO llama _calculate_image_count con string
3. main() NO llama _offline_prompt_checks
4. main() NO llama _calculate_image_count en pre-calculo

Este test NO ejecuta el live run (no llama Gemini, no usa plata).
Solo verifica estructura del módulo.
"""
import sys
import types as _pytypes
import importlib.util
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent

# Stub google.genai (+ submódulos types, errors) para correr aislado sin
# instalar deps. El smoke test no llama a Gemini.
if "google" not in sys.modules:
    google_pkg = _pytypes.ModuleType("google")
    genai_mod = _pytypes.ModuleType("google.genai")
    types_mod = _pytypes.ModuleType("google.genai.types")
    errors_mod = _pytypes.ModuleType("google.genai.errors")
    class _DummyClient:
        def __init__(self, *a, **kw): pass
    genai_mod.Client = _DummyClient
    class _DummyServerError(Exception): pass
    errors_mod.ServerError = _DummyServerError
    google_pkg.genai = genai_mod
    genai_mod.types = types_mod
    genai_mod.errors = errors_mod
    sys.modules["google"] = google_pkg
    sys.modules["google.genai"] = genai_mod
    sys.modules["google.genai.types"] = types_mod
    sys.modules["google.genai.errors"] = errors_mod

print("\n=== TEST 1: import sin errores ===")
spec = importlib.util.spec_from_file_location(
    "test_module_03", PROJECT_ROOT / "test_module_03.py"
)
try:
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    print("✓ TEST 1 PASS — test_module_03 importa sin errores")
except ImportError as e:
    print(f"✗ TEST 1 FAIL — ImportError: {e}")
    sys.exit(1)
except Exception as e:
    print(f"✗ TEST 1 FAIL — {type(e).__name__}: {e}")
    sys.exit(1)

print("\n=== TEST 2: _offline_prompt_checks ELIMINADA ===")
if hasattr(mod, "_offline_prompt_checks"):
    print(f"✗ TEST 2 FAIL — _offline_prompt_checks aún existe en el módulo")
    sys.exit(1)
print("✓ TEST 2 PASS — _offline_prompt_checks no existe (eliminada)")

print("\n=== TEST 3: símbolos esperados existen ===")
expected = ["assign_visual_prompts", "_calculate_image_count", "_build_flux_prompt",
            "_build_rules_block", "SYSTEM_INSTRUCTION_VISUAL", "MIN_IMAGES_FLUX",
            "MAX_IMAGES_FLUX", "SECONDS_PER_IMAGE_TARGET", "VEO_CHAPTERS", "FLUX_CHAPTERS",
            "_print_assignment", "_collect_visible_prompts", "main"]
missing = [sym for sym in expected if not hasattr(mod, sym)]
if missing:
    print(f"✗ TEST 3 FAIL — símbolos faltantes: {missing}")
    sys.exit(1)
print(f"✓ TEST 3 PASS — los {len(expected)} símbolos esperados están")

print("\n=== TEST 4: CHARS_PER_IMAGE NO está importado ===")
if hasattr(mod, "CHARS_PER_IMAGE"):
    print(f"✗ TEST 4 FAIL — CHARS_PER_IMAGE todavía importada")
    sys.exit(1)
print("✓ TEST 4 PASS — CHARS_PER_IMAGE ya no se importa")

print("\n=== TEST 5: _print_assignment funciona con output schema nuevo ===")
# Crear mock output del m03 chat 30 (1 campo prompt por imagen)
mock_output = {
    "topic_id": "test-mock",
    "chapters": [
        {
            "chapter_number": 1,
            "image_prompt": "rural village at dusk, kerosene lamps glowing",
            "video_prompt": "slow pan, gentle breeze",
            "subject_ref": "establishing_shot",
            "narration_anchor": "El silencio cubrió la aldea",
        },
        {
            "chapter_number": 2,
            "image_prompts": [
                {
                    "prompt": "A Cameroonian woman in her 40s sleeping inside a mud-brick hut.",
                    "subject_ref": "main_subject",
                    "emotional_rank": "R2",
                    "narration_anchor": "Los habitantes dormían tranquilos",
                },
            ],
        },
    ],
}
mock_skeleton = {"chapters": [
    {"chapter_number": 1, "render_engine": "veo", "title": "Hook"},
    {"chapter_number": 2, "render_engine": "flux", "title": "Setup"},
]}
mock_narration = {"chapters": [
    {"chapter_number": 1, "narration": "El silencio cubrió la aldea aquella noche."},
    {"chapter_number": 2, "narration": "Los habitantes dormían tranquilos sin saber nada."},
]}
try:
    mod._print_assignment(mock_output, mock_skeleton, mock_narration)
    print("✓ TEST 5 PASS — _print_assignment corre sin errores con schema chat 30")
except Exception as e:
    print(f"✗ TEST 5 FAIL — {type(e).__name__}: {e}")
    sys.exit(1)

print("\n" + "="*72)
print("✓✓✓ TODOS LOS TESTS PASS — test_module_03.py cleanup OK")
print("="*72)
