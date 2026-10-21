"""F4e: arma gfx_profiles/misterio_critico_fewshot.json — 5 bloques del plan dorado de ch02 (aprobados por Omar en el
lab) con la frase que dice la voz en ese instante (de los subtítulos de ch02). Se corre una vez; el crítico lo lee.
Uso: PYTHONIOENCODING=utf-8 python lab/hyperframes/f4e/armar_fewshot_critico.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
ASS = ROOT / "output" / "ba6c3cac-a091-41c0-8dad-afd2f4364747" / "_fase2b_work" / "ch02_subs.ass"
GOLDEN = ROOT / "gfx_profiles" / "misterio_golden_ch02.json"
OUT = ROOT / "gfx_profiles" / "misterio_critico_fewshot.json"


def _sec(ts: str) -> float:
    h, m, s = ts.split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)


def lines() -> list[tuple[float, float, str]]:
    out = []
    for ln in ASS.read_text(encoding="utf-8").splitlines():
        if not ln.startswith("Dialogue:"):
            continue
        f = ln.split(",", 9)
        txt = re.sub(r"\{[^}]*\}", "", f[9]).strip()
        if not out or out[-1][2] != txt:
            out.append((_sec(f[1]), _sec(f[2]), txt))
        else:
            out[-1] = (out[-1][0], _sec(f[2]), txt)
    return out


def voice_at(t: float, span: float = 3.0) -> str:
    return " ".join(x for a, b, x in lines() if b > t - 0.5 and a < t + span).capitalize()


def main() -> None:
    from script_engine.gfx_critic import describe
    plan = json.loads(GOLDEN.read_text(encoding="utf-8"))["plan"]
    picks = [("recorte", plan["archive_clippings"][0]), ("nivel_agua", plan["water_level"]),
             ("dato", plan["callouts"][0]), ("zoom", plan["evidence_zoom"]), ("recorte", plan["archive_clippings"][1])]
    ex = [{"bloque": describe(kind, b), "voz": voice_at(float(b["start"])), "veredicto": "suma",
           "motivo": "aprobado por Omar en el plan dorado de ch02"} for kind, b in picks]
    OUT.write_text(json.dumps({"fuente": "misterio_golden_ch02.json (Omar, 2026-10-20 01:20)", "ejemplos": ex},
                              ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    for e in ex:
        print(e["bloque"], "|", e["voz"])


if __name__ == "__main__":
    main()
