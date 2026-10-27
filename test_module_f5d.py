"""F5d: cifras canónicas, fechas, largo del narrador Pro, datos reservados para pantalla, count_up solo cantidades
y la regla de menores en el canon de m03. Sin red."""
from __future__ import annotations

from researcher_steps import evidence_pool as ep
from script_engine import m01a_skeleton as ma
from script_engine import m05_narrative as mn
import script_engine.m01b_narrator as nb

BLOCK = ("[DATOS DUROS]\n- Cifra oficial vs. extraoficial de reclusos: Según las estadísticas del Sheriff, la Prisión de "
         "Orleans Parish (OPP) albergaba a 6,375 reclusos el 29 de agosto de 2005. Sin embargo, informes de los medios "
         "de comunicación varían, estimando que había hasta 8,000 evacuados de la prisión.\n- Aproximadamente 6,500 "
         "personas estaban encarceladas en la prisión.")
POOL = {"datos": [{"id": "D01", "texto": "la Prisión de Orleans Parish (OPP) albergaba a 6,375 reclusos el 29 de agosto de 2005",
                   "tipo": "cifra", "valor": "6,375", "fecha": "2005-08-29"},
                  {"id": "D02", "texto": "Aproximadamente 6,500 personas estaban encarceladas en la prisión", "tipo": "cifra",
                   "valor": "6,500"},
                  {"id": "D03", "texto": "estimando que había hasta 8,000 evacuados de la prisión", "tipo": "cifra",
                   "valor": "8,000"},
                  {"id": "D04", "texto": "Human Rights Watch registró a 517 prisioneros como desaparecidos", "tipo": "cifra",
                   "valor": "517", "fuente": "Human Rights Watch, 2005, \"New Orleans\""}],
        "cronologia": [{"id": "T01", "fecha": "2005-08-28", "evento": "El sheriff anuncia en una conferencia de prensa que los "
                                                                   "prisioneros no serán evacuados"},
                       {"id": "T02", "fecha": "2005-08-29", "evento": "El huracán Katrina toca tierra en Nueva Orleans"}],
        "citas": [], "lugares": [], "personajes": []}


def _pool():
    import copy
    p = copy.deepcopy(POOL)
    ep.canonical_figures(p, [BLOCK], [])
    return p


def test_cifras_canonicas_en_el_pool():
    p = _pool()
    assert p["cifras_canonicas"] == [{"oficial": "D01", "valor": "6,375", "variantes": [
        {"id": "D02", "valor": "6,500", "estatus": "aproximada"}, {"id": "D03", "valor": "8,000", "estatus": "medios"}]}]


def test_skeleton_canoniza_y_marca_el_cap_de_la_contradiccion():
    p = _pool()
    sk = {"chapters": [{"chapter_number": 1, "evidence_ids": ["D02", "T02"]}, {"chapter_number": 3, "evidence_ids": ["D02"]},
                       {"chapter_number": 7, "evidence_ids": ["D03"]}]}
    ma.canonize_figures(sk, p)
    c1, c3, c7 = sk["chapters"]
    assert c1["evidence_ids"] == ["D01", "T02"] and c3["evidence_ids"] == []          # la oficial una sola vez
    assert c7["evidence_ids"] == ["D03", "D01"] and c7["contradiccion_cifras"] == ["D01"]
    assert mn.non_canonical("Eran 6,500 presos.", p, c1) == ["6,500 (aproximada; la oficial es 6,375)"]
    assert mn.non_canonical("Eran 6,375; los medios dijeron 8,000.", p, c7) == []


def test_reservados_para_pantalla():
    p = _pool()
    sk = {"chapters": [{"chapter_number": n, "evidence_ids": ids} for n, ids in
                       ((1, ["T01"]), (2, ["T02"]), (6, []), (7, ["D01"]))]}
    ma.canonize_figures(sk, p)
    ma.assign_screen_ids(sk, p)
    got = {c["chapter_number"]: c["pantalla_ids"] for c in sk["chapters"]}
    assert "D04" in got[6] + got[7]                                   # fuente exacta, nadie la narra
    assert all(i not in ("T01", "T02", "D01", "D02", "D03") for v in got.values() for i in v)
    ch = next(c for c in sk["chapters"] if "D04" in c["pantalla_ids"])
    assert mn.screen_leaks("Human Rights Watch registró a 517 prisioneros.", p, ch)
    assert not mn.screen_leaks("Nadie supo cuántos faltaban.", p, ch)


def test_fechas_con_su_fecha_y_sin_fundir():
    t = ("El 29 de agosto el huracán Katrina tocó tierra en Nueva Orleans. Esa noche el sheriff anunció en una "
         "conferencia de prensa que los prisioneros no serían evacuados.")
    probs = mn.date_problems(t, POOL, ["T01", "T02"])
    assert any("fundiste fechas: [T01]" in x for x in probs)
    ok = ("El 28 de agosto el sheriff anunció en una conferencia de prensa que los prisioneros no serían evacuados. "
          "El 29 de agosto el huracán Katrina tocó tierra en Nueva Orleans.")
    assert mn.date_problems(ok, POOL, ["T01", "T02"]) == []
    assert any("dos fechas" in x for x in mn.date_problems("Del 28 de agosto al 29 de agosto nadie salió.", POOL, []))


def test_largo_minimo_mas_15_para_pro():
    assert nb.POOL_MIN_LEN_FACTOR == 1.15
    # F23 §1.2: la banda sale de video_length (dev_words 250 × 6 × 0.5–1.3 = 750–1950; antes, fija 800–2000)
    assert nb._len_range("development") == (750, 1950) and nb._len_range("development", 1.15) == (862, 1950)


def test_canon_m03_ningun_menor_en_celdas_de_adultos():
    from script_engine import m03_visual as m3
    pool = {"lugares": [{"nombre": "CYC", "rol": "Instalación juvenil"}], "datos": [], "cronologia": [], "personajes": []}
    blk = m3._format_documented_locations({"evidence_pool": pool})
    assert blk.splitlines()[-1] == "- Ningún menor en celdas de adultos en ninguna escena."
    assert m3._format_documented_locations({"evidence_pool": None}) == ""


def test_prompt_trae_las_reglas_nuevas():
    for k in ("L. Fechas", "M. Literal es solo", "N. Cifra canónica", "O. Los DATOS RESERVADOS PARA PANTALLA"):
        assert k in nb.F5_RULES
