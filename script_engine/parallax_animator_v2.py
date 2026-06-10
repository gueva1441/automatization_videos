"""
parallax_animator_v2.py — Animador 2.5D con DepthFlow.

Reemplaza:
  - parallax_animator.py     (FFmpeg zoompan FG/BG con artefactos rembg)
  - parallax_processor.py    (rembg con pelos sueltos)
  - test_cinematic_stack.py  (stack manual)

Recibe un FlowSpec YA decidido por flow_director.select_movements_batch()
y ejecuta DepthFlow v0.9.1 contra una imagen base. Subprocess al venv
aislado .venv-depthflow (flow_render.use_subprocess=True por defecto).

Fallback: si DepthFlow falla → Ken Burns 2D puro FFmpeg.
Costos: $0 (CPU local). Registra en cost_tracker para trazabilidad.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Literal

from config import api, pipeline
from cost_tracker import cost_tracker
from error_handler import error_handler, PipelineStage

from flow_config import flow_render
from flow_profiles import FlowSpec


# ═══════════════════════════════════════════════════════════════
#  EXCEPCIONES + EXPORTS
# ═══════════════════════════════════════════════════════════════

class DepthFlowError(RuntimeError):
    """DepthFlow falló por razones técnicas. Caller debe hacer fallback."""


__all__ = [
    "DepthFlowError",
    "build_depthflow_clip",
    "build_kenburns_fallback",
    "build_animated_clip",
    "build_hook_clip",
]


# Tipo: modos posibles de wrap del shader. None = no tocar (default DepthFlow).
TilingMode = Literal["black", "clamp", "mirror", "repeat"] | None


# ═══════════════════════════════════════════════════════════════
#  RUNNER (corre dentro de .venv-depthflow vía python -c)
# ═══════════════════════════════════════════════════════════════
# Mantener este string acá (no en .py separado) para que esté
# versionado junto con el caller. Recibe params vía argv[1] como JSON.

_DEPTHFLOW_RUNNER = r"""
import os, json, sys

# Forzar GPU ANTES de importar torch/depthflow
os.environ.setdefault("TORCH_DEVICE", "cuda")
os.environ.setdefault("CUDA_VISIBLE_DEVICES", "0")

import torch
print(
    f"[depthflow-runner] torch={torch.__version__} "
    f"cuda_available={torch.cuda.is_available()} "
    f"device={torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'}",
    file=sys.stderr,
)

from depthflow.scene import DepthScene

params = json.loads(sys.argv[1])

scene = DepthScene(backend="headless")
scene.input(image=params["image_path"])

# Diagnóstico: qué device está usando el depth estimator
try:
    est_device = scene.config.estimator.device
    print(f"[depthflow-runner] estimator.device={est_device}", file=sys.stderr)
except Exception as e:
    print(f"[depthflow-runner] no pude leer estimator.device: {e}", file=sys.stderr)


# ─── CONFIG V12 (validada empíricamente chat 20) ────────────────
# state.height: default DepthFlow = 0.20, MAL para imágenes complejas con
# bordes filosos (chimeneas, postes contra cielo) — produce texture-stretching.
# Bajar a 0.05 elimina el problema. Validado sobre 10 imágenes Pripyat.
scene.state.height = 0.05
print(f"[v12] scene.state.height = {scene.state.height}", file=sys.stderr)

# state.mirror: default True → shader replica pixels en modo espejo cuando se
# muestra fuera del frame, causa "espejos" visibles en bordes. False elimina.
scene.state.mirror = False
print(f"[v12] scene.state.mirror = False", file=sys.stderr)


# ─── INTROSPECCIÓN tiling/wrap/border (S12) ─────────────────────
# Solo si introspect=True. Loggea cualquier atributo con keywords
# relacionadas con texture wrap, en scene / scene.state / scene.config
# y sus tipos. Con esto sabemos QUÉ API real existe sin adivinar.
if params.get("introspect_tiling", False):
    KEYWORDS = ("til", "wrap", "border", "edge", "clamp", "repeat", "mirror")
    def _scan(obj, label):
        try:
            attrs = dir(obj)
        except Exception as e:
            print(f"[introspect] {label}: dir() falló: {e}", file=sys.stderr)
            return
        for a in attrs:
            if a.startswith("_"):
                continue
            low = a.lower()
            if any(k in low for k in KEYWORDS):
                try:
                    val = getattr(obj, a)
                    typ = type(val).__name__
                    print(f"[introspect] {label}.{a} = {val!r} (type={typ})", file=sys.stderr)
                except Exception as e:
                    print(f"[introspect] {label}.{a} -> error: {e}", file=sys.stderr)
    _scan(scene, "scene")
    try: _scan(scene.state, "scene.state")
    except Exception: pass
    try: _scan(scene.config, "scene.config")
    except Exception: pass
    # También escanear el método de animación
    mv = params["movement"]
    m = getattr(scene, mv, None)
    if m is not None:
        try:
            import inspect
            sig = inspect.signature(m)
            print(f"[introspect] scene.{mv} signature: {sig}", file=sys.stderr)
        except Exception as e:
            print(f"[introspect] sig de {mv} falló: {e}", file=sys.stderr)


# ─── tiling_mode (legacy chat 19) ───────────────────────────────
# DEPRECADO en chat 21: ahora siempre forzamos mirror=False arriba (config v12).
# Este bloque se mantiene por compatibilidad si el caller pasa tiling_mode="mirror"
# explícitamente para casos especiales — sobrescribe el default v12.
tiling = params.get("tiling_mode")
if tiling == "mirror":
    try:
        scene.state.mirror = True
        print(
            f"[tiling] OVERRIDE: scene.state.mirror = True "
            f"(input={tiling!r})",
            file=sys.stderr,
        )
    except Exception as e:
        print(f"[tiling] ERROR aplicando mirror override: {e}", file=sys.stderr)


# Aplicar movimiento (los movimientos son metodos del scene en v0.9.1)
movement = params["movement"]
opts = params["options"]

method = getattr(scene, movement, None)
if method is None:
    print(f"ERROR: movement '{movement}' no existe en DepthScene", file=sys.stderr)
    sys.exit(2)

# Estrategia defensiva: probar todos los kwargs juntos; si falla
# por TypeError (kwarg desconocido), reintentar uno por uno descartando
# los no soportados.
try:
    method(**opts)
except TypeError:
    for k, v in opts.items():
        try:
            method(**{k: v})
        except TypeError:
            print(f"WARN: kwarg '{k}' no soportado por {movement}", file=sys.stderr)

# DOF (componente, no metodo de animacion)
if params.get("dof", False) and hasattr(scene, "dof"):
    try:
        scene.dof.enable = True
    except Exception:
        pass  # DOF es opcional

# Render: TODO via main() kwargs (NO setear scene.width/height/fps/duration
# como atributos porque dispara setters que requieren window inicializada)
scene.main(
    output=params["output_path"],
    render=True,
    width=params["width"],
    height=params["height"],
    fps=params["fps"],
    ssaa=params["ssaa"],
    time=params["duration"],   # API real: el kwarg se llama 'time', no 'duration'
    ratio="9:16",              # forzar aspecto vertical para Shorts
)
print("OK")
"""

# ═══════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════

def _resolve_python_bin() -> str:
    """Path al python.exe del venv DepthFlow aislado (Windows + fallback POSIX)."""
    venv = flow_render.venv_depthflow
    py = venv / "Scripts" / "python.exe"
    if not py.exists():
        py = venv / "bin" / "python"
    if not py.exists():
        raise DepthFlowError(
            f"No encontré python en el venv DepthFlow: {venv}"
        )
    return str(py)


def _resolve_movement_name(movement: str) -> str:
    """
    Mapea nombre de nuestro inventario → método real del scene.
    DepthFlow tiene scene.zoom() unificado; la dirección la da el signo
    de intensity (positivo=zoom_in, negativo=zoom_out).
    """
    if movement in ("zoom_in", "zoom_out"):
        return "zoom"
    return movement


# Chat 32: escala de intensity por duración. DepthFlow corre el ciclo completo
# del movimiento en cualquier duración, así que imágenes cortas se ven aceleradas.
# Reducimos intensity proporcional a la duración respecto del target de m03 (7s),
# con un floor para que el movimiento no muera del todo en imágenes muy cortas.
_DURATION_REFERENCE_S = 7.0
_INTENSITY_FLOOR_FACTOR = 0.45


def _build_options(flow_spec: FlowSpec, duration_seconds: float) -> dict[str, Any]:
    """
    Mapea FlowSpec → kwargs DepthFlow con parámetros específicos por movimiento.
    Replica EXACTO la config v12 que se validó visualmente bien en chat 21.
    isometric/depth son los que pronuncian el efecto — sin ellos los movimientos
    toman defaults conservadores y se ven sutiles.

    Chat 32: si la imagen dura menos que _DURATION_REFERENCE_S, escala intensity
    linealmente (con floor _INTENSITY_FLOOR_FACTOR) para evitar parallax
    acelerado. Imágenes de 7s+ no se tocan.
    """
    movement = flow_spec["movement"]
    intensity = flow_spec["intensity"]
    steady = flow_spec["steady"]

    # Escalar intensity si la imagen es más corta que la referencia.
    # Cap superior: 1.0 (no amplificar imágenes largas). Cap inferior: floor.
    if duration_seconds < _DURATION_REFERENCE_S:
        scale = max(duration_seconds / _DURATION_REFERENCE_S, _INTENSITY_FLOOR_FACTOR)
        intensity = intensity * scale

    # Base común a los 3 movimientos
    opts: dict[str, Any] = {
        "intensity": intensity,
        "loop": True,
        "phase": 0.0,
        "smooth": True,
    }

    # Parámetros específicos por movimiento (réplica EXACTA de v12)
    if movement in ("horizontal", "vertical"):
        opts["steady"] = steady
        opts["isometric"] = 0.6      # ← clave que faltaba: pronuncia el efecto
    elif movement == "orbital":
        opts["depth"] = 0.9           # ← clave que faltaba: pronuncia el efecto
    elif movement in ("zoom_in", "zoom_out"):
        # Camino A (chat 55): el zoom NO usa isometric/depth ni steady — su
        # amplitud es la intensity. La DIRECCIÓN depende del SIGNO de intensity
        # (positivo=in, negativo=out), pero clamp_intensity la deja siempre
        # POSITIVA, así que zoom_out zoomearía IN si dependiéramos del LLM.
        # Fix: derivamos la dirección del NOMBRE. zoom_in queda como está
        # (positivo); zoom_out niega la intensity ya escalada.
        if movement == "zoom_out":
            opts["intensity"] = -opts["intensity"]

    return opts

# ═══════════════════════════════════════════════════════════════
#  DEPTHFLOW (entry point principal)
# ═══════════════════════════════════════════════════════════════

@error_handler.retry(PipelineStage.ASSEMBLY, max_retries=2, max_server_retries=2)
def build_depthflow_clip(
    *,
    image_path: Path,
    output_path: Path,
    duration: float,
    flow_spec: FlowSpec,
    width: int | None = None,
    height: int | None = None,
    fps: int | None = None,
    timeout: int = 300,
    tiling_mode: TilingMode = None,
    introspect_tiling: bool = False,
) -> Path:
    """
    Genera MP4 silencioso 9:16 con animación DepthFlow 2.5D.

    Args:
        tiling_mode: modo de wrap del shader cuando se muestrean pixels
            fuera de la imagen. None = no tocar (default DepthFlow=mirror/repeat).
            "black" / "clamp" elimina réplicas en zoom out agresivo.
        introspect_tiling: si True, loggea atributos de scene relacionados
            con tiling/wrap/border. Solo para debug/descubrimiento de API.

    Raises:
        DepthFlowError: si DepthFlow falla → caller debe llamar Ken Burns.
        FileNotFoundError: si la imagen base no existe.
    """
    if not image_path.exists():
        raise FileNotFoundError(f"Imagen base no existe: {image_path}")

    width = width or pipeline.video_width
    height = height or pipeline.video_height
    fps = fps or flow_render.fps

    output_path.parent.mkdir(parents=True, exist_ok=True)

    params = {
        "image_path": str(image_path.resolve()),
        "output_path": str(output_path.resolve()),
        "movement": _resolve_movement_name(flow_spec["movement"]),
        "options": _build_options(flow_spec, duration_seconds=float(duration)),
        "ssaa": flow_render.ssaa,
        "fps": fps,
        "width": width,
        "height": height,
        "duration": float(duration),
        "dof": flow_spec["dof"],
        "tiling_mode": tiling_mode,
        "introspect_tiling": introspect_tiling,
    }

    error_handler.log_info(
        PipelineStage.ASSEMBLY,
        f"[depthflow] {flow_spec['movement']} "
        f"(i={flow_spec['intensity']:.2f}, s={flow_spec['steady']:.2f}, "
        f"dof={flow_spec['dof']}, tiling={tiling_mode}) sobre {image_path.name}",
    )

    # Subprocess al venv aislado
    if flow_render.use_subprocess:
        python_bin = _resolve_python_bin()
        cmd = [python_bin, "-c", _DEPTHFLOW_RUNNER, json.dumps(params)]
    else:
        cmd = [sys.executable, "-c", _DEPTHFLOW_RUNNER, json.dumps(params)]

    # Env explícito: forzar CUDA + heredar resto del entorno padre
    import os as _os
    runner_env = _os.environ.copy()
    runner_env["TORCH_DEVICE"] = "cuda"
    runner_env["CUDA_VISIBLE_DEVICES"] = "0"

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True,
            timeout=timeout, encoding="utf-8",
            errors="replace",
            env=runner_env,
        )
    except subprocess.TimeoutExpired:
        raise DepthFlowError(
            f"DepthFlow timeout ({timeout}s) sobre {image_path.name}"
        )

    # Loguear diagnóstico CUDA + introspección + tiling del runner
    if result.stderr:
        for line in result.stderr.splitlines():
            if (
                line.startswith("[depthflow-runner]")
                or line.startswith("[introspect]")
                or line.startswith("[tiling]")
            ):
                error_handler.log_info(PipelineStage.ASSEMBLY, line)

    if result.returncode != 0:
        raise DepthFlowError(
            f"DepthFlow falló sobre {image_path.name} "
            f"(rc={result.returncode}): {result.stderr[-500:]}"
        )

    if not output_path.exists():
        raise DepthFlowError(
            f"DepthFlow terminó OK pero no produjo {output_path}"
        )
    return output_path


# ═══════════════════════════════════════════════════════════════
#  KEN BURNS 2D (fallback puro FFmpeg)
# ═══════════════════════════════════════════════════════════════

def build_kenburns_fallback(
    *,
    image_path: Path,
    output_path: Path,
    duration: float,
    width: int | None = None,
    height: int | None = None,
    fps: int | None = None,
    zoom_max: float | None = None,
    timeout: int = 180,
) -> Path:
    """Fallback FFmpeg zoompan cuando DepthFlow falla. Cero costo."""
    if not image_path.exists():
        raise FileNotFoundError(f"Imagen base no existe: {image_path}")

    width = width or pipeline.video_width
    height = height or pipeline.video_height
    fps = fps or flow_render.fps
    zoom_max = zoom_max or flow_render.fallback_kenburns_zoom

    output_path.parent.mkdir(parents=True, exist_ok=True)

    total_frames = max(1, int(fps * duration))
    zoom_step = round((zoom_max - 1.0) / total_frames, 6)

    vf = (
        f"scale={width * 2}:{height * 2}:flags=lanczos,"
        f"zoompan=z='min(zoom+{zoom_step},{zoom_max})':"
        f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
        f"d={total_frames}:s={width}x{height}:fps={fps}"
    )

    cmd = [
        api.ffmpeg_path, "-y",
        "-loop", "1", "-i", str(image_path),
        "-vf", vf,
        "-c:v", "libx264",
        "-t", f"{duration:.3f}",
        "-pix_fmt", "yuv420p",
        "-preset", "fast",
        "-r", str(fps),
        str(output_path),
    ]

    result = subprocess.run(
        cmd, capture_output=True, text=True,
        timeout=timeout, encoding="utf-8",
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"Ken Burns FFmpeg falló sobre {image_path.name}: "
            f"{result.stderr[-300:]}"
        )

    error_handler.log_info(
        PipelineStage.ASSEMBLY,
        f"[kenburns] fallback → {output_path.name} ({duration:.1f}s)",
    )
    return output_path


# ═══════════════════════════════════════════════════════════════
#  ROUTER (DepthFlow + fallback automático)
# ═══════════════════════════════════════════════════════════════

def build_animated_clip(
    *,
    image_path: Path,
    output_path: Path,
    duration: float,
    flow_spec: FlowSpec,
    width: int | None = None,
    height: int | None = None,
    fps: int | None = None,
    tiling_mode: TilingMode = None,
) -> str:
    """
    Router: intenta DepthFlow → si falla → Ken Burns 2D.
    Devuelve 'depthflow' | 'kenburns' según qué se usó realmente.
    Esta es la API que llama fase2b.py.
    """
    try:
        build_depthflow_clip(
            image_path=image_path, output_path=output_path,
            duration=duration, flow_spec=flow_spec,
            width=width, height=height, fps=fps,
            tiling_mode=tiling_mode,
        )
        return "depthflow"
    except (DepthFlowError, FileNotFoundError) as e:
        if not flow_render.fallback_to_kenburns:
            raise
        error_handler.log_warning(
            PipelineStage.ASSEMBLY,
            f"[animator] DepthFlow falló ({e}) → Ken Burns 2D",
        )
        build_kenburns_fallback(
            image_path=image_path, output_path=output_path,
            duration=duration, width=width, height=height, fps=fps,
        )
        return "kenburns"


# ═══════════════════════════════════════════════════════════════
#  HOOK CLIP (zoom corto + freeze frame para ch01 primera imagen)
# ═══════════════════════════════════════════════════════════════

def build_hook_clip(
    *,
    image_path: Path,
    output_path: Path,
    total_duration: float,
    zoom_duration: float,
    flow_spec: FlowSpec,
    width: int | None = None,
    height: int | None = None,
    fps: int | None = None,
    timeout: int = 300,
) -> Path:
    """
    Hook viral: DepthFlow zoom rápido (zoom_duration s) + FFmpeg tpad clone
    el último frame el resto del tiempo hasta total_duration.

    El resultado es un clip de total_duration s con punch dramático al
    inicio y respiración estática sobre el frame final. Patrón validado
    en lab_zoom_in_reveal.py v2 (variación v2_zoom_in_balanced ganadora:
    zoom 2.5s + freeze 5.5s con i=0.95 s=0.0).

    Pipeline 2 etapas:
      1. build_depthflow_clip(duration=zoom_duration) → clip temporal
      2. FFmpeg tpad=stop_mode=clone:stop_duration=freeze_s → clip final

    Args:
        total_duration: duración final del clip en segundos.
        zoom_duration: duración del zoom DepthFlow. Debe ser < total_duration.
        flow_spec: spec del movimiento (típicamente movement="zoom_in").

    Raises:
        ValueError: si zoom_duration >= total_duration o <= 0.
        DepthFlowError: si DepthFlow falla en el zoom.
        RuntimeError: si FFmpeg tpad falla.
        FileNotFoundError: si la imagen base no existe.
    """
    if zoom_duration <= 0:
        raise ValueError(f"zoom_duration debe ser > 0, recibido: {zoom_duration}")
    if zoom_duration >= total_duration:
        raise ValueError(
            f"zoom_duration ({zoom_duration}s) debe ser < "
            f"total_duration ({total_duration}s); usar build_depthflow_clip directo."
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    freeze_duration = total_duration - zoom_duration

    # Etapa 1: DepthFlow corto sobre la imagen
    zoom_clip = output_path.parent / f"_hook_zoom_{output_path.stem}.mp4"
    build_depthflow_clip(
        image_path=image_path,
        output_path=zoom_clip,
        duration=zoom_duration,
        flow_spec=flow_spec,
        width=width, height=height, fps=fps,
        timeout=timeout,
    )

    # Etapa 2: FFmpeg tpad freeze frame
    cmd = [
        api.ffmpeg_path, "-y",
        "-i", str(zoom_clip),
        "-vf", f"tpad=stop_mode=clone:stop_duration={freeze_duration:.3f}",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-an",
        str(output_path),
    ]

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True,
            timeout=120, encoding="utf-8", errors="replace",
        )
    except subprocess.TimeoutExpired:
        zoom_clip.unlink(missing_ok=True)
        raise RuntimeError(f"FFmpeg tpad timeout (120s) sobre {image_path.name}")

    if result.returncode != 0:
        zoom_clip.unlink(missing_ok=True)
        raise RuntimeError(
            f"FFmpeg tpad falló sobre {image_path.name}: "
            f"{result.stderr[-300:]}"
        )

    if not output_path.exists():
        zoom_clip.unlink(missing_ok=True)
        raise RuntimeError(
            f"FFmpeg tpad terminó OK pero no produjo {output_path}"
        )

    # Cleanup intermedio
    zoom_clip.unlink(missing_ok=True)

    error_handler.log_info(
        PipelineStage.ASSEMBLY,
        f"[hook_clip] zoom {zoom_duration:.1f}s + freeze {freeze_duration:.1f}s "
        f"→ {output_path.name}",
    )
    return output_path
