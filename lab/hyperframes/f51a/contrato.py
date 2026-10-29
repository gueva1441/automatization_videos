# -*- coding: utf-8 -*-
"""F51a etapa 1 — contrato: el `armar` de producción (ya = C) + el post-proceso de producción (`f8_backstop` +
`_sacar_frases_con_texto`, como `m03_visual` l. 692–696, vía `f50g/rearmar.rearmar_una`) sobre los casilleros crudos
(`raw_llm_prompt`) de las 20 fotos de F50h en el 03_visual.json vivo de Wittenoom tiene que dar, byte a byte,
`PROMPTS_F50h.json → fotos[i]["C"]`. Sin modelos, sin fal; no escribe producción.
F51b: los grupos salen del canon con el que se armó F50h (`f50f/canon_f50f.json`, = el del topic hasta F51b), no del
topic vivo: así el contrato mide el armado y no se mueve cuando F51b rehace el canon.

Uso: python lab/hyperframes/f51a/contrato.py      # tabla de las 20, diff palabra por palabra si alguna difiere,
                                                  # y 2 prompts enteros (1/2 y una con cartel); sale 1 si falla una
"""
import difflib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "lab" / "hyperframes" / "f50g"))
TID = "123bbb64-9fca-4395-8bf4-57d60e219ef1"
PROMPTS = ROOT / "lab" / "hyperframes" / "f50h" / "PROMPTS_F50h.json"
CANON_F50H = ROOT / "lab" / "hyperframes" / "f50f" / "canon_f50f.json"     # el canon de F50h (F51b)


def diff_palabras(a: str, b: str) -> str:
    return " ".join(d for d in difflib.ndiff(a.split(), b.split()) if d[0] in "+-")


def main() -> int:
    import rearmar as rg
    from script_engine import m03_imagenes_v3 as v3
    from script_engine.topics_db import get_topic_by_id
    esperado = json.loads(PROMPTS.read_text(encoding="utf-8"))["fotos"]
    vivo = json.loads(rg.VISUAL.read_text(encoding="utf-8"))
    topic = get_topic_by_id(TID)
    beats = v3.load_beats(topic, rg.STEPS)
    canon = json.loads(CANON_F50H.read_text(encoding="utf-8"))
    grupos = {g["id"]: g for g in canon.get("people_groups") or [] if isinstance(g, dict) and g.get("id")}
    items = {f"{c['chapter_number']}/{i}": it for c in vivo["chapters"] for i, (it, _) in enumerate(rg.fotos(c), 1)}
    malas, prod = [], {}
    print("| foto | igual |\n|---|---|")
    for f in esperado:
        it = items[f["foto"]]
        cap = int(f["foto"].split("/")[0])
        by_n = {b["n"]: b for b in beats.get(cap) or []}
        escala = bool((by_n.get(it.get("beat")) or {}).get("escala"))
        p, _ = rg.rearmar_una(it, escala, topic.get("documented_people"), grupos)
        prod[f["foto"]] = p
        igual = p.encode("utf-8") == f["C"].encode("utf-8")
        print(f"| {f['foto']} | {'sí' if igual else 'NO'} |")
        if not igual:
            malas.append((f["foto"], diff_palabras(f["C"], p)))
    print(f"\n**{len(esperado) - len(malas)}/{len(esperado)} byte a byte iguales a PROMPTS_F50h.json → C**")
    for foto, d in malas:
        print(f"\nDIFF {foto} (- C de F50h, + producción): {d}")
    con_cartel = next(f["foto"] for f in esperado if f.get("cartel"))
    for foto in ("1/2", con_cartel):
        print(f"\n### {foto} entera, armada con el código de producción\n\n```\n{prod[foto]}\n```")
    return 1 if malas else 0


if __name__ == "__main__":
    sys.exit(main())
