"""
engine_profiles.py — Capa modular de PERFILES de motor de imagen (ESLABÓN 3a).

Cada motor (Kling, Seedream) se describe con un EngineProfile. El SELECTOR
(select_profile) elige el perfil del motor ACTIVO (api.image_engine). Esto hace
todo lo de aguas abajo model-swappable: cambiar de motor = cambiar de perfil, no
de código.

ALCANCE 3a (este PR): solo la mitad RENDER del perfil (model_id, base_url,
image_size, cost_usd). asset_manager consume render.* para armar URL + payload.
Mientras api.image_engine siga "kling", select_profile devuelve PERFIL_KLING y el
render sale BYTE-IDÉNTICO a como estaba hardcodeado (los valores salen de api.*).

ALCANCE 3b (siguiente PR): la mitad PROMPT del perfil (formula/aspect_ratio_text/
negations_in_text/style_tail) está DEFINIDA acá pero NADIE la lee todavía. La va a
consumir el ensamblador/skeleton de m03 (DOC_SKELETON §3). Inerte hasta 3b.

NO contiene los payload builders ni la llamada HTTP — eso vive en asset_manager
(junto al resto del render). El perfil es DATA; asset_manager le ata el comportamiento.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from config import api, pipeline


@dataclass(frozen=True)
class RenderProfile:
    """Mitad RENDER de un perfil: lo que define la llamada a fal (URL + tamaño + costo)."""
    model_id: str
    base_url: str            # SYNC (status 200 directo) en ambos motores t2i de hoy
    image_size: str | dict | None   # enum ("landscape_16_9") | {"width","height"} | None (Kling usa resolution+aspect)
    cost_usd: float


@dataclass(frozen=True)
class EngineProfile:
    """Perfil de un motor de imagen. engine_key = valor de api.image_engine que lo activa."""
    engine_key: str
    render: RenderProfile
    # ── mitad PROMPT (DOC_SKELETON §3) — DEFINIDA pero INERTE hasta 3b ──
    formula: tuple = ()
    aspect_ratio_text: str = ""
    negations_in_text: bool = True
    style_tail: bool = False
    text_recipe: dict = field(default_factory=dict)


# ═══════════════════════════════════════════════════════════════
#  PERFILES
# ═══════════════════════════════════════════════════════════════

# Kling: el render sale de api.* (snapshot al import; config es singleton, nada lo
# muta en runtime) → submit_url y payload byte-idénticos a los del código viejo.
PERFIL_KLING = EngineProfile(
    engine_key="kling",
    render=RenderProfile(
        model_id=api.fal_kling_model,        # "fal-ai/kling-image/o3/text-to-image"
        base_url=api.fal_sync_base_url,       # "https://fal.run"
        image_size=None,                      # Kling NO usa image_size (usa resolution+aspect en su payload)
        cost_usd=0.028,
    ),
)

# Seedream 4.5 (SEEDREAM_4.5_REFERENCIA §1-2): SYNC, sin guidance_scale ni
# negative_prompt (no existen en v4.5). CARGADO pero INACTIVO hasta que
# api.image_engine == "seedream" (eslabón 3b o flip manual).
PERFIL_SEEDREAM = EngineProfile(
    engine_key="seedream",
    render=RenderProfile(
        model_id="fal-ai/bytedance/seedream/v4.5/text-to-image",
        base_url="https://fal.run",
        image_size={"width": pipeline.image_width, "height": pipeline.image_height},   # 2560×1440 = canvas (1 fuente de verdad)
        cost_usd=0.04,
    ),
    # ── mitad PROMPT (3b — DOC_SKELETON §3): orden oficial del ensamblador ──
    formula=(
        "shot_scale", "subject", "action", "gaze_interaction",
        "setting", "hard_facts", "props_detail", "color_palette",
        "lighting", "mood",
        "style", "lens_technique", "camera_angle",
        "text_in_image",
        "aspect_ratio",
        "negations",
    ),
    aspect_ratio_text="The image has a 16:9 aspect ratio.",
    negations_in_text=True,    # Seedream no tiene negative_prompt → negaciones en el texto
    style_tail=False,          # Seedream NO usa cola de harness; el estilo es un slot
    text_recipe={"quotes": True, "needs": ("font", "location"),
                 "suffix": "in clear crisp lettering"},
)


_PROFILES: dict[str, EngineProfile] = {
    PERFIL_KLING.engine_key: PERFIL_KLING,
    PERFIL_SEEDREAM.engine_key: PERFIL_SEEDREAM,
}


def select_profile(engine_key: str) -> EngineProfile | None:
    """Devuelve el perfil del motor SYNC activo (kling/seedream), o None si el
    motor no es de perfil (ej: "flux", que mantiene su path legacy de queue)."""
    return _PROFILES.get(engine_key)
