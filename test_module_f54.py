"""
test_module_f54.py — F54 Parte A: escaleta f26-1 → f54-1 y guion v5.4 → v5.5 (un solo cambio cada uno, literal contra
su archivo), la promesa del gancho ya no se rechaza por cifras (la imagen del gancho sí), `has_figure` con los números
compuestos, bloqueantes (f) cierre no dicho y (g) cita repetida, métricas `anios_por_cap` y `datos_por_min`. Sin red.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from script_engine import guion_v4 as g4
from script_engine import m01a_escaleta as me
from script_engine.guion_v3_reglas import anios_por_cap, datos_por_min

ROOT = Path(__file__).resolve().parent
F54 = ROOT / "lab" / "hyperframes" / "f54"


def _md5(s: str) -> str:
    return hashlib.md5(s.encode("utf-8")).hexdigest()


def _sistema(p: Path) -> str:
    md = p.read_text(encoding="utf-8").replace("\r\n", "\n")
    i = md.index("\n## SISTEMA\n\n") + len("\n## SISTEMA\n\n")
    return md[i:md.index("\n\n---\n", i)]


def _dif(a: str, b: str) -> list[tuple[str, str]]:
    x, y = a.split("\n"), b.split("\n")
    assert len(x) == len(y)
    return [(p, q) for p, q in zip(x, y) if p != q]


# ═══════════════════════════════════════════════════════════════
#  Los dos prompts (A.1, A.2)
# ═══════════════════════════════════════════════════════════════

VIEJO_P = ("No cuenta lo que va a pasar, no enumera lo que viene, no nombra juicios, comisiones ni consecuencias. "
           "Probala así: si la oración se puede leer como un resumen de lo que viene («nadie lo sabrá durante años», "
           "«terminará en un juicio»), no es una promesa; es un adelanto. Volvé a escribirla con lo que se ve o lo que "
           "no cierra.")
NUEVO_P = ("La promesa dice qué va a entender el espectador si se queda: puede nombrar lo que está en juego, con años "
           "o cifras si hacen falta; no es un índice de lo que viene.")


def test_escaleta_f54_1_literal_y_un_solo_cambio():
    assert me.SYSTEM_V2 == _sistema(F54 / "PROMPT_ESCALETA_f54_1.md") and me.PROMPT_VERSION_V2 == "f54-1"
    assert me.PROMPT_VERSION_COLUMNA == "f54-1" and me.PROMPT_VERSION_V2_F26_1 == "f26-1"
    assert _md5(me.SYSTEM_V2_F26_1) == "2e67791cedbfa7492f8b6de1268b7b30"
    (viejo, nuevo), = _dif(me.SYSTEM_V2_F26_1, me.SYSTEM_V2)
    assert VIEJO_P in viejo and viejo.replace(VIEJO_P, NUEVO_P) == nuevo
    assert "Sin contexto, sin año, sin cifras: lo que se ve." in nuevo          # R1 (la imagen del gancho) se queda


def test_guion_v5_5_literal_y_un_solo_cambio():
    assert g4.system() == g4.SYSTEM_V5_5 == _sistema(F54 / "PROMPT_GUIONISTA_v5_5.md") and g4.PROMPT_VERSION == "f54-1"
    assert g4.system("f25-1") == g4.SYSTEM_V5_4 and _md5(g4.SYSTEM_V5_4) == "2f66c1e07e4d6c31178091371821c0c9"
    (viejo, nuevo), = _dif(g4.SYSTEM_V5_4, g4.SYSTEM_V5_5)
    assert viejo.replace("Segunda: la promesa, como viene en la escaleta, sin agregarle lo que va a pasar después.",
                         "Segunda: la promesa: lo que está en juego, con tus palabras, sin índice de lo que viene.") == nuevo
    assert "Primera frase: lo que se ve, sin año, sin cifra, sin institución." in nuevo
    assert g4.VERSIONES_V5[:2] == ("f54-1", "f25-1") and g4.prompt_version(version="f25-1") == "f25-1"


# ═══════════════════════════════════════════════════════════════
#  has_figure: compuestos (A.1)
# ═══════════════════════════════════════════════════════════════

@pytest.mark.parametrize("frase", ["dieciséis personas", "diecinueve", "veintiún días", "veintiuno", "veintitrés",
                                   "veintinueve años después", "treinta y dos", "noventa y nueve",
                                   "mil novecientos sesenta y dos", "1962"])
def test_has_figure_compuestos(frase):
    assert me.has_figure(frase)


@pytest.mark.parametrize("frase", ["miles de personas", "un hombre joven", "una venda blanca", "decenas de casas"])
def test_has_figure_sin_cifra(frase):
    assert not me.has_figure(frase)


def test_num_words_compuesto_es_un_solo_token():
    # m01c_editor usa NUM_WORDS.findall: «treinta y dos» y «treinta y tres» ya no son el mismo «treinta»
    assert me.NUM_WORDS.findall("treinta y dos y treinta y tres") == ["treinta y dos", "treinta y tres"]


# ═══════════════════════════════════════════════════════════════
#  La promesa con cifras pasa; la imagen del gancho con cifras no (A.1)
# ═══════════════════════════════════════════════════════════════

def test_promesa_con_cifras_ya_no_rechaza_y_la_metrica_se_borra():
    import test_module_f6b as t6
    e = t6.good()
    e["promesa_gancho"] = "Esa herida va a cerrar; lo que respiró en mil novecientos sesenta y dos, no."
    esc, hard, rep, warn = me.validate(e, t6.POOL)
    assert not any("promesa" in h for h in hard)
    e = t6.good()
    e["beats"][0]["imagen_sensorial"] = "un hombre con el pie vendado en mil novecientos sesenta y dos, bajo el sol"
    _, hard, _, _ = me.validate(e, t6.POOL)
    assert any("imagen sensorial del gancho no lleva cifras" in h for h in hard)
    import test_module_f16 as t16
    m = me.metricas_escaleta(t16.good(), t16.POOL, t16.FICHA, [])
    assert "promesa_con_cifras" not in m and "imagen_gancho_con_cifras" in m


# ═══════════════════════════════════════════════════════════════
#  Bloqueantes (f) cierre no dicho y (g) cita repetida (A.2)
# ═══════════════════════════════════════════════════════════════

def _fixture():
    import test_module_f11 as t11
    esc = t11._esc_ok()
    esc["beats"][-1]["funcion"] = "cierre"            # beat 12, cap 7, dato central D12
    return t11, esc


def test_cierre_no_dicho_frena():
    t11, esc = _fixture()
    ps = t11._parrafos(esc)
    ps[-1]["texto"] = t11.FRASE + "Nadie volvió a abrir."           # el cap 7 no dice D12
    bl = g4.bloqueantes(t11.TOPIC, esc, ps)
    f = [x for x in bl if x["codigo"] == "f"]
    assert len(f) == 1 and f[0]["cap"] == 7 and f[0]["beat"] == 12 and "D12" in f[0]["motivo"]


def test_cierre_dicho_pasa():
    t11, esc = _fixture()
    assert g4.bloqueantes(t11.TOPIC, esc, t11._parrafos(esc)) == []


def test_cita_repetida_frena():
    t11, esc = _fixture()
    ps = t11._parrafos(esc)
    q3 = " Liz Torres lo dijo: «Soy la vida de muchas personas que cayeron sobre mi cuerpo»."
    ps[1]["texto"] += q3                                             # cap 2
    ps[9]["texto"] += q3                                             # cap 6
    g = [x for x in g4.bloqueantes(t11.TOPIC, esc, ps) if x["codigo"] == "g"]
    assert len(g) == 1 and "Q3" in g[0]["motivo"] and "[2, 6]" in g[0]["motivo"] and g[0]["cap"] == 6


def test_cita_dos_veces_en_el_mismo_cap_no_es_g():
    t11, esc = _fixture()
    ps = t11._parrafos(esc)
    q3 = " Liz Torres lo dijo: «Soy la vida de muchas personas que cayeron sobre mi cuerpo»."
    ps[1]["texto"] += q3
    ps[2]["texto"] += q3                                             # los dos en el cap 2
    assert not [x for x in g4.bloqueantes(t11.TOPIC, esc, ps) if x["codigo"] == "g"]


def test_f_y_g_no_se_editan_por_oracion():
    # reparar edita por oración solo (a)(b)(d)(e): (f) y (g) llegan tal cual a `bloqueantes_despues` (frenan)
    import inspect
    src = inspect.getsource(g4.reparar)
    assert 'x["codigo"] in ("a", "b", "d", "e")' in src


# ═══════════════════════════════════════════════════════════════
#  Métricas (A.3): solo tabla, sin freno
# ═══════════════════════════════════════════════════════════════

def test_anios_por_cap():
    caps = [{"chapter_number": 1, "narration": "Wittenoom, mil novecientos sesenta y dos. Veintinueve años después."},
            {"chapter_number": 2, "narration": "En 1948 y en mil novecientos cincuenta y siete; dos mil siete, "
                                               "dos mil veintitrés. Dos mil personas. Mil novecientos ochenta y "
                                               "seis y mil novecientos noventa y dos."},
            {"chapter_number": 3, "narration": "Más de 2.000 personas."}]
    assert anios_por_cap(caps) == {1: 1, 2: 6, 3: 0}


def test_datos_por_min():
    caps = [{"chapter_number": 1, "narration": " ".join(["palabra"] * 144), "datos_usados": ["D1", "D2", "T3"]},
            {"chapter_number": 2, "narration": "", "datos_usados": []}]
    assert datos_por_min(caps, 2.4) == {1: 3.0, 2: 0.0}             # 144 palabras a 2,4 pal/s = 1 min


def test_metricas_traen_las_dos_y_no_frenan():
    t11, esc = _fixture()
    ps = t11._parrafos(esc)
    m = g4.metricas(t11.TOPIC, esc, ps)
    assert set(m["anios_por_cap"]) == set(range(1, 8)) and set(m["datos_por_min"]) == set(range(1, 8))
    assert g4.bloqueantes(t11.TOPIC, esc, ps) == []
