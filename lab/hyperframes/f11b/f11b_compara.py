"""F11b §2 — compara_f11b.html (Ycuá): v3 (v1), Gemini v4 A (F11), GPT Sol medio (prueba del analista), y las tres
corridas v4b (gem, sol, astra). Todo se re-mide con el código de hoy (bloqueantes a–e, duras v3, ids por beat), así
las seis filas son comparables. Las marcas de color salen de lab/hyperframes/f11/f11_compara.py (solo lectura, no son
reglas). Deja además `resumen_f11b.json` (lo que lee el reporte).
Uso: python -I lab/hyperframes/f11b/f11b_compara.py
"""
from __future__ import annotations

import html
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
LAB = Path(__file__).resolve().parent
sys.path.insert(1, str(LAB.parent / "f11"))                 # f11_compara (marcas); -I no agrega la carpeta del script
TID = "f8s1-ycua-bolanos"
MIN_W, MAX_W, MAX_BLQ = 1350, 1700, 2                        # criterio §2 (lo decide Omar con el analista)


def _j(p: Path):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def _prep(ps: list[dict], esc: dict) -> list[dict]:
    from script_engine import evidence as ev
    bc = {b["n"]: b["cap"] for b in esc["beats"]}
    return [{**p, "beat": int(p["beat"]), "cap": p.get("cap") or bc.get(int(p["beat"]), 0),
             "texto": ev.fix_glued_caps(str(p["texto"]).strip())} for p in ps]


def versiones(topic: dict, esc: dict) -> list[dict]:
    """[{nombre, clave, parrafos, declared, usd, segundos, extra}] en el orden de la tabla."""
    import gpt_helpers
    steps = ROOT / "data" / "scripts" / "_steps" / TID
    out = []
    v1 = _j(steps / "01b_editor_v3_v1.json")
    out.append({"nombre": "v3 (v1)", "clave": "v1", "parrafos": _prep(v1["parrafos"], esc), "declared": True,
                "usd": 0.88, "usd_nota": "guion F10 (ESTADO_SESION)", "segundos": None})
    a = _j(LAB.parent / "f11" / "guion_ycua_v4A.json")
    out.append({"nombre": "Gemini v4 A (F11)", "clave": "v4A", "parrafos": a["reparacion"]["parrafos"],
                "declared": False, "usd": a["costo"]["usd"], "segundos": a["costo"]["segundos"], "run": a})
    g = _j(ROOT / "lab" / "_gpt_probe_analista" / "ycua_gpt.json")
    out.append({"nombre": "GPT Sol medio (prueba del analista)", "clave": "probe", "parrafos": _prep(g["parrafos"], esc),
                "declared": False, "usd": round(gpt_helpers.cost_of("gpt-6.1-sol", g["usage"]), 4),
                "segundos": g["segundos"], "usd_nota": "usage × precio, sin reparación ni juez"})
    for tag, name in (("gem", "v4b gem · Gemini Pro"), ("sol", "v4b sol · gpt-6.1-sol high"),
                      ("astra", "v4b astra · gpt-6-astra")):
        r = _j(LAB / f"guion_ycua_v4b_{tag}.json")
        if not r:
            continue
        ps = (r.get("reparacion") or {}).get("parrafos")
        out.append({"nombre": name, "clave": tag, "parrafos": ps or [], "declared": False, "usd": r["costo"]["usd"],
                    "segundos": r["costo"]["segundos"], "run": r, "error": r.get("error")})
        if r.get("crudo"):
            usd_g = sum(c["usd"] for c in r["costo"]["llamadas"] if c["desc"] == "guion_v4 guionista")
            out.append({"nombre": f"{name} — crudo, antes de reparar", "clave": f"{tag}_crudo", "crudo": True,
                        "parrafos": r["crudo"], "declared": False, "usd": usd_g,
                        "segundos": r.get("segundos_guionista")})
    return out


def medir(topic: dict, esc: dict, v: dict) -> dict:
    from script_engine import guion_v4 as g4
    ps = v["parrafos"]
    if not ps:
        return {"bloqueantes": [], "metricas": None}
    return {"bloqueantes": g4.bloqueantes(topic, esc, ps), "metricas": g4.metricas(topic, esc, ps, declared=v["declared"]),
            "parrafos_ids": ps if v["declared"] else g4.with_ids(ps, topic["evidence_pool"], esc)}


def criterio(m: dict, bl: list) -> bool:
    caps = m["palabras_por_cap"]
    vacios = [n for n in range(1, 8) if not (caps.get(n) or caps.get(str(n)) or [0])[0]]
    return len(bl) <= MAX_BLQ and MIN_W <= m["palabras"] <= MAX_W and not vacios


def fila(v: dict, med: dict) -> str:
    m, bl = med["metricas"], med["bloqueantes"]
    if not m:
        return (f"<tr><th>{html.escape(v['nombre'])}</th><td colspan='9' class='bad'>"
                f"{html.escape(v.get('error') or 'sin texto')}</td></tr>")
    caps = " ".join(
        f"<span class='{'ok' if tg and 0.75 <= w / tg <= 1.25 else 'bad'}'>{w}/{tg}</span>"
        for w, tg in (m["palabras_por_cap"].get(n) or m["palabras_por_cap"].get(str(n)) or [0, 0] for n in range(1, 8)))
    ipp = m["ids_por_parrafo"]
    usd = f"{v['usd']:.3f}" if v.get("usd") is not None else "—"
    seg = f"{v['segundos']:.0f}" if v.get("segundos") is not None else "—"
    ok = criterio(m, bl)
    return (f"<tr{' class=crudo' if v.get('crudo') else ''}><th>{html.escape(v['nombre'])}</th>"
            f"<td class='n'>{m['palabras']}</td><td class='caps'>{caps}</td>"
            f"<td class='n'>{len(bl)}</td><td class='n'>{len(m['duras_v3'])}</td><td>{m['cierre']}</td>"
            f"<td class='n'>{ipp['antes']} → {ipp['despues']}</td><td class='n'>{usd}</td><td class='n'>{seg}</td>"
            f"<td class='{'ok' if ok else 'bad'}'>{'cumple' if ok else 'no'}</td></tr>")


def cap_block(n: int, vs: list[dict], meds: list[dict], pool: dict) -> str:
    from f11_compara import cap_cell, spans
    out = [f"<h3>Cap {n}</h3>"]
    for v, med in zip(vs, meds):
        m = med["metricas"]
        if not m:
            continue
        ps = med["parrafos_ids"]
        w, tg = m["palabras_por_cap"].get(n) or m["palabras_por_cap"].get(str(n)) or [0, 0]
        nb = len([x for x in med["bloqueantes"] if x.get("cap") == n])
        out.append(f"<details><summary>{html.escape(v['nombre'])} <small>· {w}/{tg} palabras · {nb} bloqueante(s)"
                   f"</small></summary><div class='col'>{cap_cell(n, ps, spans(ps, pool, med['bloqueantes']), med['bloqueantes'], m)}"
                   + "".join(f"<p class='ids'>b{p['beat']} ids: {', '.join(p.get('ids_usados') or []) or '—'}</p>"
                             for p in ps if p["cap"] == n)
                   + "</div></details>")
    return "".join(out)


def reparacion(v: dict) -> dict | None:
    r = (v.get("run") or {}).get("reparacion")
    if not r:
        return None
    p = r["pasos"]
    return {"bloqueantes": [len(r["bloqueantes_antes"]), len(r["bloqueantes_despues"])],
            "regenerados": [{"cap": x["cap"], "cambio": x["cambio"], "palabras": x["palabras"], "notas": x["notas"]}
                            for x in p["regenerados"]],
            "ediciones": [{"beat": x["beat"], "aceptada": x["aceptada"], "motivo_rechazo": x["motivo_rechazo"],
                           "problemas": [y["motivo"] for y in x["problemas"]]} for x in p["ediciones"]],
            "fechas": p["fechas"],
            "editor": [{"beat": x.get("beat"), "estado": x["estado"], "motivo_rechazo": x.get("motivo_rechazo")}
                       for x in p["editor"]],
            "palabras": [v["run"]["metricas_crudo"]["palabras"], v["run"]["metricas"]["palabras"]],
            "log": v["run"].get("log")}


CSS_EXTRA = """
.caps span{display:inline-block;margin-right:4px;font-variant-numeric:tabular-nums}.ids{font:12px system-ui,sans-serif;
color:var(--mut);margin:.2em 0}details{border:1px solid var(--line);border-radius:8px;padding:6px 10px;margin:.4em 0;
background:var(--card)}details .col{border:0;padding:4px 0}table.sum{min-width:860px}table.sum th{white-space:nowrap}
tr.crudo th,tr.crudo td{color:var(--mut);font-style:italic}
"""


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    from f11_compara import CSS
    sys.path.insert(1, str(LAB))
    from f11b_corridas import _load
    topic, esc = _load()
    pool = topic["evidence_pool"]
    vs = versiones(topic, esc)
    meds = [medir(topic, esc, v) for v in vs]
    costos = _j(LAB / "costos_f11b.json") or {}
    head = (
        "<h1>Ycuá · guion v4b: largo + tres modelos (F11b)</h1>"
        f"<p class='meta'>Escaleta fija <code>01a_escaleta_v1.json</code> (md5 e1ba1a48…), sin notas. Las tres v4b usan "
        f"el mismo prompt (<code>prompt_ycua_v4b.txt</code>). Todo re-medido con el código de hoy. Criterio §2: "
        f"bloqueantes ≤ {MAX_BLQ}, {MIN_W:,}–{MAX_W:,} palabras, sin caps vacíos (la nota la da el analista). "
        f"Costo de la tanda F11b: US$ {costos.get('usd_total', 0):.3f} (tope 2.00).</p>"
        "<p class='meta legend'><mark class='blq'>bloqueante</mark><mark class='fecha'>fecha repetida</mark>"
        "<mark class='juicio'>juicio de la lista</mark><mark class='eco'>eco después de cita</mark>"
        "<mark class='trailer'>voz de tráiler</mark> · las marcas que no son bloqueantes no rechazan nada. Por cap: "
        "palabras / objetivo (verde dentro de ±25 %).</p>")
    tabla = ("<div class='scroll'><table class='sum'><tr><th>versión</th><th>palabras</th><th>por cap / objetivo</th>"
             "<th>bloq.</th><th>duras v3</th><th>cierre</th><th>ids/párrafo antes → después</th><th>US$</th>"
             "<th>seg.</th><th>criterio</th></tr>" + "".join(fila(v, m) for v, m in zip(vs, meds)) + "</table></div>")
    blq = []
    for v, med in zip(vs, meds):
        if med["bloqueantes"]:
            blq.append(f"<details><summary>{html.escape(v['nombre'])} · {len(med['bloqueantes'])} bloqueante(s)</summary>"
                       "<ul class='blq'>" + "".join(
                           f"<li>({x['codigo']}) cap {x['cap']} beat {x['beat']}: {html.escape(x['motivo'])}</li>"
                           for x in med["bloqueantes"]) + "</ul></details>")
    caps = "".join(cap_block(n, vs, meds, pool) for n in range(1, 8))
    body = f"{head}<h2>Resumen</h2>{tabla}<h2>Bloqueantes</h2>{''.join(blq)}<h2>Texto por cap</h2>{caps}"
    doc = (f"<!doctype html><html lang='es'><head><meta charset='utf-8'><meta name='viewport' "
           f"content='width=device-width,initial-scale=1'><title>Guion v4b Ycuá</title><style>{CSS}{CSS_EXTRA}</style>"
           f"</head><body>{body}</body></html>")
    (LAB / "compara_f11b.html").write_text(doc, encoding="utf-8")
    res = []
    for v, med in zip(vs, meds):
        m = med["metricas"]
        res.append({"nombre": v["nombre"], "clave": v["clave"], "error": v.get("error"),
                    "usd": v.get("usd"), "segundos": v.get("segundos"),
                    "bloqueantes": med["bloqueantes"], "criterio": criterio(m, med["bloqueantes"]) if m else False,
                    "metricas": {k: m[k] for k in ("palabras", "palabras_por_cap", "cierre", "ids_por_parrafo", "citas",
                                                   "humano_caps")} | {"duras_v3": m["duras_v3"]} if m else None,
                    "reparacion": reparacion(v), "juez": (v.get("run") or {}).get("juez")})
    (LAB / "resumen_f11b.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    for r in res:
        m = r["metricas"] or {}
        print(f"{r['nombre']:40} {m.get('palabras', '—'):>5} palabras · bloq {len(r['bloqueantes'])} · "
              f"duras {len(m.get('duras_v3') or [])} · ids {m.get('ids_por_parrafo')} · criterio {r['criterio']}")
    print("compara_f11b.html", len(doc))


if __name__ == "__main__":
    main()
