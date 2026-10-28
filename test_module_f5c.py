"""F5c: skeleton congelado, narrador Pro con el mejor de 3, reglas duras/blandas, no inventar, no contaminar. Sin red."""
from __future__ import annotations

from script_engine import m05_narrative as mn

POOL = {"datos": [{"id": "D01", "texto": "En la prisión había niños de hasta 10 años", "tipo": "cifra", "valor": "10"},
                  {"id": "D02", "texto": "517 reclusos no estaban contabilizados", "tipo": "cifra", "valor": "517"},
                  {"id": "D03", "texto": "Se produjeron más de 50 fallas en los diques", "tipo": "cifra", "valor": "50"}],
        "cronologia": [{"id": "T01", "fecha": "2005-08-29", "evento": "Los generadores de la prisión fallan"}],
        "citas": [], "lugares": [], "personajes": [],
        "_descartados": [{"kind": "datos", "texto": "antigua cárcel de Nueva Orleans construida en 1902"},
                         {"kind": "datos", "texto": "Un médium psíquico ha detectado la energía de personas"},
                         {"kind": "personajes", "texto": "Raphael Schwarz"}]}
SKEL = {"chapters": [{"chapter_number": 2, "evidence_ids": ["D01", "D02", "D03"], "cliffhanger": "T01"}],
        "personajes": []}
BASE = "Los guardias contaron a los presos en el patio de la cárcel una vez más. "
GOOD = (BASE * 5 + "El patio estaba húmedo, sucio y oscuro, el aire pesado. " + BASE * 5
        + "En la prisión había niños de hasta 10 años. Después, 517 reclusos no estaban contabilizados. Se produjeron "
          "más de 50 fallas en los diques. Esa noche los generadores de la prisión iban a fallar.")


def test_no_inventar_y_no_contaminar():
    facts = [{"fact": "Aproximadamente 6,500 personas estaban encarceladas."}]
    assert mn.invented_numbers("Había 6,500 presos y 517 sin contar; el 29 de agosto, 7,000 más.", POOL, facts) == ["7,000"]
    assert mn.contamination("La antigua cárcel, construida en 1902, ahora es posada.", POOL) != []
    assert mn.contamination("Un médium psíquico dijo haber sentido algo.", POOL) != []
    assert mn.contamination("Casos como el de Raphael Schwarz.", POOL) == ["Raphael Schwarz"]
    assert mn.contamination(GOOD, POOL) == []


def test_reglas_duras_y_blandas_y_puntaje():
    r = mn.cap_review(GOOD, cap=2, pool=POOL, skeleton=SKEL, previous=[], declared=["D01", "D02", "D03"], facts=[])
    assert r["hard"] == [] and r["parts"]["datos"] == 3 and r["parts"]["cliffhanger"] is True
    assert r["score"] == 3 * 3 + 2 - (1 if r["parts"]["adj_fuera"] else 0)
    # F21: «manto de» y «el monstruo» salieron de la lista (de caso); quedan los clichés genéricos
    bad = GOOD.replace("Esa noche", "Bajo un velo de misterio, una trampa brutal despertó. Esa noche")
    rb = mn.cap_review(bad, cap=2, pool=POOL, skeleton=SKEL, previous=[], declared=["D01", "D02", "D03"], facts=[])
    assert any("relleno prohibido: velo de misterio, trampa brutal" in h for h in rb["hard"]) and rb["score"] <= r["score"] - 4
    adj = GOOD.replace("húmedo, sucio y oscuro, el aire pesado", "húmedo, sucio, oscuro, frío, denso, pesado, terrible, sombrío, gélido, macabro y siniestro")
    ra = mn.cap_review(adj * 1, cap=2, pool=POOL, skeleton=SKEL, previous=[], declared=["D01", "D02", "D03"], facts=[])
    assert not ra["hard"] and any("adjetivos/100" in x for x in ra["soft"])             # adjetivos: blanda
    rep = mn.cap_review(GOOD, cap=2, pool=POOL, skeleton=SKEL, previous=[GOOD], declared=["D01", "D02", "D03"], facts=[])
    assert any("ya se dijeron en caps anteriores" in x for x in rep["soft"])           # 3-gramas: blanda


def test_prompt_prioridad_y_relleno_nuevo():
    # F41: el prompt del narrador viejo (F5_RULES, POOL_NARRATOR, POOL_BEST_OF) se borró; queda la lista de relleno de m05
    for f in ("velo de misterio", "alfombra de la negación", "sentencia de abandono", "trampa brutal"):
        assert f in mn.FORBIDDEN_FILLER
    for f in ("manto de", "el monstruo", "infierno flotante", "ecos de"):    # F21: borrados de la lista (de caso)
        assert f not in mn.FORBIDDEN_FILLER
