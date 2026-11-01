"""La función que usa fase2b, sin correr fase2b: duraciones por cap con las rutas reales."""
import json
import os
import sys
from pathlib import Path
RAIZ = Path(r"C:\CLAUDE_PROJECTS\automatization_videos")
os.chdir(RAIZ)
sys.path.insert(0, str(RAIZ))
import fase2b
T = "123bbb64-9fca-4395-8bf4-57d60e219ef1"
s = json.loads((RAIZ / "data" / "scripts" / f"{T}.json").read_text(encoding="utf-8"))
for ch in s["chapters"]:
    n = ch["chapter_number"]
    its = ch.get("image_prompts") or ch.get("supplemental_image_prompts")
    an = [i["narration_anchor"].strip() for i in its if isinstance(i, dict)]
    tp = RAIZ / "output" / "audio" / T / f"ch{n:02d}_timestamps.json"
    w = json.loads(tp.read_text(encoding="utf-8"))
    w = w if isinstance(w, list) else w["words"]
    total = float(w[-1]["end"])
    clip = fase2b._get_duration(RAIZ / "output" / T / "assets" / f"ch{n:02d}_veo" / f"ch{n:02d}_clip_01.mp4") if n in (1, 7) else 0.0
    off = clip if n == 1 else 0.0
    tot = total - clip
    d = fase2b._compute_durations_from_anchors(an, tp, tot, start_offset_sec=off)
    print(f"ch{n:02d}: {'None (uniforme)' if d is None else f'{len(d)} duraciones, mín {min(d):.2f} s, máx {max(d):.2f} s, suma {sum(d):.2f} de {tot:.2f}'}")
