"""
audio_profiles.py — Librería de Presets de Audio para "Ruta de Valor"

Cada perfil incluye:
  - voice_id: ID de voz confirmado en la cuenta de ElevenLabs
  - voice_settings: parámetros de inferencia para ElevenLabs
  - mixing: parámetros para el video_assembler (duck, volúmenes)
  - music_prompt: prompt para generar la música de fondo del perfil
"""

AUDIO_PROFILES: dict[str, dict] = {
    "MISTERIO_ABISAL": {
        "description": "Voz pausada y profunda. Ideal para temas tipo El Bloop.",
        "voice_id": "pqHfZKP75CvOlQylNhV4",  # Bill
        "voice_settings": {
            "stability": 0.45,
            "similarity_boost": 0.8,
            "style": 0.6,
            "use_speaker_boost": True,
        },
        "mixing": {
            "music_volume": 0.26,
            "music_volume_floor": 0.16,   # chat 32 tune: bajado proporcional a music_volume para mantener relación
            "sfx_volume": 1.2,
            "duck_threshold": 0.03,
            "duck_ratio": 5,
            "duck_attack_ms": 80,
            "duck_release_ms": 200,
        },
        "music_prompt": (
            "Dark cinematic ambient, deep sub-bass, mysterious documentary "
            "underscore, no drums."
        ),
    },
    "SABIDURIA_ESTOICA": {
        "description": "Voz de autoridad, lenta y pesada. Para temas de historia o filosofía.",
        "voice_id": "JBFqnCBsd6RMkjVDRZzb",  # George
        "voice_settings": {
            "stability": 0.8,
            "similarity_boost": 0.9,
            "style": 0.3,
            "use_speaker_boost": True,
        },
        "mixing": {
            "music_volume": 0.18,
            "sfx_volume": 0.9,
            "duck_ratio": 7,
            "duck_release_ms": 400,
        },
        "music_prompt": (
            "Epic cinematic strings, slow cello melodies, profound and atmospheric."
        ),
    },
    "TRUE_CRIME_TERROR": {
        "description": "Voz inestable y tensa. Genera ansiedad y urgencia.",
        "voice_id": "onwK4e9ZLuTAKqWW03F9",  # Daniel
        "voice_settings": {
            "stability": 0.35,
            "similarity_boost": 0.75,
            "style": 0.85,
            "use_speaker_boost": True,
        },
        "mixing": {
            "music_volume": 0.20,
            "sfx_volume": 1.5,
            "duck_ratio": 12,
            "duck_release_ms": 600,
        },
        "music_prompt": (
            "Eerie suspenseful drone, dissonant pads, horror atmosphere, "
            "subtle heartbeats."
        ),
    },
}


# ═══════════════════════════════════════════════════════════════
#  VOICE SETTINGS POR NARRATIVE_INTENT (PR 2.A chat 24)
# ═══════════════════════════════════════════════════════════════
#
# D-A1 (chat 24): el override solo toca stability + style. El profile activo
# (MISTERIO_ABISAL, TRUE_CRIME_TERROR, SABIDURIA_ESTOICA) sigue definiendo
# similarity_boost y use_speaker_boost — eso es la identidad sonora del canal
# y no cambia entre caps.
#
# audio_manager.process_script() hace el merge: voice_settings_base del
# profile + override del intent del cap. Si el intent es desconocido o no
# está presente → fallback al profile activo sin override (compat SHORT y
# LONG sin gate).

VOICE_SETTINGS_BY_INTENT: dict[str, dict] = {
    "hook":           {"stability": 0.50, "style": 0.40},  # subí
    "setup":          {"stability": 0.65, "style": 0.40},  # igual
    "rising_tension": {"stability": 0.55, "style": 0.50},  # subí stability, bajé style
    "shock":          {"stability": 0.45, "style": 0.55},  # subí mucho stability, bajé mucho style
    "consequences":   {"stability": 0.60, "style": 0.45},  # subí ambos
    "resolution":     {"stability": 0.70, "style": 0.35},  # igual
    "outro":          {"stability": 0.75, "style": 0.30},  # igual
}