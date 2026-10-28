# -*- coding: utf-8 -*-
"""F50 A §2 — verificación en seco (sin API): el pedido del canon de producción para Wittenoom (sistema + usuario +
esquema) tiene el mismo md5 que el de la regeneración S5 de F48 (`f48.canon_s5`, con la llamada a Flash atrapada).

Uso: python lab/hyperframes/f50/verificar_a.py   → imprime los md5 y sale 1 con el diff si no coinciden.
"""
from __future__ import annotations

import difflib
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HF = ROOT / "lab" / "hyperframes"
sys.path[:0] = [str(ROOT), str(HF / "f48"), str(HF / "f47")]


def _md5(s: str) -> str:
    return hashlib.md5(s.encode("utf-8")).hexdigest()


def _schema_txt(schema) -> str:
    return json.dumps(schema.model_dump(mode="json", exclude_none=True), ensure_ascii=False, sort_keys=True)


def atrapar(fn) -> dict:
    """Corre `fn` con `step_4e.call_flash_json` reemplazada por una que guarda el primer pedido y devuelve {}."""
    from researcher_steps import step_4e_visual_canon as s4e
    pedidos = []
    orig = s4e.call_flash_json

    def falsa(prompt, response_schema=None, **k):
        pedidos.append({"system": k.get("system_instruction") or "", "user": prompt,
                        "schema": _schema_txt(response_schema) if response_schema is not None else ""})
        return {}
    s4e.call_flash_json = falsa
    try:
        fn()
    finally:
        s4e.call_flash_json = orig
    return pedidos[0]


def main() -> int:
    import f48_corridas as f48
    from researcher_steps import step_4e_visual_canon as s4e
    f47 = f48.f47
    d = f47.cargar(2)
    canon_c = {k: v for k, v in f47._j(f47.CANON_C).items() if k != "facts_de_la_ficha"}
    lab = atrapar(lambda: f48.canon_s5(d, canon_c))
    prod = atrapar(lambda: s4e.canon_desde_ficha(d["topic"], d["ficha"]))
    ok = True
    for k in ("system", "user", "schema"):
        a, b = _md5(lab[k]), _md5(prod[k])
        print(f"  {k:6s}  lab {a}  producción {b}  {'=' if a == b else 'DISTINTO'}")
        if a != b:
            ok = False
            sys.stdout.writelines(difflib.unified_diff(lab[k].splitlines(True), prod[k].splitlines(True),
                                                       "lab", "producción"))
    total_lab = _md5(lab["system"] + lab["user"] + lab["schema"])
    total_prod = _md5(prod["system"] + prod["user"] + prod["schema"])
    print(f"  pedido entero: lab {total_lab} · producción {total_prod} → {'IGUAL' if ok else 'DISTINTO (PARADA)'}")
    print(f"  largo del usuario: {len(prod['user'])} caracteres; esquema con people_groups: "
          f"{'people_groups' in prod['schema']}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
