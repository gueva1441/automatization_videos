"""test_module_f38e_a.py — F38e §A (Ensamble): r1 caché de capas por md5 del plan, R8 negro de cierre dentro del
segmento con el plan congelado, y A.3 el chequeo «costuras» medido en el mp4.

Autocontenido: planes sintéticos y mp4 chicos generados con ffmpeg lavfi en tmp_path; nada de data/ ni output/.
Correr: python -m pytest test_module_f38e_a.py -q
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

import fase2b
import script_engine.gfx_layer as gl

PLAN = {"chapter_number": 2, "title_card": {"kicker": "CAPÍTULO 2", "title": "T"}, "callouts": [],
        "count_up": None, "archive_clipping": None, "evidence_zoom": None, "punch_in": [],
        "chapter_question": None, "black_hold": None}
PLAN_B = {**PLAN, "callouts": [{"text": "otro plan", "start": 1.0, "duration": 2.0, "kind": "fact", "side": "left"}]}
# la pausa (2.0 s) y el negro (1.0 s = black_hold_sec del perfil misterio, identidad F3) van en el plan: el test no
# inventa un número del sistema, usa los del plan sintético
PLAN_Q = {**PLAN, "chapter_question": {"text": "¿Quién lo decidió?", "start": 10.0, "duration": 2.0, "pause": 2.0,
                                       "keyword": "decidió", "generated": True},
          "black_hold": {"start": 12.0, "duration": 1.0}}


def _plan_a_disco(work: Path, plan: dict) -> Path:
    f = work / "gfx_plan_ch02.resolved.json"
    f.write_text(json.dumps({"plan": plan, "rejected": []}, ensure_ascii=False, indent=1), encoding="utf-8")
    return f


def _md5(f: Path) -> str:
    return hashlib.md5(f.read_bytes()).hexdigest()


@pytest.fixture
def env(tmp_path, monkeypatch):
    """apply_gfx sin navegador ni ffmpeg: re-encode, duración, doctor, contexto, templater y CLI de HyperFrames
    mockeados (como test_module_gfx_layer_fallback). `renders` cuenta los renders; `extendido` las pausas con que se
    alargó el base; `dur` la duración que ffprobe «ve» (sube con extend_base)."""
    base = tmp_path / "ch02_flux_visual.mp4"
    base.write_bytes(b"fake")
    chplan = SimpleNamespace(chapter_id="ch02", engine="flux", narration="", timestamps_path=None,
                             narration_anchors=None, supplemental_paths=None, is_first=False)
    dur = {"v": 10.0}
    extendido: list[float] = []
    renders: list[Path] = []
    monkeypatch.setattr(gl, "_reencode", lambda src, out, fps: (out.parent.mkdir(parents=True, exist_ok=True),
                                                                 out.write_bytes(b"v")))
    monkeypatch.setattr(gl, "_ffprobe_duration", lambda p: dur["v"])

    def fake_extend(b, pause, fps):
        extendido.append(pause)
        dur["v"] = round(dur["v"] + pause, 3)
    monkeypatch.setattr(gl, "extend_base", fake_extend)
    monkeypatch.setattr(gl, "_doctor_once", lambda log: None)
    import script_engine.gfx_director as gd
    monkeypatch.setattr(gd, "load_chapter_context",
                        lambda vid, p: {"script_chapter": {}, "sources": {}, "chapter_number": 2, "facts": [], "skeleton": {}})
    monkeypatch.setattr(gl, "write_project", lambda *a, **k: None)

    def fake_hf(args, **k):
        if args[0] == "lint":
            return subprocess.CompletedProcess(args, 0, json.dumps({"errorCount": 0, "warningCount": 0}), "")
        out = Path(args[args.index("-o") + 1])
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(b"mp4 nuevo")
        renders.append(out)
        return subprocess.CompletedProcess(args, 0, "", "")
    monkeypatch.setattr(gl, "_hf", fake_hf)
    # el plan congelado es el resolved.json de disco (como con el guion aprobado y vigente; sin tocar aprobacion)
    monkeypatch.setattr(gl, "plan_congelado",
                        lambda wd, cap: (json.loads((Path(wd) / f"gfx_plan_{cap}.resolved.json").read_text(encoding="utf-8"))["plan"]
                                         if (Path(wd) / f"gfx_plan_{cap}.resolved.json").exists() else None))
    return SimpleNamespace(base=base, chplan=chplan, work=tmp_path, renders=renders, extendido=extendido, dur=dur)


def _gfx(e, **kw) -> Path:
    return gl.apply_gfx(e.base, e.chplan, "vid", e.work, width=2560, height=1440, fps=30, **kw)


def _log(e) -> str:
    return (e.work / "gfx_ch02.log").read_text(encoding="utf-8")


# ─── r1: caché de capas por md5 del plan ───

def test_r1_al_dibujar_escribe_el_sidecar_con_el_md5_del_plan(env):
    f = _plan_a_disco(env.work, PLAN)
    out = _gfx(env)
    assert out == env.work / "ch02_gfx.mp4" and len(env.renders) == 1
    sc = gl.sidecar_plan(env.work, "ch02")
    assert sc.exists() and sc.read_text(encoding="utf-8").split()[0] == _md5(f) == gl.md5_plan_resuelto(env.work, "ch02")
    assert "sidecar: ch02_gfx.plan.md5" in _log(env)


def test_r1_plan_igual_con_reuse_se_reusa(env):
    f = _plan_a_disco(env.work, PLAN)
    (env.work / "ch02_gfx.mp4").write_bytes(b"capa vieja")
    gl.sidecar_plan(env.work, "ch02").write_text(f"{_md5(f)}  gfx_plan_ch02.resolved.json\n", encoding="utf-8")
    out = _gfx(env, reuse=True)
    assert out == env.work / "ch02_gfx.mp4" and out.read_bytes() == b"capa vieja" and env.renders == []
    assert "se reusa" in _log(env)


def test_r1_plan_cambiado_con_reuse_se_rehace(env):
    f = _plan_a_disco(env.work, PLAN)
    (env.work / "ch02_gfx.mp4").write_bytes(b"capa del plan A")
    gl.sidecar_plan(env.work, "ch02").write_text(f"{_md5(f)}  gfx_plan_ch02.resolved.json\n", encoding="utf-8")
    f = _plan_a_disco(env.work, PLAN_B)                       # el plan cambió (p. ej. --plan-edit + reaprobación)
    out = _gfx(env, reuse=True)
    assert out == env.work / "ch02_gfx.mp4" and out.read_bytes() == b"mp4 nuevo" and len(env.renders) == 1
    assert "capa de otro plan: se rehace" in _log(env)
    assert gl.sidecar_plan(env.work, "ch02").read_text(encoding="utf-8").split()[0] == _md5(f)


def test_r1_sin_sidecar_con_reuse_se_rehace(env):
    _plan_a_disco(env.work, PLAN)
    (env.work / "ch02_gfx.mp4").write_bytes(b"capa de antes de F38e")     # como las capas de v5 en el render v6
    out = _gfx(env, reuse=True)
    assert out.read_bytes() == b"mp4 nuevo" and len(env.renders) == 1
    assert "capa sin md5 de plan: se rehace" in _log(env)
    assert gl.sidecar_plan(env.work, "ch02").exists()


def test_r1_capa_reusable_motivos(tmp_path):
    assert gl.capa_reusable(tmp_path, "ch02") == (False, "sin capa")
    (tmp_path / "ch02_gfx.mp4").write_bytes(b"x")
    assert gl.capa_reusable(tmp_path, "ch02")[1] == "capa sin md5 de plan: se rehace"
    gl.sidecar_plan(tmp_path, "ch02").write_text("abc\n", encoding="utf-8")
    assert "sin plan resuelto de hoy" in gl.capa_reusable(tmp_path, "ch02")[1]
    f = _plan_a_disco(tmp_path, PLAN)
    assert gl.capa_reusable(tmp_path, "ch02")[1].startswith("capa de otro plan: se rehace")
    gl.sidecar_plan(tmp_path, "ch02").write_text(f"{_md5(f)}  gfx_plan_ch02.resolved.json\n", encoding="utf-8")
    assert gl.capa_reusable(tmp_path, "ch02")[0] is True


def test_r1_la_huella_del_segmento_ve_el_plan_resuelto(tmp_path):
    """--reassemble-from-segments: un plan resuelto distinto es un segmento distinto (antes solo miraba el crudo)."""
    (tmp_path / "a.wav").write_bytes(b"a")
    (tmp_path / "t.json").write_text("[]", encoding="utf-8")
    plan = SimpleNamespace(chapter_id="ch02", audio_path=tmp_path / "a.wav", timestamps_path=tmp_path / "t.json")
    flags = {"gfx": True, "quality": "looks", "debug": False, "sfx": True, "sparse": True, "hook": None, "no_subs": False}
    _plan_a_disco(tmp_path, PLAN)
    h0 = fase2b._segment_hash(plan, tmp_path, flags)
    _plan_a_disco(tmp_path, PLAN_B)
    assert fase2b._segment_hash(plan, tmp_path, flags) != h0


# ─── R8: el negro de cierre dentro del segmento ───

def test_r8_pausa_de_cierre_es_pregunta_mas_negro():
    assert gl.pausa_de_cierre({}) == 0.0
    assert gl.pausa_de_cierre({"chapter_question": None, "black_hold": {"duration": 1.0}}) == 0.0
    assert gl.pausa_de_cierre({"chapter_question": {"pause": 6.4}}) == 6.4
    assert gl.pausa_de_cierre(PLAN_Q) == 3.0


def test_r8_pausa_a_disco_escribe_o_borra_gfx_pause(tmp_path):
    f = tmp_path / "gfx_pause_ch02.json"
    assert gl.pausa_a_disco(tmp_path, "ch02", PLAN_Q) == 3.0
    assert json.loads(f.read_text(encoding="utf-8")) == {"pause": 3.0, "text": "¿Quién lo decidió?"}
    assert gl.pausa_a_disco(tmp_path, "ch02", PLAN) == 0.0 and not f.exists()


def test_r8_plan_congelado_alarga_el_base_con_el_negro(env):
    """Antes: con el plan fijo se alargaba solo `chapter_question.pause` (2.0) y el black_hold (12.0–13.0) quedaba
    fuera del clip (10 + 2 = 12.0). Ahora: pregunta + negro (3.0); el clip termina donde termina el negro."""
    _plan_a_disco(env.work, PLAN_Q)
    out = _gfx(env)                                           # sin override: plan congelado desde disco
    assert out == env.work / "ch02_gfx.mp4"
    assert env.extendido == [3.0]
    esc = json.loads((env.work / "gfx_escenas_ch02.json").read_text(encoding="utf-8"))
    assert esc["clip_dur"] == 13.0 and esc["pausa"] == 3.0
    bh = PLAN_Q["black_hold"]
    assert bh["start"] + bh["duration"] == esc["clip_dur"]       # el negro termina con el clip: está adentro
    assert json.loads((env.work / "gfx_pause_ch02.json").read_text(encoding="utf-8"))["pause"] == 3.0
    assert "pausa de cierre (plan fijo): 3.000s = pregunta 2.000 + negro 1.000" in _log(env)


def test_r8_closing_question_y_el_plan_fijo_dan_la_misma_pausa(tmp_path):
    """La misma cuenta en los dos caminos: closing_question devuelve lo que pausa_de_cierre lee del plan que dejó."""
    txt = "¿Quién decidió que siguiera durmiendo?"
    resolved: dict = {}
    pausa = gl.closing_question(resolved, {"realizador": {"beats": [{"n": 3, "cierre": txt}]}}, tmp_path, "ch02", 10.0, [])
    assert pausa == gl.pausa_de_cierre(resolved) > resolved["chapter_question"]["pause"]
    assert json.loads((tmp_path / "gfx_pause_ch02.json").read_text(encoding="utf-8"))["pause"] == pausa


# ─── A.3: costuras medidas en el mp4 ───

def _lavfi_tramos(tmp_path: Path, nombre: str, tramos: list[tuple[str, float]]) -> Path:
    """mp4 chico a 30 fps: los tramos (color, segundos) uno detrás del otro."""
    assert fase2b.FFMPEG is not None
    out = tmp_path / nombre
    cmd = [fase2b.FFMPEG, "-v", "error", "-y"]
    for color, s in tramos:
        cmd += ["-f", "lavfi", "-i", f"color=c={color}:s=64x64:r=30:d={s}"]
    if len(tramos) > 1:
        cmd += ["-filter_complex", "".join(f"[{i}:v]" for i in range(len(tramos))) + f"concat=n={len(tramos)}:v=1:a=0[v]",
                "-map", "[v]"]
    cmd += ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30", str(out)]
    subprocess.run(cmd, check=True, capture_output=True, timeout=120)
    return out


def _lavfi(tmp_path: Path, nombre: str, rojo_s: float, negro_s: float) -> Path:
    """mp4 chico: `rojo_s` de rojo y después `negro_s` de negro (0 = sin negro)."""
    return _lavfi_tramos(tmp_path, nombre, [("red", rojo_s)] + ([("black", negro_s)] if negro_s > 0 else []))


@pytest.mark.skipif(fase2b.FFMPEG is None, reason="sin ffmpeg")
def test_a3_medir_cierre_con_negro(tmp_path):
    seg = _lavfi(tmp_path, "con_negro.mp4", 2.0, 1.0)
    m = fase2b._medir_cierre(seg, 3.0, 1.0, 30)
    assert m["duracion_ok"] and m["negro_ok"], m
    t = m["negro_detectado"][-1]                              # la corrida toca el fin: se le suma su último cuadro
    assert t["al_fin"] and abs(t["black_end"] - 3.0) <= 1 / 30 + 1e-6 and abs(t["black_duration"] - 1.0) <= 1 / 30 + 1e-6
    assert m["tolerancia_s"] == round(1 / 30, 4) and m["blackdetect_d"] == round(1.0 - 2 / 30, 4)
    # un negro de 1 s que NO llega al cierre (rojo 1 + negro 1 + rojo 1) no cuenta
    medio = _lavfi_tramos(tmp_path, "medio.mp4", [("red", 1.0), ("black", 1.0), ("red", 1.0)])
    m2 = fase2b._medir_cierre(medio, 3.0, 1.0, 30)
    assert m2["duracion_ok"] and m2["negro_ok"] is False and m2["negro_detectado"] == []
    # duración distinta a la esperada → ✗ aunque el negro esté
    assert not fase2b._medir_cierre(seg, 2.0, 1.0, 30)["duracion_ok"]
    # sin negro planeado no se mide negro
    assert fase2b._medir_cierre(seg, 3.0, 0.0, 30)["negro_ok"] is None


@pytest.mark.skipif(fase2b.FFMPEG is None, reason="sin ffmpeg")
def test_a3_medir_cierre_sin_negro(tmp_path):
    seg = _lavfi(tmp_path, "sin_negro.mp4", 3.0, 0.0)
    m = fase2b._medir_cierre(seg, 3.0, 1.0, 30)
    assert m["duracion_ok"] and m["negro_ok"] is False and m["negro_detectado"] == []


@pytest.mark.skipif(fase2b.FFMPEG is None, reason="sin ffmpeg")
def test_a3_lineas_de_costura_contra_el_guion(tmp_path, monkeypatch):
    work = tmp_path / "_fase2b_work"
    work.mkdir()
    _plan_a_disco(work, PLAN_Q)
    (work / "gfx_escenas_ch02.json").write_text(json.dumps({"cap": "ch02", "clip_dur": 3.0, "time_offset": 0.0,
                                                              "pre_roll": 0.0, "pausa": 3.0, "escenas": []}), encoding="utf-8")
    plan = SimpleNamespace(chapter_id="ch02", audio_duration=0.5, is_first=True)      # is_first: sin pre-roll
    con = _lavfi(tmp_path, "con.mp4", 2.0, 1.0)
    sin = _lavfi(tmp_path, "sin.mp4", 3.0, 0.0)
    # sin guion: la cuenta del guion sobre gfx_escenas
    lineas = fase2b._costura_del_segmento(plan, con, work, hook=None)
    assert lineas[0].startswith("✓ costura ch02: segmento 3.000 s vs gfx_escenas 3.000 s") and lineas[1].startswith("✓ costura ch02: negro de 1.00 s")
    # con guion: lo aprobado manda
    (tmp_path / "GUION_PANTALLA.json").write_text(json.dumps({"caps": [{"cap": "ch02", "seg_dur": 3.0}]}), encoding="utf-8")
    lineas = fase2b._costura_del_segmento(plan, sin, work, hook=None)
    assert lineas[0].startswith("✓ costura ch02: segmento 3.000 s vs guion 3.000 s")
    assert lineas[1].startswith("✗ costura ch02: negro de 1.00 s") and lineas[1].endswith("ninguno")
    (tmp_path / "GUION_PANTALLA.json").write_text(json.dumps({"caps": [{"cap": "ch02", "seg_dur": 4.0}]}), encoding="utf-8")
    assert fase2b._costura_del_segmento(plan, con, work, hook=None)[0].startswith("✗ costura ch02: segmento 3.000 s vs guion 4.000 s")
    # sin pregunta en el plan: no hay negro que medir
    _plan_a_disco(work, PLAN)
    assert "sin negro que medir" in fase2b._costura_del_segmento(plan, con, work, hook=None)[1]


def test_a3_el_chequeo_nunca_tira_el_render(tmp_path):
    """F38e §A.3: un plan incompleto (como los falsos de test_module_f28c, sin `is_first`) o un segmento inexistente dan
    una línea «✗ costura …: no se pudo medir», nunca una excepción (en paralelo una excepción hacía caer el cap)."""
    plan = SimpleNamespace(chapter_id="ch09")
    lineas = fase2b._costura_del_segmento(plan, tmp_path / "no_existe.mp4", tmp_path / "w", hook=None)
    assert len(lineas) == 1 and lineas[0].startswith("✗ costura ch09: no se pudo medir (")


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
