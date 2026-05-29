"""
art_config.py — Parámetros técnicos del renderizado Leonardo.

Separa los knobs de API (modelo, tamaño, contraste, estilo UUID)
del ADN visual (keywords) y del código del motor.

Editar aquí cuando quieras subir/bajar contraste, cambiar el style UUID,
o apuntar a otro modelId, SIN tocar asset_manager.py.
"""
from __future__ import annotations

from typing import Any

from config import api, pipeline


# Payload base para POST /generations de Leonardo.
# Se consume con  payload = {"prompt": ..., "negative_prompt": ..., **LEONARDO_SETTINGS}
LEONARDO_SETTINGS: dict[str, Any] = {
    "modelId":    api.leonardo_model_id,          # Lucid Realism (05ce0082-...)
    "width":      pipeline.image_width,           # 720
    "height":     pipeline.image_height,          # 1280 (9:16)
    "num_images": 1,
    "contrast":   3.5,
    "styleUUID":  "a5632c7c-ddbb-4e2f-ba34-8456ab3ac436",  # Cinematic
}
