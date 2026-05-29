"""
flow_profiles.py — DEPRECATED chat 19.

Este módulo era el catálogo de reglas DepthFlow por art_profile (FLOW_PROFILES,
FlowProfileRules, get_rules, is_allowed, fallback_spec, render_constraints_for_prompt).

En chat 19 desconectamos el catálogo del flujo activo: flow_director
decide ahora desde scene content + posición narrativa, sin profile.

Lo único que sobrevive es el TypedDict FlowSpec — output que consume
parallax_animator_v2 y que viaja por el resto del pipeline (fase2b).
"""
from __future__ import annotations

from typing import TypedDict

try:
    from typing import NotRequired  # Python 3.11+
except ImportError:
    from typing_extensions import NotRequired  # type: ignore[assignment]


class FlowSpec(TypedDict):
    """Output final que consume parallax_animator_v2."""
    movement: str
    intensity: float
    steady: float
    dof: bool
    reasoning: str
    zoom_duration: NotRequired[float | None]
    # Si está seteado y es ch01 + primera imagen → fase2b usa
    # build_hook_clip (zoom corto + tpad freeze frame).
    # None o ausente = comportamiento legacy (animación uniforme).


__all__ = ["FlowSpec"]
