"""F23 §5.4 — md5 de los dos prompts del handoff vs lo que quedó en código, y el diff línea a línea (viejo → nuevo):
ficha v2.1 (f22-1) → v2.2 (f23-1) y guion v5.2 (f22-1) → v5.3 (f23-1). Escaleta y columna: md5 sin cambio. Sin API.
Escribe `PROMPTS_f23_diff.md` (lo pega F23_REPORT.md).
Uso: python -I lab/hyperframes/f23/f23_diffs.py
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
    from script_engine import guion_v4 as g4
    from script_engine import m01a_columna as mc
    from script_engine import m01a_escaleta as me
    L = ["# F23 — md5 y diff de los prompts", "", "## md5", "", "| prompt | archivo (md5 del archivo) | bloque SISTEMA | "
         "código | igual |", "|---|---|---|---|---|"]
    for nom, arch, cod in (("ficha v2.2", "PROMPT_FICHA_v2_2.md", fc.system()),
                           ("guion v5.3", "PROMPT_GUIONISTA_v5_3.md", g4.system())):
        b = _sistema(arch)
        L.append(f"| {nom} | {arch} (`{hashlib.md5((LAB / arch).read_bytes()).hexdigest()}`) | `{_md5(b)}` | "
                 f"`{_md5(cod)}` | {'sí' if b == cod else '**NO**'} |")
    L += ["", f"Sin cambio: escaleta `SYSTEM_V2` (f22-2) `{_md5(me.SYSTEM_V2)}`, columna `SYSTEM` `{_md5(mc.SYSTEM)}`.", ""]
    for nom, va, a, vb, b in (("ficha", "f22-1", fc.system("f22-1"), "f23-1", fc.system()),
                              ("guion", "f22-1 (v5.2)", g4.system("f22-1"), "f23-1 (v5.3)", g4.system())):
        L += [f"## {nom}: {va} → {vb}", "", "```diff"]
        L += [x.rstrip("\n") for x in difflib.unified_diff(a.split("\n"), b.split("\n"), va, vb, n=0, lineterm="")]
        L += ["```", ""]
    (LAB / "PROMPTS_f23_diff.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
