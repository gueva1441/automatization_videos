"""
test_module_foto_madre_prompts.py — HANDOFF_132 (offline, sin API).

Verifica los prompts de la foto madre (motor GPT Image 2 + canon COMPLETO) con el
canon de ec3d7c7f (Alexander L. Kielland) como fixture inline. NO llama a ningún
modelo: solo arma los strings y hace asserts.

Asserts (§VALIDACIÓN del handoff):
  - prompt del SUJETO contiene: "Archival", la década, "vermilion" (color),
    "pentagonal", "strictly avoid", "three-quarter profile"
  - prompt del SUJETO NO contiene: "Isolated technical study", "seamless background"
  - prompt de PROP contiene la década y SÍ "seamless background"
  - sin ".." dobles en ninguno

USO:
    python test_module_foto_madre_prompts.py
"""
import sys

from foto_madre import _prompt_subject, _prompt_prop


# Canon real de ec3d7c7f (recortado a lo que consumen los prompts).
FIXTURE_TOPIC = {
    "era_visual_canon": {
        "primary_decade": "1980s",
        "distinctive_features": (
            "Its most distinctive feature was the pentagonal configuration of its five "
            "support columns, a specific 'Pentagone' design (P89) unique among similar "
            "rigs, giving it an unusual silhouette compared to typical four-column "
            "platforms. It was modified to function as a 'flotel' with extensive added "
            "accommodation modules on its main deck, standing starkly against the North Sea."
        ),
        "materials_textures": (
            "Structural carbon-manganese steel, smooth painted metallic surfaces, "
            "cylindrical forms, tubular beam lattice structures. Fiberglass for lifeboats."
        ),
        "scale_dimensions": (
            "Platform 103 meters long, 99 meters wide. Five vertical columns 35.6 meters "
            "high from pontoon base. Drilling derrick 40 meters high."
        ),
        "color_palette": (
            "Exterior submerged structure in red or vermilion anti-fouling paint; above "
            "waterline structure, columns, and deck in light gray or white. Lifeboats in "
            "bright orange."
        ),
        "forbidden_anachronisms": (
            "Smartphones, LED screens, contemporary clothing (post-2000s), digital cameras, "
            "GPS navigation devices, modern flat-panel displays, touchscreen interfaces."
        ),
    },
}

FIXTURE_PROP = {
    "nombre": "Lifeboats",
    "anclado": "si",
    "forma": "Covered, rectangular-shaped lifeboats with tapered ends, typical for the era.",
}


def _check(cond: bool, msg: str, fails: list) -> None:
    if not cond:
        fails.append(msg)


def main() -> int:
    fails: list[str] = []

    subj = _prompt_subject(FIXTURE_TOPIC)
    prop = _prompt_prop(FIXTURE_PROP, FIXTURE_TOPIC)

    # ── SUJETO: debe contener ──
    for token in ["Archival", "1980s", "vermilion", "pentagonal",
                  "strictly avoid", "three-quarter profile"]:
        _check(token in subj, f"SUJETO no contiene {token!r}", fails)

    # ── SUJETO: NO debe contener (el look viejo) ──
    for token in ["Isolated technical study", "seamless background"]:
        _check(token not in subj, f"SUJETO todavía contiene {token!r}", fails)

    # ── PROP: contiene la década y SÍ el fondo neutro ──
    _check("1980s" in prop, "PROP no contiene la década '1980s'", fails)
    _check("seamless background" in prop, "PROP no contiene 'seamless background'", fails)

    # ── sin '..' dobles en ninguno ──
    _check(".." not in subj, "SUJETO tiene '..' doble", fails)
    _check(".." not in prop, "PROP tiene '..' doble", fails)

    print("─" * 60)
    print("PROMPT SUJETO:")
    print(subj)
    print("─" * 60)
    print("PROMPT PROP:")
    print(prop)
    print("─" * 60)

    if fails:
        print(f"[FAIL] {len(fails)} assert(s):")
        for f in fails:
            print(f"   ✗ {f}")
        return 1
    print("[PASS] todos los asserts OK (subject canon completo + prop con época)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
