"""F53b Parte B — la cadena de clips de asset_manager: Gemini Omni Flash 1.1 (G) → Kling 4.0 (K) si G rechaza por
contenido. Offline, US$ 0: fal simulado (requests.post/get), Opus simulado (video_prompt.escribir), ffmpeg/ffprobe
simulados, sin esperas (time.sleep) y cost_tracker.track_video registrado."""
import base64
import json

import pytest
import requests

import asset_manager as am
import cost_tracker as ct
from script_engine import video_prompt

G, K = "gemini_omni_flash", "kling_4"
EP = {G: "google/gemini-omni-flash/v1.1/image-to-video", K: "kling/v4/image-to-video"}
JPEG = b"\xff\xd8\xff\xe0" + b"\x00" * 32                  # bytes JPEG con extensión .png (como Seedream, F52b)
MP4 = b"\x00\x00\x00\x18ftypmp42falso"
RECHAZO_G = json.dumps({"detail": [{
    "loc": ["body"],
    "msg": "The request was blocked because it violates Google's Responsible AI practices. Try rephrasing the prompt.",
    "type": "content_policy_violation"}]})
RECHAZO_K = json.dumps({"detail": [{"msg": "content blocked by the safety checker", "type": "content_policy_violation"}]})


class R:
    """Respuesta falsa de requests."""

    def __init__(self, code=200, data=None, text=None, content=b""):
        self.status_code = code
        self._data = data
        self.text = text if text is not None else json.dumps(data if data is not None else {})
        self.content = content

    def json(self):
        return self._data if self._data is not None else json.loads(self.text)

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code} Server Error: for url", response=self)


class Fal:
    """La cola de fal de mentira. `guion[motor]`: lista de pasos por pedido; cada paso es "ok", "rechazo",
    "504_submit" o "504_status". Se registran los POST (url, payload) y los GET."""

    def __init__(self, base, guion):
        self.base = base
        self.guion = {k: list(v) for k, v in guion.items()}
        self.posts: list[tuple[str, dict]] = []
        self.gets: list[str] = []
        self.pedidos: dict[str, str] = {}               # status/response id → paso

    def _motor(self, url):
        return next(k for k, e in EP.items() if url == f"{self.base}/{e}")

    def post(self, url, headers=None, json=None, timeout=None):
        motor = self._motor(url)
        self.posts.append((url, json))
        paso = self.guion[motor].pop(0)
        if paso == "504_submit":
            return R(504, text="<html>504 Gateway Time-out</html>")
        n = len(self.posts)
        self.pedidos[f"{motor}-{n}"] = paso
        return R(200, {"status_url": f"https://q/{motor}-{n}/status", "response_url": f"https://q/{motor}-{n}"})

    def get(self, url, headers=None, timeout=None):
        self.gets.append(url)
        if url == "https://x/v.mp4":
            return R(200, content=MP4)
        rid = url.split("/")[3]
        paso = self.pedidos[rid]
        if url.endswith("/status"):
            if paso == "504_status":
                return R(504, text="<html>504 Gateway Time-out</html>")
            return R(200, {"status": "COMPLETED"})
        if paso == "rechazo":
            return R(422, text=RECHAZO_G if rid.startswith(G) else RECHAZO_K)
        return R(200, {"video": {"url": "https://x/v.mp4"}})


@pytest.fixture
def entorno(monkeypatch, tmp_path):
    monkeypatch.setattr(am.api, "video_engines", (G, K), raising=False)
    monkeypatch.setattr(am.api, "video_resolution", "1080p", raising=False)
    monkeypatch.setattr(am.api, "fal_api_key", "test-falsa", raising=False)
    escritos, costos, sleeps = [], [], []

    def escribir(perfil, foto, image_prompt, ancla, intento, *, post=None, description=None):
        escritos.append({"perfil": perfil.engine_key, "foto": foto, "image_prompt": image_prompt, "ancla": ancla,
                         "intento": intento, "description": description})
        return f"PROMPT escrito con el perfil {perfil.engine_key}"

    monkeypatch.setattr(video_prompt, "escribir", escribir)
    monkeypatch.setattr(am, "_quitar_audio", lambda p: None)
    monkeypatch.setattr(am, "_clip_ffprobe", lambda p: {"segundos": 8.04, "ancho": 1920, "alto": 1080, "audio": False})
    monkeypatch.setattr(am.time, "sleep", lambda s: sleeps.append(s))
    monkeypatch.setattr(am.cost_tracker, "track_video",
                        lambda perfil, seg, ancho=None, alto=None, description="":
                        costos.append((perfil.engine_key, seg, ancho, alto, description)))
    foto = tmp_path / "cap01.png"
    foto.write_bytes(JPEG)

    def con_fal(guion):
        fal = Fal(am.api.fal_base_url, guion)
        monkeypatch.setattr(am.requests, "post", fal.post)
        monkeypatch.setattr(am.requests, "get", fal.get)
        return fal

    return {"foto": foto, "out": tmp_path / "clips" / "ch01_clip.mp4", "escritos": escritos, "costos": costos,
            "sleeps": sleeps, "con_fal": con_fal}


def _correr(e, log):
    return am._generate_clip(e["foto"], "slow push in on the hatch", e["out"], image_prompt="a rusted hatch",
                             ancla="the hatch", log=log)


def _posts_a(fal, motor):
    return [p for p in fal.posts if p[0].endswith(EP[motor])]


# 1. G rechaza por contenido → K lo hace
def test_g_rechaza_k_lo_hace(entorno):
    e = entorno
    fal = e["con_fal"]({G: ["rechazo"], K: ["ok"]})
    log: list = []
    assert _correr(e, log) == e["out"]
    assert e["out"].read_bytes() == MP4
    assert len(e["costos"]) == 1 and e["costos"][0][0] == K and e["costos"][0][1:4] == (8.04, 1920, 1080)
    assert [x["perfil"] for x in e["escritos"]] == [G, K]                  # Opus escribió una vez por motor
    assert e["escritos"][1]["intento"] == "slow push in on the hatch"
    assert (e["escritos"][1]["image_prompt"], e["escritos"][1]["ancla"]) == ("a rusted hatch", "the hatch")
    assert len(_posts_a(fal, G)) == 1 and len(_posts_a(fal, K)) == 1    # el rechazo no se reintenta
    assert _posts_a(fal, K)[0][1]["prompt"] == f"PROMPT escrito con el perfil {K}"
    assert len(log) == 1
    fila = log[0]
    assert fila["motor"] == K and fila["prompt"] == f"PROMPT escrito con el perfil {K}"
    assert len(fila["rechazos"]) == 1 and fila["rechazos"][0].startswith(f"{G}: ")
    assert "violates Google's Responsible AI practices" in fila["rechazos"][0]
    assert fila["rechazos"][0] == f"{G}: {RECHAZO_G}"                     # el texto literal del 422
    assert fila["usd"] == am.select_video_profile(K).costo(8.04)
    assert e["sleeps"] == []                                               # el rechazo no espera


# 2. G lo hace → K no se toca
def test_g_lo_hace_k_no_se_llama(entorno):
    e = entorno
    fal = e["con_fal"]({G: ["ok"], K: []})
    log: list = []
    _correr(e, log)
    assert [x["perfil"] for x in e["escritos"]] == [G]
    assert _posts_a(fal, K) == [] and len(_posts_a(fal, G)) == 1
    assert [c[0] for c in e["costos"]] == [G]
    assert log[0]["motor"] == G and log[0]["rechazos"] == []
    assert _posts_a(fal, G)[0][1]["prompt"] == f"PROMPT escrito con el perfil {G}"


# 3. Red 504 en G: una vez → reintenta G; persistente → levanta tras CLIP_MAX_ATTEMPTS_NON_REJECTION, K nunca
@pytest.mark.parametrize("falla", ["504_submit", "504_status"])
def test_504_una_vez_reintenta_g(entorno, falla):
    e = entorno
    fal = e["con_fal"]({G: [falla, "ok"], K: []})
    log: list = []
    _correr(e, log)
    assert len(_posts_a(fal, G)) == 2 and _posts_a(fal, K) == []
    assert [x["perfil"] for x in e["escritos"]] == [G]                   # el prompt no se reescribe al reintentar
    assert [c[0] for c in e["costos"]] == [G] and log[0]["motor"] == G and log[0]["rechazos"] == []
    assert len(e["sleeps"]) == 1


@pytest.mark.parametrize("falla", ["504_submit", "504_status"])
def test_504_persistente_levanta_sin_k(entorno, falla):
    e = entorno
    n = am.CLIP_MAX_ATTEMPTS_NON_REJECTION
    fal = e["con_fal"]({G: [falla] * n, K: ["ok"]})
    log: list = []
    with pytest.raises(requests.HTTPError, match="504"):
        _correr(e, log)
    assert len(_posts_a(fal, G)) == n and _posts_a(fal, K) == []
    assert [x["perfil"] for x in e["escritos"]] == [G]
    assert e["costos"] == [] and log == [] and not e["out"].exists()
    assert len(e["sleeps"]) == n - 1


# 4. Payload de cada motor
def test_payload_g_y_k(entorno):
    e = entorno
    fal = e["con_fal"]({G: ["rechazo"], K: ["ok"]})
    _correr(e, [])
    pg, pk = _posts_a(fal, G)[0][1], _posts_a(fal, K)[0][1]
    uri = "data:image/jpeg;base64," + base64.b64encode(JPEG).decode()
    assert pg["image_url"] == uri and "start_image_url" not in pg
    assert pk["start_image_url"] == uri and "image_url" not in pk
    for p in (pg, pk):
        assert p["duration"] == 8 and type(p["duration"]) is int
        assert p["resolution"] == "1080p"
        assert not any("audio" in c for c in p)                             # sin generate_audio
        assert set(p) == {"prompt", "duration", "resolution", "image_url" if p is pg else "start_image_url"}


# 5. Los dos motores rechazan
def test_los_dos_rechazan(entorno):
    e = entorno
    fal = e["con_fal"]({G: ["rechazo"], K: ["rechazo"]})
    log: list = []
    with pytest.raises(am.ContentRejectedError) as exc:
        _correr(e, log)
    assert "Responsible AI" in str(exc.value) and "safety checker" in str(exc.value)
    assert log == [{"clip": e["out"].name, "motor": None,
                    "rechazos": [f"{G}: {RECHAZO_G}", f"{K}: {RECHAZO_K}"]}]
    assert e["costos"] == [] and [x["perfil"] for x in e["escritos"]] == [G, K]
    assert len(fal.posts) == 2 and not e["out"].exists()


# 6. Que no quede Veo
@pytest.mark.parametrize("nombre", ["_call_veo_once", "_generate_veo_clip", "_veo_duration", "VEO_DURACIONES_S",
                                    "VEO_NEGATIVE_PROMPT", "_veo_poll"])
def test_sin_veo_en_asset_manager(nombre):
    assert not hasattr(am, nombre)


def test_sin_track_fal_en_cost_tracker():
    assert not hasattr(ct.CostTracker, "track_fal")       # lo borra la Parte B (en paralelo con este test)
