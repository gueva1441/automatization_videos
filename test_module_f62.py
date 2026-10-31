# -*- coding: utf-8 -*-
"""F62 — objetos de época: la regla 2 del pedido del canon visual (step_4e) pide el modelo o tipo concreto de uso común
en technology / vehicles_machinery y ya no pide lo genérico (HANDOFF_F62_objetos_de_epoca)."""
from __future__ import annotations

from researcher_steps import step_4e_visual_canon as s4e

TOPIC = {"video_title": "Wittenoom", "canonical_subject_description": "a mining town",
         "people_groups": [{"id": "g1", "who": "Spanish migrant miners", "where_when": "Wittenoom 1962-1966",
                            "appearance": "Southern European features"}]}
FICHA = {"hechos": [], "personas": [], "secciones": {}}


def _pedido() -> str:
    # el pedido envuelve las líneas a ~80 columnas: se compara con los espacios normalizados
    return " ".join(s4e.pedido_canon(TOPIC, FICHA).split())


def test_pedido_canon_pide_modelo_concreto_y_sin_logotipos():
    p = _pedido()
    assert "modelo o tipo concreto de uso común" in p
    assert "Sin logotipos ni texto pintado" in p
    assert "black Bakelite rotary-dial telephone" in p and "Bedford OB coach with a rounded bonnet" in p


def test_pedido_canon_ya_no_pide_lo_generico():
    p = _pedido()
    for frase in ("mantené genérico", "el más genérico", "genérica de la década", "genéricos de la década",
                  "analog gauges, vacuum tubes, rotary dials"):
        assert frase not in p, frase
    # lo que la regla 2 conserva: el detalle de un individuo nombrable sigue viviendo en documented_people
    assert "the captain wore a Rolex" in p and "documented_people, NO acá" in p
    assert "vehículos y aparatos con modelo concreto, ver regla 2" in p


def test_marca_canon_cambia_con_el_pedido():
    # la marca incluye el texto del pedido → cualquier tema rehace su canon en su próxima corrida (efecto declarado)
    m = s4e.marca_canon(TOPIC, FICHA, b"ficha")
    assert len(m) == 32 and m != s4e.marca_canon(TOPIC, {**FICHA, "secciones": {"x": "y"}}, b"ficha2")
