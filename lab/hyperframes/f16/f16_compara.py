"""F16 §2 — compara_f16.html: por tema, F15b | F16.

    Ycuá     F15b = guion v5.1 sobre la escaleta F15 (el sustituto: la escaleta F15b no salió) | F16 = escaleta v2 + v5.1
    Orleans  F15b = escaleta F15b (Pro) + guion v5.1                                          | F16 = escaleta v2 + v5.1

Arriba de cada tema, la escaleta de cada versión: humano (¿candidato de la ficha?), pico (¿el de la ficha?), beats por
cap, escenas usadas (gancho y pico), giros con beat, curva de intensidad, flash-forward, bloqueantes (los 13 de F16,
re-medidos con el código de hoy) y las métricas (lo que antes rechazaba y ahora solo se ve). Después, el embudo y la
tabla del guion (palabras, minutos, párrafos, frases por párrafo, bloqueantes del guion) y el texto por cap lado a lado.
No llama a ninguna API. Deja `resumen_f16.json`.
Uso: python -I lab/hyperframes/f16/f16_compara.py
"""
from __future__ import annotations

import html
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
LAB = Path(__file__).resolve().parent
for d in ("f11", "f11b", "f11c", "f13", "f14", "f15", "f15b"):
    sys.path.insert(1, str(LAB.parent / d))
sys.path.insert(1, str(LAB))
TEMAS = {"ycua": ("f8s1-ycua-bolanos", "Ycuá Bolaños", "ycua"), "orleans": ("ba6c3cac-f7r3", "Orleans", "orl")}


def _j(p: Path):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def versiones(nom: str) -> list[dict]:
    from script_engine.m01a_skeleton import STEPS_DIR
    tid, _, t = TEMAS[nom]
    d = STEPS_DIR / tid
    ficha = _j(LAB.parent / "f15b" / f"ficha_{nom}" / "ficha_caso.json")
    c15b = _j(LAB.parent / "f15b" / "costos_f15b.json") or {}
    c16 = _j(LAB / "costos_f16.json") or {}
    out = []
    if nom == "ycua":
        g = _j(LAB.parent / "f15b" / "guion_ycua_f15b_escf15.json")
        out.append({"nombre": "F15b · escaleta F15 (Pro) + v5.1 (sustituto)", "clave": "f15b", "parrafos": g["parrafos"],
                    "esc": _j(d / "01a_escaleta_f15.json"), "ficha": ficha, "sel_nombre": "ficha v2 re-chequeada",
                    "usd": None, "usd_nota": "ver F15b"})
    else:
        g = _j(LAB.parent / "f15b" / "guion_orleans_f15b.json")
        out.append({"nombre": "F15b · escaleta F15b (Pro) + v5.1", "clave": "f15b", "parrafos": g["parrafos"],
                    "esc": _j(d / "01a_escaleta_f15b.json"), "ficha": ficha, "sel_nombre": "ficha v2 re-chequeada",
                    "usd": round(sum(e["usd"] for e in c15b.get("etapas") or [] if e["tema"] == t), 4)})
    g = _j(LAB / f"guion_{nom}_f16.json")
    esc = _j(d / "01a_escaleta_f16.json")
    usd = round(sum(e["usd"] for e in c16.get("etapas") or [] if e["tema"] == t), 4)
    if esc:
        out.append({"nombre": "F16 · escaleta v2 (Sol) + v5.1", "clave": "f16", "parrafos": (g or {}).get("parrafos") or [],
                    "esc": esc, "ficha": ficha, "sel_nombre": "ficha v2 re-chequeada", "usd": usd,
                    "error": (g or {}).get("error")})
    return out


def escaleta_view(esc: dict, pool: dict, ficha: dict) -> dict:
    from script_engine import m01a_escaleta as ma
    raw = {k: v for k, v in esc.items() if not k.startswith("_")}
    _, bloq, rep, otros = ma.bloqueantes(raw, pool, ficha)
    m = ma.metricas_escaleta(esc, pool, ficha, otros)
    caps = [sum(1 for b in esc["beats"] if b["cap"] == n) for n in range(1, 8)]
    return {"bloqueantes": bloq, "metricas": m, "beats_por_cap": caps, "beats": len(esc["beats"]),
            "humano": (esc.get("humano") or {}).get("nombre"), "pico": esc.get("pico"),
            "prompt_version": esc.get("prompt_version"), "intentos": len(esc.get("_intentos") or [])}


def section(nom: str) -> tuple[str, list[dict]]:
    import fase1_5 as f15
    from f11_compara import cap_cell, spans
    from f15_compara import medir
    from f15b_compara import parrafos_stats
    from script_engine import evidence as ev
    tid, titulo, _ = TEMAS[nom]
    topic = dict(f15._load_topic_by_id(tid))
    pool = topic["evidence_pool"]
    topic["_pool_ids"] = {i for i, it in ev.items(pool).items()
                          if it["_kind"] in ("datos", "cronologia", "citas", "personajes", "lugares")}
    vs = versiones(nom)
    evs = [escaleta_view(v["esc"], pool, v["ficha"]) for v in vs]
    meds = [medir(topic, v) if v["parrafos"] else None for v in vs]
    sts = [parrafos_stats(v["parrafos"]) if v["parrafos"] else None for v in vs]
    # escaleta
    t1 = ("<div class='scroll'><table class='sum'><tr><th>escaleta</th><th>versión del prompt</th><th>beats (por cap)</th>"
          "<th>humano</th><th>¿candidato?</th><th>pico</th><th>¿el de la ficha?</th><th>curva</th><th>flash-forward</th>"
          "<th>escenas (gancho / pico)</th><th>giros con beat</th><th>bloqueantes (13)</th></tr>")
    for v, e in zip(vs, evs):
        m = e["metricas"]
        t1 += (f"<tr><th>{html.escape(v['nombre'])}</th><td>{e['prompt_version']}</td>"
               f"<td>{e['beats']} ({' · '.join(map(str, e['beats_por_cap']))})</td><td>{html.escape(e['humano'] or '—')}</td>"
               f"<td>{m['humano_en_candidatos']}</td><td>beat {e['pico'].get('beat')} · {e['pico'].get('id')}</td>"
               f"<td>{m['pico_es_el_de_la_ficha']}</td><td>{' '.join(map(str, m['curva_intensidad']))}</td>"
               f"<td>{m['flash_forward_beat1']}</td><td>{', '.join(f'E{x}' for x in m['escenas_usadas']) or '—'} "
               f"({m['escena_gancho'] or '—'} / {m['escena_pico'] or '—'})</td>"
               f"<td>{m['giros_con_beat']}/{m['giros_total']}</td><td class='n'>{len(e['bloqueantes'])}</td></tr>")
    t1 += "</table></div>"
    met = "".join(
        f"<details><summary>Métricas de la escaleta · {html.escape(v['nombre'])}</summary><ul>"
        + "".join(f"<li><b>{html.escape(k)}</b>: {html.escape(json.dumps(x, ensure_ascii=False))}</li>"
                  for k, x in e["metricas"].items())
        + ("<li><b>bloqueantes</b>: " + html.escape("; ".join(e["bloqueantes"])) + "</li>" if e["bloqueantes"] else "")
        + "</ul></details>" for v, e in zip(vs, evs))
    # guion
    t2 = ("<div class='scroll'><table class='sum'><tr><th>guion</th><th>palabras</th><th>min</th><th>párrafos</th>"
          "<th>frases / párrafo</th><th>párrafos de 1 frase</th><th>bloq.</th><th>duras v3</th><th>citas</th>"
          "<th>preguntas</th><th>frases de analista</th><th>humano (caps)</th><th>embudo pool → ficha → escaleta → guion</th>"
          "<th>US$</th></tr>")
    res = []
    for v, e, md, st in zip(vs, evs, meds, sts):
        if not md:
            t2 += f"<tr><th>{html.escape(v['nombre'])}</th><td colspan='13' class='bad'>sin guion</td></tr>"
            continue
        mm = md["metricas"]
        emb = md["embudo"]
        usd = f"{v['usd']:.3f}" if v.get("usd") is not None else "—"
        t2 += (f"<tr><th>{html.escape(v['nombre'])}</th><td class='n'>{mm['palabras']}</td><td class='n'><b>{md['minutos']}"
               f"</b></td><td class='n'>{st['parrafos']}</td><td class='n'>{st['frases_por_parrafo']}</td>"
               f"<td class='n'>{st['de_una_frase']}</td><td class='n'>{len(md['bloqueantes'])}</td>"
               f"<td class='n'>{len(mm['duras_v3'])}</td><td class='n'>{mm['citas']}</td><td class='n'>{md['preguntas']}</td>"
               f"<td class='n'>{sum(md['frases_analista'].values())}</td><td>{html.escape(md['humano'] or '—')} "
               f"{mm['humano_caps']}</td><td>{emb['pool']} → {emb['seleccion']} → {emb['escaleta']} → {emb['guion']}</td>"
               f"<td class='n'>{usd}</td></tr>")
        res.append({"tema": nom, "clave": v["clave"], "nombre": v["nombre"], "usd": v.get("usd"),
                    "escaleta": {k: e[k] for k in ("bloqueantes", "beats", "beats_por_cap", "humano", "pico",
                                                   "prompt_version", "intentos")} | {"metricas": e["metricas"]},
                    "guion": {"palabras": mm["palabras"], "minutos": md["minutos"], "palabras_por_cap": mm["palabras_por_cap"],
                              **{k: st[k] for k in ("parrafos", "frases_por_parrafo", "de_una_frase", "por_cap")},
                              "bloqueantes": md["bloqueantes"], "duras_v3": len(mm["duras_v3"]), "citas": mm["citas"],
                              "preguntas": md["preguntas"], "frases_analista": md["frases_analista"],
                              "humano_caps": mm["humano_caps"], "cierre": mm["cierre"], "embudo": emb}})
    t2 += "</table></div>"
    caps = [f"<div class='grid hdr'><div>{html.escape(vs[0]['nombre'])}</div><div>{html.escape(vs[-1]['nombre'])}</div></div>"]
    for n in range(1, 8):
        cells = []
        for v, md, st in zip(vs, meds, sts):
            if not md:
                cells.append("<div class='col'>—</div>")
                continue
            ps, mm = md["parrafos_ids"], md["metricas"]
            w = (mm["palabras_por_cap"].get(n) or [0, 0])[0]
            pc = st["por_cap"][n]
            cells.append(f"<div class='col'><p class='ids'>{w} palabras · {round(w / 2.05)} s · {pc['parrafos']} párrafos · "
                         f"{pc['frases_por_parrafo']} frases/párrafo · "
                         f"{len([x for x in md['bloqueantes'] if x.get('cap') == n])} bloqueante(s)</p>"
                         f"{cap_cell(n, ps, spans(ps, pool, md['bloqueantes']), md['bloqueantes'], mm)}</div>")
        caps.append(f"<h3>{titulo} · Cap {n}</h3><div class='grid'>{''.join(cells)}</div>")
    return (f"<h2>{titulo}</h2><h3>Escaleta</h3>{t1}{met}<h3>Guion</h3>{t2}{''.join(caps)}", res)


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    from f11_compara import CSS
    from f11b_compara import CSS_EXTRA
    sy, ry = section("ycua")
    so, ro = section("orleans")
    costos = _j(LAB / "costos_f16.json") or {}
    head = ("<h1>Escaleta v2: 13 bloqueantes, oficio, Sol (F16)</h1>"
            "<p class='meta'>F16 = la ficha v2 re-chequeada de F15b → escaleta v2 (prompt del analista, Sol high, solo 13 "
            "bloqueantes, una regeneración) → guion v5.1 (Sol high). F15b = la escaleta de Pro con todas las reglas. Los "
            "bloqueantes y las métricas de las dos escaletas se re-miden con el código de hoy. Minutos a 2.05 palabras/s. "
            f"Costo de la tanda F16: US$ {costos.get('usd_total', 0):.3f} (tope 2.00).</p>"
            "<p class='meta legend'><mark class='blq'>bloqueante</mark><mark class='fecha'>fecha repetida</mark>"
            "<mark class='juicio'>juicio de la lista</mark><mark class='eco'>eco después de cita</mark>"
            "<mark class='trailer'>voz de tráiler</mark> · las marcas que no son bloqueantes no rechazan nada.</p>")
    css = ("@media (max-width:760px){.grid .col:first-child::before{content:'F15b'}"
           ".grid .col:last-child::before{content:'F16'}}")
    doc = (f"<!doctype html><html lang='es'><head><meta charset='utf-8'><meta name='viewport' "
           f"content='width=device-width,initial-scale=1'><title>Escaleta v2</title><style>{CSS}{CSS_EXTRA}{css}"
           f"</style></head><body>{head}{sy}{so}</body></html>")
    (LAB / "compara_f16.html").write_text(doc, encoding="utf-8")
    (LAB / "resumen_f16.json").write_text(json.dumps(ry + ro, ensure_ascii=False, indent=1), encoding="utf-8")
    for r in ry + ro:
        e, g = r["escaleta"], r["guion"]
        m = e["metricas"]
        print(f"{r['tema']:7} {r['clave']:4} ESC {e['beats']} beats {e['beats_por_cap']} · humano {e['humano']} (cand "
              f"{m['humano_en_candidatos']}) · pico {e['pico'].get('beat')}/{e['pico'].get('id')} (ficha "
              f"{m['pico_es_el_de_la_ficha']}) · curva {m['curva_intensidad']} ff {m['flash_forward_beat1']} · escenas "
              f"{m['escenas_usadas']} g/p {m['escena_gancho']}/{m['escena_pico']} · giros {m['giros_con_beat']}/"
              f"{m['giros_total']} · bloq {len(e['bloqueantes'])}")
        print(f"        GUION {g['palabras']} pal · {g['minutos']} min · párr {g['parrafos']} · fr/p {g['frases_por_parrafo']}"
              f" · 1fr {g['de_una_frase']} · bloq {len(g['bloqueantes'])} · citas {g['citas']} · ? {g['preguntas']} · "
              f"humano caps {g['humano_caps']} · US$ {r['usd']}")
    print("compara_f16.html", len(doc))


if __name__ == "__main__":
    main()
