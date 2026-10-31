"""
test_module_f64.py — F64 (HANDOFF_F64_papel_a_produccion; DECISIONES 2026-10-31 13:07, 14:16, 14:20): el papel a
producción.
    Etapa 0  (e) la entrada completa: todo el pool entra al archivo (D con o sin cifra, T, Q, P, L), cada ítem con
             `contexto_fuente` al final, los beats con emoción/imagen/pregunta/paga, `escaleta_video` y `disputas`; un
             `ficha_caso.json` ausente no rompe (disputas {}); un L propuesto como ficha sale `normal`; el SYSTEM es el
             de m01e-6 con la oración 2 de F63 A.2 (md5 85d094be…); Opus medium, m01e-7.
    Etapa 1  sin tope en dólares: no quedan TopePantalla, tope_usd, _peor_usd ni «tope» en el raw/.json/.md; gfx_config
             ya no acepta la clave `costos`; chascada: importar error_handler en un proceso nuevo no crea logs/*.log.
    Etapa 2  (d) `momentos` por máximo del cap: un recuerdo de un año anterior no baja el relato; el cap sin año hereda
             el del anterior; el heredado no entra al máximo; las oraciones del beat flash-forward no cuentan.
Sin API. Un video chico armado acá (nada de data/).
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from script_engine import m01e_pantalla as mp  # noqa: E402

CLIMA = ["PÁNICO", "CALMA", "AMENAZA", "AVISO", "ALARMA", "INMINENTE", "COLAPSO", "SILENCIO", "RABIA", "MEMORIA"]
SEG = {"valor": 0.3459, "oraciones": 200, "caps": 9, "voz": "prueba"}
MD5_SYSTEM_F64 = "85d094bed6090b14d1802ca97433d982"      # F63 A.2, medido (HANDOFF_F64 Constantes)


def _pool() -> dict:
    return {"datos": [{"id": "D1", "texto": "La presa mide 266 metros de alto.", "fuente": "F", "fecha": "1960",
                       "cita_literal": "the dam is  266 m high"},
                      {"id": "D2", "texto": "El valle quedó vacío.", "fuente": "F", "fecha": "1964",
                       "evidencia": [{"doc_id": "x", "offset": 3, "cita_literal": "the valley was left empty"}]}],
            "cronologia": [{"id": "T1", "texto": "Se llena el embalse.", "fecha": "1962", "fuente": "F"}],
            "personajes": [{"id": "P1", "nombre": "Carlo Semenza", "rol": "ingeniero jefe", "fuente": "F"}],
            "lugares": [{"id": "L1", "nombre": "Monte Toc", "rol": "La montaña que se vino abajo.", "fuente": "F"}],
            "citas": [{"id": "Q1", "texto": "Nadie nos avisó nunca", "autor": "Un sobreviviente", "rol": "vecino",
                       "fecha": "1990", "testimonio": True, "fuente": "F"}]}


def _carga(ficha: dict | None) -> dict:
    """Un video de dos caps y dos beats, con (o sin) ficha del caso."""
    return {"topic_id": "t", "dir": Path("."), "titulos": {1: "Uno", 2: "Dos"}, "pool": _pool(), "ficha_caso": ficha,
            "escaleta": {"pico": {"beat": 2}, "a_pantalla": [], "promesa_gancho": "¿qué cayó?", "loops": ["la carta"],
                         "recuerda_loop": None, "humano": "Tina", "antagonista": "SADE", "cierre_humano": "vuelve",
                         "beats": [{"n": 1, "cap": 1, "funcion": "gancho", "dato_central": "", "datos_apoyo": [],
                                    "emocion": "vértigo", "imagen_sensorial": "el agua negra",
                                    "pregunta_abierta": "¿quién sabía?", "paga": "beat 2", "flash_forward": True},
                                   {"n": 2, "cap": 2, "funcion": "escalada", "dato_central": "D1", "datos_apoyo": ["T1"],
                                    "emocion": "miedo"}]},
            "parrafos": [{"cap": 1, "beat": 1, "texto": "Era el año mil novecientos sesenta y tres. La casa está a "
                                                       "oscuras. El valle duerme."},
                         {"cap": 2, "beat": 2, "texto": "El agua sube cada día. La montaña se mueve despacio. Nadie "
                                                       "quiere mirar la ladera."}]}


@pytest.fixture(scope="module")
def ent() -> dict:
    e = mp.entrada(_carga({"versiones": [{"a": 1}], "contradicciones": [{"b": 2}], "otra": "cosa"}), CLIMA, SEG)
    e["_pool"] = _pool()
    return e


# ═══════════════════════ Etapa 0 (e): la entrada completa ═══════════════════════

def test_e0_modelo_effort_version_y_system():
    assert (mp.MODELO, mp.EFFORT, mp.PROMPT_VERSION) == ("claude-opus-5-5", "medium", "m01e-7")
    assert hashlib.md5(mp.PANTALLA_SYSTEM.encode("utf-8")).hexdigest() == MD5_SYSTEM_F64
    assert "`contexto_fuente`" in mp.PANTALLA_SYSTEM and "`disputas`" in mp.PANTALLA_SYSTEM
    assert mp.PANTALLA_SYSTEM.count("Recibís la narración completa") == 1


def test_e1_todo_el_pool_entra_al_archivo_con_contexto_fuente_al_final(ent):
    ids = [x["id"] for x in ent["archivo"]]
    assert set(ids) == {"D1", "D2", "T1", "P1", "L1", "Q1"}            # D2 sin cifra y L1 también (antes no entraban)
    for x in ent["archivo"]:
        assert list(x)[-1] == "contexto_fuente"                        # (a) al final del ítem
    arch = {x["id"]: x for x in ent["archivo"]}
    assert arch["D1"]["contexto_fuente"] == "the dam is 266 m high"     # cita_literal, espacios normalizados
    assert arch["D2"]["contexto_fuente"] == "the valley was left empty" # la de la primera evidencia
    assert arch["T1"]["contexto_fuente"] == "" and arch["L1"]["texto"] == "Monte Toc — La montaña que se vino abajo."
    assert arch["P1"]["texto"] == "Carlo Semenza — ingeniero jefe"
    assert list(arch["Q1"])[:8] == ["id", "texto", "fuente", "fecha", "beats_que_lo_cuentan", "autor", "rol", "testimonio"]


def test_e2_beats_escaleta_video_y_disputas_en_orden(ent):
    b1 = ent["beats"][0]
    assert list(b1) == ["n", "cap", "funcion", "pico", "dato_central", "apoyo", "cierre", "emocion", "imagen_sensorial",
                        "pregunta_abierta", "paga", "flash_forward"]   # (b) después de `cierre`, en ese orden (+ Etapa 2)
    assert b1["flash_forward"] is True and ent["beats"][1]["flash_forward"] is False
    assert (b1["emocion"], b1["paga"]) == ("vértigo", "beat 2") and ent["beats"][1]["paga"] is None
    pm = mp._para_modelo(ent)
    assert list(pm) == ["caps", "beats", "archivo", "clima", "escaleta_video", "disputas"]      # (c)
    assert list(pm["escaleta_video"]) == ["promesa_gancho", "loops", "recuerda_loop", "pico", "humano", "antagonista",
                                          "cierre_humano"]              # (d) los 7, None donde falte
    assert pm["escaleta_video"]["recuerda_loop"] is None and pm["escaleta_video"]["pico"] == {"beat": 2}
    assert pm["disputas"] == {"versiones": [{"a": 1}], "contradicciones": [{"b": 2}]}   # solo esas dos claves
    assert "flash_forward" not in json.dumps(pm)                        # lo que el autor no ve


def test_e3_sin_ficha_caso_no_rompe_y_cargar_lo_anota(tmp_path):
    e = mp.entrada(_carga(None), CLIMA, SEG)
    assert e["disputas"] == {} and mp._para_modelo(e)["disputas"] == {}
    # `cargar` sobre un topic sin ficha_caso.json: None + una línea en el log
    sd = tmp_path / "t"
    sd.mkdir()
    c = _carga(None)
    (sd / "01a_skeleton.json").write_text(json.dumps({"chapters": [{"chapter_number": 1, "title": "Uno"}]}), encoding="utf-8")
    (sd / "01a_escaleta.json").write_text(json.dumps(c["escaleta"]), encoding="utf-8")
    (sd / "01b_narracion_v3.json").write_text(json.dumps({"parrafos": c["parrafos"]}), encoding="utf-8")
    (sd / "00_pool_v3.json").write_text(json.dumps(_pool()), encoding="utf-8")
    log: list[str] = []
    carga = mp.cargar("t", tmp_path, log=log)
    assert carga["ficha_caso"] is None and len(log) == 1 and "ficha_caso.json" in log[0] and "disputas" in log[0]
    (sd / "ficha_caso.json").write_text(json.dumps({"versiones": [], "contradicciones": [1]}), encoding="utf-8")
    assert mp.cargar("t", tmp_path)["ficha_caso"] == {"versiones": [], "contradicciones": [1]}


def test_e4_un_lugar_propuesto_como_ficha_sale_normal(ent):
    assert mp.estilo_de("L1", "LA MONTAÑA") == "normal" and mp.estilo_de("L1", "EL INFORME DEL MONTE") == "papel"
    resp = {"beats": [{"cap": "ch02", "beat": 2, "ficha": {"pool_id": "L1", "sentence_idx": 1, "palabra": "montaña",
                                                           "etiqueta": "LA MONTAÑA", "texto": "Monte Toc",
                                                           "respaldo": "Monte Toc", "autor": None, "aporta": "x"},
                       "sello": None}]}
    v = mp.validar(resp, ent)
    s = next(b for b in v["beats"] if b["cap"] == "ch02" and b["beat"] == 2)
    assert s["ficha"] and s["ficha"]["pool_id"] == "L1" and s["ficha"]["estilo"] == "normal"
    assert not [d for d in v["descartados"] if d.get("pool_id") == "L1"]
    # voz_no_lo_dice tolera un L (sin cifras: por sus nombres)
    it = next(i for i in _pool()["lugares"] if i["id"] == "L1")
    it["_kind"] = "lugares"
    assert mp.voz_no_lo_dice(it, "la montaña se mueve", ent.get("anios")) == ["Toc"]   # `nombres` no ve el que abre
    assert mp.voz_no_lo_dice(it, "el Monte Toc se mueve", ent.get("anios")) is None


# ═══════════════════════ Etapa 1: sin tope ═══════════════════════

def _post_seq(resps: list[dict], pedidos: list[dict]):
    """POST falso: la llamada k devuelve resps[k] (la última se repite)."""
    def post(body: dict) -> dict:
        pedidos.append(body)
        r = resps[min(len(pedidos) - 1, len(resps) - 1)]
        return {"content": [{"type": "text", "text": json.dumps(r, ensure_ascii=False)}],
                "usage": {"input_tokens": 1000, "output_tokens": 200}, "stop_reason": "end_turn"}
    return post


def test_e1_sin_tope_en_el_codigo_ni_en_la_salida(ent, tmp_path):
    for n in ("TopePantalla", "tope_usd", "TOPE_USD_RESPALDO", "_peor_usd", "OUT_TOKENS_PEOR"):
        assert not hasattr(mp, n), n
    assert "tope" not in mp.llamar.__code__.co_varnames
    pedidos: list[dict] = []
    res = mp.llamar(ent, tmp_path, post=_post_seq([{"beats": []}], pedidos))
    assert "tope" not in res and "tope" not in (res.get("error") or "")
    p = mp.armar(ent, res)
    assert "tope" not in p
    assert "tope" not in mp.a_markdown(p).lower()
    raw = json.loads((tmp_path / f"{mp.ARCHIVO}.raw.json").read_text(encoding="utf-8"))
    assert "tope" not in raw and raw["usd"] > 0                      # el costo se informa, no frena


def test_e1_gfx_config_sin_la_clave_costos():
    import gfx_config
    assert "costos" not in gfx_config._PROFILE_KEYS
    src = Path(gfx_config.__file__).read_text(encoding="utf-8")
    assert "m01e_tope_usd" not in src.split("F64 Etapa 1")[0] and 'bad.add("costos' not in src


def test_e1_fase1_5_solo_atrapa_sin_json():
    src = Path(__file__).resolve().parent.joinpath("fase1_5.py").read_text(encoding="utf-8")
    assert "TopePantalla" not in src and "except mp.SinJSON as e:" in src


def test_e1_chascada_importar_error_handler_no_crea_log(tmp_path):
    import subprocess
    import sys as _sys
    root = Path(__file__).resolve().parent
    tmp = tmp_path.as_posix()
    code = ("import sys, pathlib; sys.path.insert(0, %r); import config; antes = set(config.LOGS_DIR.glob('*.log')); "
            "import error_handler as eh; tmp = pathlib.Path(%r); h = eh.ErrorHandler(log_dir=tmp); "
            "print('NUEVOS', sorted(p.name for p in set(config.LOGS_DIR.glob('*.log')) - antes), "
            "'TMP', sorted(p.name for p in tmp.glob('*.log'))); "
            "h.logger.info('hola'); print('ESCRITO', sorted(p.name for p in tmp.glob('*.log')))") % (str(root), tmp)
    r = subprocess.run([_sys.executable, "-c", code], capture_output=True, text=True, encoding="utf-8", cwd=str(root))
    assert r.returncode == 0, r.stderr
    out = r.stdout.strip().splitlines()
    assert out[0] == "NUEVOS [] TMP []", out                          # ni el import ni construir el handler crean archivos
    assert out[1].startswith("ESCRITO ['pipeline_"), out              # y cuando sí escribe, el archivo existe


# ═══════════════════════ Etapa 2 (d): el año del relato ═══════════════════════

def _ent_anios() -> dict:
    """Cuatro caps: ch01 gancho flash-forward (dice 2024); ch02 1961, 1962, recuerda 1950; ch03 sin año (hereda);
    ch04 hereda 1962 y después dice 1943 (el heredado no entra al máximo)."""
    pool = {"datos": [{"id": "D1", "texto": "La presa mide 266 metros.", "fuente": "F", "fecha": "1930"},
                      {"id": "D2", "texto": "Murieron 2000 personas.", "fuente": "F", "fecha": "2026"}],
            "cronologia": [], "personajes": [], "lugares": [], "citas": []}
    beats = [{"n": 1, "cap": 1, "funcion": "gancho", "dato_central": "", "datos_apoyo": [], "flash_forward": True},
             {"n": 2, "cap": 2, "funcion": "planteo", "dato_central": "", "datos_apoyo": []},
             {"n": 3, "cap": 3, "funcion": "escalada", "dato_central": "", "datos_apoyo": []},
             {"n": 4, "cap": 4, "funcion": "giro", "dato_central": "", "datos_apoyo": []}]
    pars = [{"cap": 1, "beat": 1, "texto": "Hoy, en 2024, el valle sigue vacío. Nadie volvió."},
            {"cap": 2, "beat": 2, "texto": "El baile fue en 1961. Se casaron en 1962. El acuerdo venía desde 1950. "
                                           "Cruzaron el mar."},
            {"cap": 3, "beat": 3, "texto": "El agua sube. La montaña se mueve."},
            {"cap": 4, "beat": 4, "texto": "Nadie miraba. En 1943 la empresa compró la mina. En 1948 llegó un médico."}]
    carga = {"topic_id": "t", "dir": Path("."), "titulos": {1: "", 2: "", 3: "", 4: ""}, "pool": pool, "ficha_caso": None,
             "escaleta": {"pico": {"beat": 4}, "a_pantalla": [], "beats": beats}, "parrafos": pars}
    e = mp.entrada(carga, CLIMA, SEG)
    e["_pool"] = pool
    return e


def test_d1_momentos_maximo_del_cap_herencia_y_flash_forward():
    e = _ent_anios()
    assert [b["flash_forward"] for b in e["beats"]] == [True, False, False, False]
    m = mp.momentos(e)
    assert m[("ch01", 0)] is None and m[("ch01", 1)] is None            # el 2024 del gancho flash-forward no cuenta
    assert m[("ch02", 0)] == 1961 and m[("ch02", 1)] == 1962
    assert m[("ch02", 2)] == 1962                                       # el recuerdo de 1950 no baja el relato (máximo)
    assert m[("ch02", 3)] == 1962
    assert m[("ch03", 0)] == 1962 and m[("ch03", 1)] == 1962            # hereda mientras no dice ninguno
    assert m[("ch04", 0)] == 1962                                       # heredado…
    assert m[("ch04", 1)] == 1943                                       # …que NO entra al máximo: el cap manda
    assert m[("ch04", 2)] == 1948
    d = mp.momentos_detalle(e)
    assert d[("ch03", 0)] == {"anio": 1962, "cap": "ch02", "idx": 1, "heredado": True}
    assert d[("ch02", 2)] == {"anio": 1962, "cap": "ch02", "idx": 1, "heredado": False}
    assert d[("ch01", 0)] == {"anio": None, "cap": None, "idx": None, "heredado": True}


def test_d2_fecha_relato_usa_el_maximo_y_el_gancho_queda_libre():
    e = _ent_anios()
    # D2 (2026) en el gancho: sin año de relato → el filtro no actúa (el gancho puede traer cualquier dato)
    g = {"beats": [{"cap": "ch01", "beat": 1, "ficha": {"pool_id": "D2", "sentence_idx": 1, "palabra": "Nadie",
                                                        "etiqueta": "HOY", "texto": "2000 muertos", "respaldo": "2000 personas",
                                                        "autor": None, "aporta": "x"}, "sello": None}]}
    v = mp.validar(g, e)
    assert not [d for d in v["descartados"] if d.get("regla") == "fecha_relato"]
    # D2 (2026) en ch02 [3]: relato 1962 → cae por fecha_relato, y el motivo dice la regla nueva
    f = {"beats": [{"cap": "ch02", "beat": 2, "ficha": {**g["beats"][0]["ficha"], "sentence_idx": 3, "palabra": "mar"},
                    "sello": None}]}
    d = next(d for d in mp.validar(f, e)["descartados"] if d.get("pool_id") == "D2")
    assert d["regla"] == "fecha_relato" and "1962" in d["motivo"] and "año más alto" in d["motivo"]
