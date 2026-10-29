# -*- coding: utf-8 -*-
"""F53b Parte A — corrida en seco de `script_engine/video_prompt.escribir` para Gemini Omni Flash (PERFIL_VIDEO_G) sobre
las 2 fotos de F52 (`lab/hyperframes/f52/fotos/cap01.png`, `cap07.png`), con el `image_prompt`, el `narration_anchor` y el
`video_prompt` vivos de los caps 1 y 7 del 03_visual.json de Wittenoom (F51f, md5 0d57b6ba…). 2 llamadas a Opus en
paralelo; ningún clip. Guarda de tope antes. Salida: `SECO_G.md` y `seco_g.json`.
Uso: python lab/hyperframes/f53b/seco_g.py
"""
import hashlib
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "lab" / "hyperframes" / "f52"))
F53B = Path(__file__).resolve().parent
TID = "123bbb64-9fca-4395-8bf4-57d60e219ef1"
VISUAL = ROOT / "data" / "scripts" / "_steps" / TID / "03_visual.json"
MD5_VISUAL = "0d57b6bad197cae073c9c88596ed6130"
PEOR_CASO = 0.15                                             # 2 llamadas a Opus con imagen (F52b: 8 por 0,29)


def main() -> int:
    import prueba_video as pr                                 # gastado_desde_tope (F52)
    from cost_tracker import cost_tracker
    from engine_profiles import PERFIL_VIDEO_G
    from script_engine import video_prompt as vp
    raw = VISUAL.read_bytes()
    if hashlib.md5(raw).hexdigest() != MD5_VISUAL:
        print("03_visual.json no es el de F51f: PARADA")
        return 1
    gastado, tope = pr.gastado_desde_tope()
    print(f"gastado {gastado} · peor caso {PEOR_CASO} · tope {tope}")
    if gastado + PEOR_CASO >= tope:
        print("PARADA: pasa el tope")
        return 1
    caps = {c["chapter_number"]: c for c in json.loads(raw.decode("utf-8"))["chapters"] if c.get("image_prompts") is None}
    cost_tracker.start_video("f53b_seco_g")
    res = {}
    try:
        with ThreadPoolExecutor(max_workers=2) as ex:
            futs = {n: ex.submit(vp.escribir, PERFIL_VIDEO_G, ROOT / "lab" / "hyperframes" / "f52" / "fotos" / f"cap{n:02d}.png",
                                 c["image_prompt"], c["narration_anchor"], c.get("video_prompt"),
                                 description=f"f53b:seco:G:cap{n:02d}") for n, c in sorted(caps.items())}
            for n, f in futs.items():
                try:
                    res[n] = {"prompt": f.result()}
                except Exception as e:                                      # noqa: BLE001 — se reporta tal cual
                    res[n] = {"error": f"{type(e).__name__}: {e}"[:600]}
    finally:
        rep = cost_tracker.end_video()
    total = round(rep.total_cost, 4) if rep else None
    L = ["# SECO_G — `video_prompt.escribir` para Gemini Omni Flash, en seco (F53b Parte A)", "",
         f"Salida de `python lab/hyperframes/f53b/seco_g.py`: 2 llamadas a Opus 5.5 (effort high) por el módulo de "
         f"producción, con la foto como bloque `image`. Ningún clip. Costo: **US$ {total}**.", ""]
    for n in sorted(res):
        c, r = caps[n], res[n]
        L += [f"## Cap {n} (`veo_position` {c.get('veo_position')}) · foto `lab/hyperframes/f52/fotos/cap{n:02d}.png`", "",
              f"- Ancla: «{c['narration_anchor']}»", ""]
        if "error" in r:
            L += [f"**Error:** {r['error']}", ""]
            continue
        L += [f"**Prompt de G** ({len(r['prompt'].split())} palabras):", "", "```", r["prompt"], "```", ""]
    (F53B / "SECO_G.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    (F53B / "seco_g.json").write_text(json.dumps({"usd": total, "caps": {f"cap{n:02d}": r for n, r in res.items()}},
                                                 ensure_ascii=False, indent=1), encoding="utf-8")
    for n, r in sorted(res.items()):
        print(f"cap{n:02d}", r.get("error") or f"{len(r['prompt'].split())} palabras")
    print("US$", total)
    return 1 if any("error" in r for r in res.values()) else 0


if __name__ == "__main__":
    sys.exit(main())
