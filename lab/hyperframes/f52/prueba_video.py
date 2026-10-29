# -*- coding: utf-8 -*-
"""F52 etapa 3 — los 8 clips: 4 modelos (K, S, F, G) × 2 caps de Wittenoom, 1 toma, con los prompts de F52b
(`prompts_f52.json`, commit 80bd71a). Único cambio a los prompts (pedido de Omar): en cap01_K «His left foot is wrapped» →
«One foot is wrapped». La foto (`fotos/capNN.png`) va como data URI con su tipo real leído de los bytes (son JPEG con
extensión .png). Llamadas por la cola de fal (queue.fal.run), las 8 en paralelo. Guarda de tope ANTES de llamar: el peor
caso de los 8 (el mayor entre el precio leído de fal y la estimación del handoff) + lo ya gastado < tope; si no, PARADA.
El costo de cada clip = precio unitario leído de fal × unidades medidas con ffprobe (segundos; Seedance: tokens =
ancho·alto·fps·segundos/1024), anotado en `cost_tracker` (video_id `f52_lab_clips`). No toca producción.

Salida: `clips/capNN_<letra>.mp4`, `clips/resultado.json` (por clip: endpoint, campos enviados, request_id, espera, error
literal si rechazó, ffprobe, costo). La hoja ciega y la llave las arma `hoja_ciega.py`.

Uso: python lab/hyperframes/f52/prueba_video.py
"""
import base64
import json
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
F52 = Path(__file__).resolve().parent
CLIPS = F52 / "clips"
ENDPOINTS = {"K": "kling/v4/image-to-video", "S": "bytedance/seedance-2.5/image-to-video",
             "F": "blackforestlabs/flux-3-max/image-to-video", "G": "google/gemini-omni-flash/v1.1/image-to-video"}
# precio unitario leído de fal (SCHEMAS_F52.md) y estimación por clip del handoff F52 (§Constantes)
PRECIO = {"K": (0.157, "s"), "S": (0.0214, "1000 tokens"), "F": (0.02125, "s"), "G": (0.03, "s")}
ESTIMACION_HANDOFF = {"K": 1.88, "S": 3.79, "F": 0.58, "G": 1.20}
DUR = 8                                                  # m03_visual.VEO_CLIP_DURATION_SEC
CAMBIO_K1 = ("His left foot is wrapped", "One foot is wrapped")
ESPERA_MAX_S = 1800


def _key() -> str:
    from config import APIConfig
    return APIConfig().fal_api_key


def h() -> dict:
    return {"Authorization": f"Key {_key()}", "Content-Type": "application/json"}


def data_uri(n: int) -> tuple[str, str]:
    b = (F52 / "fotos" / f"cap{n:02d}.png").read_bytes()
    tipo = "image/jpeg" if b[:3] == b"\xff\xd8\xff" else "image/png" if b[:8] == b"\x89PNG\r\n\x1a\n" else None
    if tipo is None:
        raise SystemExit(f"cap{n:02d}.png no es ni JPEG ni PNG")
    return tipo, f"data:{tipo};base64,{base64.b64encode(b).decode('ascii')}"


def payload(k: str, prompt: str, foto: str) -> dict:
    if k == "K":
        return {"prompt": prompt, "start_image_url": foto, "duration": DUR, "resolution": "1080p"}
    if k == "S":
        return {"prompt": prompt, "image_url": foto, "duration": str(DUR), "resolution": "720p",
                "generate_audio": False}
    if k == "F":
        return {"prompt": prompt, "image_url": foto, "duration": DUR, "resolution": "1080p", "generate_audio": False}
    return {"prompt": prompt, "image_url": foto, "duration": DUR, "resolution": "1080p"}            # G


def _url_video(d) -> str | None:
    if isinstance(d, dict):
        v = d.get("video")
        if isinstance(v, dict) and v.get("url"):
            return v["url"]
        for x in d.values():
            u = _url_video(x)
            if u:
                return u
    if isinstance(d, list):
        for x in d:
            u = _url_video(x)
            if u:
                return u
    if isinstance(d, str) and d.startswith("http") and ".mp4" in d:
        return d
    return None


def ffprobe(p: Path) -> dict:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                          "stream=codec_type,codec_name,width,height,r_frame_rate,nb_frames:format=duration",
                          "-of", "json", str(p)], capture_output=True, text=True)
    d = json.loads(out.stdout or "{}")
    v = next((s for s in d.get("streams", []) if s.get("codec_type") == "video"), {})
    num, den = (v.get("r_frame_rate") or "0/1").split("/")
    return {"duracion_s": round(float((d.get("format") or {}).get("duration") or 0), 3), "ancho": v.get("width"),
            "alto": v.get("height"), "fps": round(float(num) / float(den or 1), 3), "codec": v.get("codec_name"),
            "cuadros": v.get("nb_frames"), "audio": any(s.get("codec_type") == "audio" for s in d.get("streams", []))}


def costo(k: str, f: dict) -> float:
    unit, _ = PRECIO[k]
    if k == "S":
        return round(unit * (f["ancho"] * f["alto"] * f["fps"] * f["duracion_s"] / 1024) / 1000, 4)
    return round(unit * f["duracion_s"], 4)


def correr(n: int, k: str, prompt: str, foto: str) -> dict:
    eid = ENDPOINTS[k]
    body = payload(k, prompt, foto)
    enviado = {c: (v if c not in ("image_url", "start_image_url") else f"data:{foto[5:foto.index(';')]};base64,…")
               for c, v in body.items() if c != "prompt"}
    r = {"clip": f"cap{n:02d}_{k}", "endpoint": eid, "campos": enviado, "prompt_palabras": len(prompt.split()),
         "inicio": datetime.now().isoformat(timespec="seconds")}
    t0 = time.time()
    try:
        s = requests.post(f"https://queue.fal.run/{eid}", headers=h(), json=body, timeout=120)
        if s.status_code >= 400:
            r.update(error=f"submit HTTP {s.status_code}: {s.text[:600]}", espera_s=round(time.time() - t0, 1))
            return r
        sj = s.json()
        r["request_id"] = sj.get("request_id")
        status_url, response_url = sj["status_url"], sj["response_url"]
        while True:
            st = requests.get(status_url, headers=h(), timeout=60)
            estado = (st.json() if st.ok else {}).get("status")
            if estado == "COMPLETED":
                break
            if time.time() - t0 > ESPERA_MAX_S:
                r.update(error=f"sin terminar en {ESPERA_MAX_S} s (último status {estado})")
                return r
            time.sleep(5)
        res = requests.get(response_url, headers=h(), timeout=120)
        r["espera_s"] = round(time.time() - t0, 1)
        if res.status_code >= 400:
            r["error"] = f"resultado HTTP {res.status_code}: {res.text[:800]}"
            return r
        rj = res.json()
        r["respuesta"] = {c: v for c, v in rj.items() if c != "video"}
        url = _url_video(rj)
        if not url:
            r["error"] = f"sin video en la respuesta: {json.dumps(rj)[:600]}"
            return r
        p = CLIPS / f"cap{n:02d}_{k}.mp4"
        p.write_bytes(requests.get(url, timeout=300).content)
        r["archivo"] = str(p.relative_to(F52))
        r["ffprobe"] = ffprobe(p)
        r["usd"] = costo(k, r["ffprobe"])
    except Exception as e:                                          # noqa: BLE001 — se reporta tal cual
        r["error"] = f"{type(e).__name__}: {e}"[:600]
        r.setdefault("espera_s", round(time.time() - t0, 1))
    return r


def gastado_desde_tope() -> tuple[float, float]:
    tope = json.loads((ROOT / "lab" / "TOPE_TANDA.json").read_text(encoding="utf-8"))
    raw = (ROOT / "data" / "cost_history.json").read_bytes()
    try:
        hist = json.loads(raw.decode("utf-8"))
    except UnicodeDecodeError:
        hist = json.loads(raw.decode("cp1252"))
    g = sum(float(v.get("total_cost") or 0) for v in hist if str(v.get("created_at")) >= tope["desde"])
    return round(g, 4), float(tope["usd"])


def main() -> int:
    if any(CLIPS.glob("*.mp4")):
        print("ya hay clips en f52/clips/: no se vuelve a llamar")
        return 1
    prompts = json.loads((F52 / "prompts_f52.json").read_text(encoding="utf-8"))["prompts"]
    k1 = prompts["cap01_K"]["prompt"]
    assert k1.count(CAMBIO_K1[0]) == 1, "cap01_K no tiene la frase a cambiar una sola vez"
    prompts["cap01_K"]["prompt"] = k1.replace(*CAMBIO_K1)

    gastado, tope = gastado_desde_tope()
    peor = sum(max(ESTIMACION_HANDOFF[k], PRECIO[k][0] * (DUR if k != "S" else 1280 * 720 * 24 * DUR / 1024 / 1000))
               for k in ENDPOINTS) * 2
    print(f"gastado {gastado} · peor caso de los 8 {peor:.2f} · tope {tope}")
    if gastado + peor >= tope:
        print("PARADA: el peor caso pasa el tope")
        return 1

    CLIPS.mkdir(exist_ok=True)
    fotos = {n: data_uri(n) for n in (1, 7)}
    trabajos = [(n, k) for n in (1, 7) for k in ENDPOINTS]
    with ThreadPoolExecutor(max_workers=len(trabajos)) as ex:
        futs = {(n, k): ex.submit(correr, n, k, prompts[f"cap{n:02d}_{k}"]["prompt"], fotos[n][1]) for n, k in trabajos}
        res = {f"cap{n:02d}_{k}": f.result() for (n, k), f in futs.items()}

    from cost_tracker import cost_tracker
    from error_handler import PipelineStage
    cost_tracker.start_video("f52_lab_clips")
    for c, r in res.items():
        if r.get("usd"):
            cost_tracker._add_entry(stage=PipelineStage.VIDEO.value, service=f"fal {r['endpoint']}",
                                    description=f"f52:clip:{c}", units=r["ffprobe"]["duracion_s"], unit_label="s",
                                    cost_per_unit=0.0, total_cost=r["usd"])
    rep = cost_tracker.end_video()
    out = {"cambio_cap01_K": list(CAMBIO_K1), "tipo_foto": {f"cap{n:02d}": fotos[n][0] for n in fotos},
           "gastado_antes": gastado, "peor_caso": round(peor, 2), "usd_clips": round(rep.total_cost, 4) if rep else 0,
           "clips": res, "prompts_enviados": {c: prompts[c]["prompt"] for c in res}}
    (CLIPS / "resultado.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    for c, r in sorted(res.items()):
        print(c, r.get("error") or f"{r['ffprobe']} · espera {r.get('espera_s')} s · US$ {r.get('usd')}")
    print(f"US$ clips {out['usd_clips']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
