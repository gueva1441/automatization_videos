"""
test_module_f38e_c.py — F38e §C (HANDOFF_F38e_lo_que_rompe_cualquier_video): el papel m01e-6 con `respaldo` y `autor`.
    §C.1  PANTALLA_SYSTEM = el bloque «Prompt nuevo (m01e-6-prueba), entero» de PRUEBA1_prompt_rotulos.md, letra por
          letra (md5 7d2ccdd2…); PROMPT_VERSION m01e-6; `prompt_md5` cambia con los formatos;
    §C.2  FORMATO_SALIDA y FORMATO_REINTENTO con `"respaldo"` después de `texto` y `"autor": "…" | null` después;
    §C.3  el respaldo tiene que ser fragmento literal del texto del ítem (regla `respaldo`, motivo del reintento que la
          vuelta siguiente puede arreglar); con respaldo válido el candado mira cifras y nombres contra el respaldo (la
          excepción de la oración ancla sigue); la cita sigue exigiendo frase literal;
    §C.4  el autor de una cita: «Municipio de Erto y Casso» (Q50) pasa; «Pietro Leone» (Q14) no → el del archivo, sin
          cortar; `caracteres` cuenta el que se muestra; el papel guarda `autor` y `autor_origen` y el .md lo dice;
    §C.5  la respuesta real de la prueba 1 (lab/hyperframes/f38/prueba1) y la corrida de esta parte (lab/hyperframes/
          f38e/c) pasan por `validar` sin ninguna caída por `respaldo`.
Sin API: el autor va con POST falsos. Nada de data/.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from script_engine import m01e_pantalla as mp  # noqa: E402
from script_engine.pantalla_colocar import caracteres  # noqa: E402

ROOT = Path(__file__).resolve().parent
F38 = ROOT / "lab" / "hyperframes" / "f38"
F38E_C = ROOT / "lab" / "hyperframes" / "f38e" / "c"
PROMPT_MD = F38 / "PRUEBA1_prompt_rotulos.md"
RAW_PRUEBA1 = F38 / "prueba1" / "prueba1.raw.json"
PAPEL_B4 = F38 / "b4" / "01e_pantalla.json"
FASE1 = F38 / "b2" / "fase1"
VAJONT = "f8s3-vajont"
MD5_SYSTEM = "7d2ccdd28055d6e621d1d251a0fe8bb7"      # F38e §C.1 (medido en F38e-0)
CLIMA = ["PÁNICO", "CALMA", "AMENAZA", "AVISO", "ALARMA", "INMINENTE", "COLAPSO", "SILENCIO", "RABIA", "MEMORIA"]
SEG = {"valor": 1.0, "oraciones": 10, "caps": 2, "voz": "prueba"}      # ancho: las oraciones del video chico son cortas
INSERTO = '"texto": "Más de 1 metro", "respaldo": "…", "autor": "…" | null, "aporta": "…"'
hay_prueba1 = pytest.mark.skipif(not RAW_PRUEBA1.exists() or not (FASE1 / VAJONT).exists(), reason="sin prueba 1 en lab/")


def _chico() -> dict:
    """Dos caps: ch01 gancho (dice 1963) y ch02 con un dato con dos cifras y dos citas (Q50 de Erto y Casso, Q14 de Leone)."""
    pool = {"datos": [{"id": "D1", "texto": "La presa mide 266 metros de alto y 190 de largo.", "fuente": "F", "fecha": "1960"},
                      {"id": "D2", "texto": "El embalse podía guardar 150 millones de metros cúbicos de agua.", "fuente": "F",
                       "fecha": "1960"}],
            "cronologia": [], "personajes": [],
            "citas": [{"id": "Q50", "texto": "Las poblaciones de Erto y Casso están viviendo en continua aprensión y en "
                                             "continua alarma", "autor": "Administración del comune di Erto e Casso",
                       "rol": "autoridad local", "fecha": "1962", "testimonio": False, "fuente": "F"},
                      {"id": "Q14", "texto": "Y justicia tendréis", "autor": "Giovanni Leone", "rol": "Presidente del Consiglio",
                       "fecha": "1963-10-12", "testimonio": False, "fuente": "F"}]}
    carga = {"topic_id": "t", "dir": Path("."), "titulos": {1: "Uno", 2: "Dos"}, "pool": pool,
             "escaleta": {"pico": {"beat": 2}, "a_pantalla": [],
                          "beats": [{"n": 1, "cap": 1, "funcion": "gancho", "dato_central": "", "datos_apoyo": []},
                                    {"n": 2, "cap": 2, "funcion": "escalada", "dato_central": "D1", "datos_apoyo": []}]},
             "parrafos": [{"cap": 1, "beat": 1, "texto": "Era el año mil novecientos sesenta y tres. La casa está a "
                                                        "oscuras. El valle duerme."},
                          {"cap": 2, "beat": 2, "texto": "El agua sube cada día. La montaña se mueve despacio. Nadie "
                                                        "quiere mirar la ladera. El muro mide doscientos sesenta y seis "
                                                        "metros."}]}
    ent = mp.entrada(carga, CLIMA, SEG)
    ent["_pool"] = pool
    return ent


def _ficha(cap: str, beat: int, pid: str, si: int, et: str, txt: str, respaldo: str | None, autor: str | None = None,
           palabra: str = "") -> dict:
    fi = {"pool_id": pid, "sentence_idx": si, "palabra": palabra, "etiqueta": et, "texto": txt, "aporta": "x"}
    if respaldo is not None:
        fi["respaldo"] = respaldo
    if autor is not None:
        fi["autor"] = autor
    return {"cap": cap, "beat": beat, "ficha": fi, "sello": None}


def _post_seq(resps: list[dict], pedidos: list[dict]):
    def post(body: dict) -> dict:
        pedidos.append(body)
        r = resps[min(len(pedidos) - 1, len(resps) - 1)]
        return {"content": [{"type": "text", "text": json.dumps(r, ensure_ascii=False)}],
                "usage": {"input_tokens": 1000, "output_tokens": 200}, "stop_reason": "end_turn"}
    return post


def _corte(v: dict, pid: str) -> dict | None:
    return next((d for d in v["descartados"] if d.get("pool_id") == pid and d.get("quien") == "validación"), None)


def _queda(v: dict, cap: str, beat: int) -> dict | None:
    return next(b for b in v["beats"] if b["cap"] == cap and b["beat"] == beat)["ficha"]


def _system_del_md() -> str:
    md = PROMPT_MD.read_text(encoding="utf-8")
    h = "## Prompt nuevo (m01e-6-prueba), entero\n"
    i = md.index(h) + len(h)
    a = md.index("```\n", i) + len("```\n")
    return md[a:md.index("\n```", a)]


# ═══════════════════════ §C.1 / §C.2 prompt y formato ═══════════════════════

def test_c1_prompt_es_el_bloque_del_md_letra_por_letra():
    assert mp.PROMPT_VERSION == "m01e-6"
    assert hashlib.md5(mp.PANTALLA_SYSTEM.encode("utf-8")).hexdigest() == MD5_SYSTEM
    if PROMPT_MD.exists():
        assert mp.PANTALLA_SYSTEM == _system_del_md()
    # lo que la prueba 1 cambió está, y lo de m01e-5 que reemplazó no
    assert "(d) se entiende solo, en 3 segundos" in mp.PANTALLA_SYSTEM
    assert "`respaldo`" in mp.PANTALLA_SYSTEM and "el autor va en español" in mp.PANTALLA_SYSTEM
    assert "tal como está en el archivo" not in mp.PANTALLA_SYSTEM and "el que tiene cifra o fecha" not in mp.PANTALLA_SYSTEM
    # la línea del gancho (F38b) sigue igual
    assert ("cualquier dato del archivo que la voz no diga en todo el video y que haga quedarse a quien mira: el gancho "
            "nunca queda sin ficha.") in mp.PANTALLA_SYSTEM


def test_c2_formatos_con_respaldo_y_autor(monkeypatch):
    assert mp.FORMATO_SALIDA.count(INSERTO) == 1 and mp.FORMATO_REINTENTO.count(INSERTO) == 1
    assert '"tipo": "voz_lo_dice" | "spoiler" | "repetido" | "otro"' in mp.FORMATO_SALIDA
    assert mp.FORMATO_REINTENTO.startswith('{"cambios": [{"cap": "ch03", "beat": 5, "ficha":')
    hoy = mp.prompt_md5()
    monkeypatch.setattr(mp, "FORMATO_REINTENTO", mp.FORMATO_REINTENTO.replace('"autor"', '"firma"'))
    assert mp.prompt_md5() != hoy                           # el md5 del prompt incluye los formatos nuevos
    monkeypatch.undo()
    assert mp.prompt_md5() == hoy


# ═══════════════════════ §C.3 respaldo ═══════════════════════

def test_c3a_sin_respaldo_o_no_literal_cae_con_regla_respaldo_y_es_motivo():
    ent = _chico()
    v = mp.validar({"beats": [_ficha("ch02", 2, "D1", 1, "ALTURA DE LA PRESA", "266 metros", None)]}, ent)
    d = _corte(v, "D1")
    assert d and d["regla"] == "respaldo" and "no trae `respaldo`" in d["motivo"]
    assert any(m.startswith("D1 (ch02 beat 2)") and "respaldo:" in m for m in v["motivos"])
    i = next(i for i, m in enumerate(v["motivos"]) if m.startswith("D1 (ch02 beat 2)"))
    assert v["motivos_beat"][i] == [("ch02", 2)]
    v2 = mp.validar({"beats": [_ficha("ch02", 2, "D1", 1, "ALTURA DE LA PRESA", "266 metros", "mide 266 m de alto")]}, ent)
    d2 = _corte(v2, "D1")
    assert d2 and d2["regla"] == "respaldo" and "no es un fragmento literal" in d2["motivo"]
    # válido: con la normalización del candado (mayúsculas, tildes, espacios)
    v3 = mp.validar({"beats": [_ficha("ch02", 2, "D1", 1, "ALTURA DE LA PRESA", "266 metros", "MIDE  266 metros")]}, ent)
    assert _corte(v3, "D1") is None and _queda(v3, "ch02", 2)["respaldo"] == "MIDE 266 metros"


def test_c3b_el_candado_mira_contra_el_respaldo_y_la_ancla_sigue_valiendo():
    ent = _chico()
    # la cifra está en el texto del ítem pero no en el respaldo elegido → candado
    v = mp.validar({"beats": [_ficha("ch02", 2, "D1", 1, "ALTURA DE LA PRESA", "266 metros", "190 de largo")]}, ent)
    d = _corte(v, "D1")
    assert d and d["regla"] == "candado" and "266" in d["motivo"]
    # con el respaldo que la trae, pasa
    v2 = mp.validar({"beats": [_ficha("ch02", 2, "D1", 1, "ALTURA DE LA PRESA", "266 metros", "mide 266 metros")]}, ent)
    assert _corte(v2, "D1") is None
    # la excepción de la oración ancla (F34 §A.2.1): la oración [3] dice «doscientos sesenta y seis» → no corta el candado
    v3 = mp.validar({"beats": [_ficha("ch02", 2, "D1", 3, "ALTURA DE LA PRESA", "266 metros", "190 de largo")]}, ent)
    assert _corte(v3, "D1") is None
    # la etiqueta también se mira contra el respaldo (y la fuente del dato)
    v4 = mp.validar({"beats": [_ficha("ch02", 2, "D1", 1, "PRESA DE 190 METROS", "266 metros", "mide 266 metros")]}, ent)
    d4 = _corte(v4, "D1")
    assert d4 and d4["regla"] == "candado" and "190" in d4["motivo"]


def test_c3c_la_cita_sigue_exigiendo_frase_literal():
    ent = _chico()
    f = _ficha("ch02", 2, "Q14", 1, "LA RESPUESTA", "«Y justicia habrá»", "Y justicia tendréis", "Giovanni Leone")
    v = mp.validar({"beats": [f]}, ent)
    d = _corte(v, "Q14")
    assert d and d["regla"] == "candado" and "no es literal" in d["motivo"]
    f2 = _ficha("ch02", 2, "Q14", 1, "LA RESPUESTA", "«Y justicia tendréis»", "Y justicia tendréis", "Giovanni Leone")
    assert _corte(mp.validar({"beats": [f2]}, ent), "Q14") is None


def test_c3_respaldo_invalido_es_motivo_de_la_vuelta_y_la_vuelta_lo_arregla(tmp_path):
    ent = _chico()
    gancho = _ficha("ch01", 1, "D2", 1, "LO QUE GUARDABA EL EMBALSE", "150 millones de metros cúbicos",
                    "150 millones de metros cúbicos")               # el gancho con ficha: el único motivo es el de D1
    # el largo (190): la voz no lo dice en ningún lado (el alto, 266, lo dice la oración [3] y sería una pregunta más)
    sin = {"beats": [gancho, _ficha("ch02", 2, "D1", 1, "LARGO DE LA PRESA", "190 metros", None)]}
    con = {"cambios": [_ficha("ch02", 2, "D1", 1, "LARGO DE LA PRESA", "190 metros", "190 de largo")]}
    pedidos: list[dict] = []
    res = mp.llamar(ent, tmp_path / "a", tope=100.0, post=_post_seq([sin, con], pedidos))
    assert len(pedidos) == 2
    p2 = pedidos[1]["messages"][0]["content"]
    assert "respaldo: la ficha no trae `respaldo`" in p2 and "ch02 beat 2" in p2 and mp.FORMATO_REINTENTO in p2
    assert res["reintento"]["cierre"] == "sin motivos" and res["reintento"]["cortados_al_cierre"] == []
    q = _queda(res["validacion"], "ch02", 2)
    assert q and q["pool_id"] == "D1" and q["respaldo"] == "190 de largo"
    # si la vuelta no lo arregla (misma respuesta), cierra sin progreso y D1 queda caída por `respaldo`
    pedidos2: list[dict] = []
    res2 = mp.llamar(ent, tmp_path / "b", tope=100.0,
                     post=_post_seq([sin, {"cambios": [sin["beats"][1]]}], pedidos2))
    assert len(pedidos2) == 2 and res2["reintento"]["cierre"] == "sin progreso"
    assert _corte(res2["validacion"], "D1")["regla"] == "respaldo"


# ═══════════════════════ §C.4 autor ═══════════════════════

def test_c4_municipio_de_erto_y_casso_pasa_y_caracteres_lo_cuenta():
    ent = _chico()
    et, txt, au = "LO QUE DECÍAN", "en continua aprensión y en continua alarma", "Municipio de Erto y Casso"
    f = _ficha("ch02", 2, "Q50", 3, et, f"«{txt}»", txt, au)       # [3]: caben 90 (13 + 42 + 25 + 5 = 85)
    v = mp.validar({"beats": [f]}, ent)
    assert _corte(v, "Q50") is None
    q = _queda(v, "ch02", 2)
    assert q["autor"] == au and q["autor_origen"] == "modelo"
    assert q["caracteres"] == caracteres("cita", et, txt, au) == len(et) + len(txt) + len(au) + 5
    md = mp.a_markdown(mp.armar(ent, {"validacion": v, "modelo": "m", "effort": "e", "intentos": []}))
    assert f"— {au} (autor: modelo)" in md and f"respaldo: «{txt}»" in md


def test_c4_pietro_leone_no_pasa_y_se_muestra_el_del_archivo_sin_cortar():
    ent = _chico()
    f = _ficha("ch02", 2, "Q14", 1, "LA RESPUESTA", "«Y justicia tendréis»", "Y justicia tendréis", "Pietro Leone")
    v = mp.validar({"beats": [f]}, ent)
    assert _corte(v, "Q14") is None
    q = _queda(v, "ch02", 2)
    assert q["autor"] == "Giovanni Leone" and q["autor_origen"].startswith("archivo:") and "Pietro" in q["autor_origen"]
    assert q["caracteres"] == caracteres("cita", "LA RESPUESTA", "Y justicia tendréis", "Giovanni Leone")
    md = mp.a_markdown(mp.armar(ent, {"validacion": v, "modelo": "m", "effort": "e", "intentos": []}))
    assert "— Giovanni Leone (autor: archivo:" in md
    # sin `autor` (null) → el del archivo, anotado; «Giovanni Leone» del modelo → modelo
    f0 = _ficha("ch02", 2, "Q14", 1, "LA RESPUESTA", "«Y justicia tendréis»", "Y justicia tendréis")
    q0 = _queda(mp.validar({"beats": [f0]}, ent), "ch02", 2)
    assert q0["autor"] == "Giovanni Leone" and q0["autor_origen"] == "archivo: el autor no escribió `autor`"
    f1 = _ficha("ch02", 2, "Q14", 1, "LA RESPUESTA", "«Y justicia tendréis»", "Y justicia tendréis", "Giovanni Leone")
    assert _queda(mp.validar({"beats": [f1]}, ent), "ch02", 2)["autor_origen"] == "modelo"
    # el autor del modelo se mide en `caben`: uno largo que no cabe cae por caben con su largo
    largo = "Giovanni Leone, presidente del Consejo de Ministros de la República Italiana en mil novecientos sesenta y tres"
    f2 = _ficha("ch02", 2, "Q14", 1, "LA RESPUESTA", "«Y justicia tendréis»", "Y justicia tendréis", largo)
    v2 = mp.validar({"beats": [f2]}, ent)
    assert _corte(v2, "Q14") is None or _corte(v2, "Q14")["regla"] == "caben"


def test_c4_autor_mostrado_y_sus_nombres():
    x50 = {"autor": "Administración del comune di Erto e Casso", "rol": "autoridad local",
           "texto": "Las poblaciones de Erto y Casso están viviendo en continua aprensión"}
    x14 = {"autor": "Giovanni Leone", "rol": "Presidente del Consiglio", "texto": "Y justicia tendréis"}
    assert mp._nombres_del_autor("Municipio de Erto y Casso") == ["Erto", "Casso"]
    assert mp._nombres_del_autor("Pietro Leone") == ["Pietro", "Leone"]
    assert mp._nombres_del_autor("Presidente del Consejo") == ["Consejo"]
    assert mp.autor_mostrado("Municipio de Erto y Casso", x50) == ("Municipio de Erto y Casso", "modelo")
    assert mp.autor_mostrado("Pietro Leone", x14)[0] == "Giovanni Leone"
    assert mp.autor_mostrado("Giovanni Leone", x14) == ("Giovanni Leone", "modelo")
    assert mp.autor_mostrado("", x14) == ("Giovanni Leone", "archivo: el autor no escribió `autor`")
    a, o = mp.autor_mostrado("Giovanni Leone, presidente del Consejo", x14)
    assert a == "Giovanni Leone" and "Consejo" in o           # «Consejo» no está en el archivo (dice «Consiglio»)


# ═══════════════════════ §C.5 Vajont: la prueba 1 y la corrida de esta parte ═══════════════════════

@pytest.fixture(scope="module")
def vajont() -> dict:
    carga = mp.cargar(VAJONT, FASE1)
    papel = json.loads(PAPEL_B4.read_text(encoding="utf-8"))
    ent = mp.entrada(carga, CLIMA, papel["seg_por_palabra"])
    ent["_pool"] = carga["pool"]
    return ent


@hay_prueba1
def test_c5_la_respuesta_de_la_prueba_1_no_cae_por_respaldo(vajont):
    resp = json.loads(RAW_PRUEBA1.read_text(encoding="utf-8"))["respuesta"]
    v = mp.validar(resp, vajont, final=False)
    assert not [d for d in v["descartados"] if d.get("regla") == "respaldo"]
    quedan = [b["ficha"] for b in v["beats"] if b["ficha"]]
    assert len(quedan) == 9 and all(f["respaldo"] for f in quedan)
    # las tres citas caen como en F38e-0 (el autor metido en el dato) → candado, no respaldo
    assert {d["pool_id"] for d in v["descartados"] if d.get("quien") == "validación"} == {"Q50", "Q51", "Q14"}
    assert all(d["regla"] == "candado" for d in v["descartados"] if d.get("quien") == "validación")
    # con el formato nuevo (el autor en su campo) Q50 entra con «Municipio de Erto y Casso» y Q14 con el del archivo
    r2 = json.loads(json.dumps(resp, ensure_ascii=False))
    for b in r2["beats"]:
        fi = b.get("ficha")
        if fi and str(fi["pool_id"]).startswith("Q") and " — " in fi["texto"]:
            fi["texto"], fi["autor"] = fi["texto"].split(" — ", 1)
    v2 = mp.validar(r2, vajont, final=False)
    q50 = _queda(v2, "ch05", 8)
    assert q50 and q50["pool_id"] == "Q50" and q50["autor"] == "Municipio de Erto y Casso" and q50["autor_origen"] == "modelo"
    assert q50["caracteres"] == 13 + 42 + 25 + 5 <= q50["caben"]
    q14 = _queda(v2, "ch07", 12)
    assert q14 and q14["autor"] == "Giovanni Leone" and q14["autor_origen"].startswith("archivo:")
    q51 = _queda(v2, "ch05", 9)
    assert q51 and q51["autor"] == "Alberico Biadene" and q51["autor_origen"] == "modelo"


@pytest.mark.skipif(not (F38E_C / "01e_pantalla.json").exists(), reason="sin la corrida de F38e §C en lab/")
def test_c5_la_corrida_de_f38e_c_es_del_formato_nuevo():
    from script_engine import evidence as ev
    p = json.loads((F38E_C / "01e_pantalla.json").read_text(encoding="utf-8"))
    assert p["prompt_version"] == "m01e-6" and p["prompt_md5"] == mp.prompt_md5()
    arch = {x["id"]: x for x in json.loads((F38E_C / "01e_pantalla.raw.json").read_text(encoding="utf-8"))["entrada"]["archivo"]}
    for b in p["beats"]:
        f = b.get("ficha")
        if not f:
            continue
        assert f["respaldo"] and ev.norm(f["respaldo"]) in ev.norm(arch[f["pool_id"]]["texto"])
        if f["estilo"] == "cita":
            assert f["autor"] and (f["autor_origen"] == "modelo" or f["autor_origen"].startswith("archivo:"))
            assert f["caracteres"] == caracteres("cita", f["etiqueta"], f["texto"], f["autor"])
