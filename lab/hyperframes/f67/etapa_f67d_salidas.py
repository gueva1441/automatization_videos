# -*- coding: utf-8 -*-
"""F67d: la tabla de los DEBERÍA de Wittenoom por código y la pestaña en Chrome headless, todo sobre una copia en un steps_dir temporal; 0
llamadas a la API. Salida: lab/hyperframes/f67/f67d/SALIDAS.md. Comprueba con steps_md5 que `_steps/<tid>/` real no cambió."""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
import threading
from http.server import ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(AQUI))

import steps_md5  # noqa: E402

TID, D = steps_md5.TID, steps_md5.STEPS
S = AQUI / "f67d"
IGNORA = shutil.ignore_patterns("_r3_cache", "fuentes", "_r1_cache.json", "fuentes_r1.json", "fuentes.json")


def etapa_a(sd: Path) -> list[str]:
    from script_engine import m01f_critico as mf
    d = sd / TID
    ps = json.loads((d / "01b_narracion_v3.json").read_text(encoding="utf-8"))["parrafos"]
    crit = mf.cargar_critica(TID, sd)
    filas = crit["validacion"]["deberia"]
    deb = [x for x in crit["respuesta"]["deberia"] if isinstance(x, dict)]
    pre = mf.borrador(ps, crit)
    todos = mf.borrador(ps, crit, {f["k"]: {"accion": "aceptar"} for f in filas})
    otra = mf.borrador(todos["parrafos"], crit, {f["k"]: {"accion": "aceptar"} for f in filas})
    L = ["## A. `borrador` sobre una copia de la narración actual de Wittenoom y su `01f_critico.json`", "",
         "| k | cap | oraciones | tramos | partes | sin decidir (`aplica`) | todos aceptados | aceptar sobre el resultado |", "|---|---|---|---|---|---|---|---|"]
    for f, x in zip(filas, deb):
        k = f["k"]
        L.append(f"| {k} | {f['cap']} | {f['idx']} | {len(mf._tramos(f))} | {len(mf._partes(x['deberia_texto']))} | {pre['por_k'][k]['aplica']} | {todos['por_k'][k]['estado']} | {otra['por_k'][k]['estado']} |")
    L += ["", f"`pendientes` con todos aceptados: {todos['pendientes']} (k=5 no aplica: `{todos['por_k'][5].get('motivo')}`).", ""]
    for k, x in zip([f["k"] for f in filas], deb):
        partes = mf._partes(x["deberia_texto"])
        for parte in partes:
            n = " ".join(p["texto"] for p in todos["parrafos"]).count(" ".join(parte.split()))
            L.append(f"- k={k}: la parte «{parte[:50]}…» aparece {n} vez/veces con todos aceptados")
    return L + [""]


def etapa_b(sd: Path) -> list[str]:
    import qa_studio_server as qa
    from playwright.sync_api import sync_playwright
    from script_engine.m01d_particion import md5_narracion
    qa._steps_dir = lambda state: sd
    qa.STATE, qa.TOPIC_ID = qa.QAState(TID, ROOT), TID
    http = ThreadingHTTPServer(("127.0.0.1", 0), qa.Handler)
    threading.Thread(target=http.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{http.server_address[1]}"
    f = sd / TID / "01b_narracion_v3.json"
    antes = f.read_bytes()
    errores: list[str] = []
    L = ["## B. La pestaña en Chrome headless (steps_dir temporal)", ""]

    def boton(pg, k, nombre):
        pg.locator(".nn-deb", has_text=f"DEBERÍA {k} ·").get_by_role("button", name=nombre, exact=True).click()
        pg.wait_for_function("!nnBusy")

    def cabecera(pg, titulo, nombre):
        marcas = pg.locator(".nn-h .nn-marca").all_inner_texts()
        btn = pg.locator("#nnAprobarBtn")
        pg.screenshot(path=str(S / f"{nombre}.png"))
        return [f"### {titulo}", "", f"- Botón «{btn.inner_text()}» apagado = **{btn.is_disabled()}** · {pg.locator('#nnFaltan').inner_text()}",
                *[f"- DEBERÍA {i}: {m}" for i, m in enumerate(marcas, start=1)], ""]

    with sync_playwright() as pw:
        br = pw.chromium.launch(channel="chrome", headless=True)
        pg = br.new_page(viewport={"width": 1400, "height": 900})
        pg.on("pageerror", lambda e: errores.append(str(e)))
        pg.goto(url + "/", wait_until="domcontentloaded")
        pg.wait_for_selector("#narrBtn")
        pg.wait_for_timeout(800)
        pg.click("#narrBtn")
        pg.wait_for_selector(".nn-deb", timeout=20000)
        L += cabecera(pg, "Sin decidir", "0_sin_decidir")
        boton(pg, 1, "Aceptar")
        boton(pg, 5, "Rechazar")
        L += cabecera(pg, "1 aceptado (k=1), 1 rechazado (k=5), 4 sin decidir", "1_parcial")
        L += [f"Sin escribir nada en disco tras esos clics: {f.read_bytes() == antes}.", ""]
        (S / "pestana_parcial.txt").write_text(pg.locator("#view").inner_text(), encoding="utf-8", newline="\n")
        boton(pg, 1, "↶ Deshacer")
        L += cabecera(pg, "Deshacer k=1", "2_deshacer")
        boton(pg, 1, "Aceptar")
        for k, nombre in ((2, "Aceptar"), (3, "Aceptar"), (4, "Aceptar"), (6, "Rechazar")):
            boton(pg, k, nombre)
        L += cabecera(pg, "Todo decidido", "3_todo_decidido")
        (S / "pestana_decidida.txt").write_text(pg.locator("#view").inner_text(), encoding="utf-8", newline="\n")
        pg.get_by_role("button", name="Aprobar narración").click()
        pg.wait_for_function("!nnBusy && NARR && NARR.estado && NARR.estado.aprobado", timeout=120000)
        L += [f"Aprobado sobre la copia: {pg.locator('.pp-estado').inner_text()}", ""]
        pg.screenshot(path=str(S / "4_aprobada.png"))
        br.close()
    http.shutdown()
    n3 = json.loads(f.read_text(encoding="utf-8"))
    txt = " ".join(p["texto"] for p in n3["parrafos"])
    L += [f"Copia después de aprobar: md5 `{md5_narracion(n3)}`, `aprobado.md5` igual = {n3['aprobado']['md5'] == md5_narracion(n3)}; «Y no fue el único que se llevó Wittenoom adentro.» aparece {txt.count('Y no fue el único que se llevó Wittenoom adentro.')} vez.",
          "", f"Errores de página: {len(errores)} {errores[:3]}", ""]
    return L


def main() -> None:
    S.mkdir(exist_ok=True)
    steps_md5.foto("F67d_antes")
    with tempfile.TemporaryDirectory() as td:
        sd = Path(td) / "steps"
        shutil.copytree(D, sd / TID, ignore=IGNORA)
        L = ["# F67d — salidas", ""] + etapa_a(sd) + etapa_b(sd)
    steps_md5.foto("F67d_despues")
    L += ["## Topic real", "", f"Archivos de `_steps/<tid>/` que cambiaron: {steps_md5.compara('F67d_antes', 'F67d_despues') or 'ninguno'}", ""]
    (S / "SALIDAS.md").write_text("\n".join(L), encoding="utf-8", newline="\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
