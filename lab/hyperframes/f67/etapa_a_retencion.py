# -*- coding: utf-8 -*-
"""F67 Etapa A: corre el juez m05 sobre Wittenoom (US$ 0; escribe solo 06_judge_narrative.json) y deja la salida en texto en
lab/hyperframes/f67/A_retencion.md: la tabla por cap, los bloques `pico` y `promesa`, la diferencia de palabras con el lab
(`words_of` vs `\\S+`) y que nada de lo que el juez ya medía cambió."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import steps_md5  # noqa: E402

TID = steps_md5.TID
D = steps_md5.STEPS
AQUI = Path(__file__).resolve().parent


def main() -> None:
    import fase1_5 as f15
    from script_engine.m05_narrative import judge_narration
    steps_md5.foto("A_antes")
    viejo = json.loads((D / "06_judge_narrative.json").read_text(encoding="utf-8"))
    rep = judge_narration(TID, pool=f15._topic_v3(TID)["evidence_pool"])
    steps_md5.foto("A_despues")
    nuevo = json.loads((D / "06_judge_narrative.json").read_text(encoding="utf-8"))
    r = rep["retencion"]
    cambian = [k for k in viejo if viejo[k] != nuevo.get(k)]
    lab = {"ch01": (161, 55, 8, 1), "ch02": (220, 75, 11, 3), "ch03": (523, 178, 27, 7), "ch04": (232, 79, 12, 1),
           "ch05": (292, 99, 15, 7), "ch06": (297, 101, 15, 4), "ch07": (216, 73, 11, 6)}
    n3 = json.loads((D / "01b_narracion_v3.json").read_text(encoding="utf-8"))
    from script_engine.voz_utils import oraciones_de_texto
    s_por_cap: dict[str, int] = {}
    for p in n3["parrafos"]:
        k = f"ch{int(p['cap']):02d}"
        s_por_cap[k] = s_por_cap.get(k, 0) + sum(len(re.findall(r"\S+", t)) for t in oraciones_de_texto(p["texto"]))
    L = ["# F67 Etapa A — retención en el juez m05 (Wittenoom)", "",
         f"`seg_por_palabra` {r['seg_por_palabra']} · total {r['total_palabras']} palabras (`words_of`) ≈ {r['total_min']} min · personaje según la escaleta: "
         f"{r['personaje']['id']} {r['personaje']['nombre']}, términos {r['personaje']['terminos']} · cap más humano: {r['cap_mas_humano']}", "",
         "| cap | título | oraciones | palabras | s | % | % acum. | años | años/min | vs más humano | con personaje | racha sin él | desde–hasta | lab F67a (pal/s/%/años) | `\\S+` |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for c in r["caps"]:
        L.append(f"| {c['cap']} | {c['titulo']} | {c['oraciones']} | {c['palabras']} | {c['segundos']} | {c['pct']} | {c['pct_acumulado']} | {c['anios_distintos']} | "
                 f"{c['anios_por_min']} | {r['anios_por_min_vs_mas_humano'][c['cap']]} | {c['oraciones_con_personaje']} | {c['racha_max_sin_personaje']} | {c['racha_desde_hasta']} | "
                 f"{'/'.join(map(str, lab[c['cap']]))} | {s_por_cap[c['cap']]} |")
    L += ["", f"**Diferencia con el lab:** `words_of` {r['total_palabras']} contra `\\S+` {sum(s_por_cap.values())} (lab F67a: 1941). Se reporta, no se corrige (F67 §2).", "",
          "## Pico", "", "```json", json.dumps(r["pico"], ensure_ascii=False, indent=1), "```", "",
          "## Promesa", "", "```json", json.dumps(r["promesa"], ensure_ascii=False, indent=1), "```", "",
          "## Lo que el juez ya medía", "",
          f"Claves de `06_judge_narrative.json` antes: {sorted(viejo)}. Las que cambiaron de valor: {cambian or 'ninguna'}. Clave nueva: `retencion`.", "",
          "## Archivos del topic que cambiaron (md5)", "", "\n".join(f"- {x}" for x in steps_md5.compara('A_antes', 'A_despues')), ""]
    (AQUI / "A_retencion.md").write_text("\n".join(L), encoding="utf-8", newline="\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
