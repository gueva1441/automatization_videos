"""
dependencias.py — F42b: qué librerías de afuera necesita la cadena del form y cuáles le faltan al Python que corre.

Sin listas a mano: los scripts de cada etapa salen de `run_pipeline.py` (por AST, los comandos `python <script>.py …`
de sus pasos, como el mapa de F42); desde ellos se siguen los imports del repo (arriba y dentro de funciones). Un import
es «de afuera» si su paquete no está en `sys.stdlib_module_names` ni es un archivo o paquete del repo; es «opcional» si
está dentro de un `try` cuyo `except` agarra `ImportError`, `ModuleNotFoundError` o `Exception` (o un `except:` pelado).
Una librería es requerida si al menos uno de sus imports no es opcional. `faltantes()` pregunta con
`importlib.util.find_spec`, sin importar las librerías.

    python dependencias.py                  → tabla: librería · requerida/opcional · archivo:línea · la tiene
    python dependencias.py --requirements   → `distribución==versión` de las requeridas instaladas en este Python
"""
from __future__ import annotations

import ast
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ORQUESTADOR = ROOT / "run_pipeline.py"
_ATRAPA = {"ImportError", "ModuleNotFoundError", "Exception", "BaseException"}


def _arbol(p: Path) -> ast.Module | None:
    try:
        return ast.parse(p.read_text(encoding="utf-8-sig"))
    except (OSError, SyntaxError, UnicodeDecodeError, ValueError):
        return None


def scripts_de_etapa() -> list[Path]:
    """Los `*.py` que `run_pipeline.py` lanza (primer elemento de cada lista de comando), más el orquestador."""
    t = _arbol(ORQUESTADOR)
    out = [ORQUESTADOR]
    for n in ast.walk(t) if t else ():
        if isinstance(n, ast.List) and n.elts and isinstance(n.elts[0], ast.Constant) \
                and isinstance(n.elts[0].value, str) and n.elts[0].value.endswith(".py"):
            p = ROOT / n.elts[0].value
            if p.exists() and p not in out:
                out.append(p)
    return out


def _del_repo(mod: str, nivel: int, desde: Path) -> Path | None:
    """El archivo del repo que importa `mod` (o None si no es del repo)."""
    if nivel:
        base = desde.parent
        for _ in range(nivel - 1):
            base = base.parent
        partes = list(base.relative_to(ROOT).parts) + (mod.split(".") if mod else [])
    else:
        partes = mod.split(".")
    for i in range(len(partes), 0, -1):
        f = ROOT.joinpath(*partes[:i])
        if f.with_suffix(".py").exists():
            return f.with_suffix(".py")
        if (f / "__init__.py").exists():
            return f / "__init__.py"
        if f.is_dir() and i == 1 and f.name != "lab":
            return f / "__init__.py"
    if not nivel and desde.parent != ROOT:                  # import «pelado» de un hermano (sys.path con la carpeta)
        cand = desde.parent / f"{partes[0]}.py"
        if cand.exists():
            return cand
    return None


def _es_opcional(pila: list[ast.AST]) -> bool:
    """¿Algún `try` de arriba agarra la falta del import?"""
    for i, n in enumerate(pila):
        if isinstance(n, ast.Try) and i + 1 < len(pila) and pila[i + 1] in n.body:
            for h in n.handlers:
                tipos = [] if h.type is None else (h.type.elts if isinstance(h.type, ast.Tuple) else [h.type])
                nombres = {x.id if isinstance(x, ast.Name) else getattr(x, "attr", "") for x in tipos}
                if h.type is None or nombres & _ATRAPA:
                    return True
    return False


def _imports(p: Path, t: ast.Module):
    """(módulo, nivel, línea, opcional) de cada import del archivo, con la pila de nodos para saber si es opcional."""
    def visitar(n: ast.AST, pila: list[ast.AST]):
        if isinstance(n, ast.Import):
            for a in n.names:
                yield a.name, 0, n.lineno, _es_opcional(pila + [n])
        elif isinstance(n, ast.ImportFrom):
            yield (n.module or ""), n.level, n.lineno, _es_opcional(pila + [n])
            if n.module is None or n.level:                 # `from . import x`: cada nombre puede ser un módulo
                for a in n.names:
                    yield (f"{n.module}.{a.name}" if n.module else a.name), n.level, n.lineno, _es_opcional(pila + [n])
            else:
                for a in n.names:
                    yield f"{n.module}.{a.name}", 0, n.lineno, _es_opcional(pila + [n])
        for h in ast.iter_child_nodes(n):
            yield from visitar(h, pila + [n])
    yield from visitar(t, [])


def librerias() -> dict[str, dict]:
    """{librería: {"requerida": bool, "sitios": [(archivo, línea, opcional)], "modulos": {nombre importado}}}."""
    stdlib = set(sys.stdlib_module_names)
    vistos: set[Path] = set()
    pila = list(scripts_de_etapa())
    libs: dict[str, dict] = {}
    while pila:
        p = pila.pop()
        if p in vistos or not p.exists():
            continue
        vistos.add(p)
        t = _arbol(p)
        if t is None:
            continue
        for mod, nivel, linea, opcional in _imports(p, t):
            dst = _del_repo(mod, nivel, p)
            if dst is not None:
                if dst not in vistos:
                    pila.append(dst)
                continue
            if nivel or not mod:
                continue
            top = mod.split(".")[0]
            if top in stdlib or top == "__future__":
                continue
            e = libs.setdefault(top, {"requerida": False, "sitios": [], "modulos": set()})
            sitio = (p.relative_to(ROOT).as_posix(), linea, opcional)
            if sitio not in e["sitios"]:
                e["sitios"].append(sitio)
            e["modulos"].add(mod)
            e["requerida"] = e["requerida"] or not opcional
    return libs


def _tiene(lib: str, modulos: set[str]) -> bool:
    """`find_spec` del paquete (no lo importa). Si es un paquete de espacio de nombres (p. ej. `google`), también el
    submódulo de segundo nivel que se usa (find_spec importa solo el padre, que no tiene código)."""
    try:
        spec = importlib.util.find_spec(lib)
    except (ImportError, ValueError):
        return False
    if spec is None:
        return False
    if spec.origin in (None, "namespace"):
        segundos = {".".join(m.split(".")[:2]) for m in modulos if m.count(".") >= 1}
        for s in segundos:
            try:
                if importlib.util.find_spec(s) is not None:
                    return True
            except (ImportError, ValueError):
                continue
        return False
    return True


def tabla() -> list[dict]:
    out = []
    for lib, e in sorted(libs_cache().items()):
        out.append({"libreria": lib, "requerida": e["requerida"], "tiene": _tiene(lib, e["modulos"]),
                    "sitios": [f"{a}:{n}" for a, n, op in sorted(e["sitios"]) if not op or not e["requerida"]]})
    return out


_CACHE: dict[str, dict] | None = None


def libs_cache() -> dict[str, dict]:
    global _CACHE
    if _CACHE is None:
        _CACHE = librerias()
    return _CACHE


def faltantes() -> dict[str, list[dict]]:
    """{"requeridas": [...], "opcionales": [...]} con las librerías que este Python no encuentra (cada una con sus
    archivo:línea)."""
    out: dict[str, list[dict]] = {"requeridas": [], "opcionales": []}
    for f in tabla():
        if not f["tiene"]:
            out["requeridas" if f["requerida"] else "opcionales"].append(f)
    return out


def comando_pip() -> str:
    return f'"{sys.executable}" -m pip install -r requirements.txt'


def requirements() -> list[str]:
    """`distribución==versión` de las requeridas que este Python tiene (de `importlib.metadata`, no de una lista)."""
    import importlib.metadata as md
    dist_de = md.packages_distributions()
    out = []
    for f in tabla():
        if f["requerida"] and f["tiene"]:
            for d in dist_de.get(f["libreria"], []):
                linea = f"{d}=={md.version(d)}"
                if linea not in out:
                    out.append(linea)
    return out


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    if "--requirements" in sys.argv:
        print("\n".join(requirements()))
        return 0
    print(f"Python: {sys.executable}")
    print("| librería | requerida u opcional | archivo:línea | la tiene |")
    print("|---|---|---|---|")
    for f in tabla():
        s = f["sitios"]
        donde = ", ".join(s[:3]) + (f" (+{len(s) - 3})" if len(s) > 3 else "")
        print(f"| {f['libreria']} | {'requerida' if f['requerida'] else 'opcional'} | {donde} | "
              f"{'sí' if f['tiene'] else 'NO'} |")
    fal = faltantes()
    print(f"\n{len(fal['requeridas'])} requeridas faltantes · {len(fal['opcionales'])} opcionales faltantes")
    return 1 if fal["requeridas"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
