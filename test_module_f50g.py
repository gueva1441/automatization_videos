"""F50g-A — el aspecto del grupo (`people_groups[].appearance` del canon) va al prompt de foto por código: una oración
por grupo de `people_group`, en el orden de Opus, entre sujeto y mirada; sin grupo o sin appearance, nada. Offline."""
import json
from pathlib import Path

import pytest

from script_engine import m03_imagenes_v3 as v3

ROOT = Path(__file__).resolve().parent
SLOTS = {"subject": "a miner", "action": "loading ore", "gaze_interaction": "eyes down", "props_detail": "a sack",
         "setting": "the mill yard", "lighting": "harsh noon", "color_palette": "ochre", "shot_scale": "wide",
         "camera_angle": "eye-level", "lens_technique": "35mm", "text_in_image": {"present": False}}
GRUPOS = {"miners": {"id": "miners", "appearance": "Lean men with sun-darkened skin and dark hair"},
          "families": {"id": "families", "appearance": "olive-skinned women and children."},
          "police": {"id": "police", "appearance": ""}}


def test_f50g_a_un_grupo_va_entre_sujeto_y_lugar():
    # F51a: sin la mirada, el aspecto queda entre el sujeto y el lugar + año
    p = v3.armar({**SLOTS, "people_group": ["miners"]}, "1962", GRUPOS)["prompt"]
    assert p.startswith("A miner. Loading ore. Lean men with sun-darkened skin and dark hair. The mill yard, 1962.")


def test_f50g_a_dos_grupos_en_el_orden_de_people_group():
    a = v3.armar({**SLOTS, "people_group": ["families", "miners"]}, "1962", GRUPOS)["partes"]["aspecto"]
    assert a == "Olive-skinned women and children. Lean men with sun-darkened skin and dark hair."


def test_f50g_a_sin_grupo_el_prompt_es_el_de_hoy():
    hoy = v3.armar(SLOTS, "1962")["prompt"]
    assert v3.armar({**SLOTS, "people_group": []}, "1962", GRUPOS)["prompt"] == hoy
    assert v3.armar({**SLOTS, "people_group": ["miners"]}, "1962")["prompt"] == hoy      # sin canon: nada


def test_f50g_a_grupo_sin_appearance_o_desconocido_no_agrega_nada():
    hoy = v3.armar(SLOTS, "1962")["prompt"]
    assert v3.armar({**SLOTS, "people_group": ["police"]}, "1962", GRUPOS)["prompt"] == hoy
    assert v3.armar({**SLOTS, "people_group": ["no_existe"]}, "1962", GRUPOS)["prompt"] == hoy


def test_f50g_a_el_resto_de_partes_no_cambia():
    sin = v3.armar(SLOTS, "1962")["partes"]
    con = v3.armar({**SLOTS, "people_group": ["miners", "families"]}, "1962", GRUPOS)["partes"]
    assert {k: v for k, v in con.items() if k != "aspecto"} == {k: v for k, v in sin.items() if k != "aspecto"}
    assert list(con) == list(sin)                                        # mismo orden de partes


def test_f50g_a_la_foto_1_2_de_wittenoom():
    """La 1/2 con los casilleros guardados y el canon de producción: lleva el aspecto de su grupo."""
    tid = "123bbb64-9fca-4395-8bf4-57d60e219ef1"
    canon_f = ROOT / "lab" / "hyperframes" / "f50f" / "canon_f50f.json"      # el canon de producción (F50f B)
    vivo = ROOT / "data" / "scripts" / "_steps" / tid / "03_visual.json"
    if not (canon_f.exists() and vivo.exists()):
        pytest.skip("sin los datos de Wittenoom")
    canon = json.loads(canon_f.read_text(encoding="utf-8"))
    grupos = {g["id"]: g for g in canon["people_groups"]}
    v = json.loads(vivo.read_text(encoding="utf-8"))
    cap1 = next(c for c in v["chapters"] if c["chapter_number"] == 1)
    it = cap1["supplemental_image_prompts"][0]                      # foto 2 del cap 1 (la 1 es el cuadro Veo)
    slots = json.loads(it["raw_llm_prompt"])
    armado = v3.armar(slots, it["anio"], grupos)
    esperado = " ".join(v3.oracion(grupos[g]["appearance"]) for g in slots["people_group"]
                        if grupos.get(g, {}).get("appearance"))
    assert esperado and armado["partes"]["aspecto"] == esperado
    print("\n1/2:", armado["prompt"])
