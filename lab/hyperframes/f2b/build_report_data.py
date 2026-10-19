"""F2b — números del reporte final a partir de la corrida completa (cues, planes resueltos, logs).

Uso: python lab/hyperframes/f2b/build_report_data.py  → imprime markdown y guarda report_data_f2b.json
"""
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
VID = "ba6c3cac-a091-41c0-8dad-afd2f4364747"
W = ROOT / "output" / VID / "_fase2b_work"
import sys
LOG = ROOT / "lab" / "hyperframes" / "f2b" / (sys.argv[1] if len(sys.argv) > 1 else "full_run_f2b.log")
OUT_JSON = sys.argv[2] if len(sys.argv) > 2 else "report_data_f2b.json"
CAPS = [f"ch{i:02d}" for i in range(1, 8)]


def last_block(path: Path, cap: str) -> list[str]:
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    idx = max((i for i, ln in enumerate(lines) if re.match(rf"\[\d{{4}}-.*\] {cap} base=", ln)), default=0)
    return lines[idx:]


rows, data = [], {"caps": {}}
all_gaps, no_icon = [], []
for cap in CAPS:
    res = json.loads((W / f"gfx_plan_{cap}.resolved.json").read_text(encoding="utf-8"))["plan"]
    cues = json.loads((W / f"gfx_cues_{cap}.json").read_text(encoding="utf-8"))
    blk = [e for e in cues["events"] if not e["block"].startswith("shot_transition")]
    starts = sorted({round(e["t"], 2) for e in blk})
    dur = cues["events"][-1]["t"] if cues["events"] else 0
    log = last_block(W / f"gfx_{cap}.log", cap)
    dur_line = next((ln for ln in log if "escenas:" in ln), "")
    m_end = re.findall(r"([\d.]+)R\d", dur_line)
    gaps = [b - a for a, b in zip(starts, starts[1:])]
    all_gaps += gaps
    zoom_ok = [ln.strip() for ln in log if "zoom box por visión" in ln]
    zoom_no = [ln.strip() for ln in log if re.search(r"zoom (omitido|descartado)", ln)]
    total = next((float(x) for ln in log for x in re.findall(r"OK total ([\d.]+)s", ln)), None)
    emph = res.get("emphasis", []) or []
    no_icon += [(cap, e["word"], e["category"], "no lo dibuja" if not e.get("icon") else "tope por cap")
                for e in emph if not e.get("icon_callout")]
    count = Counter(e["block"].split(":")[0] for e in blk)
    d = {"bloques": dict(count), "recortes": [a["headline"] for a in res.get("archive_clippings", [])],
         "moods": [f"{e['word']} ({e['category']}{', ícono ' + e['icon'] + ' · ' + e.get('icon_anim', '') if e.get('icon_callout') else ''})" for e in emph],
         "conversion": [ln.strip() for ln in log if "convertido en recorte" in ln],
         "lado_contador": [ln.strip() for ln in log if "solape con el contador" in ln],
         "icon_array": res.get("icon_array"), "zoom_con_box": zoom_ok, "zoom_sin_box": zoom_no,
         "densidad_s": round(sum(gaps) / len(gaps), 1) if gaps else None, "max_hueco_s": round(max(gaps), 1) if gaps else None,
         "gap_warnings": res.get("gap_warnings", []), "gfx_total_s": total}
    data["caps"][cap] = d
    rows.append(f"| {cap} | {sum(count.values())} | {len(d['recortes'])} | {len(emph)} / {sum(1 for e in emph if e.get('icon_callout'))} "
                f"| {len(zoom_ok)} / {len(zoom_no)} | {d['densidad_s']} (máx {d['max_hueco_s']}) | {total} |")

log = LOG.read_text(encoding="utf-8", errors="replace")
t_concat = re.findall(r"concat por ventanas: (\d+)s", log)
t_music = re.findall(r"⏱ música: (\d+)s \(([^)]+)\)", log)
t_real = re.findall(r"real\s+(\d+)m([\d.]+)s", log)
data.update({"concat_s": t_concat, "musica": t_music, "real": t_real, "sin_icono": no_icon,
             "densidad_global_s": round(sum(all_gaps) / len(all_gaps), 1) if all_gaps else None,
             "fallback_concat": "falló" in log and "concat por ventanas falló" in log,
             "fallback_musica": "mezcla audio-solo falló" in log})
(ROOT / "lab" / "hyperframes" / "f2b" / OUT_JSON).write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
print("| cap | bloques | recortes | énfasis / con ícono | zoom con box / sin | densidad s (máx hueco) | capa gfx s |")
print("|---|---|---|---|---|---|---|")
print("\n".join(rows))
print(f"\nconcat: {t_concat} · música: {t_music} · real: {t_real} · densidad global: {data['densidad_global_s']} s")
print("sin ícono:", no_icon)
for cap, d in data["caps"].items():
    print(cap, "recortes:", d["recortes"], "| moods:", d["moods"], "| conv:", d["conversion"], "| lado:", d["lado_contador"])
