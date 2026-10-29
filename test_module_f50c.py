"""F50c — cableado del expediente de foto: personas desde la ficha (A), citas con autor (B), grupos con aspecto y ropa
(C) y la chascada de `_sin_negadas` (D). Offline, sin modelos."""
from script_engine import m03_imagenes_v3 as v3


# ─────────────────────────── D. chascada de _sin_negadas ───────────────────────────
def test_f50c_d_cell_no_cifra_queda():
    assert v3._sin_negadas("Cell No. 5, a bare room") == "Cell No. 5, a bare room"


def test_f50c_d_no_cifra_al_inicio_queda():
    assert v3._sin_negadas("No. 4 Shaft, dusty") == "No. 4 Shaft, dusty"


def test_f50c_d_nothing_but_queda():
    assert v3._sin_negadas("a flat plain, nothing but red dust") == "a flat plain, nothing but red dust"
    assert v3._sin_negadas("a flat plain, with nothing but red dust") == "a flat plain, with nothing but red dust"


def test_f50c_d_with_no_sale():
    assert v3._sin_negadas("an empty street, with no figure anywhere") == "an empty street"


def test_f50c_d_without_queda():
    assert v3._sin_negadas("a playground, swings without seats") == "a playground, swings without seats"


def test_f50c_d_todo_negado_vacio():
    assert v3._sin_negadas("no work, no vehicles") == ""
