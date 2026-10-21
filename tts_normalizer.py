"""
tts_normalizer.py — Normalizador minimal para TTS de ElevenLabs.

POST PR 2.0.X chat 24: reducción drástica.
ElevenLabs maneja por defecto cardinales, decimales, monedas, fechas, ordinales,
horas HH:MM, etc. Confiamos en su normalización automática.

Este módulo aplica SOLO el custom_dict.json (siglas/abrevs/unidades acumuladas
entre videos vía gate humano) y colapsa espacios. Nada más.

Para LONG: el grueso de la normalización lo hace m02_5_normalizer_gate vía LLM
auditor + CLI humano + persistencia en 01b_narration_normalized.json. Ese
archivo es lo que audio_manager lee directo. tts_normalizer queda como
fallback minimal.

Para SHORT: este módulo sigue siendo el camino principal (no hay gate en SHORT).
"""
from __future__ import annotations

import json
import re

from config import DATA_DIR
from error_handler import error_handler, PipelineStage


# ═══════════════════════════════════════════════════════════════
#  DICCIONARIOS BASE (extensibles vía custom_dict.json)
# ═══════════════════════════════════════════════════════════════

# Siglas que SE PRONUNCIAN como palabra (ElevenLabs las lee bien tal cual).
ACRONYMS_PRONOUNCEABLE: set[str] = {
    "NASA", "OVNI", "ONU", "OEA", "OTAN", "FIFA", "ONG", "OPEP", "FEMA",   # F5 §1.4: FEMA se dice «fema»
    "UE", "PIB", "ADN", "ARN", "PYME", "SIDA", "RADAR", "LASER",
    "SONAR", "MODEM", "WIFI", "ASCII", "JPEG", "PDF", "GIF", "MAYDAY",
}

# Siglas que SE DELETREAN (custom_dict puede agregar más).
ACRONYMS_SPELLED: dict[str, str] = {
    "FBI": "efe be i",
    "CIA": "ce i a",
    "KGB": "ka ge be",
    "GPS": "ge pe ese",
    "USB": "u ese be",
    "URSS": "u erre ese ese",
    "SOS": "ese o ese",
    # F5 §1.4: siglas del research de documentales judiciales (deletreo o nombre)
    "ACLU": "a ce ele u",
    "HRW": "Human Rights Watch",
    "DOJ": "Departamento de Justicia",
    "EE.UU.": "Estados Unidos",
    "EE. UU.": "Estados Unidos",
    "EEUU": "Estados Unidos",
}

# Abreviaturas comunes con punto.
ABBREVIATIONS_ES: dict[str, str] = {
    "Sr.":   "señor",
    "Sra.":  "señora",
    "Srta.": "señorita",
    "Dr.":   "doctor",
    "Dra.":  "doctora",
    "etc.":  "etcétera",
    "vs.":   "versus",
    "aprox.": "aproximadamente",
}

# Unidades técnicas (custom_dict puede agregar más).
UNITS_MAP: dict[str, str] = {
    "kHz": "kilohertz",
    "MHz": "megahertz",
    "GHz": "gigahertz",
    "km/h": "kilómetros por hora",
}


# ═══════════════════════════════════════════════════════════════
#  REEMPLAZO POR DICCIONARIO
# ═══════════════════════════════════════════════════════════════

def _replace_from_dict(text: str, mapping: dict[str, str]) -> str:
    """Reemplaza claves del dict por sus valores. Procesa de mayor a menor longitud."""
    sorted_keys = sorted(mapping.keys(), key=len, reverse=True)
    for key in sorted_keys:
        if key in text:
            text = text.replace(key, f" {mapping[key]} ")
    return text


def _replace_acronyms(text: str) -> str:
    """Aplica deletreo a siglas conocidas con word boundary."""
    sorted_keys = sorted(ACRONYMS_SPELLED.keys(), key=len, reverse=True)
    for key in sorted_keys:
        pattern = r"(?<![A-Za-zÁÉÍÓÚÑáéíóúñ])" + re.escape(key) + r"(?![A-Za-zÁÉÍÓÚÑáéíóúñ])"
        text = re.sub(pattern, ACRONYMS_SPELLED[key], text)
    return text


_RE_MULTIPLE_SPACES = re.compile(r"[ \t]{2,}")
_RE_SPACE_BEFORE_PUNCT = re.compile(r"\s+([,.;:!?])")


def _collapse_spaces(text: str) -> str:
    text = _RE_MULTIPLE_SPACES.sub(" ", text)
    text = _RE_SPACE_BEFORE_PUNCT.sub(r"\1", text)
    return text.strip()


# ═══════════════════════════════════════════════════════════════
#  F5 §1.4: formas del evidence_pool que ElevenLabs-ES lee mal (deterministas)
# ═══════════════════════════════════════════════════════════════

_RE_HOUR_AMPM = re.compile(r"\b(\d{1,2}):(\d{2})\s*([AaPp]\.?\s?[Mm]\.?)(?![A-Za-z])")
_RE_MONEY_MILL = re.compile(r"(?:US)?\$\s?(\d[\d.,]*)\s+(millones|mil millones|millón)\b")
_RE_MONEY = re.compile(r"(?:US)?\$\s?(\d{1,3}(?:[.,]\d{3})+|\d+)(?![\d.,]*\s+(?:millones|millón|mil millones))")
_RE_PCT = re.compile(r"\b(\d{1,3}(?:[.,]\d+)?)\s?%")
_RE_QUOTES = re.compile(r"[\"“”«»]")


def _num_text(tok: str, fem: bool = False) -> str:
    from script_engine.num_es import parse_int, words
    n = parse_int(tok)
    if n is not None:
        return words(n, fem=fem)
    m = re.fullmatch(r"(\d+)[.,](\d+)", tok)                       # 98.7 → «noventa y ocho coma siete»
    if m:
        return f"{words(int(m.group(1)))} coma {' '.join(words(int(d)) for d in m.group(2))}"
    return tok


def normalize_pool_forms(text: str) -> str:
    """Horas con AM/PM, dólares, porcentajes y comillas de citas → forma hablada (F5 §1.4).
    «6:10 AM» → «seis y diez de la mañana»; «$223 millones» → «doscientos veintitrés millones de dólares»;
    «$650,000» → «seiscientos cincuenta mil dólares»; «98.7%» → «noventa y ocho coma siete por ciento»;
    las comillas de una cita se sacan (el TTS no las lee y la cita queda dicha)."""
    from script_engine.num_es import hour_words
    if not text:
        return text
    out = _RE_HOUR_AMPM.sub(lambda m: hour_words(int(m.group(1)), int(m.group(2)),
                                                 re.sub(r"[^AaPpMm]", "", m.group(3))), text)
    out = _RE_MONEY_MILL.sub(lambda m: f"{_num_text(m.group(1))} {m.group(2)} de dólares", out)
    out = _RE_MONEY.sub(lambda m: f"{_num_text(m.group(1))} dólares", out)
    out = _RE_PCT.sub(lambda m: f"{_num_text(m.group(1))} por ciento", out)
    out = _RE_QUOTES.sub("", out)
    return _collapse_spaces(out)


# ═══════════════════════════════════════════════════════════════
#  API PÚBLICA
# ═══════════════════════════════════════════════════════════════

def normalize_for_tts(text: str, language: str = "es") -> str:
    """Normalización minimal para SHORT y fallback en LONG.

    Aplica solo: abreviaturas + unidades + siglas spelled + collapse spaces.
    Para LONG, el grueso lo hace el gate LLM y el resultado vive en
    01b_narration_normalized.json.
    """
    if not text or not text.strip():
        return text

    if language != "es":
        error_handler.log_warning(
            PipelineStage.AUDIO,
            f"tts_normalizer: idioma '{language}' no soportado, devolviendo sin cambios",
        )
        return text

    out = text
    out = _replace_from_dict(out, ABBREVIATIONS_ES)
    out = _replace_from_dict(out, UNITS_MAP)
    out = _replace_acronyms(out)
    out = _collapse_spaces(out)
    return out


# ═══════════════════════════════════════════════════════════════
#  CUSTOM DICT LOADER (PR 2.0 chat 23)
# ═══════════════════════════════════════════════════════════════

CUSTOM_DICT_PATH = DATA_DIR / "normalizer_custom_dict.json"


def _load_custom_dict() -> int:
    """Carga normalizer_custom_dict.json y mergea entries en los dicts globales.

    Mapeo categoría → dict destino:
      "spelled"       → ACRONYMS_SPELLED[token] = pronunciation
      "pronounceable" → ACRONYMS_PRONOUNCEABLE.add(token)
      "abbreviation"  → ABBREVIATIONS_ES[token] = pronunciation
      "unit"          → UNITS_MAP[token] = pronunciation
    """
    if not CUSTOM_DICT_PATH.exists():
        return 0
    try:
        data = json.loads(CUSTOM_DICT_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        error_handler.log_warning(
            PipelineStage.AUDIO,
            f"tts_normalizer: custom_dict.json ilegible: {e}",
        )
        return 0

    applied = 0
    for entry in data.get("entries", []):
        try:
            token = entry["token"]
            pron = entry.get("pronunciation", "")
            cat = entry["category"]
        except KeyError:
            continue

        if cat == "spelled":
            ACRONYMS_SPELLED[token] = pron
        elif cat == "pronounceable":
            ACRONYMS_PRONOUNCEABLE.add(token)
        elif cat == "abbreviation":
            ABBREVIATIONS_ES[token] = pron
        elif cat == "unit":
            UNITS_MAP[token] = pron
        else:
            continue
        applied += 1
    return applied


# Cargar al importar.
_load_custom_dict()
