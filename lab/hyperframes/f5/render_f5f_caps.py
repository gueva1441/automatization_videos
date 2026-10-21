"""F5f (cierre de laboratorio): re-render de la capa gfx SOLO de algunos caps de Orleans v2, uno por uno, con
fase2b --gfx --gfx-sparse --gfx-quality looks --reuse-visuals --only-cap. Antes de cada cap: Firefox cerrado y RAM
libre > 14 GB (si no, para). Respalda la capa y el plan anteriores del cap en _fase2b_work/_bak_f5f_pre/ (con
--reuse-visuals fase2b reusaría la capa vieja) y copia la hoja de contactos a lab/hyperframes/f5/produccion/hojas_f5f/.
Uso: PYTHONIOENCODING=utf-8 python lab/hyperframes/f5/render_f5f_caps.py ch02 ch05 ch06 ch07
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import time
from pathlib import Path

LAB = Path(__file__).resolve().parent
sys.path.insert(0, str(LAB))
import produccion_orleans_v2 as po  # noqa: E402

WORK = po.ROOT / "output" / po.V2 / "_fase2b_work"
BAK = WORK / "_bak_f5f_pre"
SHEETS = po.PROD / "hojas_f5f"


def main(caps: list[str]) -> int:
    BAK.mkdir(exist_ok=True)
    SHEETS.mkdir(exist_ok=True)
    log = po.PROD / "render_f5f.out"
    with log.open("a", encoding="utf-8") as fh:
        for cap in caps:
            ram, ff = po._ram_free_gb(), po._firefox_open()
            fh.write(f"[{time.strftime('%H:%M:%S')}] {cap}: RAM libre {ram:.1f} GB · Firefox {'ABIERTO' if ff else 'cerrado'}\n")
            fh.flush()
            if ff or ram <= 14:
                fh.write(f"  {cap}: NO arranca (regla de Omar: Firefox cerrado y RAM > 14 GB)\n")
                return 3
            for name in (f"{cap}_gfx.mp4", f"gfx_plan_{cap}.resolved.json", f"hoja_contactos_{cap}.jpg",
                         f"gfx_cues_{cap}.md"):
                src = WORK / name
                if src.exists() and not (BAK / name).exists():
                    (shutil.move if name.endswith("_gfx.mp4") else shutil.copy2)(str(src), str(BAK / name))
            (WORK / f"{cap}_gfx.mp4").unlink(missing_ok=True)
            t0 = time.time()
            r = subprocess.run([sys.executable, "fase2b.py", po.V2, "--reuse-visuals", "--gfx", "--gfx-sparse",
                                "--gfx-quality", "looks", "--only-cap", cap], cwd=po.ROOT, stdout=fh,
                               stderr=subprocess.STDOUT, text=True,
                               env={**__import__("os").environ, "PYTHONIOENCODING": "utf-8"})
            fh.write(f"[{time.strftime('%H:%M:%S')}] {cap}: rc={r.returncode} en {(time.time() - t0) / 60:.1f} min\n")
            fh.flush()
            sheet = WORK / f"hoja_contactos_{cap}.jpg"
            if sheet.exists():
                shutil.copy2(sheet, SHEETS / sheet.name)
            if r.returncode != 0:
                return r.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:] or ["ch02", "ch05", "ch06", "ch07"]))
