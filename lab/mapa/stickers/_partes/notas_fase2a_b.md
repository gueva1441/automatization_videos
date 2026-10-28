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
