"""F4b §4: íconos gratis automáticos (game-icons restilizado) + crédito en la descripción."""
from __future__ import annotations

import json

from script_engine.gfx_icons import auto_icons as ai
from script_engine.gfx_icons import icon_svg, scoped_svg

SVG = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><path d="M0 0h512v512H0z"/>'
       '<path fill="#fff" d="M100 100h300v300H100z"/></svg>')


def _set(tmp_path, monkeypatch, index):
    gi = tmp_path / "gi"
    (gi / "lorc").mkdir(parents=True)
    (gi / "lorc" / "padlock.svg").write_text(SVG, encoding="utf-8")
    (gi / "delapouite" / "").mkdir(parents=True)
    (gi / "delapouite" / "prisoner.svg").write_text(SVG, encoding="utf-8")
    idx = tmp_path / "icons_index.json"
    idx.write_text(json.dumps(index), encoding="utf-8")
    monkeypatch.setattr(ai, "GI_DIR", gi)
    monkeypatch.setattr(ai, "INDEX", idx)
    ai._word_map.cache_clear()


def test_lemas():
    assert ai.lemmas("Celdas,") == ["celdas", "celda", "celdo"]
    assert "preso" in ai.lemmas("presos") and "candado" in ai.lemmas("candados")


def test_lookup_y_svg_restilizado(tmp_path, monkeypatch):
    _set(tmp_path, monkeypatch, {"padlock": {"path": "lorc/padlock.svg", "es": ["candado", "cerradura"]},
                                 "prisoner": {"path": "delapouite/prisoner.svg", "es": ["prisionero", "preso", "recluso"]}})
    assert ai.lookup("candados") == "gi:lorc/padlock" and ai.lookup("presos") == "gi:delapouite/prisoner"
    assert ai.lookup("tristeza") is None
    svg = icon_svg("gi:lorc/padlock")
    assert 'fill="#e8e0cc"' in svg and "M0 0h512v512H0z" not in svg and 'class="ic-fill"' in svg   # sin el fondo negro
    assert icon_svg("gi:../../secreto") is None and icon_svg("gi:lorc/nada") is None              # no sale del set
    assert 'id="u1-ink"' in scoped_svg(svg, "u1", 360)                                            # tinta + grano del canal


def test_indice_por_tandas(tmp_path, monkeypatch):
    _set(tmp_path, monkeypatch, {})
    calls = []

    def fake(prompt, **kw):
        calls.append(prompt)
        return {"items": [{"n": "padlock", "es": ["Candado"]}, {"n": "prisoner", "es": ["preso"]}]}
    idx = ai.build_index(call=fake)
    assert idx["padlock"] == {"path": "lorc/padlock.svg", "es": ["candado"]} and len(calls) == 1
    assert ai.build_index(call=lambda p, **k: 1 / 0) == idx                                        # ya indexado: no llama


def test_credito_en_la_descripcion():
    from script_engine.m09_packaging import ICON_CREDIT, _normalize_metadata
    d = _normalize_metadata({"titulos": ["t"], "overlays": ["o"], "descripcion": "Un caso real.", "tags": ["x"]})
    assert d["descripcion"].endswith(ICON_CREDIT) and "game-icons.net (CC BY 3.0)" in ICON_CREDIT
    assert _normalize_metadata({"descripcion": d["descripcion"]})["descripcion"].count(ICON_CREDIT) == 1


def test_flash_elige_entre_candidatos_o_ninguno(tmp_path, monkeypatch):
    _set(tmp_path, monkeypatch, {"padlock": {"path": "lorc/padlock.svg", "es": ["candado"]},
                                 "prisoner": {"path": "delapouite/prisoner.svg", "es": ["prisionero"]}})
    monkeypatch.setattr(ai, "CHOICES", tmp_path / "auto_choice.json")
    seen = {}

    def fake(prompt, **kw):
        seen["p"] = prompt
        return {"items": [{"palabra": "candado", "n": 1}, {"palabra": "tristeza", "n": 0, "buscar": ""},
                          {"palabra": "reclusos", "n": 0, "buscar": "prisoner"}]}
    got = ai.choose_icons([("candado", "un candado oxidado"), ("tristeza", "la tristeza"), ("reclusos", "los reclusos")], call=fake)
    assert got == {"candado": "gi:lorc/padlock", "tristeza": None, "reclusos": "gi:delapouite/prisoner"}
    assert "1. padlock" in seen["p"] and "(sin candidatos)" in seen["p"]
    assert ai.choose_icons([("candado", "x")], call=lambda p, **k: 1 / 0) == {"candado": "gi:lorc/padlock"}   # cache
