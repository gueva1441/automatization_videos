"""F41 §A (DECISIONES 2026-10-27 20:59): una sola cadena en fase1_5 y `video_type` desde el research.

- un topic sin evidence_pool v3 → PARADA con su motivo, sin gastar (desde cualquier paso);
- un topic con pool v3 y SIN `guion_version` corre la cadena única (compuerta → ficha → escaleta → guion v4 → papel)
  y para en el papel, con llamadas falsas (como test_module_f39_fase1);
- `--v3` / `--guion` ya no existen; is_v3_topic / is_v4_guion / run_guion_v3 tampoco;
- research_topics / investigar_semilla guardan el `video_type` pedido.
Sintético: sin red, sin data/ (todo a tmp_path).
"""
from __future__ import annotations

import inspect
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import fase1_5 as f15  # noqa: E402
import topic_researcher as tr  # noqa: E402
from test_module_f39_research import SEED, entorno  # noqa: E402,F401  (fixture del research falso)

TID = "t-f41"


class Gasto(AssertionError):
    """Un paso que gasta (o que corre después de la compuerta) se llamó cuando no debía."""


def _explota(nombre):
    def f(*a, **k):
        raise Gasto(f"{nombre} no debía correr")
    return f


@pytest.fixture
def cadena(tmp_path, monkeypatch):
    """La cadena con todos los pasos que gastan cambiados por falsos que anotan en `pasos`."""
    steps = tmp_path / "steps"
    steps.mkdir()
    monkeypatch.setattr(f15, "STEPS_DIR", steps)
    monkeypatch.setattr(f15, "DATA_DIR", tmp_path)
    monkeypatch.setattr(f15, "cargar_perfil", lambda tid: False)
    topics: dict[str, dict] = {}
    monkeypatch.setattr(f15, "_load_topic_by_id", lambda tid: topics[tid])
    pasos: list[str] = []

    from script_engine import m01a_escaleta as me
    monkeypatch.setattr(me, "pool_gate_profile", lambda topic, pool, **k: pasos.append("compuerta") or {"color": "v"})
    monkeypatch.setattr(me, "_frozen_is_escaleta", lambda topic: False)

    def escaleta(topic, **k):
        pasos.append("escaleta")
        (steps / topic["id"] / "01a_escaleta.json").write_text("{}", encoding="utf-8")
        return {}
    monkeypatch.setattr(me, "generate_escaleta", escaleta)

    from researcher_steps import ficha_caso as fc

    def ficha_run(topic_id, *, steps_dir, title, tag, **k):
        pasos.append("ficha")
        (steps_dir / topic_id / "ficha_caso.json").write_text(json.dumps({"historia": {}, "prompt_version": "x"}),
                                                              encoding="utf-8")
        return {"meta": {}}
    monkeypatch.setattr(fc, "run", ficha_run)

    def guion_v4(topic_id, **k):
        pasos.append("guion v4 → caps → papel")
        (steps / topic_id / "01e_pantalla.json").write_text(json.dumps({"topic_id": topic_id}), encoding="utf-8")
        return {"particion": {"skeleton": {}, "narration": {}}}
    monkeypatch.setattr(f15, "run_guion_v4", guion_v4)
    monkeypatch.setattr(f15, "asegurar_canon", lambda tid, topic, log: pasos.append("canon") or topic)   # F50 A

    for nombre in ("gate_normalizer_for_topic",):
        monkeypatch.setattr(f15.m02_5_normalizer_gate, nombre, _explota(nombre))
    monkeypatch.setattr(f15.audio_manager, "process_script", _explota("audio"))
    monkeypatch.setattr(f15.m07_music_director, "generate_music_map", _explota("m07"))
    monkeypatch.setattr(f15, "assign_visual_prompts", _explota("m03"))
    monkeypatch.setattr(f15, "generate_foto_madre_for_topic", _explota("foto madre"))
    monkeypatch.setattr(f15, "assemble_final_script", _explota("assemble"))
    return {"steps": steps, "topics": topics, "pasos": pasos}


def _sin_gasto(monkeypatch):
    """Todo lo que gasta en m01a/m01b explota: la PARADA del pool tiene que llegar antes."""
    monkeypatch.setattr(f15, "run_escaleta_v3", _explota("escaleta"))
    monkeypatch.setattr(f15, "run_guion_v4", _explota("guion v4"))
    monkeypatch.setattr(f15, "asegurar_ficha", _explota("ficha"))
    monkeypatch.setattr(f15, "asegurar_canon", _explota("canon"))
    monkeypatch.setattr(f15, "_step_cost", _explota("_step_cost"))


@pytest.mark.parametrize("pool", [None, {"datos": [{"id": "D01"}]}], ids=["sin_pool", "pool_no_v3"])
@pytest.mark.parametrize("desde", ["m01a", "m01b", "normalizer_gate", "audio", "m03"])
def test_sin_pool_v3_es_parada_sin_gastar(cadena, monkeypatch, pool, desde):
    _sin_gasto(monkeypatch)
    cadena["topics"][TID] = {"id": TID, **({"evidence_pool": pool} if pool else {})}
    r = f15.process_topic(TID, from_step=desde, gate_interactive=False, music_gate_interactive=False)
    assert r["status"] == "PARADA" and r["steps_completed"] == []
    assert "_research_v3" in r["motivo"] and TID in r["motivo"]
    assert ("sin evidence_pool" in r["motivo"]) == (pool is None)
    assert cadena["pasos"] == []
    assert not (cadena["steps"] / TID / "01_v3_costos.json").exists()


def test_sin_pool_v3_por_cli_sale_con_2(cadena, monkeypatch, capsys):
    _sin_gasto(monkeypatch)
    cadena["topics"][TID] = {"id": TID}
    monkeypatch.setattr(sys, "argv", ["fase1_5.py", "--topic", TID, "--batch"])
    with pytest.raises(SystemExit) as e:
        f15.main()
    assert e.value.code == 2                                  # otra PARADA (no la del papel)
    assert "sin evidence_pool" in capsys.readouterr().out


def test_pool_v3_sin_guion_version_corre_la_cadena_unica(cadena, capsys):
    topic = {"id": TID, "seed_title": "Un caso", "evidence_pool": {"datos": [], "_research_v3": True}}
    assert "guion_version" not in topic
    cadena["topics"][TID] = topic
    (cadena["steps"] / TID).mkdir()
    r = f15.process_topic(TID, gate_interactive=False, music_gate_interactive=False)
    assert cadena["pasos"] == ["compuerta", "ficha", "canon", "escaleta", "guion v4 → caps → papel"]
    assert r["status"] == "PARADA" and r["parada"] == "papel" and r["steps_completed"] == ["m01a", "m01b"]
    assert "PARADA del papel" in capsys.readouterr().out
    assert "guion_version" not in topic                       # nadie lo escribe: no elige nada


def test_pool_v3_desde_m01b_va_al_guion_v4(cadena):
    cadena["topics"][TID] = {"id": TID, "evidence_pool": {"datos": [], "_research_v3": True}}
    (cadena["steps"] / TID).mkdir()
    r = f15.process_topic(TID, from_step="m01b", stop_after_step="m01b")
    assert r["status"] == "PASS" and cadena["pasos"] == ["guion v4 → caps → papel"]


def test_la_cadena_vieja_ya_no_existe(monkeypatch, capsys):
    for nombre in ("is_v3_topic", "is_v4_guion", "run_guion_v3", "generate_skeleton", "generate_narration"):
        assert not hasattr(f15, nombre), nombre
    params = inspect.signature(f15.process_topic).parameters
    assert "v3" not in params and "guion" not in params
    monkeypatch.setattr(sys, "argv", ["fase1_5.py", "--help"])
    with pytest.raises(SystemExit):
        f15.main()
    out = capsys.readouterr().out
    assert "--v3" not in out and "--guion " not in out and "--guion\n" not in out
    assert "--modelo" in out and "--aprobar-papel" in out and "--semilla" in out and "--from" in out
    monkeypatch.setattr(sys, "argv", ["fase1_5.py", "--topic", TID, "--v3"])
    with pytest.raises(SystemExit) as e:
        f15.main()
    assert e.value.code == 2                                  # argparse: argumento desconocido


def test_los_modulos_viejos_no_tienen_la_cadena_vieja():
    from script_engine import m01a_escaleta, m01a_skeleton, m01b_guionista, m01b_narrator, m01c_editor, m01d_particion
    assert not hasattr(m01a_skeleton, "generate_skeleton") and not hasattr(m01b_narrator, "generate_narration")
    assert not hasattr(m01b_narrator, "regenerate_caps") and not hasattr(m01b_guionista, "write")
    assert not hasattr(m01c_editor, "edit") and not hasattr(m01d_particion, "regenerate_cap")
    assert not hasattr(m01a_escaleta, "is_v3")
    # lo que queda tiene llamadores vivos
    assert callable(m01b_narrator._validate_narration) and callable(m01a_skeleton.finalize_pool_plan)
    assert callable(m01b_guionista.review) and callable(m01c_editor.lexical_guard)


@pytest.mark.parametrize("vt", ["long", "short"])
def test_research_topics_guarda_el_video_type(entorno, monkeypatch, vt):
    if vt == "short":
        monkeypatch.setattr(tr, "_research_seed_simple", lambda seed, titles: {"video_title": "Corto"})
    out = tr.research_topics(video_type=vt)
    assert [t["video_type"] for t in out] == [vt]
    guardado = json.loads(entorno["db"].read_text(encoding="utf-8"))["topics"]
    assert [t["video_type"] for t in guardado] == [vt]


def test_investigar_semilla_guarda_long(entorno):
    topic = tr.investigar_semilla(SEED, "f41-prueba")
    assert topic["video_type"] == "long"
    guardado = json.loads(entorno["db"].read_text(encoding="utf-8"))["topics"]
    assert guardado[0]["video_type"] == "long"


def test_titulo_de_la_ficha_desde_la_semilla_archivada_por_research_topics(tmp_path, monkeypatch):
    """El topic que sale de research_topics (el camino del form) no guarda seed_title: el título de la ficha sale de
    `seeds_archive.json` → `archived` (donde research_topics archiva la semilla), no solo de `seeds`."""
    monkeypatch.setattr(f15, "DATA_DIR", tmp_path)
    (tmp_path / "seeds_archive.json").write_text(json.dumps({
        "seeds": [{"seed_id": "s-borrada", "seed_title": "Borrada"}],
        "archived": [{"seed_id": "s-form", "seed_title": "Del form", "topic_id": "t"}]}), encoding="utf-8")
    assert f15._titulo_de_semilla({"seed_id": "s-form"}) == "Del form"
    assert f15._titulo_de_semilla({"seed_id": "s-borrada"}) == "Borrada"
    assert f15._titulo_de_semilla({"seed_id": "no-esta"}) is None
    assert f15._titulo_de_semilla({"seed_id": "s-form", "seed_title": "Propio"}) == "Propio"


def test_enrich_sin_video_type_no_lo_inventa():
    seed = {"seed_id": "s", "discovery_mode": "manual"}
    assert "video_type" not in tr._enrich_with_seed_metadata({"video_title": "x"}, seed)
    assert tr._enrich_with_seed_metadata({"video_title": "x"}, seed, video_type="long")["video_type"] == "long"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
