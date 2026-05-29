"""
audio_config.py — El Interruptor Maestro de Sonido.
Aquí es donde el usuario (Perrín) elige el feeling del video.
"""
from audio_profiles import AUDIO_PROFILES

# Solo cambia este nombre para cambiar toda la psicología del audio
ACTIVE_AUDIO_PROFILE = "MISTERIO_ABISAL"

# Esta es la variable que el audio_manager.py consultará
AUDIO_STYLE = AUDIO_PROFILES.get(ACTIVE_AUDIO_PROFILE, AUDIO_PROFILES["MISTERIO_ABISAL"])