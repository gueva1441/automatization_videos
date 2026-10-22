"""
test_module_f8b.py — F8b (HANDOFF_F8b_F9 §1–§2): arreglos de research v3 y reglas de imagen + grade de post.
"""
from __future__ import annotations

import pytest

from researcher_steps import research_v3 as r3

# ═══════════════════════════════════════════════════════════════
#  §1.1 — antigüedad por ítem, no por documento
# ═══════════════════════════════════════════════════════════════


def test_documentos_de_2014_a_2023_sobre_1963_entran():
    for anio in (2014, 2019, 2023):
        assert r3.doc_contamination({"nombra_evento": True, "anio": anio}, 1963) is None
    assert r3.doc_contamination({"nombra_evento": False, "anio": 1964}, 1963)


def test_antiguedad_por_item_con_excepciones():
    assert r3.contamination({"fecha": "1963-10-09", "texto": "la ola"}, 1963) is None
    assert r3.contamination({"fecha": "2014-05-01", "texto": "una mostra fotografica a Roma"}, 1963)
    assert r3.contamination({"fecha": "1997-03-25", "texto": "La sentenza della Cassazione"}, 1963) is None
    assert r3.contamination({"fecha": "2013-10-09", "evento": "Cerimonia per il 50° anniversario"}, 1963) is None
    assert r3.contamination({"fecha": "1930-01-01", "texto": "un hecho cualquiera"}, 1963)
    assert r3.contamination({"fecha": "1929-01-01", "texto": "La SADE ottiene la concessione"}, 1963) is None
    assert r3.contamination({"fecha": "2026-03-01"}, 2005).startswith("fecha 2026")      # Orleans: igual que antes


def test_merge_con_documentos_retrospectivos():
    docs = [{"id": "F01", "anio": 2023, "nombra_evento": True, "tipo": "prensa_posterior", "url": "https://x.it/a"},
            {"id": "F02", "anio": 2014, "nombra_evento": True, "tipo": "academico", "url": "https://y.it/b"}]
    item = {"texto": "La frana del Toc cadde nel lago", "tipo": "magnitud", "fecha": "1963-10-09", "offset": 0,
            "cita_literal": "la frana del Toc"}
    per_doc = {"F01": {"datos": [dict(item)]}, "F02": {"datos": [dict(item, texto="Morirono quasi duemila persone",
                                                                         cita_literal="duemila")]}}
    pool = r3.merge_docs(per_doc, docs, event_year=1963)
    assert len(pool["datos"]) == 2 and not pool["_descartados"]


# ═══════════════════════════════════════════════════════════════
#  §1.2 — PDF enlazado que no nombra el evento
# ═══════════════════════════════════════════════════════════════

def test_pdf_enlazado_sin_el_evento_se_descarta(tmp_path, monkeypatch):
    portada = b"<html><body><p>Cromanon: las pericias</p><a href='/folleto.pdf'>pdf</a></body></html>"
    calls = []

    def get(url):
        calls.append(url)
        if url.endswith(".pdf"):
            return 200, b"%PDF-1.4 fake", "application/pdf", url
        return 200, portada, "text/html", url
    monkeypatch.setattr(r3, "pdf_to_text", lambda p: "Perfil editorial. Sumario. Productos. " * 400)
    monkeypatch.setattr(r3, "html_to_text", lambda c: "corta")
    monkeypatch.setattr(r3.time, "sleep", lambda s: None)
    f = [{"id": "F05", "slug": "perfil_2008", "url": "https://www.perfil.com/nota.phtml", "titulo": "Cromañón: pericias",
          "tipo": "prensa_posterior", "anio": 2008, "prioridad": 1}]
    log: list[str] = []
    man = r3.download_sources(f, tmp_path, place_re=r"\bCroma[ñn][oó]n\b", get=get, wayback=False, log=log)
    d = man["documentos"][0]
    assert not d["ok"] and any("PDF enlazado descartado" in x for x in log)
    assert any(c.endswith("folleto.pdf") for c in calls)


def test_pdf_enlazado_con_el_evento_entra(tmp_path, monkeypatch):
    def get(url):
        if url.endswith(".pdf"):
            return 200, b"%PDF-1.4 fake", "application/pdf", url
        return 200, b"<html><a href='/pericias.pdf'>pdf</a></html>", "text/html", url
    monkeypatch.setattr(r3, "pdf_to_text", lambda p: "Pericias del incendio de Cromañón. " * 200)
    monkeypatch.setattr(r3, "html_to_text", lambda c: "corta")
    monkeypatch.setattr(r3.time, "sleep", lambda s: None)
    f = [{"id": "F05", "slug": "perfil_2008", "url": "https://www.perfil.com/nota.phtml", "titulo": "x",
          "tipo": "prensa_posterior", "anio": 2008, "prioridad": 1}]
    man = r3.download_sources(f, tmp_path, place_re=r"\bCroma[ñn][oó]n\b", get=get, wayback=False)
    assert man["documentos"][0]["ok"] and man["documentos"][0]["via"] == "pdf_enlazado"


# ═══════════════════════════════════════════════════════════════
#  §1.3 — R3 con reintento; si no, extraccion_fallida
# ═══════════════════════════════════════════════════════════════

def _doc():
    return {"id": "F08", "titulo": "Clarín 2006", "tipo": "prensa_posterior", "anio": 2006, "fuente": "Clarín"}


def test_r3_reintenta_ante_una_caida_de_pro(monkeypatch):
    monkeypatch.setattr(r3, "R3_BACKOFF_S", 0.0)
    n = {"k": 0}

    def call(prompt, **kw):
        n["k"] += 1
        if n["k"] < 3:
            raise RuntimeError("RemoteProtocolError: Server disconnected")
        return {}
    out = r3.extract_document({"seed_title": "Cromañón"}, _doc(), "texto del documento " * 50, call=call)
    assert n["k"] == 3 and "_extraccion_fallida" not in out


def test_r3_marca_extraccion_fallida_y_sigue(monkeypatch):
    monkeypatch.setattr(r3, "R3_BACKOFF_S", 0.0)

    def call(prompt, **kw):
        raise RuntimeError("Server disconnected")
    log: list[str] = []
    out = r3.extract_document({"seed_title": "Cromañón"}, _doc(), "texto " * 50, call=call, log=log)
    assert out["_extraccion_fallida"][0]["parte"] == 1 and out["datos"] == []
    assert any("extracción fallida" in x for x in log)


# ═══════════════════════════════════════════════════════════════
#  §1.4 — R1: reintentos y Flash con búsqueda; focos con grounding
# ═══════════════════════════════════════════════════════════════

def test_r1_flash_alternativo_y_conteo_de_focos():
    pro_calls, alt_calls = [], []

    def search(prompt):
        pro_calls.append(prompt)
        if "informes completos" in prompt:         # foco 1: Pro sí busca
            return '{"fuentes": []}', [{"uri": "https://a.org/x", "title": "a"}]
        return '{"fuentes": []}', []

    def alt(prompt):
        alt_calls.append(prompt)
        return '{"fuentes": []}', [{"uri": "https://b.it/y", "title": "b"}] if "fallos" in prompt else []
    seed = {"seed_title": "Vajont", "lugar_idioma": "italiano", "nombres_lugar": ["Diga del Vajont", "Longarone"]}
    out = r3.discover_sources(seed, search=search, search_alt=alt, resolve=lambda u: u, annotate=lambda *a, **k: {})
    fg = out["_focos_grounding"]
    assert fg == {"pro": 1, "flash": 1, "sin": 2}
    assert len(pro_calls) == 1 + 3 * (1 + r3.R1_RETRIES) and r3.R1_RETRIES == 3
    assert len(alt_calls) == 3 and all('"Diga del Vajont"' in p and "italiano" in p for p in alt_calls)
