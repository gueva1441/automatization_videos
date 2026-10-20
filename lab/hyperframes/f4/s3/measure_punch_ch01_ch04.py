import subprocess, numpy as np, sys
W="output/ba6c3cac-a091-41c0-8dad-afd2f4364747/_fase2b_work/"
def fr(p,t):
    raw=subprocess.run(["ffmpeg","-v","error","-ss",f"{t}","-i",p,"-frames:v","1","-vf","scale=1280:720","-f","rawvideo","-pix_fmt","gray","-"],capture_output=True).stdout
    return np.frombuffer(raw,np.uint8).reshape(720,1280).astype(np.float32)
def best(g,b):
    H,Wd=b.shape; ys,xs=np.mgrid[0:H,0:Wd]; out=[]
    for s in np.arange(1.0,1.031,0.005):
        sy=((ys-H/2)/s+H/2).astype(int).clip(0,H-1); sx=((xs-Wd/2)/s+Wd/2).astype(int).clip(0,Wd-1)
        c=slice(100,620),slice(150,1130)
        out.append((float(np.abs(g[c]-b[sy,sx][c]).mean()),round(s,3)))
    return min(out)
for cap,base,t_before,t_after in [("ch01","ch01_hybrid_visual.mp4",3.9,5.2),("ch04","ch04_flux_visual.mp4",8.4,9.6)]:
    g=W+cap+"_gfx.mp4"; b=W+base
    print(cap,"antes",best(fr(g,t_before),fr(b,t_before)),"después del golpe",best(fr(g,t_after),fr(b,t_after)))
