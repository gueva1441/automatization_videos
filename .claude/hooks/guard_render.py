"""F33 §B.2 — PreToolUse Bash/PowerShell: bloquea (exit 2) `fase2b … --gfx` si el `output/<topic>/GUION_PANTALLA.json`
no existe, no tiene `aprobado` o su `md5_planes` no coincide con los planes de hoy (script_engine/aprobacion.py).
No pasan por el hook: `--plan-only`, `--plan-edit`, `--aprobar-guion`, `--only-cap … --gfx-debug` y todo fase2b sin
`--gfx` (el candado md5 de ch02 es `--only-cap ch02` sin `--gfx`). `--dry-run` no es salida: también se bloquea.
Los cuerpos de heredoc y los comandos de texto (echo, grep, git…) no cuentan; los prefijos (timeout, nohup, cmd /c…) y
`bash -c "…"` no salvan al comando.
Límite: ve el comando escrito en la herramienta, no lo que un runner de lab lanza por dentro (runpy/subprocess).
"""
from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _comun import ROOT, bloquear, comando, leer_evento, segmentos  # noqa: E402

CON_VALOR = {"--hook", "--gfx-quality", "--only-cap", "--gfx-workers", "--rotulista-tope", "--rotulista-modelo",
             "--forma-variante", "--limit", "--plan-edit", "--aprobar-guion"}
SIN_HOOK = {"--plan-only", "--plan-edit", "--aprobar-guion"}


def _aprobacion():
    spec = importlib.util.spec_from_file_location("aprobacion", ROOT / "script_engine" / "aprobacion.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# comandos cuyos argumentos son texto (lo que mencionan no corre); cualquier otro prefijo (timeout, nohup, time, env,
# cmd /c, start…) no salva al comando: se mira igual si adentro corre fase2b
TEXTO = {"echo", "printf", "grep", "rg", "git", "sed", "awk", "cat", "head", "tail", "write-output", "write-host",
         "select-string", "findstr"}
_HEREDOC = re.compile(r"<<-?\s*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\1[^\n]*\n.*?\n\s*\2\s*(?=\n|$)", re.S)


def sin_heredocs(cmd: str) -> str:
    """El comando sin el cuerpo de sus heredocs (`<<'X' … X`): lo que se escribe a un archivo no corre."""
    return _HEREDOC.sub(" ", cmd)


def llamada_fase2b(w: list[str]) -> list[str] | None:
    """Los argumentos de fase2b si el comando simple lo corre (`python fase2b.py …`, `python -m fase2b …`, también detrás
    de `timeout`, `nohup`, `cmd /c`…). Un comando de texto (echo, grep, git…) que solo lo menciona no cuenta; lo que va
    entre comillas como un comando entero (`bash -c "python fase2b.py …"`) se mira por dentro."""
    if not w or Path(w[0].strip("\"'")).name.lower() in TEXTO:
        return None
    for x in w:
        if " " in x and "fase2b" in x:                          # bash -c "…", powershell -Command "…"
            for w2 in segmentos(x):
                r = llamada_fase2b(w2)
                if r is not None:
                    return r
    for i, x in enumerate(w):
        n = Path(x.strip("\"'")).name.lower()
        if n in ("fase2b.py", "fase2b"):
            if n == "fase2b" and not (i > 0 and w[i - 1] == "-m"):
                continue
            return w[i + 1:]
    return None


def topic_de(args: list[str]) -> str | None:
    i = 0
    while i < len(args):
        a = args[i]
        if a in CON_VALOR:
            i += 2
            continue
        if not a.startswith("-"):
            return a
        i += 1
    return None


def revisar(cmd: str, salidas: Path = ROOT / "output") -> str | None:
    """El motivo del bloqueo, o None. `salidas` = la carpeta de los topics (output/ del repo; otra en los tests)."""
    for w in segmentos(sin_heredocs(cmd)):
        args = llamada_fase2b(w)
        if args is None or "--gfx" not in args or SIN_HOOK & set(args):
            continue
        if "--only-cap" in args and "--gfx-debug" in args:
            continue
        topic = topic_de(args)
        if topic is None:
            return ("guard_render: `fase2b --gfx` en modo batch (sin topic) no se puede verificar: correrlo por topic, "
                    "con su guion de pantalla aprobado")
        ok, motivo = _aprobacion().estado(Path(salidas) / topic)
        if not ok:
            return f"guard_render: sin guion aprobado no hay render — {motivo}"
    return None


def main() -> None:
    sys.stderr.reconfigure(encoding="utf-8")
    motivo = revisar(comando(leer_evento()))
    if motivo:
        bloquear(motivo)


if __name__ == "__main__":
    main()
