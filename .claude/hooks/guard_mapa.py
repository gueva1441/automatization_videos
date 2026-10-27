"""F33 §D.3 — PreToolUse Bash/PowerShell: antes de `git commit`, si lo que entra toca `script_engine/gfx_*.py` (desde
F36 también `rotulista_*.py` —F37: `pantalla_*.py`—, `clima.py`, `voz_datos.py`, `voz_utils.py`) o `fase2b.py` y no toca `lab/MAPA_MODULOS.md`
ni `.json`, AVISA (no bloquea): el reporte de la tanda tiene que decir por qué el mapa no cambió (o regenerarlo con
`python lab/tools/mapa_modulos.py`).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _comun import comando, git, git_args, leer_evento, segmentos  # noqa: E402

TOCA = re.compile(r"^(script_engine/(gfx_[^/]*|pantalla_[^/]*|clima|voz_datos|voz_utils)\.py|fase2b\.py)$")   # F36 §A / F37 §B.5: + los de la pantalla
MAPA = ("lab/MAPA_MODULOS.md", "lab/MAPA_MODULOS.json")


def aviso(staged: list[str]) -> str | None:
    tocados = [f for f in staged if TOCA.match(f)]
    if not tocados or any(f in MAPA for f in staged):
        return None
    return (f"guard_mapa: el commit toca {', '.join(tocados)} y no toca lab/MAPA_MODULOS.md/.json — regenerar el mapa "
            f"(`python lab/tools/mapa_modulos.py`) o decir en el reporte por qué no cambió")


def main() -> None:
    ev = leer_evento()
    cwd = Path(ev.get("cwd") or ".")
    for w in segmentos(comando(ev)):
        sub, args, c = git_args(w)
        if sub != "commit":
            continue
        staged = [x for x in git(["diff", "--cached", "--name-only"], (cwd / c) if c else cwd).splitlines() if x]
        if any(a == "--all" or re.fullmatch(r"-[A-Za-z]*a[A-Za-z]*", a) for a in args):
            staged += [x for x in git(["diff", "--name-only"], (cwd / c) if c else cwd).splitlines() if x]
        msg = aviso(staged)
        if msg:
            sys.stdout.reconfigure(encoding="utf-8")
            print(json.dumps({"systemMessage": msg, "hookSpecificOutput": {"hookEventName": "PreToolUse",
                                                                             "additionalContext": msg}},
                             ensure_ascii=False))
        return


if __name__ == "__main__":
    main()
