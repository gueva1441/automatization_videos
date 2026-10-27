"""
test_module_f37a_papel.py — F37 §A (HANDOFF_F37_papel_y_colocar): el autor del papel (script_engine/m01e_pantalla) ve lo
que el pool sabe y se corrige solo. Un test por punto, con el caso real de Vajont cuando hace falta (data/ está fuera de
git: sin Vajont en disco esos se saltean).
    §A.1c  Q43 (cita sin fecha, autor «Ingeniero jefe (sucesor de Semenza)») cae: su autor no está en la voz;
    §A.1b  un ítem con año posterior al relato cae; un testimonio no; el año dicho en dos cifras lo sitúa (D47 «cincuenta»);
    §A.2   T39 «la voz lo dice» es falso (la voz no dice «50 millones») → vuelve en el reintento;
    §A.3a  el reemplazo literal del prompt (m01e-2) y el `tipo` del descarte en el formato;
    §A.3b  un pico sin ficha dispara el reintento;
    §A.4   D47 llega al reintento como pregunta, no como corte; si el autor lo mantiene queda juzgado y Fase 2 respeta el
           juicio;
    §0     SEG_POR_PALABRA se deriva de los tiempos de palabra existentes; TOPE_USD se lee del perfil.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from script_engine import m01e_pantalla as mp  # noqa: E402

ROOT = Path(__file__).resolve().parent
VAJONT = "f8s3-vajont"
STEPS = ROOT / "data" / "scripts" / "_steps"
CLIMA = ["PÁNICO", "CALMA", "AMENAZA", "AVISO", "ALARMA", "INMINENTE", "COLAPSO", "SILENCIO", "RABIA", "MEMORIA"]
SEG = {"valor": 0.3459, "oraciones": 200, "caps": 9, "voz": "prueba"}
hay_vajont = pytest.mark.skipif(not (STEPS / VAJONT / "01a_escaleta.json").exists(), reason="sin Vajont en disco")


@pytest.fixture(scope="module")
def vajont() -> dict:
    carga = mp.cargar(VAJONT, STEPS)
    ent = mp.entrada(carga, CLIMA, SEG)
    ent["_pool"] = carga["pool"]
    return ent


def _ficha(cap: str, beat: int, pid: str, si: int, et: str, txt: str, palabra: str = "") -> dict:
    return {"cap": cap, "beat": beat, "ficha": {"pool_id": pid, "sentence_idx": si, "palabra": palabra, "etiqueta": et,
                                                "texto": txt, "aporta": "lo que la voz no dice"}, "sello": None}


def _post_seq(resps: list[dict], pedidos: list[dict]):
    """POST falso: devuelve las respuestas en orden y guarda cada body pedido."""
    def post(body: dict) -> dict:
        pedidos.append(body)
        r = resps[min(len(pedidos) - 1, len(resps) - 1)]
        return {"content": [{"type": "text", "text": json.dumps(r, ensure_ascii=False)}],
                "usage": {"input_tokens": 1000, "output_tokens": 200}, "stop_reason": "end_turn"}
    return post


def _chico(fecha_d2: str | None = "1970", testimonio: bool = False) -> dict:
    """Un video de dos caps: ch01 dice 1963, ch02 cuenta 1963 y no dice otro año."""
    pool = {"datos": [{"id": "D1", "texto": "La presa mide 266 metros de alto.", "fuente": "F", "fecha": "1960"},
                      {"id": "D2", "texto": "El juicio terminó con 11 condenas.", "fuente": "F", "fecha": fecha_d2}],
            "cronologia": [], "personajes": [],
            "citas": [{"id": "Q1", "texto": "Nadie nos avisó nunca", "autor": "Un sobreviviente", "rol": "vecino",
                       "fecha": "1990", "testimonio": testimonio, "fuente": "F"}]}
    carga = {"topic_id": "t", "dir": Path("."), "titulos": {1: "Uno", 2: "Dos"}, "pool": pool,
             "escaleta": {"pico": {"beat": 2}, "a_pantalla": [],
                          "beats": [{"n": 1, "cap": 1, "funcion": "gancho", "dato_central": "", "datos_apoyo": []},
                                    {"n": 2, "cap": 2, "funcion": "escalada", "dato_central": "D2",
                                     "datos_apoyo": []}]},
             "parrafos": [{"cap": 1, "beat": 1, "texto": "Era el año mil novecientos sesenta y tres. La casa está a "
                                                        "oscuras. El valle duerme."},
                          {"cap": 2, "beat": 2, "texto": "El agua sube cada día. La montaña se mueve despacio. Nadie "
                                                        "quiere mirar la ladera."}]}
    ent = mp.entrada(carga, CLIMA, SEG)
    ent["_pool"] = pool
    return ent


# ═══════════════════════ §A.1 fecha del relato y cita sin fecha ═══════════════════════

@hay_vajont
def test_a1c_q43_cita_sin_fecha_cae_porque_su_autor_no_esta_en_la_voz(vajont):
    q43 = next(x for x in vajont["archivo"] if x["id"] == "Q43")
    assert q43["fecha"] == "desconocida" and q43["testimonio"] == "no" and q43["rol"]          # §A.1a: como en el pool
    resp = {"beats": [_ficha("ch05", 9, "Q43", 23, "INGENIERO JEFE", "Son sacudidas menores")]}
    v = mp.validar(resp, vajont)
    d = next(d for d in v["descartados"] if d.get("pool_id") == "Q43")
    assert d["regla"] == "cita_sin_fecha", d
    assert any("Q43" in m and "cita_sin_fecha" in m for m in v["motivos"])


def test_a1b_item_posterior_al_relato_cae_y_un_testimonio_no():
    ent = _chico()
    v = mp.validar({"beats": [_ficha("ch02", 2, "D2", 1, "CONDENAS DEL JUICIO", "11 condenas")]}, ent)
    d = next(d for d in v["descartados"] if d.get("pool_id") == "D2")
    assert d["regla"] == "fecha_relato" and "1970" in d["motivo"] and "1963" in d["motivo"]
    # la cita de 1990 es testimonio: se cuenta después, pasa la fecha del relato
    ent_t = _chico(testimonio=True)
    v2 = mp.validar({"beats": [_ficha("ch02", 2, "Q1", 1, "UN SOBREVIVIENTE", "Nadie nos avisó nunca")]}, ent_t)
    assert not [d for d in v2["descartados"] if d.get("regla") == "fecha_relato"]
    ent_n = _chico(testimonio=False)
    v3 = mp.validar({"beats": [_ficha("ch02", 2, "Q1", 1, "UN SOBREVIVIENTE", "Nadie nos avisó nunca")]}, ent_n)
    assert [d for d in v3["descartados"] if d.get("regla") == "fecha_relato"]


@hay_vajont
def test_a1b_d47_el_anio_dicho_en_dos_cifras_lo_situa(vajont):
    """D47 es de 1950; en ch02 [11] el relato va por 1943, pero la oración dice «la década del cincuenta»."""
    resp = {"beats": [_ficha("ch02", 3, "D47", 11, "DESMORONAMIENTO DEL TOC", "2 km de frente y 600 m de desarrollo "
                                                                              "vertical")]}
    v = mp.validar(resp, vajont)
    assert not [d for d in v["descartados"] if d.get("pool_id") == "D47" and d.get("regla") == "fecha_relato"]


# ═══════════════════════ §A.2 descarte «la voz lo dice» verificado ═══════════════════════

@hay_vajont
def test_a2_t39_la_voz_no_dice_50_millones_y_vuelve_en_el_reintento(vajont, tmp_path):
    r1 = {"beats": [], "descartados": [{"pool_id": "T39", "tipo": "voz_lo_dice",
                                        "motivo": "La voz ya cuenta la advertencia de febrero de 1961."}]}
    v = mp.validar(r1, vajont)
    t39 = next(x for x in v["vuelven"] if x["pool_id"] == "T39")
    assert "50" in t39["falta"]
    pedidos: list[dict] = []
    mp.llamar(vajont, tmp_path, post=_post_seq([r1, {"beats": []}], pedidos), tope=100.0)
    assert len(pedidos) == 2
    assert "T39: dijiste que la voz lo dice" in pedidos[1]["messages"][0]["content"]
    assert "«50»" in pedidos[1]["messages"][0]["content"]


# ═══════════════════════ §A.3 prompt y pico sin ficha ═══════════════════════

def test_a3a_reemplazo_literal_del_prompt_y_tipo_del_descarte():
    viejo = ("en el gancho (capítulo 1), cualquier dato del archivo que la voz no diga en todo el video y que haga "
             "quedarse a quien mira: el gancho nunca queda sin ficha.")
    nuevo = ("en el gancho (capítulo 1), cualquier dato del archivo que la voz no diga en todo el video, que haga "
             "quedarse a quien mira y que pueda ir en las primeras oraciones del capítulo: el gancho nunca queda sin "
             "ficha.")
    # F38b: la línea de A.3a se revirtió a la de m01e-1 (movía el dato del gancho a una oración que no le corresponde)
    assert nuevo not in mp.PANTALLA_SYSTEM and mp.PANTALLA_SYSTEM.count(viejo) == 1
    assert mp.PROMPT_VERSION == "m01e-4"          # F38b: m01e-3 con el gancho de m01e-1
    assert '"tipo": "voz_lo_dice" | "spoiler" | "repetido" | "otro"' in mp.FORMATO_SALIDA


def test_a3b_pico_sin_ficha_dispara_el_reintento(tmp_path):
    ent = _chico()
    pedidos: list[dict] = []
    res = mp.llamar(ent, tmp_path, post=_post_seq([{"beats": []}, {"beats": []}], pedidos), tope=100.0)
    assert len(pedidos) == 2 and "el beat 2 de ch02 es pico y quedó sin ficha" in pedidos[1]["messages"][0]["content"]
    papel = mp.armar(ent, res)
    assert {"cap": "ch02", "beat": 2} in papel["picos_vacios"]          # (y el gancho: el único beat de ch01 es su pico)
    assert "⚠ pico sin ficha" in mp.a_markdown(papel)


# ═══════════════════════ §A.4 la coincidencia se pregunta, no corta ═══════════════════════

@hay_vajont
def test_a4_d47_llega_como_pregunta_y_el_juicio_del_autor_es_final(vajont, tmp_path):
    f47 = _ficha("ch02", 3, "D47", 11, "DESMORONAMIENTO DEL TOC", "2 km de frente y 600 m de desarrollo vertical")
    v = mp.validar({"beats": [f47]}, vajont)
    assert not [d for d in v["descartados"] if d.get("pool_id") == "D47"]                 # no corta
    q = next(q for q in v["preguntas"] if q["pool_id"] == "D47")
    assert q["regla"] == "spoiler" and q["donde"][0] == "ch03"
    assert any(m.startswith("D47") and "¿es el mismo hecho? si no, mantenelo" in m for m in v["motivos"])
    # el reintento lo mantiene → otro hecho, juzgado; Fase 2 no lo vuelve a cortar
    pedidos: list[dict] = []
    res = mp.llamar(vajont, tmp_path, post=_post_seq([{"beats": [f47]}, {"beats": [f47]}], pedidos), tope=100.0)
    papel = mp.armar(vajont, res)
    b = next(b for b in papel["beats"] if b["cap"] == "ch02" and b["beat"] == 3)
    assert b["ficha"]["pool_id"] == "D47" and b["ficha"]["juicio_autor"] == {"spoiler": ["2"]}
    from script_engine.pantalla_filtros import spoiler
    ctx = {"sents": [{"texto": "El Toc se desmorona."}, {"texto": "Una fisura de dos kilómetros."}], "si": 0,
           "nums": ["2"], "nms": [], "juicio": b["ficha"]["juicio_autor"]}
    assert spoiler({}, {}, ctx) is None
    assert spoiler({}, {}, {**ctx, "juicio": {}}) is not None


# ═══════════════════════ §0 constantes que salen del código ═══════════════════════

def test_0_seg_por_palabra_se_deriva_de_los_tiempos_existentes(tmp_path):
    from script_engine.voz_utils import seg_por_palabra
    for topic, h in (("a", "x1"), ("b", "x1"), ("c", "x2")):          # b es copia de a (mismo tts_hash): cuenta una vez
        d = tmp_path / topic
        d.mkdir()
        (d / "ch01.meta.json").write_text(json.dumps({"voice_id": "V", "tts_hash": h}), encoding="utf-8")
        paso = 0.4 if h == "x1" else 0.2
        words = [{"word": w, "start": i * paso, "end": i * paso + paso * 0.9}
                 for i, w in enumerate(["Una", "frase", "corta.", "Otra", "frase", "más."])]
        (d / "ch01_timestamps.json").write_text(json.dumps(words), encoding="utf-8")
    (tmp_path / "z").mkdir()
    (tmp_path / "z" / "ch01.meta.json").write_text(json.dumps({"voice_id": "OTRA", "tts_hash": "y"}), encoding="utf-8")
    s = seg_por_palabra("V", tmp_path)
    assert s["caps"] == 2 and s["oraciones"] == 4 and s["voz"] == "V"
    assert 0.2 < s["valor"] < 0.4
    assert seg_por_palabra("NADIE", tmp_path) is None
    assert mp.velocidad({"valor": 0}) ["valor"] == mp.SEG_POR_PALABRA_RESPALDO    # sin voces: respaldo, anotado


def test_0_tope_usd_se_lee_del_perfil(monkeypatch):
    import gfx_config
    monkeypatch.setitem(gfx_config.ACTIVE_PROFILE, "costos", {"m01e_tope_usd": 0.75})
    assert mp.tope_usd() == (0.75, "perfil (costos.m01e_tope_usd)")
    monkeypatch.delitem(gfx_config.ACTIVE_PROFILE, "costos")
    v, de = mp.tope_usd()
    assert v == mp.TOPE_USD_RESPALDO and de.startswith("respaldo")
