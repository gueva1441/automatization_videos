# -*- coding: utf-8 -*-
"""F46b - hojas de contactos A | B1 | C0 a/b | C1 a/b | C2 a/b del cap 2 de Wittenoom + costos f46b-lab.

Uso (desde cualquier carpeta, con el python del sistema):
  python lab/hyperframes/f46/f46b/f46b_hoja.py             # hoja_01-04.jpg .. hoja_13-16.jpg
  python lab/hyperframes/f46/f46b/f46b_hoja.py --costos    # tabla Markdown de video_id "f46b-lab" -> COSTOS.md
Solo lee; escribe unicamente dentro de lab/hyperframes/f46/f46b/. Sin llamadas a API.
"""
import argparse
import json
import sys
from collections import OrderedDict
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[4]
F46 = RAIZ / "lab" / "hyperframes" / "f46"
F46B = F46 / "f46b"
VIDEO = "123bbb64-9fca-4395-8bf4-57d60e219ef1"
A_DIR = RAIZ / "output" / VIDEO / "assets" / "ch02_flux"
PASOS = RAIZ / "data" / "scripts" / "_steps" / VIDEO / "03_visual.json"
COSTOS = RAIZ / "data" / "cost_history.json"
C0_JSON = F46B / "C0.json"
# (clave, encabezado, carpeta, sufijo)
COLS = [("A", "A", None, ""), ("B1", "B1", F46 / "B1", ""),
        ("C0a", "C0 a", F46B / "C0", "_a"), ("C0b", "C0 b", F46B / "C0", "_b"),
        ("C1a", "C1 a", F46B / "C1", "_a"), ("C1b", "C1 b", F46B / "C1", "_b"),
        ("C2a", "C2 a", F46B / "C2", "_a"), ("C2b", "C2 b", F46B / "C2", "_b")]


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


def anios():
    """Año de cada foto desde C0.json -> image_prompts[i]["anio"]; '?' si falta."""
    try:
        d = leer_json_tolerante(C0_JSON)
        ips = d["image_prompts"] if isinstance(d, dict) else d
        out = []
        for p in ips:
            v = p.get("anio") if isinstance(p, dict) else None
            out.append(str(v) if v not in (None, "") else "?")
        return out
    except Exception:
        return []


def fuente(tam):
    from PIL import ImageFont
    for f in ("C:/Windows/Fonts/arial.ttf",):
        try:
            return ImageFont.truetype(f, tam)
        except OSError:
            pass
    return ImageFont.load_default()


def rutas_celda(col, nn):
    """(ruta de la imagen, ruta del .rechazada.txt)"""
    clave, _, carpeta, suf = col
    if clave == "A":
        return A_DIR / f"ch02_img_{nn:02d}_graded.png", A_DIR / f"ch02_img_{nn:02d}.rechazada.txt"
    return (carpeta / f"ch02_img_{nn:02d}{suf}_graded.png",
            carpeta / f"ch02_img_{nn:02d}.rechazada.txt")


def hoja(desde, ancl, anio, ancho_total, salida):
    from PIL import Image, ImageDraw
    n = 4
    k = len(COLS)
    m = 10                      # margen
    rot_w = 170                 # columna de rotulos
    cw = (ancho_total - rot_w - m * (k + 1)) // k
    ch = round(cw * 1440 / 2560)
    enc_h = 36
    ancho = rot_w + m * (k + 1) + cw * k
    alto = enc_h + n * (ch + m) + m
    im = Image.new("RGB", (ancho, alto), (24, 24, 24))
    dr = ImageDraw.Draw(im)
    f_enc, f_rot, f_cel, f_anio = fuente(22), fuente(15), fuente(22), fuente(20)
    for j, col in enumerate(COLS):
        dr.text((rot_w + m * (j + 2) + cw * j + 4, 7), col[1], fill=(235, 235, 235), font=f_enc)
    for i in range(n):
        nn = desde + i
        y = enc_h + i * (ch + m)
        a = ancl[nn - 1] if nn - 1 < len(ancl) else ""
        pal = " ".join(a.split()[:8])
        an = anio[nn - 1] if nn - 1 < len(anio) else "?"
        dr.text((m, y + 2), f"Foto {nn:02d}", fill=(255, 210, 90), font=f_enc)
        dr.text((m, y + 28), f"Año: {an}", fill=(130, 220, 255), font=f_anio)
        linea, ys = "", y + 56
        for w in pal.split():
            if dr.textlength(linea + " " + w, font=f_rot) > rot_w - m:
                dr.text((m, ys), linea.strip(), fill=(200, 200, 200), font=f_rot)
                ys += 19
                linea = ""
            linea += " " + w
        if linea.strip():
            dr.text((m, ys), linea.strip(), fill=(200, 200, 200), font=f_rot)
        for j, col in enumerate(COLS):
            x = rot_w + m * (j + 2) + cw * j
            p, rech = rutas_celda(col, nn)
            if p.exists():
                with Image.open(p) as f:
                    f = f.convert("RGB").resize((cw, ch), Image.LANCZOS)
                im.paste(f, (x, y))
            else:
                txt = "rechazada" if rech.exists() else "falta"
                dr.rectangle([x, y, x + cw - 1, y + ch - 1], fill=(110, 110, 110))
                tw = dr.textlength(txt, font=f_cel)
                dr.text((x + (cw - tw) / 2, y + ch / 2 - 12), txt, fill=(240, 240, 240), font=f_cel)
    im.save(salida, "JPEG", quality=88)
    return im.size


def cmd_hojas(ancho):
    ancl, anio = anclas(), anios()
    for desde in (1, 5, 9, 13):
        s = F46B / f"hoja_{desde:02d}-{desde + 3:02d}.jpg"
        w, h = hoja(desde, ancl, anio, ancho, s)
        print(f"{s.relative_to(RAIZ)}  {w}x{h}")


def cmd_costos():
    hist = leer_json_tolerante(COSTOS)
    reps = [r for r in hist if r.get("video_id") == "f46b-lab"]
    if not reps:
        print("sin entradas f46b-lab")
        return
    grupos = OrderedDict()
    for r in reps:
        for e in r.get("entries", []):
            grupos.setdefault(e.get("service", "?"), []).append(e)
    L = ["# F46b - costos (video_id f46b-lab)", "",
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
    (F46B / "COSTOS.md").write_text(txt, encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--costos", action="store_true", help="tabla de costos f46b-lab en vez de las hojas")
    ap.add_argument("--ancho", type=int, default=3840, help="ancho de cada hoja (def. 3840, máx. 3840)")
    a = ap.parse_args()
    if a.costos:
        cmd_costos()
    else:
        cmd_hojas(min(a.ancho, 3840))


if __name__ == "__main__":
    sys.exit(main())
