"""F77 Contrato A — dónde rankea 4VgrwqGvIuc en search.list (relevanceLanguage=es, type=video) para
varias queries, hasta 4 páginas de 50. Solo diagnóstico (no cambia nada). Cuota: 100 u por página.
La llave no se imprime.  Correr:  PYTHONIOENCODING=utf-8 python lab/hyperframes/f77/a/diag_palomares_rank.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

import requests  # noqa: E402

import script_engine.youtube_scanner as ys  # noqa: E402

ESPERADO = "4VgrwqGvIuc"
H = {"X-Goog-Api-Key": ys.api.youtube_api_key}
total = 0
for q, paginas in (("Palomares 1966", 4), ("Palomares", 1), ("bombas nucleares Palomares", 1)):
    ids, tok = [], None
    for _ in range(paginas):
        p = {"part": "id", "q": q, "type": "video", "relevanceLanguage": "es", "maxResults": 50}
        if tok:
            p["pageToken"] = tok
        r = requests.get(f"{ys.api.youtube_base_url}/search", params=p, headers=H, timeout=15)
        total += 100
        r.raise_for_status()
        d = r.json()
        ids += [it["id"]["videoId"] for it in d.get("items", []) if it.get("id", {}).get("videoId")]
        tok = d.get("nextPageToken")
        if ESPERADO in ids or not tok:
            break
    pos = ids.index(ESPERADO) + 1 if ESPERADO in ids else None
    print(f"q='{q}': {len(ids)} ids revisados · posición de {ESPERADO}: {pos or 'no aparece'}")
print(f"cuota de este diagnóstico: {total} u")
