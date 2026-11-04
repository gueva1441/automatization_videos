import sys, json
sys.path.insert(0, r"C:\CLAUDE_PROJECTS\automatization_videos")
sys.path.insert(0, r"C:\CLAUDE_PROJECTS\automatization_videos\lab\hyperframes\f73\d")
import numpy as np, simular_d as sd, fase2b as fb
from config import pipeline
def variante(tr, w):
    tr, w = np.asarray(tr, np.float64), np.asarray(w, np.float64)
    m, n = len(w), len(tr)+len(w)
    c = np.fft.irfft(np.fft.rfft(tr, n)*np.conj(np.fft.rfft(w, n)), n)[:len(tr)-m+1]
    cs = np.concatenate(([0.0], np.cumsum(tr**2)))
    nz = np.concatenate(([0], np.cumsum(tr != 0, dtype=np.int64)))
    v = np.flatnonzero(nz[m:]-nz[:-m] == m)
    e = cs[m:][v]-cs[:-m][v]
    print("   e min en candidatas", e.min())
    return int(v[np.argmax(c[v]/np.sqrt(e))])
sd.mejor_lag_nuevo = variante
plans, sync_map, segs, g = sd.plans_y_segs()
seg_dur = {p.chapter_id: segs[p.chapter_id]["seg_dur"] for p in plans}
for r in sd.medir(plans, sd.LAB/"_preview_music_ducked.wav", sd.LAB, seg_dur, fb.INITIAL_SILENCE_SEC, fb.MUSIC_CROSSFADE_SEC, pipeline.fps, True):
    print(r["cap"], r.get("desvio_s"), r.get("ok"))
