"""
anchor_timing.py — matcher COMPARTIDO anchor→tiempo.

Extraído de fase2b._compute_durations_from_anchors (chat 54) para que m03
(reconciliación temporal de anchors, timing-aware merge) y fase2b (reparto de
duración por imagen) midan IDÉNTICO. Si cada uno usara su propio matcher, m03
podría creer que dos anchors están bien espaciados mientras fase2b los reparte
sub-segundo → se cuela un flash de DepthFlow.

Contrato (HANDOFF_135e — fix del veredicto diag_235):
  - TOLERA entries no-palabra: el Forced Alignment de ElevenLabs intercala entries de
    ESPACIO/PUNTUACIÓN entre palabras. Se filtran ANTES de matchear (preservando el
    índice original → los tiempos NO cambian) para que el trigrama consecutivo reviva.
    Esto cura los topics YA grabados sin regenerar audio.
  - NEEDLE normalizado como el TTS: el FA alinea contra text_for_tts (normalizado,
    "29"→"veintinueve"); los anchors vienen del guion CRUDO. Se pasa el anchor por
    normalize_for_tts (import LAZY — tts_normalizer arrastra config, y qa_studio_server
    importa este módulo evitando esas deps a propósito) antes de tokenizar.
  - Fallback ENDURECIDO: escalera 3-tokens → 2-tokens → 1-token SOLO si ≥4 chars (mata
    el/la/de/que/en/los, la raíz del start prematuro). Si nada matchea → None (uniforme).
  - GRITA en fallback (2tok/1tok): antes era silencioso y el start falso pasaba sin aviso.
  - cursor avanza para asegurar orden; None si starts no quedan crecientes.
"""
from __future__ import annotations

import re


def _norm(tok: str) -> str:
    # quita puntuación + lower
    return re.sub(r"[^\w]", "", tok or "", flags=re.UNICODE).lower()


def _first_n_tokens(text: str, n: int = 3) -> list[str]:
    toks = [_norm(t) for t in text.split() if _norm(t)]
    return toks[:n]


def _needle_normalized(anchor: str, n: int = 3) -> list[str]:
    """Primeras n palabras normalizadas del anchor, pero pasándolo ANTES por la MISMA vara
    del TTS (normalize_for_tts) → "29 de septiembre" tokeniza como "veintinueve de
    septiembre", que es lo que el Forced Alignment alineó (capa 2 del diag_235).

    Import LAZY + defensivo: tts_normalizer arrastra `config` (deps pesadas) y qa_studio_server
    importa anchor_timing evitándolas a propósito. Si el normalizer no está o falla → se usa
    el anchor crudo (la capa 1 —filtrar huecos— igual revive el trigrama en la mayoría)."""
    try:
        from tts_normalizer import normalize_for_tts
        anchor = normalize_for_tts(anchor, language="es")
    except Exception:  # noqa: BLE001 — el normalizer es best-effort, nunca rompe el matcher
        pass
    return _first_n_tokens(anchor, n=n)


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

    # CAPA 1 (diag_235): el FA intercala entries de espacio/puntuación → los huecos matan el
    # trigrama consecutivo. Matchear sobre las palabras REALES; real_idx mapea al índice
    # original para leer el start (los TIEMPOS no cambian, solo se saltan los huecos).
    real_norm: list[str] = []
    real_idx: list[int] = []
    for idx, w in enumerate(words):
        n = _norm(w.get("word", ""))
        if n:
            real_norm.append(n)
            real_idx.append(idx)
    if not real_norm:
        return None

    starts: list[float] = []
    cursor = 0  # avanza (en espacio real) para asegurar orden
    for ai, anchor in enumerate(anchors):
        needle = _needle_normalized(anchor, n=3)   # CAPA 2: needle normalizado como el TTS
        if not needle:
            return None
        found, matched_by = -1, None
        # Fallback ENDURECIDO: escalera 3 → 2 → 1(≥4 chars).
        for nlen in (3, 2):
            if len(needle) < nlen:
                continue
            sub = needle[:nlen]
            for i in range(cursor, len(real_norm) - nlen + 1):
                if real_norm[i:i + nlen] == sub:
                    found, matched_by = i, f"{nlen}-tokens"
                    break
            if found >= 0:
                break
        if found < 0 and len(needle[0]) >= 4:   # 1-token SOLO si ≥4 chars (mata el/la/de/que/en)
            for i in range(cursor, len(real_norm)):
                if real_norm[i] == needle[0]:
                    found, matched_by = i, "1-token"
                    break
        if found < 0:
            return None
        orig_i = real_idx[found]
        st = float(words[orig_i].get("start", 0.0))
        starts.append(st)
        # C) verdad de papeles: el fallback GRITA (silencio solo cuando matchea el trigrama).
        if matched_by in ("2-tokens", "1-token"):
            print(f"[anchor_timing] anchor #{ai} por FALLBACK-{matched_by}: "
                  f"'{words[orig_i].get('word', '')}' @ {st:.2f}s")
        cursor = found + 1

    # Validación: starts crecientes
    for i in range(1, len(starts)):
        if starts[i] <= starts[i - 1]:
            return None

    return starts
