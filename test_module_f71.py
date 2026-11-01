"""F71 — las fotos siguen a la voz (anclas) + chascada del falso «nsfw». Sin red. Los 5 casos reales salen de los archivos de Wittenoom
(se saltan si el topic no está en disco); lo demás, con fixtures chicos."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

import anchor_timing as at
import asset_manager as am

RAIZ = Path(__file__).resolve().parent
WIT = "123bbb64-9fca-4395-8bf4-57d60e219ef1"
hay_wit = pytest.mark.skipif(not (RAIZ / "data" / "scripts" / "_steps" / WIT / at.NORMALIZADO).exists(), reason="sin Wittenoom en disco")


def _w(txt):
    return [{"word": p, "start": float(i), "end": i + 0.5} for i, p in enumerate(txt.split())]


def _span(o, s, **k):
    return {"original": o, "suggested": s, "decision": "applied", **k}


def _entrada(orig, spans):
    return {"chapter_number": 1, "narration_original": orig, "narration_normalized": orig, "spans_applied": spans}


# ═══════════════════════════════════ A · la aguja sale de lo que leyó la voz ═══════════════════════════════════

def test_anio_con_span_empareja_y_sin_normalizado_no():
    orig = "Era de noche. En 1944, el inspector llegó."
    voz = _w("era de noche en mil novecientos cuarenta y cuatro el inspector llegó")
    nn = _entrada(orig, [_span("1944", "mil novecientos cuarenta y cuatro")])
    assert at.compute_anchor_starts(["En 1944, el inspector"], voz) is None
    assert at.compute_anchor_starts(["En 1944, el inspector"], voz, narr_norm=nn) == [3.0]


def test_sigla_que_la_voz_no_deletreo():
    voz = _w("y csr la compañía pagó")
    nn = _entrada("y CSR, la compañía pagó", [])
    assert at.compute_anchor_starts(["y CSR, la compañía"], voz, narr_norm=nn) == [0.0]


def test_maitland_solo_la_primera_aparicion_se_reemplaza():
    orig = "Maitland habló. Después Maitland calló y Maitland se fue."
    voz = _w("méitland habló después maitland calló y maitland se fue")
    nn = _entrada(orig, [_span("Maitland", "Méitland")])
    assert at.compute_anchor_starts(["Maitland habló", "Después Maitland calló", "Maitland se fue"], voz, narr_norm=nn) == [0.0, 2.0, 6.0]
    assert at._agujas_de_voz(["Maitland habló", "Maitland se fue"], nn)[0][0] == "méitland"
    assert at._agujas_de_voz(["Maitland habló", "Maitland se fue"], nn)[1][0] == "maitland"


def test_ancla_no_literal_recibe_los_spans_sobre_su_texto():
    voz = _w("el año mil novecientos cincuenta terminó mal")
    nn = _entrada("Otra narración, ya editada.", [_span("1950", "mil novecientos cincuenta")])
    assert at._agujas_de_voz(["1950 terminó mal"], nn) == [["mil", "novecientos", "cincuenta"]]
    assert at.compute_anchor_starts(["1950 terminó mal"], voz, narr_norm=nn) == [2.0]


def test_cap_sin_normalizado_es_el_comportamiento_viejo(monkeypatch):
    import tts_normalizer
    monkeypatch.setattr(tts_normalizer, "normalize_for_tts", lambda t, language="es": "uno dos tres")
    voz = _w("uno dos tres llegó")
    assert at.compute_anchor_starts(["lo que sea"], voz) == [0.0]
    assert at.compute_anchor_starts(["lo que sea"], voz, narr_norm=None) == [0.0]
    assert at.compute_anchor_starts(["lo que sea"], voz, narr_norm={}) == [0.0]


def test_offset_dentro_de_un_span_cae_al_inicio_del_reemplazo():
    nn = _entrada("Dijo «hola mundo» y se fue.", [_span("«hola mundo»", "hola mundo cruel")])
    assert at._agujas_de_voz(["hola mundo»"], nn)[0][:2] == ["hola", "mundo"]


def test_spans_que_no_se_aplicaron_y_marca_de_pool_forms_no_entran():
    nn = _entrada("En 1944 hubo (horas/dólares/porcentajes/comillas) algo.", [
        {"original": "1944", "suggested": "XX", "decision": "skipped_not_found"},
        {"original": "(horas/dólares/porcentajes/comillas)", "suggested": "(forma hablada)", "decision": "applied", "category": "f5_pool_forms"}])
    assert at._agujas_de_voz(["En 1944 hubo"], nn) == [["en", "1944", "hubo"]]
    assert at._agujas_de_voz(["(horas/dólares/porcentajes/comillas) algo"], nn)[0][0] == "horasdólaresporcentajescomillas"


def test_ancla_vacia_devuelve_none():
    assert at.compute_anchor_starts([""], _w("a b c"), narr_norm=_entrada("a b c", [])) is None


def test_cargar_normalizado(tmp_path):
    assert at.cargar_normalizado("no-existe", tmp_path) == {}
    d = tmp_path / "data" / "scripts" / "_steps" / "t"
    d.mkdir(parents=True)
    (d / at.NORMALIZADO).write_text(json.dumps({"chapters": [
        {"chapter_number": 2, "narration_normalized": "hola"}, {"chapter_number": 3, "narration_normalized": " "}]}), encoding="utf-8")
    assert list(at.cargar_normalizado("t", tmp_path)) == [2]      # la misma decisión que _resolve_text_for_tts
    (d / at.NORMALIZADO).write_text("{roto", encoding="utf-8")
    assert at.cargar_normalizado("t", tmp_path) == {}


def test_normalizado_de_timestamps_sin_topic_ni_nombre():
    assert at.normalizado_de_timestamps(None) is None
    assert at.normalizado_de_timestamps("x/ts.json") is None
    assert at.normalizado_de_timestamps("output/audio/no-existe/ch02_timestamps.json") is None


def _anclas_y_palabras(cap):
    s = json.loads((RAIZ / "data" / "scripts" / f"{WIT}.json").read_text(encoding="utf-8"))
    ch = next(c for c in s["chapters"] if c["chapter_number"] == cap)
    its = ch.get("image_prompts") or ch.get("supplemental_image_prompts")
    w = json.loads((RAIZ / "output" / "audio" / WIT / f"ch{cap:02d}_timestamps.json").read_text(encoding="utf-8"))
    return [it["narration_anchor"] for it in its], (w if isinstance(w, list) else w["words"])


@hay_wit
@pytest.mark.parametrize("cap,empieza,aguja", [(2, "y CSR", ["y", "csr", "la"]), (3, "En 1944", ["en", "mil", "novecientos"]),
                                               (5, "En 1978", ["en", "mil", "novecientos"]), (6, "En 2016", ["en", "dos", "mil"]),
                                               (7, "En 2023", ["en", "dos", "mil"])])
def test_los_5_casos_reales_del_handoff(cap, empieza, aguja):
    anclas, _ = _anclas_y_palabras(cap)
    i = next(k for k, a in enumerate(anclas) if a.startswith(empieza))
    assert at._agujas_de_voz(anclas, at.cargar_normalizado(WIT, RAIZ)[cap])[i] == aguja


@hay_wit
@pytest.mark.parametrize("cap", range(1, 8))
def test_wittenoom_los_7_caps_emparejan(cap):
    anclas, w = _anclas_y_palabras(cap)
    st = at.compute_anchor_starts(anclas, w, narr_norm=at.cargar_normalizado(WIT, RAIZ)[cap])
    assert st is not None and len(st) == len(anclas)


# ═══════════════════════════════════ B · chascada: el eco del input no cuenta ═══════════════════════════════════

def _cuerpo(tipo, msg, **entrada):
    return json.dumps({"detail": [{"loc": ["body", "prompt"], "msg": msg, "type": tipo, "input": entrada}]})


def test_base64_con_nsfw_e_invalid_request_no_es_rechazo():
    c = _cuerpo("invalid_request", "Could not generate a video with the given inputs.", prompt="x",
                image_url="data:image/png;base64,AAAAnsfwBBBB" + "C" * 500)
    assert "nsfw" in c
    assert am._is_content_rejection(c) is False


def test_content_policy_violation_es_rechazo():
    assert am._is_content_rejection(_cuerpo("content_policy_violation", "flagged by a content checker", prompt="x")) is True


def test_no_media_generated_es_rechazo_sin_palabras_de_seguridad():
    c = _cuerpo("no_media_generated", "The model did not generate the expected output.", prompt="x")
    assert am._is_content_rejection(c) is True


def test_solo_safety_tolerance_en_el_input_no_es_rechazo():
    assert am._is_content_rejection(_cuerpo("invalid_request", "bad input", prompt="x", safety_tolerance="6")) is False


def test_string_data_fuera_de_input_y_cuerpo_no_json():
    assert am._is_content_rejection(json.dumps({"detail": "data:image/png;base64,nsfw"})) is False
    assert am._is_content_rejection('error image "data:image/png;base64,AAnsfwBB" invalid') is False
    assert am._is_content_rejection("error " + "AAnsfwBB" * 40 + " invalid") is False
    assert am._is_content_rejection("corrida corta nsfw") is True
    assert am._is_content_rejection("Request blocked: content_policy_violation") is True
    assert am._is_content_rejection(ValueError("moderation")) is True


def test_el_mensaje_sigue_contando_aunque_el_input_este_limpio():
    assert am._is_content_rejection(_cuerpo("x", "The request was blocked because it violates Google's practices", prompt="x")) is True


def test_guardar_error_en_el_topic(tmp_path, monkeypatch):
    monkeypatch.setattr(am, "OUTPUT_DIR", tmp_path)
    am._destino_error_fal(tmp_path / "topic1" / "assets" / "ch01_veo" / "ch01_clip_01.mp4")
    f = am._guardar_error_fal('{"detail":"completo ' + "x" * 5000 + '"}')
    assert f.parent == tmp_path / "topic1" / "assets" / "_errores_fal" and f.name.endswith("_ch01_clip_01.json")
    assert len(f.read_text(encoding="utf-8")) > 5000


def test_guardar_error_fuera_de_output_no_guarda(tmp_path, monkeypatch):
    monkeypatch.setattr(am, "OUTPUT_DIR", tmp_path / "output")
    am._destino_error_fal(tmp_path / "lab" / "foto.png")
    assert am._guardar_error_fal("x") is None
    assert not (tmp_path / "output").exists()


def test_error_de_clip_que_no_es_rechazo_no_salta_de_motor_y_guarda_el_cuerpo(tmp_path, monkeypatch):
    """Lo que hace hoy (sin cambiarlo): sube como HTTPError, no como rechazo: `_generate_clip` no pasa a Kling."""
    import requests

    class R:
        status_code = 422
        text = _cuerpo("invalid_request", "Could not generate", image_url="data:image/png;base64,nsfw" + "A" * 300)

        def json(self):
            return {"status": "COMPLETED"}

        def raise_for_status(self):
            raise requests.HTTPError("422 Client Error", response=self)

    class Estado(R):
        status_code = 200

        def raise_for_status(self):
            return None

    respuestas = iter([Estado(), R()])
    monkeypatch.setattr(am.requests, "get", lambda *a, **k: next(respuestas))
    monkeypatch.setattr(am, "_fal_headers", lambda: {})
    monkeypatch.setattr(am, "OUTPUT_DIR", tmp_path)
    am._destino_error_fal(tmp_path / "t" / "assets" / "c.mp4")
    with pytest.raises(requests.HTTPError):
        am._fal_queue_poll("s", "r")
    assert len(list((tmp_path / "t" / "assets" / "_errores_fal").iterdir())) == 1
