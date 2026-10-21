"""F5 §1.2: m01a reparte el evidence_pool por cap — ids nuevos, puente, cronología, antagonista, cliffhanger; y sin
pool el skeleton sale igual que antes."""
from __future__ import annotations

import pytest

from script_engine import m01a_skeleton as m

POOL = {
    "datos": [{"id": f"D{i:02d}", "texto": f"dato {i} con Gusman" if i == 4 else f"dato {i}", "tipo": "cifra",
               "valor": str(i), "fecha": None} for i in range(1, 25)],
    "cronologia": [{"id": "T01", "fecha": "2005-08-26", "evento": "teléfonos"},
                   {"id": "T02", "fecha": "2005-08-29", "evento": "Katrina"},
                   {"id": "T03", "fecha": "2005-09-02", "evento": "evacuación"}],
    "citas": [], "lugares": [],
    "personajes": [{"id": "P01", "nombre": "Marlin N. Gusman", "rol": "Sheriff", "antagonista": True},
                   {"id": "P02", "nombre": "Carl Strock", "rol": "general", "antagonista": False}]}


def raw(plan, pers=None, cliffs=None):
    return {"_evidence_plan": {f"cap_{n}": ids for n, ids in plan.items()},
            "personajes": pers if pers is not None else [{"id": "P01", "entra_en_cap": 2}],
            "chapters": [{"chapter_number": n, "cliffhanger": (cliffs or {}).get(n, "")} for n in range(1, 8)]}


def good_plan():
    return {1: ["D01", "D02", "D03"], 2: ["T01", "D04", "D05", "D06"], 3: ["T02", "D07", "D08", "D09"],
            4: ["D10", "D11", "D12"], 5: ["T03", "D13", "D14", "D15"], 6: ["D16", "D17", "D18"],
            7: ["D19", "D20", "D21", "D01"]}


def test_plan_valido_y_cliffhangers():
    rp: list[str] = []
    plan, pers, cliff = m._validate_evidence_plan(raw(good_plan(), cliffs={1: "T01", 2: "T02", 3: "D10", 4: "T03",
                                                                          5: "D16", 6: "D19"}), POOL, rp)
    assert plan[7] == ["D19", "D20", "D21", "D01"] and not rp                 # un puente permitido
    assert pers[0]["nombre"] == "Marlin N. Gusman" and pers[0]["antagonista"]
    assert cliff == {1: "T01", 2: "T02", 3: "D10", 4: "T03", 5: "D16", 6: "D19"}


def test_reparaciones_deterministas():
    p = good_plan()
    p[7] = ["D19", "D20", "D21", "D01", "D02"]                                 # 2 repetidos → 1
    p[4] = ["D10", "D11", "T01"]                                               # T01 (26 ago) después de 29 ago
    p[6] = ["D16"]                                                             # 1 nuevo de 3
    p[1] = ["D01", "D02", "D03", "F05", "P01"]                                 # F## y P## se ignoran
    rp: list[str] = []
    plan, pers, cliff = m._validate_evidence_plan(raw(p, pers=[], cliffs={1: "D09"}), POOL, rp)
    assert plan[1] == ["D01", "D02", "D03"] and "D02" not in plan[7]
    assert "T01" not in plan[4] and "T01" in plan[2]                           # la cronología no retrocede
    assert len(plan[6]) == 3 and any("completado" in r for r in rp)
    assert pers == [{"id": "P01", "nombre": "Marlin N. Gusman", "rol": "Sheriff", "antagonista": True,
                     "entra_en_cap": 2}]                                        # antagonista agregado: lo nombra D04
    assert cliff[1] == next(i for i in plan[2] if i not in plan[1])            # cliffhanger reparado
    assert len(rp) >= 5


def test_errores_que_no_se_reparan():
    p = good_plan()
    p[3] = ["D99", "D07", "D08"]
    with pytest.raises(m.SkeletonValidationError, match="inexistentes"):
        m._validate_evidence_plan(raw(p), POOL)
    small = {**POOL, "datos": POOL["datos"][:2], "cronologia": []}
    assert m._min_new(small) == 1                                              # pool chico: mínimo proporcional


def test_prompt_y_schema_con_y_sin_pool():
    t = {"video_title": "x", "verified_facts": [{"fact": "f", "source_block": "humano"}]}
    plain = m._build_prompt(t)
    assert "EVIDENCE POOL" not in plain and "algún fact [F##] de la lista" in plain
    withp = m._build_prompt({**t, "evidence_pool": POOL})
    assert "EVIDENCE POOL" in withp and "[D04] DATO" in withp and "ANTAGONISTA" in withp and "_evidence_plan" in withp
    assert "_evidence_plan" not in m._skeleton_schema()["properties"]
    s = m._skeleton_schema(True)
    assert "_evidence_plan" in s["required"] and "cliffhanger" in s["properties"]["chapters"]["items"]["required"]


def test_generate_skeleton_con_pool(monkeypatch, tmp_path):
    monkeypatch.setattr(m, "STEPS_DIR", tmp_path)
    chs = [{"chapter_number": n, "title": f"Cap {n}", "narrative_intent": m.DEFAULT_INTENT_BY_CAP[n],
            "bullets": ["a", "b", "c", "d"]} for n in range(1, 8)]
    r = raw(good_plan(), cliffs={1: "T01", 2: "T02", 3: "D10", 4: "T03", 5: "D16", 6: "D19"})
    r["chapters"] = [{**c, "cliffhanger": rc["cliffhanger"]} for c, rc in zip(chs, r["chapters"])]
    r["_distribution_plan"] = {f"cap_{i}": (["F01"] if i == 2 else []) for i in m.DEVELOPMENT_CAPS}
    monkeypatch.setattr(m, "call_flash_json", lambda p, response_schema=None: r)
    sk = m.generate_skeleton({"id": "t1", "verified_facts": [{"fact": "f", "source_block": "humano"}],
                              "evidence_pool": POOL})
    assert sk["chapters"][0]["evidence_ids"] == ["D01", "D02", "D03"] and sk["chapters"][0]["cliffhanger"] == "T01"
    assert sk["chapters"][6]["cliffhanger"] is None and sk["personajes"][0]["id"] == "P01"
    import json
    full = json.loads((tmp_path / "t1" / "01a_skeleton.json").read_text(encoding="utf-8"))
    assert "_evidence_plan" in full and full["_evidence_repairs"] == []
