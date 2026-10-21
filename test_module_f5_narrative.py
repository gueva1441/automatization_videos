"""F5 §1.3–1.5: narrador con evidence_pool, normalizer (horas, dólares, %, citas, siglas), números en palabras y
el juez narrativo (densidad, repetición, adjetivación, antagonista, cliffhanger). Sin red."""
from __future__ import annotations

import json

import script_engine.m01b_narrator as nb
from script_engine import evidence as ev
from script_engine import m05_narrative as mn
from script_engine.num_es import hour_words, variants, words

POOL = {
    "datos": [{"id": "D01", "texto": "Aproximadamente 6,500 personas estaban en la prisión", "tipo": "cifra",
               "valor": "6,500", "fecha": None},
              {"id": "D02", "texto": "517 reclusos no estaban contabilizados", "tipo": "cifra", "valor": "517"},
              {"id": "D03", "texto": "Se produjeron más de 50 fallas en el sistema de diques", "tipo": "cifra",
               "valor": "50"},
              {"id": "D04", "texto": "Algunas partes quedaron bajo 15 pies (4.6 metros) de agua", "tipo": "magnitud",
               "valor": "Nueva Orleans"},                                   # valor flojo: manda la cifra del texto
              {"id": "D05", "texto": "Ubicación: Nueva Orleans", "tipo": "lugar", "valor": "Nueva Orleans"}],
    "cronologia": [{"id": "T01", "fecha": "2005-08-28", "evento": "El sheriff anuncia que los presos no serán evacuados"},
                   {"id": "T02", "fecha": "2005-08-29", "evento": "Los generadores de respaldo fallan en la prisión"}],
    "citas": [{"id": "Q01", "texto": "permanecerán donde pertenecen", "autor": "Sheriff Marlin N. Gusman"}],
    "lugares": [],
    "personajes": [{"id": "P01", "nombre": "Marlin N. Gusman", "rol": "sheriff de Orleans", "antagonista": True}]}
SKEL = {"chapters": [{"chapter_number": 2, "evidence_ids": ["T01", "Q01", "D01", "D02"], "cliffhanger": "T02"},
                     {"chapter_number": 3, "evidence_ids": ["T02", "D03", "D04"], "cliffhanger": None}],
        "personajes": [{"id": "P01", "nombre": "Marlin N. Gusman", "rol": "sheriff de Orleans", "antagonista": True,
                        "entra_en_cap": 2}]}
IDS2 = ["T01", "Q01", "D01", "D02"]                         # F5b N2: los ids que declara el narrador
GOOD2 = ("El 28 de agosto, el sheriff Marlin Gusman anunció que los presos no serían evacuados. "
         "\"Permanecerán donde pertenecen\", dijo el sheriff Gusman. Había 6,500 personas en la prisión oscura. "
         "Después, 517 reclusos no estaban contabilizados. Esa noche, los generadores iban a fallar.")


def test_numeros_en_palabras():
    assert words(6500, fem=True) == "seis mil quinientas" and words(517) == "quinientos diecisiete"
    assert words(21, fem=True) == "veintiuna" and words(1_000_000) == "un millón" and words(100) == "cien"
    assert "seis mil quinientas" in variants("6,500") and variants("2005") == ["2005", "dos mil cinco"] or \
        set(variants("2005")) == {"2005", "dos mil cinco"}
    assert hour_words(6, 10, "AM") == "seis y diez de la mañana" and hour_words(12, 0, "PM") == "doce del mediodía"


def test_normalizer_formas_del_pool():
    from tts_normalizer import normalize_for_tts, normalize_pool_forms
    assert normalize_pool_forms("A las 6:10 AM cortaron la luz.") == "A las seis y diez de la mañana cortaron la luz."
    assert normalize_pool_forms("FEMA dio $223 millones.") == "FEMA dio doscientos veintitrés millones de dólares."
    assert normalize_pool_forms("Recibieron $650,000.") == "Recibieron seiscientos cincuenta mil dólares."
    assert normalize_pool_forms("El 98.7% de los presos.") == "El noventa y ocho coma siete por ciento de los presos."
    assert normalize_pool_forms('Dijo: “permanecerán donde pertenecen”.') == "Dijo: permanecerán donde pertenecen."
    assert normalize_for_tts("La ACLU y el DOJ.") == "La a ce ele u y el Departamento de Justicia."


def test_anchors_y_uso_de_datos():
    its = ev.items(POOL)
    assert ev.anchors(its["D04"]) == ["15 pies", "4.6 metros"]             # la cifra, no el valor flojo
    assert ev.used_in("eran seis mil quinientas almas", its["D01"])         # en palabras
    assert not ev.used_in("cobraron seiscientos cincuenta mil dólares", its["D03"])   # 50 dentro de otra cifra
    assert not ev.used_in("El 29 de agosto el agua entró.", its["T02"])      # fecha sola no es el evento
    assert ev.used_in("El 29 de agosto los generadores fallaron.", its["T02"])
    assert ev.is_hard(its["D01"]) and not ev.is_hard(its["D05"])
    assert ev.primary_antagonist(POOL)["id"] == "P01" and ev.spoken_date("2006-08") == "agosto de 2006"


def test_cap_problems_y_cumplimiento():
    assert mn.cap_problems(GOOD2, cap=2, pool=POOL, skeleton=SKEL, previous=[]) == []
    bad = ("Imaginen la oscuridad. Una noche terrible, densa, implacable. Un silencio frío y profundo. "
           "Una espera interminable y angustiante. El sheriff Gusman hablaba.")
    probs = " ".join(mn.cap_problems(bad, cap=2, pool=POOL, skeleton=SKEL, previous=[]))
    assert "datos asignados" in probs and "relleno prohibido: imaginen" in probs
    assert "nombre y apellido" in probs and "cierre tiene que anticipar" in probs
    rep = mn.cap_problems("Había 6,500 personas y 517 sin contar. " * 3 + GOOD2, cap=2, pool=POOL, skeleton=SKEL,
                          previous=["Eran 6,500.", "Otra vez 6,500 presos."])
    assert any("ya salieron en 2 caps" in p for p in rep)
    order = ("El 29 de agosto los generadores fallaron. Antes, el 28 de agosto, el sheriff Marlin Gusman anunció "
             "que los presos no serían evacuados. Había 6,500 personas.")
    sk_o = {"chapters": [{"chapter_number": 2, "evidence_ids": ["T01", "T02", "D01"], "cliffhanger": None}]}
    assert any("en orden de fecha" in p for p in mn.cap_problems(order, cap=2, pool=POOL, skeleton=sk_o, previous=[]))


def test_metricas_de_video():
    v1 = ["Una noche oscura, densa y terrible.", "El agua fría y profunda subía, implacable."]
    v2 = [GOOD2, "El 29 de agosto los generadores fallaron. Hubo más de 50 fallas. Quedaron bajo 15 pies de agua."]
    r1, r2 = mn.video_metrics(v1, POOL), mn.video_metrics(v2, POOL, SKEL | {"chapters": [
        {"chapter_number": 1, "cliffhanger": "T02"}]})
    assert r1["video"]["densidad"] == 0 and r2["video"]["densidad"] > 5
    assert r1["video"]["adj_100"] > r2["video"]["adj_100"]
    assert r1["video"]["antagonista_nombrado"] is False and r2["video"]["antagonista_nombrado"] is True
    assert r2["video"]["cliffhangers"][0]["ok"] is True
    assert mn.trigram_overlap(["a b c d", "x b c d"])[0] > 0


def test_prompt_narrador_con_y_sin_pool():
    topic = {"video_title": "x", "verified_facts": [{"fact": "f"}]}
    sk = {"chapters": [{"chapter_number": n, "title": "t", "role": "development", "bullets": ["b"]} for n in range(1, 8)]}
    plain = nb._prompt_development(topic, sk, [], 2)
    assert "EVIDENCE POOL" not in plain and "literal en los verified_facts arriba" in plain
    skp = {**sk, "chapters": [{**c, **(SKEL["chapters"][0] if c["chapter_number"] == 2 else {})} for c in sk["chapters"]],
           "personajes": SKEL["personajes"]}
    withp = nb._prompt_development({**topic, "evidence_pool": POOL}, skp, [], 2)
    assert "ASIGNADOS A ESTE CAP" in withp and "[Q01] CITA" in withp and "Marlin N. Gusman" in withp
    assert "CLIFFHANGER" in withp and "o en el EVIDENCE POOL" in withp and "nunca como firma" in withp.lower()


def test_retry_por_pool_y_aceptacion_con_violaciones(monkeypatch):
    base = "Los guardias contaron a los presos en el patio de la cárcel una vez más. "
    filler = (base * 14).strip()
    good = (base * 4 + "El patio estaba húmedo, sucio y oscuro, el aire pesado. " + base * 4 + GOOD2).strip()
    q = [filler, filler, filler]
    prompts = []
    monkeypatch.setattr(nb, "call_flash_json", lambda p, response_schema=None: (prompts.append(p), {"narration": q.pop(0), "datos_usados": IDS2})[1])
    viol: dict = {}
    out = nb._call_with_length_retry("P", role="development", cap_number=2, max_attempts=3,
                                     f5={"pool": POOL, "skeleton": SKEL, "previous": []}, violations=viol)
    assert out == filler and 2 in viol and "REGLAS DEL EVIDENCE POOL" in prompts[1]   # acepta y anota
    q2 = [filler, good]
    monkeypatch.setattr(nb, "call_flash_json", lambda p, response_schema=None: {"narration": q2.pop(0), "datos_usados": IDS2})
    viol2: dict = {}
    nb._call_with_length_retry("P", role="development", cap_number=2, max_attempts=3,
                               f5={"pool": POOL, "skeleton": SKEL, "previous": []}, violations=viol2)
    assert not q2                                                            # reintentó una vez


def test_gate_sin_diccionario_global(monkeypatch, tmp_path):
    from script_engine import m02_5_normalizer_gate as g
    monkeypatch.setattr(g, "STEPS_DIR", tmp_path)
    monkeypatch.setattr(g, "_audit_with_llm", lambda n: [{"chapter_number": 1, "original": "OPP", "suggested": "o pe pe",
                                                          "category": "acronym", "is_recurring": True}])
    called = []
    monkeypatch.setattr(g, "_persist_to_custom_dict", lambda *a, **k: called.append(1) or 1)
    nar = {"topic_id": "t", "chapters": [{"chapter_number": 1, "narration": "La OPP a las 6:10 AM costó $223 millones."}]}
    out = g.gate_normalizer_for_topic("t", nar, interactive=False, persist_dict=False)
    norm = json.loads(out["normalized_path"].read_text(encoding="utf-8"))["chapters"][0]["narration_normalized"]
    assert norm == "La o pe pe a las seis y diez de la mañana costó doscientos veintitrés millones de dólares."
    assert not called and out["added_to_dict"] == 0


def test_juez_persiste_reporte(tmp_path):
    nar = {"chapters": [{"chapter_number": 1, "narration": GOOD2}], "_f5_violations": {"1": ["x"]}}
    rep = mn.judge_narration("t", steps_dir=tmp_path, pool=POOL, narration=nar, skeleton={"chapters": []})
    saved = json.loads((tmp_path / "t" / "06_judge_narrative.json").read_text(encoding="utf-8"))
    assert saved["video"]["densidad"] == rep["video"]["densidad"] and saved["violaciones_narrador"] == {"1": ["x"]}
    assert saved["umbrales"]["adj_100_max"] == mn.ADJ_MAX


def test_ultimo_intento_largo_acepta_el_anterior(monkeypatch):
    """F5: si el último intento rompe el largo pero uno anterior solo fallaba reglas del pool, se acepta el anterior."""
    base = "Los guardias contaron a los presos en el patio de la cárcel una vez más. "
    pool_only = (base * 14).strip()
    too_long = (base * 40).strip()
    q = [pool_only, too_long, too_long]
    monkeypatch.setattr(nb, "call_flash_json", lambda p, response_schema=None: {"narration": q.pop(0)})
    viol: dict = {}
    out = nb._call_with_length_retry("P", role="development", cap_number=2, max_attempts=3,
                                     f5={"pool": POOL, "skeleton": SKEL, "previous": []}, violations=viol)
    assert out == pool_only and viol[2]
