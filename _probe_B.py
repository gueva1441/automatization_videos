import scrapetube, itertools
from script_engine.youtube_scanner import _proxies_dict
got = list(itertools.islice(scrapetube.get_search("Linus Tech Tips", limit=5, results_type="channel", proxies=_proxies_dict()), 5))
print("channels:", len(got))
if got: print("keys:", sorted(got[0].keys()))
