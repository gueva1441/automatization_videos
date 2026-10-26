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
    res = {"final": {"bloques": [{"sentence_idx": 1, "word_idx": 0, "beat": 1, "rank": 1, "tipo": "hecho",
                                  "etiqueta": "Muertos", "texto": "Murieron 1.910 personas.", "pool_id": "D1",
                                  "aporta": "el total"}]}}
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
                                                                   "tipo": "hecho", "etiqueta": "Víctimas",
                                                                   "texto": "Murieron 1.910 personas."}}], ent, [])
    assert [(b["etiqueta"], b["word_idx"], b.get("editado")) for b in res3["final"]["bloques"]] == [("Víctimas", 1, True)]


def test_plan_edit_escena_mueve_al_corte():
    ent, words = _ent_simple()
    res = {"final": {"bloques": [{"sentence_idx": 1, "word_idx": 0, "beat": 1, "rank": 1, "tipo": "hecho",
                                  "etiqueta": "Muertos", "texto": "Murieron 1.910 personas.", "pool_id": "D1",
                                  "aporta": "el total"}]}}
    scenes = [Sc(0, 0.0, 8.0), Sc(1, 8.0, 30.0)]
    plan: dict = {}
    gro.colocar(plan, res, ent, scenes=scenes, pool=None, used_before=set(), lupa_box=None, zoom_dur=2.5, log=[],
                words=words, time_offset=0.0)
    gro.mover_a_escena(plan, [{"cap": "ch03", "pool_id": "D1", "escena": 1}], scenes, ent, [])
    assert plan["callouts"][0]["start"] == 8.0 and plan["callouts"][0]["editado"]


# ═══════════════════════════════ B: arreglos (se verifican en el guion) ═══════════════════════════════

def _ent_b(oraciones: list[tuple[float, str]], items: list[dict], beats: list[dict] | None = None,
           pico: dict | None = None) -> tuple[dict, list[dict]]:
    words = []
    for t0, txt in oraciones:
        words += _w(txt, t0)
    beats = beats or [{"n": 1, "funcion": "escalada", "t0": 0.0, "t1": 999.0, "cierre": "", "dato_central": "",
                       "datos_apoyo": []}]
    its = [{"a_pantalla": False, "por_que": "", "beats": [beats[0]["n"]], "kind": "datos", "fuente": "Fuente X, 2013",
            "autor": "", **x, "tipo": x["id"][0]} for x in items]
    ent = {"cap": 3, "titulo": "t", "oraciones": gro.oraciones(words), "beats": beats, "items": its, "ya_mostrado": [],
           "pico": pico, "voz_video": []}
    for s in ent["oraciones"]:
        s["beat"] = gro.beat_de_oracion(s, beats)
    return ent, words


def _bl(si: int, tipo: str, texto: str, pid: str, et: str | None = None, wi: int = 0, rank: int = 1, **kw) -> dict:
    return {"sentence_idx": si, "word_idx": wi, "beat": 0, "rank": rank, "tipo": tipo, "etiqueta": et, "texto": texto,
            "pool_id": pid, "aporta": "algo concreto", **kw}


def test_b1_ch01_sin_pre_roll_y_la_musica_arranca_con_el_title_card(tmp_path):
    import subprocess
    import numpy as np
    import fase2b
    from types import SimpleNamespace as NS
    assert fase2b._pre_roll_de(NS(is_first=True), True) == 0.0
    assert fase2b._pre_roll_de(NS(is_first=False), True) == 3.0 and fase2b._pre_roll_de(NS(is_first=False), False) == 0.0
    assert fase2b._correr_tramos([{"nivel": "fondo", "t0": 0.0, "t1": 10.0}, {"nivel": "silencio", "t0": 4.0, "t1": 5.0}],
                                 3.0) == [{"nivel": "fondo", "t0": 0.0, "t1": 13.0}, {"nivel": "silencio", "t0": 7.0, "t1": 8.0}]
    fase2b.FFMPEG = fase2b.FFMPEG or "ffmpeg"
    tone = tmp_path / "t.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "sine=frequency=300:duration=10", str(tone)],
                   check=True)
    p = fase2b._build_music_piece_for_chapter(tone, 4.0, tmp_path / "p.wav", pre_sec=3.0)
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", str(p), "-f", "s16le", "-ac", "1", "-ar", "1000", "-"],
                       capture_output=True, check=True)
    x = np.abs(np.frombuffer(r.stdout, np.int16).astype(float))
    assert abs(len(x) / 1000 - 7.0) < 0.02 and x[100:2900].mean() > 1000          # suena durante el title card


def test_b2_la_pregunta_dura_su_lectura(tmp_path):
    from script_engine import gfx_layer
    txt = "Tres días después llegó el presidente del Consejo. La gente ya sabía qué pedirle."
    real = {"beats": [{"n": 11, "cierre": txt}]}
    resolved: dict = {}
    pausa = gfx_layer.closing_question(resolved, {"realizador": real}, tmp_path, "ch06", 167.8, [])
    q = resolved["chapter_question"]
    assert q["duration"] == round(len(txt) / 15, 3) == q["pause"] and q["start"] == 167.8
    assert resolved["black_hold"] == {"start": round(167.8 + len(txt) / 15, 3), "duration": 1.0}
    assert pausa == round(len(txt) / 15, 3) + 1.0


def test_b3_si_no_cabe_antes_del_corte_arranca_en_la_escena_siguiente():
    ent, words = _ent_b([(0.0, "En mil novecientos cuarenta y tres se aprobó el proyecto de cerrar esa garganta con una "
                               "presa y empezó la compra de terrenos en Erto."), (11.0, "La empresa era SADE.")],
                        [{"id": "D117", "texto": "El Consejo aprobó el proyecto con solo 13 de 34 representantes presentes."}])
    b = _bl(0, "cifra", "Se aprobó con solo 13 de 34 representantes presentes.", "D117", et="Consejo")
    # la palabra 7 («aprobó», 2.8 s); la escena corta en 4.0: no hay 4.7 s de lectura → arranca en el corte (4.0)
    v = gro.validar({"bloques": [{**b, "word_idx": 7}]}, ent, words, escenas=[Sc(0, 0.0, 4.0), Sc(1, 4.0, 20.0)])
    k = v["bloques"][0]
    assert k["t0"] == 4.0 and k["movido_corte"].startswith("2.80 → 4.00 s") and "escena 1" in k["movido_corte"]
    # si tampoco cabe en la escena siguiente, sin tiempo de lectura
    v2 = gro.validar({"bloques": [{**b, "word_idx": 7}]}, ent, words,
                     escenas=[Sc(0, 0.0, 4.0), Sc(1, 4.0, 6.0), Sc(2, 6.0, 20.0)])
    assert not v2["bloques"] and v2["rechazos"][0]["regla"] == "lectura"


def test_b4_a_pantalla_documento_sale_como_recorte_aunque_venga_como_cita():
    ent, words = _ent_b([(0.0, "Esa mañana el municipio de arriba escribió otra vez a la empresa."),
                         (5.0, "La empresa no contestó y el agua siguió subiendo.")],
                        [{"id": "Q50", "a_pantalla": True, "kind": "citas", "autor": "Administración del comune",
                          "fuente": "Tragedia della diga del Vajont, 2018",
                          "por_que": "Carta del municipio de Erto y Casso a SADE: documento que se lee en pantalla.",
                          "texto": "Las poblaciones de Erto y Casso están viviendo en continua aprensión."}])
    v = gro.validar({"bloques": [_bl(0, "cita", "«Las poblaciones de Erto y Casso están viviendo en continua aprensión.»",
                                     "Q50")]}, ent, words)
    k = v["bloques"][0]
    assert k["tipo"] == "documento" and k["etiqueta"] == "Tragedia della diga del Vajont, 2018"
    assert k["pantalla"].startswith("Las poblaciones") and "documento" in k["forzado"]
    assert gro.pide_documento("Acta de la sesión") and not gro.pide_documento("Cifra de liras en el fallo")
    plan: dict = {}
    gro.colocar(plan, {"final": {"bloques": [_bl(0, "cita", "Las poblaciones de Erto y Casso están viviendo en continua "
                                                       "aprensión.", "Q50")]}},
                ent, scenes=[Sc(0, 0.0, 30.0)], pool=None, used_before=set(), lupa_box=None, zoom_dur=2.5, log=[],
                words=words, time_offset=0.0)
    assert plan["archive_clippings"][0]["kicker"] == "Tragedia della diga del Vajont, 2018" and plan["quote_card"] is None


def test_b5_dos_a_pantalla_por_beat_y_a_pantalla_en_el_pico():
    beats = [{"n": 10, "funcion": "pico", "t0": 0.0, "t1": 9.0, "cierre": "", "dato_central": "", "datos_apoyo": []},
             {"n": 11, "funcion": "respiro", "t0": 9.5, "t1": 40.0, "cierre": "", "dato_central": "", "datos_apoyo": []}]
    ent, words = _ent_b([(0.0, "La ladera entera se desploma dentro del embalse."), (4.5, "Nadie lo esperaba así de rápido."),
                         (10.0, "En Longarone casi no quedaron casas en pie."), (16.0, "En el estribo izquierdo estaba el "
                                                                                       "centro de control.")],
                        [{"id": "D128", "a_pantalla": True, "beats": [10, 11], "texto": "En el desastre murieron 1.910 personas."},
                         {"id": "D192", "a_pantalla": True, "beats": [11], "texto": "En el centro de control había 20 técnicos que perecieron."},
                         {"id": "D50", "beats": [10], "texto": "El alcalde Celso murió en el desastre."}],
                        beats=beats, pico={"beat": 10})
    resp = {"bloques": [_bl(2, "cifra", "1.910 personas", "D128", et="Muertos (recuento oficial)"),
                        _bl(3, "cifra", "20 técnicos", "D192", et="Técnicos en el centro de control"),
                        _bl(0, "hecho", "Celso, alcalde, murió esa noche.", "D50", et="Alcalde")]}
    v = gro.validar(resp, ent, words)
    assert sorted(b["pool_id"] for b in v["bloques"]) == ["D128", "D192"] and not v["faltan"]
    assert any(r["pool_id"] == "D50" and "solo `a_pantalla`" in r["motivo"] for r in v["rechazos"])
    v2 = gro.validar({"bloques": [_bl(0, "cifra", "1.910 personas", "D128", et="Muertos (recuento oficial)")]}, ent, words)
    assert v2["bloques"][0]["beat"] == 10 and v2["bloques"][0]["movido"] is None       # el a_pantalla queda en el pico


def test_b6_sellos_por_tema_uno_por_beat_nunca_con_un_texto():
    from script_engine import gfx_realizador as gr
    beats = [{"n": 1, "funcion": "planteo", "t0": 0.0, "t1": 9.9, "cierre": "", "dato_central": "", "datos_apoyo": []},
             {"n": 2, "funcion": "escalada", "t0": 10.0, "t1": 30.0, "cierre": "", "dato_central": "", "datos_apoyo": []}]
    ent, words = _ent_b([(0.0, "El agua del lago subía."), (4.0, "Los cadáveres flotaban en el río."),
                         (10.0, "Hubo una avalancha de fango."), (16.0, "Murieron los técnicos del turno.")], [], beats=beats)
    moods = {"muerte": {"layer": "muerte", "triggers": {"cadáveres": 3, "murieron": 2}},
             "agua": {"layer": "agua", "triggers": {"agua": 1, "avalancha": 3, "fango": 3}}}
    scenes = [Sc(0, 0.0, 4.0), Sc(1, 4.0, 10.0), Sc(2, 10.0, 16.0), Sc(3, 16.0, 30.0)]
    plan = {"emphasis": [{"word": "lago", "start": 1.0, "duration": 2.5}],                       # del director, por léxico
            "callouts": [{"text": "20 técnicos", "start": 10.2, "duration": 3.0, "ficha": True}]}
    filas = gro.sellos_por_tema(plan, scenes, ent, words, 0.0, moods, [])
    assert [(e["word"], e["tema"]) for e in plan["emphasis"]] == [("cadáveres", "muerte"), ("Murieron", "muerte")]
    mot = {f["texto"]: f["motivo"] for f in filas}
    assert "por léxico" in mot["lago"] and "agua" not in mot                 # peso 1: no llega a sello (como el pico)
    assert "ya tiene ficha" in mot["avalancha"] and "fango" not in mot         # un candidato por oración
    plan["punch_in"] = [4.4]
    gr.finalizar({**plan, "rotulista": {"filas": []}}, {"candidatos": [], "beats": beats}, [])
    p2 = {**plan, "rotulista": {"filas": []}}
    gr.finalizar(p2, {"candidatos": [], "beats": beats}, [])
    assert [e["word"] for e in p2["emphasis"]] == ["cadáveres", "Murieron"] and p2["punch_in"] == []
    assert any(f["bloque"] == "punch_in" and f["accion"] == "fuera" for f in p2["realizador"]["filas"])


def test_b7_el_prompt_cambia_solo_por_una_linea_y_la_cifra_se_anima():
    import hashlib
    import re as _re
    md = (ROOT / "lab" / "hyperframes" / "f29c" / "HANDOFF_F29c_rotulista_por_beat.md").read_text(encoding="utf-8")
    sys_f29c = _re.search(r"\*\*SYSTEM:\*\*\s*```\n(.*?)\n```", md, _re.S).group(1)
    assert gro.ROTULISTA_SYSTEM_F29C == sys_f29c
    assert hashlib.md5((sys_f29c + "\n\n" + gro.ROTULISTA_USER).encode("utf-8")).hexdigest() == "7dafbb964d7ff71daafc65c028834017"
    nuevo, viejo = gro.ROTULISTA_SYSTEM.splitlines(), sys_f29c.splitlines()
    assert len(nuevo) == len(viejo) + 1 and [x for x in nuevo if x not in viejo] == [gro.LINEA_B7]
    assert nuevo[nuevo.index(gro.LINEA_B7) - 1].startswith("- cifra:")
    assert gro.LINEA_B7.strip() == "devolvé `unidad` (metros, personas, m³, liras u otra) y `valor` numérico"
    agua = gro.animacion_de_cifra({"tipo": "cifra", "pantalla": "715 metros", "etiqueta": "Cota autorizada del embalse",
                                   "unidad": "metros", "valor": 715}, "La SADE obtuvo autorización para llenar el embalse "
                                   "hasta 715 metros, por encima de la cota de seguridad.")
    assert agua[0] == "water_level" and agua[1]["value_text"] == "715" and agua[1]["unit"] == "metros"
    cu = gro.animacion_de_cifra({"tipo": "cifra", "pantalla": "1.910 personas", "etiqueta": "Muertos", "unidad": "personas",
                                 "valor": 1910, "lectura_s": 1.4}, "En el desastre murieron 1.910 personas.")
    assert cu[0] == "count_up" and cu[1]["value_text"] == "1.910" and cu[1]["source"] == "Muertos"
    assert gro.animacion_de_cifra({"tipo": "cifra", "pantalla": "50 millones de m³", "unidad": "m³", "valor": 50000000},
                                  "Cayeron 270 millones de m³.") is None
    assert gro.animacion_de_cifra({"tipo": "cifra", "pantalla": "260 metros", "unidad": "metros", "valor": 260,
                                   "etiqueta": "Altura de la presa"}, "La presa medía 260 metros de alto.") is None


def test_b8_ficha_un_escalon_mas_chica_con_placa(tmp_path):
    from script_engine.gfx_project import GfxScene, ficha_medida, render_css, tc_metrics, write_project
    from gfx_config import gfx_rules
    plan = {"chapter_number": 6, "title_card": {"kicker": "CAPÍTULO 6", "title": "El gran rugido"},
            "callouts": [{"text": "1.910 personas", "kicker": "Muertos", "ficha": True, "start": 5.0, "duration": 4.0,
                          "kind": "figure", "side": "left", "rotulista": True}]}
    (tmp_path / "public").mkdir()
    (tmp_path / "public" / "base.mp4").write_bytes(b"")
    write_project(plan, [GfxScene(0, 0.0, 20.0)], tmp_path, duration=20.0, width=2560, height=1440, fps=30, grade=False)
    h = (tmp_path / "index.html").read_text(encoding="utf-8")
    m = tc_metrics()
    assert '<div id="tc" class="clip tc-box" data-start="0"' in h                     # el title card, igual
    assert 'class="clip tc-box ficha" data-start="5.000"' in h
    assert f'style="top:{round(m["title_top"] + gfx_rules.question_font_px * 1.05 + 20)}px"' in h
    css = render_css(2560, 1440)
    assert f".tc-box.ficha .tc-title span {{ font-size: {gfx_rules.question_font_px}px; }}" in css
    assert ".tc-box.ficha .tc-kicker { background: rgba(10,10,10,.35); padding: 6px 26px; }" in css
    assert ficha_medida("Muertos", "1.910 personas")["title"] == 1


def test_b7_sin_unidad_en_la_respuesta_se_lee_del_texto():
    """El formato de salida del USER no nombra `unidad`/`valor` (y no se toca): sin ellos, la cifra y su unidad salen
    del texto del bloque."""
    cu = gro.animacion_de_cifra({"pantalla": "1.910 personas murieron en el desastre.", "etiqueta": "Muertos",
                                 "lectura_s": 3.5}, "En el desastre murieron 1.910 personas.")
    assert cu[0] == "count_up" and cu[1]["value_text"] == "1.910" and cu[1]["duration"] == 3.7
    assert gro.animacion_de_cifra({"pantalla": "20 técnicos perecieron", "lectura_s": 2.0}, "") is None
    largo = {"pantalla": "Montedison pagó 55.645.758.500 liras a Longarone.", "etiqueta": "Tribunal de Belluno, 1997",
             "lectura_s": 4.6}
    assert gro.animacion_de_cifra(largo, "") is None             # no se lee en lo que dura el contador: queda la ficha
