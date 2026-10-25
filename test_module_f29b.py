"""
test_module_f29b.py — F29 §B: la librería de SFX regenerada con ElevenLabs. Mismos 15 nombres y duraciones que la
síntesis de F2 (que queda en `_f2_sintetizados/`); caché por prompt (no llama si nada cambió); el proceso normaliza a
−20 LUFS y no deja mudo un sonido que arranca bajo. Sin red.
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent
SFX = ROOT / "script_engine" / "sfx"


def _mod(p: Path, nombre: str):
    spec = importlib.util.spec_from_file_location(nombre, p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_mismos_nombres_y_duraciones_que_f2():
    nuevo = _mod(SFX / "make_sfx.py", "make_sfx_nuevo")
    viejo = _mod(SFX / "_f2_sintetizados" / "make_sfx_f2.py", "make_sfx_f2")
    assert {k: v[0] for k, v in nuevo._SOUNDS.items()} == {k: v[0] for k, v in viejo._SOUNDS.items()}
    assert len(nuevo._SOUNDS) == 15
    assert {p.stem for p in SFX.glob("*.wav")} == set(nuevo._SOUNDS)
    assert {p.stem for p in (SFX / "_f2_sintetizados").glob("*.wav")} == set(nuevo._SOUNDS)


def test_cache_no_llama_si_nada_cambio(monkeypatch, tmp_path):
    m = _mod(SFX / "make_sfx.py", "make_sfx_cache")
    (tmp_path / "tic.wav").write_bytes(b"x")
    dur, prompt = m._SOUNDS["tic"]
    monkeypatch.setattr(m, "CACHE", tmp_path / "_prompts.json")
    (tmp_path / "_prompts.json").write_text(json.dumps({"tic": {
        "prompt": prompt, "duracion": dur, "modelo": m.MODELO, "prompt_influence": m.PROMPT_INFLUENCE,
        "lufs": -20.0, "pico_db": -1.0}}), encoding="utf-8")
    monkeypatch.setattr(m, "_pedir", lambda *a, **k: pytest.fail("no tenía que llamar"))
    r = m.make_all(tmp_path, only=["tic"])
    assert r[0]["en_cache"] is True
    # si cambia el prompt, llama
    llamados = []
    monkeypatch.setattr(m, "_SOUNDS", {"tic": (dur, prompt + " otro")})
    monkeypatch.setattr(m, "_pedir", lambda p, d: llamados.append(p) or b"")
    monkeypatch.setattr(m, "_procesar", lambda raw, dst, d: {"lufs": -20.0, "pico_db": -1.0})
    m.make_all(tmp_path, only=["tic"])
    assert llamados == [prompt + " otro"]


def test_procesar_normaliza_y_no_vacia_un_sonido_bajo(tmp_path):
    m = _mod(SFX / "make_sfx.py", "make_sfx_proc")
    raw = tmp_path / "bajo.wav"            # un tono de 1 kHz a −53 dBFS: el recorte de silencio a −50 dB lo vaciaría
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "sine=f=1000:d=2", "-af", "volume=-50dB",
                    "-ar", "48000", "-ac", "1", str(raw)], check=True)
    info = m._procesar(raw, tmp_path / "out.wav", 1.5)
    assert info["lufs"] == pytest.approx(-20.0, abs=1.0) and info["pico_db"] <= -0.9
