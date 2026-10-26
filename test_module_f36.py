"""
test_module_f36.py — F36 (estructura de la capa de texto), sin red. Cada parte agrega sus tests con el caso real.
"""
from __future__ import annotations

import ast
import re
import subprocess
from pathlib import Path

import pytest

from script_engine import gfx_rotulista as gro
from script_engine import rotulista_filtros as rf

ROOT = Path(__file__).resolve().parent
F34 = "1973ba1"                      # el cierre de F34: la base de F36


def _f34(path: str) -> str:
    r = subprocess.run(["git", "show", f"{F34}:{path}"], cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        pytest.skip(f"sin git o sin {F34}")
    return r.stdout


def _cuerpo(src: str, fn: str) -> str:
    t = ast.parse(src)
    n = next(x for x in t.body if isinstance(x, ast.FunctionDef) and x.name == fn)
    return ast.get_source_segment(src, n) or ""


# ═══════════════ A: partir el rotulista sin cambiar comportamiento ═══════════════

def test_a_orden_de_filtros_es_el_de_f34():
    """El orden en que `validar` de F34 sacaba un bloque (la secuencia de `fuera(b, "<regla>"` en su código, sin
    repetidos seguidos) y después `finalizar` (cantidad) es exactamente `ORDEN`. Se lee del código de 1973ba1."""
    src = _f34("script_engine/gfx_rotulista.py")
    reglas = re.findall(r'fuera\(b, "(\w+)"', _cuerpo(src, "validar"))
    f34 = [r for k, r in enumerate(reglas) if k == 0 or reglas[k - 1] != r]
    assert '"regla": "cantidad"' in _cuerpo(src, "finalizar")
    f34.append("cantidad")
    assert f34 == ["anclaje", "no_dicho", "forma", "candado", "no_dicho", "spoiler", "lectura", "coherencia", "cantidad"]
    assert [rf.regla(f) for f in rf.ORDEN] == f34
    assert [f.__name__ for f in rf.ORDEN][:2] == ["anclaje", "gancho_dicho"]     # el no_dicho del gancho, antes de la forma


def test_a_la_fachada_da_todos_los_nombres_de_antes():
    """gfx_rotulista sigue teniendo cada nombre de nivel de módulo que tenía en F34 (nadie cambia de import)."""
    t = ast.parse(_f34("script_engine/gfx_rotulista.py"))
    antes = set()
    for n in t.body:
        if isinstance(n, (ast.FunctionDef, ast.ClassDef)):
            antes.add(n.name)
        elif isinstance(n, ast.Assign):
            antes |= {x.id for x in n.targets if isinstance(x, ast.Name)}
        elif isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name):
            antes.add(n.target.id)
    faltan = sorted(x for x in antes if not hasattr(gro, x))
    assert not faltan, faltan


def test_a_cada_modulo_tiene_lo_suyo():
    from script_engine import clima, rotulista_colocar, rotulista_llm, voz_datos, voz_utils
    from script_engine import gfx_peak
    assert gro.validar is rf.validar and gro.finalizar is rf.finalizar is rf.cantidad
    assert gro.llamar is rotulista_llm.llamar and gro.entrada is rotulista_llm.entrada
    assert gro.colocar is rotulista_colocar.colocar and gro.escena_final is rotulista_colocar.escena_final
    assert gro.sellos_por_tema is clima.sellos_por_tema and gfx_peak.peak_word is clima.peak_word
    assert gro.reloj_de_voz is voz_datos.reloj_de_voz and gro.tarjeta_inicial is voz_datos.tarjeta_inicial
    assert gro.numeros is voz_utils.numeros and gro._EN_VUELO is rotulista_llm._EN_VUELO
    assert gro.prompt_md5() == "d90ae69a2dc8c7928bd410ead421dc6b"      # el prompt de F34 (F34_REPORT): A no lo toca
    assert rotulista_llm.PROMPT_VERSION == "f34-1"


def test_a_guard_mapa_avisa_tambien_por_los_modulos_nuevos():
    import importlib.util
    spec = importlib.util.spec_from_file_location("gm", ROOT / ".claude" / "hooks" / "guard_mapa.py")
    gm = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gm)
    for f in ("rotulista_llm", "rotulista_filtros", "rotulista_colocar", "clima", "voz_datos", "voz_utils"):
        assert "guard_mapa" in gm.aviso([f"script_engine/{f}.py"])
    assert gm.aviso(["script_engine/clima.py", "lab/MAPA_MODULOS.json"]) is None
