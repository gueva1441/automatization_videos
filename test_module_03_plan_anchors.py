"""
test_module_03_plan_anchors.py — BLOQUE 2 del handoff m03 two-step: PASO 1 (_plan_anchors) + fallback.

Cubre los 3 candados de Omar:
  #1 el schema fuerza CANTIDAD, no contenido → un "" pasa el schema pero _validate_anchor_substring
     lo rechaza; la validación (substring/orden/no-solapa) es la red real, el fallback el último seguro.
  #2 el anchor GLOBAL del clip Veo se planifica en el Paso 1 (no queda colgado).
  #3 el fallback garantiza EXACTAMENTE n ventanas SIEMPRE, incluso si hay menos oraciones que n
     (degrada oraciones→palabras→chars). Se prueba el borde sentences < n.

Determinista, SIN red (mockea m03_visual.call_flash_json). Correr:
  python -X utf8 test_module_03_plan_anchors.py
"""
from __future__ import annotations

import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import io
from contextlib import redirect_stdout

import script_engine.m03_visual as m

_fails: list[str] = []


def check(cond: bool, msg: str):
    print(("  ✓ " if cond else "  ✗ ") + msg)
    if not cond:
        _fails.append(msg)


# Narración sintética con 6 oraciones claras.
NARR = (
    "Primera oración del capítulo sobre el evento. "
    "Segunda oración con más detalle del contexto histórico. "
    "Tercera oración que describe a las personas afectadas. "
    "Cuarta oración sobre las consecuencias más graves. "
    "Quinta oración que cierra el desarrollo del tema. "
    "Sexta y última oración que revela el misterio final."
)
LAST_SENT = "Sexta y última oración que revela el misterio final."
VEO_ZONE_CHARS = len(LAST_SENT)  # zona Veo (end) = exactamente la última oración


def _patch_flash(return_value):
    """Reemplaza m.call_flash_json por uno que devuelve siempre return_value (o lo llama)."""
    calls = {"n": 0}

    def fake(prompt, system_instruction=None, response_schema=None):
        calls["n"] += 1
        return return_value(calls["n"]) if callable(return_value) else return_value
    orig = m.call_flash_json
    m.call_flash_json = fake
    return orig, calls


def _spans_ok(items, narration):
    """Verifica: anchors no vacíos, narration[pos:end]==anchor, orden estricto, sin solapa."""
    last_end = -1
    last_pos = -1
    for it in items:
        a, p, e = it["anchor"], it["pos"], it["end"]
        if not a:
            return False, "anchor vacío"
        if narration[p:e] != a:
            return False, f"pos/end no coinciden con el anchor ({narration[p:e]!r} != {a!r})"
        if p <= last_pos:
            return False, "fuera de orden"
        if p < last_end:
            return False, "solapa con el anterior"
        last_pos, last_end = p, e
    return True, "ok"


def test_veo_llm_ok():
    print("\n[B2] veo LLM-ok → veo_anchor + n supps válidos (candado #2: veo anchor en Paso 1)")
    n = 3
    resp = {
        "veo_anchor": "revela el misterio final.",   # ⊂ zona Veo (última oración)
        "supplemental_anchors": [
            "Primera oración del capítulo sobre el evento.",
            "Segunda oración con más detalle del contexto histórico.",
            "Tercera oración que describe a las personas afectadas.",
        ],
    }
    orig, calls = _patch_flash(resp)
    try:
        out = m._plan_anchors(NARR, n, "veo", veo_position="end", veo_zone_chars=VEO_ZONE_CHARS, cap_number=7)
    finally:
        m.call_flash_json = orig
    check(calls["n"] == 1, "1 sola llamada Flash (ok al primer intento)")
    check("veo_anchor" in out and out["veo_anchor"]["anchor"] == "revela el misterio final.",
          "devuelve el veo_anchor planificado en el Paso 1")
    check(len(out["supplementals"]) == n, f"{n} supplementals")
    ok, why = _spans_ok(out["supplementals"], NARR)
    check(ok, f"supps válidos (substring/orden/no-solapa): {why}")
    # disjunción Veo (position=end): cada supp.end <= veo_anchor.pos
    va_pos = out["veo_anchor"]["pos"]
    check(all(s["end"] <= va_pos for s in out["supplementals"]),
          "supps ANTES del anchor Veo (disjunción end)")


def test_veo_empty_anchor_to_fallback():
    print("\n[B2] veo LLM devuelve un anchor '' (candado #1) → agota retries → fallback determinístico")
    n = 4
    # "" pasa el schema (es string) pero _validate_anchor_substring lo rechaza → todas las corridas fallan.
    bad = {"veo_anchor": "revela el misterio final.",
           "supplemental_anchors": ["Primera oración del capítulo sobre el evento.", "", "x", "y"]}
    orig, calls = _patch_flash(bad)
    buf = io.StringIO()
    try:
        with redirect_stdout(buf):
            out = m._plan_anchors(NARR, n, "veo", veo_position="end", veo_zone_chars=VEO_ZONE_CHARS, cap_number=7)
    finally:
        m.call_flash_json = orig
    log = buf.getvalue()
    check(calls["n"] == m.MAX_RETRY_ATTEMPTS, f"reintentó {m.MAX_RETRY_ATTEMPTS}× antes del fallback")
    check("fallback determinístico (LLM no convergió)" in log, "loguea el fallback (frase del handoff)")
    check(len(out["supplementals"]) == n, f"fallback igualó EXACTAMENTE n={n} supplementals")
    ok, why = _spans_ok(out["supplementals"], NARR)
    check(ok, f"fallback: supps válidos: {why}")
    check(bool(out["veo_anchor"]["anchor"]), "fallback también produce el veo_anchor (candado #2)")
    va_pos = out["veo_anchor"]["pos"]
    check(all(s["end"] <= va_pos for s in out["supplementals"]), "fallback respeta disjunción Veo (end)")


def test_flux_llm_ok_and_fallback():
    print("\n[B2] flux LLM-ok → n anchors; y LLM-fail (wrong count) → fallback n exactos")
    n = 5
    good = {"anchors": [
        "Primera oración del capítulo sobre el evento.",
        "Segunda oración con más detalle del contexto histórico.",
        "Tercera oración que describe a las personas afectadas.",
        "Cuarta oración sobre las consecuencias más graves.",
        "Quinta oración que cierra el desarrollo del tema.",
    ]}
    orig, _ = _patch_flash(good)
    try:
        out = m._plan_anchors(NARR, n, "flux", cap_number=3)
    finally:
        m.call_flash_json = orig
    check(len(out["anchors"]) == n, f"flux ok → {n} anchors")
    ok, why = _spans_ok(out["anchors"], NARR)
    check(ok, f"flux ok: anchors válidos: {why}")

    # LLM devuelve cantidad equivocada SIEMPRE → fallback
    bad = {"anchors": ["Primera oración del capítulo sobre el evento."]}  # 1 != n
    orig, calls = _patch_flash(bad)
    buf = io.StringIO()
    try:
        with redirect_stdout(buf):
            out2 = m._plan_anchors(NARR, n, "flux", cap_number=3)
    finally:
        m.call_flash_json = orig
    check(len(out2["anchors"]) == n, f"flux fallback → EXACTAMENTE n={n}")
    ok2, why2 = _spans_ok(out2["anchors"], NARR)
    check(ok2, f"flux fallback válido: {why2}")


def test_fallback_sentences_lt_n():
    print("\n[B2] candado #3: borde sentences < n → fallback degrada y SIEMPRE devuelve n ventanas")
    # Una sola oración, pero pedimos n=4 → debe subdividir (palabras) y dar 4 ventanas válidas.
    one_sentence = "Esta es una sola oración larga con varias palabras suficientes para subdividir bien"
    for n in (4, 8):
        w = m._fallback_anchor_windows(one_sentence, 0, len(one_sentence), n)
        check(len(w) == n, f"sentences<n: pidiendo {n} → {len(w)} ventanas")
        items = [{"anchor": a, "pos": p, "end": e} for (a, p, e) in w]
        ok, why = _spans_ok(items, one_sentence)
        check(ok, f"n={n}: ventanas válidas (no vacías/orden/no-solapa): {why}")

    # Borde extremo: words < n → tier de chars. "abcdef" (1 palabra, 6 chars) pidiendo n=5.
    w = m._fallback_anchor_windows("abcdef", 0, 6, 5)
    check(len(w) == 5, "words<n: tier de chars → 5 ventanas de 'abcdef'")
    ok, why = _spans_ok([{"anchor": a, "pos": p, "end": e} for (a, p, e) in w], "abcdef")
    check(ok, f"char-tier válido: {why}")

    # determinismo: misma entrada → mismas ventanas
    w1 = m._fallback_anchor_windows(one_sentence, 0, len(one_sentence), 4)
    w2 = m._fallback_anchor_windows(one_sentence, 0, len(one_sentence), 4)
    check(w1 == w2, "fallback determinístico (misma entrada → mismo output)")


if __name__ == "__main__":
    test_veo_llm_ok()
    test_veo_empty_anchor_to_fallback()
    test_flux_llm_ok_and_fallback()
    test_fallback_sentences_lt_n()

    print("\n" + ("=" * 60))
    if _fails:
        print(f"FALLOS: {len(_fails)}")
        for f in _fails:
            print(f"  - {f}")
        sys.exit(1)
    print("TODO OK")
