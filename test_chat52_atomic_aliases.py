"""
test_chat52_atomic_aliases.py — BLOQUE 3: el juez atómico (already_es=True) ahora recibe aliases ES.

BUG: en el atómico aliases=[] siempre → filter_relevant decidía sin aliases (el fan-out sí los pasa).
FIX: en la rama already_es, pedir translate_to_es SOLO por los es_aliases (NO reescribir la query:
Q2 lab, se mancha el scrape). es_query sigue siendo el tema crudo → la búsqueda ES no cambia, solo
el juez gana recall. Si translate falla → aliases=[] y NO rompe.

La red over-narrow queda no-op en atómico POR DISEÑO (entity==search_query → la guarda
`entity != search_query` es False) → eso NO se toca, se documenta.

Determinista, SIN red (mockea translate_to_es / list_spanish_candidates / filter_relevant).
Correr:  python -X utf8 test_chat52_atomic_aliases.py
"""
from __future__ import annotations

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


def _patch(translate, capture):
    """Instala mocks; capture['q'] = query scrapeada, capture['aliases'] = aliases pasados al juez."""
    sm.translate_to_es = translate
    sm.list_spanish_candidates = lambda q: (capture.__setitem__("q", q),
                                            [{"title": "v", "views": 1, "months": 1}])[1]

    def fake_filter(entity, cands, aliases=None):
        capture["entity"] = entity
        capture["aliases"] = aliases
        return cands
    sm.filter_relevant = fake_filter


def test_aliases_pasan_al_juez():
    print("\n[B3] already_es=True: pide aliases SIN reescribir la query")
    orig = (sm.translate_to_es, sm.list_spanish_candidates, sm.filter_relevant)
    cap: dict = {}
    try:
        _patch(lambda q: {"es_query": "QUERY_REESCRITA_MALA", "es_aliases": ["La Castañeda", "manicomio"]}, cap)
        r = _measure_es("Pacientes psiquiátricos 1900s", already_es=True)
        check(cap.get("q") == "Pacientes psiquiátricos 1900s",
              f"la búsqueda ES usa el tema CRUDO, no la reescritura (scrapeó {cap.get('q')!r})")
        check(r.get("es_query") == "Pacientes psiquiátricos 1900s",
              "es_query devuelto = el tema crudo (no la reescritura)")
        check(cap.get("aliases") == ["La Castañeda", "manicomio"],
              f"el juez RECIBE los aliases ES (obtuvo {cap.get('aliases')!r})")
        check(cap.get("entity") == "Pacientes psiquiátricos 1900s",
              "el juez juzga contra el tema ES (entity = search_query)")
    finally:
        sm.translate_to_es, sm.list_spanish_candidates, sm.filter_relevant = orig


def test_translate_falla_no_rompe():
    print("\n[B3] already_es=True con translate caído → aliases=[] y NO rompe")
    orig = (sm.translate_to_es, sm.list_spanish_candidates, sm.filter_relevant)
    cap: dict = {}

    def boom(q):
        raise RuntimeError("Gemini 503")
    try:
        _patch(boom, cap)
        r = _measure_es("Horrores del Asilo Pennhurst", already_es=True)
        check(cap.get("aliases") == [], f"aliases=[] cuando translate falla (obtuvo {cap.get('aliases')!r})")
        check(cap.get("q") == "Horrores del Asilo Pennhurst", "la búsqueda ES igual corre con el tema crudo")
        check(r.get("label") in ("VACIO", "HUECO", "DISPUTADO", "SATURADO"),
              f"devuelve un label válido (no ERROR) pese al translate caído: {r.get('label')}")
    finally:
        sm.translate_to_es, sm.list_spanish_candidates, sm.filter_relevant = orig


def test_fanout_no_cambia():
    print("\n[B3] already_es=False (fan-out): SIGUE reescribiendo la query (no-regresión)")
    orig = (sm.translate_to_es, sm.list_spanish_candidates, sm.filter_relevant)
    cap: dict = {}
    try:
        _patch(lambda q: {"es_query": "TRADUCIDO", "es_aliases": ["al1"]}, cap)
        _measure_es("Chernobyl disaster")  # default already_es=False
        check(cap.get("q") == "TRADUCIDO", "fan-out scrapea la query TRADUCIDA (intacto)")
        check(cap.get("aliases") == ["al1"], "fan-out pasa aliases al juez (intacto)")
    finally:
        sm.translate_to_es, sm.list_spanish_candidates, sm.filter_relevant = orig


if __name__ == "__main__":
    test_aliases_pasan_al_juez()
    test_translate_falla_no_rompe()
    test_fanout_no_cambia()

    print("\n" + ("=" * 60))
    if _fails:
        print(f"FALLOS: {len(_fails)}")
        for f in _fails:
            print(f"  - {f}")
        sys.exit(1)
    print("TODO OK")
