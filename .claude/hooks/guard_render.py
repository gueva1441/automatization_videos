"""F33 §B.2 — PreToolUse Bash/PowerShell: bloquea (exit 2) `fase2b … --gfx` si el `output/<topic>/GUION_PANTALLA.json`
no existe, no tiene `aprobado` o su `md5_planes` no coincide con los planes de hoy (script_engine/aprobacion.py).
No pasan por el hook: `--plan-only`, `--plan-edit`, `--aprobar-guion`, `--only-cap … --gfx-debug` y todo fase2b sin
`--gfx` (el candado md5 de ch02 es `--only-cap ch02` sin `--gfx`). `--dry-run` no es salida: también se bloquea.
Límite: ve el comando escrito en la herramienta, no lo que un runner de lab lanza por dentro (runpy/subprocess).
"""
from __future__ import annotations

import importlib.util
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


def llamada_fase2b(w: list[str]) -> list[str] | None:
    """Los argumentos de fase2b si el comando simple lo corre (`python fase2b.py …`, `python -m fase2b …`)."""
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
    for w in segmentos(cmd):
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
