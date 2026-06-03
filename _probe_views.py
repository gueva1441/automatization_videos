import scrapetube, itertools, json
from script_engine.youtube_scanner import _proxies_dict
px = _proxies_dict()
CID = "UCXuqSBlHAE6Xw-yeJA0Tunw"

v = next(itertools.islice(scrapetube.get_channel(channel_id=CID, limit=3, proxies=px), 1))
print("=== VOLCADO COMPLETO DEL PRIMER VIDEO ===")
print(json.dumps(v, indent=2, ensure_ascii=False)[:3000])
print("\n=== buscando 'view' en el objeto ===")
dump = json.dumps(v, ensure_ascii=False)
import re
for m in re.finditer(r'.{30}views?.{60}', dump, re.IGNORECASE):
    print("  ...", m.group(0), "...")
