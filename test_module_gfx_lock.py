"""test_module_gfx_lock.py — F1 capa gráfica: candado literal (D7).
Correr: python -m pytest test_module_gfx_lock.py -q
"""
import sys

import pytest

from script_engine.gfx_literal_lock import is_literal, lock, normalize, plan_strings

SOURCES = {
    "verified_facts[1]": "Algunas partes de Nueva Orleans quedaron bajo 15 pies (4.6 metros) de agua.",
    "verified_facts[4]": "Aproximadamente 6,500 personas, incluyendo hombres, mujeres y niños, estaban encarceladas.",
    "narration_ch02": "Ese día, el huracán Katrina desató su furia implacable sobre Nueva Orleans.",
    "skeleton.title": "La Tormenta Perfecta",
}


def test_string_literal_pasa():
    assert is_literal("4.6 metros", SOURCES, 2)
    assert is_literal("La Tormenta Perfecta", SOURCES, 2)


def test_numero_cambiado_falla():
    assert not is_literal("4.7 metros", SOURCES, 2)
    assert not is_literal("6,600 personas", SOURCES, 2)


def test_cromo_permitido_pasa():
    assert is_literal("CAPÍTULO 2", SOURCES, 2)
    assert is_literal("DETALLE", SOURCES, 2)
    assert not is_literal("CAPÍTULO 3", SOURCES, 2)   # cromo de OTRO cap no


def test_normalizacion_igual_al_lab():
    # lab: minúsculas + espacios colapsados; tildes y puntuación se RESPETAN
    assert normalize("  HURACÁN   Katrina ") == "huracán katrina"
    assert is_literal("HURACÁN KATRINA", SOURCES, 2)
    assert not is_literal("HURACAN KATRINA", SOURCES, 2)   # sin tilde no matchea (igual que el lab)


def test_lock_quita_bloques_no_literales_sin_reescribir():
    plan = {
        "title_card": {"kicker": "CAPÍTULO 2", "title": "La Tormenta Perfecta"},
        "callouts": [{"text": "4.6 metros", "start": 35.0}, {"text": "5 metros", "start": 40.0}],
        "archive_clipping": {"kicker": "Nueva Orleans", "headline": "inventado por el LLM", "body": "texto que nadie dijo"},
        "count_up": {"value_text": "6,500", "unit": "personas", "start": 50.0},
    }
    ok, rejected = lock(plan, SOURCES, chapter_number=2)
    assert [c["text"] for c in ok["callouts"]] == ["4.6 metros"]
    assert ok["archive_clipping"] is None
    assert ok["count_up"]["value_text"] == "6,500"
    assert ok["title_card"]["title"] == "La Tormenta Perfecta"
    assert {r["text"] for r in rejected} == {"5 metros", "inventado por el LLM", "texto que nadie dijo"}
    assert plan["callouts"][1]["text"] == "5 metros"   # no muta la entrada


def test_plan_strings():
    plan = {"title_card": {"kicker": "CAPÍTULO 2", "title": "T"}, "callouts": [{"text": "a"}],
            "evidence_zoom": {"scene_idx": 0, "box": [0, 0, .1, .1]}}
    assert plan_strings(plan) == ["CAPÍTULO 2", "T", "a", "DETALLE"]


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
