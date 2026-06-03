import scrapetube, itertools, re
from script_engine.youtube_scanner import _proxies_dict
got = list(itertools.islice(scrapetube.get_search("Linus Tech Tips", limit=3, results_type="channel", proxies=_proxies_dict()), 3))
for c in got:
    cid = c.get("channelId")
    subs = c.get("subscriberCountText", {})
    vids = c.get("videoCountText", {})
    print("channelId:", cid)
    print("  subs crudo:", subs)
    print("  videoCount crudo:", vids)
    print("---")
