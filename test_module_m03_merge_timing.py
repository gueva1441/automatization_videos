"""
test_module_m03_merge_timing.py — timing-aware anchor merge (chat 54).

Casos (handoff §2):
  (a) dos anchors a gap < piso → fusiona el segundo (el anterior absorbe el tiempo)
  (b) anchors espaciados → no fusiona (count y anchors intactos)
  (c) la fusión respeta la guarda de mínimo (no baja de MIN)
  (d) el matcher usado == el de _compute_durations_from_anchors (mismo objeto compartido)

Corre con pytest o directo:  python test_module_m03_merge_timing.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "script_engine"))

import anchor_timing
import fase2b
import m03_visual as m

GAP = m.MIN_ANCHOR_GAP_SEC  # 2.0


def _words(*pairs) -> list[dict]:
    """pairs: (word, start) → [{word,start,end}] con end = siguiente start (o +0.4)."""
    out = []
    for i, (w, s) in enumerate(pairs):
        e = pairs[i + 1][1] if i + 1 < len(pairs) else s + 0.4
        out.append({"word": w, "start": float(s), "end": float(e)})
    return out


def _flux_plan(*anchors) -> dict:
    return {"anchors": [{"anchor": a, "pos": i, "end": i + 1} for i, a in enumerate(anchors)]}


def _veo_plan(*supp_anchors) -> dict:
    return {
        "veo_anchor": {"anchor": "ZONA veo intro", "pos": 0, "end": 1},
        "supplementals": [{"anchor": a, "pos": i, "end": i + 1} for i, a in enumerate(supp_anchors)],
    }


def test_a_fusiona_anchor_apretado():
    """Gap < piso → descarta el segundo; el primero absorbe su tiempo."""
    words = _words(("alpha", 0.0), ("bravo", 0.5), ("charlie", 3.0))
    plan = _flux_plan("alpha", "bravo", "charlie")
    out, dropped = m._reconcile_anchor_timing(plan, "flux", words, min_count=2, cap_number=1)
    survivors = [x["anchor"] for x in out["anchors"]]
    assert dropped == 1, f"esperaba 1 fusión, dio {dropped}"
    assert survivors == ["alpha", "charlie"], survivors   # 'bravo' (gap 0.5 < 2.0) fuera


def test_a_cascada_multiple():
    """Varios apretados seguidos → el primero los absorbe a todos."""
    words = _words(("alpha", 0.0), ("bravo", 0.5), ("charlie", 0.6), ("delta", 4.0))
    plan = _flux_plan("alpha", "bravo", "charlie", "delta")
    out, dropped = m._reconcile_anchor_timing(plan, "flux", words, min_count=2, cap_number=1)
    assert dropped == 2
    assert [x["anchor"] for x in out["anchors"]] == ["alpha", "delta"]


def test_b_espaciados_no_fusiona():
    """Anchors bien espaciados → cero fusiones, anchors idénticos."""
    words = _words(("alpha", 0.0), ("bravo", 2.5), ("charlie", 5.0))
    plan = _flux_plan("alpha", "bravo", "charlie")
    before = [x["anchor"] for x in plan["anchors"]]
    out, dropped = m._reconcile_anchor_timing(plan, "flux", words, min_count=2, cap_number=1)
    assert dropped == 0
    assert [x["anchor"] for x in out["anchors"]] == before


def test_c_guarda_de_minimo():
    """Aunque haya gaps apretados, NO baja del mínimo."""
    # 4 items, todos apretados; min_count=4 → no debe fusionar ninguno.
    words = _words(("a", 0.0), ("b", 0.3), ("c", 0.6), ("d", 0.9))
    plan = _flux_plan("a", "b", "c", "d")
    out, dropped = m._reconcile_anchor_timing(plan, "flux", words, min_count=4, cap_number=1)
    assert dropped == 0
    assert len(out["anchors"]) == 4
    # min_count=3 → fusiona hasta quedar exactamente en 3, no menos.
    plan2 = _flux_plan("a", "b", "c", "d")
    out2, dropped2 = m._reconcile_anchor_timing(plan2, "flux", words, min_count=3, cap_number=1)
    assert len(out2["anchors"]) == 3
    assert dropped2 == 1


def test_c_veo_path_y_veo_anchor_intacto():
    """La fusión corre también para veo (supplementals); el veo_anchor NO se toca."""
    words = _words(("uno", 0.0), ("dos", 0.4), ("tres", 5.0), ("cuatro", 10.0),
                   ("cinco", 15.0))
    plan = _veo_plan("uno", "dos", "tres", "cuatro", "cinco")
    out, dropped = m._reconcile_anchor_timing(plan, "veo", words, min_count=4, cap_number=7)
    assert dropped == 1                                  # 'dos' (gap 0.4) fuera
    assert [x["anchor"] for x in out["supplementals"]] == ["uno", "tres", "cuatro", "cinco"]
    assert out["veo_anchor"]["anchor"] == "ZONA veo intro"   # intacto


def test_d_matcher_compartido():
    """m03, fase2b y anchor_timing usan EL MISMO objeto compute_anchor_starts."""
    assert m.compute_anchor_starts is anchor_timing.compute_anchor_starts
    assert fase2b.compute_anchor_starts is anchor_timing.compute_anchor_starts
    # Funcional: los starts del matcher coinciden con lo que fase2b reparte (offset=0).
    words = _words(("alpha", 0.0), ("bravo", 3.0), ("charlie", 6.0))
    import json, tempfile, os
    fd, path = tempfile.mkstemp(suffix="_timestamps.json")
    os.close(fd)
    Path(path).write_text(json.dumps(words), encoding="utf-8")
    try:
        durations = fase2b._compute_durations_from_anchors(
            ["alpha", "bravo", "charlie"], Path(path), total_duration=9.0)
        starts = anchor_timing.compute_anchor_starts(["alpha", "bravo", "charlie"], words)
        # duration[0] = starts[1]-starts[0], duration[1] = starts[2]-starts[1] (offset=0)
        assert durations is not None and starts is not None
        assert abs(durations[0] - (starts[1] - starts[0])) < 1e-9
        assert abs(durations[1] - (starts[2] - starts[1])) < 1e-9
    finally:
        os.unlink(path)


def test_no_op_si_matcher_falla():
    """Si un anchor no matchea → no toca nada (fallback seguro)."""
    words = _words(("alpha", 0.0), ("bravo", 0.4))
    plan = _flux_plan("alpha", "zzz inexistente")
    out, dropped = m._reconcile_anchor_timing(plan, "flux", words, min_count=1, cap_number=1)
    assert dropped == 0
    assert len(out["anchors"]) == 2


def _run_all():
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print(f"  OK  {fn.__name__}")
    print(f"\n{len(fns)}/{len(fns)} tests OK")


if __name__ == "__main__":
    _run_all()
