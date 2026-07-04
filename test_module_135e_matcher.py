"""
test_module_135e_matcher.py — HANDOFF_135e (offline, sin API).

Fix del matcher anchor→tiempo (veredicto diag_235):
  1. words con entries de espacio/puntuación intercaladas → 3-tokens revive, start con idx original.
  2. anchor que solo resolvería por 1-token stopword ("el …") sin trigrama → None (sin start falso).
  3. regresión: words limpias (formato viejo) → 3-tokens idéntico.
  4. escalera nueva: trigrama roto pero bigrama OK → 2-tokens; 1-token SOLO si ≥4 chars.
  5. filtro del productor (audio_manager B): _norm descarta espacios/puntuación pura.
  6. capa 2 honesta: número que LIDERA el anchor sin trigrama → None (normalize_for_tts es minimal).

USO:
    python test_module_135e_matcher.py
"""
import io
import sys
from contextlib import redirect_stdout

from anchor_timing import compute_anchor_starts, _norm


def _W(words, step=1.0):
    return [{"word": w, "start": float(i) * step, "end": float(i) * step + 0.4}
            for i, w in enumerate(words)]


def _check(c, m, fails):
    if not c:
        fails.append(m)


def main() -> int:
    fails: list[str] = []

    # ── (1) espacios intercalados (patrón real del FA) → 3-tokens, start con idx ORIGINAL ──
    words = []
    for i, w in enumerate(["día", "que", "el", "huracán", "katrina"]):
        words.append({"word": w, "start": float(i), "end": i + 0.4})
        words.append({"word": " ", "start": i + 0.4, "end": i + 0.5})   # hueco del FA
    buf = io.StringIO()
    with redirect_stdout(buf):
        r = compute_anchor_starts(["día que el huracán"], words)
    _check(r == [0.0], f"(1) empties intercaladas no revivió 3-tokens: {r}", fails)
    _check("FALLBACK" not in buf.getvalue(), "(1) matcheó por fallback (debía ser 3-tokens, silencioso)", fails)

    # ── (2) stopword 'el' sin trigrama posible → None (ya no start prematuro) ──
    r2 = compute_anchor_starts(["El zzz qqq"], _W(["el", "agua", "subio", "el", "frio"]))
    _check(r2 is None, f"(2) stopword sin trigrama debía dar None: {r2}", fails)

    # ── (3) regresión: words limpias (viejo Whisper, sin huecos) → 3-tokens ──
    r3 = compute_anchor_starts(["La ciudad entera"], _W(["la", "ciudad", "entera", "quedo", "bajo"]))
    _check(r3 == [0.0], f"(3) regresión words limpias rota: {r3}", fails)

    # ── (4) escalera: trigrama roto pero bigrama OK → 2-tokens (grita) ──
    buf4 = io.StringIO()
    with redirect_stdout(buf4):
        r4 = compute_anchor_starts(["agua contaminada zzzz"], _W(["agua", "contaminada", "subio"]))
    _check(r4 == [0.0], f"(4) 2-tokens no matcheó: {r4}", fails)
    _check("FALLBACK-2-tokens" in buf4.getvalue(), "(4) 2-tokens no gritó", fails)
    # 1-token: distintivo ≥4 matchea; stopword <4 no
    r4b = compute_anchor_starts(["huracán zzz qqq"], _W(["viento", "huracán", "fuerte"]))
    _check(r4b == [1.0], f"(4) 1-token ≥4 no matcheó: {r4b}", fails)
    r4c = compute_anchor_starts(["de zzz qqq"], _W(["viento", "de", "fuerte"]))  # 'de' <4 → no 1-token
    _check(r4c is None, f"(4) 1-token <4 chars ('de') NO debía matchear: {r4c}", fails)

    # ── (5) filtro del productor B: _norm descarta no-palabra ──
    _check(_norm(" ") == "" and _norm(",") == "" and _norm("...") == "",
           "(5) _norm no descarta espacio/puntuación pura", fails)
    _check(_norm("Día,") == "día", "(5) _norm rompió una palabra real", fails)

    # ── (6) capa 2 honesta: número que LIDERA sin trigrama → None (normalize_for_tts minimal) ──
    r6 = compute_anchor_starts(["29 de septiembre"], _W(["veintinueve", "de", "septiembre", "llego"]))
    _check(r6 is None, f"(6) número-líder debía degradar a None (honesto): {r6}", fails)
    # número MID (caso real): el needle es TEXTO → 3-tokens matchea igual
    r6b = compute_anchor_starts(["comenzó a tejerse el 29 de agosto"],
                                _W(["comenzó", "a", "tejerse", "el", "veintinueve", "de", "agosto"]))
    _check(r6b == [0.0], f"(6) número MID debía matchear por 3-tokens: {r6b}", fails)

    if fails:
        print(f"[FAIL] {len(fails)} assert(s):")
        for f in fails:
            print(f"   ✗ {f}")
        return 1
    print("[PASS] matcher: empties toleradas (3-tokens revive), escalera 3→2→1(≥4), "
          "stopword→None, número-líder→None honesto, regresión limpia OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
