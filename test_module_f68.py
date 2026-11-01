"""F68: Nano Banana 2 Lite (una foto por llamada), respaldo Seedream 4.5, registro junto a la foto. Sin red: requests falso."""
import json
from pathlib import Path

import pytest
from PIL import Image

import asset_manager as am
from config import api
from engine_profiles import PERFIL_NB2_LITE, PERFIL_SEEDREAM, select_profile


class Resp:
    def __init__(self, data=None, status=200, text=None, content=b""):
        self._data, self.status_code, self.content = data, status, content
        self.text = text if text is not None else json.dumps(data or {})

    def json(self):
        return self._data

    def raise_for_status(self):
        if self.status_code >= 400:
            raise am.requests.HTTPError(f"{self.status_code}", response=self)


RECHAZO = json.dumps({"detail": [{"msg": "flagged", "type": "content_policy_violation", "categories": ["model_moderated"],
                                  "input": {"prompt": "X", "safety_tolerance": "6"}}]})
SIN_MEDIA = json.dumps({"detail": [{"msg": "no output", "type": "no_media_generated", "input": {"prompt": "X"}}]})
OTRO_422 = json.dumps({"detail": [{"msg": "bad field", "type": "value_error", "input": {"safety_tolerance": "6"}}]})


def _png(tam=(1376, 768)):
    import io
    b = io.BytesIO()
    Image.new("RGB", tam, (90, 60, 40)).save(b, format="PNG")
    return b.getvalue()


class Fal:
    """Cola falsa: `rechazar` = {modelo: cuerpo del error al pedir el resultado}."""

    def __init__(self, monkeypatch, rechazar=None, tam=(1376, 768)):
        self.pedidos, self.resultados = [], 0
        self.rechazar, self.tam = rechazar or {}, tam
        monkeypatch.setattr(am.requests, "post", self.post)
        monkeypatch.setattr(am.requests, "get", self.get)
        monkeypatch.setattr(am.time, "sleep", lambda s: None)

    def post(self, url, headers=None, json=None, timeout=None):
        modelo = url.split("queue.fal.run/")[1]
        self.pedidos.append((modelo, json))
        return Resp({"request_id": f"r{len(self.pedidos)}", "status_url": f"https://s/{modelo}", "response_url": f"https://r/{modelo}"})

    def get(self, url, headers=None, timeout=None):
        if url.startswith("https://s/"):
            return Resp({"status": "COMPLETED"})
        if url.startswith("https://r/"):
            self.resultados += 1
            modelo = url[len("https://r/"):]
            if modelo in self.rechazar:
                return Resp(status=422, text=self.rechazar[modelo])
            return Resp({"images": [{"url": "https://img/x.png"}], "seed": 7})
        return Resp(content=_png(self.tam))


@pytest.fixture(autouse=True)
def motor(monkeypatch):
    monkeypatch.setattr(api, "image_engine", "nb2_lite")
    monkeypatch.setattr(am.cost_tracker, "track_nb2_lite", lambda **k: None)
    monkeypatch.setattr(am.cost_tracker, "track_seedream", lambda **k: None)
    monkeypatch.setattr(am.error_handler, "log_error", lambda *a, **k: None)


def _registro(out: Path) -> dict:
    return json.loads(out.with_name(out.stem + am.LLAMADA_SUFIJO).read_text(encoding="utf-8"))


def test_perfiles():
    assert api.image_engine == "nb2_lite"
    assert PERFIL_NB2_LITE.render.model_id == "google/nano-banana-2-lite"
    assert PERFIL_NB2_LITE.render.edit_model_id == "google/nano-banana-2-lite/edit"
    assert PERFIL_NB2_LITE.render.safety_tolerance == "6" and PERFIL_NB2_LITE.render.aspect_ratio == "16:9"
    assert PERFIL_SEEDREAM.render.model_id == "fal-ai/bytedance/seedream/v4.5/text-to-image"
    assert PERFIL_SEEDREAM.render.accepts_seed and PERFIL_SEEDREAM.render.cost_usd == 0.04
    assert PERFIL_SEEDREAM.aspect_ratio_text == "The image has a 16:9 aspect ratio."   # el texto de m03 no cambia


def test_sin_persona_text_to_image_tal_cual(monkeypatch, tmp_path):
    fal = Fal(monkeypatch)
    out = tmp_path / "ch02_img_01.png"
    meta = am._generate_image_raw("Una escena.", out, False)
    modelo, payload = fal.pedidos[0]
    assert modelo == "google/nano-banana-2-lite" and payload["prompt"] == "Una escena."
    assert "image_urls" not in payload and payload["safety_tolerance"] == "6" and payload["aspect_ratio"] == "16:9"
    assert meta["motor"] == "nb2_lite" and meta["respaldo_motivo"] is None and meta["usd"] == 0.042


@pytest.mark.parametrize("uris,frase", [(["data:a"], am.FRASE_EDIT_UNA), (["data:a", "data:b"], am.FRASE_EDIT_VARIAS)])
def test_edit_antepone_la_frase_del_lab(monkeypatch, tmp_path, uris, frase):
    fal = Fal(monkeypatch)
    am._generate_image_raw("Una escena.", tmp_path / "ch02_img_01.png", False, foto_madre_data_uris=uris)
    modelo, payload = fal.pedidos[0]
    assert modelo == "google/nano-banana-2-lite/edit"
    assert payload["prompt"] == f"{frase} Una escena." and payload["image_urls"] == uris


def test_foto_final_sin_frase(monkeypatch, tmp_path):
    fal = Fal(monkeypatch)
    am._generate_image_raw("Edit.", tmp_path / "x_final.png", False, foto_madre_data_uris=["data:a"], frase_de_madres=False)
    assert fal.pedidos[0][1]["prompt"] == "Edit."


def test_nativo_y_escalado(monkeypatch, tmp_path):
    Fal(monkeypatch)
    out = tmp_path / "ch02_img_01.png"
    am._generate_image_raw("Una escena.", out, False)
    assert Image.open(tmp_path / "ch02_img_01_native.png").size == (1376, 768)
    assert Image.open(out).size == (2560, 1440)


@pytest.mark.parametrize("cuerpo,tipo", [(RECHAZO, "content_policy_violation"), (SIN_MEDIA, "no_media_generated")])
def test_rechazo_va_a_seedream_con_mismo_texto_y_madres(monkeypatch, tmp_path, cuerpo, tipo):
    fal = Fal(monkeypatch, {"google/nano-banana-2-lite/edit": cuerpo}, tam=(2560, 1440))
    out = tmp_path / "ch02_img_01.png"
    meta = am._generate_image_raw("Una escena.", out, False, foto_madre_data_uris=["data:a"])
    (m1, p1), (m2, p2) = fal.pedidos
    assert m2 == "fal-ai/bytedance/seedream/v4.5/edit"
    assert p2["prompt"] == p1["prompt"] and p2["image_urls"] == p1["image_urls"]
    assert meta["motor"] == am.MOTOR_RESPALDO and tipo in meta["respaldo_motivo"] and meta["usd"] == 0.04
    assert "input" not in meta["respaldo_motivo"]
    assert Image.open(out).size == (2560, 1440)


def test_otro_422_no_dispara_respaldo(monkeypatch, tmp_path):
    fal = Fal(monkeypatch, {"google/nano-banana-2-lite": OTRO_422})
    with pytest.raises(Exception):
        am._generate_image_raw("Una escena.", tmp_path / "a.png", False)
    assert {m for m, _ in fal.pedidos} == {"google/nano-banana-2-lite"}


def test_rechazo_de_los_dos_da_tres_vueltas(monkeypatch, tmp_path):
    fal = Fal(monkeypatch, {"google/nano-banana-2-lite": RECHAZO, "fal-ai/bytedance/seedream/v4.5/text-to-image": RECHAZO})
    with pytest.raises(Exception):
        am._generate_image_raw("Una escena.", tmp_path / "a.png", False)
    assert len(fal.pedidos) == 6       # adenda 4: el intento y 2 más, cada uno por los dos motores


def test_registro_guarda_texto_y_request_id_antes_de_esperar(monkeypatch, tmp_path):
    fal = Fal(monkeypatch)
    out = tmp_path / "ch02_img_01.png"
    visto = {}
    get = fal.get

    def get_mira(url, headers=None, timeout=None):
        if url.startswith("https://s/") and not visto:
            visto.update(_registro(out))
        return get(url, headers, timeout)

    monkeypatch.setattr(am.requests, "get", get_mira)
    am._generate_image_raw("Una escena.", out, False, foto_madre_data_uris=["data:a"])
    fila = visto["llamadas"]["nb2_lite"]
    assert fila["request_id"] == "r1" and fila["estado"] == "en_cola" and fila["endpoint"] == "google/nano-banana-2-lite/edit"
    assert fila["texto"] == f"{am.FRASE_EDIT_UNA} Una escena." and fila["parametros"]["safety_tolerance"] == "6"
    assert "image_urls" not in fila["parametros"] and len(fila["referencias_md5"]) == 1
    assert _registro(out)["llamadas"]["nb2_lite"]["estado"] == "ok"


def test_reanuda_sin_volver_a_pedir(monkeypatch, tmp_path):
    fal = Fal(monkeypatch)
    out = tmp_path / "a.png"
    payload = {"prompt": "T", "aspect_ratio": "16:9", "safety_tolerance": "6", "num_images": 1}
    firma = am.hashlib.md5(json.dumps(["google/nano-banana-2-lite", payload], sort_keys=True).encode()).hexdigest()
    out.with_name("a" + am.LLAMADA_SUFIJO).write_text(json.dumps({"llamadas": {"nb2_lite": {
        "estado": "en_cola", "firma": firma, "request_id": "viejo", "status_url": "https://s/m", "response_url": "https://r/m"}}}))
    am._generate_image_raw("T", out, False)
    assert fal.pedidos == [] and out.exists()
    assert _registro(out)["llamadas"]["nb2_lite"]["request_id"] == "viejo"


def test_pedido_terminado_no_se_reusa(monkeypatch, tmp_path):
    fal = Fal(monkeypatch)
    out = tmp_path / "a.png"
    am._generate_image_raw("T", out, False)
    am._generate_image_raw("T", out, False)      # «rehacer foto» paga de nuevo
    assert len(fal.pedidos) == 2


def test_madres_solo_persona(tmp_path):
    m = tmp_path / "m.png"
    m.write_bytes(_png())
    reg = {"Daniel": str(m), "__subject__": str(m)}
    assert am._madres_para_item([], ["__subject__"], None, reg, {}) == []
    assert am._madres_para_item(["Daniel"], ["__subject__"], None, reg, {}) == [("Daniel", str(m))]


def test_madres_con_seedream_como_antes(monkeypatch, tmp_path):
    monkeypatch.setattr(api, "image_engine", "seedream")
    m = tmp_path / "m.png"
    m.write_bytes(_png())
    assert am._madres_para_item([], ["__subject__"], None, {"__subject__": str(m)}, {}) == [("__subject__", str(m))]


def _cap_clip(tmp_path, monkeypatch):
    monkeypatch.setattr(am, "OUTPUT_DIR", tmp_path)
    veo = tmp_path / "v" / "assets" / "ch01_veo"
    veo.mkdir(parents=True)
    clip = veo / "ch01_clip_01.mp4"
    clip.write_bytes(b"clip")
    return clip, {"id": "ch01", "video_prompts": ["mueve"], "image_prompts": ["foto"], "voz_clip": "voz", "render_engine": "veo",
                  "image_f8": {"persona": ["Daniel"]}}


def test_clip_existente_sin_foto_rehace_foto_y_no_el_clip(monkeypatch, tmp_path):
    clip, cap = _cap_clip(tmp_path, monkeypatch)
    madre = tmp_path / "m.png"
    madre.write_bytes(_png())
    pedidos = []

    def fake(prompt, art, path, ultra, **kw):
        pedidos.append(kw)
        Path(path).write_bytes(b"f")
        return {"flux_meta": {"motor": "nb2_lite", "respaldo_motivo": None, "segundos": 1.0, "usd": 0.042}}

    monkeypatch.setattr(am, "_generate_flux_image_at", fake)
    monkeypatch.setattr(am, "foto_final_del_clip", lambda *a, **k: {"path": clip.with_name("f.png"), "ssim": 0.5, "motivo": None})
    monkeypatch.setattr(am, "_generate_clip", lambda *a, **k: pytest.fail("no se regenera el clip"))
    r = am._process_veo_chapter(cap, "v", {"Daniel": str(madre)}, {}, {})
    fila = r["clips"][0]
    assert fila["status"] == "skipped_exists" and fila["foto_de_arranque_cambio"] and fila["motor"] == "nb2_lite"
    assert fila["foto_madre_refs"] == ["Daniel"] and len(pedidos[0]["foto_madre_data_uris"]) == 1
    assert clip.read_bytes() == b"clip"


def test_clip_y_foto_existentes_no_gastan(monkeypatch, tmp_path):
    clip, cap = _cap_clip(tmp_path, monkeypatch)
    (clip.parent / "ch01_img_01.png").write_bytes(b"f")
    monkeypatch.setattr(am, "_generate_flux_image_at", lambda *a, **k: pytest.fail("no se paga"))
    assert "foto_de_arranque_cambio" not in am._process_veo_chapter(cap, "v", {}, {}, {})["clips"][0]


def test_supps_en_orden_y_con_motor(monkeypatch, tmp_path):
    monkeypatch.setattr(am, "OUTPUT_DIR", tmp_path)

    def fake(prompt, art, path, ultra, **kw):
        Path(path).write_bytes(b"f")
        return {"flux_meta": {"motor": am.MOTOR_RESPALDO, "respaldo_motivo": "m", "segundos": 1.0, "usd": 0.04}}

    monkeypatch.setattr(am, "_generate_flux_image_at", fake)
    cap = {"id": "ch01", "supplemental_image_prompts": [{"prompt": f"p{i}"} for i in range(5)]}
    res = am._generate_supplementals_for_veo_chapter(cap, "v", "ch01", False)
    assert [r["index"] for r in res] == [1, 2, 3, 4, 5] and all(r["motor"] == am.MOTOR_RESPALDO for r in res)


def test_process_script_no_llama_a_la_secuencia(monkeypatch, tmp_path):
    monkeypatch.setattr(am, "OUTPUT_DIR", tmp_path)
    monkeypatch.setattr(am, "_pre_paso_secuencia", lambda *a, **k: pytest.fail("la secuencia queda sin uso"))
    monkeypatch.setattr(am, "_ensure_cost_tracking", lambda v: None)
    am.process_script({"video_id": "v", "video_type": "short", "chapters": []})
    assert select_profile(api.image_engine).render.secuencia is False


def test_prompt_de_madre_queda_en_disco(monkeypatch, tmp_path):
    import foto_madre
    dest = tmp_path / "daniel.png"
    foto_madre._guardar_prompt_madre(dest, "Retrato.", "modelo-x")
    assert (tmp_path / "daniel.prompt.txt").read_text(encoding="utf-8") == "modelo: modelo-x\n\nRetrato.\n"
