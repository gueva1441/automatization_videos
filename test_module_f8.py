"""
test_module_f8.py — F8 (HANDOFF_F8_imagenes_v3): cierre de parámetros de guion (§2) e imágenes v3 (§1 A–F).
"""
from __future__ import annotations

from script_engine import m01a_escaleta as me
from script_engine import m01c_editor as mc
from script_engine.guion_v3_reglas import closing_soft
from script_engine.video_length import DEFAULTS
from test_module_f6b import POOL, good


# ═══════════════════════════════════════════════════════════════
#  §2 — escaleta: ≥ 2 beats por cap de desarrollo; cierre en cita o pregunta
# ═══════════════════════════════════════════════════════════════

def _dev_msgs(hard):
    return [h for h in hard if h.startswith("caps de desarrollo")]


def test_minimo_dos_beats_por_cap_de_desarrollo():
    assert DEFAULTS["min_beats_dev_cap"] == 2 and DEFAULTS["max_beats"] == 14
    assert me.MIN_BEATS_DEV_CAP == 2
    _, hard, _, _ = me.validate(good(), POOL)              # 8 beats: caps 2, 3, 4 y 6 con uno solo
    assert _dev_msgs(hard) and "[2, 3, 4, 6]" in _dev_msgs(hard)[0]      # F39 §A.2: RULES (sin ficha) se borró


def test_doce_beats_dos_por_cap_pasan_la_regla():
    e = good()
    base = e["beats"]
    # 1 + 2 × 5 + 1: duplico los beats de los caps 2, 3, 4 y 6 (la regla de cantidad es lo que se mide acá)
    beats = []
    for b in base:
        beats.append(dict(b))
        if b["cap"] in (2, 3, 4, 6):
            beats.append({**b, "dato_central": b["dato_central"], "pregunta_pantalla": ""})
    e["beats"] = beats
    _, hard, _, _ = me.validate(e, POOL)
    assert not _dev_msgs(hard) and not [h for h in hard if "beats (tienen que ser" in h]


def test_amarillo_baja_el_minimo_a_uno():
    largo = {"cap_words": me.CAP_WORDS, "max_beats": 8, "min_beats_dev_cap": DEFAULTS["gate_yellow_min_beats_dev_cap"]}
    _, hard, _, _ = me.validate(good(), POOL, largo=largo)
    assert not _dev_msgs(hard)                             # F39 §A.2: rules_text (sin ficha) se borró


def test_cierre_resumen_es_blanda_al_editor():
    resumen = [{"texto": "Reed contó: «No sabíamos si íbamos a salir». Cientos de familias nunca supieron nada."}]
    cita = [{"texto": "Cientos de familias nunca supieron nada. «No sabíamos si íbamos a salir», dijo Reed."}]
    pregunta = [{"texto": "Nadie volvió a preguntar. ¿Dónde están los 517?"}]
    n = closing_soft(resumen)
    assert len(n) == 1 and "mové la cita" in n[0]
    assert closing_soft(cita) == [] and closing_soft(pregunta) == []
    assert "cortá la frase-resumen" in closing_soft([{"texto": "Hubo agua. Fue el final de todo."}])[0]
    esc = {"beats": [{"n": 1, "funcion": "cierre", "intensidad": 2, "palabras_objetivo": 140}], "pico": {"beat": 1}}
    par = [{"beat": 1, "cap": 7, "ids_usados": [], **resumen[0]}]
    p = mc.build_prompt(esc, par, [], closing_soft(par))
    assert "ÚLTIMA FRASE DEL VIDEO" in p and "Cientos de familias" in p
    assert "ÚLTIMA FRASE DEL VIDEO" not in mc.build_prompt(esc, par, [], [])


# ═══════════════════════════════════════════════════════════════
#  §1 A — motor Seedream 5.0 Lite
# ═══════════════════════════════════════════════════════════════

import json as _json  # noqa: E402

import pytest  # noqa: E402

import asset_manager as am  # noqa: E402
import engine_profiles as ep  # noqa: E402
from script_engine import m03_imagenes_v3 as v3  # noqa: E402
from script_engine import m03_visual as m3  # noqa: E402


def test_perfil_seedream_v5_lite():
    r = ep.PERFIL_SEEDREAM.render
    assert r.model_id == "fal-ai/bytedance/seedream/v5/lite/text-to-image"
    assert r.cost_usd == 0.035 and r.accepts_seed is False
    assert r.image_size == {"width": 2560, "height": 1440}
    p = am._seedream_payload_for("x", seed=123)
    assert "seed" not in p and p["image_size"] == {"width": 2560, "height": 1440}
    e = am._seedream_edit_payload_for("x", ["data:image/png;base64,AA"], seed=5)
    assert e["image_urls"] == ["data:image/png;base64,AA"] and "seed" not in e
    assert am.FLUX_MAX_WORKERS == 20


class _Resp:
    def __init__(self, code, body=None, content=b"png"):
        self.status_code, self._body, self.content = code, body or {}, content
        self.text = _json.dumps(self._body)

    def raise_for_status(self):
        if self.status_code >= 400:
            import requests
            raise requests.HTTPError(f"{self.status_code} Client Error: Too Many Requests", response=self)

    def json(self):
        return self._body


def test_429_reintenta_tres_veces_y_mide_ms(monkeypatch, tmp_path):
    import error_handler as eh
    import requests
    monkeypatch.setattr(eh.time, "sleep", lambda s: None)
    monkeypatch.setattr(am.api, "image_engine", "seedream")
    monkeypatch.setattr(am.cost_tracker, "track_seedream", lambda **k: None)
    calls = []

    def post(url, **k):
        calls.append(url)
        if len(calls) < 3:
            return _Resp(429)
        return _Resp(200, {"images": [{"url": "http://x/img.png", "width": 2560, "height": 1440}], "seed": 7})
    monkeypatch.setattr(requests, "post", post)
    monkeypatch.setattr(requests, "get", lambda url, **k: _Resp(200))
    out = am._generate_image_raw("prompt", tmp_path / "a.png", False)
    assert len(calls) == 3 and calls[0].endswith("seedream/v5/lite/text-to-image")
    assert out["endpoint"] == "fal-ai/bytedance/seedream/v5/lite/text-to-image" and isinstance(out["ms"], int)
    calls.clear()
    monkeypatch.setattr(requests, "post", lambda url, **k: (calls.append(url), _Resp(503))[1])
    with pytest.raises(Exception):
        am._generate_image_raw("prompt", tmp_path / "b.png", False)
    assert len(calls) == 3                               # 3 intentos y no más
    calls.clear()
    monkeypatch.setattr(requests, "post", post)
    out = am._generate_image_raw("p", tmp_path / "c.png", False, foto_madre_data_uris=["data:image/png;base64,AA"])
    assert out["endpoint"].endswith("seedream/v5/lite/edit")


# ═══════════════════════════════════════════════════════════════
#  §1 B — ancla por beat
# ═══════════════════════════════════════════════════════════════

NARR = ("Primer párrafo del beat uno con agua en la celda. Sigue el agua. "
        "Segundo párrafo, el pico: disparos desde el techo. Más disparos en la noche. "
        "Tercer párrafo, respiro en el paso elevado bajo el sol.")
BEATS = [
    {"n": 4, "cap": 5, "imagen_sensorial": "agua negra en la celda", "emocion": "angustia", "intensidad": 4,
     "funcion": "escalada", "pico": False, "parrafos": ["Primer párrafo del beat uno con agua en la celda. Sigue el agua."]},
    {"n": 5, "cap": 5, "imagen_sensorial": "el fogonazo de un rifle desde un techo", "emocion": "horror",
     "intensidad": 5, "funcion": "pico", "pico": True,
     "parrafos": ["Segundo párrafo, el pico: disparos desde el techo. Más disparos en la noche."]},
    {"n": 6, "cap": 5, "imagen_sensorial": "hombres sentados en el asfalto", "emocion": "desolación", "intensidad": 1,
     "funcion": "respiro", "pico": False, "parrafos": ["Tercer párrafo, respiro en el paso elevado bajo el sol."]},
]


def test_cada_beat_recibe_imagen_y_el_pico_dos():
    anchors = ["Primer párrafo del beat uno", "Sigue el agua", "Segundo párrafo, el pico",
               "Tercer párrafo, respiro", "bajo el sol"]
    a = v3.assign_beats(NARR, anchors, BEATS)
    beats = [x["beat"] for x in a]
    assert set(beats) == {4, 5, 6} and beats.count(5) == 2 and beats == sorted(beats)
    assert sum(x["cerrada"] for x in a) == 1 and a[[i for i, x in enumerate(a) if x["cerrada"]][0]]["beat"] == 5
    blk = v3.beats_block(BEATS, a, ["bullet de contexto"])
    assert "fogonazo" in blk and "TIGHTEST" in blk and "bullet de contexto" in blk


def test_sin_escaleta_no_hay_beats(tmp_path):
    assert v3.load_beats({"id": "x"}, tmp_path) is None
    d = tmp_path / "t1"
    d.mkdir()
    (d / "01a_escaleta.json").write_text(_json.dumps({"pico": {"beat": 2}, "beats": [
        {"n": 1, "cap": 1, "imagen_sensorial": "a", "dato_central": "D1"},
        {"n": 2, "cap": 2, "imagen_sensorial": "b", "dato_central": "D2"}]}), encoding="utf-8")
    (d / "01b_narracion_v3.json").write_text(_json.dumps({"parrafos": [{"beat": 2, "texto": "hola"}]}), encoding="utf-8")
    b = v3.load_beats({"id": "t1"}, tmp_path)
    assert b[2][0]["pico"] and b[2][0]["parrafos"] == ["hola"] and not b[1][0]["pico"]


# ═══════════════════════════════════════════════════════════════
#  §1 C–E — estilo, composición, sensible
# ═══════════════════════════════════════════════════════════════

def test_estilo_en_el_medio_del_armado():
    # F50 B: sin wrap_style; el armado por código empieza por el sujeto y pone el estilo después de lugar + año
    it = {"subject": "a flooded cell", "action": "water rising", "setting": "Orleans Parish Prison",
          "shot_scale": "wide", "text_in_image": {"present": False, "text": "", "font": "", "location": ""}}
    head = v3.style_head("2005")
    assert head.startswith("Grainy 35mm documentary photograph, 2005, dark-history realism")
    p = v3.armar(it, "2005")["prompt"]
    assert p.startswith("A flooded cell. Water rising.") and f"{head} {v3.STYLE_TAIL}" in p
    assert p.index("Orleans Parish Prison, 2005.") < p.index(head)
    assert p.endswith(f"{ep.select_profile('seedream').aspect_ratio_text} {v3.NO_TEXT}")
    # el setting que ya trae año no lo repite; con cartel no va el «sin texto»
    p2 = v3.armar({**it, "setting": "Orleans Parish Prison in 2005",
                   "text_in_image": {"present": True, "text": "PARISH PRISON", "font": "", "location": "above the gate"}},
                  "2005")["prompt"]
    assert "Orleans Parish Prison in 2005." in p2 and "2005, 2005" not in p2 and head in p2
    assert 'The words "PARISH PRISON" are written above the gate' in p2 and v3.NO_TEXT not in p2
    assert v3.topic_year({"era_visual_canon": {"spans": "2005-2010"}}, None) == "2005"


def test_reglas_de_composicion():
    bad = ("Close shot of hands gripping the bars, knuckles white, jaw clenched, three inmates on the left, "
           "blood on the floor.")
    kinds = {k for k, _ in v3.problems(bad)}
    assert {"manos/cara", "prohibida", "conteo", "izquierda/derecha"} <= kinds
    fixed = v3.fix_counts_lr("Three inmates stand on the left of the frame near 6,375 cots.")
    assert "Three" not in fixed and "left" not in fixed and "6,375" in fixed
    s = {"subject": "an inmate", "gaze_interaction": "jaw clenched, eyes toward the window", "mood": "cold"}
    gone = v3.scrub_slots(s)
    assert gone and "jaw" not in s["gaze_interaction"] and "window" in s["gaze_interaction"]
    assert "manos/cara" not in {k for k, _ in v3.problems("A man in medium shot, hands out of focus.")}
    assert v3.problems("A child stands near the drowned body.") and not v3.problems("A child's shoe on the tray.")
    out = v3.scrub_sentence_problems("A dark cell. Blood on the wall. Water rises.")
    assert "Blood" not in out and "Water rises" in out


def test_auditoria_del_video():
    def it(prompt, shot="wide", subj="a building", ref="interior_scene", beat=None):
        return {"prompt": prompt, "shot_scale": shot, "subject": subj, "subject_ref": ref, "beat": beat}
    caps = [[it("A long corridor. A dead body floating, partly hidden.", ref="establishing_shot")],
            [it("A corridor with doors."), it("Another corridor."), it("The dead inmates in the water.", "medium", "men")],
            [it("A corridor again.", ref="establishing_shot"), it("Lifeless bodies under a tarp at a distance.")],
            [it("A sheriff at a podium.", "medium", "a man", "establishing_shot")]]
    a = v3.video_audit(caps)
    assert "pasillo" in a["motivos"] and len(a["exceso_motivos"]) == 2          # 4 pasillos: 3.º y 4.º sobran
    assert len(a["cuerpos"]) == 3 and a["exceso_cuerpos"] == [(1, 0)]      # el del cap 1 sobra; los otros 2 entran
    assert a["caps_sin_establecimiento"] == [2]
    beats = {3: [{"n": 9, "imagen_sensorial": "un pasillo inundado"}]}      # el beat lo nombra: no es exceso
    caps[2][0]["beat"] = 9
    assert (3, 0, "pasillo") not in v3.video_audit(caps, beats)["exceso_motivos"]


def test_doctrina_v3_sin_cliches_y_v2_intacta():
    si3 = m3.SYSTEM_INSTRUCTION_VISUAL_SEEDREAM_V3
    assert "COMPOSITION RULES (v3" in si3 and "posture" in si3
    assert "jaw clenched, lips pressed thin, brow knotted" not in si3
    assert "jaw clenched, lips pressed thin, brow knotted" in m3.SYSTEM_INSTRUCTION_VISUAL_SEEDREAM   # v2 y m09


# ═══════════════════════════════════════════════════════════════
#  §1 F — tope y re-encuadre
# ═══════════════════════════════════════════════════════════════

def test_reencuadre_propuesto_cuando_la_duracion_pide_mas():
    assert m3._calculate_image_count(140.0, 3) == 16
    assert m3._calculate_image_count(140.0, 3, capped=False) == 18
    r = v3.reencuadres(18, 16, [3, 7, 1])
    assert [x["reencuadre_de"] for x in r] == [3, 7] and all(1.3 <= x["zoom"] <= 1.6 for x in r)
    assert v3.reencuadres(15, 16, [1]) == []


# ═══════════════════════════════════════════════════════════════
#  Integración con m03 (LLM simulado)
# ═══════════════════════════════════════════════════════════════

def _fake_slots(n, body=False):
    out = []
    for i in range(n):
        out.append({"subject": "dead inmates floating" if body and i == 1 else "a flooded prison cell",
                    "action": "water rising", "gaze_interaction": "jaw clenched, facing the window",
                    "setting": "Orleans Parish Prison", "color_palette": "grey", "props_detail": "a mattress",
                    "shot_scale": "wide", "camera_angle": "eye-level", "lens_technique": "deep focus",
                    "lighting": "low-key night", "mood": "cold", "style": "documentary",
                    "text_in_image": {"present": False, "text": "", "font": "", "location": ""},
                    "hard_fact_ids": [], "subject_ref": "interior_scene", "foto_madre_ref": [],
                    "emotional_rank": "R3", "people_group": [], "year": "2005"})
    return out


@pytest.fixture
def fake_llm(monkeypatch):
    """F50 B: se simula la llamada de los casilleros (Opus); el reintento, la validación y el armado son los reales."""
    seen = {"prompts": [], "systems": [], "descriptions": []}

    def casilleros(prompt, system_instruction=None, response_schema=None, description=None, **k):
        seen["prompts"].append(prompt)
        seen["systems"].append(system_instruction)
        seen["descriptions"].append(description)
        block = prompt.split("ANCHORS YA ELEGIDOS")[1].split("Emit EXACTLY")[0]
        n = len([ln for ln in block.splitlines() if ln.strip().startswith("[")])
        body = "FOR THIS IMAGE" not in prompt and "\nCAP 1 —" in prompt
        return {"image_prompts": _fake_slots(n, body)}
    monkeypatch.setattr(m3, "_llamar_casilleros", casilleros)
    return seen


def _topic_f8():
    beats = {1: [{**BEATS[0], "cap": 1, "n": 1, "pico": False, "parrafos": [NARR]}], 5: BEATS}
    return {"id": "t", "verified_facts": [], "_f8": {"beats": beats, "year": "2005"}}


def test_render_v3_usa_beats_estilo_y_reglas(fake_llm):
    plan = {"anchors": [{"anchor": a} for a in ["Primer párrafo del beat uno", "Sigue el agua",
                                                   "Segundo párrafo, el pico", "Tercer párrafo, respiro"]]}
    out = m3._render_prompts_seedream(_topic_f8(), {"chapter_number": 5, "bullets": ["b1"]}, NARR, plan, 5)
    assert "VISUAL SUBJECT PER IMAGE" in fake_llm["prompts"][0]
    assert "CASE FILE PER IMAGE" in fake_llm["prompts"][0]                     # F50 B: el expediente va en el pedido
    assert fake_llm["systems"][0] == m3.SYSTEM_INSTRUCTION_CASILLEROS
    assert set(fake_llm["descriptions"]) == {"m03:casilleros"}
    # el SI de los casilleros es el v3 con `people_group` y `year` agregados
    si = m3.SYSTEM_INSTRUCTION_CASILLEROS
    assert "COMPOSITION RULES (v3" in si and m3.TEXTO_2_PEOPLE_GROUP in si and m3.TEXTO_S4_YEAR in si
    its = out["image_prompts"]
    assert [i["beat"] for i in its].count(5) == 2
    head = v3.style_head("2005")
    # la prosa empieza por el sujeto; el estilo del año va en el medio
    assert all(head in i["prompt"] and not i["prompt"].startswith(head) for i in its)
    assert all(i["anio"] == "2005" and v3.NO_TEXT in i["prompt"] for i in its)
    assert all("jaw" not in i["prompt"] for i in its) and all("sensible" in i for i in its)
    assert any("ESTABLISHING" in p for p in fake_llm["prompts"][1:])   # sin establecimiento → se rehizo una
    assert any(m3.F8_NOTE_CERRADA in p for p in fake_llm["prompts"][1:])  # la del pico salió wide → se rehizo
    assert not v3.is_body("The jumpsuit clings to the body of one of the men.")
    assert v3.is_body("A body floats face-down, dead, half hidden by the dark water.")


def test_render_v3_cap1_sin_cuerpos(fake_llm):
    plan = {"anchors": [{"anchor": "Primer párrafo"}, {"anchor": "Sigue el agua"}]}
    out = m3._render_prompts_seedream(_topic_f8(), {"chapter_number": 1}, NARR, plan, 1)
    assert not any(i["sensible"] for i in out["image_prompts"])
    assert any(m3.F8_NOTE_BODY_HOOK in p for p in fake_llm["prompts"])


def test_pasada_de_video_rehace_excesos_menos_el_cuadro_veo(monkeypatch):
    calls = []

    def refill(topic, cap_data, narration, item, cap, note):
        calls.append((cap, note))
        return {**item, "prompt": "A wide exterior of the prison seen from the street.", "shot_scale": "wide",
                "subject": "the building"}
    monkeypatch.setattr(m3, "_f8_refill", refill)

    def it(p):
        return {"prompt": p, "shot_scale": "medium", "subject": "a man", "subject_ref": "interior_scene",
                "narration_anchor": "x"}
    items = {1: [it("A long corridor."), it("A corridor.")], 2: [it("A corridor again."), it("A hallway.")],
             3: [], 4: [], 5: [], 6: [], 7: [it("A corridor at night.")]}
    topic = {"_f8": {"beats": {}}}
    rep = m3._f8_fix_video(topic, {n: {} for n in range(1, 8)}, {n: {"narration": ""} for n in range(1, 8)}, items)
    assert rep["despues"]["exceso_motivos"] == [] and calls
    assert items[1][0]["prompt"] == "A long corridor."           # el cuadro del clip Veo no se rehace
    assert all("Motifs already used twice" in n for _, n in calls)
    assert v3.problems("A close shot of a man drinking from his cupped hands.")


def test_sin_escaleta_no_hay_casilleros(fake_llm):
    # F50 B: el camino v2 (sin escaleta) se borró: sin `_f8` no hay expediente ni casilleros, y no se llama al modelo
    plan = {"anchors": [{"anchor": "Primer párrafo"}]}
    topic = {"id": "t", "verified_facts": []}
    with pytest.raises(m3.VisualValidationError, match="sin escaleta"):
        m3._render_prompts_seedream(topic, {"chapter_number": 3}, NARR, plan, 3)
    assert fake_llm["prompts"] == []


def test_refill_rehace_una_foto_con_su_nota(fake_llm):
    item = {"narration_anchor": "Sigue el agua", "beat": 4, "cerrada": False}
    nota = "Show the empty bunk."
    new = m3._f8_refill(_topic_f8(), {"chapter_number": 5}, NARR, item, 5, nota)
    assert new["_f8_rehecha"] == nota and new["narration_anchor"] == "Sigue el agua" and new["beat"] == 4
    assert len(fake_llm["prompts"]) == 1 and f"FOR THIS IMAGE: {nota}" in fake_llm["prompts"][0]


def test_negativa_de_opus_es_parada(monkeypatch):
    import claude_helpers

    def niega(*a, **k):
        raise claude_helpers.ClaudeError("refusal")
    monkeypatch.setattr(m3, "_llamar_casilleros", niega)
    plan = {"anchors": [{"anchor": "Sigue el agua"}]}
    with pytest.raises(m3.CasillerosParada, match="no llenó los casilleros"):
        m3._render_prompts_seedream(_topic_f8(), {"chapter_number": 5}, NARR, plan, 5)
    item = {"narration_anchor": "Sigue el agua", "beat": 4, "cerrada": False}
    with pytest.raises(m3.CasillerosParada, match="re-hechura de la foto"):
        m3._f8_refill(_topic_f8(), {"chapter_number": 5}, NARR, item, 5, "x")
