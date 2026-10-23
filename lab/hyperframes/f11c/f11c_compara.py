"""F11c §2 — compara_f11c.html (Ycuá): v3 (v1), F11b sol crudo, F11b astra crudo, y las dos corridas v4c (argon y sol),
cada una cruda y final. Todo se re-mide con el código de hoy (bloqueantes a–e, duras v3, ids por beat). Misma forma que
compara_f11b.html (reusa lab/hyperframes/f11b/f11b_compara.py, solo lectura) más dos columnas de MÉTRICA (no rechazan
nada): «preguntas» (signos «?») y «frases de analista» (solo las que el analista marcó en F11b).
Deja `resumen_f11c.json` (lo que lee el reporte), con los tokens del prompt (sistema y usuario) contados por
`gemini-4-argon` (count_tokens, sin costo) y los que facturó cada modelo en la llamada del guionista.
Uso: python -I lab/hyperframes/f11c/f11c_compara.py
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
sys.path.insert(1, str(LAB.parent / "f11"))                 # f11_compara (marcas)
sys.path.insert(1, str(LAB.parent / "f11b"))                # f11b_compara (medición y bloques por cap)
sys.path.insert(1, str(LAB))
TID = "f8s1-ycua-bolanos"
# F11c §2: solo las expresiones que el analista ya marcó en F11b. Métrica para el reporte, no un bloqueante.
FRASES_ANALISTA = ("los datos", "el testimonio", "la frase señala", "no permiten explicar")


def preguntas(ps: list[dict]) -> int:
    return sum(p["texto"].count("?") for p in ps)


def frases_analista(ps: list[dict]) -> dict[str, int]:
    t = " ".join(p["texto"] for p in ps).lower()
    return {f: len(re.findall(rf"\b{re.escape(f)}\b", t)) for f in FRASES_ANALISTA}


def versiones(topic: dict, esc: dict) -> list[dict]:
    from f11b_compara import _j, _prep
    steps = ROOT / "data" / "scripts" / "_steps" / TID
    out = []
    v1 = _j(steps / "01b_editor_v3_v1.json")
    out.append({"nombre": "v3 (v1)", "clave": "v1", "parrafos": _prep(v1["parrafos"], esc), "declared": True,
                "usd": 0.88, "usd_nota": "guion F10 (ESTADO_SESION)", "segundos": None})
    for tag, name in (("sol", "F11b sol · gpt-6.1-sol high — crudo"), ("astra", "F11b astra · gpt-6-astra — crudo")):
        r = _j(LAB.parent / "f11b" / f"guion_ycua_v4b_{tag}.json")
        usd_g = sum(c["usd"] for c in r["costo"]["llamadas"] if c["desc"] == "guion_v4 guionista")
        out.append({"nombre": name, "clave": f"v4b_{tag}_crudo", "crudo": True, "parrafos": r["crudo"],
                    "declared": False, "usd": usd_g, "segundos": r.get("segundos_guionista")})
    for tag, name in (("argon", "v4c argon · gemini-4-argon"), ("sol", "v4c sol · gpt-6.1-sol high")):
        r = _j(LAB / f"guion_ycua_v4c_{tag}.json")
        if not r:
            continue
        if r.get("crudo"):
            usd_g = sum(c["usd"] for c in r["costo"]["llamadas"] if c["desc"] == "guion_v4 guionista")
            out.append({"nombre": f"{name} — crudo", "clave": f"{tag}_crudo", "crudo": True, "parrafos": r["crudo"],
                        "declared": False, "usd": usd_g, "segundos": r.get("segundos_guionista")})
        ps = (r.get("reparacion") or {}).get("parrafos")
        out.append({"nombre": f"{name} — final", "clave": tag, "parrafos": ps or [], "declared": False,
                    "usd": r["costo"]["usd"], "segundos": r["costo"]["segundos"], "run": r, "error": r.get("error")})
    return out


def fila(v: dict, med: dict) -> str:
    from f11b_compara import criterio
    m, bl = med["metricas"], med["bloqueantes"]
    if not m:
        return (f"<tr><th>{html.escape(v['nombre'])}</th><td colspan='11' class='bad'>"
                f"{html.escape(v.get('error') or 'sin texto')}</td></tr>")
    caps = " ".join(
        f"<span class='{'ok' if tg and 0.75 <= w / tg <= 1.25 else 'bad'}'>{w}/{tg}</span>"
        for w, tg in (m["palabras_por_cap"].get(n) or m["palabras_por_cap"].get(str(n)) or [0, 0] for n in range(1, 8)))
    ipp = m["ids_por_parrafo"]
    usd = f"{v['usd']:.3f}" if v.get("usd") is not None else "—"
    seg = f"{v['segundos']:.0f}" if v.get("segundos") is not None else "—"
    ok = criterio(m, bl)
    fa = frases_analista(v["parrafos"])
    fa_t = " · ".join(f"{k} {n}" for k, n in fa.items() if n) or "0"
    return (f"<tr{' class=crudo' if v.get('crudo') else ''}><th>{html.escape(v['nombre'])}</th>"
            f"<td class='n'>{m['palabras']}</td><td class='caps'>{caps}</td>"
            f"<td class='n'>{len(bl)}</td><td class='n'>{len(m['duras_v3'])}</td><td>{m['cierre']}</td>"
            f"<td class='n'>{preguntas(v['parrafos'])}</td><td>{html.escape(fa_t)}</td>"
            f"<td class='n'>{ipp['antes']} → {ipp['despues']}</td><td class='n'>{usd}</td><td class='n'>{seg}</td>"
            f"<td class='{'ok' if ok else 'bad'}'>{'cumple' if ok else 'no'}</td></tr>")


def tokens_prompt() -> dict:
    """Tokens del sistema y del usuario guardados, contados por gemini-4-argon (count_tokens no factura)."""
    import gemini_helpers as gh
    out = {}
    for k in ("sistema", "usuario"):
        t = (LAB / f"prompt_ycua_v4c_{k}.txt").read_text(encoding="utf-8")
        try:
            out[k] = gh._client.models.count_tokens(model="gemini-4-argon", contents=t).total_tokens
        except Exception as e:  # noqa: BLE001
            out[k] = f"{type(e).__name__}"
    return out


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    from f11_compara import CSS
    from f11b_compara import CSS_EXTRA, cap_block, criterio, medir, reparacion
    from f11c_corridas import _load
    topic, esc = _load()
    pool = topic["evidence_pool"]
    vs = versiones(topic, esc)
    meds = [medir(topic, esc, v) for v in vs]
    costos = json.loads((LAB / "costos_f11c.json").read_text(encoding="utf-8"))
    md5 = (LAB / "prompt_ycua_v4c.md5").read_text(encoding="utf-8").split()
    tok = tokens_prompt()
    head = (
        "<h1>Ycuá · guion v4c: estructura oficial + Argon vs Sol (F11c)</h1>"
        f"<p class='meta'>Escaleta fija <code>01a_escaleta_v1.json</code> (md5 e1ba1a48…), sin notas. Las dos v4c usan "
        f"el mismo prompt: sistema <code>{md5[0][:8]}</code> ({tok.get('sistema')} tokens) y usuario "
        f"<code>{md5[2][:8]}</code> ({tok.get('usuario')} tokens, contados por argon). Sin el editor m01c cuando el "
        f"crudo tiene 0 bloqueantes. Todo re-medido con el código de hoy. Criterio: bloqueantes ≤ 2, 1,350–1,700 "
        f"palabras, sin caps vacíos (la nota la da el analista). Costo de la tanda F11c: US$ "
        f"{costos.get('usd_total', 0):.3f} (tope 1.50).</p>"
        "<p class='meta'>«preguntas» = signos «?» y «frases de analista» = "
        + ", ".join(f"«{f}»" for f in FRASES_ANALISTA) + ": son métricas, no rechazan nada.</p>"
        "<p class='meta legend'><mark class='blq'>bloqueante</mark><mark class='fecha'>fecha repetida</mark>"
        "<mark class='juicio'>juicio de la lista</mark><mark class='eco'>eco después de cita</mark>"
        "<mark class='trailer'>voz de tráiler</mark> · las marcas que no son bloqueantes no rechazan nada. Por cap: "
        "palabras / objetivo (verde dentro de ±25 %). Las filas en cursiva son crudos.</p>")
    tabla = ("<div class='scroll'><table class='sum'><tr><th>versión</th><th>palabras</th><th>por cap / objetivo</th>"
             "<th>bloq.</th><th>duras v3</th><th>cierre</th><th>preguntas</th><th>frases de analista</th>"
             "<th>ids/párrafo antes → después</th><th>US$</th><th>seg.</th><th>criterio</th></tr>"
             + "".join(fila(v, m) for v, m in zip(vs, meds)) + "</table></div>")
    blq = []
    for v, med in zip(vs, meds):
        if med["bloqueantes"]:
            blq.append(f"<details><summary>{html.escape(v['nombre'])} · {len(med['bloqueantes'])} bloqueante(s)</summary>"
                       "<ul class='blq'>" + "".join(
                           f"<li>({x['codigo']}) cap {x['cap']} beat {x['beat']}: {html.escape(x['motivo'])}</li>"
                           for x in med["bloqueantes"]) + "</ul></details>")
    caps = "".join(cap_block(n, vs, meds, pool) for n in range(1, 8))
    body = (f"{head}<h2>Resumen</h2>{tabla}<h2>Bloqueantes</h2>{''.join(blq) or '<p>Ninguna versión tiene.</p>'}"
            f"<h2>Texto por cap</h2>{caps}")
    doc = (f"<!doctype html><html lang='es'><head><meta charset='utf-8'><meta name='viewport' "
           f"content='width=device-width,initial-scale=1'><title>Guion v4c Ycuá</title><style>{CSS}{CSS_EXTRA}</style>"
           f"</head><body>{body}</body></html>")
    (LAB / "compara_f11c.html").write_text(doc, encoding="utf-8")
    res = {"tokens_prompt_argon": tok, "prompt_md5": {"sistema": md5[0], "usuario": md5[2]}, "versiones": []}
    for v, med in zip(vs, meds):
        m = med["metricas"]
        run = v.get("run") or {}
        g_in = [c for c in (run.get("costo") or {}).get("llamadas") or [] if c["desc"] == "guion_v4 guionista"]
        res["versiones"].append({
            "nombre": v["nombre"], "clave": v["clave"], "error": v.get("error"), "usd": v.get("usd"),
            "segundos": v.get("segundos"), "bloqueantes": med["bloqueantes"],
            "criterio": criterio(m, med["bloqueantes"]) if m else False,
            "preguntas": preguntas(v["parrafos"]), "frases_analista": frases_analista(v["parrafos"]),
            "guionista_tokens": g_in,
            "metricas": {k: m[k] for k in ("palabras", "palabras_por_cap", "cierre", "ids_por_parrafo", "citas",
                                           "humano_caps")} | {"duras_v3": m["duras_v3"]} if m else None,
            "reparacion": reparacion(v), "juez": run.get("juez")})
    (LAB / "resumen_f11c.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print("tokens prompt (argon):", tok)
    for r in res["versiones"]:
        m = r["metricas"] or {}
        print(f"{r['nombre']:42} {m.get('palabras', '—'):>5} pal · bloq {len(r['bloqueantes'])} · duras "
              f"{len(m.get('duras_v3') or [])} · ? {r['preguntas']} · analista {sum(r['frases_analista'].values())} · "
              f"criterio {r['criterio']}")
    print("compara_f11c.html", len(doc))


if __name__ == "__main__":
    main()
