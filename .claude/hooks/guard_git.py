"""F26 §D.1 — PreToolUse Bash: bloquea (exit 2)
- `git add` / `git commit` que incluyan `.env`, `config.py`, algo bajo `lab/_gpt_probe_analista/` o un archivo con
  una llave de Anthropic u OpenAI adentro;
- `git push` hacia `main` y `git merge` estando en `main` (o `git merge` de algo hacia main con `git checkout main &&`).
Lo que entra en el add se pregunta a git (`git add --dry-run` con los mismos argumentos); en el commit, lo que está
en el índice más lo que agrega `-a` o las rutas del comando.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _comun import bloquear, comando, git, git_args, leer_evento, segmentos  # noqa: E402

PROHIBIDOS = (re.compile(r"(^|/)\.env$"), re.compile(r"(^|/)config\.py$"), re.compile(r"^lab/_gpt_probe_analista/"))
# una llave de verdad: el prefijo y al menos 20 caracteres de llave (el prefijo solo, como texto de una regla, no
# bloquea). Partido para que este archivo no se bloquee a sí mismo.
LLAVE = re.compile(r"sk-" + r"(ant|proj)-[A-Za-z0-9_\-]{20,}")


def _norm(p: str) -> str:
    p = p.strip().strip('"').replace("\\", "/")
    while p.startswith("./"):
        p = p[2:]
    return p


def prohibido(path: str) -> bool:
    p = _norm(path)
    return any(r.search(p) for r in PROHIBIDOS)


def con_llave(path: str, cwd: Path, staged: bool) -> bool:
    if staged:
        r = subprocess.run(["git", "show", f":{path}"], cwd=cwd, capture_output=True)
        data = r.stdout if r.returncode == 0 else b""
    else:
        f = cwd / path
        data = f.read_bytes() if f.is_file() else b""
    return bool(LLAVE.search(data.decode("utf-8", errors="replace")))


def archivos_add(args: list[str], cwd: Path) -> list[str]:
    out = git(["add", "--dry-run", *args], cwd)
    files = [m.group(1) for m in re.finditer(r"^add '(.+)'$", out, re.M)]
    # lo que git no añadiría (ignorado) igual se mira por nombre si se nombró explícitamente con -f
    if "-f" in args or "--force" in args:
        files += [a for a in args if not a.startswith("-")]
    return files


def archivos_commit(args: list[str], cwd: Path) -> tuple[list[str], list[str]]:
    staged = [x for x in git(["diff", "--cached", "--name-only"], cwd).splitlines() if x]
    extra = []
    if any(a == "--all" or re.fullmatch(r"-[A-Za-z]*a[A-Za-z]*", a) for a in args):      # -a, -am, -av…
        extra += [x for x in git(["diff", "--name-only"], cwd).splitlines() if x]
    if "--" in args:
        extra += args[args.index("--") + 1:]
    return staged, extra


def rama(cwd: Path) -> str:
    return git(["rev-parse", "--abbrev-ref", "HEAD"], cwd).strip()


def revisar(cmd: str, base: Path) -> str | None:
    checkout_main = False
    for w in segmentos(cmd):
        sub, args, c = git_args(w)
        cwd = (base / c) if c else base
        if sub is None:
            continue
        if sub in ("checkout", "switch") and "main" in args:
            checkout_main = True
        if sub == "add":
            malos = [f for f in archivos_add(args, cwd) if prohibido(f)]
            malos += [f for f in archivos_add(args, cwd) if not prohibido(f) and con_llave(f, cwd, False)]
            if malos:
                return f"guard_git: `git add` incluye archivos que no se commitean: {', '.join(sorted(set(malos)))}"
        elif sub == "commit":
            staged, extra = archivos_commit(args, cwd)
            malos = [f for f in staged + extra if prohibido(f)]
            malos += [f for f in staged if not prohibido(f) and con_llave(f, cwd, True)]
            malos += [f for f in extra if not prohibido(f) and con_llave(f, cwd, False)]
            if malos:
                return f"guard_git: el commit incluye archivos que no se commitean: {', '.join(sorted(set(malos)))}"
        elif sub == "push":
            pos = [a for a in args if not a.startswith("-")]
            refs = pos[1:]
            if any(r.split(":")[-1] in ("main", "refs/heads/main") for r in refs) or (not refs and rama(cwd) == "main"):
                return "guard_git: `git push` hacia main está bloqueado (sin OK explícito de Omar no se toca main)"
        elif sub == "merge":
            if checkout_main or rama(cwd) == "main":
                return "guard_git: `git merge` sobre main está bloqueado (nada se mergea sin OK de Omar)"
    return None


def main() -> None:
    ev = leer_evento()
    base = Path(ev.get("cwd") or ".").resolve()
    motivo = revisar(comando(ev), base)
    if motivo:
        bloquear(motivo)


if __name__ == "__main__":
    main()
