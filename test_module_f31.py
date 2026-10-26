"""
test_module_f31.py — F31: las variantes de forma viven detrás de `--forma-variante` y el default queda como hoy.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from gfx_config import gfx_rules
from script_engine.gfx_project import GfxScene, forma, write_project

PLAN = {"callouts": [{"text": "1.910 personas", "kicker": "Muertos", "ficha": True, "start": 4.0, "duration": 3.0,
                      "side": "left"}],
        "archive_clippings": [{"kicker": "Acta, 1943", "headline": "Aprobada con 13 de 34", "body": "", "start": 9.0,
                               "duration": 4.0, "side": "right"}],
        "emphasis": [{"word": "fisura", "start": 14.0, "duration": 2.5, "layer": "minima", "category": "x",
                      "stamp": True, "side": "right"}],
        "time_ticker": {"day": "9", "month": "OCT", "tail": "1963", "start": 1.0, "duration": 2.5, "changes": []}}


@pytest.fixture
def variante():
    viejo = gfx_rules.forma_variante

    def poner(v: str) -> None:
        object.__setattr__(gfx_rules, "forma_variante", v)
    yield poner
    object.__setattr__(gfx_rules, "forma_variante", viejo)


def _html(tmp: Path, v: str, poner) -> str:
    poner(v)
    d = tmp / (v.replace(",", "_") or "hoy")
    (d / "public").mkdir(parents=True)
    (d / "public" / "base.mp4").write_bytes(b"")
    write_project(PLAN, [GfxScene(0, 0.0, 20.0, "R2")], d, duration=20.0, width=2560, height=1440, fps=30, grade=False)
    return (d / "index.html").read_text(encoding="utf-8")


def test_sin_flag_todo_como_hoy(tmp_path, variante):
    h = _html(tmp_path, "", variante)
    assert forma("V") is None and forma("S") is None and forma("R") is None
    assert 'gsap.set("#fc0-title span", { yPercent: 110 })' in h                  # ficha con su wipe
    assert 'gsap.set("#ar0-paper", { opacity: 0, y: -40, rotation: -6 })' in h      # recorte de siempre
    assert f"font:400 {gfx_rules.emphasis_stamp_px}px/1" in h and "border:7px solid" in h
    assert "padding:8px 26px 4px;background:rgba(10,10,10,.35);white-space" in h   # el sello de hoy (ya con placa)
    assert "font:400 64px/1" in h                                                   # el reloj de hoy


def test_v2_v3_entran_y_salen_enteros(tmp_path, variante):
    h2 = _html(tmp_path, "V2", variante)
    assert 'gsap.set("#fc0", { opacity: 0, y: 0 })' in h2 and "yPercent: 110" not in h2
    assert 'gsap.set("#ar0-paper", { rotation: -2.5 })' in h2 and f"duration: {gfx_rules.title_fade_out}" in h2
    h3 = _html(tmp_path, "V3", variante)
    assert 'gsap.set("#fc0", { opacity: 0, y: 6 })' in h3 and 'y: -6' in h3 and "power4.out" in h3


def test_sello_s1_s2_s3_con_y_sin_placa_y_reloj_r2(tmp_path, variante):
    px = gfx_rules.emphasis_stamp_px
    s1 = _html(tmp_path, "S1", variante)
    assert f"font:400 {px}px/1" in s1 and "padding:8px 26px 4px;white-space" in s1     # S1 sin placa
    s3p = _html(tmp_path, "S3P,R2", variante)
    assert f"font:400 {px * 3}px/1" in s3p and "border:21px solid" in s3p and "padding:24px 78px 12px;background:rgba(10,10,10,.35);" in s3p
    assert f"font:400 {round(64 * gfx_rules.title_scale)}px/1" in s3p and "font:400 64px/1" not in s3p


def test_el_flag_esta_en_fase2b_y_no_es_default():
    src = Path("fase2b.py").read_text(encoding="utf-8")
    assert '"--forma-variante"' in src and 'object.__setattr__(_gr, "forma_variante", args.forma_variante)' in src
    assert type(gfx_rules).__dataclass_fields__["forma_variante"].default == ""
