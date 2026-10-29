"""
script_engine/video_prompt.py — F53b (HANDOFF_F53b_motor_de_clips, Parte A punto 3; adenda: el respaldo es Kling 4.0):
el escritor del prompt de video de F52b pasado a producción.

Una llamada a Opus 5.5 (MODELO_CASILLEROS, effort high, como `m03:casilleros`) por clip y por motor: primero la foto real
como bloque `image` (base64, el tipo sale de los primeros bytes, no de la extensión: Seedream devuelve JPEG y producción
lo guarda como .png), después el pedido de F52b tal cual con la ficha de guía del perfil (`VideoProfile.ficha`, en
inglés), el `image_prompt` de la foto, el ancla de narración y el `video_prompt` del `03_visual` como APPROVED MOTION.
Devuelve el texto del prompt. Sale por `claude_helpers._post` (o el `post` inyectado, los tests usan uno falso); el
costo por `claude_helpers._track` → cost_tracker. Reintentos como `claude_helpers.call_json`: red/408/429/5xx/529 y
errores de stream de sobrecarga hasta MAX_ATTEMPTS con backoff; otro 4xx o `stop_reason: refusal` → ClaudeError.
"""
from __future__ import annotations

import base64
import time
import urllib.error
from pathlib import Path
from typing import Any, Callable

import claude_helpers
from engine_profiles import VideoProfile
from script_engine.guion_v4 import ESFUERZO
from script_engine.m03_visual import MODELO_CASILLEROS

# Origen: lab/hyperframes/f52/prompts_video.py `PEDIDO` (F52b; DECISIONES 2026-10-29 13:50), copiado byte a byte.
# Producción no importa desde lab; test_module_f53b_video_prompt.py chequea que siga idéntico.
PEDIDO = """You write the motion prompt for an image-to-video model. The still image is the first frame. Follow the model guide below exactly; it decides structure, length and closing lines.
MODEL GUIDE:
{ficha}
FIRST FRAME: the attached image. Where it differs from the still image prompt (framing, pose, what is visible), describe the motion from the image as it is.
STILL IMAGE PROMPT (what the first frame was asked to show):
{prompt_foto}
NARRATION AT THIS MOMENT:
{ancla}
APPROVED MOTION (keep its intent, rewrite it for this model):
{video_prompt_vivo}
Clip length: 8 seconds, one continuous shot, no cuts, no dialogue, no music, no on-screen text.
Return only the prompt text."""

SIN_DATO = "(none)"                    # ancla o video_prompt ausente, como en F53a (`f53a/moderacion.py`)
_JPEG, _PNG = b"\xff\xd8\xff", b"\x89PNG\r\n\x1a\n"


def tipo_imagen(datos: bytes) -> str:
    """media_type de la foto leído de los primeros bytes (JPEG ff d8 ff, PNG 89 50 4E 47 0D 0A 1A 0A). Otro formato →
    ValueError: la API no recibe una imagen con el tipo equivocado."""
    if datos[:3] == _JPEG:
        return "image/jpeg"
    if datos[:8] == _PNG:
        return "image/png"
    raise ValueError(f"la foto no es JPEG ni PNG (primeros bytes {datos[:8].hex(' ')})")


def armar_pedido(perfil: VideoProfile, image_prompt: str, ancla: str | None, video_prompt_aprobado: str | None) -> str:
    """El texto del pedido: PEDIDO con la ficha del perfil; ancla y movimiento aprobado vacíos → «(none)»."""
    return PEDIDO.format(ficha=perfil.ficha, prompt_foto=image_prompt, ancla=ancla or SIN_DATO,
                         video_prompt_vivo=video_prompt_aprobado or SIN_DATO)


def armar_body(perfil: VideoProfile, foto: bytes | Path, image_prompt: str, ancla: str | None,
               video_prompt_aprobado: str | None) -> dict[str, Any]:
    """El body de la Messages API: contenido en lista, la foto primero (bloque `image` base64) y el pedido después."""
    datos = foto if isinstance(foto, (bytes, bytearray)) else Path(foto).read_bytes()
    contenido = [{"type": "image", "source": {"type": "base64", "media_type": tipo_imagen(datos),
                                              "data": base64.b64encode(datos).decode("ascii")}},
                 {"type": "text", "text": armar_pedido(perfil, image_prompt, ancla, video_prompt_aprobado)}]
    return {"model": MODELO_CASILLEROS, "max_tokens": claude_helpers.MAX_TOKENS,
            "messages": [{"role": "user", "content": contenido}],
            "output_config": {"effort": ESFUERZO[MODELO_CASILLEROS]}}


def escribir(perfil: VideoProfile, foto: bytes | Path, image_prompt: str, ancla: str, video_prompt_aprobado: str | None,
             *, post: Callable[[dict], dict] | None = None, description: str | None = None) -> str:
    """El prompt de video para `perfil` (texto, strip). `foto`: los bytes o la ruta de la foto inicial del clip.
    Reintenta red/408/429/5xx/529 y errores de stream de sobrecarga hasta claude_helpers.MAX_ATTEMPTS (backoff 2^n s);
    otro 4xx, `stop_reason: refusal` o respuesta sin texto → claude_helpers.ClaudeError."""
    post = post or claude_helpers._post
    body = armar_body(perfil, foto, image_prompt, ancla, video_prompt_aprobado)
    desc = description or f"video_prompt:{perfil.engine_key}"
    last = ""
    for attempt in range(1, claude_helpers.MAX_ATTEMPTS + 1):
        try:
            r = post(body)
        except urllib.error.HTTPError as e:
            msg = e.read().decode("utf-8", "replace")[:300]
            if e.code in (408, 429, 529) or e.code >= 500:
                last = f"HTTP {e.code}: {msg}"
                time.sleep(2 ** attempt)
                continue
            raise claude_helpers.ClaudeError(f"{MODELO_CASILLEROS}: {desc}: HTTP {e.code}: {msg}") from None
        except claude_helpers._StreamError as e:          # error a mitad del stream (F25a)
            if e.tipo in ("overloaded_error", "rate_limit_error", "api_error"):
                last = str(e)
                time.sleep(2 ** attempt)
                continue
            raise claude_helpers.ClaudeError(f"{MODELO_CASILLEROS}: {desc}: {e}") from None
        except (urllib.error.URLError, TimeoutError) as e:
            last = type(e).__name__
            time.sleep(2 ** attempt)
            continue
        claude_helpers._track(r.get("model") or MODELO_CASILLEROS, r.get("usage") or {}, desc)
        if r.get("stop_reason") == "refusal":
            raise claude_helpers.ClaudeError(f"{MODELO_CASILLEROS}: {desc}: el modelo se negó ({r.get('stop_details')})")
        txt = "".join(b.get("text") or "" for b in r.get("content") or [] if b.get("type") == "text").strip()
        if not txt:
            raise claude_helpers.ClaudeError(f"{MODELO_CASILLEROS}: {desc}: respuesta sin texto "
                                             f"(stop_reason {r.get('stop_reason')})")
        return txt
    raise claude_helpers.ClaudeError(f"{MODELO_CASILLEROS}: {desc} falló después de "
                                     f"{claude_helpers.MAX_ATTEMPTS} intentos: {last}")
