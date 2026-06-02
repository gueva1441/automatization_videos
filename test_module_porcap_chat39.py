"""
test_module_porcap_chat39.py — Smoke AISLADO del volumen de música POR INTENT (chat 39).

NO corre el video entero. Valida por MEDICIÓN (ffmpeg volumedetect) las 4 cosas que
cambiaron, sin tocar el pipeline:

  (A. la resolución de volumen se movió a test_module_40_volumen_por_track.py en el
      chat 40 — el volumen ahora es propiedad del track json, no de music_by_intent.
      Este test quedó como cobertura de la MECÁNICA del mix, independiente del origen
      de los números.)
  B. Nivel POR CAP horneado en la pieza: piece_volume atenúa exactamente 20·log10(v) dB.
  C. _build_continuous_music_track con piece_volumes + output_filename construye DOS
     pistas (ducked + floor) y cada CAP queda a su nivel (vs una pista de referencia
     a vol=1.0, mismo contenido → cancela la variación del track).
  D. El sidechain SIGUE actuando: con una narración sintética (tono / silencio / tono),
     la música baja donde hay voz y vuelve donde calla. (params del perfil, intactos.)

USO:
    python test_module_porcap_chat39.py
"""
from __future__ import annotations

import math
import re
import shutil
import sys
import tempfile
from pathlib import Path

import audio_profiles
from fase2b import (
    FFMPEG,
    ChapterPlan,
    _build_continuous_music_track,
    _build_music_piece_for_chapter,
    _get_duration,
    _run_cmd,
)

TRACK = Path("audio_library/shock_curated.mp3").resolve()
MIXING = audio_profiles.AUDIO_PROFILES["MISTERIO_ABISAL"]["mixing"]
_MEAN_RE = re.compile(r"mean_volume:\s*(-?\d+(?:\.\d+)?)\s*dB")


def _mean_db(path: Path, ss: float | None = None, t: float | None = None) -> float:
    """mean_volume (dB) del archivo (o de una ventana [ss, ss+t]) via volumedetect."""
    cmd = [FFMPEG, "-hide_banner"]
    if ss is not None:
        cmd += ["-ss", f"{ss:.3f}"]
    cmd += ["-i", str(path)]
    if t is not None:
        cmd += ["-t", f"{t:.3f}"]
    cmd += ["-af", "volumedetect", "-f", "null", "-"]
    r = _run_cmd(cmd, timeout=60)
    m = _MEAN_RE.search(r.stderr)
    if not m:
        raise RuntimeError(f"no mean_volume en {path.name}: {r.stderr[-200:]}")
    return float(m.group(1))


def _fake_plan(cid: str, intent: str, dur: float, tmp: Path) -> ChapterPlan:
    return ChapterPlan(
        chapter_id=cid, engine="flux", audio_path=tmp / f"{cid}.mp3",
        audio_duration=dur, asset_paths=[], timestamps_path=None,
        is_first=(cid == "ch01"), art_profile=None, narrative_intent=intent,
    )


def main() -> int:
    if FFMPEG is None:
        print("[FAIL] ffmpeg no encontrado"); return 1
    if not TRACK.exists():
        print(f"[FAIL] no existe {TRACK}"); return 1

    tmp = Path(tempfile.mkdtemp(prefix="porcap_chat39_"))
    fails: list[str] = []
    print(f"  tmp: {tmp}")
    print(f"  track: {TRACK.name}\n")

    try:
        # ─── B. nivel por-cap horneado en la pieza ───
        print("\n  [B] piece_volume hornea 20·log10(v) dB en la pieza")
        ref_piece = tmp / "piece_ref.wav"
        _build_music_piece_for_chapter(TRACK, 8.0, ref_piece, piece_volume=1.0)
        ref_db = _mean_db(ref_piece)
        print(f"      ref (v=1.0): {ref_db:.2f} dB")
        for v in (0.26, 0.16, 0.08, 0.03):
            pp = tmp / f"piece_{v}.wav"
            _build_music_piece_for_chapter(TRACK, 8.0, pp, piece_volume=v)
            got_delta = _mean_db(pp) - ref_db
            exp_delta = 20 * math.log10(v)
            ok = abs(got_delta - exp_delta) < 0.6
            print(f"      v={v:<4}  Δ medido={got_delta:+6.2f} dB  esperado={exp_delta:+6.2f}  "
                  f"{'OK' if ok else 'FAIL'}")
            if not ok:
                fails.append(f"B: v={v} Δ={got_delta:.2f}, esperado {exp_delta:.2f}")

        # ─── C. dos pistas continuas por-cap (vs referencia, mismo contenido) ───
        print("\n  [C] _build_continuous_music_track: 2 WAVs, nivel por-cap")
        # ch01 [0,6] limpio, crossfade [6,8], ch04 [8,14] limpio (d=8/8, xfade=2 → 14s)
        cmusic_map = {
            "ch01": {"mp3_path": "audio_library/shock_curated.mp3", "match_source": "reused"},
            "ch04": {"mp3_path": "audio_library/shock_curated.mp3", "match_source": "reused"},
        }
        cplans = [_fake_plan("ch01", "setup", 8.0, tmp), _fake_plan("ch04", "shock", 8.0, tmp)]
        # Volúmenes fijos (este test cubre la MECÁNICA del horneado, no la resolución
        # — esa vive en test_module_40). ch04=shock 0.08/0.03, ch01=no-shock 0.26/0.16.
        cduck = {"ch01": 0.26, "ch04": 0.08}
        cfloor = {"ch01": 0.16, "ch04": 0.03}
        ref_wav = _build_continuous_music_track(
            cplans, cmusic_map, tmp, crossfade_sec=2.0,
            piece_volumes={"ch01": 1.0, "ch04": 1.0}, output_filename="cont_ref.wav")
        duck_wav = _build_continuous_music_track(
            cplans, cmusic_map, tmp, crossfade_sec=2.0,
            piece_volumes=cduck, output_filename="cont_ducked.wav")
        floor_wav = _build_continuous_music_track(
            cplans, cmusic_map, tmp, crossfade_sec=2.0,
            piece_volumes=cfloor, output_filename="cont_floor.wav")
        total = _get_duration(ref_wav)
        print(f"      duración continua: {total:.2f}s (esperado ~14)  "
              f"{'OK' if abs(total - 14.0) < 0.3 else 'FAIL'}")
        if abs(total - 14.0) >= 0.3:
            fails.append(f"C: duración {total:.2f} != ~14")
        if duck_wav == floor_wav or duck_wav == ref_wav:
            fails.append("C: las pistas se pisan (mismo path)")
        # ventanas limpias: ch01=[1,5], ch04=[9,13]
        wins = {"ch01": (1.0, 4.0), "ch04": (9.0, 4.0)}
        for kind, wav, vols in (("ducked", duck_wav, cduck), ("floor", floor_wav, cfloor)):
            for cap, (ss, t) in wins.items():
                got = _mean_db(wav, ss, t) - _mean_db(ref_wav, ss, t)
                exp = 20 * math.log10(vols[cap])
                ok = abs(got - exp) < 0.8
                print(f"      {kind:6} {cap}: Δvs.ref={got:+6.2f} dB  esperado={exp:+6.2f} "
                      f"(v={vols[cap]})  {'OK' if ok else 'FAIL'}")
                if not ok:
                    fails.append(f"C: {kind} {cap} Δ={got:.2f}, esperado {exp:.2f}")

        # ─── D. el sidechain sigue actuando ───
        print("\n  [D] sidechain: la música baja donde hay voz (params del perfil)")
        # narración sintética: tono [0,2], silencio [2,4], tono [4,6]
        key = tmp / "key.wav"
        _run_cmd([FFMPEG, "-y", "-f", "lavfi", "-i", "sine=frequency=200:duration=6",
                  "-af", "volume='if(between(t,2,4),0,1)':eval=frame",
                  "-ac", "2", "-ar", "44100", str(key)], timeout=60)
        music = tmp / "music_const.wav"
        _run_cmd([FFMPEG, "-y", "-f", "lavfi", "-i", "sine=frequency=600:duration=6",
                  "-ac", "2", "-ar", "44100", str(music)], timeout=60)
        ducked_out = tmp / "ducked_out.wav"
        sc = (f"[0:a][1:a]sidechaincompress="
              f"threshold={MIXING['duck_threshold']}:ratio={MIXING['duck_ratio']}:"
              f"attack={MIXING['duck_attack_ms']}:release={MIXING['duck_release_ms']}[out]")
        r = _run_cmd([FFMPEG, "-y", "-i", str(music), "-i", str(key),
                      "-filter_complex", sc, "-map", "[out]", str(ducked_out)], timeout=60)
        if r.returncode != 0:
            fails.append("D: sidechain ffmpeg falló")
            print(f"      [FAIL] {r.stderr[-200:]}")
        else:
            voiced = _mean_db(ducked_out, 0.3, 1.4)     # voz presente → ducked
            silent = _mean_db(ducked_out, 2.4, 1.2)     # voz ausente → sin duck
            drop = silent - voiced
            ok = drop > 2.0
            print(f"      música con voz = {voiced:.2f} dB | sin voz = {silent:.2f} dB | "
                  f"caída por ducking = {drop:.2f} dB  {'OK (>2dB)' if ok else 'FAIL'}")
            if not ok:
                fails.append(f"D: caída ducking {drop:.2f} dB <= 2")

    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("\n" + "─" * 56)
    if fails:
        print(f"  [FAIL] {len(fails)} chequeo(s):")
        for f in fails:
            print(f"    - {f}")
        return 1
    print("  [OK] smoke mecánica del mix (chat 39): B+C+D pasaron. "
          "(A → test_module_40)")
    print("  Tabla de niveles medidos arriba. Gate de oído (video completo) = Omar.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
