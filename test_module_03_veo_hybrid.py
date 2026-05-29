"""
test_module_03_veo_hybrid.py — GATE 1 chat 29 #175.

Sanity test del schema híbrido Veo+Flux: corre assign_visual_prompts sobre
Pripyat (que ya tiene skeleton + narración + sync_map en disco) y verifica
que caps 1 y 7 emiten el schema nuevo con supplemental_image_prompts[]
válidos.

NO genera video. NO consume Veo. Solo m03 (Gemini Flash, ~$0.010).

POST-TEST: el _steps/<pripyat>/03_visual.json queda SOBRESCRITO con el
output de este test. El runner debe restaurar desde
.bak_gate1_chat29_pre_test inmediatamente después.

USO:
    python test_module_03_veo_hybrid.py
"""
import json
import sys
from pathlib import Path

from script_engine.m03_visual import (
    assign_visual_prompts,
    MIN_FLUX_EXTRAS,
    MAX_FLUX_EXTRAS,
    VEO_CLIP_DURATION_SEC,
)
from script_engine.topics_db import load_db

TOPIC_ID = "7b52de57-eee6-4018-ac25-8357e9779d92"
STEPS_DIR = Path("data/scripts/_steps") / TOPIC_ID
SYNC_MAP_PATH = Path("output/audio") / TOPIC_ID / "sync_map.json"


def main() -> int:
    if not STEPS_DIR.exists():
        print(f"[FAIL] no existe {STEPS_DIR}")
        return 1
    if not SYNC_MAP_PATH.exists():
        print(f"[FAIL] no existe {SYNC_MAP_PATH}")
        return 1

    # Cargar topic desde topics_db
    db = load_db()
    topics = db.get("topics", []) if isinstance(db, dict) else db
    topic = next(
        (t for t in topics if (t.get("id") or t.get("topic_id")) == TOPIC_ID),
        None,
    )
    if topic is None:
        print(f"[FAIL] topic {TOPIC_ID} no encontrado en topics_db")
        return 1

    # Cargar skeleton + narration + sync_map de disco
    skeleton = json.loads((STEPS_DIR / "01a_skeleton.json").read_text(encoding="utf-8"))
    narration = json.loads((STEPS_DIR / "01b_narration.json").read_text(encoding="utf-8"))
    sync_map = json.loads(SYNC_MAP_PATH.read_text(encoding="utf-8"))

    print(f"\n{'='*70}")
    print(f"GATE 1 chat 29 #175 — m03 v hibrido sanity (topic {TOPIC_ID[:8]})")
    print(f"{'='*70}")
    print(f"  Constantes: VEO_CLIP_DURATION_SEC={VEO_CLIP_DURATION_SEC}")
    print(f"              MIN_FLUX_EXTRAS={MIN_FLUX_EXTRAS}")
    print(f"              MAX_FLUX_EXTRAS={MAX_FLUX_EXTRAS}")
    print()

    out = assign_visual_prompts(topic, skeleton, narration, sync_map=sync_map)
    chapters = out.get("chapters", [])
    print(f"\n  Chapters generados: {len(chapters)}")

    # Map chapter_number -> dict
    by_n = {c["chapter_number"]: c for c in chapters}

    # ─── Cap 1 (hook) ───
    print(f"\n  --- Cap 1 (hook, esperado veo_position=start) ---")
    cap1 = by_n.get(1)
    assert cap1 is not None, "cap 1 ausente"
    assert "image_prompt" in cap1, "cap 1 sin image_prompt"
    assert "video_prompt" in cap1, "cap 1 sin video_prompt"
    assert cap1.get("veo_position") == "start", \
        f"cap 1 veo_position esperado 'start', vino '{cap1.get('veo_position')}'"
    supp1 = cap1.get("supplemental_image_prompts")
    assert isinstance(supp1, list), "cap 1 supplementals no es lista"
    assert MIN_FLUX_EXTRAS <= len(supp1) <= MAX_FLUX_EXTRAS, \
        f"cap 1 supplementals fuera de rango: {len(supp1)}"
    narr1 = next(
        (c.get("narration", "") for c in narration["chapters"] if c["chapter_number"] == 1),
        "",
    )
    for i, sp in enumerate(supp1, 1):
        assert sp["narration_anchor"] in narr1, \
            f"cap 1 supp {i} anchor NO es substring de narration"
    print(f"     OK image_prompt={len(cap1['image_prompt'])} chars")
    print(f"     OK video_prompt={len(cap1['video_prompt'])} chars")
    print(f"     OK veo_position=start")
    print(f"     OK {len(supp1)} supplementals (rango {MIN_FLUX_EXTRAS}-{MAX_FLUX_EXTRAS})")
    print(f"     OK todos los anchors substring exactos")

    # ─── Cap 7 (reveal_outro) ───
    print(f"\n  --- Cap 7 (reveal_outro, esperado veo_position=end) ---")
    cap7 = by_n.get(7)
    assert cap7 is not None, "cap 7 ausente"
    assert "image_prompt" in cap7, "cap 7 sin image_prompt"
    assert "video_prompt" in cap7, "cap 7 sin video_prompt"
    assert cap7.get("veo_position") == "end", \
        f"cap 7 veo_position esperado 'end', vino '{cap7.get('veo_position')}'"
    supp7 = cap7.get("supplemental_image_prompts")
    assert isinstance(supp7, list), "cap 7 supplementals no es lista"
    assert MIN_FLUX_EXTRAS <= len(supp7) <= MAX_FLUX_EXTRAS, \
        f"cap 7 supplementals fuera de rango: {len(supp7)}"
    narr7 = next(
        (c.get("narration", "") for c in narration["chapters"] if c["chapter_number"] == 7),
        "",
    )
    for i, sp in enumerate(supp7, 1):
        assert sp["narration_anchor"] in narr7, \
            f"cap 7 supp {i} anchor NO es substring de narration"
    print(f"     OK image_prompt={len(cap7['image_prompt'])} chars")
    print(f"     OK video_prompt={len(cap7['video_prompt'])} chars")
    print(f"     OK veo_position=end")
    print(f"     OK {len(supp7)} supplementals (rango {MIN_FLUX_EXTRAS}-{MAX_FLUX_EXTRAS})")
    print(f"     OK todos los anchors substring exactos")

    # ─── Caps Flux puros 2-6: no deberian tener supplementals ───
    print(f"\n  --- Caps Flux puros (2-6) sin cambios esperados ---")
    for cn in (2, 3, 4, 5, 6):
        cap = by_n.get(cn)
        assert cap is not None, f"cap {cn} ausente"
        assert "image_prompts" in cap, f"cap {cn} sin image_prompts (flux)"
        assert "veo_position" not in cap, \
            f"cap {cn} flux no deberia tener veo_position"
        print(f"     OK cap{cn} flux: {len(cap['image_prompts'])} imgs")

    print(f"\n  [OK] GATE 1 PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
