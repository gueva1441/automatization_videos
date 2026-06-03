# _probe_autocomplete.py — qué autocompleta YouTube/Google = lo que la gente MÁS busca
# Sin API key, sin librería rara. Correr:  python -X utf8 _probe_autocomplete.py
import requests, json

def sugerencias(seed, lang="es", region="MX", youtube=True):
    # ds=yt → autocomplete de YOUTUBE; sin ds → autocomplete de Google web
    url = "https://suggestqueries.google.com/complete/search"
    params = {"client": "firefox", "q": seed, "hl": lang, "gl": region}
    if youtube:
        params["ds"] = "yt"
    r = requests.get(url, params=params, timeout=10)
    data = json.loads(r.text)
    return data[1]   # data[1] = lista de sugerencias

SEEDS = [
    "misterio del oceano",
    "experimentos secretos",
    "lugares abandonados",
    "casos sin resolver",
    "historia oscura",
]

for seed in SEEDS:
    print(f"\n=== '{seed}' (YouTube) ===")
    try:
        for s in sugerencias(seed, youtube=True):
            print(f"   • {s}")
    except Exception as e:
        print(f"   ERROR: {e}")