"""
test_module_f24.py — F24 §A (fuentes que se acumulan: registro por tema, R1 unido con prioridad por aporte, R2 que no
vuelve a bajar, R3 que no vuelve a extraer el mismo texto) y §B (entre 1 y 3 beats por cap como bloqueante; prompt de la
escaleta f24-1 con una sola línea cambiada). Sin red.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from researcher_steps import research_v3 as r3
from script_engine import m01a_escaleta as me

ROOT = Path(__file__).resolve().parent
F24 = ROOT / "lab" / "hyperframes" / "f24"
F22 = ROOT / "lab" / "hyperframes" / "f22"
STEPS = ROOT / "data" / "scripts" / "_steps"
KYS = STEPS / "f18-kyshtym-mayak"
OSETROV = "cyberleninka.ru/article/n/kyshtymskaya-radiatsionnaya-avariya-1957-goda"


def _md5(s: str) -> str:
    return hashlib.md5(s.encode("utf-8")).hexdigest()


def _sistema(path: Path) -> str:
    md = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    i = md.index("\n## SISTEMA\n\n") + len("\n## SISTEMA\n\n")
    return md[i:md.index("\n\n---\n", i)]


def _f(i: int, url: str, idioma: str = "en", prioridad: int = 2) -> dict:
    return {"id": f"F{i:02d}", "url": url, "titulo": f"doc {i}", "tipo": "prensa_posterior", "anio": 2000,
            "idioma": idioma, "prioridad": prioridad, "por_que": "x"}


# ═══════════════════════════════════════════════════════════════
#  A. Registro de fuentes
# ═══════════════════════════════════════════════════════════════

def _disco(tmp_path: Path) -> Path:
    """Un tema con una corrida vieja en disco: R1 de 2 fuentes, manifest con 1 bajada y un pool que salió de ella."""
    d = tmp_path / "t"
    (d / "fuentes").mkdir(parents=True)
    (d / "fuentes" / "a-F01.txt").write_text("texto A " * 200, encoding="utf-8")
    (d / "fuentes.json").write_text(json.dumps({"fuentes": [_f(1, "https://a.org/x"), _f(2, "https://b.org/y")],
                                                "prompt_version": "f7a-1"}), encoding="utf-8")
    (d / "fuentes" / "manifest.json").write_text(json.dumps({"documentos": [
        {**_f(1, "https://a.org/x"), "ok": True, "txt": "a-F01.txt", "caracteres": 1600, "estado": "ok"},
        {**_f(2, "https://b.org/y"), "ok": False, "estado": "error", "motivo": "404"}]}), encoding="utf-8")
    (d / "00_pool_v3_f20.json").write_text(json.dumps({
        "datos": [{"id": "D1", "doc_id": "F01"}, {"id": "D2", "doc_id": "F01"}], "citas": [{"id": "Q1", "doc_id": "F01"}],
        "personajes": [{"id": "P1", "doc_id": "F01", "docs": ["F01"]}], "cronologia": [],
        "_research_v3": {"documentos": [{"id": "F01", "url": "https://a.org/x", "txt": "a-F01.txt",
                                         "caracteres": 1600}]}}), encoding="utf-8")
    return d


def test_registro_desde_disco_suma_r1_manifest_y_pool(tmp_path):
    reg = r3.cargar_registro(_disco(tmp_path))            # fuentes.json viejo (salida de R1) → se arma de disco
    by = {e["url"]: e for e in reg["fuentes"]}
    assert reg["registro"] == r3.REGISTRO_VERSION and set(by) == {"https://a.org/x", "https://b.org/y"}
    a, b = by["https://a.org/x"], by["https://b.org/y"]
    assert a["bajada_ok"] and a["chars"] == 1600 and a["aporte"] == {"datos": 2, "citas": 1, "personajes": 1}
    assert a["doc"]["txt"] == "a-F01.txt" and a["veces_vista"] == 3      # R1, manifest y pool
    assert not b["bajada_ok"] and b["aporte"] is None
    assert r3.previos_del_registro(reg) == {"https://a.org/x": a["doc"]}


def test_unir_fuentes_suma_lo_del_registro_y_ordena_por_aporte(tmp_path):
    reg = r3.cargar_registro(_disco(tmp_path))
    nuevas = [_f(1, "https://c.org/z", prioridad=1), _f(2, "https://b.org/y", prioridad=1)]
    out = r3.unir_fuentes(nuevas, reg)
    assert [f["url"] for f in out] == ["https://a.org/x", "https://c.org/z", "https://b.org/y"]   # aporte 4 primero
    assert [f["id"] for f in out] == ["F01", "F02", "F03"] and out[0]["_aporte"] == 4 and out[0]["_registro"]
    assert not out[1]["_registro"] and out[2]["_registro"] and out[0]["slug"].endswith("-F01")


def test_r2_no_vuelve_a_bajar_lo_del_registro_y_el_cupo_va_al_aporte(tmp_path):
    d = _disco(tmp_path)
    reg = r3.cargar_registro(d)
    (d / "fuentes" / "manifest.json").unlink()             # sin manifest de la corrida: solo el registro
    pedidas = []

    def get(url):
        pedidas.append(url)
        return 404, b"", "text/html", url
    cands = r3.unir_fuentes([_f(1, "https://c.org/z", prioridad=1)], reg)
    man = r3.download_sources(cands, d / "fuentes", place_re=r"texto", get=get, wayback=False, max_ok=1,
                              previos=r3.previos_del_registro(reg))
    docs = {x["url"]: x for x in man["documentos"]}
    assert "https://a.org/x" not in pedidas and docs["https://a.org/x"]["ok"]       # reusada, sin pedir
    assert docs["https://a.org/x"]["id"] == "F01" and docs["https://a.org/x"]["txt"] == "a-F01.txt"


def test_r3_no_vuelve_a_extraer_el_mismo_texto_con_otro_id(tmp_path):
    texto = "El 29 de septiembre de 1957 explotó un tanque en Mayak. " * 30
    llamadas = []

    def call(prompt, **k):
        llamadas.append(prompt)
        return {"datos": [], "cronologia": [], "lugares": [], "citas": [], "personajes": []}
    seed = {"seed_title": "Kyshtym"}
    r3.extract_document(seed, {"id": "F07", "titulo": "t", "url": "https://a.org/x"}, texto, call=call,
                        cache_dir=tmp_path)
    n = len(llamadas)
    log: list[str] = []
    r3.extract_document(seed, {"id": "F02", "titulo": "otro título", "url": "https://a.org/x"}, texto, call=call,
                        cache_dir=tmp_path, log=log)
    assert n >= 1 and len(llamadas) == n and any("ya extraídos (sin llamadas)" in x for x in log)
    r3.extract_document(seed, {"id": "F02", "titulo": "t"}, texto + " Otro párrafo distinto.", call=call,
                        cache_dir=tmp_path)
    assert len(llamadas) > n                                # otro texto: se extrae


def test_actualizar_registro_suma_la_corrida(tmp_path):
    reg = r3.cargar_registro(_disco(tmp_path))
    cands = r3.unir_fuentes([_f(1, "https://c.org/z")], reg)
    c = next(f for f in cands if f["url"] == "https://c.org/z")
    man = {"documentos": [{**c, "ok": True, "txt": "c.txt", "caracteres": 900, "estado": "ok"}]}
    pool = {"datos": [{"doc_id": c["id"]}], "citas": [], "personajes": []}
    r3.actualizar_registro(reg, cands, [c], man, pool, {c["id"]})
    e = next(x for x in reg["fuentes"] if x["url"] == "https://c.org/z")
    assert e["veces_vista"] == 1 and e["bajada_ok"] and e["aporte"] == {"datos": 1, "citas": 0, "personajes": 0}
    a = next(x for x in reg["fuentes"] if x["url"] == "https://a.org/x")
    assert a["aporte"] == {"datos": 2, "citas": 1, "personajes": 1}       # no se extrajo esta vez: queda el de antes


def test_run_seed_deja_registro_y_salida_de_r1(tmp_path, monkeypatch):
    d = _disco(tmp_path)
    (d / "_perfil.json").write_text(json.dumps({"anio_evento": 1957, "place_re": r"texto", "roles_testigo": [],
                                                "roles_antagonista": []}), encoding="utf-8")
    monkeypatch.setattr(r3, "discover_sources", lambda s2, **k: {"fuentes": [_f(1, "https://c.org/z")]})
    vistos = {}

    def dl(cands, *a, **k):
        vistos["cands"] = [f["url"] for f in cands]
        vistos["previos"] = k.get("previos")
        return {"documentos": []}
    monkeypatch.setattr(r3, "download_sources", dl)
    monkeypatch.setattr(r3, "refine_fichas", lambda *a, **k: None)
    monkeypatch.setattr(r3, "build_pool", lambda *a, **k: {"datos": [], "cronologia": [], "citas": [],
                                                           "personajes": [], "lugares": []})
    monkeypatch.setattr(r3, "pool_to_blocks", lambda pool: {})
    r3.run_seed({"seed_title": "x"}, "t", d, gate=False)
    r3.set_vocabulario(None)
    r3.set_idiomas(None)
    assert vistos["cands"][0] == "https://a.org/x" and set(vistos["cands"]) == {"https://a.org/x", "https://b.org/y",
                                                                                "https://c.org/z"}
    assert "https://a.org/x" in vistos["previos"]
    reg = json.loads((d / "fuentes.json").read_text(encoding="utf-8"))
    assert reg["registro"] == r3.REGISTRO_VERSION and len(reg["fuentes"]) == 3
    assert json.loads((d / "fuentes_r1.json").read_text(encoding="utf-8"))["fuentes"][0]["url"] == "https://c.org/z"


def test_kyshtym_el_articulo_de_osetrov_figura_con_su_aporte():
    if not (KYS / "fuentes.json").exists():
        pytest.skip("sin el registro de Kyshtym")
    reg = json.loads((KYS / "fuentes.json").read_text(encoding="utf-8"))
    if not reg.get("registro"):
        pytest.skip("el registro de Kyshtym no está armado (f24_registro.py)")
    e = next(x for x in reg["fuentes"] if OSETROV in x["url"])
    assert e["bajada_ok"] and r3.aporte_total(e) > 0 and e["aporte"]["citas"] >= 3
    cands = r3.unir_fuentes([], reg)
    ru = [f for f in sorted(cands, key=lambda f: -f["_aporte"]) if r3.fuente_idioma(f) == "ru"]
    assert OSETROV in "".join(f["url"] for f in ru[:r3.MAX_DESCARGAS_OK])        # entra en el cupo ruso


# ═══════════════════════════════════════════════════════════════
#  B. Beats repartidos
# ═══════════════════════════════════════════════════════════════

def test_prompt_escaleta_f24_literal_y_una_sola_linea():
    # F25c: la escaleta de hoy es la f25-1 (test_module_f25c); la f24-1 queda con su versión
    assert me.SYSTEM_V2_F24_1 == _sistema(F24 / "PROMPT_ESCALETA_v2_1_f24.md") and me.PROMPT_VERSION_V2_F24_1 == "f24-1"
    assert me.SYSTEM_V2_F22_2 == _sistema(F22 / "PROMPT_ESCALETA_v2_1.md")
    assert _md5(me.SYSTEM_V2_F22_2) == "22cfd68b7cee4734e95bb3ee27bb96b2"
    a, b = me.SYSTEM_V2_F22_2.split("\n"), me.SYSTEM_V2_F24_1.split("\n")
    dif = [(x, y) for x, y in zip(a, b) if x != y]
    assert len(a) == len(b) and dif == [(
        "- Repartir el material parejo para llenar siete caps. Un cap puede tener dos beats densos y otro uno solo.",
        "- Meter seis beats en un cap y uno en los demás. Cada cap lleva entre uno y tres beats; el material que no "
        "cabe se deja afuera, no se apila.")]
    assert _md5(me.SYSTEM_V2_F24_1) == "006a195f0ce4be014df34d71644aedb1"


def test_mas_de_tres_beats_en_un_cap_es_bloqueante():
    beats = [{"cap": c, "intensidad": 2, "funcion": "gancho" if k == 0 else "escalada", "dato_central": "D1",
              "datos_apoyo": []} for k, c in enumerate([1, 2, 3, 4, 5, 6, 6, 6, 6, 7])]
    _, hard, _, _ = me.validate({"beats": beats}, {}, max_por_cap=me.MAX_BEATS_POR_CAP)
    msg = [h for h in hard if h.startswith("caps con más de 3 beats")]
    assert msg and "[6]" in msg[0] and me.bloqueante_de(msg[0]) == "entre 1 y 3 beats por cap"
    _, hard, _, _ = me.validate({"beats": beats}, {})                  # sin el tope (camino viejo): no aparece
    assert not any(h.startswith("caps con más de") for h in hard)
    beats3 = [b for k, b in enumerate(beats) if k != 9 - 3]            # tres en el cap 6
    _, hard, _, _ = me.validate({"beats": beats3}, {}, max_por_cap=3)
    assert not any(h.startswith("caps con más de") for h in hard)


def test_la_escaleta_de_kyshtym_f23_no_pasaria():
    p = ROOT / "lab" / "hyperframes" / "f23" / "escaleta_kyshtym_f23.json"
    if not (p.exists() and (KYS / "00_pool_v3.json").exists() and (KYS / "ficha_caso.json").exists()):
        pytest.skip("sin la escaleta de F23")
    esc = json.loads(p.read_text(encoding="utf-8"))
    pool = json.loads((KYS / "00_pool_v3.json").read_text(encoding="utf-8"))
    ficha = json.loads((KYS / "ficha_caso.json").read_text(encoding="utf-8"))
    _, bloq, _, _ = me.bloqueantes(esc, pool, ficha)
    assert any(b.startswith("caps con más de 3 beats: [6]") for b in bloq)
