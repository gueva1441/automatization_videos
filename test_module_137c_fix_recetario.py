"""
test_module_137c_fix_recetario.py — HANDOFF_137c (offline, lint de instrucción, sin red).

El traductor criollo→prompt del QA (/fix_image, `_FIX_REWRITE_INSTRUCTION`) pasa a
EXPERTO: recetario de traducción (reemplazo positivo, pintor-no-actor, cuerpo carga la
situación, cambios quirúrgicos) + guardrail 1 corregido de doctrina Flux-era (FACELESS)
a doctrina seedream/LEY 1 (PERSONAS GENÉRICAS — la cara SÍ puede verse, se prohíbe la
identidad real). Verifica presencia de la doctrina nueva y ausencia de la forma vieja.
NO llama a Gemini: solo inspecciona el string.

USO:
    python test_module_137c_fix_recetario.py
"""
import sys

import qa_studio_server as qa


def _check(cond: bool, msg: str, fails: list) -> None:
    if not cond:
        fails.append(msg)


def main() -> int:
    fails: list[str] = []
    ins = qa._FIX_REWRITE_INSTRUCTION

    # ── doctrina nueva presente ──
    for token in ["REEMPLAZO POSITIVO", "PINTOR-NO-ACTOR",
                  "EL CUERPO CARGA LA SITUACIÓN", "PERSONAS GENÉRICAS"]:
        _check(token in ins, f"137c falta {token!r} en _FIX_REWRITE_INSTRUCTION", fails)

    # ── forma vieja (guardrail Flux-era FACELESS) ELIMINADA ──
    _check("FACELESS — nunca una cara identificable" not in ins,
           "137c: _FIX_REWRITE_INSTRUCTION TODAVÍA tiene el guardrail viejo "
           "'FACELESS — nunca una cara identificable'", fails)

    if fails:
        print(f"[FAIL] {len(fails)} assert(s):")
        for f in fails:
            print(f"   ✗ {f}")
        return 1
    print("[PASS] recetario 137c presente en _FIX_REWRITE_INSTRUCTION + guardrail FACELESS fuera")
    return 0


if __name__ == "__main__":
    sys.exit(main())
