# -*- coding: utf-8 -*-
"""F50g-A §2–3 — re-armado EN SECO de las 96 fotos de Wittenoom con el aspecto del canon: los casilleros guardados en el
03_visual.json de producción (`raw_llm_prompt` + el `anio` de cada foto) → `armar(slots, anio, grupos)` → F8 →
backstop de texto legible, igual que `m03_visual._render_prompts_seedream`. `grupos` = `people_groups` del topic de
producción (el canon de 05_visual_canon.json). Sin modelos, sin fal.

Uso:
  python lab/hyperframes/f50g/rearmar.py --igual     # con grupos = {} (sin aspecto), ¿sale cada prompt guardado?
  python lab/hyperframes/f50g/rearmar.py             # REARMADO_F50g.md/.json + verificación (no escribe producción)
  python lab/hyperframes/f50g/rearmar.py --escribir  # además copia 03_visual.json a antes/ y escribe
                                                     # prompt/sensible/motivos en las fotos que cambian

Verificación: el re-armado sin grupos = el guardado (96/96), y el re-armado con grupos menos el texto del aspecto =
el re-armado sin grupos (salvo espacios), foto por foto.
"""
import json
import re
import shutil
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
F50G = Path(__file__).resolve().parent
TID = "123bbb64-9fca-4395-8bf4-57d60e219ef1"
STEPS = ROOT / "data" / "scripts" / "_steps"
VISUAL = STEPS / TID / "03_visual.json"            # el de producción, vivo: de acá salen casilleros y prompts
ANTES = F50G / "antes" / "03_visual.json"          # copia de antes de escribir (solo con --escribir)


def fotos(cap: dict) -> list[tuple[dict, str]]:
    """[(ítem, rol)] en el orden del papel."""
    if cap.get("image_prompts") is not None:
        return [(it, "flux") for it in cap["image_prompts"]]
    f0 = {**(cap.get("image_f8") or {}), "prompt": cap.get("image_prompt")}
    return [(f0, "veo0")] + [(it, "supp") for it in cap.get("supplemental_image_prompts") or []]


def palabras(p: str) -> int:
    return len((p or "").split())


def sin_esp(p: str) -> str:
    return re.sub(r"\s+", "", p or "")


def rearmar_una(it: dict, escala: bool, documented, grupos: dict) -> tuple[str, dict]:
    from script_engine import m03_imagenes_v3 as v3
    from script_engine.m03_visual import _sacar_frases_con_texto
    slots = json.loads(it["raw_llm_prompt"])
    armado = v3.armar(slots, it["anio"], grupos)
    prose, _ = v3.f8_backstop(armado["prompt"], slots, escala, documented)
    tii = slots.get("text_in_image") or {}
    prose, _ = _sacar_frases_con_texto(prose, (tii.get("text") or "") if tii.get("present") else "")
    return prose, armado["partes"]


def correr(v: dict, topic: dict, beats, grupos: dict) -> dict:
    out = {}
    for cap in v["chapters"]:
        n = cap["chapter_number"]
        by_n = {b["n"]: b for b in beats.get(n) or []}
        for i, (it, rol) in enumerate(fotos(cap), start=1):
            esc = bool((by_n.get(it.get("beat")) or {}).get("escala"))
            out[(n, i)] = rearmar_una(it, esc, topic.get("documented_people"), grupos)
    return out


def stats(keys, guardado, nuevo, partes, n_grupos) -> dict:
    pa = [palabras(guardado[k]) for k in keys]
    pd = [palabras(nuevo[k][0]) for k in keys]
    con = sum(1 for k in keys if partes[k]["aspecto"])
    return {"fotos": len(keys), "con": con, "sin": len(keys) - con,
            "antes_med": statistics.median(pa) if pa else 0, "antes_max": max(pa, default=0),
            "despues_med": statistics.median(pd) if pd else 0, "despues_max": max(pd, default=0),
            "g0": sum(1 for k in keys if n_grupos[k] == 0), "g1": sum(1 for k in keys if n_grupos[k] == 1),
            "g2": sum(1 for k in keys if n_grupos[k] >= 2)}


def fila(nombre, s) -> str:
    return (f"| {nombre} | {s['fotos']} | {s['con']} | {s['sin']} | {s['antes_med']:g} | {s['antes_max']} | "
            f"{s['despues_med']:g} | {s['despues_max']} | {s['g0']} | {s['g1']} | {s['g2']} |")


def main() -> int:
    from script_engine import m03_imagenes_v3 as v3
    from script_engine.topics_db import get_topic_by_id
    v = json.loads(VISUAL.read_text(encoding="utf-8"))
    topic = get_topic_by_id(TID)
    beats = v3.load_beats(topic, STEPS)
    grupos = {g["id"]: g for g in topic.get("people_groups") or [] if isinstance(g, dict) and g.get("id")}
    guardado = {(c["chapter_number"], i): it["prompt"] for c in v["chapters"] for i, (it, _) in enumerate(fotos(c), 1)}
    items = {(c["chapter_number"], i): it for c in v["chapters"] for i, (it, _) in enumerate(fotos(c), 1)}

    sin = correr(v, topic, beats, {})
    dif = [k for k in guardado if sin[k][0] != guardado[k]]
    if "--igual" in sys.argv:
        print(f"fotos {len(guardado)} · iguales {len(guardado) - len(dif)} · distintas {dif}")
        return 0 if not dif else 1

    nuevo = correr(v, topic, beats, grupos)
    pg = {k: [g for g in json.loads(items[k]["raw_llm_prompt"]).get("people_group") or [] if isinstance(g, str)]
          for k in guardado}
    n_grupos = {k: len(pg[k]) for k in guardado}
    faltan = sorted({g for k in guardado for g in pg[k] if g not in grupos})
    sin_app = sorted({g for k in guardado for g in pg[k] if g in grupos and not grupos[g].get("appearance")})
    partes = {k: nuevo[k][1] for k in guardado}

    # con-grupos menos el texto del aspecto = sin-grupos (salvo espacios)
    cumple, no_cumple = [], []
    for k in guardado:
        asp = partes[k]["aspecto"]
        quitado = nuevo[k][0].replace(asp, "", 1) if asp and asp in nuevo[k][0] else nuevo[k][0]
        ok = sin_esp(quitado) == sin_esp(sin[k][0]) and (not asp or asp in nuevo[k][0])
        (cumple if ok else no_cumple).append(k)
    cambian = sorted(k for k in guardado if nuevo[k][0] != guardado[k])

    caps = sorted({k[0] for k in guardado})
    por_cap = {n: stats([k for k in guardado if k[0] == n], guardado, nuevo, partes, n_grupos) for n in caps}
    total = stats(list(guardado), guardado, nuevo, partes, n_grupos)
    veo0 = [(c["chapter_number"], 1) for c in v["chapters"] if c.get("image_prompts") is None]
    sin_veo0 = stats([k for k in guardado if k not in veo0], guardado, nuevo, partes, n_grupos)
    fallas = []
    if dif:
        fallas.append(f"sin grupos no reproduce lo guardado en {dif}")
    if no_cumple:
        fallas.append(f"con grupos − aspecto ≠ sin grupos en {no_cumple}")

    cab = ["| cap | fotos | con aspecto | sin aspecto | palabras antes med | antes máx | después med | después máx "
           "| 0 grupos | 1 grupo | 2+ grupos |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    tabla = cab + [fila(str(n), por_cap[n]) for n in caps] + [fila("**total**", total),
                                                               fila(f"total sin {', '.join(f'{a}/{b}' for a, b in veo0)}",
                                                                    sin_veo0)]
    L = ["# REARMADO_F50g — Wittenoom re-armado en seco con el aspecto del canon (F50g-A)", "",
         "Salida de `python lab/hyperframes/f50g/rearmar.py`: los casilleros guardados en el `03_visual.json` de "
         "producción → `armar(slots, anio, grupos)` → F8 → backstop de texto, con `grupos` = `people_groups` del topic. "
         "Cero llamadas a modelos, cero fal. Palabras = `len(prompt.split())`; antes = el prompt guardado, después = "
         "el re-armado con grupos.", "",
         "## Tabla", "", *tabla, "",
         f"Primeros cuadros Veo (rol `image_f8`): {', '.join(f'{a}/{b}' for a, b in veo0)} — la última fila los excluye.",
         "", "## Verificación automática", "",
         f"- Re-armado con grupos = {{}} contra el guardado: {len(guardado) - len(dif)}/{len(guardado)} iguales"
         + (f" · distintas {dif}" if dif else ""),
         f"- Con grupos menos el texto del aspecto = sin grupos (salvo espacios): {len(cumple)}/{len(guardado)}"
         + (f" · no cumplen {no_cumple}" if no_cumple else ""),
         f"- Fotos que cambian con grupos: {len(cambian)}",
         f"- Ids de `people_group` que no están en el canon: {faltan or 'ninguno'}",
         f"- Ids presentes en fotos pero sin `appearance` en el canon: {sin_app or 'ninguno'}",
         f"- **Resultado: {'PASA' if not fallas else 'FALLA — PARADA'}**", ""]
    L += [f"  - {f}" for f in fallas]
    L += ["", "## Fotos con aspecto", ""]
    for k in sorted(guardado):
        if partes[k]["aspecto"]:
            L += [f"- {k[0]}/{k[1]} · {', '.join(pg[k])} · {palabras(guardado[k])} → {palabras(nuevo[k][0])} palabras"]
    (F50G / "REARMADO_F50g.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    (F50G / "REARMADO_F50g.json").write_text(json.dumps(
        {"por_cap": por_cap, "total": total, "total_sin_veo0": sin_veo0, "veo0": [f"{a}/{b}" for a, b in veo0],
         "igual_sin_grupos": len(guardado) - len(dif), "distintas_sin_grupos": [f"{a}/{b}" for a, b in dif],
         "resta_aspecto_cumple": len(cumple), "resta_aspecto_no_cumple": [f"{a}/{b}" for a, b in no_cumple],
         "ids_fuera_del_canon": faltan, "ids_sin_appearance": sin_app, "fallas": fallas,
         "fotos": {f"{k[0]}/{k[1]}": {"people_group": pg[k], "aspecto": partes[k]["aspecto"],
                                      "palabras_antes": palabras(guardado[k]), "palabras_despues": palabras(nuevo[k][0]),
                                      "antes": guardado[k], "despues": nuevo[k][0]} for k in sorted(guardado)}},
        ensure_ascii=False, indent=1), encoding="utf-8")

    print("\n".join(tabla))
    print(f"sin grupos = guardado {len(guardado) - len(dif)}/{len(guardado)} · resta del aspecto {len(cumple)}/"
          f"{len(guardado)} · cambian {len(cambian)} · ids fuera del canon {faltan or 'ninguno'} · "
          f"ids sin appearance {sin_app or 'ninguno'} · {'PASA' if not fallas else 'FALLA: ' + ' | '.join(fallas)}")
    if fallas:
        return 1

    if "--escribir" in sys.argv:
        if ANTES.exists():
            print(f"ya existe {ANTES.relative_to(ROOT)}: no se pisa, no se escribe nada")
            return 1
        ANTES.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(VISUAL, ANTES)
        print(f"copiado {VISUAL.relative_to(ROOT)} → {ANTES.relative_to(ROOT)}")
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
