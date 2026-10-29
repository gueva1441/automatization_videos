# -*- coding: utf-8 -*-
"""F53b Parte B — 1 clip real por el camino de producción: `asset_manager._generate_clip` con la foto del cap 7 de
Wittenoom (`lab/hyperframes/f52/fotos/cap07.png`) y el `image_prompt`, `narration_anchor` y `video_prompt` del cap 7 del
03_visual.json de F51f (md5 0d57b6ba…), G (Gemini Omni Flash) a 1080p. Para esta corrida la cadena se limita a G
(`api.video_engines = ("gemini_omni_flash",)`): con K detrás, un rechazo de G llevaría el peor caso a ≈ 3,26 > tope 3.
Guarda de tope antes. Mide con ffprobe y compara el costo de cost_tracker con la tabla del handoff (G 0,15 US$/s).
Salida: `clip/cap07_clip_01.mp4` (fuera de git) y `clip_real.json`.
Uso: python lab/hyperframes/f53b/clip_real.py
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "lab" / "hyperframes" / "f52"))
F53B = Path(__file__).resolve().parent
TID = "123bbb64-9fca-4395-8bf4-57d60e219ef1"
VISUAL = ROOT / "data" / "scripts" / "_steps" / TID / "03_visual.json"
MD5_VISUAL = "0d57b6bad197cae073c9c88596ed6130"
PEOR_CASO = 1.20 + 0.04                                      # G a 1080p, 8 s (tabla del handoff) + 1 prompt de Opus


def main() -> int:
    import prueba_video as pr                                 # gastado_desde_tope (F52)
    import asset_manager as am
    from cost_tracker import cost_tracker
    salida = F53B / "clip" / "cap07_clip_01.mp4"
    if salida.exists():
        print("ya existe el clip: no se vuelve a llamar")
        return 1
    raw = VISUAL.read_bytes()
    if hashlib.md5(raw).hexdigest() != MD5_VISUAL:
        print("03_visual.json no es el de F51f: PARADA")
        return 1
    gastado, tope = pr.gastado_desde_tope()
    print(f"gastado {gastado} · peor caso {PEOR_CASO:.2f} · tope {tope}")
    if gastado + PEOR_CASO >= tope:
        print("PARADA: pasa el tope")
        return 1
    cap = next(c for c in json.loads(raw.decode("utf-8"))["chapters"] if c["chapter_number"] == 7)
    am.api.video_engines = ("gemini_omni_flash",)            # solo para esta corrida (ver docstring)
    log, error = [], None
    cost_tracker.start_video("f53b_clip_real")
    try:
        am._generate_clip(ROOT / "lab" / "hyperframes" / "f52" / "fotos" / "cap07.png", cap["video_prompt"], salida,
                          image_prompt=cap["image_prompt"], ancla=cap["narration_anchor"], log=log)
    except Exception as e:                                    # noqa: BLE001 — se reporta tal cual
        error = f"{type(e).__name__}: {e}"[:900]
    finally:
        rep = cost_tracker.end_video()
    entradas = [{"servicio": x.service, "descripcion": x.description, "usd": round(x.total_cost, 5)}
                for x in (rep.entries if rep else [])]
    ff = None
    if salida.exists():
        out = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                              "stream=codec_type,codec_name,width,height,r_frame_rate,nb_frames:format=duration",
                              "-of", "json", str(salida)], capture_output=True, text=True)
        ff = json.loads(out.stdout or "{}")
    res = {"error": error, "log": log, "ffprobe": ff, "cost_tracker": entradas,
           "usd_total": round(rep.total_cost, 4) if rep else None,
           "usd_tabla_G": round(0.15 * (log[0]["segundos"] if log and log[0].get("segundos") else 8), 4)}
    (F53B / "clip_real.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in res.items() if k != "ffprobe"}, ensure_ascii=False, indent=1)[:3000])
    return 1 if error else 0


if __name__ == "__main__":
    sys.exit(main())
