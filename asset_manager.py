"""
asset_manager.py — Motor ciego del pipeline (Protocolo v2 + Flux Migration).

CAMBIO MAYOR (Fase 2A Evolución Final):
  Eliminado Leonardo AI como motor de imágenes.
  Nuevo motor: fal.ai Flux 1.1 Pro (estándar) + Flux 1.1 Pro Ultra (ch01).

ARQUITECTURA:
  render_engine del guion ahora es uno de:
    - "veo"  → clips de video (F53b: Gemini Omni Flash 1.1 → Kling 4.0 si rechaza; `_generate_clip`)
      F57: foto final = edit de la inicial (`foto_final_del_clip`, Seedream /edit + SSIM) y el motor recibe las 2 fotos;
      el prompt del motor y la foto final salen de la voz entera del clip (`voz_clip`, de m03; sin la clave, PARA)
    - "flux" → imágenes con fal.ai Flux Pro v1.1

  El capítulo "ch01" (gancho) usa automáticamente Flux Ultra para máxima
  calidad. El resto usa Flux Pro v1.1 estándar.

PROTOCOLO DE PROMPTS v2:
  - image_prompts son descriptivos puros.
  - Cada capítulo declara `art_profile`.
  - Motor hace stitch: ART_PROFILES[profile] + raw_image_prompt.
  - Flux NO soporta negative_prompt nativo → las exclusiones van en el
    prompt positivo vía "Natural Negatives" (ver script_generator).

VISION GUARDRAIL:
  - Cada imagen Flux se valida con Gemini Vision.
  - 2 intentos: si el primero falla, el segundo re-prompta con corrección.

FALLBACK UNIVERSAL:
  - Si el clip falla (todos los motores rechazan, o error técnico) → Ken Burns con imagen Flux.
  - Manifest distingue: ok | kenburns_fallback | technical_fallback | failed.

SMART SKIP: archivos existentes no re-llaman a la API.
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
import re
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Any

import requests

from config import api, pipeline, OUTPUT_DIR
from error_handler import error_handler, PipelineStage
from cost_tracker import cost_tracker
from engine_profiles import select_profile, select_video_profile

from script_engine.vision_validator import validate_image, build_corrected_prompt


# ═══════════════════════════════════════════
#  Constantes operativas
# ═══════════════════════════════════════════

# Concurrencia de render de imágenes (fal). = el límite de CONCURRENCIA de fal de la cuenta.
# Los caps se procesan SECUENCIALES (process_script) → el pico global es este número, no ×caps.
# NO paralelizar además los caps del asset_manager: caps × workers superaría el límite fal → 429.
# F8 §1A: sale de config (`pipeline.fal_concurrency`, default 20). Baja a 10 si no se compran $100 en 4 semanas.
FLUX_MAX_WORKERS = int(getattr(pipeline, "fal_concurrency", 20) or 20)
FLUX_POLL_TIMEOUT = 180
CLIP_POLL_TIMEOUT = 600                 # F53b: espera de un clip en la cola de fal (el de Veo, sin cambios)
CLIP_MAX_ATTEMPTS_NON_REJECTION = 3     # F53b: reintentos de red/429/5xx del mismo motor (los de Veo, sin cambios)
FAL_SUBMIT_TIMEOUT_S = 60               # F60 B: timeout del submit a la cola de fal (clips, secuencia, madre de persona); el literal existente de _call_clip_once (handoff F60 B+C)
FOTOS_POR_LLAMADA = 6                   # F60 B: fotos por llamada de secuencia Seedream /edit (Omar, DECISIONES 2026-10-30 18:34)
SECUENCIA_DIR = "_secuencia"            # F60 B: output/<vid>/_secuencia/pedidos.json (request_id guardado ANTES de esperar)
FLUX_MAX_VISION_ATTEMPTS = 2
ENABLE_VISION_VALIDATOR: bool = False  # Flag maestro. False = una sola llamada Flux por imagen, sin validación. Cambiar a True para reactivar el guardrail.

RATE_LIMIT_BACKOFF_SECONDS = 20

# Capítulo del gancho → usa Flux Ultra (máxima calidad)
HOOK_CHAPTER_ID = "ch01"

# (dims viven en config.pipeline.image_* — DRY, siguen el flip 16:9)

CONTENT_REJECTION_KEYWORDS = (
    "content_policy", "content policy",
    "safety", "moderation",
    "rejected", "blocked", "violates",
    "prohibited", "nsfw", "safety_checker",
)

RATE_LIMIT_KEYWORDS = (
    "429", "resource exhausted", "resource_exhausted",
    "rate limit", "rate_limit", "quota",
)


class ContentRejectedError(Exception):
    """fal.ai rechazó el prompt por política/safety. NO reintentar."""


def _is_content_rejection(text: str | Exception) -> bool:
    s = str(text).lower()
    return any(kw in s for kw in CONTENT_REJECTION_KEYWORDS)


def _is_rate_limit(text: str | Exception) -> bool:
    s = str(text).lower()
    return any(kw in s for kw in RATE_LIMIT_KEYWORDS)


# ═══════════════════════════════════════════
#  Paths y naming
# ═══════════════════════════════════════════

def _assets_dir(video_id: str) -> Path:
    return OUTPUT_DIR / video_id / "assets"


def _chapter_dir(video_id: str, chapter_id: str, engine: str) -> Path:
    path = _assets_dir(video_id) / f"{chapter_id}_{engine}"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _image_filename(chapter_id: str, idx: int) -> str:
    return f"{chapter_id}_img_{idx:02d}.png"


def _clip_filename(chapter_id: str, idx: int) -> str:
    return f"{chapter_id}_clip_{idx:02d}.mp4"


# ═══════════════════════════════════════════
#  Validación del guion
# ═══════════════════════════════════════════

def _extract_art_profile(chapter: dict[str, Any]) -> str:
    """Devuelve art_profile del cap o "" si no existe.

    Desde refactor chat 19: el catálogo art_profiles está desconectado
    del flujo activo. Este getter mantiene la firma pública (otros
    consumidores la usan) pero ya no valida contra VALID_PROFILES.
    """
    return chapter.get("art_profile", "") or ""


def _is_hook_chapter(chapter_id: str) -> bool:
    """ch01 → Ultra (máxima calidad). Resto → estándar."""
    return chapter_id.lower() == HOOK_CHAPTER_ID


# ═══════════════════════════════════════════
#  fal.ai — headers compartidos
# ═══════════════════════════════════════════

def _fal_headers() -> dict[str, str]:
    return {
        "Authorization": f"Key {api.fal_api_key}",
        "Content-Type": "application/json",
    }


# ═══════════════════════════════════════════
#  Flux — generación cruda (Queue API)
# ═══════════════════════════════════════════

def _flux_poll(status_url: str, response_url: str,
               timeout: int = FLUX_POLL_TIMEOUT) -> dict:
    start = time.time()
    while time.time() - start < timeout:
        resp = requests.get(status_url, headers=_fal_headers(), timeout=15)
        resp.raise_for_status()
        data = resp.json()
        status = data.get("status", "").upper()

        if status == "COMPLETED":
            res = requests.get(response_url, headers=_fal_headers(), timeout=15)
            res.raise_for_status()
            return res.json()

        if status in ("FAILED", "ERROR"):
            err_body = json.dumps(data)
            if _is_content_rejection(err_body):
                raise ContentRejectedError(f"Flux rechazó prompt: {err_body[:300]}")
            raise RuntimeError(f"Flux tarea falló: {err_body[:300]}")

        time.sleep(2)
    raise TimeoutError(f"Flux timeout tras {timeout}s")


def _flux_payload_for(
    model_endpoint: str,
    prompt: str,
    seed: int | None = None,
) -> dict[str, Any]:
    """
    Payload para fal.ai Flux.2 Pro (text-to-image).

    Flux.2 Pro acepta image_size con width/height custom (igual que Flux 1.1 Pro v1.1).
    A diferencia del antiguo Flux 1.1 Pro Ultra, NO usa aspect_ratio.
    Por eso ambas branches (use_ultra=True/False) usan el mismo formato ahora.

    - seed opcional: si se pasa, Flux genera de forma reproducible.
      Se usa para mantener el mismo sujeto entre imágenes (Bucket 1.4).
    """
    base: dict[str, Any] = {
        "prompt": prompt,
        "num_images": 1,
        "enable_safety_checker": True,         # Safety Shield SIEMPRE ON
        "output_format": "png",
        "image_size": {"width": pipeline.image_width, "height": pipeline.image_height},
    }

    if seed is not None:
        base["seed"] = seed

    return base

# ═══════════════════════════════════════════
#  Seed determinístico por sujeto recurrente (Bucket 1.4)
# ═══════════════════════════════════════════

# Flux acepta seed como uint32. Tomamos primeros 4 bytes del SHA-256.
_FLUX_SEED_MAX = 2**32


def _seed_for_subject(video_id: str, subject_ref: str | None) -> int | None:
    """
    Devuelve un seed determinístico derivado de (video_id, subject_ref).
    - Mismo (video_id, subject_ref) → mismo seed siempre (reproducible).
    - subject_ref=None / "" → None (Flux usa seed aleatorio, sin consistencia).
    - Distintos subject_ref dentro del mismo video_id → seeds distintos.
    """
    if not subject_ref:
        return None
    digest = hashlib.sha256(f"{video_id}:{subject_ref}".encode("utf-8")).digest()
    return int.from_bytes(digest[:4], "big") % _FLUX_SEED_MAX


def _kling_payload_for(prompt: str) -> dict[str, Any]:
    """Payload Kling o3 t2i (SYNC). SIN enable_safety_checker (usa filtro CAC interno).

    Kling usa resolution+aspect_ratio (NO image_size). "2K"@16:9 → 2720x1536, que
    entra al canvas 2560x1440 por downsample (sin upscale).
    """
    return {
        "prompt": prompt[:2500],
        "resolution": api.fal_kling_resolution,   # "2K"
        "aspect_ratio": api.fal_kling_aspect,      # "16:9"
        "output_format": "png",
        "result_type": "single",
        "num_images": 1,
    }


def _seedream_payload_for(prompt: str, seed: int | None = None) -> dict[str, Any]:
    """Payload Seedream 4.5 t2i (SYNC) — SEEDREAM_4.5_REFERENCIA §2, §8.

    ★ Seedream 4.5 NO tiene guidance_scale NI negative_prompt (eran de la v3).
      Meterlos rompe la call. Las negaciones van EN EL TEXTO del prompt (3b).
    image_size sale del perfil (render.image_size = "landscape_16_9"). seed se
    incluye solo si no es None (reproducibilidad por sujeto, como Flux).
    """
    profile = select_profile("seedream")
    payload: dict[str, Any] = {
        "prompt": prompt,
        "image_size": profile.render.image_size,
        "num_images": 1,
        "enable_safety_checker": True,
    }
    if seed is not None and profile.render.accepts_seed:       # F8: v5 Lite no tiene seed de entrada
        payload["seed"] = seed
    return payload


def _seedream_edit_payload_for(
    prompt: str, image_data_uris: list[str], seed: int | None = None,
) -> dict[str, Any]:
    """Payload Seedream 4.5 /edit — espejo de _seedream_payload_for + image_urls.

    HANDOFF_129 (Consumo-B): ancla la foto madre como referencia-imagen. La key
    `image_urls` (lista) y el data-URI base64 son los que validó el probe
    lock_imageref (H1/H2 verde, 127). model_id del /edit lo resuelve _generate_image_raw.
    HANDOFF_131 (B): image_urls acepta hasta 2 anclas (cutaway) — la lista viaja tal cual."""
    profile = select_profile("seedream")
    payload: dict[str, Any] = {
        "prompt": prompt,
        "image_urls": list(image_data_uris),
        "image_size": profile.render.image_size,
        "num_images": 1,
        "enable_safety_checker": True,
    }
    if seed is not None and profile.render.accepts_seed:
        payload["seed"] = seed
    return payload


def _path_to_data_uri(path: str | Path) -> str:
    """Foto local → data-URI base64 (fal acepta data-URIs; NO la URL de fal). F57 (chascada 2): el tipo se lee de los
    bytes (`video_prompt.tipo_imagen`: Seedream entrega JPEG con extensión .png), antes fijaba image/png."""
    from script_engine.video_prompt import tipo_imagen
    datos = Path(path).read_bytes()
    return f"data:{tipo_imagen(datos)};base64,{base64.b64encode(datos).decode('ascii')}"


# ── Lookup por engine_key (el "selector" del 5º dispatch — NO elif disperso) ──
# Builders y cost trackers de los motores SYNC (kling/seedream). El path "flux"
# (queue) NO es de perfil y queda en su rama legacy.
_SYNC_PAYLOAD_BUILDERS = {
    "kling":    lambda prompt, seed: _kling_payload_for(prompt),       # Kling ignora seed (byte-idéntico)
    "seedream": lambda prompt, seed: _seedream_payload_for(prompt, seed),
}
_SYNC_COST_TRACKERS = {
    "kling":    cost_tracker.track_kling,
    "seedream": cost_tracker.track_seedream,
}


# F8 §1A: 3 intentos con backoff exponencial (+ jitter) en 429/503 (error_handler.retry: ~15 s, ~23 s)
@error_handler.retry(PipelineStage.IMAGE, max_server_retries=3)
def _generate_image_raw(
    prompt: str,
    output_path: Path,
    use_ultra: bool,
    seed: int | None = None,
    foto_madre_data_uris: list[str] | None = None,
) -> dict[str, Any]:
    """Llamada cruda al motor de imagen activo (api.image_engine), sin validación de visión.

    Motores SYNC (perfil): "kling" | "seedream" → fal.run, status 200 → images[0].url,
      SIN poll. El selector (engine_profiles.select_profile) elige el perfil; la URL y
      el payload salen del perfil + el lookup por engine_key. use_ultra queda inerte
      (estos motores tienen un solo endpoint). Con api.image_engine="kling" el render
      es BYTE-IDÉNTICO al del código viejo (los valores del perfil salen de api.*).
    Motor "flux": Flux.2 Pro vía queue.fal.run (path histórico legacy, NO de perfil).
    El manejo de 422 (ContentRejectedError) es idéntico en todos los motores.
    """
    profile = select_profile(api.image_engine)
    if profile is not None:
        # ── Motores SYNC de perfil (kling/seedream) ──
        engine = profile.engine_key
        # is_edit (HANDOFF_133): la MISMA condición del gate /edit, capturada UNA vez para
        # reusarla en el model_id, el log y la etiqueta de costo → la telemetría no miente.
        is_edit = bool(foto_madre_data_uris and engine == "seedream")
        # HANDOFF_129 (Consumo-B): con foto madre + seedream → /edit (ancla por
        # referencia-imagen) en vez de t2i. Cualquier otro caso = t2i byte-idéntico.
        # HANDOFF_131 (B): la lista lleva hasta 2 anclas (cutaway submarino+reactor).
        if is_edit:
            model_id = profile.render.model_id.replace("text-to-image", "edit")
            payload = _seedream_edit_payload_for(prompt, foto_madre_data_uris, seed)
            error_handler.log_info(
                PipelineStage.IMAGE,
                f"[/edit] {engine} anclando {len(foto_madre_data_uris)} foto(s) madre → {output_path.name}",
            )
        else:
            model_id = profile.render.model_id
            payload = _SYNC_PAYLOAD_BUILDERS[engine](prompt, seed)
        submit_url = f"{profile.render.base_url}/{model_id}"   # SYNC

        t0 = time.time()
        try:
            resp = requests.post(submit_url, headers=_fal_headers(),
                                 json=payload, timeout=240)
            resp.raise_for_status()
        except requests.HTTPError as e:
            body = e.response.text if e.response is not None else str(e)
            if _is_content_rejection(body):
                raise ContentRejectedError(
                    f"{engine} rechazó prompt: {body[:300]}"
                )
            raise

        data = resp.json()                       # SYNC: respuesta directa, SIN _flux_poll
        if "images" not in data or not data["images"]:
            raise RuntimeError(f"{engine} sin imágenes: {json.dumps(data)[:300]}")

        img = data["images"][0]
        image_url = img["url"]

        output_path.parent.mkdir(parents=True, exist_ok=True)
        img_resp = requests.get(image_url, timeout=60)
        img_resp.raise_for_status()
        output_path.write_bytes(img_resp.content)

        # mode="edit" (HANDOFF_133) solo aplica al seedream anclado; is_edit ya lo garantiza
        # (kling nunca es edit) → el kwarg extra jamás llega a track_kling.
        _edit_kw = {"mode": "edit"} if is_edit else {}
        _SYNC_COST_TRACKERS[engine](
            description=f"{output_path.stem}: {prompt[:60]}...", images=1, **_edit_kw
        )

        nsfw_list = data.get("has_nsfw_concepts") or [False]
        return {
            "endpoint": model_id,   # el REAL enviado a fal (t2i o /edit) — la telemetría no miente
            "ms": int((time.time() - t0) * 1000),   # F8: pedido + descarga de esta imagen (sin los reintentos)
            "width": img.get("width"),
            "height": img.get("height"),
            "seed": data.get("seed"),
            "nsfw_flag": nsfw_list[0] if nsfw_list else False,
        }

    # ── "flux" — path histórico, byte-idéntico (image_size sale de pipeline) ──
    endpoint = api.fal_image_model_ultra if use_ultra else api.fal_image_model
    payload = _flux_payload_for(endpoint, prompt, seed=seed)
    submit_url = f"{api.fal_base_url}/{endpoint}"

    try:
        resp = requests.post(submit_url, headers=_fal_headers(),
                             json=payload, timeout=30)
        resp.raise_for_status()
    except requests.HTTPError as e:
        body = e.response.text if e.response is not None else str(e)
        if _is_content_rejection(body):
            raise ContentRejectedError(
                f"Flux rechazó prompt en submit: {body[:300]}"
            )
        raise

    result = resp.json()
    if "images" in result:
        data = result
    else:
        data = _flux_poll(result["status_url"], result["response_url"])

    if "images" not in data or not data["images"]:
        raise RuntimeError(f"Flux sin imágenes: {json.dumps(data)[:300]}")

    img = data["images"][0]
    image_url = img["url"]

    # Descarga
    output_path.parent.mkdir(parents=True, exist_ok=True)
    img_resp = requests.get(image_url, timeout=60)
    img_resp.raise_for_status()
    output_path.write_bytes(img_resp.content)

    # Cost tracking nativo (Paso 2 completado — métodos track_flux_* disponibles).
    description = f"{output_path.stem}: {prompt[:60]}..."
    if use_ultra:
        cost_tracker.track_flux_ultra(description=description, images=1)
    else:
        cost_tracker.track_flux_pro(description=description, images=1)

    nsfw_list = data.get("has_nsfw_concepts") or [False]
    return {
        "endpoint": endpoint,
        "width": img.get("width"),
        "height": img.get("height"),
        "seed": data.get("seed"),
        "nsfw_flag": nsfw_list[0] if nsfw_list else False,
    }


# Alias backward-compat: scripts externos (p.ej. _gen_cap5_missing.py) importan el nombre viejo.
_flux_generate_raw = _generate_image_raw


# ═══════════════════════════════════════════
#  Flux + Vision Guardrail (2 intentos)
# ═══════════════════════════════════════════

def _generate_flux_image_at(
    raw_prompt: str,
    art_profile: str,
    output_path: Path,
    use_ultra: bool,
    seed: int | None = None,
    foto_madre_data_uris: list[str] | None = None,
) -> dict[str, Any]:
    """
    Genera imagen Flux con validación Vision (2 intentos).
    Intento 1: stitch art_profile + raw_prompt → Flux → valida.
    Intento 2 (si falla): incorpora corrección de Gemini → Flux → valida.

    seed: si no es None, Flux usará ese seed (reproducible).
    """
    # ─── MODO VALIDATOR OFF ──────────────────────────────────────
    # Una sola llamada Flux, sin reintentos por visión.
    # Útil para validar prompts crudos sin ruido del guardrail.
    if not ENABLE_VISION_VALIDATOR:
        final_prompt = raw_prompt
        model_tag = "ULTRA" if use_ultra else "PRO"
        seed_tag = f" seed={seed}" if seed is not None else ""
        error_handler.log_info(
            PipelineStage.IMAGE,
            f"Flux-{model_tag} [validator OFF]{seed_tag} → {output_path.name}",
        )
        last_meta = _generate_image_raw(final_prompt, output_path, use_ultra, seed=seed,
                                        foto_madre_data_uris=foto_madre_data_uris)
        return {
            "path": output_path,
            "attempts": 1,
            "validated": None,  # None = validador deshabilitado (no es ni True ni False)
            "last_verdict": {"reason": "validator_disabled", "match": True},
            "model_used": "flux_ultra" if use_ultra else "flux_pro",
            "flux_meta": last_meta,
        }

    # ─── MODO VALIDATOR ON (comportamiento original) ─────────────
    last_verdict: dict[str, Any] = {}
    current_raw = raw_prompt
    last_meta: dict[str, Any] = {}

    for attempt in range(1, FLUX_MAX_VISION_ATTEMPTS + 1):
        final_prompt = current_raw

        model_tag = "ULTRA" if use_ultra else "PRO"
        seed_tag = f" seed={seed}" if seed is not None else ""
        error_handler.log_info(
            PipelineStage.IMAGE,
            f"Flux-{model_tag} intento {attempt}/{FLUX_MAX_VISION_ATTEMPTS}"
            f"{seed_tag} → {output_path.name}",
        )

        last_meta = _generate_image_raw(final_prompt, output_path, use_ultra, seed=seed,
                                        foto_madre_data_uris=foto_madre_data_uris)

        # Validar contra el prompt CRUDO (Protocolo v2)
        verdict = validate_image(output_path, raw_prompt)
        last_verdict = verdict

        if verdict["match"]:
            error_handler.log_info(
                PipelineStage.IMAGE,
                f"✓ Vision OK {output_path.name} (intento {attempt}, {model_tag})",
            )
            return {
                "path": output_path,
                "attempts": attempt,
                "validated": True,
                "last_verdict": verdict,
                "model_used": "flux_ultra" if use_ultra else "flux_pro",
                "flux_meta": last_meta,
            }

        # Rechazo → preparar siguiente intento con corrección
        if attempt < FLUX_MAX_VISION_ATTEMPTS:
            ftype = verdict.get("failure_type", "") or ""
            error_handler.log_warning(
                PipelineStage.IMAGE,
                f"Vision RECHAZÓ {output_path.name} [{ftype or 'unknown'}]: "
                f"{verdict['reason']} → intento {attempt+1} con corrección: "
                f"{verdict['correction_suggestion'][:80]}",
            )
            current_raw = build_corrected_prompt(
                raw_prompt,
                verdict["correction_suggestion"],
                failure_type=ftype,
            )

    # Agotados los 2 intentos sin validación OK
    error_handler.log_warning(
        PipelineStage.IMAGE,
        f"⚠️ VISION WARN: {output_path.name} no pasó validación en "
        f"{FLUX_MAX_VISION_ATTEMPTS} intentos. "
        f"Último verdict: {last_verdict.get('reason', 'N/A')[:120]} — "
        f"se usará la imagen tal cual.",
    )
    return {
        "path": output_path,
        "attempts": FLUX_MAX_VISION_ATTEMPTS,
        "validated": False,
        "last_verdict": last_verdict,
        "model_used": "flux_ultra" if use_ultra else "flux_pro",
        "flux_meta": last_meta,
    }


# ═══════════════════════════════════════════
#  Clips de video (F53b): Gemini Omni Flash → Kling 4.0
# ═══════════════════════════════════════════

def _fal_queue_poll(status_url: str, response_url: str, timeout: int = CLIP_POLL_TIMEOUT) -> dict[str, Any]:
    """Espera un pedido en la cola de fal y devuelve su respuesta. Un rechazo de contenido (al pedir el resultado:
    HTTP 422 `content_policy_violation`, como el de Gemini en F53a) → ContentRejectedError.
    F60 B: antes `_clip_poll`; la usan los clips, la secuencia de imágenes y la madre de persona (`_flux_poll` no se toca)."""
    start = time.time()
    while time.time() - start < timeout:
        resp = requests.get(status_url, headers=_fal_headers(), timeout=15)
        resp.raise_for_status()
        data = resp.json()
        status = data.get("status", "").upper()
        if status == "COMPLETED":
            res = requests.get(response_url, headers=_fal_headers(), timeout=30)
            if res.status_code >= 400 and _is_content_rejection(res.text):
                raise ContentRejectedError(res.text[:600])
            res.raise_for_status()
            return res.json()
        if status in ("FAILED", "ERROR"):
            err_body = json.dumps(data)
            if _is_content_rejection(err_body):
                raise ContentRejectedError(err_body[:600])
            raise RuntimeError(f"fal.ai tarea falló: {err_body[:300]}")
        time.sleep(5)
    raise TimeoutError(f"fal.ai timeout tras {timeout}s")


def _clip_payload(perfil, foto: Path, prompt: str, duracion_s: float, foto_final: Path | None = None) -> dict[str, Any]:
    """El payload del motor: la foto como data URI con el tipo leído de los bytes (Seedream entrega JPEG con extensión
    .png: F52b), la duración en el rango del perfil y la resolución de config; audio apagado solo si el schema lo deja.
    F57: con `foto_final`, también la foto final en `perfil.campo_imagen_final` (`end_image_url`), mismo data URI."""
    if not perfil.duracion_min <= duracion_s <= perfil.duracion_max:
        raise ValueError(f"{perfil.engine_key}: {duracion_s} s fuera de {perfil.duracion_min}–{perfil.duracion_max}")
    payload: dict[str, Any] = {
        "prompt": prompt,
        perfil.campo_imagen: _path_to_data_uri(foto),
        "duration": str(int(duracion_s)) if perfil.duracion_como_texto else int(duracion_s),
        "resolution": getattr(api, "video_resolution", perfil.resolucion),
    }
    if foto_final is not None:
        payload[perfil.campo_imagen_final] = _path_to_data_uri(foto_final)
    if perfil.campo_audio:
        payload[perfil.campo_audio] = False
    return payload


def _clip_ffprobe(path: Path) -> dict[str, Any]:
    import subprocess  # noqa: PLC0415
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height:format=duration",
                          "-of", "json", str(path)], capture_output=True, text=True)
    d = json.loads(out.stdout or "{}")
    v = next((s for s in d.get("streams", []) if s.get("codec_type") == "video"), {})
    return {"segundos": float((d.get("format") or {}).get("duration") or 0), "ancho": v.get("width"),
            "alto": v.get("height"), "audio": any(s.get("codec_type") == "audio" for s in d.get("streams", []))}


def _quitar_audio(path: Path) -> None:
    """El motor no deja apagar el audio (G, K): la pista se quita con ffmpeg, copiando el video (F52)."""
    import subprocess  # noqa: PLC0415
    tmp = path.with_name(path.stem + "_conaudio" + path.suffix)
    path.replace(tmp)
    r = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(tmp), "-an", "-c:v", "copy",
                        str(path)], capture_output=True, text=True)
    if r.returncode:
        tmp.replace(path)
        raise RuntimeError(f"ffmpeg -an falló: {r.stderr[-300:]}")
    tmp.unlink()


def _call_clip_once(perfil, foto: Path, prompt: str, output_path: Path, duracion_s: float,
                    foto_final: Path | None = None) -> dict[str, Any]:
    """Una llamada al motor por la cola de fal: pide, espera, baja el mp4, le quita el audio si hace falta."""
    submit_url = f"{api.fal_base_url}/{perfil.endpoint}"
    try:
        resp = requests.post(submit_url, headers=_fal_headers(),
                             json=_clip_payload(perfil, foto, prompt, duracion_s, foto_final), timeout=FAL_SUBMIT_TIMEOUT_S)
        resp.raise_for_status()
    except requests.HTTPError as e:
        body = e.response.text if e.response is not None else str(e)
        if _is_content_rejection(body):
            raise ContentRejectedError(body[:600])
        raise
    sub = resp.json()
    data = sub if "video" in sub else _fal_queue_poll(sub["status_url"], sub["response_url"])
    video_url = (data.get("video") or {}).get("url")
    if not video_url:
        raise RuntimeError(f"{perfil.engine_key} sin video: {json.dumps(data)[:300]}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    vid = requests.get(video_url, timeout=300)
    vid.raise_for_status()
    output_path.write_bytes(vid.content)
    if perfil.campo_audio is None:
        _quitar_audio(output_path)
    med = _clip_ffprobe(output_path)
    if not med["segundos"] or not med["ancho"]:
        raise RuntimeError(f"{perfil.engine_key}: el mp4 bajado no tiene video legible ({med})")
    return med


def _ssim(a: Path, b: Path) -> float | None:
    """F57: parecido entre dos fotos con el filtro `ssim` de ffmpeg (`All`), escalando `b` al tamaño de `a` si difiere
    (`scale2ref`). None si ffmpeg falla o no imprime el valor: se informa, no frena."""
    import re  # noqa: PLC0415
    import subprocess  # noqa: PLC0415
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(b), "-i", str(a), "-filter_complex",
                        "[0:v][1:v]scale2ref[b][a];[a][b]ssim", "-f", "null", "-"], capture_output=True, text=True)
    m = re.search(r"All:([\d.]+)", r.stderr or "")
    return float(m.group(1)) if m else None


def foto_final_del_clip(foto_inicial: Path, image_prompt: str, voz_clip: str,
                        out_path: Path, *, use_ultra: bool = False) -> dict[str, Any]:
    """F57 (DECISIONES 2026-10-29 21:10 y 21:17): la foto final del clip, un EDIT de la inicial. Opus escribe la
    instrucción (`video_prompt.escribir_final`: foto, image_prompt, voz del clip; desde F58 A8, DECISIONES 23:10, la
    instrucción de edit no mira el movimiento; F59 chascadas, DECISIONES 2026-10-30 08:22: ya no se recibe) y Seedream la
    aplica por `/edit` con la inicial como referencia (`_generate_image_raw` con `foto_madre_data_uris`, el tipo leído
    de los bytes). Si `out_path` ya existe se reusa (no se paga de nuevo; solo se mide). Devuelve {path | None, ssim |
    None, instruccion, motivo}: un rechazo de contenido o un error del edit deja `path` None con el motivo literal, y
    el clip sale sin foto final. El SSIM inicial/final se mide y se informa; no hay umbral."""
    from script_engine import video_prompt
    if out_path.exists():
        return {"path": out_path, "ssim": _ssim(foto_inicial, out_path), "instruccion": None,
                "motivo": "reusada: ya existía"}
    instruccion = None
    try:
        instruccion = video_prompt.escribir_final(foto_inicial, image_prompt or video_prompt.SIN_DATO, voz_clip,
                                                  description=f"{out_path.stem}: instruccion")
        _generate_image_raw(instruccion, out_path, use_ultra, foto_madre_data_uris=[_path_to_data_uri(foto_inicial)])
    except ContentRejectedError as e:
        error_handler.log_warning(PipelineStage.IMAGE, f"[foto final] {out_path.name}: rechazada — {str(e)[:300]}")
        return {"path": None, "ssim": None, "instruccion": instruccion, "motivo": f"rechazo: {e}"[:600]}
    except Exception as e:  # noqa: BLE001 — el clip sale sin foto final; el motivo se informa tal cual
        error_handler.log_warning(PipelineStage.IMAGE, f"[foto final] {out_path.name}: falló — {str(e)[:300]}")
        return {"path": None, "ssim": None, "instruccion": instruccion,
                "motivo": f"{type(e).__name__}: {e}"[:600]}
    return {"path": out_path, "ssim": _ssim(foto_inicial, out_path), "instruccion": instruccion, "motivo": None}


def _generate_clip(foto: Path, intento_movimiento: str, output_path: Path, *, image_prompt: str = "",
                   ancla: str = "", foto_final: Path | None = None, log: list | None = None) -> Path:
    """F53b: el clip de un cap con clip. Recorre la cadena de motores (`api.video_engines`: Gemini Omni Flash 1.1 →
    Kling 4.0). Por cada motor, Opus escribe el prompt con su ficha mirando la foto (`script_engine.video_prompt`,
    `intento_movimiento` = el `video_prompt` aprobado) y se llama al motor. Si el motor rechaza por contenido, pasa al
    siguiente (no se suaviza el prompt); los errores de red/429/5xx reintentan el mismo motor y no saltan de motor. El
    costo va por `cost_tracker.track_video` con los segundos reales. Cada paso queda en `log` (motor, rechazo literal,
    segundos, costo) si se pasa una lista, y en el log del pipeline.
    F57: `ancla` es la voz entera del clip (`voz_clip`); con `foto_final`, Opus mira las dos fotos (PEDIDO_CON_FINAL) y
    el motor recibe las dos (`end_image_url`): el clip va de una a la otra. Si un motor rechaza, el siguiente recibe las
    mismas dos fotos."""
    from script_engine import video_prompt
    from script_engine.m03_visual import VEO_CLIP_DURATION_SEC
    rechazos: list[str] = []
    for engine_key in api.video_engines:
        perfil = select_video_profile(engine_key)
        prompt = video_prompt.escribir(perfil, foto, image_prompt or video_prompt.SIN_DATO, ancla,
                                       intento_movimiento, foto_final=foto_final,
                                       description=f"{output_path.stem}: prompt {engine_key}")
        for attempt in range(1, CLIP_MAX_ATTEMPTS_NON_REJECTION + 1):
            try:
                med = _call_clip_once(perfil, foto, prompt, output_path, VEO_CLIP_DURATION_SEC, foto_final)
                cost_tracker.track_video(perfil, med["segundos"], med["ancho"], med["alto"],
                                         description=f"{output_path.stem}: {engine_key}")
                fila = {"clip": output_path.name, "motor": engine_key, "rechazos": rechazos, **med,
                        "usd": perfil.costo(med["segundos"], med["ancho"], med["alto"]), "prompt": prompt,
                        "foto_final": foto_final.name if foto_final else None}
                error_handler.log_info(PipelineStage.VIDEO, f"[clip] {output_path.name}: {engine_key} · "
                                                            f"{med['segundos']:.2f} s · US$ {fila['usd']:.4f}"
                                                            + (f" · rechazos previos: {len(rechazos)}" if rechazos else ""))
                if log is not None:
                    log.append(fila)
                return output_path
            except ContentRejectedError as e:
                rechazos.append(f"{engine_key}: {e}")
                error_handler.log_warning(PipelineStage.VIDEO, f"[clip] {output_path.name}: {engine_key} rechazó por "
                                                               f"contenido — {str(e)[:300]}")
                break
            except (requests.HTTPError, requests.Timeout, requests.ConnectionError, RuntimeError, TimeoutError) as e:
                err_str = str(e)
                is_rate_limit = _is_rate_limit(err_str)
                is_transient = is_rate_limit or any(
                    code in err_str for code in ("503", "500", "502", "504", "timeout", "Timeout"))
                if not is_transient or attempt >= CLIP_MAX_ATTEMPTS_NON_REJECTION:
                    error_handler.log_error(PipelineStage.VIDEO, e, attempt=attempt)
                    raise
                wait = RATE_LIMIT_BACKOFF_SECONDS if is_rate_limit else 15 * attempt
                error_handler.log_warning(PipelineStage.VIDEO, f"[clip] {engine_key} intento {attempt} falló "
                                                               f"({err_str[:80]}). Retry en {wait}s...")
                time.sleep(wait)
    if log is not None:
        log.append({"clip": output_path.name, "motor": None, "rechazos": rechazos})
    raise ContentRejectedError(" | ".join(rechazos)[:900])


# ═══════════════════════════════════════════
#  Generación por capítulo — Flux
# ═══════════════════════════════════════════


def _norm_foto_madre_refs(v: Any) -> list[str]:
    """Normaliza foto_madre_ref a lista de hasta 2 refs no vacíos (dedup, orden preservado).
    Acepta: lista (HANDOFF_131, nuevo), string (contrato 129, viejo), o vacío/None → [].
    El techo de 2 lo fuerza acá (Gemini no garantiza maxItems del schema)."""
    if isinstance(v, str):
        v = [v]
    if not isinstance(v, (list, tuple)):
        return []
    out: list[str] = []
    for r in v:
        s = str(r or "").strip()
        if s and s not in out:
            out.append(s)
    return out[:2]


# ═══════════════════════════════════════════
#  F60 B — madres por PERSONA: filtro por era y regla única de madres
# ═══════════════════════════════════════════

def _anio_entero(anio: Any) -> int | None:
    """F60 B: año de una foto = primer número de 4 dígitos de `anio` (image_prompts, image_f8 y supps); sin él → None."""
    m = re.search(r"\d{4}", str(anio or ""))
    return int(m.group(0)) if m else None


def persona_aporta_madre(canon_persona: dict[str, Any] | None, anio: Any) -> bool:
    """F60 B (Omar, DECISIONES 2026-10-30 20:29): la madre es la cara de la persona en su `era`. NO aporta madre a una
    foto si el año cae fuera del tramo de su `era` Y dentro de un tramo de su `condition_by_period` que también está fuera
    de su era (tramo que no se cruza con la era; p. ej. Daniel enfermo en 1991). En cualquier otro caso aporta; `era` o
    `anio` ilegibles → aporta. Los tramos se leen con `m03_visual._tramo` (F50d)."""
    if not isinstance(canon_persona, dict):
        return True
    y = _anio_entero(anio)
    if y is None:
        return True
    from script_engine.m03_visual import _tramo  # noqa: PLC0415 — el lector de tramos del canon
    era = _tramo(canon_persona.get("era"))
    if era is None or era[0] <= y <= era[1]:
        return True
    for c in canon_persona.get("condition_by_period") or []:
        tr = _tramo(c.get("years")) if isinstance(c, dict) else None
        if tr is None:
            continue
        fuera_de_era = tr[1] < era[0] or tr[0] > era[1]
        if fuera_de_era and tr[0] <= y <= tr[1]:
            return False
    return True


def _norm_persona(v: Any) -> list[str]:
    """`persona` del casillero de m03 (F60 A) → lista de nombres no vacíos, en orden; legacy u otro tipo → []."""
    if not isinstance(v, (list, tuple)):
        return []
    return [s.strip() for s in v if isinstance(s, str) and s.strip()]


def _madres_para_item(persona: list[str], foto_madre_refs: list[str], anio: Any,
                      registry: dict[str, str] | None, personas_canon: dict[str, dict] | None) -> list[tuple[str, str]]:
    """F60 B: REGLA ÚNICA de madres para todos los caminos (secuencia, una foto, caps con clip, QA): refs = madres de
    `persona` (en orden, la principal primero; solo las que aportan por era y tienen foto en el registry) + `foto_madre_ref`
    (objeto/lugar), sin repetir, tope 2 (el de `_norm_foto_madre_refs`). Devuelve [(ref, path)] de las que EXISTEN en disco;
    `personas_canon` = {nombre: {era, condition_by_period}} del contrato (m06); sin canon la persona aporta."""
    registry = registry or {}
    personas_canon = personas_canon or {}
    out: list[tuple[str, str]] = []
    candidatos = [p for p in (persona or []) if persona_aporta_madre(personas_canon.get(p), anio)] + list(foto_madre_refs or [])
    for ref in candidatos:
        p = registry.get(ref)
        if p and Path(p).exists() and ref not in [r for r, _ in out]:
            out.append((ref, p))
    return out[:2]


def _iter_image_items(
    chapter: dict[str, Any],
) -> list[dict[str, Any]]:
    """
    Itera image_prompts del cap soportando ambos schemas (FIX #3).

    Acepta:
      - list[str] (legacy)  → cada item hereda art_profile/subject_ref del cap
      - list[dict] (nuevo)  → cada item lee su propio profile/subject; fallback al cap

    Devuelve list[dict] uniforme con claves garantizadas:
      - "idx":          int (1-indexed)
      - "prompt":       str no vacío
      - "art_profile":  str (placeholder backward-compat — desde chat 19 el
                        catálogo art_profiles está desconectado y este campo
                        suele ser "" o lo que el LLM/cap haya dejado).
      - "subject_ref":  str | None
    """
    raw_items = chapter.get("image_prompts") or []
    if not isinstance(raw_items, (list, tuple)):
        raw_items = [raw_items]

    default_profile = chapter.get("art_profile")
    default_subject = chapter.get("subject_ref")

    out: list[dict[str, Any]] = []
    for idx, raw in enumerate(raw_items, start=1):
        if isinstance(raw, dict):
            prompt_text = str(raw.get("prompt", "") or "").strip()
            profile = raw.get("art_profile") or default_profile or ""
            subject = raw.get("subject_ref") if "subject_ref" in raw else default_subject
            foto_madre_refs = _norm_foto_madre_refs(raw.get("foto_madre_ref"))
            persona = _norm_persona(raw.get("persona"))   # F60 A/B: ruteo → regla única de madres
            anio = str(raw.get("anio")).strip() if raw.get("anio") else None   # F60 B: año de la foto (filtro por era)
            cartel = bool(raw["text_in_image"].get("present")) if isinstance(raw.get("text_in_image"), dict) else False
        else:
            prompt_text = str(raw or "").strip()
            profile = default_profile or ""
            subject = default_subject
            foto_madre_refs = []   # legacy list[str] de PROMPTS → sin ancla
            persona = []
            anio = None
            cartel = False

        if not prompt_text:
            continue

        out.append({
            "idx": idx,
            "prompt": prompt_text,
            "art_profile": profile,
            "subject_ref": subject if subject else None,
            "foto_madre_refs": foto_madre_refs,   # HANDOFF_131: 0..2 refs → /edit; [] → t2i
            "persona": persona,                   # F60 A: nombres del canon (ruteo)
            "anio": anio,                         # F60 B: `anio` del ítem (primer número de 4 dígitos = año de la foto)
            "cartel": cartel,                     # F60 B: text_in_image.present (con cartel no entra a secuencia)
            # F8 §1 E: marca de contenido sensible de m03 v3 (None = guion v2, sin marca)
            "sensible": raw.get("sensible") if isinstance(raw, dict) else None,
        })
    return out


# ═══════════════════════════════════════════
#  F60 B/C — pre-paso de SECUENCIA (Seedream /edit, varias fotos por llamada, por la cola de fal)
# ═══════════════════════════════════════════

_PEDIDOS_LOCK = threading.Lock()


def _pedidos_path(video_id: str) -> Path:
    return OUTPUT_DIR / video_id / SECUENCIA_DIR / "pedidos.json"


def _leer_pedidos(video_id: str) -> dict[str, Any]:
    p = _pedidos_path(video_id)
    try:
        return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
    except (OSError, ValueError):
        return {}


def _guardar_pedido(video_id: str, clave: str, ped: dict[str, Any]) -> None:
    with _PEDIDOS_LOCK:
        d = _leer_pedidos(video_id)
        d[clave] = ped
        p = _pedidos_path(video_id)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")


def _clave_lote(prompts: list[str], refs: list[str]) -> str:
    """Clave de un lote en pedidos.json = md5 de (prompts + refs, en orden): si los ítems cambian, la clave cambia."""
    return hashlib.md5(json.dumps([list(prompts), list(refs)], ensure_ascii=False).encode("utf-8")).hexdigest()


def _prompt_secuencia(prompts: list[str]) -> str:
    """El prompt de secuencia de la Etapa 0 (en código, sin LLM): una escena por línea sin la frase de aspecto ni el
    NO_TEXT de cada foto, que van una sola vez al final. «person» en vez de «man» (la madre puede ser de una mujer o de
    un niño; declarado en SALIDA_BC)."""
    from script_engine import m03_imagenes_v3 as v3img  # noqa: PLC0415
    aspecto = select_profile("seedream").aspect_ratio_text
    lineas = []
    for j, p in enumerate(prompts, 1):
        for q in (aspecto, v3img.NO_TEXT):
            if q:
                p = p.replace(" " + q, "").replace(q, "")
        lineas.append(f"Image {j}: {p.strip()}")
    return (f"A series of {len(prompts)} separate photographs of the same person shown in the reference image. "
            f"Each image is a different scene:\n" + "\n".join(lineas) + f"\nEvery image: {aspecto} {v3img.NO_TEXT}")


def _llamar_secuencia(video_id: str, prompts: list[str], refs: list[str], madre_paths: list[str],
                      out_paths: list[Path]) -> list[Path]:
    """F60 B: UNA llamada Seedream /edit en modo secuencia (`max_images` = N, `sequential_image_generation` auto) por la
    cola de fal → baja las imágenes devueltas a `out_paths` (imagen i = escena i) y registra N en el costo (tarifa por
    imagen del perfil, 0,035 US$). request_id/status_url/response_url van a pedidos.json ANTES de esperar; si la clave del
    lote ya tiene request_id se reanuda sin volver a pedir. Devuelve los out_paths escritos (si fal devuelve menos de N, el
    resto va por el camino de una foto)."""
    profile = select_profile("seedream")
    model_id = profile.render.model_id.replace("text-to-image", "edit")
    prompt = _prompt_secuencia(prompts)
    clave = _clave_lote(prompts, refs)
    ped = _leer_pedidos(video_id).get(clave) or {}
    t0 = time.time()
    if ped.get("request_id") and ped.get("status_url") and ped.get("response_url"):
        error_handler.log_info(PipelineStage.IMAGE,
                               f"[secuencia] lote {clave[:8]} reanudado desde request_id {ped['request_id']} (sin re-pedir)")
        data = _fal_queue_poll(ped["status_url"], ped["response_url"])
    else:
        payload = _seedream_edit_payload_for(prompt, [_path_to_data_uri(p) for p in madre_paths])
        payload["max_images"] = len(prompts)
        payload["sequential_image_generation"] = "auto"
        try:
            resp = requests.post(f"{api.fal_base_url}/{model_id}", headers=_fal_headers(), json=payload,
                                 timeout=FAL_SUBMIT_TIMEOUT_S)
            resp.raise_for_status()
        except requests.HTTPError as e:
            body = e.response.text if e.response is not None else str(e)
            if _is_content_rejection(body):
                raise ContentRejectedError(f"seedream secuencia rechazó prompt: {body[:300]}")
            raise
        sub = resp.json()
        ped = {"request_id": sub.get("request_id"), "status_url": sub.get("status_url"),
               "response_url": sub.get("response_url"), "hora_submit": datetime.now().isoformat(timespec="seconds"),
               "n": len(prompts), "refs": list(refs), "fotos": [p.name for p in out_paths]}
        _guardar_pedido(video_id, clave, ped)        # en disco ANTES de esperar
        data = sub if "images" in sub else _fal_queue_poll(sub["status_url"], sub["response_url"])
    imgs = data.get("images") or []
    if not imgs:
        raise RuntimeError(f"seedream secuencia sin imágenes: {json.dumps(data)[:300]}")
    escritos: list[Path] = []
    for im, out in zip(imgs, out_paths):
        r = requests.get(im["url"], timeout=60)
        r.raise_for_status()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(r.content)
        escritos.append(out)
    cost_tracker.track_seedream(description=f"secuencia {clave[:8]} {refs}: {len(escritos)} fotos",
                                images=len(escritos), mode="edit")
    ped.update({"devueltas": len(imgs), "segundos": round(time.time() - t0, 1),
                "hora_vuelta": datetime.now().isoformat(timespec="seconds"), "seed": data.get("seed")})
    _guardar_pedido(video_id, clave, ped)
    return escritos


def _items_para_secuencia(chapters: list[dict[str, Any]], video_id: str) -> list[dict[str, Any]]:
    """Todas las fotos del guion en orden (cap, índice) que pueden entrar a secuencia: image_prompts de caps flux y supps de
    caps con clip (la foto inicial del clip va por una foto). Cada una con persona, refs, anio, cartel, prompt, path y
    clave (cap_id, "img"|"supp", idx)."""
    out: list[dict[str, Any]] = []
    for ch in chapters:
        engine = (ch.get("render_engine") or "").lower()
        cid = ch["id"]
        if engine in ("flux", "leonardo"):
            d = _chapter_dir(video_id, cid, "flux")
            for it in _iter_image_items(ch):
                out.append({"clave": (cid, "img", it["idx"]), "persona": it["persona"], "refs": it["foto_madre_refs"],
                            "anio": it["anio"], "cartel": it["cartel"], "prompt": it["prompt"],
                            "path": d / _image_filename(cid, it["idx"])})
        elif engine == "veo":
            d = _chapter_dir(video_id, cid, "flux")
            for idx, s in enumerate(ch.get("supplemental_image_prompts") or [], start=1):
                if not isinstance(s, dict):
                    continue
                cartel = bool(s["text_in_image"].get("present")) if isinstance(s.get("text_in_image"), dict) else False
                out.append({"clave": (cid, "supp", idx), "persona": _norm_persona(s.get("persona")),
                            "refs": _norm_foto_madre_refs(s.get("foto_madre_ref")), "anio": s.get("anio"), "cartel": cartel,
                            "prompt": str(s.get("prompt") or "").strip(), "path": d / f"{cid}_supp_{idx:02d}.png"})
    return out


def _pre_paso_secuencia(chapters: list[dict[str, Any]], video_id: str, registry: dict[str, str] | None,
                        personas_canon: dict[str, dict] | None) -> dict[tuple, dict[str, Any]]:
    """F60 B/C: corre UNA vez en process_script, antes del bucle de caps. Entran a secuencia los ítems sin archivo en
    disco con UNA sola persona que aporta madre (filtro por era) y la tiene en el registry, sin foto_madre_ref, sin cartel.
    Agrupados por persona en orden de guion, lotes de FOTOS_POR_LLAMADA (cruzan caps); un lote de 1 foto va por el camino
    de una foto. Lotes de distintas personas y de la misma corren a la vez (tope FLUX_MAX_WORKERS). Devuelve
    {(cap_id, "img"|"supp", idx): {status: "ok_secuencia", persona, lote, path, foto_madre_refs}}; lo que la llamada no
    devolvió o falló no figura → camino de una foto con las mismas madres."""
    registry = registry or {}
    personas_canon = personas_canon or {}
    por_persona: dict[str, list[dict]] = {}
    for it in _items_para_secuencia(chapters, video_id):
        if it["path"].exists() or len(it["persona"]) != 1 or it["refs"] or it["cartel"] or not it["prompt"]:
            continue
        p = it["persona"][0]
        if not _madres_para_item([p], [], it["anio"], registry, personas_canon):
            continue
        por_persona.setdefault(p, []).append(it)
    lotes: list[tuple[str, str, list[dict]]] = []
    for p, items in por_persona.items():
        for j in range(0, len(items), FOTOS_POR_LLAMADA):
            lote = items[j:j + FOTOS_POR_LLAMADA]
            if len(lote) >= 2:
                lotes.append((p, f"{p}#{j // FOTOS_POR_LLAMADA + 1}", lote))
    resultados: dict[tuple, dict[str, Any]] = {}
    if not lotes:
        return resultados
    error_handler.log_info(PipelineStage.IMAGE, f"[secuencia] {len(lotes)} lote(s): "
                           + ", ".join(f"{lid} ({len(l)} fotos)" for _, lid, l in lotes))

    def correr(t):
        p, lid, lote = t
        t0 = time.time()
        escritos = _llamar_secuencia(video_id, [it["prompt"] for it in lote], [p], [registry[p]],
                                     [it["path"] for it in lote])
        return escritos, round(time.time() - t0, 1)

    with ThreadPoolExecutor(max_workers=min(len(lotes), FLUX_MAX_WORKERS)) as ex:
        futs = {ex.submit(correr, t): t for t in lotes}
        for fut in as_completed(futs):
            p, lid, lote = futs[fut]
            try:
                escritos, seg = fut.result()
            except Exception as e:  # noqa: BLE001 — el lote entero cae al camino de una foto
                error_handler.log_warning(PipelineStage.IMAGE, f"[secuencia] lote {lid} falló ({type(e).__name__}: "
                                          f"{str(e)[:160]}) → sus {len(lote)} fotos van por el camino de una foto")
                continue
            hechos = set(escritos)
            for it in lote:
                if it["path"] in hechos:
                    resultados[it["clave"]] = {"status": "ok_secuencia", "persona": p, "lote": lid, "path": it["path"],
                                               "foto_madre_refs": [p], "segundos_lote": seg}
            if len(escritos) < len(lote):
                error_handler.log_warning(PipelineStage.IMAGE, f"[secuencia] lote {lid}: {len(escritos)}/{len(lote)} "
                                          f"fotos devueltas; el resto va por el camino de una foto")
    return resultados


def _process_flux_chapter(
    chapter: dict[str, Any], video_id: str,
    registry: dict[str, str] | None = None,
    personas_canon: dict[str, dict] | None = None,
    secuencia: dict[tuple, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """
    Procesa un capítulo Flux generando todas sus imágenes.
    
    v2.3 (FIX #3): cada imagen tiene su propio art_profile y subject_ref,
    leídos por _iter_image_items. El cap solo provee defaults heredables.
    Esto permite que un cap con escenas mixtas (cubierta + interior + abismo)
    use el profile correcto en cada imagen específica.
    F60 B: las madres salen de la regla única (`_madres_para_item`: persona + foto_madre_ref, filtro por era) y los
    ítems que el pre-paso de secuencia ya escribió entran al manifest como `ok_secuencia` (donantes del piso).
    """
    chapter_id: str = chapter["id"]
    use_ultra = _is_hook_chapter(chapter_id)
    
    # FIX #3: items normalizados a list[dict] con profile/subject por imagen
    items = _iter_image_items(chapter)
    
    # Defaults a nivel cap (solo para logging y manifest compat)
    cap_default_profile: str = _extract_art_profile(chapter)
    cap_default_subject: str | None = chapter.get("subject_ref")
    
    ch_dir = _chapter_dir(video_id, chapter_id, "flux")
    
    # Plan: cada item carga su profile, subject, seed propio
    registry = registry or {}
    secuencia = secuencia or {}
    plan: list[dict[str, Any]] = []
    for item in items:
        out_path = ch_dir / _image_filename(chapter_id, item["idx"])
        seed = _seed_for_subject(video_id, item["subject_ref"])
        # HANDOFF_129/131 (Consumo-B): pedido-no-orden. Resolvé cada ref (0..2) contra el
        # registry; quedate SOLO con los que apuntan a una foto madre que EXISTE. Si ≥1
        # resuelve → /edit con esa lista (cutaway = 2). Si 0 → t2i. Nunca crashear por un ref sin foto.
        # F60 B: regla única — madres de `persona` (en orden, filtro por era) + foto_madre_ref, tope 2.
        sec = secuencia.get((chapter_id, "img", item["idx"]))
        madres = _madres_para_item(item.get("persona") or [], item.get("foto_madre_refs") or [], item.get("anio"),
                                   registry, personas_canon)
        needs = not out_path.exists() and sec is None
        plan.append({
            "idx": item["idx"],
            "prompt": item["prompt"],
            "art_profile": item["art_profile"],
            "subject_ref": item["subject_ref"],
            "foto_madre_refs": sec["foto_madre_refs"] if sec else [r for r, _ in madres],   # solo los que anclaron de verdad
            "foto_madre_data_uris": [_path_to_data_uri(p) for _, p in madres] if needs else [],
            "persona": item.get("persona") or [],
            "secuencia": sec,
            "seed": seed,
            "path": out_path,
            "needs": needs,
            "sensible": item.get("sensible"),
        })
    
    to_generate = [p for p in plan if p["needs"]]
    skipped = len(plan) - len(to_generate)
    
    # Estadísticas para logging
    profiles_used = sorted({p["art_profile"] for p in plan})
    profile_label = (
        cap_default_profile if len(profiles_used) == 1
        else f"MIXED({','.join(profiles_used)})"
    )
    model_label = "ULTRA" if use_ultra else "PRO"
    error_handler.log_info(
        PipelineStage.IMAGE,
        f"[{chapter_id}] Flux-{model_label} [{profile_label}]: "
        f"{len(to_generate)} a generar, {skipped} skip",
    )
    
    results_by_idx: dict[int, dict] = {}
    
    # Skips primero (existen en disco) y los que el pre-paso de secuencia ya escribió (F60 B: `ok_secuencia`)
    for p in plan:
        if not p["needs"]:
            results_by_idx[p["idx"]] = {
                "index": p["idx"],
                "prompt": p["prompt"],
                "art_profile": p["art_profile"],
                "subject_ref": p["subject_ref"],
                "foto_madre_refs": p["foto_madre_refs"],
                "persona": p["persona"],
                "seed_used": p["seed"],
                "path": str(p["path"].relative_to(OUTPUT_DIR)),
                "status": "ok_secuencia" if p["secuencia"] else "skipped_exists",
                "validated": None,
                "model_used": "flux_ultra" if use_ultra else "flux_pro",
                **({"lote": p["secuencia"]["lote"], "segundos_lote": p["secuencia"].get("segundos_lote")} if p["secuencia"] else {}),
            }
    
    # Generación paralela
    if to_generate:
        with ThreadPoolExecutor(max_workers=FLUX_MAX_WORKERS) as executor:
            futures = {
                executor.submit(
                    _generate_flux_image_at,
                    p["prompt"],
                    p["art_profile"],
                    p["path"],
                    use_ultra,
                    p["seed"],
                    p["foto_madre_data_uris"],
                ): p
                for p in to_generate
            }
            for fut in as_completed(futures):
                p = futures[fut]
                idx = p["idx"]
                try:
                    meta = fut.result()
                    results_by_idx[idx] = {
                        "index": idx,
                        "prompt": p["prompt"],
                        "art_profile": p["art_profile"],
                        "subject_ref": p["subject_ref"],
                        "foto_madre_refs": p["foto_madre_refs"],
                        "persona": p["persona"],
                        "seed_used": p["seed"],
                        "path": str(p["path"].relative_to(OUTPUT_DIR)),
                        "status": "ok",
                        "validated": meta["validated"],
                        "vision_attempts": meta["attempts"],
                        "vision_reason": meta["last_verdict"].get("reason", ""),
                        "model_used": meta["model_used"],
                        "flux_meta": meta.get("flux_meta", {}),
                    }
                except Exception as e:
                    error_handler.log_error(
                        PipelineStage.IMAGE, e,
                        context={"chapter": chapter_id, "image_idx": idx},
                    )
                    results_by_idx[idx] = {
                        "index": idx,
                        "prompt": p["prompt"],
                        "art_profile": p["art_profile"],
                        "subject_ref": p["subject_ref"],
                        "foto_madre_refs": p["foto_madre_refs"],
                        "seed_used": p["seed"],
                        "path": None,
                        "status": "failed",
                        "error": str(e)[:200],
                        # reject_reason: solo etiqueta para el manifest (auditable). El piso
                        # anti-desync de abajo aplica a TODOS los fallos por igual.
                        "reject_reason": "content" if isinstance(e, ContentRejectedError) else "error",
                        "model_used": "flux_ultra" if use_ultra else "flux_pro",
                    }
    
    for p in plan:                                  # F8 §1 E: `sensible` al manifest (solo si m03 v3 lo marcó)
        if p.get("sensible") is not None and p["idx"] in results_by_idx:
            results_by_idx[p["idx"]]["sensible"] = bool(p["sensible"])

    # ── 2da pasada — PISO anti-desync (HANDOFF_112 · P2/RAÍZ1) ───────────────────
    # Cada item 'failed' deja path:None → fase2b ve menos fotos que narration_anchors
    # y cae a timing UNIFORME → desync silencioso de TODO el cap. Piso: copiar en disco
    # una still VECINA OK del mismo cap al slot caído. Preserva la CUENTA del cap (no la
    # calidad de ESE beat, que se recupera con el one-off de P3). Va DESPUÉS del loop
    # concurrente (las vecinas ya están todas resueltas) y NO re-renderiza (el filtro
    # re-rechazaría el prompt). Cubre rechazo de contenido Y red/timeout por igual.
    path_by_idx = {p["idx"]: p["path"] for p in plan}
    donor_idxs = [i for i, r in results_by_idx.items()
                  if r.get("status") in ("ok", "skipped_exists", "ok_secuencia")]   # F60 B: la secuencia también dona
    failed_idxs = [i for i, r in results_by_idx.items()
                   if r.get("status") == "failed"]
    if failed_idxs and not donor_idxs:
        # Degenerado: TODO el cap falló → no hay still para copiar. Hard-fail explícito
        # (NUNCA dejar path:None → desync). Un cap sin imágenes es inservible igual.
        raise RuntimeError(
            f"[{chapter_id}] las {len(failed_idxs)} imágenes del cap fallaron; no hay "
            f"still OK para el piso anti-desync. Revisar prompts/filtro de contenido."
        )
    for idx in failed_idxs:
        # Vecino OK más cercano: empata por distancia, desempata al ANTERIOR (idx-1).
        donor = min(donor_idxs, key=lambda j: (abs(j - idx), j > idx))
        src = path_by_idx[donor]
        dst = path_by_idx[idx]
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(src.read_bytes())          # copia REAL a disco (no pasa por fal.ai)
        r = results_by_idx[idx]
        r["path"] = str(dst.relative_to(OUTPUT_DIR))
        r["status"] = "neighbor_fallback"
        r["fallback_from"] = donor
        r.setdefault("reject_reason", "error")
        error_handler.log_warning(
            PipelineStage.IMAGE,
            f"[{chapter_id}] img {idx} ({r.get('reject_reason', 'error')}) → piso: "
            f"copiada still vecina img {donor} (cuenta preservada, beat duplicado).",
        )

    ordered = [results_by_idx[i] for i in sorted(results_by_idx.keys())]

    # Manifest del cap: campos default mantienen retrocompatibilidad con
    # consumidores que esperan profile/subject a nivel cap.
    return {
        "id": chapter_id,
        "engine": "flux",
        "art_profile": cap_default_profile,      # default del cap
        "subject_ref": cap_default_subject,      # default del cap
        "profiles_used": profiles_used,          # FIX #3: lista de profiles reales
        "model_used": "flux_ultra" if use_ultra else "flux_pro",
        "images": ordered,
    }

# ═══════════════════════════════════════════
#  Generación por capítulo — Veo (+ fallback universal)
# ═══════════════════════════════════════════

def _ensure_fallback_image(
    raw_img_prompt: str,
    art_profile: str,
    fallback_path: Path,
    base_img_path: Path,
    use_ultra: bool,
) -> Path:
    """Imagen para Ken Burns: reusa la base si existe, si no genera con guardrail."""
    if fallback_path.exists():
        return fallback_path

    if base_img_path.exists():
        fallback_path.parent.mkdir(parents=True, exist_ok=True)
        fallback_path.write_bytes(base_img_path.read_bytes())
        return fallback_path

    _generate_flux_image_at(raw_img_prompt, art_profile, fallback_path, use_ultra)
    return fallback_path


def _generate_supplementals_for_veo_chapter(
    chapter: dict[str, Any],
    video_id: str,
    chapter_id: str,
    use_ultra: bool,
    registry: dict[str, str] | None = None,
    personas_canon: dict[str, dict] | None = None,
    secuencia: dict[tuple, dict[str, Any]] | None = None,
) -> list[dict]:
    """
    Híbrido Veo+Flux chat 29 #175: genera N imágenes Flux supplementals
    para un cap veo. Cada PNG ocupa un anchor de la zona NO-Veo del cap.

    Los PNGs viven en el mismo directorio que los Flux fallback (ch??_flux/)
    con sufijo `_supp_NN` para distinguirlos de los clips Veo y de sus
    imágenes base.

    Devuelve lista de dicts con shape compatible con `images` de cap flux:
        {index, prompt, narration_anchor, path, status, art_profile, [error]}

    Si el cap NO tiene `supplemental_image_prompts` (topic legacy pre-chat29),
    devuelve lista vacía y no toca nada.
    F60 C: las supps que el pre-paso de secuencia ya escribió entran como `ok_secuencia`; las demás llevan las madres
    de la regla única (`persona` + `foto_madre_ref`, filtro por era) al /edit de una foto.
    """
    supplementals = chapter.get("supplemental_image_prompts") or []
    if not supplementals:
        return []

    supp_dir = _chapter_dir(video_id, chapter_id, "flux")  # mismo dir que flux
    art_profile = _extract_art_profile(chapter)
    results: list[dict] = []

    for idx, item in enumerate(supplementals, start=1):
        prompt = (item.get("prompt") or "").strip()
        anchor = (item.get("narration_anchor") or "").strip()
        img_path = supp_dir / f"{chapter_id}_supp_{idx:02d}.png"
        rel_path = str(img_path.relative_to(OUTPUT_DIR))

        sec = (secuencia or {}).get((chapter_id, "supp", idx))
        if sec:
            results.append({
                "index": idx,
                "prompt": prompt,
                "narration_anchor": anchor,
                "path": rel_path,
                "status": "ok_secuencia",
                "art_profile": "",
                "persona": [sec["persona"]],
                "foto_madre_refs": sec["foto_madre_refs"],
                "lote": sec["lote"],
            })
            continue

        if img_path.exists():
            error_handler.log_info(
                PipelineStage.IMAGE,
                f"[{chapter_id}] supp {idx} ya existe — skip",
            )
            results.append({
                "index": idx,
                "prompt": prompt,
                "narration_anchor": anchor,
                "path": rel_path,
                "status": "skipped_exists",
                "art_profile": "",
            })
            continue

        madres = _madres_para_item(_norm_persona(item.get("persona")), _norm_foto_madre_refs(item.get("foto_madre_ref")),
                                   item.get("anio"), registry, personas_canon)
        kw = {"foto_madre_data_uris": [_path_to_data_uri(p) for _, p in madres]} if madres else {}
        try:
            _generate_flux_image_at(prompt, art_profile, img_path, use_ultra, **kw)
            results.append({
                "index": idx,
                "prompt": prompt,
                "narration_anchor": anchor,
                "path": rel_path,
                "status": "ok",
                "art_profile": "",
                "foto_madre_refs": [r for r, _ in madres],
            })
        except Exception as e:
            error_handler.log_error(
                PipelineStage.IMAGE, e,
                context={"chapter": chapter_id, "supp_idx": idx, "stage": "supplemental"},
            )
            results.append({
                "index": idx,
                "prompt": prompt,
                "narration_anchor": anchor,
                "path": None,
                "status": "failed",
                "art_profile": "",
                "error": str(e)[:200],
            })

    return results


def _process_veo_chapter(
    chapter: dict[str, Any], video_id: str,
    registry: dict[str, str] | None = None,
    personas_canon: dict[str, dict] | None = None,
    secuencia: dict[tuple, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """F60 C: la foto inicial del clip lleva las madres de la regla única leídas de `image_f8` (persona/anio de la foto
    del clip, que m06 y el adaptador de fase2a ahora conservan); la foto final hereda la cara por /edit (F57). Las supps
    van al mismo pre-paso de secuencia que los caps flux."""
    chapter_id: str = chapter["id"]
    video_prompts: list[str] = chapter["video_prompts"]
    raw_image_prompts: list[str] = chapter["image_prompts"]
    art_profile: str = _extract_art_profile(chapter)
    use_ultra = _is_hook_chapter(chapter_id)

    if len(video_prompts) != len(raw_image_prompts):
        raise ValueError(
            f"[{chapter_id}] len(video_prompts)={len(video_prompts)} != "
            f"len(image_prompts)={len(raw_image_prompts)}"
        )
    # F57: la voz entera del clip viene de m03 (`voz_clip`); un guion viejo sin la clave PARA (no hay respaldo al ancla)
    voz_clip: str = (chapter.get("voz_clip") or "").strip()
    if not voz_clip:
        raise ValueError(f"[{chapter_id}] cap sin voz_clip: correr m03 de nuevo")

    veo_dir = _chapter_dir(video_id, chapter_id, "veo")
    fallback_dir = _chapter_dir(video_id, chapter_id, "flux")

    f8 = chapter.get("image_f8") if isinstance(chapter.get("image_f8"), dict) else {}
    madres_f8 = _madres_para_item(_norm_persona(f8.get("persona")), _norm_foto_madre_refs(f8.get("foto_madre_ref")),
                                  f8.get("anio"), registry, personas_canon)

    clip_results: list[dict] = []

    for idx, (raw_img_prompt, vid_prompt) in enumerate(
        zip(raw_image_prompts, video_prompts), start=1
    ):
        clip_path = veo_dir / _clip_filename(chapter_id, idx)
        base_img_path = veo_dir / _image_filename(chapter_id, idx)
        fallback_img_path = fallback_dir / _image_filename(chapter_id, idx)

        if clip_path.exists():
            error_handler.log_info(
                PipelineStage.VIDEO,
                f"[{chapter_id}] Clip {idx} ya existe — skip",
            )
            clip_results.append({
                "index": idx, "video_prompt": vid_prompt, "image_prompt": raw_img_prompt,
                "path": str(clip_path.relative_to(OUTPUT_DIR)),
                "status": "skipped_exists", "fallback_type": None,
            })
            continue

        if fallback_img_path.exists() and not clip_path.exists():
            error_handler.log_info(
                PipelineStage.VIDEO,
                f"[{chapter_id}] Clip {idx} ya tiene fallback — skip",
            )
            clip_results.append({
                "index": idx, "video_prompt": vid_prompt, "image_prompt": raw_img_prompt,
                "path": str(fallback_img_path.relative_to(OUTPUT_DIR)),
                "status": "skipped_exists", "fallback_type": "unknown_prior",
            })
            continue

        if not base_img_path.exists():
            error_handler.log_info(
                PipelineStage.IMAGE,
                f"[{chapter_id}] Imagen base clip {idx} [{art_profile}]...",
            )
            kw = ({"foto_madre_data_uris": [_path_to_data_uri(p) for _, p in madres_f8]}
                  if madres_f8 and idx == 1 else {})   # F60 C: image_f8 describe la foto del clip (la primera)
            try:
                _generate_flux_image_at(
                    raw_img_prompt, art_profile, base_img_path, use_ultra, **kw
                )
            except Exception as e:
                error_handler.log_error(
                    PipelineStage.IMAGE, e,
                    context={"chapter": chapter_id, "clip_idx": idx, "stage": "base_image"},
                )
                clip_results.append({
                    "index": idx, "video_prompt": vid_prompt, "image_prompt": raw_img_prompt,
                    "path": None, "status": "failed", "fallback_type": None,
                    "error": f"base_image: {e}"[:200],
                })
                continue

        # F57: la foto final (edit de la inicial) antes del clip; sin ella (rechazo/error) el clip sale solo con la inicial
        final_img_path = veo_dir / f"{base_img_path.stem}_final{base_img_path.suffix}"
        final = foto_final_del_clip(base_img_path, raw_img_prompt, voz_clip, final_img_path,
                                    use_ultra=use_ultra)
        error_handler.log_info(PipelineStage.VIDEO, f"[{chapter_id}] clip {idx}"
                               + (f" (foto final, ssim {final['ssim']})" if final["path"] else " (sin foto final)") + "...")
        try:
            _generate_clip(base_img_path, vid_prompt, clip_path, image_prompt=raw_img_prompt,
                           ancla=voz_clip, foto_final=final["path"])
            clip_results.append({
                "index": idx, "video_prompt": vid_prompt, "image_prompt": raw_img_prompt,
                "path": str(clip_path.relative_to(OUTPUT_DIR)),
                "status": "ok", "fallback_type": None,
                "foto_final": str(final["path"].relative_to(OUTPUT_DIR)) if final["path"] else None,
                "ssim": final["ssim"], "motivo_sin_final": None if final["path"] else final["motivo"],
            })
            continue

        except ContentRejectedError as e:
            error_handler.log_warning(
                PipelineStage.VIDEO,
                f"[{chapter_id}] Clip {idx} RECHAZADO (política) — kenburns_fallback",
            )
            fallback_type = "kenburns_fallback"
            fallback_reason = f"content_rejected: {str(e)[:180]}"

        except (requests.HTTPError, requests.Timeout, requests.ConnectionError,
                RuntimeError, TimeoutError) as e:
            error_handler.log_warning(
                PipelineStage.VIDEO,
                f"[{chapter_id}] Clip {idx} falló técnicamente "
                f"({str(e)[:100]}) — technical_fallback",
            )
            fallback_type = "technical_fallback"
            fallback_reason = f"technical: {str(e)[:180]}"

        except Exception as e:
            error_handler.log_error(
                PipelineStage.VIDEO, e,
                context={"chapter": chapter_id, "clip_idx": idx},
            )
            fallback_type = "technical_fallback"
            fallback_reason = f"unexpected: {str(e)[:180]}"

        try:
            _ensure_fallback_image(
                raw_img_prompt=raw_img_prompt,
                art_profile=art_profile,
                fallback_path=fallback_img_path,
                base_img_path=base_img_path,
                use_ultra=use_ultra,
            )
            clip_results.append({
                "index": idx, "video_prompt": vid_prompt, "image_prompt": raw_img_prompt,
                "path": str(fallback_img_path.relative_to(OUTPUT_DIR)),
                "status": fallback_type, "fallback_type": fallback_type,
                "fallback_reason": fallback_reason,
            })
        except Exception as fallback_err:
            error_handler.log_error(
                PipelineStage.IMAGE, fallback_err,
                context={"chapter": chapter_id, "clip_idx": idx, "stage": "fallback_image"},
            )
            clip_results.append({
                "index": idx, "video_prompt": vid_prompt, "image_prompt": raw_img_prompt,
                "path": None, "status": "failed", "fallback_type": None,
                "error": f"primary: {fallback_reason} | fallback_failed: {fallback_err}"[:300],
            })

    # Chat 29 #175: generar PNGs supplementals para cubrir la zona NO-Veo del cap.
    supplemental_images = _generate_supplementals_for_veo_chapter(
        chapter, video_id, chapter_id, use_ultra, registry, personas_canon, secuencia
    )

    return {
        "id": chapter_id,
        "engine": "veo",
        "art_profile": art_profile,
        "model_used": "flux_ultra" if use_ultra else "flux_pro",
        "clips": clip_results,
        # Chat 29 #175: PNGs Flux para la zona NO-Veo del cap (lista vacía
        # si el cap no es híbrido / topic legacy pre-chat29).
        "supplemental_images": supplemental_images,
        "veo_position": chapter.get("veo_position", "start"),
    }


# ═══════════════════════════════════════════
#  API pública
# ═══════════════════════════════════════════

def _grade_enabled(script: dict[str, Any]) -> bool:
    """F8b §2.6: el grade de post corre en guiones v3 (m03 marca `sensible` en cada imagen) o con IMAGE_GRADE=1;
    IMAGE_GRADE=0 lo apaga. Guiones v2 (sin la marca): como antes, sin archivos nuevos."""
    env = os.environ.get("IMAGE_GRADE")
    if env in ("0", "1"):
        return env == "1"
    for ch in script.get("chapters") or []:
        for it in (ch.get("image_prompts") or []) + (ch.get("supplemental_image_prompts") or []):
            if isinstance(it, dict) and "sensible" in it:
                return True
    return False


def _apply_grade(chapter_results: list[dict]) -> int:
    """F8b §2.6: grade de post (script_engine.image_grade) sobre cada foto del manifest: `<stem>_graded.png` al lado,
    el original se conserva (`path_original`) y `path` pasa al graduado, que es lo que reciben DepthFlow/Ken Burns.
    Devuelve cuántas graduó. Una que falla queda con el original y un aviso."""
    from script_engine import image_grade
    prm = image_grade.params()
    if not prm.get("enabled", True):
        return 0
    n = 0
    for res in chapter_results:
        for img in (res.get("images") or []) + (res.get("supplemental_images") or []):
            rel = img.get("path")
            if not rel or img.get("path_original") or str(rel).endswith(image_grade.SUFFIX + ".png"):
                continue
            src = OUTPUT_DIR / rel
            if not src.exists():
                continue
            try:
                dst = image_grade.grade(src, prm)
            except Exception as e:  # noqa: BLE001
                error_handler.log_warning(PipelineStage.IMAGE, f"grade falló en {src.name}: {e} — queda el original")
                continue
            img["path_original"] = rel
            img["path"] = str(dst.relative_to(OUTPUT_DIR))
            img["graded"] = True
            n += 1
    return n


def _ensure_cost_tracking(video_id: str) -> None:
    active = cost_tracker.current_video
    if active is None:
        cost_tracker.start_video(video_id=video_id)
        return
    if active.video_id != video_id:
        error_handler.log_warning(
            PipelineStage.IMAGE,
            f"cost_tracker tenía '{active.video_id}' — reemplazando por '{video_id}'",
        )
        cost_tracker.start_video(video_id=video_id)


def process_script(
    script: dict[str, Any],
    sync_map_path: Path | None = None,
) -> Path:
    """
    Procesa TODOS los capítulos y emite assets_manifest.json.
    Protocolo v2 + Flux migration.
    """
    video_id: str = script["video_id"]
    chapters: list[dict] = script["chapters"]
    # HANDOFF_129 (Consumo-B): registry {ref → path de foto madre} del contrato sagrado.
    foto_madre_registry: dict[str, str] = script.get("foto_madre_registry", {}) or {}
    # F60 B: {nombre: {era, condition_by_period}} de las personas con madre (m06) → filtro por era de la regla única.
    foto_madre_personas: dict[str, dict] = script.get("foto_madre_personas", {}) or {}

    _ensure_cost_tracking(video_id)

    if sync_map_path is not None:
        sync_map = json.loads(Path(sync_map_path).read_text(encoding="utf-8"))
        sync_ids = {c["id"] for c in sync_map.get("chapters", [])}
        script_ids = {c["id"] for c in chapters}
        missing = script_ids - sync_ids
        if missing:
            error_handler.log_warning(
                PipelineStage.IMAGE,
                f"Capítulos sin entry en sync_map: {missing}",
            )

    error_handler.log_info(
        PipelineStage.IMAGE,
        f"🏭 [{video_id}] Asset Manager (Flux+Veo) — {len(chapters)} capítulos "
        f"| Vision Guardrail ACTIVO "
        f"| Flux Pro={api.fal_image_model} | Ultra={api.fal_image_model_ultra}",
    )

    # F60 B/C: pre-paso de secuencia UNA vez, antes del bucle de caps (los lotes cruzan caps y entran supps de caps con clip)
    secuencia = _pre_paso_secuencia(chapters, video_id, foto_madre_registry, foto_madre_personas)

    chapter_results: list[dict] = []

    for ch in chapters:
        engine = ch.get("render_engine", "").lower()
        chapter_id = ch["id"]

        # ⚠️ Compatibilidad: guiones antiguos con "leonardo" → re-mapeamos a "flux"
        if engine == "leonardo":
            error_handler.log_warning(
                PipelineStage.IMAGE,
                f"[{chapter_id}] render_engine='leonardo' DEPRECATED → usando 'flux'",
            )
            engine = "flux"

        error_handler.log_info(
            PipelineStage.IMAGE, f"──── [{chapter_id}] engine={engine} ────"
        )

        if engine == "veo":
            result = _process_veo_chapter(ch, video_id, foto_madre_registry, foto_madre_personas, secuencia)
        elif engine == "flux":
            result = _process_flux_chapter(ch, video_id, foto_madre_registry, foto_madre_personas, secuencia)
        else:
            error_handler.log_warning(
                PipelineStage.IMAGE,
                f"[{chapter_id}] render_engine desconocido: '{engine}' — skip",
            )
            result = {
                "id": chapter_id, "engine": engine or "unknown",
                "status": "skipped_unknown_engine",
            }

        chapter_results.append(result)

    if _grade_enabled(script):                       # F8b §2.6: grade de post antes de DepthFlow/Ken Burns
        n_graded = _apply_grade(chapter_results)
        error_handler.log_info(PipelineStage.IMAGE, f"[{video_id}] grade de post: {n_graded} imagen(es) → *_graded.png")

    assets_dir = _assets_dir(video_id)
    assets_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = assets_dir / "assets_manifest.json"

    manifest = {
        "video_id": video_id,
        "generated_at": datetime.now().isoformat(),
        "prompt_protocol_version": script.get("prompt_protocol_version", "v2"),
        "image_engine": "fal.ai Flux 1.1 Pro",
        "vision_guardrail": {
            "enabled": ENABLE_VISION_VALIDATOR,
            "model": "gemini-2.5-flash",
            "max_attempts": FLUX_MAX_VISION_ATTEMPTS,
        },
        "flux_config": {
            "standard_model": api.fal_image_model,
            "ultra_model": api.fal_image_model_ultra,
            "ultra_chapter_id": HOOK_CHAPTER_ID,
            "resolution_standard": f"{pipeline.image_width}x{pipeline.image_height}",
            "resolution_ultra_aspect": api.fal_image_aspect_ultra,   # ya neutralizado a "16:9"
            "image_engine": api.image_engine,
            "safety_checker": True,
        },
        "veo_config": {                      # F53b: la clave queda (concepto «cap con clip»); los motores son los de abajo
            "video_engines": list(api.video_engines),
            "video_resolution": getattr(api, "video_resolution", None),
            "poll_timeout_seconds": CLIP_POLL_TIMEOUT,
            "max_attempts": CLIP_MAX_ATTEMPTS_NON_REJECTION,
            "rate_limit_backoff_seconds": RATE_LIMIT_BACKOFF_SECONDS,
        },
        # Deprecated chat 19: catálogo art_profiles desconectado.
        # Campo persistido como [] para compat con consumidores que esperan la key.
        "art_profiles_used": [],
        "total_chapters": len(chapter_results),
        "chapters": chapter_results,
    }
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    total_images = sum(len(c.get("images", [])) for c in chapter_results)
    total_ok_clips = sum(
        1 for c in chapter_results for item in c.get("clips", [])
        if item.get("status") == "ok"
    )
    total_kenburns = sum(
        1 for c in chapter_results for item in c.get("clips", [])
        if item.get("status") == "kenburns_fallback"
    )
    total_technical = sum(
        1 for c in chapter_results for item in c.get("clips", [])
        if item.get("status") == "technical_fallback"
    )
    total_failed = sum(
        1 for c in chapter_results for item in c.get("clips", [])
        if item.get("status") == "failed"
    )

    error_handler.log_success(
        PipelineStage.IMAGE,
        f"✅ [{video_id}] Manifest: {total_images} imgs Flux | "
        f"Veo ok={total_ok_clips} | kenburns={total_kenburns} | "
        f"technical_fallback={total_technical} | failed={total_failed}",
    )
    return manifest_path


# ═══════════════════════════════════════════
#  CLI standalone
# ═══════════════════════════════════════════

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Uso: python asset_manager.py <script.json> [<sync_map.json>]")
        sys.exit(1)

    script_path = Path(sys.argv[1])
    sync_map_arg = Path(sys.argv[2]) if len(sys.argv) > 2 else None

    script = json.loads(script_path.read_text(encoding="utf-8"))
    manifest = process_script(script, sync_map_path=sync_map_arg)
    print(f"\n✅ Manifest generado: {manifest}")
