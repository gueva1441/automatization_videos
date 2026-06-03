import scrapetube, itertools
from script_engine.youtube_scanner import _proxies_dict, _parse_views_scrapetube

px = _proxies_dict()

vids = list(itertools.islice(scrapetube.get_search("declassified ocean phenomena", limit=5, proxies=px), 5))
cid = vids[0]["longBylineText"]["runs"][0]["navigationEndpoint"]["browseEndpoint"]["browseId"]
print("channel_id:", cid)

uploads = "UU" + cid[2:]
print("uploads playlist:", uploads)
pl = list(itertools.islice(scrapetube.get_playlist(uploads, limit=10, proxies=px), 10))
print("get_playlist devolvio:", len(pl), "videos")
for v in pl[:5]:
    vt = v.get("viewCountText", {}).get("simpleText") or v.get("shortViewCountText", {}).get("simpleText")
    print("  ", vt, "->", _parse_views_scrapetube(v))
