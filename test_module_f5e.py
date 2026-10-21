"""F5e (después de ver el video): sellos sin verbos ni neutras, un contador por hecho, titular hasta 12 palabras,
reservados con prioridad, marcas de QA Studio y [DATOS DE MAGNITUD] en el ángulo técnico. Sin red."""
from __future__ import annotations

from pathlib import Path

from script_engine import gfx_intensity as gi
from script_engine import gfx_pool as gp
from script_engine.gfx_project import GfxScene, archive_head_px

POOL = {"datos": [{"id": "D01", "texto": "517 reclusos no estaban contabilizados", "tipo": "cifra", "valor": "517"},
                  {"id": "D02", "texto": "más de 500 prisioneros no figuraban en la lista", "tipo": "cifra", "valor": "500"},
                  {"id": "D03", "texto": "Había 6,500 personas presas", "tipo": "cifra", "valor": "6,500"}],
        "cronologia": [], "citas": [], "lugares": [], "personajes": []}


def test_sellos_sin_verbos_ni_neutras():
    assert [w for w in ("murió", "flotando", "ahogarse", "subiera", "cadáveres", "atrapados", "suerte", "disentería")
            if gi.is_verb_form(w)] == ["murió", "flotando", "ahogarse", "subiera"]
    moods = {"muerte": {"triggers": {"murió": 2, "cadáveres": 3}, "icon_words": {"murió": "calavera"}}}
    out = gi.stamp_lexicon(moods)
    assert out["muerte"]["triggers"] == {"cadáveres": 3} and out["muerte"]["icon_words"] == {}
    raw = {"intensidad": [0.5], "pico_sentence_idx": 0, "cargas": [
        {"word": "estrella", "sentence_idx": 0, "categoria": "muerte", "peso": 3, "concreta": True,
         "clase": "sustantivo", "neutra": True},
        {"word": "cadáveres", "sentence_idx": 0, "categoria": "muerte", "peso": 3, "concreta": True,
         "clase": "sustantivo", "neutra": False},
        {"word": "flotaban", "sentence_idx": 0, "categoria": "muerte", "peso": 2, "concreta": False,
         "clase": "verbo", "neutra": False}]}
    res, why = gi.validate(raw, ["La estrella de los cadáveres que flotaban"], moods)
    assert [c["word"] for c in res["cargas"]] == ["cadáveres"] and any("neutra" in w for w in why)


def test_un_contador_por_hecho_con_la_cifra_precisa():
    g = gp.count_groups(POOL)
    assert len(g) == 1 and g[0]["canon"]["num"] == "517" and {"500", "517"} <= g[0]["nums"]
    chapters = [{"chapter_number": 5, "narration": "517 reclusos no estaban contabilizados."},
                {"chapter_number": 7, "narration": "Más de 500 prisioneros no figuraban."}]
    words5 = [{"word": w, "start": k * 0.4} for k, w in enumerate("Después 517 reclusos no estaban contabilizados.".split())]
    p5 = {"count_up": None, "callouts": []}
    gp.pool_count_up(p5, ctx={"pool": POOL, "chapter_number": 5, "chapters": chapters}, words=words5, time_offset=0, log=[])
    assert p5["count_up"]["value_text"] == "517" and p5["count_up"]["pool_id"] == "D01"
    p7 = {"count_up": {"value_text": "500", "unit": "prisioneros", "start": 3.0}, "callouts": [{"text": "500 prisioneros"}]}
    gp.pool_count_up(p7, ctx={"pool": POOL, "chapter_number": 7, "chapters": chapters}, words=[], time_offset=0, log=[])
    assert p7["count_up"] is None and p7["callouts"] == []                      # el mismo hecho ya se animó en el 5


def test_titular_hasta_12_palabras_con_cuerpo_menor():
    px8, k8 = archive_head_px("uno dos tres cuatro cinco seis siete ocho", 2560, 1440)
    px12, k12 = archive_head_px("uno dos tres cuatro cinco seis siete ocho nueve diez once doce", 2560, 1440)
    assert k8 == 0 and k12 >= 1 and px12 < px8


def test_recorte_se_corre_dentro_de_la_escena_y_reservado_sin_eco():
    sc = GfxScene(0, 0.0, 20.0)
    assert gp._free_slot(1.0, sc, 30.0, [(0.0, 3.0)], 6.0, 4.0) == (3.0, 9.0)
    assert gp._free_slot(1.0, sc, 30.0, [(0.0, 18.0)], 6.0, 4.0) is None
    sents = [{"text": "Primera oración del cap.", "t0": 0.0}, {"text": "Segunda oración.", "t0": 4.0}]
    it = {"texto": "Los reclusos reciben su última comida", "_kind": "cronologia", "fecha": "2005-08-27"}
    assert gp._sentence_for(it, sents, True) is None
    assert gp._sentence_for(it, sents, True, reserved=True)["t0"] == 4.0          # el reservado va igual


def test_marcas_de_qa_studio_y_regeneracion_con_otra_semilla(tmp_path):
    import qa_studio_server as qs

    class S:
        assets_dir = tmp_path / "assets"
        base = tmp_path

        def resolve_fix_entry(self, name):
            return {"prompt": "the same prompt", "art_profile": "", "subject_ref": "subject"}

        def resolve_image(self, cap, name):
            return None
    st = S()
    qs.set_mark(st, "ch02", "ch02_img_03.png", True)
    assert qs.load_marks(st)["marks"]["ch02_img_03.png"]["cap"] == "ch02"
    got = {}
    ok, why, seed = qs._reseed_core(st, "t", "ch02", "ch02_img_03.png", attempt=1, seed_fn=lambda v, s: 100,
                                    generate_fn=lambda p, a, out, use_ultra, seed: got.update(p=p, seed=seed),
                                    is_hook_fn=lambda c: False)
    assert ok and got == {"p": "the same prompt", "seed": 100 + qs.RESEED_STEP} and seed == got["seed"]
    qs.set_mark(st, "ch02", "ch02_img_03.png", False)
    assert qs.load_marks(st)["marks"] == {}


def test_m00_tecnico_pide_datos_de_magnitud():
    import topic_researcher as tr
    seed = {"seed_title": "X"}
    by = {a["key"]: a for a in tr.DEEP_RESEARCH_ANGLES}
    assert "[DATOS DE MAGNITUD]" in tr._build_angle_query_prompt(seed, by["tecnico"])
    assert "[DATOS DE MAGNITUD]" not in tr._build_angle_query_prompt(seed, by["humano"])
    assert all(k in tr.MAGNITUDE_SECTION for k in ("categoría", "vientos", "marea", "altura", "muertos", "área"))
