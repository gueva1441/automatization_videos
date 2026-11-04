"""F77 A — gate ES por la API oficial (list_spanish_candidates), filtro > 180 s (Shorts fuera) en API y
raspado, query sin paréntesis ni puntuación final, cuota por medida, loops en paralelo con el raspado
topeado a ES_GAP_WORKERS, y la medida del pick sin preguntas (measure_pick_es). Sin red: requests.get,
scrapetube.get_search y el juez se reemplazan por dobles; nada escribe en disco."""
import threading
import time
from datetime import datetime

import pytest

import fase1
import niche_discoverer as nd
import script_engine.subtopic_measurer as sm
import script_engine.youtube_scanner as ys

LLAVE = "LLAVE-DE-PRUEBA-NO-REAL"


class _Resp:
    def __init__(self, data, status=200):
        self._data, self.status_code = data, status

    def raise_for_status(self):
        if self.status_code >= 400:
            # imita requests: la URL del error llevaría la llave si fuera por query string
            raise RuntimeError(f"{self.status_code} Client Error: Forbidden for url: x?key={LLAVE}")

    def json(self):
        return self._data


def _video(vid, title, dur, views, published):
    return {"id": vid, "snippet": {"title": title, "publishedAt": published},
            "contentDetails": {"duration": dur}, "statistics": {"viewCount": str(views)}}


@pytest.fixture
def api_falsa(monkeypatch):
    """requests.get falso: search.list por páginas (ids_por_pagina) y videos.list desde `videos`."""
    estado = {"llamadas": [], "ids_por_pagina": [], "videos": {}, "status": 200}
    monkeypatch.setattr(ys.api, "youtube_api_key", LLAVE, raising=False)

    def get(url, params=None, headers=None, timeout=None):
        estado["llamadas"].append({"url": url, "params": dict(params or {}), "headers": dict(headers or {})})
        if estado["status"] != 200:
            return _Resp({}, estado["status"])
        if url.endswith("/search"):
            n = sum(1 for c in estado["llamadas"] if c["url"].endswith("/search"))
            pagina = estado["ids_por_pagina"][n - 1]
            data = {"items": [{"id": {"videoId": v}} for v in pagina]}
            if n < len(estado["ids_por_pagina"]):
                data["nextPageToken"] = f"tok{n}"
            return _Resp(data)
        ids = params["id"].split(",")
        return _Resp({"items": [estado["videos"][i] for i in ids if i in estado["videos"]]})

    monkeypatch.setattr(ys.requests, "get", get)
    return estado


def _palomares(estado):
    estado["ids_por_pagina"] = [["4VgrwqGvIuc", "IUpaoH-lvkI", "Yvo7kps24Fo", "enEN0000001", "_dabgyhU3tQ"]]
    estado["videos"] = {
        "4VgrwqGvIuc": _video("4VgrwqGvIuc", "4 BOMBAS NUCLEARES cayeron en España", "PT10M47S", 212637,
                              "2026-10-25T10:00:00Z"),
        "IUpaoH-lvkI": _video("IUpaoH-lvkI", "Las bombas de Palomares que nadie recuerda", "PT58S", 4_500_000,
                              "2025-06-01T10:00:00Z"),
        "Yvo7kps24Fo": _video("Yvo7kps24Fo", "Palomares: el día que cayeron las bombas", "PT3M", 2_000_000,
                              "2025-07-01T10:00:00Z"),
        "enEN0000001": _video("enEN0000001", "The Palomares incident explained in full detail", "PT20M", 900_000,
                              "2024-01-01T10:00:00Z"),
        "_dabgyhU3tQ": _video("_dabgyhU3tQ", "El accidente nuclear de Palomares, la historia completa", "PT45M",
                              104_000, "2021-12-10T10:00:00Z"),
    }


# ── A3: la búsqueda limpia, el título no ──

@pytest.mark.parametrize("titulo,query", [
    ("Palomares 1966", "Palomares 1966"),
    ("Palomares 1966 (Almería).", "Palomares 1966"),
    ("Palomares 1966: el Proyecto Indalo y los vecinos", "Palomares 1966: el Proyecto Indalo y los vecinos"),
    ("Goiânia 1987 (Brasil) - ", "Goiânia 1987"),
    ("Los Alfaques 1978;,", "Los Alfaques 1978"),
    ("(todo entre paréntesis)", "(todo entre paréntesis)"),
])
def test_query_sin_parentesis_ni_puntuacion_final(titulo, query):
    assert ys._es_search_query(titulo) == query


def test_duracion_iso_y_meses():
    assert ys._iso8601_duration_s("PT10M47S") == 647
    assert ys._iso8601_duration_s("PT1H2M3S") == 3723
    assert ys._iso8601_duration_s("PT3M") == 180
    assert ys._iso8601_duration_s("P0D") is None          # en vivo / estreno: desconocida
    assert ys._iso8601_duration_s("") is None
    assert ys._iso8601_duration_s("basura") is None
    hoy = datetime(2026, 11, 4)
    assert ys._months_since("2026-10-25T10:00:00Z", hoy) == 0
    assert ys._months_since("2025-09-04T10:00:00Z", hoy) == 14
    assert ys._months_since("2021-12-10T10:00:00Z", hoy) == 58
    assert ys._months_since(None, hoy) is None


# ── A1: API primero, solo > 180 s, mismo shape + duration_s ──

def test_api_primero_sin_shorts_y_shape(api_falsa, monkeypatch):
    _palomares(api_falsa)
    monkeypatch.setattr(ys.scrapetube, "get_search", lambda *a, **k: pytest.fail("no debe raspar"))
    out = ys.list_spanish_candidates("Palomares 1966 (Almería).")
    ids = [c["video_id"] for c in out]
    assert "IUpaoH-lvkI" not in ids and "Yvo7kps24Fo" not in ids      # Shorts (58 s y 180 s) fuera
    assert "enEN0000001" not in ids                                       # título en inglés fuera
    assert ids == ["4VgrwqGvIuc", "_dabgyhU3tQ"]
    c = out[0]
    assert set(c) == {"title", "views", "months", "video_id", "duration_s", "source"}
    assert (c["views"], c["duration_s"], c["source"]) == (212637, 647, "api")
    assert out.source == "api" and out.n_short == 2 and out.n_raw == 5
    assert (out.search_pages, out.video_batches, out.quota_units) == (1, 1, 101)
    busq = api_falsa["llamadas"][0]["params"]
    assert busq["q"] == "Palomares 1966" and busq["type"] == "video" and busq["relevanceLanguage"] == "es"
    assert busq["maxResults"] == ys.YT_LIMIT_ARCHAEOLOGY
    vids = api_falsa["llamadas"][1]["params"]
    assert vids["part"] == "contentDetails,statistics,snippet"


def test_llave_va_en_header_nunca_en_la_url(api_falsa):
    _palomares(api_falsa)
    ys.list_spanish_candidates("Palomares 1966")
    for c in api_falsa["llamadas"]:
        assert c["headers"].get("X-Goog-Api-Key") == LLAVE
        assert LLAVE not in str(c["params"]) and LLAVE not in c["url"]


def test_paginado_hasta_el_limite_y_lotes_de_50(api_falsa):
    api_falsa["ids_por_pagina"] = [[f"a{i:09d}" for i in range(50)], [f"b{i:09d}" for i in range(50)]]
    api_falsa["videos"] = {v: _video(v, f"Documental del caso número {v} en español", "PT12M", 1000,
                                     "2026-01-01T00:00:00Z")
                           for p in api_falsa["ids_por_pagina"] for v in p}
    out = ys.list_spanish_candidates("caso", limit=70)
    busquedas = [c for c in api_falsa["llamadas"] if c["url"].endswith("/search")]
    lotes = [c for c in api_falsa["llamadas"] if c["url"].endswith("/videos")]
    assert [b["params"]["maxResults"] for b in busquedas] == [50, 20]
    assert busquedas[1]["params"]["pageToken"] == "tok1"
    assert [len(l["params"]["id"].split(",")) for l in lotes] == [50, 20]
    assert out.quota_units == 2 * ys.YT_UNITS_SEARCH + 2 * ys.YT_UNITS_VIDEOS == 202


# ── respaldo: raspado con el mismo filtro, duración desconocida = se cuenta, sin llave en el error ──

def _scrape_vid(vid, title, length, views="100 K vistas", pub="hace 2 meses"):
    v = {"videoId": vid, "title": {"runs": [{"text": title}]},
         "viewCountText": {"simpleText": views}, "publishedTimeText": {"simpleText": pub}}
    if length is not None:
        v["lengthText"] = {"simpleText": length}
    return v


def test_api_403_cae_al_raspado_con_filtro_de_duracion(api_falsa, monkeypatch, capsys):
    api_falsa["status"] = 403
    crudos = [_scrape_vid("largo000001", "El accidente nuclear de Palomares explicado", "12:30"),
              _scrape_vid("short000001", "Las bombas de Palomares que nadie recuerda", "0:58"),
              _scrape_vid("sindur00001", "Palomares, la historia que España ocultó", None)]
    monkeypatch.setattr(ys.scrapetube, "get_search", lambda *a, **k: iter(crudos))
    out = ys.list_spanish_candidates("Palomares 1966")
    assert out.source == "scrape" and out.quota_units == 0
    assert [c["video_id"] for c in out] == ["largo000001", "sindur00001"]
    assert out[1]["duration_s"] is None and out.n_short == 1
    assert "403" in out.api_error and LLAVE not in out.api_error
    log = capsys.readouterr().out
    assert "fuente=scrape" in log and LLAVE not in log


def test_api_y_raspado_caidos_devuelve_none(api_falsa, monkeypatch):
    api_falsa["status"] = 403

    def cae(*a, **k):
        raise ConnectionError("proxy muerto")
    monkeypatch.setattr(ys.scrapetube, "get_search", cae)
    assert ys.list_spanish_candidates("Palomares 1966") is None


def test_sin_llave_va_al_raspado(monkeypatch):
    monkeypatch.setattr(ys.api, "youtube_api_key", "", raising=False)
    monkeypatch.setattr(ys.requests, "get", lambda *a, **k: pytest.fail("sin llave no llama a la API"))
    monkeypatch.setattr(ys.scrapetube, "get_search",
                        lambda *a, **k: iter([_scrape_vid("largo000001", "El accidente de Palomares", "12:30")]))
    out = ys.list_spanish_candidates("Palomares")
    assert out.source == "scrape" and len(out) == 1


# ── A2: el raspado de respaldo queda topeado a ES_GAP_WORKERS aunque haya más hilos ──

def test_raspado_topeado_a_es_gap_workers(monkeypatch):
    activos, pico, lock = [0], [0], threading.Lock()

    def lento(*a, **k):
        with lock:
            activos[0] += 1
            pico[0] = max(pico[0], activos[0])
        time.sleep(0.05)
        with lock:
            activos[0] -= 1
        return iter([])
    monkeypatch.setattr(ys.scrapetube, "get_search", lento)
    hilos = [threading.Thread(target=ys._scrape_spanish_candidates, args=(f"q{i}", 10)) for i in range(9)]
    for h in hilos:
        h.start()
    for h in hilos:
        h.join()
    assert pico[0] == ys.ES_GAP_WORKERS == 3
    assert nd.ES_GAP_WORKERS is ys.ES_GAP_WORKERS


def test_fanout_mide_es_en_paralelo_con_workers_igual_a_items(monkeypatch):
    import script_engine.subtopic_classifier as sc
    import script_engine.subtopic_extractor as se
    import script_engine.transcript_fetch as tf
    workers = []
    real = nd.ThreadPoolExecutor

    class Espia(real):
        def __init__(self, max_workers=None, *a, **k):
            workers.append(max_workers)
            super().__init__(max_workers, *a, **k)
    monkeypatch.setattr(nd, "ThreadPoolExecutor", Espia)
    monkeypatch.setattr(tf, "fetch_transcript", lambda *a, **k: "transcript")
    monkeypatch.setattr(sc, "classify", lambda *a, **k: {"tipo": "CONTENEDOR"})
    subj = [{"nombre_en": f"S{i}", "search_query_en": f"S{i}", "angle_en": f"S{i}"} for i in range(5)]
    monkeypatch.setattr(se, "extract_segment_subjects", lambda *a, **k: subj)
    monkeypatch.setattr(se, "verify_names", lambda *a, **k: {})
    monkeypatch.setattr(sm, "_measure_en_laxo", lambda q, e=None: {"pasa_laxo": True, "top_rel_views": 10})
    vistos = []

    def es(q, e=None):
        vistos.append(threading.get_ident())
        time.sleep(0.02)
        return {"label": "SATURADO" if q == "S2" else "VACIO", "saturation": 0.0}
    monkeypatch.setattr(sm, "_measure_es", es)
    out = nd._try_subtema_fanout({"video_id": "V", "original_title": "T"}, None, {}, 1)
    assert workers[0] == 5                                   # ES: workers = ítems
    assert len(set(vistos)) > 1                              # de verdad en paralelo
    assert [s["nombre_en"] for s in out] == ["S0", "S1", "S3", "S4"]   # orden del cap, S2 SATURADO fuera


# ── _measure_es: fuente, unidades, candidatos con peso y relevancia, competidor con id ──

def test_measure_es_palomares_por_api(api_falsa, monkeypatch):
    _palomares(api_falsa)
    monkeypatch.setattr(sm, "translate_to_es", lambda t: {"es_query": t, "es_aliases": ["Palomares"]})
    monkeypatch.setattr(sm, "filter_relevant",
                        lambda ent, cands, aliases=None: [c for c in cands if "Palomares" in c["title"]
                                                          or "BOMBAS" in c["title"]])
    r = sm._measure_es("Palomares 1966", "Palomares 1966", already_es=True)
    assert r["label"] == "SATURADO" and r["source"] == "api+juez" and r["quota_units"] == 101
    assert r["heaviest"]["video_id"] == "4VgrwqGvIuc" and r["heaviest"]["decay"] == 1.0
    assert r["heaviest"]["duration_s"] == 647 and r["n_short_es"] == 2
    assert r["es_query"] == "Palomares 1966" and r["search_query_es"] == "Palomares 1966"
    tabla = {c["video_id"]: c for c in r["candidates"]}
    assert set(tabla) == {"4VgrwqGvIuc", "_dabgyhU3tQ"}
    assert tabla["_dabgyhU3tQ"]["relevante"] is True and tabla["_dabgyhU3tQ"]["peso"] == 0.3


def test_measure_es_suma_unidades_de_la_red_over_narrow(monkeypatch):
    llamadas = []

    def lista(q, limit=50):
        out = ys.EsCandidates()
        out.quota_units = 101
        llamadas.append(q)
        if len(llamadas) == 2:
            out.append({"title": "x", "views": 10, "months": 1, "video_id": "v", "duration_s": 600})
        return out
    monkeypatch.setattr(sm, "list_spanish_candidates", lista)
    monkeypatch.setattr(sm, "translate_to_es", lambda t: {"es_query": t, "es_aliases": []})
    monkeypatch.setattr(sm, "filter_relevant", lambda e, c, aliases=None: c)
    r = sm._measure_es("query angulada larga", "Entidad")
    assert r["query_fallback"] is True and r["quota_units"] == 202


# ── measure_pick_es: la medida del pick SIN preguntas (Etapa C) ──

def test_measure_pick_es_sin_preguntas(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda *a, **k: pytest.fail("no debe preguntar"))
    labs = iter(["HUECO", "SATURADO", "DISPUTADO"])

    def medir(q, entity=None, already_es=False):
        lab = next(labs)
        sat = {"HUECO": 10_000, "DISPUTADO": 80_000, "SATURADO": 212_637}[lab]
        return {"label": lab, "saturation": sat, "source": "api+juez", "quota_units": 101,
                "heaviest": {"title": lab, "video_id": f"id_{lab}", "views": sat, "months": 0}}
    monkeypatch.setattr(fase1, "_measure_es", medir)
    seed = nd._build_seed("Palomares 1966", "manual", None, {},
                          remeasure={"es_query": "Palomares 1966", "entity": "Palomares 1966",
                                     "already_es": True})
    m = fase1.measure_pick_es(seed, n=3)
    assert (m["status"], m["label"], m["saturation"]) == ("ok", "SATURADO", 212_637)
    assert m["heaviest"]["video_id"] == "id_SATURADO" and m["quota_units"] == 303
    assert len(m["measurements"]) == 3 and m["source"] == "api+juez"


def test_measure_pick_es_sin_receta_y_con_errores(monkeypatch):
    assert fase1.measure_pick_es({"seed_title": "viejo"})["status"] == "sin_receta"
    monkeypatch.setattr(fase1, "_measure_es", lambda *a, **k: {"label": "ERROR", "error": "caído"})
    seed = {"seed_title": "x", "remeasure": {"es_query": "x", "entity": "x", "already_es": True}}
    m = fase1.measure_pick_es(seed, n=2)
    assert m["status"] == "error" and m["label"] is None and len(m["measurements"]) == 2
