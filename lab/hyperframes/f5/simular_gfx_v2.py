"""F5f: simulación de la capa gfx de Orleans v2 SIN render (apply_gfx plan_only) sobre los clips visuales reales, en
output/ba6c3cac-f5v2/_sim_gfx/ (no toca _fase2b_work). Copia los cachés del director (intensidad, preguntas, zoom,
crítico, pool) para no re-llamar lo que no cambió; los planes resueltos se rehacen en orden (ch01 → ch07: el dedupe
entre caps lee los anteriores). Escribe un resumen por cap en lab/hyperframes/f5/produccion/SIM_F5f.md.
Uso: PYTHONIOENCODING=utf-8 python lab/hyperframes/f5/simular_gfx_v2.py
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

V2 = "ba6c3cac-f5v2"
OUT = ROOT / "output" / V2
WORK = OUT / "_fase2b_work"
SIM = OUT / "_sim_gfx"
REPORT = Path(__file__).resolve().parent / "produccion" / "SIM_F5f.md"
CACHES = ("gfx_intensity_", "gfx_question_", "gfx_zoom_box_", "gfx_critic_", "gfx_pool_docs_", "gfx_plan_")


def _plans():
    import fase2b
    audio_dir = fase2b.OUTPUT_DIR / "audio" / V2
    sync_map = json.loads((audio_dir / "sync_map.json").read_text(encoding="utf-8"))
    manifest = json.loads((OUT / "assets" / "assets_manifest.json").read_text(encoding="utf-8"))
    return fase2b._build_plans(sync_map, manifest, V2, audio_dir, fase2b._load_script_lookup(V2))


def _base(plan) -> Path:
    cap = plan.chapter_id
    for name in (f"{cap}_hybrid_visual.mp4", f"{cap}_flux_visual.mp4"):
        if (WORK / name).exists():
            return WORK / name
    supp = WORK / f"{cap}_flux_supp.mp4"           # híbrido borrado: Veo + supp, sin DepthFlow
    out = SIM / f"{cap}_hybrid_visual.mp4"
    if not out.exists() and supp.exists():
        clips = [plan.asset_paths[0], supp] if plan.veo_position == "start" else [supp, plan.asset_paths[0]]
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(clips[0]), "-i", str(clips[1]), "-filter_complex",
                        "[0:v]scale=2560:1440,fps=30,setsar=1[a];[1:v]scale=2560:1440,fps=30,setsar=1[b];"
                        "[a][b]concat=n=2:v=1:a=0[v]", "-map", "[v]", "-c:v", "libx264", "-preset", "ultrafast",
                        "-crf", "18", str(out)], check=True)
    return out


def main() -> None:
    from script_engine.gfx_layer import apply_gfx
    SIM.mkdir(exist_ok=True)
    for f in WORK.glob("gfx_*.json"):
        if f.name.startswith(CACHES) and not f.name.endswith(".resolved.json"):
            shutil.copy2(f, SIM / f.name)
    for f in SIM.glob("gfx_plan_ch*.resolved.json"):
        f.unlink()
    for f in SIM.glob("gfx_ch*.log"):
        f.unlink()
    lines = ["# Simulación F5f de la capa gfx (plan_only, sin render)", ""]
    for plan in _plans():
        cap = plan.chapter_id
        apply_gfx(_base(plan), plan, V2, SIM, width=2560, height=1440, fps=30, quality="looks", sparse=True,
                  plan_only=True)
        rp = SIM / f"gfx_plan_{cap}.resolved.json"
        if not rp.exists():
            lines += [f"## {cap}: SIN PLAN (ver {SIM / f'gfx_{cap}.log'})", ""]
            continue
        p = json.loads(rp.read_text(encoding="utf-8"))["plan"]
        log = (SIM / f"gfx_{cap}.log").read_text(encoding="utf-8").splitlines()
        lines.append(f"## {cap}")
        for a in p.get("archive_clippings") or []:
            lines.append(f"- recorte {a['pool_id']}{' (reservado)' if a.get('reserved') else ''} @ {a['start']:.1f}s: "
                         f"«{a['headline']}» · {a.get('kicker')}")
        if p.get("quote_card"):
            q = p["quote_card"]
            lines.append(f"- cita {q['pool_id']} @ {q['start']:.1f}s ({q['duration']:.1f} s): «{q['text']}» — {q['author']}")
        for e in p.get("emphasis") or []:
            lines.append(f"- sello «{e['word']}» ({e['category']}, peso {e.get('weight')}) @ {e['start']:.1f}s"
                         + (f" + ícono {e['icon']}" if e.get("icon") else "") + (" [pico]" if e.get("peak_word") else ""))
        for k in ("count_up", "water_level", "evidence_zoom", "chapter_question"):
            if p.get(k):
                b = p[k]
                lines.append(f"- {k} @ {float(b.get('start', 0)):.1f}s: "
                             f"{b.get('value_text') or b.get('text') or b.get('anchor') or ''} {b.get('unit') or ''}".rstrip())
        for c in p.get("callouts") or []:
            lines.append(f"- dato @ {c['start']:.1f}s: «{c['text']}»")
        for f in p.get("fragmentos") or []:
            if f.get("ahora") is None and f.get("motivo"):
                lines.append(f"- fuera {f.get('id')} ({f.get('bloque')}): {f['motivo']}")
        lines += [f"- log: {x.strip()}" for x in log if any(k in x for k in ("reservad", "cita ", "desplaza", "pico:",
                                                                               "nivel de agua", "contador"))]
        lines.append("")
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
