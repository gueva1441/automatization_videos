"""F51a — el armado C de F50h en producción: sujeto · aspecto · lugar+año · cartel · luz · técnica · estilo · cierre,
sin mirada, objeto, paleta, style_head ni STYLE_TAIL. Offline."""
import json
import sys
from pathlib import Path

import pytest

from script_engine import m03_imagenes_v3 as v3

ROOT = Path(__file__).resolve().parent
SLOTS = {"subject": "a miner", "action": "loading ore", "gaze_interaction": "eyes down", "props_detail": "a sack",
         "setting": "the mill yard", "lighting": "harsh noon", "color_palette": "ochre", "shot_scale": "wide",
         "camera_angle": "eye-level", "lens_technique": "35mm", "people_group": ["miners"],
         "text_in_image": {"present": True, "text": "DANGER", "font": "stencil", "location": "on the gate"}}
GRUPOS = {"miners": {"id": "miners", "appearance": "Lean men with sun-darkened skin"}}


def test_f51a_orden_c_con_cartel_y_un_grupo():
    a = v3.armar(SLOTS, "1962", GRUPOS)
    assert list(a["partes"]) == ["sujeto", "aspecto", "lugar_anio", "texto", "luz", "tecnica", "estilo", "cierre"]
    assert a["prompt"] == (
        "A miner. Loading ore. Lean men with sun-darkened skin. The mill yard, 1962. "
        'The words "DANGER" are written on the gate in stencil, in clear crisp lettering. Harsh noon. '
        "Wide shot, eye-level, 35mm. A grainy 35mm documentary photograph taken in 1962, with muted colors and slight "
        "underexposure, in a dark-history realist style. The image has a 16:9 aspect ratio.")


def test_f51a_sin_mirada_objeto_paleta_ni_estilo_viejo():
    assert not hasattr(v3, "style_head") and not hasattr(v3, "STYLE_TAIL")
    assert not {"gaze_interaction", "props_detail", "color_palette"} & set(v3._PROSA)
    p = v3.armar(SLOTS, "1962", GRUPOS)["prompt"]
    assert "Eyes down" not in p and "A sack" not in p and "ochre" not in p.lower()


def test_f51a_contrato_20_fotos_de_f50h():
    """Las 20 fotos de F50h con el armado y el post-proceso de producción = PROMPTS_F50h.json → C, byte a byte."""
    tid = "123bbb64-9fca-4395-8bf4-57d60e219ef1"
    esperado_f = ROOT / "lab" / "hyperframes" / "f50h" / "PROMPTS_F50h.json"
    vivo = ROOT / "data" / "scripts" / "_steps" / tid / "03_visual.json"
    if not (esperado_f.exists() and vivo.exists()):
        pytest.skip("sin los datos de Wittenoom")
    sys.path.insert(0, str(ROOT / "lab" / "hyperframes" / "f51a"))
    import contrato
    assert contrato.main() == 0
