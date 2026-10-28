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
