"""
anchor_timing.py — matcher COMPARTIDO anchor→tiempo.

Extraído de fase2b._compute_durations_from_anchors (chat 54) para que m03
(reconciliación temporal de anchors, timing-aware merge) y fase2b (reparto de
duración por imagen) midan IDÉNTICO. Si cada uno usara su propio matcher, m03
podría creer que dos anchors están bien espaciados mientras fase2b los reparte
sub-segundo → se cuela un flash de DepthFlow.

Comportamiento byte-idéntico al matcher inline original:
  - normaliza tokens (quita puntuación, lower)
  - busca cada anchor por sus primeras 3 palabras normalizadas en word_norm
  - fallback laxo: solo el primer token
  - cursor avanza para asegurar orden
  - devuelve None si algún anchor no matchea o los starts no quedan crecientes
"""
from __future__ import annotations

import re


def _norm(tok: str) -> str:
    # quita puntuación + lower
    return re.sub(r"[^\w]", "", tok or "", flags=re.UNICODE).lower()


def _first_n_tokens(text: str, n: int = 3) -> list[str]:
    toks = [_norm(t) for t in text.split() if _norm(t)]
    return toks[:n]


def compute_anchor_starts(
    anchors: list[str],
    words: list[dict],
) -> list[float] | None:
    """Devuelve el `start` (segundos) de cada anchor en `words`, o None.

    Args:
        anchors: lista de narration_anchors (substrings de la narración del cap).
        words: word-timestamps [{word, start, end}, ...] de chXX_timestamps.json.

    Returns:
        list[float] con el start de cada anchor (mismo orden), o None si:
          - anchors o words están vacíos,
          - algún anchor no matchea (ni por 3-tokens ni por primer token),
          - los starts no quedan estrictamente crecientes.
    """
    if not anchors or not words:
        return None

    word_norm = [_norm(w.get("word", "")) for w in words]

    starts: list[float] = []
    cursor = 0  # avanza para asegurar orden
    for anchor in anchors:
        needle = _first_n_tokens(anchor, n=3)
        if not needle:
            return None
        found = -1
        for i in range(cursor, len(words) - len(needle) + 1):
            if word_norm[i:i + len(needle)] == needle:
                found = i
                break
        if found < 0:
            # fallback más laxo: solo primer token
            for i in range(cursor, len(words)):
                if word_norm[i] == needle[0]:
                    found = i
                    break
        if found < 0:
            return None
        starts.append(float(words[found].get("start", 0.0)))
        cursor = found + 1

    # Validación: starts crecientes
    for i in range(1, len(starts)):
        if starts[i] <= starts[i - 1]:
            return None

    return starts
