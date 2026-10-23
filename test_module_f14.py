"""
test_module_f14.py — F14 (la ficha en el camino): los 5 criterios de la ficha (un caso por criterio) y
`personas_descartadas`; la escaleta sin ficha byte-idéntica (md5 tomados del m01a_escaleta.py de 2e13616) y con ficha
leyendo la ficha (no el digest) con apoyos 0–6; `guion_v4.data_line` con y sin ficha. Sin red.
"""
from __future__ import annotations

import copy
import hashlib
import json

from researcher_steps import ficha_caso as fc
from script_engine import guion_v4 as g4
from script_engine import m01a_escaleta as ma
from test_module_f11 import POOL as POOL11
from test_module_f11 import TOPIC as TOPIC11
from test_module_f11 import _esc_ok

# md5 del prompt de la escaleta de 2e13616 sobre el fixture de test_module_f11 (sin y con feedback)
ESC_MD5 = {"sin_fb": "37a87c23f619c408e87af31f8b25f1c8", "fb": "729dd168c7277ec7d724d1a5c3bb77bd"}

POOL = {
    "datos": [
        {"id": "D10", "texto": "Murieron 400 personas.", "valor": "400", "doc_id": "F05", "offset": 256,
         "cita_literal": "El suceso se cobró 400 vidas"},
        {"id": "D11", "texto": "Oficialmente hubo 327 muertos.", "valor": "327", "doc_id": "F10", "offset": 3213,
         "cita_literal": "En el incendio hubo oficialmente 327 muertos"},
        {"id": "D12", "texto": "El incendio empezó a las 11:20.", "doc_id": "F09", "offset": 9,
         "cita_literal": "el fuego empezó a las 11:25, según los bomberos"},
        {"id": "D30", "texto": "El alcalde C. Ray Nagin ordenó la evacuación obligatoria.", "doc_id": "F01", "offset": 77,
         "cita_literal": "Mayor C. Ray Nagin ordered a mandatory evacuation"},
        {"id": "D40", "texto": "Los guardias cerraron las puertas.", "doc_id": "F09", "offset": 500,
         "cita_literal": "los guardias cerraron las puertas"},
        {"id": "D41", "texto": "La defensa dice que nadie ordenó cerrar.", "doc_id": "F09", "offset": 900,
         "cita_literal": "nadie dio la orden de cerrar"},
    ],
    "cronologia": [{"id": "T21", "fecha": "2004-08-01", "hora": "11:25", "evento": "Empieza el fuego.", "doc_id": "F09",
                    "offset": 5, "cita_literal": "a las 11:25 empezó el fuego"},
                   {"id": "T22", "fecha": "2004-08-01", "hora": "11:25", "evento": "Primera llamada.", "doc_id": "F10",
                    "offset": 6, "cita_literal": "11:25, primera llamada a los bomberos"}],
    "citas": [{"id": "Q34", "texto": "el portó estaba cerrado", "autor": "Digna Cáceres", "rol": "Sobreviviente",
               "verificacion": {"estado": "verificada"}, "doc_id": "F09", "offset": 7,
               "cita_literal": "el portó estaba cerrado"}],
    "personajes": [{"id": "P28", "nombre": "Víctor Daniel Paiva", "rol": "hijo", "doc_id": "F15", "offset": 524,
                    "cita_literal": "su hijo Víctor Daniel Paiva"},
                   {"id": "P07", "nombre": "Víctor Paiva", "rol": "hijo", "doc_id": "F10", "offset": 3282,
                    "cita_literal": "a su hijo Víctor Paiva, a 10 años"}],
    "lugares": [],
    "_descartados": [{"kind": "personajes", "texto": "C. Ray Nagin", "bloque": "F01",
                      "motivo": "el research no le atribuye ninguna acción"}],
}


def _ficha(**over):
    f = {s: [] for s in fc.SECCIONES}
    f.update(over)
    return f


def _v(dice, doc, off, ids):
    return {"dice": dice, "doc_id": doc, "offset": off, "ids": ids}


# ═══════════════════════════════════════════════════════════════
#  Criterios de la ficha (§1.1): uno por criterio
# ═══════════════════════════════════════════════════════════════

def test_los_cinco_criterios_estan_en_el_prompt_de_la_ficha():
    s = fc.system()
    for t in ("Error de extracción", "Variantes de un nombre", "Conteos", "Hechos disputados", "Horas y fechas"):
        assert t in s
    assert set(fc.SCHEMA["required"]) == set(fc.SECCIONES) | {"historia"} and fc.PROMPT_VERSION == "f15-1"
    assert "<descartados_del_research" in fc.prompt(POOL, "x") and "C. Ray Nagin" in fc.prompt(POOL, "x")


def test_criterio_1_error_de_extraccion_gana_el_pasaje():
    d = {"tema": "hora del inicio", "criterio": 1, "decision": "El pasaje dice que el fuego empezó a las 11:25.",
         "ids": ["D12"], "otras_versiones": [_v("El ítem extraído dice 11:20.", "F09", 9, ["D12"])]}
    out, sacados = fc.check(_ficha(decisiones=[d]), POOL)
    assert out["decisiones"] == [d] and sacados == []


def test_criterio_2_variantes_de_un_nombre():
    d = {"tema": "nombre del hijo", "criterio": 2, "decision": "Víctor Daniel Paiva (forma judicial).",
         "ids": ["P28"], "otras_versiones": [_v("Víctor Paiva", "F10", 3282, ["P07"])]}
    out, _ = fc.check(_ficha(decisiones=[d]), POOL)
    assert out["decisiones"] == [d]


def test_criterio_3_conteo_oficial_y_otras_versiones():
    d = {"tema": "muertos", "criterio": 3, "decision": "La cifra oficial es 327 muertos.", "ids": ["D11"],
         "otras_versiones": [_v("400 vidas", "F05", 256, ["D10"])]}
    mala = {**d, "decision": "La cifra oficial es 364 muertos."}
    out, sacados = fc.check(_ficha(decisiones=[d, mala]), POOL)
    assert out["decisiones"] == [d] and "cifra 364" in sacados[0]["motivo"]


def test_criterio_4_disputado_va_a_versiones_no_a_decisiones():
    v = {"tema": "quién cerró las puertas", "versiones": [_v("Los guardias cerraron las puertas.", "F09", 500, ["D40"]),
                                                           _v("Nadie dio la orden.", "F09", 900, ["D41"])]}
    en_decisiones = {"tema": "quién cerró", "criterio": 4, "decision": "Los guardias.", "ids": ["D40"],
                     "otras_versiones": []}
    out, sacados = fc.check(_ficha(versiones=[v], decisiones=[en_decisiones]), POOL)
    assert out["versiones"] == [v] and out["decisiones"] == []
    assert "el 4 va a versiones" in sacados[0]["motivo"]


def test_criterio_5_hora_que_coincide_en_dos_fuentes_y_aproximada():
    d = {"tema": "hora del inicio", "criterio": 5, "decision": "11:25, en dos fuentes.", "ids": ["T21", "T22"],
         "otras_versiones": []}
    c = {"fecha": "2004-08-01", "hora": "11:25", "evento": "Empieza el fuego.", "aproximada": False, "ids": ["T21"]}
    out, sacados = fc.check(_ficha(decisiones=[d], cronologia=[c]), POOL)
    assert out["decisiones"] == [d] and out["cronologia"] == [c] and sacados == []
    md = fc.markdown({**out, "cronologia": [{**c, "aproximada": True}]}, {"titulo": "x", "usd": 0})
    assert "(aproximada)" in md and "criterio 5" in md


def test_personas_descartadas_nagin():
    ok = {"nombre": "C. Ray Nagin", "rol": "alcalde", "motivo": "ordena la evacuación", "ids": ["D30"]}
    no_desc = {"nombre": "Víctor Paiva", "rol": "hijo", "motivo": "x", "ids": ["P07"]}
    out, sacados = fc.check(_ficha(personas_descartadas=[ok, no_desc]), POOL)
    assert out["personas_descartadas"] == [ok]
    assert "no está entre los descartados del pool" in sacados[0]["motivo"]


def test_id_texts_cita_corregida_cifra_con_unidad_y_hecho():
    f = _ficha(citas=[{"texto": "el portón estaba cerrado", "original": "el portó estaba cerrado", "autor": "Digna Cáceres",
                       "ids": ["Q34"]}],
               cifras=[{"que": "muertos", "valor": "327", "unidad": "personas", "ids": ["D11"],
                        "otras_versiones": [{"valor": "400", "unidad": "personas", "ids": ["D10"]}]}],
               hechos=[{"texto": "Los guardias cerraron las puertas.", "ids": ["D40", "D11"]}],
               cronologia=[{"fecha": "2004-08-01", "hora": "11:25", "evento": "Empieza el fuego.", "aproximada": True,
                            "ids": ["T21"]}])
    t = fc.id_texts(f)
    assert t["Q34"] == "«el portón estaba cerrado» — Digna Cáceres"
    assert t["D11"] == "muertos: 327 personas (otras fuentes: 400 personas)"          # la cifra gana sobre el hecho
    assert t["D40"] == "Los guardias cerraron las puertas."
    assert t["T21"] == "Empieza el fuego. (2004-08-01, 11:25, aproximada)"
    assert fc.id_texts(None) == {}


# ═══════════════════════════════════════════════════════════════
#  Escaleta (§1.2)
# ═══════════════════════════════════════════════════════════════

def _md5(s: str) -> str:
    return hashlib.md5(s.encode("utf-8")).hexdigest()


def test_escaleta_sin_ficha_byte_identica():
    assert _md5(ma.build_prompt(TOPIC11, POOL11)) == ESC_MD5["sin_fb"]
    assert _md5(ma.build_prompt(TOPIC11, POOL11, ["a"])) == ESC_MD5["fb"]
    assert _md5(ma.build_prompt(TOPIC11, POOL11, None, None)) == ESC_MD5["sin_fb"]
    assert "0–3 `datos_apoyo`" in ma.RULES


FICHA_ESC = _ficha(personas=[{"nombre": "Liz Torres", "rol": "sobreviviente", "variantes": [], "ids": ["P1"]}],
                   hechos=[{"texto": "El portón 4 estaba cerrado.", "ids": ["D4"]}],
                   citas=[{"texto": "nadie nos abrió", "autor": "Liz Torres", "rol": "sobreviviente", "ids": ["Q1"]}],
                   versiones=[{"tema": "quién cerró", "versiones": [_v("los guardias", "F09", 1, ["D5"])]}],
                   personas_descartadas=[{"nombre": "C. Ray Nagin", "rol": "alcalde", "motivo": "evacuación",
                                          "ids": ["D6"]}])


def test_escaleta_con_ficha_lee_la_ficha_y_apoyos_0_6():
    pool = copy.deepcopy(POOL11)
    pool["digest"] = {"texto": "DIGEST-QUE-NO-VA"}
    p = ma.build_prompt(TOPIC11, pool, None, FICHA_ESC)
    assert "DIGEST-QUE-NO-VA" not in p and "FICHA DEL CASO" in p
    assert "[D4] El portón 4 estaba cerrado." in p and "[Q1] CITA: \"nadie nos abrió\"" in p
    assert "VERSIONES (hechos disputados" in p and "C. Ray Nagin" in p
    assert "0–6 `datos_apoyo`" in p and "0–3 `datos_apoyo`" not in p
    assert "DIGEST-QUE-NO-VA" in ma.build_prompt(TOPIC11, pool)                       # sin ficha: el digest, como siempre


def test_validate_apoyos_hasta_6_solo_con_ficha():
    esc = _esc_ok()
    raw = {**esc, "beats": [dict(b) for b in esc["beats"]]}
    pool = copy.deepcopy(POOL11)
    libres = [f"D{60 + k}" for k in range(7)]                                # ids que ningún beat usa
    pool["datos"] += [{"id": i, "texto": f"Dato libre {i}.", "fuente": "F01"} for i in libres]
    raw["beats"][1]["datos_apoyo"] = libres
    for b in raw["beats"]:
        if b["n"] != 2:
            b["datos_apoyo"] = []
    v3 = ma.validate(raw, pool)[0]["beats"][1]["datos_apoyo"]
    v6 = ma.validate(raw, pool, max_apoyos=ma.MAX_APOYOS_FICHA)[0]["beats"][1]["datos_apoyo"]
    assert len(v3) == 3 and len(v6) == 6


def test_generate_escaleta_auto_lee_la_ficha_del_disco(tmp_path, monkeypatch):
    seen = []
    monkeypatch.setattr(ma, "STEPS_DIR", tmp_path)
    monkeypatch.setattr(ma, "pool_gate_profile", lambda *a, **k: None)

    def call(prompt, **kw):
        seen.append(prompt)
        raise RuntimeError("corte")
    topic = {**TOPIC11, "id": "t-f14"}
    for con_ficha in (False, True):
        if con_ficha:
            (tmp_path / "t-f14").mkdir()
            (tmp_path / "t-f14" / "ficha_caso.json").write_text(json.dumps(FICHA_ESC), encoding="utf-8")
        try:
            ma.generate_escaleta(topic, call=call, persist=False)
        except RuntimeError:
            pass
    assert "FICHA DEL CASO" not in seen[0] and "FICHA DEL CASO" in seen[1]


# ═══════════════════════════════════════════════════════════════
#  Guion v4 (§1.3)
# ═══════════════════════════════════════════════════════════════

def test_data_line_con_y_sin_ficha():
    its = g4.ev.items(POOL11)
    esc = _esc_ok()
    sin = g4.data_line("D4", its, esc, POOL11)
    con = g4.data_line("D4", its, esc, POOL11, {"D4": "El portón número 4 seguía cerrado con llave."})
    assert sin.startswith("[D4] ") and con.startswith("[D4] El portón número 4 seguía cerrado con llave.")
    assert g4.data_line("D4", its, esc, POOL11, {"D99": "x"}) == sin                  # id fuera de la ficha: el pool
    q = g4.data_line("Q1", its, esc, POOL11, {"Q1": "«nadie nos abrió» — Liz Torres"})
    assert q.startswith("[Q1] CITA «nadie nos abrió» — Liz Torres")


def test_prompt_v4_sin_ficha_igual_y_con_ficha_usa_la_ficha():
    esc = _esc_ok()
    assert g4.prompt(TOPIC11, esc, "abierto", None) == g4.prompt(TOPIC11, esc, "abierto")
    f = _ficha(hechos=[{"texto": "TEXTO-DE-LA-FICHA", "ids": [esc["beats"][0]["dato_central"]]}])
    assert "TEXTO-DE-LA-FICHA" in g4.prompt(TOPIC11, esc, "abierto", f)
