"""
_lab_chat66b_m01a_schema.py — lab read-only (HANDOFF 66b, LEVER B / m01a).

Assert ESTRUCTURAL (sin llamar a la API): el _skeleton_schema() matchea EXACTO el contrato que
_validate_skeleton / _validate_distribution_plan ya exigen. Si el schema y el validador divergen,
el modelo emitiría algo que el validador rechaza (o viceversa) → este lab lo caza.
"""
from __future__ import annotations
import script_engine.m01a_skeleton as m

s = m._skeleton_schema()

# top-level
assert s["type"] == "OBJECT"
assert set(s["required"]) == {"_distribution_plan", "chapters"}, s["required"]

# _distribution_plan: keys EXACTO cap_2..cap_6 (= DEVELOPMENT_CAPS, lo que el validador exige)
dp = s["properties"]["_distribution_plan"]
expected_caps = {f"cap_{i}" for i in m.DEVELOPMENT_CAPS}
assert set(dp["properties"].keys()) == expected_caps, dp["properties"].keys()
assert set(dp["required"]) == expected_caps, dp["required"]
for cap, spec in dp["properties"].items():
    assert spec["type"] == "ARRAY" and spec["items"]["type"] == "STRING", (cap, spec)
print("OK _distribution_plan: cap_2..cap_6, todos required, arrays de string")

# chapters: 7 exactos, items con los 4 campos que el validador chequea
ch = s["properties"]["chapters"]
assert ch["type"] == "ARRAY" and ch["minItems"] == 7 and ch["maxItems"] == 7, ch
item = ch["items"]
assert set(item["required"]) == {"chapter_number", "title", "narrative_intent", "bullets"}, item["required"]
assert item["properties"]["chapter_number"]["type"] == "INTEGER"
assert item["properties"]["title"]["type"] == "STRING"
assert item["properties"]["narrative_intent"]["type"] == "STRING"
b = item["properties"]["bullets"]
assert b["type"] == "ARRAY" and b["items"]["type"] == "STRING"
assert b["minItems"] == m.MIN_BULLETS_PER_CHAPTER and b["maxItems"] == m.MAX_BULLETS_PER_CHAPTER, b
print("OK chapters: 7, campos required, bullets bounds = MIN/MAX_BULLETS_PER_CHAPTER")

# control: un skeleton que cumple el schema PASA _validate_skeleton (no flipea)
good = {
    "_distribution_plan": {f"cap_{i}": [] for i in m.DEVELOPMENT_CAPS},
    "chapters": [
        {"chapter_number": i, "title": f"Cap {i}",
         "narrative_intent": m.DEFAULT_INTENT_BY_CAP[i],
         "bullets": ["a", "b", "c", "d"]}
        for i in range(1, 8)
    ],
}
m._validate_skeleton(good)   # no debe lanzar
print("OK control known-good: _validate_skeleton no flipea")

print("LAB 66b-B PASS")
