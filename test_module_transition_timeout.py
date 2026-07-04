"""test_module_transition_timeout.py — timeout del concat proporcional a la duración.

Cubre (HANDOFF_135f §2) la función pura `_concat_timeout`: piso 900 en videos
cortos, 5× realtime en largos, y 900 ante duración 0/negativa. Añade cobertura del
helper genérico `_scaled_timeout` (pisos distintos para los hermanos 234/277).

Corre con pytest o directo:  python test_module_transition_timeout.py
"""
from __future__ import annotations

import os
import sys

# transition_applier resuelve sus imports (transition_config, …) con script_engine
# en sys.path — replicarlo para importar el módulo tal como corre en producción.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "script_engine"))

from transition_applier import _concat_timeout, _scaled_timeout


def test_concat_timeout_video_corto_usa_piso():
    """60s → piso 900 (5×=300 < 900)."""
    assert _concat_timeout(60) == 900


def test_concat_timeout_video_largo_escala_5x():
    """687s (el caso ba6c3cac que murió a 900) → 3435."""
    assert _concat_timeout(687) == 3435


def test_concat_timeout_cero_devuelve_piso():
    assert _concat_timeout(0) == 900


def test_concat_timeout_negativo_devuelve_piso():
    assert _concat_timeout(-5) == 900


def test_concat_timeout_none_devuelve_piso():
    assert _concat_timeout(None) == 900


def test_concat_timeout_frontera_exacta():
    """180s → 5×=900 == piso; no debe bajar del piso."""
    assert _concat_timeout(180) == 900
    assert _concat_timeout(181) == 905


def test_scaled_timeout_respeta_piso_hermano_300():
    """Piso del hermano de 1 segmento (línea 277)."""
    assert _scaled_timeout(30, 300) == 300      # 5×=150 < 300
    assert _scaled_timeout(100, 300) == 500     # 5×=500 > 300


def test_scaled_timeout_respeta_piso_hermano_600():
    """Piso del hermano concat demuxer fallback (línea 234)."""
    assert _scaled_timeout(60, 600) == 600      # 5×=300 < 600
    assert _scaled_timeout(687, 600) == 3435    # video largo escala igual


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print(f"  ok  {fn.__name__}")
    print(f"\n{len(fns)} tests OK")
