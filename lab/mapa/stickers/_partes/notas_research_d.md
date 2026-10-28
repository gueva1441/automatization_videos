# Notas de auditoría — zona research, parte research_d

Solo lectura; md5 de los 11 archivos iguales a los de A al terminar. Sin propuestas de cambio.

## Estado distinto o matizado respecto de A
- `script_engine/subtopic_classifier.py`, `subtopic_extractor.py`, `transcript_fetch.py` (y `_measure_en_laxo` en `subtopic_measurer.py:158`): A los marca `vivo`; yo también, pero solo se ejecutan con `SUBTEMA_FANOUT=1` (`niche_discoverer.py:175`, por defecto `"0"`). Nada de lo que leí en .py/.bat/.json del repo setea esa variable, así que en una corrida normal del form esa rama está apagada. `.env` no se leyó.
- `script_engine/learned_patterns.py`: de acuerdo con `huérfano`. Su único cliente es `script_engine/m05_judge.py:37`, y ningún archivo de producción importa `m05_judge` (solo tests y comentarios; `fase1_5.py:15` lo declara desconectado). `get_root_cause` (`learned_patterns.py:61`) figura con llamador en A solo por ese archivo desconectado.
- `nicho_config.py`: A le pone todas las etapas por alcance de imports. Lo que lo usa de verdad es `gfx_config.py:362` (render/pantalla). `script_engine/m03_visual.py:103` importa `get_active_nicho` pero nunca lo llama (el nombre aparece una sola vez en el archivo).
- `subtopic_measurer.measure`: A la ve con llamador (`researcher_steps/pool_gate.py`) por homonimia; ese es `pool_gate.measure` (`researcher_steps/pool_gate.py:61`), otra función. La de `subtopic_measurer.py:203` solo la llaman tests.

## Código muerto o sin llamador
- `script_engine/topics_db.py:52` `get_pending_for_video` y `:131` `revert_generation`: nadie las nombra, ni tests.
- `script_engine/learned_patterns.py:67/79/90`: `add_learned_regex`, `record_other`, `maybe_promote_other`; además `OTHER_OCCURRENCES` (`:48`) y `LEARNED_REGEX_PATTERNS` (listas vacías) nunca se llenan desde producción. `m05_judge.py:251` lee `LEARNED_REGEX_PATTERNS["text_in_image"]` que siempre es `[]`.
- `script_engine/subtopic_measurer.py:203` `measure()`: solo tests (`test_subtopic_measurer.py:29`, `test_subtema_fanout_dryrun.py:56`).

## Lógicas duplicadas
- Cargar/guardar `topics_db.json` existe en cuatro lugares: `script_engine/topics_db.py:25/32`, `fase1.py:66-74` (`load_db` propio, con el comentario "REEMPLAZO … antes from modules.topics_db"), `migrate_4e_into_topics_db.py:50/59` (con ruta relativa `Path("data")` en `:33`, no `config.DATA_DIR`) y `topic_researcher.py`/`csv_exporter.py` (según A, `_load_topics_db`).
- `purge_history.py:56-68` `_filter_topics_db` repite el filtrado de `:71-83` `_execute_purge` (dos copias de la misma regla de qué topics sobreviven).
- `TRANSCRIPT_CAP = 500_000` aparece idéntica en `transcript_fetch.py:31`, `subtopic_classifier.py:55` y `subtopic_extractor.py:29`.
- `subtopic_extractor.py:27` y `subtopic_es_relevance.py:23` repiten el mismo bloque `_client.models.generate_content(... _cfg.gemini_model ...)` en vez de pasar por `gemini_helpers.call_flash_json`.

## Costo fuera del bus
- `subtopic_classifier.py:66`, `subtopic_extractor.py:82/133` y `subtopic_es_relevance.py:60/123` llaman a Gemini con `_client.models.generate_content` directo; `_with_retry` no registra costo y no hay `cost_tracker` en esos archivos. En cambio `m_judge_seeds.py:102` usa `call_flash_json`, que sí lo registra (`gemini_helpers.py:193`). Las llamadas de `_measure_es` (traducción y juez ES) a la rama atómica, que sí es la normal, no pasan por el tracker.
- `subtopic_measurer.py:93`: con `already_es=True` igual se llama a `translate_to_es` (una llamada Gemini) solo para sacar aliases y se descarta el `es_query`; el comentario lo explica, pero el gasto es por cada medición.

## Números sin origen visible
- `subtopic_measurer.py:49` `LAXO_FLOOR_VIEWS = 50_000`: el comentario de `:48` dice "decisión abierta #2, lab=50k provisional". `:50` `EN_SEARCH_LIMIT = 15` y `:54` `EN_MIN_CANDS = 5` sin fuente.
- `subtopic_es_relevance.py:104` `_MAX_TITLES = 60`; `subtopic_extractor.py:123` `batch=40`.
- `m_judge_seeds.py:37` `N_VOTES = 3` ("mismo patrón que m05"), y el prompt de `:53-91` trae cifras de ejemplo (185x, 2.000, 1M+) y "documental 8-10 min" fijos.
- `temperature=0.0` repetido en todas las llamadas de subtopic_*.

## Comentarios y docstrings que no coinciden con el código
- `script_engine/topics_db.py:10`: el ejemplo dice `from modules.topics_db import mark_as_generated`; ese paquete `modules` ya no existe (el módulo vive en `script_engine`).
- `m_judge_seeds.py:17` documenta `judge_seeds(seeds, n_votes=3)`, pero la firma de `:154` tiene además `force`. `:19-20` cita `python -m script_engine.m_judge_seeds` como re-validación y `:4` menciona `_lab_judge_seeds.py` (existe en la raíz del repo, fuera de `lab/`).
- `m_judge_seeds.py:150-188`: tres votos todos en error dan `verdict="error"` con cohorte `3/3` (`_aggregate`, `:133-139`); no hay caso específico y fase1 solo descarta por 3/3 de `descartar` (según el comentario de `:10-12`).
- `subtopic_es_relevance.py:1` dice "Piezas 1 y 3"; la Pieza 2 está en `subtopic_measurer.py:103` (scrape ES), no en este archivo.
- `nicho_config.py:37-38`: "Futuro: se podría leer de config.py ACTIVE_NICHO o similar"; hoy `ACTIVE_NICHO` es constante fija y `estrategia`, `ancla_global` y `referencias` no los lee nadie en producción (solo `nombre`). Docstring de `:7` manda a correr `test_lab_v6.py`.
- `migrate_4e_into_topics_db.py:9-10` cita `test_module_00_4e.py` como generador de `05_visual_canon.json`; el que lo produce en el pipeline es `researcher_steps/step_4e_visual_canon.py`.
- `topics_db.py:52-64` `get_pending_for_video` filtra `status == "validated"` y `competition_level`; no verifiqué si esos valores todavía los escribe la cadena actual.

## Rutas de la cadena borrada (F41) / limpieza
- `purge_history.py:8-10` y `:100-113` borran `data/scripts/_steps/`, `data/scripts/<id>.json` y `data/issues_log/`; `migrate_4e_into_topics_db.py:35` lee `data/scripts/_steps/<id>/05_visual_canon.json`. Según el log de commits, el research de `_steps/` ya se limpió; no verifiqué si `data/scripts/<id>.json` ni `data/issues_log/` los sigue escribiendo algo.
- `purge_history.py:160`: aviso "se borra TODO incluyendo el topic recién inyectado"; con `--keep` la preservación de `topics_db.json` filtra por `id` o `topic_id`, y borra `selected_seeds.json` y `fase1_review.csv` siempre, sin backup (a diferencia de `migrate_4e_into_topics_db.py:67`, que sí lo hace).
- `migrate_4e_into_topics_db.py` y `purge_history.py` no tienen ningún llamador ni test (solo aparecen nombrados en `lab/tools/mapa_modulos.py:34` y `hechos`).

## Imports y detalles
- `script_engine/m03_visual.py:103`: `from nicho_config import get_active_nicho` sin uso (ver arriba).
- `gfx_config.py:362`: el import de `nicho_config` va dentro de `try/except Exception` y cae a `""`; si `nicho_config` desapareciera, el perfil caería en silencio al default.
- `subtopic_extractor.py:101`: `except Exception: return []` hace indistinguibles "falló Gemini" y "no hay sujetos"; a diferencia de `subtopic_classifier.py:81`, que devuelve `tipo="ERROR"`. `verify_names` (`:150`) también traga excepciones con `pass`.
- `transcript_fetch.py:64,75`: `youtube_transcript_api` se importa dentro de la función (a propósito, por el bug histórico del comentario `:66`).
- `script_engine/learned_patterns.py` no tiene docstring de módulo (comentarios `#`).
