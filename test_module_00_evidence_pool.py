"""F5 §1.1: evidence_pool (researcher_steps/evidence_pool.py) — literalidad, fuente nunca inventada, limpieza,
merge entre bloques, ids, geocodificación anclada; y step_4a emite el pool sin tocar verified_facts."""
from __future__ import annotations

import json

from researcher_steps import evidence_pool as ep

BLOCK = """[DATOS DUROS]
- Según Human Rights Watch, 517 reclusos no estaban contabilizados en las listas oficiales.
- El Sheriff Marlin N. Gusman dijo que los presos "permanecerán donde pertenecen".
- Algunas partes de Nueva Orleans quedaron bajo 15 pies (4.6 metros) de agua.

[CRONOLOGÍA]
- 26 de agosto de 2005: Se cortan los teléfonos a los reclusos.
- 29 de agosto de 2005: El huracán Katrina toca tierra en Nueva Orleans.

[FUENTES CONSULTADAS]
- Human Rights Watch, 2005, "New Orleans: Prisoners Abandoned to Floodwaters".
- American Civil Liberties Union (ACLU), 2006, "Abandoned and Abused".
"""


def raw_ok():
    return {"datos": [{"texto": "517 reclusos no estaban contabilizados en las listas oficiales", "tipo": "cifra",
                       "valor": "517", "fuente": "Human Rights Watch, 2005"},
                      {"texto": "quedaron bajo 15 pies (4.6 metros) de agua", "tipo": "magnitud", "valor": "4.6 metros",
                       "fuente": "American Civil Liberties Union (ACLU), 2006"},             # el bloque no la ata
                      {"texto": "bajo 15 pies", "tipo": "magnitud", "valor": "15 pies"},       # fragmento de otro
                      {"texto": "Katrina mató a 1,800 personas", "tipo": "cifra", "valor": "1,800"}],   # inventado
            "cronologia": [{"fecha": "2005-08-26", "evento": "Se cortan los teléfonos a los reclusos."},
                           {"fecha": "2005-08-29", "evento": "El huracán Katrina toca tierra en Nueva Orleans."}],
            "lugares": [{"nombre": "Nueva Orleans", "rol": "ciudad"}],
            "citas": [{"texto": "permanecerán donde pertenecen", "autor": "Sheriff Marlin N. Gusman"},
                      {"texto": "New Orleans: Prisoners Abandoned to Floodwaters", "autor": "Human Rights Watch"}],
            "personajes": [{"nombre": "Marlin N. Gusman", "rol": "Sheriff", "antagonista": True},
                           {"nombre": "Human Rights Watch", "rol": "ONG"}]}


def test_literal_fuente_y_limpieza():
    log: list[str] = []
    out = ep.validate_block(raw_ok(), "misterio", BLOCK, log)
    assert [d["valor"] for d in out["datos"]] == ["517", "4.6 metros"]               # inventado y fragmento fuera
    assert out["datos"][0]["fuente"].startswith("Human Rights Watch, 2005")          # el bloque la nombra
    assert out["datos"][1]["fuente"] is None                                         # nunca inventada
    assert [q["texto"] for q in out["citas"]] == ["permanecerán donde pertenecen"]   # el título no es cita
    assert [p["nombre"] for p in out["personajes"]] == ["Marlin N. Gusman"]          # HRW no es personaje
    assert "1 ítem(s) descartado(s)" in log[0]
    assert ep.block_sources(BLOCK)[1].startswith("American Civil Liberties Union (ACLU), 2006")


def test_merge_ids_y_dedupe_entre_bloques():
    a = {"datos": [{"texto": "517 reclusos", "tipo": "cifra", "fuente": None}], "cronologia": [
        {"fecha": "2005-08-29", "evento": "El huracán Katrina toca tierra.", "fuente": None}], "lugares": [],
        "citas": [], "personajes": [{"nombre": "Marlin Gusman", "rol": "Sheriff", "antagonista": False}]}
    b = {"datos": [{"texto": "517 reclusos", "tipo": "cifra", "fuente": "HRW"}], "cronologia": [
        {"fecha": "2005-08-26", "evento": "Se cortan los teléfonos.", "fuente": None},
        {"fecha": "2005-08-29", "evento": "El huracán Katrina, categoría 3, toca tierra en Nueva Orleans.", "fuente": None}],
        "lugares": [], "citas": [], "personajes": [{"nombre": "Marlin N. Gusman", "rol": "Sheriff", "antagonista": True}]}
    pool = ep.merge([a, b])
    assert [d["id"] for d in pool["datos"]] == ["D01"] and pool["datos"][0]["fuente"] == "HRW"
    assert [(c["id"], c["fecha"]) for c in pool["cronologia"]] == [("T01", "2005-08-26"), ("T02", "2005-08-29")]
    assert "categoría 3" in pool["cronologia"][1]["evento"]                                  # el más completo
    assert len(pool["personajes"]) == 1 and pool["personajes"][0]["nombre"] == "Marlin N. Gusman"
    assert pool["personajes"][0]["antagonista"] is True and list(pool["datos"][0])[0] == "id"


def test_geocode_anclado_siglas_y_cache(tmp_path):
    calls = []
    db = {"nueva orleans": [{"lat": "29.95", "lon": "-90.07"}],
          "templeman 1, nueva orleans": [],
          "templeman 1": [{"lat": "51.52", "lon": "-0.33"}],                        # Londres: fuera del radio
          "broad street, nueva orleans": [{"lat": "29.96", "lon": "-90.09"}]}

    def fetch(q):
        calls.append(q)
        return db.get(ep.norm(q), [])
    lug = [{"nombre": "Nueva Orleans", "rol": "Ciudad"}, {"nombre": "Templeman 1", "rol": "edificio"},
           {"nombre": "Broad Street", "rol": "calle"}, {"nombre": "OPP", "rol": "prisión"}]
    anchor = ep.anchor_place(lug, ["En Nueva Orleans, Nueva Orleans"])
    ep.geocode(lug, tmp_path / "geo.json", fetch=fetch, anchor=anchor)
    assert [(p["nombre"], p["lat"]) for p in lug] == [("Nueva Orleans", 29.95), ("Templeman 1", None),
                                                        ("Broad Street", 29.96), ("OPP", None)]
    n = len(calls)
    ep.geocode([dict(p) for p in lug], tmp_path / "geo.json", fetch=fetch, anchor=anchor)
    assert len(calls) == n and json.loads((tmp_path / "geo.json").read_text(encoding="utf-8"))   # caché


def test_extract_y_step_4a(tmp_path, monkeypatch):
    calls = []

    def fake(prompt, **kw):
        calls.append(kw.get("description"))
        return raw_ok()
    pool = ep.extract_evidence_pool({"misterio": BLOCK}, call=fake, geocode_cache=tmp_path / "g.json",
                                    fetch=lambda q: [], raw_cache=tmp_path / "raw.json")
    assert calls == ["4a evidence_pool misterio"] and [d["id"] for d in pool["datos"]] == ["D01", "D02"]
    ep.extract_evidence_pool({"misterio": BLOCK}, call=fake, geocode_cache=tmp_path / "g.json",
                             fetch=lambda q: [], raw_cache=tmp_path / "raw.json")
    assert len(calls) == 1                                                                   # raw en caché
    from researcher_steps import step_4a_facts as s4
    monkeypatch.setattr(s4, "call_flash_json", lambda p: {"verified_facts": [{"fact": "x", "source_block": "humano"}],
                                                           "sources": ["s"]})
    monkeypatch.setattr(ep, "extract_evidence_pool", lambda blocks, log=None: {"datos": [1]})
    out = s4.extract_facts_and_sources({"humano": "x"})
    assert out["verified_facts"] == [{"fact": "x", "source_block": "humano"}] and out["evidence_pool"] == {"datos": [1]}
    assert "evidence_pool" not in s4.extract_facts_and_sources({"humano": "x"}, with_pool=False)
