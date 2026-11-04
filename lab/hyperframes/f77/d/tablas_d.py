"""F77 D: las tablas de la corrida real, leídas del disco (solo lectura). Uso: PYTHONIOENCODING=utf-8 python ... """
import json
import re
import sys
from pathlib import Path

R = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(R))
import estante  # noqa: E402

D = R / "data"
out = []
regs = [json.loads(p.read_text(encoding="utf-8")) for p in sorted((D / "estante").glob("*.json"))]
out += ["## (a) gate ES", "", "| tema | label | competidor más pesado | unidades API | fuente | sigue |", "|---|---|---|---|---|---|"]
for r in regs:
    g = r["gate"]
    h = g.get("heaviest") or {}
    vistas = f"{int(h.get('views') or 0):,}".replace(",", ".")
    comp = f"«{h.get('title')}» `{h.get('video_id')}` {vistas} views, {h.get('months')} meses" if h else "—"
    out.append(f"| {r['titulo']} | {g.get('label')} | {comp} | {g.get('quota_units')} | {g.get('source')} | "
               f"{'sí (exit ' + str(r.get('rc')) + ')' if estante.sigue(r) else 'no (SATURADO)'} |")
out += ["", "## (b) tiempos por sub-paso (s) — Kyshtym: R1 ~780 · R3 ~348 · research 1356", "",
        "| tema | perfil | R1 | R2 | R3 | pool | research total |", "|---|---|---|---|---|---|---|"]
focos, docs = [], []
for r in regs:
    f = D / "scripts" / "_steps" / r["tid"] / "01_v3_tiempos.json"
    if not f.exists():
        continue
    t = json.loads(f.read_text(encoding="utf-8"))["tiempos_research"][-1]
    p = t["pasos"]
    out.append(f"| {r['titulo'][:40]} | {p['perfil']:.0f} | {p['R1']:.0f} | {p['R2']:.0f} | {p['R3']:.0f} | {p['pool']:.0f} | {t['total_s']:.0f} |")
    for fo in t["R1_focos"] + t.get("R1_pistas", []):
        focos.append((r["titulo"][:30], fo))
    docs.append((r["titulo"][:30], t["R3_docs"]))
out += ["", "## (c) R1 por foco — Wittenoom: 2 de 4 «sin»", "", "| tema | foco | via | URLs | rondas | s |", "|---|---|---|---|---|---|"]
for tema, fo in focos:
    out.append(f"| {tema} | {fo['label']} | {fo['via']} | {fo['n_urls']} | {len(fo['rondas'])} | {fo['s']:.0f} |")
out += ["", "R3 por documento:"] + [f"- {tema}: " + ", ".join(f"{d['doc']} {d['s']:.0f} s ({d['partes']} p.)" for d in ds) for tema, ds in docs]
out += ["", "## (d) límites de velocidad", ""]
for r in regs:
    lg = D / "estante" / f"{r['tid']}.log"
    if lg.exists():
        t = lg.read_text(encoding="utf-8", errors="replace")
        n429 = len(re.findall(r"429|RESOURCE_EXHAUSTED|rate.?limit", t, re.I))
        nre = len(re.findall(r"reintent|retry", t, re.I))
        errs = []
        f = D / "scripts" / "_steps" / r["tid"] / "01_v3_tiempos.json"
        if f.exists():
            tt = json.loads(f.read_text(encoding="utf-8"))["tiempos_research"][-1]
            for fo in tt["R1_focos"] + tt.get("R1_pistas", []):
                for ro in fo["rondas"]:
                    errs += [e for e in (ro.get("pro_error"), ro.get("flash_error")) if e]
        out.append(f"- {r['titulo'][:40]}: {n429} menciones de 429/rate limit, {nre} de reintento en el log; "
                   f"{len(errs)} errores de modelo en las rondas de R1" + (f" ({errs[0][:80]})" if errs else ""))
out += ["", "## (f) US$ por tema (01_v3_costos.json, sin el juez del gate)", ""]
for r in regs:
    out.append(f"- {r['titulo'][:50]}: US$ {estante._usd(r['tid']):.4f}")
items = estante.listar()
out += ["", "## (e) body del menú E", "", f"Estante ({len(items)})", "", estante.body(items)]
txt = "\n".join(out) + "\n"
(Path(__file__).parent / "tablas_d.md").write_text(txt, encoding="utf-8")
print(txt)
