"""F7c: página estática de comparación del guion de Orleans → lab/hyperframes/f7/compara_orleans_v3r.html

Cuatro columnas por cap: v2 F5d (`lab/hyperframes/f5/pruebas/01b_narration_f5d_pre_retoque.json`, pool f5v2) · v3 con
el pool viejo (F6c, `ba6c3cac-f6v3`) · v3 con el pool de research v3 (F7c, guardada en `lab/hyperframes/f7/f7c_v1/`)
· F7c-2 (reglas nuevas, 1,500 palabras y notas del analista; `ba6c3cac-f7r3`). Arriba, las métricas del juez
(`m05_narrative.video_metrics`, cada versión con su pool y su skeleton/escaleta) y la revisión v3 (`m01b_guionista`:
duras/blandas). Debajo de cada texto v3, su escaleta (beats del cap). Sin servidor: HTML autocontenido.
Uso: python -I lab/hyperframes/f7/build_compara_v3r.py
"""
from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
STEPS = ROOT / "data" / "scripts" / "_steps"
LAB = Path(__file__).resolve().parent
OUT = LAB / "compara_orleans_v3r.html"


def _load(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def versions() -> list[dict]:
    from script_engine import m01a_escaleta as me
    v2 = _load(ROOT / "lab/hyperframes/f5/pruebas/01b_narration_f5d_pre_retoque.json")
    out = [{"key": "v2", "titulo": "v2 · F5d", "sub": "skeleton + narrador Pro (pool f5v2: 1 research Gemini)",
            "caps": [{"n": c["chapter_number"], "texto": c["narration"], "ids": c.get("datos_usados")}
                     for c in v2["chapters"]],
            "pool": _load(STEPS / "ba6c3cac-f5v2/01_facts_sources.json")["evidence_pool"],
            "skeleton": _load(STEPS / "ba6c3cac-f5v2/01a_skeleton.json"), "esc": None, "rev": None}]
    for key, tid, src, titulo, sub in (
            ("v3", "ba6c3cac-f6v3", STEPS / "ba6c3cac-f6v3", "v3 · pool viejo (F6c)",
             "escaleta + guionista + editor (pool f6v3 + testimonios, notas del analista)"),
            ("v3r", "ba6c3cac-f7r3", LAB / "f7c_v1", "v3 · pool nuevo (F7c)",
             "la misma tubería, pool de research v3 (10 documentos), sin notas"),
            ("v3r2", "ba6c3cac-f7r3", STEPS / "ba6c3cac-f7r3", "v3 · pool nuevo (F7c-2)",
             "reglas nuevas (fragmento de cita, gancho, sin juicios), 1,500 palabras, notas del analista")):
        nar = _load(src / "01b_narracion_v3.json")
        esc = _load(src / "01a_escaleta.json")
        out.append({"key": key, "titulo": titulo, "sub": sub,
                    "caps": [{"n": c["chapter_number"], "texto": c["narration"], "ids": c.get("datos_usados")}
                             for c in nar["caps"]],
                    "pool": _load(STEPS / tid / "01_facts_sources.json")["evidence_pool"],
                    "facts": _load(STEPS / tid / "01_facts_sources.json").get("verified_facts") or [],
                    "skeleton": me.caps_view(esc), "esc": esc, "rev": nar.get("revision"), "costo": nar.get("costo"),
                    "parrafos": nar.get("parrafos")})
    return out


def metrics(v: dict) -> dict:
    from researcher_steps.research_v3 import is_named_person
    from script_engine import m05_narrative as mn
    from script_engine.m05_narrative import adjectives
    caps = [{"chapter_number": c["n"], "narration": c["texto"], "datos_usados": c["ids"]} for c in v["caps"]]
    m = mn.video_metrics(caps, v["pool"], v["skeleton"])["video"]
    full = " ".join(c["texto"] for c in v["caps"])
    its = {q["id"]: q for q in v["pool"].get("citas") or []}
    used = {i for c in v["caps"] for i in (c["ids"] or [])}
    citas = [its[i] for i in used if i in its]
    named = sorted({q["autor"] for q in citas if q.get("testimonio") and is_named_person(q.get("autor") or "")})
    rev = v.get("rev") or {}
    return {"palabras": m["palabras"], "densidad (ids/100 pal.)": m["densidad"], "datos distintos": m["datos_distintos"],
            "adjetivos/100": round(100 * len(adjectives(full)) / max(1, m["palabras"]), 2),
            "trigramas repetidos": m["trigramas_repetidos"],
            "cliffhangers ok": f"{sum(1 for c in m['cliffhangers'] if c['ok'])}/{len(m['cliffhangers'])}",
            "datos en > 2 caps": len(m["datos_en_mas_de_2_caps"]), "problemas de fechas": m["problemas_de_fechas"],
            "cifras no canónicas": len(m["cifras_no_canonicas"]), "citas usadas": len(citas),
            "testigos con nombre citados": ", ".join(named) or "—",
            "revisión v3 de su corrida: duras / blandas": (f"{len(rev.get('hard') or [])} / {len(rev.get('soft') or [])}"
                                                          if rev else "— (v2)"),
            "duras con las reglas de F7c-2 (re-medido)": now_hard(v),
            "pool: datos / citas": f"{len(v['pool'].get('datos') or [])} / {len(v['pool'].get('citas') or [])}"}


def now_hard(v: dict) -> str:
    """Duras de la versión v3 medidas HOY (m01b_guionista.review con las reglas de F7c-2), para comparar parejo."""
    if not v.get("esc") or not v.get("parrafos"):
        return "— (v2)"
    from script_engine import m01b_guionista as mg
    rv = mg.review({"evidence_pool": v["pool"], "verified_facts": v.get("facts") or []}, v["esc"], v["parrafos"])
    return str(len(rv["hard"]))


def esc_html(esc: dict | None, n: int, pool: dict) -> str:
    if not esc:
        return ""
    from script_engine import evidence as ev
    its = ev.items(pool)
    rows = []
    for b in [b for b in esc["beats"] if b["cap"] == n]:
        dc = its.get(b["dato_central"], {})
        rows.append(f"<li><b>beat {b['n']}</b> · {html.escape(b['funcion'])} · {html.escape(b['emocion'])} · "
                    f"intensidad {b['intensidad']}<br><span class=m>dato central [{b['dato_central']}]</span> "
                    f"{html.escape(ev.text_of(dc))}<br><span class=m>imagen</span> "
                    f"{html.escape(b.get('imagen_sensorial') or '')}</li>")
    return f"<details><summary>escaleta del cap {n}</summary><ul>{''.join(rows)}</ul></details>"


CSS = """
:root{--bg:#fbfaf7;--fg:#1d1c1a;--mut:#6b675f;--line:#e2ded5;--card:#ffffff;--acc:#a8321f}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#161514;--fg:#ecebe7;--mut:#a39f96;
--line:#2f2d2a;--card:#1e1d1b;--acc:#e0705c}}
body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.55 Georgia,serif}
main{max-width:1500px;margin:0 auto;padding:24px 16px}
h1{font:600 22px/1.3 system-ui,sans-serif;margin:0 0 4px}
p.lead{color:var(--mut);font-family:system-ui,sans-serif;font-size:13px;margin:0 0 20px}
table{border-collapse:collapse;width:100%;font:13px/1.4 system-ui,sans-serif;margin-bottom:28px}
th,td{border-bottom:1px solid var(--line);padding:6px 8px;text-align:left;vertical-align:top}
th{color:var(--mut);font-weight:600}
.grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin-bottom:26px}
.col{background:var(--card);border:1px solid var(--line);border-radius:6px;padding:12px 14px}
.col h3{font:600 13px system-ui,sans-serif;margin:0 0 6px;color:var(--acc)}
.col p{margin:0 0 8px;white-space:pre-wrap}
.ids{color:var(--mut);font:11px system-ui,sans-serif}
details{font:12.5px/1.45 system-ui,sans-serif;margin-top:8px;color:var(--fg)}
summary{cursor:pointer;color:var(--mut)}
ul{padding-left:18px;margin:6px 0}
.m{color:var(--mut)}
h2{font:600 17px system-ui,sans-serif;margin:30px 0 10px}
@media (max-width:1200px){.grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media (max-width:700px){.grid{grid-template-columns:1fr}}
"""


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    vs = versions()
    ms = [metrics(v) for v in vs]
    rows = "".join(f"<tr><th>{html.escape(k)}</th>" + "".join(f"<td>{html.escape(str(m[k]))}</td>" for m in ms)
                   + "</tr>" for k in ms[0])
    head = "".join(f"<th>{html.escape(v['titulo'])}<br><span class=m>{html.escape(v['sub'])}</span></th>" for v in vs)
    caps_html = []
    for n in range(1, 8):
        cols = []
        for v in vs:
            c = next((c for c in v["caps"] if c["n"] == n), None)
            txt = html.escape(c["texto"] if c else "(sin cap)")
            ids = ", ".join(c["ids"] or []) if c and c["ids"] else ""
            cols.append(f"<div class=col><h3>{html.escape(v['titulo'])}</h3><p>{txt}</p>"
                        + (f"<div class=ids>ids: {html.escape(ids)}</div>" if ids else "")
                        + esc_html(v["esc"], n, v["pool"]) + "</div>")
        caps_html.append(f"<h2>Cap {n}</h2><div class=grid>{''.join(cols)}</div>")
    doc = f"""<!doctype html><html lang=es><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1"><title>Orleans: guion v2 · v3 · v3r · v3r2</title>
<style>{CSS}</style></head><body><main>
<h1>Orleans — cuatro versiones del guion</h1>
<p class=lead>v2 F5d · v3 con el pool viejo (F6c) · v3 con el pool de research v3 (F7c) · F7c-2 (reglas nuevas, 1,500 palabras,
notas del analista). Métricas del juez
(m05_narrative) medidas con el pool y la escaleta/skeleton de cada versión.</p>
<table><tr><th>métrica</th>{head}</tr>{rows}</table>
{''.join(caps_html)}
</main></body></html>"""
    OUT.write_text(doc, encoding="utf-8")
    (LAB / "f7c_metricas_compara.json").write_text(json.dumps({v["key"]: m for v, m in zip(vs, ms)}, ensure_ascii=False,
                                                              indent=1), encoding="utf-8")
    for v, m in zip(vs, ms):
        print(v["titulo"], m)


if __name__ == "__main__":
    main()
