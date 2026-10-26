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
#  F2b §4: CONCAT POR VENTANAS (re-encode solo alrededor de cada frontera)
# ═══════════════════════════════════════════════════════════════
# El xfade encadenado re-encodea el video ENTERO (~15 min a 1440p). Acá el resultado tiene la MISMA
# línea de tiempo (Σ duraciones − Σ transiciones) pero:
#   - cada segmento se parte por COPIA en sus keyframes (muxer segment, sin decodificar);
#   - solo se re-encodea una ventana por frontera: [último keyframe ≤ fin − t − w del saliente,
#     primer keyframe ≥ t + w del entrante], con el xfade adentro y los MISMOS parámetros de encode
#     que los segmentos (mismo SPS → el concat por copia es válido);
#   - las piezas (cuerpos copiados + ventanas) se pegan con el concat demuxer y `-c copy` (MPEG-TS);
#   - el audio se arma aparte con acrossfade encadenado (audio solo, barato) y se muxea al final.
# Deja en work_dir `_concat_video.ts` y `_concat_audio.wav` para que la mezcla de música no re-encodee video.

WINDOW_SEC: float = 1.0                      # ± alrededor de cada transición (spec: ±1 s)


@dataclass(frozen=True)
class SegmentInfo:
    path: Path
    frames: int
    fps: float
    keyframes: tuple[float, ...]             # pts (s) de los keyframes de video

    @property
    def duration(self) -> float:
        return self.frames / self.fps


def probe_segment(path: Path, ffprobe: str) -> SegmentInfo:
    """Frames, fps y keyframes del video (por paquetes: sin decodificar)."""
    r = _run_cmd([ffprobe, "-v", "error", "-select_streams", "v:0", "-count_packets", "-show_entries",
                  "stream=nb_read_packets,r_frame_rate", "-of", "json", str(path)], timeout=120)
    if r.returncode != 0:
        raise RuntimeError(f"ffprobe {path.name}: {r.stderr[-200:]}")
    st = json.loads(r.stdout)["streams"][0]
    num, den = (int(x) for x in st["r_frame_rate"].split("/"))
    k = _run_cmd([ffprobe, "-v", "error", "-select_streams", "v:0", "-show_entries", "packet=pts_time,flags",
                  "-of", "csv=p=0", str(path)], timeout=300)
    kfs = sorted(float(a) for a, f in (ln.split(",")[:2] for ln in k.stdout.split() if "," in ln) if "K" in f)
    return SegmentInfo(path, int(st["nb_read_packets"]), num / den, tuple(kfs))


def plan_windows(infos: list[SegmentInfo], trans: list[float], window_sec: float = WINDOW_SEC
                 ) -> list[tuple[float, float]] | None:
    """Por segmento i: (inicio, fin) del CUERPO que se copia, alineado a keyframes. None si algún
    segmento no deja cuerpo (fronteras demasiado cerca) → el caller usa el concat clásico."""
    bodies = []
    for i, s in enumerate(infos):
        a = 0.0
        if i > 0:                                       # primer keyframe ≥ t + w (lo anterior va a la ventana)
            a = next((k for k in s.keyframes if k >= trans[i - 1] + window_sec - 1e-6), None)
        b = s.duration
        if i < len(infos) - 1:                          # último keyframe ≤ fin − t − w
            b = next((k for k in reversed(s.keyframes) if k <= s.duration - trans[i] - window_sec + 1e-6), None)
        if a is None or b is None or b - a < 1.0 / s.fps:
            return None
        bodies.append((a, b))
    return bodies


def _split_copy(seg: SegmentInfo, cuts: list[float], out_dir: Path, tag: str, ffmpeg: str) -> list[Path]:
    """Parte el video del segmento por COPIA en los keyframes `cuts` → piezas .ts en orden."""
    eps = 0.25 / seg.fps                                # el muxer corta en el 1er keyframe ≥ t
    pattern = out_dir / f"_cw_{tag}_%02d.ts"
    cmd = [ffmpeg, "-v", "error", "-y", "-i", str(seg.path), "-map", "0:v:0", "-c", "copy", "-an",
           "-f", "segment", "-reset_timestamps", "1", "-segment_format", "mpegts"]
    if cuts:
        cmd += ["-segment_times", ",".join(f"{max(0.0, c - eps):.6f}" for c in cuts)]
    r = _run_cmd(cmd + [str(pattern)], timeout=600)
    if r.returncode != 0:
        raise RuntimeError(f"split por copia {seg.path.name}: {r.stderr[-300:]}")
    return sorted(out_dir.glob(f"_cw_{tag}_*.ts"))


def concat_windowed(
    segments: list[Path],
    final_path: Path,
    work_dir: Path,
    art_profiles: list[str | None],
    ffmpeg: str,
    ffprobe: str,
    venc: list[str],
    window_sec: float = WINDOW_SEC,
    negro_frames: int | None = None,
) -> Path:
    """Mismo resultado temporal que concat_with_transitions, re-encodeando solo ventanas de frontera.

    venc: args del encoder de video de los segmentos (fase2b._venc()): las ventanas DEBEN salir con el
    mismo encoder para que el concat por copia sea válido. Lanza si algo falla (el caller cae al clásico).
    negro_frames (F30b §B.1, con --gfx): toda unión cap → cap es un corte sin solapar (el cap saliente ya termina en
    su black_hold) y el entrante sube desde negro en `negro_frames` cuadros (`fade=in`); el audio se pega sin
    acrossfade. Nunca pasa por el xfade de los perfiles de arte (ni fadewhite).
    """
    if len(segments) < 2 or not transition_render.enable_transitions:
        raise ValueError("concat por ventanas: necesita ≥ 2 segmentos y transiciones activas")
    plans = build_transition_plan(len(segments), art_profiles)
    infos = [probe_segment(s, ffprobe) for s in segments]
    fps = infos[0].fps
    if negro_frames:                                    # F30b §B.1: corte a negro, sin solapar
        plans = [TransitionPlan(i, "corte_negro", 0.0) for i in range(len(segments) - 1)]
        trans = [0.0] * (len(segments) - 1)
    else:
        trans = [max(p.duration_seconds, 1.0 / fps) for p in plans]
        trans = [round(t * fps) / fps for t in trans]   # transición en frames enteros
    bodies = plan_windows(infos, trans, window_sec)
    if bodies is None:
        raise ValueError("concat por ventanas: un segmento no deja cuerpo entre fronteras")
    tmp = work_dir / "_cw"
    if tmp.exists():
        for f in tmp.iterdir():
            f.unlink()
    tmp.mkdir(parents=True, exist_ok=True)

    pieces: list[Path] = []
    for i, (s, (a, b)) in enumerate(zip(infos, bodies)):
        cuts = [c for c in (a, b) if 0.0 < c < s.duration]
        parts = _split_copy(s, cuts, tmp, f"s{i:02d}", ffmpeg)
        # orden de las piezas: [0, a) | [a, b) | [b, fin) → el cuerpo es la del medio (o la primera si a == 0)
        pieces.append(parts[1] if a > 0 else parts[0])
        if i < len(infos) - 1:                          # ventana i: cola de s (desde b) + cabeza de s+1 (hasta a')
            nxt_a = bodies[i + 1][0]
            tail = s.duration - b
            win = tmp / f"_cw_w{i:02d}.ts"
            if negro_frames:                            # F30b §B.1: el entrante sube desde negro
                fc = (f"[0:v]setpts=PTS-STARTPTS[a];[1:v]trim=end={nxt_a:.6f},setpts=PTS-STARTPTS,"
                      f"fade=t=in:st=0:d={negro_frames / fps:.6f}[b];[a][b]concat=n=2:v=1:a=0,format=yuv420p[v]")
            else:
                fc = (f"[0:v]setpts=PTS-STARTPTS[a];[1:v]trim=end={nxt_a:.6f},setpts=PTS-STARTPTS[b];"
                      f"[a][b]xfade=transition={_xfade_transition_for(plans[i].transition_name)}:"
                      f"duration={trans[i]:.6f}:offset={tail - trans[i]:.6f},format=yuv420p[v]")
            r = _run_cmd([ffmpeg, "-v", "error", "-y", "-ss", f"{b:.6f}", "-i", str(s.path), "-i", str(segments[i + 1]),
                          "-filter_complex", fc, "-map", "[v]", *venc, "-pix_fmt", "yuv420p", "-r", f"{fps:g}",
                          "-an", "-f", "mpegts", str(win)], timeout=_scaled_timeout(tail + nxt_a, 300))
            if r.returncode != 0:
                raise RuntimeError(f"ventana {i}: {r.stderr[-300:]}")
            pieces.append(win)

    # video: concat por copia de cuerpos + ventanas
    lst = tmp / "_cw_list.txt"
    lst.write_text("\n".join(f"file '{p.resolve().as_posix()}'" for p in pieces), encoding="utf-8")
    video_ts = work_dir / "_concat_video.ts"
    r = _run_cmd([ffmpeg, "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy",
                  "-f", "mpegts", str(video_ts)], timeout=900)
    if r.returncode != 0:
        raise RuntimeError(f"concat por copia: {r.stderr[-300:]}")

    # audio: acrossfade encadenado (solo audio)
    parts_a = []
    if negro_frames:                                    # F30b §B.1: sin solapar, el audio se pega tal cual
        parts_a.append("".join(f"[{i}:a]" for i in range(len(segments)))
                       + f"concat=n={len(segments)}:v=0:a=1[a{len(segments) - 1}]")
    for i in range(len(segments) - 1) if not negro_frames else ():
        src = "0:a" if i == 0 else f"a{i}"
        parts_a.append(f"[{src}][{i + 1}:a]acrossfade=d={trans[i]:.6f}:c1=tri:c2=tri[a{i + 1}]")
    audio_wav = work_dir / "_concat_audio.wav"
    cmd = [ffmpeg, "-v", "error", "-y"]
    for s in segments:
        cmd += ["-i", str(s)]
    r = _run_cmd(cmd + ["-filter_complex", ";".join(parts_a), "-map", f"[a{len(segments) - 1}]",
                        "-c:a", "pcm_s16le", str(audio_wav)], timeout=900)
    if r.returncode != 0:
        raise RuntimeError(f"audio acrossfade: {r.stderr[-300:]}")

    # final (sin música): video copiado + audio AAC
    r = _run_cmd([ffmpeg, "-v", "error", "-y", "-i", str(video_ts), "-i", str(audio_wav), "-map", "0:v:0", "-map", "1:a:0",
                  "-c:v", "copy", "-c:a", transition_render.audio_codec, "-b:a", "192k", "-movflags", "+faststart",
                  str(final_path)], timeout=900)
    if r.returncode != 0:
        raise RuntimeError(f"mux final: {r.stderr[-300:]}")
    for f in tmp.iterdir():
        f.unlink()
    tmp.rmdir()
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
