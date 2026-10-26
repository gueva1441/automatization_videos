"""
lab/tools/mapa_hechos.py — F33 §D: los hechos del mapa de módulos sacados del código (no de memoria): por módulo, el
docstring, las funciones, a quién importa (arriba y dentro de funciones), quién lo importa (en el código del pipeline y
en los tests, por separado), qué plantillas usa y en qué commit nació. Salida JSON por stdout; MAPA_MODULOS se escribe a
mano encima de esto (los stickers y el estado los decide quien lee el código).

    python lab/tools/mapa_hechos.py > lab/hyperframes/f33/d/hechos.json
"""
from __future__ import annotations

import ast
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def modulos() -> list[Path]:
    se = ROOT / "script_engine"
    fs = sorted(se.glob("gfx_*.py")) + [se / n for n in ("aprobacion.py", "m01a_escaleta.py", "m01d_particion.py",
                                                          "music_intensity.py", "transition_applier.py")]
    fs += [se / n for n in ("rotulista_llm.py", "rotulista_filtros.py", "rotulista_colocar.py", "clima.py",   # F36 §A
                            "voz_datos.py", "voz_utils.py")]
    fs += [ROOT / n for n in ("gfx_config.py", "fase2b.py", "transition_config.py")]
    return [f for f in fs if f.exists()]


def nombre(f: Path) -> str:
    return f.stem


def importados(f: Path) -> dict[str, list[str]]:
    """{módulo importado: ['arriba'|'en <función>']} (solo los del repo)."""
    t = ast.parse(f.read_text(encoding="utf-8"))
    out: dict[str, list[str]] = {}

    def ver(nodo: ast.AST, donde: str) -> None:
        for n in ast.walk(nodo):
            mods = []
            if isinstance(n, ast.ImportFrom) and n.module:
                mods = [n.module] + [f"{n.module}.{a.name}" for a in n.names]
            elif isinstance(n, ast.Import):
                mods = [a.name for a in n.names]
            for m in mods:
                base = m.split(".")[-1] if m.startswith("script_engine.") else m.split(".")[0]
                if (ROOT / "script_engine" / f"{base}.py").exists() or (ROOT / f"{base}.py").exists():
                    out.setdefault(base, [])
                    if donde not in out[base]:
                        out[base].append(donde)
    for st in t.body:
        if isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef)):
            ver(st, f"en {st.name}")
        elif isinstance(st, ast.ClassDef):
            for b in st.body:
                if isinstance(b, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    ver(b, f"en {st.name}.{b.name}")
        else:
            ver(st, "arriba")
    out.pop(nombre(f), None)
    return out


def doc(f: Path) -> str:
    d = ast.get_docstring(ast.parse(f.read_text(encoding="utf-8"))) or ""
    return re.sub(r"\s+", " ", d.split("\n\n")[0]).strip()[:600]


def funciones(f: Path) -> list[str]:
    return [n.name for n in ast.parse(f.read_text(encoding="utf-8")).body if isinstance(n, (ast.FunctionDef, ast.ClassDef))]


def nacio(f: Path) -> str:
    r = subprocess.run(["git", "log", "--diff-filter=A", "--format=%h %ad %s", "--date=short", "--", str(f.relative_to(ROOT))],
                       cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
    ls = [x for x in r.stdout.splitlines() if x.strip()]
    return ls[-1][:140] if ls else "(sin commit)"


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    mods = modulos()
    todos_py = [p for p in ROOT.rglob("*.py") if not any(x in p.parts for x in (".git", "node_modules", "_probe_out"))
                and "gfx_runtime" not in p.parts]
    hechos: dict[str, dict] = {}
    for f in mods:
        hechos[nombre(f)] = {"archivo": f.relative_to(ROOT).as_posix(), "doc": doc(f), "funciones": funciones(f),
                             "importa": importados(f), "nacio": nacio(f), "lo_importan": {}, "tests": [], "lab": []}
    for p in todos_py:
        try:
            imp = importados(p)
        except (SyntaxError, UnicodeDecodeError, ValueError):
            continue
        rel = p.relative_to(ROOT).as_posix()
        for m, donde in imp.items():
            if m in hechos and nombre(p) != m:
                if p.name.startswith("test_"):
                    hechos[m]["tests"].append(rel)
                elif rel.startswith(("lab/", "_")) or "/_" in rel:
                    hechos[m]["lab"].append(rel)
                else:
                    hechos[m]["lo_importan"][rel] = donde
    tmpl = sorted((ROOT / "script_engine" / "gfx_templates").glob("*.tmpl"))
    usos = {}
    for t in tmpl:
        usos[t.name] = [f.relative_to(ROOT).as_posix() for f in mods if t.name in f.read_text(encoding="utf-8")]
        hechos[t.name] = {"archivo": t.relative_to(ROOT).as_posix(), "doc": "", "funciones": [], "importa": {},
                          "nacio": nacio(t), "lo_importan": {u: ["usa la plantilla"] for u in usos[t.name]}, "tests": [],
                          "lab": []}
    print(json.dumps(hechos, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
