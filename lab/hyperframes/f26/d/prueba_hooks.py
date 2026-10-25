"""F26 §D — prueba de los 4 hooks: cada uno con un caso que bloquea y uno que pasa, corriéndolos como los corre Claude
Code (el evento JSON por stdin, exit 2 = bloquea). guard_git y tope_tanda en repos/carpetas temporales; suite_rapida
con la suite de verdad (pasa) y con un test que falla (`HOOK_SUITE_RAPIDA`); md5_prompt sobre un PROMPT de verdad.
Uso: python -I lab/hyperframes/f26/d/prueba_hooks.py → tabla en prueba_hooks.md + prueba_hooks.json
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
HOOKS = ROOT / ".claude" / "hooks"
OUT = Path(__file__).resolve().parent
LLAVE = "sk-" + "ant-" + "x" * 20


def hook(nombre: str, ev: dict, env: dict | None = None) -> tuple[int, str, float]:
    t0 = time.time()
    r = subprocess.run([sys.executable, "-I", str(HOOKS / nombre)], input=json.dumps(ev).encode("utf-8"),
                       capture_output=True, env={**os.environ, **(env or {})}, timeout=300)
    txt = (r.stdout + r.stderr).decode("utf-8", errors="replace").strip()
    return r.returncode, txt, round(time.time() - t0, 1)


def bash(cmd: str, cwd: Path) -> dict:
    return {"hook_event_name": "PreToolUse", "tool_name": "Bash", "tool_input": {"command": cmd}, "cwd": str(cwd)}


def git(cwd: Path, *a: str) -> None:
    subprocess.run(["git", *a], cwd=cwd, check=True, capture_output=True)


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    filas = []

    def caso(h, que, esperado, ev, env=None):
        rc, txt, s = hook(h, ev, env)
        bloquea = rc == 2
        filas.append({"hook": h, "caso": que, "esperado": esperado, "rc": rc, "bloquea": bloquea,
                      "ok": bloquea == (esperado == "bloquea"), "salida": txt[-300:], "s": s})
        print(f"{'OK ' if filas[-1]['ok'] else 'MAL'} {h:16s} {que:55s} rc={rc} {s}s", flush=True)

    with tempfile.TemporaryDirectory() as td:
        repo = Path(td) / "repo"
        repo.mkdir()
        git(repo, "init", "-q", "-b", "main")
        git(repo, "config", "user.email", "t@t")
        git(repo, "config", "user.name", "t")
        (repo / "a.py").write_text("x = 1\n", encoding="utf-8")
        git(repo, "add", "a.py")
        git(repo, "commit", "-qm", "init")
        git(repo, "checkout", "-qb", "rama")
        (repo / ".env").write_text("K=1\n", encoding="utf-8")
        (repo / "config.py").write_text("k = 1\n", encoding="utf-8")
        (repo / "lab" / "_gpt_probe_analista").mkdir(parents=True)
        (repo / "lab" / "_gpt_probe_analista" / "x.json").write_text("{}", encoding="utf-8")
        (repo / "llave.txt").write_text(f"api = {LLAVE}\n", encoding="utf-8")
        (repo / "b.py").write_text("y = 2\n", encoding="utf-8")
        caso("guard_git.py", "git add .env", "bloquea", bash("git add .env", repo))
        caso("guard_git.py", "git add config.py (en una cadena con cd &&)", "bloquea",
             bash(f'cd "{repo}" && git add config.py b.py', repo))
        caso("guard_git.py", "git add -A (trae lab/_gpt_probe_analista/)", "bloquea", bash("git add -A", repo))
        caso("guard_git.py", "git add llave.txt (con una llave adentro)", "bloquea", bash("git add llave.txt", repo))
        caso("guard_git.py", "git add b.py", "pasa", bash("git add b.py", repo))
        git(repo, "add", "llave.txt")
        caso("guard_git.py", "git commit con llave.txt en el índice", "bloquea", bash('git commit -m "x"', repo))
        git(repo, "reset", "-q", "llave.txt")
        git(repo, "add", "b.py")
        caso("guard_git.py", "git commit con b.py en el índice", "pasa", bash('git commit -m "x"', repo))
        caso("guard_git.py", "git push origin main", "bloquea", bash("git push origin main", repo))
        caso("guard_git.py", "git push origin rama:main", "bloquea", bash("git push origin rama:main", repo))
        caso("guard_git.py", "git push origin rama", "pasa", bash("git push origin rama", repo))
        caso("guard_git.py", "git checkout main && git merge rama", "bloquea",
             bash("git checkout main && git merge rama", repo))
        caso("guard_git.py", "git merge main (estando en rama)", "pasa", bash("git merge main", repo))

        # suite_rapida
        roto = Path(td) / "test_roto.py"
        roto.write_text("def test_rojo():\n    assert 1 == 2\n", encoding="utf-8")
        caso("suite_rapida.py", "git commit con un test rojo (HOOK_SUITE_RAPIDA)", "bloquea",
             bash('git commit -m "x"', ROOT), {"HOOK_SUITE_RAPIDA": str(roto)})
        caso("suite_rapida.py", "git commit con la suite rápida de verdad", "pasa", bash('git commit -m "x"', ROOT))
        caso("suite_rapida.py", "git status (no es commit: no corre nada)", "pasa", bash("git status", ROOT))

        # tope_tanda
        base = Path(td) / "tanda"
        (base / "lab").mkdir(parents=True)
        (base / "data").mkdir()
        (base / "lab" / "TOPE_TANDA.json").write_text(json.dumps({"usd": 3, "desde": "2026-10-25T00:00:00"}),
                                                      encoding="utf-8")
        hist = [{"video_id": "a", "created_at": "2026-10-24T10:00:00", "total_cost": 50.0},
                {"video_id": "b", "created_at": "2026-10-25T01:00:00", "total_cost": 2.5},
                {"video_id": "c", "created_at": "2026-10-25T02:00:00", "total_cost": 1.0}]
        (base / "data" / "cost_history.json").write_bytes(json.dumps(hist, ensure_ascii=False).encode("cp1252"))
        caso("tope_tanda.py", "python fase2a.py con 3.50 gastados de 3.00", "bloquea",
             bash("python fase2a.py --topic x", base))
        caso("tope_tanda.py", "python -I fase1_5.py con 3.50 de 3.00", "bloquea",
             bash("cd x && python -I fase1_5.py --topic x --batch", base))
        (base / "lab" / "TOPE_TANDA.json").write_text(json.dumps({"usd": 10, "desde": "2026-10-25T00:00:00"}),
                                                      encoding="utf-8")
        caso("tope_tanda.py", "python fase2a.py con 3.50 gastados de 10.00", "pasa",
             bash("python fase2a.py --topic x", base))
        caso("tope_tanda.py", "python fase2b.py (no lo mira)", "pasa", bash("python fase2b.py x", base))

        # md5_prompt (PostToolUse): avisa sin bloquear
        for p, esperado in ((ROOT / "lab" / "hyperframes" / "f26" / "PROMPT_ESCALETA_f26_1.md", "avisa"),
                            (ROOT / "script_engine" / "m01a_escaleta.py", "avisa"),
                            (ROOT / "script_engine" / "video_length.py", "nada")):
            rc, txt, s = hook("md5_prompt.py", {"hook_event_name": "PostToolUse", "tool_name": "Edit",
                                                "tool_input": {"file_path": str(p)}, "cwd": str(ROOT)})
            avisa = bool(txt)
            filas.append({"hook": "md5_prompt.py", "caso": f"Edit {p.name}", "esperado": esperado, "rc": rc,
                          "bloquea": rc == 2, "ok": rc == 0 and avisa == (esperado == "avisa"), "salida": txt[-400:],
                          "s": s})
            print(f"{'OK ' if filas[-1]['ok'] else 'MAL'} md5_prompt.py    Edit {p.name:40s} rc={rc} {txt[:160]}")
    (OUT / "prueba_hooks.json").write_text(json.dumps(filas, ensure_ascii=False, indent=1), encoding="utf-8")
    md = ["| hook | caso | esperado | resultado | s |", "|---|---|---|---|---|"]
    for f in filas:
        res = "bloquea (exit 2)" if f["bloquea"] else ("avisa" if f["hook"] == "md5_prompt.py" and f["salida"] else "pasa")
        md.append(f"| `{f['hook']}` | {f['caso']} | {f['esperado']} | {res} {'✅' if f['ok'] else '❌'} | {f['s']} |")
    (OUT / "prueba_hooks.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"{sum(f['ok'] for f in filas)}/{len(filas)} OK")


if __name__ == "__main__":
    main()
