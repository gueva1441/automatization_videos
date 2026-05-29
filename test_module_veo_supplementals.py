"""
test_module_veo_supplementals.py — GATE 2 chat 29 #175.

Test aislado de `_generate_supplementals_for_veo_chapter`: mockea
`_generate_flux_image_at` para escribir PNGs vacíos en disco (NO consume Flux
real). Verifica que se generan N entries con status='ok' y paths correctos.

USO:
    python test_module_veo_supplementals.py
"""
import shutil
import sys
from pathlib import Path
from unittest.mock import patch

import asset_manager as am


TEST_VIDEO_ID = "TEST-CHAT29-GATE2-veo-supplementals"
CHAPTER_ID = "ch01"


def _mock_flux_generate(raw_prompt, art_profile, output_path, use_ultra, seed=None):
    """Side effect del mock: crea un PNG válido mínimo (8-byte signature)."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    # PNG signature header (8 bytes) — suficiente para que existe el archivo
    output_path.write_bytes(b"\x89PNG\r\n\x1a\n")
    return {
        "path": output_path,
        "attempts": 1,
        "validated": None,
    }


def main() -> int:
    test_dir = am.OUTPUT_DIR / TEST_VIDEO_ID
    if test_dir.exists():
        shutil.rmtree(test_dir)

    chapter = {
        "id": CHAPTER_ID,
        "image_prompts": ["dummy base image_prompt"],
        "video_prompts": ["dummy base video_prompt"],
        "art_profile": "DOCUMENTARY",
        "veo_position": "start",
        "supplemental_image_prompts": [
            {"prompt": "Wide shot of mid-1980s African village at dawn, no readable text",
             "narration_anchor": "anchor 1"},
            {"prompt": "Close-up of period-correct 1986 wooden door creaking open",
             "narration_anchor": "anchor 2"},
            {"prompt": "Aerial view of a misty lake at dawn, dark green palette",
             "narration_anchor": "anchor 3"},
            {"prompt": "Elderly man in mid-1980s rural attire walking on dirt path",
             "narration_anchor": "anchor 4"},
        ],
    }

    print(f"\n{'='*70}")
    print(f"GATE 2 chat 29 #175 — _generate_supplementals_for_veo_chapter")
    print(f"{'='*70}")
    print(f"  video_id (test): {TEST_VIDEO_ID}")
    print(f"  chapter:         {CHAPTER_ID}")
    print(f"  N supplementals: {len(chapter['supplemental_image_prompts'])}")
    print(f"  mocking:         asset_manager._generate_flux_image_at")
    print()

    with patch.object(am, "_generate_flux_image_at", side_effect=_mock_flux_generate):
        results = am._generate_supplementals_for_veo_chapter(
            chapter=chapter,
            video_id=TEST_VIDEO_ID,
            chapter_id=CHAPTER_ID,
            use_ultra=False,
        )

    # Verificaciones
    n_expected = len(chapter["supplemental_image_prompts"])
    assert len(results) == n_expected, \
        f"esperaba {n_expected} results, vinieron {len(results)}"

    for i, r in enumerate(results, start=1):
        assert r["index"] == i, f"result {i} index incorrecto: {r['index']}"
        assert r["status"] == "ok", f"result {i} status={r['status']} (esperado 'ok')"
        assert r["narration_anchor"] == f"anchor {i}", \
            f"result {i} anchor incorrecto: {r['narration_anchor']}"
        assert r["path"], f"result {i} path vacío"
        full_path = am.OUTPUT_DIR / r["path"]
        assert full_path.exists(), f"result {i} PNG no existe: {full_path}"
        assert full_path.suffix == ".png"
        assert f"_supp_{i:02d}" in full_path.name, \
            f"result {i} filename sin sufijo _supp_NN: {full_path.name}"
        print(f"  OK supp {i}: {full_path.name} (anchor='{r['narration_anchor']}', "
              f"status={r['status']})")

    # Verificar idempotencia: segundo run debería retornar 'skipped_exists'
    print(f"\n  Verificando idempotencia (re-run sin mock no debe re-generar)...")
    with patch.object(am, "_generate_flux_image_at", side_effect=AssertionError("NO LLAMAR")):
        results2 = am._generate_supplementals_for_veo_chapter(
            chapter=chapter,
            video_id=TEST_VIDEO_ID,
            chapter_id=CHAPTER_ID,
            use_ultra=False,
        )
    for i, r in enumerate(results2, start=1):
        assert r["status"] == "skipped_exists", \
            f"idempotencia roto en supp {i}: status={r['status']}"
    print(f"  OK los 4 supplementals devuelven 'skipped_exists' en re-run")

    # Cleanup
    shutil.rmtree(test_dir)
    print(f"\n  Cleanup: {test_dir} borrado")

    print(f"\n  [OK] GATE 2 PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
