"""
test_chat52_pick_gate.py — BLOQUE 2: gate de verificación del pick (anti-varianza de scrape).

BUG (Cowork Monte Carlo): el label ES no es estable corrida-a-corrida (scrapetube no siempre
surfacea el competidor pesado). A p=0.5, ~1 de 4 corridas etiqueta mal un SATURADO como hueco →
riesgo de producir sobre un nicho que creés vacío y no lo está.

FIX: _verify_pick_es_saturation(chosen, n=3) re-mide ES SOLO el/los pick(s), se queda con el PEOR
label, y si flipea a SATURADO pregunta a Omar [P]/[S]/[Q] (NO auto-excluye). NO toca el discovery.

Determinista, SIN red (mockea _measure_es + input). Correr:  python -X utf8 test_chat52_pick_gate.py
"""
from __future__ import annotations

import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import builtins
import io
from contextlib import redirect_stdout

import fase1

_fails: list[str] = []


def check(cond: bool, msg: str):
    print(("  ✓ " if cond else "  ✗ ") + msg)
    if not cond:
        _fails.append(msg)


def _seed(title="Tema X", already_es=True, orig_label="HUECO"):
    return {
        "seed_title": title,
        "remeasure": {"es_query": title, "entity": title, "already_es": already_es},
        "evidence": {"es_gap": {"label": orig_label}},
    }


def _mock_measure(labels):
    """Devuelve un fake _measure_es que recorre `labels` por llamada (saturación derivada)."""
    sat_for = {"VACIO": 0, "HUECO": 10_000, "DISPUTADO": 80_000, "SATURADO": 300_000}
    seq = iter(labels)

    def fake(search_query, entity=None, already_es=False):
        lab = next(seq)
        return {"label": lab, "saturation": sat_for[lab]}
    return fake


def _run_gate(seed, labels, answers=()):
    """Corre el gate con _measure_es y input mockeados; captura stdout. Devuelve (resultado, log)."""
    orig_measure, orig_input = fase1._measure_es, builtins.input
    ans = iter(answers)
    fase1._measure_es = _mock_measure(labels)
    builtins.input = lambda *a, **k: next(ans)
    buf = io.StringIO()
    try:
        with redirect_stdout(buf):
            res = fase1._verify_pick_es_saturation([seed], n=3)
    finally:
        fase1._measure_es, builtins.input = orig_measure, orig_input
    return res, buf.getvalue()


def test_estable_sin_aviso():
    print("\n[B2] 3× HUECO (estable) → pasa sin aviso ni input")
    res, log = _run_gate(_seed("Estable"), ["HUECO", "HUECO", "HUECO"])
    check(res is not None and len(res) == 1, "conserva el pick estable")
    check("FLIPEÓ a SATURADO" not in log, "NO dispara el aviso de flip")
    check("peor de 3: HUECO" in log, "reporta peor=HUECO sobre 3 corridas")


def test_flip_sacar():
    print("\n[B2] HUECO,HUECO,SATURADO + [S]acar → quita el pick (peor = SATURADO)")
    res, log = _run_gate(_seed("Flipante"), ["HUECO", "HUECO", "SATURADO"], answers=["S"])
    check("peor de 3: SATURADO" in log, "se queda con el PEOR label (SATURADO)")
    check("FLIPEÓ a SATURADO" in log, "dispara el aviso de flip")
    check(res is None, "1 solo pick sacado → None (no se investiga nada)")


def test_flip_disputado():
    print("\n[B2] HUECO,HUECO,DISPUTADO + [S]acar → dispara aviso (B1: evergreen None caen en DISPUTADO)")
    res, log = _run_gate(_seed("Disputado"), ["HUECO", "HUECO", "DISPUTADO"], answers=["S"])
    check("peor de 3: DISPUTADO" in log, "se queda con el PEOR label (DISPUTADO)")
    check("FLIPEÓ a DISPUTADO" in log, "DISPUTADO ahora dispara el aviso (antes pasaba mudo)")
    check("hay competencia real" in log, "mensaje específico de DISPUTADO")
    check(res is None, "[S] sobre único pick → None")


def test_flip_producir():
    print("\n[B2] HUECO,HUECO,SATURADO + [P]roducir igual → conserva el pick")
    res, log = _run_gate(_seed("Flipante"), ["SATURADO", "HUECO", "HUECO"], answers=["P"])
    check("FLIPEÓ a SATURADO" in log, "dispara el aviso aunque el SATURADO sea la 1ª corrida")
    check(res is not None and len(res) == 1, "[P] conserva el pick (Omar decide)")


def test_sin_receta():
    print("\n[B2] seed sin receta remeasure (Mode B / viejo) → no re-mide, conserva")
    seed = {"seed_title": "ModeB", "evidence": {"es_gap": {"label": "VACIO"}}}
    orig = fase1._measure_es
    called = {"n": 0}

    def spy(*a, **k):
        called["n"] += 1
        return {"label": "SATURADO", "saturation": 300_000}
    fase1._measure_es = spy
    buf = io.StringIO()
    try:
        with redirect_stdout(buf):
            res = fase1._verify_pick_es_saturation([seed], n=3)
    finally:
        fase1._measure_es = orig
    check(called["n"] == 0, "NO llama _measure_es sin receta")
    check(res is not None and len(res) == 1, "conserva el seed sin receta")
    check("sin receta remeasure" in buf.getvalue(), "lo dice claro en el log")


if __name__ == "__main__":
    test_estable_sin_aviso()
    test_flip_sacar()
    test_flip_disputado()
    test_flip_producir()
    test_sin_receta()

    print("\n" + ("=" * 60))
    if _fails:
        print(f"FALLOS: {len(_fails)}")
        for f in _fails:
            print(f"  - {f}")
        sys.exit(1)
    print("TODO OK")
