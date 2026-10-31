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
    Etapa 3  (a) `pantalla_verificador.pedido` puro y estable (md5 fijo; una Q lleva dato_archivo = frase de la ficha y
             cita_completa); (b) `_leer`: desconocido se ignora, faltante = pasa «sin veredicto»; (c) `validar` con juez
             falso: «corta» → descartados quien verificador y fuera de usados_ids, «pasa» → juicio_verificador, descarte
             «no_dicho» sigue en vuelven y «dicho» no, sin marcas no se llama; (f) `llamar` con post y juez falsos: sin
             tope, cierres «sin motivos» y «sin progreso» por claves (mismas claves con motivo de texto distinto; ciclo
             A→B→A), el verificador una vez por validación con marcas, el juez por defecto usa el `post` falso; (g) hit de
             caché con `pedido_md5` guardado: el juez real no se llama; caché parcial sí.
    F65a Etapa B (DECISIONES 2026-10-31 15:49; HANDOFF §2.3) Fase 2 respeta al verificador: `pantalla_filtros.validar_papel`
             no corta una ficha cuyo `juicio_verificador.tokens[regla]` trae la coincidencia (`no_dicho` «Australia»),
             la misma ficha sin juicio cae con regla `no_dicho`; `contradicciones(..., juicio=tokens)` no marca la
             cifra que el verificador pasó (COTA 720 m vs «setecientos quince metros» con «715» juzgado → []).
Sin API: todo `validar`/`llamar` de este archivo pasa un `juez` falso (sin él se llamaría al verificador real). Un video chico armado acá (nada de data/); el de la Etapa B va con palabras con tiempos como en test_module_f37b_colocar.
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



def _txt(body: dict) -> str:
    """F65b: el USER del autor va en bloques (caché); el texto entero."""
    c = body["messages"][0]["content"]
    return c if isinstance(c, str) else "".join(b["text"] for b in c)


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
    g = {"beats": [{"cap": "ch01", "beat": 1, "ficha": {"pool_id": "D2", "sentence_idx": 0, "palabra": "valle",
                                                        "etiqueta": "HOY", "texto": "2000 muertos", "respaldo": "2000 personas",
                                                        "autor": None, "aporta": "x"}, "sello": None}]}
    marcas: list[list] = []

    def juez(ms, caps):
        marcas.append(ms)
        return {"veredictos_fichas": [], "veredictos_descartes": []}
    v = mp.validar(g, e, juez=juez)
    assert not [m for ms in marcas for m in ms if m["regla"] == "fecha_relato"] and not v["descartados"]
    # D2 (2026) en ch02 [3]: relato 1962 → marca `fecha_relato` para el verificador (Etapa 3), con el máximo y dónde se dijo
    f = {"beats": [{"cap": "ch02", "beat": 2, "ficha": {**g["beats"][0]["ficha"], "sentence_idx": 3, "palabra": "mar"},
                    "sello": None}]}
    marcas.clear()
    mp.validar(f, e, juez=juez)
    m = next(m for ms in marcas for m in ms if m["regla"] == "fecha_relato")
    assert m["pool_id"] == "D2" and m["coincidencia"] == {"token": "2026", "relato": 1962, "cap": "ch02", "idx": 1,
                                                          "oracion": "Se casaron en 1962."}


# ═══════════════════════ Etapa 3: el verificador decide los cortes ═══════════════════════

from script_engine import pantalla_verificador as pv  # noqa: E402

SEG_ANCHO = {"valor": 1.0, "oraciones": 10, "caps": 2, "voz": "prueba"}      # las oraciones del video chico son cortas
MD5_PEDIDO_JUGUETE = "848621c94d364db29d92a0e7002a737f"      # md5 de pv.pedido(MARCAS_JUGUETE, CAPS_JUGUETE), fijo (a)
MD5_SYSTEM_V = "104b9ea817690c5b45afbe74f87a2111"          # md5 del SYSTEM literal del handoff


def _pool_v() -> dict:
    return {"datos": [{"id": "D1", "texto": "La presa mide 266 metros.", "fuente": "F", "fecha": "1930"},
                      {"id": "D2", "texto": "Murieron 2000 personas.", "fuente": "F", "fecha": "2026"},
                      {"id": "D3", "texto": "Cruzaron cerca de 8000 españoles.", "fuente": "F", "fecha": "1960"},
                      {"id": "D4", "texto": "El acuerdo se firmó en 1958.", "fuente": "F", "fecha": "1958"}],
            "cronologia": [], "personajes": [], "lugares": [],
            "citas": [{"id": "Q1", "texto": "Nadie nos avisó nunca de nada", "autor": "Una vecina", "rol": "vecina",
                       "fecha": "1990", "testimonio": True, "fuente": "F"}]}


def _ent_v() -> dict:
    """Dos caps, tres beats: gancho flash-forward (ch01), planteo y pico (ch02). La voz dice «ocho mil españoles»
    (D3 «8000» → marca no_dicho) y no dice «266» (D1 descartado «voz_lo_dice» → marca voz_lo_dice)."""
    beats = [{"n": 1, "cap": 1, "funcion": "gancho", "dato_central": "", "datos_apoyo": [], "flash_forward": True},
             {"n": 2, "cap": 2, "funcion": "planteo", "dato_central": "D4", "datos_apoyo": []},
             {"n": 3, "cap": 2, "funcion": "pico", "dato_central": "", "datos_apoyo": []}]
    pars = [{"cap": 1, "beat": 1, "texto": "Hoy, en 2024, el valle sigue vacío. Nadie volvió."},
            {"cap": 2, "beat": 2, "texto": "El baile fue en 1961. Se casaron en 1962. Cruzaron ocho mil españoles por un "
                                           "acuerdo. El acuerdo venía desde 1950."},
            {"cap": 2, "beat": 3, "texto": "Nadie nos avisó, dice ella. El valle quedó en silencio."}]
    carga = {"topic_id": "t", "dir": Path("."), "titulos": {1: "", 2: ""}, "pool": _pool_v(), "ficha_caso": None,
             "escaleta": {"pico": {"beat": 3}, "a_pantalla": [], "beats": beats}, "parrafos": pars}
    e = mp.entrada(carga, CLIMA, SEG_ANCHO)
    e["_pool"] = _pool_v()
    return e


def _fi(pid: str, si: int, pal: str, et: str, txt: str, resp: str) -> dict:
    return {"pool_id": pid, "sentence_idx": si, "palabra": pal, "etiqueta": et, "texto": txt, "respaldo": resp,
            "autor": None, "aporta": "x"}


F_D4 = _fi("D4", 0, "valle", "EL ACUERDO", "Firmado en 1958", "firmó en 1958")                      # gancho: limpia
F_D3 = _fi("D3", 2, "españoles", "LOS QUE CRUZARON", "Cerca de 8000 españoles", "cerca de 8000 españoles")  # no_dicho «8000»
F_D2_B2 = _fi("D2", 3, "acuerdo", "HOY", "2000 muertos", "2000 personas")                          # fecha_relato 2026 > 1962
F_Q1 = _fi("Q1", 4, "avisó", "UNA VECINA", "Nadie nos avisó nunca de nada", "Nadie nos avisó nunca de nada")  # pico: limpia
DESC_D1 = {"pool_id": "D1", "tipo": "voz_lo_dice", "motivo": "la voz dice la presa"}


def _resp(b2: dict | None = F_D3, gancho: dict | None = F_D4, pico: dict | None = F_Q1, desc: bool = True) -> dict:
    return {"beats": [{"cap": "ch01", "beat": 1, "ficha": gancho, "sello": None},
                      {"cap": "ch02", "beat": 2, "ficha": b2, "sello": None},
                      {"cap": "ch02", "beat": 3, "ficha": pico, "sello": None}],
            "descartados": [DESC_D1] if desc else []}


def _juez(fichas: dict | None = None, descartes: dict | None = None, motivo: str = "m", registro: list | None = None):
    """Un verificador falso: veredicto por pool_id (lo que no está: pasa / no_dicho); devuelve el `pedido_md5` real para
    que la caché del raw funcione como con el verificador de verdad."""
    fichas, descartes = fichas or {}, descartes or {}

    def juez(marcas: list[dict], caps: list[dict]) -> dict:
        if registro is not None:
            registro.append(marcas)
        vf = [{"pool_id": m["pool_id"], "cap": m["cap"], "beat": m["beat"], "veredicto": fichas.get(m["pool_id"], "pasa"),
               "motivo": f"{motivo} {m['pool_id']}", "oracion": {"cap": "ch02", "idx": 2}}
              for m in marcas if m.get("que") != "descarte"]
        vd = [{"pool_id": m["pool_id"], "veredicto": descartes.get(m["pool_id"], "no_dicho"),
               "motivo": f"{motivo} {m['pool_id']}", "oracion": None} for m in marcas if m.get("que") == "descarte"]
        return {"veredictos_fichas": vf, "veredictos_descartes": vd, "ignorados": [], "sin_veredicto": [],
                "usage": {"input_tokens": 100, "output_tokens": 10}, "usd": 0.001, "segundos": 0.1,
                "pedido_md5": pv.pedido_md5(pv.pedido(marcas, caps)), "intentos": 1, "error": None}
    return juez


MARCAS_JUGUETE = [
    {"que": "ficha", "pool_id": "D23", "cap": "ch05", "beat": 10, "sentence_idx": 12, "oracion_ancla": "En 1991…",
     "etiqueta": "NO ERA EL ÚNICO", "texto": "Para 1989, más de 500", "respaldo": "más de 500",
     "dato_archivo": "Para 1989, más de 500 habían muerto", "regla": "no_dicho",
     "coincidencia": {"token": "500", "cap": "ch06", "idx": 7, "oracion": "…cuatro mil…"}},
    {"que": "ficha", "pool_id": "Q25", "cap": "ch02", "beat": 2, "sentence_idx": 2, "oracion_ancla": "Me pegué…",
     "etiqueta": "MARÍA", "texto": "En España no teníamos nada", "respaldo": "En España no teníamos nada",
     "dato_archivo": "En España no teníamos nada",
     "cita_completa": "Me pegué a mi marido… En España no teníamos nada, ninguno de los dos.", "regla": "spoiler",
     "coincidencia": {"token": "2", "cap": "ch02", "idx": 7, "oracion": "los dos gobiernos"}},
    {"que": "descarte", "pool_id": "D21", "regla": "voz_lo_dice", "dato_archivo": "La producción subió en 1961",
     "motivo_del_autor": "la voz lo dice", "caps_que_lo_cuentan": ["ch03"], "falta": ["Wittenoom"]},
]
CAPS_JUGUETE = [{"cap": "ch01", "oraciones": [{"idx": 0, "beat": 1, "texto": "Uno.", "caben": 10}]},
                {"cap": "ch02", "oraciones": [{"idx": 0, "beat": 2, "texto": "Dos.", "caben": 10}]}]


def test_a_pedido_puro_y_estable():
    u1 = pv.pedido(MARCAS_JUGUETE, CAPS_JUGUETE)
    u2 = pv.pedido(json.loads(json.dumps(MARCAS_JUGUETE)), json.loads(json.dumps(CAPS_JUGUETE)))
    assert u1 == u2 and pv.pedido_md5(u1) == MD5_PEDIDO_JUGUETE                   # puro y estable
    cuerpo = json.loads(u1.split("\n\nFormato de salida: ")[0])
    assert u1.endswith("\n\nFormato de salida: " + pv.FORMATO_V)
    assert list(cuerpo) == ["caps", "fichas", "descartes"]
    assert cuerpo["caps"][0] == {"cap": "ch01", "oraciones": [{"idx": 0, "texto": "Uno."}]}      # sin beat ni caben
    q = next(f for f in cuerpo["fichas"] if f["pool_id"] == "Q25")
    assert q["dato_archivo"] == "En España no teníamos nada" and q["cita_completa"].startswith("Me pegué")
    assert "cita_completa" not in next(f for f in cuerpo["fichas"] if f["pool_id"] == "D23")
    assert cuerpo["descartes"] == [{"pool_id": "D21", "dato_archivo": "La producción subió en 1961",
                                   "motivo_del_autor": "la voz lo dice", "caps_que_lo_cuentan": ["ch03"]}]  # sin `falta`
    assert "falta" not in u1 and '"que"' not in u1
    assert (pv.MODELO, pv.EFFORT, pv.REINTENTOS) == ("claude-opus-5-5", "medium", 1)
    assert hashlib.md5(pv.SYSTEM_V.encode("utf-8")).hexdigest() == MD5_SYSTEM_V
    assert pv.FORMATO_V.startswith('{"fichas": [{"pool_id": "D23", "cap": "ch05", "beat": 10, "veredicto": "pasa" | "corta"')


def test_b_leer_ignora_desconocidos_y_rellena_faltantes():
    resp = {"fichas": [{"pool_id": "D23", "cap": "ch05", "beat": 10, "veredicto": "corta", "motivo": "lo dice",
                        "oracion": {"cap": "ch06", "idx": 7}},
                       {"pool_id": "D99", "cap": "ch05", "beat": 10, "veredicto": "corta", "motivo": "x", "oracion": None},
                       {"pool_id": "Q25", "cap": "ch02", "beat": 2, "veredicto": "quizás", "motivo": "x", "oracion": None}],
            "descartes": [{"pool_id": "D21", "veredicto": "dicho", "motivo": "ch03 lo dice", "oracion": {"cap": "ch03", "idx": 28}},
                          {"pool_id": "T80", "veredicto": "dicho", "motivo": "x", "oracion": None}]}
    v = pv._leer(resp, MARCAS_JUGUETE)
    assert {(x["pool_id"], x["veredicto"], x["motivo"]) for x in v["veredictos_fichas"]} == \
        {("D23", "corta", "lo dice"), ("Q25", "pasa", "sin veredicto")}                     # Q25 «quizás» → se ignora → faltante
    assert next(x for x in v["veredictos_fichas"] if x["pool_id"] == "D23")["oracion"] == {"cap": "ch06", "idx": 7}
    assert v["veredictos_descartes"] == [{"pool_id": "D21", "veredicto": "dicho", "motivo": "ch03 lo dice",
                                         "oracion": {"cap": "ch03", "idx": 28}}]
    assert [(i.get("pool_id"), i["motivo"]) for i in v["ignorados"]] == \
        [("D99", "no está en las marcas"), ("Q25", "veredicto desconocido 'quizás'"), ("T80", "no está en las marcas")]
    assert v["sin_veredicto"] == [{"que": "ficha", "pool_id": "Q25", "cap": "ch02", "beat": 2}]
    v0 = pv._leer(None, MARCAS_JUGUETE)                                      # sin respuesta: todo «sin veredicto»
    assert {x["veredicto"] for x in v0["veredictos_fichas"]} == {"pasa"} and v0["veredictos_descartes"][0]["veredicto"] == "no_dicho"
    assert len(v0["sin_veredicto"]) == 3


def test_b_verificar_sin_json_dos_veces_no_corta_a_ciegas():
    pedidos: list[dict] = []

    def post(body):
        pedidos.append(body)
        return {"content": [{"type": "text", "text": "no hay json"}], "usage": {"input_tokens": 10, "output_tokens": 2},
                "stop_reason": "end_turn"}
    log: list[str] = []
    v = pv.verificar(MARCAS_JUGUETE, CAPS_JUGUETE, post=post, log=log)
    assert len(pedidos) == 2 and v["intentos"] == 2 and v["error"] and "JSON" in v["error"]
    assert pedidos[0]["model"] == "claude-opus-5-5" and pedidos[0]["system"] == pv.SYSTEM_V
    assert pedidos[0]["output_config"] == {"effort": "medium"}
    assert pedidos[0]["messages"][0]["content"] == pv.pedido(MARCAS_JUGUETE, CAPS_JUGUETE)
    assert {x["veredicto"] for x in v["veredictos_fichas"]} == {"pasa"}
    assert all(x["motivo"] == "sin veredicto" for x in v["veredictos_fichas"])
    assert any("sin JSON en 2 intentos" in ln for ln in log) and v["usage"] == {"input_tokens": 20, "output_tokens": 4}
    assert v["pedido_md5"] == MD5_PEDIDO_JUGUETE and v["usd"] > 0
    pedidos.clear()
    v0 = pv.verificar([], CAPS_JUGUETE, post=post)                           # sin marcas no llama
    assert pedidos == [] and v0["veredictos_fichas"] == [] and v0["usd"] == 0.0


def test_c_validar_con_juez_falso():
    e = _ent_v()
    reg: list[list] = []
    # D3 corta (no_dicho «8000»), D1 «dicho»: la ficha sale, el descarte queda como lo escribió el autor
    v = mp.validar(_resp(), e, juez=_juez({"D3": "corta"}, {"D1": "dicho"}, registro=reg))
    assert len(reg) == 1 and [(m["que"], m["regla"], m["pool_id"]) for m in reg[0]] == \
        [("ficha", "no_dicho", "D3"), ("descarte", "voz_lo_dice", "D1")]
    assert reg[0][0]["coincidencia"] == {"token": "8000", "cap": "ch02", "idx": 2,
                                         "oracion": "Cruzaron ocho mil españoles por un acuerdo."}
    assert reg[0][0]["dato_archivo"] == "Cruzaron cerca de 8000 españoles." and reg[0][0]["oracion_ancla"].startswith("Cruzaron")
    assert next(b for b in v["beats"] if b["beat"] == 2)["ficha"] is None
    d = next(d for d in v["descartados"] if d.get("pool_id") == "D3")
    assert (d["quien"], d["regla"], d["que"], d["cap"], d["beat"]) == ("verificador", "no_dicho", "ficha", "ch02", 2)
    assert d["motivo"] == "m D3 (ch02 [2])" and d["tokens"] == {"no_dicho": ["8000"]}
    assert v["fichas_fuera"] == 1 and v["vuelven"] == []                     # «dicho»: no vuelve
    d1 = next(d for d in v["descartados"] if d.get("pool_id") == "D1")
    assert "verificado" not in d1 and d1["verificador"] == "dicho: m D1"
    assert any(m.startswith("D3 (ch02 beat 2)") and "no_dicho: m D3" in m for m in v["motivos"])
    assert v["claves"] == [("no_dicho", "D3", "ch02", 2, "8000")]
    assert v["verificador"]["pedido_md5"] == pv.pedido_md5(pv.pedido(reg[0], e["caps"]))
    # D3 pasa, D1 «no_dicho»: la ficha queda con juicio_verificador; el descarte vuelve, marcado «falso»
    v2 = mp.validar(_resp(), e, juez=_juez())
    f3 = next(b for b in v2["beats"] if b["beat"] == 2)["ficha"]
    assert f3["pool_id"] == "D3" and f3["juicio_verificador"] == {"regla": ["no_dicho"], "motivo": "m D3",
                                                                  "tokens": {"no_dicho": ["8000"]}}
    assert [x["pool_id"] for x in v2["vuelven"]] == ["D1"] and v2["claves"] == [("voz_lo_dice", "D1")]
    assert next(d for d in v2["descartados"] if d.get("pool_id") == "D1")["verificado"] == "falso: la voz no dice ['266']"
    assert not [d for d in v2["descartados"] if d.get("quien") == "verificador"]
    # fecha_relato también es marca y «corta» la saca con su regla original; el pool_id cortado sale de usados_ids
    v3 = mp.validar(_resp(b2=F_D2_B2), e, juez=_juez({"D2": "corta"}))
    d2 = next(d for d in v3["descartados"] if d.get("pool_id") == "D2" and d.get("quien") == "verificador")
    assert d2["regla"] == "fecha_relato" and d2["tokens"] == {"fecha_relato": ["2026"]}
    # sin marcas el juez no se llama
    reg.clear()
    v4 = mp.validar(_resp(b2=None, desc=False), e, juez=_juez(registro=reg))
    assert reg == [] and v4["verificador"] is None and v4["marcas"] == []
    # el .md y el papel llevan lo del verificador
    p = mp.armar(e, {"validacion": v, "modelo": "x", "effort": "y", "intentos": [], "usd": 0.0, "verificador": [],
                     "reintento": {}})
    md = mp.a_markdown(p)
    assert "(verificador; marcas no_dicho" in md and "## Verificador" in md and "verificador: dicho: m D1" in md
    assert "tope" not in md.lower() and "Preguntas y respuesta" not in md


def test_f_llamar_cierres_y_una_llamada_del_verificador_por_validacion(tmp_path):
    e = _ent_v()
    # (1) sin motivos: el juez pasa D3 y dice «dicho» D1 → una validación, una llamada al verificador, cierre «sin motivos»
    reg: list[list] = []
    pedidos: list[dict] = []
    res = mp.llamar(e, tmp_path / "a", post=_post_seq([_resp()], pedidos), juez=_juez(descartes={"D1": "dicho"}, registro=reg))
    assert res["reintento"]["cierre"] == "sin motivos" and len(pedidos) == 1 and len(reg) == 1
    assert "tope" not in res and res["usd_verificador"] == 0.001 and res["usd"] == round(res["usd_autor"] + 0.001, 5)
    assert len(res["verificador"]) == 1 and res["verificador"][0]["pedido_md5"] == pv.pedido_md5(pv.pedido(reg[0], e["caps"]))
    raw = json.loads((tmp_path / "a" / f"{mp.ARCHIVO}.raw.json").read_text(encoding="utf-8"))
    assert raw["verificador"][0]["veredictos"]["fichas"][0]["pool_id"] == "D3" and "tope" not in raw
    # (2) sin progreso por claves: el juez corta D3 con un motivo de texto distinto en cada llamada; el autor insiste
    reg.clear()
    pedidos.clear()
    n = [0]

    def juez_cambiante(marcas, caps):
        n[0] += 1
        return _juez({"D3": "corta"}, {"D1": "dicho"}, motivo=f"texto {n[0]}", registro=reg)(marcas, caps)
    insiste = {"cambios": [{"cap": "ch02", "beat": 2, "ficha": F_D3}]}
    res2 = mp.llamar(e, tmp_path / "b", post=_post_seq([_resp(), insiste], pedidos), juez=juez_cambiante)
    vs = res2["reintento"]["vueltas"]
    assert res2["reintento"]["cierre"] == "sin progreso" and len(vs) == 1 and len(pedidos) == 2 and len(reg) == 2
    assert vs[0]["motivos"] != res2["validacion"]["motivos"]                 # el texto cambió («texto 1» → «texto 2»)…
    assert vs[0]["claves"] == [["no_dicho", "D3", "ch02", 2, "8000"]]        # …las claves no: cierra
    assert res2["validacion"]["claves"] == [("no_dicho", "D3", "ch02", 2, "8000")]
    assert "texto 1" in _txt(pedidos[1])                 # el motivo del verificador se le mandó al autor
    md = mp.a_markdown(mp.armar(e, res2))
    assert "sin progreso" in md and "claves:" in md
    # (3) ciclo A→B→A: D3 (corta) → D2 en b2 (fecha_relato, corta) → D3 otra vez → las claves A ya se vieron: cierra
    reg.clear()
    pedidos.clear()
    a_d2 = {"cambios": [{"cap": "ch02", "beat": 2, "ficha": F_D2_B2}]}
    a_d3 = {"cambios": [{"cap": "ch02", "beat": 2, "ficha": F_D3}]}
    res3 = mp.llamar(e, tmp_path / "c", post=_post_seq([_resp(), a_d2, a_d3, a_d2], pedidos),
                     juez=_juez({"D3": "corta", "D2": "corta"}, {"D1": "dicho"}, registro=reg))
    assert res3["reintento"]["cierre"] == "sin progreso" and len(res3["reintento"]["vueltas"]) == 2 and len(pedidos) == 3
    assert [v["claves"] for v in res3["reintento"]["vueltas"]] == [[["no_dicho", "D3", "ch02", 2, "8000"]],
                                                                   [["fecha_relato", "D2", "ch02", 2, "2026"]]]
    assert len(reg) == 3                                                     # una llamada al verificador por validación
    # (4) el juez por defecto usa el `post` falso: no hay API, las marcas quedan «sin veredicto» y pasan
    pedidos.clear()
    res4 = mp.llamar(e, tmp_path / "d", post=_post_seq([_resp(), {"cambios": []}], pedidos))
    f3 = next(b for b in res4["validacion"]["beats"] if b["beat"] == 2)["ficha"]
    assert f3["pool_id"] == "D3" and f3["juicio_verificador"]["motivo"] == "sin veredicto"
    assert pedidos[1]["system"] == pv.SYSTEM_V                               # la 2.ª llamada al POST fue del verificador
    assert res4["verificador"][0]["error"] is None and res4["verificador"][0]["veredictos"]["sin_veredicto"]


def test_g_cache_con_pedido_md5_guardado_no_llama_al_juez(tmp_path):
    e = _ent_v()
    pedidos: list[dict] = []
    res = mp.llamar(e, tmp_path, post=_post_seq([_resp()], pedidos), juez=_juez(descartes={"D1": "dicho"}))
    assert res["reintento"]["cierre"] == "sin motivos" and not res.get("cache")

    def juez_prohibido(marcas, caps):
        raise AssertionError("el juez real no debe llamarse en un hit de caché")
    log: list[str] = []
    res2 = mp.llamar(e, tmp_path, post=_post_seq([_resp()], pedidos), juez=juez_prohibido, log=log)
    assert res2["cache"] is True and len(pedidos) == 1                      # ni autor ni verificador
    assert res2["validacion"]["beats"] == res["validacion"]["beats"] and res2["usd_cache_parcial"] == 0.0
    assert mp.armar(e, res2)["usd"] == 0.0 and any("caché" in ln and "parcial" not in ln for ln in log)
    # caché parcial: el raw no tiene ese pedido_md5 → se llama al juez, se anota y el raw se completa
    raw_f = tmp_path / f"{mp.ARCHIVO}.raw.json"
    raw = json.loads(raw_f.read_text(encoding="utf-8"))
    raw["verificador"] = []
    raw_f.write_text(json.dumps(raw, ensure_ascii=False), encoding="utf-8")
    reg: list[list] = []
    log.clear()
    res3 = mp.llamar(e, tmp_path, post=_post_seq([_resp()], pedidos), juez=_juez(descartes={"D1": "dicho"}, registro=reg), log=log)
    assert res3["cache"] is True and len(reg) == 1 and len(pedidos) == 1
    assert any("caché parcial" in ln for ln in log) and res3["usd_cache_parcial"] == 0.001
    assert mp.armar(e, res3)["usd"] == 0.001 and mp.armar(e, res3)["usd_verificador"] == 0.001
    assert len(json.loads(raw_f.read_text(encoding="utf-8"))["verificador"]) == 1   # el raw se completó
    res4 = mp.llamar(e, tmp_path, post=_post_seq([_resp()], pedidos), juez=juez_prohibido)
    assert res4["cache"] is True


# ═══════════════════════ F65a Etapa B: Fase 2 respeta el juicio del verificador ═══════════════════════

def _voz_palabras(frases: list[tuple[float, float, str]]) -> list[dict]:
    """Palabras con tiempos (como test_module_f37b_colocar._voz): cada frase reparte su tiempo entre sus palabras."""
    words = []
    for a, b, txt in frases:
        ws = txt.split()
        d = (b - a) / len(ws)
        words += [{"word": w, "start": round(a + i * d, 3), "end": round(a + (i + 1) * d - 0.02, 3)} for i, w in enumerate(ws)]
    return words


def _ent_fase2(words: list[dict], items: list[dict]) -> dict:
    """La entrada de un cap de Fase 2 (pantalla_entrada.preparar_cap): oraciones, un beat, ítems con la forma de
    pantalla_entrada._item, voz del video y voz anterior."""
    from script_engine.voz_utils import oraciones
    sents = oraciones(words)
    for s in sents:
        s["beat"] = 1
    return {"oraciones": sents, "beats": [{"n": 1, "funcion": "gancho", "t0": 0.0, "t1": 10.0, "cierre": "",
                                           "dato_central": "", "datos_apoyo": []}],
            "items": items, "voz_video": [s["texto"] for s in sents], "voz_antes": ""}


def test_b_fase2_respeta_juicio_verificador():
    from script_engine import pantalla_filtros as pf
    words = _voz_palabras([(0.0, 5.0, "Wittenoom, Australia Occidental, mil novecientos sesenta y tres."),
                           (5.2, 8.0, "Esa foto se tomó en un pueblo.")])
    ent = _ent_fase2(words, [{"id": "D1", "a_pantalla": False, "por_que": "", "beats": [1], "tipo": "D", "kind": "datos",
                              "texto": "considerado el peor desastre industrial en la historia de Australia",
                              "fuente": "f", "autor": "", "gancho": False}])
    assert ent["voz_video"][0].startswith("Wittenoom, Australia") and len(ent["oraciones"]) == 2
    # la ficha anclada a la oración [1], vecina de la [0] que dice «Australia»
    ficha = {"pool_id": "D1", "sentence_idx": 1, "word_idx": 2, "tipo": "hecho", "etiqueta": "LO QUE PASÓ",
             "texto": "El peor desastre industrial de Australia"}
    jv = {"regla": ["no_dicho"], "motivo": "x", "tokens": {"no_dicho": ["Australia"]}}
    # sin juicio_verificador: cae por no_dicho («Australia» en la vecina)
    sin = pf.validar_papel([dict(ficha)], ent, words, 0.0)
    assert sin["bloques"] == [] and [(r["pool_id"], r["regla"]) for r in sin["rechazos"]] == [("D1", "no_dicho")]
    assert sin["rechazos"][0]["motivo"] == "la voz lo dice en la oración ancla o en una vecina: ['Australia']"
    # la MISMA ficha con el juicio del verificador («pasa» Australia): entra, con el juicio en el bloque
    con = pf.validar_papel([{**ficha, "juicio_verificador": jv}], ent, words, 0.0)
    assert con["rechazos"] == [] and [b["pool_id"] for b in con["bloques"]] == ["D1"]
    assert con["bloques"][0]["juicio_verificador"] == jv and con["bloques"][0]["sentence_idx"] == 1
    # un juicio de otra regla no la salva
    otra = pf.validar_papel([{**ficha, "juicio_verificador": {**jv, "tokens": {"spoiler": ["Australia"]}}}], ent, words, 0.0)
    assert [(r["pool_id"], r["regla"]) for r in otra["rechazos"]] == [("D1", "no_dicho")]
    # contradicciones (el chequeo 5 de gfx_guion): sin juicio marca; con el token que el verificador pasó, no; otra regla sí
    assert pf.contradicciones("LO QUE PASÓ El peor desastre industrial de Australia", ent["voz_video"], juicio=jv["tokens"]) == []
    voz = ["La cota autorizada fue de setecientos quince metros."]
    frase = "720 m vs 715 m («" + voz[0] + "»)"
    assert pf.contradicciones("COTA 720 metros", voz, cerca=voz) == [frase]
    assert pf.contradicciones("COTA 720 metros", voz, cerca=voz, juicio={"contradice": ["715"]}) == []
    assert pf.contradicciones_de("COTA 720 metros", voz, cerca=voz, juicio={"contradice": ["715"]}) == []
    assert pf.contradicciones("COTA 720 metros", voz, cerca=voz, juicio={"no_dicho": ["715"]}) == [frase]
