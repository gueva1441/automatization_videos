"""F50 B/C — el prompt de foto en producción (expediente + casilleros con Opus + armado por código + F8 backstop) y el
del clip Veo (Opus, orden de la guía de Google; negative_prompt y duration en el payload). Offline: Opus y fal falsos."""
import json

import pytest

import asset_manager as am
from script_engine import m03_expediente as mexp
from script_engine import m03_imagenes_v3 as v3
from script_engine import m03_visual as m3


# ─────────────────────────── chascadas ───────────────────────────
@pytest.mark.parametrize("loc, font, sale", [
    ("on the warning sign fixed to the barricade", "faded block stencil",
     'The word "X" is written on the warning sign fixed to the barricade in clear crisp faded block stencil '
     'lettering.'),                                                      # F51f: una sola palabra → «The word … is»
    ("place of birth line on the passport page", "typed passport typeface",
     'The place of birth line on the passport page reads "X" in clear crisp typed passport typeface lettering.'),
    ("the folder tab", "typed serif", 'The folder tab reads "X" in clear crisp typed serif lettering.'),
    ("", "", 'A sign reads "X" in clear crisp lettering.'),
])
def test_cartel_con_sujeto(loc, font, sale):
    assert v3.frase_cartel({"present": True, "text": "X", "font": font, "location": loc}) == sale


def test_cifra_al_inicio_de_oracion_en_mayuscula():
    assert v3.fix_counts_lr("Three inmates stand.") == "A few inmates stand."
    assert v3.fix_counts_lr("The two men sit") == "A couple of men sit"
    assert v3.fix_counts_lr("two men sit") == "a couple of men sit"


# ─────────────────────────── armado, año y F8 ───────────────────────────
SLOTS = {"subject": "a miner", "action": "loading ore", "gaze_interaction": "eyes down", "props_detail": "a sack",
         "setting": "the mill yard", "lighting": "harsh noon", "color_palette": "ochre", "shot_scale": "wide",
         "camera_angle": "eye-level", "lens_technique": "35mm", "text_in_image": {"present": False}}


def test_armado_en_el_orden_c():
    # F51a: sin mirada, objeto ni paleta; el estilo C va antes del cierre
    p = v3.armar(SLOTS, "1962")["prompt"]
    assert p.startswith("A miner. Loading ore. The mill yard, 1962. Harsh noon. Wide shot, eye-level, 35mm. "
                        + v3.ESTILO_C.format(anio="1962"))
    assert "Eyes down" not in p and "A sack" not in p and "ochre" not in p.lower()
    assert p.endswith(v3.NO_TEXT) and "16:9" in p
    con_anio = v3.armar({**SLOTS, "setting": "the mill yard in the 1960s"}, "1962")["partes"]["lugar_anio"]
    assert con_anio == "The mill yard in the 1960s."                    # el setting ya trae década: sin «, 1962»
    cartel = v3.armar({**SLOTS, "text_in_image": {"present": True, "text": "DANGER", "font": "stencil",
                                                  "location": "on the gate"}}, "1962")["prompt"]
    assert 'The word "DANGER" is written on the gate in clear crisp stencil lettering.' in cartel
    assert v3.NO_TEXT not in cartel


def test_anio_final_en_orden():
    # F51c: sin el paso «dicho en el ancla»: manda el `year` del modelo y después el respaldo del expediente
    e = {"anio_ancla": "1962", "respaldo": ("1961", "2) el último año dicho en la narración de los caps anteriores")}
    assert v3.anio_final(e, {"year": "1979"}) == ("1979", "1) el casillero `year` del modelo")
    assert v3.anio_final(e, {"year": "3000"}) == ("1961", "2) el último año dicho en la narración de los caps anteriores")
    assert v3.anio_final(e, {})[0] == "1961"


def test_f8_backstop_saca_la_frase_y_no_reteje():
    p, notas = v3.f8_backstop("Two men stand on the left. Blood on the floor. A dusty road.", {"shot_scale": "wide"},
                              False)
    assert "Blood" not in p and "A couple of men stand to one side." in p and notas


def test_backstop_de_texto_legible_saca_la_frase():
    p, fuera = m3._sacar_frases_con_texto('A wall. A faded patch where the name was painted. The words "W" are '
                                          'written on the sign, in clear crisp lettering.', "W")
    assert fuera == ["A faded patch where the name was painted."] and '"W"' in p


# ─────────────────────────── expediente ───────────────────────────
TOPIC = {"evidence_pool": {
    "personajes": [{"id": "p1", "nombre": "Ana Pérez", "rol": "Esposa de minero.", "lugar": "Wittenoom",
                    "fechas_presente": ["1962"]}],
    "datos": [{"id": "d1", "texto": "La mina cerró en 1966."}],
    "cronologia": [{"id": "c1", "fecha": "1962", "evento": "Llega el barco", "lugar": "Fremantle"}],
    "citas": [{"id": "q1", "texto": "Iba pegadita"}], "lugares": []}}
FU = {"esc": {"beats": [{"n": 3, "dato_central": "c1", "datos_apoyo": ["d1", "q1", "p1"]}]},
      "ficha": {"escenas": [{"ids": ["c1"], "donde": "puerto", "quien": "familias", "que_pasa": "bajan",
                             "sentidos": "calor"}],
                # F50c A: las personas salen de la ficha (y el ancla las nombra), no de los ids P del beat
                "personas": [{"nombre": "Ana Pérez", "rol": "Esposa de minero.", "variantes": [], "ids": ["p1"]}]},
      "parrafos": [{"beat": 3, "texto": "En 1962 llegan al puerto."}]}


def test_expediente_y_bloque():
    exps = mexp.expedientes(TOPIC, FU, [{"n": 3, "fecha": "1962-05"}], ["En 1962 Ana Pérez llega al puerto."],
                            [{"beat": 3, "cerrada": False}], None, "1961")
    e = exps[0]
    assert e["anio_ancla"] == "1962" and e["donde"] == ["Fremantle", "puerto"]
    assert e["facts"] == ["1962 · Llega el barco", "La mina cerró en 1966."]
    assert e["people3"] == ["Esposa de minero · Wittenoom · 1962"] and e["respaldo"][0] == "1962"
    b = mexp.bloque(exps, [{"id": "spanish_families", "who": "w", "where_when": "ww"}])
    assert "  [1] YEAR: 1962 · WHERE: Fremantle; puerto" in b and "      FACTS: «1962 · Llega el barco»" in b
    assert "      PEOPLE (role · where · years): Esposa de minero · Wittenoom · 1962" in b
    assert b.endswith("PEOPLE GROUPS:\n  - spanish_families: w · ww · APPEARANCE: - · CLOTHING: -\n")   # F50c C


def test_anio_previo_de_la_narracion():
    caps = [{"chapter_number": 1, "narration": "En 1961 nace. Un año después, en 1962, se casan."},
            {"chapter_number": 2, "narration": "En 1964 cierra."}]
    assert mexp.anio_previo(caps, 2) == "1962" and mexp.anio_previo(caps, 3) == "1964"
    assert mexp.anio_previo(caps, 1) is None


# ─────────────────────────── pedido y Opus ───────────────────────────
def test_pedido_de_casilleros():
    si = m3.SYSTEM_INSTRUCTION_CASILLEROS
    i = si.index("- foto_madre_ref:")
    resto = si[si.index("\n", i) + 1:]
    assert resto.startswith(m3.TEXTO_2_PEOPLE_GROUP + "\n" + m3.TEXTO_S4_YEAR + "\n")
    s = m3._casilleros_schema(3)
    assert s["items"]["required"][-2:] == ["year", "people_group"] and "mood" in s["items"]["properties"]
    assert m3.MODELO_CASILLEROS == "claude-opus-5-5"


def _topic_f8():
    return {"_f8": {"beats": {}, "year": "1962", "lang": "en", "fuentes": {}, "anio_prev": {}}}


def test_render_sin_escaleta_no_corre():
    with pytest.raises(m3.VisualValidationError, match="sin escaleta"):
        m3._render_prompts_seedream({}, {}, "x", {"anchors": [{"anchor": "a"}]}, 2)


def test_negativa_de_opus_es_parada_con_la_foto(monkeypatch):
    import claude_helpers

    def niega(*a, **k):
        raise claude_helpers.ClaudeError("claude-opus-5-5: m03:casilleros: el modelo se negó (x)")
    monkeypatch.setattr(m3, "_llamar_casilleros", niega)
    monkeypatch.setattr(m3, "_build_seedream_prompt_step2", lambda *a, **k: "pedido")
    with pytest.raises(m3.CasillerosParada, match="no llenó los casilleros"):
        m3._render_prompts_seedream(_topic_f8(), {}, "x", {"anchors": [{"anchor": "a"}]}, 2)
    with pytest.raises(m3.CasillerosParada, match="re-hechura de la foto «la foto tres»"):
        m3._f8_refill(_topic_f8(), {}, "x", {"narration_anchor": "la foto tres", "beat": None}, 2, "NOTE")


def test_render_arma_y_marca(monkeypatch):
    monkeypatch.setattr(m3, "_build_seedream_prompt_step2", lambda *a, **k: "pedido")
    monkeypatch.setattr(m3, "_llamar_casilleros", lambda *a, **k: {"image_prompts": [{**SLOTS, "year": "1979", "people_group": []}]})
    out = m3._render_prompts_seedream({**_topic_f8(), "_f8": {**_topic_f8()["_f8"], "refill": True}}, {}, "x",
                                      {"anchors": [{"anchor": "diez años antes"}]}, 2)
    it = out["image_prompts"][0]
    assert it["anio"] == "1979" and it["narration_anchor"] == "diez años antes"
    assert it["prompt"].startswith("A miner. Loading ore.") and "1979" in it["prompt"]
    assert "sensible" in it and json.loads(it["raw_llm_prompt"])["year"] == "1979"


# ─────────────────────────── clip Veo (C) ───────────────────────────
def test_movimiento_con_opus_y_el_pedido_de_la_guia(monkeypatch):
    visto = {}

    def opus(user, system_instruction=None, response_schema=None, description=None, **k):
        visto.update(user=user, system=system_instruction, desc=description)
        return {"video_prompt": "A slow, somber documentary shot on grainy 35mm film. " * 3}
    monkeypatch.setattr(m3, "_llamar_casilleros", opus)
    vp = m3._seedream_video_prompt("FOTO", "con el pie vendado.", "cap 1")
    assert 120 <= len(vp) <= 700 and visto["desc"] == "m03:motion"
    assert visto["user"] == ("FIRST FRAME (final):\nFOTO\n\nNARRATOR OVER THIS CLIP (Spanish, context only): "
                             "«con el pie vendado.»\n\nCLIP LENGTH: 8 seconds.")
    assert visto["system"].startswith("You write the motion prompt for an image-to-video model (Google Veo)")
    assert not hasattr(m3, "_VEO_VIDEO_PROMPT_STRUCT") and not hasattr(m3, "_SEEDREAM_MOTION_SYSTEM")


def test_payload_veo_con_negative_prompt_y_duration(monkeypatch, tmp_path):
    img = tmp_path / "f.png"
    img.write_bytes(b"png")
    visto = {}

    class R:
        status_code, content = 200, b"mp4"

        def raise_for_status(self):
            pass

        def json(self):
            return {"video": {"url": "u"}}
    monkeypatch.setattr(am.requests, "post", lambda url, **k: visto.update(k["json"]) or R())
    monkeypatch.setattr(am.requests, "get", lambda url, **k: R())
    am._call_veo_once(img, "prompt", tmp_path / "c.mp4")
    assert visto["negative_prompt"] == am.VEO_NEGATIVE_PROMPT and visto["duration"] == "8s"
    assert visto["generate_audio"] is False and "resolution" in visto
    assert am._veo_duration(4) == "4s"
    with pytest.raises(ValueError):
        am._veo_duration(5)


def test_lo_viejo_ya_no_esta():
    for s in ("SEEDREAM_SLOTS_USE_PRO", "_fluidify_item", "_fluidify_with_leakage_guard", "_post_check_locked",
              "_classify_locked_facts", "_f8_finish_item", "FLUIDIFICADOR_SYSTEM", "_find_text_leakage"):
        assert not hasattr(m3, s), s
    assert not hasattr(v3, "wrap_style")


# ─────────────────────────── F50b: tres bugs del armado ───────────────────────────
def test_f50b_plano_con_shot_no_es_menor_en_danio():
    assert not v3.problems("Wide shot, eye-level, child's height, deep depth of field, 35mm lens.")
    assert ("menor en daño", "The boy was shot dead.") in v3.problems("The boy was shot dead.")


def test_f50b_clausula_negada_sale_del_setting():
    p = v3.armar({**SLOTS, "setting": "the empty main street, with no figure anywhere"}, "1962")["prompt"]
    assert "no figure" not in p and "The empty main street, 1962." in p
    assert v3._sin_negadas("swings without seats, a rusted frame") == "swings without seats, a rusted frame"
    assert v3._sin_negadas("no work, no vehicles") == ""
    assert v3.armar({**SLOTS, "setting": "nobody anywhere"}, "1962")["partes"]["lugar_anio"] == ""


def test_f50b_minuscula_en_mitad_de_oracion():
    p = v3.armar({**SLOTS, "camera_angle": "Eye-level", "lens_technique": "Deep depth of field"}, "1962")["prompt"]
    assert "Wide shot, eye-level, deep depth of field." in p
    assert v3._minuscula_media("DSLR look") == "DSLR look" and v3._minuscula_media("35mm") == "35mm"
    assert v3.frase_cartel({"present": True, "text": "X", "font": "Metal block letters",
                            "location": "Over the entrance"}) == \
        'The word "X" is written over the entrance in clear crisp metal block lettering.'
    assert v3.frase_cartel({"present": True, "text": "X", "font": "", "location": "Federal Court sign"}) == \
        'The Federal Court sign reads "X" in clear crisp lettering.'
    assert v3.frase_cartel({"present": True, "text": "X", "font": "", "location": "At the Federal Court"}) == \
        'The word "X" is written at the Federal Court in clear crisp lettering.'
