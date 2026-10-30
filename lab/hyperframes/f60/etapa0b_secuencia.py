# -*- coding: utf-8 -*-
"""F60 Etapa 0b — secuencia por la COLA de fal + madre con ropa limpia (solo lab; copia de etapa0_secuencia.py
con los 4 cambios del handoff HANDOFF_F60_0b_cola_y_madre_limpia.md y nada más).

1. Cola en vez de síncrono: submit a `api.fal_base_url` (queue.fal.run) con timeout 60 (como _call_clip_once),
   request_id/status_url/response_url/hora a `e0b/etapa0b_pedidos.json` ANTES de esperar; espera con
   `asset_manager._clip_poll` (importado, sin copiar). Sin pedidos duplicados: si el pedido ya está en el json, solo poll.
2. Orden y paralelo: madre sola; con la madre en disco, los 2 lotes a la vez (ThreadPoolExecutor, tope FLUX_MAX_WORKERS).
3. Madre nueva: `{canon_sin}, {ROPA_MADRE}.` en el prompt de la Etapa 0 (resto igual).
4. Salidas en `lab/hyperframes/f60/e0b/`; `e0/` no se toca.
Del código de producción solo se IMPORTA (asset_manager._clip_poll, _fal_headers, FLUX_MAX_WORKERS, config.api).
Errores (TimeoutError, ContentRejectedError, RuntimeError, submit no 2xx): sin reintento, texto literal y PARÁ.

USO: PYTHONIOENCODING=utf-8 python lab/hyperframes/f60/etapa0b_secuencia.py
"""
from __future__ import annotations

import base64
import hashlib
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from threading import Lock

import requests

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
F60 = Path(__file__).resolve().parent
BASE = F60 / "base"
E0 = F60 / "e0"                 # registro de la Etapa 0 (solo lectura: madre vieja y lote2 para la hoja)
E0B = F60 / "e0b"
TID = "123bbb64-9fca-4395-8bf4-57d60e219ef1"
PERSONA = "Daniel Écija"
FOTOS_POR_LLAMADA = 6           # constante del handoff (prueba de Omar en fal, max_images 6)
SUBMIT_TIMEOUT_S = 60           # el existente de _call_clip_once (asset_manager.py)
ROPA_MADRE = "wearing a plain, clean, light-coloured shirt"   # analista, OK de Omar 17:48

# tabla de verdad del analista: fotos flux con `persona` esperado = Daniel Écija (sin caps con clip), orden de guion.
# chapters[4].img[4] (1966, de espaldas, ~30): «Daniel Écija o ""» → entra, se declara.
ITEMS = [(1, 0), (1, 1), (1, 3), (1, 4), (2, 15), (3, 6), (3, 8), (3, 13), (4, 4)]

LOG: list[str] = []
_LOCK = Lock()
PEDIDOS_PATH = E0B / "etapa0b_pedidos.json"


def log(s: str) -> None:
    with _LOCK:
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


def fname(k: int, i: int) -> str:
    return f"ch{k + 1:02d}_img_{i + 1:02d}.png"


def _leer_pedidos() -> dict:
    return json.loads(PEDIDOS_PATH.read_text(encoding="utf-8")) if PEDIDOS_PATH.exists() else {}


def _guardar_pedido(nombre: str, ped: dict) -> None:
    with _LOCK:
        d = _leer_pedidos()
        d[nombre] = ped
        PEDIDOS_PATH.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")


def pedir_o_reanudar(nombre: str, model: str, payload: dict, payload_sin_uri: dict) -> tuple[dict, dict]:
    """Cambio 1: submit a la cola de fal (o reanudar un request_id ya guardado) → espera con _clip_poll.
    Devuelve (respuesta de fal, pedido) con `segundos` = submit → vuelta de _clip_poll (incluye cola y GET)."""
    import asset_manager as am
    from config import api
    ped = _leer_pedidos().get(nombre)
    if ped and ped.get("request_id"):
        log(f"[{nombre}] pedido ya existente request_id {ped['request_id']} ({ped['hora_submit']}): solo poll, NO se vuelve a pedir")
        ped["reanudado"] = True
        t0 = time.time()
        data = am._clip_poll(ped["status_url"], ped["response_url"])
        ped["segundos_poll_reanudado"] = round(time.time() - t0, 1)
        _guardar_pedido(nombre, ped)
        return data, ped
    t0 = time.time()
    resp = requests.post(f"{api.fal_base_url}/{model}", headers=am._fal_headers(), json=payload, timeout=SUBMIT_TIMEOUT_S)
    if not 200 <= resp.status_code < 300:
        raise RuntimeError(f"submit {nombre} HTTP {resp.status_code}: {resp.text[:900]}")
    sub = resp.json()
    ped = {"nombre": nombre, "model": model, "submit_url": f"{api.fal_base_url}/{model}",
           "request_id": sub.get("request_id"), "status_url": sub.get("status_url"), "response_url": sub.get("response_url"),
           "hora_submit": datetime.now().isoformat(timespec="seconds"), "submit_http": resp.status_code,
           "submit_trajo_images": "images" in sub, "payload_sin_uri": payload_sin_uri}
    _guardar_pedido(nombre, ped)   # en disco ANTES de esperar
    log(f"[{nombre}] submit HTTP {resp.status_code} · request_id {ped['request_id']} · status_url {ped['status_url']}")
    if "images" in sub:
        data = sub
    else:
        data = am._clip_poll(sub["status_url"], sub["response_url"])
    ped["segundos"] = round(time.time() - t0, 1)
    ped["hora_vuelta"] = datetime.now().isoformat(timespec="seconds")
    _guardar_pedido(nombre, ped)
    return data, ped


def main() -> int:
    import asset_manager as am
    from config import APIConfig, api
    from engine_profiles import select_profile
    from script_engine import m03_imagenes_v3 as v3img

    E0B.mkdir(exist_ok=True)
    key = APIConfig().fal_api_key
    prof = select_profile("seedream")
    model_t2i = prof.render.model_id
    model_edit = model_t2i.replace("text-to-image", "edit")
    image_size = prof.render.image_size
    aspecto = prof.aspect_ratio_text
    res: dict = {"tid": TID, "persona": PERSONA, "model_t2i": model_t2i, "model_edit": model_edit, "cola": api.fal_base_url,
                 "image_size": image_size, "aspecto": aspecto, "no_text": v3img.NO_TEXT,
                 "submit_timeout_s": SUBMIT_TIMEOUT_S, "poll_timeout_s": am.CLIP_POLL_TIMEOUT,
                 "flux_max_workers": am.FLUX_MAX_WORKERS, "fotos_por_llamada": FOTOS_POR_LLAMADA, "ropa_madre": ROPA_MADRE}
    log(f"cola {api.fal_base_url} · submit timeout {SUBMIT_TIMEOUT_S} s · poll CLIP_POLL_TIMEOUT {am.CLIP_POLL_TIMEOUT} s · FLUX_MAX_WORKERS {am.FLUX_MAX_WORKERS}")

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
    # appearance_canon sin ropa ni estados del cuerpo (recorte A MANO de la Etapa 0, se mantiene)
    canon_full = dp["appearance_canon"]
    canon_sin = "a young adult Spanish migrant miner"
    assert canon_full == "a young adult Spanish migrant miner in work clothes, one foot visibly bandaged", canon_full
    res["appearance_canon"] = canon_full
    res["appearance_canon_recortado"] = canon_sin
    estilo = v3img.ESTILO_C.format(anio=anio) if anio else v3img.ESTILO_C.replace(" taken in {anio}", "")
    # cambio 3: `{canon_sin}.` → `{canon_sin}, {ROPA_MADRE}.`; el resto de la línea no se toca
    prompt_madre = (f"Head-and-shoulders portrait of {canon_sin}, {ROPA_MADRE}. {grupos[pg]['appearance']} "
                    f"Neutral expression, facing the camera, plain mid-grey background, soft even light. {estilo} {v3img.NO_TEXT}")
    PROMPT_MADRE_ESPERADO = ("Head-and-shoulders portrait of a young adult Spanish migrant miner, wearing a plain, clean, "
                             "light-coloured shirt. Spanish people of Mediterranean European origin with olive to light skin, "
                             "dark brown to black hair and dark eyes. Neutral expression, facing the camera, plain mid-grey "
                             "background, soft even light. A grainy 35mm documentary photograph taken in 1962, with muted "
                             "colors and slight underexposure, in a dark-history realist style. No readable text, no signage, no labels.")
    res["prompt_madre"] = prompt_madre
    res["prompt_madre_igual_al_handoff"] = prompt_madre == PROMPT_MADRE_ESPERADO
    log(f"\nPROMPT MADRE (byte a byte contra el handoff: {'igual' if res['prompt_madre_igual_al_handoff'] else 'DIFERENTE'}):\n{prompt_madre}\n")

    # ── 1. madre t2i por la cola (sola) ──
    madre_path = E0B / "madre_daniel_ecija.png"
    payload_m = {"prompt": prompt_madre, "image_size": image_size, "num_images": 1, "enable_safety_checker": True}
    res["payload_madre"] = payload_m
    pedidos_previos = _leer_pedidos()
    if not (pedidos_previos.get("madre") or {}).get("request_id") and any(k.startswith("lote") for k in pedidos_previos):
        log("PARÁ: hay lotes pedidos en etapa0b_pedidos.json pero la madre no tiene request_id → re-pedir la madre invalida los lotes.")
        return 2
    try:
        data, ped = pedir_o_reanudar("madre", model_t2i, payload_m, payload_m)
    except Exception as e:  # noqa: BLE001 — texto literal y PARÁ
        res["madre"] = {"error": f"{type(e).__name__}: {e}"[:1500]}
        log(f"[madre] ERROR {res['madre']['error']}\nPARÁ")
        _volcar(res, items)
        return 1
    img = data["images"][0]
    if not madre_path.exists():
        madre_path.write_bytes(requests.get(img["url"], timeout=60).content)
    res["madre"] = {"path": str(madre_path.relative_to(ROOT)), "segundos": ped.get("segundos"), "seed": data.get("seed"),
                    "request_id": ped.get("request_id"), "width": img.get("width"), "height": img.get("height"),
                    "md5": md5(madre_path), "usd": up_t2i * 1, "nsfw": data.get("has_nsfw_concepts"), "url_fal": img.get("url")}
    log(f"[madre] {ped.get('segundos')} s · seed {data.get('seed')} · nsfw {data.get('has_nsfw_concepts')} · US$ {up_t2i} · {madre_path.relative_to(ROOT)}")

    # ── 2. lotes /edit en modo secuencia, los 2 a la vez (cambio 2) ──
    madre_uri = data_uri(madre_path)
    lotes = [items[j:j + FOTOS_POR_LLAMADA] for j in range(0, len(items), FOTOS_POR_LLAMADA)]
    quitar = (aspecto, v3img.NO_TEXT)
    trabajos = []
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
        L = {"n": n, "pedidas": N, "files": [it["file"] for it in lote], "prompt_secuencia": prompt_seq,
             "payload_sin_uri": payload, "fotos": []}
        trabajos.append((n, lote, dict(payload, image_urls=[madre_uri]), payload, L))
        log(f"[lote {n}] {N} fotos: {[it['file'] for it in lote]} · prompt {len(prompt_seq)} chars")

    def correr_lote(t):
        n, lote, real, payload, L = t
        try:
            data, ped = pedir_o_reanudar(f"lote{n}", model_edit, real, payload)
        except Exception as e:  # noqa: BLE001 — sin reintento, texto literal
            L["error"] = f"{type(e).__name__}: {e}"[:1500]
            L["request_id"] = (_leer_pedidos().get(f"lote{n}") or {}).get("request_id")
            log(f"[lote {n}] ERROR {L['error']} · request_id {L['request_id']}")
            return L
        imgs = data.get("images") or []
        L["devueltas"] = len(imgs)
        L["segundos"] = ped.get("segundos")
        L["segundos_por_foto"] = round(ped["segundos"] / len(imgs), 1) if ped.get("segundos") and imgs else None
        L["request_id"] = ped.get("request_id")
        L["seed"] = data.get("seed")
        L["nsfw"] = data.get("has_nsfw_concepts")
        L["usd"] = round(up_edit * len(imgs), 5)
        L["usd_por_imagen"] = up_edit
        ldir = E0B / f"lote{n}"
        ldir.mkdir(exist_ok=True)
        for j, im in enumerate(imgs):
            it = lote[j] if j < len(lote) else None
            out = ldir / (f"{j + 1:02d}_{it['file']}" if it else f"{j + 1:02d}_extra.png")
            if not out.exists():
                out.write_bytes(requests.get(im["url"], timeout=60).content)
            L["fotos"].append({"pos": j + 1, "esperada": it["file"] if it else None, "path": str(out.relative_to(ROOT)),
                               "width": im.get("width"), "height": im.get("height"), "md5": md5(out), "url_fal": im.get("url")})
        log(f"[lote {n}] devueltas {len(imgs)}/{L['pedidas']} · {L['segundos']} s ({L['segundos_por_foto']} s/foto) · seed {data.get('seed')} · nsfw {data.get('has_nsfw_concepts')} · US$ {L['usd']} ({up_edit} × {len(imgs)})")
        return L

    t_pared = time.time()
    with ThreadPoolExecutor(max_workers=min(len(trabajos), am.FLUX_MAX_WORKERS)) as ex:
        res["lotes"] = list(ex.map(correr_lote, trabajos))
    res["segundos_pared_lotes"] = round(time.time() - t_pared, 1)
    log(f"\ntiempo de pared de los {len(trabajos)} lotes en paralelo: {res['segundos_pared_lotes']} s")
    errores = [L for L in res["lotes"] if L.get("error")]

    # ── 3. hoja: madre nueva (+ madre Etapa 0) y por fila foto 0b | foto Etapa 0 del mismo slot (cambio 4: en e0b/) ──
    from PIL import Image, ImageDraw
    W, H = 640, 360
    filas = []
    for L in res["lotes"]:
        for f in L["fotos"]:
            if not f["esperada"]:
                continue
            vieja = E0 / f"lote{L['n']}" / f"{f['pos']:02d}_{f['esperada']}"
            f["etapa0_path"] = str(vieja.relative_to(ROOT)) if vieja.exists() else None
            filas.append((f"L{L['n']} #{f['pos']} {f['esperada']}", ROOT / f["path"], vieja if vieja.exists() else None))
    hoja = Image.new("RGB", (W * 2 + 30, H * (len(filas) + 1) + 20 * (len(filas) + 2)), (18, 18, 18))
    d = ImageDraw.Draw(hoja)
    y = 20
    hoja.paste(Image.open(madre_path).convert("RGB").resize((W, H)), (10, y))
    madre_e0 = E0 / "madre_daniel_ecija.png"
    if madre_e0.exists():
        hoja.paste(Image.open(madre_e0).convert("RGB").resize((W, H)), (W + 20, y))
    d.text((12, y + 2), f"MADRE 0b {PERSONA} · ropa limpia · seed {res['madre']['seed']}", fill=(255, 255, 0))
    d.text((W + 22, y + 2), "MADRE Etapa 0 (e0/)", fill=(255, 255, 0))
    y += H + 20
    for etiq, nueva, vieja in filas:
        hoja.paste(Image.open(nueva).convert("RGB").resize((W, H)), (10, y))
        if vieja:
            hoja.paste(Image.open(vieja).convert("RGB").resize((W, H)), (W + 20, y))
        else:
            d.text((W + 22, y + H // 2), "(sin foto de la Etapa 0: el lote 1 se cortó)", fill=(140, 140, 140))
        d.text((12, y + 2), etiq + " · 0b", fill=(255, 255, 0))
        d.text((W + 22, y + 2), etiq + " · Etapa 0", fill=(255, 255, 0))
        y += H + 20
    hoja_path = E0B / "hoja_madre_0b.jpg"
    hoja.save(hoja_path, quality=85)
    res["hoja"] = str(hoja_path.relative_to(ROOT))
    res["usd_total"] = round(res["madre"]["usd"] + sum(L.get("usd") or 0 for L in res["lotes"]), 5)
    log(f"\nTOTAL US$ {res['usd_total']} · hoja {hoja_path.relative_to(ROOT)}")
    if errores:
        log(f"PARÁ: {len(errores)} lote(s) con error (sin reintento); request_id en etapa0b_pedidos.json")
    _volcar(res, items)
    return 1 if errores else 0


def _volcar(res: dict, items: list) -> None:
    res["items"] = items
    res["log"] = LOG
    (E0B / "etapa0b.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    (E0B / "etapa0b.log").write_text("\n".join(LOG), encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
