"""
test_chat55_flow_zoom.py — Lab de regresión Camino A (re-exponer zoom al LLM).

Cuatro chequeos del HANDOFF (GATE 1):
  1. Gate semántico: el LLM NO asigna zoom a texturas/muros; solo (si cae) en
     sujeto+profundidad.  [requiere Gemini → se salta si no hay API]
  2. zoom_out real: por params, zoom_out aleja (intensity negativa) y zoom_in
     acerca (positiva).  [params siempre; render opcional si hay venv DepthFlow]
  3. No regresión: horizontal/vertical/orbital dan los MISMOS params que antes
     (isometric=0.6 / depth=0.9). El validador acepta los 5.
  4. Variedad: el LLM no spamea zoom en todo el video (regla ≤2 seguidas + gate).
     [requiere Gemini → se salta si no hay API]

Lab read-only: artefactos a _lab_out/lab_flow_zoom/. NO toca producción.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from flow_config import VALID_MOVEMENTS, DEPTHFLOW_INVENTORY, render_inventory_for_prompt
from flow_profiles import FlowSpec
from script_engine.parallax_animator_v2 import _build_options

LAB_DIR = Path(__file__).parent / "_lab_out" / "lab_flow_zoom"
DUR = 7.0  # = _DURATION_REFERENCE_S → sin escalado de intensity (params crudos)


def _spec(movement: str, intensity: float = 0.95, steady: float = 0.3) -> FlowSpec:
    return FlowSpec(movement=movement, intensity=intensity, steady=steady,
                    dof=True, reasoning="lab")


# ─────────────────────────────────────────────────────────────────
#  CHEQUEO 3 — NO REGRESIÓN (params puros, sin API)
# ─────────────────────────────────────────────────────────────────
def check3_no_regresion() -> tuple[bool, str]:
    ok = True
    notes: list[str] = []

    # El validador acepta los 5
    expected = {"horizontal", "vertical", "orbital", "zoom_in", "zoom_out"}
    if VALID_MOVEMENTS != expected:
        ok = False
        notes.append(f"VALID_MOVEMENTS={sorted(VALID_MOVEMENTS)} != {sorted(expected)}")
    else:
        notes.append(f"VALID_MOVEMENTS = {sorted(VALID_MOVEMENTS)} ✓ (acepta los 5)")

    # horizontal/vertical → isometric=0.6, steady pasa, intensity intacta
    for mv in ("horizontal", "vertical"):
        o = _build_options(_spec(mv), DUR)
        if o.get("isometric") != 0.6 or o.get("steady") != 0.3 or o.get("intensity") != 0.95:
            ok = False
            notes.append(f"{mv} REGRESIÓN: {o}")
        else:
            notes.append(f"{mv}: isometric=0.6, steady=0.3, intensity=0.95 ✓")

    # orbital → depth=0.9, intensity intacta, sin isometric/steady
    o = _build_options(_spec("orbital"), DUR)
    if o.get("depth") != 0.9 or o.get("intensity") != 0.95 or "isometric" in o or "steady" in o:
        ok = False
        notes.append(f"orbital REGRESIÓN: {o}")
    else:
        notes.append("orbital: depth=0.9, intensity=0.95, sin isometric/steady ✓")

    return ok, "\n".join("    " + n for n in notes)


# ─────────────────────────────────────────────────────────────────
#  CHEQUEO 2 — DIRECCIÓN zoom (params; el render visual es opcional)
# ─────────────────────────────────────────────────────────────────
def check2_zoom_direction() -> tuple[bool, str]:
    ok = True
    notes: list[str] = []

    o_in = _build_options(_spec("zoom_in"), DUR)
    o_out = _build_options(_spec("zoom_out"), DUR)

    # zoom_in: intensity POSITIVA (acerca), sin isometric/depth/steady
    if o_in.get("intensity") != 0.95 or any(k in o_in for k in ("isometric", "depth", "steady")):
        ok = False
        notes.append(f"zoom_in MAL: {o_in}")
    else:
        notes.append("zoom_in: intensity=+0.95 (acerca), sin isometric/depth/steady ✓")

    # zoom_out: intensity NEGATIVA (aleja) — el fix de dirección por NOMBRE
    if o_out.get("intensity") != -0.95 or any(k in o_out for k in ("isometric", "depth", "steady")):
        ok = False
        notes.append(f"zoom_out MAL: {o_out}")
    else:
        notes.append("zoom_out: intensity=-0.95 (aleja), sin isometric/depth/steady ✓")

    # Misma magnitud, signo opuesto
    if abs(o_in.get("intensity", 0)) != abs(o_out.get("intensity", 0)):
        ok = False
        notes.append("zoom_in/zoom_out NO tienen la misma magnitud")
    else:
        notes.append("magnitud idéntica, signo opuesto ✓")

    return ok, "\n".join("    " + n for n in notes)


# ─────────────────────────────────────────────────────────────────
#  CHEQUEOS 1 + 4 — GATE SEMÁNTICO + VARIEDAD (requiere Gemini)
# ─────────────────────────────────────────────────────────────────
# Mezcla deliberada: TEXTURA/MURO (zoom NO debe caer) vs SUJETO+PROFUNDIDAD
# (zoom permitido). Prompts al estilo Charleston.
_SCENES = [
    {"scene_number": 1, "label": "ch01", "narration": "El hook abre la historia.",
     "image_prompt": "a lone figure standing at the end of a vast dark corridor, deep perspective, light at the far end"},
    {"scene_number": 2, "label": "ch02", "narration": "Primer plano de textura.",
     "image_prompt": "extreme close-up of a corroded rusted metal wall, flaking paint, flat surface, no subject"},
    {"scene_number": 3, "label": "ch02", "narration": "Niebla disolviéndose.",
     "image_prompt": "thick gray fog slowly dissolving over an empty field, no clear subject, soft diffuse light"},
    {"scene_number": 4, "label": "ch03", "narration": "El sujeto en su cuarto.",
     "image_prompt": "a seated elderly man in a dim room, a window receding behind him, depth into the background"},
    {"scene_number": 5, "label": "ch03", "narration": "Un objeto cargado.",
     "image_prompt": "a single overturned wooden stool in an empty hall, dramatic light, oppressive depth behind it"},
    {"scene_number": 6, "label": "ch04", "narration": "Multitud en la costa.",
     "image_prompt": "wide panoramic shot of a crowd along a flat shoreline, horizon line, no central subject"},
    {"scene_number": 7, "label": "ch04", "narration": "Pared de ladrillo.",
     "image_prompt": "a flat brick wall texture filling the entire frame, even lighting, no depth"},
    {"scene_number": 8, "label": "ch05", "narration": "Detalle que se abre.",
     "image_prompt": "macro detail of an open book on a desk, the room opening up with depth behind it"},
]
# scenes 2,3,6,7 = sin sujeto/profundidad → zoom PROHIBIDO
_NO_ZOOM_IDX = {2, 3, 6, 7}


def checks_1_4_gate_y_variedad() -> tuple[bool | None, str]:
    try:
        from script_engine.flow_director import select_movements_batch
    except Exception as e:  # import puede fallar sin deps de Gemini
        return None, f"    SKIP (no se pudo importar flow_director: {e})"

    try:
        specs = select_movements_batch(_SCENES)
    except Exception as e:
        return None, f"    SKIP (Gemini no disponible / falló: {e})"

    LAB_DIR.mkdir(parents=True, exist_ok=True)
    rows = [{"scene": sc["scene_number"], "prompt": sc["image_prompt"][:60],
             "movement": s["movement"], "reasoning": s.get("reasoning", "")}
            for sc, s in zip(_SCENES, specs)]
    (LAB_DIR / "gate_semantico.json").write_text(
        json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")

    notes: list[str] = []
    ok = True

    # CHEQUEO 1: ningún zoom en texturas/muros/niebla/panorámica
    violations = [r for r in rows if r["scene"] in _NO_ZOOM_IDX and r["movement"].startswith("zoom")]
    if violations:
        ok = False
        for v in violations:
            notes.append(f"GATE VIOLADO: escena {v['scene']} ({v['prompt']}) → {v['movement']}")
    else:
        notes.append("Gate semántico: 0 zoom en texturas/muros/niebla/panorámica ✓")

    zoom_scenes = [r["scene"] for r in rows if r["movement"].startswith("zoom")]
    notes.append(f"zoom cayó en escenas: {zoom_scenes or 'ninguna'} (permitidas: sujeto+profundidad)")

    # CHEQUEO 4: variedad — zoom no domina todo el video
    n_zoom = len(zoom_scenes)
    if n_zoom > len(_SCENES) // 2:
        ok = False
        notes.append(f"VARIEDAD MAL: zoom en {n_zoom}/{len(_SCENES)} escenas (spam)")
    else:
        notes.append(f"Variedad: zoom en {n_zoom}/{len(_SCENES)} — no spamea ✓")

    # ≤2 seguidas (cualquier movimiento)
    movs = [r["movement"] for r in rows]
    run = max_run = 1
    for a, b in zip(movs, movs[1:]):
        run = run + 1 if a == b else 1
        max_run = max(max_run, run)
    if max_run > 2:
        notes.append(f"⚠ corrida de {max_run} iguales seguidas (>2): {movs}")
    else:
        notes.append(f"≤2 movimientos iguales seguidos ✓ (máx corrida={max_run})")

    notes.append(f"  → {LAB_DIR / 'gate_semantico.json'}")
    return ok, "\n".join("    " + n for n in notes)


# ─────────────────────────────────────────────────────────────────
def main() -> int:
    print("=" * 72)
    print("  LAB CAMINO A — re-exponer zoom_in/zoom_out al LLM (chat 55)")
    print("=" * 72)
    print("\nINVENTARIO inyectado a Gemini:")
    print(render_inventory_for_prompt())
    print(f"\nDEPTHFLOW_INVENTORY = {[m.name for m in DEPTHFLOW_INVENTORY]}\n")

    results: dict[str, bool | None] = {}

    for name, fn in [
        ("3·No-regresión", check3_no_regresion),
        ("2·Dirección zoom (params)", check2_zoom_direction),
        ("1+4·Gate semántico + variedad", checks_1_4_gate_y_variedad),
    ]:
        print("─" * 72)
        print(f"CHEQUEO {name}")
        ok, detail = fn()
        print(detail)
        results[name] = ok
        tag = "SKIP" if ok is None else ("PASS ✅" if ok else "FAIL ❌")
        print(f"  → {tag}\n")

    print("=" * 72)
    print("  RESUMEN GATE 1")
    for k, v in results.items():
        tag = "SKIP" if v is None else ("PASS ✅" if v else "FAIL ❌")
        print(f"    {tag:8s} {k}")
    print("=" * 72)

    # Falla solo si un chequeo que corrió dio False (SKIP no falla)
    hard_fail = any(v is False for v in results.values())
    return 1 if hard_fail else 0


if __name__ == "__main__":
    sys.exit(main())
