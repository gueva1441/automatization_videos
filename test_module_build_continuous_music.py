"""
test_module_build_continuous_music.py — Test aislado del paso A del mixer.

Valida que _build_continuous_music_track() produce un WAV continuo del
largo correcto y con los crossfades aplicados, sin tocar el resto de fase2b.

USO:
    python test_module_build_continuous_music.py
"""
import json
import shutil
import sys
from pathlib import Path

from config import OUTPUT_DIR
from fase2b import (
    ChapterPlan,
    _build_continuous_music_track,
    _build_plans,
    _load_music_map,
    _get_duration,
)

VIDEO_ID = "7b52de57-eee6-4018-ac25-8357e9779d92"


def main() -> int:
    audio_dir = OUTPUT_DIR / "audio" / VIDEO_ID
    assets_dir = OUTPUT_DIR / VIDEO_ID / "assets"

    sync_map = json.loads((audio_dir / "sync_map.json").read_text(encoding="utf-8"))
    manifest = json.loads((assets_dir / "assets_manifest.json").read_text(encoding="utf-8"))
    # No necesitamos script_lookup para este test; pasamos {} (anchors no usados)
    plans = _build_plans(sync_map, manifest, VIDEO_ID, audio_dir, {})

    music_map = _load_music_map(VIDEO_ID)
    assert music_map is not None, "music_map.json no encontrado"
    assert len(music_map) >= len(plans), (
        f"music_map tiene {len(music_map)} entries, plans tiene {len(plans)}"
    )

    work_dir = OUTPUT_DIR / VIDEO_ID / "_test_music_work"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    work_dir.mkdir(parents=True)

    print(f"\n  🎼 Construyendo track continuo para {VIDEO_ID}")
    print(f"     caps: {len(plans)}")
    print(f"     work_dir: {work_dir}")
    print()

    out_path = _build_continuous_music_track(
        plans=plans,
        music_map=music_map,
        work_dir=work_dir,
    )

    expected_total = sum(p.audio_duration for p in plans)
    actual_total = _get_duration(out_path)

    # acrossfade resta crossfade_sec por cada par concatenado
    # (N pieces → N-1 crossfades → N-1 * crossfade_sec menos)
    from fase2b import MUSIC_CROSSFADE_SEC
    expected_with_crossfade = expected_total - (len(plans) - 1) * MUSIC_CROSSFADE_SEC

    print(f"\n  ✅ {out_path.name}")
    print(f"     tamaño: {out_path.stat().st_size / 1024 / 1024:.1f} MB")
    print(f"     duración real: {actual_total:.2f}s")
    print(f"     duración esperada (sin crossfade): {expected_total:.2f}s")
    print(f"     duración esperada (con crossfade): {expected_with_crossfade:.2f}s")

    # Tolerancia ±0.5s (acrossfade puede tener jitter de muestreo)
    if abs(actual_total - expected_with_crossfade) > 0.5:
        print(f"\n  ❌ FAIL: duración real difiere de esperada > 0.5s")
        return 1

    print(f"\n  ✅ BLOQUE 2 PASS")
    print(f"     Reproducí {out_path} en VLC para validar auditivamente")
    print(f"     que los crossfades entre caps suenan limpios.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
