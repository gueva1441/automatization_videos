# -*- coding: utf-8 -*-
"""
lab/hyperframes/f65/rutas_papel.py — F65b Etapa B, salida en texto: cada ruta del papel por HTTP, sobre una COPIA del papel actual del
topic en una carpeta temporal (el papel de producción no se toca: md5 antes y después). CERO llamadas: /papel/sugerir no se llama. La
aprobación y su invalidación se muestran solo en la copia. Escribe RUTAS_PAPEL.md.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
import tempfile
import threading
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

import fase1_5 as f15  # noqa: E402
import qa_studio_server as qa  # noqa: E402

TID = "123bbb64-9fca-4395-8bf4-57d60e219ef1"
REAL = ROOT / "data/scripts/_steps" / TID
AQUI = Path(__file__).resolve().parent
ARCHIVOS = ("01e_pantalla.json", "01e_pantalla.md", "01e_pantalla.raw.json")


def main() -> None:
    md5_real = {n: hashlib.md5((REAL / n).read_bytes()).hexdigest() for n in ARCHIVOS}
    tmp = Path(tempfile.mkdtemp(prefix="f65b_rutas_"))
    d = tmp / "data/scripts/_steps" / TID
    d.mkdir(parents=True)
    for n in ARCHIVOS:
        shutil.copy2(REAL / n, d / n)
    f15.STEPS_DIR = d.parent
    qa.STATE, qa.TOPIC_ID = qa.QAState(TID, tmp), TID
    http = ThreadingHTTPServer(("127.0.0.1", 0), qa.Handler)
    threading.Thread(target=http.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{http.server_address[1]}"

    def get(r: str) -> dict:
        with urllib.request.urlopen(url + r) as x:
            return json.loads(x.read())

    def post(r: str, b: dict) -> dict:
        req = urllib.request.Request(url + r, data=json.dumps(b).encode("utf-8"), method="POST")
        with urllib.request.urlopen(req) as x:
            return json.loads(x.read())
    L = ["# F65b Etapa B — RUTAS_PAPEL: cada ruta por HTTP (copia del papel actual, 0 llamadas)", "",
         f"Copia temporal de `{', '.join(ARCHIVOS)}`; md5 del papel `{md5_real['01e_pantalla.json']}`. Lo que se aprueba y se edita acá no llega a producción.", ""]
    v = get("/papel")
    L += ["## GET /papel", "", f"Cabecera: `estado` {json.dumps(v['estado'], ensure_ascii=False)} · md5 `{v['md5']}` · US$ {v['usd']} · {v['modelo']} · fichas {v['fichas']} · revisadas {v['revisadas']} · cierre {v['cierre']} · "
          f"sin_beat {len(v['sin_beat'])} · a_pantalla_vacios {len(v['a_pantalla_vacios'])} · aviso_narracion {len(v['aviso_narracion'])}", "",
          f"Descartes atribuidos a algún beat: {sum(len(b['descartes']) for b in v['beats'])} filas · sin beat: {[d['pool_id'] for d in v['sin_beat']]}", "", "El beat 1 entero:", "", "```json",
          json.dumps(v["beats"][0], ensure_ascii=False, indent=1), "```", ""]
    L += ["## POST /papel/revisar", "", f"`{{cap: ch01, beat: 1, on: true}}` → `{json.dumps(post('/papel/revisar', {'cap': 'ch01', 'beat': 1, 'on': True}), ensure_ascii=False)}`",
          f"- `01e_pantalla.revision.json`: `{(d / '01e_pantalla.revision.json').read_text(encoding='utf-8').strip()}`",
          f"- md5 del papel sin cambios: {get('/papel')['md5'] == v['md5']} · revisadas {get('/papel')['revisadas']}", ""]
    ficha = v["beats"][8]["ficha"]
    b9 = (v["beats"][8]["cap"], v["beats"][8]["beat"])
    ap = post("/papel/aprobar", {"por": "Prueba"})
    e0 = get("/papel")
    L += ["## POST /papel/aprobar (solo en la copia)", "", f"`{{por: Prueba}}` → `{json.dumps(ap, ensure_ascii=False)}`", f"- estado: `{json.dumps(e0['estado'], ensure_ascii=False)}`", ""]
    r = post("/papel/editar", {"cap": b9[0], "beat": b9[1], "ficha": None})
    e1 = get("/papel")
    L += ["## POST /papel/editar con null", "", f"`{{cap: {b9[0]}, beat: {b9[1]}, ficha: null}}` (quitaba {ficha['pool_id']}) → `{json.dumps(r)}`", f"- ficha ahora: {e1['beats'][8]['ficha']}",
          f"- estado antes: `{json.dumps(e0['estado'], ensure_ascii=False)}`", f"- estado después: `{json.dumps(e1['estado'], ensure_ascii=False)}`",
          f"- `01e_pantalla.antes_de_edicion.json` existe: {(d / '01e_pantalla.antes_de_edicion.json').exists()}", ""]
    bak = json.loads((d / "01e_pantalla.antes_de_edicion.json").read_text(encoding="utf-8"))
    original = next(b for b in bak["beats"] if (b["cap"], b["beat"]) == b9)["ficha"]
    r = post("/papel/editar", {"cap": b9[0], "beat": b9[1], "ficha": original})
    e2 = get("/papel")
    f2 = e2["beats"][8]["ficha"]
    L += ["## Vuelta atrás (la ficha desde `01e_pantalla.antes_de_edicion.json`)", "", f"→ `{json.dumps(r)}` · ficha {f2['pool_id']} «{f2['etiqueta']} · {f2['texto']}» · juicio_verificador conservado: "
          f"{f2.get('juicio_verificador') == original.get('juicio_verificador')} · editado: {f2.get('editado')}",
          f"- md5 vuelve al original: {e2['md5'] == e0['md5']} (`editar` deja `editado` y `ediciones`: el papel «restaurado» por la ruta tiene otro md5; para volver byte a byte, copiar el `antes_de_edicion`)",
          f"- estado: `{json.dumps(e2['estado'], ensure_ascii=False)}`", ""]
    L += ["## POST /papel/sugerir", "", "No se llama acá (0 llamadas): ya se midió en la Etapa A. Probada en `test_module_f65b::test_b4` con un `sugerir` falso: hilo, 409 si hay uno en curso, `GET /papel/sugerir_status`.", "",
          "## Producción intacta", ""]
    http.shutdown()
    for n in ARCHIVOS:
        h = hashlib.md5((REAL / n).read_bytes()).hexdigest()
        L.append(f"- {n}: `{h}` · igual: {h == md5_real[n]}")
    L.append(f"- `01e_pantalla.revision.json` en producción: {(REAL / '01e_pantalla.revision.json').exists()}")
    (AQUI / "RUTAS_PAPEL.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    shutil.rmtree(tmp, ignore_errors=True)
    print("\n".join(L))


if __name__ == "__main__":
    main()
