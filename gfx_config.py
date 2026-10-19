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
    quality: str = "looks"                   # draft | looks. F2 §0b: draft (JPEG q80 + CRF 28) ablanda la imagen
    debug_quality: str = "draft"             # solo con --gfx-debug (iteración rápida)
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
        description="Recorte de periódico de época con texto real del fact, 6 s en pantalla desde el inicio de una escena.",
        params="lista de hasta 2: fact_idx, scene_idx, headline, kicker.",
        rules="máx 2 por cap, solo con facts de texto suficiente; cuerpo ≥ 52 px; la escena debe durar ≥ 4 s.",
        max_per_cap=2, llm_decides=True,
    ),
    GfxBlock(
        name="evidence_zoom",
        description="Recuadro fino sobre un detalle del frame de video y zoom 2.2× hacia él con etiqueta 'DETALLE'; termina en el corte, nunca vuelve.",
        params="scene_idx, box [x, y, w, h] normalizado 0–1 sobre el cuadro.",
        rules="máx 1 por cap; al FINAL de su escena; la escena debe durar ≥ 3.1 s.",
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
        description="Punch-in sutil de cámara (1.00→1.025 en 400 ms, se sostiene hasta el corte) sobre la capa de video en una palabra de énfasis.",
        params="lista de trigger_word_idx.",
        rules="máx 2 por cap.",
        max_per_cap=2, llm_decides=True,
    ),
    GfxBlock(
        name="shot_transition",
        description="Transición CSS en cada corte intra-cap según emotional_rank: R1 flash 30 % (≤ 2), R2 crossfade 20 f, R3 disolvencia 30 f.",
        params="(ninguno: determinista desde emotional_rank)",
        rules="el LLM no lo elige.",
        max_per_cap=999, llm_decides=False,
    ),
    GfxBlock(
        name="grade",
        description="Grade CSS (default 'off': solo grano + viñeta) sobre todo el footage.",
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
    accent_hex: str = "#c8102e"              # F2 §0b.9: acento ÚNICO del canal (subrayado, sello, línea, kicker)
    # title_card (F2 §0b.2: 30 % más chica, 3.0 s, fade de salida 0.4 s)
    title_dur: float = 3.0
    title_fade_out: float = 0.4
    title_scale: float = 0.7
    title_dim: float = 0.4
    # data_callout (D14) + tipografía (D13 / F2 §0b.8)
    callout_dur_min: float = 2.5
    callout_dur_max: float = 6.0
    callout_dur: float = 2.5                 # default si el plan no trae duración
    callout_sec_per_word: float = 0.4        # 0.4 s × palabras + 1.0 s, mín 2.5 s,
    callout_base_sec: float = 1.0            # y nunca antes del fin de la frase hablada
    callout_until_phrase_end: bool = True
    callout_font: str = "Playfair Display SC"   # name/place/year (D13); figure → Anton
    callout_font_weight: int = 900             # Black (§0b.8: Bold/Black)
    callout_font_px: int = 158                 # +20 % sobre la muestra del sampler (132 px)
    callout_anton_px: int = 168
    callout_shadow: str = "0 2px 8px rgba(0,0,0,.6)"
    # evidence_zoom (F2 §0b.5: termina en el corte, sostiene ≥ 1 s, nunca vuelve)
    zoom_rect_sec: float = 0.65
    zoom_approach_sec: float = 1.2
    zoom_hold_min_sec: float = 1.0
    zoom_scale: float = 2.2
    zoom_box_min: float = 0.06               # lado mínimo del box normalizado
    zoom_box_max: float = 0.25
    zoom_label_margin_px: int = 40           # "DETALLE" a ≥ 40 px del borde
    # archive_clipping (F2 §0b.6: 15 % más chico, 6 s, hasta 2 por cap, lado opuesto al sujeto)
    archive_dur: float = 6.0
    archive_max_per_cap: int = 2
    archive_scale: float = 0.68              # F2 §0b: 0.85 × 0.8 (otro 20 % más chico)
    archive_max_w_frac: float = 0.30         # ancho máximo del recorte = 30 % del cuadro
    archive_head_max_words: int = 8          # titular ≤ 8 palabras (si no, se descarta: nunca se reescribe)
    archive_body_default: bool = False       # F2 §0b: recorte = kicker + titular; SIN cuerpo por default
    archive_body_head_max_words: int = 4     # el cuerpo solo aparece si el titular tiene ≤ 4 palabras
    archive_body_max_words: int = 12         # ≈ 2 líneas a 40 px en el papel de 748 px (frase completa)
    archive_body_lines: int = 2              # tope duro de líneas visibles (CSS)
    archive_min_scene: float = 4.0           # la escena de inicio debe dar aire al recorte
    archive_min_sec: float = 4.0
    archive_body_px: int = 40                # Omar F2 §0b: 40 px, máx 2 líneas (reemplaza el ≥ 52 de D3 para el recorte)
    # count_up
    count_dur: float = 1.2                   # rampa 0 → valor (F2 §0b: restaurada)
    count_hold_sec: float = 2.5              # quieto en el valor DESPUÉS de la rampa
    # punch_in (F2 §0b.3: 1.025 en 400 ms ease-out, SIN regreso: se sostiene hasta el corte)
    punch_scale: float = 1.025
    punch_in_sec: float = 0.4
    punch_hold: bool = True
    punch_out_sec: float = 0.4               # solo si punch_hold=False
    # shot_transition (F2 §0b.4: R2 20 f, R3 30 f; R3 alternativa dip-to-black 10 f)
    transition_frames: dict = field(default_factory=lambda: {"R1": 3, "R2": 20, "R3": 30})
    r3_style: str = "dissolve"               # dissolve | dip
    dip_frames: int = 10
    cut_snap_window_sec: float = 0.3         # el corte se ancla al cambio REAL de imagen (±0.3 s del anchor)
    flash_peak: float = 0.3
    flash_max_per_cap: int = 2
    flash_min_gap_sec: float = 20.0
    r1_cut_punch_scale: float = 1.02
    # grade (F2 §0b.1: OFF por default → solo grano 0.15 + viñeta 0.20; recetas A/B/C inactivas)
    grade_default: str = "off"
    grain_jumps_per_sec: int = 12

    @property
    def zoom_dur(self) -> float:
        return self.zoom_rect_sec + self.zoom_approach_sec + self.zoom_hold_min_sec

    @property
    def zoom_min_scene(self) -> float:
        return self.zoom_dur + 0.2

    @property
    def css_grade_variant(self) -> str:      # alias F1b
        return self.grade_default

    @property
    def css_grade_intensity(self) -> float:
        return GRADE_VARIANTS[self.grade_default]["intensity"]

    @property
    def css_grade_opacity(self) -> dict:
        return GRADE_VARIANTS[self.grade_default]["opacity"]


# Recetas de grade CSS (opacidad base de cada capa × intensidad)
#   A = F1 · B = haze 0 + teal en sombras (F1b) · C = B a 0.3 · off = solo grano 0.15 + viñeta 0.20 (F2)
_GRADE_A = {"gr-halation": 0.35, "gr-haze": 0.6, "gr-palette": 0.5, "gr-shadowteal": 0.0, "gr-vignette": 0.7, "gr-grain": 0.12}
_GRADE_B = {"gr-halation": 0.35, "gr-haze": 0.0, "gr-palette": 0.0, "gr-shadowteal": 1.0, "gr-vignette": 0.7, "gr-grain": 0.12}
_GRADE_OFF = {"gr-halation": 0.0, "gr-haze": 0.0, "gr-palette": 0.0, "gr-shadowteal": 0.0, "gr-vignette": 0.20, "gr-grain": 0.15}
GRADE_VARIANTS: dict[str, dict] = {
    "A": {"intensity": 0.5, "opacity": _GRADE_A},
    "B": {"intensity": 0.5, "opacity": _GRADE_B},
    "C": {"intensity": 0.3, "opacity": _GRADE_B},
    "off": {"intensity": 1.0, "opacity": _GRADE_OFF},
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
