"""test_module_concat_windowed.py — F2b §4: concat por ventanas (re-encode solo en las fronteras).

Segmentos sintéticos (testsrc2 + tono) → se compara contra la REFERENCIA del xfade encadenado de hoy
re-encodeada sin pérdida (qp 0): misma línea de tiempo (± 1 frame), PSNR de luma ≥ 50 dB, decodifica sin
errores, y los cuerpos son COPIA exacta del segmento (PSNR ∞).
Correr: python -m pytest test_module_concat_windowed.py -q
"""
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from script_engine import transition_applier as ta

FF, FP = shutil.which("ffmpeg"), shutil.which("ffprobe")
pytestmark = pytest.mark.skipif(not (FF and FP), reason="sin ffmpeg")
FPS = 30


def _seg(path: Path, src: str, dur: float, freq: int) -> Path:
    subprocess.run([FF, "-v", "error", "-y", "-f", "lavfi", "-i", f"{src}=s=320x180:r={FPS}:d={dur}",
                    "-f", "lavfi", "-i", f"sine=f={freq}:d={dur}", "-c:v", "libx264", "-g", "30", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "128k", "-shortest", str(path)], check=True, timeout=120)
    return path


@pytest.fixture(scope="module")
def segs(tmp_path_factory):
    d = tmp_path_factory.mktemp("cw")
    return d, [_seg(d / f"s{i}.mp4", src, 6.0, 300 + 100 * i)
               for i, src in enumerate(("testsrc2", "smptebars", "testsrc"))]


def _frames(p: Path) -> int:
    r = subprocess.run([FP, "-v", "error", "-select_streams", "v:0", "-count_frames", "-show_entries",
                        "stream=nb_read_frames", "-of", "csv=p=0", str(p)], capture_output=True, text=True, timeout=60)
    return int(r.stdout.strip())


def test_misma_linea_de_tiempo_y_psnr(segs):
    d, s = segs
    prof = ["SUBMARINE"] * 3
    plans = ta.build_transition_plan(3, prof)
    out = d / "new.mp4"
    ta.concat_windowed(s, out, d, prof, FF, FP, ["-c:v", "libx264"], window_sec=1.0)
    # referencia: el xfade encadenado de hoy, pero sin pérdida (crf 0) y con las mismas duraciones de video
    durs = [ta.probe_segment(x, FP).duration for x in s]
    trans = [round(max(p.duration_seconds, 1 / FPS) * FPS) / FPS for p in plans]
    fc, v, _ = ta._build_filter_complex(durs, [ta.TransitionPlan(p.from_idx, p.transition_name, t) for p, t in zip(plans, trans)])
    # la referencia es solo video, en yuv420p de punta a punta (sin conversión de croma) y sin pérdida (qp 0)
    fc = ";".join(x for x in fc.split(";") if "acrossfade" not in x)
    fc = "".join(f"[{i}:v]format=yuv420p[f{i}];" for i in range(3)) + re.sub(r"\[(\d):v\]", r"[f\1]", fc)
    ref = d / "ref.mp4"
    cmd = [FF, "-v", "error", "-y"] + sum((["-i", str(x)] for x in s), [])
    subprocess.run(cmd + ["-filter_complex", fc, "-map", f"[{v}]", "-c:v", "libx264", "-qp", "0", "-preset", "ultrafast",
                          "-pix_fmt", "yuv420p", str(ref)], check=True, timeout=300)
    assert abs(_frames(out) - _frames(ref)) <= 1                                   # duración ± 1 frame
    r = subprocess.run([FF, "-i", str(out), "-i", str(ref), "-lavfi", "[0:v][1:v]psnr", "-f", "null", "-"],
                       capture_output=True, text=True, timeout=300)
    # luma: el xfade de FFmpeg 8 pasa por yuv444p (el croma de la referencia, que es el camino de hoy, ya
    # viene resampleado en TODOS sus frames); la luma no, así que mide de verdad lo que agregan las ventanas
    y = float(re.search(r"PSNR y:([\d.inf]+)", r.stderr).group(1).replace("inf", "99"))
    assert y >= 50.0, y
    body = subprocess.run([FF, "-i", str(out), "-i", str(s[0]), "-lavfi",
                           "[0:v]trim=end=3.9,setpts=PTS-STARTPTS[a];[1:v]trim=end=3.9,setpts=PTS-STARTPTS[b];[a][b]psnr",
                           "-f", "null", "-"], capture_output=True, text=True, timeout=120)
    assert "average:inf" in body.stderr                                              # cuerpo = copia exacta del segmento
    dec = subprocess.run([FF, "-v", "error", "-i", str(out), "-f", "null", "-"], capture_output=True, text=True, timeout=120)
    assert dec.stderr.strip() == ""                                                  # decodifica sin errores
    assert (d / "_concat_video.ts").exists() and (d / "_concat_audio.wav").exists()  # insumos de la mezcla de música


def test_musica_audio_solo_mismo_largo_que_la_clasica(segs, monkeypatch):
    """La mezcla audio-solo + remux da el mismo largo que la clásica (tpad + re-encode) ± 1 frame, con el video
    por copia (padding + concat) y sin errores de decodificación."""
    import fase2b
    d, s = segs
    prof = ["SUBMARINE"] * 3
    nm = d / "nm.mp4"
    ta.concat_windowed(s, nm, d, prof, FF, FP, ["-c:v", "libx264"])
    music = d / "music.wav"
    subprocess.run([FF, "-v", "error", "-y", "-f", "lavfi", "-i", "sine=f=220:d=25", str(music)], check=True, timeout=60)
    monkeypatch.setattr(fase2b.pipeline, "fps", FPS, raising=False)
    sync = {"mixing": {"music_volume": 0.2, "music_volume_floor": 0.05}}
    new = fase2b._mix_music_audio_only(work_dir=d, music_path=music, sync_map=sync, output_path=d / "mix_new.mp4",
                                       music_floor_path=music)
    old = fase2b._mix_music_into_video(video_path=nm, music_path=music, sync_map=sync, output_path=d / "mix_old.mp4",
                                       music_floor_path=music)
    assert abs(_frames(new) - _frames(old)) <= 1
    assert _frames(new) == _frames(nm) + round(fase2b.INITIAL_SILENCE_SEC * FPS)
    dec = subprocess.run([FF, "-v", "error", "-i", str(new), "-f", "null", "-"], capture_output=True, text=True, timeout=120)
    assert dec.stderr.strip() == ""


def test_cuerpos_por_copia_y_ventanas_en_keyframes(segs):
    _, s = segs
    infos = [ta.probe_segment(x, FP) for x in s]
    assert infos[0].frames == 6 * FPS and infos[0].keyframes[:2] == (0.0, 1.0)
    bodies = ta.plan_windows(infos, [0.5, 0.5], 1.0)
    assert bodies[0][0] == 0.0 and bodies[0][1] in infos[0].keyframes and bodies[0][1] <= 6.0 - 1.5
    assert bodies[1][0] in infos[1].keyframes and bodies[1][0] >= 1.5
    assert ta.plan_windows(infos, [3.0, 3.0], 1.0) is None                          # sin cuerpo → caller usa el clásico


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
