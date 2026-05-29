"""
vision_validator.py — Guardrail de calidad visual (Gemini 2.5 Flash Vision).

Objetivo:
  Antes de enviar una imagen Flux al motor Veo (caro: $0.24/clip), validar
  que la imagen CORRESPONDE al prompt descriptivo (Protocolo v2 + Flux
  Anchoring).

Evalúa:
  1) SUJETO principal presente y reconocible.
  2) ESCALA / COMPOSICIÓN acorde al prompt.
  3) FIDELIDAD HISTÓRICA — si el prompt ancla una década (ej: "1955",
     "1970s"), la imagen no debe contener elementos modernos (LEDs,
     smartphones, pantallas planas, etc.).
  4) AUSENCIA DE TEXTO visible / logos / marcas de agua.

Devuelve un VisionVerdict:
  { match, reason, correction_suggestion, failure_type }

failure_type guía el Intento 2 Agresivo:
  "subject"     → sujeto ausente o irreconocible
  "scale"       → escala/composición incorrecta
  "anachronism" → elementos modernos en escena de época
  "text"        → texto / logo visible
  "other"       → otra razón
  ""            → match=True
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, TypedDict

from google.genai import types as genai_types

from config import gemini_client
from error_handler import error_handler, PipelineStage
from cost_tracker import cost_tracker


VISION_MODEL = "gemini-2.5-flash"

VALID_FAILURE_TYPES = {"subject", "scale", "anachronism", "text", "other", ""}


class VisionVerdict(TypedDict):
    match: bool
    reason: str
    correction_suggestion: str
    failure_type: str


VISION_SYSTEM_PROMPT = """Eres un auditor visual. Evalúas si una imagen generada por IA
corresponde al prompt que la creó. Enfócate SOLO en:

  1) SUJETO principal presente y reconocible.
  2) ESCALA / COMPOSICIÓN acorde (primer plano vs paisaje, proporciones).
  3) FIDELIDAD HISTÓRICA: si el prompt ancla una década específica
     (ej: "In 1955", "1970s", "1950s"), la imagen NO debe mostrar:
       • Pantallas planas / LCD / LED / touchscreens
       • Smartphones, tablets, laptops modernas
       • Tipografía digital moderna
       • Plásticos contemporáneos, USB, cables modernos
       • Arquitectura o mobiliario post-2000 en escenas pre-2000
  4) NO hay texto, marcas de agua, logos ni subtítulos incrustados.

NO evalúes estilo artístico ni paleta (lo garantiza el system_instruction documental de m03).

Responde SIEMPRE con JSON puro, sin markdown ni fences:
{
  "match": true|false,
  "reason": "explicación breve en español (máx 25 palabras)",
  "correction_suggestion": "si match=false, instrucción concreta para re-prompt (máx 20 palabras). Si match=true, ''",
  "failure_type": "subject|scale|anachronism|text|other" (o '' si match=true)
}"""


# Exclusiones agresivas para Intento 2 cuando falla por anacronismo o texto.
_AGGRESSIVE_ANACHRONISM_NEGATIVES = (
    "NO modern elements, NO anachronisms, NO contemporary objects, "
    "NO LED lights, NO flat-panel screens, NO smartphones, NO plastic, "
    "NO digital displays, NO modern cables"
)

_AGGRESSIVE_TEXT_NEGATIVES = (
    "NO visible text, NO watermarks, NO logos, NO subtitles, "
    "NO letters, NO signs, NO written characters"
)


def _extract_json(raw: str) -> dict[str, Any]:
    """Extrae JSON aunque venga envuelto en fences de markdown."""
    raw = raw.strip()
    fence = re.search(r"```(?:json)?\s*(.*?)\s*```", raw, re.DOTALL)
    if fence:
        raw = fence.group(1).strip()
    return json.loads(raw)


def _extract_decade_marker(raw_prompt: str) -> str | None:
    """
    Detecta un marcador de década en el prompt crudo.
    Retorna "1950s", "1970s", etc. o None si la escena es atemporal.
    Patrones reconocidos:
      "In 1955"      → "1950s"
      "1970s"        → "1970s"
      "late 1980s"   → "1980s"
      "1950s style"  → "1950s"
    """
    if not raw_prompt:
        return None

    # "1970s" / "1950s" (década explícita)
    m = re.search(r"\b(1[89]\d0|20[012]0)s\b", raw_prompt, flags=re.IGNORECASE)
    if m:
        return f"{m.group(1)}s"

    # "In 1955" / "In the year 1987" → redondear a década
    m = re.search(r"\b(?:in\s+(?:the\s+year\s+)?)(1[89]\d{2}|20[012]\d)\b",
                  raw_prompt, flags=re.IGNORECASE)
    if m:
        year = int(m.group(1))
        decade = (year // 10) * 10
        return f"{decade}s"

    return None


@error_handler.retry(PipelineStage.IMAGE)
def validate_image(image_path: Path, image_prompt: str) -> VisionVerdict:
    """
    Valida una imagen Flux contra su prompt original (Protocolo v2).

    Fail-open: si la llamada al validador falla tras reintentos, devuelve
    match=True para no bloquear el pipeline.
    """
    try:
        image_bytes = image_path.read_bytes()
    except FileNotFoundError:
        return {
            "match": False,
            "reason": f"Imagen no encontrada: {image_path.name}",
            "correction_suggestion": "",
            "failure_type": "other",
        }

    user_text = (
        f"PROMPT ORIGINAL (descriptivo puro):\n{image_prompt}\n\n"
        f"Evalúa la imagen adjunta según las reglas del sistema."
    )

    contents = [
        genai_types.Part.from_bytes(data=image_bytes, mime_type="image/png"),
        user_text,
    ]

    try:
        response = gemini_client.models.generate_content(
            model=VISION_MODEL,
            contents=contents,
            config=genai_types.GenerateContentConfig(
                system_instruction=VISION_SYSTEM_PROMPT,
                temperature=0.1,
                response_mime_type="application/json",
            ),
        )
    except Exception as e:
        error_handler.log_warning(
            PipelineStage.IMAGE,
            f"Vision validator falló — fail-open para {image_path.name}: {e}"[:200],
        )
        return {
            "match": True,
            "reason": "vision_validator_unavailable",
            "correction_suggestion": "",
            "failure_type": "",
        }

    cost_tracker.track_gemini_vision(
        description=f"validate:{image_path.stem}",
        calls=1,
    )

    raw_text = (response.text or "").strip()
    try:
        data = _extract_json(raw_text)
        failure_type = str(data.get("failure_type", "")).lower().strip()
        if failure_type not in VALID_FAILURE_TYPES:
            failure_type = "other" if not bool(data.get("match", True)) else ""

        verdict: VisionVerdict = {
            "match": bool(data.get("match", True)),
            "reason": str(data.get("reason", ""))[:200],
            "correction_suggestion": str(data.get("correction_suggestion", ""))[:200],
            "failure_type": failure_type,
        }
        return verdict
    except (json.JSONDecodeError, ValueError) as e:
        error_handler.log_warning(
            PipelineStage.IMAGE,
            f"Vision validator respuesta no-JSON — fail-open: {e} | raw={raw_text[:120]}",
        )
        return {
            "match": True,
            "reason": "vision_validator_parse_error",
            "correction_suggestion": "",
            "failure_type": "",
        }


# ═══════════════════════════════════════════
#  Helper para re-stitch con corrección
# ═══════════════════════════════════════════

def build_corrected_prompt(
    original_raw_prompt: str,
    correction_suggestion: str,
    failure_type: str | None = None,
) -> str:
    """
    Arma el prompt del Intento 2 agregando la corrección del validador.

    Si failure_type es "anachronism" → inyecta NATURAL NEGATIVES agresivos
    anti-modernos + "strictly [década] period-accurate" (si se detecta década).
    Si failure_type es "text" → inyecta NATURAL NEGATIVES anti-texto.

    Mantiene el formato Protocolo v2:
      "[original] | CORRECTION: <sugerencia> | [NEGATIVES agresivos si aplica]"
    """
    correction = (correction_suggestion or "").strip()
    ftype = (failure_type or "").lower().strip()

    segments: list[str] = [original_raw_prompt.rstrip(" .|")]

    if correction:
        segments.append(f"CORRECTION: {correction}")

    if ftype == "anachronism":
        decade = _extract_decade_marker(original_raw_prompt)
        period_clause = (
            f", strictly {decade} period-accurate" if decade else ""
        )
        segments.append(f"{_AGGRESSIVE_ANACHRONISM_NEGATIVES}{period_clause}")
    elif ftype == "text":
        segments.append(_AGGRESSIVE_TEXT_NEGATIVES)

    return " | ".join(segments)
