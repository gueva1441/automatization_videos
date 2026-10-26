"""F30 — render rápido sobre Vajont v3: misma decisión de bloques y transiciones, otro lugar donde se dibuja.

Copia del topic `f8s3-vajont-f30` (el patrón de F29 C/D: no pisa v3). Se reusa TODO lo que decide (API 0):
    imágenes, Veo, voz, música      assets/*.json, flow_plan, output/audio/<id>
    visual base (DepthFlow)         chNN_{flux_visual,hybrid_visual,flux_supp}.mp4 de v3 por HARDLINK (solo se leen)
    cachés de LLM y visión          plan crudo del director, intensidad, cajas de zoom, recortes del pool
                                    (gfx_pool_docs), crítico (gfx_critic_chNN.json), photo_details / zoom_verify
    planes resueltos de v3          para lo «ya mostrado» de los caps anteriores en las corridas de un cap
Uso:
    python -I lab/hyperframes/f30/f30_vajont.py cap ch06 <etiqueta> [--workers N]   (--only-cap, apartado con etiqueta)
    python -I lab/hyperframes/f30/f30_vajont.py todo                              (D: el video entero → _v3b.mp4)
Antes de cada render: Firefox cerrado y RAM libre > 14 GB (se aborta si no).
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / "lab" / "hyperframes" / "f26" / "b")]
LAB = Path(__file__).resolve().parent
SRC, DST = "f8s3-vajont-f29", "f8s3-vajont-f30"
OUT = ROOT / "output"
W_SRC, W_DST = OUT / SRC / "_fase2b_work", OUT / DST / "_fase2b_work"
LINK = ("_flux_visual.mp4", "_hybrid_visual.mp4", "_flux_supp.mp4")
CACHE = ("gfx_zoom_box_", "gfx_intensity_", "gfx_critic_ch", "gfx_pool_docs_", "gfx_question_")


def preparar() -> list[str]:
    hechos = []
    (OUT / DST / "assets").mkdir(parents=True, exist_ok=True)
    for f in (OUT / SRC / "assets").glob("*.json"):
        if not (OUT / DST / "assets" / f.name).exists():
            shutil.copy2(f, OUT / DST / "assets" / f.name)
            hechos.append(f"assets/{f.name}")
    if (OUT / SRC / "flow_plan.json").exists() and not (OUT / DST / "flow_plan.json").exists():
        shutil.copy2(OUT / SRC / "flow_plan.json", OUT / DST / "flow_plan.json")
    if not (OUT / "audio" / DST).exists():
        shutil.copytree(OUT / "audio" / SRC, OUT / "audio" / DST)
        hechos.append("audio/")
    sd = ROOT / "data" / "scripts"
    if not (sd / f"{DST}.json").exists():
        shutil.copy2(sd / f"{SRC}.json", sd / f"{DST}.json")
    W_DST.mkdir(parents=True, exist_ok=True)
    for f in W_SRC.iterdir():
        if not f.is_file() or (W_DST / f.name).exists():
            continue
        if f.name.endswith(LINK):
            os.link(f, W_DST / f.name)
            hechos.append(f"_fase2b_work/{f.name} (hardlink)")
        elif f.name.startswith(CACHE) or (f.name.startswith("gfx_plan_ch") and f.name.endswith(".json")):
            shutil.copy2(f, W_DST / f.name)
            hechos.append(f"_fase2b_work/{f.name}")
    return hechos


def _guardia() -> float:
    import f26b_produccion as f26b
    ram, ff = f26b._ram_free_gb(), f26b._firefox_open()
    print(f"antes: RAM libre {ram:.1f} GB · Firefox {'ABIERTO' if ff else 'cerrado'}", flush=True)
    if ff or ram <= 14:
        raise SystemExit("no arranca: Firefox abierto o RAM ≤ 14 GB (regla de Omar)")
    return ram


def _fase2b(args: list[str], out: Path, env_extra: dict[str, str] | None = None) -> tuple[int, float, float | None]:
    """fase2b en un proceso nuevo (runpy: `python -I fase2b.py` no ve el repo) + muestreo de RAM cada 5 s."""
    import f26b_produccion as f26b
    muestras: list[float] = []
    fin = threading.Event()

    def mon() -> None:
        while not fin.is_set():
            muestras.append(f26b._ram_free_gb())
            fin.wait(5)
    th = threading.Thread(target=mon, daemon=True)
    th.start()
    code = ("import sys, runpy; sys.path.insert(0, '.'); sys.argv = ['fase2b.py'] + sys.argv[1:]; "
            "runpy.run_path('fase2b.py', run_name='__main__')")
    t0 = time.time()
    with out.open("w", encoding="utf-8") as fh:
        r = subprocess.run([sys.executable, "-I", "-c", code, *args], cwd=ROOT, stdout=fh, stderr=subprocess.STDOUT,
                           env={**os.environ, "PYTHONIOENCODING": "utf-8", **(env_extra or {})})
    pared = time.time() - t0
    fin.set()
    th.join(timeout=10)
    return r.returncode, pared, (min(muestras) if muestras else None)


def cap(cap_id: str, etiqueta: str, workers: int | None = None) -> dict:
    """Un `--only-cap` con --gfx (el chNN_gfx.mp4 anterior se aparta antes: --reuse-visuals lo reusaría)."""
    _guardia()
    preparar()
    for f in (W_DST / f"{cap_id}_gfx.mp4", W_DST / f"gfx_{cap_id}.log"):
        if f.exists():
            bak = W_DST / "_bak" / f"{f.stem}__{int(time.time())}{f.suffix}"
            bak.parent.mkdir(exist_ok=True)
            f.replace(bak)
    for k in range(1, int(cap_id[2:])):                 # lo ya mostrado antes de este cap = lo de v3
        f = W_SRC / f"gfx_plan_ch{k:02d}.resolved.json"
        if f.exists():
            shutil.copy2(f, W_DST / f.name)
    extra = ["--gfx-workers", str(workers)] if workers else []
    rc, pared, ram_min = _fase2b([DST, "--only-cap", cap_id, "--reuse-visuals", "--gfx", "--gfx-sparse", "--gfx-quality",
                                  "looks", *extra], LAB / f"run_{cap_id}_{etiqueta}.out")
    dst = LAB / "corridas" / etiqueta
    dst.mkdir(parents=True, exist_ok=True)
    for f in (f"{cap_id}_gfx.mp4", f"gfx_{cap_id}.log", f"gfx_plan_{cap_id}.resolved.json", f"gfx_safe_bake_{cap_id}.json",
              f"gfx_sparse_{cap_id}.json"):
        if (W_DST / f).exists():
            (dst / f).unlink(missing_ok=True)
            if f.endswith(".mp4"):
                os.link(W_DST / f, dst / f)                 # hardlink: el mp4 de cada corrida queda apartado
            else:
                shutil.copy2(W_DST / f, dst / f)
    res = {"cap": cap_id, "etiqueta": etiqueta, "rc": rc, "pared_s": round(pared, 1), "ram_libre_min_gb":
           round(ram_min, 2) if ram_min else None, "workers": workers}
    (dst / f"{cap_id}_corrida.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(res, ensure_ascii=False), flush=True)
    return res


def todo() -> dict:
    """D: el video entero con --reuse-visuals --gfx --gfx-sparse (rotulista apagado, planes de v3 de caché)."""
    ram = _guardia()
    copiados = preparar()
    bak = W_DST / "_bak_antes_de_D"
    bak.mkdir(exist_ok=True)
    for f in list(W_DST.glob("ch*_gfx.mp4")) + list(W_DST.glob("gfx_ch*.log")) + list(W_DST.glob("ch*_segment*.mp4")):
        f.replace(bak / f.name)
    for f in W_DST.glob("gfx_plan_ch*.resolved.json"):          # D rehace los planes en orden (ya mostrado incluido)
        f.replace(bak / f.name)
    rc, pared, ram_min = _fase2b([DST, "--keep-segments", "--reuse-visuals", "--gfx", "--gfx-sparse", "--gfx-quality",
                                  "looks"], LAB / "d" / "fase2b_d.out")
    final = OUT / DST / f"{DST}_final_gfx.mp4"
    v3b = OUT / SRC / "f8s3-vajont_final_gfx_v3b.mp4"
    if rc == 0 and final.exists():
        final.replace(v3b)
        nm = OUT / DST / f"{DST}_final_gfx_no_music.mp4"
        if nm.exists():
            nm.replace(OUT / SRC / "f8s3-vajont_final_gfx_v3b_no_music.mp4")
    res = {"rc": rc, "pared_min": round(pared / 60, 1), "salida": str(v3b) if v3b.exists() else None,
           "bytes": v3b.stat().st_size if v3b.exists() else None, "ram_libre_antes_gb": round(ram, 1),
           "ram_libre_min_gb": round(ram_min, 2) if ram_min else None, "copiados": len(copiados)}
    (LAB / "d" / "vajont_v3b.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(res, ensure_ascii=False), flush=True)
    return res


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    (LAB / "d").mkdir(parents=True, exist_ok=True)
    if sys.argv[1] == "cap":
        w = int(sys.argv[sys.argv.index("--workers") + 1]) if "--workers" in sys.argv else None
        cap(sys.argv[2], sys.argv[3], w)
    elif sys.argv[1] == "todo":
        todo()
    elif sys.argv[1] == "preparar":
        print(len(preparar()), "copiados")
