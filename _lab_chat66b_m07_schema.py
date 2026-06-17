"""HANDOFF 66b (R4) — structural assert for m07 _match_schema().

Read-only, NO API. Verifies the response_schema's required fields match
exactly the keys the consuming code reads from `result` in
_match_intent_to_track (the `required` set + the dict it returns).
Run: python -X utf8 _lab_chat66b_m07_schema.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "script_engine"))

from m07_music_director import _match_schema  # noqa: E402

UPPER = {"OBJECT", "ARRAY", "STRING", "INTEGER", "BOOLEAN", "NUMBER"}

# What the consuming code (_match_intent_to_track) hard-requires:
#   required = {"winner", "match_score", "reasoning"}  (L~368)
#   reads result["winner"], result["match_score"], result["reasoning"]
CODE_REQUIRED = {"winner", "match_score", "reasoning"}


def main() -> int:
    s = _match_schema()
    ok = True

    def check(cond, msg):
        nonlocal ok
        mark = "OK  " if cond else "FAIL"
        print(f"  [{mark}] {msg}")
        if not cond:
            ok = False

    print("[lab66b] m07 _match_schema() structural assert")

    check(s.get("type") == "OBJECT", f"top-level type == OBJECT (got {s.get('type')!r})")

    props = s.get("properties", {})
    req = set(s.get("required", []))

    # required in schema == what the code reads
    check(req == CODE_REQUIRED,
          f"schema.required == code-required {sorted(CODE_REQUIRED)} (got {sorted(req)})")

    # every required field must be declared in properties
    check(req <= set(props.keys()),
          f"all required fields present in properties (missing: {sorted(req - set(props.keys()))})")

    # types match the code's expectations
    check(props.get("winner", {}).get("type") == "STRING", "winner: STRING")
    check(props.get("match_score", {}).get("type") == "INTEGER",
          "match_score: INTEGER (code does int(result['match_score']))")
    check(props.get("reasoning", {}).get("type") == "STRING",
          "reasoning: STRING (code does str(result['reasoning']))")

    # all declared types are UPPERCASE (Gemini style, m03 model-citizen)
    for name, spec in props.items():
        t = spec.get("type")
        check(t in UPPER, f"{name}.type is UPPERCASE Gemini type (got {t!r})")

    print(f"[lab66b] {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
