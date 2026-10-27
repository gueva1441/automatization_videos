"""
test_constantes_con_origen.py — F33 §A.2: toda constante numérica de `GfxRules`, `GfxRenderSettings` (gfx_config.py) y
`TransitionRenderSettings` (transition_config.py) declara su origen en un comentario de la misma línea:
    # DECISIONES: <línea o fecha>   · # identidad F3   · # estándar: <nombre>   · # derivado: <de qué>   · # medido: <dónde>
**Modo inventario** (F33): el test no falla por las que no lo tienen; las lista (`python test_constantes_con_origen.py`
imprime la tabla para el reporte). Con `CONSTANTES_ESTRICTO=1` falla si queda alguna sin origen.
Constante numérica = int o float (no bool), o un dict/tupla cuyos valores son todos números.
"""
from __future__ import annotations

import ast
import io
import json
import os
import re
import sys
import tokenize
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CLASES = {"gfx_config.py": ("GfxRules", "GfxRenderSettings"), "transition_config.py": ("TransitionRenderSettings",)}
ORIGEN = re.compile(r"(DECISIONES:\s*\S|identidad F3|estándar:\s*\S|derivado:\s*\S|medido:\s*\S)")


def _numerica(v: ast.AST) -> bool:
    if isinstance(v, ast.Constant):
        return isinstance(v.value, (int, float)) and not isinstance(v.value, bool)
    if isinstance(v, ast.UnaryOp) and isinstance(v.op, ast.USub):
        return _numerica(v.operand)
    if isinstance(v, (ast.Tuple, ast.List)):
        return bool(v.elts) and all(_numerica(e) for e in v.elts)
    if isinstance(v, ast.Dict):
        return bool(v.values) and all(_numerica(e) for e in v.values)
    if isinstance(v, ast.Call) and getattr(v.func, "id", "") == "field":      # field(default_factory=lambda: {...})
        for kw in v.keywords:
            if kw.arg == "default_factory" and isinstance(kw.value, ast.Lambda):
                return _numerica(kw.value.body)
    return False


def _comentarios(src: str) -> dict[int, str]:
    out: dict[int, str] = {}
    for tok in tokenize.generate_tokens(io.StringIO(src).readline):
        if tok.type == tokenize.COMMENT:
            out[tok.start[0]] = tok.string
    return out


def constantes() -> list[dict]:
    """Una fila por constante numérica: archivo, clase, nombre, valor, línea, comentario, origen (o None)."""
    filas = []
    for archivo, clases in CLASES.items():
        src = (ROOT / archivo).read_text(encoding="utf-8")
        com = _comentarios(src)
        for nodo in ast.parse(src).body:
            if not (isinstance(nodo, ast.ClassDef) and nodo.name in clases):
                continue
            for st in nodo.body:
                if isinstance(st, ast.AnnAssign) and isinstance(st.target, ast.Name) and st.value is not None \
                        and _numerica(st.value):
                    c = com.get(st.lineno, "")
                    m = ORIGEN.search(c)
                    filas.append({"archivo": archivo, "clase": nodo.name, "nombre": st.target.id,
                                  "valor": ast.get_source_segment(src, st.value), "linea": st.lineno, "comentario": c,
                                  "origen": m.group(1) if m else None})
    return filas


def perfil_tokens() -> dict:
    """Los tokens del perfil activo (la identidad F3 que pisa los defaults del motor)."""
    try:
        return json.loads((ROOT / "gfx_profiles" / "misterio.json").read_text(encoding="utf-8")).get("tokens") or {}
    except (OSError, ValueError):
        return {}


def test_inventario_de_constantes():
    filas = constantes()
    assert len(filas) > 60                                    # el parser encontró las clases (F36 §D: 81 tras borrar perillas)
    assert {f["clase"] for f in filas} == {"GfxRules", "GfxRenderSettings", "TransitionRenderSettings"}
    sin = [f for f in filas if not f["origen"]]
    if os.environ.get("CONSTANTES_ESTRICTO") == "1":
        assert not sin, f"{len(sin)} constantes sin origen: {[f['nombre'] for f in sin]}"
    # las que CC etiquetó en F33 (identidad F3 y las que nombra DECISIONES.md) tienen la forma pedida
    por = {f["nombre"]: f for f in filas}
    assert por["title_dur"]["origen"] == "identidad F3" and por["dip_frames"]["origen"] == "identidad F3"
    assert por["workers"]["origen"].startswith("DECISIONES:")


def test_un_comentario_sin_la_forma_no_cuenta():
    assert not ORIGEN.search("# F2 §0b.2: 30 % más chica")
    assert ORIGEN.search("# identidad F3 · Black") and ORIGEN.search("# estándar: subtitulado 15 cps")
    assert not ORIGEN.search("# medido:")                     # la forma exige el dato


def tabla() -> str:
    filas, tok = constantes(), perfil_tokens()
    sin = [f for f in filas if not f["origen"]]
    L = [f"{len(filas)} constantes numéricas · {len(filas) - len(sin)} con origen · **{len(sin)} sin origen**", "",
         "| # | constante | valor del motor | valor del perfil (si lo pisa) | archivo:línea | comentario de hoy |",
         "|---|---|---|---|---|---|"]
    for k, f in enumerate(sin, 1):
        pv = tok.get(f["nombre"])
        pisa = "" if pv is None else (json.dumps(pv) if str(pv) != f["valor"] else "= (igual)")
        com = f["comentario"].lstrip("# ").replace("|", "\\|")
        L.append(f"| {k} | `{f['clase']}.{f['nombre']}` | `{f['valor']}` | {pisa} | {f['archivo']}:{f['linea']} | {com} |")
    L += ["", "Con origen:", ""] + [f"- `{f['clase']}.{f['nombre']}` = `{f['valor']}` · {f['origen']}"
                                   for f in filas if f["origen"]]
    return "\n".join(L)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    print(tabla())
