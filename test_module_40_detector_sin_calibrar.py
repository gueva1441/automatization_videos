"""
test_module_40_detector_sin_calibrar.py — GATE 6-CC (chat 40 bloque 6).

Ejerce el CÓDIGO REAL (fase2b._classify_uncalibrated_tracks), no una copia inventada
(evita el "smoke que miente" del chat 39). Usa music_maps sintéticos + jsons DUMMY
en disco (dentro del repo, para que mp3_path relativo resuelva). NO toca jsons reales.

Casos:
  1. track `generated` SIN clave → uncal_generated.
  2. track `reused` SIN clave → uncal_reused.
  3. track CON clave (music_volume) → no aparece en ninguna lista.
  4. track calibrado JUSTO a 0.26 (== base) → NO falso positivo (tiene la clave).
  5. cap `skipped` → ignorado.

USO:
    python test_module_40_detector_sin_calibrar.py
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

from fase2b import ChapterPlan, _classify_uncalibrated_tracks

TMP = Path("_tmp_test40_detector").resolve()


def _plan(cid: str) -> ChapterPlan:
    return ChapterPlan(
        chapter_id=cid, engine="flux", audio_path=Path(f"{cid}.mp3"),
        audio_duration=8.0, asset_paths=[], timestamps_path=None,
        is_first=False, art_profile=None, narrative_intent="",
    )


def _make_track(track_id: str, match_source: str, volume_keys: dict | None) -> dict:
    """Crea mp3 dummy + json dummy en TMP. Devuelve el track_info para el music_map."""
    mp3 = TMP / f"{track_id}.mp3"
    mp3.write_bytes(b"\x00")
    meta = {"track_id": track_id, "mp3_filename": f"{track_id}.mp3",
            "prompt_used": "dummy", "duration_ms": 1000}
    if volume_keys:
        meta.update(volume_keys)
    (TMP / f"{track_id}.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"track_id": track_id, "match_source": match_source,
            "mp3_path": f"_tmp_test40_detector/{track_id}.mp3"}


def main() -> int:
    if TMP.exists():
        shutil.rmtree(TMP, ignore_errors=True)
    TMP.mkdir()
    fails: list[str] = []
    try:
        music_map = {
            "ch01": _make_track("gen_nuevo", "generated", None),            # caso 1
            "ch02": _make_track("lib_base", "reused", None),                # caso 2
            "ch03": _make_track("lib_calibrado", "reused", {"music_volume": 0.08,
                                "music_volume_floor": 0.03}),               # caso 3
            "ch04": _make_track("lib_en_base_exacto", "reused", {"music_volume": 0.26,
                                "music_volume_floor": 0.16}),               # caso 4
            "ch05": {"track_id": "skip", "match_source": "skipped"},        # caso 5
        }
        plans = [_plan(c) for c in ("ch01", "ch02", "ch03", "ch04", "ch05")]

        gen, reused = _classify_uncalibrated_tracks(plans, music_map)
        gen_caps = {c for c, _ in gen}
        reused_caps = {c for c, _ in reused}
        print(f"  uncal_generated = {sorted(gen)}")
        print(f"  uncal_reused    = {sorted(reused)}")

        checks = [
            ("1 generated sin clave → uncal_generated", "ch01" in gen_caps),
            ("2 reused sin clave → uncal_reused", "ch02" in reused_caps),
            ("3 con clave (0.08) → en ninguna lista",
             "ch03" not in gen_caps and "ch03" not in reused_caps),
            ("4 calibrado == base (0.26) → NO falso positivo (tiene clave)",
             "ch04" not in gen_caps and "ch04" not in reused_caps),
            ("5 skipped → ignorado",
             "ch05" not in gen_caps and "ch05" not in reused_caps),
            ("ch01 NO en reused (clasificó como generated)", "ch01" not in reused_caps),
            ("ch02 NO en generated (clasificó como reused)", "ch02" not in gen_caps),
        ]
        for name, ok in checks:
            print(f"      {'OK ' if ok else 'FAIL'} {name}")
            if not ok:
                fails.append(name)
    finally:
        shutil.rmtree(TMP, ignore_errors=True)

    print("\n" + "─" * 56)
    if fails:
        print(f"  [FAIL] {len(fails)} chequeo(s):")
        for x in fails:
            print(f"    - {x}")
        return 1
    print("  [OK] GATE 6-CC: detector por-presencia 5/5 (sin falso positivo en ==base).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
