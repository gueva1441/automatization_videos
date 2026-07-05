"""
test_module_137_thumbs_ley1.py — HANDOFF_137a (offline, lint de plantilla, sin API).

LEY 1 "PINTOR-NO-ACTOR" portada al `_HERO_SYSTEM` de m09 (miniaturas): la emoción se
escribe SOLO como física pintable + el cuerpo carga la situación del beat. Verifica que
la doctrina nueva está y que la forma vieja ("inquietud, desasosiego — NUNCA") ya no.
NO llama a Gemini ni a fal: solo inspecciona el string del prompt.

USO:
    python test_module_137_thumbs_ley1.py
"""
import sys

import script_engine.m09_packaging as m09


def _check(cond: bool, msg: str, fails: list) -> None:
    if not cond:
        fails.append(msg)


def main() -> int:
    fails: list[str] = []
    hs = m09._HERO_SYSTEM

    # ── doctrina nueva presente ──
    # HANDOFF_138a: la doctrina LEY 1 ahora se HEREDA de m03 (bloques DOCTRINE_* en inglés);
    # 'física pintable' sigue en la capa CTR propia del hero.
    for token in ["física pintable", "BODY CARRIES THE SITUATION", "PHYSICAL TRANSLATION"]:
        _check(token in hs, f"LEY1 falta {token!r} en _HERO_SYSTEM", fails)

    # ── forma vieja (abstracción) ELIMINADA ──
    _check("inquietud, desasosiego — NUNCA" not in hs,
           "LEY1: _HERO_SYSTEM TODAVÍA tiene la forma vieja 'inquietud, desasosiego — NUNCA'", fails)

    if fails:
        print(f"[FAIL] {len(fails)} assert(s):")
        for f in fails:
            print(f"   ✗ {f}")
        return 1
    print("[PASS] LEY 1 (pintor-no-actor) presente en _HERO_SYSTEM + forma vieja fuera")
    return 0


if __name__ == "__main__":
    sys.exit(main())
