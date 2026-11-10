"""
test_module_f79.py — F79 (lab/hyperframes/f79/HANDOFF_F79.md), aire muerto fuera.
    A2: el primer cap del video no lleva title card (`gfx_layer.plan_base(ctx, primero=…)`, con `ChapterPlan.is_first`);
        un video de un solo cap no lleva ninguno; el guion de pantalla de un cap sin title card no lo nombra (ni en el
        evento, ni en la costura, ni en `tramos`) y su título sigue en el encabezado.
Sin red, sin escribir fuera de tmp.
"""
from __future__ import annotations

from script_engine import gfx_guion as gg
from script_engine.gfx_layer import plan_base
from test_module_f32 import _cap, _plan_todo

CTX = {"chapter_number": 1, "skeleton": {"title": "La herida que no cerraba"}}


def test_a2_el_primer_cap_no_lleva_title_card():
    assert plan_base(CTX, primero=True)["title_card"] is None
    tc = plan_base({**CTX, "chapter_number": 2}, primero=False)["title_card"]
    assert tc == {"kicker": "CAPÍTULO 2", "title": "La herida que no cerraba"}


def test_a2_cap_sin_title_card_en_el_guion():
    plan = {**_plan_todo(), "title_card": None}
    cap = {**_cap(plan, first=True), "cap": "ch01", "n": 1, "titulo": "La herida que no cerraba"}
    g = gg.armar([cap], title_dur=3.0, dip_frames=10, fps=30, mezcla=None, voz_video=[], topic="fix")
    ev = g["caps"][0]["eventos"]
    assert "title card" not in {e["tipo"] for e in ev}
    costura = next(e for e in ev if e["tipo"] == "costura")
    assert "title card" not in costura["texto"] and "title_card_s" not in costura["tramos"]
    assert costura["texto"].startswith("el mp4 arranca con este cap → voz a ")
    md = gg.a_markdown(g)
    assert "## ch01 — La herida que no cerraba (" in md
