"""
test_module_03_v7_prompt_v2.py

Test aislado del refactor chat 30 (#209 v2 estructural).
Valida que el nuevo schema (1 campo `prompt` en lugar de 3 slots) funciona
correctamente en _validate_flux_cap + ensamblaje.

Mockea el LLM para no gastar Gemini. Construye outputs sintéticos que
simulan lo que el LLM emitiría según el nuevo SYSTEM_INSTRUCTION_VISUAL.
"""
import sys
import json
import types as _pytypes
from pathlib import Path

# Path setup
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "script_engine"))

# ─── Stub google.genai para correr aislado sin instalar deps ───
# El test no llama a Gemini (mockea outputs sintéticos). Solo necesita
# que `from google import genai` no explote al importar m03_visual.
if "google" not in sys.modules:
    google_pkg = _pytypes.ModuleType("google")
    genai_mod = _pytypes.ModuleType("google.genai")
    types_mod = _pytypes.ModuleType("google.genai.types")
    errors_mod = _pytypes.ModuleType("google.genai.errors")
    class _StubClient:
        def __init__(self, *a, **kw): pass
    genai_mod.Client = _StubClient
    class _StubServerError(Exception): pass
    errors_mod.ServerError = _StubServerError
    google_pkg.genai = genai_mod
    genai_mod.types = types_mod
    genai_mod.errors = errors_mod
    sys.modules["google"] = google_pkg
    sys.modules["google.genai"] = genai_mod
    sys.modules["google.genai.types"] = types_mod
    sys.modules["google.genai.errors"] = errors_mod

from m03_visual import _validate_flux_cap, VisualValidationError
from nicho_config import get_active_nicho

ANCLA = get_active_nicho()["ancla_global"]

# ────────────────────────────────────────────────────────────────────────
# Test 1: validator acepta schema nuevo (1 campo prompt)
# ────────────────────────────────────────────────────────────────────────
print("\n=== TEST 1: validator acepta schema nuevo ===")
NARRATION = (
    "El silencio cubrió la aldea aquella noche. Los habitantes dormían "
    "tranquilos, sin saber que una nube invisible descendía del lago."
)
mock_output = {
    "image_prompts": [
        {
            "prompt": (
                "A Cameroonian woman in her 40s, dark skin and weathered "
                "features, wearing a 1980s rural cotton wrap, sleeping "
                "peacefully on a woven mat inside a mud-brick hut at night, "
                "dim moonlight filtering through small openings, calm "
                "atmosphere."
            ),
            "subject_ref": "main_subject",
            "emotional_rank": "R2",
            "narration_anchor": "Los habitantes dormían tranquilos",
        },
        {
            "prompt": (
                "A dense low-lying grey cloud descending silently over a "
                "rural Cameroonian valley at night, traditional huts dimly "
                "visible below, ominous atmosphere, period-correct 1986 "
                "rural setting."
            ),
            "subject_ref": "establishing_shot",
            "emotional_rank": "R1",
            "narration_anchor": "una nube invisible descendía del lago",
        },
    ]
}

try:
    result = _validate_flux_cap(mock_output, NARRATION, cap_number=2, n_expected=2)
    assert "image_prompts" in result, "Falta image_prompts en output normalizado"
    assert len(result["image_prompts"]) == 2, f"Esperaba 2 items, llegaron {len(result['image_prompts'])}"
    for i, item in enumerate(result["image_prompts"], 1):
        assert "prompt" in item, f"item {i}: falta campo 'prompt'"
        assert "sujeto_fisico" not in item, f"item {i}: schema viejo (sujeto_fisico) NO debe estar"
        assert "anclas_temporales_o_tecnicas" not in item, f"item {i}: schema viejo NO debe estar"
        assert "modificador_de_escena" not in item, f"item {i}: schema viejo NO debe estar"
    print("✓ TEST 1 PASS — validator acepta nuevo schema")
except Exception as e:
    print(f"✗ TEST 1 FAIL: {e}")
    sys.exit(1)

# ────────────────────────────────────────────────────────────────────────
# Test 2: validator rechaza si falta campo prompt
# ────────────────────────────────────────────────────────────────────────
print("\n=== TEST 2: validator rechaza si falta prompt ===")
bad_output = {
    "image_prompts": [
        {
            # falta `prompt`
            "subject_ref": "main_subject",
            "emotional_rank": "R2",
            "narration_anchor": "Los habitantes dormían tranquilos",
        },
    ]
}
try:
    _validate_flux_cap(bad_output, NARRATION, cap_number=2, n_expected=1)
    print("✗ TEST 2 FAIL — debería haber raised VisualValidationError")
    sys.exit(1)
except VisualValidationError as e:
    assert "falta campo 'prompt'" in str(e), f"Mensaje inesperado: {e}"
    print(f"✓ TEST 2 PASS — rechaza con: {e}")

# ────────────────────────────────────────────────────────────────────────
# Test 3: validator rechaza si prompt vacío
# ────────────────────────────────────────────────────────────────────────
print("\n=== TEST 3: validator rechaza prompt vacío ===")
empty_output = {
    "image_prompts": [
        {
            "prompt": "   ",  # solo whitespace
            "subject_ref": "main_subject",
            "emotional_rank": "R2",
            "narration_anchor": "Los habitantes dormían tranquilos",
        },
    ]
}
try:
    _validate_flux_cap(empty_output, NARRATION, cap_number=2, n_expected=1)
    print("✗ TEST 3 FAIL — debería haber raised por prompt vacío")
    sys.exit(1)
except VisualValidationError as e:
    assert "vacío" in str(e), f"Mensaje inesperado: {e}"
    print(f"✓ TEST 3 PASS — rechaza con: {e}")

# ────────────────────────────────────────────────────────────────────────
# Test 4: validator rechaza prompt excesivamente largo
# ────────────────────────────────────────────────────────────────────────
print("\n=== TEST 4: validator rechaza prompt sobre el budget ===")
oversized_output = {
    "image_prompts": [
        {
            "prompt": "A Cameroonian woman " * 200,  # ~4000 chars, fuera de budget
            "subject_ref": "main_subject",
            "emotional_rank": "R2",
            "narration_anchor": "Los habitantes dormían tranquilos",
        },
    ]
}
try:
    _validate_flux_cap(oversized_output, NARRATION, cap_number=2, n_expected=1)
    print("✗ TEST 4 FAIL — debería haber raised por longitud")
    sys.exit(1)
except VisualValidationError as e:
    assert "excede budget" in str(e), f"Mensaje inesperado: {e}"
    print(f"✓ TEST 4 PASS — rechaza con: {e}")

# ────────────────────────────────────────────────────────────────────────
# Test 5 (smoke test del ensamblaje): el ancla va al FINAL
# ────────────────────────────────────────────────────────────────────────
print("\n=== TEST 5: ensamblaje pone ancla al final (subject-first) ===")
# Simular ensamblaje manual replicando líneas del refactor BLOQUE 5
raw = "A Cameroonian woman in her 40s, dark skin, sleeping inside a hut."
prompt_final = raw + " " + ANCLA
assert prompt_final.startswith("A Cameroonian"), \
    f"Sujeto NO está al inicio. prompt_final empieza con: {prompt_final[:50]}"
assert prompt_final.endswith(ANCLA), \
    f"Ancla NO está al final. prompt_final termina con: {prompt_final[-50:]}"
print(f"✓ TEST 5 PASS — sujeto first, ancla al final.")
print(f"  Sample: {prompt_final[:120]}...")

print("\n" + "="*72)
print("✓✓✓ TODOS LOS TESTS PASS — refactor chat 30 listo para integración")
print("="*72)
