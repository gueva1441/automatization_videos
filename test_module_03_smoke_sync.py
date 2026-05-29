"""
test_module_03_smoke_sync.py

Smoke test post fix sync_map: valida que test_module_03.py:
1. Importa correctamente (sin nuevas dependencias)
2. main() contiene la carga del sync_map antes del try
3. La llamada a assign_visual_prompts pasa sync_map como 4to arg

Este test NO ejecuta el live run (no llama Gemini).
Solo verifica estructura del módulo via inspección de source.
"""
import sys
import inspect
import importlib.util
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent

# Stub google.genai (mismo patrón que smoke tests anteriores)
import types
for modname in ("google", "google.genai", "google.genai.errors", "google.genai.types"):
    if modname not in sys.modules:
        sys.modules[modname] = types.ModuleType(modname)

class _DummyClient:
    def __init__(self, **kwargs):
        pass
class _DummyServerError(Exception):
    pass

sys.modules["google.genai"].Client = _DummyClient
sys.modules["google.genai.errors"].ServerError = _DummyServerError

print("\n=== TEST 1: import sin errores ===")
spec = importlib.util.spec_from_file_location(
    "test_module_03", PROJECT_ROOT / "test_module_03.py"
)
try:
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    print("✓ TEST 1 PASS — test_module_03 importa sin errores")
except Exception as e:
    print(f"✗ TEST 1 FAIL — {type(e).__name__}: {e}")
    sys.exit(1)

print("\n=== TEST 2: main() contiene carga del sync_map ===")
main_source = inspect.getsource(mod.main)
required_fragments = [
    "sync_map_path",
    'Path("output") / "audio"',
    'sync_map.json',
    "sync_map_path.exists()",
    "json.loads(sync_map_path.read_text",
]
missing = [f for f in required_fragments if f not in main_source]
if missing:
    print(f"✗ TEST 2 FAIL — fragmentos faltantes en main(): {missing}")
    sys.exit(1)
print(f"✓ TEST 2 PASS — los {len(required_fragments)} fragmentos de carga sync_map están")

print("\n=== TEST 3: assign_visual_prompts es llamada con 4 args (incluye sync_map) ===")
# Buscar literal: "assign_visual_prompts(topic, skeleton, narration, sync_map)"
expected_call = "assign_visual_prompts(topic, skeleton, narration, sync_map)"
if expected_call not in main_source:
    print(f"✗ TEST 3 FAIL — no se encontró la llamada esperada:")
    print(f"  Esperada: {expected_call}")
    sys.exit(1)
print(f"✓ TEST 3 PASS — assign_visual_prompts se llama con sync_map")

print("\n=== TEST 4: no se llama assign_visual_prompts sin sync_map ===")
# Verificar que NO queda la llamada vieja
old_call_pattern = "assign_visual_prompts(topic, skeleton, narration)"
# Si está, debería estar SOLO en comentarios o no estar
non_comment_lines = [
    line for line in main_source.split("\n")
    if old_call_pattern in line and not line.strip().startswith("#")
]
if non_comment_lines:
    print(f"✗ TEST 4 FAIL — todavía queda la llamada vieja sin sync_map:")
    for line in non_comment_lines:
        print(f"    {line}")
    sys.exit(1)
print(f"✓ TEST 4 PASS — la llamada vieja sin sync_map ya no existe")

print("\n=== TEST 5: simbolos esperados siguen existiendo ===")
expected_symbols = ["main", "_print_assignment", "_collect_visible_prompts",
                    "_audit_proper_names", "_audit_literal_text",
                    "_audit_temporal_markers", "_print_post_4e_audits",
                    "assign_visual_prompts"]
missing = [s for s in expected_symbols if not hasattr(mod, s)]
if missing:
    print(f"✗ TEST 5 FAIL — símbolos faltantes: {missing}")
    sys.exit(1)
print(f"✓ TEST 5 PASS — los {len(expected_symbols)} símbolos esperados están")

print("\n" + "="*72)
print("✓✓✓ TODOS LOS TESTS PASS — sync_map fix OK")
print("="*72)
