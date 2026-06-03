import scrapetube, itertools
from script_engine.youtube_scanner import _proxies_dict

px = _proxies_dict()

# Canal conocido y enorme: LinusTechTips UCXuqSBlHAE6Xw-yeJA0Tunw -> uploads UUXuqSBlHAE6Xw-yeJA0Tunw
tests = {
    "LinusTechTips_uploads": "UUXuqSBlHAE6Xw-yeJA0Tunw",
}
for name, pid in tests.items():
    try:
        gen = scrapetube.get_playlist(pid, limit=5, proxies=px)
        got = list(itertools.islice(gen, 5))
        print(name, "->", len(got), "videos")
        if got:
            print("   keys:", sorted(got[0].keys()))
    except Exception as e:
        print(name, "-> ERROR:", repr(e))
