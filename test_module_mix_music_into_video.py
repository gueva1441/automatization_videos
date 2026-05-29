"""
test_module_mix_music_into_video.py — Test aislado del paso B del mixer.

Toma:
  - MP4 chat 27 sin música (renombrado en GATE 0.4 a _no_music.mp4)
  - WAV continuo del paso A (generado por BLOQUE 2)
  - sync_map.mixing del topic

Produce un MP4 de prueba con música+ducking, sin tocar el resto del pipeline.

USO:
    python test_module_mix_music_into_video.py
"""
import json
import sys
import time
from pathlib import Path

from config import OUTPUT_DIR
from fase2b import _mix_music_into_video, _get_duration

VIDEO_ID = "7b52de57-eee6-4018-ac25-8357e9779d92"


def main() -> int:
    video_in = OUTPUT_DIR / VIDEO_ID / "7b52de57_chat27_v6_no_music.mp4"
    music_in = OUTPUT_DIR / VIDEO_ID / "_test_music_work" / "_music_continuous.wav"
    sync_map_path = OUTPUT_DIR / "audio" / VIDEO_ID / "sync_map.json"
    video_out = OUTPUT_DIR / VIDEO_ID / "_test_mix_output.mp4"

    if not video_in.exists():
        print(f"[FAIL] Falta video input: {video_in}")
        print(f"   GATE 0.4 esperaba el MP4 chat 27 renombrado.")
        return 1
    if not music_in.exists():
        print(f"[FAIL] Falta WAV de musica: {music_in}")
        print(f"   Corre primero test_module_build_continuous_music.py")
        return 1

    sync_map = json.loads(sync_map_path.read_text(encoding="utf-8"))

    print(f"\n  🎚️  Mixing test: musica + ducking sobre narracion Pripyat")
    print(f"     video in:  {video_in.name} ({video_in.stat().st_size / 1024 / 1024:.1f} MB)")
    print(f"     music in:  {music_in.name} ({music_in.stat().st_size / 1024 / 1024:.1f} MB)")
    print(f"     video out: {video_out.name}")
    print()

    t0 = time.time()
    _mix_music_into_video(
        video_path=video_in,
        music_path=music_in,
        sync_map=sync_map,
        output_path=video_out,
    )
    elapsed = time.time() - t0

    in_dur = _get_duration(video_in)
    out_dur = _get_duration(video_out)
    out_size_mb = video_out.stat().st_size / 1024 / 1024

    print(f"\n  [OK] {video_out.name}")
    print(f"     duracion in:  {in_dur:.2f}s")
    print(f"     duracion out: {out_dur:.2f}s")
    print(f"     tamano:       {out_size_mb:.1f} MB")
    print(f"     tiempo mix:   {elapsed:.1f}s")

    if abs(out_dur - in_dur) > 1.0:
        print(f"\n  [FAIL] duracion out difiere de in > 1s")
        return 1

    print(f"\n  [OK] BLOQUE 3 PASS")
    print(f"     Reproduci {video_out} en VLC para validar:")
    print(f"       1. Musica presente de fondo todo el video")
    print(f"       2. Musica baja audiblemente cuando habla la narracion")
    print(f"       3. Musica vuelve a subir en silencios de la narracion")
    print(f"       4. Comparar contra pripyat_mezcla_fix_v2.mp3 (referencia chat 26)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
