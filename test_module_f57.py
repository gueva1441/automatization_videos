# -*- coding: utf-8 -*-
"""F57 — foto final en todos los clips + la voz entera del clip. Sin red, US$ 0: Opus simulado (`video_prompt.escribir`,
`escribir_final`), fal simulado (el `Fal` de test_module_f53b_cadena), Seedream /edit simulado (`_generate_image_raw`),
ffmpeg simulado donde hace falta (`_ssim`). La narración es la copia congelada de A0 (`lab/hyperframes/f57/antes/`) con
la duración como parámetro (2,4 palabras/s de `guion_v4.PALABRAS_POR_SEG`: la narración F56 no tiene voz todavía)."""
import ast
import base64
import inspect
import json
from pathlib import Path

import pytest

import asset_manager as am
import engine_profiles as ep
from script_engine import m03_visual as m3
from script_engine import video_prompt as vp
from script_engine.guion_v4 import PALABRAS_POR_SEG
from test_module_f53b_cadena import EP, Fal, G, K, JPEG

ROOT = Path(__file__).resolve().parent
ANTES = ROOT / "lab" / "hyperframes" / "f57" / "antes" / "01b_narration.json"
LAB_PROMPTS = ROOT / "lab" / "hyperframes" / "f52" / "prompts_video.py"
PNG = b"\x89PNG\r\n\x1a\n" + b"\x00\x00\x00\rIHDR" + b"\x00" * 32
hay = pytest.mark.skipif(not ANTES.exists(), reason="sin lab/hyperframes/f57/antes/01b_narration.json")

# la tabla del handoff (simulación del analista, confirmada por el auditor; copia congelada, 2,4 palabras/s)
TABLA = {
    1: ("start", 834, 161, 99, 20,
        "Un hombre joven posa para un retrato con el pie vendado. Ese pie va a cerrar; lo que respira mientras"),
    7: ("end", 1266, 216, 112, 21,
        "respiró allí. Wittenoom ya no está en el mapa. ¿Qué respiró en diez meses que tardó casi treinta años en matarlo?"),
}


def _narracion(cap: int) -> str:
    d = json.loads(ANTES.read_text(encoding="utf-8"))
    return next(c for c in d["chapters"] if c["chapter_number"] == cap)["narration"]


def _ventana(narracion: str) -> int:
    """La ventana en caracteres como la calcula `_process_one_cap` (m03), con la duración = palabras / 2,4."""
    dur = len(narracion.split()) / PALABRAS_POR_SEG
    v = int(m3.VEO_CLIP_DURATION_SEC * (len(narracion) / dur))
    return max(1, min(v, len(narracion) - 1))


# ═══════════════════════════════════════════════ A1 · voz_del_clip ═══════════════════════════════════════════════

@hay
@pytest.mark.parametrize("cap", [1, 7])
def test_voz_del_clip_los_dos_de_la_tabla(cap):
    pos, car, pal, ventana, pal_clip, voz = TABLA[cap]
    n = _narracion(cap)
    assert (len(n), len(n.split())) == (car, pal)
    assert _ventana(n) == ventana
    out = m3.voz_del_clip(n, pos, ventana)
    assert out == voz and len(out.split()) == pal_clip
    assert out in n                                                      # corte por palabra, sin agregar ni quitar


def test_voz_del_clip_bordes():
    n = "Una. Dos tres.  Cuatro"
    assert m3.voz_del_clip(n, "start", 10_000) == n                     # ventana ≥ narración → entera
    assert m3.voz_del_clip(n, "end", 10_000) == n
    assert m3.voz_del_clip(n, "start", 1) == "Una."                      # la palabra que empieza antes del carácter 1
    assert m3.voz_del_clip(n, "end", 1) == "Cuatro"                      # la que termina después de len − 1
    assert m3.voz_del_clip(n, "start", 7) == "Una. Dos"                  # «tres.» empieza en 9 → fuera
    assert m3.voz_del_clip(n, "end", 7) == "Cuatro"                      # «tres.» termina en 14 ≤ 22 − 7 → fuera
    assert m3.voz_del_clip("", "start", 5) == ""
    assert m3.voz_del_clip("   ", "end", 5) == ""


def test_render_veo_guarda_voz_clip_y_el_movimiento_la_recibe(monkeypatch):
    """`_render_prompts_seedream_veo` calcula `voz_clip` con la ventana que le pasa `_process_one_cap`, se la da a
    `_seedream_video_prompt` en lugar del ancla y la guarda en el cap; `narration_anchor` sigue siendo el veo_anchor."""
    n = "Un hombre joven posa. Ese pie va a cerrar; lo que respira mientras tanto es otra cosa. Fin del cap."
    visto = {}
    monkeypatch.setattr(m3, "_render_prompts_seedream",
                        lambda *a, **k: {"image_prompts": [{"prompt": "FOTO", "narration_anchor": "Un hombre joven posa."},
                                                           {"prompt": "S1", "narration_anchor": "Fin del cap."}]})
    monkeypatch.setattr(m3, "_seedream_video_prompt", lambda ip, voz, label: visto.update(voz=voz) or "MOV")
    plan = {"veo_anchor": {"anchor": "Un hombre joven posa.", "pos": 0, "end": 21}, "supplementals": [{"anchor": "Fin del cap."}]}
    out = m3._render_prompts_seedream_veo({}, {}, n, plan, "start", 1, 30)
    assert out["voz_clip"] == "Un hombre joven posa. Ese pie" == visto["voz"]   # «va» empieza en 30 → fuera
    assert out["narration_anchor"] == "Un hombre joven posa." and out["video_prompt"] == "MOV"
    assert inspect.signature(m3._render_prompts_seedream_veo).parameters.__contains__("veo_zone_chars")


def test_camino_de_la_clave_m06_y_fase2a():
    """m03 → 03_visual.json → m06_assembler (suma `voz_clip`; `narration_anchor` se queda) → fase2a._normalize_long
    (`voz_clip` en lugar de `narration_anchor`) → chapter["voz_clip"]."""
    import fase2a
    from script_engine import m06_assembler as m6
    src6 = inspect.getsource(m6)
    assert 'cap_out["voz_clip"] = vis.get("voz_clip", "")' in src6 and 'cap_out["narration_anchor"]' in src6
    script = {"topic_id": "v", "chapters": [{"chapter_number": 1, "narration": "n", "render_engine": "veo",
                                             "image_prompt": "ip", "video_prompt": "vp", "voz_clip": "la voz",
                                             "narration_anchor": "ancla", "veo_position": "start"}]}
    ch = fase2a._normalize_long(script)["chapters"][0]
    assert ch["voz_clip"] == "la voz" and "narration_anchor" not in ch


# ═══════════════════════════════════════════════ A4 · los 3 PEDIDO ═══════════════════════════════════════════════

def _pedido_lab() -> str:
    arbol = ast.parse(LAB_PROMPTS.read_text(encoding="utf-8"))
    for nodo in arbol.body:
        if isinstance(nodo, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "PEDIDO" for t in nodo.targets):
            return ast.literal_eval(nodo.value)
    raise AssertionError("PEDIDO no está en el lab")


def test_pedido_byte_a_byte_igual():
    assert vp.PEDIDO.encode("utf-8") == _pedido_lab().encode("utf-8")


PEDIDO_CON_FINAL = """You write the motion prompt for an image-to-video model. The first attached image is the first frame and the second attached image is the last frame: the shot goes from one to the other. Follow the model guide below exactly; it decides structure, length and closing lines.
MODEL GUIDE:
{ficha}
FIRST FRAME: the first attached image. Where it differs from the still image prompt (framing, pose, what is visible), describe the motion from the image as it is.
LAST FRAME: the second attached image. Describe the motion that ends exactly on it.
STILL IMAGE PROMPT (what the first frame was asked to show):
{prompt_foto}
NARRATION DURING THE CLIP (Spanish):
{ancla}
APPROVED MOTION (keep its intent, rewrite it for this model):
{video_prompt_vivo}
Clip length: {segundos} seconds, one continuous shot, no cuts, no dialogue, no music, no on-screen text.
Return only the prompt text."""

PEDIDO_FINAL = """You write an edit instruction for an image-editing model. The attached image is the first frame of a {segundos}-second continuous documentary shot. Write the instruction that turns it into the last frame of that same shot.
The last frame keeps the same place, the same people with the same faces, bodies and clothes, the same light and the same photographic style; it changes only what changes during those seconds, following the narration.
STILL IMAGE PROMPT (what the first frame was asked to show):
{prompt_foto}
NARRATION DURING THE SHOT (Spanish; the last frame shows the moment at its end):
{voz_clip}
Return only the edit instruction: one paragraph of plain English prose describing the last frame."""


def test_pedidos_nuevos_integros_con_segundos():
    assert vp.PEDIDO_CON_FINAL == PEDIDO_CON_FINAL and vp.PEDIDO_FINAL == PEDIDO_FINAL
    seg = f"{m3.VEO_CLIP_DURATION_SEC:g}"
    t = vp.armar_pedido(ep.PERFIL_VIDEO_G, "P", "la voz", "mov", foto_final=b"x")
    assert t == PEDIDO_CON_FINAL.format(ficha=ep.PERFIL_VIDEO_G.ficha, prompt_foto="P", ancla="la voz",
                                        video_prompt_vivo="mov", segundos=seg)
    assert f"Clip length: {seg} seconds" in t and "{segundos}" not in t
    assert vp.armar_pedido(ep.PERFIL_VIDEO_G, "P", "la voz", "mov") == vp.PEDIDO.format(
        ficha=ep.PERFIL_VIDEO_G.ficha, prompt_foto="P", ancla="la voz", video_prompt_vivo="mov")
    b = vp.armar_body_final(JPEG, "P", "la voz")
    assert b["messages"][0]["content"][1]["text"] == PEDIDO_FINAL.format(prompt_foto="P", voz_clip="la voz", segundos=seg)
    assert "APPROVED MOTION" not in b["messages"][0]["content"][1]["text"]            # F58 A8: sin el movimiento
    assert b["messages"][0]["content"][1]["text"].startswith(f"You write an edit instruction for an image-editing model. "
                                                              f"The attached image is the first frame of a {seg}-second")


def test_armar_body_con_dos_imagenes_en_orden():
    b = vp.armar_body(ep.PERFIL_VIDEO_K, JPEG, "P", "la voz", "mov", foto_final=PNG)
    c = b["messages"][0]["content"]
    assert [x["type"] for x in c] == ["image", "image", "text"]
    assert (c[0]["source"]["media_type"], c[1]["source"]["media_type"]) == ("image/jpeg", "image/png")
    assert c[0]["source"]["data"] == base64.b64encode(JPEG).decode() and c[1]["source"]["data"] == base64.b64encode(PNG).decode()
    assert "LAST FRAME: the second attached image." in c[2]["text"]
    sin = vp.armar_body(ep.PERFIL_VIDEO_K, JPEG, "P", "la voz", "mov")
    assert [x["type"] for x in sin["messages"][0]["content"]] == ["image", "text"]
    assert "LAST FRAME" not in sin["messages"][0]["content"][1]["text"]
    assert sin["model"] == b["model"] and sin["output_config"] == b["output_config"]


def test_escribir_final_misma_llamada_que_escribir(monkeypatch):
    """`escribir_final` y `escribir` comparten `_llamar` (factorizado, no copiado): mismo modelo, mismo reintento."""
    import claude_helpers
    bodies, tracks = [], []
    monkeypatch.setattr(claude_helpers, "_track", lambda m, u, d: tracks.append(d) or 0.0)
    resp = {"model": "claude-opus-5-5", "stop_reason": "end_turn", "usage": {},
            "content": [{"type": "text", "text": "  the last frame shows…  "}]}
    out = vp.escribir_final(JPEG, "P", "la voz", post=lambda b: bodies.append(b) or resp)
    assert out == "the last frame shows…" and tracks == ["video_prompt:final"]
    assert [x["type"] for x in bodies[0]["messages"][0]["content"]] == ["image", "text"]
    assert bodies[0]["model"] == vp.MODELO_CASILLEROS
    assert inspect.getsource(vp).count("for attempt in range(1, claude_helpers.MAX_ATTEMPTS + 1)") == 1


# ═══════════════════════════════════════════ A3 + A5 · payload y cadena ═══════════════════════════════════════════

def test_campo_imagen_final_g_y_k():
    assert ep.PERFIL_VIDEO_G.campo_imagen_final == ep.PERFIL_VIDEO_K.campo_imagen_final == "end_image_url"


@pytest.fixture
def entorno(monkeypatch, tmp_path):
    monkeypatch.setattr(am.api, "video_engines", (G, K), raising=False)
    monkeypatch.setattr(am.api, "video_resolution", "1080p", raising=False)
    monkeypatch.setattr(am.api, "fal_api_key", "test-falsa", raising=False)
    escritos = []

    def escribir(perfil, foto, image_prompt, ancla, intento, *, foto_final=None, post=None, description=None):
        escritos.append({"perfil": perfil.engine_key, "foto": foto, "foto_final": foto_final, "ancla": ancla})
        return f"PROMPT {perfil.engine_key}"
    monkeypatch.setattr(vp, "escribir", escribir)
    monkeypatch.setattr(am, "_quitar_audio", lambda p: None)
    monkeypatch.setattr(am, "_clip_ffprobe", lambda p: {"segundos": 8.0, "ancho": 1920, "alto": 1080, "audio": False})
    monkeypatch.setattr(am.cost_tracker, "track_video", lambda *a, **k: None)
    monkeypatch.setattr(am.time, "sleep", lambda s: None)
    foto, final = tmp_path / "ch01_img_01.png", tmp_path / "ch01_img_01_final.png"
    foto.write_bytes(JPEG)
    final.write_bytes(PNG)

    def con_fal(guion):
        fal = Fal(am.api.fal_base_url, guion)
        monkeypatch.setattr(am.requests, "post", fal.post)
        monkeypatch.setattr(am.requests, "get", fal.get)
        return fal
    return {"foto": foto, "final": final, "out": tmp_path / "clips" / "ch01_clip_01.mp4", "escritos": escritos,
            "con_fal": con_fal}


def _dir(p: Path) -> Path:
    p.mkdir(parents=True, exist_ok=True)
    return p


def _posts_a(fal, motor):
    return [p[1] for p in fal.posts if p[0].endswith(EP[motor])]


def test_payload_con_end_image_url_en_g_y_k_y_las_mismas_dos_fotos_si_g_rechaza(entorno):
    e = entorno
    fal = e["con_fal"]({G: ["rechazo"], K: ["ok"]})
    am._generate_clip(e["foto"], "mov", e["out"], image_prompt="ip", ancla="la voz", foto_final=e["final"])
    pg, pk = _posts_a(fal, G)[0], _posts_a(fal, K)[0]
    jpeg_uri = "data:image/jpeg;base64," + base64.b64encode(JPEG).decode()
    png_uri = "data:image/png;base64," + base64.b64encode(PNG).decode()
    assert pg["image_url"] == jpeg_uri and pg["end_image_url"] == png_uri
    assert pk["start_image_url"] == jpeg_uri and pk["end_image_url"] == png_uri
    assert set(pg) == {"prompt", "duration", "resolution", "image_url", "end_image_url"}
    assert set(pk) == {"prompt", "duration", "resolution", "start_image_url", "end_image_url"}
    assert [(x["perfil"], x["foto_final"], x["ancla"]) for x in e["escritos"]] == [(G, e["final"], "la voz"),
                                                                                    (K, e["final"], "la voz")]


def test_payload_sin_end_image_url_cuando_no_hay_final(entorno):
    e = entorno
    fal = e["con_fal"]({G: ["ok"], K: []})
    am._generate_clip(e["foto"], "mov", e["out"], image_prompt="ip", ancla="la voz")
    pg = _posts_a(fal, G)[0]
    assert "end_image_url" not in pg and set(pg) == {"prompt", "duration", "resolution", "image_url"}
    assert e["escritos"][0]["foto_final"] is None


def test_path_to_data_uri_lee_el_tipo_de_los_bytes(tmp_path):
    p = tmp_path / "x.png"
    p.write_bytes(JPEG)                                                   # JPEG con extensión .png (Seedream)
    assert am._path_to_data_uri(str(p)).startswith("data:image/jpeg;base64,")
    p.write_bytes(PNG)
    assert am._path_to_data_uri(p).startswith("data:image/png;base64,")


# ═══════════════════════════════════════════ A5 · foto_final_del_clip ═══════════════════════════════════════════

def test_foto_final_reusa_la_existente_sin_llamar_a_nada(monkeypatch, tmp_path):
    monkeypatch.setattr(vp, "escribir_final", lambda *a, **k: pytest.fail("no se llama a Opus"))
    monkeypatch.setattr(am, "_generate_image_raw", lambda *a, **k: pytest.fail("no se llama al edit"))
    monkeypatch.setattr(am, "_ssim", lambda a, b: 0.91)
    ini, fin = tmp_path / "ch01_img_01.png", tmp_path / "ch01_img_01_final.png"
    ini.write_bytes(JPEG)
    fin.write_bytes(PNG)
    out = am.foto_final_del_clip(ini, "ip", "la voz", fin)
    assert out == {"path": fin, "ssim": 0.91, "instruccion": None, "motivo": "reusada: ya existía"}


def test_foto_final_edit_con_la_inicial_de_referencia(monkeypatch, tmp_path):
    visto = {}

    def escribir_final(foto, image_prompt, voz_clip, *, post=None, description=None):          # F58 A8: sin movimiento
        visto.update(foto=foto, ip=image_prompt, voz=voz_clip)
        return "the last frame: he lowers the bandaged foot"

    def raw(prompt, out_path, use_ultra, seed=None, foto_madre_data_uris=None):
        visto.update(prompt=prompt, use_ultra=use_ultra, uris=foto_madre_data_uris)
        out_path.write_bytes(PNG)
        return {"endpoint": "fal-ai/bytedance/seedream/v5/lite/edit"}
    monkeypatch.setattr(vp, "escribir_final", escribir_final)
    monkeypatch.setattr(am, "_generate_image_raw", raw)
    monkeypatch.setattr(am, "_ssim", lambda a, b: 0.87)
    ini, fin = tmp_path / "ch01_img_01.png", tmp_path / "ch01_img_01_final.png"
    ini.write_bytes(JPEG)
    out = am.foto_final_del_clip(ini, "ip", "la voz", fin, use_ultra=True)
    assert out == {"path": fin, "ssim": 0.87, "instruccion": "the last frame: he lowers the bandaged foot", "motivo": None}
    assert (visto["foto"], visto["ip"], visto["voz"]) == (ini, "ip", "la voz") and "mov" not in visto
    assert visto["prompt"] == out["instruccion"] and visto["use_ultra"] is True
    assert visto["uris"] == ["data:image/jpeg;base64," + base64.b64encode(JPEG).decode()]    # el tipo de los bytes
    assert fin.exists()


def test_foto_final_rechazada_clip_sin_final_y_motivo(monkeypatch, tmp_path):
    monkeypatch.setattr(vp, "escribir_final", lambda *a, **k: "instr")

    def raw(prompt, out_path, use_ultra, seed=None, foto_madre_data_uris=None):
        raise am.ContentRejectedError("seedream rechazó prompt: content_policy_violation")
    monkeypatch.setattr(am, "_generate_image_raw", raw)
    ini, fin = tmp_path / "ch01_img_01.png", tmp_path / "ch01_img_01_final.png"
    ini.write_bytes(JPEG)
    out = am.foto_final_del_clip(ini, "ip", "la voz", fin)
    assert out["path"] is None and out["ssim"] is None and out["instruccion"] == "instr"
    assert out["motivo"] == "rechazo: seedream rechazó prompt: content_policy_violation"     # literal, sin suavizar
    assert not fin.exists()


def test_proceso_veo_sin_voz_clip_para(monkeypatch):
    monkeypatch.setattr(am, "_chapter_dir", lambda *a: pytest.fail("no llega a los directorios"))
    ch = {"id": "ch01", "video_prompts": ["mov"], "image_prompts": ["ip"], "narration_anchor": "ancla", "art_profile": ""}
    with pytest.raises(ValueError, match="cap sin voz_clip: correr m03 de nuevo"):
        am._process_veo_chapter(ch, "v")
    src = inspect.getsource(am._process_veo_chapter)
    assert 'chapter.get("narration_anchor")' not in src                   # la lectura del ancla se borró


def test_proceso_veo_foto_final_antes_del_clip_y_clip_results(monkeypatch, tmp_path):
    llamadas = []
    monkeypatch.setattr(am, "_chapter_dir", lambda vid, cid, kind: _dir(tmp_path / kind))
    monkeypatch.setattr(am, "OUTPUT_DIR", tmp_path)
    monkeypatch.setattr(am, "_generate_flux_image_at", lambda p, a, path, u: path.write_bytes(JPEG))
    monkeypatch.setattr(am, "_generate_supplementals_for_veo_chapter", lambda *a: [])

    def final(ini, ip, voz, out, *, use_ultra=False):
        llamadas.append(("final", ini.name, voz, out.name, use_ultra))
        out.write_bytes(PNG)
        return {"path": out, "ssim": 0.9, "instruccion": "i", "motivo": None}

    def clip(foto, mov, out, *, image_prompt="", ancla="", foto_final=None, log=None):
        llamadas.append(("clip", foto.name, ancla, foto_final.name if foto_final else None))
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(b"mp4")
        return out
    monkeypatch.setattr(am, "foto_final_del_clip", final)
    monkeypatch.setattr(am, "_generate_clip", clip)
    ch = {"id": "ch01", "video_prompts": ["mov"], "image_prompts": ["ip"], "voz_clip": "la voz entera", "art_profile": ""}
    res = am._process_veo_chapter(ch, "v")
    assert llamadas == [("final", "ch01_img_01.png", "la voz entera", "ch01_img_01_final.png", True),
                        ("clip", "ch01_img_01.png", "la voz entera", "ch01_img_01_final.png")]
    c = res["clips"][0]
    assert (c["status"], c["ssim"], c["motivo_sin_final"]) == ("ok", 0.9, None)
    assert c["path"].endswith("ch01_clip_01.mp4") and c["foto_final"].endswith("ch01_img_01_final.png")
    # QA Studio toma el primer `{cap}_img_*.png` en orden: la inicial va antes que la _final
    assert sorted((tmp_path / "veo").glob("ch01_img_*.png"))[0].name == "ch01_img_01.png"


def test_proceso_veo_sin_final_el_clip_sale_con_la_inicial(monkeypatch, tmp_path):
    monkeypatch.setattr(am, "_chapter_dir", lambda vid, cid, kind: _dir(tmp_path / kind))
    monkeypatch.setattr(am, "OUTPUT_DIR", tmp_path)
    monkeypatch.setattr(am, "_generate_flux_image_at", lambda p, a, path, u: path.write_bytes(JPEG))
    monkeypatch.setattr(am, "_generate_supplementals_for_veo_chapter", lambda *a: [])
    monkeypatch.setattr(am, "foto_final_del_clip",
                        lambda *a, **k: {"path": None, "ssim": None, "instruccion": "i", "motivo": "rechazo: x"})
    visto = {}

    def clip(foto, mov, out, *, image_prompt="", ancla="", foto_final=None, log=None):
        visto["foto_final"] = foto_final
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(b"mp4")
        return out
    monkeypatch.setattr(am, "_generate_clip", clip)
    ch = {"id": "ch03", "video_prompts": ["mov"], "image_prompts": ["ip"], "voz_clip": "voz", "art_profile": ""}
    c = am._process_veo_chapter(ch, "v")["clips"][0]
    assert visto["foto_final"] is None
    assert (c["status"], c["foto_final"], c["ssim"], c["motivo_sin_final"]) == ("ok", None, None, "rechazo: x")


# F59 A3: QA Studio ya no llama `generate_veo_fn(first_frame, video_prompt, out_clip)`: `_clipfix_core` edita el movimiento con
# Opus y pasa `foto_final` y `ancla=voz_clip` a `_generate_clip` (lo cubre test_qa_studio.py). El test «sigue con 3 posicionales
# y sin final» se borró con el camino viejo (lo viejo se borra con sus tests).
