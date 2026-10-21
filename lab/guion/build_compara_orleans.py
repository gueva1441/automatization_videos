"""F5 §3: página estática de comparación v1 / v2 del guion de Orleans → lab/guion/compara_orleans.html

v1 y v2 lado a lado por cap (datos del pool resaltados en el texto), métricas de §1.5 por cap y por video, y el
evidence_pool completo con la marca de qué versión usó cada dato. Sin servidor: un HTML autocontenido.
Uso: PYTHONIOENCODING=utf-8 python lab/guion/build_compara_orleans.py
"""
from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from script_engine import evidence as ev  # noqa: E402
from script_engine import m05_narrative as mn  # noqa: E402

V1, V2 = "ba6c3cac-a091-41c0-8dad-afd2f4364747", "ba6c3cac-f5v2"
STEPS = ROOT / "data" / "scripts" / "_steps"
OUT = Path(__file__).resolve().parent / "compara_orleans.html"


def _load(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def highlight(text: str, ids: list[str], its: dict) -> str:
    """Texto escapado con los anchors de los datos usados marcados (<mark title=id>)."""
    spans = []
    low = ev.norm(text)
    for i in ids:
        for a in ev.anchors(its[i]):
            for f in (ev._num_forms(a) if re.search(r"\d", a) else [a]):
                f = ev.norm(f).strip(" .,;:")
                if not f:
                    continue
                for m in re.finditer(rf"(?<![\w]){re.escape(f)}(?![\w])", low):
                    spans.append((m.start(), m.end(), i))
    spans.sort()
    out, pos = [], 0
    for a, b, i in spans:
        if a < pos:
            continue
        out.append(html.escape(text[pos:a]))
        out.append(f'<mark title="{i}: {html.escape(ev.text_of(its[i])[:120])}">{html.escape(text[a:b])}<sup>{i}</sup></mark>')
        pos = b
    out.append(html.escape(text[pos:]))
    return "".join(out)


def _ok(v) -> str:
    return '<span class="ok">✔</span>' if v is True else ('<span class="ko">✘</span>' if v is False else "—")


def main() -> None:
    pool = _load(STEPS / V2 / "01_facts_sources.json")["evidence_pool"]
    its = ev.items(pool)
    j1, j2 = _load(STEPS / V2 / "06_judge_narrative_v1.json"), _load(STEPS / V2 / "06_judge_narrative.json")
    n1 = {c["chapter_number"]: c["narration"] for c in _load(STEPS / V1 / "01b_narration.json")["chapters"]}
    n2 = {c["chapter_number"]: c["narration"] for c in _load(STEPS / V2 / "01b_narration.json")["chapters"]}
    sk1, sk2 = _load(STEPS / V1 / "01a_skeleton.json"), _load(STEPS / V2 / "01a_skeleton.json")
    used1 = {i for c in j1["caps"] for i in c["datos_usados"]}
    used2 = {i for c in j2["caps"] for i in c["datos_usados"]}
    cliffs = {c["cap"]: c for c in j2["video"].get("cliffhangers") or []}

    def vrow(name, a, b, fmt=str, good=None):
        return (f"<tr><th>{name}</th><td>{fmt(a)}</td><td>{fmt(b)}</td>"
                f"<td>{'' if good is None else good}</td></tr>")
    v1, v2 = j1["video"], j2["video"]
    rep = lambda v: ", ".join(f"{ev.anchors(its[i])[0] if ev.anchors(its[i]) else i} ({len(c)} caps)"  # noqa: E731
                              for i, c in v["datos_en_mas_de_2_caps"].items()) or "ninguno"
    video_tbl = "".join([
        vrow("Densidad (datos/100 palabras, umbral ≥ 2.0)", v1["densidad"], v2["densidad"]),
        vrow("Adjetivos/100 palabras (umbral ≤ 3.6, ver DECISIONES J18)", v1["adj_100"], v2["adj_100"]),
        vrow("3-gramas repetidos entre caps (umbral < 5 %)", f"{v1['trigramas_repetidos']:.1%}", f"{v2['trigramas_repetidos']:.1%}"),
        vrow("Datos en más de 2 caps", rep(v1), rep(v2)),
        vrow("Antagonista nombrado", _ok(v1["antagonista_nombrado"]), _ok(v2["antagonista_nombrado"])),
        vrow("Datos distintos del pool usados", v1["datos_distintos"], v2["datos_distintos"]),
        vrow("Palabras", v1["palabras"], v2["palabras"]),
        vrow("Umbrales que pasa", sum(1 for x in v1["umbral"].values() if x), sum(1 for x in v2["umbral"].values() if x)),
    ])
    caps_html = []
    for k in range(1, 8):
        c1, c2 = j1["caps"][k - 1], j2["caps"][k - 1]
        t1 = next((c.get("title") for c in sk1["chapters"] if c["chapter_number"] == k), "")
        t2 = next((c.get("title") for c in sk2["chapters"] if c["chapter_number"] == k), "")
        cl = cliffs.get(k)
        cliff = (f'<p class="cliff">Cliffhanger del skeleton: <b>[{cl["id"]}]</b> {html.escape(cl["texto"])} — '
                 f'{_ok(cl["ok"])} en el cierre</p>') if cl else ""
        metr = lambda c: (f'<p class="m">densidad <b>{c["densidad"]}</b> · adjetivos <b>{c["adj_100"]}</b>/100 · '  # noqa: E731
                          f'3-gramas repetidos <b>{c["trigramas_repetidos"]:.0%}</b> · {c["palabras"]} palabras · '
                          f'{len(c["datos_usados"])} datos</p>')
        caps_html.append(f"""
<section class="cap"><h2>Cap {k}</h2>
<div class="pair">
 <div><h3>v1 · {html.escape(t1)}</h3>{metr(c1)}<p class="txt">{highlight(n1[k], c1['datos_usados'], its)}</p></div>
 <div><h3>v2 · {html.escape(t2)}</h3>{metr(c2)}<p class="txt">{highlight(n2[k], c2['datos_usados'], its)}</p>{cliff}</div>
</div></section>""")
    rows = []
    lab = {"datos": "dato", "cronologia": "evento", "citas": "cita", "lugares": "lugar", "personajes": "persona"}
    for i, it in its.items():
        if it["_kind"] in ("lugares", "personajes"):
            continue
        caps1 = [k + 1 for k, c in enumerate(j1["caps"]) if i in c["datos_usados"]]
        caps2 = [k + 1 for k, c in enumerate(j2["caps"]) if i in c["datos_usados"]]
        rows.append(f"<tr class='{'u2' if caps2 else ''}'><td>{i}</td><td>{lab[it['_kind']]}"
                    f"{' · ' + it.get('tipo', '') if it.get('tipo') else ''}</td><td>{html.escape(ev.text_of(it))}</td>"
                    f"<td>{html.escape(it.get('fecha') or '')}</td><td>{html.escape((it.get('fuente') or '')[:60])}</td>"
                    f"<td>{', '.join(map(str, caps1)) or ''}</td><td>{', '.join(map(str, caps2)) or ''}</td></tr>")
    pers = "".join(f"<li><b>{html.escape(p['nombre'])}</b> — {html.escape(p.get('rol') or '')}"
                   f"{' · <b>antagonista</b>' if p.get('antagonista') else ''} (entra en el cap {p.get('entra_en_cap')})</li>"
                   for p in sk2.get("personajes") or [])
    page = f"""<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Guion v1 vs v2</title><style>
:root{{--bg:#f7f5f0;--fg:#1d1b18;--mut:#6b655c;--card:#fff;--line:#e2ddd3;--mark:#ffe38a;--ok:#1f7a3a;--ko:#b3261e;--acc:#8a2b1e}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--bg:#16140f;--fg:#ece8df;--mut:#a39c90;--card:#201d17;--line:#38332a;--mark:#6b5a12;--ok:#6fcf8b;--ko:#ff8a80;--acc:#e8a090}}}}
:root[data-theme="dark"]{{--bg:#16140f;--fg:#ece8df;--mut:#a39c90;--card:#201d17;--line:#38332a;--mark:#6b5a12;--ok:#6fcf8b;--ko:#ff8a80;--acc:#e8a090}}
body{{margin:0;background:var(--bg);color:var(--fg);font:15px/1.55 system-ui,-apple-system,"Segoe UI",sans-serif}}
main{{max-width:1240px;margin:0 auto;padding:24px 16px 60px}} h1{{font-size:24px;margin:0 0 4px}} h2{{font-size:19px;margin:28px 0 8px;color:var(--acc)}}
h3{{font-size:15px;margin:0 0 4px}} .sub{{color:var(--mut);margin:0 0 18px}}
table{{border-collapse:collapse;width:100%;background:var(--card);border:1px solid var(--line);font-size:14px}}
th,td{{border-bottom:1px solid var(--line);padding:6px 8px;text-align:left;vertical-align:top}} thead th{{font-weight:600}}
.pair{{display:grid;grid-template-columns:1fr 1fr;gap:14px}} .pair>div{{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:12px 14px;min-width:0}}
.m{{color:var(--mut);font-size:13px;margin:0 0 8px}} .txt{{margin:0}} mark{{background:var(--mark);color:inherit;border-radius:3px;padding:0 2px}}
mark sup{{font-size:9px;color:var(--mut);margin-left:1px}} .cliff{{font-size:13px;color:var(--mut);border-top:1px dashed var(--line);padding-top:6px;margin:10px 0 0}}
.ok{{color:var(--ok);font-weight:700}} .ko{{color:var(--ko);font-weight:700}} tr.u2 td:first-child{{font-weight:700}}
.scroll{{overflow-x:auto}} @media (max-width:760px){{.pair{{grid-template-columns:1fr}}}}
</style></head><body><main>
<h1>Orleans — guion v1 vs v2</h1>
<p class="sub">F5 §3. v1 = el guion producido (10 verified_facts). v2 = mismo research, con todo el evidence_pool
({sum(1 for x in its.values() if x['_kind'] in ('datos','cronologia','citas'))} datos, eventos y citas). Las métricas usan el mismo pool para
las dos versiones. Datos resaltados en el texto: <mark>así</mark> (el número chico es el id del pool).</p>
<h2>Por video</h2><div class="scroll"><table><thead><tr><th></th><th>v1</th><th>v2</th><th></th></tr></thead><tbody>{video_tbl}</tbody></table></div>
<h2>Personajes de v2</h2><ul>{pers}</ul>
{''.join(caps_html)}
<h2>evidence_pool — qué dato usó cada versión</h2><div class="scroll"><table><thead><tr><th>id</th><th>tipo</th><th>texto (literal del research)</th><th>fecha</th><th>fuente</th><th>caps v1</th><th>caps v2</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table></div>
</main></body></html>"""
    OUT.write_text(page, encoding="utf-8")
    print(f"{OUT} · v1 usa {len(used1)} datos del pool, v2 usa {len(used2)}")


if __name__ == "__main__":
    main()
