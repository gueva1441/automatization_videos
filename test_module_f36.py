"""
test_module_f36.py — F36 (estructura de la capa de texto), sin red. Cada parte agrega sus tests con el caso real.
"""
from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path
from types import SimpleNamespace as NS

import pytest

from script_engine import pantalla_filtros as pf, pantalla_colocar as pc, voz_datos as vd, voz_utils as vu

ROOT = Path(__file__).resolve().parent
F34 = "1973ba1"                      # el cierre de F34: la base de F36


def _f34(path: str) -> str:
    r = subprocess.run(["git", "show", f"{F34}:{path}"], cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        pytest.skip(f"sin git o sin {F34}")
    return r.stdout


def _cuerpo(src: str, fn: str) -> str:
    t = ast.parse(src)
    n = next(x for x in t.body if isinstance(x, ast.FunctionDef) and x.name == fn)
    return ast.get_source_segment(src, n) or ""


# ═══════════════ A: partir el rotulista sin cambiar comportamiento ═══════════════


def test_a_cada_modulo_tiene_lo_suyo():
    """F37 §B.5: cada módulo tiene lo suyo y la entrada ya no es fachada (no re-exporta lo de los otros)."""
    from script_engine import clima, pantalla_entrada
    assert callable(pf.validar_papel) and pf.ORDEN and callable(pc.colocar) and callable(pc.repartir)
    assert callable(clima.sellos_del_papel) and callable(vd.reloj_de_voz) and callable(vu.numeros)
    for n in ("validar_papel", "colocar", "repartir", "sellos_del_papel", "reloj_de_voz", "numeros", "escena_final"):
        assert not hasattr(pantalla_entrada, n), n


def test_a_guard_mapa_avisa_tambien_por_los_modulos_nuevos():
    import importlib.util
    spec = importlib.util.spec_from_file_location("gm", ROOT / ".claude" / "hooks" / "guard_mapa.py")
    gm = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gm)
    for f in ("pantalla_entrada", "pantalla_filtros", "pantalla_colocar", "clima", "voz_datos", "voz_utils"):
        assert "guard_mapa" in gm.aviso([f"script_engine/{f}.py"])
    assert gm.aviso(["script_engine/clima.py", "lab/MAPA_MODULOS.json"]) is None


# ═══════════════ B: los bugs, con el caso real de cada uno ═══════════════

class Sc:
    def __init__(self, i: int, a: float, b: float):
        self.idx, self.start, self.end, self.quiet_side = i, a, b, "right"


def _w(texto: str, t0: float, paso: float = 0.4) -> list[dict]:
    return [{"word": w, "start": round(t0 + k * paso, 3), "end": round(t0 + k * paso + paso * 0.8, 3)}
            for k, w in enumerate(texto.split())]


def _ent(oraciones: list[tuple[float, str]], items: list[dict], beats: list[dict] | None = None,
         voz_video: list[str] | None = None) -> tuple[dict, list[dict]]:
    words = []
    for t0, txt in oraciones:
        words += _w(txt, t0)
    beats = beats or [{"n": 1, "funcion": "escalada", "t0": 0.0, "t1": 999.0, "cierre": "", "dato_central": "",
                       "datos_apoyo": []}]
    its = [{"a_pantalla": False, "por_que": "", "beats": [beats[0]["n"]], "kind": "datos", "fuente": "Fuente X, 2013",
            "autor": "", **x, "tipo": x["id"][0]} for x in items]
    ent = {"cap": 2, "titulo": "t", "oraciones": vu.oraciones(words), "beats": beats, "items": its, "ya_mostrado": [],
           "pico": None, "voz_video": voz_video or [], "voz_antes": ""}
    for s in ent["oraciones"]:
        s["beat"] = vu.beat_de_oracion(s, beats)
    return ent, words


def _bl(si: int, tipo: str, texto: str, pid: str, et: str | None = None, wi: int = 0, **kw) -> dict:
    return {"sentence_idx": si, "word_idx": wi, "beat": 0, "rank": 1, "tipo": tipo, "etiqueta": et, "texto": texto,
            "pool_id": pid, "aporta": "algo concreto", **kw}


def _moods() -> dict:
    return {"agua": {"layer": "agua", "triggers": {"agua": 3}},
            "muerte": {"layer": "muerte", "triggers": {"deslizamiento": 3, "montaña": 2}}}


def test_b2_al_sello_de_clima_el_critico_solo_le_pregunta_si_estorba(tmp_path, monkeypatch):
    """ch02 CALMA (162.3): el crítico lo sacaba por «el tinte de muerte contradice la escena de vida» (forma, F31b).
    Ahora solo cuenta la (3) «¿estorba?», con el pedido del crítico del rotulista (sin prompt nuevo)."""
    from script_engine import gfx_critic as gc
    monkeypatch.setattr(gc, "frame_at", lambda base, t, dst, width=1280: dst)
    em = {"word": "CALMA", "start": 32.3, "duration": 2.5, "category": "muerte", "side": "right", "sentence_idx": 0}
    words = _w("Longarone era un pueblo con escuela y cine.", 30.0)
    vida = {"habla_de_eso": False, "motivo_1": "el tinte de muerte contradice la escena de vida",
            "dice_algo_nuevo": False, "motivo_2": "repite lo que ya se ve", "estorba": False, "motivo_3": "no tapa nada"}
    pedidos: list[str] = []
    row = gc.estorba("sello", em, base=tmp_path / "base.mp4", words=words, time_offset=0.0, work_dir=tmp_path,
                     cap="ch02", log=[], call=lambda img, prompt: pedidos.append(prompt) or vida)
    assert row["pasa"] and row["veredicto"] == "no estorba" and row["pregunta"] == "¿estorba?"
    assert pedidos == [gc.build_prompt_rot(gc.describe("sello", em), row["voz"], "", "")]
    row2 = gc.estorba("sello", {**em, "start": 40.0}, base=tmp_path / "base.mp4", words=words, time_offset=0.0,
                      work_dir=tmp_path, cap="ch02", log=[],
                      call=lambda img, prompt: {**vida, "estorba": True, "motivo_3": "tapa el rostro"})
    assert not row2["pasa"] and row2["motivo"] == "tapa el rostro"
    row3 = gc.estorba("sello", em, base=tmp_path / "base.mp4", words=words, time_offset=0.0, work_dir=tmp_path,
                      cap="ch02", log=[], call=lambda img, prompt: (_ for _ in ()).throw(AssertionError("caché")))
    assert row3["pasa"]                                                               # de la caché


def test_b4_reloj_termina_antes_del_corte():
    """Reloj ch07 «20 FEB 1968» (84.7 + 12 contra el corte de 93.77): duración = corte − inicio − 1 cuadro. F36 §D: el
    agua se borró (catálogo 18:17)."""
    plan = {"time_ticker": {"start": 84.7, "duration": 12.0}}
    pc.hasta_el_corte(plan, [Sc(7, 84.5, 93.767), Sc(8, 93.767, 120.0)], 30, [])
    assert plan["time_ticker"]["duration"] == round(93.767 - 84.7 - 1 / 30, 3)
    plan = {"time_ticker": {"start": 10.0, "duration": 2.0}}
    pc.hasta_el_corte(plan, [Sc(0, 0.0, 30.0)], 30, [])
    assert plan["time_ticker"]["duration"] == 2.0                                        # cabe: no se toca


def test_b5_cota_715_no_contradice_niveles_de_otro_momento():
    """ch04: «COTA AUTORIZADA 715 m» marcaba ✗ contra 650 m (1960) y 700 m («no pasar de los setecientos metros sobre
    el nivel del mar», la oración vecina). Una cota solo contradice a otra cota en la oración ancla o la vecina."""
    voz = ["El cuatro de noviembre de mil novecientos sesenta el embalse estaba a seiscientos cincuenta metros sobre "
           "el nivel del mar.",
           "La recomendación que salió de ahí fue no pasar de los setecientos metros sobre el nivel del mar.",
           "La cota autorizada fue de setecientos quince.",
           "En noviembre de mil novecientos sesenta y dos, la ladera ya se desplazaba más de un centímetro y medio por "
           "día."]
    assert pf.contradicciones("COTA AUTORIZADA 715 m", voz)                # sin vecindad (como antes): ✗
    assert pf.contradicciones("COTA AUTORIZADA 715 m", voz, cerca=voz[1:4]) == []
    assert pf.contradicciones("COTA AUTORIZADA 720 m", voz, cerca=voz[1:4])            # otra cota al lado: ✗
    assert pf.contradicciones("MUERTOS 2.000 personas", ["Murieron mil novecientas diez personas."],
                               cerca=[]) != []                               # los muertos, contra todo el video


def test_b9_la_tarjeta_reemplaza_la_intro(tmp_path):
    """La tarjeta «9 OCT 1963 · 22:39» estaba en el plan pero el mp4 arrancaba con 2.5 s de primer cuadro congelado.
    Con tarjeta: title_dur (3 s) de negro con la tarjeta; sin tarjeta, los 2.5 s de siempre."""
    import fase2b
    from gfx_config import gfx_rules
    p1 = NS(chapter_id="ch01", is_first=True)
    tj = {"texto": "9 OCT 1963 · 22:39", "fecha": "1963-10-09", "hora": "22:39", "pool_id": "T57"}
    assert fase2b._intro_de([p1], tmp_path, True) == (fase2b.INITIAL_SILENCE_SEC, None)        # sin plan
    (tmp_path / "gfx_plan_ch01.resolved.json").write_text(json.dumps({"plan": {"tarjeta_inicial": tj}}),
                                                          encoding="utf-8")
    assert fase2b._intro_de([p1], tmp_path, True) == (gfx_rules.title_dur, tj) and gfx_rules.title_dur == 3.0
    assert fase2b._intro_de([p1], tmp_path, False) == (2.5, None)                             # sin --gfx
    (tmp_path / "gfx_plan_ch01.resolved.json").write_text(json.dumps({"plan": {"tarjeta_inicial": {
        "falta": True, "motivo": "x"}}}), encoding="utf-8")
    assert fase2b._intro_de([p1], tmp_path, True) == (2.5, None)                              # tarjeta incompleta
    g, _ = fase2b._grafo_musica(Path("v.wav"), Path("m.wav"), {}, None, 3.0)
    assert "adelay=3000|3000" in g
    out = fase2b._pad_tarjeta(tj, tmp_path, tmp_path / "pad.ts", 3.0, 30, 2560, 1440)
    r = subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries",
                        "stream=width,height,nb_read_frames", "-of", "csv=p=0", str(out)], capture_output=True,
                       text=True)
    assert r.stdout.split()[0] == "2560,1440,90"                         # mpegts: también la línea del programa
    assert (tmp_path / "_tarjeta.txt").read_text(encoding="utf-8") == "9 OCT 1963 · 22:39"


