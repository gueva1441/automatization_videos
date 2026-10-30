"""F58 A3 — la foto de un paquete sale por `_render_prompts_seedream` del cap 1 con tres kwargs nuevos de default
byte-idéntico: `clip_apertura` (sin el bloque OPENING MOTION CLIP), `sin_cartel` (text_in_image apagado antes de armar)
y `composicion` (una oración después de la técnica, antes del estilo). Sin red: Opus falso; los casos reales leen
`_steps/123bbb64…` (Wittenoom) con skip si no está. La comparación «a hoy» carga las versiones de HEAD con `git show`."""
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
TID = "123bbb64-9fca-4395-8bf4-57d60e219ef1"
STEPS = m3.STEPS_DIR / TID
COMPOSICION = ("The person fills the right half of the frame, face and torso large; the left half is dark, "
               "uncluttered negative space.")
CLIP = "OPENING MOTION CLIP"

SLOTS = {"subject": "a young miner", "action": "posing stiffly for a family photograph", "gaze_interaction": "eyes down",
         "props_detail": "a bandaged foot", "setting": "the yard of a company house", "lighting": "hard midday light",
         "color_palette": "ochre", "shot_scale": "medium", "camera_angle": "eye-level", "lens_technique": "50mm lens",
         "mood": "still", "style": "documentary", "hard_fact_ids": [], "foto_madre_ref": [],
         "text_in_image": {"present": True, "text": "DANGER", "font": "stencil", "location": "on the gate"},
         "year": "1962", "people_group": []}


# ─────────────────────────── datos ───────────────────────────
def _topic():
    db = json.loads((ROOT / "data" / "topics_db.json").read_text(encoding="utf-8"))
    ts = db.get("topics", db) if isinstance(db, dict) else db
    return next((t for t in ts if t.get("id") == TID or t.get("topic_id") == TID), None)


def _wittenoom():
    """Topic de producción con `_f8` como m03_visual.assign_visual_prompts (sin asegurar_canon: el canon ya está en
    topics_db), cap 1 del skeleton y el gancho entero."""
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
    cap1 = next(c for c in skel if c["chapter_number"] == 1)
    gancho = next(c for c in narr if c["chapter_number"] == 1)["narration"].strip()
    return {**topic, "_f8": f8}, cap1, gancho


def _anclas(gancho, n=3):
    return re.split(r"(?<=[.!?])\s+", gancho)[:n]


def _items_reales():
    f = STEPS / "03_visual.json"
    if not f.exists():
        pytest.skip("sin 03_visual.json de Wittenoom")
    v = json.loads(f.read_text(encoding="utf-8"))
    out = [(json.loads(it["raw_llm_prompt"]), it.get("anio") or "")
           for ch in v["chapters"] for it in ch.get("supplemental_image_prompts") or [] if it.get("raw_llm_prompt")]
    if not out:
        pytest.skip("Wittenoom sin raw_llm_prompt")
    return out


def _fake(seen: dict):
    """Opus falso: guarda el user prompt y devuelve N casilleros fijos (N = ítems del esquema o anclas del pedido)."""
    def _f(prompt, system_instruction=None, response_schema=None, description=None, **_):
        seen["prompt"] = prompt
        n = (response_schema or {}).get("minItems") or (response_schema or {}).get("maxItems") \
            or len(re.findall(r"^\s+\[\d+\] «", prompt, re.M)) or 1
        return {"image_prompts": [json.loads(json.dumps(SLOTS)) for _ in range(n)]}
    return _f


def _old(path: str, name: str):
    """La versión de HEAD («hoy») del módulo, cargada como módulo aparte; sin git, skip."""
    try:
        src = subprocess.run(["git", "show", f"HEAD:{path}"], capture_output=True, check=True, cwd=ROOT).stdout
    except Exception as e:                                                   # noqa: BLE001
        pytest.skip(f"sin git show: {e}")
    mod = types.ModuleType(name)
    mod.__file__ = str(ROOT / path)
    sys.modules[name] = mod
    try:
        exec(compile(src.decode("utf-8"), f"HEAD:{path}", "exec"), mod.__dict__)
    finally:
        sys.modules.pop(name, None)
    return mod


# ─────────────────────────── byte-idéntico ───────────────────────────
def test_armar_sin_el_kwarg_es_byte_identico_a_hoy():
    old = _old("script_engine/m03_imagenes_v3.py", "_f58_old_v3")
    assert "composicion" not in old.armar.__code__.co_varnames
    for slots, anio in _items_reales():
        hoy = old.armar(slots, anio)
        assert v3.armar(slots, anio)["prompt"] == hoy["prompt"]
        assert v3.armar(slots, anio, None, composicion="")["prompt"] == hoy["prompt"]
        assert v3.armar(slots, anio)["partes"]["composicion"] == ""
        assert {k: p for k, p in v3.armar(slots, anio)["partes"].items() if k != "composicion"} == hoy["partes"]


def test_armar_con_grupos_reales_byte_identico():
    topic, _, _ = _wittenoom()
    grupos = {g["id"]: g for g in topic.get("people_groups") or [] if isinstance(g, dict) and g.get("id")}
    for slots, anio in _items_reales():
        assert v3.armar(slots, anio, grupos)["prompt"] == v3.armar(slots, anio, grupos, composicion="")["prompt"]


def test_step2_sin_el_kwarg_es_byte_identico_a_hoy():
    topic, cap1, gancho = _wittenoom()
    old = _old("script_engine/m03_visual.py", "_f58_old_m3")
    assert "clip_apertura" not in old._build_seedream_prompt_step2.__code__.co_varnames
    anclas = _anclas(gancho)
    hoy = old._build_seedream_prompt_step2(topic, cap1, gancho, anclas, "EXTRA", ["1962", "1962", "1962"])
    assert m3._build_seedream_prompt_step2(topic, cap1, gancho, anclas, "EXTRA", ["1962", "1962", "1962"]) == hoy
    assert m3._build_seedream_prompt_step2(topic, cap1, gancho, anclas, "EXTRA", ["1962", "1962", "1962"],
                                           clip_apertura=True) == hoy
    assert CLIP in hoy                                                      # el hook lleva el bloque hoy


def test_render_sin_los_kwargs_es_byte_identico_a_hoy(monkeypatch):
    topic, cap1, gancho = _wittenoom()
    old = _old("script_engine/m03_visual.py", "_f58_old_m3")
    plan = {"anchors": [{"anchor": a} for a in _anclas(gancho)]}
    t = {**topic, "_f8": dict(topic["_f8"], refill=True)}
    s_old, s_new = {}, {}
    monkeypatch.setattr(old, "_llamar_casilleros", _fake(s_old))
    monkeypatch.setattr(m3, "_llamar_casilleros", _fake(s_new))
    hoy = old._render_prompts_seedream(t, cap1, gancho, plan, 1)
    assert m3._render_prompts_seedream(t, cap1, gancho, plan, 1) == hoy
    assert m3._render_prompts_seedream(t, cap1, gancho, plan, 1, composicion="", sin_cartel=False,
                                       clip_apertura=True) == hoy
    assert s_old["prompt"] == s_new["prompt"] and CLIP in s_new["prompt"]
    assert len(hoy["image_prompts"]) == 3


# ─────────────────────────── los kwargs ───────────────────────────
def test_clip_apertura_false_saca_el_bloque():
    cap = {"chapter_number": 1, "role": "hook", "narrative_intent": "hook", "title": "t"}
    con = m3._build_seedream_prompt_step2({}, cap, "n", ["a", "b", "c"])
    sin = m3._build_seedream_prompt_step2({}, cap, "n", ["a", "b", "c"], clip_apertura=False)
    assert CLIP in con and CLIP not in sin
    i = con.index("\n" + CLIP)
    bloque = con[i:con.index("\n", i + 1) + 1]                              # el bloque es UNA línea con sus saltos
    assert con.replace(bloque, "") == sin
    cap2 = {**cap, "narrative_intent": "development"}
    assert m3._build_seedream_prompt_step2({}, cap2, "n", ["a"]) == \
        m3._build_seedream_prompt_step2({}, cap2, "n", ["a"], clip_apertura=False)


def _render(monkeypatch, **kw):
    topic, cap1, gancho = _wittenoom()
    anclas = _anclas(gancho)
    f8 = dict(topic["_f8"], refill=True, force_assign=v3.assign_beats(gancho, anclas, topic["_f8"]["beats"][1]))
    seen = {}
    monkeypatch.setattr(m3, "_llamar_casilleros", _fake(seen))
    out = m3._render_prompts_seedream({**topic, "_f8": f8}, cap1, gancho, {"anchors": [{"anchor": a} for a in anclas]},
                                      1, **kw)
    return out, seen, anclas


def test_tres_anclas_tres_items_y_sin_clip(monkeypatch):
    out, seen, anclas = _render(monkeypatch, clip_apertura=False)
    assert len(out["image_prompts"]) == 3
    assert [it["narration_anchor"] for it in out["image_prompts"]] == anclas
    assert CLIP not in seen["prompt"]
    for a in anclas:
        assert f"«{a}»" in seen["prompt"]
    _, seen_def, _ = _render(monkeypatch)
    assert CLIP in seen_def["prompt"]


def test_sin_cartel(monkeypatch):
    con, _, _ = _render(monkeypatch)
    sin, _, _ = _render(monkeypatch, sin_cartel=True)
    cartel = v3.frase_cartel(SLOTS["text_in_image"])
    for it in con["image_prompts"]:
        assert cartel in it["prompt"] and not it["prompt"].endswith(v3.NO_TEXT)
    for it in sin["image_prompts"]:
        assert cartel not in it["prompt"] and "DANGER" not in it["prompt"]
        assert it["prompt"].endswith(v3.NO_TEXT)
        assert json.loads(it["raw_llm_prompt"])["text_in_image"]["present"] is False
        assert "_f8_texto_fuera" not in it


def test_composicion_en_su_lugar_y_f8_la_deja(monkeypatch):
    out, _, _ = _render(monkeypatch, composicion=COMPOSICION, sin_cartel=True)
    tecnica = v3.oracion("medium shot, eye-level, 50mm lens")
    for it in out["image_prompts"]:
        assert f"{tecnica} {COMPOSICION} {v3.ESTILO_C.format(anio=it['anio'])}" in it["prompt"]
    slots = json.loads(json.dumps(SLOTS))
    armado = v3.armar(slots, "1962", None, composicion=COMPOSICION)
    partes = list(armado["partes"])
    assert partes[partes.index("tecnica") + 1] == "composicion" and partes[partes.index("composicion") + 1] == "estilo"
    assert armado["partes"]["composicion"] == COMPOSICION
    prosa, _ = v3.f8_backstop(armado["prompt"], slots, False)
    assert COMPOSICION in prosa                                            # excepción declarada a D4 (LR_RE)
    assert not v3.LR_RE.search(COMPOSICION)
    assert v3.fix_counts_lr(COMPOSICION) == COMPOSICION


def test_reparto_como_f8_refill_sin_fix_cap(monkeypatch):
    def no(*a, **k):
        raise AssertionError("_f8_fix_cap no debe correr con refill=True")
    monkeypatch.setattr(m3, "_f8_fix_cap", no)
    out, _, anclas = _render(monkeypatch, composicion=COMPOSICION, sin_cartel=True, clip_apertura=False)
    topic, _, gancho = _wittenoom()
    esperado = v3.assign_beats(gancho, anclas, topic["_f8"]["beats"][1])
    assert [(it["beat"], it["cerrada"]) for it in out["image_prompts"]] == [(a["beat"], a["cerrada"]) for a in esperado]
    assert all("prompt" in it and "raw_llm_prompt" in it and "anio" in it for it in out["image_prompts"])
