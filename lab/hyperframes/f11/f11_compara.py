"""F11 §2 — compara_v3_v4.html: Orleans (v3 = F7c-3) e Ycuá (v3 = v1) contra el guion v4 (corridas A y B).

Lee v3_remedido.json, guion_<tema>_v4A.json / _v4B.json, tokens_prompt.json y costos_f11.json (los deja
f11_convergencia.py). Autocontenida, legible en el teléfono. Marca en color (solo lectura, no son reglas): bloqueantes,
fecha repetida, juicio de la lista, eco después de una cita y voz de tráiler.
Uso: python -I lab/hyperframes/f11/f11_compara.py
"""
from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
LAB = Path(__file__).resolve().parent
TEMAS = {"orleans": ("Orleans · ba6c3cac-f7r3", "F7c-3"), "ycua": ("Ycuá Bolaños · f8s1-ycua-bolanos", "v1")}


def _j(name: str):
    p = LAB / name
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def wc(s: str) -> int:
    return len(re.findall(r"[\wáéíóúñü]+", s or "", re.I))


# ── marcas ───────────────────────────────────────────────────────────────────

def spans(parrafos: list[dict], pool: dict, bl: list[dict]) -> list[list[tuple[int, int, str, str]]]:
    """Por párrafo: (inicio, fin, clase, título) de lo que se marca."""
    from script_engine import evidence as ev
    from script_engine.guion_v3_reglas import DATE_RE, JUDGMENTS, TRAILER, echo_soft
    blob = ev.norm(" ".join(ev.text_of(it) for it in ev.items(pool).values()))
    seen_day: set[str] = set()
    out = []
    for k, p in enumerate(parrafos):
        t, sp = p["texto"], []
        for x in bl:
            if x.get("frase") and x.get("beat") == p["beat"] and x["frase"] in t and x["frase"] != t:
                i = t.find(x["frase"])
                sp.append((i, i + len(x["frase"]), "blq", f"bloqueante ({x['codigo']}): {x['motivo']}"))
            elif x.get("frase") == t and x.get("beat") == p["beat"]:
                sp.append((0, len(t), "blq", f"bloqueante ({x['codigo']}): {x['motivo']}"))
        for m in DATE_RE.finditer(t):
            key = re.sub(r"\s+de\s+\d{4}$", "", ev.norm(m.group(0)))
            if key in seen_day:
                sp.append((m.start(), m.end(), "fecha", "fecha repetida"))
            seen_day.add(key)
        for pat, root in JUDGMENTS:
            if ev.norm(root) in blob:
                continue
            for m in re.finditer(pat, t, re.I):
                sp.append((m.start(), m.end(), "juicio", "juicio de la lista (fuera del pool)"))
        for pat in TRAILER:
            for m in re.finditer(pat, t, re.I):
                sp.append((m.start(), m.end(), "trailer", "voz de tráiler"))
        for e in echo_soft([p]):
            mm = re.search(r"«(.+)»: cortalo", e)
            if mm and mm.group(1) in t:
                i = t.find(mm.group(1))
                sp.append((i, i + len(mm.group(1)), "eco", "eco después de la cita"))
        out.append(sp)
    return out


def render(t: str, sp: list[tuple[int, int, str, str]]) -> str:
    sp = sorted(sp, key=lambda x: (x[0], -(x[1] - x[0])))
    res, pos = [], 0
    for a, b, cls, title in sp:
        if a < pos:
            continue
        res.append(html.escape(t[pos:a]))
        res.append(f'<mark class="{cls}" title="{html.escape(title)}">{html.escape(t[a:b])}</mark>')
        pos = b
    res.append(html.escape(t[pos:]))
    return "".join(res)


# ── bloques ──────────────────────────────────────────────────────────────────

def summary_row(name: str, bl: list, m: dict, usd: str) -> str:
    hum = m.get("humano_caps") or []
    return (f"<tr><th>{html.escape(name)}</th><td class='n'>{len(bl)}</td><td class='n'>{len(m['duras_v3'])}</td>"
            f"<td class='n'>{m['palabras']}</td><td class='n'>{m['citas']}</td><td class='n'>{len(hum)} "
            f"<small>{hum}</small></td><td>{m['cierre']}</td><td class='n'>{usd}</td></tr>")


def cap_cell(n: int, parrafos: list[dict], sps: list, bl: list[dict], m: dict) -> str:
    rows = [(p, s) for p, s in zip(parrafos, sps) if p["cap"] == n]
    w, tgt = (m["palabras_por_cap"].get(str(n)) or m["palabras_por_cap"].get(n) or [0, 0])
    capbl = [x for x in bl if x.get("cap") == n]
    pc = (m.get("por_cap") or {}).get(str(n)) or (m.get("por_cap") or {}).get(n) or {}
    ratio = w / tgt if tgt else 0
    cls = "ok" if 0.75 <= ratio <= 1.25 else "bad"
    head = (f"<div class='meta'><span class='{cls}'>{w}/{tgt} palabras</span> · bloqueantes <b>{len(capbl)}</b> · "
            f"duras v3 del cap {len(pc.get('duras') or [])} · blandas {len(pc.get('blandas') or [])}</div>")
    blq = "".join(f"<li>({x['codigo']}) {html.escape(x['motivo'])}</li>" for x in capbl)
    body = "".join(f"<p><span class='beat'>b{p['beat']}</span> {render(p['texto'], s)}</p>" for p, s in rows) \
        or "<p class='bad'>(cap vacío)</p>"
    return head + (f"<ul class='blq'>{blq}</ul>" if blq else "") + body


def section(tema: str) -> str:
    title, v3name = TEMAS[tema]
    v3 = (_j("v3_remedido.json") or {}).get(tema) or {}
    runs = {tag: _j(f"guion_{tema}_v4{tag}.json") for tag in ("A", "B")}
    topic_pool = _pool(tema)
    out = [f"<section><h2>{html.escape(title)}</h2>"]
    out.append("<div class='scroll'><table class='sum'><tr><th>versión</th><th>bloqueantes</th><th>duras v3 "
               "re-medidas</th><th>palabras</th><th>citas</th><th>humano en N caps</th><th>cierre</th><th>US$</th></tr>")
    if v3:
        out.append(summary_row(f"v3 ({v3name})", v3["bloqueantes"], v3["metricas"], "—"))
    for tag, r in runs.items():
        if r and r.get("reparacion"):
            out.append(summary_row(f"v4 {tag}", r["reparacion"]["bloqueantes_despues"], r["metricas"],
                                   f"{r['costo']['usd']:.3f}"))
            out.append(summary_row(f"v4 {tag} (crudo, antes de reparar)", r["bloqueantes_crudo"], r["metricas_crudo"], ""))
    out.append("</table></div>")
    a = runs.get("A")
    if v3 and a and a.get("reparacion"):
        ps3, ps4 = v3["parrafos"], a["reparacion"]["parrafos"]
        bl3, bl4 = v3["bloqueantes"], a["reparacion"]["bloqueantes_despues"]
        s3, s4 = spans(ps3, topic_pool, bl3), spans(ps4, topic_pool, bl4)
        out.append("<div class='grid hdr'><div>v3 actual (" + v3name + ")</div><div>v4 A</div></div>")
        for n in range(1, 8):
            out.append(f"<h3>Cap {n}</h3><div class='grid'><div class='col'>{cap_cell(n, ps3, s3, bl3, v3['metricas'])}"
                       f"</div><div class='col'>{cap_cell(n, ps4, s4, bl4, a['metricas'])}</div></div>")
    b = runs.get("B")
    if b and b.get("reparacion"):
        ps = b["reparacion"]["parrafos"]
        sb = spans(ps, topic_pool, b["reparacion"]["bloqueantes_despues"])
        inner = "".join(f"<h4>Cap {n}</h4>" + cap_cell(n, ps, sb, b["reparacion"]["bloqueantes_despues"], b["metricas"])
                        for n in range(1, 8))
        out.append(f"<details><summary>v4 B — texto completo</summary><div class='col'>{inner}</div></details>")
    out.append("</section>")
    return "".join(out)


_POOLS: dict = {}


def _pool(tema: str) -> dict:
    if tema not in _POOLS:
        import fase1_5 as f15
        tid = {"orleans": "ba6c3cac-f7r3", "ycua": "f8s1-ycua-bolanos"}[tema]
        _POOLS[tema] = f15._load_topic_by_id(tid)["evidence_pool"]
    return _POOLS[tema]


CSS = """
:root{--bg:#fbfaf7;--fg:#1d1c1a;--mut:#6b6760;--line:#e3dfd6;--card:#fff;--blq:#f6c9c4;--fecha:#cfe0f7;--juicio:#f7e3b0;
--eco:#dccff3;--trailer:#c9ecd6;--ok:#2f7a45;--bad:#b3261e}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#161513;--fg:#ecebe7;--mut:#a29d94;
--line:#34312c;--card:#1f1d1a;--blq:#6b2a25;--fecha:#23415f;--juicio:#5c4a17;--eco:#3f3260;--trailer:#1f4a30;
--ok:#7cc792;--bad:#ff8a80}}
:root[data-theme="dark"]{--bg:#161513;--fg:#ecebe7;--mut:#a29d94;--line:#34312c;--card:#1f1d1a;--blq:#6b2a25;
--fecha:#23415f;--juicio:#5c4a17;--eco:#3f3260;--trailer:#1f4a30;--ok:#7cc792;--bad:#ff8a80}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.55 Georgia,serif;padding:16px;
max-width:1200px;margin:auto}h1{font-size:1.5rem;margin:.2em 0}h2{border-bottom:2px solid var(--line);padding-bottom:.2em;
margin-top:2em}h3{font-size:1rem;margin:1.4em 0 .4em;color:var(--mut)}small,.meta{font:13px/1.4 system-ui,sans-serif;
color:var(--mut)}.scroll{overflow-x:auto}table{border-collapse:collapse;font:14px system-ui,sans-serif;width:100%}
td,th{border-bottom:1px solid var(--line);padding:6px 8px;text-align:left;vertical-align:top}.n{text-align:right;
font-variant-numeric:tabular-nums}.grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}.hdr div{font:600 13px
system-ui,sans-serif;text-transform:uppercase;letter-spacing:.05em;color:var(--mut)}.col{background:var(--card);
border:1px solid var(--line);border-radius:8px;padding:10px 12px}.col p{margin:.6em 0}.beat{font:600 11px system-ui,
sans-serif;color:var(--mut);margin-right:4px}mark{color:inherit;border-radius:3px;padding:0 2px}mark.blq{background:
var(--blq);text-decoration:underline wavy var(--bad)}mark.fecha{background:var(--fecha)}mark.juicio{background:
var(--juicio)}mark.eco{background:var(--eco)}mark.trailer{background:var(--trailer)}.ok{color:var(--ok)}.bad{color:
var(--bad)}ul.blq{font:13px system-ui,sans-serif;color:var(--bad);margin:.3em 0;padding-left:1.2em}details{margin-top:1em}
summary{cursor:pointer;font:600 14px system-ui,sans-serif}.legend mark{margin-right:6px}
@media (max-width:760px){.grid{grid-template-columns:1fr}.hdr{display:none}.grid .col:first-child::before{content:"v3";
font:600 12px system-ui;color:var(--mut)}.grid .col:last-child::before{content:"v4 A";font:600 12px system-ui;
color:var(--mut)}}
"""


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    tok = _j("tokens_prompt.json") or {}
    cost = _j("costos_f11.json") or {}
    tk = " · ".join(f"{t}: v3 {v['v3']:,} → v4 {v['v4']:,} tokens" for t, v in tok.items())
    head = (f"<h1>Guion v3 vs v4 (F11)</h1><p class='meta'>Prompt del guionista (con el sistema): {tk}. "
            f"Costo de la tanda (4 corridas + reparaciones + juez): US$ {cost.get('usd_total', 0):.3f}. "
            "Escaletas fijas (Orleans = F7c-3; Ycuá = v1), sin notas.</p>"
            "<p class='meta legend'><mark class='blq'>bloqueante</mark><mark class='fecha'>fecha repetida</mark>"
            "<mark class='juicio'>juicio de la lista</mark><mark class='eco'>eco después de cita</mark>"
            "<mark class='trailer'>voz de tráiler</mark> · las marcas que no son bloqueantes no rechazan nada.</p>")
    doc = (f"<!doctype html><html lang='es'><head><meta charset='utf-8'><meta name='viewport' "
           f"content='width=device-width,initial-scale=1'><title>Guion v3 vs v4</title><style>{CSS}</style></head>"
           f"<body>{head}{section('orleans')}{section('ycua')}</body></html>")
    (LAB / "compara_v3_v4.html").write_text(doc, encoding="utf-8")
    print("compara_v3_v4.html", len(doc))


if __name__ == "__main__":
    main()
