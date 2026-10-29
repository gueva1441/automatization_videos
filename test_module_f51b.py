"""F51b — el pedido del canon separa `appearance` (solo rasgos fijos) de `condition_by_period` (el estado documentado),
y la oración de estilo C sin año va sin «taken in». Offline."""
import sys
from pathlib import Path

import pytest

from researcher_steps import step_4e_visual_canon as s4e
from script_engine import m03_imagenes_v3 as v3

ROOT = Path(__file__).resolve().parent
SLOTS = {"subject": "a miner", "action": "loading ore", "setting": "the mill yard", "lighting": "harsh noon",
         "shot_scale": "wide", "text_in_image": {"present": False}}


def test_f51b_pedido_con_las_dos_lineas_nuevas_y_sin_la_vieja():
    t = s4e.TEXTO_1_PEOPLE_GROUPS
    assert ("- appearance: solo los rasgos físicos fijos de la persona según su origen documentado: tono de piel, "
            "color y tipo de pelo, color de ojos, rasgos de la cara y contextura (EN, una frase). Nada que cambie según "
            "dónde estén, qué hagan o qué les pase: eso va en condition_by_period\n") in t
    assert ("- condition_by_period: una entrada por cada tramo de años en que el material documenta un estado físico "
            "de ese grupo (polvo, suciedad, bronceado, heridas, enfermedad, desgaste); years \"AAAA-AAAA\" y condition "
            "(EN, una frase). Si el material no documenta ningún estado, lista vacía\n") in t
    assert "según su origen documentado y su época" not in t and "contextura típica de su trabajo" not in t
    assert t.endswith("dejá appearance vacío.")                      # la frase final queda igual
    assert t in s4e.bloque_people_groups({})


def test_f51b_condition_by_period_sobrevive_la_limpieza(monkeypatch):
    g = {"id": "miners", "who": "w", "where_when": "ww", "appearance": "lean",
         "condition_by_period": [{"years": "1950-1966", "condition": "coated in fine dust"}],
         "clothing_by_period": []}
    resp = {"era_visual_canon": {"periods": [{"years": "1950-1966"}]}, "people_groups": [g]}
    monkeypatch.setattr(s4e.claude_helpers, "call_json", lambda *a, **k: resp)
    out = s4e.extract_visual_canon(seed={"seed_title": "t"}, angle_blocks={}, verified_facts=[{"fact": "f"}],
                                   canonical=None, extra="")
    assert out["people_groups"][0]["condition_by_period"] == g["condition_by_period"]


def test_f51b_estilo_sin_anio_sin_taken_in():
    p = v3.armar(SLOTS, "")
    assert p["partes"]["estilo"] == ("A grainy 35mm documentary photograph, with muted colors and slight "
                                     "underexposure, in a dark-history realist style.")
    assert "taken in" not in p["prompt"]
    assert v3.armar(SLOTS, "1962")["partes"]["estilo"] == v3.ESTILO_C.format(anio="1962")   # con año, igual que F51a


def test_f51b_el_armado_no_pega_condition_by_period():
    grupos = {"miners": {"id": "miners", "appearance": "Lean men",
                         "condition_by_period": [{"years": "1950-1966", "condition": "coated in fine dust"}]}}
    p = v3.armar({**SLOTS, "people_group": ["miners"]}, "1962", grupos)["prompt"]
    assert "Lean men." in p and "dust" not in p


def test_f51b_contrato_f51a_sigue_verde():
    if not (ROOT / "lab" / "hyperframes" / "f50h" / "PROMPTS_F50h.json").exists():
        pytest.skip("sin los datos de Wittenoom")
    sys.path.insert(0, str(ROOT / "lab" / "hyperframes" / "f51a"))
    import contrato
    assert contrato.main() == 0
