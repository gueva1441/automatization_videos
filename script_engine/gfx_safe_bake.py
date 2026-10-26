"""
script_engine/gfx_safe_bake.py — F30 §A: el movimiento seguro («safe») lo hace ffmpeg, no el navegador.

Hoy una escena safe (router anti-deformación o forma de la identidad: acercar / paneo / quieta / alejar) la dibuja
HyperFrames con el PNG encima del clip DepthFlow durante TODA la escena, y por eso la escena entera pasaba por el
navegador (gfx_sparse.event_windows). Acá cada escena safe se genera desde su PNG con el MISMO movimiento que gsap y
reemplaza su tramo en el base (`public/base_cocido.mp4`, mismo fps/tamaño/GOP que el re-encode -g30):
    push    escala 1 → S (S = gfx_rules.safe_push_scale) con sine.inOut, z(k) = 1 + (S−1)·(0.5 − 0.5·cos(π·k/N)),
            origen = `safe.origin` (rostro) o el centro
    pull    escala S → 1, sine.inOut, centro
    pan     escala 1.04 y translateX lineal de −dx/2 a +dx/2 (dx = safe_pan_frac·ancho), centro
    static  la foto quieta
con N = duración de la escena × fps (la misma progresión que el timeline de gsap). El cuadro de salida muestra el
rectángulo del PNG que empieza en x0 = ox·W − (ox·W + tx)/z, y0 = oy·H − oy·H/z, de W/z × H/z: ffmpeg `perspective`
(eval=frame, interpolación lineal, precisión de 1/256 px, hilos por franjas) lo lleva al cuadro.
Medido en ch06 contra el render de HF: `zoompan` (el handoff) recorta en píxeles ENTEROS → SSIM 0.77–0.83 con el PNG a
2560×1440·1.08; con el PNG ×6 llega a 0.97 pero lee ~166 MB por cuadro y en paralelo se ahoga (347 ms/cuadro);
`perspective` da 0.976 a ~24 ms/cuadro (una afín subpíxel exacta da 0.98: lo que queda es la captura JPEG de HF).
"""
from __future__ import annotations

import subprocess
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from gfx_config import gfx_render, gfx_rules


def frames_of(s: Any, fps: int) -> tuple[int, int]:
    """Cuadros [k0, k1) de una escena (los cortes ya están en la grilla de cuadros: snap_cuts)."""
    return round(float(s.start) * fps), round(float(s.end) * fps)


def expresiones(movement: str, dur: float, origin: list[float] | tuple[float, float] | None, *, width: int,
                height: int, fps: int) -> tuple[str, str, str]:
    """(z, x0, y0) por cuadro (`in` = cuadro de la escena desde 0): escala de gsap y esquina superior izquierda, en
    píxeles del PNG, del rectángulo visible (W/z × H/z)."""
    S = float(gfx_rules.safe_push_scale)
    D = max(1e-6, float(dur) * fps)
    ox, oy = (float(origin[0]), float(origin[1])) if origin and movement == "push" else (0.5, 0.5)
    tx = "0"
    if movement == "push":
        z = f"(1+{S - 1:.6f}*(0.5-0.5*cos(PI*in/{D:.6f})))"
    elif movement == "pull":
        z = f"({S:.6f}-{S - 1:.6f}*(0.5-0.5*cos(PI*in/{D:.6f})))"
    elif movement == "pan":
        dx = float(gfx_rules.safe_pan_frac) * width
        z = "1.04"
        tx = f"({-dx / 2:.6f}+{dx:.6f}*in/{D:.6f})"
    else:                                                   # static
        z = "1"
    x0 = f"({ox * width:.6f}-({ox * width:.6f}+{tx})/{z})"
    y0 = f"({oy * height:.6f}-{oy * height:.6f}/{z})"
    return z, x0, y0


def bake_scene(img: Path, movement: str, origin: Any, dur: float, n: int, out: Path, *, width: int, height: int,
               fps: int) -> float:
    """El tramo de una escena desde su PNG: exactamente n cuadros. Devuelve los segundos que tardó."""
    z, x0, y0 = expresiones(movement, dur, origin, width=width, height=height, fps=fps)
    x1, y2 = f"({x0}+{width}/{z})", f"({y0}+{height}/{z})"
    vf = (f"scale={width}:{height}:force_original_aspect_ratio=increase:flags=bilinear,crop={width}:{height},"
          f"format=yuv420p,setsar=1")
    if movement != "static":
        vf += (f",perspective=x0='{x0}':y0='{y0}':x1='{x1}':y1='{y0}':x2='{x0}':y2='{y2}':x3='{x1}':y3='{y2}':"
               f"interpolation=linear:sense=source:eval=frame")
    t0 = time.time()
    r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-framerate", str(fps), "-i", str(img), "-vf", vf,
                        "-frames:v", str(n), "-an", "-c:v", "libx264", "-preset", gfx_render.reencode_preset,
                        "-crf", str(gfx_render.reencode_crf), "-r", str(fps), "-g", str(gfx_render.reencode_gop),
                        "-keyint_min", str(gfx_render.reencode_gop), "-pix_fmt", "yuv420p", str(out)],
                       capture_output=True, text=True, timeout=1800)
    if r.returncode != 0 or not out.exists():
        raise RuntimeError(f"bake de {img.name} ({movement}) falló: {r.stderr[-300:]}")
    return time.time() - t0


def n_frames(video: Path) -> int:
    """Cuadros del video (el `nb_frames` del contenedor mp4)."""
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=nb_frames",
                        "-of", "csv=p=0", str(video)], capture_output=True, text=True, timeout=120)
    return int(r.stdout.strip().split(",")[0])


def plan_bake(scenes: list[Any], fps: int) -> list[dict[str, Any]]:
    """Las escenas a cocer: safe con imagen en disco, con sus cuadros."""
    out = []
    for s in scenes:
        sv = getattr(s, "safe", None)
        if not sv or not Path(sv.get("image", "")).exists():
            continue
        k0, k1 = frames_of(s, fps)
        if k1 - k0 < 2:
            continue
        out.append({"idx": s.idx, "k0": k0, "k1": k1, "n": k1 - k0, "dur": float(s.end) - float(s.start),
                    "movement": sv.get("movement") or "push", "origin": sv.get("origin"), "image": sv["image"],
                    "risk": sv.get("risk")})
    return out


def concat_graph(pieces: list[tuple[str, int, int]]) -> str:
    """filter_complex que arma el base cocido: («base», k0, k1) → trim del base por cuadros; («safe», i, n) → el clip i."""
    parts, labels = [], []
    for j, (src, a, b) in enumerate(pieces):
        if src == "base":
            parts.append(f"[0:v]trim=start_frame={a}:end_frame={b},setpts=PTS-STARTPTS[p{j}]")
        else:
            parts.append(f"[{a}:v]setpts=PTS-STARTPTS[p{j}]")
        labels.append(f"[p{j}]")
    return ";".join(parts + ["".join(labels) + f"concat=n={len(pieces)}:v=1:a=0[o]"])


def bake(base: Path, scenes: list[Any], out: Path, *, width: int, height: int, fps: int, workers: int | None = None,
         log: list[str] | None = None) -> dict[str, Any] | None:
    """Base cocido: las escenas safe desde su PNG, el resto del base tal cual. None si no hay escenas safe."""
    todo = plan_bake(scenes, fps)
    if not todo:
        return None
    tmp = out.parent / f"_{out.stem}"
    tmp.mkdir(parents=True, exist_ok=True)
    t0 = time.time()

    def one(x: dict[str, Any]) -> float:
        x["clip"] = tmp / f"safe_s{x['idx']:02d}.mp4"
        return bake_scene(Path(x["image"]), x["movement"], x["origin"], x["dur"], x["n"], x["clip"], width=width,
                          height=height, fps=fps)
    with ThreadPoolExecutor(max_workers=workers or gfx_rules.safe_bake_workers) as ex:
        secs = list(ex.map(one, todo))
    t_scenes = time.time() - t0
    total = n_frames(base)
    pieces: list[tuple[str, int, int]] = []
    k, inputs = 0, [str(base)]
    for x in sorted(todo, key=lambda x: x["k0"]):
        if x["k0"] > k:
            pieces.append(("base", k, x["k0"]))
        inputs.append(str(x["clip"]))
        pieces.append(("safe", len(inputs) - 1, x["n"]))
        k = x["k1"]
    if k < total:
        pieces.append(("base", k, total))
    cmd = ["ffmpeg", "-v", "error", "-y"]
    for i in inputs:
        cmd += ["-i", i]
    cmd += ["-filter_complex", concat_graph(pieces), "-map", "[o]", "-frames:v", str(total), "-an", "-c:v", "libx264",
            "-preset", gfx_render.reencode_preset, "-crf", str(gfx_render.reencode_crf), "-r", str(fps),
            "-g", str(gfx_render.reencode_gop), "-keyint_min", str(gfx_render.reencode_gop), "-pix_fmt", "yuv420p",
            "-movflags", "+faststart", str(out)]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
    if r.returncode != 0 or not out.exists():
        raise RuntimeError(f"base cocido falló: {r.stderr[-400:]}")
    for x in todo:
        Path(x["clip"]).unlink(missing_ok=True)
    tmp.rmdir()
    rep = {"escenas": [{k: x[k] for k in ("idx", "movement", "origin", "n", "risk")} for x in todo],
           "cuadros_cocidos": sum(x["n"] for x in todo), "cuadros_total": total, "filtro": "perspective",
           "segundos_escenas": round(t_scenes, 1), "segundos_por_escena": [round(s, 1) for s in secs],
           "segundos_total": round(time.time() - t0, 1)}
    if log is not None:
        log.append(f"  safe bake: {len(todo)} escena(s) {[(x['idx'], x['movement']) for x in todo]} · "
                   f"{rep['cuadros_cocidos']}/{total} cuadros · {rep['segundos_total']:.1f}s")
    return rep
