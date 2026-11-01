"""F68b Etapa 2: primer cuadro y cuadro del medio de cada clip nuevo como png, y ssim contra las fotos. Sin llamadas pagas.
Control: el clip viejo contra la foto nueva (debe parecerse poco) y contra su foto vieja archivada (debe parecerse mucho)."""
import json
import os
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
os.chdir(RAIZ)
sys.path.insert(0, str(RAIZ))

import asset_manager as am  # noqa: E402

TOPIC = "123bbb64-9fca-4395-8bf4-57d60e219ef1"
AQUI = Path(__file__).resolve().parent
TOPIC_DIR = am.OUTPUT_DIR / TOPIC
ASSETS = TOPIC_DIR / "assets"
ARCHIVO = TOPIC_DIR / "_archivo_seedream5lite"


def cuadro(clip: Path, out: Path, *, seg: float | None = None, ultimo: bool = False) -> Path:
    if ultimo:
        args = ["-sseof", "-0.25", "-i", str(clip), "-update", "1"]
    elif seg is None:
        args = ["-i", str(clip), "-vf", "select=eq(n\\,0)", "-vsync", "0", "-frames:v", "1"]
    else:
        args = ["-ss", f"{seg:.3f}", "-i", str(clip), "-frames:v", "1"]
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *args, str(out)], check=True)
    return out


def main() -> None:
    salida = {}
    for cap in ("ch01", "ch07"):
        veo = ASSETS / f"{cap}_veo"
        nuevo, viejo = veo / f"{cap}_clip_01.mp4", ARCHIVO / "clips" / f"{cap}_clip_01.mp4"
        foto, final = veo / f"{cap}_img_01.png", veo / f"{cap}_img_01_final.png"
        foto_vieja = ARCHIVO / f"{cap}_veo" / f"{cap}_img_01.png"
        med = am._clip_ffprobe(nuevo)
        primero = cuadro(nuevo, AQUI / f"{cap}_nuevo_primer_cuadro.png")
        medio = cuadro(nuevo, AQUI / f"{cap}_nuevo_cuadro_medio.png", seg=med["segundos"] / 2)
        ultimo = cuadro(nuevo, AQUI / f"{cap}_nuevo_ultimo_cuadro.png", ultimo=True)
        primero_viejo = cuadro(viejo, AQUI / f"{cap}_viejo_primer_cuadro.png")
        salida[cap] = {
            "clip_nuevo": med, "clip_viejo": am._clip_ffprobe(viejo),
            # la foto se escala al tamaño del cuadro: `_ssim(a, b)` lleva b al tamaño de a
            "ssim_nuevo_vs_foto_nueva": am._ssim(primero, foto),
            "ssim_viejo_vs_foto_nueva": am._ssim(primero_viejo, foto),
            "ssim_viejo_vs_foto_vieja": am._ssim(primero_viejo, foto_vieja),
            "ssim_ultimo_nuevo_vs_foto_final": am._ssim(ultimo, final),
        }
    (AQUI / "verificacion_clips.json").write_text(json.dumps(salida, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(salida, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
