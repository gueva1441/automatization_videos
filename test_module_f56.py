"""
test_module_f56.py — F56 Parte A: los 3 frenos falsos del guion F55 de Wittenoom ya no frenan (m05_narrative.contamination
salta los kinds `personajes*` y las citas duplicadas; false_quotes acepta las palabras de una duplicada como la cita que
quedó; ficha_caso.load pasa el texto de la cita duplicada al de la que quedó), y lo que debe seguir frenando sigue (un
`datos_r3` descartado; una cita inventada). Sin red. Los casos reales leen lab/hyperframes/f56/antes/.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from researcher_steps import ficha_caso as fc
from script_engine import evidence as ev
from script_engine import m05_narrative as m5

ROOT = Path(__file__).resolve().parent
ANTES = ROOT / "lab" / "hyperframes" / "f56" / "antes"
hay = pytest.mark.skipif(not (ANTES / "00_pool_v3.json").exists(), reason="sin lab/hyperframes/f56/antes/")


def _pool() -> dict:
    return json.loads((ANTES / "00_pool_v3.json").read_text(encoding="utf-8"))


def _parrafos() -> list[dict]:
    return json.loads((ANTES / "01b_guionista_v4.json").read_text(encoding="utf-8"))["reparacion"]["parrafos"]


# ═══════════════════════════════════════════════════════════════
#  Los 3 casos reales de Wittenoom
# ═══════════════════════════════════════════════════════════════

@hay
def test_q15_duplicada_ya_no_es_contaminacion_ni_cita_falsa():
    pool, ps = _pool(), _parrafos()
    q15 = next(d for d in pool["_descartados"] if d.get("kind") == "citas" and d["id"] == "Q15")
    assert q15["duplicado_de"] == "Q27"
    cap3 = [p["texto"] for p in ps if p["cap"] == 3]
    con_q15 = [t for t in cap3 if "Aterrizamos en una pista" in t]
    assert con_q15, "el párrafo del cap 3 que cita a Q15"
    for t in con_q15:
        assert not [x for x in m5.contamination(t, pool) if "avión era pequeño" in x]
        assert not [x for x in m5.false_quotes(t, pool) if "Aterrizamos" in x]


@hay
def test_defensor_del_empleador_personajes_r3_ya_no_es_contaminacion():
    pool, ps = _pool(), _parrafos()
    d = next(x for x in pool["_descartados"] if "Defensor del empleador" in str(x.get("texto")))
    assert d["kind"] == "personajes_r3"
    con = [p["texto"] for p in ps if p["cap"] == 3 and "defensor del empleador" in p["texto"].lower()]
    assert con
    for t in con:
        assert not [x for x in m5.contamination(t, pool) if "Defensor del empleador" in x]


@hay
def test_los_3_bloqueantes_de_f55_desaparecen_con_los_jueces_nuevos():
    import fase1_5
    from script_engine import guion_v4 as g4
    tid = "123bbb64-9fca-4395-8bf4-57d60e219ef1"
    try:
        topic = dict(fase1_5._load_topic_by_id(tid))
    except (FileNotFoundError, KeyError):
        pytest.skip("sin topics_db")
    fase1_5.cargar_perfil(tid)
    esc = json.loads((ANTES / "01a_escaleta.json").read_text(encoding="utf-8"))
    ficha = fc.load(tid)
    ps = _parrafos()
    bl = g4.bloqueantes(topic, esc, ps, "abierto", ficha, verificar=lambda h, o, **k: None)
    assert [x for x in bl if x["codigo"] in ("a", "d")] == [], bl


# ═══════════════════════════════════════════════════════════════
#  Lo que sigue frenando
# ═══════════════════════════════════════════════════════════════

@hay
def test_un_datos_r3_descartado_sigue_frenando():
    pool = _pool()
    # los datos_r3 cuyas palabras propias (≥ 2, de 6+ letras, fuera del pool que quedó) siguen disparando (d): al menos uno,
    # y para cada uno de esos el juez nuevo devuelve lo mismo que el viejo (el salto es solo personajes* y duplicadas)
    frenan = [d for d in pool["_descartados"] if d.get("kind") == "datos_r3" and m5.contamination(str(d["texto"]), pool)]
    assert frenan, "ningún datos_r3 descartado dispara (d) con su propio texto"


def test_sintetico_contaminacion_y_citas():
    pool = {"citas": [{"id": "Q2", "texto": "Nadie nos dijo nada del polvo que respirábamos todos los días", "autor": "A"}],
            "datos": [], "cronologia": [], "lugares": [], "personajes": [],
            "_descartados": [
                {"kind": "citas", "id": "Q1", "duplicado_de": "Q2", "texto": "Nadie nos avisó nada del polvo que respirábamos cada día"},
                {"kind": "personajes_r3", "texto": "Portavoz ministerial no identificado", "motivo": "no es una persona con nombre propio"},
                {"kind": "datos_r3", "texto": "Un médium psíquico predijo la catástrofe en Rosario", "motivo": "cita_literal no está en el documento"},
            ]}
    # la duplicada: ni (d) ni (a)
    assert m5.contamination("«Nadie nos avisó nada del polvo que respirábamos cada día», dijo A.", pool) == []
    assert m5.false_quotes("Lo dijo A: «Nadie nos avisó nada del polvo que respirábamos cada día».", pool) == []
    # personajes_r3: no es contaminación
    assert m5.contamination("El portavoz ministerial no identificado respondió que no.", pool) == []
    # datos_r3: sigue frenando (≥ 2 palabras propias)
    assert m5.contamination("Un médium psíquico lo había predicho.", pool)
    # cita inventada: sigue frenando (a)
    assert m5.false_quotes("Él lo dijo claro: «el polvo no era nada, puro cuento de los médicos».", pool)


# ═══════════════════════════════════════════════════════════════
#  ficha_caso.load: el texto de la cita que quedó
# ═══════════════════════════════════════════════════════════════

def test_ficha_load_texto_de_la_cita_que_quedo(tmp_path):
    d = tmp_path / "t1"
    d.mkdir()
    ficha = {"citas": [{"ids": ["Q1"], "texto": "Nadie nos avisó nada", "autor": "A"},
                       {"ids": ["Q3"], "texto": "Otra cita viva", "autor": "B"}],
             "hechos": [{"ids": ["Q1"], "texto": "A recuerda que nadie avisó."}]}
    (d / "ficha_caso.json").write_text(json.dumps(ficha), encoding="utf-8")
    (d / "00_pool_v3.json").write_text(json.dumps({
        "citas": [{"id": "Q2", "texto": "Nadie nos dijo nada", "autor": "A"}, {"id": "Q3", "texto": "Otra cita viva", "autor": "B"}],
        "_descartados": [{"kind": "citas", "id": "Q1", "duplicado_de": "Q2", "texto": "Nadie nos avisó nada"}]}), encoding="utf-8")
    log: list[str] = []
    out = fc.load("t1", tmp_path, log=log)
    assert out["citas"][0] == {"ids": ["Q2"], "texto": "Nadie nos dijo nada", "autor": "A"}      # texto de la que quedó
    assert out["citas"][1]["texto"] == "Otra cita viva"                                           # las demás, intactas
    assert out["hechos"][0] == {"ids": ["Q2"], "texto": "A recuerda que nadie avisó."}            # un hecho no es la cita
    assert log and "1 texto(s) de cita" in log[0]
    assert json.loads((d / "ficha_caso.json").read_text(encoding="utf-8")) == ficha               # el archivo no cambia


@hay
def test_ficha_de_wittenoom_cargada_cita_a_q27_con_su_texto():
    from script_engine.m01a_skeleton import STEPS_DIR
    tid = "123bbb64-9fca-4395-8bf4-57d60e219ef1"
    if not (STEPS_DIR / tid / "ficha_caso.json").exists():
        pytest.skip("sin la ficha de Wittenoom en _steps/")
    pool = json.loads((STEPS_DIR / tid / "00_pool_v3.json").read_text(encoding="utf-8"))
    q27 = next(q for q in pool["citas"] if q["id"] == "Q27")
    out = fc.load(tid)
    c = next(c for c in out["citas"] if "Q27" in c.get("ids", []) and "avión" in c.get("texto", ""))
    assert c["texto"] == q27["texto"]
    assert ev.norm("Aterrizamos en una pista en medio de una tierra muy, muy roja") in ev.norm(c["texto"])
