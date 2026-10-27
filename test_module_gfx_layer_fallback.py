"""test_module_gfx_layer_fallback.py — F1 capa gráfica: fallback a base_clip (D2).
npx/node ausente · lint con errores · render timeout → devuelve base_clip y NO lanza.
subprocess mockeado (no corre Chrome ni FFmpeg real salvo lo que se mockea).
Correr: python -m pytest test_module_gfx_layer_fallback.py -q
"""
import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

import script_engine.gfx_layer as gl

PLAN = {"chapter_number": 2, "title_card": {"kicker": "CAPÍTULO 2", "title": "T"}, "callouts": [],
        "count_up": None, "archive_clipping": None, "evidence_zoom": None, "punch_in": []}


@pytest.fixture
def env(tmp_path, monkeypatch):
    base = tmp_path / "ch02_flux_visual.mp4"
    base.write_bytes(b"fake")
    chplan = SimpleNamespace(chapter_id="ch02", engine="flux", narration="", timestamps_path=None,
                             narration_anchors=None, supplemental_paths=None)
    # pasos que no interesan: re-encode, duración, contexto, grade
    monkeypatch.setattr(gl, "_reencode", lambda src, out, fps: (out.parent.mkdir(parents=True, exist_ok=True), out.write_bytes(b"v")))
    monkeypatch.setattr(gl, "_ffprobe_duration", lambda p: 10.0)
    monkeypatch.setattr(gl, "_doctor_once", lambda log: None)
    import script_engine.gfx_director as gd
    monkeypatch.setattr(gd, "load_chapter_context", lambda vid, p: {"script_chapter": {}, "sources": {}, "chapter_number": 2, "facts": [], "skeleton": {}})
    monkeypatch.setattr(gl, "write_project", lambda *a, **k: None)
    return base, chplan, tmp_path


def _call(base, chplan, work):
    return gl.apply_gfx(base, chplan, "vid", work, width=2560, height=1440, fps=30, gfx_plan_override=PLAN)


def test_sin_node_devuelve_base(env, monkeypatch):
    base, chplan, work = env
    monkeypatch.setattr(gl, "resolve_node", lambda: None)
    assert _call(base, chplan, work) == base
    assert "FALLBACK" in (work / "gfx_ch02.log").read_text(encoding="utf-8")


def test_lint_con_errores_devuelve_base(env, monkeypatch):
    base, chplan, work = env
    def fake_hf(args, **k):
        if args[0] == "lint":
            return subprocess.CompletedProcess(args, 0, json.dumps({"errorCount": 2, "findings": [
                {"severity": "error", "code": "missing_local_asset"}]}), "")
        raise AssertionError("no debería renderizar si lint falla")
    monkeypatch.setattr(gl, "_hf", fake_hf)
    assert _call(base, chplan, work) == base
    log = (work / "gfx_ch02.log").read_text(encoding="utf-8")
    assert "lint con 2 error" in log and "missing_local_asset" in log


def test_render_timeout_devuelve_base(env, monkeypatch):
    base, chplan, work = env
    def fake_hf(args, **k):
        if args[0] == "lint":
            return subprocess.CompletedProcess(args, 0, json.dumps({"errorCount": 0, "warningCount": 3}), "")
        raise subprocess.TimeoutExpired(cmd=args, timeout=k.get("timeout", 900))
    monkeypatch.setattr(gl, "_hf", fake_hf)
    assert _call(base, chplan, work) == base
    assert "excedió timeout" in (work / "gfx_ch02.log").read_text(encoding="utf-8")


def test_render_ok_devuelve_gfx(env, monkeypatch):
    base, chplan, work = env
    def fake_hf(args, **k):
        if args[0] == "lint":
            return subprocess.CompletedProcess(args, 0, json.dumps({"errorCount": 0, "warningCount": 0}), "")
        out = Path(args[args.index("-o") + 1]); out.parent.mkdir(parents=True, exist_ok=True); out.write_bytes(b"mp4")
        return subprocess.CompletedProcess(args, 0, "", "")
    monkeypatch.setattr(gl, "_hf", fake_hf)
    out = _call(base, chplan, work)
    assert out == work / "ch02_gfx.mp4" and out.exists()


def test_reuse_no_re_renderiza(env, monkeypatch):
    base, chplan, work = env
    (work / "ch02_gfx.mp4").write_bytes(b"ya")
    (work / "gfx_ch02.log").write_text("render original\n", encoding="utf-8")
    monkeypatch.setattr(gl, "_hf", lambda *a, **k: (_ for _ in ()).throw(AssertionError("no debía correr")))
    assert gl.apply_gfx(base, chplan, "vid", work, width=2560, height=1440, fps=30, reuse=True) == work / "ch02_gfx.mp4"
    log = (work / "gfx_ch02.log").read_text(encoding="utf-8")
    assert "render original" in log and "reuse" in log      # el reuse agrega, no pisa


def test_excepcion_inesperada_devuelve_base(env, monkeypatch):
    base, chplan, work = env
    monkeypatch.setattr(gl, "_reencode", lambda *a: (_ for _ in ()).throw(OSError("disco lleno")))
    assert _call(base, chplan, work) == base


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
