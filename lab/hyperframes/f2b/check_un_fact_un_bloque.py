"""Verifica la regla "un fact = un bloque" + dedupe de cifras sobre los planes resueltos de los 7 caps (Orleans).
Imprime contadores y recortes por cap y FALLA si: (a) un recorte comparte fact o cifra con el contador de su cap,
o (b) una cifra se anima como contador en más de un cap. Guarda check_un_fact_un_bloque.json.
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
W = ROOT / "output" / "ba6c3cac-a091-41c0-8dad-afd2f4364747" / "_fase2b_work"
d = lambda s: re.sub(r"\D", "", s)  # noqa: E731
rows, counted, bad = {}, Counter(), []
for c in range(1, 8):
    r = json.loads((W / f"gfx_plan_ch{c:02d}.resolved.json").read_text(encoding="utf-8"))["plan"]
    cu = r.get("count_up")
    arcs = [(a["headline"], a.get("fact_idx"), a["start"]) for a in r["archive_clippings"]]
    rows[f"ch{c:02d}"] = {"contador": [cu["value_text"], cu.get("fact_idx"), cu["start"]] if cu else None, "recortes": arcs}
    if cu:
        counted[d(cu["value_text"])] += 1
        for h, fi, _ in arcs:
            if fi == cu.get("fact_idx") or d(cu["value_text"]) in {d(x) for x in re.findall(r"\d[\d.,]*\d|\d", h)}:
                bad.append(f"ch{c:02d}: recorte {h!r} comparte fact/cifra con el contador {cu['value_text']}")
bad += [f"cifra {k} animada {v} veces" for k, v in counted.items() if v > 1]
res = {"caps": rows, "contadores_por_cifra": dict(counted), "violaciones": bad}
(Path(__file__).with_suffix(".json")).write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
for cap, v in rows.items():
    print(cap, "| contador:", v["contador"], "| recortes:", v["recortes"])
print("contadores por cifra:", dict(counted))
print("VIOLACIONES:", bad or "ninguna")
sys.exit(1 if bad else 0)
