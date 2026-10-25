"""F28 §C.4 — re-render completo de Vajont desde los assets (sin regenerar imágenes ni voz) con las tres variables de
C (NVENC por defecto, gfx de a 3 caps, clips con 6 workers) y la música de B; pared contra los 128.4 min de F27.

Para no pisar nada de F27 (su `_final_gfx.mp4`, segmentos y work_dir) se renderiza una COPIA del topic,
`f8s3-vajont-f28c`: mismo `assets_manifest.json` (las rutas son relativas y apuntan a las imágenes y clips de F27, que
se leen y no se tocan), mismo audio (`output/audio/`), mismo script (`data/scripts/`) y mismos pasos (`_steps/`). Sin
caché de flow_specs ni del director de gfx, igual que en F27 (los dos vuelven a correr).
Antes: Firefox cerrado (cierre normal) y RAM libre > 14 GB. Durante: RAM y VRAM cada 10 s.
Uso: PYTHONIOENCODING=utf-8 python -I lab/hyperframes/f28/c/f28c_rerender.py
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path[:0] = [str(ROOT), str(ROOT / "lab" / "hyperframes" / "f26" / "b")]
LAB = Path(__file__).resolve().parent
SRC, DST = "f8s3-vajont", "f8s3-vajont-f28c"


def preparar() -> None:
    o, a = ROOT / "output", ROOT / "output" / "audio"
    (o / DST / "assets").mkdir(parents=True, exist_ok=True)
    shutil.copy2(o / SRC / "assets" / "assets_manifest.json", o / DST / "assets" / "assets_manifest.json")
    if not (a / DST).exists():
        shutil.copytree(a / SRC, a / DST)
    sd = ROOT / "data" / "scripts"
    shutil.copy2(sd / f"{SRC}.json", sd / f"{DST}.json")
    if not (sd / "_steps" / DST).exists():
        shutil.copytree(sd / "_steps" / SRC, sd / "_steps" / DST, ignore=shutil.ignore_patterns("fuentes", "_r3_cache",
                                                                                                "_pre_f26"))


def vram_mb() -> int | None:
    r = subprocess.run(["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
                       capture_output=True, text=True)
    try:
        return int(r.stdout.strip().splitlines()[0])
    except (ValueError, IndexError):
        return None


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    import f26b_produccion as f26b
    ram, ff = f26b._ram_free_gb(), f26b._firefox_open()
    print(f"antes: RAM libre {ram:.1f} GB · Firefox {'ABIERTO' if ff else 'cerrado'}", flush=True)
    if ff or ram <= 14:
        raise SystemExit("no arranca: Firefox abierto o RAM ≤ 14 GB (regla de Omar)")
    preparar()
    muestras: list[dict] = []
    fin = threading.Event()

    def monitor() -> None:
        t0 = time.time()
        while not fin.is_set():
            muestras.append({"t": round(time.time() - t0), "ram_libre_gb": round(f26b._ram_free_gb(), 2),
                             "vram_mb": vram_mb()})
            fin.wait(10)
    th = threading.Thread(target=monitor, daemon=True)
    th.start()
    t0 = time.time()
    with (LAB / "fase2b.out").open("w", encoding="utf-8") as fh:
        r = subprocess.run([sys.executable, "fase2b.py", DST, "--keep-segments", "--gfx", "--gfx-sparse",
                            "--gfx-quality", "looks"], cwd=ROOT, stdout=fh, stderr=subprocess.STDOUT, text=True,
                           env={**__import__("os").environ, "PYTHONIOENCODING": "utf-8"})
    pared = time.time() - t0
    fin.set()
    th.join(timeout=15)
    rams = [m["ram_libre_gb"] for m in muestras]
    vrams = [m["vram_mb"] for m in muestras if m["vram_mb"] is not None]
    res = {"rc": r.returncode, "pared_min": round(pared / 60, 1), "f27_pared_min": 128.4,
           "ram_libre_min_gb": min(rams) if rams else None, "vram_max_mb": max(vrams) if vrams else None,
           "muestras": muestras}
    (LAB / "rerender.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"rc={r.returncode} · pared {pared / 60:.1f} min (F27: 128.4) · RAM libre mínima {res['ram_libre_min_gb']} GB · "
          f"VRAM máxima {res['vram_max_mb']} MB", flush=True)


if __name__ == "__main__":
    main()
