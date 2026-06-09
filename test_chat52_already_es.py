"""
test_chat52_already_es.py — valida la migración del matcher ES atómico a _measure_es(already_es=True).

CONTEXTO (handoff chat 52): el camino atómico (spy-arbitrage) medía saturación ES con
score_spanish_saturation (substring), que fallaba en AMBAS direcciones:
  - cuenta de menos: no veía la grafía ES distinta (Pacientes psiquiátricos 1900s → SATURADO 246k
    por La Castañeda, que el substring no encontraba);
  - cuenta de más: anclas genéricas pescaban ruido (Pennhurst → falsos que el juez tira).
Fix: el atómico ya está en español → _measure_es(already_es=True) saltea el translate (Q2 del lab:
translate_to_es NO es idempotente sobre texto ya-ES) y usa el juez-LLM de relevancia.

DOS bloques:
  A) UNIT (SIN red, determinista) — la garantía de no-regresión del fan-out:
       already_es=False  → SIGUE llamando translate_to_es (camino fan-out intacto).
       already_es=True   → NO llama translate_to_es; es_query = el tema tal cual.
  B) LIVE (red + Gemini, lo que confirmó el lab) — corre si hay conectividad/API; si falla la
     infra reporta SKIP (no rompe el bloque A).
       · Pennhurst → VACIO: ASERCIÓN dura. El juez tira todo (es un hueco ES real, 9/9 dropped
         en el lab); reproducible mientras no exista video ES relevante.
       · Pacientes 1900s → SATURADO: PROBE informativo, NO aserción. El label depende de que el
         scrape de scrapetube SURFACEE el video pesado "La Castañeda" (246k); scrapetube devuelve
         conjuntos VARIABLES por llamada (el lab tuvo cands=5 con La Castañeda; corridas posteriores
         dan cands=4-6 sin él → HUECO/DISPUTADO/VACIO). El fix es idéntico al prototipo del lab
         (list+juez, sin translate); la no-reproducibilidad es varianza del scrape, no del código.
         El probe imprime el label real + si La Castañeda apareció (auditable), sin romper el test.

Correr:  python -X utf8 test_chat52_already_es.py
         SKIP_LIVE=1 python -X utf8 test_chat52_already_es.py   (solo el bloque UNIT)
"""
from __future__ import annotations

import os
import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import script_engine.subtopic_measurer as sm
from script_engine.subtopic_measurer import _measure_es

_fails: list[str] = []


def check(cond: bool, msg: str):
    print(("  ✓ " if cond else "  ✗ ") + msg)
    if not cond:
        _fails.append(msg)


# ════════════════════════════════════════════════════════════════════════
#  A) UNIT — branching de already_es, SIN red (determinista, garantía fan-out)
# ════════════════════════════════════════════════════════════════════════
def test_unit_branching():
    print("\n[UNIT] already_es controla SOLO el translate (resto idéntico)")

    calls = {"translate": 0, "list_q": [], "filter_entity": []}

    def fake_translate(q):
        calls["translate"] += 1
        return {"es_query": f"TRADUCIDO::{q}", "es_aliases": ["alias1"]}

    def fake_list(es_query):
        calls["list_q"].append(es_query)
        return [{"title": "vid", "views": 10, "months": 2}]

    def fake_filter(entity, cands, aliases=None):
        calls["filter_entity"].append(entity)
        return cands  # todos relevantes

    orig = (sm.translate_to_es, sm.list_spanish_candidates, sm.filter_relevant)
    sm.translate_to_es, sm.list_spanish_candidates, sm.filter_relevant = (
        fake_translate, fake_list, fake_filter)
    try:
        # already_es=True → NO traduce, es_query == input crudo
        r_es = _measure_es("Horrores del Asilo Pennhurst", already_es=True)
        check(calls["translate"] == 0, "already_es=True NO llama translate_to_es")
        check(r_es.get("es_query") == "Horrores del Asilo Pennhurst",
              f"already_es=True usa el tema tal cual (es_query={r_es.get('es_query')!r})")
        check(calls["list_q"] == ["Horrores del Asilo Pennhurst"],
              "scrape ES corre sobre la query ES cruda")
        check(calls["filter_entity"] == ["Horrores del Asilo Pennhurst"],
              "el juez juzga contra el tema ES (entity=search_query)")

        # reset
        calls["translate"] = 0
        calls["list_q"].clear()
        calls["filter_entity"].clear()

        # already_es=False (default fan-out) → SÍ traduce, comportamiento intacto
        r_en = _measure_es("Chernobyl disaster")
        check(calls["translate"] == 1, "already_es=False (default) SÍ llama translate_to_es")
        check(r_en.get("es_query") == "TRADUCIDO::Chernobyl disaster",
              f"fan-out usa la grafía ES traducida (es_query={r_en.get('es_query')!r})")
        check(calls["list_q"] == ["TRADUCIDO::Chernobyl disaster"],
              "fan-out scrapea sobre la query traducida")

        # shape de salida idéntico en ambos caminos (no rompe al caller)
        for r in (r_es, r_en):
            check(all(k in r for k in ("label", "saturation", "heaviest", "ontopic_count",
                                       "es_query", "n_cands_es", "query_fallback", "source")),
                  f"shape de salida completo ({r.get('es_query')!r})")
    finally:
        sm.translate_to_es, sm.list_spanish_candidates, sm.filter_relevant = orig


# ════════════════════════════════════════════════════════════════════════
#  B) LIVE — los dos casos que confirmó el lab (red + Gemini)
# ════════════════════════════════════════════════════════════════════════
def _run_live(topic: str):
    """Devuelve (r|None, skip_reason|None)."""
    try:
        r = _measure_es(topic, already_es=True)
    except Exception as e:
        return None, f"infra falló ({str(e)[:80]})"
    if r.get("label") == "ERROR":
        return None, f"ES_ERROR ({r.get('error')})"
    h = r.get("heaviest") or {}
    print(f"     '{topic}' → {r.get('label')} (sat={(r.get('saturation') or 0):,.0f} "
          f"kept={r.get('ontopic_count')} cands={r.get('n_cands_es')} "
          f"top={(h.get('title') or '')[:50]!r})")
    return r, None


def test_live_cases():
    print("\n[LIVE] casos reales del lab (red + juez Gemini)")

    # Pennhurst → VACIO: aserción dura (hueco ES real; el juez tira los falsos de las anclas).
    r, skip = _run_live("Horrores del Asilo Pennhurst")
    if skip:
        print(f"  ⚠ SKIP Pennhurst: {skip}")
    else:
        check(r.get("label") == "VACIO",
              f"Pennhurst → VACIO (el juez tira los falsos que las anclas pescaban); "
              f"obtuvo {r.get('label')}")

    # Pacientes 1900s → SATURADO: PROBE informativo (depende del scrape; ver docstring).
    r, skip = _run_live("Pacientes psiquiátricos 1900s")
    if skip:
        print(f"  ⚠ SKIP Pacientes: {skip}")
    elif r.get("label") == "SATURADO":
        print("  ✓ Pacientes → SATURADO (el scrape surfaceó La Castañeda 246k, como el lab)")
    else:
        h = r.get("heaviest") or {}
        cast = "La Castañeda" in (h.get("title") or "")
        print(f"  ℹ PROBE Pacientes: lab=SATURADO(246k), aquí={r.get('label')}. "
              f"La Castañeda en el scrape: {'sí' if cast else 'NO'} → varianza de scrapetube "
              f"(no del fix; lógica idéntica al prototipo del lab). NO cuenta como fallo.")


if __name__ == "__main__":
    test_unit_branching()
    if os.environ.get("SKIP_LIVE"):
        print("\n[LIVE] SKIPPED (SKIP_LIVE set)")
    else:
        test_live_cases()

    print("\n" + ("=" * 60))
    if _fails:
        print(f"FALLOS: {len(_fails)}")
        for f in _fails:
            print(f"  - {f}")
        sys.exit(1)
    print("TODO OK")
