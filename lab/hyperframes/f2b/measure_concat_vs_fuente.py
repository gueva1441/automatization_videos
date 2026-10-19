"""F2b §4 — PSNR contra la FUENTE (seg_02_ch02.mp4) del final viejo (xfade encadenado de F2) y del nuevo
(concat por ventanas, salida de measure_concat_f2segs.py). Guarda measure_concat_vs_fuente.json.

ch02 empieza en el final en d(ch01) − t(ch01→ch02) = 35.5 s. Tramos:
  5–60 s del segmento  → incluye la ventana de entrada (keyframe 8.3 s) + cuerpo
  20–60 s del segmento → cuerpo puro (copia en el nuevo)
ch04 se excluye en la otra medición porque seg_04 se rehízo (02:51) después del final viejo (02:44).
"""
import json
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
VID = "ba6c3cac-a091-41c0-8dad-afd2f4364747"
W = ROOT / "output" / VID / "_fase2b_work"
FF = shutil.which("ffmpeg")
OFF = 35.5
SRC = W / "seg_02_ch02.mp4"
FILES = {"viejo_xfade_encadenado": ROOT / "output" / VID / f"{VID}_final_gfx_no_music.mp4",
         "nuevo_por_ventanas": W / "_measure_cw" / "new_no_music.mp4"}
res: dict = {"fuente": SRC.name, "ch02_inicio_en_final_s": OFF}
for name, f in FILES.items():
    for a, b in ((5, 60), (20, 60)):
        r = subprocess.run([FF, "-i", str(f), "-i", str(SRC), "-lavfi",
                            f"[0:v]trim=start={OFF + a}:end={OFF + b},setpts=PTS-STARTPTS[x];"
                            f"[1:v]trim=start={a}:end={b},setpts=PTS-STARTPTS[y];[x][y]psnr", "-f", "null", "-"],
                           capture_output=True, text=True, timeout=900)
        m = re.search(r"PSNR y:([\d.inf]+) u:([\d.inf]+) v:([\d.inf]+) average:([\d.inf]+)", r.stderr)
        res[f"{name}_s{a}-{b}"] = {"y": m.group(1), "u": m.group(2), "v": m.group(3), "avg": m.group(4)}
print(json.dumps(res, indent=1))
(Path(__file__).with_suffix(".json")).write_text(json.dumps(res, indent=1), encoding="utf-8")
