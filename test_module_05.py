"""
test_module_05.py — Tests aislados para m05 (juez visual).

Ejecuta:
    python test_module_05.py

Sin LLM, sin disco, sin red. Pura lógica determinística + mocks de Flash.
Cubre Pieza 1 (Stage 1), Pieza 2 (Stage 2 con mock), Pieza 3 (validación dura).
"""

import os
import sys
import types

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


# ════════════════════════════════════════════════════════════════════════
#  MOCKS — gemini_helpers y art_profiles (si no están disponibles)
# ════════════════════════════════════════════════════════════════════════

try:
    import gemini_helpers  # noqa: F401
except ImportError:
    fake_gemini = types.ModuleType("gemini_helpers")

    def _default_fake_flash(prompt):
        return {"chapter_id": 1, "verdict": "PASS", "issues": []}

    fake_gemini.call_flash_json = _default_fake_flash
    sys.modules["gemini_helpers"] = fake_gemini

try:
    import art_profiles  # noqa: F401
except ImportError:
    fake_art = types.ModuleType("art_profiles")
    fake_art.ART_PROFILES = {
        "MARITIME_EXTERIOR": "Cinematic maritime documentary, rich steel-blue palette",
        "INDUSTRIAL": "Cinematic industrial documentary photography, cold slate-blue",
        "SUBMARINE": "Cinematic submarine documentary, deep cold-cyan with red emergency lighting",
        "URBAN": "Cinematic urban nocturne photography, deep cyan and slate-grey palette",
    }
    fake_art.VALID_PROFILES = frozenset(fake_art.ART_PROFILES.keys())
    sys.modules["art_profiles"] = fake_art


from script_engine import m05_judge  # noqa: E402
import json as _json_test
import tempfile
from pathlib import Path

from script_engine.m05_judge import (  # noqa: E402
    COST_TABLE,
    M05ValidationError,
    SYSTEM_PROMPT_FIXED,
    _compute_global_fix_plan,
    _earliest_module,
    _extract_last_name,
    _global_verdict_emoji,
    _is_substring_match,
    _normalize_chapter_images,
    _normalize_text,
    build_chapter_prompt,
    build_chapter_validator,
    call_flash_for_chapter,
    detect_anachronism_visual,
    detect_name_leakage,
    detect_text_in_image,
    estimate_fix_cost,
    judge_topic,
    merge_stage1_stage2,
    render_report,
    stage1_predetect,
    validate_chapter_output,
    validate_root_cause,
)


# ════════════════════════════════════════════════════════════════════════
#  HELPERS DE TEST
# ════════════════════════════════════════════════════════════════════════

def _section(title):
    print(f"\n{'═' * 64}\n  {title}\n{'═' * 64}")


def _ok(msg):
    print(f"  ✅ {msg}")


def _assert(cond, msg):
    if cond:
        _ok(msg)
    else:
        print(f"  ❌ {msg}")
        raise AssertionError(msg)


def _assert_raises(error_cls, fn, msg, expected_substr=None):
    """Aserta que fn() levante error_cls. Opcionalmente que el mensaje contenga substr."""
    try:
        fn()
    except error_cls as e:
        if expected_substr and expected_substr not in str(e):
            print(f"  ❌ {msg} (raised but message lacks {expected_substr!r}: {e})")
            raise AssertionError(msg)
        _ok(msg)
        return
    except Exception as e:
        print(f"  ❌ {msg} (raised wrong type: {type(e).__name__}: {e})")
        raise AssertionError(msg)
    print(f"  ❌ {msg} (no exception raised)")
    raise AssertionError(msg)


def _set_fake_flash(fn):
    m05_judge.call_flash_json = fn


def _make_sequence_flash(*responses):
    state = {"i": 0}

    def _fake(prompt):
        idx = state["i"]
        state["i"] += 1
        if idx >= len(responses):
            raise RuntimeError(f"Mock exhausted: {idx + 1}-th call sin respuesta preparada")
        return responses[idx]

    return _fake


def _make_valid_issue(image_index=1, chapter_id=1, issue_n=1, **overrides):
    """Construye un issue válido para tests, con overrides opcionales."""
    base = {
        "issue_id": f"cap{chapter_id}_img{image_index}_issue{issue_n}",
        "image_index": image_index,
        "anchor_excerpt": "the keeper studied logbook entries that night",
        "category": "anchor_mismatch",
        "severity": "medium",
        "what_happened": "anchor and image diverge in subject",
        "why_happened": "prompt drifted to atmosphere shot",
        "how_to_fix": "rewrite prompt to depict the keeper studying entries",
        "proposed_root_cause_module": "m03",
        "proposed_regex_pattern": None,
    }
    base.update(overrides)
    return base


def _make_valid_images():
    """Imgs estándar para tests con anchors realistas."""
    return [
        {
            "image_index": 1,
            "prompt": "x",
            "narration_anchor": "the keeper studied logbook entries that night",
        },
        {
            "image_index": 2,
            "prompt": "y",
            "narration_anchor": "rain fell silently on the rocky cliffs below",
        },
    ]


# ════════════════════════════════════════════════════════════════════════
#  TESTS — PIEZA 1
# ════════════════════════════════════════════════════════════════════════

def test_normalize_text():
    _section("HELPER — _normalize_text")
    _assert(_normalize_text("HELLO") == "hello", "uppercase → lowercase")
    _assert(_normalize_text("Café") == "cafe", "diacritic decompuesto (é → e)")
    _assert(_normalize_text("Müller") == "muller", "umlaut decompuesto")
    _assert(_normalize_text("") == "", "string vacío")
    _assert(_normalize_text(None) == "", "None handled sin romper")


def test_extract_last_name():
    _section("HELPER — _extract_last_name")
    _assert(_extract_last_name("Leonid Kulik") == "kulik", "'Leonid Kulik' → 'kulik'")
    _assert(_extract_last_name("Wernher von Braun") == "von braun",
            "'Wernher von Braun' → 'von braun' (1 partícula)")
    _assert(_extract_last_name("Maria de la Cruz") == "de la cruz",
            "'Maria de la Cruz' → 'de la cruz' (2 partículas)")
    _assert(_extract_last_name("Bach") == "bach", "'Bach' → 'bach' (1 solo token)")
    _assert(_extract_last_name("") == "", "string vacío → ''")
    _assert(_extract_last_name("  Slattery  ") == "slattery", "whitespace stripped")
    _assert(_extract_last_name("Pliny the Younger") == "younger",
            "'the' NO es partícula → último token solo")


def test_detect_name_leakage():
    _section("STAGE 1 — detect_name_leakage")
    people = [{"name": "Leonid Kulik", "role": "scientist"}]

    hits = detect_name_leakage("Kulik examines a tree near the epicenter", people)
    _assert(len(hits) == 1 and hits[0]["matched_pattern"] == "kulik",
            "match por last_name 'Kulik'")

    hits = detect_name_leakage("Leonid Kulik examines the site", people)
    _assert(len(hits) == 1 and hits[0]["matched_pattern"] == "Leonid Kulik",
            "match por full_name (no se duplica con last_name)")

    hits = detect_name_leakage("a Russian scientist examines the site", people)
    _assert(hits == [], "sin mención literal → no hit")

    people_v = [{"name": "Wernher von Braun"}]
    hits = detect_name_leakage("a portrait of von Braun in his lab", people_v)
    _assert(len(hits) == 1 and hits[0]["matched_pattern"] == "von braun",
            "match por last_name compuesto 'von Braun'")

    people_smith = [{"name": "John Smith"}]
    hits = detect_name_leakage("a smith hammering iron at the forge", people_smith)
    _assert(hits == [], "'smith' en blacklist → skip last_name match")

    people_wu = [{"name": "Lin Wu"}]
    hits = detect_name_leakage("a man named Wu walks past the camera", people_wu)
    _assert(hits == [], "last_name <5 chars → skip")

    people_acc = [{"name": "Marie Curié"}]
    hits = detect_name_leakage("CURIE in her laboratory", people_acc)
    _assert(len(hits) == 1, "case-insensitive + diacrítico decompuesto matchea")

    hits = detect_name_leakage("a man named Kulikov reads a report", people)
    _assert(hits == [], "word boundary impide match de 'kulik' dentro de 'Kulikov'")

    people_multi = [{"name": "Leonid Kulik"}, {"name": "Vasily Surin"}]
    hits = detect_name_leakage("Kulik finds the tree, Surin takes notes", people_multi)
    matched = sorted(h["matched_pattern"] for h in hits)
    _assert(matched == ["kulik", "surin"], "2 personas en el prompt → 2 hits separados")

    _assert(detect_name_leakage("", people) == [], "prompt vacío → []")
    _assert(detect_name_leakage("anything", []) == [], "people vacío → []")
    _assert(detect_name_leakage("anything", [{"name": ""}]) == [],
            "person con name vacío → skip silencioso")


def test_detect_text_in_image():
    _section("STAGE 1 — detect_text_in_image")

    hits = detect_text_in_image("a stone marker reading 17 october at the entrance")
    _assert(len(hits) >= 1, "fecha '17 october' (minúsculas) detectada")

    hits = detect_text_in_image("with the words '17 October' inscribed")
    has_quoted = any("'17 October'" in h["matched_pattern"] for h in hits)
    has_date = any("17 October".lower() in h["matched_pattern"].lower() for h in hits)
    _assert(has_quoted or has_date, "Pompeya cap 6 — '17 October' detectado")

    hits = detect_text_in_image("a faded sign that reads 'No Trespassing'")
    _assert(any("'No Trespassing'" in h["matched_pattern"] for h in hits),
            "texto entre comillas simples")

    hits = detect_text_in_image('a poster declaring "danger ahead" hangs on the wall')
    _assert(any('"danger ahead"' in h["matched_pattern"] for h in hits),
            "texto entre comillas dobles")

    hits = detect_text_in_image("a stamp showing legible letters in dark ink")
    _assert(len(hits) >= 1, "'showing legible' detectado")

    hits = detect_text_in_image("the page had three letters written in faded ink")
    _assert(any("letters written" in h["matched_pattern"].lower() for h in hits),
            "'letters written' detectado")

    hits = detect_text_in_image("a portrait of an elderly woman by candlelight")
    _assert(hits == [], "prompt limpio → sin hits")
    _assert(detect_text_in_image("") == [], "prompt vacío → []")


def test_detect_anachronism_visual():
    _section("STAGE 1 — detect_anachronism_visual")
    blocklist = ["smartphones", "modern cars", "neon signs"]

    hits = detect_anachronism_visual("a Roman senator holding smartphones", blocklist)
    _assert(len(hits) == 1 and hits[0]["matched_pattern"] == "smartphones",
            "single-word anachronism detectado")

    hits = detect_anachronism_visual("a forum scene with modern cars passing", blocklist)
    _assert(len(hits) == 1 and hits[0]["matched_pattern"] == "modern cars",
            "multi-word anachronism detectado")

    _assert(detect_anachronism_visual("a Roman forum at sunset", []) == [],
            "blocklist vacío → sin hits")
    _assert(detect_anachronism_visual("a Roman forum at sunset", blocklist) == [],
            "blocklist sin matches → sin hits")
    _assert(detect_anachronism_visual("a neonatal ward", ["neon"]) == [],
            "word boundary impide match de 'neon' dentro de 'neonatal'")

    hits = detect_anachronism_visual("a Roman holding SMARTPHONES at the forum", blocklist)
    _assert(len(hits) == 1, "match case-insensitive en MAYÚSCULAS")


def test_stage1_predetect():
    _section("STAGE 1 — stage1_predetect (orquestadora)")
    topic_data = {
        "documented_people": [{"name": "Leonid Kulik"}],
        "anachronism_blocklist": ["smartphones"],
    }
    images = [
        {"image_index": 1, "prompt": "a Russian scientist by a fallen tree, somber light"},
        {"image_index": 2, "prompt": "Kulik examines smartphones near the epicenter"},
        {"image_index": 3, "prompt": "a stamp showing legible letters reading 'CLASSIFIED'"},
    ]
    pre = stage1_predetect(images, topic_data)

    _assert([h for h in pre if h["image_index"] == 1] == [], "img 1 limpia → 0 hits")
    cats_2 = sorted(h["category"] for h in pre if h["image_index"] == 2)
    _assert(cats_2 == ["anachronism_visual", "name_leakage"],
            f"img 2 → name_leakage + anachronism_visual (got {cats_2})")
    _assert(any(h["category"] == "text_in_image" for h in pre if h["image_index"] == 3),
            "img 3 → text_in_image detectado")

    images_with_empty = [
        {"image_index": 1, "prompt": ""},
        {"image_index": 2, "prompt": "Kulik on site"},
    ]
    pre_robust = stage1_predetect(images_with_empty, topic_data)
    _assert(all(h["image_index"] == 2 for h in pre_robust),
            "img con prompt vacío skipped sin romper")

    pre_partial = stage1_predetect(
        [{"image_index": 1, "prompt": "Kulik with smartphones"}],
        {"documented_people": [{"name": "Leonid Kulik"}]},
    )
    cats_partial = sorted(h["category"] for h in pre_partial)
    _assert(cats_partial == ["name_leakage"],
            "topic sin blocklist → solo name_leakage detectado")


# ════════════════════════════════════════════════════════════════════════
#  TESTS — PIEZA 2
# ════════════════════════════════════════════════════════════════════════

def test_system_prompt_loaded():
    _section("STAGE 2 — SYSTEM_PROMPT_FIXED carga al import")
    _assert(isinstance(SYSTEM_PROMPT_FIXED, str), "SYSTEM_PROMPT_FIXED es string")
    _assert(SYSTEM_PROMPT_FIXED.startswith("You are"),
            "arranca con 'You are a visual auditor...'")
    cats = [
        "name_leakage", "text_in_image", "era_mismatch_anchor",
        "era_textual_in_canon", "anchor_mismatch", "profile_incoherence",
        "anachronism_visual", "narration_unvisualizable", "other",
    ]
    for cat in cats:
        _assert(cat in SYSTEM_PROMPT_FIXED, f"contiene categoría '{cat}'")
    _assert("NON-NEGOTIABLE RULES" in SYSTEM_PROMPT_FIXED,
            "contiene sección 'NON-NEGOTIABLE RULES'")
    _assert("OUTPUT SCHEMA" in SYSTEM_PROMPT_FIXED,
            "contiene sección 'OUTPUT SCHEMA'")
    forbidden = ["tone:", "setting_era:", "mood:", "documented_persons"]
    for f in forbidden:
        _assert(f not in SYSTEM_PROMPT_FIXED,
                f"NO contiene '{f}' (limpieza tras edición)")


def test_build_chapter_prompt_basic():
    _section("STAGE 2 — build_chapter_prompt: shape correcto")
    images = [
        {"image_index": 1, "prompt": "an industrial pipe valve in cold blue light",
         "narration_anchor": "the valve was the last barrier"},
        {"image_index": 2, "prompt": "a man standing alone in the rain",
         "narration_anchor": "Slattery stood watch through the night"},
    ]
    profile = {"chapter_number": 3, "art_profile": "INDUSTRIAL",
               "rationale": "Industrial encaja con el ambiente del submarino."}
    topic_data = {
        "era_visual_canon": {"primary_decade": "1960s", "spans": "1960s Cold War era"},
        "documented_people": [{"name": "Francis Slattery", "role": "commander"}],
        "anachronism_blocklist": ["smartphones", "drones"],
    }
    prompt = build_chapter_prompt(3, images, profile, topic_data, [])

    _assert(isinstance(prompt, str), "retorna string")
    _assert(prompt.startswith("You are"), "arranca con system prompt")
    _assert("CHAPTER 3 CONTEXT" in prompt, "incluye chapter_id 3 en variable_block")
    _assert("'INDUSTRIAL'" in prompt, "incluye art_profile como repr")
    # Fix meta-bug: el catálogo completo de aesthetics se inyecta + warning
    _assert("ART_PROFILES CATALOG" in prompt, "catálogo completo inyectado")
    _assert("judge each image" in prompt and "ITS OWN image_art_profile" in prompt,
            "warning sobre image_art_profile vs cap default")
    _assert("DESERT:" in prompt and "scorched ochre" in prompt,
            "aesthetic de DESERT presente en catálogo")
    _assert("Cinematic industrial" in prompt, "incluye profile_description del catálogo")
    _assert("'1960s Cold War era'" in prompt, "incluye expected_era de spans")
    _assert("Francis Slattery" in prompt, "incluye documented_people")
    _assert("smartphones" in prompt, "incluye anachronism_blocklist")
    _assert("IMG 1:" in prompt and "IMG 2:" in prompt, "incluye 2 IMGs")
    _assert("'the valve was the last barrier'" in prompt, "incluye anchor de IMG 1")
    _assert("PRE_DETECTED_ISSUES (from Stage 1):" in prompt,
            "incluye encabezado pre_detected")
    _assert("\n[]\n" in prompt, "pre_detected vacío → '[]'")


def test_build_chapter_prompt_pre_detected_no_vacio():
    _section("STAGE 2 — build_chapter_prompt: pre_detected con hits")
    images = [{"image_index": 1, "prompt": "a stamp showing legible letters",
               "narration_anchor": "the document was sealed"}]
    profile = {"chapter_number": 1, "art_profile": "INDUSTRIAL", "rationale": "ok"}
    topic_data = {"era_visual_canon": {"primary_decade": "1960s"}}
    pre_detected = [
        {"image_index": 1, "category": "text_in_image",
         "matched_pattern": "showing legible"},
    ]
    prompt = build_chapter_prompt(1, images, profile, topic_data, pre_detected)
    _assert('"category": "text_in_image"' in prompt,
            "pre_detected serializado como JSON con quotes dobles")
    _assert('"matched_pattern": "showing legible"' in prompt,
            "matched_pattern preservado")


def test_build_chapter_prompt_topic_data_minimo():
    _section("STAGE 2 — build_chapter_prompt: topic_data parcial")
    images = [{"image_index": 1, "prompt": "anything", "narration_anchor": "anything"}]
    profile = {"chapter_number": 1, "art_profile": "INDUSTRIAL", "rationale": "ok"}
    prompt = build_chapter_prompt(1, images, profile, {}, [])
    _assert("'(unknown)'" in prompt,
            "expected_era fallback a '(unknown)' cuando no hay era_visual_canon")
    _assert("documented_people: []" in prompt,
            "documented_people vacío representado como []")
    _assert("anachronism_blocklist: []" in prompt,
            "anachronism_blocklist vacío representado como []")


def test_call_flash_for_chapter_happy_path():
    _section("STAGE 2 — call_flash_for_chapter: happy path (1 intento)")
    expected = {"chapter_id": 1, "verdict": "PASS", "issues": []}
    _set_fake_flash(_make_sequence_flash(expected))
    result = call_flash_for_chapter(
        1,
        [{"image_index": 1, "prompt": "x", "narration_anchor": "y"}],
        {"chapter_number": 1, "art_profile": "INDUSTRIAL", "rationale": "ok"},
        {"era_visual_canon": {"primary_decade": "1960s"}},
        [],
    )
    _assert(result == expected, "retorna el dict del mock al primer intento")


def test_call_flash_for_chapter_retry_then_success():
    _section("STAGE 2 — call_flash_for_chapter: 1 fallo → retry → éxito")
    bad = "not a dict"
    good = {"chapter_id": 1, "verdict": "PASS", "issues": []}
    _set_fake_flash(_make_sequence_flash(bad, good))
    result = call_flash_for_chapter(
        1,
        [{"image_index": 1, "prompt": "x", "narration_anchor": "y"}],
        {"chapter_number": 1, "art_profile": "INDUSTRIAL", "rationale": "ok"},
        {"era_visual_canon": {"primary_decade": "1960s"}},
        [],
    )
    _assert(result == good, "retorna el dict tras 1 retry exitoso")


def test_call_flash_for_chapter_three_failures_raise():
    _section("STAGE 2 — call_flash_for_chapter: 3 fallos → M05ValidationError")
    _set_fake_flash(_make_sequence_flash("g1", "g2", "g3"))
    raised = False
    try:
        call_flash_for_chapter(
            1,
            [{"image_index": 1, "prompt": "x", "narration_anchor": "y"}],
            {"chapter_number": 1, "art_profile": "INDUSTRIAL", "rationale": "ok"},
            {"era_visual_canon": {"primary_decade": "1960s"}},
            [],
        )
    except M05ValidationError as e:
        raised = True
        _assert("3 veces" in str(e), "mensaje incluye conteo de intentos exhaustos")
        _assert("cap 1" in str(e), "mensaje incluye chapter_id")
    _assert(raised, "M05ValidationError fue levantada")


def test_call_flash_validator_personalizado():
    _section("STAGE 2 — call_flash_for_chapter: validator_fn custom")
    response = {"chapter_id": 99, "verdict": "PASS", "issues": []}
    _set_fake_flash(_make_sequence_flash(response, response, response))

    def strict(parsed):
        if not isinstance(parsed, dict):
            raise M05ValidationError("not dict")
        if parsed.get("chapter_id") != 1:
            raise M05ValidationError(f"chapter_id esperado 1, llegó {parsed.get('chapter_id')}")
        return parsed

    raised = False
    try:
        call_flash_for_chapter(
            1,
            [{"image_index": 1, "prompt": "x", "narration_anchor": "y"}],
            {"chapter_number": 1, "art_profile": "INDUSTRIAL", "rationale": "ok"},
            {"era_visual_canon": {"primary_decade": "1960s"}},
            [],
            validator_fn=strict,
        )
    except M05ValidationError as e:
        raised = True
        _assert("chapter_id esperado 1" in str(e),
                "feedback custom propagado al error final")
    _assert(raised, "validator personalizado puede rechazar y forzar M05ValidationError")


# ════════════════════════════════════════════════════════════════════════
#  TESTS — PIEZA 3
# ════════════════════════════════════════════════════════════════════════

def test_is_substring_match():
    _section("PIEZA 3 — _is_substring_match (helper)")
    anchor = "the keeper studied logbook entries that night carefully"

    _assert(_is_substring_match("the keeper studied logbook entries", anchor),
            "substring exacto → True")
    _assert(_is_substring_match("STUDIED LOGBOOK ENTRIES", anchor),
            "case-insensitive → True")
    _assert(_is_substring_match("studied logb00k entries that night", anchor),
            "typo menor (1 char) cubre ≥85% del excerpt → True")
    _assert(not _is_substring_match("the alien spaceship landed", anchor),
            "totalmente diferente → False")
    _assert(not _is_substring_match("", anchor), "excerpt vacío → False")
    _assert(not _is_substring_match("anything", ""), "anchor vacío → False")


def test_validate_pass_valido():
    _section("PIEZA 3 — validate_chapter_output: PASS válido")
    images = _make_valid_images()
    parsed = {"chapter_id": 1, "verdict": "PASS", "issues": []}
    result = validate_chapter_output(parsed, 1, images)
    _assert(result == parsed, "PASS con issues vacíos pasa validación")


def test_validate_flag_valido_un_issue():
    _section("PIEZA 3 — validate_chapter_output: FLAG válido con 1 issue")
    images = _make_valid_images()
    parsed = {
        "chapter_id": 1, "verdict": "FLAG",
        "issues": [_make_valid_issue()],
    }
    result = validate_chapter_output(parsed, 1, images)
    _assert(result == parsed, "FLAG con 1 issue válido pasa validación")


def test_validate_flag_valido_multiples_issues():
    _section("PIEZA 3 — validate_chapter_output: FLAG con múltiples issues")
    images = _make_valid_images()
    parsed = {
        "chapter_id": 1, "verdict": "FLAG",
        "issues": [
            _make_valid_issue(image_index=1, issue_n=1),
            _make_valid_issue(image_index=2, issue_n=1, category="text_in_image",
                              severity="medium",
                              anchor_excerpt="rain fell silently on the rocky cliffs",
                              proposed_regex_pattern=r"\b(rain|drizzle)\b"),
        ],
    }
    result = validate_chapter_output(parsed, 1, images)
    _assert(result == parsed, "2 issues válidos en distintas imgs → ok")


def test_validate_no_dict():
    _section("PIEZA 3 — validate_chapter_output: input no-dict")
    _assert_raises(
        M05ValidationError,
        lambda: validate_chapter_output("not a dict", 1, _make_valid_images()),
        "string en vez de dict → error",
        expected_substr="must be a dict",
    )


def test_validate_chapter_id_mismatch():
    _section("PIEZA 3 — validate_chapter_output: chapter_id mismatch")
    images = _make_valid_images()
    parsed = {"chapter_id": 99, "verdict": "PASS", "issues": []}
    _assert_raises(
        M05ValidationError,
        lambda: validate_chapter_output(parsed, 1, images),
        "chapter_id 99 ≠ 1 → error",
        expected_substr="does not match expected",
    )


def test_validate_verdict_invalido():
    _section("PIEZA 3 — validate_chapter_output: verdict inválido")
    images = _make_valid_images()
    _assert_raises(
        M05ValidationError,
        lambda: validate_chapter_output(
            {"chapter_id": 1, "verdict": "MAYBE", "issues": []}, 1, images),
        "verdict 'MAYBE' fuera de enum → error",
        expected_substr="Invalid verdict",
    )


def test_validate_pass_con_issues():
    _section("PIEZA 3 — validate_chapter_output: PASS con issues no-vacío")
    images = _make_valid_images()
    parsed = {"chapter_id": 1, "verdict": "PASS",
              "issues": [_make_valid_issue()]}
    _assert_raises(
        M05ValidationError,
        lambda: validate_chapter_output(parsed, 1, images),
        "PASS con 1 issue → error",
        expected_substr="empty issues array",
    )


def test_validate_flag_sin_issues():
    _section("PIEZA 3 — validate_chapter_output: FLAG sin issues")
    images = _make_valid_images()
    parsed = {"chapter_id": 1, "verdict": "FLAG", "issues": []}
    _assert_raises(
        M05ValidationError,
        lambda: validate_chapter_output(parsed, 1, images),
        "FLAG con issues vacíos → error",
        expected_substr="at least one issue",
    )


def test_validate_issue_sin_field():
    _section("PIEZA 3 — validate issue: missing mandatory field")
    images = _make_valid_images()
    bad = _make_valid_issue()
    del bad["how_to_fix"]
    parsed = {"chapter_id": 1, "verdict": "FLAG", "issues": [bad]}
    _assert_raises(
        M05ValidationError,
        lambda: validate_chapter_output(parsed, 1, images),
        "issue sin 'how_to_fix' → error",
        expected_substr="missing mandatory field 'how_to_fix'",
    )


def test_validate_issue_category_invalida():
    _section("PIEZA 3 — validate issue: category fuera de enum")
    images = _make_valid_images()
    bad = _make_valid_issue(category="bug")
    parsed = {"chapter_id": 1, "verdict": "FLAG", "issues": [bad]}
    _assert_raises(
        M05ValidationError,
        lambda: validate_chapter_output(parsed, 1, images),
        "category='bug' fuera de enum → error",
        expected_substr="invalid category",
    )


def test_validate_issue_severity_invalida():
    _section("PIEZA 3 — validate issue: severity fuera de enum")
    images = _make_valid_images()
    bad = _make_valid_issue(severity="critical")
    parsed = {"chapter_id": 1, "verdict": "FLAG", "issues": [bad]}
    _assert_raises(
        M05ValidationError,
        lambda: validate_chapter_output(parsed, 1, images),
        "severity='critical' fuera de enum → error",
        expected_substr="invalid severity",
    )


def test_validate_issue_root_cause_invalida():
    _section("PIEZA 3 — validate issue: proposed_root_cause_module fuera de enum")
    images = _make_valid_images()
    bad = _make_valid_issue(proposed_root_cause_module="m99")
    parsed = {"chapter_id": 1, "verdict": "FLAG", "issues": [bad]}
    _assert_raises(
        M05ValidationError,
        lambda: validate_chapter_output(parsed, 1, images),
        "proposed_root_cause_module='m99' → error",
        expected_substr="invalid proposed_root_cause_module",
    )


def test_validate_issue_image_index_no_existe():
    _section("PIEZA 3 — validate issue: image_index no existe en cap")
    images = _make_valid_images()  # solo tiene 1 y 2
    bad = _make_valid_issue(
        image_index=99,
        issue_id="cap1_img99_issue1",
        anchor_excerpt="some text excerpt for testing",
    )
    parsed = {"chapter_id": 1, "verdict": "FLAG", "issues": [bad]}
    _assert_raises(
        M05ValidationError,
        lambda: validate_chapter_output(parsed, 1, images),
        "image_index=99 inexistente → error",
        expected_substr="does not exist in chapter",
    )


def test_validate_issue_id_malformado():
    _section("PIEZA 3 — validate issue: issue_id formato inválido")
    images = _make_valid_images()
    bad = _make_valid_issue(issue_id="bug_001")
    parsed = {"chapter_id": 1, "verdict": "FLAG", "issues": [bad]}
    _assert_raises(
        M05ValidationError,
        lambda: validate_chapter_output(parsed, 1, images),
        "issue_id 'bug_001' formato inválido → error",
        expected_substr="invalid issue_id format",
    )


def test_validate_issue_id_chapter_mismatch():
    _section("PIEZA 3 — validate issue: issue_id con cap número equivocado")
    images = _make_valid_images()
    # chapter_id real es 1, pero issue_id dice cap5
    bad = _make_valid_issue(issue_id="cap5_img1_issue1")
    parsed = {"chapter_id": 1, "verdict": "FLAG", "issues": [bad]}
    _assert_raises(
        M05ValidationError,
        lambda: validate_chapter_output(parsed, 1, images),
        "issue_id 'cap5_...' inconsistente con chapter_id=1 → error",
        expected_substr="inconsistent with",
    )


def test_validate_anchor_excerpt_no_substring():
    _section("PIEZA 3 — validate issue: anchor_excerpt no es substring del anchor")
    images = _make_valid_images()
    bad = _make_valid_issue(
        anchor_excerpt="something completely unrelated to the actual anchor"
    )
    parsed = {"chapter_id": 1, "verdict": "FLAG", "issues": [bad]}
    _assert_raises(
        M05ValidationError,
        lambda: validate_chapter_output(parsed, 1, images),
        "anchor_excerpt no relacionado → error",
        expected_substr="NOT a verbatim substring",
    )


def test_validate_anchor_excerpt_too_short():
    _section("PIEZA 3 — validate issue: anchor_excerpt demasiado corto")
    images = _make_valid_images()
    bad = _make_valid_issue(anchor_excerpt="too short")  # 2 palabras
    parsed = {"chapter_id": 1, "verdict": "FLAG", "issues": [bad]}
    _assert_raises(
        M05ValidationError,
        lambda: validate_chapter_output(parsed, 1, images),
        "anchor_excerpt con 2 palabras → error",
        expected_substr="too short",
    )


def test_validate_regex_pattern_invalido():
    _section("PIEZA 3 — validate issue: proposed_regex_pattern inválido")
    images = _make_valid_images()
    bad = _make_valid_issue(proposed_regex_pattern=r"[unclosed")
    parsed = {"chapter_id": 1, "verdict": "FLAG", "issues": [bad]}
    _assert_raises(
        M05ValidationError,
        lambda: validate_chapter_output(parsed, 1, images),
        "regex '[unclosed' no compila → error",
        expected_substr="not a valid",
    )


def test_validate_regex_pattern_null_ok():
    _section("PIEZA 3 — validate issue: proposed_regex_pattern null es ok")
    images = _make_valid_images()
    parsed = {"chapter_id": 1, "verdict": "FLAG",
              "issues": [_make_valid_issue(proposed_regex_pattern=None)]}
    result = validate_chapter_output(parsed, 1, images)
    _assert(result == parsed, "proposed_regex_pattern=None → válido")


def test_validate_string_field_vacio():
    _section("PIEZA 3 — validate issue: campo narrativo vacío")
    images = _make_valid_images()
    bad = _make_valid_issue(why_happened="")
    parsed = {"chapter_id": 1, "verdict": "FLAG", "issues": [bad]}
    _assert_raises(
        M05ValidationError,
        lambda: validate_chapter_output(parsed, 1, images),
        "why_happened vacío → error",
        expected_substr="non-empty string",
    )


def test_validate_anchor_excerpt_typo_menor_ok():
    _section("PIEZA 3 — validate issue: anchor_excerpt con typo menor pasa")
    images = _make_valid_images()
    # Anchor real: "the keeper studied logbook entries that night"
    # Excerpt con un typo de 1 char (l00gbook en vez de logbook)
    bad = _make_valid_issue(
        anchor_excerpt="the keeper studied l00gbook entries that night"
    )
    parsed = {"chapter_id": 1, "verdict": "FLAG", "issues": [bad]}
    result = validate_chapter_output(parsed, 1, images)
    _assert(result == parsed, "typo menor (≤15%) tolerado por SequenceMatcher")


def test_build_chapter_validator_integration():
    _section("PIEZA 3 — build_chapter_validator: integración con call_flash")
    images = _make_valid_images()
    profile = {"chapter_number": 1, "art_profile": "INDUSTRIAL", "rationale": "ok"}
    topic_data = {"era_visual_canon": {"primary_decade": "1960s"}}

    # 1. Mock devuelve un PASS válido al primer intento
    valid_response = {"chapter_id": 1, "verdict": "PASS", "issues": []}
    _set_fake_flash(_make_sequence_flash(valid_response))
    validator = build_chapter_validator(1, images)
    result = call_flash_for_chapter(1, images, profile, topic_data, [],
                                     validator_fn=validator)
    _assert(result == valid_response, "PASS válido pasa el validator de Pieza 3")

    # 2. Mock devuelve issue con category inválida → retry → válido
    bad_response = {
        "chapter_id": 1, "verdict": "FLAG",
        "issues": [_make_valid_issue(category="bug")],  # category inválida
    }
    fixed_response = {
        "chapter_id": 1, "verdict": "FLAG",
        "issues": [_make_valid_issue(category="anchor_mismatch")],
    }
    _set_fake_flash(_make_sequence_flash(bad_response, fixed_response))
    validator = build_chapter_validator(1, images)
    result = call_flash_for_chapter(1, images, profile, topic_data, [],
                                     validator_fn=validator)
    _assert(result == fixed_response,
            "category inválida → retry con feedback → fix válido")


# ════════════════════════════════════════════════════════════════════════
#  TESTS — PIEZA 4
# ════════════════════════════════════════════════════════════════════════

import io
import contextlib


def test_merge_sin_pre_detected():
    _section("PIEZA 4 — merge_stage1_stage2: sin pre_detected")
    s2 = [_make_valid_issue()]
    result = merge_stage1_stage2(s2, [], chapter_id=1)
    _assert(result == s2, "stage1 vacío → devuelve stage2 tal cual")


def test_merge_stage2_confirma_stage1():
    _section("PIEZA 4 — merge_stage1_stage2: Stage 2 confirma Stage 1")
    s2 = [_make_valid_issue(image_index=1, category="text_in_image")]
    s1 = [{
        "image_index": 1,
        "category": "text_in_image",
        "matched_pattern": "showing legible",
    }]
    # Capturar stdout para verificar que NO se imprime log de silenciado
    captured = io.StringIO()
    with contextlib.redirect_stdout(captured):
        result = merge_stage1_stage2(s2, s1, chapter_id=1)
    _assert(result == s2, "stage2 confirmó hit de stage1 → respetado")
    _assert("silenció" not in captured.getvalue(),
            "no se imprime log de silenciado cuando hay confirmación")


def test_merge_stage2_silencia_stage1():
    _section("PIEZA 4 — merge_stage1_stage2: Stage 2 silencia Stage 1")
    s2 = []  # LLM no flagó nada
    s1 = [{
        "image_index": 1,
        "category": "text_in_image",
        "matched_pattern": "showing legible",
    }]
    # Capturar stdout para verificar log de silenciado
    captured = io.StringIO()
    with contextlib.redirect_stdout(captured):
        result = merge_stage1_stage2(s2, s1, chapter_id=5)
    _assert(result == [], "stage2 silenció stage1 → falso positivo descartado")
    log = captured.getvalue()
    _assert("Stage 1 detectó" in log,
            "imprime log informativo cuando silencia")
    _assert("'text_in_image'" in log,
            "log incluye la categoría silenciada")
    _assert("img 1" in log,
            "log incluye image_index")
    _assert("cap 5" in log,
            "log incluye chapter_id si está")
    _assert("Regla 14" in log,
            "log menciona Regla 14 como justificación")


def test_merge_mixto_confirma_y_silencia():
    _section("PIEZA 4 — merge_stage1_stage2: confirma uno, silencia otro")
    s2 = [_make_valid_issue(image_index=2, category="anachronism_visual")]
    s1 = [
        # Img 1 detectado en s1 pero NO en s2 → silenciado
        {"image_index": 1, "category": "name_leakage", "matched_pattern": "Kulik"},
        # Img 2 detectado en s1 Y en s2 → confirmado
        {"image_index": 2, "category": "anachronism_visual", "matched_pattern": "smartphones"},
    ]
    captured = io.StringIO()
    with contextlib.redirect_stdout(captured):
        result = merge_stage1_stage2(s2, s1, chapter_id=3)
    _assert(result == s2, "resultado = stage2_issues")
    log = captured.getvalue()
    _assert("'name_leakage'" in log and "img 1" in log,
            "silenciado: name_leakage img 1 logueado")
    _assert("'anachronism_visual'" not in log or "silenció" not in log.split("anachronism_visual")[0],
            "confirmado: anachronism_visual NO se loguea como silenciado")


def test_merge_chapter_id_none():
    _section("PIEZA 4 — merge_stage1_stage2: chapter_id=None usa fallback")
    s2 = []
    s1 = [{"image_index": 1, "category": "name_leakage", "matched_pattern": "X"}]
    captured = io.StringIO()
    with contextlib.redirect_stdout(captured):
        merge_stage1_stage2(s2, s1, chapter_id=None)
    _assert("cap ?" in captured.getvalue(),
            "log usa 'cap ?' cuando chapter_id es None")


def test_validate_root_cause_coinciden():
    _section("PIEZA 4 — validate_root_cause: LLM coincide con heurística")
    issue = _make_valid_issue(
        category="text_in_image",
        proposed_root_cause_module="m03",  # heurística dice m03
    )
    result = validate_root_cause(issue)
    _assert(result["root_cause_conflict"] is False,
            "text_in_image + m03 → no conflict")
    _assert("heuristic_root_cause_module" not in result,
            "no se agrega heuristic field cuando no hay conflicto")


def test_validate_root_cause_difieren():
    _section("PIEZA 4 — validate_root_cause: LLM difiere de heurística")
    issue = _make_valid_issue(
        category="text_in_image",  # heurística dice m03
        proposed_root_cause_module="m00",  # LLM dice m00
    )
    result = validate_root_cause(issue)
    _assert(result["root_cause_conflict"] is True,
            "text_in_image + m00 → CONFLICT")
    _assert(result["heuristic_root_cause_module"] == "m03",
            "heuristic_root_cause_module='m03' agregado")
    _assert(result["proposed_root_cause_module"] == "m00",
            "proposed_root_cause_module original preservado")


def test_validate_root_cause_other():
    _section("PIEZA 4 — validate_root_cause: category='other'")
    # Para 'other' la heurística devuelve None → LLM tiene autoridad
    issue = _make_valid_issue(
        category="other",
        proposed_root_cause_module="m01b",  # cualquier valor del enum
    )
    result = validate_root_cause(issue)
    _assert(result["root_cause_conflict"] is False,
            "category='other' → no conflict (LLM tiene autoridad)")
    _assert("heuristic_root_cause_module" not in result,
            "no se agrega heuristic field para 'other'")


def test_validate_root_cause_categoria_desconocida():
    _section("PIEZA 4 — validate_root_cause: categoría no en heurística")
    # Caso defensivo: si get_root_cause devuelve None por categoría no mapeada
    # (no debería pasar tras Pieza 3 que valida enum, pero el código es defensivo)
    issue = {
        "category": "unmapped_category_for_test",
        "proposed_root_cause_module": "m03",
    }
    result = validate_root_cause(issue)
    _assert(result["root_cause_conflict"] is False,
            "heurística None → no conflict (defensivo)")


def test_validate_root_cause_es_in_place():
    _section("PIEZA 4 — validate_root_cause: mutación in-place")
    issue = _make_valid_issue(category="text_in_image",
                               proposed_root_cause_module="m03")
    result = validate_root_cause(issue)
    _assert(result is issue, "retorna el mismo objeto (mutación in-place)")


# ════════════════════════════════════════════════════════════════════════
#  TESTS — PIEZA 5
# ════════════════════════════════════════════════════════════════════════

def test_estimate_fix_cost_m03():
    _section("PIEZA 5 — estimate_fix_cost: causa raíz m03 (caso típico)")
    result = estimate_fix_cost("m03")
    # m03 no tiene downstream → cadena = [m03, m05]
    _assert(result["chain"] == ["m03", "m05"],
            f"chain = [m03, m05] (got {result['chain']})")
    # m03=0.012 + m05=0.005 = 0.017
    _assert(result["total_cost_usd"] == 0.017,
            f"total_cost_usd = 0.017 (got {result['total_cost_usd']})")
    # m03=2min + m05=1min = 3min
    _assert(result["total_minutes"] == 3,
            f"total_minutes = 3 (got {result['total_minutes']})")
    _assert(result["chain_str"] == "m03 → m05",
            f"chain_str legible (got {result['chain_str']!r})")


def test_estimate_fix_cost_m02():
    _section("PIEZA 5 — estimate_fix_cost: causa raíz m02")
    result = estimate_fix_cost("m02")
    # m02 → downstream=[m03] + m05
    _assert(result["chain"] == ["m02", "m03", "m05"],
            f"chain = [m02, m03, m05] (got {result['chain']})")
    # m02=0.001 + m03=0.012 + m05=0.005 = 0.018
    _assert(result["total_cost_usd"] == 0.018,
            f"total_cost_usd = 0.018 (got {result['total_cost_usd']})")
    _assert(result["total_minutes"] == 4,
            f"total_minutes = 4 (got {result['total_minutes']})")


def test_estimate_fix_cost_m00_cadena_completa():
    _section("PIEZA 5 — estimate_fix_cost: causa raíz m00 (cadena completa)")
    result = estimate_fix_cost("m00")
    # m00 → downstream=[m01a, m01b, m02, m03] + m05 = 6 módulos
    _assert(result["chain"] == ["m00", "m01a", "m01b", "m02", "m03", "m05"],
            f"chain completa (got {result['chain']})")
    # 0.025 + 0.005 + 0.015 + 0.001 + 0.012 + 0.005 = 0.063
    _assert(result["total_cost_usd"] == 0.063,
            f"total_cost_usd = 0.063 (got {result['total_cost_usd']})")
    # 5 + 1 + 3 + 1 + 2 + 1 = 13
    _assert(result["total_minutes"] == 13,
            f"total_minutes = 13 (got {result['total_minutes']})")
    _assert("m00 → m01a → m01b → m02 → m03 → m05" == result["chain_str"],
            "chain_str con flechas Unicode")


def test_estimate_fix_cost_m01a():
    _section("PIEZA 5 — estimate_fix_cost: causa raíz m01a")
    result = estimate_fix_cost("m01a")
    _assert(result["chain"] == ["m01a", "m01b", "m02", "m03", "m05"],
            f"chain saltea m00 (got {result['chain']})")
    # 0.005 + 0.015 + 0.001 + 0.012 + 0.005 = 0.038
    _assert(result["total_cost_usd"] == 0.038,
            f"total_cost_usd = 0.038 (got {result['total_cost_usd']})")
    _assert(result["total_minutes"] == 8,
            f"total_minutes = 8 (got {result['total_minutes']})")


def test_estimate_fix_cost_m01b():
    _section("PIEZA 5 — estimate_fix_cost: causa raíz m01b")
    result = estimate_fix_cost("m01b")
    _assert(result["chain"] == ["m01b", "m02", "m03", "m05"],
            f"chain (got {result['chain']})")
    # 0.015 + 0.001 + 0.012 + 0.005 = 0.033
    _assert(result["total_cost_usd"] == 0.033,
            f"total_cost_usd = 0.033 (got {result['total_cost_usd']})")
    _assert(result["total_minutes"] == 7,
            f"total_minutes = 7 (got {result['total_minutes']})")


def test_estimate_fix_cost_modulo_invalido():
    _section("PIEZA 5 — estimate_fix_cost: módulo inválido → ValueError")
    raised = False
    try:
        estimate_fix_cost("m99")
    except ValueError as e:
        raised = True
        _assert("m99" in str(e), "mensaje incluye el módulo inválido")
        _assert("Válidos" in str(e), "mensaje incluye lista de válidos")
    _assert(raised, "ValueError levantada para módulo desconocido")


def test_estimate_fix_cost_m05_no_permitido():
    _section("PIEZA 5 — estimate_fix_cost: m05 NO puede ser causa raíz")
    raised = False
    try:
        estimate_fix_cost("m05")
    except ValueError as e:
        raised = True
        _assert("m05" in str(e), "mensaje menciona m05")
        _assert("juez" in str(e).lower() or "audita" in str(e).lower(),
                "mensaje explica por qué (el juez no se juzga a sí mismo)")
    _assert(raised, "ValueError levantada para m05 como causa raíz")


def test_cost_table_consistente():
    _section("PIEZA 5 — COST_TABLE: estructura consistente")
    expected_keys = {"cost_usd", "minutes", "downstream"}
    for module, entry in COST_TABLE.items():
        _assert(set(entry.keys()) == expected_keys,
                f"{module}: tiene exactamente {sorted(expected_keys)}")
        _assert(isinstance(entry["cost_usd"], (int, float)),
                f"{module}: cost_usd es numérico")
        _assert(isinstance(entry["minutes"], int),
                f"{module}: minutes es int")
        _assert(isinstance(entry["downstream"], list),
                f"{module}: downstream es lista")
    # m05 incluido
    _assert("m05" in COST_TABLE, "COST_TABLE incluye m05")
    _assert(COST_TABLE["m05"]["downstream"] == [],
            "m05 no tiene downstream (es el último de la cadena)")


# ════════════════════════════════════════════════════════════════════════
#  TESTS — PIEZA 6
# ════════════════════════════════════════════════════════════════════════

def _make_issue_for_report(chapter_id=1, image_index=1, issue_n=1, **overrides):
    """Issue válido + chapter_id (que se inyecta normalmente en Pieza 7)."""
    base = _make_valid_issue(chapter_id=chapter_id, image_index=image_index,
                              issue_n=issue_n, **overrides)
    base["chapter_id"] = chapter_id
    base["root_cause_conflict"] = False  # default sin conflicto
    return base


def test_earliest_module():
    _section("PIEZA 6 — _earliest_module: orden lineal")
    _assert(_earliest_module(["m03", "m02", "m01b"]) == "m01b",
            "[m03, m02, m01b] → 'm01b' (más upstream)")
    _assert(_earliest_module(["m03"]) == "m03",
            "['m03'] → 'm03' (único)")
    _assert(_earliest_module(["m03", "m03", "m03"]) == "m03",
            "todos iguales → ese mismo")
    _assert(_earliest_module(["m05", "m00"]) == "m00",
            "m00 vence a m05")


def test_compute_global_fix_plan_dedup():
    _section("PIEZA 6 — _compute_global_fix_plan: dedup correcta")

    # 3 issues con causa raíz m03 → cadena m03 → m05 ($0.017)
    issues_3xm03 = [
        _make_issue_for_report(proposed_root_cause_module="m03"),
        _make_issue_for_report(image_index=2, issue_n=1, proposed_root_cause_module="m03"),
        _make_issue_for_report(chapter_id=2, image_index=1, issue_n=1,
                                proposed_root_cause_module="m03"),
    ]
    plan = _compute_global_fix_plan(issues_3xm03)
    _assert(plan["total_cost_usd"] == 0.017,
            f"3 issues m03 dedupea a 1 cadena (got ${plan['total_cost_usd']})")
    _assert(plan["chain"] == ["m03", "m05"], "cadena correcta")

    # 3 issues m03 + 1 issue m02 → m02 absorbe a m03 → cadena m02→m03→m05 ($0.018)
    issues_mixto = issues_3xm03 + [
        _make_issue_for_report(chapter_id=3, image_index=1, issue_n=1,
                                proposed_root_cause_module="m02"),
    ]
    plan = _compute_global_fix_plan(issues_mixto)
    _assert(plan["total_cost_usd"] == 0.018,
            f"m02 absorbe m03 → $0.018 (got ${plan['total_cost_usd']})")
    _assert(plan["chain"] == ["m02", "m03", "m05"], "cadena absorbente")

    # 1 issue m00 + 5 issues m03 → m00 absorbe todo → cadena completa ($0.063)
    issues_m00 = [_make_issue_for_report(proposed_root_cause_module="m00")] + [
        _make_issue_for_report(image_index=i, issue_n=1,
                                proposed_root_cause_module="m03")
        for i in range(2, 7)
    ]
    plan = _compute_global_fix_plan(issues_m00)
    _assert(plan["total_cost_usd"] == 0.063,
            f"m00 absorbe todo → $0.063 (got ${plan['total_cost_usd']})")


def test_compute_global_fix_plan_vacio():
    _section("PIEZA 6 — _compute_global_fix_plan: lista vacía")
    plan = _compute_global_fix_plan([])
    _assert(plan["chain"] == [], "issues=[] → chain vacía")
    _assert(plan["total_cost_usd"] == 0.0, "issues=[] → costo 0")
    _assert(plan["total_minutes"] == 0, "issues=[] → tiempo 0")


def test_global_verdict_emoji():
    _section("PIEZA 6 — _global_verdict_emoji: 3 niveles")
    _assert(_global_verdict_emoji("PASS", []) == "🟢", "PASS sin issues → verde")
    _assert(_global_verdict_emoji("FLAG", [_make_issue_for_report(severity="low")]) == "🟡",
            "FLAG con todos low → amarillo")
    _assert(_global_verdict_emoji("FLAG", [_make_issue_for_report(severity="medium")]) == "🟡",
            "FLAG con medium → amarillo")
    _assert(_global_verdict_emoji("FLAG", [_make_issue_for_report(severity="high")]) == "🔴",
            "FLAG con high → rojo")
    _assert(_global_verdict_emoji("FLAG", [
        _make_issue_for_report(severity="low"),
        _make_issue_for_report(image_index=2, severity="high"),
    ]) == "🔴", "FLAG con high entre varios → rojo")


def test_render_report_pass():
    _section("PIEZA 6 — render_report: PASS limpio")
    report = render_report("Wittenoom", [], "PASS")
    _assert("VEREDICTO PARA \"Wittenoom\"" in report, "incluye topic en header")
    _assert("🟢 PASS" in report, "PASS con emoji verde")
    _assert("sin issues" in report, "menciona 'sin issues'")
    _assert("¡Listo para m04!" in report, "invita a proceder con m04")
    # PASS NO debe mostrar el menú de acciones
    _assert("[V] Ver issue por issue" not in report,
            "PASS no muestra menú de acciones")


def test_render_report_flag_un_issue():
    _section("PIEZA 6 — render_report: FLAG con 1 issue medium")
    issues = [_make_issue_for_report(
        chapter_id=6, image_index=1, severity="medium", category="text_in_image",
        anchor_excerpt="the keeper studied logbook entries that night",
        what_happened="prompt requests literal text rendering",
        why_happened="m03 included date as readable text",
        how_to_fix="rewrite without legible text",
        proposed_regex_pattern=r"\b\d{1,2}\s+october\b",
    )]
    report = render_report("Pompeya", issues, "FLAG")

    _assert("Pompeya" in report, "incluye topic")
    _assert("🟡 FLAG" in report, "FLAG con medium → amarillo")
    _assert("1 issue encontrado" in report, "singular '1 issue encontrado'")
    _assert("Capítulo 6, imagen 1" in report, "ubicación legible en castellano")
    _assert("ISSUE 1 de 1" in report, "header del issue")
    _assert("Categoría: text_in_image" in report, "categoría del issue")
    _assert("📖 Anchor:" in report, "anchor_excerpt mostrado")
    _assert("🐛 Qué pasó" in report, "sección 'qué pasó'")
    _assert("🔍 Por qué pasó" in report, "sección 'por qué'")
    _assert("🛠 Cómo arreglarlo" in report, "sección 'cómo arreglar'")
    _assert("⏱ Costo del fix: $0.017" in report, "costo del fix en m03")
    _assert("Cadena: m03 → m05" in report, "cadena del fix")
    _assert("🔧 Patrón regex sugerido:" in report, "sección regex sugerido")
    _assert(r"\b\d{1,2}\s+october\b" in report, "regex literal mostrado")
    _assert("Costo total estimado para aplicar todos los fixes: $0.017"
            in report, "costo total deduplicado")
    _assert("[V] Ver issue por issue" in report, "menú de acciones presente")
    _assert("[A] Aprobar todos" in report, "menú [A]")
    _assert("[R] Rechazar todos" in report, "menú [R]")
    _assert("[S] Salir" in report, "menú [S]")


def test_render_report_multiples_issues():
    _section("PIEZA 6 — render_report: múltiples issues con dedup de costo")
    issues = [
        _make_issue_for_report(chapter_id=5, image_index=6, issue_n=1,
                                severity="high", category="era_mismatch_anchor"),
        _make_issue_for_report(chapter_id=5, image_index=7, issue_n=1,
                                severity="medium", category="era_mismatch_anchor"),
        _make_issue_for_report(chapter_id=6, image_index=1, issue_n=1,
                                severity="low", category="text_in_image"),
    ]
    report = render_report("Pompeya", issues, "FLAG")

    _assert("🔴 FLAG" in report, "any high → emoji rojo")
    _assert("3 issues encontrados" in report, "plural '3 issues encontrados'")
    _assert("ISSUE 1 de 3" in report and "ISSUE 2 de 3" in report
            and "ISSUE 3 de 3" in report, "los 3 issues numerados correctamente")
    # Dedup: 3 issues m03 → 1 sola cadena m03→m05 = $0.017
    _assert("Costo total estimado para aplicar todos los fixes: $0.017"
            in report, "dedup global a $0.017")


def test_render_report_conflicto_causa_raiz():
    _section("PIEZA 6 — render_report: conflicto de causa raíz mostrado")
    issue = _make_issue_for_report(
        category="text_in_image",
        proposed_root_cause_module="m00",  # LLM dice m00
    )
    issue["root_cause_conflict"] = True
    issue["heuristic_root_cause_module"] = "m03"
    report = render_report("Tunguska", [issue], "FLAG")

    _assert("⚠ Conflicto de causa raíz" in report, "sección de conflicto presente")
    _assert("LLM propone:     m00" in report, "muestra propuesta del LLM")
    _assert("Heurística dice: m03" in report, "muestra heurística")
    _assert("decidí cuál preferís" in report,
            "explica que el usuario decide")


def test_render_report_sin_regex_pattern():
    _section("PIEZA 6 — render_report: bug semántico sin regex")
    issue = _make_issue_for_report(
        category="era_mismatch_anchor",
        proposed_regex_pattern=None,  # bug semántico, no regex-able
    )
    report = render_report("Pompeya", [issue], "FLAG")
    _assert("🔧 Patrón regex sugerido" not in report,
            "regex=None → sección regex NO aparece")


# ════════════════════════════════════════════════════════════════════════
#  TESTS — PIEZA 7
# ════════════════════════════════════════════════════════════════════════

def _setup_workspace(tmpdir: Path, topic_id: str) -> dict:
    """Crea estructura de archivos sintética bajo tmpdir.

    Retorna los datos sintéticos para que el caller pueda customizar tests.
    """
    # 1. topics_db.json
    topics_db = {
        "topics": [{
            "topic_id": topic_id,
            "video_title": "Test Topic",
            "era_visual_canon": {
                "primary_decade": "1960s",
                "spans": "1960s Cold War era",
                "clothing": "naval uniforms",
                "technology": "vintage radios",
                "vehicles_machinery": "submarines",
                "interiors": "industrial steel",
                "forbidden_anachronisms": "smartphones",
            },
            "documented_people": [
                {"name": "Francis Slattery", "role": "commander",
                 "age_at_event": 36, "era": "1968",
                 "appearance_canon": "mid-30s American naval officer"},
            ],
            "anachronism_blocklist": ["smartphones", "drones"],
        }]
    }
    (tmpdir / "topics_db.json").write_text(
        _json_test.dumps(topics_db, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # 2. Estructura _steps/{topic_id}/
    steps = tmpdir / "scripts" / "_steps" / topic_id
    steps.mkdir(parents=True, exist_ok=True)

    # 3. 01a_skeleton.json — skeleton mínimo de 2 caps
    skeleton = {
        "topic_id": topic_id,
        "chapters": [
            {"chapter_number": 1, "render_engine": "flux", "role": "hook"},
            {"chapter_number": 2, "render_engine": "veo", "role": "climax"},
        ],
    }
    (steps / "01a_skeleton.json").write_text(
        _json_test.dumps(skeleton, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # 4. 01b_narration.json — minimal (m05 no lo usa pero viene del contrato)
    narration = {"topic_id": topic_id, "chapters": []}
    (steps / "01b_narration.json").write_text(
        _json_test.dumps(narration, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # 5. 02_profiles.json
    profiles = {
        "topic_id": topic_id,
        "chapters": [
            {"chapter_number": 1, "art_profile": "INDUSTRIAL",
             "rationale": "Industrial encaja con submarino."},
            {"chapter_number": 2, "art_profile": "SUBMARINE",
             "rationale": "Submarine es el clímax."},
        ],
    }
    (steps / "02_profiles.json").write_text(
        _json_test.dumps(profiles, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # 6. 03_visual.json — cap 1 flux con 2 imgs, cap 2 veo con 1 img
    visual = {
        "topic_id": topic_id,
        "chapters": [
            {
                "chapter_number": 1,
                "image_prompts": [
                    {
                        "prompt": "an industrial submarine valve in cold blue light",
                        "art_profile": "INDUSTRIAL",
                        "subject_ref": "valve",
                        "emotional_rank": "MID",
                        "narration_anchor": "the valve was the last barrier",
                    },
                    {
                        "prompt": "the commander stood watch through the night",
                        "art_profile": "INDUSTRIAL",
                        "subject_ref": "commander",
                        "emotional_rank": "HIGH",
                        "narration_anchor": "the commander stood watch through the night",
                    },
                ],
            },
            {
                "chapter_number": 2,
                "image_prompt": "a wide shot of a 1960s submarine cutting through Atlantic waves",
                "video_prompt": "slow push in",
                "subject_ref": "submarine",
                "narration_anchor": "the submarine vanished into the Atlantic mist",
            },
        ],
    }
    (steps / "03_visual.json").write_text(
        _json_test.dumps(visual, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return {
        "topic_id": topic_id,
        "topics_db": topics_db,
        "skeleton": skeleton,
        "profiles": profiles,
        "visual": visual,
        "steps_dir": steps,
    }


def test_normalize_chapter_images_flux():
    _section("PIEZA 7 — _normalize_chapter_images: flux")
    cap_flux = {
        "chapter_number": 1,
        "image_prompts": [
            {"prompt": "img 1 prompt", "narration_anchor": "anchor 1",
             "art_profile": "DESERT"},
            {"prompt": "img 2 prompt", "narration_anchor": "anchor 2",
             "art_profile": "INTERIOR"},
            {"prompt": "img 3 prompt", "narration_anchor": "anchor 3"},  # sin art_profile
        ],
    }
    # Fix meta-bug: cap_profile ahora obligatorio (fallback para imgs sin art_profile)
    result = _normalize_chapter_images(cap_flux, "flux", "AERIAL")
    _assert(len(result) == 3, "3 imgs normalizadas")
    _assert(result[0]["image_index"] == 1, "image_index 1-indexed")
    _assert(result[2]["image_index"] == 3, "última img con index 3")
    _assert(result[1]["prompt"] == "img 2 prompt", "prompt preservado")
    _assert(result[1]["narration_anchor"] == "anchor 2", "anchor preservado")
    # Fix meta-bug: art_profile leído del item m03 (override) o fallback al cap
    _assert(result[0]["art_profile"] == "DESERT", "img 1: art_profile leído del item")
    _assert(result[1]["art_profile"] == "INTERIOR", "img 2: art_profile override leído")
    _assert(result[2]["art_profile"] == "AERIAL",
            "img 3: art_profile vacío → fallback al cap_profile")


def test_normalize_chapter_images_veo():
    _section("PIEZA 7 — _normalize_chapter_images: veo")
    cap_veo = {
        "chapter_number": 2,
        "image_prompt": "veo prompt",
        "video_prompt": "ignored",
        "narration_anchor": "veo anchor",
    }
    # Fix meta-bug: cap_profile siempre se hereda (veo no tiene art_profile a nivel img)
    result = _normalize_chapter_images(cap_veo, "veo", "INDUSTRIAL")
    _assert(len(result) == 1, "veo siempre 1 img")
    _assert(result[0]["image_index"] == 1, "image_index = 1")
    _assert(result[0]["prompt"] == "veo prompt", "prompt preservado")
    _assert(result[0]["narration_anchor"] == "veo anchor", "anchor preservado")
    # Fix meta-bug: veo hereda art_profile del cap (no tiene a nivel img)
    _assert(result[0]["art_profile"] == "INDUSTRIAL",
            "veo hereda art_profile del cap_profile")


def test_normalize_chapter_images_engine_invalido():
    _section("PIEZA 7 — _normalize_chapter_images: engine inválido")
    raised = False
    try:
        _normalize_chapter_images({}, "unknown_engine", "DESERT")
    except ValueError as e:
        raised = True
        _assert("unknown_engine" in str(e), "mensaje incluye engine inválido")
    _assert(raised, "ValueError por engine desconocido")


def test_format_images_block_includes_image_art_profile():
    """Fix meta-bug: el bloque IMAGES TO AUDIT expone image_art_profile."""
    _section("META-BUG FIX — _format_images_block expone image_art_profile")
    from script_engine.m05_judge import _format_images_block
    images = [
        {
            "image_index": 1,
            "prompt": "test prompt 1",
            "narration_anchor": "test anchor 1",
            "art_profile": "DESERT",
        },
        {
            "image_index": 2,
            "prompt": "test prompt 2",
            "narration_anchor": "test anchor 2",
            "art_profile": "AERIAL",
        },
    ]
    block = _format_images_block(images)
    _assert("image_art_profile: 'DESERT'" in block,
            "img 1 expone image_art_profile=DESERT")
    _assert("image_art_profile: 'AERIAL'" in block,
            "img 2 expone image_art_profile=AERIAL")
    _assert("anchor:" in block, "anchor sigue presente")
    _assert("prompt:" in block, "prompt sigue presente")


def test_prompt_profile_incoherence_redefined():
    """Fix meta-bug: el prompt redefine profile_incoherence contra image_art_profile."""
    _section("META-BUG FIX — prompt redefine profile_incoherence")
    from script_engine.m05_judge import SYSTEM_PROMPT_FIXED
    # La nueva definición habla de "image_art_profile" y override permitido
    _assert("image_art_profile" in SYSTEM_PROMPT_FIXED,
            "prompt menciona image_art_profile")
    _assert("override" in SYSTEM_PROMPT_FIXED.lower(),
            "prompt explica el concepto de override")
    _assert("Anti-patterns to AVOID flagging" in SYSTEM_PROMPT_FIXED,
            "prompt incluye anti-patrón explícito sobre override")
    # No debe quedar la vieja definición que comparaba contra cap profile
    # (verificar que el bloque viejo "established by the chapter profile" no sea el ÚNICO)
    # Verificar que el GOOD example menciona override OK
    _assert("override of cap default is fine" in SYSTEM_PROMPT_FIXED,
            "GOOD example reconoce override de m03 como válido")


def test_judge_topic_happy_path_pass():
    _section("PIEZA 7 — judge_topic: happy path PASS")
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        topic_id = "test-uuid-pass"
        _setup_workspace(tmp, topic_id)

        # Mock Flash para retornar PASS en cada cap
        def fake_flash_pass(prompt):
            # Detectar chapter_id desde el prompt
            if "CHAPTER 1" in prompt:
                return {"chapter_id": 1, "verdict": "PASS", "issues": []}
            if "CHAPTER 2" in prompt:
                return {"chapter_id": 2, "verdict": "PASS", "issues": []}
            return {"chapter_id": 0, "verdict": "PASS", "issues": []}

        _set_fake_flash(fake_flash_pass)

        # Capturar stdout para no contaminar el output
        captured = io.StringIO()
        with contextlib.redirect_stdout(captured):
            result = judge_topic(topic_id, data_root=tmp)

    _assert(result["topic_id"] == topic_id, "topic_id en output")
    _assert(result["topic_title"] == "Test Topic", "topic_title del topic")
    _assert(result["global_verdict"] == "PASS",
            "global_verdict=PASS cuando todos los caps son PASS")
    _assert(len(result["chapters"]) == 2, "2 caps procesados")
    _assert(result["all_issues"] == [], "all_issues vacío en PASS global")
    _assert("VEREDICTO PARA \"Test Topic\"" in result["report_str"],
            "report_str contiene topic_title")
    _assert("🟢 PASS" in result["report_str"],
            "report_str contiene PASS verde")


def test_judge_topic_persiste_output():
    _section("PIEZA 7 — judge_topic: persiste 05_judge.json")
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        topic_id = "test-uuid-persist"
        ws = _setup_workspace(tmp, topic_id)

        def fake(prompt):
            return {"chapter_id": 1 if "CHAPTER 1" in prompt else 2,
                    "verdict": "PASS", "issues": []}
        _set_fake_flash(fake)

        captured = io.StringIO()
        with contextlib.redirect_stdout(captured):
            judge_topic(topic_id, data_root=tmp)

        # Verificar que el archivo existe
        out_file = ws["steps_dir"] / "05_judge.json"
        _assert(out_file.exists(), "05_judge.json persistido en disco")

        # Verificar que es JSON parseable con shape esperado
        persisted = _json_test.loads(out_file.read_text(encoding="utf-8"))
        _assert(persisted["topic_id"] == topic_id,
                "persistido tiene topic_id correcto")
        _assert(persisted["global_verdict"] == "PASS",
                "persistido tiene verdict")
        _assert("chapters" in persisted, "persistido tiene chapters")
        _assert("all_issues" in persisted, "persistido tiene all_issues")
        _assert("cost_data" in persisted, "persistido tiene cost_data")


def test_judge_topic_flag_global():
    _section("PIEZA 7 — judge_topic: FLAG global cuando algún cap es FLAG")
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        topic_id = "test-uuid-flag"
        _setup_workspace(tmp, topic_id)

        def fake(prompt):
            if "CHAPTER 1" in prompt:
                # Cap 1 PASS
                return {"chapter_id": 1, "verdict": "PASS", "issues": []}
            # Cap 2 FLAG con 1 issue
            return {
                "chapter_id": 2, "verdict": "FLAG",
                "issues": [{
                    "issue_id": "cap2_img1_issue1",
                    "image_index": 1,
                    "anchor_excerpt": "the submarine vanished into the Atlantic mist",
                    "category": "anchor_mismatch",
                    "severity": "medium",
                    "what_happened": "image and anchor diverge",
                    "why_happened": "prompt drifted",
                    "how_to_fix": "rewrite to depict the submarine",
                    "proposed_root_cause_module": "m03",
                    "proposed_regex_pattern": None,
                }],
            }
        _set_fake_flash(fake)

        captured = io.StringIO()
        with contextlib.redirect_stdout(captured):
            result = judge_topic(topic_id, data_root=tmp)

    _assert(result["global_verdict"] == "FLAG",
            "global=FLAG cuando algún cap es FLAG")
    _assert(len(result["all_issues"]) == 1, "1 issue total")
    _assert(result["all_issues"][0]["chapter_id"] == 2,
            "chapter_id=2 inyectado en el issue")
    _assert(result["all_issues"][0].get("root_cause_conflict") is False,
            "validate_root_cause aplicado (m03 + anchor_mismatch coinciden)")
    _assert(result["cost_data"]["total_cost_usd"] == 0.017,
            "cost_data calculado para m03→m05")


def test_judge_topic_topic_no_existe():
    _section("PIEZA 7 — judge_topic: topic_id desconocido → KeyError")
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        _setup_workspace(tmp, "real-uuid")

        raised = False
        try:
            judge_topic("uuid-fantasma", data_root=tmp)
        except KeyError as e:
            raised = True
            _assert("uuid-fantasma" in str(e), "mensaje menciona el id buscado")
        _assert(raised, "KeyError levantada")


def test_judge_topic_archivo_upstream_falta():
    _section("PIEZA 7 — judge_topic: 03_visual.json falta → FileNotFoundError")
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        topic_id = "test-uuid-missing"
        ws = _setup_workspace(tmp, topic_id)
        # Borrar el 03_visual.json
        (ws["steps_dir"] / "03_visual.json").unlink()

        raised = False
        try:
            judge_topic(topic_id, data_root=tmp)
        except FileNotFoundError as e:
            raised = True
            _assert("03_visual.json" in str(e),
                    "mensaje menciona archivo faltante")
        _assert(raised, "FileNotFoundError levantada cuando falta upstream")


def test_judge_topic_chapter_id_inyectado_en_issues():
    _section("PIEZA 7 — judge_topic: chapter_id inyectado en cada issue")
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        topic_id = "test-uuid-inject"
        _setup_workspace(tmp, topic_id)

        def fake(prompt):
            cap = 1 if "CHAPTER 1" in prompt else 2
            return {
                "chapter_id": cap, "verdict": "FLAG",
                "issues": [{
                    "issue_id": f"cap{cap}_img1_issue1",
                    "image_index": 1,
                    "anchor_excerpt": (
                        "the valve was the last barrier"
                        if cap == 1
                        else "the submarine vanished into the Atlantic mist"
                    ),
                    "category": "anchor_mismatch",
                    "severity": "low",
                    "what_happened": "test",
                    "why_happened": "test",
                    "how_to_fix": "test",
                    "proposed_root_cause_module": "m03",
                    "proposed_regex_pattern": None,
                }],
            }
        _set_fake_flash(fake)

        captured = io.StringIO()
        with contextlib.redirect_stdout(captured):
            result = judge_topic(topic_id, data_root=tmp)

    _assert(len(result["all_issues"]) == 2, "1 issue por cap → 2 totales")
    chapter_ids = sorted(i["chapter_id"] for i in result["all_issues"])
    _assert(chapter_ids == [1, 2],
            "chapter_id inyectado correctamente en cada issue")


# ════════════════════════════════════════════════════════════════════════
#  PIEZA 9 — VOTING (N corridas con dedup + cohorte)
# ════════════════════════════════════════════════════════════════════════

def test_voting_key_canonica():
    """_voting_key debe usar (chapter_id, image_index, category)."""
    _section("PIEZA 9 — _voting_key clave canónica")
    from script_engine.m05_judge import _voting_key
    issue = {
        "chapter_id": 4,
        "image_index": 2,
        "category": "anchor_mismatch",
        "severity": "high",
        "what_happened": "...",
    }
    key = _voting_key(issue)
    _assert(key == (4, 2, "anchor_mismatch"),
            "clave es (cap, img, cat) — severidad y otros NO entran")
    # Mismo cap/img pero distinta categoría → claves distintas
    issue2 = dict(issue)
    issue2["category"] = "era_mismatch_anchor"
    _assert(_voting_key(issue) != _voting_key(issue2),
            "distinta categoría → clave distinta (issues independientes)")


def test_voting_merge_unanime_3de3():
    """Issue que aparece en las 3 corridas → cohort=3, una sola entrada."""
    _section("PIEZA 9 — voting merge: consenso unánime 3/3")
    from script_engine.m05_judge import _merge_runs_with_voting

    def make_run(verdict="FLAG"):
        return {
            "topic_id": "T",
            "topic_title": "Test",
            "global_verdict": verdict,
            "all_issues": [{
                "chapter_id": 7, "image_index": 1,
                "category": "profile_incoherence",
                "severity": "medium",
                "what_happened": "palette mismatch",
                "why_happened": "x", "how_to_fix": "y",
                "issue_id": "cap7_img1_issue1",
                "anchor_excerpt": "test",
                "proposed_root_cause_module": "m03",
                "proposed_regex_pattern": None,
            }],
        }

    runs = [make_run(), make_run(), make_run()]
    merged = _merge_runs_with_voting(runs, n_runs=3)
    _assert(len(merged["all_issues"]) == 1, "3 corridas con mismo issue → 1 entrada")
    iss = merged["all_issues"][0]
    _assert(iss["cohort"] == 3, "cohort=3 (todas)")
    _assert(iss["cohort_total"] == 3, "cohort_total=3")
    _assert(merged["voting_stats"]["cohort_3_of_3"] == 1, "stats: 1 issue en cohort 3")
    _assert(merged["voting_stats"]["cohort_2_of_3"] == 0, "stats: 0 en cohort 2")
    _assert(merged["voting_stats"]["cohort_1_of_3"] == 0, "stats: 0 en cohort 1")


def test_voting_merge_mayoria_2de3():
    """Issue en 2 corridas, NO en la 3ra → cohort=2."""
    _section("PIEZA 9 — voting merge: mayoría 2/3")
    from script_engine.m05_judge import _merge_runs_with_voting

    issue_A = {
        "chapter_id": 4, "image_index": 4, "category": "anchor_mismatch",
        "severity": "high", "what_happened": "...", "why_happened": "...",
        "how_to_fix": "...", "issue_id": "cap4_img4_issue1",
        "anchor_excerpt": "test", "proposed_root_cause_module": "m03",
        "proposed_regex_pattern": None,
    }
    runs = [
        {"topic_id": "T", "topic_title": "Test", "global_verdict": "FLAG",
         "all_issues": [issue_A]},
        {"topic_id": "T", "topic_title": "Test", "global_verdict": "FLAG",
         "all_issues": [issue_A]},
        {"topic_id": "T", "topic_title": "Test", "global_verdict": "PASS",
         "all_issues": []},
    ]
    merged = _merge_runs_with_voting(runs, n_runs=3)
    _assert(len(merged["all_issues"]) == 1, "1 issue único")
    _assert(merged["all_issues"][0]["cohort"] == 2, "cohort=2 (2/3)")
    _assert(merged["global_verdict"] == "FLAG",
            "FLAG porque ≥1 corrida flageó (PASS solo si TODAS dijeron PASS Y sin issues)")


def test_voting_merge_minoria_1de3():
    """Issue solo en 1 corrida → cohort=1, sigue presente (cohorte ≥1 política)."""
    _section("PIEZA 9 — voting merge: minoría 1/3 (sigue presente)")
    from script_engine.m05_judge import _merge_runs_with_voting

    issue_A = {
        "chapter_id": 3, "image_index": 7, "category": "narration_unvisualizable",
        "severity": "medium", "what_happened": "...", "why_happened": "...",
        "how_to_fix": "...", "issue_id": "cap3_img7_issue1",
        "anchor_excerpt": "test", "proposed_root_cause_module": "m01b",
        "proposed_regex_pattern": None,
    }
    runs = [
        {"topic_id": "T", "topic_title": "Test", "global_verdict": "FLAG",
         "all_issues": [issue_A]},
        {"topic_id": "T", "topic_title": "Test", "global_verdict": "PASS",
         "all_issues": []},
        {"topic_id": "T", "topic_title": "Test", "global_verdict": "PASS",
         "all_issues": []},
    ]
    merged = _merge_runs_with_voting(runs, n_runs=3)
    _assert(len(merged["all_issues"]) == 1, "issue minoría sigue emitido (política cohorte ≥1)")
    _assert(merged["all_issues"][0]["cohort"] == 1, "cohort=1")
    _assert(merged["voting_stats"]["cohort_1_of_3"] == 1, "stats: 1 issue cohort 1")


def test_voting_merge_orden_por_cohort():
    """all_issues ordenado: cohort desc, luego severity (high primero)."""
    _section("PIEZA 9 — voting merge: orden cohort desc + severity")
    from script_engine.m05_judge import _merge_runs_with_voting

    base_fields = {
        "what_happened": "...", "why_happened": "...", "how_to_fix": "...",
        "anchor_excerpt": "test", "proposed_root_cause_module": "m03",
        "proposed_regex_pattern": None,
    }
    iss_unanime_low = {
        "chapter_id": 5, "image_index": 1, "category": "text_in_image",
        "severity": "low", "issue_id": "cap5_img1_issue1", **base_fields,
    }
    iss_minoria_high = {
        "chapter_id": 4, "image_index": 4, "category": "anchor_mismatch",
        "severity": "high", "issue_id": "cap4_img4_issue1", **base_fields,
    }
    runs = [
        # Run 1: ambos issues
        {"topic_id": "T", "topic_title": "Test", "global_verdict": "FLAG",
         "all_issues": [iss_unanime_low, iss_minoria_high]},
        # Run 2: solo unanime
        {"topic_id": "T", "topic_title": "Test", "global_verdict": "FLAG",
         "all_issues": [iss_unanime_low]},
        # Run 3: solo unanime
        {"topic_id": "T", "topic_title": "Test", "global_verdict": "FLAG",
         "all_issues": [iss_unanime_low]},
    ]
    merged = _merge_runs_with_voting(runs, n_runs=3)
    _assert(len(merged["all_issues"]) == 2, "2 issues únicos")
    # cohort=3 va primero (aunque sea low)
    _assert(merged["all_issues"][0]["cohort"] == 3, "primero: cohort más alto")
    _assert(merged["all_issues"][0]["severity"] == "low", "primero: cohort 3 low")
    _assert(merged["all_issues"][1]["cohort"] == 1, "segundo: cohort menor")
    _assert(merged["all_issues"][1]["severity"] == "high", "segundo: cohort 1 high")


def test_voting_merge_dedup_dentro_de_un_run():
    """Si un run emite el mismo issue 2 veces (bug raro), cuenta solo 1 vez."""
    _section("PIEZA 9 — voting merge: dedup intra-run")
    from script_engine.m05_judge import _merge_runs_with_voting

    issue_A = {
        "chapter_id": 1, "image_index": 1, "category": "text_in_image",
        "severity": "low", "what_happened": "...", "why_happened": "...",
        "how_to_fix": "...", "issue_id": "cap1_img1_issue1",
        "anchor_excerpt": "test", "proposed_root_cause_module": "m03",
        "proposed_regex_pattern": None,
    }
    # Run 1 emite el mismo issue 2 veces (no debería pasar pero defensa)
    runs = [{
        "topic_id": "T", "topic_title": "Test", "global_verdict": "FLAG",
        "all_issues": [issue_A, issue_A],
    }]
    merged = _merge_runs_with_voting(runs, n_runs=1)
    _assert(len(merged["all_issues"]) == 1, "duplicado intra-run colapsa")
    _assert(merged["all_issues"][0]["cohort"] == 1, "cohort=1 (NO se suma a 2 por duplicado)")


def test_voting_merge_global_verdict_pass_solo_si_todos_pass():
    """global_verdict='PASS' solo si TODAS las corridas son PASS y sin issues."""
    _section("PIEZA 9 — voting merge: global_verdict")
    from script_engine.m05_judge import _merge_runs_with_voting

    runs_all_pass = [
        {"topic_id": "T", "topic_title": "Test", "global_verdict": "PASS",
         "all_issues": []} for _ in range(3)
    ]
    merged = _merge_runs_with_voting(runs_all_pass, n_runs=3)
    _assert(merged["global_verdict"] == "PASS", "todas PASS sin issues → PASS")
    _assert(len(merged["all_issues"]) == 0, "sin issues")


def test_voting_merge_n_runs_vacio():
    """ValueError si lista de runs vacía."""
    _section("PIEZA 9 — voting merge: lista vacía → ValueError")
    from script_engine.m05_judge import _merge_runs_with_voting
    raised = False
    try:
        _merge_runs_with_voting([], n_runs=3)
    except ValueError:
        raised = True
    _assert(raised, "lista vacía levanta ValueError")


def test_voting_judge_topic_n_invalido():
    """judge_topic_with_voting valida n: <2 y >10."""
    _section("PIEZA 9 — judge_topic_with_voting valida n")
    from script_engine.m05_judge import judge_topic_with_voting
    raised_low = False
    try:
        judge_topic_with_voting("fake-id", n=1)
    except ValueError as e:
        raised_low = "n debe ser ≥ 2" in str(e)
    _assert(raised_low, "n=1 → ValueError")

    raised_high = False
    try:
        judge_topic_with_voting("fake-id", n=11)
    except ValueError as e:
        raised_high = "n > 10" in str(e)
    _assert(raised_high, "n=11 → ValueError")


def test_voting_format_issue_block_muestra_cohorte():
    """_format_issue_block muestra cohorte si está presente."""
    _section("PIEZA 9 — _format_issue_block muestra cohorte")
    from script_engine.m05_judge import _format_issue_block
    issue_3of3 = {
        "chapter_id": 7, "image_index": 1, "category": "profile_incoherence",
        "severity": "medium", "anchor_excerpt": "test",
        "what_happened": "...", "why_happened": "...", "how_to_fix": "...",
        "issue_id": "cap7_img1_issue1", "proposed_root_cause_module": "m03",
        "proposed_regex_pattern": None,
        "cohort": 3, "cohort_total": 3,
    }
    block_3 = _format_issue_block(issue_3of3, 1, 1)
    _assert("3/3" in block_3, "muestra '3/3' en header")
    _assert("🎯" in block_3, "muestra emoji 🎯 (alta confianza)")
    _assert("alta confianza" in block_3, "muestra label castellano")

    issue_2of3 = dict(issue_3of3); issue_2of3["cohort"] = 2
    block_2 = _format_issue_block(issue_2of3, 1, 1)
    _assert("2/3" in block_2 and "⚠" in block_2 and "mayoría" in block_2,
            "cohort 2/3 → ⚠ mayoría")

    issue_1of3 = dict(issue_3of3); issue_1of3["cohort"] = 1
    block_1 = _format_issue_block(issue_1of3, 1, 1)
    _assert("1/3" in block_1 and "❓" in block_1 and "baja confianza" in block_1,
            "cohort 1/3 → ❓ baja confianza")

    # Backward compat: issue SIN cohort (judge_topic single) no muestra header de cohorte
    issue_no_cohort = dict(issue_3of3)
    del issue_no_cohort["cohort"]
    del issue_no_cohort["cohort_total"]
    block_n = _format_issue_block(issue_no_cohort, 1, 1)
    _assert("/3" not in block_n and "🎯" not in block_n,
            "issue sin cohort: NO muestra cohorte (backward compat)")


# ════════════════════════════════════════════════════════════════════════
#  RUN
# ════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # Pieza 1
    test_normalize_text()
    test_extract_last_name()
    test_detect_name_leakage()
    test_detect_text_in_image()
    test_detect_anachronism_visual()
    test_stage1_predetect()
    # Pieza 2
    test_system_prompt_loaded()
    test_build_chapter_prompt_basic()
    test_build_chapter_prompt_pre_detected_no_vacio()
    test_build_chapter_prompt_topic_data_minimo()
    test_call_flash_for_chapter_happy_path()
    test_call_flash_for_chapter_retry_then_success()
    test_call_flash_for_chapter_three_failures_raise()
    test_call_flash_validator_personalizado()
    # Pieza 3
    test_is_substring_match()
    test_validate_pass_valido()
    test_validate_flag_valido_un_issue()
    test_validate_flag_valido_multiples_issues()
    test_validate_no_dict()
    test_validate_chapter_id_mismatch()
    test_validate_verdict_invalido()
    test_validate_pass_con_issues()
    test_validate_flag_sin_issues()
    test_validate_issue_sin_field()
    test_validate_issue_category_invalida()
    test_validate_issue_severity_invalida()
    test_validate_issue_root_cause_invalida()
    test_validate_issue_image_index_no_existe()
    test_validate_issue_id_malformado()
    test_validate_issue_id_chapter_mismatch()
    test_validate_anchor_excerpt_no_substring()
    test_validate_anchor_excerpt_too_short()
    test_validate_regex_pattern_invalido()
    test_validate_regex_pattern_null_ok()
    test_validate_string_field_vacio()
    test_validate_anchor_excerpt_typo_menor_ok()
    test_build_chapter_validator_integration()
    # Pieza 4
    test_merge_sin_pre_detected()
    test_merge_stage2_confirma_stage1()
    test_merge_stage2_silencia_stage1()
    test_merge_mixto_confirma_y_silencia()
    test_merge_chapter_id_none()
    test_validate_root_cause_coinciden()
    test_validate_root_cause_difieren()
    test_validate_root_cause_other()
    test_validate_root_cause_categoria_desconocida()
    test_validate_root_cause_es_in_place()
    # Pieza 5
    test_estimate_fix_cost_m03()
    test_estimate_fix_cost_m02()
    test_estimate_fix_cost_m00_cadena_completa()
    test_estimate_fix_cost_m01a()
    test_estimate_fix_cost_m01b()
    test_estimate_fix_cost_modulo_invalido()
    test_estimate_fix_cost_m05_no_permitido()
    test_cost_table_consistente()
    # Pieza 6
    test_earliest_module()
    test_compute_global_fix_plan_dedup()
    test_compute_global_fix_plan_vacio()
    test_global_verdict_emoji()
    test_render_report_pass()
    test_render_report_flag_un_issue()
    test_render_report_multiples_issues()
    test_render_report_conflicto_causa_raiz()
    test_render_report_sin_regex_pattern()
    # Pieza 7
    test_normalize_chapter_images_flux()
    test_normalize_chapter_images_veo()
    test_normalize_chapter_images_engine_invalido()
    # Meta-bug fix: image_art_profile y prompt redefinido
    test_format_images_block_includes_image_art_profile()
    test_prompt_profile_incoherence_redefined()
    test_judge_topic_happy_path_pass()
    test_judge_topic_persiste_output()
    test_judge_topic_flag_global()
    test_judge_topic_topic_no_existe()
    test_judge_topic_archivo_upstream_falta()
    test_judge_topic_chapter_id_inyectado_en_issues()

    # Pieza 9 — Voting (N corridas con dedup + cohorte)
    test_voting_key_canonica()
    test_voting_merge_unanime_3de3()
    test_voting_merge_mayoria_2de3()
    test_voting_merge_minoria_1de3()
    test_voting_merge_orden_por_cohort()
    test_voting_merge_dedup_dentro_de_un_run()
    test_voting_merge_global_verdict_pass_solo_si_todos_pass()
    test_voting_merge_n_runs_vacio()
    test_voting_judge_topic_n_invalido()
    test_voting_format_issue_block_muestra_cohorte()

    print(f"\n{'═' * 64}\n  ✅ TODOS LOS TESTS DE PIEZAS 1+2+3+4+5+6+7+9 PASARON\n{'═' * 64}\n")
