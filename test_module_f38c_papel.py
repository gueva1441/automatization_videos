"""
test_module_f38c_papel.py — F38c §A.1 y §A.2 (HANDOFF_F38c_marcas_contradice_decimales), la parte del papel:
    §A.1  dos marcas distintas: el `a_pantalla` de la escaleta va en un campo propio del ítem ({beat, por_que}) y no en
          `beats_que_lo_cuentan`; un beat sin ninguno de sus `a_pantalla` es motivo del reintento (y ⚠ en el .md); si
          lleva uno, los demás de ese beat no son motivo; un `a_pantalla` descartado «voz_lo_dice» se verifica contra
          todo el video;
    §A.2  la cifra que contradice la voz es una pregunta al autor (regla `contradice`, token = la cifra de la voz); lo
          que el autor mantiene queda en `juicio_autor["contradice"]` y el chequeo 5 de gfx_guion lo respeta.
Sin API. Las entradas de Fase 1 de Vajont y el papel de F38b se leen de sus copias congeladas (lab/hyperframes/f38/b2).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from script_engine import gfx_guion as gg  # noqa: E402
from script_engine import m01e_pantalla as mp  # noqa: E402
from script_engine import pantalla_filtros as pf  # noqa: E402

ROOT = Path(__file__).resolve().parent
VAJONT = "f8s3-vajont"
B2 = ROOT / "lab" / "hyperframes" / "f38" / "b2"
FASE1 = B2 / "fase1"
RAW_F38B = B2 / "01e_pantalla.raw.json"
CLIMA = ["PÁNICO", "CALMA", "AMENAZA", "AVISO", "ALARMA", "INMINENTE", "COLAPSO", "SILENCIO", "RABIA", "MEMORIA"]
SEG = {"valor": 0.3459, "oraciones": 200, "caps": 9, "voz": "prueba"}
PREGUNTA_D40 = ("D40 (ch04 beat 7, oración [13]) «COTA MÁXIMA · 722.50 metros»: la voz dice «715» para lo mismo, en la "
                "oración ancla o en una vecina en ch04 [13] («La cota autorizada fue de setecientos quince.»); ¿es el "
                "mismo hecho? si no, mantenelo")
hay_vajont = pytest.mark.skipif(not RAW_F38B.exists() or not (FASE1 / VAJONT).exists(), reason="sin Vajont (F38b)")


@pytest.fixture(scope="module")
def ent() -> dict:
    carga = mp.cargar(VAJONT, FASE1)
    e = mp.entrada(carga, CLIMA, SEG)
    e["_pool"] = carga["pool"]
    return e


@pytest.fixture(scope="module")
def papel() -> dict:
    """La respuesta final del autor en F38b (12 fichas)."""
    return json.loads(RAW_F38B.read_text(encoding="utf-8"))["final"]


@pytest.fixture(scope="module")
def val1(ent, papel) -> dict:
    return mp.validar(papel, ent)


def _x(ent: dict, pid: str) -> dict:
    return next(x for x in ent["archivo"] if x["id"] == pid)


def _a_pantalla_motivos(v: dict) -> list[tuple[str, list]]:
    return [(m, b) for m, b in zip(v["motivos"], v["motivos_beat"])
            if "datos que la escaleta dejó para la pantalla" in m]


def test_prompt_no_cambia():
    # F38c no cambió el prompt (163e1fd1…); F38d §A.2.1 cambia solo la línea de «caben» (m01e-5)
    assert mp.prompt_md5() == "76f1de7ac124b27b0670a5d5234e2f78"


# ═══════════════════════ §A.1 ═══════════════════════

@hay_vajont
def test_a1_a_pantalla_en_campo_propio(ent):
    cuentan = {}
    for b in ent["beats"]:
        for i in [b["dato_central"]] + b["apoyo"]:
            if i:
                cuentan.setdefault(i, []).append(b["n"])
    for pid, beat in (("D128", 11), ("D192", 11), ("D245", 13)):
        x = _x(ent, pid)
        assert x["a_pantalla"]["beat"] == beat
        assert x["a_pantalla"]["por_que"] == ent["a_pantalla"][pid]
        assert beat not in x["beats_que_lo_cuentan"]
        assert x["beats_que_lo_cuentan"] == sorted(cuentan.get(pid) or [])     # solo dato central / apoyo
    para = {x["id"]: x for x in mp._para_modelo(ent)["archivo"]}
    assert para["D128"]["a_pantalla"] == {"beat": 11, "por_que": ent["a_pantalla"]["D128"]}   # el modelo lo ve


@hay_vajont
def test_a1_papel_f38b_da_dos_motivos(val1):
    ms = _a_pantalla_motivos(val1)
    assert [b for _, b in ms] == [[("ch06", 11)], [("ch07", 13)]]
    assert ms[0][0].startswith("el beat 11 de ch06 quedó sin ninguno de los datos que la escaleta dejó para la "
                               "pantalla porque la voz no los dice: D128 («")
    assert "), D192 («" in ms[0][0]
    assert ms[1][0].startswith("el beat 13 de ch07 quedó sin ninguno de los datos que la escaleta dejó para la "
                               "pantalla porque la voz no los dice: D245 («")
    assert [(a["cap"], a["beat"]) for a in val1["a_pantalla_vacios"]] == [("ch06", 11), ("ch07", 13)]


@hay_vajont
def test_a1_md_marca_el_beat_sin_su_a_pantalla(ent, val1):
    p = mp.armar(ent, {"validacion": val1, "modelo": "m", "effort": "e", "intentos": []})
    md = mp.a_markdown(p)
    l11 = next(ln for ln in md.splitlines() if ln.startswith("- beat 11 "))
    assert "⚠ sin su a_pantalla: D128 (el autor no lo puso); D192 (el autor lo descartó [otro]: " in l11
    l13 = next(ln for ln in md.splitlines() if ln.startswith("- beat 13 "))
    assert "⚠ sin su a_pantalla: D245 (el autor no lo puso)" in l13
    assert "⚠ sin su a_pantalla" not in next(ln for ln in md.splitlines() if ln.startswith("- beat 2 "))


@hay_vajont
def test_a1_d128_en_b11_no_da_motivo_por_d192(ent, papel):
    resp = json.loads(json.dumps(papel, ensure_ascii=False))
    fila = next(b for b in resp["beats"] if b["cap"] == "ch06" and b["beat"] == 11)
    fila["ficha"] = {"pool_id": "D128", "sentence_idx": fila["ficha"]["sentence_idx"], "palabra": "",
                     "etiqueta": "MUERTOS", "texto": "1.910 personas", "aporta": "el recuento"}
    v = mp.validar(resp, ent)
    s11 = next(b for b in v["beats"] if b["cap"] == "ch06" and b["beat"] == 11)
    assert s11["ficha"] and s11["ficha"]["pool_id"] == "D128"
    assert [b for _, b in _a_pantalla_motivos(v)] == [[("ch07", 13)]]
    assert not any("D192" in m for m in v["motivos"])


@hay_vajont
def test_a1_a_pantalla_descartado_voz_lo_dice_contra_todo_el_video(ent, papel):
    resp = json.loads(json.dumps(papel, ensure_ascii=False))
    resp["descartados"] = list(resp.get("descartados") or []) + [
        {"pool_id": "D128", "tipo": "voz_lo_dice", "motivo": "la voz ya cuenta los muertos"}]
    v = mp.validar(resp, ent)
    vu = next(x for x in v["vuelven"] if x["pool_id"] == "D128")
    assert vu["caps"] == ["todo el video"]                     # sin `beats_que_lo_cuentan`: todos los caps
    assert vu["falta"] == ["1.910"]


# ═══════════════════════ §A.2 ═══════════════════════

@hay_vajont
def test_a2_d40_pregunta_literal(val1):
    qs = [q for q in val1["preguntas"] if q["regla"] == "contradice"]
    assert [(q["pool_id"], q["token"]) for q in qs] == [("D40", "715")]      # las otras 11 fichas no preguntan
    assert PREGUNTA_D40 in val1["motivos"]
    i = val1["motivos"].index(PREGUNTA_D40)
    assert val1["motivos_beat"][i] == [("ch04", 7)]


@hay_vajont
def test_a2_confirmada_queda_juzgada_y_el_chequeo_5_no_la_marca(ent, papel, val1):
    conf = mp._confirmar(val1["preguntas"])
    assert conf["D40"] == {"contradice": ["715"]}
    v2 = mp.validar(papel, ent, conf)                          # el autor la mantuvo (la misma ficha)
    s7 = next(b for b in v2["beats"] if b["cap"] == "ch04" and b["beat"] == 7)
    assert s7["ficha"]["pool_id"] == "D40"
    assert s7["ficha"]["juicio_autor"]["contradice"] == ["715"]
    assert not [q for q in v2["preguntas"] if q["regla"] == "contradice"]
    # chequeo 5 de gfx_guion: el evento de la ficha con su juicio (como lo lleva pantalla_colocar → eventos_cap)
    c4 = next(c for c in ent["caps"] if c["cap"] == "ch04")
    si = s7["ficha"]["sentence_idx"]
    ors = [s["texto"] for s in c4["oraciones"]]
    voz_video = [s["texto"] for c in ent["caps"] for s in c["oraciones"]]

    def chequeo5(juicio):
        e = {"t": 1.0, "t_mp4": 1.0, "cap": "ch04", "beat": 7, "funcion": "", "tipo": "ficha", "queda": True,
             "etiqueta": s7["ficha"]["etiqueta"], "texto": s7["ficha"]["texto"], "dur": 3.0, "lectura_min": None,
             "escena": None, "escena_t0": None, "escena_t1": None, "voz_prev": ors[si - 1], "voz_ancla": ors[si],
             "voz_next": ors[si + 1], "pool_id": "D40", "juicio_autor": juicio}
        cap = {"cap": "ch04", "eventos": [e], "a_pantalla": [], "plan": {}, "resumen": [], "seg_dur": 10.0}
        out = gg.chequeos([cap], title_dur=3.0, fps=30, mezcla=None, voz_video=voz_video)
        return next(r for r in out if r["nombre"] == "cifra que contradice la voz")
    assert chequeo5(None)["ok"] is False                       # sin juicio: ✗ como en F38b
    assert chequeo5(s7["ficha"]["juicio_autor"])["ok"] is True


@hay_vajont
def test_a2_contradice_nueva_tras_el_reintento_corta(ent, papel):
    v = mp.validar(papel, ent, {})                             # confirmados sin la pregunta: la coincidencia corta
    d = next(d for d in v["descartados"] if d.get("pool_id") == "D40" and d.get("quien") == "validación")
    assert d["regla"] == "contradice"


def test_a2_contradicciones_estructura_y_frases():
    voz = ["La cota autorizada fue de setecientos quince."]
    cs = pf.contradicciones_de("COTA MÁXIMA 720 m", voz, cerca=voz)
    assert [(c["bloque"], c["voz"], c["token"], c["oracion"]) for c in cs] == [(720, 715, "715", voz[0])]
    assert pf.contradicciones("COTA MÁXIMA 720 m", voz, cerca=voz) == [pf.frase_contradiccion(cs[0])]
    assert pf.contradicciones("COTA MÁXIMA 720 m", voz, cerca=voz, juicio={"contradice": ["715"]}) == []
    assert pf.contradicciones("COTA MÁXIMA 720 m", voz, cerca=voz, juicio={"no_dicho": ["715"]})   # otra regla
