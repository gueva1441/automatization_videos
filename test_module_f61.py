# -*- coding: utf-8 -*-
"""F61 — variedad de planos: sin R7 en el system instruction de casilleros, sin «a lo sumo un cuarto» en
COMPOSITION_RULES_V3 y sin el tope del 25 % en `video_audit`; el encuadre lo decide VISUAL ARC OF THIS CAP (HANDOFF_F61_planos)."""
from __future__ import annotations

import inspect

from script_engine import m03_imagenes_v3 as v3img
from script_engine import m03_visual as m3


def test_si_casilleros_sin_r7_ni_cuarto_y_con_establecimiento():
    si = m3.SYSTEM_INSTRUCTION_CASILLEROS
    for frase in ("dominates", "ONLY for one human emotion", "QUARTER", "prefer places, objects, distance"):
        assert frase not in si, frase
    assert "Every cap has at least ONE establishing" in si
    assert "- shot_scale: one of extreme_wide|wide|medium|close|detail, following the VISUAL ARC OF THIS CAP block when it is present." in si
    assert "- camera_angle: e.g. low angle for scale, eye-level, high angle (R7)." in si      # la l. 184 no se toca
    # la misma línea está en el SI v2 y v3 (la cadena SYSTEM_INSTRUCTION_VISUAL_SEEDREAM → _V3 → _si_casilleros)
    assert "following the VISUAL ARC OF THIS CAP block" in m3.SYSTEM_INSTRUCTION_VISUAL_SEEDREAM
    assert "QUARTER" not in v3img.COMPOSITION_RULES_V3 and "4. Every cap has at least ONE establishing / exterior image" in v3img.COMPOSITION_RULES_V3


def test_video_audit_sin_humano_medio_y_con_caps_sin_establecimiento():
    assert not hasattr(v3img, "human_medium")
    caps = [[{"shot_scale": "medium", "subject": "a man", "prompt": "a man", "subject_ref": "main_subject"}],
            [{"shot_scale": "extreme_wide", "subject": "the town", "prompt": "the town", "subject_ref": "establishing_shot"}]]
    a = v3img.video_audit(caps)
    assert "exceso_humano_medio" not in a and "humano_medio" not in a
    assert a["caps_sin_establecimiento"] == [1] and a["total"] == 2
    assert set(a) == {"total", "motivos", "exceso_motivos", "cuerpos", "exceso_cuerpos", "caps_sin_establecimiento"}
    assert v3img.establishing(caps[1][0]) and not v3img.establishing(caps[0][0])


def test_f8_fix_video_ya_no_rehace_planos_medios_y_sigue_motivos_y_cuerpos():
    src = inspect.getsource(m3._f8_fix_video)
    assert "exceso_humano_medio" not in src and "NO person in medium shot" not in src and "humano_medio" not in src
    assert 'cur["exceso_motivos"]' in src and 'cur["exceso_cuerpos"]' in src
    assert m3.F8_FIX_PASSES == 2
    # lo que queda de «D5»: establecimiento por cap
    assert "F8_NOTE_ESTABLISHING" in inspect.getsource(m3._f8_fix_cap) and m3.F8_NOTE_CERRADA and callable(v3img.establishing)
    assert "VISUAL ARC OF THIS CAP" in m3._visual_arc_block("shock") and m3._visual_arc_block(None) == ""
