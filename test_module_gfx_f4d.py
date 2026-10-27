"""F4d (Omar 2026-10-20): pico con preferencia (agua > recorte con fuente > zoom humano), recortes por cláusula
completa con las 3 mejores para Flash, marca con +1 px y el \\b de los íconos Lucide."""
from __future__ import annotations

import gfx_config as gc
from script_engine import gfx_intensity as gi
from script_engine import gfx_peak as gp
from script_engine.gfx_project import GfxScene

MOODS = {"agua": {"active": True, "layer": "agua", "triggers": {"agua": 1, "sumergidos": 3}},
         "veneno_enfermedad": {"active": True, "layer": "veneno", "triggers": {"putrefacta": 3}},
         "oscuridad_encierro": {"active": True, "layer": "oscuridad", "triggers": {"celdas": 3}}}
FACT_K = "El huracán Katrina tocó tierra el 29 de agosto de 2005."
FACT_S = ("Los prisioneros quedaron atrapados durante días en celdas inundadas con agua contaminada con aguas residuales, "
          "que en algunos casos les llegaba hasta el pecho.")
FACT_T = ("Reclusos de la sección 'Templeman III' informaron haber visto cadáveres flotando en las aguas de la inundación "
          "mientras eran evacuados el 1 de septiembre.")


def W(text: str, step: float = 0.5) -> list[dict]:
    return [{"word": w, "start": round(k * step, 3), "end": round(k * step + 0.4, 3)} for k, w in enumerate(text.split())]


def _plan():
    return {"callouts": [], "emphasis": [], "punch_in": [], "archive_clippings": []}


