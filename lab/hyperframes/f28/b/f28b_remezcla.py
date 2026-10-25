"""F28 §B.3 — re-mezcla de Vajont SOLO AUDIO con la paleta F28 y el mapa de intensidad → f8s3-vajont_final_gfx_v2.mp4.

No toca imágenes, clips, gfx ni segmentos: usa lo que dejó el render de F27 en `_fase2b_work` (`_concat_video.ts`, video
de los 7 segmentos; `_concat_audio.wav`, narración + sfx) y las mismas funciones de la etapa de música de fase2b:
`_build_plans` → `_gfx_pauses` → `_resolve_music_volumes` → `_mapa_intensidad` → `_build_continuous_music_track`
(ducked + floor) → `_mix_music_audio_only` (con `_HW_ENCODE` = el `--hw-encode` del handoff: solo afecta al clip de
2.5 s del arranque; el video va por copia).
El `music_map.json` de F26 (las curated) se guarda como `music_map_f26.json` (se mueve, no se borra) y m07 arma el
nuevo con la paleta (el matcher elige entre las 2 de cada intent; Gemini Flash, centavos).
Mide: pista por cap, mapa de intensidad, LUFS por cap con y sin música (y el total), tiempo del pase.
Uso: PYTHONIOENCODING=utf-8 python -I lab/hyperframes/f28/b/f28b_remezcla.py
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path[:0] = [str(ROOT)]
LAB = Path(__file__).resolve().parent
TID = "f8s3-vajont"
OUT = ROOT / "output" / TID
AUD = ROOT / "output" / "audio" / TID
WORK = OUT / "_fase2b_work"
V2 = OUT / f"{TID}_final_gfx_v2.mp4"
F27 = OUT / f"{TID}_final_gfx.mp4"


def lufs(p: Path, ss: float | None = None, t: float | None = None) -> dict:
    cmd = ["ffmpeg", "-hide_banner", "-nostats"]
    if ss is not None:
        cmd += ["-ss", f"{ss:.3f}", "-t", f"{t:.3f}"]
    cmd += ["-i", str(p), "-vn", "-af", "ebur128", "-f", "null", "-"]
    err = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace").stderr
    r = err[err.rfind("Summary:"):]
    return {"I": float(re.search(r"I:\s+(-?[\d.]+) LUFS", r).group(1)),
            "LRA": float(re.search(r"LRA:\s+(-?[\d.]+) LU", r).group(1))}


def dur(p: Path) -> float:
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                 str(p)], capture_output=True, text=True).stdout.strip())


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    import fase2b as fb
    from script_engine import m07_music_director as m7
    if V2.exists():
        raise SystemExit(f"{V2.name} ya existe: no se pisa")
    t0 = time.time()
    sync_map = json.loads((AUD / "sync_map.json").read_text(encoding="utf-8"))
    viejo = AUD / "music_map.json"
    if viejo.exists() and not (AUD / "music_map_f26.json").exists():
        shutil.move(str(viejo), str(AUD / "music_map_f26.json"))
    mm = m7.generate_music_map(TID, sync_map, interactive=False)
    music_map = fb._load_music_map(TID)
    manifest = json.loads((OUT / "assets" / "assets_manifest.json").read_text(encoding="utf-8"))
    plans = fb._build_plans(sync_map, manifest, TID, AUD, fb._load_script_lookup(TID))
    pauses = fb._gfx_pauses(plans, WORK)
    mixing = sync_map.get("mixing", {})
    ducked, floor = fb._resolve_music_volumes(plans, mixing, music_map)
    intensidad = fb._mapa_intensidad(TID, plans, pauses)
    t1 = time.time()
    md = fb._build_continuous_music_track(plans=plans, music_map=music_map, work_dir=WORK,
                                          crossfade_sec=fb.MUSIC_CROSSFADE_SEC, piece_volumes=ducked,
                                          output_filename="_music_continuous_ducked.wav", extra_sec=pauses,
                                          intensidad=intensidad)
    mf = fb._build_continuous_music_track(plans=plans, music_map=music_map, work_dir=WORK,
                                          crossfade_sec=fb.MUSIC_CROSSFADE_SEC, piece_volumes=floor,
                                          output_filename="_music_continuous_floor.wav", extra_sec=pauses,
                                          intensidad=intensidad)
    fb._HW_ENCODE = True
    fb._mix_music_audio_only(work_dir=WORK, music_path=md, sync_map=sync_map, output_path=V2, music_floor_path=mf)
    md.unlink(missing_ok=True)
    mf.unlink(missing_ok=True)
    t_mezcla = time.time() - t1
    # LUFS por cap: los límites salen de los segmentos que se concatenaron (+ el arranque de 2.5 s)
    off = fb.INITIAL_SILENCE_SEC
    caps = []
    for k, p in enumerate(plans, start=1):
        seg = WORK / f"seg_{k:02d}_{p.chapter_id}.mp4"
        d = dur(seg)
        con = lufs(V2, off, d)
        sin = lufs(OUT / f"{TID}_final_gfx_no_music.mp4", off, d)
        f27 = lufs(F27, off, d)
        ti = (music_map.get(p.chapter_id) or {})
        caps.append({"cap": p.chapter_id, "intent": p.narrative_intent, "pista": ti.get("track_id"),
                     "matcher": ti.get("reasoning"), "ducked": ducked[p.chapter_id], "floor": floor[p.chapter_id],
                     "inicio_s": round(off, 2), "dur_s": round(d, 2), "I_sin_musica": sin["I"], "I_con_musica": con["I"],
                     "dif_LU": round(con["I"] - sin["I"], 2), "I_f27": f27["I"], "LRA_v2": con["LRA"],
                     "tramos": [t for t in (intensidad or {}).get(p.chapter_id, []) if t["nivel"] != "fondo"]})
        off += d
    tot = {"v2": lufs(V2), "sin_musica": lufs(OUT / f"{TID}_final_gfx_no_music.mp4"), "f27": lufs(F27)}
    res = {"salida": str(V2), "dur_v2": dur(V2), "dur_f27": dur(F27), "segundos_mezcla": round(t_mezcla, 1),
           "segundos_total": round(time.time() - t0, 1), "hw_encode": True, "total": tot,
           "dif_total_LU": round(tot["v2"]["I"] - tot["sin_musica"]["I"], 2), "caps": caps,
           "music_map": mm.get("tracks_by_chapter")}
    (LAB / "remezcla_vajont.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    for c in caps:
        print(f"[{c['cap']}] {c['intent']:<15} {c['pista']:<22} sin {c['I_sin_musica']:6.1f} · con "
              f"{c['I_con_musica']:6.1f} ({c['dif_LU']:+.2f} LU) · F27 {c['I_f27']:6.1f} · "
              f"{','.join(t['nivel'] for t in c['tramos']) or 'fondo'}")
    print(f"total: v2 {tot['v2']} · sin música {tot['sin_musica']} · F27 {tot['f27']} · Δ {res['dif_total_LU']} LU · "
          f"mezcla {t_mezcla:.0f} s · {res['dur_v2']:.1f} s de video")


if __name__ == "__main__":
    main()
