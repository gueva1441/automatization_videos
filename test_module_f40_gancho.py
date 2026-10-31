"""
test_module_f40_gancho.py — F40 §A (HANDOFF_F40_gancho_subs_kyshtym §6; DECISIONES 2026-10-27 18:30): el gancho deja de
cortar por una cifra suelta en cualquier parte de la voz. Se borró `pantalla_filtros.gancho_dicho` (y su lugar en
`ORDEN`) y `dice_voz` (m01e_pantalla, pantalla_entrada); la coincidencia de una cifra del dato del gancho con la voz de
todo el video es de `no_dicho`. F64 Etapa 3 (DECISIONES 2026-10-31 14:20): ya no se le PREGUNTA al autor: es una MARCA
(con dónde la dice la voz: cap, oración y la oración) que juzga pantalla_verificador en una llamada; «pasa» → la ficha
queda con `juicio_verificador`; «corta» → cae con quien «verificador».
    1  D03 «Nivel 6 de 7» (Kyshtym, la ficha del intento 1 de F39) con «Seis de octubre…» en ch05 → marca `no_dicho`
       con cap, oración y texto (no corta en seco); con JUEZ_PASA queda, con juicio_verificador;
    2  un gancho cuya cifra la voz dice de verdad con el mismo hecho (D91 «Más de 5000 personas»; la voz: «Más de cinco
       mil personas estaban en el sitio industrial…» en ch04 [11], la única vez) → marca; con un juez que la corta cae
       con quien «verificador» y el autor, en la vuelta, la saca → sale;
    3  Vajont v6 D195 «1.269 de 1.328» → sin marcas, sin juez, sin juicio_verificador (sin cambio);
    4  lo borrado no está; Fase 2 (validar_papel → no_dicho) deja la coincidencia en ctx["dichos"]; F65a Etapa B
       (DECISIONES 2026-10-31 15:49): `pantalla_filtros._sin_juicio` volvió y con ctx["juicio"] (los `tokens` del
       `juicio_verificador` de la ficha del papel) la coincidencia que el verificador ya pasó no cuenta.
Borrado por F64 Etapa 3: test_1_d03_pregunta_con_cap_oracion_y_texto y test_1_d03_el_autor_la_mantiene_otro_hecho_queda
(reescritos en test_1_d03_llega_como_marca_no_dicho_con_cap_oracion_y_texto), test_2_mismo_hecho_el_autor_la_saca_sale
(reescrito en test_2_mismo_hecho_el_verificador_la_corta_y_el_autor_la_saca), test_2_sin_preguntar_al_cierre_corta_como_no_dicho
(ya no hay cierre que corte sin preguntar) y test_4_fase2_no_dicho_en_el_gancho_respeta_el_juicio_del_autor (F64 borró
`juicio` de pantalla_filtros; F65a Etapa B lo trae de vuelta con el juicio del VERIFICADOR:
test_4_no_dicho_en_el_gancho_respeta_el_juicio_del_verificador reemplaza a test_4_no_dicho_en_el_gancho_deja_la_coincidencia_en_dichos);
`preguntas`, `juicio_autor`, `cortados_al_cierre` y «¿es el mismo hecho? si no, mantenelo» no existen.
Sin API (POST falso; el verificador es JUEZ_PASA). Los datos reales se leen de sus copias congeladas en
lab/hyperframes/f40/a/ (nunca de data/).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from script_engine import m01e_pantalla as mp  # noqa: E402
from script_engine import pantalla_entrada as pe  # noqa: E402
from script_engine import pantalla_filtros as pf  # noqa: E402
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
A = ROOT / "lab" / "hyperframes" / "f40" / "a"
GANCHO = ("ch01", 1)
SEIS = "Seis de octubre de mil novecientos cincuenta y siete."
hay = pytest.mark.skipif(not (A / "kyshtym" / "01e_pantalla.raw.json").exists()
                         or not (A / "vajont" / "01e_pantalla.raw.json").exists(), reason="sin las copias de F40 §A")


def _ent(nombre: str) -> dict:
    """La entrada de m01e desde la copia congelada, con la voz que vio m01e (`entrada.caps` del raw)."""
    raw = json.loads((A / nombre / "01e_pantalla.raw.json").read_text(encoding="utf-8"))
    carga = mp.cargar(nombre, A)
    e = mp.entrada(carga, raw["entrada"]["clima"], {"valor": mp.SEG_POR_PALABRA_RESPALDO, "oraciones": 0, "caps": 0,
                                                     "voz": "test"})
    e["caps"] = raw["entrada"]["caps"]
    e["_pool"] = carga["pool"]
    return e


@pytest.fixture(scope="module")
def ky() -> dict:
    return _ent("kyshtym")


@pytest.fixture(scope="module")
def d03() -> dict:
    """La ficha D03 que el autor propuso en el intento 1 del papel de F39 (ch01 beat 1, oración [5])."""
    raw = json.loads((A / "kyshtym" / "01e_pantalla.raw.json").read_text(encoding="utf-8"))
    fi = next(b["ficha"] for b in raw["intentos"][0]["respuesta"]["beats"] if (b["cap"], b["beat"]) == GANCHO)
    assert fi["pool_id"] == "D03" and fi["texto"] == "Nivel 6 de 7" and fi["sentence_idx"] == 5
    return fi


def _resp(fi: dict | None) -> dict:
    return {"beats": [{"cap": GANCHO[0], "beat": GANCHO[1], "ficha": fi}]}


# D91 (Kyshtym): «más de 5000 personas en la zona industrial»; la voz lo dice una sola vez, con el mismo hecho, en
# ch04 [11] («Más de cinco mil personas estaban en el sitio industrial…»)
D91 = {"pool_id": "D91", "sentence_idx": 5, "palabra": "hormigón", "etiqueta": "EN LA ZONA INDUSTRIAL",
       "texto": "Más de 5000 personas expuestas", "respaldo": "más de 5000 personas en la zona industrial",
       "autor": None, "aporta": "x"}


def _post_seq(resps: list[dict], pedidos: list[dict]):
    """POST falso: la llamada k devuelve resps[k] (la última se repite)."""
    def post(body: dict) -> dict:
        pedidos.append(body)
        r = resps[min(len(pedidos) - 1, len(resps) - 1)]
        return {"content": [{"type": "text", "text": json.dumps(r, ensure_ascii=False)}],
                "usage": {"input_tokens": 1000, "output_tokens": 200}, "stop_reason": "end_turn"}
    return post


def _ficha_final(res: dict) -> dict | None:
    return next((s["ficha"] for s in res["validacion"]["beats"] if (s["cap"], s["beat"]) == GANCHO), None)


# ═══════════════════════ 1. D03 con «seis de octubre» en otro cap: marca no_dicho con dónde → el verificador ═══════════════════════

@hay
def test_1_d03_llega_como_marca_no_dicho_con_cap_oracion_y_texto(ky, d03):
    v = mp.validar(_resp(d03), ky)                                              # JUEZ_PASA
    assert not [d for d in v["descartados"] if d.get("que") == "ficha"]          # antes de F40: no_dicho «(gancho)», en seco
    nd = [m for m in v["marcas"] if m["regla"] == "no_dicho"]
    assert [(m["pool_id"], m["cap"], m["beat"], m["sentence_idx"]) for m in nd] == [("D03", "ch01", 1, 5)] * 2
    assert [(m["coincidencia"]["token"], m["coincidencia"]["cap"], m["coincidencia"]["idx"]) for m in nd] == \
        [("6", "ch05", 12), ("7", "ch04", 14)]                                  # fuera de la oración ancla y sus vecinas
    assert nd[0]["coincidencia"]["oracion"] == SEIS
    assert nd[0]["etiqueta"] == "ESCALA DE ACCIDENTES NUCLEARES" and nd[0]["texto"] == "Nivel 6 de 7"
    assert not any("D03" in m for m in v["motivos"])                            # no es motivo: lo juzga el verificador
    f = next(s["ficha"] for s in v["beats"] if (s["cap"], s["beat"]) == GANCHO)
    assert f["pool_id"] == "D03" and f["juicio_verificador"]["tokens"]["no_dicho"] == ["6", "7"]
    assert "juicio_autor" not in f and "preguntas" not in v


# ═══════════════════════ 2. la voz dice la cifra con el mismo hecho: el verificador la corta; el autor la saca ═══════════════════════

@hay
def test_2_mismo_hecho_el_verificador_la_corta_y_el_autor_la_saca(ky, tmp_path):
    v = mp.validar(_resp(D91), ky)                                              # JUEZ_PASA: marca, no corta
    nd = [m for m in v["marcas"] if m["regla"] == "no_dicho"]
    assert [(m["coincidencia"]["token"], m["coincidencia"]["cap"], m["coincidencia"]["idx"]) for m in nd] == [("5000", "ch04", 11)]
    assert nd[0]["coincidencia"]["oracion"].startswith("Más de cinco mil personas estaban en el sitio industrial")
    assert not [d for d in v["descartados"] if d.get("pool_id") == "D91"]

    def corta(marcas, caps):                                                    # el verificador: el mismo hecho
        return {"veredictos_fichas": [{"pool_id": "D91", "cap": "ch01", "beat": 1, "veredicto": "corta",
                                       "motivo": "la voz cuenta el mismo hecho", "oracion": {"cap": "ch04", "idx": 11}}],
                "veredictos_descartes": []}
    vc = mp.validar(_resp(D91), ky, juez=corta)
    d = next(d for d in vc["descartados"] if d.get("pool_id") == "D91")
    assert d["quien"] == "verificador" and d["regla"] == "no_dicho" and d["motivo"] == "la voz cuenta el mismo hecho (ch04 [11])"
    assert next(s["ficha"] for s in vc["beats"] if (s["cap"], s["beat"]) == GANCHO) is None
    motivo = ("D91 (ch01 beat 1) «EN LA ZONA INDUSTRIAL · Más de 5000 personas expuestas»: no_dicho: la voz cuenta el "
              "mismo hecho (ch04 [11])")
    assert motivo in vc["motivos"]
    # por llamar: el motivo del verificador va a la vuelta 1 y el autor saca la ficha → sale
    pedidos: list[dict] = []
    saca = {"cambios": [{"cap": GANCHO[0], "beat": GANCHO[1], "ficha": None}]}
    res = mp.llamar(ky, tmp_path, post=_post_seq([_resp(D91), saca], pedidos), juez=corta)
    assert motivo in res["reintento"]["vueltas"][0]["motivos"] and motivo in pedidos[1]["messages"][0]["content"]
    assert _ficha_final(res) is None
    assert "D91" not in json.dumps(res["final"], ensure_ascii=False)
    assert len(res["verificador"]) == 1 and res["usd_verificador"] == 0.0     # una llamada al juez (la del intento 1)


# ═══════════════════════ 3. Vajont v6 D195: sin cambio ═══════════════════════

@hay
def test_3_vajont_d195_pasa_sin_pregunta():
    ent = _ent("vajont")
    d195 = {"pool_id": "D195", "sentence_idx": 2, "palabra": "Longarone", "etiqueta": "LONGARONE",
            "texto": "1.269 de 1.328 habitantes murieron", "respaldo": "1.269 de 1.328 habitantes fallecidos",
            "autor": None, "aporta": "x"}
    v = mp.validar(_resp(d195), ent)
    assert not [d for d in v["descartados"] if d.get("que") == "ficha"]
    assert not [m for m in v["marcas"] if m["pool_id"] == "D195"] and v["verificador"] is None   # sin marcas no hay juez
    f = next(s["ficha"] for s in v["beats"] if (s["cap"], s["beat"]) == GANCHO)
    assert f["pool_id"] == "D195" and "juicio_verificador" not in f and "juicio_autor" not in f


# ═══════════════════════ 4. lo borrado y Fase 2 ═══════════════════════

def test_4_gancho_dicho_y_dice_voz_borrados():
    assert not hasattr(pf, "gancho_dicho")
    assert [pf.regla(f) for f in pf.ORDEN] == ["anclaje", "candado", "no_dicho", "spoiler", "lectura"]
    src = "".join((ROOT / "script_engine" / n).read_text(encoding="utf-8")
                  for n in ("pantalla_filtros.py", "m01e_pantalla.py", "pantalla_entrada.py"))
    assert "dice_voz" not in src and "gancho_dicho" not in src.replace("borró `gancho_dicho`", "") \
        .replace("ya no la corta `gancho_dicho`", "")
    x = pe._item("D1", {"datos": [{"id": "D1", "texto": "Nivel 6 de 7", "fuente": "f"}]}, {}, 1, True)
    assert x["gancho"] is True and "dice_voz" not in x


def _ctx_gancho() -> dict:
    sents = [{"texto": "Una columna de humo sube sobre la planta."}, {"texto": "Nadie dijo nada."},
             {"texto": "Esa noche cenaron temprano."}, {"texto": "Seis de octubre de mil novecientos cincuenta y siete."}]
    return {"sents": sents, "si": 0, "x": {"gancho": True}, "txt": "Nivel 6 de 7", "tipo": "hecho",
            "voz_video": [s["texto"] for s in sents]}


def test_4_no_dicho_en_el_gancho_respeta_el_juicio_del_verificador():
    """F65a Etapa B: sin juicio la coincidencia del gancho es motivo y queda en ctx["dichos"] (en el papel es la marca);
    con ctx["juicio"] = los `tokens` del `juicio_verificador` («pasa» el «6») el mismo ctx no corta y «6» sale de
    `dichos`; un juicio de otra regla no la salva."""
    ctx = _ctx_gancho()
    mot = pf.no_dicho({}, {}, ctx)
    assert mot == "la voz lo dice en otra oración del video (gancho): ['6']" and ctx["dichos"] == ["6"]
    ctx = {**_ctx_gancho(), "juicio": {"no_dicho": ["6"]}}
    assert pf.no_dicho({}, {}, ctx) is None and ctx["dichos"] == []
    ctx = {**_ctx_gancho(), "juicio": {"spoiler": ["6"]}}
    assert pf.no_dicho({}, {}, ctx) == "la voz lo dice en otra oración del video (gancho): ['6']"
    assert pf._sin_juicio({"juicio": {"no_dicho": ["6", 7]}}, "no_dicho", ["6", "7", "8"]) == ["8"]
    assert pf._sin_juicio({}, "no_dicho", ["6"]) == ["6"]


def test_4_fuera_del_gancho_no_dicho_igual_que_antes():
    ctx = {**_ctx_gancho(), "x": {"gancho": False}}
    assert pf.no_dicho({}, {}, ctx) is None                    # la oración [3] no es vecina de la [0]
    ctx = {**_ctx_gancho(), "x": {"gancho": False}, "si": 2}
    assert pf.no_dicho({}, {}, ctx) == "la voz lo dice en la oración ancla o en una vecina: ['6']"


def test_prompt_no_cambia():
    import hashlib
    md5 = {k: hashlib.md5(getattr(mp, k).encode("utf-8")).hexdigest()
           for k in ("PANTALLA_SYSTEM", "FORMATO_SALIDA", "FORMATO_REINTENTO", "REINTENTO_PARCIAL")}
    assert md5 == {"PANTALLA_SYSTEM": "85d094bed6090b14d1802ca97433d982",      # F64 Etapa 0 (antes 7d2ccdd2…)
                   "FORMATO_SALIDA": "f63ad89ad721f319370fe2ebb8b539b5",
                   "FORMATO_REINTENTO": "07cd8ad0fb3f3e31b46dcd2a6641fa23",
                   "REINTENTO_PARCIAL": "29deed051c1440eb4ea8c2b5e7b776e8"}
    assert mp.prompt_md5() == "f2bfdf2044a4c77a59fc62ebe93966c2" and mp.PROMPT_VERSION == "m01e-7"
