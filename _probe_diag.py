import scrapetube, itertools, threading, sys, traceback

from script_engine.youtube_scanner import _proxies_dict
px = _proxies_dict()
CID = "UCXuqSBlHAE6Xw-yeJA0Tunw"   # LinusTechTips
UPL = "UU" + CID[2:]

def run_con_timeout(nombre, fn, timeout=30):
    res = {"got": [], "err": None, "done": False}
    def worker():
        try:
            for v in itertools.islice(fn(), 30):
                res["got"].append(v)
            res["done"] = True
        except Exception:
            res["err"] = traceback.format_exc()
    t = threading.Thread(target=worker, daemon=True)
    print(f"\n>>> {nombre} (timeout {timeout}s)...")
    t.start()
    t.join(timeout)
    if t.is_alive():
        # sigue colgado: volcamos el stack del thread para ver DONDE
        frame = sys._current_frames().get(t.ident)
        print(f"    COLGADO tras {timeout}s. Stack del thread (donde esta trabado):")
        if frame:
            for line in traceback.format_stack(frame):
                print("      " + line.strip())
        print(f"    (rescatados antes de colgar: {len(res['got'])})")
    elif res["err"]:
        print(f"    REVENTO. Traceback:")
        print("      " + res["err"].replace("\n", "\n      "))
        print(f"    (rescatados antes de reventar: {len(res['got'])})")
    else:
        print(f"    OK: {len(res['got'])} videos.")
        if res["got"]:
            print("    keys:", sorted(res["got"][0].keys()))

run_con_timeout("get_channel(channel_id)", lambda: scrapetube.get_channel(channel_id=CID, limit=30, proxies=px))
run_con_timeout("get_playlist(uploads UU)", lambda: scrapetube.get_playlist(UPL, limit=30, proxies=px))

print("\n>>> FIN. El proceso puede tardar en cerrar si quedan threads daemon colgados; Ctrl+C si hace falta.")
