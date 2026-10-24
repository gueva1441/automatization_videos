"""
test_module_f21.py — F21 (familias A + B + F de la auditoría). `script_engine/nombres.py` como única fuente sobre nombres
(cualquier alfabeto, iniciales, partículas, mononimios, MAYÚSCULAS de PDF); `norm` igual al de antes en texto latino y sin
romper el cirílico; `slugify` con el id; fuera el molde de Orleans (`role_class` con las palabras del perfil, sin perfil
nada; `fix_glued_caps` con los roles del pool; `photo_problems` solo la foto; población sin sujeto de Orleans); los jueces
leen la traducción (`pool_con_traducciones`); los cuatro prompts sin cambio (md5). Sin red.
"""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from pathlib import Path

import pytest

from researcher_steps import research_v3 as r3
from script_engine import evidence as ev
from script_engine import nombres as nm

ROOT = Path(__file__).resolve().parent
ORLEANS_POOL = ROOT / "data" / "scripts" / "_steps" / "ba6c3cac-f7r3" / "00_pool_v3.json"
PERFIL_ORLEANS = {"roles_testigo": ["preso", "presos", "recluso", "reclusos", "abogado"],
                  "roles_antagonista": ["sheriff", "deputy", "alcaide"]}
PERFIL_KYSHTYM = {"roles_testigo": ["sobreviviente", "evacuado", "trabajador", "liquidador"],
                  "roles_antagonista": ["ministerio", "dirección de la planta"]}


@pytest.fixture(autouse=True)
def _sin_vocabulario():
    r3.set_vocabulario(None)
    yield
    r3.set_vocabulario(None)


# ═══════════════════════════════════════════════════════════════
#  nombres.py (A)
# ═══════════════════════════════════════════════════════════════

@pytest.mark.parametrize("nombre, es", [
    ("V.M. Osetrov", True), ("Juan de la Cruz", True), ("Jürgen Müller", True), ("Любовь Ладейщикова", True),
    ("MARLIN GUSMAN", True), ("Renard Reed", True), ("Deputy Foster", True), ("Rasputin", False),
    ("National Guard Officers", False), ("Criminal Justice Working Group", False), ("según la ACLU", False),
    ("el Ministerio de Construcción", False), ("un preso de Templeman III", False),
])
def test_es_persona(nombre, es):
    assert nm.es_persona(nombre) is es


def test_claves_y_mismas():
    assert nm.es_persona("Rasputin", mononimo_ok=True)
    assert nm.clave("Deputy Foster") == ("", "foster")
    assert nm.clave("Juan de la Cruz") == ("juan", "cruz")
    assert nm.clave("Sgt. Bell") == ("", "bell")
    assert nm.clave("Gonçalves") == ("", "goncalves")
    assert nm.clave("Любовь Ладейщикова") == ("любовь", "ладейщикова")
    assert nm.misma("Marlin Gusman", "Martin Gusman") and nm.misma("Deputy Renard Reed", "Renard Reed")
    assert not nm.misma("Christina Foster", "Mike Foster")
    assert nm.menciona("dijo Ладейщикова, la vecina", "ладейщикова")
    assert not nm.menciona("lista", "li") and nm.menciona("Li dijo", "li")
    assert nm.terminos({"nombre": "Renard Reed"}, [{"nombre": "Renard Reed"}]) == ["renard reed", "reed"]


def _norm_viejo(s: str) -> str:
    """El `evidence_pool.norm` de 08d63d9, copiado para comparar."""
    q = str.maketrans({"“": '"', "”": '"', "«": '"', "»": '"', "‘": "'", "’": "'", "´": "'"})
    s = str(s or "").translate(q).lower()
    s = "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", s).strip().strip(" .,;:")


def test_norm_igual_en_latino_y_sin_romper_el_cirilico():
    if not ORLEANS_POOL.exists():
        pytest.skip("sin el pool de Orleans")
    pool = json.loads(ORLEANS_POOL.read_text(encoding="utf-8"))
    xs = [str(it[f]) for k in ("datos", "cronologia", "citas", "personajes") for it in pool[k]
          for f in ("texto", "evento", "nombre", "texto_original", "autor", "rol") if it.get(f)][:500]
    assert len(xs) == 500 and all(nm.norm(x) == _norm_viejo(x) for x in xs)
    assert nm.norm("Озёрск") == "озёрск" and nm.norm("Кыштым й") == "кыштым й"
    assert nm.norm("“Templeman”") == '"templeman"' and nm.norm("éxito") == "exito"
    from researcher_steps.evidence_pool import norm as ep_norm
    assert ep_norm("Озёрск") == "озёрск"                                        # el alias


def test_slugify_con_el_id():
    a = {"id": "F03", "url": "https://ru.wikipedia.org/wiki/x", "anio": 2020, "titulo": "Кыштымская авария"}
    b = {**a, "id": "F07", "titulo": "Авария на «Маяке»"}
    assert r3.slugify(a) != r3.slugify(b) and r3.slugify(a).endswith("-F03")


def test_alias_viejos():
    assert r3.person_key("Sgt. Bell") == ("", "bell") and r3.is_named_person("V.M. Osetrov")
    assert r3.same_person("Marlin N. Gusman", "Sheriff Martin Gusman")
    from researcher_steps.evidence_pool import is_person
    from researcher_steps.verify_quotes import _named
    from script_engine import guion_v4 as g4
    from script_engine import m01b_guionista as mg
    assert is_person("Любовь Ладейщикова") and _named("I.F. Serov")
    assert ev._surname("Lev Tumerman") == g4._surname("Lev Tumerman") == mg._surname("Lev Tumerman") == "tumerman"


def test_personaje_de_r3_con_iniciales_y_cirilico():
    doc = {"id": "F01", "idioma": "ru"}
    text = ("В.М. Осетров рассказал о взрыве. I.F. Serov estaba en la planta 25. " * 3)
    raw = {"datos": [], "cronologia": [], "lugares": [], "citas": [], "personajes": [
        {"nombre": "I.F. Serov", "rol": "operario", "testigo": True, "cita_literal": "I.F. Serov estaba en la planta 25"},
        {"nombre": "Осетров", "rol": "operario", "testigo": True, "cita_literal": "В.М. Осетров рассказал о взрыве"}]}
    part = r3.validate_doc_items(raw, doc, r3.DocText("F01", text), [])
    assert [p["nombre"] for p in part["personajes"]] == ["I.F. Serov", "Осетров"]     # mononimio con rol


# ═══════════════════════════════════════════════════════════════
#  Fuera el molde de Orleans (B)
# ═══════════════════════════════════════════════════════════════

def test_role_class_con_el_perfil():
    from script_engine.guion_v3_reglas import role_class, role_problems
    assert role_class("el deputy Foster") is None and role_class("un preso") is None      # sin perfil: nada
    r3.set_vocabulario(PERFIL_ORLEANS)
    assert role_class("el deputy Foster") == "antagonista" and role_class("un preso") == "testigo"
    r3.set_vocabulario(PERFIL_KYSHTYM)
    assert role_class("el teniente") is None
    pool = {"personajes": [{"nombre": "Pavel Ivanov", "rol": "sobreviviente"}], "citas": []}
    t = "El teniente Ivanov llegó primero. Horas después, el sobreviviente Ivanov volvió a la planta."
    assert role_problems(t, pool) == []
    r3.set_vocabulario(None)
    assert role_problems(t, pool) == []


def test_fix_glued_caps_con_los_roles_del_pool():
    pool = {"personajes": [{"nombre": "Ana Paz", "rol": "recluso de Templeman III"}]}
    assert ev.fix_glued_caps("Lo vio el Recluso dijo después.", pool) == "Lo vio el recluso dijo después."
    assert ev.fix_glued_caps("Llegó el Huracán Katrina.", pool) == "Llegó el Huracán Katrina."
    assert ev.fix_glued_caps("Llegó a Templeman III.", pool) == "Llegó a Templeman III."


def test_photo_problems_solo_la_foto():
    from script_engine.guion_v3_reglas import photo_problems
    assert photo_problems([{"chapter_number": 3, "narration": "La cámara de reacción y la imagen satelital."}]) == []
    assert photo_problems([{"chapter_number": 3, "narration": "La foto muestra el patio."}])


def test_sin_sujeto_de_orleans():
    assert not hasattr(r3, "SUBJECT_RE_DEFAULT") and not hasattr(r3, "_OTHER_PLACE")
    assert r3.subject_re_del_perfil({"nombres_lugar": ["Mayak"], "nombres_locales": ["Маяк"]})
    assert r3.subject_re_del_perfil({}) is None
    from researcher_steps.verify_quotes import build_prompt
    p = build_prompt({"texto": "x", "autor": "y"}, "Kyshtym, 1957")
    assert "Orleans" not in p and "TEMA: Kyshtym, 1957" in p


# ═══════════════════════════════════════════════════════════════
#  Los jueces leen la traducción (F)
# ═══════════════════════════════════════════════════════════════

def test_pool_con_traducciones():
    from script_engine import guion_v4 as g4
    from script_engine.m05_narrative import false_quotes
    pool = {"citas": [{"id": "Q01", "texto": "Nobody ever came for us in that place", "texto_original":
                       "Nobody ever came for us in that place", "autor": "Ivan Osetrov"}]}
    ficha = {"citas": [{"texto": "Nobody ever came for us in that place", "traduccion":
                        "Nadie vino nunca por nosotros en ese lugar", "ids": ["Q01"]}]}
    t = "«Nadie vino nunca por nosotros en ese lugar», dijo Osetrov."
    assert false_quotes(t, pool)                                                 # el juez de antes: «cita falsa»
    pj = g4.pool_con_traducciones(pool, ficha)
    assert false_quotes(t, pj) == [] and pj["citas"][0]["texto_original"] == "Nobody ever came for us in that place"
    assert g4.pool_con_traducciones(pool, None) is pool and pool["citas"][0]["texto"].startswith("Nobody")


# ═══════════════════════════════════════════════════════════════
#  Prompts sin cambio
# ═══════════════════════════════════════════════════════════════

def test_md5_de_los_cuatro_prompts():
    from researcher_steps import ficha_caso as fc
    from script_engine import guion_v4 as g4
    from script_engine import m01a_columna as mc
    from script_engine import m01a_escaleta as me

    def m(s: str) -> str:
        return hashlib.md5(s.encode("utf-8")).hexdigest()
    assert m(fc.system()) == "2e151732da47e09acf0cb48eb7089fcb"
    assert m(mc.SYSTEM) == "1408569c5c9de22ec406a10ba0cd9b13"
    assert m(me.SYSTEM_V2) == "49ed74d941def064cdda077212629ff1"
    assert m(g4.system()) == "cdce609abea95ee36d0eb4f44d74dda8"


# ═══════════════════════════════════════════════════════════════
#  F21b
# ═══════════════════════════════════════════════════════════════

def test_f21b_bloqueante_b_con_y_sin_perfil(tmp_path, monkeypatch):
    import fase1_5 as f15
    from script_engine import guion_v4 as g4
    from test_module_f11 import TOPIC, _esc_ok, _parrafos
    esc = _esc_ok()
    ps = _parrafos(esc)
    ps[3]["texto"] += " La sobreviviente Daniel Areco miró la puerta."          # Areco es guardia de seguridad
    (tmp_path / "t").mkdir()
    (tmp_path / "t" / "_perfil.json").write_text(json.dumps(
        {"roles_testigo": ["sobreviviente"], "roles_antagonista": ["guardia"]}), encoding="utf-8")
    monkeypatch.setattr(f15, "STEPS_DIR", tmp_path)
    assert f15.cargar_perfil("t") is True and g4.nota_b() is None
    assert any(x["codigo"] == "b" for x in g4.bloqueantes(TOPIC, esc, ps, largo="objetivo"))
    assert f15.cargar_perfil("sin-perfil") is False
    assert g4.nota_b() == "(b) sin perfil: no evaluado"
    assert not any(x["codigo"] == "b" for x in g4.bloqueantes(TOPIC, esc, ps, largo="objetivo"))


def test_f21b_rol_que_decide_en_cualquier_parte():
    r3.set_vocabulario({"roles_antagonista": ["sheriff", "ministerio"]})
    says = r3._official_says()
    assert says.search("El sheriff tenía 6375 presos.") and says.search("Según el ministerio, 10.000 evacuados.")
    assert says.search("Los registros oficiales dan 6375.") and not says.search("La prensa estimó 7,000.")
    assert not says.search("El sheriffazo")                                     # palabra entera


@pytest.mark.parametrize("nombre, es", [
    ("Толстиков, Бочкарева", False), ("Ana Paz y Juan Gil", False), ("Ann Lee and Bob Ray", False),
    ("Sheriff de Orleans Parish", False), ("Captain of the Guard", False), ("Director of Corrections", False),
    ("Juan de la Cruz", True), ("Deputy Foster", True), ("María Berzabé Meza Vda. de Brizuela", True),
    ("Leroy P. Gardner, III", True), ("Ronnie Lee Morgan, Jr.", True),            # la coma antes del sufijo
])
def test_f21b_criterios_de_forma(nombre, es):
    assert nm.es_persona(nombre) is es


def test_f21b_add_quote_authors_los_salta():
    pool = {"personajes": [], "citas": [
        {"id": "Q01", "autor": "Толстиков, Бочкарева", "doc_id": "F01", "cita_literal": "x", "offset": 0, "docs": ["F01"],
         "n_fuentes": 1, "evidencia": []},
        {"id": "Q02", "autor": "Sheriff de Orleans Parish", "doc_id": "F01", "cita_literal": "x", "offset": 0,
         "docs": ["F01"], "n_fuentes": 1, "evidencia": []},
        {"id": "Q03", "autor": "Любовь Ладейщикова", "doc_id": "F01", "cita_literal": "x", "offset": 0, "docs": ["F01"],
         "n_fuentes": 1, "evidencia": []}]}
    r3.add_quote_authors(pool, [])
    assert [p["nombre"] for p in pool["personajes"]] == ["Любовь Ладейщикова"]


# ═══════════════════════════════════════════════════════════════
#  F21c
# ═══════════════════════════════════════════════════════════════

@pytest.mark.parametrize("nombre, es, cl", [
    ("Warden de Hunt Correctional Center", False, None), ("Director of Corrections", False, None),
    ("el director Ivanov", True, ("", "ivanov")), ("la ministra Ana Paz", True, ("ana", "paz")),
])
def test_f21c_cargos_genericos(nombre, es, cl):
    assert nm.es_persona(nombre) is es
    if cl:
        assert nm.clave(nombre) == cl


def test_f21c_elegible_tiene_que_ser_persona():
    pool = {"cronologia": [], "datos": [],
            "citas": [{"autor": "periódico Komsomolskaya Pravda", "texto": "x", "verificacion": {"estado": "verificada"}},
                      {"autor": "Rasputin", "texto": "y", "verificacion": {"estado": "verificada"}}],
            "personajes": [{"nombre": "periódico Komsomolskaya Pravda", "presente_en": []},
                           {"nombre": "Rasputin", "rol": "monje", "presente_en": []}]}
    r3.person_stats(pool, 1957)
    assert [p["elegible_humano"] for p in pool["personajes"]] == [False, True]
