import scrapetube, itertools, json
from script_engine.youtube_scanner import _proxies_dict
px = _proxies_dict()
CID = "UCXuqSBlHAE6Xw-yeJA0Tunw"

for v in itertools.islice(scrapetube.get_channel(channel_id=CID, limit=5, proxies=px), 5):
    title = v.get("title", {})
    title_txt = title.get("content") if isinstance(title, dict) else title
    rows = (v.get("metadata", {})
             .get("lockupMetadataViewModel", {})
             .get("metadata", {})
             .get("contentMetadataViewModel", {})
             .get("metadataRows", []))
    partes = []
    for row in rows:
        for part in row.get("metadataParts", []):
            txt = part.get("text", {}).get("content")
            if txt:
                partes.append(txt)
    print(f"- {str(title_txt)[:40]:42} -> partes: {partes}")
