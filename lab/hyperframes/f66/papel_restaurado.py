# -*- coding: utf-8 -*-
"""
lab/hyperframes/f66/papel_restaurado.py — F66b Etapa 2, salida (solo lectura, CERO llamadas): PAPEL_RESTAURADO.md con la tabla del papel,
los descartes del verificador, el cierre y el costo; confirma en Chrome headless que el QA Studio, con el papel de producción, lo muestra en
PAPEL con el aviso de los 7 «contradice» en la cabecera (GET /papel y la vista: no toca ningún botón; md5 del papel antes y después).
"""
from __future__ import annotations

import hashlib
import json
import sys
import threading
from http.server import ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

import fase1_5 as f15  # noqa: E402
import qa_studio_server as qa  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

TID = "123bbb64-9fca-4395-8bf4-57d60e219ef1"
D = ROOT / "data/scripts/_steps" / TID
F = Path(__file__).resolve().parent


def c(t: object) -> str:
    return str(t if t is not None else "—").replace("|", "/").replace("\n", " ")


def main() -> None:
    fp = D / "01e_pantalla.json"
    antes = hashlib.md5(fp.read_bytes()).hexdigest()
    p = json.loads(fp.read_text(encoding="utf-8"))
    raw = json.loads((D / "01e_pantalla.raw.json").read_text(encoding="utf-8"))
    md = (D / "01e_pantalla.md").read_text(encoding="utf-8")
    L = ["# F66b Etapa 2 — el papel sobre la narración restaurada", "",
         f"`{p['prompt_version']}` · {p['modelo']} {p['effort']} · narración `{hashlib.md5((D / '01b_narracion_v3.json').read_bytes()).hexdigest()}` · entrada `{p['entrada_md5']}` · "
         f"{sum(1 for b in p['beats'] if b['ficha'])} de {len(p['beats'])} fichas · {sum(1 for b in p['beats'] if b['sello'])} sellos · {len(p['relojes'])} relojes · cierre **{p['reintento'].get('cierre')}** tras "
         f"{len(p['reintento'].get('vueltas') or [])} vuelta(s) · **sin aprobar**: {f15.estado_papel(TID)[1]}", "",
         "| beat | cap | función | ficha | texto | oración ancla |", "|---|---|---|---|---|---|"]
    for b in p["beats"]:
        f = b["ficha"]
        if f:
            au = f" — {f['autor']}" if f.get("autor") else ""
            L.append(f"| {b['beat']} | {b['cap']} | {c(b['funcion'])}{' ⚡' if b['pico'] else ''} | {f['pool_id']} | {c(f['etiqueta'])} · {c(f['texto'])}{c(au) if au else ''} | [{f['sentence_idx']}] {c(f['oracion'])} |")
        else:
            L.append(f"| {b['beat']} | {b['cap']} | {c(b['funcion'])}{' ⚡' if b['pico'] else ''} | — | sin ficha | — |")
    L += ["", "## Descartes del verificador", ""]
    cort = [d for d in p["descartados"] if d.get("quien") == "verificador"]
    L += [f"- {d.get('cap')} beat {d.get('beat')} · {d.get('pool_id')} «{d.get('etiqueta')} · {d.get('texto')}» → {d.get('regla')}: {d.get('motivo')}" for d in cort] or ["- En el papel final: ninguno."]
    L += ["", "Por llamada (incluye lo que se cortó en el intento 1 y la vuelta reemplazó):", "",
          "| llamada | marcas | pasa | corta | dicho | no_dicho | US$ |", "|---|---|---|---|---|---|---|"]
    for k, r in enumerate(raw.get("verificador") or []):
        vs = r["veredictos"]
        n = lambda lista, v: sum(1 for x in vs[lista] if x["veredicto"] == v)  # noqa: E731
        L.append(f"| {k + 1} | {len(r['marcas'])} | {n('fichas', 'pasa')} | {n('fichas', 'corta')} | {n('descartes', 'dicho')} | {n('descartes', 'no_dicho')} | {r['usd']:.4f} |")
        for x in vs["fichas"]:
            if x["veredicto"] == "corta":
                L.append(f"| → corta | {x['pool_id']} ({x['cap']} b{x['beat']}) | {c(x['motivo'])} | | | | |")
    otros = [d for d in p["descartados"] if d.get("quien") == "validación"]
    if otros:
        L += ["", "Cortes del código en el papel final:"] + [f"- {d.get('pool_id')}: {d.get('regla')}: {d.get('motivo')}" for d in otros]
    vac = p.get("a_pantalla_vacios") or []
    L += ["", f"`a_pantalla` como aviso (⚠, no obligan): {', '.join(x['id'] + ' (b' + str(a['beat']) + ')' for a in vac for x in a['ids']) or 'ninguno'}", "", "## Costo por llamada", "",
          "| llamada | in | escritos al caché | leídos | out | US$ | s |", "|---|---|---|---|---|---|---|"]
    for k, i in enumerate(raw["intentos"]):
        u = i["usage"]
        L.append(f"| autor {'intento 1' if k == 0 else 'vuelta ' + str(k)} | {u.get('input_tokens')} | {u.get('cache_creation_input_tokens') or 0} | {u.get('cache_read_input_tokens') or 0} | {u.get('output_tokens')} | {i['usd']:.4f} | {i['segundos']} |")
    for k, r in enumerate(raw.get("verificador") or []):
        u = r.get("usage") or {}
        L.append(f"| verificador {k + 1} | {u.get('input_tokens')} | — | — | {u.get('output_tokens')} | {r['usd']:.4f} | {r['segundos']} |")
    L.append(f"| **total** | | | | | **{p['usd']:.4f}** (autor {p['usd_autor']:.4f} + verificador {p['usd_verificador']:.4f}) | |")
    # ── el QA Studio, de verdad, sobre producción: solo lectura
    qa.STATE, qa.TOPIC_ID = qa.QAState(TID, ROOT), TID
    assert qa._preflight(qa.STATE) == []
    http = ThreadingHTTPServer(("127.0.0.1", 0), qa.Handler)
    threading.Thread(target=http.serve_forever, daemon=True).start()
    errores: list[str] = []
    with sync_playwright() as pw:
        br = pw.chromium.launch(channel="chrome", headless=True)
        pg = br.new_page(viewport={"width": 1320, "height": 1000})
        pg.on("pageerror", lambda e: errores.append(str(e)))
        pg.goto(f"http://127.0.0.1:{http.server_address[1]}/", wait_until="domcontentloaded")
        pg.wait_for_selector("#papelBtn")
        pg.wait_for_timeout(800)
        pg.click("#papelBtn")
        pg.wait_for_selector(".pp-beat", timeout=20000)
        beats = pg.locator(".pp-beat").count()
        est = pg.locator(".pp-estado").inner_text()
        aviso = pg.locator(".pp-aviso").first.inner_text()
        pg.wait_for_timeout(400)
        pg.screenshot(path=str(F / "papel_restaurado_qa.png"))
        br.close()
    http.shutdown()
    lineas_aviso = [x for x in aviso.splitlines() if x.strip().startswith("ch")]
    final = md[md.index("## Descartados por el modelo"):] if "## Descartados por el modelo" in md else ""
    sec = final[final.index("## ⚠ Aviso"):] if "## ⚠ Aviso" in final else ""
    en_md = [x for x in sec.splitlines() if x.startswith("- ch")]
    despues = hashlib.md5(fp.read_bytes()).hexdigest()
    parada = f15.parada_del_papel(TID)
    L += ["", "## Confirmación del QA Studio y del aviso", "",
          f"- QA Studio → 📄 PAPEL en Chrome headless, con el papel de producción y sin tocar botones: {beats} beats · estado «{est}» · {len(errores)} errores de página · captura `papel_restaurado_qa.png`.",
          f"- Cabecera de la vista: {len(lineas_aviso)} «contradice» en el aviso.",
          f"- Final del `01e_pantalla.md`: sección de aviso {'presente y última' if sec else 'AUSENTE'}, {len(en_md)} «contradice».",
          f"- PARADA: {'lleva el aviso' if '7 punto(s)' in parada else 'SIN EL AVISO DE 7'}: «{[x.strip() for x in parada.splitlines() if '⚠' in x][0][:110] if '⚠' in parada else ''}…»",
          f"- md5 del papel antes y después de mirar: `{antes}` / `{despues}` ({'iguales' if antes == despues else 'DISTINTOS'}).", "", "En la cabecera:", ""]
    L += [f"- {x.strip()}" for x in lineas_aviso]
    L.append("")
    (F / "PAPEL_RESTAURADO.md").write_text("\n".join(L), encoding="utf-8", newline="\n")
    print("\n".join(L))
    assert beats == 13 and len(lineas_aviso) == 7 and len(en_md) == 7 and antes == despues and not errores and "7 punto(s)" in parada


if __name__ == "__main__":
    main()
