"""Tests del laboratorio de identidad (F3 §A): helpers HTTP del servidor, memo de freezes y sesión real de ch02."""
from __future__ import annotations

import json
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest

import gfx_lab_server as lab
from script_engine import gfx_project

VIDEO = lab.DEFAULT_VIDEO


# ── helpers puros

def test_inject_runtime_va_al_principio_del_head():
    html = '<!doctype html><html><head data-x="1"><meta charset="UTF-8"></head><body></body></html>'
    out = lab.inject_runtime(html)
    assert out.count(lab.RUNTIME_TAG) == 1
    assert out.index('<head data-x="1">') < out.index(lab.RUNTIME_TAG) < out.index("<meta")


def test_inject_runtime_sin_head_y_template():
    tpl = "<template><div>escena</div></template>"
    assert lab.inject_runtime(tpl) == lab.RUNTIME_TAG + tpl


@pytest.mark.parametrize("header,size,expected", [
    (None, 100, None),
    ("bytes=0-9", 100, (0, 9)),
    ("bytes=90-", 100, (90, 99)),
    ("bytes=-10", 100, (90, 99)),
    ("bytes=50-500", 100, (50, 99)),
    ("bytes=100-", 100, None),
    ("bytes=-", 100, None),
    ("items=0-9", 100, None),
])
def test_parse_range(header, size, expected):
    assert lab.parse_range(header, size) == expected


def test_safe_join_no_sale_de_la_raiz(tmp_path):
    assert lab.safe_join(tmp_path, "a/b.html") == (tmp_path / "a" / "b.html").resolve()
    assert lab.safe_join(tmp_path, "../fuera.txt") is None
    assert lab.safe_join(tmp_path, "a/../../fuera.txt") is None


def test_player_y_runtime_son_los_del_paquete_pineado():
    """El preview usa el runtime real de hyperframes (nunca una copia)."""
    assert lab.PLAYER_JS.exists() and lab.RUNTIME_JS.exists()
    assert "gfx_runtime" in lab.PLAYER_JS.parts and "node_modules" in lab.RUNTIME_JS.parts


# ── memo de freezes (gfx_project._extract_freeze)

def test_freeze_memo_no_repite_ffmpeg(tmp_path, monkeypatch):
    base = tmp_path / "base.mp4"
    base.write_bytes(b"x" * 10)
    out = tmp_path / "cuts" / "freeze_02.jpg"
    calls = []

    def fake_run(cmd, **kw):
        calls.append(cmd)
        Path(cmd[-1]).write_bytes(b"jpg")
        return type("R", (), {"returncode": 0})()

    monkeypatch.setattr(gfx_project.subprocess, "run", fake_run)
    monkeypatch.setattr(gfx_project, "_FREEZE_MEMO", set())
    assert gfx_project._extract_freeze(base, 1.5, out)
    assert gfx_project._extract_freeze(base, 1.5, out)
    assert len(calls) == 1                                  # segunda vez: memo
    assert gfx_project._extract_freeze(base, 2.5, out)
    assert len(calls) == 2                                  # otro t → ffmpeg
    out.unlink()
    assert gfx_project._extract_freeze(base, 2.5, out)
    assert len(calls) == 3                                  # el archivo desapareció → ffmpeg
    base.write_bytes(b"y" * 20)                             # el base cambió → ffmpeg
    assert gfx_project._extract_freeze(base, 2.5, out)
    assert len(calls) == 4


# ── sesión real de ch02 (solo si están los datos de Orleans)

def _has_data() -> bool:
    try:
        from config import OUTPUT_DIR
    except Exception:  # noqa: BLE001
        return False
    w = OUTPUT_DIR / VIDEO / "_fase2b_work"
    return (w / "gfx_plan_ch02.resolved.json").exists() and (
        (w / "gfx_ch02" / "public" / "base.mp4").exists() or (w / "gfx_lab_ch02" / "public" / "base.mp4").exists())


needs_data = pytest.mark.skipif(not _has_data(), reason="sin datos de Orleans ch02")


@pytest.fixture(scope="module")
def server():
    session = lab.LabSession(VIDEO, "ch02")
    lab.LabHandler.session = session
    srv = ThreadingHTTPServer(("127.0.0.1", 0), lab.LabHandler)
    th = threading.Thread(target=srv.serve_forever, daemon=True)
    th.start()
    yield session, f"http://127.0.0.1:{srv.server_address[1]}"
    srv.shutdown()


def _get(url: str, headers: dict | None = None):
    req = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.status, dict(r.headers), r.read()


def _post(url: str, obj: dict):
    req = urllib.request.Request(url, data=json.dumps(obj).encode(), method="POST",
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())


@needs_data
def test_story_tiene_palabras_fotos_y_audio(server):
    _, url = server
    st = json.loads(_get(url + "/api/story")[2])
    assert st["cap"] == "ch02" and st["duration"] > 90
    assert len(st["words"]) > 100 and all(w["word"] for w in st["words"])
    assert [w["start"] for w in st["words"]] == sorted(w["start"] for w in st["words"])
    assert len(st["photos"]) == 15 and st["photos"][0]["start"] == 0.0
    assert all(p["thumb"] for p in st["photos"])
    code, h, body = _get(url + "/media/audio", {"Range": "bytes=0-99"})
    assert code == 206 and len(body) == 100 and h["Content-Type"] == "audio/mpeg"
    code, h, _ = _get(url + "/media/thumb/0")
    assert code == 200 and h["Content-Type"] == "image/jpeg"


@needs_data
def test_preview_usa_las_plantillas_reales(server):
    """El preview es write_project (mismo templater que el render) + el runtime inyectado."""
    session, url = server
    plan = session.director_plan()
    r = _post(url + "/preview", {"plan": plan})
    assert r["src"].startswith("/composition/index.html?v=")
    assert any(c["block"] == "title_card" for c in r["cues"])
    html = _get(url + "/composition/index.html")[2].decode("utf-8")
    assert html.count(lab.RUNTIME_TAG) == 1
    assert 'data-composition-src="compositions/scene_01.html"' in html
    on_disk = (session.project / "index.html").read_text(encoding="utf-8")
    assert html.replace(lab.RUNTIME_TAG, "") == on_disk
    scene = _get(url + "/composition/compositions/scene_02.html")[2].decode("utf-8")
    assert lab.RUNTIME_TAG in scene and 'data-composition-id="scene-02"' in scene
    code, _, body = _get(url + "/composition/public/base.mp4", {"Range": "bytes=0-1023"})
    assert code == 206 and len(body) == 1024
    # el proyecto del lab NUNCA es el del render
    assert session.project.name == "gfx_lab_ch02"


@needs_data
def test_preview_refleja_cambios_del_plan(server):
    session, url = server
    plan = session.director_plan()
    plan["callouts"] = []
    r = _post(url + "/preview", {"plan": plan})
    assert not any(c["block"] == "data_callout" for c in r["cues"])
    assert 'class="callout' not in (session.project / "index.html").read_text(encoding="utf-8")
    _post(url + "/preview", {"plan": session.director_plan()})


@needs_data
def test_rutas_fuera_de_raiz_dan_403(server):
    _, url = server
    with pytest.raises(urllib.error.HTTPError) as e:
        _get(url + "/composition/..%2F..%2Fgfx_plan_ch02.json")
    assert e.value.code in (403, 404)


# ── §B: catálogo, sugerencias, tokens en vivo y candado

CAT = json.loads((lab.LAB_DIR / "catalogo.json").read_text(encoding="utf-8"))
SUG = json.loads((lab.LAB_DIR / "sugerencias_ch02.json").read_text(encoding="utf-8"))
_HANDOFF_IDS = {"ken_burns_in", "ken_burns_out", "pan", "depthflow", "veo", "punch_in", "hold", "vignette", "grain",
                "desat", "tint", "letterbox", "spotlight", "keyword_emphasis", "title_card", "data_callout", "count_up",
                "keyword_stamp", "source_tag", "lower_third", "quote_card", "archive_clipping", "icon_callout",
                "icon_array", "cut", "dip_to_black", "flash", "crossfade", "zoom_through", "ink_wipe", "burn",
                "match_cut", "sfx", "chapter_question", "next_chapter_card", "black_hold"}


def test_miniaturas_css_existen_para_cada_animacion():
    css = (lab.LAB_DIR / "anim_previews.css").read_text(encoding="utf-8")
    anims = {o["anim"] for e in CAT["elementos"] for a in e["atributos"] if a["tipo"] == "anim" for o in a["opciones"]}
    missing = [a for a in anims if f".ap-{a}" not in css]
    assert not missing, missing


def test_sugerencias_borrador_valido():
    ids = {e["id"] for e in CAT["elementos"]}
    s = SUG["sugerencias"]
    assert 15 <= len(s) <= 20
    assert len({x["id"] for x in s}) == len(s)
    for x in s:
        assert x["elemento"] in ids, x["id"]
        assert x["accion"]["tipo"] in SUG["acciones"], x["id"]
        assert x["titulo"] and x["por_que"]


def test_rules_override_se_restaura():
    from script_engine import gfx_project
    before = (gfx_project.gfx_rules, gfx_project.GRADE_VARIANTS)
    with lab.rules_override({"accent_hex": "#123456", "vignette_opacity": 0.3}):
        assert gfx_project.gfx_rules.accent_hex == "#123456"
        assert gfx_project.GRADE_VARIANTS["off"]["opacity"]["gr-vignette"] == 0.3
    assert (gfx_project.gfx_rules, gfx_project.GRADE_VARIANTS) == before
    with pytest.raises(ValueError):
        lab.rules_override({"no_existe": 1})
    with pytest.raises(RuntimeError):
        with lab.rules_override({"accent_hex": "#000000"}):
            raise RuntimeError("falla en el medio")
    assert (gfx_project.gfx_rules, gfx_project.GRADE_VARIANTS) == before


@needs_data
def test_sugerencias_apuntan_a_palabras_de_ch02(server):
    session, _ = server
    words = {w["i"]: w["word"] for w in session.story()["words"]}
    lex = {h["i"] for h in session.context()["lexicon_hits"]}
    for x in SUG["sugerencias"]:
        assert x["word_i"] in words, x["id"]
        if x["accion"]["tipo"] in ("add_emphasis", "set_emphasis"):
            assert x["word_i"] in lex, f"{x['id']}: «{words[x['word_i']]}» no es del léxico"


@needs_data
def test_candado_en_el_preview(server):
    session, url = server
    plan = session.director_plan()
    plan["callouts"] = plan["callouts"] + [{"text": "TEXTO INVENTADO 999", "start": 20.0, "kind": "figure",
                                           "duration": 2.5, "side": "left", "source": ""}]
    plan["chapter_question"] = {"text": "¿Quién apagó la luz?", "start": 94.0, "duration": 3.0, "keyword": "", "manual": True}
    r = _post(url + "/preview", {"plan": plan, "tokens": {"accent_hex": "#123456"}})
    assert any(x["text"] == "TEXTO INVENTADO 999" for x in r["rejected"])
    assert not any(c["text"] == "TEXTO INVENTADO 999" for c in r["cues"])
    assert any(c["block"] == "chapter_question" for c in r["cues"])        # manual: fuera del candado
    html = (session.project / "index.html").read_text(encoding="utf-8")
    assert "#123456" in html and "Quién apagó la luz" in html
    # F37 §B.4: sin el candado de la pregunta reformulada del director (borrado): la pregunta es el `cierre` de la
    # escaleta o la manual de Omar
    _post(url + "/preview", {"plan": session.director_plan(), "tokens": {}})


@needs_data
def test_contexto_lexico_y_facts(server):
    session, url = server
    ctx = json.loads(_get(url + "/api/context")[2])
    words = {h["word"].strip(".,") for h in ctx["lexicon_hits"]}
    assert {"sumergidos", "encierro", "aguas"} <= words
    assert any(h["icon"] == "candado" for h in ctx["lexicon_hits"])
    assert any(f["eligible"] for f in ctx["facts"])
    prof = json.loads(_get(url + "/api/profile")[2])
    assert prof["rules"]["accent_hex"].startswith("#")


# ── §F: foto por foto (GET /objetos + sugerencia de movimiento)

@pytest.mark.parametrize("prompt,expected", [
    ({"text_in_image": {"present": True, "text": "AGOSTO 2005"}, "shot_scale": "close"}, "quieta"),
    ({"shot_scale": "medium", "subject": "An African American woman and a young boy"}, "acercar"),
    ({"shot_scale": "wide", "subject": "a dense, crowded mass of incarcerated individuals"}, "paneo"),
    ({"shot_scale": "detail", "subject": "the base of a steel door"}, "acercar"),
    ({"shot_scale": "extreme_wide", "subject": "the cityscape of New Orleans"}, "alejar"),
])
def test_suggest_movement(prompt, expected):
    assert lab.suggest_movement(prompt, already_out=False)[0] == expected


def test_suggest_movement_un_solo_alejar():
    p = {"shot_scale": "wide", "subject": "The Orleans Parish Prison complex"}
    assert lab.suggest_movement(p, already_out=False)[0] == "alejar"
    assert lab.suggest_movement(p, already_out=True)[0] == "3D"


@needs_data
def test_objetos_por_foto(server):
    _, url = server
    seen = []
    for i in range(15):
        o = json.loads(_get(url + f"/objetos?foto={i}")[2])
        assert o["foto"] == i and o["end"] > o["start"]
        assert o["movimiento_ia"]["forma"] in ("acercar", "alejar", "paneo", "3D", "quieta")
        assert o["movimiento_pipeline"]["forma"]
        seen.append(o["movimiento_ia"]["forma"])
    assert seen[0] == "quieta"                       # el calendario tiene texto: no se mueve
    assert seen.count("alejar") <= 1                 # "1 por capítulo como máximo" (§2 A)
    with pytest.raises(urllib.error.HTTPError) as e:
        _get(url + "/objetos?foto=99")
    assert e.value.code == 400


def test_pantalla_foto_por_foto_y_modo_experto():
    """§F: la vista por defecto es foto por foto; la experta sigue en ?modo=experto (sin link en la UI)."""
    idx = (lab.LAB_DIR / "index.html").read_text(encoding="utf-8")
    exp = (lab.LAB_DIR / "experto.html").read_text(encoding="utf-8")
    assert "lab_foto.js" in idx and 'modo") === "experto"' in idx and "experto.html" in idx
    assert "lab_foto.js" not in exp and 'id="catalog"' in exp
    assert 'id="catalog"' not in idx and 'id="strip"' not in idx      # sin pestañas ni tira permanente
    js = (lab.LAB_DIR / "lab_foto.js").read_text(encoding="utf-8")
    for txt in ("▶ Probar", "Se queda", "Otras formas", "más opciones", "✖ Nunca", "Ver capítulo completo",
                "Agregar", "Ver este tramo con todo", "TRAMO", "misma foto que el tramo anterior"):
        assert txt in js or txt in idx, txt
    # regla 6: ninguna forma que el preview no dibuje (las de §D ya no aparecen)
    for gone in ('"fundido cruzado", "tinta"', 'opt("zoom")', '"post-it"', '"máquina"', '"respira"', 'Tercio inferior', '"Cita"', 'btn-render" class'):
        assert gone not in js and gone not in idx, gone


# ── §F2: tramo por tramo — Probar aislado, movimientos y salidas por tramo

def test_safe_static_y_pull_en_el_templater(tmp_path):
    """quieta = sin tween; alejar = de safe_push_scale a 1 (los valores viejos push/pan no cambian)."""
    from script_engine.gfx_project import GfxScene, _scene_html
    img = tmp_path / "f.png"
    img.write_bytes(b"png")
    (tmp_path / "public").mkdir()
    out = {}
    for mv in ("push", "pan", "pull", "static"):
        sc = GfxScene(3, 10.0, 15.0, "R3", safe={"image": str(img), "movement": mv})
        out[mv] = _scene_html(sc, 4, {}, tmp_path, tmp_path / "public" / "base.mp4", 2560, 1440, 30)
    assert 'tl.to("#sf04"' not in out["static"] and 'gsap.set("#sf04", { scale: 1,' in out["static"]
    assert 'tl.to("#sf04", { scale: 1, duration' in out["pull"]
    assert 'tl.to("#sf04", { x:' in out["pan"]
    assert 'tl.to("#sf04", { scale: 1.08' in out["push"] or "tl.to(\"#sf04\", { scale:" in out["push"]


@needs_data
def test_preview_solo_un_objeto_sobre_la_foto_quieta(server):
    session, url = server
    e = {"word": "sumergidos", "category": "agua", "layer": "agua", "start": 33.7, "duration": 2.5, "side": "right",
         "stamp": True, "icon_callout": False, "icon": None}
    solo = {"chapter_number": 2, "emphasis": [dict(e, layer="", icon_callout=False)]}
    r = _post(url + "/preview", {"plan": solo, "tokens": {}, "movimientos": {"4": "quieta"}, "solo": [4]})
    assert r["src"].startswith("/solo/index.html")
    idx = _get(url + "/solo/index.html")[2].decode("utf-8")
    assert idx.count("data-composition-src") == 1 and ">sumergidos<" in idx
    assert "md0-rise" not in idx and "md0-vig" not in idx       # sin la capa de mood agua
    sc = _get(url + "/solo/compositions/scene_05.html")[2].decode("utf-8")
    assert "sf05" in sc and 'tl.to("#sf05"' not in sc            # foto fija, quieta
    assert session.solo_project.name == "gfx_lab_ch02_solo"


@needs_data
def test_preview_movimientos_y_salidas_por_tramo(server):
    session, url = server
    r = _post(url + "/preview", {"plan": {"chapter_number": 2}, "tokens": {},
                                 "movimientos": {"3": "alejar", "4": "3D"}, "salidas": {"3": "fundido negro"}, "solo": [3, 4]})
    assert "/solo/" in r["src"]
    s4 = _get(url + "/solo/compositions/scene_04.html")[2].decode("utf-8")
    s5 = _get(url + "/solo/compositions/scene_05.html")[2].decode("utf-8")
    assert 'tl.to("#sf04", { scale: 1, duration' in s4         # alejar sobre el PNG
    assert "sf05" not in s5 and "public/base.mp4" in s5         # 3D = clip DepthFlow
    assert "dp05" in s5                                          # fundido negro elegido para esa salida
    with pytest.raises(urllib.error.HTTPError):
        _post(url + "/preview", {"plan": {"chapter_number": 2}, "movimientos": {"3": "volar"}, "solo": [3]})


@needs_data
def test_cues_sin_escribir_el_proyecto(server):
    session, url = server
    before = (session.project / "index.html").stat().st_mtime_ns
    r = _post(url + "/cues", {"plan": session.director_plan(), "tokens": {}})
    assert any(c["block"] == "archive_clipping" for c in r["cues"]) and r["rejected"] == []
    assert (session.project / "index.html").stat().st_mtime_ns == before


@needs_data
def test_objetos_trae_imagen_y_3d(server):
    _, url = server
    o = json.loads(_get(url + "/objetos?foto=3")[2])
    assert o["imagen"].endswith(".png") and o["hay_3d"] is True


# ── moods sin patrones repetidos (Omar: las cáusticas del agua se veían como un mosquitero)

@pytest.mark.parametrize("layer", ["agua", "veneno", "muerte", "oscuridad"])
def test_moods_sin_patrones_repetidos(layer):
    from script_engine.gfx_project import mood_layer
    html, init, js = mood_layer(0, layer, 33.7, 2.5, 2560, 1440)
    assert "repeating-" not in html, f"{layer}: patrón repetido"
    assert "cau" not in html


def test_mood_agua_sube_en_1s_y_baja_al_salir():
    from script_engine.gfx_project import mood_layer
    html, init, js = mood_layer(0, "agua", 33.7, 2.5, 2560, 1440)
    tl = " ".join(js)
    assert "height:34%" in html                                          # hasta 1/3
    assert 'tl.to("#md0-rise", { yPercent: 0, duration: 1.0' in tl          # sube en 1 s
    assert '.to("#md0-rise", { yPercent: 100, duration: .5' in tl           # baja al salir (no se desvanece)
    assert "md0-vig" in html                                              # bordes un poco más oscuros


# ── F3: íconos y pregunta de cierre en el lab

@needs_data
def test_lab_iconos_y_contexto(server):
    _, url = server
    ctx = json.loads(_get(url + "/api/context")[2])
    assert len(ctx["icon_keys"]) == 14 and ctx["category_icon"]["agua"] == "gota"   # 12 + espiral y rayo (G4)
    assert ctx["fact_icon"]                                            # datos con ícono de su categoría
    code, h, body = _get(url + "/media/icon/gota.svg")
    assert code == 200 and h["Content-Type"] == "image/svg+xml" and b"<svg" in body
    code, h, _ = _get(url + "/media/sfx/drone_subida.wav")
    assert code == 200 and h["Content-Type"] == "audio/wav"
    with pytest.raises(urllib.error.HTTPError):
        _get(url + "/media/icon/no_existe.svg")
    st = json.loads(_get(url + "/api/story")[2])
    assert all(p["dark_v"] in ("top", "mid") for p in st["photos"])


def test_pantalla_iconos_y_pregunta():
    js = (lab.LAB_DIR / "lab_foto.js").read_text(encoding="utf-8")
    idx = (lab.LAB_DIR / "index.html").read_text(encoding="utf-8")
    for txt in ("openIconPicker", "prop:icono:", "con ícono", "otra pregunta", "/question", "sfx-drone", "free_icon"):
        assert txt in js or txt in idx, txt
    assert "Con la palabra en sello" not in js                         # el ícono nunca va suelto


@needs_data
def test_dos_pestanas_no_se_pisan(server, monkeypatch, tmp_path):
    session, url = server
    monkeypatch.setattr(session, "state_path", tmp_path / "estado.json")
    st = {"plan": {"chapter_number": 2}, "tokens": {}}
    v1 = _post(url + "/api/plan", st)["version"]
    v2 = _post(url + "/api/plan", {**st, "base_version": v1})["version"]       # misma pestaña: ok
    with pytest.raises(urllib.error.HTTPError) as e:
        _post(url + "/api/plan", {**st, "base_version": v1})                   # pestaña vieja: 409, no pisa
    assert e.value.code == 409 and json.loads(session.state_path.read_text(encoding="utf-8"))["version"] == v2


def test_pantalla_pico_y_bloques_nuevos():
    js = (lab.LAB_DIR / "lab_foto.js").read_text(encoding="utf-8")
    for txt in ("Nivel de agua", "Reloj «", "latido", "Corte a negro", "badge pico", "PICO", "sfx-latido", "regla de pico"):
        assert txt in js or txt in (lab.LAB_DIR / "index.html").read_text(encoding="utf-8"), txt
