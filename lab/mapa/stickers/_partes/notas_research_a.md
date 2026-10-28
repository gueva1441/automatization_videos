# Notas de auditoría — zona research, parte research_a

Archivos leídos enteros: `researcher_steps/research_v3.py` (2612 líneas) y `niche_discoverer.py` (1582 líneas). El md5 al terminar es igual al de A en los dos (2a4b4247… y ca8822da…).

## researcher_steps/research_v3.py

- `research_v3.py:21-22` y `:58`: la docstring del módulo y la de `research_v3_enabled` dicen que el camino viejo (4 ángulos resumidos) «queda detrás de RESEARCH_V3=0, sin cambios»; `topic_researcher.py:548-577` todavía lo tiene vivo (`_gather_angle_blocks`) después de la limpieza de F41, que borró otras cadenas viejas pero no esta.
- `research_v3.py:1015` `rebuild_texts`: sin ningún llamador en el repo (ni producción, ni tests, ni strings).
- `research_v3.py:2074` `metrics`: solo la llaman `test_module_f7.py:333` y `lab/hyperframes/f7/f7b_pool_orleans.py:90`; los hechos de A le atribuyen `fase2b.py` y `depth_probe.py`, pero ahí `metrics` es una variable local (p. ej. `fase2b.py:2424`): falso positivo.
- `research_v3.py:1382-1390`: rama inalcanzable; `FOCUS_SOLO_METRICA = True` (L1368) es una constante y el `return` de L1380 siempre sale antes.
- `research_v3.py:1656-1657` `_TITLES_BASE` y `_TITLES`: alias de módulo que nadie lee (`_TITLES` solo se reasigna en `set_vocabulario`, L1689 y L1697).
- `research_v3.py:1687`: la docstring de `set_vocabulario` habla de `_NOT_PERSON`, que ya no existe como nombre en el código (`script_engine/nombres.py:103` dice que `_GRUPO` es «lo que queda de _NOT_PERSON»).
- `research_v3.py:664` y `:800`: `import unicodedata` dentro de `detect_lang` y `fuente_idioma` aunque el módulo ya lo importa arriba (L32); en `detect_lang` (L667) una variable local `nombres` tapa al módulo `nombres` importado en L39.
- `research_v3.py:657-658`, `:661-675` y `:797-806`: tres lógicas de alfabeto → idioma: `_ALFABETOS`, las reglas de `detect_lang` y el dict inline de `fuente_idioma` (este sin `cjk`); dos funciones distintas para lo mismo.
- `research_v3.py:1586`: `1.25` y `10.0` (USD por millón de tokens de entrada y de salida) y `CHUNK_CHARS / 2.5` (caracteres por token) escritos a mano en el peor caso del tope de costo, sin origen citado ni vínculo con config.
- `research_v3.py:1558-1561` `_gasto_tracker`: lee `cost_tracker._lock` y `_all_entries()` (miembros privados de otro módulo).
- Números de tuning sin origen en `DECISIONES.md` (grep de MAX_DESCARGAS, COUNT_MIN, CANON_RATIO, POP_BAND, R1_TEMPERATURE, MAX_DOC_CHARS y WORKERS en DECISIONES.md: sin resultados): L44-52 (`MIN_FUENTES, MAX_FUENTES = 8, 20`, `MAX_DESCARGAS_OK`, `WORKERS`, `MAX_DOC_CHARS`, `MIN_DOC_CHARS`, `TIMEOUT_S`), L156 `R1_TEMPERATURE`, L1266-1270, L1365-1367, L1659 `COUNT_MIN`, L1739 `ITEM_YEARS`, L1896-1897 `CANON_*`, L1966-1967, L2178 `POP_BAND`, L2231-2236 `DIGEST_*`, L2361-2362 `FRAGMENT_*`. Solo traen comentarios de tanda (F20, F23, F26…), no citan DECISIONES.
- `research_v3.py:53-54`: el `USER_AGENT` lleva «automatization_videos-research/0.7», parece el número de F7 y no se movió desde entonces.
- `research_v3.py:847`, `:1127` (`time.sleep(0.5)`) y `:957` (`_por_sitio`): pausas fijas más un candado por sitio dentro de hilos; la espera de la Wayback (`WAYBACK_PAUSE_S = 3.0`) se suma dentro del mismo hilo.
- `research_v3.py:2604` y `:2611`: `00_pool_v3.json` se escribe antes de asignar `pool["_pool_gate"]`, así que ese campo no queda en el archivo que escribe `run_seed` (solo en el pool devuelto).
- `research_v3.py:2562`: `from config import DATA_DIR` dentro de `run_seed`; solo para `geocode_cache.json` (L2602); el resto de las rutas llegan por argumento.

## niche_discoverer.py

- `niche_discoverer.py:198` `_load_seeds`: sin llamador; `fase1.py:85` y `topic_researcher.py:786` definen cada uno la suya (tres copias del mismo nombre). Los hechos de A la daban como usada por esos dos archivos.
- `niche_discoverer.py:208` `_save_seeds`: `fase1.py:99` (docstring) dice «Mismo esquema que niche_discoverer._save_seeds»; el esquema de `selected_seeds.json` está duplicado en dos archivos.
- `niche_discoverer.py:76` `_emit_qaform_choice_marker`: copia declarada de la de `fase1.py:242` (comentario L70-72: se replica, no se importa, para evitar un import circular). A le atribuye `fase1.py` como llamador, pero `fase1.py` llama a la suya.
- `niche_discoverer.py:157-160`: `SPY_TOP_PER_QUERY`, `SPY_ES_WINDOW_MONTHS`, `SPY_ES_MIN_VIEWS` y `SPY_MAX_COMPETING_FOR_GAP` sin uso en producción; solo `_lab_chat44_workers.py` usa tres de ellas y `SPY_TOP_PER_QUERY` no la usa nadie.
- `niche_discoverer.py:168` `SPY_MIN_EN_VIEWS`: marcada «deprecado» y solo se usa en la tabla del dry-run (L618).
- `niche_discoverer.py:55` `score_spanish_saturation`: importada y nunca usada en este archivo (solo aparece en comentarios, L62).
- `niche_discoverer.py:874` / `:606` `_print_dry_run_table`: `dry_run=True` solo lo pasan scripts sueltos (`_dry_run_modeA_chat42.py:22`, `_lab_chat44_workers.py:11`); desde `discover_niches` (L1493) nunca.
- `niche_discoverer.py:175` `SUBTEMA_FANOUT`: apagado por defecto (`SUBTEMA_FANOUT=0`); todo el fan-out (`_try_subtema_fanout` L657-840, `_apply_fanout_cap`, `_persist_dropped_by_cap`) solo corre si alguien exporta esa variable; ningún `.py` de producción la fija (el `.env` no se lee).
- `niche_discoverer.py:525-604` `_gemini_translate_viral_titles`: es la única llamada a Gemini del archivo que no anota el costo (las de L390 y L1174 sí llaman a `cost_tracker.track_gemini_response`).
- `niche_discoverer.py:1120-1155`: el prompt de arqueología fija «1950-2000» y «poco conocido hoy en 2026» con el año escrito a mano.
- `niche_discoverer.py:1570`: el mensaje final dice «python -m modules.topic_researcher», pero la carpeta `modules/` no existe (hoy es `topic_researcher.py` en la raíz).
- `niche_discoverer.py:26`: la docstring dice «modules.youtube_scanner»; el import real (L50) es `script_engine.youtube_scanner`.
- `niche_discoverer.py:1291` `_run_manual` y `:1478`: Modo C está deshabilitado en el form (`"disabled": True`); solo se llega desde terminal.
- `niche_discoverer.py:1201` y `:1224-1252`: la docstring de `_run_archaeology` dice «competing_count ≤ 3» como valor fijo; el código usa `apuesta_viral.*` de config (nombres: `max_competing_videos`, `min_views_to_count`, `window_months`).
- `niche_discoverer.py:264-279` `_extract_json_array`: reemplaza todos los saltos de línea del array por espacios antes de parsear, también los que estén dentro de strings.

## estado_a de A vs lo leído

- Los dos «vivo»: coincido.
- Etapas: `niche_discoverer.py` corre solo en `research` (fase1.py). `research_v3.py` corre en `research` (run_seed) y en `guion` (set_vocabulario / vocabulario / caso desde fase1_5, guion_v4 y m05_narrative). A marcó también `papel`, `voz`, `assets`, `fondos`, `guion_pantalla`, `aprobar_guion` y `render` por alcance de imports; en `assets`, `fondos`, `guion_pantalla` y `render` no vi un uso real, pero no rastreé cada camino de `m05_narrative`/`pool_gate` hacia esas etapas, así que `papel` y `voz` quedan sin confirmar.
