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
    "dev_words": 250,              # caps 2–6, cada uno (§9.1; el §8 decía 240 y sumaba 1,440)
    "outro_words": 140,            # cap 7 (§9.1; antes 130)
    "hook_cap_seconds": 45,
    "dev_cap_seconds": 105,        # antes 75
    "outro_cap_seconds": 45,
    "max_images_per_video": 90,    # el tope no es por costo: es el tiempo de QA de Omar
    # F8 §2: escaleta con ≥ 2 beats por cap de desarrollo (caps 2–6) → 1 + 2 × 5 + 1 = 12 como mínimo; el tope de 12
    # del handoff («10–12») deja exactamente 12 (DECISIONES_F8 D2)
    "min_beats": 7,
    "max_beats": 12,
    "min_beats_dev_cap": 2,
    # F7d (§9.2): compuerta del pool (researcher_steps/pool_gate.py)
    "gate_datos": 150,
    "gate_citas_verificadas": 8,
    "gate_elegibles": 2,
    "gate_eventos_fecha": 10,
    "gate_yellow_pct": 50,         # amarillo: todo ≥ la mitad de cada umbral
    "gate_yellow_target_words": 1200,
    "gate_yellow_max_beats": 8,
    "gate_yellow_min_beats_dev_cap": 1,  # amarillo: 7–8 beats no alcanzan para 2 por cap de desarrollo
}


def get(name: str) -> int:
    try:
        from config import long_video
    except Exception:  # noqa: BLE001 — sin config.py (tests en otra máquina): los defaults
        return DEFAULTS[name]
    return int(getattr(long_video, name, DEFAULTS[name]))
