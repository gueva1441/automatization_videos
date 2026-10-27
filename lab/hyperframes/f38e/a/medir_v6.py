"""F38e §A.2: medir los 7 segmentos de v6 (solo lectura) contra el guion, gfx_escenas y gfx_pause, con fase2b._medir_cierre.
Correr desde la raíz: PYTHONIOENCODING=utf-8 python lab/hyperframes/f38e/a/medir_v6.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
import fase2b  # noqa: E402

T = ROOT / "output" / "f8s3-vajont-f30"
W = T / "_fase2b_work"
g = json.loads((T / "GUION_PANTALLA.json").read_text(encoding="utf-8"))
caps = {c["cap"]: c for c in g["caps"]}
fps = int(g["fps"])
print("| cap | seg_0N (ffprobe) | guion seg_dur | diferencia | gfx_escenas clip_dur / pausa | gfx_pause | plan: pause + black_hold | negro al cierre (blackdetect) |")
print("|---|---|---|---|---|---|---|---|")
for i in range(1, 8):
    cap = f"ch{i:02d}"
    seg = W / f"seg_{i:02d}_{cap}.mp4"
    esc = json.loads((W / f"gfx_escenas_{cap}.json").read_text(encoding="utf-8"))
    pz = json.loads((W / f"gfx_pause_{cap}.json").read_text(encoding="utf-8"))
    plan = json.loads((W / f"gfx_plan_{cap}.resolved.json").read_text(encoding="utf-8"))["plan"]
    cq, bh = plan.get("chapter_question") or {}, plan.get("black_hold") or {}
    m = fase2b._medir_cierre(seg, float(caps[cap]["seg_dur"]), float(bh.get("duration") or 0.0), fps)
    det = ", ".join(f"{t['black_start']:.3f}→{t['black_end']:.3f} ({t['black_duration']:.3f} s)" for t in m["negro_detectado"] or []) or "ninguno"
    print(f"| {cap} | {m['duracion_s']:.3f} | {caps[cap]['seg_dur']:.3f} | {m['duracion_s'] - caps[cap]['seg_dur']:+.3f} "
          f"{'✓' if m['duracion_ok'] else '✗'} | {esc['clip_dur']:.3f} / {esc['pausa']:.3f} | {pz['pause']:.3f} | "
          f"{float(cq.get('pause') or 0):.3f} + {float(bh.get('duration') or 0):.1f} (start {float(bh.get('start') or 0):.3f}) | "
          f"{'✓' if m['negro_ok'] else '✗'} {det} (d={m['blackdetect_d']}) |")
