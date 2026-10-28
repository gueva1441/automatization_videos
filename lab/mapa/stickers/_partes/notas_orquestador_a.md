# Notas de auditoría — zona orquestador, parte orquestador_a

Materia prima para F43. Sin propuestas de cambio. Todo leído de la primera a la última línea (los 8 archivos), solo lectura.

## Discrepancias con `estado_a`
- `version_stamp.py`: A lo marca `huérfano`; yo puse `solo herramienta manual`. Nadie lo importa ni lo lanza (grep en .py, .claude/ y hooks), pero `REPO_MAP.md:13` dice que lo corre CC a mano y `VERSION.json` (raíz) está versionado y con push_id de 2026-07-13. Es la única diferencia con A.
- `_reseed_core` (qa_studio_server.py:819): A la marca `sin_llamador`. La confirmo como muerta en el servidor y el form, pero tiene un llamador real en una herramienta manual de lab (`lab/hyperframes/f5/regen_marcadas.py:37`) además del test. Dejo la decisión a la auditoría.
- `Handler.log_message` (L1724) y `Handler.do_POST` (L1865): no las cuento como muertas; las llama el framework `http.server`.

## Código muerto o dormido
- qa_studio_server.py:975-1011 `_FIX_CLIP_REWRITE_INSTRUCTION` y :1014 `_build_clipfix_user_prompt`: el comentario de L968-971 las declara dormidas (chat 113, "NO borrar sin decisión de Omar"); ningún call-site.
- qa_studio_server.py:247-251 `_is_single` devuelve siempre `False` ("Option A retirada"); se sigue llamando en `caps()` y el campo `single` viaja al front.
- qa_studio.html:168-179 (CSS `.single-wrap`, `.single-card`, `.galtitle`, `.gal`, `.galitem`) y :768 (selector `.galitem img`): estilos y selector de la "Option A / galería" que el servidor ya no emite (`single` siempre falso). También :345 `c.single?' · clip':''`.
- qa_studio.html:718-722 `fixbar()`: sigue mostrando "corregir narración/audio (Zona 2) → v2" aunque la Zona 2 ya existe (botón `narrFixBtn`, L428).
- qa_form.html:267 y :338-360 menús `judge_action` y `remeasure_pick`, y qa_studio_server.py:1426 `__judge__ → qa_judge.html`: el juez m05 está DESCONECTADO del chain (fase1_5.py:15 y :65, chat 119); `m05_judge.py:1617-1618` todavía emite `judge_action` pero nada de la cadena lo llama. `remeasure_pick` sale de fase1.py:438.
- qa_form_markers.py:10-13: el docstring dice que m05_judge.py es "código nuevo" que usa este módulo; m05_judge hoy está fuera de la cadena.

## Restos de la cadena borrada (F41) que siguen vivos
- qa_form.html:219-232 `activityLabel`: reconoce `m01a|m01b` ("Writing narration"), `m05|judge|juez` ("Auditing script"), `m06` ("Classifying issues") y el encabezado `VIDEO (`; ni la cadena única de F41 ni `_phase_header` de run_pipeline emiten ya `VIDEO (` (hoy: FONDOS, PANTALLA, RENDER).
- run_pipeline.py:149 y :173-180 `CADENA_VIEJA`: manejo explícito de topics de la cadena borrada (sin papel pero con guion/assets/video): es intencional de F41, pero es una rama que solo existe por los datos viejos.
- script_engine/__init__.py:3-9: el docstring lista `m01a_skeleton`, `m01b_narrator`, `m02_profiles`, `m04_sanitizer` y `m05_judge` como "pendiente"; `m02_profiles` y `m04_sanitizer` no existen en `script_engine/`, y los otros ya no son el motor actual (m01a_escaleta, m01b_guionista, m01e_pantalla).
- qa_studio_server.py:1417 `_FORM_PHASES` y :1530 `_form_topics` están ajustados a F41. La lista de fases (`RESEARCH, GUION, PAPEL, VOZ, ASSETS, FONDOS, PANTALLA, RENDER, PACKAGING`) está escrita tres veces: qa_studio_server.py:1417, qa_form.html:213-215 (`PHASE_LABEL`) y :436-437 (`PHASE_ES`), más los encabezados de run_pipeline.py.

## Dos lógicas para lo mismo
- run_pipeline.py:85-106 `_visuales_base_faltan` copia a mano la regla de `fase2b._visual_base_existente` (fase2b.py:2869) "porque fase2b arrastra DepthFlow y Gemini": dos copias de la regla de qué visual base existe por cap; si fase2b la cambia, run_pipeline no se entera.
- El estado "terminado" de un topic aparece como literal tres veces: fase3.py:27 `DONE_STATUS = "video_generated"` (comentario "mismo contrato que fase2b"), run_pipeline.py:137 (literal suelto) y el marcador `packaged` en run_pipeline.py:132.
- qa_studio_server.py:633-638 `_assemble_command` corre `fase2b.py <tid>` sin flags (preview sin gfx), mientras run_pipeline.py:246 y :412 corre el render con `--reuse-visuals --keep-segments --gfx --gfx-sparse`. Dos "ensamblar" distintos; el botón ENSAMBLAR del visor no hace el render final.
- qa_studio_server.py:773-784 `_invalidate_baked` borra `_fase2b_work/chNN_flux_visual.mp4` y `chNN_hybrid_visual.mp4`, los mismos archivos que `run_pipeline._visuales_base_faltan` (L98-102) usa para decidir si falta la etapa `fondos`. Acoplamiento por nombre de archivo entre el visor y el orquestador.
- qa_studio_server.py:1202-1204 arma `data/normalizer_custom_dict.json` con `state.base/"data"` (comentario: "base/data == DATA_DIR en producción") en vez de usar DATA_DIR de config: otra convención de ruta paralela a la de run_pipeline.py:48.
- qa_studio_server.py:2002-2009 `_free_port` y :1444-1451 `_free_port_local`: dos funciones de puerto libre en el mismo archivo (una con `connect_ex` desde 8000, otra con bind a 0).

## Comentarios que contradicen el código
- qa_studio_server.py:28-33 (docstring): dice que el wiring de fase3 queda DEFERIDO y que ENSAMBLAR solo corre fase2b; hoy `run_pipeline` lanza fase3 (run_pipeline.py:430) y el server lanza el review de m09 (L1490).
- qa_studio_server.py:1436-1437: dice que se usa subprocess porque "m09_packaging arrastra config/gemini/cost_tracker que este server evita a propósito", pero el mismo archivo importa `asset_manager`, `gemini_helpers` y `audio_manager` (pesados) en los núcleos de fix (L824, L870, L1046, L1255-1256), solo que de forma diferida.
- qa_studio.html:13: "Botones de fix VISIBLES pero DESHABILITADOS (tooltip v2)"; hoy están habilitados y cableados (L500-540).
- qa_studio.html:507, :510 y :803: el panel del clip dice "mismo primer frame, cambia el MOVIMIENTO/cámara" y "reescribe el video_prompt"; el servidor hace lo contrario (qa_studio_server.py:962-971 y :1072-1111: regenera la FOTO del primer frame con el video_prompt intacto).
- run_pipeline.py:37: cita "DECISIONES 2026-10-27 00:30" para "no cierra ningún programa"; esa entrada es la regla de RAM que la de 21:50 (DECISIONES.md:126) dejó sin efecto.
- qa_studio_server.py:1375-1378 (cabecera del bloque) y qa_form.html:3: dicen que el form lanza `run_pipeline --research`; cierto para el botón, pero el form también retoma con `--topic` (L1525-1527, qa_form.html:473).
- run_pipeline.py:21-26 y L33: el docstring habla de PACKAGING "solo con form"; el form (qa_studio_server.py:1522 y :1527) siempre pasa `--batch`, así que desde el form fase3 nunca corre: solo se imprime `python fase3.py <id>`.

## Números sin origen visible
- qa_studio_server.py:630 `_ASM_LOG_MAX = 600`, :1418 `_FORM_CONSOLE_MAX = 600`, :1640 límite de 500 caracteres de `_sanitize_form_line`, :2005 rango de 50 puertos en `_free_port`, :1482 `timeout=3` al matar el review de miniaturas, :1698 `tail=200`: ninguno cita DECISIONES ni un estándar.
- qa_studio_server.py:792 `RESEED_STEP = 104729` ("primo", F5e): el origen es el comentario, no un DECISIONES.
- qa_studio_server.py:69 `TOPIC_ID` por defecto cableado a un uuid concreto (985a942f-…): un dato de un video puntual como default.
- qa_studio.html:26-27 `--heat-good-max:8` y `--heat-long-max:13` (segundos): el comentario dice "perilla; afinar con videos reales"; sin origen en DECISIONES.
- qa_form.html:41 y :45 (CSS): animación de 26 s que llena la barra hasta 88%: heurística visual sin origen.

## Otros
- run_pipeline.py:363 y :290: `input()` sin timeout en el visor y en las compuertas; con el form las responde el navegador, sin form la corrida queda esperando stdin.
- run_pipeline.py:121-122 y :543: import diferido de `fase1_5` "porque es pesado", pero `etapa_de` llama a `_estado_papel` al arrancar cualquier corrida, así que siempre se importa.
- run_pipeline.py: el parámetro `batch` lo usa solo `_paso_packaging`; todos los `_paso_*` lo reciben por uniformidad (L296-407).
- run_pipeline.py:147 `ETAPAS` no incluye `research`; el research vive solo en `main()` (L523-539) y se secuencia aparte.
- fase3.py:54 `_volatile_warning` busca `*_final_*ZOOM*.mp4`, un nombre de artefactos viejos; el render actual deja `<id>_final_gfx.mp4` (run_pipeline.py:116). No encontré en fase2b.py ningún nombre `*_ZOOM.mp4` que lo produzca.
- fase3.py:127-131: exige `topic.status == "video_generated"` y `video_path` existente; si el render de run_pipeline escribe `_final_gfx.mp4`, depende de que fase2b lo registre en topics_db (no verificado, no leí fase2b entero).
- qa_form_markers.py:19: `QA_FORM` se lee una sola vez al importar; run_pipeline.py:53 lo importa en el nivel de módulo, así que un `QA_FORM` seteado después del import no tiene efecto (diseño intencional según el docstring).
- version_stamp.py:1-11: sin docstring ni `__main__`; ejecuta y escribe al importarse (efecto de módulo).
