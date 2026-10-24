"""F22 §2 — compara_f22.html y resumen_f22.json, con lo que quedó en disco (sin API).

    Ycuá     antes (F17 columna con las notas de Omar · F16 escaleta v2 · F16 guion v5.1: la última cadena completa de
             Ycuá; F17 no llegó a escaleta ni guion) | F22 (columna v1.1 · escaleta v2.1 · guion v5.2), por cap.
    Kyshtym  solo F22, con la columna arriba (tal cual), el antagonista y los bloqueantes por paso.
Abajo: «cero Cardal» en cada salida y el costo por paso.
Uso: python -I lab/hyperframes/f22/f22_compara.py
"""
from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LAB = Path(__file__).resolve().parent
HF = LAB.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(1, str(LAB))
STEPS = ROOT / "data" / "scripts" / "_steps"
TID = {"ycua": "f8s1-ycua-bolanos", "kyshtym": "f18-kyshtym-mayak"}
NOMBRE = {"ycua": "Ycuá Bolaños", "kyshtym": "Kyshtym / Mayak"}


def _j(p: Path):
    return json.loads(p.read_text(encoding="utf-8")) if p and p.exists() else None


def _e(x) -> str:
    return html.escape(str(x if x is not None else "—"))


def personas_por_cap(caps: list[dict], ficha: dict) -> dict[int, list[str]]:
    """Las personas de la ficha (con nombre de persona) que la narración de cada cap nombra («nombre apellido» de su
    nombre o variantes, o el apellido si nadie más de la ficha lo comparte)."""
    from script_engine import nombres
    from script_engine.m01a_columna import personas_ficha
    ps = [p for p in personas_ficha(ficha) if nombres.es_persona(p["nombre"] or "")]     # sin mononimios
    uniq: dict[str, dict] = {}
    for p in ps:
        uniq.setdefault(p["nombre"], p)
    gente = [{"nombre": n, "variantes": p["nombres"]} for n, p in uniq.items()]
    out = {}
    for c in caps:
        out[c["chapter_number"]] = sorted({g["nombre"] for g in gente if nombres.nombra(c["narration"], g, gente)})
    return out


def guion_view(tema: str, g: dict | None, esc: dict | None, ficha: dict, pool: dict) -> dict | None:
    if not g or not g.get("parrafos") or not esc:
        return None
    from script_engine import m01b_guionista as mg
    from script_engine.guion_v3_reglas import antagonista_caps, antagonista_tipo, quotes_in
    caps = mg.caps_text(esc, g["parrafos"])
    m = g.get("metricas") or {}
    pc = personas_por_cap(caps, ficha)
    bl: dict[int, int] = {}
    for b in g.get("bloqueantes") or []:
        bl[b.get("cap") or 0] = bl.get(b.get("cap") or 0, 0) + 1
    idx = {b["n"]: b.get("escena_idx") for b in esc.get("beats") or []}
    return {"palabras": m.get("palabras"), "minutos": g.get("minutos"), "bloqueantes": len(g.get("bloqueantes") or []),
            "bloqueantes_lista": g.get("bloqueantes") or [], "prompt_version": g.get("prompt_version"),
            "antagonista": esc.get("antagonista"), "antagonista_tipo": antagonista_tipo(esc),
            "antagonista_caps": antagonista_caps(caps, esc, pool), "humano": (esc.get("humano") or {}).get("nombre"),
            "personas_total": sorted({n for v in pc.values() for n in v}),
            "escenas_usadas": sorted({x for x in idx.values() if x}),
            "por_cap": {c["chapter_number"]: {
                "palabras": len(c["narration"].split()), "personas": pc[c["chapter_number"]],
                "citas": sum(len(quotes_in(p["texto"])) for p in g["parrafos"] if p.get("cap") == c["chapter_number"]),
                "bloqueantes": bl.get(c["chapter_number"], 0),
                "escenas": sorted({idx[b["n"]] for b in esc["beats"] if b["cap"] == c["chapter_number"] and idx.get(b["n"])}),
                "texto": c["narration"]} for c in caps}}


def cardal_table(rows: list[tuple[str, Path]]) -> tuple[str, list[dict]]:
    from cero_cardal import coincidencias
    res, L = [], ["<table><tr><th>salida</th><th>coincidencias</th></tr>"]
    for nom, p in rows:
        if not p.exists():
            res.append({"salida": nom, "archivo": p.name, "existe": False})
            L.append(f"<tr><td>{_e(nom)}</td><td class=dim>no existe (no corrió)</td></tr>")
            continue
        c = coincidencias(p.read_text(encoding="utf-8"))
        res.append({"salida": nom, "archivo": p.name, "existe": True, "coincidencias": c})
        L.append(f"<tr><td>{_e(nom)} <span class=dim>{_e(p.name)}</span></td><td>"
                 + ("<b class=ok>cero Cardal</b>" if not c else f"<b class=bad>{_e(c)}</b>") + "</td></tr>")
    return "\n".join(L + ["</table>"]), res


def ag_txt(a: dict | None) -> str:
    a = a or {}
    t = a.get("tipo") or "persona"
    return "ninguno" if t == "ninguno" else f"{a.get('nombre') or a.get('id')} ({t})"


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    from script_engine.m01a_columna import to_markdown
    costos = _j(LAB / "costos_f22.json") or {"etapas": [], "usd_total": 0.0}
    resumen: dict = {"costos": costos}
    body: list[str] = []

    # ── Ycuá
    d = STEPS / TID["ycua"]
    pool = _j(d / "00_pool_v3.json") or {}
    ficha = _j(d / "ficha_caso.json") or {}
    antes = guion_view("ycua", _j(HF / "f16" / "guion_ycua_f16.json"), _j(d / "01a_escaleta_f16.json"), ficha, pool)
    esc22 = _j(d / "01a_escaleta_f22.json")
    ahora = guion_view("ycua", _j(LAB / "guion_ycua_f22.json"), esc22, ficha, pool)
    col17, col22 = _j(d / "01a_columna_f17.json") or _j(HF / "f17" / "columna_ycua_f17.json"), _j(LAB / "columna_ycua_f22.json")
    resumen["ycua"] = {"antes": {k: v for k, v in (antes or {}).items() if k != "por_cap"},
                       "f22": {k: v for k, v in (ahora or {}).items() if k != "por_cap"},
                       "columna_f17": {"humano": ((col17 or {}).get("humano") or {}).get("nombre"),
                                       "personas": ((col17 or {}).get("_metricas") or {}).get("personas_con_nombre")},
                       "columna_f22": {"humano": ((col22 or {}).get("humano") or {}).get("nombre"),
                                       "antagonista": (col22 or {}).get("antagonista"),
                                       "personas": ((col22 or {}).get("_metricas") or {}).get("personas_con_nombre")}}
    body.append(f"<h2>{NOMBRE['ycua']} — antes | F22</h2>")
    body.append("<p class=dim>Antes = la última cadena completa: columna F17 (con las notas de Omar), escaleta v2 de "
                "F16 y guion v5.1 de F16 (F17 no llegó a escaleta ni guion). F22 = columna v1.1 → escaleta v2.1 → "
                "guion v5.2, desde la misma ficha v2 de F15b.</p>")
    rows = [("humano (columna)", resumen["ycua"]["columna_f17"]["humano"], resumen["ycua"]["columna_f22"]["humano"]),
            ("quién decide (columna)", "— (la v1 no lo tenía)", ag_txt((col22 or {}).get("antagonista"))),
            ("personas con nombre (columna)", resumen["ycua"]["columna_f17"]["personas"],
             resumen["ycua"]["columna_f22"]["personas"])]
    if antes or ahora:
        a, b = antes or {}, ahora or {}
        rows += [("palabras · minutos", f"{a.get('palabras')} · {a.get('minutos')}", f"{b.get('palabras')} · {b.get('minutos')}"),
                 ("bloqueantes del guion", a.get("bloqueantes"), b.get("bloqueantes")),
                 ("humano (escaleta)", a.get("humano"), b.get("humano")),
                 ("antagonista (escaleta)", ag_txt(a.get("antagonista")), ag_txt(b.get("antagonista"))),
                 ("caps donde la voz nombra al antagonista", a.get("antagonista_caps"), b.get("antagonista_caps")),
                 ("personas con nombre en el guion", len(a.get("personas_total") or []), len(b.get("personas_total") or [])),
                 ("escenas de la ficha usadas", a.get("escenas_usadas"), b.get("escenas_usadas"))]
    body.append("<table><tr><th></th><th>antes</th><th>F22</th></tr>"
                + "".join(f"<tr><td>{_e(k)}</td><td>{_e(x)}</td><td>{_e(y)}</td></tr>" for k, x, y in rows) + "</table>")
    if antes and ahora:
        body.append("<table><tr><th>cap</th><th>palabras</th><th>personas con nombre</th><th>citas</th>"
                    "<th>bloqueantes</th><th>escenas</th></tr>")
        for n in range(1, 8):
            x, y = antes["por_cap"].get(n) or {}, ahora["por_cap"].get(n) or {}
            body.append(f"<tr><td>{n}</td>" + "".join(
                f"<td>{_e(x.get(k) if not isinstance(x.get(k), list) else ', '.join(map(str, x.get(k))) or '—')} | "
                f"<b>{_e(y.get(k) if not isinstance(y.get(k), list) else ', '.join(map(str, y.get(k))) or '—')}</b></td>"
                for k in ("palabras", "personas", "citas", "bloqueantes", "escenas")) + "</tr>")
        body.append("</table><p class=dim>Cada celda: antes | <b>F22</b>.</p>")
        for n in range(1, 8):
            body.append(f"<details><summary>Cap {n}: texto lado a lado</summary><div class=two>"
                        f"<div><h4>antes</h4><p>{_e((antes['por_cap'].get(n) or {}).get('texto'))}</p></div>"
                        f"<div><h4>F22</h4><p>{_e((ahora['por_cap'].get(n) or {}).get('texto'))}</p></div></div></details>")
    elif not ahora:
        body.append("<p class=bad>Ycuá F22 no llegó a guion (ver F22_REPORT §2).</p>")

    # ── Kyshtym
    d = STEPS / TID["kyshtym"]
    poolk = _j(d / "00_pool_v3.json") or {}
    fichak = _j(d / "ficha_caso.json") or {}
    colk = _j(LAB / "columna_kyshtym_f22.json")
    esck = _j(d / "01a_escaleta_f22.json")
    gk = _j(LAB / "guion_kyshtym_f22.json")
    vk = guion_view("kyshtym", gk, esck, fichak, poolk) if fichak.get("prompt_version") == "f22-1" else None
    body.append(f"<h2>{NOMBRE['kyshtym']} — F22 (primera vez hasta el guion)</h2>")
    if colk:
        body.append("<h3>La columna, tal cual</h3><pre>" + _e(to_markdown(colk, "Kyshtym")) + "</pre>")
    else:
        body.append("<p class=bad>No hay columna de F22.</p>")
    pasos = [("ficha", f"prompt {fichak.get('prompt_version')} · sacados {fichak.get('sacados')}"
              if fichak.get("prompt_version") == "f22-1" else "no corrió")]
    for nom, crudo in (("columna", colk), ("escaleta", esck)):
        it = (crudo or {}).get("_intentos") or []
        pasos.append((nom, " · ".join(f"intento {x['intento']}: {len(x.get('problemas', x.get('bloqueantes')) or [])} "
                                      f"{'problema(s)' if 'problemas' in x else 'bloqueante(s)'}" for x in it) or "no salió"))
    pasos.append(("guion", f"{vk['bloqueantes']} bloqueante(s) · {vk['palabras']} palabras ≈ {vk['minutos']} min · "
                           f"antagonista {ag_txt(vk['antagonista'])} nombrado en caps {vk['antagonista_caps']}"
                  if vk else "no salió"))
    body.append("<table><tr><th>paso</th><th>resultado</th></tr>"
                + "".join(f"<tr><td>{_e(a)}</td><td>{_e(b)}</td></tr>" for a, b in pasos) + "</table>")
    resumen["kyshtym"] = {"pasos": dict(pasos), "guion": {k: v for k, v in (vk or {}).items() if k != "por_cap"}}
    if vk:
        body.append("<table><tr><th>cap</th><th>palabras</th><th>personas con nombre</th><th>citas</th>"
                    "<th>bloqueantes</th><th>escenas</th></tr>")
        for n in range(1, 8):
            y = vk["por_cap"].get(n) or {}
            body.append(f"<tr><td>{n}</td>" + "".join(
                f"<td>{_e(', '.join(map(str, y.get(k))) if isinstance(y.get(k), list) else y.get(k))}</td>"
                for k in ("palabras", "personas", "citas", "bloqueantes", "escenas")) + "</tr>")
        body.append("</table>")
        for n in range(1, 8):
            body.append(f"<details><summary>Cap {n}</summary><p>{_e((vk['por_cap'].get(n) or {}).get('texto'))}</p></details>")
        if vk["bloqueantes_lista"]:
            body.append("<h3>Bloqueantes del guion</h3><ul>" + "".join(
                f"<li>({_e(b.get('codigo'))}) cap {_e(b.get('cap'))}: {_e(b.get('motivo'))}</li>"
                for b in vk["bloqueantes_lista"]) + "</ul>")

    # ── cero Cardal y costos
    filas = [(f"{t} {k}", LAB / f"{k.upper()}_{t}{'_f22' if k == 'narracion' else ''}.md")
             for t in ("ycua", "kyshtym") for k in ("columna", "escaleta", "narracion")]
    filas.insert(3, ("kyshtym ficha", LAB / "FICHA_kyshtym.md"))
    tabla, res = cardal_table(filas)
    resumen["cero_cardal"] = res
    body.append("<h2>«Cero Cardal»</h2><p class=dim>Palabras del caso inventado de los ejemplos (Cardal, Soto, "
                "Bascuñán, Quiroga, Marín, Alborada, Faros y Balizas, querosén, telegrama) en cada salida.</p>" + tabla)
    body.append("<h2>Costo por paso</h2><table><tr><th>tema</th><th>paso</th><th>US$</th><th>s</th></tr>"
                + "".join(f"<tr><td>{_e(x['tema'])}</td><td>{_e(x['etapa'])}</td><td>{x['usd']:.4f}</td>"
                          f"<td>{x['segundos']:.0f}</td></tr>" for x in costos["etapas"])
                + f"<tr><td colspan=2><b>total</b></td><td><b>{costos['usd_total']:.4f}</b></td><td></td></tr></table>")
    page = f"""<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>Compara F22</title>
<style>
:root{{--bg:#fbfaf7;--fg:#1d1d1b;--dim:#6b6b66;--line:#ddd9cf;--ok:#1f7a3a;--bad:#a8321e;--card:#fff}}
@media (prefers-color-scheme: dark){{:root{{--bg:#16161a;--fg:#e8e6e1;--dim:#9a988f;--line:#34343a;--ok:#6fcf8b;--bad:#f08a72;--card:#1e1e23}}}}
body{{background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,sans-serif;margin:0 auto;max-width:1100px;padding:16px}}
h1{{font-size:1.4em}} h2{{margin-top:2em;border-bottom:1px solid var(--line)}} .dim{{color:var(--dim)}}
.ok{{color:var(--ok)}} .bad{{color:var(--bad)}}
table{{border-collapse:collapse;width:100%;display:block;overflow-x:auto;margin:.6em 0}}
th,td{{border:1px solid var(--line);padding:4px 8px;vertical-align:top;text-align:left}}
pre{{white-space:pre-wrap;background:var(--card);border:1px solid var(--line);padding:10px;overflow-x:auto}}
details{{margin:.3em 0}} .two{{display:grid;grid-template-columns:1fr 1fr;gap:12px}}
@media (max-width:700px){{.two{{grid-template-columns:1fr}}}}
</style></head><body>
<h1>F22 — ejemplos de un caso inventado y antagonista de tres tipos</h1>
<p class=dim>Ficha v2.1 · columna v1.1 · escaleta v2.1 · guion v5.2 (gpt-6.1-sol high). Tanda US$ {costos['usd_total']:.4f}
de 3.00.</p>
{chr(10).join(body)}
</body></html>"""
    (LAB / "compara_f22.html").write_text(page, encoding="utf-8")
    (LAB / "resumen_f22.json").write_text(json.dumps(resumen, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print("compara_f22.html y resumen_f22.json")


if __name__ == "__main__":
    main()
