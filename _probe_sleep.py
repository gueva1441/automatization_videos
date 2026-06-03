import scrapetube, itertools, threading, sys, traceback
from script_engine.youtube_scanner import _proxies_dict
px = _proxies_dict()
CID = "UCXuqSBlHAE6Xw-yeJA0Tunw"

def run(nombre, fn, timeout=30):
    res={"got":[],"err":None}
    def w():
        try:
            for v in itertools.islice(fn(),30): res["got"].append(v)
        except Exception: res["err"]=traceback.format_exc()
    t=threading.Thread(target=w,daemon=True); print(f"\n>>> {nombre}"); t.start(); t.join(timeout)
    if t.is_alive():
        f=sys._current_frames().get(t.ident)
        print(f"    COLGADO {timeout}s en:", traceback.format_stack(f)[-1].strip() if f else "?")
    elif res["err"]: print("    ERROR:", res["err"].splitlines()[-1])
    else:
        print(f"    OK {len(res['got'])} videos")
        if res["got"]:
            v=res["got"][0]
            print("    keys:", sorted(v.keys())[:8])
            print("    views:", v.get("viewCountText",{}).get("simpleText") or v.get("shortViewCountText",{}).get("simpleText"))
    print(f"    (rescatados: {len(res['got'])})")

run("get_channel sleep=0 limit=10", lambda: scrapetube.get_channel(channel_id=CID, limit=10, sleep=0, proxies=px))
run("get_channel sleep=0.2 limit=5", lambda: scrapetube.get_channel(channel_id=CID, limit=5, sleep=0.2, proxies=px))
