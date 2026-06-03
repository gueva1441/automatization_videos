import scrapetube, itertools
from script_engine.youtube_scanner import _proxies_dict

# Playlist pública conocida (no uploads). Si ESTA tira el mismo KeyError, es la VERSION, no el canal.
PID = "PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf"  # Google Developers, playlist publica grande

print(">>> SIN proxy:")
try:
    got = list(itertools.islice(scrapetube.get_playlist(PID, limit=5), 5))
    print("   ", len(got), "videos")
except Exception as e:
    print("    ERROR:", repr(e))

print(">>> CON proxy:")
try:
    got = list(itertools.islice(scrapetube.get_playlist(PID, limit=5, proxies=_proxies_dict()), 5))
    print("   ", len(got), "videos")
except Exception as e:
    print("    ERROR:", repr(e))
