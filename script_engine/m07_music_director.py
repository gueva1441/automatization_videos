"""
m07_music_director.py — Music director: matchea intents a tracks de library
o genera nuevos con ElevenLabs Music + gate interactivo de aprobación.

PR 2.B chat 25 (Camino A + Sound Bank Curado):
  - Tracks NUEVOS por video al principio (sprint de curación)
  - Library reusable entre videos via matcher LLM Gemini Flash
  - Gate interactivo de aprobación humana (lección normalizer_gate chat 24)
  - Threshold conservador (80) para evitar reuso espurio del LLM matcher
  - Filtro DURO por intent_origin antes de pasar al matcher LLM
    (lección art_profiles chat 19: nunca dejar al LLM elegir entre N items
    sin pre-filtro determinístico)

INPUT: sync_map.json (post PR 2.A — incluye narrative_intent por cap)
OUTPUT:
  - music_map.json: para cada cap, qué track usar (path + intent + match_source)
  - audio_library/<track_id>.mp3 + audio_library/<track_id>.json (si generó nuevo
    Y fue aprobado por el humano en el gate interactivo)

LLAMADAS GEMINI: 0-7 por video (1 por cap si library tiene >=2 candidatos
                    del intent; 0 si library tiene 0 candidatos → genera directo;
                    0 si library tiene 1 candidato → single-candidate fallback).
LLAMADAS ELEVENLABS: 0-7 por video (1 por cap si NO hay match >= threshold,
                    +1 por cada re-roll del gate interactivo).

Deudas menores anotadas chat 25:
  - #167: cost_tracker no tiene método para Music — m07 loguea costo manual
  - #168: PipelineStage no tiene MUSIC — m07 usa AUDIO por proximidad funcional
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Literal

import os
import subprocess
import sys
import tempfile
from email.parser import BytesParser
from email.policy import default

import requests

from config import api, BASE_DIR, OUTPUT_DIR
from error_handler import error_handler, PipelineStage
from gemini_helpers import call_flash_json
from music_config import (
    MATCH_SCORE_THRESHOLD,
    MUSIC_API_URL,
    MUSIC_LENGTH_MS,
    MUSIC_MODEL_ID,
    MUSIC_OUTPUT_FORMAT,
    MUSIC_REQUEST_TIMEOUT_SEC,
    MusicConfigError,
    build_music_prompt,
    validate_music_config,
)


# ═══════════════════════════════════════════════════════════════
#  CONSTANTES
# ═══════════════════════════════════════════════════════════════

# audio_library/ en raíz del proyecto. Shared entre todos los videos del canal.
AUDIO_LIBRARY_DIR: Path = BASE_DIR / "audio_library"

# Prefijo para tracks generados pero NO aprobados todavía (gate interactivo).
# Si el gate aprueba: rename _DRAFT_<id>.mp3 → <id>.mp3 + crear JSON.
# Si rechaza: borrar el _DRAFT_<id>.mp3 sin persistir nada.
DRAFT_PREFIX = "_DRAFT_"

# Source del match en music_map.json (auditoría humana legible)
MatchSource = Literal["reused", "generated", "skipped"]


# ═══════════════════════════════════════════════════════════════
#  EXCEPCIONES
# ═══════════════════════════════════════════════════════════════

class MusicDirectorError(Exception):
    """Error fatal de m07 (config inválida, library corrupta, etc.).

    NO se usa para fallos transitorios de API (timeout, 503). Esos se
    manejan con retry en _generate_new_track_with_gate (2.2.C).
    """


# ═══════════════════════════════════════════════════════════════
#  CARGA DE LIBRARY
# ═══════════════════════════════════════════════════════════════

def _ensure_library_dir() -> None:
    """Crea audio_library/ si no existe. Idempotente."""
    AUDIO_LIBRARY_DIR.mkdir(parents=True, exist_ok=True)


def _load_library() -> list[dict[str, Any]]:
    """Escanea audio_library/ y devuelve la lista de descriptores JSON.

    Cada item es un dict con el schema persistido al disco:
        track_id, mp3_filename, intent_origin, fits_intents,
        compatible_profiles, topic_source, topic_title, prompt_used,
        duration_ms, cost_usd, generated_at, approved_at,
        elevenlabs_metadata, times_used, last_used_at

    Solo lee archivos *.json. Los *.mp3 son los assets binarios paralelos.
    Si un *.json es ilegible, loguea warning y lo skipea (no aborta).
    Si un *.json no tiene los keys mínimos, loguea warning y skipea.
    Si un *.json apunta a un .mp3 que no existe, loguea warning y skipea.

    Returns:
        Lista de descriptores válidos. Puede ser [] si library está vacía
        (caso primer video del canal).
    """
    _ensure_library_dir()
    library: list[dict[str, Any]] = []
    for json_path in sorted(AUDIO_LIBRARY_DIR.glob("*.json")):
        try:
            data = json.loads(json_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as e:
            error_handler.log_warning(
                PipelineStage.AUDIO,
                f"[m07] library: {json_path.name} ilegible "
                f"({type(e).__name__}: {e}), skipping",
            )
            continue
        if not isinstance(data, dict):
            error_handler.log_warning(
                PipelineStage.AUDIO,
                f"[m07] library: {json_path.name} no es un dict, skipping",
            )
            continue
        required_keys = {"track_id", "mp3_filename", "intent_origin"}
        missing = required_keys - set(data.keys())
        if missing:
            error_handler.log_warning(
                PipelineStage.AUDIO,
                f"[m07] library: {json_path.name} falta keys {missing}, "
                f"skipping",
            )
            continue
        mp3_path = AUDIO_LIBRARY_DIR / data["mp3_filename"]
        if not mp3_path.exists():
            error_handler.log_warning(
                PipelineStage.AUDIO,
                f"[m07] library: {json_path.name} apunta a "
                f"{data['mp3_filename']} que no existe, skipping",
            )
            continue
        library.append(data)
    return library


# ═══════════════════════════════════════════════════════════════
#  FILTRO DE CANDIDATOS — POR INTENT + PROFILE (DURO, sin LLM)
# ═══════════════════════════════════════════════════════════════

def _filter_candidates(
    library: list[dict[str, Any]],
    intent: str,
    profile: str,
) -> list[dict[str, Any]]:
    """Filtro DURO de candidatos antes de pasar al LLM matcher.

    Aplica 2 filtros determinísticos:
      1. Track es del intent correcto, o el usuario lo marcó manualmente
         como compatible con ese intent (fits_intents contiene el intent).
      2. Track es compatible con el profile activo del canal
         (compatible_profiles contiene el profile).

    Esto reduce el universo del LLM matcher de N tracks a 0-3 tracks
    típicamente. Evita el modo de falla "LLM elige incorrectamente entre
    demasiadas opciones" (lección art_profiles chat 19).

    Args:
        library: output de _load_library().
        intent: uno de los 7 narrative_intents del catálogo m01a.
        profile: profile activo del canal (sync_map.profile).

    Returns:
        Sublista de library con tracks que pasan los 2 filtros.
        Puede ser [] si ningún track encaja → caller debe generar nuevo.
    """
    candidates: list[dict[str, Any]] = []
    for track in library:
        # Filtro 1: intent match (origin O explicit fits_intents)
        intent_origin_match = track.get("intent_origin") == intent
        fits_intents_match = intent in track.get("fits_intents", [])
        if not (intent_origin_match or fits_intents_match):
            continue
        # Filtro 2: profile compatibility
        compatible = track.get("compatible_profiles", [])
        if profile not in compatible:
            continue
        candidates.append(track)
    return candidates


# ═══════════════════════════════════════════════════════════════
#  STUBS — implementados en sub-handoffs 2.2.B y 2.2.C
# ═══════════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════════
#  MATCHER LLM — Gemini Flash decide entre 2-3 candidatos filtrados
# ═══════════════════════════════════════════════════════════════

_MATCHER_SYSTEM_INSTRUCTION = """Sos un asistente especializado en seleccionar música de fondo para videos documentales dark mystery. Tu trabajo: dado un capítulo nuevo de un video y varios candidatos musicales de la library, elegir el que MEJOR encaja emocionalmente.

CRITERIO PRINCIPAL: el feel/atmósfera del track debe acompañar el intent narrativo del capítulo y el feel del anchor (primera frase del cap). Buscás match EMOCIONAL, no semántico. Ignorá palabras-clave temáticas (lugares, nombres) — concentrate en la energía musical (tonalidad, BPM, instrumentación, intensidad).

OUTPUT: JSON estricto sin markdown, sin texto adicional:
{
  "winner": "<track_id exacto de la lista de candidatos>",
  "match_score": <int 0-100>,
  "reasoning": "<2-3 frases citando características concretas del track ganador>"
}

ESCALA de match_score:
  80-100: reuso seguro (encaja muy bien)
  60-79:  encaja pero no ideal (caller decidirá si reusar o generar nuevo)
  0-59:   NO encaja, mejor generar nuevo

REGLAS INVIOLABLES:
1. "winner" DEBE ser EXACTAMENTE uno de los track_id listados (string exacto).
2. NUNCA inventes track_ids que no estén en la lista.
3. NUNCA infles el score artificialmente para "evitar que se genere nuevo".
   Un score honesto bajo (50) es preferible a un reuso forzado con score
   inflado (85). El sistema tiene un generador como red de seguridad.
4. "reasoning" debe CITAR características concretas (instrumentos, BPM,
   mood) del track ganador. NO frases vagas tipo "parece similar".
"""


def _build_matcher_user_prompt(
    intent: str,
    anchor: str,
    candidates: list[dict[str, Any]],
) -> str:
    """Arma el user prompt para el matcher LLM.

    Estructura rígida (no narrativa libre) para reducir espacio de
    alucinación. Por cada candidato muestra: track_id, description
    (de ElevenLabs metadata), genres, prompt_used.

    NO incluye composition_plan completo (ruido) ni topic_title del video
    nuevo (induce sesgo temático en vez de match emocional).
    """
    parts: list[str] = [
        "CAPÍTULO NUEVO:",
        f"  intent_narrativo: {intent}",
        f'  narration_anchor: "{anchor}"',
        "",
        f"CANDIDATOS DE LA LIBRARY (todos compatibles con intent '{intent}'):",
        "",
    ]
    for i, track in enumerate(candidates, 1):
        track_id = track["track_id"]
        prompt_used = track.get("prompt_used", "(sin prompt registrado)")
        if len(prompt_used) > 400:
            prompt_used = prompt_used[:400] + "..."

        elevenlabs_meta = track.get("elevenlabs_metadata", {})
        description = elevenlabs_meta.get("description", "(sin descripción)")
        if len(description) > 300:
            description = description[:300] + "..."
        genres = elevenlabs_meta.get("genres", [])

        parts.append(f"[{i}] track_id: {track_id}")
        parts.append(f'    description: "{description}"')
        parts.append(f"    genres: {genres}")
        parts.append(f'    prompt_used: "{prompt_used}"')
        parts.append("")

    parts.append(
        "Elegí el mejor match y devolvé el JSON estricto. "
        "Recordá: score honesto, winner exacto de la lista, "
        "reasoning con características concretas."
    )
    return "\n".join(parts)


def _match_intent_to_track(
    intent: str,
    anchor: str,
    profile: str,
    candidates: list[dict[str, Any]],
) -> dict[str, Any] | None:
    """Matcher LLM con red de seguridad.

    Edge cases (sin LLM):
      - 0 candidatos → None (caller genera nuevo)
      - 1 candidato → single-candidate fallback, score=100 forzado,
                      NO llama LLM (no tiene sentido elegir entre 1)

    Caso normal (2+ candidatos):
      - Llama Gemini Flash con system_instruction + user_prompt estructurado.
      - Valida shape del response: dict con winner+match_score+reasoning.
      - Valida winner ∈ candidate_ids (anti-alucinación).
      - Valida match_score ∈ [0, 100].
      - Si match_score >= MATCH_SCORE_THRESHOLD (80) → devuelve dict.
      - Si match_score < threshold → return None (caller genera nuevo).
      - Si CUALQUIER validación falla → log warning + return None.

    Args:
        intent: uno de los 7 narrative_intents.
        anchor: primera oración del cap (narration_anchor).
        profile: profile activo del canal (solo para logging, NO se le
                 pasa al LLM — el filtro de profile ya se aplicó upstream
                 en _filter_candidates).
        candidates: lista pre-filtrada por _filter_candidates. Garantizado
                    que todos los items son del intent correcto y
                    compatible con el profile.

    Returns:
        dict {"winner", "match_score", "reasoning"} si hay match >= threshold,
        None si caller debe generar nuevo.
    """
    # Edge case 1: cero candidatos
    if not candidates:
        return None

    # Edge case 2: un solo candidato → single-candidate fallback
    if len(candidates) == 1:
        only = candidates[0]
        error_handler.log_info(
            PipelineStage.AUDIO,
            f"[m07] match {intent}: single-candidate fallback "
            f"({only['track_id']}) — no se llama LLM",
        )
        return {
            "winner": only["track_id"],
            "match_score": 100,
            "reasoning": (
                "Single candidate in library for this intent — auto-selected"
            ),
        }

    # Caso normal: 2+ candidatos → Gemini Flash decide
    user_prompt = _build_matcher_user_prompt(intent, anchor, candidates)

    try:
        result = call_flash_json(
            user_prompt,
            system_instruction=_MATCHER_SYSTEM_INSTRUCTION,
        )
    except Exception as e:
        # Cualquier fallo del LLM (timeout, parse error, etc) → red de
        # seguridad: caller genera nuevo. No retries en m07.
        error_handler.log_warning(
            PipelineStage.AUDIO,
            f"[m07] matcher {intent}: LLM falló "
            f"({type(e).__name__}: {e}) — fallback a generación nueva",
        )
        return None

    # Validar shape: dict con keys requeridos
    if not isinstance(result, dict):
        error_handler.log_warning(
            PipelineStage.AUDIO,
            f"[m07] matcher {intent}: LLM devolvió {type(result).__name__}, "
            f"esperaba dict — fallback a generación nueva",
        )
        return None

    required = {"winner", "match_score", "reasoning"}
    missing = required - set(result.keys())
    if missing:
        error_handler.log_warning(
            PipelineStage.AUDIO,
            f"[m07] matcher {intent}: LLM response falta keys {missing} "
            f"— fallback a generación nueva",
        )
        return None

    # Validar winner ∈ candidate_ids (anti-alucinación)
    candidate_ids = {c["track_id"] for c in candidates}
    if result["winner"] not in candidate_ids:
        error_handler.log_warning(
            PipelineStage.AUDIO,
            f"[m07] matcher {intent}: LLM eligió winner inválido "
            f"({result['winner']!r}, no está en {sorted(candidate_ids)}) "
            f"— fallback a generación nueva",
        )
        return None

    # Validar match_score ∈ [0, 100]
    try:
        score = int(result["match_score"])
    except (TypeError, ValueError):
        error_handler.log_warning(
            PipelineStage.AUDIO,
            f"[m07] matcher {intent}: match_score no parseable "
            f"({result['match_score']!r}) — fallback a generación nueva",
        )
        return None

    if not (0 <= score <= 100):
        error_handler.log_warning(
            PipelineStage.AUDIO,
            f"[m07] matcher {intent}: match_score fuera de rango "
            f"({score}) — fallback a generación nueva",
        )
        return None

    reasoning = str(result["reasoning"])

    # Log de decisión completa para auditoría humana (lección anti-art_profiles).
    # Vos auditás estos logs en los primeros 5 videos para validar que el
    # matcher no aluciona.
    reasoning_excerpt = reasoning[:120] + ("..." if len(reasoning) > 120 else "")
    error_handler.log_info(
        PipelineStage.AUDIO,
        f"[m07] matcher {intent}: winner={result['winner']} "
        f"score={score} reasoning=\"{reasoning_excerpt}\"",
    )

    # Threshold check final
    if score < MATCH_SCORE_THRESHOLD:
        error_handler.log_info(
            PipelineStage.AUDIO,
            f"[m07] matcher {intent}: score {score} < threshold "
            f"{MATCH_SCORE_THRESHOLD} → generar nuevo",
        )
        return None

    return {
        "winner": result["winner"],
        "match_score": score,
        "reasoning": reasoning,
    }


# ═══════════════════════════════════════════════════════════════
#  NAMING + I/O HELPERS
# ═══════════════════════════════════════════════════════════════

def _generate_track_id(intent: str, topic_id: str) -> str:
    """Naming convention para tracks de la library: `<intent>_<topic_id_first8>`.

    Ej: "hook_7b52de57" (de intent="hook" + topic_id="7b52de57-eee6-4018-...").

    Estable, human-readable, ASCII-safe. NO incluye topic_title porque
    puede tener caracteres especiales o no-ASCII (paths cross-platform).
    """
    return f"{intent}_{topic_id[:8]}"


def _parse_multipart_response(
    content_type: str,
    content: bytes,
) -> tuple[bytes, dict[str, Any]]:
    """Parsea el response multipart/mixed de POST /v1/music/detailed.

    El response trae 2 parts:
      - application/json con metadata (composition_plan, song_metadata, ...)
      - audio/mpeg con los bytes del MP3

    Reusa el patrón validado por el probe chat 25 (_test_elevenlabs_music_probe).

    Args:
        content_type: valor del header HTTP Content-Type del response.
        content: bytes del body del response.

    Returns:
        Tupla (mp3_bytes, metadata_dict). metadata_dict tiene keys
        composition_plan, song_metadata, words_timestamps (este último
        puede ser None para tracks instrumentales).

    Raises:
        MusicDirectorError si no se encuentra MP3 o metadata en el multipart.
    """
    # email.parser necesita el Content-Type como header para descubrir el boundary
    raw = f"Content-Type: {content_type}\r\n\r\n".encode() + content
    msg = BytesParser(policy=default).parsebytes(raw)

    mp3_bytes: bytes | None = None
    metadata: dict[str, Any] | None = None

    for part in msg.iter_parts():
        part_ct = part.get_content_type().lower()
        payload = part.get_payload(decode=True)
        if payload is None:
            continue
        if "json" in part_ct:
            try:
                metadata = json.loads(payload)
            except json.JSONDecodeError as e:
                raise MusicDirectorError(
                    f"ElevenLabs Music response: JSON metadata ilegible: {e}"
                ) from e
        elif "audio" in part_ct or "mpeg" in part_ct or "octet" in part_ct:
            mp3_bytes = payload

    if mp3_bytes is None:
        raise MusicDirectorError(
            "ElevenLabs Music response: no se encontró part audio en multipart"
        )
    if metadata is None:
        raise MusicDirectorError(
            "ElevenLabs Music response: no se encontró part JSON metadata"
        )
    return mp3_bytes, metadata


# ═══════════════════════════════════════════════════════════════
#  ELEVENLABS MUSIC API
# ═══════════════════════════════════════════════════════════════

@error_handler.retry(PipelineStage.AUDIO)
def _call_elevenlabs_music_api(prompt_text: str) -> tuple[bytes, dict[str, Any]]:
    """Llama POST /v1/music/detailed con el prompt y devuelve (mp3, metadata).

    Protegido por @error_handler.retry: mismo patrón que audio_manager._generate_chapter_audio.
    Reintentos automáticos para 503/429. Timeout configurable via music_config.

    Args:
        prompt_text: prompt completo (build_music_prompt(intent) ya appended
                     negative_global_styles).

    Returns:
        Tupla (mp3_bytes, metadata_dict).

    Raises:
        MusicDirectorError si el response no es multipart parseable.
        requests exceptions si todos los retries fallan.
    """
    resp = requests.post(
        MUSIC_API_URL,
        headers={
            "xi-api-key": api.elevenlabs_api_key,
            "Accept": "multipart/mixed",
        },
        json={
            "prompt": prompt_text,
            "music_length_ms": MUSIC_LENGTH_MS,
            "model_id": MUSIC_MODEL_ID,
            "force_instrumental": True,
        },
        params={"output_format": MUSIC_OUTPUT_FORMAT},
        timeout=MUSIC_REQUEST_TIMEOUT_SEC,
    )
    resp.raise_for_status()

    content_type = resp.headers.get("Content-Type", "")
    mp3_bytes, metadata = _parse_multipart_response(content_type, resp.content)
    return mp3_bytes, metadata


# ═══════════════════════════════════════════════════════════════
#  PERSISTENCIA — track aprobado en library
# ═══════════════════════════════════════════════════════════════

def _persist_track_descriptor(
    track_data: dict[str, Any],
    draft_mp3_path: Path,
) -> Path:
    """Persiste un track aprobado en la library.

    Hace 2 operaciones:
      1. Rename atómico: _DRAFT_<id>.mp3 → <id>.mp3
      2. Escribe <id>.json con el descriptor completo.

    El track_data debe estar pre-construido con todos los campos del schema
    (el orquestador _generate_new_track_with_gate de 2.2.C.2 lo arma).

    Args:
        track_data: dict con keys mínimas: track_id, mp3_filename. El resto
                    de keys (descriptor completo) se persiste tal cual al JSON.
        draft_mp3_path: path al archivo _DRAFT_<id>.mp3 que el gate aprobó.

    Returns:
        Path al .mp3 final (ya en library aprobado).

    Raises:
        MusicDirectorError si:
          - draft_mp3_path no existe
          - el .mp3 final ya existe (colisión, library inconsistente)
          - rename o write fallan
    """
    if not draft_mp3_path.exists():
        raise MusicDirectorError(
            f"_persist_track_descriptor: draft MP3 no existe: {draft_mp3_path}"
        )

    track_id = track_data["track_id"]
    mp3_filename = track_data["mp3_filename"]
    final_mp3_path = AUDIO_LIBRARY_DIR / mp3_filename
    final_json_path = AUDIO_LIBRARY_DIR / f"{track_id}.json"

    if final_mp3_path.exists():
        raise MusicDirectorError(
            f"_persist_track_descriptor: colisión, {final_mp3_path.name} "
            f"ya existe en library. ¿Track duplicado o library inconsistente?"
        )

    # Rename atómico (más seguro que write a final path)
    try:
        draft_mp3_path.rename(final_mp3_path)
    except OSError as e:
        raise MusicDirectorError(
            f"_persist_track_descriptor: rename falló "
            f"{draft_mp3_path.name} → {final_mp3_path.name}: {e}"
        ) from e

    # Escribir JSON descriptor
    try:
        final_json_path.write_text(
            json.dumps(track_data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except OSError as e:
        # Intentar rollback: si JSON falló, devolver el MP3 a draft
        try:
            final_mp3_path.rename(draft_mp3_path)
        except OSError:
            pass  # rollback failed, library left in inconsistent state
        raise MusicDirectorError(
            f"_persist_track_descriptor: write JSON falló: {e}"
        ) from e

    error_handler.log_success(
        PipelineStage.AUDIO,
        f"[m07] track persistido en library: {track_id}",
    )
    return final_mp3_path


# ═══════════════════════════════════════════════════════════════
#  PERSISTENCIA — music_map del video
# ═══════════════════════════════════════════════════════════════

def _persist_music_map(
    topic_id: str,
    music_map: dict[str, Any],
) -> Path:
    """Persiste music_map.json a output/audio/<topic_id>/music_map.json.

    Mismo directorio que sync_map.json para mantener todos los assets del
    video juntos. fase2b va a leer ambos del mismo path.

    Args:
        topic_id: UUID del topic.
        music_map: dict con la estructura completa (video_id, profile,
                   tracks_by_chapter, etc.).

    Returns:
        Path al music_map.json escrito.
    """
    out_dir = OUTPUT_DIR / "audio" / topic_id
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "music_map.json"
    out_path.write_text(
        json.dumps(music_map, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    error_handler.log_success(
        PipelineStage.AUDIO,
        f"[m07] music_map persistido: {out_path}",
    )
    return out_path


# ═══════════════════════════════════════════════════════════════
#  GATE INTERACTIVO — decisión humana A/R/E/S/P
# ═══════════════════════════════════════════════════════════════

# Decisiones que el gate puede devolver
GateDecision = Literal["approve", "reroll", "edit", "skip"]


def _play_audio_file(mp3_path: Path) -> None:
    """Reproduce el MP3 con el reproductor default del sistema.

    Windows: wmplayer.exe directo (fix #169 v2 — tanto os.startfile como
             cmd /c start tiran WinError 1332 en algunos entornos).
    Mac: open <path>.
    Linux: xdg-open <path>.

    NO bloquea el thread principal — el reproductor abre como proceso aparte.
    Si falla por cualquier razón, loguea warning y sigue (el humano puede
    abrir el archivo a mano).
    """
    try:
        if os.name == "nt":
            # Fix #169 v2 chat 25: tanto os.startfile como cmd /c start fallan
            # con WinError 1332 (security IDs no resuelve). Invocar wmplayer
            # directo bypassa el resolver de SIDs. Validado empíricamente.
            WMPLAYER_PATH = r"C:\Program Files\Windows Media Player\wmplayer.exe"
            if os.path.exists(WMPLAYER_PATH):
                subprocess.Popen([WMPLAYER_PATH, str(mp3_path)])
            else:
                # Fallback si wmplayer no existe (Windows 11+ removió wmplayer
                # legacy en algunas instalaciones). Probar wmplayer.exe en PATH.
                subprocess.Popen(["wmplayer.exe", str(mp3_path)])
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(mp3_path)])
        else:
            subprocess.Popen(["xdg-open", str(mp3_path)])
    except Exception as e:
        error_handler.log_warning(
            PipelineStage.AUDIO,
            f"[m07] no pude reproducir {mp3_path.name} auto "
            f"({type(e).__name__}: {e}). Abrilo manualmente con: "
            f"& \"C:\\Program Files\\Windows Media Player\\wmplayer.exe\" \"{mp3_path}\"",
        )


def _edit_prompt_with_notepad(current_prompt: str) -> str | None:
    """Abre notepad con el prompt actual cargado, espera a que el usuario
    cierre, y devuelve el contenido editado.

    Si el usuario no cambia nada → devuelve el mismo prompt.
    Si el archivo temporal queda vacío → devuelve None (señal de cancelación).
    Si notepad falla → devuelve None.

    Windows: notepad. Linux/Mac: nano/vim fallback. Por ahora solo Windows
    soportado bien (canal corre en Windows por design chat 21+).
    """
    try:
        # Crear archivo temporal con el prompt actual
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding="utf-8"
        ) as f:
            f.write(current_prompt)
            tmp_path = Path(f.name)

        # Abrir editor y bloquear hasta que se cierre
        if os.name == "nt":
            # notepad bloquea hasta que se cierre
            subprocess.run(["notepad", str(tmp_path)], check=False)
        else:
            # fallback: editor por defecto del sistema
            editor = os.environ.get("EDITOR", "nano")
            subprocess.run([editor, str(tmp_path)], check=False)

        # Leer el contenido editado
        edited = tmp_path.read_text(encoding="utf-8").strip()
        tmp_path.unlink(missing_ok=True)

        if not edited:
            return None
        return edited
    except Exception as e:
        error_handler.log_warning(
            PipelineStage.AUDIO,
            f"[m07] edición de prompt falló "
            f"({type(e).__name__}: {e}). Cancelando edición.",
        )
        return None


def _gate_approve_track(
    intent: str,
    track_id: str,
    mp3_path: Path,
    prompt_text: str,
    interactive: bool,
) -> tuple[GateDecision, str]:
    """Gate interactivo CLI: humano escucha el track y decide.

    Opciones:
      [A] Aprobar — track va a la library
      [R] Re-roll — generar otro con mismo prompt (con confirmación)
      [E] Editar prompt — abre notepad, re-genera con prompt nuevo
      [S] Skip — cap sin música (deuda)
      [P] Play de nuevo

    Si interactive=False → siempre devuelve ("approve", prompt_text)
    (modo batch nocturno, sin humano).

    Args:
        intent: para mostrar contexto en el CLI.
        track_id: para mostrar contexto en el CLI.
        mp3_path: el _DRAFT_<id>.mp3 a reproducir.
        prompt_text: prompt actual (puede ser modificado por [E]).
        interactive: True para modo CLI humano; False para batch.

    Returns:
        Tupla (decisión, prompt_a_usar).
        - decisión: "approve" | "reroll" | "edit" | "skip"
        - prompt_a_usar: el mismo prompt_text excepto si humano usó [E]
                         (en ese caso, el prompt editado nuevo)
    """
    if not interactive:
        return "approve", prompt_text

    # Reproducir automáticamente al entrar al gate
    _play_audio_file(mp3_path)

    while True:
        print()
        print("=" * 60)
        print(f"🎵 [GATE MÚSICA] Track generado para intent={intent}")
        print(f"   track_id: {track_id}")
        print(f"   archivo:  {mp3_path.name}")
        print("=" * 60)
        print("  [A] Aprobar y guardar en library")
        print("  [R] Rechazar — generar otro con MISMO prompt (re-roll)")
        print("  [E] Editar el prompt y re-generar")
        print("  [S] Saltar — dejar este cap sin música")
        print("  [P] Reproducir otra vez")
        print()
        choice = input("> ").strip().lower()

        if choice == "a":
            return "approve", prompt_text
        elif choice == "r":
            # Confirmación de re-roll (gasta créditos otra vez)
            print()
            confirm = input(
                "⚠ Re-roll va a gastar créditos otra vez. ¿Seguro? [y/N] "
            ).strip().lower()
            if confirm == "y":
                return "reroll", prompt_text
            # Si dice N, vuelve al menú
            continue
        elif choice == "e":
            # Abrir notepad con el prompt actual
            edited = _edit_prompt_with_notepad(prompt_text)
            if edited is None:
                print("  Edición cancelada. Volviendo al menú.")
                continue
            if edited == prompt_text:
                print("  No detecté cambios en el prompt. Volviendo al menú.")
                continue
            print(f"  Prompt editado ({len(edited)} chars). Generando con nuevo prompt...")
            return "edit", edited
        elif choice == "s":
            print()
            confirm = input(
                "⚠ Saltar deja este cap SIN música. ¿Seguro? [y/N] "
            ).strip().lower()
            if confirm == "y":
                return "skip", prompt_text
            continue
        elif choice == "p":
            _play_audio_file(mp3_path)
            print("  Reproduciendo otra vez...")
            continue
        else:
            print(f"  Opción inválida: '{choice}'. Usá A / R / E / S / P.")
            continue


# ═══════════════════════════════════════════════════════════════
#  ORQUESTADOR DE GENERACIÓN — ElevenLabs + gate + persist
# ═══════════════════════════════════════════════════════════════

def _generate_new_track_with_gate(
    intent: str,
    profile: str,
    topic_id: str,
    topic_title: str,
    anchor: str,
    interactive: bool = True,
) -> dict[str, Any] | None:
    """Orquesta: genera con ElevenLabs → escribe _DRAFT_ → gate → persist o discard.

    Loop:
      1. Construye prompt con build_music_prompt(intent) (de music_config.py)
      2. Llama _call_elevenlabs_music_api → mp3_bytes + metadata
      3. Escribe _DRAFT_<track_id>.mp3 al disco
      4. Llama _gate_approve_track (humano decide)
      5. Según decisión:
         - approve → _persist_track_descriptor + return dict
         - reroll → loop con MISMO prompt (genera otra vez)
         - edit → loop con PROMPT EDITADO (humano cambió)
         - skip → borra _DRAFT_ + return None
      6. Max 10 loops (safety limit anti loop infinito por humano indeciso)

    Returns:
        Dict descriptor del track aprobado, o None si humano skipeó.
    """
    _ensure_library_dir()
    track_id = _generate_track_id(intent, topic_id)
    draft_path = AUDIO_LIBRARY_DIR / f"{DRAFT_PREFIX}{track_id}.mp3"

    # Verificar que no hay colisión en la library
    final_path = AUDIO_LIBRARY_DIR / f"{track_id}.mp3"
    if final_path.exists():
        raise MusicDirectorError(
            f"[m07] track {track_id}.mp3 ya existe en library — "
            f"¿topic_id duplicado? abortando para evitar sobrescribir."
        )

    # Prompt inicial desde music_config.py (puede ser editado por [E] en gate)
    current_prompt = build_music_prompt(intent)

    MAX_ATTEMPTS = 10
    for attempt in range(1, MAX_ATTEMPTS + 1):
        print()
        print(f"[m07] {intent}: generando track (intento {attempt}/{MAX_ATTEMPTS})...")
        print(f"[m07] Llamando ElevenLabs Music API (puede tardar 30-90s)...")

        try:
            mp3_bytes, elevenlabs_metadata = _call_elevenlabs_music_api(current_prompt)
        except Exception as e:
            error_handler.log_warning(
                PipelineStage.AUDIO,
                f"[m07] {intent}: generación falló "
                f"({type(e).__name__}: {e}). Abortando este cap.",
            )
            # Cleanup defensivo del _DRAFT_ si quedó algo
            draft_path.unlink(missing_ok=True)
            return None

        # Escribir _DRAFT_ al disco para que el humano pueda reproducirlo
        draft_path.write_bytes(mp3_bytes)
        print(f"[m07] ✅ Track generado: {len(mp3_bytes)/1024:.0f}KB")

        # Gate interactivo
        decision, prompt_to_use = _gate_approve_track(
            intent=intent,
            track_id=track_id,
            mp3_path=draft_path,
            prompt_text=current_prompt,
            interactive=interactive,
        )

        if decision == "approve":
            # Construir descriptor completo + persistir
            now_iso = datetime.now().isoformat()
            # Calcular duración total del composition_plan (suma de sections)
            comp_plan = elevenlabs_metadata.get("composition_plan", {})
            sections = comp_plan.get("sections", [])
            duration_ms = sum(s.get("duration_ms", 0) for s in sections) or MUSIC_LENGTH_MS

            track_data: dict[str, Any] = {
                "track_id": track_id,
                "mp3_filename": f"{track_id}.mp3",
                "intent_origin": intent,
                "fits_intents": [intent],  # arranca con el origin
                "compatible_profiles": [profile],
                "topic_source": topic_id,
                "topic_title": topic_title,
                "prompt_used": current_prompt,
                "duration_ms": duration_ms,
                # cost_usd: deuda #167 — por ahora None, m07 loguea costo manual
                "cost_usd": None,
                "generated_at": now_iso,
                "approved_at": now_iso,
                "elevenlabs_metadata": {
                    "title": elevenlabs_metadata.get("song_metadata", {}).get("title"),
                    "description": elevenlabs_metadata.get("song_metadata", {}).get("description"),
                    "genres": elevenlabs_metadata.get("song_metadata", {}).get("genres", []),
                    "composition_plan": comp_plan,
                },
                "times_used": 0,
                "last_used_at": None,
            }

            _persist_track_descriptor(track_data, draft_path)
            return track_data

        elif decision == "skip":
            # Borrar _DRAFT_ y devolver None
            draft_path.unlink(missing_ok=True)
            error_handler.log_info(
                PipelineStage.AUDIO,
                f"[m07] {intent}: humano skipeó. Cap quedará sin música.",
            )
            return None

        elif decision == "reroll":
            # Borrar _DRAFT_ viejo, loop con mismo prompt
            draft_path.unlink(missing_ok=True)
            print(f"[m07] {intent}: re-roll con mismo prompt...")
            # current_prompt no cambia
            continue

        elif decision == "edit":
            # Borrar _DRAFT_ viejo, loop con prompt nuevo
            draft_path.unlink(missing_ok=True)
            current_prompt = prompt_to_use
            print(f"[m07] {intent}: re-generando con prompt editado...")
            continue

    # Si llegó acá, agotó MAX_ATTEMPTS
    draft_path.unlink(missing_ok=True)
    error_handler.log_warning(
        PipelineStage.AUDIO,
        f"[m07] {intent}: agotó {MAX_ATTEMPTS} intentos sin aprobación. "
        f"Cap quedará sin música.",
    )
    return None


# ═══════════════════════════════════════════════════════════════
#  API PÚBLICA — generate_music_map
# ═══════════════════════════════════════════════════════════════

def generate_music_map(
    topic_id: str,
    sync_map: dict[str, Any],
    interactive: bool = True,
) -> dict[str, Any]:
    """Genera music_map.json para el video: matchea cada cap a un track.

    Por cada cap del sync_map:
      1. Filtra candidatos de la library por intent + profile
      2. Si hay 1+ candidatos → matcher LLM decide reuse vs nuevo
      3. Si matcher devuelve track con score >= THRESHOLD → reuse (sin gate)
      4. Sino → _generate_new_track_with_gate (con gate humano si interactive)
      5. Si humano skipea → cap queda como "skipped" en music_map

    Reuses NO pasan por el gate humano (decisión chat 25): un track ya en
    library ya fue aprobado alguna vez al guardarse, no necesita re-aprobar.

    Args:
        topic_id: UUID del topic actual.
        sync_map: dict cargado desde output/audio/<topic_id>/sync_map.json
                  (post PR 2.A: incluye narrative_intent por cap).
        interactive: True (default) para modo CLI humano. False para batch.

    Returns:
        Dict music_map persistido a output/audio/<topic_id>/music_map.json.
    """
    # Sanity check antes de gastar créditos
    validate_music_config()

    profile = sync_map.get("profile", "")
    if not profile:
        raise MusicDirectorError(
            "[m07] sync_map.profile vacío. m07 necesita conocer el profile "
            "activo para filtrar candidatos. ¿sync_map corrupto?"
        )

    chapters = sync_map.get("chapters", [])
    if not chapters:
        raise MusicDirectorError(
            "[m07] sync_map.chapters vacío. Nada para procesar."
        )

    topic_title = sync_map.get("video_id", topic_id)[:50]  # fallback razonable

    # Cargar library una vez al inicio
    library = _load_library()
    error_handler.log_info(
        PipelineStage.AUDIO,
        f"[m07] library tiene {len(library)} tracks acumulados.",
    )

    tracks_by_chapter: dict[str, dict[str, Any]] = {}

    for ch in chapters:
        ch_id = ch.get("id", "")
        intent = ch.get("narrative_intent", "")
        anchor = ch.get("text", "")[:200]  # primera oración aprox

        if not intent:
            error_handler.log_warning(
                PipelineStage.AUDIO,
                f"[m07] {ch_id}: sin narrative_intent. Skipping música.",
            )
            tracks_by_chapter[ch_id] = {
                "track_id": None,
                "mp3_path": None,
                "match_source": "skipped",
                "match_score": None,
                "reason": "no narrative_intent in sync_map",
            }
            continue

        print()
        print(f"━━━ [m07] {ch_id} (intent={intent}) ━━━")

        # Paso 1: filtrar candidatos
        candidates = _filter_candidates(library, intent, profile)
        print(f"[m07] candidatos en library para {intent}: {len(candidates)}")

        # Paso 2: matcher LLM (si hay candidatos)
        match_result = None
        if candidates:
            match_result = _match_intent_to_track(
                intent=intent,
                anchor=anchor,
                profile=profile,
                candidates=candidates,
            )

        if match_result is not None:
            # REUSE — track de la library, sin gate
            winner_id = match_result["winner"]
            score = match_result["match_score"]
            print(f"[m07] DECISION: REUSE {winner_id} (score={score})")
            tracks_by_chapter[ch_id] = {
                "track_id": winner_id,
                "mp3_path": f"audio_library/{winner_id}.mp3",
                "match_source": "reused",
                "match_score": score,
                "reasoning": match_result["reasoning"],
            }
            continue

        # Paso 3: generar nuevo con gate
        print(f"[m07] DECISION: GENERATE NEW (sin match en library)")
        new_track = _generate_new_track_with_gate(
            intent=intent,
            profile=profile,
            topic_id=topic_id,
            topic_title=topic_title,
            anchor=anchor,
            interactive=interactive,
        )

        if new_track is None:
            # Humano skipeó o falló
            tracks_by_chapter[ch_id] = {
                "track_id": None,
                "mp3_path": None,
                "match_source": "skipped",
                "match_score": None,
                "reason": "user skipped or generation failed",
            }
        else:
            tracks_by_chapter[ch_id] = {
                "track_id": new_track["track_id"],
                "mp3_path": f"audio_library/{new_track['mp3_filename']}",
                "match_source": "generated",
                "match_score": None,
                "reasoning": "newly generated (no match in library)",
            }
            # Agregar a la library en memoria para que próximos caps puedan reusarlo
            library.append(new_track)

    music_map = {
        "video_id": topic_id,
        "profile": profile,
        "generated_at": datetime.now().isoformat(),
        "total_chapters": len(chapters),
        "tracks_by_chapter": tracks_by_chapter,
    }

    _persist_music_map(topic_id, music_map)
    return music_map
