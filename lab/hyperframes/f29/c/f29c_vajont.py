"""F29 §C — Vajont con el realizador: SOLO la capa gfx. Copia del topic, `f8s3-vajont-f29` (el patrón de F28 C: no pisa
nada). Se reusan:
    imágenes y clips Veo     el `assets_manifest.json` de F27 (rutas relativas a las imágenes de F27, que solo se leen)
    visual base (DepthFlow)  `chNN_flux_visual/hybrid_visual/flux_supp.mp4` del work de F27 → `--reuse-visuals`
    voz, música, intensidad  `output/audio/f8s3-vajont/` (F28: paleta y mapa de intensidad)
    cachés de LLM/visión     flow_specs, photo_details/zoom_verify, gfx_zoom_box, gfx_intensity y el plan crudo del
                             director (gfx_plan_chNN.json): misma narración, misma decisión
Lo que se rehace: el realizador (ventanas, candidatos, pool docs con Flash, topes, pico, pregunta), el crítico, el
render de la capa gfx (en fila, NVENC cq 23, timeout del render 1500 s) y el ensamble.
Antes: Firefox cerrado y RAM libre > 14 GB. Salida: output/f8s3-vajont-f29/f8s3-vajont_final_gfx_v3.mp4.
Uso: PYTHONIOENCODING=utf-8 python -I lab/hyperframes/f29/c/f29c_vajont.py
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
SRC, DST = "f8s3-vajont", "f8s3-vajont-f29"
REUSO_WORK = ("_flux_visual.mp4", "_hybrid_visual.mp4", "_flux_supp.mp4")
REUSO_CACHE = ("gfx_zoom_box_", "gfx_intensity_")


def preparar() -> list[str]:
    o, a = ROOT / "output", ROOT / "output" / "audio"
    hechos = []
    (o / DST / "assets").mkdir(parents=True, exist_ok=True)
    for f in (o / SRC / "assets").glob("*.json"):
        shutil.copy2(f, o / DST / "assets" / f.name)
        hechos.append(f"assets/{f.name}")
    if (o / SRC / "flow_plan.json").exists():
        shutil.copy2(o / SRC / "flow_plan.json", o / DST / "flow_plan.json")
    if not (a / DST).exists():
        shutil.copytree(a / SRC, a / DST)
        hechos.append("audio/")
    sd = ROOT / "data" / "scripts"
    shutil.copy2(sd / f"{SRC}.json", sd / f"{DST}.json")
    w_src, w_dst = o / SRC / "_fase2b_work", o / DST / "_fase2b_work"
    w_dst.mkdir(parents=True, exist_ok=True)
    for f in w_src.iterdir():
        if f.is_file() and (f.name.endswith(REUSO_WORK) or f.name.startswith(REUSO_CACHE)
                            or (f.name.startswith("gfx_plan_ch") and f.name.endswith(".json")
                                and not f.name.endswith(".resolved.json"))):
            if not (w_dst / f.name).exists():
                shutil.copy2(f, w_dst / f.name)
                hechos.append(f"_fase2b_work/{f.name}")
    return hechos


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    import f26b_produccion as f26b
    ram, ff = f26b._ram_free_gb(), f26b._firefox_open()
    print(f"antes: RAM libre {ram:.1f} GB · Firefox {'ABIERTO' if ff else 'cerrado'}", flush=True)
    if ff or ram <= 14:
        raise SystemExit("no arranca: Firefox abierto o RAM ≤ 14 GB (regla de Omar)")
    copiados = preparar()
    muestras: list[dict] = []
    fin = threading.Event()

    def monitor() -> None:
        t0 = time.time()
        while not fin.is_set():
            muestras.append({"t": round(time.time() - t0), "ram_libre_gb": round(f26b._ram_free_gb(), 2)})
            fin.wait(15)
    th = threading.Thread(target=monitor, daemon=True)
    th.start()
    t0 = time.time()
    with (LAB / "fase2b.out").open("w", encoding="utf-8") as fh:
        r = subprocess.run([sys.executable, "fase2b.py", DST, "--keep-segments", "--reuse-visuals", "--gfx",
                            "--gfx-sparse", "--gfx-quality", "looks"], cwd=ROOT, stdout=fh, stderr=subprocess.STDOUT,
                           text=True, env={**__import__("os").environ, "PYTHONIOENCODING": "utf-8"})
    pared = time.time() - t0
    fin.set()
    th.join(timeout=20)
    out = ROOT / "output" / DST
    final = out / f"{DST}_final_gfx.mp4"
    v3 = out / f"{SRC}_final_gfx_v3.mp4"
    if r.returncode == 0 and final.exists():
        final.replace(v3)
        nm = out / f"{DST}_final_gfx_no_music.mp4"
        if nm.exists():
            nm.replace(out / f"{SRC}_final_gfx_v3_no_music.mp4")
    res = {"rc": r.returncode, "pared_min": round(pared / 60, 1), "salida": str(v3) if v3.exists() else None,
           "bytes": v3.stat().st_size if v3.exists() else None,
           "ram_libre_min_gb": min((m["ram_libre_gb"] for m in muestras), default=None), "copiados": copiados}
    (LAB / "vajont_v3.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in res.items() if k != "copiados"}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
