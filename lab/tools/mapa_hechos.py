"""
lab/tools/mapa_hechos.py — F42 §A (antes F33 §D, solo gfx): los hechos del mapa del proyecto sacados del código, no de
memoria, para TODO lo de producción. Por archivo: docstring, funciones, a quién importa (arriba y dentro de funciones),
a qué `*.py` lanza por `subprocess`, quién lo importa (producción y tests por separado), imports que fallan, si es punto
de entrada (`if __name__ == "__main__"`), commit de nacimiento, último commit y su tanda, md5. Además: la secuencia del
form leída de `run_pipeline.py` por AST (etapas, comando y compuerta), el alcance de cada etapa por import y el estado
por alcance (vivo / solo herramienta manual / huérfano), y las funciones sin llamador.

Qué es producción (handoff F42, por código, no por lista): `.py` de la raíz que no empiezan con `_`, `test_` ni `diag`;
`script_engine/*.py`, `researcher_steps/*.py`, `tools/*.py`; los `.html` de la raíz que nombra un `.py` de producción;
`script_engine/gfx_templates/*`; `gfx_profiles/*.json` (fuera de git: solo nombre y claves); `.claude/hooks/*`,
`.claude/agents/*`, `.claude/commands/*`. De `config.py` solo salen nombres, nunca valores.

    python lab/tools/mapa_hechos.py                 → lab/mapa/hechos.json
    python lab/tools/mapa_hechos.py --tests         → además lab/mapa/tests_collect.json (pytest --collect-only, no corre tests)
    python lab/tools/mapa_hechos.py --stdout        → el JSON por stdout, sin escribir
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SALIDA = ROOT / "lab" / "mapa"
PAQUETES = ("script_engine", "researcher_steps", "tools")
CLAUDE_DIRS = (".claude/hooks", ".claude/agents", ".claude/commands")
FORM_HTML = "qa_form.html"          # el form: su servidor es la raíz de lo que «lanza el form» (handoff F42 §A.3)


# ─────────────────────────── qué es producción ───────────────────────────
def es_py_prod(rel: str) -> bool:
    p = Path(rel)
    if p.suffix != ".py":
        return False
    if len(p.parts) == 1:
        return not p.name.startswith(("_", "test_", "diag"))
    return len(p.parts) == 2 and p.parts[0] in PAQUETES


def py_produccion() -> list[Path]:
    fs = [p for p in ROOT.glob("*.py") if es_py_prod(p.name)]
    for d in PAQUETES:
        fs += sorted((ROOT / d).glob("*.py"))
    return sorted(fs)


def no_py_produccion(pys: list[Path]) -> list[Path]:
    textos = "\n".join(p.read_text(encoding="utf-8", errors="replace") for p in pys)
    fs = [h for h in sorted(ROOT.glob("*.html")) if h.name in textos]
    fs += sorted(p for p in (ROOT / "script_engine" / "gfx_templates").iterdir() if p.is_file())
    fs += sorted((ROOT / "gfx_profiles").glob("*.json"))
    for d in CLAUDE_DIRS:
        fs += sorted(p for p in (ROOT / d).iterdir() if p.is_file() and p.suffix in (".py", ".md"))
    return fs


def rel(p: Path) -> str:
    return p.relative_to(ROOT).as_posix()


def md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


def arbol(p: Path) -> ast.Module | None:
    try:
        return ast.parse(p.read_text(encoding="utf-8-sig"))
    except (SyntaxError, UnicodeDecodeError, ValueError):
        return None


# ─────────────────────────── imports ───────────────────────────
def _archivo_de(partes: list[str]) -> Path | None:
    if not partes:
        return None
    f = ROOT.joinpath(*partes).with_suffix(".py")
    if f.exists():
        return f
    d = ROOT.joinpath(*partes)
    if (d / "__init__.py").exists() or (d.is_dir() and d.name in PAQUETES):
        return d
    return None


def resolver(mod: str | None, nivel: int, desde: Path) -> Path | None:
    """El archivo (o carpeta de paquete) del repo que importa `mod`; None si es de afuera."""
    if nivel:
        base = desde.parent
        for _ in range(nivel - 1):
            base = base.parent
        partes = list(base.relative_to(ROOT).parts) + (mod.split(".") if mod else [])
        return _archivo_de(partes)
    if not mod:
        return None
    r = _archivo_de(mod.split("."))
    if r is None and desde.parent != ROOT:          # import «pelado» de un hermano (sys.path con la carpeta)
        cand = desde.parent / (mod.split(".")[0] + ".py")
        if cand.exists():
            return cand
    return r


def nombres_de_arriba(t: ast.Module) -> tuple[set[str], bool]:
    """Nombres definidos a nivel módulo (def, class, asignaciones, imports, también dentro de if/try/with de arriba).
    El bool dice si el módulo tiene `import *` o `__getattr__` (no se puede afirmar que falte un nombre)."""
    out: set[str] = set()
    abierto = False

    def ver(cuerpo: list[ast.stmt]) -> None:
        nonlocal abierto
        for n in cuerpo:
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                out.add(n.name)
                if n.name == "__getattr__":
                    abierto = True
            elif isinstance(n, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
                tg = n.targets if isinstance(n, ast.Assign) else [n.target]
                for x in tg:
                    for y in ast.walk(x):
                        if isinstance(y, ast.Name):
                            out.add(y.id)
            elif isinstance(n, (ast.Import, ast.ImportFrom)):
                for a in n.names:
                    if a.name == "*":
                        abierto = True
                    out.add(a.asname or a.name.split(".")[0])
            elif isinstance(n, (ast.If, ast.Try, ast.With, ast.For, ast.While)):
                for campo in ("body", "orelse", "finalbody"):
                    ver(getattr(n, campo, []) or [])
                for h in getattr(n, "handlers", []) or []:
                    ver(h.body)
    ver(t.body)
    return out, abierto


def _lugares(t: ast.Module):
    """(nodo, 'arriba' | 'en <func>') para cada sentencia de arriba y cada función/método."""
    for st in t.body:
        if isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef)):
            yield st, f"en {st.name}"
        elif isinstance(st, ast.ClassDef):
            for b in st.body:
                if isinstance(b, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    yield b, f"en {st.name}.{b.name}"
                else:
                    yield b, "arriba"
        else:
            yield st, "arriba"


def importados(f: Path, t: ast.Module, nombres: dict[str, tuple[set[str], bool]]) -> tuple[dict, list]:
    """({archivo importado: ['arriba'|'en <función>'|'importlib'…]}, [imports rotos])."""
    out: dict[str, list[str]] = {}
    rotos: list[dict] = []

    def poner(dst: Path, donde: str) -> None:
        if dst.is_dir():
            dst = dst / "__init__.py"
            if not dst.exists():
                return
        k = rel(dst)
        if k == rel(f):
            return
        out.setdefault(k, [])
        if donde not in out[k]:
            out[k].append(donde)

    for nodo, donde in _lugares(t):
        for n in ast.walk(nodo):
            if isinstance(n, ast.Import):
                for a in n.names:
                    r = resolver(a.name, 0, f)
                    if r is not None:
                        poner(r, donde)
            elif isinstance(n, ast.ImportFrom):
                r = resolver(n.module, n.level, f)
                if r is None:
                    continue
                for a in n.names:
                    if a.name == "*":
                        poner(r, donde)
                        continue
                    if r.is_dir():
                        sub = r / f"{a.name}.py"
                        if sub.exists():
                            poner(sub, donde)
                            continue
                        ini = r / "__init__.py"
                        tiene = ini.exists() and (a.name in nombres.get(rel(ini), (set(), False))[0])
                        if not tiene:
                            rotos.append({"linea": n.lineno, "donde": donde, "falta": f"{rel(r)}/{a.name}.py",
                                          "import": f"from {'.' * n.level}{n.module or ''} import {a.name}"})
                        elif ini.exists():
                            poner(ini, donde)
                        continue
                    poner(r, donde)
                    ns, abierto = nombres.get(rel(r), (set(), True))
                    if not abierto and a.name not in ns:
                        rotos.append({"linea": n.lineno, "donde": donde, "falta": f"{rel(r)}:{a.name}",
                                      "import": f"from {'.' * n.level}{n.module or ''} import {a.name}"})
            elif isinstance(n, ast.Call):
                fn = n.func
                nom = fn.attr if isinstance(fn, ast.Attribute) else (fn.id if isinstance(fn, ast.Name) else "")
                if nom in ("import_module", "__import__") and n.args and isinstance(n.args[0], ast.Constant) \
                        and isinstance(n.args[0].value, str):
                    r = resolver(n.args[0].value, 0, f)
                    if r is not None:
                        poner(r, f"{donde} (importlib)")
    return out, rotos


def lanzados(f: Path, t: ast.Module, pys: set[str]) -> dict[str, list[int]]:
    """`*.py` de producción que el archivo lanza por subprocess: en un archivo que usa subprocess, cada string que es
    exactamente el nombre de un `.py` de producción (o `-m paquete.modulo`). {archivo: [líneas]}."""
    src = f.read_text(encoding="utf-8-sig", errors="replace")
    if "subprocess" not in src:
        return {}
    por_nombre = {Path(p).name: p for p in pys if "/" not in p}
    por_mod = {p[:-3].replace("/", "."): p for p in pys}
    out: dict[str, list[int]] = {}
    for n in ast.walk(t):
        if isinstance(n, ast.Constant) and isinstance(n.value, str):
            v = n.value.strip().replace("\\", "/")
            dst = por_nombre.get(v) or (v if v in pys else None) or por_mod.get(v)
            if dst and dst != rel(f):
                out.setdefault(dst, []).append(n.lineno)
    return out


# ─────────────────────────── funciones y referencias ───────────────────────────
def funciones(t: ast.Module) -> list[dict]:
    out = []
    for n in t.body:
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            out.append({"nombre": n.name, "linea": n.lineno, "tipo": "funcion"})
        elif isinstance(n, ast.ClassDef):
            out.append({"nombre": n.name, "linea": n.lineno, "tipo": "clase"})
            for b in n.body:
                if isinstance(b, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    out.append({"nombre": f"{n.name}.{b.name}", "linea": b.lineno, "tipo": "metodo"})
    return out


def referencias(t: ast.Module) -> tuple[set[str], set[str]]:
    """(nombres usados como Name/Attribute/alias de import, strings constantes que parecen identificadores)."""
    usos, strs = set(), set()
    for n in ast.walk(t):
        if isinstance(n, ast.Name):
            usos.add(n.id)
        elif isinstance(n, ast.Attribute):
            usos.add(n.attr)
        elif isinstance(n, ast.alias):
            usos.add(n.name.split(".")[-1])
        elif isinstance(n, ast.keyword) and n.arg:
            pass
        elif isinstance(n, ast.Constant) and isinstance(n.value, str) and re.fullmatch(r"[A-Za-z_]\w*", n.value):
            strs.add(n.value)
    return usos, strs


def es_entrada(t: ast.Module) -> bool:
    for n in t.body:
        if isinstance(n, ast.If) and isinstance(n.test, ast.Compare):
            partes = [n.test.left, *n.test.comparators]
            if any(isinstance(x, ast.Name) and x.id == "__name__" for x in partes) and \
                    any(isinstance(x, ast.Constant) and x.value == "__main__" for x in partes):
                return True
    return False


def doc(t: ast.Module | None) -> str:
    d = (ast.get_docstring(t) if t else "") or ""
    return re.sub(r"\s+", " ", d.split("\n\n")[0]).strip()[:600]


# ─────────────────────────── git (una pasada) ───────────────────────────
def tanda_de(asunto: str) -> str:
    m = re.match(r"^\w+\(([Ff]\d+[A-Za-z0-9]*)", asunto) or re.search(r"\b[Ff](\d+[a-z]?)\b", asunto)
    if not m:
        return ""
    g = m.group(1)
    return ("F" + g[1:]) if g[:1] in "fF" and g[1:2].isdigit() else ("F" + g)


def git_historia(rutas: list[str]) -> dict[str, dict]:
    r = subprocess.run(["git", "log", "--format=@@%h\t%ad\t%s", "--date=short", "--name-status", "-M", "--", *rutas],
                       cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
    out: dict[str, dict] = {}
    actual = None
    for ln in r.stdout.splitlines():
        if ln.startswith("@@"):
            h, fecha, asunto = (ln[2:].split("\t", 2) + ["", ""])[:3]
            actual = {"commit": h, "fecha": fecha, "asunto": asunto[:140], "tanda": tanda_de(asunto)}
            continue
        if not ln.strip() or actual is None:
            continue
        cols = ln.split("\t")
        st, ruta = cols[0], cols[-1]
        e = out.setdefault(ruta, {})
        e.setdefault("ultimo", actual)                 # git log va de lo nuevo a lo viejo
        if st.startswith(("A", "R", "C")):
            e["nacio"] = actual                        # se pisa hasta quedar el más viejo
    return out


# ─────────────────────────── la secuencia del form (run_pipeline, AST) ───────────────────────────
def _cmd_de_lista(n: ast.List, constantes: dict[str, list[str]]) -> list[str]:
    out = []
    for e in n.elts:
        if isinstance(e, ast.Constant):
            out.append(str(e.value))
        elif isinstance(e, ast.Starred) and isinstance(e.value, ast.Name) and e.value.id in constantes:
            out += constantes[e.value.id]
        elif isinstance(e, ast.Name):
            out.append(f"<{e.id}>")
        elif isinstance(e, ast.JoinedStr):
            out.append("".join(v.value if isinstance(v, ast.Constant) else "<…>" for v in e.values))
        else:
            out.append("<…>")
    return out


def secuencia(rp: Path) -> dict:
    """Las etapas de `run_pipeline.sequence` en orden (ETAPAS), con la función de `_PASOS`, el encabezado, los
    comandos `python …` que lanza y la compuerta (menú del form) que muestra. Más la etapa de research de `main`."""
    t = ast.parse(rp.read_text(encoding="utf-8"))
    etapas: list[str] = []
    pasos: dict[str, str] = {}
    constantes: dict[str, list[str]] = {}
    funcs = {n.name: n for n in t.body if isinstance(n, ast.FunctionDef)}
    for n in t.body:
        if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name):
            k = n.targets[0].id
            if k == "ETAPAS" and isinstance(n.value, ast.Tuple):
                etapas = [e.value for e in n.value.elts if isinstance(e, ast.Constant)]
            elif k == "_PASOS" and isinstance(n.value, ast.Dict):
                pasos = {kk.value: vv.id for kk, vv in zip(n.value.keys, n.value.values)
                         if isinstance(kk, ast.Constant) and isinstance(vv, ast.Name)}
            elif isinstance(n.value, ast.List) and all(isinstance(e, ast.Constant) for e in n.value.elts):
                constantes[k] = [str(e.value) for e in n.value.elts]

    def leer(fn: ast.FunctionDef) -> dict:
        d = {"funcion": fn.name, "linea": fn.lineno, "encabezado": "", "comandos": [], "compuertas": [],
             "sin_form": "", "doc": doc(ast.Module(body=fn.body, type_ignores=[]))}
        for n in ast.walk(fn):
            if isinstance(n, ast.Call):
                nom = n.func.id if isinstance(n.func, ast.Name) else (n.func.attr if isinstance(n.func, ast.Attribute)
                                                                       else "")
                if nom == "_phase_header" and n.args and isinstance(n.args[0], ast.Constant):
                    d["encabezado"] = n.args[0].value
                elif nom == "_compuerta" and n.args and isinstance(n.args[0], ast.Constant):
                    d["compuertas"].append({"menu": n.args[0].value, "linea": n.lineno, "solo_con_form": True})
                elif nom == "emit_choice_marker":
                    for kw in n.keywords:
                        if kw.arg == "menu" and isinstance(kw.value, ast.Constant):
                            d["compuertas"].append({"menu": kw.value.value, "linea": n.lineno, "solo_con_form": True})
            if isinstance(n, ast.List) and n.elts and isinstance(n.elts[0], ast.Constant) \
                    and str(n.elts[0].value).endswith(".py"):
                c = _cmd_de_lista(n, constantes)
                if c not in [x["argv"] for x in d["comandos"]]:
                    d["comandos"].append({"argv": c, "linea": n.lineno, "script": c[0]})
            if isinstance(n, ast.If) and isinstance(n.test, ast.UnaryOp) and isinstance(n.test.op, ast.Not) \
                    and isinstance(n.test.operand, ast.Name) and n.test.operand.id == "QA_FORM":
                d["sin_form"] = "para y reporta el comando (la compuerta no se aprueba sola)"
        return d

    out = []
    main = funcs.get("main")
    if main is not None:
        r = leer(main)
        r["comandos"] = [c for c in r["comandos"] if c["script"] == "fase1.py"]
        if r["comandos"]:
            out.append({"etapa": "research", "orden": 0, "funcion": "main (--research)", "linea": r["comandos"][0]["linea"],
                        "encabezado": "RESEARCH (fase1)", "comandos": r["comandos"], "compuertas": [],
                        "sin_form": "", "doc": "Research a pedido del form: fase1 --no-chain (semilla + research + "
                                               "validación) y después la secuencia del topic que produjo."})
    for i, e in enumerate(etapas, 1):
        if e not in pasos:
            out.append({"etapa": e, "orden": i, "funcion": None, "encabezado": "", "comandos": [], "compuertas": [],
                        "sin_form": "", "doc": "(sin paso: fin de la cadena)"})
            continue
        r = leer(funcs[pasos[e]])
        r.update(etapa=e, orden=i)
        out.append(r)
    return {"archivo": rel(rp), "etapas": out, "ETAPAS": etapas, "_PASOS": pasos}


# ─────────────────────────── alcance ───────────────────────────
def alcance(desde: str, aristas: dict[str, set[str]], cortar: set[str] = frozenset()) -> set[str]:
    vistos, pila = {desde}, [desde]
    while pila:
        x = pila.pop()
        for y in aristas.get(x, ()):
            if y not in vistos and y not in cortar:
                vistos.add(y)
                pila.append(y)
    return vistos


# ─────────────────────────── tests (A.4) ───────────────────────────
# Lo que delata un script (no un módulo de tests) en el código de arriba de un test_*.py: importarlo lo ejecuta. F42:
# `test_full_pipeline_lab.py` llamó a Gemini y a FAL durante una colecta; estos no se importan nunca.
_EFECTOS = re.compile(r"\b(requests|genai|Client|APIConfig|generate_content|urlopen|subprocess|Popen|mkdir|write_text|"
                      r"write_bytes|exit|exec_module|ModuleType|print|input)\b")


def efectos_al_importar(p: Path) -> list[str]:
    """Líneas de arriba (fuera de def/class/imports/docstring/`if __name__`) con red, escritura, salida o prints."""
    t = arbol(p)
    if t is None:
        return ["(error de sintaxis)"]
    out = []
    for n in t.body:
        if isinstance(n, (ast.Import, ast.ImportFrom, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        if isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant):
            continue
        if isinstance(n, ast.If) and "__main__" in ast.dump(n.test):
            continue
        hits = sorted(set(_EFECTOS.findall(ast.unparse(n))))
        if hits:
            out.append(f"{n.lineno}: {', '.join(hits)}")
    return out


def colecta_tests() -> dict:
    """`pytest --collect-only -q` sobre los test_*.py de la raíz que no tienen efectos al importarse, en una sola
    llamada (no corre tests), con `HTTP(S)_PROXY` a un puerto muerto: cualquier HTTP que se cuele falla en vez de
    gastar. Los que tienen efectos (scripts de lab con llamadas a API a nivel de módulo) no se importan: quedan como
    «no colectado» con la línea que lo prueba. Por archivo: cuántos tests colecta o el error de import."""
    todos = sorted(p.name for p in ROOT.glob("test_*.py"))
    excluidos = {t: e for t in todos if (e := efectos_al_importar(ROOT / t))}
    tests = [t for t in todos if t not in excluidos]
    muerto = "http://127.0.0.1:9"      # derivado: puerto «discard», nadie escucha; corta la red sin tocar config
    env = {**os.environ, "PYTHONIOENCODING": "utf-8", "HTTP_PROXY": muerto, "HTTPS_PROXY": muerto,
           "http_proxy": muerto, "https_proxy": muerto, "NO_PROXY": "", "no_proxy": ""}
    r = subprocess.run([sys.executable, "-m", "pytest", "--collect-only", "-q", "-p", "no:cacheprovider", *tests],
                       cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", env=env,
                       timeout=900)
    out = {t: {"colecta": 0, "error": ""} for t in tests}
    for t, e in excluidos.items():
        out[t] = {"colecta": 0, "error": "", "no_colectado": "efectos al importarse (script): " + "; ".join(e[:3])}
    for ln in r.stdout.splitlines():
        m = re.match(r"^(test_[\w]+\.py)::", ln)
        if m and m.group(1) in out:
            out[m.group(1)]["colecta"] += 1
    # bloques «_ ERROR collecting test_x.py _» … hasta el siguiente bloque
    bloques = re.split(r"^_+ ERROR collecting (\S+) _+$", r.stdout, flags=re.M)
    for i in range(1, len(bloques) - 1, 2):
        nom, cuerpo = Path(bloques[i]).name, bloques[i + 1]
        err = [x.strip() for x in cuerpo.splitlines() if re.match(r"^E\s+\w*(Error|Exception)", x.strip())]
        out.setdefault(nom, {"colecta": 0, "error": ""})["error"] = (err[-1][1:].strip() if err else "error de colecta")[:300]
    resumen = (r.stdout.strip().splitlines() or [""])[-1]
    return {"comando": "python -m pytest --collect-only -q -p no:cacheprovider test_*.py", "exit": r.returncode,
            "resumen": resumen, "archivos": out}


# ─────────────────────────── armado ───────────────────────────
def hechos() -> dict:
    pys = py_produccion()
    otros = no_py_produccion(pys)
    tests = sorted(ROOT.glob("test_*.py"))
    prod = {rel(p) for p in pys}
    arboles = {rel(p): arbol(p) for p in pys + tests}
    nombres = {k: nombres_de_arriba(t) for k, t in arboles.items() if t is not None}
    for d in PAQUETES:                                    # los __init__ que no están en producción igual cuentan
        ini = ROOT / d / "__init__.py"
        if ini.exists() and rel(ini) not in nombres and (t := arbol(ini)) is not None:
            nombres[rel(ini)] = nombres_de_arriba(t)
    hist = git_historia(sorted(prod | {rel(p) for p in otros}))
    H: dict[str, dict] = {}
    refs: dict[str, tuple[set[str], set[str]]] = {}
    for p in pys + tests:
        k, t = rel(p), arboles[rel(p)]
        if t is None:
            if k in prod:
                H[k] = {"archivo": k, "tipo": "py", "error_sintaxis": True, "md5": md5(p)}
            continue
        refs[k] = referencias(t)
        if k not in prod:
            continue
        imp, rotos = importados(p, t, nombres)
        H[k] = {"archivo": k, "modulo": p.stem, "tipo": "py", "lineas": len(p.read_text(encoding="utf-8-sig",
                                                                                       errors="replace").splitlines()),
                "md5": md5(p), "doc": "" if p.name == "config.py" else doc(t), "entrada": es_entrada(t),
                "funciones": funciones(t), "importa": imp, "lanza": lanzados(p, t, prod), "imports_rotos": rotos,
                "lo_importan": {}, "lo_lanzan": {}, "tests": [], "nacio": hist.get(k, {}).get("nacio"),
                "ultimo": hist.get(k, {}).get("ultimo")}
        if p.name == "config.py":                           # solo nombres de claves, nunca valores
            H[k]["claves"] = sorted(x for x in nombres[k][0] if x.isupper())
    # quién importa / lanza / testea a quién
    T: dict[str, dict] = {}
    for p in pys + tests:
        k, t = rel(p), arboles[rel(p)]
        if t is None:
            if k not in prod:
                T[k] = {"importa": [], "imports_rotos": [{"linea": 0, "falta": "(error de sintaxis)"}]}
            continue
        if k in H:
            imp = H[k]["importa"]
        else:
            imp, rotos_t = importados(p, t, nombres)
            T[k] = {"importa": sorted(d for d in imp if d in prod), "imports_rotos": rotos_t}
        for dst, donde in imp.items():
            if dst in H:
                if k in prod:
                    H[dst]["lo_importan"][k] = donde
                else:
                    H[dst]["tests"].append(k)
        if k in H:
            for dst, lineas in H[k]["lanza"].items():
                H[dst]["lo_lanzan"][k] = lineas
    # funciones sin llamador (por nombre: Name/Attribute/alias; aparte, las que solo aparecen como string). Una
    # referencia cuenta solo desde el mismo archivo o desde uno que importa al módulo (si no, `main` o `nombres` de
    # otro módulo pasaban por llamadores); los strings cuentan desde cualquier archivo (despacho por nombre).
    for k, h in H.items():
        if h.get("tipo") != "py" or "funciones" not in h:
            continue
        vecinos = {k} | set(h["lo_importan"]) | set(h["tests"])
        for fn in h["funciones"]:
            nom = fn["nombre"].split(".")[-1]
            if nom.startswith("__") and nom.endswith("__"):
                fn.update(prod=["(dunder)"], tests=[], string=[])
                continue
            fn["prod"] = sorted(o for o in prod & vecinos if o in refs and nom in refs[o][0])
            fn["tests"] = sorted(o for o in vecinos - prod if o in refs and nom in refs[o][0])
            fn["string"] = sorted(o for o in prod if o in refs and nom in refs[o][1] and o not in fn["prod"])
            fn["sin_llamador"] = not fn["prod"] and not fn["string"]
    # no-.py
    textos = {k: (ROOT / k).read_text(encoding="utf-8-sig", errors="replace") for k in prod}
    claude_txt = {rel(p): p.read_text(encoding="utf-8", errors="replace")
                  for p in [ROOT / ".claude" / "settings.json", ROOT / "CLAUDE.md", *sorted((ROOT / ".claude").rglob("*.md"))]
                  if p.exists()}
    for p in otros:
        k = rel(p)
        e = {"archivo": k, "modulo": p.name, "tipo": p.suffix.lstrip(".") or "archivo", "md5": md5(p),
             "nacio": hist.get(k, {}).get("nacio"), "ultimo": hist.get(k, {}).get("ultimo"),
             "en_git": k in hist, "lo_referencian": []}
        if k.startswith("gfx_profiles/"):
            try:
                d = json.loads(p.read_text(encoding="utf-8"))
                e["claves"] = sorted(d) if isinstance(d, dict) else []
            except (ValueError, UnicodeDecodeError):
                e["claves"] = ["(no es JSON válido)"]
            e["lo_referencian"] = sorted(o for o, s in textos.items() if "gfx_profiles" in s)
            e["por_nombre_de_perfil"] = True
        elif k.startswith(".claude/"):
            e["lo_referencian"] = sorted(o for o, s in claude_txt.items() if p.name in s and o != k)
        else:
            e["lo_referencian"] = sorted(o for o, s in textos.items() if p.name in s)
        H[k] = e
    # la secuencia y el alcance
    seq = secuencia(ROOT / "run_pipeline.py")
    aristas: dict[str, set[str]] = {}
    for k, h in H.items():
        if h.get("tipo") == "py" and "importa" in h:
            aristas[k] = set(h["importa"]) | set(h["lanza"])
            ini = f"{Path(k).parent.as_posix()}/__init__.py"     # importar un submódulo corre el __init__ del paquete
            if "/" in k and ini in H and ini != k:
                aristas[k].add(ini)
        for o in h.get("lo_referencian", []) if h.get("tipo") != "py" else []:
            aristas.setdefault(o, set()).add(k)
    form = sorted(k for k, h in H.items() if h.get("tipo") == "py" and FORM_HTML in textos.get(k, ""))
    orq = seq["archivo"]
    scripts_etapa: dict[str, list[str]] = {}
    for e in seq["etapas"]:
        for c in e["comandos"]:
            s = c["script"]
            if s in H:
                scripts_etapa.setdefault(s, [])
                if e["etapa"] not in scripts_etapa[s]:
                    scripts_etapa[s].append(e["etapa"])
    alc_script = {s: alcance(s, aristas, cortar={orq, *form}) for s in scripts_etapa}
    alc_form = set()
    for f in form:
        alc_form |= alcance(f, aristas)
    entradas = [k for k, h in H.items() if h.get("entrada")]
    manual = set()
    for en in entradas:
        if en in alc_form:
            continue
        manual |= alcance(en, aristas, cortar=alc_form)
    for k, h in H.items():
        scs = sorted(s for s, a in alc_script.items() if k in a)
        h["scripts_que_lo_alcanzan"] = scs
        h["etapas"] = sorted({e for s in scs for e in scripts_etapa[s]},
                             key=lambda x: [e["etapa"] for e in seq["etapas"]].index(x))
        h["compartido"] = len(scs) > 1
        if k.startswith(".claude/"):
            h["estado_a"] = "solo herramienta manual"     # lo carga Claude Code, no el video
            h["etapas"] = ["Claude Code"]
        elif k in alc_form:
            h["estado_a"] = "vivo"
            if not h["etapas"]:
                h["etapas"] = ["orquestador/form"]
        elif k in manual:
            h["estado_a"] = "solo herramienta manual"
        else:
            h["estado_a"] = "huérfano"
        if h.get("imports_rotos"):
            h["estado_a"] += " · roto"
    return {"generado_por": "lab/tools/mapa_hechos.py (F42 §A)", "form": form, "orquestador": orq,
            "secuencia": seq, "scripts_de_etapa": scripts_etapa, "entradas": sorted(entradas), "modulos": H,
            "tests": T}


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--stdout", action="store_true")
    ap.add_argument("--tests", action="store_true", help="además colecta los tests (pytest --collect-only)")
    a = ap.parse_args()
    h = hechos()
    if a.stdout:
        print(json.dumps(h, ensure_ascii=False, indent=1))
        return
    SALIDA.mkdir(parents=True, exist_ok=True)
    (SALIDA / "hechos.json").write_text(json.dumps(h, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"hechos: {len(h['modulos'])} archivos de producción → {rel(SALIDA / 'hechos.json')}")
    if a.tests:
        c = colecta_tests()
        (SALIDA / "tests_collect.json").write_text(json.dumps(c, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"tests: {c['resumen']} → {rel(SALIDA / 'tests_collect.json')}")


if __name__ == "__main__":
    main()
