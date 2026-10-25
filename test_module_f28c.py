"""
test_module_f28c.py — F28 §C: NVENC por defecto en fase2b (--sw-encode vuelve a libx264), clips animados con 6 workers;
segmentos con --gfx en paralelo DESCARTADO (GFX_PARALELO = 1; la función se prueba forzando 2: orden de
los segmentos, tope de concurrencia, memoria → reintento de a 1, cap sin gfx → se rehace, otro error → rc 2). Sin red,
sin render.
"""
from __future__ import annotations

import threading
import time
from pathlib import Path
from types import SimpleNamespace

import fase2b


def test_nvenc_por_defecto_y_sw_encode():
    assert fase2b._HW_ENCODE is True
    src = Path(fase2b.__file__).read_text(encoding="utf-8")
    assert '"--sw-encode"' in src and "_HW_ENCODE = not args.sw_encode" in src
    assert fase2b.CLIP_WORKERS == 6 and "min(CLIP_WORKERS, n)" in src
    assert fase2b.GFX_PARALELO == 1                  # F28 §C.2: paralelo descartado (en fila por defecto)


def _plans(n):
    return [SimpleNamespace(chapter_id=f"ch{k:02d}", engine="flux") for k in range(1, n + 1)]


def _kw(tmp_path):
    return dict(work_dir=tmp_path, manifest={}, manifest_path=tmp_path / "m.json", seg_flags={}, reassemble=False,
                flow_specs={}, per_image_by_cap={}, reuse_visuals=False, reuse_caps=set(), promotions={}, hook=None,
                no_subs=False, gfx=True, gfx_quality="looks", video_id="t", sfx=True, gfx_sparse=True,
                safe_router=True, safe_by_cap={}, gfx_debug=False)


def _mocks(monkeypatch, falla=None):
    import script_engine.gfx_review as gr
    monkeypatch.setattr(fase2b, "GFX_PARALELO", 2)          # la función sigue y se prueba con el paralelo forzado
    estado = {"vivos": 0, "max": 0, "llamadas": []}
    lock = threading.Lock()

    def build(plan, segment_path, **kw):
        with lock:
            estado["vivos"] += 1
            estado["max"] = max(estado["max"], estado["vivos"])
            estado["llamadas"].append(plan.chapter_id)
        time.sleep(0.05)
        with lock:
            estado["vivos"] -= 1
        if falla:
            falla(plan)
        Path(segment_path).write_bytes(b"x")
        (Path(segment_path).parent / f"{plan.chapter_id}_gfx.mp4").write_bytes(b"g")
    monkeypatch.setattr(fase2b, "_build_chapter_segment", build)
    monkeypatch.setattr(fase2b, "_segment_hash", lambda plan, wd, fl: f"h-{plan.chapter_id}")
    monkeypatch.setattr(fase2b, "_get_duration", lambda p: 1.0)
    monkeypatch.setattr(gr, "write_review", lambda *a, **k: None)
    return estado


def test_paralelo_respeta_orden_y_tope(monkeypatch, tmp_path):
    estado = _mocks(monkeypatch)
    segs, reused, rc = fase2b._segmentos_en_paralelo(_plans(7), **_kw(tmp_path))
    assert rc == 0 and reused == []
    assert [s.name for s in segs] == [f"seg_{k:02d}_ch{k:02d}.mp4" for k in range(1, 8)]
    assert 1 < estado["max"] <= fase2b.GFX_PARALELO


def test_memoria_se_reintenta_de_a_dos(monkeypatch, tmp_path):
    vistos = {}

    def falla(plan):
        vistos[plan.chapter_id] = vistos.get(plan.chapter_id, 0) + 1
        if plan.chapter_id == "ch02" and vistos["ch02"] == 1:
            raise RuntimeError("CUDA out of memory")
    _mocks(monkeypatch, falla)
    segs, _, rc = fase2b._segmentos_en_paralelo(_plans(4), **_kw(tmp_path))
    assert rc == 0 and vistos["ch02"] == 2 and len(segs) == 4


def test_otro_error_termina_con_rc_2(monkeypatch, tmp_path):
    def falla(plan):
        if plan.chapter_id == "ch03":
            raise ValueError("roto")
    _mocks(monkeypatch, falla)
    segs, _, rc = fase2b._segmentos_en_paralelo(_plans(4), **_kw(tmp_path))
    assert rc == 2 and segs == []


def test_reensamble_reusa_sin_rehacer(monkeypatch, tmp_path):
    estado = _mocks(monkeypatch)
    kw = _kw(tmp_path)
    kw.update(reassemble=True, manifest={"ch01": "h-ch01"})
    (tmp_path / "seg_01_ch01.mp4").write_bytes(b"x")
    segs, reused, rc = fase2b._segmentos_en_paralelo(_plans(2), **kw)
    assert rc == 0 and reused == ["ch01"] and estado["llamadas"] == ["ch02"] and len(segs) == 2


def test_visual_base_bajo_candado(monkeypatch):
    src = Path(fase2b.__file__).read_text(encoding="utf-8")
    cuerpo = src.split("def _build_chapter_segment(", 1)[1].split("\ndef ", 1)[0]
    assert "_VISUAL_LOCK.acquire()" in cuerpo and "_visual_base(" in cuerpo
    assert "_VISUAL_LOCK.release()" in cuerpo


def test_cap_sin_gfx_en_paralelo_se_rehace_en_fila(monkeypatch, tmp_path):
    estado = _mocks(monkeypatch)
    import script_engine.gfx_review as gr  # noqa: F401
    original = fase2b._build_chapter_segment
    vistos = {}

    def build(plan, segment_path, **kw):
        vistos[plan.chapter_id] = vistos.get(plan.chapter_id, 0) + 1
        original(plan, segment_path, **kw)
        if plan.chapter_id == "ch02" and vistos["ch02"] == 1:          # la 1.ª vez el gfx cayó a base_clip
            (Path(segment_path).parent / "ch02_gfx.mp4").unlink()
    monkeypatch.setattr(fase2b, "_build_chapter_segment", build)
    segs, _, rc = fase2b._segmentos_en_paralelo(_plans(3), **_kw(tmp_path))
    assert rc == 0 and vistos == {"ch01": 1, "ch02": 2, "ch03": 1} and len(segs) == 3
    assert estado["max"] >= 1
