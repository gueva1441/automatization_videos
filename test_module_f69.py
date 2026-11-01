"""F69 — QA Studio: la foto de arranque del clip se puede rehacer. Sin red: todas las deps inyectadas, como los de F59."""
from __future__ import annotations

import hashlib
import inspect
import json

import pytest

import qa_studio_server as qa
from test_qa_studio import (TID, _cap03, _cap_vivo, _fake_armar_item, _opus_casilleros, _Rejected, _TOPIC, build_topic)

CAS = {"subject": "A lean miner", "action": "Posing for a family portrait", "setting": "A yard, 1963", "lighting": "Hard sun",
       "camera_angle": "eye-level", "lens_technique": "50mm", "shot_scale": "medium",
       "text_in_image": {"present": False, "text": "", "font": "", "location": ""}, "people_group": ["g1"], "year": "1963"}
TS = "20261101_000000"
VIDEO_PROMPT = "Static camera with subtle upward drift over the skyline"


def _armar(tmp_path):
    """El fixture de QA con la forma real de un cap con clip: `image_prompt` + `image_f8`, sin `image_prompts`; más el manifest."""
    build_topic(tmp_path)
    f8 = {"beat": 1, "motivos": [], "raw_llm_prompt": json.dumps(CAS), "anio": "1963", "anio_fuente": "x",
          "people_group": ["g1"], "persona": ["Daniel"], "shot_scale": "medium", "camera_angle": "eye-level",
          "lens_technique": "50mm", "_f8_slots_scrub": ["viejo"]}
    vivo = tmp_path / "data" / "scripts" / f"{TID}.json"
    vis = tmp_path / "data" / "scripts" / "_steps" / TID / "03_visual.json"
    for f in (vivo, vis):
        d = json.loads(f.read_text(encoding="utf-8"))
        next(c for c in d["chapters"] if c["chapter_number"] == 1)["image_f8"] = f8
        if f == vis:
            next(c for c in d["chapters"] if c["chapter_number"] == 1)["image_sensible"] = True
        f.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    st = qa.QAState(TID, base_dir=tmp_path)
    veo = st.assets_dir / "ch01_veo"
    (veo / "ch01_img_01.png").write_bytes(b"FOTO_VIEJA")
    (veo / "ch01_img_01_native.png").write_bytes(b"NATIVA_VIEJA")
    (veo / "ch01_img_01.llamada.json").write_text("{}", encoding="utf-8")
    (veo / "ch01_img_01_final.png").write_bytes(b"FINAL_VIEJA")
    (veo / "ch01_clip_01.mp4").write_bytes(b"CLIP_VIEJO")
    man = {"papel_md5": "sello", "generated_at": "fecha", "chapters": [
        {"id": "ch01", "engine": "veo", "clips": [{"index": 1, "video_prompt": "viejo", "image_prompt": "viejo", "status": "skipped_exists",
                                                  "foto_de_arranque_cambio": True, "foto_arranque_md5": "viejo", "motor": "nb2_lite"}]},
        {"id": "ch02", "engine": "flux", "images": [{"prompt": "intacta"}]}]}
    (st.assets_dir / "assets_manifest.json").write_text(json.dumps(man), encoding="utf-8")
    return st


def _deps(*, foto=None, final=None, clip=None):
    """Las deps de `_fotoclip_core`, con un registro de quién corrió y en qué orden."""
    from script_engine import m03_visual
    orden, seen = [], {}

    def generate(prompt, art, out, use_ultra=False, seed=None, foto_madre_data_uris=None):
        orden.append("foto")
        seen.update(prompt=prompt, out=out, uris=foto_madre_data_uris)
        out.write_bytes(b"FOTO_NUEVA")
        return {"flux_meta": {"motor": "nb2_lite", "respaldo_motivo": None, "segundos": 9.0, "usd": 0.042}}

    def foto_final(inicial, image_prompt, voz, out, *, use_ultra=False):
        orden.append("final")
        seen.update(final_existia=out.exists(), final_prompt=image_prompt, final_inicial=inicial.read_bytes())
        out.write_bytes(b"FINAL_NUEVA")
        return {"path": out, "ssim": 0.5, "instruccion": "x", "motivo": None}

    def genera_clip(f, mov, out, *, image_prompt="", ancla="", foto_final=None, log=None):
        orden.append("clip")
        seen.update(mov=mov, clip_foto=f.read_bytes(), clip_final=foto_final, ancla=ancla, clip_prompt=image_prompt)
        out.write_bytes(b"CLIP_NUEVO")
        log.append({"clip": out.name, "motor": "gemini_omni_flash", "rechazos": [], "segundos": 8.0, "usd": 1.2})
        return out

    return dict(generate_fn=foto or generate, foto_final_fn=final or foto_final, generate_clip_fn=clip or genera_clip,
                llamar_fn=_opus_casilleros({"action": "Standing alone"}), retry_fn=m03_visual._call_with_validation_retry,
                armar_item_fn=_fake_armar_item, topic_fn=lambda tid: _TOPIC, seed_fn=lambda v, s: 1, is_hook_fn=lambda c: c == "ch01",
                data_uri_fn=lambda p: f"uri:{p}", madres_fn=lambda *a: [("Daniel", "madre.png")], content_rejected_exc=_Rejected,
                now_ts=TS), orden, seen


def test_cap_con_clip_expone_la_foto_sin_agregar_segmentos(tmp_path):
    st = _armar(tmp_path)
    antes = len(st.cap(1)["segments"])
    for n in (1, 7):
        c = st.cap(n)
        s = next(x for x in c["segments"] if x["is_clip"])
        assert s["foto_img_name"] == f"ch{n:02d}_img_01.png" and s["foto_url"] == f"/img?cap=ch{n:02d}&name=ch{n:02d}_img_01.png"
        assert s["img_name"] is None
        assert c["count"] == sum(1 for x in c["segments"] if not x["is_clip"])
    assert len(st.cap(1)["segments"]) == antes


def test_cap_con_clip_sin_foto_no_ofrece_rehacer(tmp_path):
    st = _armar(tmp_path)
    (st.assets_dir / "ch01_veo" / "ch01_img_01.png").unlink()
    assert "foto_img_name" not in next(x for x in st.cap(1)["segments"] if x["is_clip"])


def test_resolve_fix_entry_lee_la_foto_del_clip(tmp_path):
    st = _armar(tmp_path)
    e = st.resolve_fix_entry("ch01_img_01.png")
    assert e["clip"] is True and e["casilleros"] == CAS and e["anio"] == "1963" and e["persona"] == ["Daniel"]
    assert e["prompt"].startswith("A wide panoramic") and e["narration_anchor"] == "apertura del cap 1"
    assert st.resolve_fix_entry("ch01_supp_01.png")["clip"] is False
    assert st.resolve_fix_entry("ch02_img_01.png")["clip"] is False


def test_cadena_foto_final_clip_en_orden_y_con_el_movimiento_aprobado(tmp_path):
    st = _armar(tmp_path)
    work = tmp_path / "output" / TID / "_fase2b_work"
    work.mkdir(parents=True, exist_ok=True)
    (work / "ch01_hybrid_visual.mp4").write_bytes(b"OLD")
    deps, orden, seen = _deps()
    opus = deps["llamar_fn"]
    ok, txt = qa._fotoclip_core(st, TID, "ch01", "solo Daniel", **deps)
    assert ok is True, txt
    assert orden == ["foto", "final", "clip"]
    assert opus.calls[0]["prompt"].endswith("PEDIDO DE OMAR:\nsolo Daniel") and len(opus.calls) == 1
    # la foto vieja no se reusa en ningún paso; el clip recibe la foto y la final nuevas y el video_prompt sin cambios
    assert seen["final_existia"] is False and seen["final_inicial"] == b"FOTO_NUEVA" and seen["clip_foto"] == b"FOTO_NUEVA"
    assert seen["mov"] == VIDEO_PROMPT and seen["ancla"] == "voz del clip uno" and seen["clip_final"].read_bytes() == b"FINAL_NUEVA"
    assert "Standing alone" in seen["final_prompt"] and seen["final_prompt"] == seen["clip_prompt"]
    assert seen["uris"] == ["uri:madre.png"] and seen["out"] == st.assets_dir / "ch01_veo" / "ch01_img_01.png"
    assert not (work / "ch01_hybrid_visual.mp4").exists()
    assert "gemini_omni_flash" in txt


def test_lo_viejo_queda_en_backup(tmp_path):
    st = _armar(tmp_path)
    deps, _, _ = _deps()
    assert qa._fotoclip_core(st, TID, "ch01", "p", **deps)[0]
    b = st.assets_dir / "_qa_backups"
    esperado = {"ch01_img_01.png": b"FOTO_VIEJA", "ch01_img_01_native.png": b"NATIVA_VIEJA", "ch01_img_01_final.png": b"FINAL_VIEJA",
                "ch01_clip_01.mp4": b"CLIP_VIEJO"}
    for nombre, datos in esperado.items():
        sufijo = nombre[nombre.rindex("."):]
        assert (b / f"{nombre}.{TS}.bak{sufijo}").read_bytes() == datos
    for nombre in ("03_visual.json", f"{TID}.json", "assets_manifest.json", "ch01_img_01.llamada.json"):
        assert (b / f"{nombre}.{TS}.bak.json").exists()


def test_guion_y_03_guardan_el_item_con_la_forma_del_cap_con_clip(tmp_path):
    st = _armar(tmp_path)
    deps, _, _ = _deps()
    sello = json.loads(st.script_path.read_text(encoding="utf-8")).get("papel_md5")
    assert qa._fotoclip_core(st, TID, "ch01", "p", **deps)[0]
    for c in (_cap03(tmp_path, 1), _cap_vivo(tmp_path, 1)):
        assert "Standing alone" in c["image_prompt"] and "image_prompts" not in c
        assert json.loads(c["image_f8"]["raw_llm_prompt"])["action"] == "Standing alone"
        assert c["image_f8"]["persona"] == ["Daniel"] and "_f8_slots_scrub" not in c["image_f8"] and "prompt" not in c["image_f8"]
        assert c["video_prompt"] == VIDEO_PROMPT and c["voz_clip"] == "voz del clip uno"
    assert _cap03(tmp_path, 1)["image_sensible"] is False and "image_sensible" not in _cap_vivo(tmp_path, 1)
    assert json.loads(st.script_path.read_text(encoding="utf-8")).get("papel_md5") == sello


def test_manifest_solo_cambia_la_fila_del_clip(tmp_path):
    st = _armar(tmp_path)
    mpath = st.assets_dir / "assets_manifest.json"
    antes = json.loads(mpath.read_text(encoding="utf-8"))
    deps, _, _ = _deps()
    assert qa._fotoclip_core(st, TID, "ch01", "p", **deps)[0]
    man = json.loads(mpath.read_text(encoding="utf-8"))
    fila = man["chapters"][0]["clips"][0]
    assert fila["foto_arranque_md5"] == hashlib.md5(b"FOTO_NUEVA").hexdigest()
    assert fila["foto_final_md5"] == hashlib.md5(b"FINAL_NUEVA").hexdigest()
    assert "foto_de_arranque_cambio" not in fila and fila["status"] == "ok" and fila["video_prompt"] == VIDEO_PROMPT
    assert fila["clip_motor"] == "gemini_omni_flash" and fila["clip_usd"] == 1.2 and fila["usd"] == 0.042
    assert "Standing alone" in fila["image_prompt"]
    assert man["chapters"][1] == antes["chapters"][1]
    assert {k: man[k] for k in ("papel_md5", "generated_at")} == {k: antes[k] for k in ("papel_md5", "generated_at")}


def test_foto_sin_grade(tmp_path):
    """El video usa el clip: la foto de arranque no lleva `_graded` (como producción, `_apply_grade` no la mira)."""
    st = _armar(tmp_path)
    deps, _, _ = _deps()
    assert qa._fotoclip_core(st, TID, "ch01", "p", **deps)[0]
    assert not (st.assets_dir / "ch01_veo" / "ch01_img_01_graded.png").exists()


def test_si_la_foto_falla_no_se_toca_nada_mas(tmp_path):
    st = _armar(tmp_path)

    def rechazo(*a, **k):
        raise _Rejected("no")
    deps, orden, _ = _deps(foto=rechazo)
    guion = st.script_path.read_bytes()
    man = (st.assets_dir / "assets_manifest.json").read_bytes()
    ok, txt = qa._fotoclip_core(st, TID, "ch01", "p", **deps)
    assert ok is False and txt.startswith("filtro:") and orden == []
    veo = st.assets_dir / "ch01_veo"
    assert (veo / "ch01_img_01_final.png").read_bytes() == b"FINAL_VIEJA" and (veo / "ch01_clip_01.mp4").read_bytes() == b"CLIP_VIEJO"
    assert st.script_path.read_bytes() == guion and (st.assets_dir / "assets_manifest.json").read_bytes() == man


def test_si_el_clip_lo_rechazan_el_mp4_viejo_queda_y_se_avisa(tmp_path):
    st = _armar(tmp_path)

    def rechazo(*a, **k):
        raise _Rejected("G y K")
    deps, _, _ = _deps(clip=rechazo)
    man = (st.assets_dir / "assets_manifest.json").read_bytes()
    ok, txt = qa._fotoclip_core(st, TID, "ch01", "p", **deps)
    assert ok is False and "foto nueva, pero el clip sigue siendo el viejo" in txt and "G y K" in txt
    assert (st.assets_dir / "ch01_veo" / "ch01_clip_01.mp4").read_bytes() == b"CLIP_VIEJO"
    assert (st.assets_dir / "assets_manifest.json").read_bytes() == man


def test_sin_foto_final_el_clip_sale_igual_y_se_dice(tmp_path):
    st = _armar(tmp_path)
    deps, orden, seen = _deps(final=lambda *a, **k: {"path": None, "ssim": None, "instruccion": None, "motivo": "rechazo: x"})
    ok, txt = qa._fotoclip_core(st, TID, "ch01", "p", **deps)
    assert ok is True and "Sin foto final: rechazo: x" in txt and seen["clip_final"] is None
    fila = json.loads((st.assets_dir / "assets_manifest.json").read_text(encoding="utf-8"))["chapters"][0]["clips"][0]
    assert fila["foto_final_md5"] is None and fila["motivo_sin_final"] == "rechazo: x"


def test_guion_viejo_no_gasta(tmp_path):
    build_topic(tmp_path, old_script=True)
    st = qa.QAState(TID, base_dir=tmp_path)
    deps, orden, _ = _deps()
    ok, txt = qa._fotoclip_core(st, TID, "ch01", "p", **deps)
    assert ok is False and txt == "guion viejo: correr m03 de nuevo" and orden == []


def test_rehacer_clip_y_fotos_comunes_siguen_igual():
    """Regla 2: «rehacer clip» no llama a la cadena. La ruta manda a la cadena solo la foto de arranque de un cap con clip."""
    assert "_fix_core" not in inspect.getsource(qa._clipfix_core)
    assert "_fotoclip" not in inspect.getsource(qa._clipfix_core)
    ruta = inspect.getsource(qa)
    assert 'img_name == f"{cap}_img_01.png"' in ruta
    assert "_start_fotoclip(cap, img_name, feedback) if es_foto_clip else _start_fix(cap, img_name, feedback)" in ruta


@pytest.mark.parametrize("nombre", ["fotoclip", "data-fotofix", "submitFotoClip", "foto_img_name"])
def test_la_pagina_muestra_la_foto_y_el_boton(nombre):
    assert nombre in (qa.BASE_DIR / "qa_studio.html").read_text(encoding="utf-8")


def test_ruta_manda_la_foto_del_clip_a_la_cadena_y_las_demas_al_fix(tmp_path, monkeypatch):
    import threading
    import urllib.request
    from http.server import ThreadingHTTPServer
    st = _armar(tmp_path)
    vistos = []
    monkeypatch.setattr(qa, "STATE", st)
    monkeypatch.setattr(qa, "_start_fotoclip", lambda c, n, f: vistos.append(("cadena", n)) or {"started": True})
    monkeypatch.setattr(qa, "_start_fix", lambda c, n, f: vistos.append(("fix", n)) or {"started": True})
    srv = ThreadingHTTPServer(("127.0.0.1", 0), qa.Handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        for cap, nombre in (("ch01", "ch01_img_01.png"), ("ch01", "ch01_supp_01.png"), ("ch02", "ch02_img_01.png")):
            pedido = urllib.request.Request(f"http://127.0.0.1:{srv.server_address[1]}/fix_image", method="POST",
                                            data=json.dumps({"cap": cap, "img_name": nombre, "feedback": "p"}).encode("utf-8"))
            urllib.request.build_opener(urllib.request.ProxyHandler({})).open(pedido, timeout=5).read()
    finally:
        srv.shutdown()
    assert vistos == [("cadena", "ch01_img_01.png"), ("fix", "ch01_supp_01.png"), ("fix", "ch02_img_01.png")]
