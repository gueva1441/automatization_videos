"""Tests del laboratorio de identidad (F3 §A): helpers HTTP del servidor, memo de freezes y sesión real de ch02."""
from __future__ import annotations

import json
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest

import gfx_lab_server as lab
from script_engine import gfx_project

VIDEO = lab.DEFAULT_VIDEO


# ── helpers puros

def test_inject_runtime_va_al_principio_del_head():
    html = '<!doctype html><html><head data-x="1"><meta charset="UTF-8"></head><body></body></html>'
    out = lab.inject_runtime(html)
    assert out.count(lab.RUNTIME_TAG) == 1
    assert out.index('<head data-x="1">') < out.index(lab.RUNTIME_TAG) < out.index("<meta")


def test_inject_runtime_sin_head_y_template():
    tpl = "<template><div>escena</div></template>"
    assert lab.inject_runtime(tpl) == lab.RUNTIME_TAG + tpl


@pytest.mark.parametrize("header,size,expected", [
    (None, 100, None),
    ("bytes=0-9", 100, (0, 9)),
    ("bytes=90-", 100, (90, 99)),
    ("bytes=-10", 100, (90, 99)),
    ("bytes=50-500", 100, (50, 99)),
    ("bytes=100-", 100, None),
    ("bytes=-", 100, None),
    ("items=0-9", 100, None),
])
def test_parse_range(header, size, expected):
    assert lab.parse_range(header, size) == expected


def test_safe_join_no_sale_de_la_raiz(tmp_path):
    assert lab.safe_join(tmp_path, "a/b.html") == (tmp_path / "a" / "b.html").resolve()
    assert lab.safe_join(tmp_path, "../fuera.txt") is None
    assert lab.safe_join(tmp_path, "a/../../fuera.txt") is None


def test_player_y_runtime_son_los_del_paquete_pineado():
    """El preview usa el runtime real de hyperframes (nunca una copia)."""
    assert lab.PLAYER_JS.exists() and lab.RUNTIME_JS.exists()
    assert "gfx_runtime" in lab.PLAYER_JS.parts and "node_modules" in lab.RUNTIME_JS.parts


# ── memo de freezes (gfx_project._extract_freeze)

def test_freeze_memo_no_repite_ffmpeg(tmp_path, monkeypatch):
    base = tmp_path / "base.mp4"
    base.write_bytes(b"x" * 10)
    out = tmp_path / "cuts" / "freeze_02.jpg"
    calls = []

    def fake_run(cmd, **kw):
        calls.append(cmd)
        Path(cmd[-1]).write_bytes(b"jpg")
        return type("R", (), {"returncode": 0})()

    monkeypatch.setattr(gfx_project.subprocess, "run", fake_run)
    monkeypatch.setattr(gfx_project, "_FREEZE_MEMO", set())
    assert gfx_project._extract_freeze(base, 1.5, out)
    assert gfx_project._extract_freeze(base, 1.5, out)
    assert len(calls) == 1                                  # segunda vez: memo
    assert gfx_project._extract_freeze(base, 2.5, out)
    assert len(calls) == 2                                  # otro t → ffmpeg
    out.unlink()
    assert gfx_project._extract_freeze(base, 2.5, out)
    assert len(calls) == 3                                  # el archivo desapareció → ffmpeg
    base.write_bytes(b"y" * 20)                             # el base cambió → ffmpeg
    assert gfx_project._extract_freeze(base, 2.5, out)
    assert len(calls) == 4


# ── sesión real de ch02 (solo si están los datos de Orleans)

def _has_data() -> bool:
    try:
        from config import OUTPUT_DIR
    except Exception:  # noqa: BLE001
        return False
    w = OUTPUT_DIR / VIDEO / "_fase2b_work"
    return (w / "gfx_plan_ch02.resolved.json").exists() and (
        (w / "gfx_ch02" / "public" / "base.mp4").exists() or (w / "gfx_lab_ch02" / "public" / "base.mp4").exists())


needs_data = pytest.mark.skipif(not _has_data(), reason="sin datos de Orleans ch02")


@pytest.fixture(scope="module")
def server():
    session = lab.LabSession(VIDEO, "ch02")
    lab.LabHandler.session = session
    srv = ThreadingHTTPServer(("127.0.0.1", 0), lab.LabHandler)
    th = threading.Thread(target=srv.serve_forever, daemon=True)
    th.start()
    yield session, f"http://127.0.0.1:{srv.server_address[1]}"
    srv.shutdown()


def _get(url: str, headers: dict | None = None):
    req = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.status, dict(r.headers), r.read()


def _post(url: str, obj: dict):
    req = urllib.request.Request(url, data=json.dumps(obj).encode(), method="POST",
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())


@needs_data
def test_story_tiene_palabras_fotos_y_audio(server):
    _, url = server
    st = json.loads(_get(url + "/api/story")[2])
    assert st["cap"] == "ch02" and st["duration"] > 90
    assert len(st["words"]) > 100 and all(w["word"] for w in st["words"])
    assert [w["start"] for w in st["words"]] == sorted(w["start"] for w in st["words"])
    assert len(st["photos"]) == 15 and st["photos"][0]["start"] == 0.0
    assert all(p["thumb"] for p in st["photos"])
    code, h, body = _get(url + "/media/audio", {"Range": "bytes=0-99"})
    assert code == 206 and len(body) == 100 and h["Content-Type"] == "audio/mpeg"
    code, h, _ = _get(url + "/media/thumb/0")
    assert code == 200 and h["Content-Type"] == "image/jpeg"


@needs_data
def test_preview_usa_las_plantillas_reales(server):
    """El preview es write_project (mismo templater que el render) + el runtime inyectado."""
    session, url = server
    plan = session.director_plan()
    r = _post(url + "/preview", {"plan": plan})
    assert r["src"].startswith("/composition/index.html?v=")
    assert any(c["block"] == "title_card" for c in r["cues"])
    html = _get(url + "/composition/index.html")[2].decode("utf-8")
    assert html.count(lab.RUNTIME_TAG) == 1
    assert 'data-composition-src="compositions/scene_01.html"' in html
    on_disk = (session.project / "index.html").read_text(encoding="utf-8")
    assert html.replace(lab.RUNTIME_TAG, "") == on_disk
    scene = _get(url + "/composition/compositions/scene_02.html")[2].decode("utf-8")
    assert lab.RUNTIME_TAG in scene and 'data-composition-id="scene-02"' in scene
    code, _, body = _get(url + "/composition/public/base.mp4", {"Range": "bytes=0-1023"})
    assert code == 206 and len(body) == 1024
    # el proyecto del lab NUNCA es el del render
    assert session.project.name == "gfx_lab_ch02"


@needs_data
def test_preview_refleja_cambios_del_plan(server):
    session, url = server
    plan = session.director_plan()
    plan["callouts"] = []
    r = _post(url + "/preview", {"plan": plan})
    assert not any(c["block"] == "data_callout" for c in r["cues"])
    assert 'class="callout' not in (session.project / "index.html").read_text(encoding="utf-8")
    _post(url + "/preview", {"plan": session.director_plan()})


@needs_data
def test_rutas_fuera_de_raiz_dan_403(server):
    _, url = server
    with pytest.raises(urllib.error.HTTPError) as e:
        _get(url + "/composition/..%2F..%2Fgfx_plan_ch02.json")
    assert e.value.code in (403, 404)
