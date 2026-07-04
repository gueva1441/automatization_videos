"""
test_module_03_leakage_retry.py — HANDOFF_134 (offline, sin API).

Verifica que REGLA 3 (text-leakage) pasó de FATAL-de-un-tiro a retry+feedback → backstop
scrub (espejo de Guarda 1), y la yapa del rótulo FAIL honesto:
  1. fuga intento 1, limpio intento 2 → prosa limpia, 0 WARN de degradación, sin excepción.
  2. fuga SIEMPRE → backstop: prosa scrubeada sin el fragmento, sin inglés roto, WARN, sin excepción.
  3. rótulo sancionado (text_in_image == lo entrecomillado) → exento (camino C), pasa al 1er intento.
  4. prosa que tras scrub queda < PROMPT_MIN_CHARS → VisualValidationError (terminal legítimo).
  5. yapa: _derive_failed_step('m01a', [...m07]) == 'm03' (no el mentiroso).

Mockea el módulo-level _fluidify_item; NO llama a Gemini.

USO:
    python test_module_03_leakage_retry.py
"""
import io
import sys
from contextlib import redirect_stdout

import script_engine.m03_visual as m03
from script_engine.m03_visual import VisualValidationError, PROMPT_MIN_CHARS
import fase1_5


class _Profile:   # dummy: el _fluidify_item real está mockeado, no se usa
    formula = ()
    aspect_ratio_text = ""


def _run_guard(it):
    """Corre el guard capturando stdout (para ver el WARN)."""
    buf = io.StringIO()
    with redirect_stdout(buf):
        prose = m03._fluidify_with_leakage_guard(it, [], _Profile(), [], cap_number=4, i=14)
    return prose, buf.getvalue()


def _patch_fluidify(sequence):
    """Reemplaza _fluidify_item por uno que devuelve sequence[call_idx] (último se repite)."""
    calls = {"n": 0}

    def fake(slots, locked, profile, label, max_attempts=3, extra_feedback=""):
        idx = min(calls["n"], len(sequence) - 1)
        calls["n"] += 1
        return sequence[idx]
    m03._fluidify_item = fake
    return calls


def main() -> int:
    fails: list[str] = []
    orig = m03._fluidify_item

    LEAK = ("a small glass vial bearing the word 'streptomycin' in faded ink, resting on a "
            "cold metal tray inside the dim, abandoned dispensary of the old asylum ward, "
            "grey overcast light falling through a cracked and grimy window onto dusty shelves.")
    CLEAN = ("a small glass vial resting on a cold metal tray inside the dim, abandoned "
             "dispensary of the old asylum ward, its worn surface bare under grey overcast light.")

    try:
        # ── (1) fuga → limpio en el 2do intento ──
        calls = _patch_fluidify([LEAK, CLEAN])
        prose, out = _run_guard({"text_in_image": {"text": ""}})
        if prose != CLEAN:
            fails.append(f"(1) no devolvió la prosa limpia del 2do intento: {prose!r}")
        if "DEGRADADA" in out:
            fails.append("(1) marcó DEGRADADA cuando el retry alcanzó")
        if calls["n"] != 2:
            fails.append(f"(1) esperaba 2 tejidos, hubo {calls['n']}")

        # ── (2) fuga SIEMPRE → backstop scrub ──
        _patch_fluidify([LEAK])
        prose, out = _run_guard({"text_in_image": {"text": ""}})
        if "streptomycin" in prose.lower() or "the word" in prose.lower():
            fails.append(f"(2) el backstop no sacó el fragmento: {prose!r}")
        if "  " in prose:
            fails.append("(2) quedó doble espacio (inglés roto)")
        if "bearing" in prose.lower():
            fails.append("(2) quedó la attach-word colgante ('bearing')")
        if "DEGRADADA" not in out:
            fails.append("(2) no emitió el WARN de degradación")
        if m03._find_text_leakage(prose, allow_intentional_text=True) is not None:
            fails.append("(2) la prosa scrubeada TODAVÍA fuga")

        # ── (3) rótulo sancionado → exento (camino C) ──
        SANCTIONED = ("a weathered wooden board showing the label 'HOSPITAL' above the "
                      "arched entrance of the crumbling asylum, lit by grey overcast light.")
        calls = _patch_fluidify([SANCTIONED])
        prose, out = _run_guard({"text_in_image": {"text": "HOSPITAL"}})
        if prose != SANCTIONED:
            fails.append(f"(3) camino C alteró la prosa sancionada: {prose!r}")
        if calls["n"] != 1:
            fails.append(f"(3) reintentó un rótulo sancionado (calls={calls['n']})")
        if "DEGRADADA" in out:
            fails.append("(3) degradó un rótulo sancionado")

        # ── (4) prosa que tras scrub queda inutilizable → VisualValidationError ──
        _patch_fluidify(["the word 'streptomycin'."])   # corta: tras scrub queda vacía
        raised = False
        try:
            _run_guard({"text_in_image": {"text": ""}})
        except VisualValidationError:
            raised = True
        if not raised:
            fails.append("(4) prosa inutilizable tras scrub NO levantó VisualValidationError")

        # ── (5) yapa: paso REAL, no from_step ──
        fs = fase1_5._derive_failed_step("m01a", ["m01a", "m01b", "normalizer_gate", "audio", "m07"])
        if fs != "m03":
            fails.append(f"(5) yapa: esperaba 'm03', dio {fs!r}")
        if fase1_5._derive_failed_step("m01a", ["m01a", "m01b", "normalizer_gate", "audio",
                                                "m07", "m03", "assemble"]) is not None:
            fails.append("(5) yapa: todo completo debería dar None (rótulo honesto)")
    finally:
        m03._fluidify_item = orig

    if fails:
        print(f"[FAIL] {len(fails)} assert(s):")
        for f in fails:
            print(f"   ✗ {f}")
        return 1
    print("[PASS] regla 3: retry→limpio, backstop scrub sin inglés roto, camino C exento, "
          "terminal legítimo, y yapa del rótulo honesto")
    return 0


if __name__ == "__main__":
    sys.exit(main())
