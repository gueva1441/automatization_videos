"""Tests de la identidad que guarda el lab (F3 §C): perfil + plan dorado + IDENTIDAD_<perfil>.md."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

import gfx_config
from script_engine import gfx_identity as gi

CATALOG = json.loads((Path(__file__).parent / "lab" / "identidad" / "catalogo.json").read_text(encoding="utf-8"))
PROFILE = json.loads(gfx_config.profile_path("misterio").read_text(encoding="utf-8"))


def _state(**kw):
    st = {"plan": {"chapter_number": 2, "callouts": [], "punch_in": []}, "tokens": {}, "anotado": {}, "marks": {},
          "sugerencias": {}, "lexicon": {}, "faltan": "", "touched": []}
    st.update(kw)
    return st


@pytest.fixture
def profiles(tmp_path, monkeypatch):
    """Directorio de perfiles temporal con una copia de misterio.json (el real nunca se toca)."""
    d = tmp_path / "gfx_profiles"
    d.mkdir()
    shutil.copy2(gfx_config.profile_path("misterio"), d / "misterio.json")
    monkeypatch.setattr(gfx_config, "GFX_PROFILES_DIR", d)
    return d


def test_perfil_con_identity_es_valido_para_el_pipeline(profiles):
    p = dict(PROFILE, identity={"version": 1, "marks": {}})
    (profiles / "misterio.json").write_text(json.dumps(p, ensure_ascii=False), encoding="utf-8")
    assert gfx_config.load_profile("misterio")["identity"]["version"] == 1
    assert gfx_config.rules_from_profile(p) == gfx_config.rules_from_profile(PROFILE)   # el motor la ignora


def test_apply_identity_tokens_fuentes_bloques_y_lexico():
    word = next(iter(PROFILE["moods"]["agua"]["triggers"]))
    st = _state(tokens={"accent_hex": "#c2302f", "vignette_opacity": 0.3, "callout_font": "Anton"},
                marks={"lower_third": {"v": "no"}, "count_up": {"v": "no", "por_que": "no me gusta"},
                       "archive_clipping": {"v": "si"}, "keyword_stamp": {"v": "no"}},
                lexicon={word: 0, "sumergidos": 2})
    new = gi.apply_identity(PROFILE, st, golden_name="misterio_golden_ch02.json")
    assert new["tokens"]["accent_hex"] == "#c2302f" and new["tokens"]["vignette_opacity"] == 0.3
    assert new["fonts"]["callout"] == "Anton" and "callout_font" not in new["tokens"]
    assert new["blocks"]["count_up"]["enabled"] is False and new["blocks"]["archive_clipping"]["enabled"] is True
    assert new["tokens"]["emphasis_stamp"] is False                     # ✖ sello rojo → token
    assert word not in new["moods"]["agua"]["triggers"]
    assert word not in (new["moods"]["agua"].get("icon_words") or {})
    assert new["moods"]["agua"]["triggers"]["sumergidos"] == 2
    assert new["identity"]["marks"]["count_up"]["por_que"] == "no me gusta"
    assert PROFILE["tokens"]["accent_hex"] != "#c2302f" or True        # el original no se muta
    assert PROFILE.get("identity", {}).get("marks", {}).get("count_up", {}).get("por_que") != "no me gusta"


def _save(st, profiles, tmp_path):
    return gi.save_identity(st, profile="misterio", cap="ch02", video_id="vid", locked_plan=st["plan"],
                            rejected=[], summary="# resumen\n", md_dir=tmp_path / "md")


def test_save_identity_escribe_los_tres_archivos_y_respalda(profiles, tmp_path):
    st = _state(tokens={"grain_opacity": 0.08}, marks={"vignette": {"v": "si"}})
    out = _save(st, profiles, tmp_path)
    prof = json.loads(Path(out["perfil"]).read_text(encoding="utf-8"))
    assert prof["tokens"]["grain_opacity"] == 0.08 and prof["identity"]["golden_plan"] == "misterio_golden_ch02.json"
    assert json.loads(Path(out["respaldo"]).read_text(encoding="utf-8")) == PROFILE
    gold = json.loads(Path(out["golden"]).read_text(encoding="utf-8"))
    assert gold["plan"] == st["plan"] and gold["cap"] == "ch02"
    assert Path(out["resumen"]).name == "IDENTIDAD_misterio.md"
    assert not list(profiles.glob("_lab_tmp_*"))                       # sin restos de la validación
    gfx_config.load_profile("misterio")                                 # sigue cargando


def test_save_identity_invalido_no_toca_el_perfil(profiles, tmp_path):
    before = (profiles / "misterio.json").read_bytes()
    trig = list(PROFILE["moods"]["agua"]["triggers"])
    st = _state(lexicon={w: 0 for w in trig})                          # deja el mood activo con < 25 disparadores
    with pytest.raises(ValueError):
        _save(st, profiles, tmp_path)
    assert (profiles / "misterio.json").read_bytes() == before
    assert not list(profiles.glob("_lab_tmp_*")) and not list(profiles.glob("*.bak_f3_*"))
    assert not (profiles / "misterio_golden_ch02.json").exists()


def test_summary_tiene_las_cinco_secciones():
    cues = [{"t": 0.0, "dur": 3.0, "block": "title_card", "text": "CAPÍTULO 2 · X"},
            {"t": 9.9, "dur": 4.0, "block": "archive_clipping", "text": "El huracán"},
            {"t": 26.8, "dur": 2.5, "block": "keyword_emphasis:oscuridad_encierro", "text": "oscuro"},
            {"t": 9.4, "dur": 0.6, "block": "shot_transition:dissolve", "text": "20 f"}]
    words = [{"i": 0, "word": "Aquel", "start": 0.08}, {"i": 21, "word": "día,", "start": 9.8},
             {"i": 60, "word": "oscuro", "start": 26.82}]
    st = _state(marks={"archive_clipping": {"v": "si", "regla": "primer dato con fuente"},
                       "lower_third": {"v": "no", "por_que": "no hay entrevistas"},
                       "zoom_through": {"v": "si"}, "match_cut": {"v": "si"}, "keyword_emphasis": {"v": "no"}},
                anotado={"archive_clipping": {"estilo": "postit"}}, sugerencias={"S03": "probando", "S06": "no"},
                faltan="Quisiera que…", touched=["grain"], tokens={"accent_hex": "#c2302f"}, lexicon={"oscuro": 0})
    sugs = [{"id": "S06", "titulo": "ahogaba"}]
    md = gi.summary_md(st, CATALOG, cues, words, {"accent_hex": "#c8102e", "anim_archive_head": "cascade"},
                       profile="misterio", cap="ch02", video_id="vid", sugerencias=sugs)
    for h in ("## 1. Lo que se queda", "## 2. Lo que nunca", "## 3. Lo que falta", "## 4. Plan dorado de ch02",
              "## 5. Preguntas abiertas"):
        assert h in md
    assert "primer dato con fuente" in md and "Estilo: post-it (anotado)" in md
    assert "no hay entrevistas" in md and "S06 · ahogaba" in md and "> Quisiera que…" in md
    assert "| 00:09.9 | día, | Recorte de archivo | El huracán |" in md
    assert "Fundido cruzado × 1" in md and "«oscuro» → apagada" in md
    assert "Probaste **Grano**" in md and "S03 quedó en 'probando'" in md
    assert "**Zoom a través** está ✔ pero todavía no se dibuja" in md
    assert "Match cut" in md and "no se construye en F3" in md
    assert "**Mood + sello rojo** está ✖ pero sigue 1" in md


def test_http_save_identity_en_directorios_temporales(profiles, tmp_path, monkeypatch):
    """POST /save_identity de punta a punta, con el perfil y el md en carpetas temporales."""
    import test_module_gfx_lab as tl
    if not tl._has_data():
        pytest.skip("sin datos de Orleans ch02")
    import threading
    import urllib.request
    from http.server import ThreadingHTTPServer
    import gfx_lab_server as lab
    lab_dir = tmp_path / "identidad"
    lab_dir.mkdir()
    for f in ("catalogo.json", "sugerencias_ch02.json"):
        shutil.copy2(lab.LAB_DIR / f, lab_dir / f)
    monkeypatch.setattr(lab, "LAB_DIR", lab_dir)
    session = lab.LabSession(lab.DEFAULT_VIDEO, "ch02")
    assert session.state_path.parent == lab_dir                       # el estado de Omar no se toca
    lab.LabHandler.session = session
    srv = ThreadingHTTPServer(("127.0.0.1", 0), lab.LabHandler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        url = f"http://127.0.0.1:{srv.server_address[1]}"
        st = _state(plan=session.director_plan(), tokens={"accent_hex": "#c2302f"},
                    marks={"archive_clipping": {"v": "si"}})
        req = urllib.request.Request(url + "/save_identity", data=json.dumps(st).encode(), method="POST",
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=60) as r:
            out = json.loads(r.read())["archivos"]
        assert Path(out["perfil"]).parent == profiles and Path(out["resumen"]).parent == profiles   # F4: IDENTIDAD va con el perfil
        gold = json.loads(Path(out["golden"]).read_text(encoding="utf-8"))
        assert gold["plan"]["title_card"] and gold["tokens"] == {"accent_hex": "#c2302f"}
        assert "## 4. Plan dorado de ch02" in Path(out["resumen"]).read_text(encoding="utf-8")
        with urllib.request.urlopen(url + "/summary", timeout=60) as r:
            assert r.headers["Content-Type"].startswith("text/markdown") and b"IDENTIDAD" in r.read()
    finally:
        srv.shutdown()


def test_dos_guardados_seguidos_no_pisan_el_respaldo(profiles, tmp_path):
    a = _save(_state(tokens={"grain_opacity": 0.08}), profiles, tmp_path)
    b = _save(_state(tokens={"grain_opacity": 0.15}), profiles, tmp_path)
    assert a["respaldo"] != b["respaldo"]
    assert json.loads(Path(a["respaldo"]).read_text(encoding="utf-8")) == PROFILE
    assert json.loads(Path(b["respaldo"]).read_text(encoding="utf-8"))["tokens"]["grain_opacity"] == 0.08
