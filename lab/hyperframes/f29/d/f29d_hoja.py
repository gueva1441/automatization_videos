"""F29 §D.2 — hoja de contactos de bloques LADO A LADO, Flash | Sonnet, caps 5 y 6, y la tabla de diferencias.
Cada fila es un bloque (en orden de tiempo) de cada realizador, con el cuadro de su `chNN_gfx_{flash,sonnet}.mp4` en
t + 1 s. → lab/hyperframes/f29/D_flash_vs_sonnet.jpg + d/diferencias.json
Uso: PYTHONIOENCODING=utf-8 python -I lab/hyperframes/f29/d/f29d_hoja.py
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
LAB = Path(__file__).resolve().parent
SAL = ROOT / "output" / "f8s3-vajont-f29" / "d"
sys.path.insert(0, str(LAB.parent / "c"))
from f29c_bloques import KIND  # noqa: E402


def bloques(plan_json: Path) -> list[dict]:
    plan = json.loads(plan_json.read_text(encoding="utf-8")).get("plan") or {}
    out = []
    for k, nombre in KIND.items():
        v = plan.get(k)
        for b in (v if isinstance(v, list) else [v] if v else []):
            if isinstance(b, dict) and "start" in b:
                out.append({"t": round(float(b["start"]), 1), "tipo": nombre, "dur": round(float(b.get("duration", 0)), 1),
                            "texto": str(b.get("headline") or b.get("text") or b.get("word") or b.get("value_text")
                                         or b.get("anchor") or ""), "pool_id": b.get("pool_id"), "beat": b.get("beat")})
    return sorted(out, key=lambda x: x["t"])


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    from PIL import Image, ImageDraw, ImageFont
    try:
        font = ImageFont.truetype("arial.ttf", 18)
    except OSError:
        font = ImageFont.load_default()
    filas, dif = [], {}
    tmp = LAB / "_cuadros"
    tmp.mkdir(exist_ok=True)
    for cap in ("ch05", "ch06"):
        lados = {}
        for quien in ("flash", "sonnet"):
            pj = SAL / f"gfx_plan_{cap}_{quien}.resolved.json"
            lados[quien] = bloques(pj) if pj.exists() else []
        a, b = lados["flash"], lados["sonnet"]
        dif[cap] = {"flash": a, "sonnet": b,
                    "solo_flash": [x for x in a if not any(y["pool_id"] == x["pool_id"] and y["tipo"] == x["tipo"] for y in b)],
                    "solo_sonnet": [y for y in b if not any(x["pool_id"] == y["pool_id"] and x["tipo"] == y["tipo"] for x in a)],
                    "mismo_id_otro_texto": [(x["pool_id"], x["texto"], y["texto"]) for x in a for y in b
                                            if x["pool_id"] and x["pool_id"] == y["pool_id"] and x["texto"] != y["texto"]]}
        for k in range(max(len(a), len(b))):
            fila = []
            for quien, lst in (("flash", a), ("sonnet", b)):
                c = Image.new("RGB", (800, 450 + 56), (16, 16, 16))
                if k < len(lst):
                    x = lst[k]
                    jpg = tmp / f"{cap}_{quien}_{k}.jpg"
                    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{x['t'] + min(1.0, x['dur'] / 2):.2f}", "-i",
                                    str(SAL / f"{cap}_gfx_{quien}.mp4"), "-frames:v", "1", "-vf", "scale=800:-2",
                                    "-q:v", "4", str(jpg)], check=False)
                    if jpg.exists():
                        c.paste(Image.open(jpg).convert("RGB").resize((800, 450)), (0, 56))
                    d = ImageDraw.Draw(c)
                    d.text((8, 4), f"{cap} {quien.upper()} · {x['t']:.1f}s · {x['tipo']} · {x['pool_id'] or '—'} · "
                                   f"beat {x['beat'] or '—'}", fill=(255, 210, 90), font=font)
                    d.text((8, 28), x["texto"][:78], fill=(235, 235, 235), font=font)
                fila.append(c)
            filas.append(fila)
    sheet = Image.new("RGB", (1600, max(1, len(filas)) * 506), (0, 0, 0))
    for i, (l, r) in enumerate(filas):
        sheet.paste(l, (0, i * 506))
        sheet.paste(r, (800, i * 506))
    sheet.save(LAB.parent / "D_flash_vs_sonnet.jpg", quality=82)
    (LAB / "diferencias.json").write_text(json.dumps(dif, ensure_ascii=False, indent=1), encoding="utf-8")
    for cap, v in dif.items():
        print(cap, "flash", len(v["flash"]), "sonnet", len(v["sonnet"]), "solo flash", len(v["solo_flash"]),
              "solo sonnet", len(v["solo_sonnet"]), "mismo id otro texto", len(v["mismo_id_otro_texto"]))


if __name__ == "__main__":
    main()
