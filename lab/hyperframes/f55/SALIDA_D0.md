# F55 — Salida D.0 (texto)

## 1. Ids de citas en las tres copias del pool

Ver `SALIDA_B.md` §3 (corrida de `dedupe_pool.py` de D.0): `topics_db.json`, `01_facts_sources.json` y `00_pool_v3.json` tienen las mismas 50 citas y los mismos 8 descartados (Q12, Q15, Q20, Q23, Q26, Q28, Q29, Q30).

## 2. La ficha cargada (`ficha_caso.load`)

- ids descartados en `ficha_caso.json` **en disco**: 36 apariciones ({'Q15': 5, 'Q12': 7, 'Q20': 7, 'Q23': 11, 'Q26': 4, 'Q28': 2}); `ids_remapeados` = 36.
- log de `load`: ['  [ficha] 36 id(s) de citas duplicadas remapeados al cargar (el archivo no cambia)']
- `grep` de `Q12|Q15|Q20|Q23|Q26|Q28|Q29|Q30` sobre el JSON de la ficha **cargada**: **0**.
- el archivo en disco no cambia (md5 igual antes y después de `load`).
