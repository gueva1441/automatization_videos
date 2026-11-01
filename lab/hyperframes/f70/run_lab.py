"""LAB F70 — fotos sin texto pedido y cola de época sin «taken in». Solo escribe en esta carpeta; de output/ solo lee.

    python lab/hyperframes/f70/run_lab.py ensayo   # sin gastar: textos nuevos, diffs y madres resueltas
    python lab/hyperframes/f70/run_lab.py correr   # las 13 fotos en paralelo; retoma y no repite las que ya están
    python lab/hyperframes/f70/run_lab.py hojas    # <foto>_hoja.jpg vieja | nueva

El envío es `asset_manager._generar_nb2`, sin cambios (cola, tolerancia, 16:9, respaldo y bajada de producción), con `frase_de_madres=False`
porque el texto de la `.llamada.json` ya trae esa frase. Las madres son las mismas de producción: se buscan en `foto_madre/` por el
`referencias_md5` que quedó en cada `.llamada.json`; si alguna no aparece, no se gasta nada.

Constantes (origen):
    FOTOS          HANDOFF_F70_lab.md, tabla de constantes
    A, B           HANDOFF_F70_lab.md; A = la oración que arma `frase_cartel`, en cualquiera de sus formas (m03_imagenes_v3.py:590)
    workers        una por foto: todas en paralelo (regla de Omar)
"""
from __future__ import annotations

import concurrent.futures as cf
import difflib
import hashlib
import json
import re
import sys
from pathlib import Path

from PIL import Image, ImageDraw

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[2]
sys.path[:0] = [str(RAIZ), str(RAIZ / "lab" / "_nb_tol6")]

import asset_manager as am  # noqa: E402
from cost_tracker import cost_tracker  # noqa: E402
import run_lab as tol6  # noqa: E402  (lab/_nb_tol6/run_lab.py, por la fuente de las hojas)

TOPIC = "123bbb64-9fca-4395-8bf4-57d60e219ef1"
BASE = am.OUTPUT_DIR / TOPIC
ERROR = ("ch03_img_08", "ch03_img_15", "ch05_img_03", "ch06_img_11", "ch02_img_04", "ch07_supp_04", "ch06_img_07")
CONTROL = ("ch02_img_05", "ch03_img_12", "ch04_img_09", "ch05_img_12", "ch06_img_04", "ch07_supp_02")
FOTOS = ERROR + CONTROL
RESULTADOS = AQUI / "resultados.json"

FRASE_A = re.compile(r'(?:(?<=\. )|^)[^."]*"[^"]*"[^."]*\bin clear crisp\b[^.]*\blettering\. ')
COLA_B = re.compile(r"\btaken in (\d{4})\b")


def transformar(texto: str) -> tuple[str, str | None, int]:
    """Aplica A y B al texto enviado. Devuelve (texto nuevo, frase A quitada o None, cambios de la cola)."""
    m = FRASE_A.search(texto)
    frase = m.group(0).strip() if m else None
    nuevo = FRASE_A.sub("", texto, count=1)
    return COLA_B.subn(r"in the style of \1", nuevo)[0], frase, len(COLA_B.findall(nuevo))


def _registro(foto: str) -> dict:
    f = BASE / "assets" / f"{foto[:4]}_flux" / f"{foto}.llamada.json"
    return json.loads(f.read_text(encoding="utf-8"))["llamadas"]["nb2_lite"]


def _madres() -> dict[str, tuple[Path, str]]:
    """{md5 del data URI: (archivo, data URI)} de todas las fotos madre del tema."""
    salida = {}
    for p in sorted((BASE / "foto_madre").rglob("*.png")):
        uri = am._path_to_data_uri(p)
        salida[hashlib.md5(uri.encode("utf-8")).hexdigest()] = (p, uri)
    return salida


def _plan() -> list[dict]:
    madres = _madres()
    plan = []
    for foto in FOTOS:
        r = _registro(foto)
        nuevo, frase, cola = transformar(r["texto"])
        faltan = [h for h in r["referencias_md5"] if h not in madres]
        if faltan or cola != 1:
            sys.exit(f"{foto}: madres sin encontrar {faltan} o cola cambiada {cola} veces; no se gasta nada")
        plan.append({"foto": foto, "grupo": "error" if foto in ERROR else "control", "viejo": r["texto"], "nuevo": nuevo, "frase_a": frase,
                     "cola_cambio": cola == 1, "cierre_no_text": "No readable text, no signage, no labels." in nuevo,
                     "madres": [madres[h][0].name for h in r["referencias_md5"]], "uris": [madres[h][1] for h in r["referencias_md5"]]})
    return plan


def _escribir_diffs(plan: list[dict]) -> None:
    for p in plan:
        partir = lambda t: re.sub(r"(?<=\.) ", "\n", t).splitlines()  # noqa: E731
        (AQUI / f"{p['foto']}.diff.txt").write_text(
            "\n".join(difflib.unified_diff(partir(p["viejo"]), partir(p["nuevo"]), "viejo", "nuevo", lineterm="", n=0)) + "\n", encoding="utf-8")


def ensayo() -> None:
    plan = _plan()
    _escribir_diffs(plan)
    for p in plan:
        print(p["foto"], "| A:", p["frase_a"], "| cola:", p["cola_cambio"], "| cierre:", p["cierre_no_text"], "| madres:", p["madres"])


def _una(p: dict) -> dict:
    png = AQUI / f"{p['foto']}.png"
    fila = {k: p[k] for k in ("foto", "grupo", "frase_a", "cola_cambio", "cierre_no_text", "madres")}
    if png.exists():
        return {**fila, "reusada": True}
    try:
        meta = am._generar_nb2(p["nuevo"], png, None, p["uris"], False)
        print(f"  {p['foto']}: {meta['motor']} {meta['segundos']} s", flush=True)
        return {**fila, **{k: meta[k] for k in ("endpoint", "motor", "respaldo_motivo", "segundos", "usd", "width", "height")}}
    except Exception as e:  # noqa: BLE001 — una foto que falla no tumba a las otras; se reintenta volviendo a correr
        print(f"  {p['foto']}: ERROR {e}"[:300], flush=True)
        return {**fila, "error": f"{type(e).__name__}: {e}"[:600]}


def correr() -> None:
    plan = _plan()
    _escribir_diffs(plan)
    cost_tracker.start_video(video_id="lab_f70")
    with cf.ThreadPoolExecutor(max_workers=len(plan)) as ex:
        filas = list(ex.map(_una, plan))
    previas = json.loads(RESULTADOS.read_text(encoding="utf-8")) if RESULTADOS.exists() else {}
    for f in filas:
        if not f.get("reusada"):
            previas[f["foto"]] = f
    RESULTADOS.write_text(json.dumps(previas, ensure_ascii=False, indent=1), encoding="utf-8")
    print("fotos:", sum(1 for f in previas.values() if not f.get("error")), "errores:", [k for k, f in previas.items() if f.get("error")],
          "US$ estimado:", round(sum(f.get("usd") or 0 for f in previas.values()), 3))


def hojas() -> None:
    ancho, alto, cab = 960, 540, 44
    for foto in FOTOS:
        hoja = Image.new("RGB", (ancho * 2, alto + cab), (20, 20, 20))
        d = ImageDraw.Draw(hoja)
        for i, (rotulo, f) in enumerate((("VIEJA", BASE / "assets" / f"{foto[:4]}_flux" / f"{foto}.png"), ("NUEVA", AQUI / f"{foto}.png"))):
            d.text((i * ancho + 10, 8), f"{foto} · {rotulo}", fill=(255, 255, 255), font=tol6._fuente(24))
            img = Image.open(f).convert("RGB")
            img.thumbnail((ancho, alto), Image.LANCZOS)
            hoja.paste(img, (i * ancho, cab))
        hoja.save(AQUI / f"{foto}_hoja.jpg", quality=92)
    print("hojas:", len(FOTOS))


if __name__ == "__main__":
    orden = {"ensayo": ensayo, "correr": correr, "hojas": hojas}.get(sys.argv[1] if len(sys.argv) > 1 else "")
    if orden is None:
        sys.exit(__doc__)
    orden()
