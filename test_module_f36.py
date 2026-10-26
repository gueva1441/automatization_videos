"""
test_module_f36.py — F36 (estructura de la capa de texto), sin red. Cada parte agrega sus tests con el caso real.
"""
from __future__ import annotations

import ast
import json
import re
import subprocess
from pathlib import Path
from types import SimpleNamespace as NS

import pytest

from script_engine import gfx_rotulista as gro
from script_engine import rotulista_filtros as rf

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

def test_a_orden_de_filtros_es_el_de_f34():
    """El orden en que `validar` de F34 sacaba un bloque (la secuencia de `fuera(b, "<regla>"` en su código, sin
    repetidos seguidos) y después `finalizar` (cantidad) es exactamente `ORDEN`. Se lee del código de 1973ba1."""
    src = _f34("script_engine/gfx_rotulista.py")
    reglas = re.findall(r'fuera\(b, "(\w+)"', _cuerpo(src, "validar"))
    f34 = [r for k, r in enumerate(reglas) if k == 0 or reglas[k - 1] != r]
    assert '"regla": "cantidad"' in _cuerpo(src, "finalizar")
    f34.append("cantidad")
    assert f34 == ["anclaje", "no_dicho", "forma", "candado", "no_dicho", "spoiler", "lectura", "coherencia", "cantidad"]
    assert [rf.regla(f) for f in rf.ORDEN] == f34
    assert [f.__name__ for f in rf.ORDEN][:2] == ["anclaje", "gancho_dicho"]     # el no_dicho del gancho, antes de la forma


def test_a_la_fachada_da_todos_los_nombres_de_antes():
    """gfx_rotulista sigue teniendo cada nombre de nivel de módulo que tenía en F34 (nadie cambia de import)."""
    t = ast.parse(_f34("script_engine/gfx_rotulista.py"))
    antes = set()
    for n in t.body:
        if isinstance(n, (ast.FunctionDef, ast.ClassDef)):
            antes.add(n.name)
        elif isinstance(n, ast.Assign):
            antes |= {x.id for x in n.targets if isinstance(x, ast.Name)}
        elif isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name):
            antes.add(n.target.id)
    faltan = sorted(x for x in antes if not hasattr(gro, x))
    assert not faltan, faltan


def test_a_cada_modulo_tiene_lo_suyo():
    from script_engine import clima, rotulista_colocar, rotulista_llm, voz_datos, voz_utils
    from script_engine import gfx_peak
    assert gro.validar is rf.validar and gro.finalizar is rf.finalizar is rf.cantidad
    assert gro.llamar is rotulista_llm.llamar and gro.entrada is rotulista_llm.entrada
    assert gro.colocar is rotulista_colocar.colocar and gro.escena_final is rotulista_colocar.escena_final
    assert gro.sellos_por_tema is clima.sellos_por_tema and gfx_peak.peak_word is clima.peak_word
    assert gro.reloj_de_voz is voz_datos.reloj_de_voz and gro.tarjeta_inicial is voz_datos.tarjeta_inicial
    assert gro.numeros is voz_utils.numeros and gro._EN_VUELO is rotulista_llm._EN_VUELO
    assert gro.prompt_md5() == "d90ae69a2dc8c7928bd410ead421dc6b"      # el prompt de F34 (F34_REPORT): A no lo toca
    assert rotulista_llm.PROMPT_VERSION == "f34-1"


def test_a_guard_mapa_avisa_tambien_por_los_modulos_nuevos():
    import importlib.util
    spec = importlib.util.spec_from_file_location("gm", ROOT / ".claude" / "hooks" / "guard_mapa.py")
    gm = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gm)
    for f in ("rotulista_llm", "rotulista_filtros", "rotulista_colocar", "clima", "voz_datos", "voz_utils"):
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
    ent = {"cap": 2, "titulo": "t", "oraciones": gro.oraciones(words), "beats": beats, "items": its, "ya_mostrado": [],
           "pico": None, "voz_video": voz_video or [], "voz_antes": ""}
    for s in ent["oraciones"]:
        s["beat"] = gro.beat_de_oracion(s, beats)
    return ent, words


def _bl(si: int, tipo: str, texto: str, pid: str, et: str | None = None, wi: int = 0, **kw) -> dict:
    return {"sentence_idx": si, "word_idx": wi, "beat": 0, "rank": 1, "tipo": tipo, "etiqueta": et, "texto": texto,
            "pool_id": pid, "aporta": "algo concreto", **kw}


def test_b1_el_realizador_no_borra_el_contador_del_rotulista_y_su_texto_es_el_valor():
    """D128 ch06: el contador «1.910 personas» del rotulista queda; el del director (cifra que dice la voz) sale y su
    fila dice el valor, no la palabra del ancla («Guglielmo»)."""
    from script_engine.gfx_realizador import finalizar
    real = {"candidatos": [], "beats": [{"n": 11, "funcion": "respiro", "t0": 120.0, "t1": 140.0, "intensidad": 1,
                                         "dato_central": "", "datos_apoyo": [], "cierre": ""}]}
    cu = {"start": 128.04, "duration": 4.0, "value_text": "1.910", "unit": "personas", "word": "Guglielmo",
          "rotulista": True, "pool_id": "D128"}
    plan = {"rotulista": {}, "count_up": dict(cu), "emphasis": [], "punch_in": []}
    finalizar(plan, real, [])
    assert plan["count_up"] and plan["count_up"]["value_text"] == "1.910"
    plan2 = {"rotulista": {}, "count_up": {k: v for k, v in cu.items() if k != "rotulista"}, "emphasis": [],
             "punch_in": []}
    filas = finalizar(plan2, real, [])
    assert plan2["count_up"] is None
    assert [f["texto"] for f in filas if f["bloque"] == "count_up"] == ["1.910"]


def _moods() -> dict:
    return {"agua": {"layer": "agua", "triggers": {"agua": 3}},
            "muerte": {"layer": "muerte", "triggers": {"deslizamiento": 3, "montaña": 2}}}


def test_b2_el_critico_va_antes_del_reparto_un_sello_que_estorba_no_ocupa_el_beat(monkeypatch):
    """ch02 beat 3: AVISO (175.8) caía por el crítico DESPUÉS de ocupar el beat, y AMENAZA (211.1, «deslizamiento») no
    entraba. Con el crítico antes del reparto, AVISO sale y AMENAZA ocupa el beat."""
    from script_engine import clima
    monkeypatch.setattr(clima, "vocabulario_clima", lambda: ["AVISO", "AMENAZA", "CALMA"])
    beats = [{"n": 3, "funcion": "escalada", "t0": 0.0, "t1": 30.0, "cierre": "", "dato_central": "", "datos_apoyo": []}]
    ent, words = _ent([(0.0, "El agua subió despacio en el valle."), (12.0, "Empezó el deslizamiento de la montaña.")],
                      [], beats=beats)
    scenes = [Sc(0, 0.0, 10.0), Sc(1, 10.0, 30.0)]

    def call(p: str) -> str:
        return "AVISO" if "agua subió" in p.split("Momento")[1] else "AMENAZA"
    viejo: dict = {"emphasis": []}
    gro.sellos_por_tema(viejo, scenes, ent, words, 0.0, _moods(), [], call=call)
    assert [e["word"] for e in viejo["emphasis"]] == ["AVISO"]           # sin crítico: el primero ocupa el beat
    juzgados = []

    def juez(em: dict) -> dict:
        juzgados.append(em["word"])
        return {"pasa": em["word"] != "AVISO", "motivo": "tapa un rostro", "mira": "foto sola", "t": em["start"],
                "bloque": "sello", "veredicto": "estorba" if em["word"] == "AVISO" else "no estorba"}
    plan: dict = {"emphasis": []}
    gro.sellos_por_tema(plan, scenes, ent, words, 0.0, _moods(), [], call=call, juez=juez)
    assert [e["word"] for e in plan["emphasis"]] == ["AMENAZA"] and juzgados == ["AVISO", "AMENAZA"]
    f = next(x for x in plan["sellos_tema"] if x["quien"] == "crítico")
    assert "«AVISO» estorba" in f["motivo"] and f["regla"] == "crítico"
    assert [r["pasa"] for r in plan["critico_sellos"]] == [False, True]


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


def test_b3_amenaza_no_se_repite_en_el_video_se_pide_otra_una_vez(tmp_path, monkeypatch):
    """AMENAZA ×4: si la palabra ya salió en un cap anterior, se pide otra de la lista sin las usadas (una vez); si
    tampoco hay, ese momento queda sin sello."""
    from script_engine import clima
    monkeypatch.setattr(clima, "vocabulario_clima", lambda: ["AMENAZA", "AVISO", "COLAPSO"])
    (tmp_path / "gfx_plan_ch03.resolved.json").write_text(json.dumps(
        {"plan": {"emphasis": [{"word": "AMENAZA", "clima": True}, {"word": "INMINENTE", "clima": True}]}}),
        encoding="utf-8")
    (tmp_path / "gfx_plan_ch05.resolved.json").write_text(json.dumps(
        {"plan": {"emphasis": [{"word": "PÁNICO", "clima": True}]}}), encoding="utf-8")
    assert clima.usadas_antes(tmp_path, 5) == {"AMENAZA", "INMINENTE"}           # el cap 5 y los siguientes no
    beats = [{"n": 1, "funcion": "escalada", "t0": 0.0, "t1": 30.0, "cierre": "", "dato_central": "", "datos_apoyo": []}]
    ent, words = _ent([(0.0, "El agua subió despacio en el valle.")], [], beats=beats)
    scenes = [Sc(0, 0.0, 30.0)]
    pedidos: list[str] = []

    def call(p: str) -> str:
        pedidos.append(p)
        return "AMENAZA" if "AMENAZA" in p.split("\n")[0] else "AVISO"
    plan: dict = {"emphasis": []}
    gro.sellos_por_tema(plan, scenes, ent, words, 0.0, _moods(), [], call=call, usadas_video={"AMENAZA"})
    assert [e["word"] for e in plan["emphasis"]] == ["AVISO"] and len(pedidos) == 2
    assert "AMENAZA" not in pedidos[1].split("\n")[0]                                # la lista sin la usada
    plan2: dict = {"emphasis": []}
    gro.sellos_por_tema(plan2, scenes, ent, words, 0.0, _moods(), [], call=lambda p: "AMENAZA",
                        usadas_video={"AMENAZA"})
    assert plan2["emphasis"] == [] and "ya salió en el video" in plan2["sellos_tema"][0]["motivo"]


def test_b4_agua_y_reloj_terminan_antes_del_corte():
    """Agua ch04 «COTA AUTORIZADA 715 m» (84.06 + 4.5 cruzaba el corte de 88.03 por 0.53 s) y reloj ch07 «20 FEB 1968»
    (84.7 + 12 contra el corte de 93.77): duración = corte − inicio − 1 cuadro."""
    plan = {"water_level": {"start": 84.06, "duration": 4.5}, "time_ticker": {"start": 84.7, "duration": 12.0}}
    gro.hasta_el_corte(plan, [Sc(6, 80.0, 84.0), Sc(7, 84.0, 88.033)], 30, [])
    assert plan["water_level"]["duration"] == round(88.033 - 84.06 - 1 / 30, 3)          # 3.94
    plan = {"time_ticker": {"start": 84.7, "duration": 12.0}}
    gro.hasta_el_corte(plan, [Sc(7, 84.5, 93.767), Sc(8, 93.767, 120.0)], 30, [])
    assert plan["time_ticker"]["duration"] == round(93.767 - 84.7 - 1 / 30, 3)
    plan = {"water_level": {"start": 10.0, "duration": 2.0}}
    gro.hasta_el_corte(plan, [Sc(0, 0.0, 30.0)], 30, [])
    assert plan["water_level"]["duration"] == 2.0                                        # cabe: no se toca


def test_b5_cota_715_no_contradice_niveles_de_otro_momento():
    """ch04: «COTA AUTORIZADA 715 m» marcaba ✗ contra 650 m (1960) y 700 m («no pasar de los setecientos metros sobre
    el nivel del mar», la oración vecina). Una cota solo contradice a otra cota en la oración ancla o la vecina."""
    voz = ["El cuatro de noviembre de mil novecientos sesenta el embalse estaba a seiscientos cincuenta metros sobre "
           "el nivel del mar.",
           "La recomendación que salió de ahí fue no pasar de los setecientos metros sobre el nivel del mar.",
           "La cota autorizada fue de setecientos quince.",
           "En noviembre de mil novecientos sesenta y dos, la ladera ya se desplazaba más de un centímetro y medio por "
           "día."]
    assert gro.contradicciones("COTA AUTORIZADA 715 m", voz)                # sin vecindad (como antes): ✗
    assert gro.contradicciones("COTA AUTORIZADA 715 m", voz, cerca=voz[1:4]) == []
    assert gro.contradicciones("COTA AUTORIZADA 720 m", voz, cerca=voz[1:4])            # otra cota al lado: ✗
    assert gro.contradicciones("MUERTOS 2.000 personas", ["Murieron mil novecientas diez personas."],
                               cerca=[]) != []                               # los muertos, contra todo el video


def test_b6_desempate_d49_con_cifra_gana_a_d71():
    """ch03 beat 5: D71 «L'UNITÀ · Diario del Partido Comunista Italiano» (oración 13) ganaba a D49 «ANCHO DE LA FISURA ·
    Más de 1 metro de ancho» (oración 14) por orden de oración. Desempate: a_pantalla → rank → con cifra → oración."""
    def v(pid: str, si: int, pantalla: str, et: str) -> dict:
        return {"pool_id": pid, "beat": 5, "rank": 1, "a_pantalla": False, "sentence_idx": si, "t0": float(si),
                "pantalla": pantalla, "etiqueta": et, "tipo": "lupa"}
    keep, rech = gro.finalizar([v("D71", 13, "Diario del Partido Comunista Italiano", "L'UNITÀ"),
                                v("D49", 14, "Más de 1 metro de ancho", "ANCHO DE LA FISURA")], None)
    assert [b["pool_id"] for b in keep] == ["D49"] and rech[0]["pool_id"] == "D71"


def test_b7_candado_del_gancho_acepta_lo_que_la_voz_dice_en_el_video():
    """ch01: D195 «LONGARONE, 1963 · 1.269 de 1.328 habitantes murieron» caía por el candado: «1963» no está en D195,
    pero la voz lo dice a 1:16 («nueve de octubre de mil novecientos sesenta y tres»)."""
    voz = ["La niña se llama Micaela Coletti y es una niña de Longarone, un pueblo de fondo de valle.",
           "Longarone, Italia, nueve de octubre de mil novecientos sesenta y tres."]
    beats = [{"n": 1, "funcion": "gancho", "t0": 0.0, "t1": 999.0, "cierre": "", "dato_central": "", "datos_apoyo": []}]
    d195 = {"id": "D195", "texto": "La tasa de mortalidad en Longarone fue del 94%, con 1.269 de 1.328 habitantes "
                                   "fallecidos.", "gancho": True, "dice_voz": False,
            "fuente": "A Tragedy in the Italian Alps (50th Anniversary) Vajont Dam, 2013"}
    ent, words = _ent([(0.0, voz[0]), (20.0, "El agua llegó de noche.")], [d195], beats=beats, voz_video=voz)
    b = _bl(0, "hecho", "1.269 de 1.328 habitantes murieron", "D195", "LONGARONE, 1963", wi=11)
    v = gro.validar({"bloques": [b]}, ent, words)
    assert [x["pool_id"] for x in v["bloques"]] == ["D195"], v["rechazos"]
    ent["items"][0]["gancho"] = False                                     # fuera del gancho: el candado de siempre
    v = gro.validar({"bloques": [b]}, ent, words)
    assert v["rechazos"][0]["regla"] == "candado" and "1963" in v["rechazos"][0]["motivo"]


def test_b8_max_chars_por_bloque_y_el_reintento_con_el_numero():
    """ch05 Q50: el recorte salió con 147 caracteres donde caben 75 (5.0 s hasta el corte × 15). El bloque validado
    lleva `max_chars`; si la entrada trae `caben`, el reintento le dice el número."""
    ent, words = _ent([(0.0, "Desde el dos de octubre los avisos se multiplicaron."), (5.0, "Nadie se fue.")],
                      [{"id": "Q50", "texto": "En continua aprensión y en continua alarma", "kind": "citas",
                        "autor": "Municipio de Erto y Casso"}])
    assert gro.caben(ent["oraciones"], 0, [Sc(0, 0.0, 5.0), Sc(1, 5.0, 9.0)]) == 75
    et = "CARTA DEL MUNICIPIO DE ERTO Y CASSO"
    largo = "x" * 112
    b = _bl(0, "documento", largo, "Q50", et)
    assert gro.pasados_de_largo({"bloques": [b]}, ent) == []                        # sin `caben` en la entrada: nada
    ent["oraciones"][0]["caben"] = 75
    msg = gro.pasados_de_largo({"bloques": [b]}, ent)
    assert len(msg) == 1 and "caben 75" in msg[0] and f"tienen {len(et) + len(largo)} caracteres" in msg[0]
    v = gro.validar({"bloques": [_bl(0, "cita", "En continua aprensión y en continua alarma", "Q50")]}, ent, words,
                    escenas=[Sc(0, 0.0, 5.0), Sc(1, 5.0, 9.0)])
    assert v["bloques"] and v["bloques"][0]["max_chars"] == 75, v["rechazos"]


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


def test_b7_el_gancho_no_es_pico_a_efectos_del_texto():
    """ch01: el gancho es el beat pico del cap; D195 (del pool, no a_pantalla) caía por «beat pico: solo a_pantalla».
    DECISIONES 2026-10-26 14:28: el gancho no es pico a efectos del texto (0–1 texto)."""
    b = {"pool_id": "D195", "beat": 1, "rank": 1, "a_pantalla": False, "sentence_idx": 2, "t0": 18.8,
         "pantalla": "1.269 de 1.328 habitantes murieron", "etiqueta": "LONGARONE, 1963", "tipo": "hecho"}
    keep, _ = gro.finalizar([{**b, "funcion": "gancho"}], 1)
    assert [x["pool_id"] for x in keep] == ["D195"]
    keep, rech = gro.finalizar([{**b, "funcion": "escalada"}], 1)
    assert not keep and "beat pico" in rech[0]["motivo"]
