"""
subs_remap.py — Remap de timings normalizado→original para subtítulos legibles.

PROBLEMA (confirmado por Omar, primer video): el .ass hereda el texto NORMALIZADO
para TTS (años expandidos "mil ochocientos veinte", nombres EN fonetizados
"Américan Cólech ov de Bílding Arts") porque el forced-alignment corrió sobre
`text_for_tts`. El espectador LEE el fonético en vez del original legible.

FIX (CAMINO B): reasignar los timings YA existentes (del normalizado) al texto
ORIGINAL vía diff token-a-token. NO re-genera audio ni re-alinea. Costo API = 0.

Lo usa fase2b._build_chapter_segment ANTES de _build_ass_from_words:
    words_orig = remap_words_to_original(plan.narration, timestamps_words)
    _build_ass_from_words(words=words_orig, ...)
"""
from __future__ import annotations

import difflib

# Puntuación ignorada al COMPARAR tokens (no al mostrarlos).
_PUNCT = ".,;:!?\"'()¿¡—–-«»…“”"


def _key(tok: str) -> str:
    """Clave de comparación: minúsculas + sin puntuación de borde.

    NO quita acentos a propósito: queremos que 'Américan' ≠ 'American' caiga en
    un bloque 'replace' (es texto fonetizado, no el mismo token).
    """
    return tok.strip(_PUNCT).lower()


def remap_words_to_original(
    original_text: str,
    normalized_words: list[dict],
) -> list[dict]:
    """Reasigna los timings del texto normalizado al texto ORIGINAL.

    Args:
        original_text: narración ORIGINAL legible del cap (plan.narration en runtime).
        normalized_words: list[{word,start,end}] de chXX_timestamps.json (word-level).
            Puede traer tokens de espacio puro " " — se filtran acá.

    Returns:
        list[{word,start,end}] con las words ORIGINALES (display) y timings
        remapeados, listo para _build_ass_from_words. Lista vacía si no hay
        texto original.

    Reglas:
      - Token igual → copia su timing tal cual.
      - Span cambiado (replace/insert) → los token(s) original(es) reciben el
        timing COMBINADO del run normalizado que reemplazan [start_primero,
        end_último]. Si el span original tiene >1 token, la ventana combinada se
        reparte proporcional al largo en chars (para que los `start` queden
        estrictamente crecientes — _build_ass_from_words deriva el `end` de cada
        palabra del `start` de la siguiente). Para el caso 1→N (año) esto se
        reduce a "el único token recibe el span entero" = handoff literal.
      - Tokens normalizados sin original (delete) → se descartan (su tiempo lo
        absorben los vecinos).
    """
    norm = [dict(w) for w in normalized_words if w.get("word", "").strip()]
    orig = original_text.split()

    if not orig:
        return []
    if not norm:
        # Sin timings: devolver words sin timing; el caller decide fallback.
        return [{"word": t, "start": 0.0, "end": 0.0} for t in orig]

    a = [_key(w["word"]) for w in norm]   # claves normalizado
    b = [_key(t) for t in orig]           # claves original

    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    out: list[dict] = []

    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            for k in range(j2 - j1):
                nw = norm[i1 + k]
                out.append({
                    "word": orig[j1 + k],
                    "start": float(nw["start"]),
                    "end": float(nw["end"]),
                })
            continue

        # replace / insert / delete
        orig_span = orig[j1:j2]
        if not orig_span:
            # delete puro: tokens normalizados sin contraparte original → descartar.
            continue

        if i2 > i1:
            # replace: ventana = del primer al último token normalizado reemplazado.
            span_start = float(norm[i1]["start"])
            span_end = float(norm[i2 - 1]["end"])
        else:
            # insert puro: original tiene tokens sin timing normalizado.
            # Anclar al borde entre el fin del último out y el siguiente token norm.
            span_start = out[-1]["end"] if out else float(norm[0]["start"])
            span_end = float(norm[i1]["start"]) if i1 < len(norm) else span_start

        if span_end <= span_start:
            span_end = span_start + 0.05

        # Repartir la ventana combinada entre los tokens originales del span,
        # proporcional al largo en chars (starts estrictamente crecientes).
        lens = [max(1, len(t)) for t in orig_span]
        total = sum(lens)
        cursor = span_start
        for k, tok in enumerate(orig_span):
            seg = (span_end - span_start) * (lens[k] / total)
            s = cursor
            e = span_end if k == len(orig_span) - 1 else cursor + seg
            out.append({"word": tok, "start": s, "end": e})
            cursor = e

    # Pasada defensiva: starts estrictamente crecientes, end >= start.
    for k in range(1, len(out)):
        if out[k]["start"] <= out[k - 1]["start"]:
            out[k]["start"] = out[k - 1]["start"] + 0.01
        if out[k]["end"] < out[k]["start"]:
            out[k]["end"] = out[k]["start"] + 0.05

    return out
