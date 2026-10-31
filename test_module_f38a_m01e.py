"""
test_module_f38a_m01e.py — F38 §A (HANDOFF_F38_reintento_tarjeta_juez), la parte de script_engine/m01e_pantalla:
    §A.1  reintento parcial: el reintento devuelve solo `cambios` de los beats con motivo y el código los fusiona por
          (cap, beat); con la respuesta del intento 1 de F37 y un reintento armado desde el de F37, D128, AVISO, ALARMA
          (y T92) sobreviven, y los cambios en beats sin motivo se ignoran y se anotan. Q14 NO estaba en el intento 1
          (el autor lo descartó ahí: «una sola ficha, se eligió T85»): no hay nada que sobreviva;
    §A.2  (F38e §D: la fecha-hora del segundo 0 se borró del código; sus dos tests también);
    F38b  (HANDOFF_F38b_quitar_juez) el juez de §A.3 se borró con sus tests y su grabación; la línea del gancho vuelve
          a la de m01e-1 (m01e-4) y nada en script_engine llama a ESE juez (el de anclaje de F38). F64 Etapa 3 trae
          `juez` = el verificador de fichas (pantalla_verificador, el parámetro `juez` de validar/llamar): es otro.
    F64 Etapa 3: las coincidencias `spoiler`/`no_dicho`/`contradice` del intento 1 de F37 (D47, T15, T39, D105, D161) ya
          no son preguntas al autor ni motivos: son marcas que el verificador juzga; con JUEZ_PASA quedan.
    F65a Etapa A (DECISIONES 2026-10-31 15:49): un beat sin su `a_pantalla` (ch05 b8 sin Q50, ch07 b13 sin D245) ya no
          es motivo ni clave: queda en `a_pantalla_vacios`. Con eso el ÚNICO motivo del intento 1 de F37 es el descarte
          Q15 que vuelve (sin beat) → `beats_con_motivo` vacío → `llamar` cierra «sin beat» con 1 POST y sin vueltas.
          La fusión parcial (lo del intento 1 sobrevive, el cambio en un beat sin motivo se ignora) se mide con
          `fusionar` + `validar` directo sobre los beats que hasta F64 tenían motivo (el camino por `llamar` ya no pasa
          por ahí con estos datos).
Sin API: el autor va con POST falsos; el verificador es JUEZ_PASA. El papel de F37 se lee de su copia congelada
(lab/hyperframes/f37/c).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from script_engine import m01e_pantalla as mp  # noqa: E402
from script_engine import pantalla_verificador as pv  # noqa: E402


def JUEZ_PASA(marcas: list[dict], caps: list[dict]) -> dict:
    """F64 Etapa 3: el verificador falso de los tests: «pasa» toda ficha marcada y «no_dicho» todo descarte dudoso."""
    return {"veredictos_fichas": [{"pool_id": m["pool_id"], "cap": m["cap"], "beat": m["beat"], "veredicto": "pasa",
                                   "motivo": "test", "oracion": None} for m in marcas if m.get("que") != "descarte"],
            "veredictos_descartes": [{"pool_id": m["pool_id"], "veredicto": "no_dicho", "motivo": "test", "oracion": None}
                                     for m in marcas if m.get("que") == "descarte"],
            "usage": None, "usd": 0.0, "segundos": 0.0, "pedido_md5": "test", "intentos": 0}


@pytest.fixture(scope="module", autouse=True)
def _sin_verificador_real():
    """F64 Etapa 3: ningún test de este archivo llama al verificador real (gasta API). `validar` sin `juez` toma
    `_juez_por_defecto` → JUEZ_PASA; `llamar` sin `juez` toma `pantalla_verificador.verificar` con el POST falso, que
    también se reemplaza por JUEZ_PASA para que la llamada del verificador no consuma las respuestas en orden del POST."""
    m = pytest.MonkeyPatch()
    m.setattr(mp, "_juez_por_defecto", lambda: JUEZ_PASA)
    m.setattr(pv, "verificar", lambda marcas, caps, **kw: JUEZ_PASA(marcas, caps))
    yield
    m.undo()


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
    cambios = [{"cap": c, "beat": b, "ficha": _fila(r2, c, b)["ficha"],
                **({"sello": _fila(r2, c, b)["sello"]} if (c, b) == ("ch07", 13) else {})} for c, b in beats_m]
    cambios += [{"cap": "ch06", "beat": 11, "ficha": _fila(r2, "ch06", 11)["ficha"], "sello": None}]
    if ("ch07", 13) not in beats_m:
        cambios += [{"cap": "ch07", "beat": 13, "ficha": _fila(r2, "ch07", 13)["ficha"],
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
    assert len(v1["motivos_beat"]) == len(v1["motivos"]) == len(v1["claves"])
    # F64 Etapa 3: las coincidencias del intento 1 son marcas para el verificador, no motivos (con JUEZ_PASA quedan)
    assert {(m["regla"], m["pool_id"], m["cap"], m["beat"], m["coincidencia"]["token"])
            for m in v1["marcas"] if m["que"] == "ficha"} == {("spoiler", "D47", "ch02", 3, "2"),
                                                               ("spoiler", "T15", "ch03", 4, "3"),
                                                               ("spoiler", "T39", "ch04", 6, "50"),
                                                               ("no_dicho", "D105", "ch04", 7, "1962"),
                                                               ("spoiler", "D161", "ch05", 8, "2")}
    assert all(_fila(v1, c, b)["ficha"]["juicio_verificador"]["tokens"] for c, b in
               (("ch02", 3), ("ch03", 4), ("ch04", 6), ("ch04", 7), ("ch05", 8)))
    assert not [d for d in v1["descartados"] if d.get("quien") == "verificador"]
    # F65a Etapa A: ch05 b8 (sin su `a_pantalla` Q50) y ch07 b13 (T92, sin D245) ya no son motivo: solo aviso
    assert [(a["cap"], a["beat"]) for a in v1["a_pantalla_vacios"]] == [("ch05", 8), ("ch07", 13)]
    assert not any(str(c[0]) == "a_pantalla" for c in v1["claves"])
    vuelve = [mb for m, mb in zip(v1["motivos"], v1["motivos_beat"]) if "vuelve a ser candidato" in m]
    assert vuelve and all(mb == [] for mb in vuelve)                      # Q15: sin beat
    assert len(v1["motivos"]) == 1 and v1["claves"] == [("voz_lo_dice", "Q15")] and beats_m == []
    # la fusión parcial, directa (los beats que hasta F64 tenían motivo): lo del intento 1 sobrevive, el cambio de ch06
    # b11 (sin motivo) se ignora y se anota, el de ch07 b13 entra (D245; su sello MEMORIA cae: ya salió en ch06 b11)
    bm = [("ch05", 8), ("ch07", 13)]
    fus, aplicados, ignorados = mp.fusionar(r1, _cambios_desde_f37(raw37, bm), bm)
    assert [(a["cap"], a["beat"], a["partes"]) for a in aplicados] == [("ch05", 8, ["ficha"]), ("ch07", 13, ["ficha", "sello"])]
    assert [(i["cap"], i["beat"], i["motivo"]) for i in ignorados] == [("ch06", 11, "el beat no tiene motivo")]
    fin = mp.validar(fus, vajont)
    assert _fila(fin, "ch06", 11)["ficha"]["pool_id"] == "D128" and _fila(fin, "ch06", 11)["sello"]["palabra"] == "MEMORIA"
    assert _fila(fin, "ch03", 4)["sello"]["palabra"] == "AVISO"
    assert _fila(fin, "ch07", 13)["ficha"]["pool_id"] == "D245" and _fila(fin, "ch07", 13)["sello"] is None
    assert any(d.get("cap") == "ch07" and d.get("beat") == 13 and d["que"] == "sello" and d["texto"] == "MEMORIA"
               for d in fin["descartados"] if d.get("quien") == "validación")
    assert [(a["cap"], a["beat"]) for a in fin["a_pantalla_vacios"]] == [("ch05", 8)]   # D245 ya está en ch07 b13
    assert _fila(fus, "ch01", 1)["ficha"]["sentence_idx"] == 15                       # D131 sin motivo: queda en [15]
    # por llamar: el único motivo (Q15) no tiene beat → no hay reintento: cierra «sin beat» con 1 POST (el del intento 1)
    pedidos: list[dict] = []
    res = mp.llamar(vajont, tmp_path, post=_post_seq([r1, _cambios_desde_f37(raw37, bm)], pedidos))
    rt = res["reintento"]
    assert len(pedidos) == 1 and rt["cierre"] == "sin beat" and rt["vueltas"] == [] and rt.get("tipo") is None
    assert rt["sin_beat"] == v1["motivos"] and res["claves"] == [["voz_lo_dice", "Q15"]]
    assert _fila(res["final"], "ch06", 11)["ficha"]["pool_id"] == "D128"               # el intento 1, tal cual
    assert _fila(res["final"], "ch07", 13)["ficha"]["pool_id"] == "T92"
    assert (tmp_path / f"{mp.ARCHIVO}.raw.json").exists()
    raw = json.loads((tmp_path / f"{mp.ARCHIVO}.raw.json").read_text(encoding="utf-8"))
    assert len(raw["intentos"]) == 1 and raw["reintento"]["cierre"] == "sin beat"
    md = mp.a_markdown(mp.armar(vajont, res))
    assert "### Motivos sin beat (no hubo reintento)" in md and "cerró por: **sin beat**" in md
    assert "### Reintento parcial" not in md


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
    assert mp.FORMATO_REINTENTO.startswith('{"cambios": [{"cap": "ch03", "beat": 5, "ficha":')
    assert mp.PROMPT_VERSION == "m01e-7"          # F38b: + el gancho de m01e-1 · F38d §A.2 · F38e §C.1: el de la prueba 1 · F64 Etapa 0


# ═══════════════════════ F38b: la línea del gancho de m01e-1, sin juez ═══════════════════════

def test_f38b_gancho_literal_de_m01e_1_sin_las_primeras_oraciones():
    h = (ROOT / "lab" / "hyperframes" / "f38" / "HANDOFF_F38b_quitar_juez.md").read_text(encoding="utf-8")
    linea = ("cualquier dato del archivo que la voz no diga en todo el video y que haga quedarse a quien mira: el gancho "
             "nunca queda sin ficha.")
    assert linea in h and linea in mp.PANTALLA_SYSTEM
    assert "primeras oraciones" not in mp.PANTALLA_SYSTEM
    assert mp.PROMPT_VERSION == "m01e-7"                      # F38d §A.2 · F38e §C.1 · F64 Etapa 0 (la línea del gancho sigue igual)


def test_f38b_nada_llama_a_un_juez():
    """El juez de anclaje de F38 §A.3 no está (sus nombres). F64 Etapa 3: la palabra `juez` SÍ está en m01e_pantalla
    (el parámetro `juez` de validar/llamar = el verificador de fichas de pantalla_verificador) y el crítico «¿estorba?»
    de pantalla_colocar/clima también se llama `juez`: son otros; lo que se mira son los nombres del de F38."""
    for f in (ROOT / "script_engine").glob("*.py"):
        txt = f.read_text(encoding="utf-8", errors="replace")
        assert not any(n in txt for n in ("JUEZ_SYSTEM", "JUEZ_VERSION", "juzgar(", "01e_juez", "juez_post",
                                          "motivo_juez", "sacar_juzgadas")), f
    assert not hasattr(mp, "juzgar") and not hasattr(mp, "JUEZ_SYSTEM")
    assert "juez_post" not in mp.llamar.__code__.co_varnames
