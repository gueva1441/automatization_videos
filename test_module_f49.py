"""F49 — chascada de F8: `fix_counts_lr` se lleva el artículo junto con la cifra («The two men» ya no da «The a couple
of men»)."""
from script_engine import m03_imagenes_v3 as v3


def test_articulo_se_va_con_la_cifra():
    assert v3.fix_counts_lr("The two men sit") == "A couple of men sit"
    assert v3.fix_counts_lr("two men sit") == "a couple of men sit"
    assert v3.fix_counts_lr("The three inmates") == "A few inmates"
    assert v3.fix_counts_lr("Behind them, the two men wait.") == "Behind them, a couple of men wait."
    assert "a couple of" not in v3.fix_counts_lr("The two of them wait.")   # sin persona después: no es conteo
