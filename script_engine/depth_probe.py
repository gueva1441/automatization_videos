"""
depth_probe.py — Pre-filtro geométrico del gate de zoom v3 (Camino B, chat 55).

Mide el depth map REAL de cada PNG con DepthAnythingV2 (el MISMO estimador que
DepthFlow usa para renderizar) y expone la métrica `center_minus_border` (c-b),
que separa "sujeto cercano centrado vs entorno que recede". Es el pre-filtro
determinístico antes del juez de visión (zoom_judge): geometría barata primero,
visión semántica solo sobre las candidatas.

Validado en el lab chat 55 (BLOQUE 1): c-b es la métrica que ordena los sujetos;
spread/std miden varianza global y no discriminan. Umbral c-b ≥ 0.15.

Costo doble ≈ 0: el constructor DEFAULT de DepthAnythingV2 comparte el DiskCache
con el render, así que si el probe corre antes, el render pega en caché. Se setea
DEPTHMAP_CACHE_SIZE_MB=500 para que mapas grandes no disparen evictions.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from flow_config import flow_render

# ═══════════════════════════════════════════════════════════════
#  CONSTANTES DEL GATE (valores del lab chat 55, NO hardcodear inline)
# ═══════════════════════════════════════════════════════════════

DEPTH_ZOOM_CB_MIN: float = 0.15      # c-b mínimo para ser CANDIDATA a zoom (pre-filtro)
MAX_ZOOMS_PER_CHAPTER: int = 7       # HANDOFF_140b (C4): 2→7. El juez de visión ya
                                     # evaluó las candidatas; subir el tope solo deja
                                     # promover más de las YA aprobadas (no gatilla
                                     # más visión). DEPTH_ZOOM_CB_MIN NO se toca.


# ═══════════════════════════════════════════════════════════════
#  RUNNER (corre dentro de .venv-depthflow vía python -c)
# ═══════════════════════════════════════════════════════════════
# Mantener acá (no en .py separado) para versionarlo junto al caller.
# Recibe params vía argv[1] JSON; escribe métricas a un JSON de salida.

_PROBE_RUNNER = r"""
import os, json, sys
# Caché grande ANTES de importar broken (size_limit default 50MB → evictions en videos largos)
os.environ.setdefault("DEPTHMAP_CACHE_SIZE_MB", "500")
os.environ.setdefault("TORCH_DEVICE", "cuda")
os.environ.setdefault("CUDA_VISIBLE_DEVICES", "0")

import numpy as np
from broken.externals.depthmap import DepthAnythingV2

params = json.loads(sys.argv[1])
est = DepthAnythingV2()   # constructor DEFAULT — mismo hash que usa el render → comparte caché

rows = {}
for p in params["image_paths"]:
    name = os.path.splitext(os.path.basename(p))[0]
    d = np.asarray(est.estimate(p), dtype=np.float32)
    if d.ndim == 3:
        d = d[..., 0]
    h, w = d.shape
    cy0, cy1 = int(h*0.25), int(h*0.75)
    cx0, cx1 = int(w*0.25), int(w*0.75)
    center = d[cy0:cy1, cx0:cx1]
    border = d.copy(); border[cy0:cy1, cx0:cx1] = np.nan
    p10 = float(np.percentile(d, 10)); p50 = float(np.percentile(d, 50)); p90 = float(np.percentile(d, 90))
    rows[name] = {
        "p10": p10, "p50": p50, "p90": p90,
        "spread": p90 - p10,
        "center_minus_border": float(np.mean(center) - np.nanmean(border)),
        "std": float(d.std()),
    }

with open(params["out_path"], "w", encoding="utf-8") as f:
    json.dump(rows, f)
print(f"[depth_probe] {len(rows)} imagenes medidas", file=sys.stderr)
"""


def _resolve_python_bin() -> str:
    venv = flow_render.venv_depthflow
    py = venv / "Scripts" / "python.exe"
    if not py.exists():
        py = venv / "bin" / "python"
    if not py.exists():
        raise RuntimeError(f"No encontré python en el venv DepthFlow: {venv}")
    return str(py)


# ═══════════════════════════════════════════════════════════════
#  API PÚBLICA
# ═══════════════════════════════════════════════════════════════

def gate_zoom(metrics: dict[str, Any]) -> bool:
    """Pre-filtro geométrico puro y testeable: ¿la imagen es CANDIDATA a zoom?

    True si center_minus_border ≥ DEPTH_ZOOM_CB_MIN (sujeto cercano centrado con
    fondo que recede). NO decide la promoción final — eso lo cierra zoom_judge
    (visión) + el tope por capítulo.
    """
    try:
        return float(metrics["center_minus_border"]) >= DEPTH_ZOOM_CB_MIN
    except (KeyError, TypeError, ValueError):
        return False


def rank_promotions(scored: list[tuple[str, float]],
                    max_per_cap: int = MAX_ZOOMS_PER_CHAPTER) -> list[str]:
    """Dado [(nombre, c-b)] de las candidatas de UN cap que ya pasaron visión,
    devuelve los nombres a promover: top-`max_per_cap` por c-b DESCENDENTE.
    Puro y testeable (encapsula 'tope por cap' + 'orden por c-b')."""
    return [name for name, _ in sorted(scored, key=lambda t: t[1], reverse=True)[:max_per_cap]]


def probe_images(image_paths: list[Path], cache_path: Path,
                 timeout: int = 1800) -> dict[str, dict[str, Any]]:
    """Mide el depth map de cada PNG y devuelve {nombre_sin_ext: metrics}.

    Persiste/lee `cache_path` (depth_metrics.json en el dir de assets). Si el caché
    existe y CUBRE todos los nombres pedidos, no re-corre (re-animaciones gratis).
    Si falta alguno, re-mide todo el batch (un solo subprocess, el modelo carga 1 vez).
    """
    names = [p.stem for p in image_paths]

    if cache_path.exists():
        try:
            cached = json.loads(cache_path.read_text(encoding="utf-8"))
            if all(n in cached for n in names):
                return {n: cached[n] for n in names}
        except (json.JSONDecodeError, OSError):
            pass  # caché corrupto → re-medir

    cache_path.parent.mkdir(parents=True, exist_ok=True)
    out_tmp = cache_path.parent / "_depth_metrics_probe.json"
    params = {
        "image_paths": [str(p.resolve()) for p in image_paths],
        "out_path": str(out_tmp.resolve()),
    }
    import os as _os
    env = _os.environ.copy()
    env["DEPTHMAP_CACHE_SIZE_MB"] = "500"
    env["TORCH_DEVICE"] = "cuda"
    env["CUDA_VISIBLE_DEVICES"] = "0"

    result = subprocess.run(
        [_resolve_python_bin(), "-c", _PROBE_RUNNER, json.dumps(params)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        env=env, timeout=timeout,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"depth_probe runner falló (rc={result.returncode}): {(result.stderr or '')[-500:]}"
        )

    metrics = json.loads(out_tmp.read_text(encoding="utf-8"))
    out_tmp.unlink(missing_ok=True)

    # Merge con el caché previo (si había) y persistir el set acumulado
    merged: dict[str, Any] = {}
    if cache_path.exists():
        try:
            merged = json.loads(cache_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            merged = {}
    merged.update(metrics)
    cache_path.write_text(json.dumps(merged, indent=2, ensure_ascii=False), encoding="utf-8")

    return {n: metrics[n] for n in names if n in metrics}
