"""
test_chat52_dropped_cap.py — BLOQUE 5: loggear los dropped_by_cap (el cap K=8 deja de tirar oro sin rastro).

BUG: capped = en_passing[:K] descartaba subtemas que pasaron EN (rankeados #K+1+) ANTES de medir ES,
sin dejar registro → un subtema con nicho ES VACIO real se perdía en silencio.

FIX (cero cambio de comportamiento, solo observabilidad):
  - _apply_fanout_cap(en_passing, k) → (capped, dropped_subtemas). El cap NO cambia (sigue top-K);
    dropped_subtemas = los >K con {nombre_en, search_query_en, top_rel_views}.
  - _persist_dropped_by_cap(...) → append JSONL en _steps/ (sobrevive aunque el contenedor emita 0 seeds).

Determinista, SIN red. Correr:  python -X utf8 test_chat52_dropped_cap.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import niche_discoverer as nd
from niche_discoverer import _apply_fanout_cap, _persist_dropped_by_cap

_fails: list[str] = []


def check(cond: bool, msg: str):
    print(("  ✓ " if cond else "  ✗ ") + msg)
    if not cond:
        _fails.append(msg)


def _en_passing(n: int) -> list:
    """n subtemas (subj, en) con views decrecientes (ya 'ordenados' como en el fan-out)."""
    return [({"nombre_en": f"Sujeto {i}", "search_query_en": f"query {i}", "angle_en": f"a{i}"},
             {"top_rel_views": (n - i) * 100_000})
            for i in range(n)]


def test_cap_no_cambia_y_loguea_resto():
    print("\n[B5] >K subtemas pasando EN → capped = top-K (sin cambio), resto logueado con nombre+views")
    k = nd.SUBTEMA_FANOUT_CAP_K   # 8
    en_passing = _en_passing(k + 3)   # 11 → 8 capped, 3 dropped
    capped, dropped = _apply_fanout_cap(en_passing, k)

    check(len(capped) == k, f"capped sigue siendo top-{k} (sin cambio funcional); obtuvo {len(capped)}")
    check(len(dropped) == 3, f"los >K quedan en dropped_subtemas; obtuvo {len(dropped)}")
    # el set capeado son los de MÁS views (los primeros, ya ordenados)
    capped_names = {s["nombre_en"] for s, _ in capped}
    check("Sujeto 0" in capped_names and "Sujeto 7" in capped_names, "capped = los de más demanda EN")
    # los dropped traen nombre + query + views
    d0 = dropped[0]
    check(set(d0) == {"nombre_en", "search_query_en", "top_rel_views"},
          f"cada dropped trae nombre_en/search_query_en/top_rel_views; obtuvo {set(d0)}")
    check(d0["nombre_en"] == "Sujeto 8" and d0["top_rel_views"] == 3 * 100_000,
          "el primer dropped es el rankeado #K+1 con sus views reales")


def test_cap_exacto_K_no_dropea():
    print("\n[B5] exactamente K subtemas → 0 dropped (no inventa rastro)")
    k = nd.SUBTEMA_FANOUT_CAP_K
    capped, dropped = _apply_fanout_cap(_en_passing(k), k)
    check(len(capped) == k and dropped == [], "K exactos → capped=K, dropped vacío")


def test_persist_jsonl(tmp_log: Path):
    print("\n[B5] _persist_dropped_by_cap → append JSONL en _steps/ (sobrevive a 0 seeds)")
    orig = nd.DROPPED_CAP_LOG
    nd.DROPPED_CAP_LOG = tmp_log
    try:
        dropped = [{"nombre_en": "Oro ES", "search_query_en": "oro es", "top_rel_views": 500_000}]
        _persist_dropped_by_cap("vidABC", "Contenedor Padre", dropped)
        _persist_dropped_by_cap("vidXYZ", "Otro Padre", [])   # vacío → NO escribe línea
        check(tmp_log.exists(), "crea el archivo _steps/ JSONL")
        lines = tmp_log.read_text(encoding="utf-8").strip().splitlines()
        check(len(lines) == 1, f"solo 1 línea (la vacía no escribe); obtuvo {len(lines)}")
        rec = json.loads(lines[0])
        check(rec["parent_video_id"] == "vidABC" and rec["dropped"][0]["nombre_en"] == "Oro ES",
              "la línea trae parent + la lista de dropped")
        check("at" in rec, "incluye timestamp 'at'")
    finally:
        nd.DROPPED_CAP_LOG = orig


def test_persist_no_lanza():
    print("\n[B5] persistencia tolerante a fallo de disco (nunca rompe el discovery)")
    orig = nd.DROPPED_CAP_LOG
    # ruta inválida (un archivo como 'directorio' padre) → mkdir/​open fallan, pero no debe lanzar
    nd.DROPPED_CAP_LOG = Path(__file__) / "no" / "puede" / "x.jsonl"
    try:
        _persist_dropped_by_cap("v", "p", [{"nombre_en": "x", "search_query_en": "q", "top_rel_views": 1}])
        check(True, "no lanza aunque el disco falle (solo imprime el aviso)")
    except Exception as e:
        check(False, f"NO debía lanzar; lanzó {e}")
    finally:
        nd.DROPPED_CAP_LOG = orig


if __name__ == "__main__":
    test_cap_no_cambia_y_loguea_resto()
    test_cap_exacto_K_no_dropea()
    tmp = Path(__file__).parent / "_tmp_dropped_cap_test.jsonl"
    if tmp.exists():
        tmp.unlink()
    try:
        test_persist_jsonl(tmp)
    finally:
        if tmp.exists():
            tmp.unlink()
    test_persist_no_lanza()

    print("\n" + ("=" * 60))
    if _fails:
        print(f"FALLOS: {len(_fails)}")
        for f in _fails:
            print(f"  - {f}")
        sys.exit(1)
    print("TODO OK")
