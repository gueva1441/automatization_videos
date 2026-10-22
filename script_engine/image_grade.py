"""
script_engine/image_grade.py — F8b §2.6: grade de post sobre cada imagen generada (cualquier motor), antes de
DepthFlow/Ken Burns. Arregla el «limpias y saturadas» sin más texto en el prompt.

    desaturación   15–25 %                        (`saturation` 0.72: medida en HSV baja ~18 %)
    negros         levantados (lift)              (`lift` 0.035: el negro puro pasa a ~9/255)
    viñeta         leve                           (`vignette_angle` 0.35 rad)
    grano          fino, fijo por imagen          (`grain` 6, semilla = hash del nombre: re-grade idéntico)
    temperatura    ligeramente fría               (`cool` 0.03: menos rojo, más azul en medios y luces)

Parámetros: DEFAULTS de acá; el perfil del canal los pisa con una clave `image_grade` ({...}) en
gfx_profiles/<perfil>.json (solo lectura: este módulo no escribe el perfil). Salida `<stem>_graded.png` al lado del
original, que se conserva.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

DEFAULTS: dict[str, Any] = {
    "enabled": True,
    "saturation": 0.70,
    "lift": 0.035,
    "vignette_angle": 0.35,
    "grain": 6,
    "cool": 0.02,
}
SUFFIX = "_graded"


def params(profile: str = "misterio") -> dict[str, Any]:
    """DEFAULTS pisados por `image_grade` del perfil del canal, si lo tiene."""
    p = dict(DEFAULTS)
    f = Path(__file__).resolve().parents[1] / "gfx_profiles" / f"{profile}.json"
    try:
        over = json.loads(f.read_text(encoding="utf-8")).get("image_grade") or {}
    except (OSError, ValueError):
        over = {}
    p.update({k: v for k, v in over.items() if k in DEFAULTS})
    return p


def filter_chain(p: dict[str, Any], seed: int) -> str:
    lift = float(p["lift"])
    cool = float(p["cool"])
    return ",".join([
        f"colorbalance=rm={-cool:.3f}:bm={cool:.3f}:rh={-cool / 2:.3f}:bh={cool / 2:.3f}",   # frío en medios y luces
        f"eq=saturation={float(p['saturation']):.3f}",   # después del tinte: desatura también lo que agrega
        f"vignette=angle={float(p['vignette_angle']):.3f}",
        f"colorlevels=romin={lift:.3f}:gomin={lift:.3f}:bomin={lift + 0.01:.3f}",   # lift al final: la viñeta no recorta
        "format=yuv444p",                              # grano solo en luma: sin croma nuevo en las sombras
        f"noise=c0s={int(p['grain'])}:c0f=u:c0_seed={seed}",
        "format=rgb24",
    ])


def graded_path(src: Path) -> Path:
    return src.with_name(f"{src.stem}{SUFFIX}{src.suffix}")


def grade(src: Path, p: dict[str, Any] | None = None, *, dst: Path | None = None, overwrite: bool = False) -> Path:
    """Aplica el grade a `src` → `dst` (default `<stem>_graded.png`). Devuelve `dst`. El original no se toca."""
    p = p or params()
    dst = dst or graded_path(src)
    if dst.exists() and not overwrite:
        return dst
    seed = int(hashlib.sha1(src.name.encode("utf-8")).hexdigest()[:6], 16)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", str(src), "-vf", filter_chain(p, seed), "-frames:v", "1",
           str(dst)]
    subprocess.run(cmd, check=True, capture_output=True)
    return dst


def stats(path: Path) -> dict[str, float]:
    """Saturación media (HSV, 0–1), luminancia mínima y % de píxeles negros puros (luma ≤ 2): el test del grade."""
    from PIL import Image
    im = Image.open(path).convert("RGB")
    im.thumbnail((640, 640))
    hsv = im.convert("HSV")
    luma = list(im.convert("L").getdata())
    # la saturación HSV de un píxel casi negro es ruido: se mide sobre los que tienen luma > 24
    s = [sv for sv, lv in zip(hsv.getdata(band=1), luma) if lv > 24] or [0]
    return {"sat_media": sum(s) / len(s) / 255, "luma_min": min(luma),
            "negro_puro_pct": 100 * sum(1 for v in luma if v <= 2) / len(luma),
            "luma_media": sum(luma) / len(luma)}
