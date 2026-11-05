"""F78b Etapa A: para Colza, por persona con madre y clave de variante: tramo, edad, condición del canon y qué se pediría
(fila de la llamada de estado; variante con edad exacta y/o estado visible; o sin variante si el estado sale vacío y no hay edad).
Solo lectura: no llama a nada. Uso: PYTHONIOENCODING=utf-8 python lab/hyperframes/f78a/a2/tabla_pedidos.py"""
import json
import sys
from pathlib import Path

R = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(R))
import foto_madre as fm  # noqa: E402

TID = "c4934b7d-3f54-448f-ba5f-539dc744f0d8"
db = json.loads((R / "data" / "topics_db.json").read_text(encoding="utf-8"))
topic = next(t for t in db["topics"] if t.get("id") == TID)
fotos = fm._fotos_del_guion(json.loads((R / "data" / "scripts" / "_steps" / TID / "03_visual.json").read_text(encoding="utf-8")))
filas, out = [], ["| persona | clave | tramo | edad | condición (canon) | fotos | qué se pediría |", "|---|---|---|---|---|---|---|"]
for p in topic["documented_people"]:
    if not p.get("foto_madre"):
        continue
    por_clave: dict[str, dict] = {}
    for f in fm._fotos_con_madre_de(p, fotos):
        cv = fm.clave_de_foto(p, f["anio"])
        if cv["clave"]:
            por_clave.setdefault(cv["clave"], {**cv, "n": 0})["n"] += 1
    for clave, cv in por_clave.items():
        fila = {"name": p["name"], "tramo": cv["tramo"], "condition": cv["condition"]}
        if cv["tramo"] and fila not in filas:
            filas.append(fila)
        edad = cv["edad"]
        if edad is not None:
            pedido = f"variante con «now {edad} years old» + estado visible si la llamada devuelve algo"
        else:
            pedido = "variante con el estado visible; si sale \"\" → sin variante (sus fotos con la madre limpia)"
        out.append(f"| {p['name']} | {clave} | {cv['tramo'] or '—'} | {edad if edad is not None else '—'} | {cv['condition'] or '—'} | "
                   f"{cv['n']} | {pedido} |")
out += ["", f"Llamada de estado: 1, con {len(filas)} filas (pares persona/tramo únicos):", ""]
out += [f"- {f['name']} · {f['tramo']} · «{f['condition']}»" for f in filas]
txt = "\n".join(out) + "\n"
(Path(__file__).parent / "tabla_pedidos.md").write_text(txt, encoding="utf-8")
print(txt)
