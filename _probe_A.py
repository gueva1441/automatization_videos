import scrapetube, itertools
from script_engine.youtube_scanner import _proxies_dict, _parse_views_scrapetube
PID = "PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf"
got = list(itertools.islice(scrapetube.get_playlist(PID, limit=30, proxies=_proxies_dict()), 30))
print("videos:", len(got))
if got:
    print("keys:", sorted(got[0].keys()))
    v = got[0]
    vt = v.get("viewCountText", {}).get("simpleText") or v.get("shortViewCountText", {}).get("simpleText")
    print("views crudo:", repr(vt), "->", _parse_views_scrapetube(v))
