"""
test_module_qa_form_cost.py — HANDOFF_133 (offline, sin server ni subprocess).

Verifica el costo Gemini EN VIVO del QA form:
  (a) emit_cost_marker: con QA_FORM imprime 1 línea @@QAFORM_COST@@ JSON válida; sin QA_FORM, nada.
  (b) _form_apply_cost: bucketea por ETAPA (fase activa) y por modelo, suma total/calls/tokens.
  (c) fase None → etapa '(inicio)' (no rompe).

USO:
    python test_module_qa_form_cost.py
"""
import io
import json
import sys
from contextlib import redirect_stdout

import qa_form_markers
from qa_studio_server import _empty_gemini_cost, _form_apply_cost, _FORM_COST_MARKER


def _check(cond, msg, fails):
    if not cond:
        fails.append(msg)


def _emit_capture(qa_form_on: bool) -> str:
    prev = qa_form_markers.QA_FORM
    qa_form_markers.QA_FORM = qa_form_on
    try:
        buf = io.StringIO()
        with redirect_stdout(buf):
            qa_form_markers.emit_cost_marker("Gemini 2.5 Pro", 0.0101, 100, 200, 800)
        return buf.getvalue()
    finally:
        qa_form_markers.QA_FORM = prev


def main() -> int:
    fails: list[str] = []

    # ── (a) gating + formato del marcador ──
    out_off = _emit_capture(False)
    _check(out_off.strip() == "", "(a) sin QA_FORM NO debe emitir marcador", fails)

    out_on = _emit_capture(True)
    _check(out_on.startswith(_FORM_COST_MARKER), "(a) con QA_FORM debe emitir @@QAFORM_COST@@", fails)
    try:
        m = json.loads(out_on[len(_FORM_COST_MARKER):])
        _check(m["model"] == "Gemini 2.5 Pro" and m["think"] == 800 and m["usd"] == 0.0101,
               f"(a) payload del marcador incorrecto: {m}", fails)
    except Exception as e:
        fails.append(f"(a) marcador no es JSON válido: {e}")

    # ── (b) bucketing por etapa + modelo ──
    gc = _empty_gemini_cost()
    _form_apply_cost(gc, {"model": "Gemini 2.5 Pro", "usd": 0.01, "in": 100, "out": 200, "think": 800}, "RESEARCH")
    _form_apply_cost(gc, {"model": "Gemini 2.5 Flash", "usd": 0.002, "in": 50, "out": 60, "think": 10}, "RESEARCH")
    _form_apply_cost(gc, {"model": "Gemini 2.5 Pro", "usd": 0.05, "in": 7000, "out": 5000, "think": 8000}, "GUION")
    _check(round(gc["total_usd"], 6) == 0.062, f"(b) total {gc['total_usd']} != 0.062", fails)
    _check(gc["calls"] == 3, f"(b) calls {gc['calls']} != 3", fails)
    _check(gc["by_phase"]["RESEARCH"]["calls"] == 2, "(b) RESEARCH no acumuló 2 calls", fails)
    _check(round(gc["by_phase"]["GUION"]["usd"], 6) == 0.05, "(b) GUION usd mal", fails)
    _check(round(gc["by_model"]["Gemini 2.5 Pro"]["usd"], 6) == 0.06, "(b) Pro por-modelo mal", fails)
    _check(gc["tokens_thinking"] == 8810, f"(b) thinking total {gc['tokens_thinking']} != 8810", fails)

    # ── (c) fase None → '(inicio)' ──
    gc2 = _empty_gemini_cost()
    _form_apply_cost(gc2, {"model": "Gemini 2.5 Pro", "usd": 0.001, "in": 1, "out": 1, "think": 1}, None)
    _check("(inicio)" in gc2["by_phase"], "(c) fase None no cayó en '(inicio)'", fails)

    if fails:
        print(f"[FAIL] {len(fails)} assert(s):")
        for f in fails:
            print(f"   ✗ {f}")
        return 1
    print("[PASS] QA form cost: marcador gated+válido, bucketing por etapa/modelo, fase None tolerada")
    return 0


if __name__ == "__main__":
    sys.exit(main())
