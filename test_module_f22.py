"""
test_module_f22.py — F22 (familias C + E de la auditoría y el nombre como lo escribe el documento): los cuatro bloques
SISTEMA byte-idénticos a los archivos del handoff (extraídos anclando en «## SISTEMA», hasta el «---»), la tarea de la
columna literal, los prompts viejos intactos con su versión (F39 §A.2: la escaleta v1, sin ficha, se borró con su
test); el antagonista persona /
institución / ninguno en columna, escaleta, partición y guion; `verify_pool` con `autor_en_documento` (documento ruso
de Kyshtym ya bajado); los mensajes al modelo sin nombres de Orleans; «cero Cardal»; el dorado v3 con solo los mensajes
cambiados. Sin red.
"""
from __future__ import annotations

import copy
import hashlib
import json
import sys
from pathlib import Path

import pytest

from researcher_steps import ficha_caso as fc
from researcher_steps import research_v3 as r3
from script_engine import guion_v3_reglas as gr
from script_engine import guion_v4 as g4
from script_engine import m01a_columna as mc
from script_engine import m01a_escaleta as me
from script_engine import m01d_particion as md
from test_module_f6b import POOL, good
from test_module_f16 import TOPIC
from test_module_f17 import FICHA as FICHA17
from test_module_f17 import col_buena

ROOT = Path(__file__).resolve().parent
F22 = ROOT / "lab" / "hyperframes" / "f22"
STEPS = ROOT / "data" / "scripts" / "_steps"
sys.path.insert(0, str(F22))
import cero_cardal  # noqa: E402

HANDOFF_MD5 = {"HANDOFF_F22_ejemplos_y_antagonista.md": "2685deecf8e8516d6cc8ee2c61b47384",
               "CASO_EJEMPLO_cardal.md": "7068cef5063db1de5a015c50891204e4",
               "PROMPT_FICHA_v2_1.md": "168358d182f9831dedc1bd21ba910540",
               "PROMPT_COLUMNA_v1_1.md": "af1d5f4150b4f4fc54a0c603e7f65cbb",
               # F22e: el archivo suma una oración en <oficio> §2 (antes 601aa76a77ce2c1dd9bd861a3bba6a02)
               "PROMPT_ESCALETA_v2_1.md": "dc08061c557951c0daa21d6e81cfa793",
               "PROMPT_GUIONISTA_v5_2.md": "9d80720a0d6770c7cb4220f2ba0f4217"}

# la institución que decide en el fixture (inventada: no es de ningún tema)
INST = {"nombre": "Ministerio de Obras", "rol": "ministerio que ordena no evacuar",
        "variantes": ["el Ministerio", "MinObras"], "ids": ["T01"]}


def _md5(s: str) -> str:
    return hashlib.md5(s.encode("utf-8")).hexdigest()


def _sistema(name: str) -> str:
    md = (F22 / name).read_text(encoding="utf-8").replace("\r\n", "\n")
    i = md.index("\n## SISTEMA\n\n") + len("\n## SISTEMA\n\n")
    return md[i:md.index("\n\n---\n", i)]


def _ficha_inst() -> dict:
    f = copy.deepcopy(FICHA17)
    f["personas"].append(copy.deepcopy(INST))
    return f


# ═══════════════════════════════════════════════════════════════
#  §3 md5: archivos del handoff, cuatro SISTEMA, tarea de la columna, viejos intactos
# ═══════════════════════════════════════════════════════════════

@pytest.mark.parametrize("name, md5", sorted(HANDOFF_MD5.items()))
def test_md5_de_los_archivos_del_handoff(name, md5):
    # los md5 del analista son de los archivos en LF (git puede dejarlos en CRLF al hacer checkout)
    assert hashlib.md5((F22 / name).read_bytes().replace(b"\r\n", b"\n")).hexdigest() == md5


def test_los_cuatro_sistemas_byte_identicos_al_handoff():
    # F23: la ficha v2.1 y el guion v5.2 quedan con su versión (f22-1); los de hoy, en test_module_f23
    assert fc.system("f22-1") == fc.SYSTEM_F22_1 == _sistema("PROMPT_FICHA_v2_1.md")
    assert mc.SYSTEM == _sistema("PROMPT_COLUMNA_v1_1.md")
    assert me.SYSTEM_V2_F22_2 == _sistema("PROMPT_ESCALETA_v2_1.md")   # F24: la f22-2, con su versión
    assert g4.system("f22-1") == g4.SYSTEM_V5_2 == _sistema("PROMPT_GUIONISTA_v5_2.md")
    assert [_md5(x) for x in (fc.system("f22-1"), mc.SYSTEM, me.SYSTEM_V2_F22_2, g4.system("f22-1"))] == [
        "7d3599dc6e4123a3bb883fc15a541e71", "f294cf6b1220983903ce339f5b21cb27", "22cfd68b7cee4734e95bb3ee27bb96b2",
        "743e4f0a7ff9e58d86762bbd43679952"]                                     # F22e: escaleta 22cfd68b
    assert _md5(me.SYSTEM_V2_F22_1) == "7ea18a6aa1ca91c5ad0dfb7cc9b239a8"     # la v2.1 de F22, con su versión
    for s in (fc.system(), mc.SYSTEM, me.SYSTEM_V2, g4.system()):
        assert "## SISTEMA" not in s and "Para CC" not in s and s.startswith("<rol>")
    assert (fc.PROMPT_VERSION_F22, mc.PROMPT_VERSION, g4.PROMPT_VERSION_V5_2) == ("f22-1",) * 3
    assert (me.PROMPT_VERSION_V2_F22_2, me.PROMPT_VERSION_V2_F22) == ("f22-2", "f22-1")   # F24: hoy f24-1 (test_module_f24)


def test_tarea_de_la_columna_literal_y_las_otras_sin_cambios():
    md = (F22 / "PROMPT_COLUMNA_v1_1.md").read_text(encoding="utf-8").replace("\r\n", "\n")
    u0 = md.index("\n## USUARIO")
    assert mc.TAREA == md[md.index("<tarea>", u0):md.index("</tarea>", u0) + len("</tarea>")]
    assert "QUIÉN DECIDE" in mc.TAREA and '"antagonista": {"tipo"' in mc.TAREA
    p = mc.build_prompt(TOPIC, POOL, FICHA17)
    assert p.endswith(mc.TAREA)
    # la tarea del guion es la del USUARIO del v5.2 («sin cambios respecto de v5.1»); las de la escaleta, las de F16/F17
    gmd = (F22 / "PROMPT_GUIONISTA_v5_2.md").read_text(encoding="utf-8").replace("\r\n", "\n")
    assert g4.TAREA_V5 in gmd[gmd.index("\n## USUARIO"):]
    assert _md5(me.TAREA_V2) == "5808b41eb57a0949f009213d52076521"            # = 8be0ea9
    assert _md5(me.TAREA_COLUMNA) == "b53c30be945ea2ababa857ff04e87c83"       # = 8be0ea9


def test_los_viejos_quedan_con_su_version():
    assert _md5(fc.system("f15-1")) == "2e151732da47e09acf0cb48eb7089fcb"
    assert _md5(mc.SYSTEM_F17_1) == "1408569c5c9de22ec406a10ba0cd9b13"
    assert _md5(me.SYSTEM_V2_F16_1) == "49ed74d941def064cdda077212629ff1"
    assert _md5(g4.system("f15b-1")) == "cdce609abea95ee36d0eb4f44d74dda8"
    assert g4.system("f15-1") == g4.SYSTEM_V5 and g4.VERSIONES_V5 == ("f54-2", "f25-1", "f23-1", "f22-1", "f15b-1", "f15-1")


def test_prompts_sin_ejemplos_de_orleans_ni_ycua():
    for s in (fc.system(), mc.SYSTEM, mc.TAREA, me.SYSTEM_V2, g4.system()):
        for w in ("Templeman", "Gusman", "Reed", "Pearl", "Orleans", "Ycuá", "Paiva", "517", "398", "Q184", "D192",
                  "guaraníes", "huérfanos"):
            assert w not in s, w


# ═══════════════════════════════════════════════════════════════
#  §1.1 research y mensajes al modelo sin nombres de Orleans
# ═══════════════════════════════════════════════════════════════

def test_research_r3_y_seed_sin_orleans():
    seed = {"seed_title": "x"}
    p = r3.build_extraction_prompt(seed, {"titulo": "t", "tipo": "otro", "url": "u"}, "texto", (1, 1))
    assert "Templeman" not in p and "«una vecina», «un operario»" in p
    assert p.count("exactamente como aparece en ESTE texto, en su alfabeto; vacío") == 2
    src = (ROOT / "researcher_steps" / "research_v3.py").read_text(encoding="utf-8")
    assert '"anio":2006' not in src and src.count('"anio":0,"idioma":"xx"') == 3
    assert "Nueva Orleans" not in src and "el idioma del lugar del caso" in src
    assert "una planta: operario, ingeniero, evacuado" in src and "el dueño · el ministerio · el" in src
    for k in ("autor_en_documento",):
        assert k in r3.R3_SCHEMA["properties"]["citas"]["items"]["properties"]
    assert "nombre_en_documento" in r3.R3_SCHEMA["properties"]["personajes"]["items"]["properties"]


def test_mensajes_al_modelo_sin_nombres_de_orleans():
    for f in ("script_engine/m05_narrative.py", "script_engine/guion_v3_reglas.py"):
        src = (ROOT / f).read_text(encoding="utf-8")
        # los mensajes que van al modelo (los docstrings con Orleans son de la familia J, fuera de esta tanda)
        for w in ("«Interestatal 10» no son", "«sheriff Marlin N. Gusman» basta", "«Nueva Orleans, agosto",
                  "la celda, el calor", "después de la primera, «ese domingo»"):
            assert w not in src, (f, w)


def test_ancla_modelo_con_el_lugar_y_el_anio_del_seed():
    try:
        r3.set_vocabulario(None)
        m = gr.hook_anchor_problems("Una frase sin ancla.", {"lugares": [{"nombre": "Asunción"}]})
        assert m and "Nueva Orleans" not in m[0] and "«" not in m[0]
        r3.set_vocabulario({"lugar_principal": "Asunción", "anio_evento": 2004})
        m = gr.hook_anchor_problems("Una frase sin ancla.", {"lugares": [{"nombre": "Asunción"}]})
        assert "«Asunción, 2004.»" in m[0]
    finally:
        r3.set_vocabulario(None)


def test_fechas_ese_dia():
    # F23 §1.1: dos fechas en un cap ya no son un problema (métrica); el mensaje ya no tiene «ese domingo»
    caps = [{"chapter_number": 2, "narration": "El 1 de agosto pasó. El 2 de agosto, otra cosa."}]
    assert gr.date_problems(caps) == [] and gr.fechas_literales_por_cap(caps) == {2: 2}
    src = (ROOT / "script_engine" / "guion_v3_reglas.py").read_text(encoding="utf-8")
    assert "«ese domingo»" not in src


# ═══════════════════════════════════════════════════════════════
#  §1.2 antagonista: columna
# ═══════════════════════════════════════════════════════════════

def test_esquema_columna_con_antagonista_de_tres_tipos():
    a = mc.SCHEMA["properties"]["antagonista"]
    assert a["properties"]["tipo"]["enum"] == ["persona", "institucion", "ninguno"]
    assert "antagonista" in mc.SCHEMA["required"]


@pytest.mark.parametrize("ag, ok", [
    ({"tipo": "persona", "nombre": "Marlin N. Gusman", "por_que": "x", "ids": ["P01"]}, True),
    ({"tipo": "persona", "nombre": "Nadie Inventado", "por_que": "x", "ids": []}, False),
    ({"tipo": "institucion", "nombre": "Ministerio de Obras", "por_que": "x", "ids": ["T01"]}, True),
    ({"tipo": "institucion", "nombre": "MinObras", "por_que": "x", "ids": []}, True),            # una variante
    ({"tipo": "institucion", "nombre": "el Ministerio", "por_que": "x", "ids": []}, True),       # variante con artículo
    ({"tipo": "institucion", "nombre": "Comisión Nacional", "por_que": "x", "ids": []}, False),  # no está en la ficha
    ({"tipo": "ninguno", "nombre": "", "por_que": "la ficha no atribuye la decisión a nadie", "ids": []}, True),
    ({"tipo": "ninguno", "nombre": "", "por_que": " ", "ids": []}, False),
])
def test_chequeo_columna_antagonista(ag, ok):
    c = col_buena()
    c["antagonista"] = ag
    prob = mc.chequeo(c, POOL, _ficha_inst())
    assert (prob == []) is ok, prob
    if not ok:
        assert all(p.startswith("antagonista") for p in prob)


def test_institucion_en_dos_hechos_aunque_no_sea_persona_de_la_ficha():
    f = copy.deepcopy(FICHA17)
    f["hechos"] += [{"texto": "La Comisión Nacional ordenó cerrar.", "ids": ["T01"]},
                    {"texto": "Según la comisión nacional, no hubo muertos.", "ids": ["D09"]}]
    assert mc.institucion_de_la_ficha("la Comisión Nacional", f)
    assert not mc.institucion_de_la_ficha("Comisión Nacional", FICHA17)
    assert me.institucion_de_la_ficha("la Comisión Nacional", f)          # la escaleta usa la misma


def test_columna_markdown_y_seccion_con_quien_decide():
    c = col_buena()
    c["antagonista"] = {"tipo": "institucion", "nombre": "Ministerio de Obras", "por_que": "ordena", "ids": ["T01"]}
    md_ = mc.to_markdown(c, "x")
    assert md_.index("**HUMANO:**") < md_.index("**QUIÉN DECIDE:** Ministerio de Obras (institución): ordena") < \
        md_.index("**PICO:**")
    s = mc.section(c)
    assert s.index("HUMANO:") < s.index("QUIÉN DECIDE: Ministerio de Obras (institución): ordena [T01]") < \
        s.index("PICO:")
    c["antagonista"] = {"tipo": "ninguno", "nombre": "", "por_que": "nadie decidió", "ids": []}
    assert "**QUIÉN DECIDE:** ninguno: nadie decidió" in mc.to_markdown(c)
    del c["antagonista"]
    assert "QUIÉN DECIDE" not in mc.section(c)                             # una columna de F17 se lee igual


# ═══════════════════════════════════════════════════════════════
#  §1.2 antagonista: escaleta v2.1
# ═══════════════════════════════════════════════════════════════

def _esc_v2(ag: dict) -> dict:
    e = good()
    e["antagonista"] = ag
    return e


def test_esquema_escaleta_con_tres_tipos():
    a = me.SCHEMA_FICHA["properties"]["antagonista"]
    assert a["properties"]["tipo"]["enum"] == ["persona", "institucion", "ninguno"]
    assert me.SCHEMA["properties"]["antagonista"] == {"type": "OBJECT", "properties": {
        "id": {"type": "STRING"}, "por_que": {"type": "STRING"}}, "required": ["id"]}   # sin ficha: como siempre


@pytest.mark.parametrize("ag, ok", [
    ({"tipo": "persona", "id": "P01", "nombre": "Marlin N. Gusman", "por_que": "x"}, True),
    ({"tipo": "persona", "id": "P99", "nombre": "x", "por_que": "x"}, False),
    ({"tipo": "institucion", "id": "", "nombre": "MinObras", "por_que": "x"}, True),
    ({"tipo": "institucion", "id": "", "nombre": "Comisión Nacional", "por_que": "x"}, False),
    ({"tipo": "ninguno", "id": "", "nombre": "", "por_que": "la ficha no lo atribuye"}, True),
    ({"tipo": "ninguno", "id": "", "nombre": "", "por_que": ""}, False),
])
def test_bloqueante_antagonista_escaleta(ag, ok):
    raw, _ = me.ids_v2(_esc_v2(ag))
    _, bloq, _, _ = me.bloqueantes(raw, POOL, _ficha_inst())
    ant = [b for b in bloq if b.startswith("antagonista")]
    assert (ant == []) is ok, bloq
    assert all(me.bloqueante_de(b) == "antagonista es persona de la ficha" for b in ant)


def test_generar_escaleta_con_institucion_copia_variantes_y_mide(monkeypatch, tmp_path):
    monkeypatch.setattr(me, "STEPS_DIR", tmp_path)
    monkeypatch.setattr(me, "pool_gate_profile", lambda *a, **k: None)
    e = _esc_v2({"tipo": "institucion", "id": "", "nombre": "Ministerio de Obras", "por_que": "ordena"})
    e["beats"][1]["cierre"] = "El Ministerio no contestó."
    e["beats"][6]["imagen_sensorial"] = "la carta de MinObras sobre una mesa vacía de la oficina"
    col = col_buena()
    col["antagonista"] = {"tipo": "institucion", "nombre": "el Ministerio de Obras", "por_que": "x", "ids": ["T01"]}
    esc = me.generate_escaleta(TOPIC, call=lambda *a, **k: copy.deepcopy(e), persist=False, ficha=_ficha_inst(),
                               columna=col)
    assert esc["prompt_version"] == me.PROMPT_VERSION_COLUMNA
    assert esc["antagonista"]["variantes"] == ["el Ministerio", "MinObras"]
    m = esc["_metricas"]
    assert m["antagonista_tipo"] == "institucion" and m["antagonista_caps"] == [2, 6]
    assert m["columna"]["antagonista_es_el_de_la_columna"] is True
    col["antagonista"] = {"tipo": "ninguno", "nombre": "", "por_que": "x", "ids": []}
    esc = me.generate_escaleta(TOPIC, call=lambda *a, **k: copy.deepcopy(e), persist=False, ficha=_ficha_inst(),
                               columna=col)
    assert esc["_metricas"]["columna"]["antagonista_es_el_de_la_columna"] is False


def test_metricas_escaleta_con_persona():
    esc, _, _, _ = me.validate(good(), POOL)
    m = me.antagonista_metricas(esc, POOL)
    assert m == {"antagonista_tipo": "persona", "antagonista_caps": []}      # sin tipo = persona; nadie nombra a Gusman
    esc["beats"][1]["datos_apoyo"] = ["D03", "Q02"]                         # Q02: «Sheriff Gusman»
    assert me.antagonista_metricas(esc, POOL)["antagonista_caps"] == [2]


# ═══════════════════════════════════════════════════════════════
#  §1.2 antagonista: partición (m01d) y guion
# ═══════════════════════════════════════════════════════════════

def test_m01d_conserva_la_institucion_con_su_tipo():
    from test_module_f10 import POOL as POOL10
    from test_module_f10 import _esc, _parrafos
    esc = _esc()
    esc["antagonista"] = {"tipo": "institucion", "id": "", "nombre": "Ministerio de Obras", "variantes": ["MinObras"]}
    esc["beats"][4]["imagen_sensorial"] = "la carta de MinObras"
    sk, _, _ = md.build_contract({"id": "t"}, esc, _parrafos(esc), POOL10, title_list=[f"T{n}" for n in range(1, 8)])
    inst = [p for p in sk["personajes"] if p.get("tipo") == "institucion"]
    assert inst == [{"id": "", "nombre": "Ministerio de Obras", "rol": "institución", "tipo": "institucion",
                     "variantes": ["MinObras"], "antagonista": True, "entra_en_cap": esc["beats"][4]["cap"]}]
    assert [p["nombre"] for p in sk["personajes"]] == ["Blas Cristaldo", "Ministerio de Obras"]
    esc["antagonista"] = {"tipo": "ninguno", "id": "", "nombre": "", "por_que": "x"}
    sk, _, _ = md.build_contract({"id": "t"}, esc, _parrafos(esc), POOL10, title_list=[f"T{n}" for n in range(1, 8)])
    assert [p["nombre"] for p in sk["personajes"]] == ["Blas Cristaldo"]


def test_m05_no_pide_nombre_y_apellido_a_una_institucion():
    from script_engine import m05_narrative as m05
    import inspect
    src = inspect.getsource(m05)
    assert 'if p.get("tipo") == "institucion":' in src


def test_antagonista_y_anon_voice_solo_con_persona():
    from test_module_f7 import POOL_C3
    caps = [{"chapter_number": 2, "narration": "El 28 de agosto hubo una reunión. La orden fue clara, según alguien."}]
    beats = [{"n": 2, "cap": 2, "dato_central": "T39", "datos_apoyo": ["Q02"]}]
    pers = gr.antagonist_problems(caps, {"antagonista": {"id": "P03"}, "beats": beats}, POOL_C3)
    assert any("no se nombra" in x for x in pers) and any("según alguien" in x for x in pers)   # Orleans, como antes
    pers2 = gr.antagonist_problems(caps, {"antagonista": {"tipo": "persona", "id": "P03"}, "beats": beats}, POOL_C3)
    assert pers2 == pers
    for ag in ({"tipo": "institucion", "id": "", "nombre": "Ministerio de Obras"},
               {"tipo": "ninguno", "id": "", "nombre": "", "por_que": "x"}):
        assert gr.antagonist_problems(caps, {"antagonista": ag, "beats": beats}, POOL_C3) == []


def test_guion_metrica_la_institucion_se_nombra_en_n_caps():
    from test_module_f7 import POOL_C3
    caps = [{"chapter_number": 1, "narration": "Nadie lo sabía."},
            {"chapter_number": 3, "narration": "La orden vino del Ministerio de Obras."},
            {"chapter_number": 5, "narration": "MinObras no contestó."}]
    esc = {"antagonista": {"tipo": "institucion", "nombre": "el Ministerio de Obras", "variantes": ["MinObras"]}}
    assert gr.antagonista_caps(caps, esc, POOL_C3) == [3, 5]
    assert gr.antagonista_caps(caps, {"antagonista": {"tipo": "ninguno"}}, POOL_C3) == []
    caps.append({"chapter_number": 6, "narration": "Marlin Gusman no habló."})
    assert gr.antagonista_caps(caps, {"antagonista": {"id": "P03"}}, POOL_C3) == [6]


def test_guion_metricas_traen_antagonista():
    from test_module_f11 import POOL as POOL11
    from test_module_f11 import TOPIC as TOPIC11
    from test_module_f11 import _esc_ok
    from script_engine import m01b_guionista as mg
    esc = _esc_ok()
    ps = mg.normalize({"parrafos": [{"beat": b["n"], "texto": "x"} for b in esc["beats"]]}, esc, POOL11)
    m = g4.metricas(TOPIC11, esc, ps)
    assert m["antagonista_tipo"] == "persona" and m["antagonista_caps"] == []
    assert POOL11 is TOPIC11["evidence_pool"]


def test_ficha_institucion_en_personas_pasa_el_chequeo():
    # el chequeo de la ficha no aplica es_persona a `personas` (y no se le agrega nada): una institución pasa
    ficha = {"personas": [{"nombre": "Ministerio de Obras", "rol": "ministerio", "variantes": [], "ids": ["T01"]}]}
    out, sacados = fc.check(ficha, POOL)
    assert out["personas"] == ficha["personas"] and sacados == []


# ═══════════════════════════════════════════════════════════════
#  §1.3 el nombre como lo escribe el documento (Kyshtym, documento ruso F13 ya bajado)
# ═══════════════════════════════════════════════════════════════

def _kyshtym():
    d = STEPS / "f18-kyshtym-mayak"
    pf = d / "00_pool_v3_f22.json"                       # F23 rehízo el pool: el de F22 quedó como respaldo
    pf = pf if pf.exists() else d / "00_pool_v3.json"
    if not pf.exists():
        pytest.skip("sin el pool de Kyshtym en _steps")
    pool = json.loads(pf.read_text(encoding="utf-8"))
    docs = pool["_research_v3"]["documentos"]
    f13 = next(x for x in docs if x["id"] == "F13")
    if not (d / "fuentes" / f13["txt"]).exists():
        pytest.skip("sin el txt de F13")
    return pool, docs, r3.DocText("F13", (d / "fuentes" / f13["txt"]).read_text(encoding="utf-8"))


def _verif(q: dict, dt, docs) -> str:
    p = {k: [] for k in r3.KINDS}
    p["citas"] = [q]
    r3.verify_pool(p, {"F13": dt}, docs)
    return q["verificacion"]["estado"]


@pytest.mark.parametrize("qid, forma, estado", [
    ("Q16", None, "verificada_parcial"),                 # sin el campo: igual que hoy (Osetrov ↔ Осетров)
    ("Q16", "", "verificada_parcial"),
    ("Q16", "В.М. Осетрова", "verificada"),              # como lo escribe el texto junto a la cita
    ("Q16", "Осетров", "verificada_parcial"),            # en nominativo: a 658 caracteres, fuera de la ventana
    ("Q17", "В.И. Комарова", "verificada"),
    ("Q18", "Серов", "verificada"),
    ("Q18", None, "verificada_parcial"),
])
def test_verify_pool_con_autor_en_documento(qid, forma, estado):
    pool, docs, dt = _kyshtym()
    q = copy.deepcopy(next(x for x in pool["citas"] if x["id"] == qid))
    if forma is not None:
        q["autor_en_documento"] = forma
    assert _verif(q, dt, docs) == estado


def test_validate_personaje_acepta_nombre_en_documento():
    _, _, dt = _kyshtym()
    lit = dt.text[12560:12620]
    raw = {"personajes": [{"nombre": "V.M. Osetrov", "rol": "maquinista", "testigo": True, "cita_literal": lit}]}
    out = r3.validate_doc_items(raw, {"id": "F13", "titulo": "t"}, dt, [])
    assert out["personajes"] == [] and "el apellido no está en el documento" in out["_descartados"][0]["motivo"]
    raw["personajes"][0]["nombre_en_documento"] = "В.М. Осетров"
    out = r3.validate_doc_items(raw, {"id": "F13", "titulo": "t"}, dt, [])
    assert out["personajes"][0]["nombre_en_documento"] == "В.М. Осетров"


def test_merge_y_presencia_con_nombre_en_documento():
    a = {"nombre": "V.M. Osetrov", "nombre_en_documento": "В.М. Осетров"}
    assert r3.name_terms(a, [a]) == ["osetrov", "осетров"]
    assert r3.name_terms({"nombre": "V.M. Osetrov"}, [{"nombre": "V.M. Osetrov"}]) == ["osetrov"]   # pool viejo
    b = {**a, "nombre_en_documentos": ["В.М. Осетров", "Осетрова"]}   # lo que deja el merge
    assert r3.en_documento(b, "nombre_en_documento") == ["В.М. Осетров", "Осетрова"]
    assert r3.en_documento({"nombre": "x"}, "nombre_en_documento") == []


# ═══════════════════════════════════════════════════════════════
#  §3 «cero Cardal»
# ═══════════════════════════════════════════════════════════════

def test_cero_cardal_en_los_controles():
    hf = ROOT / "lab" / "hyperframes"
    controles = [hf / "f7" / "ESCALETA_orleans_v3r3.md", hf / "f7" / "NARRACION_orleans_v3r3.md",
                 hf / "f17" / "COLUMNA_ycua.md", hf / "f16" / "ESCALETA_ycua_f16.md", hf / "f16" / "NARRACION_ycua_f16.md"]
    for p in controles:
        if p.exists():
            assert cero_cardal.coincidencias(p.read_text(encoding="utf-8")) == {}, p.name
    caso = cero_cardal.coincidencias((F22 / "CASO_EJEMPLO_cardal.md").read_text(encoding="utf-8"))
    assert {"Cardal", "Soto", "Bascuñán", "Quiroga", "Marín", "Alborada", "Faros y Balizas", "telegrama"} <= set(caso)
    assert cero_cardal.coincidencias("olía a queroseno; los telegramas de Soto") == {"Soto": 1, "querosén": 1,
                                                                                     "telegrama": 1}
    assert cero_cardal.coincidencias("Sotomayor y el marino") == {}
