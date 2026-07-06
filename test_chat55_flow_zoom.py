"""
test_chat55_flow_zoom.py — Regresión del gate de zoom v3 (Camino B, chat 55).

Camino A (gate semántico del LLM) MURIÓ: el LLM ya no ve zoom (inventario vuelve a 3).
El zoom lo inyecta un gate por IMAGEN: depth_probe (geometría c-b) + zoom_judge (visión).

Chequeos (todos puros, sin GPU ni Gemini):
  1. No-regresión: inventario LLM = 3 movimientos; _build_options da los params v12.
  2. Dirección zoom a nivel animador: zoom_in=+intensity, zoom_out=-intensity (el gate
     inyecta zoom_in; el branch y el fix de dirección DEBEN seguir vivos).
  3. gate_zoom (pre-filtro geométrico): umbral c-b ≥ 0.15.
  4. rank_promotions: tope por cap + orden por c-b descendente.
  5. Gate end-to-end (puro, fixtures reales del lab): las promovidas de Charleston son
     exactamente {ch02_img_14, ch03_img_08, ch04_img_02, ch04_img_05}.
"""
from __future__ import annotations

import sys

from flow_config import VALID_MOVEMENTS
from flow_profiles import FlowSpec
from script_engine.parallax_animator_v2 import _build_options
from script_engine.depth_probe import gate_zoom, rank_promotions, DEPTH_ZOOM_CB_MIN
from script_engine.zoom_judge import promotes_to_zoom

DUR = 7.0  # = _DURATION_REFERENCE_S → sin escalado de intensity


def _spec(movement, intensity=0.95, steady=0.3) -> FlowSpec:
    return FlowSpec(movement=movement, intensity=intensity, steady=steady, dof=True, reasoning="t")


# ─────────────────────────────────────────────────────────────────
def check1_no_regresion():
    ok, notes = True, []
    expected = {"horizontal", "vertical", "orbital"}
    if VALID_MOVEMENTS != expected:
        ok = False; notes.append(f"VALID_MOVEMENTS={sorted(VALID_MOVEMENTS)} != {sorted(expected)} (LLM debe ver 3)")
    else:
        notes.append(f"VALID_MOVEMENTS = {sorted(VALID_MOVEMENTS)} ✓ (LLM vuelve a 3, sin zoom)")
    for mv in ("horizontal", "vertical"):
        o = _build_options(_spec(mv), DUR)
        if o.get("isometric") != 0.6 or o.get("steady") != 0.3 or o.get("intensity") != 0.95:
            ok = False; notes.append(f"{mv} REGRESIÓN: {o}")
        else:
            notes.append(f"{mv}: isometric=0.6 steady=0.3 intensity=0.95 ✓")
    o = _build_options(_spec("orbital"), DUR)
    if o.get("depth") != 0.9 or "isometric" in o:
        ok = False; notes.append(f"orbital REGRESIÓN: {o}")
    else:
        notes.append("orbital: depth=0.9 ✓")
    return ok, "\n".join("    " + n for n in notes)


def check2_zoom_direction():
    ok, notes = True, []
    o_in = _build_options(_spec("zoom_in"), DUR)
    o_out = _build_options(_spec("zoom_out"), DUR)
    if o_in.get("intensity") != 0.95 or any(k in o_in for k in ("isometric", "depth", "steady")):
        ok = False; notes.append(f"zoom_in MAL: {o_in}")
    else:
        notes.append("zoom_in: intensity=+0.95 (acerca) ✓")
    if o_out.get("intensity") != -0.95 or any(k in o_out for k in ("isometric", "depth", "steady")):
        ok = False; notes.append(f"zoom_out MAL: {o_out}")
    else:
        notes.append("zoom_out: intensity=-0.95 (aleja) ✓ — branch + fix de dirección vivos")
    return ok, "\n".join("    " + n for n in notes)


def check3_gate_zoom_threshold():
    ok, notes = True, []
    cases = [
        ("img_08 (c-b 0.258)", {"center_minus_border": 0.258}, True),
        ("img_05_05 (c-b 0.177)", {"center_minus_border": 0.177}, True),
        ("umbral exacto (0.15)", {"center_minus_border": 0.15}, True),
        ("just below (0.149)", {"center_minus_border": 0.149}, False),
        ("muro plano (c-b -0.008)", {"center_minus_border": -0.008}, False),
        ("sin métrica", {}, False),
    ]
    for label, m, want in cases:
        got = gate_zoom(m)
        if got != want:
            ok = False; notes.append(f"✗ {label}: got={got} want={want}")
        else:
            notes.append(f"{label}: {got} ✓")
    notes.append(f"(DEPTH_ZOOM_CB_MIN = {DEPTH_ZOOM_CB_MIN})")
    return ok, "\n".join("    " + n for n in notes)


def check4_rank_promotions():
    ok, notes = True, []
    # tope por cap: 3 candidatas → top-2 por c-b
    scored = [("a", 0.21), ("b", 0.182), ("c", 0.30)]
    r = rank_promotions(scored, 2)
    if r != ["c", "a"]:
        ok = False; notes.append(f"✗ orden/tope: {r} (esperaba ['c','a'])")
    else:
        notes.append("tope=2 + orden por c-b desc → ['c','a'] ✓")
    if rank_promotions([("x", 0.5)], 2) != ["x"]:
        ok = False; notes.append("✗ menos candidatas que el tope")
    else:
        notes.append("menos candidatas que el tope → devuelve las que hay ✓")
    if rank_promotions([], 2) != []:
        ok = False; notes.append("✗ vacío")
    else:
        notes.append("sin candidatas → [] ✓")
    return ok, "\n".join("    " + n for n in notes)


def check5_gate_end_to_end():
    """Réplica pura de _apply_zoom_gate con los valores REALES del lab chat 55.
    Verifica que las promovidas de Charleston son exactamente las 4 esperadas."""
    ok, notes = True, []
    # (imagen, cap, c-b real, veredicto de visión real del lab)
    fixtures = [
        ("ch04_img_06", "ch04", 0.383, "cara_closeup"),
        ("ch02_img_14", "ch02", 0.355, "sujeto_con_fondo"),
        ("ch03_img_08", "ch03", 0.258, "sujeto_con_fondo"),
        ("ch04_img_02", "ch04", 0.210, "sujeto_con_fondo"),
        ("ch04_img_05", "ch04", 0.182, "sujeto_con_fondo"),
        ("ch05_img_05", "ch05", 0.177, "superficie_plana"),
        ("ch06_img_08", "ch06", -0.008, "sujeto_con_fondo"),  # geometría lo descarta
    ]
    # 1. pre-filtro geométrico
    candidates = [(n, cap, cb, v) for (n, cap, cb, v) in fixtures
                  if gate_zoom({"center_minus_border": cb})]
    # 2. visión + 3. tope/orden por cap
    promoted = set()
    by_cap: dict[str, list[tuple[str, float]]] = {}
    for n, cap, cb, v in candidates:
        if promotes_to_zoom({"categoria": v}):
            by_cap.setdefault(cap, []).append((n, cb))
    for cap, scored in by_cap.items():
        promoted.update(rank_promotions(scored, 2))

    expected = {"ch02_img_14", "ch03_img_08", "ch04_img_02", "ch04_img_05"}
    if promoted != expected:
        ok = False
        notes.append(f"✗ promovidas={sorted(promoted)} != esperadas={sorted(expected)}")
    else:
        notes.append(f"promovidas = {sorted(promoted)} ✓ (las 4 esperadas)")
    notes.append("  cara (img_06) excluida por visión ✓ · fachada (img_05_05) excluida ✓ · "
                 "muro (img_08 c-b<0) excluido por geometría ✓")
    # ch04 tenía 2 candidatas sujeto (img_02, img_05) → tope=2 las toma a ambas
    notes.append(f"  ch04: {sorted(rank_promotions(by_cap['ch04'], 2))} (tope 2 respetado) ✓")
    return ok, "\n".join("    " + n for n in notes)


def check6_flow_specs_cache():
    """Si flow_specs.json existe y cubre los caps → REUSA, NO llama al LLM."""
    import tempfile
    from pathlib import Path
    import fase2b

    ok, notes = True, []
    tmp = Path(tempfile.mkdtemp())
    cache = tmp / "flow_specs.json"
    # HANDOFF_140b (C2): cache nuevo cap→LISTA `specs` (una por imagen). ch02 anima
    # 1 imagen (asset_paths abajo) → lista de largo 1.
    cache.write_text(
        '{"video_id":"x","chapters":{'
        '"ch01":{"reuse_baked":true},'
        '"ch02":{"specs":[{"movement":"horizontal","intensity":0.85,"steady":0.0,"dof":false,"reasoning":"v2"}]}}}',
        encoding="utf-8",
    )

    # Plans mínimos: ch01 veo+supps (reuse), ch02 flux
    P = fase2b.ChapterPlan
    plan_ch01 = P(chapter_id="ch01", engine="veo", audio_path=tmp / "a.mp3",
                  audio_duration=10.0, asset_paths=[tmp / "v.mp4"], timestamps_path=None,
                  is_first=True, art_profile=None, supplemental_paths=[tmp / "s1.png"])
    plan_ch02 = P(chapter_id="ch02", engine="flux", audio_path=tmp / "b.mp3",
                  audio_duration=20.0, asset_paths=[tmp / "ch02_img_01.png"], timestamps_path=None,
                  is_first=False, art_profile=None)
    plans = [plan_ch01, plan_ch02]

    orig_path = fase2b._flow_specs_cache_path
    orig_dispatch = fase2b._dispatch_flow_specs
    called = {"llm": False}
    def _boom(_plans, _vid=None):   # C2: firma nueva (plans, video_id)
        called["llm"] = True
        raise AssertionError("NO debía llamarse al LLM con cache presente")
    try:
        fase2b._flow_specs_cache_path = lambda vid: cache
        fase2b._dispatch_flow_specs = _boom
        specs, reuse = fase2b._resolve_flow_specs(plans, "x")
    finally:
        fase2b._flow_specs_cache_path = orig_path
        fase2b._dispatch_flow_specs = orig_dispatch

    if called["llm"]:
        ok = False; notes.append("✗ se llamó al LLM pese al cache")
    else:
        notes.append("cache presente → NO se llamó al LLM ✓")
    if ("ch02" not in specs or not isinstance(specs["ch02"], list)
            or not specs["ch02"] or specs["ch02"][0]["movement"] != "horizontal"):
        ok = False; notes.append(f"✗ spec ch02 mal recuperado: {specs.get('ch02')}")
    else:
        notes.append("ch02 spec[list] recuperado del cache (horizontal) ✓")
    if "ch01" not in reuse:
        ok = False; notes.append(f"✗ ch01 no marcado reuse_baked: {reuse}")
    else:
        notes.append("ch01 reuse_baked ✓ (reusa clip v2, no re-anima)")
    return ok, "\n".join("    " + n for n in notes)


def main() -> int:
    print("=" * 72)
    print("  REGRESIÓN GATE DE ZOOM v3 (Camino B, chat 55) — depth + visión por imagen")
    print("=" * 72)
    checks = [
        ("1·No-regresión (LLM=3 movs)", check1_no_regresion),
        ("2·Dirección zoom (animador)", check2_zoom_direction),
        ("3·gate_zoom pre-filtro c-b", check3_gate_zoom_threshold),
        ("4·rank_promotions (tope+orden)", check4_rank_promotions),
        ("5·Gate end-to-end (fixtures lab)", check5_gate_end_to_end),
        ("6·Cache flow_specs (no LLM)", check6_flow_specs_cache),
    ]
    results = {}
    for name, fn in checks:
        print("─" * 72); print(f"CHEQUEO {name}")
        ok, detail = fn(); print(detail)
        results[name] = ok
        print(f"  → {'PASS ✅' if ok else 'FAIL ❌'}\n")
    print("=" * 72); print("  RESUMEN")
    for k, v in results.items():
        print(f"    {'PASS ✅' if v else 'FAIL ❌'}  {k}")
    print("=" * 72)
    return 1 if any(v is False for v in results.values()) else 0


if __name__ == "__main__":
    sys.exit(main())
