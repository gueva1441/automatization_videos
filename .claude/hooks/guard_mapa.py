"""F42 §C.4 (antes F33 §D.3, solo gfx) — PreToolUse Bash/PowerShell: antes de `git commit` corre el chequeo del mapa del
proyecto (`lab/tools/mapa_modulos.py --check`, en proceso: md5 de cada archivo de producción contra el de su sticker en
`lab/mapa/stickers/<zona>.json`). Si un archivo de producción que entra en el commit no tiene sticker o lo tiene viejo,
AVISA (no bloquea): releer el archivo, reescribir su sticker y regenerar `lab/MAPA_PROYECTO.md` (`python
lab/tools/mapa_modulos.py`), o decir en el reporte por qué el mapa no cambió. Vale para cualquier archivo de producción,
no solo gfx.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _comun import ROOT, comando, git, git_args, leer_evento, segmentos  # noqa: E402

sys.path.insert(0, str(ROOT / "lab" / "tools"))


def aviso(staged: list[str]) -> str | None:
    try:
        import mapa_modulos as mm
        fallas = mm.check()
    except Exception as e:  # noqa: BLE001 — el hook nunca tira el commit
        return f"guard_mapa: no pude correr `mapa_modulos.py --check` ({type(e).__name__}: {e})"
    if not fallas:
        return None
    del_commit = [f for f in fallas if any(f"{s} " in f or f.endswith(s) for s in staged)]
    if not del_commit:
        return None
    return (f"guard_mapa: el commit toca archivos de producción con sticker viejo o sin sticker — "
            f"{'; '.join(del_commit[:8])}{' …' if len(del_commit) > 8 else ''}. Releer el archivo, reescribir su "
            f"sticker en lab/mapa/stickers/ y regenerar el mapa (`python lab/tools/mapa_modulos.py`), o decir en el "
            f"reporte por qué no cambió. (`--check` da {len(fallas)} fallas en total.)")


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
