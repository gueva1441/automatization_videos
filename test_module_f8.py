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
    assert DEFAULTS["min_beats_dev_cap"] == 2 and DEFAULTS["max_beats"] == 12
    assert me.MIN_BEATS_DEV_CAP == 2
    _, hard, _, _ = me.validate(good(), POOL)              # 8 beats: caps 2, 3, 4 y 6 con uno solo
    assert _dev_msgs(hard) and "[2, 3, 4, 6]" in _dev_msgs(hard)[0]
    assert "al menos 2 beats cada uno" in me.RULES


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
    assert not _dev_msgs(hard)
    assert "al menos" not in me.rules_text(me.CAP_WORDS, 7, 8, 1).split("\n")[1]


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
