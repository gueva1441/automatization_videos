"""
nicho_config.py — Identidad visual permanente por nicho (chat 27).

Decisión arquitectónica chat 26: identidad por NICHO, no por video.
HITL se corre una vez por nicho. 50+ videos heredan misma estrategia + ancla.

Para agregar nicho nuevo: correr test_lab_v6.py con narración del nicho,
elegir estrategia + ancla, copiar resultado acá.

Ancla validada en chat 26 con stress test Apolo 13 (cuarto continente)
y chat 27 con stress test Bhopal 1984 (cuarto continente confirmado agnóstico).
"""
from __future__ import annotations
from typing import Any


NICHO_DARK_HISTORY: dict[str, Any] = {
    "nombre": "dark_history",
    "descripcion": "Dark history / mystery documentary, canal Ruta de Valor",
    "validado_chat": 26,
    "stress_tested_chats": [26, 27],  # Apolo 13, Bhopal 1984

    "estrategia": {
        "nombre": "Realismo Oscuro",
        "descripcion": "Estética cruda y granulada del pasado, evocando descubrimiento prohibido (Mindhunter / Chernobyl HBO style)",
        "referencias": "True Detective S1, Zodiac, Se7en, Mindhunter, Chernobyl HBO",
    },

    "ancla_global": (
        "Shot with documentary-style cinematography, gritty digital film "
        "emulation, low-key dramatic lighting, cold desaturated palette, "
        "coarse analog noise texture."
    ),
}


# Mapping de profile activo → nicho. Por ahora hardcoded a dark_history.
# Futuro: se podría leer de config.py ACTIVE_NICHO o similar.
ACTIVE_NICHO = NICHO_DARK_HISTORY


def get_active_nicho() -> dict[str, Any]:
    """Devuelve el dict del nicho activo. Usado por m03 para ensamblaje."""
    return ACTIVE_NICHO
