import scrapetube, itertools
from script_engine.youtube_scanner import _proxies_dict

px = _proxies_dict()
CID = "UCXuqSBlHAE6Xw-yeJA0Tunw"  # LinusTechTips

print(">>> get_channel con el FORK #73:")
got = []
try:
    gen = scrapetube.get_channel(channel_id=CID, limit=30, proxies=px)
    for v in itertools.islice(gen, 30):
        got.append(v)
except Exception as e:
    print("    error:", repr(e))

print("    videos:", len(got))
if got:
    print("    keys:", sorted(got[0].keys()))
    for v in got[:5]:
        vt = (v.get("viewCountText", {}).get("simpleText")
              or v.get("shortViewCountText", {}).get("simpleText"))
        print("      views crudo:", repr(vt))
