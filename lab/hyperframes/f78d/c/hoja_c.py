"""F78d Etapa C: hoja lab/hyperframes/f78d/ETAPA_C.html — por foto: referencia (madres) | vieja (_previas_f78d) | nueva + subject
nuevo y motivo; en los clips, además un cuadro del clip viejo y del nuevo (ffmpeg, segundo 4). Solo lectura.
Uso: PYTHONIOENCODING=utf-8 python lab/hyperframes/f78d/c/hoja_c.py"""
import base64
import html
import io
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

R = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(R))
from script_engine import m03_visual as m3  # noqa: E402

TID = "c4934b7d-3f54-448f-ba5f-539dc744f0d8"
AQUI = Path(__file__).parent
lista = json.loads((AQUI / "lista.json").read_text(encoding="utf-8"))
movidos = json.loads((AQUI / "movidos.json").read_text(encoding="utf-8"))
costo = json.loads((AQUI / "costo.json").read_text(encoding="utf-8"))
visual = json.loads((m3.STEPS_DIR / TID / "03_visual.json").read_text(encoding="utf-8"))
items = {f["foto"]: f["item"] for f in m3._fotos_con_persona(visual)}
vis_caps = {c["chapter_number"]: c for c in visual["chapters"]}


def img(p, ancho=520):
    p = Path(p) if p else None
    if not p or not p.exists():
        return '<div class="falta">—</div>'
    with Image.open(p) as im:
        im = im.convert("RGB")
        im.thumbnail((ancho, ancho))
        b = io.BytesIO()
        im.save(b, "JPEG", quality=80)
    return f'<img src="data:image/jpeg;base64,{base64.b64encode(b.getvalue()).decode()}" alt="{html.escape(p.name)}">'


def cuadro(mp4, seg=4):
    if not mp4 or not Path(mp4).exists():
        return None
    out = Path(tempfile.mkdtemp()) / "c.png"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(seg), "-i", str(mp4), "-frames:v", "1", str(out)], check=False)
    return out if out.exists() else None


def subj(it):
    try:
        return (json.loads((it or {}).get("raw_llm_prompt") or "{}") or {}).get("subject") or ""
    except ValueError:
        return ""


S = []
for f in lista:
    viejos = movidos.get(f["foto"], [])
    vieja = next((p for p in viejos if p.endswith(f"{f['foto']}.png")), None)
    refs = "".join(f"<figure>{img(m['path'], 260)}<figcaption>{html.escape(Path(m['path']).name)}</figcaption></figure>"
                   for m in f["madres"]) or '<div class="falta">sin madre (t2i)</div>'
    extra = ""
    if f["clip"]:
        mp4_v = next((p for p in viejos if p.endswith(".mp4")), None)
        mp4_n = Path(f["path"]).with_name(f"{f['clip']}_clip_01.mp4")
        extra = (f"<div class='fila3'><figure>{img(cuadro(mp4_v))}<figcaption>clip viejo, s 4</figcaption></figure>"
                 f"<figure>{img(cuadro(mp4_n))}<figcaption>clip nuevo, s 4 ({html.escape(mp4_n.name)})</figcaption></figure>"
                 f"<div><p class='nota'>movimiento nuevo:</p><pre>{html.escape(vis_caps[int(f['clip'][2:])].get('video_prompt') or '')}</pre></div></div>")
    it = items.get(f["foto"]) or {}
    S.append(f"<section><h3>{f['foto']} <span class='nota'>{html.escape(' · '.join(f['motivo']))}</span></h3>"
             f"<div class='fila3'><div class='refs'>{refs}</div>"
             f"<figure>{img(vieja)}<figcaption>vieja (_previas_f78d)</figcaption></figure>"
             f"<figure>{img(f['path'])}<figcaption>nueva</figcaption></figure></div>{extra}"
             f"<p><b>persona</b> {html.escape(', '.join(m3._personas_de(it)) or '—')} · <b>marca</b> "
             f"{html.escape(it.get('_rasgos_refill') or it.get('aspecto_fuente') or '—')}</p>"
             f"<p><b>subject nuevo</b> {html.escape(subj(it) or '(sin casilleros: foto de clip sin persona)')}</p>"
             f"<details><summary>prompt</summary><pre>{html.escape(f['prompt'] or '')}</pre></details></section>")
cost = "".join(f"<li>{html.escape(k)}: US$ {v:.4f}</li>" for k, v in costo["por_servicio"].items())
doc = f"""<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>F78d Etapa C</title><style>
:root{{--bg:#f6f5f2;--fg:#1d1d1b;--mut:#6b6a66;--card:#fff;--line:#dedcd6}}
@media (prefers-color-scheme:dark){{:root{{--bg:#151514;--fg:#ecebe7;--mut:#a3a29d;--card:#1f1f1d;--line:#353531}}}}
body{{background:var(--bg);color:var(--fg);font:15px/1.45 system-ui,sans-serif;margin:0 auto;padding:16px;max-width:1600px}}
h1{{font-size:22px}} h3{{margin:0 0 6px;font-size:16px}} section{{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:12px;margin:12px 0}}
.fila3{{display:grid;grid-template-columns:1fr 2fr 2fr;gap:10px;margin:6px 0}} .refs{{display:grid;gap:6px}} figure{{margin:0}}
img{{width:100%;height:auto;border-radius:4px}} figcaption,.nota{{color:var(--mut);font-size:13px;font-weight:normal}}
pre{{white-space:pre-wrap;font-size:12px;background:var(--bg);padding:8px;border-radius:4px}}
.falta{{padding:30px;text-align:center;color:var(--mut);border:1px dashed var(--line)}} @media (max-width:800px){{.fila3{{grid-template-columns:1fr}}}}
</style></head><body><h1>F78d · Etapa C de Colza: fotos /edit y clips del gancho y ch07 con Lite</h1>
<p class="nota">{len(lista)} fotos regeneradas por el camino de producción (asset_manager.process_script). Lo viejo está en
&lt;carpeta del cap&gt;/_previas_f78d/. Costo total US$ {costo['total_usd']:.4f}:</p><ul>{cost}</ul>
<p class="nota">PARADA: Omar revisa en QA Studio. Sin render.</p>{''.join(S)}</body></html>"""
(AQUI.parent / "ETAPA_C.html").write_text(doc, encoding="utf-8")
print("ETAPA_C.html", len(doc) // 1024, "KB")
