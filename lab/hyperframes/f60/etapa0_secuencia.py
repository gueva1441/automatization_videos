# -*- coding: utf-8 -*-
"""F60 Etapa 0 — prueba de secuencia en lab (SIN tocar código de producción).

1. Madre de Daniel Écija: Seedream v5 Lite t2i (model_id del perfil, image_size del perfil), prompt B.1 armado a mano.
2. Fotos flux de Daniel de la tabla de verdad (sin caps con clip), orden de guion, lotes de 6 → UNA llamada /edit por
   lote con image_urls=[madre], max_images=len(lote), prompt de secuencia del handoff (en código, sin LLM).
3. Precio REAL por imagen: pricing de fal (GET api.fal.ai/v1/models/pricing), unit_price × imágenes devueltas.
4. Hoja: madre + por foto (nueva | t2i vieja del slot en la copia de lab).
Todo lee de la copia lab/hyperframes/f60/base/; escribe solo en lab/hyperframes/f60/e0/. Nada en data/ ni output/.

USO: PYTHONIOENCODING=utf-8 python lab/hyperframes/f60/etapa0_secuencia.py
"""
from __future__ import annotations

import base64
import hashlib
import json
import sys
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
F60 = Path(__file__).resolve().parent
BASE = F60 / "base"
E0 = F60 / "e0"
TID = "123bbb64-9fca-4395-8bf4-57d60e219ef1"
PERSONA = "Daniel Écija"
FOTOS_POR_LLAMADA = 6           # constante del handoff (prueba de Omar en fal, max_images 6)
TIMEOUT_S = 240                 # el existente de _generate_image_raw (asset_manager.py)

# tabla de verdad del analista: fotos flux con `persona` esperado = Daniel Écija (sin caps con clip), orden de guion.
# chapters[4].img[4] (1966, de espaldas, ~30): «Daniel Écija o ""» → entra, se declara.
ITEMS = [(1, 0), (1, 1), (1, 3), (1, 4), (2, 15), (3, 6), (3, 8), (3, 13), (4, 4)]

LOG: list[str] = []


def log(s: str) -> None:
    print(s, flush=True)
    LOG.append(s)


def md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


def data_uri(p: Path) -> str:
    from script_engine.video_prompt import tipo_imagen
    b = p.read_bytes()
    return f"data:{tipo_imagen(b)};base64,{base64.b64encode(b).decode('ascii')}"


def precio(eid: str, key: str) -> dict:
    r = requests.get("https://api.fal.ai/v1/models/pricing", params={"endpoint_id": eid},
                     headers={"Authorization": f"Key {key}"}, timeout=60)
    r.raise_for_status()
    return r.json()


def fal_post(url: str, payload: dict, headers: dict) -> tuple[dict, float]:
    t0 = time.time()
    resp = requests.post(url, headers=headers, json=payload, timeout=TIMEOUT_S)
    if resp.status_code >= 400:
        raise RuntimeError(f"HTTP {resp.status_code}: {resp.text[:900]}")
    return resp.json(), round(time.time() - t0, 1)


def fname(k: int, i: int) -> str:
    return f"ch{k + 1:02d}_img_{i + 1:02d}.png"


def main() -> int:
    from config import APIConfig
    from engine_profiles import select_profile
    from script_engine import m03_imagenes_v3 as v3img

    E0.mkdir(exist_ok=True)
    key = APIConfig().fal_api_key
    headers = {"Authorization": f"Key {key}", "Content-Type": "application/json"}
    prof = select_profile("seedream")
    model_t2i = prof.render.model_id
    model_edit = model_t2i.replace("text-to-image", "edit")
    image_size = prof.render.image_size
    aspecto = prof.aspect_ratio_text
    res: dict = {"tid": TID, "persona": PERSONA, "model_t2i": model_t2i, "model_edit": model_edit,
                 "image_size": image_size, "aspecto": aspecto, "no_text": v3img.NO_TEXT, "timeout_s": TIMEOUT_S,
                 "fotos_por_llamada": FOTOS_POR_LLAMADA}

    # ── precios reales (GET) ──
    res["precio_t2i"] = precio(model_t2i, key)
    res["precio_edit"] = precio(model_edit, key)
    up_t2i = res["precio_t2i"]["prices"][0]["unit_price"]
    up_edit = res["precio_edit"]["prices"][0]["unit_price"]
    log(f"precio fal: t2i {up_t2i} US$/{res['precio_t2i']['prices'][0]['unit']} · edit {up_edit} US$/{res['precio_edit']['prices'][0]['unit']}")

    # ── canon y 03_visual de la copia ──
    canon = json.loads((ROOT / "data/scripts/_steps" / TID / "05_visual_canon.json").read_text(encoding="utf-8"))
    visual = json.loads((BASE / "data/scripts/_steps" / TID / "03_visual.json").read_text(encoding="utf-8"))
    ch = visual["chapters"]
    dp = next(p for p in canon["documented_people"] if p["name"] == PERSONA)
    grupos = {g["id"]: g for g in canon["people_groups"]}
    items = []
    for k, i in ITEMS:
        it = ch[k]["image_prompts"][i]
        items.append({"k": k, "i": i, "cap": ch[k]["chapter_number"], "file": fname(k, i), "prompt": it["prompt"],
                      "year": it.get("year"), "people_group": it.get("people_group"), "shot_scale": it.get("shot_scale"),
                      "anchor": it.get("narration_anchor"), "text_present": (it.get("text_in_image") or {}).get("present")})
    # people_group más frecuente entre las fotos de Daniel; empate → el del primero en orden de guion
    cuenta: dict[str, int] = {}
    for it in items:
        for g in it["people_group"] or []:
            cuenta[g] = cuenta.get(g, 0) + 1
    pg = max(cuenta, key=lambda g: (cuenta[g], -[x["people_group"][0] for x in items if x["people_group"]].index(g)
                                    if g in [x["people_group"][0] for x in items if x["people_group"]] else 0))
    res["people_group_cuenta"] = cuenta
    res["people_group_madre"] = pg
    # año de la madre = primer número de 4 dígitos de `era`
    import re
    m = re.search(r"\d{4}", dp.get("era") or "")
    anio = m.group(0) if m else ""
    res["canon_daniel"] = dp
    res["anio_madre"] = anio
    # appearance_canon sin ropa ni estados del cuerpo (recorte A MANO para la Etapa 0, como pide el handoff)
    canon_full = dp["appearance_canon"]
    canon_sin = "a young adult Spanish migrant miner"
    assert canon_full == "a young adult Spanish migrant miner in work clothes, one foot visibly bandaged", canon_full
    res["appearance_canon"] = canon_full
    res["appearance_canon_recortado"] = canon_sin
    estilo = v3img.ESTILO_C.format(anio=anio) if anio else v3img.ESTILO_C.replace(" taken in {anio}", "")
    prompt_madre = (f"Head-and-shoulders portrait of {canon_sin}. {grupos[pg]['appearance']} "
                    f"Neutral expression, facing the camera, plain mid-grey background, soft even light. {estilo} {v3img.NO_TEXT}")
    res["prompt_madre"] = prompt_madre
    log(f"\nPROMPT MADRE:\n{prompt_madre}\n")

    # ── 1. madre t2i ──
    madre_path = E0 / "madre_daniel_ecija.png"
    payload_m = {"prompt": prompt_madre, "image_size": image_size, "num_images": 1, "enable_safety_checker": True}
    res["payload_madre"] = payload_m
    data, seg = fal_post(f"{prof.render.base_url}/{model_t2i}", payload_m, headers)
    img = data["images"][0]
    madre_path.write_bytes(requests.get(img["url"], timeout=60).content)
    res["madre"] = {"path": str(madre_path.relative_to(ROOT)), "segundos": seg, "seed": data.get("seed"),
                    "width": img.get("width"), "height": img.get("height"), "md5": md5(madre_path),
                    "usd": up_t2i * 1, "nsfw": data.get("has_nsfw_concepts")}
    log(f"[madre] {seg} s · seed {data.get('seed')} · {img.get('width')}x{img.get('height')} · US$ {up_t2i}")

    # ── 2. lotes /edit en modo secuencia ──
    madre_uri = data_uri(madre_path)
    lotes = [items[j:j + FOTOS_POR_LLAMADA] for j in range(0, len(items), FOTOS_POR_LLAMADA)]
    res["lotes"] = []
    quitar = (aspecto, v3img.NO_TEXT)
    for n, lote in enumerate(lotes, 1):
        N = len(lote)
        lineas = []
        for j, it in enumerate(lote, 1):
            p = it["prompt"]
            for q in quitar:
                p = p.replace(" " + q, "").replace(q, "")
            it["prompt_escena"] = p.strip()
            lineas.append(f"Image {j}: {it['prompt_escena']}")
        prompt_seq = (f"A series of {N} separate photographs of the same man shown in the reference image. "
                      f"Each image is a different scene:\n" + "\n".join(lineas) +
                      f"\nEvery image: {aspecto} {v3img.NO_TEXT}")
        payload = {"prompt": prompt_seq, "image_urls": ["<data-uri madre>"], "image_size": image_size, "num_images": 1,
                   "max_images": N, "sequential_image_generation": "auto", "enable_safety_checker": True}
        log(f"\n[lote {n}] {N} fotos: {[it['file'] for it in lote]} · prompt {len(prompt_seq)} chars")
        real = dict(payload, image_urls=[madre_uri])
        L = {"n": n, "pedidas": N, "files": [it["file"] for it in lote], "prompt_secuencia": prompt_seq,
             "payload_sin_uri": payload, "fotos": []}
        try:
            data, seg = fal_post(f"{prof.render.base_url}/{model_edit}", real, headers)
        except Exception as e:  # noqa: BLE001 — se reporta tal cual
            L["error"] = f"{type(e).__name__}: {e}"[:1200]
            L["segundos"] = None
            log(f"[lote {n}] ERROR {L['error']}")
            res["lotes"].append(L)
            continue
        imgs = data.get("images") or []
        L["devueltas"] = len(imgs)
        L["segundos"] = seg
        L["seed"] = data.get("seed")
        L["nsfw"] = data.get("has_nsfw_concepts")
        L["usd"] = round(up_edit * len(imgs), 5)
        L["usd_por_imagen"] = up_edit
        ldir = E0 / f"lote{n}"
        ldir.mkdir(exist_ok=True)
        for j, im in enumerate(imgs):
            it = lote[j] if j < len(lote) else None
            out = ldir / (f"{j + 1:02d}_{it['file']}" if it else f"{j + 1:02d}_extra.png")
            out.write_bytes(requests.get(im["url"], timeout=60).content)
            L["fotos"].append({"pos": j + 1, "esperada": it["file"] if it else None, "path": str(out.relative_to(ROOT)),
                               "width": im.get("width"), "height": im.get("height"), "md5": md5(out)})
        log(f"[lote {n}] devueltas {len(imgs)}/{N} · {seg} s · seed {data.get('seed')} · US$ {L['usd']} ({up_edit} × {len(imgs)})")
        res["lotes"].append(L)

    # ── 3. hoja: madre + (nueva | vieja) por foto ──
    from PIL import Image, ImageDraw
    assets = BASE / "output" / TID / "assets"
    W, H = 640, 360
    filas = []
    for L in res["lotes"]:
        for f in L["fotos"]:
            if not f["esperada"]:
                continue
            cap = f["esperada"][:4]
            vieja = assets / f"{cap}_flux" / f["esperada"]
            f["vieja_path"] = str(vieja.relative_to(ROOT)) if vieja.exists() else None
            filas.append((f"L{L['n']} #{f['pos']} {f['esperada']}", ROOT / f["path"], vieja if vieja.exists() else None))
    hoja = Image.new("RGB", (W * 2 + 30, H * (len(filas) + 1) + 20 * (len(filas) + 2)), (18, 18, 18))
    d = ImageDraw.Draw(hoja)
    y = 20
    mimg = Image.open(madre_path).convert("RGB").resize((W, H))
    hoja.paste(mimg, (10, y))
    d.text((W + 30, y + 10), f"MADRE {PERSONA} · Seedream v5 Lite t2i · seed {res['madre']['seed']}", fill=(230, 230, 230))
    d.text((W + 30, y + 30), "columna izquierda: /edit secuencia con la madre · derecha: PNG t2i viejo del slot (copia de lab)",
           fill=(200, 200, 200))
    y += H + 20
    for etiq, nueva, vieja in filas:
        hoja.paste(Image.open(nueva).convert("RGB").resize((W, H)), (10, y))
        if vieja:
            hoja.paste(Image.open(vieja).convert("RGB").resize((W, H)), (W + 20, y))
        d.text((12, y + 2), etiq + " · NUEVA", fill=(255, 255, 0))
        d.text((W + 22, y + 2), etiq + " · VIEJA t2i", fill=(255, 255, 0))
        y += H + 20
    hoja_path = F60 / "hoja_madre_secuencia.jpg"
    hoja.save(hoja_path, quality=85)
    res["hoja"] = str(hoja_path.relative_to(ROOT))
    # hoja de caras: madre + crop central de cada nueva, para mirar la cara
    res["usd_total"] = round(res["madre"]["usd"] + sum(L.get("usd") or 0 for L in res["lotes"]), 5)
    res["items"] = items
    res["log"] = LOG
    (F60 / "etapa0.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    (F60 / "etapa0.log").write_text("\n".join(LOG), encoding="utf-8")
    log(f"\nTOTAL US$ {res['usd_total']} · hoja {hoja_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
