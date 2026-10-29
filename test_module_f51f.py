"""F51f — la frase del cartel con una sola forma: «… in clear crisp {font} lettering» (sin repetir «lettering/letters»;
sin font, «in clear crisp lettering»); un texto de una sola palabra va «The word "X" is …». Los 8 fonts reales de
Wittenoom (03_visual.json de F51d-A). Offline."""
import pytest

from script_engine import m03_imagenes_v3 as v3


@pytest.mark.parametrize("font, sale", [
    ("painted block lettering", "in clear crisp painted block lettering"),
    ("typewriter", "in clear crisp typewriter lettering"),
    ("handwritten ink", "in clear crisp handwritten ink lettering"),
    ("bold serif newsprint headline", "in clear crisp bold serif newsprint headline lettering"),
    ("highway sign sans-serif", "in clear crisp highway sign sans-serif lettering"),
    ("block stencil", "in clear crisp block stencil lettering"),
    ("carved", "in clear crisp carved lettering"),
    ("block", "in clear crisp block lettering"),
    ("Metal block letters", "in clear crisp metal block lettering"),
    ("", "in clear crisp lettering"),
])
def test_f51f_los_fonts_de_wittenoom(font, sale):
    p = v3.frase_cartel({"present": True, "text": "DANGER ASBESTOS", "font": font, "location": "on the warning sign"})
    assert p == f'The words "DANGER ASBESTOS" are written on the warning sign {sale}.'
    assert p.count("lettering") == 1 and ", in clear" not in p


def test_f51f_las_tres_aperturas_quedan():
    t = {"present": True, "text": "ROAD CLOSED", "font": "block stencil"}
    assert v3.frase_cartel({**t, "location": ""}) == 'A sign reads "ROAD CLOSED" in clear crisp block stencil lettering.'
    assert v3.frase_cartel({**t, "location": "the barricade sign"}) == \
        'The barricade sign reads "ROAD CLOSED" in clear crisp block stencil lettering.'
    assert v3.frase_cartel({**t, "location": "on the barricade"}) == \
        'The words "ROAD CLOSED" are written on the barricade in clear crisp block stencil lettering.'


def test_f51f_una_sola_palabra():
    assert v3.frase_cartel({"present": True, "text": "WITTENOOM", "font": "highway sign sans-serif",
                            "location": "on the fallen sign panel in the dust"}) == \
        'The word "WITTENOOM" is written on the fallen sign panel in the dust in clear crisp highway sign sans-serif lettering.'
