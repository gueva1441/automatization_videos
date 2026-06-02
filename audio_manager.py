"""
audio_manager.py — Motor de Audio + Sincronización para "Ruta de Valor"

Responsabilidades:
  1. Generar un .mp3 por capítulo con ElevenLabs (voice_id y voice_settings
     del perfil activo en audio_config.ACTIVE_AUDIO_PROFILE).
  2. Transcribir cada .mp3 con faster-whisper → timestamps word-level (.json).
  3. FORCED ALIGNMENT: reemplazar palabras de Whisper (que pueden estar mal
     escritas en nombres propios) por las del guion, manteniendo timestamps.
  4. Emitir un sync_map.json maestro que el video_assembler consume para
     colocar efectos de marca (Whip Pan, Glitch, duck ratio, música).

Estructura de salida:
  output/audio/{video_id}/
    ├── ch01.mp3
    ├── ch01_timestamps.json
    ├── ch02.mp3
    ├── ch02_timestamps.json
    ├── ...
    └── sync_map.json   ← índice maestro (incluye mixing del perfil activo)

Contrato del guion de entrada (dict):
  {
    "video_id": "bloop",
    "chapters": [
        {"id": "ch01", "text": "..."},
        {"id": "ch02", "text": "..."},
        ...
    ]
  }
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import unicodedata
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

import requests
# faster_whisper se importa lazy dentro de _get_whisper_model() — evita
# cargar la DLL pyAV.loudnorm en imports top-level (chat 26: WDAC la bloquea
# desde Windows update reciente). Topics con sync_map.json en disco NO
# necesitan Whisper en runtime — solo la generación inicial de sync_map.

from config import api, OUTPUT_DIR, DATA_DIR

_NORMALIZED_NARRATION_FILENAME = "01b_narration_normalized.json"
from audio_config import AUDIO_STYLE, ACTIVE_AUDIO_PROFILE
from audio_profiles import VOICE_SETTINGS_BY_INTENT
from error_handler import error_handler, PipelineStage
from cost_tracker import cost_tracker

from tts_normalizer import normalize_for_tts


# ═══════════════════════════════════════════
#  Localización de binarios (ffprobe)
# ═══════════════════════════════════════════

_ffprobe_path: str | None = None


def _find_ffmpeg_binary(name: str) -> str | None:
    """
    Busca ffmpeg/ffprobe en PATH, y si falla en la ruta de Winget.
    Misma estrategia validada en test_full_video.py.
    """
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


def _get_ffprobe() -> str:
    """
    Retorna la ruta absoluta de ffprobe. Resolución lazy + cache.
    Lanza RuntimeError con mensaje accionable si no está instalado.
    """
    global _ffprobe_path
    if _ffprobe_path is None:
        found = _find_ffmpeg_binary("ffprobe")
        if not found:
            raise RuntimeError(
                "No se encontró ffprobe en PATH ni en Winget. "
                "Instalá con: winget install Gyan.FFmpeg"
            )
        _ffprobe_path = found
        error_handler.log_info(PipelineStage.AUDIO, f"ffprobe resuelto: {found}")
    return _ffprobe_path


# ═══════════════════════════════════════════
#  Whisper — singleton (evita recargar modelo)
# ═══════════════════════════════════════════

_whisper_model = None  # tipo: WhisperModel | None, sin import top-level


def _get_whisper_model():
    """Lazy load del modelo Whisper. Import diferido — solo carga la DLL
    pyAV cuando realmente se necesita transcribir audio (no en imports)."""
    global _whisper_model
    if _whisper_model is None:
        from faster_whisper import WhisperModel  # lazy import
        error_handler.log_info(
            PipelineStage.AUDIO,
            "Cargando modelo Whisper (base, int8)...",
        )
        _whisper_model = WhisperModel("base", device="cuda", compute_type="float16")
    return _whisper_model


# ═══════════════════════════════════════════
#  Utilidades de timestamps
# ═══════════════════════════════════════════

def _merge_punctuation_words(words: list[dict]) -> list[dict]:
    """Une tokens huérfanos que empiezan con puntuación: '10' + '.000' → '10.000'."""
    if not words:
        return words
    merged = [dict(words[0])]
    for w in words[1:]:
        first_char = w["word"][0]
        prev_last = merged[-1]["word"][-1] if merged[-1]["word"] else ""
        if first_char in ".,:;" and prev_last.isalnum():
            merged[-1]["word"] += w["word"]
            merged[-1]["end"] = w["end"]
        else:
            merged.append(dict(w))
    return merged


def _transcribe_word_timestamps(
    audio_path: Path, language: str = "es"
) -> list[dict]:
    """Transcribe audio y retorna [{word, start, end}, ...] con puntuación unida."""
    model = _get_whisper_model()
    segments, _info = model.transcribe(
        str(audio_path), language=language, word_timestamps=True,
    )
    words: list[dict] = []
    for seg in segments:
        for w in seg.words:
            text = w.word.strip()
            if text:
                words.append({
                    "word": text,
                    "start": float(w.start),
                    "end": float(w.end),
                })
    return _merge_punctuation_words(words)


# ═══════════════════════════════════════════
#  Forced Alignment: palabras del guion + timestamps Whisper
#  ─────────────────────────────────────────────
#  Whisper transcribe lo que SUENA. En nombres propios falla:
#      "Wittenoom" → "Bitenum"
#      "Panyjima"  → "Paniyima" / "Pañima"
#      "crocidolita" → "crocidolíta" (acento mal)
#  Pero los TIMESTAMPS que devuelve son correctos.
#
#  Solución: tomar texto del guion (que ElevenLabs leyó literal)
#  y mapear cada palabra correcta a un timestamp Whisper.
# ═══════════════════════════════════════════

_PUNCT_LEAD = re.compile(r"^[¿¡.,;:!?\"'(]+")
_PUNCT_TRAIL = re.compile(r"[.,;:!?\"')]+$")


def _normalize_token(tok: str) -> str:
    """Lowercase + sin acentos + sin puntuación de bordes (para comparar)."""
    tok = _PUNCT_LEAD.sub("", tok)
    tok = _PUNCT_TRAIL.sub("", tok)
    nfkd = unicodedata.normalize("NFKD", tok.lower())
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def _interp_spans(
    n: int, prev_end: float, next_start: float
) -> list[tuple[float, float]]:
    """Reparte n palabras uniformemente entre prev_end y next_start."""
    if n <= 0:
        return []
    span = max(next_start - prev_end, 0.0)
    if span <= 0:
        return [(prev_end, prev_end + 0.05) for _ in range(n)]
    step = span / n
    return [(prev_end + i * step, prev_end + (i + 1) * step) for i in range(n)]


def _force_align_to_script(
    whisper_words: list[dict], script_text: str
) -> list[dict]:
    """
    Forced alignment: usa palabras del GUION + timestamps de Whisper.

    Args:
        whisper_words: salida cruda de Whisper [{word, start, end}, ...].
        script_text: texto exacto que ElevenLabs leyó (text_for_tts).

    Returns:
        Misma estructura, pero con `word` corregido al guion y
        timestamps únicos + monotónicos (sin duplicados).
    """
    if not whisper_words or not script_text.strip():
        return whisper_words

    script_tokens: list[str] = [t for t in script_text.split() if t]
    if not script_tokens:
        return whisper_words

    s_keys = [_normalize_token(t) for t in script_tokens]
    w_keys = [_normalize_token(w["word"]) for w in whisper_words]

    matcher = SequenceMatcher(a=s_keys, b=w_keys, autojunk=False)
    aligned: list[dict] = []
    n_replaced = 0
    n_interp = 0

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            # Match exacto: palabra del guion + timestamp Whisper directo
            for s_i, w_j in zip(range(i1, i2), range(j1, j2)):
                aligned.append({
                    "word": script_tokens[s_i],
                    "start": float(whisper_words[w_j]["start"]),
                    "end": float(whisper_words[w_j]["end"]),
                })

        elif tag == "replace":
            # FIX: en lugar de mapear por offset entero (que producía
            # timestamps duplicados cuando len(s_block) > len(w_block)),
            # interpolamos UNIFORMEMENTE entre el inicio del primer
            # Whisper word del bloque y el fin del último. Garantiza
            # un span único por palabra del guion.
            s_block = list(range(i1, i2))
            w_block = list(range(j1, j2))
            if not w_block:
                continue
            block_start = float(whisper_words[j1]["start"])
            block_end = float(whisper_words[j2 - 1]["end"])
            spans = _interp_spans(len(s_block), block_start, block_end)
            for s_i, (st, en) in zip(s_block, spans):
                aligned.append({
                    "word": script_tokens[s_i],
                    "start": st,
                    "end": en,
                })
                n_replaced += 1

        elif tag == "delete":
            # Palabra del guion sin contraparte Whisper → interpolar timestamps
            prev_end = aligned[-1]["end"] if aligned else 0.0
            if j1 < len(whisper_words):
                next_start = float(whisper_words[j1]["start"])
            else:
                next_start = prev_end + (i2 - i1) * 0.3
            for s_i, (st, en) in zip(
                range(i1, i2), _interp_spans(i2 - i1, prev_end, next_start)
            ):
                aligned.append({
                    "word": script_tokens[s_i],
                    "start": st,
                    "end": en,
                })
                n_interp += 1

        elif tag == "insert":
            # Whisper alucinó palabras que no están en el guion → descartar
            pass

    # Post-proceso: garantizar timestamps únicos + monotónicos.
    # Cubre casos degenerados donde block_start == block_end (Whisper
    # devolvió span de 0s) o runs colapsados de _interp_spans.
    aligned = _enforce_monotonic_timestamps(aligned, min_dur=0.05)

    if n_replaced or n_interp:
        error_handler.log_info(
            PipelineStage.AUDIO,
            f"Forced alignment: {n_replaced} reemplazos, {n_interp} interpolaciones "
            f"sobre {len(script_tokens)} palabras del guion",
        )

    return aligned


def _enforce_monotonic_timestamps(
    words: list[dict], min_dur: float = 0.05
) -> list[dict]:
    """
    Garantiza que cada palabra tenga:
      - start estrictamente >= start anterior + min_dur
      - duración mínima `min_dur` segundos (default 50ms)
      - end >= start + min_dur

    Si detecta runs de palabras con el mismo `start` (caso degenerado del
    `replace` cuando block_start == block_end), las redistribuye
    uniformemente entre run_start y el start de la próxima palabra distinta.
    """
    if not words:
        return words

    fixed: list[dict] = [dict(w) for w in words]
    n = len(fixed)

    # Pasada 1: redistribuir runs de palabras con el mismo start
    i = 0
    while i < n:
        run_start_val = float(fixed[i]["start"])
        j = i + 1
        while j < n and float(fixed[j]["start"]) <= run_start_val + 1e-6:
            j += 1
        run_len = j - i
        if run_len > 1:
            if j < n:
                run_end_val = float(fixed[j]["start"])
            else:
                last_end = max(float(fixed[k]["end"]) for k in range(i, j))
                run_end_val = max(last_end, run_start_val + run_len * min_dur)
            span = max(run_end_val - run_start_val, run_len * min_dur)
            step = span / run_len
            for k in range(run_len):
                fixed[i + k]["start"] = run_start_val + k * step
                fixed[i + k]["end"] = run_start_val + (k + 1) * step
        i = j

    # Pasada 2: monotonicidad estricta + duración mínima
    for k in range(n):
        if k > 0:
            min_start = float(fixed[k - 1]["start"]) + min_dur
            if float(fixed[k]["start"]) < min_start:
                fixed[k]["start"] = min_start
        if float(fixed[k]["end"]) < float(fixed[k]["start"]) + min_dur:
            fixed[k]["end"] = float(fixed[k]["start"]) + min_dur

    return fixed


def _get_audio_duration(audio_path: Path) -> float:
    """Lee duración del .mp3 vía ffprobe (ruta absoluta)."""
    ffprobe = _get_ffprobe()
    try:
        result = subprocess.run(
            [
                ffprobe, "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                str(audio_path),
            ],
            capture_output=True, text=True, timeout=15,
        )
        return float(result.stdout.strip())
    except (subprocess.SubprocessError, ValueError) as e:
        error_handler.log_warning(
            PipelineStage.AUDIO,
            f"ffprobe falló para {audio_path.name}: {e}. Usando 0.0.",
        )
        return 0.0


# ═══════════════════════════════════════════
#  ElevenLabs — TTS por capítulo
# ═══════════════════════════════════════════

@error_handler.retry(PipelineStage.AUDIO)
def _generate_chapter_audio(
    text: str,
    output_path: Path,
    voice_id: str,
    voice_settings: dict[str, Any],
) -> Path:
    """
    Llama a ElevenLabs y escribe el .mp3. Registra costo.
    Protegido por @retry: 3 intentos normales, 5 si es 503/429.
    """
    payload = {
        "text": text,
        "model_id": api.elevenlabs_model,
        "voice_settings": voice_settings,
    }
    resp = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
        headers={
            "xi-api-key": api.elevenlabs_api_key,
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=120,  # audios largos pueden tardar
    )
    resp.raise_for_status()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(resp.content)

    cost_tracker.track_elevenlabs(
        description=f"{output_path.stem}: {text[:50]}...",
        characters=len(text),
    )
    return output_path


# ═══════════════════════════════════════════
#  API pública
# ═══════════════════════════════════════════

def _resolve_voice_settings(
    base_settings: dict,
    narrative_intent: str | None,
) -> dict:
    """Mergea voice_settings base del profile con override por intent.

    PR 2.A chat 24, D-A1: el override solo toca stability + style. El profile
    activo sigue dueño de similarity_boost y use_speaker_boost (identidad
    sonora del canal).

    Args:
        base_settings: voice_settings del profile activo (AUDIO_STYLE).
        narrative_intent: uno de los 7 del catálogo, o None/string vacío.

    Returns:
        dict mergeado. Si narrative_intent es None/vacío/desconocido,
        devuelve base_settings sin tocar (compat).
    """
    if not narrative_intent:
        return base_settings
    override = VOICE_SETTINGS_BY_INTENT.get(narrative_intent)
    if not override:
        return base_settings
    return {**base_settings, **override}


def _ensure_cost_tracking(video_id: str) -> None:
    """
    Garantiza que cost_tracker tenga un video activo para este video_id.
    Idempotente: si fase2.py ya llamó start_video con el mismo id, no pisa.
    Si hay otro video activo distinto, lo reemplaza (con warning).
    """
    active = cost_tracker.current_video
    if active is None:
        cost_tracker.start_video(video_id=video_id)
        return
    if active.video_id != video_id:
        error_handler.log_warning(
            PipelineStage.AUDIO,
            f"cost_tracker tenía video activo '{active.video_id}' — "
            f"reemplazando por '{video_id}'",
        )
        cost_tracker.start_video(video_id=video_id)


def _resolve_text_for_tts(
    chapter_id: str,
    raw_text: str,
    video_id: str,
    language: str = "es",
) -> str:
    """Resuelve el texto que efectivamente se manda a ElevenLabs.

    Prioridad:
      1. Si existe data/scripts/_steps/<video_id>/01b_narration_normalized.json
         con entry para este chapter_id → usar narration_normalized de ahí.
         (LONG con gate corrido — chat 24 PR 2.0.X.)
      2. Fallback: aplicar normalize_for_tts(raw_text) (SHORT path o LONG sin gate).

    Args:
        chapter_id: "ch01", "ch02", ...
        raw_text: texto original de m01b (lo que viene en script["chapters"][i]["text"]).
        video_id: topic_id, para localizar el _steps/<video_id>/.
        language: idioma para fallback.

    Returns:
        El texto que se va a hashear y mandar a ElevenLabs.
    """
    normalized_path = (
        DATA_DIR / "scripts" / "_steps" / video_id / _NORMALIZED_NARRATION_FILENAME
    )
    if normalized_path.exists():
        try:
            data = json.loads(normalized_path.read_text(encoding="utf-8"))
            cap_n = int(chapter_id.replace("ch", ""))
            for ch in data.get("chapters", []):
                if ch.get("chapter_number") == cap_n:
                    norm_text = ch.get("narration_normalized")
                    if isinstance(norm_text, str) and norm_text.strip():
                        error_handler.log_info(
                            PipelineStage.AUDIO,
                            f"[{chapter_id}] usando narration_normalized del gate",
                        )
                        return norm_text
        except (json.JSONDecodeError, OSError, ValueError) as e:
            error_handler.log_warning(
                PipelineStage.AUDIO,
                f"[{chapter_id}] {_NORMALIZED_NARRATION_FILENAME} ilegible "
                f"({type(e).__name__}: {e}) → fallback a normalize_for_tts",
            )

    return normalize_for_tts(raw_text, language=language)


@error_handler.retry(PipelineStage.AUDIO)
def _forced_align_elevenlabs(
    audio_path: Path, text_for_tts: str, language: str = "es"
) -> dict:
    """Alinea el MP3 ya generado contra el texto que leyó el TTS, vía el
    Forced Alignment API de ElevenLabs. Devuelve el dict con 'characters'
    y 'words' (cada uno [{text, start, end}, ...]) tal cual lo da la API.

    NO regenera audio. NO usa Whisper. El texto DEBE ser text_for_tts
    (el normalizado que leyó el TTS), no el crudo del guion.

    `language` se deja en la firma por compat / logging; la API de FA
    NO lo exige (detecta del texto). No mandarlo en el form salvo que el
    Bloque 0 confirme que el endpoint lo acepta.
    """
    url = "https://api.elevenlabs.io/v1/forced-alignment"
    with open(audio_path, "rb") as f:
        files = {"file": (audio_path.name, f, "audio/mpeg")}
        data = {"text": text_for_tts}
        resp = requests.post(
            url,
            headers={"xi-api-key": api.elevenlabs_api_key},
            files=files,
            data=data,
            timeout=180,
        )
    resp.raise_for_status()
    return resp.json()


def generate_chapter_assets(
    chapter: dict[str, str],
    video_id: str,
    voice_id: str,
    voice_settings: dict[str, Any],
    language: str = "es",
    skip_if_exists: bool = True,
) -> dict[str, Any]:
    """
    Genera .mp3 + _timestamps.json para UN capítulo.

    Retorna el entry del capítulo para el sync_map.
    """
    chapter_id: str = chapter["id"]
    text: str = chapter["text"]

    audio_dir = OUTPUT_DIR / "audio" / video_id
    audio_dir.mkdir(parents=True, exist_ok=True)

    audio_path = audio_dir / f"{chapter_id}.mp3"
    timestamps_path = audio_dir / f"{chapter_id}_timestamps.json"
    meta_path = audio_dir / f"{chapter_id}.meta.json"

    # ─── 1. Audio ───

    # PR 2.0.X: si existe 01b_narration_normalized.json (LONG con gate corrido),
    # usarlo como fuente de verdad. El normalize_for_tts queda como fallback
    # (SHORT path o LONG sin gate).
    text_for_tts = _resolve_text_for_tts(
        chapter_id=chapter_id,
        raw_text=text,
        video_id=video_id,
        language=language,
    )

    # Hash del texto que efectivamente se va a grabar — invalida cache si
    # m01b regeneró narración y resulta en TTS distinto. PR 1 chat 24.
    text_hash = hashlib.md5(text_for_tts.encode("utf-8")).hexdigest()[:12]

    # Si los assets existen, validar que correspondan al texto actual.
    # Si el hash difiere → texto cambió, regenerar audio + timestamps.
    if skip_if_exists and audio_path.exists():
        prior_hash: str | None = None
        if meta_path.exists():
            try:
                prior_meta = json.loads(meta_path.read_text(encoding="utf-8"))
                prior_hash = prior_meta.get("text_hash")
            except (json.JSONDecodeError, OSError):
                prior_hash = None

        if prior_hash != text_hash:
            error_handler.log_info(
                PipelineStage.AUDIO,
                f"[{chapter_id}] text_hash difiere "
                f"(disk={prior_hash!r}, current={text_hash!r}) → regenerando",
            )
            audio_path.unlink(missing_ok=True)
            timestamps_path.unlink(missing_ok=True)
            (audio_dir / f"{chapter_id}_alignment.json").unlink(missing_ok=True)  # NUEVO

    if skip_if_exists and audio_path.exists():
        error_handler.log_info(
            PipelineStage.AUDIO,
            f"[{chapter_id}] Audio ya existe (text_hash match) — reusando",
        )
    else:
        error_handler.log_info(
            PipelineStage.AUDIO,
            f"[{chapter_id}] Generando audio ({len(text_for_tts)} chars normalizados, "
            f"{len(text)} originales)...",
        )
        _generate_chapter_audio(
            text=text_for_tts,
            output_path=audio_path,
            voice_id=voice_id,
            voice_settings=voice_settings,
        )

    duration = _get_audio_duration(audio_path)

    # ─── 2. Timestamps vía ElevenLabs Forced Alignment ───
    alignment_path = audio_dir / f"{chapter_id}_alignment.json"
    if skip_if_exists and timestamps_path.exists() and alignment_path.exists():
        error_handler.log_info(
            PipelineStage.AUDIO,
            f"[{chapter_id}] Timestamps + alignment ya existen — reusando",
        )
        words = json.loads(timestamps_path.read_text(encoding="utf-8"))
    else:
        error_handler.log_info(
            PipelineStage.AUDIO,
            f"[{chapter_id}] Forced Alignment (ElevenLabs)...",
        )
        alignment = _forced_align_elevenlabs(audio_path, text_for_tts, language)

        # Log de loss NO opcional: si FA dudó, queremos enterarnos (no caer callado).
        loss = alignment.get("loss")
        if loss is not None and float(loss) > 0.15:
            error_handler.log_warning(
                PipelineStage.AUDIO,
                f"[{chapter_id}] Forced Alignment loss alto: {loss} (>0.15) — revisar sync",
            )

        words = [
            {"word": w["text"], "start": float(w["start"]), "end": float(w["end"])}
            for w in alignment.get("words", [])
        ]

        # Clamp defensivo de monotonía a nivel palabra (FA suele venir perfecto,
        # pero NO confiamos a ciegas — antes lo garantizaba _enforce_monotonic).
        for k in range(1, len(words)):
            if words[k]["start"] < words[k - 1]["start"]:
                words[k]["start"] = words[k - 1]["start"]
            if words[k]["end"] < words[k]["start"]:
                words[k]["end"] = words[k]["start"]

        alignment_path.write_text(
            json.dumps(alignment.get("characters", []), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    timestamps_path.write_text(
        json.dumps(words, ensure_ascii=False, indent=2), encoding="utf-8",
    )

    # Persistir el text_hash para la próxima corrida (cache invalidation).
    meta_path.write_text(
        json.dumps(
            {"text_hash": text_hash, "generated_at": datetime.now().isoformat()},
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    error_handler.log_success(
        PipelineStage.AUDIO,
        f"[{chapter_id}] {duration:.1f}s, {len(words)} palabras",
    )

    return {
        "id": chapter_id,
        "text": text,                  # texto original (referencia)
        "text_for_tts": text_for_tts,  # texto normalizado (lo que se grabó)
        "text_hash": text_hash,        # md5[:12] de text_for_tts (cache invalidation)
        "audio_path": audio_path.name,
        "timestamps_path": timestamps_path.name,
        "duration_sec": round(duration, 3),
        "word_count": len(words),
    }


def process_script(
    script: dict[str, Any],
    language: str = "es",
    skip_if_exists: bool = True,
) -> Path:
    """
    Procesa un guion completo (múltiples capítulos) y emite sync_map.json.

    El sync_map.json incluye todo lo que el video_assembler necesita:
      - Rutas de audio y timestamps por capítulo
      - voice_settings del perfil activo
      - mixing (duck_ratio, music_volume, sfx_volume, duck_release_ms)
      - music_prompt para generar la música de fondo

    Args:
        script: {"video_id": str, "chapters": [{"id": str, "text": str}, ...]}
        language: idioma para Whisper (default "es")
        skip_if_exists: si True, reutiliza audios/timestamps ya generados

    Returns:
        Path al sync_map.json generado.
    """
    video_id: str = script["video_id"]
    chapters: list[dict] = script["chapters"]

    # Garantizar tracking de costos ANTES de cualquier llamada a ElevenLabs
    _ensure_cost_tracking(video_id)

    # Voice ID: perfil activo > config global
    voice_id: str = AUDIO_STYLE.get("voice_id") or api.elevenlabs_voice_id
    voice_settings: dict = AUDIO_STYLE["voice_settings"]
    mixing: dict = AUDIO_STYLE.get("mixing", {})

    error_handler.log_info(
        PipelineStage.AUDIO,
        f"🎙️  [{video_id}] Perfil: {ACTIVE_AUDIO_PROFILE} | "
        f"Voz: {voice_id} | Capítulos: {len(chapters)}",
    )

    chapter_entries: list[dict] = []
    running_offset: float = 0.0

    for ch in chapters:
        # PR 2.A chat 24: override de stability+style por narrative_intent del
        # cap. Si el cap no tiene intent (SHORT, o LONG generado pre-PR 2.A) →
        # _resolve_voice_settings devuelve base_settings sin tocar.
        cap_intent = ch.get("narrative_intent")
        cap_voice_settings = _resolve_voice_settings(
            base_settings=voice_settings,
            narrative_intent=cap_intent,
        )

        if cap_intent:
            error_handler.log_info(
                PipelineStage.AUDIO,
                f"[{ch['id']}] intent={cap_intent} → "
                f"stability={cap_voice_settings.get('stability')}, "
                f"style={cap_voice_settings.get('style')}",
            )

        entry = generate_chapter_assets(
            chapter=ch,
            video_id=video_id,
            voice_id=voice_id,
            voice_settings=cap_voice_settings,
            language=language,
            skip_if_exists=skip_if_exists,
        )
        entry["narrative_intent"] = cap_intent or ""
        entry["voice_settings_applied"] = cap_voice_settings
        entry["start_offset_sec"] = round(running_offset, 3)
        entry["end_offset_sec"] = round(running_offset + entry["duration_sec"], 3)
        running_offset = entry["end_offset_sec"]
        chapter_entries.append(entry)

    # ─── sync_map.json ───
    audio_dir = OUTPUT_DIR / "audio" / video_id
    sync_map_path = audio_dir / "sync_map.json"

    sync_map = {
        "video_id": video_id,
        "profile": ACTIVE_AUDIO_PROFILE,
        "profile_description": AUDIO_STYLE.get("description", ""),
        "generated_at": datetime.now().isoformat(),
        "voice_id": voice_id,
        "voice_settings": voice_settings,
        "mixing": mixing,  # duck_ratio, music_volume, sfx_volume, duck_release_ms
        "music_prompt": AUDIO_STYLE.get("music_prompt", ""),
        "total_duration_sec": round(running_offset, 3),
        "total_chapters": len(chapter_entries),
        "chapters": chapter_entries,
    }
    sync_map_path.write_text(
        json.dumps(sync_map, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    error_handler.log_success(
        PipelineStage.AUDIO,
        f"✅ [{video_id}] sync_map.json listo — "
        f"{len(chapter_entries)} capítulos, {running_offset:.1f}s totales",
    )
    return sync_map_path


# ═══════════════════════════════════════════
#  CLI standalone (para testing)
# ═══════════════════════════════════════════

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Uso: python audio_manager.py <ruta_al_script.json>")
        sys.exit(1)

    script_path = Path(sys.argv[1])
    script = json.loads(script_path.read_text(encoding="utf-8"))

    sync_map = process_script(script)
    print(f"\n✅ sync_map generado: {sync_map}")
