"""
test_module_f8b.py — F8b (HANDOFF_F8b_F9 §1–§2): arreglos de research v3 y reglas de imagen + grade de post.
"""
from __future__ import annotations

import pytest

from researcher_steps import research_v3 as r3

# ═══════════════════════════════════════════════════════════════
#  §1.1 — antigüedad por ítem, no por documento
# ═══════════════════════════════════════════════════════════════


def test_documentos_de_2014_a_2023_sobre_1963_entran():
    for anio in (2014, 2019, 2023):
        assert r3.doc_contamination({"nombra_evento": True, "anio": anio}, 1963) is None
    assert r3.doc_contamination({"nombra_evento": False, "anio": 1964}, 1963)


def test_antiguedad_por_item_con_excepciones():
    assert r3.contamination({"fecha": "1963-10-09", "texto": "la ola"}, 1963) is None
    assert r3.contamination({"fecha": "2014-05-01", "texto": "una mostra fotografica a Roma"}, 1963)
    assert r3.contamination({"fecha": "1997-03-25", "texto": "La sentenza della Cassazione"}, 1963) is None
    assert r3.contamination({"fecha": "2013-10-09", "evento": "Cerimonia per il 50° anniversario"}, 1963) is None
    assert r3.contamination({"fecha": "1930-01-01", "texto": "un hecho cualquiera"}, 1963)
    assert r3.contamination({"fecha": "1929-01-01", "texto": "La SADE ottiene la concessione"}, 1963) is None
    assert r3.contamination({"fecha": "2026-03-01"}, 2005).startswith("fecha 2026")      # Orleans: igual que antes


def test_merge_con_documentos_retrospectivos():
    docs = [{"id": "F01", "anio": 2023, "nombra_evento": True, "tipo": "prensa_posterior", "url": "https://x.it/a"},
            {"id": "F02", "anio": 2014, "nombra_evento": True, "tipo": "academico", "url": "https://y.it/b"}]
    item = {"texto": "La frana del Toc cadde nel lago", "tipo": "magnitud", "fecha": "1963-10-09", "offset": 0,
            "cita_literal": "la frana del Toc"}
    per_doc = {"F01": {"datos": [dict(item)]}, "F02": {"datos": [dict(item, texto="Morirono quasi duemila persone",
                                                                         cita_literal="duemila")]}}
    pool = r3.merge_docs(per_doc, docs, event_year=1963)
    assert len(pool["datos"]) == 2 and not pool["_descartados"]


# ═══════════════════════════════════════════════════════════════
#  §1.2 — PDF enlazado que no nombra el evento
# ═══════════════════════════════════════════════════════════════

def test_pdf_enlazado_sin_el_evento_se_descarta(tmp_path, monkeypatch):
    portada = b"<html><body><p>Cromanon: las pericias</p><a href='/folleto.pdf'>pdf</a></body></html>"
    calls = []

    def get(url):
        calls.append(url)
        if url.endswith(".pdf"):
            return 200, b"%PDF-1.4 fake", "application/pdf", url
        return 200, portada, "text/html", url
    monkeypatch.setattr(r3, "pdf_to_text", lambda p: "Perfil editorial. Sumario. Productos. " * 400)
    monkeypatch.setattr(r3, "html_to_text", lambda c: "corta")
    monkeypatch.setattr(r3.time, "sleep", lambda s: None)
    f = [{"id": "F05", "slug": "perfil_2008", "url": "https://www.perfil.com/nota.phtml", "titulo": "Cromañón: pericias",
          "tipo": "prensa_posterior", "anio": 2008, "prioridad": 1}]
    log: list[str] = []
    man = r3.download_sources(f, tmp_path, place_re=r"\bCroma[ñn][oó]n\b", get=get, wayback=False, log=log)
    d = man["documentos"][0]
    assert not d["ok"] and any("PDF enlazado descartado" in x for x in log)
    assert any(c.endswith("folleto.pdf") for c in calls)


def test_pdf_enlazado_con_el_evento_entra(tmp_path, monkeypatch):
    def get(url):
        if url.endswith(".pdf"):
            return 200, b"%PDF-1.4 fake", "application/pdf", url
        return 200, b"<html><a href='/pericias.pdf'>pdf</a></html>", "text/html", url
    monkeypatch.setattr(r3, "pdf_to_text", lambda p: "Pericias del incendio de Cromañón. " * 200)
    monkeypatch.setattr(r3, "html_to_text", lambda c: "corta")
    monkeypatch.setattr(r3.time, "sleep", lambda s: None)
    f = [{"id": "F05", "slug": "perfil_2008", "url": "https://www.perfil.com/nota.phtml", "titulo": "x",
          "tipo": "prensa_posterior", "anio": 2008, "prioridad": 1}]
    man = r3.download_sources(f, tmp_path, place_re=r"\bCroma[ñn][oó]n\b", get=get, wayback=False)
    assert man["documentos"][0]["ok"] and man["documentos"][0]["via"] == "pdf_enlazado"


# ═══════════════════════════════════════════════════════════════
#  §1.3 — R3 con reintento; si no, extraccion_fallida
# ═══════════════════════════════════════════════════════════════

def _doc():
    return {"id": "F08", "titulo": "Clarín 2006", "tipo": "prensa_posterior", "anio": 2006, "fuente": "Clarín"}


def test_r3_reintenta_ante_una_caida_de_pro(monkeypatch):
    monkeypatch.setattr(r3, "R3_BACKOFF_S", 0.0)
    n = {"k": 0}

    def call(prompt, **kw):
        n["k"] += 1
        if n["k"] < 3:
            raise RuntimeError("RemoteProtocolError: Server disconnected")
        return {}
    out = r3.extract_document({"seed_title": "Cromañón"}, _doc(), "texto del documento " * 50, call=call)
    assert n["k"] == 3 and "_extraccion_fallida" not in out


def test_r3_marca_extraccion_fallida_y_sigue(monkeypatch):
    monkeypatch.setattr(r3, "R3_BACKOFF_S", 0.0)

    def call(prompt, **kw):
        raise RuntimeError("Server disconnected")
    log: list[str] = []
    out = r3.extract_document({"seed_title": "Cromañón"}, _doc(), "texto " * 50, call=call, log=log)
    assert out["_extraccion_fallida"][0]["parte"] == 1 and out["datos"] == []
    assert any("extracción fallida" in x for x in log)


# ═══════════════════════════════════════════════════════════════
#  §1.4 — R1: reintentos y Flash con búsqueda; focos con grounding
# ═══════════════════════════════════════════════════════════════

def test_r1_flash_alternativo_y_conteo_de_focos():
    pro_calls, alt_calls = [], []

    def search(prompt):
        pro_calls.append(prompt)
        if "informes completos" in prompt:         # foco 1: Pro sí busca
            return '{"fuentes": []}', [{"uri": "https://a.org/x", "title": "a"}]
        return '{"fuentes": []}', []

    def alt(prompt):
        alt_calls.append(prompt)
        return '{"fuentes": []}', [{"uri": "https://b.it/y", "title": "b"}] if "fallos" in prompt else []
    seed = {"seed_title": "Vajont", "lugar_idioma": "italiano", "nombres_lugar": ["Diga del Vajont", "Longarone"]}
    out = r3.discover_sources(seed, search=search, search_alt=alt, resolve=lambda u: u, annotate=lambda *a, **k: {})
    fg = out["_focos_grounding"]
    assert fg == {"pro": 1, "flash": 1, "sin": 2}
    assert len(pro_calls) == 1 + 3 * (1 + r3.R1_RETRIES) and r3.R1_RETRIES == 3
    assert len(alt_calls) == 3 and all('"Diga del Vajont"' in p and "italiano" in p for p in alt_calls)


# ═══════════════════════════════════════════════════════════════
#  §2.1–§2.5 — reglas de imagen
# ═══════════════════════════════════════════════════════════════

from script_engine import m03_imagenes_v3 as v3  # noqa: E402
from script_engine import m03_visual as m3  # noqa: E402
from test_module_f8 import BEATS, NARR, _topic_f8, fake_llm  # noqa: E402,F401


def test_armas_nunca_fogonazo_ni_primera_persona():
    for bad in ("A sniper rifle erupts in a muzzle flash.", "A first-person view down the rifle's barrel.",
                "Officers firing from a rooftop.", "The gunman aims straight at the camera.", "POV of the shooter",
                "A deputy prone on a rooftop with a long rifle.", "A distant figure aiming a rifle at the street."):
        assert any(k == "arma" for k, _ in v3.problems(bad)), bad
    ok = "Still silhouettes of deputies on a far rooftop, rifles at rest, seen from behind."
    assert not [k for k, _ in v3.problems(ok) if k == "arma"]
    assert "muzzle" not in v3.scrub_sentence_problems("A flooded cell. A muzzle flash lights the window. Water rises.")


def test_beat_de_arma_se_cuenta_desde_las_victimas():
    assert v3.weapon_subject({"subject": "a silhouetted sniper on a rooftop", "action": "lying still"})
    assert not v3.weapon_subject({"subject": "inmates crouching in the water", "action": "ducking"})
    b = [{"n": 5, "imagen_sensorial": "El fogonazo de un rifle desde un techo", "funcion": "pico"}]
    assert "WEAPON BEAT" in v3.beats_block(b, [{"beat": 5, "cerrada": False}])
    assert "victims or the witness" in m3.F8_NOTE_ARMA


def test_pico_a_escala_humana():
    assert not v3.human_scale({"subject": "the barrel of a sniper rifle", "props_detail": "smoke"})
    assert v3.human_scale({"subject": "inmates crouching in the water", "props_detail": ""})
    assert v3.human_scale({"subject": "an empty bunk", "props_detail": "a pair of shoes"})
    assert "HUMAN scale" in m3.F8_NOTE_CERRADA


def test_texto_en_el_idioma_del_lugar():
    it = {"text_in_image": {"present": True, "text": "desconocido", "font": "typed", "location": "list"}}
    assert v3.fix_text_slot(it, "en") and it["text_in_image"]["present"] is False and it["texto_en_imagen"] is False
    it = {"text_in_image": {"present": True, "text": "ORLEANS PARISH PRISON INMATE LIST", "font": "x", "location": "y"}}
    v3.fix_text_slot(it, "en")
    assert it["text_in_image"]["text"] == "ORLEANS PARISH PRISON" and it["texto_en_imagen"] is True
    assert v3.place_language({"evidence_pool": {"_research_v3": {"documentos": [{"idioma": "en"}, {"idioma": "en"},
                                                                                 {"idioma": "es"}]}}}) == "en"
    assert v3.place_language({"idioma_local": "italiano (Longarone)"}) == "it"
    si = m3.SYSTEM_INSTRUCTION_VISUAL_SEEDREAM_V3
    assert "IN SPANISH" not in si and "LANGUAGE OF THE PLACE" in si


def test_escala_desde_el_pool():
    b = {"imagen_sensorial": "Hombres con monos naranjas sentados en el asfalto", "dato_texto": "Unos 6,375 presos"}
    assert v3.beat_scale(b)
    assert not v3.beat_scale({"imagen_sensorial": "una celda vacía", "dato_texto": "6,375 presos"})
    assert v3.fix_scale("A wide shot of a few inmates sitting on the overpass.").startswith("A wide shot of hundreds of")


def test_cliches_ampliados():
    for c in ("hollowed eyes", "cracked lips", "facial muscles tensed", "eyes squeezed shut", "a grimace", "bulging veins"):
        assert any(k == "manos/cara" for k, _ in v3.problems(f"A man with {c} in a cell.")), c
    assert "cracked lips" not in m3.SYSTEM_INSTRUCTION_VISUAL_SEEDREAM_V3


def test_render_v3_sin_texto_por_defecto(fake_llm):
    plan = {"anchors": [{"anchor": a} for a in ["Primer párrafo del beat uno", "Sigue el agua",
                                                   "Segundo párrafo, el pico", "Tercer párrafo, respiro"]]}
    topic = _topic_f8()
    topic["_f8"]["lang"] = "en"
    out = m3._render_prompts_seedream(topic, {"chapter_number": 5}, NARR, plan, 5)
    assert all(v3.NO_TEXT in i["prompt"] for i in out["image_prompts"])
    assert all(i["texto_en_imagen"] is False for i in out["image_prompts"])
    assert "Language of the place of the event" in fake_llm["prompts"][0] and "English" in fake_llm["prompts"][0]


# ═══════════════════════════════════════════════════════════════
#  §2.6 — grade de post
# ═══════════════════════════════════════════════════════════════

def _img(path):
    from PIL import Image, ImageDraw
    im = Image.new("RGB", (320, 180), (200, 60, 30))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 100, 180], fill=(0, 0, 0))               # negro puro
    d.rectangle([220, 0, 320, 180], fill=(40, 90, 200))
    im.save(path)
    return path


def test_grade_baja_saturacion_y_no_recorta_negros(tmp_path):
    from script_engine import image_grade as g
    src = _img(tmp_path / "ch02_img_01.png")
    dst = g.grade(src)
    assert dst.name == "ch02_img_01_graded.png" and src.exists()
    a, b = g.stats(src), g.stats(dst)
    assert b["sat_media"] < 0.85 * a["sat_media"]                   # ≥ 15 % menos saturada
    assert a["negro_puro_pct"] > 20 and b["negro_puro_pct"] == 0 and b["luma_min"] >= 3
    assert g.grade(src) == dst                                      # no rehace si ya existe


def test_asset_manager_aplica_el_grade_solo_en_v3(tmp_path, monkeypatch):
    import asset_manager as am
    monkeypatch.setattr(am, "OUTPUT_DIR", tmp_path)
    monkeypatch.delenv("IMAGE_GRADE", raising=False)
    (tmp_path / "v" / "assets" / "ch02_flux").mkdir(parents=True)
    _img(tmp_path / "v" / "assets" / "ch02_flux" / "ch02_img_01.png")
    v2 = {"chapters": [{"image_prompts": [{"prompt": "x"}]}]}
    v3s = {"chapters": [{"image_prompts": [{"prompt": "x", "sensible": False}]}]}
    assert not am._grade_enabled(v2) and am._grade_enabled(v3s)
    monkeypatch.setenv("IMAGE_GRADE", "0")
    assert not am._grade_enabled(v3s)
    res = [{"images": [{"path": "v/assets/ch02_flux/ch02_img_01.png", "status": "ok"}]}]
    assert am._apply_grade(res) == 1
    img = res[0]["images"][0]
    assert img["path"].endswith("ch02_img_01_graded.png") and img["path_original"].endswith("ch02_img_01.png")
    assert am._apply_grade(res) == 0                                # idempotente
