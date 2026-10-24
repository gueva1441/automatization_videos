"""F19 §3 — compara_f19.html: el embudo F18 | F19 por idioma de fuente (documentos propuestos, bajados, que nombran el
evento y que aportan ítems; ítems del pool por idioma; → ficha → columna → escaleta → guion), la compuerta, la columna,
la escaleta (con las métricas de la columna y el antagonista) y el guion por cap con bloqueantes, personas con nombre,
escenas usadas y frases marcadas. F18 sale de los respaldos (`_steps/<topic>/_f18/`, `00_pool_v3_f18.json`,
`lab/hyperframes/f18/`). No llama a ninguna API. Deja `resumen_f19.json`.
Uso: python -I lab/hyperframes/f19/f19_compara.py
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
for d in ("f11", "f11b", "f11c", "f13", "f14", "f15", "f15b"):
    sys.path.insert(1, str(LAB.parent / d))
TID = "f18-kyshtym-mayak"
_ID = re.compile(r"\b[PDTQ]\d{1,4}\b")


def _j(p: Path):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


_CYR = re.compile(r"[\u0400-\u04FF]")


def doc_idioma(doc: dict, src: Path) -> str:
    """Idioma de un documento por su texto (el `idioma` del manifiesto no es fiable: marca «en» o «?» a los rusos)."""
    t = str(doc.get("titulo") or "")
    if doc.get("ok") and doc.get("txt") and (src / doc["txt"]).exists():
        t += (src / doc["txt"]).read_text(encoding="utf-8")[:3000]
    letras = [c for c in t if c.isalpha()]
    if not letras:
        return str(doc.get("idioma") or "?")
    if sum(1 for c in letras if _CYR.match(c)) / len(letras) > 0.3:
        return "ru"
    return "es" if str(doc.get("idioma") or "").startswith("es") else "en"


def embudo_idiomas(man: dict, pool: dict, src: Path) -> dict:
    """Por idioma: documentos propuestos, bajados, que nombran el evento, que aportan ítems, e ítems del pool."""
    docs = man.get("documentos") or []
    lang = {d["id"]: doc_idioma(d, src) for d in docs}
    aporta: dict[str, int] = {}
    for k in ("datos", "cronologia", "citas", "personajes", "lugares"):
        for it in pool.get(k) or []:
            for x in set(it.get("docs") or []):
                aporta[x] = aporta.get(x, 0) + 1
    out: dict[str, dict] = {}
    for d in docs:
        o = out.setdefault(lang[d["id"]], {"propuestos": 0, "bajados": 0, "nombran_evento": 0, "aportan": 0,
                                           "items": 0})
        o["propuestos"] += 1
        o["bajados"] += int(bool(d.get("ok")))
        o["nombran_evento"] += int(bool(d.get("ok") and d.get("nombra_evento")))
        o["aportan"] += int(aporta.get(d["id"], 0) > 0)
        o["items"] += aporta.get(d["id"], 0)
    return out


def personas_en(texto: str, ficha: dict) -> list[str]:
    """Personas de la ficha nombradas en un texto: nombre completo o apellido (≥ 4 letras), sin acentos."""
    from script_engine import evidence as ev
    from script_engine.m01a_columna import personas_ficha
    t = " " + " ".join(re.findall(r"[a-z0-9ñ]+", ev.norm(texto))) + " "
    out = []
    for p in personas_ficha(ficha):
        for n in p["nombres"]:
            toks = re.findall(r"[a-z0-9ñ]+", ev.norm(n or ""))
            if toks and (f" {' '.join(toks)} " in t or (len(toks) >= 2 and len(toks[-1]) >= 4 and f" {toks[-1]} " in t)):
                if p["nombre"] not in out:
                    out.append(p["nombre"])
                break
    return out


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    import fase1_5 as f15
    from f11_compara import CSS, cap_cell, spans
    from f11b_compara import CSS_EXTRA
    from f15_compara import medir
    from f15b_compara import parrafos_stats
    from researcher_steps import ficha_caso as fc
    from researcher_steps import pool_gate as pg
    from script_engine import evidence as ev
    from script_engine import m01a_columna as mc
    from script_engine.m01a_skeleton import STEPS_DIR
    d = STEPS_DIR / TID
    topic = dict(f15._load_topic_by_id(TID))
    pool = json.loads((d / "00_pool_v3.json").read_text(encoding="utf-8"))   # F19: el pool nuevo (rojo: no entró al topic)
    its = ev.items(pool)
    topic["_pool_ids"] = {i for i, it in its.items() if it["_kind"] in ("datos", "cronologia", "citas", "personajes",
                                                                         "lugares")}
    ficha = fc.load(TID)
    col = mc.load(TID)
    esc = _j(d / "01a_escaleta_f19.json")
    g = _j(LAB / "guion_kyshtym_f19.json") or {}
    man = _j(d / "fuentes" / "manifest.json") or {}
    costos = _j(LAB / "costos_f19.json") or {"etapas": [], "usd_total": 0}
    gate = pg.evaluate(json.loads((d / "00_pool_v3.json").read_text(encoding="utf-8")))
    docs = man.get("documentos") or []
    ok_docs = [x for x in docs if x.get("ok")]
    idiomas: dict[str, int] = {}
    for x in ok_docs:
        idiomas[str(x.get("idioma") or "?")] = idiomas.get(str(x.get("idioma") or "?"), 0) + 1
    ficha_ids = {i for sec in ("personas", "cronologia", "hechos", "cifras", "citas", "escenas")
                 for x in (ficha or {}).get(sec) or [] for i in x.get("ids") or []} & topic["_pool_ids"]
    col_ids = set()
    if col:
        for x in [col.get("humano") or {}, col.get("pico") or {}, *(col.get("caps") or [])]:
            col_ids |= set(x.get("ids") or [])
    esc_ids = set()
    for b in (esc or {}).get("beats") or []:
        esc_ids |= {b.get("dato_central"), *(b.get("datos_apoyo") or [])}
    esc_ids.discard(None)
    v = {"esc": esc, "parrafos": g.get("parrafos") or [], "ficha": ficha, "nombre": "F19"}
    md = medir(topic, v) if esc and v["parrafos"] else None
    st = parrafos_stats(v["parrafos"]) if v["parrafos"] else None
    guion_ids = set(i for p in (md or {}).get("parrafos_ids") or [] for i in p.get("ids_usados") or [])
    cit_ver = sum(1 for it in its.values() if it["_kind"] == "citas" and (it.get("verificacion") or {}).get("estado")
                  == "verificada")
    embudo = [("documentos (bajados / propuestos)", f"{len(ok_docs)} / {len(docs)}"),
              ("ítems del pool", len(topic["_pool_ids"])), ("→ ficha (ids)", len(ficha_ids)),
              ("→ columna (ids)", len(col_ids)), ("→ escaleta (ids)", len(esc_ids)), ("→ guion (ids)", len(guion_ids))]
    pool18 = _j(d / "00_pool_v3_f18.json") or {}
    man18 = _j(d / "_f18" / "fuentes" / "manifest.json") or {}
    ficha18 = _j(d / "_f18" / "ficha_caso.json") or {}
    col18 = _j(d / "_f18" / "01a_columna.json") or {}
    its18 = ev.items(pool18)
    pid18 = {i for i, it in its18.items() if it["_kind"] in ("datos", "cronologia", "citas", "personajes", "lugares")}
    fid18 = {i for sec in ("personas", "cronologia", "hechos", "cifras", "citas", "escenas")
             for x in ficha18.get(sec) or [] for i in x.get("ids") or []} & pid18
    cid18 = set()
    for x in [col18.get("humano") or {}, col18.get("pico") or {}, *(col18.get("caps") or [])]:
        cid18 |= set(x.get("ids") or [])
    l18 = embudo_idiomas(man18, pool18, d / "_f18" / "fuentes")
    l19 = embudo_idiomas(man, json.loads((d / "00_pool_v3.json").read_text(encoding="utf-8")), d / "fuentes")
    filas = [("documentos propuestos (R1)", len(man18.get("documentos") or []), len(docs)),
             ("documentos bajados", sum(1 for x in man18.get("documentos") or [] if x.get("ok")), len(ok_docs)),
             ("documentos que nombran el evento", sum(1 for x in man18.get("documentos") or []
                                                     if x.get("ok") and x.get("nombra_evento")),
              sum(1 for x in ok_docs if x.get("nombra_evento"))),
             ("ítems del pool", len(pid18), len(topic["_pool_ids"])),
             ("citas del pool (verificadas)", f"{sum(1 for it in its18.values() if it['_kind'] == 'citas')} "
              f"({sum(1 for it in its18.values() if it['_kind'] == 'citas' and (it.get('verificacion') or {}).get('estado') == 'verificada')})",
              f"{sum(1 for it in its.values() if it['_kind'] == 'citas')} ({cit_ver})"),
             ("personajes del pool", sum(1 for it in its18.values() if it["_kind"] == "personajes"),
              sum(1 for it in its.values() if it["_kind"] == "personajes")),
             ("→ ficha (ids)", len(fid18), len(ficha_ids)), ("→ ficha: citas", len(ficha18.get("citas") or []),
                                                            len((ficha or {}).get("citas") or [])),
             ("→ columna (ids)", len(cid18), len(col_ids)), ("→ escaleta (ids)", 0, len(esc_ids)),
             ("→ guion (ids)", 0, len(guion_ids))]
    for lg in sorted(set(l18) | set(l19)):
        a18, a19 = l18.get(lg) or {}, l19.get(lg) or {}
        filas.append((f"[{lg}] propuestos · bajados · nombran el evento · aportan · ítems",
                      " · ".join(str(a18.get(k, 0)) for k in ("propuestos", "bajados", "nombran_evento", "aportan",
                                                              "items")),
                      " · ".join(str(a19.get(k, 0)) for k in ("propuestos", "bajados", "nombran_evento", "aportan",
                                                              "items"))))
    embudo = [(k, y) for k, _, y in filas]
    E = ("<div class='scroll'><table class='sum emb' style='min-width:0'><tr><th></th><th>F18</th><th>F19</th></tr>"
         + "".join(f"<tr><th>{html.escape(k)}</th><td class='n'>{x}</td><td class='n'><b>{y}</b></td></tr>"
                   for k, x, y in filas) + "</table></div>")
    G = (f"<p><b>Compuerta: {html.escape(gate['color'].upper())}</b> · "
         + " · ".join(f"{k} {x}" for k, x in gate["metricas"].items())
         + (f"<br><small>{html.escape('; '.join(gate['motivos']))}</small>" if gate.get("motivos") else "") + "</p>")
    C = "<p class='bad'>sin columna</p>"
    if col:
        h, pk = col["humano"], col["pico"]
        C = (f"<div class='col'><p><b>HUMANO:</b> {html.escape(h.get('nombre') or '')}: {html.escape(h.get('por_que') or '')}</p>"
             f"<p><b>PICO:</b> cap {pk.get('cap')}, {html.escape(pk.get('que') or '')}</p>"
             + "".join(f"<p><b>CAP {c['cap']} · QUÉ PASA:</b> {html.escape(c.get('que_pasa') or '')} <b>TERMINA:</b> "
                       f"{html.escape(c.get('termina') or '')}<br><small>personas: "
                       f"{html.escape(', '.join(c.get('personas') or []) or '—')}</small></p>" for c in col["caps"])
             + "<p><b>AFUERA:</b></p><ul>" + "".join(f"<li>{html.escape(a.get('que') or '')} <small>("
                                                    f"{html.escape(a.get('por_que') or '')})</small></li>"
                                                    for a in col.get("afuera") or []) + "</ul>"
             + f"<p class='meta'>personas con nombre en toda la columna: {col['_metricas']['personas_con_nombre']} · "
               f"intentos: {len(col.get('_intentos') or [])}</p></div>")
    res: dict = {}
    intentos = [(e.get("pase"), line) for e in costos["etapas"] if e["etapa"] == "escaleta"
                for line in (e.get("log") or []) + ([f"  → {e['error']}"] if e.get("error") else [])]
    S = ("<p class='bad'><b>Sin escaleta: PARADA.</b></p><ul class='blq'>"
         + "".join(f"<li>pase {p or 1}: {html.escape(x.strip())}</li>" for p, x in intentos) + "</ul>")
    res["escaleta_intentos"] = [{"pase": p or 1, "linea": x.strip()} for p, x in intentos]
    if esc:
        m, mcol = esc["_metricas"], esc["_metricas"].get("columna") or {}
        caps = [sum(1 for b in esc["beats"] if b["cap"] == n) for n in range(1, 8)]
        S = ("<div class='scroll'><table class='sum' style='min-width:0'>"
             f"<tr><th>beats (por cap)</th><td>{len(esc['beats'])} ({' · '.join(map(str, caps))})</td></tr>"
             f"<tr><th>intentos</th><td>{len(esc.get('_intentos') or [])}</td></tr>"
             f"<tr><th>humano</th><td>{html.escape(esc['humano'].get('nombre') or '')} · = columna: "
             f"{mcol.get('humano_es_el_de_la_columna')}</td></tr>"
             f"<tr><th>antagonista</th><td>{html.escape(str(esc.get('antagonista') or {}))}</td></tr>"
             f"<tr><th>pico</th><td>beat {esc['pico'].get('beat')} · {esc['pico'].get('id')} · el de la ficha: "
             f"{m['pico_es_el_de_la_ficha']}</td></tr>"
             f"<tr><th>personas fuera de la columna</th><td>{html.escape(json.dumps(mcol.get('personas_fuera_de_la_columna'), ensure_ascii=False))}</td></tr>"
             f"<tr><th>cierres = «termina»</th><td>{mcol.get('cierres_iguales')}/7</td></tr>"
             f"<tr><th>curva</th><td>{' '.join(map(str, m['curva_intensidad']))} · flash-forward {m['flash_forward_beat1']}</td></tr>"
             f"<tr><th>escenas (gancho / pico)</th><td>{', '.join(f'E{x}' for x in m['escenas_usadas']) or '—'} "
             f"({m['escena_gancho'] or '—'} / {m['escena_pico'] or '—'})</td></tr>"
             f"<tr><th>giros con beat</th><td>{m['giros_con_beat']}/{m['giros_total']}</td></tr></table></div>"
             "<details><summary>Cierres: escaleta vs «termina» de la columna</summary><ul>"
             + "".join(f"<li>cap {k}: «{html.escape(x['cierre'])}» / «{html.escape(x['termina'])}» "
                       f"(parecido {x['parecido']})</li>" for k, x in (mcol.get("cierres") or {}).items())
             + "</ul></details>")
    T = "<p class='bad'>sin guion" + (f": {html.escape(g.get('error') or '')}" if g.get("error") else "") + "</p>"
    res.update({"embudo": {k: {"f18": x, "f19": y} for k, x, y in filas}, "idiomas": {"f18": l18, "f19": l19},
                "compuerta": gate, "costos": costos})
    if md:
        mm = md["metricas"]
        sps = spans(md["parrafos_ids"], pool, md["bloqueantes"])
        por_cap = {}
        T = ("<div class='scroll'><table class='sum' style='min-width:0'>"
             f"<tr><th>palabras · minutos</th><td>{mm['palabras']} · <b>{md['minutos']} min</b></td></tr>"
             f"<tr><th>párrafos · frases/párrafo · de 1 frase</th><td>{st['parrafos']} · {st['frases_por_parrafo']} · "
             f"{st['de_una_frase']}</td></tr>"
             f"<tr><th>bloqueantes</th><td>{len(md['bloqueantes'])}</td></tr>"
             f"<tr><th>citas · preguntas · frases de analista</th><td>{mm['citas']} · {md['preguntas']} · "
             f"{sum(md['frases_analista'].values())}</td></tr>"
             f"<tr><th>humano (caps)</th><td>{html.escape(md['humano'] or '—')} {mm['humano_caps']}</td></tr>"
             f"<tr><th>escenas usadas</th><td>{', '.join(f'E{x}' for x in md['escenas_usadas']) or '—'}</td></tr>"
             "</table></div>")
        todas = []
        for n in range(1, 8):
            texto = " ".join(p["texto"] for p in md["parrafos_ids"] if p["cap"] == n)
            pers = personas_en(texto, ficha)
            todas += [x for x in pers if x not in todas]
            w = (mm["palabras_por_cap"].get(n) or [0, 0])[0]
            pc = st["por_cap"][n]
            nb = len([x for x in md["bloqueantes"] if x.get("cap") == n])
            esc_cap = sorted({b.get("escena_idx") for b in esc["beats"] if b["cap"] == n and b.get("escena_idx")})
            por_cap[n] = {"palabras": w, "personas": pers, "bloqueantes": nb, "escenas": esc_cap}
            T += (f"<h3>Cap {n}</h3><div class='col'><p class='ids'>{w} palabras · {round(w / 2.05)} s · "
                  f"{pc['parrafos']} párrafos · {nb} bloqueante(s) · escenas {', '.join(f'E{x}' for x in esc_cap) or '—'}"
                  f" · personas con nombre ({len(pers)}): {html.escape(', '.join(pers) or '—')}</p>"
                  f"{cap_cell(n, md['parrafos_ids'], sps, md['bloqueantes'], mm)}</div>")
        T = T.replace("<tr><th>humano (caps)</th>", f"<tr><th>personas con nombre en el guion</th><td>{len(todas)}: "
                      f"{html.escape(', '.join(todas))}</td></tr><tr><th>humano (caps)</th>", 1)
        res["guion"] = {"palabras": mm["palabras"], "minutos": md["minutos"], "parrafos": st["parrafos"],
                        "frases_por_parrafo": st["frases_por_parrafo"], "de_una_frase": st["de_una_frase"],
                        "bloqueantes": md["bloqueantes"], "citas": mm["citas"], "preguntas": md["preguntas"],
                        "frases_analista": md["frases_analista"], "humano": md["humano"], "humano_caps": mm["humano_caps"],
                        "escenas_usadas": md["escenas_usadas"], "personas_con_nombre": todas, "por_cap": por_cap}
    cost_rows = "".join(f"<tr><th>{html.escape(e['etapa'])}</th><td class='n'>{e['usd']:.4f}</td><td class='n'>"
                        f"{e['segundos']:.0f} s</td></tr>" for e in costos["etapas"])
    K = (f"<div class='scroll'><table class='sum' style='min-width:0'>{cost_rows}<tr><th>total</th><td class='n'><b>"
         f"{costos['usd_total']:.4f}</b></td><td>tope 5.00</td></tr></table></div>")
    head = (f"<h1>Kyshtym / Mayak (F19: research con cirílico)</h1><p class='meta'>«{html.escape(topic.get('video_title') or '')}» · F19 = el research rehecho con los nombres locales en cirílico en `place_re`, y la misma cadena (ficha v2 → columna → "
            "escaleta v2 con antagonista persona o institución y el rango de beats de la compuerta → guion v5.1, Sol high), sin paradas. F18 sale de los respaldos. Minutos a 2.05 palabras/s.</p>"
            "<p class='meta legend'><mark class='blq'>bloqueante</mark><mark class='fecha'>fecha repetida</mark>"
            "<mark class='juicio'>juicio de la lista</mark><mark class='eco'>eco después de cita</mark>"
            "<mark class='trailer'>voz de tráiler</mark> · las marcas que no son bloqueantes no rechazan nada.</p>")
    body = (f"{head}<h2>Embudo</h2>{E}{G}<h2>Costo</h2>{K}<h2>Columna</h2>{C}<h2>Escaleta</h2>{S}<h2>Guion</h2>{T}")
    css = (".grid{grid-template-columns:1fr}table.sum td{word-break:break-word}"
           "table.emb th{white-space:normal}table.emb td{white-space:nowrap}")
    doc = (f"<!doctype html><html lang='es'><head><meta charset='utf-8'><meta name='viewport' "
           f"content='width=device-width,initial-scale=1'><title>Kyshtym F19</title><style>{CSS}{CSS_EXTRA}{css}</style>"
           f"</head><body>{body}</body></html>")
    (LAB / "compara_f19.html").write_text(doc, encoding="utf-8")
    (LAB / "resumen_f19.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print(json.dumps({k: res[k] for k in ("embudo",)}, ensure_ascii=False), "· compara_f19.html", len(doc))
    if res.get("guion"):
        r = res["guion"]
        print(f"guion {r['palabras']} pal · {r['minutos']} min · bloq {len(r['bloqueantes'])} · personas "
              f"{len(r['personas_con_nombre'])} · escenas {r['escenas_usadas']}")


if __name__ == "__main__":
    main()
