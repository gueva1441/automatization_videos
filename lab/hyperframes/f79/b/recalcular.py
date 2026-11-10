"""F79 Etapa B: recalcula `narration_tts` de Wittenoom y Colza con la función de producción, SIN escribir en data/.

Mismos insumos que m01d_particion.build_contract: `01a_escaleta.json`, los párrafos de `01b_narracion_v3.json`,
`m01b_guionista.caps_text`, `m01c_editor.narration_tts` (→ `tts_tags.caps_tts`) con `slowly_dev=False`.

Uso: python lab/hyperframes/f79/b/recalcular.py <etiqueta>     (antes | despues)
Escribe lab/hyperframes/f79/b/<etiqueta>_<topic>.json (narration_tts y conteo de etiquetas por cap) e imprime la tabla y
el md5 del 01b_narration.json guardado (que no se toca).
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(RAIZ))

from script_engine import m01b_guionista as mg  # noqa: E402
from script_engine.m01c_editor import narration_tts  # noqa: E402
from script_engine.tts_tags import LONG, QUIET, SHORT, SLOW, WHISPER  # noqa: E402

TOPICS = {"wittenoom": "123bbb64-9fca-4395-8bf4-57d60e219ef1", "colza": "c4934b7d-3f54-448f-ba5f-539dc744f0d8"}
AQUI = Path(__file__).resolve().parent


def main(etiqueta: str) -> int:
    for nombre, tid in TOPICS.items():
        steps = RAIZ / "data" / "scripts" / "_steps" / tid
        esc = json.loads((steps / "01a_escaleta.json").read_text(encoding="utf-8"))
        parrafos = json.loads((steps / "01b_narracion_v3.json").read_text(encoding="utf-8"))["parrafos"]
        guardado = steps / "01b_narration.json"
        md5 = hashlib.md5(guardado.read_bytes()).hexdigest()
        caps = narration_tts(esc, parrafos, mg.caps_text(esc, parrafos), slowly_dev=False)
        citas = [sum(1 for s in mg.sentences(c["narration"]) if "«" in s or "“" in s) for c in caps]
        filas = [{"cap": c["chapter_number"], "tags": c["tts_tags"], "oraciones_con_cita": citas[i],
                  "narration_tts": c["narration_tts"]} for i, c in enumerate(caps)]
        (AQUI / f"{etiqueta}_{nombre}.json").write_text(
            json.dumps({"topic": tid, "md5_01b_narration": md5, "caps": filas}, ensure_ascii=False, indent=1),
            encoding="utf-8")
        tot = {t: sum(f["tags"][t] for f in filas) for t in (LONG, SHORT, QUIET, WHISPER, SLOW)}
        print(f"## {nombre} ({tid}) — {etiqueta} · md5 01b_narration.json {md5}")
        print("| etiqueta | total | por cap |")
        print("|---|---|---|")
        for t in (LONG, SHORT, QUIET, WHISPER, SLOW):
            print(f"| `{t}` | {tot[t]} | {', '.join(str(f['tags'][t]) for f in filas)} |")
        print(f"| oraciones con cita | {sum(citas)} | {', '.join(map(str, citas))} |\n")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv[1]))
