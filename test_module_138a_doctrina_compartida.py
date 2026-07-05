"""
test_module_138a_doctrina_compartida.py — HANDOFF_138a (offline, sin red).

La doctrina Seedream vive UNA sola vez (m03, bloques DOCTRINE_*) y el hero de miniaturas
(m09) la HEREDA por import — mata el doc-drift de doctrina paralela. Verifica:
 1. cada DOCTRINE_* está verbatim en SYSTEM_INSTRUCTION_VISUAL_SEEDREAM (fuente completa).
 2. cada DOCTRINE_* está verbatim en _HERO_SYSTEM (la herencia es real).
 3. 'Flux' NO aparece en m09_packaging.py (la mina de doc-drift murió).
 4. _HERO_SYSTEM tiene 'SEEDREAM 4.5' + el bloque 137e (3 conceptos) verbatim.
 5. _META_SYSTEM tiene 'CONTRATO DE RETENCIÓN'.
 6. SNAPSHOT: el SI ensamblado es IDÉNTICO (sha1) al del commit 678abea — ESTE assert
    protege el "cero cambio de doctrina en m03" del EDIT A.

USO:
    python test_module_138a_doctrina_compartida.py
"""
import hashlib
import pathlib
import sys

import script_engine.m03_visual as m03
import script_engine.m09_packaging as m09

# sha1 del SYSTEM_INSTRUCTION_VISUAL_SEEDREAM tal cual en el seal 678abea (pre-refactor).
SI_SHA_678ABEA = "93bacc713a96e70b5ff6d9b7d984bf851c27a5d7"
DOCS = ["DOCTRINE_R6_PHYSICAL_TRANSLATION", "DOCTRINE_BODY_CARRIES",
        "DOCTRINE_PEOPLE", "DOCTRINE_R5_CEILING"]


def _check(cond: bool, msg: str, fails: list) -> None:
    if not cond:
        fails.append(msg)


def main() -> int:
    fails: list[str] = []
    si = m03.SYSTEM_INSTRUCTION_VISUAL_SEEDREAM
    hs = m09._HERO_SYSTEM
    ms = m09._META_SYSTEM

    for k in DOCS:
        blk = getattr(m03, k)
        _check(blk in si, f"1: {k} NO está verbatim en SYSTEM_INSTRUCTION_VISUAL_SEEDREAM", fails)
        _check(blk in hs, f"2: {k} NO está verbatim en _HERO_SYSTEM (herencia rota)", fails)

    # 3: la mina 'Flux' murió en m09_packaging.py
    src = pathlib.Path(m09.__file__).read_text(encoding="utf-8")
    _check("Flux" not in src, "3: 'Flux' TODAVÍA aparece en m09_packaging.py (drift vivo)", fails)

    # 4: hero es Seedream + bloque 137e verbatim
    _check("SEEDREAM 4.5" in hs, "4: falta 'SEEDREAM 4.5' en _HERO_SYSTEM", fails)
    _check("DEVOLVÉS TRES CONCEPTOS, NO UNO. REGLA INVIOLABLE" in hs,
           "4: falta el bloque 137e (3 conceptos) en _HERO_SYSTEM", fails)

    # 5: contrato de retención en overlays
    _check("CONTRATO DE RETENCIÓN" in ms, "5: falta 'CONTRATO DE RETENCIÓN' en _META_SYSTEM", fails)

    # 6: SNAPSHOT — el SI ensamblado es idéntico al de 678abea (cero cambio en m03)
    sha = hashlib.sha1(si.encode("utf-8")).hexdigest()
    _check(sha == SI_SHA_678ABEA,
           f"6: SYSTEM_INSTRUCTION cambió — sha1 {sha} != {SI_SHA_678ABEA} (678abea). "
           f"El EDIT A NO quedó char-a-char idéntico.", fails)

    if fails:
        print(f"[FAIL] {len(fails)} assert(s):")
        for f in fails:
            print(f"   ✗ {f}")
        return 1
    print("[PASS] 138a: doctrina compartida m03→m09 + Flux muerto + SI byte-idéntico a 678abea")
    return 0


if __name__ == "__main__":
    sys.exit(main())
