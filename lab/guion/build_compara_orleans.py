"""F5 §3: página estática de comparación v1 / v2 del guion de Orleans → lab/guion/compara_orleans.html

v1 y v2 lado a lado por cap (datos del pool resaltados en el texto), métricas de §1.5 por cap y por video, y el
evidence_pool completo con la marca de qué versión usó cada dato. Sin servidor: un HTML autocontenido.
F5b: la tabla por video suma la columna «v2 F5» (la v2 de F5 medida con el pool nuevo, por regex) y las métricas
nuevas (conteo por id declarado, piso/techo de adjetivos, repetición dentro del cap, nombres sin acción); al final, lo
que el filtro del pool sacó (N1 no relacionado, N5 sin acción).
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
    f5 = STEPS / V2 / "06_judge_narrative_v2f5.json"
    j5 = _load(f5) if f5.exists() else None
    f5b = STEPS / V2 / "06_judge_narrative_v2f5b.json"
    jb = _load(f5b) if f5b.exists() else None
    f5c = STEPS / V2 / "06_judge_narrative_v2f5c.json"
    jc = _load(f5c) if f5c.exists() else None
    dec2 = {c["chapter_number"]: c.get("datos_usados") for c in _load(STEPS / V2 / "01b_narration.json")["chapters"]}
    n1 = {c["chapter_number"]: c["narration"] for c in _load(STEPS / V1 / "01b_narration.json")["chapters"]}
    n2 = {c["chapter_number"]: c["narration"] for c in _load(STEPS / V2 / "01b_narration.json")["chapters"]}
    sk1, sk2 = _load(STEPS / V1 / "01a_skeleton.json"), _load(STEPS / V2 / "01a_skeleton.json")
    used1 = {i for c in j1["caps"] for i in c["datos_usados"]}
    used2 = {i for c in j2["caps"] for i in c["datos_usados"]}
    cliffs = {c["cap"]: c for c in j2["video"].get("cliffhangers") or []}

    v1, v2 = j1["video"], j2["video"]
    v5 = j5["video"] if j5 else None
    vb = jb["video"] if jb else None
    vc = jc["video"] if jc else None
    cols = [v1] + ([v5] if v5 else []) + ([vb] if vb else []) + ([vc] if vc else []) + [v2]

    def vrow(name, f):
        return f"<tr><th>{name}</th>" + "".join(f"<td>{f(v)}</td>" for v in cols) + "</tr>"
    rep = lambda v: ", ".join(f"{ev.anchors(its[i])[0] if i in its and ev.anchors(its[i]) else i} ({len(c)} caps)"  # noqa: E731
                              for i, c in v["datos_en_mas_de_2_caps"].items()) or "ninguno"
    ncaps = lambda key: (lambda v: ", ".join(map(str, v.get(key) or [])) or "ninguno")  # noqa: E731
    video_tbl = "".join([
        vrow("Conteo de datos", lambda v: "por id declarado" if v.get("conteo") == "por_id" else "regex (sin declaración)"),
        vrow("Densidad (datos/100 palabras, umbral ≥ 2.0)", lambda v: v["densidad"]),
        vrow("Densidad por regex (la medición de F5)", lambda v: v.get("densidad_regex", v["densidad"])),
        vrow("Densidad por hecho (anclas distintas que suenan)", lambda v: v.get("densidad_hechos", "—")),
        vrow("Adjetivos/100 palabras (F5b: entre 2 y 4)", lambda v: v["adj_100"]),
        vrow("Caps fuera de 2–4 adjetivos/100", ncaps("caps_fuera_de_adjetivos")),
        vrow("Caps con un dato repetido dentro del cap", ncaps("caps_con_repetidos_en_cap")),
        vrow("3-gramas repetidos entre caps (umbral < 5 %)", lambda v: f"{v['trigramas_repetidos']:.1%}"),
        vrow("Datos en más de 2 caps", rep),
        vrow("Nombres sin acción en la historia", lambda v: ", ".join(v.get("nombres_sin_accion") or []) or "ninguno"),
        vrow("Cifras no canónicas (F5d)", lambda v: ", ".join(v.get("cifras_no_canonicas") or []) or "ninguna"),
        vrow("Problemas de fechas (F5d)", lambda v: v.get("problemas_de_fechas", "—")),
        vrow("Datos de pantalla dichos por la voz (F5d)", lambda v: ", ".join(v.get("pantalla_dichos") or []) or "ninguno"),
        vrow("Antagonista nombrado", lambda v: _ok(v["antagonista_nombrado"])),
        vrow("Cliffhangers con el dato en el cierre", lambda v: f"{sum(1 for c in v.get('cliffhangers') or [] if c['ok'])}"
                                                               f" de {len(v.get('cliffhangers') or [])}"),
        vrow("Datos distintos del pool usados", lambda v: v["datos_distintos"]),
        vrow("Palabras", lambda v: v["palabras"]),
        vrow("Umbrales que pasa", lambda v: f"{sum(1 for x in v['umbral'].values() if x)} de {len(v['umbral'])}"),
    ])
    video_head = ("<tr><th></th><th>v1</th>" + ("<th>v2 F5</th>" if v5 else "") + ("<th>v2 F5b</th>" if vb else "")
                  + ("<th>v2 F5c</th>" if vc else "") + "<th>v2 F5d</th></tr>")
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
                          f'{len(c["datos_usados"])} datos ({"por id" if c.get("conteo") == "por_id" else "regex"})'
                          + (" · repetidos en el cap: " + ", ".join(f"«{f}» ×{n}" for f, n in c["repetidos_en_cap"])
                             if c.get("repetidos_en_cap") else "")
                          + (" · nombres sin acción: " + ", ".join(c["nombres_sin_accion"])
                             if c.get("nombres_sin_accion") else "") + '</p>')
        decl = (f'<p class="m">ids declarados por el narrador: {", ".join(dec2.get(k) or []) or "—"}</p>'
                if dec2.get(k) is not None else "")
        caps_html.append(f"""
<section class="cap"><h2>Cap {k}</h2>
<div class="pair">
 <div><h3>v1 · {html.escape(t1)}</h3>{metr(c1)}<p class="txt">{highlight(n1[k], c1['datos_usados'], its)}</p></div>
 <div><h3>v2 F5d · {html.escape(t2)}</h3>{metr(c2)}{decl}<p class="txt">{highlight(n2[k], c2['datos_usados'], its)}</p>{cliff}</div>
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
    desc = "".join(f"<tr><td>{html.escape(d.get('kind') or '')}</td><td>{html.escape(d.get('texto') or '')}</td>"
                   f"<td>{html.escape(d.get('bloque') or '')}</td><td>{html.escape(d.get('motivo') or '')}</td></tr>"
                   for d in pool.get("_descartados") or [])
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
<p class="sub">F5d. v1 = el guion producido (10 verified_facts). v2 F5d = mismo research y evidence_pool, skeleton
congelado de F5 con cifras canónicas y datos reservados para pantalla, narrador Gemini Pro con el mejor de 3 por cap.
«v2 F5», «v2 F5b» y «v2 F5c» son las versiones anteriores
({sum(1 for x in its.values() if x['_kind'] in ('datos','cronologia','citas'))} datos, eventos y citas). Las métricas usan el mismo pool para
las versiones (la columna «v2 F5» se mide por regex con el pool nuevo: no declaraba ids). Datos
resaltados en el texto: <mark>así</mark> (el número chico es el id del pool).</p>
<h2>Por video</h2><div class="scroll"><table><thead>{video_head}</thead><tbody>{video_tbl}</tbody></table></div>
<h2>Personajes de v2</h2><ul>{pers}</ul>
{''.join(caps_html)}
<h2>evidence_pool — qué dato usó cada versión</h2><div class="scroll"><table><thead><tr><th>id</th><th>tipo</th><th>texto (literal del research)</th><th>fecha</th><th>fuente</th><th>caps v1</th><th>caps v2</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table></div>
<h2>Lo que el filtro del pool sacó (F5b N1 y N5)</h2><div class="scroll"><table><thead><tr><th>tipo</th><th>texto</th><th>bloque</th><th>motivo</th></tr></thead>
<tbody>{desc or '<tr><td colspan="4">nada</td></tr>'}</tbody></table></div>
</main></body></html>"""
    OUT.write_text(page, encoding="utf-8")
    print(f"{OUT} · v1 usa {len(used1)} datos del pool, v2 usa {len(used2)}")


if __name__ == "__main__":
    main()
