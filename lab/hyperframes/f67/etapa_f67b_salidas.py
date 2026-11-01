# -*- coding: utf-8 -*-
"""F67b: las salidas en texto, 0 llamadas a la API y nada de producción corre. Sobre Wittenoom solo lee (POST /papel/aprobar responde
409 sin escribir); lo que borra o escribe corre sobre una copia temporal. Salida: lab/hyperframes/f67/f67b/SALIDAS.md."""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(AQUI))

import steps_md5  # noqa: E402

TID, D = steps_md5.TID, steps_md5.STEPS
S = AQUI / "f67b"
IGNORA = shutil.ignore_patterns("_r3_cache", "fuentes", "_r1_cache.json", "fuentes_r1.json", "fuentes.json")


def copia(base: Path) -> Path:
    sd = base / "steps"
    shutil.copytree(D, sd / TID, ignore=IGNORA)
    return sd


def etapa1(f15, rp) -> list[str]:
    from script_engine.m01d_particion import md5_narracion
    n3 = json.loads((D / "01b_narracion_v3.json").read_text(encoding="utf-8"))
    p = json.loads((D / "01e_pantalla.json").read_text(encoding="utf-8"))
    return ["## 1. `papel_falta` y `etapa_de`", "", "Wittenoom hoy (narración sin aprobar):", "",
            f"- `papel_falta` → `{f15.papel_falta(TID)}` (el papel tiene `narracion_md5` = {p.get('narracion_md5')}; narración `{md5_narracion(n3)}`)",
            f"- `etapa_de` → `{rp.etapa_de(TID)}`", ""]


def etapa1_copia(f15, rp, sd: Path) -> list[str]:
    """Con la narración aprobada, sobre la copia: `etapa_de` lee rutas de rp, se le apuntan a la copia."""
    f15.STEPS_DIR = sd
    rp._steps_path = lambda tid, n: sd / tid / n
    rp._papel_md_path = lambda tid: sd / tid / "01e_pantalla.md"
    ap = f15.aprobar_narracion(TID, "Prueba 2026-10-31")
    return ["Sobre una copia, con la narración aprobada:", "", f"- aprobada: `{ap['md5']}`", f"- `papel_falta` → `{f15.papel_falta(TID)}`", f"- `etapa_de` → `{rp.etapa_de(TID)}`", ""]


def etapa2() -> list[str]:
    import qa_studio_server as qa
    from playwright.sync_api import sync_playwright
    qa.STATE, qa.TOPIC_ID = qa.QAState(TID, ROOT), TID
    http = ThreadingHTTPServer(("127.0.0.1", 0), qa.Handler)
    threading.Thread(target=http.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{http.server_address[1]}"
    req = urllib.request.Request(url + "/papel/aprobar", data=json.dumps({"por": "Prueba"}).encode(), headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req) as r:
            post = (r.status, r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        post = (e.code, e.read().decode("utf-8"))
    errores: list[str] = []
    with sync_playwright() as pw:
        br = pw.chromium.launch(channel="chrome", headless=True)
        pg = br.new_page(viewport={"width": 1400, "height": 900})
        pg.on("pageerror", lambda e: errores.append(str(e)))
        pg.goto(url + "/", wait_until="domcontentloaded")
        pg.wait_for_selector("#papelBtn")
        pg.wait_for_timeout(800)
        pg.click("#papelBtn")
        pg.wait_for_selector(".pp-beat", timeout=20000)
        boton = pg.locator(".pp-aprobar button")
        disabled = boton.is_disabled()
        aviso = pg.locator("#ppBloqueo").inner_text()
        txt = pg.locator("#view").inner_text()
        pg.screenshot(path=str(S / "papel_bloqueado.png"))
        br.close()
    http.shutdown()
    (S / "papel_pestana.txt").write_text(txt, encoding="utf-8", newline="\n")
    return ["## 2. `/papel/aprobar` 409 y botón deshabilitado", "", f"POST `/papel/aprobar` con Wittenoom hoy: **{post[0]}** `{post[1]}`", "",
            f"Pestaña PAPEL en Chrome headless: botón «{boton_txt(txt)}» deshabilitado = **{disabled}** · {len(errores)} errores de página · aviso: «{aviso}» · captura `f67b/papel_bloqueado.png`.", "",
            "Comienzo de la pestaña:", "", "```", txt[:600], "```", ""]


def boton_txt(txt: str) -> str:
    return "Aprobar papel" if "Aprobar papel" in txt else "?"


def etapa3(f15, sd: Path, sd_real: Path) -> list[str]:
    import io
    from contextlib import redirect_stdout
    caps = f15.normalizado_desfasado(TID, sd_real)
    buf = io.StringIO()
    with redirect_stdout(buf):
        borrados = f15.descartar_normalizado(TID, sd)
    existe = (sd / TID / f15.NORMALIZADO).exists()
    import audio_manager as am
    ch1 = next(c for c in json.loads((sd / TID / "01b_narration.json").read_text(encoding="utf-8"))["chapters"] if c["chapter_number"] == 1)
    viejo = json.loads((D / f15.NORMALIZADO).read_text(encoding="utf-8"))["chapters"][0]["narration_normalized"]
    con_real = am._resolve_text_for_tts("ch01", ch1["narration"], TID)
    base_dd = am.DATA_DIR
    am.DATA_DIR = sd.parent / "data_vacio"
    sin = am._resolve_text_for_tts("ch01", ch1["narration"], TID)
    am.DATA_DIR = base_dd
    from script_engine import m02_5_normalizer_gate as g
    orig_steps = g.STEPS_DIR
    g.STEPS_DIR = sd
    g._persist_normalized_narration(TID, g._apply_spans_to_narration(json.loads((sd / TID / "01b_narration.json").read_text(encoding="utf-8")), [], []))
    g.STEPS_DIR = orig_steps
    tras_gate = f15.normalizado_desfasado(TID, sd)
    return ["## 3. Normalizado desfasado", "", f"Comprobación de solo lectura sobre Wittenoom: caps distintos {caps} ({len(caps)}). El archivo real sigue en disco: se borra al correr la voz.", "",
            "Sobre la copia, `descartar_normalizado` imprime:", "", "```", buf.getvalue().strip(), "```", "", f"Caps {borrados}; el archivo sigue: {existe}.", "",
            f"`audio_manager._resolve_text_for_tts`, hoy con el archivo real: lee el texto viejo = **{con_real == viejo}**. Sin el archivo: normalize_for_tts de la narración actual = **{sin == am.normalize_for_tts(ch1['narration'], language='es')}** (el `exists()` de `audio_manager.py:519`).", "",
            f"`normalizer_gate` lo regenera sobre la copia, sin LLM (`_apply_spans_to_narration` + `_persist_normalized_narration`, lo que corre siempre el gate): desfasado después = {tras_gate}.", ""]


def etapa4(f15, sd: Path) -> list[str]:
    import io
    from contextlib import redirect_stdout

    import claude_helpers as hx
    from script_engine import m01f_critico as mf
    from script_engine import narracion_verificador as nv
    ayuda = subprocess.run([sys.executable, "fase1_5.py", "--help"], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", env={**__import__("os").environ, "PYTHONIOENCODING": "utf-8"}).stdout
    i = ayuda.index("--criticar  ") if "--criticar  " in ayuda else ayuda.rindex("--criticar")
    bloque = re.split(r"\n  --", ayuda[i:])[0].rstrip()

    def explota(*a, **k):
        raise AssertionError("llamada real o verificador")
    hx._post = explota
    nv.verificar_caps = explota
    f15.run_verificacion = explota
    f15.run_pantalla = explota
    f15.STEPS_DIR = sd
    f15._step_cost = lambda tid, label, fn: fn()
    llamadas: list[str] = []
    resp = {"nota_total": 6.5, "resumen": ["seco"], "gancho": {}, "caps": [], "loops": [], "pico": {}, "cierre": "c", "deberia": [], "reglas_generales_candidatas": [], "riesgos": []}

    def post(body):
        llamadas.append(f"{body['model']} · system md5 {mf.md5(body['system'])}")
        return {"content": [{"type": "text", "text": json.dumps(resp)}], "usage": {"input_tokens": 1, "output_tokens": 1}, "stop_reason": "end_turn"}
    antes = (sd / TID / "01b_narracion_v3.json").read_bytes()
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = f15.criticar(TID, post=post)
    return ["## 4. `--criticar`", "", "`python fase1_5.py --help`:", "", "```", bloque, "```", "", f"Corrida en seco sobre una copia, con `post` falso; el POST real, `verificar_caps`, `run_verificacion` y `run_pantalla` explotan: exit {rc}, {len(llamadas)} llamada(s) al `post` falso: {llamadas}. La narración no cambió: {antes == (sd / TID / '01b_narracion_v3.json').read_bytes()}.", "",
            "```", "\n".join(x for x in buf.getvalue().strip().splitlines()), "```", ""]


def main() -> None:
    S.mkdir(exist_ok=True)
    import fase1_5 as f15
    import run_pipeline as rp
    steps_md5.foto("F67b_antes")
    real = f15.STEPS_DIR
    L = ["# F67b — salidas", ""] + etapa1(f15, rp)
    L += etapa2()
    with tempfile.TemporaryDirectory() as td:
        sd = copia(Path(td))
        L[L.index("## 2. `/papel/aprobar` 409 y botón deshabilitado"):L.index("## 2. `/papel/aprobar` 409 y botón deshabilitado")] = etapa1_copia(f15, rp, sd)
        L += etapa3(f15, sd, real)
        L += etapa4(f15, sd)
    steps_md5.foto("F67b_despues")
    L += ["## Topic real", "", f"Archivos de `_steps/<tid>/` que cambiaron: {steps_md5.compara('F67b_antes', 'F67b_despues') or 'ninguno'}", ""]
    (S / "SALIDAS.md").write_text("\n".join(L), encoding="utf-8", newline="\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
