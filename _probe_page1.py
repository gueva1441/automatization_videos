import json, itertools, threading, sys, traceback
import scrapetube
from scrapetube import scrapetube as st   # modulo interno
from script_engine.youtube_scanner import _proxies_dict

px = _proxies_dict()
CID = "UCXuqSBlHAE6Xw-yeJA0Tunw"
UPL = "UU" + CID[2:]

def run(timeout=40):
    res = {"vids": [], "err": None, "view_fields": None}
    def w():
        try:
            # Reproducir el arranque de get_playlist: pedir la pagina 1 cruda
            url = "https://www.youtube.com/playlist?list=" + UPL
            # st.get_videos es el generador interno; lo recorremos pero
            # capturamos el KeyError de la pagina 2 para quedarnos con la 1.
            gen = scrapetube.get_playlist(UPL, proxies=px, sleep=0)
            for v in gen:
                res["vids"].append(v)
        except KeyError as e:
            res["err"] = f"KeyError {e} (pagina 2) -> nos quedamos con pagina 1"
        except Exception:
            res["err"] = traceback.format_exc().splitlines()[-1]
    t = threading.Thread(target=w, daemon=True)
    print(">>> get_playlist pagina 1 (capturando KeyError de la pag 2)")
    t.start(); t.join(timeout)
    if t.is_alive():
        f = sys._current_frames().get(t.ident)
        print("    COLGADO en:", traceback.format_stack(f)[-1].strip() if f else "?")
    print("    nota:", res["err"])
    print("    videos rescatados de pagina 1:", len(res["vids"]))
    if res["vids"]:
        v = res["vids"][0]
        print("    keys:", sorted(v.keys()))
        # buscar CUALQUIER campo que huela a views
        dump = json.dumps(v)
        for kw in ["viewCount", "shortViewCount", "videoInfo"]:
            if kw in dump:
                print(f"    contiene '{kw}'")
        print("    videoInfo:", v.get("videoInfo"))

run()
