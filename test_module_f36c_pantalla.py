"""
test_module_f36c_pantalla.py — F36 §C (HANDOFF_F36_C_D_pantalla, aclaración 8): el guion de pantalla en papel
(script_engine/m01e_pantalla) y su consumo en Fase 2 (pantalla_entrada.preparar_cap, pantalla_filtros.validar_papel).
    (a) el JSON de salida valida contra el esquema;
    (b) el candado en papel rechaza una ficha con un año que no está en el dato (caso D195 «1963» en la etiqueta);
    (c) las 7 narraciones de Vajont alinean con la voz (100 % o la lista de las que no);
    (d) un dato no sale dos veces en el video;
    (e) un sello no repite palabra en el video;
    (f) Fase 2 (--plan-only) no llama a ningún modelo de texto: el papel se lee de disco.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from script_engine import m01e_pantalla as mp  # noqa: E402

ROOT = Path(__file__).resolve().parent
VAJONT = "f8s3-vajont"
STEPS = ROOT / "data" / "scripts" / "_steps"
CLIMA = ["PÁNICO", "CALMA", "AMENAZA", "AVISO", "ALARMA", "INMINENTE", "COLAPSO", "SILENCIO", "RABIA", "MEMORIA"]


def _ent() -> dict:
    """Un video chico de dos caps: el gancho (beat 1) y un cap de la fisura (beat 2)."""
    pool = {"datos": [{"id": "D195", "texto": "La tasa de mortalidad en Longarone fue del 94%, con 1.269 de 1.328 "
                                          "habitantes fallecidos.", "fuente": "A Tragedy in the Italian Alps, 2013"},
                      {"id": "D49", "texto": "En 1960, un pequeño desmoronamiento provocó una fisura de más de 1 metro de "
                                         "ancho y casi 2 kilómetros de largo en la montaña.", "fuente": "La inundación"}],
            "cronologia": [], "citas": [], "personajes": []}
    carga = {"topic_id": "t", "dir": Path("."), "titulos": {1: "Cama", 2: "Costura"}, "pool": pool,
             "escaleta": {"pico": {"beat": 2}, "a_pantalla": [],
                          "beats": [{"n": 1, "cap": 1, "funcion": "gancho", "intensidad": 4, "dato_central": "",
                                     "datos_apoyo": []},
                                    {"n": 2, "cap": 2, "funcion": "escalada", "intensidad": 3, "dato_central": "D49",
                                     "datos_apoyo": []}]},
             "parrafos": [{"cap": 1, "beat": 1, "texto": "Hay una casa a oscuras en el valle. La niña es de Longarone. "
                                                        "Era el año mil novecientos sesenta y tres."},
                          {"cap": 2, "beat": 2, "texto": "La montaña se abre en silencio. Aparece una fisura larga en "
                                                        "la ladera del monte. Nadie la quiere mirar de cerca."}]}
    ent = mp.entrada(carga, CLIMA)
    ent["_pool"] = pool
    return ent


def _ficha(cap: str, beat: int, pid: str, si: int, et: str, txt: str, palabra: str = "") -> dict:
    return {"cap": cap, "beat": beat, "ficha": {"pool_id": pid, "sentence_idx": si, "palabra": palabra, "etiqueta": et,
                                                "texto": txt, "aporta": "lo que la voz no dice"}, "sello": None}


def _con_respaldo(resp: dict, ent: dict) -> dict:
    """F38e §C.3: el formato pide `respaldo` por ficha y las fichas de estos tests no lo traen: se completa con el texto
    entero del ítem (fragmento literal trivial), con lo que el candado contra el respaldo es el de antes."""
    arch = {x["id"]: x["texto"] for x in ent["archivo"]}
    out = json.loads(json.dumps(resp, ensure_ascii=False))
    for fila in list(out.get("beats") or []) + list(out.get("cambios") or []):
        fi = fila.get("ficha") if isinstance(fila, dict) else None
        if isinstance(fi, dict) and not fi.get("respaldo") and fi.get("pool_id") in arch:
            fi["respaldo"] = arch[fi["pool_id"]]
    return out


def _post(resp: dict):
    def post(body: dict) -> dict:
        return {"content": [{"type": "text", "text": json.dumps(resp, ensure_ascii=False)}],
                "usage": {"input_tokens": 1000, "output_tokens": 200}, "stop_reason": "end_turn"}
    return post


def _esquema(p: dict) -> list[str]:
    """Los errores de forma del papel (vacío = válido)."""
    err = []
    for k in ("topic_id", "prompt_version", "prompt_md5", "caps", "beats", "relojes", "tarjeta", "descartados"):
        if k not in p:
            err.append(f"falta {k}")
    for b in p.get("beats") or []:
        if not {"cap", "beat", "ficha", "sello"} <= set(b):
            err.append(f"beat sin campos: {b}")
            continue
        f, s = b["ficha"], b["sello"]
        if f is not None:
            for k, t in (("pool_id", str), ("sentence_idx", int), ("palabra", str), ("etiqueta", str), ("texto", str),
                         ("estilo", str), ("aporta", str)):
                if not isinstance(f.get(k), t):
                    err.append(f"ficha {b['cap']}/{b['beat']}: {k} no es {t.__name__}")
            if f.get("estilo") not in mp.ESTILOS:
                err.append(f"estilo {f.get('estilo')!r}")
            if f.get("estilo") == "cita" and not f.get("autor"):
                err.append("cita sin autor")
        if s is not None and not (isinstance(s.get("palabra"), str) and isinstance(s.get("sentence_idx"), int)):
            err.append(f"sello {b['cap']}/{b['beat']} mal formado")
    for r in p.get("relojes") or []:
        if not (isinstance(r.get("fecha"), str) and isinstance(r.get("sentence_idx"), int)):
            err.append(f"reloj mal formado {r}")
    if p.get("tarjeta") is not None and not isinstance(p["tarjeta"].get("texto"), str):
        err.append("tarjeta mal formada")
    return err


# (a)
def test_a_salida_valida_el_esquema(tmp_path):
    ent = _ent()
    resp = {"beats": [_ficha("ch02", 2, "D49", 1, "ANCHO DE LA FISURA", "Más de 1 metro", "fisura")],
            "relojes": [], "tarjeta": None, "descartados": [{"pool_id": "D195", "motivo": "x"}]}
    res = mp.llamar(ent, tmp_path, post=_post(_con_respaldo(resp, ent)))
    p = mp.armar(ent, res)
    assert _esquema(p) == []
    f = next(b["ficha"] for b in p["beats"] if b["ficha"])
    assert f["estilo"] == "normal" and f["palabra_en_oracion"]
    assert {b["beat"] for b in p["beats"]} == {1, 2}                  # todos los beats, aunque el modelo nombre uno
    real = mp.cargar_papel(VAJONT)                                     # el papel de Vajont en disco
    if real is not None:
        assert _esquema(real) == []


# (b)
def test_b_candado_en_papel_rechaza_el_anio_que_no_esta_en_el_dato():
    ent = _ent()
    # fuera del gancho: «1963» no está en D195 ni en la oración ancla → candado
    resp = {"beats": [_ficha("ch02", 2, "D195", 1, "LONGARONE 1963", "1.269 de 1.328 habitantes murieron")]}
    v = mp.validar(_con_respaldo(resp, ent), ent)
    d = [x for x in v["descartados"] if x.get("que") == "ficha"]
    assert d and d[0]["regla"] == "candado" and "1963" in d[0]["motivo"]
    # sin el año (lo que pidió Omar, DECISIONES 16:41) pasa el candado
    resp2 = {"beats": [_ficha("ch02", 2, "D195", 1, "LONGARONE", "1.269 de 1.328 habitantes murieron")]}
    v2 = mp.validar(_con_respaldo(resp2, ent), ent)
    assert not [x for x in v2["descartados"] if x.get("regla") == "candado"]
    # en el gancho vale lo que la voz dice en todo el video (F36 §B.7): la voz dice «mil novecientos sesenta y tres»
    resp3 = {"beats": [_ficha("ch01", 1, "D195", 1, "LONGARONE 1963", "1.269 de 1.328 habitantes murieron")]}
    assert not [x for x in mp.validar(_con_respaldo(resp3, ent), ent)["descartados"] if x.get("regla") == "candado"]


# (c)
def test_c_las_siete_narraciones_de_vajont_alinean():
    from script_engine.gfx_layer import remapped_words
    from script_engine.pantalla_entrada import alinear
    from script_engine.voz_utils import oraciones
    sc = ROOT / "data" / "scripts" / "f8s3-vajont-f30.json"
    if not (STEPS / VAJONT / "01b_narracion_v3.json").exists() or not sc.exists():
        pytest.skip("sin Vajont en disco")
    ent = mp.entrada(mp.cargar(VAJONT, STEPS), CLIMA)
    chs = json.loads(sc.read_text(encoding="utf-8"))["chapters"]
    sin = []
    for c, ch in zip(ent["caps"], chs):
        ts = ROOT / "output" / "audio" / "f8s3-vajont-f30" / f"{c['cap']}_timestamps.json"
        _, words = remapped_words(SimpleNamespace(timestamps_path=str(ts), narration=ch["narration"]))
        al = alinear([s["texto"] for s in c["oraciones"]], oraciones(words))
        sin += [(c["cap"], a["papel"], a["texto"]) for a in al if not a["exacta"]]
        assert [a["voz"] for a in al] == list(range(len(al)))           # en orden, una a una
    assert sin == [], sin


# (d)
def test_d_un_dato_no_sale_dos_veces_en_el_video():
    ent = _ent()
    resp = {"beats": [_ficha("ch01", 1, "D49", 0, "ANCHO DE LA FISURA", "Más de 1 metro"),
                      _ficha("ch02", 2, "D49", 2, "ANCHO DE LA FISURA", "Más de 1 metro")]}
    v = mp.validar(_con_respaldo(resp, ent), ent)
    assert sum(1 for b in v["beats"] if b["ficha"]) == 1
    assert any(d["regla"] == "una_vez" for d in v["descartados"])


# (e)
def test_e_el_sello_no_repite_palabra_en_el_video():
    ent = _ent()
    resp = {"beats": [{"cap": "ch01", "beat": 1, "ficha": None, "sello": {"palabra": "PÁNICO", "sentence_idx": 0}},
                      {"cap": "ch02", "beat": 2, "ficha": None, "sello": {"palabra": "pánico", "sentence_idx": 0}}]}
    v = mp.validar(resp, ent)
    assert [b["sello"]["palabra"] for b in v["beats"] if b["sello"]] == ["PÁNICO"]
    assert any("ya salió en el video" in d["motivo"] for d in v["descartados"])
    # y nunca la palabra que dice la voz del cap («silencio» en ch02)
    v2 = mp.validar({"beats": [{"cap": "ch02", "beat": 2, "ficha": None,
                                 "sello": {"palabra": "SILENCIO", "sentence_idx": 1}}]}, ent)
    assert not any(b["sello"] for b in v2["beats"]) and "palabra de la voz" in v2["descartados"][0]["motivo"]


# (f)
def test_f_fase2_lee_el_papel_sin_llamar_a_ningun_modelo_de_texto(monkeypatch, tmp_path):
    import claude_helpers as hx
    from script_engine import gfx_realizador as gr
    from script_engine import pantalla_entrada as pe
    from script_engine.gfx_layer import remapped_words
    from script_engine.pantalla_filtros import validar_papel

    def no(*a, **k):
        raise AssertionError("Fase 2 llamó a un modelo de texto")
    monkeypatch.setattr(hx, "_post", no)
    monkeypatch.setattr(hx, "call_json", no)
    papel = mp.cargar_papel(VAJONT)
    sc = ROOT / "data" / "scripts" / "f8s3-vajont-f30.json"
    if papel is None or not sc.exists():
        pytest.skip("sin papel de Vajont en disco")
    script = json.loads(sc.read_text(encoding="utf-8"))
    carga = gr.cargar(VAJONT, STEPS)
    for n in range(1, 8):
        ch = script["chapters"][n - 1]
        ts = ROOT / "output" / "audio" / "f8s3-vajont-f30" / f"ch{n:02d}_timestamps.json"
        _, words = remapped_words(SimpleNamespace(timestamps_path=str(ts), narration=ch["narration"]))
        real = gr.preparar(n, carga, script["evidence_pool"], words, 0.0, tmp_path, f"ch{n:02d}")
        ctx = {"topic_id": VAJONT, "escaleta": carga["escaleta"], "pool": script["evidence_pool"],
               "chapters": script["chapters"], "chapter_number": n}
        ent, rot = pe.preparar_cap(n, f"ch{n:02d}", real, ctx, words, 0.0)
        assert rot["papel"] and rot["sin_alinear"] == []
        assert len(rot["final"]["bloques"]) == sum(1 for b in papel["beats"] if b["cap"] == f"ch{n:02d}" and b["ficha"])
        validar_papel(rot["final"]["bloques"], ent, words)
    src = (ROOT / "fase2b.py").read_text(encoding="utf-8") + (ROOT / "script_engine" / "gfx_layer.py").read_text(encoding="utf-8")
    assert "_rot_prefetch(" not in src and "gro.llamar(" not in src
    from script_engine import pantalla_filtros as rf                # aclaración 3: el ORDEN recortado
    assert [rf.regla(f) for f in rf.ORDEN] == ["anclaje", "no_dicho", "candado", "no_dicho", "spoiler", "lectura"]


# F36 §C.4 / §D: lo que Fase 2 hace con el papel (sin modelo)
def test_g_cita_ficha_con_autor_y_sellos_del_papel_nunca_al_mismo_tiempo(monkeypatch):
    from script_engine import clima
    from script_engine import pantalla_colocar as rc
    Sc = SimpleNamespace
    words = [{"word": w, "start": i * 0.5, "end": i * 0.5 + 0.4} for i, w in
             enumerate("La gente pidió justicia en la plaza. El presidente respondió algo esa noche. Nadie volvió a hablar.".split())]
    sents = __import__("script_engine.voz_utils", fromlist=["oraciones"]).oraciones(words)
    ent = {"oraciones": sents, "beats": [{"n": 1, "funcion": "revelacion", "t0": 0.0, "t1": 20.0, "cierre": "",
                                          "dato_central": "", "datos_apoyo": []}],
           "items": [{"id": "Q14", "a_pantalla": False, "por_que": "", "beats": [1], "tipo": "Q", "kind": "citas",
                      "texto": "Y justicia tendréis", "fuente": "x", "autor": "Giovanni Leone", "gancho": False,
                      "dice_voz": False}], "voz_video": [s["texto"] for s in sents], "voz_antes": ""}
    pool = {"citas": [{"id": "Q14", "texto": "Y justicia tendréis", "autor": "Giovanni Leone", "fuente": "x"}]}
    res = {"papel": True, "final": {"bloques": [{"pool_id": "Q14", "sentence_idx": 0, "word_idx": 1, "beat": 1, "rank": 1,
                                                 "tipo": "cita", "estilo": "cita", "etiqueta": "RESPUESTA DE LEONE",
                                                 "texto": "«Y justicia tendréis»", "aporta": "x", "papel": True}]}}
    plan: dict = {"title_card": None}
    scenes = [Sc(idx=0, start=0.0, end=20.0, rank="R3", quiet_side="right")]
    rc.colocar(plan, res, ent, scenes=scenes, pool=pool, used_before=set(), log=[], words=words)
    c = plan["callouts"][0]
    assert c["ficha"] and c["kind"] == "quote" and c["text"] == "«Y justicia tendréis» — Giovanni Leone"
    assert c["papel"] and c["estilo"] == "cita"
    monkeypatch.setattr(clima, "vocabulario_clima", lambda: ["MEMORIA", "RABIA"])
    juez = lambda em: {"pasa": em["word"] != "RABIA", "motivo": "tapa un rostro", "mira": "foto sola"}
    # F37 §B.1: MEMORIA en la oración 1 choca con la ficha → se mueve a la oración siguiente del beat (no se corta)
    filas = clima.sellos_del_papel(plan, scenes, ent, words, 0.0, {}, [], [{"palabra": "MEMORIA", "sentence_idx": 1}],
                                   juez=juez, usadas_video=set())
    assert [e["word"] for e in plan["emphasis"]] == ["MEMORIA"] and plan["emphasis"][0]["start"] == sents[2]["t0"]
    assert plan["emphasis"][0]["start"] >= c["start"] + c["duration"]
    assert any(f["accion"] == "movido" and "se solapa con ficha" in f["motivo"] for f in filas)
    # el crítico, en cada intento y en los dos lados: RABIA estorba en todos → papel sin colocar, con la lista
    filas = clima.sellos_del_papel(plan, scenes, ent, words, 0.0, {}, [], [{"palabra": "RABIA", "sentence_idx": 2}],
                                   juez=juez, usadas_video=set())
    mot = {f["texto"]: f["motivo"] for f in filas}
    assert "estorba" in mot["RABIA"] and "lado right" in mot["RABIA"] and "lado left" in mot["RABIA"]
    assert plan["emphasis"] == []


def test_h_plan_edit_edita_el_papel(tmp_path):
    d = tmp_path / "t"
    d.mkdir()
    p = {"topic_id": "t", "prompt_version": "m01e-1", "prompt_md5": "x", "modelo": "m", "effort": "medium",
         "intentos": 1, "usd": 0.0, "tokens_in": 1, "tarjeta": None, "relojes": [], "descartados": [],
         "caps": [{"cap": "ch01", "titulo": "T", "oraciones": ["La niña es de Longarone.", "Era de noche."]}],
         "beats": [{"cap": "ch01", "beat": 1, "funcion": "gancho", "pico": True, "ficha": None, "sello": None}]}
    (d / "01e_pantalla.json").write_text(json.dumps(p, ensure_ascii=False), encoding="utf-8")
    f = mp.editar("t", [{"cap": "ch01", "beat": 1, "ficha": {"pool_id": "D195", "sentence_idx": 0, "palabra": "Longarone",
                                                            "etiqueta": "LONGARONE", "texto": "1.269 de 1.328 habitantes"}},
                        {"tarjeta": {"texto": "9 OCT 1963 · 22:39"}}], tmp_path)
    q = json.loads(f.read_text(encoding="utf-8"))
    fi = q["beats"][0]["ficha"]
    assert fi["editado"] and fi["estilo"] == "normal" and fi["palabra_en_oracion"]
    assert q["tarjeta"]["texto"] == "9 OCT 1963 · 22:39" and (d / "01e_pantalla.antes_de_edicion.json").exists()
    assert "LONGARONE · 1.269 de 1.328 habitantes" in (d / "01e_pantalla.md").read_text(encoding="utf-8")


def test_i_el_unico_sfx_es_el_golpe_del_title_card():
    """F36 §D (catálogo 18:17, componente 9): sfx solo del title card, corrido al hueco si cae sobre una palabra."""
    from script_engine.gfx_layer import sfx_title_card
    sfx_for = lambda b: (Path("golpe.wav"), -18.0) if b == "title_card" else (Path("otro.wav"), -18.0)
    plan = {"title_card": {"kicker": "CAPÍTULO 1", "title": "t"}, "emphasis": [{"start": 5.0}], "callouts": [{"start": 9.0}],
            "chapter_question": {"start": 20.0}}
    ev = sfx_title_card(plan, [{"word": "hola", "start": 0.0, "end": 0.04}, {"word": "y", "start": 0.12, "end": 0.2}],
                        0.0, sfx_for)
    assert [e["block"] for e in ev] == ["title_card"] and ev[0]["t"] == 0.05 + ev[0]["shift_ms"] / 1000
    assert sfx_title_card({"emphasis": [{"start": 5.0}]}, [], 0.0, sfx_for) == []

