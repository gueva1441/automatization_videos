"""F48 S1 — GEO y ERA del pedido de los casilleros de foto (m03_visual._geo_era) y fuera el bloque «UBICACIONES
DOCUMENTADAS» (hardcode de Orleans). Offline: lee el perfil y la narración de Wittenoom de `_steps/` si están."""
import json

import pytest

from script_engine import m03_visual as m3

WITTENOOM = "123bbb64-9fca-4395-8bf4-57d60e219ef1"
_W = m3.STEPS_DIR / WITTENOOM


@pytest.mark.skipif(not (_W / "_perfil.json").exists() or not (_W / "01b_narration.json").exists(),
                    reason="sin el research de Wittenoom en _steps/")
def test_geo_era_de_wittenoom():
    narr = json.loads((_W / "01b_narration.json").read_text(encoding="utf-8"))
    ge = m3._geo_era(WITTENOOM, narr)
    assert ge == {"canonical_geo": "Wittenoom", "canonical_era": "1943–2024"}   # el perfil dice anio_fin 2007: no se usa
    block = m3._build_topic_block({"video_title": "x", **ge})
    assert "GEO     : Wittenoom" in block and "ERA     : 1943–2024" in block


def test_geo_era_perfil_y_anios_en_letras(tmp_path, monkeypatch):
    monkeypatch.setattr(m3, "STEPS_DIR", tmp_path)
    (tmp_path / "t1").mkdir()
    (tmp_path / "t1" / "_perfil.json").write_text(json.dumps({"lugar_principal": "Kyshtym"}), encoding="utf-8")
    narr = {"chapters": [{"narration": "En mil novecientos cincuenta y siete estalló el tanque."},
                         {"narration": "Recién en 1989 se supo. Hoy, en dos mil veinte, 300 personas viven ahí."}]}
    assert m3._geo_era("t1", narr) == {"canonical_geo": "Kyshtym", "canonical_era": "1957–2020"}


def test_geo_era_sin_datos_queda_el_respaldo(tmp_path, monkeypatch):
    monkeypatch.setattr(m3, "STEPS_DIR", tmp_path)
    assert m3._geo_era("nadie", {"chapters": [{"narration": "Sin años acá."}]}) == {}
    block = m3._build_topic_block({"video_title": "x"})
    assert "GEO     : (sin geo)" in block and "ERA     : (sin era)" in block


def test_sin_bloque_de_ubicaciones():
    for nombre in ("_format_documented_locations", "_documented_places", "_LOC_GROUPS", "_LOC_DEST"):
        assert not hasattr(m3, nombre)
    pool = {"lugares": [{"nombre": "CYC", "rol": "Instalación juvenil"}], "datos": [], "cronologia": [],
            "personajes": [{"nombre": "Ana Pérez", "rol": "Minera"}]}
    canon = m3._format_seedream_canon_block({"era_visual_canon": {}, "documented_people": [], "documented_props": [],
                                             "evidence_pool": pool})
    assert "UBICACIONES" not in canon and "Ningún menor" not in canon
