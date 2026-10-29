"""F53b Parte A punto 2 — costo de clips por VideoProfile: CostTracker.track_video y las estimaciones de config sin
`fal_per_clip` (G a 8 s). Offline: no llama a fal ni a ningún modelo; no escribe data/cost_history.json (no se llama
end_video, se lee current_video.entries)."""
import pytest

from config import long_video, pipeline, short_video
from cost_tracker import CostTracker
from engine_profiles import PERFIL_VIDEO_G, PERFIL_VIDEO_K
from error_handler import PipelineStage


@pytest.mark.parametrize("perfil, total", [(PERFIL_VIDEO_G, 1.20), (PERFIL_VIDEO_K, 1.884)])
def test_f53b_track_video_registra_el_costo_del_perfil(perfil, total):
    ct = CostTracker()
    ct.start_video("f53b_test")
    ct.track_video(perfil, 8, 1920, 1080, description="clip de prueba")
    (e,) = ct.current_video.entries
    assert e.total_cost == pytest.approx(total)
    assert e.stage == PipelineStage.VIDEO.value
    assert e.service == f"fal {perfil.endpoint}"
    assert e.units == 8 and e.unit_label == "s"
    assert e.description == "clip de prueba"
    assert ct.current_video.total_cost == pytest.approx(total)
    assert ct.session_overhead == []


def test_f53b_track_video_sin_video_activo_va_a_overhead():
    ct = CostTracker()
    ct.track_video(PERFIL_VIDEO_G, 8)
    assert ct.get_session_overhead_total() == pytest.approx(1.20)


def _sin_fal(costs):
    return {k: v for k, v in costs.items() if k != "fal_per_clip"}


def test_f53b_estimaciones_no_leen_fal_per_clip():
    costs = _sin_fal(pipeline.costs)
    assert "fal_per_clip" not in costs
    long_video.estimated_cost_per_long_video(costs)       # no KeyError
    short_video.estimated_cost_per_short_video(costs)


def test_f53b_estimaciones_suben_en_G8_menos_veo_por_clip():
    costs = dict(pipeline.costs)
    veo = 0.24
    delta = PERFIL_VIDEO_G.costo(8) - veo
    # cálculo viejo: el mismo método con fal_per_clip = 0,24 → se reconstruye restando el delta por clip
    viejo_long = long_video.estimated_cost_per_long_video(costs) - delta * long_video.veo_clips_per_long_video
    viejo_short = short_video.estimated_cost_per_short_video(costs) - delta * short_video.veo_clips_per_short_video
    ref_long = (long_video.veo_clips_per_long_video * veo
                + 1 * costs["flux_pro_ultra_per_image"]
                + (long_video.leonardo_images_per_long_video + long_video.veo_clips_per_long_video - 1)
                * costs["flux_pro_per_image"]
                + 2 * costs["gemini_per_call_long"]
                + 1500 * 6 * costs["elevenlabs_per_char"])
    ref_short = (short_video.veo_clips_per_short_video * veo
                 + 1 * costs["flux_pro_ultra_per_image"]
                 + (short_video.leonardo_images_per_short_video - 1) * costs["flux_pro_per_image"]
                 + 1 * costs["gemini_per_call"]
                 + 120 * 6 * costs["elevenlabs_per_char"])
    assert viejo_long == pytest.approx(ref_long)
    assert viejo_short == pytest.approx(ref_short)
    assert delta == pytest.approx(0.96)
