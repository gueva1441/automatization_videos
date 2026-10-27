"""F3 (pedido de Omar 2026-10-20): pico del capítulo, nivel de agua, reloj de esquina, zoom con latido, corte a negro."""
from __future__ import annotations

import json
from dataclasses import replace

from script_engine import gfx_peak as gp
from script_engine.gfx_project import GfxScene

MOODS = {"agua": {"triggers": {"sumergidos": 3, "agua": 1, "ahogaba": 3}},
         "oscuridad_encierro": {"triggers": {"oscuro": 1, "encierro": 2}}}


def W(text: str, t0: float = 0.0, step: float = 0.4) -> list[dict]:
    return [{"word": w, "start": round(t0 + k * step, 3), "end": round(t0 + k * step + 0.3, 3)} for k, w in enumerate(text.split())]


WORDS = W("Aquel 29 de agosto de 2005 todo cambió. Un manto oscuro cubrió la ciudad. "
          "Calles enteras quedaron sumergidas, sumergidos bajo 4.6 metros de agua putrefacta. "
          "El mundo exterior se ahogaba. Un nuevo tipo de encierro.")
CTX = {"facts": ["Algunas partes quedaron bajo 15 pies (4.6 metros) de agua.", "El huracán tocó tierra el 29 de agosto de 2005."],
       "eligible": {0: False, 1: False}, "fact_source": {}}


def test_candado_nivel_de_agua_y_reloj():
    from script_engine.gfx_literal_lock import lock
    src = {"verified_facts[0]": "Algunas partes quedaron bajo 15 pies (4.6 metros) de agua.",
           "verified_facts[1]": "El huracán tocó tierra el 29 de agosto de 2005."}
    plan = {"time_ticker": {"source_text": "29 de agosto de 2005", "times": []}}     # F37 §B.4: sin nivel de agua
    ok, rej = lock(plan, src, chapter_number=2)
    assert ok["time_ticker"] and not rej
    bad = {"time_ticker": {"source_text": "30 de agosto", "times": []}}
    ok, rej = lock(bad, src, chapter_number=2)
    assert ok["time_ticker"] is None and len(rej) == 1


def test_reloj_elige_la_esquina_libre():
    from script_engine.voz_datos import ticker_corner                         # F36 §D: el reloj vive en voz_datos
    tk = {"start": 6.0, "duration": 20.0}
    ticker_corner(tk, {"archive_clippings": [{"start": 9.9, "duration": 4.0, "side": "left"}]})
    assert tk["side"] == "right" and tk["start"] == 6.0
    tk = {"start": 6.0, "duration": 20.0}
    ticker_corner(tk, {"callouts": [{"start": 8.0, "duration": 2.5, "side": "right"}]})
    assert tk["side"] == "left"
    tk = {"start": 6.0, "duration": 20.0}
    ticker_corner(tk, {"callouts": [{"start": 8.0, "duration": 2.5, "side": "right"}],
                          "archive_clippings": [{"start": 9.0, "duration": 4.0, "side": "left"}]})
    assert tk["start"] == 13.3 and tk["duration"] == 12.7                    # las dos ocupadas → arranca después


def test_f4_golpes_escalan_el_contenedor_del_video(tmp_path, monkeypatch):
    """F4 §3: golpe de zoom y corte+golpe animan #vw (el frame del <video> va adentro). F36 §D: sin la lupa."""
    from script_engine import gfx_project
    from script_engine.gfx_project import write_project
    assert gfx_project.gfx_rules.zoom_freeze_frame is False
    monkeypatch.setattr(gfx_project, "_extract_freeze", lambda base, t, out: True)
    (tmp_path / "public").mkdir()
    (tmp_path / "public" / "base.mp4").write_bytes(b"x")
    plan = {"chapter_number": 2, "punch_in": [3.0], "transitions": {"1": {"kind": "cut_punch", "frames": 0, "rank": "R1"}}}
    write_project(plan, [GfxScene(0, 0.0, 8.0), GfxScene(1, 8.0, 16.0)], tmp_path, duration=16.0, width=2560, height=1440, fps=30)
    s1 = (tmp_path / "compositions" / "scene_01.html").read_text(encoding="utf-8")
    s2 = (tmp_path / "compositions" / "scene_02.html").read_text(encoding="utf-8")
    assert 'tl.to("#vw01", { scale: 1.015' in s1 and 'tl.fromTo("#vw02", { scale:' in s2
