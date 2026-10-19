"""F2b §4 — medición sobre los 7 segmentos reales de F2 (Orleans): concat por ventanas vs el concat de hoy.

Referencia: <id>_final_gfx_no_music.mp4 de F2 (xfade encadenado sobre los mismos segmentos; seg_04 se rehízo
después → el tramo de ch04 se excluye del PSNR). Mide tiempo, frames, PSNR Y/total global y sin ch04.
Uso: python lab/hyperframes/f2b/measure_concat_f2segs.py
"""
import json
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from script_engine import transition_applier as ta  # noqa: E402

VID = "ba6c3cac-a091-41c0-8dad-afd2f4364747"
OUT = ROOT / "output" / VID
WORK = OUT / "_fase2b_work"
FF, FP = shutil.which("ffmpeg"), shutil.which("ffprobe")
script = json.loads((ROOT / "data" / "scripts" / f"{VID}.json").read_text(encoding="utf-8"))
profiles = [c.get("art_profile") for c in script["chapters"]]
segs = sorted(WORK.glob("seg_0*_ch0*.mp4"))
tmp = WORK / "_measure_cw"
tmp.mkdir(exist_ok=True)
new = tmp / "new_no_music.mp4"
t0 = time.time()
ta.concat_windowed(segs, new, tmp, profiles, FF, FP, ["-c:v", "libx264"])
t_cw = time.time() - t0
ref = OUT / f"{VID}_final_gfx_no_music.mp4"


def frames(p):
    r = subprocess.run([FP, "-v", "error", "-select_streams", "v:0", "-count_packets", "-show_entries",
                        "stream=nb_read_packets", "-of", "csv=p=0", str(p)], capture_output=True, text=True)
    return int(r.stdout.strip())


infos = [ta.probe_segment(s, FP) for s in segs]
plans = ta.build_transition_plan(len(segs), profiles)
trans = [round(max(p.duration_seconds, 1 / 30) * 30) / 30 for p in plans]
start4 = sum(i.duration for i in infos[:3]) - sum(trans[:3])
end4 = start4 + infos[3].duration
stats = tmp / "psnr.txt"
t1 = time.time()
r = subprocess.run([FF, "-i", str(new), "-i", str(ref), "-lavfi", f"[0:v][1:v]psnr=stats_file={stats.name}",
                    "-f", "null", "-"], capture_output=True, text=True, cwd=tmp)
t_psnr = time.time() - t1
glob_y = re.search(r"PSNR y:([\d.inf]+)", r.stderr).group(1)
glob_all = re.search(r"average:([\d.inf]+)", r.stderr).group(1)
ys, alls = [], []
for i, ln in enumerate(stats.read_text().splitlines()):
    t = i / 30
    if start4 - 0.5 <= t <= end4 + 0.5:
        continue
    d = dict(kv.split(":") for kv in ln.split() if ":" in kv)
    ys.append(float(d["mse_y"]))
    alls.append(float(d["mse_avg"]))
import math  # noqa: E402
ps = lambda mse: 99.0 if mse == 0 else 10 * math.log10(255 ** 2 / mse)  # noqa: E731
res = {"concat_windowed_sec": round(t_cw, 1), "frames_new": frames(new), "frames_ref": frames(ref),
       "psnr_global_y": glob_y, "psnr_global_avg": glob_all,
       "psnr_sin_ch04_y": round(ps(sum(ys) / len(ys)), 2), "psnr_sin_ch04_avg": round(ps(sum(alls) / len(alls)), 2),
       "ch04_excluido_s": [round(start4, 2), round(end4, 2)], "psnr_calc_sec": round(t_psnr, 1)}
print(json.dumps(res, indent=1))
(ROOT / "lab" / "hyperframes" / "f2b" / "measure_concat_f2segs.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
