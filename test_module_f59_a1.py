"""F59 A1 — `m03_visual.armar_item` (scrub + fix_text_slot + armar + f8_backstop + _sacar_frases_con_texto) es la misma
función que el bucle de `_render_prompts_seedream` tenía adentro: contra la copia FIJA `lab/hyperframes/f59/a1_fixture.json`
(Wittenoom, caps 2–6, supp de 1 y 7, y la foto del clip) da `prompt`/`raw_llm_prompt`/`sensible`/`motivos`/`_f8_*`
byte-idénticos. Y `_render_prompts_seedream` entero, con Opus falso, es byte-idéntico a la versión de ANTES del módulo
(commit ANTES_A1, cargado con `git show`). Sin red, US$ 0."""
import json
import re
import subprocess
import sys
import types
from pathlib import Path

import pytest

from script_engine import m03_expediente as mexp
from script_engine import m03_imagenes_v3 as v3
from script_engine import m03_visual as m3

ROOT = Path(__file__).resolve().parent
FIXTURE = ROOT / "lab" / "hyperframes" / "f59" / "a1_fixture.json"
ANTES_A1 = "f7265fe"       # el último commit con el bucle adentro de _render_prompts_seedream (F59 Etapa 0)
TID = "123bbb64-9fca-4395-8bf4-57d60e219ef1"
STEPS = m3.STEPS_DIR / TID
# `_f8_slots_scrub` NO entra acá: el fixture guarda los casilleros DESPUÉS del scrub (raw_llm_prompt se escribe post-scrub),
# así que el scrub ya no tiene nada que sacar y la lista no se puede reproducir (ver test_f8_slots_scrub_no_reproducible).
COMPARAR = ("prompt", "raw_llm_prompt", "sensible", "motivos", "_f8_problemas", "_f8_texto_fuera")


def _fixture() -> dict:
    if not FIXTURE.exists():
        pytest.skip(f"sin {FIXTURE.name}: correr lab/hyperframes/f59/a1_fixture.py")
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


_FX = json.loads(FIXTURE.read_text(encoding="utf-8")) if FIXTURE.exists() else {"items": []}


def _armar(fx: dict, item: dict) -> dict:
    grupos = {g["id"]: g for g in fx["people_groups"] if isinstance(g, dict) and g.get("id")}
    ent = item["entrada"]
    it = json.loads(json.dumps(ent["casilleros"]))                     # copia: el fixture no se toca
    out = m3.armar_item(it, ent["anio"], grupos, ent["escala"], fx["lang"], anio_fuente=ent["anio_fuente"])
    assert out is it
    return out


@pytest.mark.parametrize("item", _FX["items"], ids=[i["id"] for i in _FX["items"]])
def test_armar_item_byte_identico_al_fixture(item):
    fx = _fixture()
    out = _armar(fx, item)
    got = {k: out[k] for k in COMPARAR if k in out}
    esperado = {k: item["esperado"][k] for k in COMPARAR if k in item["esperado"]}
    assert got == esperado
    ent = item["entrada"]
    assert out["anio"] == ent["anio"] and out["anio_fuente"] == ent["anio_fuente"] and out["art_profile"] == ""


_CON_SCRUB = [i for i in _FX["items"] if "_f8_slots_scrub" in i["esperado"]]


@pytest.mark.xfail(strict=True, reason="causa externa: 03_visual.json guarda los casilleros YA scrubeados (raw_llm_prompt "
                   "se escribe después de scrub_slots), así que el scrub no tiene nada que sacar y `_f8_slots_scrub` no se "
                   "puede regenerar desde el fixture; el prompt sí sale byte-idéntico (test de arriba)")
@pytest.mark.parametrize("item", _CON_SCRUB, ids=[i["id"] for i in _CON_SCRUB])
def test_f8_slots_scrub_no_reproducible_desde_casilleros_scrubeados(item):
    fx = _fixture()
    out = _armar(fx, item)
    assert out.get("_f8_slots_scrub") == item["esperado"]["_f8_slots_scrub"]


@pytest.mark.parametrize("item", _CON_SCRUB, ids=[i["id"] for i in _CON_SCRUB])
def test_lo_scrubeado_ya_no_esta_en_los_casilleros(item):
    """Confirma la causa: la frase anotada en `_f8_slots_scrub` ya no está en el casillero del fixture."""
    for nota in item["esperado"]["_f8_slots_scrub"]:
        slot, frase = nota.split(": ", 1)
        assert frase not in (item["entrada"]["casilleros"].get(slot) or "")


def test_fixture_cubre_todos_los_caps():
    fx = _fixture()
    assert {i["cap"] for i in fx["items"]} == set(range(1, 8))
    assert {i["id"] for i in fx["items"] if i["id"].endswith("_f8")} == {"ch01_f8", "ch07_f8"}
    assert all(i["id"].startswith(("ch01_supp", "ch07_supp")) for i in fx["items"] if "_supp_" in i["id"])


# ─────────────────────────── _render_prompts_seedream antes/después (Opus falso) ───────────────────────────
SLOTS = {"subject": "a young miner", "action": "posing stiffly for a family photograph", "gaze_interaction": "eyes down",
         "props_detail": "a bandaged foot", "setting": "the yard of a company house", "lighting": "hard midday light",
         "color_palette": "ochre", "shot_scale": "medium", "camera_angle": "eye-level", "lens_technique": "50mm lens",
         "mood": "still", "style": "documentary", "hard_fact_ids": [], "subject_ref": "establishing_shot",
         "foto_madre_ref": ["__subject__"], "emotional_rank": "R2",
         "text_in_image": {"present": True, "text": "DANGER ahead of the mine", "font": "stencil", "location": "on the gate"},
         "year": "1962", "people_group": ["mine_and_mill_workers"]}
# variantes: una con cliché de manos y palabra prohibida (scrub), una interior (el filtro place saca __subject__),
# una sin año válido (anio_final cae al respaldo del expediente), una con texto en español (fix_text_slot lo apaga)
VARIANTES = [
    SLOTS,
    {**SLOTS, "subject": "a miner, knuckles white, blood on his shirt", "action": "trembling, he waits",
     "subject_ref": "interior_scene", "shot_scale": "close"},
    {**SLOTS, "year": "circa 1960s", "subject_ref": "main_subject", "shot_scale": "detail"},
    {**SLOTS, "text_in_image": {"present": True, "text": "sin registro", "font": "", "location": "over the door"}},
]


def _topic():
    db = json.loads((ROOT / "data" / "topics_db.json").read_text(encoding="utf-8"))
    ts = db.get("topics", db) if isinstance(db, dict) else db
    return next((t for t in ts if t.get("id") == TID or t.get("topic_id") == TID), None)


def _wittenoom():
    topic = _topic()
    if not topic or not (STEPS / "01a_skeleton.json").exists() or not (STEPS / "01b_narration.json").exists():
        pytest.skip("sin los datos de Wittenoom")
    narr = json.loads((STEPS / "01b_narration.json").read_text(encoding="utf-8"))["chapters"]
    skel = json.loads((STEPS / "01a_skeleton.json").read_text(encoding="utf-8"))["chapters"]
    beats = v3.load_beats(topic, m3.STEPS_DIR)
    if not beats:
        pytest.skip("Wittenoom sin escaleta")
    f8 = {"beats": beats, "year": v3.topic_year(topic, beats), "lang": v3.place_language(topic),
          "fuentes": mexp.fuentes(TID, m3.STEPS_DIR),
          "anio_prev": {n: mexp.anio_previo(narr, n) for n in range(1, m3.EXPECTED_CHAPTER_COUNT + 1)}}
    cap = next(c for c in skel if c["chapter_number"] == 2)
    narracion = next(c for c in narr if c["chapter_number"] == 2)["narration"].strip()
    return {**topic, "_f8": f8}, cap, narracion


def _fake(seen: dict):
    def _f(prompt, system_instruction=None, response_schema=None, description=None, **_):
        seen["prompt"] = prompt
        return {"image_prompts": [json.loads(json.dumps(v)) for v in VARIANTES]}
    return _f


def _old(path: str, name: str):
    try:
        src = subprocess.run(["git", "show", f"{ANTES_A1}:{path}"], capture_output=True, check=True, cwd=ROOT).stdout
    except Exception as e:                                                   # noqa: BLE001
        pytest.skip(f"sin git show: {e}")
    assert b"def armar_item(" not in src, f"{ANTES_A1} ya tiene armar_item: no es la versión de antes"
    mod = types.ModuleType(name)
    mod.__file__ = str(ROOT / path)
    sys.modules[name] = mod
    try:
        exec(compile(src.decode("utf-8"), f"{ANTES_A1}:{path}", "exec"), mod.__dict__)
    finally:
        sys.modules.pop(name, None)
    return mod


@pytest.mark.parametrize("kw", [{}, {"sin_cartel": True}, {"composicion": "The person fills the right half of the frame."}],
                         ids=["default", "sin_cartel", "composicion"])
def test_render_prompts_seedream_byte_identico_a_antes(monkeypatch, kw):
    topic, cap, narracion = _wittenoom()
    old = _old("script_engine/m03_visual.py", "_f59_old_m3")
    anclas = re.split(r"(?<=[.!?])\s+", narracion)[:len(VARIANTES)]
    plan = {"anchors": [{"anchor": a} for a in anclas]}
    t = {**topic, "_f8": dict(topic["_f8"], refill=True)}        # refill=True: sin _f8_fix_cap (que llamaría a Opus)
    s_old, s_new = {}, {}
    monkeypatch.setattr(old, "_llamar_casilleros", _fake(s_old))
    monkeypatch.setattr(m3, "_llamar_casilleros", _fake(s_new))
    antes = old._render_prompts_seedream(t, cap, narracion, plan, 2, **kw)
    despues = m3._render_prompts_seedream(t, cap, narracion, plan, 2, **kw)
    assert json.dumps(despues, ensure_ascii=False, indent=2) == json.dumps(antes, ensure_ascii=False, indent=2)
    assert s_old["prompt"] == s_new["prompt"]
    its = despues["image_prompts"]
    assert len(its) == len(VARIANTES)
    assert "_f8_slots_scrub" in its[1] and its[1]["foto_madre_ref"] == []           # scrub + filtro place (interior)
    assert its[2]["anio_fuente"] != "1) el casillero `year` del modelo"               # cayó al respaldo
    assert its[3]["texto_en_imagen"] is False and "_f8_slots_scrub" in its[3]         # texto en español apagado
    for a, d in zip(antes["image_prompts"], its):
        assert list(d.keys()) == list(a.keys())                                        # mismo orden de claves
