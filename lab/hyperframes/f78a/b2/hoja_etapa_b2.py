"""F78b Etapa B: hoja lab/hyperframes/f78a/ETAPA_B2.html — estados.json, variantes F78a vs F78b, 4 fotos de control F78a vs
F78b con su prompt. Solo lectura; imágenes embebidas (JPEG 720 px). Uso: PYTHONIOENCODING=utf-8 python lab/hyperframes/f78a/b2/hoja_etapa_b2.py"""
import base64
import html
import io
import json
import re
from pathlib import Path

from PIL import Image

R = Path(__file__).resolve().parents[4]
TID = "c4934b7d-3f54-448f-ba5f-539dc744f0d8"
OUT = R / "output" / TID
MADRES = OUT / "foto_madre"
PREV = MADRES / "_previas_f78b"
AQUI = Path(__file__).parent
CONTROL = [("ch01_supp_05", "Arcadio, juicio 1989"), ("ch06_img_14", "Arcadio, calculadora 1989"),
           ("ch04_img_12", "Lozano 1981"), ("ch07_supp_07", "Carmen 2000")]


def img(p: Path, ancho: int = 720) -> str:
    if not p.exists():
        return '<div class="falta">sin archivo</div>'
    with Image.open(p) as im:
        im = im.convert("RGB")
        im.thumbnail((ancho, ancho))
        b = io.BytesIO()
        im.save(b, "JPEG", quality=82)
    return f'<img src="data:image/jpeg;base64,{base64.b64encode(b.getvalue()).decode()}" alt="{html.escape(p.name)}">'


def texto(p: Path) -> str:
    return p.read_text(encoding="utf-8") if p.exists() else ""


def prompt_llamada(p: Path) -> str:
    j = p.with_name(p.stem + ".llamada.json")
    if not j.exists():
        return ""
    d = json.loads(j.read_text(encoding="utf-8"))
    return "\n\n".join(f"[{k}] {v.get('texto', '')}" for k, v in (d.get("llamadas") or {}).items())


db = json.loads((R / "data" / "topics_db.json").read_text(encoding="utf-8"))
topic = next(t for t in db["topics"] if t.get("id") == TID)
est = json.loads((MADRES / "estados.json").read_text(encoding="utf-8"))
costo = json.loads((AQUI / "costo_etapa_b.json").read_text(encoding="utf-8"))
S = ["<h2>1 · estados.json (una llamada, 6 filas)</h2><table><tr><th>persona</th><th>tramo</th><th>condición del canon</th>"
     "<th>estado_visible</th></tr>"]
cond = {(e["name"], e["tramo"]): e["condition"] for e in est["entrada"]}
for e in est["estados"]:
    S.append(f"<tr><td>{html.escape(e['name'])}</td><td>{e['tramo']}</td><td>{html.escape(cond[(e['name'], e['tramo'])])}</td>"
             f"<td><b>{html.escape(e['estado_visible']) or '— (vacío)'}</b></td></tr>")
S.append("</table>")
S.append("<h2>2 · Variantes: F78a (condición cruda, edad en rango) vs F78b (estado visible, edad exacta)</h2>")
for p in topic["documented_people"]:
    for v in p.get("foto_madre_variantes") or []:
        nueva = Path(v["path"])
        vieja = PREV / nueva.name
        S.append(f"<section><h3>{html.escape(p['name'])} @ {html.escape(v['clave'])}</h3>"
                 f"<p class='nota'>{len(v['fotos'])} fotos: {', '.join(v['fotos'])}</p>"
                 f"<div class='tri'><figure>{img(Path(p['foto_madre']))}<figcaption>madre limpia (sin cambio)</figcaption></figure>"
                 f"<figure>{img(vieja)}<figcaption>F78a</figcaption></figure>"
                 f"<figure>{img(nueva)}<figcaption>F78b</figcaption></figure></div>"
                 f"<details><summary>prompts</summary><pre>F78a\n{html.escape(texto(vieja.with_suffix('.prompt.txt')))}\n\nF78b\n"
                 f"{html.escape(texto(nueva.with_suffix('.prompt.txt')))}</pre></details></section>")
S.append("<h2>3 · 4 fotos de control: F78a vs F78b (mismo prompt de escena)</h2>")
for stem, que in CONTROL:
    d = OUT / "assets" / f"{stem[:4]}_flux"
    S.append(f"<section><h3>{stem} <span class='rol'>{que}</span></h3>"
             f"<div class='par'><figure>{img(d / '_previas_f78b' / f'{stem}.png')}<figcaption>F78a</figcaption></figure>"
             f"<figure>{img(d / f'{stem}.png')}<figcaption>F78b</figcaption></figure></div>"
             f"<details><summary>prompt (F78b)</summary><pre>{html.escape(prompt_llamada(d / f'{stem}.png'))}</pre></details></section>")
doc = f"""<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>F78b Etapa B</title><style>
:root{{--bg:#f6f5f2;--fg:#1d1d1b;--mut:#6b6a66;--card:#fff;--line:#dedcd6}}
@media (prefers-color-scheme:dark){{:root{{--bg:#151514;--fg:#ecebe7;--mut:#a3a29d;--card:#1f1f1d;--line:#353531}}}}
body{{background:var(--bg);color:var(--fg);font:15px/1.45 system-ui,sans-serif;margin:0 auto;padding:16px;max-width:1600px}}
h1{{font-size:22px}} h2{{margin-top:36px;border-bottom:1px solid var(--line);padding-bottom:6px}} h3{{margin:0 0 6px;font-size:16px}}
section{{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:12px;margin:12px 0}}
.par{{display:grid;grid-template-columns:1fr 1fr;gap:10px}} .tri{{display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px}}
figure{{margin:0}} img{{width:100%;height:auto;border-radius:4px}} figcaption,.nota,.rol{{color:var(--mut);font-size:13px}}
table{{border-collapse:collapse;width:100%;background:var(--card)}} td,th{{border:1px solid var(--line);padding:6px;text-align:left;vertical-align:top;font-size:14px}}
pre{{white-space:pre-wrap;font-size:12px;background:var(--bg);padding:8px;border-radius:4px}} .falta{{padding:40px;text-align:center;color:var(--mut);border:1px dashed var(--line)}}
@media (max-width:640px){{.par,.tri{{grid-template-columns:1fr}}}}
</style></head><body>
<h1>F78b · Etapa B · Colza: estado visible + edad exacta</h1>
<p class="nota">Tema {TID}. Las madres limpias y los rasgos no cambiaron. Costo real de la etapa: <b>US$ {costo['total_usd']:.4f}</b>.
PARADA: Omar y el analista miran; la Etapa C de F78a no corrió. Las otras fotos de cada variante siguen con la foto de F78a hasta la Etapa C.</p>
{''.join(S)}
</body></html>"""
(R / "lab" / "hyperframes" / "f78a" / "ETAPA_B2.html").write_text(doc, encoding="utf-8")
print("ETAPA_B2.html", len(doc) // 1024, "KB")
