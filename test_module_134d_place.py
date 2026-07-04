"""
test_module_134d_place.py — HANDOFF_134d RUTA B (offline, sin API).

1. kind=place → candidato con plantilla place; prompt SIN época-de-foto ("archival",
   "photograph from") y CON el estado de condition_evolution.
2. kind=other/person → skip CON el print gritado (stdout).
3. kind=object → cero cambios (regresión: misma plantilla object de hoy).
4. Ruteo: place → establishing/exterior anclan __subject__, interior_scene/landscape/detalle no.
5. Estado: la plantilla place incluye el estado elegido (at_event dominante).

Mockea foto_madre._generate_madre_gpt (no llama a fal/GPT).

USO:
    python test_module_134d_place.py
"""
import io
import sys
from contextlib import redirect_stdout

import foto_madre as fm
import script_engine.m03_visual as m03

CANON = {
    "primary_decade": "1970s",
    "distinctive_features": "a brutalist 10-story concrete tower (Templeman) over a walled campus.",
    "scale_dimensions": "12-building campus, one 10-story tower.",
    "materials_textures": "poured concrete, steel bars.",
    "color_palette": "grey concrete, rust.",
    "forbidden_anachronisms": "smartphones, LED signs.",
    "condition_evolution": {"at_event": "flooded to the second floor, power out.",
                            "later": "abandoned, roof collapsing."},
}


def _check(c, m, fails):
    if not c:
        fails.append(m)


def main() -> int:
    fails: list[str] = []

    # ── (1)+(5) plantilla place ──
    p = fm._prompt_place({"era_visual_canon": CANON, "anachronism_blocklist": ["modern cars"]})
    _check("archival" not in p.lower(), "(1) place tiene 'archival' (época-de-foto)", fails)
    _check("photograph from" not in p.lower(), "(1) place tiene 'photograph from' (época-de-foto)", fails)
    _check("full-color" in p.lower(), "(1) place no dice 'full-color'", fails)
    _check("Templeman" in p, "(1) place no metió distinctive_features", fails)
    _check("modern cars" in p, "(1) place no metió el anachronism_blocklist", fails)
    _check("flooded to the second floor" in p, "(5) place no incluyó el estado at_event", fails)

    # ── (2) skip gritado (person/other) ──
    for kind in ("person", "other", None):
        buf = io.StringIO()
        with redirect_stdout(buf):
            fm.generate_foto_madre_for_topic({"central_subject": {"kind": kind}}, "vid_skip")
        out = buf.getvalue()
        _check("SIN madre/anclas" in out and f"kind={kind!r}" in out,
               f"(2) kind={kind!r}: no gritó el skip → {out!r}", fails)

    # ── (1b)+(3) ruteo de candidato por kind (qué plantilla se usa) ──
    cap = {}
    orig = fm._generate_madre_gpt
    fm._generate_madre_gpt = lambda prompt, dest: cap.__setitem__("prompt", prompt)
    try:
        cap.clear()
        fm.generate_foto_madre_for_topic(
            {"central_subject": {"kind": "place"}, "era_visual_canon": CANON}, "vid_place")
        _check("establishing view of a single place" in cap.get("prompt", ""),
               "(1b) place no usó la plantilla place", fails)

        cap.clear()
        fm.generate_foto_madre_for_topic(
            {"central_subject": {"kind": "object"}, "era_visual_canon": CANON}, "vid_obj")
        op = cap.get("prompt", "")
        _check("of a single subject" in op and "Archival" in op,
               "(3) object NO usó la plantilla object de hoy (regresión)", fails)
        _check("establishing view of a single place" not in op,
               "(3) object se contaminó con texto de place", fails)
    finally:
        fm._generate_madre_gpt = orig

    # ── (4) filtro exterior-only ──
    imgs = [
        {"foto_madre_ref": ["__subject__"], "subject_ref": "establishing_shot", "shot_scale": "wide"},
        {"foto_madre_ref": ["__subject__"], "subject_ref": "interior_scene", "shot_scale": "medium"},
        {"foto_madre_ref": ["__subject__"], "subject_ref": "main_subject", "shot_scale": "detail"},
        {"foto_madre_ref": ["__subject__"], "subject_ref": "landscape_view", "shot_scale": "wide"},
        {"foto_madre_ref": ["__subject__"], "subject_ref": "main_subject", "shot_scale": "wide"},
    ]
    m03._apply_place_exterior_filter(imgs, True)
    got = [i["foto_madre_ref"] for i in imgs]
    _check(got == [["__subject__"], [], [], [], ["__subject__"]],
           f"(4) filtro place mal: {got}", fails)
    # no-op si NO es place (object no se filtra)
    obj = [{"foto_madre_ref": ["__subject__"], "subject_ref": "interior_scene"}]
    m03._apply_place_exterior_filter(obj, False)
    _check(obj[0]["foto_madre_ref"] == ["__subject__"], "(4) filtro pisó un topic no-place", fails)

    if fails:
        print(f"[FAIL] {len(fails)} assert(s):")
        for f in fails:
            print(f"   ✗ {f}")
        return 1
    print("[PASS] place: plantilla sin época-de-foto + estado, skip gritado, object intacto, "
          "ruteo exterior-only")
    return 0


if __name__ == "__main__":
    sys.exit(main())
