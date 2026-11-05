# -*- coding: utf-8 -*-
"""F78d — la identidad de las personas en producción (HANDOFF_F78d + adenda 1): l.166 de DOCTRINE_PEOPLE, `_f8_refill` con
`personas_fijas`, `aspecto_fuente` en cada ítem con persona y el paso `rehacer_aspecto_personas` (`fase1_5 --only aspecto`).

Sin red: los casilleros de Opus, el movimiento del clip y los rasgos se simulan; el armado es el real."""
from __future__ import annotations

import hashlib
import json

import pytest

import fase1_5
import foto_madre as fm
from script_engine import m03_visual as m3
from test_module_f8 import BEATS, NARR, _fake_slots

CARMEN = {"name": "Carmen Cortés", "role": "victim", "era": "1981-2000", "age_at_event": 14,
          "appearance_canon": "a fourteen-year-old Spanish girl", "condition_by_period": []}
ARCADIO = {"name": "Arcadio Fernández", "role": "victim", "era": "1981-1990", "age_at_event": 40,
           "appearance_canon": "a middle-aged Spanish man", "condition_by_period": []}
RASGOS = {"Carmen Cortés": "Oval face, long dark braid", "Arcadio Fernández": "Full dark beard, curly black hair"}


def _topic(**k):
    beats = {5: BEATS, 1: [{**BEATS[0], "cap": 1, "n": 1, "pico": False, "parrafos": [NARR]}]}
    return {"id": "t78d", "verified_facts": [], "documented_people": [dict(CARMEN), dict(ARCADIO)],
            "_f8": {"beats": beats, "year": "1985"}, **k}


@pytest.fixture
def opus(monkeypatch):
    """Casilleros simulados: devuelven `persona` = lo que diga `opus["persona"]` (por defecto, las personas del bloque)."""
    seen = {"prompts": [], "persona": None}

    def casilleros(prompt, system_instruction=None, response_schema=None, description=None, **k):
        seen["prompts"].append(prompt)
        bloque = prompt.split("PERSONAS DOCUMENTADAS")[1].split("OBJETOS DOCUMENTADOS")[0] if "PERSONAS DOCUMENTADAS" in prompt else ""
        presentes = [p["name"] for p in (CARMEN, ARCADIO) if p["name"] in bloque]
        slots = _fake_slots(1)
        for s in slots:
            s["persona"] = seen["persona"] if seen["persona"] is not None else presentes
        return {"image_prompts": slots}
    monkeypatch.setattr(m3, "_llamar_casilleros", casilleros)
    monkeypatch.setattr(m3, "_rasgos_de_madres", lambda t: dict(RASGOS))
    return seen


# ── l.166 ────────────────────────────────────────────────────────────────────────────────────────────
def test_l166_dice_appearance_o_canon():
    assert ("from a documented person's appearance (or appearance_canon if there is none) when it is one"
            in m3.DOCTRINE_PEOPLE)
    assert "appearance_canon when it is one" not in m3.DOCTRINE_PEOPLE


# ── personas_fijas: filtro del bloque y persona distinta ─────────────────────────────────────────────
def test_refill_con_personas_fijas_lleva_solo_esas_personas(opus):
    item = {"narration_anchor": "Sigue el agua", "beat": 4, "persona": ["Arcadio Fernández"]}
    new = m3._f8_refill(_topic(), {"chapter_number": 5}, NARR, item, 5, "", personas_fijas=["Arcadio Fernández"])
    bloque = opus["prompts"][0].split("PERSONAS DOCUMENTADAS")[1].split("OBJETOS DOCUMENTADOS")[0]
    assert "Arcadio Fernández" in bloque and "Carmen Cortés" not in bloque
    assert f"appearance: {RASGOS['Arcadio Fernández']}" in bloque          # los rasgos del topic entero
    assert new["persona"] == ["Arcadio Fernández"] and new["aspecto_fuente"] == "rasgos"
    assert "_rasgos_refill" not in new and "_f8_rehecha" not in new          # note="" no deja la clave vacía


def test_refill_sin_personas_fijas_es_el_de_siempre(opus):
    item = {"narration_anchor": "Sigue el agua", "beat": 4}
    new = m3._f8_refill(_topic(), {"chapter_number": 5}, NARR, item, 5, "Show the empty bunk.")
    bloque = opus["prompts"][0].split("PERSONAS DOCUMENTADAS")[1].split("OBJETOS DOCUMENTADOS")[0]
    assert "Arcadio Fernández" in bloque and "Carmen Cortés" in bloque
    assert new["_f8_rehecha"] == "Show the empty bunk."


def test_persona_distinta_queda_lo_viejo_con_marca(opus):
    opus["persona"] = ["Carmen Cortés"]
    item = {"narration_anchor": "Sigue el agua", "beat": 4, "persona": ["Arcadio Fernández"], "prompt": "VIEJO"}
    new = m3._f8_refill(_topic(), {"chapter_number": 5}, NARR, item, 5, "", personas_fijas=["Arcadio Fernández"])
    assert new == {**item, "_rasgos_refill": "persona_distinta"}
    assert len(opus["prompts"]) == 1                                          # sin reintentos


# ── aspecto_fuente ───────────────────────────────────────────────────────────────────────────────────
def test_aspecto_fuente():
    it = {"persona": ["Carmen Cortés", "Arcadio Fernández"]}
    m3._marcar_aspecto(it, RASGOS)
    assert it["aspecto_fuente"] == "rasgos"
    m3._marcar_aspecto(it, {"Carmen Cortés": "x"})
    assert it["aspecto_fuente"] == "canon"
    sin = {"persona": []}
    m3._marcar_aspecto(sin, RASGOS)
    assert "aspecto_fuente" not in sin
    assert {"aspecto_fuente", "_rasgos_refill"} <= set(m3.CLAVES_F8_PAPEL)    # viajan a supps e image_f8


def test_render_marca_aspecto_fuente_y_lee_rasgos_una_vez(opus, monkeypatch):
    lecturas = []
    monkeypatch.setattr(m3, "_rasgos_de_madres", lambda t: lecturas.append(1) or {"Carmen Cortés": "x"})
    plan = {"anchors": [{"anchor": "Sigue el agua"}]}
    out = m3._render_prompts_seedream({**_topic(), "_f8": {**_topic()["_f8"], "refill": True}}, {"chapter_number": 5},
                                      NARR, plan, 5)
    assert out["image_prompts"][0]["aspecto_fuente"] == "canon" and lecturas == [1]   # Arcadio sin rasgos → canon


def test_bloque_con_rasgos_dados_no_lee_disco(monkeypatch):
    monkeypatch.setattr(fm, "rasgos_vigentes", lambda *a, **k: pytest.fail("no debía leer rasgos"))
    b = m3._format_seedream_canon_block(_topic(), rasgos=dict(RASGOS))
    assert f"appearance: {RASGOS['Carmen Cortés']}" in b


# ── el paso: idempotencia, QA, nota previa, foto del clip ────────────────────────────────────────────
def _visual():
    supp = {"prompt": "S1", "narration_anchor": "Sigue el agua", "art_profile": "", "raw_llm_prompt": "{}", "beat": 4,
            "persona": ["Carmen Cortés"], "anio": "1985"}
    return {"topic_id": "t78d", "chapters": [
        {"chapter_number": 1, "image_prompt": "CLIP VIEJO", "video_prompt": "MOV VIEJO", "voz_clip": "la voz",
         "veo_position": "start", "subject_ref": "main_subject", "narration_anchor": "Primer párrafo del beat uno",
         "image_sensible": False, "image_f8": {"beat": 1, "persona": ["Arcadio Fernández"], "anio": "1985"},
         "supplemental_image_prompts": [supp]},
        {"chapter_number": 5, "image_prompts": [
            {"prompt": "A", "narration_anchor": "Sigue el agua", "beat": 4, "persona": ["Arcadio Fernández"],
             "_f8_rehecha": "NO dead bodies in this image"},
            {"prompt": "B", "narration_anchor": "Sigue el agua", "beat": 4, "persona": ["Carmen Cortés"]},
            {"prompt": "C", "narration_anchor": "Sigue el agua", "beat": 4, "persona": []},
            {"prompt": "D", "narration_anchor": "Sigue el agua", "beat": 4, "persona": ["Carmen Cortés"],
             "aspecto_fuente": "rasgos"},
            {"prompt": "E", "narration_anchor": "Sigue el agua", "beat": 4, "persona": ["Javier Moscoso"]}]}]}


@pytest.fixture
def paso(tmp_path, monkeypatch, opus):
    monkeypatch.setattr(m3, "STEPS_DIR", tmp_path / "_steps")
    monkeypatch.setattr(m3, "OUTPUT_DIR", tmp_path / "output")
    (tmp_path / "_steps" / "t78d").mkdir(parents=True)
    vpath = tmp_path / "_steps" / "t78d" / "03_visual.json"
    vpath.write_text(json.dumps(_visual(), ensure_ascii=False), encoding="utf-8")
    monkeypatch.setattr(fm, "rasgos_vigentes", lambda t, v=None: (dict(RASGOS), "ok"))
    monkeypatch.setattr(m3, "_geo_era", lambda tid, n: {})
    monkeypatch.setattr(m3, "_con_f8", lambda t, tid, chs: {**t, "_f8": _topic()["_f8"]})
    movs = []
    monkeypatch.setattr(m3, "_seedream_video_prompt", lambda img, voz, label: movs.append((img, voz)) or "MOV NUEVO")
    llamadas = []
    real = m3._f8_refill

    def refill(*a, **k):
        llamadas.append((a[3].get("prompt"), a[5], k.get("personas_fijas")))
        return real(*a, **k)
    monkeypatch.setattr(m3, "_f8_refill", refill)
    sk = {"chapters": [{"chapter_number": n} for n in range(1, 8)]}
    nr = {"chapters": [{"chapter_number": n, "narration": NARR} for n in range(1, 8)]}
    return {"vpath": vpath, "llamadas": llamadas, "movs": movs, "sk": sk, "nr": nr, "tmp": tmp_path}


def test_lista_sin_llamar(paso):
    filas = m3.fotos_aspecto("t78d", json.loads(paso["vpath"].read_text(encoding="utf-8")), RASGOS)
    acc = {f["foto"]: f["accion"] for f in filas}
    assert acc == {"ch01_img_01": "rehacer", "ch01_supp_01": "rehacer", "ch05_img_01": "rehacer",
                   "ch05_img_02": "rehacer", "ch05_img_04": "ya_rasgos", "ch05_img_05": "sin_rasgos"}
    assert paso["llamadas"] == []


def test_paso_rehace_pasa_la_nota_y_es_idempotente(paso):
    topic = {"id": "t78d", "documented_people": [dict(CARMEN), dict(ARCADIO)]}
    res = m3.rehacer_aspecto_personas(topic, paso["sk"], paso["nr"], "t78d")
    notas = {p: n for p, n, _ in paso["llamadas"]}
    assert notas == {"CLIP VIEJO": "", "S1": "", "A": "NO dead bodies in this image", "B": ""}   # adenda 1.2
    assert {tuple(f) for _, _, f in paso["llamadas"]} == {("Arcadio Fernández",), ("Carmen Cortés",)}
    v = json.loads(paso["vpath"].read_text(encoding="utf-8"))
    c1, c5 = v["chapters"][0], v["chapters"][1]
    assert c1["image_prompt"] != "CLIP VIEJO" and c1["image_f8"]["aspecto_fuente"] == "rasgos"
    assert c1["video_prompt"] == "MOV NUEVO" and paso["movs"] == [(c1["image_prompt"], "la voz")]   # adenda 1.3
    assert res["movimiento"] == [{"foto": "ch01_img_01", "viejo": "MOV VIEJO", "nuevo": "MOV NUEVO"}]
    s = c1["supplemental_image_prompts"][0]
    assert s["aspecto_fuente"] == "rasgos" and set(s) <= {"prompt", "narration_anchor", "art_profile", "raw_llm_prompt",
                                                         "beat", "sensible", "motivos", *m3.CLAVES_F8_PAPEL}
    assert [i.get("aspecto_fuente") for i in c5["image_prompts"]] == ["rasgos", "rasgos", None, "rasgos", None]
    assert c5["image_prompts"][0]["_f8_rehecha"] == "NO dead bodies in this image"
    md5 = hashlib.md5(paso["vpath"].read_bytes()).hexdigest()
    n = len(paso["llamadas"])
    res2 = m3.rehacer_aspecto_personas(topic, paso["sk"], paso["nr"], "t78d")
    assert len(paso["llamadas"]) == n and hashlib.md5(paso["vpath"].read_bytes()).hexdigest() == md5
    assert res2["rehechas"] == [] and paso["movs"] == [(c1["image_prompt"], "la voz")]


def test_paso_persona_distinta_no_se_reintenta(paso, opus):
    opus["persona"] = ["Javier Moscoso"]
    topic = {"id": "t78d", "documented_people": [dict(CARMEN), dict(ARCADIO)]}
    res = m3.rehacer_aspecto_personas(topic, paso["sk"], paso["nr"], "t78d")
    assert len(res["persona_distinta"]) == 4 and res["rehechas"] == [] and paso["movs"] == []
    v = json.loads(paso["vpath"].read_text(encoding="utf-8"))
    assert v["chapters"][0]["image_prompt"] == "CLIP VIEJO"
    assert v["chapters"][0]["image_f8"]["_rasgos_refill"] == "persona_distinta"
    assert v["chapters"][1]["image_prompts"][0]["prompt"] == "A"
    n = len(paso["llamadas"])
    m3.rehacer_aspecto_personas(topic, paso["sk"], paso["nr"], "t78d")
    assert len(paso["llamadas"]) == n


def test_paso_salta_las_fotos_de_qa(paso):
    qa = paso["tmp"] / "output" / "t78d" / "assets" / m3.QA_BACKUPS_DIR
    qa.mkdir(parents=True)
    (qa / "ch05_img_02.png.20261105_0900.bak.png").write_bytes(b"x")
    (qa / "ch05_img_01_native.png.20261105_0900.bak.png").write_bytes(b"x")   # otro archivo de la foto: no cuenta
    topic = {"id": "t78d", "documented_people": [dict(CARMEN), dict(ARCADIO)]}
    res = m3.rehacer_aspecto_personas(topic, paso["sk"], paso["nr"], "t78d")
    assert [f["foto"] for f in res["filas"] if f["accion"] == "qa"] == ["ch05_img_02"]
    assert "B" not in {p for p, _, _ in paso["llamadas"]} and "A" in {p for p, _, _ in paso["llamadas"]}
    assert json.loads(paso["vpath"].read_text(encoding="utf-8"))["chapters"][1]["image_prompts"][1]["prompt"] == "B"


def test_paso_sin_rasgos_vigentes_no_llama(paso, monkeypatch):
    monkeypatch.setattr(fm, "rasgos_vigentes", lambda t, v=None: ({}, "sin rasgos.json"))
    md5 = hashlib.md5(paso["vpath"].read_bytes()).hexdigest()
    res = m3.rehacer_aspecto_personas({"id": "t78d"}, paso["sk"], paso["nr"], "t78d")
    assert paso["llamadas"] == [] and res["rasgos"] == "sin rasgos.json"
    assert hashlib.md5(paso["vpath"].read_bytes()).hexdigest() == md5


# ── fase1_5 --only aspecto ───────────────────────────────────────────────────────────────────────────
def test_fase1_5_only_aspecto():
    assert "aspecto" in fase1_5.VALID_FROM_STEPS
    o = fase1_5._PIPELINE_ORDER
    assert o.index("m03") < o.index("aspecto") < o.index("assemble")
    src = open(fase1_5.__file__, encoding="utf-8").read()
    i_madre, i_asp, i_asm = (src.index("generate_foto_madre_for_topic(t, topic_id)"),
                             src.index("rehacer_aspecto_personas(topic, skeleton"), src.index("assemble_final_script(topic_id)"))
    assert i_madre < i_asp < i_asm                                         # después de foto madre, antes de assemble
