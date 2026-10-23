"""F15 §2 — compara_f15.html: por tema, la mejor versión anterior | F15, por cap.

    Ycuá     F13 abierto (digest + escaleta v1, prompt f13-1)        | F15 (ficha v2 + escaleta nueva + guion v5)
    Orleans  F14 (ficha f14-1 + escaleta f14, prompt f13-1 + ficha)   | F15

Arriba de cada tema: el embudo (pool → selección → escaleta → guion), el humano y el pico que eligió cada escaleta, y la
tabla resumen (palabras, minutos a 2.05 palabras/s, bloqueantes, duras v3, citas, preguntas, frases de analista,
repetición, costo). Por cap, las dos columnas con palabras, segundos, bloqueantes, preguntas, citas y las frases
marcadas en color (tráiler, juicio, eco; las de analista se cuentan). Todo se re-mide con el código de hoy, cada versión
con su ficha (el bloqueante (d) mira la ficha desde F15 §1.4). No llama a ninguna API. Deja `resumen_f15.json`.
Uso: python -I lab/hyperframes/f15/f15_compara.py
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
for d in (LAB.parent / "f11", LAB.parent / "f11b", LAB.parent / "f11c", LAB.parent / "f13", LAB.parent / "f14", LAB):
    sys.path.insert(1, str(d))
TEMAS = {"ycua": ("f8s1-ycua-bolanos", "Ycuá Bolaños"), "orleans": ("ba6c3cac-f7r3", "Orleans")}


def _j(p: Path):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def versiones(nom: str, pool: dict) -> list[dict]:
    from script_engine.m01a_skeleton import STEPS_DIR
    tid = TEMAS[nom][0]
    d = STEPS_DIR / tid
    out = []
    if nom == "ycua":
        r = _j(LAB.parent / "f13" / "guion_ycua_f13_abierto.json")
        dig = set(re.findall(r"\b[DTQPL]\d{1,3}\b", (pool.get("digest") or {}).get("texto") or ""))
        out.append({"nombre": "F13 abierto · digest + escaleta v1", "clave": "f13", "parrafos": r["parrafos"],
                    "esc": _j(d / "01a_escaleta_v1.json"), "ficha": None, "seleccion": dig, "sel_nombre": "digest",
                    "usd": r["costo"]["usd"], "usd_nota": "solo el guion"})
    else:
        r = _j(LAB.parent / "f14" / "guion_orleans_f14.json")
        f14 = _j(LAB.parent / "f14" / "ficha_caso.json")
        c14 = _j(LAB.parent / "f14" / "costos_f14.json") or {}
        out.append({"nombre": "F14 · ficha f14 + escaleta f14", "clave": "f14", "parrafos": r["parrafos"],
                    "esc": _j(d / "01a_escaleta_f14.json"), "ficha": f14, "sel_nombre": "ficha f14",
                    "usd": c14.get("usd_total"), "usd_nota": "ficha + escaleta + guion"})
    g = _j(LAB / f"guion_{nom}_f15.json")
    ficha = _j(LAB / f"ficha_{nom}" / "ficha_caso.json")
    esc = _j(d / "01a_escaleta_f15.json")
    costos = _j(LAB / "costos_f15.json") or {}
    usd = round(sum(e["usd"] for e in costos.get("etapas") or [] if e["tema"] == {"ycua": "ycua", "orleans": "orl"}[nom]), 4)
    if g and ficha and esc:
        out.append({"nombre": "F15 · ficha v2 + escaleta nueva + guion v5", "clave": "f15",
                    "parrafos": g.get("parrafos") or [], "esc": esc, "ficha": ficha, "sel_nombre": "ficha v2",
                    "usd": usd, "usd_nota": "ficha + escaleta + guion", "error": g.get("error")})
    return out


def medir(topic: dict, v: dict) -> dict:
    from f11c_compara import frases_analista, preguntas
    from f13_corridas import PALABRAS_POR_SEG, repeticion_interna
    from f14_compara import esc_ids, ficha_ids
    from script_engine import guion_v4 as g4
    from script_engine import m01b_guionista as mg
    from script_engine.guion_v3_reglas import quotes_in
    esc, ps, pool = v["esc"], v["parrafos"], topic["evidence_pool"]
    pid = g4.with_ids(ps, pool, esc)
    m = g4.metricas(topic, esc, ps)
    rep = {c["chapter_number"]: repeticion_interna(c["narration"]) for c in mg.caps_text(esc, ps)}
    sel = v.get("seleccion") if v.get("seleccion") is not None else ficha_ids(v["ficha"] or {})
    its = g4.ev.items(pool)
    pk = esc.get("pico") or {}
    return {"bloqueantes": g4.bloqueantes(topic, esc, ps, largo="abierto", ficha=v["ficha"]), "metricas": m,
            "parrafos_ids": pid, "minutos": round(m["palabras"] / PALABRAS_POR_SEG / 60, 1),
            "repeticion": round(sum(rep.values()) / len(rep), 1) if rep else 0.0,
            "preguntas": preguntas(ps), "frases_analista": frases_analista(ps),
            "embudo": {"pool": len(topic["_pool_ids"]), "seleccion": len(set(sel) & topic["_pool_ids"]),
                       "escaleta": len(esc_ids(esc)),
                       "guion": len({i for p in pid for i in p.get("ids_usados") or []})},
            "beats": len(esc["beats"]),
            "humano": (esc.get("humano") or {}).get("nombre"),
            "pico": {"beat": pk.get("beat"), "id": pk.get("id"), "texto": g4.ev.text_of(its[pk["id"]])
                     if pk.get("id") in its else None, "por_que": pk.get("por_que")},
            "avisos": esc.get("_avisos") or [],
            "escenas_usadas": sorted({b["escena_idx"] for b in esc["beats"] if b.get("escena_idx")}),
            "preguntas_por_cap": {n: sum(p["texto"].count("?") for p in ps if p["cap"] == n) for n in range(1, 8)},
            "citas_por_cap": {n: sum(len(quotes_in(p["texto"])) for p in ps if p["cap"] == n) for n in range(1, 8)},
            "analista_por_cap": {n: sum(frases_analista([p]).get(k, 0) for p in ps if p["cap"] == n
                                        for k in frases_analista([p])) for n in range(1, 8)}}


def section(nom: str) -> tuple[str, list[dict]]:
    import fase1_5 as f15
    from f11_compara import cap_cell, spans
    tid, titulo = TEMAS[nom]
    topic = dict(f15._load_topic_by_id(tid))
    pool = topic["evidence_pool"]
    topic["_pool_ids"] = {i for i, it in __import__("script_engine.evidence", fromlist=["x"]).items(pool).items()
                          if it["_kind"] in ("datos", "cronologia", "citas", "personajes", "lugares")}
    vs = versiones(nom, pool)
    meds = [medir(topic, v) for v in vs]
    emb = ("<div class='scroll'><table class='sum'><tr><th>versión</th><th>ítems del pool</th><th>→ selección</th>"
           "<th>→ escaleta</th><th>→ guion</th><th>beats</th><th>humano</th><th>pico</th></tr>"
           + "".join(f"<tr><th>{html.escape(v['nombre'])}</th><td class='n'>{m['embudo']['pool']}</td>"
                     f"<td class='n'>{m['embudo']['seleccion']} ({v['sel_nombre']})</td>"
                     f"<td class='n'>{m['embudo']['escaleta']}</td><td class='n'>{m['embudo']['guion']}</td>"
                     f"<td class='n'>{m['beats']}</td><td>{html.escape(m['humano'] or '—')}</td>"
                     f"<td>beat {m['pico']['beat']} · {m['pico']['id']}: {html.escape(str(m['pico']['texto'])[:140])}</td></tr>"
                     for v, m in zip(vs, meds)) + "</table></div>")
    tabla = ("<div class='scroll'><table class='sum'><tr><th>versión</th><th>palabras</th><th>min</th>"
             "<th>palabras por cap (1–7)</th><th>bloq.</th><th>duras v3</th><th>citas</th><th>preguntas</th>"
             "<th>frases de analista</th><th>repetición</th><th>cierre</th><th>US$</th></tr>")
    for v, med in zip(vs, meds):
        m = med["metricas"]
        caps = " ".join(f"{(m['palabras_por_cap'].get(n) or [0, 0])[0]}" for n in range(1, 8))
        usd = f"{v['usd']:.3f}" if v.get("usd") is not None else "—"
        tabla += (f"<tr><th>{html.escape(v['nombre'])}</th><td class='n'>{m['palabras']}</td>"
                  f"<td class='n'><b>{med['minutos']}</b></td><td class='caps'>{caps}</td>"
                  f"<td class='n'>{len(med['bloqueantes'])}</td><td class='n'>{len(m['duras_v3'])}</td>"
                  f"<td class='n'>{m['citas']}</td><td class='n'>{med['preguntas']}</td>"
                  f"<td class='n'>{sum(med['frases_analista'].values())}</td><td class='n'>{med['repeticion']} %</td>"
                  f"<td>{m['cierre']}</td><td class='n'>{usd}</td></tr>")
    tabla += "</table></div>"
    blq = "".join(f"<details><summary>{html.escape(v['nombre'])} · {len(med['bloqueantes'])} bloqueante(s)</summary>"
                  "<ul class='blq'>" + "".join(f"<li>({x['codigo']}) cap {x['cap']} beat {x['beat']}: "
                                               f"{html.escape(x['motivo'])}</li>" for x in med["bloqueantes"])
                  + "</ul></details>" for v, med in zip(vs, meds) if med["bloqueantes"])
    caps = [f"<div class='grid hdr'><div>{html.escape(vs[0]['nombre'])}</div>"
            f"<div>{html.escape(vs[-1]['nombre'])}</div></div>"]
    for n in range(1, 8):
        cells = []
        for v, med in zip(vs, meds):
            ps, m = med["parrafos_ids"], med["metricas"]
            w = (m["palabras_por_cap"].get(n) or [0, 0])[0]
            nb = len([x for x in med["bloqueantes"] if x.get("cap") == n])
            cells.append(f"<div class='col'><p class='ids'>{w} palabras · {round(w / 2.05)} s · {nb} bloqueante(s) · "
                         f"{med['preguntas_por_cap'][n]} pregunta(s) · {med['citas_por_cap'][n]} cita(s) · "
                         f"{med['analista_por_cap'][n]} frase(s) de analista</p>"
                         f"{cap_cell(n, ps, spans(ps, pool, med['bloqueantes']), med['bloqueantes'], m)}</div>")
        caps.append(f"<h3>{titulo} · Cap {n}</h3><div class='grid'>{''.join(cells)}</div>")
    body = (f"<h2>{titulo}</h2><h3>Embudo, humano y pico</h3>{emb}<h3>Resumen</h3>{tabla}"
            f"{'<h3>Bloqueantes</h3>' + blq if blq else '<p>Sin bloqueantes en ninguna versión.</p>'}{''.join(caps)}")
    res = [{"tema": nom, "nombre": v["nombre"], "clave": v["clave"], "usd": v.get("usd"), "usd_nota": v.get("usd_nota"),
            "error": v.get("error"),
            **{k: med[k] for k in ("bloqueantes", "minutos", "repeticion", "preguntas", "frases_analista", "embudo",
                                   "beats", "humano", "pico", "avisos", "escenas_usadas", "citas_por_cap",
                                   "preguntas_por_cap")},
            "metricas": {k: med["metricas"][k] for k in ("palabras", "palabras_por_cap", "citas", "cierre",
                                                          "humano_caps", "duras_v3")}} for v, med in zip(vs, meds)]
    return body, res


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    from f11_compara import CSS
    from f11b_compara import CSS_EXTRA
    sy, ry = section("ycua")
    so, ro = section("orleans")
    costos = _j(LAB / "costos_f15.json") or {}
    head = ("<h1>Guion v5 + ficha con historia y escenas (F15)</h1>"
            "<p class='meta'>F15: ficha v2 (Sol high) → escaleta nueva (Pro, lee historia y escenas primero) → guion v5 "
            "(prompt del analista, literal; Sol high, largo abierto, una llamada, sin notas, sin reparación ni editor). "
            "Minutos a 2.05 palabras/s. Bloqueantes re-medidos con el código de hoy, cada versión con su ficha. Costo de "
            f"la tanda F15: US$ {costos.get('usd_total', 0):.3f} (tope 2.50).</p>"
            "<p class='meta legend'><mark class='blq'>bloqueante</mark><mark class='fecha'>fecha repetida</mark>"
            "<mark class='juicio'>juicio de la lista</mark><mark class='eco'>eco después de cita</mark>"
            "<mark class='trailer'>voz de tráiler</mark> · las marcas que no son bloqueantes no rechazan nada. "
            "«N/objetivo palabras» es solo referencia (largo abierto); «duras v3 del cap K» = K duras.</p>")
    css = ("@media (max-width:760px){.grid .col:first-child::before{content:'antes'}"
           ".grid .col:last-child::before{content:'F15'}}")
    doc = (f"<!doctype html><html lang='es'><head><meta charset='utf-8'><meta name='viewport' "
           f"content='width=device-width,initial-scale=1'><title>Guion v5 y ficha v2</title><style>{CSS}{CSS_EXTRA}{css}"
           f"</style></head><body>{head}{sy}{so}</body></html>")
    (LAB / "compara_f15.html").write_text(doc, encoding="utf-8")
    (LAB / "resumen_f15.json").write_text(json.dumps(ry + ro, ensure_ascii=False, indent=1), encoding="utf-8")
    for r in ry + ro:
        m = r["metricas"]
        print(f"{r['tema']:7} {r['clave']} {m['palabras']} pal · {r['minutos']} min · embudo {r['embudo']} · bloq "
              f"{len(r['bloqueantes'])} · duras {len(m['duras_v3'])} · citas {m['citas']} · ? {r['preguntas']} · "
              f"analista {sum(r['frases_analista'].values())} · humano {r['humano']} · pico {r['pico']['beat']}/"
              f"{r['pico']['id']} · escenas {r['escenas_usadas']} · US$ {r['usd']}")
    print("compara_f15.html", len(doc))


if __name__ == "__main__":
    main()
