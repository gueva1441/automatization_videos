"""F30 — ¿el plan resuelto de una corrida es el de v3? (bloques, textos, tiempos y transiciones; se ignoran los campos
de caché/log del crítico). Uso: python -I lab/hyperframes/f30/f30_planes.py <work_dir_nuevo> [ch01 ch02 …]"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
V3 = ROOT / "output" / "f8s3-vajont-f29" / "_fase2b_work"
CLAVES = ("title_card", "callouts", "count_up", "archive_clippings", "evidence_zoom", "punch_in", "chapter_question",
          "icon_array", "emphasis", "quote_card", "water_level", "time_ticker", "black_hold", "transitions", "pico",
          "outro_bug")


def limpio(x):
    if isinstance(x, dict):
        return {k: limpio(v) for k, v in x.items() if k not in ("cache",)}
    if isinstance(x, list):
        return [limpio(v) for v in x]
    return x


def comparar(nuevo: Path, cap: str) -> dict:
    a = json.loads((V3 / f"gfx_plan_{cap}.resolved.json").read_text(encoding="utf-8"))["plan"]
    b = json.loads((nuevo / f"gfx_plan_{cap}.resolved.json").read_text(encoding="utf-8"))["plan"]
    dif = [k for k in CLAVES if limpio(a.get(k)) != limpio(b.get(k))]
    crit = [(r.get("texto"), r.get("veredicto")) for r in a.get("critico") or []] == \
           [(r.get("texto"), r.get("veredicto")) for r in b.get("critico") or []]
    return {"cap": cap, "claves_distintas": dif, "critico_igual": crit,
            "transiciones": [v["kind"] for _, v in sorted((b.get("transitions") or {}).items(), key=lambda x: int(x[0]))]}


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    nuevo = Path(sys.argv[1])
    for cap in sys.argv[2:] or [f"ch{k:02d}" for k in range(1, 8)]:
        print(json.dumps(comparar(nuevo, cap), ensure_ascii=False), flush=True)
