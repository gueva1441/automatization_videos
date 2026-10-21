"""F5c: skeleton congelado, narrador Pro con el mejor de 3, reglas duras/blandas, no inventar, no contaminar. Sin red."""
from __future__ import annotations

import json

import script_engine.m01b_narrator as nb
from script_engine import m01a_skeleton as ma
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
GOOD = (BASE * 4 + "El patio estaba húmedo, sucio y oscuro, el aire pesado. " + BASE * 4
        + "En la prisión había niños de hasta 10 años. Después, 517 reclusos no estaban contabilizados. Se produjeron "
          "más de 50 fallas en los diques. Esa noche los generadores de la prisión iban a fallar.")


def test_skeleton_congelado_traduce_ids_y_saca_lo_que_no_esta(tmp_path, monkeypatch):
    old = {"evidence_pool": {"datos": [{"id": "D07", "texto": "517 reclusos no estaban contabilizados", "tipo": "cifra"},
                                       {"id": "D71", "texto": "Un médium psíquico ha detectado la energía", "tipo": "nombre"}],
                             "cronologia": [{"id": "T09", "fecha": "2005-08-29", "evento": "Los generadores de la prisión fallan"}]}}
    sk = {"chapters": [{"chapter_number": 1, "evidence_ids": ["D07", "D71"], "cliffhanger": "T09"}],
          "personajes": [{"nombre": "Marlin N. Gusman", "entra_en_cap": 1}, {"nombre": "Cornel Hubert", "entra_en_cap": 5}]}
    (tmp_path / "sk.json").write_text(json.dumps(sk), encoding="utf-8")
    (tmp_path / "pool.json").write_text(json.dumps(old), encoding="utf-8")
    monkeypatch.setattr(ma, "STEPS_DIR", tmp_path)
    monkeypatch.setattr(ma, "_call_with_validation_retry", lambda *a, **k: (_ for _ in ()).throw(AssertionError("Flash")))
    cur = {**POOL, "personajes": [{"id": "P01", "nombre": "Marlin N. Gusman", "rol": "sheriff"}]}
    out = ma.generate_skeleton({"id": "t", "evidence_pool": cur,
                                "skeleton_frozen": {"skeleton": str(tmp_path / "sk.json"), "pool": str(tmp_path / "pool.json")}})
    ch = out["chapters"][0]
    assert ch["evidence_ids"] == ["D02"] and ch["cliffhanger"] == "T01"            # D07→D02, el médium fuera
    assert [p["nombre"] for p in out["personajes"]] == ["Marlin N. Gusman"]          # Hubert no entra
    saved = json.loads((tmp_path / "t" / "01a_skeleton.json").read_text(encoding="utf-8"))
    assert any("Cornel Hubert" in n for n in saved["_frozen"]["notas"])


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
    bad = GOOD.replace("Esa noche", "Bajo un manto de sombras, el monstruo despertó. Esa noche")
    rb = mn.cap_review(bad, cap=2, pool=POOL, skeleton=SKEL, previous=[], declared=["D01", "D02", "D03"], facts=[])
    assert any("relleno prohibido: manto de, el monstruo" in h for h in rb["hard"]) and rb["score"] == r["score"] - 4
    adj = GOOD.replace("húmedo, sucio y oscuro, el aire pesado", "húmedo, sucio, oscuro, frío, denso, pesado y terrible")
    ra = mn.cap_review(adj * 1, cap=2, pool=POOL, skeleton=SKEL, previous=[], declared=["D01", "D02", "D03"], facts=[])
    assert not ra["hard"] and any("adjetivos/100" in x for x in ra["soft"])             # adjetivos: blanda
    rep = mn.cap_review(GOOD, cap=2, pool=POOL, skeleton=SKEL, previous=[GOOD], declared=["D01", "D02", "D03"], facts=[])
    assert any("ya se dijeron en caps anteriores" in x for x in rep["soft"])           # 3-gramas: blanda


def test_mejor_de_3_se_queda_con_el_mejor_no_con_el_ultimo(monkeypatch):
    weak = GOOD.replace("Después, 517 reclusos no estaban contabilizados. ", "Después, nadie sabía nada. ")
    worse = weak.replace("Se produjeron más de 50 fallas en los diques. ", "Todo era incierto. ")
    q = [{"narration": weak, "datos_usados": ["D01", "D03"]}, {"narration": GOOD, "datos_usados": ["D01", "D02", "D03"]},
         {"narration": worse, "datos_usados": ["D01"]}]
    calls = []
    monkeypatch.setattr(nb, "call_pro_json", lambda p, response_schema=None, description=None: (calls.append(p), q.pop(0))[1])
    monkeypatch.setattr(nb, "call_flash_json", lambda *a, **k: (_ for _ in ()).throw(AssertionError("Flash")))
    viol, dec, aud = {}, {}, {}
    out = nb._best_of_n("P", "development", 2, {"pool": POOL, "skeleton": SKEL, "previous": [], "facts": []},
                        violations=viol, declared=dec, audit=aud)
    assert out == GOOD and dec[2] == ["D01", "D02", "D03"] and aud[2]["elegido"] == 2
    assert len(calls) == 2 or len(calls) == 3                                            # el 2.º sale limpio: puede cortar
    assert "REGLAS DURAS" in calls[1]


def test_mejor_de_3_no_toma_el_ultimo_si_es_peor(monkeypatch):
    weak = GOOD.replace("Después, 517 reclusos no estaban contabilizados. ", "Después, nadie sabía nada. ")
    worse = weak.replace("Se produjeron más de 50 fallas en los diques. ", "Todo era incierto. ")
    q = [{"narration": weak, "datos_usados": ["D01", "D03"]}, {"narration": worse, "datos_usados": ["D01"]},
         {"narration": worse, "datos_usados": ["D01"]}]
    monkeypatch.setattr(nb, "call_pro_json", lambda p, response_schema=None, description=None: q.pop(0))
    aud: dict = {}
    out = nb._best_of_n("P", "development", 2, {"pool": POOL, "skeleton": SKEL, "previous": [], "facts": []},
                        violations={}, declared={}, audit=aud)
    assert out == weak and aud[2]["elegido"] == 1 and not q


def test_prompt_prioridad_y_relleno_nuevo():
    assert "Si no podés cumplir todo, sacrificá la ventana de adjetivos, nunca los datos ni los nombres." in nb.F5_RULES
    for f in ("manto de", "el monstruo", "infierno flotante", "velo de misterio", "ecos de", "alfombra de la negación",
              "sentencia de abandono", "trampa brutal"):
        assert f in mn.FORBIDDEN_FILLER and f in nb.F5_RULES
    assert (nb.POOL_NARRATOR, nb.POOL_BEST_OF) == ("pro", 3)
