"""
fase2b.py — Ensamblaje final del video SIN regenerar imágenes/clips/audio.

Lee los assets que dejó Fase 2A:
  output/audio/{video_id}/sync_map.json + chXX.mp3 + chXX_timestamps.json
  output/{video_id}/assets/assets_manifest.json + chXX_{flux|veo}/...
  data/scripts/{video_id}.json (script crudo — para narration + image_prompt)

Por cada capítulo construye un segmento MP4 sincronizado:
  - render_engine='veo'  → clip MP4 con loop fix (-stream_loop -1 + -t)
  - render_engine='flux' → slideshow con DepthFlow 2.5D guiado por flow_director
                           (1 call a Gemini Flash por art_profile distinto)
                           con fallback automático a Ken Burns 2D si falla.
Quema subtítulos virales (karaoke 3-words) desde los timestamps Whisper YA
generados (NO se vuelve a transcribir). Hook overlay opcional en ch01.

Concatena todos los segmentos → output/{video_id}/{video_id}_final.mp4

USO:
    python fase2b.py <video_id>
    python fase2b.py <video_id> --hook "TEXTO GIGANTE"
    python fase2b.py <video_id> --dry-run
    python fase2b.py <video_id> --no-subs           # sin subtítulos
    python fase2b.py <video_id> --keep-segments    # no borrar segments temp

Costo API: solo Gemini Flash batch del flow_director (~$0.0001 por art_profile).
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import pyphen

from config import BASE_DIR, OUTPUT_DIR, pipeline
from cost_tracker import cost_tracker
from error_handler import error_handler, PipelineStage
from script_engine.flow_director import select_movements_batch
from script_engine.parallax_animator_v2 import (
    build_animated_clip,
    build_kenburns_fallback,
)
from script_engine.topics_db import (
    load_db,
    mark_as_generated,
    save_db,
)
from flow_profiles import FlowSpec
from script_engine.transition_applier import concat_with_transitions
from subs_remap import remap_words_to_original
from anchor_timing import compute_anchor_starts

# Estados procesables por fase2b
ASSETS_READY_STATUS: str = "assets_rendered"
DONE_STATUS: str = "video_generated"


# ═══════════════════════════════════════════════════════════════
#  Forzar UTF-8 (Windows usa cp1252 por defecto)
# ═══════════════════════════════════════════════════════════════

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


# ═══════════════════════════════════════════════════════════════
#  FFmpeg / FFprobe lookup (Windows winget fallback)
# ═══════════════════════════════════════════════════════════════

def _find_ffmpeg_binary(name: str) -> str | None:
    found = shutil.which(name)
    if found:
        return found
    winget_base = Path.home() / "AppData" / "Local" / "Microsoft" / "WinGet" / "Packages"
    if winget_base.exists():
        for pkg_dir in winget_base.glob("Gyan.FFmpeg_*"):
            matches = list(pkg_dir.glob(f"ffmpeg-*/bin/{name}.exe"))
            if matches:
                return str(matches[0])
    return None


FFMPEG: str | None = _find_ffmpeg_binary("ffmpeg")
FFPROBE: str | None = _find_ffmpeg_binary("ffprobe")


# ═══════════════════════════════════════════════════════════════
#  Constantes de render
# ═══════════════════════════════════════════════════════════════

HOOK_DURATION: float = 1.8           # seg de pre-padding/overlay en ch01


# ═══════════════════════════════════════════════════════════════
#  Mixer música/ducking (PR 2.C chat 28)
# ═══════════════════════════════════════════════════════════════

# Duración del crossfade entre tracks de música en límites de cap.
# Default 2.0s (estándar documental — suficiente flujo sin diluir cortes).
MUSIC_CROSSFADE_SEC: float = 2.0

# Suffix del MP4 final cuando hay música mezclada.
# Sin música → `{video_id}_final.mp4` (default histórico, compat).
# Con música → `{video_id}_final.mp4` también; el sin-música se preserva
# como `{video_id}_final_no_music.mp4` durante el run para debugging.
MUSIC_INTERMEDIATE_SUFFIX: str = "_no_music"

# Filename del track continuo de música en work_dir (intermediate).
# WAV para no perder calidad en el sidechain.
CONTINUOUS_MUSIC_FILENAME: str = "_music_continuous.wav"

# Chat 32: padding de silencio al inicio del MP4 final (música respira sola,
# arranca el hook con pausa estructural).
INITIAL_SILENCE_SEC = 2.5


# ═══════════════════════════════════════════════════════════════
#  Helpers FFmpeg / paths
# ═══════════════════════════════════════════════════════════════

def _run_cmd(cmd: list[str], timeout: int = 240) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def _get_duration(filepath: Path) -> float:
    assert FFPROBE is not None
    result = _run_cmd(
        [FFPROBE, "-v", "quiet", "-print_format", "json", "-show_format", str(filepath)],
        timeout=15,
    )
    if result.returncode != 0:
        raise RuntimeError(f"ffprobe falló sobre {filepath.name}: {result.stderr[-200:]}")
    data = json.loads(result.stdout)
    return float(data["format"]["duration"])


def _escape_ass_path_for_ffmpeg(path: Path) -> str:
    """Escapa el path al estilo que el filtro ass= de FFmpeg necesita en Windows."""
    p = str(path.resolve()).replace("\\", "/")
    if len(p) > 1 and p[1] == ":":
        p = p[0] + r"\:" + p[2:]
    return p


def _format_ass_time(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return f"{h}:{m:02d}:{s:05.2f}"


# ═══════════════════════════════════════════════════════════════
#  Subs virales (karaoke) desde timestamps PRE-EXISTENTES
# ═══════════════════════════════════════════════════════════════

def _merge_punctuation_words(words: list[dict]) -> list[dict]:
    """Une tokens huérfanos: '10' + '.000' → '10.000'."""
    if not words:
        return words
    merged: list[dict] = [dict(words[0])]
    for w in words[1:]:
        first_char = w["word"][0] if w["word"] else ""
        prev_last = merged[-1]["word"][-1] if merged[-1]["word"] else ""
        if first_char in ".,:;" and prev_last.isalnum():
            merged[-1]["word"] += w["word"]
            merged[-1]["end"] = w["end"]
        else:
            merged.append(dict(w))
    return merged


def _chunk_words_adaptive(
    words: list[dict], target: int = 3, max_chars: int = 18,
) -> list[list[dict]]:
    chunks: list[list[dict]] = []
    i = 0
    while i < len(words):
        chunk = words[i:i + target]
        total = sum(len(w["word"]) for w in chunk) + max(0, len(chunk) - 1)
        while len(chunk) > 1 and total > max_chars:
            chunk = chunk[:-1]
            total = sum(len(w["word"]) for w in chunk) + max(0, len(chunk) - 1)
        chunks.append(chunk)
        i += len(chunk)
    return chunks


def _calc_hook_layout(text: str, max_width: int = 640) -> tuple[str, int]:
    """Divide hook en 1-2 líneas y calcula fontsize. Retorna (texto_con_\\N, fontsize)."""
    text = text.upper().strip()
    words = text.split()
    if len(words) <= 2 or len(text) <= 12:
        lines = [text]
        max_cap = 180
    else:
        total_len = sum(len(w) for w in words) + len(words) - 1
        target = total_len / 2
        acc = 0
        split_at = 1
        for i, w in enumerate(words):
            acc += len(w) + (1 if i > 0 else 0)
            if acc >= target:
                split_at = i + 1
                break
        lines = [" ".join(words[:split_at]), " ".join(words[split_at:])]
        max_cap = 140
    longest = max(len(line) for line in lines)
    size_from_width = int(max_width / (longest * 0.55))
    fontsize = max(min(size_from_width, max_cap), 80)
    return "\\N".join(lines), fontsize


def _build_ass_from_words(
    words: list[dict],
    output_path: Path,
    audio_duration: float,
    video_width: int,
    video_height: int,
    words_per_chunk: int = 3,
    hook_text: str | None = None,
    hook_duration: float = HOOK_DURATION,
    pre_pad: float = 0.0,
) -> Path:
    """
    Variante de generate_viral_subtitles_ass() que NO transcribe — usa words pre-existentes.
    `words` es una lista de dicts {word, start, end} (formato Whisper).
    """
    # Normalizar (los timestamps guardados ya están sin merge, aplicamos por seguridad)
    words = _merge_punctuation_words([dict(w) for w in words])

    # Desplazar palabras si hay pre-padding
    if pre_pad > 0:
        for w in words:
            w["start"] = float(w["start"]) + pre_pad
            w["end"] = float(w["end"]) + pre_pad

    if not words and not hook_text:
        output_path.write_text("", encoding="utf-8")
        return output_path

    chunks = _chunk_words_adaptive(words, target=words_per_chunk, max_chars=18)
    word_map: dict[int, tuple[int, int]] = {}
    gidx = 0
    for ch_idx, chunk in enumerate(chunks):
        for pos, _ in enumerate(chunk):
            word_map[gidx] = (ch_idx, pos)
            gidx += 1

    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {video_width}
PlayResY: {video_height}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Viral,Anton,100,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,7,4,2,40,40,320,1
Style: Hook,Anton,180,&H0000FFFF,&H000000FF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,8,5,5,40,40,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events: list[str] = []

    # ─── Hook overlay ───
    if hook_text:
        hook_txt_clean = hook_text.replace("{", "").replace("}", "").replace("\\", "")
        hook_formatted, hook_fontsize = _calc_hook_layout(hook_txt_clean)
        hook_effect = (
            r"{\an5"
            f"\\fs{hook_fontsize}"
            r"\fscx0\fscy0"
            r"\t(0,120,\fscx115\fscy115)"
            r"\t(120,220,\fscx100\fscy100)"
            r"\fad(0,150)}"
        )
        events.append(
            f"Dialogue: 0,{_format_ass_time(0.0)},"
            f"{_format_ass_time(hook_duration)},Hook,,0,0,0,,"
            f"{hook_effect}{hook_formatted}"
        )

    # ─── Subs karaoke word-level ───
    for word_idx, word in enumerate(words):
        start = float(word["start"])
        if word_idx + 1 < len(words):
            end = float(words[word_idx + 1]["start"])
        else:
            end = min(float(word["end"]) + 0.3, audio_duration)
        chunk_idx, pos_in_chunk = word_map[word_idx]
        chunk = chunks[chunk_idx]
        parts: list[str] = []
        for i, w in enumerate(chunk):
            txt = w["word"].upper().replace("{", "").replace("}", "").replace("\\", "")
            if i == pos_in_chunk:
                parts.append(
                    r"{\c&H0000FFFF&\fscx115\fscy115"
                    r"\t(0,80,\fscx135\fscy135)"
                    r"\t(80,180,\fscx120\fscy120)}"
                    + txt
                )
            else:
                parts.append(r"{\c&H00FFFFFF&\fscx100\fscy100}" + txt)
        text = " ".join(parts)
        events.append(
            f"Dialogue: 0,{_format_ass_time(start)},{_format_ass_time(end)},Viral,,0,0,0,,{text}"
        )

    output_path.write_text(header + "\n".join(events) + "\n", encoding="utf-8")
    return output_path


# ═══════════════════════════════════════════════════════════════
#  Subtítulos por SÍLABA (chat 38 — Forced Alignment + ventana deslizante)
# ═══════════════════════════════════════════════════════════════

_DIC_ES = pyphen.Pyphen(lang="es_ES")


def _chars_to_syllables(characters: list[dict]) -> list[dict]:
    """characters: [{text, start, end}, ...] de ElevenLabs alignment.
    Devuelve [{text, start, end, word_idx}, ...] por sílaba, timing REAL.
    word_idx permite al render insertar espacio entre palabras distintas.
    """
    # 1. Reconstruir palabras con sus índices de char (la puntuación/espacio corta)
    words = []  # [{text, idxs:[int,...]}]
    cur = {"text": "", "idxs": []}
    for i, c in enumerate(characters):
        ch = c.get("text", "")
        if ch == " " or ch in ".,;:!?\"'()¿¡":
            if cur["text"]:
                words.append(cur)
                cur = {"text": "", "idxs": []}
            continue
        cur["text"] += ch
        cur["idxs"].append(i)
    if cur["text"]:
        words.append(cur)

    # 2. Partir cada palabra en sílabas y mapear a chars (timing real)
    syllables = []
    for wi, w in enumerate(words):
        parts = _DIC_ES.inserted(w["text"]).split("-")
        pos = 0
        for part in parts:
            if not part:
                continue
            idxs = w["idxs"][pos:pos + len(part)]
            if not idxs:
                continue
            start = float(characters[idxs[0]]["start"])
            end = float(characters[idxs[-1]]["end"])
            syllables.append(
                {"text": part, "start": start, "end": end, "word_idx": wi}
            )
            pos += len(part)
    return syllables


def _build_ass_from_syllables(
    syllables: list[dict],
    output_path: Path,
    audio_duration: float,
    video_width: int,
    video_height: int,
    words_per_chunk: int = 3,
    max_chars: int = 18,
    hook_text: str | None = None,
    hook_duration: float = HOOK_DURATION,
    pre_pad: float = 0.0,
) -> Path:
    """Karaoke por SÍLABA con CHUNK ESTÁTICO (no marquesina).

    El chunk (~words_per_chunk palabras enteras) queda FIJO en pantalla mientras
    Bill lo pronuncia; solo popea la sílaba activa. Al terminar la última sílaba
    del chunk, aparece el siguiente. Chunking por palabra entera (reusa
    _chunk_words_adaptive) → una palabra nunca se parte.
    """
    if pre_pad > 0:
        for s in syllables:
            s["start"] = float(s["start"]) + pre_pad
            s["end"] = float(s["end"]) + pre_pad

    if not syllables and not hook_text:
        output_path.write_text("", encoding="utf-8")
        return output_path

    # Header EXACTO de _build_ass_from_words (Anton 100 Viral / Anton 180 Hook).
    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {video_width}
PlayResY: {video_height}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Viral,Anton,100,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,7,4,2,40,40,320,1
Style: Hook,Anton,180,&H0000FFFF,&H000000FF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,8,5,5,40,40,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events: list[str] = []

    # ─── Hook overlay (VERBATIM de _build_ass_from_words) ───
    if hook_text:
        hook_txt_clean = hook_text.replace("{", "").replace("}", "").replace("\\", "")
        hook_formatted, hook_fontsize = _calc_hook_layout(hook_txt_clean)
        hook_effect = (
            r"{\an5"
            f"\\fs{hook_fontsize}"
            r"\fscx0\fscy0"
            r"\t(0,120,\fscx115\fscy115)"
            r"\t(120,220,\fscx100\fscy100)"
            r"\fad(0,150)}"
        )
        events.append(
            f"Dialogue: 0,{_format_ass_time(0.0)},"
            f"{_format_ass_time(hook_duration)},Hook,,0,0,0,,"
            f"{hook_effect}{hook_formatted}"
        )

    # 1. Reconstruir palabras desde las sílabas (agrupar por word_idx).
    from itertools import groupby
    words: list[dict] = []
    for _wi, grp in groupby(enumerate(syllables), key=lambda t: t[1]["word_idx"]):
        idxs = [i for i, _ in grp]
        words.append({
            "word": "".join(syllables[i]["text"] for i in idxs),  # para _chunk_words_adaptive
            "syl_idxs": idxs,
        })

    # 2. Chunkear por palabra (MISMO criterio que el path por palabra).
    chunks = _chunk_words_adaptive(words, target=words_per_chunk, max_chars=max_chars)

    # 3. Map sílaba global -> índice de chunk.
    syl_chunk: dict[int, int] = {}
    for ci, chunk in enumerate(chunks):
        for w in chunk:
            for si in w["syl_idxs"]:
                syl_chunk[si] = ci

    # 4. Un evento por sílaba: chunk QUIETO, solo cambia el resaltado.
    n = len(syllables)
    for i in range(n):
        start = float(syllables[i]["start"])
        if i + 1 < n:
            end = float(syllables[i + 1]["start"])      # encadenado (anti-gap)
        else:
            end = min(float(syllables[i]["end"]) + 0.3, audio_duration)
        if end <= start:                                 # clamp defensivo
            end = start + 0.05

        chunk = chunks[syl_chunk[i]]
        parts: list[str] = []
        for w_pos, w in enumerate(chunk):
            if w_pos > 0:
                parts.append(" ")                        # espacio entre palabras del chunk
            for si in w["syl_idxs"]:
                txt = syllables[si]["text"].upper().replace("{", "").replace("}", "")
                if si == i:
                    parts.append(
                        r"{\c&H0000FFFF&\fscx115\fscy115"
                        r"\t(0,80,\fscx135\fscy135)"
                        r"\t(80,180,\fscx120\fscy120)}"
                        + txt
                    )
                else:
                    parts.append(r"{\c&H00FFFFFF&\fscx100\fscy100}" + txt)
        text = "".join(parts)
        events.append(
            f"Dialogue: 0,{_format_ass_time(start)},{_format_ass_time(end)},Viral,,0,0,0,,{text}"
        )

    output_path.write_text(header + "\n".join(events) + "\n", encoding="utf-8")
    return output_path


# ═══════════════════════════════════════════════════════════════
#  Construcción de segmento por capítulo
# ═══════════════════════════════════════════════════════════════

@dataclass
class ChapterPlan:
    chapter_id: str
    engine: str                 # 'veo' | 'flux'
    audio_path: Path
    audio_duration: float
    asset_paths: list[Path]     # 1 clip MP4 (veo) o N imágenes PNG (flux)
    timestamps_path: Path | None
    is_first: bool
    art_profile: str | None     # ej. 'SUBMARINE'; usado por flow_director
    narration: str = ""         # narración cruda — feed para flow_director
    image_prompt: str = ""      # prompt visual original — feed para flow_director
    label: str = ""             # 'gancho' | 'desarrollo' | etc — solo para director
    narration_anchors: list[str] | None = None  # solo flux LONG; None para veo/short
    # Híbrido Veo+Flux chat 29 #175:
    supplemental_paths: list[Path] | None = None     # PNGs Flux suplementarios (solo cap veo híbrido)
    supplemental_anchors: list[str] | None = None    # anchors paralelos a supplemental_paths
    veo_position: str = "start"                      # "start" si role=hook, "end" si role=reveal_outro
    # chat 38: path al chXX_alignment.json (characters de Forced Alignment) para
    # subs por sílaba. Defaulted para respetar el orden del dataclass; se setea
    # en la construcción del plan junto a timestamps_path.
    alignment_path: Path | None = None
    # chat 39: narrative_intent del cap (leído del sync_map). Usado por el mixer
    # de música para modular el volumen por intent (music_by_intent). "" si el cap
    # no tiene intent → usa el volumen base del perfil.
    narrative_intent: str = ""


def _compute_durations_from_anchors(
    anchors: list[str],
    timestamps_path: Path,
    total_duration: float,
    start_offset_sec: float = 0.0,
) -> list[float] | None:
    """
    Calcula la duración por imagen alineando cada narration_anchor con los words
    de chXX_timestamps.json. Devuelve None si algo falla → caller usa uniforme.

    Estrategia:
    - Para cada anchor: tomar las primeras 3 palabras alfanuméricas del anchor
      y buscar esa secuencia consecutiva en words[]. Match case-insensitive,
      ignorando puntuación.
    - start_i = words[match_idx].start
    - end_i = start_{i+1} (o end_of_segment para el último)
    - Validar: starts crecientes, durations > 0.

    Si algún anchor no matchea o el orden quedó mal → return None (fallback uniforme).

    Chat 29 #175 — start_offset_sec:
    Permite que el SEGMENTO cubierto por los anchors empiece a una offset > 0
    dentro del audio del cap. Usado para caps veo híbridos donde los Flux
    supplementals empiezan después del clip Veo (offset=8s si veo_position=start).

    Args:
        total_duration: duración del SEGMENTO que cubren los anchors
            (NO del cap entero si offset > 0).
        start_offset_sec: offset dentro del audio del cap donde arrancan los
            anchors. Default 0.0.

    Backward compat: con start_offset_sec=0.0 el comportamiento es IDÉNTICO
    bit-a-bit al pre-chat29 — sin imputación de gap, sin sum check, sin
    starts[0] >= offset check (que con offset=0 siempre pasaría trivialmente).
    """
    if not anchors or not timestamps_path.exists():
        return None
    try:
        words = json.loads(timestamps_path.read_text(encoding="utf-8"))
    except Exception:
        return None
    if not words:
        return None

    # Chat 54: matcher anchor→tiempo extraído a helper compartido (anchor_timing)
    # para que m03 (timing-aware merge) mida IDÉNTICO. Comportamiento byte-a-byte
    # igual al matcher inline previo (3-tokens → word_norm, fallback primer token,
    # cursor de orden, None si no matchea o starts no crecientes).
    starts = compute_anchor_starts(anchors, words)
    if starts is None:
        return None

    # Chat 29 #175: solo en modo híbrido (offset > 0) validar que el primer
    # anchor no caiga ANTES del offset (caso: LLM matcheó zona Veo por error).
    if start_offset_sec > 0.0:
        if starts[0] < start_offset_sec - 0.5:
            return None

    # durations[i] = starts[i+1] - starts[i]; durations[-1] = end_of_segment - starts[-1]
    # Chat 29 #175: end_of_segment = start_offset_sec + total_duration (con
    # offset=0 reduce a total_duration → comportamiento OLD).
    # Chat 29 #175: si offset > 0, la primera duration imputa el gap
    # [offset, starts[0]) a la primera imagen.
    durations: list[float] = []
    end_of_segment = start_offset_sec + total_duration
    for i in range(len(starts)):
        end = starts[i + 1] if i + 1 < len(starts) else end_of_segment
        if i == 0 and start_offset_sec > 0.0:
            # Híbrido: la primera imagen cubre [offset, end), imputando el gap
            d = end - start_offset_sec
        else:
            # Backward compat (offset=0) o no-primera imagen: comportamiento OLD
            d = end - starts[i]
        if d <= 0.05:    # mínimo razonable (mismo umbral que enforce_monotonic)
            return None
        durations.append(d)

    # Chat 29 #175: sanity sum check SOLO en modo híbrido.
    # En el modo OLD (offset=0), el código viejo no contabiliza el gap
    # [0, starts[0]) y la suma puede ser < total. Mantener comportamiento.
    if start_offset_sec > 0.0:
        sum_d = sum(durations)
        if abs(sum_d - total_duration) > 0.5:
            return None

    return durations


def _build_flux_visual(
    images: list[Path], out_path: Path, total_duration: float,
    width: int, height: int, fps: int, work_dir: Path,
    art_profile: str | None,
    flow_spec: FlowSpec | None,
    narration_anchors: list[str] | None = None,
    timestamps_path: Path | None = None,
    start_offset_sec: float = 0.0,
) -> Path:
    """
    Genera un MP4 silencioso del capítulo Flux: slideshow con DepthFlow 2.5D
    guiado por flow_spec (decisión cinematográfica del flow_director).

    Si flow_spec is None → fallback Ken Burns 2D directo (sin DepthFlow).
    El mismo flow_spec se aplica a TODAS las imágenes del capítulo.

    Distribución temporal: por anchor si narration_anchors + timestamps_path
    están disponibles y matchean correctamente; uniforme como fallback.

    Chat 29 #175 — start_offset_sec: dónde arranca este segmento dentro del
    audio del cap (>0 cuando es Flux post-Veo en un cap híbrido). Default
    0.0 = cubre el cap entero (comportamiento Flux puro pre-chat29).
    """
    assert FFMPEG is not None
    work_dir.mkdir(parents=True, exist_ok=True)
    n = len(images)
    if n == 0:
        raise ValueError("Capítulo Flux sin imágenes")

    # Calcular duración por imagen: por anchor si hay datos, uniforme si no
    per_image_list: list[float] | None = None
    if narration_anchors and timestamps_path and len(narration_anchors) == n:
        per_image_list = _compute_durations_from_anchors(
            narration_anchors, timestamps_path, total_duration,
            start_offset_sec=start_offset_sec,
        )
        if per_image_list is None:
            error_handler.log_warning(
                PipelineStage.ASSEMBLY,
                f"[flux_visual] anchor matching falló — fallback uniforme",
            )

    if per_image_list is None:
        per_image_list = [total_duration / n] * n

    # Log de durations (debugging)
    error_handler.log_info(
        PipelineStage.ASSEMBLY,
        f"[flux_visual] durations: " + ", ".join(f"{d:.2f}s" for d in per_image_list),
    )

    mini_clips: list[Path] = [None] * n  # type: ignore

    def _process_one(idx: int, img: Path) -> tuple[int, Path, str]:
        """Procesa 1 imagen → mini clip. Devuelve (idx, path, mode_used)."""
        mini = work_dir / f"_mini_{idx:02d}.mp4"
        duration = per_image_list[idx - 1]   # idx es 1-indexed
        if flow_spec is None:
            build_kenburns_fallback(
                image_path=img, output_path=mini, duration=duration,
                width=width, height=height, fps=fps,
            )
            return idx, mini, "kenburns"
        mode = build_animated_clip(
            image_path=img, output_path=mini, duration=duration,
            flow_spec=flow_spec, width=width, height=height, fps=fps,
        )
        return idx, mini, mode

    # Paralelización: 3 subprocess concurrentes (3080 Ti soporta holgado)
    from concurrent.futures import ThreadPoolExecutor, as_completed
    max_workers = min(4, n)  # no más workers que imágenes
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {
            pool.submit(_process_one, i, img): i
            for i, img in enumerate(images, start=1)
        }
        for future in as_completed(futures):
            idx, mini, mode = future.result()
            mini_clips[idx - 1] = mini  # preserva orden
            if mode == "kenburns" and flow_spec is not None:
                print(f"     ↩  depthflow→kenburns ({images[idx-1].name})")

    # Concat demuxer
    concat_file = work_dir / "_kb_concat.txt"
    concat_file.write_text(
        "\n".join(f"file '{m.resolve()}'" for m in mini_clips),
        encoding="utf-8",
    )
    cmd = [
        FFMPEG, "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_file),
        "-c", "copy",
        str(out_path),
    ]
    result = _run_cmd(cmd, timeout=180)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg concat flux falló: {result.stderr[-300:]}")

    # Cleanup mini-clips
    for m in mini_clips:
        m.unlink(missing_ok=True)
    concat_file.unlink(missing_ok=True)
    return out_path


def _concat_visual_clips(
    clips: list[Path], output_path: Path,
    video_width: int, video_height: int, fps: int, work_dir: Path,
) -> Path:
    """
    Concatena 2+ clips MP4 visuales (sin audio) en uno solo (chat 29 #175).

    Usado por el branch híbrido de _build_chapter_segment para encadenar el
    clip Veo + el slideshow Flux DepthFlow dentro de un mismo cap.

    Por qué filter_complex y NO -c copy:
      - Veo MP4: H.264 + AAC, 1080×1920, fps variable.
      - DepthFlow MP4: H.264 sin audio, 1080×1920, fps fijo.
      - Sample rates / encoding flags pueden diferir → concat demuxer +
        -c copy fallaría con "Non-monotonous DTS" o "different codec params".
      - Re-encode con filter_complex concat uniforma todo a H.264 + yuv420p
        + fps fijo + setsar=1 (clave: sin setsar los Veo y DepthFlow pueden
        tener Sample Aspect Ratio distinto y rompen el concat).

    Output: MP4 sin audio (concat=n=N:v=1:a=0). El audio se mezcla en
    _build_chapter_segment después con el sync_map narration mp3.

    Args:
        clips: 2+ MP4s a concatenar en orden.
        output_path: destino del MP4 concatenado.
        video_width/height/fps: parámetros canónicos del cap.
        work_dir: incluido por consistencia con el módulo (no se usa
            internamente — no hay archivos intermedios).
    """
    assert FFMPEG is not None
    if len(clips) < 2:
        raise ValueError(
            f"_concat_visual_clips necesita 2+ clips, llegaron {len(clips)}"
        )
    for c in clips:
        if not c.exists():
            raise FileNotFoundError(
                f"_concat_visual_clips: clip no encontrado: {c}"
            )

    inputs: list[str] = []
    for c in clips:
        inputs += ["-i", str(c)]

    # Filter_complex: cada video se escala+padea uniforme, después concat.
    # pad con (ow-iw)/2:(oh-ih)/2 centra el frame si la relación cambió.
    n = len(clips)
    filter_parts: list[str] = []
    for i in range(n):
        filter_parts.append(
            f"[{i}:v]scale={video_width}:{video_height}:"
            f"force_original_aspect_ratio=decrease,"
            f"pad={video_width}:{video_height}:(ow-iw)/2:(oh-ih)/2,"
            f"fps={fps},setsar=1[v{i}]"
        )
    concat_inputs = "".join(f"[v{i}]" for i in range(n))
    filter_parts.append(f"{concat_inputs}concat=n={n}:v=1:a=0[outv]")
    filter_complex = ";".join(filter_parts)

    cmd = [
        FFMPEG, "-y", *inputs,
        "-filter_complex", filter_complex,
        "-map", "[outv]",
        "-c:v", "libx264",
        "-r", str(fps),
        "-pix_fmt", "yuv420p",
        str(output_path),
    ]
    result = _run_cmd(cmd, timeout=300)
    if result.returncode != 0:
        raise RuntimeError(
            f"_concat_visual_clips falló: {result.stderr[-300:]}"
        )
    return output_path


def _build_chapter_segment(
    plan: ChapterPlan, segment_path: Path, work_dir: Path,
    *, hook_text: str | None, no_subs: bool, video_width: int,
    video_height: int, fps: int,
    flow_spec: FlowSpec | None = None,
    reuse_visuals: bool = False,
) -> Path:
    """
    Genera UN segmento MP4 completo de un capítulo (visual + audio + subs).
    Aplica loop fix (-stream_loop) si audio > clip; padding si clip > audio.
    Si engine='flux' y hay flow_spec, usa DepthFlow 2.5D guiado.

    reuse_visuals: si True y el clip visual base (flux_visual / hybrid_visual)
    ya existe en work_dir, NO se regenera (se reutiliza el DepthFlow/parallax ya
    horneado). Usado para re-quemar subtítulos sin re-correr DepthFlow.
    """
    assert FFMPEG is not None
    is_first = plan.is_first
    apply_hook = is_first and bool(hook_text)
    pre_pad = HOOK_DURATION if apply_hook else 0.0

    # ─── Visual base (clip MP4 sin audio) ───
    if plan.engine == "veo":
        veo_clip = plan.asset_paths[0]

        hybrid_path = work_dir / f"{plan.chapter_id}_hybrid_visual.mp4"
        if plan.supplemental_paths and reuse_visuals and hybrid_path.exists():
            # Re-burn: reutilizar el híbrido Veo+Flux ya horneado (sin DepthFlow).
            base_clip = hybrid_path
            print(f"  [fase2b] {plan.chapter_id} reuse-visuals: "
                  f"{hybrid_path.name} (sin DepthFlow)")
        elif plan.supplemental_paths:
            # ═══ HÍBRIDO chat 29 #175 ═══════════════════════════════
            # Concat Veo + DepthFlow de supplementals Flux dentro del cap.
            # Mide la duración REAL del clip Veo (fal.ai Veo 3.1 Lite puede
            # variar ±0.2s respecto al nominal 8.0s).
            veo_actual_dur = _get_duration(veo_clip)
            flux_segment_dur = plan.audio_duration - veo_actual_dur

            if flux_segment_dur < 1.0:
                # Edge defensivo: con MIN_FLUX_EXTRAS=4 + audio cap ≥45s nunca
                # se activa (flux_segment ≥ 37s). El branch existe por seguridad
                # contra runtime drift del clip Veo o caps anormalmente cortos.
                error_handler.log_warning(
                    PipelineStage.ASSEMBLY,
                    f"[{plan.chapter_id}] flux_segment_dur={flux_segment_dur:.2f}s "
                    f"<1.0s — usando solo Veo (legacy loop)",
                )
                base_clip = veo_clip
            else:
                # Render del segmento Flux (slideshow DepthFlow de supplementals).
                # start_offset_sec mueve la ventana de anchors según veo_position.
                flux_visual_path = work_dir / f"{plan.chapter_id}_flux_supp.mp4"
                offset = veo_actual_dur if plan.veo_position == "start" else 0.0
                _build_flux_visual(
                    images=plan.supplemental_paths,
                    out_path=flux_visual_path,
                    total_duration=flux_segment_dur,
                    width=video_width,
                    height=video_height,
                    fps=fps,
                    work_dir=work_dir,
                    art_profile=plan.art_profile,
                    flow_spec=flow_spec,
                    narration_anchors=plan.supplemental_anchors,
                    timestamps_path=plan.timestamps_path,
                    start_offset_sec=offset,
                )

                # Concat Veo + Flux según veo_position. Output: base_clip de
                # duración ≈ audio_duration → needs_video_loop quedará False
                # (el bug #175 del loop NO se activa).
                base_clip = work_dir / f"{plan.chapter_id}_hybrid_visual.mp4"
                clips_order = (
                    [veo_clip, flux_visual_path]
                    if plan.veo_position == "start"
                    else [flux_visual_path, veo_clip]
                )
                _concat_visual_clips(
                    clips=clips_order,
                    output_path=base_clip,
                    video_width=video_width,
                    video_height=video_height,
                    fps=fps,
                    work_dir=work_dir,
                )
                print(
                    f"  [fase2b] {plan.chapter_id} híbrido veo+flux: "
                    f"Veo {veo_actual_dur:.1f}s @ pos={plan.veo_position} + "
                    f"{len(plan.supplemental_paths)} Flux supps "
                    f"({flux_segment_dur:.1f}s)"
                )
        else:
            # Legacy: 1 clip Veo solo (cap veo sin supplementals — comportamiento
            # pre-chat29 o topic con supps todos failed). Con audio > clip, el
            # branch común aplica -stream_loop -1 (bug #175 visible).
            base_clip = veo_clip

    elif plan.engine == "flux":
        base_clip = work_dir / f"{plan.chapter_id}_flux_visual.mp4"
        if reuse_visuals and base_clip.exists():
            # Re-burn: reutilizar el slideshow DepthFlow ya horneado.
            print(f"  [fase2b] {plan.chapter_id} reuse-visuals: "
                  f"{base_clip.name} (sin DepthFlow)")
        else:
            _build_flux_visual(
                plan.asset_paths, base_clip, plan.audio_duration,
                video_width, video_height, fps, work_dir, plan.art_profile,
                flow_spec=flow_spec,
                narration_anchors=plan.narration_anchors,
                timestamps_path=plan.timestamps_path,
            )
    else:
        raise ValueError(f"engine desconocido: {plan.engine}")

    clip_duration = _get_duration(base_clip)
    effective_audio = plan.audio_duration + pre_pad
    target_dur = max(effective_audio, clip_duration)
    needs_video_loop = effective_audio > clip_duration
    needs_audio_pad = clip_duration > effective_audio

    # ─── Subs ASS (desde timestamps pre-existentes) ───
    # FIX subs fonéticos (CAMINO B): el forced-alignment corrió sobre el texto
    # NORMALIZADO para TTS, así que los timestamps/alignment traen el texto
    # fonético (años expandidos, nombres EN fonetizados). Remapeamos esos timings
    # al texto ORIGINAL legible (plan.narration) vía diff token-a-token y armamos
    # el .ass con karaoke por PALABRA (_build_ass_from_words). El switch desde la
    # rama por sílaba (_build_ass_from_syllables) es INTENCIONAL — Omar prefiere
    # el karaoke por palabra (sin el efecto de la sílaba agrandándose).
    subs_path: Path | None = None
    if not no_subs and plan.timestamps_path and plan.timestamps_path.exists():
        subs_path = work_dir / f"{plan.chapter_id}_subs.ass"
        norm_words = json.loads(plan.timestamps_path.read_text(encoding="utf-8"))

        original_text = (plan.narration or "").strip()
        if original_text:
            words = remap_words_to_original(original_text, norm_words)
            if not words:
                # Remap vacío (caso patológico) → usar normalizado como red de
                # seguridad para no perder subtítulos.
                words = norm_words
        else:
            # Sin narración original en el script (no debería pasar en LONG) →
            # fallback al texto normalizado tal cual.
            words = norm_words

        _build_ass_from_words(
            words=words,
            output_path=subs_path,
            audio_duration=plan.audio_duration + pre_pad,
            video_width=video_width,
            video_height=video_height,
            hook_text=hook_text if apply_hook else None,
            hook_duration=HOOK_DURATION,
            pre_pad=pre_pad,
        )
    elif apply_hook and not no_subs:
        # Hook sin timestamps: igual generamos un ASS solo con hook
        subs_path = work_dir / f"{plan.chapter_id}_hook_only.ass"
        _build_ass_from_words(
            words=[],
            output_path=subs_path,
            audio_duration=plan.audio_duration + pre_pad,
            video_width=video_width,
            video_height=video_height,
            hook_text=hook_text,
            hook_duration=HOOK_DURATION,
            pre_pad=pre_pad,
        )

    # ─── Filtro de video ───
    vf_parts = [
        f"scale={video_width}:{video_height}:force_original_aspect_ratio=decrease",
        f"pad={video_width}:{video_height}:(ow-iw)/2:(oh-ih)/2",
    ]
    if subs_path is not None and subs_path.stat().st_size > 0:
        vf_parts.append(f"ass='{_escape_ass_path_for_ffmpeg(subs_path)}'")
    vf = ",".join(vf_parts)

    # ─── Filtro de audio (delay para hook + padding final) ───
    af_parts: list[str] = []
    if pre_pad > 0:
        delay_ms = int(pre_pad * 1000)
        af_parts.append(f"adelay={delay_ms}|{delay_ms}")
    if needs_audio_pad:
        silence = clip_duration - effective_audio
        af_parts.append(f"apad=pad_dur={silence:.3f}")

    cmd: list[str] = [FFMPEG, "-y"]
    if needs_video_loop:
        cmd += ["-stream_loop", "-1"]
    cmd += [
        "-i", str(base_clip),
        "-i", str(plan.audio_path),
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-c:v", "libx264",
        "-c:a", "aac",
        "-b:a", "192k",
    ]
    if af_parts:
        cmd += ["-af", ",".join(af_parts)]
    cmd += [
        "-t", f"{target_dur:.3f}",
        "-vf", vf,
        "-r", str(fps),
        "-pix_fmt", "yuv420p",
        str(segment_path),
    ]

    result = _run_cmd(cmd, timeout=600)
    if result.returncode != 0:
        raise RuntimeError(
            f"FFmpeg segmento {plan.chapter_id} falló: {result.stderr[-400:]}"
        )
    return segment_path


# ═══════════════════════════════════════════════════════════════
#  Resolución de assets desde manifest + sync_map
# ═══════════════════════════════════════════════════════════════

def _resolve_chapter_paths(
    chapter_manifest: dict, video_id: str,
) -> tuple[str, list[Path]]:
    """
    Devuelve (engine, asset_paths) para un capítulo según el manifest.
    veo → 1 clip MP4 (con fallback a fallback_img si status != ok)
    flux → lista de imágenes PNG ordenadas por index
    """
    engine = chapter_manifest.get("engine", "").lower()

    if engine == "flux":
        images = chapter_manifest.get("images", [])
        # Ordenar por index, filtrar los que tienen path
        ordered = sorted(
            [img for img in images if img.get("path")],
            key=lambda x: x.get("index", 0),
        )
        paths = [OUTPUT_DIR / img["path"] for img in ordered]
        missing = [p for p in paths if not p.exists()]
        if missing:
            raise FileNotFoundError(
                f"[{chapter_manifest.get('id')}] imágenes faltantes: "
                f"{[m.name for m in missing[:3]]}"
            )
        return "flux", paths

    if engine == "veo":
        clips = chapter_manifest.get("clips", [])
        if not clips:
            raise ValueError(f"[{chapter_manifest.get('id')}] sin clips en manifest")
        # Tomamos el primer clip ok. Si hay múltiples clips Veo en un cap,
        # el ensamblaje 1-a-1 con narración requiere lógica más fina; por
        # ahora asumimos 1 clip por cap (caso SS Poet ch01/ch08).
        primary = clips[0]
        path = OUTPUT_DIR / primary["path"]
        if not path.exists():
            raise FileNotFoundError(
                f"[{chapter_manifest.get('id')}] clip no encontrado: {path}"
            )
        # Si el status fue fallback, el path apunta a una imagen → tratar como flux 1-img
        status = primary.get("status", "ok")
        if status in ("kenburns_fallback", "technical_fallback") or path.suffix.lower() == ".png":
            return "flux", [path]
        return "veo", [path]

    raise ValueError(
        f"[{chapter_manifest.get('id')}] engine no soportado: '{engine}'"
    )


def _load_script_lookup(video_id: str) -> dict[str, dict[str, Any]]:
    """
    Carga data/scripts/{video_id}.json y devuelve un mapping
        chapter_id ('chXX') → {narration, image_prompt, art_profile,
                                render_engine, label, narration_anchors}

    Soporta SHORT (variations[best].scenes[]) y LONG (chapters[]).
    Si el archivo no existe, devuelve {} (el director caerá a fallbacks estáticos).
    """
    script_path = Path("data") / "scripts" / f"{video_id}.json"
    if not script_path.exists():
        print(f"  ⚠️  data/scripts/{video_id}.json no existe — flow_director sin contexto")
        return {}

    raw = json.loads(script_path.read_text(encoding="utf-8"))
    video_type = raw.get("video_type", "short")

    lookup: dict[str, dict[str, Any]] = {}

    if video_type == "long":
        items = raw.get("chapters", [])
        num_key = "chapter_number"
    else:
        variations = raw.get("variations", [])
        if not variations:
            return {}
        chosen_num = raw.get("best") or 1
        chosen = next(
            (v for v in variations if v.get("variation_number") == chosen_num),
            variations[0],
        )
        items = chosen.get("scenes", [])
        num_key = "scene_number"

    for item in items:
        n = item.get(num_key)
        if n is None:
            continue
        cid = f"ch{int(n):02d}"
        # image_prompt puede venir como str o list[str] (LONG); normalizamos a str
        ip = item.get("image_prompt") or item.get("image_prompts") or ""
        if isinstance(ip, list):
            ip = " | ".join(str(x) for x in ip if x)

        # Extraer anchors en orden desde image_prompts[] (LONG flux con N imgs)
        anchors: list[str] = []
        raw_image_prompts = item.get("image_prompts")
        if isinstance(raw_image_prompts, list):
            for ip_item in raw_image_prompts:
                if isinstance(ip_item, dict):
                    a = (ip_item.get("narration_anchor") or "").strip()
                    if a:
                        anchors.append(a)

        lookup[cid] = {
            "narration": str(item.get("narration", "")).strip(),
            "image_prompt": str(ip).strip(),
            "art_profile": str(item.get("art_profile") or ""),
            "render_engine": str(item.get("render_engine", "")).lower(),
            "label": str(item.get("label", "")),
            "narration_anchors": anchors,
        }
    return lookup


def _load_music_map(video_id: str) -> dict[str, dict[str, Any]] | None:
    """
    Carga output/audio/{video_id}/music_map.json y devuelve un mapping
        chapter_id ('chXX') → {track_id, mp3_path, match_source, ...}

    El music_map es emitido por m07_music_director. Si no existe, fase2b
    procede SIN música (compat con topics legacy pre-PR 2.B).

    El path en `mp3_path` es relativo a BASE_DIR (ver m07 _persist_music_map).

    Returns:
        dict {ch_id: track_info} o None si no existe music_map.
    """
    mm_path = OUTPUT_DIR / "audio" / video_id / "music_map.json"
    if not mm_path.exists():
        return None

    try:
        raw = json.loads(mm_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        print(f"  ⚠  music_map.json ilegible ({type(e).__name__}): "
              f"procediendo sin música")
        return None

    tracks = raw.get("tracks_by_chapter", {})
    if not tracks:
        return None

    return tracks


def _resolve_music_track_path(track_info: dict[str, Any]) -> Path | None:
    """
    Resuelve el path absoluto del mp3 a partir del entry de music_map.
    Devuelve None si el track fue skipped o el mp3 no existe en disco.
    """
    if track_info.get("match_source") == "skipped":
        return None

    mp3_rel = track_info.get("mp3_path")
    if not mp3_rel:
        return None

    mp3_abs = BASE_DIR / mp3_rel
    if not mp3_abs.exists():
        print(f"  ⚠  Track en music_map no existe en disco: {mp3_abs}")
        return None

    return mp3_abs


def _build_music_piece_for_chapter(
    track_path: Path | None,
    cap_duration_sec: float,
    output_path: Path,
    sample_rate: int = 44100,
    piece_volume: float = 1.0,
) -> Path:
    """
    Genera 1 piece WAV del largo exacto del cap.

    Si track_path is None → silencio puro del largo del cap.
    Si track_path existe → loop+trim del mp3 al largo del cap.

    chat 39 (piece_volume): pre-atenúa la música del cap a su nivel por-intent
    ANTES de entrar al mix (volumen POR CAP horneado en la pieza). Default 1.0 =
    sin atenuar → ruta byte-idéntica a pre-chat39 (compat). No aplica a silencio.

    Output: WAV PCM 16-bit estéreo @44.1kHz para compatibilidad sidechain.
    """
    assert FFMPEG is not None
    cmd: list[str]

    if track_path is None:
        # Silencio del largo del cap (piece_volume es moot: silencio × k = silencio)
        cmd = [
            FFMPEG, "-y",
            "-f", "lavfi",
            "-i", f"anullsrc=channel_layout=stereo:sample_rate={sample_rate}",
            "-t", f"{cap_duration_sec:.3f}",
            "-c:a", "pcm_s16le",
            str(output_path),
        ]
    else:
        # Loop+trim del mp3 al largo del cap
        # -stream_loop -1 hace loop infinito del input; -t corta a cap_duration_sec
        cmd = [
            FFMPEG, "-y",
            "-stream_loop", "-1",
            "-i", str(track_path),
            "-t", f"{cap_duration_sec:.3f}",
            "-ar", str(sample_rate),
            "-ac", "2",
        ]
        # chat 39: hornear el volumen por-cap solo si difiere de 1.0 (así la ruta
        # default queda idéntica a pre-chat39).
        if piece_volume != 1.0:
            cmd += ["-af", f"volume={piece_volume}"]
        cmd += [
            "-c:a", "pcm_s16le",
            str(output_path),
        ]

    result = _run_cmd(cmd, timeout=120)
    if result.returncode != 0:
        raise RuntimeError(
            f"FFmpeg piece falló para {output_path.name}: "
            f"{result.stderr[-300:]}"
        )

    return output_path


def _build_continuous_music_track(
    plans: list[ChapterPlan],
    music_map: dict[str, dict[str, Any]],
    work_dir: Path,
    crossfade_sec: float = MUSIC_CROSSFADE_SEC,
    piece_volumes: dict[str, float] | None = None,
    output_filename: str | None = None,
) -> Path:
    """
    Construye un único WAV continuo del largo total del video, con
    tracks de música encadenados con crossfade en límites de cap.

    Strategy:
    1. Por cada cap (en orden de plans), generar 1 piece WAV del largo
       exacto del cap (silencio si skipped, loop+trim si reused/generated).
    2. Encadenar todos los pieces con acrossfade=d=crossfade_sec via un
       solo filter_complex.

    Args:
        plans: lista de ChapterPlan en orden cronológico.
        music_map: output de _load_music_map().
        work_dir: directorio temporal donde escribir pieces + output.
        crossfade_sec: duración del crossfade entre pieces.
        piece_volumes: chat 39 — dict {chapter_id: volumen} para pre-atenuar la
            música POR CAP (volumen por-intent horneado en la pieza). Si None o un
            cap falta → 1.0 (sin atenuar). El acrossfade entre caps a distinto
            volumen crea la transición natural en la costura (gate de oído de Omar).
        output_filename: chat 39 — nombre del WAV de salida en work_dir. Default
            None → CONTINUOUS_MUSIC_FILENAME. Se pasa distinto en cada llamada
            (ducked vs floor) para que las dos pistas no se pisen.

    Returns:
        Path al WAV continuo en work_dir.
    """
    assert FFMPEG is not None
    work_dir.mkdir(parents=True, exist_ok=True)
    piece_volumes = piece_volumes or {}
    out_name = output_filename or CONTINUOUS_MUSIC_FILENAME

    # ─── Generar pieces individuales por cap ───
    piece_paths: list[Path] = []
    for plan in plans:
        ch_id = plan.chapter_id
        track_info = music_map.get(ch_id)

        if track_info is None:
            print(f"     [{ch_id}] sin entry en music_map → silencio")
            track_path = None
        else:
            track_path = _resolve_music_track_path(track_info)
            if track_path is None:
                src = track_info.get("match_source", "?")
                print(f"     [{ch_id}] {src} → silencio fallback")
            else:
                src = track_info.get("match_source", "?")
                print(f"     [{ch_id}] {src} → {track_path.name} "
                      f"(loop a {plan.audio_duration:.1f}s)")

        piece_path = work_dir / f"_music_piece_{ch_id}.wav"
        _build_music_piece_for_chapter(
            track_path=track_path,
            cap_duration_sec=plan.audio_duration,
            output_path=piece_path,
            piece_volume=piece_volumes.get(ch_id, 1.0),  # chat 39: volumen por-cap
        )
        piece_paths.append(piece_path)

    if not piece_paths:
        raise RuntimeError("No se generaron pieces de música")

    # ─── Encadenar pieces con acrossfade en filter_complex ───
    output_path = work_dir / out_name

    if len(piece_paths) == 1:
        # Caso trivial: 1 cap. Copia directa.
        cmd = [
            FFMPEG, "-y",
            "-i", str(piece_paths[0]),
            "-c:a", "pcm_s16le",
            str(output_path),
        ]
        result = _run_cmd(cmd, timeout=60)
        if result.returncode != 0:
            raise RuntimeError(
                f"FFmpeg single-piece copy falló: {result.stderr[-300:]}"
            )
        for p in piece_paths:
            p.unlink(missing_ok=True)
        return output_path

    # Caso N > 1: filter_complex con acrossfade encadenado.
    # Sintaxis acrossfade: [a0][a1]acrossfade=d=2[a01]; [a01][a2]acrossfade=d=2[a02]; ...
    inputs_cmd: list[str] = []
    for p in piece_paths:
        inputs_cmd += ["-i", str(p)]

    filter_parts: list[str] = []
    prev_label = "0:a"
    for i in range(1, len(piece_paths)):
        next_input = f"{i}:a"
        out_label = f"a{i:02d}" if i < len(piece_paths) - 1 else "out"
        filter_parts.append(
            f"[{prev_label}][{next_input}]acrossfade=d={crossfade_sec}:"
            f"c1=tri:c2=tri[{out_label}]"
        )
        prev_label = out_label

    filter_complex = ";".join(filter_parts)

    cmd = [FFMPEG, "-y"]
    cmd += inputs_cmd
    cmd += [
        "-filter_complex", filter_complex,
        "-map", "[out]",
        "-c:a", "pcm_s16le",
        str(output_path),
    ]

    result = _run_cmd(cmd, timeout=300)
    if result.returncode != 0:
        raise RuntimeError(
            f"FFmpeg acrossfade chain falló: {result.stderr[-500:]}"
        )

    for p in piece_paths:
        p.unlink(missing_ok=True)

    return output_path


def _resolve_music_volumes(
    plans: list[ChapterPlan],
    mixing: dict,
    music_map: dict[str, dict[str, Any]],
) -> tuple[dict[str, float], dict[str, float]]:
    """
    chat 40 — el volumen de música es propiedad del TRACK, no del intent ni del
    video. Lee {music_volume, music_volume_floor} del audio_library/<track>.json
    (al lado del mp3, via music_map). Si el json no tiene las claves → cae al BASE
    del perfil (music_volume / music_volume_floor del sync_map mixing). Así los
    tracks no calibrados quedan en 0.26/0.16 sin tocarse.

    Por qué por-track y no por-intent (chat 39, eliminado): el 0.08 sale del masking
    espectral del mp3 puntual; pinearlo al intent asume que detrás de "shock" siempre
    está ese mismo track (falso al cambiar de nicho). El número viaja con el track.

    Devuelve (ducked_by_cap, floor_by_cap): por chapter_id, el music_volume y el
    music_volume_floor efectivos.
    """
    base_vol = float(mixing.get("music_volume", 0.25))
    base_floor = float(mixing.get("music_volume_floor", 0.0))
    ducked: dict[str, float] = {}
    floor: dict[str, float] = {}
    for p in plans:
        vol, flr = base_vol, base_floor
        track_info = music_map.get(p.chapter_id)
        if track_info:
            mp3_abs = _resolve_music_track_path(track_info)
            if mp3_abs is not None:
                json_path = mp3_abs.with_suffix(".json")
                if json_path.exists():
                    try:
                        meta = json.loads(json_path.read_text(encoding="utf-8"))
                        if "music_volume" in meta:
                            vol = float(meta["music_volume"])
                        if "music_volume_floor" in meta:
                            flr = float(meta["music_volume_floor"])
                    except (json.JSONDecodeError, OSError, ValueError) as e:
                        print(f"     ⚠ [{p.chapter_id}] json del track ilegible "
                              f"({type(e).__name__}) → base {base_vol}/{base_floor}")
        ducked[p.chapter_id] = vol
        floor[p.chapter_id] = flr
    return ducked, floor


def _classify_uncalibrated_tracks(
    plans: list[ChapterPlan],
    music_map: dict[str, dict[str, Any]],
) -> tuple[list[tuple[str, str]], list[tuple[str, str]]]:
    """
    chat 40 — detector "track sin calibrar" (print-only en el caller). Clasifica los
    caps cuyo track NO tiene la clave music_volume en su json (usan BASE):
      - generated + sin clave → uncal_generated (track nuevo, warning FUERTE).
      - reused    + sin clave → uncal_reused    (library en base, nota suave).
    Devuelve (uncal_generated, uncal_reused) como listas de (chapter_id, track_id).

    Robusto: mira PRESENCIA de la clave, NO el valor (un track calibrado justo a 0.26
    no es falso positivo). Re-lee los jsons de los tracks (costo despreciable, 7
    archivos chicos) para NO tocar la firma de _resolve_music_volumes (ya validada).
    NO toca la lógica de mezcla ni el sidechain.
    """
    uncal_generated: list[tuple[str, str]] = []
    uncal_reused: list[tuple[str, str]] = []
    for p in plans:
        ti = music_map.get(p.chapter_id) or {}
        if not ti or ti.get("match_source") == "skipped":
            continue
        tid = ti.get("track_id", "?")
        mp3 = _resolve_music_track_path(ti)
        has_key = False
        if mp3 is not None:
            jp = mp3.with_suffix(".json")
            if jp.exists():
                try:
                    has_key = "music_volume" in json.loads(
                        jp.read_text(encoding="utf-8"))
                except (json.JSONDecodeError, OSError):
                    has_key = False
        if not has_key:
            if ti.get("match_source") == "generated":
                uncal_generated.append((p.chapter_id, tid))
            else:
                uncal_reused.append((p.chapter_id, tid))
    return uncal_generated, uncal_reused


def _mix_music_into_video(
    video_path: Path,
    music_path: Path,
    sync_map: dict,
    output_path: Path,
    music_floor_path: Path | None = None,
) -> Path:
    """
    Mezcla música con ducking sidechain sobre la narración del video.

    Lee los 6 params de mixing del sync_map (escritos por audio_manager):
        music_volume, duck_threshold, duck_ratio, duck_attack_ms, duck_release_ms

    Estrategia ffmpeg:
        [0:a] = narración del MP4 (será preservada + detector sidechain)
        [1:a] = música continua del WAV
        - música a volumen base
        - sidechain detecta voz, comprime música
        - amix de narración + música ducked
        - video del MP4 se copia sin re-encodear

    Args:
        video_path: MP4 con narración muxeada (no debe tener música).
        music_path: WAV continuo del paso A (rama ducked).
        sync_map: dict cargado de sync_map.json (para leer params de mixing).
        output_path: MP4 final con música ducked.
        music_floor_path: chat 39 — si se pasa, activa el modo VOLUMEN POR-CAP:
            la música llega PRE-ATENUADA por cap en DOS WAVs (music_path = pista
            ducked-source, music_floor_path = pista floor-source), cada uno con su
            volumen por-intent ya horneado. El filtro aplica volume=1.0 (ya
            horneado) y manda SOLO la rama ducked al sidechain; la rama floor va
            directa. Los params del sidechain (threshold/ratio/attack/release)
            quedan IDÉNTICOS al chat 32. Si es None → ruta chat 32 original
            (1 WAV, asplit, volume del sync_map) intacta.

    Returns:
        Path al MP4 final.
    """
    assert FFMPEG is not None

    mixing = sync_map.get("mixing", {})
    music_volume = float(mixing.get("music_volume", 0.25))
    # CHAT 32: piso de música sin ducking. Default 0.0 (= sin floor) para compat
    # con perfiles que no lo definieron.
    music_volume_floor = float(mixing.get("music_volume_floor", 0.0))
    duck_threshold = float(mixing.get("duck_threshold", 0.03))
    duck_ratio = float(mixing.get("duck_ratio", 8))
    duck_attack_ms = float(mixing.get("duck_attack_ms", 80))
    duck_release_ms = float(mixing.get("duck_release_ms", 200))

    pad_sec = INITIAL_SILENCE_SEC   # CHAT 32

    print(f"     mixing params: vol={music_volume}, floor={music_volume_floor}, "
          f"thr={duck_threshold}, ratio={duck_ratio}, "
          f"atk={duck_attack_ms}ms, rel={duck_release_ms}ms, "
          f"init_silence={pad_sec}s")

    pad_ms = int(pad_sec * 1000)

    if music_floor_path is None:
        # ─── RUTA CHAT 32 (volumen global) — INTACTA ───
        # filter_complex breakdown (CHAT 32: rama-piso + padding inicial):
        # [0:v] = video → tpad clone primer frame por pad_sec al inicio → [v_pad]
        # [0:a] = audio narración → adelay pad_sec → asplit en 2 → [narr_main][narr_sc]
        # [1:a] = música → asplit en 2:
        #   rama-ducked:    volume(music_volume) → sidechaincompress vs [narr_sc] → [music_ducked]
        #   rama-floor:     volume(music_volume_floor) (SIN ducking) → [music_floor]
        # amix(narr_main, music_ducked, music_floor) → [mixed]
        filter_complex = (
            f"[0:v]tpad=start_duration={pad_sec}:start_mode=clone[v_pad];"
            f"[0:a]adelay={pad_ms}|{pad_ms},aresample=44100,asplit=2[narr_main][narr_sc];"
            f"[1:a]aresample=44100,asplit=2[music_a][music_b];"
            f"[music_a]volume={music_volume}[music_lvl];"
            f"[music_lvl][narr_sc]sidechaincompress="
            f"threshold={duck_threshold}:"
            f"ratio={duck_ratio}:"
            f"attack={duck_attack_ms}:"
            f"release={duck_release_ms}"
            f"[music_ducked];"
            f"[music_b]volume={music_volume_floor}[music_floor];"
            f"[narr_main][music_ducked][music_floor]amix=inputs=3:duration=longest:"
            f"dropout_transition=0:normalize=0[mixed]"
        )
        cmd = [
            FFMPEG, "-y",
            "-i", str(video_path),
            "-i", str(music_path),
            "-filter_complex", filter_complex,
            "-map", "[v_pad]",          # CHAT 32: usar el video padeado, no 0:v directo
            "-map", "[mixed]",
            "-c:v", "libx264",          # CHAT 32: tpad re-encodea → ya no podemos copy
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            str(output_path),
        ]
    else:
        # ─── RUTA CHAT 39 (volumen POR CAP) — música pre-atenuada en 2 WAVs ───
        # El volumen por-intent (p.ej. shock=0.08/0.03) YA está horneado en cada WAV
        # (ver _build_music_piece_for_chapter piece_volume). Acá NO se aplica volume=
        # (sería doble atenuación). El sidechain (threshold/ratio/attack/release) es
        # BYTE-IDÉNTICO al chat 32 — solo cambia de dónde viene la música:
        # [0:v] = video → tpad → [v_pad]
        # [0:a] = narración → adelay → asplit → [narr_main][narr_sc]
        # [1:a] = música ducked-source (vol por-cap horneado) → sidechaincompress vs [narr_sc]
        # [2:a] = música floor-source  (vol por-cap horneado) → directa (sin ducking)
        # amix(narr_main, music_ducked, music_floor) → [mixed]
        print(f"     CHAT 39: volumen POR CAP (música pre-atenuada en 2 WAVs, "
              f"sidechain intacto)")
        filter_complex = (
            f"[0:v]tpad=start_duration={pad_sec}:start_mode=clone[v_pad];"
            f"[0:a]adelay={pad_ms}|{pad_ms},aresample=44100,asplit=2[narr_main][narr_sc];"
            f"[1:a]aresample=44100[music_ducked_src];"
            f"[music_ducked_src][narr_sc]sidechaincompress="
            f"threshold={duck_threshold}:"
            f"ratio={duck_ratio}:"
            f"attack={duck_attack_ms}:"
            f"release={duck_release_ms}"
            f"[music_ducked];"
            f"[2:a]aresample=44100[music_floor];"
            f"[narr_main][music_ducked][music_floor]amix=inputs=3:duration=longest:"
            f"dropout_transition=0:normalize=0[mixed]"
        )
        cmd = [
            FFMPEG, "-y",
            "-i", str(video_path),
            "-i", str(music_path),
            "-i", str(music_floor_path),
            "-filter_complex", filter_complex,
            "-map", "[v_pad]",
            "-map", "[mixed]",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            str(output_path),
        ]

    print(f"     ejecutando ffmpeg sidechain mix...")
    result = _run_cmd(cmd, timeout=900)
    if result.returncode != 0:
        raise RuntimeError(
            f"FFmpeg sidechain mix falló: {result.stderr[-500:]}"
        )

    return output_path


def _dispatch_flow_specs(plans: list[ChapterPlan]) -> dict[str, FlowSpec]:
    """
    Llama a flow_director.select_movements_batch() UNA SOLA VEZ pasándole
    todas las escenas que necesitan FlowSpec para DepthFlow (ordenadas por
    chapter_id para que el director vea el arco narrativo completo).

    Refactor chat 19: ya no agrupa por art_profile (catálogo desconectado).
    Una sola batch call por video.

    Chat 29 #175: incluye caps veo HÍBRIDOS (engine=="veo" + supplementals).
    Sus PNGs Flux supplementals necesitan FlowSpec para animarse con DepthFlow.
    Caps veo legacy SIN supps NO entran (movimiento embebido en el clip Veo).

    Devuelve {chapter_id: FlowSpec}.
    """
    plans_needing_spec = [
        p for p in plans
        if p.engine == "flux"
        or (p.engine == "veo" and p.supplemental_paths)
    ]
    if not plans_needing_spec:
        return {}

    # Ordenar por chapter_id para que el director vea el arco narrativo
    plans_needing_spec.sort(key=lambda p: p.chapter_id)

    scenes_payload: list[dict] = []
    for i, p in enumerate(plans_needing_spec, start=1):
        # Chat 29 #175: hint semántico "hibrido" para que el director sepa
        # que el cap mezcla Veo + Flux. Permite (en el futuro) elegir
        # movimientos que complementen el motion de Veo en vez de competir.
        label = p.label or ("hibrido" if p.engine == "veo" else "desarrollo")
        scenes_payload.append({
            "scene_number": i,
            "label": label,
            "narration": p.narration,
            "image_prompt": p.image_prompt,
        })

    print(f"  🎬 flow_director: {len(plans_needing_spec)} escena(s) "
          f"({', '.join(p.chapter_id for p in plans_needing_spec)})...")

    try:
        specs = select_movements_batch(scenes_payload)
    except Exception as e:
        print(f"     ⚠ flow_director falló ({type(e).__name__}: {e}) → "
              f"fallback dolly estático")
        specs = [
            FlowSpec(
                movement="dolly", intensity=0.7, steady=0.5,
                dof=True, reasoning="fallback global",
            )
            for _ in plans_needing_spec
        ]

    # Mapear de vuelta a chapter_id (orden preservado por sort + zip)
    flow_specs: dict[str, FlowSpec] = {}
    for p, spec in zip(plans_needing_spec, specs):
        flow_specs[p.chapter_id] = spec
        print(f"     [{p.chapter_id}] {spec['movement']} "
              f"(i={spec['intensity']:.2f}, s={spec['steady']:.2f}, "
              f"dof={spec['dof']})")

    return flow_specs


def _build_plans(
    sync_map: dict, manifest: dict, video_id: str, audio_dir: Path,
    script_lookup: dict[str, dict[str, str]],
) -> list[ChapterPlan]:
    """Cruza sync_map (audio + timestamps) con manifest (assets) por chapter_id."""
    sm_chapters = {c["id"]: c for c in sync_map.get("chapters", [])}
    mf_chapters = {c["id"]: c for c in manifest.get("chapters", [])}

    common_ids = sorted(set(sm_chapters) & set(mf_chapters))
    only_audio = sorted(set(sm_chapters) - set(mf_chapters))
    only_assets = sorted(set(mf_chapters) - set(sm_chapters))
    if only_audio or only_assets:
        print(f"  ⚠️  IDs solo en audio: {only_audio}")
        print(f"  ⚠️  IDs solo en assets: {only_assets}")

    plans: list[ChapterPlan] = []
    for i, cid in enumerate(common_ids):
        sm = sm_chapters[cid]
        mf = mf_chapters[cid]
        scr = script_lookup.get(cid, {})

        audio_path = audio_dir / sm["audio_path"]
        if not audio_path.exists():
            raise FileNotFoundError(f"[{cid}] audio faltante: {audio_path}")
        ts_path = audio_dir / sm["timestamps_path"]
        # chat 38: alignment al lado del timestamps, mismo audio_dir (NO inventar path).
        align_path = audio_dir / f"{cid}_alignment.json"

        engine, asset_paths = _resolve_chapter_paths(mf, video_id)

        # Híbrido Veo+Flux chat 29 #175: leer supplementals SOLO si engine=="veo".
        # Si después de filtrar (status=="ok" + path en disco) la lista queda
        # vacía, dejamos None para que _build_chapter_segment caiga al branch
        # legacy (1 clip Veo solo, con loop si audio > clip). Caps flux puros
        # ignoran estos campos completamente.
        supp_paths: list[Path] = []
        supp_anchors: list[str] = []
        veo_position = "start"
        if engine == "veo":
            veo_position = mf.get("veo_position", "start")
            supp_images = mf.get("supplemental_images", []) or []
            ordered_supps = sorted(
                [s for s in supp_images
                 if s.get("status") == "ok" and s.get("path")],
                key=lambda x: x.get("index", 0),
            )
            for s in ordered_supps:
                p = OUTPUT_DIR / s["path"]
                if not p.exists():
                    raise FileNotFoundError(
                        f"[{cid}] supplemental PNG no encontrado: {p}"
                    )
                supp_paths.append(p)
                supp_anchors.append((s.get("narration_anchor") or "").strip())

        plans.append(ChapterPlan(
            chapter_id=cid,
            engine=engine,
            audio_path=audio_path,
            audio_duration=float(sm["duration_sec"]),
            asset_paths=asset_paths,
            timestamps_path=ts_path if ts_path.exists() else None,
            alignment_path=align_path if align_path.exists() else None,
            is_first=(i == 0),
            art_profile=mf.get("art_profile") or scr.get("art_profile") or None,
            narration=scr.get("narration", ""),
            image_prompt=scr.get("image_prompt", ""),
            label=scr.get("label", ""),
            narration_anchors=scr.get("narration_anchors"),
            supplemental_paths=supp_paths if supp_paths else None,
            supplemental_anchors=supp_anchors if supp_anchors else None,
            veo_position=veo_position,
            narrative_intent=sm.get("narrative_intent", "") or "",  # chat 39
        ))
    return plans


# ═══════════════════════════════════════════════════════════════
#  Concatenación final
# ═══════════════════════════════════════════════════════════════

def _concat_segments(
    segments: list[Path],
    final_path: Path,
    work_dir: Path,
    art_profiles: list[str | None],
) -> Path:
    """Concatena segmentos con transiciones. Fallback a hard cut si falla."""
    assert FFMPEG is not None
    assert FFPROBE is not None
    return concat_with_transitions(
        segments=segments,
        final_path=final_path,
        work_dir=work_dir,
        art_profiles=art_profiles,
        ffmpeg=FFMPEG,
        ffprobe=FFPROBE,
    )


# ═══════════════════════════════════════════════════════════════
#  Discovery & batch helpers
# ═══════════════════════════════════════════════════════════════

def _list_pending_for_assembly() -> list[dict]:
    """
    Devuelve topics con status='assets_rendered' (fase2a terminó, fase2b pendiente).
    Ordenados por assets_rendered_at (más viejo primero → FIFO).
    """
    db = load_db()
    pending = [
        t for t in db.get("topics", [])
        if t.get("status") == ASSETS_READY_STATUS
    ]
    pending.sort(key=lambda t: t.get("assets_rendered_at", ""))
    return pending


def _resolve_topic_id_for_video(video_id: str) -> str | None:
    """
    Encuentra el topic_id en la DB cuyo video_id == el dado.
    Como en este pipeline topic_id == video_id, normalmente coincide,
    pero si en el futuro se desacoplan, este helper lo abstrae.
    """
    db = load_db()
    for t in db.get("topics", []):
        if t.get("video_id") == video_id or t.get("id") == video_id:
            return t.get("id")
    return None


def _has_assets_on_disk(video_id: str) -> bool:
    """Check rápido: ¿están los manifests en disco?"""
    sm = OUTPUT_DIR / "audio" / video_id / "sync_map.json"
    mf = OUTPUT_DIR / video_id / "assets" / "assets_manifest.json"
    return sm.exists() and mf.exists()


# ═══════════════════════════════════════════════════════════════
#  Single-video assembly (extraído de main para reuso en batch)
# ═══════════════════════════════════════════════════════════════

def _assemble_one_video(
    video_id: str, *,
    hook: str | None,
    no_subs: bool,
    keep_segments: bool,
    dry_run: bool,
    reuse_visuals: bool = False,
) -> tuple[int, Path | None]:
    """
    Ensambla un único video. Retorna (returncode, final_path | None).
    NO toca topics_db (eso lo hace el caller para mantener responsabilidades claras).
    """
    audio_dir = OUTPUT_DIR / "audio" / video_id
    assets_dir = OUTPUT_DIR / video_id / "assets"
    sync_map_path = audio_dir / "sync_map.json"
    manifest_path = assets_dir / "assets_manifest.json"

    if not sync_map_path.exists():
        print(f"❌ [{video_id}] No existe {sync_map_path}")
        return 1, None
    if not manifest_path.exists():
        print(f"❌ [{video_id}] No existe {manifest_path}")
        return 1, None

    sync_map = json.loads(sync_map_path.read_text(encoding="utf-8"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    script_lookup = _load_script_lookup(video_id)

    plans = _build_plans(sync_map, manifest, video_id, audio_dir, script_lookup)
    if not plans:
        print(f"❌ [{video_id}] Sin capítulos comunes entre sync_map y manifest")
        return 1, None

    print(f"\n{'═' * 60}")
    print(f"  🎬 FASE 2B — {video_id}")
    print(f"{'═' * 60}")
    print(f"  🪝 hook:     {hook or '(ninguno)'}")
    print(f"  📝 subs:     {'OFF' if no_subs else 'ON (karaoke)'}")
    print(f"  📊 capítulos: {len(plans)}")
    total_audio = sum(p.audio_duration for p in plans)
    print(f"  ⏱  duración total estimada: {total_audio:.1f}s ({total_audio / 60:.1f} min)")

    print(f"\n  Plan por capítulo:")
    for p in plans:
        n_assets = len(p.asset_paths)
        kind = f"{n_assets} img(s)" if p.engine == "flux" else "1 clip"
        profile_label = f" [{p.art_profile}]" if p.art_profile else ""
        print(
            f"    [{p.chapter_id}] engine={p.engine:4s} | "
            f"audio={p.audio_duration:5.1f}s | {kind:10s}{profile_label} | "
            f"{'subs+ts' if p.timestamps_path else 'sin timestamps'}"
            f"{' | HOOK' if (p.is_first and hook) else ''}"
        )

    if dry_run:
        print(f"\n  🧪 DRY RUN — nada se ejecutó.\n")
        return 0, None

    # ─── cost_tracker (Gemini Flash del flow_director) ───
    if cost_tracker.current_video is None:
        cost_tracker.start_video(video_id=video_id)
    started_tracker = (cost_tracker.current_video is not None
                       and cost_tracker.current_video.video_id == video_id)

    if reuse_visuals:
        # Re-burn: NO se decide movimiento ni se llama a flow_director (los clips
        # visuales ya están horneados). Se deja el flow_plan.json existente intacto.
        print(f"\n  ♻  reuse-visuals: salteando flow_director (clips ya horneados)")
        flow_specs = {}
    else:
        print(f"\n  🎥 Decidiendo movimientos cinematográficos...")
        flow_specs = _dispatch_flow_specs(plans)

    # Persistir flow_plan para inspección post-corrida (se omite en re-burn para
    # no clobberear el flow_plan.json original con flow_specs vacíos).
    if not reuse_visuals:
        flow_plan_path = OUTPUT_DIR / video_id / "flow_plan.json"
        flow_plan_path.parent.mkdir(parents=True, exist_ok=True)
        flow_plan_data = {
            "video_id": video_id,
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "chapters": [
                {
                    "chapter_id": p.chapter_id,
                    "engine": p.engine,
                    "art_profile": p.art_profile,
                    "audio_duration_sec": round(p.audio_duration, 2),
                    "narration_anchors_count": len(p.narration_anchors) if p.narration_anchors else 0,
                    "flow_spec": (
                        {
                            "movement": flow_specs[p.chapter_id]["movement"],
                            "intensity_base": float(flow_specs[p.chapter_id]["intensity"]),
                            "steady": float(flow_specs[p.chapter_id]["steady"]),
                            "dof": bool(flow_specs[p.chapter_id]["dof"]),
                            "rationale": flow_specs[p.chapter_id].get("rationale", ""),
                        }
                        if p.chapter_id in flow_specs and p.engine == "flux"
                        else None
                    ),
                }
                for p in plans
            ],
        }
        flow_plan_path.write_text(
            json.dumps(flow_plan_data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(f"     💾 flow_plan persistido en {flow_plan_path.name}")

    work_dir = OUTPUT_DIR / video_id / "_fase2b_work"
    work_dir.mkdir(parents=True, exist_ok=True)
    final_path = OUTPUT_DIR / video_id / f"{video_id}_final.mp4"

    segments: list[Path] = []
    for i, plan in enumerate(plans, start=1):
        seg_path = work_dir / f"seg_{i:02d}_{plan.chapter_id}.mp4"
        spec = flow_specs.get(plan.chapter_id)
        spec_label = f" {spec['movement']}" if spec else ""
        print(f"\n  🔧 [{i}/{len(plans)}] {plan.chapter_id} ({plan.engine}{spec_label})...")
        try:
            _build_chapter_segment(
                plan=plan, segment_path=seg_path, work_dir=work_dir,
                hook_text=hook, no_subs=no_subs,
                video_width=pipeline.video_width,
                video_height=pipeline.video_height,
                fps=pipeline.fps, flow_spec=spec,
                reuse_visuals=reuse_visuals,
            )
        except Exception as e:
            print(f"     ❌ {type(e).__name__}: {e}")
            if started_tracker:
                cost_tracker.end_video()
            return 2, None
        seg_dur = _get_duration(seg_path)
        print(f"     ✓ {seg_path.name} — {seg_dur:.1f}s")
        segments.append(seg_path)

    print(f"\n  🔗 Concatenando {len(segments)} segmentos...")
    art_profiles_list = [p.art_profile for p in plans]
    _concat_segments(segments, final_path, work_dir, art_profiles_list)

    # ─── Mixer música + ducking (PR 2.C chat 28) ───
    # Si existe music_map.json del topic, montar música con sidechain ducking
    # sobre el MP4 que recién salió del concat. Sino, dejar sin música (compat
    # con topics legacy pre-PR 2.B).
    music_map = _load_music_map(video_id)
    if music_map is None:
        print(f"\n  🔇 Sin music_map.json — MP4 final queda sin música")
    else:
        print(f"\n  🎚️  Mezclando música + ducking ({len(music_map)} tracks)...")

        # Renombrar el MP4 sin música a backup (evita sobrescritura, backlog #193)
        no_music_path = final_path.with_name(
            f"{final_path.stem}{MUSIC_INTERMEDIATE_SUFFIX}{final_path.suffix}"
        )
        final_path.replace(no_music_path)
        print(f"     backup: {no_music_path.name}")

        # CHAT 40: volumen de música POR TRACK (leído del audio_library/<track>.json
        # vía music_map; base del perfil como fallback). Resolver el par (ducked,
        # floor) efectivo de cada cap antes de hornear las pistas.
        mixing = sync_map.get("mixing", {})
        ducked_by_cap, floor_by_cap = _resolve_music_volumes(plans, mixing, music_map)
        print(f"     volumen por cap (chat 40 por-track):")
        for p in plans:
            src = "base" if ducked_by_cap[p.chapter_id] == float(mixing.get("music_volume", 0.25)) else "json"
            ti = music_map.get(p.chapter_id) or {}
            tid = ti.get("track_id", "—")
            print(f"       [{p.chapter_id}] track={tid:<22} "
                  f"ducked={ducked_by_cap[p.chapter_id]:.3f} "
                  f"floor={floor_by_cap[p.chapter_id]:.3f} ({src})")

        # CHAT 40 — detector "track sin calibrar" (print-only, después de la tabla).
        # Regla backlog #197/#231: si un track usa BASE por falta de calibración,
        # GRITAR (no caer calladito). La clasificación vive en un helper puro
        # (_classify_uncalibrated_tracks) para que el smoke ejerza el código REAL;
        # acá SOLO se imprime. NO toca _resolve_music_volumes ni el mix.
        uncal_generated, uncal_reused = _classify_uncalibrated_tracks(plans, music_map)
        if uncal_generated:
            print("\n  ⚠⚠ TRACKS NUEVOS SIN CALIBRAR (generados, nunca pasaron por el mixer):")
            for ch, tid in uncal_generated:
                print(f"       [{ch}] {tid} → usando BASE. Corré el mixer "
                      f"(python mixer_server.py) y calibrá este track ANTES de publicar.")
        if uncal_reused:
            print("\n  ℹ  tracks usando volumen BASE (no calibrados; OK si suenan bien, "
                  "sino mixer):")
            for ch, tid in uncal_reused:
                print(f"       [{ch}] {tid}")

        # Construir track continuo de música (paso A) — DOS pistas pre-atenuadas por
        # cap: ducked-source y floor-source. Cada cap entra con su volumen horneado.
        print(f"     paso A: tracks continuos (ducked + floor, vol por-cap)...")
        music_ducked_path = _build_continuous_music_track(
            plans=plans,
            music_map=music_map,
            work_dir=work_dir,
            crossfade_sec=MUSIC_CROSSFADE_SEC,
            piece_volumes=ducked_by_cap,
            output_filename="_music_continuous_ducked.wav",
        )
        music_floor_path = _build_continuous_music_track(
            plans=plans,
            music_map=music_map,
            work_dir=work_dir,
            crossfade_sec=MUSIC_CROSSFADE_SEC,
            piece_volumes=floor_by_cap,
            output_filename="_music_continuous_floor.wav",
        )

        # Mezclar con sidechain (paso B). Output: filename canónico final_path.
        # music_floor_path activa la ruta por-cap (volume=1.0, sidechain intacto).
        print(f"     paso B: sidechain mix (por-cap)...")
        _mix_music_into_video(
            video_path=no_music_path,
            music_path=music_ducked_path,
            sync_map=sync_map,
            output_path=final_path,
            music_floor_path=music_floor_path,
        )

        # Cleanup: WAVs intermedios (no_music.mp4 se preserva como backup auditable)
        music_ducked_path.unlink(missing_ok=True)
        music_floor_path.unlink(missing_ok=True)
        print(f"     ✅ música mezclada en {final_path.name}")

    final_dur = _get_duration(final_path)
    final_size_mb = final_path.stat().st_size / (1024 * 1024)

    if not keep_segments:
        for s in segments:
            s.unlink(missing_ok=True)
        try:
            work_dir.rmdir()
        except OSError:
            pass

    fase_cost = 0.0
    if started_tracker:
        report = cost_tracker.end_video()
        if report:
            fase_cost = report.total_cost

    print(f"\n  ✅ {final_path.name} — {final_dur:.1f}s · {final_size_mb:.1f}MB · ${fase_cost:.4f}")
    return 0, final_path


# ═══════════════════════════════════════════════════════════════
#  Main
# ═══════════════════════════════════════════════════════════════

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fase 2B — Ensamblaje final batch (procesa todos los topics con assets listos).",
    )
    parser.add_argument("video_id", nargs="?", default=None,
                        help="Opcional: procesa solo ese video_id. Sin argumento → modo batch.")
    parser.add_argument("--hook", type=str, default=None,
                        help="Texto gigante en ch01 los primeros 1.8s. Solo aplica en modo single.")
    parser.add_argument("--no-subs", action="store_true",
                        help="No quemar subtítulos karaoke.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Mostrar plan sin ejecutar FFmpeg.")
    parser.add_argument("--keep-segments", action="store_true",
                        help="No borrar los MP4 intermedios.")
    parser.add_argument("--reuse-visuals", action="store_true",
                        help="Re-quemar reutilizando los clips visuales ya horneados "
                             "(flux_visual/hybrid_visual en _fase2b_work) sin re-correr "
                             "DepthFlow ni flow_director. Para re-generar solo subs/música.")
    parser.add_argument("--limit", type=int, default=None,
                        help="Solo en modo batch: tope de videos a procesar en esta corrida.")
    parser.add_argument("--force", action="store_true",
                        help="Reprocesa aunque el topic ya esté en 'video_generated'.")
    args = parser.parse_args()

    if FFMPEG is None or FFPROBE is None:
        print(f"❌ No se encontró ffmpeg/ffprobe (winget Gyan.FFmpeg).")
        return 1

    # ─── Determinar lista de videos a procesar ───
    if args.video_id:
        # Modo SINGLE — override manual
        targets: list[tuple[str, str | None]] = [
            (args.video_id, _resolve_topic_id_for_video(args.video_id))
        ]
        mode = "single"
    else:
        # Modo BATCH — leer DB
        pending = _list_pending_for_assembly()
        if args.limit:
            pending = pending[:args.limit]
        targets = [(t.get("video_id") or t["id"], t["id"]) for t in pending]
        mode = "batch"

    if not targets:
        print(f"\n  ℹ  No hay topics con status='{ASSETS_READY_STATUS}' pendientes.")
        print(f"     Corré primero fase2a.py o pasá un video_id explícito.\n")
        return 0

    print(f"\n  🎬 Modo: {mode.upper()} · {len(targets)} video(s) a procesar")
    if mode == "batch":
        for vid, tid in targets:
            print(f"     - {vid} (topic_id={tid})")

    # ─── Procesar uno por uno ───
    success: list[str] = []
    failed: list[tuple[str, int]] = []
    total_cost = 0.0

    for vid, tid in targets:
        if not _has_assets_on_disk(vid):
            print(f"\n  ⚠  [{vid}] DB dice 'assets_rendered' pero faltan archivos en disco — skip")
            failed.append((vid, -1))
            continue

        rc, final_path = _assemble_one_video(
            vid,
            hook=args.hook if mode == "single" else None,  # hook solo manual
            no_subs=args.no_subs,
            keep_segments=args.keep_segments,
            dry_run=args.dry_run,
            reuse_visuals=args.reuse_visuals,
        )

        if rc == 0 and final_path is not None and not args.dry_run:
            # Marcar como video_generated en DB
            target_topic_id = tid or vid
            ok = mark_as_generated(
                topic_id=target_topic_id,
                video_id=vid,
                video_path=str(final_path),
            )
            if ok:
                print(f"     📌 topics_db: {target_topic_id} → {DONE_STATUS}")
            else:
                print(f"     ⚠  topics_db: no se encontró topic '{target_topic_id}' para marcar")
            success.append(vid)
        elif rc == 0:
            success.append(vid)  # dry run
        else:
            failed.append((vid, rc))

    # ─── Resumen final ───
    print(f"\n{'═' * 60}")
    print(f"  ✅ FASE 2B BATCH TERMINADA")
    print(f"{'═' * 60}")
    print(f"  Procesados OK: {len(success)}/{len(targets)}")
    if failed:
        print(f"  ❌ Fallidos:")
        for vid, rc in failed:
            print(f"     - {vid} (rc={rc})")
    print(f"{'═' * 60}\n")
    return 0 if not failed else 2


if __name__ == "__main__":
    sys.exit(main())
