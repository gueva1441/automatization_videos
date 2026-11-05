"""F78d Etapa A: qué fotos de Colza tocaría el paso `aspecto` (cap, id, persona, aspecto_fuente, QA, nota previa), SIN llamar.
Solo lectura: `foto_madre.rasgos_vigentes` + `m03_visual.fotos_aspecto`. Uso: PYTHONIOENCODING=utf-8 python lab/hyperframes/f78d/a/lista_aspecto.py"""
import json
import sys
from pathlib import Path

R = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(R))
import fase1_5  # noqa: E402
import foto_madre as fm  # noqa: E402
from script_engine import m03_visual as m3  # noqa: E402

TID = "c4934b7d-3f54-448f-ba5f-539dc744f0d8"
topic = fase1_5._load_topic_by_id(TID)
visual = json.loads((m3.STEPS_DIR / TID / "03_visual.json").read_text(encoding="utf-8"))
rasgos, motivo = fm.rasgos_vigentes(topic, TID)
filas = m3.fotos_aspecto(TID, visual, rasgos, TID)
out = [f"rasgos vigentes: {motivo} ({len(rasgos)} personas)", "",
       "| cap | foto | persona | aspecto_fuente | editada en QA | nota previa (`_f8_rehecha`) | acción |", "|---|---|---|---|---|---|---|"]
for f in filas:
    out.append(f"| {f['cap']} | {f['foto']} | {', '.join(f['persona'])} | {f['aspecto_fuente'] or '—'} | "
               f"{'sí' if f['qa'] else 'no'} | {f['nota'][:90] or '—'} | {f['accion']} |")
cuenta = {}
for f in filas:
    cuenta[f["accion"]] = cuenta.get(f["accion"], 0) + 1
out += ["", f"total con persona: {len(filas)} · {cuenta}"]
txt = "\n".join(out)
(Path(__file__).parent / "lista_aspecto.md").write_text(txt + "\n", encoding="utf-8")
print(txt)
