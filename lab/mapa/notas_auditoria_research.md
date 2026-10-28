# Notas de auditoría — zona research (F42 §B)

Materia prima para F43: lo raro que vio cada worker leyendo su parte entera, con archivo:línea. Sin propuestas.

<!-- parte research_a -->
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

<!-- parte research_b -->
# Notas de auditoría — zona research, parte research_b

Archivos leídos enteros: topic_validator.py (1301 líneas), script_engine/youtube_scanner.py (1247), topic_researcher.py (1101), fase1.py (900). Los md5 al terminar coinciden con los de A en los cuatro. Sin proponer cambios.

## Discrepancias con A

- topic_researcher.py: A lo marca con etapas research, guion, papel, voz y assets (por el import de fase1_5.py). Leyendo, el único llamador desde fase1_5 es `research_de_semilla` (fase1_5.py:348-365 → `investigar_semilla`, topic_researcher.py:952), que se activa solo con `--semilla` (fase1_5.py:932-934). Los comandos del form para guion/papel/voz no pasan `--semilla`. Puse solo `research`.
- topic_validator.py: A dice `tests: []`; ningún test lo importa directo. `validate_topics` solo se nombra en tests que parchean fase1 (test_chat51_menu_pre_research.py). Las funciones privadas no tienen ninguna prueba.
- Las candidatas de A con `sin_llamador` en mi parte eran 3 y confirmé las 3: `fork_title` (youtube_scanner.py:573), `research_testimonios` (topic_researcher.py:390), `_save_script` (fase1.py:476).

## Código muerto o casi muerto

- topic_researcher.py:349-387 y 392: `TESTIMONIOS_ANGLE` y `_build_testimonios_prompt` solo se alcanzan desde `research_testimonios` (muerta). test_module_f6a.py prueba el prompt, así que en producción no corre.
- fase1.py:78: `SCRIPTS_DIR` solo lo usa `_save_script` (muerta).
- fase1.py:43 y 45: `OUTPUT_CSV` y `parse_decisions_csv` se importan y no se usan en el archivo.
- script_engine/youtube_scanner.py:470: `EN_OUTLIER_SLEEP_SEC` solo tiene la definición; el comentario de 643-645 dice que el sleep secuencial se quitó.
- fase1.py:57-62: `check_pending_promises` es un stub que devuelve None; por eso `_audit_pending_promises` (523-549) no hace nada nunca. Lo dice el propio docstring (TODO).
- fase1.py:827-837: `run_latido_b` solo imprime un aviso de deprecado; el aviso (834-836) habla de «m01a→m05→m06» y de leer «el CSV editado», que es la cadena que F41 borró.
- fase1.py:817-820: la rama sin `--no-chain` (`run_one_topic_from_menu` de fase1_5) no la usa el form; run_pipeline.py:530 siempre pasa `--no-chain`.

## Dos lógicas para lo mismo / duplicados

- `_build_proxy_url`: topic_validator.py:125 y script_engine/youtube_scanner.py:87 son copias (el comentario de topic_validator.py:121-123 dice que es a propósito). El id de sesión aleatorio también: inline en topic_validator.py:135 y como `_random_session_id` en youtube_scanner.py:108.
- Tres lectores de topics_db.json: `load_db` local en fase1.py:68 (con `import json` redundante en 70), `script_engine.topics_db.load_db` que usa topic_validator.py:58, y `_load_topics_db` en topic_researcher.py:867.
- `_load_seeds` duplicada: fase1.py:85 y topic_researcher.py:786, idénticas.
- seeds_archive.json con dos formatos: topic_researcher.py:833-862 (`_archive_seed`) escribe `{"archived": [...]}`; fase1.py:112-126 (`_archive_seed_local`) lee `.get("seeds")` y reescribe el archivo entero como `{"seeds": [...]}` (fase1.py:123). Si el archivo ya trae `archived`, esa reescritura lo deja afuera. fase1_5.py:257 lee `archived`.
- Scraping duplicado dentro del scanner: el bucle de pasadas `ES_SCRAPE_PASSES` está en `score_spanish_saturation` (youtube_scanner.py:1132-1141) y copiado en `list_spanish_candidates` (1190-1198). `count_competing_spanish` (1028) y `score_spanish_saturation` (1122) miden lo mismo de dos maneras (la segunda dice reemplazar a la primera solo en spy-arbitrage).
- Respaldo vs principal en el scanner: `_scrape_viral_english` no filtra por fecha (730-733, «ventana QUITADA») pero `_api_fallback_viral_english` filtra últimos 30 días (775, 788) y devuelve dicts sin `channel_id` ni `en_age_months` (818-824). `_api_fallback_es_en` usa 365 días (380) mientras `_scrape_es_en` no filtra edad.
- topic_researcher.py:549-560 y 396-422: la rama `RESEARCH_V3=0` (variable de entorno, researcher_steps/research_v3.py:57-61) conserva el camino viejo de 4 búsquedas resumidas (`_gather_angle_blocks`). Ese camino arma un evidence_pool sin la marca `_research_v3`, así que fase1_5.py:179-186 lo pararía en el guion.
- topic_researcher.py:688-779 (`_research_seed_simple`, SHORT): el topic resultante no trae evidence_pool, y fase1_5.py:179-186 para antes de gastar si falta. El form sigue ofreciendo SHORT (fase1.py:510-511).
- topic_validator.py:1101-1103: `_get_pending_topics` toma TODOS los topics con `competition_level` vacío, no solo el de esta corrida; si quedó alguno sin validar en la base, `validate_topics` lo valida también (Trends, YouTube y Gemini) y entra al sentinel de fase1.py:813.

## Rutas viejas y restos de la cadena borrada (F41)

- topic_validator.py:2 y 1138, youtube_scanner.py:2 y 1229-1231: mencionan `modules/...`, `python -m modules.topic_researcher` y `python -m modules.youtube_scanner`; la carpeta `modules` ya no existe. fase1.py:66 también dice «antes from modules.topics_db».
- topic_validator.py:1138 manda a correr topic_researcher a mano como primer paso; hoy lo llama fase1.py:771.
- fase1.py:30-31 y 57-62: dicen que channel_memory «no existe en el repo actual» y se reemplazó por stubs.

## Comentarios que contradicen el código

- topic_researcher.py:6 dice «5 sub-pasos Flash» (son 5: 4a a 4e); pero 527 («los 4 sub-pasos»), 533 («4 angle queries … + sub-pasos Flash»), 997 y 1024 («4 sub-pasos Flash») y fase1.py:769 («4 llamadas/seed») cuentan 4.
- topic_researcher.py:181: «3 llamadas × seed en LONG»; DEEP_RESEARCH_ANGLES (89-150) tiene 4 ángulos (y 413 usa `len(DEEP_RESEARCH_ANGLES)` workers).
- topic_researcher.py:127-128 («nadie lo consume aguas abajo todavía (eso es eslabón 2)») parece viejo: 603-605 pasa `angle_blocks` completos a `extract_visual_canon`, cuyo docstring (researcher_steps/step_4e_visual_canon.py:33) dice que incluye "visual".
- topic_researcher.py:557-559 dice que los sleeps entre ángulos se quitaron; en 570 sigue un `time.sleep(DELAY_BETWEEN_ANGLES_SEC)` fijo después de los ángulos, también con research v3.
- script_engine/youtube_scanner.py:843: «Busca videos EN del último(s) mes(es)»; el camino principal ya no filtra por fecha (730-733).
- script_engine/youtube_scanner.py:14-24: la lista de «funciones públicas» no nombra `score_spanish_saturation`, `list_spanish_candidates`, `compute_outlier_filter` ni `extract_anchors`, que son las que hoy usan otros módulos.
- script_engine/youtube_scanner.py:309-310: «Idéntica a la función que estaba en topic_validator»; ya no está allá.
- topic_validator.py:17-23: el docstring de cabecera no menciona la rama spy_arbitrage (353-393, 1066-1074), que saltea Trends.
- fase1.py:3-9: la cabecera lista 4 pasos (niche, research, validator, csv) y no nombra el juez ni la verificación del pick (PASO 1.5 y B2), que son lo central hoy.
- fase1.py:597-600 y 810-814: el sentinel se declara «lista vacía = no produje nada», pero `validated` puede traer más de un tid (ver topic_validator.py:1101).

## Números sin origen citado en el archivo

- topic_validator.py:66-71: `CACHE_TTL_HOURS` 24, `TREND_PIVOT_TRIGGER` 10, `YT_LIMIT_SCRAPE` 25, `DELAY_BETWEEN_TOPICS_SEC` 5. 145-146: `MOMENTUM_RATIO` 3.0 y `MOMENTUM_MIN_RECENT` 5.0. 289 y 304: 3 sugerencias y `sleep(2)`. 811: 12 hechos. 828-829: temperatura 0.85 y 2500 tokens de salida. Los umbrales de `validator_strictness` y `apuesta_viral` viven en config (no copié valores).
- topic_validator.py:747-748: lista fija de nombres de lugares de un caso (Pilbara) usada como filtro general; 561-578 y 772: ejemplos del prompt y del fallback con datos de un caso real (un doctor, una empresa, «20K likes»).
- script_engine/youtube_scanner.py:463-473 y 477-483: `OUTLIER_MIN`, `PISO_MEDIANA`, `ABS_FLOOR`, `PISO_DEMANDA`, `BASELINE_N`, `MIN_BASELINE_VIDEOS`, `EN_CANDIDATES_PER_QUERY`, tramos de `ES_DECAY_TIERS`, `ES_SAT_HUECO`, `ES_SAT_DISPUTADO`: citan «chat 42/43/44» y «no cambiar sin Omar», pero ninguno cita DECISIONES.md. 677: umbral 8.0 s/fetch del aviso de proxy, con medidas de «144b/144c/144d» en el comentario.
- script_engine/youtube_scanner.py:210-233: `_STOPWORDS` incluye palabras del nicho marino/submarinos puestas a mano en un filtro de anclas general.
- topic_researcher.py:77-78: `DELAY_BETWEEN_CALLS_SEC` 8 y `DELAY_BETWEEN_ANGLES_SEC` 6; 657-664: truncados 240, 80, 100 y 60 caracteres; 442 y 464-466: máximo 3 palabras en `search_keyword`.
- fase1.py:758: `n=3` re-mediciones (cita «CHAT 52 B2»); 317 y 328: cortes de 48 y 70 caracteres de pantalla.

## Imports y otros detalles

- topic_validator.py:669: `import re as _re` dentro de `_generic_fallback_hooks_outros`, aunque `re` ya está importado arriba (33). 725: f-string sin placeholders. 727-729: el comentario «Hook 3 — AUTORIDAD-NOMBRE» está repetido.
- topic_researcher.py:551, 554, 1040, 1098: imports a researcher_steps dentro de funciones; todos existen (`research_v3_enabled`, `run_seed`, `PoolGateRed`). No hay imports rotos en mis cuatro archivos.
- topic_researcher.py:1093-1101: el CLI corre `research_topics()` sin `video_type`, o sea SHORT por defecto (991), mientras que lo que la cadena usa de verdad es LONG.
- topic_researcher.py:392: `_ANGLE_PROMPT_BUILDERS.setdefault(...)` modifica un dict global dentro de la función.
- topic_validator.py:783-891 y 1203: `human_options` (3 hooks y 3 cierres con Gemini) solo lo leen csv_exporter.py, fase1.py (docstring) y un test; no vi con grep que lo consuma el guion v4.
- topic_validator.py:65 y 82: `data/trends_cache.json` no existe hoy (solo `ls`, sin leer).

<!-- parte research_c -->
# Notas de auditoría — zona research, parte research_c

Solo materia prima, sin propuestas. Los md5 de los 11 archivos coinciden con los de A al terminar de leer.

## Código muerto o casi muerto
- `researcher_steps/verify_quotes.py:166` `verify_literal` y `:241` `verify_testimonios`: ningún llamador en producción (el segundo solo lo toca `test_module_f6b.py`). Arrastran sin uso real a `judge` (81), `_parse` (71), `_domain` (50), `build_prompt` (34), `find_literal` (147), `doc_ok` (156) y `_search` (223); de todo el archivo solo se usan `_grounding`, `resolve_redirect`, `FFFD`, `_nz`, `_pattern` (research_v3.py:165,191,372,1179,1218,1227,1246) y `_named` (m01b_guionista.py:212).
- `researcher_steps/evidence_pool.py:697` `add_block`: solo `test_module_f6a.py` la llama.
- `script_engine/evidence.py:177` `format_pool`: nadie la nombra, ni tests; solo el docstring (línea 8).
- `researcher_steps/step_4d_summary.py:148-150`: `if len(summary) < 500: pass` no hace nada (el comentario dice que el orquestador loguea el tamaño; no lo hace esta función).

## Dos lógicas para lo mismo
- Verificación de citas literal: `verify_quotes.py:127-220` (`_nz`, `_pattern`, `find_literal`, `verify_literal`) y la verificación de `research_v3.py` (`DocText`, líneas 1177-1250, cuyo docstring dice que normaliza «como `verify_quotes._nz`») conviven; research_v3 solo importa de verify_quotes las piezas chicas.
- Armado del pool: con RESEARCH_V3 por defecto (`research_v3.py:57-61`) solo se usan de evidence_pool `fix_caps`, `_content_set`, `norm`, `acting_filter`, `anchor_place` y `geocode` (research_v3.py:1399,1718,1925,2042). `extract_evidence_pool` (758), `validate_block` (349), `merge` (444), `canonical_figures` (614), `presence` (678), `unrelated_lines` (191), `build_prompt` (319) y `SCHEMA` (65) corren solo con `RESEARCH_V3=0` (`topic_researcher.py:575`, `step_4a_facts.py:128`). research_v3 tiene su propio `canonical_v3`, `validate_doc_items` y `merge_docs` para lo mismo.
- `norm`: `evidence_pool.py:96` es un alias de `nombres.norm`; `script_engine/evidence.py:25` tiene su propia implementación (NFD sin marcas, no respeta la regla «solo letras latinas: й, ё intactas» que dice el docstring de la otra). Dos normalizaciones con el mismo nombre en dos módulos que se importan entre sí por el pool.
- `literal_in`: `evidence_pool.py:103` (subcadena normalizada) y `evidence.py:142` (con formas en palabras y números): mismo nombre, semántica distinta.
- `_content_set` (`evidence_pool.py:163`, raíces de 5, palabras ≥ 4, solo latino) vs `_content` (`evidence.py:157`, raíces de 6, palabras ≥ 5, cualquier alfabeto, con stopwords); `_sents` (`evidence_pool.py:182`) vs `_sentences` (`evidence.py:161`); `fix_caps` (`evidence_pool.py:292`, con lista fija `_COMMON_HEADS`) vs `fix_glued_caps` (`evidence.py:333`, con roles del pool + `nombres.tratamientos`). El comentario F21 de evidence.py dice que nombres.py es «única fuente», pero ambas versiones siguen vivas.
- `_num_forms`: `ficha_caso.py:360` devuelve `set[str]` y `evidence.py:106` devuelve `list[str]` (dígitos a palabras con `num_es.variants`); mismo nombre, tipo y fin distintos. `ficha_caso.py:412-448` (`word_numbers`: palabras a dígitos) es otra tabla de números en español aparte de `script_engine/num_es.py`.
- `step_4b/4c/4d/4e`: cuatro `_format_facts` casi iguales (`step_4b_canonical.py:17`, `step_4c_meta.py:25` con etiqueta de bloque, `step_4d_summary.py:17`, `step_4e_visual_canon.py:83`) y tres formateadores de bloques que truncan distinto (1500 en 4b, 800 en 4c, completo en 4d, 1500/6000 en 4e).
- `step_4a_facts.py:81` `with_pool=True` por defecto (llama a evidence_pool) y `topic_researcher.py:577` lo pisa con `with_pool=False` en la ruta v3: el parámetro existe para que la ruta v3 lo apague.

## Rutas de la cadena borrada (F41) o restos
- `ficha_caso.py:744` y `:844` importan `STEPS_DIR` de `script_engine/m01a_skeleton.py` (módulo que F41 recortó pero que sigue siendo dueño de `STEPS_DIR`, `finalize_pool_plan` y `SCREEN_PER_CAP`; m01a_escaleta.py:58 lo reimporta). No hay import roto.
- `ficha_caso.py:138-266`: tres SYSTEM de ~45 líneas cada uno (f23-1, f22-1, f15-1). F22 y F15 solo se piden con `system("f22-1")` / `system("f15-1")` explícito; no vi en producción ningún llamador con esa versión (el grep de `system(` fuera de tests solo muestra la del propio guion_v4.py:528 y el default). Sirven para tests byte-idénticos y reproducir fichas viejas, según sus comentarios (líneas 46-47, 136, 181, 226).
- `evidence.py:346` `resolve_declared` depende de `datos_usados`, que arma `m01b_guionista.py:84` desde `ids_usados`; su único llamador es `m01b_guionista.py:152` (dentro de `review`, que guion_v4.py:1216 sí usa).
- `step_4a_facts.py` y `step_4e` conservan la ruta `RESEARCH_V3=0` (4 ángulos resumidos) que research_v3.py:22 describe «sin cambios».

## Comentarios o docstrings que no coinciden con el código
- `step_4e_visual_canon.py:8-18` y `topic_researcher.py:11` dicen que el 4e produce 4 bloques; el código produce 5 (`central_subject`, líneas 412-415, 527-536, 597, 827) y el prompt dice «CINCO bloques» (línea 152). `extract_visual_canon` docstring (763-765) también lista 4.
- `step_4e_visual_canon.py:458` comenta «gemini_helpers L127-129» (referencia a línea ya vieja, no verificada).
- `step_4b_canonical.py:128` el comentario dice «Truncar si Gemini se pasó de palabras» pero el corte es por 500 caracteres (línea 129).
- `ficha_caso.py:335` el prompt de usuario fija «escenas (6–15), hechos (40–80), citas (10–25)» mientras SYSTEM_F22_1 y SYSTEM_F15_1 piden 8–15, 60–80 y 15–25: con `system("f22-1")` el sistema y la tarea final se contradicen.
- `ficha_caso.py:5-6 y :46 citan casos concretos (los 509 ítems de Ycuá, Orleans, Puerto Cardal) en docstrings de un módulo genérico.
- `pool_gate.py:6-12` y `:106-112`: el docstring y el texto del reporte repiten números (datos 150, citas verificadas 8, elegibles 2, eventos con fecha 10; pisos 40/2/3; «12 min», «≈ 1,500 palabras», «7–14 beats») que viven en `script_engine/video_length.py`; si cambian allá, el reporte seguiría diciendo lo viejo.
- `step_4d_summary.py:61` pide 1.800 palabras de guion y `step_4c_meta.py:61` «español neutro»; la ruta de guion actual es la v4, no verifiqué si esos números siguen vigentes.

## Números y reglas sin origen que encontré en DECISIONES.md
Busqué por grep en `DECISIONES.md` y no aparecen (el origen es solo un comentario de handoff F5/F14/F15b/F23 en el código):
- `evidence_pool.py:491` `GEO_MAX_KM = 400.0`, `:577` `CANON_RATIO = 1.5`, `:175` `UNRELATED_MIN_SHARED = 2`, `:624-625` piso de cifras ≥ 1000.
- `verify_quotes.py:124` `AUTHOR_WINDOW = 400` y `:160` «evento + 20 años».
- `ficha_caso.py:48` `MAX_LEV = 3` (el docstring lo cita de F12).
- `step_4e_visual_canon.py:110,113` truncados 1500 y 6000; `step_4c_meta.py:46` truncado 800; `step_4b_canonical.py:129` 500/497.

## Reglas hechas a medida de un caso
- `evidence_pool.py:289` `_COMMON_HEADS = ("Sheriff", "Huracán", "Teniente General", …, "Recluso")`, `:576` `_COUNT_NOUN` (reclusos|presos|prisioneros|evacuados…) y `:571-575` `_OFICIAL`/`_MEDIOS` (sheriff, departamento, estadísticas del…) están escritas para el caso de la prisión de Orleans, en un módulo genérico.
- `evidence_pool.py:59` `USER_AGENT` dice «contact: repo owner»; `geocode` pega contra Nominatim real con `time.sleep(1.1)` (red, no gasto en US$) cuando no hay caché.

## Cosas raras de comportamiento
- `ficha_caso.py:825-830` `save` toma el gasto de `cost_tracker.current_video`; corrida desde `main()` (`python -m researcher_steps.ficha_caso`, líneas 840-858) no abre video, así que `usd` queda en 0.0 aunque haya llamada paga. Con `usd=None` y sin video activo, igual.
- `ficha_caso.py:826` mismo módulo en `fase1_5.asegurar_ficha` (fase1_5.py:265): ahí sí hay video abierto o no según quién llame; no lo verifiqué.
- `step_4c_meta.py:158` `virality_score` solo lo nombra `topic_researcher.py` entre los archivos de producción (grep): no encontré otro consumidor.
- `research_summary` (4d) lo leen `m03_visual.py`, `m06_assembler.py` y `topic_validator.py` según grep; `m06_assembler` y `m03_visual` son de otra parte, no verifiqué si todavía están vivos en el form.
- `verify_quotes.py:223-238` `_search` usa `gemini_client` y `cost_tracker` con la etiqueta «verify_quote»; sin llamador real, así que esa etiqueta de costo no puede aparecer en una corrida actual.
- `pool_gate.py:43-44` `_tipo_evento` importa `caso()` de `research_v3` dentro de una función cuando el pool no trae `_tiempo`: dependencia de pool_gate hacia research_v3 y de research_v3 (línea 2609) hacia pool_gate.

## Discrepancias con `estado_a`
Ninguna: leí los 11 archivos y los 11 son `vivo`. Matices: `verify_quotes.py` está vivo solo por sus piezas chicas (ver arriba); la mayor parte de `evidence_pool.py` está viva solo con `RESEARCH_V3=0`. `evidence_pool.py` en A figura alcanzando fondos a render (por alias de nombres como `norm`); leyendo el código solo corre en `research`.

<!-- parte research_d -->
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
