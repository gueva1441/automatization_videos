"""
test_module_f20.py — F20 (parte 1: el research se adapta al tema). El perfil del seed trae `roles_testigo`,
`roles_antagonista` y `sustantivos_conteo` (después de R1); el research los lee en lugar de las listas fijas de Orleans:
`_TITLES`/`_NOT_PERSON` sin términos de tema, el prompt de R3 con los roles del perfil, el conteo con los sustantivos del
perfil (un caso de presos, uno de muertos); descargas con cupo por idioma; `elegible_humano` = no antagonista y (cita
propia verificada o ≥ 3 ítems), sin presencia en el año (Reed, Kutepova, Osetrov, Gusman). Sin red ni LLM.
"""
from __future__ import annotations

import json
import random
import string

import pytest

from researcher_steps import research_v3 as r3

VOC_ORLEANS = {"roles_testigo": ["preso", "presos", "guardia", "guardias", "oficial", "deputy", "deputies"],
               "roles_antagonista": ["sheriff", "alguacil"], "sustantivos_conteo": ["presos", "reclusos", "prisoners"]}
VOC_KYSHTYM = {"roles_testigo": ["operario", "liquidador", "evacuado", "médico", "físico", "ликвидатор"],
               "roles_antagonista": ["ministerio", "dirección de la planta", "министерство"],
               "sustantivos_conteo": ["muertos", "evacuados", "irradiados", "hospitalizados", "погибших", "эвакуированных"]}
# los términos de tema que el handoff saca (§1.2); «sheriff», «deputy» y «alguacil» quedan como cargos delante de un
# nombre (como «captain»), no como palabras que hacen de un nombre un no-persona
TEMA = ("inmate", "recluso", "reclusa", "preso", "presa", "warden", "deputies", "guardias", "guards", "abogado",
        "abogada", "attorney")


@pytest.fixture(autouse=True)
def _sin_vocabulario():
    r3.set_vocabulario(None)
    yield
    r3.set_vocabulario(None)


# ═══════════════════════════════════════════════════════════════
#  1.1 Perfil con los tres campos
# ═══════════════════════════════════════════════════════════════

def test_vocabulario_del_perfil_con_los_tres_campos():
    seen = {}

    def call(prompt, response_schema=None, description=None):
        seen.update(p=prompt, s=response_schema)
        return {"roles_testigo": [{"es": "operario", "otras": ["operator", "оператор"]}, {"es": " ", "otras": []},
                                  "liquidador"],
                "roles_antagonista": [{"es": "ministerio", "otras": []}],
                "sustantivos_conteo": [{"es": "muertos", "otras": ["погибших"]}, {"es": "evacuados", "otras": []}]}
    voc = r3.seed_vocabulario({"seed_title": "Desastre nuclear Kyshtym Mayak"},
                              [{"titulo": "Кыштымская авария", "idioma": "ru", "por_que": "testimonios"}],
                              idiomas="ruso", call=call)
    assert voc == {"roles_testigo": ["operario", "operator", "оператор", "liquidador"],
                   "roles_antagonista": ["ministerio"], "sustantivos_conteo": ["muertos", "погибших", "evacuados"]}
    assert set(seen["s"]["required"]) == {"roles_testigo", "roles_antagonista", "sustantivos_conteo"}
    assert seen["s"]["properties"]["roles_testigo"]["items"]["required"] == ["es", "otras"]
    assert "Кыштымская авария" in seen["p"] and "ruso" in seen["p"] and "4 a 10" in seen["p"]


def test_formas_una_por_elemento():
    assert r3._formas(["preso / presos (en) prisoner / prisoners", "sheriff", "Corte Suprema (es); Supreme Court (en)",
                       "x", "presos"]) == ["preso", "presos", "prisoner", "prisoners", "sheriff", "Corte Suprema",
                                           "Supreme Court"]
    r3.set_vocabulario({"sustantivos_conteo": ["preso / presos (en) prisoner / prisoners"]})
    assert r3.count_value("The jail held 6,375 prisoners.") == ("6,375", 6375)


def test_run_seed_completa_el_perfil_despues_de_r1(tmp_path, monkeypatch):
    (tmp_path / "_perfil.json").write_text(json.dumps({"anio_evento": 1957, "nombres_lugar": ["Mayak"],
                                                       "place_re": r"\bMayak\b", "idioma_local": "ruso"}),
                                           encoding="utf-8")
    orden = []
    monkeypatch.setattr(r3, "discover_sources", lambda s2, **k: orden.append("R1") or {"fuentes": [{"titulo": "x"}]})
    monkeypatch.setattr(r3, "seed_vocabulario", lambda seed, fuentes, **k: orden.append(("perfil", fuentes)) or VOC_KYSHTYM)
    (tmp_path / "fuentes").mkdir()
    monkeypatch.setattr(r3, "download_sources", lambda *a, **k: {"documentos": []})
    monkeypatch.setattr(r3, "refine_fichas", lambda *a, **k: None)
    monkeypatch.setattr(r3, "build_pool", lambda *a, **k: {"datos": [], "cronologia": [], "citas": [],
                                                           "personajes": [], "lugares": []})
    monkeypatch.setattr(r3, "pool_to_blocks", lambda pool: {})
    r3.run_seed({"seed_title": "Kyshtym"}, "t", tmp_path, gate=False)
    prof = json.loads((tmp_path / "_perfil.json").read_text(encoding="utf-8"))
    assert orden == ["R1", ("perfil", [{"titulo": "x"}])]
    assert all(prof[k] == VOC_KYSHTYM[k] for k in VOC_KYSHTYM) and prof["nombres_lugar"] == ["Mayak"]
    assert r3.count_value("Hubo 10,700 evacuados.") == ("10,700", 10700)     # el vocabulario quedó puesto


# ═══════════════════════════════════════════════════════════════
#  1.2 Listas sin términos de tema; R3 con los roles del perfil
# ═══════════════════════════════════════════════════════════════

def test_listas_sin_terminos_de_tema():
    pat = r3._NOT_PERSON.pattern
    assert not [t for t in TEMA if t in pat.split("|") or rf"|{t}|" in pat or rf"({t}|" in pat or rf"|{t})" in pat]
    assert not set(TEMA) & r3._TITLES
    assert not r3.is_named_person("Oficiales en Conchetta") and r3.is_named_person("Keanna Herbert")
    r3.set_vocabulario(VOC_ORLEANS)                              # los roles del caso se suman en tiempo de ejecución
    assert {"sheriff", "deputy", "guardias"} <= r3._TITLES
    assert r3.is_named_person("Deputy Foster") and not r3.is_named_person("Guardias Templeman")
    assert r3.same_person("Marlin N. Gusman", "Sheriff Martin Gusman")
    r3.set_vocabulario(None)
    assert "guardias" not in r3._TITLES and r3.same_person("Deputy Renard Reed", "Renard Reed")


def test_prompt_r3_con_los_roles_del_perfil():
    doc = {"titulo": "t", "tipo": "academico", "anio": 2016, "url": "u"}
    p = r3.build_extraction_prompt({"seed_title": "Kyshtym", **VOC_KYSHTYM}, doc, "texto", (1, 1))
    assert "operario, liquidador, evacuado" in p and "ministerio, dirección de la planta" in p
    for viejo in ("preso, guardia, familiar, rescatista, vecino", "funcionarios, abogados o expertos"):
        assert viejo not in p
    assert "según el caso" in r3.build_extraction_prompt({"seed_title": "x"}, doc, "texto", (1, 1))


def test_conteo_con_los_sustantivos_del_perfil():
    assert r3.count_value("La cárcel tenía 6,375 presos.") is None            # sin perfil, «presos» no es conteo
    assert r3.count_value("Murieron 1,500 personas.") == ("1,500", 1500)      # «personas» y «víctimas», siempre
    r3.set_vocabulario(VOC_ORLEANS)
    assert r3.count_value("La cárcel tenía 6,375 presos.") == ("6,375", 6375)
    assert r3.count_value("Se estimaron 8,015 muertos.") is None
    r3.set_vocabulario(VOC_KYSHTYM)
    assert r3.count_value("Se estimaron 8,015 muertos por la radiación.") == ("8,015", 8015)
    assert r3.count_value("Fueron 10,000 evacuados y 2,000 irradiados.") is None   # dos conteos: no es canónica
    assert r3.count_value("было 10 700 эвакуированных") is None              # «10 700» con espacio no es cifra
    assert r3.count_value("La cárcel tenía 6,375 presos.") is None


# ═══════════════════════════════════════════════════════════════
#  1.2 Descargas por idioma
# ═══════════════════════════════════════════════════════════════

def _texto(k: int) -> str:
    rnd = random.Random(k)
    return " ".join("".join(rnd.choice(string.ascii_lowercase) for _ in range(7)) for _ in range(600))


def test_descargas_por_idioma(tmp_path):
    fuentes, prev = [], []
    for k in range(24):
        ru = k % 2 == 1
        f = {"id": f"F{k + 1:02d}", "url": f"https://x{k}.org/a", "titulo": ("Кыштымская авария " if ru else "Kyshtym ")
             + str(k), "idioma": "en" if k % 4 == 1 else ("ru" if ru else "en"), "prioridad": 1 + k // 12, "tipo": "x"}
        fuentes.append(f)
        (tmp_path / f"d{k}.txt").write_text(_texto(k), encoding="utf-8")
        prev.append({"url": f["url"], "ok": True, "estado": "ok", "txt": f"d{k}.txt", "caracteres": 4500,
                     "nombra_evento": True})
    (tmp_path / "manifest.json").write_text(json.dumps({"documentos": prev}), encoding="utf-8")
    man = r3.download_sources(fuentes, tmp_path, place_re="Kyshtym", get=lambda u: (_ for _ in ()).throw(AssertionError))
    ok = {}
    por_id = {f["id"]: f for f in fuentes}
    for d in man["documentos"]:
        lg = r3.fuente_idioma(por_id[d["id"]])
        ok.setdefault(lg, [0, 0])[0 if d["ok"] else 1] += 1
    assert ok == {"en": [10, 2], "ru": [10, 2]}                               # 10 por idioma, no 10 en total
    sin = [d["id"] for d in man["documentos"] if d["estado"] == "no_intentada"]
    assert sin == ["F21", "F22", "F23", "F24"]                                # dentro de cada idioma, por prioridad
    assert r3.fuente_idioma({"titulo": "Авария на «Маяке»", "idioma": "en"}) == "ru"   # el alfabeto manda
    assert r3.fuente_idioma({"titulo": "Kyshtym", "idioma": "EN"}) == "en"


# ═══════════════════════════════════════════════════════════════
#  1.3 Humano elegible
# ═══════════════════════════════════════════════════════════════

def _cita(autor: str, verificada: bool = True) -> dict:
    return {"autor": autor, "texto": "x", "testimonio": True,
            "verificacion": {"estado": "verificada" if verificada else "sin_verificar"}}


def test_elegible_humano_cuatro_casos():
    r3.set_vocabulario({**VOC_KYSHTYM, "roles_antagonista": VOC_KYSHTYM["roles_antagonista"] + ["sheriff"]})
    pool = {"cronologia": [{"id": "T01", "fecha": "1957-09-29", "evento": "explota el tanque"}],
            "datos": [{"texto": f"Reed vio el agua {i}"} for i in range(2)]
                     + [{"texto": "Kutepova demandó al Estado"}],
            "citas": [_cita("Renard Reed"), _cita("Nadezhda Kutepova"), _cita("Ivan Osetrov"),
                      _cita("Marlin Gusman"), _cita("Pyotr Serov", verificada=False)],
            "personajes": [
                {"nombre": "Renard Reed", "testigo": True, "presente_en": ["T01"]},         # testigo con 3 ítems
                {"nombre": "Nadezhda Kutepova", "testigo": False, "presente_en": []},     # décadas después: cita propia
                {"nombre": "Ivan Osetrov", "testigo": True, "presente_en": []},           # una sola frase verificada
                {"nombre": "Marlin Gusman", "rol": "sheriff", "testigo": True, "presente_en": ["T01"]},  # rol que decide
                {"nombre": "Pyotr Serov", "testigo": True, "presente_en": []},            # una cita sin verificar
                {"nombre": "Renard Reedy", "rol": "Oficial del sheriff", "testigo": True, "presente_en": []},  # nombra
                {"nombre": "Ana Ministro", "antagonista": True, "presente_en": []}]}
    pool["datos"] += [{"texto": f"Ana Ministro firmó {i}"} for i in range(3)]
    pool["citas"].append(_cita("Renard Reedy"))
    r3.person_stats(pool, 1957)
    el = {p["nombre"]: p["elegible_humano"] for p in pool["personajes"]}
    assert el == {"Renard Reed": True, "Nadezhda Kutepova": True, "Ivan Osetrov": True, "Marlin Gusman": False,
                  "Pyotr Serov": False, "Ana Ministro": False, "Renard Reedy": True}   # el rol lo nombra, no lo es
    pres = {p["nombre"]: p["presente_en_evento"] for p in pool["personajes"]}
    assert pres["Renard Reed"] and pres["Ivan Osetrov"] and not pres["Pyotr Serov"]   # informativo, no excluye
