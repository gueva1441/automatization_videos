"""F7d (HANDOFF_F7 §9.2): compuerta del pool (verde / amarillo / rojo) antes de la escaleta, POOL_GATE.md, y research v3
como default de topic_researcher para seeds nuevos (RESEARCH_V3=0 → camino viejo). Sin red ni LLM."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from researcher_steps import pool_gate as pg

ROOT = Path(__file__).resolve().parent


def _pool(datos: int, citas_ver: int, elegibles: int, eventos: int) -> dict:
    return {"_research_v3": {"documentos": []},
            "datos": [{"id": f"D{i:02d}", "texto": f"dato {i}"} for i in range(datos)],
            "citas": [{"id": f"Q{i:02d}", "texto": "una cita de testigo", "verificacion": {"estado": "verificada"}}
                      for i in range(citas_ver)] + [{"id": "Q99", "texto": "x", "verificacion": {"estado": "sin_verificar"}}],
            "personajes": [{"id": f"P{i:02d}", "nombre": f"Ana Paz{i}", "elegible_humano": i < elegibles}
                           for i in range(max(elegibles, 1) + 1)],
            "cronologia": [{"id": f"T{i:02d}", "fecha": f"2005-08-{i % 28 + 1:02d}", "evento": "e"} for i in range(eventos)]
                          + [{"id": "T99", "fecha": "2005-09", "evento": "sin día"}],
            "lugares": []}


GREEN = _pool(160, 9, 2, 12)
YELLOW = _pool(90, 5, 1, 6)          # todo ≥ la mitad (75, 4, 1, 5), algo por debajo del verde
RED = _pool(200, 2, 0, 3)            # sin testigos, sin humano, sin cronología


def test_three_colors():
    assert pg.evaluate(GREEN)["color"] == pg.GREEN and pg.evaluate(GREEN)["faltan"] == []
    y = pg.evaluate(YELLOW)
    assert y["color"] == pg.YELLOW and y["target_words"] == 1200 and y["max_beats"] == 8
    assert {f["metrica"] for f in y["faltan"]} == {"datos", "citas_verificadas", "elegibles_humano", "eventos_con_fecha"}
    r = pg.evaluate(RED)
    assert r["color"] == pg.RED
    assert set(r["motivos"]) == {pg.CHECKS["citas_verificadas"][1], pg.CHECKS["elegibles_humano"][1],
                                 pg.CHECKS["eventos_con_fecha"][1]}
    assert r["metricas"]["eventos_con_fecha"] == 3            # «2005-09» no es una fecha completa


def test_orleans_pool_is_green():
    pool = json.loads((ROOT / "lab/hyperframes/f7/00_pool_v3.json").read_text(encoding="utf-8"))
    g = pg.evaluate(pool)
    assert g["color"] == pg.GREEN, g


def test_report_and_red_raises(tmp_path):
    with pytest.raises(pg.PoolGateRed) as e:
        pg.check(RED, "t-red", tmp_path)
    assert "sin testigos" in str(e.value)
    md = (tmp_path / "POOL_GATE.md").read_text(encoding="utf-8")
    assert "ROJO" in md and "vuelve al inbox" in md
    g = pg.check(YELLOW, "t-y", tmp_path / "y")
    assert "AMARILLO" in (tmp_path / "y" / "POOL_GATE.md").read_text(encoding="utf-8") and g["color"] == pg.YELLOW


def test_thresholds_come_from_video_length(monkeypatch):
    from script_engine import video_length as vl
    monkeypatch.setitem(vl.DEFAULTS, "gate_datos", 1000)
    monkeypatch.setattr(vl, "get", lambda k: vl.DEFAULTS[k])
    assert pg.evaluate(GREEN)["color"] == pg.RED                 # 160 < la mitad de 1000


def test_escaleta_gate_red_spends_nothing_yellow_shortens(tmp_path, monkeypatch):
    from script_engine import m01a_escaleta as me
    monkeypatch.setattr(me, "STEPS_DIR", tmp_path)

    def no_call(*a, **k):
        raise AssertionError("la escaleta no debería llamar al LLM con el pool en rojo")
    with pytest.raises(pg.PoolGateRed):
        me.generate_escaleta({"id": "t-red", "evidence_pool": RED}, call=no_call)
    assert (tmp_path / "t-red" / "POOL_GATE.md").exists()
    t = {"id": "t-y", "evidence_pool": YELLOW}
    g = me.pool_gate_profile(t, YELLOW)
    assert g["color"] == pg.YELLOW
    assert abs(sum(t["_largo"]["cap_words"].values()) - 1200) <= 7 and t["_largo"]["max_beats"] == 8
    assert "Entre 7 y 8 beats" in me.build_prompt(t, YELLOW)
    old = {k: v for k, v in GREEN.items() if k != "_research_v3"}      # pool viejo: sin compuerta
    assert me.pool_gate_profile({"id": "t-old"}, old) is None
    assert f"Entre 7 y {me.MAX_BEATS} beats" in me.build_prompt({"id": "t-old"}, old)       # F8b: tope 14


# ── RESEARCH_V3 por defecto en topic_researcher ───────────────────────────────

def _stub_steps(monkeypatch, tr, calls):
    monkeypatch.setattr(tr, "_save_step_output", lambda *a, **k: None)
    monkeypatch.setattr(tr, "time", type("T", (), {"sleep": staticmethod(lambda s: None)}))
    monkeypatch.setattr(tr, "extract_facts_and_sources",
                        lambda blocks, *a, **k: calls.append(("4a", a, k)) or {"verified_facts": [], "sources": [],
                                                                               "evidence_pool": {"viejo": True}})
    monkeypatch.setattr(tr, "extract_canonical", lambda *a, **k: {"canonical_subject_description": "c"})
    monkeypatch.setattr(tr, "extract_meta", lambda *a, **k: {"video_title": "T", "search_keyword": "k"})
    monkeypatch.setattr(tr, "extract_research_summary", lambda *a, **k: {"research_summary": "r"})
    monkeypatch.setattr(tr, "extract_visual_canon", lambda *a, **k: {"era_visual_canon": {"primary_decade": "2000s"}})


def test_research_v3_is_default_and_zero_keeps_old_path(monkeypatch):
    import topic_researcher as tr
    from researcher_steps import research_v3 as r3
    calls: list = []
    _stub_steps(monkeypatch, tr, calls)
    monkeypatch.setattr(tr, "_gather_angle_blocks", lambda seed: calls.append("angulos") or {"tecnico": "b"})
    monkeypatch.setattr(r3, "run_seed", lambda seed, tid, d, **k: (calls.append("v3") or ({"v3": True}, {"tecnico": "p"}, None)))
    seed = {"seed_title": "OPP", "seed_id": "s1"}
    monkeypatch.delenv("RESEARCH_V3", raising=False)
    d = tr._research_seed_deep(seed, [])
    assert calls[0] == "v3" and d["evidence_pool"] == {"v3": True} and d["research_version"] == 3
    assert calls[1] == ("4a", (), {"with_pool": False})
    calls.clear()
    monkeypatch.setenv("RESEARCH_V3", "0")
    d = tr._research_seed_deep(seed, [])
    assert calls == ["angulos", ("4a", (), {})] and d["evidence_pool"] == {"viejo": True} and "research_version" not in d


def test_red_seed_stays_in_inbox_with_reason(monkeypatch, tmp_path):
    import topic_researcher as tr
    inbox = tmp_path / "seeds.json"
    inbox.write_text(json.dumps({"seeds": [{"seed_id": "s1", "seed_title": "OPP", "discovery_mode": "x"}]}),
                     encoding="utf-8")
    monkeypatch.setattr(tr, "SEEDS_FILE", inbox)
    monkeypatch.setattr(tr, "_load_topics_db", lambda: {"topics": []})
    monkeypatch.setattr(tr, "_save_topics_db", lambda db: None)

    def red(seed, titles):
        raise pg.PoolGateRed(pg.evaluate(RED))
    monkeypatch.setattr(tr, "_research_seed_deep", red)
    out = tr.research_topics(video_type="long")
    seeds = json.loads(inbox.read_text(encoding="utf-8"))["seeds"]
    assert out == [] and len(seeds) == 1
    assert seeds[0]["pool_gate"]["color"] == "rojo" and "sin testigos" in " ".join(seeds[0]["pool_gate"]["motivos"])


def test_pool_to_blocks_feeds_4a_4e():
    from researcher_steps.research_v3 import pool_to_blocks
    pool = json.loads((ROOT / "lab/hyperframes/f7/00_pool_v3.json").read_text(encoding="utf-8"))
    b = pool_to_blocks(pool)
    assert set(b) == {"tecnico", "humano", "misterio", "visual"}
    assert "[FUENTES CONSULTADAS]" in b["tecnico"] and "[TESTIMONIOS]" in b["humano"] and "[LUGARES]" in b["visual"]
