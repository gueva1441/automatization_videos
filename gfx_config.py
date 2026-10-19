"""
gfx_config.py — Settings de render de la capa gráfica HyperFrames + inventario inmutable.

DOS responsabilidades separadas (patrón flow_config):
  1. SETTINGS: render HyperFrames (calidad, workers, timeout, runtime Node, reencode).
  2. INVENTARIO: bloques gráficos válidos con sus parámetros, rangos y reglas duras
     (DOC_MAESTRO_HyperFrames §3). Se inyecta TAL CUAL en el system prompt del
     gfx_director para que el LLM solo elija de esta lista.

NO contiene la lógica de selección (eso vive en script_engine/gfx_director.py).
NO contiene HTML (eso vive en script_engine/gfx_templates/).
"""
from __future__ import annotations

import os
import shutil
from dataclasses import dataclass, field
from pathlib import Path

from config import BASE_DIR


# ═══════════════════════════════════════════════════════════════
#  SETTINGS DE RENDER
# ═══════════════════════════════════════════════════════════════

GFX_RUNTIME_DIR: Path = BASE_DIR / "script_engine" / "gfx_runtime"
GFX_TEMPLATES_DIR: Path = BASE_DIR / "script_engine" / "gfx_templates"
GFX_FONTS_DIR: Path = BASE_DIR / "script_engine" / "fonts"


@dataclass(frozen=True)
class GfxRenderSettings:
    """Parámetros de render de la capa gráfica (no cambian por nicho)."""
    enable_gfx: bool = False                 # default OFF: solo con fase2b --gfx
    quality: str = "draft"                   # draft | looks
    workers: int = 5                         # sin shaders (D5) → 5 workers (lab v1)
    timeout_sec: int = 900                   # por cap; excedido → fallback a base_clip
    player_ready_timeout_ms: int = 240_000   # lab v2: 45 s default no alcanza a 1440p
    protocol_timeout_ms: int = 600_000
    hyperframes_version: str = "0.8.172"     # versión validada en F0/LAB v1/LAB v2
    node_dir: Path = Path(r"C:\Program Files\nodejs")
    runtime_dir: Path = GFX_RUNTIME_DIR
    # D11: re-encode del base_clip con keyframe cada frame-bloque (draft #1 del lab falló sin esto)
    reencode_gop: int = 30
    reencode_crf: int = 14
    reencode_preset: str = "ultrafast"         # F1b palanca: re-encode -g30 (antes veryfast)


gfx_render = GfxRenderSettings()

VALID_QUALITIES: frozenset[str] = frozenset({"draft", "looks"})


def resolve_node() -> str | None:
    """Ruta a node.exe: PATH primero, luego node_dir del settings. None si no hay Node."""
    found = shutil.which("node")
    if found:
        return found
    cand = gfx_render.node_dir / ("node.exe" if os.name == "nt" else "node")
    return str(cand) if cand.exists() else None


def hyperframes_cli() -> Path:
    """Entry point del CLI pineado en el runtime local (sin npx, sin shell)."""
    return gfx_render.runtime_dir / "node_modules" / "hyperframes" / "bin" / "hyperframes.mjs"


def gsap_js() -> Path:
    """GSAP local (nunca CDN)."""
    return gfx_render.runtime_dir / "node_modules" / "gsap" / "dist" / "gsap.min.js"


def browser_env() -> dict[str, str]:
    """Entorno para el CLI: respeta HYPERFRAMES_BROWSER_PATH si está seteado."""
    env = dict(os.environ)
    node = resolve_node()
    if node:
        env["PATH"] = str(Path(node).parent) + os.pathsep + env.get("PATH", "")
    env["HYPERFRAMES_SKIP_SKILLS"] = "1"
    return env


# ═══════════════════════════════════════════════════════════════
#  INVENTARIO INMUTABLE DE BLOQUES (DOC_MAESTRO §3, v1.0)
# ═══════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class GfxBlock:
    """Definición canónica de un bloque gráfico."""
    name: str
    description: str           # qué hace (lo lee el LLM)
    params: str                # qué llena el director (lo lee el LLM)
    rules: str                 # reglas duras (lo lee el LLM; las garantiza el validador)
    max_per_cap: int
    llm_decides: bool          # False = determinista (shot_transition, grade)


GFX_INVENTORY: tuple[GfxBlock, ...] = (
    GfxBlock(
        name="title_card",
        description="Rótulo de capítulo al inicio: 'CAPÍTULO N' + título del skeleton sobre el video oscurecido 40 %.",
        params="use (bool). El título y el número los pone el sistema desde el skeleton.",
        rules="1 por cap, 1.9 s, no congela el video.",
        max_per_cap=1, llm_decides=True,
    ),
    GfxBlock(
        name="data_callout",
        description="Dato grande (año, cifra, nombre, lugar) en el tercio superior cuando la voz lo dice.",
        params="fact_idx (índice de verified_facts), trigger_word_idx (índice en WORDS donde la voz dice el dato), kind year|figure|name|place.",
        rules="máx 3 por cap; omitir si el texto en imagen de esa escena ya muestra el dato; 1.2–2 s; el texto sale del fact, no lo escribís vos.",
        max_per_cap=3, llm_decides=True,
    ),
    GfxBlock(
        name="archive_clipping",
        description="Recorte de periódico de época con texto real del fact, sobre una escena.",
        params="fact_idx, scene_idx.",
        rules="máx 1 por cap; cuerpo ≥ 52 px; tipografía por década; la escena debe durar ≥ 4 s.",
        max_per_cap=1, llm_decides=True,
    ),
    GfxBlock(
        name="evidence_zoom",
        description="Recuadro fino sobre un detalle del frame de video y zoom 2.2× hacia él con etiqueta 'DETALLE'.",
        params="scene_idx, box [x, y, w, h] normalizado 0–1 sobre el cuadro.",
        rules="máx 1 por cap; sobre el frame de video; salida en corte; la escena debe durar ≥ 3.6 s.",
        max_per_cap=1, llm_decides=True,
    ),
    GfxBlock(
        name="count_up",
        description="Contador que sube de 0 a una cifra presente en un fact, cuando la voz la dice.",
        params="fact_idx, trigger_word_idx.",
        rules="máx 1 por cap; solo cifras presentes literalmente en el fact.",
        max_per_cap=1, llm_decides=True,
    ),
    GfxBlock(
        name="punch_in",
        description="Punch-in sutil de cámara (1.00→1.03 en 200 ms) sobre la capa de video en una palabra de énfasis.",
        params="lista de trigger_word_idx.",
        rules="máx 2 por cap.",
        max_per_cap=2, llm_decides=True,
    ),
    GfxBlock(
        name="shot_transition",
        description="Transición CSS en cada corte intra-cap según emotional_rank: R1 flash 40 % 3 f, R2 crossfade 9 f, R3 disolvencia 15 f.",
        params="(ninguno: determinista desde emotional_rank)",
        rules="el LLM no lo elige.",
        max_per_cap=999, llm_decides=False,
    ),
    GfxBlock(
        name="grade",
        description="Grade CSS de identidad (teal frío, halation, viñeta, grano) sobre todo el footage.",
        params="(ninguno: preset fijo)",
        rules="todos los caps, incluido Veo; el LLM no lo elige.",
        max_per_cap=1, llm_decides=False,
    ),
)

VALID_BLOCKS: frozenset[str] = frozenset(b.name for b in GFX_INVENTORY)
LLM_BLOCKS: frozenset[str] = frozenset(b.name for b in GFX_INVENTORY if b.llm_decides)
VALID_CALLOUT_KINDS: frozenset[str] = frozenset({"year", "figure", "name", "place"})


def max_per_cap(block: str) -> int:
    """Máximo por cap de un bloque del inventario (KeyError si no existe)."""
    return next(b.max_per_cap for b in GFX_INVENTORY if b.name == block)


# ═══════════════════════════════════════════════════════════════
#  REGLAS Y RANGOS (para clamping post-LLM y para el templater)
# ═══════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class GfxRules:
    interrupt_min_sec: float = 25.0          # pattern interrupt: un bloque cada 25–35 s
    interrupt_max_sec: float = 35.0
    title_dur: float = 1.9
    title_dim: float = 0.4
    callout_dur_min: float = 2.5             # F1b: texto legible (antes 1.2)
    callout_dur_max: float = 6.0
    callout_dur: float = 2.5                 # default si el plan no trae duración
    callout_sec_per_word: float = 0.4        # F1b: 0.4 s × palabras + 1.0 s, mín 2.5 s,
    callout_base_sec: float = 1.0            #      y nunca antes del fin de la frase hablada
    callout_until_phrase_end: bool = True
    zoom_dur: float = 3.0
    zoom_scale: float = 2.2
    zoom_min_scene: float = 3.6
    zoom_box_min: float = 0.06               # lado mínimo del box normalizado
    zoom_box_max: float = 0.25               # F1b: ×2.2 entra holgado (F1: 0.35; bug ch06 con 0.6)
    zoom_label_margin_px: int = 40           # "DETALLE" a ≥ 40 px del borde
    archive_min_scene: float = 5.0           # F1b: el recorte dura escena − 1 s ≥ 4.0 s
    archive_min_sec: float = 4.0
    archive_body_px: int = 52
    count_dur: float = 1.6                   # subida 0 → valor
    count_hold_sec: float = 2.5              # F1b: ≥ 2.5 s quieto después de llegar al valor
    punch_scale: float = 1.03
    punch_in_sec: float = 0.2
    punch_out_sec: float = 0.4
    # shot_transition por emotional_rank del plano entrante (F1b: R2 12 f, R3 20 f, flash 30 %)
    transition_frames: dict = field(default_factory=lambda: {"R1": 3, "R2": 12, "R3": 20})
    flash_peak: float = 0.3
    flash_max_per_cap: int = 2               # F1b: flash solo en ≤ 2 R1 por cap...
    flash_min_gap_sec: float = 20.0          # ...separados ≥ 20 s; el resto → corte duro + punch
    r1_cut_punch_scale: float = 1.02         # punch del R1 sin flash
    # grade CSS (lab v1/v2). Desvío de D4: la pasada media-treatment costó 6.29× tiempo real
    # (F1 paso 1); el preset nativo queda versionado en gfx_templates/gfx_grade.json.
    css_grade_variant: str = "B"             # A | B | C (GRADE_VARIANTS); Omar eligió B (F1b §2.4)
    grain_jumps_per_sec: int = 12

    @property
    def css_grade_intensity(self) -> float:
        return GRADE_VARIANTS[self.css_grade_variant]["intensity"]

    @property
    def css_grade_opacity(self) -> dict:
        return GRADE_VARIANTS[self.css_grade_variant]["opacity"]


# Recetas de grade CSS (opacidad base de cada capa × intensidad)
#   A = F1 tal cual · B = haze 0 + teal solo en sombras profundas (screen de teal muy oscuro: suma en
#   negros, ~nada en altas luces; contraste y halation intactos) · C = B a intensidad 0.3
_GRADE_A = {"gr-halation": 0.35, "gr-haze": 0.6, "gr-palette": 0.5, "gr-shadowteal": 0.0, "gr-vignette": 0.7, "gr-grain": 0.12}
_GRADE_B = {"gr-halation": 0.35, "gr-haze": 0.0, "gr-palette": 0.0, "gr-shadowteal": 1.0, "gr-vignette": 0.7, "gr-grain": 0.12}
GRADE_VARIANTS: dict[str, dict] = {
    "A": {"intensity": 0.5, "opacity": _GRADE_A},
    "B": {"intensity": 0.5, "opacity": _GRADE_B},
    "C": {"intensity": 0.3, "opacity": _GRADE_B},
}


gfx_rules = GfxRules()

# D7: cromo fijo declarado (no es contenido; fuera del candado literal)
CHROME_TEMPLATES: tuple[str, ...] = ("CAPÍTULO {n}", "DETALLE")


def chrome_strings(chapter_number: int) -> frozenset[str]:
    """Strings de cromo permitidos para un cap."""
    return frozenset(t.format(n=chapter_number) for t in CHROME_TEMPLATES)


# ═══════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════

def render_inventory_for_prompt() -> str:
    """Serializa el inventario para el system prompt del gfx_director."""
    lines: list[str] = []
    for b in GFX_INVENTORY:
        who = "VOS elegís" if b.llm_decides else "NO lo elegís (determinista)"
        lines.append(f"- {b.name} [{who}]: {b.description} Parámetros: {b.params} Reglas: {b.rules}")
    return "\n".join(lines)


def clamp_count(items: list, block: str) -> list:
    """Recorta una lista al máximo por cap del bloque."""
    return list(items)[: max_per_cap(block)]


def clamp_callout_duration(value: float) -> float:
    return max(gfx_rules.callout_dur_min, min(gfx_rules.callout_dur_max, float(value)))


def clamp_box(box: list[float]) -> list[float] | None:
    """Normaliza un box [x, y, w, h] a [0, 1] y a lados dentro de rango. None si inválido."""
    try:
        x, y, w, h = (float(v) for v in box)
    except (TypeError, ValueError):
        return None
    w = max(gfx_rules.zoom_box_min, min(gfx_rules.zoom_box_max, w))
    h = max(gfx_rules.zoom_box_min, min(gfx_rules.zoom_box_max, h))
    x = max(0.0, min(1.0 - w, x))
    y = max(0.0, min(1.0 - h, y))
    return [round(x, 4), round(y, 4), round(w, 4), round(h, 4)]


def clamp_quality(value: str) -> str:
    return value if value in VALID_QUALITIES else gfx_render.quality
