# -*- coding: utf-8 -*-
"""F50b §2–3 — re-armado EN SECO de las 96 fotos de Wittenoom desde los casilleros guardados en 03_visual.json
(`raw_llm_prompt` = casilleros después de scrub_slots/fix_text_slot, y el `anio` de cada foto) → `armar` → F8 →
backstop de texto legible, igual que `m03_visual._render_prompts_seedream`. Sin modelos, sin fal.

Uso:
  python lab/hyperframes/f50b/rearmar.py --igual     # con el código de hoy, ¿sale cada prompt guardado byte a byte?
  python lab/hyperframes/f50b/rearmar.py             # DIFF_PAPEL.md + verificación (no escribe)
  python lab/hyperframes/f50b/rearmar.py --escribir  # además escribe prompt/sensible/motivos en 03_visual.json

Atribución: un arreglo «toca» una foto si al apagar solo ese arreglo el prompt de esa foto cambia.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
F50B = Path(__file__).resolve().parent
TID = "123bbb64-9fca-4395-8bf4-57d60e219ef1"
STEPS = ROOT / "data" / "scripts" / "_steps"
VISUAL = STEPS / TID / "03_visual.json"
ANTES = F50B / "antes" / "03_visual.json"          # copia de antes del re-armado: de acá salen casilleros y prompts

# la tabla del handoff F50b (numeración del papel: en un cap Veo la foto 1 es el primer cuadro del clip)
ESPERADO = {1: {(2, 13), (4, 1), (5, 16)}, 2: {(4, 14), (6, 1), (7, 1), (7, 11)}}
ESPERADO_3 = {"tecnica": 29, "texto": 2}
HARM_VIEJO = r"\b(beaten|hurt|injur\w*|dead|dying|drown\w*|burn\w*|shot|kill\w*|corpse|body|bodies|abuse\w*|struck)\b"


def fotos(cap: dict) -> list[tuple[dict, str]]:
    """[(ítem, rol)] en el orden del papel."""
    if cap.get("image_prompts") is not None:
        return [(it, "flux") for it in cap["image_prompts"]]
    f0 = {**(cap.get("image_f8") or {}), "prompt": cap.get("image_prompt")}
    return [(f0, "veo0")] + [(it, "supp") for it in cap.get("supplemental_image_prompts") or []]


def frases(p: str) -> list[str]:
    return re.split(r"(?<=[.!?])\s+", p or "")


def rearmar_una(it: dict, escala: bool, documented) -> tuple[str, dict]:
    from script_engine import m03_imagenes_v3 as v3
    from script_engine.m03_visual import _sacar_frases_con_texto
    slots = json.loads(it["raw_llm_prompt"])
    armado = v3.armar(slots, it["anio"])
    prose, _ = v3.f8_backstop(armado["prompt"], slots, escala, documented)
    tii = slots.get("text_in_image") or {}
    prose, _ = _sacar_frases_con_texto(prose, (tii.get("text") or "") if tii.get("present") else "")
    return prose, armado["partes"]


def correr(v: dict, topic: dict, beats) -> dict:
    out = {}
    for cap in v["chapters"]:
        n = cap["chapter_number"]
        by_n = {b["n"]: b for b in beats.get(n) or []}
        for i, (it, rol) in enumerate(fotos(cap), start=1):
            esc = bool((by_n.get(it.get("beat")) or {}).get("escala"))
            out[(n, i)] = rearmar_una(it, esc, topic.get("documented_people"))
    return out


def main() -> int:
    from script_engine import m03_imagenes_v3 as v3
    from script_engine.topics_db import get_topic_by_id
    v = json.loads((VISUAL if "--igual" in sys.argv else ANTES).read_text(encoding="utf-8"))
    topic = get_topic_by_id(TID)
    beats = v3.load_beats(topic, STEPS)
    guardado = {(c["chapter_number"], i): it["prompt"] for c in v["chapters"] for i, (it, _) in enumerate(fotos(c), 1)}

    if "--igual" in sys.argv:
        hoy = correr(v, topic, beats)
        dif = [k for k in guardado if hoy[k][0] != guardado[k]]
        print(f"fotos {len(guardado)} · iguales {len(guardado) - len(dif)} · distintas {dif}")
        return 0 if not dif else 1

    nuevo = correr(v, topic, beats)
    # apagar un arreglo por vez
    harm, neg, minus = v3.HARM, v3._sin_negadas, v3._minuscula_media
    v3.HARM = HARM_VIEJO
    sin1 = correr(v, topic, beats)
    v3.HARM = harm
    v3._sin_negadas = lambda t: t
    sin2 = correr(v, topic, beats)
    v3._sin_negadas = neg
    v3._minuscula_media = lambda t: t
    sin3 = correr(v, topic, beats)
    v3._minuscula_media = minus

    cambian = sorted(k for k in guardado if nuevo[k][0] != guardado[k])
    por = {1: {k for k in cambian if sin1[k][0] != nuevo[k][0]},
           2: {k for k in cambian if sin2[k][0] != nuevo[k][0]},
           3: {k for k in cambian if sin3[k][0] != nuevo[k][0]}}
    partes3 = {}
    for k in por[3]:
        partes3[k] = [p for p in nuevo[k][1] if nuevo[k][1][p] != sin3[k][1][p]]
    sin_arreglo = [k for k in cambian if not any(k in s for s in por.values())]
    cuenta3 = {"tecnica": sum("tecnica" in p for p in partes3.values()),
               "texto": sum("texto" in p for p in partes3.values())}
    otras3 = sorted(k for k, p in partes3.items() if set(p) - {"tecnica", "texto"})

    fallas = []
    for a in (1, 2):
        if por[a] != ESPERADO[a]:
            fallas.append(f"arreglo {a}: tocó {sorted(por[a])}, la tabla dice {sorted(ESPERADO[a])}")
    if cuenta3 != ESPERADO_3:
        fallas.append(f"arreglo 3: {cuenta3}, la tabla dice {ESPERADO_3}")
    if otras3:
        fallas.append(f"arreglo 3 tocó otra parte del armado en {otras3}")
    if sin_arreglo:
        fallas.append(f"cambian sin arreglo que lo explique: {sin_arreglo}")

    L = ["# DIFF_PAPEL — Wittenoom re-armado en seco (F50b)", "",
         "Salida de `python lab/hyperframes/f50b/rearmar.py`: los casilleros guardados en `03_visual.json` → `armar` → "
         "F8 → backstop de texto, con los arreglos 1–3 del handoff F50b. Cero llamadas a modelos, cero fal.", "",
         "## Verificación automática", "",
         f"- Fotos: {len(guardado)} · cambian: {len(cambian)} · iguales: {len(guardado) - len(cambian)}",
         f"- Arreglo 1 (`HARM`): {len(por[1])} fotos {sorted(por[1])} · tabla {sorted(ESPERADO[1])}",
         f"- Arreglo 2 (cláusulas negadas): {len(por[2])} fotos {sorted(por[2])} · tabla {sorted(ESPERADO[2])}",
         f"- Arreglo 3 (minúscula en mitad de oración): {len(por[3])} fotos · oración de plano {cuenta3['tecnica']} "
         f"(tabla 29) · carteles {cuenta3['texto']} (tabla 2) · otras partes tocadas: {otras3 or 'ninguna'}",
         f"- Cambios sin arreglo que los explique: {sin_arreglo or 'ninguno'}",
         f"- **Resultado: {'PASA' if not fallas else 'FALLA — PARADA'}**", ""]
    L += [f"  - {f}" for f in fallas]
    L += ["", "## Fotos que cambian", ""]
    for k in cambian:
        arr = [str(a) for a in (1, 2, 3) if k in por[a]]
        L += [f"### Cap {k[0]} · foto {k[1]} — arreglo {', '.join(arr)}"
              + (f" (partes: {', '.join(partes3[k])})" if k in partes3 else ""), "",
              *[f"- sale: «{x}»" for x in frases(guardado[k]) if x not in frases(nuevo[k][0])],
              *[f"- entra: «{x}»" for x in frases(nuevo[k][0]) if x not in frases(guardado[k])],
              f"- antes: {guardado[k]}", f"- después: {nuevo[k][0]}", ""]
    (F50B / "DIFF_PAPEL.md").write_text("\n".join(L), encoding="utf-8")
    (F50B / "DIFF_PAPEL.json").write_text(json.dumps(
        {"cambian": [list(k) for k in cambian], "por_arreglo": {a: sorted(map(list, s)) for a, s in por.items()},
         "partes_arreglo_3": {f"{k[0]}/{k[1]}": p for k, p in sorted(partes3.items())}, "fallas": fallas,
         "antes": {f"{k[0]}/{k[1]}": guardado[k] for k in cambian},
         "despues": {f"{k[0]}/{k[1]}": nuevo[k][0] for k in cambian}}, ensure_ascii=False, indent=1),
        encoding="utf-8")
    print(f"cambian {len(cambian)} · 1={len(por[1])} 2={len(por[2])} 3={len(por[3])} {cuenta3} · "
          f"{'PASA' if not fallas else 'FALLA: ' + ' | '.join(fallas)}")
    if fallas:
        return 1

    if "--escribir" in sys.argv:
        for cap in v["chapters"]:
            n = cap["chapter_number"]
            for i, (it, rol) in enumerate(fotos(cap), start=1):
                p = nuevo[(n, i)][0]
                if p == guardado[(n, i)]:
                    continue
                sens, mot = v3.is_body(p), sorted(v3.motifs_of(p))
                if rol == "veo0":
                    cap["image_prompt"], cap["image_sensible"] = p, sens
                    cap["image_f8"]["motivos"] = mot
                else:
                    it["prompt"], it["sensible"], it["motivos"] = p, sens, mot
        VISUAL.write_text(json.dumps(v, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"escrito {VISUAL.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
