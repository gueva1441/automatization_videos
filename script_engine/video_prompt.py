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
F57 (Parte A4): foto final opcional del clip — con `foto_final` el pedido es PEDIDO_CON_FINAL (dos imágenes, primer y
último cuadro) y `escribir_final` escribe con PEDIDO_FINAL la instrucción de edit que convierte la foto inicial en la final.
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
from script_engine.m03_visual import MODELO_CASILLEROS, VEO_CLIP_DURATION_SEC

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

# F57 Parte A4: el mismo pedido cuando el clip tiene foto final (primer y último cuadro adjuntos). `{segundos}` sale de
# VEO_CLIP_DURATION_SEC (`:g`); el 8 escrito de PEDIDO se deja así a propósito (byte a byte con el lab).
PEDIDO_CON_FINAL = """You write the motion prompt for an image-to-video model. The first attached image is the first frame and the second attached image is the last frame: the shot goes from one to the other. Follow the model guide below exactly; it decides structure, length and closing lines.
MODEL GUIDE:
{ficha}
FIRST FRAME: the first attached image. Where it differs from the still image prompt (framing, pose, what is visible), describe the motion from the image as it is.
LAST FRAME: the second attached image. Describe the motion that ends exactly on it.
STILL IMAGE PROMPT (what the first frame was asked to show):
{prompt_foto}
NARRATION DURING THE CLIP (Spanish):
{ancla}
APPROVED MOTION (keep its intent, rewrite it for this model):
{video_prompt_vivo}
Clip length: {segundos} seconds, one continuous shot, no cuts, no dialogue, no music, no on-screen text.
Return only the prompt text."""

# F57 Parte A4: la instrucción de edit (modelo de edición de imagen) que convierte la foto inicial en el último cuadro.
PEDIDO_FINAL = """You write an edit instruction for an image-editing model. The attached image is the first frame of a {segundos}-second continuous documentary shot. Write the instruction that turns it into the last frame of that same shot.
The last frame keeps the same place, the same people with the same faces, bodies and clothes, the same light and the same photographic style; it changes only what changes during those seconds, following the narration and the approved motion.
STILL IMAGE PROMPT (what the first frame was asked to show):
{prompt_foto}
NARRATION DURING THE SHOT (Spanish; the last frame shows the moment at its end):
{voz_clip}
APPROVED MOTION (where the camera ends up):
{video_prompt_vivo}
Return only the edit instruction: one paragraph of plain English prose describing the last frame."""

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


def _segundos() -> str:
    """La duración del clip para los pedidos de F57: VEO_CLIP_DURATION_SEC con `:g` (8.0 → «8»)."""
    return f"{VEO_CLIP_DURATION_SEC:g}"


def armar_pedido(perfil: VideoProfile, image_prompt: str, ancla: str | None, video_prompt_aprobado: str | None,
                 foto_final: Any = None) -> str:
    """El texto del pedido: PEDIDO con la ficha del perfil; ancla y movimiento aprobado vacíos → «(none)».
    Con `foto_final` (F57) → PEDIDO_CON_FINAL (dos imágenes adjuntas, duración de VEO_CLIP_DURATION_SEC)."""
    campos = dict(ficha=perfil.ficha, prompt_foto=image_prompt, ancla=ancla or SIN_DATO,
                  video_prompt_vivo=video_prompt_aprobado or SIN_DATO)
    if foto_final is not None:
        return PEDIDO_CON_FINAL.format(segundos=_segundos(), **campos)
    return PEDIDO.format(**campos)


def _bloque_imagen(foto: bytes | Path) -> dict[str, Any]:
    """El bloque `image` base64 de la Messages API para los bytes o la ruta de una foto (tipo por los primeros bytes)."""
    datos = foto if isinstance(foto, (bytes, bytearray)) else Path(foto).read_bytes()
    return {"type": "image", "source": {"type": "base64", "media_type": tipo_imagen(datos),
                                        "data": base64.b64encode(datos).decode("ascii")}}


def _body(contenido: list[dict[str, Any]]) -> dict[str, Any]:
    """El body de la Messages API con `contenido` como único mensaje de usuario: MODELO_CASILLEROS, effort de ESFUERZO."""
    return {"model": MODELO_CASILLEROS, "max_tokens": claude_helpers.MAX_TOKENS,
            "messages": [{"role": "user", "content": contenido}],
            "output_config": {"effort": ESFUERZO[MODELO_CASILLEROS]}}


def armar_body(perfil: VideoProfile, foto: bytes | Path, image_prompt: str, ancla: str | None,
               video_prompt_aprobado: str | None, foto_final: bytes | Path | None = None) -> dict[str, Any]:
    """El body de la Messages API: contenido en lista, la foto primero (bloque `image` base64) y el pedido después.
    Con `foto_final` (F57): foto inicial, foto final y el pedido PEDIDO_CON_FINAL; sin ella, el body de siempre."""
    contenido: list[dict[str, Any]] = [_bloque_imagen(foto)]
    if foto_final is not None:
        contenido.append(_bloque_imagen(foto_final))
    contenido.append({"type": "text", "text": armar_pedido(perfil, image_prompt, ancla, video_prompt_aprobado,
                                                           foto_final=foto_final)})
    return _body(contenido)


def armar_body_final(foto: bytes | Path, image_prompt: str, voz_clip: str | None,
                     video_prompt_aprobado: str | None) -> dict[str, Any]:
    """F57: el body que pide la instrucción de edit de la foto final: la foto inicial y PEDIDO_FINAL (voz del clip y
    movimiento aprobado vacíos → «(none)»); mismo modelo, max_tokens y effort que `armar_body`."""
    texto = PEDIDO_FINAL.format(prompt_foto=image_prompt, voz_clip=voz_clip or SIN_DATO,
                                video_prompt_vivo=video_prompt_aprobado or SIN_DATO, segundos=_segundos())
    return _body([_bloque_imagen(foto), {"type": "text", "text": texto}])


def _llamar(body: dict[str, Any], desc: str, post: Callable[[dict], dict] | None) -> str:
    """Manda `body` por `post` (o `claude_helpers._post`) y devuelve el texto de la respuesta (strip).
    Reintenta red/408/429/5xx/529 y errores de stream de sobrecarga hasta claude_helpers.MAX_ATTEMPTS (backoff 2^n s);
    otro 4xx, `stop_reason: refusal` o respuesta sin texto → claude_helpers.ClaudeError. Cobra por `_track` con `desc`."""
    post = post or claude_helpers._post
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


def escribir(perfil: VideoProfile, foto: bytes | Path, image_prompt: str, ancla: str, video_prompt_aprobado: str | None,
             *, foto_final: bytes | Path | None = None, post: Callable[[dict], dict] | None = None,
             description: str | None = None) -> str:
    """El prompt de video para `perfil` (texto, strip). `foto`: los bytes o la ruta de la foto inicial del clip;
    `foto_final` (F57): los de la foto final, si el clip la tiene (el pedido pasa a PEDIDO_CON_FINAL).
    Reintentos y errores como `_llamar`."""
    body = armar_body(perfil, foto, image_prompt, ancla, video_prompt_aprobado, foto_final=foto_final)
    return _llamar(body, description or f"video_prompt:{perfil.engine_key}", post)


def escribir_final(foto: bytes | Path, image_prompt: str, voz_clip: str | None, video_prompt_aprobado: str | None,
                   *, post: Callable[[dict], dict] | None = None, description: str | None = None) -> str:
    """F57: la instrucción de edit (texto, strip) que convierte la foto inicial del clip en su último cuadro, con
    PEDIDO_FINAL sobre la foto, el `image_prompt`, la voz del clip y el movimiento aprobado. Reintentos y errores como
    `_llamar`; costo con la descripción «video_prompt:final» por defecto."""
    body = armar_body_final(foto, image_prompt, voz_clip, video_prompt_aprobado)
    return _llamar(body, description or "video_prompt:final", post)
