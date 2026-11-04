"""F73 D.1 (ADENDA 2): reconstruye la pista ducked y las piezas de música de Wittenoom en lab/hyperframes/f73/d/work/ con
`_build_continuous_music_track` y los MISMOS argumentos que `_mezcla_preview`, y mide el inicio de la música por cap con
dos copias de la medida que NO borran piezas: «hoy» (la de fase2b, +1e-9) y «con el cambio» (float64 + máscara de
ventanas con al menos una muestra != 0). Solo lee `_fase2b_work/` (copia al lab lo que las funciones leen de ahí).
Uso: python simular_d.py [--real]   (--real: además corre la función de fase2b sobre COPIAS de las piezas)"""
import json
import shutil
import sys
from pathlib import Path

R = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(R))

import numpy as np  # noqa: E402

import fase2b as fb  # noqa: E402
from config import DATA_DIR, OUTPUT_DIR, pipeline  # noqa: E402

TID = "123bbb64-9fca-4395-8bf4-57d60e219ef1"
WORK = OUTPUT_DIR / TID / "_fase2b_work"
LAB = Path(__file__).parent / "work"


def plans_y_segs():
    audio_dir = OUTPUT_DIR / "audio" / TID
    sync_map = json.loads((audio_dir / "sync_map.json").read_text(encoding="utf-8"))
    manifest = json.loads((OUTPUT_DIR / TID / "assets" / "assets_manifest.json").read_text(encoding="utf-8"))
    plans = fb._build_plans(sync_map, manifest, TID, audio_dir, fb._load_script_lookup(TID))
    g = json.loads((OUTPUT_DIR / TID / "GUION_PANTALLA.json").read_text(encoding="utf-8"))
    LAB.mkdir(parents=True, exist_ok=True)
    for p in plans:                                   # lo único que leen de work_dir: escenas (segmento) y pausas
        for n in (f"gfx_escenas_{p.chapter_id}.json", f"gfx_pause_{p.chapter_id}.json"):
            if (WORK / n).exists():
                shutil.copy2(WORK / n, LAB / n)
    gcaps = {c["cap"] if "cap" in c else c.get("id"): c for c in g["caps"]}
    segs = {}
    for p in plans:
        pre_pad = float(gcaps[p.chapter_id]["pre_pad"])
        segs[p.chapter_id] = fb._segmento_de_cap(p, LAB, pre_pad)
        assert abs(segs[p.chapter_id]["seg_dur"] - float(gcaps[p.chapter_id]["seg_dur"])) < 1e-6, p.chapter_id
    return plans, sync_map, segs, g


def intensidad_sin_escribir(plans, pauses):
    """`_mapa_intensidad` sin el write_text a output/audio/<id>/intensity_map.json."""
    from script_engine import music_intensity as mi
    steps = DATA_DIR / "scripts" / "_steps"
    dur = {p.chapter_id: p.audio_duration + (pauses or {}).get(p.chapter_id, 0.0) for p in plans}
    return mi.mapa_del_topic(TID, steps, OUTPUT_DIR / "audio" / TID, dur)


def mejor_lag_nuevo(tr, w):
    """El cambio propuesto (F73 D): correlación y norma en float64; solo son candidatas las posiciones cuya ventana tiene
    al menos una muestra != 0 (conteo exacto con cumsum de enteros), fuera ANTES de dividir."""
    tr, w = np.asarray(tr, dtype=np.float64), np.asarray(w, dtype=np.float64)
    m, n = len(w), len(tr) + len(w)
    c = np.fft.irfft(np.fft.rfft(tr, n) * np.conj(np.fft.rfft(w, n)), n)[:len(tr) - m + 1]
    cs = np.concatenate(([0.0], np.cumsum(tr ** 2)))
    nz = np.concatenate(([0], np.cumsum(tr != 0, dtype=np.int64)))
    validas = np.flatnonzero(nz[m:] - nz[:-m] > 0)
    if validas.size == 0:
        raise ValueError("la pista no tiene sonido en la búsqueda")
    e = cs[m:][validas] - cs[:-m][validas]
    return int(validas[np.argmax(c[validas] / np.sqrt(e))])


def medir(plans, pista, work_dir, seg_dur, intro, crossfade, fps, nuevo: bool):
    """Copia de fase2b._medir_inicio_musica (F72e) sin el unlink; `nuevo` = el cambio de F73 D."""
    from script_engine.gfx_guion import _pcm
    sr = 11025
    out, t_tc = [], intro
    VENTANA_S, BUSCA_S = 4.0, 20.0
    for i, p in enumerate(plans):
        cap = p.chapter_id
        pieza = work_dir / f"_music_piece_{cap}.wav"
        fila = {"cap": cap, "title_card_s": round(t_tc, 3)}
        entra = crossfade if i > 0 else 0.0
        pz = _pcm(pieza, 0.0, min(fb._get_duration(pieza), entra + BUSCA_S), sr)
        if pz is None or len(pz) < int((entra + VENTANA_S) * sr) or float(np.abs(pz).max()) == 0.0:
            fila.update({"medido_s": None, "ok": None})
        else:
            n_w = int(VENTANA_S * sr)
            cands = range(int(entra * sr), len(pz) - n_w, sr // 2)
            a = max(cands, key=lambda k: float(np.sqrt(np.mean(pz[k:k + n_w] ** 2))))
            w = pz[a:a + n_w]
            ini = max(0.0, t_tc + a / sr - BUSCA_S)
            tr = _pcm(pista, ini, 2 * BUSCA_S + VENTANA_S, sr)
            if not nuevo:
                n = len(tr) + len(w)
                c = np.fft.irfft(np.fft.rfft(tr, n) * np.conj(np.fft.rfft(w, n)), n)[:len(tr) - len(w) + 1]
                cs = np.concatenate(([0.0], np.cumsum(tr.astype(np.float64) ** 2)))
                norma = np.sqrt(np.maximum(cs[len(w):] - cs[:-len(w)], 0.0)) + 1e-9
                lag = int(np.argmax(c / norma))
            else:
                lag = mejor_lag_nuevo(tr, w)
            medido = ini + lag / sr - a / sr
            d = medido - t_tc
            fila.update({"medido_s": round(medido, 3), "desvio_s": round(d, 3), "desvio_cuadros": round(d * fps, 2),
                         "ok": abs(d) <= 1.0 / fps})
        out.append(fila)
        t_tc += seg_dur[cap]
    return out


def main():
    plans, sync_map, segs, g = plans_y_segs()
    intro = fb.INITIAL_SILENCE_SEC
    mixing = sync_map.get("mixing", {})
    music_map = fb._load_music_map(TID)
    ducked, _floor = fb._resolve_music_volumes(plans, mixing, music_map)
    pauses = fb._gfx_pauses(plans, LAB)
    intensidad = intensidad_sin_escribir(plans, pauses)
    prerolls = {p.chapter_id: segs[p.chapter_id]["pre_roll"] for p in plans}
    seg_dur = {p.chapter_id: segs[p.chapter_id]["seg_dur"] for p in plans}
    md = LAB / "_preview_music_ducked.wav"
    if not md.exists() or not all((LAB / f"_music_piece_{p.chapter_id}.wav").exists() for p in plans):
        md = fb._build_continuous_music_track(plans=plans, music_map=music_map, work_dir=LAB,
                                              crossfade_sec=fb.MUSIC_CROSSFADE_SEC, piece_volumes=ducked,
                                              output_filename="_preview_music_ducked.wav", extra_sec=pauses,
                                              intensidad=intensidad, pre_sec=prerolls, segmentos=seg_dur,
                                              intro_sec=intro, conservar_piezas=True)
    guion = {r["cap"]: r for r in g["mezcla"]["musica"]}
    tabla = {"guion": guion}
    tabla["hoy"] = {r["cap"]: r for r in medir(plans, md, LAB, seg_dur, intro, fb.MUSIC_CROSSFADE_SEC, pipeline.fps, False)}
    if True:
        tabla["cambio"] = {r["cap"]: r for r in medir(plans, md, LAB, seg_dur, intro, fb.MUSIC_CROSSFADE_SEC, pipeline.fps, True)}
    if "--real" in sys.argv:                          # D.2: la función real sobre copias de las piezas
        cop = LAB.parent / "work_copia_real"
        if cop.exists():
            shutil.rmtree(cop)
        cop.mkdir()
        for p in plans:
            shutil.copy2(LAB / f"_music_piece_{p.chapter_id}.wav", cop / f"_music_piece_{p.chapter_id}.wav")
        tabla["real"] = {r["cap"]: r for r in fb._medir_inicio_musica(plans, md, cop, seg_dur, intro,
                                                                       fb.MUSIC_CROSSFADE_SEC, pipeline.fps)}
    cols = [k for k in ("guion", "hoy", "cambio", "real") if k in tabla]
    print("| cap | title card s | " + " | ".join(f"desvío {k} s" for k in cols) + " |")
    print("|---|---|" + "---|" * len(cols))
    for p in plans:
        c = p.chapter_id
        celdas = []
        for k in cols:
            r = tabla[k][c]
            celdas.append("—" if r.get("desvio_s") is None else f"{r['desvio_s']:+.3f} {'✓' if r['ok'] else '✗'}")
        print(f"| {c} | {guion[c]['title_card_s']:.3f} | " + " | ".join(celdas) + " |")
    (Path(__file__).parent / ("tabla_real.json" if "--real" in sys.argv else "tabla_sim.json")).write_text(
        json.dumps(tabla, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
