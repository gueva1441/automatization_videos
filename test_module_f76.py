"""F76 — master −14 LUFS del mp4 final (script_engine/audio_master.py). Sin red ni API: el bucle se prueba con
mediciones simuladas; la prueba con ffmpeg real usa un mp4 sintético de lavfi (testsrc + sine) en tmp_path."""
import ast
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

R = Path(__file__).resolve().parent
sys.path.insert(0, str(R))

from script_engine import audio_master as am  # noqa: E402

LUFS = am.perfil("master_lufs")
TP = am.perfil("master_tp_dbtp")
TOL = am.perfil("master_lufs_tol_lu")


def _simulada(medidas):
    """pasada(G, techo) que devuelve las medidas en orden y anota con qué G/techo la llamaron."""
    llamadas, it = [], iter(medidas)

    def pasada(g, techo):
        llamadas.append((round(g, 2), round(techo, 2)))
        return dict(next(it))
    return pasada, llamadas


# ─── el bucle con mediciones simuladas ───

def test_cierra_en_1_pasada():
    pasada, llamadas = _simulada([{"I": -14.1, "LRA": 6.0, "pico": -1.6}])
    tabla, elegida, aviso = am.bucle({"I": -24.0, "LRA": 6.6, "pico": -6.6}, pasada)
    assert len(tabla) == 1 and elegida is tabla[0] and aviso is None
    assert llamadas == [(10.0, TP)]              # G = −14 − (−24); techo arranca en el techo de pico
    assert elegida["falla"] == 0


def test_cierra_en_3_pasadas_como_la_tabla_del_handoff():
    medidas = [{"I": -14.3, "LRA": 6.0, "pico": -0.3},
               {"I": -14.5, "LRA": 5.5, "pico": -1.0},
               {"I": -14.4, "LRA": 5.1, "pico": -1.5}]
    pasada, llamadas = _simulada(medidas)
    tabla, elegida, aviso = am.bucle({"I": -24.0, "LRA": 6.6, "pico": -6.6}, pasada)
    # G y techo exactos de la tabla: (+10,00 −1,50) (+10,30 −2,70) (+10,80 −3,20)
    assert llamadas == [(10.0, -1.5), (10.3, -2.7), (10.8, -3.2)]
    assert [(f["G"], f["techo"]) for f in tabla] == llamadas
    assert len(tabla) == 3 and elegida is tabla[2] and aviso is None
    assert [f["falla"] for f in tabla] == [1.2, 0.5, 0.0]


def test_actualizacion_de_g_y_techo_segun_la_receta():
    """techo −= max(0, pico − tp); G += lufs − I. Pico bajo el techo → el techo no se mueve; G sube o baja."""
    medidas = [{"I": -15.2, "LRA": 6.0, "pico": -2.0},     # pico cumple → techo igual; faltan 1,2 LU → G +1,2
               {"I": -13.4, "LRA": 6.0, "pico": -1.2},     # pico +0,3 sobre el techo → techo −0,3; sobran 0,6 → G −0,6
               {"I": -14.0, "LRA": 6.0, "pico": -1.5}]
    pasada, llamadas = _simulada(medidas)
    original = {"I": -20.0, "LRA": 6.6, "pico": -5.0}
    tabla, elegida, aviso = am.bucle(original, pasada)
    g0 = LUFS - original["I"]
    esperadas = [(round(g0, 2), TP),
                 (round(g0 + (LUFS - -15.2), 2), TP),
                 (round(g0 + (LUFS - -15.2) + (LUFS - -13.4), 2), round(TP - (-1.2 - TP), 2))]
    assert llamadas == esperadas
    assert aviso is None and elegida is tabla[-1]


def test_sin_progreso_queda_la_mejor_que_cumple_pico_con_aviso():
    medidas = [{"I": -15.0, "LRA": 6.0, "pico": -1.6},      # falla 0,5 (sonoridad), cumple pico
               {"I": -13.0, "LRA": 6.0, "pico": -1.0}]      # falla 1,0 ≥ 0,5 → para
    pasada, _ = _simulada(medidas)
    tabla, elegida, aviso = am.bucle({"I": -24.0, "LRA": 6.6, "pico": -6.6}, pasada)
    assert len(tabla) == 2
    assert elegida is tabla[0] and elegida["pico"] <= TP
    assert aviso and aviso.startswith("⚠") and "NINGUNA" not in aviso


def test_sin_progreso_y_ninguna_cumple_pico_queda_la_de_menor_pico():
    medidas = [{"I": -16.0, "LRA": 6.0, "pico": -1.0},      # falla 0,5 + 1,5 = 2,0
               {"I": -11.0, "LRA": 6.0, "pico": -1.2}]      # falla 0,3 + 2,5 = 2,8 → para
    pasada, _ = _simulada(medidas)
    tabla, elegida, aviso = am.bucle({"I": -24.0, "LRA": 6.6, "pico": -6.6}, pasada)
    assert elegida is tabla[1]                              # menor pico, aunque no sea la de menor falla
    assert aviso and aviso.startswith("⚠") and "NINGUNA" in aviso


def test_falla_es_la_formula_del_handoff():
    assert am.falla({"I": -14.0, "pico": -1.5}, LUFS, TP, TOL) == 0
    assert am.falla({"I": -14.5, "pico": -1.5}, LUFS, TP, TOL) == 0          # dentro de ±0,5 LU
    assert am.falla({"I": -15.0, "pico": -1.0}, LUFS, TP, TOL) == pytest.approx(0.5 + 0.5)


# ─── la cadena y las constantes ───

def test_cadena_latency_oversample_y_limite_del_techo():
    c = am.cadena(10.0, -2.7)
    assert "latency=1" in c
    ov = am.perfil("master_oversample")
    assert f"aresample={am.SAMPLE_RATE * ov}" in c and am.SAMPLE_RATE * ov == 176400
    assert c.endswith(f"aresample={am.SAMPLE_RATE}")
    assert f"limit={10 ** (-2.7 / 20):.6f}" in c
    assert "level=disabled" in c and c.startswith("volume=10.00dB,")


def test_audio_master_no_tiene_el_menos_2_dbfs_de_f75():
    src = (R / "script_engine" / "audio_master.py").read_text(encoding="utf-8")
    assert not re.search(r"[-−]\s*2(\.0+)?\s*dB", src)
    arbol = ast.parse(src)
    indices = {id(x) for s in ast.walk(arbol) if isinstance(s, ast.Subscript) for x in ast.walk(s.slice)}
    for n in ast.walk(arbol):                                            # tabla[-2] es un índice, no un nivel
        if id(n) not in indices and isinstance(n, ast.UnaryOp) and isinstance(n.op, ast.USub) and isinstance(n.operand, ast.Constant):
            assert n.operand.value != 2, "literal −2 en audio_master.py"


def test_constantes_del_perfil():
    from audio_profiles import AUDIO_PROFILES
    p = AUDIO_PROFILES["MISTERIO_ABISAL"]
    assert (p["master_lufs"], p["master_tp_dbtp"], p["master_oversample"], p["master_lufs_tol_lu"], p["aac_bitrate"]) \
        == (-14.0, -1.5, 4, 0.5, "192k")


# ─── cableado (inspección de fuente) ───

def test_fase2b_llama_al_master_una_vez_justo_antes_de_final_dur():
    lineas = (R / "fase2b.py").read_text(encoding="utf-8").splitlines()
    llamadas = [i for i, l in enumerate(lineas) if re.search(r"\bmaster_mp4\(", l)]
    assert len(llamadas) == 1
    i = llamadas[0]
    assert lineas[i].strip() == "master_mp4(final_path, ffmpeg=FFMPEG, log=print)"
    siguiente = next(l for l in lineas[i + 1:] if l.strip())
    assert siguiente == "    final_dur = _get_duration(final_path)"
    assert lineas[i].startswith("    master_mp4(")                  # nivel de la función: común a (a)/(b)/(c)
    assert sum(l == "    final_dur = _get_duration(final_path)" for l in lineas) == 1
    assert any(l.startswith("from script_engine.audio_master import") for l in lineas)


def test_sin_literal_192k_y_audio_manager_usa_la_constante():
    for f in ("fase2b.py", "script_engine/transition_applier.py"):
        assert '"192k"' not in (R / f).read_text(encoding="utf-8"), f
    am_src = (R / "audio_manager.py").read_text(encoding="utf-8")
    assert "TP=-1.5" not in am_src
    assert "TP={_master_perfil('master_tp_dbtp')}" in am_src
    import fase2b
    assert fase2b.AAC_BITRATE == "192k"                               # sin cambio de salida


# ─── ffmpeg real sobre un mp4 sintético ───

FF = shutil.which("ffmpeg")


def _md5_video(ff, p):
    r = subprocess.run([ff, "-v", "error", "-i", str(p), "-map", "0:v", "-c", "copy", "-f", "md5", "-"],
                       capture_output=True, text=True, check=True)
    return r.stdout.strip()


def _dur_audio(p):
    fp = shutil.which("ffprobe")
    r = subprocess.run([fp, "-v", "error", "-select_streams", "a:0", "-show_entries", "stream=duration",
                        "-of", "csv=p=0", str(p)], capture_output=True, text=True, check=True)
    return float(r.stdout.strip())


@pytest.mark.skipif(FF is None, reason="sin ffmpeg")
def test_master_mp4_real_video_intacto_y_audio_mas_fuerte(tmp_path):
    mp4 = tmp_path / "x_final_gfx.mp4"
    subprocess.run([FF, "-v", "error", "-y", "-f", "lavfi", "-i", "testsrc=size=160x120:rate=30:duration=4",
                    "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=44100:duration=4",
                    "-af", "volume=0.1", "-ac", "2", "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", am.perfil("aac_bitrate"), "-shortest", str(mp4)],
                   check=True, capture_output=True)
    md5_antes = _md5_video(FF, mp4)
    dur_antes = _dur_audio(mp4)
    antes = am.medir(mp4, FF)
    log = []
    res = am.master_mp4(mp4, ffmpeg=FF, log=log.append)
    assert _md5_video(FF, mp4) == md5_antes                           # -c:v copy: el video no cambia
    despues = am.medir(mp4, FF)
    assert despues["I"] > antes["I"] + 10                             # sintético a ~−38 → sube a ~−14
    el = res["elegida"]
    assert res["aviso"] is None, res
    assert abs(el["I"] - LUFS) <= TOL and el["pico"] <= TP
    assert abs(despues["I"] - LUFS) <= TOL and despues["pico"] <= TP  # lo remuxado es la pasada elegida
    assert abs(_dur_audio(mp4) - dur_antes) <= 1 / 30                # duración del audio: ≤ 1 cuadro
    assert any("elegida" in l for l in log)
    assert sorted(p.name for p in tmp_path.iterdir()) == ["x_final_gfx.mp4"]   # sin temporales
