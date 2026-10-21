"""
gfx_config.py — MOTOR de la capa gráfica HyperFrames (inmutable) + carga del PERFIL DE CANAL.

Responsabilidades separadas (patrón flow_config; F2 §0c motor/perfil):
  1. SETTINGS: render HyperFrames (calidad, workers, timeout, runtime Node, reencode). Motor.
  2. INVENTARIO: bloques gráficos válidos con sus parámetros y reglas duras (DOC_MAESTRO §3).
     Motor = qué bloques EXISTEN y qué hacen; el perfil decide cuáles están habilitados,
     cuántos por cap y dónde. Se inyecta en el system prompt del gfx_director.
  3. PERFIL DE CANAL: gfx_profiles/<perfil>.json (tokens visuales, fuentes, duraciones,
     grade/grano/viñeta, inventario habilitado). Se elige por el nicho activo
     (nicho_config.get_active_nicho()["nombre"] ∈ perfil["nichos"]) o por GFX_PROFILE.
     Un perfil nuevo NO requiere tocar código.

NO contiene la lógica de selección (eso vive en script_engine/gfx_director.py).
NO contiene HTML (eso vive en script_engine/gfx_templates/).
"""
from __future__ import annotations

import json
import os
import shutil
from dataclasses import dataclass, field, fields, replace
from pathlib import Path
from typing import Any

from config import BASE_DIR


# ═══════════════════════════════════════════════════════════════
#  SETTINGS DE RENDER
# ═══════════════════════════════════════════════════════════════

GFX_RUNTIME_DIR: Path = BASE_DIR / "script_engine" / "gfx_runtime"
GFX_TEMPLATES_DIR: Path = BASE_DIR / "script_engine" / "gfx_templates"
GFX_FONTS_DIR: Path = BASE_DIR / "script_engine" / "fonts"
GFX_PROFILES_DIR: Path = BASE_DIR / "gfx_profiles"
SFX_DIR: Path = BASE_DIR / "script_engine" / "sfx"
DEFAULT_PROFILE: str = "misterio"


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
    max_per_cap: int           # default del motor; el perfil lo pisa
    llm_decides: bool          # False = determinista (shot_transition, grade)
    enabled: bool = True       # el perfil de canal lo apaga/prende
    where: str = ""            # regla de dónde se permite (texto del perfil, lo lee el LLM)


_ENGINE_INVENTORY: tuple[GfxBlock, ...] = (
    GfxBlock(
        name="title_card",
        description="Rótulo de capítulo al inicio: 'CAPÍTULO N' + título del skeleton sobre el video oscurecido 40 %.",
        params="use (bool). El título y el número los pone el sistema desde el skeleton.",
        rules="no congela el video.",
        max_per_cap=1, llm_decides=True,
    ),
    GfxBlock(
        name="data_callout",
        description="Dato grande (año, cifra, nombre, lugar) en el tercio superior cuando la voz lo dice.",
        params="fact_idx (índice de verified_facts), trigger_word_idx (índice en WORDS donde la voz dice el dato), kind year|figure|name|place.",
        rules="omitir si el texto en imagen de esa escena ya muestra el dato; el texto sale del fact, no lo escribís vos.",
        max_per_cap=5, llm_decides=True,
    ),
    GfxBlock(
        name="archive_clipping",
        description="Recorte de periódico de época con texto real del fact, 6 s en pantalla desde el inicio de una escena.",
        params="lista de hasta 2: fact_idx, scene_idx, headline, kicker.",
        rules="solo con facts de texto suficiente; titular ≤ 8 palabras; la escena debe durar ≥ 4 s.",
        max_per_cap=2, llm_decides=True,
    ),
    GfxBlock(
        name="evidence_zoom",
        description="Recuadro fino sobre un detalle del frame de video y zoom 2.2× hacia él con etiqueta 'DETALLE'; termina en el corte, nunca vuelve.",
        params="scene_idx, box [x, y, w, h] normalizado 0–1 sobre el cuadro.",
        rules="al FINAL de su escena; la escena debe durar ≥ 3.1 s.",
        max_per_cap=1, llm_decides=True,
    ),
    GfxBlock(
        name="count_up",
        description="Contador que sube de 0 a una cifra presente en un fact, cuando la voz la dice.",
        params="fact_idx, trigger_word_idx.",
        rules="solo cifras presentes literalmente en el fact.",
        max_per_cap=1, llm_decides=True,
    ),
    GfxBlock(
        name="punch_in",
        description="Punch-in sutil de cámara (1.00→1.025 en 400 ms, se sostiene hasta el corte) sobre la capa de video en una palabra de énfasis.",
        params="lista de trigger_word_idx.",
        rules="palabras de énfasis.",
        max_per_cap=2, llm_decides=True,
    ),
    GfxBlock(
        name="chapter_question",
        description="Tarjeta de 2.0–2.5 s al cierre del cap con la pregunta que responde el capítulo SIGUIENTE (fondo oscurecido 50 %).",
        params="use (bool), text: una de las bullets del PRÓXIMO CAPÍTULO reformulada como pregunta.",
        rules="máx 9 palabras; toda palabra de contenido tiene que estar en las bullets o la narración del próximo cap; no en el último cap.",
        max_per_cap=1, llm_decides=True,
    ),
    GfxBlock(
        name="source_tag",
        description="Etiqueta de 1 línea bajo un data_callout o count_up con la fuente del fact (organización, año).",
        params="(ninguno: sale de sources[] cuando el fact nombra la organización)",
        rules="el LLM no lo elige; sin fuente resoluble no hay etiqueta.",
        max_per_cap=999, llm_decides=False,
    ),
    GfxBlock(
        name="keyword_emphasis",
        description="Palabra de carga de la narración (léxico de moods del perfil) → capa de mood de 1–3 s (CSS, intensidad baja) + sello rojo con la palabra.",
        params="(ninguno: detección por regex sobre la narración con el léxico del perfil)",
        rules="el LLM no lo elige; máx 1 por frase; ≥ 20 s entre moods de la misma categoría; si hay más disparadores que el máximo, quedan las palabras más raras.",
        max_per_cap=5, llm_decides=False,
    ),
    GfxBlock(
        name="icon_callout",
        description="Ícono del set (grabado 1890) + la palabra de énfasis; reemplaza al sello de texto cuando la categoría del mood tiene ícono.",
        params="(ninguno: sale del énfasis de palabra y del ícono de su categoría en el perfil)",
        rules="el LLM no lo elige; solo íconos de la lista blanca; sin ícono aprobado → sello de texto solo.",
        max_per_cap=3, llm_decides=False,
    ),
    GfxBlock(
        name="icon_array",
        description="Cifra = N figuras humanas dibujándose en filas de 10; las víctimas en rojo.",
        params="(ninguno: sale de un fact con relación afectados/total, p. ej. '12 de los 300')",
        rules="el LLM no lo elige; solo cifras ≤ 500 con relación total/afectados en el fact; la voz tiene que decir la cifra.",
        max_per_cap=1, llm_decides=False,
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

VALID_BLOCKS: frozenset[str] = frozenset(b.name for b in _ENGINE_INVENTORY)
VALID_CALLOUT_KINDS: frozenset[str] = frozenset({"year", "figure", "name", "place"})


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
    callout_font: str = "Playfair Display SC"   # name/place/year (D13); figure → figure_font
    figure_font: str = "Anton"                 # F2 §0c: fuentes como tokens del perfil (fonts.*)
    title_font: str = "Anton"
    clipping_font: str = "Playfair Display SC"
    callout_font_weight: int = 900             # Black (§0b.8: Bold/Black)
    callout_font_px: int = 158                 # +20 % sobre la muestra del sampler (132 px)
    callout_anton_px: int = 168
    callout_shadow: str = "0 2px 8px rgba(0,0,0,.6)"
    # evidence_zoom (F2 §0b.5: termina en el corte, sostiene ≥ 1 s, nunca vuelve)
    zoom_rect_sec: float = 0.65
    zoom_approach_sec: float = 1.2
    zoom_hold_min_sec: float = 1.0
    zoom_scale: float = 2.2
    zoom_freeze_frame: bool = False          # F4 §3: el render SÍ escala el <video> (C64 era del preview); True = cuadro congelado (lab)
    zoom_box_min: float = 0.06               # lado mínimo del box normalizado
    zoom_box_max: float = 0.25
    zoom_label_margin_px: int = 40           # "DETALLE" a ≥ 40 px del borde
    zoom_conf_min: float = 0.7               # F2b §1.2: confianza mínima de visión para el box de la frase ancla
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
    # animaciones firma (F2 §2; portadas de lab/hyperframes/f1/text_sampler)
    anim_name_place: str = "cascade"         # data_callout kind=name/place
    anim_year: str = "stamp"                 # data_callout kind=year
    anim_figure: str = "number_pop"          # data_callout kind=figure + count_up
    anim_archive_head: str = "cascade"
    anim_detail_label: str = "stamp"         # etiqueta "DETALLE"
    cascade_stagger: float = 0.025           # 25 ms por letra
    cascade_rise_px: int = 60
    stamp_from_scale: float = 1.4
    stamp_rotation: float = -3.0
    stamp_sec: float = 0.18
    pop_from_scale: float = 1.08
    pop_sec: float = 0.25
    # router anti-deformación (F2 §4): movimiento seguro HyperFrames en vez de DepthFlow
    safe_push_scale: float = 1.08            # push-in 1.00 → 1.08 con easing
    safe_pan_frac: float = 0.03              # paneo 3 % del ancho
    # chapter_question / source_tag / sfx (F2 §0d)
    question_dur: float = 2.3                # 2.0–2.5 s al cierre del cap
    question_dim: float = 0.5
    question_max_words: int = 9
    question_font_px: int = 96
    question_auto: bool = False              # F3: pregunta de cierre generada por Flash (gfx_question) — el perfil la prende
    question_pause_sec: float = 3.0          # F3: silencio real al final del cap mientras se ve la pregunta (alarga el cap)
    question_max_words_auto: int = 12        # F3: tope de la pregunta generada
    black_hold_sec: float = 0.0              # F3: corte a negro después de la pregunta de cierre (se suma a la pausa)
    peak_blocks: bool = False                # F3: pico del cap (gfx_peak): bloque grande + ±5 s libres, zoom con latido, reloj
    # F4 §2: el director aplica la identidad del lab (gfx_style). OFF en el motor = F3 tal cual; misterio lo prende
    identity_rules: bool = False
    crossfade_frames: int = 20               # fundido cruzado default de la identidad (20 f)
    fast_cut_sec: float = 3.5                # plano de < 3.5 s (entrante o saliente) → corte (ritmo rápido)
    dip_max_per_cap: int = 1                 # fundido a negro: 1 por cap
    dip_min_t: float = 10.0                  # …no antes de los 10 s (el título abre el cap)
    punch_max_identity: int = 4              # golpes de zoom por cap (F4 §1.2.1: Omar aprobó la forma, no 8)
    icon_stamp_px: int = 112                 # sello dentro del bloque de ícono: M (F4 §1.2.3), aunque el suelto sea S
    ticker_min_times: int = 0                # F4: el reloj solo sale con ≥ N horas verificadas (misterio: 2)
    intensity_director: bool = False         # F4b §1: Flash marca pico, intensidad por frase y cargas (gfx_intensity)
    fragment_director: bool = False          # F4b §2: Flash elige el fragmento literal más impactante (gfx_fragments)
    photo_first_zoom: bool = False           # F4b §3: visión mira cada foto antes del zoom (gfx_vision)
    auto_icons: bool = False                 # F4b §4: palabra de carga concreta sin ícono propio → game-icons
    icon_literal_only: bool = False          # F5b S4: ícono SOLO si la palabra está en icon_words del perfil (nunca la
                                             # categoría, nunca un adjetivo, sin game-icons automáticos)
    # F4c: doctrina del director (ANALISIS_director_trace_2026-10-20 §3). OFF en el motor; misterio las prende
    peak_word: bool = False                  # R3: el pico lleva su palabra de mayor peso (sello + mood + ícono)
    doc_clippings: bool = False              # R6: recorte = documento (solo del fact, suma algo, kicker obligatorio)
    callout_no_repeat: bool = False          # R7: el dato no repite lo que la voz dice en ese tramo
    question_rubric: bool = False            # R8: 3 preguntas + elección por rúbrica (gancho, no trivia)
    visual_critic: bool = False              # F4e 6b: Gemini juzga cada bloque contra el cuadro real (suma/repite/estorba)
    critic_snapshot: bool = False            # G1: el crítico mira el bloque DIBUJADO (snapshot de HyperFrames en t+1 s)
    source_tag_scale: float = 0.4            # 40 % del tamaño del callout
    sfx_gain_db: float = -18.0               # bajo la voz
    sfx_shift_max_ms: int = 120              # se corre al hueco entre palabras más cercano
    # keyword_emphasis + moods (F2b §2)
    emphasis_base_per_cap: int = 3          # selección inicial (las más raras); el relleno de huecos sube hasta max_per_cap
    emphasis_same_cat_gap_sec: float = 20.0  # mínimo entre moods de la misma categoría
    mood_dur: float = 2.5                    # duración de la capa de mood (1–3 s)
    emphasis_stamp: bool = True              # sello rojo con la palabra (opcional por perfil)
    emphasis_stamp_sec: float = 1.6          # el sello se ve 1.6 s dentro del mood
    emphasis_stamp_px: int = 112
    # íconos (F2b §3)
    icon_px: int = 190                       # lado del ícono del icon_callout
    icon_fallback_lucide: bool = False       # respaldo Lucide solo para claves rechazadas por Omar (se prende por perfil)
    icon_array_max: int = 500
    icon_array_dur: float = 4.0
    icon_array_px: int = 34                  # lado de cada figura
    mood_dark_flicker: bool = True           # mood oscuridad: 2 parpadeos de luz (PARADA 1: OFF en misterio)
    grade_default: str = "off"
    grain_opacity: float = 0.15              # F2 §0c: tokens del perfil (antes constantes de _GRADE_OFF)
    vignette_opacity: float = 0.20
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


# ═══════════════════════════════════════════════════════════════
#  PERFIL DE CANAL (F2 §0c)
# ═══════════════════════════════════════════════════════════════

_RULE_FIELDS: frozenset[str] = frozenset(f.name for f in fields(GfxRules))
_PROFILE_KEYS: frozenset[str] = frozenset({"name", "description", "nichos", "fonts", "tokens", "blocks", "sfx", "moods",
                                          "identity",    # F3: lo escribe el lab; el motor lo ignora
                                          "channel_bug"})   # F4b §0.3: marca del canal (gfx_bug)
# F2b §2: capas de mood que el templater sabe dibujar (CSS, nunca toca píxeles)
VALID_MOOD_LAYERS: frozenset[str] = frozenset({"veneno", "agua", "muerte", "oscuridad", "minima"})
# F4c R5: capa mínima (viñeta + desaturación leve) para las categorías de reserva hasta que el lab les dé forma; no
# exige los MIN_TRIGGERS_ACTIVE disparadores de una capa propia
MINIMAL_MOOD_LAYER = "minima"
# claves del set de íconos (= gfx_icons.ICON_WHITELIST; acá sin importar gfx_icons para no crear un ciclo)
ICON_KEYS: frozenset[str] = frozenset({"calavera", "gota", "llama", "biohazard", "reloj", "candado", "ojo_tachado",
                                       "balanza", "cruz", "persona", "edificio_ruina", "pregunta", "espiral", "rayo_tachado"})
VALID_ICON_ANIMS: frozenset[str] = frozenset({"ink_bleed", "press_wipe", "engrave", "stamp"})
MIN_TRIGGERS_ACTIVE: int = 25
_FONT_KEYS: frozenset[str] = frozenset({"subs", "title", "callout", "callout_figure", "clipping"})
# fuentes que el templater sabe cargar (@font-face en gfx_common.css → script_engine/fonts)
KNOWN_FONTS: frozenset[str] = frozenset({"Anton", "Playfair Display SC"})


def profile_path(name: str) -> Path:
    return GFX_PROFILES_DIR / f"{name}.json"


def active_profile_name() -> str:
    """GFX_PROFILE (env) > perfil cuyo `nichos` contiene el nicho activo > misterio."""
    env = os.environ.get("GFX_PROFILE", "").strip()
    if env:
        return env
    try:
        from nicho_config import get_active_nicho
        nicho = str(get_active_nicho().get("nombre", ""))
    except Exception:  # noqa: BLE001 — sin nicho → perfil por default
        nicho = ""
    for p in sorted(GFX_PROFILES_DIR.glob("*.json")):
        try:
            if nicho and nicho in json.loads(p.read_text(encoding="utf-8")).get("nichos", []):
                return p.stem
        except (OSError, ValueError):
            continue
    return DEFAULT_PROFILE


def load_profile(name: str | None = None) -> dict[str, Any]:
    """Lee y valida un perfil. Claves o tokens desconocidos → ValueError (un typo no pasa en silencio)."""
    name = name or active_profile_name()
    prof = json.loads(profile_path(name).read_text(encoding="utf-8"))
    bad = set(prof) - _PROFILE_KEYS
    bad |= {f"tokens.{k}" for k in prof.get("tokens", {}) if k not in _RULE_FIELDS}
    bad |= {f"fonts.{k}" for k in prof.get("fonts", {}) if k not in _FONT_KEYS}
    bad |= {f"blocks.{k}" for k in prof.get("blocks", {}) if k not in VALID_BLOCKS}
    bad |= {f"fonts.{k}={v!r} (sin @font-face)" for k, v in prof.get("fonts", {}).items() if v not in KNOWN_FONTS}
    bad |= {f"sfx.{k}" for k, v in prof.get("sfx", {}).items()
            if k not in VALID_BLOCKS or not (SFX_DIR / str(v.get("file", ""))).exists()}
    for cat, m in (prof.get("moods") or {}).items():
        extra = set(m) - {"active", "triggers", "layer", "icon_words", "icon_anim", "sfx"}
        if extra:
            bad.add(f"moods.{cat}: claves {sorted(extra)}")
        if m.get("icon_anim") not in (None, *VALID_ICON_ANIMS):
            bad.add(f"moods.{cat}.icon_anim={m.get('icon_anim')!r}")
        # pre-merge: ícono POR PALABRA (la palabra tiene que ser lo que el ícono dibuja; si no, no está acá)
        iw = m.get("icon_words") or {}
        if any(w not in (m.get("triggers") or {}) or k not in ICON_KEYS for w, k in iw.items()):
            bad.add(f"moods.{cat}.icon_words (palabra del léxico → clave del set)")
        if m.get("sfx") and not (SFX_DIR / str(m["sfx"].get("file", ""))).exists():
            bad.add(f"moods.{cat}.sfx (wav inexistente)")
        if m.get("active") and (m.get("layer") not in VALID_MOOD_LAYERS or (
                m.get("layer") != MINIMAL_MOOD_LAYER and len(m.get("triggers", {})) < MIN_TRIGGERS_ACTIVE)):
            bad.add(f"moods.{cat} (activa: capa válida y ≥ {MIN_TRIGGERS_ACTIVE} disparadores)")
        # PARADA 1 F2b: triggers = {palabra: peso 1–3}
        if not isinstance(m.get("triggers"), dict) or any(w not in (1, 2, 3) for w in m["triggers"].values()):
            bad.add(f"moods.{cat}.triggers (dict palabra → peso 1–3)")
    if bad:
        raise ValueError(f"perfil gfx '{name}': claves desconocidas {sorted(bad)}")
    return prof


def rules_from_profile(prof: dict[str, Any]) -> GfxRules:
    """Motor (defaults de GfxRules) pisado por los tokens del perfil."""
    over: dict[str, Any] = dict(prof.get("tokens", {}))
    fonts = prof.get("fonts", {})
    # fonts.subs NO se cablea: los subs ASS de fase2b quedan constantes (sin --gfx byte-idéntico)
    for key, field_name in (("callout", "callout_font"), ("callout_figure", "figure_font"),
                            ("title", "title_font"), ("clipping", "clipping_font")):
        if fonts.get(key):
            over[field_name] = fonts[key]
    ar = prof.get("blocks", {}).get("archive_clipping")
    if ar is not None:
        over["archive_max_per_cap"] = int(ar.get("max_per_cap", 0)) if ar.get("enabled", True) else 0
    return replace(GfxRules(), **over)


def inventory_from_profile(prof: dict[str, Any]) -> tuple[GfxBlock, ...]:
    """Inventario del motor con enabled / max_per_cap / where del perfil."""
    out = []
    for b in _ENGINE_INVENTORY:
        cfg = prof.get("blocks", {}).get(b.name, {})
        enabled = bool(cfg.get("enabled", True))
        out.append(replace(b, enabled=enabled,
                           max_per_cap=int(cfg.get("max_per_cap", b.max_per_cap)) if enabled else 0,
                           where=str(cfg.get("where", ""))))
    return tuple(out)


def grade_variants(rules: GfxRules) -> dict[str, dict]:
    """Recetas de grade; 'off' toma grano/viñeta del perfil."""
    off = {"gr-halation": 0.0, "gr-haze": 0.0, "gr-palette": 0.0, "gr-shadowteal": 0.0,
           "gr-vignette": rules.vignette_opacity, "gr-grain": rules.grain_opacity}
    return {"A": {"intensity": 0.5, "opacity": _GRADE_A}, "B": {"intensity": 0.5, "opacity": _GRADE_B},
            "C": {"intensity": 0.3, "opacity": _GRADE_B}, "off": {"intensity": 1.0, "opacity": off}}


ACTIVE_PROFILE: dict[str, Any] = load_profile()
gfx_rules = rules_from_profile(ACTIVE_PROFILE)
GFX_INVENTORY: tuple[GfxBlock, ...] = inventory_from_profile(ACTIVE_PROFILE)
GRADE_VARIANTS: dict[str, dict] = grade_variants(gfx_rules)
LLM_BLOCKS: frozenset[str] = frozenset(b.name for b in GFX_INVENTORY if b.llm_decides and b.enabled)


def active_moods() -> dict[str, dict[str, Any]]:
    """F2b §2: categorías de mood ACTIVAS del perfil {categoría: {triggers, layer, icon}} (las de reserva no)."""
    return {k: v for k, v in (ACTIVE_PROFILE.get("moods") or {}).items() if v.get("active")}


def max_per_cap(block: str) -> int:
    """Máximo por cap de un bloque según el perfil activo (0 si está apagado; KeyError si no existe)."""
    return next(b.max_per_cap for b in GFX_INVENTORY if b.name == block)


def block_enabled(block: str) -> bool:
    return next(b.enabled for b in GFX_INVENTORY if b.name == block)


def sfx_for(block: str) -> tuple[Path, float] | None:
    """SFX que el perfil declara para un bloque: (wav, ganancia dB) o None."""
    cfg = ACTIVE_PROFILE.get("sfx", {}).get(block)
    if not cfg:
        return None
    return SFX_DIR / cfg["file"], float(cfg.get("gain_db", gfx_rules.sfx_gain_db))

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
        if not b.enabled:                    # el perfil lo apaga → el LLM ni lo ve
            continue
        who = "VOS elegís" if b.llm_decides else "NO lo elegís (determinista)"
        lim = f"máx {b.max_per_cap} por cap; " if b.llm_decides else ""
        where = f" Dónde: {b.where}." if b.where else ""
        lines.append(f"- {b.name} [{who}]: {b.description} Parámetros: {b.params} Reglas: {lim}{b.rules}{where}")
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
