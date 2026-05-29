"""
TEST AISLADO PR 3 — chat 27.

Valida _calculate_image_count nueva contra sync_map real de Pripyat.

Espera duraciones reales del sync_map de Pripyat (calculado contra la lógica
preservada de bonus_position que el handoff explícitamente mantuvo:
  first_third = development_index < n_dev/3
  last_third  = development_index >= 2*n_dev/3
  middle      = otherwise

Con n_dev=5: third=1.667, 2*third=3.333. Por lo tanto:
  cap 2 (dev_idx=0): first_third (+1)
  cap 3 (dev_idx=1): first_third (+1)   <-- corrige expected del handoff (16->17)
  cap 4 (dev_idx=2): middle (0)
  cap 5 (dev_idx=3): middle (0)
  cap 6 (dev_idx=4): last_third (+1)

Esperados reales:
  ch02: 107.6s  -> round(107.6/7)=15 +1 first_third = 16 imgs
  ch03: 113.7s  -> round(113.7/7)=16 +1 first_third = 17 imgs  [handoff decia 16, era error]
  ch04:  86.7s  -> round(86.7/7)=12 +0 middle      = 12 imgs
  ch05: 149.4s  -> round(149.4/7)=21 +0 middle     = 21 -> clamp 18
  ch06: 129.8s  -> round(129.8/7)=19 +1 last_third = 20 -> clamp 18

NO toca produccion. Solo lee sync_map.json existente.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from script_engine.m03_visual import (
    _calculate_image_count,
    SECONDS_PER_IMAGE_TARGET,
    MIN_IMAGES_FLUX,
    MAX_IMAGES_FLUX,
)

TOPIC_ID = "7b52de57-eee6-4018-ac25-8357e9779d92"
SYNC_MAP_PATH = Path("output/audio") / TOPIC_ID / "sync_map.json"

EXPECTED = {
    2: ("setup first_third (+1)",      16),
    3: ("rising first_third (+1)",     17),
    4: ("shock middle (0)",            12),
    5: ("consequences middle (clamp 18)", 18),
    6: ("resolution last_third (clamp 18)", 18),
}


def main():
    print(f"\n{'='*70}")
    print(f"TEST PR 3 — _calculate_image_count vs sync_map Pripyat")
    print(f"SECONDS_PER_IMAGE_TARGET={SECONDS_PER_IMAGE_TARGET}, "
          f"MIN={MIN_IMAGES_FLUX}, MAX={MAX_IMAGES_FLUX}")
    print(f"{'='*70}\n")

    if not SYNC_MAP_PATH.exists():
        print(f"[ERROR] sync_map.json no existe en {SYNC_MAP_PATH}")
        print(f"   Re-correr: python fase1_5.py --topic {TOPIC_ID} --only audio")
        sys.exit(1)

    sync_map = json.loads(SYNC_MAP_PATH.read_text(encoding="utf-8"))
    chapters = sync_map.get("chapters", [])
    print(f"sync_map cargado: {len(chapters)} caps, "
          f"total {sync_map.get('total_duration_sec', '?')}s\n")

    print(f"{'Cap':<6}{'Duration':<12}{'n_imgs':<10}{'s/img':<10}"
          f"{'Expected':<12}{'Result':<8}")
    print("-" * 60)

    all_pass = True
    for cap in chapters:
        cap_id = cap.get("id", "")
        if not cap_id.startswith("ch"):
            continue
        cap_n = int(cap_id[2:])
        if cap_n not in EXPECTED:
            continue  # skip caps veo (1, 7) — no usan _calculate_image_count

        duration = float(cap["duration_sec"])
        n_imgs = _calculate_image_count(
            cap_duration_sec=duration,
            chapter_number=cap_n,
            total_chapters=7,
        )
        s_per_img = duration / n_imgs
        desc, expected = EXPECTED[cap_n]
        status = "PASS" if n_imgs == expected else f"FAIL (esperado {expected})"
        if n_imgs != expected:
            all_pass = False

        print(f"ch{cap_n:02d}   {duration:>6.1f}s    {n_imgs:>4} imgs   "
              f"{s_per_img:>5.1f}s   {expected:>5}      {status}")

    print()
    if all_pass:
        print("[OK] TODOS LOS CAPS PASAN — PR 3 implementacion OK")
        print("   -> Avanzar al BLOQUE 2 del HANDOFF")
        sys.exit(0)
    else:
        print("[FAIL] HAY FALLOS — revisar implementacion antes de avanzar")
        sys.exit(2)


if __name__ == "__main__":
    main()
