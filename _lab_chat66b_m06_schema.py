"""
_lab_chat66b_m06_schema.py — STRUCTURAL assert (NO API).

Verifica que _classification_schema() de m06 es coherente con lo que el código
lee desde el dict `classification` en classify_one_issue:

  - todo campo que el schema declara debe ser un campo que el código lee
    (no inventar campos),
  - el único `required` (`bucket`) debe ser el campo sobre el que el código
    bifurca (defensivos + persist/menú/assembler),
  - tipos UPPERCASE estilo m03 (OBJECT / STRING / ...).

Read-only: no toca disco, no llama Gemini.
"""

import re
from pathlib import Path

from script_engine.m06_classifier import _classification_schema

SRC = Path(__file__).parent / "script_engine" / "m06_classifier.py"
src = SRC.read_text(encoding="utf-8")

# 1) Campos que el código realmente lee del LLM: classification.get("X")
read_fields = set(re.findall(r'classification\.get\(\s*["\'](\w+)["\']', src))
assert read_fields, "no se hallaron classification.get(...) en el fuente"

schema = _classification_schema()

# 2) Forma básica estilo m03 (UPPERCASE)
assert schema["type"] == "OBJECT", schema["type"]
props = schema["properties"]
required = schema["required"]
for k, v in props.items():
    assert v.get("type") == "STRING", f"{k} no es STRING UPPERCASE: {v}"

# 3) El schema NO inventa campos: cada prop debe ser un campo leído por el código
extra = set(props) - read_fields
assert not extra, f"schema declara campos que el codigo NO lee (inventados): {extra}"

# 4) required == solo 'bucket' y bucket es leido + usado en lógica defensiva
assert required == ["bucket"], f"required esperado ['bucket'], got {required}"
assert "bucket" in read_fields, "bucket no se lee del classification"
assert 'payload.get("bucket")' in src, "bucket no se usa en lógica defensiva (payload.get)"

# 5) Cobertura: el schema cubre todos los campos del LLM (no faltan props)
missing = read_fields - set(props)
assert not missing, f"el schema NO cubre campos leidos por el codigo: {missing}"

print("OK _classification_schema:")
print(f"  campos leidos por el codigo : {sorted(read_fields)}")
print(f"  propiedades del schema      : {sorted(props)}")
print(f"  required                    : {required}")
print("  -> sin campos inventados, sin faltantes, required minimal = ['bucket']")
