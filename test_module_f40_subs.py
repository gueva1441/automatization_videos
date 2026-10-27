"""
test_module_f40_subs.py — F40 §B: subtítulos documentales en long-form (DECISIONES 2026-10-27 03:34), karaoke solo en
Shorts. Sintético, sin red ni ffmpeg: arma los .ass con palabras inventadas y mira el estilo, los cortes y los tiempos.
"""
from __future__ import annotations

import json
from pathlib import Path

import fase2b


def _t(s: str) -> float:
    h, m, sec = s.split(":")
    return int(h) * 3600 + int(m) * 60 + float(sec)


def _palabras(texto: str, t0: float = 0.5, paso: float = 0.3, pausa: float = 0.5) -> list[dict]:
    """Una palabra cada `paso` s; después de un punto, `pausa` s de silencio."""
    out, t = [], t0
    for w in texto.split():
        out.append({"word": w, "start": round(t, 3), "end": round(t + paso * 0.8, 3)})
        t += paso + (pausa if w.endswith((".", "?", "!")) else 0.0)
    return out


TEXTO = ("Longarone está en el fondo del valle del Piave. El río pasa por delante del pueblo y, enfrente, desde una "
         "garganta lateral, baja un torrente que se llama Vajont y que desemboca en el Piave justo frente a Longarone "
         "y Castellavazzo. La empresa era SADE. No. La gente llamaba al monte Toc «la montaña que camina», y lo decían "
         "los residentes desde antes… de que nadie fuera a medirla.")


def _doc(tmp_path: Path, words: list[dict], **kw) -> tuple[str, list[tuple[float, float, list[str]]]]:
    out = fase2b._build_ass_documental(words=words, output_path=tmp_path / "doc.ass",
                                       audio_duration=kw.pop("audio_duration", 120.0), video_width=1920,
                                       video_height=1080, **kw)
    src = out.read_text(encoding="utf-8")
    ev = []
    for ln in src.splitlines():
        if ln.startswith("Dialogue:") and ",Documental," in ln:
            p = ln.split(",", 9)
            ev.append((_t(p[1]), _t(p[2]), p[9].split("\\N")))
    return src, ev


def _estilo(src: str, nombre: str) -> list[str]:
    linea = next(ln for ln in src.splitlines() if ln.startswith(f"Style: {nombre},"))
    return linea[len("Style: "):].split(",")


# ═══════════════ estilo ═══════════════

def test_estilo_documental_constantes_de_f40(tmp_path):
    src, ev = _doc(tmp_path, _palabras(TEXTO))
    st = _estilo(src, "Documental")
    assert st[1] == "Anton"                                   # fonts.subs del perfil
    assert float(st[2]) == 60                                 # 60 px a 1080p
    assert st[3] == "&H00FFFFFF" and st[5] == "&H00000000"    # blanco con borde negro
    assert float(st[16]) == 4 and float(st[17]) == 2          # borde 4, sombra 2
    assert st[21] == "108"                                    # MarginV del Viral
    assert "0000FFFF" not in ",".join(st)                     # sin amarillo
    eventos = [ln for ln in src.splitlines() if ln.startswith("Dialogue:")]
    assert eventos and all(",Documental," in ln for ln in eventos)
    assert "\\k" not in src and "\\c&" not in src and "\\t(" not in src and "\\fscx" not in src   # sin resaltado


def test_estilo_escala_con_el_alto_del_video(tmp_path):
    out = fase2b._build_ass_documental(words=_palabras("Hola mundo."), output_path=tmp_path / "a.ass",
                                       audio_duration=5.0, video_width=2560, video_height=1440)
    st = _estilo(out.read_text(encoding="utf-8"), "Documental")
    assert float(st[2]) == 80 and abs(float(st[16]) - 16 / 3) < 1e-3 and abs(float(st[17]) - 8 / 3) < 1e-3
    assert st[21] == "108"


def test_fuente_sale_del_perfil(tmp_path, monkeypatch):
    import gfx_config
    monkeypatch.setitem(gfx_config.ACTIVE_PROFILE, "fonts", {**gfx_config.ACTIVE_PROFILE["fonts"], "subs": "OtraFuente"})
    src, _ = _doc(tmp_path, _palabras("Hola mundo."))
    assert _estilo(src, "Documental")[1] == "OtraFuente"


# ═══════════════ cortes y tiempos ═══════════════

def test_renglones_y_duraciones_dentro_de_netflix(tmp_path):
    _, ev = _doc(tmp_path, _palabras(TEXTO))
    assert len(ev) >= 4
    for a, b, renglones in ev:
        assert 1 <= len(renglones) <= 2
        assert all(len(r) <= 42 for r in renglones)
        assert 0.833 <= round(b - a, 2) <= 7.0


def test_texto_sin_mayusculas_forzadas_ni_comillas(tmp_path):
    src, ev = _doc(tmp_path, _palabras(TEXTO))
    texto = " ".join(" ".join(r) for _, _, r in ev)
    assert "la montaña que camina," in texto and "Longarone está en el fondo" in texto
    assert "«" not in src and "»" not in src and "…" not in src
    assert texto != texto.upper()


def test_un_evento_por_oracion_cuando_entra(tmp_path):
    _, ev = _doc(tmp_path, _palabras("La empresa era SADE. El experto decía que no."))
    assert [" ".join(r) for _, _, r in ev] == ["La empresa era SADE.", "El experto decía que no."]


def test_oracion_larga_se_parte_en_la_pausa(tmp_path):
    _, ev = _doc(tmp_path, _palabras("El río pasa por delante del pueblo y, enfrente, desde una garganta lateral, "
                                     "baja un torrente que se llama Vajont y que desemboca en el Piave justo frente "
                                     "a Longarone y Castellavazzo."))
    assert len(ev) >= 2
    assert ev[0][2][-1].endswith(",")                          # el primer corte cae en una coma


def test_tiempos_de_las_palabras(tmp_path):
    w = _palabras("La empresa era SADE. El experto decía que no.")
    _, ev = _doc(tmp_path, w)
    assert ev[0][0] == round(w[0]["start"], 2) and ev[1][0] == round(w[4]["start"], 2)


def test_evento_corto_se_estira_hasta_el_minimo(tmp_path):
    w = [{"word": "No.", "start": 1.0, "end": 1.2}, {"word": "Sí.", "start": 3.0, "end": 3.2}]
    _, ev = _doc(tmp_path, w)
    assert [round(b - a, 2) >= 0.833 for a, b, _ in ev] == [True, True]
    assert ev[0][0] == 1.0


def test_evento_corto_sin_silencio_se_junta_con_el_vecino(tmp_path):
    w = [{"word": "No.", "start": 1.0, "end": 1.2}, {"word": "Nunca", "start": 1.3, "end": 1.6},
         {"word": "lo", "start": 1.6, "end": 1.7}, {"word": "dijo.", "start": 1.7, "end": 2.4}]
    _, ev = _doc(tmp_path, w)
    assert len(ev) == 1 and " ".join(ev[0][2]) == "No. Nunca lo dijo."


def test_maximo_siete_segundos(tmp_path):
    w = _palabras("una oración muy lenta que no termina nunca y sigue y sigue sin punto", paso=0.9)
    _, ev = _doc(tmp_path, w)
    assert len(ev) >= 2 and all(round(b - a, 2) <= 7.0 for a, b, _ in ev)


def test_pre_pad_corre_los_subtitulos(tmp_path):
    w = _palabras("La empresa era SADE.")
    _, ev0 = _doc(tmp_path, w)
    _, ev3 = _doc(tmp_path, w, pre_pad=3.0, audio_duration=123.0)
    assert round(ev3[0][0] - ev0[0][0], 2) == 3.0


def test_hook_sigue_igual_en_long_form(tmp_path):
    src, _ = _doc(tmp_path, _palabras("Hola mundo."), hook_text="La presa", pre_pad=fase2b.HOOK_DURATION)
    k = tmp_path / "k.ass"
    fase2b._build_ass_from_words(words=[], output_path=k, audio_duration=5.0, video_width=1920, video_height=1080,
                                 hook_text="La presa")
    hook_k = [ln for ln in k.read_text(encoding="utf-8").splitlines() if ",Hook," in ln or ln.startswith("Style: Hook")]
    hook_d = [ln for ln in src.splitlines() if ",Hook," in ln or ln.startswith("Style: Hook")]
    assert hook_k == hook_d and len(hook_d) == 2


def test_sin_palabras_ni_hook_archivo_vacio(tmp_path):
    out = fase2b._build_ass_documental(words=[], output_path=tmp_path / "v.ass", audio_duration=1.0,
                                       video_width=1920, video_height=1080)
    assert out.read_text(encoding="utf-8") == ""


# ═══════════════ long vs short en el segmento ═══════════════

def _plan(tmp_path: Path, video_type: str) -> fase2b.ChapterPlan:
    ts = tmp_path / "ch02_timestamps.json"
    ts.write_text(json.dumps(_palabras("La empresa era SADE. El experto decía que no.")), encoding="utf-8")
    return fase2b.ChapterPlan(chapter_id="ch02", engine="flux", audio_path=tmp_path / "a.mp3", audio_duration=6.0,
                              asset_paths=[], timestamps_path=ts, is_first=False, art_profile=None,
                              narration="La empresa era SADE. El experto decía que no.", video_type=video_type)


def _segmento(monkeypatch, tmp_path, video_type: str) -> str:
    """Corre _build_chapter_segment hasta el .ass (visual y ffmpeg falsos) y devuelve el .ass."""
    class Corte(Exception):
        pass
    monkeypatch.setattr(fase2b, "FFMPEG", "ffmpeg")
    monkeypatch.setattr(fase2b, "_visual_base", lambda *a, **k: tmp_path / "v.mp4")
    monkeypatch.setattr(fase2b, "_get_duration", lambda p: 6.0)

    def _run(cmd, timeout=240):
        raise Corte()
    monkeypatch.setattr(fase2b, "_run_cmd", _run)
    monkeypatch.setattr(fase2b.subprocess, "run", lambda *a, **k: (_ for _ in ()).throw(Corte()))
    try:
        fase2b._build_chapter_segment(_plan(tmp_path, video_type), tmp_path / "seg.mp4", tmp_path, hook_text=None,
                                      no_subs=False, video_width=1920, video_height=1080, fps=30)
    except Corte:
        pass
    return (tmp_path / "ch02_subs.ass").read_text(encoding="utf-8")


def test_long_form_quema_documental(monkeypatch, tmp_path):
    src = _segmento(monkeypatch, tmp_path, "long")
    assert "Style: Documental," in src and ",Viral," not in src.split("[Events]")[1]
    assert "La empresa era SADE." in src


def test_short_quema_karaoke_como_hoy(monkeypatch, tmp_path):
    src = _segmento(monkeypatch, tmp_path, "short")
    ev = [ln for ln in src.splitlines() if ln.startswith("Dialogue:")]
    assert ev and all(",Viral," in ln for ln in ev)
    assert "Style: Viral,Anton,150," in src and "\\c&H0000FFFF&" in src and "SADE." in src and "EMPRESA" in src


def test_script_lookup_lleva_el_video_type(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "data" / "scripts").mkdir(parents=True)
    (tmp_path / "data" / "scripts" / "x.json").write_text(json.dumps(
        {"video_type": "long", "chapters": [{"chapter_number": 1, "narration": "Hola."}]}), encoding="utf-8")
    assert fase2b._load_script_lookup("x")["ch01"]["video_type"] == "long"
