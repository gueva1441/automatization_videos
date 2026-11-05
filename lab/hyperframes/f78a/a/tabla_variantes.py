"""F78a Etapa A: la tabla real de variantes de Colza con las funciones de producción (foto_madre._fotos_del_guion,
_fotos_con_madre_de, clave_de_foto). Solo lectura: no genera nada, no llama a nada.
Uso: PYTHONIOENCODING=utf-8 python lab/hyperframes/f78a/a/tabla_variantes.py"""
import json
import sys
from pathlib import Path

R = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(R))
import foto_madre as fm  # noqa: E402

TID = "c4934b7d-3f54-448f-ba5f-539dc744f0d8"
db = json.loads((R / "data" / "topics_db.json").read_text(encoding="utf-8"))
topic = next(t for t in (db["topics"] if isinstance(db, dict) else db) if t.get("id") == TID)
visual = json.loads((R / "data" / "scripts" / "_steps" / TID / "03_visual.json").read_text(encoding="utf-8"))
fotos = fm._fotos_del_guion(visual)
filas, total, n_var = [], 0, 0
for p in topic["documented_people"]:
    mias = fm._fotos_con_madre_de(p, fotos)
    if len(mias) < fm.MADRE_PERSONA_MIN_FOTOS or not fm._clean(p.get("appearance_canon")):
        continue
    grupos: dict[str, list[str]] = {}
    edades: dict[str, object] = {}
    for f in mias:
        cv = fm.clave_de_foto(p, f["anio"])
        k = cv["clave"]
        grupos.setdefault(k, []).append(f"ch{f['cap']:02d}_{f['kind']}_{f['idx']:02d} ({f['anio']})")
        edades[k] = cv["edad"]
    for k, ids in grupos.items():
        total += len(ids)
        n_var += bool(k)
        nombre = f"{fm._slug(p['name'])}@{k}.png" if k else f"{fm._slug(p['name'])}.png (madre limpia)"
        filas.append(f"| {p['name']} | {k or '— (limpia)'} | {edades[k] if edades[k] is not None else '—'} | {len(ids)} | "
                     f"{nombre} | {', '.join(ids)} |")
out = ["| persona | clave | edad | fotos | archivo | ids (año) |", "|---|---|---|---|---|---|", *filas, "",
       f"Total: {total} fotos con madre de persona · {n_var} variantes · "
       f"{sum(1 for l in filas if '(limpia)' in l)} grupos con la madre limpia"]
txt = "\n".join(out) + "\n"
(Path(__file__).parent / "tabla_variantes.md").write_text(txt, encoding="utf-8")
print(txt)
