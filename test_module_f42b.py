"""F42b — las librerías del form y que una falla se vea como falla. Sin red ni API: `find_spec` simulado, `_run` y
`sequence` stubeados, el research de la semilla simulado. Correr con el proxy muerto de F42:

    HTTP_PROXY=http://127.0.0.1:9 HTTPS_PROXY=http://127.0.0.1:9 python -m pytest -q test_module_f42b.py
"""
from __future__ import annotations

import importlib.machinery
import importlib.util
import sys

import pytest

import dependencias
import run_pipeline as rp

_FIND_SPEC = importlib.util.find_spec


def _specs(faltan: set[str]):
    """find_spec simulado: None para las librerías de `faltan` (por su nombre de arriba); un spec de mentira para el
    resto, así el test no depende de lo que tenga instalado el Python que lo corre."""
    def find_spec(name, package=None):
        if name.split(".")[0] in faltan:
            return None
        return importlib.machinery.ModuleSpec(name, None, origin="stub")
    return find_spec


@pytest.fixture
def sin_etapas(monkeypatch):
    """`_run` y `sequence` que registran; `_run` falla si lo llaman cuando no debe (lo decide cada test)."""
    llamadas: list = []
    monkeypatch.setattr(rp, "_run", lambda cmd: pytest.fail(f"no debía correr ninguna etapa: {cmd}"))
    monkeypatch.setattr(rp, "sequence", lambda tid, batch=False: llamadas.append(tid) or 0)
    return llamadas


# ═══════════════════════ B ═══════════════════════

def test_dependencias_lee_requeridas_y_opcionales_del_codigo():
    """Sobre el código real: bs4 es requerida (import suelto en html_to_text) y trafilatura opcional (dentro del try)."""
    libs = dependencias.libs_cache()
    assert libs["bs4"]["requerida"] is True
    assert libs["trafilatura"]["requerida"] is False
    assert any(a == "researcher_steps/research_v3.py" for a, _, _ in libs["bs4"]["sitios"])


def test_falta_bs4_para_antes_de_gastar(monkeypatch, sin_etapas, capsys):
    """`--research` sin bs4 → exit 1, la lista con el archivo:línea que da dependencias y el comando de pip; ninguna
    etapa corre (el stub de `_run` falla si lo llaman)."""
    monkeypatch.setattr(importlib.util, "find_spec", _specs({"bs4"}))
    monkeypatch.setattr(sys, "argv", ["run_pipeline.py", "--research", "--video-type", "long", "--batch"])
    assert rp.main() == 1
    out = capsys.readouterr().out
    sitios = next(f["sitios"] for f in dependencias.tabla() if f["libreria"] == "bs4")
    assert f"- bs4: {', '.join(sitios)}" in out
    assert dependencias.comando_pip() in out and "PARADA antes de gastar" in out
    assert sin_etapas == []
    print(out)


def test_opcional_faltante_solo_avisa_y_sigue(monkeypatch, sin_etapas, capsys):
    monkeypatch.setattr(importlib.util, "find_spec", _specs({"trafilatura"}))
    monkeypatch.setattr(sys, "argv", ["run_pipeline.py", "--topic", "t1"])
    assert rp.main() == 0
    out = capsys.readouterr().out
    assert "opcionales que faltan" in out and "trafilatura" in out and "PARADA" not in out
    assert sin_etapas == ["t1"]


def test_con_todo_presente_sigue_igual(monkeypatch, sin_etapas, capsys):
    monkeypatch.setattr(importlib.util, "find_spec", _specs(set()))
    monkeypatch.setattr(sys, "argv", ["run_pipeline.py", "--topic", "t1", "--batch"])
    assert rp.main() == 0
    out = capsys.readouterr().out
    assert "PARADA" not in out and "opcionales" not in out
    assert sin_etapas == ["t1"]
