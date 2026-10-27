"""F39 §A (fase1_5): de la semilla al papel en producción, con llamadas falsas (sin red, sin data/).

- A.3: `--semilla <archivo> --topic <id>` investiga la semilla en ese topic (topic_researcher.investigar_semilla), con
  respaldo de topics_db, y no pisa un topic existente;
- A.1: compuerta del pool → ficha si falta (ficha_caso.run, paso «ficha» en 01_v3_costos) → escaleta; compuerta roja =
  PARADA sin pagar la ficha; ficha v2 existente = no se regenera;
- A.4: después de m01b, PARADA del papel salvo `--aprobar-papel` vigente (md5); un papel cambiado queda sin aprobar; sin
  papel no hay nada que aprobar; al reanudar (--from audio) mira lo mismo.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import fase1_5 as f15  # noqa: E402

TID = "t-f39"
SEMILLA = {"seed_id": "s-1", "seed_title": "Un desastre de prueba", "discovery_mode": "x"}


class Explota(AssertionError):
    pass


@pytest.fixture
def env(tmp_path, monkeypatch):
    steps, db = tmp_path / "steps", tmp_path / "topics_db.json"
    steps.mkdir()
    db.write_text(json.dumps({"topics": [{"id": "otro"}]}), encoding="utf-8")
    monkeypatch.setattr(f15, "STEPS_DIR", steps)
    monkeypatch.setattr(f15, "TOPICS_DB", db)
    monkeypatch.setattr(f15, "DATA_DIR", tmp_path)
    pasos: list[str] = []

    import topic_researcher as tr

    def investigar(seed, topic_id):
        pasos.append("research")
        (steps / topic_id).mkdir(parents=True, exist_ok=True)
        topic = {"id": topic_id, "seed_id": seed["seed_id"], "seed_title": seed["seed_title"], "video_title": "VT",
                 "evidence_pool": {"datos": [], "_research_v3": True}, "status": "researched"}
        d = json.loads(db.read_text(encoding="utf-8"))
        d["topics"].append(topic)
        db.write_text(json.dumps(d), encoding="utf-8")
        return topic
    monkeypatch.setattr(tr, "investigar_semilla", investigar)

    def topic_por_id(topic_id):
        return next(t for t in json.loads(db.read_text(encoding="utf-8"))["topics"] if t["id"] == topic_id)
    monkeypatch.setattr(f15, "_load_topic_by_id", topic_por_id)
    monkeypatch.setattr(f15, "cargar_perfil", lambda tid: False)

    from script_engine import m01a_escaleta as me
    monkeypatch.setattr(me, "pool_gate_profile", lambda topic, pool, **k: pasos.append("compuerta") or {"color": "verde"})
    monkeypatch.setattr(me, "_frozen_is_escaleta", lambda topic: False)

    def escaleta(topic, **k):
        pasos.append("escaleta")
        (steps / topic["id"] / "01a_escaleta.json").write_text("{}", encoding="utf-8")
        return {}
    monkeypatch.setattr(me, "generate_escaleta", escaleta)

    from researcher_steps import ficha_caso as fc

    def ficha_run(topic_id, *, steps_dir, title, tag, **k):
        pasos.append(f"ficha «{title}»")
        (steps_dir / topic_id / "ficha_caso.json").write_text(json.dumps({"historia": {}, "prompt_version": "x"}),
                                                              encoding="utf-8")
        return {"meta": {"conteos": {}, "sacados": 0}}
    monkeypatch.setattr(fc, "run", ficha_run)

    def guion_v4(topic_id, **k):
        pasos.append("guion → caps → papel")
        d = steps / topic_id
        (d / "01e_pantalla.json").write_text(json.dumps({"topic_id": topic_id, "beats": []}), encoding="utf-8")
        (d / "01e_pantalla.md").write_text("# papel", encoding="utf-8")
        return {"particion": {"skeleton": {}, "narration": {}}}
    monkeypatch.setattr(f15, "run_guion_v4", guion_v4)
    monkeypatch.setattr(f15, "_topic_v3", lambda tid: topic_por_id(tid))

    def nada(*a, **k):
        raise Explota("después de m01b no corre nada sin el papel aprobado")
    monkeypatch.setattr(f15.m02_5_normalizer_gate, "gate_normalizer_for_topic", nada)
    monkeypatch.setattr(f15, "_build_audio_script", nada)
    monkeypatch.setattr(f15.audio_manager, "generate_audio", nada, raising=False)
    sem = tmp_path / "semilla.json"
    sem.write_text(json.dumps(SEMILLA, ensure_ascii=False), encoding="utf-8")
    return {"steps": steps, "db": db, "pasos": pasos, "sem": sem, "tmp": tmp_path}


def _cadena(env, capsys):
    f15.research_de_semilla(env["sem"], TID)
    r = f15.process_topic(TID, v3=True, guion="v4", gate_interactive=False, music_gate_interactive=False)
    return r, capsys.readouterr().out


def test_a3_de_la_semilla_al_papel_en_orden_y_para_en_el_papel(env, capsys):
    r, out = _cadena(env, capsys)
    with capsys.disabled():                       # A.5 (b): con `pytest -s` la salida queda a la vista
        print("\n── pasos:", " → ".join(env["pasos"]), "\n" + out)
    assert env["pasos"] ==["research", "compuerta", "ficha «Un desastre de prueba»", "escaleta",
                            "guion → caps → papel"]
    assert r["status"] == "PARADA" and r["parada"] == "papel" and r["steps_completed"] == ["m01a", "m01b"]
    assert "PARADA del papel: el papel no está aprobado" in out
    assert f"--topic {TID} --aprobar-papel" in out and "01e_pantalla.md" in out
    assert (env["tmp"] / f"topics_db.pre_{TID}.json").exists()                      # respaldo antes de registrar
    costos = json.loads((env["steps"] / TID / "01_v3_costos.json").read_text(encoding="utf-8"))["_corridas"]
    assert [c["paso"] for c in costos] == ["research", "ficha", "escaleta"]          # el guion es falso: sin costo


def test_a3_no_pisa_un_topic_existente(env):
    (env["steps"] / TID).mkdir()
    with pytest.raises(f15.Parada, match="ya existe"):
        f15.research_de_semilla(env["sem"], TID)
    (env["steps"] / TID).rmdir()
    with pytest.raises(f15.Parada, match="ya está en topics_db"):
        f15.research_de_semilla(env["sem"], "otro")
    assert env["pasos"] == []


def test_a3_compuerta_roja_en_el_research_es_parada(env, monkeypatch):
    import topic_researcher as tr
    from researcher_steps.pool_gate import PoolGateRed

    def rojo(seed, topic_id):
        raise PoolGateRed({"color": "rojo", "motivos": ["pocas fuentes"], "metricas": {}})
    monkeypatch.setattr(tr, "investigar_semilla", rojo)
    with pytest.raises(f15.Parada, match="ROJA: pocas fuentes"):
        f15.research_de_semilla(env["sem"], TID)


def test_a1_compuerta_roja_no_paga_la_ficha(env, monkeypatch, capsys):
    from script_engine import m01a_escaleta as me
    from researcher_steps.pool_gate import PoolGateRed

    def rojo(topic, pool, **k):
        raise PoolGateRed({"color": "rojo", "motivos": ["sin fecha"], "metricas": {}})
    monkeypatch.setattr(me, "pool_gate_profile", rojo)
    f15.research_de_semilla(env["sem"], TID)
    r = f15.process_topic(TID, v3=True, guion="v4", gate_interactive=False, music_gate_interactive=False)
    assert r["status"] == "PARADA" and "ROJA: sin fecha" in r["motivo"]
    assert not any(p.startswith("ficha") for p in env["pasos"])


def test_a1_ficha_v2_existente_no_se_regenera(env, capsys):
    f15.research_de_semilla(env["sem"], TID)
    (env["steps"] / TID / "ficha_caso.json").write_text(json.dumps({"historia": {}, "prompt_version": "f23-1"}),
                                                        encoding="utf-8")
    f15.process_topic(TID, v3=True, guion="v4", gate_interactive=False, music_gate_interactive=False)
    assert not any(p.startswith("ficha") for p in env["pasos"])
    assert "ya hay ficha v2 (f23-1): se usa" in capsys.readouterr().out


def test_a1_sin_seed_title_no_se_inventa(env, monkeypatch):
    topic = {"id": TID, "seed_id": "no-esta"}
    (env["steps"] / TID).mkdir()
    with pytest.raises(f15.Parada, match="sin seed_title"):
        f15.asegurar_ficha(TID, topic, [])


def test_a4_aprobar_papel_y_md5(env, capsys, monkeypatch):
    _cadena(env, capsys)
    ap = f15.aprobar_papel(TID, "Omar 2026-10-27")
    assert ap["por"] == "Omar" and ap["fecha"] == "2026-10-27"
    ok, motivo = f15.estado_papel(TID)
    assert ok and "aprobado por Omar" in motivo
    # un papel cambiado después de aprobar queda sin aprobar
    f = env["steps"] / TID / "01e_pantalla.json"
    p = json.loads(f.read_text(encoding="utf-8"))
    p["beats"] = [{"cap": "ch01"}]
    f.write_text(json.dumps(p), encoding="utf-8")
    ok, motivo = f15.estado_papel(TID)
    assert not ok and "cambió después de la aprobación" in motivo


def test_a4_reanudar_despues_de_m01b_mira_el_papel(env, capsys):
    _cadena(env, capsys)
    r = f15.process_topic(TID, from_step="audio", v3=True, guion="v4", gate_interactive=False,
                          music_gate_interactive=False)
    assert r["status"] == "PARADA" and r["parada"] == "papel"


def test_a4_sin_papel_no_hay_nada_que_aprobar(env):
    (env["steps"] / TID).mkdir()
    ok, motivo = f15.estado_papel(TID)
    assert not ok and "no hay nada que aprobar" in motivo
    with pytest.raises(f15.Parada, match="no hay papel"):
        f15.aprobar_papel(TID, "Omar 2026-10-27")


def test_a4_papel_aprobado_deja_seguir(env, capsys):
    _cadena(env, capsys)
    f15.aprobar_papel(TID, "Omar 2026-10-27")
    r = f15.process_topic(TID, from_step="normalizer_gate", v3=True, guion="v4", gate_interactive=False,
                          music_gate_interactive=False)
    out = capsys.readouterr().out
    assert "[papel] papel aprobado por Omar (2026-10-27)" in out        # pasó la compuerta del papel …
    assert r["status"] == "FAIL" and r["failed_step"] == "normalizer_gate"   # … y siguió al paso siguiente (sin datos)


def test_cli_help_tiene_los_flags_nuevos(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["fase1_5.py", "--help"])
    with pytest.raises(SystemExit):
        f15.main()
    out = capsys.readouterr().out
    assert "--semilla" in out and "--aprobar-papel" in out


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
