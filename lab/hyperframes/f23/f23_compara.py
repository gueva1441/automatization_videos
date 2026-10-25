"""F23 §2 — compara_f23.html y resumen_f23.json, con lo que quedó en disco (sin API).

    F22d  pool y ficha de F22 (`00_pool_v3_f22.json`, `f22/ficha_kyshtym_f22.json`) → escaleta f22-1 sin columna (Sol)
          → guion v5.2 con Fable 5.1 (`guion_kyshtym_f22d_fable.json`: el mismo modelo que F23; el de Opus va aparte).
    F23   perfil nuevo → research v3 → compuerta → ficha v2.2 → escaleta f22-2 sin columna → guion v5.3 (Fable 5.1).
Por cap: intent, palabras, personas con nombre, citas, fechas literales, bloqueantes, y el texto lado a lado.
Uso: python -I lab/hyperframes/f23/f23_compara.py
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
sys.path[:0] = [str(ROOT), str(LAB), str(HF / "f22")]
STEPS = ROOT / "data" / "scripts" / "_steps"
KYS = "f18-kyshtym-mayak"
# Frases de tráiler (lo que f22-2 saca del gancho): anuncian lo que viene en vez de mostrarlo
TRAILER = re.compile(r"\b(en este video|vas a ver|vamos a ver|veremos|lo que viene|te voy a contar|te cuento|"
                     r"descubriremos|vamos a descubrir|esta es la historia de|quédate|acompáñanos|a continuación)\b", re.I)


def _j(p: Path):
    return json.loads(p.read_text(encoding="utf-8")) if p and p.exists() else None


def _e(x) -> str:
    return html.escape(str(x if x is not None else "—"))


def vista(g: dict | None, esc: dict | None, ficha: dict, pool: dict) -> dict | None:
    from f22_compara import guion_view
    from script_engine import m01b_guionista as mg
    from script_engine.guion_v3_reglas import fechas_literales_por_cap
    from script_engine.m01a_escaleta import intent_de_cap
    v = guion_view("kyshtym", g, esc, ficha, pool)
    if not v:
        return None
    caps = mg.caps_text(esc, g["parrafos"])
    fl = fechas_literales_por_cap(caps)
    fijos = {c.get("chapter_number"): c.get("narrative_intent") for c in esc.get("caps") or []}
    for n, c in v["por_cap"].items():
        c["fechas"] = fl.get(n, 0)
        c["intent"] = intent_de_cap(esc, n)
        c["intent_escaleta"] = fijos.get(n)
    v["trailer_gancho"] = sorted({m.group(0) for m in TRAILER.finditer(v["por_cap"].get(1, {}).get("texto") or "")})
    v["citas"] = (g.get("metricas") or {}).get("citas")
    return v


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    from script_engine.m01a_skeleton import DEFAULT_INTENT_BY_CAP
    d = STEPS / KYS
    costos = _j(LAB / "costos_f23.json") or {"etapas": [], "usd_total": 0.0}
    antes = vista(_j(HF / "f22d" / "guion_kyshtym_f22d_fable.json"), _j(HF / "f22d" / "escaleta_kyshtym_f22d.json"),
                  _j(HF / "f22" / "ficha_kyshtym_f22.json") or {}, _j(d / "00_pool_v3_f22.json") or {})
    ahora = vista(_j(LAB / "guion_kyshtym_f23.json"), _j(LAB / "escaleta_kyshtym_f23.json"),
                  _j(d / "ficha_caso.json") or {}, _j(d / "00_pool_v3.json") or {})
    from researcher_steps import pool_gate as pg
    pool22 = _j(d / "00_pool_v3_f22.json") or {}
    gate_a = pool22.get("_pool_gate") or {}
    gate_a2 = pg.evaluate(pool22) if pool22 else {}
    res = _j(LAB / "kyshtym_research_f23.json") or {}
    gate_b = res.get("gate") or {}
    body: list[str] = ["<h2>Compuerta</h2><table><tr><th></th><th>color</th><th>medidas</th></tr>" + "".join(
        f"<tr><td>{_e(k)}</td><td>{_e(g.get('color'))}</td><td>{_e(g.get('metricas'))}</td></tr>" for k, g in (
            ("pool F22, compuerta de F22 (lo guardado)", gate_a), ("pool F22, compuerta de F23", gate_a2),
            ("pool F23, compuerta de F23", gate_b))) + "</table>"]
    a, b = antes or {}, ahora or {}
    rows = [("compuerta", gate_a.get("color"), gate_b.get("color")),
            ("palabras · minutos", f"{a.get('palabras')} · {a.get('minutos')}", f"{b.get('palabras')} · {b.get('minutos')}"),
            ("bloqueantes del guion", a.get("bloqueantes"), b.get("bloqueantes")),
            ("citas en el guion", a.get("citas"), b.get("citas")),
            ("prompt del guion", a.get("prompt_version"), b.get("prompt_version")),
            ("humano (escaleta)", a.get("humano"), b.get("humano")),
            ("personas con nombre en el guion", len(a.get("personas_total") or []), len(b.get("personas_total") or [])),
            ("frases de tráiler en el gancho", ", ".join(a.get("trailer_gancho") or []) or "ninguna",
             ", ".join(b.get("trailer_gancho") or []) or "ninguna")]
    body.append("<table><tr><th></th><th>F22d (Fable, v5.2)</th><th>F23 (Fable, v5.3)</th></tr>"
                + "".join(f"<tr><td>{_e(k)}</td><td>{_e(x)}</td><td>{_e(y)}</td></tr>" for k, x, y in rows) + "</table>")
    if antes or ahora:
        body.append("<h2>Por cap</h2><table><tr><th>cap</th><th>intent (fijo → F22d | F23)</th><th>palabras</th>"
                    "<th>personas con nombre</th><th>citas</th><th>fechas literales</th><th>bloqueantes</th></tr>")
        for n in range(1, 8):
            x, y = (a.get("por_cap") or {}).get(n) or {}, (b.get("por_cap") or {}).get(n) or {}
            cel = []
            for k in ("palabras", "personas", "citas", "fechas", "bloqueantes"):
                f = [", ".join(map(str, z.get(k))) or "—" if isinstance(z.get(k), list) else z.get(k) for z in (x, y)]
                cel.append(f"<td>{_e(f[0])} | <b>{_e(f[1])}</b></td>")
            body.append(f"<tr><td>{n}</td><td>{_e(DEFAULT_INTENT_BY_CAP.get(n))} → {_e(x.get('intent'))} | "
                        f"<b>{_e(y.get('intent'))}</b></td>{''.join(cel)}</tr>")
        body.append("</table><p class=dim>Cada celda: F22d | <b>F23</b>. Intent: el fijo de m01a_skeleton → el que se "
                    "deriva de las funciones de los beats de cada escaleta (§1.3).</p>")
        for n in range(1, 8):
            body.append(f"<details{' open' if n == 1 else ''}><summary>Cap {n}: texto lado a lado</summary><div class=two>"
                        f"<div><h4>F22d</h4><p>{_e(((a.get('por_cap') or {}).get(n) or {}).get('texto'))}</p></div>"
                        f"<div><h4>F23</h4><p>{_e(((b.get('por_cap') or {}).get(n) or {}).get('texto'))}</p></div></div>"
                        "</details>")
    for nom, v in (("F23", ahora),):
        if v and v["bloqueantes_lista"]:
            body.append(f"<h3>Bloqueantes del guion {nom}</h3><ul>" + "".join(
                f"<li>({_e(x.get('codigo'))}) cap {_e(x.get('cap'))}: {_e(x.get('motivo'))}</li>"
                for x in v["bloqueantes_lista"]) + "</ul>")
    body.append("<h2>Costo por paso (F23)</h2><table><tr><th>paso</th><th>US$</th><th>s</th></tr>"
                + "".join(f"<tr><td>{_e(x['etapa'])}</td><td>{x['usd']:.4f}</td><td>{x['segundos']:.0f}</td></tr>"
                          for x in costos["etapas"])
                + f"<tr><td><b>total</b></td><td><b>{costos['usd_total']:.4f}</b></td><td></td></tr></table>")
    page = f"""<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>Compara F23</title>
<style>
:root{{--bg:#fbfaf7;--fg:#1d1d1b;--dim:#6b6b66;--line:#ddd9cf;--ok:#1f7a3a;--bad:#a8321e;--card:#fff}}
@media (prefers-color-scheme: dark){{:root{{--bg:#16161a;--fg:#e8e6e1;--dim:#9a988f;--line:#34343a;--ok:#6fcf8b;--bad:#f08a72;--card:#1e1e23}}}}
body{{background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,sans-serif;margin:0 auto;max-width:1100px;padding:16px}}
h1{{font-size:1.4em}} h2{{margin-top:2em;border-bottom:1px solid var(--line)}} .dim{{color:var(--dim)}}
table{{border-collapse:collapse;width:100%;display:block;overflow-x:auto;margin:.6em 0}}
th,td{{border:1px solid var(--line);padding:4px 8px;vertical-align:top;text-align:left}}
details{{margin:.3em 0}} .two{{display:grid;grid-template-columns:1fr 1fr;gap:12px}}
@media (max-width:700px){{.two{{grid-template-columns:1fr}}}}
</style></head><body>
<h1>F23 — Kyshtym desde la semilla: F22d | F23</h1>
<p class=dim>F22d: pool y ficha de F22 → escaleta f22-1 sin columna → guion v5.2 (Fable 5.1). F23: perfil nuevo →
research v3 → ficha v2.2 → escaleta f22-2 sin columna → guion v5.3 (Fable 5.1). Tanda F23 US$ {costos['usd_total']:.4f}
de 6.00.</p>
{chr(10).join(body)}
</body></html>"""
    (LAB / "compara_f23.html").write_text(page, encoding="utf-8")
    resumen = {"compuerta": {"f22_guardada": gate_a, "f22_con_f23": {k: gate_a2.get(k) for k in ("color", "metricas")},
                             "f23": gate_b},
               "F22d": {k: v for k, v in a.items() if k != "por_cap"}, "F23": {k: v for k, v in b.items() if k != "por_cap"},
               "por_cap": {n: {"F22d": {k: v for k, v in ((a.get("por_cap") or {}).get(n) or {}).items() if k != "texto"},
                               "F23": {k: v for k, v in ((b.get("por_cap") or {}).get(n) or {}).items() if k != "texto"}}
                           for n in range(1, 8)}, "costos": costos}
    (LAB / "resumen_f23.json").write_text(json.dumps(resumen, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print("compara_f23.html y resumen_f23.json")


if __name__ == "__main__":
    main()
