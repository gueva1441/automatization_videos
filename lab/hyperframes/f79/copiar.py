"""F79: copia los archivos del guion de pantalla de Wittenoom a lab/hyperframes/f79/<dest>/.

Uso: python lab/hyperframes/f79/copiar.py <dest>   (antes | 0 | a1 | a2)
"""
import glob
import os
import shutil
import sys

TID = "123bbb64-9fca-4395-8bf4-57d60e219ef1"
RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
OUT = os.path.join(RAIZ, "output", TID)
WORK = os.path.join(OUT, "_fase2b_work")
PATRONES = ["gfx_plan_ch*.resolved.json", "gfx_escenas_ch*.json", "gfx_sfx_ch*.json",
            "gfx_critic_rot_ch*.json", "gfx_ch*.log"]


def main(dest):
    d = os.path.join(os.path.dirname(os.path.abspath(__file__)), dest)
    os.makedirs(os.path.join(d, "_fase2b_work"), exist_ok=True)
    n = 0
    for f in ("GUION_PANTALLA.json", "GUION_PANTALLA.md"):
        shutil.copy2(os.path.join(OUT, f), os.path.join(d, f))
        n += 1
    for p in PATRONES:
        for f in sorted(glob.glob(os.path.join(WORK, p))):
            shutil.copy2(f, os.path.join(d, "_fase2b_work", os.path.basename(f)))
            n += 1
    print(f"{n} archivos -> {d}")


if __name__ == "__main__":
    main(sys.argv[1])
