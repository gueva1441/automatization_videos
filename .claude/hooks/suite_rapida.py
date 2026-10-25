"""F26 §D.2 — PreToolUse Bash: antes de `git commit` corre la suite rápida (f25c, f24, f21; < 2 min). Si sale roja,
bloquea (exit 2) con el final del error. `HOOK_SUITE_RAPIDA` (rutas separadas por espacios) cambia la lista: lo usa la
prueba del hook para ver un rojo de verdad.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _comun import ROOT, bloquear, comando, git_args, leer_evento, segmentos  # noqa: E402

SUITE = ("test_module_f25c.py", "test_module_f24.py", "test_module_f21.py")
TIMEOUT_S = 170


def hay_commit(cmd: str) -> bool:
    return any(git_args(w)[0] == "commit" for w in segmentos(cmd))


def correr(suite: list[str], cwd: Path) -> tuple[bool, str]:
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    try:
        r = subprocess.run([sys.executable, "-m", "pytest", *suite, "-q", "-x", "-p", "no:cacheprovider"], cwd=cwd,
                           capture_output=True, text=True, encoding="utf-8", errors="replace", env=env,
                           timeout=TIMEOUT_S)
    except subprocess.TimeoutExpired:
        return False, f"la suite rápida pasó de {TIMEOUT_S} s"
    return r.returncode == 0, (r.stdout + r.stderr)


def main() -> None:
    ev = leer_evento()
    if not hay_commit(comando(ev)):
        return
    suite = os.environ.get("HOOK_SUITE_RAPIDA", "").split() or list(SUITE)
    ok, out = correr(suite, Path(ev.get("cwd") or ROOT))
    if not ok:
        cola = "\n".join(out.strip().splitlines()[-25:])
        bloquear(f"suite_rapida: la suite rápida ({' '.join(suite)}) está en rojo; el commit no sale.\n{cola}")


if __name__ == "__main__":
    main()
