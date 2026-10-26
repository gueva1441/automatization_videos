"""
test_module_f32.py — F32: el guion de pantalla, sin red. §A.6: guion de un cap de fixture con todos los tipos, beat vacío
marcado, cap sin texto marcado, silencio contra la pausa más larga del guion, inicio de voz con rampa (v3b) y sin rampa
(v5 ch01, lab/hyperframes/f32/fixtures/), `--plan-edit` que reemplaza un texto y el guion lo refleja.
"""
from __future__ import annotations

import json
from pathlib import Path

from script_engine import gfx_guion as gg
from script_engine import gfx_rotulista as gro
from script_engine.gfx_peak import sentences

ROOT = Path(__file__).resolve().parent
FIX = ROOT / "lab" / "hyperframes" / "f32" / "fixtures"
UMBRAL = -30.46            # duck_threshold 0.03 del sync map de Vajont, en dB


class Sc:
    def __init__(self, i: int, a: float, b: float):
        self.idx, self.start, self.end, self.quiet_side = i, a, b, "right"


def _w(texto: str, t0: float, paso: float = 0.4) -> list[dict]:
    return [{"word": w, "start": round(t0 + k * paso, 3), "end": round(t0 + k * paso + paso * 0.8, 3)}
            for k, w in enumerate(texto.split())]


ORACIONES = [(0.2, "La presa se levantó en el valle."), (4.0, "Murieron cientos de personas aquella noche."),
             (7.0, "El agua subió por encima del dique."), (10.5, "Nadie había leído el informe de Padua."),
             (17.5, "El juez dictó la sentencia en mil novecientos setenta y uno.")]


def _cap(plan: dict, *, beats: list[dict] | None = None, first: bool = False, pre: float = 3.0) -> dict:
    raw = []
    for t0, txt in ORACIONES:
        raw += _w(txt, t0)
    words = [{**w, "start": w["start"], "end": w["end"]} for w in raw]
    beats = beats or [{"n": 1, "funcion": "planteo", "t0": pre + 0.2, "t1": pre + 9.72},
                      {"n": 2, "funcion": "pico", "t0": pre + 10.5, "t1": pre + 13.22},
                      {"n": 3, "funcion": "cierre", "t0": pre + 17.5, "t1": pre + 24.0}]
    escenas = [{"idx": 0, "start": 0.0, "end": pre + 4.0}, {"idx": 1, "start": pre + 4.0, "end": pre + 7.0},
               {"idx": 2, "start": pre + 7.0, "end": pre + 10.5}, {"idx": 3, "start": pre + 10.5, "end": pre + 17.5},
               {"idx": 4, "start": pre + 17.5, "end": pre + 30.0}]
    return {"cap": "ch03", "n": 3, "titulo": "La ola", "plan": plan, "rejected": [], "escenas": escenas, "beats": beats,
            "sents": sentences(words, pre), "raw": raw, "offset": 100.0, "seg_dur": pre + 30.0, "pre_pad": pre,
            "pre_roll": pre, "primera_palabra": raw[0]["start"], "is_first": first, "audio": None, "pool_items": {},
            "tts_text": "La presa se levantó en el valle. [long pause] Murieron casi dos mil personas aquella noche. "
                        "El agua subió por encima del dique. Nadie había leído el informe de Padua. El juez dictó la "
                        "sentencia en mil novecientos setenta y uno.", "a_pantalla": ["D1", "D9"]}


def _plan_todo(pre: float = 3.0) -> dict:
    return {
        "title_card": {"kicker": "CAPÍTULO 3", "title": "La ola"},
        "callouts": [{"text": "1.910 personas", "kicker": "Muertos", "ficha": True, "start": pre + 4.4, "duration": 2.5,
                      "pool_id": "D1", "rotulista": True, "sentence_idx": 1, "tipo_rotulista": "cifra", "aporta": "el total",
                      "a_pantalla": True},
                     {"text": "Alberico Biadene", "kicker": "Director", "ficha": True, "start": pre + 10.6, "duration": 2.5,
                      "pool_id": "T1", "rotulista": True, "sentence_idx": 3, "tipo_rotulista": "persona", "aporta": "el nombre"}],
        "archive_clippings": [{"kicker": "Informe de Padua, 1962", "headline": "No superar los 700 metros",
                               "start": pre + 14.0, "duration": 3.0, "pool_id": "D2", "rotulista": True, "sentence_idx": 3}],
        "quote_card": {"text": "Era una montaña que caminaba", "author": "Tina Merlin", "start": pre + 17.6,
                       "duration": 3.0, "pool_id": "Q1", "rotulista": True, "sentence_idx": 4},
        "evidence_zoom": {"scene_idx": 2, "start": pre + 7.2, "detail": "la fisura", "box": [0.1, 0.1, 0.2, 0.2],
                          "rotulista": True, "pool_id": "D3", "sentence_idx": 2},
        "water_level": {"value_text": "715", "unit": "metros", "start": pre + 8.5, "duration": 1.9, "height": 0.85,
                        "pool_id": "D4", "rotulista": True},
        "count_up": {"value_text": "1.910", "unit": "personas", "start": pre + 12.0, "duration": 3.7, "pool_id": "D5"},
        "emphasis": [{"word": "agua", "start": pre + 7.5, "duration": 2.5, "category": "agua", "stamp": True}],
        "time_ticker": {"start": pre + 0.5, "duration": 3.0, "day": "9", "month": "OCT", "tail": "1963"},
        "chapter_question": {"text": "¿Quién firmó?", "start": pre + 30.0, "duration": 3.0, "pause": 3.0},
        "black_hold": {"start": pre + 29.0, "duration": 1.0},
        "transitions": {"1": {"kind": "cut", "why": "corte"}, "2": {"kind": "zoom_punch", "frames": 12, "why": "pico"},
                        "4": {"kind": "dip", "frames": 10, "why": "cierre"}},
        "rotulista": {"filas": [{"pool_id": "D9", "tipo": "cifra", "etiqueta": "Técnicos", "texto": "20 técnicos",
                                 "sentence_idx": 1, "regla": "cantidad", "motivo": "un texto por beat", "accion": "fuera"}],
                      "motivo_faltan": {"D9": "cantidad: un texto por beat"}},
        "realizador": {"filas": [{"bloque": "emphasis", "texto": "valle", "t": pre + 1.0, "accion": "fuera",
                                  "motivo": "sello por léxico"}]},
    }


def _guion(caps: list[dict]) -> dict:
    return gg.armar(caps, title_dur=3.0, dip_frames=10, fps=30, intro=2.5, mezcla=None, voz_video=[], topic="fix")


# ═══════════════ A.1–A.2: un cap con todos los tipos ═══════════════

def test_guion_de_un_cap_con_todos_los_tipos():
    g = _guion([_cap(_plan_todo())])
    ev = g["caps"][0]["eventos"]
    tipos = {e["tipo"] for e in ev}
    for t in ("costura", "title card", "ficha", "persona", "recorte", "cita", "lupa", "nivel de agua", "contador",
              "sello", "reloj", "pregunta de cierre", "transición", "punch", "silencio de voz"):
        assert t in tipos, t
    f = next(e for e in ev if e["tipo"] == "ficha" and e["queda"])
    assert f["t_mp4"] == 107.4 and f["beat"] == 1 and f["escena"] == 1 and f["lectura_min"] == round(21 / 15, 2)
    assert f["voz_ancla"].startswith("Murieron") and f["voz_prev"].startswith("La presa")
    corte = next(e for e in ev if not e["queda"] and e.get("pool_id") == "D9")
    assert "cortó rotulista (cantidad)" in corte["filtro"]
    md = gg.a_markdown(g)
    assert "01:47.4 · ch03 · beat 1 (planteo) · ficha · «Muertos | 1.910 personas» · dura 2.5 s (lectura mínima 1.4 s)" in md
    assert "✂ " in md and "### ✗ a_pantalla" in md and "- ✗ ch03 D9: cortó rotulista (cantidad): un texto por beat" in md
    pu = next(e for e in ev if e["tipo"] == "punch")
    assert pu["razon"] == "pico" and (pu["saliente"], pu["entrante"]) == (1, 2)


def test_beat_vacio_marcado():
    plan = {"title_card": {"kicker": "CAPÍTULO 3", "title": "La ola"},
            "callouts": [{"text": "1.910 personas", "kicker": "Muertos", "ficha": True, "start": 7.4, "duration": 3.4,
                          "pool_id": "D1", "rotulista": True, "sentence_idx": 1, "tipo_rotulista": "cifra"}]}
    g = _guion([_cap(plan)])
    res = {b["n"]: b for b in g["caps"][0]["resumen"]}
    assert not res[1]["vacio"] and res[2]["vacio"] and res[3]["vacio"]
    assert "| 2 ⚠ BEAT VACÍO | pico |" in gg.a_markdown(g)


def test_cap_sin_texto_marcado():
    plan = {"title_card": {"kicker": "CAPÍTULO 3", "title": "La ola"},
            "emphasis": [{"word": "agua", "start": 10.5, "duration": 2.5, "category": "agua", "stamp": True}]}
    g = _guion([_cap(plan)])
    assert g["caps"][0]["sin_texto"] and "**⚠ CAP SIN TEXTO**" in gg.a_markdown(g)
    g2 = _guion([_cap(_plan_todo())])
    assert not g2["caps"][0]["sin_texto"]


# ═══════════════ A.1: silencio de voz contra la pausa más larga del guion ═══════════════

def test_silencio_contra_la_pausa_mas_larga_del_guion():
    c = _cap({"title_card": None})
    pm = gg.pausa_max_guion(c["raw"], c["tts_text"])
    # la marca [long pause] cae después de «valle.» (fin 2.92, siguiente 4.0: 1.08 s) → esa es la pausa del guion
    assert pm == {"s": 1.08, "palabra": "valle.", "como": "marca de pausa del guion"}
    sil = gg.silencios(c["raw"], pm["s"], 3.0)
    # el único hueco mayor: «Padua.» (13.22) → «El» (17.5) = 4.28 s, en el tiempo del cap (pre-roll 3 s)
    assert [(s["antes"], s["dur"], s["t"]) for s in sil] == [("Padua.", 4.28, 16.22)]
    assert gg.pausa_max_guion(c["raw"], c["tts_text"].replace("[long pause]", ""))["como"].startswith("entre oraciones")


# ═══════════════ A.3: inicio de voz (fixtures con el audio de v5 y de v3b) ═══════════════

def test_inicio_de_voz_v5_ch01_sin_rampa():
    """v5 ch01: la voz entra a tiempo (el mp3 corrido 2.5 + 3.0 s exactos), pero la mezcla salta de silencio a −18 dB:
    los 100 ms previos están en −34.7 dB (música + aire), bajo la voz presente. El handoff esperaba «5.55»: es el 0.05
    del golpe del title card que en v3b caía junto con la voz (la «rampa» de v3b); la primera palabra del mp3 está en
    0.12 → 5.62. Ver F32_REPORT, B.1."""
    r = gg.inicio_de_voz(FIX / "v5_mezcla_0a10s.wav", FIX / "ch01_voz_0a3s.wav", 2.5 + 3.0 + 0.12, 0.12,
                         umbral_db=UMBRAL, fps=30)
    assert r["medido"] == 5.62 and r["a_tiempo"] and abs(r["t_18db"] - 5.65) <= 0.01
    assert not r["rampa"] and not r["ok"] and r["previo_db"] < UMBRAL
    ln = gg.linea_inicio("ch01", r)
    assert ln.startswith("✗ ch01 · voz esperada 5.62 s · medida 5.62 s · llega a −18 dB en 5.6") and "sin rampa" in ln


def test_inicio_de_voz_v3b_con_rampa():
    r = gg.inicio_de_voz(FIX / "v3b_mezcla_0a6s.wav", FIX / "ch01_voz_0a3s.wav", 2.5 + 0.12, 0.12,
                         umbral_db=UMBRAL, fps=30)
    assert r["ok"] and r["rampa"] and r["medido"] == 2.62 and r["previo_db"] > UMBRAL
    assert gg.linea_inicio("ch01", r).startswith("✓ ch01")


def test_inicio_de_voz_corrido_falla_por_tiempo():
    r = gg.inicio_de_voz(FIX / "v5_mezcla_0a10s.wav", FIX / "ch01_voz_0a3s.wav", 2.5 + 3.0 + 0.12 + 0.2, 0.12,
                         umbral_db=UMBRAL, fps=30)
    assert r["medido"] == 5.62 and not r["a_tiempo"] and not r["ok"]


# ═══════════════ A.5: --plan-edit reemplaza un texto y el guion lo refleja ═══════════════

def _ent_simple() -> tuple[dict, list[dict]]:
    words = []
    for t0, txt in ORACIONES:
        words += _w(txt, t0)
    beats = [{"n": 1, "funcion": "escalada", "t0": 0.0, "t1": 999.0, "cierre": "", "dato_central": "", "datos_apoyo": []}]
    its = [{"id": "D1", "a_pantalla": False, "por_que": "", "beats": [1], "kind": "datos", "fuente": "Informe, 1963",
            "autor": "", "tipo": "D", "texto": "En el desastre murieron 1.910 personas de Longarone."}]
    ent = {"cap": 3, "titulo": "t", "oraciones": gro.oraciones(words), "beats": beats, "items": its, "ya_mostrado": [],
           "pico": None, "voz_video": []}
    for s in ent["oraciones"]:
        s["beat"] = gro.beat_de_oracion(s, beats)
    return ent, words


def test_plan_edit_reemplaza_un_texto_y_el_guion_lo_refleja(tmp_path):
    ent, words = _ent_simple()
    res = {"final": {"bloques": [{"sentence_idx": 1, "word_idx": 0, "beat": 1, "rank": 1, "tipo": "cifra",
                                  "etiqueta": "Muertos", "texto": "1.910 personas", "pool_id": "D1", "aporta": "el total"}]}}
    scenes = [Sc(0, 0.0, 30.0)]
    gro.guardar_ediciones(tmp_path, [{"cap": "ch03", "pool_id": "D1", "etiqueta": "Muertos en Longarone"}])
    edits = gro.ediciones_de(tmp_path, "ch03")
    assert edits == [{"cap": "ch03", "pool_id": "D1", "etiqueta": "Muertos en Longarone"}]
    res2 = gro.aplicar_ediciones(res, edits, ent, [])
    assert res["final"]["bloques"][0]["etiqueta"] == "Muertos"                 # la caché del rotulista no se toca
    plan: dict = {}
    gro.colocar(plan, res2, ent, scenes=scenes, pool=None, used_before=set(), lupa_box=None, zoom_dur=2.5, log=[],
                words=words, time_offset=0.0)
    c = plan["callouts"][0]
    assert c["kicker"] == "Muertos en Longarone" and c.get("editado")
    g = _guion([{**_cap(plan, pre=0.0), "plan": plan}])
    f = next(e for e in g["caps"][0]["eventos"] if e["tipo"] == "ficha")
    assert f["etiqueta"] == "Muertos en Longarone" and "editado a mano" in f["filtro"]
    # borrar y agregar
    res3 = gro.aplicar_ediciones(res, [{"cap": "ch03", "pool_id": "D1", "borrar": True},
                                       {"cap": "ch03", "agregar": {"pool_id": "D1", "sentence_idx": 1, "word_idx": 1,
                                                                   "tipo": "cifra", "etiqueta": "Víctimas",
                                                                   "texto": "1.910 personas"}}], ent, [])
    assert [(b["etiqueta"], b["word_idx"], b.get("editado")) for b in res3["final"]["bloques"]] == [("Víctimas", 1, True)]


def test_plan_edit_escena_mueve_al_corte():
    ent, words = _ent_simple()
    res = {"final": {"bloques": [{"sentence_idx": 1, "word_idx": 0, "beat": 1, "rank": 1, "tipo": "cifra",
                                  "etiqueta": "Muertos", "texto": "1.910 personas", "pool_id": "D1", "aporta": "el total"}]}}
    scenes = [Sc(0, 0.0, 8.0), Sc(1, 8.0, 30.0)]
    plan: dict = {}
    gro.colocar(plan, res, ent, scenes=scenes, pool=None, used_before=set(), lupa_box=None, zoom_dur=2.5, log=[],
                words=words, time_offset=0.0)
    gro.mover_a_escena(plan, [{"cap": "ch03", "pool_id": "D1", "escena": 1}], scenes, ent, [])
    assert plan["callouts"][0]["start"] == 8.0 and plan["callouts"][0]["editado"]
