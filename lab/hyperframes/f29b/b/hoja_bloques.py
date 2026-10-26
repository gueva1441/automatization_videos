"""F29b §B.3 — la hoja de bloques (la que lee el analista en vez de los logs). Reusable para los renders que sigan.

Un renglón por bloque de texto del plan resuelto de cada cap:
    (i)   el cuadro en t0 + 1 s (en la hoja a 1280 px; el de 2560 queda al lado como jpg)
    (ii)  el mismo cuadro a 360 px de ancho (celular)
    (iii) la voz −6 s / durante / +6 s
    (iv)  `aporta` del rotulista · (v) veredicto del crítico · (vi) pool_id, tipo, oración, t0 en el cap y en el mp4
          (offset del cap + t0 + 2.5 s, la fórmula del handoff)
El cuadro sale del segmento con subtítulos (`chNN_segment_only.mp4` o `seg_NN_chNN.mp4`) si existe; si no, de
`chNN_gfx.mp4`. Uso:
    python -I lab/hyperframes/f29b/b/hoja_bloques.py <topic> <salida.jpg> ch03 ch06 [--offsets ch03=120.5,ch06=…]
"""
from __future__ import annotations

import json
import subprocess
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))


def _video(wd: Path, cap: str) -> Path:
    for f in (wd / f"{cap}_segment_only.mp4", *sorted(wd.glob(f"seg_*_{cap}.mp4")), wd / f"{cap}_gfx.mp4"):
        if f.exists():
            return f
    raise FileNotFoundError(cap)


def _cuadro(video: Path, t: float, dst: Path, width: int | None = None) -> Path:
    vf = ["-vf", f"scale={width}:-2:flags=area"] if width else []
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", str(video), "-frames:v", "1", *vf,
                    "-q:v", "2", str(dst)], check=True)
    return dst


def bloques(plan: dict) -> list[dict]:
    """Los bloques de texto del plan (con lo del rotulista si lo hay), en orden de tiempo."""
    out = []
    for c in plan.get("callouts") or []:
        out.append({"bloque": "dato", "texto": c.get("text"), **c})
    for a in plan.get("archive_clippings") or []:
        out.append({"bloque": "recorte", "texto": f"{a.get('kicker', '')} | {a.get('headline', '')}", **a})
    if plan.get("quote_card"):
        q = plan["quote_card"]
        out.append({"bloque": "cita", "texto": f"«{q.get('text')}» — {q.get('author')}", **q})
    if plan.get("evidence_zoom"):
        z = plan["evidence_zoom"]
        out.append({"bloque": "lupa", "texto": z.get("detail") or z.get("anchor"), **z})
    if plan.get("water_level"):
        w = plan["water_level"]
        out.append({"bloque": "nivel", "texto": f"{w.get('value_text')} {w.get('unit', '')}", **w})
    if plan.get("count_up"):
        c = plan["count_up"]
        out.append({"bloque": "contador", "texto": c.get("value_text"), **c})
    return sorted(out, key=lambda b: float(b["start"]))


def _critico(plan: dict, b: dict) -> str:
    v = b.get("critico")
    if isinstance(v, dict):
        if v.get("error"):
            return f"sin veredicto ({v['error']})"
        return (f"(1) {'sí' if v.get('habla_de_eso') else 'NO'}: {v.get('motivo_1')} · (2) "
                f"{'sí' if v.get('dice_algo_nuevo') else 'NO'}: {v.get('motivo_2')}")
    for r in plan.get("critico") or []:
        if abs(float(r.get("t", -1)) - float(b["start"])) < 0.01:
            return f"{r.get('veredicto')}: {r.get('motivo')}"
    return "—"


def _voz(words: list[dict], a: float, b: float, off: float) -> str:
    return " ".join(str(w["word"]) for w in words if a <= float(w["start"]) + off < b)


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    from PIL import Image, ImageDraw, ImageFont
    import fase2b
    from config import OUTPUT_DIR
    from script_engine.gfx_layer import remapped_words
    topic, salida = sys.argv[1], Path(sys.argv[2])
    caps = [a for a in sys.argv[3:] if a.startswith("ch")]
    offs = {}
    if "--offsets" in sys.argv:
        for kv in sys.argv[sys.argv.index("--offsets") + 1].split(","):
            k, v = kv.split("=")
            offs[k] = float(v)
    wd = OUTPUT_DIR / topic / "_fase2b_work"
    ad = OUTPUT_DIR / "audio" / topic
    plans = {p.chapter_id: p for p in fase2b._build_plans(
        json.loads((ad / "sync_map.json").read_text(encoding="utf-8")),
        json.loads((OUTPUT_DIR / topic / "assets" / "assets_manifest.json").read_text(encoding="utf-8")),
        topic, ad, fase2b._load_script_lookup(topic))}
    tmp = salida.parent / f"_{salida.stem}"
    tmp.mkdir(parents=True, exist_ok=True)
    try:
        font = ImageFont.truetype("arial.ttf", 22)
        small = ImageFont.truetype("arial.ttf", 18)
    except OSError:
        font = small = ImageFont.load_default()
    filas, datos = [], []
    for cap in caps:
        plan = json.loads((wd / f"gfx_plan_{cap}.resolved.json").read_text(encoding="utf-8"))["plan"]
        _, words = remapped_words(plans[cap])
        vid = _video(wd, cap)
        for k, b in enumerate(bloques(plan)):
            t0 = float(b["start"])
            full = _cuadro(vid, t0 + 1.0, tmp / f"{cap}_{k:02d}_2560.jpg")
            big = Image.open(full).convert("RGB")
            med = big.resize((1280, round(1280 * big.height / big.width)), Image.LANCZOS)
            cel = big.resize((360, round(360 * big.height / big.width)), Image.LANCZOS)
            row = {"cap": cap, "bloque": b["bloque"], "texto": b.get("texto"), "pool_id": b.get("pool_id"),
                   "tipo": b.get("tipo_rotulista") or b["bloque"], "oracion": b.get("sentence_idx"),
                   "t0_cap": round(t0, 2), "t0_mp4": round(offs.get(cap, 0.0) + t0 + 2.5, 2) if cap in offs else None,
                   "aporta": b.get("aporta"), "critico": _critico(plan, b),
                   "voz_antes": _voz(words, t0 - 6, t0, 0.0), "voz_durante": _voz(words, t0, t0 + float(b.get("duration", 3)), 0.0),
                   "voz_despues": _voz(words, t0 + float(b.get("duration", 3)), t0 + float(b.get("duration", 3)) + 6, 0.0),
                   "cuadro_2560": full.name}
            datos.append(row)
            filas.append((med, cel, row))
    if not filas:
        print("sin bloques", flush=True)
        return
    wtxt = 760
    rh = max(m.height for m, _, _ in filas) + 20
    sheet = Image.new("RGB", (1280 + 360 + wtxt + 40, len(filas) * rh + 10), (16, 16, 16))
    d = ImageDraw.Draw(sheet)
    for k, (med, cel, r) in enumerate(filas):
        y = 10 + k * rh
        sheet.paste(med, (10, y))
        sheet.paste(cel, (1300, y))
        x = 1300 + 360 + 20
        lines = [f"{r['cap']} · {r['tipo']} · {r['pool_id']} · oración [{r['oracion']}] · t0 {r['t0_cap']} s"
                 + (f" · mp4 {r['t0_mp4']} s" if r['t0_mp4'] is not None else ""), f"«{r['texto']}»", ""]
        lines += textwrap.wrap(f"APORTA: {r['aporta']}", 70) + textwrap.wrap(f"CRÍTICO: {r['critico']}", 70) + [""]
        lines += textwrap.wrap(f"VOZ −6 s: {r['voz_antes']}", 70)[:3] + textwrap.wrap(f"DURANTE: {r['voz_durante']}", 70)[:3]
        lines += textwrap.wrap(f"+6 s: {r['voz_despues']}", 70)[:3]
        for j, ln in enumerate(lines[:22]):
            d.text((x, y + j * 24), ln, fill=(240, 232, 210) if j < 2 else (175, 175, 165), font=font if j < 2 else small)
    salida.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(salida, quality=86)
    (salida.with_suffix(".json")).write_text(json.dumps(datos, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{salida} · {len(filas)} bloques", flush=True)


if __name__ == "__main__":
    main()
