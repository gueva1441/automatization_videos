"""F31 — laboratorio de forma: 11 renders `--only-cap ch06` (los planes de v5 en caché) con `--forma-variante`, los
clips con los tramos de bloque, la hoja VARIANTES_ch06.jpg y las medidas. Nada queda como default.

    render <etiqueta>   un `--only-cap ch06` con la variante (Firefox cerrado, RAM > 14 GB); el segmento queda en
                        corridas/<etiqueta>/ (hardlink) con el plan y el log.
    todas               las 11 en fila.
    clips               ch06_<etiqueta>.mp4: los tramos con bloque ± una oración, concatenados.
    hoja                VARIANTES_ch06.jpg: una fila por bloque, una columna por variante; celda = 6 cuadros a 360 px
                        (2 de la entrada, 2 de la mitad, 2 de la salida) y debajo el recorte del bloque a 2560 (1:1).
    medidas             contraste WCAG texto/fondo, cuadros reales de entrada y salida, alto de letra a 360 px.
Uso: python -I lab/hyperframes/f31/f31_variantes.py render V1 | todas | clips | hoja | medidas
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / "lab" / "hyperframes" / "f30"), str(ROOT / "lab" / "hyperframes" / "f26" / "b")]
LAB = Path(__file__).resolve().parent
DST = "f8s3-vajont-f30"
WD = ROOT / "output" / DST / "_fase2b_work"
CAP = "ch06"
FPS = 30
# HANDOFF_F31 §B.1: V1/V2/V3 con S2+placa y R2 · S1/S2/S3 con y sin placa con V2 y R2 · R1/R2 con V2 y S2+placa
VARIANTES = {
    "V1_S2P_R2": "V1,S2P,R2", "V2_S2P_R2": "V2,S2P,R2", "V3_S2P_R2": "V3,S2P,R2",
    "V2_S1_R2": "V2,S1,R2", "V2_S1P_R2": "V2,S1P,R2", "V2_S2_R2": "V2,S2,R2", "V2_S2P_R2_b": "V2,S2P,R2",
    "V2_S3_R2": "V2,S3,R2", "V2_S3P_R2": "V2,S3P,R2",
    "V2_S2P_R1": "V2,S2P,R1", "V2_S2P_R2_c": "V2,S2P,R2",
}


def _f30():
    import f30_vajont as f
    f.DST, f.W_DST, f.LAB = DST, WD, LAB
    return f


def render(etq: str) -> dict:
    f = _f30()
    ram = f._guardia()
    for x in (WD / f"{CAP}_gfx.mp4", WD / f"gfx_{CAP}.log"):
        if x.exists():
            bak = WD / "_bak_f31" / f"{x.stem}__{int(time.time())}{x.suffix}"
            bak.parent.mkdir(exist_ok=True)
            x.replace(bak)
    rc, pared, ram_min = f._fase2b([DST, "--only-cap", CAP, "--reuse-visuals", "--gfx", "--gfx-sparse", "--gfx-quality",
                                    "looks", "--rotulista", "--rotulista-tope", "0.5", "--forma-variante", VARIANTES[etq]],
                                   LAB / "corridas" / f"{etq}.out")
    dst = LAB / "corridas" / etq
    dst.mkdir(parents=True, exist_ok=True)
    for n in (f"{CAP}_segment_only.mp4", f"{CAP}_gfx.mp4", f"gfx_{CAP}.log", f"gfx_plan_{CAP}.resolved.json"):
        if (WD / n).exists():
            (dst / n).unlink(missing_ok=True)
            if n.endswith(".mp4"):
                shutil.copy2(WD / n, dst / n) if n.startswith(CAP + "_segment") else os.link(WD / n, dst / n)
            else:
                shutil.copy2(WD / n, dst / n)
    res = {"etiqueta": etq, "flag": VARIANTES[etq], "rc": rc, "pared_s": round(pared, 1), "ram_antes_gb": round(ram, 1),
           "ram_min_gb": round(ram_min, 2) if ram_min else None}
    (dst / "corrida.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(res, ensure_ascii=False), flush=True)
    return res


def todas() -> list[dict]:
    out = []
    for etq in VARIANTES:
        if (LAB / "corridas" / etq / "corrida.json").exists():
            continue
        subprocess.run(["powershell", "-NoProfile", "-Command",
                        "Get-Process firefox -ErrorAction SilentlyContinue | ForEach-Object { $_.CloseMainWindow() | Out-Null }"],
                       capture_output=True)
        out.append(render(etq))
    return out


def _bloques(plan: dict) -> list[dict]:
    """Los bloques de ch06 que cambian con la forma: fichas y recortes, el sello y el reloj."""
    out = []
    for c in plan.get("callouts") or []:
        if c.get("ficha"):
            out.append({"bloque": f"ficha {c.get('pool_id')}", "t0": c["start"], "t1": c["start"] + c["duration"],
                        "zona": (0.05, 0.22, 0.85, 0.50)})
    for a in plan.get("archive_clippings") or []:
        out.append({"bloque": f"recorte {a.get('pool_id')}", "t0": a["start"], "t1": a["start"] + a["duration"],
                    "zona": (0.0, 0.0, 1.0, 1.0)})
    for e in plan.get("emphasis") or []:
        if e.get("stamp") and e.get("word"):
            dur = 1.6
            out.append({"bloque": f"sello «{e['word']}»", "t0": e["start"], "t1": e["start"] + dur,
                        "zona": (0.45, 0.30, 1.0, 0.62) if e.get("side", "right") == "right" else (0.0, 0.30, 0.55, 0.62)})
    tk = plan.get("time_ticker")
    if tk:
        out.append({"bloque": f"reloj {tk.get('day')} {tk.get('month')}", "t0": tk["start"],
                    "t1": tk["start"] + tk["duration"],
                    "zona": (0.0, 0.0, 0.45, 0.16) if tk.get("side") != "right" else (0.55, 0.0, 1.0, 0.16)})
    return sorted(out, key=lambda b: b["t0"])


def _plan(etq: str) -> dict:
    return json.loads((LAB / "corridas" / etq / f"gfx_plan_{CAP}.resolved.json").read_text(encoding="utf-8"))["plan"]


def clips() -> None:
    from script_engine.gfx_peak import sentences
    import fase2b
    from config import OUTPUT_DIR
    from script_engine.gfx_layer import remapped_words
    ad = OUTPUT_DIR / "audio" / DST
    plans = {p.chapter_id: p for p in fase2b._build_plans(
        json.loads((ad / "sync_map.json").read_text(encoding="utf-8")),
        json.loads((OUTPUT_DIR / DST / "assets" / "assets_manifest.json").read_text(encoding="utf-8")),
        DST, ad, fase2b._load_script_lookup(DST))}
    _, words = remapped_words(plans[CAP])
    ss = sentences(words, 3.0)                    # el pre-roll del title card (F30b) corre la voz 3 s
    for etq in VARIANTES:
        seg = LAB / "corridas" / etq / f"{CAP}_segment_only.mp4"
        if not seg.exists():
            continue
        tramos = []
        for b in _bloques(_plan(etq)):
            a = max([s["t0"] for s in ss if s["t0"] <= b["t0"]][-2:] or [b["t0"] - 3])
            z = min([s["t1"] for s in ss if s["t1"] >= b["t1"]][:2] or [b["t1"] + 3])
            tramos.append((max(0.0, a), z))
        tramos.sort()
        fus = []
        for a, z in tramos:
            if fus and a <= fus[-1][1]:
                fus[-1][1] = max(fus[-1][1], z)
            else:
                fus.append([a, z])
        fc = "".join(f"[0:v]trim={a:.3f}:{z:.3f},setpts=PTS-STARTPTS[v{i}];[0:a]atrim={a:.3f}:{z:.3f},asetpts=PTS-STARTPTS[a{i}];"
                     for i, (a, z) in enumerate(fus))
        fc += "".join(f"[v{i}][a{i}]" for i in range(len(fus))) + f"concat=n={len(fus)}:v=1:a=1[v][a]"
        out = LAB / f"{CAP}_{etq}.mp4"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(seg), "-filter_complex", fc, "-map", "[v]", "-map", "[a]",
                        "-c:v", "libx264", "-preset", "fast", "-crf", "20", "-c:a", "aac", str(out)], check=True)
        print(out.name, [(round(a, 1), round(z, 1)) for a, z in fus], flush=True)


def _frame(seg: Path, t: float, w: int | None = None) -> np.ndarray:
    vf = ["-vf", f"scale={w}:-2:flags=area"] if w else []
    r = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.4f}", "-i", str(seg), "-frames:v", "1", *vf, "-f", "image2pipe",
                        "-vcodec", "png", "-"], capture_output=True, check=True)
    from PIL import Image
    import io
    return np.asarray(Image.open(io.BytesIO(r.stdout)).convert("RGB"))


def _tiempos_celda(b: dict) -> list[float]:
    t0, t1 = b["t0"], b["t1"]
    return [t0 + 0.10, t0 + 0.35, (t0 + t1) / 2 - 0.2, (t0 + t1) / 2 + 0.2, t1 - 0.30, t1 - 0.08]


def hoja() -> Path:
    from PIL import Image, ImageDraw, ImageFont
    etqs = [e for e in VARIANTES if (LAB / "corridas" / e / f"{CAP}_segment_only.mp4").exists()]
    filas = _bloques(_plan(etqs[0]))
    try:
        font = ImageFont.truetype("arial.ttf", 26)
    except OSError:
        font = ImageFont.load_default()
    cw, ch = 360, 203                                   # 6 cuadros a 360 px: 3 × 2
    crop_w = 3 * cw
    cell_h = 2 * ch + 20 + 420 + 40
    sheet = Image.new("RGB", (260 + len(etqs) * (crop_w + 20), 60 + len(filas) * cell_h), (14, 14, 14))
    d = ImageDraw.Draw(sheet)
    for j, e in enumerate(etqs):
        d.text((260 + j * (crop_w + 20), 15), f"{e}  ({VARIANTES[e]})", fill=(240, 232, 210), font=font)
    for i, b in enumerate(filas):
        y0 = 60 + i * cell_h
        d.text((10, y0 + 10), b["bloque"], fill=(240, 232, 210), font=font)
        for j, e in enumerate(etqs):
            seg = LAB / "corridas" / e / f"{CAP}_segment_only.mp4"
            bb = next((x for x in _bloques(_plan(e)) if x["bloque"] == b["bloque"]), b)
            x0 = 260 + j * (crop_w + 20)
            for k, t in enumerate(_tiempos_celda(bb)):
                im = Image.fromarray(_frame(seg, t, cw))
                sheet.paste(im, (x0 + (k % 3) * cw, y0 + (k // 3) * ch))
            full = _frame(seg, (bb["t0"] + bb["t1"]) / 2)
            H, W = full.shape[:2]
            zx0, zy0, zx1, zy1 = bb["zona"]
            cx, cy = int((zx0 + zx1) / 2 * W), int((zy0 + zy1) / 2 * H)
            x_ini = int(zx0 * W) if bb["bloque"].startswith("ficha") else max(0, cx - crop_w // 2)   # la ficha arranca a la izquierda
            cr = full[max(0, cy - 210):cy + 210, x_ini:x_ini + crop_w]
            sheet.paste(Image.fromarray(np.ascontiguousarray(cr)), (x0, y0 + 2 * ch + 20))
    out = LAB / "VARIANTES_ch06.jpg"
    sheet.save(out, quality=86)
    print(out, sheet.size, flush=True)
    return out


def _lin(c: np.ndarray) -> np.ndarray:
    c = c / 255.0
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def _lum(rgb: np.ndarray) -> np.ndarray:
    li = _lin(rgb.astype(np.float64))
    return 0.2126 * li[..., 0] + 0.7152 * li[..., 1] + 0.0722 * li[..., 2]


ZONAS = {"ficha título": ((0.06, 0.300, 0.95, 0.420), "blanco"), "ficha kicker": ((0.06, 0.258, 0.95, 0.302), "rojo"),
         "sello": ((0.40, 0.40, 0.99, 0.68), "rojo")}


def _zona_rgb(video: Path, a: float, dur: float, zona: tuple) -> np.ndarray:
    """La zona en color, cuadro a cuadro, a la mitad de resolución: [n, h, w, 3]."""
    zx0, zy0, zx1, zy1 = zona
    w, h = int((zx1 - zx0) * 2560) // 4 * 4, int((zy1 - zy0) * 1440) // 4 * 4
    r = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{max(0.0, a):.4f}", "-i", str(video), "-t", f"{dur:.4f}", "-vf",
                        f"crop={w}:{h}:{int(zx0 * 2560)}:{int(zy0 * 1440)},scale={w // 2}:{h // 2},format=rgb24",
                        "-f", "rawvideo", "-"], capture_output=True, check=True)
    return np.frombuffer(r.stdout, np.uint8).reshape(-1, h // 2, w // 2, 3).astype(np.int16)


def _mascara(rgb: np.ndarray, color: str) -> np.ndarray:
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    if color == "blanco":                                 # el dato de la ficha (#f4f1ea)
        return (r > 205) & (g > 200) & (b > 190) & (np.abs(r - b) < 45)
    return (r > 130) & (g < 95) & (b < 105) & (r - g > 70)  # el acento (#c8102e): kicker y sello


def _contraste(rgb: np.ndarray, m: np.ndarray) -> float | None:
    """WCAG del texto contra su fondo inmediato: el recuadro del texto (+6 px) menos el texto dilatado 2 px."""
    if m.sum() < 30:
        return None
    ys, xs = np.where(m)
    y0, y1, x0, x1 = max(0, ys.min() - 6), ys.max() + 7, max(0, xs.min() - 6), xs.max() + 7
    sub, ms = rgb[y0:y1, x0:x1].astype(np.uint8), m[y0:y1, x0:x1]
    dil = ms.copy()
    for dy in (-2, -1, 0, 1, 2):
        for dx in (-2, -1, 0, 1, 2):
            dil |= np.roll(np.roll(ms, dy, 0), dx, 1)
    fondo = ~dil
    if fondo.sum() < 30:
        return None
    lt, lf = float(_lum(sub[ms]).mean()), float(_lum(sub[fondo]).mean())
    return round((max(lt, lf) + 0.05) / (min(lt, lf) + 0.05), 2)


def medidas() -> dict:
    """Por bloque y variante, en el mismo segmento:
    - texto = píxeles del color del texto en su zona (blanco del dato de la ficha; rojo del acento en el kicker y el sello);
    - contraste WCAG = luminancia relativa media del texto contra la de su fondo inmediato (el recuadro del texto menos el
      texto), en el cuadro con más texto;
    - cuadros de entrada = del primer cuadro con ≥ 5 % del texto (descontado el piso de ese color en el fondo, los 0.25 s
      antes del bloque) al primero con ≥ 95 %; salida = del último con ≥ 95 % al
      último con ≥ 5 %;
    - alto de letra a 360 px = alto de mayúscula de Anton (métrica de la fuente) × cuerpo × 360 / 2560."""
    from PIL import ImageFont
    from gfx_config import GFX_FONTS_DIR, gfx_rules
    from script_engine.gfx_project import tc_metrics
    f = ImageFont.truetype(str(GFX_FONTS_DIR / "Anton-Regular.ttf"), 1000)
    cap_em = (f.getbbox("H")[3] - f.getbbox("H")[1]) / 1000
    res: dict = {"_metodo": medidas.__doc__, "_alto_mayuscula_em": round(cap_em, 3)}
    for e in [e for e in VARIANTES if (LAB / "corridas" / e / f"{CAP}_segment_only.mp4").exists()]:
        seg = LAB / "corridas" / e / f"{CAP}_segment_only.mp4"
        fs = VARIANTES[e].split(",")[1]
        res[e] = []
        for b in _bloques(_plan(e)):
            partes = ["ficha título", "ficha kicker"] if b["bloque"].startswith("ficha") else \
                ["sello"] if b["bloque"].startswith("sello") else []
            for parte in partes:
                zona, color = ZONAS[parte]
                a = b["t0"] - 0.3
                fr = _zona_rgb(seg, a, (b["t1"] - b["t0"]) + 0.6, zona)
                ms = _mascara(fr, color)
                cuenta = ms.reshape(len(ms), -1).sum(axis=1).astype(float)
                cuenta = np.maximum(0.0, cuenta - float(np.median(cuenta[:int(0.25 * FPS)])))   # el piso: blancos del fondo antes del bloque
                top = int(cuenta.max())
                on = np.where(cuenta >= 0.05 * top)[0]
                full = np.where(cuenta >= 0.95 * top)[0]
                k = int(np.argmax(cuenta))
                cuerpo = {"ficha título": tc_metrics()["title_px"], "ficha kicker": tc_metrics()["kicker_px"],
                          "sello": gfx_rules.emphasis_stamp_px * {"S2": 2, "S3": 3}.get(fs[:2], 1)}[parte]
                res[e].append({"bloque": f"{b['bloque']} · {parte}", "contraste_wcag": _contraste(fr[k], ms[k]),
                               "cuadros_entrada": int(full[0] - on[0]) if len(on) and len(full) else None,
                               "cuadros_salida": int(on[-1] - full[-1]) if len(on) and len(full) else None,
                               "pixeles_texto": top, "cuerpo_px_2560": cuerpo,
                               "alto_mayuscula_px_360": round(cuerpo * cap_em * 360 / 2560, 1)})
    for e, filas in list(res.items()):
        if isinstance(filas, list):
            for r in filas:
                r["pasa_4_5"] = None if r["contraste_wcag"] is None else bool(r["contraste_wcag"] >= 4.5)
    (LAB / "medidas.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in res.items() if not k.startswith("_")}, ensure_ascii=False)[:3500], flush=True)
    return res


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    os.chdir(ROOT)
    cmd = sys.argv[1]
    if cmd == "render":
        render(sys.argv[2])
    else:
        {"todas": todas, "clips": clips, "hoja": hoja, "medidas": medidas}[cmd]()
