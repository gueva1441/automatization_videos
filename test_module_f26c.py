"""
test_module_f26c.py — F26 §C: R2 y R3 del research v3 con hilos (mismo manifest, mismo pool que en fila), tope con
lock en R3, cost_tracker desde hilos y `fase1_5 --temas` (un proceso por tema). Sin red.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent


# ═══════════════════════════════════════════════════════════════
#  F26 §C: workers en R2/R3, cost_tracker con lock, --temas
# ═══════════════════════════════════════════════════════════════

import json
import re
import threading

import pytest

from researcher_steps import research_v3 as rv

KYS = ROOT / "data" / "scripts" / "_steps" / "f18-kyshtym-mayak"


def _fuentes():
    fs = []
    for i in range(14):
        lg = "ru" if i % 2 else "en"
        fs.append({"id": f"F{i + 1:02d}", "slug": f"f{i + 1:02d}", "url": f"https://sitio{i % 4}.org/doc{i}",
                   "titulo": f"doc {i}", "tipo": "prensa_epoca", "anio": 1957, "prioridad": i % 3,
                   "idioma": lg, "por_que": "x"})
    fs.append({**fs[0], "id": "F99", "slug": "f99", "url": "https://www.youtube.com/watch?v=1"})
    return fs


def _get(url):
    n = int(url.rsplit("doc", 1)[1])
    if n in (2, 5):
        return 404, b"", "text/html", url
    lugar = "Kyshtym" if n != 7 else "otra cosa"
    cuerpo = (f"<html><body><p>{lugar} documento {n}. " + " ".join(f"palabra{n}x{k}" for k in range(200))
              + "</p></body></html>")
    return 200, cuerpo.encode("utf-8"), "text/html", url


def test_r2_con_workers_igual_que_en_fila(tmp_path, monkeypatch):
    monkeypatch.setattr(rv.time, "sleep", lambda s: None)
    out = {}
    for w in (1, 8):
        log = []
        man = rv.download_sources(_fuentes(), tmp_path / f"w{w}", place_re=r"Kyshtym", get=_get, max_ok=3,
                                  wayback=False, log=log, workers=w)
        out[w] = (man["documentos"], log)
    assert out[1] == out[8]
    ok = [d["id"] for d in out[8][0] if d["ok"]]
    assert ok and sum(1 for d in out[8][0] if d["estado"] == "no_intentada") > 0


def test_r2_prebajar_no_pasa_el_cupo(tmp_path, monkeypatch):
    monkeypatch.setattr(rv.time, "sleep", lambda s: None)
    pedidos = []
    lock = threading.Lock()

    def get(url):
        with lock:
            pedidos.append(url)
        return _get(url)
    rv.download_sources(_fuentes(), tmp_path, place_re=r"Kyshtym", get=get, max_ok=2, wayback=False, workers=8)
    pedidos_fila = []
    rv.download_sources(_fuentes(), tmp_path / "fila", place_re=r"Kyshtym",
                        get=lambda u: pedidos_fila.append(u) or _get(u), max_ok=2, wayback=False, workers=1)
    assert sorted(pedidos) == sorted(pedidos_fila)


@pytest.mark.skipif(not (KYS / "fuentes" / "manifest.json").exists(), reason="sin los datos de Kyshtym en disco")
def test_r3_con_workers_mismo_pool_que_en_fila(tmp_path):
    """Mock de R3 que devuelve lo guardado en la caché de Kyshtym (por la clave del prompt): mismo pool en fila y
    con 8 hilos."""
    perfil = json.loads((KYS / "_perfil.json").read_text(encoding="utf-8"))
    rv.set_vocabulario(perfil)
    try:
        man = json.loads((KYS / "fuentes" / "manifest.json").read_text(encoding="utf-8"))
        guardado = {}                    # url del documento → respuestas guardadas de R3, en el orden de los trozos
        for d in man["documentos"]:
            c = KYS / "_r3_cache" / f"r3_{d['id']}.json"
            if d.get("ok") and c.exists():
                guardado[d["url"]] = list(json.loads(c.read_text(encoding="utf-8")).values())

        def call(prompt, **kw):
            cab = prompt.splitlines()[1]
            url = cab.rsplit(" — ", 1)[1].strip()
            m = re.search(r"\(parte (\d+) de \d+\)", cab)
            xs = guardado.get(url) or [{}]
            return json.loads(json.dumps(xs[min(int(m.group(1)) - 1 if m else 0, len(xs) - 1)]))
        seed = {"seed_title": "Kyshtym", "roles_testigo": perfil.get("roles_testigo") or [],
                "roles_antagonista": perfil.get("roles_antagonista") or []}
        tiempo = rv.tiempo_del_perfil(perfil)
        pools = {}
        for w in (1, 8):
            docs = [dict(d) for d in man["documentos"] if d.get("ok")]
            texts = {d["id"]: rv.DocText(d["id"], (KYS / "fuentes" / d["txt"]).read_text(encoding="utf-8"))
                     for d in docs}
            log = []
            per_doc = rv.extract_documents(seed, docs, texts, event_year=tiempo["anio_inicio"], cache_dir=None,
                                           place_re=perfil["place_re"], log=log, workers=w, call=call)
            pool = rv.build_pool(per_doc, docs, texts, event_year=tiempo["anio_inicio"], anio_fin=tiempo["anio_fin"],
                                 log=log, subject_re=rv.subject_re_del_perfil(perfil))
            pools[w] = (json.dumps(pool, ensure_ascii=False, sort_keys=True, default=str), log)
        assert pools[1] == pools[8]
        assert json.loads(pools[8][0])["datos"]
    finally:
        rv.set_vocabulario(None)


def test_r3_tope_con_lock_no_lee_lo_que_no_entra(monkeypatch):
    docs = [{"id": f"F{i}", "tipo": "libro", "anio": 1990, "nombra_evento": True} for i in range(4)]
    texts = {d["id"]: rv.DocText(d["id"], f"Kyshtym {d['id']} " + "x " * 500) for d in docs}
    llamados = []
    monkeypatch.setattr(rv, "extract_document", lambda s, d, t, **k: llamados.append(d["id"]) or
                        {kk: [] for kk in (*rv.KINDS, "_descartados")})
    log = []
    per = rv.extract_documents({}, docs, texts, event_year=1957, cache_dir=None, place_re="Kyshtym", log=log,
                               workers=8, tope_usd=0.0)
    assert llamados == [] and all(d.get("extraccion_fallida") for d in docs) and set(per) == {d["id"] for d in docs}
    assert any("tope de US$" in x for x in log)


def test_cost_tracker_desde_hilos_no_se_pisa():
    from cost_tracker import CostTracker
    ct = CostTracker()
    ct.start_video("x")

    def anota():
        for _ in range(500):
            ct.track_custom("t", "s", "d", 1, "u", 0.001)
    hs = [threading.Thread(target=anota) for _ in range(8)]
    [h.start() for h in hs]
    [h.join() for h in hs]
    assert len(ct.current_video.entries) == 4000
    assert round(ct.current_video.total_cost, 6) == 4.0


def test_temas_un_proceso_por_tema(tmp_path, monkeypatch):
    import fase1_5 as f15
    monkeypatch.setattr(f15, "STEPS_DIR", tmp_path)
    cmds = f15.temas_cmds(["a", "b"], ["--temas", "a,b", "--v3", "--from", "m01b"])
    assert [c[-2:] for c in cmds] == [["--topic", "a"], ["--topic", "b"]]
    assert all("--temas" not in c and "--batch" in c and "--v3" in c for c in cmds)
    vistos = []

    class P:
        def __init__(self, cmd, **kw):
            vistos.append(cmd)
            self.pid = len(vistos)

        def wait(self):
            return 0 if self.pid == 1 else 3
    assert f15.run_temas(["a", "b"], ["--temas", "a,b"], popen=P) == 1
    assert len(vistos) == 2 and (tmp_path / "a" / "fase1_5_temas.log").exists()
