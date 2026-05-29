"""
transition_config.py — Settings técnicos de transiciones FFmpeg + inventario inmutable.

DOS responsabilidades separadas:
  1. SETTINGS: parámetros de render (CRF, preset, fps)
  2. INVENTARIO: lista exacta de transiciones válidas. Sirve como guard-rail
     para que el director (futuro) no devuelva nombres alucinados tipo
     "matrix_swirl" o "infinite_zoom" que no existen en FFmpeg.

NO contiene reglas por art_profile (eso vive en transition_profiles.py).
NO contiene la lógica de selección (eso vive en modules/transition_director.py
cuando se implemente; por ahora se usan los defaults estáticos).

DEFAULT GANADOR: whip_pan_flash (whip pan + flash blanco intermedio).
Es el patrón viral pro para contenido faceless cinematográfico de misterio.
"""
from __future__ import annotations

from dataclasses import dataclass


# ═══════════════════════════════════════════════════════════════
#  SETTINGS DE RENDER
# ═══════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class TransitionRenderSettings:
    """Parámetros de render FFmpeg (no cambian por nicho)."""
    # Calidad
    crf: int = 18                       # CRF=18 mantiene calidad cinematográfica
    preset: str = "medium"              # balance velocidad/calidad
    pix_fmt: str = "yuv420p"            # compatible reproductores estándar
    fps: int = 30                       # debe coincidir con flow_render.fps

    # Codec
    video_codec: str = "libx264"
    audio_codec: str = "aac"

    # Comportamiento
    enable_transitions: bool = True     # master switch (False = hard cut puro)
    fallback_to_hard_cut: bool = True   # si la transición falla → corte seco


# ═══════════════════════════════════════════════════════════════
#  INVENTARIO INMUTABLE DE TRANSICIONES
# ═══════════════════════════════════════════════════════════════
# Cualquier valor fuera de esta lista se descarta como alucinación.

@dataclass(frozen=True)
class TransitionEffect:
    """Definición canónica de una transición FFmpeg."""
    name: str
    description: str           # Qué hace visualmente
    best_for: str              # Casos de uso narrativos
    duration_ms: int           # Duración total del efecto en milisegundos
    ffmpeg_filter: str         # filtro xfade o filter_complex hint
    risk: str = ""             # Advertencia opcional


TRANSITION_INVENTORY: tuple[TransitionEffect, ...] = (
    # ─── GANADORA: default global ───
    TransitionEffect(
        name="whip_pan_flash",
        description="Motion blur horizontal violento + flash blanco intermedio + reentrada borrosa.",
        best_for="hooks, giros narrativos, mid-points, cualquier cambio dramático. EFECTO VIRAL.",
        duration_ms=350,
        ffmpeg_filter="fade+boxblur+white_frame",  # filter_complex custom
    ),

    # ─── Para revelaciones (caída hacia adentro) ───
    TransitionEffect(
        name="zoom_punch",
        description="Zoom-in agresivo del frame final (1.0→1.4) + zoom-out del inicial (1.4→1.0).",
        best_for="revelaciones (ch07→ch08), mostrar el secreto, caer en la respuesta.",
        duration_ms=400,
        ffmpeg_filter="xfade=transition=zoomin",
    ),

    # ─── Suave para uniones neutras ───
    TransitionEffect(
        name="crossfade",
        description="Disolvencia suave entre clips, ambos visibles brevemente.",
        best_for="uniones neutras (ch02→ch03, ch03→ch04), respiro entre golpes.",
        duration_ms=200,
        ffmpeg_filter="xfade=transition=fade",
    ),

    # ─── Crossfade muy corto para foto→foto dentro de capítulo ───
    TransitionEffect(
        name="crossfade_micro",
        description="Disolvencia casi imperceptible (150ms), apenas un parpadeo.",
        best_for="foto→foto dentro del MISMO capítulo Flux, evita corte seco brutal.",
        duration_ms=150,
        ffmpeg_filter="xfade=transition=fade",
    ),

    # ─── Separador de actos ───
    TransitionEffect(
        name="fade_to_black",
        description="Fundido a negro completo + apertura desde negro.",
        best_for="separar actos, cambio de bloque narrativo grande, pausa dramática.",
        duration_ms=500,
        ffmpeg_filter="xfade=transition=fadeblack",
        risk="usar máximo 1 vez por video; abusar mata el ritmo viral.",
    ),

    # ─── Fade a blanco (revelación suave) ───
    TransitionEffect(
        name="fade_to_white",
        description="Fundido a blanco completo + apertura desde blanco.",
        best_for="revelación suave o purificadora, contenido espiritual/celestial (Canal 2 futuro).",
        duration_ms=400,
        ffmpeg_filter="xfade=transition=fadewhite",
    ),

    # ─── Hard cut explícito (lo que hay hoy) ───
    TransitionEffect(
        name="hard_cut",
        description="Corte seco sin transición (concat demuxer puro).",
        best_for="ritmo agresivo intencional, beat drops, momentos de impacto seco.",
        duration_ms=0,
        ffmpeg_filter="none",  # se maneja con concat demuxer normal
    ),
)

VALID_TRANSITIONS: frozenset[str] = frozenset(t.name for t in TRANSITION_INVENTORY)


# ═══════════════════════════════════════════════════════════════
#  DEFAULT GLOBAL
# ═══════════════════════════════════════════════════════════════
# Si no hay regla específica por (art_profile, posición), se usa esta.

DEFAULT_TRANSITION: str = "whip_pan_flash"


# ═══════════════════════════════════════════════════════════════
#  RANGOS DE PARÁMETROS (para clamping si futuro director devuelve duración)
# ═══════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class TransitionParamRanges:
    duration_ms_min: int = 100          # menos de 100ms es invisible
    duration_ms_max: int = 800          # más de 800ms mata el ritmo viral


# ═══════════════════════════════════════════════════════════════
#  INSTANCIAS GLOBALES
# ═══════════════════════════════════════════════════════════════

transition_render = TransitionRenderSettings()
transition_param_ranges = TransitionParamRanges()


# ═══════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════

def get_effect(name: str) -> TransitionEffect:
    """Devuelve la definición de una transición por nombre. KeyError si no existe."""
    for t in TRANSITION_INVENTORY:
        if t.name == name:
            return t
    raise KeyError(f"Transición desconocida: '{name}'. Válidas: {sorted(VALID_TRANSITIONS)}")


def is_valid(name: str) -> bool:
    """¿Esta transición existe en el inventario?"""
    return name in VALID_TRANSITIONS


def clamp_duration_ms(value: int) -> int:
    """Clampea duración a rango válido."""
    return max(transition_param_ranges.duration_ms_min,
               min(transition_param_ranges.duration_ms_max, int(value)))


def render_inventory_for_prompt() -> str:
    """Serializa el inventario para inyectar en system prompt de Gemini (futuro director)."""
    lines: list[str] = []
    for t in TRANSITION_INVENTORY:
        line = f"- {t.name} ({t.duration_ms}ms): {t.description} Bueno para {t.best_for}"
        if t.risk:
            line += f" [⚠ {t.risk}]"
        lines.append(line)
    return "\n".join(lines)
