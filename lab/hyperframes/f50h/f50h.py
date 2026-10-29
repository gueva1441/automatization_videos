# -*- coding: utf-8 -*-
"""F50h — prueba L contra C del armado del prompt de foto (lab; no toca producción).

Etapa 1 (`--prompts`, US$ 0): los 60 prompts en texto de las 20 fotos del handoff.
- L  = el `prompt` guardado en el papel de F50g (`f50g/PAPEL_FOTOS_WITTENOOM.json`), verificado contra
       `f50g/rearmar.rearmar_una(..., grupos)` y contra el 03_visual.json vivo.
- C  = los mismos casilleros, sin mirada, objeto, paleta, `style_head` ni `STYLE_TAIL`, en el orden de la guía de fal:
       sujeto + acción → aspecto → lugar + año → cartel → luz → plano → una oración de estilo → cierre. Las partes que
       comparte con L salen de `m03_imagenes_v3.armar` (misma regla de lugar/año, plano, cartel y cierre, ya con
       `_sin_negadas`); la luz es `oracion(_sin_negadas(lighting))`, sin `color_palette`.
- C+ép = C con la oración de estilo «como una foto real de ese año».
Después, el mismo post-proceso que L: `f8_backstop` y `_sacar_frases_con_texto` (como `rearmar_una`).
Salida: PROMPTS_F50h.json y PROMPTS_F50h.md.

Las etapas 2 y 3 (`--fotos`, `--hojas`, `--vision`, `--tabla`) esperan el OK de Omar y no están escritas.
Uso: python lab/hyperframes/f50h/f50h.py --prompts
"""
import json
import re
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "lab" / "hyperframes" / "f50g"))
F50H = Path(__file__).resolve().parent
TID = "123bbb64-9fca-4395-8bf4-57d60e219ef1"

# las 20 fotos del handoff F50h §Etapa 1 (cap, foto del papel de F50g)
FOTOS = [(1, 2), (1, 3), (1, 4), (2, 9), (2, 11), (2, 15), (3, 3), (3, 6), (3, 10), (4, 1), (4, 11), (4, 12), (5, 1),
         (5, 8), (5, 13), (5, 16), (6, 5), (6, 15), (7, 7), (7, 9)]
ENTEROS = [(1, 2), (3, 3), (7, 7)]                      # los 3 prompts que el .md pega enteros
ESTILO_C = ("A grainy 35mm documentary photograph taken in {anio}, with muted colors and slight underexposure, in a "
            "dark-history realist style.")          # handoff F50h, parte 7 de C
ESTILO_EP = ("A grainy documentary photograph taken in {anio}, with the film, color and tones a real photograph from "
             "{anio} would have, slightly underexposed, in a dark-history realist style.")   # handoff F50h, C+ép


def oraciones(p: str) -> int:
    return len([x for x in re.split(r"(?<=[.!?])\s+", (p or "").strip()) if x])


def palabras(p: str) -> int:
    return len((p or "").split())


def armar_c(slots: dict, anio: str, grupos: dict, estilo: str) -> str:
    """C (o C+ép con otro `estilo`): las partes de `armar` que comparte con L, en el orden de la guía de fal."""
    from script_engine import m03_imagenes_v3 as v3
    pa = v3.armar(slots, anio, grupos)["partes"]
    luz = v3.oracion(v3._sin_negadas(slots.get("lighting"))) if isinstance(slots.get("lighting"), str) else ""
    partes = [pa["sujeto"], pa["aspecto"], pa["lugar_anio"], pa["texto"], luz, pa["tecnica"],
              estilo.format(anio=anio), pa["cierre"]]
    return " ".join(p for p in partes if p)


def post(prompt: str, slots: dict, escala: bool, documented) -> str:
    """El mismo post-proceso que L (`f50g/rearmar.rearmar_una`)."""
    from script_engine import m03_imagenes_v3 as v3
    from script_engine.m03_visual import _sacar_frases_con_texto
    prose, _ = v3.f8_backstop(prompt, slots, escala, documented)
    tii = slots.get("text_in_image") or {}
    prose, _ = _sacar_frases_con_texto(prose, (tii.get("text") or "") if tii.get("present") else "")
    return prose


def prompts() -> int:
    import rearmar as rg
    from script_engine import m03_imagenes_v3 as v3
    from script_engine.topics_db import get_topic_by_id
    vivo = json.loads(rg.VISUAL.read_text(encoding="utf-8"))
    papel = {(f["cap"], f["foto"]): f for f in json.loads(
        (ROOT / "lab" / "hyperframes" / "f50g" / "PAPEL_FOTOS_WITTENOOM.json").read_text(encoding="utf-8"))["fotos"]}
    topic = get_topic_by_id(TID)
    beats = v3.load_beats(topic, rg.STEPS)
    grupos = {g["id"]: g for g in topic.get("people_groups") or [] if isinstance(g, dict) and g.get("id")}
    items = {(c["chapter_number"], i): it for c in vivo["chapters"] for i, (it, _) in enumerate(rg.fotos(c), 1)}
    out, verif = [], []
    for cap, foto in FOTOS:
        it = items[(cap, foto)]
        by_n = {b["n"]: b for b in beats.get(cap) or []}
        escala = bool((by_n.get(it.get("beat")) or {}).get("escala"))
        documented = topic.get("documented_people")
        slots = json.loads(it["raw_llm_prompt"])
        anio = it["anio"]
        L = papel[(cap, foto)]["prompt"]
        rearmado, _ = rg.rearmar_una(it, escala, documented, grupos)
        verif.append({"foto": f"{cap}/{foto}", "L_igual_rearmar": L == rearmado, "L_igual_vivo": L == it["prompt"]})
        C = post(armar_c(slots, anio, grupos, ESTILO_C), slots, escala, documented)
        CE = post(armar_c(slots, anio, grupos, ESTILO_EP), slots, escala, documented)
        out.append({"foto": f"{cap}/{foto}", "anio": anio, "people_group": slots.get("people_group") or [],
                    "shot_scale": slots.get("shot_scale"),
                    "cartel": (slots.get("text_in_image") or {}).get("text")
                    if (slots.get("text_in_image") or {}).get("present") else None,
                    "L": L, "C": C, "C+ép": CE,
                    "palabras": {"L": palabras(L), "C": palabras(C), "C+ép": palabras(CE)},
                    "oraciones": {"L": oraciones(L), "C": oraciones(C), "C+ép": oraciones(CE)}})
    ok = sum(v["L_igual_rearmar"] and v["L_igual_vivo"] for v in verif)
    med = {k: statistics.median(f["palabras"][k] for f in out) for k in ("L", "C", "C+ép")}
    mx = {k: max(f["palabras"][k] for f in out) for k in ("L", "C", "C+ép")}
    mn = {k: min(f["palabras"][k] for f in out) for k in ("L", "C", "C+ép")}
    ormed = {k: statistics.median(f["oraciones"][k] for f in out) for k in ("L", "C", "C+ép")}
    (F50H / "PROMPTS_F50h.json").write_text(json.dumps(
        {"fotos": out, "verificacion_L": verif, "L_igual_guardado": f"{ok}/{len(out)}",
         "palabras": {"mediana": med, "max": mx, "min": mn}, "oraciones_mediana": ormed},
        ensure_ascii=False, indent=1), encoding="utf-8")
    L_ = ["# PROMPTS_F50h — L, C y C+ép de las 20 fotos (F50h etapa 1, en texto, US$ 0)", "",
          "Salida de `python lab/hyperframes/f50h/f50h.py --prompts`. Casilleros: el `raw_llm_prompt` y el `anio` de "
          "cada foto del 03_visual.json vivo de Wittenoom; grupos: los `people_groups` del topic (igual que "
          "`f50g/rearmar.py`). Ninguna llamada a modelos ni a fal.", "",
          f"**Verificación L = guardado: {ok}/{len(out)}**. L (el `prompt` del papel de F50g) es igual a "
          f"`rearmar_una(..., grupos)` y al `prompt` del 03_visual.json vivo en {ok} de {len(out)} fotos.", "",
          "| | L | C | C+ép |", "|---|---:|---:|---:|",
          f"| palabras, mediana | {med['L']} | {med['C']} | {med['C+ép']} |",
          f"| palabras, mín · máx | {mn['L']} · {mx['L']} | {mn['C']} · {mx['C']} | {mn['C+ép']} · {mx['C+ép']} |",
          f"| oraciones, mediana | {ormed['L']} | {ormed['C']} | {ormed['C+ép']} |", "",
          "Referencia de la guía de fal (no es un corte; el handoff lo pide solo como dato al lado): 2–4 oraciones.", "",
          "## Por foto", "",
          "| foto | año | plano | grupos | cartel | palabras L · C · C+ép | oraciones L · C · C+ép | L = guardado |",
          "|---|---|---|---|---|---|---|---|"]
    for f, v in zip(out, verif):
        p, o = f["palabras"], f["oraciones"]
        L_.append(f"| {f['foto']} | {f['anio']} | {f['shot_scale']} | {', '.join(f['people_group']) or '—'} | "
                  f"{f['cartel'] or '—'} | {p['L']} · {p['C']} · {p['C+ép']} | {o['L']} · {o['C']} · {o['C+ép']} | "
                  f"{'sí' if v['L_igual_rearmar'] and v['L_igual_vivo'] else 'NO'} |")
    for cap, foto in ENTEROS:
        f = next(x for x in out if x["foto"] == f"{cap}/{foto}")
        L_ += ["", f"## {cap}/{foto} entera", ""]
        for k in ("L", "C", "C+ép"):
            L_ += [f"**{k}** ({f['palabras'][k]} palabras, {f['oraciones'][k]} oraciones)", "", "```", f[k], "```", ""]
    (F50H / "PROMPTS_F50h.md").write_text("\n".join(L_), encoding="utf-8")
    print(f"L = guardado {ok}/{len(out)} · palabras mediana {med} · máx {mx} · oraciones mediana {ormed}")
    return 0 if ok == len(out) else 1


def main() -> int:
    if "--prompts" in sys.argv:
        return prompts()
    print("F50h: solo está la etapa 1 (--prompts); las etapas 2 y 3 esperan el OK de Omar.")
    return 2


if __name__ == "__main__":
    sys.exit(main())
