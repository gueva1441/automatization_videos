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
           "evidence_zoom": {"use": True, "scene_idx": 0, "anchor_word_idx": 1, "anchor_len": 2},
           "count_up": {"use": True, "fact_idx": 2, "value": "6,500", "unit": "personas", "trigger_word_idx": 13},
           "punch_in_word_idx": [10]}
    plan = _run(monkeypatch, tmp_path, raw)
    assert plan["callouts"][0]["text"] == "4.6 metros"
    assert plan["archive_clippings"][0]["scene_idx"] == 2    # compat: objeto F1 → lista F2
    assert plan["evidence_zoom"]["anchor"] == "día el" and plan["evidence_zoom"]["box"] is None   # F2b §1.2
    assert plan["archive_clippings"][0]["headline"] == "partes de Nueva Orleans quedaron bajo 15 pies"  # §1.1
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
           "evidence_zoom": {"use": True, "scene_idx": 2, "anchor_word_idx": 20, "anchor_len": 1},
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


def test_titular_lo_arma_el_validador_no_el_llm(monkeypatch, tmp_path):
    """F2b §1.1: lo que mande el LLM como headline se ignora; el titular sale del fact (≤ 8 palabras, con la cifra)."""
    raw = {"archive_clippings": [{"fact_idx": 2, "scene_idx": 2, "kicker": "inventado",
                                  "headline": "Seis mil almas en el agua"}]}
    monkeypatch.setattr(gd, "call_flash_json", lambda *a, **k: raw)
    plan = gd.select_gfx_plan(CHPLAN, ctx=CTX, words=WORDS, scenes=SCENES, work_dir=tmp_path)
    ar = plan["archive_clippings"][0]
    assert ar["headline"] == "Aproximadamente 6,500 personas estaban encarceladas en la Prisión"
    assert ar["kicker"] == ""                                   # sin fuente ni año en el fact


@pytest.mark.parametrize("fact,head", [
    ("Aproximadamente 6,500 personas, incluyendo hombres, mujeres y niños, estaban encarceladas.", "Aproximadamente 6,500 personas"),
    ("Más de 500 prisioneros no figuraban en la lista de personas evacuadas de la cárcel, según Human Rights Watch.",
     "Más de 500 prisioneros no figuraban"),
    ("El huracán Katrina tocó tierra el 29 de agosto de 2005.", "El huracán Katrina tocó tierra"),   # día ≠ cifra
    ("El agua dentro de algunos edificios de la Prisión Parroquial de Orleans (OPP), como Templeman 1 y 2, alcanzó el nivel del pecho.",
     "El agua dentro de algunos edificios"),
    ("Había niños de hasta 10 años en la prisión; la población juvenil era abrumadoramente afroamericana (98.7% en el CYC y 95% en el YSC).",
     "Había niños de hasta 10 años"),
])
def test_build_headline_literal_y_corto(fact, head):
    out = gd.build_headline(fact)
    assert out == head and gd._literal_in(out, fact) and len(out.split()) <= 8


def test_kicker_fuente_o_anio():
    assert gd.build_kicker("x en 2005", "Human Rights Watch, 2005", "x") == "Human Rights Watch, 2005"
    assert gd.build_kicker("pasó en 2005 algo", "", "pasó") == "2005"
    assert gd.build_kicker("pasó en 2005 algo", "", "pasó en 2005") == ""      # el año ya está en el titular


def test_zoom_sin_ancla_en_su_escena_no_va(monkeypatch, tmp_path):
    """F2b §1.2: la frase ancla tiene que decirse dentro de la escena del zoom (± 1 s)."""
    raw = {"evidence_zoom": {"use": True, "scene_idx": 0, "anchor_word_idx": 20, "anchor_len": 1}}   # "almas" @ 20 s
    log: list[str] = []
    monkeypatch.setattr(gd, "call_flash_json", lambda *a, **k: raw)
    plan = gd.select_gfx_plan(CHPLAN, ctx=CTX, words=WORDS, scenes=SCENES, work_dir=tmp_path, log=log)
    assert plan["evidence_zoom"] is None and any("frase ancla" in m for m in log)


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


def test_seis_callouts_quedan_cinco_y_texto_no_literal_se_descarta(monkeypatch, tmp_path):
    cs = [{"fact_idx": 1, "text": "4.6 metros", "trigger_word_idx": i, "kind": "figure"} for i in range(6)]
    cs.append({"fact_idx": 1, "text": "cinco metros", "trigger_word_idx": 3, "kind": "figure"})  # no literal
    plan = _run(monkeypatch, tmp_path, {"callouts": cs})
    assert len(plan["callouts"]) == 5                       # F2 §1: techo 5/cap
    assert all(c["text"] == "4.6 metros" for c in plan["callouts"])


def test_omision_por_text_in_image(monkeypatch, tmp_path):
    raw = {"callouts": [{"fact_idx": 0, "text": "29 de agosto de 2005", "trigger_word_idx": 3, "kind": "year"}]}
    plan = _run(monkeypatch, tmp_path, raw)
    res = gd.resolve_plan(plan, ctx=CTX, words=WORDS, scenes=SCENES)
    assert all(c["text"] != "29 de agosto de 2005" for c in res["callouts"])   # escena 0 ya muestra "AGOSTO 2005"


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


def test_hueco_lo_rellena_el_validador_con_texto_literal():
    """F2 §1: hueco > 35 s → callout con un fragmento LITERAL de un fact que la voz dice en el tramo;
    lo que no se puede tapar (sin palabras) queda como gap_warning (métrica)."""
    long_scenes = [GfxScene(0, 0.0, 90.0, "R3", "")]
    log = []
    res = gd.resolve_plan({"title_card": {"use": True}}, ctx=CTX, words=WORDS, scenes=long_scenes, log=log)
    assert res["callouts"] and any("gap_fill: callout" in l for l in log)
    assert all(any(c["text"] in f for f in FACTS) for c in res["callouts"])   # nunca texto inventado
    assert all(c.get("gap_fill") for c in res["callouts"])
    assert res["gap_warnings"]                                  # 20–90 s sin palabras: no se puede tapar


def test_hueco_sin_fact_dicho_pone_punch_in():
    words = [{"word": w, "start": float(i), "end": float(i) + .9} for i, w in enumerate(
        ("Las paredes guardaban silencio mientras el agua subía " * 8).split())]
    scenes = [GfxScene(0, 0.0, 60.0, "R3", "")]
    log = []
    res = gd.resolve_plan({}, ctx={**CTX, "eligible": {}}, words=words, scenes=scenes, log=log)
    assert res["callouts"] == [] and res["punch_in"] and any("gap_fill: punch_in" in l for l in log)
    assert res["gap_warnings"] == []


def _orleans():
    import json
    from pathlib import Path
    d = json.loads((Path(__file__).parent / "data/scripts/ba6c3cac-a091-41c0-8dad-afd2f4364747.json").read_text(encoding="utf-8"))
    return [f["fact"] for f in d["verified_facts"]], d["chapters"]


def test_epoca_el_fact_de_2010_no_cae_en_ch02():
    facts, chapters = _orleans()
    i2010 = next(i for i, f in enumerate(facts) if "2010" in f)
    elig, era = gd.eligible_facts(facts, chapters, 2, chapters[1]["narration"])
    assert era == [2004, 2006] and i2010 not in elig
    elig6, _ = gd.eligible_facts(facts, chapters, 6, chapters[5]["narration"])
    assert i2010 in elig6                                       # en su cap sí


def test_facts_por_cap_y_foraneos():
    facts = ["Juan Pérez llegó en 1990 a la isla.", "El faro de Punta Gris se apagó en 1991.",
             "La familia Ortiz vendió el barco en 1992."]
    chapters = [{"chapter_number": 1, "narration": "Todo empezó cuando Juan Pérez llegó.", "image_prompts": []},
                {"chapter_number": 2, "narration": "Nadie sabe por qué pasó.", "image_prompts": [{"hard_fact_ids": ["F02"]}]},
                {"chapter_number": 3, "narration": "El final llegó con la familia Ortiz.", "image_prompts": [{"hard_fact_ids": ["F03"]}]}]
    elig, _ = gd.eligible_facts(facts, chapters, 2, chapters[1]["narration"])
    assert elig[1] is False                                     # propio por hard_fact_ids
    assert elig.get(2) is True                                  # < 2 propios → vecino foráneo
    plan = gd.validate_plan({"archive_clippings": [{"fact_idx": 2, "scene_idx": 0, "headline": "vendió el barco", "kicker": ""}],
                             "callouts": [{"fact_idx": 2, "text": "1992", "trigger_word_idx": 0, "kind": "year"}]},
                            n_facts=3, n_words=5, scenes=[GfxScene(0, 0, 10)], facts=facts, eligible=elig)
    assert plan["archive_clippings"] == [] and plan["callouts"][0]["foreign"]     # foráneo: solo callout


def test_anti_spoiler_en_ch01():
    facts, chapters = _orleans()
    i2010 = next(i for i, f in enumerate(facts) if "2010" in f)      # F07: solo aparece en ch06
    elig, _ = gd.eligible_facts(facts, chapters, 1, chapters[0]["narration"] + " Robie Waganfeald")
    assert i2010 not in elig


def test_titular_nunca_substring_del_cuerpo():
    log: list[str] = []
    fact = "Más de 500 prisioneros no figuraban en la lista. Según Human Rights Watch, nadie los buscó."
    head, body = gd.headline_vs_body("Más de 500 prisioneros", "Más de 500 prisioneros no figuraban en la lista.",
                                     "Human Rights Watch", fact, log)
    assert body == "" and head == "Más de 500 prisioneros"      # kicker + año no es literal → sin cuerpo
    fact2 = "El informe de Human Rights Watch 2005 dice que más de 500 prisioneros no figuraban."
    head2, _ = gd.headline_vs_body("más de 500 prisioneros", "más de 500 prisioneros no figuraban.",
                                   "Human Rights Watch", fact2, log)
    assert head2 == "Human Rights Watch 2005"


def test_zoom_box_null_sin_zoom(tmp_path):
    import unittest.mock as um
    plan = {"evidence_zoom": {"scene_idx": 0, "anchor": "la herida", "box": None}}
    log: list[str] = []
    with um.patch.object(gd, "judge_zoom_box", return_value={"box": None, "confianza": 0.0, "detalle": "solo cielo"}):
        out = gd.apply_zoom_vision(plan, frame_for_scene=lambda si: tmp_path / "f.jpg",
                                   cache=tmp_path / "zb.json", log=log)
    assert out["evidence_zoom"] is None and any("visión" in l for l in log)
    with um.patch.object(gd, "judge_zoom_box", side_effect=AssertionError("no debe re-llamar")):
        again = gd.apply_zoom_vision(plan, frame_for_scene=lambda si: None, cache=tmp_path / "zb.json", log=log)
    assert again["evidence_zoom"] is None                       # cacheado
    with um.patch.object(gd, "judge_zoom_box", return_value={"box": [0.5, 0.5, 0.1, 0.1], "confianza": 0.9, "detalle": "candado"}):
        ok = gd.apply_zoom_vision({"evidence_zoom": {"scene_idx": 1, "anchor": "el candado", "box": None}},
                                  frame_for_scene=lambda si: tmp_path / "f.jpg", cache=tmp_path / "zb.json", log=log)
    assert ok["evidence_zoom"]["box"] == [0.5, 0.5, 0.1, 0.1]
    # F2b §1.2: confianza bajo el umbral → sin zoom aunque haya box
    with um.patch.object(gd, "judge_zoom_box", return_value={"box": [0.5, 0.5, 0.1, 0.1], "confianza": 0.4, "detalle": "dudoso"}):
        low = gd.apply_zoom_vision({"evidence_zoom": {"scene_idx": 2, "anchor": "la mano", "box": None}},
                                   frame_for_scene=lambda si: tmp_path / "f.jpg", cache=tmp_path / "zb.json", log=log)
    assert low["evidence_zoom"] is None


def test_cache_de_version_anterior_se_re_llama(monkeypatch, tmp_path):
    import json
    (tmp_path / "gfx_plan_ch02.json").write_text(json.dumps({"raw": {"callouts": []}}), encoding="utf-8")
    calls = []
    monkeypatch.setattr(gd, "call_flash_json", lambda *a, **k: calls.append(1) or {"title_card": {"use": True}})
    gd.select_gfx_plan(CHPLAN, ctx=CTX, words=WORDS, scenes=SCENES, work_dir=tmp_path)
    assert calls and json.loads((tmp_path / "gfx_plan_ch02.json").read_text(encoding="utf-8"))["director"] == gd.DIRECTOR_VERSION


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
