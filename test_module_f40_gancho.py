"""
test_module_f40_gancho.py — F40 §A (HANDOFF_F40_gancho_subs_kyshtym §6; DECISIONES 2026-10-27 18:30): el gancho deja de
cortar por una cifra suelta en cualquier parte de la voz. Se borró `pantalla_filtros.gancho_dicho` (y su lugar en
`ORDEN`) y `dice_voz` (m01e_pantalla, pantalla_entrada); la coincidencia de una cifra del dato del gancho con la voz de
todo el video es de `no_dicho` y se le PREGUNTA al autor (F37 §A.4 / F38c / F38d): la pregunta dice dónde la dice la
voz (cap, oración y la oración), con el formato del spoiler; lo que el autor mantiene queda `juicio_autor`.
    1  D03 «Nivel 6 de 7» (Kyshtym, la ficha del intento 1 de F39) con «Seis de octubre…» en ch05 → pregunta con cap,
       oración y texto; el autor la mantiene («otro hecho») → queda, con juicio_autor;
    2  un gancho cuya cifra la voz dice de verdad con el mismo hecho (D91 «Más de 5000 personas»; la voz: «Más de cinco
       mil personas estaban en el sitio industrial…» en ch04 [11], la única vez) → pregunta; el autor la saca → sale;
    3  Vajont v6 D195 «1.269 de 1.328» → pasa sin pregunta (sin cambio);
    4  lo borrado no está; Fase 2 (validar_papel → no_dicho) respeta el juicio del autor en el gancho.
Sin API (POST falso). Los datos reales se leen de sus copias congeladas en lab/hyperframes/f40/a/ (nunca de data/).
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

ROOT = Path(__file__).resolve().parent
A = ROOT / "lab" / "hyperframes" / "f40" / "a"
GANCHO = ("ch01", 1)
SEIS = "Seis de octubre de mil novecientos cincuenta y siete."
PREGUNTA_D03_6 = ("D03 (ch01 beat 1, oración [5]) «ESCALA DE ACCIDENTES NUCLEARES · Nivel 6 de 7»: la voz dice «6» en "
                  f"ch05 [12] («{SEIS}»); ¿es el mismo hecho? si no, mantenelo")
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


# ═══════════════════════ 1. D03 con «seis de octubre» en otro cap: pregunta → otro hecho → queda ═══════════════════════

@hay
def test_1_d03_pregunta_con_cap_oracion_y_texto(ky, d03):
    v = mp.validar(_resp(d03), ky)
    assert not [d for d in v["descartados"] if d.get("que") == "ficha"]          # antes: no_dicho «(gancho)», en seco
    nd = [q for q in v["preguntas"] if q["regla"] == "no_dicho"]
    assert [(q["token"], q["donde"][:2]) for q in nd] == [("6", ("ch05", 12)), ("7", ("ch04", 14))]
    assert all(q.get("video") for q in nd)                       # fuera de la oración ancla y sus vecinas
    assert nd[0]["donde"][2] == SEIS
    assert PREGUNTA_D03_6 in v["motivos"]                         # el formato del spoiler: cap [oración] («…»)
    assert not any("D03" in m and "no_dicho" in m and "(gancho)" in m for m in v["motivos"])


@hay
def test_1_d03_el_autor_la_mantiene_otro_hecho_queda(ky, d03, tmp_path):
    pedidos: list[dict] = []
    res = mp.llamar(ky, tmp_path, tope=100.0, post=_post_seq([_resp(d03), {"cambios": []}], pedidos))
    assert PREGUNTA_D03_6 in res["reintento"]["vueltas"][0]["motivos"]          # se le preguntó en la vuelta 1
    assert PREGUNTA_D03_6 in pedidos[1]["messages"][0]["content"]
    f = _ficha_final(res)                                                        # no la cambió: «otro hecho»
    assert f is not None and f["pool_id"] == "D03"
    assert set(f["juicio_autor"]["no_dicho"]) == {"6", "7"}
    assert not [d for d in res["validacion"]["descartados"] if d.get("pool_id") == "D03"]
    assert not res["reintento"]["cortados_al_cierre"]


# ═══════════════════════ 2. la voz dice la cifra con el mismo hecho: el autor la saca → sale ═══════════════════════

@hay
def test_2_mismo_hecho_el_autor_la_saca_sale(ky, tmp_path):
    v = mp.validar(_resp(D91), ky)
    nd = [q for q in v["preguntas"] if q["regla"] == "no_dicho"]
    assert [(q["token"], q["donde"][:2]) for q in nd] == [("5000", ("ch04", 11))]
    assert nd[0]["donde"][2].startswith("Más de cinco mil personas estaban en el sitio industrial")
    assert (f"D91 (ch01 beat 1, oración [5]) «EN LA ZONA INDUSTRIAL · Más de 5000 personas expuestas»: la voz dice "
            f"«5000» en ch04 [11] («{nd[0]['donde'][2]}»); ¿es el mismo hecho? si no, mantenelo") in v["motivos"]
    pedidos: list[dict] = []
    saca = {"cambios": [{"cap": GANCHO[0], "beat": GANCHO[1], "ficha": None}]}   # «mismo hecho»: la saca
    res = mp.llamar(ky, tmp_path, tope=100.0, post=_post_seq([_resp(D91), saca], pedidos))
    assert _ficha_final(res) is None
    assert "D91" not in json.dumps(res["final"], ensure_ascii=False)


@hay
def test_2_sin_preguntar_al_cierre_corta_como_no_dicho(ky):
    """F38d §A.1: una coincidencia que el autor no contestó corta al cerrar (regla no_dicho, con dónde: otro cap)."""
    v = mp.validar(_resp(D91), ky, {}, final=True)
    d = next(d for d in v["descartados"] if d.get("pool_id") == "D91")
    assert d["regla"] == "no_dicho" and "en otra oración del video (gancho)" in d["motivo"]


# ═══════════════════════ 3. Vajont v6 D195: sin cambio ═══════════════════════

@hay
def test_3_vajont_d195_pasa_sin_pregunta():
    ent = _ent("vajont")
    d195 = {"pool_id": "D195", "sentence_idx": 2, "palabra": "Longarone", "etiqueta": "LONGARONE",
            "texto": "1.269 de 1.328 habitantes murieron", "respaldo": "1.269 de 1.328 habitantes fallecidos",
            "autor": None, "aporta": "x"}
    v = mp.validar(_resp(d195), ent)
    assert not [d for d in v["descartados"] if d.get("que") == "ficha"]
    assert not [q for q in v["preguntas"] if q["pool_id"] == "D195"]
    f = next(s["ficha"] for s in v["beats"] if (s["cap"], s["beat"]) == GANCHO)
    assert f["pool_id"] == "D195" and "pregunta" not in f and "juicio_autor" not in f


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


def _ctx_gancho(juicio: dict | None) -> dict:
    sents = [{"texto": "Una columna de humo sube sobre la planta."}, {"texto": "Nadie dijo nada."},
             {"texto": "Esa noche cenaron temprano."}, {"texto": "Seis de octubre de mil novecientos cincuenta y siete."}]
    return {"sents": sents, "si": 0, "x": {"gancho": True}, "txt": "Nivel 6 de 7", "tipo": "hecho",
            "voz_video": [s["texto"] for s in sents], "juicio": juicio or {}}


def test_4_fase2_no_dicho_en_el_gancho_respeta_el_juicio_del_autor():
    ctx = _ctx_gancho(None)
    mot = pf.no_dicho({}, {}, ctx)
    assert mot == "la voz lo dice en otra oración del video (gancho): ['6']" and ctx["dichos"] == ["6"]
    ctx = _ctx_gancho({"no_dicho": ["6"]})                     # el autor la mantuvo en el papel: otro hecho
    assert pf.no_dicho({}, {}, ctx) is None and ctx["dichos"] == []


def test_4_fuera_del_gancho_no_dicho_igual_que_antes():
    ctx = {**_ctx_gancho(None), "x": {"gancho": False}}
    assert pf.no_dicho({}, {}, ctx) is None                    # la oración [3] no es vecina de la [0]
    ctx = {**_ctx_gancho(None), "x": {"gancho": False}, "si": 2}
    assert pf.no_dicho({}, {}, ctx) == "la voz lo dice en la oración ancla o en una vecina: ['6']"


def test_prompt_no_cambia():
    import hashlib
    md5 = {k: hashlib.md5(getattr(mp, k).encode("utf-8")).hexdigest()
           for k in ("PANTALLA_SYSTEM", "FORMATO_SALIDA", "FORMATO_REINTENTO", "REINTENTO_PARCIAL")}
    assert md5 == {"PANTALLA_SYSTEM": "7d2ccdd28055d6e621d1d251a0fe8bb7",
                   "FORMATO_SALIDA": "f63ad89ad721f319370fe2ebb8b539b5",
                   "FORMATO_REINTENTO": "07cd8ad0fb3f3e31b46dcd2a6641fa23",
                   "REINTENTO_PARCIAL": "29deed051c1440eb4ea8c2b5e7b776e8"}
    assert mp.prompt_md5() == "3b98aef1d8595124967ac7a85b75bab7" and mp.PROMPT_VERSION == "m01e-6"
