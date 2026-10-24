"""F22 §5.1 — md5 de los archivos del handoff vs lo que quedó en código, y el diff línea a línea de cada prompt
(viejo → nuevo). Sin API. Escribe `PROMPTS_f22_diff.md` (lo pega F22_REPORT.md).
Uso: python -I lab/hyperframes/f22/f22_diffs.py
"""
from __future__ import annotations

import difflib
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LAB = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))


def _md5(s: str) -> str:
    return hashlib.md5(s.encode("utf-8")).hexdigest()


def _sistema(name: str) -> str:
    md = (LAB / name).read_text(encoding="utf-8").replace("\r\n", "\n")
    i = md.index("\n## SISTEMA\n\n") + len("\n## SISTEMA\n\n")
    return md[i:md.index("\n\n---\n", i)]


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    from researcher_steps import ficha_caso as fc
    from researcher_steps import research_v3 as r3  # noqa: F401
    from script_engine import guion_v4 as g4
    from script_engine import m01a_columna as mc
    from script_engine import m01a_escaleta as me
    archivos = ["HANDOFF_F22_ejemplos_y_antagonista.md", "CASO_EJEMPLO_cardal.md", "PROMPT_FICHA_v2_1.md",
                "PROMPT_COLUMNA_v1_1.md", "PROMPT_ESCALETA_v2_1.md", "PROMPT_GUIONISTA_v5_2.md"]
    L = ["# F22 — md5 y diff de los prompts", "", "## md5 de los archivos del handoff", "", "| archivo | md5 |", "|---|---|"]
    L += [f"| {a} | `{hashlib.md5((LAB / a).read_bytes()).hexdigest()}` |" for a in archivos]
    prompts = [("ficha", "PROMPT_FICHA_v2_1.md", "ficha_caso.system(\"f15-1\") (f15-1)", fc.system("f15-1"),
                "ficha_caso.system() (f22-1)", fc.system()),
               ("columna", "PROMPT_COLUMNA_v1_1.md", "m01a_columna.SYSTEM_F17_1 (f17-1)", mc.SYSTEM_F17_1,
                "m01a_columna.SYSTEM (f22-1)", mc.SYSTEM),
               ("columna (tarea)", None, "m01a_columna.TAREA_F17_1", mc.TAREA_F17_1, "m01a_columna.TAREA", mc.TAREA),
               ("escaleta", "PROMPT_ESCALETA_v2_1.md", "m01a_escaleta.SYSTEM_V2_F16_1 (f16-1)", me.SYSTEM_V2_F16_1,
                "m01a_escaleta.SYSTEM_V2 (f22-1)", me.SYSTEM_V2),
               ("guion", "PROMPT_GUIONISTA_v5_2.md", "guion_v4.system(\"f15b-1\") (v5.1)", g4.system("f15b-1"),
                "guion_v4.system() (v5.2, f22-1)", g4.system())]
    L += ["", "## Bloque SISTEMA del archivo vs código", "",
          "| prompt | md5 del bloque `## SISTEMA` del archivo | md5 en código | igual | md5 del viejo (sigue en código) |",
          "|---|---|---|---|---|"]
    for nom, arch, _, old, _, new in prompts:
        if arch:
            b = _sistema(arch)
            L.append(f"| {nom} | `{_md5(b)}` | `{_md5(new)}` | {'sí' if b == new else '**NO**'} | `{_md5(old)}` |")
    for nom, _, on, old, nn, new in prompts:
        a, b = old.split("\n"), new.split("\n")
        d = list(difflib.unified_diff(a, b, on, nn, n=0, lineterm=""))
        L += ["", f"## Diff {nom}: {on} → {nn}", "",
              f"{sum(1 for x in d if x.startswith('-') and not x.startswith('---'))} líneas salen, "
              f"{sum(1 for x in d if x.startswith('+') and not x.startswith('+++'))} entran "
              f"(de {len(a)} → {len(b)} líneas). Cada línea del prompt es un párrafo entero.", "", "```diff"]
        L += d + ["```"]
    (LAB / "PROMPTS_f22_diff.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("PROMPTS_f22_diff.md", len(L), "líneas")


if __name__ == "__main__":
    main()
