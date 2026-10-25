"""F26 §D.3 — PostToolUse Edit|Write: si el archivo tocado es un `PROMPT_*.md` o tiene `## SISTEMA` o `SYSTEM_V2`
adentro, avisa el md5 nuevo y el viejo (el de HEAD) del archivo y, si tiene un bloque `## SISTEMA`, también el del
bloque (extraído como en los tests: desde «## SISTEMA» hasta el «---» siguiente). No bloquea.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _comun import ROOT, leer_evento  # noqa: E402

MARCAS = ("## SISTEMA", "SYSTEM_V2")


def md5(s: str) -> str:
    return hashlib.md5(s.encode("utf-8")).hexdigest()


def bloque(texto: str) -> str | None:
    t = texto.replace("\r\n", "\n")
    a = "\n## SISTEMA\n\n"
    if a not in t:
        return None
    i = t.index(a) + len(a)
    j = t.find("\n\n---\n", i)
    return t[i:j if j >= 0 else len(t)]


def viejo(path: Path) -> str | None:
    try:
        rel = path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return None
    r = subprocess.run(["git", "show", f"HEAD:{rel}"], cwd=ROOT, capture_output=True)
    return r.stdout.decode("utf-8", errors="replace") if r.returncode == 0 else None


def aviso(path: Path) -> str | None:
    if not path.is_file():
        return None
    nuevo = path.read_bytes().decode("utf-8", errors="replace")
    if not (path.name.startswith("PROMPT_") and path.suffix == ".md") and not any(m in nuevo for m in MARCAS):
        return None
    v = viejo(path)
    partes = [f"md5_prompt: {path.name}: archivo {md5(nuevo.replace(chr(13) + chr(10), chr(10)))} (antes, en HEAD: "
              f"{md5(v.replace(chr(13) + chr(10), chr(10))) if v is not None else 'no estaba'})"]
    bn, bv = bloque(nuevo), (bloque(v) if v is not None else None)
    if bn is not None:
        partes.append(f"bloque SISTEMA {md5(bn)} (antes: {md5(bv) if bv is not None else '—'})")
    return " · ".join(partes)


def main() -> None:
    ev = leer_evento()
    fp = (ev.get("tool_input") or {}).get("file_path")
    if not fp:
        return
    msg = aviso(Path(fp))
    if msg:
        print(json.dumps({"systemMessage": msg,
                          "hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": msg}},
                         ensure_ascii=False))


if __name__ == "__main__":
    main()
