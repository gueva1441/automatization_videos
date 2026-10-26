"""F29c §B.2 — la hoja de bloques de v4 (la de F29b con las unidades de F29c). Un renglón por bloque del rotulista en
pantalla (y uno por bloque cortado por el crítico o fuera por zona, con el cuadro de la foto sola):
    (i)   el cuadro en t0 + 1 s del mp4 entero (en la hoja a 1280 px; el de 2560 queda al lado como jpg)
    (ii)  el mismo cuadro a 360 px (celular)
    (iii) la voz: oración anterior / ANCLA / siguiente
    (iv)  `aporta` · (v) crítico (las 3 preguntas) · (vi) cap, beat, tipo, pool_id, oración/palabra, t0 en el cap y
          t en el mp4 entero (offset del cap + t0 + 2.5 s de la intro)
Offset del cap = su inicio en `_concat_video.ts` (Σ segmentos anteriores − Σ transiciones entre caps, las de
transition_applier). Uso: python -I lab/hyperframes/f29c/b/hoja_bloques.py <mp4 entero> <salida.jpg> [<work_dir>]
"""
from __future__ import annotations

import json
import subprocess
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
DST = "f8s3-vajont-f30"
INTRO_S = 2.5


def _dur(p: Path) -> float:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                       capture_output=True, text=True)
    return float(r.stdout.strip())


def offsets(wd: Path, plans: list, negro: bool = False) -> dict[str, float]:
    from script_engine.transition_applier import build_transition_plan
    caps = [p.chapter_id for p in plans]
    segs = [wd / f"seg_{i + 1:02d}_{c}.mp4" for i, c in enumerate(caps)]
    tr = [0.0] * (len(caps) - 1) if negro else \
        [round(max(t.duration_seconds, 1 / 30) * 30) / 30 for t in build_transition_plan(len(caps), [p.art_profile for p in plans])]
    off, t = {}, 0.0
    for i, c in enumerate(caps):
        off[c] = round(t, 3)
        t += _dur(segs[i]) - (tr[i] if i < len(tr) else 0.0)
    return off


def _cuadro(video: Path, t: float, dst: Path) -> Path:
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", str(video), "-frames:v", "1", "-q:v", "2",
                    str(dst)], check=True)
    return dst


def _critico(v: dict | None) -> str:
    if not isinstance(v, dict):
        return "—"
    if v.get("error"):
        return f"sin veredicto ({v['error']})"
    return (f"(1) {'sí' if v.get('habla_de_eso') else 'NO'}: {v.get('motivo_1')} · (2) "
            f"{'sí' if v.get('dice_algo_nuevo') else 'NO'}: {v.get('motivo_2')} · (3) estorba "
            f"{'SÍ' if v.get('estorba') else 'no'}: {v.get('motivo_3')}")


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    from PIL import Image, ImageDraw, ImageFont
    import fase2b
    from config import OUTPUT_DIR
    from script_engine.gfx_peak import sentences
    from script_engine.gfx_layer import remapped_words
    mp4, salida = Path(sys.argv[1]), Path(sys.argv[2])
    wd = Path(sys.argv[3]) if len(sys.argv) > 3 else OUTPUT_DIR / DST / "_fase2b_work"
    negro = "--negro" in sys.argv
    pre = 3.0 if "--pre-roll" in sys.argv else 0.0
    ad = OUTPUT_DIR / "audio" / DST
    plans = fase2b._build_plans(json.loads((ad / "sync_map.json").read_text(encoding="utf-8")),
                                json.loads((OUTPUT_DIR / DST / "assets" / "assets_manifest.json").read_text(encoding="utf-8")),
                                DST, ad, fase2b._load_script_lookup(DST))
    off = offsets(wd, plans, negro)
    tmp = salida.parent / f"_{salida.stem}"
    tmp.mkdir(parents=True, exist_ok=True)
    try:
        font = ImageFont.truetype("arial.ttf", 22)
        small = ImageFont.truetype("arial.ttf", 18)
    except OSError:
        font = small = ImageFont.load_default()
    filas, datos = [], []
    for p in plans:
        cap = p.chapter_id
        plan = json.loads((wd / f"gfx_plan_{cap}.resolved.json").read_text(encoding="utf-8"))["plan"]
        _, words = remapped_words(p)
        ss = sentences(words, pre)
        bl = []
        for c in plan.get("callouts") or []:
            if c.get("rotulista"):
                bl.append(("ficha", f"{str(c.get('kicker', '')).upper()} | {c['text']}", c, "en pantalla"))
        for a in plan.get("archive_clippings") or []:
            if a.get("rotulista"):
                bl.append(("documento", f"{a.get('kicker', '')} | {a.get('headline', '')}", a, "en pantalla"))
        if plan.get("quote_card") and plan["quote_card"].get("rotulista"):
            q = plan["quote_card"]
            bl.append(("cita", f"«{q['text']}» — {q.get('author')}", q, "en pantalla"))
        if plan.get("evidence_zoom") and plan["evidence_zoom"].get("rotulista"):
            z = plan["evidence_zoom"]
            bl.append(("lupa", z.get("detail") or "", z, "en pantalla"))
        for r in plan.get("critico_rotulista") or []:
            if not r.get("pasa"):
                bl.append((r.get("bloque"), r.get("texto"), {"start": r["t"], "pool_id": r.get("pool_id"),
                                                              "aporta": r.get("aporta"), "critico": r}, "CORTADO por el crítico"))
        for nombre, txt, b, estado in sorted(bl, key=lambda x: float(x[2]["start"])):
            t0 = float(b["start"])
            tm = off[cap] + t0 + INTRO_S
            full = _cuadro(mp4, tm + 1.0, tmp / f"{cap}_{t0:07.2f}_2560.jpg")
            big = Image.open(full).convert("RGB")
            med = big.resize((1280, round(1280 * big.height / big.width)), Image.LANCZOS)
            cel = big.resize((360, round(360 * big.height / big.width)), Image.LANCZOS)
            si = b.get("sentence_idx")
            voz = [ss[k]["text"] if si is not None and 0 <= k < len(ss) else "—" for k in ((si or 0) - 1, si or 0, (si or 0) + 1)]
            row = {"cap": cap, "estado": estado, "tipo": b.get("tipo_rotulista") or nombre, "texto": txt,
                   "pool_id": b.get("pool_id"), "beat": b.get("beat"), "oracion": si, "palabra": b.get("word_idx"),
                   "t0_cap": round(t0, 2), "t_mp4": round(tm, 2), "aporta": b.get("aporta"),
                   "critico": _critico(b.get("critico")), "a_pantalla": b.get("a_pantalla"),
                   "voz_anterior": voz[0], "voz_ancla": voz[1], "voz_siguiente": voz[2], "cuadro_2560": full.name}
            datos.append(row)
            filas.append((med, cel, row))
    if not filas:
        print("sin bloques", flush=True)
        (salida.with_suffix(".json")).write_text("[]", encoding="utf-8")
        return
    wtxt = 820
    rh = max(m.height for m, _, _ in filas) + 20
    sheet = Image.new("RGB", (1280 + 360 + wtxt + 40, len(filas) * rh + 10), (16, 16, 16))
    d = ImageDraw.Draw(sheet)
    for k, (med, cel, r) in enumerate(filas):
        y = 10 + k * rh
        sheet.paste(med, (10, y))
        sheet.paste(cel, (1300, y))
        x = 1300 + 360 + 20
        lines = [f"{r['cap']} · beat {r['beat']} · {r['tipo']} · {r['pool_id']}" + (" (a_pantalla)" if r["a_pantalla"] else "")
                 + f" · {r['estado']}",
                 f"oración [{r['oracion']}] palabra {r['palabra']} · t0 cap {r['t0_cap']} s · t mp4 {r['t_mp4']} s",
                 f"«{r['texto']}»", ""]
        lines += textwrap.wrap(f"APORTA: {r['aporta']}", 76) + textwrap.wrap(f"CRÍTICO: {r['critico']}", 76)[:4] + [""]
        lines += textwrap.wrap(f"−1: {r['voz_anterior']}", 76)[:2] + textwrap.wrap(f"ANCLA: {r['voz_ancla']}", 76)[:3]
        lines += textwrap.wrap(f"+1: {r['voz_siguiente']}", 76)[:2]
        for j, ln in enumerate(lines[:24]):
            d.text((x, y + j * 23), ln, fill=(240, 232, 210) if j < 3 else (175, 175, 165), font=font if j < 3 else small)
    salida.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(salida, quality=86)
    (salida.with_suffix(".json")).write_text(json.dumps({"offsets_concat": off, "bloques": datos}, ensure_ascii=False,
                                                        indent=1), encoding="utf-8")
    print(f"{salida} · {len(filas)} renglones", flush=True)


if __name__ == "__main__":
    main()
