"""
modules/transition_applier.py — Aplicador FFmpeg de transiciones entre segmentos.

Reemplaza el `concat demuxer` plano por un pipeline `filter_complex` con xfade
encadenado (video) + acrossfade encadenado (audio).

Inputs:
  - lista de segmentos MP4 (uno por capítulo, ya con audio + subs quemados)
  - lista de plans (para resolver art_profile y posición narrativa)

Output:
  - MP4 final concatenado con transiciones aplicadas

Cascada de fallback:
  1. Si enable_transitions=False → concat demuxer puro (hard cut)
  2. Si todas las transiciones son hard_cut → concat demuxer puro
  3. Si filter_complex falla → fallback a concat demuxer (si fallback_to_hard_cut=True)

NO modifica los segmentos de entrada (read-only).
NO toca cost_tracker (FFmpeg local, costo $0).
NO requiere error_handler (es síncrono y los errores se devuelven como excepción).
"""
from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path

from transition_config import (
    DEFAULT_TRANSITION,
    get_effect,
    is_valid,
    transition_render,
)
from transition_profiles import (
    NARRATIVE_POSITIONS,
    get_default_transition,
    is_allowed,
)


# ═══════════════════════════════════════════════════════════════
#  TIPOS
# ═══════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class TransitionPlan:
    """Una transición entre el segmento `from_idx` y el segmento `from_idx + 1`."""
    from_idx: int
    transition_name: str
    duration_seconds: float


# ═══════════════════════════════════════════════════════════════
#  RESOLUCIÓN DE POSICIÓN NARRATIVA
# ═══════════════════════════════════════════════════════════════

def resolve_position(from_idx: int, total: int) -> str:
    """
    Determina la posición narrativa de la unión entre segmento `from_idx` y `from_idx+1`.

    Reglas:
      - 0 → 1                  : "hook_to_body"   (entrada al misterio)
      - total-2 → total-1      : "body_to_reveal" (caída a revelación)
      - mid-1 → mid (mid=total//2) en LONG (≥6) : "body_to_climax"
      - resto                  : "body_to_body"

    Para SHORT (4 segmentos): 0→1=hook, 1→2=climax (mid=2), 2→3=reveal
    Para LONG (8 segmentos): 0→1=hook, 3→4=climax (mid=4), 6→7=reveal, resto body
    """
    if from_idx < 0 or from_idx >= total - 1:
        return "body_to_body"  # fallback seguro

    if from_idx == 0:
        return "hook_to_body"
    if from_idx == total - 2:
        return "body_to_reveal"
    # Climax solo si total tiene un mid bien definido
    mid = total // 2
    if total >= 4 and from_idx == mid - 1:
        return "body_to_climax"
    return "body_to_body"


def build_transition_plan(
    segment_count: int,
    art_profiles: list[str | None],
) -> list[TransitionPlan]:
    """
    Construye la lista de transiciones a aplicar entre N segmentos consecutivos.

    `art_profiles[i]` corresponde al art_profile del segmento i. Si es None,
    usa "SUBMARINE" como fallback (cualquier profile válido sirve para resolver).

    La transición entre segmento i y i+1 usa el art_profile del segmento i+1
    (el que está entrando), porque la estética que entra es la que dicta el efecto.
    """
    if segment_count < 2:
        return []

    plans: list[TransitionPlan] = []
    for i in range(segment_count - 1):
        next_profile = art_profiles[i + 1] if i + 1 < len(art_profiles) else None
        profile = next_profile or "SUBMARINE"  # fallback seguro

        position = resolve_position(i, segment_count)
        try:
            name = get_default_transition(profile, position)
        except KeyError:
            # art_profile desconocido → usa default global
            name = DEFAULT_TRANSITION

        # Validar que esté permitida (defensa extra)
        if not is_allowed(profile, name):
            name = DEFAULT_TRANSITION
            if not is_allowed(profile, name):
                name = "hard_cut"

        effect = get_effect(name)
        plans.append(TransitionPlan(
            from_idx=i,
            transition_name=name,
            duration_seconds=effect.duration_ms / 1000.0,
        ))
    return plans


# ═══════════════════════════════════════════════════════════════
#  MAPEO TRANSICIÓN → FFMPEG xfade transition name
# ═══════════════════════════════════════════════════════════════

# Mapeo del nombre interno → nombre nativo de xfade en FFmpeg.
# whip_pan_flash usa fadewhite (flash blanco) como aproximación pragmática:
# es 80% del efecto whip+flash sin filter_complex extremadamente complejo.
# Para un whip real (motion blur horizontal) se requiere filter custom.
_XFADE_MAP: dict[str, str] = {
    "whip_pan_flash":  "fadewhite",   # flash blanco (parte clave del efecto)
    "zoom_punch":      "zoomin",
    "crossfade":       "fade",
    "crossfade_micro": "fade",
    "fade_to_black":   "fadeblack",
    "fade_to_white":   "fadewhite",
    "hard_cut":        "fade",        # fade de 1 frame ≈ corte seco
}


def _xfade_transition_for(name: str) -> str:
    return _XFADE_MAP.get(name, "fade")


# ═══════════════════════════════════════════════════════════════
#  APLICADOR FFMPEG
# ═══════════════════════════════════════════════════════════════

def _build_filter_complex(
    durations: list[float], plans: list[TransitionPlan],
) -> tuple[str, str, str]:
    """
    Construye el filter_complex string para xfade encadenado + acrossfade encadenado.

    Retorna (filter_complex, video_label_final, audio_label_final).
    """
    n = len(durations)
    if n < 2 or len(plans) != n - 1:
        raise ValueError(f"Mismatch durations={n} plans={len(plans)}")

    parts: list[str] = []
    acc_duration = durations[0]
    prev_v_label = "0:v"
    prev_a_label = "0:a"

    for i, plan in enumerate(plans):
        t = max(plan.duration_seconds, 0.04)  # mínimo 1 frame para evitar xfade=0
        offset = max(acc_duration - t, 0.04)
        x_name = _xfade_transition_for(plan.transition_name)

        v_out = f"v{i+1}" if i < n - 2 else "vout"
        a_out = f"a{i+1}" if i < n - 2 else "aout"

        parts.append(
            f"[{prev_v_label}][{i+1}:v]"
            f"xfade=transition={x_name}:duration={t:.3f}:offset={offset:.3f}"
            f"[{v_out}]"
        )
        parts.append(
            f"[{prev_a_label}][{i+1}:a]"
            f"acrossfade=d={t:.3f}:c1=tri:c2=tri"
            f"[{a_out}]"
        )

        acc_duration = acc_duration + durations[i + 1] - t
        prev_v_label = v_out
        prev_a_label = a_out

    return ";".join(parts), prev_v_label, prev_a_label


def _run_cmd(cmd: list[str], timeout: int = 600) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def _scaled_timeout(total_dur: float, floor: int) -> int:
    """Timeout proporcional a la duración del contenido (5× realtime), con piso.

    El costo de un re-encode FFmpeg escala con la duración del video; un timeout
    fijo se queda corto en videos largos. `total_dur` no-positivo/None → el piso.
    """
    if not total_dur or total_dur <= 0:
        return floor
    return max(floor, int(total_dur * 5))


def _concat_timeout(total_dur: float) -> int:
    """Timeout del concat final (piso 900). 60s→900 · 687s→3435 · 0/neg→900."""
    return _scaled_timeout(total_dur, 900)


def _get_duration(filepath: Path, ffprobe: str) -> float:
    result = _run_cmd(
        [ffprobe, "-v", "quiet", "-print_format", "json",
         "-show_format", str(filepath)],
        timeout=15,
    )
    if result.returncode != 0:
        raise RuntimeError(f"ffprobe falló sobre {filepath.name}: {result.stderr[-200:]}")
    data = json.loads(result.stdout)
    return float(data["format"]["duration"])


def _concat_demuxer_fallback(
    segments: list[Path], final_path: Path, work_dir: Path, ffmpeg: str,
    ffprobe: str, total_dur: float | None = None,
) -> Path:
    """Concat demuxer puro (hard cut sin transiciones). Mismo comportamiento histórico.

    Re-encodea todo el video (libx264), así que el timeout escala con la duración
    total igual que el concat con transiciones. `total_dur` se reusa si el caller ya
    lo midió; si es None se mide aquí (ffprobe barato). Piso 600 (histórico).
    """
    if total_dur is None:
        total_dur = sum(_get_duration(s, ffprobe) for s in segments)
    timeout = _scaled_timeout(total_dur, 600)
    concat_file = work_dir / "_final_concat.txt"
    concat_file.write_text(
        "\n".join(f"file '{s.resolve()}'" for s in segments),
        encoding="utf-8",
    )
    cmd = [
        ffmpeg, "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_file),
        "-c:v", "libx264",
        "-c:a", "aac",
        "-movflags", "+faststart",
        str(final_path),
    ]
    result = _run_cmd(cmd, timeout=timeout)
    concat_file.unlink(missing_ok=True)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg concat fallback falló: {result.stderr[-300:]}")
    return final_path


# ═══════════════════════════════════════════════════════════════
#  ENTRY POINT PÚBLICO
# ═══════════════════════════════════════════════════════════════

def concat_with_transitions(
    segments: list[Path],
    final_path: Path,
    work_dir: Path,
    art_profiles: list[str | None],
    ffmpeg: str,
    ffprobe: str,
) -> Path:
    """
    Concatena `segments` aplicando transiciones según `art_profiles` y posiciones.

    - Master switch en transition_config.transition_render.enable_transitions
    - Si todas las uniones resuelven a hard_cut → fallback a concat demuxer
    - Si filter_complex falla y fallback_to_hard_cut=True → concat demuxer

    Args:
        segments      : segmentos MP4 ordenados (1 por capítulo)
        final_path    : ruta de salida del MP4 final
        work_dir      : directorio para archivos temporales
        art_profiles  : list[str|None] paralelo a segments (art_profile por capítulo)
        ffmpeg/ffprobe: rutas absolutas a los binarios

    Returns:
        Path al MP4 final.
    """
    if len(segments) == 0:
        raise ValueError("No hay segmentos para concatenar")
    if len(segments) == 1:
        # Un solo segmento → solo copiarlo (re-encode: escala con SU duración)
        try:
            dur = _get_duration(segments[0], ffprobe)
        except Exception:
            dur = 0.0
        timeout = _scaled_timeout(dur, 300)
        cmd = [ffmpeg, "-y", "-i", str(segments[0]),
               "-c:v", "libx264", "-c:a", "aac",
               "-movflags", "+faststart", str(final_path)]
        result = _run_cmd(cmd, timeout=timeout)
        if result.returncode != 0:
            raise RuntimeError(f"FFmpeg copia 1-seg falló: {result.stderr[-300:]}")
        return final_path

    # Master switch
    if not transition_render.enable_transitions:
        print("     ↩  transitions DESHABILITADAS (master switch) → concat demuxer")
        return _concat_demuxer_fallback(segments, final_path, work_dir, ffmpeg, ffprobe)

    # Construir plan
    plans = build_transition_plan(len(segments), art_profiles)

    # Si todas son hard_cut → no vale la pena filter_complex
    if all(p.transition_name == "hard_cut" for p in plans):
        print("     ↩  todas hard_cut → concat demuxer")
        return _concat_demuxer_fallback(segments, final_path, work_dir, ffmpeg, ffprobe)

    # Resumen de transiciones (visible en logs)
    summary = " · ".join(
        f"{p.from_idx}→{p.from_idx+1}:{p.transition_name}" for p in plans
    )
    print(f"     🎬 transiciones: {summary}")

    # Calcular duraciones reales
    durations = [_get_duration(s, ffprobe) for s in segments]
    total_dur = sum(durations)

    # Construir filter_complex
    try:
        fc, v_label, a_label = _build_filter_complex(durations, plans)
    except Exception as e:
        if transition_render.fallback_to_hard_cut:
            print(f"     ⚠ filter_complex inválido ({e}) → fallback hard cut")
            return _concat_demuxer_fallback(
                segments, final_path, work_dir, ffmpeg, ffprobe, total_dur
            )
        raise

    # Construir comando FFmpeg
    cmd: list[str] = [ffmpeg, "-y"]
    for s in segments:
        cmd.extend(["-i", str(s)])
    cmd.extend([
        "-filter_complex", fc,
        "-map", f"[{v_label}]",
        "-map", f"[{a_label}]",
        "-c:v", transition_render.video_codec,
        "-preset", transition_render.preset,
        "-crf", str(transition_render.crf),
        "-pix_fmt", transition_render.pix_fmt,
        "-c:a", transition_render.audio_codec,
        "-movflags", "+faststart",
        str(final_path),
    ])

    timeout = _concat_timeout(total_dur)
    print(f"     ⏱ concat final: {total_dur:.0f}s de video → timeout {timeout}s")
    result = _run_cmd(cmd, timeout=timeout)
    if result.returncode != 0:
        if transition_render.fallback_to_hard_cut:
            print(f"     ⚠ FFmpeg xfade falló → fallback hard cut")
            print(f"        stderr: {result.stderr[-300:]}")
            return _concat_demuxer_fallback(
                segments, final_path, work_dir, ffmpeg, ffprobe, total_dur
            )
        raise RuntimeError(
            f"FFmpeg concat con transiciones falló: {result.stderr[-300:]}"
        )

    return final_path
