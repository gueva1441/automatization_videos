"""F78c Etapa B: hoja lab/hyperframes/f78c/ETAPA_F78c.html — por foto: referencia | V0 (producción) | V1 (prompt nuevo + Lite) |
V2 (prompt nuevo + Nano Banana 2 completo), con los dos prompts debajo; y la tabla foto → subject viejo → subject nuevo
(b/tabla_subject.md). Solo lectura. Uso: PYTHONIOENCODING=utf-8 python lab/hyperframes/f78c/b/hoja_f78c.py"""
import base64
import html
import io
import json
from pathlib import Path

from PIL import Image

R = Path(__file__).resolve().parents[4]
AQUI = Path(__file__).parent
res = json.loads((AQUI / "resultados.json").read_text(encoding="utf-8"))
costo = json.loads((AQUI / "costo.json").read_text(encoding="utf-8"))["servicios"]


def img(p, ancho=640):
    p = Path(p) if p else None
    if not p or not p.exists():
        return '<div class="falta">—</div>'
    with Image.open(p) as im:
        im = im.convert("RGB")
        im.thumbnail((ancho, ancho))
        b = io.BytesIO()
        im.save(b, "JPEG", quality=82)
    return f'<img src="data:image/jpeg;base64,{base64.b64encode(b.getvalue()).decode()}" alt="{html.escape(p.name)}">'


def sujeto(cas):
    return (cas or {}).get("subject") or ""


S, tabla = [], ["| foto | persona vieja → nueva | subject viejo | subject nuevo |", "|---|---|---|---|"]
for foto, r in res.items():
    ref = r["referencias"][0]["path"] if r["referencias"] else None
    refs = ", ".join(Path(x["path"]).name for x in r["referencias"]) or "sin referencia"
    v = {k: (r.get(k) or {}) for k in ("V1", "V2")}
    est = lambda k: "" if not v[k] else (v[k]["estado"] if v[k]["estado"] == "ok" else f"{v[k]['estado']}: {v[k].get('motivo', '')[:200]}")  # noqa: E731
    S.append(f"<section><h3>{foto} <span class='nota'>referencia: {html.escape(refs)} · persona {r['persona_vieja']} → "
             f"{r['persona_nueva']}</span></h3><div class='fila'>"
             f"<figure>{img(ref)}<figcaption>referencia</figcaption></figure>"
             f"<figure>{img(r['v0'])}<figcaption>V0 · producción (prompt viejo, Lite)</figcaption></figure>"
             f"<figure>{img(v['V1'].get('path'))}<figcaption>V1 · prompt nuevo + Lite {html.escape(est('V1'))}</figcaption></figure>"
             f"<figure>{img(v['V2'].get('path'))}<figcaption>V2 · prompt nuevo + Nano Banana 2 completo "
             f"{html.escape(est('V2')) or '(no se pidió)'}</figcaption></figure></div>"
             f"<details open><summary>prompts</summary><pre>VIEJO\n{html.escape(r['prompt_viejo'] or '')}\n\nNUEVO\n"
             f"{html.escape(r['prompt_nuevo'])}</pre></details></section>")
    tabla.append(f"| {foto} | {r['persona_vieja']} → {r['persona_nueva']} | {sujeto(r['casilleros_viejos'])} | "
                 f"{sujeto(r['casilleros_nuevos'])} |")
(AQUI / "tabla_subject.md").write_text("\n".join(tabla) + "\n", encoding="utf-8")
cost = "".join(f"<li>{html.escape(k)}: US$ {v:.4f}</li>" for k, v in costo.items())
doc = f"""<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>F78c Lab Rasgos</title><style>
:root{{--bg:#f6f5f2;--fg:#1d1d1b;--mut:#6b6a66;--card:#fff;--line:#dedcd6}}
@media (prefers-color-scheme:dark){{:root{{--bg:#151514;--fg:#ecebe7;--mut:#a3a29d;--card:#1f1f1d;--line:#353531}}}}
body{{background:var(--bg);color:var(--fg);font:15px/1.45 system-ui,sans-serif;margin:0 auto;padding:16px;max-width:1700px}}
h1{{font-size:22px}} h3{{margin:0 0 6px;font-size:16px}} section{{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:12px;margin:12px 0}}
.fila{{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}} figure{{margin:0}} img{{width:100%;height:auto;border-radius:4px}}
figcaption,.nota{{color:var(--mut);font-size:13px;font-weight:normal}} pre{{white-space:pre-wrap;font-size:12px;background:var(--bg);padding:8px;border-radius:4px}}
.falta{{padding:40px;text-align:center;color:var(--mut);border:1px dashed var(--line)}} @media (max-width:800px){{.fila{{grid-template-columns:1fr 1fr}}}}
</style></head><body><h1>F78c · lab de 5 fotos de Colza: texto con los rasgos de la madre + motor Lite vs completo</h1>
<p class="nota">Nada de producción se tocó (md5 de 422 archivos igual antes y después). Casilleros rehechos con Opus por
<code>_f8_refill</code> (nota vacía, mismo ancla y beat). Sin respaldo Seedream. PARADA: Omar y el analista deciden.</p><ul>{cost}</ul>
{''.join(S)}</body></html>"""
(R / "lab" / "hyperframes" / "f78c" / "ETAPA_F78c.html").write_text(doc, encoding="utf-8")
print("ETAPA_F78c.html", len(doc) // 1024, "KB")
print("\n".join(tabla))
