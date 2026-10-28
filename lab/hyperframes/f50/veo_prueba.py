# -*- coding: utf-8 -*-
"""F50 C §4 — UNA llamada de prueba a Veo (fal) con el payload de producción nuevo: el primer cuadro de hoy del cap 1
de Wittenoom, su video_prompt de hoy (f50/antes/03_visual.json), VEO_NEGATIVE_PROMPT y duration "4s".
Guarda veo_prueba.mp4 y veo_prueba.json (payload sin la imagen, respuestas de fal, duración medida, costo).
Uso: python lab/hyperframes/f50/veo_prueba.py
"""
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
F50 = Path(__file__).resolve().parent
TID = "123bbb64-9fca-4395-8bf4-57d60e219ef1"


def main() -> int:
    import requests

    import asset_manager as am
    from cost_tracker import cost_tracker
    img = ROOT / "output" / TID / "assets" / "ch01_veo" / "ch01_img_01.png"
    ch1 = next(c for c in json.loads((F50 / "antes" / "03_visual.json").read_text(encoding="utf-8"))["chapters"]
               if c["chapter_number"] == 1)
    vp = ch1["video_prompt"]
    reg = {"imagen": str(img.relative_to(ROOT)), "video_prompt": vp, "negative_prompt": am.VEO_NEGATIVE_PROMPT,
           "duration": "4s", "endpoint": f"{am.api.fal_base_url}/{am.api.fal_video_model}", "respuestas": []}
    post_orig, get_orig = requests.post, requests.get

    def post(url, **k):
        r = post_orig(url, **k)
        pl = dict(k.get("json") or {})
        pl["image_url"] = pl.get("image_url", "")[:40] + "…"
        reg["payload"] = pl
        reg["respuestas"].append({"url": url, "status": r.status_code, "body": r.text[:2000]})
        return r

    def get(url, **k):
        r = get_orig(url, **k)
        if "video" not in url and not url.endswith(".mp4"):
            reg["respuestas"].append({"url": url, "status": r.status_code, "body": r.text[:2000]})
        return r
    am.requests.post, am.requests.get = post, get
    cost_tracker.start_video("f50-veo-prueba")
    t0 = time.time()
    out = F50 / "veo_prueba.mp4"
    try:
        am._call_veo_once(img, vp, out, duracion_s=4)
        cost_tracker.track_fal(description="f50 veo_prueba 4s", clips=1)
        reg["estado"] = "ok"
    except Exception as e:  # noqa: BLE001 — se reporta tal cual (PARADA si fal rechaza negative_prompt o duration)
        reg["estado"] = f"{type(e).__name__}: {e}"
    finally:
        am.requests.post, am.requests.get = post_orig, get_orig
        r = cost_tracker.end_video()
        reg["costo_tracker_usd"] = round(getattr(r, "total_cost", 0.0) or 0.0, 4)
    reg["segundos"] = round(time.time() - t0, 1)
    if out.exists():
        pr = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=width,height,codec_name",
                             "-of", "json", str(out)], capture_output=True, text=True)
        reg["ffprobe"] = json.loads(pr.stdout or "{}")
    (F50 / "veo_prueba.json").write_text(json.dumps(reg, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: reg.get(k) for k in ("estado", "segundos", "costo_tracker_usd", "ffprobe")}, ensure_ascii=False))
    return 0 if reg["estado"] == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
