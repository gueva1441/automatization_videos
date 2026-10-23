"""F10 §4.2: entregas del guion de Ycuá Bolaños desde los pasos de `fase1_5 --v3` (no llama a ningún LLM).

Uso: python -I lab/hyperframes/f10/f10_ycua_docs.py
Escribe en lab/hyperframes/f10/: ESCALETA_ycua.md, NARRACION_ycua.md (por beat, con `narration_tts`), 06_judge_ycua.json,
costo_guion_ycua.json y copias de 01a_escaleta / 01a_skeleton / 01b_narration (los pasos viven fuera de git).
"""
from __future__ import annotations

import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
TOPIC = "f8s1-ycua-bolanos"
LAB = Path(__file__).resolve().parent


def wc(s: str) -> int:
    return len(re.findall(r"[\wáéíóúñü]+", s or "", re.I))


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")                # -I ignora PYTHONIOENCODING
    from script_engine import m01a_escaleta as me
    from script_engine.m01a_skeleton import STEPS_DIR
    d = STEPS_DIR / TOPIC
    ld = lambda f: json.loads((d / f).read_text(encoding="utf-8"))  # noqa: E731
    esc, sk, na, n3, ed = (ld("01a_escaleta.json"), ld("01a_skeleton.json"), ld("01b_narration.json"),
                           ld("01b_narracion_v3.json"), ld("01b_editor_v3.json"))
    judge = ld("06_judge_narrative.json")
    costs = ld("01_v3_costos.json")
    pool = json.loads((d / "00_pool_v3.json").read_text(encoding="utf-8"))
    (LAB / "ESCALETA_ycua.md").write_text(
        me.to_markdown(esc, pool) + f"\n---\nIntentos de la escaleta: {len(esc.get('_intentos') or [])} · avisos: "
        f"{len(esc.get('_avisos') or [])}\n", encoding="utf-8")
    beats = {b["n"]: b for b in esc["beats"]}
    tts = {c["chapter_number"]: c["narration_tts"] for c in na["chapters"]}
    total = sum(wc(c["narration"]) for c in na["chapters"])
    rv = ed.get("revision_despues") or {}
    lines = [f"# Narración — Ycuá Bolaños (guion v3, F10)", "",
             f"**{total} palabras** (objetivo 1,500; tope 1,700) · títulos de cap: "
             + " · ".join(f"{c['chapter_number']}. {c['title']}" for c in sk["chapters"]), "",
             f"Duras que quedan después del editor: {len(rv.get('hard') or [])} · cambios del editor aceptados: "
             f"{ed.get('aceptados')} de {len(ed.get('cambios') or [])}", ""]
    for x in rv.get("hard") or []:
        lines.append(f"- dura: {x}")
    lines.append("")
    for c in sk["chapters"]:
        n = c["chapter_number"]
        nc = next(x for x in na["chapters"] if x["chapter_number"] == n)
        lines += [f"## Cap {n} — {c['title']} ({c['role']}, {c['narrative_intent']}) · {wc(nc['narration'])} palabras", ""]
        for p in [p for p in n3["parrafos"] if p["cap"] == n]:
            b = beats.get(p["beat"], {})
            lines += [f"**Beat {p['beat']}** · {b.get('funcion')} · {b.get('emocion')} {b.get('intensidad')} · "
                      f"«{b.get('imagen_sensorial')}» · ids {', '.join(p.get('ids_usados') or [])}", "", p["texto"], ""]
        lines += ["<details><summary>narration_tts (lo que lee la voz v4)</summary>", "", "```", tts[n], "```", "",
                  "</details>", ""]
    (LAB / "NARRACION_ycua.md").write_text("\n".join(lines), encoding="utf-8")
    (LAB / "06_judge_ycua.json").write_text(json.dumps(judge, ensure_ascii=False, indent=1), encoding="utf-8")
    runs = costs.get("_corridas") or []
    (LAB / "costo_guion_ycua.json").write_text(json.dumps({"corridas": runs, "usd_total": round(sum(r["usd"] for r in runs), 4)},
                                                         ensure_ascii=False, indent=1), encoding="utf-8")
    for f in ("01a_escaleta.json", "01a_skeleton.json", "01b_narration.json"):
        shutil.copy2(d / f, LAB / f"ycua_{f}")
    print(f"palabras {total} · duras {len(rv.get('hard') or [])} · US$ {sum(r['usd'] for r in runs):.3f}")


if __name__ == "__main__":
    main()
