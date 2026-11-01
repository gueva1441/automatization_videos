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
    "29"→"veintinueve"); los anchors vienen del guion CRUDO. F71: con normalizado del cap
    (`narr_norm`, de 01b_narration_normalized.json) la aguja sale del MISMO texto que leyó la
    voz (`_agujas_de_voz`); sin él, por normalize_for_tts, que es lo que la voz usa en ese caso
    (import LAZY — tts_normalizer arrastra config, y qa_studio_server importa este módulo
    evitando esas deps a propósito).
  - Fallback ENDURECIDO: escalera 3-tokens → 2-tokens → 1-token SOLO si ≥4 chars (mata
    el/la/de/que/en/los, la raíz del start prematuro). Si nada matchea → None (uniforme).
  - GRITA en fallback (2tok/1tok): antes era silencioso y el start falso pasaba sin aviso.
  - cursor avanza para asegurar orden; None si starts no quedan crecientes.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

NORMALIZADO = "01b_narration_normalized.json"
VENTANA_AGUJA = 200   # HANDOFF_F71, derivado: 3 tokens caben de sobra; solo acota normalize_pool_forms


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


def cargar_normalizado(topic_id: str, base_dir: Path | None = None) -> dict[int, dict]:
    """F71: {n de cap: entrada de 01b_narration_normalized.json}, solo los caps que la voz lee de ahí (la misma decisión que
    audio_manager._resolve_text_for_tts: `narration_normalized` no vacío). {} si no existe o no se puede leer."""
    f = (base_dir or Path(__file__).resolve().parent) / "data" / "scripts" / "_steps" / topic_id / NORMALIZADO
    try:
        caps = json.loads(f.read_text(encoding="utf-8")).get("chapters", [])
    except (OSError, ValueError):
        return {}
    return {int(c["chapter_number"]): c for c in caps if isinstance(c.get("narration_normalized"), str)
            and c["narration_normalized"].strip()}


def normalizado_de_timestamps(timestamps_path: Path | str | None) -> dict | None:
    """F71: la entrada del cap a partir de output/audio/<topic>/chNN_timestamps.json, para los que solo tienen esa ruta."""
    p = Path(timestamps_path) if timestamps_path else None
    m = re.match(r"ch(\d+)_", p.name) if p else None
    return cargar_normalizado(p.parent.name).get(int(m.group(1))) if m else None


def _pool_forms(texto: str) -> str:
    """normalize_pool_forms, LAZY y defensivo como `_needle_normalized`."""
    try:
        from tts_normalizer import normalize_pool_forms
        return normalize_pool_forms(texto)
    except Exception:  # noqa: BLE001 — best-effort, nunca rompe el matcher
        return texto


def _agujas_de_voz(anchors: list[str], narr_norm: dict, n: int = 3) -> list[list[str]]:
    """F71: la aguja de cada anchor, del MISMO texto que leyó la voz. Se ubican los anchors en `narration_original` (en orden,
    con cursor) y se re-aplican los spans como `m02_5._apply_spans_to_narration` (más largo primero, primera aparición) corriendo
    los offsets; un offset dentro de un span cae al inicio del reemplazo. Importa la primera aparición: «Maitland»→«Méitland» se
    aplicó solo a la primera, y aplicar el span al anchor suelto falla en las otras. Un anchor que no está literal (narración
    editada después de m03) recibe los spans sobre su propio texto."""
    texto = narr_norm.get("narration_original") or ""
    spans = sorted((s for s in narr_norm.get("spans_applied") or []
                    if s.get("decision") == "applied" and s.get("category") != "f5_pool_forms" and s.get("original")),
                   key=lambda s: len(s["original"]), reverse=True)
    limpios = [(a or "").strip() for a in anchors]
    offsets, cursor = [], 0
    for a in limpios:
        i = texto.find(a, cursor) if a else -1
        offsets.append(i)
        if i >= 0:
            cursor = i + 1
    for s in spans:
        viejo, nuevo = s["original"], s.get("suggested") or ""
        idx = texto.find(viejo)
        if idx < 0:
            continue
        texto = texto[:idx] + nuevo + texto[idx + len(viejo):]
        d = len(nuevo) - len(viejo)
        offsets = [x if x < 0 or x <= idx else (x + d if x >= idx + len(viejo) else idx) for x in offsets]
    agujas = []
    for a, x in zip(limpios, offsets):
        if x >= 0:
            trozo = texto[x:x + VENTANA_AGUJA]
        else:
            trozo = a
            for s in spans:
                trozo = trozo.replace(s["original"], s.get("suggested") or "", 1)
        agujas.append(_first_n_tokens(_pool_forms(trozo), n=n))
    return agujas


def compute_anchor_starts(
    anchors: list[str],
    words: list[dict],
    narr_norm: dict | None = None,
) -> list[float] | None:
    """Devuelve el `start` (segundos) de cada anchor en `words`, o None.

    Args:
        anchors: lista de narration_anchors (substrings de la narración del cap).
        words: word-timestamps [{word, start, end}, ...] de chXX_timestamps.json.
        narr_norm: F71, la entrada del cap en 01b_narration_normalized.json; None si la voz no leyó de ahí.

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

    agujas = _agujas_de_voz(anchors, narr_norm, n=3) if narr_norm else None
    starts: list[float] = []
    cursor = 0  # avanza (en espacio real) para asegurar orden
    for ai, anchor in enumerate(anchors):
        needle = agujas[ai] if agujas else _needle_normalized(anchor, n=3)   # CAPA 2: needle como lo que leyó la voz
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
