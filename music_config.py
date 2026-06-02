"""
music_config.py — Configuración hardcoded para m07 music_director.

PR 2.B chat 25. D-B1: prompts curados a mano, NO emitidos por LLM.
Las 7 entries de MUSIC_PROMPTS deben estar TODAS completas antes de la primera
corrida — validate_music_config() raisa MusicConfigError si alguna es
placeholder. Esto evita gastar plata en ElevenLabs Music con prompts vacíos.

Camino A aprobado chat 25:
- MUSIC_LENGTH_MS = 60000 (60s tracks, sweet spot para plan Creator/Pro)
- MATCH_SCORE_THRESHOLD = 80 (conservador, evita reuso espurio del matcher LLM)
- URL endpoint correcta: /v1/music/detailed (NO /v1/music/compose-detailed)
"""

from __future__ import annotations


# ═══════════════════════════════════════════════════════════════
#  EXCEPCIONES
# ═══════════════════════════════════════════════════════════════

class MusicConfigError(Exception):
    """Raise cuando music_config tiene placeholders/prompts incompletos.

    m07_music_director debe llamar a validate_music_config() al inicio para
    evitar gastar plata en ElevenLabs con prompts vacíos o malformados.
    """


# ═══════════════════════════════════════════════════════════════
#  CONSTANTES OPERACIONALES
# ═══════════════════════════════════════════════════════════════

# Endpoint correcto verificado en docu oficial chat 25.
# NO usar /v1/music/compose-detailed (URL del handoff chat 24, incorrecta).
MUSIC_API_URL = "https://api.elevenlabs.io/v1/music/detailed"

# Único modelo de música disponible (oct 2025+). El SDK lista solo "music_v1".
MUSIC_MODEL_ID = "music_v1"

# Duración fija para todos los tracks de la library. Camino A: 60s.
# Cada cap del video va a loopear este track tantas veces como necesite.
# Min 3000ms, max 600000ms según docs.
MUSIC_LENGTH_MS = 60000

# Threshold del matcher LLM (chat 25). Si match_score >= este valor, reusa el
# track de la library en vez de generar nuevo. 80 es conservador inicial; bajar
# a 70 si la validación palpable confirma que el matcher es confiable.
MATCH_SCORE_THRESHOLD = 80

# Timeout para llamadas a ElevenLabs Music. Music tarda más que TTS porque
# genera audio largo. 180s = 3 minutos margen amplio.
MUSIC_REQUEST_TIMEOUT_SEC = 180

# Output format por default. mp3_44100_128 está disponible en plan Creator+
# y es buena calidad para fondo documental.
MUSIC_OUTPUT_FORMAT = "mp3_44100_128"


# ═══════════════════════════════════════════════════════════════
#  PROMPTS POR NARRATIVE_INTENT — CURADOS A MANO
# ═══════════════════════════════════════════════════════════════
#
# Cada prompt sigue la estructura:
#   género/tonalidad → instrumentos → energía/dinámica → loop-friendly → BPM
#
# IMPORTANTE: estos prompts contienen SOLO positivos. Los negative styles se
# concatenan automáticamente desde NEGATIVE_GLOBAL_STYLES por el helper
# build_music_prompt(). NO mezclar negativos acá ("no drums") — generan ruido.
#
# Calibrados para MISTERIO_ABISAL (dark documental). Si en chat futuro se
# activa un profile distinto (TRUE_CRIME_TERROR, SABIDURIA_ESTOICA), estos
# prompts pueden necesitar ajustes. Por ahora MISTERIO_ABISAL es el único
# profile activo (audio_config.ACTIVE_AUDIO_PROFILE).

MUSIC_PROMPTS: dict[str, str] = {
    "hook": (
        "Dark cinematic underscore in D minor. A low sustained cello drone with "
        "bright glockenspiel notes ringing clearly high above in a tense, insistent "
        "pulse, creating a sense of imminence and pulling the listener in from the "
        "very first second. Present and gripping, not slow or contemplative. Designed "
        "for seamless background looping under documentary narration. 85 BPM, dark and "
        "urgent, consistent intensity throughout."
    ),
    "setup": (
        "Slow cinematic underscore in D minor. A patient low cello drone with sparse, "
        "distant glockenspiel notes ringing high above at long intervals, clearly "
        "audible against the dark bed. Dark mystery atmosphere with quiet ominous "
        "tension and a sense of space. Designed for seamless background looping under "
        "documentary narration. 65 BPM, brooding and spacious, consistent dark depth "
        "throughout."
    ),
    "rising_tension": (
        "Building cinematic underscore in G sharp minor. A low sustained cello drone "
        "beneath high tremolo strings in viola and violin that slowly rise and "
        "intensify, clearly audible up high, mounting unease that pushes forward and "
        "refuses to settle. Designed for seamless background looping under documentary "
        "narration. 78 BPM, dark and steadily tightening, consistent intensity "
        "throughout."
    ),
    "shock": (
        "Dramatic cinematic underscore in F sharp minor. A heavy low cello drone "
        "holding the foundation, with dissonant tension lifted high into glassy, "
        "screeching violin harmonics ringing far above the voice, shimmering and "
        "unsettling. The low end is dark and weighted, the midrange left open and "
        "uncluttered. Designed for seamless background looping under documentary "
        "narration. 80 BPM, dark and ominous, consistent intensity throughout."
    ),
    "consequences": (
        "Heavy cinematic underscore in D minor. A deep low cello drone with slow, "
        "spaced glockenspiel notes ringing high above, sparse and weighted, carrying a "
        "sense of crushing gravity and loss. Clearly audible high notes against the "
        "dark bed. Designed for seamless background looping under documentary "
        "narration. 60 BPM, brooding and heavy, consistent dark depth throughout."
    ),
    "resolution": (
        "Lingering cinematic underscore in D minor. A low sustained cello drone under "
        "high sustained string harmonics that hang unresolved, shimmering and clearly "
        "audible above, an open question that never fully releases. Designed for "
        "seamless background looping under documentary narration. 62 BPM, brooding and "
        "suspended, consistent quiet tension throughout."
    ),
    "outro": (
        "Fading cinematic underscore in D minor. Sustained low cello receding into the "
        "distance, with a slow descending harp glissando shimmering high above. Dark "
        "mystery atmosphere with lingering unease that refuses to resolve. Designed for "
        "seamless background looping under documentary narration. 60 BPM, brooding and "
        "haunting, consistent dark throughout."
    ),
}


# ═══════════════════════════════════════════════════════════════
#  NEGATIVE GLOBAL STYLES — se concatenan a todos los prompts
# ═══════════════════════════════════════════════════════════════
#
# Lista única de estilos que NUNCA deben aparecer en ningún track del canal.
# El helper build_music_prompt() los appenda al final del prompt como bloque
# "STRICTLY AVOID: ...". ElevenLabs Music los procesa internamente como
# negative_global_styles del composition_plan.

NEGATIVE_GLOBAL_STYLES: list[str] = [
    # Voces
    "vocals", "lyrics", "singing", "choir", "spoken word",
    # Percusión
    "drums", "percussion", "drum beat", "rhythm patterns",
    "kick drum", "snare", "hi-hat",
    # Melodías memorables (compiten con narración)
    "melody hooks", "memorable melodies", "vocal-like leads",
    # Estructuras pop/EDM (no encajan documental)
    "pop structure", "EDM", "synthwave", "dubstep", "trap",
    "verse chorus structure",
    # Sonidos disruptivos
    "electric guitar", "distortion", "harsh synths",
    # Transiciones que rompen loop
    "intro fade-in", "outro fade-out", "abrupt ending",
    "sudden silence", "build-up drops",
    # Emociones que no encajan dark documental
    "upbeat", "happy", "energetic dance", "playful",
]


# ═══════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════

def build_music_prompt(intent: str) -> str:
    """Construye el prompt final para ElevenLabs Music combinando el prompt
    positivo del intent + los negative styles globales.

    Args:
        intent: uno de los 7 narrative_intents del catálogo m01a.

    Returns:
        String del estilo:
            "<prompt positivo del intent>. STRICTLY AVOID: <neg1>, <neg2>..."

    Raises:
        MusicConfigError si intent no está en MUSIC_PROMPTS.
    """
    if intent not in MUSIC_PROMPTS:
        raise MusicConfigError(
            f"Unknown intent for music: {intent!r}. "
            f"Valid intents: {sorted(MUSIC_PROMPTS.keys())}"
        )
    base = MUSIC_PROMPTS[intent].rstrip(".")
    negatives = ", ".join(NEGATIVE_GLOBAL_STYLES)
    return f"{base}. STRICTLY AVOID: {negatives}."


def validate_music_config() -> None:
    """Valida que MUSIC_PROMPTS esté completo y curado antes de gastar plata.

    m07_music_director debe llamarla al inicio (antes de cualquier request a
    ElevenLabs). Si raisa, m07 aborta sin gastar créditos.

    Raises:
        MusicConfigError si:
        - Falta algún intent del catálogo de 7
        - Algún prompt es placeholder ("...", "", None)
        - Algún prompt es demasiado corto (<80 chars sugiere placeholder)
        - NEGATIVE_GLOBAL_STYLES está vacío o tiene menos de 5 items
    """
    expected_intents = {
        "hook", "setup", "rising_tension", "shock",
        "consequences", "resolution", "outro",
    }
    missing = expected_intents - set(MUSIC_PROMPTS.keys())
    if missing:
        raise MusicConfigError(
            f"MUSIC_PROMPTS missing intents: {sorted(missing)}. "
            f"Las 7 entries deben estar todas presentes."
        )

    extra = set(MUSIC_PROMPTS.keys()) - expected_intents
    if extra:
        raise MusicConfigError(
            f"MUSIC_PROMPTS contains unknown intents: {sorted(extra)}. "
            f"Solo se permiten los 7 del catálogo: {sorted(expected_intents)}"
        )

    placeholders: list[str] = []
    for intent, prompt in MUSIC_PROMPTS.items():
        if not prompt:
            placeholders.append(f"{intent} (empty/None)")
            continue
        stripped = prompt.strip()
        if stripped in ("", "...", "..."):
            placeholders.append(f"{intent} (placeholder)")
            continue
        if len(stripped) < 80:
            placeholders.append(
                f"{intent} (too short: {len(stripped)} chars, "
                f"likely placeholder)"
            )

    if placeholders:
        raise MusicConfigError(
            f"MUSIC_PROMPTS contains incomplete prompts: {placeholders}. "
            f"All 7 prompts must be curated (>=80 chars) before use."
        )

    if not NEGATIVE_GLOBAL_STYLES or len(NEGATIVE_GLOBAL_STYLES) < 5:
        raise MusicConfigError(
            f"NEGATIVE_GLOBAL_STYLES debe tener al menos 5 items "
            f"(actual: {len(NEGATIVE_GLOBAL_STYLES)})"
        )
