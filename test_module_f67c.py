# -*- coding: utf-8 -*-
"""F67c: candado río abajo. Papel aprobado P1 → artefactos sellados P1 → se aprueba P2 → `etapa_de` = voz y cada reuso de la tabla A se
niega; el audio con el mismo texto se reusa igual. Todo en tmp_path: DATA_DIR, OUTPUT_DIR, STEPS_DIR y topics_db monkeypatcheados."""
from __future__ import annotations

import inspect
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

import asset_manager as am
import fase1_5 as f15
import fase2b as fb
import run_pipeline as rp
from script_engine import aprobacion
from script_engine import m01d_particion as md
from script_engine import m06_assembler as m6
from test_module_f9 import _script as _script_audio  # noqa: F401
from test_module_f9 import fake_eleven  # noqa: F401

TID = "t"
TOPIC = {"id": TID, "video_title": "T"}


def _w(p: Path, obj) -> Path:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(obj if isinstance(obj, str) else json.dumps(obj, ensure_ascii=False), encoding="utf-8")
    return p


def _aprobar_papel(env, autor: str) -> str:
    """Un papel de esta narración, con `autor` en el contenido: otro autor = otro md5."""
    n3 = json.loads((env["d"] / "01b_narracion_v3.json").read_text(encoding="utf-8"))
    _w(env["d"] / "01e_pantalla.json", {"narracion_md5": md.md5_narracion(n3), "autor": autor, "beats": []})
    _w(env["d"] / "01e_pantalla.md", "# papel")
    return f15.aprobar_papel(TID, f"Omar {autor}")["md5"]


@pytest.fixture
def env(tmp_path, monkeypatch):
    data, out = tmp_path / "data", tmp_path / "output"
    sd = data / "scripts" / "_steps"
    d = sd / TID
    monkeypatch.setattr(f15, "STEPS_DIR", sd)
    monkeypatch.setattr(md, "STEPS_DIR", sd)
    monkeypatch.setattr(m6, "STEPS_DIR", sd)
    monkeypatch.setattr(m6, "SCRIPTS_DIR", data / "scripts")
    monkeypatch.setattr(m6, "TOPICS_DB", _w(data / "topics_db.json", {"topics": [TOPIC]}))
    monkeypatch.setattr(am, "DATA_DIR", data)
    monkeypatch.setattr(am, "OUTPUT_DIR", out)
    monkeypatch.setattr(am, "_ensure_cost_tracking", lambda v: None)
    monkeypatch.setattr(fb, "OUTPUT_DIR", out)
    monkeypatch.setattr(rp, "DATA_DIR", data)
    monkeypatch.setattr(rp, "OUTPUT_DIR", out)
    monkeypatch.setattr(rp, "_video_hecho", lambda t: False)
    monkeypatch.setattr(rp, "_packaged", lambda t: False)
    caps = [{"chapter_number": 1, "narration": "Ana llegó. La casa estaba a oscuras."}]
    _w(d / "01b_narracion_v3.json", {"topic_id": TID, "parrafos": [{"cap": 1, "beat": 1, "texto": caps[0]["narration"]}], "caps": caps})
    _w(d / "01b_narration.json", {"topic_id": TID, "chapters": caps})
    _w(d / "03_visual.json", {"chapters": [{"chapter_number": 1, "image_prompts": [{"prompt": "p"}]}]})
    _w(d / "01b_verificacion.json", {})
    f15.aprobar_narracion(TID, "Omar 2026-10-31")
    return {"d": d, "data": data, "out": out, "assets": out / TID / "assets", "work": out / TID / "_fase2b_work"}


def _script_normalizado(sello=None) -> dict:
    """Lo que fase2a le pasa a asset_manager: lista blanca, sin `papel_md5` (por eso asset_manager lee el archivo)."""
    s = {"video_id": TID, "topic_id": TID, "video_type": "long", "chapters": [
        {"id": "ch01", "text": "x", "render_engine": "flux", "art_profile": "", "image_prompts": ["una foto"]}]}
    return {**s, "papel_md5": sello} if sello else s


def _fake_flux(monkeypatch) -> list[Path]:
    hechos: list[Path] = []

    def gen(prompt, profile, path, use_ultra, seed=None, uris=None):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"png")
        hechos.append(path)
        return {"validated": True, "attempts": 1, "last_verdict": {}, "model_used": "fake"}
    monkeypatch.setattr(am, "_generate_flux_image_at", gen)
    monkeypatch.setenv("IMAGE_GRADE", "0")
    return hechos


# ═══════════════════════ m06 ═══════════════════════

def test_assemble_escribe_el_sello(env):
    sello = _aprobar_papel(env, "P1")
    out = json.loads(m6.assemble_final_script(TID).read_text(encoding="utf-8"))
    assert out["papel_md5"] == sello == m6.sello_vigente(TID)


@pytest.mark.parametrize("caso,motivo", [("sin_aprobar", "no está aprobado"), ("cambiado", "cambió después"), ("otra_narracion", "otra narración"),
                                         ("sin_papel", "no hay papel"), ("voz_distinta", "no viene de la narración aprobada"),
                                         ("narracion_sin_aprobar", "narración no está aprobada")])
def test_assemble_sin_papel_aprobado_vigente_no_escribe(env, caso, motivo):
    _aprobar_papel(env, "P1")
    f = env["d"] / "01e_pantalla.json"
    papel = json.loads(f.read_text(encoding="utf-8"))
    if caso == "sin_aprobar":
        papel.pop("aprobado")
    elif caso == "cambiado":
        papel["beats"] = [1]
    elif caso == "otra_narracion":
        papel["narracion_md5"] = "otra"
        papel["aprobado"]["md5"] = f15.md5_papel(papel)
    elif caso == "voz_distinta":
        _w(env["d"] / "01b_narration.json", {"chapters": [{"chapter_number": 1, "narration": "Otro texto."}]})
    elif caso == "narracion_sin_aprobar":
        n3 = json.loads((env["d"] / "01b_narracion_v3.json").read_text(encoding="utf-8"))
        n3.pop("aprobado")
        _w(env["d"] / "01b_narracion_v3.json", n3)
    if caso == "sin_papel":
        f.unlink()
    else:
        _w(f, papel)
    with pytest.raises(ValueError, match=motivo):
        m6.assemble_final_script(TID)
    assert not (env["data"] / "scripts" / f"{TID}.json").exists()


# ═══════════════════════ asset_manager ═══════════════════════

def test_lo_de_otro_papel_no_se_reusa_y_el_mismo_sello_si(env, monkeypatch):
    p1 = _aprobar_papel(env, "P1")
    hechos = _fake_flux(monkeypatch)
    png = env["assets"] / "ch01_flux" / "ch01_img_01.png"
    # fase2a pasa el normalizado: el sello sale de data/scripts/<id>.json
    m6.assemble_final_script(TID)
    man = json.loads(am.process_script(_script_normalizado()).read_text(encoding="utf-8"))
    assert man["papel_md5"] == p1 and len(hechos) == 1 and png.exists()
    assert not (env["assets"] / am.SELLO_EN_CURSO).exists()
    png.write_bytes(b"editada en QA")
    am.process_script(_script_normalizado(p1))                         # mismo sello: se reusa, no se paga
    assert len(hechos) == 1 and png.read_bytes() == b"editada en QA"
    p2 = _aprobar_papel(env, "P2")
    man = json.loads(am.process_script(_script_normalizado(p2)).read_text(encoding="utf-8"))
    assert len(hechos) == 2 and png.read_bytes() == b"png" and man["papel_md5"] == p2
    assert man["chapters"][0]["images"][0]["status"] != "skipped_exists"
    viejos = list(env["assets"].glob("_desfasado_*"))
    assert len(viejos) == 1 and (viejos[0] / "ch01_flux" / "ch01_img_01.png").read_bytes() == b"editada en QA"   # no se borra


@pytest.mark.parametrize("archivo", ["ch01_flux/ch01_img_01.png", "ch01_flux/ch01_img_01_graded.png", "ch01_flux/ch01_supp_01.png", "ch01_veo/ch01_clip_01.mp4",
                                     "ch01_veo/ch01_img_01.png", "ch01_veo/ch01_img_01_final.png", "ch01_flux/pedidos.json"])
def test_todos_los_reusos_por_existencia_se_niegan(env, archivo):
    """Tabla A (asset_manager): imágenes, `_graded`, supps, clips, base y foto final del clip, fallbacks: todos viven en chNN_*."""
    f = env["assets"] / archivo
    _w(f, "viejo")
    _w(env["assets"] / "assets_manifest.json", {"papel_md5": "P1"})
    d = am._archivar_si_desfasado(TID, "P2")
    assert d is not None and not f.exists() and (d / archivo).exists() and not (env["assets"] / "assets_manifest.json").exists()


def test_manifest_sin_sello_se_archiva(env):
    _w(env["assets"] / "ch01_flux" / "a.png", "viejo")
    _w(env["assets"] / "assets_manifest.json", {"chapters": []})       # como los del 28-oct
    d = am._archivar_si_desfasado(TID, "P1")
    assert d.name.startswith("_desfasado_sin_sello_")


def test_corrida_cortada_no_re_paga_lo_de_este_papel(env):
    """Sin manifest, `assets_en_curso.json` dice de qué papel son las fotos ya pagadas; si es de otro papel, se archivan."""
    _w(env["assets"] / "ch01_flux" / "a.png", "viejo")
    _w(env["assets"] / "assets_manifest.json", {"papel_md5": "P1"})
    assert am._archivar_si_desfasado(TID, "P2")
    _w(env["assets"] / "ch01_flux" / "b.png", "nuevo")                 # se corta acá
    assert am._archivar_si_desfasado(TID, "P2") is None and (env["assets"] / "ch01_flux" / "b.png").exists()
    assert am._archivar_si_desfasado(TID, "P3") is not None and not (env["assets"] / "ch01_flux").exists()


def test_long_sin_sello_no_paga_fotos(env, monkeypatch):
    hechos = _fake_flux(monkeypatch)
    with pytest.raises(ValueError, match="sin sello"):
        am.process_script(_script_normalizado())
    assert hechos == [] and not (env["assets"] / "assets_manifest.json").exists()


# ═══════════════════════ fase2b ═══════════════════════

def _plan() -> SimpleNamespace:
    return SimpleNamespace(chapter_id="ch01", engine="flux", asset_paths=[], audio_duration=1.0, art_profile="", timestamps_path=None,
                           is_first=True, video_type="long", supplemental_paths=[])


def _fase2b_hasta_el_candado(env, monkeypatch, sello="P2") -> list[str]:
    """Stubs hasta el primer paso de después del candado (`_resolve_flow_specs` o el plan): explotan si se llega."""
    _w(env["out"] / "audio" / TID / "sync_map.json", {"chapters": []})
    _w(env["assets"] / "assets_manifest.json", {"papel_md5": sello, "chapters": []})
    monkeypatch.setattr(fb, "_build_plans", lambda *a: [_plan()])
    monkeypatch.setattr(fb, "_load_script_lookup", lambda v: {})
    pasaron: list[str] = []

    class Llego(Exception):
        pass

    def resolve(plans, vid):
        pasaron.append("flow_specs")
        raise Llego()
    monkeypatch.setattr(fb, "_resolve_flow_specs", resolve)
    monkeypatch.setattr(fb, "Llego", Llego, raising=False)
    return pasaron


def _kw(**k) -> dict:
    return {"hook": None, "no_subs": False, "keep_segments": True, "dry_run": False, **k}


def _sembrar_fondos(env, sello="P1"):
    for n in ("ch01_flux_visual.mp4", "ch01_flux_visual.kenburns.json", "ch01_gfx.mp4", "ch01_gfx.plan.md5", "gfx_plan_ch01.resolved.json", "gfx_sfx_ch01.json",
              "gfx_pause_ch01.json", "gfx_escenas_ch01.json", "gfx_beats_ch01.json", "gfx_critic_rot_ch01.json"):
        _w(env["work"] / n, "viejo")
    for n in ("flow_specs.json", "depth_metrics.json", "zoom_verdicts.json"):
        _w(env["assets"] / n, "{}")
    _w(env["work"] / "fondos.json", {"papel_md5": sello})


@pytest.mark.parametrize("flags", [{"reuse_visuals": True}, {"reuse_visuals": True, "plan_only": True}])
def test_plan_only_y_reuse_se_niegan_con_fondos_de_otro_papel(env, monkeypatch, flags):
    pasaron = _fase2b_hasta_el_candado(env, monkeypatch)
    _sembrar_fondos(env)
    rc, final = fb._assemble_one_video(TID, **_kw(**flags))
    assert (rc, final) == (2, None) and pasaron == [] and (env["work"] / "ch01_flux_visual.mp4").exists()


def test_fondos_de_otro_papel_se_archivan_enteros(env, monkeypatch):
    pasaron = _fase2b_hasta_el_candado(env, monkeypatch)
    _sembrar_fondos(env)
    with pytest.raises(fb.Llego):
        fb._assemble_one_video(TID, **_kw())
    assert pasaron == ["flow_specs"]
    assert not any(p.is_file() for p in env["work"].rglob("*")) and not (env["assets"] / "flow_specs.json").exists()
    viejo = next((env["out"] / TID).glob("_fase2b_work_desfasado_*"))
    assert (viejo / "ch01_gfx.mp4").exists() and (viejo / "gfx_plan_ch01.resolved.json").exists() and (viejo / "zoom_verdicts.json").exists()


def test_con_el_mismo_sello_reusa_flow_specs_y_visuales(env, monkeypatch):
    pasaron = _fase2b_hasta_el_candado(env, monkeypatch, sello="P1")
    _sembrar_fondos(env, "P1")
    with pytest.raises(fb.Llego):
        fb._assemble_one_video(TID, **_kw())
    assert pasaron == ["flow_specs"] and (env["assets"] / "flow_specs.json").exists() and (env["work"] / "ch01_gfx.mp4").exists()


def test_only_cap_sigue_siendo_el_banco_del_candado_de_ch02(env, monkeypatch, capsys):
    """--only-cap --reuse-visuals (md5 de ch02, sin sello) avisa y sigue: no deja video ni sidecar."""
    _fase2b_hasta_el_candado(env, monkeypatch, sello=None)
    _sembrar_fondos(env)
    (env["work"] / "fondos.json").unlink()

    class Plan(Exception):
        pass

    def corte(*a, **k):
        raise Plan()
    monkeypatch.setattr(fb.cost_tracker, "start_video", corte)
    monkeypatch.setattr(fb.cost_tracker, "current_video", None)
    with pytest.raises(Plan):
        fb._assemble_one_video(TID, **_kw(reuse_visuals=True, only_cap="ch01"))
    assert (env["work"] / "ch01_gfx.mp4").exists() and "otro papel o sin sello" in capsys.readouterr().out


def test_el_guion_lleva_el_sello_y_aprobar_lo_conserva(env):
    src = inspect.getsource(fb._solo_plan)
    assert 'g["papel_md5"] = papel_md5' in src and src.index('g["papel_md5"]') < src.index("gg.escribir(g,")
    topic_dir = env["out"] / TID
    _w(env["work"] / "gfx_plan_ch01.resolved.json", "{}")
    from script_engine import gfx_guion as gg
    assert "json.dumps(g," in inspect.getsource(gg.escribir)           # escribe el dict entero
    _w(topic_dir / aprobacion.GUION, {"papel_md5": "P1"})
    aprobacion.aprobar(topic_dir, "Omar")
    assert json.loads((topic_dir / aprobacion.GUION).read_text(encoding="utf-8"))["papel_md5"] == "P1"


# ═══════════════════════ etapa_de y audio ═══════════════════════

def test_p1_sellado_se_aprueba_p2_y_etapa_de_vuelve_a_la_voz(env):
    p1 = _aprobar_papel(env, "P1")
    m6.assemble_final_script(TID)
    assert rp.etapa_de(TID) == ("assets", "falta assets_manifest.json")
    _w(env["assets"] / "assets_manifest.json", {"papel_md5": p1})
    assert rp.etapa_de(TID) == ("fondos", "falta fondos.json")
    _w(env["work"] / "fondos.json", {"papel_md5": p1})
    assert rp.etapa_de(TID)[0] == "guion_pantalla"
    _w(env["out"] / TID / "GUION_PANTALLA.json", {"papel_md5": p1})
    assert rp.etapa_de(TID)[0] == "aprobar_guion"
    p2 = _aprobar_papel(env, "P2")
    assert p2 != p1
    etapa, motivo = rp.etapa_de(TID)
    assert etapa == "voz" and motivo == f"data/scripts/{TID}.json: sello {p1[:8]}… de otro papel"
    m6.assemble_final_script(TID)                                      # la voz vuelve a sellar: lo de abajo sigue viejo
    assert rp.etapa_de(TID) == ("assets", f"assets_manifest.json: sello {p1[:8]}… de otro papel")
    _w(env["assets"] / "assets_manifest.json", {"papel_md5": p2})
    assert rp.etapa_de(TID) == ("fondos", f"fondos.json: sello {p1[:8]}… de otro papel")
    _w(env["work"] / "fondos.json", {"papel_md5": p2})
    assert rp.etapa_de(TID) == ("guion_pantalla", f"GUION_PANTALLA.json: sello {p1[:8]}… de otro papel")


def test_papel_sin_aprobar_nunca_llega_a_los_sellos(env):
    _w(env["d"] / "01e_pantalla.json", {"narracion_md5": md.md5_narracion(json.loads((env["d"] / "01b_narracion_v3.json").read_text(encoding="utf-8")))})
    _w(env["d"] / "01e_pantalla.md", "# papel")
    _w(env["data"] / "scripts" / f"{TID}.json", {})
    assert rp.etapa_de(TID)[0] == "papel"


def test_el_audio_con_el_mismo_texto_se_reusa_aunque_cambie_el_papel(env, fake_eleven):  # noqa: F811
    """Fuera del candado: audio_manager decide por text_hash/tts_hash; aprobar P2 no re-paga ElevenLabs."""
    import audio_manager as au
    s = _script_audio(True)
    _aprobar_papel(env, "P1")
    au.process_script(s)
    _aprobar_papel(env, "P2")
    au.process_script(s)
    assert len(fake_eleven["tts"]) == 1
