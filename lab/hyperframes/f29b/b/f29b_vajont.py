"""F29b §B — Vajont con el rotulista, ya con el render rápido de F30: planes de los 7 caps y render de ch03 y ch06.

Sobre la copia `f8s3-vajont-f30` ya cocida (la de F30 D; pedido de Omar): imágenes, Veo, voz, música, intensidad,
visual base (hardlink) y cachés de visión y del director. Los planes resueltos de v3b se apartan como
`gfx_plan_chNN.resolved.v3b.json`; las crudas de ch03 y ch06 de la parte A (misma entrada) se reusan. Se rehacen el rotulista (los 7 caps en paralelo:
7 llamadas, tope Claude = 2 − lo gastado en A), el plan de cada cap EN ORDEN (plan_only: lo ya mostrado sale del cap
anterior) con el crítico nuevo, y el render `--only-cap ch03` y `--only-cap ch06` en fila (`fase2b --rotulista`).
Antes de cada render: Firefox cerrado y RAM libre > 14 GB.
Uso: python -I lab/hyperframes/f29b/b/f29b_vajont.py planes | render ch03 | render ch06
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path[:0] = [str(ROOT), str(ROOT / "lab" / "hyperframes" / "f30"), str(ROOT / "lab" / "hyperframes" / "f26" / "b")]
LAB = Path(__file__).resolve().parent
SRC, DST = "f8s3-vajont-f29", "f8s3-vajont-f30"
A_COSTOS = LAB.parent / "a" / "rotulista_costos.json"
TOPE_TANDA = 2.0


def _f30():
    import f30_vajont as f
    f.DST = DST
    f.W_DST = ROOT / "output" / DST / "_fase2b_work"
    f.LAB = LAB
    return f


def _gemini() -> float:
    from cost_tracker import cost_tracker
    return sum(e.total_cost for e in cost_tracker._all_entries() if "gemini" in e.service.lower())


def planes() -> dict:
    f = _f30()
    wd = f.W_DST
    for p in wd.glob("gfx_plan_ch*.resolved.json"):          # lo ya mostrado lo deciden ESTOS planes, no los de v3b
        dst = p.with_name(p.name.replace(".resolved.json", ".resolved.v3b.json"))
        if not dst.exists():
            p.rename(dst)
    import shutil
    for cap in ("ch03", "ch06"):                              # las crudas de la parte A: misma entrada, ya pagadas
        src = LAB.parent / "a" / f"rotulista_{cap}.raw.json"
        if src.exists() and not (wd / src.name).exists():
            shutil.copy2(src, wd / src.name)
    import fase2b
    from config import OUTPUT_DIR
    from gfx_config import gfx_rules
    from script_engine import gfx_intensity
    from script_engine import gfx_rotulista as gro
    from script_engine.gfx_layer import apply_gfx
    gfx_intensity.record_proposals = lambda *a, **k: []      # no toca gfx_profiles/
    object.__setattr__(gfx_rules, "rotulista", True)
    object.__setattr__(gfx_rules, "garantizar_pico", False)
    gastado_a = json.loads(A_COSTOS.read_text(encoding="utf-8"))["usd"]
    tope = round(TOPE_TANDA - gastado_a, 4)
    object.__setattr__(gfx_rules, "rotulista_tope_usd", tope)
    ad = OUTPUT_DIR / "audio" / DST
    plans = fase2b._build_plans(json.loads((ad / "sync_map.json").read_text(encoding="utf-8")),
                                json.loads((OUTPUT_DIR / DST / "assets" / "assets_manifest.json").read_text(encoding="utf-8")),
                                DST, ad, fase2b._load_script_lookup(DST))
    t0 = time.time()
    pre = gro.prefetch(plans, DST, wd, {p.chapter_id: 0.0 for p in plans}, tope=tope)
    t_pre = time.time() - t0
    print(f"rotulista (7 en paralelo): {t_pre:.1f}s {pre}", flush=True)
    g0 = _gemini()
    tiempos = {}
    for p in plans:                                           # en orden: lo ya mostrado sale del cap anterior
        base = next(x for x in (wd / f"{p.chapter_id}_flux_visual.mp4", wd / f"{p.chapter_id}_hybrid_visual.mp4")
                    if x.exists())
        t = time.time()
        apply_gfx(base, p, DST, wd, width=2560, height=1440, fps=30, quality="looks", plan_only=True)
        tiempos[p.chapter_id] = round(time.time() - t, 1)
        print(f"plan {p.chapter_id}: {tiempos[p.chapter_id]}s", flush=True)
    res = {"tope_claude": tope, "gastado_a": gastado_a, "rotulista_paralelo_s": round(t_pre, 1), "prefetch": pre,
           "plan_only_s": tiempos, "gemini_usd": round(_gemini() - g0, 4),
           "claude_usd_b": json.loads((wd / "rotulista_costos.json").read_text(encoding="utf-8"))["usd"]
           if (wd / "rotulista_costos.json").exists() else 0.0}
    (LAB / "planes.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(res, ensure_ascii=False), flush=True)
    return res


def render(cap: str) -> dict:
    f = _f30()
    f._guardia()
    wd = f.W_DST
    for x in (wd / f"{cap}_gfx.mp4", wd / f"gfx_{cap}.log"):
        if x.exists():
            bak = wd / "_bak" / f"{x.stem}__{int(time.time())}{x.suffix}"
            bak.parent.mkdir(exist_ok=True)
            x.replace(bak)
    assert (wd / f"rotulista_{cap}.raw.json").exists(), "sin la cruda del rotulista: correr `planes` antes"
    planes_j = json.loads((LAB / "planes.json").read_text(encoding="utf-8"))
    queda = round(planes_j["tope_claude"] - planes_j["claude_usd_b"], 4)
    rc, pared, ram_min = f._fase2b([DST, "--only-cap", cap, "--reuse-visuals", "--gfx", "--gfx-sparse", "--gfx-quality",
                                    "looks", "--rotulista", "--rotulista-tope", str(queda)], LAB / f"render_{cap}.out")
    log = (wd / f"gfx_{cap}.log").read_text(encoding="utf-8")
    import re
    blk = log.split("\n[")[-1]
    g = lambda pat: (re.findall(pat, blk) or [None])[-1]         # noqa: E731
    res = {"cap": cap, "rc": rc, "pared_s": round(pared, 1), "ram_libre_min_gb": round(ram_min, 2) if ram_min else None,
           "gfx_total_s": g(r"OK total ([\d.]+)s"), "hf_s": g(r"6 lint \+ render looks \(sparse\): ([\d.]+)s"),
           "bake_s": g(r"4b safe bake \(ffmpeg\): ([\d.]+)s"), "stitch_s": g(r"7 stitch \+ grade FFmpeg: ([\d.]+)s"),
           "cobertura": g(r"sparse: \d+ ventanas, ([\d.]+s de [\d.]+s \(\d+ %\))")}
    (LAB / f"render_{cap}.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(res, ensure_ascii=False), flush=True)
    return res


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    os.chdir(ROOT)
    if sys.argv[1] == "planes":
        planes()
    elif sys.argv[1] == "render":
        render(sys.argv[2])
