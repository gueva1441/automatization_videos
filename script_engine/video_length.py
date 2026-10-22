"""
script_engine/video_length.py — F7c-2 / HANDOFF_F7 §8.2: parámetros de largo del video (Omar, 2026-10-21).

Se leen de `config.long_video` (config.py, fuera de git porque tiene las claves); si un campo no está (otra máquina,
config viejo), vale el default de acá, que es el mismo. 12 min ≈ 1,500 palabras a 2.05 palabras/s (medido en v2 F5d).
Hipótesis de arranque: los ajusta la curva de retención de YouTube Studio.
"""
from __future__ import annotations

DEFAULTS = {
    "target_words": 1500,          # largo objetivo del guion v3
    "max_words": 1700,             # tope duro (≈ 13 min)
    "hook_words": 110,             # cap 1
    "dev_words": 240,              # caps 2–6, cada uno
    "outro_words": 130,            # cap 7
    "hook_cap_seconds": 45,
    "dev_cap_seconds": 105,        # antes 75
    "outro_cap_seconds": 45,
    "max_images_per_video": 90,    # el tope no es por costo: es el tiempo de QA de Omar
}


def get(name: str) -> int:
    try:
        from config import long_video
    except Exception:  # noqa: BLE001 — sin config.py (tests en otra máquina): los defaults
        return DEFAULTS[name]
    return int(getattr(long_video, name, DEFAULTS[name]))
