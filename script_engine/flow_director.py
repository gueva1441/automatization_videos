"""
flow_director.py — Director de cinematografía (Gemini batch).

Recibe las N escenas de un script y devuelve los N movimientos DepthFlow
en UNA sola llamada a Gemini Flash (más barato + permite ver el arco
narrativo completo).

Refactor chat 19: ya no recibe art_profile. Decide solo desde scene
content + posición narrativa, guiado por system_instruction documental.

Defensas anti-alucinación (orden):
  1. System prompt con inventario inmutable (3 movimientos) + reglas semánticas
  2. Validación post-output: movement ∈ inventario
  3. Clamping de intensity/steady a rangos válidos
  4. Fallback genérico por posición narrativa si JSON parse falla
  5. Fallback total si Gemini cae completamente
"""
from __future__ import annotations

import json
import re
from typing import Any

from google.genai import types

from config import api, gemini_client
from cost_tracker import cost_tracker
from error_handler import error_handler, PipelineStage

from flow_config import (
    VALID_MOVEMENTS,
    clamp_intensity,
    clamp_steady,
    render_inventory_for_prompt,
)
from flow_profiles import FlowSpec


# ═══════════════════════════════════════════════════════════════
#  PROMPT TEMPLATES
# ═══════════════════════════════════════════════════════════════

_SYSTEM_PROMPT = f"""Eres director de cinematografía para shorts virales documentales verticales (9:16).
Decides el movimiento DepthFlow para CADA escena en UNA sola pasada (ves el arco completo del video).

INVENTARIO EXACTO — usa SOLO estos 3 nombres, NO inventes otros:
{render_inventory_for_prompt()}

PARÁMETROS POR ESCENA:
- intensity: float 0.6-1.0 (0.6=intenso pero contenido, 1.0=máxima energía).
  NUNCA por debajo de 0.6 — todos los movimientos deben sentirse intensos.
- steady: float 0.0-0.8. Usa >0.4 cuando hay sujeto humano frontal definido (lo mantiene como ancla).
- dof: bool. True para escenas con sujeto humano definido (depth-of-field bokeh). False para paisajes/multitudes/texturas.

REGLAS DURAS:
- VARIÁ los movimientos. NO repitas el mismo más de 2 veces seguidas.
- ARCO NARRATIVO: la primera escena (hook) preferí orbital o vertical para enganchar con dramatismo. Las del medio mezclá los 3. La última (outro/reveal) preferí horizontal u orbital para cerrar suave.

CRITERIO SEMÁNTICO (qué movimiento para qué contenido):
- Rostro frontal, retrato, sujeto humano definido → vertical (recorre de pelo a mentón) u orbital (enfatiza volumen).
- Paisaje amplio, horizonte, líneas de costa/edificios/gente, escena extendida lateralmente → horizontal.
- Sujetos verticales (chimeneas, edificios altos, árboles, columnas) → vertical.
- Objetos centrales, productos, detalles que querés enfatizar → orbital.
- Multitudes, panorámicas amplias → horizontal.
- Texturas y superficies sin sujeto claro → horizontal o vertical (cualquiera funciona).

FORMATO OUTPUT — JSON estricto, SIN markdown, SIN ```json fences:
{{
  "scenes": [
    {{"scene_number": 1, "movement": "<inventario>", "intensity": <float 0.6-1.0>,
      "steady": <float 0.0-0.8>, "dof": <bool>, "reasoning": "<máx 15 palabras>"}},
    ... (una entrada por cada escena recibida, en el mismo orden)
  ]
}}
"""


def _build_user_prompt(scenes: list[dict]) -> str:
    """Construye el user prompt con las escenas (sin profile)."""
    lines: list[str] = ["ESCENAS:"]
    for sc in scenes:
        n = sc.get("scene_number", "?")
        label = sc.get("label", "?")
        narration = (sc.get("narration") or "").strip()
        image_prompt = (sc.get("image_prompt") or "").strip()
        lines.append(
            f"- Escena {n} ({label}):\n"
            f"  Narración: {narration}\n"
            f"  Imagen: {image_prompt}"
        )
    lines.append("")
    lines.append("Devolvé JSON con UN movimiento por escena en el mismo orden.")
    return "\n".join(lines)


def _fallback_spec(scene_position: str, total_scenes: int) -> FlowSpec:
    """
    Fallback genérico cuando Gemini falla o devuelve algo inválido.
    Sin profile — decide solo por posición narrativa.

    Inventario reducido en chat 21 a 3 movimientos universalmente robustos:
    - ch01 (hook) → orbital (dramático, enfatiza volumen)
    - última (outro) → horizontal (cierre suave)
    - resto → vertical o horizontal (alterna por paridad para variar)
    """
    try:
        n = int(scene_position.replace("ch", ""))
    except (ValueError, AttributeError):
        n = 0

    if n == 1:
        movement = "orbital"
        reasoning = "fallback hook"
    elif n == total_scenes:
        movement = "horizontal"
        reasoning = "fallback outro"
    else:
        # Alterna vertical/horizontal por paridad para no repetir el mismo
        movement = "vertical" if n % 2 == 0 else "horizontal"
        reasoning = "fallback genérico"

    return FlowSpec(
        movement=movement,
        intensity=0.95,        # subido de 0.7 (chat 21: replica v12 validado)
        steady=0.3,            # bajado de 0.5 (chat 21: replica v12 validado)
        dof=True,
        reasoning=reasoning,
    )


# ═══════════════════════════════════════════════════════════════
#  PARSER + VALIDACIÓN
# ═══════════════════════════════════════════════════════════════

_JSON_FENCE = re.compile(r"^```(?:json)?\s*|\s*```$", re.MULTILINE)


def _extract_json(raw: str) -> dict[str, Any]:
    """Limpia fences markdown y parsea. Lanza si no es JSON válido."""
    cleaned = _JSON_FENCE.sub("", raw).strip()
    return json.loads(cleaned)


def _validate_and_repair(
    spec: dict[str, Any],
    scene_position: str,
    total_scenes: int,
) -> FlowSpec:
    """
    Valida un spec individual contra el inventario reducido (4 movimientos).
    Si algo está mal → reemplaza por valor fallback (no aborta).
    """
    fallback = _fallback_spec(scene_position, total_scenes)

    # 1. Movement: debe existir en VALID_MOVEMENTS (las 4 reducidas en C1)
    movement = spec.get("movement", "")
    if movement not in VALID_MOVEMENTS:
        error_handler.log_warning(
            PipelineStage.ASSEMBLY,
            f"[flow_director] movement inválido='{movement}' → fallback {fallback['movement']}",
        )
        movement = fallback["movement"]

    # 2. Clamp numéricos (intensity_min=0.6 ya está en flow_config)
    try:
        intensity = clamp_intensity(spec.get("intensity", fallback["intensity"]))
    except (TypeError, ValueError):
        intensity = fallback["intensity"]

    try:
        steady = clamp_steady(spec.get("steady", fallback["steady"]))
    except (TypeError, ValueError):
        steady = fallback["steady"]

    # 3. DOF: forzar bool
    dof = bool(spec.get("dof", fallback["dof"]))

    # 4. Reasoning truncado
    reasoning = str(spec.get("reasoning", "")).strip()[:120] or "sin razón"

    return FlowSpec(
        movement=movement, intensity=intensity, steady=steady,
        dof=dof, reasoning=reasoning,
    )


# ═══════════════════════════════════════════════════════════════
#  GEMINI CALL (con retry automático)
# ═══════════════════════════════════════════════════════════════

@error_handler.retry(PipelineStage.ASSEMBLY, max_retries=2, max_server_retries=3)
def _call_gemini(system: str, user: str) -> str:
    """Llamada a Gemini Flash. Retry automático en 503/429."""
    response = gemini_client.models.generate_content(
        model=api.gemini_model,
        contents=user,
        config=types.GenerateContentConfig(
            system_instruction=system,
            temperature=0.6,  # algo de variedad pero no caos
        ),
    )
    return response.text or ""


# ═══════════════════════════════════════════════════════════════
#  ENTRY POINT PÚBLICO
# ═══════════════════════════════════════════════════════════════

def select_movements_batch(scenes: list[dict]) -> list[FlowSpec]:
    """
    Punto de entrada principal. Recibe las escenas del script.
    Devuelve lista de FlowSpec en el mismo orden (siempre len(scenes) elementos).

    Si Gemini falla totalmente → devuelve specs estáticas por posición narrativa
    (NO aborta el pipeline; DepthFlow puede correr con defaults razonables).
    """
    if not scenes:
        return []

    error_handler.log_info(
        PipelineStage.ASSEMBLY,
        f"[flow_director] Eligiendo movimientos para {len(scenes)} escenas",
    )

    total = len(scenes)
    positions = [f"ch{i+1:02d}" for i in range(total)]

    # Llamada a Gemini
    user_prompt = _build_user_prompt(scenes)
    try:
        raw = _call_gemini(_SYSTEM_PROMPT, user_prompt)
        cost_tracker.track_gemini(
            description=f"flow_director batch ({total} escenas)",
            calls=1,
        )
    except Exception as e:
        error_handler.log_warning(
            PipelineStage.ASSEMBLY,
            f"[flow_director] Gemini falló ({e}) → fallback estático completo",
        )
        return [_fallback_spec(p, total) for p in positions]

    # Parse + validación de la respuesta
    try:
        data = _extract_json(raw)
        gemini_scenes = data.get("scenes", [])
        if not isinstance(gemini_scenes, list) or len(gemini_scenes) != total:
            raise ValueError(
                f"Gemini devolvió {len(gemini_scenes)} escenas, esperaba {total}"
            )
    except (json.JSONDecodeError, ValueError) as e:
        error_handler.log_warning(
            PipelineStage.ASSEMBLY,
            f"[flow_director] JSON inválido ({e}) → fallback estático completo",
        )
        return [_fallback_spec(p, total) for p in positions]

    # Validar/reparar cada uno
    result = [
        _validate_and_repair(g, p, total)
        for g, p in zip(gemini_scenes, positions)
    ]

    error_handler.log_success(
        PipelineStage.ASSEMBLY,
        "[flow_director] " + ", ".join(
            f"{p}={s['movement']}" for p, s in zip(positions, result)
        ),
    )
    return result
