"""
lab/hyperframes/f36/diff_guion.py — F36: diff de dos GUION_PANTALLA.json sin los metadatos de la corrida.

Se sacan `generado`, `tiempos_s` (los que nombra el handoff), `costos` (lo que gastó ESA corrida: con caché da 0) y
`mezcla.segundos` (el tiempo de pared de la mezcla). Medido en la base: el guion de F34 B regenerado con caché sobre
1973ba1 difiere de lab/hyperframes/f34/GUION_PANTALLA.json solo en esas cuatro claves (a/plan_only_base.log).

    python lab/hyperframes/f36/diff_guion.py <viejo.json> <nuevo.json>      → imprime el diff (vacío = idénticos)
"""
from __future__ import annotations

import difflib
import json
import sys
from pathlib import Path


def limpio(p: str) -> list[str]:
    g = json.loads(Path(p).read_text(encoding="utf-8"))
    for k in ("generado", "tiempos_s", "costos"):
        g.pop(k, None)
    if isinstance(g.get("mezcla"), dict):
        g["mezcla"].pop("segundos", None)
    return json.dumps(g, ensure_ascii=False, indent=1, sort_keys=True).splitlines()


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    a, b = sys.argv[1], sys.argv[2]
    d = list(difflib.unified_diff(limpio(a), limpio(b), a, b, lineterm="", n=2))
    print("\n".join(d))
    print(f"--- {len([x for x in d if x[:1] in '+-' and x[:3] not in ('+++', '---')])} líneas distintas", file=sys.stderr)
