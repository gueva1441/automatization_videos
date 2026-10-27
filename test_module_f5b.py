"""F5b (VALIDACION_F5): narración N1–N5 y pantalla S1–S6. Sin red."""
from __future__ import annotations

import json

from researcher_steps import evidence_pool as ep
from script_engine import evidence as ev
from script_engine import gfx_pool as gp
from script_engine import m05_narrative as mn
from script_engine.gfx_icons import ICON_WHITELIST
from script_engine.gfx_project import GfxScene

MISTERIO = """=== HALLAZGOS ===

[DATOS DUROS]
- Reclusos no contabilizados: Según un informe de Human Rights Watch, más de 500 prisioneros no figuraban en la lista.
- Fenómenos paranormales reportados: En una antigua cárcel de Nueva Orleans construida en 1902, ahora una posada, se reportan espíritus. Un médium psíquico ha detectado la energía de personas que trabajaron allí.

[FUENTES CONSULTADAS]
- Human Rights Watch, 2005, "New Orleans: Prisoners Abandoned to Floodwaters"

[OBSERVACIONES DEL INVESTIGADOR]
La falta de registros en Nueva Orleans sugiere un encubrimiento.

Desde una perspectiva paranormal, aunque no directamente relacionado con los eventos de Katrina, la existencia de informes sobre actividad espiritual en otras antiguas instalaciones carcelarias añade misterio. Si bien los testimonios de fantasmas en la "Inn at the Old Jail" no prueban nada sobre lo ocurrido, reflejan una creencia en la energía residual."""

HUMANO = """[DATOS DUROS]
- Ronnie L. Morgan, Jr., un recluso, presentó una demanda federal contra el Sheriff Marlin Gusman y el alcaide Cornel Hubert del Elayn Hunt Correctional Center.
- El Teniente General Carl Strock del Cuerpo de Ingenieros del Ejército de EE. UU. testifica ante el Senado.
[CRONOLOGÍA]
- 2005-08-27: Robie Waganfeald y Paul Kunkel Jr. son arrestados en Bourbon Street. Raphael Schwarz es arrestado por intoxicación pública."""


# ═══════════════════════════════ N1 relevancia ═══════════════════════════════

def test_n1_fuera_lo_que_el_bloque_marca_como_no_relacionado():
    raw = {"datos": [{"texto": "antigua cárcel de Nueva Orleans construida en 1902", "tipo": "fecha", "valor": "1902"},
                     {"texto": "Un médium psíquico ha detectado la energía de personas que trabajaron allí",
                      "tipo": "nombre", "valor": "médium psíquico"},
                     {"texto": "más de 500 prisioneros no figuraban en la lista", "tipo": "cifra", "valor": "500"}],
           "cronologia": [], "citas": [], "personajes": [],
           "lugares": [{"nombre": "Inn at the Old Jail", "rol": "posada"}, {"nombre": "Nueva Orleans", "rol": "Ciudad"}]}
    out = ep.validate_block(raw, "misterio", MISTERIO, [])
    assert [d["valor"] for d in out["datos"]] == ["500"]                         # 1902 y el médium, fuera
    assert [p["nombre"] for p in out["lugares"]] == ["Nueva Orleans"]            # está en todo el bloque: se queda
    assert {d["texto"][:12] for d in out["_descartados"]} == {"antigua cárc", "Un médium ps", "Inn at the O"}
    assert out["lugares"][0]["rol"] == "ciudad"                                   # N5: rol en minúscula
    assert ep.unrelated_lines("[DATOS DUROS]\n- 517 reclusos no estaban contabilizados.") == []


# ═══════════════════════════════ N5 nombres con acción ═══════════════════════════════

def test_n5_un_nombre_entra_solo_si_hace_algo():
    blocks = [HUMANO]
    assert ep.person_acts("Ronnie L. Morgan, Jr.", blocks)                       # «…, un recluso, presentó»
    assert ep.person_acts("Carl Strock", blocks)                                 # «… del Cuerpo de … testifica»
    assert ep.person_acts("Robie Waganfeald", [HUMANO + " Robie Waganfeald y Paul Kunkel Jr., dos turistas, recibieron "
                                               "una indemnización."])
    assert not ep.person_acts("Raphael Schwarz", blocks)                         # «es arrestado»: pasiva
    assert not ep.person_acts("Cornel Hubert", blocks)                           # demandado, no hace nada
    assert ep.person_acts("Marlin Gusman", blocks, [{"texto": "x", "autor": "Sheriff Gusman"}])   # autor de una cita
    pool = {"personajes": [{"id": "P01", "nombre": "Raphael Schwarz", "rol": "arrestado", "antagonista": False},
                           {"id": "P02", "nombre": "William Hunter", "rol": "adjunto", "antagonista": True}],
            "datos": [{"id": "D01", "texto": "Raphael Schwarz", "tipo": "nombre"}], "citas": []}
    ep.acting_filter(pool, blocks, [])
    assert [p["nombre"] for p in pool["personajes"]] == ["William Hunter"] and pool["datos"] == []
    assert mn.silent_names("Casos como el de Raphael Schwarz.", pool) == ["Raphael Schwarz"]


def test_n5_mayusculas_pegadas():
    assert ep.fix_caps("Población carcelaria: Aproximadamente 6,375 personas") == \
        "Población carcelaria: aproximadamente 6,375 personas"
    assert ep.fix_caps("Institución: Prisión Parroquial de Orleans") == "Institución: Prisión Parroquial de Orleans"
    assert ep.fix_caps("Evento principal: Huracán Katrina.") == "Evento principal: huracán Katrina."
    assert ep.fix_caps("El Sheriff Gusman reabrió el edificio") == "El sheriff Gusman reabrió el edificio"
    # F21: solo palabras de rol del pool (o tratamientos), no la lista fija de Orleans
    pool = {"personajes": [{"nombre": "Raphael Schwarz", "rol": "Arrestado por intoxicación pública"}]}
    assert ev.fix_glued_caps("Casos como el de Raphael Schwarz, Arrestado por intoxicación.", pool) == \
        "Casos como el de Raphael Schwarz, arrestado por intoxicación."
    assert ev.fix_glued_caps("Casos como el de Raphael Schwarz, Arrestado por intoxicación.") == \
        "Casos como el de Raphael Schwarz, Arrestado por intoxicación."      # sin pool: no hay roles que bajar
    assert ev.fix_glued_caps('Arrestado el lunes. Dijo: "Turistas de Ohio".') == 'Arrestado el lunes. Dijo: "Turistas de Ohio".'


# ═══════════════════════════════ N2 por id · N3 una vez · N4 piso ═══════════════════════════════

POOL = {"datos": [{"id": "D01", "texto": "En la prisión había niños de hasta 10 años", "tipo": "cifra", "valor": "10"},
                  {"id": "D02", "texto": "La evacuación no se completó hasta el viernes 2 de septiembre", "tipo": "fecha",
                   "valor": "2 de septiembre", "fecha": "2005-09-02"}],
        "cronologia": [{"id": "T01", "fecha": "2005-08-30",
                        "evento": "Comienza la evacuación cuando el agua alcanza el nivel del pecho en el interior"}],
        "citas": [], "lugares": [], "personajes": []}
I10 = "Los llevaron al paso elevado de la Interestatal 10, bajo un sol pesado y húmedo."


def test_n2_metricas_por_id_declarado():
    assert mn.used_items(I10, POOL) == ["D01"]                                   # regex: «10» de la I-10 = los niños
    assert mn.used_items(I10, POOL, declared=[]) == []                           # por id: no lo declaró → no cuenta
    assert mn.used_items("Había niños de hasta 10 años.", POOL, declared=["D01"]) == ["D01"]
    m = mn.video_metrics([{"narration": I10, "datos_usados": []}], POOL)
    assert m["caps"][0]["conteo"] == "por_id" and m["caps"][0]["densidad"] == 0 and m["caps"][0]["densidad_regex"] > 0
    assert mn.video_metrics([I10], POOL)["caps"][0]["conteo"] == "regex"          # v1 sin declaración: como F5
    probs = mn.cap_problems(I10, cap=1, pool=POOL, skeleton={"chapters": []}, previous=[], declared=["D02"])
    assert any("no están LITERALES" in p for p in probs)


def test_n3_cada_dato_una_vez_por_cap():
    t = ("El 30 de agosto el agua alcanzó el nivel del pecho. A la tarde, el nivel del pecho era la línea. "
         "Esa noche seguía el nivel del pecho. El 30 de agosto no terminó. La evacuación no se completó hasta el 2 de "
         "septiembre.")
    reps = dict(ev.repeats_in_cap(t, ["T01", "D02"], POOL))
    assert reps.get("nivel del pecho") == 3 and reps.get("30 de agosto") == 2
    probs = " ".join(mn.cap_problems(t, cap=1, pool=POOL, skeleton={"chapters": []}, previous=[],
                                     declared=["T01", "D02"]))
    assert "UNA vez por cap" in probs and "«nivel del pecho» ×3" in probs
    assert ev.count_in("2 de septiembre", "el 2 de septiembre y el dos de septiembre") == 2


def test_n4_piso_y_techo_de_adjetivos():
    assert (mn.ADJ_MIN, mn.ADJ_MAX) == (2.0, 4.0)
    acta = "Los reclusos fueron sacados en botes. Se les llevó al paso elevado. Luego los subieron a autobuses. " * 3
    assert any("se lee como un acta" in p for p in mn.cap_problems(acta, cap=1, pool=POOL, skeleton={"chapters": []},
                                                                   previous=[], declared=[]))


# ═══════════════════════════════ S1 cláusula completa ═══════════════════════════════

def test_s1_recorte_es_clausula_completa_nunca_una_cola():
    o = gp.pool_clause_options
    assert o("Las celdas del primer piso comienzan a inundarse y las aguas residuales refluyen.") == \
        ["Las celdas del primer piso comienzan a inundarse", "las aguas residuales refluyen"]
    t = ("Un jurado federal otorga más de $650,000 a dos turistas de Ohio que fueron encarcelados por ebriedad en la "
         "vía pública antes de Katrina y retenidos durante más de un mes en las caóticas secuelas.")
    assert o(t) == ["Un jurado federal otorga más de $650,000"]                  # no «federal otorga…»
    assert o("La evacuación completa de la prisión no finalizó hasta el viernes 2 de septiembre de 2005.") == []
    assert o("Robie Waganfeald y Paul Kunkel Jr. son arrestados en Bourbon Street por presunta intoxicación pública.") \
        == ["Robie Waganfeald y Paul Kunkel Jr. son arrestados"]                 # sujeto coordinado: uno
    assert o("El recluso Ronnie L. Morgan, Jr. presenta una demanda federal por violación de sus derechos civiles.") \
        == ["El recluso Ronnie L. Morgan, Jr. presenta una demanda federal"]
    assert o("La Prisión de Orleans Parish (OPP) albergaba a 6,375 reclusos el 29 de agosto de 2005") == \
        ["La Prisión de Orleans Parish (OPP) albergaba a 6,375 reclusos"]
    assert "toca tierra en Nueva Orleans" not in o("El huracán Katrina, un huracán de categoría 3, toca tierra en "
                                                   "Nueva Orleans.")                     # predicado sin sujeto
    for opts in (o(t), o("Comienza la evacuación de algunos edificios de la prisión (Templeman 1 y 2) cuando el agua "
                         "alcanza el nivel del pecho en el interior.")):
        assert all(x.split()[-1].lower() not in {"de", "a", "en", "que", "y"} for x in opts)


# ═══════════════════════════════ S5 unidades métricas ═══════════════════════════════


# ═══════════════════════════════ S2 cronología · S3 hecho ═══════════════════════════════

PP = {"datos": [{"id": "D01", "texto": "Un jurado federal otorga más de $650,000 a dos turistas de Ohio", "tipo": "cifra",
                 "valor": "650,000", "fecha": "2010-10-14"},
                {"id": "D02", "texto": "más de 650,000 dólares", "tipo": "cifra", "valor": "650,000"}],
      "cronologia": [{"id": "T01", "fecha": "2005-08-28",
                      "evento": "El sheriff anuncia que los prisioneros no serán evacuados de la prisión"},
                     {"id": "T02", "fecha": "2005-08-29", "hora": "medianoche",
                      "evento": "A la medianoche, el sheriff Marlin Gusman solicita ayuda para la evacuación de los "
                                "prisioneros"}],
      "citas": [], "lugares": [], "personajes": []}


def W(text: str, step: float = 0.4) -> list[dict]:
    return [{"word": w, "start": round(k * step, 3), "end": round(k * step + 0.3, 3)} for k, w in enumerate(text.split())]


def test_s3_mismo_hecho_y_nunca_del_cap_siguiente():
    its = ev.items(PP)
    assert ev.same_fact(its["D01"], its["D02"])                                  # misma cifra grande: un hecho
    assert not ev.same_fact(its["T01"], its["T02"])
    skel = {"chapters": [{"chapter_number": 2, "evidence_ids": ["T01"]}, {"chapter_number": 3, "evidence_ids": ["T02"]},
                         {"chapter_number": 1, "evidence_ids": ["D02"]}]}
    assert gp.cap_candidates(PP, skel, 2, set()) == ["T01", "D02"]               # el suyo y el del cap 1; nunca el 3
    assert gp.cap_candidates(PP, {"chapters": [{"chapter_number": 5, "evidence_ids": ["D01"]}]}, 5, {"D02"}) == []


# ═══════════════════════════════ S4 ícono literal ═══════════════════════════════

def test_s4_icono_solo_por_mapa_literal():
    moods = {"encierro": {"icon_words": {"celdas": "candado", "encierro": "candado"}},
             "agua": {"icon_words": {"agua": "gota", "inundación": "gota"}}}
    cel = {"texto": "x", "tipo": "fecha"}
    assert gp.content_icon(cel, ICON_WHITELIST, moods, "Las celdas del primer piso") == ("candado", None)
    assert gp.content_icon(cel, ICON_WHITELIST, moods, "el agua alcanza el nivel del pecho") == (None, None)  # agua sola
    assert gp.content_icon(cel, ICON_WHITELIST, moods, "una penumbra sofocante") == (None, None)
    assert gp.content_icon(cel, ICON_WHITELIST, moods, "la inundación del 80 %") == ("gota", None)
    assert gp.content_icon(cel, ICON_WHITELIST, moods, "Los generadores de la prisión fallan") == ("rayo_tachado", None)
    assert gp.content_icon(cel, ICON_WHITELIST - {"espiral"} if isinstance(ICON_WHITELIST, set) else
                           {k: v for k, v in ICON_WHITELIST.items() if k != "espiral"}, moods,
                           "El huracán Katrina toca tierra") == (None, "espiral")   # sin la clave: se anota


# ═══════════════════════════════ S6 / §1.6 ubicaciones en el canon ═══════════════════════════════

def test_s6_ubicaciones_documentadas_solo_con_pool():
    from script_engine import m03_visual as m3
    pool = {"lugares": [{"nombre": "CYC", "rol": "Instalación juvenil"}, {"nombre": "Broad Street", "rol": "Paso elevado"},
                        {"nombre": "Interestatal 10", "rol": "Carretera"}],
            "datos": [{"texto": "Los prisioneros fueron llevados en bote al paso elevado de Broad Street sobre la "
                                "Interestatal 10.", "tipo": "lugar", "valor": "Broad Street"},
                      {"texto": "Prisioneras llegan a la Penitenciaría Estatal de Luisiana (Angola).", "tipo": "lugar",
                       "valor": "Penitenciaría Estatal de Luisiana (Angola)"}],
            "cronologia": [], "personajes": []}
    blk = m3._format_documented_locations({"evidence_pool": pool})
    assert blk.startswith("UBICACIONES DOCUMENTADAS (no mezclar en una misma escena):")
    assert "- Menores detenidos → CYC (instalación juvenil); separados de los adultos." in blk
    assert "- Mujeres → Penitenciaría Estatal de Luisiana (Angola); nunca en la misma celda que hombres." in blk
    assert "- Evacuados → paso elevado de Broad Street sobre la Interestatal 10." in blk
    topic = {"era_visual_canon": {}, "documented_people": [], "documented_props": []}
    plain = m3._format_seedream_canon_block(topic)
    assert "UBICACIONES" not in plain and plain == m3._format_seedream_canon_block({**topic, "evidence_pool": None})
    assert "UBICACIONES DOCUMENTADAS" in m3._format_seedream_canon_block({**topic, "evidence_pool": pool})


def test_narrador_declara_ids_y_corrige_mayusculas(monkeypatch):
    import script_engine.m01b_narrator as nb
    base = "Los guardias contaron a los presos en el patio de la cárcel una vez más. "
    good = (base * 5 + "El patio estaba húmedo, sucio y oscuro, el aire pesado. " + base * 5
            + "En la prisión había niños de hasta 10 años, dijo un Recluso, Arrestado el lunes. Nadie los contó.").strip()
    sk = {"chapters": [{"chapter_number": 2, "evidence_ids": ["D01"], "cliffhanger": None}], "personajes": []}
    monkeypatch.setattr(nb, "call_flash_json", lambda p, response_schema=None: (
        json.dumps(response_schema) and {"narration": good, "datos_usados": ["[D01]"]}))
    declared: dict = {}
    out = nb._call_with_length_retry("P", role="development", cap_number=2, max_attempts=3,
                                     f5={"pool": {**POOL, "personajes": [*(POOL.get("personajes") or []),
                                                                        {"id": "P99", "nombre": "Ana Paz",
                                                                         "rol": "recluso arrestado"}]},
                                         "skeleton": sk, "previous": []}, violations={}, declared=declared)
    assert declared == {2: ["D01"]} and ", arrestado el lunes" in out
    assert "datos_usados" in nb._narration_schema(with_ids=True)["required"]
    assert nb._narration_schema() == {"type": "OBJECT", "properties": {"narration": {"type": "STRING"}},
                                      "required": ["narration"]}            # sin pool: igual que antes
