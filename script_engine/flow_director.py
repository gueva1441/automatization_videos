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

from typing import Any

from error_handler import error_handler, PipelineStage
# HANDOFF_140b (C1/ROOT): el director usa el MISMO helper JSON robusto que todo el repo
# (response_mime_type=json + retry de parse + tracking) en vez de su _call_gemini frágil.
from gemini_helpers import call_flash_json

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

_SYSTEM_PROMPT = f"""Eres director de cinematografía para documentales largos horizontales (16:9, YouTube long).
Decides el movimiento DepthFlow para CADA escena en UNA sola pasada (ves el arco completo del video).
Cada escena es UNA IMAGEN del video; el capítulo al que pertenece va en su label (p.ej. "ch03 (desarrollo)").

INVENTARIO EXACTO — usa SOLO estos 3 nombres, NO inventes otros:
{render_inventory_for_prompt()}

PARÁMETROS POR ESCENA:
- intensity: float 0.6-1.0 (0.6=intenso pero contenido, 1.0=máxima energía).
  NUNCA por debajo de 0.6 — todos los movimientos deben sentirse intensos.
- steady: float 0.0-0.8. Usa >0.4 cuando hay sujeto humano frontal definido (lo mantiene como ancla).
- dof: bool. True para escenas con sujeto humano definido (depth-of-field bokeh). False para paisajes/multitudes/texturas.

REGLAS DURAS:
- VARIÁ los movimientos. NO repitas el mismo más de 2 veces seguidas.
- ARCO NARRATIVO (por capítulo, según el label): las imágenes del PRIMER capítulo (hook) preferí orbital para enganchar con dramatismo. Las de los capítulos del medio mezclá los 3. Las del ÚLTIMO capítulo (outro/reveal) preferí horizontal u orbital para cerrar suave. Dentro de un mismo capítulo, VARIÁ imagen a imagen.

CRITERIO SEMÁNTICO (DEFAULT vertical en 16:9 — el eje corto del cuadro da más moción aparente; horizontal solo como excepción):
- Rostro frontal, retrato, sujeto humano definido → orbital (enfatiza volumen) o vertical suave.
- Objetos centrales, detalles que querés enfatizar → orbital.
- Sujeto vertical dominante (torre/chimenea/árbol/figura que llena el alto del cuadro) → vertical.
- Paisaje ambiguo, interiores anchos, multitudes, texturas y superficies sin sujeto claro → vertical (el default residual).
- Paisaje GENUINAMENTE apaisado y dominante (horizonte/costa/skyline que llena el ANCHO, panorámica lateral) → horizontal, solo si el vertical chocaría la composición.

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
    - última (outro) → horizontal (cierre suave, baja energía — único hogar de horizontal)
    - resto → vertical (par) u orbital (impar) — B-QA-3: vertical-default, horizontal sale del medio
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
        # B-QA-3: vertical-default en 16:9 (eje corto = +moción). Horizontal sale del medio → solo outro.
        movement = "vertical" if n % 2 == 0 else "orbital"
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
#  CONTROL ANTI-RACHA (HANDOFF_140b C5 — post-output, duro)
# ═══════════════════════════════════════════════════════════════

# Orden fijo del inventario base → reemplazo determinístico (frozenset no garantiza
# orden de iteración; sorted lo fija). NO incluye zoom_in/zoom_out: el zoom lo inyecta
# el gate depth+visión DESPUÉS (FLAG-A), este control solo baraja el inventario base.
_STREAK_INVENTORY: tuple[str, ...] = tuple(sorted(VALID_MOVEMENTS))


def _break_movement_streaks(specs: list[FlowSpec], max_run: int = 2) -> list[FlowSpec]:
    """Rompe rachas de >max_run movimientos iguales seguidos. Determinístico.

    El system prompt PIDE la regla ("no repitas más de 2 seguidas") pero es blanda y
    Gemini la incumple; este control la GARANTIZA. Solo toca `movement` (deja
    intensity/steady/dof intactos). No introduce zoom (no está en el inventario base).
    Corre sobre TODA la secuencia ordenada por-imagen (ve rachas cruzando capítulos).
    """
    run = 1
    for i in range(1, len(specs)):
        if specs[i]["movement"] == specs[i - 1]["movement"]:
            run += 1
        else:
            run = 1
        if run > max_run:
            streak_mov = specs[i]["movement"]
            nxt = specs[i + 1]["movement"] if i + 1 < len(specs) else None
            for cand in _STREAK_INVENTORY:      # orden fijo → determinístico
                if cand != streak_mov and cand != nxt:
                    specs[i] = {
                        **specs[i],
                        "movement": cand,
                        "reasoning": f"anti-racha: rompe seguidilla de {streak_mov}",
                    }
                    break
            run = 1
    return specs


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

    # HANDOFF_140b (C1): call_flash_json (response_mime_type=json + retry de parse + retry
    # de servidor + tracking de costo). Antes _call_gemini frágil (sin JSON mode) fallaba SIEMPRE
    # → fallback estático en los 7 caps. Una sola red de except; _validate_and_repair es la 2ª red.
    user_prompt = _build_user_prompt(scenes)
    try:
        data = call_flash_json(
            user_prompt,
            system_instruction=_SYSTEM_PROMPT,
            description=f"flow_director batch ({total} escenas)",
        )
        gemini_scenes = data.get("scenes", [])
        if not isinstance(gemini_scenes, list) or len(gemini_scenes) != total:
            raise ValueError(f"Gemini devolvió {len(gemini_scenes)}, esperaba {total}")
    except Exception as e:  # noqa: BLE001 — cualquier fallo (red/JSON/forma) → fallback completo
        error_handler.log_warning(
            PipelineStage.ASSEMBLY,
            f"[flow_director] Gemini/JSON falló ({e}) → fallback estático completo",
        )
        return [_fallback_spec(p, total) for p in positions]

    # Validar/reparar cada uno (1ª red: valores inválidos)
    result = [
        _validate_and_repair(g, p, total)
        for g, p in zip(gemini_scenes, positions)
    ]

    # HANDOFF_140b (C5): 2ª red post-output sobre la secuencia ordenada — garantiza
    # que no queden rachas de 3+ movimientos iguales seguidos (regla que el prompt
    # pide pero Gemini incumple). Determinístico; solo toca movement.
    result = _break_movement_streaks(result)

    error_handler.log_success(
        PipelineStage.ASSEMBLY,
        "[flow_director] " + ", ".join(
            f"{p}={s['movement']}" for p, s in zip(positions, result)
        ),
    )
    return result
