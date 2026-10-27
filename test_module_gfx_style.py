"""F4 §2: el director aplica la identidad del lab (gfx_style) — movimiento, transiciones, golpes de zoom, few-shot."""
from __future__ import annotations

from types import SimpleNamespace

from script_engine import gfx_style as st
from script_engine.gfx_project import GfxScene, transitions_of

MOODS = {"agua": {"triggers": {"sumergidos": 3, "ahogaba": 3, "agua": 1, "inundación": 2}},
         "oscuridad_encierro": {"triggers": {"encierro": 2, "celdas": 2, "oscuro": 1}}}


def W(text: str, t0: float = 0.0, step: float = 0.5) -> list[dict]:
    return [{"word": w, "start": round(t0 + k * step, 3), "end": round(t0 + k * step + 0.4, 3)} for k, w in enumerate(text.split())]


def test_perfil_misterio_prende_la_identidad():
    r = st.gfx_rules
    assert r.identity_rules and r.punch_max_identity == 4 and r.crossfade_frames == 20
    assert r.emphasis_stamp_px == 84                                       # sello suelto S, el del ícono sigue M


def test_movimiento_por_foto():
    doc = {"text_in_image": {"present": True, "text": "1965"}}
    wide_place = {"shot_scale": "wide", "subject": "the prison complex under a storm sky"}
    crowd = {"shot_scale": "wide", "subject": "a crowd of inmates in a row"}
    person = {"shot_scale": "medium", "subject": "a man behind bars"}
    assert st.movement_for(doc, 3, 10)[0] == "quieta"                      # nunca quieta salvo documentos
    assert st.movement_for(person, 0, 10)[0] == "alejar"                   # apertura
    assert st.movement_for(person, 9, 10)[0] == "alejar"                   # cierre
    assert st.movement_for(wide_place, 4, 10)[0] == "3D"                   # paisaje
    assert st.movement_for(crowd, 4, 10)[0] == "paneo"
    assert st.movement_for(person, 4, 10)[0] == "acercar"                  # default
    assert st.movement_for({}, 5, 10)[0] == "acercar"


def test_plan_movements_respeta_el_router_y_el_3d(tmp_path):
    imgs = []
    for i in range(4):
        p = tmp_path / f"ch05_img_{i + 1:02d}.png"
        p.write_bytes(b"png")
        imgs.append(p)
    prompts = [{"subject": "a man"}, {"shot_scale": "wide", "subject": "prison complex, sky"}, {"subject": "a man"},
               {"subject": "a woman"}]
    scenes = [GfxScene(i, i * 5.0, i * 5.0 + 5.0) for i in range(4)]
    scenes[2].safe = {"image": str(imgs[2]), "movement": "pan", "risk": "high"}
    movs = st.plan_movements(scenes, SimpleNamespace(engine="flux", asset_paths=imgs), prompts)
    assert [m["forma"] for m in movs] == ["alejar", "3D", "router", "alejar"]
    assert scenes[0].safe["movement"] == "pull" and scenes[1].safe is None             # 3D = clip DepthFlow
    assert scenes[2].safe["movement"] == "pan" and scenes[2].safe["risk"] == "high"    # el router manda
    assert st.plan_movements(scenes, SimpleNamespace(engine="veo", asset_paths=imgs), prompts) == []


def _scenes(durs, ranks=None):
    out, t = [], 0.0
    for i, d in enumerate(durs):
        out.append(GfxScene(i, t, t + d, (ranks or ["R3"] * len(durs))[i]))
        t += d
    return out


def test_transiciones_del_plan_mandan_en_templater_y_cues():
    sc = _scenes([5, 5, 5])
    plan = {"transitions": {"1": {"kind": "cut", "frames": 0, "rank": "R3"}, "2": {"kind": "dip", "frames": 10, "rank": "R3"}}}
    tr = transitions_of(plan, sc)
    assert tr == {1: plan["transitions"]["1"], 2: plan["transitions"]["2"]}
    assert transitions_of({}, sc)[1]["kind"] == "dissolve"                          # sin identidad: F3 tal cual


def test_disperso_corre_los_bloques_del_pico():
    from script_engine.gfx_sparse import compose_sparse, event_windows
    sc = _scenes([20, 20, 20])
    plan = {"callouts": [], "punch_in": [], "emphasis": [],
            "water_level": {"start": 30.0, "duration": 4.5, "value_text": "4.6"},
            "black_hold": {"start": 59.0, "duration": 1.0},
            "evidence_zoom": {"scene_idx": 0, "box": [.4, .4, .2, .2], "start": 17.0, "latido_t": 18.0},
            "transitions": {"1": {"kind": "cut", "frames": 0, "rank": "R3"}, "2": {"kind": "cut", "frames": 0, "rank": "R3"}}}
    win = event_windows(plan, sc, 30, 60.0)
    assert any(a <= 30.0 and b >= 34.5 for a, b in win) and any(a <= 59.0 and b >= 60.0 - 1e-6 for a, b in win)
    p, scs, tr, offs = compose_sparse(plan, sc, win, 30)
    assert "transitions" not in p
    assert p["water_level"]["start"] is not None and p["water_level"]["start"] < 30.0       # corrido al timeline disperso
    assert p["evidence_zoom"]["latido_t"] - p["evidence_zoom"]["start"] == 1.0


def test_lab_usa_la_misma_regla_de_movimiento():
    import gfx_lab_server as lab
    assert lab.suggest_movement is st.suggest_movement
