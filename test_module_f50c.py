"""F50c — cableado del expediente de foto: personas desde la ficha (A), citas con autor (B), grupos con aspecto y ropa
(C) y la chascada de `_sin_negadas` (D). Offline, sin modelos."""
import json
import sys
from pathlib import Path

import pytest

from script_engine import m03_expediente as mexp
from script_engine import m03_imagenes_v3 as v3

ROOT = Path(__file__).resolve().parent


# ─────────────────────────── A. personas desde la ficha ───────────────────────────
PADRE = {"nombre": "Daniel Écija (padre)", "rol": "Minero español.", "variantes": ["Daniel Écija"],
         "ids": ["P16", "P17", "T01"]}
HIJO = {"nombre": "Daniel Écija (hijo)", "rol": "Hijo del minero.", "variantes": ["Daniel Écija"],
        "ids": ["P17", "P30", "T01"]}
MARIA = {"nombre": "María Bernal", "rol": "Esposa de Daniel.", "variantes": [], "ids": ["P18"]}
POOL = {"personajes": [{"id": "P16", "fechas_presente": ["1962"], "lugar": "Wittenoom"},
                       {"id": "P17", "fechas_presente": ["1962", "2003"], "lugar": None},
                       {"id": "P18", "fechas_presente": ["1962"], "lugar": "Wittenoom"},
                       {"id": "P30", "fechas_presente": ["2003"], "lugar": "Madrid"}],
        "cronologia": [{"id": "T01", "fecha": "1962-05", "evento": "x"}], "datos": [], "citas": [], "lugares": []}
FICHA = [PADRE, HIJO, MARIA]


def test_f50c_a_forma_unica_y_forma_mas_larga():
    ps, dudas = mexp.personas_del_ancla("Daniel Écija conoce a María Bernal", 1962, FICHA, POOL)
    assert [p["nombre"] for p in ps] == ["Daniel Écija (padre)", "María Bernal"] and dudas == []


def test_f50c_a_calificativo_hijo():
    ps, _ = mexp.personas_del_ancla("el documento de Daniel Écija hijo", 1962, FICHA, POOL)
    assert [p["nombre"] for p in ps] == ["Daniel Écija (hijo)"]


def test_f50c_a_por_anio_y_ambigua_sin_anio_es_nadie():
    assert [p["nombre"] for p in mexp.personas_del_ancla("Daniel Écija va al médico", 2004, FICHA, POOL)[0]] == \
        ["Daniel Écija (hijo)"]
    ps, dudas = mexp.personas_del_ancla("Daniel Écija va al médico", None, FICHA, POOL)
    assert ps == [] and dudas == ["daniel écija"]


def test_f50c_a_linea_people_con_lugar_y_anios_del_primer_id():
    pers = {p["id"]: p for p in POOL["personajes"]}
    assert mexp.linea_persona(HIJO, pers) == "Hijo del minero · Madrid · 1962, 2003"


def _exps(anclas, parrafos):
    topic = {"evidence_pool": POOL}
    fu = {"esc": {"beats": [{"n": 1, "dato_central": "T01", "datos_apoyo": []}]},
          "ficha": {"escenas": [], "personas": FICHA}, "parrafos": parrafos}
    return mexp.expedientes(topic, fu, [{"n": 1, "fecha": "1962-05"}], anclas,
                            [{"beat": 1, "cerrada": False} for _ in anclas], None, "1962")


def test_f50c_a_arrastre_dentro_del_parrafo_y_no_entre_parrafos():
    pars = [{"beat": 1, "texto": "María Bernal llega. Se casan en el pueblo."},
            {"beat": 1, "texto": "Pasan los años en la casa."}]
    e = _exps(["María Bernal llega.", "Se casan en el pueblo.", "Pasan los años en la casa."], pars)
    assert e[0]["personas_fuente"] == "ancla" and e[1]["personas_fuente"] == "arrastre"
    assert e[1]["people3"] == ["Esposa de Daniel · Wittenoom · 1962" + mexp.ARRASTRE]
    assert e[2]["people3"] == [] and e[2]["personas_fuente"] is None


def test_f50c_a_ya_no_busca_en_el_pool_por_nombre():
    assert not hasattr(mexp, "_sale_entero")


def test_f50c_a_fotos_testigo_de_wittenoom():
    """Las 8 fotos testigo del handoff con los datos reales de Wittenoom (en seco: la llamada a Opus se corta). Las
    anclas son las de F50c, congeladas en `lab/hyperframes/f50f/antes/03_visual.json` (F50f: m03 re-planea las anclas
    en cada corrida, así que el 03_visual.json vivo ya no tiene las mismas frases en las mismas posiciones)."""
    anclas = ROOT / "lab" / "hyperframes" / "f50f" / "antes" / "03_visual.json"
    if not (ROOT / "data" / "scripts" / "_steps" / "123bbb64-9fca-4395-8bf4-57d60e219ef1").exists() or not anclas.exists():
        pytest.skip("sin los datos de Wittenoom")
    sys.path.insert(0, str(ROOT / "lab" / "hyperframes" / "f50c"))
    import expedientes_f50c as ex
    topic, skel, narr_ch = ex.preparar()
    v = json.loads(anclas.read_text(encoding="utf-8"))
    for (cap, foto), (nombres, fuente) in ex.TESTIGOS.items():
        c = next(x for x in v["chapters"] if x["chapter_number"] == cap)
        anchors, _ = ex._anclas(c)
        sch = next(x for x in skel["chapters"] if x["chapter_number"] == cap)
        narr = next(x for x in narr_ch if x["chapter_number"] == cap)["narration"].strip()
        _, exps = ex.pedido_y_expedientes(mexp, topic, sch, narr, anchors, cap)
        e = exps[foto - 1]
        assert (e["personas"], e["personas_fuente"]) == (nombres, fuente), (cap, foto)


# ─────────────────────────── B. citas con autor · C. grupos con aspecto y ropa ───────────────────────────
def test_f50c_b_cita_con_y_sin_fecha_y_testigo():
    q = {"texto": "Iba pegadita", "autor": "María Bernal", "rol": "Esposa de minero.", "fecha": "1962",
         "testigo": True}
    assert mexp.linea_cita(q) == "«Iba pegadita» — María Bernal · Esposa de minero · 1962 · witness"
    assert mexp.linea_cita({**q, "fecha": None, "testigo": False}) == "«Iba pegadita» — María Bernal · Esposa de minero"


def test_f50c_c_grupo_con_aspecto_y_ropa_y_quotes_en_el_bloque():
    e = {"foto": 1, "anio_ancla": "1962", "donde": [], "parrafo": "p", "escenas": [], "facts": [],
         "citas": [mexp.linea_cita({"texto": "x", "autor": "A", "rol": "r"})], "people3": []}
    b = mexp.bloque([e], [{"id": "migrant_families", "who": "w", "where_when": "ww", "appearance": "olive skin",
                           "clothing_by_period": [{"years": "1958-1966", "clothing": "cotton dresses"}]}])  # F50d B
    assert "      QUOTES: «x» — A · r" in b
    assert b.endswith("  - migrant_families: w · ww · APPEARANCE: olive skin · CLOTHING: 1958-1966: cotton dresses\n")


# ─────────────────────────── D. chascada de _sin_negadas ───────────────────────────
def test_f50c_d_cell_no_cifra_queda():
    assert v3._sin_negadas("Cell No. 5, a bare room") == "Cell No. 5, a bare room"


def test_f50c_d_no_cifra_al_inicio_queda():
    assert v3._sin_negadas("No. 4 Shaft, dusty") == "No. 4 Shaft, dusty"


def test_f50c_d_nothing_but_queda():
    assert v3._sin_negadas("a flat plain, nothing but red dust") == "a flat plain, nothing but red dust"
    assert v3._sin_negadas("a flat plain, with nothing but red dust") == "a flat plain, with nothing but red dust"


def test_f50c_d_with_no_sale():
    assert v3._sin_negadas("an empty street, with no figure anywhere") == "an empty street"


def test_f50c_d_without_queda():
    assert v3._sin_negadas("a playground, swings without seats") == "a playground, swings without seats"


def test_f50c_d_todo_negado_vacio():
    assert v3._sin_negadas("no work, no vehicles") == ""
