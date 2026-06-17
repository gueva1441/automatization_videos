"""
_lab_chat66b_m01b_schema.py — HANDOFF 66b (R4)

Lab READ-ONLY / STRUCTURAL: verifica que los response_schema agregados a
script_engine/m01b_narrator.py concuerden con lo que exigen sus validadores.
NO hace ninguna llamada a la API (Gemini). Sólo:
  1. Asserts estructurales sobre los dicts de schema (tipos UPPERCASE, required).
  2. Cruza cada `required` del schema contra lo que el validador hard-requiere.
  3. Control: un dict known-good pasa el validador real del módulo.

Run: python -X utf8 _lab_chat66b_m01b_schema.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "script_engine"))

from m01b_narrator import (  # noqa: E402
    _narration_schema,
    _humanizer_schema,
    _validate_narration,
    _validate_humanizer,
    HUMANIZER_COUNT,
    HUMANIZER_MAX_CHARS,
    LEN_HOOK,
    NarrationValidationError,
)

ok = 0
fail = 0


def check(label, cond):
    global ok, fail
    if cond:
        ok += 1
        print(f"  PASS  {label}")
    else:
        fail += 1
        print(f"  FAIL  {label}")


print("=" * 60)
print("HANDOFF 66b (R4) — structural lab m01b schemas (NO API)")
print("=" * 60)

# ── narration schema ──
ns = _narration_schema()
print("\n[narration schema]")
print(f"  {ns}")
check("type OBJECT", ns.get("type") == "OBJECT")
check("tiene property 'narration'", "narration" in ns.get("properties", {}))
check("narration es STRING", ns["properties"]["narration"].get("type") == "STRING")
check("required == ['narration']", ns.get("required") == ["narration"])
# El validador exige narration como string no vacío → debe ser required.
check("required cubre lo que exige _validate_narration (narration)",
      "narration" in ns.get("required", []))
# El modelo NO emite chapter_number (lo agrega el código) → NO debe ser required.
check("chapter_number NO está en required (lo agrega el código)",
      "chapter_number" not in ns.get("required", []))

# ── humanizer schema ──
hs = _humanizer_schema()
print("\n[humanizer schema]")
print(f"  {hs}")
check("type OBJECT", hs.get("type") == "OBJECT")
check("tiene property 'humanizer_phrases'", "humanizer_phrases" in hs.get("properties", {}))
hp = hs["properties"]["humanizer_phrases"]
check("humanizer_phrases es ARRAY", hp.get("type") == "ARRAY")
check("items STRING", hp.get("items", {}).get("type") == "STRING")
check(f"minItems == {HUMANIZER_COUNT}", hp.get("minItems") == HUMANIZER_COUNT)
check(f"maxItems == {HUMANIZER_COUNT}", hp.get("maxItems") == HUMANIZER_COUNT)
check("required == ['humanizer_phrases']", hs.get("required") == ["humanizer_phrases"])

# ── controls: known-good dicts pasan los validadores reales ──
print("\n[control: known-good pasa el validador real]")

# narration hook válida: 1ra oración corta, largo dentro de LEN_HOOK, sin frases prohibidas.
lo, hi = LEN_HOOK
good_narration = "99 marinos. Sin un solo SOS. "
# rellenar con oraciones completas hasta entrar en banda [lo, hi]
filler = "El metal cedió bajo la presión del abismo y nadie supo jamás por qué. "
while len(good_narration) < lo:
    good_narration += filler
good_narration = good_narration.strip()
if len(good_narration) > hi:  # red de seguridad: recortar en límite de oración
    cut = good_narration[:hi]
    good_narration = cut[: cut.rfind(".") + 1]
try:
    _validate_narration(good_narration, role="hook", cap_number=1)
    check(f"good narration ({len(good_narration)} chars) pasa _validate_narration", True)
except NarrationValidationError as e:
    check(f"good narration pasa _validate_narration — {e}", False)

# humanizer known-good: 3 frases, sin números, <= HUMANIZER_MAX_CHARS
good_humanizer = ["Y eso fue solo el principio.", "Imaginá ese instante.", "Para que nadie lo olvide."]
assert all(len(p) <= HUMANIZER_MAX_CHARS for p in good_humanizer)
try:
    cleaned = _validate_humanizer(good_humanizer)
    check(f"good humanizer pasa _validate_humanizer ({len(cleaned)} frases)",
          len(cleaned) == HUMANIZER_COUNT)
except NarrationValidationError as e:
    check(f"good humanizer pasa _validate_humanizer — {e}", False)

# cross-check: el schema NO sería más estricto que el validador.
# narration: validador no exige ningún campo más que narration → schema OK.
# humanizer: validador exige exactamente HUMANIZER_COUNT → schema min==max==COUNT OK.
print("\n[cross-check schema vs validador]")
check("narration schema no exige campos que el validador no pide",
      set(ns.get("required", [])) <= {"narration"})
check("humanizer schema min/max == HUMANIZER_COUNT (igual que el validador)",
      hp.get("minItems") == HUMANIZER_COUNT and hp.get("maxItems") == HUMANIZER_COUNT)

print("\n" + "=" * 60)
print(f"RESULTADO: {ok} PASS / {fail} FAIL")
print("=" * 60)
sys.exit(1 if fail else 0)
