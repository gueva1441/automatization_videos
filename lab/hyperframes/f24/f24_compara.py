"""F24 §C — compara_f24.html y resumen_f24.json: Pennhurst | Vajont, cap por cap, con lo que quedó en disco (sin API).
Por cap: intent (de los beats), beats, palabras (guion y después de la partición), personas con nombre, citas, fechas
literales (métrica en dígitos · día + mes dichos en letras) y el texto lado a lado. Arriba: perfil, compuerta, humano,
antagonista, promesa y costo por paso.
Uso: python -I lab/hyperframes/f24/f24_compara.py
"""
from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LAB = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT), str(LAB), str(LAB.parent / "f22"), str(LAB.parent / "f23")]
STEPS = ROOT / "data" / "scripts" / "_steps"
TEMAS = {"pennhurst": "4ac37187-pennhurst", "vajont": "f8s3-vajont"}
MESES = "enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre"
FECHA_LETRAS = re.compile(r"\b(?:\d{1,2}|uno|dos|tres|cuatro|cinco|seis|siete|ocho|nueve|diez|once|doce|trece|catorce|"
                          r"quince|dieciséis|diecisiete|dieciocho|diecinueve|veinte|veinti\w+|treinta(?: y uno)?) de "
                          rf"(?:{MESES})\b", re.I)


def _j(p: Path):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def _e(x) -> str:
    return html.escape(str(x if x is not None else "—"))


def vista(tema: str) -> dict | None:
    from f23_compara import TRAILER
    from script_engine import m01b_guionista as mg
    from script_engine.m01a_escaleta import intent_de_cap
    d = LAB / tema
    g, esc = _j(d / "guion.json"), _j(d / "escaleta.json")
    if not (g and esc and g.get("parrafos")):
        return None
    caps = {c["chapter_number"]: c["narration"] for c in mg.caps_text(esc, g["parrafos"])}
    nar = _j(STEPS / TEMAS[tema] / "01b_narration.json") or {"chapters": []}
    sk = _j(STEPS / TEMAS[tema] / "01a_skeleton.json") or {"chapters": []}
    post = {c["chapter_number"]: c["narration"] for c in nar["chapters"]}
    tit = {c["chapter_number"]: c.get("title") for c in sk["chapters"]}
    m = g["metricas"]
    pc = {}
    for n in range(1, 8):
        k = str(n)
        pc[n] = {"intent": intent_de_cap(esc, n), "titulo": tit.get(n),
                 "beats": [f"{b['funcion']} {b['intensidad']}" for b in esc["beats"] if b["cap"] == n],
                 "palabras": m["palabras_por_cap"].get(k), "palabras_particion": len((post.get(n) or "").split()),
                 "personas": m["personas_por_cap"].get(k) or [], "citas": m["citas_por_cap"].get(k),
                 "fechas": m["fechas_literales_por_cap"].get(k), "fechas_letras": FECHA_LETRAS.findall(caps.get(n) or ""),
                 "texto": caps.get(n)}
    return {"metricas": {k: v for k, v in m.items() if not k.endswith("_por_cap")}, "bloqueantes": g["bloqueantes"],
            "reparacion": g.get("reparacion"), "por_cap": pc, "promesa": esc.get("promesa_gancho"),
            "humano": (esc.get("humano") or {}).get("nombre"), "antagonista": esc.get("antagonista"),
            "trailer_gancho": sorted({x.group(0) for x in TRAILER.finditer(caps.get(1) or "")})}


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    costos = _j(LAB / "costos_f24.json") or {"etapas": []}
    V = {t: vista(t) for t in TEMAS}
    R = {t: _j(LAB / t / "research.json") or {} for t in TEMAS}
    P = {t: _j(STEPS / TEMAS[t] / "_perfil.json") or {} for t in TEMAS}
    body = []
    rows = [("perfil", *(f"{P[t].get('anio_inicio')}–{P[t].get('anio_fin')} {P[t].get('tipo_evento')} · "
                         f"{', '.join(P[t].get('idiomas_research') or [])}" for t in TEMAS)),
            ("compuerta", *(f"{(R[t].get('gate') or {}).get('color')} {(R[t].get('gate') or {}).get('metricas')}"
                            for t in TEMAS)),
            ("documentos en el pool", *(len(R[t].get("docs") or []) for t in TEMAS)),
            ("humano", *((V[t] or {}).get("humano") for t in TEMAS)),
            ("antagonista", *(((V[t] or {}).get("antagonista") or {}).get("nombre") for t in TEMAS)),
            ("promesa", *((V[t] or {}).get("promesa") for t in TEMAS)),
            ("palabras · minutos", *(f"{(V[t] or {}).get('metricas', {}).get('palabras')} · "
                                     f"{(V[t] or {}).get('metricas', {}).get('minutos')}" for t in TEMAS)),
            ("bloqueantes del guion", *("; ".join(b["motivo"] for b in (V[t] or {}).get("bloqueantes") or []) or "0"
                                        for t in TEMAS)),
            ("citas · duras de v3 (métrica)", *(f"{(V[t] or {}).get('metricas', {}).get('citas')} · "
                                                f"{(V[t] or {}).get('metricas', {}).get('duras_v3')}" for t in TEMAS)),
            ("frases de tráiler en el gancho", *(", ".join((V[t] or {}).get("trailer_gancho") or []) or "ninguna"
                                                 for t in TEMAS))]
    body.append("<table><tr><th></th><th>Pennhurst</th><th>Vajont</th></tr>" + "".join(
        f"<tr><td>{_e(a)}</td><td>{_e(b)}</td><td>{_e(c)}</td></tr>" for a, b, c in rows) + "</table>")
    body.append("<h2>Por cap</h2><table><tr><th>cap</th><th>intent · beats</th><th>palabras (guion → partición)</th>"
                "<th>personas con nombre</th><th>citas</th><th>fechas (dígitos · letras)</th></tr>")
    for n in range(1, 8):
        cel = []
        for t in TEMAS:
            c = ((V[t] or {}).get("por_cap") or {}).get(n) or {}
            cel.append(c)
        def celda(c: dict, k: str) -> str:
            if k == "intent":
                return f"{c.get('intent')} · {', '.join(c.get('beats') or [])}"
            if k == "palabras":
                return f"{c.get('palabras')} → {c.get('palabras_particion')}"
            if k == "fechas":
                return f"{c.get('fechas')} · {len(c.get('fechas_letras') or [])}"
            v = c.get(k)
            return ", ".join(v) or "—" if isinstance(v, list) else str(v)
        body.append(f"<tr><td>{n}</td>" + "".join(
            "<td>" + _e(" | ".join(celda(c, k) for c in cel)) + "</td>"
            for k in ("intent", "palabras", "personas", "citas", "fechas")) + "</tr>")
    body.append("</table><p class=dim>Cada celda: Pennhurst | Vajont. Palabras: el guion v4 → después de la partición "
                "(m01d mueve o acorta párrafos por la banda de caracteres).</p>")
    for n in range(1, 8):
        ts = [((V[t] or {}).get("por_cap") or {}).get(n) or {} for t in TEMAS]
        body.append(f"<details{' open' if n == 1 else ''}><summary>Cap {n}: {_e(ts[0].get('titulo'))} | "
                    f"{_e(ts[1].get('titulo'))}</summary><div class=two>"
                    + "".join(f"<div><h4>{t}</h4><p>{_e(c.get('texto'))}</p></div>" for t, c in zip(TEMAS, ts))
                    + "</div></details>")
    body.append("<h2>Costo por paso</h2><table><tr><th>tema</th><th>paso</th><th>US$</th><th>s</th></tr>" + "".join(
        f"<tr><td>{_e(x['tema'])}</td><td>{_e(x['etapa'])}</td><td>{x['usd']:.4f}</td><td>{x['segundos']:.0f}</td></tr>"
        for x in costos["etapas"]) + f"<tr><td colspan=2><b>total</b></td><td><b>{costos.get('usd_total', 0):.4f}"
        "</b></td><td></td></tr></table>")
    page = f"""<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>Compara F24</title>
<style>
:root{{--bg:#fbfaf7;--fg:#1d1d1b;--dim:#6b6b66;--line:#ddd9cf;--card:#fff}}
@media (prefers-color-scheme: dark){{:root{{--bg:#16161a;--fg:#e8e6e1;--dim:#9a988f;--line:#34343a;--card:#1e1e23}}}}
body{{background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,sans-serif;margin:0 auto;max-width:1100px;padding:16px}}
h1{{font-size:1.4em}} h2{{margin-top:2em;border-bottom:1px solid var(--line)}} .dim{{color:var(--dim)}}
table{{border-collapse:collapse;width:100%;display:block;overflow-x:auto;margin:.6em 0}}
th,td{{border:1px solid var(--line);padding:4px 8px;vertical-align:top;text-align:left}}
details{{margin:.3em 0}} .two{{display:grid;grid-template-columns:1fr 1fr;gap:12px}}
@media (max-width:700px){{.two{{grid-template-columns:1fr}}}}
</style></head><body>
<h1>F24 — dos temas nuevos de la semilla al guion: Pennhurst | Vajont</h1>
<p class=dim>Perfil → research v3 (con el registro de fuentes) → compuerta → ficha v2.2 (Sol) → escaleta f24-1 sin columna
(Sol) → guion v5.3 (Fable 5.1) → reparación → partición. Sin tocar código de producción.</p>
{chr(10).join(body)}
</body></html>"""
    (LAB / "compara_f24.html").write_text(page, encoding="utf-8")
    _j_out = {t: {k: v for k, v in (V[t] or {}).items() if k != "por_cap"} | {"por_cap": {
        n: {k: v for k, v in c.items() if k != "texto"} for n, c in ((V[t] or {}).get("por_cap") or {}).items()}}
        for t in TEMAS}
    (LAB / "resumen_f24.json").write_text(json.dumps(_j_out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print("compara_f24.html y resumen_f24.json")


if __name__ == "__main__":
    main()
