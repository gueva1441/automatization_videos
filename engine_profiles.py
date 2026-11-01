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
    accepts_seed: bool = True       # F8: Seedream 5.0 Lite no tiene `seed` de entrada (solo lo devuelve)
    edit_model_id: str | None = None   # F68: el id de /edit cuando no sale de reemplazar «text-to-image» en model_id
    secuencia: bool = True          # F68: con False el pre-paso de secuencia no corre (una foto = una llamada)
    madres_solo_persona: bool = False   # F68: con True `foto_madre_ref` (objeto/lugar) no entra a la regla única de madres
    aspect_ratio: str | None = None     # F68: motores que piden aspect_ratio en vez de image_size
    safety_tolerance: str | None = None # F68: enum "1".."6" de los endpoints Nano Banana


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

# Seedream (SEEDREAM_4.5_REFERENCIA §1-2): SYNC, sin guidance_scale ni negative_prompt.
# F68: Seedream 4.5 (propuesta del analista, 2026-11-01), solo respaldo de Nano Banana 2 Lite y madres de persona nuevas. El
# /edit sale del mismo id (text-to-image → edit; acepta `image_urls`). 5.0 Lite salió por deformar caras (lab NB-TOL6).
SEEDREAM_45_MODEL_ID = "fal-ai/bytedance/seedream/v4.5/text-to-image"
SEEDREAM_V5_LITE_MODEL_ID = "fal-ai/bytedance/seedream/v5/lite/text-to-image"
PERFIL_SEEDREAM = EngineProfile(
    engine_key="seedream",
    render=RenderProfile(
        model_id=SEEDREAM_45_MODEL_ID,
        base_url="https://fal.run",
        image_size={"width": pipeline.image_width, "height": pipeline.image_height},   # 2560×1440 fijo (no «auto_2K»)
        cost_usd=0.04,
        accepts_seed=True,
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


# F68: motor principal de fotos (elección de Omar, 2026-11-01, lab NB-TOL6 hoja_P4). Cola de fal, una foto por llamada, salida
# nativa fija 1K (1376×768); asset_manager guarda el nativo y lo lleva a pipeline.image_*. Tarifa por tokens: cost_usd es la
# medida por Omar en el panel de fal, estimada. La mitad PROMPT no se usa: m03 lee la de PERFIL_SEEDREAM.
PERFIL_NB2_LITE = EngineProfile(
    engine_key="nb2_lite",
    render=RenderProfile(
        model_id="google/nano-banana-2-lite",
        base_url=api.fal_base_url,
        image_size=None,
        cost_usd=0.042,
        edit_model_id="google/nano-banana-2-lite/edit",
        secuencia=False,
        madres_solo_persona=True,
        aspect_ratio="16:9",
        safety_tolerance="6",
    ),
)


_PROFILES: dict[str, EngineProfile] = {
    PERFIL_KLING.engine_key: PERFIL_KLING,
    PERFIL_SEEDREAM.engine_key: PERFIL_SEEDREAM,
    PERFIL_NB2_LITE.engine_key: PERFIL_NB2_LITE,
}


def select_profile(engine_key: str) -> EngineProfile | None:
    """Devuelve el perfil del motor SYNC activo (kling/seedream), o None si el
    motor no es de perfil (ej: "flux", que mantiene su path legacy de queue)."""
    return _PROFILES.get(engine_key)


# ═══════════════════════════════════════════════════════════════
#  PERFILES DE VIDEO (F53b): motor de clips image-to-video por fal
# ═══════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class VideoProfile:
    """Un motor de clips image-to-video (F53b). DATA, sin HTTP: la llamada vive en asset_manager.
    Campos del schema de fal leídos en F52 (`lab/hyperframes/f52/SCHEMAS_F52.md`); ficha de guía en inglés de F52b
    (`lab/hyperframes/f52/guias/<letra>.md`, copiada tal cual); costo medido en el panel de fal (2026-10-29 14:22)."""
    engine_key: str
    endpoint: str                 # id de fal (queue)
    campo_imagen: str             # el campo de la foto inicial («image_url» | «start_image_url»)
    campo_imagen_final: str       # F57: el campo de la foto final («end_image_url» en G y K; SCHEMAS_F52 l.18 y l.72)
    duracion_min: int             # rango del schema, en segundos
    duracion_max: int
    duracion_como_texto: bool     # el schema pide `duration` como string (Seedance) o como entero (G, K)
    resolucion: str
    campo_audio: str | None       # None: el schema no deja apagar el audio → la pista se quita con ffmpeg (`-an`)
    ficha: str                    # ficha de guía del modelo (entrada para Opus en script_engine/video_prompt.py)
    usd_por_s_leido: float        # precio unitario de api.fal.ai/v1/models/pricing
    mult_resolucion: float        # cobro real / precio leído a `resolucion` (panel de fal)

    def costo(self, segundos: float, ancho: int | None = None, alto: int | None = None) -> float:
        """US$ de un clip: precio leído × multiplicador de la resolución × segundos. G y K cobran por segundo (ancho y
        alto no cambian el precio; quedan en la firma para un motor que cobre por tokens)."""
        return round(self.usd_por_s_leido * self.mult_resolucion * segundos, 4)


# G: 0,03 US$/s leído; a 1080p el panel cobró 80,43 s por 16,09 s generados (×5) → 0,15 US$/s (DECISIONES 14:24).
PERFIL_VIDEO_G = VideoProfile(
    engine_key="gemini_omni_flash",
    endpoint="google/gemini-omni-flash/v1.1/image-to-video",
    campo_imagen="image_url",
    campo_imagen_final="end_image_url",
    duracion_min=3,
    duracion_max=10,
    duracion_como_texto=False,
    resolucion="1080p",
    campo_audio=None,
    ficha='**G — Gemini Omni Flash 1.1** (Google via fal): subject, action, camera movement, look and sound, written as directions to a film crew; camera moves by their film name; less prescriptive than Veo: short focused prompts work better than long ones; in image-to-video name what from the image must survive; close with "no captions".',
    usd_por_s_leido=0.03,
    mult_resolucion=5.0,
)

# K: 0,157 US$/s leído; a 1080p el panel cobró 23,95 s por 16,08 s generados (×1,5) → 0,235 US$/s (adenda F53b).
PERFIL_VIDEO_K = VideoProfile(
    engine_key="kling_4",
    endpoint="kling/v4/image-to-video",
    campo_imagen="start_image_url",
    campo_imagen_final="end_image_url",
    duracion_min=3,
    duracion_max=30,
    duracion_como_texto=False,
    resolucion="1080p",
    campo_audio=None,
    ficha='**K — Kling 4.0** (official Kling guide, 2026-10-26): descriptive, concrete language; few abstract words and few negations (they increase errors); the only negations needed: no subtitles and no background music. Structure: [General settings] scene and texture, visual style, camera tone · [Sequence] 0–X s / X–Y s / Y s–end with action and camera movement · [Audio]. In image-to-video: subject + motion, background + motion.',
    usd_por_s_leido=0.157,
    mult_resolucion=1.5,
)

_VIDEO_PROFILES: dict[str, VideoProfile] = {
    PERFIL_VIDEO_G.engine_key: PERFIL_VIDEO_G,
    PERFIL_VIDEO_K.engine_key: PERFIL_VIDEO_K,
}


def select_video_profile(engine_key: str) -> VideoProfile:
    """El perfil de video de `engine_key` («gemini_omni_flash» | «kling_4»). KeyError si no existe."""
    return _VIDEO_PROFILES[engine_key]
