"""F77 Contrato A — diagnóstico: ¿por qué no aparece 4VgrwqGvIuc (A toda leche)?
Repite la búsqueda cruda de la API (sin filtros) y mira, para el esperado: si vino en los 50 ids, su
duración, views, fecha y lo que dice detect_language. Lista también los descartados por idioma.
Cuota: 1 search (100) + 2 videos.list (2) = 102 u. Sin Gemini. La llave no se imprime.

Correr (desde la raíz):  PYTHONIOENCODING=utf-8 python lab/hyperframes/f77/a/diag_palomares_faltante.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

import requests  # noqa: E402

import script_engine.youtube_scanner as ys  # noqa: E402

ESPERADO = "4VgrwqGvIuc"
H = {"X-Goog-Api-Key": ys.api.youtube_api_key}
B = ys.api.youtube_base_url


def videos(ids):
    r = requests.get(f"{B}/videos", params={"part": "contentDetails,statistics,snippet", "id": ",".join(ids)},
                     headers=H, timeout=15)
    r.raise_for_status()
    return r.json().get("items", [])


r = requests.get(f"{B}/search", params={"part": "id", "q": "Palomares 1966", "type": "video",
                                        "relevanceLanguage": "es", "maxResults": 50}, headers=H, timeout=15)
r.raise_for_status()
ids = [it["id"]["videoId"] for it in r.json().get("items", []) if it.get("id", {}).get("videoId")]
print(f"search 'Palomares 1966': {len(ids)} ids · ¿{ESPERADO} está? {ESPERADO in ids}"
      + (f" (posición {ids.index(ESPERADO) + 1})" if ESPERADO in ids else ""))

print("\nDescartados por idioma (largos > 180 s, detect_language != es):")
for v in videos(ids):
    t = v["snippet"]["title"]
    d = ys._iso8601_duration_s(v["contentDetails"].get("duration"))
    lang = ys.detect_language(t)
    if (d is None or d > ys.SHORTS_MAX_S) and lang != "es":
        print(f"  {v['id']} · {lang} · {d}s · {int(v['statistics'].get('viewCount', 0)):,} v · {t[:80]}")

print(f"\nEl esperado por id:")
for v in videos([ESPERADO]):
    t = v["snippet"]["title"]
    print(f"  título: {t}")
    print(f"  duración: {v['contentDetails'].get('duration')} → {ys._iso8601_duration_s(v['contentDetails'].get('duration'))} s")
    print(f"  views: {int(v['statistics'].get('viewCount', 0)):,} · publicado: {v['snippet'].get('publishedAt')} "
          f"→ {ys._months_since(v['snippet'].get('publishedAt'))} meses")
    print(f"  detect_language(título) = {ys.detect_language(t)} · defaultAudioLanguage = "
          f"{v['snippet'].get('defaultAudioLanguage')} · canal = {v['snippet'].get('channelTitle')}")
