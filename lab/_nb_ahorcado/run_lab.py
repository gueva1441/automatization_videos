"""LAB NB-AHORCADO — ¿cuántas veces pasa un ahorcado por Nano Banana 2 Lite y Nano Banana 2, a tolerancia 6?

    python lab/_nb_ahorcado/run_lab.py correr    # 21 llamadas en paralelo; retoma y no repite lo terminado
    python lab/_nb_ahorcado/run_lab.py reporte   # hoja_A1..A3.png y REPORTE.md

No toca producción: la cola y la lectura de rechazos son `_llamada_cola` y `_motivo_rechazo` de asset_manager, sin cambios;
el esquema, la fuente y la API de uso son los de lab/_nb_tol6/run_lab.py.

Constantes (origen):
    SAFETY_TOLERANCE "6"   Omar; el script frena si el OpenAPI vivo dice otro máximo
    ASPECT_RATIO "16:9"    pedido del lab
    num_images 1           pedido del lab
    corridas 3 / 3 / 1     pedido del lab
    PRECIO_NB2             api.fal.ai/v1/models/pricing y fal.ai/models/fal-ai/nano-banana-2/llms.txt, leídos el 2026-11-01
"""
from __future__ import annotations

import concurrent.futures as cf
import datetime
import hashlib
import io
import json
import sys
import threading
import time
from pathlib import Path

import requests
from PIL import Image, ImageDraw

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
sys.path[:0] = [str(RAIZ), str(RAIZ / "lab" / "_nb_tol6")]

import asset_manager as am  # noqa: E402
import run_lab as tol6  # noqa: E402  (lab/_nb_tol6/run_lab.py: este archivo corre como __main__)

PROMPTS_MD5 = "5bfd1e3cc633d62e4c9c742d896ee2ea"
PROMPTS = json.loads((AQUI / "PROMPTS.json").read_bytes())
RESULTADOS = AQUI / "resultados.json"
LLAMADAS = AQUI / "llamadas"
SAFETY_TOLERANCE = "6"
ASPECT_RATIO = "16:9"
LITE = "google/nano-banana-2-lite"
NB2 = "fal-ai/nano-banana-2"
PRECIO_NB2 = {"1K": 0.08, "2K": 0.12}    # lista: 0,08 por imagen; «2K ... 1.5 times the standard rate»
PRECIO_ORIGEN = ("api.fal.ai/v1/models/pricing (fal-ai/nano-banana-2: 0,08 por imagen) y fal.ai/models/fal-ai/nano-banana-2/llms.txt "
                 "(2K = 1,5 veces el precio base)")
# etiqueta, modelo, resolución que se manda (None: el lite no tiene el parámetro), resolución del nombre, corridas
GRUPOS = (("nb2_lite", LITE, None, "1K", 3), ("nb2", NB2, "1K", "1K", 3), ("nb2", NB2, "2K", "2K", 1))

_lock = threading.Lock()


def _cargar() -> dict:
    return json.loads(RESULTADOS.read_text(encoding="utf-8")) if RESULTADOS.exists() else {"llamadas": {}}


def _escribir(todo: dict) -> None:
    tmp = RESULTADOS.with_suffix(".tmp")
    tmp.write_text(json.dumps(todo, ensure_ascii=False, indent=1), encoding="utf-8")
    tmp.replace(RESULTADOS)


def _guardar(clave: str, fila: dict) -> None:
    with _lock:
        todo = _cargar()
        todo["llamadas"][clave] = fila
        _escribir(todo)


def _clave(etiqueta: str, res: str, pid: str, corrida: int) -> str:
    return f"{etiqueta}_{res}_{pid}_{corrida}"


def _costo(modelo: str, res: str, estado: str) -> tuple[float | None, str]:
    if modelo == LITE:
        return None, "por tokens, sin medir"
    if estado == "OK":
        return PRECIO_NB2[res], "precio de lista: " + PRECIO_ORIGEN
    return None, "sin imagen; se asume que no cobra, no verificado"


def _una(etiqueta: str, modelo: str, res_pedida: str | None, res: str, pid: str, corrida: int) -> None:
    clave = _clave(etiqueta, res, pid, corrida)
    with _lock:
        if _cargar()["llamadas"].get(clave, {}).get("estado") in ("OK", "BLOQUEADO"):
            return
    payload = {"prompt": PROMPTS[pid], "aspect_ratio": ASPECT_RATIO, "safety_tolerance": SAFETY_TOLERANCE, "num_images": 1}
    if res_pedida:
        payload["resolution"] = res_pedida
    png = AQUI / f"{clave}.png"
    registro = LLAMADAS / png.name
    t0 = time.time()
    fila = {"modelo": modelo, "resolucion_pedida": res_pedida or "no se manda: fija 1K según la ficha", "prompt_id": pid, "corrida": corrida,
            "request_id": None, "estado": None, "type": None, "msg": None, "segundos": None, "resolucion_devuelta": None}
    try:
        data = am._llamada_cola(etiqueta + "_" + res, modelo, payload, registro)
        if not data.get("images"):
            fila.update(estado="BLOQUEADO", msg="respuesta sin imágenes: " + json.dumps(data, ensure_ascii=False)[:600])
        else:
            crudo = requests.get(data["images"][0]["url"], timeout=120)
            crudo.raise_for_status()
            img = Image.open(io.BytesIO(crudo.content))
            img.convert("RGB").save(png)
            fila.update(estado="OK", resolucion_devuelta=f"{img.width}x{img.height}",
                        negra=max(hi for _, hi in img.convert("RGB").getextrema()) <= tol6.NEGRO_MAX,
                        respuesta_sin_imagen={k: v for k, v in data.items() if k != "images"})
    except Exception as e:  # noqa: BLE001 — un fallo de una llamada no tumba a las otras
        cuerpo = getattr(getattr(e, "response", None), "text", None) or str(e)
        motivo = am._motivo_rechazo(cuerpo)
        if motivo:
            m = json.loads(motivo)
            fila.update(estado="BLOQUEADO", type=m.get("type"), msg=m.get("msg"), categories=m.get("categories"))
        else:
            fila.update(estado="ERROR", type=type(e).__name__, msg=cuerpo[:600])
    fila["segundos"] = round(time.time() - t0, 1)
    f = registro.with_name(registro.stem + am.LLAMADA_SUFIJO)
    fila["request_id"] = (am._leer_llamadas(f).get("llamadas") or {}).get(etiqueta + "_" + res, {}).get("request_id")
    fila["costo_usd"], fila["costo_origen"] = _costo(modelo, res, fila["estado"])
    fila["precio_lista_usd"] = PRECIO_NB2[res] if modelo == NB2 else "por tokens, sin medir"
    _guardar(clave, fila)
    print(f"  {clave}: {fila['estado']} {fila['type'] or ''} ({fila['segundos']} s)", flush=True)


def correr() -> None:
    if hashlib.md5((AQUI / "PROMPTS.json").read_bytes()).hexdigest() != PROMPTS_MD5:
        sys.exit("PROMPTS.json no es el del pedido")
    vivo = {}
    for ep in (LITE, NB2):
        p = tol6._esquema(ep)
        tol = tol6._enum(p.get("safety_tolerance"))
        if tol[-1] != SAFETY_TOLERANCE:
            sys.exit(f"{ep}: el máximo de safety_tolerance ya no es 6: {tol}")
        vivo[ep] = {"safety_tolerance": tol, "resolution": tol6._enum(p.get("resolution")), "16:9": "16:9" in tol6._enum(p.get("aspect_ratio"))}
    LLAMADAS.mkdir(exist_ok=True)
    with _lock:
        todo = _cargar()
        todo.setdefault("desde", datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"))
        todo["openapi_vivo"] = {"fecha": datetime.date.today().isoformat(), **vivo}
        _escribir(todo)
    lista = [(e, m, rp, r, pid, c) for e, m, rp, r, n in GRUPOS for pid in PROMPTS for c in range(1, n + 1)]
    print(f"{len(lista)} llamadas", flush=True)
    with cf.ThreadPoolExecutor(max_workers=len(lista)) as ex:
        list(ex.map(lambda a: _una(*a), lista))
    with _lock:
        todo = _cargar()
        todo["hasta"] = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
        _escribir(todo)
    print({e: sum(1 for v in todo["llamadas"].values() if v["estado"] == e) for e in ("OK", "BLOQUEADO", "ERROR")})


def _hoja(pid: str, llamadas: dict) -> None:
    ancho, alto, cab = 640, 360, 40
    filas = len(GRUPOS)
    hoja = Image.new("RGB", (ancho * 3, (alto + cab) * filas), (20, 20, 20))
    d = ImageDraw.Draw(hoja)
    for y, (e, _, _, res, n) in enumerate(GRUPOS):
        for c in range(1, n + 1):
            clave = _clave(e, res, pid, c)
            estado = llamadas.get(clave, {}).get("estado", "SIN CORRER")
            x0, y0 = (c - 1) * ancho, y * (alto + cab)
            d.text((x0 + 10, y0 + 8), f"{e} · {res} · corrida {c} · {estado}", fill=(255, 255, 255), font=tol6._fuente(22))
            f = AQUI / f"{clave}.png"
            if estado == "OK" and f.exists():
                img = Image.open(f).convert("RGB")
                img.thumbnail((ancho, alto))
                hoja.paste(img, (x0 + (ancho - img.width) // 2, y0 + cab + (alto - img.height) // 2))
            else:
                d.text((x0 + 200, y0 + cab + alto // 2 - 15), estado, fill=(220, 80, 80), font=tol6._fuente(30))
    hoja.save(AQUI / f"hoja_{pid}.png")


def reporte() -> None:
    todo = _cargar()
    ll = todo["llamadas"]
    for pid in PROMPTS:
        _hoja(pid, ll)

    def pasan(e: str, res: str, pid: str, n: int) -> str:
        est = [ll.get(_clave(e, res, pid, c), {}).get("estado") for c in range(1, n + 1)]
        err = est.count("ERROR")
        return f"{est.count('OK')}/{n}" + (f" ({err} ERROR)" if err else "")

    tabla = "\n".join(f"| {e} {res} | " + " | ".join(pasan(e, res, pid, n) for pid in PROMPTS) + " |" for e, _, _, res, n in GRUPOS)
    costos = [v["costo_usd"] for v in ll.values() if v.get("costo_usd") is not None]
    lite_ok = sum(1 for v in ll.values() if v["modelo"] == LITE and v["estado"] == "OK")
    usos = {ep: tol6._costo_uso(ep, todo.get("desde", ""), todo.get("hasta", "")) for ep in (LITE, NB2)}
    bloqueos = [f"- **{k}** ({v['estado']}), request_id `{v['request_id']}`: type `{v.get('type')}` · msg `{v.get('msg')}`"
                + (f" · categories `{v['categories']}`" if v.get("categories") else "")
                for k, v in sorted(ll.items()) if v["estado"] != "OK"]
    res_dev = sorted({f"`{v['modelo']}` → {v['resolucion_devuelta']}" for v in ll.values() if v.get("resolucion_devuelta")})
    vivo = todo["openapi_vivo"]
    (AQUI / "REPORTE.md").write_text(
        "# LAB NB-AHORCADO — reporte\n\n"
        "<!--LECTURA-->\n\n"
        f"`PROMPTS.json` md5 {PROMPTS_MD5}, byte a byte. Text-to-image, sin referencia, {ASPECT_RATIO}, 1 imagen, `safety_tolerance` {SAFETY_TOLERANCE}. "
        f"OpenAPI vivo ({vivo['fecha']}): `{LITE}` {vivo[LITE]['safety_tolerance']} y `{NB2}` {vivo[NB2]['safety_tolerance']}: **6 sigue siendo el máximo**. "
        "Detalle por llamada: `resultados.json`; registro de cada pedido: `llamadas/`.\n\n"
        "## Modelo × prompt (pasaron)\n\n"
        "| Modelo y resolución | A1 horca en prisión | A2 minero en el galpón | A3 silueta en el árbol |\n|---|---|---|---|\n" + tabla + "\n\n"
        "Resolución devuelta: " + "; ".join(res_dev) + ".\n\n"
        "## Mensajes de bloqueo y error, exactos\n\n" + ("\n".join(bloqueos) or "Ninguno.") + "\n\n"
        "## Costo\n\n"
        f"**Total conocido: US$ {sum(costos):.2f}** ({len(costos)} fotos de nb2: las 12 llamadas de nb2 se bloquearon). No incluye las {lite_ok} fotos del lite, que no tienen número.\n\n"
        "| Modelo | Costo por foto | Origen |\n|---|---|---|\n"
        "| nb2_lite (1K fija) | por tokens, sin medir | fal.ai/models/google/nano-banana-2-lite/llms.txt; fal no devuelve tokens |\n"
        f"| nb2 1K | US$ {PRECIO_NB2['1K']:.2f} | lista: {PRECIO_ORIGEN} |\n"
        f"| nb2 2K | US$ {PRECIO_NB2['2K']:.2f} | lista: {PRECIO_ORIGEN} |\n\n"
        "API de uso de fal: " + "; ".join(f"`{ep}` → {u[1]}" + (f" US$ {u[0]:.4f}" if u[0] is not None else "") for ep, u in usos.items())
        + ". Se asume que una llamada bloqueada no cobra; no está verificado.\n\n"
        "## Hojas de contacto\n\n" + "\n".join(f"- `hoja_{p}.png`" for p in PROMPTS) + "\n",
        encoding="utf-8")
    print("escrito", AQUI / "REPORTE.md")


if __name__ == "__main__":
    orden = sys.argv[1] if len(sys.argv) > 1 else ""
    if orden == "correr":
        correr()
    elif orden == "reporte":
        reporte()
    else:
        sys.exit(__doc__)
