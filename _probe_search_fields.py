# _probe_search_fields.py — vuelca TODOS los campos crudos de un search de scrapetube
# Correr: python -X utf8 _probe_search_fields.py
import scrapetube, itertools, json

# usa tu proxy si lo querés (descomentá las 2 líneas)
# from script_engine.youtube_scanner import _proxies_dict
# px = _proxies_dict()
px = None

QUERY = "declassified medical experiments"   # cambiá por una puerta tuya
N = 3                                          # cuántos resultados inspeccionar

results = scrapetube.get_search(QUERY, limit=N) if px is None else \
          scrapetube.get_search(QUERY, limit=N, proxies=px)

for i, v in enumerate(itertools.islice(results, N)):
    print(f"\n{'='*70}\nRESULTADO {i}  — claves top-level: {list(v.keys())}\n{'='*70}")
    # volcado completo del dict crudo (todo lo que trae YouTube por video)
    print(json.dumps(v, ensure_ascii=False, indent=2)[:6000])