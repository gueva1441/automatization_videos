"""F29 §C.2–C.3 — bloques de un render de Vajont: tabla por cap (segundo, tipo, texto, beat, ventana, ya-dicho), pico,
sellos, pregunta, crítico y tiempo de gfx; comparación F27 → F29; y la hoja `BLOQUES_v3.jpg` (un cuadro por bloque del
mp4, en t + 1 s, con segundo, tipo, texto y beat).
Los tiempos del plan son del cap; en el video final se suma el arranque (2.5 s) y los segmentos anteriores.
Uso: PYTHONIOENCODING=utf-8 python -I lab/hyperframes/f29/c/f29c_bloques.py [work_f29] [mp4] [salida.jpg] [prefijo]
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
LAB = Path(__file__).resolve().parent
F27_WORK = ROOT / "output" / "f8s3-vajont" / "_fase2b_work"
F29_WORK = ROOT / "output" / "f8s3-vajont-f29" / "_fase2b_work"
V3 = ROOT / "output" / "f8s3-vajont-f29" / "f8s3-vajont_final_gfx_v3.mp4"
ARRANQUE = 2.5
SPOILERS = {"ch06": "1.910", "ch07": "Montedison"}      # los dos del diagnóstico F27 (§0)
KIND = {"archive_clippings": "recorte", "callouts": "rótulo", "emphasis": "sello", "quote_card": "cita",
        "count_up": "contador", "water_level": "nivel de agua", "evidence_zoom": "zoom", "icon_array": "íconos"}


def _dur(p: Path) -> float:
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                 str(p)], capture_output=True, text=True).stdout.strip())


def bloques(work: Path, cap: str) -> dict:
    f = work / f"gfx_plan_{cap}.resolved.json"
    if not f.exists():
        return {"cap": cap, "falta": True}
    plan = json.loads(f.read_text(encoding="utf-8")).get("plan") or {}
    out = []
    for k, nombre in KIND.items():
        v = plan.get(k)
        for b in (v if isinstance(v, list) else [v] if v else []):
            if not isinstance(b, dict) or "start" not in b:
                continue
            out.append({"t": round(float(b["start"]), 1), "tipo": nombre, "dur": round(float(b.get("duration", 0)), 1),
                        "texto": str(b.get("headline") or b.get("text") or b.get("word") or b.get("value_text")
                                     or b.get("anchor") or b.get("detail") or ""),
                        "beat": b.get("beat"), "pool_id": b.get("pool_id"), "pico": bool(b.get("pico"))})
    out.sort(key=lambda x: x["t"])
    pk = plan.get("pico") or {}
    real_f = work / f"gfx_beats_{cap}.json"
    real = json.loads(real_f.read_text(encoding="utf-8")) if real_f.exists() else None
    cand = {c["id"]: c for c in (real or {}).get("candidatos") or []}
    for b in out:
        c = cand.get(b["pool_id"] or "")
        if c:
            b["ventana"] = f"{c['t0']:.0f}–{c['t1']:.0f}"
            b["ya_dicho"] = c["ya_dicho"]
            b["beat"] = b["beat"] or c["beat"]
    crit = plan.get("critico") or []
    log = work / f"gfx_{cap}.log"
    t_gfx = None
    if log.exists():
        m = re.findall(r"OK (?:sparse )?(\d+(?:\.\d+)?)s", log.read_text(encoding="utf-8", errors="replace"))
        t_gfx = float(m[-1]) if m else None
    q = plan.get("chapter_question") or {}
    sp = SPOILERS.get(cap)
    return {"cap": cap, "bloques": out, "n": len([b for b in out if b["tipo"] != "zoom" or True]),
            "sellos": sum(b["tipo"] == "sello" for b in out),
            "pico": {"t": pk.get("t"), "word": pk.get("word"), "block": pk.get("block"),
                     "con_bloque": pk.get("block") in ("water_level", "evidence_zoom", "archive_clippings", "callouts",
                                                       "quote_card")},
            "pregunta": q.get("text"), "pregunta_fuente": q.get("fuente") or ("generada" if q.get("generated") else None),
            "critico": [(r.get("bloque"), r.get("texto"), r.get("veredicto"), r.get("pasa")) for r in crit],
            "spoiler": bool(sp and any(sp in b["texto"] and (pk.get("t") is None or b["t"] < float(pk["t"]))
                                       for b in out)),
            "t_gfx_s": t_gfx}


def resumen(work: Path) -> dict:
    caps = [bloques(work, f"ch{k:02d}") for k in range(1, 8)]
    ok = [c for c in caps if not c.get("falta")]
    return {"caps": caps, "bloques": sum(c["n"] for c in ok), "sellos": sum(c["sellos"] for c in ok),
            "pico_con_bloque": sum(c["pico"]["con_bloque"] for c in ok), "spoilers": sum(c["spoiler"] for c in ok)}


def hoja(work: Path, mp4: Path, out: Path) -> None:
    from PIL import Image, ImageDraw, ImageFont
    segs = sorted(work.glob("seg_0*_ch0*.mp4"))
    off, t_ini = ARRANQUE, {}
    for s in segs:
        t_ini[s.stem.split("_")[-1]] = off
        off += _dur(s)
    tiles = []
    tmp = LAB / "_cuadros"
    tmp.mkdir(exist_ok=True)
    try:
        font = ImageFont.truetype("arial.ttf", 18)
    except OSError:
        font = ImageFont.load_default()
    for k in range(1, 8):
        cap = f"ch{k:02d}"
        for b in bloques(work, cap).get("bloques") or []:
            t = t_ini.get(cap, 0) + b["t"] + min(1.0, b["dur"] / 2)
            jpg = tmp / f"{cap}_{b['t']:06.1f}.jpg"
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", str(mp4), "-frames:v", "1", "-vf",
                            "scale=640:-2", "-q:v", "4", str(jpg)], check=False)
            im = Image.open(jpg).convert("RGB") if jpg.exists() else Image.new("RGB", (640, 360))
            c = Image.new("RGB", (640, 360 + 52), (16, 16, 16))
            c.paste(im.resize((640, 360)), (0, 52))
            d = ImageDraw.Draw(c)
            d.text((8, 4), f"{cap} {b['t']:.1f}s · {b['tipo']} · beat {b.get('beat') or '—'}"
                           + (" · PICO" if b.get("pico") else ""), fill=(255, 210, 90), font=font)
            d.text((8, 27), b["texto"][:62], fill=(235, 235, 235), font=font)
            tiles.append(c)
    cols = 5
    rows = max(1, -(-len(tiles) // cols))
    sheet = Image.new("RGB", (cols * 640, rows * 412), (0, 0, 0))
    for i, t in enumerate(tiles):
        sheet.paste(t, ((i % cols) * 640, (i // cols) * 412))
    sheet.save(out, quality=82)


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    work = Path(sys.argv[1]) if len(sys.argv) > 1 else F29_WORK
    mp4 = Path(sys.argv[2]) if len(sys.argv) > 2 else V3
    out = Path(sys.argv[3]) if len(sys.argv) > 3 else LAB.parent / "BLOQUES_v3.jpg"
    pref = sys.argv[4] if len(sys.argv) > 4 else "bloques"
    res = {"F27": resumen(F27_WORK), "F29": resumen(work)}
    (LAB / f"{pref}.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    for k, v in res.items():
        print(k, {x: v[x] for x in ("bloques", "sellos", "pico_con_bloque", "spoilers")})
    if mp4.exists():
        hoja(work, mp4, out)
        print("hoja:", out)


if __name__ == "__main__":
    main()
