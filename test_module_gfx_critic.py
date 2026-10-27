"""F4e: crítico visual (gfx_critic) — veredictos, solo pasan los «suma», caché, error no vacía el cap, hoja de
contactos; y la marca de esquina apagada desde el perfil (queda el cierre)."""
from __future__ import annotations

import subprocess

import numpy as np
from PIL import Image

import gfx_config as gc
from script_engine import gfx_critic as cr


def W(text: str, step: float = 0.5) -> list[dict]:
    return [{"word": w, "start": round(k * step, 3), "end": round(k * step + 0.4, 3)} for k, w in enumerate(text.split())]


def _video(path, dur=12):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"testsrc=s=640x360:r=30:d={dur}",
                    "-pix_fmt", "yuv420p", str(path)], check=True)
    return path


def _plan():
    return {"emphasis": [{"word": "putrefacta", "category": "veneno_enfermedad", "start": 1.0, "duration": 2.5,
                          "icon": "biohazard", "icon_callout": True, "side": "right"},
                         {"word": "agua", "category": "agua", "start": 5.0, "duration": 2.5, "side": "left"}],
            "archive_clippings": [{"headline": "Katrina tocó tierra el 29 de agosto", "kicker": "2005", "start": 7.0,
                                   "duration": 4.0, "side": "left"}],
            "callouts": [{"text": "4.6 metros", "start": 3.0, "duration": 2.0, "side": "left"}],
            "water_level": {"value_text": "4.6", "unit": "metros", "height": 0.6, "start": 2.0, "duration": 4.5},
            "evidence_zoom": None, "count_up": None, "pico": {"t": 2.0, "block": "water_level", "word": "sumergidos"}}


def test_describe_y_bloques():
    b = cr.blocks(_plan())
    assert [x["kind"] for x in b] == ["icono", "nivel_agua", "dato", "sello", "recorte"]
    assert "ÍCONO «biohazard»" in b[0]["desc"] and "60 %" in b[1]["desc"] and "kicker «2005»" in b[4]["desc"]


