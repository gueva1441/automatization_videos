"""
gfx_peak.py — F3: el pico del capítulo (pedido de Omar 2026-10-20). F36 §D: queda solo la utilería de la voz que
usan clima y voz_utils: `sentences` (las frases de la narración con sus palabras y tiempos), `lexicon_hits` (las
palabras del léxico de moods) y `prefer_icon_nouns`. Lo demás (plan_peak, nivel de agua, zoom con latido, reloj de
gfx_peak, clear_around) se borró; el reloj en la esquina y la palabra del pico pasaron a voz_datos.
"""
from __future__ import annotations

import re
from typing import Any

from gfx_config import gfx_rules


def _clean(w: str) -> str:
    return re.sub(r"^[¿¡\"«(]+|[.,;:!?\"»)]+$", "", str(w)).lower()


def sentences(words: list[dict], time_offset: float = 0.0) -> list[dict[str, Any]]:
    """Frases de la narración con sus palabras (índices) y tiempos."""
    out, cur = [], []
    for i, w in enumerate(words):
        if not str(w.get("word", "")).strip():
            continue
        cur.append(i)
        if re.search(r"[.!?…]$", str(w["word"]).strip()):
            out.append(cur)
            cur = []
    if cur:
        out.append(cur)
    return [{"idx": s, "t0": float(words[s[0]]["start"]) + time_offset, "t1": float(words[s[-1]]["end"]) + time_offset,
             "text": " ".join(str(words[i]["word"]).strip() for i in s)} for s in out]


def lexicon_hits(words: list[dict], moods: dict[str, dict], idxs: list[int] | None = None) -> list[dict[str, Any]]:
    hits = []
    for i in (idxs if idxs is not None else range(len(words))):
        k = _clean(words[i].get("word", ""))
        for cat, m in moods.items():
            if k in (m.get("triggers") or {}):
                hits.append({"i": i, "word": k, "category": cat, "weight": int(m["triggers"][k])})
                break
    return hits


def prefer_icon_nouns(hits: list[dict[str, Any]], moods: dict[str, dict]) -> list[dict[str, Any]]:
    """F5f (con stamp_nouns_only): en UNA frase, un sustantivo del mapa de íconos de su categoría (icon_words, peso ≥ 2)
    gana siempre sobre un adjetivo de la MISMA categoría: «cadáveres» (calavera) sobre «escalofriantes». El adjetivo
    sale de los candidatos de esa frase; los de otras categorías quedan."""
    if not gfx_rules.stamp_nouns_only or len(hits) < 2:
        return hits
    from script_engine.m05_narrative import adjectives

    def _adj(w: str) -> bool:
        return bool(adjectives(w))
    noun_cats = {h["category"] for h in hits if h["weight"] >= 2 and not _adj(h["word"])
                 and h["word"] in ((moods.get(h["category"]) or {}).get("icon_words") or {})}
    return [h for h in hits if not (h["category"] in noun_cats and _adj(h["word"]))]
