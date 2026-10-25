"""F26 §D — piezas comunes de los hooks de Claude Code del repo (sin dependencias fuera de la biblioteca estándar)."""
from __future__ import annotations

import json
import re
import shlex
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
_SEP = re.compile(r"&&|\|\||;|\||\n")


def leer_evento() -> dict:
    try:
        return json.loads(sys.stdin.buffer.read().decode("utf-8") or "{}")
    except ValueError:
        return {}


def comando(ev: dict) -> str:
    return str((ev.get("tool_input") or {}).get("command") or "")


def segmentos(cmd: str) -> list[list[str]]:
    """El comando partido en sus comandos simples (&&, ||, ;, |, saltos de línea), cada uno en palabras."""
    out = []
    for s in _SEP.split(cmd):
        s = s.strip()
        if not s:
            continue
        try:
            w = shlex.split(s, posix=True)
        except ValueError:
            w = s.split()
        while w and re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", w[0]):     # VAR=valor delante del comando
            w = w[1:]
        if w:
            out.append(w)
    return out


def git_args(w: list[str]) -> tuple[str | None, list[str], str | None]:
    """(subcomando, argumentos, carpeta de -C) si el comando simple es `git …`; si no, (None, [], None)."""
    if not w or Path(w[0]).name.lower() not in ("git", "git.exe"):
        return None, [], None
    i, cwd = 1, None
    while i < len(w) and w[i].startswith("-"):
        if w[i] == "-C" and i + 1 < len(w):
            cwd = w[i + 1]
            i += 2
            continue
        if w[i] in ("-c",) and i + 1 < len(w):
            i += 2
            continue
        i += 1
    if i >= len(w):
        return None, [], cwd
    return w[i], w[i + 1:], cwd


def git(args: list[str], cwd: str | Path | None = None) -> str:
    r = subprocess.run(["git", *args], cwd=cwd or ROOT, capture_output=True, text=True, encoding="utf-8",
                       errors="replace")
    return r.stdout


def bloquear(motivo: str) -> None:
    """exit 2: Claude Code frena la herramienta y le muestra el motivo a Claude."""
    sys.stderr.write(motivo.rstrip() + "\n")
    sys.exit(2)
