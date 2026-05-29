"""
art_profiles.py — ADN Visual del pipeline (Refactor v2.2: Vibrant Cinematic).

Cambios v2.2 vs v2.1:
  - SUBMARINE: paleta cian DESATURADA → cian-teal RICO con acentos bioluminiscentes
    vivos (cyan eléctrico, magentas, azules profundos saturados pero filmicos).
    El look "documental moody" se mantiene vía grano + aberración + óptica vintage,
    NO vía colores apagados.
  - INTERIOR: tonos cálidos más ricos (ámbar, oro viejo) sin saturación plástica.
  - NEGATIVE_PROMPT_GLOBAL: removido "bright saturated colors" (estaba bloqueando
    los acentos bioluminiscentes y luces dramáticas que QUEREMOS).
  - Nuevo helper `stitch_prompt_with_subject()`: inyecta canonical_subject_description
    en posición correcta (entre art_profile y raw_prompt) para forzar consistencia
    visual del sujeto recurrente.
"""
from __future__ import annotations

# ═══════════════════════════════════════════
#  Escudo de Excepciones (Negative Prompt)
# ═══════════════════════════════════════════

# v2.2: removido "bright saturated colors" — bloqueaba bioluminiscencia y luces
# dramáticas que sí queremos. Mantenemos solo lo que rompe la estética cinemática.
# v2.4 (Solución 4): ampliado con anti-anacronismos, anti-texto-inventado y
# anti-hollywood-default para reducir re-rolls obligatorios en topics históricos.
NEGATIVE_PROMPT_GLOBAL: str = (
    # ── Anatomía / artefactos ──
    "musical instruments, piano, extra fingers, deformed hands, "
    "distorted anatomy, "
    # ── Texto y branding inventado ──
    "text on images, signs, logos, watermarks, "
    "fictional names on gravestones, fictional names on signs, "
    "modern infographics, pie charts, data overlays, "
    # ── Estética rota ──
    "cartoon, 3d render cgi, low quality, plastic toy colors, "
    "neon airbrush, oversaturated cartoon palette, "
    "floating monitors, plastic materials, harsh LED lighting, "
    # ── Anacronismos contemporáneos en escenas históricas ──
    "smartphones, tablets, modern LED screens, modern digital displays, "
    "contemporary 2020s clothing, Wrangler jeans, Adidas sneakers, Nike, "
    "modern cars, modern vehicles, modern street furniture, "
    # ── Hollywood-default geográfico ──
    "Monument Valley landmarks, Grand Canyon mesas, Hollywood western backdrop."
)

# ═══════════════════════════════════════════
#  Diccionario de Estilos (ADN con Textura Óptica + Color Rico)
# ═══════════════════════════════════════════

ART_PROFILES: dict[str, str] = {
    "SUBMARINE": (
        "Cinematic deep-sea documentary photography, rich teal and deep cyan palette "
        "with vivid bioluminescent accents in electric blue and magenta, "
        "high contrast against absolute black void, dramatic chiaroscuro, "
        "fine film grain, subtle chromatic aberration, marine snow particles, "
        "vintage Zeiss underwater optics, deep shadows with luminous highlights."
    ),
    "INTERIOR": (
        "Cinematic interior photography, warm amber and burnished gold palette "
        "with deep mahogany shadows, Kodak Portra 800 aesthetic, "
        "rich color saturation in shadows, dust motes catching shafts of warm light, "
        "soft analog falloff, textured wood and oxidized brass surfaces, "
        "35mm film stock with fine grain, period-accurate practical lighting."
    ),
    "POLAR": (
        "Cinematic polar expedition photography, icy cyan-white palette "
        "with deep cobalt shadows and crisp golden hour highlights, "
        "fine Leica grain, wind-driven snow particles, blown specular highlights, "
        "vintage rangefinder optics, lens frost edges, "
        "high dynamic range between shadow and snow glare."
    ),
    "MARITIME_EXTERIOR": (
        "Cinematic maritime documentary, rich steel-blue palette with "
        "warm amber sodium-lamp highlights and deep storm-grey shadows, "
        "16mm film aesthetic, fine grain, salt-streaked lens, "
        "dramatic overcast diffusion with shafts of broken sunlight, "
        "subtle camera motion, weathered metal and wet canvas textures."
    ),
    "DESERT": (
        "Cinematic desert expedition photography, scorched ochre and burnt "
        "sienna palette with deep violet shadows and amber low-sun highlights, "
        "dramatic heat haze on the horizon, 16mm Panavision anamorphic aesthetic, "
        "fine grain, drifting dust and wind-blown sand particles, "
        "vintage warm-toned optics, long hard shadows against sun-bleached terrain."
    ),
    "JUNGLE": (
        "Cinematic tropical jungle expedition photography, deep emerald and "
        "moss-green palette with humid amber light shafts piercing dense canopy, "
        "near-black shadows in undergrowth, 35mm Aaton aesthetic, "
        "fine grain, drifting vapor and floating spores in filtered sunbeams, "
        "vintage Arriflex optics, claustrophobic high-contrast composition."
    ),
    "WILDERNESS": (
        "Cinematic wilderness landscape photography, muted forest green and "
        "slate-blue palette with weathered stone greys and ember sunset highlights, "
        "vast melancholic atmospheric depth, 65mm Panavision large-format aesthetic, "
        "subtle grain, low-lying morning mist and cold breath vapor, "
        "vintage anamorphic optics, deep valley shadows with ridge-line highlights."
    ),
    "URBAN": (
        "Cinematic urban nocturne photography, deep cyan and slate-grey palette "
        "with amber sodium-vapor streetlight highlights and oxblood neon accents, "
        "high-contrast wet-pavement reflections, 35mm anamorphic aesthetic, "
        "fine grain, drifting steam from grates and atmospheric haze, "
        "vintage Cooke S4 optics, deep alley shadows with practical light pools."
    ),
    "INDUSTRIAL": (
        "Cinematic industrial documentary photography, cold slate-blue and "
        "ash-grey palette with desaturated mineral tones and deep machine-oil "
        "shadows, oppressive low-key mineral lighting, 16mm documentary aesthetic, "
        "heavy grain, suspended industrial dust haze and slow-drifting cold smoke, "
        "vintage anamorphic optics, harsh top-down shafts cutting through "
        "overcast gloom. DOMINANT PALETTE: cold slate-blue and ash-grey, "
        "desaturated, minimal warm tones; AVOID sepia, golden, tungsten, amber, "
        "rust unless explicitly specified by scene context."
    ),
    "UNDERGROUND": (
        "Cinematic subterranean exploration photography, damp slate-cyan and "
        "mineral-green palette with warm amber torchlight and absolute black voids, "
        "oppressive close-quarters chiaroscuro, 35mm aesthetic, "
        "fine grain, suspended limestone dust and breath vapor in cold air, "
        "vintage Cooke Speed Panchro optics, deep cavernous shadows pierced by "
        "single light sources."
    ),
    "AERIAL": (
        "Cinematic high-altitude aerial photography, deep stratospheric cyan and "
        "storm-grey cloud palette with warm horizon amber and golden ridge highlights, "
        "vast atmospheric perspective with layered haze, 65mm large-format aesthetic, "
        "subtle grain, ice crystal refraction and volumetric cloud densities, "
        "vintage IMAX-style optics, dramatic shadow contrast across cloud tops."
    ),
    "SPACE": (
        "Cinematic NASA-archival space photography, deep cobalt void and "
        "warm solar amber palette with rust-red planetary surfaces and "
        "absolute black shadow, hard sunlight contrast with no atmospheric diffusion, "
        "70mm Hasselblad aesthetic, fine grain, suspended particulate in vacuum "
        "and subtle lens flare from direct sun, vintage Apollo-era optics, "
        "crushed black shadows against blown-highlight sunlit surfaces."
    ),
    "HISTORICAL": (
        "Cinematic pre-industrial period photography, candle-lit gold and "
        "parchment-cream palette with deep umber shadows and ember firelight highlights, "
        "warm low-key chiaroscuro, 35mm Panavision E-series anamorphic aesthetic, "
        "fine grain, drifting torch smoke and dust motes in shafts of natural light, "
        "vintage anamorphic optics, deep shadow textures on stone and aged fabric."
    ),
}
# ═══════════════════════════════════════════
#  Helpers de validación
# ═══════════════════════════════════════════

VALID_PROFILES: frozenset[str] = frozenset(ART_PROFILES.keys())


def stitch_prompt(art_profile: str, raw_prompt: str) -> str:
    """Stitching v2.3 (Fase A bugfix): raw_prompt PRIMERO, profile al FINAL.

    Razón: Flux 1.1 Pro pondera tokens iniciales con más peso. La doc oficial
    de fal.ai dice: 'If you bury the subject at the end of a long description,
    FLUX may deprioritize it. This is the most common structural mistake'.
    Estructura oficial recomendada: Subject → Action → Environment → Lighting → Style.

    Antes (v2.2, BUG): [PROFILE 50 palabras] + [raw_prompt] → "interior" en
    posición #2 dominaba la escena, ignorando "deck of vessel" del raw.
    Ahora (v2.3): [raw_prompt sujeto+acción] + [PROFILE estilo/grano/paleta].
    """
    if art_profile not in ART_PROFILES:
        raise KeyError(f"art_profile desconocido: '{art_profile}'")
    return f"{raw_prompt.strip()} {ART_PROFILES[art_profile]}"


def stitch_prompt_with_subject(
    art_profile: str,
    raw_prompt: str,
    canonical_subject: str | None = None,
) -> str:
    """
    Stitching v2.3 (Fase A bugfix): orden corregido para Flux.

    Estructura oficial Flux: Subject → Action → Environment → Style.
    Antes (v2.2): [PROFILE] [SUBJECT] [RAW]  ← profile dominaba
    Ahora (v2.3): [SUBJECT] [RAW]  [PROFILE]  ← sujeto domina, profile modula

    Si canonical_subject es None o vacío, equivale a stitch_prompt() normal.
    """
    if art_profile not in ART_PROFILES:
        raise KeyError(f"art_profile desconocido: '{art_profile}'")
    profile_text = ART_PROFILES[art_profile]
    raw_text = raw_prompt.strip()
    if canonical_subject and canonical_subject.strip():
        subject_text = canonical_subject.strip().rstrip(".") + "."
        return f"{subject_text} {raw_text} {profile_text}"
    return f"{raw_text} {profile_text}"


# ═══════════════════════════════════════════
#  Detección de "fugas de estilo" (Protocolo v2)
# ═══════════════════════════════════════════

STYLE_LEAKAGE_KEYWORDS: tuple[str, ...] = (
    "cinematic", "8k", "4k", "film grain", "film stock",
    "dramatic lighting", "volumetric", "anamorphic", "lens flare",
    "hyper-realistic", "photorealistic", "national geographic",
    "35mm", "kodak", "vision3", "grainy", "documentary style",
    "depth of field", "bokeh", "epic composition", "god rays",
    "atmospheric lighting", "moody lighting",
)


def detect_style_leakage(prompt: str) -> list[str]:
    low = prompt.lower()
    return [kw for kw in STYLE_LEAKAGE_KEYWORDS if kw in low]


# ═══════════════════════════════════════════
#  Detección de "fugas de metadatos" (Protocolo v2.2)
# ═══════════════════════════════════════════
#
# Bug observado en producción (cap 6 caso Bioluminiscencia): Gemini empezó
# image_prompts con "SUBMARINE, flux, A wide shot..." — metiendo metadatos
# del JSON (art_profile + render_engine) DENTRO del prompt como si fueran
# keywords. Flux interpretó "SUBMARINE" como sujeto → generó submarinos en
# vez de animales bioluminiscentes.
#
# Esta lista detecta ese leak post-generación. La sanitización in-place vive
# en script_generator.sanitize_metadata_leak().

METADATA_LEAKAGE_PREFIXES: tuple[str, ...] = (
    # art_profiles válidos (seguidos de coma o espacio)
    "submarine,", "submarine ",
    "interior,", "interior ",
    "polar,", "polar ",
    "maritime_exterior,", "maritime exterior,",
    "desert,", "desert ",
    "jungle,", "jungle ",
    "wilderness,", "wilderness ",
    "urban,", "urban ",
    "industrial,", "industrial ",
    "underground,", "underground ",
    "aerial,", "aerial ",
    "space,", "space ",
    "historical,", "historical ",
    # render_engines
    "flux,", "flux ",
    "veo,", "veo ",
    "leonardo,",
    # animation_styles
    "ken_burns_zoom,", "ken_burns,",
    # combinaciones comunes
    "flux render engine,", "flux render engine.",
    "render engine flux,",
)


def detect_metadata_leak(prompt: str) -> bool:
    """True si el prompt arranca con metadatos del JSON."""
    if not prompt:
        return False
    low = prompt.lower().lstrip()
    return any(low.startswith(p) for p in METADATA_LEAKAGE_PREFIXES)



# ═══════════════════════════════════════════════════════════════════════
#  PATCH CHAT 14 — approach 2-zona para video_prompt de caps Veo
#  AGREGAR AL FINAL de art_profiles.py
# ═══════════════════════════════════════════════════════════════════════
#
#  Después de pegar este bloque, art_profiles.py expone:
#    - ART_PROFILES (existente, sin tocar) — zona 2 estática para Flux y Veo image_prompt
#    - VEO_MOTION (nuevo) — zona 2 motion para Veo video_prompt
#    - stitch_prompt / stitch_prompt_with_subject (existentes, sin tocar)
#    - stitch_veo_video_prompt (nuevo)
#
#  Las 13 keys de VEO_MOTION coinciden 1:1 con las de ART_PROFILES.
#  Hay un assert al final del bloque que falla en import si alguien rompe
#  la paridad por accidente.
#
# ═══════════════════════════════════════════════════════════════════════


# ═══════════════════════════════════════════
#  VEO_MOTION — zona 2 motion (caps Veo only)
# ═══════════════════════════════════════════
#
# Approach 2-zona para video_prompt de caps Veo:
#
#   zona 1 (LLM escribe):
#     - movimiento del sujeto (coat swaying, eyes blinking, camera arc específico
#       como push in / pull out / orbit)
#     - movimiento ambient específico de la escena (dust around the miner)
#
#   zona 2 (fija, este dict):
#     - camera behavior uniforme coherente con un documental observacional
#     - ambient signature universal del profile (marine snow, heat shimmer, etc.)
#     - hard rules invariantes (no cuts, no rapid motion, atmósfera period-correct)
#
# Lo que NO va acá:
#   - lighting / palette / film grain / óptica → vive en ART_PROFILES
#   - movimiento del sujeto o ambient particular del cap → lo escribe el LLM
#
# Aplica solo a caps 1 y 7 (render_engine="veo"). Los caps 2-6 (Flux) generan
# fotos estáticas y el movimiento se lo agrega depthflow en fase2b — m03 no
# emite motion para Flux.

VEO_MOTION: dict[str, str] = {
    "SUBMARINE": (
        "static composition with very subtle slow drift, "
        "marine snow particles drifting upward through cones of light, "
        "distant suspended particulate floating in deep water, "
        "no cuts, no rapid motion, period-correct submerged atmosphere"
    ),
    "INTERIOR": (
        "static composition with very subtle slow drift, "
        "dust motes drifting slowly through shafts of light, "
        "distant curtain swaying faintly in still air, "
        "quiet stillness of an enclosed period space, "
        "no cuts, no rapid motion, period-correct interior atmosphere"
    ),
    "POLAR": (
        "static composition with very subtle slow drift, "
        "wind-driven snow particles drifting across the frame, "
        "distant cold breath vapor rising from figures, "
        "ice crystals catching glints of light, "
        "no cuts, no rapid motion, period-correct expedition atmosphere"
    ),
    "MARITIME_EXTERIOR": (
        "static composition with very subtle slow drift, "
        "salt spray drifting across the lens, "
        "distant whitecaps cresting on the horizon, "
        "low cloud cover slowly shifting overhead, "
        "no cuts, no rapid motion, period-correct maritime atmosphere"
    ),
    "DESERT": (
        "static composition with very subtle slow drift, "
        "fine drifting sand particles carried on dry wind, "
        "distant heat shimmer warping the horizon, "
        "long shadows stretching across the terrain, "
        "no cuts, no rapid motion, period-correct expedition atmosphere"
    ),
    "JUNGLE": (
        "static composition with very subtle slow drift, "
        "drifting vapor and floating spores in filtered light shafts, "
        "distant canopy leaves swaying faintly in still humid air, "
        "fine mist hanging between trunks, "
        "no cuts, no rapid motion, period-correct tropical atmosphere"
    ),
    "WILDERNESS": (
        "static composition with very subtle slow drift, "
        "low-lying morning mist drifting through the valley, "
        "cold breath vapor rising slowly from figures, "
        "distant ridgeline shadows shifting imperceptibly, "
        "no cuts, no rapid motion, period-correct wilderness atmosphere"
    ),
    "URBAN": (
        "static composition with very subtle slow drift, "
        "steam rising slowly from street grates, "
        "atmospheric haze drifting through pools of streetlight, "
        "distant indistinct movement of pedestrians far away, "
        "no cuts, no rapid motion, period-correct urban atmosphere"
    ),
    "INDUSTRIAL": (
        "static composition with very subtle slow drift, "
        "suspended industrial dust haze hanging motionless in cold air, "
        "slow-drifting cold smoke from distant stacks, "
        "stagnant atmosphere with no human movement, "
        "no cuts, no rapid motion, period-correct industrial atmosphere"
    ),
    "UNDERGROUND": (
        "static composition with very subtle slow drift, "
        "suspended limestone dust drifting in the still air, "
        "cold breath vapor rising visibly in the chill, "
        "distant water dripping echoes implied by mist near walls, "
        "no cuts, no rapid motion, period-correct subterranean atmosphere"
    ),
    "AERIAL": (
        "static composition with very subtle slow drift, "
        "layered atmospheric haze shifting between cloud densities, "
        "ice crystal refraction sparkling at the edges of the frame, "
        "distant cloud tops slowly rolling beneath, "
        "no cuts, no rapid motion, period-correct high-altitude atmosphere"
    ),
    "SPACE": (
        "static composition with very subtle slow drift, "
        "suspended particulate floating motionless in vacuum, "
        "subtle lens flare drifting across the edge of the frame, "
        "absolute stillness of airless void, "
        "no cuts, no rapid motion, period-correct space mission atmosphere"
    ),
    "HISTORICAL": (
        "static composition with very subtle slow drift, "
        "drifting torch smoke curling slowly upward, "
        "dust motes suspended in shafts of natural light, "
        "distant flame flicker just outside the frame edge, "
        "no cuts, no rapid motion, period-correct pre-industrial atmosphere"
    ),
}

VALID_VEO_MOTION_PROFILES: frozenset[str] = frozenset(VEO_MOTION.keys())

# Paridad ART_PROFILES ↔ VEO_MOTION: si alguien agrega/quita un profile
# de uno solo de los dos dicts, este assert revienta el import.
assert VALID_VEO_MOTION_PROFILES == VALID_PROFILES, (
    f"VEO_MOTION desincronizado con ART_PROFILES. "
    f"Solo en ART_PROFILES: {VALID_PROFILES - VALID_VEO_MOTION_PROFILES}. "
    f"Solo en VEO_MOTION:   {VALID_VEO_MOTION_PROFILES - VALID_PROFILES}."
)


# ═══════════════════════════════════════════
#  Helper de stitching para video_prompt Veo
# ═══════════════════════════════════════════

def stitch_veo_video_prompt(art_profile: str, raw_video_prompt: str) -> str:
    """Stitch para video_prompt de caps Veo (zona 1 + zona 2).

    Estructura final del string devuelto:

        [raw_video_prompt]               ← zona 1, escrita por el LLM:
                                            movimiento del sujeto + ambient
                                            específico de la escena.

        [ART_PROFILES[profile]]          ← zona 2 estética:
                                            paleta, lighting, óptica, grain.
                                            (Misma string que se usa para
                                            Flux y para image_prompt de Veo.)

        [VEO_MOTION[profile]]            ← zona 2 motion:
                                            camera behavior + ambient signature
                                            universal del profile + hard rules.

    Análogo a stitch_prompt() pero exclusivo para video_prompt de Veo, que
    necesita la capa de motion adicional. Para image_prompt de Veo (estática)
    se sigue usando stitch_prompt() / stitch_prompt_with_subject() normal.

    Args:
        art_profile: clave de ART_PROFILES (ej. "SUBMARINE", "URBAN").
        raw_video_prompt: zona 1 cruda emitida por el LLM, validada antes
            de llegar acá (sin lighting/palette/style — eso lo agrega zona 2).

    Returns:
        String final lista para mandar a Veo.

    Raises:
        KeyError: si art_profile no existe en ART_PROFILES o en VEO_MOTION.
    """
    if art_profile not in ART_PROFILES:
        raise KeyError(f"art_profile desconocido: '{art_profile}'")
    if art_profile not in VEO_MOTION:
        # Defensa redundante: el assert de paridad ya lo garantiza al import,
        # pero si alguien muta VEO_MOTION en runtime esto lo atrapa.
        raise KeyError(f"VEO_MOTION no definido para profile: '{art_profile}'")
    raw = raw_video_prompt.strip()
    profile_text = ART_PROFILES[art_profile]
    motion_text = VEO_MOTION[art_profile]
    return f"{raw} {profile_text} {motion_text}"


# Guía pedagógica por profile (cuándo usar cada uno).
# OJO: NO confundir con el texto largo de ART_PROFILES (ese es para
# inyectar a Flux). Esta guía es solo para que Flash entienda criterios.
PROFILE_GUIDE: dict[str, str] = {
    "POLAR": (
        "Ártico/Antártico, hielo, glaciares, expediciones polares. "
        "Paleta cyan-blanca con sombras cobalto."
    ),
    "DESERT": (
        "Desierto, dunas, outback, mesetas áridas, pueblos del desierto. "
        "Paleta ocre/sienna quemada con sombras violetas. Calor visible."
    ),
    "JUNGLE": (
        "Selva tropical densa, vegetación cerrada, copas espesas, vapor "
        "y esporas. Paleta esmeralda con luz ámbar filtrada por canopy."
    ),
    "WILDERNESS": (
        "Naturaleza salvaje no tropical: bosques templados, valles, "
        "montañas, lagos, ríos, parques nacionales fríos. "
        "Paleta verde apagado y azul pizarra, niebla matinal."
    ),
    "AERIAL": (
        "Toma desde altura considerable: nubes vistas desde arriba, "
        "panorámica de tierra desde avión, vuelo en cabina alta. "
        "Perspectiva atmosférica con capas de bruma."
    ),
    "SPACE": (
        "Espacio exterior, cosmos, planetas, vacío negro absoluto, "
        "estética NASA-archival. Sin atmósfera, sombras duras."
    ),
    "SUBMARINE": (
        "FONDO marino, abismos oceánicos, pecios sumergidos en negro "
        "absoluto, criaturas bioluminiscentes, expediciones submarinas. "
        "NO usar para barcos en superficie (eso es MARITIME_EXTERIOR)."
    ),
    "MARITIME_EXTERIOR": (
        "Barcos en superficie, puertos, mar abierto vista desde cubierta, "
        "naufragios sobre el agua, puentes de mando. "
        "Paleta steel-blue con ámbar de lámparas. Aire libre marino."
    ),
    "INTERIOR": (
        "Interiores cálidos de cualquier época moderna (siglo XX o XXI): "
        "oficinas, salones, bibliotecas, comedores, casas. Madera, latón, "
        "lámparas. Paleta ámbar/oro viejo con sombras profundas."
    ),
    "URBAN": (
        "Calles de ciudad nocturnas, neón, asfalto mojado, faroles ámbar, "
        "callejones, fachadas urbanas. NO usar para pueblos rurales o "
        "casas aisladas (eso es DESERT/WILDERNESS según contexto)."
    ),
    "INDUSTRIAL": (
        "Fábricas, plantas procesadoras, refinerías, instalaciones "
        "industriales del siglo XX/XXI. Paleta cold slate-blue/ash-grey "
        "OBLIGATORIA. EVITAR sepia/golden/amber (eso entra en HISTORICAL "
        "o INTERIOR). Maquinaria pesada, vapor, polvo industrial."
    ),
    "UNDERGROUND": (
        "Subterráneo: minas excavadas, cuevas, túneles, galerías, "
        "catacumbas. Luz puntual de antorchas o linternas. Paleta "
        "mineral-green/slate-cyan con voids negros. NO confundir con "
        "INDUSTRIAL (planta procesadora) — UNDERGROUND es la galería."
    ),
    "HISTORICAL": (
        "EXCLUSIVO para épocas PRE-INDUSTRIALES (Antigüedad, Edad Media, "
        "época colonial, hasta inicios siglo XIX). Iluminación por velas, "
        "antorchas, fuegos de hogar. Paleta candle-lit gold + parchment. "
        "PROHIBIDO para temas del siglo XX/XXI — usar INTERIOR/INDUSTRIAL."
    ),
}
