"""
asset_manager.py — Motor ciego del pipeline (Protocolo v2 + Flux Migration).

CAMBIO MAYOR (Fase 2A Evolución Final):
  Eliminado Leonardo AI como motor de imágenes.
  Nuevo motor: fal.ai Flux 1.1 Pro (estándar) + Flux 1.1 Pro Ultra (ch01).

ARQUITECTURA:
  render_engine del guion ahora es uno de:
    - "veo"  → clips de video con fal.ai Veo 3.1 Lite
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
  - Si Veo falla (contenido o técnico) → Ken Burns con imagen Flux.
  - Manifest distingue: ok | kenburns_fallback | technical_fallback | failed.

SMART SKIP: archivos existentes no re-llaman a la API.
"""
from __future__ import annotations

import base64
import hashlib
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Any

import requests

from config import api, pipeline, OUTPUT_DIR
from error_handler import error_handler, PipelineStage
from cost_tracker import cost_tracker

from script_engine.vision_validator import validate_image, build_corrected_prompt


# ═══════════════════════════════════════════
#  Constantes operativas
# ═══════════════════════════════════════════

FLUX_MAX_WORKERS = 5
FLUX_POLL_TIMEOUT = 180
VEO_POLL_TIMEOUT = 600
VEO_MAX_ATTEMPTS_NON_REJECTION = 3
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


@error_handler.retry(PipelineStage.IMAGE, max_server_retries=2)
def _generate_image_raw(
    prompt: str,
    output_path: Path,
    use_ultra: bool,
    seed: int | None = None,
) -> dict[str, Any]:
    """Llamada cruda al motor de imagen activo (api.image_engine), sin validación de visión.

    - "kling": Kling o3 t2i, SYNC (fal.run, status 200 → images[0].url, SIN poll).
      use_ultra queda inerte (Kling tiene un solo endpoint).
    - "flux":  Flux.2 Pro vía queue.fal.run (path histórico, byte-idéntico salvo
      image_size que ahora sale de pipeline).
    El manejo de 422 (ContentRejectedError) es idéntico en ambos motores.
    """
    if api.image_engine == "kling":
        submit_url = f"{api.fal_sync_base_url}/{api.fal_kling_model}"   # SYNC
        payload = _kling_payload_for(prompt)

        try:
            resp = requests.post(submit_url, headers=_fal_headers(),
                                 json=payload, timeout=240)
            resp.raise_for_status()
        except requests.HTTPError as e:
            body = e.response.text if e.response is not None else str(e)
            if _is_content_rejection(body):
                raise ContentRejectedError(
                    f"Kling rechazó prompt: {body[:300]}"
                )
            raise

        data = resp.json()                       # SYNC: respuesta directa, SIN _flux_poll
        if "images" not in data or not data["images"]:
            raise RuntimeError(f"Kling sin imágenes: {json.dumps(data)[:300]}")

        img = data["images"][0]
        image_url = img["url"]

        output_path.parent.mkdir(parents=True, exist_ok=True)
        img_resp = requests.get(image_url, timeout=60)
        img_resp.raise_for_status()
        output_path.write_bytes(img_resp.content)

        cost_tracker.track_kling(
            description=f"{output_path.stem}: {prompt[:60]}...", images=1
        )

        nsfw_list = data.get("has_nsfw_concepts") or [False]
        return {
            "endpoint": api.fal_kling_model,
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
        last_meta = _generate_image_raw(final_prompt, output_path, use_ultra, seed=seed)
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

        last_meta = _generate_image_raw(final_prompt, output_path, use_ultra, seed=seed)

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
#  Veo
# ═══════════════════════════════════════════

def _veo_poll(status_url: str, response_url: str,
              timeout: int = VEO_POLL_TIMEOUT) -> str:
    start = time.time()
    while time.time() - start < timeout:
        resp = requests.get(status_url, headers=_fal_headers(), timeout=15)
        resp.raise_for_status()
        data = resp.json()
        status = data.get("status", "").upper()

        if status == "COMPLETED":
            res = requests.get(response_url, headers=_fal_headers(), timeout=15)
            res.raise_for_status()
            return res.json()["video"]["url"]

        if status in ("FAILED", "ERROR"):
            err_body = json.dumps(data)
            if _is_content_rejection(err_body):
                raise ContentRejectedError(f"Veo rechazó prompt: {err_body[:300]}")
            raise RuntimeError(f"fal.ai tarea falló: {err_body[:300]}")

        time.sleep(5)
    raise TimeoutError(f"fal.ai timeout tras {timeout}s")


def _call_veo_once(image_path: Path, prompt: str, output_path: Path) -> Path:
    image_b64 = base64.b64encode(image_path.read_bytes()).decode()
    payload = {
        "prompt": prompt,
        "image_url": f"data:image/png;base64,{image_b64}",
        "generate_audio": False,
    }
    submit_url = f"{api.fal_base_url}/{api.fal_video_model}"

    try:
        resp = requests.post(submit_url, headers=_fal_headers(),
                             json=payload, timeout=30)
        resp.raise_for_status()
    except requests.HTTPError as e:
        body = e.response.text if e.response is not None else str(e)
        if _is_content_rejection(body):
            raise ContentRejectedError(f"Veo rechazó prompt en submit: {body[:300]}")
        raise

    result = resp.json()
    if "video" in result:
        video_url = result["video"]["url"]
    else:
        video_url = _veo_poll(result["status_url"], result["response_url"])

    output_path.parent.mkdir(parents=True, exist_ok=True)
    vid_resp = requests.get(video_url, timeout=120)
    vid_resp.raise_for_status()
    output_path.write_bytes(vid_resp.content)
    return output_path


def _generate_veo_clip(image_path: Path, prompt: str, output_path: Path) -> Path:
    """Veo con backoff: 20s para 429, lineal para 5xx/timeout."""
    last_error: Exception | None = None
    for attempt in range(1, VEO_MAX_ATTEMPTS_NON_REJECTION + 1):
        try:
            path = _call_veo_once(image_path, prompt, output_path)
            cost_tracker.track_fal(
                description=f"{output_path.stem}: {prompt[:50]}...",
                clips=1,
            )
            return path
        except ContentRejectedError:
            raise
        except (requests.HTTPError, requests.Timeout, requests.ConnectionError,
                RuntimeError) as e:
            last_error = e
            err_str = str(e)

            is_rate_limit = _is_rate_limit(err_str)
            is_transient = is_rate_limit or any(
                code in err_str for code in ("503", "500", "502", "504", "timeout", "Timeout")
            )

            if not is_transient or attempt >= VEO_MAX_ATTEMPTS_NON_REJECTION:
                error_handler.log_error(PipelineStage.VIDEO, e, attempt=attempt)
                raise

            if is_rate_limit:
                wait = RATE_LIMIT_BACKOFF_SECONDS
                error_handler.log_warning(
                    PipelineStage.VIDEO,
                    f"Veo 429 — backoff {wait}s (intento {attempt})",
                )
            else:
                wait = 15 * attempt
                error_handler.log_warning(
                    PipelineStage.VIDEO,
                    f"Veo intento {attempt} falló ({err_str[:80]}). Retry en {wait}s...",
                )
            time.sleep(wait)

    raise RuntimeError(
        f"Veo falló tras {VEO_MAX_ATTEMPTS_NON_REJECTION} intentos: {last_error}"
    )


# ═══════════════════════════════════════════
#  Generación por capítulo — Flux
# ═══════════════════════════════════════════


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
        else:
            prompt_text = str(raw or "").strip()
            profile = default_profile or ""
            subject = default_subject

        if not prompt_text:
            continue

        out.append({
            "idx": idx,
            "prompt": prompt_text,
            "art_profile": profile,
            "subject_ref": subject if subject else None,
        })
    return out


def _process_flux_chapter(
    chapter: dict[str, Any], video_id: str,
) -> dict[str, Any]:
    """
    Procesa un capítulo Flux generando todas sus imágenes.
    
    v2.3 (FIX #3): cada imagen tiene su propio art_profile y subject_ref,
    leídos por _iter_image_items. El cap solo provee defaults heredables.
    Esto permite que un cap con escenas mixtas (cubierta + interior + abismo)
    use el profile correcto en cada imagen específica.
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
    plan: list[dict[str, Any]] = []
    for item in items:
        out_path = ch_dir / _image_filename(chapter_id, item["idx"])
        seed = _seed_for_subject(video_id, item["subject_ref"])
        plan.append({
            "idx": item["idx"],
            "prompt": item["prompt"],
            "art_profile": item["art_profile"],
            "subject_ref": item["subject_ref"],
            "seed": seed,
            "path": out_path,
            "needs": not out_path.exists(),
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
    
    # Skips primero (existen en disco)
    for p in plan:
        if not p["needs"]:
            results_by_idx[p["idx"]] = {
                "index": p["idx"],
                "prompt": p["prompt"],
                "art_profile": p["art_profile"],
                "subject_ref": p["subject_ref"],
                "seed_used": p["seed"],
                "path": str(p["path"].relative_to(OUTPUT_DIR)),
                "status": "skipped_exists",
                "validated": None,
                "model_used": "flux_ultra" if use_ultra else "flux_pro",
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
                        "seed_used": p["seed"],
                        "path": None,
                        "status": "failed",
                        "error": str(e)[:200],
                        "model_used": "flux_ultra" if use_ultra else "flux_pro",
                    }
    
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

        try:
            _generate_flux_image_at(prompt, art_profile, img_path, use_ultra)
            results.append({
                "index": idx,
                "prompt": prompt,
                "narration_anchor": anchor,
                "path": rel_path,
                "status": "ok",
                "art_profile": "",
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
) -> dict[str, Any]:
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

    veo_dir = _chapter_dir(video_id, chapter_id, "veo")
    fallback_dir = _chapter_dir(video_id, chapter_id, "flux")

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
            try:
                _generate_flux_image_at(
                    raw_img_prompt, art_profile, base_img_path, use_ultra
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

        error_handler.log_info(PipelineStage.VIDEO, f"[{chapter_id}] Veo clip {idx}...")
        try:
            _generate_veo_clip(base_img_path, vid_prompt, clip_path)
            clip_results.append({
                "index": idx, "video_prompt": vid_prompt, "image_prompt": raw_img_prompt,
                "path": str(clip_path.relative_to(OUTPUT_DIR)),
                "status": "ok", "fallback_type": None,
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
        chapter, video_id, chapter_id, use_ultra
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
            result = _process_veo_chapter(ch, video_id)
        elif engine == "flux":
            result = _process_flux_chapter(ch, video_id)
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
        "veo_config": {
            "poll_timeout_seconds": VEO_POLL_TIMEOUT,
            "max_attempts": VEO_MAX_ATTEMPTS_NON_REJECTION,
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
