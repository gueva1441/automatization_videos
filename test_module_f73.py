"""F73 — miniaturas con foto madre (A) y sello de narración (B); toda la voz de cada foto en QA (C). Sin red: el motor de
fotos, la regla de madres y la narración aprobada se reemplazan por dobles; todo escribe en tmp_path.
(D no tiene test: la simulación de F73 mostró que la regla del handoff no alcanza y `fase2b.py` no se tocó.)"""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import asset_manager as am  # noqa: E402
from script_engine import m09_packaging as pkg  # noqa: E402
import qa_studio_server as q  # noqa: E402,F401
from qa_studio_server import voz_por_anclas  # noqa: E402

TID = "t-f73"
ESTADO: dict = {}          # la narración aprobada vigente que ve el doble de `narracion_vigente`


@pytest.fixture
def pub(tmp_path, monkeypatch):
    """publish/ y data/scripts en tmp_path; narración aprobada vigente = «AAA» salvo que el test la cambie."""
    monkeypatch.setattr(pkg, "_publish_dir", lambda tid: tmp_path / "publish")
    monkeypatch.setattr(pkg, "_candidates_dir", lambda tid: tmp_path / "publish" / "thumb_candidates")
    monkeypatch.setattr(pkg, "DATA_DIR", tmp_path / "data")
    ESTADO["md5"] = "AAA"
    monkeypatch.setattr(pkg, "narracion_vigente", lambda tid: ESTADO["md5"])
    p = tmp_path / "publish"
    p.mkdir()
    return p


def _meta(pub, **kw):
    (pub / "metadata.json").write_text(json.dumps({"topic_id": TID, "paquetes": [{"n": 1, "titulo": "viejo"}],
                                                   "descripcion": "d", "tags": ["t"], **kw}), encoding="utf-8")


# ─── A: madres en la foto del paquete ───
def test_a_madres_con_la_regla_unica_y_los_args_de_qa(pub, monkeypatch):
    (pub.parent / "data" / "scripts").mkdir(parents=True)
    script = {"foto_madre_registry": {"Daniel": "d.png"}, "foto_madre_personas": {"Daniel": {"era": "x"}}}
    (pub.parent / "data" / "scripts" / f"{TID}.json").write_text(json.dumps(script), encoding="utf-8")
    vistos = []
    monkeypatch.setattr(am, "_madres_para_item", lambda *a: vistos.append(a) or [("Daniel", "d.png")])
    item = {"persona": ["Daniel"], "foto_madre_ref": "__subject__", "anio": 1963, "prompt": "un minero"}
    assert pkg.madres_del_paquete(TID, item) == [("Daniel", "d.png")]
    assert vistos == [(["Daniel"], ["__subject__"], 1963, script["foto_madre_registry"],
                       script["foto_madre_personas"], "un minero")]


def test_a_sin_guion_vivo_no_hay_madres(pub, monkeypatch):
    monkeypatch.setattr(am, "_madres_para_item", lambda *a: pytest.fail("sin guion no se llama"))
    assert pkg.madres_del_paquete(TID, {"persona": ["Daniel"]}) == []


def test_a_foto_paquete_pasa_las_madres_como_data_uris(tmp_path, monkeypatch):
    llamadas = []
    monkeypatch.setattr(am, "_path_to_data_uri", lambda p: f"uri:{p}")
    monkeypatch.setattr(am, "_generate_image_raw", lambda prompt, out, use_ultra, **kw: llamadas.append((prompt, kw)))
    assert pkg.foto_paquete("p", tmp_path / "x.png", [("Daniel", "d.png"), ("María", "m.png")]) is None
    assert pkg.foto_paquete("p", tmp_path / "y.png", []) is None
    assert llamadas == [("p", {"foto_madre_data_uris": ["uri:d.png", "uri:m.png"]}), ("p", {"foto_madre_data_uris": None})]


def test_a_el_paquete_guarda_persona_y_las_madres_que_anclaron(pub, monkeypatch):
    monkeypatch.setattr(pkg, "madres_del_paquete", lambda tid, item: [("Daniel", "d.png")])
    vistos = []
    monkeypatch.setattr(pkg, "foto_paquete", lambda prompt, out, madres: vistos.append(madres))
    p = {"n": 4}
    pkg._foto_del_paquete(TID, p, {"prompt": "x", "persona": ["Daniel"]})
    assert p["persona"] == ["Daniel"] and p["foto_madre_refs"] == ["Daniel"] and p["foto"] == "paquete_04_base.png"
    assert vistos == [[("Daniel", "d.png")]]


def test_a_un_solo_camino_sin_la_llamada_vieja():
    import inspect
    src = inspect.getsource(pkg)
    assert "_generate_image_raw(prompt, out_path, use_ultra=False)\n" not in src
    assert src.count("_generate_image_raw(") == 1


# ─── B: sello de narración ───
def test_b_sin_sello_se_archiva_todo_y_no_queda_vigente(pub):
    _meta(pub)
    (pub / "thumb_candidates").mkdir()
    (pub / "thumb_candidates" / "paquete_01.png").write_bytes(b"x")
    (pub / "CHECKLIST_PUBLICACION.md").write_text("viejo", encoding="utf-8")
    assert not pkg.candidates_ready(TID)
    d = pkg.archivar_paquetes_desfasados(TID)
    assert d is not None and d.parent == pub and d.name.startswith("_desfasado_")
    assert (d / "thumb_candidates" / "paquete_01.png").exists() and (d / "CHECKLIST_PUBLICACION.md").exists()
    assert json.loads((d / "metadata.json").read_text(encoding="utf-8"))["paquetes"][0]["titulo"] == "viejo"
    resto = json.loads((pub / "metadata.json").read_text(encoding="utf-8"))
    assert "paquetes" not in resto and "descripcion" not in resto and resto["topic_id"] == TID
    assert not (pub / "thumb_candidates").exists()


def test_b_sello_de_otra_narracion_se_archiva(pub):
    _meta(pub, narracion_md5="VIEJO")
    assert pkg.archivar_paquetes_desfasados(TID) is not None


def test_b_sello_vigente_no_se_toca(pub):
    _meta(pub, narracion_md5="AAA")
    assert pkg.candidates_ready(TID)
    assert pkg.archivar_paquetes_desfasados(TID) is None
    assert json.loads((pub / "metadata.json").read_text(encoding="utf-8"))["paquetes"]


def test_b_narracion_sin_aprobar_no_genera(pub, monkeypatch):
    ESTADO["md5"] = None
    monkeypatch.setattr(pkg, "pedir_paquetes", lambda *a: pytest.fail("no se piden paquetes"))
    import fase1_5
    monkeypatch.setattr(fase1_5, "estado_narracion", lambda *a, **k: (False, "la narración no está aprobada"))
    with pytest.raises(pkg.PaquetesParada, match="sin narración aprobada"):
        pkg.run_candidates(TID)


def test_b_run_candidates_archiva_sella_y_arranca_de_1(pub, monkeypatch):
    _meta(pub, narracion_md5="VIEJO")
    monkeypatch.setattr(pkg, "cargar_narracion", lambda tid: {})
    monkeypatch.setattr(pkg, "cargar_pool", lambda tid: {})
    monkeypatch.setattr(pkg, "numeros_pool", lambda pool: set())
    monkeypatch.setattr(pkg, "textos_pool", lambda pool: {})
    monkeypatch.setattr(pkg, "pedir_paquetes", lambda *a: {"paquetes": [{"titulo": "nuevo", "texto": "T", "ancla": "a",
                                                                         "dato_ids": []}], "descripcion": "D", "tags": []})
    monkeypatch.setattr(pkg, "prompts_paquetes", lambda tid, narr, anclas: [None])
    pkg.run_candidates(TID)
    meta = json.loads((pub / "metadata.json").read_text(encoding="utf-8"))
    assert meta["narracion_md5"] == "AAA" and [p["n"] for p in meta["paquetes"]] == [1]
    assert meta["paquetes"][0]["titulo"] == "nuevo"
    assert len(list(pub.glob("_desfasado_*"))) == 1


def test_b_serve_y_run_pipeline_archivan():
    import inspect
    import run_pipeline
    from script_engine import m09_review_server as rs
    assert "archivar_paquetes_desfasados(tid)" in inspect.getsource(rs.serve)
    assert "archivar_paquetes_desfasados(tid)" in inspect.getsource(run_pipeline._paso_packaging)


# ─── C: toda la voz debajo de cada foto (QA) ───
TEXTO = "Uno dos tres. Cuatro cinco seis. Siete ocho.\n\nNueve diez once. Doce trece."


def _palabras(xs):
    return sum(len((x or "").split()) for x in xs)


def test_c_tramo_ancla_a_ancla():
    v = voz_por_anclas(TEXTO, ["Uno dos tres.", "Siete ocho.", "Doce trece."])
    assert v[0] == "Uno dos tres. Cuatro cinco seis."
    assert v[1] == "Siete ocho.\n\nNueve diez once."


def test_c_ultimo_hasta_el_final():
    v = voz_por_anclas(TEXTO, ["Uno dos tres.", "Nueve diez once."])
    assert v[-1] == "Nueve diez once. Doce trece."


def test_c_ancla_tolera_solo_espacios_en_blanco():
    v = voz_por_anclas(TEXTO, ["Uno  dos\ttres.", "Siete ocho. Nueve diez"])
    assert v[1].startswith("Siete ocho.\n\nNueve diez")
    # otra diferencia (mayúsculas, puntuación) ya no es el ancla
    v2 = voz_por_anclas(TEXTO, ["Uno dos tres.", "siete ocho"])
    assert v2[1] == "siete ocho"


def test_c_clip_primero_cubre_lo_previo_a_la_primera_supp():
    # el ancla del clip no tiene que estar al inicio: el clip arranca en el inicio del texto
    v = voz_por_anclas(TEXTO, ["ancla del clip con números normalizados", "Siete ocho.", "Doce trece."],
                       primero_desde_inicio=True)
    assert v[0] == "Uno dos tres. Cuatro cinco seis."
    assert v[1] == "Siete ocho.\n\nNueve diez once."
    assert v[2] == "Doce trece."


def test_c_clip_ultimo_desde_su_ancla():
    v = voz_por_anclas(TEXTO, ["Uno dos tres.", "Cuatro cinco seis.", "Nueve diez once."])
    assert v[-1] == "Nueve diez once. Doce trece."
    assert v[1] == "Cuatro cinco seis. Siete ocho."


def test_c_ancla_no_encontrada_es_solo_el_ancla():
    v = voz_por_anclas(TEXTO, ["Uno dos tres.", "No está en el texto.", "Nueve diez once."])
    assert v[1] == "No está en el texto."
    assert v[0] == "Uno dos tres. Cuatro cinco seis. Siete ocho."   # el anterior sigue hasta la siguiente encontrada
    assert voz_por_anclas(TEXTO, [None, ""]) == [None, ""]


def test_c_busca_en_orden():
    t = "Otra vez. Algo. Otra vez. Fin."
    v = voz_por_anclas(t, ["Otra vez.", "Algo.", "Otra vez."])
    assert v == ["Otra vez.", "Algo.", "Otra vez. Fin."]


def test_c_cobertura_100_sintetica():
    anclas = ["Uno dos tres.", "Cuatro cinco seis.", "Siete ocho.", "Nueve diez once.", "Doce trece."]
    assert _palabras(voz_por_anclas(TEXTO, anclas)) == len(TEXTO.split())
    assert _palabras(voz_por_anclas(TEXTO, ["x", "Siete ocho."], primero_desde_inicio=True)) == len(TEXTO.split())


def _topic(tmp_path, chapter, imgs, sub):
    tid = "t-f73c"
    (tmp_path / "data" / "scripts").mkdir(parents=True)
    (tmp_path / "data" / "scripts" / f"{tid}.json").write_text(
        json.dumps({"video_type": "long", "chapters": [chapter]}), encoding="utf-8")
    d = tmp_path / "output" / tid / "assets" / sub
    d.mkdir(parents=True)
    for name in imgs:
        (d / name).write_bytes(b"\x89PNG")
    return q.QAState(tid, base_dir=tmp_path)


def test_c_cap_flux_segmentos_llevan_voz(tmp_path):
    ch = {"chapter_number": 1, "narration": TEXTO,
          "image_prompts": [{"narration_anchor": "Uno dos tres."}, {"narration_anchor": "Nueve diez once."}]}
    st = _topic(tmp_path, ch, ["ch01_img_01.png", "ch01_img_02.png"], "ch01_flux")
    segs = st.cap(1)["segments"]
    assert [s["voz"] for s in segs] == ["Uno dos tres. Cuatro cinco seis. Siete ocho.", "Nueve diez once. Doce trece."]
    assert [s["anchor"] for s in segs] == ["Uno dos tres.", "Nueve diez once."]   # el ancla no cambia


def test_c_cap_veo_end_clip_desde_su_ancla(tmp_path):
    ch = {"chapter_number": 1, "narration": TEXTO, "render_engine": "veo", "veo_position": "end",
          "narration_anchor": "Nueve diez once.",
          "supplemental_image_prompts": [{"narration_anchor": "Uno dos tres."}]}
    st = _topic(tmp_path, ch, ["ch01_supp_01.png"], "ch01_flux")
    segs = st.cap(1)["segments"]
    assert segs[-1]["is_clip"] and segs[-1]["voz"] == "Nueve diez once. Doce trece."
    assert segs[0]["voz"] == "Uno dos tres. Cuatro cinco seis. Siete ocho."
