"""F78a Etapa B: hoja de contacto lab/hyperframes/f78a/ETAPA_B.html (madres viejas vs nuevas, rasgos, variantes, 6 fotos de
control antes/después con su prompt). Solo lectura; las imágenes van embebidas (JPEG 720 px) para abrirla en cualquier lado.
Uso: PYTHONIOENCODING=utf-8 python lab/hyperframes/f78a/b/hoja_etapa_b.py"""
import base64
import html
import io
import json
import sys
from pathlib import Path

from PIL import Image

R = Path(__file__).resolve().parents[4]
TID = "c4934b7d-3f54-448f-ba5f-539dc744f0d8"
OUT = R / "output" / TID
MADRES = OUT / "foto_madre"
PREV = MADRES / "_previas_f78a"
AQUI = Path(__file__).parent
CONTROL = [("ch01_supp_05", "Arcadio, juicio 1989"), ("ch06_img_14", "Arcadio, calculadora 1989"),
           ("ch03_img_11", "Sancho Rof 1981"), ("ch03_img_14", "Muro 1981"), ("ch05_img_12", "Angela 1985"),
           ("ch07_supp_07", "Carmen 2000")]
sys.path.insert(0, str(R))
import foto_madre as fm  # noqa: E402


def img(p: Path, ancho: int = 720) -> str:
    if not p.exists():
        return '<div class="falta">sin archivo</div>'
    with Image.open(p) as im:
        im = im.convert("RGB")
        im.thumbnail((ancho, ancho))
        b = io.BytesIO()
        im.save(b, "JPEG", quality=82)
    return f'<img src="data:image/jpeg;base64,{base64.b64encode(b.getvalue()).decode()}" alt="{html.escape(p.name)}">'


def prompt_de(p: Path) -> str:
    t = p.with_suffix(".prompt.txt")
    return t.read_text(encoding="utf-8") if t.exists() else ""


def llamada(p: Path) -> str:
    j = p.with_name(p.stem + ".llamada.json")
    if not j.exists():
        return ""
    d = json.loads(j.read_text(encoding="utf-8"))
    return json.dumps(d, ensure_ascii=False, indent=1)[:3000]


db = json.loads((R / "data" / "topics_db.json").read_text(encoding="utf-8"))
topic = next(t for t in db["topics"] if t.get("id") == TID)
rasgos = json.loads((MADRES / "rasgos.json").read_text(encoding="utf-8"))["personas"]
costo = json.loads((AQUI / "costo_etapa_b.json").read_text(encoding="utf-8")) if (AQUI / "costo_etapa_b.json").exists() else {}
personas = [p for p in topic["documented_people"] if p.get("foto_madre")]

S = []
S.append("<h2>1 · Madres: antes y ahora</h2><p class='nota'>Antes: canon + grupo (10 de 15 personas = «a middle-aged Spanish man»). "
         "Ahora: canon + <b>rasgos</b> inventados (una llamada con todas) + grupo. Rasgos = invento para distinguirlas, no dato.</p>")
for p in personas:
    slug = fm._slug(p["name"])
    nueva = Path(p["foto_madre"])
    S.append(f"<section><h3>{html.escape(p['name'])} <span class='rol'>{html.escape(p.get('role') or '')}</span></h3>"
             f"<p class='rasgos'>rasgos: <b>{html.escape((rasgos.get(p['name']) or {}).get('rasgos', '—'))}</b></p>"
             f"<div class='par'><figure>{img(PREV / f'{slug}.png')}<figcaption>antes</figcaption></figure>"
             f"<figure>{img(nueva)}<figcaption>ahora</figcaption></figure></div>"
             f"<details><summary>prompts</summary><pre>ANTES\n{html.escape(prompt_de(PREV / f'{slug}.png'))}\n\nAHORA\n"
             f"{html.escape(prompt_de(nueva))}</pre></details></section>")

S.append("<h2>2 · Variantes (edit de la madre limpia, cintura para arriba)</h2>")
for p in personas:
    for v in p.get("foto_madre_variantes") or []:
        vp = Path(v["path"])
        S.append(f"<section><h3>{html.escape(p['name'])} @ {html.escape(v['clave'])}</h3>"
                 f"<p class='nota'>tramo {v['tramo'] or '—'} · edad {v['edad'] if v['edad'] is not None else '— (la de la madre)'} · "
                 f"{len(v['fotos'])} fotos: {', '.join(v['fotos'])}</p>"
                 f"<div class='par'><figure>{img(Path(p['foto_madre']))}<figcaption>madre limpia</figcaption></figure>"
                 f"<figure>{img(vp)}<figcaption>variante</figcaption></figure></div>"
                 f"<details><summary>prompt</summary><pre>{html.escape(prompt_de(vp))}</pre></details></section>")

S.append("<h2>3 · Las 6 fotos de control (mismo prompt, madre nueva)</h2>")
for stem, que in CONTROL:
    d = OUT / "assets" / f"{stem[:4]}_flux"
    S.append(f"<section><h3>{stem} <span class='rol'>{que}</span></h3>"
             f"<div class='par'><figure>{img(d / '_previas_f78a' / f'{stem}.png')}<figcaption>antes</figcaption></figure>"
             f"<figure>{img(d / f'{stem}.png')}<figcaption>después</figcaption></figure></div>"
             f"<details><summary>llamada (después)</summary><pre>{html.escape(llamada(d / f'{stem}.png'))}</pre></details></section>")

total = costo.get("total_usd")
doc = f"""<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>F78a Etapa B</title><style>
:root{{--bg:#f6f5f2;--fg:#1d1d1b;--mut:#6b6a66;--card:#fff;--line:#dedcd6}}
@media (prefers-color-scheme:dark){{:root{{--bg:#151514;--fg:#ecebe7;--mut:#a3a29d;--card:#1f1f1d;--line:#353531}}}}
body{{background:var(--bg);color:var(--fg);font:15px/1.45 system-ui,sans-serif;margin:0;padding:16px;max-width:1500px;margin:auto}}
h1{{font-size:22px}} h2{{margin-top:36px;border-bottom:1px solid var(--line);padding-bottom:6px}} h3{{margin:0 0 6px;font-size:16px}}
section{{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:12px;margin:12px 0}}
.par{{display:grid;grid-template-columns:1fr 1fr;gap:10px}} figure{{margin:0}} img{{width:100%;height:auto;border-radius:4px}}
figcaption,.nota,.rol{{color:var(--mut);font-size:13px}} .rol{{font-weight:normal}} .rasgos{{margin:4px 0 8px}}
pre{{white-space:pre-wrap;font-size:12px;background:var(--bg);padding:8px;border-radius:4px}} .falta{{padding:40px;text-align:center;color:var(--mut);border:1px dashed var(--line)}}
@media (max-width:640px){{.par{{grid-template-columns:1fr}}}}
</style></head><body>
<h1>F78a · Etapa B · Colza (síndrome del aceite tóxico)</h1>
<p class="nota">Tema {TID}. Madres de persona con identidad propia + variante por tramo de estado y edad. Costo real de la etapa:
<b>US$ {total:.4f}</b>. PARADA: Omar mira; la Etapa C (regenerar todas las /edit con madre cambiada) no corrió.</p>
{''.join(S)}
</body></html>""" if total is not None else "<p>sin costo_etapa_b.json</p>"
(R / "lab" / "hyperframes" / "f78a" / "ETAPA_B.html").write_text(doc, encoding="utf-8")
print("ETAPA_B.html", len(doc) // 1024, "KB")
