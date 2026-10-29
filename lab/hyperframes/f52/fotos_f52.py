# -*- coding: utf-8 -*-
"""F52 etapa 1 — las 2 fotos de arranque de los clips de Wittenoom (cap 1, veo_position start; cap 7, end) con el
prompt vivo del 03_visual.json (`image_prompt` del cap) y el mismo motor y camino de producción:
`asset_manager._generate_flux_image_at(image_prompt, art_profile, path, use_ultra=False)` → con el validador apagado,
una sola llamada `_generate_image_raw` → Seedream (`engine_profiles.select_profile("seedream")`), t2i (las dos fotos
no tienen foto_madre_ref). No toca producción: solo importa. Costo por `cost_tracker` (video_id `f52_lab`).

Uso: python lab/hyperframes/f52/fotos_f52.py
"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
F52 = Path(__file__).resolve().parent
TID = "123bbb64-9fca-4395-8bf4-57d60e219ef1"
VISUAL = ROOT / "data" / "scripts" / "_steps" / TID / "03_visual.json"
MD5_VISUAL = "0d57b6bad197cae073c9c88596ed6130"


def main() -> int:
    raw = VISUAL.read_bytes()
    if hashlib.md5(raw).hexdigest() != MD5_VISUAL:
        print(f"03_visual.json no es el de F51f ({MD5_VISUAL[:8]}…): PARADA")
        return 1
    v = json.loads(raw.decode("utf-8"))
    import asset_manager as am
    from cost_tracker import cost_tracker
    (F52 / "fotos").mkdir(exist_ok=True)
    cost_tracker.start_video("f52_lab")
    out = {}
    try:
        for cap in v["chapters"]:
            n = cap["chapter_number"]
            if cap.get("image_prompts") is not None:
                continue
            ref = (cap.get("image_f8") or {}).get("foto_madre_ref")
            if ref:
                print(f"cap {n}: tiene foto_madre_ref {ref}: PARADA (esta tanda va sin foto madre)")
                return 1
            p = F52 / "fotos" / f"cap{n:02d}.png"
            if p.exists():
                print(f"ya existe {p.name}: no se regenera")
                continue
            r = am._generate_flux_image_at(cap["image_prompt"], cap.get("art_profile") or "", p, False)
            out[f"cap{n:02d}"] = {"veo_position": cap.get("veo_position"), "prompt": cap["image_prompt"],
                                  "art_profile": cap.get("art_profile") or "", "meta": r.get("flux_meta"),
                                  "md5": hashlib.md5(p.read_bytes()).hexdigest()}
            print(f"cap {n}: {p.name} · {json.dumps(r.get('flux_meta'), ensure_ascii=False)}")
    finally:
        rep = cost_tracker.end_video()
        if rep:
            print(f"costo: US$ {rep.total_cost:.4f}")
            out["_costo_usd"] = round(rep.total_cost, 4)
    (F52 / "fotos" / "fotos_f52.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
