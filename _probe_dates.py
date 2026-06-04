"""PROBE chat 44 — caza TODO campo de fecha/tiempo en el payload crudo del get_search."""
import scrapetube, itertools, json
from script_engine.youtube_scanner import _proxies_dict   # usar proxy para no comerse ban

QUERY = "submarine disasters history"   # una puerta real
N = 5

results = scrapetube.get_search(QUERY, limit=N, proxies=_proxies_dict())

def walk(o, path=""):
    if isinstance(o, dict):
        for k, val in o.items():
            kp = f"{path}.{k}" if path else k
            if any(t in k.lower() for t in ("date", "time", "publish")):
                print(f"    {kp} = {json.dumps(val, ensure_ascii=False)[:240]}")
            walk(val, kp)
    elif isinstance(o, list):
        for j, item in enumerate(o):
            walk(item, f"{path}[{j}]")

for i, v in enumerate(itertools.islice(results, N)):
    title = (v.get("title", {}).get("runs", [{}]) or [{}])[0].get("text", "?")
    print(f"\n=== RESULTADO {i}: {title[:55]} ===")
    print(f"    (claves top-level: {list(v.keys())})")
    walk(v)
