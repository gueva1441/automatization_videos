"""F75 C1 — lab del master -14 LUFS / -1,5 dBTP sobre el audio de Wittenoom (US$ 0, sin API, sin render).

Solo LEE output/123bbb64-.../<tid>_final_gfx.mp4 (publicado). Escribe solo en lab/hyperframes/f75/c/.
Constantes (HANDOFF_F75 §1): -14 LUFS (DECISIONES l.237, Omar) · -1,5 dBTP (audio_manager.py:463) ·
-2 dBFS de muestra para el alimiter (analista, técnico) · LRA = el medido en la 1.a pasada · 60 s de extracto (solo lab).
AAC del master: -c:a aac -b:a 192k (lo mismo que fase2b usa para el audio final: fase2b.py:2171/2040/2082,
transition_applier.py:431). -ar 48000 en la 2.a pasada (HANDOFF_F75 C1).

Uso: PYTHONIOENCODING=utf-8 python lab/hyperframes/f75/c/f75c1_master_lab.py
"""
from __future__ import annotations

import json
import math
import re
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[4]
TID = "123bbb64-9fca-4395-8bf4-57d60e219ef1"
SRC = BASE / "output" / TID / f"{TID}_final_gfx.mp4"
OUT = Path(__file__).resolve().parent
LOG = OUT / "f75c1.log"

TARGET_I = -14.0          # DECISIONES 2026-11-04 (línea 237), Omar
TARGET_TP = -1.5          # audio_manager.py:463 (loudnorm … TP=-1.5), proyecto
LIMIT_DBFS = -2.0         # HANDOFF_F75 §1: margen AAC entre muestras, analista (técnico)
EXTRACT_S = 60            # HANDOFF_F75 §1: largo de extracto, solo lab
AAC = ["-c:a", "aac", "-b:a", "192k"]   # fase2b.py:2171 (camino a), 2040/2082 (camino b), transition_applier.py:431 (c)
AR = "48000"              # HANDOFF_F75 C1

_log = LOG.open("w", encoding="utf-8")


def log(s: str = "") -> None:
    print(s)
    _log.write(s + "\n")
    _log.flush()


def run(cmd: list[str], keep_stderr: bool = True) -> str:
    log("$ " + " ".join(f'"{c}"' if (" " in c or ";" in c or "|" in c) else c for c in cmd))
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        log(r.stderr[-3000:])
        raise SystemExit(f"ffmpeg rc={r.returncode}")
    return r.stderr if keep_stderr else ""


def ebur128(path: Path, verbose: bool = False) -> dict:
    af = "ebur128=peak=true" + (":framelog=verbose" if verbose else "")
    err = run(["ffmpeg", "-hide_banner", "-nostats", *(["-v", "verbose"] if verbose else []), "-i", str(path), "-vn",
               "-af", af, "-f", "null", "-"])
    summ = err[err.rfind("Summary:"):]
    i = float(re.search(r"I:\s+(-?[\d.]+) LUFS", summ).group(1))
    lra = float(re.search(r"LRA:\s+(-?[\d.]+) LU", summ).group(1))
    tp = float(re.search(r"True peak:\s+Peak:\s+(-?[\d.]+|-inf) dBFS", summ).group(1))
    res = {"I": i, "LRA": lra, "TP": tp, "summary": summ.strip()}
    if verbose:
        frames = [(float(m.group(1)), float(m.group(2)))
                  for m in re.finditer(r"t:\s*([\d.]+)\s+TARGET:.*?M:\s*(-?[\d.]+|-inf)", err)
                  if m.group(2) != "-inf"]
        res["frames"] = frames
    return res


def loudest_window(frames: list[tuple[float, float]], win: float) -> tuple[float, float]:
    """Ventana de `win` s con más energía media de la sonoridad momentánea (M, bloques de 400 ms cada 100 ms,
    ebur128 framelog). Sonoridad de ventana = 10·log10(media(10^(M/10))) sin compuerta; paso 1 s; inicio en s enteros."""
    t = [f[0] for f in frames]
    e = [10 ** (f[1] / 10) for f in frames]
    pref = [0.0]
    for x in e:
        pref.append(pref[-1] + x)
    best = (-1e9, 0.0)
    import bisect
    s = 0.0
    while s + win <= t[-1] + 1e-6:
        a = bisect.bisect_left(t, s + 0.4)          # el bloque que termina en t cubre [t-0.4, t]
        b = bisect.bisect_right(t, s + win)
        if b > a:
            L = 10 * math.log10((pref[b] - pref[a]) / (b - a))
            if L > best[0]:
                best = (L, s)
        s += 1.0
    return best[1], best[0]


def loudnorm_json(err: str) -> dict:
    j = err[err.rfind("{"):err.rfind("}") + 1]
    return json.loads(j)


def main() -> int:
    log(f"# F75 C1 — {SRC.name}")
    v = subprocess.run(["ffmpeg", "-hide_banner", "-version"], capture_output=True, text=True).stdout.splitlines()[0]
    log(v)

    # 0. semántica del alimiter en esta versión (sin API): limit lineal 0.0625..1; level=disabled → sin auto-nivel
    log("\n## 0. alimiter: semántica de limit / level / latency")
    lim = 10 ** (LIMIT_DBFS / 20)
    lim_s = f"{lim:.6f}"
    log(f"limit = 10^({LIMIT_DBFS}/20) = {lim!r} → '{lim_s}' (amplitud lineal de muestra)")
    for lvl in ("disabled", "enabled"):
        err = run(["ffmpeg", "-hide_banner", "-nostats", "-f", "lavfi", "-i", "sine=f=440:d=2:sample_rate=44100",
                   "-af", f"volume=-6dB,alimiter=level={lvl}:limit={lim_s},astats=metadata=0:measure_overall=Peak_level",
                   "-f", "null", "-"])
        pk = re.findall(r"Peak level dB:\s*(-?[\d.]+)", err)
        log(f"  seno pico −24 dBFS (sine 1/8 = −18, −6 dB) por alimiter level={lvl}: pico de salida {pk[-1] if pk else '?'} dBFS")
    err = run(["ffmpeg", "-hide_banner", "-nostats", "-f", "lavfi", "-i", "sine=f=440:d=2:sample_rate=44100",
               "-af", f"volume=+20dB,alimiter=level=disabled:limit={lim_s},astats=metadata=0:measure_overall=Peak_level",
               "-f", "null", "-"])
    pk = re.findall(r"Peak level dB:\s*(-?[\d.]+)", err)
    log(f"  seno pico +2 dBFS (−18 +20) → alimiter limit={lim_s}: pico de salida {pk[-1] if pk else '?'} dBFS")
    # latencia: un impulso en la muestra 22050; ¿dónde sale?
    for lat in ("0", "1"):
        imp = OUT / f"_imp_lat{lat}.raw"
        run(["ffmpeg", "-hide_banner", "-nostats", "-y", "-f", "lavfi",
             "-i", "aevalsrc='if(eq(n,22050),0.5,0)':s=44100:d=1",
             "-af", f"alimiter=level=disabled:limit={lim_s}:latency={lat}", "-f", "f32le", "-ac", "1", str(imp)])
        import array
        a = array.array("f")
        a.frombytes(imp.read_bytes())
        n = max(range(len(a)), key=lambda k: abs(a[k]))
        log(f"  impulso en muestra 22050, latency={lat}: sale en muestra {n} (corrimiento {n - 22050} = "
            f"{(n - 22050) / 44.1:.2f} ms), {len(a)} muestras")
        imp.unlink()

    # 1. extraer
    log("\n## 1. extraer audio")
    orig_wav = OUT / "_orig_full.wav"
    run(["ffmpeg", "-hide_banner", "-nostats", "-y", "-i", str(SRC), "-vn", "-map", "0:a:0", "-c:a", "pcm_f32le",
         str(orig_wav)])

    # 2. medir original
    log("\n## 2. ebur128 original")
    m0 = ebur128(orig_wav, verbose=True)
    log(m0["summary"])
    log(f"ORIGINAL: I={m0['I']} LRA={m0['LRA']} TP={m0['TP']}  ({len(m0['frames'])} cuadros M)")
    s_hot, l_hot = loudest_window(m0["frames"], EXTRACT_S)
    log(f"minuto más fuerte (original): {s_hot:.0f}–{s_hot + EXTRACT_S:.0f} s, {l_hot:.2f} LUFS sin compuerta")
    l_hook = 10 * math.log10(sum(10 ** (m / 10) for t, m in m0["frames"] if 0.4 <= t <= EXTRACT_S) /
                             max(1, sum(1 for t, m in m0["frames"] if 0.4 <= t <= EXTRACT_S)))
    log(f"gancho 0–60 s (original): {l_hook:.2f} LUFS sin compuerta")

    # 3. ganancia
    G = TARGET_I - m0["I"]
    G_s = f"{G:+.1f}dB"
    log(f"\n## 3. G = {TARGET_I} - ({m0['I']}) = {G:+.2f} dB → volume={G_s}")

    pre = f"volume={G_s},alimiter=level=disabled:limit={lim_s}"

    # 4a. 1.a pasada: medir la señal limitada
    f1 = f"{pre},loudnorm=print_format=json"
    log(f"\n## 4a. 1.a pasada: -af \"{f1}\"")
    p1 = loudnorm_json(run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(orig_wav), "-af", f1, "-f", "null", "-"]))
    log(json.dumps(p1, indent=1))
    (OUT / "loudnorm_pass1.json").write_text(json.dumps(p1, indent=1), encoding="utf-8")

    # 4b. 2.a pasada → AAC directo (como lo haría el master en fase2b)
    f2 = (f"{pre},loudnorm=I={TARGET_I:g}:TP={TARGET_TP:g}:LRA={p1['input_lra']}:linear=true:"
          f"measured_I={p1['input_i']}:measured_TP={p1['input_tp']}:measured_LRA={p1['input_lra']}:"
          f"measured_thresh={p1['input_thresh']}:offset={p1['target_offset']}:print_format=json")
    master = OUT / "master_full.m4a"
    log(f"\n## 4b. 2.a pasada: -af \"{f2}\" -ar {AR} {' '.join(AAC)}")
    p2 = loudnorm_json(run(["ffmpeg", "-hide_banner", "-nostats", "-y", "-i", str(orig_wav), "-af", f2,
                            "-ar", AR, *AAC, str(master)]))
    log(json.dumps(p2, indent=1))
    (OUT / "loudnorm_pass2.json").write_text(json.dumps(p2, indent=1), encoding="utf-8")
    log(f"normalization_type = {p2.get('normalization_type')}")

    # 5. medir el master codificado (AAC)
    log("\n## 5. ebur128 master (sobre el m4a AAC)")
    m1 = ebur128(master, verbose=True)
    log(m1["summary"])
    log(f"MASTER AAC: I={m1['I']} LRA={m1['LRA']} TP={m1['TP']}")
    s_hot1, l_hot1 = loudest_window(m1["frames"], EXTRACT_S)
    log(f"minuto más fuerte (master): {s_hot1:.0f}–{s_hot1 + EXTRACT_S:.0f} s, {l_hot1:.2f} LUFS sin compuerta")
    probe = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                            "stream=codec_name,sample_rate,channels,bit_rate:format=duration,size", "-of", "json",
                            str(master)], capture_output=True, text=True).stdout
    log(probe)
    ok_tp = m1["TP"] <= TARGET_TP
    log(f"chequeo: TP {m1['TP']} <= {TARGET_TP}: {ok_tp} · I {m1['I']} vs {TARGET_I}: Δ {m1['I'] - TARGET_I:+.1f}")

    # 6. extractos (wav s16, escuchables)
    log("\n## 6. extractos de 60 s")
    cuts = {"gancho_0000-0100": 0.0, (f"fuerte_{int(s_hot) // 60:02d}{int(s_hot) % 60:02d}-"
                                         f"{int(s_hot + EXTRACT_S) // 60:02d}{int(s_hot + EXTRACT_S) % 60:02d}"): s_hot}
    out_files = []
    for name, ss in cuts.items():
        for tag, src in (("original", orig_wav), ("master", master)):
            dst = OUT / f"extracto_{name}_{tag}.wav"
            run(["ffmpeg", "-hide_banner", "-nostats", "-y", "-ss", f"{ss:.3f}", "-t", str(EXTRACT_S), "-i", str(src),
                 "-c:a", "pcm_s16le", str(dst)])
            e = ebur128(dst)
            log(f"  {dst.name}: I={e['I']} LRA={e['LRA']} TP={e['TP']}")
            out_files.append(str(dst))

    res = {"src": str(SRC), "limit_lineal": lim_s, "G_dB": G_s, "filtro_pass1": f1, "filtro_pass2": f2,
           "ar": AR, "aac": AAC, "original": {k: m0[k] for k in ("I", "LRA", "TP")},
           "master_aac": {k: m1[k] for k in ("I", "LRA", "TP")}, "normalization_type": p2.get("normalization_type"),
           "minuto_fuerte_s": s_hot, "minuto_fuerte_lufs_sin_compuerta": round(l_hot, 2),
           "gancho_lufs_sin_compuerta": round(l_hook, 2), "extractos": out_files}
    (OUT / "f75c1_result.json").write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
    log("\n" + json.dumps(res, indent=1, ensure_ascii=False))

    # 7. diagnóstico del pico real: ¿dónde se pierde el margen? (sample peak vs true peak por etapa)
    log("\n## 7. diagnóstico: pico de muestra y pico real por etapa")
    pre_aac = OUT / "_diag_master_preaac.wav"
    run(["ffmpeg", "-hide_banner", "-nostats", "-y", "-i", str(orig_wav), "-af", f2, "-ar", AR, "-c:a", "pcm_f32le",
         str(pre_aac)])
    diag = {}
    for tag, src, af in (("volume", orig_wav, f"volume={G_s}"), ("volume+alimiter", orig_wav, pre),
                         ("volume+alimiter(latency=1)", orig_wav, pre + ":latency=1"),
                         ("master pre-AAC (wav 48k)", pre_aac, None), ("master AAC (m4a)", master, None)):
        chain = (af + "," if af else "") + "ebur128=peak=true+sample"
        err = run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(src), "-vn", "-af", chain, "-f", "null", "-"])
        summ = err[err.rfind("Summary:"):]
        i = re.search(r"I:\s+(-?[\d.]+) LUFS", summ).group(1)
        sp = re.search(r"Sample peak:\s+Peak:\s+(-?[\d.]+) dBFS", summ).group(1)
        tp = re.search(r"True peak:\s+Peak:\s+(-?[\d.]+) dBFS", summ).group(1)
        diag[tag] = {"I": float(i), "sample_peak": float(sp), "true_peak": float(tp)}
        log(f"  {tag:<30} I={i:>6} LUFS  sample peak={sp:>5} dBFS  true peak={tp:>5} dBTP")
    pre_aac.unlink()
    res["diagnostico_picos"] = diag
    (OUT / "f75c1_result.json").write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")

    orig_wav.unlink()
    log(f"\nborrado {orig_wav.name}; master_full.m4a = {master.stat().st_size / 1e6:.1f} MB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
