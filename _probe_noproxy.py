import scrapetube, itertools, threading, sys, traceback
CID = "UCXuqSBlHAE6Xw-yeJA0Tunw"

def run(nombre, fn, timeout=30):
    res={"got":[],"err":None}
    def w():
        try:
            for v in itertools.islice(fn(),10): res["got"].append(v)
        except Exception: res["err"]=traceback.format_exc()
    t=threading.Thread(target=w,daemon=True); print(f"\n>>> {nombre}"); t.start(); t.join(timeout)
    if t.is_alive():
        f=sys._current_frames().get(t.ident)
        print("    COLGADO en:", traceback.format_stack(f)[-1].strip() if f else "?")
    elif res["err"]: print("    ERROR:", res["err"].splitlines()[-1])
    else: print(f"    OK {len(res['got'])} videos")
    print(f"    (rescatados: {len(res['got'])})")

run("get_channel SIN proxy, sleep=0", lambda: scrapetube.get_channel(channel_id=CID, limit=10, sleep=0))
