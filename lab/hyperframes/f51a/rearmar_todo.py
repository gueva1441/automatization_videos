# -*- coding: utf-8 -*-
"""F51a — re-armado EN SECO de todas las fotos de Wittenoom con el `armar` nuevo (C: sujeto, aspecto, lugar_anio, texto,
luz, tecnica, estilo, cierre). Casilleros = el `raw_llm_prompt` + `anio` de cada foto del 03_visual.json de producción
→ `f50g/rearmar.rearmar_una` (armar → f8_backstop → _sacar_frases_con_texto), con `grupos` = `people_groups` del topic.
Antes = el `prompt` guardado (armado viejo). Una foto sin `raw_llm_prompt` no pasa por `armar`: se cuenta aparte.
Sin modelos, sin fal. No escribe 03_visual.json, ni el canon, ni topics_db: solo REARMADO_F51a.md.

Uso:
  python lab/hyperframes/f51a/rearmar_todo.py
"""
import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "lab" / "hyperframes" / "f50g"))
F51A = Path(__file__).resolve().parent
TID = "123bbb64-9fca-4395-8bf4-57d60e219ef1"
SALIDA = F51A / "REARMADO_F51a.md"


def palabras(p: str) -> int:
    return len((p or "").split())


def cf(k) -> str:
    return f"{k[0]}/{k[1]}"


def med_max(xs: list[int]) -> str:
    return f"{statistics.median(xs):g} · {max(xs)}" if xs else "— · —"


def bloque(titulo: str, k, antes: str, despues: str) -> list[str]:
    return [f"### {titulo}: {k[0]}/{k[1]}", "", f"**Antes** ({palabras(antes)} palabras)", "", "```", antes, "```", "",
            f"**Después** ({palabras(despues)} palabras)", "", "```", despues, "```", ""]


def main() -> int:
    import rearmar as rg
    from script_engine import m03_imagenes_v3 as v3
    from script_engine.topics_db import get_topic_by_id
    v = json.loads(rg.VISUAL.read_text(encoding="utf-8"))           # solo lectura
    topic = get_topic_by_id(TID)
    beats = v3.load_beats(topic, rg.STEPS)
    grupos = {g["id"]: g for g in topic.get("people_groups") or [] if isinstance(g, dict) and g.get("id")}
    documented = topic.get("documented_people")

    filas, sin_armar = [], []
    for cap in v["chapters"]:
        n = cap["chapter_number"]
        by_n = {b["n"]: b for b in beats.get(n) or []}
        for i, (it, rol) in enumerate(rg.fotos(cap), start=1):
            antes = it.get("prompt") or ""
            if not it.get("raw_llm_prompt"):                         # no pasa por armar: no se rearma
                sin_armar.append({"k": (n, i), "rol": rol, "antes": antes})
                continue
            escala = bool((by_n.get(it.get("beat")) or {}).get("escala"))
            despues, partes = rg.rearmar_una(it, escala, documented, grupos)
            pg = [g for g in json.loads(it["raw_llm_prompt"]).get("people_group") or [] if isinstance(g, str)]
            filas.append({"k": (n, i), "rol": rol, "antes": antes, "despues": despues, "partes": partes, "pg": pg})

    total = len(filas) + len(sin_armar)
    pa, pd = [palabras(f["antes"]) for f in filas], [palabras(f["despues"]) for f in filas]
    cambian = [f for f in filas if f["despues"] != f["antes"]]
    vacias = [f for f in filas if not f["despues"].strip() or not (f["partes"].get("sujeto") or "").strip()]
    por_k = {f["k"]: f for f in filas}
    f12 = por_k.get((1, 2))
    f2g = next((f for f in filas if len(f["pg"]) >= 2), None)
    fveo = next((f for f in filas if f["rol"] == "veo0"), None)

    L = ["# REARMADO_F51a — Wittenoom re-armado en seco con el `armar` nuevo (C)", "",
         "Salida de `PYTHONIOENCODING=utf-8 python lab/hyperframes/f51a/rearmar_todo.py`. Casilleros: el "
         "`raw_llm_prompt` y el `anio` de cada foto del `03_visual.json` de producción de Wittenoom → "
         "`f50g/rearmar.rearmar_una` (armar → f8_backstop → _sacar_frases_con_texto), con `grupos` = `people_groups` "
         "del topic. Antes = el `prompt` guardado (armado viejo); después = el re-armado. Palabras = "
         "`len(prompt.split())`. Cero llamadas a modelos, cero fal; no se escribe producción.", "",
         "## Resumen", "",
         f"- Fotos: {total} · pasan por `armar`: {len(filas)} · no pasan (sin `raw_llm_prompt`): {len(sin_armar)}"
         + (" (" + ", ".join(cf(s["k"]) + " " + s["rol"] for s in sin_armar) + ")" if sin_armar else ""),
         f"- Palabras antes, mediana · máx: {med_max(pa)}",
         f"- Palabras después, mediana · máx: {med_max(pd)}",
         f"- Cambian (después ≠ antes): {len(cambian)}/{len(filas)}",
         f"- Prompt nuevo vacío o sin `sujeto`: "
         + (", ".join(cf(f["k"]) for f in vacias) if vacias else "ninguna"), "",
         "## Prompts enteros", ""]
    L += bloque("Cap 1, foto 2", f12["k"], f12["antes"], f12["despues"]) if f12 else ["La 1/2 no pasa por `armar`.", ""]
    L += (bloque(f"Con 2 grupos ({', '.join(f2g['pg'])})", f2g["k"], f2g["antes"], f2g["despues"]) if f2g
          else ["Ninguna foto tiene 2 grupos o más en `people_group`.", ""])
    L += (bloque("Veo (rol veo0)", fveo["k"], fveo["antes"], fveo["despues"]) if fveo
          else ["Ningún cuadro Veo (rol veo0) pasa por `armar`.", ""])
    L += ["## Por foto", "", "| foto | rol | palabras antes | después | cambia |", "|---|---|---:|---:|---|"]
    L += [f"| {f['k'][0]}/{f['k'][1]} | {f['rol']} | {palabras(f['antes'])} | {palabras(f['despues'])} | "
          f"{'sí' if f['despues'] != f['antes'] else 'no'} |" for f in filas]
    L += [f"| {s['k'][0]}/{s['k'][1]} | {s['rol']} | {palabras(s['antes'])} | — (no pasa por armar) | — |"
          for s in sin_armar]
    SALIDA.write_text("\n".join(L) + "\n", encoding="utf-8")

    print(f"fotos {total} · por armar {len(filas)} · sin armar {len(sin_armar)} "
          + str([cf(s["k"]) for s in sin_armar]))
    print(f"palabras antes med·máx {med_max(pa)} · después {med_max(pd)} · cambian {len(cambian)}/{len(filas)}")
    print("vacías o sin sujeto: " + (", ".join(cf(f["k"]) for f in vacias) or "ninguna"))
    print(f"enteros: 1/2 {'sí' if f12 else 'no'} · 2 grupos {f2g['k'] if f2g else 'ninguna'} · "
          f"veo0 {fveo['k'] if fveo else 'ninguna'}")
    print(f"escrito {SALIDA.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
