# -*- coding: utf-8 -*-
"""F78a — madres de persona: identidad propia + variante por tramo (estado / edad) (HANDOFF_F78a_madres_identidad_estado).

Sin red: nada llama a fal ni a un LLM."""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

import pytest

import asset_manager as am
import foto_madre as fm

PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 16


# ── asset_manager (F78a) ──────────────────────────────────────────────────────────────────────────────────────────
@pytest.fixture
def _motor_seedream(monkeypatch):
    """El camino de secuencia sigue vivo con Seedream (como test_module_f60_bc)."""
    monkeypatch.setattr(am.api, "image_engine", "seedream")


def _png(p: Path, contenido: bytes = PNG) -> str:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(contenido)
    return str(p)


def _carmen(tmp_path: Path, claves=("1981-1982", "1981-1982_15", "1992-2000_33"), crear=True) -> tuple[dict, dict]:
    """Carmen-like: era 1981-2000, 14 años en 1981, estado 1981-1982 y 1992-2000. Devuelve (registry, personas_canon)."""
    d = tmp_path / "foto_madre"
    reg = {"Carmen Cortés": _png(d / "carmen_cortes.png")}
    variantes = []
    for c in claves:
        p = d / f"carmen_cortes@{c}.png"
        if crear:
            _png(p, PNG + c.encode())
        variantes.append({"clave": c, "tramo": c.split("_")[0], "edad": None, "path": str(p)})
    canon = {"Carmen Cortés": {"era": "1981-2000", "age_at_event": 14,
                               "condition_by_period": [{"years": "1981-1982", "condition": "rash on the hands"},
                                                       {"years": "1992-2000", "condition": "unable to work"}],
                               "variantes": variantes}}
    return reg, canon


@pytest.mark.parametrize("anio, clave", [
    ("1981", "1981-1982"),        # tramo, edad = la de la madre → sin sufijo
    ("1982", "1981-1982_15"),     # tramo + edad 15
    ("2000", "1992-2000_33"),     # tramo + edad 33
])
def test_variante_elegida_por_tramo_y_edad(tmp_path, anio, clave):
    reg, canon = _carmen(tmp_path)
    assert fm.clave_de_foto(canon["Carmen Cortés"], anio)["clave"] == clave
    m = am._madres_para_item(["Carmen Cortés"], [], anio, reg, canon)
    assert m == [("Carmen Cortés", str(tmp_path / "foto_madre" / f"carmen_cortes@{clave}.png"))]   # ref = el NOMBRE


def test_sin_variante_para_la_clave_va_la_madre_limpia(tmp_path):
    reg, canon = _carmen(tmp_path)
    # 1990: fuera de los tramos; la regla única da una clave de edad que no tiene variante declarada → madre limpia
    assert fm.clave_de_foto(canon["Carmen Cortés"], "1990")["clave"] not in ("1981-1982", "1981-1982_15", "1992-2000_33")
    assert am._madres_para_item(["Carmen Cortés"], [], "1990", reg, canon) == [("Carmen Cortés", reg["Carmen Cortés"])]
    # clave vacía (sin tramo ni edad que difiera) → madre limpia
    canon_sin_edad = {"Carmen Cortés": dict(canon["Carmen Cortés"], age_at_event=None)}
    assert fm.clave_de_foto(canon_sin_edad["Carmen Cortés"], "1990")["clave"] == ""
    assert am._madres_para_item(["Carmen Cortés"], [], "1990", reg, canon_sin_edad) == [("Carmen Cortés", reg["Carmen Cortés"])]
    # año ilegible → madre limpia
    assert am._madres_para_item(["Carmen Cortés"], [], None, reg, canon) == [("Carmen Cortés", reg["Carmen Cortés"])]


def test_desempate_entre_tramos_que_se_pisan_gana_el_mas_corto(tmp_path):
    d = tmp_path / "foto_madre"
    reg = {"Arcadio": _png(d / "arcadio.png")}
    canon = {"Arcadio": {"era": "1981-1990", "age_at_event": None,
                         "condition_by_period": [{"years": "1981-1990", "condition": "deformed hands"},
                                                 {"years": "1985-1986", "condition": "in a wheelchair"}],
                         "variantes": [{"clave": "1981-1990", "path": _png(d / "arcadio@1981-1990.png", PNG + b"a")},
                                       {"clave": "1985-1986", "path": _png(d / "arcadio@1985-1986.png", PNG + b"b")}]}}
    assert am._madres_para_item(["Arcadio"], [], "1985", reg, canon) == [("Arcadio", str(d / "arcadio@1985-1986.png"))]
    assert am._madres_para_item(["Arcadio"], [], "1983", reg, canon) == [("Arcadio", str(d / "arcadio@1981-1990.png"))]


def test_variante_declarada_sin_archivo_va_la_madre_limpia(tmp_path):
    reg, canon = _carmen(tmp_path, crear=False)
    assert am._madres_para_item(["Carmen Cortés"], [], "1982", reg, canon) == [("Carmen Cortés", reg["Carmen Cortés"])]


def test_persona_fuera_de_era_sigue_sin_madre(tmp_path):
    d = tmp_path / "foto_madre"
    reg = {"Daniel Écija": _png(d / "daniel_ecija.png")}
    canon = {"Daniel Écija": {"era": "1962-1963", "age_at_event": 25,
                              "condition_by_period": [{"years": "1991-1992", "condition": "terminally ill"}],
                              "variantes": [{"clave": "1991-1992_54", "path": _png(d / "daniel_ecija@1991-1992_54.png")}]}}
    assert am.persona_aporta_madre(canon["Daniel Écija"], "1991") is False
    assert am._madres_para_item(["Daniel Écija"], [], "1991", reg, canon) == []


def test_objeto_no_usa_variantes(tmp_path, _motor_seedream):
    reg, canon = _carmen(tmp_path)
    reg["__subject__"] = _png(tmp_path / "foto_madre" / "__subject__.png")
    m = am._madres_para_item(["Carmen Cortés"], ["__subject__"], "1982", reg, canon)
    assert m == [("Carmen Cortés", str(tmp_path / "foto_madre" / "carmen_cortes@1981-1982_15.png")),
                 ("__subject__", reg["__subject__"])]


def _item(prompt, anio):
    return {"prompt": prompt, "persona": ["Carmen Cortés"], "anio": anio, "foto_madre_ref": [],
            "text_in_image": {"present": False, "text": "", "font": "", "location": ""}}


def test_secuencia_dos_variantes_de_una_persona_son_dos_lotes(tmp_path, monkeypatch, _motor_seedream):
    monkeypatch.setattr(am, "OUTPUT_DIR", tmp_path)
    reg, canon = _carmen(tmp_path)
    llamadas = []

    def fake(video_id, prompts, refs, madre_paths, out_paths):
        llamadas.append((list(prompts), refs, madre_paths))
        for p in out_paths:
            p.write_bytes(PNG)
        return list(out_paths)
    monkeypatch.setattr(am, "_llamar_secuencia", fake)
    ch = {"id": "ch02", "render_engine": "flux",
          "image_prompts": [_item("a1", "1981"), _item("b1", "2000"), _item("a2", "1981"), _item("b2", "2000")]}
    res = am._pre_paso_secuencia([ch], "v", reg, canon)
    d = tmp_path / "foto_madre"
    por_madre = {tuple(mp): (pr, refs) for pr, refs, mp in llamadas}
    assert len(llamadas) == 2
    assert por_madre[(str(d / "carmen_cortes@1981-1982.png"),)] == (["a1", "a2"], ["Carmen Cortés"])
    assert por_madre[(str(d / "carmen_cortes@1992-2000_33.png"),)] == (["b1", "b2"], ["Carmen Cortés"])
    lotes = {res[("ch02", "img", i)]["lote"] for i in (1, 2, 3, 4)}
    assert lotes == {"Carmen Cortés@carmen_cortes@1981-1982#1", "Carmen Cortés@carmen_cortes@1992-2000_33#1"}
    assert all(res[("ch02", "img", i)]["foto_madre_refs"] == ["Carmen Cortés"] for i in (1, 2, 3, 4))


def test_clave_lote_cambia_si_cambia_el_contenido_de_la_madre(tmp_path):
    madre = tmp_path / "carmen_cortes@1981-1982.png"
    _png(madre, PNG + b"vieja")
    c1 = am._clave_lote(["a1", "a2"], ["Carmen Cortés"], [str(madre)])
    assert am._clave_lote(["a1", "a2"], ["Carmen Cortés"], [str(madre)]) == c1          # mismo contenido → misma clave
    _png(madre, PNG + b"nueva")
    assert am._clave_lote(["a1", "a2"], ["Carmen Cortés"], [str(madre)]) != c1          # madre regenerada → clave nueva
    falta = am._clave_lote(["a1", "a2"], ["Carmen Cortés"], [str(tmp_path / "no_existe.png")])
    assert falta not in (c1, am._clave_lote(["a1", "a2"], ["Carmen Cortés"], [str(madre)]))   # inexistente → md5 ""


# ── foto_madre + m06 (F78a) ─────────────────────────────────────────────────────────────────────────────────────


PNG78 = b"\x89PNG\r\n\x1a\n" + b"\x00" * 16
CARMEN = {"name": "Carmen Cortés", "role": "adolescent victim", "era": "1981-2000", "age_at_event": 14,
          "appearance_canon": "a fourteen-year-old Spanish girl",
          "condition_by_period": [{"years": "1981-1982", "condition": "Visibly emaciated."},
                                  {"years": "1992-2000", "condition": "Unable to work, living on a disability pension."}]}
ARCADIO = {"name": "Arcadio Fernandez", "role": "victim", "era": "1981-1989", "age_at_event": None,
           "appearance_canon": "a middle-aged Spanish man",
           "condition_by_period": [{"years": "1981-1989", "condition": "Deformed hands and upper body with disabling chronic pain."}]}
SANCHO = {"name": "Jesús Sancho Rof", "role": "minister", "era": "1981", "age_at_event": None,
          "appearance_canon": "a middle-aged Spanish man", "condition_by_period": []}


def test_descriptor_edad_tabla_y_palabras():
    assert fm.descriptor_edad(14) == "fourteen-year-old" and fm.descriptor_edad(1) == "one-year-old"
    assert fm.descriptor_edad(19) == "nineteen-year-old" and fm.descriptor_edad(20) == "early-20s"
    assert fm.descriptor_edad(25) == "mid-20s" and fm.descriptor_edad(33) == "early-30s" and fm.descriptor_edad(59) == "late-50s"
    assert fm.descriptor_edad(60) == "elderly" and fm.descriptor_edad(91) == "elderly"
    assert fm.descriptor_edad(None) is None and fm.descriptor_edad("14") is None and fm.descriptor_edad(0) is None
    assert fm.descriptor_edad(True) is None


def test_clave_de_foto_tramo_y_edad():
    c = lambda a: fm.clave_de_foto(CARMEN, a)  # noqa: E731
    assert c("1981")["clave"] == "1981-1982" and c("1981")["edad"] is None          # edad = la de la madre → sin sufijo
    assert c("1982")["clave"] == "1981-1982_15" and c("1982")["anio_estilo"] == 1981
    assert c("1992")["clave"] == "1992-2000_25" and c("2000")["clave"] == "1992-2000_33" and c("2000")["anio_estilo"] == 1992
    assert c("1990") == {"clave": "sin_estado_23", "tramo": None, "condition": None, "edad": 23, "anio_estilo": 1990}
    assert c("2000")["condition"] == "Unable to work, living on a disability pension"
    assert fm.clave_de_foto(ARCADIO, "1985")["clave"] == "1981-1989" and fm.clave_de_foto(ARCADIO, "2000")["clave"] == ""
    assert fm.clave_de_foto(SANCHO, "1981")["clave"] == "" and fm.clave_de_foto(CARMEN, None)["clave"] == ""
    assert fm.clave_de_foto(None, "1981")["clave"] == ""
    pisan = {**ARCADIO, "condition_by_period": [{"years": "1981-1989", "condition": "largo"}, {"years": "1983-1984", "condition": "corto"}]}
    assert fm.clave_de_foto(pisan, "1983")["clave"] == "1983-1984" and fm.clave_de_foto(pisan, "1985")["clave"] == "1981-1989"


def test_prompt_variante_texto_completo():
    """F78b: edad exacta en dígitos + estado_visible (no la condition cruda); sin la frase «Show only…» ni el descriptor."""
    p = fm._prompt_variante(fm.clave_de_foto(CARMEN, "2000"), "")
    assert p == ("The same person as in the reference image: same face, same features, same identity. The person is now 33 years "
                 "old; show that age in the face, hair and body. Waist-up portrait framed so that the face and both hands are "
                 "visible, wearing a plain, clean, light-coloured shirt, plain mid-grey background, soft even light. A grainy 35mm "
                 "documentary photograph taken in 1992, with muted colors and slight underexposure, in a dark-history realist "
                 "style. No readable text, no signage, no labels.")
    con = fm._prompt_variante(fm.clave_de_foto(ARCADIO, "1985"), "fingers curled and rigid with misshapen knuckles.")
    assert ("same identity. fingers curled and rigid with misshapen knuckles. Waist-up portrait" in con
            and "years old" not in con and "Deformed" not in con and "Show only" not in con and "taken in 1981" in con)
    assert "early-30s" not in p and "Show only" not in p


def test_prompt_persona_lleva_rasgos():
    p = fm._prompt_persona(SANCHO, "Southern European Spanish features.", "long oval face, receding grey hair")
    assert p.startswith("Head-and-shoulders portrait of a middle-aged Spanish man, long oval face, receding grey hair, wearing a "
                        "plain, clean, light-coloured shirt. Southern European Spanish features. Neutral expression")


def test_llamar_rasgos_una_llamada_con_schema_enum(monkeypatch):
    import claude_helpers
    vistos = []

    def call_json(prompt, **k):
        vistos.append((prompt, k))
        return [{"name": "Carmen Cortés", "rasgos": "heart-shaped face."}, {"name": "Arcadio Fernandez", "rasgos": "square jaw"}]
    monkeypatch.setattr(claude_helpers, "call_json", call_json)
    entrada = [{"name": "Carmen Cortés"}, {"name": "Arcadio Fernandez"}]
    assert fm._llamar_rasgos(entrada) == {"Carmen Cortés": "heart-shaped face", "Arcadio Fernandez": "square jaw"}
    (prompt, k), = vistos
    assert prompt.startswith(fm.PROMPT_RASGOS) and '"Carmen Cortés"' in prompt
    assert k["model"] == "claude-opus-5-5" and k["effort"] == "high" and k["description"] == "foto madre rasgos"
    assert k["response_schema"]["items"]["properties"]["name"]["enum"] == ["Carmen Cortés", "Arcadio Fernandez"]


def _visual78():
    return {"chapters": [{"chapter_number": 4, "image_prompts": [
        {"prompt": "a", "persona": ["Carmen Cortés"], "anio": "1981", "people_group": []},
        {"prompt": "b", "persona": ["Carmen Cortés"], "anio": "1981", "people_group": []},
        {"prompt": "c", "persona": ["Carmen Cortés"], "anio": "1982", "people_group": []},
        {"prompt": "d", "persona": ["Carmen Cortés"], "anio": "2000", "people_group": []},
        {"prompt": "e", "persona": ["Jesús Sancho Rof"], "anio": "1981", "people_group": []},
        {"prompt": "f", "persona": ["Jesús Sancho Rof"], "anio": "1981", "people_group": []}]}]}


ESTADOS_FAKE: dict[str, str] = {}


def _fakes(monkeypatch, tmp_path, llamadas, rasgos_por_nombre):
    monkeypatch.setattr(fm, "OUTPUT_DIR", tmp_path)
    monkeypatch.setattr(fm.api, "image_engine", "nb2_lite", raising=False)
    monkeypatch.setattr(fm, "_llamar_rasgos", lambda entrada: (llamadas.append(("rasgos", [e["name"] for e in entrada])),
                                                               {e["name"]: rasgos_por_nombre[e["name"]] for e in entrada})[1])
    monkeypatch.setattr(fm, "_llamar_estados", lambda filas: (llamadas.append(("estados", [(f["name"], f["tramo"]) for f in filas])),
                                                              {(f["name"], f["tramo"]): ESTADOS_FAKE.get(f["tramo"], "gaunt face")
                                                               for f in filas})[1])

    def madre(prompt, dest):
        llamadas.append(("madre", dest.name, prompt))
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(PNG78 + prompt.encode())
        return {"endpoint": "seedream", "path": str(dest)}

    def variante(prompt, ref, dest):
        llamadas.append(("variante", dest.name, ref.name, prompt))
        dest.write_bytes(PNG78 + prompt.encode())
        return {"motor": "nb2_lite", "usd": 0.04}
    monkeypatch.setattr(fm, "_generate_madre_seedream", madre)
    monkeypatch.setattr(fm, "_generate_variante", variante)


def test_madres_con_rasgos_y_variantes_por_clave(tmp_path, monkeypatch):
    llamadas: list = []
    rasgos = {"Carmen Cortés": "heart-shaped face, long dark hair", "Jesús Sancho Rof": "long oval face, grey moustache"}
    _fakes(monkeypatch, tmp_path, llamadas, rasgos)
    topic = {"id": "t", "documented_people": [dict(CARMEN), dict(SANCHO)], "people_groups": []}
    est = fm.generate_fotos_madre_personas(topic, "vid", _visual78())
    assert [c for c in llamadas if c[0] == "rasgos"] == [("rasgos", ["Carmen Cortés", "Jesús Sancho Rof"])]   # UNA llamada
    madres = {c[1]: c[2] for c in llamadas if c[0] == "madre"}
    assert set(madres) == {"carmen_cort_s.png", "jes_s_sancho_rof.png"} and rasgos["Jesús Sancho Rof"] in madres["jes_s_sancho_rof.png"]
    variantes = sorted((c[1], c[2]) for c in llamadas if c[0] == "variante")
    assert variantes == [("carmen_cort_s@1981-1982.png", "carmen_cort_s.png"), ("carmen_cort_s@1981-1982_15.png", "carmen_cort_s.png"),
                         ("carmen_cort_s@1992-2000_33.png", "carmen_cort_s.png")]            # Sancho Rof: sin estado → limpia
    carmen = topic["documented_people"][0]
    assert [(v["clave"], v["edad"], v["fotos"]) for v in carmen["foto_madre_variantes"]] == [
        ("1981-1982", None, ["ch04_img_01", "ch04_img_02"]), ("1981-1982_15", 15, ["ch04_img_03"]), ("1992-2000_33", 33, ["ch04_img_04"])]
    assert topic["documented_people"][1]["foto_madre_variantes"] == []
    assert est["Carmen Cortés"]["rasgos"] == rasgos["Carmen Cortés"]
    rj = json.loads((tmp_path / "vid" / "foto_madre" / "rasgos.json").read_text(encoding="utf-8"))
    assert set(rj["personas"]) == {"Carmen Cortés", "Jesús Sancho Rof"} and rj["md5_entrada"]
    # segunda corrida, misma entrada: sin llamada de rasgos, sin madres ni variantes nuevas
    llamadas.clear()
    fm.generate_fotos_madre_personas(topic, "vid", _visual78())
    assert llamadas == []
    # cambian los rasgos de Carmen (entrada nueva): su madre y sus variantes van a _previas_f78b y se regeneran; Sancho Rof no
    topic["documented_people"][0]["role"] = "otra"
    rasgos["Carmen Cortés"] = "round face, short curly hair"
    fm.generate_fotos_madre_personas(topic, "vid", _visual78())
    assert ("madre", "carmen_cort_s.png") in [c[:2] for c in llamadas] and not [c for c in llamadas if c[1] == "jes_s_sancho_rof.png"]
    previas = sorted(p.name for p in (tmp_path / "vid" / "foto_madre" / "_previas_f78b").iterdir())
    assert previas == ["carmen_cort_s.png", "carmen_cort_s@1981-1982.png", "carmen_cort_s@1981-1982.prompt.txt",
                       "carmen_cort_s@1981-1982_15.png", "carmen_cort_s@1981-1982_15.prompt.txt",
                       "carmen_cort_s@1992-2000_33.png", "carmen_cort_s@1992-2000_33.prompt.txt"]
    assert len([c for c in llamadas if c[0] == "variante"]) == 3


def test_madre_de_antes_de_los_rasgos_se_mueve(tmp_path, monkeypatch):
    llamadas: list = []
    _fakes(monkeypatch, tmp_path, llamadas, {"Carmen Cortés": "x face", "Jesús Sancho Rof": "y face"})
    d = tmp_path / "vid" / "foto_madre"
    d.mkdir(parents=True)
    (d / "jes_s_sancho_rof.png").write_bytes(PNG78)
    (d / "jes_s_sancho_rof.prompt.txt").write_text("viejo", encoding="utf-8")
    topic = {"id": "t", "documented_people": [dict(CARMEN), {**SANCHO, "foto_madre": str(d / "jes_s_sancho_rof.png")}]}
    fm.generate_fotos_madre_personas(topic, "vid", _visual78())
    assert (d / "_previas_f78b" / "jes_s_sancho_rof.png").read_bytes() == PNG78
    assert (d / "_previas_f78b" / "jes_s_sancho_rof.prompt.txt").read_text(encoding="utf-8") == "viejo"
    assert "y face" in (d / "jes_s_sancho_rof.png").read_bytes().decode("latin-1")


def test_rasgos_fallan_no_mueve_nada(tmp_path, monkeypatch):
    _fakes(monkeypatch, tmp_path, [], {})
    monkeypatch.setattr(fm, "_llamar_rasgos", lambda e: (_ for _ in ()).throw(RuntimeError("401")))
    d = tmp_path / "vid" / "foto_madre"
    d.mkdir(parents=True)
    (d / "jes_s_sancho_rof.png").write_bytes(PNG78)
    topic = {"id": "t", "documented_people": [dict(CARMEN), {**SANCHO, "foto_madre": str(d / "jes_s_sancho_rof.png")}]}
    est = fm.generate_fotos_madre_personas(topic, "vid", _visual78())
    assert (d / "jes_s_sancho_rof.png").exists() and not (d / "_previas_f78b").exists()
    assert est["Carmen Cortés"]["estado"].startswith("sin cambios: rasgos fallaron")


def test_m06_variantes_dentro_de_la_persona(tmp_path, monkeypatch):
    from script_engine import m06_assembler as m6
    madre, var = tmp_path / "carmen.png", tmp_path / "carmen@1992-2000_33.png"
    madre.write_bytes(PNG78)
    var.write_bytes(PNG78)
    vs = [{"clave": "1992-2000_33", "tramo": "1992-2000", "edad": 33, "path": str(var), "fotos": ["ch07_supp_07"]},
          {"clave": "1981-1982", "tramo": "1981-1982", "edad": None, "path": str(tmp_path / "no.png"), "fotos": []}]
    topic = {"id": "t", "documented_people": [{**CARMEN, "foto_madre": str(madre), "foto_madre_variantes": vs}]}
    monkeypatch.setattr(m6, "sello_vigente", lambda tid: "papel")
    monkeypatch.setattr(m6, "_load_topic", lambda tid: topic)
    monkeypatch.setattr(m6, "_load_step", lambda tid, f: {"chapters": []})
    monkeypatch.setattr(m6, "SCRIPTS_DIR", tmp_path / "scripts")
    out = json.loads(m6.assemble_final_script("t").read_text(encoding="utf-8"))
    assert out["foto_madre_registry"] == {"Carmen Cortés": str(madre)}                    # las claves no entran al registry
    per = out["foto_madre_personas"]["Carmen Cortés"]
    assert per["age_at_event"] == 14 and per["variantes"] == [vs[0]]                    # solo las que existen
    assert "foto_madre_variantes" not in out


# ── F78b: estado visible + edad exacta ──────────────────────────────────────────────────────────────────────────
LOZANO = {"name": "Jesús Lozano", "role": "child victim", "era": "1981", "age_at_event": 6, "appearance_canon": "a six-year-old Spanish boy",
          "condition_by_period": [{"years": "1981-1981", "condition": "Hospitalized in a glass-walled room with ten other children."}]}


def _visual78b():
    v = _visual78()
    v["chapters"][0]["image_prompts"] += [{"prompt": "g", "persona": ["Jesús Lozano"], "anio": "1981", "people_group": []},
                                          {"prompt": "h", "persona": ["Jesús Lozano"], "anio": "1981", "people_group": []}]
    return v


def test_estados_una_llamada_pares_unicos_y_prompt_nuevo(tmp_path, monkeypatch):
    llamadas: list = []
    _fakes(monkeypatch, tmp_path, llamadas, {"Carmen Cortés": "a", "Jesús Sancho Rof": "b", "Jesús Lozano": "c"})
    monkeypatch.setattr(sys.modules[__name__], "ESTADOS_FAKE", {"1981-1982": "emaciated, hollow cheeks, very thin arms."})
    topic = {"id": "t", "documented_people": [dict(CARMEN), dict(SANCHO), dict(LOZANO)]}
    est = fm.generate_fotos_madre_personas(topic, "vid", _visual78b())
    # UNA llamada; una fila por (persona, tramo) único: Carmen 1981-1982 (dos claves → una fila), Carmen 1992-2000, Lozano
    assert [c for c in llamadas if c[0] == "estados"] == [("estados", [("Carmen Cortés", "1981-1982"), ("Carmen Cortés", "1992-2000"),
                                                                       ("Jesús Lozano", "1981-1981")])]
    prompts = {c[1]: c[3] for c in llamadas if c[0] == "variante"}
    assert "same identity. emaciated, hollow cheeks, very thin arms. Waist-up" in prompts["carmen_cort_s@1981-1982.png"]
    assert "now 15 years old; show that age in the face, hair and body. emaciated" in prompts["carmen_cort_s@1981-1982_15.png"]
    assert "now 33 years old" in prompts["carmen_cort_s@1992-2000_33.png"] and "gaunt face." in prompts["carmen_cort_s@1992-2000_33.png"]
    ej = json.loads((tmp_path / "vid" / "foto_madre" / "estados.json").read_text(encoding="utf-8"))
    assert ej["md5_entrada"] and [e["tramo"] for e in ej["estados"]] == ["1981-1982", "1992-2000", "1981-1981"]
    assert ej["entrada"][0] == {"name": "Carmen Cortés", "tramo": "1981-1982", "condition": "Visibly emaciated"}
    # la firma queda en el .prompt.txt de la variante
    txt = (tmp_path / "vid" / "foto_madre" / "carmen_cort_s@1981-1982.prompt.txt").read_text(encoding="utf-8")
    assert re.search(r"^firma: [0-9a-f]{32}$", txt, re.M) and "emaciated" in txt
    assert [v["estado"] for v in est["Carmen Cortés"]["variantes"]] == ["ok", "ok", "ok"]


def test_sin_estado_visible_y_sin_edad_no_hay_variante(tmp_path, monkeypatch):
    llamadas: list = []
    _fakes(monkeypatch, tmp_path, llamadas, {"Carmen Cortés": "a", "Jesús Sancho Rof": "b", "Jesús Lozano": "c"})
    monkeypatch.setattr(sys.modules[__name__], "ESTADOS_FAKE", {"1981-1981": "", "1992-2000": ""})
    d = tmp_path / "vid" / "foto_madre"
    d.mkdir(parents=True)
    for n in ("jes_s_lozano@1981-1981.png", "jes_s_lozano@1981-1981_native.png"):     # variante vieja (F78a) en disco
        (d / n).write_bytes(PNG78)
    (d / "jes_s_lozano@1981-1981.llamada.json").write_text("{}", encoding="utf-8")
    topic = {"id": "t", "documented_people": [dict(CARMEN), dict(SANCHO), dict(LOZANO)]}
    est = fm.generate_fotos_madre_personas(topic, "vid", _visual78b())
    lozano = topic["documented_people"][2]
    assert lozano["foto_madre_variantes"] == [] and est["Jesús Lozano"]["variantes"][0]["estado"] == "sin variante: sin estado visible"
    assert not [c for c in llamadas if c[0] == "variante" and c[1].startswith("jes_s_lozano")]
    assert sorted(x.name for x in (d / "_previas_f78b").iterdir()) == [
        "jes_s_lozano@1981-1981.llamada.json", "jes_s_lozano@1981-1981.png", "jes_s_lozano@1981-1981_native.png"]
    # Carmen 1992-2000 sin estado visible pero con edad 33 → variante solo con la edad
    p33 = next(c[3] for c in llamadas if c[0] == "variante" and c[1] == "carmen_cort_s@1992-2000_33.png")
    assert "now 33 years old; show that age in the face, hair and body. Waist-up" in p33


def test_cache_de_estados_firma_y_rasgos_intactos(tmp_path, monkeypatch):
    llamadas: list = []
    _fakes(monkeypatch, tmp_path, llamadas, {"Carmen Cortés": "a", "Jesús Sancho Rof": "b"})
    estados_fake = {"1981-1982": "thin arms", "1992-2000": ""}
    monkeypatch.setattr(sys.modules[__name__], "ESTADOS_FAKE", estados_fake)
    topic = {"id": "t", "documented_people": [dict(CARMEN), dict(SANCHO)]}
    fm.generate_fotos_madre_personas(topic, "vid", _visual78())
    d = tmp_path / "vid" / "foto_madre"
    rasgos_md5 = hashlib.md5((d / "rasgos.json").read_bytes()).hexdigest()
    madre_md5 = hashlib.md5((d / "carmen_cort_s.png").read_bytes()).hexdigest()
    llamadas.clear()
    fm.generate_fotos_madre_personas(topic, "vid", _visual78())        # misma entrada, misma firma → nada
    assert llamadas == []
    # cambia la condición de 1981-1982 (entrada de estados nueva): una llamada de estados, solo esas variantes se rehacen
    topic["documented_people"][0]["condition_by_period"][0]["condition"] = "Lost twenty kilos."
    estados_fake["1981-1982"] = "very thin, sunken cheeks"
    fm.generate_fotos_madre_personas(topic, "vid", _visual78())
    assert [c[0] for c in llamadas].count("estados") == 1 and not [c for c in llamadas if c[0] in ("rasgos", "madre")]
    rehechas = sorted(c[1] for c in llamadas if c[0] == "variante")
    assert rehechas == ["carmen_cort_s@1981-1982.png", "carmen_cort_s@1981-1982_15.png"]      # la de 33 tiene la misma firma
    assert hashlib.md5((d / "rasgos.json").read_bytes()).hexdigest() == rasgos_md5                  # rasgos.json intacto
    assert hashlib.md5((d / "carmen_cort_s.png").read_bytes()).hexdigest() == madre_md5              # la madre no cambia de cara
    assert sorted(x.name for x in (d / "_previas_f78b").iterdir() if x.suffix == ".png") == [
        "carmen_cort_s@1981-1982.png", "carmen_cort_s@1981-1982_15.png"]


def test_variante_de_antes_de_la_firma_se_rehace(tmp_path, monkeypatch):
    llamadas: list = []
    _fakes(monkeypatch, tmp_path, llamadas, {"Carmen Cortés": "a", "Jesús Sancho Rof": "b"})
    topic = {"id": "t", "documented_people": [dict(CARMEN), dict(SANCHO)]}
    fm.generate_fotos_madre_personas(topic, "vid", _visual78())
    d = tmp_path / "vid" / "foto_madre"
    pt = d / "carmen_cort_s@1992-2000_33.prompt.txt"
    pt.write_text("modelo: x\n\nprompt viejo de F78a\n", encoding="utf-8")          # sin firma
    llamadas.clear()
    fm.generate_fotos_madre_personas(topic, "vid", _visual78())
    assert [c[1] for c in llamadas if c[0] == "variante"] == ["carmen_cort_s@1992-2000_33.png"]
    assert (d / "_previas_f78b" / "carmen_cort_s@1992-2000_33.prompt.txt").read_text(encoding="utf-8").endswith("F78a\n")


def test_estados_fallan_no_mueve_ni_genera_variantes(tmp_path, monkeypatch):
    llamadas: list = []
    _fakes(monkeypatch, tmp_path, llamadas, {"Carmen Cortés": "a", "Jesús Sancho Rof": "b"})
    topic = {"id": "t", "documented_people": [dict(CARMEN), dict(SANCHO)]}
    fm.generate_fotos_madre_personas(topic, "vid", _visual78())
    vivas = topic["documented_people"][0]["foto_madre_variantes"]
    topic["documented_people"][0]["condition_by_period"][0]["condition"] = "otra"
    monkeypatch.setattr(fm, "_llamar_estados", lambda f: (_ for _ in ()).throw(RuntimeError("401")))
    llamadas.clear()
    est = fm.generate_fotos_madre_personas(topic, "vid", _visual78())
    assert est["Carmen Cortés"]["variantes"].startswith("sin cambios: estados fallaron")
    assert not [c for c in llamadas if c[0] == "variante"] and not (tmp_path / "vid" / "foto_madre" / "_previas_f78b").exists()
    assert topic["documented_people"][0]["foto_madre_variantes"] == vivas


def test_sin_tramos_no_hay_llamada_de_estados(tmp_path, monkeypatch):
    llamadas: list = []
    _fakes(monkeypatch, tmp_path, llamadas, {"Carmen Cortés": "a"})
    sin_estado = {**CARMEN, "condition_by_period": []}
    visual = {"chapters": [{"chapter_number": 7, "image_prompts": [
        {"prompt": "a", "persona": ["Carmen Cortés"], "anio": "1990", "people_group": []},
        {"prompt": "b", "persona": ["Carmen Cortés"], "anio": "1990", "people_group": []}]}]}
    topic = {"id": "t", "documented_people": [sin_estado]}
    fm.generate_fotos_madre_personas(topic, "vid", visual)
    assert not [c for c in llamadas if c[0] == "estados"] and not (tmp_path / "vid" / "foto_madre" / "estados.json").exists()
    assert [c[1] for c in llamadas if c[0] == "variante"] == ["carmen_cort_s@sin_estado_23.png"]      # solo la edad


def test_llamar_estados_schema_y_cruce(monkeypatch):
    import claude_helpers
    vistos = []

    def call_json(prompt, **k):
        vistos.append((prompt, k))
        return [{"name": "Arcadio Fernandez", "tramo": "1981-1989", "estado_visible": "curled rigid fingers."},
                {"name": "Arcadio Fernandez", "tramo": "1981-1982", "estado_visible": "cruzado"}]   # par que no está en la entrada
    monkeypatch.setattr(claude_helpers, "call_json", call_json)
    filas = [{"name": "Arcadio Fernandez", "tramo": "1981-1989", "condition": "x"},
             {"name": "Carmen Cortés", "tramo": "1981-1982", "condition": "y"}]
    assert fm._llamar_estados(filas) == {("Arcadio Fernandez", "1981-1989"): "curled rigid fingers"}
    (prompt, k), = vistos
    assert prompt.startswith(fm.PROMPT_ESTADOS) and k["description"] == "foto madre estados" and k["model"] == "claude-opus-5-5"
    props = k["response_schema"]["items"]["properties"]
    assert props["name"]["enum"] == ["Arcadio Fernandez", "Carmen Cortés"] and props["tramo"]["enum"] == ["1981-1982", "1981-1989"]


def test_a_previas_mueve_todos_los_hermanos(tmp_path):
    for n in ("v@1.png", "v@1_native.png", "v@1.prompt.txt", "v@1.llamada.json"):
        (tmp_path / n).write_text(n, encoding="utf-8")
    assert fm._a_previas(tmp_path / "v@1.png", "_previas_x") == tmp_path / "_previas_x" / "v@1.png"
    assert sorted(x.name for x in tmp_path.iterdir()) == ["_previas_x"]
    (tmp_path / "v@1.png").write_text("otra", encoding="utf-8")
    assert fm._a_previas(tmp_path / "v@1.png", "_previas_x").name == "v@1_2.png"      # nada se pisa
    assert fm._a_previas(tmp_path / "no.png") is None
