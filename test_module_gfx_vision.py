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


