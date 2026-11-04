"""
test_module_f77b.py — F77 Etapa B (HANDOFF_F77 B1–B4): research v3 más rápido. Todo con mocks: CERO llamadas reales.

B1  R1: los DISCOVERY_FOCOS en paralelo; después, en paralelo, las pistas que falten; la caché con un solo escritor.
B2  carrera por foco: Pro y Flash con búsqueda a la vez en cada ronda; ambos → se suman (dedupe por URL); uno → ese;
    ninguno → otra ronda (Pro + R1_FORCE_SEARCH) hasta R1_RETRIES; `via` = pro|flash|ambos|sin.
B3  R3: las partes de un documento en paralelo, con el mismo resultado que en fila.
B4  reloj por sub-paso en el log, en 01_v3_costos.json (`tiempos_research`) y en 01_v3_tiempos.json.
"""
from __future__ import annotations

import json
import threading
import time

import pytest

from researcher_steps import research_v3 as r3

SEED = {"seed_title": "Wittenoom", "lugar_idioma": "inglés", "nombres_lugar": ["Wittenoom"]}
NO_ANNOTATE = {"annotate": lambda *a, **k: {"fuentes": []}, "resolve": lambda u: u}


def _foco_n(prompt: str) -> int:
    """El n.º de foco (1..4) de un prompt de Pro (el foco va entero) o de Flash (también)."""
    for n, foco in enumerate(r3.DISCOVERY_FOCOS, start=1):
        if foco in prompt:
            return n
    return 0


def _chunk(url: str) -> dict:
    return {"uri": url, "title": url.split("/")[2]}


class _EnVuelo:
    """Cuenta llamadas simultáneas (máximo observado)."""

    def __init__(self) -> None:
        self.lock, self.ahora, self.max = threading.Lock(), 0, 0

    def __enter__(self):
        with self.lock:
            self.ahora += 1
            self.max = max(self.max, self.ahora)

    def __exit__(self, *a):
        with self.lock:
            self.ahora -= 1


# ═══════════════════════════════════════════════════════════════
#  B1 — focos en paralelo
# ═══════════════════════════════════════════════════════════════

def test_b1_los_focos_corren_en_paralelo():
    n = len(r3.DISCOVERY_FOCOS)
    barrera = threading.Barrier(n, timeout=10)             # en fila, la barrera se rompe (timeout) y el foco queda «sin»
    vuelo = _EnVuelo()

    def pro(prompt):
        with vuelo:
            barrera.wait()
            return '{"fuentes": []}', [_chunk(f"https://a{_foco_n(prompt)}.org/doc")]

    out = r3.discover_sources(SEED, search=pro, search_alt=lambda p: ("", []), **NO_ANNOTATE)
    assert [f["via"] for f in out["_focos"]] == ["pro"] * n
    assert vuelo.max == n
    assert out["_focos_grounding"] == {"pro": n, "flash": 0, "ambos": 0, "sin": 0}
    assert [f["label"] for f in out["_focos"]] == [f"foco {i}" for i in range(1, n + 1)]   # en orden, no por hilo


def test_b1_pistas_que_faltan_en_paralelo_despues_de_los_focos():
    pistas = [f"Informe oficial número {i} sobre amianto en Wittenoom" for i in range(1, 4)]
    orden, barrera = [], threading.Barrier(len(pistas), timeout=10)

    def pro(prompt):
        if "ESTE documento" in prompt:                                        # prompt de pista
            orden.append("pista")
            barrera.wait()
            return '{"fuentes": []}', [_chunk(f"https://p.org/{abs(hash(prompt)) % 997}")]
        orden.append("foco")
        return '{"fuentes": []}', [_chunk(f"https://a{_foco_n(prompt)}.org/doc")]

    out = r3.discover_sources(SEED, search=pro, search_alt=lambda p: ("", []), pistas=pistas, **NO_ANNOTATE)
    assert orden[:len(r3.DISCOVERY_FOCOS)] == ["foco"] * len(r3.DISCOVERY_FOCOS)          # pistas, después
    assert len(out["_pistas"]) == len(pistas) and all(p["via"] == "pro" for p in out["_pistas"])


def test_b1_pista_cubierta_por_un_foco_no_se_busca():
    pista = "ACLU Abandoned Abused Orleans Prisoners report"
    llamadas = []

    def pro(prompt):
        llamadas.append(prompt)
        f = {"url": "https://aclu.org/abandoned-abused", "titulo": "Abandoned Abused Orleans Prisoners",
             "tipo": "informe_oficial", "anio": 2006, "prioridad": 1}
        return json.dumps({"fuentes": [f]}), [_chunk("https://aclu.org/abandoned-abused")]

    out = r3.discover_sources(SEED, search=pro, search_alt=lambda p: ("", []), pistas=[pista], **NO_ANNOTATE)
    assert out["_pistas"] == [] and len(llamadas) == len(r3.DISCOVERY_FOCOS)


# ═══════════════════════════════════════════════════════════════
#  B2 — carrera Pro + Flash
# ═══════════════════════════════════════════════════════════════

def test_b2_pro_y_flash_van_a_la_vez_en_la_ronda():
    barrera = threading.Barrier(2, timeout=10)             # Pro espera a Flash: solo pasa si van a la vez

    def pro(prompt):
        barrera.wait()
        return '{"fuentes": []}', [_chunk("https://pro.org/a")]

    def flash(prompt):
        barrera.wait()
        return '{"fuentes": []}', [_chunk("https://flash.org/b")]
    e = r3.r1_carrera("P", "A", "foco 1", search=pro, search_alt=flash, log=[])
    assert e["via"] == "ambos" and len(e["rondas"]) == 1
    assert e["rondas"][0]["pro_error"] is None and e["rondas"][0]["flash_error"] is None


def test_b2_solo_pro():
    e = r3.r1_carrera("P", "A", "f", search=lambda p: ('{"fuentes": [{"url": "x"}]}', [_chunk("https://pro.org/a")]),
                      search_alt=lambda p: ('{"fuentes": [{"url": "y"}]}', []), log=[])
    assert e["via"] == "pro" and e["textos"] == ['{"fuentes": [{"url": "x"}]}'] and len(e["chunks"]) == 1


def test_b2_solo_flash():
    e = r3.r1_carrera("P", "A", "f", search=lambda p: ("pro", []),
                      search_alt=lambda p: ("flash", [_chunk("https://flash.org/b")]), log=[])
    assert e["via"] == "flash" and e["textos"] == ["flash"] and e["rondas"][0]["flash_chunks"] == 1


def test_b2_pro_falla_y_flash_trae_grounding():
    def pro(prompt):
        raise RuntimeError("429 RESOURCE_EXHAUSTED")
    log: list[str] = []
    e = r3.r1_carrera("P", "A", "foco 2", search=pro, search_alt=lambda p: ("", [_chunk("https://f.org/b")]), log=log)
    assert e["via"] == "flash" and "RuntimeError" in e["rondas"][0]["pro_error"]
    assert any("Pro falló" in x for x in log)


def test_b2_ambos_suma_chunks_con_dedupe_por_url():
    def pro(prompt):
        return (json.dumps({"fuentes": [{"url": "https://comun.org/x", "titulo": "Común", "prioridad": 1}]}),
                [_chunk("https://comun.org/x"), _chunk("https://pro.org/a")])

    def flash(prompt):
        return (json.dumps({"fuentes": [{"url": "https://flash.org/b", "titulo": "Flash", "prioridad": 2}]}),
                [_chunk("https://www.comun.org/x/"), _chunk("https://flash.org/b")])   # la misma URL, otra forma
    out = r3.discover_sources(SEED, search=pro, search_alt=flash, **NO_ANNOTATE)
    assert all(f["via"] == "ambos" and f["n_urls"] == 3 for f in out["_focos"])      # 2 + 2 − 1 repetida
    assert out["_focos_grounding"]["ambos"] == len(r3.DISCOVERY_FOCOS)
    urls = {r3.norm_url(g["url"]) for g in out["_grounding"]}
    assert urls == {"comun.org/x", "pro.org/a", "flash.org/b"}
    assert {f["titulo"] for f in out["fuentes"]} >= {"Común", "Flash"}                   # fichas de los dos textos


def test_b2_ninguno_hasta_r1_retries_rondas_queda_sin():
    pro_p, flash_p = [], []
    e = r3.r1_carrera("PROMPT", "ALT", "foco 3", search=lambda p: pro_p.append(p) or ("", []),
                      search_alt=lambda p: flash_p.append(p) or ("", []), log=[])
    assert r3.R1_RETRIES == 3
    assert e["via"] == "sin" and len(e["rondas"]) == r3.R1_RETRIES
    assert len(pro_p) == len(flash_p) == r3.R1_RETRIES                                   # rondas, no intentos de Pro
    assert pro_p[0] == "PROMPT" and all(p == "PROMPT" + r3.R1_FORCE_SEARCH for p in pro_p[1:])
    assert flash_p == ["ALT"] * r3.R1_RETRIES


def test_b2_segunda_ronda_trae_grounding():
    def pro(p):
        return ("", [_chunk("https://pro.org/a")] if r3.R1_FORCE_SEARCH in p else [])
    e = r3.r1_carrera("P", "A", "f", search=pro, search_alt=lambda p: ("", []), log=[])
    assert e["via"] == "pro" and [r["ronda"] for r in e["rondas"]] == [1, 2]


def test_b2_cuenta_de_focos_por_via():
    def pro(prompt):
        n = _foco_n(prompt)
        return "", [_chunk(f"https://pro{n}.org/a")] if n in (1, 3) else []

    def flash(prompt):
        n = _foco_n(prompt)
        return "", [_chunk(f"https://flash{n}.org/b")] if n in (2, 3) else []
    out = r3.discover_sources(SEED, search=pro, search_alt=flash, **NO_ANNOTATE)
    assert [f["via"] for f in out["_focos"]] == ["pro", "flash", "ambos", "sin"]
    assert out["_focos_grounding"] == {"pro": 1, "flash": 1, "ambos": 1, "sin": 1}
    assert [f["n_urls"] for f in out["_focos"]] == [1, 1, 2, 0]
    assert len(out["_focos"][3]["rondas"]) == r3.R1_RETRIES


def test_b2_la_cadena_vieja_no_existe():
    import inspect
    src = inspect.getsource(r3.discover_sources) + inspect.getsource(r3.r1_carrera)
    assert "reintentos → Flash" not in src and "for _ in range(R1_RETRIES)" not in src


# ═══════════════════════════════════════════════════════════════
#  B1 — caché sin carreras
# ═══════════════════════════════════════════════════════════════

def test_b1_cache_un_solo_escritor_con_muchos_hilos(tmp_path, monkeypatch):
    pistas = [f"Documento judicial distinto número {i} expediente" for i in range(12)]
    vuelo = _EnVuelo()
    real_replace = r3.os.replace

    def replace(a, b):                                       # ventana ancha: dos escritores a la vez se verían
        with vuelo:
            time.sleep(0.01)
            return real_replace(a, b)
    monkeypatch.setattr(r3.os, "replace", replace)

    def pro(prompt):
        time.sleep(0.005)
        return "", [_chunk(f"https://x.org/{abs(hash(prompt)) % 100003}")]
    cache = tmp_path / "_r1_cache.json"
    out = r3.discover_sources(SEED, search=pro, search_alt=lambda p: ("", []), pistas=pistas, cache=cache,
                              workers=r3.WORKERS, **NO_ANNOTATE)
    assert vuelo.max == 1
    store = json.loads(cache.read_text(encoding="utf-8"))
    claves = [k for k in store if k.startswith(r3.PROMPT_VERSION_R1 + "|")]
    assert len(claves) == len(r3.DISCOVERY_FOCOS) + len(out["_pistas"]) == len(r3.DISCOVERY_FOCOS) + len(pistas)
    assert all(store[k]["via"] == "pro" and store[k]["ground"] for k in claves)
    assert not (tmp_path / "_r1_cache.json.tmp").exists()
    # 2.ª corrida: todo de la caché, sin llamadas
    out2 = r3.discover_sources(SEED, search=lambda p: pytest.fail("llamó a Pro"),
                               search_alt=lambda p: pytest.fail("llamó a Flash"), pistas=pistas, cache=cache,
                               **NO_ANNOTATE)
    assert all(f["cache"] for f in out2["_focos"] + out2["_pistas"])


def test_b1_cache_vieja_con_via_pro_sigue_valiendo(tmp_path):
    prompt = r3.build_discovery_prompt(SEED, r3.DISCOVERY_FOCOS[0], None)
    import hashlib
    key = f"{r3.PROMPT_VERSION_R1}|" + hashlib.sha1(prompt.encode("utf-8")).hexdigest()[:16]
    cache = tmp_path / "c.json"
    cache.write_text(json.dumps({key: {"text": "", "chunks": [_chunk("https://viejo.org/a")], "via": "pro"}}),
                     encoding="utf-8")
    out = r3.discover_sources(SEED, search=lambda p: ("", []), search_alt=lambda p: ("", []), cache=cache,
                              **NO_ANNOTATE)
    assert out["_focos"][0]["via"] == "pro" and out["_focos"][0]["cache"] and out["_focos"][0]["n_urls"] == 1


# ═══════════════════════════════════════════════════════════════
#  B3 — R3: las partes de un documento en paralelo
# ═══════════════════════════════════════════════════════════════

def _texto_largo() -> str:
    parr = "El 29 de septiembre de 1957 explotó un tanque en Mayak y los vecinos de Kyshtym vieron la nube. "
    return (parr * (r3.CHUNK_CHARS * 3 // len(parr) + 10))


def test_b3_partes_en_paralelo_y_mismo_resultado_que_en_fila(tmp_path):
    texto = _texto_largo()
    n = len(r3.chunk_text(texto))
    assert n >= 3
    barrera = threading.Barrier(n, timeout=10)

    def resp() -> dict:
        return {"datos": [{"texto": "explotó un tanque", "cita_literal": "explotó un tanque en Mayak",
                           "tipo": "magnitud", "fecha": "1957-09-29"}], "cronologia": [], "lugares": [], "citas": [],
                "personajes": []}

    def call_paralelo(prompt, **kw):
        barrera.wait()                                       # en fila, se rompe: la parte falla y el test lo ve
        return resp()

    def call_fila(prompt, **kw):
        return resp()
    doc = {"id": "F07", "titulo": "Informe", "tipo": "informe_oficial", "anio": 1990, "url": "https://a.org/x"}
    seed = {"seed_title": "Kyshtym"}
    log_p: list[str] = []
    par = r3.extract_document(seed, doc, texto, call=call_paralelo, cache_dir=tmp_path / "p", log=log_p)
    assert "_extraccion_fallida" not in par
    log_f: list[str] = []
    fila = r3.extract_document(seed, doc, texto, call=call_fila, cache_dir=tmp_path / "f", log=log_f, workers=1)
    assert par == fila and log_p == log_f
    assert len(json.loads((tmp_path / "p" / "r3_F07.json").read_text(encoding="utf-8"))) == n   # caché completa


def test_b3_cupo_limita_las_llamadas_en_vuelo():
    texto = _texto_largo()
    vuelo = _EnVuelo()

    def call(prompt, **kw):
        with vuelo:
            time.sleep(0.02)
            return {}
    cupo = threading.BoundedSemaphore(1)
    r3.extract_document({"seed_title": "K"}, {"id": "F01", "titulo": "t"}, texto, call=call, cupo=cupo)
    assert vuelo.max == 1


def test_b3_extract_documents_lee_las_partes_de_un_documento_en_paralelo():
    texto = _texto_largo()
    n = len(r3.chunk_text(texto))
    barrera = threading.Barrier(n, timeout=10)              # un solo documento: solo pasa si sus partes van a la vez

    def call(prompt, **kw):
        barrera.wait()
        return {}
    docs = [{"id": "F07", "titulo": "a", "anio": 1990, "nombra_evento": True}]
    per = r3.extract_documents({"seed_title": "K"}, docs, {"F07": r3.DocText("F07", texto)}, event_year=1957,
                               cache_dir=None, place_re=None, call=call)
    assert "extraccion_fallida" not in docs[0] and set(per) == {"F07"}
    for tope in (None, 100.0):                               # con tope de costo, igual (el `w` del tope no se cruza)
        barrera.reset()
        docs = [{"id": "F07", "titulo": "a", "anio": 1990, "nombra_evento": True}]
        r3.extract_documents({"seed_title": "K"}, docs, {"F07": r3.DocText("F07", texto)}, event_year=1957,
                             cache_dir=None, place_re=None, call=call, tope_usd=tope)
        assert "extraccion_fallida" not in docs[0]


def test_b3_extract_documents_anota_tiempo_por_documento():
    texto = _texto_largo()
    docs = [{"id": "F01", "titulo": "a", "anio": 1990, "nombra_evento": True},
            {"id": "F02", "titulo": "b", "anio": 1990, "nombra_evento": True}]
    texts = {"F01": r3.DocText("F01", texto), "F02": r3.DocText("F02", "Kyshtym 1957. " * 100)}
    tiempos: list[dict] = []
    log: list[str] = []
    r3.extract_documents({"seed_title": "K"}, docs, texts, event_year=1957, cache_dir=None, place_re=None, log=log,
                         call=lambda p, **k: {}, tiempos=tiempos)
    assert [t["doc"] for t in tiempos] == ["F01", "F02"]
    assert tiempos[0]["partes"] == len(r3.chunk_text(texto)) and tiempos[1]["partes"] == 1
    assert all(isinstance(t["s"], float) for t in tiempos)
    assert any("[reloj] R3 F01" in x for x in log)


# ═══════════════════════════════════════════════════════════════
#  B4 — reloj por sub-paso
# ═══════════════════════════════════════════════════════════════

def _mock_run_seed(monkeypatch, tmp_path, r1: dict):
    (tmp_path / "_perfil.json").write_text(json.dumps({"anio_evento": 1957, "place_re": r"texto", "roles_testigo": [],
                                                       "roles_antagonista": []}), encoding="utf-8")
    (tmp_path / "fuentes").mkdir()
    monkeypatch.setattr(r3, "discover_sources", lambda s2, **k: r1)
    monkeypatch.setattr(r3, "download_sources", lambda *a, **k: {"documentos": []})
    monkeypatch.setattr(r3, "refine_fichas", lambda *a, **k: None)
    monkeypatch.setattr(r3, "build_pool", lambda *a, **k: {"datos": [], "cronologia": [], "citas": [],
                                                           "personajes": [], "lugares": []})
    monkeypatch.setattr(r3, "pool_to_blocks", lambda pool: {})


R1_MOCK = {"fuentes": [], "_focos": [{"label": "foco 1", "via": "ambos", "n_urls": 7, "n_fichas": 5, "cache": False,
                                      "s": 1.5, "rondas": [{"ronda": 1, "s": 1.5, "pro_s": 1.5, "flash_s": 0.9,
                                                            "pro_chunks": 4, "flash_chunks": 4, "pro_error": None,
                                                            "flash_error": None}]}],
           "_pistas": [], "_tiempos": {"total_s": 2.0, "focos_s": 1.5, "pistas_s": 0.0, "fichas_flash_s": 0.5}}


def test_b4_reloj_en_costos_y_en_el_log(tmp_path, monkeypatch):
    _mock_run_seed(monkeypatch, tmp_path, R1_MOCK)
    (tmp_path / "01_v3_costos.json").write_text(json.dumps({"_corridas": [{"paso": "ficha", "usd": 0.3,
                                                                           "segundos": 9.0}]}), encoding="utf-8")
    log: list[str] = []
    try:
        r3.run_seed({"seed_title": "x"}, "t", tmp_path, gate=False, log=log, gate_es_s=4.25)
    finally:
        r3.set_vocabulario(None)
        r3.set_idiomas(None)
    costos = json.loads((tmp_path / "01_v3_costos.json").read_text(encoding="utf-8"))
    assert costos["_corridas"] == [{"paso": "ficha", "usd": 0.3, "segundos": 9.0}]       # lo de antes, intacto
    rec = costos["tiempos_research"][-1]
    assert set(rec) == {"inicio", "total_s", "pasos", "R1_detalle", "R1_focos", "R1_pistas", "R3_docs", "error"}
    assert set(rec["pasos"]) == set(r3.RELOJ_PASOS)
    assert rec["pasos"]["gate_es"] == 4.25 and rec["pasos"]["compuerta_pool"] is None     # gate=False
    assert all(isinstance(rec["pasos"][k], float) for k in ("perfil", "R1", "R2", "R3", "pool"))
    assert rec["R1_focos"][0]["via"] == "ambos" and rec["R1_focos"][0]["n_urls"] == 7
    assert rec["R1_detalle"]["focos_s"] == 1.5 and rec["error"] is None
    assert json.loads((tmp_path / r3.RELOJ_ARCHIVO).read_text(encoding="utf-8"))["tiempos_research"] == [rec]
    assert any(x.startswith("  [reloj] research:") and "R1" in x for x in log)
    assert any("[reloj] R1 foco 1" in x and "via ambos" in x for x in log)


def test_b4_reloj_queda_aunque_la_compuerta_salga_roja(tmp_path, monkeypatch):
    _mock_run_seed(monkeypatch, tmp_path, R1_MOCK)
    from researcher_steps import pool_gate as pg

    class Roja(Exception):
        pass

    def check(*a, **k):
        raise Roja("compuerta roja")
    monkeypatch.setattr(pg, "check", check)
    try:
        with pytest.raises(Roja):
            r3.run_seed({"seed_title": "x"}, "t", tmp_path, gate=True)
    finally:
        r3.set_vocabulario(None)
        r3.set_idiomas(None)
    rec = json.loads((tmp_path / "01_v3_costos.json").read_text(encoding="utf-8"))["tiempos_research"][-1]
    assert isinstance(rec["pasos"]["compuerta_pool"], float) and rec["pasos"]["gate_es"] is None
    assert rec["error"].startswith("Roja")


def test_b4_discover_sources_trae_tiempos_y_rondas():
    out = r3.discover_sources(SEED, search=lambda p: ("", [_chunk("https://a.org/x")]),
                              search_alt=lambda p: ("", []), **NO_ANNOTATE)
    assert set(out["_tiempos"]) == {"total_s", "focos_s", "pistas_s", "fichas_flash_s"}
    f = out["_focos"][0]
    assert set(f) == {"label", "via", "n_urls", "n_fichas", "cache", "s", "rondas"}
    assert set(f["rondas"][0]) == {"ronda", "s", "pro_s", "flash_s", "pro_chunks", "flash_chunks", "pro_error",
                                   "flash_error"}
