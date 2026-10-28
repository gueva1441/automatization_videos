# Notas de auditoría — zona fase2a (F42 §B)

Materia prima para F43: lo raro que vio cada worker leyendo su parte entera, con archivo:línea. Sin propuestas.

<!-- parte fase2a_a -->
# Notas de auditoría — zona fase2a, parte fase2a_a

Los 6 archivos se leyeron enteros (m03_visual.py 2747 líneas en 4 tramos). Los md5 de los 6 coinciden con los de A al terminar.

## Estado y etapas distintas de lo que marca A

- `script_engine/vision_validator.py` (todo el archivo): A lo marca vivo en 6 etapas por la cadena de imports. En realidad `validate_image` y `build_corrected_prompt` solo se llaman si `ENABLE_VISION_VALIDATOR` (asset_manager.py:68) es True, y la constante está fija en False; el módulo se importa (asset_manager.py:52) pero nunca ejecuta. Lo dejé como `vivo` por el import y lo expliqué en `estado_prueba`; el estado real es dormido por constante.
- `script_engine/m03_visual.py`: A le da research, guion, papel, voz, assets, packaging. Lo que corre de verdad es `assign_visual_prompts` en el tramo audio -> m07 -> m03 de `fase1_5.py` (línea 632), o sea etapa `voz` (el `--from normalizer_gate`). Las otras etapas solo lo alcanzan por import. packaging lo carga porque `m09_packaging.py:40` importa sus constantes DOCTRINE_*; ahí no corre ninguna función de m03.
- `script_engine/m03_imagenes_v3.py`: ídem, solo `voz`.
- `script_engine/image_grade.py`: A lo marca en 6 etapas; corre solo en `assets` (asset_manager.py:1321 -> `_apply_grade`).
- `depth_probe.py` y `zoom_judge.py`: A dice fondos, guion_pantalla, aprobar_guion, render. `aprobar_guion` no los toca (fase2b.py:3719 sale antes de procesar el video). `fondos`: puerta de zoom (fase2b.py:3300, solo sin `--reuse-visuals`). `guion_pantalla` y `render`: `_route_safe` (fase2b.py:3376) corre con `--gfx` (el plan-only lo activa) y vuelve a llamar a `judge_candidates` sobre imágenes con persona (fase2b.py:2617), o sea llamadas de visión en esas dos etapas también.

## Código muerto o sin uso

- `m03_visual.py:1368` `_format_bullets`: sin ningún llamador en el repo.
- `m03_visual.py:1374` `_format_visual_canon_block`: sin llamadores; el docstring de `_format_seedream_canon_block` (línea 367) lo llama "espejo"; `test_module_m03_reglas_133.py:10` lo declara "dead code" y cuenta su texto en el fuente.
- `m03_visual.py:1895` `_validate_no_text_leakage`: solo la usa `test_module_03_text_leakage_casing.py` (que además hace `import m03_visual` sin el prefijo `script_engine`). El camino real usa `_find_text_leakage` (línea 1972), que duplica sus patrones y pasadas a propósito (comentario en 1969).
- `m03_visual.py:112` `VALID_LIGHT_MODES`, `:1237` `VALID_RANKS`, `:1190` `FLUX_CHAPTERS`: constantes definidas y nunca leídas en producción. `MAX_RETRY_ATTEMPTS` (1239) solo se usa como default de `_call_with_validation_retry`.
- `m03_visual.py:103` `from nicho_config import get_active_nicho`: importado, nunca usado en el archivo.
- `m03_visual.py:2489-2498` `_stitch_zone2_into_cap_veo/flux`: no-ops explícitos desde el chat 19, se siguen llamando (2649 y 2702); no los conté como muertas porque tienen llamador.
- `image_grade.py:77` `stats`: solo tests.
- `depth_probe.py:182` `DEFORM_RISK_LEVELS`: constante sin uso; `deform_risk` (186) recibe `metrics` y no lo usa; el nivel `mid` "existe en el contrato, sin regla" (comentario 177-180).

## Dos lógicas para lo mismo / duplicación

- `m03_visual.py` tiene dos detectores de fuga de texto (`_validate_no_text_leakage` que levanta error y `_find_text_leakage` que devuelve el span) con los mismos patrones copiados en dos cuerpos (1923-1951 y 1978-1995).
- `m03_visual.py:1374` y `:364`: dos bloques de canon visual (el viejo sin uso y el de 2 capas).
- `m03_visual.py:1881` `_validate_prompt_length` (rango 120-700) y `:814` (rango 120-2500 con `KLING_PROMPT_MAX_CHARS`): dos topes de largo distintos para prompts de imagen; el de 700 solo se usa hoy en el motion del clip Veo (`_seedream_video_prompt`, 2401).
- `m03_visual.py` `_build_plan_anchors_prompt_veo/flux` y `_validate_plan_veo/flux`: dos ramas casi idénticas para "veo" y "flux", aunque el motor es único (seedream).
- `depth_probe.py:48-50` y `:144-146`: las mismas tres variables de entorno (DEPTHMAP_CACHE_SIZE_MB, TORCH_DEVICE, CUDA_VISIBLE_DEVICES) se fijan dos veces, en el runner y en `probe_images`.
- `vision_validator.py:42` fija `VISION_MODEL = "gemini-2.5-flash"` en el archivo, mientras `zoom_judge.py:77` usa `api.gemini_model` de config: dos maneras de elegir el modelo de visión.

## Comentarios y docstrings que contradicen el código

- `m03_visual.py:73`: "LLAMADAS GEMINI: 7 (Flash, 1 por cap, secuencial). ~$0.010/video". Hoy son Pro para slots (`SEEDREAM_SLOTS_USE_PRO = True`, 139), Flash para anclas y para el fluidificador por imagen, y un Pro para el motion; paralelo por cap (`CAP_MAX_WORKERS`). Costo sin origen en el código.
- `m03_visual.py:53` y `:79-81`: el docstring habla de prompts de 120-400 caracteres y de N = clamp(.., 6, 18); el código usa `PROMPT_MAX_CHARS = 700` y `KLING_PROMPT_MAX_CHARS = 2500`; y la fórmula tiene además tope por video (línea 1326-1331).
- `m03_visual.py:1227-1232`: el comentario describe un "ANCLA_GLOBAL + 3 slots del Traductor" (refactor v6 chat 27), que ya no existe.
- `m03_visual.py:1235`: la constante se llama KLING_ pero la usa el camino seedream; el comentario habla de "endpoint Kling".
- `m03_visual.py:2544-2549`: "los paths flux/kling/veo-old fueron removidos", pero el módulo conserva `render_engine == "flux"/"veo"` como nombres de rama, `_calculate_image_count` hablando de "Flux" y comentarios de "Flux/Kling" por todo el archivo.
- `m03_visual.py:1115`: `F8_NOTE_BODY_HOOK ="NO ..."` (falta un espacio; cosmético).
- `foto_madre.py:36` y `lab/probe_orphan_mothers.py:71` citan `m03_visual.py:149` / `L149` como lugar del slot `style`; hoy ese slot está unas ~55 líneas más abajo (el comentario de otro archivo quedó viejo).
- `image_grade.py:6-9` (docstring) dice saturación 0.72 y frío 0.03; `DEFAULTS` (24-30) trae `saturation` 0.70 y `cool` 0.02. `gfx_profiles/misterio.json` no tiene clave `image_grade`, así que valen los DEFAULTS.
- `vision_validator.py:5-6`: habla de "Flux" y de "Veo (caro: $0.24/clip)": precio sin origen y motor que el código ya no usa como único. El decorador `@error_handler.retry` de `validate_image` (130) casi no actúa: la función atrapa sus propias excepciones y devuelve fail-open.
- `depth_probe.py:177`: comentario "Nocturno §3 (default)" sin referencia a un documento.
- `m03_imagenes_v3.py:3-4`, `asset_manager.py:1199-1200`: hablan de guion v2 "sin escaleta" que sale byte-idéntico; tras F41 la cadena v2 está borrada y un tema sin escaleta ya no llega a m03 (`fase1_5.py` para antes). La rama `f8_beats is None` de `assign_visual_prompts` (2571) queda alcanzable solo desde tests y desde labs.

## Rutas de la cadena borrada (F41) que siguen vivas

- `m03_visual.py:2570-2574` y todas las condiciones `if f8:` / `if f8_beats:` (1008, 1049, 1063, 2696, 2727): la rama "sin escaleta / guion v2" se mantiene; sin escaleta se usa `SYSTEM_INSTRUCTION_VISUAL_SEEDREAM` (no el V3, línea 1003).
- `m03_visual.py` conserva el contrato de 7 capítulos con caps `veo` 1 y 7 (`VEO_CHAPTERS`, `EXPECTED_CHAPTER_COUNT = 7`) que viene del guion viejo; el guion v4 produce 7 caps pero la lógica de `render_engine` por cap sale del esqueleto (`01a_*.json`).
- `m03_visual.py:1352-1365` `_format_facts`: también lo importan los pasos de researcher_steps (step_4b/4c/4d/4e); es un helper compartido, no exclusivo de m03.

## Números sin origen citado en el archivo

- `m03_visual.py:146` `FLUIDIFY_MAX_WORKERS = 16` (origen: comentario "conservador", pico ~16 RPM; sin cita), `:152` `CAP_MAX_WORKERS = 7`, `:764` `LEAK_MAX_RETEJIDOS = 2`, `:1114` `F8_FIX_PASSES = 2`, `:1196-1197` `MIN_IMAGES_FLUX = 6`, `MAX_IMAGES_FLUX = 18`, `:1216-1217` `MIN_FLUX_EXTRAS = 4` / `MAX_FLUX_EXTRAS = 14`, `:547` `MAX_MEASURES_PER_IMAGE = 1`, `:717` y `:714` `thinking_budget=0` (cita HANDOFF_134b), `:1206` `MIN_ANCHOR_GAP_SEC = 1.0` (cita calibración chat 54), `:1195` `SECONDS_PER_IMAGE_TARGET = 7.0` (cita test_movements_v12).
- `m03_imagenes_v3.py:232` `MOTIF_MAX = 2`, `:423` `TEXT_MAX_WORDS = 3`, `:405` umbral de 100 en `beat_scale`, `:539` 25 % de planos medios, `:555` zoom 1.3-1.6 en `reencuadres`: origen en el docstring del handoff F8/F8b, sin valor en DECISIONES citado en el archivo.
- `image_grade.py:24-30` (saturación, lift, viñeta, grano, frío) y `:85` (luma > 24): citan "F8b §2.6" y una medición ("baja ~18 %"), no un estándar.
- `depth_probe.py:32-33` (`DEPTH_ZOOM_CB_MIN = 0.15`, `MAX_ZOOMS_PER_CHAPTER = 7`): citan lab chat 55 y HANDOFF_140b (C4).
- `zoom_judge.py:92` recorte de `razon` a 160 caracteres y `vision_validator.py:191-195` recortes a 200: sin origen.

## Otros

- `m03_visual.py:747-753` (`_fluidify_item`): con `sin_respuesta == max_attempts` devuelve los slots crudos sin tejer (F27 §A.1) y los cuenta como prosa válida para el resto de la cadena.
- `m03_visual.py:1039`: `raw_llm_prompt` se arma a partir de los slots y se guarda en `03_visual.json`; el nombre quedó del camino viejo "prompt crudo del LLM" (el prompt final lo teje otro modelo).
- `m03_visual.py:2744` `_sync_map_ref` se persiste como ref (comentario PR 1 chat 24).
- `image_grade.py:79` importa PIL dentro de la función (`stats`), la única que lo necesita; si PIL no está, solo falla esa función muerta en producción.

<!-- parte fase2a_b -->
# Notas de auditoría — zona fase2a, parte fase2a_b

Los 7 archivos se leyeron enteros. Los md5 al terminar coinciden con los de A. Sin discrepancias con el `estado_a`.

## Juez visual y clasificador (cadena desconectada)
- `fase1_5.py:15` y `:65` dicen que m05_judge y m06_classifier «siguen VIVOS en el repo»; en producción no los importa nadie (A: `lo_importan` vacío). Solo viven tests y `_lab_chat66b_*`.
- `m05_judge.py:1855` `judge_topic_with_voting` abre un gate interactivo con `input()` (vía `prompt_user_action`, `m05_judge.py:1914`) y emite marcadores `QA_FORM` (`m05_judge.py:1616`, `:1691`): código pensado para el form que hoy nadie llama.
- `m05_judge.py:1017` y `m06_classifier.py:189` definen cada uno su propio `_earliest_module` con lógica distinta (uno `min` por índice y falla con módulo desconocido; el otro devuelve `m00` por defecto); `MODULE_ORDER` de m06 (`:37`) no tiene m05 y `_MODULE_PIPELINE_ORDER` de m05 (`:1004`) sí.
- `m06_classifier.py:134` `_load_step` duplica a `m06_assembler.py:22` (solo cambia el prefijo del error); `_load_topic_facts` (`m06_classifier.py:143`) importa `_load_topic` dentro de la función desde un módulo que ya importa arriba (`:28`).
- `m05_judge.py:408` y `:466` (`build_chapter_prompt`, `call_flash_for_chapter`) reciben `profile` y no lo usan; el docstring (`:12`) dice que art_profile se desconectó en el chat 19.
- `m05_judge.py:1241-1246` `_UPSTREAM_FILES` lista `narration` (`01b_narration.json`) que `judge_topic` no carga (comentario en `:1438`).
- `m05_judge.py:1191` el reporte dice «¡Listo para m04!»; no hay m04 en ninguna de las tablas del módulo (m00, m01a, m01b, m02, m03, m05).
- `m05_judge.py:937-944` `COST_TABLE` (costos en US$ y minutos por módulo) cita como origen «HANDOFF Bloque 4 Pieza 5», que no es DECISIONES ni un estándar citado. `ANCHOR_EXCERPT_SIMILARITY_THRESHOLD` 0.85 (`:156`) y `MAX_RETRY_ATTEMPTS_M05` 3 (`:95`) citan solo «HANDOFF» o nada.
- `m05_judge.py:93` («igual en las 7 llamadas»), `:1234` y el docstring de `judge_topic` hablan de «7 llamadas / 7 caps», fijo; `m06_classifier.py:37` fija `m00..m03` y su prompt (`:119`) los enumera.
- `m06_classifier.py:11-18` (docstring) y `:601` hablan del menú `[P]/[R]/[E]`; el menú real es `[A]/[H]/[P]/[R]/[E]` (`:523-556`).
- `m06_classifier.py:70-72` el prompt llama «stylistic categorization (deprecated)» a la PART B del prompt visual: referencia a la capa de art_profile que ya no existe.
- `m06_classifier.py:516` `_print_summary` calcula la ruta del JSON con el índice dentro del bucket (`items.index(p)+1`), pero `_persist_issue_payload` (`:311`, llamado en `:663`) numera por orden global de issues: las rutas impresas pueden no existir.
- `m06_classifier.py:570` el id `FP-NNN` se arma con `len(existing)+n_added+1`; `:578` guarda `fp.get("issue_id")` en el campo `source_topic_id` (es el id del issue, no del topic); `:579` usa `__import__("datetime")` en línea.
- `m06_classifier.py:455-464` el handoff generado manda correr `test_module_03.py`, `test_module_05.py` y `python fase1_5.py --topic <id> --from m03`; sus reglas dicen «NO modificar m05, m06, fase1_5» (`:425`).
- `m06_classifier.py:671-686` rama `auto_pass` de «batch desatendido»: sirve a una cadena que ya no la usa.

## m06_assembler (vivo)
- `m06_assembler.py:96` pone `art_profile` del capítulo desde `03_visual.json` y para los caps Flux lo pisa con `""` en `:117` (vía `_mode_art_profile`, `:40-48`, que siempre devuelve `""`): la clave sale vacía aunque `03_visual.json` traiga valor.
- `m06_assembler.py:91` `render_engine = "veo" if cap_num in (1, 7) else "flux"`: los números 1 y 7 están fijos en el código; no vi su origen citado en el archivo. `:123-124` fija `video_type: "long"` y `prompt_protocol_version: "v2"`.
- `m06_assembler.py:2-3` el docstring dice que lee outputs «m00→m03» y sección 7 de ARCHITECTURE.md; el código solo lee `01b_narration.json` y `03_visual.json` (`:61-62`).
- `m06_assembler.py:138` usa `datetime.utcnow()`.
- `fase1_5.py:653-655` comenta «Gate = MISMO alcance que tenía m06»; el gate real (`from_step in (...)`) hace que `assemble_final_script` corra en la etapa `voz`, no en `guion` (la cadena de `guion` para en el papel antes de llegar).

## m05_narrative (vivo)
- `m05_narrative.py:352` `cap_problems`: su único llamador de producción es `m01b_narrator.py:178`, dentro de `if f5 and f5.get("pool")`; ningún llamador pasa `f5=` (grep sin resultados en `script_engine/` y `fase1_5.py`), así que esa rama es inalcanzable en producción. `m01b_guionista.py:141` llama `_validate_narration` sin `f5`. A no la marcó como candidata porque `m01b_narrator.py` la nombra.
- `m05_narrative.py:4-5` dice que lo usa m01b «para validar cada cap y reintentar con feedback»; hoy lo usan `m01b_guionista.review` (`m01b_guionista.py:153`, `cap_review`) y `guion_v4` (`:794`, `:952`, `:1238`).
- `m05_narrative.py:263` («las 7 narraciones»), `:282` y `:610` (`k <= 6`, `cap <= 6`): asumen 7 capítulos.
- Números sin origen en DECISIONES ni estándar, con referencia solo a tandas (F5, F5b, F5c): `DENSITY_MIN` 2.0 (`:31`), `MAX_DATO_CAPS` 2, `TRIGRAM_MAX` 0.05, `ADJ_MIN`/`ADJ_MAX` 2.0/4.0 (`:36-37`), `FILLER_RUN_MAX` 2, `SCORE` (`:368`), `DATE_MATCH_MIN` 0.5 y `DATE_MATCH_WORDS` 2 (`:467-468`). El comentario de `:34` cuenta que F5 había fijado 3.6 y F5b N4 lo cambió a piso 2 / techo 4.
- `m05_narrative.py:129`, `:478` importan `researcher_steps.research_v3.caso` dentro de funciones; `:130` importa `script_engine.guion_v3_reglas.DATE_PARAPHRASE` (nombre de la cadena v3).
- `m05_narrative.py:337-342` `judge_narration` lee `01a_skeleton.json` y `_f5_violations` de `01b_narration.json`; `fase1_5.py:12` dice que la cadena vieja (m01a_skeleton, m01b_narrator) se borró y `m01b_narrator.py` sigue en el repo (lo importa `m01b_guionista.py:115`). El skeleton hoy lo escribe `m01d_particion` (`m01d_particion.py:243`).

## flow_director, flow_config, flow_profiles (vivos)
- `flow_director.py:44-55` y `:67-68` el prompt dice intensity «0.6-1.0» («NUNCA por debajo de 0.6») y steady «0.0-0.8»; `flow_config.py:97-100` fuerza intensity 0.85-1.0 y steady 0.0-0.4. El LLM recibe rangos que el código luego recorta.
- `flow_director.py:138` y `:143` dicen «4 movimientos» / «las 4 reducidas en C1»; el inventario son 3 (`flow_config.py:70-86`, prompt `flow_director.py:44`).
- `flow_director.py:93-125` `_fallback_spec(scene_position, total_scenes)`: se llama con posiciones `ch01…chNN` generadas por escena (`:235`), no por capítulo, pero trata `n == 1` como hook y `n == total_scenes` como outro. Con la granularidad por imagen, solo la primera y la última imagen del video caen en esas ramas.
- `flow_director.py:121-122` fallback con intensity 0.95 y steady 0.3; `fase2b.py:2276-2282` repite 0.95 / 0.3 en su propio fallback y elige siempre `vertical`: dos fallbacks distintos para lo mismo.
- `flow_director.py:40` el prompt se arma al importar (f-string con `render_inventory_for_prompt()`); `:22` usa `PipelineStage.ASSEMBLY` para loguear.
- `flow_config.py:11-12` el docstring dice que la selección vive en `modules/flow_director.py`; el archivo está en `script_engine/flow_director.py`.
- `flow_config.py:36` fija la ruta absoluta del venv de DepthFlow en el código. `FlowRenderSettings` (`:29-41`) define `ssaa`, `fps`, `default_duration_seconds`, `use_subprocess`, `fallback_to_kenburns` y `fallback_kenburns_zoom`; `flow_director` no los usa (`flow_render` lo consumen `depth_probe.py:26` y `parallax_animator_v2.py:28`).
- `flow_config.py:18` importa `BASE_DIR` y no lo usa en el archivo.
- `flow_profiles.py:1-12` «DEPRECATED chat 19»: solo conserva `FlowSpec`; `flow_config.py:10` aún dice que las reglas por art_profile viven en `flow_profiles.py`.
- `fase2b.py:3290-3292` en el re-burn (`reuse-visuals`) no se llama a flow_director. A marca estos tres módulos en `fondos`, `guion_pantalla`, `aprobar_guion` y `render` porque fase2b los importa; solo `fondos` decide movimientos (el cache `flow_specs`, `fase2b.py:2377`, puede leerse en otras pasadas).

<!-- parte fase2a_c -->
# Notas de auditoría — zona fase2a, parte fase2a_c

Material crudo para F43. Sin propuestas de cambio. Los 11 archivos se leyeron enteros; ninguno cambió (md5 de A copiados tal cual).

## Código muerto, duplicado y dos lógicas para lo mismo

- `audio_manager.py:149` `_transcribe_word_timestamps` y `audio_manager.py:208` `_force_align_to_script`: nadie las llama en el repo. Es el camino Whisper, reemplazado por el Forced Alignment de ElevenLabs (`audio_manager.py:543`).
- Muertas por arrastre (solo las usan las dos de arriba): `_get_whisper_model` (115), `_merge_punctuation_words` (133), `_normalize_token` (187), `_interp_spans` (195), `_enforce_monotonic_timestamps` (304). A no las marcó porque se nombran entre ellas.
- `audio_manager.py:133` `_merge_punctuation_words` está repetida en `fase2b.py:192`, y `audio_manager.py:71` `_find_ffmpeg_binary` en `fase2b.py:86` (y `mixer_server.py`, según A). El «llamador en fase2b» que A registró es la copia propia de fase2b, no un import de audio_manager.
- `audio_manager.py:462` `_normalize_loudness` llama a `ffmpeg` por nombre pelado, mientras `_get_ffprobe` (90) resuelve la ruta con Winget. Dos formas de ubicar el binario en el mismo archivo.
- `script_engine/m07_music_director.py:1218` `fijar_plan` solo la llama `plan_composicion` (1215), que está muerta en producción: muerta por arrastre. `m07:1202` `plan_composicion` y `m07:1249` `generar_con_plan` solo las usan `test_module_f28a.py` y `lab/hyperframes/f28/a/f28a_paleta.py`.
- `script_engine/m07_music_director.py:877` `_generate_new_track_with_gate` (con `_gate_approve_track` 780, `_play_audio_file` 699, `_edit_prompt_with_notepad` 736, `_persist_track_descriptor` 581, `_call_elevenlabs_music_api` 538) es el camino viejo «una pista nueva por video». Sigue conectado (m07:1134) y se activa si un intent no tiene pista de paleta en la biblioteca. Con F28 la idea declarada es «nunca se genera música por video» (m07:1103-1104).
- Dos lógicas para elegir pista: rama paleta (m07:1101-1109, sin umbral, cae a la pista «a») y rama vieja con `MATCH_SCORE_THRESHOLD` (m07:1110-1116 y 1446). El log de m07:449-451 imprime `MATCH_SCORE_THRESHOLD` aunque ahora el umbral efectivo puede ser el parámetro `umbral`.
- `audio_manager.py:456` `tts_v4_enabled` y `audio_profiles.py:105` `VOICE_SETTINGS_BY_INTENT` (v2 + Bill) siguen vivos; solo se usan si el capítulo no trae `narration_tts` o con `TTS_V2=1`. Tras F41 (cadena única v4) no hay otra fuente de capítulos sin `narration_tts` que el camino SHORT de `fase2a.py:324`.
- `audio_profiles.py:49` y `:68` perfiles `SABIDURIA_ESTOICA` y `TRUE_CRIME_TERROR`: nadie los activa (`audio_config.py:8` fija MISTERIO_ABISAL). Hay también `music_prompt` en los tres perfiles, escrito al sync_map (`audio_manager.py:847`) y no leído por ningún módulo de esta parte.
- `music_config.py:76` `MUSIC_PROMPTS` (7 prompts «curados a mano») es la fuente del camino viejo de generación; la paleta nueva usa `PALETA_INTENTS` (265) más `SONIDO_DEL_CANAL` (254). `SONIDO_DEL_CANAL` solo lo consume el lab de F28 (grep en lab/hyperframes/f28), no producción.

## Comentarios y docstrings que contradicen el código

- `audio_manager.py:7-9` dice que transcribe con faster-whisper y hace forced alignment contra Whisper; el código real usa el Forced Alignment de ElevenLabs (`audio_manager.py:686`). Los comentarios de 47-51 y 696-698 también arrastran la historia.
- `audio_manager.py:122` el log dice «Whisper (base, int8)» y la línea 125 carga `device="cuda", compute_type="float16"`.
- `audio_manager.py:808` `AUDIO_STYLE.get("elevenlabs_model_v4") or "eleven_v4"`: el valor literal aparece como respaldo, y `audio_profiles.py:18` ya lo trae. Duplicado de la constante.
- `fase2a.py:309-311`: fase2a habla de «timestamps Whisper en PR 3»; los timestamps ya no vienen de Whisper.
- `script_engine/m02_5_normalizer_gate.py:5-8` y `:113` anuncian «8 categorías» / «los 8 casos»; el prompt enumera 11 (hasta LARGE_NUMBER, 228) y `VALID_LLM_CATEGORIES` (54) tiene 13 valores. `:342` habla de «6 casos». `:84-90` el docstring de `_build_system_instruction` no menciona los cambios de F5.
- `script_engine/m02_5_normalizer_gate.py:97` y todo el prompt asumen «español neutro»; el docstring de `tts_normalizer.py:8-15` dice «Para SHORT… camino principal» y «LONG con gate», lenguaje de antes de F41.
- `script_engine/m07_music_director.py:20` «LLAMADAS GEMINI: 0-7 por video»; con paleta hay 1 por capítulo con 2+ pistas de paleta, y el flujo F28 puede tener más caps que 7 (no hay tope en el código).
- `music_config.py:41-44` el comentario dice «Duración fija… 60s» y «Camino A: 60s» (también en el encabezado, líneas 10-11), mientras `MUSIC_LENGTH_MS = 180000`. El comentario de la línea 44 sí explica el cambio; los dos de arriba no.
- `music_config.py:51-53` timeout «180s = 3 minutos» pero `m07_music_director.py:1255` usa `max(MUSIC_REQUEST_TIMEOUT_SEC, 400)`: dos números para lo mismo.
- `music_config.py:228` `stripped in ("", "...", "...")`: dos elementos iguales (probablemente un punto suspensivo Unicode y tres puntos que perdieron la diferencia).
- `music_config.py:29` y `:191-200` hablan de «las 7 entries»; `PALETA_INTENTS` (265-275) tiene 6: falta `resolution`.
- `script_engine/music_intensity.py:13-16` docstring define silencio «nunca más de 2 por cap; (a) va primero»; el código lo cumple, pero la regla (b) se evalúa solo contra citas que caen fuera de la ventana del golpe (línea 116) y eso no figura en el docstring.
- `patch_sync_map_mixing.py:6` «Descartable después de chat 28»: sigue en el repo y nada lo referencia.
- `subs_remap.py:12-15` cita `fase2b._build_chapter_segment ANTES de _build_ass_from_words`; `script_engine/gfx_layer.py:478` lo usa también y el docstring no lo dice.

## Números sin origen visible (para la regla «número que no esté en DECISIONES / F3 / estándar citado»)

- `script_engine/m07_music_director.py:917` `MAX_ATTEMPTS = 10`; `:266` y `:271` cortes de 400 y 300 caracteres del prompt/descripción; `:1076` `[:200]` del anchor; `:1062` `[:50]` del video_id; `:1255` 400 s de timeout; `PLAN_SECCIONES = (3, 5)` (1179), 3000 y 120000 ms por sección (1239-1241; el prompt de 1189 dice lo mismo), 50 y 48 estilos máximos (1231-1245).
- `script_engine/m07_music_director.py:313` y `music_config.py:49` umbral 80 («conservador inicial», sin medición citada); `:445` umbral 0 con paleta («F28: se elige entre las dos»).
- `audio_manager.py:410` timeout 120 s; `:566` 180 s; `:367` 15 s; `:690` loss > 0.15; `:462-464` `TP=-1.5`, `LRA=11`, 44100, 128k; `:470` respaldos `0.55` / `0.8`; `:809` `"es"`. `audio_profiles.py:23` `voice_lufs_v4 = -24.0` (justificado por una medición de F9 en el comentario); `audio_profiles.py:31-37` volúmenes y ducking del canal, con comentarios de «chat 32 tune».
- `audio_profiles.py:106-123` stability y style por intent: comentarios como «# subí / # igual / # subí mucho stability, bajé mucho style» describen cambios que ya no coinciden con los números (por ejemplo `shock` stability 0.45, el comentario dice «subí mucho»).
- `script_engine/music_intensity.py:27-35` `GANANCIA_DB`, `FADE_SILENCIO_S`, `SILENCIO_PREVIO_S`, `VUELTA_GOLPE_S`, `RAMPA_SUBE_S`, `MAX_SILENCIOS`, `SUBE_DESDE`, `ENV_HZ`: origen declarado «HANDOFF_F28 §B.2» en el docstring, no en DECISIONES.
- `anchor_timing.py:95` escalera 3 → 2 y `:105` mínimo 4 caracteres para el fallback de 1 token (origen: diag_235 / HANDOFF_135e en el docstring).
- `subs_remap.py:104` `0.05`, `:121` `0.01`: separaciones mínimas sin origen.
- `tts_normalizer.py:113-117` regex de horas AM/PM, dólares y porcentajes: F5 §1.4 en el comentario.

## Rutas de la cadena borrada (F41) que siguen vivas

- `audio_manager.py:54` `_NORMALIZED_NARRATION_FILENAME = "01b_narration_normalized.json"` y `:517` lectura de `data/scripts/_steps/<id>/01b_narration_normalized.json`; `script_engine/m02_5_normalizer_gate.py:639-642` lo escribe. Nombre y estructura (`narration_original`, `chapter_number`) son los del guion de antes de la cadena v4; hoy se alimentan de `01b_narration.json` que fase1_5 todavía produce para compatibilidad.
- `fase1_5.py:166-167` y `:570` leen `01a_skeleton.json` / `01b_narration.json` (los escribe `run_guion_v4`, `fase1_5.py:411`), y `audio_manager.process_script` toma `narrative_intent` de ese esqueleto (`audio_manager.py:799`). No es código de esta parte, pero es de donde cuelga.
- `fase2a.py:312-324` (camino SHORT: `audio_process(normalized, ...)`) es la única llamada a `process_script` fuera de fase1_5 y el form; con la cadena única «long» no está claro quién produce un topic SHORT.
- `audio_manager.py:456` comentario «guion v3 → v4», `audio_manager.py:805`: «guion v3» en comentarios; la cadena v3 (guionista v3) se borró en F41-A.
- `script_engine/m07_music_director.py:14` «INPUT: sync_map.json (post PR 2.A)», `:1063`: `topic_title = sync_map.get("video_id", topic_id)[:50]`: es el id, no el título (el comentario dice «fallback razonable»; se guarda en `topic_title` del descriptor).

## Imports dentro de funciones

- `audio_manager.py:120` import perezoso de `faster_whisper`: solo lo alcanza la rama muerta.
- `audio_manager.py:619` `from script_engine.tts_tags import transfer_tags` dentro de `generate_chapter_assets`: el módulo existe.
- `tts_normalizer.py:121, 136` `from script_engine.num_es import ...` dentro de `_num_text` y `normalize_pool_forms`: existe.
- `anchor_timing.py:48` `from tts_normalizer import normalize_for_tts` dentro de `_needle_normalized`, con `except Exception: pass` (`:50`): si el import fallara, el matcher seguiría con el anchor crudo sin avisar.
- `script_engine/music_intensity.py:157` `import wave` dentro de `aplicar_a_wav`.
- Ninguno de los imports de esta parte apunta a un módulo inexistente (`imports_rotos` de A confirmado vacío).

## Discrepancias con `estado_a` y otros hallazgos

- `patch_sync_map_mixing.py`: estoy de acuerdo con A (`huérfano`). Además corre código a nivel de módulo (lee/escribe `output/audio/7b52de57-.../sync_map.json` al ser importado, líneas 15-41): con solo importarlo reescribe el sync_map de Pripyat.
- `audio_profiles.py` y `audio_config.py`: A puso `etapas` hasta `render` (por import transitivo de fase2b). Leyendo el código, fase2b no las importa; el sync_map ya trae el bloque mixing (`fase2b.py:1957`). Las etapas reales son la voz y la planificación del guion por `voz_utils.narrador`; también las lee `mixer_server.py:41` (herramienta manual).
- `audio_manager.py` y `m07_music_director.py`: A los marcó alcanzados desde `research` y `assets`. En `research` no corren; en `assets` (fase2a) solo `process_script` del camino SHORT (`fase2a.py:324`), y solo si el topic no es «long».
- `music_config.py`: la función `validate_music_config` (191) exige exactamente los 7 intents de `MUSIC_PROMPTS` aunque la paleta de F28 defina 6; `generate_music_map` la llama siempre (`m07:1047`).
- Intent `resolution`: está en `MUSIC_PROMPTS` y en `VOICE_SETTINGS_BY_INTENT*`, no en `PALETA_INTENTS`; un capítulo `resolution` sin pista de paleta en la biblioteca cae al camino de generación con ElevenLabs (m07:1134), con gate interactivo si `music_gate_interactive` es True.
- `script_engine/m07_music_director.py:1101` lee `c.get("paleta")` de los descriptores de `audio_library/*.json`, campo que no figura en el esquema documentado en `_load_library` (m07:107-111) ni en `track_data` de `_generate_new_track_with_gate` (956-978).
- `script_engine/m07_music_director.py:352`, `:439`, `:1066` usan `error_handler.log_info(PipelineStage.AUDIO...)`; docstring de cabecera (26-28) anota deudas #167/#168 (sin cost_tracker para Music, `PipelineStage` sin MUSIC): el gasto de música no pasa por `cost_tracker` (`cost_usd: None`, m07:967). `generar_con_plan` tampoco registra costo.
- `script_engine/m02_5_normalizer_gate.py:699-709` en modo batch aplica TODOS los spans del LLM sin revisión y los recurrentes se escriben al diccionario global `data/normalizer_custom_dict.json` (persist_dict=True por defecto, no pasado por `fase1_5.py:541`).
- `audio_manager.py:630-639` la invalidación por `tts_hash` se evalúa solo si existe `meta_path`; con audio sin meta el código usa `prior_hash=None` y regenera. Funciona, pero depende del orden de dos `if` seguidos.
- `tts_normalizer.py:228` ejecuta `_load_custom_dict()` al importar y `m02_5_normalizer_gate.py:555` lo vuelve a ejecutar tras cada alta: las entradas ya cargadas se reasignan (idempotente para dicts, el `set` no duplica).

<!-- parte fase2a_d -->
# Notas de auditoría — zona fase2a, parte fase2a_d

Solo lo que vi leyendo los 9 archivos enteros. Sin propuestas. Los md5 de los 9 archivos coinciden con los de A al terminar.

## Falsos positivos en los hechos de A
- `script_engine/voz_utils.py:70` (`nombres`): la lista `prod` de A (evidence_pool, ficha_caso, pool_gate, research_v3, verify_quotes, evidence, guion_v3_reglas, guion_v4, m01a_*, m01b_guionista, m01d_particion, m05_narrative…) sale de `from script_engine import nombres`, que es el módulo `script_engine/nombres.py`, no esta función. Los llamadores reales de `voz_utils.nombres` son `m01e_pantalla.py:62` y `pantalla_filtros.py:16`. Por eso A marca `research` como etapa de voz_utils y es falso: voz_utils corre solo en `guion`, `guion_pantalla` y `render`.
- `script_engine/voz_utils.py:112` (`palabras`): mismo problema por nombre genérico; A lista guion_v4.py y nombres.py como llamadores y ahí es la palabra común, no la función.
- `fase2a.py:370` (`main`): A le asigna ~18 archivos y ~90 tests como llamadores porque todos tienen una función llamada `main`. El único que lanza fase2a es `run_pipeline.py:342`.
- `engine_profiles.py`: A le pone `research`, `guion`, `papel` y `packaging` por el cierre de imports (fase3.py, fase1.py). Los usos reales son `asset_manager.py:257,278,329` (assets) y `m03_visual.py:965` (voz, vía fase1_5).
- `foto_madre.py`: A le pone `research`, `guion`, `papel`; en el código solo corre en `voz` (fase1_5.py:647, paso0 dentro del bloque que arranca en normalizer_gate) y en `assets` (fase2a.py:337).
- `art_profiles.py`: A dice `tests: test_module_02.py, test_module_05.py` y 0 importadores; es cierto en producción, pero `test_module_02.py:22` hace `from art_profiles import VALID_PROFILES` y `script_engine/_archived/m02_profiles.py:50` también lo importa. Mi `estado` es el mismo (huérfano).

## Código muerto
- `script_engine/parallax_animator_v2.py:573` `build_hook_clip`: nadie la llama en todo el repo; está en `__all__` (línea 45) y su comentario sigue en `flow_profiles.py:32`.
- `script_engine/parallax_animator_v2.py:238` `_build_options`: la escala de intensidad por duración corta (líneas 253-257) ya no se usa en el camino de `build_animated_clip` (el docstring de las líneas 485-493 lo dice: siempre recibe 7.0); queda viva solo por `build_hook_clip` (que nadie llama) y por tests (test_chat55_flow_zoom.py, test_module_parallax_intensity_scale.py).
- `script_engine/parallax_animator_v2.py:300-301,337-338` `tiling_mode` e `introspect_tiling` (y el bloque `introspect_tiling` del runner, líneas 102-139): `build_animated_clip` solo pasa `tiling_mode=None` y fase2b no pasa nada; ninguna llamada de producción los activa. El comentario de la línea 143 los llama «DEPRECADO en chat 21».
- `script_engine/voz_utils.py:120` `munon`: ni producción ni tests; sus datos (`_ARTPREP`) sí se usan en otros lados.
- `art_profiles.py:155,172,210,255,414`: las cinco funciones sin llamador; también son código sin uso `PROFILE_GUIDE` (línea 462), `VEO_MOTION`, `NEGATIVE_PROMPT_GLOBAL` y los dos tuples de leakage, solo alcanzados por `_archived/m02_profiles.py` (que copia su propio `PROFILE_GUIDE`, línea 65, duplicado del de art_profiles).
- `art_config.py:19` `LEONARDO_SETTINGS`: nadie lo importa (`QA_sweep_flux_stale.md` ya lo marcó). Al importarlo leería `api.leonardo_model_id`, que sigue en config.
- `engine_profiles.py:71` `SEEDREAM_45_MODEL_ID`: se define y no se lee en ningún lado del repo (el comentario de las líneas 69-70 lo deja como ruta de vuelta).

## Dos lógicas para lo mismo / duplicados
- `engine_profiles.py:63,79` `cost_usd` (0.028 Kling, 0.035 Seedream) y `cost_tracker.py:229,247` (`kling_per_image` 0.028, `seedream_per_image` 0.035 desde `pipeline.costs`): el precio por imagen vive en dos sitios; `asset_manager.py` no lee `render.cost_usd` (grep: no aparece).
- `script_engine/voz_utils.py:333` `frases` y `:322`/`:340` `oraciones`/`oraciones_de_texto`: tres cortes de oraciones distintos (regex propia vs. `gfx_peak.sentences`); el docstring de `frases` dice que se movió de `gfx_question.sentences`.
- `foto_madre.py:84` hardcodea `{"width": 2560, "height": 1440}` y `engine_profiles.py:78` usa `pipeline.image_width/height`; `art_config.py:21-22` también usa `pipeline`. El comentario de foto_madre dice que son iguales a propósito, pero son dos fuentes del mismo número.
- `fase2a.py:333-339` repite la generación de foto madre que ya hace `fase1_5.py:647`; el comentario de las líneas 329-332 lo reconoce como «red de seguridad».
- `fase2a.py:206` `normalize_script` y `fase1_5.py:120` (`_build_audio_script`, comentario «mismo formato que fase2a._chapter_id»): dos constructores del mismo formato de capítulo.

## Comentarios que contradicen el código
- `engine_profiles.py:13-16` y `:43`: la «mitad PROMPT» está «DEFINIDA pero NADIE la lee todavía / INERTE hasta 3b», pero `script_engine/m03_visual.py:649-682,748` lee `profile.formula` y `profile.aspect_ratio_text`. `negations_in_text`, `style_tail` y `text_recipe` sí no los lee nadie fuera de tests.
- `engine_profiles.py:11`: «Mientras api.image_engine siga "kling"…» y el docstring dice «Cada motor (Kling, Seedream)»; el código usa `select_profile("seedream")` fijo en `asset_manager.py:257,278` y `m03_visual.py:965`.
- `fase2a.py:2-8` y `:280`: el docstring lista como paso 1 `audio_manager.process_script()` que genera `sync_map.json`, pero para LONG (el único tipo que lanza el form) el audio ya viene de fase1_5 y fase2a solo lee el sync_map (líneas 312-321).
- `fase2a.py:342`: el log dice «Assets... (imágenes Leonardo + clips Veo)» y el comentario de 125 usa `"leonardo"` como default de `render_engine`; Leonardo ya no es el motor (ver `QA_sweep_flux_stale.md`).
- `fase2a.py:24-28`: la NOTA habla de imports `from modules.xxx (legacy)` y de `art_config`, pero el archivo no importa ninguno de los dos.
- `fase2a.py:319`: el mensaje de error manda a `--from m01b`, que en `fase1_5.VALID_FROM_STEPS` rehace el guion completo; para recuperar solo el audio el paso sería `normalizer_gate`/`audio` (no lo verifiqué corriendo nada).
- `art_profiles.py:1-15` y `:264-280`: el encabezado dice «Refactor v2.2» y el bloque del chat 14 todavía dice «AGREGAR AL FINAL de art_profiles.py» / «Después de pegar este bloque» (instrucciones de parche ya aplicadas). `:226` cita `script_generator.sanitize_metadata_leak()`; `script_generator.py` no existe en la raíz.
- `script_engine/voz_datos.py:119`: el encabezado de sección dice «reloj en la esquina y palabra del pico (de gfx_peak, F36 §D)», pero solo hay `ticker_corner`; la palabra del pico no está en el archivo.
- `script_engine/voz_datos.py:106` `pico_plan`: recibe `words, scenes, moods, intensity, time_offset, freq` y no usa ninguno (solo `plan`, `ent`, `log`); el docstring cuenta que el sello propio del pico se borró.
- `script_engine/voz_utils.py:2-7`: el docstring dice que la usan «pantalla_filtros, pantalla_colocar, clima, voz_datos y m01e_pantalla»; en el código `pantalla_colocar` y `clima` solo la nombran en strings/comentarios (pantalla_colocar.py:96), y la importan además `pantalla_entrada`, `gfx_layer` y `gfx_realizador`.
- `script_engine/voz_utils.py:392-399` `narrador`: el docstring dice «para guiones v3»; F41 borró la cadena v3 y la voz v4 es la única.

## Números sin origen citado en el código
- `parallax_animator_v2.py:235` `_INTENSITY_FLOOR_FACTOR = 0.45` y `:681` `MID_RISK_MAX_INTENSITY = 0.85`: sin fuente (el 7.0 de `_DURATION_REFERENCE_S` sí dice «velocidad dulce validada img_03»); `:299,583` timeout 300 s, `:413` 180 s, `:561`/`:560` 180 y 120 s de FFmpeg, `-crf 18` (:548, :638), `DEPTHMAP_CACHE_SIZE_MB = 500` (:363) con razón dada pero sin medida.
- `parallax_animator_v2.py:93,270,272` `state.height = 0.05`, `isometric = 0.6`, `depth = 0.9`: «validada empíricamente chat 20/21»; sin DECISIONES citada.
- `foto_madre.py:91,105,112` timeouts 120/300/60 s; `:36-37` `_STYLE`: copiado de m03_visual (el comentario dice línea 149, no la verifiqué).
- `voz_datos.py:36,131` y `voz_utils.py:445`: la tolerancia 0.3 s («la tolerancia de pico_cap») y el `+0.3` del reloj aparecen escritos tres veces; `voz_datos.py:125` el `2.5` s de duración por defecto de un callout; `voz_datos.py:68,74` márgenes `i-4`, `i+8` («derivado»).
- `voz_utils.py:32` `range(100_000)` para el conversor palabras→número: el docstring dice 0-99 999, sin origen del tope; `:86-89` raíz de 5 letras; `:149` palabras de ≥ 4 letras.
- `engine_profiles.py:63,79`: costos con comentario («probado por Omar… $0.035») pero repetidos (ver arriba).
- `promote_palette_to_library_chat36.py:104` `NOMINAL_DURATION_MS = 60000` y los BPM/tonalidades de los prompts (líneas 46-102): registro del chat 36, sin ruta a DECISIONES.

## Rutas viejas / estado raro
- `promote_palette_to_library_chat36.py:143-174`: `audio_library/` hoy contiene pistas `*_f28_*` y subcarpetas `_paleta_f28`, `_retiradas` (no hay `*_curated`), por lo que el guard de la línea 146 no frenaría una corrida: movería los archivos sueltos de la library actual a `audio_library_backup_nyos_chat36/` y copiaría los 7 curados del chat 36. No lo ejecuté; es observación del código contra el listado del directorio.
- `fase2a.py:437-449`: rama sin `--topic` (lista blanca en `data/fase1_review.csv`, `_read_approved_topic_ids_from_csv`, `_should_skip`, `SKIP_STATUSES`) y rama SHORT (`_normalize_short`, `audio_process`, `--variation`): el form siempre pasa `--topic` y solo lanza LONG (`run_pipeline.py:342`); quedan alcanzables solo corriendo fase2a a mano (`_normalize_short` también por default `video_type="short"` de la línea 208 si el script no trae `video_type`).
- `fase2a.py:56` y `foto_madre.py:28-34`: importan `ContentRejectedError`, `_fal_headers`, `_flux_poll` (nombre «flux») de `asset_manager`; `_flux_poll` se usa para GPT Image 2 (foto_madre.py:105).
- `foto_madre.py` no importa ni usa `cost_tracker`: el gasto de GPT Image 2 (2560x1440, quality high, líneas 84-87) no se registra desde este módulo (coincide con la nota de memoria «Foto madre: costo fuera del bus»).
- `foto_madre.py:293` y `asset_manager`: el fallback llama `_generate_image_raw(prompt, dest, use_ultra=False, seed=None)`; `use_ultra` es un parámetro del motor Flux viejo.
- `art_profiles.py:244,247` y `:228-252`: prefijos de leakage con `leonardo,` y `flux,` / `ken_burns_zoom,` (motores y estilos del pasado) en un módulo huérfano.
- `art_profiles.py:306-308`: el comentario dice «Aplica solo a caps 1 y 7 (render_engine="veo"); los caps 2-6 (Flux)… depthflow en fase2b» —sigue la lógica Veo+Flux de chat 14, hoy el motor es Seedream.

## `estado_a` de A que no coincide
- Ninguno. Coinciden los 9: parallax vivo, art_profiles huérfano, fase2a vivo, voz_utils vivo, foto_madre vivo, promote solo herramienta manual, voz_datos vivo, engine_profiles vivo, art_config huérfano. Lo que difiere es la etapa de cada uno (ver «Falsos positivos»).

## Lo que no pude comprobar
- No leí `config.py` más allá de nombres de claves (`image_engine`, `fal_kling_model`, `leonardo_model_id`, valores omitidos), ni el contenido de `gfx_profiles`.
- No verifiqué el modelo exacto de Veo ni de ElevenLabs que usan `asset_manager`/`audio_manager`; en los stickers los nombro por su clave de config.
