"""
test_module_f28b.py — F28 §B: poda de la paleta sobre medidas sintéticas; mapa de intensidad por cap sobre una escaleta de
prueba (reglas fijas); envolvente aplicada = ganancias esperadas; fase2b: loop con acrossfade y envolvente en la pieza;
m07: con la paleta, el matcher elige entre las dos y nunca genera. Sin red.
"""
from __future__ import annotations

import sys
import wave
from pathlib import Path

import numpy as np
import pytest

from script_engine import music_intensity as mi

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "lab" / "hyperframes" / "f28" / "a"))


# ── poda (parte A) sobre medidas sintéticas ──

def _m(**kw):
    base = {"pulso": 0.1, "tonalidad_ok": True, "tonalidad": "D minor", "LRA_lu": 5.0, "banda_voz": 0.01,
            "fade": False, "rms_inicio_db": 0.0, "rms_final_db": 0.0}
    return {**base, **kw}


def test_poda_sobre_medidas_sinteticas():
    import f28a_paleta as fp
    assert fp.poda(_m()) == []
    assert fp.poda(_m(pulso=0.36)) == ["pulso 0.36"]
    assert fp.poda(_m(tonalidad_ok=False, tonalidad="G# minor")) == ["tonalidad G# minor"]
    assert fp.poda(_m(LRA_lu=12.5)) == ["LRA 12.5"]
    assert fp.poda(_m(banda_voz=0.31)) == ["banda-voz 0.31"]
    assert fp.poda(_m(fade=True, rms_inicio_db=-9.0, rms_final_db=-30.0))[0].startswith("fade en la costura")
    assert len(fp.poda(_m(pulso=0.9, LRA_lu=20, fade=True))) == 3


# ── mapa de intensidad ──

BEATS = [{"n": "1", "cap": "1", "funcion": "gancho", "intensidad": "4", "dato_central": "T1", "datos_apoyo": []},
         {"n": "2", "cap": "2", "funcion": "planteo", "intensidad": "1", "dato_central": "D1", "datos_apoyo": []},
         {"n": "3", "cap": "2", "funcion": "escalada", "intensidad": "3", "dato_central": "D2",
          "datos_apoyo": ["Q1"]},
         {"n": "4", "cap": "3", "funcion": "pico", "intensidad": "5", "dato_central": "T2",
          "datos_apoyo": ["Q2", "Q3"]}]


def _par(cap, beat, n_pal, cita=None):
    txt = " ".join(f"p{cap}_{beat}_{i}" for i in range(n_pal))
    if cita:
        txt += f" dijo «{cita}» y siguió"
    return {"cap": cap, "beat": beat, "texto": txt}


def _ts(n, dt=0.5):
    return [{"word": f"w{i}", "start": i * dt, "end": i * dt + dt * 0.8} for i in range(n)]


def test_mapa_cap_2_silencio_antes_del_pico_del_cap_y_cita_de_testigo():
    pars = [_par(2, 2, 20), _par(2, 3, 20, cita="la presa se movía todos los días")]
    n = sum(len(p["texto"].split()) for p in pars)
    t = mi.tramos_de_cap(2, BEATS, pars, _ts(n), {"Q1"}, n * 0.5)
    sil = [x for x in t if x["nivel"] == "silencio"]
    assert len(sil) == 2
    assert sil[0]["motivo"].startswith("antes del pico del cap") and sil[0]["t1"] == pytest.approx(10.0)
    assert sil[0]["t1"] - sil[0]["t0"] == pytest.approx(mi.SILENCIO_PREVIO_S)
    assert sil[1]["motivo"] == "cita de testigo (beat 3)"
    assert not [x for x in t if x["nivel"] in ("golpe", "sube")]        # intensidad < 4 y no hay pico de video


def test_mapa_cita_sin_testigo_no_calla():
    pars = [_par(2, 2, 20), _par(2, 3, 20, cita="la presa se movía")]
    n = sum(len(p["texto"].split()) for p in pars)
    t = mi.tramos_de_cap(2, BEATS, pars, _ts(n), set(), n * 0.5)
    assert [x["motivo"] for x in t if x["nivel"] == "silencio"] == ["antes del pico del cap (beat 3)"]


def test_mapa_golpe_solo_en_el_pico_y_el_silencio_no_lo_tapa():
    pars = [_par(3, 4, 3, cita="un trueno de verano"), _par(3, 4, 30, cita="y después la nada")]
    n = sum(len(p["texto"].split()) for p in pars)
    t = mi.tramos_de_cap(3, BEATS, pars, _ts(n), {"Q2"}, n * 0.5)
    golpe = [x for x in t if x["nivel"] == "golpe"]
    assert len(golpe) == 1 and golpe[0]["t0"] == 0.0 and golpe[0]["t1"] == mi.VUELTA_GOLPE_S
    sil = [x for x in t if x["nivel"] == "silencio"]
    assert len(sil) == 1 and sil[0]["t0"] > golpe[0]["t1"] + mi.FADE_SILENCIO_S   # la 1.ª cita pisaba el golpe
    assert not [x for x in t if x["nivel"] == "sube"]                  # el beat de pico no «sube»: golpea


def test_mapa_sube_en_beats_intensos_y_maximo_dos_silencios():
    pars = [_par(1, 1, 10, cita=f"cita {k}") for k in range(4)]
    n = sum(len(p["texto"].split()) for p in pars)
    t = mi.tramos_de_cap(1, BEATS, pars, _ts(n), {"T1"}, n * 0.5)
    assert [x["nivel"] for x in t].count("sube") == 1
    assert [x["nivel"] for x in t].count("silencio") == mi.MAX_SILENCIOS


# ── envolvente ──

def test_ganancias_esperadas():
    tr = [{"nivel": "fondo", "t0": 0, "t1": 60}, {"nivel": "sube", "t0": 10, "t1": 20},
          {"nivel": "golpe", "t0": 30, "t1": 34}, {"nivel": "silencio", "t0": 45, "t1": 48}]
    g = mi.ganancias(tr, 60)
    at = lambda s: g[int(round(s * mi.ENV_HZ))]  # noqa: E731
    assert at(2) == pytest.approx(1.0)
    assert at(15) == pytest.approx(10 ** (3 / 20))
    assert at(30) == pytest.approx(10 ** (5 / 20))
    assert at(32) == pytest.approx(10 ** (2.5 / 20), rel=1e-3)        # vuelve a fondo en 4 s
    assert at(36) == pytest.approx(1.0)
    assert at(46) == 0.0 and at(43.5) == pytest.approx(1.0) and at(44.25) == pytest.approx(0.5, abs=0.01)
    assert at(49.5) == pytest.approx(1.0)


def test_aplicar_a_wav(tmp_path):
    sr = 1000
    x = np.full((10 * sr, 2), 10000, dtype=np.int16)
    p = tmp_path / "m.wav"
    with wave.open(str(p), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(x.tobytes())
    mi.aplicar_a_wav(p, [{"nivel": "golpe", "t0": 0, "t1": 4}, {"nivel": "silencio", "t0": 7, "t1": 8}])
    with wave.open(str(p), "rb") as w:
        y = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).reshape(-1, 2)
    assert y[0, 0] == round(10000 * 10 ** (5 / 20))
    assert y[5 * sr, 0] == 10000 and y[int(7.5 * sr), 0] == 0


# ── fase2b ──

def test_fase2b_loop_con_crossfade_y_envolvente(monkeypatch, tmp_path):
    import fase2b
    cmds, env = [], []
    monkeypatch.setattr(fase2b, "_get_duration", lambda p: 160.0)
    monkeypatch.setattr(fase2b, "_run_cmd", lambda cmd, timeout=0: cmds.append(cmd) or
                        type("R", (), {"returncode": 0, "stderr": ""})())
    monkeypatch.setattr(mi, "aplicar_a_wav", lambda p, tr: env.append(tr))
    tr = Path("x.mp3")
    fase2b._build_music_piece_for_chapter(tr, 400.0, tmp_path / "a.wav", piece_volume=0.2, loop_crossfade_sec=3.0,
                                          envolvente=[{"nivel": "golpe", "t0": 0, "t1": 4}])
    c = cmds[-1]
    assert c.count("-i") == 3 and "-stream_loop" not in c                 # 160 + 157 + 157 ≥ 400
    fc = c[c.index("-filter_complex") + 1]
    assert fc.count("acrossfade=d=3.0") == 2 and "volume=0.2" in fc and c[c.index("-t") + 1] == "400.000"
    assert env == [[{"nivel": "golpe", "t0": 0, "t1": 4}]]
    # sin loop_crossfade: la ruta de siempre (-stream_loop), sin envolvente
    fase2b._build_music_piece_for_chapter(tr, 400.0, tmp_path / "b.wav")
    assert "-stream_loop" in cmds[-1] and len(env) == 1
    # pista más larga que el cap: sin loop aunque tenga crossfade
    fase2b._build_music_piece_for_chapter(tr, 100.0, tmp_path / "c.wav", loop_crossfade_sec=3.0)
    assert "-filter_complex" not in cmds[-1]


# ── m07: paleta ──

def test_m07_elige_entre_las_dos_de_la_paleta_y_no_genera(monkeypatch, tmp_path):
    from script_engine import m07_music_director as m7
    lib = [{"track_id": "shock_f28_a", "intent_origin": "shock", "fits_intents": ["shock"], "paleta": "f28",
            "compatible_profiles": ["P"]},
           {"track_id": "shock_f28_b", "intent_origin": "shock", "fits_intents": ["shock"], "paleta": "f28",
            "compatible_profiles": ["P"]}]
    vistos = []
    monkeypatch.setattr(m7, "validate_music_config", lambda: None)
    monkeypatch.setattr(m7, "_load_library", lambda: lib)
    monkeypatch.setattr(m7, "_persist_music_map", lambda tid, mm: None)
    monkeypatch.setattr(m7, "_generate_new_track_with_gate", lambda **k: pytest.fail("no se genera"))

    def matcher(intent, anchor, profile, candidates, umbral=80):
        vistos.append((sorted(c["track_id"] for c in candidates), umbral))
        return None if len(vistos) == 1 else {"winner": "shock_f28_b", "match_score": 40, "reasoning": "x"}
    monkeypatch.setattr(m7, "_match_intent_to_track", matcher)
    sm = {"profile": "P", "chapters": [{"id": "ch01", "narrative_intent": "shock", "text": "a"},
                                       {"id": "ch02", "narrative_intent": "shock", "text": "b"}]}
    mm = m7.generate_music_map("t", sm, interactive=False)
    assert vistos == [(["shock_f28_a", "shock_f28_b"], 0)] * 2
    assert mm["tracks_by_chapter"]["ch01"]["track_id"] == "shock_f28_a"          # el matcher no eligió → la «a»
    assert mm["tracks_by_chapter"]["ch02"]["track_id"] == "shock_f28_b"          # score 40 < 80 igual vale
    assert all(t["match_source"] == "reused" for t in mm["tracks_by_chapter"].values())
