"""
test_module_m03_reglas_133.py — HANDOFF_133 (offline, lint de plantilla, sin API).

Verifica que las 4 reglas nuevas ("el canon como contrato") están presentes en la
plantilla del path ACTIVO (seedream) y que visual_reference_availability salió del
bloque de contexto. NO llama a Gemini ni a fal: solo inspecciona strings.

Nota de alcance (HANDOFF_133): m03 SOLO soporta image_engine='seedream' (guard duro en
assign_visual_prompts; los paths flux/kling/veo-old fueron removidos en chat 117). El
"builder viejo" `_format_visual_canon_block` NO tiene callers → dead code → no se toca.

USO:
    python test_module_m03_reglas_133.py
"""
import sys

import script_engine.m03_visual as m03
from script_engine.topics_db import load_db

FIXTURE_TID = "ec3d7c7f-c7f7-4fbe-9c91-2ed5e05cfb76"


def _check(cond: bool, msg: str, fails: list) -> None:
    if not cond:
        fails.append(msg)


def main() -> int:
    fails: list[str] = []
    si = m03.SYSTEM_INSTRUCTION_VISUAL_SEEDREAM

    # ── REGLA 1: estado por beat + ancla respeta estado (slot foto_madre_ref) ──
    for token in ["STATE MUST MATCH THE BEAT", "STATE BY BEAT", "condition_evolution"]:
        _check(token in si, f"R1 falta {token!r} en la system-instruction", fails)

    # ── REGLA 2: personas (paquete de 3) ──
    for token in ["DEMOGRAPHY IS MANDATORY", "GROUPS — compose first",
                  "rim-lit silhouette", "ORDINARY PERIOD FACES",
                  "never by reference to an actor"]:
        _check(token in si, f"R2 falta {token!r} en la system-instruction", fails)
    _check("demographics" in si, "R2 no referencia 'demographics'", fails)

    # ── REGLA 3: campos de época condicionales ──
    _check("ERA FIELDS ON DEMAND" in si, "R3 falta 'ERA FIELDS ON DEMAND'", fails)
    for token in ["clothing", "interiors", "vehicles_machinery", "technology"]:
        _check(token in si, f"R3 no referencia el campo {token!r}", fails)

    # ── REGLA 4: visual_reference_availability ECHADO del bloque de contexto ──
    topic = next((t for t in load_db().get("topics", []) if t.get("id") == FIXTURE_TID), None)
    _check(topic is not None, f"fixture topic {FIXTURE_TID} no está en topics_db", fails)
    if topic is not None:
        cb = m03._format_seedream_canon_block(topic)
        _check("visual_reference_availability" not in cb,
               "R4: visual_reference_availability TODAVÍA está en el bloque de contexto", fails)
        # el resto del canon sigue viajando (no rompimos el contexto)
        _check("demographics" in cb, "R4: el bloque perdió 'demographics' (regresión)", fails)
        _check("condition_evolution.at_event" in cb,
               "R4: el bloque perdió 'condition_evolution' (regresión)", fails)

    # ── ALCANCE: el builder viejo sigue sin callers (dead code, no lo tocamos) ──
    import inspect
    src = inspect.getsource(m03)
    _check(src.count("_format_visual_canon_block(") == 1,
           "el builder viejo ahora TIENE un caller — revisar alcance", fails)

    if fails:
        print(f"[FAIL] {len(fails)} assert(s):")
        for f in fails:
            print(f"   ✗ {f}")
        return 1
    print("[PASS] 4 reglas presentes en el path seedream + visual_reference_availability fuera")
    return 0


if __name__ == "__main__":
    sys.exit(main())
