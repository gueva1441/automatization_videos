"""
test_module_f38a_m01e.py — F38 §A (HANDOFF_F38_reintento_tarjeta_juez), la parte de script_engine/m01e_pantalla:
    §A.1  reintento parcial: el reintento devuelve solo `cambios` de los beats con motivo y el código los fusiona por
          (cap, beat); con la respuesta del intento 1 de F37 y un reintento armado desde el de F37, D128, AVISO, ALARMA
          (y T92) sobreviven, y los cambios en beats sin motivo se ignoran y se anotan. Q14 NO estaba en el intento 1
          (el autor lo descartó ahí: «una sola ficha, se eligió T85»): no hay nada que sobreviva;
    §A.2  cableado: la tarjeta sale de voz_datos.tarjeta_de_voz (no del autor); `validar` no la lee;
    §A.3  juez de anclaje: la entrada (oración, vecinas, dato, voz posterior), la respuesta grabada sobre el papel de F37
          (lab/hyperframes/f38/a/juez_cache_f37.json, una llamada real a Gemini Flash), el motivo de su beat, lo que sigue
          marcado sale, la segunda ronda solo sobre lo nuevo, el error y el tope no frenan.
Sin API: el autor y el juez van con POST falsos o la caché grabada. Los de Vajont se saltean sin data/ en disco.
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from script_engine import m01e_pantalla as mp  # noqa: E402

ROOT = Path(__file__).resolve().parent
VAJONT = "f8s3-vajont"
STEPS = ROOT / "data" / "scripts" / "_steps"
RAW_F37 = STEPS / VAJONT / "01e_pantalla.raw.json"
PAPEL_F37 = STEPS / VAJONT / "01e_pantalla.json"
CACHE_JUEZ = ROOT / "lab" / "hyperframes" / "f38" / "a" / "juez_cache_f37.json"
CLIMA = ["PÁNICO", "CALMA", "AMENAZA", "AVISO", "ALARMA", "INMINENTE", "COLAPSO", "SILENCIO", "RABIA", "MEMORIA"]
SEG = {"valor": 0.3459, "oraciones": 200, "caps": 9, "voz": "prueba"}
hay_vajont = pytest.mark.skipif(not RAW_F37.exists() or not PAPEL_F37.exists(), reason="sin Vajont (F37) en disco")


@pytest.fixture(scope="module")
def vajont() -> dict:
    carga = mp.cargar(VAJONT, STEPS)
    ent = mp.entrada(carga, CLIMA, SEG)
    ent["_pool"] = carga["pool"]
    return ent


@pytest.fixture(scope="module")
def raw37() -> dict:
    return json.loads(RAW_F37.read_text(encoding="utf-8"))


def _fila(resp: dict, cap: str, beat: int) -> dict:
    return next(b for b in resp["beats"] if b["cap"] == cap and b["beat"] == beat)


def _post_seq(resps: list[dict], pedidos: list[dict]):
    def post(body: dict) -> dict:
        pedidos.append(body)
        r = resps[min(len(pedidos) - 1, len(resps) - 1)]
        return {"content": [{"type": "text", "text": json.dumps(r, ensure_ascii=False)}],
                "usage": {"input_tokens": 1000, "output_tokens": 200}, "stop_reason": "end_turn"}
    return post


def _cambios_desde_f37(raw37: dict, beats_m: list[tuple[str, int]]) -> dict:
    """El reintento de F37 en formato `cambios`: para cada beat con motivo, la ficha que puso el intento 2 (los motivos
    de F37 eran todos de fichas: el sello no se toca, la clave no va); más dos cambios en beats SIN motivo que hizo el
    intento 2 de F37 (ch06 b11 D228 en lugar de D128, y ch07 b13 D245 + MEMORIA en lugar de T92 + ALARMA)."""
    r2 = raw37["intentos"][1]["respuesta"]
    cambios = [{"cap": c, "beat": b, "ficha": _fila(r2, c, b)["ficha"]} for c, b in beats_m]
    cambios += [{"cap": "ch06", "beat": 11, "ficha": _fila(r2, "ch06", 11)["ficha"], "sello": None},
                {"cap": "ch07", "beat": 13, "ficha": _fila(r2, "ch07", 13)["ficha"],
                 "sello": _fila(r2, "ch07", 13)["sello"]}]
    return {"cambios": cambios}


# ═══════════════════════ §A.1 reintento parcial ═══════════════════════

@hay_vajont
def test_a1_lo_del_intento_1_sobrevive_al_reintento_parcial(vajont, raw37, tmp_path):
    r1 = raw37["intentos"][0]["respuesta"]
    # lo que había en el intento 1 (verificado en el raw): D128 en ch06 b11, AVISO en ch03 b4, ALARMA (y T92) en ch07 b13
    assert _fila(r1, "ch06", 11)["ficha"]["pool_id"] == "D128"
    assert _fila(r1, "ch03", 4)["sello"]["palabra"] == "AVISO"
    assert _fila(r1, "ch07", 13)["sello"]["palabra"] == "ALARMA"
    # Q14 no estaba: el autor lo descartó en el intento 1 (no hay nada que el reintento pueda perder)
    assert not any((b.get("ficha") or {}).get("pool_id") == "Q14" for b in r1["beats"])
    assert any(d.get("pool_id") == "Q14" for d in r1["descartados"])
    v1 = mp.validar(r1, vajont)
    beats_m = mp.beats_con_motivo(v1["motivos_beat"])
    assert len(v1["motivos_beat"]) == len(v1["motivos"])
    assert beats_m == [("ch02", 3), ("ch03", 4), ("ch04", 6), ("ch04", 7), ("ch05", 8)]
    vuelve = [mb for m, mb in zip(v1["motivos"], v1["motivos_beat"]) if "vuelve a ser candidato" in m]
    assert vuelve and all(mb == [] for mb in vuelve)                      # D68: sin beat
    # por llamar: el reintento ve el papel entero como contexto y pide solo los cambios de esos beats
    pedidos: list[dict] = []
    res = mp.llamar(vajont, tmp_path, tope=100.0,
                    post=_post_seq([r1, _cambios_desde_f37(raw37, beats_m)], pedidos))
    assert len(pedidos) == 2
    p2 = pedidos[1]["messages"][0]["content"]
    assert "TU RESPUESTA ANTERIOR (el papel completo, como contexto)" in p2 and mp.FORMATO_REINTENTO in p2
    assert "ch02 beat 3, ch03 beat 4, ch04 beat 6, ch04 beat 7, ch05 beat 8" in p2
    rt = res["reintento"]
    assert rt["tipo"] == "parcial"
    assert {(i["cap"], i["beat"]) for i in rt["ignorados"]} == {("ch06", 11), ("ch07", 13)}
    assert all(i["motivo"] == "el beat no tiene motivo" for i in rt["ignorados"])
    fin = res["validacion"]
    assert _fila(fin, "ch06", 11)["ficha"]["pool_id"] == "D128" and _fila(fin, "ch06", 11)["sello"]["palabra"] == "MEMORIA"
    assert _fila(fin, "ch03", 4)["sello"]["palabra"] == "AVISO"
    assert _fila(fin, "ch07", 13)["ficha"]["pool_id"] == "T92" and _fila(fin, "ch07", 13)["sello"]["palabra"] == "ALARMA"
    # lo cambiado con motivo sí entra (D131 de ch01 no tenía motivo: queda en [15], como el intento 1)
    assert _fila(res["final"], "ch01", 1)["ficha"]["sentence_idx"] == 15
    papel = mp.armar(vajont, res)
    assert papel["reintento"]["ignorados"] and "### Reintento parcial" in mp.a_markdown(papel)


def test_a1_fusionar_null_borra_ausente_no_cambia_y_beat_sin_motivo_se_ignora():
    base = {"beats": [{"cap": "ch01", "beat": 1, "ficha": {"pool_id": "D1"}, "sello": {"palabra": "AVISO"}},
                      {"cap": "ch01", "beat": 2, "ficha": {"pool_id": "D2"}, "sello": None}],
            "relojes": [{"cap": "ch01", "sentence_idx": 0, "fecha": "1 ENE 1900"}], "descartados": []}
    resp = {"cambios": [{"cap": "ch01", "beat": 1, "ficha": None},                       # borra la ficha; sello igual
                        {"cap": "ch01", "beat": 2, "ficha": {"pool_id": "D9"}},           # sin motivo → ignorado
                        {"cap": "ch01", "beat": 3, "sello": {"palabra": "CALMA"}}]}       # beat nuevo con motivo
    fus, apl, ign = mp.fusionar(base, resp, [("ch01", 1), ("ch01", 3)])
    assert _fila(fus, "ch01", 1)["ficha"] is None and _fila(fus, "ch01", 1)["sello"] == {"palabra": "AVISO"}
    assert _fila(fus, "ch01", 2)["ficha"] == {"pool_id": "D2"}
    assert _fila(fus, "ch01", 3)["sello"] == {"palabra": "CALMA"}
    assert fus["relojes"] == base["relojes"] and base["beats"][0]["ficha"] == {"pool_id": "D1"}   # base intacta
    assert [(a["cap"], a["beat"], a["partes"]) for a in apl] == [("ch01", 1, ["ficha"]), ("ch01", 3, ["sello"])]
    assert [(i["cap"], i["beat"]) for i in ign] == [("ch01", 2)]
    # una respuesta sin `cambios` no cambia nada (se anota)
    fus2, apl2, ign2 = mp.fusionar(base, {"beats": []}, [("ch01", 1)])
    assert fus2["beats"] == base["beats"] and not apl2 and "no trae `cambios`" in ign2[0]["motivo"]


def test_a1_motivos_sin_beat_no_abren_beats():
    assert mp.beats_con_motivo([[], []]) == []
    assert mp.beats_con_motivo([[("ch02", 3)], [], [("ch01", 1), ("ch02", 3)]]) == [("ch01", 1), ("ch02", 3)]


def test_a1_formatos_literales():
    assert "TARJETA" not in mp.PANTALLA_SYSTEM and '"tarjeta"' not in mp.FORMATO_SALIDA
    assert mp.FORMATO_REINTENTO.startswith('{"cambios": [{"cap": "ch03", "beat": 5, "ficha":')
    assert mp.PROMPT_VERSION == "m01e-3"


# ═══════════════════════ §A.2 tarjeta desde la voz ═══════════════════════

def test_a2_la_tarjeta_sale_de_voz_datos_y_no_del_autor(monkeypatch):
    from script_engine import voz_datos as vd
    ent = {"topic_id": "t", "caps": [{"cap": "ch01", "n": 1, "titulo": "", "oraciones": []}], "beats": [],
           "archivo": [], "clima": [], "a_pantalla": {}, "_escaleta": {"pico": {"beat": 1}}, "_pool": {"datos": []}}
    vista = []

    def falsa(e, esc, pool):
        vista.append((e is ent, esc, pool))
        return {"texto": "9 OCT 1963 · 22:39", "fecha": "1963-10-09", "hora": "22:39", "fecha_de": "ch01 [13]",
                "hora_de": "T66", "fuente": "voz ch01 [13] + T66"}
    monkeypatch.setattr(vd, "tarjeta_de_voz", falsa)
    v = mp.validar({"beats": [], "tarjeta": {"texto": "1 ENE 2000 · 00:00"}}, ent)
    assert "tarjeta" not in v                                                # validar ya no la lee
    res = {"validacion": v, "modelo": mp.MODELO, "effort": mp.EFFORT, "intentos": [], "usd": 0.0}
    p = mp.armar(ent, res)
    assert vista == [(True, {"pico": {"beat": 1}}, {"datos": []})]
    assert p["tarjeta"]["texto"] == "9 OCT 1963 · 22:39" and p["tarjeta"]["fuente"] == "voz ch01 [13] + T66"
    assert p["tarjeta_motivo"] is None and "(fuente: voz ch01 [13] + T66)" in mp.a_markdown(p)
    monkeypatch.setattr(vd, "tarjeta_de_voz", lambda e, esc, pool: {"falta": True, "motivo": "la voz no dice fecha"})
    p2 = mp.armar(ent, res)
    assert p2["tarjeta"] is None and p2["tarjeta_motivo"] == "la voz no dice fecha"
    assert "**Tarjeta:** — (la voz no dice fecha)" in mp.a_markdown(p2)


@hay_vajont
def test_a2_vajont_tarjeta_real(vajont):
    from script_engine import voz_datos as vd
    if not hasattr(vd, "tarjeta_de_voz"):
        pytest.skip("voz_datos.tarjeta_de_voz todavía no está")
    tj, motivo = mp.tarjeta(vajont)
    assert motivo is None and tj["texto"] == "9 OCT 1963 · 22:39"


# ═══════════════════════ §A.3 juez de anclaje ═══════════════════════

def test_a3_prompt_literal_del_juez():
    h = (ROOT / "lab" / "hyperframes" / "f38" / "HANDOFF_F38_reintento_tarjeta_juez.md").read_text(encoding="utf-8")
    assert mp.JUEZ_SYSTEM in h and mp.JUEZ_VERSION == "juez-1"
    assert "gemini" not in mp.JUEZ_SYSTEM.lower()


@hay_vajont
def test_a3_entrada_del_juez_d131_con_su_oracion_vecinas_y_voz_posterior(vajont):
    papel = json.loads(PAPEL_F37.read_text(encoding="utf-8"))
    assert [c["oraciones"] for c in papel["caps"]] == [[s["texto"] for s in c["oraciones"]] for c in vajont["caps"]]
    filas = mp.juez_entrada(papel["beats"], vajont)
    d = next(f for f in filas if f["id"] == "D131")
    ors = vajont["caps"][0]["oraciones"]
    assert d["_donde"]["cap"] == "ch01" and d["_donde"]["sentence_idx"] == 1 and d["_donde"]["beat"] == 1
    assert d["oracion"] == f"ch01 [1] {ors[1]['texto']}"
    assert d["anterior"] == f"ch01 [0] {ors[0]['texto']}" and d["siguiente"] == f"ch01 [2] {ors[2]['texto']}"
    x = next(x for x in vajont["archivo"] if x["id"] == "D131")
    assert d["dato"]["texto"] == x["texto"] and d["dato"]["fuente"] == x["fuente"]
    total = sum(len(c["oraciones"]) for c in vajont["caps"])
    assert len(d["voz_despues"]) == total - 2 and d["voz_despues"][0].startswith("ch01 [2] ")
    ult = vajont["caps"][-1]
    assert d["voz_despues"][-1] == f"{ult['cap']} [{len(ult['oraciones']) - 1}] {ult['oraciones'][-1]['texto']}"
    assert "_donde" not in mp.juez_pedido(filas)


@hay_vajont
@pytest.mark.skipif(not CACHE_JUEZ.exists(), reason="sin la respuesta grabada del juez")
def test_a3_d131_marcado_por_la_respuesta_grabada_y_motivo_de_su_beat(vajont, tmp_path, monkeypatch):
    papel = json.loads(PAPEL_F37.read_text(encoding="utf-8"))
    grab = json.loads(CACHE_JUEZ.read_text(encoding="utf-8"))
    monkeypatch.setattr(mp, "_juez_modelo", lambda: next(iter(grab.values()))["modelo"])   # el de la grabación
    shutil.copy(CACHE_JUEZ, tmp_path / "01e_juez.raw.json")

    def sin_api(*_a):
        raise AssertionError("el test no llama a la API")
    r = mp.juzgar(papel["beats"], vajont, tmp_path, ronda=1, call=sin_api)
    assert r["cache"] and r["error"] is None and r["usd"] == 0.0
    v = next(v for v in r["veredictos"] if v["id"] == "D131")
    assert v["mismo_asunto"] is False or v["adelanta"] is True
    assert v["marcada"] and (v["cap"], v["beat"], v["sentence_idx"]) == ("ch01", 1, 1)
    m = mp.motivo_juez(v)
    assert m.startswith("D131 (ch01 beat 1, oración [1])") and v["motivo"] in m and "elegí otra oración u otro dato" in m


def _chico() -> dict:
    pool = {"datos": [{"id": "D1", "texto": "La presa mide 266 metros de alto.", "fuente": "F", "fecha": "1960"},
                      {"id": "D2", "texto": "El lago tenía 115 millones de metros cúbicos.", "fuente": "F",
                       "fecha": "1960"}],
            "cronologia": [], "personajes": [], "citas": []}
    carga = {"topic_id": "t", "dir": Path("."), "titulos": {1: "Uno"}, "pool": pool,
             "escaleta": {"pico": {"beat": 1}, "a_pantalla": [],
                          "beats": [{"n": 1, "cap": 1, "funcion": "gancho", "dato_central": "", "datos_apoyo": []}]},
             "parrafos": [{"cap": 1, "beat": 1, "texto": "Era el año mil novecientos sesenta. La presa del valle se "
                                                        "levanta enorme sobre el pueblo entero. El agua del lago "
                                                        "llena el valle de punta a punta y sube."}]}
    ent = mp.entrada(carga, CLIMA, SEG)
    ent["_pool"] = pool
    return ent


def _ficha(pid: str, si: int, et: str, txt: str) -> dict:
    return {"cap": "ch01", "beat": 1, "ficha": {"pool_id": pid, "sentence_idx": si, "palabra": "", "etiqueta": et,
                                                "texto": txt, "aporta": "x"}, "sello": None}


def _juez_seq(resps: list[list[dict]], llamadas: list[str]):
    def call(system: str, user: str, modelo: str) -> dict:
        llamadas.append(user)
        return {"texto": json.dumps(resps[min(len(llamadas) - 1, len(resps) - 1)]),
                "usage": {"input_tokens": 100, "output_tokens": 10, "thinking_tokens": 0}}
    return call


def test_a3_lo_marcado_va_al_reintento_y_si_sigue_sale(tmp_path, monkeypatch):
    monkeypatch.setattr(mp, "_juez_modelo", lambda: "gemini-2.5-flash")
    ent = _chico()
    r1 = {"beats": [_ficha("D1", 1, "ALTURA", "266 metros")], "relojes": [], "descartados": []}
    assert mp.validar(r1, ent)["beats"][0]["ficha"]["pool_id"] == "D1"
    pedidos, llamadas = [], []
    res = mp.llamar(ent, tmp_path, tope=100.0, post=_post_seq([r1, {"cambios": []}], pedidos),
                    juez_post=_juez_seq([[{"id": "D1", "mismo_asunto": False, "adelanta": False,
                                           "motivo": "la oración habla del año, no de la presa"}]], llamadas))
    assert len(pedidos) == 2 and len(llamadas) == 1                         # sin fichas nuevas: sin segunda ronda
    assert "D1 (ch01 beat 1, oración [1])" in pedidos[1]["messages"][0]["content"]
    assert "la oración habla del año, no de la presa" in pedidos[1]["messages"][0]["content"]
    fin = res["validacion"]
    assert fin["beats"][0]["ficha"] is None
    d = next(d for d in fin["descartados"] if d.get("regla") == "juez")
    assert d["pool_id"] == "D1" and "la oración habla del año" in d["motivo"]
    assert res["juez"]["usd"] > 0 and res["usd"] >= res["juez"]["usd"]
    papel = mp.armar(ent, res)
    assert papel["juez"]["salieron"] and "**juez**" in mp.a_markdown(papel)
    # repetida: caché del autor y del juez → la misma salida, US$ 0
    res2 = mp.llamar(ent, tmp_path, tope=100.0, post=_post_seq([{}], []), juez_post=_juez_seq([[]], []))
    assert res2.get("cache") and res2["validacion"]["beats"][0]["ficha"] is None


def test_a3_la_ficha_nueva_del_reintento_se_juzga_en_una_segunda_ronda(tmp_path, monkeypatch):
    monkeypatch.setattr(mp, "_juez_modelo", lambda: "gemini-2.5-flash")
    ent = _chico()
    r1 = {"beats": [_ficha("D1", 1, "ALTURA", "266 metros")], "relojes": [], "descartados": []}
    nueva = _ficha("D2", 2, "AGUA DEL LAGO", "115 millones de m³")["ficha"]
    llamadas: list[str] = []
    res = mp.llamar(ent, tmp_path, tope=100.0,
                    post=_post_seq([r1, {"cambios": [{"cap": "ch01", "beat": 1, "ficha": nueva}]}], []),
                    juez_post=_juez_seq([[{"id": "D1", "mismo_asunto": False, "adelanta": False, "motivo": "otro"}],
                                         [{"id": "D2", "mismo_asunto": True, "adelanta": True,
                                           "motivo": "la voz lo cuenta después"}]], llamadas))
    assert len(llamadas) == 2
    assert '"id": "D2"' in llamadas[1] and '"id": "D1"' not in llamadas[1]     # solo la nueva
    assert res["validacion"]["beats"][0]["ficha"] is None
    assert [d["pool_id"] for d in res["juez"]["salieron"]] == ["D2"]


def test_a3_si_el_juez_falla_o_no_entra_en_el_tope_la_corrida_sigue(tmp_path, monkeypatch):
    monkeypatch.setattr(mp, "_juez_modelo", lambda: "gemini-2.5-flash")
    ent = _chico()
    r1 = {"beats": [_ficha("D1", 1, "ALTURA", "266 metros")], "relojes": [], "descartados": []}

    def rota(*_a):
        raise RuntimeError("503")
    res = mp.llamar(ent, tmp_path, tope=100.0, post=_post_seq([r1], []), juez_post=rota)
    assert "503" in res["juez"]["error"] and res["validacion"]["beats"][0]["ficha"]["pool_id"] == "D1"
    assert len(res["intentos"]) == 1                                           # sin motivos: sin reintento
    r = mp.juzgar(mp.validar(r1, ent)["beats"], ent, tmp_path / "x", ronda=1, call=rota, libre_usd=0.0)
    assert r["error"].startswith("tope:")
    r = mp.juzgar(mp.validar(r1, ent)["beats"], ent, tmp_path / "y", ronda=1,
                  call=lambda *_a: {"texto": "no sé", "usage": {}})
    assert r["error"].startswith("sin JSON") and not r["veredictos"]
