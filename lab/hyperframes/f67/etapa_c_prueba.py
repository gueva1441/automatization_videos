# -*- coding: utf-8 -*-
"""F67 C.4 (0 llamadas al modelo): (1) `run_pipeline --topic <tid> --batch` sobre Wittenoom para en «narracion» sin tocar un archivo
del topic; (2) QA Studio en Chrome headless, pestaña NARRACIÓN capturada a texto, sobre el topic real y sin tocar botones; (3) la
prueba de aceptar + editar + aprobar + invalidación SOBRE UNA COPIA de _steps/<tid>/ en lab/hyperframes/f67/c/. Salida: c/SALIDA_C.md."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import threading
import time
from http.server import ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(AQUI))

import steps_md5  # noqa: E402

TID, D, C = steps_md5.TID, steps_md5.STEPS, AQUI / "c"


def correr_pipeline() -> str:
    p = subprocess.run([sys.executable, "run_pipeline.py", "--topic", TID, "--batch"], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace",
                       env={**__import__("os").environ, "PYTHONIOENCODING": "utf-8"})
    return f"exit {p.returncode}\n" + "\n".join(x for x in p.stdout.splitlines() if "viral_pipeline" not in x)


def chrome() -> tuple[dict, str, list[str]]:
    """GET /narracion y la pestaña, sobre el topic real, sin tocar ningún botón de acción."""
    import qa_studio_server as qa
    from playwright.sync_api import sync_playwright
    qa.STATE, qa.TOPIC_ID = qa.QAState(TID, ROOT), TID
    assert qa._preflight(qa.STATE) == []
    http = ThreadingHTTPServer(("127.0.0.1", 0), qa.Handler)
    threading.Thread(target=http.serve_forever, daemon=True).start()
    errores: list[str] = []
    with sync_playwright() as pw:
        br = pw.chromium.launch(channel="chrome", headless=True)
        pg = br.new_page(viewport={"width": 1400, "height": 1000})
        pg.on("pageerror", lambda e: errores.append(str(e)))
        pg.goto(f"http://127.0.0.1:{http.server_address[1]}/", wait_until="domcontentloaded")
        pg.wait_for_selector("#narrBtn")
        pg.wait_for_timeout(800)
        pg.click("#narrBtn")
        pg.wait_for_selector(".nn-par", timeout=20000)
        pg.wait_for_timeout(300)
        txt = pg.locator("#view").inner_text()
        v = pg.evaluate("async()=>await (await fetch('/narracion')).json()")
        pg.screenshot(path=str(C / "narracion_qa.png"))
        pg.locator(".nn-deb").first.scroll_into_view_if_needed()
        pg.screenshot(path=str(C / "narracion_qa_deberia.png"))
        br.close()
    http.shutdown()
    return v, txt, errores


def caps_de(steps: Path, cap: int) -> list[dict]:
    n3 = json.loads((steps / TID / "01b_narracion_v3.json").read_text(encoding="utf-8"))
    return [{"i": i, "beat": p["beat"], "texto": p["texto"]} for i, p in enumerate(n3["parrafos"]) if int(p["cap"]) == cap]


def prueba_en_copia() -> list[str]:
    """La narración de Wittenoom la toca Omar: esto corre sobre c/<tid>/."""
    import fase1_5 as f15
    from script_engine import m01d_particion as md
    from script_engine import m01f_critico as mf
    cop = C / TID
    if cop.exists():
        shutil.rmtree(cop)
    C.mkdir(exist_ok=True)
    shutil.copytree(D, cop, ignore=shutil.ignore_patterns("_r3_cache", "fuentes", "_r1_cache.json", "fuentes_r1.json", "fuentes.json"))
    L: list[str] = []
    def md5_n3():
        return md.md5_narracion(json.loads((cop / "01b_narracion_v3.json").read_text(encoding="utf-8")))
    def est():
        return f15.estado_narracion(TID, C)
    # reconstruir sin cambios: los 3 archivos idénticos
    antes = {n: (cop / n).read_bytes() for n in ("01a_skeleton.json", "01b_narration.json", "01b_narracion_v3.json")}
    c = mf._carga(TID, C)
    md.reconstruir(c["topic"], c["esc"], c["parrafos"], c["pool"], c["titulos"], steps_dir=C)
    iguales = {n: (cop / n).read_bytes() == b for n, b in antes.items()}
    L += ["### Reconstruir sin cambios", "", f"Los 3 archivos con los mismos bytes: {iguales}", ""]
    if not all(iguales.values()):
        L += ["Diferencias en texto (se comparan como JSON):", ""]
        for n, b in antes.items():
            L.append(f"- {n}: JSON igual = {json.loads(b) == json.loads((cop / n).read_bytes())}")
        L.append("")
    crit = mf.cargar_critica(TID, C)
    filas = crit["validacion"]["deberia"]
    pars = json.loads((cop / "01b_narracion_v3.json").read_text(encoding="utf-8"))["parrafos"]
    apl = {f["k"]: mf.aplica(f, pars) for f in filas}
    L += ["### Qué DEBERÍA aplican hoy", "", f"{apl}", ""]
    # aprobar
    m0 = md5_n3()
    ap = f15.aprobar_narracion(TID, "Prueba 2026-10-31", C)
    L += ["### Aprobar", "", f"`{ap}` · estado: {est()} · md5 sigue `{md5_n3() == m0}`", ""]
    # aceptar: el que más párrafos cruza entre los que aplican
    def cruza(f):
        ors = mf._oraciones_cap(pars, int(f["cap"][2:]))
        j = mf._ubicar(ors, f["texto_original"])
        return len({o["parrafo"] for o in ors[j:j + len(f["texto_original"])]}) if j is not None else 0
    f = max(filas, key=cruza)
    k, cap = f["k"], int(f["cap"][2:])
    a = caps_de(C, cap)
    r = mf.aceptar_deberia(TID, k, C)
    b = caps_de(C, cap)
    L += [f"### Aceptar DEBERÍA {k} ({f['cap']}, {len(f['texto_original'])} oraciones, cruza {cruza(f)} párrafos)", "",
          f"Respuesta: `{r}`", "", f"md5 cambió: `{m0[:8]}…` → `{md5_n3()[:8]}…` · estado: {est()}", "", "**Párrafos antes:**", ""]
    L += [f"- [{x['i']}] beat {x['beat']}: {x['texto']}" for x in a] + ["", "**Párrafos después:**", ""] + [f"- [{x['i']}] beat {x['beat']}: {x['texto']}" for x in b] + [""]
    try:
        mf.aceptar_deberia(TID, k, C)
        L.append("⚠ aceptar otra vez no dio error")
    except ValueError as e:
        L += [f"Aceptar otra vez → `{e}`", ""]
    # editar a mano y volver a aprobar e invalidar
    i = b[0]["i"]
    f15.aprobar_narracion(TID, "Prueba 2026-10-31", C)
    ok_antes = est()
    m1 = md5_n3()
    r = mf.editar_parrafo(TID, i, b[0]["texto"] + " Oración de prueba.", C)
    L += [f"### Editar el párrafo {i}", "", f"Antes: {ok_antes}", "", f"Respuesta: `{r}`", "", f"md5 cambió: `{m1[:8]}…` → `{md5_n3()[:8]}…` · la aprobación cayó: {est()}", ""]
    # el juez siguió vigente sobre la copia
    j = json.loads((cop / "06_judge_narrative.json").read_text(encoding="utf-8"))
    L += ["### Métricas vigentes en la copia", "", f"`retencion.total_palabras` {j['retencion']['total_palabras']} · pico {j['retencion']['pico']['cap']} {j['retencion']['pico']['pct_acumulado']} %", ""]
    return L


def main() -> None:
    C.mkdir(exist_ok=True)
    steps_md5.foto("C_antes")
    salida = correr_pipeline()
    steps_md5.foto("C_tras_pipeline")
    cambio1 = steps_md5.compara("C_antes", "C_tras_pipeline")
    v, txt, errores = chrome()
    steps_md5.foto("C_tras_chrome")
    cambio2 = steps_md5.compara("C_tras_pipeline", "C_tras_chrome")
    copia = prueba_en_copia()
    steps_md5.foto("C_despues")
    cambio3 = steps_md5.compara("C_tras_chrome", "C_despues")
    (C / "narracion_get.json").write_text(json.dumps(v, ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
    (C / "narracion_pestana.txt").write_text(txt, encoding="utf-8", newline="\n")
    nd = sum(len(c["deberia"]) for c in v["caps"])
    apl = sum(1 for c in v["caps"] for d in c["deberia"] if d["aplica"])
    L = ["# F67 Etapa C — la compuerta de narración", "", "## 1. La PARADA (`run_pipeline --topic <tid> --batch`)", "", "```", salida, "```", "",
         f"Archivos del topic que cambiaron: {cambio1 or 'ninguno'}", "", "## 2. GET /narracion, resumido (topic real)", "",
         f"- estado: {v['estado']}", f"- nota: {(v['critico'] or {}).get('nota_total')} · crítico vigente: {(v['critico'] or {}).get('vigente')} · sin_critico: {v['sin_critico']}",
         f"- {len(v['caps'])} caps · {nd} DEBERÍA · {apl} con `aplica`", f"- verificación: {len(v['verificacion']['quedan'])} «contradice», vigente {v['verificacion']['vigente']}",
         f"- pico: {v['metricas']['pico']['cap']} {v['metricas']['pico']['pct_acumulado']} %, {v['metricas']['pico']['segundos_despues']} s después", "",
         f"Chrome headless: {len(errores)} errores de página {errores or ''} · texto entero en `c/narracion_pestana.txt`, JSON en `c/narracion_get.json`, capturas `c/narracion_qa.png` y `c/narracion_qa_deberia.png`.",
         f"Archivos del topic que cambiaron al abrir la pestaña: {cambio2 or 'ninguno'}", "", "Comienzo de la pestaña:", "", "```", txt[:1500], "```", "",
         "## 3. Prueba sobre la copia (`lab/hyperframes/f67/c/<tid>/`)", ""] + copia + [f"Archivos del topic REAL que cambiaron durante la prueba: {cambio3 or 'ninguno'}", ""]
    (C / "SALIDA_C.md").write_text("\n".join(L), encoding="utf-8", newline="\n")
    print("\n".join(L))
    assert not cambio1 and not cambio2 and not cambio3 and not errores


if __name__ == "__main__":
    main()
