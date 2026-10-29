# -*- coding: utf-8 -*-
"""F52 etapa 3 — medidas de los 8 clips con ffmpeg (skill ver-render), sin modelos ni fal:
- SSIM del primer cuadro contra la foto de arranque (`fotos/capNN.png`), los dos en gris a 1280×720;
- SSIM del último cuadro contra el primero (cuánto cambió la toma en 8 s);
- cortes: cuadros con `scene` > 0,4 (select + showinfo);
- congelados: `freezedetect` (ruido 0,001, ≥ 0,5 s);
- movimiento: media y máximo de la diferencia entre cuadros seguidos (`tblend=difference` + `signalstats` YAVG, 0–255);
- audio: si el mp4 trae pista (K y G no dejan apagarla; la hoja ciega va sin audio).
Salida: `MEDIDAS_CLIPS.md` (por clip, con el modelo: no es la hoja ciega).
Uso: python lab/hyperframes/f52/medidas_clips.py
"""
import json
import re
import statistics
import subprocess
import sys
from pathlib import Path

F52 = Path(__file__).resolve().parent
CLIPS = F52 / "clips"
MODELOS = {"K": "Kling 4.0", "S": "Seedance 2.5", "F": "FLUX 3 Max", "G": "Gemini Omni Flash 1.1"}
G720 = "scale=1280:720,format=gray"


def ff(args: list) -> str:
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", *map(str, args)], capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    return r.stderr


def ssim(a_args: list, b_args: list, fa: str, fb: str) -> float:
    err = ff([*a_args, *b_args, "-lavfi", f"[0:v]{fa}[a];[1:v]{fb}[b];[a][b]ssim", "-f", "null", "-"])
    m = re.search(r"All:([0-9.]+)", err)
    return round(float(m.group(1)), 4) if m else float("nan")


def medir(n: int, k: str) -> dict:
    p = CLIPS / f"cap{n:02d}_{k}.mp4"
    foto = F52 / "fotos" / f"cap{n:02d}.png"
    r = {"clip": p.name}
    r["ssim_primero_vs_foto"] = ssim(["-i", foto], ["-i", p], G720, f"select=eq(n\\,0),{G720}")
    r["ssim_ultimo_vs_primero"] = ssim(["-i", p], ["-sseof", "-0.1", "-i", p], f"select=eq(n\\,0),{G720}", G720)
    cortes = ff(["-i", p, "-vf", "select='gt(scene,0.4)',showinfo", "-f", "null", "-"])
    r["cortes_s"] = [round(float(t), 2) for t in re.findall(r"pts_time:([0-9.]+)", cortes)]
    fr = ff(["-i", p, "-vf", "freezedetect=n=0.001:d=0.5", "-f", "null", "-"])
    ini = [float(x) for x in re.findall(r"freeze_start: ([0-9.]+)", fr)]
    dur = [float(x) for x in re.findall(r"freeze_duration: ([0-9.]+)", fr)]
    r["congelados"] = [f"{a:.2f}s +{d:.2f}s" for a, d in zip(ini, dur)] + \
                      ([f"{ini[-1]:.2f}s hasta el final"] if len(ini) > len(dur) else [])
    mv = ff(["-i", p, "-vf", "format=gray,tblend=all_mode=difference,signalstats,metadata=print:key=lavfi.signalstats.YAVG",
             "-f", "null", "-"])
    ys = [float(x) for x in re.findall(r"lavfi\.signalstats\.YAVG=([0-9.]+)", mv)]
    r["mov_medio"] = round(statistics.mean(ys), 2) if ys else None
    r["mov_max"] = round(max(ys), 2) if ys else None
    pr = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type", "-of", "csv=p=0", str(p)],
                        capture_output=True, text=True).stdout
    r["audio"] = "audio" in pr
    return r


def main() -> int:
    res = {f"cap{n:02d}_{k}": medir(n, k) for n in (1, 7) for k in MODELOS if (CLIPS / f"cap{n:02d}_{k}.mp4").exists()}
    L = ["# MEDIDAS_CLIPS — los 8 clips de F52 medidos con ffmpeg (por modelo: NO es la hoja ciega)", "",
         "Salida de `python lab/hyperframes/f52/medidas_clips.py`.", "",
         "- **SSIM 1.º vs foto:** el primer cuadro contra la foto de arranque, en gris a 1280×720; 1 = idénticos.",
         "- **SSIM último vs 1.º:** cuánto cambió la toma en 8 s; más bajo, más cambio.",
         "- **Cortes:** cuadros con cambio de escena mayor a 0,4.",
         "- **Congelados:** tramos de 0,5 s o más sin cambio.",
         "- **Movimiento:** media y máximo de la diferencia entre cuadros seguidos, en escala 0–255.", "",
         "| clip | modelo | SSIM 1.º vs foto | SSIM último vs 1.º | cortes (s) | congelados | mov. medio | mov. máx | audio |",
         "|---|---|---|---|---|---|---|---|---|"]
    for c, r in res.items():
        k = c.split("_")[1]
        L += [f"| {c} | {k} {MODELOS[k]} | {r['ssim_primero_vs_foto']} | {r['ssim_ultimo_vs_primero']} | "
              f"{', '.join(map(str, r['cortes_s'])) or '—'} | {'; '.join(r['congelados']) or '—'} | {r['mov_medio']} | "
              f"{r['mov_max']} | {'sí (se descarta)' if r['audio'] else 'no'} |"]
    (F52 / "MEDIDAS_CLIPS.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    (CLIPS / "medidas.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print("\n".join(L[-len(res):]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
