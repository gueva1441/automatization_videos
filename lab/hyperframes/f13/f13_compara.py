"""F13 §2 — compara_f13.html: por tema (Orleans, Ycuá), largo objetivo | largo abierto, lado a lado por cap.

    objetivo  Orleans: lab/_gpt_probe_analista/orleans/orleans_v4c_sol.json (corrida del analista, f11c-1, solo lectura)
              Ycuá:    lab/hyperframes/f11c/guion_ycua_v4c_sol.json (crudo)
    abierto   lab/hyperframes/f13/guion_<tema>_f13_abierto.json

Todo se re-mide con el código de hoy: bloqueantes (cada versión con su largo), duras v3, citas, cierre. Métricas que no
rechazan nada: minutos estimados (2.05 palabras/s), preguntas, frases de analista y «repetición interna» (% de 3-gramas
de contenido, m05._trigrams, que se repiten en dos o más oraciones del mismo cap). Misma forma que compara_f11c.html.
Deja `resumen_f13.json` (lo que lee el reporte).
Uso: python -I lab/hyperframes/f13/f13_compara.py
"""
from __future__ import annotations

import html
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
LAB = Path(__file__).resolve().parent
for d in (LAB.parent / "f11", LAB.parent / "f11b", LAB.parent / "f11c", LAB):
    sys.path.insert(1, str(d))                              # -I no agrega la carpeta del script


def _j(p: Path):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def versiones(tag: str) -> list[dict]:
    if tag == "orl":
        r = _j(ROOT / "lab" / "_gpt_probe_analista" / "orleans" / "orleans_v4c_sol.json")
        obj = {"nombre": "objetivo (f11c-1, corrida del analista)", "largo": "objetivo", "parrafos": r["parrafos"],
               "usd": r["raw"]["usd"], "segundos": r["raw"]["segundos"],
               "tokens": {"in": r["raw"]["usage"]["prompt_tokens"], "out": r["raw"]["usage"]["completion_tokens"],
                          "thinking": r["raw"]["usage"]["completion_tokens_details"]["reasoning_tokens"]}}
    else:
        r = _j(LAB.parent / "f11c" / "guion_ycua_v4c_sol.json")
        g = [c for c in r["costo"]["llamadas"] if c["desc"] == "guion_v4 guionista"][0]
        obj = {"nombre": "objetivo (f11c-1, F11c sol crudo)", "largo": "objetivo", "parrafos": r["crudo"],
               "usd": g["usd"], "segundos": r.get("segundos_guionista"),
               "tokens": {"in": g["in"], "out": g["out"], "thinking": g["thinking"]}}
    tema = {"orl": "orleans", "ycua": "ycua"}[tag]
    a = _j(LAB / f"guion_{tema}_f13_abierto.json") or {}
    ga = ((a.get("costo") or {}).get("llamadas") or [{}])[0]
    abi = {"nombre": "abierto (f13-1)", "largo": "abierto", "parrafos": a.get("parrafos") or [],
           "usd": (a.get("costo") or {}).get("usd"), "segundos": (a.get("costo") or {}).get("segundos"),
           "error": a.get("error"), "tokens": {"in": ga.get("in"), "out": ga.get("out"), "thinking": ga.get("thinking")}}
    return [obj, abi]


def medir(topic: dict, esc: dict, v: dict) -> dict:
    from f11c_compara import frases_analista, preguntas
    from f13_corridas import PALABRAS_POR_SEG, repeticion_interna
    from script_engine import guion_v4 as g4
    from script_engine import m01b_guionista as mg
    ps = v["parrafos"]
    if not ps:
        return {}
    m = g4.metricas(topic, esc, ps)
    rep = {c["chapter_number"]: repeticion_interna(c["narration"]) for c in mg.caps_text(esc, ps)}
    return {"bloqueantes": g4.bloqueantes(topic, esc, ps, largo=v["largo"]), "metricas": m,
            "minutos": round(m["palabras"] / PALABRAS_POR_SEG / 60, 1), "repeticion_por_cap": rep,
            "repeticion": round(sum(rep.values()) / len(rep), 1) if rep else 0.0,
            "preguntas": preguntas(ps), "frases_analista": frases_analista(ps),
            "parrafos_ids": g4.with_ids(ps, topic["evidence_pool"], esc)}


def fila(v: dict, med: dict) -> str:
    if not med:
        return (f"<tr><th>{html.escape(v['nombre'])}</th><td colspan='11' class='bad'>"
                f"{html.escape(v.get('error') or 'sin texto')}</td></tr>")
    m = med["metricas"]
    caps = " ".join(f"{(m['palabras_por_cap'].get(n) or [0, 0])[0]}" for n in range(1, 8))
    rep = " ".join(f"{med['repeticion_por_cap'].get(n, 0):g}" for n in range(1, 8))
    usd = f"{v['usd']:.3f}" if v.get("usd") is not None else "—"
    fa = sum(med["frases_analista"].values())
    return (f"<tr><th>{html.escape(v['nombre'])}</th><td class='n'>{m['palabras']}</td>"
            f"<td class='n'><b>{med['minutos']}</b></td><td class='caps'>{caps}</td>"
            f"<td class='n'>{med['repeticion']} %</td><td class='caps'>{rep}</td>"
            f"<td class='n'>{len(med['bloqueantes'])}</td><td class='n'>{len(m['duras_v3'])}</td>"
            f"<td class='n'>{m['citas']}</td><td class='n'>{med['preguntas']}</td><td class='n'>{fa}</td>"
            f"<td>{m['cierre']}</td><td class='n'>{usd}</td></tr>")


def section(tag: str, titulo: str) -> tuple[str, list[dict]]:
    from f11_compara import cap_cell, spans
    from f13_corridas import load
    topic, esc = load(tag)
    pool = topic["evidence_pool"]
    vs = versiones(tag)
    meds = [medir(topic, esc, v) for v in vs]
    tgt = {c["chapter_number"]: c.get("palabras_objetivo") or 0 for c in esc.get("caps") or []}
    out = [f"<h2>{titulo}</h2>", "<div class='scroll'><table class='sum'><tr><th>versión</th><th>palabras</th>"
           "<th>min (2.05 p/s)</th><th>palabras por cap (1–7)</th><th>repetición interna</th><th>rep. por cap (%)</th>"
           "<th>bloq.</th><th>duras v3</th><th>citas</th><th>preguntas</th><th>frases de analista</th><th>cierre</th>"
           "<th>US$</th></tr>" + "".join(fila(v, m) for v, m in zip(vs, meds)) + "</table></div>",
           "<p class='meta'>Objetivo de la escaleta por cap: " + " · ".join(f"{n}: {tgt.get(n, 0)}" for n in range(1, 8))
           + " (el abierto no lo recibió).</p>"]
    for v, med in zip(vs, meds):
        if med and med["bloqueantes"]:
            out.append(f"<details><summary>{html.escape(v['nombre'])} · {len(med['bloqueantes'])} bloqueante(s)"
                       "</summary><ul class='blq'>" + "".join(
                           f"<li>({x['codigo']}) cap {x['cap']} beat {x['beat']}: {html.escape(x['motivo'])}</li>"
                           for x in med["bloqueantes"]) + "</ul></details>")
    out.append("<div class='grid hdr'><div>largo objetivo</div><div>largo abierto</div></div>")
    for n in range(1, 8):
        cells = []
        for v, med in zip(vs, meds):
            if not med:
                cells.append("<div class='col'>—</div>")
                continue
            ps = med["parrafos_ids"]
            m = med["metricas"]
            w = (m["palabras_por_cap"].get(n) or [0, 0])[0]
            pre = sum(p["texto"].count("?") for p in ps if p["cap"] == n)
            nb = len([x for x in med["bloqueantes"] if x.get("cap") == n])
            cells.append(f"<div class='col'><p class='ids'>{w} palabras · {round(w / 2.05)} s · "
                         f"repetición {med['repeticion_por_cap'].get(n, 0)} % · {pre} pregunta(s) · {nb} bloqueante(s)"
                         f"</p>{cap_cell(n, ps, spans(ps, pool, med['bloqueantes']), med['bloqueantes'], m)}</div>")
        out.append(f"<h3>Cap {n}</h3><div class='grid'>{''.join(cells)}</div>")
    res = [{"tema": tag, "nombre": v["nombre"], "largo": v["largo"], "usd": v.get("usd"), "segundos": v.get("segundos"),
            "tokens": v.get("tokens"), "error": v.get("error"),
            **({k: med[k] for k in ("bloqueantes", "minutos", "repeticion", "repeticion_por_cap", "preguntas",
                                    "frases_analista")}
               | {"metricas": {k: med["metricas"][k] for k in ("palabras", "palabras_por_cap", "citas", "cierre",
                                                                "humano_caps", "duras_v3")}} if med else {})}
           for v, med in zip(vs, meds)]
    return "".join(out), res


CSS_F13 = """
@media (max-width:760px){.grid .col:first-child::before{content:"objetivo"}.grid .col:last-child::before{content:"abierto"}}
"""


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    from f11_compara import CSS
    from f11b_compara import CSS_EXTRA
    costos = _j(LAB / "costos_f13.json") or {}
    so, ro = section("orl", "Orleans (ba6c3cac-f7r3 · escaleta 01a_escaleta.json, md5 2f794418…)")
    sy, ry = section("ycua", "Ycuá (f8s1-ycua-bolanos · escaleta 01a_escaleta_v1.json, md5 e1ba1a48…)")
    head = (
        "<h1>Guion v4 · largo objetivo vs largo abierto (F13)</h1>"
        "<p class='meta'>Sol high, una llamada, sin notas, sin reparación ni editor. «Objetivo» = prompt f11c-1 (≈ N "
        "palabras por cap y el total); «abierto» = f13-1 (sin cifras de largo: «Cada cap dura lo que su historia "
        "necesita: ni relleno ni resumen.»). Minutos estimados a 2.05 palabras/s. «Repetición interna» = % de 3-gramas "
        "de contenido que aparecen en dos o más oraciones del mismo cap (mide el relleno; no rechaza nada). Bloqueantes "
        "re-medidos con el código de hoy, cada versión con su largo (en abierto no se mide el ±25 %). Costo de la tanda "
        f"F13: US$ {costos.get('usd_total', 0):.3f} (tope 0.50).</p>"
        "<p class='meta legend'><mark class='blq'>bloqueante</mark><mark class='fecha'>fecha repetida</mark>"
        "<mark class='juicio'>juicio de la lista</mark><mark class='eco'>eco después de cita</mark>"
        "<mark class='trailer'>voz de tráiler</mark> · las marcas que no son bloqueantes no rechazan nada. En cada cap, "
        "«N/objetivo palabras» en verde o rojo es solo referencia contra la escaleta (en abierto no es bloqueante); "
        "«duras v3 del cap K» = K duras v3 en ese cap.</p>")
    doc = (f"<!doctype html><html lang='es'><head><meta charset='utf-8'><meta name='viewport' "
           f"content='width=device-width,initial-scale=1'><title>Guion largo abierto</title><style>{CSS}{CSS_EXTRA}"
           f"{CSS_F13}</style></head><body>{head}{so}{sy}</body></html>")
    (LAB / "compara_f13.html").write_text(doc, encoding="utf-8")
    (LAB / "resumen_f13.json").write_text(json.dumps(ro + ry, ensure_ascii=False, indent=1), encoding="utf-8")
    for r in ro + ry:
        m = r.get("metricas") or {}
        print(f"{r['tema']:5} {r['nombre']:40} {m.get('palabras', '—'):>5} pal · {r.get('minutos')} min · rep "
              f"{r.get('repeticion')} % · bloq {len(r.get('bloqueantes') or [])} · duras {len(m.get('duras_v3') or [])}"
              f" · citas {m.get('citas')} · ? {r.get('preguntas')} · US$ {r.get('usd')}")
    print("compara_f13.html", len(doc))


if __name__ == "__main__":
    main()
