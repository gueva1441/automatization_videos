# F39 A.3 — `topic_researcher.investigar_semilla` (subagente 2)

Base `a67ed45`, rama `f11-guion-v4`, sin commit. Archivos: `topic_researcher.py` (CRLF, verificado con `file`),
`test_module_f39_research.py` (nuevo). Cero llamadas a modelos, nada en `data/`, ningún número nuevo, ningún prompt tocado.

## Firma

```python
def investigar_semilla(seed: dict, topic_id: str) -> dict:
    """F39 §A.3: investiga UNA semilla en el topic `topic_id` y la registra en topics_db.

    La misma cadena que `research_topics(video_type="long")`: `_research_seed_deep` (research v3 `run_seed` en
    `STEPS_DIR / topic_id` + sub-pasos 4a–4e) + `_enrich_with_seed_metadata`, pero:
      - el topic queda con `id == topic_id` (no uuid4) y guarda `seed_title` (el título de la ficha, como F23/F24);
      - sin el filtro de semillas ya investigadas;
      - no toca el inbox (`selected_seeds.json`) ni el archivo de semillas (`seeds_archive.json`).
    `topic_id` ya en topics_db → ValueError antes de gastar (y de nuevo al registrar: no pisa).
    Compuerta del pool en rojo → `PoolGateRed` se propaga (no se registra nada).
    Devuelve el topic tal como quedó guardado."""
```

## Diff resumido (`git diff --stat`: 1 archivo, +42 −3)

- `_research_seed_deep(seed, existing_titles, topic_id=None)`: `topic_id = topic_id or str(uuid.uuid4())`
  (antes, siempre `uuid4`). Una línea del docstring. El resto de la cadena no cambia.
- `_topic_registrado(db, topic_id)` (auxiliar nueva, 1 línea).
- `investigar_semilla` (nueva), en este orden:
  1. `ValueError` si `topic_id` está vacío, si a la semilla le falta `seed_id`, `seed_title` o `discovery_mode`
     (`_enrich_with_seed_metadata` los pide al final, y sin este chequeo la falla llegaba después de gastar), o si
     `topic_id` ya está en topics_db. Todo antes de gastar.
  2. `_research_seed_deep(seed, títulos existentes, topic_id=topic_id)`. Si da `PoolGateRed`, la excepción se
     propaga.
  3. `_enrich_with_seed_metadata` + `"seed_title": seed["seed_title"]`.
  4. Vuelve a leer topics_db, porque el research tarda minutos. Si el id apareció mientras tanto, `ValueError`.
     Si no, append + `_save_topics_db`.
  5. Dos `print`: el de arranque y el de registro.
- `research_topics`: **no se tocó**. Sigue llamando `_research_seed_deep(seed, existing_titles)` con 2 argumentos
  (o sea, uuid4), con el mismo filtro, el mismo inbox y archivo, y su topic sigue sin `seed_title`.

## Tests

`python -m pytest -v test_module_f39_research.py` → **5 passed**:

| test | qué prueba |
|---|---|
| `test_investigar_semilla_registra_con_el_id_dado_sin_tocar_inbox_ni_archivo` | id = el dado, `seed_title`, orden `run_seed(tid, STEPS_DIR/tid)` → 4a → 4b → 4c → 4d → 4e, topic guardado igual al devuelto, los 6 `0X_*.json` en `_steps/<id>/`, inbox y `seeds_archive` byte a byte iguales |
| `test_investigar_semilla_no_filtra_semillas_ya_investigadas` | el mismo `seed_id` ya en topics_db con otro id → igual investiga y registra |
| `test_id_ya_en_topics_db_es_valueerror_sin_llamar_run_seed` | id repetido / id vacío / semilla sin `discovery_mode` → `ValueError`, 0 llamadas, topics_db intacto, sin `_steps/<id>/` |
| `test_pool_gate_red_se_propaga_y_no_registra` | `PoolGateRed` sale con sus motivos, 4a–4e no corren, no se crea topics_db y el inbox queda sin bandera |
| `test_research_topics_igual_que_antes` | saltea la semilla ya investigada, uuid4 de 36 caracteres, `run_seed` con ese id, saca del inbox, archiva con el topic_id, no hay `seed_title` |

Tests existentes de `topic_researcher` (`grep -ln topic_researcher test_module_*.py`): `test_module_f10/f5e/f6a/f7d`
**28 passed**, sin cambios. `test_module_00.py` no tiene funciones `test_` (es un script) y da 0 tests.
Suite rápida `test_module_f25c.py test_module_f24.py test_module_f21.py`: **58 passed**.

Sticker: `topic_researcher` **no está** en `lab/MAPA_MODULOS.md`, así que no hay sticker que actualizar.
