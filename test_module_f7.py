"""F7: research v3 (researcher_steps/research_v3.py) — fuentes solo del grounding, HTML/PDF → txt, cita literal con
posición, dedupe entre documentos, contaminación (por fecha y por lugar: el caso Burnley/Trinidad), cifra oficial y
verificación por texto. Sin red ni LLM."""
from __future__ import annotations

import copy
import json

import pytest

from researcher_steps import research_v3 as r3

PLACE = r"Orleans Parish|\bOPP\b|Katrina"
# F20: el vocabulario de la cárcel ya no está en el código: viene del perfil del caso. Estos tests son de Orleans.
VOC_ORLEANS = {"roles_testigo": ["preso", "presos", "recluso", "reclusos", "guardia", "guardias", "deputy", "deputies",
                                 "inmate", "inmates", "abogado"],
               "roles_antagonista": ["sheriff", "warden", "alguacil"],
               "sustantivos_conteo": ["presos", "presas", "reclusos", "reclusas", "prisioneros", "prisioneras",
                                      "internos", "detenidos", "evacuados", "individuos"],
               "lugares_excluidos": ["Hunt", "Angola", "Templeman", "paso elevado"]}
# F21: el sujeto del video (antes `SUBJECT_RE_DEFAULT`, Orleans para todos) sale del perfil del caso
SUBJECT_ORLEANS = r"\b(OPP|Prisi[oó]n Parroquial de Orleans|Orleans Parish Prison|c[aá]rcel de (?:Nueva )?Orleans)\b"


@pytest.fixture
def voc_orleans():
    r3.set_vocabulario(VOC_ORLEANS)
    yield
    r3.set_vocabulario(None)


# ── R1: fuentes ───────────────────────────────────────────────────────────────

GROUND = [
    {"title": "aclu.org", "uri": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AAA",
     "url": "https://www.aclu.org/publications/abandoned-abused-complete-report"},
    {"title": "hrw.org", "uri": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/BBB",
     "url": "https://www.hrw.org/news/2005/09/21/new-orleans-prisoners-abandoned-floodwaters"},
    {"title": "thelensnola.org", "uri": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/CCC",
     "url": "https://thelensnola.org/category/katrina20/"},
]


def _f(url, **kw):
    return r3._clean_fuente({"url": url, "titulo": kw.get("titulo", "t"), "tipo": kw.get("tipo", "informe_oficial"),
                             "anio": kw.get("anio", 2006), "prioridad": kw.get("prioridad", 1)})


def test_r1_only_grounding_urls():
    fuentes = [
        _f("https://www.hrw.org/news/2005/09/21/new-orleans-prisoners-abandoned-floodwaters"),        # exacta
        _f("https://www.aclu.org/report/abandoned-abused-complete-report", anio=2007),               # misma, otra ruta
        _f("https://www.justice.gov/sites/default/files/crt/legacy/opp_findings_9-11-09.pdf"),        # inventada
        _f("https://www.aclu.org/other/something-else-entirely"),                                     # mismo sitio, otra
    ]
    ok, rest, bad = r3.match_grounding(fuentes, GROUND)
    urls = {f["url"] for f in ok}
    assert urls == {GROUND[0]["url"], GROUND[1]["url"]}                     # solo URLs del grounding
    assert all(f["url"] in {g["url"] for g in GROUND} for f in ok)
    assert {f["url"] for f in bad} == {fuentes[2]["url"], fuentes[3]["url"]}
    assert rest == []                                                       # el listado /category/ no es documento
    hrw = next(f for f in ok if "hrw" in f["url"])
    assert hrw["match"] == "exacta" and hrw["anio"] == 2005                 # el año de la ruta manda


def test_r1_redirect_uri_counts_as_grounding():
    ok, _, bad = r3.match_grounding([_f(GROUND[0]["uri"])], GROUND)
    assert [f["url"] for f in ok] == [GROUND[0]["url"]] and not bad


def test_r1_discover_drops_memory_answers(tmp_path):
    calls = []

    def search(prompt):
        calls.append(prompt)
        fuentes = [{"url": GROUND[1]["url"], "titulo": "HRW", "tipo": "informe_oficial", "anio": 2005, "prioridad": 1},
                   {"url": "https://www.toledoblade.com/inventada", "titulo": "Blade", "tipo": "prensa_epoca",
                    "anio": 2005, "prioridad": 1}]
        chunks = [] if len(calls) == 1 else [{"title": "hrw.org", "uri": GROUND[1]["uri"]}]
        return json.dumps({"fuentes": fuentes}), chunks

    out = r3.discover_sources({"seed_title": "OPP"}, search=search, resolve=lambda u: GROUND[1]["url"],
                              cache=tmp_path / "c.json", annotate=lambda *a, **k: {"fuentes": []})
    assert "IMPORTANTE: no respondas de memoria" in calls[1]               # reintento con búsqueda obligatoria
    assert [f["url"] for f in out["fuentes"]] == [GROUND[1]["url"]]
    assert any("toledoblade" in f["url"] for f in out["_descartadas"])


def test_pista_covered():
    f = {"titulo": "Abandoned & Abused: Orleans Parish Prisoners in the Wake of Hurricane Katrina"}
    # F21: `_words` ya no resta orleans/parish/prison/katrina/hurricane: la pista nombra el título entero
    assert r3.pista_covered("ACLU, «Abandoned & Abused: Orleans Parish Prisoners after Hurricane Katrina» (2006)", f)
    assert not r3.pista_covered("Toledo Blade, «Arrested on misdemeanors, left to die in flooded jail»", f)


# ── R2: texto ─────────────────────────────────────────────────────────────────

HTML = b"""<html><head><title>x</title><script>var a=1;</script></head><body><nav>Menu Home About</nav>
<article><h1>Prisoners Abandoned to Floodwaters</h1>""" + b"".join(
    b"<p>Inmates at Orleans Parish Prison said the water rose to their chests on August 29, 2005. Paragraph %d.</p>" % i
    for i in range(60)) + b"</article><footer>Copyright</footer></body></html>"


def _pdf(text: str) -> bytes:
    """Un PDF mínimo de una página con `text` (para no depender de archivos de muestra)."""
    stream = f"BT /F1 12 Tf 72 720 Td ({text}) Tj ET".encode("latin-1")
    objs = [b"<< /Type /Catalog /Pages 2 0 R >>", b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R "
            b"/Resources << /Font << /F1 5 0 R >> >> >>",
            b"<< /Length %d >>\nstream\n" % len(stream) + stream + b"\nendstream",
            b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"]
    out, offs = b"%PDF-1.4\n", []
    for i, o in enumerate(objs, start=1):
        offs.append(len(out))
        out += b"%d 0 obj\n" % i + o + b"\nendobj\n"
    x = len(out)
    out += b"xref\n0 %d\n0000000000 65535 f \n" % (len(objs) + 1) + b"".join(b"%010d 00000 n \n" % o for o in offs)
    out += b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (len(objs) + 1, x)
    return out


def test_html_to_text_keeps_article_drops_chrome():
    t = r3.html_to_text(HTML)
    assert "water rose to their chests" in t and "var a=1" not in t
    assert r3.names_event(t, PLACE)


def test_pdf_to_text(tmp_path):
    p = tmp_path / "x.pdf"
    p.write_bytes(_pdf("Orleans Parish Prison report. " * 4))
    t = r3.pdf_to_text(p)
    assert "Orleans Parish Prison report" in t


def test_dehyphenate_and_cap_by_sections():
    assert r3.dehyphenate("concen-\ntration camp") == "concentration camp"
    body = ("Paragraph about the jail. " * 40 + "\n\n") * 300
    text = body + "ENDNOTES\n" + "1. note\n" * 5000
    out, why = r3.cap_text(text, limit=len(body) + 10)
    assert "ENDNOTES" not in out and "cola" in why
    out2, why2 = r3.cap_text(body, limit=10_000)
    assert len(out2) <= 10_000 and out2.endswith("jail.") and "párrafo" in why2


def test_download_wayback_and_dedupe(tmp_path, monkeypatch):
    pages = {"https://a.org/doc": (403, b"no", "text/html", "https://a.org/doc")}
    html = HTML

    def get(url):
        if url in pages:
            return pages[url]
        if "archive.org/wayback/available" in url:
            return 200, json.dumps({"archived_snapshots": {"closest": {
                "available": True, "url": "http://web.archive.org/web/20051001000000/https://a.org/doc"}}}).encode(), \
                "application/json", url
        if "web.archive.org/web/20051001000000id_/" in url:
            return 200, html, "text/html", url
        if url == "https://b.org/copy":
            return 200, html, "text/html", url
        raise AssertionError(url)
    monkeypatch.setattr(r3, "WAYBACK_PAUSE_S", 0)
    monkeypatch.setattr(r3.time, "sleep", lambda s: None)
    fs = [{"id": "F01", "slug": "a", "url": "https://a.org/doc", "titulo": "A", "tipo": "testimonio", "anio": 2005,
           "prioridad": 1}, {"id": "F02", "slug": "b", "url": "https://b.org/copy", "titulo": "B",
                             "tipo": "prensa_epoca", "anio": 2005, "prioridad": 2},
          {"id": "F03", "slug": "c", "url": "https://www.youtube.com/watch?v=x", "titulo": "C", "tipo": "documental",
           "anio": 2005, "prioridad": 2}]
    man = r3.download_sources(fs, tmp_path, place_re=PLACE, get=get)
    d = {x["id"]: x for x in man["documentos"]}
    assert d["F01"]["ok"] and d["F01"]["via"] == "wayback" and d["F01"]["intentos"][0]["status"] == 403
    assert d["F02"]["estado"] == "duplicado"
    assert d["F03"]["estado"] == "sin_texto" and d["F03"]["intentos"] == []
    assert (tmp_path / "manifest.json").exists() and (tmp_path / "a.txt").exists()


# ── R3: cita literal con posición ─────────────────────────────────────────────

DOC_A = ("ABANDONED AND ABUSED. Orleans Parish Prison, August 2005.\n"
         "On August 29, 2005, at 6:10 a.m., Hurricane Katrina made landfall. The jail held 6,375 prisoners.\n"
         "Dan Bright said: “They left us there to die, with no food, no water, lights, or medical attention.”\n"
         "Deputies abandoned Templeman III. The water rose to the second tier.\n")
DOC_B = ("Times story. In Orleans Parish, 7,000 prisoners were held, the paper estimated.\n"
         "The jail held 6,375 prisoners when the storm came, said Dan Bright, a prisoner in Templeman III.\n"
         "“They left us there to die,” Bright recalled.\n")
DOC_TRINIDAD = ("ACLU statement on prison conditions in Trinidad. Lenore Burnley said that her son Chad Joseph was "
                "beaten in custody in 2026. " * 60)
DOCS = [{"id": "F01", "titulo": "ACLU, Abandoned and Abused", "tipo": "informe_oficial", "anio": 2006, "prioridad": 1,
         "url": "https://aclu.org/a", "nombra_evento": True},
        {"id": "F02", "titulo": "Times", "tipo": "prensa_epoca", "anio": 2005, "prioridad": 2,
         "url": "https://times.com/b", "nombra_evento": True},
        {"id": "F03", "titulo": "ACLU Trinidad", "tipo": "prensa_posterior", "anio": 2026, "prioridad": 2,
         "url": "https://aclu.org/t", "nombra_evento": r3.names_event(DOC_TRINIDAD, PLACE)}]


def _raw_a():
    return {"datos": [
        {"texto": "La cárcel tenía 6,375 presos.", "tipo": "cifra", "valor": "6,375",
         "cita_literal": "The jail held 6,375 prisoners."},
        {"texto": "El agua llegó al segundo piso.", "tipo": "magnitud", "cita_literal": "The water rose to the second tier"},
        {"texto": "Inventado.", "tipo": "cifra", "cita_literal": "The jail held 9,999 prisoners in a palace"}],
        "cronologia": [{"fecha": "2005-08-29", "hora": "06:10", "evento": "Katrina toca tierra.",
                        "cita_literal": "On August 29, 2005, at 6:10 a.m., Hurricane Katrina made landfall"}],
        "lugares": [{"nombre": "Templeman III", "rol": "edificio", "cita_literal": "Deputies abandoned Templeman III."}],
        "citas": [{"autor": "Dan Bright", "rol": "preso", "testigo": True, "lugar": "Templeman III",
                   "texto_original": "They left us there to die, with no food, no water, lights, or medical attention.",
                   "texto_es": "Nos dejaron ahí para morir, sin comida, sin agua, sin luz ni atención médica.",
                   "cita_literal": "Dan Bright said: “They left us there to die, with no food, no water"}],
        "personajes": [{"nombre": "Dan Bright", "rol": "preso", "testigo": True, "fechas_presente": ["2005-08-29"],
                        "cita_literal": "Dan Bright said: “They left us there to die"}]}


def _raw_b():
    return {"datos": [
        {"texto": "La prisión tenía 6,375 presos cuando llegó la tormenta.", "tipo": "cifra",
         "cita_literal": "The jail held 6,375 prisoners when the storm came"},
        {"texto": "La prensa estimó 7,000 presos en la cárcel de Orleans Parish.", "tipo": "cifra",
         "cita_literal": "In Orleans Parish, 7,000 prisoners were held, the paper estimated."}],
        "cronologia": [], "lugares": [], "personajes": [],
        "citas": [{"autor": "Dan Bright", "rol": "preso", "testigo": True, "texto_original": "They left us there to die",
                   "texto_es": "Nos dejaron ahí para morir", "cita_literal": "“They left us there to die,” Bright recalled."}]}


def _raw_t():
    return {"datos": [{"texto": "Chad Joseph fue golpeado bajo custodia en 2026.", "tipo": "cifra", "fecha": "2026",
                       "cita_literal": "her son Chad Joseph was beaten in custody in 2026"}],
            "cronologia": [], "lugares": [], "personajes": [], "citas": [
                {"autor": "Lenore Burnley", "rol": "madre", "testigo": False, "fecha": "2026",
                 "texto_original": "her son Chad Joseph was beaten in custody", "texto_es": "su hijo fue golpeado",
                 "cita_literal": "Lenore Burnley said that her son Chad Joseph was beaten in custody"}]}


def _texts():
    return {"F01": r3.DocText("F01", DOC_A), "F02": r3.DocText("F02", DOC_B), "F03": r3.DocText("F03", DOC_TRINIDAD)}


def _per_doc():
    t = _texts()
    log = []
    return {"F01": r3.validate_doc_items(_raw_a(), {**DOCS[0], "idioma": "en"}, t["F01"], log),
            "F02": r3.validate_doc_items(_raw_b(), {**DOCS[1], "idioma": "en"}, t["F02"], log),
            "F03": r3.validate_doc_items(_raw_t(), {**DOCS[2], "idioma": "en"}, t["F03"], log)}


def test_locate_gives_raw_offset():
    dt = r3.DocText("F01", DOC_A)
    k = dt.locate("at 6:10 a.m., Hurricane Katrina made landfall")
    assert DOC_A[k:k + 6] == "at 6:1"
    assert dt.locate("Dan Bright said ... no food, no water, lights") == DOC_A.index("Dan Bright said")
    assert dt.locate("they left us in a palace") is None
    assert dt.longest_run("They left us there to die in the rain", 5) == 6      # «they left us there to die»
    assert dt.longest_run("They left us alone", 5) == 0


def test_every_item_has_findable_literal():
    part = _per_doc()["F01"]
    items = [it for k in r3.KINDS for it in part[k]]
    assert len(part["datos"]) == 2 and part["_descartados"][0]["motivo"] == "cita_literal no está en el documento"
    for it in items:
        assert it["doc_id"] == "F01" and it["offset"] is not None
        assert r3.DocText("F01", DOC_A).locate(it["cita_literal"]) == it["offset"]
    assert part["cronologia"][0]["hora"] == "06:10"
    assert part["citas"][0]["texto"].startswith("Nos dejaron") and part["citas"][0]["testimonio"] is True


def test_chunk_text_overlaps_and_covers():
    text = "\n".join(f"line {i} " + "x" * 80 for i in range(3000))
    ch = r3.chunk_text(text, size=20_000, overlap=2_000)
    assert len(ch) > 10 and ch[0][0] == 0
    assert all(len(c) <= 20_000 for _, c in ch)
    for (a, ca), (b, _) in zip(ch, ch[1:]):
        assert b < a + len(ca)                                             # solapan
    assert ch[-1][0] + len(ch[-1][1]) == len(text)


def test_focus_text_low_density():
    text = ("Other prisons in Texas and Ohio were inspected. " * 2000) + " Orleans Parish Prison was flooded. " + \
           ("More unrelated cases. " * 2000)
    out, why = r3.focus_text(text, PLACE)
    # F23 §1.2: la densidad baja se anota (métrica); el documento se lee entero
    assert why and "densidad baja" in why and out == text
    r3.FOCUS_SOLO_METRICA = False                                  # el recorte de antes sigue disponible
    try:
        out, why = r3.focus_text(text, PLACE)
        assert why and len(out) < 9000 and "Orleans Parish Prison was flooded" in out
    finally:
        r3.FOCUS_SOLO_METRICA = True
    dense = "Orleans Parish Prison. " * 4000
    assert r3.focus_text(dense, PLACE) == (dense, None)


# ── R4: merge, contaminación, canon ───────────────────────────────────────────

def test_merge_dedupes_between_docs_and_drops_contamination():
    pool = r3.merge_docs(_per_doc(), DOCS, event_year=2005)
    six = [d for d in pool["datos"] if "6,375" in d["texto"]]
    assert len(six) == 1 and six[0]["docs"] == ["F01", "F02"] and six[0]["n_fuentes"] == 2
    bright = [q for q in pool["citas"] if q["autor"] == "Dan Bright"]
    assert len(bright) == 1 and bright[0]["n_fuentes"] == 2
    texts = json.dumps(pool["datos"] + pool["citas"], ensure_ascii=False)
    assert "Burnley" not in texts and "Chad Joseph" not in texts             # caso Trinidad fuera
    motivos = [d["motivo"] for d in pool["_descartados"] if d.get("doc_id") == "F03"]
    assert motivos and all(m.startswith("contaminación") for m in motivos)
    assert [d["id"] for d in pool["datos"]][:2] == ["D01", "D02"]


def test_contamination_by_item_date():
    # F23 §1.1: nada posterior se descarta por año; antes de inicio − 20, sí
    assert r3.contamination({"fecha": "2026-03-01"}, 2005) is None
    assert r3.contamination({"fecha": "2025-08-29"}, 2005) is None
    assert r3.contamination({"fecha": "1980"}, 2005).startswith("fecha 1980")
    assert r3.doc_contamination({"nombra_evento": False}, 2005)
    assert r3.doc_contamination({"nombra_evento": True, "anio": 2031}, 2005) is None   # F8b: el año del documento ya no cuenta


def test_canonical_prefers_official(voc_orleans):
    pool = r3.merge_docs(_per_doc(), DOCS, event_year=2005)
    r3.canonical_v3(pool, DOCS, [])
    c = pool["cifras_canonicas"]
    assert len(c) == 1 and c[0]["valor"] == "6,375" and c[0]["fuente"] == "F01"
    assert c[0]["variantes"][0]["valor"] == "7,000" and c[0]["variantes"][0]["estatus"].startswith("estimación de Times")


# ── R5 y pool completo ────────────────────────────────────────────────────────

def test_build_pool_contract_and_verification():
    pool = r3.build_pool(_per_doc(), DOCS, _texts(), event_year=2005)
    for k in ("datos", "cronologia", "lugares", "citas", "personajes", "_descartados", "cifras_canonicas"):
        assert k in pool
    q = next(q for q in pool["citas"] if q["autor"] == "Dan Bright")
    assert q["verificacion"]["estado"] == "verificada" and q["verificacion"]["documento"] in ("F01", "F02")
    p = next(p for p in pool["personajes"] if p["nombre"] == "Dan Bright")
    assert p["testigo"] and p["testigo_verificado"] and p["n_citas"] == 1
    m = r3.metrics(pool)
    assert m["pct_doc_y_posicion"] == 100.0 and m["items_2_fuentes"] >= 2


def test_verification_states():
    pool = r3.merge_docs(_per_doc(), DOCS, event_year=2005)
    q = copy.deepcopy(next(q for q in pool["citas"] if q["autor"] == "Dan Bright"))
    t = _texts()
    q2 = {**copy.deepcopy(q), "id": "Q90", "texto_original": "They left us there to die in a burning palace",
          "docs": ["F01"]}
    q3 = {**copy.deepcopy(q), "id": "Q91", "texto_original": "Nothing like this was ever said", "docs": ["F01"]}
    q4 = {**copy.deepcopy(q), "id": "Q92", "autor": "Marlin Gusman", "docs": ["F01"],
          "texto_original": "Deputies abandoned Templeman III."}
    p = {"datos": [], "cronologia": [], "lugares": [], "personajes": [], "citas": [q, q2, q3, q4]}
    c = r3.verify_pool(p, t, DOCS)
    est = {x["id"]: x["verificacion"]["estado"] for x in p["citas"]}
    assert est[q["id"]] == "verificada" and est["Q90"] == "verificada_parcial" and est["Q91"] == "sin_verificar"
    assert est["Q92"] == "verificada_parcial"                               # literal, pero Gusman no está cerca
    assert c == {"verificada": 1, "verificada_parcial": 2, "sin_verificar": 1}


def test_escaleta_reads_v3_pool():
    """Integración sin LLM: el prompt de la escaleta (m01a) se arma con el pool v3."""
    from script_engine import m01a_escaleta as me
    pool = r3.build_pool(_per_doc(), DOCS, _texts(), event_year=2005)
    prompt = me.build_prompt({"id": "t", "video_title": "OPP", "evidence_pool": pool, "verified_facts": []}, pool)
    assert "Dan Bright" in prompt and "VERIFICADA" in prompt


def test_flag_on_by_default(monkeypatch):
    """F7d (§9.2): research v3 es el default para seeds nuevos; RESEARCH_V3=0 vuelve al camino viejo."""
    monkeypatch.delenv("RESEARCH_V3", raising=False)
    assert r3.research_v3_enabled({})
    monkeypatch.setenv("RESEARCH_V3", "0")
    assert not r3.research_v3_enabled({})
    assert r3.research_v3_enabled({"research_version": 3})


# ── reglas que salieron de los documentos reales (F7b) ────────────────────────

def test_ocr_without_spaces_and_footnote_markers():
    ocr = "we nowwrite to advise youofthe findings ofourinvestigation, the facts supportingthem, andthe minimum steps"
    dt = r3.DocText("F09", ocr)
    assert dt.locate("we now write to advise you of the findings of our investigation, the facts") == 0
    assert dt.locate("we now write") is None                                # corta: sin segundo intento
    assert r3.dehyphenate("held at OPP.11This number, OPP,17$2.00 and charges,14\nsuch") == \
        "held at OPP.This number, OPP,$2.00 and charges,\nsuch"
    assert r3.dehyphenate("pays $24.39 per day to 1,300 people in 2005.1 The") == \
        "pays $24.39 per day to 1,300 people in 2005.1 The"


def test_chronology_date_must_match_literal_year():
    text = "On August 10, 2001, another prisoner noticed that Mr. Duncan was not breathing in Orleans Parish Prison."
    raw = {"datos": [], "lugares": [], "citas": [], "personajes": [], "cronologia": [
        {"fecha": "2005-08-10", "evento": "Duncan no respira.", "cita_literal": "On August 10, 2001, another prisoner noticed"},
        {"fecha": "2001-08-10", "evento": "Duncan no respira.", "cita_literal": "On August 10, 2001, another prisoner noticed"}]}
    part = r3.validate_doc_items(raw, {**DOCS[0], "idioma": "en"}, r3.DocText("F01", text), [])
    assert [c["fecha"] for c in part["cronologia"]] == ["2001-08-10"]
    assert "no coincide con el año" in part["_descartados"][0]["motivo"]


def test_people_names_and_eligibility(voc_orleans):
    assert r3.same_person("Sgt. Bell", "Sergeant Bell") and r3.same_person("Marlin N. Gusman", "Sheriff Martin Gusman")
    assert not r3.same_person("Christina Foster", "Mike Foster")
    assert r3.is_named_person("Deputy Foster") and r3.is_named_person("Keanna Herbert")
    assert not r3.is_named_person("Abogado del Sheriff") and not r3.is_named_person("Oficiales en Conchetta")
    pool = {"datos": [{"texto": f"Bright vio el agua {i}"} for i in range(3)], "citas": [],
            "cronologia": [{"id": "T01", "fecha": "2001-08-10", "evento": "Duncan muere"},
                           {"id": "T02", "fecha": "2005-08-29", "evento": "El agua sube"}],
            "personajes": [
                {"nombre": "Dan Bright", "testigo": True, "fechas_presente": [], "presente_en": ["T02"]},
                {"nombre": "Marlin Gusman", "testigo": True, "antagonista": True, "fechas_presente": ["2005-08-29"],
                 "presente_en": []},
                {"nombre": "Shawn Duncan", "testigo": True, "fechas_presente": [], "presente_en": ["T01"]}]}
    pool["datos"] += [{"texto": f"Gusman ordenó {i}"} for i in range(3)] + [{"texto": f"Duncan {i}"} for i in range(3)]
    r3.person_stats(pool, 2005)
    # F20: la presencia en el año ya no excluye (Duncan, muerto en 2001, es elegible y queda presente_en_evento False)
    assert [p["elegible_humano"] for p in pool["personajes"]] == [True, False, True]
    assert [p["presente_en_evento"] for p in pool["personajes"]] == [True, False, False]
    p = {"personajes": [{"nombre": "Sheriff Gusman", "variantes_nombre": ["Marlin N. Gusman", "Gusman"]}]}
    r3.canonical_names(p, {"a": r3.DocText("a", "Marlin N. Gusman said. Gusman left. Gusman. Marlin N. Gusman")})
    assert p["personajes"][0]["nombre"] == "Marlin N. Gusman"


def test_count_value_takes_the_number_next_to_the_noun(voc_orleans):
    assert r3.count_value("La cárcel tenía 6,375 presos el 29 de agosto de 2005.") == ("6,375", 6375)
    assert r3.count_value("En junio había 6,295 reclusos; el promedio fue 5,919 reclusos.") is None   # dos: rango
    # F23 §1.2: el piso es 10 (antes 1000): «800 presos» también es un conteo → dos conteos, no hay canónica
    assert r3.count_value("En 1974 había 800 presos; en 2004, 6,500 presos.") is None
    assert r3.count_value("En 2004 había 6,500 presos.") == ("6,500", 6500)
    assert r3.count_value("Murieron 327 personas.") == ("327", 327)
    assert r3.count_value("La capacidad era de 8,000 camas.") is None


# ── F7c: presencia por párrafo, población, digest ─────────────────────────────

PRES_DOC = ("Tyrone Lewis was arrested in July. " + "x " * 400 + "\nOn August 29 the water rose in Templeman III. "
            + "y " * 400 + "\nDuane Lewis, a deputy, stayed at his post on August 30. " + "z " * 400
            + "\nOn September 1 the evacuation began from the overpass.")


def _pres_pool():
    def ev_(i, fecha, evento, lit):
        return {"id": i, "fecha": fecha, "evento": evento, "doc_id": "F01", "offset": PRES_DOC.index(lit),
                "cita_literal": lit, "evidencia": [{"doc_id": "F01", "offset": PRES_DOC.index(lit), "cita_literal": lit}]}
    return {"datos": [], "citas": [], "lugares": [],
            "cronologia": [ev_("T01", "2005-08-29", "El agua sube en Templeman III.", "On August 29 the water rose"),
                           ev_("T02", "2005-08-30", "Un guardia se queda en su puesto.", "Duane Lewis, a deputy, stayed"),
                           ev_("T03", "2005-09-01", "Empieza la evacuación.", "On September 1 the evacuation began")],
            "personajes": [{"id": "P01", "nombre": "Tyrone Lewis", "testigo": True,
                            "fechas_presente": ["2005-08-29", "2005-08-30", "2005-08-31", "2005-09-01"]},
                           {"id": "P02", "nombre": "Duane Lewis", "testigo": True, "fechas_presente": []}]}


def test_presence_by_paragraph_never_by_date_range():
    pool = _pres_pool()
    r3.presence_v3(pool, {"F01": r3.DocText("F01", PRES_DOC)})
    p = {x["nombre"]: x["presente_en"] for x in pool["personajes"]}
    assert p["Duane Lewis"] == ["T02"]                       # su cita literal lo nombra
    assert p["Tyrone Lewis"] == []                           # sus fechas cubren T01–T03, pero ningún párrafo lo nombra
    assert r3.name_terms(pool["personajes"][0], pool["personajes"]) == ["tyrone lewis"]   # «lewis» es ambiguo
    near = PRES_DOC.replace("x " * 400, "x " * 100)        # Tyrone a < 500 caracteres del evento del agua
    pool2 = _pres_pool()
    for c in pool2["cronologia"]:
        c["evidencia"][0]["offset"] = near.index(c["cita_literal"])
    r3.presence_v3(pool2, {"F01": r3.DocText("F01", near)})
    assert pool2["personajes"][0]["presente_en"] == ["T01"]


def test_population_canon_lists_all_variants_with_source(voc_orleans):
    docs = [{"id": "F01", "titulo": "ACLU", "tipo": "informe_oficial", "anio": 2006, "prioridad": 1, "url": "u"},
            {"id": "F08", "titulo": "Vera", "tipo": "informe_oficial", "anio": 2015, "prioridad": 1, "url": "v"},
            {"id": "F10", "titulo": "The Lens", "tipo": "prensa_posterior", "anio": 2025, "prioridad": 2, "url": "w"}]
    pool = {"datos": [
        {"id": "D01", "doc_id": "F01", "texto": "Según el sheriff, la OPP tenía 6375 presos el 29 de agosto."},
        {"id": "D02", "doc_id": "F08", "texto": "El 30 de junio de 2005 había 6.295 reclusos en la Prisión Parroquial de Orleans."},
        {"id": "D03", "doc_id": "F10", "texto": "La cárcel de Nueva Orleans tenía 6,500 presos."},
        {"id": "D04", "doc_id": "F01", "texto": "En Hunt, 5,000 presos de la OPP esperaron en un patio."},     # otro lugar
        {"id": "D05", "doc_id": "F10", "texto": "6.375 personas estaban detenidas en la OPP."}]}
    g = r3.population_canon(pool, docs, SUBJECT_ORLEANS)
    assert g["oficial"] == "D01" and g["valor"] == "6,375" and not g["sin_oficial"]
    assert {v["valor"] for v in g["variantes"]} == {"6,295", "6,500", "6,375"}
    assert next(v for v in g["variantes"] if v["id"] == "D03")["estatus"] == "según The Lens (2025)"
    assert next(v for v in g["variantes"] if v["id"] == "D05")["estatus"] == "oficial (mismo valor)"
    docs2 = [{**d, "tipo": "prensa_posterior"} for d in docs]
    g2 = r3.population_canon(copy.deepcopy(pool), docs2, SUBJECT_ORLEANS)
    assert g2["sin_oficial"] and g2["oficial"] is None
    assert all(v["estatus"].startswith("según ") for v in g2["variantes"])


def test_digest_has_real_ids_and_escaleta_uses_it(monkeypatch):
    from script_engine import m01a_escaleta as me
    pool = r3.build_pool(_per_doc(), DOCS, _texts(), event_year=2005)
    dg = pool["digest"]
    its = {it["id"] for k in r3.KINDS for it in pool[k]}
    assert dg["ids"] and set(dg["ids"]) <= its and "DATOS POR DOCUMENTO" in dg["texto"]
    topic = {"id": "t", "video_title": "OPP", "evidence_pool": pool, "verified_facts": []}
    assert dg["texto"] in me.build_prompt(topic, pool)
    monkeypatch.setenv("ESCALETA_DIGEST", "0")
    assert dg["texto"] not in me.build_prompt(topic, pool)
    old = {k: v for k, v in pool.items() if k != "digest"}
    monkeypatch.delenv("ESCALETA_DIGEST")
    assert me.pool_section(old) == me.pool_section({**old})                 # sin digest: el camino de siempre
    assert "DATOS, CRONOLOGÍA Y LUGARES" in me.pool_section(old)


def test_one_word_quote_is_not_a_quote():
    raw = {"datos": [], "cronologia": [], "lugares": [], "personajes": [], "citas": [
        {"autor": "an officer", "texto_original": "no", "texto_es": "no", "testigo": True,
         "cita_literal": "Deputies abandoned Templeman III."}]}
    part = r3.validate_doc_items(raw, {**DOCS[0], "idioma": "en"}, r3.DocText("F01", DOC_A), [])
    assert part["citas"] == [] and "menos de 3 palabras" in part["_descartados"][0]["motivo"]


def test_pool_does_not_trip_f6_validators():
    """Los validadores de F6 (m05) leen el pool: un descarte de lectura no veta palabras y las cifras canónicas se
    escriben con coma de miles."""
    from script_engine import m05_narrative as mn
    raw = {"datos": [], "cronologia": [], "lugares": [], "citas": [],
           "personajes": [{"nombre": "Preso #13", "rol": "preso", "testigo": True, "cita_literal": "Deputies abandoned Templeman III."}]}
    part = r3.validate_doc_items(raw, {**DOCS[0], "idioma": "en"}, r3.DocText("F01", DOC_A), [])
    pool = {"_descartados": part["_descartados"]}
    assert part["_descartados"][0]["kind"] == "personajes_r3"
    assert mn.silent_names("Un preso gritó en la oscuridad.", pool) == []
    g = {"oficial": "D01", "valor": "6,375", "variantes": [{"id": "D02", "valor": "6,000", "estatus": "según X"}]}
    assert mn.non_canonical("Había 6,375 presos.", {"cifras_canonicas": [g]}, {}) == []
    assert mn.non_canonical("Había 6,000 presos.", {"cifras_canonicas": [g]}, {})


# ── F7c-2: parámetros de largo, fragmento de cita y reglas duras nuevas ───────

def test_length_params_from_config():
    from script_engine import m01a_escaleta as me
    from script_engine import video_length as vl
    from script_engine.m01a_skeleton import CHAPTER_SCHEMA
    from script_engine.m03_visual import _calculate_flux_extras_count, _calculate_image_count
    assert [vl.get(k) for k in ("target_words", "max_words", "dev_cap_seconds", "max_images_per_video")] == \
        [1500, 2200, 105, 90]                                              # F25c: tope 1700 → 2200
    assert me.CAP_WORDS == {1: 110, 2: 250, 3: 250, 4: 250, 5: 250, 6: 250, 7: 140}      # §9.1: 1,500
    assert [c["duration_seconds"] for c in CHAPTER_SCHEMA] == [45, 105, 105, 105, 105, 105, 45]
    dev = sum(_calculate_image_count(400, n) for n in range(2, 7))          # caps larguísimos: manda el tope
    assert dev + 2 * _calculate_flux_extras_count(45) <= vl.get("max_images_per_video")
    assert _calculate_image_count(75, 3) == 12                              # un cap normal no cambia (11 + 1 de posición)


def test_quote_fragment_is_literal_and_short():
    long_q = ("Parecía que estaban abatiendo a la gente. Ves a alguien caer. No sé si les estaban disparando con "
              "munición real o qué; caían al agua y eso fue suficiente para que yo lo viera allí mismo, desde la "
              "terraza del edificio, sin poder hacer nada por ellos.")
    f = r3.quote_fragment(long_q)
    assert f in long_q and r3.FRAGMENT_MIN_WORDS <= len(f.split()) <= r3.FRAGMENT_MAX_WORDS
    assert r3.quote_fragment("Nos dejaron morir allí.") == "Nos dejaron morir allí."
    one = "todo el mundo tenía que pelear para conseguir un sándwich, " * 4
    assert len(r3.quote_fragment(one).split()) <= 25 and r3.quote_fragment(one) in one
    from script_engine import evidence as ev
    q = {"_kind": "citas", "texto": long_q, "fragmento": f}
    assert ev.anchors(q) == [f, long_q]
    assert ev.anchors({"_kind": "citas", "texto": "Nos dejaron morir allí."}) == ["Nos dejaron morir allí."]


def test_one_literal_quote_per_paragraph():
    from script_engine.guion_v3_reglas import quotes_per_paragraph
    ok = [{"beat": 1, "texto": "Reed lo dijo: «los oficiales empezaron a renunciar a diestra y siniestra». «Templeman»."}]
    bad = [{"beat": 2, "texto": "«Nos dejaron morir allí, hombre», dijo Burton. Y Reyes: «todavía hay presos muertos ahí»."}]
    assert quotes_per_paragraph(ok) == [] and quotes_per_paragraph(bad)


def test_hook_rules():
    from script_engine.guion_v3_reglas import hook_problems
    later = ["Tuvimos que beber agua del inodoro solo para mantenernos con vida"]
    assert hook_problems("El agua negra llega al pecho. Nadie viene. Huele a cloaca.", later) == []
    p = hook_problems("La foto es del 31 de agosto de 2005: tuvimos que beber agua del inodoro para vivir.", later)
    assert any("fechas" in x for x in p)                     # las fotos: photo_problems, en todos los caps (F7c-3)
    assert any("adelanta" in x for x in hook_problems("Contó: «tuvimos que beber agua del inodoro solo para»", later))


def test_judgments_outside_pool_are_hard():
    from script_engine.guion_v3_reglas import judgment_problems
    pool = {"datos": [{"id": "D01", "texto": "Los guardias arrojaban sándwiches a los presos."}]}
    assert judgment_problems("Un caos deliberado. Ya no eran considerados humanos.", pool)
    assert judgment_problems("Arrojaban sándwiches a la multitud.", pool) == []
    pool2 = {"datos": [{"id": "D01", "texto": "Un abogado dijo que fue un castigo deliberado."}]}
    assert judgment_problems("Fue un castigo deliberado.", pool2) == []                 # lo dice el documento


def test_full_name_once_per_cap_and_cross_cap_repetition():
    from script_engine.guion_v3_reglas import full_name_problems, repetition_problems
    caps = [{"chapter_number": 2, "narration": "Renard Reed vio todo. Más tarde, Renard Reed volvió."},
            {"chapter_number": 3, "narration": "Renard Reed habló una vez. Reed calló."}]
    assert full_name_problems(caps, "Renard Reed") == [
        "cap 2: el nombre completo de Renard Reed suena 2 veces; una vez por cap, después solo el apellido"]
    pool = {"personajes": [{"nombre": "Renard Reed"}], "lugares": [{"nombre": "Templeman III"}]}
    caps2 = [{"chapter_number": 1, "narration": "Los oficiales empezaron a renunciar. El agua subía en Templeman III."},
             {"chapter_number": 2, "narration": "Otra vez, los oficiales empezaron a renunciar. Templeman III quedó a oscuras."}]
    rep = repetition_problems(caps2, pool)
    assert len(rep) == 1 and "oficiales empezaron renunciar" not in rep[0] and "«oficiales empezaron a»" in rep[0]
    assert repetition_problems([caps2[0], {"chapter_number": 2, "narration": "En Templeman III el agua."}], pool) == []


# ── F7c-3 (HANDOFF_F7 §9.1): una prueba por regla ────────────────────────────

POOL_C3 = {
    "personajes": [{"id": "P01", "nombre": "Rhonda Ducre", "rol": "Alguacil en el edificio HOD"},
                   {"id": "P02", "nombre": "Big Whappy", "rol": "Preso"},
                   {"id": "P03", "nombre": "Marlin Gusman", "rol": "sheriff", "antagonista": True}],
    "citas": [{"id": "Q01", "autor": "Big Whappy", "rol": "Preso", "texto": "Hombre, ese lugar olía a muerte.",
               "fragmento": "Hombre, ese lugar olía a muerte."},
              {"id": "Q02", "autor": "Marlin Gusman", "rol": "sheriff",
               "texto": "Vamos a mantener a nuestros prisioneros donde pertenecen.",
               "verificacion": {"estado": "verificada_parcial"}}],
    "cronologia": [{"id": "T39", "fecha": "2005-08-28", "evento": "El sheriff Gusman mantuvo una reunión para discutir el huracán.",
                    "verificacion": {"estado": "verificada"}}],
    "datos": [], "lugares": [{"id": "L01", "nombre": "Nueva Orleans", "rol": "ciudad"}],
}


def test_rule1_role_of_speaker():
    from script_engine.guion_v3_reglas import role_problems, role_class
    # F21: las clases salen del perfil del caso (testigo / antagonista); sin perfil, ninguna
    assert role_class("Preso") is None and role_problems("La reclusa Rhonda Ducre lo resumió.", POOL_C3) == []
    r3.set_vocabulario({"roles_testigo": ["preso", "presos", "reclusa", "recluso"],
                        "roles_antagonista": ["alguacil", "guardia", "sheriff"]})
    assert role_class("Alguacil en el edificio HOD") == "antagonista" and role_class("Preso") == "testigo"
    p = role_problems("La reclusa Rhonda Ducre lo resumió. Un guardia lo describió: «Hombre, ese lugar olía a muerte».", POOL_C3)
    assert any("Rhonda Ducre" in x for x in p) and any("Q01" in x for x in p)
    assert role_problems("La guardia Rhonda Ducre lo resumió. Un preso lo describió: «Hombre, ese lugar olía a muerte».",
                         POOL_C3) == []
    assert any("Rhonda Ducre, una reclusa" in x for x in role_problems("Rhonda Ducre, una reclusa, lo vio.", POOL_C3))
    r3.set_vocabulario(None)


def test_rule2_paragraph_without_id_is_filler():
    from script_engine.guion_v3_reglas import empty_paragraph_problems
    filler = {"beat": 4, "ids_usados": [], "texto": "Era una tumba sellada. Nadie venía. Afuera, la ciudad se ahogaba."}
    bridge = {"beat": 5, "ids_usados": [], "texto": "Pero eso no fue lo peor. Lo peor llegó con la luz."}
    data = {"beat": 6, "ids_usados": ["T39"], "texto": "Una. Dos. Tres. Cuatro."}
    assert len(empty_paragraph_problems([filler, bridge, data])) == 1


def test_rule3_antagonist_named_and_partial_quote_allowed():
    from script_engine import m01b_guionista as mg
    from script_engine.guion_v3_reglas import antagonist_problems
    esc = {"antagonista": {"id": "P03"}, "beats": [{"n": 2, "cap": 2, "dato_central": "T39", "datos_apoyo": ["Q02"]}]}
    caps = [{"chapter_number": 2, "narration": "El 28 de agosto hubo una reunión. La orden fue clara, según alguien."}]
    p = antagonist_problems(caps, esc, POOL_C3)
    assert any("no se nombra" in x for x in p) and any("según alguien" in x for x in p)
    ok = [{"chapter_number": 2, "narration": "El sheriff Marlin Gusman se reunió el 28 de agosto."}]
    assert antagonist_problems(ok, esc, POOL_C3) == []
    assert mg._verified_antagonist(esc, POOL_C3, "Gusman") and not mg._verified_antagonist(esc, POOL_C3, "Ducre")


def test_rule4_no_photos_in_any_cap():
    from script_engine.guion_v3_reglas import photo_problems
    caps = [{"chapter_number": 1, "narration": "El agua sube."},
            {"chapter_number": 6, "narration": "Las imágenes dieron la vuelta al mundo. Una fotógrafa tomó la foto."}]
    p = photo_problems(caps)
    assert len(p) == 1 and p[0].startswith("cap 6")


def test_rule5_no_trailer_voice():
    from script_engine.guion_v3_reglas import trailer_problems
    assert len(trailer_problems("Es la historia de la orden y de los testigos que se negaron a olvidar.")) == 2
    assert trailer_problems("Una verdad que algunos testigos se niegan a olvidar.")
    assert trailer_problems("El agua llegó al pecho el 30 de agosto.") == []


def test_rule6_hook_anchor_place_and_year():
    from script_engine.guion_v3_reglas import hook_anchor_problems, hook_problems
    good = ("El agua negra llega al pecho. Nadie viene. «Tuvimos que beber agua del inodoro para vivir», contó Burton. "
            "Nueva Orleans, agosto de 2005. «Hombre, ese lugar olía a muerte», dijo un preso.")
    assert hook_anchor_problems(good, POOL_C3) == [] and hook_problems(good, [], POOL_C3) == []
    pool_p = {**POOL_C3, "lugares": [{"id": "L01", "nombre": "Nueva Orleans, Luisiana"}]}     # coma en el nombre
    assert hook_anchor_problems("Nadie viene. Ni nadie. Nueva Orleans, agosto de 2005. El agua sube.", pool_p) == []
    late = ("El agua negra llega al pecho. «Tuvimos que beber agua del inodoro para vivir», contó Burton. «Hombre, ese "
            "lugar olía a muerte», dijo un preso. Nueva Orleans, agosto de 2005.")
    assert hook_anchor_problems(late, POOL_C3) == ["gancho: el ancla de lugar y fecha va antes de la segunda cita"]
    assert hook_anchor_problems("El agua negra llega al pecho. Nadie viene.", POOL_C3)


def test_rule7_echo_after_quote_is_soft_and_goes_to_editor():
    from script_engine import m01c_editor as mc
    from script_engine.guion_v3_reglas import echo_soft
    ps = [{"beat": 1, "cap": 1, "ids_usados": ["Q01"],
           "texto": "Burton contó: «Tuvimos que beber agua del inodoro para vivir». Era la única opción. El agua subía."}]
    soft = echo_soft(ps)
    assert soft and "Era la única opción" in soft[0]
    assert "CITA FUERTE, SILENCIO DESPUÉS" in mc.build_prompt({"beats": [], "pico": {}}, ps, soft)
    assert echo_soft([{**ps[0], "texto": "Burton contó: «Tuvimos que beber agua del inodoro para vivir». El 30 de "
                                         "agosto el agua llegó al segundo piso."}]) == []
