"""F71b — la persona que el prompt nombra trae su foto madre, y QA lo puede arreglar. Sin red."""
from __future__ import annotations

import json

import pytest

import asset_manager as am
import qa_studio_server as qa
from test_qa_studio import TID, _call_fix, _fix_deps, build_topic

PERSONAS = {"Daniel Écija": {"era": "1962-1963", "condition_by_period": [{"years": "1991-1992", "condition": "enfermo"}]}}


@pytest.fixture(autouse=True)
def _motor_nb2(monkeypatch):
    monkeypatch.setattr(am.api, "image_engine", "nb2_lite", raising=False)


def _reg(tmp_path, *nombres):
    reg = {}
    for n in nombres:
        f = tmp_path / f"{n.replace(' ', '_')}.png"
        f.write_bytes(b"x")
        reg[n] = str(f)
    return reg


def test_el_caso_de_la_mujer_con_la_foto_de_daniel(tmp_path):
    """persona vacía, prompt que la nombra, año 2026 fuera de era pero no de un tramo fuera de era: aporta."""
    reg = _reg(tmp_path, "Daniel Écija", "María Bernal")
    prompt = "An aged black-and-white print of Daniel Écija held by a woman's hands."
    assert am._madres_para_item([], [], "2026", reg, PERSONAS, prompt) == [("Daniel Écija", reg["Daniel Écija"])]
    assert am._madres_para_item([], [], "2026", reg, PERSONAS) == []      # sin prompt, como antes


def test_daniel_hijo_no_dispara_a_daniel(tmp_path):
    reg = _reg(tmp_path, "Daniel Écija", "Daniel Écija hijo")
    m = am._madres_para_item([], [], "1985", reg, {}, "The young Daniel Écija hijo at the airport.")
    assert [r for r, _ in m] == ["Daniel Écija hijo"]
    assert am._nombres_en_prompt("Daniel Écija hijo and his father Daniel Écija.", reg) == ["Daniel Écija hijo", "Daniel Écija"]


def test_nombre_entero_y_exacto(tmp_path):
    reg = _reg(tmp_path, "Ana", "Daniel Écija")
    assert am._nombres_en_prompt("A banana and Anabel, with Daniel alone.", reg) == []
    assert am._nombres_en_prompt("Ana, near the wall.", reg) == ["Ana"]


def test_claves_de_objeto_fuera(tmp_path):
    reg = _reg(tmp_path, "__subject__")
    assert am._nombres_en_prompt("the __subject__ of the shot", reg) == []
    assert am._madres_para_item([], [], None, reg, {}, "the __subject__ of the shot") == []


def test_filtro_de_era_sigue_mandando(tmp_path):
    reg = _reg(tmp_path, "Daniel Écija")
    assert am._madres_para_item([], [], "1991", reg, PERSONAS, "Daniel Écija in a hospital bed") == []
    assert [r for r, _ in am._madres_para_item([], [], "1962", reg, PERSONAS, "Daniel Écija at the mine")] == ["Daniel Écija"]


def test_tope_2_persona_primero_sin_repetir(tmp_path):
    reg = _reg(tmp_path, "A Uno", "B Dos", "C Tres")
    m = am._madres_para_item(["C Tres"], [], None, reg, {}, "A Uno, C Tres and B Dos together")
    assert [r for r, _ in m] == ["C Tres", "A Uno"]


def test_madre_que_no_existe_en_disco_no_entra(tmp_path):
    reg = _reg(tmp_path, "A Uno")
    reg["B Dos"] = str(tmp_path / "no.png")
    assert [r for r, _ in am._madres_para_item([], [], None, reg, {}, "A Uno and B Dos")] == ["A Uno"]


def _arma_qa(tmp_path, prompt_en_subject):
    build_topic(tmp_path)
    reg = _reg(tmp_path, "Daniel Écija")
    for p in (tmp_path / "data" / "scripts" / f"{TID}.json", tmp_path / "data" / "scripts" / "_steps" / TID / "03_visual.json"):
        d = json.loads(p.read_text(encoding="utf-8"))
        it = next(c for c in d["chapters"] if c["chapter_number"] == 3)["image_prompts"][0]
        it["persona"], it["anio"] = [], "2026"
        if "foto_madre_registry" in d:
            d["foto_madre_registry"].update(reg)
            d["foto_madre_personas"] = PERSONAS
        p.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    return qa.QAState(TID, base_dir=tmp_path), reg


def test_qa_usa_el_prompt_rearmado_y_no_guarda_en_persona(tmp_path):
    """El pedido trae el nombre: el prompt viejo no lo tenía, el rearmado sí. Y eso alcanza para que venga la madre."""
    st, _ = _arma_qa(tmp_path, None)
    seen = {}

    def gen(prompt, art_profile, out_path, use_ultra, seed, foto_madre_data_uris=None):
        seen.update(uris=foto_madre_data_uris, prompt=prompt)
        out_path.write_bytes(b"X")
        return {}
    deps = _fix_deps(gen, editar={"subject": "A print of Daniel Écija"})
    (ok, texto), _ = _call_fix(st, "ch03", "ch03_img_01.png", "que sea Daniel", deps)
    assert ok is True and "Daniel Écija" in seen["prompt"]
    assert seen["uris"] == ["uri:Daniel_Écija.png"]
    assert "madre de Daniel Écija" in texto
    for p in (st.script_path, tmp_path / "data" / "scripts" / "_steps" / TID / "03_visual.json"):
        d = json.loads(p.read_text(encoding="utf-8"))
        assert next(c for c in d["chapters"] if c["chapter_number"] == 3)["image_prompts"][0]["persona"] == []


def test_qa_sin_nombre_en_el_prompt_sigue_sin_madre(tmp_path):
    st, _ = _arma_qa(tmp_path, None)
    seen = {}

    def gen(prompt, art_profile, out_path, use_ultra, seed, foto_madre_data_uris=None):
        seen["uris"] = foto_madre_data_uris
        out_path.write_bytes(b"X")
        return {}
    (ok, texto), _ = _call_fix(st, "ch03", "ch03_img_01.png", "x", _fix_deps(gen))
    assert ok is True and seen["uris"] is None and "madre de" not in texto


def test_fix_respalda_nativo_y_llamada(tmp_path):
    st, _ = _arma_qa(tmp_path, None)
    d = st.resolve_image("ch03", "ch03_img_01.png").parent
    (d / "ch03_img_01_native.png").write_bytes(b"NATIVA")
    (d / "ch03_img_01.llamada.json").write_text("{}", encoding="utf-8")

    def gen(prompt, art_profile, out_path, use_ultra, seed, foto_madre_data_uris=None):
        out_path.write_bytes(b"X")
        return {}
    (ok, _t), _ = _call_fix(st, "ch03", "ch03_img_01.png", "x", _fix_deps(gen))
    b = st.assets_dir / "_qa_backups"
    assert ok and (b / "ch03_img_01_native.png.20260614_000000.bak.png").read_bytes() == b"NATIVA"
    assert (b / "ch03_img_01.llamada.json.20260614_000000.bak.json").exists()
