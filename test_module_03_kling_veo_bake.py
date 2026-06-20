"""Tests del bake §Kling path VEO (HANDOFF B80-1 §5). python test_module_03_kling_veo_bake.py
Sin red / sin keys: mockea _call_with_validation_retry y fuerza api.image_engine.
"""
import os, sys, importlib.util, subprocess, inspect

sys.path.insert(0, os.path.join(os.getcwd(), "script_engine"))
import m03_visual as m
from config import api

FAILS = []
def check(name, cond, extra=""):
    print(("  OK  " if cond else "  XX  ") + name + (("  | " + extra) if (extra and not cond) else ""))
    if not cond:
        FAILS.append(name)

# ---- fixture veo (veo_position="start": veo_anchor primero, supps después) ----
VEO_ANCHOR = "Una torre de ladrillo se alzaba sobre el patio al amanecer."
SUPPS = [
    "Los muros guardaban marcas de un siglo de abandono.",
    "Un pasillo angosto se perdia en la penumbra.",
    "Cadenas oxidadas colgaban de un gancho de hierro.",
    "El viento arrastraba polvo por el patio vacio.",
]
NARR = VEO_ANCHOR + " " + " ".join(SUPPS)
CAP = {"chapter_number": 1, "role": "hook", "title": "El gancho", "bullets": ["b1", "b2"]}
TOPIC = {}
PLAN = {"veo_anchor": {"anchor": VEO_ANCHOR},
        "supplementals": [{"anchor": s} for s in SUPPS]}

EN = ("A wide establishing shot of a tall weathered brick tower rising over an empty courtyard at "
      "dawn, period ironwork and worn stone, cold pale light, oppressive scale, documentary realism.")  # ~150 chars
def supp_items(shot="wide", light="night"):
    return [{"prompt": EN, "shot_scale": shot, "light_mode": light, "narration_anchor": s, "has_human_subject": True} for s in SUPPS]
def parsed_ok():
    return {"image_prompt": EN, "video_prompt": EN, "subject_ref": "main_subject",
            "narration_anchor": VEO_ANCHOR, "supplemental_image_prompts": supp_items()}

# ════════ TEST 2 — schema ════════
print("[2] schema veo-kling")
sc = m._veo_kling_step2_schema(4)
img_props = sc["properties"]["image_prompt"]
check("image_prompt SIN shot_scale/light_mode", "properties" not in img_props or
      not ({"shot_scale", "light_mode"} & set(img_props.get("properties", {}))))
supp_props = sc["properties"]["supplemental_image_prompts"]["items"]["properties"]
check("supp tiene shot_scale + light_mode", "shot_scale" in supp_props and "light_mode" in supp_props)
check("supp required = prompt/shot_scale/light_mode/has_human_subject",
      set(sc["properties"]["supplemental_image_prompts"]["items"]["required"]) == {"prompt", "shot_scale", "light_mode", "has_human_subject"})

# ════════ TEST 4 — validador kling ════════
print("[4] _validate_veo_kling_cap")
out = m._validate_veo_kling_cap(parsed_ok(), NARR, 1, "start")
check("normalized supps cargan shot_scale/light_mode",
      all("shot_scale" in s and "light_mode" in s for s in out["supplemental_image_prompts"]))
check("normalized supps cargan has_human_subject", all("has_human_subject" in s for s in out["supplemental_image_prompts"]))
check("shape sagrado intacto", set(out) == {"chapter_number", "image_prompt", "video_prompt", "subject_ref",
                                            "art_profile", "narration_anchor", "veo_position", "supplemental_image_prompts"})
# image_prompt budget = KLING_PROMPT_MAX_CHARS (2501 falla, 2500 pasa)
p = parsed_ok(); p["image_prompt"] = "A " + ("x" * (m.KLING_PROMPT_MAX_CHARS - 1))  # 2501
try: m._validate_veo_kling_cap(p, NARR, 1, "start"); r = False
except m.VisualValidationError: r = True
check("image_prompt > KLING_MAX dispara", r, f"len={len(p['image_prompt'])}")
p2 = parsed_ok(); p2["image_prompt"] = "A " + ("x" * (m.KLING_PROMPT_MAX_CHARS - 2))  # 2500
try: m._validate_veo_kling_cap(p2, NARR, 1, "start"); ok1 = True
except m.VisualValidationError: ok1 = False
check("image_prompt == KLING_MAX pasa", ok1)
# supp budget = KLING - LONGEST_TAIL
supp_budget = m.KLING_PROMPT_MAX_CHARS - m.LONGEST_TAIL_LEN
p3 = parsed_ok(); p3["supplemental_image_prompts"][0]["prompt"] = "A " + ("x" * (supp_budget - 1))  # budget+1
try: m._validate_veo_kling_cap(p3, NARR, 1, "start"); r3 = False
except m.VisualValidationError: r3 = True
check("supp > (KLING - tail) dispara", r3, f"len={len(p3['supplemental_image_prompts'][0]['prompt'])} budget={supp_budget}")
# enum inválido en supp
p4 = parsed_ok(); p4["supplemental_image_prompts"][1]["shot_scale"] = "panoramic"
try: m._validate_veo_kling_cap(p4, NARR, 1, "start"); r4 = False
except m.VisualValidationError: r4 = True
check("supp shot_scale inválido dispara", r4)
p5 = parsed_ok(); p5["supplemental_image_prompts"][2]["light_mode"] = "dusk"
try: m._validate_veo_kling_cap(p5, NARR, 1, "start"); r5 = False
except m.VisualValidationError: r5 = True
check("supp light_mode inválido dispara", r5)
# video_prompt longitud Veo de hoy (PROMPT_MAX_CHARS=700): 800 chars falla
p6 = parsed_ok(); p6["video_prompt"] = "A " + ("x" * 800)
try: m._validate_veo_kling_cap(p6, NARR, 1, "start"); r6 = False
except m.VisualValidationError: r6 = True
check("video_prompt > longitud Veo de hoy dispara", r6)

# ════════ TEST 5 — append (fórmula del harness; solo supps, image_prompt SIN tail) ════════
print("[5] append veo kling")
s0 = out["supplemental_image_prompts"][0]  # wide/night -> TAIL_NIGHT_STRONG
raw = s0["prompt"].strip()
tail = m.pick_tail(s0["light_mode"], m.anti_plastic_dial(s0["shot_scale"], s0["has_human_subject"]))
prompt_final = f"{raw.rstrip('.')}. {tail}"[:m.KLING_PROMPT_MAX_CHARS]
check("supp termina en TAIL_* (wide/night=NIGHT_STRONG)", prompt_final.endswith(m.TAIL_NIGHT_STRONG))
check("len <= KLING_PROMPT_MAX_CHARS", len(prompt_final) <= m.KLING_PROMPT_MAX_CHARS)
check("image_prompt NO recibe tail (sin TAIL_* en el raw)", all(t not in out["image_prompt"] for t in
      (m.TAIL_NIGHT_STRONG, m.TAIL_NIGHT_MOD, m.TAIL_DAY_STRONG, m.TAIL_DAY_MOD, m.TAIL_GOLDEN)))

# ════════ TEST 3 / 6 / dispatch — mock _call_with_validation_retry ════════
print("[3/6] dispatch + build is_kling + no-leak")
captured = {}
_orig = m._call_with_validation_retry
def _spy(prompt, validator, cap_number, system_instruction=None, response_schema=None):
    captured.update(prompt=prompt, system_instruction=system_instruction,
                    response_schema=response_schema, validator=validator)
    return {"_sentinel": True}
m._call_with_validation_retry = _spy
try:
    # KLING
    m.api.image_engine = "kling"
    m._render_prompts_veo(TOPIC, CAP, NARR, PLAN, "start", 1)
    kp = captured["prompt"]
    check("kling build NO contiene _build_rules_block", m._build_rules_block() not in kp)
    check("kling build NO contiene _VEO_EXAMPLES", m._VEO_EXAMPLES not in kp)
    check("kling build NO contiene _VEO_IMG_VIDEO_SUBJECT_SPEC", m._VEO_IMG_VIDEO_SUBJECT_SPEC not in kp)
    check("kling build SÍ contiene _VEO_VIDEO_PROMPT_STRUCT", m._VEO_VIDEO_PROMPT_STRUCT in kp)
    check("kling system_instruction = _KLING", captured["system_instruction"] is m.SYSTEM_INSTRUCTION_VISUAL_KLING)
    check("kling response_schema = _veo_kling_step2_schema", captured["response_schema"] == m._veo_kling_step2_schema(4))
    vk = captured["validator"]
    okv = vk(parsed_ok())
    check("kling validator carga shot_scale en supps", all("shot_scale" in s for s in okv["supplemental_image_prompts"]))
    # no-leak corre sobre supps (kling): un supp con leak dispara
    leak = parsed_ok(); leak["supplemental_image_prompts"][0]["prompt"] = "A wall with the name written in large letters on a sign"
    try: vk(leak); rl = False
    except m.VisualValidationError: rl = True
    check("no-leak corre sobre supps (kling)", rl)

    # FLUX
    m.api.image_engine = "flux"
    m._render_prompts_veo(TOPIC, CAP, NARR, PLAN, "start", 1)
    check("flux system_instruction = SYSTEM_INSTRUCTION_VISUAL", captured["system_instruction"] is m.SYSTEM_INSTRUCTION_VISUAL)
    check("flux response_schema = _veo_step2_schema", captured["response_schema"] == m._veo_step2_schema(4))
    # no-leak corre sobre supps (flux): mismo wiring
    vf = captured["validator"]
    leak_f = {"image_prompt": EN, "video_prompt": EN, "subject_ref": "main_subject",
              "supplemental_image_prompts": [{"prompt": "name engraved on a plaque with visible text"}] * 4}
    try: vf(leak_f); rlf = False
    except m.VisualValidationError: rlf = True
    check("no-leak corre sobre supps (flux)", rlf)

    # ════════ TEST 1 — byte-idéntico veo flux vs 085d05c (EL QUE NO PUEDE FALLAR) ════════
    print("[1] byte-idéntico veo FLUX (vs 085d05c)")
    old_src = subprocess.check_output(["git", "show", "085d05c:script_engine/m03_visual.py"]).decode("utf-8")
    tmp = os.path.join(os.getcwd(), "script_engine", "_m03_old_veo_snapshot.py")
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(old_src)
    try:
        spec = importlib.util.spec_from_file_location("_m03_old_veo_snapshot", tmp)
        old = importlib.util.module_from_spec(spec); spec.loader.exec_module(old)
        new_veo = m._build_veo_prompt_step2(TOPIC, CAP, NARR, VEO_ANCHOR, SUPPS, "start", is_kling=False)
        old_veo = old._build_veo_prompt_step2(TOPIC, CAP, NARR, VEO_ANCHOR, SUPPS, "start")
        check("_build_veo_prompt_step2(is_kling=False) BYTE-IDÉNTICO a 085d05c", new_veo == old_veo,
              f"len new={len(new_veo)} old={len(old_veo)}")
        # _validate_veo_cap output idéntico
        nv = m._validate_veo_cap(parsed_ok(), NARR, 1, "start")
        ov = old._validate_veo_cap(parsed_ok(), NARR, 1, "start")
        check("_validate_veo_cap output idéntico (flux)", nv == ov)
        # TEST 7 regresión: funciones flux/kling-flux byte-idénticas vs 085d05c
        print("[7] regresión: funciones flux intactas vs 085d05c")
        # _validate_kling_cap + _render_prompts_flux SACADOS: B-QA-1 (chat 86) los modifica a propósito.
        for fn in ["_validate_flux_cap", "_build_flux_prompt_step2",
                   "_validate_veo_cap", "_veo_step2_schema"]:
            same = inspect.getsource(getattr(m, fn)) == inspect.getsource(getattr(old, fn))
            check(f"{fn} byte-idéntico", same)
    finally:
        os.remove(tmp)
finally:
    m._call_with_validation_retry = _orig
    m.api.image_engine = "kling"

print("\n" + ("ALL GREEN" if not FAILS else f"FAILS ({len(FAILS)}): " + ", ".join(FAILS)))
sys.exit(1 if FAILS else 0)
