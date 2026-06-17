"""
_lab_chat66b_m02_5_schema.py — HANDOFF 66b (R4)

Lab READ-ONLY / STRUCTURAL: verifica que el response_schema agregado a
script_engine/m02_5_normalizer_gate.py concuerde con lo que el código consume
de la respuesta del LLM auditor. NO hace ninguna llamada a la API (Gemini).

El contrato que cruzamos:
  - _audit_with_llm lee response["spans"] (lista de objetos) → schema OBJECT
    con clave "spans" (NO array bare).
  - El validador inline acepta un span sólo si tiene:
      chapter_number (int), original (str no vacío), suggested (str no vacío),
      category (str ∈ VALID_LLM_CATEGORIES), is_recurring (bool)
    → esos 5 son hard-required en el schema.
  - reasoning se lee en la CLI/persistencia pero NO se valida → opcional
    (presente en properties, ausente de required).

Run: python -X utf8 _lab_chat66b_m02_5_schema.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "script_engine"))

from m02_5_normalizer_gate import (  # noqa: E402
    _normalizer_schema,
    VALID_LLM_CATEGORIES,
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
print("HANDOFF 66b (R4) — structural lab m02_5 schema (NO API)")
print("=" * 60)

sch = _normalizer_schema()
print("\n[normalizer schema]")
print(f"  {sch}")

# ── shape top-level: OBJECT con clave "spans" (no array bare) ──
check("type OBJECT (el codigo lee response['spans'], no array bare)",
      sch.get("type") == "OBJECT")
check("tiene property 'spans'", "spans" in sch.get("properties", {}))
check("required == ['spans']", sch.get("required") == ["spans"])

spans = sch["properties"]["spans"]
check("spans es ARRAY", spans.get("type") == "ARRAY")

item = spans.get("items", {})
check("items es OBJECT", item.get("type") == "OBJECT")

props = item.get("properties", {})
req = item.get("required", [])

# ── tipos UPPERCASE de cada campo (estilo model citizen m03) ──
print("\n[tipos de campos del span]")
check("chapter_number es INTEGER", props.get("chapter_number", {}).get("type") == "INTEGER")
check("original es STRING", props.get("original", {}).get("type") == "STRING")
check("suggested es STRING", props.get("suggested", {}).get("type") == "STRING")
check("category es STRING", props.get("category", {}).get("type") == "STRING")
check("is_recurring es BOOLEAN", props.get("is_recurring", {}).get("type") == "BOOLEAN")
check("reasoning es STRING", props.get("reasoning", {}).get("type") == "STRING")

# ── enum de category == VALID_LLM_CATEGORIES exacto ──
print("\n[category enum]")
check("category.enum == VALID_LLM_CATEGORIES",
      props.get("category", {}).get("enum") == list(VALID_LLM_CATEGORIES))

# ── required == EXACTO los 5 campos hard-validados inline ──
print("\n[required vs validador inline de _audit_with_llm]")
HARD_REQUIRED = {"chapter_number", "original", "suggested", "category", "is_recurring"}
check("required cubre los 5 campos hard-validados",
      HARD_REQUIRED <= set(req))
check("reasoning NO esta en required (se lee pero no se valida)",
      "reasoning" not in req)
check("required no agrega campos que el validador no exige",
      set(req) <= HARD_REQUIRED)
check("reasoning si esta en properties (lo lee la CLI/persistencia)",
      "reasoning" in props)

# ── control: un span known-good pasa el filtro inline del modulo ──
# Replica EXACTA de la condicion en _audit_with_llm (L351-360) para garantizar
# que el schema describe spans que el codigo realmente acepta.
print("\n[control: known-good span pasa el filtro inline]")


def passes_inline_filter(s: dict) -> bool:
    return (
        isinstance(s.get("chapter_number"), int)
        and isinstance(s.get("original"), str) and bool(s["original"])
        and isinstance(s.get("suggested"), str) and bool(s["suggested"])
        and s.get("category") in VALID_LLM_CATEGORIES
        and isinstance(s.get("is_recurring"), bool)
    )


good_span = {
    "chapter_number": 1,
    "original": "RBMK-1000",
    "suggested": "erre be eme ka mil",
    "category": "acronym_with_number",
    "is_recurring": True,
    "reasoning": "sigla con numero",
}
check("good span (todos los required) pasa el filtro inline",
      passes_inline_filter(good_span))

# Un span SIN un required del schema debe ser rechazado por el filtro inline
# → confirma que cada required del schema es efectivamente hard.
for missing in HARD_REQUIRED:
    bad = dict(good_span)
    del bad[missing]
    check(f"span sin '{missing}' es rechazado por el filtro inline",
          not passes_inline_filter(bad))

# Un span SIN reasoning igual pasa → confirma reasoning opcional.
no_reason = dict(good_span)
del no_reason["reasoning"]
check("span sin 'reasoning' pasa el filtro inline (opcional, correcto)",
      passes_inline_filter(no_reason))

print("\n" + "=" * 60)
print(f"RESULTADO: {ok} PASS / {fail} FAIL")
print("=" * 60)
sys.exit(1 if fail else 0)
