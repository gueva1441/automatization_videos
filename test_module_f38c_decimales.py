"""
test_module_f38c_decimales.py — F38c §A.3 (HANDOFF_F38c_marcas_contradice_decimales): cómo se leen los decimales.
    `voz_utils._num_tok` usa la regla de miles de `num_es.parse_int`; si no son miles y hay un solo separador es
    decimal («722.50» = 722,5, no 72 250); con más de uno no es una cifra («25.10.2005»). Tabla §2(a) del handoff.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from script_engine import pantalla_filtros as pf  # noqa: E402
from script_engine import voz_utils as vu  # noqa: E402

# tabla §2(a): token → valor con el arreglo (los de miles quedan como los lee parse_int hoy)
TABLA = [
    ("722.50", 722.5),
    ("0.0282", 0.0282),
    ("1.910", 1910.0),
    ("2.600", 2600.0),
    ("6,500", 6500.0),
    ("55.645.758.500", 55645758500.0),
    ("0,5", 0.5),
    ("1,5", 1.5),
    ("22.39", 22.39),
    ("8.30", 8.3),
    ("25.10.2005", None),
]


@pytest.mark.parametrize("tok,esperado", TABLA)
def test_num_tok_tabla_2a(tok, esperado):
    assert vu._num_tok(tok) == esperado


def test_contradicciones_lee_722_5_y_no_72250():
    v = "La cota autorizada fue de setecientos quince."
    out = pf.contradicciones("COTA MÁXIMA 722.50 metros", [v], cerca=[v])
    txt = " ".join(map(str, out if isinstance(out, (list, tuple)) else [out]))
    assert "722.5" in txt and "715" in txt
    assert "72250" not in txt
