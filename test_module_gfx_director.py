"""test_module_gfx_director.py — F1 capa gráfica: director con Flash MOCKEADO.
(a) plan válido · (b) índices fuera de rango · (c) 6 callouts → ≤3 · nunca lanza.
Correr: python -m pytest test_module_gfx_director.py -q
"""
import sys
from types import SimpleNamespace

import pytest

import script_engine.gfx_director as gd
from script_engine.gfx_project import GfxScene

FACTS = [
    "El huracán Katrina tocó tierra el 29 de agosto de 2005.",
    "Algunas partes de Nueva Orleans quedaron bajo 15 pies (4.6 metros) de agua.",
    "Aproximadamente 6,500 personas estaban encarceladas en la Prisión de Orleans Parish (OPP).",
]
WORDS = [{"word": w, "start": float(i), "end": float(i) + .9} for i, w in enumerate(
    "Ese día el 29 de agosto de 2005 Katrina llegó y el agua subió 4.6 metros sobre seis mil quinientas almas".split())]
SCENES = [GfxScene(0, 0.0, 8.0, "R3", "AGOSTO 2005"), GfxScene(1, 8.0, 20.0, "R2", ""),
          GfxScene(2, 20.0, 40.0, "R3", "")]
CTX = {"chapter_number": 2, "facts": FACTS, "skeleton": {"title": "La Tormenta Perfecta", "bullets": []},
       "script_chapter": {"image_prompts": []}, "sources": {}}
CHPLAN = SimpleNamespace(chapter_id="ch02")


def _run(monkeypatch, tmp_path, raw):
    monkeypatch.setattr(gd, "call_flash_json", lambda *a, **k: raw)
    return gd.select_gfx_plan(CHPLAN, ctx=CTX, words=WORDS, scenes=SCENES, work_dir=tmp_path)


def test_plan_valido(monkeypatch, tmp_path):
    raw = {"title_card": {"use": True},
           "callouts": [{"fact_idx": 1, "text": "4.6 metros", "trigger_word_idx": 10, "kind": "figure"}],
           "archive_clipping": {"use": True, "fact_idx": 1, "scene_idx": 2, "headline": "quedaron bajo 15 pies", "kicker": "Nueva Orleans"},
           "evidence_zoom": {"use": True, "scene_idx": 0, "box": [0.4, 0.6, 0.15, 0.2]},
           "count_up": {"use": True, "fact_idx": 2, "value": "6,500", "unit": "personas", "trigger_word_idx": 13},
           "punch_in_word_idx": [10]}
    plan = _run(monkeypatch, tmp_path, raw)
    assert plan["callouts"][0]["text"] == "4.6 metros"
    assert plan["archive_clippings"][0]["scene_idx"] == 2    # compat: objeto F1 → lista F2
    assert plan["evidence_zoom"]["box"] == [0.4, 0.6, 0.15, 0.2]
    assert plan["count_up"]["value"] == "6,500"
    assert (tmp_path / "gfx_plan_ch02.json").exists()      # cache
    res = gd.resolve_plan(plan, ctx=CTX, words=WORDS, scenes=SCENES)
    assert res["title_card"] == {"kicker": "CAPÍTULO 2", "title": "La Tormenta Perfecta"}
    assert res["callouts"][0]["start"] == 10.0
    ar = res["archive_clippings"][0]
    assert ar["body"] == "" and ar["duration"] == 6.0 and ar["start"] == 20.5   # F2: 6 s; 13 palabras sin corte ≤ 12 → sin cuerpo
    assert res["count_up"]["start"] == 13.0
    assert res["callouts"][0]["duration"] == 2.5                # F1b: mínimo 2.5 s
    # F2 §0b.5: el zoom ocupa el FINAL de su escena (escena 0 termina en 8.0)
    assert res["evidence_zoom"]["start"] == pytest.approx(8.0 - gd.gfx_rules.zoom_dur)
    assert all(c["side"] in ("left", "right") for c in res["callouts"])


def test_cache_ida_y_vuelta_no_pierde_bloques(monkeypatch, tmp_path):
    raw = {"title_card": {"use": True},
           "archive_clipping": {"use": True, "fact_idx": 1, "scene_idx": 2, "headline": "quedaron bajo 15 pies", "kicker": ""},
           "evidence_zoom": {"use": True, "scene_idx": 2, "box": [0.4, 0.6, 0.15, 0.2]},
           "count_up": {"use": True, "fact_idx": 2, "value": "6,500", "unit": "personas", "trigger_word_idx": 12}}
    first = _run(monkeypatch, tmp_path, raw)
    def boom(*a, **k):
        raise AssertionError("con cache no debe llamar a Gemini")
    monkeypatch.setattr(gd, "call_flash_json", boom)
    again = gd.select_gfx_plan(CHPLAN, ctx=CTX, words=WORDS, scenes=SCENES, work_dir=tmp_path)
    assert again == first and again["archive_clippings"] and again["evidence_zoom"] and again["count_up"]


def test_callout_dura_hasta_fin_de_frase():
    words = [{"word": w, "start": float(i), "end": float(i) + .9} for i, w in enumerate(
        "bajo hasta 4.6 metros o quince pies de agua putrefacta. En medio".split())]
    # trigger en "4.6" (idx 2): la frase termina en "putrefacta." (idx 8, end 8.9) → 6.9 s > 0.4·2+1
    assert gd.callout_duration("4.6 metros", 2, words) == pytest.approx(6.0)   # recortado al máximo 6.0
    assert gd.callout_duration("4.6 metros", 2, words[:5] + [{"word": "metros.", "start": 5.0, "end": 5.5}]) == pytest.approx(3.5)


def test_hasta_dos_recortes_y_callouts_alternan_lado(monkeypatch, tmp_path):
    long_fact = "Algunas partes de Nueva Orleans quedaron bajo 15 pies (4.6 metros) de agua."
    scenes = [GfxScene(0, 0.0, 8.0, "R3", "", "right"), GfxScene(1, 8.0, 20.0, "R2", "", "right"),
              GfxScene(2, 20.0, 40.0, "R3", "", "left")]
    raw = {"title_card": {"use": True},
           "callouts": [{"fact_idx": 1, "text": "4.6 metros", "trigger_word_idx": 10, "kind": "figure"},
                        {"fact_idx": 2, "text": "6,500 personas", "trigger_word_idx": 14, "kind": "figure"}],
           "archive_clippings": [{"fact_idx": 1, "scene_idx": 0, "headline": "quedaron bajo 15 pies", "kicker": ""},
                                 {"fact_idx": 2, "scene_idx": 2, "headline": "6,500 personas", "kicker": ""},
                                 {"fact_idx": 0, "scene_idx": 1, "headline": "29 de agosto de 2005", "kicker": ""}]}
    monkeypatch.setattr(gd, "call_flash_json", lambda *a, **k: raw)
    plan = gd.select_gfx_plan(CHPLAN, ctx=CTX, words=WORDS, scenes=scenes, work_dir=tmp_path)
    assert len(plan["archive_clippings"]) == 2                       # máx 2 por cap
    res = gd.resolve_plan(plan, ctx=CTX, words=WORDS, scenes=scenes)
    sides = [c["side"] for c in res["callouts"]]
    assert sides == ["right", "left"]                                # nunca dos seguidos en la misma esquina
    assert res["archive_clippings"][-1]["side"] == "left"           # lado tranquilo de su escena


def test_count_up_gana_al_callout_de_la_misma_cifra(monkeypatch, tmp_path):
    """Regresión F2 §0b (ch02): callout «6,500 personas» y count_up en la misma palabra → va el count_up."""
    raw = {"callouts": [{"fact_idx": 2, "text": "6,500 personas", "trigger_word_idx": 13, "kind": "figure"}],
           "count_up": {"use": True, "fact_idx": 2, "value": "6,500", "unit": "personas", "trigger_word_idx": 13}}
    plan = _run(monkeypatch, tmp_path, raw)
    log: list[str] = []
    res = gd.resolve_plan(plan, ctx=CTX, words=WORDS, scenes=SCENES, log=log)
    assert res["count_up"] and res["count_up"]["start"] == 13.0
    assert res["callouts"] == [] and any("callout omitido" in m for m in log)


def test_cuerpo_del_recorte_corta_en_frase_completa():
    corto = "Más de 500 prisioneros no figuraban en la lista de personas evacuadas de la cárcel, según Human Rights Watch."
    assert gd.trim_body(corto, 25) == corto                               # 19 palabras: entero
    largo = ("Los presos quedaron encerrados durante días sin comida ni agua potable. " * 2 +
             "Nadie supo cuántos eran.").strip()
    out = gd.trim_body(largo)
    assert out.endswith(".") and len(out.split()) <= 25 and largo.startswith(out)   # oración entera, literal
    una = ("Los presos quedaron encerrados durante varios días en celdas inundadas, sin comida ni agua potable "
           "mientras los guardias abandonaban sus puestos y el agua seguía subiendo sin parar")
    out = gd.trim_body(una)                                                # una sola oración larga → corta en la coma
    assert out == "Los presos quedaron encerrados durante varios días en celdas inundadas"
    assert gd.trim_body(" ".join(["palabra"] * 40)) is None                # sin corte limpio → None


def test_recorte_sin_cuerpo_salvo_titular_corto():
    fact = "Más de 500 prisioneros no figuraban en la lista de personas evacuadas de la cárcel, según Human Rights Watch."
    assert gd.archive_body("Más de 500 prisioneros no figuraban", fact) == ""          # 6 palabras → sin cuerpo
    assert gd.archive_body("Más de 500 prisioneros", fact) == ""                       # 19 palabras sin corte ≤ 12
    fact2 = "Más de 500 prisioneros no figuraban en la lista. Según Human Rights Watch, nadie los buscó."
    assert gd.archive_body("Más de 500 prisioneros", fact2) == "Más de 500 prisioneros no figuraban en la lista."


def test_plantilla_sin_cuerpo_no_emite_ar_body(tmp_path):
    from script_engine.gfx_project import write_project
    (tmp_path / "public").mkdir()
    (tmp_path / "public" / "base.mp4").write_bytes(b"x")
    plan = {"chapter_number": 2, "title_card": None, "callouts": [], "count_up": None, "evidence_zoom": None,
            "punch_in": [], "archive_clippings": [{"kicker": "", "headline": "Más de 500 prisioneros no figuraban",
                                                   "body": "", "start": 1.0, "duration": 5.0, "side": "left"}]}
    write_project(plan, [GfxScene(0, 0.0, 10.0, "R3", "")], tmp_path, duration=10.0, width=2560, height=1440, fps=30)
    html = (tmp_path / "index.html").read_text(encoding="utf-8")
    assert 'id="ar0"' in html and 'class="ar-body"' not in html


def test_titular_de_mas_de_8_palabras_se_descarta(monkeypatch, tmp_path):
    raw = {"archive_clippings": [{"fact_idx": 2, "scene_idx": 2, "kicker": "",
                                  "headline": "Aproximadamente 6,500 personas estaban encarceladas en la Prisión de Orleans"}]}
    log: list[str] = []
    monkeypatch.setattr(gd, "call_flash_json", lambda *a, **k: raw)
    plan = gd.select_gfx_plan(CHPLAN, ctx=CTX, words=WORDS, scenes=SCENES, work_dir=tmp_path, log=log)
    assert plan["archive_clippings"] == [] and any("titular de 10 palabras" in m for m in log)


def test_zoom_en_escena_corta_no_va(monkeypatch, tmp_path):
    scenes = [GfxScene(0, 0.0, 2.5, "R3", ""), GfxScene(1, 2.5, 40.0, "R3", "")]
    raw = {"evidence_zoom": {"use": True, "scene_idx": 0, "box": [0.4, 0.4, 0.1, 0.1]}}
    monkeypatch.setattr(gd, "call_flash_json", lambda *a, **k: raw)
    plan = gd.select_gfx_plan(CHPLAN, ctx=CTX, words=WORDS, scenes=scenes, work_dir=tmp_path)
    assert plan["evidence_zoom"] is None                             # no entra acercar + sostener ≥ 1 s


def test_indices_fuera_de_rango(monkeypatch, tmp_path):
    raw = {"callouts": [{"fact_idx": 99, "text": "x", "trigger_word_idx": 1, "kind": "year"},
                        {"fact_idx": 0, "text": "2005", "trigger_word_idx": 999, "kind": "year"}],
           "archive_clipping": {"use": True, "fact_idx": 0, "scene_idx": 7, "headline": "29 de agosto", "kicker": ""},
           "evidence_zoom": {"use": True, "scene_idx": -1, "box": [0, 0, .1, .1]},
           "count_up": {"use": True, "fact_idx": 5, "value": "6,500", "unit": "", "trigger_word_idx": 1},
           "punch_in_word_idx": [500, -3, 2]}
    plan = _run(monkeypatch, tmp_path, raw)
    assert plan["callouts"] == [] and plan["archive_clippings"] == []
    assert plan["evidence_zoom"] is None and plan["count_up"] is None
    assert plan["punch_in_word_idx"] == [2]


def test_seis_callouts_quedan_tres_y_texto_no_literal_se_descarta(monkeypatch, tmp_path):
    cs = [{"fact_idx": 1, "text": "4.6 metros", "trigger_word_idx": i, "kind": "figure"} for i in range(6)]
    cs.append({"fact_idx": 1, "text": "cinco metros", "trigger_word_idx": 3, "kind": "figure"})  # no literal
    plan = _run(monkeypatch, tmp_path, {"callouts": cs})
    assert len(plan["callouts"]) == 3
    assert all(c["text"] == "4.6 metros" for c in plan["callouts"])


def test_omision_por_text_in_image(monkeypatch, tmp_path):
    raw = {"callouts": [{"fact_idx": 0, "text": "29 de agosto de 2005", "trigger_word_idx": 3, "kind": "year"}]}
    plan = _run(monkeypatch, tmp_path, raw)
    res = gd.resolve_plan(plan, ctx=CTX, words=WORDS, scenes=SCENES)
    assert res["callouts"] == []           # escena 0 ya muestra "AGOSTO 2005"


def test_gemini_caido_no_lanza(monkeypatch, tmp_path):
    def boom(*a, **k):
        raise RuntimeError("503")
    monkeypatch.setattr(gd, "call_flash_json", boom)
    plan = gd.select_gfx_plan(CHPLAN, ctx=CTX, words=WORDS, scenes=SCENES, work_dir=tmp_path)
    assert plan["title_card"] == {"use": True} and plan["callouts"] == []


def test_basura_no_lanza(monkeypatch, tmp_path):
    for raw in (None, [], "texto", {"callouts": "no-lista", "evidence_zoom": [1, 2]}):
        (tmp_path / "gfx_plan_ch02.json").unlink(missing_ok=True)
        plan = _run(monkeypatch, tmp_path, raw)
        assert isinstance(plan, dict)


def test_gap_warning_solo_loguea():
    long_scenes = [GfxScene(0, 0.0, 90.0, "R3", "")]
    log = []
    res = gd.resolve_plan({"title_card": {"use": True}}, ctx=CTX, words=WORDS, scenes=long_scenes, log=log)
    assert res["gap_warnings"] and any("gap_warning" in l for l in log)
    assert res["callouts"] == []           # no inventa bloques


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
