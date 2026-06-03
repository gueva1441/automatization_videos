import scrapetube, itertools
from script_engine.youtube_scanner import _proxies_dict

px = _proxies_dict()
CID = "UCXuqSBlHAE6Xw-yeJA0Tunw"  # LinusTechTips (canal grande conocido)

print(">>> get_channel, capturando el KeyError y quedandonos con lo acumulado:")
got = []
try:
    gen = scrapetube.get_channel(channel_id=CID, limit=30, proxies=px)
    for v in gen:
        got.append(v)
        if len(got) >= 30:
            break
except KeyError as e:
    print("    KeyError al paginar:", repr(e), "-> nos quedamos con lo que ya vino")
except Exception as e:
    print("    Otro error:", repr(e))

print("    videos rescatados:", len(got))
if got:
    print("    keys:", sorted(got[0].keys()))
    for v in got[:5]:
        vt = v.get("viewCountText", {}).get("simpleText") or v.get("shortViewCountText", {}).get("simpleText")
        print("      views crudo:", repr(vt))
