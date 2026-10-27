"""
test_module_f38e_d.py — F38e §D (HANDOFF_F38e_lo_que_rompe_cualquier_video): la fecha-hora del segundo 0 se BORRÓ del
código (DECISIONES 2026-10-27 11:21; «borrar, no apagar», 16:38/18:17): sin flag, sin plantilla, sin chequeo, sin
tests. El video arranca con la primera imagen (intro INITIAL_SILENCE_SEC con el primer cuadro congelado).
    (1) ningún .py de script_engine/ ni fase2b.py menciona la palabra (en ninguna caja);
    (2) gfx_guion con un plan sintético de ch01 (aunque traiga la clave vieja `tarjeta_inicial` de un plan resuelto
        de antes) no emite el evento ni el chequeo, y la costura dice «primer cuadro congelado»;
    (3) m01e_pantalla.armar / a_markdown no traen la clave, y `editar` RECHAZA una edición que no sea ficha ni sello
        (ValueError con el motivo): no se ignora en silencio.
Sin API, sin data/: todo sintético.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from script_engine import gfx_guion as gg  # noqa: E402
from script_engine import m01e_pantalla as mp  # noqa: E402
from test_module_f32 import _cap, _plan_todo  # noqa: E402

PALABRA = "tarjeta"


# (1)
def test_d1_la_palabra_no_esta_en_el_codigo():
    archivos = [ROOT / "fase2b.py"] + [p for p in (ROOT / "script_engine").glob("*.py")]
    assert len(archivos) > 20
    con = [str(p.relative_to(ROOT)) for p in archivos if PALABRA in p.read_text(encoding="utf-8").lower()]
    assert con == []


# (2)
def test_d2_gfx_guion_sin_evento_ni_chequeo_y_la_intro_es_el_primer_cuadro():
    import fase2b
    intro = fase2b.INITIAL_SILENCE_SEC
    plan = _plan_todo()
    plan["tarjeta_inicial"] = {"texto": "9 OCT 1963 · 22:39", "fuente": "plan resuelto viejo"}   # clave vieja: se ignora
    cap = {**_cap(plan, first=True), "cap": "ch01", "n": 1}
    g = gg.armar([cap], title_dur=3.0, dip_frames=10, fps=30, intro=intro, mezcla=None, voz_video=[], topic="fix")
    tipos = {e["tipo"] for e in g["caps"][0]["eventos"]}
    assert "tarjeta fecha-hora" not in tipos and "costura" in tipos and "title card" in tipos
    assert [c["nombre"] for c in g["chequeos"] if PALABRA in c["nombre"]] == []
    costura = next(e for e in g["caps"][0]["eventos"] if e["tipo"] == "costura")
    assert costura["texto"].startswith(f"intro {intro:.1f} s (primer cuadro congelado, sin voz) → title card 3.0 s")
    assert costura["tramos"]["intro_s"] == intro and g["intro_s"] == intro
    assert PALABRA not in gg.a_markdown(g).lower()
    assert min(e["t_mp4"] for e in g["caps"][0]["eventos"]) >= cap["offset"]          # nada antes del cap


# (3)
def _ent() -> dict:
    return {"topic_id": "t", "caps": [{"cap": "ch01", "n": 1, "titulo": "T", "oraciones": []}], "beats": [],
            "archivo": [], "clima": [], "a_pantalla": {}, "_pool": {"datos": []}}


def test_d3_armar_y_markdown_sin_la_clave():
    ent = _ent()
    v = mp.validar({"beats": [], "relojes": [], "descartados": []}, ent)
    res = {"validacion": v, "modelo": mp.MODELO, "effort": mp.EFFORT, "intentos": [], "usd": 0.0}
    p = mp.armar(ent, res)
    assert not [k for k in p if PALABRA in k]
    md = mp.a_markdown(p)
    assert PALABRA not in md.lower() and "Totales: 0 fichas · 0 sellos · 0 relojes · 0 descartados" in md


def test_d3_editar_rechaza_lo_que_no_es_ficha_ni_sello(tmp_path):
    d = tmp_path / "t"
    d.mkdir()
    p = {"topic_id": "t", "prompt_version": "m01e-6", "prompt_md5": "x", "modelo": "m", "effort": "medium",
         "intentos": 1, "usd": 0.0, "tokens_in": 1, "relojes": [], "descartados": [],
         "caps": [{"cap": "ch01", "titulo": "T", "oraciones": ["La niña es de Longarone."]}],
         "beats": [{"cap": "ch01", "beat": 1, "funcion": "gancho", "pico": True, "ficha": None, "sello": None}]}
    (d / "01e_pantalla.json").write_text(json.dumps(p, ensure_ascii=False), encoding="utf-8")
    for ed in ({PALABRA: {"texto": "9 OCT 1963 · 22:39"}}, {PALABRA: None}):
        with pytest.raises(ValueError, match="sin ficha ni sello"):
            mp.editar("t", [ed], tmp_path)
    q = json.loads((d / "01e_pantalla.json").read_text(encoding="utf-8"))
    assert PALABRA not in q and q["beats"][0]["ficha"] is None                      # el papel no cambió
