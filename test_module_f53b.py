"""F53b Parte A — los perfiles de video de engine_profiles: Gemini Omni Flash 1.1 (G) y Kling 4.0 (K, el respaldo de la
adenda; Seedance no). Campos del schema de fal (F52), fichas de guía de F52b tal cual y costo medido en el panel. Offline."""
import json
from pathlib import Path

import pytest

import engine_profiles as ep

ROOT = Path(__file__).resolve().parent
GUIAS = ROOT / "lab" / "hyperframes" / "f52" / "guias"
SCHEMAS = ROOT / "lab" / "hyperframes" / "f52" / "schemas"


@pytest.mark.parametrize("key, letra, endpoint, campo, dmin, dmax", [
    ("gemini_omni_flash", "G", "google/gemini-omni-flash/v1.1/image-to-video", "image_url", 3, 10),
    ("kling_4", "K", "kling/v4/image-to-video", "start_image_url", 3, 30),
])
def test_f53b_perfil_de_video(key, letra, endpoint, campo, dmin, dmax):
    p = ep.select_video_profile(key)
    assert (p.endpoint, p.campo_imagen, p.duracion_min, p.duracion_max) == (endpoint, campo, dmin, dmax)
    assert p.resolucion == "1080p" and p.campo_audio is None and not p.duracion_como_texto
    assert p.ficha == (GUIAS / f"{letra}.md").read_text(encoding="utf-8").strip()       # la ficha de F52b, tal cual
    sch = SCHEMAS / f"{letra}.json"
    if sch.exists():                                                                   # el schema leído de fal en F52
        props = next(v for k, v in json.loads(sch.read_text(encoding="utf-8"))["components"]["schemas"].items()
                     if k.endswith("Input"))["properties"]
        assert campo in props and "duration" in props and "resolution" in props
        assert not any("audio" in c for c in props)                                    # sin campo de audio
        assert not any("safety" in c or "tolerance" in c for c in props)


def test_f53b_costo_por_clip_de_8_s():
    assert ep.PERFIL_VIDEO_G.costo(8) == 1.2                       # 0,03 × 5 × 8 (DECISIONES 14:24)
    assert ep.PERFIL_VIDEO_K.costo(8) == 1.884                     # 0,157 × 1,5 × 8 (adenda F53b)
    assert ep.PERFIL_VIDEO_G.costo(8, 1920, 1080) == ep.PERFIL_VIDEO_G.costo(8)    # cobran por segundo


def test_f53b_sin_seedance_y_clave_desconocida():
    assert set(ep._VIDEO_PROFILES) == {"gemini_omni_flash", "kling_4"}
    assert not hasattr(ep, "PERFIL_VIDEO_S")
    with pytest.raises(KeyError):
        ep.select_video_profile("seedance_2_5")
