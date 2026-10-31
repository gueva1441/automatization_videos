# -*- coding: utf-8 -*-
"""
lab/hyperframes/f65/ui/capturas.py — F65b Etapa C, salida: 3 capturas de la vista PAPEL en un navegador de verdad, sobre una COPIA del papel
actual (producción intacta) y con `sugerir` falso que devuelve el resultado guardado de la Etapa A (sugerir_prueba.json): 0 llamadas.
  1_general.png         la vista general
  2_sugerir.png         un beat con las alternativas de «sugerir»
  3_invalidada.png      «aprobación invalidada por edición»
  01e_pantalla.revision.json  el resultante
Falla si la consola del navegador tira un error.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
import tempfile
import threading
import time
from http.server import ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

import fase1_5 as f15  # noqa: E402
import qa_studio_server as qa  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402
from script_engine import m01e_pantalla as mp  # noqa: E402

TID = "123bbb64-9fca-4395-8bf4-57d60e219ef1"
REAL = ROOT / "data/scripts/_steps" / TID
AQUI = Path(__file__).resolve().parent
ARCHIVOS = ("01e_pantalla.json", "01e_pantalla.md", "01e_pantalla.raw.json")


def main() -> None:
    md5_real = hashlib.md5((REAL / ARCHIVOS[0]).read_bytes()).hexdigest()
    tmp = Path(tempfile.mkdtemp(prefix="f65b_ui_"))
    d = tmp / "data/scripts/_steps" / TID
    d.mkdir(parents=True)
    for n in ARCHIVOS:
        shutil.copy2(REAL / n, d / n)
    f15.STEPS_DIR = d.parent
    guardado = json.loads((ROOT / "lab/hyperframes/f65/sugerir_prueba.json").read_text(encoding="utf-8"))["a"]

    def sugerir_falso(tid, cap, beat, n, *, steps_dir=None, **k):
        time.sleep(0.5)
        return {**guardado, "cap": cap, "beat": beat}
    mp.sugerir = sugerir_falso
    qa.STATE, qa.TOPIC_ID = qa.QAState(TID, tmp), TID
    assert qa._preflight(qa.STATE) == [], "preflight con solo el papel"
    http = ThreadingHTTPServer(("127.0.0.1", 0), qa.Handler)
    threading.Thread(target=http.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{http.server_address[1]}/"
    errores: list[str] = []
    with sync_playwright() as pw:
        br = pw.chromium.launch(channel="chrome", headless=True)
        pg = br.new_page(viewport={"width": 1320, "height": 1000})
        pg.on("pageerror", lambda e: errores.append(f"pageerror: {e}"))
        pg.on("console", lambda m: errores.append(f"console: {m.text} ({m.location.get('url')})")
              if m.type == "error" and not str(m.location.get("url") or "").endswith("/favicon.ico") else None)
        pg.goto(url, wait_until="domcontentloaded")
        pg.wait_for_selector(".pp-beat", timeout=20000)      # sin caps abre el papel solo
        assert pg.locator(".pp-beat").count() == 13, pg.locator(".pp-beat").count()
        pg.wait_for_timeout(600)
        pg.screenshot(path=str(AQUI / "1_general.png"), full_page=False)
        # ✓ una ficha; revisión fuera del papel
        b1 = pg.locator("#beat-ch01-1")
        b1.get_by_text("Aprobar ficha").click()
        pg.wait_for_selector("#beat-ch01-1.rev")
        b2 = pg.locator("#beat-ch02-2")
        b2.get_by_text("Aprobar ficha").click()
        pg.wait_for_selector("#beat-ch02-2.rev")
        # sugerir
        pg.locator("#beat-ch01-1").get_by_text("Sugerir").click()
        pg.wait_for_selector("#beat-ch01-1 .pp-alts .pp-btn.pri", timeout=15000)
        pg.locator("#beat-ch01-1").scroll_into_view_if_needed()
        pg.locator("#beat-ch01-1").screenshot(path=str(AQUI / "2_sugerir.png"))
        assert pg.locator("#beat-ch01-1 .pp-alts .pp-btn.pri").count() == len(guardado["alternativas"])
        # «Ninguna» cierra sin tocar nada
        pg.locator("#beat-ch01-1").get_by_text("Ninguna").click()
        assert pg.locator("#beat-ch01-1 .pp-alts").count() == 0
        # aprobar sin quién → error; con quién → aprobado (en la copia)
        pg.get_by_text("Aprobar papel").click()
        pg.wait_for_selector(".err")
        pg.fill("#ppQuien", "Prueba de captura")
        pg.get_by_text("Aprobar papel").click()
        pg.wait_for_selector(".pp-estado.ok")
        # quitar con confirmación en la fila (sin confirm() del navegador)
        pg.locator("#beat-ch05-9").get_by_text("Quitar").click()
        pg.locator("#beat-ch05-9").get_by_text("Sí, quitar").click()
        pg.wait_for_selector(".pp-estado.no")
        assert "sin ficha" in pg.locator("#beat-ch05-9").inner_text()
        pg.evaluate("window.scrollTo(0,0)")
        # editar texto inline y guardar
        pg.locator("#beat-ch04-8").get_by_text("Editar texto").click()
        pg.fill("#ppTx", "Productor de televisión")
        pg.locator("#beat-ch04-8").get_by_text("Guardar").click()
        pg.wait_for_function("document.querySelector('#beat-ch04-8 .pp-tx')?.textContent==='Productor de televisión'")
        pg.evaluate("window.scrollTo(0,0)")
        pg.wait_for_timeout(300)
        pg.screenshot(path=str(AQUI / "3_invalidada.png"), full_page=False)
        estado = pg.locator(".pp-estado").inner_text() + " | " + pg.locator(".pp-meta").first.inner_text()
        br.close()
    http.shutdown()
    shutil.copy2(d / "01e_pantalla.revision.json", AQUI / "01e_pantalla.revision.json")
    assert hashlib.md5((REAL / ARCHIVOS[0]).read_bytes()).hexdigest() == md5_real, "producción cambió"
    assert not (REAL / "01e_pantalla.revision.json").exists()
    shutil.rmtree(tmp, ignore_errors=True)
    print("estado final en la copia:", estado)
    print("errores de consola:", errores)
    print("revisión:", (AQUI / "01e_pantalla.revision.json").read_text(encoding="utf-8").replace("\n", " "))
    print("producción md5", md5_real, "intacta")
    if errores:
        raise SystemExit("hubo errores en la consola")


if __name__ == "__main__":
    main()
