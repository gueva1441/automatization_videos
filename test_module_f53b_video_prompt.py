# -*- coding: utf-8 -*-
"""F53b Parte A punto 3 — script_engine/video_prompt.py, offline (US$ 0): `_post` falso, `_track` falso, sin red."""
import ast
import base64
import io
import urllib.error
from pathlib import Path

import pytest

import claude_helpers
from engine_profiles import PERFIL_VIDEO_G, PERFIL_VIDEO_K
from script_engine import video_prompt as vp

ROOT = Path(__file__).resolve().parent
LAB_PROMPTS = ROOT / "lab" / "hyperframes" / "f52" / "prompts_video.py"
FOTO_LAB = ROOT / "lab" / "hyperframes" / "f52" / "fotos" / "cap01.png"
JPEG = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01" + b"\x00" * 32
PNG = b"\x89PNG\r\n\x1a\n" + b"\x00\x00\x00\rIHDR" + b"\x00" * 32


def _pedido_lab() -> str:
    arbol = ast.parse(LAB_PROMPTS.read_text(encoding="utf-8"))
    for nodo in arbol.body:
        if isinstance(nodo, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "PEDIDO" for t in nodo.targets):
            return ast.literal_eval(nodo.value)
    raise AssertionError("PEDIDO no está en lab/hyperframes/f52/prompts_video.py")


def _resp(texto="  a slow push-in on the hull  ", stop="end_turn"):
    return {"model": "claude-opus-5-5", "stop_reason": stop, "usage": {"input_tokens": 10, "output_tokens": 5},
            "content": [{"type": "thinking", "thinking": "x"}, {"type": "text", "text": texto}]}


class _Post:
    def __init__(self, *respuestas):
        self.respuestas, self.bodies = list(respuestas), []

    def __call__(self, body):
        self.bodies.append(body)
        r = self.respuestas.pop(0)
        if isinstance(r, Exception):
            raise r
        return r


@pytest.fixture(autouse=True)
def _sin_costo_ni_espera(monkeypatch):
    llamadas = []
    monkeypatch.setattr(claude_helpers, "_track", lambda m, u, d: llamadas.append((m, u, d)) or 0.0)
    monkeypatch.setattr(vp.time, "sleep", lambda s: None)
    monkeypatch.setattr(claude_helpers, "_post", lambda b: pytest.fail("no se usa el _post real"))
    return llamadas


# (a) PEDIDO byte a byte
def test_pedido_byte_a_byte_el_de_f52b():
    assert vp.PEDIDO.encode("utf-8") == _pedido_lab().encode("utf-8")


# (b) el body
def test_body_jpeg_real_del_lab_imagen_primero_y_ficha_g():
    foto = FOTO_LAB.read_bytes() if FOTO_LAB.exists() else JPEG
    assert foto[:3] == b"\xff\xd8\xff"
    post = _Post(_resp())
    vp.escribir(PERFIL_VIDEO_G, foto, "a submarine hull at dusk", "the hull was never found", "slow push-in",
                post=post)
    body = post.bodies[0]
    assert body["model"] == "claude-opus-5-5" == vp.MODELO_CASILLEROS
    assert body["output_config"] == {"effort": "high"}
    assert body["max_tokens"] == claude_helpers.MAX_TOKENS
    contenido = body["messages"][0]["content"]
    assert [b["type"] for b in contenido] == ["image", "text"]
    src = contenido[0]["source"]
    assert src["type"] == "base64" and src["media_type"] == "image/jpeg"
    assert base64.b64decode(src["data"]) == foto
    texto = contenido[1]["text"]
    assert PERFIL_VIDEO_G.ficha in texto and PERFIL_VIDEO_K.ficha not in texto
    assert "a submarine hull at dusk" in texto and "the hull was never found" in texto
    assert "APPROVED MOTION (keep its intent, rewrite it for this model):\nslow push-in\n" in texto


def test_body_png_y_ficha_k_desde_ruta(tmp_path):
    ruta = tmp_path / "foto.png"
    ruta.write_bytes(PNG)
    post = _Post(_resp())
    vp.escribir(PERFIL_VIDEO_K, ruta, "img", "ancla", "mov", post=post)
    contenido = post.bodies[0]["messages"][0]["content"]
    assert contenido[0]["source"]["media_type"] == "image/png"
    assert PERFIL_VIDEO_K.ficha in contenido[1]["text"] and PERFIL_VIDEO_G.ficha not in contenido[1]["text"]
    assert contenido[1]["text"] == vp.PEDIDO.format(ficha=PERFIL_VIDEO_K.ficha, prompt_foto="img", ancla="ancla",
                                                    video_prompt_vivo="mov")


# (c) sin video_prompt (y sin ancla) → «(none)»
@pytest.mark.parametrize("vacio", [None, ""])
def test_sin_video_prompt_none(vacio):
    post = _Post(_resp())
    vp.escribir(PERFIL_VIDEO_G, JPEG, "img", "", vacio, post=post)
    texto = post.bodies[0]["messages"][0]["content"][1]["text"]
    assert "APPROVED MOTION (keep its intent, rewrite it for this model):\n(none)\n" in texto
    assert "NARRATION AT THIS MOMENT:\n(none)\n" in texto


# (d) refusal → ClaudeError (y se cobra igual)
def test_refusal_es_claude_error(_sin_costo_ni_espera):
    post = _Post(_resp(texto="", stop="refusal"))
    with pytest.raises(claude_helpers.ClaudeError, match="se negó"):
        vp.escribir(PERFIL_VIDEO_G, JPEG, "img", "a", "m", post=post)
    assert len(post.bodies) == 1 and len(_sin_costo_ni_espera) == 1


# (e) devuelve el texto del modelo; costo con la descripción por defecto
def test_devuelve_texto_y_track(_sin_costo_ni_espera):
    post = _Post(_resp())
    assert vp.escribir(PERFIL_VIDEO_K, JPEG, "img", "a", "m", post=post) == "a slow push-in on the hull"
    assert _sin_costo_ni_espera == [("claude-opus-5-5", {"input_tokens": 10, "output_tokens": 5},
                                     "video_prompt:kling_4")]
    post = _Post(_resp())
    vp.escribir(PERFIL_VIDEO_G, JPEG, "img", "a", "m", post=post, description="clip:cap01")
    assert _sin_costo_ni_espera[-1][2] == "clip:cap01"


# (f) ni JPEG ni PNG → error claro, sin llamar
def test_formato_desconocido_error_claro(tmp_path):
    ruta = tmp_path / "foto.webp"
    ruta.write_bytes(b"RIFF\x00\x00\x00\x00WEBPVP8 ")
    post = _Post()
    with pytest.raises(ValueError, match="no es JPEG ni PNG"):
        vp.escribir(PERFIL_VIDEO_G, ruta, "img", "a", "m", post=post)
    assert post.bodies == []


# reintentos como call_json
def _http(code):
    return urllib.error.HTTPError(vp.claude_helpers.URL, code, "x", {}, io.BytesIO(b'{"error":"x"}'))


def test_reintenta_529_y_red_luego_responde():
    post = _Post(_http(529), urllib.error.URLError("caida"), _resp())
    assert vp.escribir(PERFIL_VIDEO_G, JPEG, "img", "a", "m", post=post) == "a slow push-in on the hull"
    assert len(post.bodies) == 3


def test_400_es_claude_error_sin_reintento():
    post = _Post(_http(400), _resp())
    with pytest.raises(claude_helpers.ClaudeError, match="HTTP 400"):
        vp.escribir(PERFIL_VIDEO_G, JPEG, "img", "a", "m", post=post)
    assert len(post.bodies) == 1


def test_agota_intentos():
    post = _Post(*[_http(503)] * claude_helpers.MAX_ATTEMPTS)
    with pytest.raises(claude_helpers.ClaudeError, match="intentos"):
        vp.escribir(PERFIL_VIDEO_G, JPEG, "img", "a", "m", post=post)
    assert len(post.bodies) == claude_helpers.MAX_ATTEMPTS
