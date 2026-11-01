"""F68: arma la tabla por foto de F68_REPORT.md desde el manifest y los `.llamada.json`; deja hoja_todas.jpg. Sin llamadas."""
import json
import re
from pathlib import Path

from PIL import Image, ImageDraw

R = Path(__file__).resolve().parents[3]
AQUI = Path(__file__).resolve().parent
A = R / "output" / "123bbb64-9fca-4395-8bf4-57d60e219ef1" / "assets"
filas, res, usd, seg, fotos = [], {"nb2_lite": 0, "seedream45_respaldo": 0}, 0.0, 0.0, []
for d in sorted(p for p in A.iterdir() if p.is_dir() and re.fullmatch(r"ch\d+_(flux|veo)", p.name)):
    for l in sorted(d.glob("*.llamada.json")):
        r = json.loads(l.read_text(encoding="utf-8"))
        ll = r["llamadas"]
        motor = "seedream45_respaldo" if ll.get("seedream45_respaldo", {}).get("estado") == "ok" else "nb2_lite"
        f = ll[motor]
        motivo = ll["nb2_lite"].get("mensaje", "") if motor != "nb2_lite" else ""
        u = 0.04 if motor != "nb2_lite" else 0.042
        tipo = "edit" if f["endpoint"].endswith("/edit") else "t2i"
        n = len(f["referencias_md5"])
        res[motor] += 1
        usd += u
        seg += f.get("segundos") or 0
        filas.append(f"| {r['foto']} | {motor} | {tipo} ({n} ref.) | {'sí: ' + motivo if motivo else 'no'} | {f.get('segundos')} | {u:.3f} |")
        fotos.append(d / r["foto"])
(AQUI / "TABLA_FOTOS.md").write_text(
    "| Foto | Motor | Llamada | Respaldo y motivo | s | US$ (estimado) |\n|---|---|---|---|---|---|\n" + "\n".join(filas) + "\n", encoding="utf-8")
print(len(filas), res, round(usd, 3), round(seg))
W, H, C = 320, 180, 10
hoja = Image.new("RGB", (W * C, (H + 18) * ((len(fotos) + C - 1) // C)), (20, 20, 20))
dr = ImageDraw.Draw(hoja)
for i, p in enumerate(fotos):
    im = Image.open(p).convert("RGB")
    im.thumbnail((W, H))
    x, y = (i % C) * W, (i // C) * (H + 18)
    hoja.paste(im, (x, y + 18))
    dr.text((x + 3, y + 3), p.stem, fill=(255, 255, 255))
hoja.save(AQUI / "hoja_todas.jpg", quality=80)
