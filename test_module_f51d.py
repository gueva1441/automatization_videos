"""F51d-A chascada — el expediente rotula el respaldo del año «2)/3)/4)» en el origen y `anio_final` lo pasa tal cual
(sin el regex de F51c). Offline."""
import pytest

from script_engine import m03_expediente as mexp
from script_engine import m03_imagenes_v3 as v3


@pytest.mark.parametrize("anio_prev, beat, year, sale", [
    ("1958", {"n": 1, "fecha": "1961-05-01"}, "1990",
     ("1958", "2) el último año dicho en la narración de los caps anteriores")),
    (None, {"n": 1, "fecha": "1961-05-01"}, "1990", ("1961", "3) la fecha del dato_central del beat")),
    (None, {"n": 1}, "1990", ("1990", "4) topic_year")),
])
def test_f51d_rotulos_del_respaldo_y_anio_final_los_pasa_tal_cual(anio_prev, beat, year, sale):
    e = mexp.expedientes({}, {}, [beat], ["Una voz sin año."], [{"beat": 1}], anio_prev, year)[0]
    assert tuple(e["respaldo"]) == sale
    assert v3.anio_final(e, {}) == sale                                # sin `year` del modelo: el respaldo tal cual
    assert v3.anio_final(e, {"year": "1975"}) == ("1975", "1) el casillero `year` del modelo")
