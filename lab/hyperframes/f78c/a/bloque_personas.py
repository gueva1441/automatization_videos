"""F78c Etapa A: el bloque PERSONAS DOCUMENTADAS de Colza antes (sin rasgos) y después (con rasgos.json vigente), con la función
de producción. Solo lectura, sin llamadas. Uso: PYTHONIOENCODING=utf-8 python lab/hyperframes/f78c/a/bloque_personas.py"""
import json
import sys
from pathlib import Path

R = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(R))
import foto_madre as fm  # noqa: E402
from script_engine import m03_visual as m3  # noqa: E402

TID = "c4934b7d-3f54-448f-ba5f-539dc744f0d8"
db = json.loads((R / "data" / "topics_db.json").read_text(encoding="utf-8"))
topic = next(t for t in db["topics"] if t.get("id") == TID)


def bloque(texto: str) -> str:
    i = texto.index("PERSONAS DOCUMENTADAS")
    j = texto.find("\n\n", i)
    return texto[i:j if j > 0 else None]


rasgos, motivo = fm.rasgos_vigentes(topic)
visual = json.loads((R / "data" / "scripts" / "_steps" / TID / "03_visual.json").read_text(encoding="utf-8"))
md5_m03 = fm._md5(fm.entrada_rasgos(topic, visual))
md5_cache = json.loads((R / "output" / TID / "foto_madre" / "rasgos.json").read_text(encoding="utf-8"))["md5_entrada"]
despues = bloque(m3._format_seedream_canon_block(topic))
orig = m3._rasgos_de_madres
m3._rasgos_de_madres = lambda t: {}
antes = bloque(m3._format_seedream_canon_block(topic)).replace(   # la cabecera de antes de F78c (commit a6ff9a9)
    "en la prosa usar appearance (o appearance_canon si no hay), NUNCA", "en la prosa usar appearance_canon, NUNCA")
m3._rasgos_de_madres = orig
txt = (f"rasgos_vigentes: {motivo} · {len(rasgos)} personas\nmd5 entrada desde m03 = {md5_m03}\nmd5_entrada de rasgos.json = "
       f"{md5_cache}\ncoinciden: {md5_m03 == md5_cache}\n\n## ANTES\n\n```\n{antes}\n```\n\n## DESPUÉS\n\n```\n{despues}\n```\n")
(Path(__file__).parent / "bloque_personas.md").write_text(txt, encoding="utf-8")
print(txt)
