"""F4b §3: zoom foto-primero (gfx_vision) — validación, cache por hash, nombrado > de editor, textura solo nombrada."""
from __future__ import annotations

from script_engine import gfx_vision as gv
from script_engine.gfx_peak import sentences
from script_engine.gfx_project import GfxScene, write_project


def W(text: str, t0: float = 0.0, step: float = 0.5) -> list[dict]:
    return [{"word": w, "start": round(t0 + k * step, 3), "end": round(t0 + k * step + 0.4, 3)} for k, w in enumerate(text.split())]


HERIDA = {"label": "herida en la mano", "box": [0.4, 0.5, 0.12, 0.1], "conf": 0.9, "tipo": "manos"}
ACEITE = {"label": "mancha de aceite", "box": [0.2, 0.7, 0.2, 0.1], "conf": 0.95, "tipo": "textura"}
ROSTRO = {"label": "rostro del niño", "box": [0.5, 0.2, 0.1, 0.12], "conf": 0.85, "tipo": "rostro"}


def test_validacion_y_prioridad():
    raw = {"detalles": [{"label": "agua", "box": [0, 0, 2, 2], "conf": 0.99, "tipo": "textura"},
                        {"label": "candado", "box": [0.5, 0.5, 0.1, 0.1], "conf": 0.7, "tipo": "objeto"},
                        {"label": "mano", "box": [0.1, 0.1, 0.1, 0.1], "conf": 0.8, "tipo": "manos"},
                        {"label": "x", "box": [0.1, 0.1, 0.1, 0.1], "conf": 0.3, "tipo": "objeto"},       # baja confianza
                        {"label": "y", "box": [0.1, 0.1, 0.1, 0.1], "conf": 0.9, "tipo": "fantasma"}]}    # tipo inválido
    det = gv.validate(raw)
    assert [d["tipo"] for d in det] == ["manos", "objeto", "textura"]
    assert det[2]["box"] == [0.0, 0.0, 0.3, 0.3]                              # caja acotada (lado ≤ 0.3)


def test_cache_por_hash(tmp_path):
    img = tmp_path / "a.png"
    img.write_bytes(b"png-1")
    calls = []
    fake = lambda p: (calls.append(p), {"detalles": [HERIDA]})[1]  # noqa: E731
    assert gv.photo_details(img, tmp_path / "c.json", call=fake)[0]["label"] == "herida en la mano"
    assert gv.photo_details(img, tmp_path / "c.json", call=fake) and len(calls) == 1        # misma imagen → cache
    boom = lambda p: (_ for _ in ()).throw(RuntimeError("caído"))  # noqa: E731
    img2 = tmp_path / "b.png"
    img2.write_bytes(b"png-2")
    assert gv.photo_details(img2, tmp_path / "c.json", call=boom) is None                   # falla → respaldo zoom_judge
    assert gv.photo_details(img2, tmp_path / "c.json", call=boom) == []                     # el fallo queda anotado: no se reintenta


def test_nombrado_gana_y_textura_nunca_con_humano():
    scenes = [GfxScene(0, 0.0, 6.0), GfxScene(1, 6.0, 12.0)]
    words = W("El aceite cubría todo el piso. Tenía una herida abierta en la mano izquierda.", step=0.5)
    det = {0: [ACEITE, HERIDA]}
    z = gv.pick_zoom(det, scenes, words, intensity=None, sentences=sentences(words), peak_t=None)
    assert z["detail"] == "herida en la mano" and z["como"] == "nombrado" and z["latido"]        # no el aceite
    solo_aceite = {0: [ACEITE]}
    z2 = gv.pick_zoom(solo_aceite, scenes, words, intensity=None, sentences=sentences(words), peak_t=None)
    assert z2 and z2["tipo"] == "textura" and z2["como"] == "nombrado"                         # sin humano y nombrado: sí
    z3 = gv.pick_zoom(solo_aceite, scenes, W("Nada que ver acá."), intensity=None, sentences=[], peak_t=None)
    assert z3 is None                                                                            # textura sin nombrar: no


def test_zoom_de_editor_en_la_foto_mas_intensa_y_lejos_del_pico():
    scenes = [GfxScene(0, 0.0, 6.0), GfxScene(1, 6.0, 12.0)]
    words = W("Todo era silencio. Nadie sabía nada. Las horas pasaban lentas. Y entonces llegó el final.", step=0.6)
    sents = sentences(words)
    det = {0: [ROSTRO], 1: [dict(ROSTRO, label="rostro de un preso")]}
    hot1 = {"intensidad": [0.2, 0.3, 0.9, 0.95]}
    z = gv.pick_zoom(det, scenes, words, intensity=hot1, sentences=sents, peak_t=None)
    assert z["como"] == "de editor" and z["scene_idx"] == 1
    z = gv.pick_zoom(det, scenes, words, intensity=hot1, sentences=sents, peak_t=9.2)            # zoom de la escena 1 a ±5 s del pico
    assert z["scene_idx"] == 0
    low = {0: [dict(ROSTRO, conf=0.7)]}
    assert gv.pick_zoom(low, scenes, words, intensity=hot1, sentences=sents, peak_t=None) is None   # conf < 0.8


def test_acercar_apunta_al_rostro(tmp_path):
    img = tmp_path / "foto.png"
    img.write_bytes(b"png")
    (tmp_path / "public").mkdir()
    (tmp_path / "public" / "base.mp4").write_bytes(b"x")
    sc = GfxScene(0, 0.0, 5.0)
    sc.safe = {"image": str(img), "movement": "push", "risk": "rostro", "origin": [0.55, 0.26]}
    write_project({"chapter_number": 2}, [sc], tmp_path, duration=5.0, width=2560, height=1440, fps=30)
    html = (tmp_path / "compositions" / "scene_01.html").read_text(encoding="utf-8")
    assert 'transformOrigin: "55.0% 26.0%"' in html
    assert gv.human_box([ACEITE, ROSTRO]) == ROSTRO["box"] and gv.human_box([ACEITE]) is None


def test_verificacion_del_recorte_pasa_al_siguiente(tmp_path):
    from PIL import Image
    img = tmp_path / "f.png"
    Image.new("RGB", (200, 100), (40, 40, 40)).save(img)
    barrotes = dict(ROSTRO, label="manos aferradas", tipo="manos", conf=0.95)
    scenes = [GfxScene(0, 0.0, 6.0), GfxScene(1, 6.0, 12.0)]
    det = {0: [barrotes], 1: [ROSTRO]}
    ok = {"manos aferradas": False, "rostro del niño": True}
    calls = []

    def fake(jpg, d):
        calls.append(d["label"])
        return ok[d["label"]]
    vc = tmp_path / "v.json"
    z = gv.pick_zoom(det, scenes, W("Nadie dijo nada."), intensity={"intensidad": [0.9]},
                     sentences=sentences(W("Nadie dijo nada.")), peak_t=None,
                     verify=lambda sc, d: gv.verify_crop(img, d, vc, call=fake))
    assert z["detail"] == "rostro del niño" and calls == ["manos aferradas", "rostro del niño"]
    assert gv.verify_crop(img, barrotes, vc, call=lambda *a: 1 / 0) is False                      # cacheado: no llama
