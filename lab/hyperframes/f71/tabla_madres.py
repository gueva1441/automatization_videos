"""F71b Etapa A: las 99 fotos de Wittenoom, madres antes → después, con la regla de producción y el guion vivo. Solo lee."""
import json
import os
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
os.chdir(RAIZ)
sys.path.insert(0, str(RAIZ))

import asset_manager as am  # noqa: E402

T = "123bbb64-9fca-4395-8bf4-57d60e219ef1"
s = json.loads((RAIZ / "data" / "scripts" / f"{T}.json").read_text(encoding="utf-8"))
reg, canon = s.get("foto_madre_registry") or {}, s.get("foto_madre_personas") or {}


def fotos(ch):
    cid = f"ch{ch['chapter_number']:02d}"
    if isinstance(ch.get("image_f8"), dict) and ch.get("image_prompt"):
        yield f"{cid}_img_01", ch["image_f8"], ch["image_prompt"]
    for k, it in enumerate(ch.get("image_prompts") or [], 1):
        if isinstance(it, dict):
            yield f"{cid}_img_{k:02d}", it, it.get("prompt") or ""
    for k, it in enumerate(ch.get("supplemental_image_prompts") or [], 1):
        yield f"{cid}_supp_{k:02d}", it, it.get("prompt") or ""


filas, cambian = [], []
for ch in s["chapters"]:
    for nombre, it, prompt in fotos(ch):
        args = (am._norm_persona(it.get("persona")), am._norm_foto_madre_refs(it.get("foto_madre_ref")), it.get("anio"), reg, canon)
        antes = [r for r, _ in am._madres_para_item(*args)]
        despues = [r for r, _ in am._madres_para_item(*args, prompt)]
        filas.append(f"| {nombre} | {it.get('anio') or '-'} | {', '.join(args[0]) or '-'} | {', '.join(antes) or '-'} | {', '.join(despues) or '-'} | {'**CAMBIA**' if antes != despues else ''} |")
        if antes != despues:
            cambian.append((nombre, antes, despues))
txt = [f"# F71b: madres antes → después, {len(filas)} fotos", "", f"Motor activo: `{am.api.image_engine}`. Cambian: {len(cambian)}: " + "; ".join(f"`{n}` {a or '[]'} → {d}" for n, a, d in cambian) + ".", "",
       "| Foto | Año | persona | Antes | Después | |", "|---|---|---|---|---|---|", *filas]
(Path(__file__).parent / "TABLA_MADRES.md").write_text("\n".join(txt) + "\n", encoding="utf-8")
print(len(filas), cambian)
