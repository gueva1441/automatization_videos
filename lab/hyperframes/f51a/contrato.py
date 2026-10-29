# -*- coding: utf-8 -*-
"""F51a etapa 1 — contrato: el `armar` de producción (ya = C) + el post-proceso de producción (`f8_backstop` +
`_sacar_frases_con_texto`, como `m03_visual` l. 692–696, vía `f50g/rearmar.rearmar_una`) sobre los casilleros crudos
(`raw_llm_prompt`) de las 20 fotos de F50h en el 03_visual.json vivo de Wittenoom tiene que dar, byte a byte,
`PROMPTS_F50h.json → fotos[i]["C"]`. Sin modelos, sin fal; no escribe producción.
F51b: los grupos salen del canon con el que se armó F50h (`f50f/canon_f50f.json`, = el del topic hasta F51b), no del
topic vivo: así el contrato mide el armado y no se mueve cuando F51b rehace el canon.
F51d-A: los casilleros salen de la copia del 03_visual.json de antes de rehacer m03 (`f51d/antes/03_visual.json`, md5
59a8484d…, = el vivo hasta F51d-A), por la misma razón.
F51f: la frase del cartel cambió a propósito («… in clear crisp {font} lettering»). Lo esperado = el C de F50h con la
frase vieja del cartel (`_frase_cartel_f50h`, la de producción hasta F51f) cambiada por la de `frase_cartel`; además,
el prompt de producción sin la oración nueva tiene que ser igual al C de F50h sin la vieja (solo cambia el cartel).

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
VISUAL_F50H = ROOT / "lab" / "hyperframes" / "f51d" / "antes" / "03_visual.json"  # los casilleros de F50h (F51d-A)


def _frase_cartel_f50h(tii: dict) -> str:
    """La frase del cartel de producción hasta F51f (copia, para el contrato)."""
    import re
    from script_engine import m03_imagenes_v3 as v3
    texto = tii.get("text")
    font = v3._minuscula_media(str(tii.get("font") or "").strip().rstrip(".,;"))
    loc = re.sub(r"\s+", " ", str(tii.get("location") or "")).strip().rstrip(".,;")
    en = f" in {font}" if font else ""
    if not loc:
        return v3.oracion(f'A sign reads "{texto}"{en}, in clear crisp lettering')
    if loc.split()[0].lower() in v3._PREP_LUGAR:
        loc = v3._minuscula_media(loc)
        return v3.oracion(f'The words "{texto}" are written {loc}{en}, in clear crisp lettering')
    sujeto = re.sub(r"^(the|a|an)\s+", "", loc, flags=re.I)
    return v3.oracion(f'The {sujeto} reads "{texto}"{en}, in clear crisp lettering')


def diff_palabras(a: str, b: str) -> str:
    return " ".join(d for d in difflib.ndiff(a.split(), b.split()) if d[0] in "+-")


def main() -> int:
    import rearmar as rg
    from script_engine import m03_imagenes_v3 as v3
    from script_engine.topics_db import get_topic_by_id
    esperado = json.loads(PROMPTS.read_text(encoding="utf-8"))["fotos"]
    vivo = json.loads(VISUAL_F50H.read_text(encoding="utf-8"))
    topic = get_topic_by_id(TID)
    beats = v3.load_beats(topic, rg.STEPS)
    canon = json.loads(CANON_F50H.read_text(encoding="utf-8"))
    grupos = {g["id"]: g for g in canon.get("people_groups") or [] if isinstance(g, dict) and g.get("id")}
    items = {f"{c['chapter_number']}/{i}": it for c in vivo["chapters"] for i, (it, _) in enumerate(rg.fotos(c), 1)}
    malas, prod, carteles = [], {}, []
    print("| foto | igual |\n|---|---|")
    for f in esperado:
        it = items[f["foto"]]
        cap = int(f["foto"].split("/")[0])
        by_n = {b["n"]: b for b in beats.get(cap) or []}
        escala = bool((by_n.get(it.get("beat")) or {}).get("escala"))
        p, _ = rg.rearmar_una(it, escala, grupos)
        prod[f["foto"]] = p
        C = f["C"]
        tii = json.loads(it["raw_llm_prompt"]).get("text_in_image") or {}
        if tii.get("present"):                                   # F51f: el cartel cambió a propósito
            vieja, nueva = _frase_cartel_f50h(tii), v3.frase_cartel(tii)
            solo_cartel = C.count(vieja) == 1 and p.count(nueva) == 1 and C.replace(vieja, "") == p.replace(nueva, "")
            carteles.append((f["foto"], vieja, nueva, solo_cartel))
            C = C.replace(vieja, nueva) if solo_cartel else C
        igual = p.encode("utf-8") == C.encode("utf-8")
        print(f"| {f['foto']} | {'sí' if igual else 'NO'} |")
        if not igual:
            malas.append((f["foto"], diff_palabras(C, p)))
    print(f"\n**{len(esperado) - len(malas)}/{len(esperado)} byte a byte iguales a PROMPTS_F50h.json → C "
          f"(con la frase del cartel de F51f)**")
    print(f"\nCarteles: {len(carteles)} fotos, solo cambia la oración del cartel en "
          f"{sum(1 for c in carteles if c[3])}/{len(carteles)}")
    for foto, vieja, nueva, ok in carteles:
        print(f"- {foto} {'ok' if ok else 'NO'}: «{vieja}» → «{nueva}» · diff contra F50h: "
              f"{diff_palabras(next(x['C'] for x in esperado if x['foto'] == foto), prod[foto])}")
    for foto, d in malas:
        print(f"\nDIFF {foto} (- C de F50h, + producción): {d}")
    con_cartel = next(f["foto"] for f in esperado if f.get("cartel"))
    for foto in ("1/2", con_cartel):
        print(f"\n### {foto} entera, armada con el código de producción\n\n```\n{prod[foto]}\n```")
    return 1 if malas else 0


if __name__ == "__main__":
    sys.exit(main())
