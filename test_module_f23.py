"""
test_module_f23.py — F23 (familias D + G + H + I de la auditoría): el tiempo del caso (perfil con rango y tipo, descarte
solo hacia atrás, fechas de año/mes/día, paráfrasis solo en casos puntuales), los umbrales de Orleans a medida (rojo solo
sin con qué contar, el amarillo no acorta, pisos bajos, oficial por defecto), el intent de cada cap desde la escaleta,
los rangos como valor válido, los idiomas del caso y los dos prompts (guion v5.3, ficha v2.2) literales. Sin red.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import pytest

from researcher_steps import ficha_caso as fc
from researcher_steps import pool_gate as pg
from researcher_steps import research_v3 as r3
from script_engine import evidence as ev
from script_engine import guion_v4 as g4
from script_engine import m01a_columna as mc
from script_engine import m01a_escaleta as me

ROOT = Path(__file__).resolve().parent
F23 = ROOT / "lab" / "hyperframes" / "f23"
STEPS = ROOT / "data" / "scripts" / "_steps"


def _md5(s: str) -> str:
    return hashlib.md5(s.encode("utf-8")).hexdigest()


def _sistema(name: str) -> str:
    md = (F23 / name).read_text(encoding="utf-8").replace("\r\n", "\n")
    i = md.index("\n## SISTEMA\n\n") + len("\n## SISTEMA\n\n")
    return md[i:md.index("\n\n---\n", i)]


@pytest.fixture
def sin_perfil():
    r3.set_vocabulario(None)
    yield
    r3.set_vocabulario(None)


# ═══════════════════════════════════════════════════════════════
#  §1.1 el tiempo del caso
# ═══════════════════════════════════════════════════════════════

def test_perfil_con_rango_y_tipo_y_fallback():
    assert r3.tiempo_del_perfil({"anio_inicio": 1949, "anio_fin": 1997, "tipo_evento": "prolongado"}) == {
        "anio_inicio": 1949, "anio_fin": 1997, "tipo_evento": "prolongado"}
    assert r3.tiempo_del_perfil({"anio_evento": 2004}) == {"anio_inicio": 2004, "anio_fin": 2004, "tipo_evento": None}
    assert r3.tiempo_del_perfil({"anio_inicio": 1960, "anio_fin": 1950})["anio_fin"] == 1960
    props = r3.PROFILE_SCHEMA["properties"]
    assert {"anio_inicio", "anio_fin", "tipo_evento", "cobertura_ingles"} <= set(props)
    assert props["tipo_evento"]["enum"] == ["puntual", "prolongado"]


def test_seed_profile_llena_el_tiempo_y_los_idiomas():
    raw = {"anio_evento": 1957, "anio_inicio": 1949, "anio_fin": 1997, "tipo_evento": "prolongado",
           "cobertura_ingles": True, "lugar_principal": "Mayak", "idioma_local": "ruso (Ozyorsk, URSS)",
           "nombres_lugar": ["Mayak", "Kyshtym disaster"], "nombres_locales": ["Маяк"]}
    p = r3.seed_profile({"seed_title": "Kyshtym"}, call=lambda *a, **k: raw)
    assert (p["anio_evento"], p["anio_inicio"], p["anio_fin"], p["tipo_evento"]) == (1949, 1949, 1997, "prolongado")
    assert p["idiomas_research"] == ["ruso", "inglés", "español"]
    raw2 = {**raw, "cobertura_ingles": False, "idioma_local": "español (Asunción)", "anio_inicio": 2004,
            "anio_fin": 2004, "tipo_evento": "puntual"}
    assert r3.seed_profile({"seed_title": "Ycuá"}, call=lambda *a, **k: raw2)["idiomas_research"] == ["español"]


def test_descarte_por_anio_solo_hacia_atras():
    assert r3.contamination({"fecha": "1930"}, 1957)
    assert r3.contamination({"fecha": "1997-06"}, 1957) is None
    assert r3.contamination({"fecha": "2019-04-01", "texto": "una muestra de fotos"}, 1957) is None   # nada posterior
    assert not hasattr(r3, "LATE_OK") and not hasattr(r3, "EARLY_OK")                               # sin listas


def test_presente_en_evento_con_el_rango():
    pool = {"personajes": [{"id": "P01", "nombre": "Ana Paz", "presente_en": ["T01"]}],
            "citas": [], "datos": [], "cronologia": [{"id": "T01", "fecha": "1976", "evento": "x"}]}
    r3.person_stats(pool, 1957, 1997)
    assert pool["personajes"][0]["presente_en_evento"] is True
    r3.person_stats(pool, 1957)
    assert pool["personajes"][0]["presente_en_evento"] is False


def test_run_seed_sin_anio_es_un_error(tmp_path, monkeypatch):
    (tmp_path / "_perfil.json").write_text(json.dumps({"anio_evento": 0, "nombres_lugar": [], "place_re": "x",
                                                       "roles_testigo": []}), encoding="utf-8")
    monkeypatch.setattr(r3, "discover_sources", lambda *a, **k: {"fuentes": []})
    monkeypatch.setattr(r3, "download_sources", lambda *a, **k: {"documentos": []})
    monkeypatch.setattr(r3, "refine_fichas", lambda *a, **k: None)
    (tmp_path / "fuentes").mkdir()
    with pytest.raises(ValueError, match="no tiene año"):
        r3.run_seed({"seed_title": "x"}, "t", tmp_path)


def test_r3_acepta_fechas_de_anio_y_la_cita_con_un_anio_de_diferencia():
    dt = r3.DocText("F01", "En 1957 explotó el tanque del complejo. Hacia 1958 se evacuaron las aldeas del valle.")
    raw = {"cronologia": [{"fecha": "1957", "evento": "Explota el tanque", "cita_literal": "En 1957 explotó el tanque"},
                          {"fecha": "1959", "evento": "Evacuación",
                           "cita_literal": "Hacia 1958 se evacuaron las aldeas del valle"},
                          {"fecha": "1962", "evento": "Otra", "cita_literal": "Hacia 1958 se evacuaron las aldeas del valle"}]}
    out = r3.validate_doc_items(raw, {"id": "F01", "titulo": "t"}, dt, [])
    assert [c["fecha"] for c in out["cronologia"]] == ["1957", "1959"]            # 1962 difiere en más de 1
    assert "fechas_presente`: las fechas (AAAA-MM-DD, AAAA-MM o AAAA)" in r3.build_extraction_prompt(
        {"seed_title": "x"}, {"titulo": "t"}, "texto", (1, 1))


def test_anios_desde_el_1000():
    assert ev._numbers("En 1902 hubo 40 heridos.") == ["40"]
    from script_engine.guion_v3_reglas import _YEAR
    assert _YEAR.search("Lisboa, 1755.") and _YEAR.search("2004")


def test_is_hard_y_used_in_con_mes_y_anio():
    mes = {"_kind": "cronologia", "id": "T01", "fecha": "1957-09", "evento": "La explosión del tanque en el complejo"}
    anio = {"_kind": "cronologia", "id": "T02", "fecha": "1976", "evento": "Medvedev publica el accidente en Londres"}
    assert ev.is_hard(mes) and ev.is_hard(anio)
    assert ev.used_in("En septiembre de 1957, la explosión del tanque sacudió el complejo.", mes)
    assert ev.used_in("En 1976, Medvedev publica el accidente en una revista de Londres.", anio)
    assert not ev.used_in("La explosión del tanque sacudió el complejo.", mes)


def test_compuerta_cuenta_mes_y_anio_si_es_prolongado():
    pool = {"cronologia": [{"fecha": "1957-09-29"}, {"fecha": "1957-10"}, {"fecha": "1976"}]}
    assert pg.measure(pool)["eventos_con_fecha"] == 2
    assert pg.measure({**pool, "_tiempo": {"tipo_evento": "prolongado"}})["eventos_con_fecha"] == 3


def test_replace_repeated_dates_puntual_y_prolongado():
    ps = [{"beat": 1, "cap": 2, "texto": "El 9 de octubre de 1963 cayó la montaña."},
          {"beat": 2, "cap": 3, "texto": "Del 9 de octubre quedaron los relojes parados. El 9 de octubre de 1964 hubo misa."}]
    out, ch = g4.replace_repeated_dates(ps, "1963-10-09", "puntual")
    assert out[1]["texto"].startswith("De ese miércoles quedaron")                      # Vajont 9/10/1963 → miércoles
    assert "El 9 de octubre de 1964 hubo misa" in out[1]["texto"]                      # otro año: no se toca
    assert g4.replace_repeated_dates(ps, "1963-10-09", "prolongado") == (ps, [])
    assert g4.replace_repeated_dates(ps, "1963-10", "puntual") == (ps, [])            # sin fecha completa, nada


def test_parafrasis_de_fecha_solo_en_casos_puntuales(sin_perfil):
    from script_engine.m05_narrative import _date_paraphrased
    it = {"_kind": "cronologia", "fecha": "1957-09-29", "evento": "La explosión del tanque"}
    texto = "Ese día, la explosión del tanque se oyó en todo el valle."
    assert _date_paraphrased(texto, it)                                                # sin perfil: como antes
    r3.set_vocabulario({"anio_inicio": 1949, "anio_fin": 1997, "tipo_evento": "prolongado"})
    assert not _date_paraphrased(texto, it)
    r3.set_vocabulario({"anio_inicio": 1957, "anio_fin": 1957, "tipo_evento": "puntual"})
    assert _date_paraphrased(texto, it)
    from script_engine.guion_v3_reglas import DATE_PARAPHRASE
    assert all(DATE_PARAPHRASE.search(x) for x in ("ese año", "ese invierno", "esa primavera", "ese mes"))


def test_fechas_literales_por_cap_es_metrica():
    from script_engine.guion_v3_reglas import date_problems, fechas_literales_por_cap
    caps = [{"chapter_number": 2, "narration": "El 29 de septiembre explotó. El 2 de octubre llegaron los soldados."}]
    assert date_problems(caps) == [] and fechas_literales_por_cap(caps) == {2: 2}
    import script_engine.guion_v3_reglas as gr
    assert not hasattr(gr, "replace_repeated_dates")


def test_m05_anio_por_defecto_del_perfil(sin_perfil):
    from script_engine.m05_narrative import date_problems
    pool = {"cronologia": []}
    frase = "El 29 de septiembre y el 3 de octubre fueron distintos."
    assert date_problems(frase, pool, []) == []                 # sin año ni perfil: ya no se inventa «2000»
    r3.set_vocabulario({"anio_inicio": 1957, "anio_fin": 1997, "tipo_evento": "prolongado"})
    assert date_problems(frase, pool, [])                       # con el inicio del caso del perfil, sí


# ═══════════════════════════════════════════════════════════════
#  §1.2 umbrales a medida
# ═══════════════════════════════════════════════════════════════

def _pool(datos: int, personas: int, eventos: int) -> dict:
    return {"_research_v3": {"documentos": []},
            "datos": [{"id": f"D{i:02d}", "texto": f"dato {i}"} for i in range(datos)],
            "citas": [], "lugares": [],
            "personajes": [{"id": f"P{i:02d}", "nombre": f"Ana Paz{chr(65 + i)}", "elegible_humano": False}
                           for i in range(personas)],
            "cronologia": [{"id": f"T{i:02d}", "fecha": f"1957-{i % 12 + 1:02d}", "evento": "e"} for i in range(eventos)]}


def test_compuerta_rojo_solo_sin_con_que_contar():
    y = pg.evaluate(_pool(45, 2, 3))
    assert y["color"] == pg.YELLOW and y["max_beats"] is None and y["target_words"] == 1500
    assert {f["metrica"] for f in y["faltan"]} == {"datos", "citas_verificadas", "elegibles_humano", "eventos_con_fecha"}
    r = pg.evaluate(_pool(30, 2, 3))
    assert r["color"] == pg.RED and r["motivos"] == [pg.ROJO["datos"][1]]
    assert pg.evaluate(_pool(45, 1, 3))["color"] == pg.RED
    assert pg.evaluate(_pool(45, 2, 2))["color"] == pg.RED


@pytest.mark.parametrize("ruta", ["lab/hyperframes/f7/00_pool_v3.json", "data/scripts/_steps/f8s1-ycua-bolanos/00_pool_v3.json"])
def test_orleans_e_ycua_siguen_verdes(ruta):
    p = ROOT / ruta
    if not p.exists():
        pytest.skip("sin el pool en disco")
    assert pg.evaluate(json.loads(p.read_text(encoding="utf-8")))["color"] == pg.GREEN


def test_amarillo_no_cambia_el_rango_de_beats(tmp_path, monkeypatch):
    monkeypatch.setattr(me, "STEPS_DIR", tmp_path)
    t = {"id": "t-y", "evidence_pool": _pool(45, 2, 3)}
    assert me.pool_gate_profile(t, t["evidence_pool"])["color"] == pg.YELLOW
    assert "_largo" not in t and me._profile(t)[1:3] == (me.MIN_BEATS, me.MAX_BEATS)


def test_pisos_de_research():
    assert r3.MIN_DOC_CHARS == 800 and r3.EVENT_CHECK_CHARS == 20_000 and r3.COUNT_MIN == 10
    assert r3.count_value("Murieron 327 personas en el incendio.") == ("327", 327)
    assert r3.count_value("было 10 700 эвакуированных") is None
    text = "x " * 30000 + " Mayak " + "y " * 30000
    out, why = r3.focus_text(text, "Mayak")
    assert out == text and "densidad baja" in why


def test_oficial_por_defecto_sin_documentos_oficiales(sin_perfil):
    docs = [{"id": "F01", "tipo": "academico", "url": "https://a.org/x", "prioridad": 1, "titulo": "A"},
            {"id": "F02", "tipo": "prensa_posterior", "url": "https://b.com/y", "prioridad": 2, "titulo": "B"}]
    assert r3.tipos_oficiales(docs) == (r3.OFICIAL_POR_DEFECTO, True)
    assert r3.tipos_oficiales(docs + [{"id": "F03", "tipo": "informe_oficial"}])[1] is False
    pool = {"datos": [{"id": "D01", "texto": "Murieron 327 personas.", "doc_id": "F01"},
                      {"id": "D02", "texto": "Murieron 330 personas.", "doc_id": "F02"}]}
    r3.canonical_v3(pool, docs, [])
    c = pool["cifras_canonicas"]
    assert c and c[0]["oficial"] == "D01" and c[0]["oficial_por_defecto"] is True


def test_bandas_de_caracteres_desde_video_length():
    from script_engine import m01d_particion as md
    from script_engine.video_length import char_band, get
    assert char_band("development") == (round(get("dev_words") * 6 * 0.5), round(get("dev_words") * 6 * 1.3))
    lo, hi = char_band("hook")
    assert md.len_range("hook") == (int(lo * 0.85), int(hi * 1.15))


def test_sin_robo_de_pantalla():
    import inspect

    from script_engine import m01a_skeleton as sk
    assert "donors" not in inspect.getsource(sk.assign_screen_ids)


# ═══════════════════════════════════════════════════════════════
#  §1.3 intent desde la escaleta, rangos
# ═══════════════════════════════════════════════════════════════

def test_intent_desde_los_beats():
    p = ROOT / "lab/hyperframes/f22d/escaleta_kyshtym_f22d.json"
    if not p.exists():
        pytest.skip("sin la escaleta de F22d")
    esc = json.loads(p.read_text(encoding="utf-8"))
    assert [me.intent_de_cap(esc, n) for n in range(1, 8)] == [
        "hook", "setup", "rising_tension", "rising_tension", "shock", "rising_tension", "outro"]
    assert [c["narrative_intent"] for c in me.caps_view(esc)["chapters"]] == [
        me.intent_de_cap(esc, n) for n in range(1, 8)]
    from script_engine.m01a_skeleton import DEFAULT_INTENT_BY_CAP
    assert [me.intent_de_cap({"beats": []}, n) for n in range(1, 8)] == [DEFAULT_INTENT_BY_CAP[n] for n in range(1, 8)]


def test_tts_pone_golpes_en_un_cap_2_rising():
    from script_engine.tts_tags import caps_tts
    esc = {"beats": [{"n": 1, "cap": 1, "funcion": "gancho", "intensidad": 4},
                     {"n": 2, "cap": 2, "funcion": "escalada", "intensidad": 4}], "pico": {"beat": 9}}
    ps = [{"beat": 2, "cap": 2, "texto": "El tanque se calienta día tras día sin que nadie lo repare. Nadie mira."}]
    caps = caps_tts(esc, ps, [{"chapter_number": 2, "narration": ps[0]["texto"]}])
    assert caps[0]["tts_tags"].get("[quietly]") == 1                                  # como «setup» no tenía golpes
    esc["beats"][1]["funcion"] = "planteo"
    caps = caps_tts(esc, ps, [{"chapter_number": 2, "narration": ps[0]["texto"]}])
    assert not caps[0]["tts_tags"].get("[quietly]")


def test_un_rango_es_un_valor_valido():
    pool = {"datos": [{"id": "D01", "tipo": "cifra", "texto": "Fueron evacuadas 10,000 personas de las aldeas."},
                      {"id": "D02", "tipo": "cifra", "texto": "Fueron evacuadas 10,500 personas, según otra fuente."},
                      {"id": "D03", "tipo": "cifra", "texto": "Entre 9,800 y 10,200 personas fueron evacuadas."}]}
    vs = me.count_variants(pool)
    assert vs and "D03" not in vs[0]["variantes"] and "D02" in vs[0]["variantes"]
    assert ev.es_rango("de 200 a 10.000 personas") and not ev.es_rango("327 personas")


# ═══════════════════════════════════════════════════════════════
#  §1.4 idiomas del caso
# ═══════════════════════════════════════════════════════════════

@pytest.mark.parametrize("texto, lang", [
    ("Это был взрыв на комбинате, и люди не знали, что делать.", "ru"),
    ("Der Unfall war nicht im Werk und die Arbeiter wurden nach Hause geschickt.", "de"),
    ("O acidente não foi na usina e os trabalhadores também não sabiam.", "pt"),
    ("El accidente fue en la planta y los obreros no sabían nada.", "es"),
])
def test_detect_lang(texto, lang):
    assert r3.detect_lang(texto) == lang


def test_r1_con_los_idiomas_del_caso_y_sin_foia():
    seed = {"seed_title": "Kyshtym", "idiomas_research": ["ruso", "inglés", "español"]}
    p = r3.build_discovery_prompt(seed, "un foco")
    assert "Buscá con Google en ruso, inglés y español." in p and "FOIA" not in p and "INGLÉS" not in p
    assert "prensa local de la época del evento" in p and "archivos desclasificados" in p
    assert "en ruso, inglés y español, con estas palabras" in r3.build_alt_prompt({**seed, "nombres_lugar": ["Mayak"]}, "f")
    assert "INGLÉS y en el idioma" in r3.build_discovery_prompt({"seed_title": "x"}, "f")   # sin perfil: como antes
    assert not any("FOIA" in f or "primera semana" in f for f in r3.DISCOVERY_FOCOS)


def test_gobiernos_y_accept_language():
    rank = lambda u: r3._doc_rank({"tipo": "prensa_posterior", "url": u})[1]   # noqa: E731
    assert rank("https://www.gob.mx/x") is False and rank("https://x.gov.it/a") is False and rank("https://a.gov/b") is False
    assert rank("https://www.nytimes.com/x") is True
    try:
        r3.set_idiomas(["ruso", "inglés", "español"])
        assert r3.ACCEPT_LANGUAGE == "ru,en;q=0.8,es;q=0.6"
    finally:
        r3.set_idiomas(None)
    assert r3.ACCEPT_LANGUAGE == "en,es;q=0.8"


def test_colas_de_notas_en_varios_idiomas():
    for h in ("Notas", "Bibliografía", "Referencias", "Anmerkungen", "Literatur", "Примечания", "Литература"):
        assert r3._TAIL_HEAD.search(f"\n{h}\n"), h


# ═══════════════════════════════════════════════════════════════
#  prompts: guion v5.3 y ficha v2.2 literales; escaleta y columna sin cambio
# ═══════════════════════════════════════════════════════════════

def test_prompts_f23_literales():
    assert g4.system() == g4.SYSTEM_V5_3 == _sistema("PROMPT_GUIONISTA_v5_3.md") and g4.PROMPT_VERSION == "f23-1"
    assert fc.system() == fc.SYSTEM_F23_1 == _sistema("PROMPT_FICHA_v2_2.md") and fc.PROMPT_VERSION == "f23-1"
    assert [_md5(g4.system()), _md5(fc.system())] == ["8ca9aa494e3a0b9b4a99f60e6006c5f8",
                                                      "070b75dff58aecfa407fac3d62020ce4"]
    assert [_md5(me.SYSTEM_V2), _md5(mc.SYSTEM)] == ["22cfd68b7cee4734e95bb3ee27bb96b2", "f294cf6b1220983903ce339f5b21cb27"]
    assert _md5(g4.system("f22-1")) == "743e4f0a7ff9e58d86762bbd43679952"
    assert _md5(fc.system("f22-1")) == "7d3599dc6e4123a3bb883fc15a541e71"


def test_diff_de_los_prompts_es_solo_lo_dicho():
    import difflib
    d = [x for x in difflib.unified_diff(g4.system("f22-1").split("\n"), g4.system().split("\n"), n=0, lineterm="")
         if x[:1] in "+-" and x[:3] not in ("+++", "---")]
    assert len(d) == 2 and d[0].startswith("-Las fechas: la fecha completa una vez") and \
        d[1].startswith("+Las fechas: cada fecha nueva se dice completa la primera vez")
    d = [x for x in difflib.unified_diff(fc.system("f22-1").split("\n"), fc.system().split("\n"), n=0, lineterm="")
         if x[:1] in "+-" and x[:3] not in ("+++", "---")]
    assert len(d) == 10
    assert "(año, mes o día)" in fc.system() and "(6 a 15)" in fc.system() and "las mejores 10 a 25" in fc.system()
    assert "entre 40 y 80 según lo que el pool dé (nivel 1 entre 10 y 20)" in fc.system()
    assert "escenas (6–15), hechos (40–80" in fc.prompt({"datos": [], "cronologia": [], "citas": [], "personajes": [],
                                                       "lugares": []}, "x")


def test_dorado_v3_solo_cambian_las_bandas(tmp_path, monkeypatch):
    import test_module_f11 as t11
    digest, out = t11._run_v3(tmp_path, monkeypatch)
    assert digest == t11.V3_GOLDEN

    def rev(s: str) -> str:
        for a, b in t11.BANDAS_F23:
            s = s.replace(a, b)
        return s
    h = hashlib.sha256()
    for name in ("01b_guionista_v3.json", "01b_editor_v3.json", "01a_skeleton.json", "01b_narration.json",
                 "01b_narracion_v3.json"):
        h.update(rev((tmp_path / "t-f11" / name).read_bytes().decode("utf-8")).encode("utf-8"))
    h.update(rev(json.dumps(out["juez"], ensure_ascii=False, sort_keys=True)).encode("utf-8"))
    assert h.hexdigest() == t11.V3_GOLDEN_F22
