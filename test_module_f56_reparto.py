"""
test_module_f56_reparto.py — F56 Parte B: `m01d_particion.rebalance` no mueve ni recorta mal el párrafo del re-gancho
(`recuerda_loop`), igual que protege el pico; sin `recuerda_loop` se comporta como siempre. `medida_retencion.re_gancho`
busca la oración en todos los caps y dice en cuál cayó. Sin red.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

from script_engine import m01d_particion as md

ROOT = Path(__file__).resolve().parent
ANTES = ROOT / "lab" / "hyperframes" / "f56" / "antes"
hay = pytest.mark.skipif(not (ANTES / "01b_guionista_v4.json").exists(), reason="sin el guion F55 de Wittenoom (f56/antes)")


def _esc_sint(recuerda: dict | None = None) -> dict:
    """Escaleta mínima: beats 1..8, pico en el 5; cap 3 con los beats 3 y 4."""
    beats = [{"n": n, "cap": c} for n, c in ((1, 1), (2, 2), (3, 3), (4, 3), (5, 4), (6, 5), (7, 6), (8, 7))]
    esc = {"beats": beats, "pico": {"beat": 5}}
    if recuerda is not None:
        esc["recuerda_loop"] = recuerda
    return esc


def _parrafos(hi3: int) -> list[dict]:
    """Un párrafo por beat; el cap 3 tiene dos y se pasa del tope (`hi3` = tope del cap 3) por el segundo."""
    txt = {1: "a" * 300, 2: "b" * 1200, 3: "c" * (hi3 - 100), 4: "La oración del regancho sigue aquí. " + "d" * 400,
           5: "e" * 1200, 6: "f" * 1200, 7: "g" * 1200, 8: "h" * 300}
    caps = {1: 1, 2: 2, 3: 3, 4: 3, 5: 4, 6: 5, 7: 6, 8: 7}
    return [{"beat": n, "cap": caps[n], "texto": txt[n]} for n in range(1, 9)]


def _hi(n: int) -> int:
    roles = {c["chapter_number"]: c["role"] for c in md.CHAPTER_SCHEMA}
    return md.len_range(roles[n])[1]


RL = {"beat": 4, "oracion": "La oración del regancho sigue aquí."}


def test_sin_recuerda_loop_el_ultimo_parrafo_se_mueve_como_siempre():
    ps, notes = md.rebalance(_esc_sint(None), _parrafos(_hi(3)), shorten=None)
    assert next(p for p in ps if p["beat"] == 4)["cap"] == 4
    assert any("pasa al cap 4" in x for x in notes)


def test_el_parrafo_del_regancho_no_se_mueve():
    ps, notes = md.rebalance(_esc_sint(RL), _parrafos(_hi(3)), shorten=None)
    assert next(p for p in ps if p["beat"] == 4)["cap"] == 3
    assert any(x.startswith("cap 3:") and "no se pudo mover ni acortar" in x for x in notes)


def test_otro_parrafo_ultimo_si_se_mueve_aunque_haya_regancho():
    esc = _esc_sint({"beat": 3, "oracion": "x"})          # el re-gancho es el beat 3, que no es el último del cap 3
    ps, notes = md.rebalance(esc, _parrafos(_hi(3)), shorten=None)
    assert next(p for p in ps if p["beat"] == 4)["cap"] == 4


def test_acortar_el_parrafo_del_regancho_conserva_la_oracion_o_no_se_acorta():
    ps0 = _parrafos(_hi(3))
    sin = lambda texto, target: "d" * 200                                        # pierde la oración
    ps, notes = md.rebalance(_esc_sint(RL), ps0, shorten=sin)
    p4 = next(p for p in ps if p["beat"] == 4)
    assert p4["cap"] == 3 and p4["texto"] == ps0[3]["texto"]
    assert any("perdía la oración del re-gancho" in x for x in notes) and any("no se pudo mover ni acortar" in x for x in notes)
    con = lambda texto, target: "La oración del regancho sigue aquí. " + "d" * 50   # la conserva
    ps, notes = md.rebalance(_esc_sint(RL), ps0, shorten=con)
    p4 = next(p for p in ps if p["beat"] == 4)
    assert p4["cap"] == 3 and p4["texto"].startswith("La oración del regancho sigue aquí.") and len(p4["texto"]) < len(ps0[3]["texto"])
    assert any("el editor acortó" in x for x in notes)


def test_pico_sigue_protegido():
    esc = _esc_sint(None)
    esc["pico"] = {"beat": 4}
    ps, notes = md.rebalance(esc, _parrafos(_hi(3)), shorten=None)
    assert next(p for p in ps if p["beat"] == 4)["cap"] == 3


@hay
def test_wittenoom_f55_el_parrafo_del_beat_6_queda_en_el_cap_3():
    esc = json.loads((ANTES / "01a_escaleta.json").read_text(encoding="utf-8"))
    ps0 = json.loads((ANTES / "01b_guionista_v4.json").read_text(encoding="utf-8"))["reparacion"]["parrafos"]
    assert esc["recuerda_loop"]["beat"] == 6
    ps, notes = md.rebalance(esc, ps0, shorten=None)
    assert all(p["cap"] == 3 for p in ps if p["beat"] == 6)
    assert any(x.startswith("cap 3:") and ("no se pudo mover ni acortar" in x or "acortó" in x) for x in notes)
    assert not any("pasa al cap 4" in x for x in notes)


def _medida():
    p = ROOT / "lab" / "hyperframes" / "f54" / "medida_retencion.py"
    spec = importlib.util.spec_from_file_location("medida_retencion_f54", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_re_gancho_se_busca_en_todos_los_caps():
    mr = _medida()
    esc = {"beats": [{"n": 1, "cap": 1}, {"n": 2, "cap": 3}, {"n": 3, "cap": 4}],
           "recuerda_loop": {"beat": 2, "oracion": "Un año después, un recién casado bajaba del avión en esa pista de polvo."}}
    caps = [{"chapter_number": 1, "narration": "Un hombre posa para una foto."},
            {"chapter_number": 3, "narration": "El polvo cubría el molino. Nadie decía nada."},
            {"chapter_number": 4, "narration": "Un año después, un recién casado bajaba del avión en esa pista de polvo. Llegó con su mujer."}]
    r = mr.re_gancho(esc, caps)
    assert r["declarado"] and r["dicho"] and r["cap_declarado"] == 3 and r["cap_dicho"] == 4 and r["parecido"] == 1.0
    assert mr.re_gancho({"beats": esc["beats"]}, caps) == {"declarado": False, "dicho": False, "minuto": None}
