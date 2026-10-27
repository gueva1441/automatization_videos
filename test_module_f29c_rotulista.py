"""
test_module_f29c_rotulista.py — F29c §A.7: el rotulista por beat, sin red. Fixtures de Vajont ch06 (F29b) y las 4 crudas
de ch01 que no parseaban (lab/hyperframes/f29c/fixtures/): prompt literal del handoff F29c, 1 texto por beat y 0 en el
pico, arranque en la palabra, fin en la oración / la siguiente / el corte de escena, «sin tiempo de lectura», no dicho
por oraciones vecinas, spoiler por oración posterior, coherencia de cifras (720 vs 700/715), la ficha (= title card sin
#tc-dim), la ficha no convive con reloj ni title card, el primer JSON válido y D245 pasa el crítico.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from script_engine import gfx_rotulista as gro

ROOT = Path(__file__).resolve().parent
FIX_B = ROOT / "lab" / "hyperframes" / "f29b" / "fixtures"
FIX_C = ROOT / "lab" / "hyperframes" / "f29c" / "fixtures"
HANDOFF = ROOT / "lab" / "hyperframes" / "f29c" / "HANDOFF_F29c_rotulista_por_beat.md"


class Sc:
    def __init__(self, i: int, a: float, b: float):
        self.idx, self.start, self.end, self.quiet_side = i, a, b, "right"


def _ch06() -> tuple[dict, list[dict]]:
    f = json.loads((FIX_B / "rotulista_ch06_entrada.json").read_text(encoding="utf-8"))
    return f["entrada"], f["words"]


def _w(texto: str, t0: float, paso: float = 0.4) -> list[dict]:
    return [{"word": w, "start": round(t0 + k * paso, 3), "end": round(t0 + k * paso + paso * 0.8, 3)}
            for k, w in enumerate(texto.split())]


def _ent(oraciones: list[tuple[float, str]], items: list[dict], beats: list[dict] | None = None,
         pico: dict | None = None, voz_video: list[str] | None = None) -> tuple[dict, list]:
    words = []
    for t0, txt in oraciones:
        words += _w(txt, t0)
    beats = beats or [{"n": 1, "funcion": "escalada", "t0": 0.0, "t1": 999.0, "cierre": "", "dato_central": "",
                       "datos_apoyo": []}]
    its = [{"a_pantalla": False, "por_que": "", "beats": [beats[0]["n"]], "kind": "datos", "fuente": "Fuente X, 2013",
            "autor": "", **x, "tipo": x["id"][0]} for x in items]
    ent = {"cap": 3, "titulo": "t", "oraciones": gro.oraciones(words), "beats": beats, "items": its,
           "ya_mostrado": [], "pico": pico, "voz_video": voz_video or []}
    for s in ent["oraciones"]:
        s["beat"] = gro.beat_de_oracion(s, beats)
    return ent, words


def _b(si: int, tipo: str, texto: str, pid: str, et: str | None = None, wi: int = 0, rank: int = 1,
       aporta: str = "algo concreto") -> dict:
    return {"sentence_idx": si, "word_idx": wi, "beat": 0, "rank": rank, "tipo": tipo, "etiqueta": et, "texto": texto,
            "pool_id": pid, "aporta": aporta}


# ═══════════════ prompt literal (A.5) ═══════════════


# ═══════════════ A.1: 1 por beat, 0 en el pico ═══════════════


# ═══════════════ A.2: arranque y fin ═══════════════


# ═══════════════ A.3: no dicho por vecinas, spoiler por posterior ═══════════════


# ═══════════════ A.4: coherencia de cifras ═══════════════


# ═══════════════ A.5: la ficha ═══════════════

def test_ficha_es_el_title_card_con_kicker_y_titulo_y_sin_tc_dim(tmp_path):
    from script_engine.gfx_project import ficha_html, ficha_medida, write_project
    html_, init, js = ficha_html("fc0", {"text": "Giorgio Dal Piaz", "kicker": "geólogo"}, 12.0, 3.0, 2560)
    assert 'id="fc0-kicker" class="tc-kicker">GEÓLOGO<' in html_ and "Giorgio Dal Piaz" in html_
    assert "tc-dim" not in html_ and 'class="clip tc-box ficha" data-start="12.000" data-duration="3.000"' in html_
    assert "#fc0-title span" in init[0] and '"#fc0", { opacity: 0, duration: 0.4' in js[0]
    assert ficha_medida("ANCHO DE LA FISURA", "Más de 1 metro") == {"kicker": 1, "title": 1}
    assert ficha_medida("x", "Aprobada con solo 13 de 34 representantes presentes en la sala")["title"] == 2
    # el title card sigue con su #tc-dim
    from script_engine.gfx_project import GfxScene
    (tmp_path / "public").mkdir()
    (tmp_path / "public" / "base.mp4").write_bytes(b"")
    plan = {"title_card": {"kicker": "CAPÍTULO 3", "title": "La fisura"},
            "callouts": [{"text": "Más de 1 metro", "kicker": "Ancho de la fisura", "ficha": True, "start": 8.0,
                          "duration": 3.0, "side": "left"}]}
    sc = [GfxScene(idx=0, start=0.0, end=20.0, rank="R2")]
    write_project(plan, sc, tmp_path, duration=20.0, width=2560, height=1440, fps=30, grade=False)
    idx = (tmp_path / "index.html").read_text(encoding="utf-8")
    assert idx.count('id="tc-dim"') == 1 and 'id="fc0"' in idx and "ANCHO DE LA FISURA" in idx


def test_ficha_no_convive_con_reloj_ni_con_title_card():
    ent, words = _ent([(0, "Arranca el capítulo con su título."), (5, "La comisión aprobó el proyecto ese invierno."),
                       (12, "Después la obra siguió por meses en la garganta."), (20, "Nadie protestó.")],
                      [{"id": "T10", "texto": "x"}])
    scenes = [Sc(0, 0.0, 9.0), Sc(1, 9.0, 18.0), Sc(2, 18.0, 30.0)]
    plan = {"title_card": {"kicker": "CAPÍTULO 3", "title": "t"},
            "callouts": [{"text": "Aprobada con 13", "kicker": "Acta", "ficha": True, "start": 5.5, "duration": 2.0,
                          "t1": 7.5, "pool_id": "T10", "tipo_rotulista": "hecho", "rotulista": True}]}
    filas = gro.escena_final(plan, scenes, ent, [])
    c = plan["callouts"][0]
    # DECISIONES 17:58 (F36 C): nunca al mismo tiempo; la ficha (5.5–7.5 s) no toca el title card (0–3 s): se queda
    assert c["start"] == 5.5 and not [f for f in filas if f.get("accion") == "movido"]
    plan1 = {"title_card": {"kicker": "CAPÍTULO 3", "title": "t"},
             "callouts": [{"text": "Aprobada con 13", "kicker": "Acta", "ficha": True, "start": 2.0, "duration": 2.0,
                           "t1": 4.0, "pool_id": "T10", "tipo_rotulista": "hecho", "rotulista": True}]}
    filas1 = gro.escena_final(plan1, scenes, ent, [])
    c1 = plan1["callouts"][0]                                                       # se solapa con el title card
    assert c1["start"] == 9.0 and any(f["accion"] == "movido" and "title card" in f["motivo"] for f in filas1)
    plan2 = {"time_ticker": {"day": "9", "month": "OCT", "start": 9.5, "duration": 12.0, "changes": []},
             "callouts": [{"text": "Aprobada con 13", "kicker": "Acta", "ficha": True, "start": 12.0, "duration": 2.0,
                           "pool_id": "T10", "tipo_rotulista": "hecho", "rotulista": True}]}
    filas2 = gro.escena_final(plan2, scenes, ent, [])
    assert plan2["callouts"] == [] and plan2["time_ticker"]                           # el reloj cubre el resto del beat
    assert any(f["regla"] == "zona" and f["accion"] == "fuera" and "reloj" in f["motivo"] for f in filas2)


def test_reloj_no_va_encima_de_un_recorte_y_arranca_en_la_escena_siguiente_del_beat():
    ent, words = _ent([(0, "Uno dos tres."), (10, "Cuatro cinco seis.")], [{"id": "D1", "texto": "x"}])
    scenes = [Sc(0, 0.0, 9.0), Sc(1, 9.0, 18.0), Sc(2, 18.0, 30.0)]
    plan = {"archive_clippings": [{"headline": "h", "start": 2.0, "duration": 3.0, "rotulista": True, "pool_id": "D1"}],
            "time_ticker": {"day": "9", "month": "OCT", "start": 3.0, "duration": 12.0, "changes": []}}
    gro.escena_final(plan, scenes, ent, [])
    assert plan["time_ticker"]["start"] == 9.0 and plan["time_ticker"]["duration"] == 6.0


# ═══════════════ A.6.1: el primer JSON válido ═══════════════


# ═══════════════ A.6.2: D245 pasa el crítico ═══════════════

