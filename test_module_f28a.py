"""
test_module_f28a.py — F28 §A: el composition_plan de la paleta (m07.plan_composicion / fijar_plan) con las reglas
fijas sin depender del modelo, y la llamada al endpoint detailed con composition_plan. Sin red.
"""
from __future__ import annotations

from types import SimpleNamespace

import pytest

import music_config as mc
from script_engine import m07_music_director as m7


def _plan_modelo():
    return {"positive_global_styles": ["cinematic documentary underscore", "C minor", "slow fade-in", "60 BPM"],
            "negative_global_styles": ["drums"],
            "sections": [
                {"section_name": "a", "duration_ms": 50000, "positive_local_styles": ["low cello drone", "sub-bass"],
                 "negative_local_styles": ["melody"], "lines": []},
                {"section_name": "b", "duration_ms": 70000, "positive_local_styles": ["denser strings"],
                 "negative_local_styles": [], "lines": ["la"]},
                {"section_name": "c", "duration_ms": 61000, "positive_local_styles": ["thin pad", "fading out"],
                 "negative_local_styles": [], "lines": []}]}


def test_reglas_fijas_del_plan():
    p = m7.fijar_plan(_plan_modelo(), 180_000)
    assert p["positive_global_styles"][0] == "D minor"
    assert not any("C minor" in s or "fade" in s.lower() for s in p["positive_global_styles"])
    assert p["negative_global_styles"] == list(mc.NEGATIVE_GLOBAL_STYLES)[:50]
    secs = p["sections"]
    assert sum(s["duration_ms"] for s in secs) == 180_000 and all(3000 <= s["duration_ms"] <= 120_000 for s in secs)
    assert secs[-1]["positive_local_styles"] == secs[0]["positive_local_styles"] == ["low cello drone", "sub-bass"]
    assert "fade-in" in secs[0]["negative_local_styles"] and "fade-out" in secs[-1]["negative_local_styles"]
    assert all(s["lines"] == [] for s in secs)


def test_secciones_fuera_de_rango():
    malo = _plan_modelo()
    malo["sections"] = malo["sections"][:2]
    with pytest.raises(m7.MusicDirectorError):
        m7.fijar_plan(malo, 180_000)


def test_plan_composicion_lleva_el_sonido_del_canal():
    vistos = {}

    def call(user, **kw):
        vistos.update(user=user, **kw)
        return _plan_modelo()
    p = m7.plan_composicion("shock", mc.SONIDO_DEL_CANAL, 180_000, call=call)
    assert mc.SONIDO_DEL_CANAL in vistos["user"] and mc.PALETA_INTENTS["shock"] in vistos["user"]
    assert "180000 ms" in vistos["user"] and vistos["system_instruction"] == m7.PLAN_SYSTEM
    assert p["positive_global_styles"][0] == "D minor"
    with pytest.raises(mc.MusicConfigError):
        m7.plan_composicion("resolution", mc.SONIDO_DEL_CANAL, 180_000, call=call)


def test_generar_con_plan_manda_composition_plan_sin_prompt(monkeypatch):
    vistos = {}
    monkeypatch.setattr(m7, "_parse_multipart_response", lambda ct, c: (b"MP3", {"song_metadata": {}}))

    def post(url, **kw):
        vistos.update(url=url, **kw)
        return SimpleNamespace(status_code=200, headers={"Content-Type": "multipart/mixed", "song-id": "x"},
                               content=b"", text="")
    mp3, meta, hdr = m7.generar_con_plan({"sections": []}, post=post)
    assert mp3 == b"MP3" and hdr["song-id"] == "x"
    assert vistos["url"].endswith("/v1/music/detailed")
    assert "composition_plan" in vistos["json"] and "prompt" not in vistos["json"]
    assert "music_length_ms" not in vistos["json"]


def test_sonido_del_canal_literal():
    assert mc.SONIDO_DEL_CANAL.startswith("Misterios Sepultados suena **grave, quieto y paciente**.")
    assert "Re menor" in mc.SONIDO_DEL_CANAL and mc.SONIDO_DEL_CANAL.endswith("con narrador único.")
    assert set(mc.PALETA_INTENTS) == {"hook", "setup", "rising_tension", "shock", "consequences", "outro"}
