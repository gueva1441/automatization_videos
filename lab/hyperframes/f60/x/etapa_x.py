# -*- coding: utf-8 -*-
"""F60 Etapa X — regenerar 3 fotos de la Etapa 0b con el anacronismo corregido en el prompt (solo lab).
3 llamadas /edit sueltas (num_images 1, sin max_images/secuencia), image_urls=[madre 0b], mismo image_size.
Pedidos a x/pedidos_x.json ANTES de esperar. Sin reintentos: error → texto literal y PARÁ.
USO: PYTHONIOENCODING=utf-8 python lab/hyperframes/f60/x/etapa_x.py
"""
from __future__ import annotations
import base64, hashlib, json, sys, time
from datetime import datetime
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
F60 = Path(__file__).resolve().parents[1]
E0B = F60 / "e0b"
X = F60 / "x"
PEDIDOS = X / "pedidos_x.json"
SUBMIT_TIMEOUT_S = 60

# id 0b → (frase ANTES, frase DESPUÉS, modo). modo "sub" = sustituir; "add" = agregar DESPUÉS de la frase ANTES.
CAMBIOS = {
    "ch03_img_16": ("Stepping down from a small propeller aircraft onto the airstrip.",
                    "Stepping down from a twin-engine Douglas DC-3 propeller airliner, tail wheel resting on the strip, onto the airstrip.",
                    "sub"),
    "ch02_img_05": ("the women in modest cotton dresses.",
                    "the women in modest cotton dresses. One of the men wears a small round early-1960s steel wristwatch with a plain pale dial on a thin brown leather strap.",
                    "sub"),
    "ch05_img_05": ("entering their home.",
                    "entering their home. Beside the doorway only a small brass letter slot set into the wooden street door and a round brass bell push, as in 1960s Madrid; no electronic intercom panel, no camera and no metal mailbox on the facade.",
                    "sub"),
}
PATH_0B = {"ch03_img_16": "e0b/lote1/05_ch03_img_16.png", "ch02_img_05": "e0b/lote1/04_ch02_img_05.png",
           "ch05_img_05": "e0b/lote2/03_ch05_img_05.png"}

def md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()

def data_uri(p: Path) -> str:
    from script_engine.video_prompt import tipo_imagen
    b = p.read_bytes()
    return f"data:{tipo_imagen(b)};base64,{base64.b64encode(b).decode('ascii')}"

def _leer() -> dict:
    return json.loads(PEDIDOS.read_text(encoding="utf-8")) if PEDIDOS.exists() else {}

def _guardar(nombre: str, ped: dict) -> None:
    d = _leer(); d[nombre] = ped
    PEDIDOS.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")

def main() -> int:
    import asset_manager as am
    from config import api
    poll = getattr(am, "_fal_queue_poll", None) or am._clip_poll
    e0b = json.loads((E0B / "etapa0b.json").read_text(encoding="utf-8"))
    model = e0b["model_edit"]; image_size = e0b["image_size"]
    up = e0b["precio_edit"]["prices"][0]["unit_price"]
    madre = E0B / "madre_daniel_ecija.png"
    madre_uri = data_uri(madre)
    items0b = {it["file"].replace(".png", ""): it for it in e0b["items"]}
    res = {"model_edit": model, "image_size": image_size, "madre": str(madre.relative_to(ROOT)), "madre_md5": md5(madre),
           "poll_func": poll.__name__, "usd_por_imagen": up, "semilla": "Seedream v5 Lite /edit no acepta `seed` de entrada: no se puede reusar la semilla de 0b",
           "fotos": []}
    for fid, (antes, despues, modo) in CAMBIOS.items():
        it = items0b[fid]
        p0 = it["prompt"]
        assert p0.count(antes) == 1, (fid, p0.count(antes))
        p1 = p0.replace(antes, despues)
        F = {"id": fid, "path_0b": str((F60 / PATH_0B[fid]).relative_to(ROOT)), "prompt_antes": p0, "prompt_despues": p1,
             "frase_antes": antes, "frase_despues": despues}
        payload = {"prompt": p1, "image_urls": ["<data-uri madre>"], "image_size": image_size, "num_images": 1, "enable_safety_checker": True}
        F["payload_sin_uri"] = payload
        real = dict(payload, image_urls=[madre_uri])
        ped = _leer().get(fid)
        t0 = time.time()
        try:
            if ped and ped.get("request_id"):
                print(f"[{fid}] pedido existente {ped['request_id']}: solo poll"); ped["reanudado"] = True
                data = poll(ped["status_url"], ped["response_url"])
            else:
                r = requests.post(f"{api.fal_base_url}/{model}", headers=am._fal_headers(), json=real, timeout=SUBMIT_TIMEOUT_S)
                if not 200 <= r.status_code < 300:
                    raise RuntimeError(f"submit {fid} HTTP {r.status_code}: {r.text[:900]}")
                sub = r.json()
                ped = {"nombre": fid, "model": model, "request_id": sub.get("request_id"), "status_url": sub.get("status_url"),
                       "response_url": sub.get("response_url"), "hora_submit": datetime.now().isoformat(timespec="seconds"),
                       "submit_http": r.status_code, "payload_sin_uri": payload}
                _guardar(fid, ped)
                print(f"[{fid}] submit HTTP {r.status_code} · request_id {ped['request_id']}")
                data = sub if "images" in sub else poll(sub["status_url"], sub["response_url"])
        except Exception as e:  # noqa: BLE001
            F["error"] = f"{type(e).__name__}: {e}"[:1500]
            print(f"[{fid}] ERROR {F['error']}\nPARÁ"); res["fotos"].append(F)
            _volcar(res); return 1
        F["segundos"] = round(time.time() - t0, 1); ped["segundos"] = F["segundos"]
        ped["hora_vuelta"] = datetime.now().isoformat(timespec="seconds"); _guardar(fid, ped)
        im = data["images"][0]
        out = X / f"x_{fid}.png"
        if not out.exists():
            out.write_bytes(requests.get(im["url"], timeout=60).content)
        F.update({"request_id": ped["request_id"], "path_x": str(out.relative_to(ROOT)), "md5": md5(out), "url_fal": im.get("url"),
                  "seed_devuelta": data.get("seed"), "nsfw": data.get("has_nsfw_concepts"), "usd": up})
        print(f"[{fid}] {F['segundos']} s · seed devuelta {data.get('seed')} · US$ {up} · {out.name}")
        res["fotos"].append(F)
    res["usd_total"] = round(up * len(res["fotos"]), 5)
    # hoja de contacto: fila = foto 0b | foto X
    from PIL import Image, ImageDraw
    W, H = 640, 360
    hoja = Image.new("RGB", (W * 2 + 30, (H + 20) * len(res["fotos"]) + 20), (18, 18, 18)); d = ImageDraw.Draw(hoja); y = 20
    for F in res["fotos"]:
        hoja.paste(Image.open(ROOT / F["path_0b"]).convert("RGB").resize((W, H)), (10, y))
        hoja.paste(Image.open(ROOT / F["path_x"]).convert("RGB").resize((W, H)), (W + 20, y))
        d.text((12, y + 2), f"{F['id']} · 0b", fill=(255, 255, 0)); d.text((W + 22, y + 2), f"{F['id']} · X", fill=(255, 255, 0))
        y += H + 20
    hoja.save(X / "hoja_x.jpg", quality=85); res["hoja"] = "lab/hyperframes/f60/x/hoja_x.jpg"
    print(f"TOTAL US$ {res['usd_total']}")
    _volcar(res); return 0

def _volcar(res: dict) -> None:
    (X / "etapa_x.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")

if __name__ == "__main__":
    sys.exit(main())
