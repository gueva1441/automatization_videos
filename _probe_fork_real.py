import scrapetube, itertools, threading, sys, traceback
from script_engine.youtube_scanner import _proxies_dict
px = _proxies_dict()
CID = "UCXuqSBlHAE6Xw-yeJA0Tunw"  # LinusTechTips

res = {"got": [], "err": None}
def w():
    try:
        for v in itertools.islice(scrapetube.get_channel(channel_id=CID, limit=15, proxies=px), 15):
            res["got"].append(v)
    except Exception:
        res["err"] = traceback.format_exc()
t = threading.Thread(target=w, daemon=True)
print(">>> get_channel con FORK #73 (timeout 40s)")
t.start(); t.join(40)
if t.is_alive():
    f = sys._current_frames().get(t.ident)
    print("    COLGADO en:", traceback.format_stack(f)[-1].strip() if f else "?")
elif res["err"]:
    print("    ERROR:", res["err"].splitlines()[-1])
else:
    print(f"    OK: {len(res['got'])} videos")
    if res["got"]:
        v = res["got"][0]
        print("    keys:", sorted(v.keys()))
        vt = v.get("viewCountText", {}).get("simpleText") or v.get("shortViewCountText", {}).get("simpleText")
        print("    views crudo:", repr(vt))
print(f"    (rescatados: {len(res['got'])})")
