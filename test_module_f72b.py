"""
test_module_f72b.py — F72b (HANDOFF_F72b §A): la pregunta de cierre es la ÚLTIMA oración de la voz del cap
(`voz_utils.oraciones_de_texto`), fuente «voz-final»; si termina en «?», la pregunta, fuente «voz-pregunta». El `cierre`
de la escaleta ya no se lee (se borraron el emparejamiento «voz-alineada» y el respaldo literal «escaleta» de F38e B4).
Sin red. Lee de lab/ (entradas de Wittenoom congeladas en lab/hyperframes/f72/b_fase1_wittenoom) o es sintético.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from script_engine import gfx_layer as gl, gfx_realizador as gr  # noqa: E402

FASE1 = Path(__file__).resolve().parent / "lab" / "hyperframes" / "f72"
TOPIC = "b_fase1_wittenoom"


def test_voz_final_es_la_ultima_oracion_del_cap_aunque_el_cierre_diga_otra_cosa():
    real = {"beats": [{"n": 1, "cierre": "", "texto": "El dique no cedió. Llegó por encima."},
                      {"n": 2, "cierre": "El dique no cedió esa noche.",
                       "texto": "Pero el dique no cedió esa noche. Y para entender eso hay que volver atrás."}]}
    assert gr.pregunta_cierre_fuente(real) == ("Y para entender eso hay que volver atrás.", "voz-final")
    assert gr.pregunta_cierre(real) == "Y para entender eso hay que volver atrás."


def test_voz_pregunta_se_queda_como_hoy():
    real = {"beats": [{"n": 3, "cierre": "Otra cosa.", "texto": "Alguien lo sabía. ¿Quién decidió callar?"}]}
    assert gr.pregunta_cierre_fuente(real) == ("¿Quién decidió callar?", "voz-pregunta")
    assert gr.pregunta_cierre_fuente({"beats": [{"n": 1, "texto": "Y él dijo: «¿quién lo decidió?»"}]})[1] == "voz-pregunta"


def test_el_cierre_de_la_escaleta_ya_no_es_respaldo():
    assert gr.pregunta_cierre_fuente({"beats": [{"n": 2, "cierre": "Pregunta de la escaleta.", "texto": ""}]}) == (None, None)
    assert gr.pregunta_cierre_fuente({"beats": [{"n": 2, "cierre": "Sólo escaleta."}]}) == (None, None)
    assert gr.pregunta_cierre_fuente({"beats": []}) == (None, None)
    assert gr.pregunta_cierre_fuente({}) == (None, None)
    assert gr.FUENTES_CIERRE == ("voz-pregunta", "voz-final")


def test_la_voz_es_la_de_todos_los_beats_del_cap_y_el_ultimo_beat_sin_voz_no_borra_la_pregunta():
    real = {"beats": [{"n": 1, "texto": "Primera. Última del cap."}, {"n": 2, "cierre": "Algo.", "texto": ""}]}
    assert gr.pregunta_cierre_fuente(real) == ("Última del cap.", "voz-final")


def test_closing_question_guarda_la_fuente_y_dura_la_lectura(tmp_path):
    txt = "Lo que sobró de la mina, sí."
    resolved: dict = {}
    log: list[str] = []
    pausa = gl.closing_question(resolved, {"realizador": {"beats": [{"n": 9, "cierre": "Otra.", "texto": "Antes. " + txt}]}},
                                tmp_path, "ch07", 80.0, log)
    q = resolved["chapter_question"]
    assert q["text"] == txt and q["fuente"] == "voz-final" and q["duration"] == round(len(txt) / 15, 3)
    assert pausa == gl.pausa_de_cierre(resolved)
    assert any("voz-final" in l for l in log)


def test_wittenoom_los_7_caps_dan_la_ultima_oracion_de_la_voz_aprobada():
    carga = gr.cargar(TOPIC, FASE1)
    assert carga is not None
    esc, pars = carga["escaleta"], carga["parrafos"]

    def real(cap: int) -> dict:
        return {"beats": [{"n": int(b["n"]), "cierre": str(b.get("cierre") or "").strip(),
                           "texto": " ".join(p["texto"] for p in pars
                                             if int(p["cap"]) == cap and int(p.get("beat") or 0) == int(b["n"]))}
                          for b in esc["beats"] if int(b["cap"]) == cap]}
    esperado = {
        1: "Dos años antes de la foto, en Madrid, hubo un baile.",
        2: "Del avión, a la tierra más roja que Víctor había visto en su vida.",
        3: "Ese mismo año, un recién casado de Madrid se bajaba de un avión en esa misma pista de polvo.",
        4: "Creyeron que se llevaban de Wittenoom un hijo y nada más.",
        5: "Y no fue el único que se llevó Wittenoom adentro.",
        6: "En esa tierra vivía un hombre que no podía irse.",
        7: "Lo que sobró de la mina, sí.",
    }
    for cap, txt in esperado.items():
        assert gr.pregunta_cierre_fuente(real(cap)) == (txt, "voz-final"), cap


def test_las_entradas_congeladas_son_json():
    for f in ("01a_escaleta.json", "01b_narracion_v3.json"):
        assert json.loads((FASE1 / TOPIC / f).read_text(encoding="utf-8"))
