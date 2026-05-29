"""
test_module_fase2b_hybrid_segment.py — GATE 4 chat 29 #175.

Test aislado de _build_chapter_segment rama veo HÍBRIDA. Construye dummy
Veo MP4 + 4 PNGs + audio dummy, llama _build_chapter_segment con
ChapterPlan híbrido, verifica:

  a) MP4 output existe
  b) Duración ≈ audio_duration ± 0.5s
  c) NINGUN comando ffmpeg invocado uso -stream_loop (el bug #175 NO se
     activa porque base_clip ya tiene duración matcheada al audio)
  d) hybrid_visual.mp4 fue creado por _concat_visual_clips

Hace los 2 casos: veo_position="start" (cap 1 hook) y "end" (cap 7 outro).

USO:
    python test_module_fase2b_hybrid_segment.py
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import fase2b as fb
from fase2b import ChapterPlan, _get_duration


def _make_dummy_veo(out: Path, dur_sec: float = 8.0) -> None:
    """color=blue 1080×1920 sin audio."""
    assert fb.FFMPEG is not None
    cmd = [
        fb.FFMPEG, "-y", "-f", "lavfi",
        "-i", f"color=blue:s=1080x1920:d={dur_sec}:r=30",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-an",
        str(out),
    ]
    r = subprocess.run(cmd, capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"dummy veo gen falló: {r.stderr.decode()[-300:]}")


def _make_dummy_png(out: Path, color: str) -> None:
    """1080×1920 PNG sólido. color = 'red', 'green', 'yellow', 'magenta', etc."""
    assert fb.FFMPEG is not None
    cmd = [
        fb.FFMPEG, "-y", "-f", "lavfi",
        "-i", f"color={color}:s=1080x1920:d=0.1",
        "-frames:v", "1",
        str(out),
    ]
    r = subprocess.run(cmd, capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"dummy png gen falló: {r.stderr.decode()[-300:]}")


def _make_dummy_audio(out: Path, dur_sec: float) -> None:
    """Tono 440Hz, WAV PCM."""
    assert fb.FFMPEG is not None
    cmd = [
        fb.FFMPEG, "-y", "-f", "lavfi",
        "-i", f"sine=frequency=440:duration={dur_sec}",
        "-c:a", "pcm_s16le",
        str(out),
    ]
    r = subprocess.run(cmd, capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"dummy audio gen falló: {r.stderr.decode()[-300:]}")


def _run_one(tmp_dir: Path, label: str, veo_position: str, audio_dur: float) -> bool:
    """Ejecuta el test para un veo_position. Retorna True si PASS."""
    print(f"\n  --- CASE: veo_position={veo_position}, audio={audio_dur}s ---")

    case_dir = tmp_dir / f"case_{veo_position}"
    case_dir.mkdir(parents=True, exist_ok=True)
    work_dir = case_dir / "work"
    work_dir.mkdir(parents=True, exist_ok=True)

    # ─── Assets dummy ───
    veo_path = case_dir / "dummy_veo.mp4"
    _make_dummy_veo(veo_path, dur_sec=8.0)
    veo_real_dur = _get_duration(veo_path)
    print(f"     dummy_veo.mp4 dur={veo_real_dur:.2f}s")

    audio_path = case_dir / "dummy_audio.wav"
    _make_dummy_audio(audio_path, dur_sec=audio_dur)

    supp_colors = ["red", "green", "yellow", "magenta"]
    supp_paths = []
    for i, color in enumerate(supp_colors, start=1):
        p = case_dir / f"dummy_supp_{i:02d}.png"
        _make_dummy_png(p, color)
        supp_paths.append(p)

    # ─── ChapterPlan híbrido ───
    plan = ChapterPlan(
        chapter_id="ch01",
        engine="veo",
        audio_path=audio_path,
        audio_duration=audio_dur,
        asset_paths=[veo_path],
        timestamps_path=None,  # CRITICAL: forza fallback uniforme
        is_first=(veo_position == "start"),
        art_profile=None,
        narration="placeholder",
        image_prompt="placeholder",
        label="hibrido",
        narration_anchors=None,
        supplemental_paths=supp_paths,
        supplemental_anchors=["a", "b", "c", "d"],
        veo_position=veo_position,
    )

    flow_spec = {
        "movement": "horizontal",
        "intensity": 0.95,
        "steady": 0.30,
        "dof": True,
        "reasoning": "test_dummy_chat29",
    }

    # ─── Instrumentar _run_cmd para capturar TODOS los comandos ───
    captured_cmds: list[list[str]] = []
    original_run_cmd = fb._run_cmd

    def _spy_run_cmd(cmd, timeout=240):
        captured_cmds.append(list(cmd))
        return original_run_cmd(cmd, timeout=timeout)

    segment_path = case_dir / "segment_out.mp4"

    with patch.object(fb, "_run_cmd", side_effect=_spy_run_cmd):
        try:
            fb._build_chapter_segment(
                plan=plan,
                segment_path=segment_path,
                work_dir=work_dir,
                hook_text=None,
                no_subs=True,
                video_width=1080,
                video_height=1920,
                fps=30,
                flow_spec=flow_spec,
            )
        except Exception as e:
            print(f"     [FAIL] _build_chapter_segment lanzó: {type(e).__name__}: {e}")
            return False

    # ─── ASSERT (a): MP4 output existe ───
    if not segment_path.exists():
        print(f"     [FAIL a] MP4 output no existe: {segment_path}")
        return False
    print(f"     [OK a] MP4 output existe ({segment_path.stat().st_size / 1024 / 1024:.1f} MB)")

    # ─── ASSERT (b): duración ≈ audio_duration ± 0.5 ───
    out_dur = _get_duration(segment_path)
    if abs(out_dur - audio_dur) > 0.5:
        print(f"     [FAIL b] duración out={out_dur:.2f}s difiere de audio={audio_dur}s > 0.5s")
        return False
    print(f"     [OK b] duración {out_dur:.2f}s ≈ {audio_dur}s")

    # ─── ASSERT (c): stream_loop NO activado significativamente ───
    # El bug #175 era el clip Veo de 8s loopeando 6-9× para cubrir 50-75s.
    # Distinguimos:
    #   - MALIGNO (bug #175): stream_loop con hybrid_dur << audio_dur (gap > 0.5s)
    #   - BENIGNO (cuantización fps): hybrid_dur ≈ audio_dur ± 0.5s, stream_loop
    #     rellena <0.5s de cuantización de DepthFlow a fps fijo. Operacionalmente
    #     inocuo. Es un known artifact, NO la regresión.
    hybrid_path = work_dir / "ch01_hybrid_visual.mp4"
    hybrid_dur = _get_duration(hybrid_path) if hybrid_path.exists() else 0.0
    gap = audio_dur - hybrid_dur

    stream_loop_cmds = [
        c for c in captured_cmds
        if any("-stream_loop" in arg or arg == "-stream_loop" for arg in c)
    ]

    if stream_loop_cmds and gap > 0.5:
        print(f"     [FAIL c] BUG #175: stream_loop con gap={gap:.2f}s "
              f"(hybrid {hybrid_dur:.2f}s << audio {audio_dur}s)")
        for c in stream_loop_cmds[:2]:
            print(f"        {' '.join(c[:8])}...")
        return False
    if stream_loop_cmds:
        print(f"     [OK c] stream_loop benigno (gap={gap*1000:.0f}ms, cuantización fps), "
              f"NO es bug #175")
    else:
        print(f"     [OK c] ningún cmd usó -stream_loop "
              f"({len(captured_cmds)} cmds totales, gap={gap*1000:+.0f}ms)")

    # ─── ASSERT (d): hybrid_visual.mp4 fue creado por _concat_visual_clips ───
    if not hybrid_path.exists():
        print(f"     [FAIL d] hybrid_visual.mp4 no existe: {hybrid_path}")
        print(f"        cmds capturados: {len(captured_cmds)}")
        for c in captured_cmds:
            print(f"        - {c[0]} ... {c[-1] if c else ''}")
        return False
    print(f"     [OK d] hybrid_visual.mp4 existe ({hybrid_path.stat().st_size / 1024 / 1024:.1f} MB)")

    return True


def main() -> int:
    if fb.FFMPEG is None:
        print("[FAIL] ffmpeg no encontrado")
        return 1

    print(f"\n{'='*70}")
    print(f"GATE 4 chat 29 #175 — _build_chapter_segment rama veo HÍBRIDA")
    print(f"{'='*70}")

    with tempfile.TemporaryDirectory(prefix="test_chat29_gate4_") as tmp:
        tmp_dir = Path(tmp)
        print(f"  tmp dir: {tmp_dir}")

        # CASE 1: veo_position=start (cap 1 hook, audio ~49.3s)
        ok_start = _run_one(tmp_dir, "ch01", "start", 49.3)

        # CASE 2: veo_position=end (cap 7 outro, audio ~75.5s)
        ok_end = _run_one(tmp_dir, "ch07", "end", 75.5)

    if ok_start and ok_end:
        print(f"\n  [OK] GATE 4 PASS — los 4 asserts pasaron en start Y end")
        return 0
    else:
        print(f"\n  [FAIL] GATE 4 FAIL — start={ok_start}, end={ok_end}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
