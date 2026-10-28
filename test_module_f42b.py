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


# ═══════════════════════ C ═══════════════════════

SEMILLA = {"seed_id": "s-waverly", "seed_title": "Hospital Waverly Hills embrujado", "discovery_mode": "manual"}


@pytest.fixture
def fase1_sin_red(tmp_path, monkeypatch):
    """`fase1.run_latido_a` de punta a punta sin red ni disco del repo: bandeja en tmp_path, juez/pick/re-medición
    stubeados, `error_handler` y `cost_tracker` mudos. `_research_seed_deep` lo pone cada test."""
    import json

    import fase1
    import topic_researcher as tr
    from script_engine import m_judge_seeds

    bandeja = tmp_path / "selected_seeds.json"
    bandeja.write_text(json.dumps({"seeds": [SEMILLA]}), encoding="utf-8")
    monkeypatch.setattr(tr, "SEEDS_FILE", bandeja)
    monkeypatch.setattr(tr, "_load_topics_db", lambda: {"topics": []})
    monkeypatch.setattr(tr, "_save_topics_db", lambda db: None)
    monkeypatch.setattr(tr.error_handler, "log_error", lambda *a, **k: None)
    monkeypatch.setattr(m_judge_seeds, "judge_seeds", lambda seeds, force=False: seeds)
    for nombre, f in {"_audit_pending_promises": lambda: None, "_write_research_sentinel": lambda tids: None,
                      "_load_seeds": lambda: [dict(SEMILLA)], "_save_seeds_with_judge": lambda s: None,
                      "_print_judge_summary": lambda s: None, "_select_seed_interactive": lambda s: s,
                      "_verify_pick_es_saturation": lambda c, n=3: c, "_close_cost_tracking": lambda: None,
                      "load_db": lambda: {"topics": []}}.items():
        monkeypatch.setattr(fase1, nombre, f)
    monkeypatch.setattr(fase1, "_QA_FORM", False)

    def bandeja_ids():
        return [s["seed_id"] for s in json.loads(bandeja.read_text(encoding="utf-8"))["seeds"]]
    return fase1, tr, bandeja_ids


def test_research_que_truena_sale_con_1_y_la_semilla_sigue(fase1_sin_red, monkeypatch, capsys):
    fase1, tr, bandeja_ids = fase1_sin_red

    def truena(seed, titles):
        raise ModuleNotFoundError("No module named 'bs4'")
    monkeypatch.setattr(tr, "_research_seed_deep", truena)
    rc = fase1.run_latido_a(video_type="long", skip_niche=True, no_chain=True)
    out = capsys.readouterr().out
    assert rc == 1
    assert "semilla «Hospital Waverly Hills embrujado»: ModuleNotFoundError: No module named 'bs4'; sigue en la bandeja" in out
    assert bandeja_ids() == ["s-waverly"]
    print(out)


def test_soltar_el_pick_sale_con_0(fase1_sin_red, monkeypatch):
    fase1, tr, bandeja_ids = fase1_sin_red
    monkeypatch.setattr(fase1, "_select_seed_interactive", lambda s: None)
    monkeypatch.setattr(tr, "_research_seed_deep", lambda s, t: pytest.fail("no debía investigar"))
    assert (fase1.run_latido_a(video_type="long", skip_niche=True, no_chain=True) or 0) == 0
    assert bandeja_ids() == ["s-waverly"]


def test_compuerta_del_pool_igual_que_hoy(fase1_sin_red, monkeypatch, capsys):
    """PoolGateRed no es una falla: la semilla vuelve a la bandeja con su motivo y fase1 sale como hoy (exit 0)."""
    fase1, tr, bandeja_ids = fase1_sin_red
    from researcher_steps import pool_gate as pg

    def rojo(seed, titles):
        raise pg.PoolGateRed({"color": "rojo", "motivos": ["no hay con qué contar"]})
    monkeypatch.setattr(tr, "_research_seed_deep", rojo)
    rc = fase1.run_latido_a(video_type="long", skip_niche=True, no_chain=True)
    out = capsys.readouterr().out
    assert (rc or 0) == 0
    assert "Compuerta del pool" in out and "El research falló" not in out
    assert bandeja_ids() == ["s-waverly"]


def test_run_pipeline_research_propaga_la_falla(monkeypatch, capsys):
    """`run_pipeline --research` con fase1 exit 1 → exit 1 y «fase1: el research falló» (el form muestra «✗ pipeline
    terminó (código 1)», qa_form.html)."""
    monkeypatch.setattr(rp, "_chequeo_dependencias", lambda: None)
    monkeypatch.setattr(rp, "_run", lambda cmd: 1 if cmd[0] == "fase1.py" else pytest.fail(f"no debía seguir: {cmd}"))
    monkeypatch.setattr(sys, "argv", ["run_pipeline.py", "--research", "--video-type", "long", "--batch"])
    assert rp.main() == 1
    assert "fase1: el research falló (exit 1)" in capsys.readouterr().out
