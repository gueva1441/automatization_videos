# -*- coding: utf-8 -*-
"""F53b Parte B (chascada 2) — corrida en seco de `script_engine/video_prompt.escribir` para Kling 4.0 (PERFIL_VIDEO_K)
sobre `lab/hyperframes/f52/fotos/cap01.png`, con el mismo `image_prompt`, `narration_anchor` y `video_prompt` del cap 1
que `seco_g.py` (03_visual.json de Wittenoom, F51f, md5 0d57b6ba…). 1 llamada a Opus; ningún clip. Guarda de tope antes.
Salida: `SECO_K.md` (el prompt de K al lado del de G del cap 1, de `seco_g.json`) y `seco_k.json`.
Uso: python lab/hyperframes/f53b/seco_k.py
"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "lab" / "hyperframes" / "f52"))
F53B = Path(__file__).resolve().parent
TID = "123bbb64-9fca-4395-8bf4-57d60e219ef1"
VISUAL = ROOT / "data" / "scripts" / "_steps" / TID / "03_visual.json"
MD5_VISUAL = "0d57b6bad197cae073c9c88596ed6130"
PEOR_CASO = 0.065 / 2 * 1.5                    # SECO_G costó 0,065 por 2 llamadas; margen ×1,5


def main() -> int:
    import prueba_video as pr                  # gastado_desde_tope (F52)
    from cost_tracker import cost_tracker
    from engine_profiles import PERFIL_VIDEO_K
    from script_engine import video_prompt as vp
    raw = VISUAL.read_bytes()
    if hashlib.md5(raw).hexdigest() != MD5_VISUAL:
        print("03_visual.json no es el de F51f: PARADA")
        return 1
    gastado, tope = pr.gastado_desde_tope()
    print(f"gastado {gastado} · peor caso {PEOR_CASO:.3f} · tope {tope}")
    if gastado + PEOR_CASO >= tope:
        print("PARADA: pasa el tope")
        return 1
    cap = next(c for c in json.loads(raw.decode("utf-8"))["chapters"] if c["chapter_number"] == 1)
    cost_tracker.start_video("f53b_seco_k")
    try:
        prompt = vp.escribir(PERFIL_VIDEO_K, ROOT / "lab" / "hyperframes" / "f52" / "fotos" / "cap01.png",
                             cap["image_prompt"], cap["narration_anchor"], cap.get("video_prompt"),
                             description="f53b:seco:K:cap01")
    finally:
        rep = cost_tracker.end_video()
    total = round(rep.total_cost, 4) if rep else None
    g = json.loads((F53B / "seco_g.json").read_text(encoding="utf-8"))["caps"]["cap01"]["prompt"]
    L = ["# SECO_K — `video_prompt.escribir` para Kling 4.0, en seco (F53b Parte B, chascada 2)", "",
         f"Salida de `python lab/hyperframes/f53b/seco_k.py`: 1 llamada a Opus 5.5 (effort high) por el módulo de "
         f"producción, con la foto `lab/hyperframes/f52/fotos/cap01.png` como bloque `image` y las mismas entradas que "
         f"`SECO_G.md`. Ningún clip. Costo: **US$ {total}**.", "",
         f"- Ancla: «{cap['narration_anchor']}»", "",
         f"## K — Kling 4.0 ({len(prompt.split())} palabras)", "", "```", prompt, "```", "",
         f"## G — Gemini Omni Flash, el de SECO_G ({len(g.split())} palabras)", "", "```", g, "```", ""]
    (F53B / "SECO_K.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    (F53B / "seco_k.json").write_text(json.dumps({"usd": total, "cap01": {"prompt": prompt}}, ensure_ascii=False,
                                                 indent=1), encoding="utf-8")
    print(f"cap01 K: {len(prompt.split())} palabras · US$ {total}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
