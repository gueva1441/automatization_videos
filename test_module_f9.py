"""
test_module_f9.py — F9 (HANDOFF_F8b_F9 §3): voz v4 + MS Narrador, etiquetas desde el guion.
"""
from __future__ import annotations

import json

import pytest

import audio_manager as am
from audio_profiles import AUDIO_PROFILES, VOICE_SETTINGS_BY_INTENT_V4
from script_engine import tts_tags as tt

CAP = ("El agua subió. Los presos gritaban sin parar en la oscuridad del pabellón.\n\n"
       "Reed lo contó así: «Una vez que se fue la luz, los oficiales empezaron a renunciar», dijo. Nadie volvió.\n\n"
       "Vieron cómo el nivel subía… sin poder hacer nada. Pasaron cuatro días encerrados en el agua. Eran disparos.")


# ═══════════════════════════════════════════════════════════════
#  §3.3 — etiquetas
# ═══════════════════════════════════════════════════════════════

def test_pausas_largas_despues_de_cita_y_al_cerrar():
    t, c = tt.tag_cap(CAP, intent="rising_tension", intensities=[3, 3, 3])
    assert "renunciar», dijo. [long pause] Nadie" in t and t.rstrip().endswith("[long pause]")
    assert "subía… [short pause] sin poder" in t
    assert tt.strip_tags(t) == tt.strip_tags(CAP) and c["[whispers]"] == 0 and c["[quietly]"] == 0


def test_golpe_solo_en_beats_intensos_y_whispers_en_el_pico():
    t, c = tt.tag_cap(CAP, intent="shock", intensities=[4, 4, 5], pico_par=2)
    assert t.split("\n\n")[2].startswith("[short pause] [slowly] Vieron")
    assert "[whispers] Eran disparos." in t and c["[whispers]"] == 1
    assert c["[quietly]"] + c["[whispers]"] <= tt.GOLPE_MAX_PER_CAP
    t2, c2 = tt.tag_cap(CAP, intent="setup", intensities=[5, 5, 5], pico_par=None)
    assert c2["[quietly]"] == 0 and c2["[whispers]"] == 0                 # nunca en caps setup


def test_slowly_en_gancho_y_en_desarrollo_si_v4_corre():
    t, _ = tt.tag_cap(CAP, intent="hook", intensities=[4, 4, 4])
    assert t.startswith("[slowly] El agua") and t.count("[slowly]") == 1
    t2, _ = tt.tag_cap(CAP, intent="consequences", intensities=[2, 2, 2], slowly_dev=True)
    assert all(p.startswith("[slowly]") for p in t2.split("\n\n"))
    t3, _ = tt.tag_cap(CAP, intent="consequences", intensities=[2, 2, 2])
    assert "[slowly]" not in t3


def test_transfer_al_texto_normalizado():
    t, _ = tt.tag_cap(CAP, intent="shock", intensities=[4, 4, 5], pico_par=2)
    norm = CAP.replace("cuatro días", "4 días")
    out, mode = tt.transfer_tags(t, norm)
    assert mode == "oracion" and "4 días" in out and "[whispers] Eran disparos." in out
    assert tt.strip_tags(out) == tt.strip_tags(norm)
    out2, mode2 = tt.transfer_tags(t, norm.replace(" Nadie volvió.", ""))     # una oración menos: solo párrafos
    assert mode2 == "parrafo" and out2.split("\n\n")[2].startswith("[short pause] [slowly]")
    out3, mode3 = tt.transfer_tags(t, "Un solo párrafo.")
    assert mode3 == "final" and out3.endswith("[long pause]")


def test_caps_tts_no_toca_narration():
    esc = {"pico": {"beat": 3}, "beats": [{"n": 1, "intensidad": 2}, {"n": 2, "intensidad": 4}, {"n": 3, "intensidad": 5}]}
    pars = [{"cap": 4, "beat": 1, "texto": CAP.split("\n\n")[0]}, {"cap": 4, "beat": 2, "texto": CAP.split("\n\n")[1]},
            {"cap": 4, "beat": 3, "texto": CAP.split("\n\n")[2]}]
    caps = [{"chapter_number": 4, "narration": CAP}]
    from script_engine import m01c_editor as mc
    mc.narration_tts(esc, pars, caps)
    assert caps[0]["narration"] == CAP and "[whispers]" in caps[0]["narration_tts"]


# ═══════════════════════════════════════════════════════════════
#  §3.1–§3.4 — audio_manager
# ═══════════════════════════════════════════════════════════════

def test_perfil_v4():
    p = AUDIO_PROFILES["MISTERIO_ABISAL"]
    assert p["voice_id"] == "pqHfZKP75CvOlQylNhV4"                          # v2 sigue con Bill
    assert p["voice_id_v4"] == "N9Z5MLTIaHFLflaLtbDi" and p["elevenlabs_model_v4"] == "eleven_v4"
    assert VOICE_SETTINGS_BY_INTENT_V4["hook"] == {"stability": 0.45}
    s = am._resolve_voice_settings_v4("shock")
    assert s == {"stability": 0.45, "similarity_boost": 0.8}                # sin style, sin speed


class _R:
    status_code = 200
    content = b"mp3"

    def raise_for_status(self):
        pass


def test_payload_v2_identico_y_v4_con_idioma(monkeypatch, tmp_path):
    sent = []
    monkeypatch.setattr(am.requests, "post", lambda url, **k: (sent.append(k["json"]), _R())[1])
    monkeypatch.setattr(am.cost_tracker, "track_elevenlabs", lambda **k: None)
    am._generate_chapter_audio("hola", tmp_path / "a.mp3", "v", {"stability": 0.5})
    am._generate_chapter_audio("[slowly] hola", tmp_path / "b.mp3", "v", {"stability": 0.5}, model_id="eleven_v4",
                               language_code="es")
    assert sent[0] == {"text": "hola", "model_id": am.api.elevenlabs_model, "voice_settings": {"stability": 0.5}}
    assert sent[1]["model_id"] == "eleven_v4" and sent[1]["language_code"] == "es"


@pytest.fixture
def fake_eleven(monkeypatch, tmp_path):
    calls = {"tts": [], "fa": [], "norm": []}
    monkeypatch.setattr(am, "OUTPUT_DIR", tmp_path)
    monkeypatch.setattr(am, "_normalize_loudness", lambda p, lufs: calls["norm"].append(lufs))

    def tts(text, output_path, voice_id, voice_settings, model_id=None, language_code=None):
        calls["tts"].append({"text": text, "voice": voice_id, "vs": voice_settings, "model": model_id})
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(b"mp3")
        return output_path

    def fa(path, text, language="es"):
        calls["fa"].append(text)
        return {"words": [{"text": w, "start": i * 0.4, "end": i * 0.4 + 0.3} for i, w in enumerate(text.split())],
                "characters": []}
    monkeypatch.setattr(am, "_generate_chapter_audio", tts)
    monkeypatch.setattr(am, "_forced_align_elevenlabs", fa)
    monkeypatch.setattr(am, "_get_audio_duration", lambda p: 10.0)
    monkeypatch.setattr(am, "_ensure_cost_tracking", lambda v: None)
    monkeypatch.delenv("TTS_V2", raising=False)
    return calls


def _script(tagged: bool):
    tagged_txt, _ = tt.tag_cap(CAP, intent="shock", intensities=[4, 4, 5], pico_par=2)
    ch = {"id": "ch04", "text": CAP, "narrative_intent": "shock"}
    if tagged:
        ch["narration_tts"] = tagged_txt
    return {"video_id": "vid-f9", "chapters": [ch]}


def test_v3_va_a_v4_con_etiquetas_y_alinea_limpio(fake_eleven):
    sm = json.loads(am.process_script(_script(True)).read_text(encoding="utf-8"))
    tts = fake_eleven["tts"][0]
    assert tts["voice"] == "N9Z5MLTIaHFLflaLtbDi" and tts["model"] == "eleven_v4"
    assert "[whispers]" in tts["text"] and "style" not in tts["vs"]
    assert "[" not in fake_eleven["fa"][0]                               # forced alignment con el texto limpio
    ch = sm["chapters"][0]
    assert ch["tts_transfer"] == "oracion" and "[" not in ch["text_for_tts"]
    assert fake_eleven["norm"] == [-24.0]                                 # la voz v4 al nivel de la música calibrada


def test_v2_sigue_igual_y_tts_v2_fuerza_bill(fake_eleven, monkeypatch):
    am.process_script(_script(False))
    t = fake_eleven["tts"][0]
    assert t["voice"] == "pqHfZKP75CvOlQylNhV4" and t["model"] is None and "[" not in t["text"]
    assert fake_eleven["norm"] == []                                      # v2: sin normalizar (como antes)
    monkeypatch.setenv("TTS_V2", "1")
    fake_eleven["tts"].clear()
    s = _script(True)
    s["video_id"] = "vid-f9-b"
    am.process_script(s)
    t = fake_eleven["tts"][0]
    assert t["voice"] == "pqHfZKP75CvOlQylNhV4" and t["model"] is None and "[" not in t["text"]


def test_cambio_de_etiquetas_regenera(fake_eleven):
    s = _script(True)
    am.process_script(s)
    am.process_script(s)
    assert len(fake_eleven["tts"]) == 1                                   # mismo pedido: reusa
    s["chapters"][0]["narration_tts"] = s["chapters"][0]["narration_tts"].replace("[whispers]", "[quietly]")
    am.process_script(s)
    assert len(fake_eleven["tts"]) == 2
