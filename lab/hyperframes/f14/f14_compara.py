"""F14 §2 — compara_f14.html (Orleans): F13 abierto (digest + escaleta F7c-3) | F14 (ficha + escaleta nueva), por cap.

Arriba, el embudo en números para las dos versiones:
    pool        ítems del research (datos, cronología, citas, personas, lugares)
    selección   F13: ids distintos que nombra el digest · F14: ids distintos que cita la ficha (sin descartados)
    escaleta    ids distintos de la escaleta (beats + ids de los caps + a_pantalla)
    guion       ids distintos que usa la narración (`guion_v4.with_ids`: lo que suena ∩ lo del beat)
Tabla resumen (palabras, minutos a 2.05 palabras/s, bloqueantes, duras v3, citas, ids, repetición, preguntas, costo) y,
por cap, las dos columnas con palabras, segundos, bloqueantes, ids distintos, citas y las frases marcadas en color.
Todo re-medido con el código de hoy (largo abierto en los dos). No llama a ninguna API. Deja `resumen_f14.json`.
Uso: python -I lab/hyperframes/f14/f14_compara.py
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
for d in (LAB.parent / "f11", LAB.parent / "f11b", LAB.parent / "f11c", LAB.parent / "f13", LAB):
    sys.path.insert(1, str(d))
TID = "ba6c3cac-f7r3"


def _j(p: Path):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def esc_ids(esc: dict) -> set[str]:
    b = {i for x in esc["beats"] for i in [x["dato_central"]] + list(x.get("datos_apoyo") or [])}
    c = {i for x in esc.get("caps") or [] for k in ("evidence_ids", "pantalla_ids") for i in x.get(k) or []}
    return b | c | {x["id"] for x in esc.get("a_pantalla") or []}


def ficha_ids(ficha: dict) -> set[str]:
    out = set()
    for s, sec in ficha.items():
        if s in ("descartados", "chequeo") or not isinstance(sec, list):
            continue
        for x in sec:
            if not isinstance(x, dict):
                continue
            out |= set(x.get("ids") or [])
            for v in (x.get("versiones") or []) + (x.get("otras_versiones") or []):
                out |= set(v.get("ids") or [])
    return out


def versiones(topic: dict) -> list[dict]:
    from script_engine.m01a_skeleton import STEPS_DIR
    d = STEPS_DIR / TID
    pool = topic["evidence_pool"]
    f13 = _j(LAB.parent / "f13" / "guion_orleans_f13_abierto.json")
    esc13 = _j(d / "01a_escaleta_f7c3.json") or _j(d / "01a_escaleta.json")
    dig = set(re.findall(r"\b[DTQPL]\d{1,3}\b", (pool.get("digest") or {}).get("texto") or ""))
    out = [{"nombre": "F13 abierto · digest + escaleta F7c-3", "clave": "f13", "parrafos": f13["parrafos"], "esc": esc13,
            "seleccion": dig, "seleccion_nombre": "digest", "usd": f13["costo"]["usd"],
            "usd_nota": "solo el guion (el digest y la escaleta F7c-3 son de antes)",
            "tokens": f13["costo"]["llamadas"][0]}]
    g = _j(LAB / "guion_orleans_f14.json")
    esc14 = _j(d / "01a_escaleta_f14.json")
    ficha = _j(d / "ficha_caso.json")
    costos = _j(LAB / "costos_f14.json") or {}
    if g and esc14 and ficha:
        out.append({"nombre": "F14 · ficha + escaleta nueva", "clave": "f14", "parrafos": g.get("parrafos") or [],
                    "esc": esc14, "seleccion": ficha_ids(ficha), "seleccion_nombre": "ficha",
                    "usd": costos.get("usd_total"), "usd_nota": "ficha + escaleta + guion", "error": g.get("error"),
                    "etapas": costos.get("etapas")})
    return out


def medir(topic: dict, v: dict) -> dict:
    from f11c_compara import frases_analista, preguntas
    from f13_corridas import PALABRAS_POR_SEG, repeticion_interna
    from script_engine import guion_v4 as g4
    from script_engine import m01b_guionista as mg
    from script_engine.guion_v3_reglas import quotes_in
    esc, ps = v["esc"], v["parrafos"]
    pool = topic["evidence_pool"]
    pid = g4.with_ids(ps, pool, esc)
    m = g4.metricas(topic, esc, ps)
    rep = {c["chapter_number"]: repeticion_interna(c["narration"]) for c in mg.caps_text(esc, ps)}
    guion_ids = {i for p in pid for i in p.get("ids_usados") or []}
    eids = esc_ids(esc)
    return {"bloqueantes": g4.bloqueantes(topic, esc, ps, largo="abierto"), "metricas": m, "parrafos_ids": pid,
            "minutos": round(m["palabras"] / PALABRAS_POR_SEG / 60, 1), "repeticion_por_cap": rep,
            "repeticion": round(sum(rep.values()) / len(rep), 1) if rep else 0.0,
            "preguntas": preguntas(ps), "frases_analista": frases_analista(ps),
            "embudo": {"pool": len(topic["_pool_ids"]), "seleccion": len(v["seleccion"] & topic["_pool_ids"]),
                       "escaleta": len(eids), "guion": len(guion_ids)},
            "escaleta_fuera_de_seleccion": sorted(eids - v["seleccion"]),
            "beats": len(esc["beats"]), "apoyos_por_beat": round(sum(len(b.get("datos_apoyo") or []) for b in esc["beats"])
                                                                 / max(1, len(esc["beats"])), 2),
            "ids_por_cap": {n: len({i for p in pid if p["cap"] == n for i in p.get("ids_usados") or []})
                            for n in range(1, 8)},
            "citas_por_cap": {n: sum(len(quotes_in(p["texto"])) for p in ps if p["cap"] == n) for n in range(1, 8)},
            "humano": (esc.get("humano") or {}).get("nombre")}


def fila(v: dict, med: dict) -> str:
    m = med["metricas"]
    caps = " ".join(f"{(m['palabras_por_cap'].get(n) or [0, 0])[0]}" for n in range(1, 8))
    e = med["embudo"]
    usd = f"{v['usd']:.3f}" if v.get("usd") is not None else "—"
    return (f"<tr><th>{html.escape(v['nombre'])}</th><td class='n'>{m['palabras']}</td>"
            f"<td class='n'><b>{med['minutos']}</b></td><td class='caps'>{caps}</td>"
            f"<td class='n'>{len(med['bloqueantes'])}</td><td class='n'>{len(m['duras_v3'])}</td>"
            f"<td class='n'>{m['citas']}</td><td class='n'>{e['guion']}</td><td class='n'>{med['repeticion']} %</td>"
            f"<td class='n'>{med['preguntas']}</td><td>{html.escape(med['humano'] or '—')}</td>"
            f"<td>{m['cierre']}</td><td class='n'>{usd}</td></tr>")


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    import fase1_5 as f15
    from f11_compara import CSS, cap_cell, spans
    from f11b_compara import CSS_EXTRA
    from script_engine import evidence as ev
    topic = dict(f15._load_topic_by_id(TID))
    pool = topic["evidence_pool"]
    topic["_pool_ids"] = {i for i, it in ev.items(pool).items()
                          if it["_kind"] in ("datos", "cronologia", "citas", "personajes", "lugares")}
    vs = versiones(topic)
    meds = [medir(topic, v) for v in vs]
    emb = ("<div class='scroll'><table class='sum'><tr><th>versión</th><th>ítems del pool</th><th>→ en la selección</th>"
           "<th>→ en la escaleta</th><th>→ en el guion</th><th>beats</th><th>apoyos por beat</th></tr>"
           + "".join(f"<tr><th>{html.escape(v['nombre'])}</th><td class='n'>{m['embudo']['pool']}</td>"
                     f"<td class='n'>{m['embudo']['seleccion']} ({v['seleccion_nombre']})</td>"
                     f"<td class='n'>{m['embudo']['escaleta']}</td><td class='n'>{m['embudo']['guion']}</td>"
                     f"<td class='n'>{m['beats']}</td><td class='n'>{m['apoyos_por_beat']}</td></tr>"
                     for v, m in zip(vs, meds)) + "</table></div>")
    tabla = ("<div class='scroll'><table class='sum'><tr><th>versión</th><th>palabras</th><th>min (2.05 p/s)</th>"
             "<th>palabras por cap (1–7)</th><th>bloq.</th><th>duras v3</th><th>citas</th><th>ids en el guion</th>"
             "<th>repetición interna</th><th>preguntas</th><th>humano</th><th>cierre</th><th>US$</th></tr>"
             + "".join(fila(v, m) for v, m in zip(vs, meds)) + "</table></div>")
    blq = []
    for v, med in zip(vs, meds):
        if med["bloqueantes"]:
            blq.append(f"<details><summary>{html.escape(v['nombre'])} · {len(med['bloqueantes'])} bloqueante(s)"
                       "</summary><ul class='blq'>" + "".join(
                           f"<li>({x['codigo']}) cap {x['cap']} beat {x['beat']}: {html.escape(x['motivo'])}</li>"
                           for x in med["bloqueantes"]) + "</ul></details>")
    caps = ["<div class='grid hdr'><div>F13 (digest + escaleta F7c-3)</div><div>F14 (ficha + escaleta nueva)</div></div>"]
    for n in range(1, 8):
        cells = []
        for v, med in zip(vs, meds):
            ps = med["parrafos_ids"]
            m = med["metricas"]
            w = (m["palabras_por_cap"].get(n) or [0, 0])[0]
            nb = len([x for x in med["bloqueantes"] if x.get("cap") == n])
            cells.append(f"<div class='col'><p class='ids'>{w} palabras · {round(w / 2.05)} s · {nb} bloqueante(s) · "
                         f"{med['ids_por_cap'][n]} ids distintos · {med['citas_por_cap'][n]} cita(s)</p>"
                         f"{cap_cell(n, ps, spans(ps, pool, med['bloqueantes']), med['bloqueantes'], m)}"
                         + "".join(f"<p class='ids'>b{p['beat']} ids: {', '.join(p.get('ids_usados') or []) or '—'}</p>"
                                   for p in ps if p["cap"] == n) + "</div>")
        caps.append(f"<h3>Cap {n}</h3><div class='grid'>{''.join(cells)}</div>")
    head = ("<h1>Orleans · la ficha reemplaza al digest (F14)</h1>"
            "<p class='meta'>Las dos versiones: Sol high, largo abierto (f13-1), una llamada, sin notas, sin reparación ni "
            "editor. F13 = digest de F7c → escaleta F7c-3 → guion. F14 = ficha con criterios (f14-1) → escaleta nueva "
            "(Pro, lee la ficha, apoyos 0–6) → guion con el texto de la ficha. Minutos a 2.05 palabras/s. Bloqueantes "
            "re-medidos con el código de hoy. Costo de la tanda F14 (ficha + escaleta + guion): US$ "
            f"{(vs[-1].get('usd') or 0):.3f} (tope 1.50).</p>"
            "<p class='meta legend'><mark class='blq'>bloqueante</mark><mark class='fecha'>fecha repetida</mark>"
            "<mark class='juicio'>juicio de la lista</mark><mark class='eco'>eco después de cita</mark>"
            "<mark class='trailer'>voz de tráiler</mark> · las marcas que no son bloqueantes no rechazan nada. "
            "«N/objetivo palabras» en verde o rojo es solo referencia (largo abierto); «duras v3 del cap K» = K duras.</p>")
    css = ("@media (max-width:760px){.grid .col:first-child::before{content:'F13'}"
           ".grid .col:last-child::before{content:'F14'}}")
    doc = (f"<!doctype html><html lang='es'><head><meta charset='utf-8'><meta name='viewport' "
           f"content='width=device-width,initial-scale=1'><title>Ficha en el camino</title><style>{CSS}{CSS_EXTRA}{css}"
           f"</style></head><body>{head}<h2>Embudo</h2>{emb}<h2>Resumen</h2>{tabla}<h2>Bloqueantes</h2>"
           f"{''.join(blq) or '<p>Ninguna versión tiene.</p>'}<h2>Texto por cap</h2>{''.join(caps)}</body></html>")
    (LAB / "compara_f14.html").write_text(doc, encoding="utf-8")
    res = [{"nombre": v["nombre"], "clave": v["clave"], "usd": v.get("usd"), "usd_nota": v.get("usd_nota"),
            "etapas": v.get("etapas"), "error": v.get("error"),
            **{k: med[k] for k in ("bloqueantes", "minutos", "repeticion", "repeticion_por_cap", "preguntas",
                                   "frases_analista", "embudo", "escaleta_fuera_de_seleccion", "beats",
                                   "apoyos_por_beat", "ids_por_cap", "citas_por_cap", "humano")},
            "metricas": {k: med["metricas"][k] for k in ("palabras", "palabras_por_cap", "citas", "cierre",
                                                          "humano_caps", "duras_v3")}} for v, med in zip(vs, meds)]
    (LAB / "resumen_f14.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    for r in res:
        m = r["metricas"]
        print(f"{r['clave']} {m['palabras']} pal · {r['minutos']} min · embudo {r['embudo']} · bloq "
              f"{len(r['bloqueantes'])} · duras {len(m['duras_v3'])} · citas {m['citas']} · beats {r['beats']} · "
              f"apoyos/beat {r['apoyos_por_beat']} · fuera de la selección {r['escaleta_fuera_de_seleccion']} · US$ {r['usd']}")
    print("compara_f14.html", len(doc))


if __name__ == "__main__":
    main()
