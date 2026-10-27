"""
test_module_f38a_m01e.py — F38 §A (HANDOFF_F38_reintento_tarjeta_juez), la parte de script_engine/m01e_pantalla:
    §A.1  reintento parcial: el reintento devuelve solo `cambios` de los beats con motivo y el código los fusiona por
          (cap, beat); con la respuesta del intento 1 de F37 y un reintento armado desde el de F37, D128, AVISO, ALARMA
          (y T92) sobreviven, y los cambios en beats sin motivo se ignoran y se anotan. Q14 NO estaba en el intento 1
          (el autor lo descartó ahí: «una sola ficha, se eligió T85»): no hay nada que sobreviva;
    §A.2  cableado: la tarjeta sale de voz_datos.tarjeta_de_voz (no del autor); `validar` no la lee;
    F38b  (HANDOFF_F38b_quitar_juez) el juez de §A.3 se borró con sus tests y su grabación; la línea del gancho vuelve
          a la de m01e-1 (m01e-4) y nada en script_engine llama a un juez.
Sin API: el autor va con POST falsos. El papel de F37 se lee de su copia congelada (lab/hyperframes/f37/c).
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
STEPS = ROOT / "lab" / "hyperframes" / "f38" / "b2" / "fase1"   # F38c: las entradas de Fase 1 congeladas (nunca data/)
RAW_F37 = ROOT / "lab" / "hyperframes" / "f37" / "c" / "01e_pantalla.raw.json"   # la copia congelada de F37 (la corrida B pisa la de data/)
PAPEL_F37 = ROOT / "lab" / "hyperframes" / "f37" / "c" / "01e_pantalla.json"
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
def raw37(vajont) -> dict:
    """F38e §C.3: el formato pide `respaldo` por ficha y las respuestas de F37 no lo traen: se completa con el texto
    entero del ítem (fragmento literal trivial), con lo que el candado contra el respaldo es el de antes."""
    raw = json.loads(RAW_F37.read_text(encoding="utf-8"))
    arch = {x["id"]: x["texto"] for x in vajont["archivo"]}
    for it in raw["intentos"]:
        for fila in (it.get("respuesta") or {}).get("beats") or []:
            fi = fila.get("ficha") if isinstance(fila, dict) else None
            if isinstance(fi, dict) and not fi.get("respaldo") and fi.get("pool_id") in arch:
                fi["respaldo"] = arch[fi["pool_id"]]
    return raw


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
    de F37 eran todos de fichas: el sello no se toca, la clave no va); más dos cambios que hizo el intento 2 de F37
    (ch06 b11 D228 en lugar de D128, SIN motivo, y ch07 b13 D245 + MEMORIA en lugar de T92 + ALARMA: F38c §A.1, ese
    beat ahora tiene motivo porque quedó sin su `a_pantalla` D245)."""
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
    # F38c §A.1: ch07 b13 (T92, sin su `a_pantalla` D245) tiene motivo; ch05 b8 ya lo tenía (y además le falta Q50)
    assert beats_m == [("ch02", 3), ("ch03", 4), ("ch04", 6), ("ch04", 7), ("ch05", 8), ("ch07", 13)]
    vuelve = [mb for m, mb in zip(v1["motivos"], v1["motivos_beat"]) if "vuelve a ser candidato" in m]
    assert vuelve and all(mb == [] for mb in vuelve)                      # D68: sin beat
    # por llamar: el reintento ve el papel entero como contexto y pide solo los cambios de esos beats
    pedidos: list[dict] = []
    res = mp.llamar(vajont, tmp_path, tope=100.0,
                    post=_post_seq([r1, _cambios_desde_f37(raw37, beats_m)], pedidos))
    # F38d §A.1: la vuelta 1 deja motivos nuevos (Q15 vuelve y ch05 b8 sigue sin Q50) → vuelta 2 con solo ch05 b8; el
    # POST repite la misma respuesta, los motivos quedan iguales → cierra «sin progreso» (3 llamadas)
    assert len(pedidos) == 3
    p2 = pedidos[1]["messages"][0]["content"]
    assert "TU RESPUESTA ANTERIOR (el papel completo, como contexto)" in p2 and mp.FORMATO_REINTENTO in p2
    assert "ch02 beat 3, ch03 beat 4, ch04 beat 6, ch04 beat 7, ch05 beat 8, ch07 beat 13" in p2
    rt = res["reintento"]
    assert rt["tipo"] == "parcial"
    # F38d: el reintento único de F38 es la vuelta 1 (lo de `rt` es la unión de las vueltas)
    v1r = rt["vueltas"][0]
    assert {(i["cap"], i["beat"]) for i in v1r["ignorados"]} == {("ch06", 11)}
    assert all(i["motivo"] == "el beat no tiene motivo" for i in rt["ignorados"])
    assert [v["vuelta"] for v in rt["vueltas"]] == [1, 2] and rt["vueltas"][1]["beats"] == [("ch05", 8)]
    assert "ch05 beat 8." in pedidos[2]["messages"][0]["content"] and rt["cierre"] == "sin progreso"
    fin = res["validacion"]
    assert _fila(fin, "ch06", 11)["ficha"]["pool_id"] == "D128" and _fila(fin, "ch06", 11)["sello"]["palabra"] == "MEMORIA"
    assert _fila(fin, "ch03", 4)["sello"]["palabra"] == "AVISO"
    # F38c §A.1: el cambio de ch07 b13 se aplica (tiene motivo): entra D245; su sello MEMORIA cae (ya salió en ch06 b11)
    assert _fila(fin, "ch07", 13)["ficha"]["pool_id"] == "D245" and _fila(fin, "ch07", 13)["sello"] is None
    assert any(d.get("cap") == "ch07" and d.get("beat") == 13 and d["que"] == "sello" and d["texto"] == "MEMORIA"
               for d in fin["descartados"] if d.get("quien") == "validación")
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
    assert mp.PROMPT_VERSION == "m01e-6"          # F38b: + el gancho de m01e-1 · F38d §A.2 · F38e §C.1: el de la prueba 1


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


# ═══════════════════════ F38b: la línea del gancho de m01e-1, sin juez ═══════════════════════

def test_f38b_gancho_literal_de_m01e_1_sin_las_primeras_oraciones():
    h = (ROOT / "lab" / "hyperframes" / "f38" / "HANDOFF_F38b_quitar_juez.md").read_text(encoding="utf-8")
    linea = ("cualquier dato del archivo que la voz no diga en todo el video y que haga quedarse a quien mira: el gancho "
             "nunca queda sin ficha.")
    assert linea in h and linea in mp.PANTALLA_SYSTEM
    assert "primeras oraciones" not in mp.PANTALLA_SYSTEM
    assert mp.PROMPT_VERSION == "m01e-6"                      # F38d §A.2 · F38e §C.1 (la línea del gancho sigue igual)


def test_f38b_nada_llama_a_un_juez():
    # el juez de anclaje de F38 §A.3 (el parámetro `juez` del crítico «¿estorba?» de pantalla_colocar/clima es otro)
    assert "juez" not in (ROOT / "script_engine" / "m01e_pantalla.py").read_text(encoding="utf-8").lower()
    for f in (ROOT / "script_engine").glob("*.py"):
        txt = f.read_text(encoding="utf-8", errors="replace")
        assert not any(n in txt for n in ("JUEZ_SYSTEM", "JUEZ_VERSION", "juzgar(", "01e_juez", "juez_post",
                                          "motivo_juez", "sacar_juzgadas")), f
    assert not hasattr(mp, "juzgar") and not hasattr(mp, "JUEZ_SYSTEM")
    assert "juez_post" not in mp.llamar.__code__.co_varnames
