# -*- coding: utf-8 -*-
"""F46 - hojas de contactos A | B1 | B2 del cap 2 de Wittenoom + tabla de costos f46-lab.

Uso (desde cualquier carpeta, con el python del sistema):
  python lab/hyperframes/f46/f46_hoja.py             # genera hoja_01-04..hoja_13-16.jpg
  python lab/hyperframes/f46/f46_hoja.py --costos    # tabla Markdown de video_id "f46-lab" -> COSTOS.md
Solo lee; escribe unicamente dentro de lab/hyperframes/f46/. Sin llamadas a API.
"""
import argparse
import json
import sys
from collections import OrderedDict
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
F46 = RAIZ / "lab" / "hyperframes" / "f46"
VIDEO = "123bbb64-9fca-4395-8bf4-57d60e219ef1"
A_DIR = RAIZ / "output" / VIDEO / "assets" / "ch02_flux"
PASOS = RAIZ / "data" / "scripts" / "_steps" / VIDEO / "03_visual.json"
COSTOS = RAIZ / "data" / "cost_history.json"
COLS = [("A", "A (hoy)"), ("B1", "B1 (entrada nueva)"), ("B2", "B2 (entrada + estructura)")]


def leer_json_tolerante(ruta):
    raw = ruta.read_bytes()
    try:
        txt = raw.decode("utf-8")
    except UnicodeDecodeError:
        txt = raw.decode("cp1252", errors="replace")  # el historial mezcla codificaciones
    return json.loads(txt)


def anclas():
    d = leer_json_tolerante(PASOS)
    cap = next(c for c in d["chapters"] if c.get("chapter_number") == 2)
    return [p.get("narration_anchor", "") for p in cap["image_prompts"]]


def fuente(tam):
    from PIL import ImageFont
    for f in ("C:/Windows/Fonts/arial.ttf",):
        try:
            return ImageFont.truetype(f, tam)
        except OSError:
            pass
    return ImageFont.load_default()


def ruta_celda(var, nn):
    if var == "A":
        return A_DIR / f"ch02_img_{nn:02d}_graded.png"
    return F46 / var / f"ch02_img_{nn:02d}_graded.png"


def hoja(desde, ancl, ancho_total, salida):
    from PIL import Image, ImageDraw
    n = 4
    m = 12                      # margen
    rot_w = 190                 # columna de rotulos
    cw = (ancho_total - rot_w - m * 4) // 3
    ch = round(cw * 1440 / 2560)
    enc_h = 44
    ancho = rot_w + m * 4 + cw * 3
    alto = enc_h + n * (ch + m) + m
    im = Image.new("RGB", (ancho, alto), (24, 24, 24))
    dr = ImageDraw.Draw(im)
    f_enc, f_rot, f_cel = fuente(24), fuente(17), fuente(28)
    for j, (_, tit) in enumerate(COLS):
        dr.text((rot_w + m * (j + 2) + cw * j + 6, 10), tit, fill=(235, 235, 235), font=f_enc)
    for i in range(n):
        nn = desde + i
        y = enc_h + i * (ch + m)
        # rotulo: n.º y primeras 8 palabras del ancla
        a = ancl[nn - 1] if nn - 1 < len(ancl) else ""
        pal = " ".join(a.split()[:8])
        dr.text((m, y + 4), f"Foto {nn:02d}", fill=(255, 210, 90), font=f_enc)
        linea, ys = "", y + 40
        for w in pal.split():
            if dr.textlength(linea + " " + w, font=f_rot) > rot_w - m:
                dr.text((m, ys), linea.strip(), fill=(200, 200, 200), font=f_rot)
                ys += 22
                linea = ""
            linea += " " + w
        if linea.strip():
            dr.text((m, ys), linea.strip(), fill=(200, 200, 200), font=f_rot)
        for j, (var, _) in enumerate(COLS):
            x = rot_w + m * (j + 2) + cw * j
            p = ruta_celda(var, nn)
            if p.exists():
                with Image.open(p) as f:
                    f = f.convert("RGB").resize((cw, ch), Image.LANCZOS)
                im.paste(f, (x, y))
            else:
                rech = F46 / var / f"ch02_img_{nn:02d}.rechazada.txt"
                txt = "rechazada" if rech.exists() else "falta"
                dr.rectangle([x, y, x + cw - 1, y + ch - 1], fill=(110, 110, 110))
                tw = dr.textlength(txt, font=f_cel)
                dr.text((x + (cw - tw) / 2, y + ch / 2 - 16), txt, fill=(240, 240, 240), font=f_cel)
    im.save(salida, "JPEG", quality=88)
    return im.size


def cmd_hojas(ancho):
    ancl = anclas()
    for desde in (1, 5, 9, 13):
        s = F46 / f"hoja_{desde:02d}-{desde + 3:02d}.jpg"
        w, h = hoja(desde, ancl, ancho, s)
        print(f"{s.relative_to(RAIZ)}  {w}x{h}")


def cmd_costos():
    hist = leer_json_tolerante(COSTOS)
    reps = [r for r in hist if r.get("video_id") == "f46-lab"]
    if not reps:
        print("sin entradas f46-lab")
        return
    grupos = OrderedDict()
    for r in reps:
        for e in r.get("entries", []):
            grupos.setdefault(e.get("service", "?"), []).append(e)
    L = ["# F46 - costos (video_id f46-lab)", "",
         "| servicio | descripción | costo US$ |", "|---|---|---:|"]
    total = 0.0
    for srv, es in grupos.items():
        sub = 0.0
        for e in es:
            c = float(e.get("total_cost", 0) or 0)
            sub += c
            d = str(e.get("description", "")).replace("|", "/")
            d = d if len(d) <= 60 else d[:57] + "..."
            L.append(f"| {srv} | {d} | {c:.4f} |")
        L.append(f"| **{srv} - subtotal** | {len(es)} entradas | **{sub:.4f}** |")
        total += sub
    L += [f"| **TOTAL** | {len(reps)} reportes | **{total:.4f}** |", ""]
    txt = "\n".join(L)
    print(txt)
    (F46 / "COSTOS.md").write_text(txt, encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--costos", action="store_true", help="tabla de costos f46-lab en vez de las hojas")
    ap.add_argument("--ancho", type=int, default=2560, help="ancho máximo de cada hoja (def. 2560)")
    a = ap.parse_args()
    if a.costos:
        cmd_costos()
    else:
        cmd_hojas(min(a.ancho, 2560))


if __name__ == "__main__":
    sys.exit(main())
