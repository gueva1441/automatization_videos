"""F22 §3 — «cero Cardal»: dada una salida (columna, escaleta o guion, en texto), las palabras del caso inventado de los
ejemplos (`CASO_EJEMPLO_cardal.md`) que aparecen. Determinista, sin red.

Nombres y lugares: palabra entera (sin tildes ni mayúsculas, `nombres.norm`). Los dos sustantivos comunes de la lista
(«querosén», «telegrama») cuentan con cualquier terminación («queroseno», «telegramas»): son los que un modelo copia con
otra forma.
Uso: python -I lab/hyperframes/f22/cero_cardal.py <archivo> [...]
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

PALABRAS = ("Cardal", "Soto", "Bascuñán", "Quiroga", "Marín", "Alborada", "Faros y Balizas")
RAICES = ("querosén", "telegrama")


def _pat(w: str, raiz: bool) -> re.Pattern:
    from script_engine import nombres
    t = r"\s+".join(re.escape(x) for x in nombres.norm(w).split())
    return re.compile(rf"(?<![^\W\d_]){t}" + (r"[^\W\d_]*" if raiz else r"(?![^\W\d_])"))


def coincidencias(texto: str) -> dict[str, int]:
    """{palabra: veces} de las palabras del caso inventado en `texto` (vacío = cero Cardal)."""
    from script_engine import nombres
    t = nombres.norm(texto)
    out = {}
    for w, raiz in [(w, False) for w in PALABRAS] + [(w, True) for w in RAICES]:
        n = len(_pat(w, raiz).findall(t))
        if n:
            out[w] = n
    return out


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    for a in sys.argv[1:]:
        print(a, coincidencias(Path(a).read_text(encoding="utf-8")) or "cero Cardal")


if __name__ == "__main__":
    main()
