"""
test_module_f30b.py — F30b: transiciones por relato (§A), costura entre caps a negro y pre-roll del title card (§B),
chascada de comillas en el .ass (§C.3). Sin red; los de ffmpeg usan clips sintéticos chicos.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import numpy as np

from gfx_config import gfx_rules
from script_engine.gfx_project import GfxScene
from script_engine.gfx_style import ZOOM_PUNCH_SCALE, transiciones_por_relato


def _sc(starts: list[float], end: float, ranks: list[str] | None = None) -> list[GfxScene]:
    ranks = ranks or ["R3"] * len(starts)
    return [GfxScene(i, a, starts[i + 1] if i + 1 < len(starts) else end, ranks[i]) for i, a in enumerate(starts)]


BEATS = [{"n": 10, "funcion": "pico", "t0": 0.0, "t1": 29.5}, {"n": 11, "funcion": "respiro", "t0": 30.0, "t1": 60.0}]


def _plan(lupa: int | None = 0, ticker: float | None = 42.0) -> dict:
    return {"pico": {"t": 21.0, "beat": 10},
            "evidence_zoom": {"scene_idx": lupa, "start": 5.0} if lupa is not None else None,
            "time_ticker": {"start": ticker, "duration": 6.0} if ticker is not None else None}


# ═══════════════ A: transiciones por relato ═══════════════

def test_seis_escenas_lupa_pico_beat_ticker_cierre():
    sc = _sc([0, 10, 20, 30, 40, 50], 60)
    tr = transiciones_por_relato(sc, _plan(), BEATS)
    assert [tr[k]["kind"] for k in sorted(tr)] == ["cut", "zoom_punch", "dissolve", "dissolve", "dip"]
    assert [tr[k]["why"] for k in sorted(tr)] == ["corte", "pico", "cambio de beat", "salto de tiempo",
                                                   "cierre"]                 # F36 §D: sin la regla de la lupa
    assert tr[2]["frames"] == 12 and tr[3]["frames"] == gfx_rules.crossfade_frames and tr[5]["frames"] == gfx_rules.dip_frames


def test_sin_lupa_no_hay_corte_despues_de_la_lupa_y_un_solo_punch():
    sc = _sc([0, 10, 20, 25, 30, 40, 50], 60)
    tr = transiciones_por_relato(sc, _plan(lupa=None, ticker=None), BEATS)
    assert not any(t["why"] == "después de la lupa" for t in tr.values())
    assert sum(t["kind"] == "zoom_punch" for t in tr.values()) == 1
    assert tr[2]["kind"] == "zoom_punch"                                   # el corte más cercano a pico.t (21 s)
    assert tr[1]["kind"] == "cut" and tr[1]["why"] == "corte"


def test_pico_sin_corte_en_su_beat_no_hay_punch():
    sc = _sc([0, 30, 45], 60)
    tr = transiciones_por_relato(sc, {"pico": {"t": 21.0, "beat": 10}}, BEATS)
    assert not any(t["kind"] == "zoom_punch" for t in tr.values())


def test_emotional_rank_no_cambia_nada():
    a = transiciones_por_relato(_sc([0, 10, 20, 30, 40, 50], 60, ["R1"] * 6), _plan(), BEATS)
    b = transiciones_por_relato(_sc([0, 10, 20, 30, 40, 50], 60, ["R3"] * 6), _plan(), BEATS)
    assert [(v["kind"], v["why"]) for v in a.values()] == [(v["kind"], v["why"]) for v in b.values()]
    assert not any(v["kind"] in ("flash", "cut_punch") for v in a.values())


def test_zoom_punch_en_el_stitch_mitad_antes_y_mitad_despues():
    from script_engine.gfx_sparse import stitch_graph, stitch_segments, transition_span
    tr = {"kind": "zoom_punch", "frames": 12}
    lo, hi = transition_span(10.0, tr, 30)
    assert abs(hi - 10.2) < 1e-9 and lo < 9.8
    segs = stitch_segments([], 20.0, 30, [(10.0, tr)])
    kinds = [(s["kind"], s["k0"], s["k1"]) for s in segs]
    assert ("zp_out", 294, 300) in kinds and ("zp_in", 300, 306) in kinds
    g, _ = stitch_graph(segs, 30, 640, 360)
    assert sum("zoompan" in x for x in g) == 2 and str(ZOOM_PUNCH_SCALE) in " ".join(g)


# ═══════════════ B.1: costura a negro ═══════════════

def _clip(path: Path, color: str, dur: float, tono: int) -> Path:
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"color=c={color}:s=160x90:r=30:d={dur}",
                    "-f", "lavfi", "-i", f"sine=frequency={tono}:duration={dur}", "-c:v", "libx264", "-preset",
                    "ultrafast", "-g", "15", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", str(path)], check=True)
    return path


def _lumas(video: Path) -> np.ndarray:
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", str(video), "-vf", "scale=32:18,format=gray", "-f", "rawvideo",
                        "-"], capture_output=True, check=True)
    return np.frombuffer(r.stdout, np.uint8).reshape(-1, 18, 32).mean(axis=(1, 2))


def test_union_cap_a_cap_es_negro_y_nunca_blanco(tmp_path):
    from script_engine.transition_applier import concat_windowed
    a = _clip(tmp_path / "a.mp4", "black", 3.0, 440)
    b = _clip(tmp_path / "b.mp4", "gray", 3.0, 660)
    out = concat_windowed([a, b], tmp_path / "f.mp4", tmp_path, ["SUBMARINE", "SUBMARINE"], "ffmpeg", "ffprobe",
                          ["-c:v", "libx264", "-preset", "ultrafast", "-g", "15"], negro_frames=10)
    lu = _lumas(tmp_path / "_concat_video.ts")
    assert len(lu) == 180                                                   # sin solapar: 90 + 90
    assert lu.max() < 200                                                   # ningún blanco
    assert lu[90] < 20 and lu[95] < lu[99] < lu[110] and abs(lu[110] - lu[170]) < 3   # sube desde negro en 10 f
    assert out.exists()


def test_concat_segments_con_gfx_no_cae_al_xfade_de_arte():
    src = Path("fase2b.py").read_text(encoding="utf-8")
    assert "negro_frames=int(_gr_cat.dip_frames) if gfx else None" in src
    assert "if negro_frames:                                            # F30b §B.1" in src


# ═══════════════ B.3: pre-roll del title card ═══════════════

def test_pre_roll_corre_los_subtitulos_y_la_chascada_saca_las_comillas(tmp_path):
    import fase2b
    words = [{"word": "Dijo", "start": 1.0, "end": 1.3}, {"word": "«basta»", "start": 1.4, "end": 1.9},
             {"word": "y…", "start": 2.0, "end": 2.2}, {"word": "calló.", "start": 2.3, "end": 2.8}]
    a = fase2b._build_ass_from_words(words=words, output_path=tmp_path / "a.ass", audio_duration=4.0,
                                     video_width=2560, video_height=1440)
    b = fase2b._build_ass_from_words(words=words, output_path=tmp_path / "b.ass", audio_duration=7.0,
                                     video_width=2560, video_height=1440, pre_pad=3.0, sin_comillas=True)
    la = [x for x in a.read_text(encoding="utf-8").splitlines() if x.startswith("Dialogue")]
    lb = [x for x in b.read_text(encoding="utf-8").splitlines() if x.startswith("Dialogue")]
    assert "«BASTA»" in la[1] and "BASTA" in lb[1] and "«" not in "".join(lb) and "»" not in "".join(lb)
    assert "…" not in "".join(lb)
    ta = [fase2b._format_ass_time(1.4), fase2b._format_ass_time(4.4)]
    assert ta[0] in la[1] and ta[1] in lb[1]                                # mismos tiempos + title_dur


def test_visual_con_pre_roll_agrega_title_dur_de_primer_cuadro(tmp_path):
    import fase2b
    fase2b.FFMPEG = fase2b.FFMPEG or "ffmpeg"
    src = tmp_path / "v.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "testsrc=s=160x90:r=30:d=2", "-c:v",
                    "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", str(src)], check=True)
    out = fase2b._visual_con_pre_roll(src, 3.0, tmp_path / "p.mp4", 30)
    n = int(subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries",
                            "stream=nb_read_frames", "-of", "csv=p=0", str(out)], capture_output=True, text=True).stdout)
    assert n == 150


def test_pieza_de_musica_cubre_el_pre_roll(tmp_path):
    """F32 §B.1: la música del cap arranca con el title card (antes la pieza se corría con silencio adelante)."""
    import fase2b
    fase2b.FFMPEG = fase2b.FFMPEG or "ffmpeg"
    tone = tmp_path / "t.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "sine=frequency=300:duration=10", str(tone)],
                   check=True)
    p = fase2b._build_music_piece_for_chapter(tone, 4.0, tmp_path / "p.wav", pre_sec=3.0)
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", str(p), "-f", "s16le", "-ac", "1", "-ar", "1000", "-"],
                       capture_output=True, check=True)
    x = np.abs(np.frombuffer(r.stdout, np.int16).astype(float))
    assert abs(len(x) / 1000 - 7.0) < 0.02 and x[100:2900].mean() > 1000 and x[3200:].mean() > 1000


def test_critico_reusa_el_veredicto_por_identidad_del_bloque(tmp_path):
    """F37 §B.1: el crítico corre por intento (gfx_critic.estorba); la identidad es el bloque en su instante y su lado
    (descripción) con su voz: el mismo intento reusa su veredicto, otro instante no."""
    from script_engine.gfx_critic import PROMPT_VERSION_ROT, build_prompt_rot, clave_identidad, describe, estorba, voice_vecinas
    words = [{"word": "x.", "start": 0.0, "end": 1.0}]
    c = {"text": "1.910 personas", "kicker": "Muertos", "ficha": True, "start": 13.0, "duration": 4.0,
         "rotulista": True, "pool_id": "D128", "aporta": "la cifra", "sentence_idx": 0}
    voz = voice_vecinas(words, 0, 13.0, 0.0)
    assert build_prompt_rot(describe("ficha", c), voz, "", "")
    (tmp_path / "gfx_critic_rot_ch06.json").write_text(json.dumps(
        {clave_identidad("estorba", "ch06", "ficha", 13.0, describe("ficha", c), voz, PROMPT_VERSION_ROT):
         {"estorba": False, "motivo_3": "no tapa"}}), encoding="utf-8")

    def call(*a):
        raise AssertionError("no tenía que llamar a Gemini")
    row = estorba("ficha", c, base=tmp_path / "no.mp4", words=words, time_offset=0.0, work_dir=tmp_path, cap="ch06",
                  log=[], call=call)
    assert row["pasa"] and row["veredicto"] == "no estorba" and row["texto"] == "1.910 personas"
    otro = estorba("ficha", {**c, "start": 20.0}, base=tmp_path / "no.mp4", words=words, time_offset=0.0,
                   work_dir=tmp_path, cap="ch06", log=[], call=call)
    assert otro["veredicto"] == "error" and otro["pasa"]            # otro instante: no reusa (sin Gemini, queda)
