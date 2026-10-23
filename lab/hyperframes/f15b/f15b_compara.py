"""F15b §2 — compara_f15b.html: por tema (Ycuá, Orleans), F15 (v5) | F15b (v5.1), por cap.

Arriba de cada tema: palabras, minutos (2.05 palabras/s), párrafos, frases por párrafo (promedio), párrafos de una sola
frase, escenas que usó la escaleta (y si el gancho y el pico tienen escena), bloqueantes, duras v3, citas, preguntas,
frases de analista, humano y pico. Por cap, las dos columnas con palabras, segundos, párrafos, frases por párrafo,
bloqueantes y las frases marcadas en color (tráiler, juicio, eco). Re-medido con el código de hoy, cada versión con su
ficha. No llama a ninguna API. Deja `resumen_f15b.json`.
Uso: python -I lab/hyperframes/f15b/f15b_compara.py
"""
from __future__ import annotations

import html
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
LAB = Path(__file__).resolve().parent
for d in (LAB.parent / "f11", LAB.parent / "f11b", LAB.parent / "f11c", LAB.parent / "f13", LAB.parent / "f14",
          LAB.parent / "f15", LAB):
    sys.path.insert(1, str(d))
TEMAS = {"ycua": ("f8s1-ycua-bolanos", "Ycuá Bolaños"), "orleans": ("ba6c3cac-f7r3", "Orleans")}


def _j(p: Path):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def versiones(nom: str) -> list[dict]:
    from script_engine.m01a_skeleton import STEPS_DIR
    d = STEPS_DIR / TEMAS[nom][0]
    c15 = _j(LAB.parent / "f15" / "costos_f15.json") or {}
    c15b = _j(LAB / "costos_f15b.json") or {}
    t = {"ycua": "ycua", "orleans": "orl"}[nom]
    out = []
    for clave, lab, esc, nombre, costos in (
            ("f15", LAB.parent / "f15", "01a_escaleta_f15.json", "F15 · v5", c15),
            ("f15b", LAB, "01a_escaleta_f15b.json", "F15b · v5.1", c15b)):
        g = _j(lab / f"guion_{nom}_{clave}.json")
        if not g and clave == "f15b" and (lab / f"guion_{nom}_f15b_escf15.json").exists():
            # la escaleta F15b no salió: el guion v5.1 sobre la escaleta de F15 (sustituto)
            g, esc, nombre = _j(lab / f"guion_{nom}_f15b_escf15.json"), "01a_escaleta_f15.json",                 "F15b · v5.1 sobre la escaleta F15 (la F15b no salió)"
        if not g:
            continue
        out.append({"nombre": nombre, "clave": clave, "parrafos": g.get("parrafos") or [], "esc": _j(d / esc),
                    "ficha": _j(lab / f"ficha_{nom}" / "ficha_caso.json"), "sel_nombre": f"ficha ({clave})",
                    "usd": round(sum(e["usd"] for e in costos.get("etapas") or [] if e["tema"] == t), 4),
                    "error": g.get("error")})
    return out


def parrafos_stats(ps: list[dict]) -> dict:
    from script_engine import m01b_guionista as mg
    fr = [len(mg.sentences(p["texto"])) for p in ps]
    por_cap = {}
    for n in range(1, 8):
        f = [len(mg.sentences(p["texto"])) for p in ps if p["cap"] == n]
        por_cap[n] = {"parrafos": len(f), "frases_por_parrafo": round(sum(f) / len(f), 1) if f else 0.0,
                      "de_una_frase": sum(1 for x in f if x == 1)}
    return {"parrafos": len(ps), "frases_por_parrafo": round(sum(fr) / len(fr), 1) if fr else 0.0,
            "de_una_frase": sum(1 for x in fr if x == 1), "por_cap": por_cap}


def section(nom: str) -> tuple[str, list[dict]]:
    import fase1_5 as f15
    from f11_compara import cap_cell, spans
    from f15_compara import medir
    from script_engine import evidence as ev
    tid, titulo = TEMAS[nom]
    topic = dict(f15._load_topic_by_id(tid))
    pool = topic["evidence_pool"]
    topic["_pool_ids"] = {i for i, it in ev.items(pool).items()
                          if it["_kind"] in ("datos", "cronologia", "citas", "personajes", "lugares")}
    vs = versiones(nom)
    meds = [medir(topic, v) for v in vs]
    sts = [parrafos_stats(v["parrafos"]) for v in vs]
    tabla = ("<div class='scroll'><table class='sum'><tr><th>versión</th><th>palabras</th><th>min</th><th>párrafos</th>"
             "<th>frases / párrafo</th><th>párrafos de 1 frase</th><th>escenas usadas</th><th>gancho / pico con escena</th>"
             "<th>bloq.</th><th>duras v3</th><th>citas</th><th>preguntas</th><th>frases de analista</th><th>humano</th>"
             "<th>pico</th><th>US$</th></tr>")
    res = []
    for v, m, st in zip(vs, meds, sts):
        esc = v["esc"]
        idx = {b["n"]: b.get("escena_idx") for b in esc["beats"]}
        pb = (esc.get("pico") or {}).get("beat")
        usadas = sorted({x for x in idx.values() if x})
        gp = f"{'sí' if idx.get(1) else 'no'} / {'sí' if idx.get(pb) else 'no'}"
        mm = m["metricas"]
        tabla += (f"<tr><th>{html.escape(v['nombre'])}</th><td class='n'>{mm['palabras']}</td>"
                  f"<td class='n'><b>{m['minutos']}</b></td><td class='n'>{st['parrafos']}</td>"
                  f"<td class='n'>{st['frases_por_parrafo']}</td><td class='n'>{st['de_una_frase']}</td>"
                  f"<td>{', '.join(f'E{x}' for x in usadas) or '—'}</td><td>{gp}</td>"
                  f"<td class='n'>{len(m['bloqueantes'])}</td><td class='n'>{len(mm['duras_v3'])}</td>"
                  f"<td class='n'>{mm['citas']}</td><td class='n'>{m['preguntas']}</td>"
                  f"<td class='n'>{sum(m['frases_analista'].values())}</td><td>{html.escape(m['humano'] or '—')}</td>"
                  f"<td>beat {pb} · {m['pico']['id']}</td><td class='n'>{v['usd']:.3f}</td></tr>")
        res.append({"tema": nom, "clave": v["clave"], "nombre": v["nombre"], "usd": v["usd"], "error": v.get("error"),
                    "palabras": mm["palabras"], "minutos": m["minutos"], "palabras_por_cap": mm["palabras_por_cap"],
                    **{k: st[k] for k in ("parrafos", "frases_por_parrafo", "de_una_frase", "por_cap")},
                    "escenas_usadas": usadas, "escena_gancho": idx.get(1), "escena_pico": idx.get(pb),
                    "bloqueantes": m["bloqueantes"], "duras_v3": len(mm["duras_v3"]), "citas": mm["citas"],
                    "preguntas": m["preguntas"], "frases_analista": m["frases_analista"], "humano": m["humano"],
                    "humano_caps": mm["humano_caps"], "pico": m["pico"], "avisos": m["avisos"], "cierre": mm["cierre"],
                    "embudo": m["embudo"]})
    tabla += "</table></div>"
    caps = [f"<div class='grid hdr'><div>{html.escape(vs[0]['nombre'])}</div><div>{html.escape(vs[-1]['nombre'])}</div></div>"]
    for n in range(1, 8):
        cells = []
        for v, m, st in zip(vs, meds, sts):
            ps, mm = m["parrafos_ids"], m["metricas"]
            w = (mm["palabras_por_cap"].get(n) or [0, 0])[0]
            pc = st["por_cap"][n]
            nb = len([x for x in m["bloqueantes"] if x.get("cap") == n])
            cells.append(f"<div class='col'><p class='ids'>{w} palabras · {round(w / 2.05)} s · {pc['parrafos']} párrafos · "
                         f"{pc['frases_por_parrafo']} frases/párrafo · {pc['de_una_frase']} de 1 frase · "
                         f"{nb} bloqueante(s)</p>{cap_cell(n, ps, spans(ps, topic['evidence_pool'], m['bloqueantes']), m['bloqueantes'], mm)}</div>")
        caps.append(f"<h3>{titulo} · Cap {n}</h3><div class='grid'>{''.join(cells)}</div>")
    return f"<h2>{titulo}</h2>{tabla}{''.join(caps)}", res


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    from f11_compara import CSS
    from f11b_compara import CSS_EXTRA
    sy, ry = section("ycua")
    so, ro = section("orleans")
    costos = _j(LAB / "costos_f15b.json") or {}
    head = ("<h1>v5.1: la escena merece un párrafo (F15b)</h1>"
            "<p class='meta'>F15 = ficha v2 → escaleta F15 → guion v5. F15b = la misma ficha re-chequeada (sin llamada) → "
            "escaleta nueva (gancho y pico desde las escenas) → guion v5.1 (prompt literal del analista). Sol high, largo "
            "abierto, una llamada, sin notas, sin reparación ni editor. Minutos a 2.05 palabras/s. Costo de la tanda F15b: "
            f"US$ {costos.get('usd_total', 0):.3f} (tope 1.50); el US$ de F15 es el de su tanda completa.</p>"
            "<p class='meta legend'><mark class='blq'>bloqueante</mark><mark class='fecha'>fecha repetida</mark>"
            "<mark class='juicio'>juicio de la lista</mark><mark class='eco'>eco después de cita</mark>"
            "<mark class='trailer'>voz de tráiler</mark> · las marcas que no son bloqueantes no rechazan nada.</p>")
    css = ("@media (max-width:760px){.grid .col:first-child::before{content:'F15'}"
           ".grid .col:last-child::before{content:'F15b'}}")
    doc = (f"<!doctype html><html lang='es'><head><meta charset='utf-8'><meta name='viewport' "
           f"content='width=device-width,initial-scale=1'><title>Escena por párrafo</title><style>{CSS}{CSS_EXTRA}{css}"
           f"</style></head><body>{head}{sy}{so}</body></html>")
    (LAB / "compara_f15b.html").write_text(doc, encoding="utf-8")
    (LAB / "resumen_f15b.json").write_text(json.dumps(ry + ro, ensure_ascii=False, indent=1), encoding="utf-8")
    for r in ry + ro:
        print(f"{r['tema']:7} {r['clave']:4} {r['palabras']} pal · {r['minutos']} min · párrafos {r['parrafos']} · "
              f"frases/párr {r['frases_por_parrafo']} · de 1 frase {r['de_una_frase']} · escenas {r['escenas_usadas']} "
              f"(gancho {r['escena_gancho']}, pico {r['escena_pico']}) · bloq {len(r['bloqueantes'])} · duras "
              f"{r['duras_v3']} · citas {r['citas']} · ? {r['preguntas']} · humano {r['humano']} {r['humano_caps']} · "
              f"US$ {r['usd']}")
    print("compara_f15b.html", len(doc))


if __name__ == "__main__":
    main()
