"""
flow_config.py — Settings técnicos de DepthFlow + inventario inmutable.

DOS responsabilidades separadas:
  1. SETTINGS: parámetros de render (SSAA, fps, fallback)
  2. INVENTARIO: lista exacta de movimientos válidos. Se inyecta TAL CUAL
     en el system prompt de Gemini para evitar alucinaciones tipo
     "spiral_zoom" o "matrix_dolly" que no existen en DepthFlow.

NO contiene reglas por art_profile (eso vive en flow_profiles.py).
NO contiene la lógica de selección (eso vive en modules/flow_director.py).
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from config import BASE_DIR


# ═══════════════════════════════════════════════════════════════
#  SETTINGS DE RENDER
# ═══════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class FlowRenderSettings:
    """Parámetros de render DepthFlow (no cambian por nicho)."""
    # Calidad
    ssaa: int = 2                       # Super-sampling anti-aliasing (4K downsample)
    fps: int = 30                       # FPS del clip animado

    # Duración base por escena (los segundos reales los manda el script)
    default_duration_seconds: float = 5.0

    # Entorno DepthFlow (venv aislado)
    venv_depthflow: Path = Path(r"C:\CLAUDE_PROJECTS\viral-video-pipeline\.venv-depthflow")
    use_subprocess: bool = True         # True = invocar venv aislado, False = mismo venv

    # Fallback
    fallback_to_kenburns: bool = True   # Si DepthFlow falla → Ken Burns 2D
    fallback_kenburns_zoom: float = 1.15  # 15% zoom en Ken Burns


# ═══════════════════════════════════════════════════════════════
#  INVENTARIO INMUTABLE DE MOVIMIENTOS DEPTHFLOW
# ═══════════════════════════════════════════════════════════════
# Cualquier valor fuera de esta lista se descarta como alucinación de Gemini.

@dataclass(frozen=True)
class DepthFlowMovement:
    """Definición canónica de un movimiento DepthFlow."""
    name: str
    description: str       # Qué hace la cámara (lo lee Gemini)
    best_for: str          # Casos de uso (también lo lee Gemini)
    risk: str = ""         # Advertencia opcional (también lo lee Gemini)


# Inventario reducido en chat 21: de 4 → 3 movimientos UNIVERSALMENTE robustos.
# Validado empíricamente sobre las 10 imágenes de Pripyat (incluyendo las complejas:
# explosión, fuego, ruinas con varillas finas). Los 3 robustos NO piden
# recomposición 3D agresiva al depth map mal estimado.
#
# Camino A (chat 55) re-expuso zoom_in/zoom_out al LLM, pero falló: el gate por
# TEXTO del prompt no funciona (el texto y la imagen divergen — Flux no obedece) y
# la granularidad del LLM es por CAPÍTULO, no por imagen. Camino B (chat 55) lo
# REVIERTE acá: el LLM vuelve a 3 movimientos y NO ve zoom. El zoom lo inyecta un
# GATE por IMAGEN (depth_probe geométrico + zoom_judge de visión) DESPUÉS de la
# validación del LLM. El branch zoom del animador y el fix de dirección de zoom_out
# QUEDAN (los usa el gate). `dolly` sigue fuera.
DEPTHFLOW_INVENTORY: tuple[DepthFlowMovement, ...] = (
    DepthFlowMovement(
        name="horizontal",
        description="Paneo lateral izquierda↔derecha. La cámara se desliza sin cambiar la profundidad.",
        best_for="horizontes, paisajes, líneas de elementos, escenas extendidas lateralmente.",
    ),
    DepthFlowMovement(
        name="vertical",
        description="Paneo vertical arriba↔abajo. La cámara se desliza verticalmente sin cambiar la profundidad.",
        best_for="rostros (recorre de pelo a mentón con dramatismo), edificios altos, sujetos verticales.",
    ),
    DepthFlowMovement(
        name="orbital",
        description="La cámara orbita ligeramente alrededor de un punto fijo, dando sensación de tridimensionalidad sutil.",
        best_for="objetos centrales, retratos, productos, cuando querés enfatizar volumen sin desplazamiento lateral.",
    ),
)

VALID_MOVEMENTS: frozenset[str] = frozenset(m.name for m in DEPTHFLOW_INVENTORY)


# ═══════════════════════════════════════════════════════════════
#  RANGOS DE PARÁMETROS (para clamping post-Gemini)
# ═══════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class ParamRanges:
    intensity_min: float = 0.85   # subido de 0.6 (chat 21: garantizar movimiento visible)
    intensity_max: float = 1.0
    steady_min: float = 0.0
    steady_max: float = 0.4       # bajado de 0.8 (chat 21: evitar anclar demasiado)


# ═══════════════════════════════════════════════════════════════
#  INSTANCIAS GLOBALES
# ═══════════════════════════════════════════════════════════════

flow_render = FlowRenderSettings()
param_ranges = ParamRanges()


# ═══════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════

def render_inventory_for_prompt() -> str:
    """Serializa el inventario para inyectar en el system prompt de Gemini."""
    lines: list[str] = []
    for m in DEPTHFLOW_INVENTORY:
        line = f"- {m.name}: {m.description} Bueno para {m.best_for}"
        if m.risk:
            line += f" [⚠ {m.risk}]"
        lines.append(line)
    return "\n".join(lines)


def clamp_intensity(value: float) -> float:
    return max(param_ranges.intensity_min,
               min(param_ranges.intensity_max, float(value)))


def clamp_steady(value: float) -> float:
    return max(param_ranges.steady_min,
               min(param_ranges.steady_max, float(value)))