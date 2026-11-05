# -*- coding: utf-8 -*-
"""F78a — madres de persona: identidad propia + variante por tramo (estado / edad) (HANDOFF_F78a_madres_identidad_estado).

Sin red: nada llama a fal ni a un LLM."""
from __future__ import annotations

import json
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
    p = fm._prompt_variante(fm.clave_de_foto(CARMEN, "2000"))
    assert p == ("The same person as in the reference image: same face, same features, same identity. Now a early-30s person. "
                 "Unable to work, living on a disability pension. Show only what of this would be visible on the body; if nothing "
                 "is visible, keep the person unchanged. Waist-up portrait framed so that the face and both hands are visible, "
                 "wearing a plain, clean, light-coloured shirt, plain mid-grey background, soft even light. A grainy 35mm "
                 "documentary photograph taken in 1992, with muted colors and slight underexposure, in a dark-history realist "
                 "style. No readable text, no signage, no labels.")
    sin_edad = fm._prompt_variante(fm.clave_de_foto(ARCADIO, "1985"))
    assert "Now a" not in sin_edad and "Deformed hands and upper body with disabling chronic pain. Show only" in sin_edad
    assert "taken in 1981" in sin_edad


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


def _fakes(monkeypatch, tmp_path, llamadas, rasgos_por_nombre):
    monkeypatch.setattr(fm, "OUTPUT_DIR", tmp_path)
    monkeypatch.setattr(fm.api, "image_engine", "nb2_lite", raising=False)
    monkeypatch.setattr(fm, "_llamar_rasgos", lambda entrada: (llamadas.append(("rasgos", [e["name"] for e in entrada])),
                                                               {e["name"]: rasgos_por_nombre[e["name"]] for e in entrada})[1])

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
    # cambian los rasgos de Carmen (entrada nueva): su madre y sus variantes van a _previas_f78a y se regeneran; Sancho Rof no
    topic["documented_people"][0]["role"] = "otra"
    rasgos["Carmen Cortés"] = "round face, short curly hair"
    fm.generate_fotos_madre_personas(topic, "vid", _visual78())
    assert ("madre", "carmen_cort_s.png") in [c[:2] for c in llamadas] and not [c for c in llamadas if c[1] == "jes_s_sancho_rof.png"]
    previas = sorted(p.name for p in (tmp_path / "vid" / "foto_madre" / "_previas_f78a").iterdir())
    assert previas == ["carmen_cort_s.png", "carmen_cort_s@1981-1982.png",
                       "carmen_cort_s@1981-1982_15.png", "carmen_cort_s@1992-2000_33.png"]
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
    assert (d / "_previas_f78a" / "jes_s_sancho_rof.png").read_bytes() == PNG78
    assert (d / "_previas_f78a" / "jes_s_sancho_rof.prompt.txt").read_text(encoding="utf-8") == "viejo"
    assert "y face" in (d / "jes_s_sancho_rof.png").read_bytes().decode("latin-1")


def test_rasgos_fallan_no_mueve_nada(tmp_path, monkeypatch):
    _fakes(monkeypatch, tmp_path, [], {})
    monkeypatch.setattr(fm, "_llamar_rasgos", lambda e: (_ for _ in ()).throw(RuntimeError("401")))
    d = tmp_path / "vid" / "foto_madre"
    d.mkdir(parents=True)
    (d / "jes_s_sancho_rof.png").write_bytes(PNG78)
    topic = {"id": "t", "documented_people": [dict(CARMEN), {**SANCHO, "foto_madre": str(d / "jes_s_sancho_rof.png")}]}
    est = fm.generate_fotos_madre_personas(topic, "vid", _visual78())
    assert (d / "jes_s_sancho_rof.png").exists() and not (d / "_previas_f78a").exists()
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
