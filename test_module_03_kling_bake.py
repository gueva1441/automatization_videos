"""Tests del bake §Kling en m03 (HANDOFF_80 §5). Standalone: python test_module_03_kling_bake.py
Sin red fal / sin keys: mockea _call_with_validation_retry y fuerza api.image_engine.
"""
import os, sys, importlib.util, subprocess, tempfile

sys.path.insert(0, os.path.join(os.getcwd(), "script_engine"))
import m03_visual as m
from config import api

FAILS = []
def check(name, cond, extra=""):
    print(("  OK  " if cond else "  XX  ") + name + (("  | " + extra) if extra and not cond else ""))
    if not cond:
        FAILS.append(name)

# ---- fixture común ----
NARR = ("Un hombre libre caminaba al amanecer por el muelle. "
        "La ciudad dormia bajo una niebla espesa. "
        "Los muros de ladrillo guardaban un secreto antiguo.")
ANCHORS = [
    "Un hombre libre caminaba al amanecer por el muelle.",
    "La ciudad dormia bajo una niebla espesa.",
    "Los muros de ladrillo guardaban un secreto antiguo.",
]
CAP = {"chapter_number": 3, "role": "development", "title": "El muelle"}
PLAN = {"anchors": [{"anchor": a} for a in ANCHORS]}

def kling_items():
    # items "del LLM" válidos para el path kling (English, sin nombres propios, sin vertical)
    prompts = [
        "Wide horizontal composition. A free African-American dockworker in his forties at dawn, "
        "linen shirt and canvas trousers, walking along weathered timber piers, mist over the harbor.",
        "Extreme wide shot of a period brick city sleeping under thick fog, empty cobblestone streets, "
        "gas lamps barely glowing, oppressive silence.",
        "Medium shot of an old brick wall, worn mortar and iron fittings, a single shaft of pale light, "
        "the surface plain and weathered.",
    ]
    scales = ["wide", "extreme_wide", "medium"]
    lights = ["day", "night", "night"]
    return [{"prompt": p, "subject_ref": "main_subject", "emotional_rank": r,
             "shot_scale": s, "light_mode": l, "narration_anchor": a,
             "has_human_subject": True}
            for p, r, s, l, a in zip(prompts, ["R1", "R2", "R3"], scales, lights, ANCHORS)]

# ════════ TEST 5.5 — tail dialed ════════
print("[5.5] tail dialed")
check("anti_plastic_dial(close,human)==moderate", m.anti_plastic_dial("close", True) == "moderate")
check("anti_plastic_dial(medium,human)==moderate", m.anti_plastic_dial("medium", True) == "moderate")
check("anti_plastic_dial(wide,human)==strong", m.anti_plastic_dial("wide", True) == "strong")
check("anti_plastic_dial(extreme_wide,human)==strong", m.anti_plastic_dial("extreme_wide", True) == "strong")
check("anti_plastic_dial(close,FACELESS)==strong", m.anti_plastic_dial("close", False) == "strong")    # B-QA-1
check("anti_plastic_dial(medium,FACELESS)==strong", m.anti_plastic_dial("medium", False) == "strong")  # B-QA-1
check("pick_tail(night,moderate)==TAIL_NIGHT_MOD", m.pick_tail("night", "moderate") == m.TAIL_NIGHT_MOD)
check("pick_tail(night,strong)==TAIL_NIGHT_STRONG", m.pick_tail("night", "strong") == m.TAIL_NIGHT_STRONG)
check("pick_tail(day,moderate)==TAIL_DAY_MOD", m.pick_tail("day", "moderate") == m.TAIL_DAY_MOD)
check("pick_tail(golden,_)==TAIL_GOLDEN", m.pick_tail("golden", "strong") == m.TAIL_GOLDEN
      and m.pick_tail("golden", "moderate") == m.TAIL_GOLDEN)

# ════════ TEST 5.3 — schema Kling ════════
print("[5.3] schema Kling")
sc = m._kling_step2_schema(4)
props = sc["items"]["properties"]
req = sc["items"]["required"]
check("6 campos requeridos", set(req) == {"prompt", "subject_ref", "emotional_rank", "shot_scale", "light_mode", "has_human_subject"}, str(req))
check("light_mode enum incluye golden", "golden" in props["light_mode"]["enum"])
check("shot_scale enum 5 valores",
      set(props["shot_scale"]["enum"]) == {"extreme_wide", "wide", "medium", "close", "detail"})
check("minItems/maxItems == n", sc["minItems"] == 4 and sc["maxItems"] == 4)

# ════════ TEST 5.4 — validador Kling carga campos + rechaza enum inválido ════════
print("[5.4] _validate_kling_cap carga shot_scale/light_mode + rechaza enums")
out = m._validate_kling_cap({"image_prompts": kling_items()}, NARR, 3, 3)
norm = out["image_prompts"]
check("normalized tiene shot_scale", all("shot_scale" in it for it in norm))
check("normalized tiene light_mode", all("light_mode" in it for it in norm))
check("valores cargados correctos", norm[0]["shot_scale"] == "wide" and norm[1]["light_mode"] == "night")
check("normalized tiene has_human_subject", all("has_human_subject" in it for it in norm))
badh = kling_items(); badh[0]["has_human_subject"] = "yes"
try:
    m._validate_kling_cap({"image_prompts": badh}, NARR, 3, 3); raisedh = False
except m.VisualValidationError: raisedh = True
check("rechaza has_human_subject no-bool", raisedh)
# rechazo enum
bad = kling_items(); bad[0]["shot_scale"] = "panoramic"
try:
    m._validate_kling_cap({"image_prompts": bad}, NARR, 3, 3); raised = False
except m.VisualValidationError: raised = True
check("rechaza shot_scale fuera de enum", raised)
bad2 = kling_items(); bad2[1]["light_mode"] = "dusk"
try:
    m._validate_kling_cap({"image_prompts": bad2}, NARR, 3, 3); raised2 = False
except m.VisualValidationError: raised2 = True
check("rechaza light_mode fuera de enum", raised2)

# ════════ TEST 5.8 — budget ════════
print("[5.8] budget Kling")
budget = m.KLING_PROMPT_MAX_CHARS - m.LONGEST_TAIL_LEN
over = kling_items()
# prompt de budget+1 chars que sigue conteniendo el anchor (substring) para no fallar por otra razón
filler = ANCHORS[0] + " " + ("x" * (budget + 1 - len(ANCHORS[0]) - 1))
over[0]["prompt"] = filler
check("len fixture == budget+1", len(filler) == budget + 1, f"len={len(filler)} budget={budget}")
try:
    m._validate_kling_cap({"image_prompts": over}, NARR, 3, 3); raised3 = False
except m.VisualValidationError: raised3 = True
check("raw kling de budget+1 dispara VisualValidationError", raised3)
# y budget exacto pasa (mismo prompt -1 char)
okp = kling_items(); okp[0]["prompt"] = ANCHORS[0] + " " + ("x" * (budget - len(ANCHORS[0]) - 1))
try:
    m._validate_kling_cap({"image_prompts": okp}, NARR, 3, 3); ok_pass = True
except m.VisualValidationError as e: ok_pass = False
check("raw kling de budget exacto pasa", ok_pass)

# ════════ TEST 5.6 — append Kling (fórmula del harness) ════════
print("[5.6] append Kling")
it = norm[0]  # wide/day -> TAIL_DAY_STRONG
raw = it["prompt"].strip()
dial = m.anti_plastic_dial(it["shot_scale"], it["has_human_subject"]); tail = m.pick_tail(it["light_mode"], dial)
prompt_final = f"{raw.rstrip('.')}. {tail}"[:m.KLING_PROMPT_MAX_CHARS]
check("append = raw.rstrip('.') + '. ' + tail", prompt_final == f"{raw.rstrip('.')}. {tail}"[:m.KLING_PROMPT_MAX_CHARS])
check("termina con el tail correcto (wide/day=DAY_STRONG)", prompt_final.endswith(m.TAIL_DAY_STRONG))
check("len <= KLING_PROMPT_MAX_CHARS", len(prompt_final) <= m.KLING_PROMPT_MAX_CHARS)
check("raw_llm_prompt sería el raw sin tail", m.TAIL_DAY_STRONG not in raw)

# ════════ TEST 5.7 — no proper names / no vertical ════════
print("[5.7] no text leakage / no vertical en fixture kling")
banned = ("vertical", "tiktok", "shorts", "16:9")
leak_ok = True; vert_ok = True
for i, it in enumerate(kling_items(), 1):
    try:
        m._validate_no_text_leakage(it["prompt"], f"fix #{i}")
    except m.VisualValidationError:
        leak_ok = False
    if any(b in it["prompt"].lower() for b in banned):
        vert_ok = False
check("_validate_no_text_leakage pasa en fixture kling", leak_ok)
check("ningun prompt kling contiene vertical/TikTok/Shorts/16:9", vert_ok)

# ════════ TEST 5.1 / 5.2 — dispatch (mock _call_with_validation_retry) ════════
print("[5.1/5.2] dispatch por engine")
captured = {}
_orig = m._call_with_validation_retry
def _spy(prompt, validator, cap_number, system_instruction=None, response_schema=None):
    captured["prompt"] = prompt
    captured["system_instruction"] = system_instruction
    captured["response_schema"] = response_schema
    captured["validator"] = validator
    return {"image_prompts": []}
m._call_with_validation_retry = _spy
try:
    # KLING
    m.api.image_engine = "kling"
    m._render_prompts_flux({}, CAP, NARR, PLAN, 3)
    check("kling -> system_instruction = _KLING", captured["system_instruction"] is m.SYSTEM_INSTRUCTION_VISUAL_KLING)
    check("kling -> response_schema = _kling_step2_schema", captured["response_schema"] == m._kling_step2_schema(3))
    # el validator kling acepta items con shot_scale/light_mode
    vk = captured["validator"]
    okv = vk({"image_prompts": kling_items()})
    check("kling validator carga shot_scale", all("shot_scale" in x for x in okv["image_prompts"]))

    # FLUX
    m.api.image_engine = "flux"
    m._render_prompts_flux({}, CAP, NARR, PLAN, 3)
    check("flux -> system_instruction = SYSTEM_INSTRUCTION_VISUAL", captured["system_instruction"] is m.SYSTEM_INSTRUCTION_VISUAL)
    check("flux -> response_schema = _flux_step2_schema", captured["response_schema"] == m._flux_step2_schema(3))

    # 5.2 BYTE-IDENTICO: el user-prompt flux (is_kling=False) == versión db2bae3
    print("[5.2] byte-identico Flux (vs db2bae3) — EL QUE NO PUEDE FALLAR")
    old_src = subprocess.check_output(["git", "show", "db2bae3:script_engine/m03_visual.py"]).decode("utf-8")
    tmp = os.path.join(os.getcwd(), "script_engine", "_m03_old_snapshot.py")
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(old_src)
    try:
        spec = importlib.util.spec_from_file_location("_m03_old_snapshot", tmp)
        old = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(old)
        new_flux = m._build_flux_prompt_step2({}, CAP, NARR, ANCHORS, is_kling=False)
        old_flux = old._build_flux_prompt_step2({}, CAP, NARR, ANCHORS)
        check("_build_flux_prompt_step2 (is_kling=False) BYTE-IDENTICO a db2bae3", new_flux == old_flux,
              f"len new={len(new_flux)} old={len(old_flux)}")
    finally:
        os.remove(tmp)
finally:
    m._call_with_validation_retry = _orig
    m.api.image_engine = "kling"   # restaurar default prod

print("\n" + ("ALL GREEN" if not FAILS else f"FAILS ({len(FAILS)}): " + ", ".join(FAILS)))
sys.exit(1 if FAILS else 0)
