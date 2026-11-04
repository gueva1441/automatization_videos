import sys, json
from pathlib import Path
sys.path.insert(0, r"C:\CLAUDE_PROJECTS\automatization_videos")
sys.path.insert(0, r"C:\CLAUDE_PROJECTS\automatization_videos\lab\hyperframes\f73\d")
import numpy as np
import simular_d as sd, fase2b as fb
from script_engine.gfx_guion import _pcm
t = json.loads((sd.Path(sd.__file__).parent/"tabla_sim.json").read_text(encoding="utf-8"))
LAB = sd.LAB; sr = 11025; md = LAB/"_preview_music_ducked.wav"
for cap in ("ch03","ch07"):
    tc = t["guion"][cap]["title_card_s"]
    pz = _pcm(LAB/f"_music_piece_{cap}.wav", 0.0, min(fb._get_duration(LAB/f"_music_piece_{cap}.wav"), fb.MUSIC_CROSSFADE_SEC+20), sr)
    n_w = int(4*sr); entra = fb.MUSIC_CROSSFADE_SEC
    a = max(range(int(entra*sr), len(pz)-n_w, sr//2), key=lambda k: float(np.sqrt(np.mean(pz[k:k+n_w]**2))))
    w = pz[a:a+n_w].astype(np.float64); ini = max(0.0, tc + a/sr - 20)
    tr = _pcm(md, ini, 44, sr).astype(np.float64)
    m=len(w); n=len(tr)+m
    c = np.fft.irfft(np.fft.rfft(tr,n)*np.conj(np.fft.rfft(w,n)),n)[:len(tr)-m+1]
    cs=np.concatenate(([0.0],np.cumsum(tr**2))); e=cs[m:]-cs[:-m]
    nz=np.concatenate(([0],np.cumsum(tr!=0,dtype=np.int64))); cnt=nz[m:]-nz[:-m]
    score=np.where(cnt>0, c/np.sqrt(np.where(e>0,e,1)), -np.inf)
    esperado = int(round((tc - ini)*sr + a))
    for nombre,lag in (("elegido",int(np.argmax(score))),("esperado",esperado)):
        print(cap,nombre,"t",round(ini+lag/sr-a/sr-tc,3),"score",score[lag],"corr_norm",c[lag]/np.sqrt(e[lag])/np.linalg.norm(w),"energia",e[lag],"nz",cnt[lag],"rms_ventana",np.sqrt(e[lag]/m))
    # silencio digital en la pista de búsqueda
    z = (tr==0); print(cap,"muestras en 0 en la búsqueda:",int(z.sum()),"de",len(tr), "min |x| no cero", np.min(np.abs(tr[tr!=0])))
    lag2 = sd.mejor_lag_nuevo(tr.astype(np.float32), w.astype(np.float32))
    print(cap, "sim fn lag", round(ini+lag2/sr-a/sr-tc,3), "score", score[lag2], "e", e[lag2], "cnt", cnt[lag2])
    vv = np.flatnonzero(cnt>0); ee = cs[m:][vv]-cs[:-m][vv]; s2 = c[vv]/np.sqrt(ee); k=int(np.argmax(s2))
    print(cap, "ee min", ee.min(), "s2 max", s2[k], "at", round(ini+vv[k]/sr-a/sr-tc,3), "nans", int(np.isnan(s2).sum()))
