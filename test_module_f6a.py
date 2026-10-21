"""F6a: [TESTIMONIOS] en el research y testigo/presente_en en el pool; add_block suma un bloque sin tocar ids. Sin red."""
from __future__ import annotations

import topic_researcher as tr
from researcher_steps import evidence_pool as ep

BLOCK = """=== HALLAZGOS DEL ÁNGULO TESTIMONIOS ===
[TESTIMONIOS]
- "El agua nos llegaba al pecho y nadie abría las celdas" — Dan Bright, preso de Templeman III, 2005-08-30 — Human Rights Watch, 2005
- "Los guardias se fueron y nos dejaron" — un preso de Templeman III — ACLU, 2006
Dan Bright estuvo en Templeman III el 2005-08-29 y el 2005-08-30; Dan Bright declaró ante Human Rights Watch.
[CRONOLOGÍA]
- 2005-08-30: Dan Bright pasa la noche en el segundo piso inundado.
[FUENTES CONSULTADAS]
- Human Rights Watch, 2005, "Abandoned and Abused"
- ACLU, 2006, informe
"""
RAW = {"datos": [], "lugares": [],
       "cronologia": [{"fecha": "2005-08-30", "evento": "Dan Bright pasa la noche en el segundo piso inundado."}],
       "citas": [{"texto": "El agua nos llegaba al pecho y nadie abría las celdas", "autor": "Dan Bright",
                  "rol": "preso de Templeman III", "testimonio": True, "fuente": "Human Rights Watch, 2005"},
                 {"texto": "Los guardias se fueron y nos dejaron", "autor": "un preso de Templeman III",
                  "rol": "preso", "testimonio": True}],
       "personajes": [{"nombre": "Dan Bright", "rol": "preso de Templeman III", "testigo": True,
                       "fechas_presente": ["2005-08-29", "2005-08-30", "agosto"]},
                      {"nombre": "Marlin N. Gusman", "rol": "sheriff", "antagonista": True}]}


def test_prompt_pide_testimonios_en_humano_y_misterio():
    by = {a["key"]: a for a in tr.DEEP_RESEARCH_ANGLES}
    seed = {"seed_title": "X"}
    assert "[TESTIMONIOS]" in tr._build_angle_query_prompt(seed, by["humano"])
    assert "[TESTIMONIOS]" in tr._build_angle_query_prompt(seed, by["misterio"])
    tec = tr._build_angle_query_prompt(seed, by["tecnico"])
    assert "[TESTIMONIOS]" not in tec and "[DATOS DE MAGNITUD]" in tec
    q = tr._build_testimonios_prompt(seed, tr.TESTIMONIOS_ANGLE)
    assert "[TESTIMONIOS]" in q and "Nunca inventes" in q
    assert "testimonio=true" in ep.build_prompt("humano", "x") and "fechas_presente" in ep.build_prompt("humano", "x")


def test_bloque_con_testigo_y_presencia():
    out = ep.validate_block(RAW, "testimonios", BLOCK + "El sheriff Marlin N. Gusman ordenó que nadie saliera.", [])
    q = out["citas"][0]
    assert q["testimonio"] is True and q["rol"] == "preso de Templeman III" and q["fuente"]
    p = next(x for x in out["personajes"] if x["nombre"] == "Dan Bright")
    assert p["testigo"] and p["fechas_presente"] == ["2005-08-29", "2005-08-30"]        # «agosto» no es fecha
    pool = ep.merge([out])
    pool["cronologia"].append({"id": "T09", "fecha": "2005-08-29", "evento": "Se corta la luz.", "bloque": "x"})
    ep.presence(pool)
    dan = next(x for x in pool["personajes"] if x["nombre"] == "Dan Bright")
    assert dan["testigo"] and set(dan["presente_en"]) == {"T01", "T09"}
    gus = next(x for x in pool["personajes"] if x["nombre"] == "Marlin N. Gusman")
    assert not gus["testigo"] and gus["presente_en"] == []


def test_add_block_no_cambia_ids_viejos():
    old = {"datos": [{"id": "D01", "texto": "Había 6,375 presos", "tipo": "cifra", "valor": "6,375", "bloque": "tecnico"}],
           "cronologia": [{"id": "T01", "fecha": "2005-08-29", "evento": "Katrina toca tierra en Nueva Orleans.",
                           "bloque": "tecnico"}],
           "lugares": [], "citas": [{"id": "Q01", "texto": "donde pertenecen", "autor": "Sheriff Gusman", "bloque": "humano"}],
           "personajes": [{"id": "P01", "nombre": "Marlin N. Gusman", "rol": "sheriff", "antagonista": True,
                           "bloque": "tecnico"}]}
    blk = BLOCK + "\nEl sheriff Marlin N. Gusman ordenó que nadie saliera.\n"
    pool = ep.add_block(old, "testimonios", blk, call=lambda *a, **k: RAW, log=[])
    assert [x["id"] for x in pool["datos"]] == ["D01"]
    assert {x["id"] for x in pool["citas"]} == {"Q01", "Q02", "Q03"}
    assert {x["id"]: x["nombre"] for x in pool["personajes"]} == {"P01": "Marlin N. Gusman", "P02": "Dan Bright"}
    t = {x["id"]: x["fecha"] for x in pool["cronologia"]}
    assert t["T01"] == "2005-08-29" and t["T02"] == "2005-08-30"
    assert next(x for x in pool["personajes"] if x["id"] == "P02")["presente_en"] == ["T01", "T02"]
