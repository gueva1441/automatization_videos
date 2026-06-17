"""
_lab_chat66b_m05_schema.py — lab read-only (HANDOFF 66b, LEVER B / m05).
Assert estructural (sin API): _judge_schema() cubre AMBAS formas (PASS/FLAG) y matchea
_validate_chapter_output / _validate_single_issue. No inventa campos.
"""
from __future__ import annotations
import script_engine.m05_judge as m

s = m._judge_schema()
assert s["type"] == "OBJECT"
assert set(s["required"]) == {"chapter_id", "verdict", "issues"}, s["required"]
assert s["properties"]["chapter_id"]["type"] == "INTEGER"
assert set(s["properties"]["verdict"]["enum"]) == set(m.VALID_VERDICTS)

issues = s["properties"]["issues"]
assert issues["type"] == "ARRAY"
item = issues["items"]
# required del item == los 10 campos mandatorios del validador (exacto)
assert set(item["required"]) == set(m.ISSUE_REQUIRED_FIELDS), item["required"]
# enums atados a las constantes vivas (no drift)
assert set(item["properties"]["category"]["enum"]) == set(m.VALID_CATEGORIES)
assert set(item["properties"]["severity"]["enum"]) == set(m.VALID_SEVERITIES)
assert set(item["properties"]["proposed_root_cause_module"]["enum"]) == set(m.VALID_ROOT_CAUSE_MODULES)
assert item["properties"]["image_index"]["type"] == "INTEGER"
# todas las props del item existen en ISSUE_REQUIRED_FIELDS (no inventadas)
assert set(item["properties"].keys()) == set(m.ISSUE_REQUIRED_FIELDS), item["properties"].keys()
print("OK m05: chapter_id/verdict/issues required; item = 10 campos; enums vivos; sin inventar")
print("LAB 66b-m05 PASS")
