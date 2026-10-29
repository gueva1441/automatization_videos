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

# A.1 + chascada (analista, 2026-10-29): desde «La promesa es una sola oración…» hasta «…lo que no cierra.» → una
# oración sobre la promesa; B.1: + una oración sobre los loops (formato de salida)
VIEJO_P = ("La promesa es una sola oración que deja una imagen sin cerrar o una pregunta que el espectador no puede "
           "responder todavía. No cuenta lo que va a pasar, no enumera lo que viene, no nombra juicios, comisiones ni "
           "consecuencias. Probala así: si la oración se puede leer como un resumen de lo que viene («nadie lo sabrá "
           "durante años», «terminará en un juicio»), no es una promesa; es un adelanto. Volvé a escribirla con lo que "
           "se ve o lo que no cierra.")
NUEVO_P = ("La promesa dice qué va a entender el espectador si se queda: puede nombrar lo que está en juego, con años "
           "o cifras si hacen falta; no es un índice de lo que viene. Declará 1–2 loops: la pregunta que el video deja "
           "abierta, en qué beat se abre y en qué beat se paga. Cada beat dice qué pregunta anterior paga (o ninguna).")


def test_escaleta_f54_1_literal_y_un_solo_cambio():
    assert me.SYSTEM_V2 == _sistema(F54 / "PROMPT_ESCALETA_f54_1.md") and me.PROMPT_VERSION_V2 == "f54-1"
    assert me.PROMPT_VERSION_COLUMNA == "f54-1" and me.PROMPT_VERSION_V2_F26_1 == "f26-1"
    assert _md5(me.SYSTEM_V2_F26_1) == "2e67791cedbfa7492f8b6de1268b7b30"
    (viejo, nuevo), = _dif(me.SYSTEM_V2_F26_1, me.SYSTEM_V2)
    assert VIEJO_P in viejo and viejo.replace(VIEJO_P, NUEVO_P) == nuevo
    assert "Sin contexto, sin año, sin cifras: lo que se ve." in nuevo          # R1 (la imagen del gancho) se queda
    assert nuevo.count("La promesa") == 1                                      # chascada: una sola oración sobre la promesa


def test_guion_v5_6_literal_y_solo_cambia_ejemplos():
    # B.2 (OK del analista 2026-10-29 18:30): el v5.6 = v5.5 con el bloque <ejemplos> de EJEMPLOS_v5_6_propuesta.md
    assert g4.system() == g4.SYSTEM_V5_6 == _sistema(F54 / "PROMPT_GUIONISTA_v5_6.md") and g4.PROMPT_VERSION == "f54-2"
    ej = (F54 / "EJEMPLOS_v5_6_propuesta.md").read_text(encoding="utf-8").split("```text", 1)[1]
    bloque = ej[ej.index("<ejemplos>"):ej.index("</ejemplos>") + len("</ejemplos>")]
    assert bloque in g4.SYSTEM_V5_6 and "Tres de ellas no van a ver la primavera." in bloque
    v55 = g4.SYSTEM_V5_5
    viejo = v55[v55.index("<ejemplos>"):v55.index("</ejemplos>") + len("</ejemplos>")]
    assert g4.SYSTEM_V5_6.replace(bloque, viejo) == v55 and viejo not in g4.SYSTEM_V5_6
    assert g4.VERSIONES_V5[:3] == ("f54-2", "f54-1", "f25-1") and g4.prompt_version(version="f54-1") == "f54-1"


def test_guion_v5_5_literal_y_dos_cambios():
    assert g4.system("f54-1") == g4.SYSTEM_V5_5 == _sistema(F54 / "PROMPT_GUIONISTA_v5_5.md") and g4.PROMPT_VERSION_V5_5 == "f54-1"
    assert g4.system("f25-1") == g4.SYSTEM_V5_4 and _md5(g4.SYSTEM_V5_4) == "2f66c1e07e4d6c31178091371821c0c9"
    dif = _dif(g4.SYSTEM_V5_4, g4.SYSTEM_V5_5)
    assert len(dif) == 2
    (v1, n1), (v2, n2) = dif
    assert v1.replace("Segunda: la promesa, como viene en la escaleta, sin agregarle lo que va a pasar después.",
                      "Segunda: la promesa: lo que está en juego, con tus palabras, sin índice de lo que viene.") == n1
    assert "Primera frase: lo que se ve, sin año, sin cifra, sin institución." in n1
    assert v2.replace("cada uno avanza la historia y termina con algo sin resolver que el siguiente paga.",
                      "cada uno avanza la historia. La primera frase de cada cap paga lo que el beat marcado `paga` dejó "
                      "abierto; la escaleta dice cuál.") == n2                   # B.3: reemplaza, no suma
    assert g4.prompt_version(version="f25-1") == "f25-1"


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
#  B.1: loops, paga, recuerda_loop en el esquema y en el validador (DECISIONES 2026-10-29 16:05)
# ═══════════════════════════════════════════════════════════════

def _good():
    import test_module_f6b as t6
    return t6.good(), t6.POOL


def _hard(mut):
    e, pool = _good()
    mut(e)
    return me.validate(e, pool)[1]


def test_esquema_con_loops_paga_y_recuerda_loop():
    for s in (me.SCHEMA, me.SCHEMA_FICHA):
        lp = s["properties"]["loops"]["items"]
        assert set(lp["required"]) == {"id", "pregunta", "abre_beat", "paga_beat"}
        assert "loops" in s["required"] and "recuerda_loop" not in s["required"]
        assert s["properties"]["recuerda_loop"]["required"] == ["beat", "oracion"]
        assert s["properties"]["beats"]["items"]["properties"]["paga"]["type"] == "INTEGER"
        assert "paga" not in s["properties"]["beats"]["items"]["required"]
    assert me.LOOPS_RANGO == (1, 2) and me.RECUERDA_LOOP_CAP == 3


def test_escaleta_con_un_loop_pasa_y_normaliza(monkeypatch):
    monkeypatch.setattr(me, "MIN_BEATS_DEV_CAP", 1)
    e, pool = _good()
    e["beats"][3]["paga"] = 0                                           # 0 = ninguna
    esc, hard, _, _ = me.validate(e, pool)
    assert hard == []
    assert esc["loops"] == [{"id": "L1", "pregunta": "¿cuántos eran?", "abre_beat": 1, "paga_beat": 8}]
    assert esc["beats"][-1]["paga"] == 1 and esc["beats"][3]["paga"] is None and esc["recuerda_loop"] is None


@pytest.mark.parametrize("nombre, mut, frag", [
    ("sin loop → hard, sin fabricar", lambda e: e.update(loops=[]), "loops: 0 declarado(s)"),
    ("más de 2 loops", lambda e: e.update(loops=e["loops"] * 3), "loops: 3 declarado(s)"),
    ("se paga antes de abrirse", lambda e: e["loops"][0].update(abre_beat=5, paga_beat=3), "pagarse después de abrirse"),
    ("el principal fuera del cap 7 y del pico", lambda e: e["loops"][0].update(paga_beat=5), "cap 7 o en el pico"),
    ("beat inexistente", lambda e: e["loops"][0].update(paga_beat=40), "no es un beat"),
    ("sin pregunta", lambda e: e["loops"][0].update(pregunta=""), "sin pregunta"),
    ("paga hacia adelante", lambda e: e["beats"][2].update(paga=5), "beat 3: paga 5 tiene que apuntar a un beat anterior"),
    ("recuerda_loop fuera del cierre del cap 3", lambda e: e.update(recuerda_loop={"beat": 2, "oracion": "x"}),
     "recuerda_loop: va en el último beat del cap 3 (beat 3)"),
    ("recuerda_loop sin oración", lambda e: e.update(recuerda_loop={"beat": 3, "oracion": ""}), "recuerda_loop"),
])
def test_loops_rechazos_duros_y_son_bloqueantes(nombre, mut, frag):
    hard = _hard(mut)
    hit = [h for h in hard if frag in h]
    assert hit, (nombre, hard)
    assert all(me.bloqueante_de(h) for h in hit), (nombre, hit)


def test_loop_principal_pagado_en_el_pico_pasa():
    assert not [h for h in _hard(lambda e: e["loops"][0].update(paga_beat=6)) if h.startswith("loop")]


def test_recuerda_loop_en_el_cierre_del_cap_3_pasa():
    e, pool = _good()
    e["recuerda_loop"] = {"beat": 3, "oracion": "El polvo seguía ahí."}
    esc, hard, _, _ = me.validate(e, pool)
    assert not [h for h in hard if "recuerda_loop" in h] and esc["recuerda_loop"]["beat"] == 3


def test_segundo_loop_no_exige_cap_7_ni_pico():
    e, pool = _good()
    e["loops"].append({"id": "L2", "pregunta": "¿quién apagó la luz?", "abre_beat": 2, "paga_beat": 4})
    assert not [h for h in me.validate(e, pool)[1] if h.startswith("loop")]


def test_metricas_escaleta_traen_loops():
    import test_module_f16 as t16
    e = t16.good()
    e["recuerda_loop"] = {"beat": 3, "oracion": "El polvo seguía ahí."}
    esc = me.validate(e, t16.POOL)[0]
    m = me.metricas_escaleta(esc, t16.POOL, t16.FICHA, [])
    assert m["loops"] == esc["loops"] and m["beats_con_paga"] == {8: 1} and m["recuerda_loop"]["beat"] == 3


# ═══════════════════════════════════════════════════════════════
#  B.3: la escaleta que ve el guionista dice qué paga; bloqueante (h) pago no dicho
# ═══════════════════════════════════════════════════════════════

def test_escaleta_section_muestra_paga_loops_y_recuerda():
    import test_module_f11 as t11
    esc = t11._esc_ok()
    esc["beats"][5]["paga"] = 2                                       # beat 6 (cap 4) paga la pregunta del beat 2
    esc["loops"] = [{"id": "L1", "pregunta": "¿quién cerró el portón?", "abre_beat": 1, "paga_beat": 12}]
    esc["recuerda_loop"] = {"beat": 5, "oracion": "El portón seguía cerrado."}
    sec = g4.escaleta_section_v5(esc, t11.POOL)
    assert "    paga: la pregunta del beat 2 («¿quién cerró?»)" in sec
    assert "    recuerda el loop: El portón seguía cerrado." in sec
    assert "LOOP 1: ¿quién cerró el portón? — se abre en el beat 1, se paga en el beat 12\n" in g4.prompt_v5(t11.TOPIC, esc)
    esc.pop("loops"); esc.pop("recuerda_loop")
    assert "LOOP" not in g4.prompt_v5(t11.TOPIC, esc)                  # sin loops (escaletas viejas): nada


def test_pago_no_dicho_frena_y_dicho_pasa():
    t11, esc = _fixture()
    esc["beats"][5]["paga"] = 2                                       # beat 6, cap 4, dato central D6
    esc["loops"] = [{"id": "L1", "pregunta": "¿quién cerró?", "abre_beat": 1, "paga_beat": 10}]   # beat 10, cap 6, D10
    ps = t11._parrafos(esc)
    assert not [x for x in g4.bloqueantes(t11.TOPIC, esc, ps) if x["codigo"] == "h"]
    ps[5]["texto"] = t11.FRASE + "Nadie volvió a abrir."             # el cap 4 ya no dice D6
    ps[9]["texto"] = t11.FRASE + "Nadie volvió a abrir."             # el cap 6 ya no dice D10
    h = sorted((x["beat"], x["cap"]) for x in g4.bloqueantes(t11.TOPIC, esc, ps) if x["codigo"] == "h")
    assert h == [(6, 4), (10, 6)]
    m = [x["motivo"] for x in g4.bloqueantes(t11.TOPIC, esc, ps) if x["codigo"] == "h"]
    assert any("la pregunta del beat 2 con D6" in x for x in m) and any("el loop L1 con D10" in x for x in m)


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


# ═══════════════════════════════════════════════════════════════
#  B.4: el hero y la metadata reciben el GANCHO (cap 1 entero) primero
# ═══════════════════════════════════════════════════════════════

def test_m09_gancho_primero_y_cap_1_sin_truncar():
    from script_engine import m09_packaging as m9
    cap1 = "Un hombre joven posa con el pie vendado. " * 60                    # > HERO_NARRATION_PER_CAP
    canonical = {"video_title": "W", "canonical_subject_description": "s", "verified_facts": [{"fact": "f"}],
                 "chapters": [{"chapter_number": 1, "narration": cap1},
                              {"chapter_number": 7, "narration": "Z" * 2000}]}
    for u in (m9._hero_user_prompt(canonical), m9._meta_user_prompt(canonical)):
        assert u.startswith("GANCHO (la narración del cap 1 entera; " + m9.GANCHO_INSTRUCCION + "):\n" + cap1.strip())
        assert "la primera oración del título y el sujeto de la miniatura salen del GANCHO" in u
    hero = m9._hero_user_prompt(canonical)
    assert hero.count(cap1.strip()) == 2                                       # en el GANCHO y en [Cap 1], entero
    assert "[Cap 1] " + cap1.strip() in hero and "[Cap 7] " + "Z" * m9.HERO_NARRATION_PER_CAP + " […]" in hero
    assert m9._meta_user_prompt(canonical).count("NARRACIÓN COMPLETA") == 1
